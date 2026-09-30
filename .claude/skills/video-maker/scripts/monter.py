#!/usr/bin/env python3
"""Monte la vidéo d'un dossier Zehon : 03_scenes.md + images/ + clips/ + voix/ → rendu/video.mp4.

  python3 monter.py <dossier_video>                  # valide, cale, rend, contrôle
  python3 monter.py <dossier_video> --plan           # valide et cale seulement (rien n'est rendu)
  python3 monter.py <dossier_video> --scenes 1-10    # un extrait (scènes 1 à 10)

Le dossier contient 03_scenes.md, images/scene_NNN.(png|jpg), clips/(anim|scene)_NNN.mp4,
voix/voix.wav et voix/mots.json (écrits par le notebook voix_zehon.ipynb). Sortie : la vidéo,
et rendu/rapport.json (durée de chaque scène, avertissements, contrôle avant publication).

Les durées ne s'écrivent pas à la main : chaque scène est calée sur les mots horodatés de la
voix (mots.json), en retrouvant son « texte dit » dans la transcription. Les scènes « titre »
ajoutent une pause de TITRE_S secondes dans la voix, le temps de lire la question.

Dépendances : Python 3.9+, numpy, opencv-python(-headless), Pillow, et ffmpeg/ffprobe.
"""
import argparse
import bisect
import difflib
import json
import re
import subprocess
import sys
import tempfile
import unicodedata
from dataclasses import dataclass
from pathlib import Path

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

# ── La charte (nouveau_systeme.md §2), en chiffres ─────────────────────────────
LARGEUR, HAUTEUR, IPS = 1920, 1080, 30
FONDU_S = 0.6          # fondu enchaîné entre deux scènes (charte : 0,5 à 1 s)
TITRE_S = 3.0          # pause ajoutée dans la voix pour une scène « titre »
DEBUT_NOIR_S = 0.3     # la vidéo sort du noir
FIN_S = 1.5            # dernière image tenue après la voix, puis fondu au noir
ZOOM = 0.05            # zoom lent sur une scène (charte : 3 à 5 %)
PAN = 0.06             # marge du panoramique (part de l'image traversée : 80 % de cette marge)
MARGE_SOURCE = 1.10    # l'image est préparée 10 % plus grande que l'écran, pour bouger dedans
RALENTI_MAX = 1.35     # un plan animé trop court est ralenti jusque-là, puis figé sur sa dernière image
TEXTE_MIN_S = 2.5     # un texte animé reste au moins ce temps-là à l'écran (quitte à venir avant son mot)
IMAGE_MAX_S = 10.0     # garde-fou : une image qui reste plus longtemps est signalée
VOLUME_LUFS = -14.0   # volume de référence de YouTube (il baisse ce qui est plus fort, ne monte pas le reste)
CRETE_DBTP = -1.5     # limiteur (le contrôle refuse une crête au-dessus de −0,5 dB)
BLANC_CASSE = (244, 239, 230)

TYPES = {"image", "video", "titre"}
MOUVEMENTS = {"zoom_avant", "zoom_arriere", "pan_droite", "pan_gauche", "fixe"}
VIDE = {"", "—", "–", "-"}
EXT_IMAGES = (".png", ".jpg", ".jpeg", ".webp")
EXT_CLIPS = (".mp4", ".mov", ".webm", ".m4v")
POLICES = Path(__file__).resolve().parent.parent / "assets" / "polices"
POLICE_TITRE = POLICES / "Nunito-ExtraBold.ttf"
POLICE_TEXTE = POLICES / "IBMPlexMono-Medium.ttf"


class ErreurMontage(Exception):
    """Une erreur qui empêche le rendu, avec un message pour Franco."""


# ── Les nombres, pour comparer le texte écrit à ce que Whisper a entendu ──────
UNITES = "zéro un deux trois quatre cinq six sept huit neuf dix onze douze treize quatorze quinze seize".split()
DIZAINES = {1: "dix", 2: "vingt", 3: "trente", 4: "quarante", 5: "cinquante", 6: "soixante", 8: "quatre-vingt"}


def en_lettres(n):
    """Un entier (jusqu'à 999 999 999) en toutes lettres, à la française."""
    if n < 17:
        return UNITES[n]
    if n < 100:
        d, u = divmod(n, 10)
        if d in (7, 9):  # soixante-dix…, quatre-vingt-dix…
            return DIZAINES[d - 1] + ("-et-" if n == 71 else "-") + en_lettres(10 + u)
        if u == 0:
            return DIZAINES[d] + ("s" if d == 8 else "")
        return DIZAINES[d] + ("-et-un" if u == 1 and d != 8 else "-" + UNITES[u])
    if n < 1000:
        c, r = divmod(n, 100)
        tete = "cent" if c == 1 else UNITES[c] + " cent"
        return tete + (" " + en_lettres(r) if r else ("s" if c > 1 else ""))
    for taille, nom in ((10**6, "million"), (1000, "mille")):
        if n >= taille:
            q, r = divmod(n, taille)
            tete = nom if (q == 1 and taille == 1000) else en_lettres(q) + " " + nom + ("s" if taille > 1000 and q > 1 else "")
            return tete + (" " + en_lettres(r) if r else "")


