"""
Teste la normalisation des references de chaines (A3, stats_youtube.py).

Le script n'acceptait que des identifiants `UCxxxx`, alors qu'une URL
YouTube moderne n'en expose plus : on y lit `/@nomdechaine`. Convertir
chaque concurrent a la main est exactement le genre de friction qui fait
qu'une liste ne se remplit jamais — et `chaines_concurrentes.json` est
vide depuis le debut.
"""
import json
import os
import sys
import tempfile
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


class TestFusionnerChaines(unittest.TestCase):
    """
    Franco donne sa liste de chaines en conversation et l'agent l'ecrit
    (decision du 12/09/2026). Le fichier reste le sien : un agent qui le
    remplacerait effacerait une chaine ajoutee a la main entre deux
    analyses.
    """

    def setUp(self):
        self.tmp = tempfile.mkdtemp(prefix="chaines_test_")
        self.chemin = os.path.join(self.tmp, "00_Profil", "chaines_concurrentes.json")

    def tearDown(self):
        import shutil
        shutil.rmtree(self.tmp, ignore_errors=True)

    def _ecrire(self, contenu):
        os.makedirs(os.path.dirname(self.chemin), exist_ok=True)
        with open(self.chemin, "w", encoding="utf-8") as f:
            f.write(contenu)

    def _lire(self):
        with open(self.chemin, encoding="utf-8-sig") as f:
            return json.load(f)

    def test_cree_le_fichier_absent(self):
        liste, ajoutees = stats_youtube.fusionner_chaines(
            self.chemin, [{"channel_id": "UC1", "nom": "Chaine A"}])
        self.assertEqual(ajoutees, 1)
        self.assertEqual(self._lire(), [{"channel_id": "UC1", "nom": "Chaine A"}])
        self.assertEqual(liste, self._lire())

    def test_n_efface_jamais_une_chaine_existante(self):
        self._ecrire(json.dumps([{"channel_id": "UC1", "nom": "Ajoutee a la main"}]))

        _, ajoutees = stats_youtube.fusionner_chaines(
            self.chemin, [{"channel_id": "UC2", "nom": "Chaine B"}])

        self.assertEqual(ajoutees, 1)
        self.assertEqual([c["channel_id"] for c in self._lire()], ["UC1", "UC2"])
        self.assertEqual(self._lire()[0]["nom"], "Ajoutee a la main")

    def test_une_chaine_deja_presente_n_est_pas_dupliquee(self):
        self._ecrire(json.dumps([{"channel_id": "UC1", "nom": "Chaine A"}]))
        _, ajoutees = stats_youtube.fusionner_chaines(
            self.chemin, [{"channel_id": "UC1", "nom": "Chaine A"}])
        self.assertEqual(ajoutees, 0)
        self.assertEqual(len(self._lire()), 1)

    def test_un_nom_manquant_est_complete(self):
        self._ecrire(json.dumps([{"channel_id": "UC1", "nom": None}]))
        stats_youtube.fusionner_chaines(self.chemin, [{"channel_id": "UC1", "nom": "Chaine A"}])
        self.assertEqual(self._lire()[0]["nom"], "Chaine A")

    def test_un_fichier_illisible_n_est_pas_ecrase(self):
        self._ecrire("{ ceci n'est pas du json")
        with self.assertRaises(ValueError):
            stats_youtube.fusionner_chaines(self.chemin, [{"channel_id": "UC1", "nom": "A"}])
        with open(self.chemin, encoding="utf-8") as f:
            self.assertIn("ceci n'est pas du json", f.read())
