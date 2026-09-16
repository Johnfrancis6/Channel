#!/usr/bin/env python3
"""
rendre_video.py — orchestre le rendu complet de l'etape E6_montage (§8) :
verifie les prerequis, lance `remotion render` sur les props deja
construites par construire_props.py, et verifie le MP4 produit.

Sur un format long, le rendu se fait **par tranches reprenables**. Un
`remotion render` monolithique de 15 minutes, c'est 27 000 frames rendues
une par une : un echec a 80 % perd tout, et il n'y a aucun moyen de repartir
d'ou on s'etait arrete. Le defaut ne se voyait pas sur des videos de 50 s.

Chaque tranche est rendue dans son propre fichier, ecrite en deux temps
(`.tmp.mp4` puis `os.replace`) et **sautee si elle existe deja** — la meme
regle que le cache des clips TTS, pour la meme raison : un cache dont le
seul role est de survivre a une interruption ne peut pas se permettre de
relire un fichier tronque comme s'il etait bon. Les tranches sont ensuite
recollees sans reencodage.

Le nombre de frames n'est pas recalcule ici : il est demande a
`remotion compositions`, qui applique `calculateMetadata` comme le rendu.
Le recalculer en Python aurait cree une deuxieme source de verite pour la
duree, a cote de `dureeTotaleFrames()`.

Usage :
  python3 rendre_video.py --video ID --root R --props P.json \
      --sortie videos/ID/06_video_finale.mp4 [--browser CHEMIN] [--dry-run] \
      [--format-video short|long] [--tranche-s 120] [--concurrence N] \
      [--garder-tranches]

Sortie : JSON sur stdout. Codes :
  0 ok | 2 props absentes/invalides | 4 node_modules absent |
  5 registry.ts inaccessible | 6 echec remotion render | 7 mp4 absent/vide |
  8 echec du recollage des tranches
"""
import argparse
import json
import os
import re
import subprocess
import sys
from pathlib import Path

def trouver_repo_root():
    """
    Racine du depot, trouvee en remontant jusqu'au dossier qui contient la
    bibliotheque de composants.

    Un simple `parents[3]` marche depuis agents/short-monteur/scripts/ mais
    pas depuis la copie deployee dans .claude/skills/short-monteur/scripts/,
    qui n'a pas la meme profondeur : il y designait `.claude/`, ou il n'y a
    pas de composants/. Le skill documente pourtant l'appel par le chemin du
    skill — la commande de la doc etait donc la seule a ne pas marcher. On
    cherche le repere plutot que de compter les niveaux.
    """
    depart = Path(__file__).resolve()
    for candidat in depart.parents:
        if (candidat / "composants" / "src" / "components" / "registry.ts").is_file():
            return candidat
    return depart.parents[3]


REPO_ROOT = trouver_repo_root()
COMPOSANTS = REPO_ROOT / "composants"
REGISTRY_TS = COMPOSANTS / "src" / "components" / "registry.ts"


def _charger_formats_video():
    """Importe outils/formats_video.py, source unique des valeurs de format."""
    import importlib.util
    for base in Path(__file__).resolve().parents:
        candidat = base / "outils" / "formats_video.py"
        if candidat.is_file():
            spec = importlib.util.spec_from_file_location("formats_video", candidat)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            return module
    raise ImportError("outils/formats_video.py introuvable depuis " + str(Path(__file__).resolve()))


formats_video = _charger_formats_video()

# Longueur d'une tranche, en secondes de video rendue. 120 s a 30 fps =
# 3600 frames : assez grand pour que le cout fixe du bundle et du navigateur
# (quelques secondes) reste negligeable, assez petit pour qu'un echec ne
# coute jamais plus de deux minutes de rendu a refaire.
TRANCHE_S_DEFAUT = 120

# En dessous, le decoupage ne sert a rien : un Short entier tient dans une
# tranche, et le recollage n'ajouterait qu'un risque.
TRANCHES_MIN = 2

# `Video    30      1920x1080      27000 (900.00 sec)` — la ligne que rend
# `remotion compositions`. On lit le nombre de frames, pas la duree : c'est
# l'unite de `--frames`.
RE_COMPOSITION = re.compile(r"^\s*(?P<id>\S+)\s+(?P<fps>[\d.]+)\s+(?P<taille>\d+x\d+)"
                            r"\s+(?P<frames>\d+)\s*\(")


