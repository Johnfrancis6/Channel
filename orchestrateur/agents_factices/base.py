"""
Agents factices : simulent A2/A4/A5/A6/A7 pour tester le squelette de
l'Orchestrateur avant que les vrais agents existent (§13, etape 1).

Chaque agent expose run(video_dir, state, etape_id) -> dict avec au moins
{"statut": "termine"|"echec", "sorties": [...], "message": str}.

Le scenario est pilote depuis state.json (jamais depuis du hasard, pour que
les tests soient reproductibles) :

  "_scenario": {
    "E1_recherche": "succes",
    "E3_filtre": "revision",   # renvoie E2_redaction en a_venir (boucle A4<->A5)
    ...
  }

Une etape non listee dans "_scenario" reussit par defaut.
"""


def scenario_pour(state, etape_id):
    return state.get("_scenario", {}).get(etape_id, "succes")


def resultat_succes(sorties, message):
    return {"statut": "termine", "sorties": sorties, "message": message, "action": None}


def resultat_echec(message, action=None):
    return {"statut": "echec", "sorties": [], "message": message, "action": action}
