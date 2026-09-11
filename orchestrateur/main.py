"""
Point d'entree de l'Orchestrateur (A1).

Ce qu'il fait a chaque execution (§4.3) : verrou, lecture des state.json,
transcription des decisions de Franco, avancement de chaque video, puis
regeneration du registre, du tableau de bord et de derniere_execution.json.

Le mode d'execution des agents vient de `mode_agents` dans config.json :
- "factice" : l'Orchestrateur execute lui-meme les agents simules
  (agents_factices/), pour les tests ;
- "reel" : les agents sont des skills Claude Code lances a la main ou en
  headless. L'Orchestrateur ne les execute pas ; il signale au tableau de
  bord l'etape prete, gere la boucle A4<->A5 et l'escalade en alerte.
  C'est ce que init_structure ecrit pour une vraie installation.

Reste a construire (§13) : la creation automatique de videos depuis le
backlog quand le tampon descend sous la cible (A1, point 5). Les taches
hebdomadaires (A3, H1, lot de sujets A2) ne sont pas executees ici non plus,
mais leur absence est signalee au tableau de bord (voir hebdo.py).

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
