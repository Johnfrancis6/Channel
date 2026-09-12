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

from orchestrateur import engine
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
        # Meme sans priorite declaree, une liste de liens passe apres le
        # contenu : elle ne porte la decision d'aucun checkpoint.
        self.assertIn("## Faits verifies", extrait)

    def test_fichier_sans_titre_markdown(self):
        contenu = "du texte brut " * 500
        extrait = _extraire_sections(contenu, 500, ("Peu importe",))
        self.assertLessEqual(len(extrait), 700)


class TestSectionsPrioritairesReelles(unittest.TestCase):
    """Les motifs declares dans RESUME_SOURCES doivent couvrir le gabarit
    reel de 01_recherche.md, y compris ses variantes selon le mode."""

    def gabarit(self, titre_angle):
        return (
            "# Recherche — un titre\n\n## Sources\n" + "- https://x.test\n" * 120 +
            "\n## Faits verifies\n" + "- un fait verifie et detaille. " * 120 +
            f"\n\n## Matiere a hook\n\n- un fait contre-intuitif\n"
            f"\n## {titre_angle}\n\nProgression en trois etapes.\n"
            "\n## Incertitudes assumees\n\nLe chiffre de dix mille n'est pas recoupe.\n"
            "\n## Termes a risque de prononciation\n\n- MCP\n"
            + QUESTIONS
        )

    def extraire(self, titre_angle):
        from orchestrateur.engine import RESUME_SOURCES
        prioritaires = RESUME_SOURCES["CP1"][0][2]
        return _extraire_sections(self.gabarit(titre_angle), 3000, prioritaires)

    def test_angle_propose_survit(self):
        self.assertIn("Progression en trois etapes", self.extraire("Angle propose"))

    def test_angle_confirme_survit_aussi(self):
        # En mode `sujet_impose`, A6 ecrit "Angle confirme" : un motif cale
        # sur la seule forme "Angle propose" laisserait tomber la section.
        self.assertIn("Progression en trois etapes", self.extraire("Angle confirme"))

    def test_les_incertitudes_survivent(self):
        # Un chiffre non recoupe qui disparait du rapport devient une
        # affirmation de la chaine sans que Franco l'ait vu.
        self.assertIn("n'est pas recoupe", self.extraire("Angle confirme"))

    def test_les_questions_survivent(self):
        self.assertIn("Points a trancher par Franco", self.extraire("Angle confirme"))


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


class TestResumeCP3(unittest.TestCase):
    """Le CP3 autorise la publication. Le rapport ne montrait que le
    storyboard — le plan de tournage — et pas un chiffre du rendu : sur
    2026-09-11_v01, le fichier video n'etait meme pas nomme, et l'ecart de
    16,4 s entre le rendu et la voix off n'apparaissait nulle part."""

    def setUp(self):
        self.dir = tempfile.mkdtemp(prefix="chaine_yt_cp3_")
        os.makedirs(os.path.join(self.dir, "checkpoints"), exist_ok=True)
        self.ecrire_storyboard([("s1", 10.0), ("s2", 10.0)])
        self.ecrire_phrases(20.0)
        with open(os.path.join(self.dir, "05_storyboard.md"), "w", encoding="utf-8") as f:
            f.write("# Storyboard\n\n## Duree totale indicative\n\n20 s\n")
        with open(os.path.join(self.dir, "06_video_finale.mp4"), "wb") as f:
            f.write(b"\0" * 2048)
        self.state = {"etapes": {
            "CP3": {"statut": "a_venir", "commentaire": None},
            "E6_montage": {"statut": "termine", "sorties": ["06_video_finale.mp4"],
                           "message": "2 scenes rendues."},
        }}

    def tearDown(self):
        shutil.rmtree(self.dir, ignore_errors=True)

    def ecrire_storyboard(self, scenes, nouveaux=None, a_completer=()):
        import json as j
        data = {"scenes": [{"id": i, "composant": "TitleCard", "duree_s": d, "params": {},
                            **({"a_completer": True} if i in a_completer else {})}
                           for i, d in scenes],
                "nouveaux_composants_necessaires": nouveaux or []}
        with open(os.path.join(self.dir, "05_storyboard.json"), "w", encoding="utf-8") as f:
            j.dump(data, f)

    def ecrire_phrases(self, duree):
        import json as j
        with open(os.path.join(self.dir, "04_phrases.json"), "w", encoding="utf-8") as f:
            j.dump({"phrases": [], "duree_totale_s": duree}, f)

    def resume(self):
        return _construire_resume_checkpoint(self.dir, self.state, "CP3")

    def test_le_fichier_est_nomme_et_pese(self):
        r = self.resume()
        self.assertIn("06_video_finale.mp4", r)
        self.assertIn("Ko", r)

    def test_les_deux_durees_sont_donnees(self):
        r = self.resume()
        self.assertIn("Duree du rendu", r)
        self.assertIn("Duree de la voix off", r)

    def test_pas_d_alerte_quand_les_durees_collent(self):
        self.assertNotIn("Ecart de", self.resume())

    def test_l_ecart_est_signale(self):
        # Le cas reel : rendu 98,8 s, voix off 82,5 s.
        self.ecrire_storyboard([("s1", 50.0), ("s2", 48.8)])
        self.ecrire_phrases(82.5)
        r = self.resume()
        self.assertIn("Ecart de 16.3 s", r)
        self.assertIn("depasse la voix off", r)

    def test_un_rendu_trop_court_est_signale_aussi(self):
        self.ecrire_storyboard([("s1", 10.0)])
        self.ecrire_phrases(30.0)
        self.assertIn("s'arrete avant la fin", self.resume())

    def test_mp4_manquant_est_dit(self):
        os.remove(os.path.join(self.dir, "06_video_finale.mp4"))
        self.assertIn("introuvable", self.resume())

    def test_scenes_non_tranchees_alertent(self):
        self.ecrire_storyboard([("s1", 10.0), ("s2", 10.0)], a_completer={"s2"})
        self.assertIn("non tranchees par le Designer", self.resume())

    def test_nouveaux_composants_signales(self):
        self.ecrire_storyboard([("s1", 20.0)], nouveaux=["StickmanTalk"])
        self.assertIn("StickmanTalk", self.resume())

    def test_la_video_passe_avant_le_plan(self):
        r = self.resume()
        self.assertLess(r.index("La video a valider"), r.index("Storyboard"))

    def test_le_rappel_de_regarder_est_present(self):
        self.assertIn("Regarde la video avant de valider", self.resume())

    def test_les_champs_seo_restent(self):
        self.assertIn("SEO", self.resume())


