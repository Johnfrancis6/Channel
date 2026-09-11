#!/usr/bin/env python3
"""
etape.py — applique le contrat state.json (§4.2) pour une etape pilotee par
un agent : demarrage (en_cours), succes (termine) ou echec.

Ne touche jamais aux checkpoints (CP1/CP2/CP3) ni a l'etape d'un autre
agent : c'est le role de l'Orchestrateur (§4.2, point 4).

Usage :
  python3 etape.py commencer --video ID --etape E1_recherche [--root R]
  python3 etape.py terminer  --video ID --etape E1_recherche --sorties a.md b.md \
      [--message "..."] [--sujet "..."] [--angle "..."] [--titre "..."]
  python3 etape.py echouer   --video ID --etape E1_recherche --message "..." \
      [--action-suivi revision_redaction]

--sujet/--angle/--titre ne s'appliquent qu'a E1_recherche en voie rapide
(veille actu), quand le Chercheur propose lui-meme le sujet (§4.3, A2).

Sortie : JSON sur stdout. Codes : 0 ok | 2 racine introuvable | 5 etape invalide | 6 video inconnue
"""
import argparse
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path


def maintenant_iso():
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


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


def lire_state(dossier):
    return json.loads((dossier / "state.json").read_text(encoding="utf-8-sig"))


def ecrire_state(dossier, state):
    chemin = dossier / "state.json"
    tmp = chemin.with_name(chemin.name + ".tmp")
    tmp.write_text(json.dumps(state, ensure_ascii=False, indent=2), encoding="utf-8")
    os.replace(tmp, chemin)


def ajouter_historique(state, agent, evenement, message):
    state.setdefault("historique", []).append({
        "horodatage": maintenant_iso(), "agent": agent, "evenement": evenement,
        "message": message or "",
    })


def main():
    ap = argparse.ArgumentParser(description="Applique le contrat state.json pour une etape d'agent.")
    ap.add_argument("action", choices=["commencer", "terminer", "echouer"])
    ap.add_argument("--root")
    ap.add_argument("--video", required=True)
    ap.add_argument("--etape", required=True)
    ap.add_argument("--message")
    ap.add_argument("--sorties", nargs="*", default=[])
    ap.add_argument("--sujet")
    ap.add_argument("--angle")
    ap.add_argument("--titre")
    ap.add_argument("--action-suivi", dest="action_suivi",
                     help="ex: revision_redaction, pour renvoyer E3_filtre vers E2_redaction")
    a = ap.parse_args()

    racine = trouver_racine(a.root)
    if racine is None:
        sortir(2, message="Dossier ChaineYouTube introuvable. Passe --root ou definis CHAINE_YT_ROOT.")

    dossier = racine / "videos" / a.video
    if not (dossier / "state.json").is_file():
        sortir(6, message=f"Video inconnue : {a.video}")

    state = lire_state(dossier)
    etapes = state.get("etapes", {})
    if a.etape not in etapes or "agent" not in (etapes.get(a.etape) or {}):
        sortir(5, message=f"Etape invalide ou non pilotee par un agent : {a.etape}")

    etape = etapes[a.etape]
    agent = etape.get("agent") or a.etape

    if a.action == "commencer":
        etape["tentatives"] = etape.get("tentatives", 0) + 1
        etape["statut"] = "en_cours"
        etape["debut"] = maintenant_iso()
        etape["fin"] = None
        etape.pop("action", None)
        ajouter_historique(state, agent, "en_cours", f"Tentative {etape['tentatives']}")
    elif a.action == "terminer":
        etape["statut"] = "termine"
        etape["fin"] = maintenant_iso()
        etape["sorties"] = a.sorties
        etape["message"] = a.message
        etape.pop("action", None)
        if a.sujet:
            state["sujet"] = a.sujet
        if a.angle:
            state["angle"] = a.angle
        if a.titre:
            state["titre_travail"] = a.titre
        ajouter_historique(state, agent, "termine", a.message or "OK")
    else:
        etape["statut"] = "echec"
        etape["fin"] = maintenant_iso()
        etape["message"] = a.message
        if a.action_suivi:
            etape["action"] = a.action_suivi
        ajouter_historique(state, agent, "echec", a.message or "Echec")

    ecrire_state(dossier, state)
    sortir(0, message="Etape mise a jour.", etape=a.etape, statut=etape["statut"],
           tentatives=etape.get("tentatives"))


if __name__ == "__main__":
    main()
