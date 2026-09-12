"""
Test d'integration bout en bout : skills/new-short (vendored) -> Orchestrateur
(agents factices) -> skills/short-state (vendored), comme demande au §13
etape 1 : "short-state sert d'outil de verification."

Lancer : python -m unittest tests.test_integration_short_state -v
"""

import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from datetime import datetime, timezone

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
NEW_SHORT = os.path.join(REPO_ROOT, "skills", "new-short", "scripts", "new_short.py")
SHORT_STATE = os.path.join(REPO_ROOT, "skills", "short-state", "scripts", "short_state.py")

from orchestrateur.checkpoints import chemin_rapport
from orchestrateur.init_structure import initialiser
from orchestrateur.main import run_once
from orchestrateur.state_store import load_state, save_state


def _lancer(script, *args):
    p = subprocess.run([sys.executable, script, *args], capture_output=True, text=True)
    return json.loads(p.stdout)


def _valider_checkpoint(video_dir, checkpoint_id, statut="VALIDE", commentaire="OK"):
    path = chemin_rapport(video_dir, checkpoint_id)
    with open(path, "r", encoding="utf-8") as f:
        contenu = f.read()
    contenu = contenu.replace("Statut : EN_ATTENTE        <!-- remplacer par VALIDE ou REFUSE -->",
                               f"Statut : {statut}")
    contenu = contenu.replace("Commentaire :\n", f"Commentaire : {commentaire}\n")
    with open(path, "w", encoding="utf-8") as f:
        f.write(contenu)


class TestIntegrationShortState(unittest.TestCase):
    def setUp(self):
        self.root = tempfile.mkdtemp(prefix="chaine_yt_integration_")
        initialiser(self.root)
        # Ces tests exercent les agents factices (§13 etape 1), pas les
        # skills reels : on force le mode "factice" malgre le config.json
        # "reel" ecrit par defaut par initialiser() pour la production.
        config_path = os.path.join(self.root, "01_Orchestrateur", "config.json")
        with open(config_path, "r", encoding="utf-8") as f:
            config = json.load(f)
        config["mode_agents"] = "factice"
        with open(config_path, "w", encoding="utf-8") as f:
            json.dump(config, f, ensure_ascii=False, indent=2)

    def tearDown(self):
        shutil.rmtree(self.root, ignore_errors=True)

    def test_checkpoint_visible_dans_short_state_puis_valide(self):
        creation = _lancer(NEW_SHORT, "--root", self.root, "--sujet", "Test sujet CP1",
                            "--pilier", "actu_ia", "--voie", "rapide")
        self.assertEqual(creation["code"], 0, creation)
        video_id = creation["video_id"]
        video_dir = os.path.join(self.root, "videos", video_id)

        run_once(self.root)

        etat = _lancer(SHORT_STATE, "--root", self.root)
        self.assertEqual(etat["code"], 0, etat)
        checkpoints = [a for a in etat["actions"] if a["type"] == "CHECKPOINT" and a["video_id"] == video_id]
        self.assertEqual(len(checkpoints), 1, etat["actions"])
        self.assertEqual(checkpoints[0]["etape"], "CP1")

        _valider_checkpoint(video_dir, "CP1")
        run_once(self.root)

        etat = _lancer(SHORT_STATE, "--root", self.root, "--video", video_id)
        self.assertEqual(etat["code"], 0, etat)
        cp1 = next(e for e in etat["etapes"] if e["etape"] == "CP1")
        self.assertEqual(cp1["statut"], "valide")

    def test_alerte_visible_dans_short_state(self):
        creation = _lancer(NEW_SHORT, "--root", self.root, "--sujet", "Test sujet echec",
                            "--pilier", "actu_ia", "--voie", "rapide")
        self.assertEqual(creation["code"], 0, creation)
        video_id = creation["video_id"]
        video_dir = os.path.join(self.root, "videos", video_id)

        state = load_state(video_dir)
        state["_scenario"] = {"E1_recherche": "echec"}
        save_state(video_dir, state)

        for _ in range(3):
            run_once(self.root)

        etat = _lancer(SHORT_STATE, "--root", self.root)
        alertes = [a for a in etat["actions"] if a["type"] == "ALERTE" and a["video_id"] == video_id]
        self.assertEqual(len(alertes), 1, etat["actions"])
        self.assertEqual(alertes[0]["etape"], "E1_recherche")

    def test_registre_liste_les_videos_creees(self):
        creation = _lancer(NEW_SHORT, "--root", self.root, "--sujet", "Test registre",
                            "--pilier", "concept", "--voie", "tampon")
        self.assertEqual(creation["code"], 0, creation)

        registre = _lancer(SHORT_STATE, "--root", self.root, "--registre")
        self.assertEqual(registre["total"], 1)
        self.assertEqual(registre["videos"][0]["video_id"], creation["video_id"])


if __name__ == "__main__":
    unittest.main()


class TestDateDuDernierPassage(unittest.TestCase):
    """
    L'Orchestrateur ecrit `{"horodatage": ...}` ; short-state lisait
    `fin`/`debut`, qui n'ont jamais existe. La date declaree n'etait donc
    jamais trouvee et on retombait en silence sur la mtime du tableau de
    bord — un repli qui marche par accident.
    """

    def setUp(self):
        self.root = tempfile.mkdtemp(prefix="etat_horodatage_")
        os.makedirs(os.path.join(self.root, "00_Profil"))
        os.makedirs(os.path.join(self.root, "01_Orchestrateur"))
        os.makedirs(os.path.join(self.root, "videos"))

    def tearDown(self):
        shutil.rmtree(self.root, ignore_errors=True)

    def _ecrire_execution(self, contenu):
        chemin = os.path.join(self.root, "01_Orchestrateur", "derniere_execution.json")
        with open(chemin, "w", encoding="utf-8") as f:
            json.dump(contenu, f)

    def _lancer(self):
        proc = subprocess.run(
            [sys.executable,
             os.path.join(REPO_ROOT, "skills", "short-state", "scripts", "short_state.py"),
             "--root", self.root],
            capture_output=True, text=True)
        return json.loads(proc.stdout)

    def test_la_cle_horodatage_est_lue(self):
        maintenant = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        self._ecrire_execution({"horodatage": maintenant})

        sortie = self._lancer()

        systeme = sortie.get("systeme") or {}
        self.assertEqual(systeme.get("source"), "derniere_execution.json")
        self.assertIsNotNone(systeme.get("orchestrateur_dernier_passage"))

    def test_sans_tableau_de_bord_ni_horodatage_lisible(self):
        # Le repli sur la mtime n'existe pas ici : il faut que l'absence se
        # dise, pas qu'elle se devine.
        self._ecrire_execution({"fin": None})
        sortie = self._lancer()
        self.assertIsNone((sortie.get("systeme") or {}).get("orchestrateur_dernier_passage"))
