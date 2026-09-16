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

sys.path.insert(0, os.path.dirname(SCRIPT))
import generer_storyboard  # noqa: E402


def _duree_attendue(nb_mots):
    """Meme calcul que le script, depuis ses constantes.

    Le debit se recalibre sur les runs reels (2,5 -> 3,2 apres la premiere
    video) : un test qui code la valeur en dur casserait a chaque
    ajustement et pousserait a figer une constante fausse.
    """
    return round(max(nb_mots / generer_storyboard.MOTS_PAR_SECONDE,
                     generer_storyboard.DUREE_MIN_S), 1)


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
        _creer_script_tts(self.root, video_id, [
            "un deux trois quatre cinq six sept huit neuf dix",
            "un deux trois quatre cinq",
        ])

        code, data = _executer(self.root, video_id)
        self.assertEqual(code, 0)

        chemin_json = os.path.join(self.root, "videos", video_id, "05_storyboard.json")
        with open(chemin_json, encoding="utf-8") as f:
            storyboard = json.load(f)
        self.assertEqual(storyboard["scenes"][0]["duree_s"], _duree_attendue(10))
        self.assertEqual(storyboard["scenes"][1]["duree_s"], _duree_attendue(5))
        # La duree doit suivre le nombre de mots, pas etre constante.
        self.assertGreater(storyboard["scenes"][0]["duree_s"],
                           storyboard["scenes"][1]["duree_s"])

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


class TestDecoupageFormatLong(unittest.TestCase):
    """Le squelette d'un format long groupe les phrases en scenes de segment.

    « Une scene par phrase » tient sur 24 phrases et casse sur 280 : le
    livrable remis a A6 serait 280 scenes `a_completer` a trancher une par
    une. Il ne le ferait pas — il en sauterait — et A7 monterait a l'aveugle.
    """

    def phrases(self, n, mots=14):
        return [" ".join(["mot"] * mots) + "." for _ in range(n)]

    def test_le_short_garde_une_scene_par_phrase(self):
        # Le format long est un ajout : la regle du Short ne bouge pas.
        groupes = generer_storyboard.grouper_phrases(self.phrases(24), None)
        self.assertEqual(groupes, [[i] for i in range(24)])

    def test_le_long_groupe_vers_la_duree_cible(self):
        # 14 mots a 2,8 mots/s = 5 s par phrase, cible 12 s -> 3 phrases.
        groupes = generer_storyboard.grouper_phrases(self.phrases(30), 12.0)
        self.assertLess(len(groupes), 30)
        self.assertTrue(all(len(g) >= 2 for g in groupes[:-1]))

    def test_toutes_les_phrases_sont_couvertes_une_seule_fois(self):
        # La garantie qui compte : une phrase oubliee, c'est un trou a
        # l'image pendant que la voix off continue ; une phrase en double,
        # c'est un recalage incoherent au montage.
        for n in (1, 2, 7, 53, 280):
            groupes = generer_storyboard.grouper_phrases(self.phrases(n), 12.0)
            couvertes = [i for g in groupes for i in g]
            self.assertEqual(couvertes, list(range(n)), f"{n} phrases")

    def test_le_plafond_de_scenes_est_tenu(self):
        # Un script inattendu (600 phrases) ne doit pas franchir le plafond :
        # on elargit les scenes, on ne tronque jamais.
        groupes = generer_storyboard.grouper_phrases(self.phrases(600), 12.0, scenes_max=120)
        self.assertLessEqual(len(groupes), 120)
        self.assertEqual([i for g in groupes for i in g], list(range(600)))

    def test_les_scenes_portent_les_numeros_de_phrases(self):
        # C'est `phrases` qui permet le recalage sur 04_phrases.json quand
        # une scene en couvre plusieurs (§8) — sans lui, pas de recalage.
        scenes, _ = generer_storyboard.construire_scenes(
            self.phrases(20), ["TitleCard"], {"mouvement": "fondu"}, "long")
        self.assertLess(len(scenes), 20)
        couvertes = [n for s in scenes for n in s["phrases"]]
        self.assertEqual(couvertes, list(range(1, 21)))

    def test_la_duree_d_une_scene_est_la_somme_de_ses_phrases(self):
        scenes, _ = generer_storyboard.construire_scenes(
            self.phrases(20), ["TitleCard"], {"mouvement": "fondu"}, "long")
        attendue = _duree_attendue(14)
        for s in scenes:
            self.assertAlmostEqual(s["duree_s"], round(attendue * len(s["phrases"]), 1),
                                   places=1)

    def test_le_format_short_par_defaut_ne_change_rien(self):
        # Toute video anterieure au 16/09/2026 passe par ce chemin.
        avec, _ = generer_storyboard.construire_scenes(
            self.phrases(10), ["TitleCard"], {"mouvement": "fondu"}, "short")
        sans, _ = generer_storyboard.construire_scenes(
            self.phrases(10), ["TitleCard"], {"mouvement": "fondu"})
        self.assertEqual(avec, sans)
        self.assertEqual(len(sans), 10)


class TestStoryboardLongDeBoutEnBout(unittest.TestCase):
    def setUp(self):
        self.root = tempfile.mkdtemp(prefix="chaine_yt_sb_long_")
        self.video = "2026-01-01_v01"
        dossier = os.path.join(self.root, "videos", self.video)
        os.makedirs(dossier)
        phrases = [" ".join(["mot"] * 14) + "." for _ in range(150)]
        with open(os.path.join(dossier, "03_script_tts.txt"), "w", encoding="utf-8") as f:
            f.write("\n".join(phrases))
        with open(os.path.join(dossier, "state.json"), "w", encoding="utf-8") as f:
            json.dump({"video_id": self.video, "format_video": "long"}, f)

    def tearDown(self):
        shutil.rmtree(self.root, ignore_errors=True)

    def lancer(self, *args):
        proc = subprocess.run(
            [sys.executable, SCRIPT, "--video", self.video, "--root", self.root,
             "--sortie-md", f"videos/{self.video}/05_storyboard.md",
             "--sortie-json", f"videos/{self.video}/05_storyboard.json", *args],
            capture_output=True, text=True)
        return proc.returncode, json.loads(proc.stdout)

    def storyboard(self):
        with open(os.path.join(self.root, "videos", self.video, "05_storyboard.json"),
                  encoding="utf-8") as f:
            return json.load(f)

    def test_le_format_est_lu_dans_le_state(self):
        # Le Designer n'a rien a passer : le format appartient a la video.
        code, out = self.lancer()
        self.assertEqual(code, 0, out)
        self.assertEqual(out["format_video"], "long")
        self.assertLess(out["nb_scenes"], out["nb_phrases"])
        self.assertEqual(self.storyboard()["format_video"], "long")

    def test_l_option_surcharge_le_state(self):
        code, out = self.lancer("--format-video", "short")
        self.assertEqual(code, 0, out)
        self.assertEqual(out["nb_scenes"], 150)

    def test_le_md_liste_les_phrases_de_chaque_scene(self):
        # A6 designe un accent par numero de phrase : le .md doit donc
        # montrer ces numeros, sinon il ne peut en designer aucun.
        self.lancer()
        with open(os.path.join(self.root, "videos", self.video, "05_storyboard.md"),
                  encoding="utf-8") as f:
            md = f.read()
        self.assertIn("Format : **long**", md)
        self.assertIn("1. ", md)
        self.assertRegex(md, r"phrases \d+ a \d+")


if __name__ == "__main__":
    unittest.main()
