"""
Tests de l'echec d'une etape manuelle (E4 audio, E7 publication).

Regression couverte : le notebook Colab passe `E4_audio` a `echec` quand le
controle qualite WER ne passe pas (§7.2, cellule 5). Or E4_audio est de kind
"attente_franco", pas "agent" : ni _traiter_echec_agent_reel ni
etapes_agent_actionnables ne la regardaient, et la branche manuelle de
traiter_video ne traitait que `a_venir`. Le run audio pouvait echouer trois
fois sans que rien n'apparaisse au tableau de bord — la video disparaissait
de "A faire par Franco" et s'arretait la, en violation du §2 ("3 tentatives
maximum par etape, puis alerte a Franco").

Lancer : python3 -m pytest tests/test_echec_etape_manuelle.py -v
"""

import os
import shutil
import tempfile
import unittest

from orchestrateur.config import charger_config
from orchestrateur.dashboard import rendre_dashboard
from orchestrateur.main import run_once
from orchestrateur.state_store import load_state, save_state

from tests.test_orchestrateur_factice import _etat_de_base, _valider_checkpoint


class TestEchecEtapeManuelle(unittest.TestCase):
    def setUp(self):
        self.root = tempfile.mkdtemp(prefix="chaine_yt_e4_")
        os.makedirs(os.path.join(self.root, "videos"), exist_ok=True)
        self.video_dir = os.path.join(self.root, "videos", "2026-09-10_v01")
        os.makedirs(os.path.join(self.video_dir, "checkpoints"), exist_ok=True)
        save_state(self.video_dir, _etat_de_base("2026-09-10_v01"))
        # Amener la video jusqu'a E4_audio en attente du run Colab.
        run_once(self.root)
        _valider_checkpoint(self.video_dir, "CP1")
        run_once(self.root)
        _valider_checkpoint(self.video_dir, "CP2")
        run_once(self.root)
        self.assertEqual(load_state(self.video_dir)["etapes"]["E4_audio"]["statut"],
                         "attente_franco")

    def tearDown(self):
        shutil.rmtree(self.root, ignore_errors=True)

    def _echec_colab(self, tentative, message="WER 7.10% > seuil 3%"):
        """Simule ce qu'ecrit etape_echouer() du notebook."""
        state = load_state(self.video_dir)
        state["etapes"]["E4_audio"].update(
            statut="echec", tentatives=tentative, message=message)
        save_state(self.video_dir, state)
        run_once(self.root)
        return load_state(self.video_dir)["etapes"]["E4_audio"]

    def _tableau(self):
        return rendre_dashboard(self.root, charger_config(self.root))

    def test_un_echec_redemande_l_action_a_franco(self):
        etape = self._echec_colab(1)
        self.assertEqual(etape["statut"], "attente_franco")
        self.assertIn("2026-09-10_v01", self._tableau())

    def test_la_raison_de_l_echec_est_affichee(self):
        """Franco ne doit pas relancer le meme run sans savoir ce qui a rate."""
        self._echec_colab(1, message="WER 7.10% > seuil 3%")
        tableau = self._tableau()
        self.assertIn("[ACTION]", tableau)
        self.assertIn("WER 7.10%", tableau)

    def test_trois_echecs_declenchent_une_alerte(self):
        for tentative in (1, 2):
            self.assertEqual(self._echec_colab(tentative)["statut"], "attente_franco")
        self.assertEqual(self._echec_colab(3)["statut"], "alerte")

        tableau = self._tableau()
        self.assertIn("[ALERTE]", tableau)
        self.assertIn("E4_audio", tableau)

    def test_l_historique_garde_la_trace_des_echecs(self):
        self._echec_colab(1)
        self._echec_colab(2)
        self._echec_colab(3)
        evenements = [h["evenement"] for h in load_state(self.video_dir)["historique"]]
        self.assertIn("alerte", evenements)

    def test_le_montage_ne_demarre_jamais_sur_un_audio_en_echec(self):
        self._echec_colab(1)
        self.assertEqual(load_state(self.video_dir)["etapes"]["E6_montage"]["statut"], "a_venir")

    def test_un_run_reussi_apres_un_echec_debloque_la_suite(self):
        self._echec_colab(1)
        state = load_state(self.video_dir)
        state["etapes"]["E4_audio"].update(
            statut="termine", sorties=["04_voixoff.wav", "04_timestamps.json"])
        save_state(self.video_dir, state)
        run_once(self.root)

        state = load_state(self.video_dir)
        self.assertEqual(state["etapes"]["E6_montage"]["statut"], "termine")
        self.assertEqual(state["etapes"]["CP3"]["statut"], "attente_validation")


if __name__ == "__main__":
    unittest.main()
