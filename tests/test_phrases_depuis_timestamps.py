"""
Teste outils/phrases_depuis_timestamps.py (§7.2).

Les mots horodates et leurs bornes viennent du **vrai** run de
2026-09-11_v01 (04_timestamps.json, Qwen3-TTS, WER 0.87 %) : le script
sert precisement a rattraper cette video, et une reconstruction se juge
sur les donnees qui l'ont motivee, pas sur des donnees inventees.
"""

import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCRIPT = os.path.join(REPO_ROOT, "outils", "phrases_depuis_timestamps.py")
sys.path.insert(0, os.path.join(REPO_ROOT, "outils"))
import phrases_depuis_timestamps as pdt  # noqa: E402

# Quatre premieres phrases de 03_script_tts.txt.
PHRASES = [
    "Everyone calls their product an AI agent now.",
    "Most of them are not agents at all.",
    "By the end of this video, you will know the real difference.",
    "LLM, AI workflow, AI agent, three very different things.",
]

# Les mots correspondants de 04_timestamps.json, bornes reelles.
MOTS = [
    ("everyone", 0.0, 0.44), ("calls", 0.44, 0.78), ("their", 0.78, 0.92),
    ("product", 0.92, 1.26), ("an", 1.26, 1.44), ("AI", 1.44, 1.66),
    ("agent", 1.66, 2.0), ("now.", 2.0, 2.3),
    ("Most", 2.74, 3.26), ("of", 3.26, 3.38), ("them", 3.38, 3.5),
    ("are", 3.5, 3.62), ("not", 3.62, 3.76), ("agents", 3.76, 4.1),
    ("at", 4.1, 4.28), ("all.", 4.28, 4.54),
    ("By", 5.02, 5.48), ("the", 5.48, 5.62), ("end", 5.62, 5.82),
    ("of", 5.82, 5.94), ("this", 5.94, 6.1), ("video,", 6.1, 6.4),
    ("you", 6.62, 6.66), ("will", 6.66, 6.8), ("know", 6.8, 6.98),
    ("the", 6.98, 7.14), ("real", 7.14, 7.38), ("difference.", 7.38, 7.88),
    ("LLM,", 8.88, 9.3), ("AI", 9.4, 9.6), ("workflow,", 9.6, 10.04),
    ("AI", 10.36, 10.6), ("agent,", 10.6, 11.0), ("three", 11.36, 11.58),
    ("very", 11.58, 11.94), ("different", 11.94, 12.24), ("things.", 12.24, 12.62),
]


def _mots(triplets=None):
    return [{"mot": m, "debut_s": d, "fin_s": f} for m, d, f in (triplets or MOTS)]


class TestReconstruction(unittest.TestCase):
    def test_les_bornes_reelles_sont_retrouvees(self):
        resultat, _ = pdt.reconstruire(PHRASES, _mots(), duree_totale=13.0)

        bornes = [(p["debut_s"], p["fin_s"]) for p in resultat["phrases"]]
        self.assertEqual(bornes, [(0.0, 2.3), (2.74, 4.54), (5.02, 7.88), (8.88, 12.62)])
        self.assertEqual(resultat["taux_alignement"], 1.0)
        self.assertEqual(resultat["duree_totale_s"], 13.0)

    def test_le_fichier_se_declare_reconstruit(self):
        # Il ne doit jamais passer pour des bornes exactes : le notebook les
        # connait, ce script les devine.
        resultat, _ = pdt.reconstruire(PHRASES, _mots())
        self.assertEqual(resultat["source"], "reconstruit")

    def test_une_contraction_ne_decale_pas_la_suite(self):
        # Cas reel : le script dit « Here is a real example », la
        # transcription « Here's a real example ». Un decoupage par nombre
        # de mots decalerait tout ce qui suit.
        phrases = ["Here is a real example, not a demo.", "Nobody is typing the commands."]
        mots = _mots([("Here's", 58.44, 59.0), ("a", 59.0, 59.08), ("real", 59.08, 59.28),
                      ("example,", 59.28, 59.74), ("not", 59.98, 60.34), ("a", 60.34, 60.44),
                      ("demo.", 60.44, 60.74),
                      ("Nobody", 70.28, 70.84), ("is", 70.84, 71.0), ("typing", 71.0, 71.28),
                      ("the", 71.28, 71.46), ("commands.", 71.46, 71.9)])
        resultat, _ = pdt.reconstruire(phrases, mots)

        p1, p2 = resultat["phrases"]
        self.assertEqual((p2["debut_s"], p2["fin_s"]), (70.28, 71.9))
        self.assertLessEqual(p1["fin_s"], p2["debut_s"])

    def test_les_bornes_ne_reculent_jamais(self):
        resultat, _ = pdt.reconstruire(PHRASES, _mots())
        precedent = 0.0
        for phrase in resultat["phrases"]:
            self.assertGreaterEqual(phrase["debut_s"], precedent)
            self.assertGreaterEqual(phrase["fin_s"], phrase["debut_s"])
            precedent = phrase["fin_s"]

    def test_une_phrase_non_prononcee_est_interpolee(self):
        # Une scene sans borne casserait le recalage : on l'intercale.
        phrases = PHRASES[:1] + ["Cette phrase n'a jamais ete prononcee."] + PHRASES[1:2]
        resultat, avertissements = pdt.reconstruire(phrases, _mots(MOTS[:16]))

        self.assertEqual(len(resultat["phrases"]), 3)
        self.assertTrue(any("interpolees" in a for a in avertissements))
        self.assertLess(resultat["taux_alignement"], 1.0)

    def test_sans_duree_donnee_la_queue_de_silence_est_signalee(self):
        resultat, avertissements = pdt.reconstruire(PHRASES, _mots())
        self.assertEqual(resultat["duree_totale_s"], 12.62)
        self.assertTrue(any("queue de silence" in a for a in avertissements))

    def test_script_ou_mots_vides(self):
        with self.assertRaises(ValueError):
            pdt.reconstruire([], _mots())
        with self.assertRaises(ValueError):
            pdt.reconstruire(PHRASES, [])


