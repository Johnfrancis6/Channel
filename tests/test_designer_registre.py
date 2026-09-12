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
import re
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


class TestGeometrieDesComposants(unittest.TestCase):
    """
    Les defauts de dessin ne se voient qu'au rendu, mais certains se
    calculent. Celui-ci a ete introduit par un correctif : passer le rayon
    des noeuds de 72 a 88 pour que « OBSERVE » tienne dans son cercle a fait
    sortir le cercle du cadre — 380 + 300 + 88 + 2,5 = 770,5 pour un viewBox
    de 760, soit quatre noeuds rognes de 10,5 px. Aucun test ne pouvait le
    dire ; celui-ci le dit.
    """

    def _source(self):
        chemin = (Path(__file__).resolve().parent.parent / "composants" / "src"
                  / "components" / "ConceptCutaway.tsx")
        return chemin.read_text(encoding="utf-8-sig")

    def _constante(self, source, nom):
        trouve = re.search(rf"const {nom} = ([0-9.]+);", source)
        self.assertIsNotNone(trouve, f"{nom} introuvable")
        return float(trouve.group(1))

    def test_les_noeuds_de_la_boucle_tiennent_dans_le_cadre(self):
        source = self._source()
        taille = self._constante(source, "TAILLE")
        rayon_noeud = self._constante(source, "RAYON_NOEUD")
        trait = self._constante(source, "TRAIT_NOEUD")
        marge = self._constante(source, "MARGE")

        centre = taille / 2
        rayon_boucle = centre - rayon_noeud - trait / 2 - marge
        extremite = centre + rayon_boucle + rayon_noeud + trait / 2

        self.assertLessEqual(extremite, taille,
                             "les noeuds de agent_loop sortent du viewBox")
        # Et le rayon reste utile : une boucle ecrasee ne se lit pas non plus.
        self.assertGreater(rayon_boucle, taille * 0.3)

    def test_le_rayon_de_la_boucle_est_derive_et_non_ecrit(self):
        # C'est la forme du code qui empeche le defaut de revenir : un rayon
        # ecrit a la main se desynchronise du reste au premier ajustement.
        source = self._source()
        self.assertIn("const R = C - RAYON_NOEUD", source)
        self.assertNotIn("const R = 300", source)


class TestPosesAtteignables(unittest.TestCase):
    """
    `intro` et `outro` rendaient la meme image parce que les deux pointaient
    sur 'wave'. Corrige — puis `lean_in` pointait sur 'point', et 'lean', la
    seule pose qui incline le buste, n'etait atteignable par personne. Deux
    fois le meme defaut : l'API annonce un choix que le rendu ne fait pas.
    """

    def _sources(self):
        base = Path(__file__).resolve().parent.parent / "composants" / "src" / "components"
        return (base / "StickmanTalk.tsx").read_text(encoding="utf-8-sig"), \
               (base / "Stickman.tsx").read_text(encoding="utf-8-sig")

    def test_chaque_pose_de_stickmantalk_rend_une_image_distincte(self):
        talk, _ = self._sources()
        bloc = talk.split("POSE_VERS_STICKMAN")[1].split("}")[0]
        cibles = re.findall(r"^\s*(\w+):\s*'(\w+)'", bloc, re.MULTILINE)
        self.assertTrue(cibles, "mapping illisible")

        rendus = [cible for _, cible in cibles]
        self.assertEqual(len(rendus), len(set(rendus)),
                         f"deux poses rendent la meme image : {cibles}")

    def test_la_pose_qui_incline_le_buste_est_utilisee(self):
        talk, stickman = self._sources()
        # La pose qui porte l'inclinaison, quelle qu'elle soit nommee.
        inclinee = re.search(r"pose === '(\w+)' \? 7 : 0", stickman)
        self.assertIsNotNone(inclinee, "plus d'inclinaison dans Stickman")
        self.assertIn(f"'{inclinee.group(1)}'", talk,
                      f"la pose '{inclinee.group(1)}' n'est atteignable par personne")
