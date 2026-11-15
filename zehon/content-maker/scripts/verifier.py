#!/usr/bin/env python3
"""Contrôles automatiques des livrables content-maker (Zehon).

Le jugement (la qualité du récit, l'exactitude) reste au modèle et à Franco.
Ce script ne vérifie que ce qui se compte : longueurs, formats, continuité.

Usage :
  python3 verifier.py 02_script.md
  python3 verifier.py 02_script_voix.txt
  python3 verifier.py 03_scenes.md [--script 02_script.md]
                    (types de scène : image, video, photo, titre)
  Option --debit 3.21 : le débit de la voix en mots/s, pauses comprises
                    (« Réglages mesurés » de Memoire/lecons.md), pour la durée.

Sortie : une ligne par problème, préfixée ERREUR (à corriger) ou
AVERTISSEMENT (à regarder), puis un bilan. Code 1 s'il reste une erreur.
"""
import re
import statistics
import sys
import unicodedata
from pathlib import Path

MOTS_CIBLE = (1400, 1560)
PHRASE_MAX_SCRIPT = 25
PHRASE_MAX_VOIX = 22
PHRASE_MIN_VOIX = 4
SCENES_CIBLE = (60, 80)
TYPES = {"image", "video", "photo", "preuve", "titre"}  # « preuve » : ancien nom de « photo »
# Voix de la chaîne, pauses comprises. Calculé, pas mesuré : le sel, 1 551 mots en 461,8 s mesurés avec
# 300 ms de pause, plus 21 s pour la pause passée à 450 ms (140 phrases) = 482,8 s. À remesurer sur la
# prochaine voix.
DEBIT_MOTS_S = 3.21
SAUF_QUE_MAX = 5     # au-delà, la charnière devient un tic (9 fins de bloc sur 10 dans l'aluminium)
NOMBRES_MAX = 40     # nombres en chiffres dans le script : une histoire, pas un exposé (verre 20, alu 48, sel 53)
NOMBRES_HOOK_MAX = 2
HOOK_MOTS_MAX = 15   # mots de « texte dit » par scène du hook (avant le premier titre) : 4 à 5 s à l'écran
VIDEOS_MAX = 12  # plans animés : quelques-uns par vidéo, pas plus (quota de génération)
MOUVEMENTS = {"zoom_avant", "zoom_arriere", "pan_gauche", "pan_droite"}
RE_CTA = re.compile(r"abonne|pouce bleu|\blike\b|la cloche|partage[sz]? (la|cette) vid", re.I)
RE_LICENCE = re.compile(r"CC0|CC[ -]BY|domaine public|public domain", re.I)

problemes = []

debit = DEBIT_MOTS_S


def erreur(msg):
    problemes.append(("ERREUR", msg))


def avertir(msg):
    problemes.append(("AVERTISSEMENT", msg))


def mots(texte):
    return re.findall(r"[\w’'-]+", texte)


def phrases(texte):
    texte = " ".join(texte.split())
    return [p for p in re.split(r"(?<=[.!?…])\s+", texte) if p.strip()]


def nombres(texte):
    """Les nombres écrits en chiffres : « 1344 », « 2 834 », « 3,6 », « 8 % » comptent chacun pour un."""
    return re.findall(r"\d+(?:[   .,]\d+)*", texte)


def texte_du_script(contenu):
    """Le texte dit : sans titres, commentaires ni lignes vides."""
    contenu = re.sub(r"<!--.*?-->", " ", contenu, flags=re.S)
    lignes = [l for l in contenu.splitlines() if l.strip() and not l.lstrip().startswith("#")]
    return re.sub(r"[*_`>]", "", "\n".join(lignes))


def blocs(contenu):
    """{titre de bloc: texte} d'après les titres ## du script."""
    resultat, courant = {}, None
    for ligne in contenu.splitlines():
        m = re.match(r"^##\s+(.*)", ligne)
        if m:
            courant = m.group(1).strip()
            resultat[courant] = ""
        elif courant and not ligne.lstrip().startswith("#"):
            resultat[courant] += ligne + "\n"
    return resultat


