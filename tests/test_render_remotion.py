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
import zlib

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
COMPOSANTS = os.path.join(REPO_ROOT, "composants")
CONSTRUIRE_PROPS = os.path.join(REPO_ROOT, "agents", "short-monteur", "scripts", "construire_props.py")


def _bloc_png(nom, donnees):
    corps = nom + donnees
    return struct.pack(">I", len(donnees)) + corps + struct.pack(">I", zlib.crc32(corps))


def _ecrire_png_uni(chemin, largeur, hauteur, rgb):
    """Ecrit un PNG d'une seule couleur. Sert d'asset de test.

    Une couleur pleine est ce qui rend l'assertion lisible : apres zoom,
    recadrage et `objectFit: cover`, elle reste exactement elle-meme, alors
    qu'une image quelconque ne permettrait que de dire « ca a change ».
    """
    brut = b"".join(b"\x00" + bytes(rgb) * largeur for _ in range(hauteur))
    entete = struct.pack(">IIBBBBB", largeur, hauteur, 8, 2, 0, 0, 0)
    with open(chemin, "wb") as f:
        f.write(b"\x89PNG\r\n\x1a\n"
                + _bloc_png(b"IHDR", entete)
                + _bloc_png(b"IDAT", zlib.compress(brut))
                + _bloc_png(b"IEND", b""))


