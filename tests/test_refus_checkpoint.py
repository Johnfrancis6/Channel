"""
Tests du chemin "refus de checkpoint" (§5.5), qui n'etait couvert nulle part.

Regression couverte : un checkpoint refuse restait `refuse` pour toujours.
_ouvrir_checkpoint_si_pret() n'agit que sur `a_venir` et _pret() exige
`valide` en aval, donc la video se figeait sans rien signaler a Franco.

Lancer : python3 -m pytest tests/test_refus_checkpoint.py -v
"""

import os
import shutil
import tempfile
import unittest

from orchestrateur.checkpoints import chemin_rapport
from orchestrateur.main import run_once
from orchestrateur.state_store import load_state, save_state

from tests.test_orchestrateur_factice import _etat_de_base, _valider_checkpoint


def _dossier_refuses(video_dir):
    return os.path.join(video_dir, "checkpoints", "refuses")


class TestRefusCheckpoint(unittest.TestCase):
    def setUp(self):
        self.root = tempfile.mkdtemp(prefix="chaine_yt_refus_")
        os.makedirs(os.path.join(self.root, "videos"), exist_ok=True)

    def tearDown(self):
        shutil.rmtree(self.root, ignore_errors=True)

    def _creer_video(self, video_id, scenario=None):
        video_dir = os.path.join(self.root, "videos", video_id)
        os.makedirs(os.path.join(video_dir, "checkpoints"), exist_ok=True)
        save_state(video_dir, _etat_de_base(video_id, scenario))
        return video_dir

    def _amener_a(self, video_dir, checkpoint_id):
        """Fait avancer la video jusqu'a ce que `checkpoint_id` attende Franco."""
        precedents = {"CP1": [], "CP2": ["CP1"], "CP3": ["CP1", "CP2"]}[checkpoint_id]
        run_once(self.root)
        for cp in precedents:
            _valider_checkpoint(video_dir, cp)
            run_once(self.root)
            if cp == "CP2":
                # E4_audio est manuel : on simule le run Colab de Franco.
                state = load_state(video_dir)
                state["etapes"]["E4_audio"]["statut"] = "termine"
                save_state(video_dir, state)
                run_once(self.root)
        state = load_state(video_dir)
        self.assertEqual(state["etapes"][checkpoint_id]["statut"], "attente_validation")

    def test_cp1_refuse_relance_la_recherche_et_rouvre_le_checkpoint(self):
        video_dir = self._creer_video("2026-09-10_v01")
        self._amener_a(video_dir, "CP1")

        _valider_checkpoint(video_dir, "CP1", statut="REFUSE", commentaire="Angle trop vague")
        run_once(self.root)

        state = load_state(video_dir)
        # La recherche a ete refaite et le checkpoint attend une NOUVELLE decision.
        self.assertEqual(state["etapes"]["E1_recherche"]["statut"], "termine")
        self.assertEqual(state["etapes"]["CP1"]["statut"], "attente_validation")
        # Le commentaire de Franco reste l'input de l'agent relance (§5.5).
        self.assertEqual(state["etapes"]["CP1"]["commentaire"], "Angle trop vague")

    def test_le_rapport_refuse_est_archive_et_regenere_a_neuf(self):
        video_dir = self._creer_video("2026-09-10_v02")
        self._amener_a(video_dir, "CP1")

        _valider_checkpoint(video_dir, "CP1", statut="REFUSE", commentaire="Angle trop vague")
        run_once(self.root)

        archives = os.listdir(_dossier_refuses(video_dir))
        self.assertEqual(len(archives), 1)
        self.assertIn("REFUSE", open(os.path.join(_dossier_refuses(video_dir), archives[0]),
                                      encoding="utf-8").read())

        # Le rapport courant est neuf : sans archivage, l'Orchestrateur
        # relisait indefiniment le meme REFUSE.
        courant = open(chemin_rapport(video_dir, "CP1"), encoding="utf-8").read()
        self.assertIn("EN_ATTENTE", courant)
        self.assertIn("Refus precedent : Angle trop vague", courant)

    def test_un_rapport_disparu_est_regenere_au_passage_suivant(self):
        # La generation etait accrochee a la seule transition `a_venir` ->
        # `attente_validation`. Un rapport perdu ensuite ne revenait jamais :
        # la video restait en attente d'une decision que Franco n'avait aucun
        # fichier pour prendre, et le tableau de bord la reclamait a chaque
        # passage.
        video_dir = self._creer_video("2026-09-10_v06")
        self._amener_a(video_dir, "CP1")

        os.remove(chemin_rapport(video_dir, "CP1"))
        run_once(self.root)

        self.assertTrue(os.path.isfile(chemin_rapport(video_dir, "CP1")))
        self.assertIn("EN_ATTENTE", open(chemin_rapport(video_dir, "CP1"),
                                          encoding="utf-8").read())
        self.assertEqual(load_state(video_dir)["etapes"]["CP1"]["statut"], "attente_validation")

    def test_refus_puis_validation_laisse_le_pipeline_repartir(self):
        video_dir = self._creer_video("2026-09-10_v03")
        self._amener_a(video_dir, "CP1")

        _valider_checkpoint(video_dir, "CP1", statut="REFUSE", commentaire="A revoir")
        run_once(self.root)
        _valider_checkpoint(video_dir, "CP1", statut="VALIDE", commentaire="OK cette fois")
        run_once(self.root)

        state = load_state(video_dir)
        self.assertEqual(state["etapes"]["CP1"]["statut"], "valide")
        self.assertEqual(state["statut_global"], "en_production")
        self.assertEqual(state["etapes"]["E2_redaction"]["statut"], "termine")

    def test_refus_ne_consomme_pas_les_tentatives_de_l_etape(self):
        """Un refus n'est pas un echec technique : il ne doit pas rapprocher
        l'etape de l'alerte a 3 echecs."""
        video_dir = self._creer_video("2026-09-10_v04")
        self._amener_a(video_dir, "CP1")

        for _ in range(3):
            _valider_checkpoint(video_dir, "CP1", statut="REFUSE", commentaire="Encore non")
            run_once(self.root)

        state = load_state(video_dir)
        self.assertEqual(state["etapes"]["E1_recherche"]["statut"], "termine")
        self.assertEqual(state["etapes"]["E1_recherche"]["tentatives"], 1)
        self.assertEqual(state["etapes"]["CP1"]["statut"], "attente_validation")

    def test_cp2_refuse_relance_redaction_et_filtre_et_remet_la_boucle_a_zero(self):
        video_dir = self._creer_video("2026-09-10_v05")
        self._amener_a(video_dir, "CP2")

        state = load_state(video_dir)
        state["boucle_A4_A5"] = 2  # la video avait deja boucle deux fois
        save_state(video_dir, state)

        _valider_checkpoint(video_dir, "CP2", statut="REFUSE", commentaire="Hook faible")
        run_once(self.root)

        state = load_state(video_dir)
        # Sans remise a zero, le premier tour de revision partait en alerte.
        self.assertEqual(state["boucle_A4_A5"], 0)
        self.assertEqual(state["etapes"]["E2_redaction"]["statut"], "termine")
        self.assertEqual(state["etapes"]["E3_filtre"]["statut"], "termine")
        self.assertEqual(state["etapes"]["CP2"]["statut"], "attente_validation")

    def test_cp3_refuse_relance_le_montage(self):
        video_dir = self._creer_video("2026-09-10_v06")
        self._amener_a(video_dir, "CP3")

        _valider_checkpoint(video_dir, "CP3", statut="REFUSE", commentaire="Sous-titres decales")
        run_once(self.root)

        state = load_state(video_dir)
        self.assertEqual(state["etapes"]["E6_montage"]["statut"], "termine")
        self.assertEqual(state["etapes"]["CP3"]["statut"], "attente_validation")
        # La video n'est surtout pas passee "prete" : §2, pas de publication
        # sans CP3 valide.
        self.assertNotEqual(state["statut_global"], "prete")

    def test_une_video_refusee_reste_visible_au_tableau_de_bord(self):
        from orchestrateur.config import charger_config
        from orchestrateur.dashboard import rendre_dashboard

        video_dir = self._creer_video("2026-09-10_v07")
        self._amener_a(video_dir, "CP1")
        _valider_checkpoint(video_dir, "CP1", statut="REFUSE", commentaire="Non")
        run_once(self.root)

        tableau = rendre_dashboard(self.root, charger_config(self.root))
        self.assertIn("2026-09-10_v07", tableau)
        self.assertIn("CP1", tableau)


if __name__ == "__main__":
    unittest.main()
