"""
Teste agents/short-amelioration/scripts/rassembler_inputs.py (§4.3, H1) :
il doit lister les fichiers pertinents recents sans faire d'analyse.
"""

import os
import shutil
import sys
import tempfile
import time
import unittest

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(REPO_ROOT, "agents", "short-amelioration", "scripts"))
import rassembler_inputs  # noqa: E402


class TestRassemblerInputs(unittest.TestCase):
    def setUp(self):
        self.root = tempfile.mkdtemp(prefix="h1_test_")

    def tearDown(self):
        shutil.rmtree(self.root, ignore_errors=True)

    def _creer(self, relatif, ancien=False):
        chemin = os.path.join(self.root, *relatif.split("/"))
        os.makedirs(os.path.dirname(chemin), exist_ok=True)
        with open(chemin, "w", encoding="utf-8") as f:
            f.write("contenu")
        if ancien:
            vieux = time.time() - 30 * 86400
            os.utime(chemin, (vieux, vieux))

    def test_liste_les_fichiers_recents_et_ignore_les_anciens(self):
        self._creer("videos/2026-09-10_v01/checkpoints/rapport_CP1.md")
        self._creer("videos/2026-09-10_v01/03_rapport_metriques.md")
        self._creer("videos/2026-09-10_v01/04_rapport_audio.md")
        self._creer("videos/2026-08-01_v01/checkpoints/rapport_CP1.md", ancien=True)
        self._creer("03_Amelioration/analytics/export.csv")

        resultat = rassembler_inputs.rassembler(self.root, jours=7)

        self.assertEqual(len(resultat["checkpoints"]), 1)
        self.assertIn("2026-09-10_v01", resultat["checkpoints"][0])
        self.assertEqual(len(resultat["metriques_filtre"]), 1)
        self.assertEqual(len(resultat["rapports_audio"]), 1)
        self.assertEqual(len(resultat["analytics_csv"]), 1)

    def test_racine_vide_ne_plante_pas(self):
        resultat = rassembler_inputs.rassembler(self.root, jours=7)
        self.assertEqual(resultat, {"checkpoints": [], "metriques_filtre": [], "rapports_audio": [], "analytics_csv": []})


if __name__ == "__main__":
    unittest.main()
