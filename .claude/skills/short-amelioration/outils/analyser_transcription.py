#!/usr/bin/env python3
"""
analyser_transcription.py — segmente et mesure la structure d'une video,
pour A3 (concurrents) et H1 (nos propres videos).

Ce que faisait A3 avant : une note en **prose libre, indexee par chaine**,
recopiee telle quelle dans le rapport hebdomadaire. Trois consequences, et
chacune empeche d'apprendre quoi que ce soit :

- le hook, le CTA et le rythme sont des proprietes d'UNE video ; ecraser
  cinq videos dans une phrase detruit l'information avant de l'ecrire ;
- de la prose ne se mesure pas, ne se compare pas, ne s'agrege pas ;
- le rapport hebdo est un fichier neuf chaque semaine. **Rien ne
  s'accumulait** dans tout le systeme, et un systeme qui n'accumule rien ne
  peut rien apprendre.

Separation des roles, comme `metriques.py` pour A5 : **le LLM segmente**
(c'est du jugement — reconnaitre un hook ou un CTA demande de comprendre le
propos), **le script compte** et valide le schema. Le vocabulaire des roles
est ferme : s'il est libre, le corpus n'est plus agregeable et on retombe
sur la prose.

Deux temps :
  1. `--gabarit`  : sort un squelette de segmentation, phrases numerotees
  2. `--mesurer`  : prend la segmentation remplie, calcule les metriques,
                    valide, et ajoute une ligne au corpus

Usage :
  python3 analyser_transcription.py --gabarit --transcription t.txt --duree 47
  python3 analyser_transcription.py --gabarit --script 03_script_tts.txt \\
      --phrases 04_phrases.json
  python3 analyser_transcription.py --mesurer --segmentation s.json \\
      [--corpus 02_Veille_hebdo/corpus_structures.jsonl]

Codes : 0 ok | 2 entree invalide | 3 segmentation invalide
"""
import argparse
import json
import re
import sys
from pathlib import Path

# Vocabulaire FERME. Etendre la liste est possible, mais alors le role entre
# au registre et s'applique a tout le corpus : un role invente au cas par cas
# rend les lignes incomparables entre elles.
ROLES = ("hook", "promesse", "contexte", "idee", "exemple", "transition", "cta", "sponsoring")

# Ces roles n'apparaissent qu'a un seul endroit de la video — mais peuvent
# tenir en plusieurs phrases. Un hook en deux temps ("Tout le monde appelle
# ca un agent." / "La plupart n'en sont pas.") est une figure classique, pas
# une erreur : c'est la forme du script reel de 2026-09-11_v01. Ce qui est
# suspect, c'est un role de ce type DISPERSE dans la video.
ROLES_CONTIGUS = ("hook", "promesse", "cta")


def sortir(code, **data):
    print(json.dumps({"ok": code == 0, **data}, ensure_ascii=False, indent=2))
    sys.exit(code)


def lire_json(chemin):
    return json.loads(Path(chemin).read_text(encoding="utf-8-sig"))


def decouper_phrases(texte):
    """Une phrase par ligne si le fichier est deja calibre, sinon par ponctuation."""
    lignes = [l.strip() for l in texte.splitlines() if l.strip()]
    if len(lignes) > 1:
        return lignes
    return [p.strip() for p in re.split(r"(?<=[.!?])\s+", texte) if p.strip()]


def gabarit(phrases, bornes=None, duree_totale=None):
    """Squelette a remplir : chaque phrase attend son role."""
    segments = []
    for i, phrase in enumerate(phrases):
        # `groupe` : numero d'idee, a renseigner quand plusieurs phrases
        # developpent la MEME idee. Sans lui, des phrases contigues comptent
        # pour une seule idee, ce qui est le cas le plus frequent.
        segment = {"index": i + 1, "texte": phrase, "role": None, "groupe": None}
        if bornes and i < len(bornes):
            segment["debut_s"] = bornes[i].get("debut_s")
            segment["fin_s"] = bornes[i].get("fin_s")
        segments.append(segment)
    return {
        "video_id": None,
        "source": None,
        "chaine": None,
        "titre": None,
        "vues": None,
        "duree_s": duree_totale,
        "roles_possibles": list(ROLES),
        "segments": segments,
    }


