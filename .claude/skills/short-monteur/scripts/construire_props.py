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


def _charger_formats_video():
    """Importe outils/formats_video.py, source unique des valeurs de format.

    On cherche le repere plutot que de compter les niveaux : le fichier vit a
    `outils/` a la racine du depot et a `<skill>/outils/` une fois le skill
    deploye (§9.2), deux profondeurs differentes — le defaut deja corrige
    dans `rendre_video.py`.
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


def appliquer_format(charte, format_video):
    """Ecrit dans `charte.format` les dimensions du format de la video.

    `Root.tsx` lit `props.charte.format` dans `calculateMetadata` depuis le
    16/09/2026 : c'est le seul endroit ou la composition apprend ses
    dimensions. Un format long rendu avec la charte telle quelle sortirait
    donc en 1080x1920 — du paysage compose dans un cadre vertical.

    Trois sources, de la plus explicite a la plus implicite :

    1. `charte.formats[<format>]`, si Franco l'a renseigne. C'est la seule
       facon pour lui de choisir autre chose que du 16/9 sans toucher au code ;
    2. pour un Short sans ce bloc, `charte.format` **tel quel** : le champ
       historique *est* le format court, et l'ecraser avec une valeur par
       defaut effacerait une resolution ou un fps que Franco aurait regles ;
    3. pour un long sans ce bloc, la rotation de `charte.format` — on garde sa
       resolution et son fps, on echange largeur et hauteur. Imposer 1920x1080
       jetterait ses reglages au passage.

    Retourne (charte, avertissements). La charte d'entree n'est pas modifiee.
    """
    formats_charte = charte.get("formats") or {}
    avertissements = []

    declare = formats_charte.get(format_video)
    if isinstance(declare, dict) and declare.get("largeur_px") and declare.get("hauteur_px"):
        return {**charte, "format": dict(declare)}, avertissements

    actuel = charte.get("format") or {}
    if format_video == formats_video.SHORT:
        # Sans avertissement : une charte anterieure au 16/09/2026 n'a pas de
        # bloc `format`, et `Root.tsx` retombe de toute facon sur la meme
        # amorce verticale. Il n'y a rien a corriger, donc rien a signaler.
        return ({**charte, "format": formats_video.dimensions(format_video)}
                if not actuel else charte), avertissements

    largeur, hauteur = actuel.get("largeur_px"), actuel.get("hauteur_px")
    if not largeur or not hauteur:
        return {**charte, "format": formats_video.dimensions(format_video)}, [
            "charte.json sans bloc `format` — dimensions par defaut du format long utilisees."]

    tourne = {"largeur_px": max(largeur, hauteur), "hauteur_px": min(largeur, hauteur)}
    if actuel.get("fps"):
        tourne["fps"] = actuel["fps"]
    if (tourne["largeur_px"], tourne["hauteur_px"]) != (largeur, hauteur):
        avertissements.append(
            f"Format long sans `charte.formats.long` : dimensions deduites de charte.format "
            f"par rotation ({largeur}x{hauteur} -> {tourne['largeur_px']}x{tourne['hauteur_px']}). "
            "Ajoute le bloc `formats` a charte.json pour le choisir explicitement.")
    return {**charte, "format": tourne}, avertissements


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


# Duree d'un insert quand ni le storyboard ni la ressource ne la disent. Un
# zoom sur un point precis se regarde et se quitte : au-dela, ce n'est plus
# un insert, c'est un plan — et le format long a `PlanBroll` pour ca.
DUREE_INSERT_DEFAUT_S = 3.0


def resoudre_inserts(scenes, phrases, ressources):
    """Resout les inserts de footage declares sur les scenes (§8).

    Un insert est un **detail dans une scene**, pas une scene de plus : la
    scene animee continue, et un clip reel apparait par-dessus pendant
    quelques secondes, sur le point precis dont parle le script. C'est la
    meme famille que `Subtitles` — une surcouche bornee, hors du registre —
    et pas un composant de scene, qui occuperait tout le cadre et redeviendrait
    le plan de liaison que la contrainte interdit.

    A6 designe le debut en clair (`"phrase 7"`), exactement comme `da.accent`,
    parce que c'est la seule chose qu'il connaisse au moment du storyboard :
    les secondes n'existent qu'apres la voix off. La conversion se fait ici,
    seul endroit ou 04_phrases.json est connu.

    Retourne (scenes, avertissements). Un insert dont la ressource manque est
    **retire** : la scene animee reste valide sans lui, alors qu'une URL vide
    produirait un trou noir au milieu du cadre.
    """
    avertissements = []
    sorties = []
    debut_scene = 0.0
    for scene in scenes:
        inserts = scene.get("inserts")
        duree_scene = float(scene.get("duree_s") or 0.0)
        if not isinstance(inserts, list) or not inserts:
            sorties.append(scene)
            debut_scene += duree_scene
            continue

        resolus = []
        for position, insert in enumerate(inserts):
            ref = f"scene {scene.get('id')}, insert {position + 1}"
            cle = insert.get("cle")
            if not cle:
                avertissements.append(f"{ref} : sans `cle` de ressource — ignore.")
                continue
            if ressources is not None and cle not in ressources:
                avertissements.append(
                    f"{ref} : ressource « {cle} » absente de 05b_ressources.json — insert "
                    "retire. La scene animee est rendue sans lui.")
                continue

            debut_s = insert.get("debut_s")
            if debut_s is None:
                m = MOTIF_PHRASE_ACCENT.search(insert.get("debut") or "")
                if not m:
                    avertissements.append(
                        f"{ref} : ni `debut_s` ni `debut` designant une phrase "
                        "(ex. « phrase 7 ») — insert retire.")
                    continue
                index = int(m.group(1))
                if not phrases or not 1 <= index <= len(phrases):
                    avertissements.append(
                        f"{ref} : phrase {index} introuvable dans 04_phrases.json — "
                        "insert retire.")
                    continue
                couvertes = scene.get("phrases")
                if isinstance(couvertes, list) and couvertes and index not in [int(x) for x in couvertes]:
                    # Une phrase hors de la scene placerait l'insert pendant
                    # une autre scene, ou hors du cadre temporel : il ne
                    # serait jamais vu, ou vu au mauvais moment.
                    avertissements.append(
                        f"{ref} : phrase {index} hors des phrases couvertes {couvertes} "
                        "— insert retire.")
                    continue
                debut_s = float(phrases[index - 1]["debut_s"]) - debut_scene

            debut_s = max(0.0, float(debut_s))
            if duree_scene and debut_s >= duree_scene:
                avertissements.append(
                    f"{ref} : commence a {debut_s:.1f}s alors que la scene dure "
                    f"{duree_scene:.1f}s — insert retire.")
                continue

            duree = insert.get("duree_s")
            if duree is None and ressources:
                duree = (ressources.get(cle) or {}).get("duree_s")
            duree = float(duree or DUREE_INSERT_DEFAUT_S)
            # Un insert ne deborde jamais de sa scene : au montage, la scene
            # suivante le couperait de toute facon, mais la duree ecrite dans
            # les props doit dire la verite — c'est elle qu'on relit au CP3.
            if duree_scene:
                restant = duree_scene - debut_s
                if duree > restant:
                    avertissements.append(
                        f"{ref} : raccourci de {duree:.1f}s a {restant:.1f}s pour tenir "
                        "dans la scene.")
                    duree = restant
            resolus.append({**insert, "cle": cle,
                            "debut_s": round(debut_s, 3),
                            "duree_s": round(duree, 3)})

        sorties.append({**scene, "inserts": resolus} if resolus
                       else {k: v for k, v in scene.items() if k != "inserts"})
        debut_scene += duree_scene
    return sorties, avertissements


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


def construire(charte, storyboard, timestamps_bruts, audio=None, phrases_json=None,
               ressources=None, format_video=None):
    scenes = storyboard.get("scenes", [])
    if not scenes:
        raise ValueError("Aucune scene dans le storyboard.")
    # Le format du storyboard fait foi quand l'appelant n'en impose pas :
    # c'est A6 qui a decoupe les scenes, et une video decoupee en segments
    # longs rendue au format Short serait cadree pour le mauvais ecran.
    if format_video is None:
        format_video = storyboard.get("format_video") or formats_video.FORMAT_DEFAUT
    charte, avertissements = appliquer_format(charte, format_video)
    duree_audio_s = None
    if phrases_json is not None:
        scenes, duree_audio_s, avert_recalage = recaler_scenes(scenes, phrases_json)
        avertissements += avert_recalage
    else:
        avertissements.append(
            "Aucun 04_phrases.json : les durees de scenes restent des estimations "
            "(~2.5 mots/s) et ne suivent pas la voix off."
        )
    # Apres le recalage : les durees de scenes sont alors definitives, donc
    # le debut de chaque scene aussi — et c'est de lui que se compte le
    # debut d'un insert.
    scenes, avert_inserts = resoudre_inserts(
        scenes, (phrases_json or {}).get("phrases") or [], ressources)
    avertissements += avert_inserts

    props = {"charte": charte, "scenes": scenes, "mots": normaliser_mots(timestamps_bruts),
             "format_video": format_video}
    if ressources:
        props["ressources"] = ressources
    if duree_audio_s is not None:
        props["duree_audio_s"] = duree_audio_s
    if audio:
        props["audioSrc"] = audio
    return props, avertissements


def copier_vers_public(source, video_id, categorie):
    """Copie un fichier dans composants/public/ et rend l'URL que le rendu
    saura servir.

    Le serveur de rendu de Remotion ne sert que ce dossier : un chemin
    absolu brut ou une URI file:// echouent tous les deux (404 / protocole
    non supporte). Suppose cwd == composants/ (cf. skill A7, etape 4).

    Ce tuyau existait deja, mais cable en dur pour 04_voixoff.wav — c'etait
    le **seul** asset du systeme, et la raison pour laquelle tout ce qui
    s'affichait devait d'abord etre dessine a la main en SVG. Le generaliser
    est ce qui ouvre les captures, les logos, les images et le b-roll.
    """
    source = Path(source).resolve()
    dossier_public = Path("public") / categorie / video_id
    dossier_public.mkdir(parents=True, exist_ok=True)
    dest = dossier_public / source.name
    shutil.copyfile(source, dest)
    # Le bundle de rendu sert le contenu de public/ sous le prefixe
    # /public/ (copie dans <outDir>/public par @remotion/bundler), pas a la
    # racine — verifie empiriquement, staticFile() ne s'applique pas ici
    # puisque ce chemin est ecrit en dur dans les props JSON.
    return f"/public/{categorie}/{video_id}/{source.name}"


def preparer_audio_public(audio_path):
    """Cas particulier historique : la voix off (§8)."""
    source = Path(audio_path).resolve()
    return copier_vers_public(source, source.parent.name, "audio")


# Les cles du fichier de ressources qu'on recopie telles quelles dans les
# props. Liste explicite : une cle interne a A8 (cout, requete d'origine,
# tentatives) n'a rien a faire dans le bundle de rendu.
CLES_RESSOURCE = ("type", "largeur_px", "hauteur_px", "duree_s", "provenance", "licence")


def preparer_ressources(chemin_ressources):
    """Resout 05b_ressources.json (ecrit par A8, E5b) en une table prete pour
    le rendu : chaque fichier est copie dans public/ et sa cle porte l'URL.

    Retourne (ressources, avertissements). Une ressource dont le fichier
    manque est **omise** plutot que fausse : le composant affiche alors
    « Ressource manquante » en clair, ce qui se voit au catalogue et au CP3.
    Une URL qui pointe dans le vide, elle, produirait un trou noir que
    personne ne remarque.
    """
    chemin = Path(chemin_ressources)
    if not chemin.is_file():
        return {}, [f"Aucun fichier de ressources a {chemin} : les plans qui en "
                    f"attendent afficheront « Ressource manquante »."]
    with open(chemin, encoding="utf-8-sig") as f:
        brut = json.load(f)

    dossier_video = chemin.resolve().parent
    video_id = brut.get("video_id") or dossier_video.name
    table = brut.get("ressources") or {}

    ressources = {}
    avertissements = []
    for cle, r in table.items():
        rel = r.get("chemin")
        if not rel:
            avertissements.append(f"Ressource « {cle} » sans champ `chemin` — ignoree.")
            continue
        source = Path(rel)
        if not source.is_absolute():
            source = dossier_video / rel
        if not source.is_file():
            avertissements.append(f"Ressource « {cle} » introuvable : {source} — ignoree.")
            continue
        entree = {k: r[k] for k in CLES_RESSOURCE if k in r}
        entree["src"] = copier_vers_public(source, video_id, "assets")
        entree.setdefault("type", "image")
        ressources[cle] = entree
    return ressources, avertissements


def main():
    ap = argparse.ArgumentParser(description="Assemble les props Remotion pour le rendu (§8).")
    ap.add_argument("--charte", required=True)
    ap.add_argument("--storyboard", required=True)
    ap.add_argument("--timestamps", required=True)
    ap.add_argument("--phrases", help="04_phrases.json (bornes par phrase) — recale les durees de scenes.")
    ap.add_argument("--audio")
    ap.add_argument("--format-video", dest="format_video",
                    choices=list(formats_video.FORMATS),
                    help="state.json > format_video. Choisit les dimensions de composition "
                         "(charte.formats, sinon rotation de charte.format). Defaut : "
                         "ce que declare le storyboard, sinon short.")
    ap.add_argument("--ressources",
                    help="05b_ressources.json (ecrit par A8, E5b) — captures, logos, images, b-roll.")
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

    ressources, avert_ressources = ({}, [])
    if a.ressources:
        ressources, avert_ressources = preparer_ressources(a.ressources)

    try:
        props, avertissements = construire(charte, storyboard, timestamps_bruts, audio_src,
                                           phrases_json, ressources, a.format_video)
    except ValueError as e:
        print(json.dumps({"ok": False, "message": str(e)}, ensure_ascii=False))
        sys.exit(2)

    with open(a.sortie, "w", encoding="utf-8") as f:
        json.dump(props, f, ensure_ascii=False, indent=2)

    # Le recalage se constate sur les scenes elles-memes (`duree_s_storyboard`
    # n'est ecrit que par recaler_scenes), pas sur l'absence d'avertissement :
    # un accent non resolu n'empeche pas les durees d'etre calees.
    avertissements = avert_ressources + avertissements
    recalees = [s for s in props["scenes"] if "duree_s_storyboard" in s]
    pulsations = {s["id"]: s["pulsation_s"] for s in props["scenes"] if "pulsation_s" in s}
    print(json.dumps({"ok": True, "sortie": a.sortie, "nb_scenes": len(props["scenes"]),
                      "nb_mots": len(props["mots"]),
                      "format_video": props["format_video"],
                      "dimensions": props["charte"].get("format"),
                      "nb_ressources": len(ressources),
                      "duree_audio_s": props.get("duree_audio_s"),
                      "scenes_recalees": len(recalees) == len(props["scenes"]) and bool(recalees),
                      "pulsations_s": pulsations,
                      "nb_inserts": sum(len(s.get("inserts") or []) for s in props["scenes"]),
                      "avertissements": avertissements}, ensure_ascii=False))


if __name__ == "__main__":
    main()
