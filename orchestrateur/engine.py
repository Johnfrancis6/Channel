"""
Machine d'etats de l'Orchestrateur (A1). Fait avancer un video state.json
d'une etape a la suivante, en respectant §4.2 (contrat agent) et §6.2
(sequencement).
"""

import os
import re
import unicodedata

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


RE_TITRE = re.compile(r"^#{1,6} .*$", re.MULTILINE)


def _normaliser_titre(texte):
    sans_accent = unicodedata.normalize("NFKD", texte).encode("ascii", "ignore").decode().lower()
    return re.sub(r"[^a-z0-9]+", " ", sans_accent).strip()


def _decouper_sections(contenu):
    """[(titre|None, bloc)] en suivant les titres Markdown. Le preambule a un titre None."""
    debuts = [m.start() for m in RE_TITRE.finditer(contenu)]
    if not debuts:
        return [(None, contenu)]
    sections = []
    if debuts[0] > 0:
        sections.append((None, contenu[:debuts[0]]))
    bornes = debuts + [len(contenu)]
    for i, depart in enumerate(debuts):
        bloc = contenu[depart:bornes[i + 1]]
        sections.append((bloc.splitlines()[0], bloc))
    return sections


def _tronquer(bloc, budget):
    return bloc[:max(budget, 0)].rstrip() + "\n\n[...]"


def _extraire_sections(contenu, max_chars, sections_prioritaires):
    """
    Reduit `contenu` a `max_chars`, en gardant d'abord les sections dont le
    titre correspond a `sections_prioritaires`.

    Une troncature naive par le debut coupait le rapport de CP1 en plein
    milieu d'une phrase, et jetait precisement la section "Points a trancher
    par Franco" — c'est-a-dire les questions sur lesquelles il doit decider.
    Restaient les sources, qui ne servent pas a decider. Le rapport de
    checkpoint est fait pour etre lu au telephone sans ouvrir les sorties
    (§5.5) : ce qui porte la decision doit survivre a la coupe.
    """
    if len(contenu) <= max_chars:
        return contenu

    sections = _decouper_sections(contenu)
    motifs = [_normaliser_titre(p) for p in sections_prioritaires if p]
    est_prio = [
        bool(titre) and any(motif in _normaliser_titre(titre) for motif in motifs)
        for titre, _ in sections
    ]

    budget = max_chars
    gardees = {}
    for indices in ([i for i, p in enumerate(est_prio) if p],
                    [i for i, p in enumerate(est_prio) if not p]):
        for i in indices:
            if budget <= 0:
                break
            bloc = sections[i][1]
            if len(bloc) > budget:
                gardees[i] = _tronquer(bloc, budget)
                budget = 0
            else:
                gardees[i] = bloc
                budget -= len(bloc)

    morceaux = []
    precedent = None
    for i in sorted(gardees):
        if precedent is not None and i != precedent + 1:
            morceaux.append("[...]")
        morceaux.append(gardees[i].strip())
        precedent = i
    if gardees and max(gardees) != len(sections) - 1:
        morceaux.append("[...]")
    return "\n\n".join(morceaux)


def _lire_extrait(video_dir, nom_fichier, max_chars=3000, sections_prioritaires=()):
    chemin = os.path.join(video_dir, nom_fichier)
    if not os.path.isfile(chemin):
        return None
    with open(chemin, "r", encoding="utf-8-sig") as f:
        contenu = f.read()
    return _extraire_sections(contenu, max_chars, sections_prioritaires)


# (fichier, titre affiche, sections a preserver en priorite si le fichier
# depasse la taille de l'extrait). Ce sont les sections qui portent la
# decision de Franco, pas celles qui l'informent.
RESUME_SOURCES = {
    "CP1": [("01_recherche.md", "Recherche",
             # "Angle confirme" en mode sujet_impose, "Angle propose" sinon.
             ("Points a trancher", "Angle confirme", "Angle propose",
              "Incertitudes"))],
    "CP2": [("03_script_final.md", "Script final", ()),
            ("03_rapport_metriques.md", "Rapport metriques (nouveaux termes de lexique)",
             ("Nouveaux termes", "Lexique", "A corriger", "Hors cible"))],
    "CP3": [("05_storyboard.md", "Storyboard",
             ("Nouveaux composants", "Duree totale"))],
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
    for nom_fichier, titre, prioritaires in RESUME_SOURCES.get(checkpoint_id, []):
        extrait = _lire_extrait(video_dir, nom_fichier, sections_prioritaires=prioritaires)
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


def _traiter_echec_etape_manuelle(state, etape_id, max_tentatives):
    """
    Une etape manuelle peut echouer sans qu'aucun agent soit en cause : le
    notebook Colab passe `E4_audio` a `echec` quand le controle qualite WER
    ne passe pas (§7.2, cellule 5).

    Rien ne rattrapait ce statut. E4_audio n'est pas de kind "agent", donc ni
    _traiter_echec_agent_reel ni etapes_agent_actionnables ne la regardaient,
    et la branche `attente_franco`/`manuel` de traiter_video ne traitait que
    `a_venir`. Le run audio pouvait echouer trois fois d'affilee sans que rien
    n'apparaisse au tableau de bord : la video disparaissait de "A faire par
    Franco" et s'arretait la.

    On applique donc la regle du §2 : relance tant qu'on est sous les 3
    tentatives (ici, c'est Franco qui relance le run), alerte au-dela.
    """
    etape = state["etapes"][etape_id]
    tentatives = etape.get("tentatives", 0)
    message = etape.get("message") or "echec"
    agent = etape.get("agent") or etape_id

    if tentatives >= max_tentatives:
        etape["statut"] = "alerte"
        ajouter_historique(state, agent, "alerte",
                            f"{etape_id} : {tentatives} echecs, intervention de Franco requise.")
    else:
        etape["statut"] = "attente_franco"
        ajouter_historique(state, agent, "attente_franco",
                            f"{etape_id} : {message} — a relancer par Franco.")


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
            elif etape["statut"] == "echec":
                _traiter_echec_etape_manuelle(state, etape_id, max_tentatives)

    _mettre_a_jour_statut_global(state)
    _mettre_a_jour_etape_actuelle(state)