def valider(segmentation):
    """Liste des problemes. Vide = segmentation exploitable."""
    problemes = []
    segments = segmentation.get("segments") or []
    if not segments:
        return ["aucun segment"]

    positions = {}
    for s in segments:
        role = s.get("role")
        if role is None:
            problemes.append(f"segment {s.get('index')} : role non renseigne")
        elif role not in ROLES:
            problemes.append(f"segment {s.get('index')} : role inconnu '{role}' (attendu : {', '.join(ROLES)})")
        else:
            positions.setdefault(role, []).append(s.get("index"))

    for role in ROLES_CONTIGUS:
        indices = sorted(i for i in positions.get(role, []) if isinstance(i, int))
        if len(indices) > 1 and indices != list(range(indices[0], indices[0] + len(indices))):
            problemes.append(
                f"segments '{role}' disperses (indices {indices}) : ce role tient en un seul "
                f"bloc, meme s'il occupe plusieurs phrases")

    if not segmentation.get("duree_s"):
        problemes.append("duree_s manquante : sans elle, aucune metrique de rythme")
    return problemes


def _mots(texte):
    return len((texte or "").split())


def _mediane(valeurs):
    if not valeurs:
        return 0
    ordonnees = sorted(valeurs)
    milieu = len(ordonnees) // 2
    if len(ordonnees) % 2:
        return ordonnees[milieu]
    return round((ordonnees[milieu - 1] + ordonnees[milieu]) / 2, 1)


def mesurer(segmentation):
    """Metriques comparables d'une video a l'autre. Ne juge rien, compte."""
    segments = segmentation["segments"]
    duree = float(segmentation["duree_s"])
    mots_total = sum(_mots(s.get("texte")) for s in segments)

    par_role = {}
    for s in segments:
        par_role.setdefault(s["role"], []).append(s)

    def duree_role(role):
        blocs = par_role.get(role) or []
        bornes = [(b.get("debut_s"), b.get("fin_s")) for b in blocs
                  if b.get("debut_s") is not None and b.get("fin_s") is not None]
        if bornes:
            return round(sum(f - d for d, f in bornes), 1)
        # Pas de timing (cas d'une transcription de concurrent) : on repartit
        # au prorata des mots, ce qui vaut mieux que rien mais reste estime.
        mots_role = sum(_mots(b.get("texte")) for b in blocs)
        return round(duree * mots_role / mots_total, 1) if mots_total else 0.0

    # Une idee du budget (§8, 3 max) n'est pas un segment : sur
    # 2026-09-11_v01, les trois idees — LLM, workflow, agent — occupent
    # douze phrases. On compte donc les BLOCS : les groupes explicites
    # (`groupe`) s'ils sont renseignes, sinon les suites contigues.
    idees = par_role.get("idee") or []
    groupes = {s.get("groupe") for s in idees if s.get("groupe") is not None}
    if groupes:
        nb_idees = len(groupes)
        mots_par_groupe = {}
        for s in idees:
            g = s.get("groupe")
            mots_par_groupe[g] = mots_par_groupe.get(g, 0) + _mots(s.get("texte"))
        tailles = list(mots_par_groupe.values())
    else:
        indices = sorted(s["index"] for s in idees)
        blocs, courant = [], []
        for i in indices:
            if courant and i != courant[-1] + 1:
                blocs.append(courant)
                courant = []
            courant.append(i)
        if courant:
            blocs.append(courant)
        nb_idees = len(blocs)
        par_index = {s["index"]: _mots(s.get("texte")) for s in idees}
        tailles = [sum(par_index[i] for i in bloc) for bloc in blocs]
    cta = par_role.get("cta") or []
    position_cta = None
    if cta:
        index_cta = min(c["index"] for c in cta)
        position_cta = round(100 * index_cta / len(segments))

    return {
        "duree_s": duree,
        "mots_total": mots_total,
        "mots_par_seconde": round(mots_total / duree, 2) if duree else None,
        "nb_segments": len(segments),
        "phrase_mediane_mots": _mediane([_mots(s.get("texte")) for s in segments]),
        "hook_duree_s": duree_role("hook"),
        "hook_mots": sum(_mots(s.get("texte")) for s in par_role.get("hook", [])),
        "nb_idees": nb_idees,
        "nb_segments_idee": len(idees),
        "mots_par_idee": tailles,
        "mots_par_idee_moyen": round(sum(tailles) / len(tailles)) if tailles else None,
        # Le cout TOTAL d'une idee : hook, promesse, exemple et CTA compris.
        # C'est cette valeur-la qui se compare au budget de A5, pas la
        # precedente — sur 2026-09-11_v01, les trois idees ne pesent que 115
        # mots sur 231, l'autre moitie etant l'enveloppe narrative.
        "cout_total_par_idee": round(mots_total / nb_idees) if nb_idees else None,
        "cta_present": bool(cta),
        "cta_position_pct": position_cta,
        "sponsoring_present": bool(par_role.get("sponsoring")),
        "repartition_roles_pct": {
            role: round(100 * sum(_mots(s.get("texte")) for s in blocs) / mots_total)
            for role, blocs in sorted(par_role.items()) if mots_total
        },
    }


