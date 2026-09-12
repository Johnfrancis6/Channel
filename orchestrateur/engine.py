"""
Machine d'etats de l'Orchestrateur (A1). Fait avancer un video state.json
d'une etape a la suivante, en respectant §4.2 (contrat agent) et §6.2
(sequencement).
"""

import json
import os
import re
import unicodedata

from .agents_registry import obtenir_agent
from .checkpoints import archiver_rapport_refuse, generer_rapport_si_absent, lire_decision
from .constants import DEPENDANCES, ORDRE_IDS, PIPELINE_PAR_ID, STATUTS_CLOS, STATUTS_E7
from .state_store import ajouter_historique, now_iso

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


# Sections qui ne portent jamais la decision, a aucun checkpoint : une
# liste de liens se verifie en ouvrant le fichier, elle ne se lit pas au
# telephone. Servies en dernier, elles ne prennent que ce qui reste.
SECTIONS_RELEGUEES = ("Sources",)


def _rang_section(titre, motifs_prioritaires):
    """
    (rang, sous-rang) : 0 porte la decision, 1 l'informe, 2 ne fait que la
    documenter.

    Le sous-rang est la **position du motif dans `sections_prioritaires`**.
    Sans lui, les sections prioritaires se servaient entre elles dans
    l'ordre du document, et l'ordre declare ne voulait rien dire : au CP2,
    `Hors cible` precede `Budget` dans le rapport et prenait tout le budget,
    alors que le verdict de longueur est ce qui porte la decision.
    """
    if not titre:
        return (1, 0)
    normalise = _normaliser_titre(titre)
    for position, motif in enumerate(motifs_prioritaires):
        if motif in normalise:
            return (0, position)
    if any(_normaliser_titre(r) in normalise for r in SECTIONS_RELEGUEES):
        return (2, 0)
    return (1, 0)


def _extraire_sections(contenu, max_chars, sections_prioritaires):
    """
    Reduit `contenu` a `max_chars` en trois rangs : ce qui porte la
    decision, ce qui l'informe, ce qui ne fait que la documenter.

    Une troncature naive par le debut coupait le rapport de CP1 en plein
    milieu d'une phrase, et jetait precisement la section "Points a trancher
    par Franco" — c'est-a-dire les questions sur lesquelles il doit decider.
    Le rapport de checkpoint est fait pour etre lu au telephone sans ouvrir
    les sorties (§5.5) : ce qui porte la decision doit survivre a la coupe.

    Les deux rangs ont d'abord suffi, mais le reste du budget se servait
    dans l'ordre du document — et `## Sources` est la premiere section de
    `01_recherche.md`. Mesure sur le rapport reel de 2026-09-11_v01 (4538
    caracteres pour 3000) : 506 caracteres de liens gardes entiers pendant
    que `## Faits verifies` — le coeur de la recherche — tombait a 622 sur
    2151. Le troisieme rang lui rend exactement ces 506 caracteres : 1128.

    Le meme defaut vivait un rang plus haut : entre sections prioritaires,
    c'etait encore l'ordre du document qui tranchait. Au CP2, `Hors cible`
    precede `Budget` dans le rapport et prenait tout. L'ordre dans lequel
    `sections_prioritaires` est ecrit fait donc foi.
    """
    if len(contenu) <= max_chars:
        return contenu

    sections = _decouper_sections(contenu)
    motifs = [_normaliser_titre(p) for p in sections_prioritaires if p]
    rangs = [_rang_section(titre, motifs) for titre, _ in sections]

    # Rang, puis ordre declare des priorites, puis ordre du document.
    ordre = sorted(range(len(sections)), key=lambda i: (rangs[i], i))

    budget = max_chars
    gardees = {}
    for i in ordre:
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
             # "Matiere a hook" est dans le gabarit d'A2 mais n'etait pas
             # prioritaire : c'est pourtant ce qui dit si le sujet accrochera,
             # donc ce sur quoi Franco tranche au CP1.
             ("Points a trancher", "Angle confirme", "Angle propose",
              "Incertitudes", "Matiere a hook"))],
    "CP2": [("03_script_final.md", "Script final", ()),
            ("03_rapport_metriques.md", "Rapport metriques (budget et nouveaux termes)",
             # "Budget" d'abord : c'est la seule section du CP2 qui parle de
             # longueur. Sur 2026-09-11_v01 le script depassait de 91 % et le
             # rapport n'en disait pas un mot — ni le gabarit d'A5 ni ces
             # priorites ne prevoyaient la question.
             ("Budget", "Nouveaux termes", "Lexique", "A corriger", "Hors cible"))],
    "CP3": [("05_storyboard.md", "Storyboard (rappel du plan)",
             ("Nouveaux composants", "Duree totale"))],
}


def _octets_lisibles(n):
    for unite in ("o", "Ko", "Mo", "Go"):
        if n < 1024 or unite == "Go":
            return f"{n:.0f} {unite}" if unite == "o" else f"{n:.1f} {unite}"
        n /= 1024
    return f"{n:.1f} Go"


def _lire_json(video_dir, nom_fichier):
    chemin = os.path.join(video_dir, nom_fichier)
    if not os.path.isfile(chemin):
        return None
    try:
        with open(chemin, "r", encoding="utf-8-sig") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        return None


