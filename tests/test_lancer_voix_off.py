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


class TestVerdictSurLaVM(unittest.TestCase):
    """Le controle qui decide vraiment, execute la ou l'ecriture a eu lieu.

    Le 16/09/2026, un run reussi — WER 1,47 %, E4_audio = termine, quatre
    fichiers ecrits — a ete declare en echec parce que le controle lisait le
    miroir Drive local, qui n'avait pas encore synchronise. Juger depuis le
    mauvais cote du reseau, c'est le meme defaut que capturer_web.py sous une
    autre forme.
    """

    def _executer_sur(self, racine, video_id):
        """Execute LE code reel envoye a la VM, ici, contre un dossier temoin.

        Ce n'est pas un faux `colab` : c'est le snippet lui-meme, tel qu'il
        partira, joue sur un vrai systeme de fichiers.
        """
        import io as _io, contextlib
        code = lvo.code_verification(str(racine), video_id)
        tampon = _io.StringIO()
        with contextlib.redirect_stdout(tampon):
            exec(compile(code, "verification", "exec"), {})  # noqa: S102
        return tampon.getvalue()

    def test_succes(self):
        with tempfile.TemporaryDirectory() as tmp:
            dossier = _ecrire_video(tmp, "2026-09-16_v01", "termine")
            _ecrire_sorties(dossier)
            ok, _ = lvo.juger_verdict(self._executer_sur(tmp, "2026-09-16_v01"))
            self.assertTrue(ok)

    def test_sortie_manquante(self):
        with tempfile.TemporaryDirectory() as tmp:
            dossier = _ecrire_video(tmp, "2026-09-16_v01", "termine")
            _ecrire_sorties(dossier, absents=("04_phrases.json",))
            ok, message = lvo.juger_verdict(self._executer_sur(tmp, "2026-09-16_v01"))
            self.assertFalse(ok)
            self.assertIn("04_phrases.json", message)

    def test_statut_echec_remonte_son_message(self):
        with tempfile.TemporaryDirectory() as tmp:
            dossier = _ecrire_video(tmp, "2026-09-16_v01", "echec", message="WER 18 %")
            _ecrire_sorties(dossier)
            ok, message = lvo.juger_verdict(self._executer_sur(tmp, "2026-09-16_v01"))
            self.assertFalse(ok)
            self.assertIn("WER 18 %", message)

    def test_verdict_absent_ne_vaut_pas_succes(self):
        """Si le snippet n'a pas pu tourner, on ne conclut pas — c'est tout le
        point d'un marqueur explicite plutot qu'un code de retour."""
        for sortie in ("", "Traceback (most recent call last):\n  ...", None):
            ok, message = lvo.juger_verdict(sortie)
            self.assertFalse(ok)
            self.assertIn("verdict introuvable", message)

    def test_verdict_illisible_ne_vaut_pas_succes(self):
        ok, message = lvo.juger_verdict("RESULTAT_E4 {pas du json")
        self.assertFalse(ok)
        self.assertIn("illisible", message)


