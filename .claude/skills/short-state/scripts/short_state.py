#!/usr/bin/env python3
"""
short_state.py — état de la production, calculé en direct depuis les state.json.

LECTURE SEULE : ce script n'écrit, ne déplace et ne supprime aucun fichier.

Modes :
  (défaut)          vue d'ensemble : actions pour Franco, vidéos actives, tampon, système
  --video ID        détail complet d'une vidéo
  --registre        liste de toutes les vidéos conçues (y compris publiées / abandonnées)

Sortie : JSON sur stdout. Codes : 0 ok | 2 racine introuvable | 6 vidéo inconnue
"""
import argparse
import json
import os
import re
import sys
from datetime import datetime, timezone, timedelta
from pathlib import Path

ORDRE_ETAPES = ["E1_recherche", "CP1", "E2_redaction", "E3_filtre", "CP2",
                "E4_audio", "E5_storyboard", "E6_montage", "CP3", "E7_publication"]
LIBELLES = {
    "E1_recherche": "Recherche", "CP1": "CP1 sujet/angle", "E2_redaction": "Rédaction",
    "E3_filtre": "Filtre TTS", "CP2": "CP2 script", "E4_audio": "Voix off",
    "E5_storyboard": "Storyboard", "E6_montage": "Montage", "CP3": "CP3 rendu final",
    "E7_publication": "Publication",
}
INACTIFS = {"publiee", "abandonnee"}
PRIORITE = {"CORROMPU": 0, "ALERTE": 1, "BLOQUE": 2, "CHECKPOINT": 3, "AUDIO": 4,
            "SUJETS": 5, "ORCHESTRATEUR": 6, "DECISION_EN_ATTENTE_ORCHESTRATEUR": 7}


def sortir(code, **data):
    print(json.dumps({"ok": code == 0, "code": code, **data}, ensure_ascii=False, indent=2))
    sys.exit(code)


def est_racine(p):
    return p.is_dir() and ((p / "00_Profil").is_dir() or (p / "videos").is_dir())


def trouver_racine(arg):
    if arg:
        p = Path(arg).expanduser()
        return p.resolve() if est_racine(p) else None
    candidats = []
    env = os.environ.get("CHAINE_YT_ROOT")
    if env:
        candidats.append(Path(env).expanduser())
    home = Path.home()
    for sous in ["ChaineYouTube", "GoogleDrive/ChaineYouTube", "Google Drive/ChaineYouTube",
                 "gdrive/ChaineYouTube", "My Drive/ChaineYouTube", "Mon Drive/ChaineYouTube"]:
        candidats.append(home / sous)
    candidats += sorted(home.glob("Library/CloudStorage/GoogleDrive-*/*/ChaineYouTube"))
    for lettre in "GHIJ":
        for sous in ["Mon Drive", "My Drive"]:
            candidats.append(Path(f"{lettre}:/") / sous / "ChaineYouTube")
    for c in candidats:
        try:
            if est_racine(c):
                return c.resolve()
        except OSError:
            continue
    return None


def lire_json(chemin):
    try:
        return json.loads(chemin.read_text(encoding="utf-8-sig")), None
    except FileNotFoundError:
        return None, "absent"
    except (json.JSONDecodeError, OSError) as e:
        return None, str(e)


def parse_iso(s):
    if not s:
        return None
    try:
        d = datetime.fromisoformat(str(s).replace("Z", "+00:00"))
        return d if d.tzinfo else d.replace(tzinfo=timezone.utc)
    except ValueError:
        return None


def depuis(dt, now):
    if dt is None:
        return None
    h = (now - dt).total_seconds() / 3600
    if h < 1:
        return f"{max(int(h * 60), 0)} min"
    if h < 48:
        return f"{int(h)} h"
    return f"{int(h // 24)} j"


