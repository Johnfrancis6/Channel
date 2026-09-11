"""
Teste outils/analyser_transcription.py : segmentation et mesure d'une video.

Ce que faisait A3 avant : une note en prose libre INDEXEE PAR CHAINE,
recopiee telle quelle dans le rapport. Le hook, le CTA et le rythme sont
des proprietes d'UNE video ; de la prose ne se mesure ni ne s'agrege ; et
le rapport hebdo etant un fichier neuf chaque semaine, rien ne
s'accumulait. Un systeme qui n'accumule rien ne peut rien apprendre.

Separation des roles : le LLM segmente (jugement), le script compte.
"""
import json
import os
import shutil
import sys
import tempfile
import unittest

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(REPO_ROOT, "outils"))

import analyser_transcription as at  # noqa: E402


def segment(i, role, texte, debut=None, fin=None):
    s = {"index": i, "role": role, "texte": texte}
    if debut is not None:
        s["debut_s"], s["fin_s"] = debut, fin
    return s


SEGMENTATION = {
    "video_id": "v1", "chaine": "UC1", "titre": "Une video", "vues": 12000, "duree_s": 50.0,
    "segments": [
        segment(1, "hook", "Everyone calls this an agent now.", 0.0, 3.0),
        segment(2, "promesse", "You will know the real difference.", 3.2, 6.0),
        segment(3, "idee", "A plain model answers once and stops.", 6.2, 16.0),
        segment(4, "idee", "A workflow has tools but a fixed path.", 16.2, 30.0),
        segment(5, "exemple", "Claude edits code on GitHub by itself.", 30.2, 44.0),
        segment(6, "cta", "Who controls the loop?", 44.2, 50.0),
    ],
}


class TestValidation(unittest.TestCase):
    def test_segmentation_complete_acceptee(self):
        self.assertEqual(at.valider(SEGMENTATION), [])

    def test_role_manquant_refuse(self):
        s = json.loads(json.dumps(SEGMENTATION))
        s["segments"][2]["role"] = None
        self.assertTrue(any("role non renseigne" in p for p in at.valider(s)))

    def test_role_hors_vocabulaire_refuse(self):
        # Un role invente rend la ligne incomparable aux autres : c'est le
        # retour a la prose par une autre porte.
        s = json.loads(json.dumps(SEGMENTATION))
        s["segments"][0]["role"] = "accroche_choc"
        problemes = at.valider(s)
        self.assertTrue(any("role inconnu" in p for p in problemes))

    def test_hook_en_deux_phrases_accepte(self):
        # Forme reelle du script de 2026-09-11_v01 : "Everyone calls their
        # product an AI agent now." / "Most of them are not agents at all."
        # Un hook en deux temps est une figure classique, pas une erreur.
        s = json.loads(json.dumps(SEGMENTATION))
        s["segments"][1]["role"] = "hook"
        self.assertEqual(at.valider(s), [])

    def test_hook_disperse_refuse(self):
        # Deux hooks separes dans la video, en revanche, signalent bien une
        # segmentation douteuse.
        s = json.loads(json.dumps(SEGMENTATION))
        s["segments"][4]["role"] = "hook"
        self.assertTrue(any("disperses" in p for p in at.valider(s)))

    def test_duree_manquante_refusee(self):
        s = json.loads(json.dumps(SEGMENTATION))
        s["duree_s"] = None
        self.assertTrue(any("duree_s" in p for p in at.valider(s)))

    def test_aucun_segment(self):
        self.assertEqual(at.valider({"segments": [], "duree_s": 10}), ["aucun segment"])


