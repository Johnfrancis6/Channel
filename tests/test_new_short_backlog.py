"""
Tests de new_short.py sur la regle la plus importante du §2 : le systeme ne
choisit jamais le sujet final d'une video sans l'accord de Franco.

new_short pre-valide le CP1 (`statut: valide`) pour les sujets venant du
backlog, au motif qu'ils ont ete valides en lot au CP1 groupe. Rien ne le
verifiait : toute entree portant un `sujet_id` etait traitee comme validee,
donc une proposition pas encore soumise a Franco suffisait a lancer une
video avec son CP1 deja franchi.

Lancer : python3 -m pytest tests/test_new_short_backlog.py -v
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


class TestBacklogValidation(unittest.TestCase):
    def setUp(self):
        self.root = tempfile.mkdtemp(prefix="chaine_yt_newshort_")
        os.makedirs(os.path.join(self.root, "videos"), exist_ok=True)
        os.makedirs(os.path.join(self.root, "02_Veille_hebdo"), exist_ok=True)
        os.makedirs(os.path.join(self.root, "00_Profil"), exist_ok=True)

    def tearDown(self):
        shutil.rmtree(self.root, ignore_errors=True)

    def _ecrire_backlog(self, sujets):
        with open(os.path.join(self.root, "02_Veille_hebdo", "backlog_sujets.json"),
                  "w", encoding="utf-8") as f:
            json.dump({"sujets": sujets}, f, ensure_ascii=False)

    def _lancer(self, *args):
        p = subprocess.run([sys.executable, SCRIPT, "--root", self.root, *args],
                           capture_output=True, text=True)
        return p.returncode, json.loads(p.stdout) if p.stdout.strip() else None

    VALIDE = {"sujet_id": "2026-S37-01", "sujet": "How RAG actually works",
              "angle": "test reel", "pilier": "concept", "semaine": "2026-S37",
              "valide_le": "2026-09-08T10:00:00Z"}
    NON_VALIDE = {"sujet_id": "2026-S37-99", "sujet": "Proposition pas encore soumise",
                  "pilier": "concept", "semaine": "2026-S37"}

    def test_un_sujet_valide_en_lot_prevalide_le_cp1(self):
        self._ecrire_backlog([self.VALIDE])
        code, out = self._lancer()
        self.assertEqual(code, 0, out)
        self.assertEqual(out["cp1"], "valide")
        self.assertEqual(out["sujet_id"], "2026-S37-01")

        state = json.load(open(os.path.join(self.root, "videos", out["video_id"], "state.json"),
                               encoding="utf-8"))
        self.assertEqual(state["etapes"]["CP1"]["statut"], "valide")
        self.assertEqual(state["statut_global"], "sujet_valide")

    def test_un_sujet_sans_valide_le_n_est_jamais_choisi_tout_seul(self):
        """Sans `valide_le`, le sujet n'a pas passe le CP1 groupe : il ne doit
        pas servir de source au mode "new short" sans precision."""
        self._ecrire_backlog([self.NON_VALIDE])
        code, out = self._lancer()
        self.assertEqual(code, 3, out)          # backlog vide, pas "video creee"
        self.assertEqual(out["sujets_non_valides"], ["2026-S37-99"])
        self.assertEqual(os.listdir(os.path.join(self.root, "videos")), [])

    def test_sujet_id_non_valide_refuse_explicitement(self):
        self._ecrire_backlog([self.NON_VALIDE])
        code, out = self._lancer("--sujet-id", "2026-S37-99")
        self.assertEqual(code, 5, out)
        self.assertIn("valide_le", out["message"])
        self.assertEqual(os.listdir(os.path.join(self.root, "videos")), [])

    def test_force_ne_contourne_pas_la_validation_du_sujet(self):
        """--force sert a passer outre un doublon, jamais l'accord de Franco."""
        self._ecrire_backlog([self.NON_VALIDE])
        code, _ = self._lancer("--sujet-id", "2026-S37-99", "--force")
        self.assertEqual(code, 5)
        self.assertEqual(os.listdir(os.path.join(self.root, "videos")), [])

    def test_le_sujet_valide_est_choisi_malgre_un_non_valide_plus_ancien(self):
        self._ecrire_backlog([self.NON_VALIDE, self.VALIDE])
        code, out = self._lancer()
        self.assertEqual(code, 0, out)
        self.assertEqual(out["sujet_id"], "2026-S37-01")

    def test_sujet_donne_par_franco_reste_en_cp1_individuel(self):
        """Voie "new short sur X" : Franco donne le sujet, mais l'angle passe
        quand meme par un CP1 individuel (§14)."""
        self._ecrire_backlog([])
        code, out = self._lancer("--sujet", "Why vLLM is fast", "--pilier", "concept")
        self.assertEqual(code, 0, out)
        self.assertEqual(out["cp1"], "a_venir")

        state = json.load(open(os.path.join(self.root, "videos", out["video_id"], "state.json"),
                               encoding="utf-8"))
        self.assertEqual(state["statut_global"], "idee")
        self.assertEqual(state["consignes"]["mode_recherche"], "sujet_impose")

    def test_veille_actu_ne_choisit_aucun_sujet(self):
        self._ecrire_backlog([])
        code, out = self._lancer("--voie", "rapide")
        self.assertEqual(code, 0, out)
        self.assertIsNone(out["sujet"])
        self.assertEqual(out["cp1"], "a_venir")
        self.assertEqual(out["mode_recherche"], "veille_actu")


if __name__ == "__main__":
    unittest.main()
