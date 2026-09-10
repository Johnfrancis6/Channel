"""
Teste agents/short-monteur/scripts/construire_props.py : assemblage des props
Remotion et normalisation de 04_timestamps.json quel que soit son format
(§13 etape 5).
"""

import json
import os
import subprocess
import sys
import tempfile
import unittest

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCRIPT = os.path.join(REPO_ROOT, "agents", "short-monteur", "scripts", "construire_props.py")
sys.path.insert(0, os.path.join(REPO_ROOT, "agents", "short-monteur", "scripts"))
import construire_props  # noqa: E402


class TestNormaliserMots(unittest.TestCase):
    def test_convention_faster_whisper(self):
        mots = construire_props.normaliser_mots([{"word": "hello", "start": 0.1, "end": 0.4}])
        self.assertEqual(mots, [{"mot": "hello", "debut_s": 0.1, "fin_s": 0.4}])

    def test_convention_francaise_enveloppee(self):
        mots = construire_props.normaliser_mots({"mots": [{"mot": "salut", "debut_s": 0, "fin_s": 0.3}]})
        self.assertEqual(mots, [{"mot": "salut", "debut_s": 0.0, "fin_s": 0.3}])

    def test_ignore_entrees_incompletes(self):
        mots = construire_props.normaliser_mots([{"word": "x"}, {"word": "y", "start": 0, "end": 1}])
        self.assertEqual(len(mots), 1)


class TestConstruire(unittest.TestCase):
    def test_leve_une_erreur_si_aucune_scene(self):
        with self.assertRaises(ValueError):
            construire_props.construire({}, {"scenes": []}, [])


class TestScriptCLI(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp(prefix="props_test_")

    def tearDown(self):
        import shutil
        shutil.rmtree(self.tmp, ignore_errors=True)

    def _ecrire(self, nom, data):
        chemin = os.path.join(self.tmp, nom)
        with open(chemin, "w", encoding="utf-8") as f:
            json.dump(data, f)
        return chemin

    def test_assemble_un_props_json_valide(self):
        charte = self._ecrire("charte.json", {"couleurs": {"fond": "#000"}})
        storyboard = self._ecrire("storyboard.json", {
            "scenes": [{"id": "s1", "composant": "TitleCard", "duree_s": 3, "params": {"texte": "Hi"}}]
        })
        timestamps = self._ecrire("timestamps.json", [{"word": "Hi", "start": 0, "end": 0.3}])
        sortie = os.path.join(self.tmp, "props.json")

        p = subprocess.run([sys.executable, SCRIPT, "--charte", charte, "--storyboard", storyboard,
                             "--timestamps", timestamps, "--sortie", sortie],
                            capture_output=True, text=True)
        self.assertEqual(p.returncode, 0, p.stderr)
        resultat = json.loads(p.stdout)
        self.assertTrue(resultat["ok"])
        self.assertEqual(resultat["nb_scenes"], 1)
        self.assertEqual(resultat["nb_mots"], 1)

        with open(sortie, encoding="utf-8") as f:
            props = json.load(f)
        self.assertEqual(props["scenes"][0]["composant"], "TitleCard")
        self.assertEqual(props["mots"][0]["mot"], "Hi")


if __name__ == "__main__":
    unittest.main()
