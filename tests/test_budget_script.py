"""
Teste le controle de budget d'un script (A5, metriques.py).

La duree d'un Short n'est pas fixee en secondes : c'est le nombre d'idees
qui est plafonne, et le cout en mots d'une idee depend du format (§8).

Regression d'origine : personne ne mesurait la longueur totale avant le
montage. Sur 2026-09-11_v01, le script faisait 264 mots — 82,5 s de voix
off pour un budget de ~135 — et le depassement n'a ete constate qu'a E5,
quand tout etait ecrit et enregistre. Le Designer l'a signale sans pouvoir
rien faire, en le repoussant au CP3.
"""
import os
import sys
import unittest

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(REPO_ROOT, "agents", "short-filtre-tts", "scripts"))

import metriques  # noqa: E402


class TestEvaluerBudget(unittest.TestCase):
    def test_sans_budget_aucune_evaluation(self):
        # --idees absent : le script mesure les phrases, rien d'autre.
        self.assertIsNone(metriques.evaluer_budget(264))

    def test_dans_le_budget(self):
        b = metriques.evaluer_budget(120, idees=3)
        self.assertEqual(b["verdict"], "ok")
        self.assertEqual(b["budget_mots"], 3 * metriques.MOTS_PAR_IDEE_DEFAUT)
        self.assertEqual(b["depassement_mots"], 0)

    def test_pile_au_budget(self):
        budget = 3 * metriques.MOTS_PAR_IDEE_DEFAUT
        self.assertEqual(metriques.evaluer_budget(budget, idees=3)["verdict"], "ok")

    def test_limite_se_resserre_au_calibrage(self):
        # +10 % : du gras, pas une idee de trop.
        budget = 3 * metriques.MOTS_PAR_IDEE_DEFAUT
        b = metriques.evaluer_budget(int(budget * 1.10), idees=3)
        self.assertEqual(b["verdict"], "limite")

    def test_depassement_franc_renvoie_a_la_redaction(self):
        budget = 3 * metriques.MOTS_PAR_IDEE_DEFAUT
        b = metriques.evaluer_budget(int(budget * 1.5), idees=3)
        self.assertEqual(b["verdict"], "depasse")
        self.assertGreater(b["depassement_mots"], 0)

    def test_le_cas_reel_aurait_crie(self):
        # 2026-09-11_v01 : 264 mots pour 3 idees.
        b = metriques.evaluer_budget(264, idees=3)
        self.assertEqual(b["verdict"], "depasse")
        self.assertGreater(b["ratio"], 1.5)
        # Et la duree annoncee doit coller a l'audio reellement produit (82,5 s).
        self.assertAlmostEqual(b["duree_estimee_s"], 82.5, delta=3.0)

    def test_un_format_plus_couteux_change_le_verdict(self):
        # Une interview fictive incarne et relance : plus de mots par idee,
        # sans idee supplementaire. Le depassement n'en est pas un.
        serre = metriques.evaluer_budget(264, idees=3)
        large = metriques.evaluer_budget(264, idees=3, mots_par_idee=95)
        self.assertEqual(serre["verdict"], "depasse")
        self.assertEqual(large["verdict"], "ok")

    def test_budget_impose_court_circuite_les_idees(self):
        # 3 idees donneraient 135 mots de budget ; --budget-mots prime.
        b = metriques.evaluer_budget(130, idees=3, budget_mots=90)
        self.assertEqual(b["budget_mots"], 90)
        self.assertEqual(b["verdict"], "depasse")

    def test_budget_absurde_ignore(self):
        self.assertIsNone(metriques.evaluer_budget(100, budget_mots=0))

    def test_les_durees_sont_coherentes(self):
        b = metriques.evaluer_budget(320, idees=4)
        self.assertAlmostEqual(b["duree_estimee_s"],
                               320 / metriques.MOTS_PAR_SECONDE, places=1)
        self.assertAlmostEqual(b["duree_budget_s"],
                               b["budget_mots"] / metriques.MOTS_PAR_SECONDE, places=1)


class TestResumeComplet(unittest.TestCase):
    SCRIPT = """# Script brut — test

## Hook
Everyone calls their product an AI agent now.

## Corps
A plain model answers once and stops there.
A workflow adds tools but follows a fixed path.
"""

    def test_le_resume_porte_le_total_et_la_duree(self):
        phrases = [metriques.analyser(p, s)
                   for s, p in metriques.decouper_phrases(self.SCRIPT)]
        total = sum(p["mots"] for p in phrases)
        self.assertGreater(total, 0)
        # Le total doit etre la somme des phrases prononcees, titres exclus.
        self.assertNotIn("Hook", " ".join(p["phrase"] for p in phrases))

    def test_les_seuils_sont_coherents(self):
        self.assertLess(metriques.CIBLE_MAX, metriques.SEUIL_DECOUPE)
        self.assertLess(metriques.SEUIL_FUSION, metriques.CIBLE_MIN)
        self.assertGreater(metriques.MOTS_PAR_SECONDE, 0)
        self.assertGreater(metriques.TOLERANCE_BUDGET, 0)


if __name__ == "__main__":
    unittest.main()