class TestMesures(unittest.TestCase):
    def setUp(self):
        self.m = at.mesurer(SEGMENTATION)

    def test_hook_mesure_sur_les_bornes_reelles(self):
        self.assertEqual(self.m["hook_duree_s"], 3.0)

    def test_les_idees_contigues_comptent_pour_une(self):
        # Deux phrases qui se suivent developpent la meme idee. Sur
        # 2026-09-11_v01, les trois idees du script occupent douze phrases :
        # compter les segments donnait "12 idees" pour un budget de 3.
        self.assertEqual(self.m["nb_idees"], 1)
        self.assertEqual(self.m["nb_segments_idee"], 2)

    def test_le_champ_groupe_separe_les_idees(self):
        s = json.loads(json.dumps(SEGMENTATION))
        s["segments"][2]["groupe"] = 1
        s["segments"][3]["groupe"] = 2
        m = at.mesurer(s)
        self.assertEqual(m["nb_idees"], 2)

    def test_deux_blocs_separes_comptent_pour_deux(self):
        s = json.loads(json.dumps(SEGMENTATION))
        # idee / exemple / idee -> deux blocs distincts
        s["segments"][3]["role"] = "exemple"
        s["segments"][4]["role"] = "idee"
        m = at.mesurer(s)
        self.assertEqual(m["nb_idees"], 2)

    def test_cta_detecte_et_situe(self):
        self.assertTrue(self.m["cta_present"])
        # Dernier segment sur six : le CTA est en fin de video.
        self.assertEqual(self.m["cta_position_pct"], 100)

    def test_sponsoring_absent(self):
        self.assertFalse(self.m["sponsoring_present"])

    def test_debit_coherent(self):
        self.assertAlmostEqual(self.m["mots_par_seconde"],
                               self.m["mots_total"] / 50.0, places=2)

    def test_cout_total_par_idee_inclut_l_enveloppe(self):
        # Le budget de A5 se compare a CETTE valeur, pas a mots_par_idee :
        # sur 2026-09-11_v01, les trois idees pesent 115 mots sur 231, le
        # reste etant hook, promesse, exemple et CTA.
        self.assertEqual(self.m["cout_total_par_idee"], self.m["mots_total"] // self.m["nb_idees"])
        self.assertGreater(self.m["cout_total_par_idee"], self.m["mots_par_idee_moyen"])

    def test_repartition_en_pourcentage(self):
        total = sum(self.m["repartition_roles_pct"].values())
        self.assertAlmostEqual(total, 100, delta=2)

    def test_sans_timings_la_duree_est_estimee_au_prorata(self):
        # Cas d'une transcription de concurrent : pas de bornes, mais une
        # estimation vaut mieux que rien — elle est marquee comme telle par
        # l'absence de debut_s dans la source.
        sans = json.loads(json.dumps(SEGMENTATION))
        for s in sans["segments"]:
            s.pop("debut_s", None)
            s.pop("fin_s", None)
        m = at.mesurer(sans)
        self.assertGreater(m["hook_duree_s"], 0)
        self.assertLess(m["hook_duree_s"], sans["duree_s"])


class TestGabarit(unittest.TestCase):
    def test_une_phrase_par_ligne(self):
        g = at.gabarit(["Une phrase.", "Une autre."], duree_totale=10)
        self.assertEqual(len(g["segments"]), 2)
        self.assertIsNone(g["segments"][0]["role"])

    def test_le_vocabulaire_est_rappele(self):
        g = at.gabarit(["x"], duree_totale=5)
        self.assertEqual(g["roles_possibles"], list(at.ROLES))

    def test_les_bornes_sont_reprises(self):
        g = at.gabarit(["a", "b"], bornes=[{"debut_s": 0, "fin_s": 2},
                                            {"debut_s": 2.2, "fin_s": 5}], duree_totale=5)
        self.assertEqual(g["segments"][1]["debut_s"], 2.2)

    def test_decoupage_par_ponctuation_si_un_seul_bloc(self):
        phrases = at.decouper_phrases("Premiere phrase. Deuxieme phrase !")
        self.assertEqual(len(phrases), 2)


class TestCorpus(unittest.TestCase):
    def setUp(self):
        self.dir = tempfile.mkdtemp(prefix="corpus_")
        self.corpus = os.path.join(self.dir, "sous", "corpus_structures.jsonl")

    def tearDown(self):
        shutil.rmtree(self.dir, ignore_errors=True)

    def test_append_only(self):
        # Le corpus est le seul actif qui prend de la valeur avec le temps :
        # on n'y reecrit jamais une ligne passee.
        at.ajouter_au_corpus(self.corpus, {"video_id": "a"})
        at.ajouter_au_corpus(self.corpus, {"video_id": "b"})
        with open(self.corpus, encoding="utf-8") as f:
            lignes = [json.loads(l) for l in f if l.strip()]
        self.assertEqual([l["video_id"] for l in lignes], ["a", "b"])

    def test_dossier_cree_au_besoin(self):
        at.ajouter_au_corpus(self.corpus, {"video_id": "a"})
        self.assertTrue(os.path.isfile(self.corpus))


if __name__ == "__main__":
    unittest.main()
