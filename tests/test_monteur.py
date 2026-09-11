"""
Tests de l'agent A7 Monteur (§4.3, §8) : le script rendre_video.py (mode
--dry-run, sans dependre de Node/Remotion) et son integration E6 -> CP3
dans l'Orchestrateur.
"""

import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest

from orchestrateur.checkpoints import chemin_rapport
from orchestrateur.main import run_once
from orchestrateur.state_store import load_state, save_state

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCRIPT = os.path.join(REPO_ROOT, "agents", "short-monteur", "scripts", "rendre_video.py")
NODE_MODULES = os.path.join(REPO_ROOT, "composants", "node_modules")


def _executer(root, video_id, props_path, sortie_path):
    cmd = [sys.executable, SCRIPT, "--video", video_id, "--root", root,
           "--props", props_path, "--sortie", sortie_path, "--dry-run"]
    p = subprocess.run(cmd, capture_output=True, text=True)
    data = json.loads(p.stdout) if p.stdout.strip() else None
    return p.returncode, data


class TestRendreVideo(unittest.TestCase):
    def setUp(self):
        self.root = tempfile.mkdtemp(prefix="chaine_yt_monteur_")
        self.props_path = os.path.join(self.root, "props.json")
        self.sortie_path = os.path.join(self.root, "06_video_finale.mp4")
        with open(self.props_path, "w", encoding="utf-8") as f:
            json.dump({"charte": {}, "scenes": [], "mots": []}, f)
        self._node_modules_preexistant = os.path.isdir(NODE_MODULES)

    def tearDown(self):
        shutil.rmtree(self.root, ignore_errors=True)
        if not self._node_modules_preexistant and os.path.isdir(NODE_MODULES):
            shutil.rmtree(NODE_MODULES)

    def test_dry_run_ok_si_node_modules_present(self):
        os.makedirs(NODE_MODULES, exist_ok=True)
        code, data = _executer(self.root, "2026-09-11_v01", self.props_path, self.sortie_path)
        self.assertEqual(code, 0, data)
        self.assertTrue(data["ok"])
        self.assertTrue(data["dry_run"])

    def test_dry_run_exit4_si_node_modules_absent(self):
        if self._node_modules_preexistant:
            self.skipTest("composants/node_modules existe reellement (npm install fait) — "
                           "impossible de simuler son absence sans le supprimer.")
        code, data = _executer(self.root, "2026-09-11_v02", self.props_path, self.sortie_path)
        self.assertEqual(code, 4)
        self.assertFalse(data["ok"])

    def test_exit2_si_props_json_invalide(self):
        os.makedirs(NODE_MODULES, exist_ok=True)
        props_invalide = os.path.join(self.root, "props_invalide.json")
        with open(props_invalide, "w", encoding="utf-8") as f:
            f.write("ceci n'est pas du json")
        code, data = _executer(self.root, "2026-09-11_v03", props_invalide, self.sortie_path)
        self.assertEqual(code, 2)
        self.assertFalse(data["ok"])

    def test_exit2_si_props_absent(self):
        os.makedirs(NODE_MODULES, exist_ok=True)
        props_absent = os.path.join(self.root, "n_existe_pas.json")
        code, data = _executer(self.root, "2026-09-11_v04", props_absent, self.sortie_path)
        self.assertEqual(code, 2)
        self.assertFalse(data["ok"])


def _etape_agent(statut="a_venir"):
    return {"agent": None, "statut": statut, "tentatives": 0, "debut": None, "fin": None, "sorties": [], "message": None}


def _checkpoint(statut="a_venir"):
    return {"statut": statut, "commentaire": None, "date": None}


def _etat_e6(video_id, e4_statut, e5_statut, e6_statut="a_venir", cp2_statut="valide"):
    return {
        "video_id": video_id,
        "titre_travail": f"Titre de test {video_id}",
        "pilier": "actu_ia",
        "voie": "rapide",
        "statut_global": "en_production",
        "etape_actuelle": "E6_montage",
        "etapes": {
            "E1_recherche": _etape_agent("termine"),
            "CP1": _checkpoint("valide"),
            "E2_redaction": _etape_agent("termine"),
            "E3_filtre": _etape_agent("termine"),
            "CP2": _checkpoint(cp2_statut),
            "E4_audio": {**_etape_agent(e4_statut), "agent": None},
            "E5_storyboard": _etape_agent(e5_statut),
            "E6_montage": _etape_agent(e6_statut),
            "CP3": _checkpoint(),
            "E7_publication": _etape_agent(),
        },
        "publication": {"date_prevue": None, "date_effective": None, "url": None},
        "historique": [],
        "_scenario": {},
    }


class TestE6DansOrchestateur(unittest.TestCase):
    def setUp(self):
        self.root = tempfile.mkdtemp(prefix="chaine_yt_monteur_orch_")
        os.makedirs(os.path.join(self.root, "videos"), exist_ok=True)

    def tearDown(self):
        shutil.rmtree(self.root, ignore_errors=True)

    def _creer_video(self, video_id, e4_statut, e5_statut, e6_statut="a_venir", cp2_statut="valide"):
        video_dir = os.path.join(self.root, "videos", video_id)
        os.makedirs(os.path.join(video_dir, "checkpoints"), exist_ok=True)
        save_state(video_dir, _etat_e6(video_id, e4_statut, e5_statut, e6_statut, cp2_statut))
        return video_dir

    def test_e6_declenche_apres_e4_et_e5(self):
        video_dir = self._creer_video("2026-09-11_v05", e4_statut="termine", e5_statut="termine")

        run_once(self.root)
        state = load_state(video_dir)
        self.assertEqual(state["etapes"]["E6_montage"]["statut"], "termine")
        self.assertIn("06_video_finale.mp4", state["etapes"]["E6_montage"]["sorties"])

    def test_e6_bloque_si_e4_attente_franco(self):
        video_dir = self._creer_video("2026-09-11_v06", e4_statut="attente_franco", e5_statut="termine")

        run_once(self.root)
        state = load_state(video_dir)
        self.assertEqual(state["etapes"]["E6_montage"]["statut"], "a_venir")

    def test_e6_bloque_si_e5_absent(self):
        # CP2 pas encore valide : E5_storyboard (qui en depend) ne peut pas
        # etre auto-complete par l'agent factice pendant ce run_once, meme
        # si E4_audio est deja termine (simule directement pour le test).
        video_dir = self._creer_video("2026-09-11_v07", e4_statut="termine", e5_statut="a_venir",
                                       cp2_statut="a_venir")

        run_once(self.root)
        state = load_state(video_dir)
        self.assertNotEqual(state["etapes"]["E5_storyboard"]["statut"], "termine")
        self.assertEqual(state["etapes"]["E6_montage"]["statut"], "a_venir")

    def test_cp3_declenche_apres_e6(self):
        video_dir = self._creer_video("2026-09-11_v08", e4_statut="termine", e5_statut="termine")

        run_once(self.root)
        state = load_state(video_dir)
        self.assertEqual(state["etapes"]["E6_montage"]["statut"], "termine")
        self.assertEqual(state["etapes"]["CP3"]["statut"], "attente_validation")

        rapport_path = chemin_rapport(video_dir, "CP3")
        self.assertTrue(os.path.isfile(rapport_path))
        with open(rapport_path, encoding="utf-8") as f:
            contenu = f.read()
        self.assertIn("Storyboard", contenu)


if __name__ == "__main__":
    unittest.main()
