#!/usr/bin/env python3
"""
capturer_web.py — photographie une page web en PNG, pour servir de plan (E5b).

Usage :
  python3 capturer_web.py --url https://github.com/upstash/context7 \
      --sortie videos/<id>/assets/ressources/capture_repo.png \
      [--largeur 1400] [--hauteur 900] [--attente-ms 2500] [--navigateur CHEMIN]

Pourquoi ce script existe : la chaine parle d'outils qui ont tous une page
web. Jusqu'ici, « Context7 te donne la vraie doc » etait rendu par trois
boites dessinees dont l'une disait CONTEXT7 — une image qui ressemble
exactement a celle du serveur MCP suivant. La vraie page, elle, ne ressemble
a aucune autre. C'est de la variete gratuite et exacte.

**Aucune dependance nouvelle.** On pilote le Chromium **que Remotion
telecharge deja** pour rendre les videos, en mode headless screenshot. Ajouter
Playwright aurait installe un second navigateur pour faire ce que le premier
sait faire.
"""
import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

# Ou chercher un Chromium, du plus explicite au plus devinatoire.
CANDIDATS = [
    "/opt/pw-browsers/chromium/chrome-linux/chrome",
    "/opt/pw-browsers/chromium/chrome",
    "/usr/bin/chromium",
    "/usr/bin/chromium-browser",
    "/usr/bin/google-chrome",
    "C:/Program Files/Google/Chrome/Application/chrome.exe",
]


def trouver_navigateur(explicite=None):
    """Ordre : argument, variable d'environnement, PATH, chemins connus,
    cache de Remotion. Le cache de Remotion est teste en dernier parce que
    son arborescence varie avec la version."""
    if explicite:
        return explicite if Path(explicite).is_file() else None
    if os.environ.get("CHROMIUM_PATH"):
        p = os.environ["CHROMIUM_PATH"]
        if Path(p).is_file():
            return p
    for nom in ("chromium", "chromium-browser", "google-chrome", "chrome"):
        trouve = shutil.which(nom)
        if trouve:
            return trouve
    for c in CANDIDATS:
        if Path(c).is_file():
            return c
    for racine in (Path.home() / ".remotion", Path("/opt/pw-browsers")):
        if racine.is_dir():
            for motif in ("**/chrome", "**/chrome.exe", "**/headless_shell"):
                for trouve in racine.glob(motif):
                    if trouve.is_file():
                        return str(trouve)
    return None


# Signatures d'impasse. Un PNG non vide ne prouve RIEN : une interstitielle
# TLS, un 404, un mur de cookies ou une page anti-robot produisent tous une
# image parfaitement valide. C'est la meme classe de defaut que celle qui
# traverse tout le diagnostic — un critere verifiable au vert, et une image
# fausse a l'ecran.
MARQUEURS_ERREUR = (
    "your connection is not private",
    "this site can't be reached",
    "the webpage at",
    "page not found",
    "404 not found",
    "privacy error",
    "access denied",
    "are you a robot",
    "just a moment...",
    "enable javascript and cookies to continue",
)

# Les codes reseau de Chromium, tous prefixes ERR_. Les matcher en bloc
# evite d'en lister quarante et d'en oublier trente-neuf.
MOTIF_ERR = re.compile(r"\berr_[a-z_]{4,}\b")

# Chrome titre ses pages d'erreur reseau avec le NOM DE DOMAINE. Un titre
# plausible ne prouve donc rien : c'est ce qui a laisse passer une capture
# d'erreur portant fierement le titre « example.com ».
APOSTROPHES = {"\u2019": "'", "\u2018": "'", "\u00b4": "'", "`": "'"}


def normaliser(texte):
    for source, cible in APOSTROPHES.items():
        texte = texte.replace(source, cible)
    return texte.lower()


