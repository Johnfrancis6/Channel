#!/usr/bin/env python3
"""
resoudre_ressources.py — resout les `besoins` d'un storyboard en
`05b_ressources.json` (E5b, file d'attente #18).

Usage :
  python3 resoudre_ressources.py --storyboard <video>/05_storyboard.json \
      [--sortie <video>/05b_ressources.json] [--root RACINE] \
      [--associer cle=fichier ...] [--hors-ligne]

Sortie : JSON sur stdout. Codes :
  0 tout est resolu | 2 storyboard illisible |
  3 des besoins **obligatoires** restent non resolus

Ce que ce script ferme
----------------------
Le contrat de ressources etait complet des deux cotes et **vide au milieu** :
A6 declare des `besoins` dans le storyboard, `construire_props.py` sait lire
`05b_ressources.json`, `PlanBroll` / `PlanCapture` / `PlanLogos` savent
afficher le resultat — mais rien n'ecrivait le fichier du milieu. Les trois
composants ont ete ecrits, mis au registre, et jamais alimentes : aucune
image reelle n'est jamais arrivee a l'ecran.

Ce qu'il fait, et ce qu'il ne fait pas
-------------------------------------
Il fait la plomberie **deterministe** : telecharger un logo, capturer une
page, retrouver un fichier designe, mesurer la duree d'un clip. Il ne
choisit pas quel rush illustre quelle scene — associer « l'agent modifie le
fichier dans VS Code » a `demo_mcp.mp4` est un jugement, et un jugement
rendu par une correspondance de mots-cles serait un jugement qu'on ne peut
pas relire. Les besoins qu'il ne sait pas resoudre sortent dans
`non_resolus`, avec la liste de ce qui est disponible : c'est l'agent qui
tranche, puis relance avec `--associer`.

C'est la meme separation que `generer_storyboard.py`, qui produit un
squelette et laisse le choix des composants a A6.

Les rushes
----------
Decision du 16/09/2026 : Franco depose ses propres rushes dans
`videos/<id>/assets/`. Une banque libre illustre une ambiance ; elle ne
montre presque jamais le point precis dont parle le script. Trois facons de
lier un rush a un besoin, de la plus explicite a la plus implicite :

  1. `--associer <cle>=<fichier>` sur la ligne de commande ;
  2. `assets/rushes.json` — `{"rushes": [{"cle": "...", "fichier": "...",
     "decrit": "...", "duree_s": 12.4}]}` ;
  3. le nom du fichier : `assets/<cle>.mp4` pour le besoin `<cle>`.
"""
import argparse
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

EXTENSIONS_VIDEO = {".mp4", ".mov", ".webm", ".m4v", ".mkv"}
EXTENSIONS_IMAGE = {".png", ".jpg", ".jpeg", ".webp", ".gif", ".svg", ".avif"}


def trouver_outil(nom):
    """Chemin d'un outil frere.

    A cote de ce fichier dans `outils/`, et a cote de lui aussi dans la copie
    deployee sous `<skill>/outils/` : un skill doit rester installable seul,
    donc il embarque ses outils plutot que de les partager par un chemin
    commun (cf. _synchroniser_vers_claude_skills.py).
    """
    voisin = Path(__file__).resolve().parent / nom
    if voisin.is_file():
        return voisin
    for parent in Path(__file__).resolve().parents:
        candidat = parent / "outils" / nom
        if candidat.is_file():
            return candidat
    return None


def maintenant_iso():
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def sortir(code, **data):
    print(json.dumps({"ok": code == 0, "code": code, **data}, ensure_ascii=False, indent=2))
    sys.exit(code)


def besoins_du_storyboard(storyboard):
    """Aplatit les besoins de toutes les scenes, dedupliques par cle.

    Une meme cle dans deux scenes est le cas nominal — un logo sert plusieurs
    plans. Deux besoins **differents** sous la meme cle sont en revanche une
    faute d'A6 : le second ecraserait silencieusement le premier dans la
    table, et la scene afficherait autre chose que ce qu'elle a demande.
    """
    besoins, conflits = {}, []
    for scene in storyboard.get("scenes") or []:
        for besoin in scene.get("besoins") or []:
            cle = besoin.get("cle")
            if not cle:
                continue
            connu = besoins.get(cle)
            if connu is None:
                besoins[cle] = besoin
            elif {k: v for k, v in connu.items() if k != "cle"} != \
                 {k: v for k, v in besoin.items() if k != "cle"}:
                conflits.append(cle)
    return besoins, sorted(set(conflits))


