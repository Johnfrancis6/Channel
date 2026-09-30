"""video-maker : lecture de 03_scenes.md, calage sur la voix, titres, et un vrai rendu miniature."""
import importlib.util
import json
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

import numpy as np

RACINE = Path(__file__).resolve().parent.parent
MONTER = RACINE / "zehon" / "video-maker" / "scripts" / "monter.py"


def charger():
    spec = importlib.util.spec_from_file_location("monter", MONTER)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


m = charger()

SCENES = """# Scènes

| n° | type | texte dit | image | mouvement | texte animé | crédit |
|---|---|---|---|---|---|---|
| 1 | image | Regarde la salière sur ta table. | scene_001.png | zoom_avant | — | — |
| 2 | video | Il y a 8 000 ans, on faisait bouillir l'eau. | clips/scene_002.mp4 | — | 8 000 ans | — |
| 3 | titre | — | — | — | Comment sort-on le sel ? | — |
| 4 | image | Sauf que le feu coûte cher. Très cher. | scene_004.png | pan_droite | — | — |
"""


def voix_de_test():
    """La transcription horodatée des 3 scènes dites, comme l'écrit le notebook (chiffres compris)."""
    phrases = ["Regarde la salière sur ta table.", "Il y a 8000 ans, on faisait bouillir l'eau.",
               "Sauf que le feu coûte cher.", "Très cher."]
    mots, bornes, t = [], [], 0.0
    for n, p in enumerate(phrases, 1):
        debut = t
        for mot in p.split():
            mots.append({"mot": mot, "debut_s": round(t, 3), "fin_s": round(t + 0.3, 3)})
            t += 0.35
        bornes.append({"n": n, "texte": p, "debut_s": round(debut, 3), "fin_s": round(t - 0.05, 3)})
        t += 0.3
    return {"duree_s": round(t - 0.3, 3), "phrases": bornes, "mots": mots}


class Dossier:
    ouverts = []

    def __init__(self, images=(1, 2, 4)):
        self.tmp = tempfile.TemporaryDirectory()
        Dossier.ouverts.append(self.tmp)
        self.d = Path(self.tmp.name)
        (self.d / "03_scenes.md").write_text(SCENES, encoding="utf-8")
        (self.d / "images").mkdir()
        (self.d / "voix").mkdir()
        for n in images:
            image = np.zeros((96, 172, 3), np.uint8)
            image[:, :, n % 3] = 180
            import cv2
            cv2.imwrite(str(self.d / "images" / f"scene_{n:03d}.jpg"), image)
        (self.d / "voix" / "mots.json").write_text(json.dumps(voix_de_test()), encoding="utf-8")


def tearDownModule():
    for tmp in Dossier.ouverts:
        tmp.cleanup()


class Nombres(unittest.TestCase):
    def test_en_lettres(self):
        self.assertEqual(m.en_lettres(1344), "mille trois cent quarante-quatre")
        self.assertEqual(m.en_lettres(80), "quatre-vingts")
        self.assertEqual(m.en_lettres(71), "soixante-et-onze")
        self.assertEqual(m.en_lettres(270000000), "deux cent soixante-dix millions")

    def test_jetons_du_script_et_de_whisper_se_rejoignent(self):
        self.assertEqual(m.jetons("il y a 8 000 ans"), m.jetons("il y a huit mille ans"))
        self.assertEqual(m.jetons("42 %"), ["quarante", "deux", "pour", "cent"])
        self.assertEqual(m.jetons("au 6e siècle"), m.jetons("au sixième siècle"))
        self.assertEqual(m.jetons("Duzdağı"), ["duzdagi"])


class Scenes(unittest.TestCase):
    def test_lecture(self):
        d = Dossier()
        scenes = m.lire_scenes(d.d / "03_scenes.md")
        self.assertEqual([s.type for s in scenes], ["image", "video", "titre", "image"])
        self.assertEqual(scenes[1].texte_anime, "8 000 ans")

    def test_image_manquante_nommee(self):
        d = Dossier(images=(1, 2))
        with self.assertRaises(m.ErreurMontage) as e:
            m.planifier(d.d)
        self.assertIn("scène 4", str(e.exception))

    def test_extrait_n_exige_que_ses_images(self):
        d = Dossier(images=(1, 2))
        scenes, *_ = m.planifier(d.d, extrait=(1, 2))
        self.assertEqual(len(scenes), 4)

    def test_extensions_et_clip_anim(self):
        d = Dossier()
        (d.d / "clips").mkdir()
        (d.d / "clips" / "anim_002.mp4").write_bytes(b"")
        scenes, *_ = m.planifier(d.d)
        self.assertEqual(scenes[0].fichier_image.name, "scene_001.jpg")
        self.assertEqual(scenes[1].fichier_clip.name, "anim_002.mp4")