def _lire_pixels_png(chemin):
    """(largeur, hauteur, [(r,g,b), ...]) d'un PNG 8 bits RGB ou RGBA.

    Ecrit a la main parce que Pillow n'est pas une dependance du depot, et
    parce que verifier un rendu sur autre chose que les pixels reels revient
    a verifier le typecheck une seconde fois.
    """
    donnees = _lire_octets(chemin)
    assert donnees[:8] == b"\x89PNG\r\n\x1a\n", "pas un PNG"
    position, idat, entete = 8, b"", None
    while position < len(donnees):
        taille = struct.unpack(">I", donnees[position:position + 4])[0]
        nom = donnees[position + 4:position + 8]
        corps = donnees[position + 8:position + 8 + taille]
        if nom == b"IHDR":
            entete = struct.unpack(">IIBBBBB", corps)
        elif nom == b"IDAT":
            idat += corps
        elif nom == b"IEND":
            break
        position += 12 + taille

    largeur, hauteur, profondeur, type_couleur = entete[0], entete[1], entete[2], entete[3]
    assert profondeur == 8 and type_couleur in (2, 6), (profondeur, type_couleur)
    canaux = 3 if type_couleur == 2 else 4
    brut = zlib.decompress(idat)
    octets_ligne = largeur * canaux

    pixels = []
    precedente = bytearray(octets_ligne)
    index = 0
    for _ in range(hauteur):
        filtre = brut[index]
        ligne = bytearray(brut[index + 1:index + 1 + octets_ligne])
        index += 1 + octets_ligne
        for i in range(octets_ligne):
            a = ligne[i - canaux] if i >= canaux else 0
            b = precedente[i]
            c = precedente[i - canaux] if i >= canaux else 0
            if filtre == 1:
                ligne[i] = (ligne[i] + a) & 0xFF
            elif filtre == 2:
                ligne[i] = (ligne[i] + b) & 0xFF
            elif filtre == 3:
                ligne[i] = (ligne[i] + (a + b) // 2) & 0xFF
            elif filtre == 4:
                p = a + b - c
                pa, pb, pc = abs(p - a), abs(p - b), abs(p - c)
                pred = a if (pa <= pb and pa <= pc) else (b if pb <= pc else c)
                ligne[i] = (ligne[i] + pred) & 0xFF
        for x in range(largeur):
            d = x * canaux
            pixels.append((ligne[d], ligne[d + 1], ligne[d + 2]))
        precedente = ligne
    return largeur, hauteur, pixels


def _lire_octets(chemin):
    with open(chemin, "rb") as f:
        return f.read()


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


@unittest.skipUnless(_remotion_pret(), "composants/node_modules absent (npm install non fait)")
class TestInsertFootage(unittest.TestCase):
    """L'insert de footage apparait vraiment a l'ecran, et seulement pendant
    sa fenetre.

    Le tuyau footage -> ecran a deja ete ecrit une fois de bout en bout sans
    qu'un seul pixel reel y passe : trois composants `Plan*` au registre,
    alimentes par rien. Un test qui n'irait pas jusqu'aux pixels rendus
    referait exactement la meme erreur — il verifierait que le contrat est
    ecrit, pas qu'il transporte quelque chose.
    """

    COULEUR = (255, 0, 255)  # magenta : aucune couleur de la charte ne s'en approche

    def setUp(self):
        self.tmp = tempfile.mkdtemp(prefix="render_insert_")
        self.video_id = "2026-01-01_v01"
        self.dossier_public = os.path.join(COMPOSANTS, "public", "assets", self.video_id)

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)
        shutil.rmtree(self.dossier_public, ignore_errors=True)

    def _props(self):
        """Props construites par le vrai construire_props.py, ressources comprises."""
        dossier_video = os.path.join(self.tmp, "videos", self.video_id)
        os.makedirs(dossier_video)
        asset = os.path.join(dossier_video, "demo.png")
        _ecrire_png_uni(asset, 320, 180, self.COULEUR)

        chemins = {nom: os.path.join(self.tmp, nom) for nom in
                   ("charte.json", "storyboard.json", "timestamps.json", "props.json")}
        with open(chemins["charte.json"], "w", encoding="utf-8") as f:
            json.dump({
                "couleurs": {"fond": "#0B0F14", "texte_principal": "#FFF",
                             "accent": "#5B8CFF", "accent_secondaire": "#FFD166"},
                "typographie": {"sous_titres": {"famille": "Arial", "taille_px": 60,
                                                "graisse": "bold"}},
                "rythme": {"duree_transition_s": 0.2, "easing": "ease-in-out"},
                "format": {"largeur_px": 1080, "hauteur_px": 1920, "fps": 30},
                "formats": {"long": {"largeur_px": 1280, "hauteur_px": 720, "fps": 30}},
            }, f)
        with open(chemins["storyboard.json"], "w", encoding="utf-8") as f:
            json.dump({"format_video": "long", "scenes": [{
                "id": "s1", "composant": "TitleCard", "duree_s": 6,
                "params": {"texte": "Segment"},
                # L'insert ne couvre qu'un tiers de la scene : c'est un
                # detail dans une scene animee, pas un plan.
                "inserts": [{"cle": "demo", "debut_s": 2.0, "duree_s": 2.0}],
            }]}, f)
        with open(chemins["timestamps.json"], "w", encoding="utf-8") as f:
            json.dump([{"word": "Segment", "start": 0.1, "end": 0.5}], f)
        with open(os.path.join(dossier_video, "05b_ressources.json"), "w", encoding="utf-8") as f:
            json.dump({"video_id": self.video_id,
                       "ressources": {"demo": {"type": "image", "chemin": "demo.png"}}}, f)

        p = subprocess.run(
            [sys.executable, CONSTRUIRE_PROPS, "--charte", chemins["charte.json"],
             "--storyboard", chemins["storyboard.json"],
             "--timestamps", chemins["timestamps.json"],
             "--ressources", os.path.join(dossier_video, "05b_ressources.json"),
             "--sortie", chemins["props.json"]],
            capture_output=True, text=True, cwd=COMPOSANTS)
        self.assertEqual(p.returncode, 0, p.stderr)
        return chemins["props.json"], json.loads(p.stdout)

    def _still(self, props_path, frame):
        sortie = os.path.join(self.tmp, f"frame{frame}.png")
        env = dict(os.environ)
        chromium = _trouver_chromium()
        if chromium:
            env["REMOTION_BROWSER_EXECUTABLE"] = chromium
        rendu = subprocess.run(
            ["npx", "remotion", "still", "src/index.ts", "Video", sortie,
             f"--props={props_path}", f"--frame={frame}"],
            cwd=COMPOSANTS, capture_output=True, text=True, env=env, timeout=180)
        self.assertEqual(rendu.returncode, 0, rendu.stdout + rendu.stderr)
        return _lire_pixels_png(sortie)

    def _compte_couleur(self, pixels):
        # Tolerance : l'echelle et le lissage des bords deplacent legerement
        # les composantes. Le fond de charte en est a des centaines d'unites.
        return sum(1 for r, v, b in pixels
                   if abs(r - self.COULEUR[0]) < 24 and v < 40 and abs(b - self.COULEUR[2]) < 24)

    def test_l_insert_n_existe_que_dans_sa_fenetre(self):
        props_path, resume = self._props()
        self.assertEqual(resume["nb_inserts"], 1)
        self.assertEqual(resume["format_video"], "long")
        # La charte declare le format long : la composition doit etre paysage.
        self.assertEqual(resume["dimensions"]["largeur_px"], 1280)

        largeur, hauteur, avant = self._still(props_path, 30)     # 1,0 s
        _, _, pendant = self._still(props_path, 90)               # 3,0 s
        _, _, apres = self._still(props_path, 160)                # 5,3 s

        self.assertEqual((largeur, hauteur), (1280, 720))
        surface = largeur * hauteur
        pixels_insert = self._compte_couleur(pendant)

        self.assertEqual(self._compte_couleur(avant), 0,
                         "l'insert est visible avant son debut")
        self.assertEqual(self._compte_couleur(apres), 0,
                         "l'insert est encore visible apres sa fin")
        self.assertGreater(pixels_insert, surface * 0.05,
                           "l'insert ne couvre presque rien : cadre non rendu ?")
        # Et il ne remplit pas le cadre : la scene animee doit rester visible
        # dessous, sinon l'insert est redevenu un plan.
        self.assertLess(pixels_insert, surface * 0.75,
                        "l'insert occupe tout l'ecran : ce n'est plus un insert")