def ordinal(n):
    if n == 1:
        return "premier"
    base = en_lettres(n)
    if base.endswith(("vingts", "cents")):
        base = base[:-1]
    if base.endswith("cinq"):
        return base + "uième"
    if base.endswith("neuf"):
        return base[:-1] + "vième"
    return (base[:-1] if base.endswith("e") else base) + "ième"


def chiffres_en_lettres(t):
    """« 8 000 ans », « 42 % », « 21 km », « 1er », « 6e siècle » : redits en lettres."""
    t = re.sub(r"(\d)[\s  ](?=\d{3}\b)", r"\1", t)
    t = re.sub(r"\b1er\b", "premier", t)
    t = re.sub(r"\b(\d+)e\b", lambda m: ordinal(int(m.group(1))), t)
    t = re.sub(r"\s*%", " pour cent", t)
    t = re.sub(r"\b(\d+)\s*km\b", r"\1 kilomètres", t)
    return re.sub(r"\d+", lambda m: en_lettres(int(m.group())), t)


def jetons(texte):
    """Les mots d'un texte, en minuscules sans accents : ce qu'on compare entre script et voix."""
    t = chiffres_en_lettres(texte).lower().replace("œ", "oe").replace("æ", "ae").replace("ı", "i")
    t = "".join(c for c in unicodedata.normalize("NFKD", t) if not unicodedata.combining(c))
    return re.findall(r"[a-z]+", t)


# ── 03_scenes.md ──────────────────────────────────────────────────────────────
@dataclass
class Scene:
    n: int
    type: str
    texte: str
    image: str
    mouvement: str
    texte_anime: str
    ligne: int
    fichier_image: Path = None
    fichier_clip: Path = None
    debut: float = 0.0        # en temps de la vidéo
    fin: float = 0.0
    voix_debut: float = None  # en temps de la voix (mots.json)
    voix_fin: float = None
    couverture: float = 1.0   # part des mots de la scène retrouvés dans la voix
    apparition: float = None  # moment où le texte animé apparaît (temps de la vidéo)

    @property
    def duree(self):
        return self.fin - self.debut


COLONNES = {"n°": "n", "n": "n", "no": "n", "type": "type", "texte dit": "texte", "image": "image",
            "mouvement": "mouvement", "texte animé": "texte_anime", "texte anime": "texte_anime"}


def lire_scenes(chemin):
    """Le premier tableau de 03_scenes.md qui commence par « n° | type ». Erreur claire sinon."""
    lignes = Path(chemin).read_text(encoding="utf-8").splitlines()
    scenes, index = [], None
    for num, ligne in enumerate(lignes, 1):
        brut = ligne.strip()
        if not brut.startswith("|"):
            if scenes:
                break
            continue
        cellules = [c.strip() for c in brut.strip("|").split("|")]
        if index is None:
            noms = [c.lower() for c in cellules]
            if noms and COLONNES.get(noms[0]) == "n" and "type" in noms:
                index = {COLONNES[c]: i for i, c in enumerate(noms) if c in COLONNES}
                manque = {"n", "type", "texte", "image", "mouvement", "texte_anime"} - set(index)
                if manque:
                    raise ErreurMontage(f"03_scenes.md, ligne {num} : colonnes manquantes dans l'en-tête : {sorted(manque)}")
            continue
        if set(brut.replace("|", "")) <= set("-: "):
            continue
        if len(cellules) <= max(index.values()):
            raise ErreurMontage(f"03_scenes.md, ligne {num} : {len(cellules)} colonnes, il en faut {max(index.values()) + 1}")
        valeur = {cle: cellules[i] for cle, i in index.items()}
        if not valeur["n"].isdigit():
            raise ErreurMontage(f"03_scenes.md, ligne {num} : numéro de scène illisible « {valeur['n']} »")
        scenes.append(Scene(n=int(valeur["n"]), type=valeur["type"].lower(), texte=valeur["texte"],
                            image=valeur["image"], mouvement=valeur["mouvement"].lower(),
                            texte_anime=valeur["texte_anime"], ligne=num))
    if not scenes:
        raise ErreurMontage("03_scenes.md : aucun tableau de scènes (en-tête attendu : | n° | type | texte dit | image | mouvement | texte animé |)")
    return scenes


def trouver(dossier, noms, extensions):
    for nom in noms:
        for ext in extensions:
            p = dossier / (nom + ext)
            if p.is_file():
                return p
    return None


