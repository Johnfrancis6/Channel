"""
Teste outils/lancer_orchestrateur.py (§12) : le lanceur cron de
l'Orchestrateur.

Le test central est celui de la racine non montee. `orchestrateur.main`
lance sur un dossier vide **sort 0 et ecrit** registre_videos.json,
TABLEAU_DE_BORD.md et 01_Orchestrateur/derniere_execution.json : cron ne
dirait rien, et le faux dossier masquerait le vrai Drive au remontage.
Le garde-fou doit passer avant toute ecriture.
"""

import os
import shutil
import subprocess
import sys
import tempfile
import unittest

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LANCEUR = os.path.join(REPO_ROOT, "outils", "lancer_orchestrateur.py")
sys.path.insert(0, os.path.join(REPO_ROOT, "outils"))
import lancer_orchestrateur  # noqa: E402

from orchestrateur.init_structure import initialiser  # noqa: E402
from orchestrateur.lock import acquerir_verrou  # noqa: E402


def _lancer(*args):
    return subprocess.run([sys.executable, LANCEUR, *args], capture_output=True, text=True)


class TestGardeFous(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp(prefix="cron_test_")

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_racine_absente_rien_ecrit(self):
        absent = os.path.join(self.tmp, "pas_la")
        p = _lancer("--root", absent)
        self.assertEqual(p.returncode, 2)
        self.assertIn("Drive non monte", p.stderr)
        self.assertFalse(os.path.exists(absent))

    def test_racine_vide_rien_ecrit(self):
        # Le point de montage existe mais le Drive n'est pas monte : c'est
        # le cas qui fabriquait une fausse racine locale.
        vide = os.path.join(self.tmp, "ChaineYouTube")
        os.makedirs(vide)
        p = _lancer("--root", vide)
        self.assertEqual(p.returncode, 2)
        self.assertIn("non initialisee", p.stderr)
        self.assertEqual(os.listdir(vide), [])

    def test_racine_initialisee_execute_et_journalise(self):
        racine = os.path.join(self.tmp, "ChaineYouTube")
        initialiser(racine)

        p = _lancer("--root", racine)
        self.assertEqual(p.returncode, 0, p.stderr)

        journal = os.path.join(racine, "01_Orchestrateur", "journal_cron.log")
        self.assertTrue(os.path.isfile(journal))
        with open(journal, encoding="utf-8") as f:
            lignes = f.read().splitlines()
        self.assertEqual(len(lignes), 1)
        self.assertIn("ok", lignes[0])
        self.assertTrue(os.path.isfile(os.path.join(racine, "TABLEAU_DE_BORD.md")))

    def test_un_verrou_actif_n_est_pas_une_erreur(self):
        # Deux executions qui se chevauchent sont le cas nominal d'un cron
        # serre. Sortir 1 enverrait un mail d'erreur a chaque passage.
        racine = os.path.join(self.tmp, "ChaineYouTube")
        initialiser(racine)
        acquerir_verrou(racine)

        p = _lancer("--root", racine)
        self.assertEqual(p.returncode, 0, p.stderr)
        self.assertEqual(p.stderr, "")
        with open(os.path.join(racine, "01_Orchestrateur", "journal_cron.log"),
                  encoding="utf-8") as f:
            self.assertIn("ignore", f.read())


class TestJournal(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp(prefix="cron_journal_")

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_le_journal_reste_borne(self):
        # Un passage tous les quarts d'heure sur un fichier synchronise par
        # le Drive : sans plafond, il grossit indefiniment.
        for i in range(lancer_orchestrateur.MAX_LIGNES_JOURNAL + 50):
            lancer_orchestrateur.journaliser(self.tmp, f"ligne {i}")

        with open(os.path.join(self.tmp, "01_Orchestrateur", "journal_cron.log"),
                  encoding="utf-8") as f:
            lignes = f.read().splitlines()
        self.assertEqual(len(lignes), lancer_orchestrateur.MAX_LIGNES_JOURNAL)
        # Ce sont les dernieres qui restent.
        self.assertEqual(lignes[-1], f"ligne {lancer_orchestrateur.MAX_LIGNES_JOURNAL + 49}")


class TestVerifier(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp(prefix="cron_verif_")

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_le_rapport_donne_une_ligne_de_crontab_utilisable(self):
        # Les chemins Drive contiennent une espace (« Mon Drive ») : la
        # ligne doit rester copiable telle quelle.
        racine = os.path.join(self.tmp, "Mon Drive", "ChaineYouTube")
        initialiser(racine)

        p = _lancer("--root", racine, "--verifier")
        self.assertEqual(p.returncode, 0, p.stderr)
        self.assertIn("*/15 * * * *", p.stdout)
        self.assertIn("orchestrateur_cmd", p.stdout)
        self.assertIn(f"'{racine}'", p.stdout)

    def test_le_rapport_signale_une_racine_inutilisable(self):
        p = _lancer("--root", os.path.join(self.tmp, "pas_la"), "--verifier")
        self.assertEqual(p.returncode, 2)
        self.assertIn("BLOQUANT", p.stdout)

    def test_verifier_n_ecrit_rien(self):
        racine = os.path.join(self.tmp, "ChaineYouTube")
        initialiser(racine)
        avant = sorted(os.listdir(os.path.join(racine, "01_Orchestrateur")))

        _lancer("--root", racine, "--verifier")

        self.assertEqual(sorted(os.listdir(os.path.join(racine, "01_Orchestrateur"))), avant)


if __name__ == "__main__":
    unittest.main()
