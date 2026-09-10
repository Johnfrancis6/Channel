"""
Verifie le mode "reel" (§13 etape 3) : l'Orchestrateur n'execute plus
lui-meme les agents, il se contente de signaler au tableau de bord quelle
etape est prete, et gere l'escalade en alerte a 3 echecs.
"""

import os
import shutil
import tempfile
import unittest

from orchestrateur.dashboard import ecrire_dashboard
from orchestrateur.config import charger_config
from orchestrateur.init_structure import initialiser
from orchestrateur.main import run_once
from orchestrateur.state_store import load_state, save_state


def _creer_video_minimale(video_dir, video_id):
    os.makedirs(os.path.join(video_dir, "checkpoints"), exist_ok=True)
    save_state(video_dir, {
        "version_schema": 1, "video_id": video_id, "cree_le": "2026-09-10T00:00:00Z",
        "cree_par": "test", "titre_travail": "Titre test", "sujet": "Sujet test",
        "angle": None, "sujet_id": None, "pilier": "actu_ia", "voie": "rapide",
        "consignes": {"mode_recherche": "sujet_impose", "note_franco": None},
        "statut_global": "idee", "etape_actuelle": "E1_recherche",
        "etapes": {
            "E1_recherche": {"agent": "chercheur", "statut": "a_venir", "tentatives": 0, "debut": None, "fin": None, "sorties": []},
            "CP1": {"statut": "a_venir", "commentaire": None, "date": None},
            "E2_redaction": {"agent": "redacteur", "statut": "a_venir", "tentatives": 0, "debut": None, "fin": None, "sorties": []},
            "E3_filtre": {"agent": "filtre_tts", "statut": "a_venir", "tentatives": 0, "debut": None, "fin": None, "sorties": []},
            "CP2": {"statut": "a_venir", "commentaire": None, "date": None},
            "E4_audio": {"agent": "colab_voix", "statut": "a_venir", "tentatives": 0, "debut": None, "fin": None, "sorties": []},
            "E5_storyboard": {"agent": "designer", "statut": "a_venir", "tentatives": 0, "debut": None, "fin": None, "sorties": []},
            "E6_montage": {"agent": "monteur", "statut": "a_venir", "tentatives": 0, "debut": None, "fin": None, "sorties": []},
            "CP3": {"statut": "a_venir", "commentaire": None, "date": None, "seo": {"titre": None, "description": None, "tags": []}},
            "E7_publication": {"agent": "publication", "statut": "a_venir", "tentatives": 0, "debut": None, "fin": None, "sorties": []},
        },
        "publication": {"date_prevue": None, "date_effective": None, "url": None},
        "historique": [],
    })


class TestModeAgentsReel(unittest.TestCase):
    def setUp(self):
        self.root = tempfile.mkdtemp(prefix="chaine_yt_reel_")
        initialiser(self.root)  # ecrit un config.json avec mode_agents="reel"
        self.video_id = "2026-09-10_v01"
        self.video_dir = os.path.join(self.root, "videos", self.video_id)
        _creer_video_minimale(self.video_dir, self.video_id)

    def tearDown(self):
        shutil.rmtree(self.root, ignore_errors=True)

    def test_ne_lance_pas_l_agent_et_le_signale_au_tableau_de_bord(self):
        self.assertEqual(charger_config(self.root)["mode_agents"], "reel")

        run_once(self.root)

        state = load_state(self.video_dir)
        self.assertEqual(state["etapes"]["E1_recherche"]["statut"], "a_venir")
        self.assertEqual(state["etapes"]["CP1"]["statut"], "a_venir")

        with open(os.path.join(self.root, "TABLEAU_DE_BORD.md"), encoding="utf-8") as f:
            contenu = f.read()
        self.assertIn("[AGENT]", contenu)
        self.assertIn("chercheur", contenu)

    def test_echec_repete_de_l_agent_reel_declenche_une_alerte(self):
        state = load_state(self.video_dir)
        state["etapes"]["E1_recherche"].update({"statut": "echec", "tentatives": 3})
        save_state(self.video_dir, state)

        run_once(self.root)

        state = load_state(self.video_dir)
        self.assertEqual(state["etapes"]["E1_recherche"]["statut"], "alerte")


if __name__ == "__main__":
    unittest.main()