def valider(scenes, dossier, verifier_fichiers=True, seulement=None):
    """Rattache les images et les clips. Renvoie (erreurs, avertissements) : des phrases pour Franco.
    `seulement` : les numéros des scènes dont on vérifie les fichiers (un extrait), sinon toutes."""
    erreurs, avert = [], []
    vus = set()
    for s in scenes:
        ou = f"scène {s.n} (ligne {s.ligne})"
        if s.n in vus:
            erreurs.append(f"{ou} : numéro en double")
        vus.add(s.n)
        if s.type not in TYPES:
            erreurs.append(f"{ou} : type « {s.type} » inconnu (image, video ou titre)")
            continue
        if s.type == "titre":
            if s.texte_anime in VIDE:
                erreurs.append(f"{ou} : une scène titre doit porter sa question dans « texte animé »")
            continue
        if s.texte in VIDE:
            erreurs.append(f"{ou} : pas de « texte dit » : impossible de la caler sur la voix")
        if s.type == "image" and s.mouvement not in MOUVEMENTS:
            avert.append(f"{ou} : mouvement « {s.mouvement} » inconnu, remplacé par zoom_avant")
            s.mouvement = "zoom_avant"
        if not verifier_fichiers or (seulement is not None and s.n not in seulement):
            continue
        propre = f"scene_{s.n:03d}"
        noms = [Path(s.image).stem] if s.image not in VIDE and not s.image.startswith("clips/") else []
        s.fichier_image = trouver(dossier / "images", noms + [propre], EXT_IMAGES)
        if s.fichier_image is None:
            erreurs.append(f"{ou} : image introuvable (images/{propre}.png ou .jpg)")
        if s.type == "video":
            s.fichier_clip = trouver(dossier / "clips", [Path(s.image).stem, f"anim_{s.n:03d}", propre], EXT_CLIPS)
            if s.fichier_clip is None:
                avert.append(f"{ou} : plan animé absent (clips/anim_{s.n:03d}.mp4) : l'image fixe le remplace")
            if s.mouvement not in MOUVEMENTS:
                s.mouvement = "zoom_avant"  # si le clip manque, l'image bouge comme les autres
    if scenes and scenes[0].type == "titre":
        erreurs.append("la première scène ne peut pas être un titre (la vidéo commence sur le hook)")
    return erreurs, avert


# ── Caler les scènes sur la voix ──────────────────────────────────────────────
def trouver_suite(cherche, dans):
    """Position de la première occurrence de la suite `cherche` dans `dans`, ou None."""
    for i in range(len(dans) - len(cherche) + 1):
        if dans[i:i + len(cherche)] == cherche:
            return i
    return None


def caler(scenes, voix):
    """Temps de début et de fin de chaque scène dite, en temps de la voix (mots.json).

    On aligne mot à mot le texte des scènes sur la transcription de Whisper (difflib) : les
    scènes découpent le script autrement que les phrases de la voix, parfois au milieu d'une
    phrase. Chaque coupe tombe au milieu du silence entre deux scènes ; quand une pause entre
    deux phrases de la voix est tout près, la coupe s'y aligne (ces bornes-là sont exactes)."""
    dites = [s for s in scenes if s.type != "titre"]
    a, a_scene = [], []
    for k, s in enumerate(dites):
        for j in jetons(s.texte):
            a.append(j)
            a_scene.append(k)
    mots = voix["mots"]
    b, b_mot = [], []
    for i, m in enumerate(mots):
        for j in jetons(m["mot"]):
            b.append(j)
            b_mot.append(i)
    vers = {}
    for bloc in difflib.SequenceMatcher(None, a, b, autojunk=False).get_matching_blocks():
        for d in range(bloc.size):
            vers[bloc.a + d] = bloc.b + d
    avert = []
    for k, s in enumerate(dites):
        idx = [i for i, sc in enumerate(a_scene) if sc == k]
        trouves = [vers[i] for i in idx if i in vers]
        s.couverture = len(trouves) / len(idx) if idx else 0.0
        s._jetons_voix = (trouves[0], trouves[-1]) if trouves else None
        if trouves:
            s.voix_debut = mots[b_mot[trouves[0]]]["debut_s"]
            s.voix_fin = mots[b_mot[trouves[-1]]]["fin_s"]
        if s.couverture < 0.6:
            avert.append(f"scène {s.n} : seulement {s.couverture:.0%} de son texte retrouvé dans la voix : "
                         "vérifie qu'elle correspond bien au script lu")
    # Une scène introuvable prend place entre ses voisines, à parts égales.
    for k, s in enumerate(dites):
        if s.voix_debut is None:
            avant = next((d.voix_fin for d in reversed(dites[:k]) if d.voix_fin is not None), 0.0)
            apres = next((d.voix_debut for d in dites[k + 1:] if d.voix_debut is not None), voix["duree_s"])
            s.voix_debut, s.voix_fin = avant, apres
            avert.append(f"scène {s.n} : texte introuvable dans la voix, placée entre ses voisines")
    for k in range(1, len(dites)):
        if dites[k].voix_debut < dites[k - 1].voix_debut:
            raise ErreurMontage(f"scènes {dites[k - 1].n} et {dites[k].n} : l'ordre du texte ne suit pas "
                                "celui de la voix. La voix correspond-elle à ce 03_scenes.md ?")
    # Les coupes, en temps de la voix.
    phrases = voix.get("phrases", [])
    pauses = [((p["fin_s"] + q["debut_s"]) / 2) for p, q in zip(phrases, phrases[1:])]
    coupes = [0.0]
    for g, d in zip(dites, dites[1:]):
        fin, debut = g.voix_fin, d.voix_debut
        milieu = (fin + debut) / 2 if debut >= fin else debut
        proches = [p for p in pauses if fin - 0.25 <= p <= debut + 0.25]
        coupes.append(min(proches, key=lambda p: abs(p - milieu)) if proches else milieu)
    coupes.append(voix["duree_s"])
    for k, s in enumerate(dites):
        s._coupe_debut, s._coupe_fin = coupes[k], coupes[k + 1]
    return avert


