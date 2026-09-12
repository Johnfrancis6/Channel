"""
Teste agents/short-amelioration/scripts/rassembler_inputs.py (§4.3, H1).

Deux choses distinctes s'y verifient :

- le **listage** des fichiers recents, qui existait deja ;
- les **indicateurs** tires des `state.json`. Le cas de reference est celui
  du 11/09/2026 : huit tentatives sur E4_audio, alerte levee, personne
  n'ayant rien vu. Ce que H1 ne mesure pas, H1 ne le trouve pas.
"""

import json
import os
import shutil
import sys
import tempfile
import time
import unittest

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(REPO_ROOT, "agents", "short-amelioration", "scripts"))
import rassembler_inputs  # noqa: E402


def _etape(statut="termine", tentatives=1, **extra):
    base = {"agent": "x", "statut": statut, "tentatives": tentatives,
            "debut": None, "fin": None, "sorties": []}
    base.update(extra)
    return base


def _state(video_id="2026-09-10_v01", **extra):
    state = {
        "version_schema": 1, "video_id": video_id, "cree_le": "2026-09-10T08:00:00Z",
        "cree_par": "new_short", "statut_global": "en_production",
        "etape_actuelle": "E4_audio", "consignes": {"format": "interview_fictive"},
        "etapes": {}, "historique": [],
    }
    state.update(extra)
    return state


class TestListage(unittest.TestCase):
    def setUp(self):
        self.root = tempfile.mkdtemp(prefix="h1_test_")

    def tearDown(self):
        shutil.rmtree(self.root, ignore_errors=True)

    def _creer(self, relatif, contenu="contenu", ancien=False):
        chemin = os.path.join(self.root, *relatif.split("/"))
        os.makedirs(os.path.dirname(chemin), exist_ok=True)
        with open(chemin, "w", encoding="utf-8") as f:
            f.write(contenu)
        if ancien:
            vieux = time.time() - 30 * 86400
            os.utime(chemin, (vieux, vieux))
        return chemin

    def test_liste_les_fichiers_recents_et_ignore_les_anciens(self):
        self._creer("videos/2026-09-10_v01/checkpoints/rapport_CP1.md")
        self._creer("videos/2026-09-10_v01/03_rapport_metriques.md")
        self._creer("videos/2026-09-10_v01/04_rapport_audio.md")
        self._creer("videos/2026-08-01_v01/checkpoints/rapport_CP1.md", ancien=True)
        self._creer("03_Amelioration/analytics/export.csv")

        resultat = rassembler_inputs.rassembler(self.root, jours=7)

        self.assertEqual(len(resultat["checkpoints"]), 1)
        self.assertIn("2026-09-10_v01", resultat["checkpoints"][0])
        self.assertEqual(len(resultat["metriques_filtre"]), 1)
        self.assertEqual(len(resultat["rapports_audio"]), 1)
        self.assertEqual(len(resultat["analytics_csv"]), 1)

    def test_les_rapports_refuses_archives_sont_listes(self):
        # C'est la trace la plus directe de ce que Franco a rejete ;
        # archivee dans refuses/, elle n'etait pas ramassee.
        self._creer("videos/2026-09-10_v01/checkpoints/refuses/rapport_CP2_2026-09-10.md")
        resultat = rassembler_inputs.rassembler(self.root, jours=7)
        self.assertEqual(len(resultat["checkpoints"]), 1)
        self.assertIn("refuses", resultat["checkpoints"][0])

    def test_le_corpus_et_le_suivi_des_recommandations_sont_exposes(self):
        self._creer("02_Veille_hebdo/corpus_structures.jsonl", '{"video": "x"}\n')
        self._creer("03_Amelioration/recommandations.jsonl",
                    '{"semaine": "2026-S36", "texte": "baisser le seuil", "statut": "refusee"}\n'
                    '\n'
                    '{"semaine": "2026-S37", "texte": "revoir le hook", "statut": "proposee"}\n')

        resultat = rassembler_inputs.rassembler(self.root, jours=7)

        self.assertTrue(resultat["corpus_structures"].endswith("corpus_structures.jsonl"))
        self.assertEqual(len(resultat["recommandations_passees"]), 2)
        self.assertEqual([r["semaine"] for r in resultat["recommandations_en_attente"]],
                         ["2026-S37"])

    def test_une_ligne_de_suivi_illisible_ne_fait_pas_tomber_le_bilan(self):
        self._creer("03_Amelioration/recommandations.jsonl",
                    'pas du json\n{"statut": "proposee"}\n')
        resultat = rassembler_inputs.rassembler(self.root, jours=7)
        self.assertEqual(len(resultat["recommandations_passees"]), 1)

    def test_video_active_porte_son_inactivite(self):
        chemin = self._creer("videos/2026-08-01_v01/state.json",
                             json.dumps(_state("2026-08-01_v01")), ancien=True)
        self.assertTrue(os.path.isfile(chemin))
        resultat = rassembler_inputs.rassembler(self.root, jours=7)

        (video,) = resultat["videos_actives"]
        self.assertEqual(video["video_id"], "2026-08-01_v01")
        self.assertEqual(video["format"], "interview_fictive")
        self.assertGreater(video["jours_sans_activite"], 7)
        # Figee depuis un mois : elle reste visible, mais ses compteurs ne
        # comptent pas dans le bilan de la semaine.
        self.assertEqual(resultat["indicateurs"]["tentatives_par_etape"], {})

    def test_racine_vide_ne_plante_pas(self):
        resultat = rassembler_inputs.rassembler(self.root, jours=7)
        self.assertEqual(resultat["videos_actives"], [])
        self.assertEqual(resultat["checkpoints"], [])
        self.assertEqual(resultat["indicateurs"]["alertes"], [])