def indexer_assets(dossier_assets):
    """Ce que Franco a depose, tel quel. C'est le menu propose a l'agent."""
    if not dossier_assets.is_dir():
        return []
    fichiers = []
    for f in sorted(dossier_assets.iterdir()):
        if not f.is_file() or f.name.startswith("."):
            continue
        if f.suffix.lower() not in EXTENSIONS_VIDEO | EXTENSIONS_IMAGE:
            continue
        fichiers.append(f)
    return fichiers


def lire_rushes(dossier_assets):
    """`assets/rushes.json` : ce que Franco (ou l'agent) declare sur ses rushes."""
    chemin = dossier_assets / "rushes.json"
    if not chemin.is_file():
        return {}, []
    try:
        data = json.loads(chemin.read_text(encoding="utf-8-sig"))
    except (OSError, ValueError) as e:
        return {}, [f"`assets/rushes.json` illisible ({e}) — ignore."]
    par_cle = {}
    for entree in data.get("rushes") or []:
        cle = entree.get("cle")
        if cle and entree.get("fichier"):
            par_cle[cle] = entree
    return par_cle, []


def duree_video_s(chemin):
    """Duree d'un clip, via ffprobe s'il est installe.

    Elle sert a `PlanBroll` pour reboucler un clip plus court que sa scene ;
    sans elle, la fin du plan est un ecran noir. Le recalage sur l'audio peut
    allonger une scene bien apres qu'on a choisi le clip, donc l'information
    ne peut pas etre deduite du storyboard.
    """
    try:
        p = subprocess.run(
            ["ffprobe", "-v", "error", "-show_entries", "format=duration",
             "-of", "default=noprint_wrappers=1:nokey=1", str(chemin)],
            capture_output=True, text=True, timeout=30)
    except (OSError, subprocess.SubprocessError):
        return None
    if p.returncode != 0:
        return None
    try:
        return round(float(p.stdout.strip()), 3)
    except ValueError:
        return None


def type_reel(besoin_type, chemin):
    """Le type suit le **fichier**, pas la demande.

    `PlanBroll` choisit `<OffthreadVideo>` ou `<Img>` sur `type === 'broll'`,
    et `PlanCapture` n'affiche sa barre de navigateur que sur
    `type === 'capture'`. Un besoin de b-roll honore par une photo doit donc
    sortir en `image`, sinon le composant tente de lire un PNG comme une
    video et n'affiche rien.
    """
    extension = chemin.suffix.lower()
    if besoin_type == "broll":
        return "broll" if extension in EXTENSIONS_VIDEO else "image"
    if besoin_type in ("capture", "logo", "image"):
        return besoin_type
    return "broll" if extension in EXTENSIONS_VIDEO else "image"


def chemin_relatif(chemin, dossier_video):
    """`05b_ressources.json` porte des chemins relatifs au dossier de la video.

    C'est ce que `construire_props.preparer_ressources` resout, et ca garde le
    fichier valable quand le dossier est lu depuis une autre machine — le
    Drive n'est pas monte au meme endroit chez Franco et sur Colab.
    """
    try:
        return chemin.resolve().relative_to(dossier_video.resolve()).as_posix()
    except ValueError:
        return str(chemin.resolve())


