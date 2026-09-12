#!/usr/bin/env python3
"""
recuperer_logo.py — telecharge le vrai logo d'une marque en SVG (E5b).

Usage :
  python3 recuperer_logo.py --marque anthropic \
      --sortie 00_Profil/banque_assets/logos/anthropic.svg [--couleur 191919]

Source : Simple Icons (cdn.simpleicons.org), ~3000 marques, SVG officiels,
licence CC0. Deterministe et gratuit : la meme marque rend toujours le meme
fichier, ce qui compte pour un pipeline dont tout le reste est reproductible.

Pourquoi : les marques dont parlent les scripts etaient rendues par leur NOM
EN MAJUSCULES dans une boite dessinee. Une boite « GITHUB » ressemble
exactement a une boite « CONTEXT7 » ; les deux logos, non. La variete etait
a un telechargement de distance.

Le fichier atterrit dans la **banque** (`00_Profil/banque_assets/logos/`),
pas dans le dossier d'une video : un logo sert vingt videos, et la banque est
le deuxieme actif du systeme qui s'accumule, apres le corpus.
"""
import argparse
import json
import re
import sys
import urllib.error
import urllib.request
from pathlib import Path

BASE = "https://cdn.simpleicons.org"


def slug(marque):
    """Slug Simple Icons : minuscules, sans espace ni ponctuation.
    « Claude AI » -> « claudeai », « Next.js » -> « nextdotjs » (cas connu,
    traite explicitement parce que la regle generale le raterait)."""
    exceptions = {
        "next.js": "nextdotjs", "node.js": "nodedotjs", "vue.js": "vuedotjs",
        "socket.io": "socketdotio", "d3.js": "d3dotjs",
    }
    m = marque.strip().lower()
    if m in exceptions:
        return exceptions[m]
    m = m.replace(".", "dot") if re.fullmatch(r"[a-z0-9]+\.[a-z]+", m) else m
    return re.sub(r"[^a-z0-9]", "", m)


def telecharger(marque, couleur=None, delai=20):
    s = slug(marque)
    url = f"{BASE}/{s}" + (f"/{couleur.lstrip('#')}" if couleur else "")
    requete = urllib.request.Request(url, headers={"User-Agent": "chaine-youtube/1.0"})
    with urllib.request.urlopen(requete, timeout=delai) as r:
        contenu = r.read()
    texte = contenu.decode("utf-8", "replace")
    # Simple Icons rend un 404 en HTML : sans ce controle on ecrirait une
    # page d'erreur avec l'extension .svg, et le composant afficherait un
    # carre vide sans que rien ne le signale.
    if "<svg" not in texte[:400].lower():
        raise ValueError(f"Reponse non-SVG pour « {marque} » (slug « {s} ») : marque inconnue ?")
    return contenu, url, s


def main():
    ap = argparse.ArgumentParser(description="Telecharge un logo de marque en SVG (E5b).")
    ap.add_argument("--marque", required=True, help="Nom de la marque, ex. « GitHub », « Anthropic ».")
    ap.add_argument("--sortie", required=True)
    ap.add_argument("--couleur", help="Hex sans #. Par defaut noir, ce qui convient a la "
                                      "pastille claire de PlanLogos sur fond sombre.")
    a = ap.parse_args()

    try:
        contenu, url, s = telecharger(a.marque, a.couleur)
    except (urllib.error.URLError, urllib.error.HTTPError) as e:
        print(json.dumps({"ok": False, "marque": a.marque, "slug": slug(a.marque),
                          "message": f"Telechargement impossible : {e}"}, ensure_ascii=False))
        sys.exit(6)
    except ValueError as e:
        print(json.dumps({"ok": False, "marque": a.marque, "slug": slug(a.marque),
                          "message": str(e)}, ensure_ascii=False))
        sys.exit(5)

    sortie = Path(a.sortie)
    sortie.parent.mkdir(parents=True, exist_ok=True)
    sortie.write_bytes(contenu)
    print(json.dumps({"ok": True, "sortie": str(sortie), "marque": a.marque, "slug": s,
                      "provenance": f"simpleicons:{s}", "licence": "CC0-1.0"},
                     ensure_ascii=False))


if __name__ == "__main__":
    main()
