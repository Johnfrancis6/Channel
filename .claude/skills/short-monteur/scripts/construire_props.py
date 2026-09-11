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
import sys


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


def main():
    ap = argparse.ArgumentParser(description="Assemble les props Remotion pour le rendu (§8).")
    ap.add_argument("--charte", required=True)
    ap.add_argument("--storyboard", required=True)
    ap.add_argument("--timestamps", required=True)
    ap.add_argument("--audio")
    ap.add_argument("--sortie", required=True)
    a = ap.parse_args()

    with open(a.charte, encoding="utf-8") as f:
        charte = json.load(f)
    with open(a.storyboard, encoding="utf-8") as f:
        storyboard = json.load(f)
    with open(a.timestamps, encoding="utf-8") as f:
        timestamps_bruts = json.load(f)

    try:
        props = construire(charte, storyboard, timestamps_bruts, a.audio)
    except ValueError as e:
        print(json.dumps({"ok": False, "message": str(e)}, ensure_ascii=False))
        sys.exit(2)

    with open(a.sortie, "w", encoding="utf-8") as f:
        json.dump(props, f, ensure_ascii=False, indent=2)

    print(json.dumps({"ok": True, "sortie": a.sortie, "nb_scenes": len(props["scenes"]),
                      "nb_mots": len(props["mots"])}, ensure_ascii=False))


if __name__ == "__main__":
    main()