def juger(dom):
    """(titre, suspect, motif) a partir du DOM **du chargement photographie**.

    Les trois controles ci-dessous ont ete ajoutes sur trois echecs reels,
    dans cet ordre : une interstitielle TLS, un corps JSON d'erreur de proxy,
    et une page d'erreur reseau que le controle precedent avait validee. Le
    troisieme a ete vu **en regardant le PNG**, pas en le testant — ce qui
    reste la limite de tout controle automatique, et la raison pour laquelle
    le skill d'A8 impose de regarder les captures avant de les monter.
    """
    if not dom.strip():
        return None, True, "page vide"

    bas = normaliser(dom)
    titre = None
    debut = bas.find("<title")
    if debut != -1:
        ouvre = bas.find(">", debut)
        ferme = bas.find("</title>", ouvre)
        if ouvre != -1 and ferme != -1:
            titre = dom[ouvre + 1:ferme].strip()[:200]

    # Scanner le DOM ENTIER, sans borne. Une premiere version s'arretait aux
    # 40 000 premiers caracteres « par prudence » : la page d'erreur de
    # Chromium embarque une grosse ressource inline avant son texte visible,
    # et ses marqueurs tombaient vers l'offset 142 000. Le controle etait
    # donc ecrit, correct, et desactive en silence par une borne arbitraire.
    for marqueur in MARQUEURS_ERREUR:
        if marqueur in bas:
            return titre, True, f"la page contient \u00ab {marqueur} \u00bb"

    trouve = MOTIF_ERR.search(bas)
    if trouve:
        return titre, True, f"code d'erreur reseau {trouve.group(0).upper()}"

    if not titre:
        return titre, True, "page sans <title> (une vraie page web en a un)"

    corps = bas.find("<body")
    if corps != -1:
        texte = bas[bas.find(">", corps) + 1:].strip()
        texte = texte.replace("<pre>", "").lstrip()
        if texte.startswith("{") and ('"message"' in texte[:2000] or '"error"' in texte[:2000]):
            return titre, True, "le corps est une reponse JSON, pas une page"

    return titre, False, ""


def capturer(url, sortie, largeur, hauteur, attente_ms, navigateur, ignorer_tls=False, echelle=2):
    """Photographie la page ET relit son DOM **dans le meme lancement**.

    Deux lancements separes ne garantissent pas le meme chargement : sur un
    reseau instable, la relecture peut reussir pendant que la capture, elle,
    a ramene une page d'erreur. C'est arrive, et la capture fausse est
    passee pour bonne. Chromium accepte --screenshot et --dump-dom ensemble ;
    il n'y a donc aucune raison de les separer.
    """
    sortie = Path(sortie)
    sortie.parent.mkdir(parents=True, exist_ok=True)
    # Partir d'un fichier absent, pour que « le PNG existe » soit une preuve
    # et pas un reliquat du run precedent.
    if sortie.exists():
        sortie.unlink()

    # --user-data-dir jetable : sans lui, deux captures lancees a la suite se
    # disputent le profil par defaut et la seconde sort vide.
    with tempfile.TemporaryDirectory() as profil:
        cmd = [navigateur, "--headless=new", "--disable-gpu", "--no-sandbox",
               "--hide-scrollbars", f"--user-data-dir={profil}",
               f"--window-size={largeur},{hauteur}",
               f"--virtual-time-budget={attente_ms}",
               # Capture en 2x par defaut : ramenee a 1080 px de large dans
               # un Short, une capture 1x rend un texte baveux. Le PNG pese
               # plus lourd, ce qui n'a aucune importance ici.
               f"--force-device-scale-factor={echelle}",
               "--disable-features=Translate,AcceptCHFrame",
               f"--screenshot={sortie}", "--dump-dom", url]
        # Chromium n'honore PAS les variables HTTPS_PROXY/HTTP_PROXY : il
        # faut les lui passer en option. Sans ca, derriere un proxy
        # d'entreprise ou de bac a sable, chaque capture ramene sagement une
        # page « this site can't be reached » — avec un PNG valide.
        proxy = os.environ.get("HTTPS_PROXY") or os.environ.get("https_proxy") \
            or os.environ.get("HTTP_PROXY") or os.environ.get("http_proxy")
        if proxy:
            cmd.insert(1, f"--proxy-server={proxy}")
        if ignorer_tls:
            cmd.insert(1, "--ignore-certificate-errors")
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=180)

    if not sortie.is_file() or sortie.stat().st_size == 0:
        return None, True, "PNG absent ou vide", (r.stderr or "").strip()[-400:]
    titre, suspect, motif = juger(r.stdout or "")
    return titre, suspect, motif, ""


