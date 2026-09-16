"""
Teste agents/short-monteur/scripts/construire_props.py : assemblage des props
Remotion et normalisation de 04_timestamps.json quel que soit son format
(§13 etape 5).
"""

import json
import os
import subprocess
import sys
import tempfile
import unittest

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCRIPT = os.path.join(REPO_ROOT, "agents", "short-monteur", "scripts", "construire_props.py")
sys.path.insert(0, os.path.join(REPO_ROOT, "agents", "short-monteur", "scripts"))
import construire_props  # noqa: E402


class TestNormaliserMots(unittest.TestCase):
    def test_convention_faster_whisper(self):
        mots = construire_props.normaliser_mots([{"word": "hello", "start": 0.1, "end": 0.4}])
        self.assertEqual(mots, [{"mot": "hello", "debut_s": 0.1, "fin_s": 0.4}])

    def test_convention_francaise_enveloppee(self):
        mots = construire_props.normaliser_mots({"mots": [{"mot": "salut", "debut_s": 0, "fin_s": 0.3}]})
        self.assertEqual(mots, [{"mot": "salut", "debut_s": 0.0, "fin_s": 0.3}])

    def test_ignore_entrees_incompletes(self):
        mots = construire_props.normaliser_mots([{"word": "x"}, {"word": "y", "start": 0, "end": 1}])
        self.assertEqual(len(mots), 1)


class TestConstruire(unittest.TestCase):
    def test_leve_une_erreur_si_aucune_scene(self):
        with self.assertRaises(ValueError):
            construire_props.construire({}, {"scenes": []}, [])