def lire_decision(chemin):
    """Lit le bloc DÉCISION d'un rapport de checkpoint (lecture seule)."""
    try:
        texte = chemin.read_text(encoding="utf-8-sig")
    except OSError:
        return None
    idx = max(texte.upper().find("DÉCISION"), texte.upper().find("DECISION"))
    bloc = texte[idx:] if idx >= 0 else texte
    m = re.search(r"Statut\s*:\s*([A-Za-zÉéÈè_]+)", bloc)
    c = re.search(r"Commentaire\s*:\s*(.*)", bloc)
    statut = m.group(1).upper().replace("É", "E") if m else None
    return {"statut": statut, "commentaire": (c.group(1).strip() or None) if c else None}


def dernier_message(st, etape):
    agent = (st.get("etapes", {}).get(etape) or {}).get("agent")
    for ev in reversed(st.get("historique") or []):
        if ev.get("etape") == etape or (agent and ev.get("agent") == agent):
            return ev.get("message")
    return None


def charger(racine):
    videos, corrompus = [], []
    d = racine / "videos"
    if d.is_dir():
        for p in sorted(d.iterdir()):
            if not p.is_dir():
                continue
            st, err = lire_json(p / "state.json")
            if isinstance(st, dict):
                st["_dossier"] = p
                videos.append(st)
            else:
                corrompus.append({"video_id": p.name, "erreur": err or "format inattendu"})
    return videos, corrompus


def resume_video(st, now):
    etapes = st.get("etapes") or {}
    cle = st.get("etape_actuelle")
    e = etapes.get(cle) or {}
    reperes = [parse_iso(e.get("debut"))]
    reperes += [parse_iso(ev.get("horodatage")) for ev in (st.get("historique") or [])[-1:]]
    reperes.append(parse_iso(st.get("cree_le")))
    ref = next((r for r in reperes if r), None)
    paralleles = [
        {"etape": k, "libelle": LIBELLES.get(k, k), "statut": (etapes.get(k) or {}).get("statut")}
        for k in ("E4_audio", "E5_storyboard")
        if k != cle and (etapes.get(k) or {}).get("statut") not in (None, "a_venir", "termine")
    ]
    return {
        "video_id": st.get("video_id"),
        "titre": st.get("titre_travail"),
        "pilier": st.get("pilier"),
        "voie": st.get("voie"),
        "statut_global": st.get("statut_global"),
        "etape": cle,
        "etape_libelle": LIBELLES.get(cle, cle),
        "statut_etape": e.get("statut"),
        "tentative": e.get("tentatives"),
        "depuis": depuis(ref, now),
        "en_parallele": paralleles,
    }


def actions_video(st, now, seuil_blocage_h):
    acts = []
    vid, titre = st.get("video_id"), st.get("titre_travail")
    dossier = st["_dossier"]
    for cle in ORDRE_ETAPES:
        e = (st.get("etapes") or {}).get(cle) or {}
        s = e.get("statut")
        if s == "alerte":
            acts.append({"type": "ALERTE", "video_id": vid, "titre": titre, "etape": cle,
                         "detail": dernier_message(st, cle) or "3 échecs consécutifs",
                         "fichier": "01_Orchestrateur/log_erreurs.md"})
        elif s == "attente_validation":
            rapport = dossier / "checkpoints" / f"rapport_{cle}.md"
            dec = lire_decision(rapport) if rapport.exists() else None
            if dec and dec["statut"] in ("VALIDE", "REFUSE"):
                acts.append({"type": "DECISION_EN_ATTENTE_ORCHESTRATEUR", "video_id": vid, "titre": titre,
                             "etape": cle, "detail": f"Décision {dec['statut']} déjà saisie"})
            else:
                acts.append({"type": "CHECKPOINT", "video_id": vid, "titre": titre, "etape": cle,
                             "detail": LIBELLES.get(cle, cle),
                             "fichier": f"videos/{vid}/checkpoints/rapport_{cle}.md",
                             "rapport_present": rapport.exists(),
                             "_age": parse_iso(e.get("debut")) or parse_iso(st.get("cree_le"))})
        elif s == "attente_franco":
            acts.append({"type": "AUDIO" if cle == "E4_audio" else "ACTION_MANUELLE",
                         "video_id": vid, "titre": titre, "etape": cle,
                         "detail": "Lancer le run Colab (voix off)" if cle == "E4_audio" else LIBELLES.get(cle, cle)})
        elif s == "en_cours":
            debut = parse_iso(e.get("debut"))
            if debut and now - debut > timedelta(hours=seuil_blocage_h):
                acts.append({"type": "BLOQUE", "video_id": vid, "titre": titre, "etape": cle,
                             "detail": f"En cours depuis {depuis(debut, now)} (seuil {seuil_blocage_h:g} h)"})
    return acts


