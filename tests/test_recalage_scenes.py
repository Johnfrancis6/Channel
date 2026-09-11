"""
Teste le recalage des durees de scenes sur l'audio reel (04_phrases.json).

Sans ce recalage, A6 estimait les durees a ~2.5 mots/s et A7 les passait
telles quelles a Remotion : le visuel derivait de la voix off des la
premiere phrase mal estimee, et la composition pouvait se terminer avant
l'audio (voix coupee) ou apres (ecran fixe en fin de video).
"""
import os
import sys
import unittest

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(REPO_ROOT, "agents", "short-monteur", "scripts"))

import construire_props  # noqa: E402


def scenes(*durees):
    return [{"id": f"s{i + 1}", "composant": "TitleCard", "duree_s": d, "params": {}}
            for i, d in enumerate(durees)]


def phrases(*bornes, duree_totale=None):
    return {
        "phrases": [{"index": i + 1, "texte": f"p{i + 1}", "debut_s": d, "fin_s": f}
                    for i, (d, f) in enumerate(bornes)],
        "duree_totale_s": duree_totale if duree_totale is not None else bornes[-1][1],
    }


class TestRecalageScenes(unittest.TestCase):
    def test_durees_calees_sur_les_bornes_de_phrases(self):
        recalees, duree, avertissements = construire_props.recaler_scenes(
            scenes(3.0, 3.0), phrases((0.0, 2.4), (2.65, 5.1)))
        self.assertEqual(avertissements, [])
        self.assertEqual([s["duree_s"] for s in recalees], [2.4, 2.7])
        self.assertEqual(duree, 5.1)

    def test_les_scenes_couvrent_tout_l_audio_sans_trou(self):
        # La pause inter-phrases (250 ms par defaut) est absorbee par la
        # scene suivante : deux scenes qui ne se touchent pas laisseraient
        # un trou noir a l'image a chaque respiration.
        recalees, duree, _ = construire_props.recaler_scenes(
            scenes(1.0, 1.0, 1.0), phrases((0.0, 2.0), (2.25, 4.0), (4.25, 6.0), duree_totale=6.4))
        self.assertAlmostEqual(sum(s["duree_s"] for s in recalees), duree, places=3)

    def test_derniere_scene_prolongee_jusqu_au_bout_de_l_audio(self):
        recalees, _, _ = construire_props.recaler_scenes(
            scenes(1.0, 1.0), phrases((0.0, 2.0), (2.25, 4.0), duree_totale=4.6))
        self.assertEqual(recalees[-1]["duree_s"], 2.6)

    def test_duree_du_storyboard_conservee_pour_comparaison(self):
        recalees, _, _ = construire_props.recaler_scenes(
            scenes(9.0), phrases((0.0, 2.0)))
        self.assertEqual(recalees[0]["duree_s_storyboard"], 9.0)

    def test_desaccord_de_nombre_ne_recale_rien(self):
        # Un appariement par index decalerait tout le montage : on prefere
        # l'estimation du storyboard, avec un avertissement visible.
        originales = scenes(3.0, 3.0, 3.0)
        recalees, _, avertissements = construire_props.recaler_scenes(
            originales, phrases((0.0, 2.0), (2.25, 4.0)))
        self.assertEqual(recalees, originales)
        self.assertTrue(avertissements)
        self.assertIn("2 phrases pour 3 scenes", avertissements[0])

    def test_phrases_vides_ne_recale_rien(self):
        originales = scenes(3.0)
        recalees, _, avertissements = construire_props.recaler_scenes(
            originales, {"phrases": [], "duree_totale_s": None})
        self.assertEqual(recalees, originales)
        self.assertTrue(avertissements)


class TestConstruireAvecPhrases(unittest.TestCase):
    def test_duree_audio_exposee_aux_props(self):
        props, avertissements = construire_props.construire(
            {"couleurs": {}}, {"scenes": scenes(3.0)}, [], None, phrases((0.0, 2.2)))
        self.assertEqual(props["duree_audio_s"], 2.2)
        self.assertEqual(avertissements, [])

    def test_sans_phrases_l_agent_est_averti(self):
        props, avertissements = construire_props.construire(
            {"couleurs": {}}, {"scenes": scenes(3.0)}, [])
        self.assertNotIn("duree_audio_s", props)
        self.assertTrue(avertissements)
        self.assertIn("estimations", avertissements[0])


if __name__ == "__main__":
    unittest.main()