def chronologie(scenes, voix):
    """Place toutes les scènes en temps de la vidéo. Renvoie les insertions de silence (temps de la
    voix, durée) pour les titres, et la durée totale."""
    decalage, insertions, precedente = 0.0, [], None
    for i, s in enumerate(scenes):
        if s.type == "titre":
            suivante = next((d for d in scenes[i + 1:] if d.type != "titre"), None)
            point = suivante._coupe_debut if suivante else voix["duree_s"]
            s.debut = point + decalage
            s.fin = s.debut + TITRE_S
            insertions.append((point, TITRE_S))
            decalage += TITRE_S
            continue
        s.debut = s._coupe_debut + decalage
        s.fin = s._coupe_fin + decalage
        precedente = s
    if precedente is not None:
        precedente.fin += FIN_S
    total = voix["duree_s"] + decalage + FIN_S
    return insertions, total


def placer_textes(scenes, voix):
    """Le texte animé apparaît quand la voix prononce le mot qu'il reprend (sinon, en début de scène)."""
    mots = voix["mots"]
    b, b_mot = [], []
    for i, m in enumerate(mots):
        for j in jetons(m["mot"]):
            b.append(j)
            b_mot.append(i)
    petits = {"la", "le", "les", "l", "d", "de", "du", "des", "un", "une", "et", "a", "au", "en"}
    for s in scenes:
        if s.type == "titre" or s.texte_anime in VIDE:
            continue
        cherche = jetons(s.texte_anime)
        while cherche and cherche[0] in petits:
            cherche = cherche[1:]
        moment = None
        zone = getattr(s, "_jetons_voix", None)
        if cherche and zone:
            dans = b[zone[0]:zone[1] + 1]
            for longueur in range(len(cherche), 0, -1):
                pos = trouver_suite(cherche[:longueur], dans)
                if pos is not None:
                    moment = mots[b_mot[zone[0] + pos]]["debut_s"] - s._coupe_debut + s.debut
                    break
        if moment is None:
            moment = s.debut + 0.5
        s.apparition = min(max(moment, s.debut + 0.2), max(s.debut + 0.2, s.fin - TEXTE_MIN_S))


def planifier(dossier, verifier_fichiers=True, extrait=None):
    """Lit, valide et cale. Renvoie (scenes, voix, insertions, total, avertissements).
    `extrait` : (première, dernière) scène ; seuls leurs fichiers sont exigés."""
    dossier = Path(dossier)
    scenes = lire_scenes(dossier / "03_scenes.md")
    seulement = None
    if extrait:
        seulement = {s.n for s in scenes if extrait[0] <= s.n <= extrait[1]}
        # un titre prend en fond l'image de la scène qui le suit
        for i, s in enumerate(scenes):
            if s.n in seulement and s.type == "titre":
                suivante = next((d.n for d in scenes[i + 1:] if d.type != "titre"), None)
                if suivante is not None:
                    seulement.add(suivante)
    erreurs, avert = valider(scenes, dossier, verifier_fichiers, seulement)
    chemin_mots = dossier / "voix" / "mots.json"
    if not chemin_mots.is_file():
        erreurs.append("voix/mots.json introuvable : lance d'abord le notebook voix_zehon.ipynb")
    if erreurs:
        raise ErreurMontage("Montage impossible :\n  - " + "\n  - ".join(erreurs))
    voix = json.loads(chemin_mots.read_text(encoding="utf-8"))
    avert += caler(scenes, voix)
    insertions, total = chronologie(scenes, voix)
    placer_textes(scenes, voix)
    for s in scenes:
        if s.type == "image" and s.duree > IMAGE_MAX_S:
            avert.append(f"scène {s.n} : image fixe pendant {s.duree:.1f} s (plus de {IMAGE_MAX_S:.0f} s) : "
                         "à couper en deux scènes ?")
    return scenes, voix, insertions, total, avert


# ── L'image, scène par scène ──────────────────────────────────────────────────
def lire_image(chemin, largeur, hauteur):
    """L'image recadrée (sans déformation) pour couvrir largeur × hauteur."""
    im = cv2.imread(str(chemin), cv2.IMREAD_COLOR)
    if im is None:
        raise ErreurMontage(f"image illisible : {chemin}")
    im = im[:, :, ::-1]
    h, w = im.shape[:2]
    e = max(largeur / w, hauteur / h)
    nw, nh = max(largeur, round(w * e)), max(hauteur, round(h * e))
    im = cv2.resize(im, (nw, nh), interpolation=cv2.INTER_LANCZOS4 if e > 1 else cv2.INTER_AREA)
    x, y = (nw - largeur) // 2, (nh - hauteur) // 2
    return np.ascontiguousarray(im[y:y + hauteur, x:x + largeur])


def cadrer(source, zoom, cx, cy, largeur, hauteur):
    """La vue de la source agrandie `zoom` fois autour de (cx, cy) (fractions de la source), au sous-pixel près."""
    sh, sw = source.shape[:2]
    vw, vh = sw / zoom, sh / zoom
    x0 = min(max(cx * sw - vw / 2, 0), sw - vw)
    y0 = min(max(cy * sh - vh / 2, 0), sh - vh)
    e = largeur / vw
    matrice = np.float32([[e, 0, -x0 * e], [0, e, -y0 * e]])
    return cv2.warpAffine(source, matrice, (largeur, hauteur), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)


