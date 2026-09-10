"""
Test d'integration des vrais scripts d'agent (agents/*/scripts/etape.py),
en mode "reel" : simule ce qu'un skill Claude Code ferait, verifie que
l'Orchestrateur enchaine correctement (§13, etape 3).
"""

import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
NEW_SHORT = os.path.join(REPO_ROOT, "skills", "new-short", "scripts", "new_short.py")
ETAPE = {
    "chercheur": os.path.join(REPO_ROOT, "agents", "chercheur", "scripts", "etape.py"),
    "redacteur": os.path.join(REPO_ROOT, "agents", "redacteur", "scripts", "etape.py"),
    "filtre_tts": os.path.join(REPO_ROOT, "agents", "filtre_tts", "scripts", "etape.py"),
}

from orchestrateur.checkpoints import chemin_rapport
from orchestrateur.init_structure import initialiser
from orchestrateur.main import run_once
from orchestrateur.state_store import load_state


def _lancer(script, *args):
    p = subprocess.run([sys.executable, script, *args], capture_output=True, text=True)
    if p.returncode != 0:
        raise AssertionError(f"{script} {args} -> {p.returncode}\n{p.stdout}\n{p.stderr}")
    return json.loads(p.stdout)


def _valider_checkpoint(video_dir, checkpoint_id):
    path = chemin_rapport(video_dir, checkpoint_id)
    with open(path, "r", encoding="utf-8") as f:
        contenu = f.read()
    contenu = contenu.replace("Statut : EN_ATTENTE        <!-- remplacer par VALIDE ou REFUSE -->",
                               "Statut : VALIDE")
    with open(path, "w", encoding="utf-8") as f:
        f.write(contenu)


class TestAgentsReels(unittest.TestCase):
    def setUp(self):
        self.root = tempfile.mkdtemp(prefix="chaine_yt_agents_reels_")
        initialiser(self.root)
        creation = _lancer(NEW_SHORT, "--root", self.root, "--sujet", "Comment fonctionne RAG",
                            "--pilier", "concept", "--voie", "tampon")
        self.video_id = creation["video_id"]
        self.video_dir = os.path.join(self.root, "videos", self.video_id)

    def tearDown(self):
        shutil.rmtree(self.root, ignore_errors=True)

    def _executer_chercheur(self):
        _lancer(ETAPE["chercheur"], "commencer", "--root", self.root, "--video", self.video_id,
                "--etape", "E1_recherche")
        with open(os.path.join(self.video_dir, "01_recherche.md"), "w", encoding="utf-8") as f:
            f.write("# Recherche\n\n## Faits verifies\n- RAG combine recherche et generation.\n")
        _lancer(ETAPE["chercheur"], "terminer", "--root", self.root, "--video", self.video_id,
                "--etape", "E1_recherche", "--sorties", "01_recherche.md", "--message", "OK")

    def _executer_redacteur(self):
        _lancer(ETAPE["redacteur"], "commencer", "--root", self.root, "--video", self.video_id,
                "--etape", "E2_redaction")
        with open(os.path.join(self.video_dir, "02_script_brut.md"), "w", encoding="utf-8") as f:
            f.write("# Script brut\n\nRAG means retrieval augmented generation. It helps models use fresh facts.\n")
        _lancer(ETAPE["redacteur"], "terminer", "--root", self.root, "--video", self.video_id,
                "--etape", "E2_redaction", "--sorties", "02_script_brut.md", "--message", "OK")

    def test_flux_complet_jusqu_a_cp2(self):
        self._executer_chercheur()
        run_once(self.root)

        state = load_state(self.video_dir)
        self.assertEqual(state["etapes"]["CP1"]["statut"], "attente_validation")
        with open(chemin_rapport(self.video_dir, "CP1"), encoding="utf-8") as f:
            self.assertIn("RAG combine recherche et generation", f.read())

        _valider_checkpoint(self.video_dir, "CP1")
        run_once(self.root)
        state = load_state(self.video_dir)
        self.assertEqual(state["etapes"]["CP1"]["statut"], "valide")
        self.assertEqual(state["etapes"]["E2_redaction"]["statut"], "a_venir")

        self._executer_redacteur()
        run_once(self.root)
        state = load_state(self.video_dir)
        self.assertEqual(state["etapes"]["E3_filtre"]["statut"], "a_venir")

        _lancer(ETAPE["filtre_tts"], "commencer", "--root", self.root, "--video", self.video_id,
                "--etape", "E3_filtre")
        for nom in ("03_script_final.md", "03_script_tts.txt", "03_rapport_metriques.md"):
            with open(os.path.join(self.video_dir, nom), "w", encoding="utf-8") as f:
                f.write("contenu de test\n")
        _lancer(ETAPE["filtre_tts"], "terminer", "--root", self.root, "--video", self.video_id,
                "--etape", "E3_filtre", "--sorties", "03_script_final.md", "03_script_tts.txt",
                "03_rapport_metriques.md", "--message", "OK")

        run_once(self.root)
        state = load_state(self.video_dir)
        self.assertEqual(state["etapes"]["CP2"]["statut"], "attente_validation")

    def test_revision_filtre_renvoie_a_la_redaction(self):
        self._executer_chercheur()
        run_once(self.root)
        _valider_checkpoint(self.video_dir, "CP1")
        run_once(self.root)
        self._executer_redacteur()
        run_once(self.root)

        _lancer(ETAPE["filtre_tts"], "commencer", "--root", self.root, "--video", self.video_id,
                "--etape", "E3_filtre")
        _lancer(ETAPE["filtre_tts"], "echouer", "--root", self.root, "--video", self.video_id,
                "--etape", "E3_filtre", "--message", "3 phrases trop longues, ton trop formel",
                "--action-suivi", "revision_redaction")

        run_once(self.root)
        state = load_state(self.video_dir)
        self.assertEqual(state["boucle_A4_A5"], 1)
        self.assertEqual(state["etapes"]["E2_redaction"]["statut"], "a_venir")
        self.assertEqual(state["etapes"]["E3_filtre"]["statut"], "a_venir")


if __name__ == "__main__":
    unittest.main()
