#!/usr/bin/env python3
"""
construire_props.py — assemble les props Remotion (charte + scenes +
mots horodates) pour rendre une video (§8), a partir des sorties du
pipeline.

Usage :
  python3 construire_props.py --charte CHARTE.json --storyboard 05_storyboard.json \
      --timestamps 04_timestamps.json [--phrases 04_phrases.json] \
      [--audio 04_voixoff.wav] --sortie props.json

`--phrases` (04_phrases.json, ecrit par le notebook voix off) recale les
durees de scenes sur l'audio reellement synthetise. Sans lui, les scenes
gardent l'estimation a ~2.5 mots/s du storyboard : le visuel derive de la
voix des la premiere phrase un peu longue, et la video se termine avant ou
apres l'audio. A6 fait une scene par phrase, donc le recalage est un simple
appariement par index.

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


def recaler_scenes(scenes, phrases_json):
    """
    Cale les durees de scenes sur les bornes reelles des phrases.

    Retourne (scenes, duree_audio_s, avertissements). Les scenes se suivent
    sans trou : la duree d'une scene va de la fin de la phrase precedente a
    la fin de la sienne, ce qui absorbe la pause inter-phrases. La derniere
    scene est prolongee jusqu'au bout de l'audio.

    En cas de desaccord de nombre (A6 a fusionne ou coupe des scenes,
    storyboard d'avant la revue du 11/09/2026), on ne recale rien : mieux
    vaut l'estimation du storyboard qu'un appariement par index qui
    decalerait tout le montage. L'avertissement remonte a l'agent.
    """
    phrases = phrases_json.get("phrases") or []
    duree_totale = phrases_json.get("duree_totale_s")
    if not phrases:
        return scenes, duree_totale, ["04_phrases.json ne contient aucune phrase — durees du storyboard conservees."]
    if len(phrases) != len(scenes):
        return scenes, duree_totale, [
            f"{len(phrases)} phrases pour {len(scenes)} scenes — recalage impossible, "
            "durees du storyboard conservees. Verifie que le storyboard suit bien "
            "03_script_tts.txt ligne a ligne (§8)."
        ]

    fin_audio = duree_totale if duree_totale is not None else float(phrases[-1]["fin_s"])
    scenes_recalees = []
    precedent = 0.0
    for i, (scene, phrase) in enumerate(zip(scenes, phrases)):
        fin = fin_audio if i == len(phrases) - 1 else float(phrase["fin_s"])
        duree = round(max(fin - precedent, 0.1), 3)
        scenes_recalees.append({**scene, "duree_s": duree, "duree_s_storyboard": scene.get("duree_s")})
        precedent = fin
    return scenes_recalees, fin_audio, []


def construire(charte, storyboard, timestamps_bruts, audio=None, phrases_json=None):
    scenes = storyboard.get("scenes", [])
    if not scenes:
        raise ValueError("Aucune scene dans le storyboard.")
    avertissements = []
    duree_audio_s = None
    if phrases_json is not None:
        scenes, duree_audio_s, avertissements = recaler_scenes(scenes, phrases_json)
    else:
        avertissements.append(
            "Aucun 04_phrases.json : les durees de scenes restent des estimations "
            "(~2.5 mots/s) et ne suivent pas la voix off."
        )
    props = {"charte": charte, "scenes": scenes, "mots": normaliser_mots(timestamps_bruts)}
    if duree_audio_s is not None:
        props["duree_audio_s"] = duree_audio_s
    if audio:
        props["audioSrc"] = audio
    return props, avertissements


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
    ap.add_argument("--phrases", help="04_phrases.json (bornes par phrase) — recale les durees de scenes.")
    ap.add_argument("--audio")
    ap.add_argument("--sortie", required=True)
    a = ap.parse_args()

    with open(a.charte, encoding="utf-8-sig") as f:
        charte = json.load(f)
    with open(a.storyboard, encoding="utf-8-sig") as f:
        storyboard = json.load(f)
    with open(a.timestamps, encoding="utf-8-sig") as f:
        timestamps_bruts = json.load(f)

    phrases_json = None
    if a.phrases:
        chemin_phrases = Path(a.phrases)
        if chemin_phrases.is_file():
            with open(chemin_phrases, encoding="utf-8-sig") as f:
                phrases_json = json.load(f)

    audio_src = preparer_audio_public(a.audio) if a.audio else None

    try:
        props, avertissements = construire(charte, storyboard, timestamps_bruts, audio_src, phrases_json)
    except ValueError as e:
        print(json.dumps({"ok": False, "message": str(e)}, ensure_ascii=False))
        sys.exit(2)

    with open(a.sortie, "w", encoding="utf-8") as f:
        json.dump(props, f, ensure_ascii=False, indent=2)

    print(json.dumps({"ok": True, "sortie": a.sortie, "nb_scenes": len(props["scenes"]),
                      "nb_mots": len(props["mots"]),
                      "duree_audio_s": props.get("duree_audio_s"),
                      "scenes_recalees": bool(props.get("duree_audio_s")) and not avertissements,
                      "avertissements": avertissements}, ensure_ascii=False))


if __name__ == "__main__":
    main()