def main():
    ap = argparse.ArgumentParser(description="Capture une page web en PNG (E5b).")
    ap.add_argument("--url", required=True)
    ap.add_argument("--sortie", required=True)
    ap.add_argument("--largeur", type=int, default=1400,
                    help="Largeur de la fenetre. Capture au plus ETROIT possible : la page "
                         "sera ramenee a ~975 px de large dans le cadre, et un viewport "
                         "large rend le texte minuscule a l'ecran d'un telephone.")
    ap.add_argument("--hauteur", type=int, default=900)
    ap.add_argument("--attente-ms", type=int, default=3000,
                    help="Budget de temps virtuel : laisse la page charger polices et images.")
    ap.add_argument("--echelle", type=float, default=2,
                    help="Facteur d'echelle du rendu (defaut 2). Une capture ramenee a "
                         "1080 px de large dans un Short doit rester nette.")
    ap.add_argument("--navigateur")
    ap.add_argument("--ignorer-erreurs-tls", action="store_true",
                    help="N'utiliser que derriere un proxy de developpement qui reforge les "
                         "certificats (sandbox). Desactive la verification TLS : ne jamais "
                         "l'employer pour capturer une page dont le contenu compte vraiment.")
    ap.add_argument("--autoriser-suspect", action="store_true",
                    help="Ecrit la capture meme si la relecture la juge suspecte (page "
                         "d'erreur, mur anti-robot). Par defaut on echoue plutot que de "
                         "laisser une fausse image entrer dans la video.")
    a = ap.parse_args()

    navigateur = trouver_navigateur(a.navigateur)
    if not navigateur:
        print(json.dumps({"ok": False, "message":
            "Aucun Chromium trouve. Passe --navigateur, ou definis CHROMIUM_PATH. "
            "Remotion en telecharge un : `cd composants && npx remotion browser ensure`."},
            ensure_ascii=False))
        sys.exit(4)

    try:
        titre, suspect, motif, erreur = capturer(a.url, a.sortie, a.largeur, a.hauteur,
                                                 a.attente_ms, navigateur,
                                                 a.ignorer_erreurs_tls, a.echelle)
    except subprocess.TimeoutExpired:
        print(json.dumps({"ok": False, "message": f"Delai depasse sur {a.url}"}, ensure_ascii=False))
        sys.exit(6)

    resultat = {"ok": True, "sortie": a.sortie, "url": a.url,
                "largeur_px": a.largeur, "hauteur_px": a.hauteur,
                "navigateur": navigateur, "titre": titre,
                "suspect": suspect, "motif_suspicion": motif,
                "provenance": f"capture:{a.url}", "licence": "capture-ecran"}

    if suspect and not a.autoriser_suspect:
        Path(a.sortie).unlink(missing_ok=True)
        resultat["ok"] = False
        resultat["message"] = (
            f"Capture refusee : {motif}. Le PNG etait pourtant valide - c'est "
            f"precisement pour ca qu'on relit la page. Titre lu : {titre!r}. "
            f"Forcer avec --autoriser-suspect si c'est un faux positif."
        )
        print(json.dumps(resultat, ensure_ascii=False))
        sys.exit(6)

    print(json.dumps(resultat, ensure_ascii=False))


if __name__ == "__main__":
    main()
