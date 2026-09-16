#!/usr/bin/env python3
"""
generer_storyboard.py — construit le storyboard (05_storyboard.md/.json) a
partir du script TTS calibre, pour l'etape E5_storyboard (§4.3, §8, A6).

Une phrase de 03_script_tts.txt = une scene **en format court**. En format
long, les phrases sont groupees en scenes de duree cible (§8) : la meme
regle y produirait 150 a 300 scenes toutes `a_completer`, ce qui n'est pas
une charge de travail mais un livrable indefendable — A6 le rendrait en
sautant des scenes, et A7 monterait a l'aveugle. Le groupage est fait ici,
par le generateur, pas laisse a A6.

Le composant est choisi dans
le registre Remotion existant (composants/src/components/registry.ts) ;
s'il n'existe pas encore, il est quand meme nomme dans le storyboard et
signale dans "nouveaux_composants_necessaires" pour le Monteur (A7, §8) —
ce script ne cree jamais de composant.

**Ce script produit un squelette, pas un storyboard fini.** Il pose la
structure (une scene par phrase au depart, les durees, la direction artistique par
defaut de la charte) et marque chaque scene `a_completer`. C'est A6 qui
tranche ensuite, scene par scene, le composant, ses parametres et la
direction artistique — c'est le coeur de son travail (§8), pas quelque
chose qu'un script peut deviner. Une scene laissee `a_completer` est
signalee au Monteur (A7), qui ne doit pas monter a l'aveugle.

Le format est lu dans `state.json > format_video` ; `--format-video` le
surcharge (pour rejouer un squelette sans toucher au state).

Usage :
  python3 generer_storyboard.py --video ID --root R \
      --sortie-md videos/ID/05_storyboard.md --sortie-json videos/ID/05_storyboard.json \
      [--format-video short|long]

Sortie : JSON sur stdout. Codes : 0 ok | 2 script_tts absent | 3 script_tts vide
"""
import argparse
import json
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
REGISTRY_TS = REPO_ROOT / "composants" / "src" / "components" / "registry.ts"


def _charger_formats_video():
    """Importe outils/formats_video.py, source unique des valeurs de format.

    On cherche le repere plutot que de compter les niveaux : le fichier vit a
    `outils/` a la racine du depot et a `<skill>/outils/` une fois le skill
    deploye (§9.2), deux profondeurs differentes.
    """
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

# Debit mesure sur 2026-09-11_v01 : 231 mots reellement prononces pour
# 82,5 s de voix off, pauses comprises. La valeur d'origine (2,5)
# sous-estimait le debit et surestimait chaque duree de scene — c'est
# l'arithmetique derriere les 16,4 s d'ecart entre l'audio et la video
# rendue. Une premiere correction a 3,2 partait du script brut, marqueurs
# de mise en scene compris : 27 mots jamais prononces. Le recalage sur
# 04_phrases.json rend l'erreur inoffensive au montage, mais l'estimation
# affichee au Designer doit rester juste — c'est sur elle qu'il juge si la
# video est trop longue.
#
# La valeur vit desormais dans outils/formats_video.py, avec le cout par
# idee d'A5 : c'est le meme debit, il etait recopie a l'identique dans les
# deux scripts, et il faudra le recalibrer a un seul endroit.
MOTS_PAR_SECONDE = formats_video.MOTS_PAR_SECONDE
DUREE_MIN_S = 1.5

# Direction artistique par defaut, en attendant celle que A6 decide par
# scene (§8). Les valeurs viennent de charte.json > animation, validee une
# fois avec la charte plutot que redecidee a chaque video.
DA_DEFAUT = {"mouvement": "fondu", "rythme": "standard", "technique": "spring"}


def sortir(code, **data):
    print(json.dumps({"ok": code == 0, **data}, ensure_ascii=False, indent=2))
    sys.exit(code)


def lire_phrases(chemin):
    lignes = chemin.read_text(encoding="utf-8-sig").splitlines()
    return [l.strip() for l in lignes if l.strip()]


def lire_json_defaut(chemin, defaut=None):
    try:
        return json.loads(chemin.read_text(encoding="utf-8-sig"))
    except (FileNotFoundError, json.JSONDecodeError, OSError):
        return defaut