def sortir(code, **data):
    print(json.dumps({"ok": code == 0, **data}, ensure_ascii=False, indent=2))
    sys.exit(code)


def frames_de_composition(props_path, env, composition="Video"):
    """Nombre de frames et fps de la composition, demandes a Remotion.

    On ne recalcule pas la duree en Python : `calculateMetadata` peut la
    deriver de l'audio (`duree_audio_s`) autant que des scenes, et deux
    formules pour une meme duree finiraient par diverger — c'est exactement
    le motif « deux sources de verite » que ce depot a deja paye ailleurs.

    Retourne (frames, fps) ou (None, None) si la sortie n'est pas lisible :
    l'appelant retombe alors sur un rendu monolithique, qui marche toujours.
    """
    resultat = subprocess.run(
        ["npx", "remotion", "compositions", "src/index.ts", f"--props={props_path}"],
        cwd=str(COMPOSANTS), env=env, capture_output=True, text=True)
    if resultat.returncode != 0:
        return None, None
    for ligne in resultat.stdout.splitlines():
        m = RE_COMPOSITION.match(ligne)
        if m and m.group("id") == composition:
            return int(m.group("frames")), float(m.group("fps"))
    return None, None


def decouper(total_frames, frames_par_tranche):
    """[(premiere, derniere), ...] — bornes incluses, comme `--frames=a-b`."""
    bornes = []
    debut = 0
    while debut < total_frames:
        fin = min(debut + frames_par_tranche, total_frames) - 1
        bornes.append((debut, fin))
        debut = fin + 1
    return bornes


def rendre_tranches(props_path, sortie_path, bornes, env, concurrence=None):
    """Rend chaque tranche dans son propre fichier, en sautant celles qui sont
    deja la.

    Ecriture en deux temps : `remotion render` ecrit dans `.tmp.mp4`, puis
    `os.replace` publie le fichier. Sans ca, une tranche interrompue en cours
    d'ecriture serait relue comme terminee au run suivant, et le recollage
    produirait une video tronquee au milieu — un defaut silencieux, qui ne se
    verrait qu'a la relecture humaine.

    Retourne (tranches, deja_presentes, erreur).
    """
    dossier = sortie_path.parent / (sortie_path.name + ".tranches")
    dossier.mkdir(parents=True, exist_ok=True)
    tranches, deja = [], 0
    for index, (premiere, derniere) in enumerate(bornes):
        cible = dossier / f"tranche_{index:04d}.mp4"
        tranches.append(cible)
        if cible.is_file() and cible.stat().st_size > 0:
            deja += 1
            continue
        temporaire = cible.with_suffix(".tmp.mp4")
        # `--muted` : chaque tranche est rendue **sans son**. L'AAC ne se coupe
        # pas a la frame — il se code par blocs de 1024 echantillons — donc
        # recoller des tranches sonores ajoute une vingtaine de millisecondes
        # de silence a chaque jointure. Mesure ici : 4,096 s recolle contre
        # 4,054 s en monolithique, sur deux tranches. Sur huit, la voix off
        # finirait ~150 ms derriere l'image, et le decalage grandirait jusqu'a
        # la fin de la video — exactement le defaut que le recalage sur
        # 04_phrases.json existe pour eliminer.
        #
        # L'audio est donc remonte une seule fois, d'un seul morceau, au
        # recollage.
        cmd = ["npx", "remotion", "render", "src/index.ts", "Video", str(temporaire),
               f"--props={props_path}", f"--frames={premiere}-{derniere}", "--muted"]
        if concurrence:
            cmd.append(f"--concurrency={concurrence}")
        resultat = subprocess.run(cmd, cwd=str(COMPOSANTS), env=env)
        if resultat.returncode != 0 or not temporaire.is_file() or temporaire.stat().st_size == 0:
            temporaire.unlink(missing_ok=True)
            return tranches, deja, (f"Echec du rendu de la tranche {index + 1}/{len(bornes)} "
                                    f"(frames {premiere}-{derniere}). Les tranches deja rendues "
                                    f"sont conservees dans {dossier.name} : relancer la meme "
                                    f"commande reprend a partir d'ici.")
        os.replace(temporaire, cible)
    return tranches, deja, None


