"""
Association agent_id -> module executant l'agent.

Pour l'etape 1 (Fondations), tous les agents sont factices. Les etapes
suivantes du §13 remplaceront ces entrees par les vrais agents (A2, A4...)
sans toucher au reste de l'Orchestrateur.
"""

from agents.factices import chercheur, designer, filtre_tts, monteur, redacteur

REGISTRE = {
    "chercheur": chercheur,
    "redacteur": redacteur,
    "filtre_tts": filtre_tts,
    "designer": designer,
    "monteur": monteur,
}


def obtenir_agent(agent_id):
    return REGISTRE[agent_id]