def mouvement(nom, u):
    """(zoom, cx, cy) au temps u ∈ [0, 1] de la scène. Zoom 1 = l'image préparée entière."""
    course = 0.8 * (1 - 1 / (1 + PAN)) / 2
    if nom == "zoom_avant":
        return 1 + ZOOM * u, 0.5, 0.5
    if nom == "zoom_arriere":
        return 1 + ZOOM * (1 - u), 0.5, 0.5
    if nom == "pan_droite":
        return 1 + PAN, 0.5 - course + 2 * course * u, 0.5
    if nom == "pan_gauche":
        return 1 + PAN, 0.5 + course - 2 * course * u, 0.5
    return 1 + ZOOM / 2, 0.5, 0.5


def calque_texte(texte, police, taille, largeur_max, centre=False):
    """Le texte en blanc cassé avec une ombre douce, sur fond transparent : tableau RGBA."""
    fonte = ImageFont.truetype(str(police), taille)
    lignes, ligne = [], ""
    for mot in texte.split():
        essai = (ligne + " " + mot).strip()
        if fonte.getlength(essai) <= largeur_max or not ligne:
            ligne = essai
        else:
            lignes.append(ligne)
            ligne = mot
    lignes.append(ligne)
    interligne = round(taille * 1.22)
    marge = round(taille * 0.5)
    larg = int(max(fonte.getlength(l) for l in lignes)) + 2 * marge
    haut = interligne * len(lignes) + 2 * marge
    ombre = Image.new("RGBA", (larg, haut), (0, 0, 0, 0))
    texte_seul = Image.new("RGBA", (larg, haut), (0, 0, 0, 0))
    for i, l in enumerate(lignes):
        x = (larg - fonte.getlength(l)) / 2 if centre else marge
        y = marge + i * interligne
        ImageDraw.Draw(ombre).text((x, y + taille * 0.06), l, font=fonte, fill=(0, 0, 0, 190))
        ImageDraw.Draw(texte_seul).text((x, y), l, font=fonte, fill=BLANC_CASSE + (255,))
    ombre = ombre.filter(ImageFilter.GaussianBlur(taille * 0.12))
    return np.asarray(Image.alpha_composite(ombre, texte_seul))


def poser(image, calque, x, y, opacite):
    """Pose un calque RGBA sur l'image (en place), avec une opacité globale."""
    if opacite <= 0:
        return image
    h, w = calque.shape[:2]
    H, W = image.shape[:2]
    x, y = int(round(x)), int(round(y))
    x0, y0, x1, y1 = max(x, 0), max(y, 0), min(x + w, W), min(y + h, H)
    if x1 <= x0 or y1 <= y0:
        return image
    c = calque[y0 - y:y1 - y, x0 - x:x1 - x].astype(np.float32)
    a = c[:, :, 3:4] / 255.0 * opacite
    zone = image[y0:y1, x0:x1].astype(np.float32)
    image[y0:y1, x0:x1] = (zone * (1 - a) + c[:, :, :3] * a).astype(np.uint8)
    return image


def lisser(u):
    u = min(max(u, 0.0), 1.0)
    return u * u * (3 - 2 * u)


