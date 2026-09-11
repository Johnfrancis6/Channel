from .base import resultat_echec, resultat_succes, scenario_pour

AGENT_ID = "redacteur"


def run(video_dir, state, etape_id):
    scenario = scenario_pour(state, etape_id)
    if scenario == "echec":
        return resultat_echec("Agent factice : redaction simulee en echec.")
    return resultat_succes(["02_script_brut.md"], "Agent factice : script brut simule OK.")
