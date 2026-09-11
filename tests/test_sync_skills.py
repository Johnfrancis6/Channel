"""
.claude/skills/ est entierement genere a partir de deux sources de verite
(§9.2) : agents/short-*/ pour les 7 agents, skills/*/ pour new-short et
short-state.

Cette copie avait deja derive en silence : generer_storyboard.py et
rendre_video.py existaient dans agents/ mais pas dans .claude/skills/, donc
les skills reellement charges par Claude Code tournaient sans eux. Ces tests
font echouer la suite plutot que de laisser la derive s'installer.

Lancer : python3 -m pytest tests/test_sync_skills.py -v
"""

import importlib.util
import os
import shutil
import tempfile
import unittest
from pathlib import Path

RACINE_DEPOT = Path(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SYNC_PATH = RACINE_DEPOT / "agents" / "_synchroniser_vers_claude_skills.py"
CLAUDE_SKILLS = RACINE_DEPOT / ".claude" / "skills"

AGENTS = {"short-chercheur", "short-redacteur", "short-filtre-tts", "short-designer",
          "short-monteur", "short-analyse-chaines", "short-amelioration"}
UTILITAIRES = {"new-short", "short-state"}


def _module():
    spec = importlib.util.spec_from_file_location("sync_skills", SYNC_PATH)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


m = _module()


class TestEtatDuDepot(unittest.TestCase):
    def test_aucune_derive(self):
        self.assertEqual(
            m.verifier(), [],
            "Relance : python3 agents/_synchroniser_vers_claude_skills.py",
        )

    def test_les_deux_sources_sont_couvertes(self):
        """La regression d'origine : skills/* n'etait pas couvert par le
        script et sa copie se faisait a la main."""
        noms = {d.name for d in m.dossiers_sources()}
        self.assertEqual(noms, AGENTS | UTILITAIRES)

    def test_les_utilitaires_viennent_bien_de_skills(self):
        par_nom = {d.name: d for d in m.dossiers_sources()}
        for nom in UTILITAIRES:
            self.assertEqual(par_nom[nom].parent.name, "skills")
        for nom in AGENTS:
            self.assertEqual(par_nom[nom].parent.name, "agents")

    def test_tout_le_deploye_est_en_lf(self):
        for chemin in CLAUDE_SKILLS.rglob("*"):
            if not chemin.is_file() or chemin.suffix.lower() not in m.EXTENSIONS_TEXTE:
                continue
            with self.subTest(fichier=chemin.relative_to(CLAUDE_SKILLS)):
                self.assertNotIn(b"\r\n", chemin.read_bytes())

    def test_les_scripts_ajoutes_tardivement_sont_deployes(self):
        """Les deux fichiers dont l'absence avait revele la derive."""
        for relatif in ("short-designer/scripts/generer_storyboard.py",
                        "short-monteur/scripts/rendre_video.py"):
            with self.subTest(fichier=relatif):
                self.assertTrue((CLAUDE_SKILLS / relatif).is_file())


class TestMecanismeSync(unittest.TestCase):
    """Teste le script sur une arborescence jetable, sans toucher au depot.

    Chaque test recharge le module et fait pointer ses constantes vers le
    dossier temporaire : pas d'etat partage entre tests, et aucun risque de
    regenerer le vrai .claude/skills/."""

    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="sync_skills_"))
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)
        self.agents = self.tmp / "agents"
        self.skills = self.tmp / "skills"
        self.cible = self.tmp / ".claude" / "skills"
        (self.agents / "short-demo" / "scripts").mkdir(parents=True)
        (self.skills / "demo-outil").mkdir(parents=True)

        # Source en CRLF, comme les fichiers reels du depot.
        (self.agents / "short-demo" / "SKILL.md").write_bytes(b"# Demo\r\nligne\r\n")
        (self.agents / "short-demo" / "scripts" / "etape.py").write_bytes(b"x = 1\r\n")
        (self.skills / "demo-outil" / "SKILL.md").write_bytes(b"# Outil\r\n")

        self.m = _module()
        self.m.AGENTS_DIR = self.agents
        self.m.SKILLS_DIR = self.skills
        self.m.CIBLE_DIR = self.cible

    def test_la_copie_normalise_en_lf(self):
        self.m.synchroniser()
        depose = (self.cible / "short-demo" / "SKILL.md").read_bytes()
        self.assertEqual(depose, b"# Demo\nligne\n")
        self.assertNotIn(b"\r", depose)

    def test_source_crlf_et_cible_lf_ne_comptent_pas_comme_une_derive(self):
        self.m.synchroniser()
        self.assertEqual(self.m.verifier(), [])

    def test_une_modification_reelle_est_detectee(self):
        self.m.synchroniser()
        (self.cible / "short-demo" / "SKILL.md").write_bytes(b"# Demo modifie\n")
        self.assertTrue(any("contenu different" in e for e in self.m.verifier()))

    def test_un_fichier_ajoute_a_la_source_est_detecte(self):
        self.m.synchroniser()
        (self.agents / "short-demo" / "scripts" / "nouveau.py").write_bytes(b"y = 2\r\n")
        self.assertTrue(any("manquant" in e for e in self.m.verifier()))

    def test_un_dossier_orphelin_est_detecte_puis_retire(self):
        self.m.synchroniser()
        (self.cible / "skill-supprime").mkdir()
        self.assertTrue(any("orphelin" in e for e in self.m.verifier()))

        _, orphelins = self.m.synchroniser()
        self.assertEqual(orphelins, ["skill-supprime"])
        self.assertFalse((self.cible / "skill-supprime").exists())
        self.assertEqual(self.m.verifier(), [])

    def test_les_deux_arborescences_sont_deployees_cote_a_cote(self):
        deployes, _ = self.m.synchroniser()
        self.assertEqual(deployes, ["demo-outil", "short-demo"])
        self.assertTrue((self.cible / "demo-outil" / "SKILL.md").is_file())
        self.assertTrue((self.cible / "short-demo" / "scripts" / "etape.py").is_file())

    def test_un_conflit_de_nom_echoue_bruyamment(self):
        (self.skills / "short-demo").mkdir()
        with self.assertRaises(SystemExit):
            self.m.dossiers_sources()

    def test_les_caches_python_ne_sont_pas_deployes(self):
        cache = self.agents / "short-demo" / "scripts" / "__pycache__"
        cache.mkdir()
        (cache / "etape.cpython-311.pyc").write_bytes(b"\x00\x01")
        self.m.synchroniser()
        self.assertFalse((self.cible / "short-demo" / "scripts" / "__pycache__").exists())
        self.assertEqual(self.m.verifier(), [])


if __name__ == "__main__":
    unittest.main()
