"""
Machine d'etats de l'Orchestrateur (A1). Fait avancer un video state.json
d'une etape a la suivante, en respectant §4.2 (contrat agent) et §6.2
(sequencement).
"""

import os

from .agents_registry import obtenir_agent
from .checkpoints import archiver_rapport_refuse, generer_rapport_si_absent, lire_decision
from .constants import PIPELINE_PAR_ID
from .state_store import ajouter_historique, now_iso

DEPENDANCES = {
    "E1_recherche": [],
    "CP1": ["E1_recherche"],
    "E2_redaction": ["CP1"],
    "E3_filtre": ["E2_redaction"],
    "CP2": ["E3_filtre"],
    "E4_audio": ["CP2"],
    "E5_storyboard": ["CP2"],
    "E6_montage": ["E4_audio", "E5_storyboard"],
    "CP3": ["E6_montage"],
    "E7_publication": ["CP3"],
}


def _pret(state, etape_id):
    for dep_id in DEPENDANCES[etape_id]:
        dep = state["etapes"].get(dep_id)
        if dep is None:
            return False
        seuil = "valide" if dep_id.startswith("CP") else "termine"
        if dep["statut"] != seuil:
            return False
    return True


def _gerer_boucle_redaction_filtre(state):
    compteur = state.get("boucle_A4_A5", 0) + 1
    state["boucle_A4_A5"] = compteur
    filtre = state["etapes"]["E3_filtre"]
    if compteur >= 3:
        filtre["statut"] = "alerte"
        ajouter_historique(state, "filtre_tts", "alerte",
                            "3 tours de revision redaction/filtre, intervention de Franco requise.")
    else:
        filtre["statut"] = "a_venir"
        state["etapes"]["E2_redaction"]["statut"] = "a_venir"
        ajouter_historique(state, "filtre_tts", "echec", f"Tour {compteur} : retour a la redaction.")


def _executer_etape_agent(video_dir, state, etape_def, max_tentatives):
    etape_id = etape_def["id"]
    etape = state["etapes"][etape_id]
    agent_id = etape_def["agent"]

    tentative_num = etape.get("tentatives", 0) + 1
    etape["agent"] = agent_id
    etape["statut"] = "en_cours"
    etape["tentatives"] = tentative_num
    etape["debut"] = now_iso()

    resultat = obtenir_agent(agent_id).run(video_dir, state, etape_id)

    etape["fin"] = now_iso()
    etape["message"] = resultat["message"]

    if resultat["statut"] == "termine":
        etape["statut"] = "termine"
        etape["sorties"] = resultat["sorties"]
        ajouter_historique(state, agent_id, "termine", resultat["message"])
        return

    if resultat.get("action") == "revision_redaction":
        _gerer_boucle_redaction_filtre(state)
        return

    if tentative_num >= max_tentatives:
        etape["statut"] = "alerte"
        ajouter_historique(state, agent_id, "alerte",
                            f"{etape_id} : {tentative_num} echecs, intervention de Franco requise.")
    else:
        etape["statut"] = "echec"
        ajouter_historique(state, agent_id, "echec", resultat["message"])


def _lire_extrait(video_dir, nom_fichier, max_chars=3000):
    chemin = os.path.join(video_dir, nom_fichier)
    if not os.path.isfile(chemin):
        return None
    with open(chemin, "r", encoding="utf-8") as f:
        contenu = f.read()
    if len(contenu) > max_chars:
        contenu = contenu[:max_chars] + "\n\n[...]"
    return contenu


RESUME_SOURCES = {
    "CP1": [("01_recherche.md", "Recherche")],
    "CP2": [("03_script_final.md", "Script final"), ("03_rapport_metriques.md", "Rapport metriques (nouveaux termes de lexique)")],
    "CP3": [("05_storyboard.md", "Storyboard")],
}


