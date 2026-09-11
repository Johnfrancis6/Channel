#!/usr/bin/env python3
"""Orchestrateur — machine d'états pilotée par videos/*/state.json.

Il ne garde aucune mémoire entre deux exécutions (voir docs/architecture_chaine_v1.2.md §4.3/§5).
Codes de sortie : 0 ok | 1 au moins un state.json corrompu | 2 racine introuvable | 3 verrou actif.
"""
import argparse
import json
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

MAX_TENTATIVES = 3
VERROU_TTL_SECONDES = 15 * 60

# Séquence des étapes d'une vidéo (docs/architecture_chaine_v1.2.md §5.2, §6.2).
SEQUENCE = [
    "E1_recherche",
    "CP1",
    "E2_redaction",
    "E3_filtre",
    "CP2",
    "E4_audio",
    "E5_storyboard",
    "E6_montage",
    "CP3",
    "E7_publication",
]
# Après CP2, E4_audio et E5_storyboard démarrent en parallèle ; E6_montage
# attend que les deux soient "termine" avant de démarrer.
ETAPES_PARALLELES = ("E4_audio", "E5_storyboard")

# [ \t]* et non \s* : \s inclut les sauts de ligne et mangerait tout jusqu'à
# la prochaine ligne non vide (ex. le "---" qui suit "Commentaire : " vide).
RE_STATUT = re.compile(r"^Statut[ \t]*:[ \t]*(\S+)", re.MULTILINE)
RE_COMMENTAIRE = re.compile(r"^Commentaire[ \t]*:[ \t]*(.*)$", re.MULTILINE)


def maintenant():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def trouver_racine(root_arg):
    candidats = []
    if root_arg:
        candidats.append(Path(root_arg))
    env = os.environ.get("CHAINE_YT_ROOT")
    if env:
        candidats.append(Path(env))
    home = Path.home()
    utilisateur = os.environ.get("USERNAME") or os.environ.get("USER") or ""
    candidats += [
        home / "ChaineYouTube",
        home / "Google Drive" / "Mon Drive" / "ChaineYouTube",
        home / "GoogleDrive" / "Mon Drive" / "ChaineYouTube",
        Path("G:/Mon Drive/ChaineYouTube"),
        Path("C:/Users") / utilisateur / "ChaineYouTube",
    ]
    for candidat in candidats:
        if candidat and candidat.is_dir():
            return candidat
    return None


def ecrire_json_atomique(chemin, data, dry_run):
    if dry_run:
        return
    chemin.parent.mkdir(parents=True, exist_ok=True)
    tmp = chemin.with_suffix(chemin.suffix + ".tmp")
    tmp.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    tmp.replace(chemin)


def log_erreur(root, message, dry_run):
    if dry_run:
        print(f"[dry-run] log_erreurs.md <- {message}")
        return
    dossier = root / "01_Orchestrateur"
    dossier.mkdir(parents=True, exist_ok=True)
    with (dossier / "log_erreurs.md").open("a", encoding="utf-8") as f:
        f.write(f"- {maintenant()} : {message}\n")