def resoudre_logo(besoin, banque_logos, hors_ligne):
    """Le logo vit dans la banque partagee, pas dans le dossier de la video :
    il sert vingt videos. On ne retelecharge que ce qui manque."""
    marque = besoin.get("requete") or besoin.get("cle")
    outil = trouver_outil("recuperer_logo.py")
    if outil is None:
        return None, f"`recuperer_logo.py` introuvable — logo « {marque} » non resolu."

    sys.path.insert(0, str(outil.parent))
    try:
        import recuperer_logo
        nom = recuperer_logo.slug(marque)
    except Exception:
        nom = "".join(c for c in marque.lower() if c.isalnum())
    finally:
        sys.path.pop(0)

    cible = banque_logos / f"{nom}.svg"
    if cible.is_file():
        return {"chemin": cible, "provenance": f"simpleicons:{nom}", "licence": "CC0-1.0"}, None
    if hors_ligne:
        return None, (f"Logo « {marque} » absent de la banque et --hors-ligne demande. "
                      f"Lance : recuperer_logo.py --marque \"{marque}\" --sortie {cible}")

    cible.parent.mkdir(parents=True, exist_ok=True)
    p = subprocess.run([sys.executable, str(outil), "--marque", marque, "--sortie", str(cible)],
                       capture_output=True, text=True)
    if p.returncode != 0 or not cible.is_file():
        detail = (p.stdout or p.stderr or "").strip()
        return None, f"Logo « {marque} » non recupere : {detail}"
    return {"chemin": cible, "provenance": f"simpleicons:{nom}", "licence": "CC0-1.0"}, None


def resoudre_capture(besoin, dossier_assets, hors_ligne):
    """Une capture deja prise n'est pas reprise : la page a pu changer entre
    deux runs, et le fichier du dossier est celui que l'agent a regarde."""
    cle = besoin["cle"]
    url = besoin.get("url")
    deja = dossier_assets / f"{cle}.png"
    if deja.is_file():
        return {"chemin": deja, "provenance": f"capture:{url or cle}",
                "licence": "capture-ecran"}, None
    if not url:
        return None, f"Besoin de capture « {cle} » sans `url` — rien a photographier."
    if hors_ligne:
        return None, f"Capture « {cle} » a prendre et --hors-ligne demande ({url})."

    outil = trouver_outil("capturer_web.py")
    if outil is None:
        return None, f"`capturer_web.py` introuvable — capture « {cle} » non resolue."
    dossier_assets.mkdir(parents=True, exist_ok=True)
    p = subprocess.run([sys.executable, str(outil), "--url", url, "--sortie", str(deja)],
                       capture_output=True, text=True)
    if p.returncode != 0 or not deja.is_file():
        detail = (p.stdout or p.stderr or "").strip()
        return None, f"Capture « {cle} » echouee : {detail}"
    return {"chemin": deja, "provenance": f"capture:{url}", "licence": "capture-ecran"}, None


def resoudre_fichier_local(besoin, dossier_assets, associations, rushes):
    """Image ou b-roll : un fichier depose par Franco, designe explicitement
    ou nomme d'apres la cle du besoin."""
    cle = besoin["cle"]

    designe = associations.get(cle) or (rushes.get(cle) or {}).get("fichier")
    if designe:
        chemin = Path(designe)
        if not chemin.is_absolute():
            chemin = dossier_assets / designe
        if not chemin.is_file():
            return None, f"« {cle} » designe {designe}, introuvable dans {dossier_assets}."
        return {"chemin": chemin, "provenance": f"rush:{chemin.name}",
                "licence": "propre"}, None

    for f in indexer_assets(dossier_assets):
        if f.stem == cle:
            return {"chemin": f, "provenance": f"rush:{f.name}", "licence": "propre"}, None
    return None, None  # Pas une erreur : un choix a faire, pas une panne.


