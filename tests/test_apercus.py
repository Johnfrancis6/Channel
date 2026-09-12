"""
Teste outils/generer_apercus.py et le deploiement de outils/ par le script
de synchronisation.

Le §8 prevoit « un apercu » par composant depuis le depart ; il n'a jamais
existe. Consequence observee sur 2026-09-11_v01 : A6 a demande
`scene="workflow_fixed_path"` sans avoir jamais vu ce que ca rend, et le
plan a tourne 14,4 s. Le catalogue supprime ce point aveugle.
"""
import json
import os
import sys
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "outils"))
sys.path.insert(0, str(REPO_ROOT / "agents"))

import generer_apercus  # noqa: E402
import importlib.util  # noqa: E402

_spec = importlib.util.spec_from_file_location(
    "sync_skills", REPO_ROOT / "agents" / "_synchroniser_vers_claude_skills.py")
sync_skills = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(sync_skills)


class TestSousTitresDansLApercu(unittest.TestCase):
    """
    Le catalogue passait `mots: []`, donc Subtitles ne rendait rien et la
    bande basse qu'il occupe (paddingBottom: 220) n'apparaissait jamais.
    Or « un element du composant passe sous les sous-titres » est exactement
    le genre de defaut qu'un apercu doit attraper, et le docstring promettait
    « exactement ce que la video montrera ».
    """

    def test_les_props_portent_des_mots_horodates(self):
        props = generer_apercus.props_pour(
            "TitleCard", {"texte": "Un titre"},
            {"mouvement": "fondu", "rythme": "standard", "technique": "spring"},
            {"couleurs": {}, "typographie": {}})

        self.assertTrue(props["mots"], "sans mots, l'apercu cache les sous-titres")
        for mot in props["mots"]:
            self.assertEqual(set(mot) >= {"mot", "debut_s", "fin_s"}, True)
            self.assertLess(mot["debut_s"], mot["fin_s"])


class TestDeclaration(unittest.TestCase):
    def test_apercus_json_couvre_le_registre(self):
        """Un composant du registre sans variante declaree n'aurait pas d'apercu."""
        declaration = json.loads((REPO_ROOT / "composants" / "apercus.json")
                                 .read_text(encoding="utf-8-sig"))
        registre = (REPO_ROOT / "composants" / "src" / "components" / "registry.ts") \
            .read_text(encoding="utf-8-sig")
        corps = registre.split("export const REGISTRE")[1].split("{")[1].split("}")[0]
        noms = {m.strip().rstrip(",") for m in corps.split(",") if m.strip()
                and not m.strip().startswith("//")}
        noms = {n for n in noms if n and n.isidentifier()}
        self.assertTrue(noms, "registre illisible")
        manquants = noms - set(declaration)
        self.assertFalse(manquants, f"composants sans apercu declare : {manquants}")

    def test_chaque_variante_a_un_nom_unique_par_composant(self):
        declaration = json.loads((REPO_ROOT / "composants" / "apercus.json")
                                 .read_text(encoding="utf-8-sig"))
        for composant, liste in declaration.items():
            noms = [v.get("nom") for v in liste]
            self.assertEqual(len(noms), len(set(noms)),
                             f"noms de variantes en double pour {composant}")


class TestProps(unittest.TestCase):
    def test_les_props_passent_par_la_composition_reelle(self):
        # L'apercu doit montrer ce que la video montrera : meme composition,
        # memes tokens. Une composition de preview separee divergerait.
        props = generer_apercus.props_pour("TitleCard", {"texte": "x"}, None,
                                           generer_apercus.charte_par_defaut())
        self.assertEqual(len(props["scenes"]), 1)
        self.assertEqual(props["scenes"][0]["composant"], "TitleCard")
        self.assertIn("charte", props)

    def test_des_mots_donc_la_bande_de_sous_titres_est_visible(self):
        # Ce test exigeait l'inverse (`mots == []`) : il figeait en exigence
        # le fait que le catalogue ne montre pas les sous-titres, alors que
        # les composants leur reservent 220 px en bas de cadre.
        props = generer_apercus.props_pour("TitleCard", {}, None,
                                           generer_apercus.charte_par_defaut())
        self.assertEqual(len(props["mots"]), 2)

    def test_la_da_est_transmise_si_declaree(self):
        props = generer_apercus.props_pour(
            "TitleCard", {}, {"mouvement": "fondu", "rythme": "pose", "technique": "spring"},
            generer_apercus.charte_par_defaut())
        self.assertEqual(props["scenes"][0]["da"]["mouvement"], "fondu")

    def test_la_da_est_absente_sinon(self):
        props = generer_apercus.props_pour("TitleCard", {}, None,
                                           generer_apercus.charte_par_defaut())
        self.assertNotIn("da", props["scenes"][0])

    def test_la_charte_par_defaut_porte_les_tokens_d_animation(self):
        charte = generer_apercus.charte_par_defaut()
        self.assertIn("animation", charte)
        self.assertIn("wobble", charte["animation"])