def ajouter_au_corpus(chemin, ligne):
    """Append-only : le corpus est le seul actif qui prend de la valeur avec
    le temps. On n'y reecrit jamais une ligne passee."""
    chemin = Path(chemin)
    chemin.parent.mkdir(parents=True, exist_ok=True)
    with open(chemin, "a", encoding="utf-8") as f:
        f.write(json.dumps(ligne, ensure_ascii=False) + "\n")


def main():
    ap = argparse.ArgumentParser(description="Segmente et mesure la structure d'une video.")
    ap.add_argument("--gabarit", action="store_true")
    ap.add_argument("--mesurer", action="store_true")
    ap.add_argument("--transcription", help="texte brut (concurrent)")
    ap.add_argument("--script", help="03_script_tts.txt (nos videos)")
    ap.add_argument("--phrases", help="04_phrases.json (nos videos, bornes exactes)")
    ap.add_argument("--duree", type=float, help="duree totale en secondes")
    ap.add_argument("--segmentation", help="segmentation remplie (mode --mesurer)")
    ap.add_argument("--corpus", help="corpus_structures.jsonl — ajoute une ligne si fourni")
    a = ap.parse_args()

    if a.gabarit == a.mesurer:
        sortir(2, message="Choisis --gabarit ou --mesurer.")

    if a.gabarit:
        source = a.script or a.transcription
        if not source:
            sortir(2, message="--gabarit demande --script ou --transcription.")
        texte = Path(source).read_text(encoding="utf-8-sig")
        phrases = decouper_phrases(texte)
        if not phrases:
            sortir(2, message=f"Aucune phrase dans {source}.")

        bornes, duree = None, a.duree
        if a.phrases:
            data = lire_json(a.phrases)
            bornes = data.get("phrases") or []
            duree = duree or data.get("duree_totale_s")
        print(json.dumps(gabarit(phrases, bornes, duree), ensure_ascii=False, indent=2))
        return

    if not a.segmentation:
        sortir(2, message="--mesurer demande --segmentation.")
    segmentation = lire_json(a.segmentation)
    problemes = valider(segmentation)
    if problemes:
        sortir(3, message="Segmentation invalide.", problemes=problemes)

    metriques = mesurer(segmentation)
    ligne = {
        "video_id": segmentation.get("video_id"),
        "source": segmentation.get("source"),
        "chaine": segmentation.get("chaine"),
        "titre": segmentation.get("titre"),
        "vues": segmentation.get("vues"),
        "metriques": metriques,
        "segments": [{"index": s["index"], "role": s["role"], "mots": _mots(s.get("texte"))}
                     for s in segmentation["segments"]],
    }
    if a.corpus:
        ajouter_au_corpus(a.corpus, ligne)
    sortir(0, metriques=metriques, corpus=a.corpus, ajoute=bool(a.corpus))


if __name__ == "__main__":
    main()