# Ancre sur la declaration elle-meme, pas sur n'importe quelle occurrence du
# mot REGISTRE : le fichier le mentionne d'abord dans un commentaire
# ("...dans composants/REGISTRE.md"), et un motif large partait de la pour
# capturer le premier bloc {...} venu — en pratique `{charte?: CharteTokens}`
# de ComposantParams. parser_registre() renvoyait donc une liste vide, A6
# croyait qu'aucun composant n'existait, et demandait a A7 de recreer
# TitleCard alors qu'il est deja au registre (contraire au §8, qui impose de
# reutiliser d'abord).
# `[^}]*` plutot que `.*?` avec DOTALL : le corps ne peut pas deborder du bloc.
RE_REGISTRE = re.compile(r"export\s+const\s+REGISTRE\b[^={};]*=\s*\{([^}]*)\}")


def parser_registre(chemin):
    if not chemin.is_file():
        return []
    contenu = chemin.read_text(encoding="utf-8-sig")
    m = RE_REGISTRE.search(contenu)
    if not m:
        return []
    corps = re.sub(r"//[^\n]*", "", m.group(1))  # commentaires de fin de ligne
    noms = []
    for morceau in corps.split(","):
        nom = morceau.strip().split(":")[0].strip()
        if re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", nom):
            noms.append(nom)
    return noms


def da_par_defaut(charte):
    """DA de repli, derivee des principes de la charte (§8)."""
    animation = (charte or {}).get("animation") or {}
    da = dict(DA_DEFAUT)
    technique = animation.get("technique_defaut")
    if technique:
        da["technique"] = technique
    return da


def duree_pour(phrase):
    nb_mots = len(phrase.split())
    return round(max(nb_mots / MOTS_PAR_SECONDE, DUREE_MIN_S), 1)


def composant_ideal(index):
    # Point de depart neutre, pas un choix editorial : le registre contient
    # desormais plusieurs composants (StickmanTalk, ConceptCutaway...) et
    # c'est A6 qui choisit lequel sert quelle phrase. Le squelette met le
    # plus generique et laisse `a_completer` a true.
    return "TitleCard"


def grouper_phrases(phrases, cible_s, scenes_max=None):
    """Groupe les phrases en scenes de duree cible. Retourne une liste de
    listes d'index (0-based), dans l'ordre.

    `cible_s = None` rend le comportement du Short : une phrase = une scene.

    Le groupage est glouton et ferme une scene **des qu'elle atteint la
    cible**, jamais avant : une scene plus courte que la cible ne se justifie
    que sur la derniere, faute de phrases restantes. Chaque phrase reste
    entiere dans une seule scene — la decouper casserait `phrases`, donc le
    recalage sur 04_phrases.json.

    `scenes_max` est un plafond dur. Quand il est atteint, on ne tronque pas :
    on recalcule une cible plus large et on regroupe. Tronquer produirait un
    storyboard qui ne couvre pas tout l'audio, c'est-a-dire un ecran fige
    pendant la fin de la voix off.
    """
    if cible_s is None:
        return [[i] for i in range(len(phrases))]

    def passe(cible):
        groupes, courant, cumul = [], [], 0.0
        for i, phrase in enumerate(phrases):
            courant.append(i)
            cumul += duree_pour(phrase)
            if cumul >= cible:
                groupes.append(courant)
                courant, cumul = [], 0.0
        if courant:
            groupes.append(courant)
        return groupes

    groupes = passe(cible_s)
    if scenes_max and len(groupes) > scenes_max:
        total = sum(duree_pour(p) for p in phrases)
        groupes = passe(total / scenes_max)
        # Le glouton peut encore depasser d'une scene (le reliquat de fin).
        # On la recolle plutot que de relancer une passe de plus pour une
        # seule scene.
        while len(groupes) > scenes_max and len(groupes) >= 2:
            groupes[-2].extend(groupes.pop())
    return groupes