class LecteurClip:
    """Les images d'un plan animé, lues dans l'ordre par ffmpeg, à la taille de la vidéo."""

    def __init__(self, chemin, duree_voulue, largeur, hauteur):
        self.taille = largeur * hauteur * 3
        self.forme = (hauteur, largeur, 3)
        duree = sonder_duree(chemin)
        self.ralenti = min(max(duree_voulue / duree, 1.0), RALENTI_MAX) if duree else 1.0
        self.fige_s = max(0.0, duree_voulue - duree * self.ralenti) if duree else 0.0
        filtre = (f"setpts={self.ralenti:.4f}*PTS,fps={IPS},"
                  f"scale={largeur}:{hauteur}:force_original_aspect_ratio=increase:flags=lanczos,"
                  f"crop={largeur}:{hauteur},format=rgb24")
        self.proc = subprocess.Popen(["ffmpeg", "-v", "error", "-i", str(chemin), "-an", "-vf", filtre,
                                      "-f", "rawvideo", "-pix_fmt", "rgb24", "-"],
                                     stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
        self.derniere, self.index = None, -1

    def image(self, k):
        while self.index < k:
            brut = self.proc.stdout.read(self.taille)
            if len(brut) < self.taille:
                break
            self.derniere = np.frombuffer(brut, np.uint8).reshape(self.forme)
            self.index += 1
        return self.derniere

    def fermer(self):
        self.proc.stdout.close()
        self.proc.kill()
        self.proc.wait()


class Rendu:
    """Une scène à l'écran : sait fabriquer son image à n'importe quel instant de sa présence."""

    def __init__(self, scene, suivante, largeur, hauteur):
        self.s, self.suivante = scene, suivante
        self.l, self.h = largeur, hauteur
        self.debut_vue = scene.debut - FONDU_S / 2
        self.duree_vue = scene.duree + FONDU_S
        self.pret = False
        self.clip = None
        self.avertissement = None

    def preparer(self):
        s, l, h = self.s, self.l, self.h
        grand = (round(l * MARGE_SOURCE), round(h * MARGE_SOURCE))
        echelle = l / LARGEUR
        if s.type == "titre":
            fond = lire_image(self.suivante.fichier_image, *grand) if self.suivante else np.zeros((grand[1], grand[0], 3), np.uint8)
            fond = cv2.GaussianBlur(fond, (0, 0), 18 * echelle)
            self.source = (fond.astype(np.float32) * 0.42).astype(np.uint8)
            self.calque = calque_texte(s.texte_anime, POLICE_TITRE, round(84 * echelle), round(1500 * echelle), centre=True)
        else:
            self.source = lire_image(s.fichier_image, *grand)
            self.calque = (calque_texte(s.texte_anime, POLICE_TEXTE, round(64 * echelle), round(1400 * echelle))
                           if s.texte_anime not in VIDE else None)
            if s.type == "video" and s.fichier_clip is not None:
                self.clip = LecteurClip(s.fichier_clip, self.duree_vue, l, h)
                if self.clip.fige_s > 1.0:
                    self.avertissement = (f"scène {s.n} : plan animé trop court, ralenti ×{self.clip.ralenti:.2f} "
                                          f"puis figé {self.clip.fige_s:.1f} s")
        self.pret = True

    def image(self, t):
        if not self.pret:
            self.preparer()
        s = self.s
        u = (t - self.debut_vue) / self.duree_vue
        if self.clip is not None:
            vue = self.clip.image(int((t - self.debut_vue) * IPS))
            image = vue.copy() if vue is not None else cadrer(self.source, *mouvement(s.mouvement, u), self.l, self.h)
        elif s.type == "titre":
            image = cadrer(self.source, 1 + 0.03 * u, 0.5, 0.5, self.l, self.h)
        else:
            image = cadrer(self.source, *mouvement(s.mouvement, u), self.l, self.h)
        if self.calque is not None:
            if s.type == "titre":
                apparition = s.debut + 0.15
                x = (self.l - self.calque.shape[1]) / 2
                y = (self.h - self.calque.shape[0]) / 2
                glisse = 0
            else:
                apparition = s.apparition
                x = round(110 * self.l / LARGEUR)
                y = self.h - round(120 * self.h / HAUTEUR) - self.calque.shape[0]
                glisse = 14 * self.h / HAUTEUR
            entree = lisser((t - apparition) / 0.5)
            sortie = lisser((s.fin - 0.2 - t) / 0.4)
            poser(image, self.calque, x, y + glisse * (1 - entree), min(entree, sortie))
        return image

    def liberer(self):
        if self.clip is not None:
            self.clip.fermer()
            self.clip = None
        self.source = self.calque = None


# ── Le son ────────────────────────────────────────────────────────────────────
TAUX_AUDIO = 48000


def lire_audio(chemin):
    brut = subprocess.run(["ffmpeg", "-v", "error", "-i", str(chemin), "-f", "f32le", "-ac", "1",
                           "-ar", str(TAUX_AUDIO), "-"], capture_output=True, check=True).stdout
    return np.frombuffer(brut, np.float32)


def piste_son(chemin_voix, insertions, total, musique=None, volume_musique_db=-26.0):
    """La voix, avec les silences des titres ; la musique (facultative) en nappe, plus basse sous la voix."""
    voix = lire_audio(chemin_voix)
    morceaux, dernier = [], 0
    for point, duree in sorted(insertions):
        i = min(int(round(point * TAUX_AUDIO)), len(voix))
        morceaux += [voix[dernier:i], np.zeros(int(round(duree * TAUX_AUDIO)), np.float32)]
        dernier = i
    morceaux.append(voix[dernier:])
    son = np.concatenate(morceaux)
    son = np.concatenate([son, np.zeros(max(0, int(round(total * TAUX_AUDIO)) - len(son)), np.float32)])
    if musique is not None:
        nappe = lire_audio(musique)
        if len(nappe):
            nappe = np.tile(nappe, len(son) // len(nappe) + 1)[:len(son)]
            # La musique baisse encore de 6 dB quand la voix parle (enveloppe lissée sur 0,3 s).
            enveloppe = np.convolve(np.abs(son), np.ones(int(0.3 * TAUX_AUDIO)) / (0.3 * TAUX_AUDIO), mode="same")
            parle = np.clip(enveloppe / 0.02, 0, 1)
            gain = 10 ** (volume_musique_db / 20) * (1 - 0.5 * parle)
            son = son + nappe * gain.astype(np.float32)
    return normaliser(son.astype(np.float32))


def normaliser(son):
    """Volume ramené à VOLUME_LUFS, crêtes limitées à CRETE_DBTP (filtre loudnorm de ffmpeg).

    Nécessaire : la voix du notebook est baissée en bloc quand une crête dépasse, et sortait
    à −22 LUFS sur le sel (mesuré le 30/09), bien trop bas pour YouTube."""
    r = subprocess.run(["ffmpeg", "-v", "error", "-f", "f32le", "-ar", str(TAUX_AUDIO), "-ac", "1", "-i", "-",
                        "-af", f"loudnorm=I={VOLUME_LUFS}:TP={CRETE_DBTP}:LRA=11", "-f", "f32le",
                        "-ar", str(TAUX_AUDIO), "-ac", "1", "-"], input=son.tobytes(), capture_output=True, check=True)
    sortie = np.frombuffer(r.stdout, np.float32)
    return np.concatenate([sortie, np.zeros(max(0, len(son) - len(sortie)), np.float32)])[:len(son)]


# ── Rendu et contrôle ─────────────────────────────────────────────────────────
def sonder_duree(chemin):
    r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(chemin)],
                       capture_output=True, text=True)
    try:
        return float(r.stdout.strip())
    except ValueError:
        return 0.0


