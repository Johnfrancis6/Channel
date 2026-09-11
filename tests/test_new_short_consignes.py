"""
Teste les consignes structurees de new_short.py : format, reference video,
budget d'idees, et titre de travail raccourci.

Deux regressions d'origine, vues sur 2026-09-11_v01 :

1. `titre_travail` recopiait `sujet` sans limite. Le sujet faisait 148
   caracteres, et cette phrase entiere s'est propagee comme "titre" dans le
   registre, le tableau de bord et l'en-tete du storyboard.

2. Aucun champ ne portait le format narratif ni la video de reference.
   `--note` etant la seule porte d'entree libre, Franco y a mis toute sa
   direction de mise en scene. Elle n'a atteint le Designer que par ricochet,
   recopiee dans la recherche puis dans le script.
"""
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCRIPT = os.path.join(REPO_ROOT, "skills", "new-short", "scripts", "new_short.py")
sys.path.insert(0, os.path.join(REPO_ROOT, "skills", "new-short", "scripts"))

import new_short  # noqa: E402

SUJET_REEL = ("AI agents explained in 3 simple steps: LLM (passive) vs AI workflow "
              "(has tool access, still passive) vs AI agent (active, can act via other services)")


class TestRaccourcirTitre(unittest.TestCase):
    def test_le_sujet_reel_est_ramene_a_une_etiquette(self):
        titre = new_short.raccourcir_titre(SUJET_REEL)
        self.assertLessEqual(len(titre), new_short.TITRE_MAX + 1)  # +1 pour l'ellipse
        self.assertTrue(titre.endswith("…"))
        self.assertTrue(titre.startswith("AI agents explained"))

    def test_la_coupe_tombe_sur_un_mot_entier(self):
        titre = new_short.raccourcir_titre(SUJET_REEL)
        self.assertNotIn("  ", titre)
        # Pas de mot tronque : le dernier fragment avant l'ellipse est un mot complet.
        self.assertTrue(SUJET_REEL.startswith(titre[:-1]))

    def test_un_titre_court_passe_intact(self):
        self.assertEqual(new_short.raccourcir_titre("Un sujet court"), "Un sujet court")

    def test_les_espaces_sont_normalises(self):
        self.assertEqual(new_short.raccourcir_titre("Un  sujet\n  espace"), "Un sujet espace")

    def test_valeur_vide(self):
        self.assertIsNone(new_short.raccourcir_titre(None))


class TestConsignesStructurees(unittest.TestCase):
    def setUp(self):
        self.root = tempfile.mkdtemp(prefix="chaine_yt_consignes_")
        os.makedirs(os.path.join(self.root, "00_Profil"))
        os.makedirs(os.path.join(self.root, "videos"))

    def tearDown(self):
        shutil.rmtree(self.root, ignore_errors=True)

    def run_script(self, *args):
        proc = subprocess.run([sys.executable, SCRIPT, "--root", self.root, *args],
                              capture_output=True, text=True)
        return proc.returncode, json.loads(proc.stdout)

    def lire_state(self, video_id):
        with open(os.path.join(self.root, "videos", video_id, "state.json"), encoding="utf-8-sig") as f:
            return json.load(f)

    def test_format_reference_et_idees_sont_enregistres(self):
        code, out = self.run_script(
            "--sujet", "Comment fonctionne un agent",
            "--format", "interview_fictive",
            "--reference", "https://www.youtube.com/shorts/BF2k_fKuCVM",
            "--idees", "2")
        self.assertEqual(code, 0, out)
        consignes = self.lire_state(out["video_id"])["consignes"]
        self.assertEqual(consignes["format"], "interview_fictive")
        self.assertEqual(consignes["reference"], "https://www.youtube.com/shorts/BF2k_fKuCVM")
        self.assertEqual(consignes["idees_max"], 2)

    def test_le_format_reste_un_champ_libre(self):
        # Les formats se decouvrent au fil des premieres videos : aucun enum
        # ne doit refuser un nom que Franco essaie pour la premiere fois.
        code, out = self.run_script("--sujet", "Un test", "--format", "format_jamais_vu")
        self.assertEqual(code, 0, out)
        self.assertEqual(self.lire_state(out["video_id"])["consignes"]["format"], "format_jamais_vu")

    def test_budget_d_idees_par_defaut(self):
        code, out = self.run_script("--sujet", "Un sujet quelconque")
        self.assertEqual(code, 0, out)
        self.assertEqual(self.lire_state(out["video_id"])["consignes"]["idees_max"],
                         new_short.IDEES_MAX_DEFAUT)

    def test_idees_invalide_refuse(self):
        code, out = self.run_script("--sujet", "Un sujet", "--idees", "0")
        self.assertEqual(code, 2)

    def test_le_titre_de_travail_est_raccourci(self):
        code, out = self.run_script("--sujet", SUJET_REEL)
        self.assertEqual(code, 0, out)
        state = self.lire_state(out["video_id"])
        self.assertLessEqual(len(state["titre_travail"]), new_short.TITRE_MAX + 1)
        # Le sujet complet, lui, reste intact.
        self.assertEqual(state["sujet"], SUJET_REEL)

    def test_titre_explicite_prioritaire(self):
        code, out = self.run_script("--sujet", SUJET_REEL, "--titre", "LLM vs workflow vs agent")
        self.assertEqual(code, 0, out)
        self.assertEqual(self.lire_state(out["video_id"])["titre_travail"], "LLM vs workflow vs agent")

    def test_le_dossier_assets_est_cree(self):
        # Franco y depose ses references visuelles ; A6 s'en inspire pour
        # cadrer. Sans le dossier, il n'a pas d'endroit ou les mettre et la
        # reference repart dans une note en texte libre.
        code, out = self.run_script("--sujet", "Un sujet")
        self.assertEqual(code, 0, out)
        chemin = os.path.join(self.root, "videos", out["video_id"], "assets")
        self.assertTrue(os.path.isdir(chemin), f"{chemin} absent")
        self.assertIn(f"videos/{out['video_id']}/assets/", out["fichiers_crees"])

    def test_dry_run_ne_cree_pas_assets(self):
        code, out = self.run_script("--sujet", "Un sujet", "--dry-run")
        self.assertEqual(code, 0, out)
        self.assertEqual(out["fichiers_crees"], [])
        self.assertFalse(os.path.isdir(os.path.join(self.root, "videos", out["video_id"])))

    def test_note_franco_reste_disponible(self):
        code, out = self.run_script("--sujet", "Un sujet", "--note", "Garder le ton direct")
        self.assertEqual(code, 0, out)
        self.assertEqual(self.lire_state(out["video_id"])["consignes"]["note_franco"], "Garder le ton direct")

    def test_state_conforme_au_schema(self):
        code, out = self.run_script("--sujet", "Un sujet", "--format", "demo_outil", "--idees", "3")
        self.assertEqual(code, 0, out)
        with open(os.path.join(REPO_ROOT, "schemas", "state_schema.json"), encoding="utf-8-sig") as f:
            schema = json.load(f)
        props = schema["properties"]["consignes"]["properties"]
        for cle in ("mode_recherche", "note_franco", "format", "reference", "idees_max"):
            self.assertIn(cle, props, f"{cle} absent du schema")
        self.assertEqual(set(self.lire_state(out["video_id"])["consignes"]), set(props))


if __name__ == "__main__":
    unittest.main()
