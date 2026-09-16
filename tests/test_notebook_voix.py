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


def _extraire_fonction(nom):
    """Sort une fonction du notebook pour la tester pour de vrai.

    Le reste du fichier verifie des chaines de caracteres, faute de pouvoir
    executer le notebook. Une fonction pure, elle, s'execute ici — et
    l'invalidation du cache est exactement le genre de regle qu'un test par
    sous-chaine declarerait verte en se trompant.
    """
    import hashlib
    for _, source in cellules_code():
        arbre = ast.parse(source)
        for noeud in ast.walk(arbre):
            if isinstance(noeud, ast.FunctionDef) and noeud.name == nom:
                espace = {"hashlib": hashlib}
                exec(compile(ast.Module([noeud], []), "<notebook>", "exec"), espace)
                return espace[nom], espace
    raise AssertionError(f"fonction {nom} absente du notebook")


class TestCacheDesClips(unittest.TestCase):
    """Les clips ne vivaient qu'en RAM : `resume_after_fail` re-synthetisait
    tout le script depuis zero, et un run coupe avant l'assemblage ne laissait
    rien. Sur un script long, une session Colab a un timeout — l'echec devient
    alors structurel, puisque le run ne peut jamais atteindre l'assemblage."""

    def setUp(self):
        self.source = source_complete()
        self.cle_clip, self.espace = _extraire_fonction("cle_clip")

    def _nom(self, i=0, phrase="Hello world", graine=42, voix="voix_principale", ref="ref"):
        self.espace.update({"GRAINE": graine, "NOM_VOIX": voix, "ref_txt": ref})
        return self.cle_clip(i, phrase)

    def test_meme_entree_meme_nom(self):
        self.assertEqual(self._nom(), self._nom())

    def test_un_script_corrige_invalide_le_cache(self):
        self.assertNotEqual(self._nom(phrase="Hello world"), self._nom(phrase="Hello there"))

    def test_une_autre_graine_invalide_le_cache(self):
        # C'est le conseil que donne le notebook sur un WER marginal : il doit
        # produire une vraie re-synthese, pas relire les memes clips.
        self.assertNotEqual(self._nom(graine=42), self._nom(graine=43))

    def test_une_autre_voix_invalide_le_cache(self):
        self.assertNotEqual(self._nom(voix="a"), self._nom(voix="b"))
        self.assertNotEqual(self._nom(ref="texte de reference"), self._nom(ref="un autre"))

    def test_deux_phrases_identiques_ne_partagent_pas_leur_clip(self):
        # Meme texte a deux endroits du script : la graine est GRAINE + i,
        # donc les deux clips different et l'index doit les separer.
        self.assertNotEqual(self._nom(i=0), self._nom(i=1))

    def test_le_nom_est_ordonnable(self):
        # Les clips se lisent dans l'ordre du script quand on ouvre le dossier.
        self.assertTrue(self._nom(i=0).startswith("0001_"))
        self.assertTrue(self._nom(i=11).startswith("0012_"))

    def test_le_clip_est_ecrit_puis_relu(self):
        self.assertIn("sf.read(chemin_clip", self.source)
        self.assertIn("sf.write(provisoire", self.source)

    def test_l_ecriture_est_atomique(self):
        # Un run coupe pendant l'ecriture laisserait un wav tronque que le run
        # suivant relirait comme s'il etait bon.
        self.assertIn("os.replace(provisoire, chemin_clip)", self.source)


if __name__ == "__main__":
    unittest.main()