class Calage(unittest.TestCase):
    def test_coupes_dans_les_pauses_et_titre_ajoute(self):
        d = Dossier()
        scenes, voix, insertions, total, avert = m.planifier(d.d)
        un, deux, titre, quatre = scenes
        self.assertEqual(un.debut, 0)
        # la coupe 1→2 tombe au milieu de la pause entre les phrases 1 et 2
        p = voix["phrases"]
        self.assertAlmostEqual(deux.debut, (p[0]["fin_s"] + p[1]["debut_s"]) / 2, places=3)
        self.assertEqual(titre.debut, deux.fin)
        self.assertAlmostEqual(titre.duree, m.TITRE_S)
        self.assertEqual(insertions, [(deux.fin, m.TITRE_S)])
        self.assertAlmostEqual(quatre.debut, titre.fin)
        self.assertAlmostEqual(total, voix["duree_s"] + m.TITRE_S + m.FIN_S, places=3)
        self.assertTrue(all(s.couverture == 1.0 for s in scenes if s.type != "titre"))
        # le texte animé vient sur « 8000 », mais reste au moins TEXTE_MIN_S à l'écran
        self.assertLessEqual(deux.apparition, deux.fin - m.TEXTE_MIN_S + 1e-6)


class Musique(unittest.TestCase):
    def test_boucle_sans_coupure(self):
        taux = m.TAUX_AUDIO
        nappe = np.ones(10 * taux, np.float32)
        boucle = m.boucler(nappe, 25 * taux)
        self.assertEqual(len(boucle), 25 * taux)
        milieu = boucle[3 * taux:-4 * taux]  # hors entrée et sortie : ni trou ni saut aux reprises
        self.assertGreater(milieu.min(), 0.99)
        self.assertLess(milieu.max(), 1.42)
        self.assertEqual(boucle[0], 0.0)
        self.assertAlmostEqual(float(boucle[-1]), 0.0)


class SousTitres(unittest.TestCase):
    def test_mots_affiches_d_un_tenant(self):
        self.assertEqual(m.mots_du_texte("il y a 8 000 ans, 42 % de l'eau ?"),
                         ["il", "y", "a", "8 000", "ans,", "42 %", "de", "l'eau ?"])
        self.assertEqual(m.mots_du_texte("de « sal », le sel"), ["de", "« sal »,", "le", "sel"])
        self.assertEqual(m.mots_du_texte("un conduit de 21 km part"), ["un", "conduit", "de", "21 km", "part"])

    def test_mots_cales_sur_la_voix_et_decales_par_le_titre(self):
        d = Dossier()
        scenes, voix, *_ = m.planifier(d.d)
        mots, cales = m.minuter_mots(scenes, voix)
        self.assertEqual(cales, 1.0)
        self.assertEqual(" ".join(x.texte for x in mots[:2]), "Regarde la")
        huit = next(x for x in mots if x.texte == "8 000")
        self.assertAlmostEqual(huit.debut, voix["mots"][9]["debut_s"])  # « 8000 » dans la voix
        sauf = next(x for x in mots if x.texte == "Sauf")
        self.assertAlmostEqual(sauf.debut, voix["mots"][15]["debut_s"] + m.TITRE_S)
        self.assertEqual(sorted(x.debut for x in mots), [x.debut for x in mots])

    def test_groupes_courts_equilibres_et_hors_titre(self):
        d = Dossier()
        scenes, voix, *_ = m.planifier(d.d)
        mots, _ = m.minuter_mots(scenes, voix)
        groupes = m.grouper(mots, scenes, 20, 4)
        self.assertEqual(" ".join(g.texte for g in groupes), " ".join(x.texte for x in mots))
        self.assertEqual(groupes[0].texte, "Regarde la salière")
        self.assertTrue(all(len(g.mots) <= 4 and len(g.texte) <= 20 for g in groupes))
        self.assertEqual([g.texte for g in groupes][-2:], ["coûte cher.", "Très cher."])  # fin de phrase
        titre = scenes[2]
        self.assertTrue(all(g.fin <= titre.debut or g.debut >= titre.fin for g in groupes))
        self.assertFalse(any(g.mots[-1].texte.lower() in m.PETITS_MOTS for g in groupes))

    def test_srt(self):
        d = Dossier()
        scenes, voix, *_ = m.planifier(d.d)
        mots, _ = m.minuter_mots(scenes, voix)
        n = m.ecrire_srt(mots, scenes, d.d / "rendu" / "sous_titres.srt")
        blocs = (d.d / "rendu" / "sous_titres.srt").read_text(encoding="utf-8").strip().split("\n\n")
        self.assertEqual(len(blocs), n)
        self.assertRegex(blocs[0], r"^1\n00:00:00,000 --> 00:00:0\d,\d{3}\nRegarde la salière sur ta table\.$")
        self.assertEqual(m.deux_lignes("Et il y a moins de 300 ans, en France, en faire passer"),
                         "Et il y a moins de 300 ans,\nen France, en faire passer")