class TestTransfertSansDrive(unittest.TestCase):
    """Le mode qui supprime le consentement Drive, donc l'humain.

    Ce qui est teste ici, c'est ce qui decide de ce que la VM verra : un
    fichier oublie par `plan_transfert` ne se verrait qu'au milieu d'un run,
    dans un message de cellule, apres plusieurs minutes de GPU.
    """

    def _profil_voix(self, racine, nom="voix_principale", versions=(1,)):
        for v in versions:
            d = Path(racine) / "00_Profil" / "voix" / nom / f"v{v}"
            d.mkdir(parents=True, exist_ok=True)
            (d / "ref.wav").write_bytes(b"RIFF")
            (d / "ref.txt").write_text("texte lu", encoding="utf-8")

    def test_plan_complet(self):
        with tempfile.TemporaryDirectory() as tmp:
            dossier = _ecrire_video(tmp, "2026-09-16_v01", "attente_franco")
            (dossier / "03_script_tts.txt").write_text("phrase", encoding="utf-8")
            self._profil_voix(tmp)
            entrees, manquants = lvo.plan_transfert(tmp, "2026-09-16_v01",
                                                    "voix_principale", "/content/CY")
            self.assertEqual(manquants, [])
            distants = [d for _, d in entrees]
            self.assertIn("/content/CY/videos/2026-09-16_v01/state.json", distants)
            self.assertIn("/content/CY/videos/2026-09-16_v01/03_script_tts.txt", distants)
            self.assertIn("/content/CY/00_Profil/voix/voix_principale/v1/ref.wav", distants)
            self.assertIn("/content/CY/00_Profil/voix/voix_principale/v1/ref.txt", distants)

    def test_derniere_version_de_voix_choisie(self):
        """Meme regle que la Cell 2 du notebook : le plus grand vN gagne."""
        with tempfile.TemporaryDirectory() as tmp:
            dossier = _ecrire_video(tmp, "v1", "attente_franco")
            (dossier / "03_script_tts.txt").write_text("x", encoding="utf-8")
            self._profil_voix(tmp, versions=(1, 2, 10))
            self.assertEqual(lvo.version_voix(tmp, "voix_principale"), 10)
            entrees, _ = lvo.plan_transfert(tmp, "v1", "voix_principale", "/r")
            self.assertTrue(any("/v10/ref.wav" in d for _, d in entrees))

    def test_script_manquant_refuse_avant_tout_gpu(self):
        with tempfile.TemporaryDirectory() as tmp:
            _ecrire_video(tmp, "v1", "attente_franco")
            self._profil_voix(tmp)
            _, manquants = lvo.plan_transfert(tmp, "v1", "voix_principale", "/r")
            self.assertTrue(any("03_script_tts.txt" in m for m in manquants))

    def test_profil_de_voix_absent_refuse(self):
        with tempfile.TemporaryDirectory() as tmp:
            dossier = _ecrire_video(tmp, "v1", "attente_franco")
            (dossier / "03_script_tts.txt").write_text("x", encoding="utf-8")
            _, manquants = lvo.plan_transfert(tmp, "v1", "voix_principale", "/r")
            self.assertTrue(any("aucun profil de voix" in m for m in manquants))

    def test_sans_drive_et_reprendre_s_excluent(self):
        """`main` rend un code, il ne leve pas : c'est `sys.exit(main())` qui
        sort. Le refus doit arriver avant toute allocation de GPU."""
        self.assertEqual(lvo.main(["--root", "/x", "--sans-drive", "--reprendre"]), 2)


class TestFusionState(unittest.TestCase):
    """Rapatrier le state.json de la VM tel quel ecraserait ce que
    l'Orchestrateur aurait ecrit pendant le run. Le §4.2 dit qu'une etape ne
    touche qu'a elle-meme ; la regle vaut aussi pour le transfert."""

    def _ecrire(self, chemin, etapes, historique=()):
        Path(chemin).write_text(json.dumps(
            {"video_id": "v1", "etapes": etapes, "historique": list(historique)}),
            encoding="utf-8")

    def test_les_autres_etapes_survivent(self):
        with tempfile.TemporaryDirectory() as tmp:
            local, distant = Path(tmp) / "local.json", Path(tmp) / "vm.json"
            # L'Orchestrateur a fait avancer E5 pendant le run audio.
            self._ecrire(local, {"E4_audio": {"statut": "en_cours"},
                                 "E5_storyboard": {"statut": "termine"}})
            # La VM ne connait que l'etat d'avant pour E5.
            self._ecrire(distant, {"E4_audio": {"statut": "termine"},
                                   "E5_storyboard": {"statut": "a_venir"}})
            lvo.fusionner_state(local, distant)
            fusionne = json.loads(local.read_text(encoding="utf-8"))
            self.assertEqual(fusionne["etapes"]["E4_audio"]["statut"], "termine")
            self.assertEqual(fusionne["etapes"]["E5_storyboard"]["statut"], "termine")

    def test_historique_neuf_ajoute_sans_doublon(self):
        with tempfile.TemporaryDirectory() as tmp:
            local, distant = Path(tmp) / "local.json", Path(tmp) / "vm.json"
            self._ecrire(local, {"E4_audio": {}}, [{"evenement": "cree"}])
            self._ecrire(distant, {"E4_audio": {}},
                         [{"evenement": "cree"}, {"evenement": "en_cours"},
                          {"evenement": "termine"}])
            lvo.fusionner_state(local, distant)
            h = json.loads(local.read_text(encoding="utf-8"))["historique"]
            self.assertEqual([e["evenement"] for e in h], ["cree", "en_cours", "termine"])

    def test_state_local_absent_recopie(self):
        with tempfile.TemporaryDirectory() as tmp:
            local, distant = Path(tmp) / "local.json", Path(tmp) / "vm.json"
            self._ecrire(distant, {"E4_audio": {"statut": "termine"}})
            lvo.fusionner_state(local, distant)
            self.assertEqual(json.loads(local.read_text(encoding="utf-8"))
                             ["etapes"]["E4_audio"]["statut"], "termine")


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
