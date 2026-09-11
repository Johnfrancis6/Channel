#!/usr/bin/env python3
"""
construire_props.py — assemble les props Remotion (charte + scenes +
mots horodates) pour rendre une video (§8), a partir des sorties du
pipeline.

Usage :
  python3 construire_props.py --charte CHARTE.json --storyboard 05_storyboard.json \
      --timestamps 04_timestamps.json [--audio 04_voixoff.wav] --sortie props.json

Normalise `04_timestamps.json` quelle que soit sa forme exacte (le
notebook voix off n'est pas encore fige, §13 etape 4) : accepte une liste
de mots avec les cles word/start/end (convention faster-whisper) ou
mot/debut_s/fin_s, au besoin enveloppee dans {"mots": [...]} ou
{"words": [...]} ou {"segments": [...]}.
"""
import argparse
import json
import shutil
import sys
from pathlib import Path


def normaliser_mots(data):
    if isinstance(data, dict):
        data = data.get("mots") or data.get("words") or data.get("segments") or []
    mots = []
    for m in data:
        mot = m.get("mot", m.get("word", m.get("text")))
        debut = m.get("debut_s", m.get("start"))
        fin = m.get("fin_s", m.get("end"))
        if mot is None or debut is None or fin is None:
            continue
        mots.append({"mot": str(mot).strip(), "debut_s": float(debut), "fin_s": float(fin)})
    return mots


def construire(charte, storyboard, timestamps_bruts, audio=None):
    scenes = storyboard.get("scenes", [])
    if not scenes:
        raise ValueError("Aucune scene dans le storyboard.")
    props = {"charte": charte, "scenes": scenes, "mots": normaliser_mots(timestamps_bruts)}
    if audio:
        props["audioSrc"] = audio
    return props


def preparer_audio_public(audio_path):
    """Copie l'audio dans composants/public/ (§8) : le serveur de rendu de
    Remotion sert les assets locaux depuis ce dossier, a la racine — un
    chemin absolu brut ou une URI file:// echouent tous les deux (404 /
    protocole non supporte). Suppose cwd == composants/ (cf. skill A7,
    etape 4)."""
    source = Path(audio_path).resolve()
    video_id = source.parent.name
    dossier_public = Path("public") / "audio" / video_id
    dossier_public.mkdir(parents=True, exist_ok=True)
    dest = dossier_public / source.name
    shutil.copyfile(source, dest)
    # Le bundle de rendu sert le contenu de public/ sous le prefixe
    # /public/ (copie dans <outDir>/public par @remotion/bundler), pas a la
    # racine — verifie empiriquement, staticFile() ne s'applique pas ici
    # puisque ce chemin est ecrit en dur dans les props JSON.
    return f"/public/audio/{video_id}/{source.name}"


def main():
    ap = argparse.ArgumentParser(description="Assemble les props Remotion pour le rendu (§8).")
    ap.add_argument("--charte", required=True)
    ap.add_argument("--storyboard", required=True)
    ap.add_argument("--timestamps", required=True)
    ap.add_argument("--audio")
    ap.add_argument("--sortie", required=True)
    a = ap.parse_args()

    with open(a.charte, encoding="utf-8-sig") as f:
        charte = json.load(f)
    with open(a.storyboard, encoding="utf-8-sig") as f:
        storyboard = json.load(f)
    with open(a.timestamps, encoding="utf-8-sig") as f:
        timestamps_bruts = json.load(f)

    audio_src = preparer_audio_public(a.audio) if a.audio else None

    try:
        props = construire(charte, storyboard, timestamps_bruts, audio_src)
    except ValueError as e:
        print(json.dumps({"ok": False, "message": str(e)}, ensure_ascii=False))
        sys.exit(2)

    with open(a.sortie, "w", encoding="utf-8") as f:
        json.dump(props, f, ensure_ascii=False, indent=2)

    print(json.dumps({"ok": True, "sortie": a.sortie, "nb_scenes": len(props["scenes"]),
                      "nb_mots": len(props["mots"])}, ensure_ascii=False))


if __name__ == "__main__":
    main()
