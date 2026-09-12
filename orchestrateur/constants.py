MAX_TENTATIVES_DEFAUT = 3

# Statuts globaux qui appartiennent a E7 (§5.3, §11) : une fois la
# publication enregistree, l'Orchestrateur ne les recalcule plus. Sans cette
# regle il reecrivait `publiee` en `prete` des le passage suivant, parce que
# CP3 est valide — la publication etait defaite par la commande que le skill
# demande de lancer juste apres, puis par le cron toutes les 15 minutes.
STATUTS_E7 = {"programmee", "publiee", "abandonnee"}

# Cycle de vie clos : plus rien a faire avancer, et plus rien a signaler au
# tableau de bord. `programmee` n'en fait pas partie — la video attend encore
# sa mise en ligne.
STATUTS_CLOS = {"publiee", "abandonnee"}

# Sequencement du pipeline (§6.2). E4_audio et E5_storyboard tournent en parallele
# apres CP2 ; E6_montage attend que les deux soient "termine".
PIPELINE = [
    {"id": "E1_recherche", "kind": "agent", "agent": "chercheur"},
    {"id": "CP1", "kind": "checkpoint"},
    {"id": "E2_redaction", "kind": "agent", "agent": "redacteur"},
    {"id": "E3_filtre", "kind": "agent", "agent": "filtre_tts"},
    {"id": "CP2", "kind": "checkpoint"},
    {"id": "E4_audio", "kind": "attente_franco"},
    # `depend_de` explicite la ou l'ordre de la liste ne suffit pas : E5 ne
    # depend pas de E4 (les deux partent du CP2, en parallele), et E6 attend
    # les deux. Partout ailleurs, une etape depend de celle qui la precede.
    {"id": "E5_storyboard", "kind": "agent", "agent": "designer", "depend_de": ["CP2"]},
    {"id": "E6_montage", "kind": "agent", "agent": "monteur", "depend_de": ["E4_audio", "E5_storyboard"]},
    {"id": "CP3", "kind": "checkpoint"},
    {"id": "E7_publication", "kind": "manuel"},
]

PIPELINE_PAR_ID = {etape["id"]: etape for etape in PIPELINE}
ORDRE_IDS = [etape["id"] for etape in PIPELINE]


def _construire_dependances():
    """
    {etape: [prealables]}, derive de PIPELINE.

    Il existait un second dictionnaire, ecrit a la main dans engine.py, et
    `depend_de` n'etait lu par personne : deux sources pour un meme graphe,
    dont une morte. Elles concordaient, rien ne l'imposait. C'est le meme
    motif que la geometrie des composants — deux constantes liees qui vivent
    separement — et il se regle de la meme facon : on en derive une.
    """
    dependances = {}
    for position, etape in enumerate(PIPELINE):
        if "depend_de" in etape:
            dependances[etape["id"]] = list(etape["depend_de"])
        elif position == 0:
            dependances[etape["id"]] = []
        else:
            dependances[etape["id"]] = [PIPELINE[position - 1]["id"]]
    return dependances


DEPENDANCES = _construire_dependances()
