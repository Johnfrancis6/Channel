#!/usr/bin/env python3
"""
generer_storyboard.py — construit le storyboard (05_storyboard.md/.json) a
partir du script TTS calibre, pour l'etape E5_storyboard (§4.3, §8, A6).

Une phrase de 03_script_tts.txt = une scene. Le composant est choisi dans
le registre Remotion existant (composants/src/components/registry.ts) ;
s'il n'existe pas encore, il est quand meme nomme dans le storyboard et
signale dans "nouveaux_composants_necessaires" pour le Monteur (A7, §8) —
ce script ne cree jamais de composant.

**Ce script produit un squelette, pas un storyboard fini.** Il pose la
structure (une scene par phrase, les durees, la direction artistique par
defaut de la charte) et marque chaque scene `a_completer`. C'est A6 qui
tranche ensuite, scene par scene, le composant, ses parametres et la
direction artistique — c'est le coeur de son travail (§8), pas quelque
chose qu'un script peut deviner. Une scene laissee `a_completer` est
signalee au Monteur (A7), qui ne doit pas monter a l'aveugle.

Usage :
  python3 generer_storyboard.py --video ID --root R \
      --sortie-md videos/ID/05_storyboard.md --sortie-json videos/ID/05_storyboard.json

Sortie : JSON sur stdout. Codes : 0 ok | 2 script_tts absent | 3 script_tts vide
"""
import argparse
import json
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
REGISTRY_TS = REPO_ROOT / "composants" / "src" / "components" / "registry.ts"

MOTS_PAR_SECONDE = 2.5
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


def construire_scenes(phrases, composants_disponibles, da_defaut):
    scenes = []
    nouveaux = []
    for i, phrase in enumerate(phrases):
        nom = composant_ideal(i)
        if nom not in composants_disponibles and nom not in nouveaux:
            nouveaux.append(nom)
        scenes.append({
            "id": f"s{i + 1}",
            # La phrase prononcee, pour que le storyboard reste lisible et
            # que A7 sache a quoi correspond la scene. Ce n'est pas un
            # parametre de composant : afficher la phrase a l'ecran ferait
            # doublon avec les sous-titres, qui la portent deja.
            "phrase": phrase,
            "composant": nom,
            "duree_s": duree_pour(phrase),
            "params": {},
            "da": dict(da_defaut),
            "a_completer": True,
        })
    return scenes, nouveaux


def rendre_markdown(video_id, scenes, avertissements):
    lignes = [f"# Storyboard — {video_id}", ""]
    if avertissements:
        lignes += ["## Avertissements", ""]
        lignes += [f"- {a}" for a in avertissements]
        lignes.append("")
    lignes.append(f"Duree totale estimee : {sum(s['duree_s'] for s in scenes):.1f}s "
                   f"({len(scenes)} scenes)")
    lignes.append("")
    lignes.append("Les durees sont des estimations (~2.5 mots/s). Elles sont recalees "
                   "sur l'audio reel au montage, a partir de `04_phrases.json` (§7.2).")
    lignes.append("")
    for s in scenes:
        marque = " — **A COMPLETER**" if s.get("a_completer") else ""
        lignes.append(f"## {s['id']} — {s['composant']} ({s['duree_s']}s){marque}")
        lignes.append("")
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

    scenes, nouveaux = construire_scenes(phrases, composants_disponibles, da_par_defaut(charte))
    a_completer = sum(1 for s in scenes if s.get("a_completer"))
    if a_completer:
        avertissements.append(
            f"{a_completer} scene(s) marquee(s) `a_completer` : squelette genere, "
            "composant / parametres / direction artistique restent a trancher par A6 (§8)."
        )
    duree_totale = round(sum(s["duree_s"] for s in scenes), 1)

    sortie = {
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
    chemin_md.write_text(rendre_markdown(a.video, scenes, avertissements), encoding="utf-8")

    sortir(0, nb_scenes=len(scenes), nouveaux_composants=nouveaux,
           duree_totale_s=duree_totale, scenes_a_completer=a_completer,
           avertissements=avertissements)


if __name__ == "__main__":
    main()
