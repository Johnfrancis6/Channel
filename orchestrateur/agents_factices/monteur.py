from .base import resultat_echec, resultat_succes, scenario_pour

AGENT_ID = "monteur"


def run(video_dir, state, etape_id):
    scenario = scenario_pour(state, etape_id)
    if scenario == "echec":
        return resultat_echec("Agent factice : montage simule en echec.")
    return resultat_succes(["06_video_finale.mp4"], "Agent factice : montage simule OK.")