RENDRE_VIDEO = os.path.join(REPO_ROOT, "agents", "short-monteur", "scripts", "rendre_video.py")


@unittest.skipUnless(_remotion_pret(), "composants/node_modules absent (npm install non fait)")
class TestRenduParTranches(unittest.TestCase):
    """Le rendu d'un format long se reprend la ou il s'est arrete.

    Un `remotion render` monolithique de 15 minutes rend 27 000 frames sans
    aucun point de reprise : un echec a 80 % perd tout, et une session trop
    longue peut ne jamais atteindre la fin. Le defaut ne se voyait pas sur des
    videos de 50 s — il devient bloquant des qu'elles durent.
    """

    def setUp(self):
        self.tmp = tempfile.mkdtemp(prefix="render_tranches_")
        self.video_id = "2026-01-01_v01"
        self.dossier = os.path.join(self.tmp, "videos", self.video_id)
        os.makedirs(self.dossier)
        self.props = os.path.join(self.dossier, "props.json")
        with open(self.props, "w", encoding="utf-8") as f:
            json.dump({
                "charte": {
                    "couleurs": {"fond": "#0B0F14", "texte_principal": "#FFF",
                                 "accent": "#5B8CFF", "accent_secondaire": "#FFD166"},
                    "typographie": {"sous_titres": {"famille": "Arial", "taille_px": 40,
                                                    "graisse": "bold"}},
                    "rythme": {"duree_transition_s": 0.2, "easing": "ease-in-out"},
                    "format": {"largeur_px": 640, "hauteur_px": 360, "fps": 30},
                },
                "format_video": "long",
                "scenes": [{"id": "s1", "composant": "TitleCard", "duree_s": 1,
                            "params": {"texte": "A"}},
                           {"id": "s2", "composant": "TitleCard", "duree_s": 1,
                            "params": {"texte": "B"}}],
                "mots": [{"mot": "A", "debut_s": 0.1, "fin_s": 0.5}],
            }, f)
        self.sortie = os.path.join(self.dossier, "06_video_finale.mp4")

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    @staticmethod
    def _json_final(stdout):
        """Dernier objet JSON de stdout.

        `rendre_video.py` herite volontairement de la sortie de `remotion`
        (progression en temps reel, non bufferisee) : son JSON de fin cohabite
        donc avec elle sur le meme flux.
        """
        debut = stdout.rfind("\n{")
        return json.loads(stdout[debut + 1:] if debut >= 0 else stdout)

    def rendre(self, *args):
        env = dict(os.environ)
        chromium = _trouver_chromium()
        if chromium:
            env["REMOTION_BROWSER_EXECUTABLE"] = chromium
        proc = subprocess.run(
            [sys.executable, RENDRE_VIDEO, "--video", self.video_id, "--root", self.tmp,
             "--props", self.props, "--sortie", self.sortie, *args],
            capture_output=True, text=True, env=env, timeout=600)
        return proc.returncode, self._json_final(proc.stdout), proc.stdout + proc.stderr

    @property
    def dossier_tranches(self):
        return self.sortie + ".tranches"

    def test_les_tranches_deja_rendues_sont_reprises(self):
        code, out, err = self.rendre("--tranche-s", "1", "--garder-tranches")
        self.assertEqual(code, 0, err)
        self.assertEqual(out["tranches"], 2)
        self.assertEqual(out["tranches_reprises"], 0)
        self.assertGreater(os.path.getsize(self.sortie), 0)

        # Deuxieme passage : tout est deja la, rien n'est re-rendu.
        code, out, err = self.rendre("--tranche-s", "1", "--garder-tranches")
        self.assertEqual(code, 0, err)
        self.assertEqual(out["tranches_reprises"], 2)

        # Une tranche perdue (echec, interruption) : elle seule est refaite.
        os.remove(os.path.join(self.dossier_tranches, "tranche_0001.mp4"))
        code, out, err = self.rendre("--tranche-s", "1", "--garder-tranches")
        self.assertEqual(code, 0, err)
        self.assertEqual(out["tranches_reprises"], 1)

    def test_les_tranches_sont_effacees_apres_un_recollage_reussi(self):
        code, out, err = self.rendre("--tranche-s", "1")
        self.assertEqual(code, 0, err)
        self.assertFalse(os.path.isdir(self.dossier_tranches),
                         "les tranches encombrent le Drive une fois le MP4 verifie")

    def test_un_short_reste_rendu_d_un_seul_bloc(self):
        # Le format long est un ajout : le chemin du Short ne change pas, et
        # un recollage inutile est un recollage a rater.
        code, out, err = self.rendre("--format-video", "short")
        self.assertEqual(code, 0, err)
        self.assertEqual(out["tranches"], 1)
        self.assertFalse(os.path.isdir(self.dossier_tranches))


if __name__ == "__main__":
    unittest.main()