def _resume_video_finale(video_dir, state):
    """
    Ce qu'il faut pour decider au CP3 : le fichier a regarder, sa duree face
    a celle de l'audio, et ce que le Monteur signale.

    Le rapport ne montrait que le storyboard — le plan de tournage, pas le
    resultat. Sur 2026-09-11_v01, le fichier video n'etait meme pas nomme,
    et l'ecart de 16,4 s entre le rendu (98,9 s) et la voix off (82,5 s)
    n'apparaissait nulle part. Franco validait le rendu final sans qu'aucun
    chiffre du rendu ne lui soit presente.
    """
    montage = state.get("etapes", {}).get("E6_montage", {}) or {}
    lignes = ["## La video a valider", ""]

    sorties = [s for s in (montage.get("sorties") or []) if s.endswith(".mp4")]
    nom_mp4 = sorties[0] if sorties else "06_video_finale.mp4"
    chemin_mp4 = os.path.join(video_dir, nom_mp4)
    if os.path.isfile(chemin_mp4):
        lignes.append(f"- **Fichier** : `{nom_mp4}` ({_octets_lisibles(os.path.getsize(chemin_mp4))})")
    else:
        lignes.append(f"- **Fichier** : `{nom_mp4}` — *introuvable dans le dossier de la video*")

    storyboard = _lire_json(video_dir, "05_storyboard.json") or {}
    scenes = storyboard.get("scenes") or []
    duree_rendu = round(sum(float(sc.get("duree_s") or 0) for sc in scenes), 1) if scenes else None

    phrases = _lire_json(video_dir, "04_phrases.json") or {}
    duree_audio = phrases.get("duree_totale_s")

    if duree_rendu:
        lignes.append(f"- **Duree du rendu** : {duree_rendu} s, sur {len(scenes)} scenes")
    if duree_audio:
        lignes.append(f"- **Duree de la voix off** : {duree_audio} s")
    if duree_rendu and duree_audio:
        ecart = round(duree_rendu - duree_audio, 1)
        if abs(ecart) > 1:
            sens = "depasse la voix off" if ecart > 0 else "s'arrete avant la fin de la voix off"
            lignes.append(f"- ⚠️ **Ecart de {abs(ecart)} s** : le visuel {sens}. "
                           f"Le recalage sur `04_phrases.json` n'a pas eu lieu.")

    a_completer = [sc.get("id") for sc in scenes if sc.get("a_completer")]
    if a_completer:
        lignes.append(f"- ⚠️ **Scenes non tranchees par le Designer** : {', '.join(map(str, a_completer))} "
                       f"— le storyboard a ete livre a l'etat de squelette.")

    nouveaux = storyboard.get("nouveaux_composants_necessaires") or []
    if nouveaux:
        lignes.append(f"- **Nouveaux composants** : {', '.join(nouveaux)} — "
                       f"ils n'ont jamais ete revus ailleurs qu'ici (§8).")

    if montage.get("message"):
        lignes.append(f"- **Monteur** : {montage['message']}")

    lignes += [
        "",
        "**Regarde la video avant de valider.** Ce qui suit est le plan de "
        "tournage, pas le resultat : il ne dit pas ce qui est reellement a "
        "l'ecran.",
    ]
    return "\n".join(lignes)


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
    if checkpoint_id == "CP3":
        # Le fichier a valider passe avant le plan de tournage.
        morceaux.append(_resume_video_finale(video_dir, state))

    # Au CP3, le storyboard n'est plus qu'un rappel : c'est la video qui
    # porte la decision, et un plan de tournage de 3000 caracteres la
    # noierait comme il le faisait avant.
    budget = 1200 if checkpoint_id == "CP3" else 3000

    for nom_fichier, titre, prioritaires in RESUME_SOURCES.get(checkpoint_id, []):
        extrait = _lire_extrait(video_dir, nom_fichier, max_chars=budget,
                                sections_prioritaires=prioritaires)
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
    # Au-dela de `prete`, le statut appartient a E7 (§11) : le recalculer
    # ecrasait `publiee` par `prete` a chaque passage, CP3 etant valide.
    if state["statut_global"] in STATUTS_E7:
        return
    etapes = state["etapes"]
    if etapes["CP1"]["statut"] == "valide" and state["statut_global"] in ("idee", "sujet_valide"):
        state["statut_global"] = "en_production"
    if etapes.get("CP3", {}).get("statut") == "valide":
        state["statut_global"] = "prete"


def _mettre_a_jour_etape_actuelle(state):
    for etape_id in ORDRE_IDS:
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
    for etape_id in ORDRE_IDS:
        etape_def = PIPELINE_PAR_ID[etape_id]
        if etape_def["kind"] != "agent":
            continue
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

    # Une video publiee ou abandonnee est sortie du pipeline : la faire
    # avancer n'a plus de sens, et pour une video abandonnee en cours de
    # route, l'etape en attente serait proposee indefiniment au tableau de
    # bord.
    if state["statut_global"] in STATUTS_CLOS:
        return

    _transcrire_decisions_franco(video_dir, state)

    # ORDRE_IDS plutot que l'ordre d'insertion du dict : il existe pour ca,
    # et l'ordre du sequencement ne doit pas dependre d'un detail de Python.
    for etape_id in ORDRE_IDS:
        etape_def = PIPELINE_PAR_ID[etape_id]
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
