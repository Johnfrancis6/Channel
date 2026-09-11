#!/usr/bin/env python3
"""
publier.py — enregistre la publication d'une video (E7, §11) et ferme son
cycle de vie dans le registre (§5.3).

C'etait le chainon manquant du pipeline : `statut_global` ne depassait
jamais `prete`. Personne n'ecrivait `programmee` ni `publiee`, ni
`publication.date_effective` / `url`, alors que le tableau de bord et
`short-state` les lisent tous les deux. Resultat : le compteur "Publiees"
restait a zero, le tampon comptait des videos deja en ligne, et la seule
facon d'avancer etait de modifier state.json a la main — exactement ce que
le §5.5 veut eviter.

Ne publie rien sur YouTube : Franco publie (phase test, §11), ce script
enregistre. Il refuse d'agir si le CP3 n'est pas valide (§2 : aucune
publication sans CP3 valide).

Usage :
  python3 publier.py --video ID [--root R] --url https://youtube.com/shorts/xxx
  python3 publier.py --video ID --statut programmee --date 2026-09-14

Sortie : JSON sur stdout. Codes :
  0 ok | 2 racine introuvable | 4 date invalide | 6 video inconnue |
  7 CP3 non valide | 8 deja publiee (relancer avec --force)
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


def normaliser_date(valeur):
    """Accepte 2026-09-14 ou 2026-09-14T18:00:00Z. Retourne la forme ISO Z."""
    if not valeur:
        return maintenant_iso()
    texte = valeur.strip().replace("Z", "+00:00")
    for gabarit in ("%Y-%m-%dT%H:%M:%S%z", "%Y-%m-%d"):
        try:
            dt = datetime.strptime(texte, gabarit)
        except ValueError:
            continue
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    return None


def ecrire_state(dossier, state):
    chemin = dossier / "state.json"
    tmp = chemin.with_name(chemin.name + ".tmp")
    tmp.write_text(json.dumps(state, ensure_ascii=False, indent=2), encoding="utf-8")
    os.replace(tmp, chemin)


def main():
    ap = argparse.ArgumentParser(description="Enregistre la publication d'une video (E7, §11).")
    ap.add_argument("--root")
    ap.add_argument("--video", required=True)
    ap.add_argument("--url", help="URL du Short publie (obligatoire pour --statut publiee).")
    ap.add_argument("--date", help="Date de publication (AAAA-MM-JJ ou ISO). Defaut : maintenant.")
    ap.add_argument("--statut", choices=["publiee", "programmee"], default="publiee")
    ap.add_argument("--force", action="store_true",
                    help="Reecrit une publication deja enregistree (correction d'URL ou de date).")
    a = ap.parse_args()

    racine = trouver_racine(a.root)
    if racine is None:
        sortir(2, message="Dossier ChaineYouTube introuvable. Passe --root ou definis CHAINE_YT_ROOT.")

    dossier = racine / "videos" / a.video
    if not (dossier / "state.json").is_file():
        sortir(6, message=f"Video inconnue : {a.video}")

    state = json.loads((dossier / "state.json").read_text(encoding="utf-8-sig"))
    etapes = state.get("etapes", {})

    cp3 = (etapes.get("CP3") or {}).get("statut")
    if cp3 != "valide":
        sortir(7, message=f"CP3 non valide (statut : {cp3}). Aucune publication sans CP3 valide (§2).",
               checkpoint=cp3)

    if state.get("statut_global") in ("publiee", "programmee") and not a.force:
        sortir(8, message=f"Deja enregistree comme {state['statut_global']}. Relance avec --force pour corriger.",
               statut_global=state["statut_global"],
               publication=state.get("publication"))

    if a.statut == "publiee" and not a.url:
        sortir(4, message="--url est obligatoire pour --statut publiee.")

    date_iso = normaliser_date(a.date)
    if date_iso is None:
        sortir(4, message=f"Date illisible : {a.date}. Attendu AAAA-MM-JJ ou AAAA-MM-JJTHH:MM:SSZ.")

    publication = state.setdefault("publication", {"date_prevue": None, "date_effective": None, "url": None})
    if a.statut == "publiee":
        publication["date_effective"] = date_iso
        # Une video publiee sans passer par `programmee` n'a pas de date
        # prevue : on la renseigne pour que le calendrier reste lisible.
        publication["date_prevue"] = publication.get("date_prevue") or date_iso
    else:
        publication["date_prevue"] = date_iso
    if a.url:
        publication["url"] = a.url

    etape = etapes.setdefault("E7_publication", {"agent": "publication", "tentatives": 0,
                                                 "debut": None, "fin": None, "sorties": []})
    etape["agent"] = etape.get("agent") or "publication"
    etape["tentatives"] = etape.get("tentatives", 0) + 1
    etape["debut"] = etape.get("debut") or date_iso
    if a.statut == "publiee":
        etape["statut"] = "termine"
        etape["fin"] = maintenant_iso()
        etape["message"] = f"Publiee le {date_iso}" + (f" — {a.url}" if a.url else "")
    else:
        # Programmee : l'etape reste ouverte jusqu'a la mise en ligne reelle,
        # sinon elle sortirait du tableau de bord avant d'etre faite.
        etape["statut"] = "attente_franco"
        etape["message"] = f"Programmee pour le {date_iso}"

    state["statut_global"] = a.statut
    state["etape_actuelle"] = "termine" if a.statut == "publiee" else "E7_publication"
    state.setdefault("historique", []).append({
        "horodatage": maintenant_iso(),
        "agent": "publication",
        "evenement": a.statut,
        "message": etape["message"],
    })

    ecrire_state(dossier, state)
    sortir(0, message="Publication enregistree.", video=a.video, statut_global=a.statut,
           publication=publication)


if __name__ == "__main__":
    main()