class TestCLI(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp(prefix="phrases_test_")
        self.timestamps = os.path.join(self.tmp, "04_timestamps.json")
        self.script = os.path.join(self.tmp, "03_script_tts.txt")
        self.sortie = os.path.join(self.tmp, "04_phrases.json")
        with open(self.timestamps, "w", encoding="utf-8") as f:
            json.dump(_mots(), f)
        with open(self.script, "w", encoding="utf-8") as f:
            f.write("\n".join(PHRASES) + "\n")

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def _run(self, *args):
        p = subprocess.run([sys.executable, SCRIPT, "--timestamps", self.timestamps,
                            "--script", self.script, "--sortie", self.sortie, *args],
                           capture_output=True, text=True)
        return p.returncode, json.loads(p.stdout)

    def test_ecrit_un_fichier_lisible_par_le_monteur(self):
        code, out = self._run()
        self.assertEqual(code, 0, out)

        with open(self.sortie, encoding="utf-8") as f:
            produit = json.load(f)
        # Les cles que construire_props.recaler_scenes exige.
        self.assertIn("duree_totale_s", produit)
        for phrase in produit["phrases"]:
            self.assertEqual(set(phrase) >= {"index", "texte", "debut_s", "fin_s"}, True)

    def _script_partiellement_faux(self):
        # Le cas dangereux n'est pas le script totalement etranger (il ne
        # s'aligne sur rien et le script s'arrete), mais celui qui ressemble
        # assez pour produire des bornes plausibles et fausses.
        with open(self.script, "w", encoding="utf-8") as f:
            f.write("\n".join([PHRASES[0],
                               "Quelque chose que personne n'a jamais prononce ici.",
                               "Encore une ligne totalement etrangere a cet enregistrement.",
                               "Et une troisieme pour faire bonne mesure."]) + "\n")

    def test_refuse_d_ecrire_un_alignement_trop_faible(self):
        # Des bornes fausses decaleraient tout le montage : mieux vaut rien.
        self._script_partiellement_faux()

        code, out = self._run()

        self.assertEqual(code, 4, out)
        self.assertFalse(os.path.exists(self.sortie))
        self.assertIn("Alignement trop faible", out["message"])

    def test_forcer_passe_outre(self):
        self._script_partiellement_faux()
        code, out = self._run("--forcer")
        self.assertEqual(code, 0, out)
        self.assertTrue(os.path.exists(self.sortie))

    def test_un_script_totalement_etranger_s_arrete(self):
        with open(self.script, "w", encoding="utf-8") as f:
            f.write("Zzzz qqqq wwww.\nXxxx yyyy vvvv.\n")
        code, out = self._run("--forcer")
        self.assertEqual(code, 2)
        self.assertFalse(os.path.exists(self.sortie))

    def test_fichier_introuvable(self):
        p = subprocess.run([sys.executable, SCRIPT, "--timestamps", "/pas/la.json",
                            "--script", self.script, "--sortie", self.sortie],
                           capture_output=True, text=True)
        self.assertEqual(p.returncode, 2)


if __name__ == "__main__":
    unittest.main()
