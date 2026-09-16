"""
Rendu Remotion bout en bout a partir de props construites par
construire_props.py (§13 etape 5). Saute silencieusement si Node/Remotion
ou un Chromium exploitable ne sont pas disponibles (l'essentiel de la
logique est deja couvert par test_construire_props.py, qui ne depend pas
de Node).
"""

import glob
import json
import os
import shutil
import struct
import subprocess
import sys
import tempfile
import unittest

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
COMPOSANTS = os.path.join(REPO_ROOT, "composants")
CONSTRUIRE_PROPS = os.path.join(REPO_ROOT, "agents", "short-monteur", "scripts", "construire_props.py")


def _trouver_chromium():
    for motif in ("/opt/pw-browsers/chromium_headless_shell-*/chrome-linux/headless_shell",
                  "/opt/pw-browsers/chromium-*/chrome-linux/chrome"):
        trouves = sorted(glob.glob(motif))
        if trouves:
            return trouves[-1]
    return None


def _remotion_pret():
    return os.path.isdir(os.path.join(COMPOSANTS, "node_modules"))


@unittest.skipUnless(_remotion_pret(), "composants/node_modules absent (npm install non fait)")
class TestRenduRemotion(unittest.TestCase):
    def test_rendu_a_partir_des_props_construites(self):
        chromium = _trouver_chromium()
        tmp = tempfile.mkdtemp(prefix="render_test_")
        try:
            charte_path = os.path.join(tmp, "charte.json")
            storyboard_path = os.path.join(tmp, "storyboard.json")
            timestamps_path = os.path.join(tmp, "timestamps.json")
            props_path = os.path.join(tmp, "props.json")
            sortie_mp4 = os.path.join(tmp, "video.mp4")

            with open(charte_path, "w", encoding="utf-8") as f:
                json.dump({
                    "couleurs": {"fond": "#0B0F14", "texte_principal": "#FFF",
                                 "accent": "#5B8CFF", "accent_secondaire": "#FFD166"},
                    "typographie": {"sous_titres": {"famille": "Arial", "taille_px": 60, "graisse": "bold"}},
                    "rythme": {"duree_transition_s": 0.2, "easing": "ease-in-out"},
                    "format": {"largeur_px": 1080, "hauteur_px": 1920, "fps": 30},
                }, f)
            with open(storyboard_path, "w", encoding="utf-8") as f:
                json.dump({"scenes": [
                    {"id": "s1", "composant": "TitleCard", "duree_s": 1, "params": {"texte": "Test"}}
                ]}, f)
            with open(timestamps_path, "w", encoding="utf-8") as f:
                json.dump([{"word": "Test", "start": 0.1, "end": 0.5}], f)

            p = subprocess.run([sys.executable, CONSTRUIRE_PROPS, "--charte", charte_path,
                                 "--storyboard", storyboard_path, "--timestamps", timestamps_path,
                                 "--sortie", props_path], capture_output=True, text=True)
            self.assertEqual(p.returncode, 0, p.stderr)

            env = dict(os.environ)
            if chromium:
                env["REMOTION_BROWSER_EXECUTABLE"] = chromium

            rendu = subprocess.run(
                ["npx", "remotion", "render", "src/index.ts", "Video", sortie_mp4, f"--props={props_path}"],
                cwd=COMPOSANTS, capture_output=True, text=True, env=env, timeout=180,
            )
            self.assertEqual(rendu.returncode, 0, rendu.stdout + rendu.stderr)
            self.assertTrue(os.path.isfile(sortie_mp4))
            self.assertGreater(os.path.getsize(sortie_mp4), 0)
        finally:
            shutil.rmtree(tmp, ignore_errors=True)

    def test_dimensions_suivent_la_charte(self):
        """Le format fait partie de la charte : une charte paysage doit rendre
        en paysage. Les dimensions etaient en dur sur <Composition>, ce qui
        rendait `charte.format` decoratif pour deux de ses trois valeurs."""
        chromium = _trouver_chromium()
        tmp = tempfile.mkdtemp(prefix="render_format_")
        try:
            props_path = os.path.join(tmp, "props.json")
            sortie_png = os.path.join(tmp, "image.png")
            with open(props_path, "w", encoding="utf-8") as f:
                json.dump({
                    "charte": {
                        "couleurs": {"fond": "#0B0F14", "texte_principal": "#FFF",
                                     "accent": "#5B8CFF", "accent_secondaire": "#FFD166"},
                        "typographie": {"sous_titres": {"famille": "Arial", "taille_px": 60,
                                                        "graisse": "bold"}},
                        "rythme": {"duree_transition_s": 0.2, "easing": "ease-in-out"},
                        "format": {"largeur_px": 1920, "hauteur_px": 1080, "fps": 30},
                    },
                    "scenes": [{"id": "s1", "composant": "TitleCard", "duree_s": 1,
                                "params": {"texte": "Paysage"}}],
                    "mots": [{"mot": "Paysage", "debut_s": 0.1, "fin_s": 0.5}],
                }, f)

            env = dict(os.environ)
            if chromium:
                env["REMOTION_BROWSER_EXECUTABLE"] = chromium

            rendu = subprocess.run(
                ["npx", "remotion", "still", "src/index.ts", "Video", sortie_png,
                 f"--props={props_path}", "--frame=0"],
                cwd=COMPOSANTS, capture_output=True, text=True, env=env, timeout=180,
            )
            self.assertEqual(rendu.returncode, 0, rendu.stdout + rendu.stderr)

            # En-tete PNG : largeur et hauteur en big-endian a l'offset 16.
            with open(sortie_png, "rb") as f:
                largeur, hauteur = struct.unpack(">II", f.read(24)[16:24])
            self.assertEqual((largeur, hauteur), (1920, 1080))
        finally:
            shutil.rmtree(tmp, ignore_errors=True)


if __name__ == "__main__":
    unittest.main()