def construire_scenes(phrases, composants_disponibles, da_defaut,
                      format_video=None):
    format_video = format_video or formats_video.FORMAT_DEFAUT
    groupes = grouper_phrases(phrases,
                              formats_video.duree_scene_cible(format_video),
                              formats_video.scenes_max(format_video))
    scenes = []
    nouveaux = []
    for i, groupe in enumerate(groupes):
        textes = [phrases[j] for j in groupe]
        phrase = " ".join(textes)
        nom = composant_ideal(i)
        if nom not in composants_disponibles and nom not in nouveaux:
            nouveaux.append(nom)
        scenes.append({
            "id": f"s{i + 1}",
            # Le texte prononce pendant la scene, pour que le storyboard
            # reste lisible et que A7 sache a quoi correspond la scene. Ce
            # n'est pas un parametre de composant : l'afficher a l'ecran
            # ferait doublon avec les sous-titres, qui le portent deja. En
            # format long, une scene couvre plusieurs phrases : elles sont
            # recollees ici, et listees une par une dans le .md.
            "phrase": phrase,
            # Les phrases que la scene couvre, en numeros de ligne de
            # 03_script_tts.txt. Le squelette en met une ; **si A6 fusionne
            # des scenes, il fusionne ces listes** (§8). Sans elles, A7 ne
            # peut recaler les durees que si le nombre de scenes est reste
            # egal au nombre de phrases — ce qui n'a pas ete le cas sur la
            # premiere video reelle : 11 scenes pour 24 phrases, donc aucun
            # recalage, donc 16,4 s d'ecart entre le son et l'image.
            "phrases": [j + 1 for j in groupe],
            "composant": nom,
            # Somme des durees de phrase, pas la duree du texte recolle : le
            # plancher DUREE_MIN_S s'applique par phrase, et une scene de
            # quatre phrases courtes dure bien quatre planchers.
            "duree_s": round(sum(duree_pour(x) for x in textes), 1),
            "params": {},
            "da": dict(da_defaut),
            "a_completer": True,
        })
    return scenes, nouveaux


def rendre_markdown(video_id, scenes, avertissements, phrases=None,
                    format_video=None):
    format_video = format_video or formats_video.FORMAT_DEFAUT
    lignes = [f"# Storyboard — {video_id}", ""]
    if format_video != formats_video.FORMAT_DEFAUT:
        lignes += [f"Format : **{format_video}**", ""]
    if avertissements:
        lignes += ["## Avertissements", ""]
        lignes += [f"- {a}" for a in avertissements]
        lignes.append("")
    total = sum(s["duree_s"] for s in scenes)
    lignes.append(f"Duree totale estimee : {total:.1f}s ({total / 60:.1f} min, "
                  f"{len(scenes)} scenes)")
    lignes.append("")
    lignes.append(f"Les durees sont des estimations (~{MOTS_PAR_SECONDE} mots/s). Elles sont "
                  "recalees sur l'audio reel au montage, a partir de `04_phrases.json` (§7.2).")
    lignes.append("")
    for s in scenes:
        marque = " — **A COMPLETER**" if s.get("a_completer") else ""
        couvertes = s.get("phrases") or []
        portee = ""
        if len(couvertes) > 1:
            portee = f" — phrases {couvertes[0]} a {couvertes[-1]}"
        lignes.append(f"## {s['id']} — {s['composant']} ({s['duree_s']}s){portee}{marque}")
        lignes.append("")
        # Une scene de segment couvre plusieurs phrases : les lister une par
        # une, numerotees, plutot que recollees en un pave. C'est sur cette
        # liste qu'A6 decide ou poser un accent ou un insert, et un accent se
        # designe par un numero de phrase.
        if phrases and len(couvertes) > 1:
            for numero in couvertes:
                if 1 <= numero <= len(phrases):
                    lignes.append(f"{numero}. {phrases[numero - 1]}")
        else:
            lignes.append(s.get("phrase") or s["params"].get("texte", ""))
        lignes.append("")
        da = s.get("da") or {}
        if da:
            lignes.append(f"- Mouvement : {da.get('mouvement', '?')}")
            lignes.append(f"- Rythme : {da.get('rythme', '?')}")
            lignes.append(f"- Technique : {da.get('technique', '?')}")
            if da.get("accent"):
                lignes.append(f"- Accent : {da['accent']}")
            lignes.append("")
        if s["params"]:
            lignes.append(f"- Parametres : {s['params']}")
            lignes.append("")
    return "\n".join(lignes)


