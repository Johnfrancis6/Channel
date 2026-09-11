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
montage : sur 2026-09-11_v01, le script faisait 264 mots — 82,5 s de voix
off — et le depassement n'a ete constate qu'a E5, quand tout etait deja
ecrit et enregistre. Le Designer l'a signale sans pouvoir rien faire, en le
repoussant au CP3.

Usage :
  python3 metriques.py --fichier 02_script_brut.md [--idees 3]
                       [--mots-par-idee 45] [--budget-mots 135]
Sortie : JSON (resume + budget + detail par phrase).
"""
import argparse
import json
import re


# Seuils du §7.3 : cible 8-18 mots, decoupe au-dessus de 22, fusion en dessous de 4.
CIBLE_MIN, CIBLE_MAX = 8, 18
SEUIL_DECOUPE, SEUIL_FUSION = 22, 4

# Debit mesure sur 2026-09-11_v01 : 264 mots pour 82,5 s de voix off, pauses
# inter-phrases comprises. A recalibrer quand le corpus aura plusieurs voix.
MOTS_PAR_SECONDE = 3.2

# Cout en mots d'une idee. Valeur de depart : les formats se decouvrent au
# fil des premieres videos, et chacun a son propre cout — un dialogue en
# consomme bien plus qu'une explication. A surcharger avec --mots-par-idee.
MOTS_PAR_IDEE_DEFAUT = 45

# Au-dela de quel depassement on parle. Sous +20 %, un script se resserre au
# calibrage ; au-dela, c'est une idee de trop, et ca se regle en reecrivant.
TOLERANCE_BUDGET = 0.20

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
        courant.append(re.sub(r"^>\s*", "", nue))
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


def evaluer_budget(mots_total, idees=None, mots_par_idee=None, budget_mots=None):
    """Compare la longueur reelle au budget. None si aucun budget n'est donne."""
    if budget_mots is None:
        if not idees:
            return None
        budget_mots = int(idees) * int(mots_par_idee or MOTS_PAR_IDEE_DEFAUT)
    if budget_mots <= 0:
        return None

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
        "mots_par_idee": int(mots_par_idee or MOTS_PAR_IDEE_DEFAUT) if idees else None,
        "ratio": round(ratio, 2),
        "depassement_mots": max(0, mots_total - budget_mots),
        "duree_estimee_s": round(mots_total / MOTS_PAR_SECONDE, 1),
        "duree_budget_s": round(budget_mots / MOTS_PAR_SECONDE, 1),
        "verdict": verdict,
    }


def main():
    ap = argparse.ArgumentParser(description="Metriques de calibrage des phrases (§7.3).")
    ap.add_argument("--fichier", required=True)
    ap.add_argument("--idees", type=int, help="consignes.idees_max — budget du Short")
    ap.add_argument("--mots-par-idee", type=int, dest="mots_par_idee",
                    help=f"cout en mots d'une idee pour ce format (defaut {MOTS_PAR_IDEE_DEFAUT})")
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
    budget = evaluer_budget(mots_total, a.idees, a.mots_par_idee, a.budget_mots)
    if budget:
        sortie["budget"] = budget
    print(json.dumps(sortie, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