def acquerir_verrou(root, dry_run):
    if dry_run:
        return True, None
    dossier = root / "01_Orchestrateur"
    dossier.mkdir(parents=True, exist_ok=True)
    chemin = dossier / "verrou.json"
    if chemin.exists():
        try:
            data = json.loads(chemin.read_text(encoding="utf-8"))
            pose_le = datetime.strptime(data["horodatage"], "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
            age = (datetime.now(timezone.utc) - pose_le).total_seconds()
            if age < VERROU_TTL_SECONDES:
                return False, None
        except (OSError, KeyError, ValueError):
            pass  # verrou corrompu ou illisible : on le considère comme expiré
    ecrire_json_atomique(chemin, {"pid": os.getpid(), "horodatage": maintenant()}, dry_run=False)
    return True, chemin


def liberer_verrou(chemin, dry_run):
    if dry_run or chemin is None:
        return
    chemin.unlink(missing_ok=True)


def charger_state(chemin):
    try:
        return json.loads(chemin.read_text(encoding="utf-8")), None
    except (json.JSONDecodeError, OSError) as exc:
        return None, str(exc)


def lire_decision(chemin_rapport):
    """Renvoie (statut, commentaire). statut est None si le rapport n'existe pas encore."""
    if not chemin_rapport.exists():
        return None, None
    texte = chemin_rapport.read_text(encoding="utf-8")
    marqueur = "## DÉCISION" if "## DÉCISION" in texte else "## DECISION"
    if marqueur not in texte:
        return None, None
    bloc = texte.split(marqueur, 1)[1]
    m_statut = RE_STATUT.search(bloc)
    m_commentaire = RE_COMMENTAIRE.search(bloc)
    statut = m_statut.group(1).strip().upper() if m_statut else "EN_ATTENTE"
    commentaire = m_commentaire.group(1).strip() if m_commentaire else ""
    return statut, commentaire


def etape_suivante(etape):
    if etape == "CP2":
        return ETAPES_PARALLELES
    if etape not in SEQUENCE:
        return None
    idx = SEQUENCE.index(etape)
    if idx + 1 >= len(SEQUENCE):
        return None
    return (SEQUENCE[idx + 1],)


def etape_precedente(etape):
    if etape in ETAPES_PARALLELES:
        return "CP2"
    if etape not in SEQUENCE:
        return None
    idx = SEQUENCE.index(etape)
    return SEQUENCE[idx - 1] if idx > 0 else None


def statut_initial(nom_etape):
    if nom_etape.startswith("CP"):
        return "attente_validation"
    if nom_etape in ("E4_audio", "E7_publication"):
        return "attente_franco"  # action manuelle de Franco (run Colab, publication)
    return "en_cours"


def ajouter_historique(state, agent, evenement, message):
    state.setdefault("historique", []).append(
        {"horodatage": maintenant(), "agent": agent, "evenement": evenement, "message": message}
    )


def avancer(state, etape_terminee, video_id, actions):
    etapes = state["etapes"]

    # Étape parallèle : n'avance vers E6_montage que si la sœur est aussi terminée.
    if etape_terminee in ETAPES_PARALLELES:
        soeur = ETAPES_PARALLELES[1] if etape_terminee == ETAPES_PARALLELES[0] else ETAPES_PARALLELES[0]
        fronts = [f for f in str(state.get("etape_actuelle", "")).split(",") if f]
        fronts = [f for f in fronts if f != etape_terminee] or [etape_terminee]
        state["etape_actuelle"] = ",".join(fronts)
        if etapes.get(soeur, {}).get("statut") != "termine":
            actions.append(f"{video_id} : {etape_terminee} terminé, en attente de {soeur}")
            return

    suivantes = etape_suivante(etape_terminee)
    if suivantes is None:
        actions.append(f"{video_id} : {etape_terminee} terminé — fin de séquence")
        return

    noms = []
    for nom in suivantes:
        statut = statut_initial(nom)
        info = {"statut": statut}
        if statut == "attente_validation":
            info = {"statut": statut, "commentaire": None, "date": None}
        else:
            info["debut"] = maintenant()
        etapes[nom] = info
        noms.append(nom)
    state["etape_actuelle"] = ",".join(noms)
    ajouter_historique(state, etape_terminee, "termine", f"Passage à {', '.join(noms)}")
    actions.append(f"{video_id} : {etape_terminee} → {', '.join(noms)}")


def traiter_video(dossier_video, root, dry_run, actions):
    video_id = dossier_video.name
    chemin_state = dossier_video / "state.json"
    state, erreur = charger_state(chemin_state)
    if state is None:
        log_erreur(root, f"{video_id} : state.json illisible ({erreur})", dry_run)
        actions.append(f"{video_id} : state.json corrompu — ignorée")
        return "corrompue"

    etapes = state.setdefault("etapes", {})
    fronts = [f for f in str(state.get("etape_actuelle", "")).split(",") if f]
    if not fronts:
        actions.append(f"{video_id} : etape_actuelle manquante — rien à faire")
        return "ok"

    modifie = False
    for front in fronts:
        info = etapes.get(front, {})
        statut = info.get("statut")

        if statut == "termine":
            avancer(state, front, video_id, actions)
            modifie = True

        elif statut == "echec":
            tentatives = info.get("tentatives", 0) + 1
            info["tentatives"] = tentatives
            if tentatives < MAX_TENTATIVES:
                info["statut"] = "en_cours"
                info["debut"] = maintenant()
                ajouter_historique(state, front, "relance", f"Tentative {tentatives}")
                actions.append(f"{video_id} : {front} relancé (tentative {tentatives}/{MAX_TENTATIVES})")
            else:
                info["statut"] = "alerte"
                ajouter_historique(state, front, "alerte", f"{MAX_TENTATIVES} échecs consécutifs")
                log_erreur(root, f"{video_id} : {front} en alerte après {MAX_TENTATIVES} échecs", dry_run)
                actions.append(f"{video_id} : ALERTE {front} — intervention de Franco requise")
            etapes[front] = info
            modifie = True

        elif front.startswith("CP") and statut == "attente_validation":
            chemin_rapport = dossier_video / "checkpoints" / f"rapport_{front}.md"
            decision, commentaire = lire_decision(chemin_rapport)
            if decision is None:
                actions.append(f"{video_id} : {front} — rapport absent, rien à faire")
            elif decision == "EN_ATTENTE":
                actions.append(f"{video_id} : {front} — en attente de la décision de Franco")
            elif decision == "VALIDE":
                info.update({"statut": "valide", "commentaire": commentaire, "date": maintenant()})
                etapes[front] = info
                ajouter_historique(state, front, "valide", commentaire or "")
                actions.append(f"{video_id} : {front} validé par Franco")
                avancer(state, front, video_id, actions)
                modifie = True
            elif decision == "REFUSE":
                info.update({"statut": "refuse", "commentaire": commentaire, "date": maintenant()})
                etapes[front] = info
                ajouter_historique(state, front, "refuse", commentaire or "")
                precedente = etape_precedente(front)
                if precedente:
                    prev = etapes.get(precedente, {})
                    prev.update({"statut": "en_cours", "debut": maintenant(), "commentaire_refus": commentaire})
                    etapes[precedente] = prev
                    state["etape_actuelle"] = precedente
                actions.append(f"{video_id} : {front} refusé — retour à {precedente or '?'}")
                modifie = True
            else:
                actions.append(f"{video_id} : {front} — statut de décision non reconnu ({decision!r})")
        # "en_cours" et "a_venir" : l'agent travaille encore ou l'étape n'a pas démarré, rien à faire.

    if modifie:
        if dry_run:
            actions.append(f"{video_id} : state.json serait mis à jour (dry-run)")
        else:
            ecrire_json_atomique(chemin_state, state, dry_run=False)
    return "ok"


def main():
    parser = argparse.ArgumentParser(description="Orchestrateur de la chaîne YouTube")
    parser.add_argument("--root", help="Racine /ChaineYouTube (sinon CHAINE_YT_ROOT, sinon emplacements habituels)")
    parser.add_argument("--dry-run", action="store_true", help="Ne rien écrire, seulement afficher les actions")
    args = parser.parse_args()

    root = trouver_racine(args.root)
    if root is None:
        print(json.dumps({"ok": False, "code": 2, "message": "racine introuvable", "videos_traitees": 0}, ensure_ascii=False))
        return 2

    verrou_ok, chemin_verrou = acquerir_verrou(root, args.dry_run)
    if not verrou_ok:
        print(json.dumps({"ok": False, "code": 3, "message": "verrou actif, autre exécution en cours", "videos_traitees": 0}, ensure_ascii=False))
        return 3

    actions = []
    corrompues = []
    videos_traitees = 0
    dossier_videos = root / "videos"
    if dossier_videos.is_dir():
        for dossier_video in sorted(p for p in dossier_videos.iterdir() if p.is_dir()):
            resultat = traiter_video(dossier_video, root, args.dry_run, actions)
            videos_traitees += 1
            if resultat == "corrompue":
                corrompues.append(dossier_video.name)

    ecrire_json_atomique(
        root / "01_Orchestrateur" / "derniere_execution.json",
        {"horodatage": maintenant(), "videos_traitees": videos_traitees},
        args.dry_run,
    )
    liberer_verrou(chemin_verrou, args.dry_run)

    code = 1 if corrompues else 0
    sortie = {"ok": not corrompues, "code": code, "videos_traitees": videos_traitees, "actions": actions}
    if corrompues:
        sortie["corrompues"] = corrompues
    print(json.dumps(sortie, ensure_ascii=False, indent=2))
    return code


if __name__ == "__main__":
    sys.exit(main())