def rendre(scenes, son, t0, t1, sortie, largeur=LARGEUR, hauteur=HAUTEUR, preset="medium", crf=18, bavard=True):
    """Fabrique la vidéo entre t0 et t1 (temps de la vidéo). Renvoie les avertissements du rendu."""
    visibles = [s for s in scenes if s.fin > t0 and s.debut < t1]
    rendus = []
    for i, s in enumerate(visibles):
        suivante = next((d for d in scenes[scenes.index(s) + 1:] if d.type != "titre"), None)
        rendus.append(Rendu(s, suivante, largeur, hauteur))
    debuts = [r.s.debut for r in rendus]
    sortie = Path(sortie)
    sortie.parent.mkdir(parents=True, exist_ok=True)
    extrait = son[int(round(t0 * TAUX_AUDIO)):int(round(t1 * TAUX_AUDIO))]
    avert = []
    with tempfile.NamedTemporaryFile(suffix=".f32") as fichier_son:
        fichier_son.write(extrait.tobytes())
        fichier_son.flush()
        commande = ["ffmpeg", "-y", "-v", "error",
                    "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{largeur}x{hauteur}", "-r", str(IPS), "-i", "-",
                    "-f", "f32le", "-ar", str(TAUX_AUDIO), "-ac", "1", "-i", fichier_son.name,
                    "-map", "0:v", "-map", "1:a", "-c:v", "libx264", "-preset", preset, "-crf", str(crf),
                    "-pix_fmt", "yuv420p", "-g", str(2 * IPS), "-c:a", "aac", "-b:a", "192k", "-ac", "2",
                    "-movflags", "+faststart", "-shortest", str(sortie)]
        encodeur = subprocess.Popen(commande, stdin=subprocess.PIPE)
        n_images = int(round((t1 - t0) * IPS))
        try:
            for f in range(n_images):
                t = t0 + f / IPS
                k = max(0, bisect.bisect_right(debuts, t) - 1)
                r = rendus[k]
                image = r.image(t)
                if k + 1 < len(rendus) and t > r.s.fin - FONDU_S / 2:
                    a = lisser((t - (r.s.fin - FONDU_S / 2)) / FONDU_S)
                    image = cv2.addWeighted(image, 1 - a, rendus[k + 1].image(t), a, 0)
                elif k > 0 and t < r.s.debut + FONDU_S / 2:
                    a = lisser(0.5 + (t - r.s.debut) / FONDU_S)
                    image = cv2.addWeighted(rendus[k - 1].image(t), 1 - a, image, a, 0)
                noir = min(lisser(t / DEBUT_NOIR_S) if t0 == 0 else 1.0, lisser((scenes[-1].fin - t) / 1.0))
                if noir < 1:
                    image = (image.astype(np.float32) * noir).astype(np.uint8)
                encodeur.stdin.write(np.ascontiguousarray(image).tobytes())
                for j in range(k - 1):  # les scènes passées libèrent leur mémoire et leur lecteur
                    if rendus[j].pret and rendus[j].source is not None:
                        rendus[j].liberer()
                if bavard and f % (IPS * 10) == 0:
                    print(f"   {f / IPS:6.1f} s / {n_images / IPS:.1f} s", flush=True)
        finally:
            encodeur.stdin.close()
            code = encodeur.wait()
            for r in rendus:
                if r.avertissement:
                    avert.append(r.avertissement)
                if r.pret and r.clip is not None:
                    r.liberer()
        if code != 0:
            raise ErreurMontage(f"ffmpeg a échoué (code {code}) pendant l'encodage de {sortie}")
    return avert


def controler(chemin, duree_attendue, largeur=LARGEUR, hauteur=HAUTEUR):
    """Le contrôle avant publication : [(vérification, réussie, détail)].

    Idée et seuils repris de scripts/preflight.py du plugin « AI YouTube OS » (channelroom-studio,
    licence MIT) : piste audio présente, pas de silence, pas de saturation, bonne taille, bonne durée."""
    sonde = json.loads(subprocess.run(["ffprobe", "-v", "error", "-show_entries",
                                       "stream=codec_type,width,height:format=duration", "-of", "json", str(chemin)],
                                      capture_output=True, text=True).stdout or "{}")
    flux = sonde.get("streams", [])
    video = next((f for f in flux if f.get("codec_type") == "video"), {})
    audio = [f for f in flux if f.get("codec_type") == "audio"]
    duree = float(sonde.get("format", {}).get("duration", 0))
    niveaux = subprocess.run(["ffmpeg", "-v", "info", "-i", str(chemin), "-vn", "-af", "volumedetect", "-f", "null", "-"],
                             capture_output=True, text=True).stderr
    moyen = re.search(r"mean_volume: (-?[\d.]+) dB", niveaux)
    crete = re.search(r"max_volume: (-?[\d.]+) dB", niveaux)
    moyen = float(moyen.group(1)) if moyen else -99.0
    crete = float(crete.group(1)) if crete else 0.0
    return [
        ("image", video.get("width") == largeur and video.get("height") == hauteur,
         f"{video.get('width')}×{video.get('height')}"),
        ("piste audio", bool(audio), f"{len(audio)} piste(s)"),
        ("pas de silence", moyen > -60, f"volume moyen {moyen:.1f} dB (seuil −60 dB)"),
        ("pas de saturation", crete <= -0.5, f"crête {crete:.1f} dB (seuil −0,5 dB)"),
        ("durée", abs(duree - duree_attendue) <= 0.5, f"{duree:.1f} s pour {duree_attendue:.1f} s attendues"),
    ]