class TestScriptCLI(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp(prefix="props_test_")

    def tearDown(self):
        import shutil
        shutil.rmtree(self.tmp, ignore_errors=True)

    def _ecrire(self, nom, data):
        chemin = os.path.join(self.tmp, nom)
        with open(chemin, "w", encoding="utf-8") as f:
            json.dump(data, f)
        return chemin

    def test_assemble_un_props_json_valide(self):
        charte = self._ecrire("charte.json", {"couleurs": {"fond": "#000"}})
        storyboard = self._ecrire("storyboard.json", {
            "scenes": [{"id": "s1", "composant": "TitleCard", "duree_s": 3, "params": {"texte": "Hi"}}]
        })
        timestamps = self._ecrire("timestamps.json", [{"word": "Hi", "start": 0, "end": 0.3}])
        sortie = os.path.join(self.tmp, "props.json")

        p = subprocess.run([sys.executable, SCRIPT, "--charte", charte, "--storyboard", storyboard,
                             "--timestamps", timestamps, "--sortie", sortie],
                            capture_output=True, text=True)
        self.assertEqual(p.returncode, 0, p.stderr)
        resultat = json.loads(p.stdout)
        self.assertTrue(resultat["ok"])
        self.assertEqual(resultat["nb_scenes"], 1)
        self.assertEqual(resultat["nb_mots"], 1)

        with open(sortie, encoding="utf-8") as f:
            props = json.load(f)
        self.assertEqual(props["scenes"][0]["composant"], "TitleCard")
        self.assertEqual(props["mots"][0]["mot"], "Hi")


CHARTE_SHORT = {"couleurs": {}, "format": {"largeur_px": 1080, "hauteur_px": 1920, "fps": 30}}


class TestAppliquerFormat(unittest.TestCase):
    """Les dimensions de composition suivent le format de la video.

    `Root.tsx` lit `props.charte.format` et rien d'autre : un format long
    rendu avec la charte telle quelle sortirait en 1080x1920, c'est-a-dire du
    paysage compose dans un cadre vertical.
    """

    def test_le_short_garde_sa_charte_intacte(self):
        charte, avert = construire_props.appliquer_format(CHARTE_SHORT, "short")
        self.assertEqual(charte["format"], CHARTE_SHORT["format"])
        self.assertEqual(avert, [])

    def test_le_long_bascule_en_paysage(self):
        charte, avert = construire_props.appliquer_format(CHARTE_SHORT, "long")
        self.assertEqual(charte["format"]["largeur_px"], 1920)
        self.assertEqual(charte["format"]["hauteur_px"], 1080)
        self.assertTrue(avert, "la deduction par rotation doit etre signalee")

    def test_le_long_garde_le_fps_et_la_resolution_de_franco(self):
        # Une charte reglee en 1440x2560 a 60 fps ne doit pas se faire
        # remplacer par les valeurs par defaut du code : on la tourne.
        charte, _ = construire_props.appliquer_format(
            {"format": {"largeur_px": 1440, "hauteur_px": 2560, "fps": 60}}, "long")
        self.assertEqual(charte["format"], {"largeur_px": 2560, "hauteur_px": 1440, "fps": 60})

    def test_le_bloc_formats_de_la_charte_a_la_priorite(self):
        # Le seul moyen pour Franco de choisir autre chose que la rotation,
        # sans toucher au code.
        charte, avert = construire_props.appliquer_format(
            {**CHARTE_SHORT, "formats": {"long": {"largeur_px": 2560, "hauteur_px": 1440, "fps": 25}}},
            "long")
        self.assertEqual(charte["format"]["largeur_px"], 2560)
        self.assertEqual(charte["format"]["fps"], 25)
        self.assertEqual(avert, [])

    def test_la_charte_d_entree_n_est_pas_modifiee(self):
        avant = json.loads(json.dumps(CHARTE_SHORT))
        construire_props.appliquer_format(CHARTE_SHORT, "long")
        self.assertEqual(CHARTE_SHORT, avant)

    def test_le_storyboard_porte_le_format_quand_l_appelant_se_tait(self):
        props, _ = construire_props.construire(
            CHARTE_SHORT,
            {"format_video": "long", "scenes": [{"id": "s1", "composant": "TitleCard",
                                                 "duree_s": 1, "params": {}}]},
            [])
        self.assertEqual(props["format_video"], "long")
        self.assertEqual(props["charte"]["format"]["largeur_px"], 1920)


def _phrases(*bornes):
    return [{"debut_s": d, "fin_s": f} for d, f in bornes]


class TestResoudreInserts(unittest.TestCase):
    """Un insert est un intervalle dans une scene, designe par une phrase.

    Meme mecanique que `pulsation_s` (un instant), avec une borne de plus.
    """

    RESSOURCES = {"demo": {"type": "broll", "src": "/public/x.mp4", "duree_s": 4.0}}

    def scene(self, **surcharges):
        base = {"id": "s1", "composant": "TitleCard", "duree_s": 10.0,
                "params": {}, "phrases": [1, 2, 3]}
        base.update(surcharges)
        return base

    def test_une_phrase_devient_un_instant(self):
        scenes, avert = construire_props.resoudre_inserts(
            [self.scene(inserts=[{"cle": "demo", "debut": "sur la phrase 2"}])],
            _phrases((0.0, 2.0), (2.0, 5.0), (5.0, 10.0)), self.RESSOURCES)
        self.assertEqual(scenes[0]["inserts"][0]["debut_s"], 2.0)
        # Duree absente : celle du clip fait foi.
        self.assertEqual(scenes[0]["inserts"][0]["duree_s"], 4.0)
        self.assertEqual(avert, [])

    def test_le_debut_se_compte_depuis_le_debut_de_la_scene(self):
        # Deuxieme scene : la phrase 3 commence a 5 s dans la video, donc a
        # 1 s dans une scene qui demarre a 4 s.
        scenes, _ = construire_props.resoudre_inserts(
            [self.scene(duree_s=4.0, phrases=[1, 2]),
             self.scene(id="s2", duree_s=6.0, phrases=[3],
                        inserts=[{"cle": "demo", "debut": "phrase 3"}])],
            _phrases((0.0, 2.0), (2.0, 4.0), (5.0, 10.0)), self.RESSOURCES)
        self.assertEqual(scenes[1]["inserts"][0]["debut_s"], 1.0)

    def test_un_insert_ne_deborde_jamais_de_sa_scene(self):
        scenes, avert = construire_props.resoudre_inserts(
            [self.scene(duree_s=5.0, inserts=[{"cle": "demo", "debut_s": 3.0, "duree_s": 9.0}])],
            [], self.RESSOURCES)
        self.assertEqual(scenes[0]["inserts"][0]["duree_s"], 2.0)
        self.assertTrue(any("raccourci" in a for a in avert))

    def test_une_ressource_absente_retire_l_insert(self):
        # La scene animee reste valide sans lui ; une URL vide produirait un
        # trou noir au milieu du cadre.
        scenes, avert = construire_props.resoudre_inserts(
            [self.scene(inserts=[{"cle": "jamais_resolue", "debut_s": 1.0}])], [], {})
        self.assertNotIn("inserts", scenes[0])
        self.assertTrue(any("jamais_resolue" in a for a in avert))

    def test_une_phrase_hors_de_la_scene_est_refusee(self):
        # Elle tomberait pendant une autre scene : l'insert ne serait jamais
        # vu, ou vu au mauvais moment.
        scenes, avert = construire_props.resoudre_inserts(
            [self.scene(phrases=[1, 2], inserts=[{"cle": "demo", "debut": "phrase 9"}])],
            _phrases(*[(float(i), float(i + 1)) for i in range(12)]), self.RESSOURCES)
        self.assertNotIn("inserts", scenes[0])
        self.assertTrue(any("hors des phrases couvertes" in a for a in avert))

    def test_une_scene_sans_insert_traverse_sans_etre_touchee(self):
        scene = self.scene()
        scenes, avert = construire_props.resoudre_inserts([scene], [], self.RESSOURCES)
        self.assertEqual(scenes[0], scene)
        self.assertEqual(avert, [])

    def test_un_insert_ne_change_ni_la_duree_ni_les_phrases(self):
        # C'est la garantie qui protege le recalage : un detail *dans* une
        # scene ne doit pas deplacer les bornes de la scene.
        scenes, _ = construire_props.resoudre_inserts(
            [self.scene(inserts=[{"cle": "demo", "debut_s": 1.0}])],
            _phrases((0.0, 2.0), (2.0, 5.0), (5.0, 10.0)), self.RESSOURCES)
        self.assertEqual(scenes[0]["duree_s"], 10.0)
        self.assertEqual(scenes[0]["phrases"], [1, 2, 3])


if __name__ == "__main__":
    unittest.main()
