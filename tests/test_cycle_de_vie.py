"""
Fermeture du cycle de vie d'une video (§5.3, §11) : ce que l'Orchestrateur
doit cesser de faire une fois que E7 a parle.

Le defaut corrige ici est le plus couteux du lot : `publier.py` ecrivait
`publiee`, puis le passage suivant de l'Orchestrateur — celui que le skill
demande de lancer juste apres, et que le cron relance tous les quarts
d'heure — reecrivait `prete`, parce que CP3 est valide. La publication
etait defaite par la commande censee la confirmer, et le tampon recomptait
comme disponible une video deja en ligne : exactement le bug que
`short-publier` avait ete ecrit pour corriger.
"""

import os
import shutil
import tempfile
import unittest

from orchestrateur.config import DEFAUTS
from orchestrateur.dashboard import rendre_dashboard
from orchestrateur.engine import traiter_video
from orchestrateur.main import run_once
from orchestrateur.state_store import load_state, save_state

from tests.test_orchestrateur_factice import _etat_de_base


def _etat_termine(video_id, statut_global):
    state = _etat_de_base(video_id)
    for etape_id, etape in state["etapes"].items():
        etape["statut"] = "valide" if etape_id.startswith("CP") else "termine"
    state["statut_global"] = statut_global
    state["etape_actuelle"] = "termine"
    return state


class TestStatutsDeE7(unittest.TestCase):
    def setUp(self):
        self.root = tempfile.mkdtemp(prefix="cycle_test_")
        os.makedirs(os.path.join(self.root, "01_Orchestrateur"))
        self.videos = os.path.join(self.root, "videos")
        os.makedirs(self.videos)

    def tearDown(self):
        shutil.rmtree(self.root, ignore_errors=True)

    def _creer(self, video_id, state):
        video_dir = os.path.join(self.videos, video_id)
        os.makedirs(video_dir, exist_ok=True)
        save_state(video_dir, state)
        return video_dir

    def test_une_video_publiee_ne_redevient_pas_prete(self):
        video_dir = self._creer("2026-09-11_v01", _etat_termine("2026-09-11_v01", "publiee"))
        run_once(self.root)
        self.assertEqual(load_state(video_dir)["statut_global"], "publiee")

    def test_une_video_programmee_ne_redevient_pas_prete(self):
        # Elle attend sa mise en ligne : la repasser a `prete` la remettrait
        # dans le tampon et ferait croire qu'il reste une video a publier.
        state = _etat_termine("2026-09-11_v02", "programmee")
        state["etapes"]["E7_publication"]["statut"] = "attente_franco"
        video_dir = self._creer("2026-09-11_v02", state)
        run_once(self.root)
        self.assertEqual(load_state(video_dir)["statut_global"], "programmee")

    def test_le_compteur_du_tableau_de_bord_voit_la_publication(self):
        # Le symptome visible : "Publiees : 0" alors que la video est en ligne.
        self._creer("2026-09-11_v01", _etat_termine("2026-09-11_v01", "publiee"))
        run_once(self.root)
        contenu = rendre_dashboard(self.root, DEFAUTS)
        self.assertIn("Publiees : 1", contenu)
        self.assertIn("Pretes : 0", contenu)

    def test_une_video_prete_reste_calculee_normalement(self):
        # Le garde-fou ne doit pas figer les statuts d'avant E7.
        state = _etat_termine("2026-09-11_v03", "en_production")
        video_dir = self._creer("2026-09-11_v03", state)
        run_once(self.root)
        self.assertEqual(load_state(video_dir)["statut_global"], "prete")


class TestVideoAbandonnee(unittest.TestCase):
    def setUp(self):
        self.root = tempfile.mkdtemp(prefix="cycle_abandon_")
        os.makedirs(os.path.join(self.root, "01_Orchestrateur"))
        self.videos = os.path.join(self.root, "videos")
        os.makedirs(self.videos)
        # Abandonnee en cours de route : CP1 valide, la redaction n'a jamais
        # commence. C'est le cas frequent — un sujet qu'on laisse tomber.
        state = _etat_de_base("2026-09-11_v04")
        state["etapes"]["E1_recherche"]["statut"] = "termine"
        state["etapes"]["CP1"]["statut"] = "valide"
        state["statut_global"] = "abandonnee"
        state["etape_actuelle"] = "termine"
        self.video_dir = os.path.join(self.videos, "2026-09-11_v04")
        os.makedirs(self.video_dir)
        save_state(self.video_dir, state)

    def tearDown(self):
        shutil.rmtree(self.root, ignore_errors=True)

    def test_l_orchestrateur_ne_la_fait_plus_avancer(self):
        state = load_state(self.video_dir)
        traiter_video(self.video_dir, state, {**DEFAUTS, "mode_agents": "factice"})
        self.assertEqual(state["statut_global"], "abandonnee")
        self.assertEqual(state["etapes"]["E2_redaction"]["statut"], "a_venir")
        self.assertEqual(state["etapes"]["E2_redaction"]["tentatives"], 0)

    def test_elle_ne_reclame_plus_d_agent_au_tableau_de_bord(self):
        # Sans ce filtre, la video abandonnee affiche « Lancer l'agent
        # redacteur » a chaque passage, pour toujours.
        run_once(self.root)
        contenu = rendre_dashboard(self.root, DEFAUTS)
        self.assertNotIn("redacteur", contenu)
        self.assertIn("Abandonnees : 1", contenu)


if __name__ == "__main__":
    unittest.main()