def chemin_audio(props):
    """Fichier de voix off reellement sur le disque, depuis `props.audioSrc`.

    `audioSrc` est une URL servie par le bundle de rendu
    (`/public/audio/<video>/04_voixoff.wav`), pas un chemin : c'est
    `copier_vers_public()` qui l'a ecrite, et le fichier est sous
    `composants/public/`. On refait le chemin inverse.
    """
    src = (props or {}).get("audioSrc")
    if not src or not src.startswith("/public/"):
        return None
    candidat = COMPOSANTS / src.lstrip("/")
    return candidat if candidat.is_file() else None


def recoller(tranches, sortie_path, env, audio=None):
    """Recolle les tranches (muettes) et remonte la voix off d'un seul bloc.

    Deux passes plutot qu'une, pour une raison de synchronisation : la video
    se recolle a la frame pres sans reencodage, alors que l'audio encode ne
    se coupe pas a la frame. Recoller des tranches sonores ajouterait un
    silence par jointure, et la voix off prendrait du retard sur l'image tout
    au long de la video. En repartant du WAV d'origine, il n'y a plus qu'une
    seule horloge audio, et elle n'est jamais coupee.

    `npx remotion ffmpeg` plutot que `ffmpeg` : Remotion embarque le sien, ce
    qui evite d'ajouter une dependance systeme a une chaine qui tourne aussi
    bien sur le poste de Franco que dans un bac a sable.
    """
    dossier = sortie_path.parent / (sortie_path.name + ".tranches")
    liste = dossier / "liste.txt"
    liste.write_text("".join(f"file '{t.name}'\n" for t in tranches), encoding="utf-8")

    muette = dossier / "recollee.mp4" if audio else sortie_path
    resultat = subprocess.run(
        ["npx", "remotion", "ffmpeg", "-y", "-f", "concat", "-safe", "0",
         "-i", str(liste), "-c", "copy", str(muette)],
        cwd=str(COMPOSANTS), env=env, capture_output=True, text=True)
    if resultat.returncode != 0:
        return False, (resultat.stderr or "")[-2000:]
    if not audio:
        return True, ""

    resultat = subprocess.run(
        ["npx", "remotion", "ffmpeg", "-y", "-i", str(muette), "-i", str(audio),
         "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-shortest", str(sortie_path)],
        cwd=str(COMPOSANTS), env=env, capture_output=True, text=True)
    return resultat.returncode == 0, (resultat.stderr or "")[-2000:]


def verifier_prerequis(props_path):
    if not (COMPOSANTS / "node_modules").is_dir():
        return 4, "composants/node_modules absent — lance 'npm install' dans composants/"
    if not props_path.is_file():
        return 2, f"Fichier props introuvable : {props_path}"
    try:
        json.loads(props_path.read_text(encoding="utf-8-sig"))
    except json.JSONDecodeError as e:
        return 2, f"Props JSON invalide ({props_path}) : {e}"
    if not REGISTRY_TS.is_file():
        return 5, f"registry.ts inaccessible : {REGISTRY_TS}"
    return 0, None


