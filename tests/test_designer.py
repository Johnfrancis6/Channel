"""
Tests de l'agent A6 Designer (§4.3, §8) : le script deterministe
generer_storyboard.py (E5_storyboard) et son integration dans
l'Orchestrateur (agent factice + sequencement E4/E5 -> E6).
"""

import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest

from orchestrateur.main import run_once
from orchestrateur.state_store import load_state, save_state

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCRIPT = os.path.join(REPO_ROOT, "agents", "short-designer", "scripts", "generer_storyboard.py")


def _executer(root, video_id):
    cmd = [
        sys.executable, SCRIPT,
        "--video", video_id,
        "--root", root,
        "--sortie-md", os.path.join("videos", video_id, "05_storyboard.md"),
        "--sortie-json", os.path.join("videos", video_id, "05_storyboard.json"),
    ]
    p = subprocess.run(cmd, capture_output=True, text=True)
    data = json.loads(p.stdout) if p.stdout.strip() else None
    return p.returncode, data


def _creer_script_tts(root, video_id, phrases):
    dossier = os.path.join(root, "videos", video_id)
    os.makedirs(dossier, exist_ok=True)
    with open(os.path.join(dossier, "03_script_tts.txt"), "w", encoding="utf-8") as f:
        f.write("\n".join(phrases) + "\n")
    return dossier


class TestGenererStoryboard(unittest.TestCase):
    def setUp(self):
        self.root = tempfile.mkdtemp(prefix="chaine_yt_designer_")

    def tearDown(self):
        shutil.rmtree(self.root, ignore_errors=True)

    def test_genere_depuis_script_valide(self):
        video_id = "2026-09-11_v01"
        _creer_script_tts(self.root, video_id, [
            "Voici comment fonctionne le RAG.",
            "Il combine recherche et generation.",
            "Cela ameliore la fraicheur des reponses.",
        ])

        code, data = _executer(self.root, video_id)
        self.assertEqual(code, 0)
        self.assertTrue(data["ok"])
        self.assertEqual(data["nb_scenes"], 3)

        chemin_json = os.path.join(self.root, "videos", video_id, "05_storyboard.json")
        with open(chemin_json, encoding="utf-8") as f:
            storyboard = json.load(f)
        self.assertEqual(len(storyboard["scenes"]), 3)
        for scene in storyboard["scenes"]:
            self.assertIn("id", scene)
            self.assertIn("composant", scene)
            self.assertGreater(scene["duree_s"], 0)
            self.assertIn("params", scene)

        chemin_md = os.path.join(self.root, "videos", video_id, "05_storyboard.md")
        with open(chemin_md, encoding="utf-8") as f:
            contenu_md = f.read()
        self.assertIn("Voici comment fonctionne le RAG.", contenu_md)
        self.assertIn("Il combine recherche et generation.", contenu_md)
        self.assertIn("Cela ameliore la fraicheur des reponses.", contenu_md)

    def test_duree_calculee_correctement(self):
        video_id = "2026-09-11_v02"
        # 10 mots -> 10/2.5 = 4.0s ; 5 mots -> 5/2.5 = 2.0s
        _creer_script_tts(self.root, video_id, [
            "un deux trois quatre cinq six sept huit neuf dix",
            "un deux trois quatre cinq",
        ])

        code, data = _executer(self.root, video_id)
        self.assertEqual(code, 0)

        chemin_json = os.path.join(self.root, "videos", video_id, "05_storyboard.json")
        with open(chemin_json, encoding="utf-8") as f:
            storyboard = json.load(f)
        self.assertEqual(storyboard["scenes"][0]["duree_s"], 4.0)
        self.assertEqual(storyboard["scenes"][1]["duree_s"], 2.0)

    def test_script_absent_exit_2(self):
        video_id = "2026-09-11_v03"
        os.makedirs(os.path.join(self.root, "videos", video_id), exist_ok=True)

        code, data = _executer(self.root, video_id)
        self.assertEqual(code, 2)
        self.assertFalse(data["ok"])

    def test_script_vide_exit_3(self):
        video_id = "2026-09-11_v04"
        _creer_script_tts(self.root, video_id, [])

        code, data = _executer(self.root, video_id)
        self.assertEqual(code, 3)
        self.assertFalse(data["ok"])

    def test_coherence_md_json(self):
        video_id = "2026-09-11_v05"
        phrases = ["Premiere phrase du script.", "Deuxieme phrase du script.",
                   "Troisieme phrase du script.", "Quatrieme phrase du script."]
        _creer_script_tts(self.root, video_id, phrases)

        code, data = _executer(self.root, video_id)
        self.assertEqual(code, 0)

        chemin_json = os.path.join(self.root, "videos", video_id, "05_storyboard.json")
        chemin_md = os.path.join(self.root, "videos", video_id, "05_storyboard.md")
        with open(chemin_json, encoding="utf-8") as f:
            storyboard = json.load(f)
        with open(chemin_md, encoding="utf-8") as f:
            contenu_md = f.read()

        self.assertEqual(len(storyboard["scenes"]), len(phrases))
        for phrase in phrases:
            self.assertIn(phrase, contenu_md)


