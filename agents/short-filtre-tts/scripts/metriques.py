#!/usr/bin/env python3
"""
metriques.py — mesure objective des phrases d'un script, pour appuyer le
jugement du Filtre TTS (§7.3). Le style (zombie nouns, ton) reste un
jugement qualitatif a faire par Claude ; ce script ne fait que compter.

Il mesure aussi le **budget** du Short quand on le lui donne. La duree
d'une video n'est pas fixee en secondes : c'est le nombre d'idees qui est
plafonne, et le cout en mots d'une idee depend du format (§8). Le budget
se deduit donc de `consignes.idees_max`.

Sans ce controle, personne ne mesurait la longueur totale avant le
montage : sur 2026-09-11_v01, le script faisait 258 mots — 92,1 s de voix
off — et le depassement n'a ete constate qu'a E5, quand tout etait deja
ecrit et enregistre. Le Designer l'a signale sans pouvoir rien faire, en le
repoussant au CP3.

Le budget depend du **format de la video** (`state.json > format_video`) :
un Short compte en dizaines de mots par idee, un format long en centaines.
`--format-video long` bascule le modele. Les valeurs, elles, vivent dans
`outils/formats_video.py` — et pas ici — parce qu'A6 doit les lire aussi.

Usage :
  python3 metriques.py --fichier 02_script_brut.md [--idees 3]
                       [--format-video short|long]
                       [--mots-par-idee 45] [--budget-mots 135]
Sortie : JSON (resume + budget + detail par phrase).
"""
import argparse
import json
import re
from pathlib import Path


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


# Seuils du §7.3 : cible 8-18 mots, decoupe au-dessus de 22, fusion en dessous de 4.
CIBLE_MIN, CIBLE_MAX = 8, 18
SEUIL_DECOUPE, SEUIL_FUSION = 22, 4

# Le debit, le cout par idee et la tolerance vivent dans
# `outils/formats_video.py` : ils dependent du format, et A6 les lit aussi
# pour decouper le storyboard. Les alias ci-dessous gardent la surface
# historique du module (H1 propose des reglages en les nommant), mais il n'y
# a plus qu'une valeur a corriger pour recalibrer la chaine entiere.
MOTS_PAR_SECONDE = formats_video.MOTS_PAR_SECONDE
MOTS_PAR_IDEE_DEFAUT = formats_video.MOTS_PAR_IDEE[formats_video.SHORT]
TOLERANCE_BUDGET = formats_video.TOLERANCE_BUDGET

# Marqueur de mise en scene en debut de ligne : "[intro — stickman face
# camera]". A4 en pose dans le script brut ; ils ne sont jamais prononces.
# Comptes comme du texte, ils gonflaient le total de 27 mots sur
# 2026-09-11_v01 — assez pour fausser le debit de reference de 14 %.
RE_MARQUEUR = re.compile(r"^\s*\[[^\]]*\]\s*")

RE_TITRE = re.compile(r"^#{1,6}\s+(.*)$")
RE_FILET = re.compile(r"^(-{3,}|\*{3,}|_{3,})$")
RE_ITEM = re.compile(r"^(?:[-*+]|\d+[.)])\s+(.*)$")


def _nettoyer_inline(bloc):
    """Retire le balisage qui n'est jamais prononce (code, gras, italique).

    Les liens et parentheses sont laisses tels quels a dessein : le §7.3 les
    interdit dans le script TTS, et c'est a `contient_parenthese_ou_url` de
    les signaler a A5 plutot qu'a ce nettoyage de les masquer.
    """
    bloc = re.sub(r"`([^`]*)`", r"\1", bloc)
    bloc = re.sub(r"\*\*([^*]+)\*\*", r"\1", bloc)
    bloc = re.sub(r"(?<!\w)[*_]([^*_\s][^*_]*)[*_](?!\w)", r"\1", bloc)
    return re.sub(r"\s+", " ", bloc).strip()


def blocs_parles(texte):
    """(section, paragraphe) pour chaque bloc reellement dit a voix haute.

    Les titres du gabarit (`# Script brut — ...`, `## Hook`, `## Corps`...)
    ne sont pas prononces : ils sont retires du texte mesure et conservés
    seulement comme nom de section. Sans ca, ils etaient recolles a la phrase
    suivante — faute de ponctuation finale — et gonflaient son compte de mots,
    ce qui pouvait faire franchir le seuil de decoupe a une phrase correcte et
    declencher une revision A4<->A5 pour rien.
    """
    texte = re.sub(r"^(```|~~~).*?^\1", "\n\n", texte, flags=re.DOTALL | re.MULTILINE)
    blocs, courant, section = [], [], None

    def vider():
        if courant:
            blocs.append((section, " ".join(courant)))
            courant.clear()

    for ligne in texte.splitlines():
        nue = ligne.strip()
        titre = RE_TITRE.match(nue)
        if titre:
            vider()
            section = _nettoyer_inline(titre.group(1)) or None
            continue
        if not nue or RE_FILET.match(nue):
            vider()
            continue
        item = RE_ITEM.match(nue)
        if item:
            # Un item de liste est une unite a lui seul, meme sans ponctuation.
            vider()
            blocs.append((section, item.group(1)))
            continue
        courant.append(RE_MARQUEUR.sub("", re.sub(r"^>\s*", "", nue)))
    vider()

    return [(sec, _nettoyer_inline(b)) for sec, b in blocs if _nettoyer_inline(b)]