def verifier_script(chemin):
    contenu = Path(chemin).read_text(encoding="utf-8")
    texte = texte_du_script(contenu)
    n = len(mots(texte))
    if not MOTS_CIBLE[0] <= n <= MOTS_CIBLE[1]:
        avertir(f"{n} mots (cible {MOTS_CIBLE[0]}-{MOTS_CIBLE[1]}, environ 8 min)")

    ps = phrases(texte)
    longueurs = [len(mots(p)) for p in ps]
    trop_longues = [p for p in ps if len(mots(p)) > PHRASE_MAX_SCRIPT]
    for p in trop_longues[:5]:
        avertir(f"phrase de {len(mots(p))} mots (max {PHRASE_MAX_SCRIPT}) : « {p[:80]}… »")

    parties = blocs(contenu)
    hook = next((t for titre, t in parties.items() if "hook" in titre.lower()), None)
    if hook is None:
        avertir("pas de bloc « ## Hook » : position de la question non vérifiée")
    else:
        ph = phrases(texte_du_script(hook))
        rang = next((i + 1 for i, p in enumerate(ph) if p.rstrip().endswith("?")), None)
        if rang is None:
            erreur("le hook ne pose aucune question")
        elif rang > 9:
            erreur(f"la question du hook tombe à la phrase {rang} (au plus tard la 9e)")
        n_hook = len(nombres(texte_du_script(hook)))
        if n_hook > NOMBRES_HOOK_MAX:
            avertir(f"{n_hook} nombres dans le hook (au plus {NOMBRES_HOOK_MAX}) : garder le plus frappant")

    n_sauf = len(re.findall(r"\bsauf qu(?:e\b|['’])", texte, re.I))
    if not n_sauf:
        avertir("aucun « Sauf que » : les obstacles entre les temps sont-ils là ?")
    elif n_sauf > SAUF_QUE_MAX:
        avertir(f"{n_sauf} « Sauf que » (au plus {SAUF_QUE_MAX}) : varier les charnières (« Mais », « Reste un problème », une question)")
    n_nombres = len(nombres(texte))
    if n_nombres > NOMBRES_MAX:
        avertir(f"{n_nombres} nombres en chiffres (au plus {NOMBRES_MAX}) : ne garder que ceux qui frappent")
    if RE_CTA.search(texte):
        erreur(f"appel à s'abonner ou à liker repéré : « {RE_CTA.search(texte).group(0)} »")
    if ps and not ps[-1].rstrip().endswith("?"):
        avertir("la dernière phrase n'est pas une question ouverte")

    med = statistics.median(longueurs) if longueurs else 0
    return (f"{n} mots, {len(ps)} phrases, médiane {med} mots, {n_sauf} « Sauf que », {n_nombres} nombres, "
            f"~{n / debit / 60:.1f} min à {debit:g} mots/s (la durée se juge sur la version voix)")


def verifier_voix(chemin):
    lignes = [l.strip() for l in Path(chemin).read_text(encoding="utf-8").splitlines() if l.strip()]
    total = 0
    for i, ligne in enumerate(lignes, 1):
        n = len(mots(ligne))
        total += n
        if n > PHRASE_MAX_VOIX:
            erreur(f"ligne {i} : {n} mots (max {PHRASE_MAX_VOIX}), à couper")
        elif n < PHRASE_MIN_VOIX:
            avertir(f"ligne {i} : {n} mots, à fusionner avec la voisine ?")
        if re.search(r"\d", ligne):
            erreur(f"ligne {i} : chiffre à écrire en lettres : « {ligne[:70]} »")
        if re.search(r"[%()\[\]/&€$§#*_<>=+]", ligne):
            erreur(f"ligne {i} : symbole ou parenthèse : « {ligne[:70]} »")
        sigle = re.search(r"\b[A-ZÀ-Ý]{2,}\b", ligne)
        if sigle:
            avertir(f"ligne {i} : sigle « {sigle.group(0)} », à dire en toutes lettres ?")
        if ligne.startswith("#"):
            erreur(f"ligne {i} : titre ou commentaire, rien que du texte prononcé")
    minutes = total / debit / 60
    if minutes > 9:
        avertir(f"durée estimée {minutes:.1f} min à {debit:g} mots/s : au-delà de 9 min, resserrer le script")
    elif minutes < 7.5 and total > 400:
        avertir(f"durée estimée {minutes:.1f} min à {debit:g} mots/s : en dessous de 7 min 30, la vidéo "
                "finit sous les 8 min, titres compris")
    return f"{len(lignes)} lignes, {total} mots, ~{minutes:.1f} min à {debit:g} mots/s (sans les titres)"


def normaliser(texte):
    texte = unicodedata.normalize("NFKC", texte).lower().replace("’", "'")
    return " ".join(re.findall(r"[\w']+", texte))


