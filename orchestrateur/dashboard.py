import json
import os
from datetime import datetime, timedelta, timezone

from .engine import etapes_agent_actionnables
from .hebdo import taches_hebdo_manquantes
from .state_store import list_video_dirs, load_state, now_iso


def _parse_iso(valeur):
    try:
        return datetime.strptime(valeur, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
    except (ValueError, TypeError):
        return None


def _depuis(debut, maintenant):
    heures = (maintenant - debut).total_seconds() / 3600
    return f"{heures:.0f} h" if heures >= 1 else f"{heures * 60:.0f} min"


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


def _lignes_a_faire(root, config):
    lignes = []
    maintenant = datetime.now(timezone.utc)
    seuil_blocage = timedelta(hours=float(config.get("seuil_blocage_heures", 2)))
    for video_dir in list_video_dirs(root):
        state = load_state(video_dir)
        video_id = state["video_id"]
        for etape_id, etape in state["etapes"].items():
            statut = etape.get("statut")
            if statut == "en_cours":
                # En mode `reel`, un agent qui plante ou qu'on interrompt laisse
                # son etape a `en_cours` pour toujours : elle n'est ni relancable
                # (etapes_agent_actionnables ignore `en_cours`) ni signalee. Sans
                # ce test, la video s'arrete en silence. short-state le detecte
                # deja avec le meme seuil ; le tableau de bord doit le voir aussi.
                debut = _parse_iso(etape.get("debut"))
                if debut and maintenant - debut > seuil_blocage:
                    lignes.append(
                        f"- [BLOQUE] {video_id} — {etape_id} : en cours depuis "
                        f"{_depuis(debut, maintenant)}, l'agent a probablement echoue"
                    )
            elif statut == "alerte":
                lignes.append(f"- [ALERTE] {video_id} — {etape_id} : {etape.get('tentatives', '?')} echecs (voir historique)")
            elif statut == "attente_validation":
                lignes.append(f"- [{etape_id}] {video_id} — valider le rapport de checkpoint")
            elif statut == "attente_franco":
                lignes.append(f"- [ACTION] {video_id} — {etape_id} : action manuelle requise")
            elif statut == "refuse":
                # Filet de securite : l'Orchestrateur remet normalement le
                # checkpoint a `a_venir` apres un refus. Un `refuse` qui
                # persiste signale une video figee, a ne pas laisser invisible.
                lignes.append(f"- [REFUS] {video_id} — {etape_id} : refuse, reprise non declenchee")
        for a in etapes_agent_actionnables(state):
            verbe = "Relancer" if a["statut"] == "echec" else "Lancer"
            lignes.append(
                f"- [AGENT] {video_id} — {verbe} l'agent {a['agent']} ({a['etape']}, tentative {a['tentatives'] + 1})"
            )

    semaine, manquantes = taches_hebdo_manquantes(root)
    for m in manquantes:
        lignes.append(f"- [HEBDO] {semaine} — {m['tache']} : `{m['fichier_attendu']}` manquant")

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
    a_faire = _lignes_a_faire(root, config)
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
