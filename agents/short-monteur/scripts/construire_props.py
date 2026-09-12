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
apres l'audio. Chaque scene declare les phrases qu'elle couvre (cle
`phrases`), parce qu'une scene en illustre souvent plusieurs ; a defaut, on
retombe sur l'appariement 1 pour 1 quand les nombres coincident.

`--phrases` sert aussi a resoudre les **accents ponctuels** : quand
`da.accent` designe une phrase ("boite 3 pulse au debut de la phrase 7"),
la scene recoit `pulsation_s`, l'instant reel de cette phrase compte depuis
le debut de la scene. Le milieu chronometrique d'une scene qui couvre
quatre phrases ne tombe sur aucun mot en particulier.

Normalise `04_timestamps.json` quelle que soit sa forme exacte (le
notebook voix off n'est pas encore fige, §13 etape 4) : accepte une liste
de mots avec les cles word/start/end (convention faster-whisper) ou
mot/debut_s/fin_s, au besoin enveloppee dans {"mots": [...]} ou
{"words": [...]} ou {"segments": [...]}.
"""
import argparse
import json
import re
import shutil
import sys
from pathlib import Path


# A6 designe la phrase qui porte l'accent en clair dans `da.accent` ("boite 3
# pulse au debut de la phrase 7"). Le vocabulaire de la DA est ferme, mais
# `accent` est du texte libre par construction (§8) : c'est la seule facon
# d'y designer une phrase precise. On ne lit que le numero.
MOTIF_PHRASE_ACCENT = re.compile(r"\bphrase\s+(\d+)", re.IGNORECASE)


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


def _fins_par_scene(scenes, phrases):
    """
    Fin de chaque scene, en secondes, ou None si on ne sait pas la calculer.

    Deux appariements, dans cet ordre :

    1. **chaque scene declare les phrases qu'elle couvre** (`phrases`, ecrit
       par le squelette d'A6 et fusionne par A6 quand il fusionne des
       scenes). C'est le cas general : une scene illustre souvent plusieurs
       phrases ;
    2. **autant de scenes que de phrases** : l'appariement 1 pour 1 des
       storyboards qui n'ont pas encore la cle `phrases`.

    Sinon on ne devine pas. Un appariement par index sur des nombres
    differents decalerait tout le montage, ce qui est pire que de garder
    l'estimation du storyboard.
    """
    numeros = [s.get("phrases") for s in scenes]
    if all(isinstance(n, list) and n for n in numeros):
        fins = []
        for n in numeros:
            dernier = max(int(x) for x in n)
            if not 1 <= dernier <= len(phrases):
                return None
            fins.append(float(phrases[dernier - 1]["fin_s"]))
        return fins
    if len(scenes) == len(phrases):
        return [float(p["fin_s"]) for p in phrases]
    return None


def _pulsation_s(scene, debut_scene_s, phrases):
    """
    Instant de l'accent ponctuel demande par la DA, en secondes depuis le
    debut de la scene — ou None si la scene n'en demande pas.

    Le milieu chronometrique d'une scene ne veut rien dire : une scene de
    15 s qui couvre quatre phrases a son moment fort la ou le benefice est
    prononce, pas a 7,5 s. A6 designe donc la phrase dans `da.accent`, et
    c'est au montage — seul endroit ou 04_phrases.json est connu — qu'elle
    devient un instant.

    Retourne (pulsation_s, avertissement).
    """
    accent = ((scene.get("da") or {}).get("accent") or "")
    m = MOTIF_PHRASE_ACCENT.search(accent)
    if not m:
        return None, None
    index = int(m.group(1))
    ref = f"scene {scene.get('id')} : accent sur la phrase {index}"
    if not 1 <= index <= len(phrases):
        return None, f"{ref}, hors des {len(phrases)} phrases de 04_phrases.json — accent ignore."
    couvertes = scene.get("phrases")
    if isinstance(couvertes, list) and couvertes and index not in [int(x) for x in couvertes]:
        # Une phrase hors de la scene tomberait pendant une autre scene : le
        # composant ne la verrait jamais, ou la verrait au mauvais moment.
        return None, f"{ref}, qui n'est pas dans les phrases couvertes {couvertes} — accent ignore."
    return round(max(float(phrases[index - 1]["debut_s"]) - debut_scene_s, 0.0), 3), None


def recaler_scenes(scenes, phrases_json):
    """
    Cale les durees de scenes sur les bornes reelles des phrases.

    Retourne (scenes, duree_audio_s, avertissements). Les scenes se suivent
    sans trou : la duree d'une scene va de la fin de la phrase precedente a
    la fin de la sienne, ce qui absorbe la pause inter-phrases. La derniere
    scene est prolongee jusqu'au bout de l'audio.
    """
    phrases = phrases_json.get("phrases") or []
    duree_totale = phrases_json.get("duree_totale_s")
    if not phrases:
        return scenes, duree_totale, ["04_phrases.json ne contient aucune phrase — durees du storyboard conservees."]

    fins = _fins_par_scene(scenes, phrases)
    if fins is None:
        return scenes, duree_totale, [
            f"{len(phrases)} phrases pour {len(scenes)} scenes, et les scenes ne disent "
            "pas quelles phrases elles couvrent — recalage impossible, durees du "
            "storyboard conservees. Ajoute la cle `phrases` a chaque scene du "
            "storyboard (§8) : c'est ce qui permet a une scene d'en illustrer "
            "plusieurs sans perdre le recalage."
        ]

    fin_audio = duree_totale if duree_totale is not None else float(phrases[-1]["fin_s"])
    scenes_recalees = []
    avertissements = []
    precedent = 0.0
    for i, scene in enumerate(scenes):
        # La derniere scene va jusqu'au bout de l'audio : sinon la video
        # s'arrete avant la voix off.
        fin = fin_audio if i == len(scenes) - 1 else fins[i]
        duree = round(max(fin - precedent, 0.1), 3)
        recalee = {**scene, "duree_s": duree, "duree_s_storyboard": scene.get("duree_s")}
        pulsation, avertissement = _pulsation_s(scene, precedent, phrases)
        if pulsation is not None:
            recalee["pulsation_s"] = pulsation
        if avertissement:
            avertissements.append(avertissement)
        scenes_recalees.append(recalee)
        precedent = max(fin, precedent)
    return scenes_recalees, fin_audio, avertissements


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

    # Le recalage se constate sur les scenes elles-memes (`duree_s_storyboard`
    # n'est ecrit que par recaler_scenes), pas sur l'absence d'avertissement :
    # un accent non resolu n'empeche pas les durees d'etre calees.
    recalees = [s for s in props["scenes"] if "duree_s_storyboard" in s]
    pulsations = {s["id"]: s["pulsation_s"] for s in props["scenes"] if "pulsation_s" in s}
    print(json.dumps({"ok": True, "sortie": a.sortie, "nb_scenes": len(props["scenes"]),
                      "nb_mots": len(props["mots"]),
                      "duree_audio_s": props.get("duree_audio_s"),
                      "scenes_recalees": len(recalees) == len(props["scenes"]) and bool(recalees),
                      "pulsations_s": pulsations,
                      "avertissements": avertissements}, ensure_ascii=False))


if __name__ == "__main__":
    main()
