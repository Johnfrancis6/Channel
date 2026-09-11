"""
.claude/skills/ est une copie de la source de verite (agents/short-* pour les
7 agents, skills/* pour new-short et short-state). Cette copie avait deja
derive en silence : generer_storyboard.py et rendre_video.py existaient dans
agents/ mais pas dans .claude/skills/, donc les skills reellement charges par
Claude Code tournaient sans eux.

Ces tests font echouer la suite plutot que de laisser la derive s'installer.

Lancer : python3 -m pytest tests/test_sync_skills.py -v
"""

import importlib.util
import json
import os
import unittest

RACINE_DEPOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SYNC_PATH = os.path.join(RACINE_DEPOT, "agents", "_synchroniser_vers_claude_skills.py")
CLAUDE_SKILLS = os.path.join(RACINE_DEPOT, ".claude", "skills")


def _charger_module_sync():
    spec = importlib.util.spec_from_file_location("sync_skills", SYNC_PATH)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _lire(path):
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


class TestSyncAgents(unittest.TestCase):
    def test_aucune_derive_entre_agents_et_claude_skills(self):
        ecarts = _charger_module_sync().verifier()
        self.assertEqual(
            ecarts, [],
            "Derive detectee. Relance : python3 agents/_synchroniser_vers_claude_skills.py",
        )

    def test_les_sept_agents_sont_deployes(self):
        module = _charger_module_sync()
        noms = {d.name for d in module.dossiers_sources()}
        self.assertEqual(noms, {
            "short-chercheur", "short-redacteur", "short-filtre-tts", "short-designer",
            "short-monteur", "short-analyse-chaines", "short-amelioration",
        })


class TestSyncSkillsUtilitaires(unittest.TestCase):
    """new-short et short-state ne sont PAS couverts par le script de sync :
    leur copie dans .claude/skills/ a ete faite a la main. Tant que c'est le
    cas, ces tests sont le seul garde-fou contre la derive."""

    CAS = [
        ("new-short", ["SKILL.md", "scripts/new_short.py", "assets/state_template.json"]),
        ("short-state", ["SKILL.md", "scripts/short_state.py"]),
    ]

    def test_les_copies_manuelles_correspondent_a_la_source(self):
        for skill, fichiers in self.CAS:
            for relatif in fichiers:
                with self.subTest(skill=skill, fichier=relatif):
                    source = os.path.join(RACINE_DEPOT, "skills", skill, relatif)
                    deploye = os.path.join(CLAUDE_SKILLS, skill, relatif)
                    self.assertTrue(os.path.isfile(deploye), f"{skill}/{relatif} non deploye")
                    if relatif.endswith(".json"):
                        self.assertEqual(json.loads(_lire(deploye)), json.loads(_lire(source)))
                    else:
                        # Comparaison insensible aux fins de ligne : la source est
                        # en CRLF, la copie deployee en LF.
                        self.assertEqual(_lire(deploye).replace("\r\n", "\n"),
                                          _lire(source).replace("\r\n", "\n"),
                                          f"{skill}/{relatif} a derive de skills/{skill}/")


if __name__ == "__main__":
    unittest.main()