def _construire_resume_checkpoint(video_dir, state, checkpoint_id):
    morceaux = []
    # Un checkpoint ne revient a `a_venir` qu'apres un refus : si un
    # commentaire subsiste au moment de le rouvrir, c'est celui de ce refus.
    # On le rappelle pour que Franco voie ce qu'il avait demande.
    refus_precedent = state["etapes"][checkpoint_id].get("commentaire")
    if refus_precedent:
        morceaux.append(f"> Refus precedent : {refus_precedent}\n> "
                         f"(rapport archive dans `checkpoints/refuses/`)")
    if checkpoint_id == "CP1":
        morceaux.append(f"Sujet : {state.get('sujet') or state.get('titre_travail') or '(a determiner)'}")
        if state.get("angle"):
            morceaux.append(f"Angle propose : {state['angle']}")
    for nom_fichier, titre in RESUME_SOURCES.get(checkpoint_id, []):
        extrait = _lire_extrait(video_dir, nom_fichier)
        if extrait:
            morceaux.append(f"## {titre} (`{nom_fichier}`)\n\n{extrait}")
    if checkpoint_id == "CP3":
        morceaux.append("Champs SEO a remplir dans le bloc de decision : titre, description, tags (§11).")
    if not morceaux:
        return f"Resume a completer pour {checkpoint_id} (aucune sortie trouvee)."
    return "\n\n".join(morceaux)


def _ouvrir_checkpoint_si_pret(video_dir, state, etape_id):
    etape = state["etapes"][etape_id]
    if etape["statut"] == "a_venir" and _pret(state, etape_id):
        etape["statut"] = "attente_validation"
        resume = _construire_resume_checkpoint(video_dir, state, etape_id)
        generer_rapport_si_absent(video_dir, etape_id, resume=resume)


ETAPES_A_REPRENDRE_APRES_REFUS = {
    "CP1": ["E1_recherche"],
    "CP2": ["E2_redaction", "E3_filtre"],
    "CP3": ["E6_montage"],
}


def _reagir_au_refus(video_dir, state, checkpoint_id):
    """
    Refus de Franco (§5.5) : les etapes en amont repartent avec le commentaire
    en input, et le checkpoint lui-meme revient a `a_venir` pour pouvoir se
    rouvrir quand elles auront fini.

    Remettre le checkpoint a `a_venir` est indispensable : laisse a `refuse`,
    il ne se rouvrait jamais (_ouvrir_checkpoint_si_pret n'agit que sur
    `a_venir`) et _pret() bloquait tout l'aval, qui exige `valide`. La video
    restait coincee sans rien signaler au tableau de bord.
    """
    for etape_id in ETAPES_A_REPRENDRE_APRES_REFUS[checkpoint_id]:
        etape = state["etapes"][etape_id]
        etape["statut"] = "a_venir"
        # Un refus n'est pas un echec technique : le compteur repart a zero,
        # sinon quelques refus suffisent a declencher une fausse alerte.
        etape["tentatives"] = 0
        etape.pop("action", None)

    if checkpoint_id == "CP2":
        # La boucle A4<->A5 repart elle aussi : sinon un refus sur une video
        # ayant deja boucle deux fois partirait en alerte des le premier tour.
        state["boucle_A4_A5"] = 0

    # Le commentaire reste dans l'etape du checkpoint : c'est l'input de
    # l'agent relance (§5.5). Seul le statut est remis a zero.
    state["etapes"][checkpoint_id]["statut"] = "a_venir"
    archiver_rapport_refuse(video_dir, checkpoint_id)


def _transcrire_decisions_franco(video_dir, state):
    for checkpoint_id in ("CP1", "CP2", "CP3"):
        etape = state["etapes"].get(checkpoint_id)
        if not etape or etape["statut"] != "attente_validation":
            continue
        decision = lire_decision(video_dir, checkpoint_id)
        if not decision or decision["statut"] not in ("VALIDE", "REFUSE"):
            continue
        nouveau_statut = "valide" if decision["statut"] == "VALIDE" else "refuse"
        etape["statut"] = nouveau_statut
        etape["commentaire"] = decision["commentaire"]
        etape["date"] = now_iso()
        ajouter_historique(state, "orchestrateur", f"{checkpoint_id}_{nouveau_statut}",
                            decision["commentaire"] or "")
        if nouveau_statut == "refuse":
            _reagir_au_refus(video_dir, state, checkpoint_id)


