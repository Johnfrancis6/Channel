import os
import shutil
import tempfile
import unittest
from datetime import datetime, timezone

from orchestrateur.hebdo import semaine_iso, taches_hebdo_manquantes


class TestHebdo(unittest.TestCase):
    def setUp(self):
        self.root = tempfile.mkdtemp(prefix="hebdo_test_")

    def tearDown(self):
        shutil.rmtree(self.root, ignore_errors=True)

    def test_semaine_iso_format(self):
        d = datetime(2026, 9, 10, tzinfo=timezone.utc)
        self.assertEqual(semaine_iso(d), "2026-S37")

    def test_toutes_les_taches_manquantes_par_defaut(self):
        d = datetime(2026, 9, 10, tzinfo=timezone.utc)
        semaine, manquantes = taches_hebdo_manquantes(self.root, d)
        self.assertEqual(semaine, "2026-S37")
        self.assertEqual(len(manquantes), 3)

    def test_tache_disparait_une_fois_le_fichier_present(self):
        d = datetime(2026, 9, 10, tzinfo=timezone.utc)
        os.makedirs(os.path.join(self.root, "02_Veille_hebdo"), exist_ok=True)
        with open(os.path.join(self.root, "02_Veille_hebdo", "2026-S37_analyse_concurrentielle.md"), "w") as f:
            f.write("ok")

        _, manquantes = taches_hebdo_manquantes(self.root, d)
        taches = [m["tache"] for m in manquantes]
        self.assertNotIn("A3 (analyseur_chaines)", taches)
        self.assertEqual(len(manquantes), 2)


if __name__ == "__main__":
    unittest.main()