def decouper_phrases(texte):
    """Phrases prononcees, avec leur section. Le decoupage ne franchit jamais
    une frontiere de paragraphe : deux paragraphes ne forment pas une phrase."""
    phrases = []
    for section, bloc in blocs_parles(texte):
        for p in re.split(r"(?<=[.!?])\s+", bloc):
            p = p.strip()
            if p:
                phrases.append((section, p))
    return phrases


def analyser(phrase, section=None):
    mots = phrase.split()
    n = len(mots)
    triade_probable = phrase.count(",") >= 2 or bool(
        re.search(r",\s*[\w'-]+\s*,\s*(and|et)\s+[\w'-]+", phrase, re.IGNORECASE)
    )
    return {
        "phrase": phrase,
        "section": section,
        "mots": n,
        # §7.3 : hors de la bande cible sans pour autant exiger une action.
        "hors_cible": n < CIBLE_MIN or n > CIBLE_MAX,
        "trop_longue": n > SEUIL_DECOUPE,
        # Les hooks courts sont une exception explicite du §7.3 : on signale la
        # section pour qu'A5 puisse l'appliquer au lieu de fusionner betement.
        "trop_courte": n < SEUIL_FUSION,
        "virgules": phrase.count(","),
        "triade_probable": triade_probable,
        "contient_parenthese_ou_url": bool(re.search(r"[()]|https?://", phrase)),
    }


def evaluer_budget(mots_total, idees=None, mots_par_idee=None, budget_mots=None,
                   format_video=formats_video.SHORT):
    """Compare la longueur reelle au budget. None si aucun budget n'est donne.

    `format_video` choisit le cout par idee : 45 mots en short, 300 en long.
    Appliquer le modele du Short a un script long le declarerait « depasse »
    des la premiere minute — et A5 le renverrait a A4 pour le couper, ce qui
    est exactement l'inverse du travail demande.
    """
    if budget_mots is None:
        if not idees:
            return None
        budget_mots = int(idees) * formats_video.mots_par_idee(format_video, mots_par_idee)
    if budget_mots <= 0:
        return None

    calibrage, note_calibrage = formats_video.calibrage(format_video)
    ratio = mots_total / budget_mots
    if ratio <= 1.0:
        verdict = "ok"
    elif ratio <= 1.0 + TOLERANCE_BUDGET:
        verdict = "limite"
    else:
        verdict = "depasse"
    return {
        "mots_total": mots_total,
        "budget_mots": budget_mots,
        "idees_max": idees,
        "format_video": format_video,
        "mots_par_idee": formats_video.mots_par_idee(format_video, mots_par_idee) if idees else None,
        "ratio": round(ratio, 2),
        "depassement_mots": max(0, mots_total - budget_mots),
        "duree_estimee_s": round(mots_total / MOTS_PAR_SECONDE, 1),
        "duree_budget_s": round(budget_mots / MOTS_PAR_SECONDE, 1),
        "verdict": verdict,
        # D'ou vient le modele, en clair. Un seuil sans sa provenance se lit
        # comme une loi : celui du Short a ete mesure une fois, celui du long
        # est une hypothese de depart, et A5 doit pouvoir faire la difference
        # avant de renvoyer un script a la reecriture.
        "calibrage": calibrage,
        "calibrage_note": note_calibrage,
    }


def main():
    ap = argparse.ArgumentParser(description="Metriques de calibrage des phrases (§7.3).")
    ap.add_argument("--fichier", required=True)
    ap.add_argument("--idees", type=int, help="consignes.idees_max — budget de la video")
    ap.add_argument("--format-video", dest="format_video", choices=list(formats_video.FORMATS),
                    default=formats_video.FORMAT_DEFAUT,
                    help="state.json > format_video. Choisit le cout par idee "
                         f"({formats_video.MOTS_PAR_IDEE[formats_video.SHORT]} mots en short, "
                         f"{formats_video.MOTS_PAR_IDEE[formats_video.LONG]} en long).")
    ap.add_argument("--mots-par-idee", type=int, dest="mots_par_idee",
                    help="cout en mots d'une idee, s'il faut surcharger le defaut du format")
    ap.add_argument("--budget-mots", type=int, dest="budget_mots",
                    help="budget en mots impose directement (court-circuite --idees)")
    a = ap.parse_args()

    with open(a.fichier, encoding="utf-8-sig") as f:
        texte = f.read()

    phrases = [analyser(p, section) for section, p in decouper_phrases(texte)]
    mots = [p["mots"] for p in phrases]
    mots_total = sum(mots)
    resume = {
        "nb_phrases": len(phrases),
        "mots_total": mots_total,
        "duree_estimee_s": round(mots_total / MOTS_PAR_SECONDE, 1),
        "mots_median": sorted(mots)[len(mots) // 2] if mots else 0,
        "cible": f"{CIBLE_MIN}-{CIBLE_MAX} mots",
        "hors_cible": sum(1 for p in phrases if p["hors_cible"]),
        "trop_longues": sum(1 for p in phrases if p["trop_longue"]),
        "trop_courtes": sum(1 for p in phrases if p["trop_courte"]),
        "triades_probables": sum(1 for p in phrases if p["triade_probable"]),
        "parentheses_ou_url": sum(1 for p in phrases if p["contient_parenthese_ou_url"]),
    }
    sortie = {"resume": resume, "phrases": phrases}
    budget = evaluer_budget(mots_total, a.idees, a.mots_par_idee, a.budget_mots,
                            format_video=a.format_video)
    if budget:
        sortie["budget"] = budget
    print(json.dumps(sortie, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