class TestIndicateurs(unittest.TestCase):
    def test_le_cas_e4_huit_tentatives_ressort(self):
        state = _state(etapes={"E4_audio": _etape("alerte", 8,
                                                  message="E4_audio : 8 echecs, intervention de Franco requise.")})
        ind = rassembler_inputs.indicateurs([state])

        self.assertEqual(ind["tentatives_par_etape"]["E4_audio"],
                         {"tentatives_total": 8, "videos": 1, "max": 8, "tentatives_moyennes": 8.0})
        (alerte,) = ind["alertes"]
        self.assertEqual((alerte["etape"], alerte["tentatives"]), ("E4_audio", 8))

    def test_une_alerte_levee_survit_dans_l_historique(self):
        # Une fois le probleme corrige, l'etape repasse a `termine` : sans
        # l'historique, la semaine de la correction serait celle de l'oubli.
        state = _state(
            etapes={"E4_audio": _etape("termine", 9)},
            historique=[{"horodatage": "2026-09-10T10:00:00Z", "agent": "colab_voix",
                         "evenement": "alerte",
                         "message": "E4_audio : 8 echecs, intervention de Franco requise."}])
        ind = rassembler_inputs.indicateurs([state])

        (alerte,) = ind["alertes"]
        self.assertEqual(alerte["etape"], "E4_audio")
        self.assertEqual(alerte["source"], "historique")

    def test_une_alerte_n_est_pas_comptee_deux_fois(self):
        message = "E4_audio : 8 echecs, intervention de Franco requise."
        state = _state(
            etapes={"E4_audio": _etape("alerte", 8, message=message)},
            historique=[{"horodatage": "2026-09-10T10:00:00Z", "agent": "colab_voix",
                         "evenement": "alerte", "message": message}])
        self.assertEqual(len(rassembler_inputs.indicateurs([state])["alertes"]), 1)

    def test_les_refus_de_checkpoint_viennent_des_deux_sources_sans_doublon(self):
        # _reagir_au_refus remet le checkpoint a `a_venir` : en pratique seul
        # l'historique garde le refus. Les deux lectures doivent coexister.
        state = _state(
            etapes={"CP2": {"statut": "refuse", "commentaire": "hook trop mou", "date": None},
                    "CP1": {"statut": "a_venir", "commentaire": "sujet deja traite", "date": None}},
            historique=[{"horodatage": "2026-09-09T10:00:00Z", "agent": "orchestrateur",
                         "evenement": "CP2_refuse", "message": "hook trop mou"},
                        {"horodatage": "2026-09-08T10:00:00Z", "agent": "orchestrateur",
                         "evenement": "CP1_refuse", "message": "sujet deja traite"}])
        refus = rassembler_inputs.indicateurs([state])["refus_checkpoints"]

        self.assertEqual(len(refus), 2)
        self.assertEqual({r["checkpoint"] for r in refus}, {"CP1", "CP2"})
        self.assertEqual({r["commentaire"] for r in refus}, {"hook trop mou", "sujet deja traite"})

    def test_les_tours_de_boucle_perdus_par_un_refus_cp2_sont_retrouves(self):
        # engine._reagir_au_refus remet boucle_A4_A5 a zero : le compteur seul
        # sous-estime le cout reel de la video.
        state = _state(
            boucle_A4_A5=1,
            historique=[{"horodatage": "2026-09-09T1%d:00:00Z" % i, "agent": "filtre_tts",
                         "evenement": "echec",
                         "message": "Tour %d : retour a la redaction." % i} for i in (1, 2, 3)])
        (boucle,) = rassembler_inputs.indicateurs([state])["boucles_redaction_filtre"]
        self.assertEqual(boucle["tours"], 3)

    def test_duree_de_production_mesuree_jusqu_au_cp3(self):
        state = _state(cree_le="2026-09-10T08:00:00Z",
                       etapes={"CP3": {"statut": "valide", "commentaire": None,
                                       "date": "2026-09-11T10:30:00Z"}})
        (duree,) = rassembler_inputs.indicateurs([state])["durees_production_h"]
        self.assertEqual(duree["heures"], 26.5)

    def test_une_date_absente_ou_incoherente_ne_produit_pas_de_duree(self):
        sans_cp3 = _state(etapes={"CP3": {"statut": "a_venir", "commentaire": None, "date": None}})
        a_rebours = _state(cree_le="2026-09-11T10:00:00Z",
                           etapes={"CP3": {"statut": "valide", "commentaire": None,
                                           "date": "2026-09-10T08:00:00Z"}})
        self.assertEqual(rassembler_inputs.indicateurs([sans_cp3, a_rebours])["durees_production_h"], [])

    def test_les_tentatives_s_agregent_sur_plusieurs_videos(self):
        states = [_state("2026-09-10_v01", etapes={"E3_filtre": _etape("termine", 3)}),
                  _state("2026-09-10_v02", etapes={"E3_filtre": _etape("termine", 1)})]
        stats = rassembler_inputs.indicateurs(states)["tentatives_par_etape"]["E3_filtre"]
        self.assertEqual(stats, {"tentatives_total": 4, "videos": 2, "max": 3,
                                 "tentatives_moyennes": 2.0})


