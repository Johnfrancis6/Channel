#!/usr/bin/env python3
"""
rassembler_inputs.py — rassemble et **mesure** les inputs du rapport
hebdomadaire d'amelioration continue (§4.3, H1).

Il ne listait que des chemins de fichiers, a charge pour l'agent de tout
relire et de reperer des motifs a l'oeil. Deux problemes :

- **les donnees d'execution n'y etaient pas.** Le signal le plus fort de la
  semaine du 11/09/2026 — huit tentatives sur E4_audio, 2 h 20 perdues —
  vit dans les `state.json`, qui n'etaient pas lus. H1 cherchait des motifs
  sans avoir les evenements ;
- **rien n'etait agrege.** A vingt videos, relire tous les rapports pour
  compter les refus a la main n'est pas tenable.

Il calcule donc des indicateurs — tentatives par etape, alertes, refus de
checkpoint et leurs motifs, boucles A4<->A5, duree de production — et
laisse le jugement a l'agent : ce script ne fait que compter, comme
`metriques.py` pour A5.

Les evenements se lisent a deux endroits, et les deux sont necessaires :
l'etape porte l'etat *courant*, l'historique porte ce qui a ete *resolu*.
Un refus repris repasse le checkpoint a `a_venir` (engine._reagir_au_refus)
et une alerte levee disparait de l'etape : sans l'historique, la semaine
ou le probleme a ete corrige serait aussi celle ou il devient invisible.

Usage : python3 rassembler_inputs.py --root R [--jours 7]
"""
import argparse
import json
import re
from datetime import datetime, timedelta, timezone
from pathlib import Path

CHECKPOINTS = ("CP1", "CP2", "CP3")
RE_ETAPE_EN_TETE = re.compile(r"^(E\d+_[a-z]+|CP\d)\s*:")


def _mtime(chemin):
    return datetime.fromtimestamp(chemin.stat().st_mtime, timezone.utc)


def _modifie_recemment(chemin, seuil):
    return _mtime(chemin) >= seuil


