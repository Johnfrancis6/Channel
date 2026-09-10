from .base import resultat_echec, resultat_succes, scenario_pour

AGENT_ID = "chercheur"


def run(video_dir, state, etape_id):
    scenario = scenario_pour(state, etape_id)
    if scenario == "echec":
        return resultat_echec("Agent factice : recherche simulee en echec.")
    return resultat_succes(["01_recherche.md"], "Agent factice : recherche simulee OK.")
