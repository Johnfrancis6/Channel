"""
Tests de la detection d'etape bloquee au tableau de bord.

En mode `reel` — celui qu'ecrit init_structure pour une vraie installation —
les agents sont des skills Claude Code lances a la main. Un agent qui plante
ou qu'on interrompt apres `etape.py commencer` laisse son etape a `en_cours`
pour toujours : etapes_agent_actionnables() ignore `en_cours`, donc rien ne
proposait de la relancer et rien ne la signalait. short-state le detectait
deja (action BLOQUE) mais pas TABLEAU_DE_BORD.md, qui est pourtant "la
premiere chose que Franco ouvre" (§10).

Lancer : python3 -m pytest tests/test_dashboard_blocage.py -v
"""

import os
import shutil
import tempfile
import unittest
from datetime import datetime, timedelta, timezone

from orchestrateur.config import charger_config
from orchestrateur.dashboard import rendre_dashboard
from orchestrateur.state_store import save_state

from tests.test_orchestrateur_factice import _etat_de_base


def _il_y_a(heures):
    return (datetime.now(timezone.utc) - timedelta(hours=heures)).strftime("%Y-%m-%dT%H:%M:%SZ")


class TestBlocageTableauDeBord(unittest.TestCase):
    def setUp(self):
        self.root = tempfile.mkdtemp(prefix="chaine_yt_blocage_")
        os.makedirs(os.path.join(self.root, "videos"), exist_ok=True)

    def tearDown(self):
        shutil.rmtree(self.root, ignore_errors=True)

    def _video_en_cours(self, video_id, depuis_heures):
        video_dir = os.path.join(self.root, "videos", video_id)
        os.makedirs(os.path.join(video_dir, "checkpoints"), exist_ok=True)
        state = _etat_de_base(video_id)
        state["etapes"]["E1_recherche"].update(
            statut="en_cours", tentatives=1, debut=_il_y_a(depuis_heures), agent="chercheur")
        save_state(video_dir, state)
        return video_dir

    def _tableau(self):
        return rendre_dashboard(self.root, charger_config(self.root))

    def test_etape_en_cours_depuis_trop_longtemps_est_signalee(self):
        self._video_en_cours("2026-09-10_v01", depuis_heures=5)  # seuil par defaut : 2 h
        tableau = self._tableau()
        self.assertIn("[BLOQUE]", tableau)
        self.assertIn("2026-09-10_v01", tableau)
        self.assertIn("E1_recherche", tableau)

    def test_etape_en_cours_recente_n_est_pas_signalee(self):
        """Un agent qui travaille normalement ne doit pas polluer la liste."""
        self._video_en_cours("2026-09-10_v02", depuis_heures=0.2)
        self.assertNotIn("[BLOQUE]", self._tableau())

    def test_le_seuil_vient_de_la_config(self):
        import json
        os.makedirs(os.path.join(self.root, "01_Orchestrateur"), exist_ok=True)
        with open(os.path.join(self.root, "01_Orchestrateur", "config.json"),
                  "w", encoding="utf-8") as f:
            json.dump({"seuil_blocage_heures": 12}, f)

        self._video_en_cours("2026-09-10_v03", depuis_heures=5)
        self.assertNotIn("[BLOQUE]", self._tableau())

    def test_debut_absent_ou_illisible_ne_fait_pas_planter(self):
        video_dir = os.path.join(self.root, "videos", "2026-09-10_v04")
        os.makedirs(os.path.join(video_dir, "checkpoints"), exist_ok=True)
        state = _etat_de_base("2026-09-10_v04")
        state["etapes"]["E1_recherche"].update(statut="en_cours", debut="pas une date")
        save_state(video_dir, state)

        tableau = self._tableau()  # ne doit pas lever
        self.assertNotIn("[BLOQUE]", tableau)


if __name__ == "__main__":
    unittest.main()
