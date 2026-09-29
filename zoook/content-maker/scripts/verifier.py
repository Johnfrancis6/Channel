#!/usr/bin/env python3
"""Contrôles automatiques des livrables content-maker (Zoook).

Le jugement (la qualité du récit, l'exactitude) reste au modèle et à Franco.
Ce script ne vérifie que ce qui se compte : longueurs, formats, continuité.

Usage :
  python3 verifier.py 02_script.md
  python3 verifier.py 02_script_voix.txt
  python3 verifier.py 03_scenes.md [--script 02_script.md]

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
TYPES = {"image", "preuve", "titre"}
MOUVEMENTS = {"zoom_avant", "zoom_arriere", "pan_gauche", "pan_droite"}
RE_CTA = re.compile(r"abonne|pouce bleu|\blike\b|la cloche|partage[sz]? (la|cette) vid", re.I)
RE_LICENCE = re.compile(r"CC0|CC[ -]BY|domaine public|public domain", re.I)

problemes = []


def erreur(msg):
    problemes.append(("ERREUR", msg))


def avertir(msg):
    problemes.append(("AVERTISSEMENT", msg))


def mots(texte):
    return re.findall(r"[\w’'-]+", texte)


def phrases(texte):
    texte = " ".join(texte.split())
    return [p for p in re.split(r"(?<=[.!?…])\s+", texte) if p.strip()]


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

    if not re.search(r"\bsauf que\b", texte, re.I):
        avertir("aucun « Sauf que » : les obstacles entre les temps sont-ils là ?")
    if RE_CTA.search(texte):
        erreur(f"appel à s'abonner ou à liker repéré : « {RE_CTA.search(texte).group(0)} »")
    if ps and not ps[-1].rstrip().endswith("?"):
        avertir("la dernière phrase n'est pas une question ouverte")

    med = statistics.median(longueurs) if longueurs else 0
    return f"{n} mots, {len(ps)} phrases, médiane {med} mots, ~{n / 3.0 / 60:.1f} min à 3 mots/s"


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
    return f"{len(lignes)} lignes, {total} mots"


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
    precedent, serie, n_texte = None, 0, 0
    textes = []
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
        if typ != "titre" and not 10 <= n_mots <= 35:
            avertir(f"scène {num} : {n_mots} mots de texte dit (cible 18-25, soit 6 à 8 s)")
        if typ == "image":
            if image != f"scene_{int(num):03d}.png":
                erreur(f"scène {num} : image « {image} », attendu scene_{int(num):03d}.png")
            if int(num) not in prompts:
                erreur(f"scène {num} : aucun prompt **scene_{int(num):03d}**")
        elif typ == "preuve":
            if not image.startswith("preuves/"):
                erreur(f"scène {num} : une preuve pointe vers preuves/…, pas « {image} »")
            if preuve in ("", "—", "-") or not RE_LICENCE.search(preuve):
                erreur(f"scène {num} : preuve sans licence ni crédit (« {preuve} »)")
            if int(num) in prompts:
                avertir(f"scène {num} : prompt présent pour une preuve (vraie photo attendue)")
        if typ != "titre":
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
    return f"{total} scènes, {len(prompts)} prompts, texte animé sur {n_texte}"


def main(argv):
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
