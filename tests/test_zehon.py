"""Garde-fous de la chaîne Zehon : miroir des skills à jour, vérificateur de content-maker."""
import importlib.util
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

RACINE = Path(__file__).resolve().parent.parent
VERIFIER = RACINE / "zehon" / "content-maker" / "scripts" / "verifier.py"


def charger(chemin):
    spec = importlib.util.spec_from_file_location(chemin.stem, chemin)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class MiroirDesSkills(unittest.TestCase):
    def test_miroir_et_archive_a_jour(self):
        sync = charger(RACINE / "zehon" / "synchroniser_skills.py")
        self.assertEqual(sync.ecarts(), [], "relancer : python3 zehon/synchroniser_skills.py")

    def test_archive_sans_evals(self):
        sync = charger(RACINE / "zehon" / "synchroniser_skills.py")
        for source in sync.skills():
            import io, zipfile
            noms = zipfile.ZipFile(io.BytesIO(sync.archive(source))).namelist()
            self.assertIn(f"{source.name}/SKILL.md", noms)
            self.assertFalse([n for n in noms if "/evals/" in n])


SCRIPT = """# Script

## Hook

Regarde la salière sur ta table, c'est sans doute ce qu'il y a de moins cher dans ta cuisine.
Sauf que pendant des millénaires, cette poudre blanche a été un trésor recherché partout.
Comment un trésor est-il devenu presque gratuit ?
"""

SCENES = """# Scènes

| n° | type | texte dit | image | mouvement | texte animé | crédit |
|---|---|---|---|---|---|---|
| 1 | image | Regarde la salière sur ta table, c'est sans doute ce qu'il y a de moins cher dans ta cuisine. | scene_001.png | zoom_avant | — | — |
| 2 | titre | — | — | — | Une question ? | — |
| 3 | video | Sauf que pendant des millénaires, cette poudre blanche a été un trésor recherché partout. | clips/scene_003.mp4 | — | — | — |
| 4 | image | Comment un trésor est-il devenu presque gratuit ? | scene_004.png | pan_droite | — | — |

**scene_001** — *a*
> x

**scene_003** — *b*
> y

**scene_004** — *c*
> z

**anim_003** — *d*
> w
"""


class VerificateurDeScenes(unittest.TestCase):
    def lancer(self, scenes):
        with tempfile.TemporaryDirectory() as d:
            (Path(d) / "02_script.md").write_text(SCRIPT, encoding="utf-8")
            (Path(d) / "03_scenes.md").write_text(scenes, encoding="utf-8")
            return subprocess.run([sys.executable, str(VERIFIER), str(Path(d) / "03_scenes.md"),
                                   "--script", str(Path(d) / "02_script.md")],
                                  capture_output=True, text=True)

    def test_scenes_valides(self):
        r = self.lancer(SCENES)
        self.assertEqual(r.returncode, 0, r.stdout)
        self.assertIn("dont 1 animées", r.stdout)

    def test_clip_sans_prompt_d_animation(self):
        r = self.lancer(SCENES.replace("**anim_003**", "**anim_099**"))
        self.assertEqual(r.returncode, 1)
        self.assertIn("aucun prompt d'animation **anim_003**", r.stdout)

    def test_clip_avec_mouvement_de_camera(self):
        r = self.lancer(SCENES.replace("clips/scene_003.mp4 | — |", "clips/scene_003.mp4 | zoom_avant |"))
        self.assertEqual(r.returncode, 1)
        self.assertIn("porte son propre mouvement", r.stdout)

    def test_texte_dit_qui_s_ecarte_du_script(self):
        r = self.lancer(SCENES.replace("recherché partout", "recherché ailleurs"))
        self.assertEqual(r.returncode, 1)
        self.assertIn("mot pour mot", r.stdout)


if __name__ == "__main__":
    unittest.main()