def minutes(t):
    return f"{int(t // 60)}:{t % 60:04.1f}"


def main(argv=None):
    p = argparse.ArgumentParser(description="Monte la vidéo d'un dossier Zehon.")
    p.add_argument("dossier", help="le dossier de la vidéo (Videos/01_sel)")
    p.add_argument("--scenes", help="un extrait, par exemple 1-10")
    p.add_argument("--sortie", help="chemin de la vidéo (défaut : rendu/video.mp4, ou rendu/extrait_A-B.mp4)")
    p.add_argument("--plan", action="store_true", help="valider et caler seulement, sans rendu")
    p.add_argument("--sans-fichiers", action="store_true",
                   help="avec --plan : ne pas chercher images et clips (ils sont dans Drive, pas ici)")
    p.add_argument("--musique", help="une nappe musicale (mp3, wav…), mise en boucle à bas volume")
    p.add_argument("--taille", default=f"{LARGEUR}x{HAUTEUR}", help="par exemple 960x540 pour un aperçu rapide")
    p.add_argument("--preset", default="medium", help="preset x264 (ultrafast pour un essai, medium pour la vraie)")
    args = p.parse_args(argv)
    dossier = Path(args.dossier)
    largeur, hauteur = (int(x) for x in args.taille.lower().split("x"))
    extrait = None
    if args.scenes:
        a, _, b = args.scenes.partition("-")
        extrait = (int(a), int(b or a))
    try:
        scenes, voix, insertions, total, avert = planifier(dossier, not (args.plan and args.sans_fichiers), extrait)
    except ErreurMontage as e:
        print(f"❌ {e}")
        return 1
    print(f"🎬 {dossier.resolve().name} : {len(scenes)} scènes, {minutes(total)} ({len(insertions)} titre(s) ajoutent {sum(d for _, d in insertions):.0f} s)")
    for s in scenes:
        texte = s.texte_anime if s.type == "titre" else s.texte
        print(f"   {s.n:3d} {s.type:6s} {minutes(s.debut):>7s}  {s.duree:5.1f} s  {s.couverture:4.0%}  {texte[:60]}")
    for a in avert:
        print(f"⚠️  {a}")
    if args.plan:
        return 0
    t0, t1, suffixe = 0.0, total, "video"
    if extrait:
        choisies = [s for s in scenes if extrait[0] <= s.n <= extrait[1]]
        if not choisies:
            print(f"❌ aucune scène dans {args.scenes}")
            return 1
        t0, t1 = choisies[0].debut, choisies[-1].fin
        suffixe = f"extrait_{extrait[0]:03d}-{extrait[1]:03d}"
    sortie = Path(args.sortie) if args.sortie else dossier / "rendu" / f"{suffixe}.mp4"
    chemin_voix = dossier / "voix" / "voix.wav"
    if not chemin_voix.is_file():
        print("❌ voix/voix.wav introuvable")
        return 1
    son = piste_son(chemin_voix, insertions, total, args.musique)
    print(f"🎞️  Rendu de {minutes(t0)} à {minutes(t1)} → {sortie}")
    for a in rendre(scenes, son, t0, t1, sortie, largeur, hauteur, args.preset):
        print(f"⚠️  {a}")
        avert.append(a)
    controle = controler(sortie, t1 - t0, largeur, hauteur)
    rapport = {
        "video": dossier.resolve().name, "sortie": str(sortie), "de_s": round(t0, 2), "a_s": round(t1, 2),
        "duree_totale_s": round(total, 2),
        "scenes": [{"n": s.n, "type": s.type, "debut_s": round(s.debut, 2), "duree_s": round(s.duree, 2),
                    "couverture": round(s.couverture, 2),
                    "texte_anime_s": round(s.apparition, 2) if s.apparition is not None else None} for s in scenes],
        "avertissements": avert,
        "controle": [{"verification": v, "reussie": ok, "detail": d} for v, ok, d in controle],
        "pret": all(ok for _, ok, _ in controle),
    }
    (sortie.parent / ("rapport.json" if suffixe == "video" else f"rapport_{suffixe}.json")).write_text(
        json.dumps(rapport, ensure_ascii=False, indent=2), encoding="utf-8")
    print("🔎 Contrôle avant publication :")
    for v, ok, d in controle:
        print(f"   {'✓' if ok else '✗'} {v} : {d}")
    print("✅ Rendu prêt." if rapport["pret"] else "❌ Le contrôle a échoué : ne pas publier en l'état.")
    return 0 if rapport["pret"] else 1


if __name__ == "__main__":
    sys.exit(main())