class TestVariantes(unittest.TestCase):
    DECLARATION = {"A": [{"nom": "un", "params": {"x": 1}}, {"params": {"x": 2}}],
                   "B": [{"nom": "trois", "params": {}}]}

    def test_toutes_les_variantes_sont_listees(self):
        self.assertEqual(len(generer_apercus.variantes(self.DECLARATION)), 3)

    def test_nom_derive_si_absent(self):
        noms = [n for c, n, _, _, _ in generer_apercus.variantes(self.DECLARATION) if c == "A"]
        self.assertIn("v2", noms)

    def test_ressources_de_la_variante_sont_transmises(self):
        """Les composants « contenants » (PlanCapture, PlanBroll, PlanLogos) ne
        rendent rien sans asset : leur declaration porte une table
        `ressources` que le rendu doit recevoir telle quelle."""
        declaration = {"PlanCapture": [
            {"nom": "avec-asset", "params": {"capture": "page"},
             "ressources": {"page": {"type": "capture", "src": "/public/apercus/x.png"}}}]}
        (_, _, _, _, ressources), = generer_apercus.variantes(declaration)
        self.assertEqual(ressources["page"]["src"], "/public/apercus/x.png")
        props = generer_apercus.props_pour("PlanCapture", {"capture": "page"}, None,
                                           generer_apercus.charte_par_defaut(), ressources)
        self.assertEqual(props["ressources"], ressources)

    def test_props_sans_ressources_nomet_pas_la_cle(self):
        """Une video montee avant E5b n'a pas de ressources : la cle ne doit
        pas apparaitre a vide dans les props."""
        props = generer_apercus.props_pour("TitleCard", {}, None,
                                           generer_apercus.charte_par_defaut(), {})
        self.assertNotIn("ressources", props)

    def test_filtre_par_composant(self):
        resultat = generer_apercus.variantes(self.DECLARATION, "B")
        self.assertEqual([c for c, _, _, _, _ in resultat], ["B"])


class TestDeploiementOutils(unittest.TestCase):
    def test_les_outils_declares_existent(self):
        for skill, outils in sync_skills.OUTILS_PAR_SKILL.items():
            for nom in outils:
                self.assertTrue((sync_skills.OUTILS_DIR / nom).is_file(),
                                f"{nom} declare pour {skill} mais absent de outils/")

    def test_les_skills_declares_existent(self):
        sources = {d.name for d in sync_skills.dossiers_sources()}
        for skill in sync_skills.OUTILS_PAR_SKILL:
            self.assertIn(skill, sources, f"{skill} declare dans OUTILS_PAR_SKILL mais sans source")

    def test_l_outil_est_embarque_par_le_skill(self):
        source = next(d for d in sync_skills.dossiers_sources() if d.name == "short-designer")
        attendu = sync_skills.contenu_attendu(source)
        self.assertIn(Path("outils") / "generer_apercus.py", attendu)

    def test_un_skill_non_declare_n_embarque_rien(self):
        source = next(d for d in sync_skills.dossiers_sources() if d.name == "short-chercheur")
        attendu = sync_skills.contenu_attendu(source)
        self.assertFalse([p for p in attendu if p.parts[0] == "outils"])

    def test_l_outil_est_reellement_deploye(self):
        deploye = REPO_ROOT / ".claude" / "skills" / "short-monteur" / "outils" / "generer_apercus.py"
        self.assertTrue(deploye.is_file(),
                        "outil non deploye — relance le script de synchronisation")


if __name__ == "__main__":
    unittest.main()
