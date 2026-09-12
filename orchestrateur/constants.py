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
    {"id": "E5_storyboard", "kind": "agent", "agent": "designer"},
    {"id": "E6_montage", "kind": "agent", "agent": "monteur", "depend_de": ["E4_audio", "E5_storyboard"]},
    {"id": "CP3", "kind": "checkpoint"},
    {"id": "E7_publication", "kind": "manuel"},
]

PIPELINE_PAR_ID = {etape["id"]: etape for etape in PIPELINE}
ORDRE_IDS = [etape["id"] for etape in PIPELINE]