def cellules(ligne):
    return [c.strip() for c in ligne.strip().strip("|").split("|")]


def verifier_scenes(chemin, chemin_script=None):
    contenu = Path(chemin).read_text(encoding="utf-8")
    rangees = [cellules(l) for l in contenu.splitlines() if re.match(r"^\|\s*\d+\s*\|", l)]
    if not rangees:
        erreur("aucune ligne de scène trouvée (tableau « | n° | type | … | »)")
        return "0 scène"

    prompts = set(int(n) for n in re.findall(r"\*\*scene_(\d{3})\*\*", contenu))
    anims = set(int(n) for n in re.findall(r"\*\*anim_(\d{3})\*\*", contenu))
    n_video, n_reprises = 0, 0
    images_vues = set()  # numéros des scènes image ou video déjà passées : leur image peut resservir
    precedent, serie, n_texte = None, 0, 0
    textes = []
    # le hook : les scènes placées avant la première scène « titre » (aucun titre : pas de hook repéré)
    fin_hook = next((i for i, c in enumerate(rangees, 1) if len(c) == 7 and c[1] == "titre"), 0)
    for attendu, c in enumerate(rangees, 1):
        if len(c) != 7:
            erreur(f"scène {c[0]} : {len(c)} colonnes au lieu de 7")
            continue
        num, typ, dit, image, mouvement, anime, preuve = c
        if int(num) != attendu:
            erreur(f"numérotation : scène {num} à la place de {attendu}")
        textes.append(dit)
        if typ not in TYPES:
            erreur(f"scène {num} : type « {typ} » inconnu ({', '.join(sorted(TYPES))})")
        n_mots = len(mots(dit))
        if attendu < fin_hook:
            if n_mots > HOOK_MOTS_MAX:
                avertir(f"scène {num} : {n_mots} mots dans le hook (au plus {HOOK_MOTS_MAX}, soit 4 à 5 s)")
        elif typ != "titre" and not 10 <= n_mots <= 35:
            avertir(f"scène {num} : {n_mots} mots de texte dit (cible 18-25, soit 6 à 8 s)")
        if typ == "image":
            reprise = re.fullmatch(r"scene_(\d{3})\.png", image)
            if reprise and int(reprise.group(1)) != int(num) and int(reprise.group(1)) in images_vues:
                # l'image d'une scène précédente, reprise avec un autre mouvement : pas de prompt
                n_reprises += 1
                if int(num) in prompts:
                    avertir(f"scène {num} : prompt **scene_{int(num):03d}** inutile, la scène reprend {image}")
                if textes[:-1] and len(rangees[attendu - 2]) == 7 and rangees[attendu - 2][3] == image \
                        and rangees[attendu - 2][4] == mouvement:
                    avertir(f"scène {num} : même image et même mouvement que la scène d'avant, changer le mouvement")
            else:
                if image != f"scene_{int(num):03d}.png":
                    erreur(f"scène {num} : image « {image} », attendu scene_{int(num):03d}.png "
                           "(ou l'image d'une scène précédente, pour la reprendre)")
                if int(num) not in prompts:
                    erreur(f"scène {num} : aucun prompt **scene_{int(num):03d}**")
                images_vues.add(int(num))
        elif typ == "video":
            n_video += 1
            images_vues.add(int(num))
            if image != f"clips/scene_{int(num):03d}.mp4":
                erreur(f"scène {num} : clip « {image} », attendu clips/scene_{int(num):03d}.mp4")
            if int(num) not in prompts:
                erreur(f"scène {num} : aucun prompt **scene_{int(num):03d}** (l'image de départ du clip)")
            if int(num) not in anims:
                erreur(f"scène {num} : aucun prompt d'animation **anim_{int(num):03d}**")
            if mouvement not in ("—", "-", ""):
                erreur(f"scène {num} : un clip porte son propre mouvement (mouvement « — », pas « {mouvement} »)")
        elif typ in ("photo", "preuve"):
            if not image.startswith(("photos/", "preuves/")):
                erreur(f"scène {num} : une photo pointe vers photos/…, pas « {image} »")
            if preuve.upper().startswith("À TROUVER") or preuve.upper().startswith("A TROUVER"):
                avertir(f"scène {num} : preuve à trouver ({preuve[:80]}) — rendu impossible tant qu'elle manque")
            elif preuve in ("", "—", "-") or not RE_LICENCE.search(preuve):
                erreur(f"scène {num} : photo sans crédit ni licence (« {preuve} ») : sinon, en faire une scène image")
            if int(num) in prompts:
                avertir(f"scène {num} : prompt présent pour une scène photo (vraie photo attendue)")
        if typ not in ("titre", "video"):
            ok = mouvement in MOUVEMENTS or re.fullmatch(r"zoom_vers:0?\.\d+,0?\.\d+|zoom_vers:[01],[01]", mouvement or "")
            if not ok:
                erreur(f"scène {num} : mouvement « {mouvement} » inconnu")
            serie = serie + 1 if mouvement == precedent else 1
            precedent = mouvement
            if serie > 3:
                avertir(f"scène {num} : 4e « {mouvement} » de suite, alterner")
        if typ == "titre":
            if dit not in ("", "—", "-"):
                erreur(f"scène {num} : un titre n'est pas dit (texte dit « — », la question va en texte animé)")
            if anime in ("", "—", "-"):
                erreur(f"scène {num} : titre sans question dans « texte animé »")
        elif anime not in ("", "—", "-"):
            n_texte += 1

    for n in sorted(anims):
        typ_n = next((r[1] for r in rangees if len(r) == 7 and r[0] == str(n)), None)
        if typ_n != "video":
            erreur(f"prompt **anim_{n:03d}** pour la scène {n}, qui n'est pas de type video")
    if n_video > VIDEOS_MAX:
        avertir(f"{n_video} plans animés (au plus {VIDEOS_MAX} : quota de génération vidéo)")
    total = len(rangees)
    if not SCENES_CIBLE[0] <= total <= SCENES_CIBLE[1]:
        avertir(f"{total} scènes (cible {SCENES_CIBLE[0]}-{SCENES_CIBLE[1]} pour 8 min)")
    if n_texte > total / 3 + 1:
        avertir(f"texte animé sur {n_texte} scènes sur {total} (au plus une sur trois)")
    if re.search(r"\b(text|letters|words|caption|sign) (reading|saying|that says)", contenu, re.I):
        avertir("un prompt semble demander du texte dans l'image")

    if chemin_script:
        script = normaliser(texte_du_script(Path(chemin_script).read_text(encoding="utf-8")))
        scenes = normaliser(" ".join(t for t, r in zip(textes, rangees) if r[1] != "titre"))
        if script != scenes:
            i = next((k for k, (a, b) in enumerate(zip(script, scenes)) if a != b), min(len(script), len(scenes)))
            erreur("le texte dit ne redonne pas le script mot pour mot. Premier écart :\n"
                   f"    script : …{script[max(0, i - 40):i + 40]}…\n"
                   f"    scènes : …{scenes[max(0, i - 40):i + 40]}…")
    if n_reprises > total / 4:
        avertir(f"{n_reprises} images reprises sur {total} scènes (au plus une sur quatre) : la vidéo va sembler figée")
    return (f"{total} scènes dont {n_video} animées et {n_reprises} images reprises, {len(prompts)} prompts d'image, "
            f"{len(anims)} d'animation, texte animé sur {n_texte}")


