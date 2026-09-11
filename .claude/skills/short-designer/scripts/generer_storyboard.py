#!/usr/bin/env python3
"""
generer_storyboard.py — construit le storyboard (05_storyboard.md/.json) a
partir du script TTS calibre, pour l'etape E5_storyboard (§4.3, §8, A6).

Une phrase de 03_script_tts.txt = une scene. Le composant est choisi dans
le registre Remotion existant (composants/src/components/registry.ts) ;
s'il n'existe pas encore, il est quand meme nomme dans le storyboard et
signale dans "nouveaux_composants_necessaires" pour le Monteur (A7, §8) —
ce script ne cree jamais de composant.

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


def sortir(code, **data):
    print(json.dumps({"ok": code == 0, **data}, ensure_ascii=False, indent=2))
    sys.exit(code)


def lire_phrases(chemin):
    lignes = chemin.read_text(encoding="utf-8").splitlines()
    return [l.strip() for l in lignes if l.strip()]


def lire_json_defaut(chemin, defaut=None):
    try:
        return json.loads(chemin.read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError, OSError):
        return defaut


def parser_registre(chemin):
    if not chemin.is_file():
        return []
    contenu = chemin.read_text(encoding="utf-8")
    m = re.search(r"REGISTRE[^{]*\{(.*?)\}", contenu, re.DOTALL)
    if not m:
        return []
    noms = []
    for morceau in m.group(1).split(","):
        nom = morceau.strip().split(":")[0].strip()
        if re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", nom):
            noms.append(nom)
    return noms


def duree_pour(phrase):
    nb_mots = len(phrase.split())
    return round(max(nb_mots / MOTS_PAR_SECONDE, DUREE_MIN_S), 1)


def composant_ideal(index):
    # V1 (§8) : un seul composant existe, utilise pour le hook et le corps.
    # Point d'extension pour de futures scenes (ex. citation, comparaison).
    return "TitleCard"


def construire_scenes(phrases, composants_disponibles):
    scenes = []
    nouveaux = []
    for i, phrase in enumerate(phrases):
        nom = composant_ideal(i)
        if nom not in composants_disponibles and nom not in nouveaux:
            nouveaux.append(nom)
        scenes.append({
            "id": f"s{i + 1}",
            "composant": nom,
            "duree_s": duree_pour(phrase),
            "params": {"texte": phrase},
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
    for s in scenes:
        lignes.append(f"## {s['id']} — {s['composant']} ({s['duree_s']}s)")
        lignes.append("")
        lignes.append(s["params"].get("texte", ""))
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

    scenes, nouveaux = construire_scenes(phrases, composants_disponibles)
    duree_totale = round(sum(s["duree_s"] for s in scenes), 1)

    sortie = {"scenes": scenes, "nouveaux_composants_necessaires": nouveaux}

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
           duree_totale_s=duree_totale, avertissements=avertissements)


if __name__ == "__main__":
    main()
