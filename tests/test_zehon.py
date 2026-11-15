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

    def test_image_reprise_sans_prompt(self):
        reprise = SCENES.replace("| scene_004.png | pan_droite |", "| scene_001.png | pan_droite |") \
                        .replace("**scene_004** — *c*\n> z\n\n", "")
        r = self.lancer(reprise)
        self.assertEqual(r.returncode, 0, r.stdout)
        self.assertIn("1 images reprises", r.stdout)

    def test_image_reprise_d_une_scene_a_venir(self):
        r = self.lancer(SCENES.replace("| scene_001.png | zoom_avant |", "| scene_004.png | zoom_avant |"))
        self.assertEqual(r.returncode, 1)
        self.assertIn("attendu scene_001.png", r.stdout)


def script_long(sauf_que, nombres_hook):
    hook = "Regarde ta table. " + " ".join(f"Il y en a {k + 2} ici." for k in range(nombres_hook))
    temps = "\n".join(f"Le potier chauffe son four pendant des jours entiers. Sauf que rien ne fond."
                      for _ in range(sauf_que))
    return f"# Script\n\n## Hook\n\n{hook} Alors pourquoi ?\n\n## Q1 — T1\n\n{temps}\nEt toi ?\n"


class VerificateurDeScript(unittest.TestCase):
    def lancer(self, contenu, nom="02_script.md", *options):
        with tempfile.TemporaryDirectory() as d:
            (Path(d) / nom).write_text(contenu, encoding="utf-8")
            return subprocess.run([sys.executable, str(VERIFIER), str(Path(d) / nom), *options],
                                  capture_output=True, text=True)

    def test_trop_de_sauf_que(self):
        self.assertIn("6 « Sauf que » (au plus 5)", self.lancer(script_long(6, 0)).stdout)
        self.assertNotIn("au plus 5", self.lancer(script_long(5, 0)).stdout)

    def test_trop_de_nombres_dans_le_hook(self):
        self.assertIn("3 nombres dans le hook", self.lancer(script_long(1, 3)).stdout)
        self.assertNotIn("nombres dans le hook", self.lancer(script_long(1, 2)).stdout)

    def test_un_nombre_avec_espace_ou_virgule_compte_pour_un(self):
        v = charger(VERIFIER)
        self.assertEqual(len(v.nombres("En 1884, 3,6 tonnes contre 2 834 tonnes, soit 8 %.")), 4)

    def test_duree_au_debit_de_la_voix(self):
        voix = "\n".join(["Le potier chauffe son four pendant des jours entiers sans rien obtenir."] * 100)
        self.assertIn("~6.0 min à 3.36 mots/s", self.lancer(voix, "02_script_voix.txt").stdout)
        self.assertIn("~6.7 min à 3 mots/s", self.lancer(voix, "02_script_voix.txt", "--debit", "3").stdout)
        self.assertEqual(self.lancer(voix, "02_script_voix.txt", "--debit", "vite").returncode, 2)


if __name__ == "__main__":
    unittest.main()