def main(argv):
    global debit
    argv = list(argv)
    if "--debit" in argv:
        i = argv.index("--debit")
        try:
            debit = float(argv[i + 1].replace(",", "."))
        except (IndexError, ValueError):
            print("ERREUR : --debit attend un nombre de mots par seconde, par exemple --debit 3.21")
            return 2
        if not 1.5 <= debit <= 6:
            print(f"ERREUR : débit {debit:g} mots/s invraisemblable (entre 1,5 et 6)")
            return 2
        del argv[i:i + 2]
    if not argv:
        print(__doc__)
        return 2
    chemin = argv[0]
    nom = Path(chemin).name
    if not Path(chemin).exists():
        print(f"ERREUR : fichier introuvable : {chemin}")
        return 2
    if nom.endswith(".txt"):
        bilan = verifier_voix(chemin)
    elif "scene" in nom:
        script = argv[argv.index("--script") + 1] if "--script" in argv else None
        bilan = verifier_scenes(chemin, script)
    else:
        bilan = verifier_script(chemin)

    for niveau, msg in problemes:
        print(f"{niveau} : {msg}")
    n_err = sum(1 for n, _ in problemes if n == "ERREUR")
    n_av = len(problemes) - n_err
    print(f"\n{nom} — {bilan}. {n_err} erreur(s), {n_av} avertissement(s).")
    return 1 if n_err else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
