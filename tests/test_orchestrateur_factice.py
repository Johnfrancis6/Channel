"""
Tests du squelette de l'Orchestrateur avec des agents factices (§13, etape 1).
Verifie les trois comportements attendus : succes, echec -> alerte, et
checkpoints (attente_validation + decision de Franco retranscrite).

Lancer : python -m unittest tests.test_orchestrateur_factice -v
"""

import os
import shutil
import tempfile
import unittest

from orchestrateur.checkpoints import chemin_rapport
from orchestrateur.main import run_once
from orchestrateur.state_store import load_state, save_state


def _etape_agent(statut="a_venir"):
    return {"agent": None, "statut": statut, "tentatives": 0, "debut": None, "fin": None, "sorties": [], "message": None}


def _checkpoint(statut="a_venir"):
    return {"statut": statut, "commentaire": None, "date": None}


def _etat_de_base(video_id, scenario=None):
    return {
        "video_id": video_id,
        "titre_travail": f"Titre de test {video_id}",
        "pilier": "actu_ia",
        "voie": "rapide",
        "statut_global": "sujet_valide",
        "etape_actuelle": "E1_recherche",
        "etapes": {
            "E1_recherche": _etape_agent(),
            "CP1": _checkpoint(),
            "E2_redaction": _etape_agent(),
            "E3_filtre": _etape_agent(),
            "CP2": _checkpoint(),
            "E4_audio": _etape_agent(),
            "E5_storyboard": _etape_agent(),
            "E6_montage": _etape_agent(),
            "CP3": _checkpoint(),
            "E7_publication": _etape_agent(),
        },
        "publication": {"date_prevue": None, "date_effective": None, "url": None},
        "historique": [],
        "_scenario": scenario or {},
    }


def _valider_checkpoint(video_dir, checkpoint_id, statut="VALIDE", commentaire="OK"):
    path = chemin_rapport(video_dir, checkpoint_id)
    with open(path, "r", encoding="utf-8") as f:
        contenu = f.read()
    contenu = contenu.replace("Statut : EN_ATTENTE        <!-- remplacer par VALIDE ou REFUSE -->",
                               f"Statut : {statut}")
    contenu = contenu.replace("Commentaire :\n", f"Commentaire : {commentaire}\n")
    with open(path, "w", encoding="utf-8") as f:
        f.write(contenu)


class TestOrchestrateurFactice(unittest.TestCase):
    def setUp(self):
        self.root = tempfile.mkdtemp(prefix="chaine_yt_test_")
        os.makedirs(os.path.join(self.root, "videos"), exist_ok=True)

    def tearDown(self):
        shutil.rmtree(self.root, ignore_errors=True)

    def _creer_video(self, video_id, scenario=None):
        video_dir = os.path.join(self.root, "videos", video_id)
        os.makedirs(os.path.join(video_dir, "checkpoints"), exist_ok=True)
        save_state(video_dir, _etat_de_base(video_id, scenario))
        return video_dir

    def test_parcours_succes_avec_checkpoints(self):
        video_dir = self._creer_video("2026-09-10_v01")

        run_once(self.root)
        state = load_state(video_dir)
        self.assertEqual(state["etapes"]["E1_recherche"]["statut"], "termine")
        self.assertEqual(state["etapes"]["CP1"]["statut"], "attente_validation")
        self.assertTrue(os.path.isfile(chemin_rapport(video_dir, "CP1")))

        _valider_checkpoint(video_dir, "CP1")
        run_once(self.root)
        state = load_state(video_dir)
        self.assertEqual(state["etapes"]["CP1"]["statut"], "valide")
        self.assertEqual(state["statut_global"], "en_production")
        self.assertEqual(state["etapes"]["E2_redaction"]["statut"], "termine")
        self.assertEqual(state["etapes"]["E3_filtre"]["statut"], "termine")
        self.assertEqual(state["etapes"]["CP2"]["statut"], "attente_validation")

        _valider_checkpoint(video_dir, "CP2")
        run_once(self.root)
        state = load_state(video_dir)
        self.assertEqual(state["etapes"]["CP2"]["statut"], "valide")
        self.assertEqual(state["etapes"]["E4_audio"]["statut"], "attente_franco")
        self.assertEqual(state["etapes"]["E5_storyboard"]["statut"], "termine")
        # E6 attend E4 (audio manuel) : pas encore lance
        self.assertEqual(state["etapes"]["E6_montage"]["statut"], "a_venir")

        # Simule Franco qui lance le run Colab (le notebook ecrirait "termine")
        state["etapes"]["E4_audio"]["statut"] = "termine"
        state["etapes"]["E4_audio"]["sorties"] = ["04_voixoff.wav", "04_timestamps.json"]
        save_state(video_dir, state)

        run_once(self.root)
        state = load_state(video_dir)
        self.assertEqual(state["etapes"]["E6_montage"]["statut"], "termine")
        self.assertEqual(state["etapes"]["CP3"]["statut"], "attente_validation")

        _valider_checkpoint(video_dir, "CP3")
        run_once(self.root)
        state = load_state(video_dir)
        self.assertEqual(state["statut_global"], "prete")
        self.assertEqual(state["etapes"]["E7_publication"]["statut"], "attente_franco")

    def test_echec_repete_declenche_alerte(self):
        video_dir = self._creer_video("2026-09-10_v02", scenario={"E1_recherche": "echec"})

        for _ in range(3):
            run_once(self.root)

        state = load_state(video_dir)
        self.assertEqual(state["etapes"]["E1_recherche"]["statut"], "alerte")
        self.assertEqual(state["etapes"]["E1_recherche"]["tentatives"], 3)
        self.assertEqual(state["etapes"]["CP1"]["statut"], "a_venir")

    def test_boucle_redaction_filtre_plafonnee_a_trois_tours(self):
        video_dir = self._creer_video("2026-09-10_v03", scenario={"E3_filtre": "revision"})
        state = load_state(video_dir)
        state["etapes"]["CP1"]["statut"] = "valide"
        save_state(video_dir, state)

        for _ in range(3):
            run_once(self.root)

        state = load_state(video_dir)
        self.assertEqual(state["boucle_A4_A5"], 3)
        self.assertEqual(state["etapes"]["E3_filtre"]["statut"], "alerte")
        self.assertEqual(state["etapes"]["CP2"]["statut"], "a_venir")


if __name__ == "__main__":
    unittest.main()