@unittest.skipUnless(shutil.which("ffmpeg"), "ffmpeg absent")
class Rendu(unittest.TestCase):
    def test_rendu_miniature_passe_le_controle(self):
        d = Dossier()
        voix = voix_de_test()
        t = np.arange(int(voix["duree_s"] * 24000)) / 24000
        signal = (0.3 * np.sin(2 * np.pi * 220 * t)).astype(np.float32)
        subprocess.run(["ffmpeg", "-v", "error", "-f", "f32le", "-ar", "24000", "-ac", "1", "-i", "-",
                        str(d.d / "voix" / "voix.wav")], input=signal.tobytes(), check=True)
        code = m.main([str(d.d), "--taille", "320x180", "--preset", "ultrafast"])
        self.assertEqual(code, 0)
        rapport = json.loads((d.d / "rendu" / "rapport.json").read_text(encoding="utf-8"))
        self.assertTrue(rapport["pret"], rapport["controle"])

    def test_rendu_avec_sous_titres(self):
        d = Dossier()
        voix = voix_de_test()
        t = np.arange(int(voix["duree_s"] * 24000)) / 24000
        signal = (0.3 * np.sin(2 * np.pi * 220 * t)).astype(np.float32)
        subprocess.run(["ffmpeg", "-v", "error", "-f", "f32le", "-ar", "24000", "-ac", "1", "-i", "-",
                        str(d.d / "voix" / "voix.wav")], input=signal.tobytes(), check=True)
        code = m.main([str(d.d), "--taille", "320x180", "--preset", "ultrafast", "--sous-titres"])
        self.assertEqual(code, 0)
        rapport = json.loads((d.d / "rendu" / "rapport.json").read_text(encoding="utf-8"))
        self.assertTrue(rapport["sous_titres_incrustes"])
        self.assertTrue((d.d / "rendu" / "sous_titres.srt").is_file())
        # le verdict court et l'aperçu, ce que Claude lit après un rendu dans Colab
        brut = (d.d / "rendu" / "verdict.json").read_bytes()
        self.assertLessEqual(len(brut), m.VERDICT_MAX)
        verdict = json.loads(brut)
        self.assertTrue(verdict["pret"])
        self.assertEqual(verdict["sortie"], "video.mp4")
        for cle in ("controle", "avertissements", "duree_s", "rendu_s"):
            self.assertIn(cle, verdict)
        apercu = sorted(p.name for p in (d.d / "rendu" / "apercu").glob("*.jpg"))
        self.assertEqual(apercu, verdict["apercu"])
        self.assertEqual(len(apercu), 6)
        self.assertIn("2_titre.jpg", apercu)
        self.assertIn("4_sous_titres.jpg", apercu)
        self.assertIn("3_milieu.jpg", apercu)  # la scène 2 n'a pas de plan animé
        # le bandeau est bien là : le bas de l'image, pendant la première phrase, n'est plus uni
        image = subprocess.run(["ffmpeg", "-v", "error", "-ss", "1.0", "-i", str(d.d / "rendu" / "video.mp4"),
                                "-frames:v", "1", "-f", "rawvideo", "-pix_fmt", "gray", "-"],
                               capture_output=True, check=True).stdout
        bas = np.frombuffer(image, np.uint8).reshape(180, 320)[150:175]
        self.assertGreater(bas.std(), 20)