def resoudre(storyboard, dossier_video, racine, associations, hors_ligne):
    dossier_assets = dossier_video / "assets"
    banque_logos = racine / "00_Profil" / "banque_assets" / "logos" if racine else \
        dossier_video / "assets"

    besoins, conflits = besoins_du_storyboard(storyboard)
    rushes, avertissements = lire_rushes(dossier_assets)
    avertissements += [f"Cle « {c} » declaree deux fois avec des besoins differents — "
                       f"le premier l'emporte." for c in conflits]

    ressources, non_resolus = {}, []
    for cle, besoin in besoins.items():
        type_demande = besoin.get("type") or "image"
        if type_demande == "logo":
            trouve, erreur = resoudre_logo(besoin, banque_logos, hors_ligne)
        elif type_demande == "capture":
            trouve, erreur = resoudre_capture(besoin, dossier_assets, hors_ligne)
        else:
            trouve, erreur = resoudre_fichier_local(besoin, dossier_assets, associations, rushes)

        if trouve is None:
            non_resolus.append({
                "cle": cle, "type": type_demande,
                "requete": besoin.get("requete"), "url": besoin.get("url"),
                "obligatoire": bool(besoin.get("obligatoire")),
                "motif": erreur or "Aucun fichier designe : choisis un rush et relance "
                                   "avec --associer, ou depose le fichier sous "
                                   f"assets/{cle}.<extension>.",
            })
            continue

        chemin = trouve["chemin"]
        entree = {
            "chemin": chemin_relatif(chemin, dossier_video),
            "type": type_reel(type_demande, chemin),
            "provenance": trouve["provenance"],
            "licence": trouve["licence"],
        }
        if entree["type"] == "broll":
            declaree = (rushes.get(cle) or {}).get("duree_s")
            duree = duree_video_s(chemin) or declaree
            if duree:
                entree["duree_s"] = duree
            else:
                avertissements.append(
                    f"Duree inconnue pour « {cle} » (ffprobe absent, rien dans "
                    f"rushes.json) : le clip ne sera pas reboucle s'il est plus "
                    f"court que sa scene.")
        if type_demande == "broll" and entree["type"] != "broll":
            avertissements.append(
                f"« {cle} » demandait du b-roll et recoit une image : rendue en "
                f"plan fixe.")
        ressources[cle] = entree

    disponibles = [{"fichier": f.name,
                    "decrit": (rushes.get(f.stem) or {}).get("decrit")}
                   for f in indexer_assets(dossier_assets)]
    return ressources, non_resolus, avertissements, disponibles


def main():
    ap = argparse.ArgumentParser(
        description="Resout les besoins d'un storyboard en 05b_ressources.json (E5b).")
    ap.add_argument("--storyboard", required=True)
    ap.add_argument("--sortie", help="Defaut : 05b_ressources.json a cote du storyboard.")
    ap.add_argument("--root", help="Racine ChaineYouTube, pour la banque de logos partagee.")
    ap.add_argument("--associer", action="append", default=[], metavar="CLE=FICHIER",
                    help="Lie un besoin a un rush du dossier assets/. Repetable.")
    ap.add_argument("--hors-ligne", dest="hors_ligne", action="store_true",
                    help="N'appelle ni capturer_web.py ni recuperer_logo.py : ce qui "
                         "manque sort en non_resolus au lieu d'etre telecharge.")
    a = ap.parse_args()

    chemin_storyboard = Path(a.storyboard)
    try:
        storyboard = json.loads(chemin_storyboard.read_text(encoding="utf-8-sig"))
    except (OSError, ValueError) as e:
        sortir(2, message=f"Storyboard illisible : {e}")

    associations = {}
    for paire in a.associer:
        if "=" not in paire:
            sortir(2, message=f"--associer attend CLE=FICHIER, recu « {paire} ».")
        cle, fichier = paire.split("=", 1)
        associations[cle.strip()] = fichier.strip()

    dossier_video = chemin_storyboard.resolve().parent
    racine = Path(a.root).expanduser().resolve() if a.root else None
    if racine is None and dossier_video.parent.name == "videos":
        racine = dossier_video.parent.parent

    ressources, non_resolus, avertissements, disponibles = resoudre(
        storyboard, dossier_video, racine, associations, a.hors_ligne)

    sortie = Path(a.sortie) if a.sortie else dossier_video / "05b_ressources.json"
    sortie.parent.mkdir(parents=True, exist_ok=True)
    sortie.write_text(json.dumps({
        "video_id": dossier_video.name,
        "genere_le": maintenant_iso(),
        "ressources": ressources,
    }, ensure_ascii=False, indent=2), encoding="utf-8")

    bloquants = [n for n in non_resolus if n["obligatoire"]]
    code = 3 if bloquants else 0
    sortir(code,
           sortie=str(sortie),
           nb_ressources=len(ressources),
           non_resolus=non_resolus,
           rushes_disponibles=disponibles,
           avertissements=avertissements,
           message=("Toutes les ressources sont resolues." if not non_resolus else
                    f"{len(non_resolus)} besoin(s) non resolu(s), dont "
                    f"{len(bloquants)} obligatoire(s)."))


if __name__ == "__main__":
    main()
