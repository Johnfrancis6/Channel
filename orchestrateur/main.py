"""
Point d'entree de l'Orchestrateur (A1). Squelette etape 1 (§13) : agents
factices, pas encore de declenchement hebdomadaire (A3/H1) ni de creation
automatique de videos depuis le backlog (a construire aux etapes suivantes).

Usage : python -m orchestrateur.main --root /chemin/vers/ChaineYouTube
"""

import argparse
import sys

from .config import charger_config
from .dashboard import ecrire_dashboard, ecrire_derniere_execution, ecrire_registre, construire_registre
from .engine import traiter_video
from .lock import VerrouActifError, acquerir_verrou, liberer_verrou
from .state_store import list_video_dirs, load_state, save_state


def run_once(root):
    acquerir_verrou(root)
    try:
        config = charger_config(root)
        for video_dir in list_video_dirs(root):
            state = load_state(video_dir)
            traiter_video(video_dir, state, config)
            save_state(video_dir, state)

        ecrire_registre(root, construire_registre(root))
        ecrire_dashboard(root, config)
        ecrire_derniere_execution(root)
    finally:
        liberer_verrou(root)


def main(argv=None):
    parser = argparse.ArgumentParser(description="Orchestrateur de la chaine YouTube (squelette, etape 1).")
    parser.add_argument("--root", required=True, help="Racine du dossier ChaineYouTube.")
    args = parser.parse_args(argv)

    try:
        run_once(args.root)
    except VerrouActifError as e:
        print(f"Execution ignoree : {e}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