class Verdict(unittest.TestCase):
    def test_sous_la_limite_meme_avec_beaucoup_d_avertissements(self):
        with tempfile.TemporaryDirectory() as tmp:
            chemin = Path(tmp) / "verdict.json"
            v = m.ecrire_verdict(chemin, {"pret": True, "controle": ["✓ image : 1920×1080"] * 5,
                                          "avertissements": [f"scène {n} : " + "x" * 200 for n in range(40)]})
            self.assertLessEqual(len(chemin.read_bytes()), m.VERDICT_MAX)
            self.assertIn("autre(s) dans le rapport", v["avertissements"][-1])
            self.assertTrue(all(len(a) <= 110 for a in v["avertissements"]))


class Lanceur(unittest.TestCase):
    """Les lanceurs Drive : un formulaire et quelques lignes, le vrai notebook vient du dépôt."""
    NOTEBOOKS = RACINE / "zehon" / "notebooks"

    def charger_lanceur(self):
        spec = importlib.util.spec_from_file_location("lanceur", self.NOTEBOOKS / "lanceur.py")
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module

    def test_reglages_du_lanceur_par_dessus_et_arret_net(self):
        lanceur = self.charger_lanceur()
        cellule = lambda source, tags=(): {"cell_type": "code", "metadata": {"tags": list(tags)}, "source": [source]}
        nb = {"cells": [cellule('A = 1\nB = 2', ["reglages"]), cellule("C = A + B"),
                        cellule('raise SystemExit("stop")'), cellule("D = 4")]}
        with tempfile.TemporaryDirectory() as tmp:
            (Path(tmp) / "essai.ipynb").write_text(json.dumps(nb), encoding="utf-8")
            lanceur.ICI = Path(tmp)
            espace = {}
            with self.assertRaises(SystemExit):
                lanceur.executer("essai.ipynb", {"A": 10}, espace)
        self.assertEqual((espace["A"], espace["B"], espace["C"]), (10, 2, 12))  # B garde sa valeur par défaut
        self.assertTrue(espace["DEPOT_PRET"])
        self.assertNotIn("D", espace)

    def test_lanceurs_accordes_aux_notebooks(self):
        for lanceur, cible in [("lanceur_montage.ipynb", "montage_zehon.ipynb"), ("lanceur_voix.ipynb", "voix_zehon.ipynb")]:
            code = "".join(json.loads((self.NOTEBOOKS / lanceur).read_text(encoding="utf-8"))["cells"][1]["source"])
            nb = json.loads((self.NOTEBOOKS / cible).read_text(encoding="utf-8"))
            reglages = [c for c in nb["cells"] if "reglages" in c.get("metadata", {}).get("tags", [])]
            self.assertEqual(len(reglages), 1, cible)
            connus = set(re.findall(r"^(\w+) =", "".join(reglages[0]["source"]), re.M)) | {"BRANCHE"}
            formulaire = re.findall(r"^(\w+) = .*# @param", code, re.M)
            self.assertTrue(formulaire)
            self.assertLessEqual(set(formulaire), connus, lanceur)
            self.assertIn(f'lanceur.executer("{cible}"', code)
            self.assertLess(len(code.splitlines()), 45)


class NotebookMontage(unittest.TestCase):
    """montage_zehon.ipynb : du Python valide, et seulement des options que monter.py connaît."""

    def test_cellules_et_options(self):
        import ast
        nb = json.loads((RACINE / "zehon" / "notebooks" / "montage_zehon.ipynb").read_text(encoding="utf-8"))
        code = "\n".join("".join(c["source"]) for c in nb["cells"] if c["cell_type"] == "code")
        ast.parse(code)
        aide = subprocess.run([sys.executable, str(MONTER), "--help"], capture_output=True, text=True).stdout
        montage = "\n".join("".join(c["source"]) for c in nb["cells"] if "lancer(" in "".join(c["source"]))
        for option in set(re.findall(r'"(--[a-z-]+)"', montage)):
            self.assertIn(option, aide, f"{option} : inconnue de monter.py")
        self.assertIn("monter.py", code)
        self.assertNotIn("def rendre(", code)  # le code du montage n'est pas recopié dans le notebook


if __name__ == "__main__":
    unittest.main()