def main():
    ap = argparse.ArgumentParser(description="État de la production (lecture seule).")
    ap.add_argument("--root")
    ap.add_argument("--video", help="Identifiant de vidéo pour le détail complet")
    ap.add_argument("--registre", action="store_true", help="Lister toutes les vidéos conçues")
    a = ap.parse_args()

    racine = trouver_racine(a.root)
    if racine is None:
        sortir(2, message="Dossier ChaineYouTube introuvable. Passe --root ou définis CHAINE_YT_ROOT.")

    now = datetime.now(timezone.utc)
    config, _ = lire_json(racine / "01_Orchestrateur" / "config.json")
    config = config if isinstance(config, dict) else {}
    cible = int(config.get("cible_tampon", 4))
    seuil_blocage = float(config.get("seuil_blocage_heures", 2))
    seuil_orch = float(config.get("seuil_orchestrateur_heures", 6))

    videos, corrompus = charger(racine)

    if a.video:
        st = next((v for v in videos if v.get("video_id") == a.video or v["_dossier"].name == a.video), None)
        if st is None:
            sortir(6, message=f"Vidéo inconnue : {a.video}",
                   videos_connues=[v.get("video_id") for v in videos][-15:])
        dossier = st["_dossier"]
        detail = []
        for cle in ORDRE_ETAPES:
            e = (st.get("etapes") or {}).get(cle) or {}
            d, f = parse_iso(e.get("debut")), parse_iso(e.get("fin"))
            item = {"etape": cle, "libelle": LIBELLES[cle], "statut": e.get("statut"),
                    "tentatives": e.get("tentatives"),
                    "duree": depuis(d, f) if d and f else None,
                    "commentaire": e.get("commentaire")}
            sorties = e.get("sorties") or []
            if sorties:
                item["sorties"] = [{"fichier": s, "present": (dossier / s).exists()} for s in sorties]
            if cle.startswith("CP"):
                r = dossier / "checkpoints" / f"rapport_{cle}.md"
                if r.exists():
                    item["decision_rapport"] = lire_decision(r)
            detail.append(item)
        sortir(0, mode="video", resume=resume_video(st, now),
               sujet=st.get("sujet"), angle=st.get("angle"),
               consignes=st.get("consignes"), publication=st.get("publication"),
               etapes=detail, actions=[{k: v for k, v in x.items() if not k.startswith("_")}
                                       for x in actions_video(st, now, seuil_blocage)],
               historique_recent=(st.get("historique") or [])[-10:])

    if a.registre:
        lignes = [{"video_id": v.get("video_id"), "titre": v.get("titre_travail"),
                   "pilier": v.get("pilier"), "statut_global": v.get("statut_global"),
                   "cree_le": v.get("cree_le"),
                   "date_prevue": (v.get("publication") or {}).get("date_prevue"),
                   "date_publication": (v.get("publication") or {}).get("date_effective"),
                   "url": (v.get("publication") or {}).get("url")} for v in videos]
        compte = {}
        for v in videos:
            compte[v.get("statut_global")] = compte.get(v.get("statut_global"), 0) + 1
        sortir(0, mode="registre", total=len(videos), par_statut=compte,
               videos=lignes, corrompus=corrompus)

    actives = [v for v in videos if v.get("statut_global") not in INACTIFS]
    actions = [{"type": "CORROMPU", "video_id": c["video_id"], "detail": c["erreur"],
                "fichier": f"videos/{c['video_id']}/state.json"} for c in corrompus]
    for v in actives:
        actions += actions_video(v, now, seuil_blocage)

    tampon = [v for v in videos if v.get("statut_global") in ("prete", "programmee")]
    backlog_data, _ = lire_json(racine / "02_Veille_hebdo" / "backlog_sujets.json")
    backlog = backlog_data.get("sujets", []) if isinstance(backlog_data, dict) else (backlog_data or [])
    utilises = {v.get("sujet_id") for v in videos if v.get("sujet_id") and v.get("statut_global") != "abandonnee"}
    backlog_dispo = [s for s in backlog if isinstance(s, dict) and s.get("sujet_id") not in utilises]
    if len(tampon) < cible and not backlog_dispo:
        actions.append({"type": "SUJETS", "detail": f"Tampon {len(tampon)}/{cible} et aucun sujet validé en réserve"})

    derniere, source = None, None
    ex, _ = lire_json(racine / "01_Orchestrateur" / "derniere_execution.json")
    if isinstance(ex, dict):
        # `horodatage` est ce que l'Orchestrateur ecrit
        # (dashboard.ecrire_derniere_execution) ; `fin`/`debut` etaient lus
        # ici et n'ont jamais existe. La date declarée n'etait donc jamais
        # trouvee, et on retombait en silence sur la mtime du tableau de
        # bord — un repli qui marche par accident et que n'importe quel
        # outil touchant le fichier fausserait.
        derniere = parse_iso(ex.get("horodatage") or ex.get("fin") or ex.get("debut"))
        source = "derniere_execution.json"
    if derniere is None and (racine / "TABLEAU_DE_BORD.md").exists():
        derniere = datetime.fromtimestamp((racine / "TABLEAU_DE_BORD.md").stat().st_mtime, timezone.utc)
        source = "date de TABLEAU_DE_BORD.md"
    if actives and (derniere is None or now - derniere > timedelta(hours=seuil_orch)):
        actions.append({"type": "ORCHESTRATEUR",
                        "detail": "Jamais exécuté" if derniere is None
                        else f"Dernier passage il y a {depuis(derniere, now)}"})

    lointain = datetime.max.replace(tzinfo=timezone.utc)
    actions.sort(key=lambda x: (PRIORITE.get(x["type"], 9), x.get("_age") or lointain))
    for x in actions:
        x.pop("_age", None)

    prevues = sorted(
        [(parse_iso((v.get("publication") or {}).get("date_prevue")), v) for v in tampon],
        key=lambda t: t[0] or lointain)
    prochaine = next(({"video_id": v.get("video_id"), "titre": v.get("titre_travail"),
                       "date_prevue": (v.get("publication") or {}).get("date_prevue")}
                      for d, v in prevues if d), None)
    semaine = now - timedelta(days=7)
    publiees_7j = sum(1 for v in videos if v.get("statut_global") == "publiee"
                      and (parse_iso((v.get("publication") or {}).get("date_effective")) or lointain.replace(year=1)) >= semaine)

    sortir(0, mode="ensemble",
           genere_le=now.replace(microsecond=0).isoformat().replace("+00:00", "Z"),
           racine=str(racine),
           actions=actions,
           en_production=[resume_video(v, now) for v in actives if v.get("statut_global") not in ("prete", "programmee")],
           tampon={"pretes": len(tampon), "cible": cible,
                   "backlog_sujets_disponibles": len(backlog_dispo),
                   "prochaine_publication": prochaine},
           semaine={"publiees_7j": publiees_7j},
           systeme={"orchestrateur_dernier_passage": depuis(derniere, now) if derniere else None,
                    "source": source, "videos_totales": len(videos),
                    "state_json_corrompus": len(corrompus)})


if __name__ == "__main__":
    main()
