"""
Teste la construction du resume des rapports de checkpoint (§5.5).

Regression d'origine, observee sur le rapport CP1 reel de 2026-09-11_v01 :
l'extrait etait tronque par le debut a 3000 caracteres, ce qui coupait en
plein milieu du mot "camera" et supprimait entierement la section "Points a
trancher par Franco au CP1". Franco lisait donc un rapport qui ne contenait
pas les questions sur lesquelles il devait decider — il restait les sources,
qui ne servent pas a decider. Il a du ouvrir 01_recherche.md en direct, ce
que le §5.5 cherche precisement a eviter.
"""
import os
import shutil
import tempfile
import unittest

from orchestrateur.checkpoints import chemin_rapport
from orchestrateur.engine import _construire_resume_checkpoint, _extraire_sections

QUESTIONS = """## Points a trancher par Franco au CP1

- Faut-il nommer MCP explicitement dans le script, ou le garder en arriere-plan ?
- Exemple pour l'etape 3 : garder "upgrade Laravel" (niche) ou plus universel ?
- Aucune analyse concurrentielle disponible cette semaine.
"""


def recherche_longue(taille_faits=4000):
    """Meme forme que 01_recherche.md : les questions sont la derniere section."""
    return (
        "# Recherche — un titre de travail\n\n"
        "## Sources\n\n" + "- https://exemple.test/source\n" * 40 + "\n"
        "## Faits verifies\n\n" + ("- Un fait verifie et detaille. " * 10 + "\n") * (taille_faits // 300) + "\n"
        "## Angle propose\n\nProgression en trois etapes, du passif a l'actif.\n\n"
        + QUESTIONS
    )


class TestExtraireSections(unittest.TestCase):
    def test_les_questions_survivent_a_la_troncature(self):
        contenu = recherche_longue()
        self.assertGreater(len(contenu), 3000)
        extrait = _extraire_sections(contenu, 3000, ("Points a trancher", "Angle propose"))
        self.assertIn("Points a trancher par Franco", extrait)
        self.assertIn("Faut-il nommer MCP explicitement", extrait)
        self.assertIn("garder \"upgrade Laravel\" (niche) ou plus universel", extrait)

    def test_l_angle_survit_aussi(self):
        extrait = _extraire_sections(recherche_longue(), 3000, ("Points a trancher", "Angle propose"))
        self.assertIn("Progression en trois etapes", extrait)

    def test_les_accents_du_titre_ne_font_pas_rater_la_section(self):
        # Le fichier reel ecrit "Points à trancher" ; le motif est sans accent.
        contenu = recherche_longue().replace("Points a trancher", "Points à trancher")
        extrait = _extraire_sections(contenu, 3000, ("Points a trancher",))
        self.assertIn("Points à trancher par Franco", extrait)

    def test_la_coupe_est_signalee(self):
        extrait = _extraire_sections(recherche_longue(), 3000, ("Points a trancher",))
        self.assertIn("[...]", extrait)

    def test_le_budget_est_respecte(self):
        extrait = _extraire_sections(recherche_longue(), 3000, ("Points a trancher",))
        # Marges de reassemblage : separateurs et marqueurs [...].
        self.assertLessEqual(len(extrait), 3000 + 200)

    def test_un_fichier_court_passe_intact(self):
        contenu = "# Titre\n\n## Section\n\nCourt.\n"
        self.assertEqual(_extraire_sections(contenu, 3000, ("Section",)), contenu)

    def test_sans_section_prioritaire_on_tronque_sans_planter(self):
        extrait = _extraire_sections(recherche_longue(), 3000, ())
        self.assertTrue(extrait)
        self.assertIn("## Sources", extrait)

    def test_fichier_sans_titre_markdown(self):
        contenu = "du texte brut " * 500
        extrait = _extraire_sections(contenu, 500, ("Peu importe",))
        self.assertLessEqual(len(extrait), 700)


class TestResumeCP1(unittest.TestCase):
    def setUp(self):
        self.video_dir = tempfile.mkdtemp(prefix="chaine_yt_resume_")
        os.makedirs(os.path.join(self.video_dir, "checkpoints"), exist_ok=True)
        with open(os.path.join(self.video_dir, "01_recherche.md"), "w", encoding="utf-8") as f:
            f.write(recherche_longue())
        self.state = {
            "sujet": "AI agents expliques en trois etapes",
            "angle": "Du passif a l'actif",
            "etapes": {"CP1": {"statut": "a_venir", "commentaire": None}},
        }

    def tearDown(self):
        shutil.rmtree(self.video_dir, ignore_errors=True)

    def test_le_resume_cp1_contient_les_questions(self):
        resume = _construire_resume_checkpoint(self.video_dir, self.state, "CP1")
        self.assertIn("Points a trancher par Franco", resume)
        self.assertIn("Faut-il nommer MCP explicitement", resume)

    def test_le_resume_rappelle_sujet_et_angle(self):
        resume = _construire_resume_checkpoint(self.video_dir, self.state, "CP1")
        self.assertIn("AI agents expliques en trois etapes", resume)
        self.assertIn("Du passif a l'actif", resume)

    def test_le_refus_precedent_est_rappele(self):
        self.state["etapes"]["CP1"]["commentaire"] = "Angle trop large, resserrer"
        resume = _construire_resume_checkpoint(self.video_dir, self.state, "CP1")
        self.assertIn("Angle trop large, resserrer", resume)


if __name__ == "__main__":
    unittest.main()
