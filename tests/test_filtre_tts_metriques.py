"""
Tests de metriques.py (agent A5, §7.3), qui n'en avait aucun.

Regression couverte : le script mesurait le Markdown brut. Les titres du
gabarit (`# Script brut — ...`, `## Hook`) n'ont pas de ponctuation finale et
etaient donc recolles a la phrase suivante, gonflant son compte de mots. Une
phrase correcte pouvait ainsi franchir le seuil de decoupe (22 mots) et
declencher une revision A4<->A5 — boucle plafonnee a 3 tours avant alerte.

Lancer : python3 -m pytest tests/test_filtre_tts_metriques.py -v
"""

import importlib.util
import json
import os
import subprocess
import sys
import tempfile
import unittest

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCRIPT = os.path.join(REPO_ROOT, "agents", "short-filtre-tts", "scripts", "metriques.py")


def _module():
    spec = importlib.util.spec_from_file_location("metriques", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


m = _module()

# Le gabarit impose au redacteur (SKILL.md de A4).
SCRIPT_GABARIT = """# Script brut — What the new model actually changes

## Hook

Everyone says this model is a huge leap.

## Promesse spectateur

I ran the benchmarks myself so you do not have to.

## Corps (marqueurs de voix / style oral)

It scores 88.2 on the public eval.

## CTA / cloture

Follow for more tests like this one.
"""


class TestDecoupage(unittest.TestCase):
    def test_les_titres_ne_sont_pas_comptes_comme_du_texte_parle(self):
        phrases = m.decouper_phrases(SCRIPT_GABARIT)
        textes = [p for _, p in phrases]
        self.assertEqual(textes, [
            "Everyone says this model is a huge leap.",
            "I ran the benchmarks myself so you do not have to.",
            "It scores 88.2 on the public eval.",
            "Follow for more tests like this one.",
        ])

    def test_la_section_d_origine_est_conservee(self):
        """§7.3 : les hooks courts sont une exception a la fusion. A5 doit
        pouvoir savoir qu'une phrase courte vient du Hook."""
        sections = [s for s, _ in m.decouper_phrases(SCRIPT_GABARIT)]
        self.assertEqual(sections[0], "Hook")
        self.assertEqual(sections[3], "CTA / cloture")

    def test_un_titre_ne_gonfle_plus_la_phrase_suivante(self):
        """Le coeur de la regression : une phrase de 14 mots, parfaitement dans
        les clous, depassait le seuil de decoupe une fois les titres recolles."""
        titre = "What the new open weight model actually changes for you"
        phrase = "This model changes how you run things locally and it is worth ten minutes."
        texte = f"# Script brut — {titre}\n\n## Hook\n\n{phrase}\n"

        # Ce que mesurait l'ancienne version : tout colle, faute de ponctuation
        # finale sur les titres.
        ancien_compte = len(f"# Script brut — {titre} ## Hook {phrase}".split())
        self.assertGreater(ancien_compte, m.SEUIL_DECOUPE,
                           "le cas de test ne reproduit plus la regression")

        phrases = [m.analyser(p, s) for s, p in m.decouper_phrases(texte)]
        self.assertEqual(len(phrases), 1)
        self.assertEqual(phrases[0]["mots"], 14)
        self.assertFalse(phrases[0]["trop_longue"])

    def test_un_paragraphe_sur_plusieurs_lignes_reste_une_phrase(self):
        """Un retour a la ligne souple ne doit pas fabriquer de fausses
        phrases courtes."""
        texte = "## Corps\n\nThis sentence is wrapped\nacross two source lines.\n"
        phrases = m.decouper_phrases(texte)
        self.assertEqual([p for _, p in phrases],
                         ["This sentence is wrapped across two source lines."])

    def test_deux_paragraphes_ne_fusionnent_pas(self):
        texte = "## Corps\n\nFirst idea without a period\n\nSecond idea here.\n"
        self.assertEqual([p for _, p in m.decouper_phrases(texte)],
                         ["First idea without a period", "Second idea here."])

    def test_les_items_de_liste_sont_des_unites(self):
        texte = "## Corps\n\n- first point here\n- second point here\n"
        self.assertEqual([p for _, p in m.decouper_phrases(texte)],
                         ["first point here", "second point here"])

    def test_le_gras_et_le_code_ne_comptent_pas_comme_des_mots(self):
        texte = "## Corps\n\nThis is **really** fast with `vllm` today.\n"
        phrases = [m.analyser(p, s) for s, p in m.decouper_phrases(texte)]
        self.assertEqual(phrases[0]["phrase"], "This is really fast with vllm today.")
        self.assertEqual(phrases[0]["mots"], 7)

    def test_un_numero_de_version_ne_coupe_pas_la_phrase(self):
        """La niche est tech : les versions et decimales sont partout."""
        texte = "## Corps\n\nWe tested GPT-4.5 and it scores 88.2 overall.\n"
        self.assertEqual(len(m.decouper_phrases(texte)), 1)

    def test_un_bloc_de_code_est_ignore(self):
        texte = "## Corps\n\nRun this command.\n\n```bash\npip install vllm\n```\n\nThen you are done.\n"
        self.assertEqual([p for _, p in m.decouper_phrases(texte)],
                         ["Run this command.", "Then you are done."])


class TestSeuils(unittest.TestCase):
    def test_seuils_du_paragraphe_7_3(self):
        self.assertEqual((m.CIBLE_MIN, m.CIBLE_MAX), (8, 18))
        self.assertEqual((m.SEUIL_DECOUPE, m.SEUIL_FUSION), (22, 4))

    def test_bande_cible_signalee_sans_exiger_d_action(self):
        courte = m.analyser("One two three four five.")          # 5 mots
        dans_cible = m.analyser(" ".join(["mot"] * 12) + ".")     # 12 mots
        longue = m.analyser(" ".join(["mot"] * 25) + ".")         # 25 mots

        self.assertTrue(courte["hors_cible"])
        self.assertFalse(courte["trop_courte"])   # >= 4 : pas de fusion imposee
        self.assertFalse(dans_cible["hors_cible"])
        self.assertTrue(longue["hors_cible"])
        self.assertTrue(longue["trop_longue"])    # > 22 : decoupe imposee

    def test_parentheses_et_url_toujours_signalees(self):
        self.assertTrue(m.analyser("See the paper (Smith).")["contient_parenthese_ou_url"])
        self.assertTrue(m.analyser("Go to https://example.com now.")["contient_parenthese_ou_url"])


class TestSortieScript(unittest.TestCase):
    def test_sortie_json_complete(self):
        with tempfile.NamedTemporaryFile("w", suffix=".md", delete=False, encoding="utf-8") as f:
            f.write(SCRIPT_GABARIT)
            chemin = f.name
        try:
            p = subprocess.run([sys.executable, SCRIPT, "--fichier", chemin],
                               capture_output=True, text=True)
            self.assertEqual(p.returncode, 0, p.stderr)
            data = json.loads(p.stdout)
        finally:
            os.unlink(chemin)

        self.assertEqual(data["resume"]["nb_phrases"], 4)
        self.assertEqual(data["resume"]["trop_longues"], 0)
        self.assertEqual(data["resume"]["cible"], "8-18 mots")
        self.assertIn("hors_cible", data["resume"])
        self.assertEqual(data["phrases"][0]["section"], "Hook")


if __name__ == "__main__":
    unittest.main()
