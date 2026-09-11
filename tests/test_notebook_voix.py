"""
Garde-fous sur notebooks/voix_off.ipynb.

Le notebook ne peut pas etre execute ici (ni GPU, ni Colab, ni les
librairies), mais les defauts qui ont coute le plus cher sur
2026-09-11_v01 sont verifiables statiquement :

- `MAX_TENTATIVES` etait **defini et jamais lu** : un garde-fou decoratif.
  Le compteur est monte a 8 pour un plafond affiche a 3, sans qu'aucune
  alerte ne parte — 2 h 20 a relancer un moteur qui ne pouvait pas marcher.
- l'agent de l'historique etait ecrit en dur, d'ou deux noms
  (`colab_voix_f5tts`, `colab_voix_qwen_tts`) pour une meme etape.
- le diagnostic WER etait identique a 96 % et a 9 %.
"""
import ast
import json
import unittest
from pathlib import Path

NOTEBOOK = Path(__file__).resolve().parent.parent / "notebooks" / "voix_off.ipynb"


def cellules_code():
    nb = json.loads(NOTEBOOK.read_text(encoding="utf-8-sig"))
    return [(i, "".join(c["source"])) for i, c in enumerate(nb["cells"])
            if c["cell_type"] == "code"]


def source_complete():
    return "\n".join(s for _, s in cellules_code())


class TestSyntaxe(unittest.TestCase):
    def test_chaque_cellule_de_code_parse(self):
        for index, source in cellules_code():
            with self.subTest(cellule=index):
                try:
                    ast.parse(source)
                except SyntaxError as e:
                    self.fail(f"cellule {index} : {e}")


class TestPlafondTentatives(unittest.TestCase):
    def setUp(self):
        self.source = source_complete()

    def test_max_tentatives_n_est_plus_une_variable_morte(self):
        # Definie + lue au moins une fois ailleurs que dans sa definition.
        occurrences = self.source.count("MAX_TENTATIVES")
        self.assertGreater(occurrences, 1,
                           "MAX_TENTATIVES est defini mais jamais lu — garde-fou decoratif")

    def test_etape_commencer_refuse_au_dela_du_plafond(self):
        corps = self.source.split("def etape_commencer")[1].split("def etape_terminer")[0]
        self.assertIn("MAX_TENTATIVES", corps,
                      "etape_commencer ne consulte pas le plafond")
        self.assertIn("SystemExit", corps,
                      "etape_commencer ne s'arrete pas au-dela du plafond")

    def test_une_porte_de_sortie_explicite_existe(self):
        # Refuser sans recours bloquerait Franco : il doit pouvoir passer
        # outre, mais en connaissance de cause.
        self.assertIn("FORCER_RELANCE", self.source)
        corps = self.source.split("def etape_commencer")[1].split("def etape_terminer")[0]
        self.assertIn("FORCER_RELANCE", corps)


class TestAgentHistorique(unittest.TestCase):
    def setUp(self):
        self.source = source_complete()

    def test_l_agent_n_est_pas_ecrit_en_dur(self):
        for en_dur in ("'agent': 'colab_voix_qwen_tts'", "'agent': 'colab_voix_f5tts'"):
            self.assertNotIn(en_dur, self.source,
                             "l'agent doit venir de state.json, pas d'une constante")

    def test_l_agent_vient_du_state(self):
        corps = self.source.split("def _historique")[1].split("def etape_commencer")[0]
        self.assertIn("E4_audio", corps)
        self.assertIn("agent", corps)


class TestDiagnosticWER(unittest.TestCase):
    def setUp(self):
        self.source = source_complete()

    def test_le_seuil_structurel_existe_et_est_utilise(self):
        self.assertGreater(self.source.count("SEUIL_WER_GRAVE"), 1,
                           "SEUIL_WER_GRAVE defini mais jamais lu")

    def test_le_diagnostic_distingue_les_deux_natures_d_echec(self):
        # A 96 % de WER, conseiller "re-synthese avec une autre graine" est
        # une perte de temps : c'est ce conseil suivi quatre fois qui a
        # coute 2 h 20 sur la premiere video.
        self.assertIn("STRUCTUREL", self.source)
        self.assertIn("marginal", self.source)

    def test_le_rapport_porte_aussi_le_diagnostic(self):
        # Franco lit 04_rapport_audio.md apres coup, pas la sortie console.
        rapport = self.source.split("rapport_lignes")[1]
        self.assertIn("SEUIL_WER_GRAVE", rapport)

    def test_les_seuils_sont_ordonnes(self):
        import re
        seuil = float(re.search(r"SEUIL_WER\s*=\s*([\d.]+)", self.source).group(1))
        grave = float(re.search(r"SEUIL_WER_GRAVE\s*=\s*([\d.]+)", self.source).group(1))
        self.assertLess(seuil, grave)
        # Les runs reels : 8-18 % marginaux, 93-98 % structurels. La
        # frontiere doit tomber entre les deux.
        self.assertGreater(grave, 0.20)
        self.assertLess(grave, 0.90)


if __name__ == "__main__":
    unittest.main()
