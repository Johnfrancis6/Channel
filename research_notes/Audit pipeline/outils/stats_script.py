#!/usr/bin/env python3
"""Mesures simples d'un script Zehon et de sa version voix (audit du 07/11/2026).

Usage :
  python3 stats_script.py 02_script.md 02_script_voix.txt

Sortie : nombre de phrases, médiane et écart-type de leur longueur, nombre de
« Sauf que », de questions, de nombres écrits en chiffres, premiers mots les
plus fréquents, et la même chose pour la version voix (une phrase par ligne).
"""
import re
import statistics
import sys
from collections import Counter


def mots(t):
    return re.findall(r"[\w’'-]+", t)


def main(chemin_script, chemin_voix):
    script = open(chemin_script, encoding="utf-8").read()
    voix = open(chemin_voix, encoding="utf-8").read()
    texte = "\n".join(l for l in script.splitlines() if l.strip() and not l.startswith("#"))
    texte = re.sub(r"<!--.*?-->", " ", texte, flags=re.S)
    phrases = [p for p in re.split(r"(?<=[.!?…])\s+", " ".join(texte.split())) if p.strip()]
    longueurs = [len(mots(p)) for p in phrases]
    print(f"script : {len(mots(texte))} mots, {len(phrases)} phrases, médiane {statistics.median(longueurs)}, "
          f"écart-type {statistics.pstdev(longueurs):.1f}")
    print(f"« Sauf que » : {len(re.findall(r'Sauf qu', texte))} ; « Mais » : {len(re.findall(r'Mais', texte))} ; "
          f"questions : {texte.count('?')} ; nombres en chiffres : {len(re.findall(r'[0-9][0-9  ,]*', texte))}")
    print("premiers mots :", Counter(p.split()[0] for p in phrases).most_common(6))
    lignes = [l for l in voix.splitlines() if l.strip()]
    lv = [len(mots(l)) for l in lignes]
    print(f"voix : {len(lignes)} lignes, médiane {statistics.median(lv)}, écart-type {statistics.pstdev(lv):.1f}, "
          f"fins de ligne : {dict(Counter(l.strip()[-1] for l in lignes))}")


if __name__ == "__main__":
    main(*sys.argv[1:3])
