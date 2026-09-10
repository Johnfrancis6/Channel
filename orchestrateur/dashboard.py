import json
import os

from .engine import etapes_agent_actionnables
from .state_store import list_video_dirs, load_state, now_iso


def construire_registre(root):
    registre = []
    for video_dir in list_video_dirs(root):
        state = load_state(video_dir)
        registre.append({
            "video_id": state["video_id"],
            "titre_travail": state["titre_travail"],
            "pilier": state["pilier"],
            "voie": state["voie"],
            "statut_global": state["statut_global"],
            "etape_actuelle": state["etape_actuelle"],
            "publication": state.get("publication", {}),
        })
    return registre


def ecrire_registre(root, registre):
    path = os.path.join(root, "registre_videos.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(registre, f, ensure_ascii=False, indent=2)


def _lignes_a_faire(root):
    lignes = []
    for video_dir in list_video_dirs(root):
        state = load_state(video_dir)
        video_id = state["video_id"]
        for etape_id, etape in state["etapes"].items():
            statut = etape.get("statut")
            if statut == "alerte":
                lignes.append(f"- [ALERTE] {video_id} — {etape_id} : {etape.get('tentatives', '?')} echecs (voir historique)")
            elif statut == "attente_validation":
                lignes.append(f"- [{etape_id}] {video_id} — valider le rapport de checkpoint")
            elif statut == "attente_franco":
                lignes.append(f"- [ACTION] {video_id} — {etape_id} : action manuelle requise")
        for a in etapes_agent_actionnables(state):
            verbe = "Relancer" if a["statut"] == "echec" else "Lancer"
            lignes.append(
                f"- [AGENT] {video_id} — {verbe} l'agent {a['agent']} ({a['etape']}, tentative {a['tentatives'] + 1})"
            )
    return lignes


def _lignes_en_production(root):
    lignes = []
    for video_dir in list_video_dirs(root):
        state = load_state(video_dir)
        if state["statut_global"] != "en_production":
            continue
        etape_actuelle = state["etape_actuelle"]
        etape = state["etapes"].get(etape_actuelle, {})
        lignes.append(
            f"| {state['video_id']} | {state['pilier']} | {etape_actuelle} | "
            f"{etape.get('statut', '-')} | {etape.get('tentatives', '-')} |"
        )
    return lignes


def rendre_dashboard(root, config):
    a_faire = _lignes_a_faire(root)
    en_production = _lignes_en_production(root)
    registre = construire_registre(root)

    nb_pretes = sum(1 for v in registre if v["statut_global"] == "prete")
    nb_publiees = sum(1 for v in registre if v["statut_global"] == "publiee")
    nb_abandonnees = sum(1 for v in registre if v["statut_global"] == "abandonnee")
    cible_tampon = config.get("cible_tampon", 4)

    parties = [f"# Tableau de bord — mis a jour le {now_iso()}", ""]

    parties.append("## A faire par Franco maintenant")
    parties.extend(a_faire if a_faire else ["- Rien pour le moment."])
    parties.append("")

    parties.append("## En production")
    parties.append("| Video | Pilier | Etape | Statut | Tentative |")
    parties.append("|---|---|---|---|---|")
    parties.extend(en_production)
    parties.append("")

    parties.append("## Tampon")
    parties.append(f"Pretes : {nb_pretes} / cible {cible_tampon}")
    parties.append("")

    parties.append("## Semaine (cumul, non filtre par date pour l'instant)")
    parties.append(f"Publiees : {nb_publiees} — Abandonnees : {nb_abandonnees}")
    parties.append("")

    return "\n".join(parties)


def ecrire_dashboard(root, config):
    contenu = rendre_dashboard(root, config)
    path = os.path.join(root, "TABLEAU_DE_BORD.md")
    with open(path, "w", encoding="utf-8") as f:
        f.write(contenu)
    return contenu


def ecrire_derniere_execution(root):
    path = os.path.join(root, "01_Orchestrateur", "derniere_execution.json")
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump({"horodatage": now_iso()}, f, ensure_ascii=False, indent=2)