def main():
    ap = argparse.ArgumentParser(description="Genere 05_storyboard.md/.json depuis 03_script_tts.txt.")
    ap.add_argument("--video", required=True, help="video_id")
    ap.add_argument("--root", required=True, help="Racine de /ChaineYouTube")
    ap.add_argument("--sortie-md", required=True, help="Chemin du .md a ecrire")
    ap.add_argument("--sortie-json", required=True, help="Chemin du .json a ecrire")
    ap.add_argument("--format-video", dest="format_video",
                    choices=list(formats_video.FORMATS),
                    help="Surcharge state.json > format_video. En long, les phrases sont "
                         "groupees en scenes de duree cible au lieu d'une scene par phrase.")
    a = ap.parse_args()

    racine = Path(a.root).expanduser()
    dossier_video = racine / "videos" / a.video
    script_tts = dossier_video / "03_script_tts.txt"

    if not script_tts.is_file():
        sortir(2, message=f"03_script_tts.txt introuvable : {script_tts}")

    phrases = lire_phrases(script_tts)
    if not phrases:
        sortir(3, message="03_script_tts.txt est vide (aucune phrase).")

    avertissements = []
    # Le format vient du state de la video ; --format-video n'existe que pour
    # rejouer un squelette sans toucher au state. `format_de` retombe sur
    # "short" si le state est absent ou anterieur au 16/09/2026.
    state = lire_json_defaut(dossier_video / "state.json", {})
    format_video = a.format_video or formats_video.format_de(state)

    charte = lire_json_defaut(racine / "00_Profil" / "charte_visuelle" / "charte.json")
    if charte is None:
        avertissements.append("charte.json introuvable — valeurs par defaut utilisees.")

    composants_disponibles = parser_registre(REGISTRY_TS)
    if REGISTRY_TS.is_file() and not composants_disponibles:
        # Ne pas laisser passer ca en silence : A7 se verrait demander de
        # recreer des composants qui existent deja (§8).
        avertissements.append(
            f"Registre Remotion illisible ou vide ({REGISTRY_TS.name}) — aucun composant "
            "reutilisable detecte. Verifie la declaration `export const REGISTRE = {...}`."
        )

    scenes, nouveaux = construire_scenes(phrases, composants_disponibles,
                                         da_par_defaut(charte), format_video)
    if format_video != formats_video.FORMAT_DEFAUT:
        avertissements.append(
            f"Format {format_video} : {len(phrases)} phrases groupees en {len(scenes)} scenes "
            f"de ~{formats_video.duree_scene_cible(format_video):.0f}s. Une scene par phrase "
            "aurait rendu un squelette illisible ; A6 peut redecouper, a condition de "
            "reporter les listes `phrases` (§8).")
    a_completer = sum(1 for s in scenes if s.get("a_completer"))
    if a_completer:
        avertissements.append(
            f"{a_completer} scene(s) marquee(s) `a_completer` : squelette genere, "
            "composant / parametres / direction artistique restent a trancher par A6 (§8)."
        )
    duree_totale = round(sum(s["duree_s"] for s in scenes), 1)

    sortie = {
        # Le format voyage avec le storyboard : c'est lui qui a decide du
        # decoupage, et c'est ce que le Monteur lit pour cadrer la
        # composition quand personne ne le lui passe en argument.
        "format_video": format_video,
        "scenes": scenes,
        "nouveaux_composants_necessaires": nouveaux,
        # Rappel machine des principes valides une fois avec la charte, pour
        # que A7 n'ait pas a relire charte.json pour les appliquer.
        "da_defaut": da_par_defaut(charte),
    }

    chemin_md = Path(a.sortie_md)
    if not chemin_md.is_absolute():
        chemin_md = racine / chemin_md
    chemin_json = Path(a.sortie_json)
    if not chemin_json.is_absolute():
        chemin_json = racine / chemin_json

    chemin_md.parent.mkdir(parents=True, exist_ok=True)
    chemin_json.parent.mkdir(parents=True, exist_ok=True)
    chemin_json.write_text(json.dumps(sortie, ensure_ascii=False, indent=2), encoding="utf-8")
    chemin_md.write_text(
        rendre_markdown(a.video, scenes, avertissements, phrases, format_video),
        encoding="utf-8")

    sortir(0, nb_scenes=len(scenes), nouveaux_composants=nouveaux,
           format_video=format_video, nb_phrases=len(phrases),
           duree_totale_s=duree_totale, scenes_a_completer=a_completer,
           avertissements=avertissements)


if __name__ == "__main__":
    main()
