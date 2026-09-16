"""
Teste la partie de `outils/lancer_voix_off.py` qui ne depend pas de Colab :
le choix de la video, le garde-fou de racine, la verification du resultat, et
les parametres poses dans le noyau distant.

**Ce qui n'est PAS teste ici, et pourquoi.** Aucun faux binaire `colab` :
simuler un outil dont on ne connait ni les codes de retour ni le format de
sortie ne teste que la simulation. L'enchainement `new / drivemount / exec /
log / stop` se constatera au premier run reel.

C'est precisement pour ca que le lanceur ne conclut pas sur le code de retour
de `colab exec` mais sur `verifier_sorties`, qui relit le Drive — et cette
fonction-la, elle, est testable sans Colab. Les tests portent donc sur le seul
controle dont le succes depend.
"""
import json
import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "outils"))

import lancer_voix_off as lvo  # noqa: E402


def _ecrire_video(racine, video_id, statut_audio, message=None):
    dossier = Path(racine) / "videos" / video_id
    dossier.mkdir(parents=True, exist_ok=True)
    etape = {"statut": statut_audio, "tentatives": 0}
    if message:
        etape["message"] = message
    state = {
        "video_id": video_id,
        "titre_travail": f"titre de {video_id}",
        "etapes": {"E4_audio": etape},
    }
    (dossier / "state.json").write_text(json.dumps(state), encoding="utf-8")
    return dossier


def _ecrire_sorties(dossier, vides=(), absents=()):
    for nom in lvo.SORTIES_ATTENDUES:
        if nom in absents:
            continue
        (dossier / nom).write_text("" if nom in vides else "contenu", encoding="utf-8")


class TestRacine(unittest.TestCase):
    def test_racine_absente_refusee(self):
        ok, message = lvo.verifier_racine("/chemin/qui/n/existe/pas")
        self.assertFalse(ok)
        self.assertIn("introuvable", message)

    def test_point_de_montage_vide_refuse(self):
        """Un Drive non monte laisse souvent un dossier vide a sa place. Il
        ressemble a une racine valide et n'en est pas — meme garde-fou que
        lancer_orchestrateur.py."""
        with tempfile.TemporaryDirectory() as tmp:
            ok, message = lvo.verifier_racine(tmp)
            self.assertFalse(ok)
            self.assertIn("videos", message)

    def test_racine_valide_acceptee(self):
        with tempfile.TemporaryDirectory() as tmp:
            (Path(tmp) / "videos").mkdir()
            ok, _ = lvo.verifier_racine(tmp)
            self.assertTrue(ok)


class TestChoixVideo(unittest.TestCase):
    def test_une_seule_candidate_selectionnee(self):
        with tempfile.TemporaryDirectory() as tmp:
            _ecrire_video(tmp, "2026-09-11_v01", "attente_franco")
            _ecrire_video(tmp, "2026-09-12_v01", "termine")
            vid, _ = lvo.choisir_video(tmp, None)
            self.assertEqual(vid, "2026-09-11_v01")

    def test_echec_et_en_cours_sont_candidats(self):
        """`echec` se reprend, `en_cours` est un run precedent coupe net."""
        for statut in ("echec", "en_cours"):
            with tempfile.TemporaryDirectory() as tmp:
                _ecrire_video(tmp, "2026-09-11_v01", statut)
                vid, _ = lvo.choisir_video(tmp, None)
                self.assertEqual(vid, "2026-09-11_v01", statut)

    def test_ambiguite_refusee(self):
        """Deux videos en attente : choisir pour Franco, c'est risquer de
        synthetiser la mauvaise, ce qui consomme une tentative sur les trois."""
        with tempfile.TemporaryDirectory() as tmp:
            _ecrire_video(tmp, "2026-09-11_v01", "attente_franco")
            _ecrire_video(tmp, "2026-09-12_v01", "echec")
            vid, message = lvo.choisir_video(tmp, None)
            self.assertIsNone(vid)
            self.assertIn("ambigu", message)

    def test_aucune_candidate(self):
        with tempfile.TemporaryDirectory() as tmp:
            _ecrire_video(tmp, "2026-09-11_v01", "termine")
            vid, message = lvo.choisir_video(tmp, None)
            self.assertIsNone(vid)
            self.assertIn("aucune", message.lower())

    def test_video_imposee_sans_state(self):
        with tempfile.TemporaryDirectory() as tmp:
            (Path(tmp) / "videos").mkdir()
            vid, message = lvo.choisir_video(tmp, "2026-09-99_v01")
            self.assertIsNone(vid)
            self.assertIn("state.json", message)

    def test_state_avec_bom_lisible(self):
        """Les state.json edites sous Windows portent un BOM ; le reste du
        depot les tolere depuis le 11/09, celui-ci doit faire pareil."""
        with tempfile.TemporaryDirectory() as tmp:
            dossier = _ecrire_video(tmp, "2026-09-11_v01", "attente_franco")
            brut = (dossier / "state.json").read_text(encoding="utf-8")
            (dossier / "state.json").write_text("﻿" + brut, encoding="utf-8")
            vid, _ = lvo.choisir_video(tmp, None)
            self.assertEqual(vid, "2026-09-11_v01")


