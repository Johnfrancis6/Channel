from .base import resultat_echec, resultat_succes, scenario_pour

AGENT_ID = "designer"


def run(video_dir, state, etape_id):
    scenario = scenario_pour(state, etape_id)
    if scenario == "echec":
        return resultat_echec("Agent factice : storyboard simule en echec.")
    return resultat_succes(["05_storyboard.md"], "Agent factice : storyboard simule OK.")
