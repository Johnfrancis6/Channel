from .base import resultat_echec, resultat_succes, scenario_pour

AGENT_ID = "filtre_tts"


def run(video_dir, state, etape_id):
    scenario = scenario_pour(state, etape_id)
    if scenario == "echec":
        return resultat_echec("Agent factice : filtre TTS simule en echec (metriques hors seuil).")
    if scenario == "revision":
        return resultat_echec(
            "Agent factice : style rejete, retour a la redaction.",
            action="revision_redaction",
        )
    return resultat_succes(
        ["03_script_final.md", "03_script_tts.txt", "03_rapport_metriques.md"],
        "Agent factice : filtre TTS simule OK.",
    )