def _mettre_a_jour_statut_global(state):
    etapes = state["etapes"]
    if etapes["CP1"]["statut"] == "valide" and state["statut_global"] in ("idee", "sujet_valide"):
        state["statut_global"] = "en_production"
    if etapes.get("CP3", {}).get("statut") == "valide":
        state["statut_global"] = "prete"


def _mettre_a_jour_etape_actuelle(state):
    for etape_id in PIPELINE_PAR_ID:
        etape = state["etapes"].get(etape_id)
        if etape is None:
            continue
        termine = etape["statut"] in ("valide",) if etape_id.startswith("CP") else etape["statut"] == "termine"
        if not termine:
            state["etape_actuelle"] = etape_id
            return
    state["etape_actuelle"] = "termine"


def _traiter_echec_agent_reel(state, etape_id, max_tentatives):
    """
    Mode reel : l'Orchestrateur ne relance pas lui-meme l'agent (c'est un
    skill Claude Code lance a la main ou en headless). Il gere seulement ce
    qui lui revient : la boucle A4<->A5 et l'escalade en alerte a 3 echecs.
    """
    etape = state["etapes"][etape_id]
    if etape_id == "E3_filtre" and etape.get("action") == "revision_redaction":
        _gerer_boucle_redaction_filtre(state)
        return
    tentatives = etape.get("tentatives", 0)
    if tentatives >= max_tentatives:
        etape["statut"] = "alerte"
        ajouter_historique(state, etape.get("agent", etape_id), "alerte",
                            f"{etape_id} : {tentatives} echecs, intervention de Franco requise.")
    # sinon on laisse "echec" : l'agent reel devra etre relance manuellement
    # (l'action apparait au tableau de bord via etapes_agent_actionnables).


def etapes_agent_actionnables(state):
    """Etapes 'agent' (a_venir ou echec) pretes a etre lancees par un agent reel."""
    resultat = []
    for etape_def in PIPELINE_PAR_ID.values():
        if etape_def["kind"] != "agent":
            continue
        etape_id = etape_def["id"]
        etape = state["etapes"].get(etape_id)
        if etape is None or etape["statut"] not in ("a_venir", "echec"):
            continue
        if _pret(state, etape_id):
            resultat.append({
                "etape": etape_id,
                "agent": etape_def["agent"],
                "statut": etape["statut"],
                "tentatives": etape.get("tentatives", 0),
            })
    return resultat


def traiter_video(video_dir, state, config):
    """Fait avancer une video d'un pas d'execution de l'Orchestrateur. Mute `state`."""
    max_tentatives = config["max_tentatives"]
    mode_agents = config.get("mode_agents", "factice")

    _transcrire_decisions_franco(video_dir, state)

    for etape_def in PIPELINE_PAR_ID.values():
        etape_id = etape_def["id"]
        etape = state["etapes"].get(etape_id)
        if etape is None:
            continue

        if etape_def["kind"] == "agent":
            if mode_agents == "factice":
                if etape["statut"] in ("a_venir", "echec") and _pret(state, etape_id):
                    _executer_etape_agent(video_dir, state, etape_def, max_tentatives)
            else:
                if etape["statut"] == "echec":
                    _traiter_echec_agent_reel(state, etape_id, max_tentatives)
                # "a_venir" et pret : rien a faire ici, voir etapes_agent_actionnables

        elif etape_def["kind"] == "checkpoint":
            _ouvrir_checkpoint_si_pret(video_dir, state, etape_id)

        elif etape_def["kind"] in ("attente_franco", "manuel"):
            if etape["statut"] == "a_venir" and _pret(state, etape_id):
                etape["statut"] = "attente_franco"

    _mettre_a_jour_statut_global(state)
    _mettre_a_jour_etape_actuelle(state)