if __name__ == "__main__":
    unittest.main()


class TestRangsDeSections(unittest.TestCase):
    """
    Le budget restant se servait dans l'ordre du document, et `## Sources`
    est la premiere section de `01_recherche.md`. Sur le rapport reel de
    2026-09-11_v01 (4538 caracteres pour 3000), Franco recevait 506
    caracteres de liens entiers et perdait les trois quarts des faits
    verifies (622 sur 2151).
    """

    PRIO = ("Points a trancher", "Angle propose")

    def _document(self):
        return (
            "# Titre\n\n"
            "## Sources\n\n" + "lien. " * 100 + "\n\n"
            "## Faits verifies\n\n" + "fait. " * 400 + "\n\n"
            "## Angle propose\n\n" + "angle. " * 30 + "\n\n"
            "## Points a trancher par Franco au CP1\n\n" + "question. " * 30 + "\n"
        )

    def test_les_liens_cedent_le_budget_aux_faits(self):
        extrait = engine._extraire_sections(self._document(), 1500, self.PRIO)

        self.assertIn("Points a trancher", extrait)
        self.assertIn("Angle propose", extrait)
        self.assertIn("Faits verifies", extrait)
        # Une liste de liens se verifie en ouvrant le fichier ; elle ne se
        # lit pas au telephone. Elle part la premiere.
        self.assertNotIn("## Sources", extrait)

    def test_les_sources_restent_quand_le_budget_suffit(self):
        # Releguees ne veut pas dire supprimees : elles degradent en dernier.
        document = self._document()
        extrait = engine._extraire_sections(document, len(document) - 10, self.PRIO)
        self.assertIn("## Sources", extrait)

    def test_la_matiere_a_hook_est_prioritaire_au_cp1(self):
        # Elle est au gabarit d'A2 depuis la revue, mais n'etait pas
        # prioritaire : c'est pourtant ce qui dit si le sujet accrochera.
        prioritaires = engine.RESUME_SOURCES["CP1"][0][2]
        self.assertIn("Matiere a hook", prioritaires)

        accroche = "accroche. " * 20
        document = ("# Titre\n\n## Sources\n\n" + "lien. " * 200 + "\n\n"
                    "## Matiere a hook\n\n" + accroche + "\n")
        extrait = engine._extraire_sections(document, 400, prioritaires)

        # L'accroche passe entiere ; les liens ne prennent que le reste.
        self.assertIn(accroche.strip(), extrait)
        self.assertLess(extrait.index("Matiere a hook"), len(extrait))
        self.assertNotIn("lien. " * 200, extrait)


class TestBudgetAuCP2(unittest.TestCase):
    """
    Sur 2026-09-11_v01, le script depassait le budget de 91 % et le rapport
    de CP2 n'en disait pas un mot : ni le gabarit d'A5 ni les priorites du
    checkpoint ne prevoyaient la question. Franco a valide sans savoir.
    """

    def _prioritaires_metriques(self):
        (_, _, prioritaires), = [s for s in engine.RESUME_SOURCES["CP2"]
                                 if s[0] == "03_rapport_metriques.md"]
        return prioritaires

    def test_le_budget_est_prioritaire(self):
        prioritaires = self._prioritaires_metriques()
        self.assertIn("Budget", prioritaires)
        # Il passe avant les termes de lexique : une prononciation se
        # rattrape au run suivant, une idee de trop se reecrit.
        self.assertLess(prioritaires.index("Budget"), prioritaires.index("Nouveaux termes"))

    def test_le_verdict_survit_a_la_coupe(self):
        document = ("# Rapport metriques\n\n"
                    "## Hors cible\n\n" + "phrase longue. " * 200 + "\n\n"
                    "## Budget\n\n| Ratio | 1.91 |\n| Verdict | **depasse** |\n")
        extrait = engine._extraire_sections(document, 400, self._prioritaires_metriques())
        self.assertIn("depasse", extrait)