if __name__ == "__main__":
    unittest.main()


class TestRapportsAudioArchives(unittest.TestCase):
    """
    `04_rapport_audio.md` ne garde que la derniere tentative, et une
    tentative reussie ne contient aucun diff. Sur 2026-09-11_v01, huit runs
    n'ont laisse qu'un fichier : celui du succes. H1 n'avait donc jamais
    acces aux echecs, qui sont precisement ce qu'il y a a apprendre.
    """

    def setUp(self):
        self.root = tempfile.mkdtemp(prefix="h1_audio_")
        self.video = os.path.join(self.root, "videos", "2026-09-11_v01")
        os.makedirs(os.path.join(self.video, "audio"))

    def tearDown(self):
        shutil.rmtree(self.root, ignore_errors=True)

    def _creer(self, relatif, ancien=False):
        chemin = os.path.join(self.video, *relatif.split("/"))
        with open(chemin, "w", encoding="utf-8") as f:
            f.write("# Rapport Audio E4\n")
        if ancien:
            vieux = time.time() - 30 * 86400
            os.utime(chemin, (vieux, vieux))

    def test_les_tentatives_archivees_sont_ramassees(self):
        self._creer("04_rapport_audio.md")
        self._creer("audio/rapport_tentative_01.md")
        self._creer("audio/rapport_tentative_08.md")

        rapports = rassembler_inputs.rassembler(self.root, jours=7)["rapports_audio"]

        self.assertEqual(len(rapports), 3)
        self.assertTrue(any("rapport_tentative_01" in r for r in rapports))
        self.assertTrue(any("rapport_tentative_08" in r for r in rapports))

    def test_les_archives_anciennes_sont_ignorees(self):
        self._creer("audio/rapport_tentative_01.md", ancien=True)
        self.assertEqual(rassembler_inputs.rassembler(self.root, jours=7)["rapports_audio"], [])
