"""
Teste les fonctions pures de agents/short-analyse-chaines/scripts (§4.3, A3),
sans appel reseau : parsing des reponses API YouTube Data et generation
du rapport hebdomadaire.
"""

import json
import os
import subprocess
import sys
import tempfile
import unittest

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCRIPTS_DIR = os.path.join(REPO_ROOT, "agents", "short-analyse-chaines", "scripts")
sys.path.insert(0, SCRIPTS_DIR)
import stats_youtube  # noqa: E402
import generer_rapport  # noqa: E402


class TestStatsYoutube(unittest.TestCase):
    def test_resumer_reponse_chaine(self):
        reponse = {
            "items": [{
                "id": "UC123",
                "snippet": {"title": "Ma Chaine"},
                "statistics": {"subscriberCount": "1000", "viewCount": "50000", "videoCount": "42"},
                "contentDetails": {"relatedPlaylists": {"uploads": "UU123"}},
            }]
        }
        resume = stats_youtube.resumer_reponse_chaine(reponse)
        self.assertEqual(resume, {
            "channel_id": "UC123", "titre": "Ma Chaine", "abonnes": 1000,
            "vues_totales": 50000, "nb_videos": 42, "uploads_playlist": "UU123",
        })

    def test_resumer_reponse_chaine_introuvable(self):
        self.assertIsNone(stats_youtube.resumer_reponse_chaine({"items": []}))

    def test_resumer_reponse_videos(self):
        reponse = {"items": [{
            "id": "vid1",
            "snippet": {"title": "Titre", "publishedAt": "2026-09-01T00:00:00Z"},
            "statistics": {"viewCount": "1234"},
        }]}
        videos = stats_youtube.resumer_reponse_videos(reponse)
        self.assertEqual(videos, [{"video_id": "vid1", "titre": "Titre",
                                    "date_publication": "2026-09-01T00:00:00Z", "vues": 1234}])


class TestGenererRapport(unittest.TestCase):
    def test_rendre_avec_et_sans_notes(self):
        chaines = [
            {"channel_id": "UC1", "titre": "Chaine A", "abonnes": 100, "vues_totales": 200,
             "nb_videos": 3, "videos_recentes": [{"titre": "V1", "vues": 50, "date_publication": "2026-09-01"}]},
            {"channel_id": "UC2", "erreur": "chaine introuvable"},
        ]
        contenu = generer_rapport.rendre(chaines, "2026-S37", {"UC1": "Hook percutant, CTA discret."})

        self.assertIn("# Analyse concurrentielle — 2026-S37", contenu)
        self.assertIn("Chaine A", contenu)
        self.assertIn("Hook percutant, CTA discret.", contenu)
        self.assertIn("chaine introuvable", contenu)
        self.assertIn("V1 — 50 vues", contenu)

    def test_rendre_sans_notes_indique_indisponible(self):
        contenu = generer_rapport.rendre([{"channel_id": "UC1", "titre": "X", "abonnes": 1,
                                            "vues_totales": 1, "nb_videos": 1}], "2026-S37", None)
        self.assertIn("Transcriptions indisponibles", contenu)


class TestGenererRapportCLI(unittest.TestCase):
    def test_script_ecrit_le_fichier(self):
        tmp = tempfile.mkdtemp(prefix="a3_test_")
        try:
            stats_path = os.path.join(tmp, "stats.json")
            sortie_path = os.path.join(tmp, "rapport.md")
            with open(stats_path, "w", encoding="utf-8") as f:
                json.dump({"chaines": [{"channel_id": "UC1", "titre": "X"}]}, f)

            p = subprocess.run([sys.executable, os.path.join(SCRIPTS_DIR, "generer_rapport.py"),
                                 "--stats", stats_path, "--semaine", "2026-S37", "--sortie", sortie_path],
                                capture_output=True, text=True)
            self.assertEqual(p.returncode, 0, p.stderr)
            self.assertTrue(os.path.isfile(sortie_path))
        finally:
            import shutil
            shutil.rmtree(tmp, ignore_errors=True)


if __name__ == "__main__":
    unittest.main()
