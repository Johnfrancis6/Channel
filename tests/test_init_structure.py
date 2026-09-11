import json
import os
import shutil
import tempfile
import unittest

from orchestrateur.init_structure import initialiser


class TestInitStructure(unittest.TestCase):
    def setUp(self):
        self.root = tempfile.mkdtemp(prefix="chaine_yt_init_")

    def tearDown(self):
        shutil.rmtree(self.root, ignore_errors=True)

    def test_cree_la_structure_et_les_brouillons_de_profil(self):
        resultat = initialiser(self.root)

        for relatif in ("00_Profil/profil_chaine.md", "00_Profil/conventions.md",
                         "00_Profil/lexique_prononciation.md",
                         "00_Profil/projets_franco.md",
                         "00_Profil/charte_visuelle/charte.md",
                         "00_Profil/charte_visuelle/charte.json",
                         "00_Profil/chaines_concurrentes.json",
                         "01_Orchestrateur/config.json",
                         "02_Veille_hebdo/backlog_sujets.json"):
            self.assertTrue(os.path.isfile(os.path.join(self.root, *relatif.split("/"))), relatif)
            self.assertIn(relatif, resultat["fichiers_crees"])

        with open(os.path.join(self.root, "00_Profil", "charte_visuelle", "charte.json"), encoding="utf-8") as f:
            charte = json.load(f)
        self.assertEqual(charte["statut"], "brouillon")

    def test_est_idempotent(self):
        initialiser(self.root)
        with open(os.path.join(self.root, "00_Profil", "profil_chaine.md"), "a", encoding="utf-8") as f:
            f.write("\n## Note ajoutee par Franco\n")

        resultat = initialiser(self.root)

        self.assertIn("00_Profil/profil_chaine.md", resultat["deja_present"])
        with open(os.path.join(self.root, "00_Profil", "profil_chaine.md"), encoding="utf-8") as f:
            contenu = f.read()
        self.assertIn("Note ajoutee par Franco", contenu)


if __name__ == "__main__":
    unittest.main()
