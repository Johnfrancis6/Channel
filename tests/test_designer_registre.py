"""
Tests de parser_registre() (agent A6), branche sur le VRAI registry.ts.

Regression couverte, de la meme famille que le bug de checkpoints.py : le
motif `REGISTRE[^{]*\\{(.*?)\\}` avec re.DOTALL ne s'ancrait pas sur la
declaration. La premiere occurrence de "REGISTRE" dans registry.ts est un
commentaire ("...dans composants/REGISTRE.md"), et `[^{]*` filait ensuite
jusqu'au premier bloc venu — `{charte?: CharteTokens}` de ComposantParams.
parser_registre() renvoyait donc [] : A6 croyait qu'aucun composant
n'existait et demandait a A7 de recreer TitleCard, alors que le §8 impose de
reutiliser d'abord.

Lancer : python3 -m pytest tests/test_designer_registre.py -v
"""

import importlib.util
import os
import unittest
from pathlib import Path

REPO_ROOT = Path(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SCRIPT = REPO_ROOT / "agents" / "short-designer" / "scripts" / "generer_storyboard.py"
REGISTRY_TS = REPO_ROOT / "composants" / "src" / "components" / "registry.ts"


def _module():
    spec = importlib.util.spec_from_file_location("generer_storyboard", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


m = _module()


class TestParserRegistreReel(unittest.TestCase):
    def test_le_registre_du_depot_est_lu(self):
        """Test d'ancrage : il lit le fichier reel, pas une imitation. Si
        registry.ts evolue d'une facon que le parseur ne comprend pas, c'est
        ici que ca doit casser."""
        self.assertIn("TitleCard", m.parser_registre(REGISTRY_TS))

    def test_le_commentaire_mentionnant_REGISTRE_md_ne_piege_plus(self):
        contenu = REGISTRY_TS.read_text(encoding="utf-8")
        self.assertIn("REGISTRE.md", contenu,
                      "le piege a disparu du fichier : ce test ne prouve plus rien")
        self.assertNotIn("charte?", m.parser_registre(REGISTRY_TS))


class TestParserRegistreCasLimites(unittest.TestCase):
    def _ecrire(self, contenu):
        import tempfile
        f = tempfile.NamedTemporaryFile("w", suffix=".ts", delete=False, encoding="utf-8")
        f.write(contenu)
        f.close()
        self.addCleanup(os.unlink, f.name)
        return Path(f.name)

    def test_plusieurs_composants(self):
        chemin = self._ecrire(
            "export const REGISTRE: Record<string, C> = {\n  TitleCard,\n  Quote,\n  CodeBlock,\n};\n")
        self.assertEqual(m.parser_registre(chemin), ["TitleCard", "Quote", "CodeBlock"])

    def test_cles_renommees(self):
        chemin = self._ecrire("export const REGISTRE = {\n  TitleCard: TitleCardV2,\n};\n")
        self.assertEqual(m.parser_registre(chemin), ["TitleCard"])

    def test_commentaires_ignores(self):
        chemin = self._ecrire(
            "export const REGISTRE = {\n  TitleCard, // le seul pour l'instant\n  // Quote, a venir\n};\n")
        self.assertEqual(m.parser_registre(chemin), ["TitleCard"])

    def test_registre_vide(self):
        chemin = self._ecrire("export const REGISTRE = {};\n")
        self.assertEqual(m.parser_registre(chemin), [])

    def test_fichier_absent(self):
        self.assertEqual(m.parser_registre(Path("/introuvable/registry.ts")), [])

    def test_une_declaration_precedee_de_commentaires_reste_trouvee(self):
        chemin = self._ecrire(
            "// voir composants/REGISTRE.md\n"
            "export type ComposantParams = Record<string, unknown> & {charte?: X};\n"
            "export const REGISTRE = {\n  TitleCard,\n};\n")
        self.assertEqual(m.parser_registre(chemin), ["TitleCard"])


if __name__ == "__main__":
    unittest.main()