def _etape_agent(statut="a_venir"):
    return {"agent": None, "statut": statut, "tentatives": 0, "debut": None, "fin": None, "sorties": [], "message": None}


def _checkpoint(statut="a_venir"):
    return {"statut": statut, "commentaire": None, "date": None}


def _etat_apres_cp2(video_id, e4_statut):
    return {
        "video_id": video_id,
        "titre_travail": f"Titre de test {video_id}",
        "pilier": "actu_ia",
        "voie": "rapide",
        "statut_global": "en_production",
        "etape_actuelle": "E4_audio",
        "etapes": {
            "E1_recherche": _etape_agent("termine"),
            "CP1": _checkpoint("valide"),
            "E2_redaction": _etape_agent("termine"),
            "E3_filtre": _etape_agent("termine"),
            "CP2": _checkpoint("valide"),
            "E4_audio": {**_etape_agent(e4_statut), "agent": None},
            "E5_storyboard": _etape_agent(),
            "E6_montage": _etape_agent(),
            "CP3": _checkpoint(),
            "E7_publication": _etape_agent(),
        },
        "publication": {"date_prevue": None, "date_effective": None, "url": None},
        "historique": [],
        "_scenario": {},
    }


class TestDesignerDansOrchestateur(unittest.TestCase):
    def setUp(self):
        self.root = tempfile.mkdtemp(prefix="chaine_yt_designer_orch_")
        os.makedirs(os.path.join(self.root, "videos"), exist_ok=True)

    def tearDown(self):
        shutil.rmtree(self.root, ignore_errors=True)

    def _creer_video(self, video_id, e4_statut):
        video_dir = os.path.join(self.root, "videos", video_id)
        os.makedirs(os.path.join(video_dir, "checkpoints"), exist_ok=True)
        save_state(video_dir, _etat_apres_cp2(video_id, e4_statut))
        return video_dir

    def test_e5_declenche_apres_cp2(self):
        video_dir = self._creer_video("2026-09-11_v06", e4_statut="attente_franco")

        run_once(self.root)
        state = load_state(video_dir)
        self.assertEqual(state["etapes"]["E5_storyboard"]["statut"], "termine")

    def test_e6_attend_e4_et_e5(self):
        video_dir = self._creer_video("2026-09-11_v07", e4_statut="attente_franco")

        run_once(self.root)
        state = load_state(video_dir)
        self.assertEqual(state["etapes"]["E5_storyboard"]["statut"], "termine")
        self.assertEqual(state["etapes"]["E4_audio"]["statut"], "attente_franco")
        self.assertEqual(state["etapes"]["E6_montage"]["statut"], "a_venir")


if __name__ == "__main__":
    unittest.main()
