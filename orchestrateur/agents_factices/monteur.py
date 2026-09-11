import os

from .base import resultat_echec, resultat_succes, scenario_pour

AGENT_ID = "monteur"


def run(video_dir, state, etape_id):
    scenario = scenario_pour(state, etape_id)
    if scenario == "echec":
        return resultat_echec("Agent factice : montage simule en echec.")

    # Le CP3 (§4.2) lit 05_storyboard.md pour son resume : le cree si
    # l'agent factice designer (E5) ne l'a pas deja fait.
    storyboard_path = os.path.join(video_dir, "05_storyboard.md")
    if not os.path.isfile(storyboard_path):
        with open(storyboard_path, "w", encoding="utf-8") as f:
            f.write("# Storyboard (factice)\n\nGenere par l'agent factice monteur pour les tests.\n")

    with open(os.path.join(video_dir, "06_video_finale.mp4"), "wb") as f:
        f.write(b"\x00")

    return resultat_succes(["06_video_finale.mp4"], "Agent factice : montage simule OK.")
