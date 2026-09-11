"""
Teste la normalisation des references de chaines (A3, stats_youtube.py).

Le script n'acceptait que des identifiants `UCxxxx`, alors qu'une URL
YouTube moderne n'en expose plus : on y lit `/@nomdechaine`. Convertir
chaque concurrent a la main est exactement le genre de friction qui fait
qu'une liste ne se remplit jamais — et `chaines_concurrentes.json` est
vide depuis le debut.
"""
import os
import sys
import unittest

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(REPO_ROOT, "agents", "short-analyse-chaines", "scripts"))

import stats_youtube  # noqa: E402

UC = "UCXuqSBlHAE6Xw-yeJA0Tunw"


class TestNormaliser(unittest.TestCase):
    def test_identifiant_uc(self):
        self.assertEqual(stats_youtube.normaliser_reference(UC), ("id", UC))

    def test_handle_avec_arobase(self):
        self.assertEqual(stats_youtube.normaliser_reference("@linustechtips"),
                         ("handle", "@linustechtips"))

    def test_handle_sans_arobase(self):
        self.assertEqual(stats_youtube.normaliser_reference("linustechtips"),
                         ("handle", "@linustechtips"))

    def test_url_handle(self):
        self.assertEqual(stats_youtube.normaliser_reference("https://www.youtube.com/@fireship"),
                         ("handle", "@fireship"))

    def test_url_channel(self):
        self.assertEqual(stats_youtube.normaliser_reference(f"https://youtube.com/channel/{UC}"),
                         ("id", UC))

    def test_url_avec_chemin_supplementaire(self):
        self.assertEqual(stats_youtube.normaliser_reference("https://www.youtube.com/@fireship/videos"),
                         ("handle", "@fireship"))

    def test_ancienne_url_user(self):
        self.assertEqual(stats_youtube.normaliser_reference("https://youtube.com/user/vieuxnom"),
                         ("pseudo", "vieuxnom"))

    def test_ancienne_url_c(self):
        self.assertEqual(stats_youtube.normaliser_reference("https://youtube.com/c/vieuxnom"),
                         ("pseudo", "vieuxnom"))

    def test_espaces_ignores(self):
        self.assertEqual(stats_youtube.normaliser_reference("  @fireship  "),
                         ("handle", "@fireship"))

    def test_valeur_vide(self):
        genre, _ = stats_youtube.normaliser_reference("")
        self.assertIsNone(genre)


class TestParametresChaine(unittest.TestCase):
    def test_id_passe_par_id(self):
        self.assertEqual(stats_youtube.parametres_chaine(UC), {"id": UC})

    def test_handle_passe_par_for_handle(self):
        # forHandle est le seul parametre de channels.list qui resout un @handle.
        self.assertEqual(stats_youtube.parametres_chaine("@fireship"),
                         {"forHandle": "@fireship"})

    def test_pseudo_passe_par_for_username(self):
        self.assertEqual(stats_youtube.parametres_chaine("https://youtube.com/user/vieux"),
                         {"forUsername": "vieux"})

    def test_reference_vide_refusee(self):
        self.assertIsNone(stats_youtube.parametres_chaine("  "))


class TestResumeReponse(unittest.TestCase):
    REPONSE = {
        "items": [{
            "id": UC,
            "snippet": {"title": "Une chaine"},
            "statistics": {"subscriberCount": "1200", "viewCount": "34000", "videoCount": "58"},
            "contentDetails": {"relatedPlaylists": {"uploads": "UU123"}},
        }]
    }

    def test_extraction(self):
        r = stats_youtube.resumer_reponse_chaine(self.REPONSE)
        self.assertEqual(r["channel_id"], UC)
        self.assertEqual(r["titre"], "Une chaine")
        self.assertEqual(r["abonnes"], 1200)
        self.assertEqual(r["uploads_playlist"], "UU123")

    def test_reponse_vide(self):
        self.assertIsNone(stats_youtube.resumer_reponse_chaine({"items": []}))

    def test_statistiques_masquees(self):
        # Une chaine peut cacher son nombre d'abonnes : ce n'est pas une erreur.
        reponse = {"items": [{"id": UC, "snippet": {"title": "X"}, "statistics": {}}]}
        self.assertIsNone(stats_youtube.resumer_reponse_chaine(reponse)["abonnes"])


if __name__ == "__main__":
    unittest.main()