class TestVerificationDuResultat(unittest.TestCase):
    """Le controle qui decide du succes, a la place du code de retour."""

    def test_succes_complet(self):
        with tempfile.TemporaryDirectory() as tmp:
            dossier = _ecrire_video(tmp, "2026-09-11_v01", "termine")
            _ecrire_sorties(dossier)
            ok, _ = lvo.verifier_sorties(tmp, "2026-09-11_v01")
            self.assertTrue(ok)

    def test_statut_termine_mais_sortie_manquante(self):
        """Le cas qui justifie ce controle : un state.json qui dit `termine`
        alors que `04_phrases.json` n'a pas ete ecrit. Le montage partirait
        sur les estimations du storyboard, et le decalage son/image
        reapparaitrait sans que rien ne l'ait signale."""
        with tempfile.TemporaryDirectory() as tmp:
            dossier = _ecrire_video(tmp, "2026-09-11_v01", "termine")
            _ecrire_sorties(dossier, absents=("04_phrases.json",))
            ok, message = lvo.verifier_sorties(tmp, "2026-09-11_v01")
            self.assertFalse(ok)
            self.assertIn("04_phrases.json", message)

    def test_sortie_vide_refusee(self):
        with tempfile.TemporaryDirectory() as tmp:
            dossier = _ecrire_video(tmp, "2026-09-11_v01", "termine")
            _ecrire_sorties(dossier, vides=("04_voixoff.wav",))
            ok, message = lvo.verifier_sorties(tmp, "2026-09-11_v01")
            self.assertFalse(ok)
            self.assertIn("vide", message)

    def test_sorties_presentes_mais_statut_echec(self):
        """Un run refuse au controle WER laisse des fichiers d'une tentative
        precedente. Les fichiers ne suffisent donc pas : le statut compte."""
        with tempfile.TemporaryDirectory() as tmp:
            dossier = _ecrire_video(tmp, "2026-09-11_v01", "echec", message="WER 18 %")
            _ecrire_sorties(dossier)
            ok, message = lvo.verifier_sorties(tmp, "2026-09-11_v01")
            self.assertFalse(ok)
            self.assertIn("WER 18 %", message)


class TestParametresDistants(unittest.TestCase):
    def test_preambule_est_du_python_valide(self):
        code = lvo._preambule("2026-09-11_v01", "full", "/content/drive/MyDrive/ChaineYouTube", False)
        compile(code, "preambule", "exec")

    def test_preambule_pose_les_variables(self):
        code = lvo._preambule("2026-09-11_v01", "full", "/racine/vm", True)
        espace = {}
        exec(compile(code, "preambule", "exec"), espace)  # noqa: S102
        env = espace["os"].environ
        self.assertEqual(env["VOIX_VIDEO_ID"], "2026-09-11_v01")
        self.assertEqual(env["VOIX_MODE"], "full")
        self.assertEqual(env["VOIX_RACINE"], "/racine/vm")
        self.assertEqual(env["VOIX_FORCER_RELANCE"], "1")
        # Sans ce drapeau, la Cell 2 ouvrirait un selecteur de fichiers que
        # personne ne regarde, et la session attendrait jusqu'au timeout.
        self.assertEqual(env["VOIX_NON_INTERACTIF"], "1")

    def test_voice_only_refuse_en_ligne_de_commande(self):
        """Enregistrer une voix demande un upload interactif : ce mode n'a pas
        de sens depuis le lanceur, et le laisser passer produirait le blocage
        silencieux que le garde-fou de la Cell 2 est cense empecher."""
        with self.assertRaises(SystemExit):
            lvo.main(["--root", "/x", "--mode", "voice_only"])


if __name__ == "__main__":
    unittest.main()