def main():
    ap = argparse.ArgumentParser(description="Rend la video finale (E6, §8) via remotion render.")
    ap.add_argument("--video", required=True, help="video_id")
    ap.add_argument("--root", required=True, help="Racine de /ChaineYouTube")
    ap.add_argument("--props", required=True, help="Chemin du fichier props.json")
    ap.add_argument("--sortie", required=True, help="Chemin du .mp4 a produire")
    ap.add_argument("--browser", help="Executable Chromium (REMOTION_BROWSER_EXECUTABLE)")
    ap.add_argument("--dry-run", action="store_true", help="Verifie les prerequis sans rendre")
    ap.add_argument("--format-video", dest="format_video", choices=list(formats_video.FORMATS),
                    help="state.json > format_video. En long, le rendu se fait par tranches "
                         "reprenables. Defaut : ce que declarent les props, sinon short.")
    ap.add_argument("--tranche-s", dest="tranche_s", type=int,
                    help=f"Longueur d'une tranche en secondes (defaut {TRANCHE_S_DEFAUT} en long). "
                         "0 force le rendu monolithique.")
    ap.add_argument("--concurrence", type=int,
                    help="Passe --concurrency a remotion render.")
    ap.add_argument("--garder-tranches", dest="garder_tranches", action="store_true",
                    help="Ne pas effacer les tranches apres un recollage reussi.")
    a = ap.parse_args()

    racine = Path(a.root).expanduser()
    props_path = Path(a.props)
    if not props_path.is_absolute():
        props_path = racine / props_path
    sortie_path = Path(a.sortie)
    if not sortie_path.is_absolute():
        sortie_path = racine / sortie_path
    # Resolus avant tout appel : `remotion` tourne avec cwd=composants/, donc
    # un chemin encore relatif y designe autre chose — et `--props` relatif
    # echouait sur « neither valid JSON nor a file path », sans que rien ne
    # dise que le probleme etait le chemin. Un --root relatif est pourtant la
    # facon la plus naturelle d'appeler le script depuis le dossier de la chaine.
    props_path = props_path.resolve()
    sortie_path = sortie_path.resolve()

    code, message = verifier_prerequis(props_path)
    if code != 0:
        sortir(code, message=message)

    props = json.loads(props_path.read_text(encoding="utf-8-sig"))
    format_video = a.format_video or props.get("format_video") or formats_video.FORMAT_DEFAUT
    # Un Short tient dans une tranche : le decoupage n'y apporterait qu'un
    # recollage de plus a rater. Il reste forcable par --tranche-s.
    tranche_s = a.tranche_s if a.tranche_s is not None else (
        TRANCHE_S_DEFAUT if format_video == formats_video.LONG else 0)

    if a.dry_run:
        sortir(0, dry_run=True, video=a.video, node_modules=True,
               props_valide=True, registry_accessible=True,
               format_video=format_video, tranche_s=tranche_s)

    sortie_path.parent.mkdir(parents=True, exist_ok=True)

    env = dict(os.environ)
    if a.browser:
        env["REMOTION_BROWSER_EXECUTABLE"] = a.browser

    bornes = []
    total_frames = None
    if tranche_s > 0:
        total_frames, fps = frames_de_composition(props_path, env)
        if total_frames:
            bornes = decouper(total_frames, max(1, int(tranche_s * fps)))
            if len(bornes) < TRANCHES_MIN:
                # Une seule tranche, c'est un rendu monolithique avec un
                # recollage inutile par-dessus.
                bornes = []

    if bornes:
        tranches, deja, erreur = rendre_tranches(props_path, sortie_path, bornes, env,
                                                 a.concurrence)
        if erreur:
            sortir(6, message=erreur, tranches_rendues=len(tranches) - 1,
                   tranches_total=len(bornes), format_video=format_video)
        ok, stderr = recoller(tranches, sortie_path, env, chemin_audio(props))
        if not ok:
            sortir(8, message="Echec du recollage des tranches (ffmpeg concat).",
                   detail=stderr, tranches=len(tranches))
        if not sortie_path.is_file() or sortie_path.stat().st_size == 0:
            sortir(7, message=f"MP4 absent ou vide apres recollage : {sortie_path}")
        dossier_tranches = sortie_path.parent / (sortie_path.name + ".tranches")
        if not a.garder_tranches:
            # Le MP4 final existe et a ete verifie : les tranches ne servent
            # plus qu'a occuper le Drive de Franco.
            for fichier in dossier_tranches.glob("*"):
                fichier.unlink(missing_ok=True)
            dossier_tranches.rmdir()
        sortir(0, sortie=str(sortie_path), taille_bytes=sortie_path.stat().st_size,
               format_video=format_video, tranches=len(bornes),
               tranches_reprises=deja, total_frames=total_frames)

    cmd = ["npx", "remotion", "render", "src/index.ts", "Video",
           str(sortie_path), f"--props={props_path}"]
    if a.concurrence:
        cmd.append(f"--concurrency={a.concurrence}")
    # Pas de capture_output : stdout/stderr de remotion sont heredites et
    # s'affichent en temps reel, sans etre bufferises.
    resultat = subprocess.run(cmd, cwd=str(COMPOSANTS), env=env)

    if resultat.returncode != 0:
        # `code_remotion` et non `code` : `sortir()` prend deja `code` en
        # premier parametre, donc ce kwarg levait un TypeError au lieu de
        # rendre le JSON d'erreur promis par le skill. Le seul chemin ou ca
        # se voyait etait celui d'un rendu qui echoue.
        sortir(6, message="Remotion render failed", code_remotion=resultat.returncode)

    if not sortie_path.is_file() or sortie_path.stat().st_size == 0:
        sortir(7, message=f"MP4 absent ou vide apres rendu : {sortie_path}")

    sortir(0, sortie=str(sortie_path), taille_bytes=sortie_path.stat().st_size,
           format_video=format_video, tranches=1)


if __name__ == "__main__":
    main()
