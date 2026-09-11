"""
Tests du verrou de l'Orchestrateur (§4.3, A1 point 1).

Regression couverte : un verrou.json illisible faisait lever json.load /
strptime a l'interieur d'acquerir_verrou(), et comme ce fichier n'est jamais
nettoye par ce chemin d'erreur, TOUTES les executions suivantes plantaient de
la meme facon. Le pipeline restait bloque jusqu'a une suppression a la main,
alors que le fichier vit sur un dossier Drive synchronise, ou une ecriture a
moitie propagee est un cas realiste.

Lancer : python3 -m pytest tests/test_verrou.py -v
"""

import json
import os
import shutil
import tempfile
import unittest
from datetime import datetime, timedelta, timezone

from orchestrateur.lock import VerrouActifError, acquerir_verrou, liberer_verrou


class TestVerrou(unittest.TestCase):
    def setUp(self):
        self.root = tempfile.mkdtemp(prefix="chaine_yt_verrou_")
        self.chemin = os.path.join(self.root, "01_Orchestrateur", "verrou.json")
        os.makedirs(os.path.dirname(self.chemin), exist_ok=True)

    def tearDown(self):
        shutil.rmtree(self.root, ignore_errors=True)

    def _ecrire_verrou(self, contenu):
        with open(self.chemin, "w", encoding="utf-8") as f:
            f.write(contenu)

    def test_acquisition_puis_liberation(self):
        acquerir_verrou(self.root)
        self.assertTrue(os.path.isfile(self.chemin))
        liberer_verrou(self.root)
        self.assertFalse(os.path.exists(self.chemin))

    def test_verrou_actif_empeche_une_seconde_execution(self):
        acquerir_verrou(self.root)
        with self.assertRaises(VerrouActifError):
            acquerir_verrou(self.root)

    def test_verrou_expire_est_repris(self):
        expire = (datetime.now(timezone.utc) - timedelta(minutes=5)).strftime("%Y-%m-%dT%H:%M:%SZ")
        self._ecrire_verrou(json.dumps({"expire_le": expire, "pid": 1}))
        acquerir_verrou(self.root)  # ne doit pas lever

    def test_verrou_illisible_est_repris_au_lieu_de_tout_bloquer(self):
        for contenu in ('{"expire_le": "pas une date"}',   # date invalide
                        '{"pid": 42}',                     # champ manquant
                        '{"expire_le": ',                  # JSON tronque
                        ''):                               # fichier vide
            with self.subTest(contenu=contenu):
                self._ecrire_verrou(contenu)
                acquerir_verrou(self.root)  # ne doit pas lever
                liberer_verrou(self.root)

    def test_le_verrou_repris_est_de_nouveau_valide(self):
        self._ecrire_verrou("corrompu")
        acquerir_verrou(self.root)
        with open(self.chemin, encoding="utf-8") as f:
            verrou = json.load(f)
        self.assertEqual(verrou["pid"], os.getpid())
        with self.assertRaises(VerrouActifError):
            acquerir_verrou(self.root)


if __name__ == "__main__":
    unittest.main()