def _parse_iso(valeur):
    try:
        return datetime.strptime(valeur, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
    except (ValueError, TypeError):
        return None


def _lire_json(chemin, defaut=None):
    try:
        return json.loads(Path(chemin).read_text(encoding="utf-8-sig"))
    except (OSError, json.JSONDecodeError):
        return defaut


def _etape_depuis_message(message):
    trouve = RE_ETAPE_EN_TETE.match(message or "")
    return trouve.group(1) if trouve else None


def indicateurs(states):
    """Ce qui se compte dans les state.json. Aucun jugement, que des faits."""
    par_etape = {}
    refus = []
    alertes = []
    boucles = []
    durees_production = []
    vus_refus = set()
    vus_alertes = set()

    for state in states:
        vid = state.get("video_id")
        etapes = state.get("etapes") or {}

        for etape_id, etape in sorted(etapes.items()):
            if not isinstance(etape, dict):
                continue
            tentatives = etape.get("tentatives")
            if isinstance(tentatives, int) and tentatives:
                stats = par_etape.setdefault(etape_id, {"tentatives_total": 0, "videos": 0, "max": 0})
                stats["tentatives_total"] += tentatives
                stats["videos"] += 1
                stats["max"] = max(stats["max"], tentatives)
            if etape.get("statut") == "alerte":
                message = etape.get("message") or ""
                alertes.append({"video_id": vid, "etape": etape_id, "tentatives": tentatives,
                                "message": message, "source": "etape"})
                vus_alertes.add((vid, etape_id, message))

        for cp in CHECKPOINTS:
            etape = etapes.get(cp) or {}
            if etape.get("statut") == "refuse":
                commentaire = etape.get("commentaire") or ""
                refus.append({"video_id": vid, "checkpoint": cp,
                              "commentaire": commentaire, "source": "etape"})
                vus_refus.add((vid, cp, commentaire))

        for evenement in state.get("historique") or []:
            if not isinstance(evenement, dict):
                continue
            nom = evenement.get("evenement") or ""
            message = evenement.get("message") or ""
            if nom.endswith("_refuse"):
                cp = nom.rsplit("_", 1)[0]
                if (vid, cp, message) not in vus_refus:
                    vus_refus.add((vid, cp, message))
                    refus.append({"video_id": vid, "checkpoint": cp,
                                  "commentaire": message, "source": "historique",
                                  "horodatage": evenement.get("horodatage")})
            elif nom == "alerte":
                etape_id = _etape_depuis_message(message)
                if (vid, etape_id, message) not in vus_alertes:
                    vus_alertes.add((vid, etape_id, message))
                    alertes.append({"video_id": vid, "etape": etape_id, "tentatives": None,
                                    "message": message, "source": "historique",
                                    "horodatage": evenement.get("horodatage")})

        # Le compteur vit dans le state (engine._gerer_boucle_redaction_filtre)
        # mais un refus CP2 le remet a zero : l'historique garde les tours
        # perdus, sans quoi une video qui a boucle six fois en afficherait deux.
        tours_historique = sum(1 for e in (state.get("historique") or [])
                               if isinstance(e, dict)
                               and (e.get("message") or "").startswith("Tour ")
                               and "redaction" in (e.get("message") or ""))
        tours = max(state.get("boucle_A4_A5") or 0, tours_historique)
        if tours:
            boucles.append({"video_id": vid, "tours": tours})

        debut = _parse_iso(state.get("cree_le"))
        fin = _parse_iso((etapes.get("CP3") or {}).get("date"))
        if debut and fin and fin >= debut:
            durees_production.append({"video_id": vid,
                                      "heures": round((fin - debut).total_seconds() / 3600, 1)})

    for stats in par_etape.values():
        stats["tentatives_moyennes"] = round(stats["tentatives_total"] / stats["videos"], 2)

    return {
        "tentatives_par_etape": dict(sorted(par_etape.items())),
        "alertes": alertes,
        "refus_checkpoints": refus,
        "boucles_redaction_filtre": boucles,
        "durees_production_h": durees_production,
    }


def rassembler(root, jours=7):
    maintenant = datetime.now(timezone.utc)
    seuil = maintenant - timedelta(days=jours)
    root = Path(root)
    resultat = {"periode_jours": jours, "checkpoints": [], "metriques_filtre": [],
                "rapports_audio": [], "analytics_csv": [], "corpus_structures": None,
                "videos_actives": [], "recommandations_passees": [],
                "recommandations_en_attente": []}
    states = []

    videos_dir = root / "videos"
    if videos_dir.is_dir():
        for video_dir in sorted(p for p in videos_dir.iterdir() if p.is_dir()):
            chemin_state = video_dir / "state.json"
            state = _lire_json(chemin_state)
            if isinstance(state, dict):
                inactivite = (maintenant - _mtime(chemin_state)).total_seconds() / 86400
                resultat["videos_actives"].append({
                    "video_id": state.get("video_id"),
                    "statut_global": state.get("statut_global"),
                    "etape_actuelle": state.get("etape_actuelle"),
                    "format": (state.get("consignes") or {}).get("format"),
                    "jours_sans_activite": round(inactivite, 1),
                })
                # Une video figee depuis un mois n'a rien produit cette semaine :
                # ses compteurs fausseraient le bilan. Elle reste listee au-dessus,
                # justement parce qu'etre figee est en soi un signal.
                if _modifie_recemment(chemin_state, seuil):
                    states.append(state)

            checkpoints_dir = video_dir / "checkpoints"
            if checkpoints_dir.is_dir():
                for rapport in sorted(checkpoints_dir.glob("rapport_CP*.md")):
                    if _modifie_recemment(rapport, seuil):
                        resultat["checkpoints"].append(str(rapport))
                # Un rapport refuse est archive : c'est la trace la plus
                # directe de ce que Franco a rejete, et elle etait ignoree.
                refuses = checkpoints_dir / "refuses"
                if refuses.is_dir():
                    resultat["checkpoints"] += [str(p) for p in sorted(refuses.glob("*.md"))
                                                if _modifie_recemment(p, seuil)]

            for nom, cle in (("03_rapport_metriques.md", "metriques_filtre"),
                             ("04_rapport_audio.md", "rapports_audio")):
                chemin = video_dir / nom
                if chemin.is_file() and _modifie_recemment(chemin, seuil):
                    resultat[cle].append(str(chemin))

            # Les tentatives archivees : `04_rapport_audio.md` ne garde que
            # la derniere, et une tentative reussie ne contient aucun diff.
            # Les runs en echec — ceux qui ont quelque chose a apprendre —
            # ne vivaient nulle part.
            audio_archive = video_dir / "audio"
            if audio_archive.is_dir():
                resultat["rapports_audio"] += [
                    str(p) for p in sorted(audio_archive.glob("rapport_tentative_*.md"))
                    if _modifie_recemment(p, seuil)]

    analytics_dir = root / "03_Amelioration" / "analytics"
    if analytics_dir.is_dir():
        resultat["analytics_csv"] = [str(p) for p in sorted(analytics_dir.glob("*.csv"))]

    corpus = root / "02_Veille_hebdo" / "corpus_structures.jsonl"
    if corpus.is_file():
        resultat["corpus_structures"] = str(corpus)

    # Ce que H1 a deja propose : sans ca, il repropose chaque semaine ce que
    # Franco a deja refuse la semaine precedente.
    suivi = root / "03_Amelioration" / "recommandations.jsonl"
    if suivi.is_file():
        lignes = []
        for ligne in suivi.read_text(encoding="utf-8-sig").splitlines():
            if not ligne.strip():
                continue
            try:
                lignes.append(json.loads(ligne))
            except json.JSONDecodeError:
                continue
        resultat["recommandations_passees"] = lignes
        resultat["recommandations_en_attente"] = [l for l in lignes
                                                  if l.get("statut") == "proposee"]

    resultat["indicateurs"] = indicateurs(states)
    return resultat


def main():
    ap = argparse.ArgumentParser(description="Rassemble et mesure les inputs du rapport H1 (§4.3).")
    ap.add_argument("--root", required=True)
    ap.add_argument("--jours", type=int, default=7)
    a = ap.parse_args()
    print(json.dumps(rassembler(a.root, a.jours), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
