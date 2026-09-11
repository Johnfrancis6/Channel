#!/usr/bin/env python3
"""
metriques.py — mesure objective des phrases d'un script, pour appuyer le
jugement du Filtre TTS (§7.3). Le style (zombie nouns, ton) reste un
jugement qualitatif a faire par Claude ; ce script ne fait que compter.

Usage : python3 metriques.py --fichier 02_script_brut.md
Sortie : JSON (resume + detail par phrase).
"""
import argparse
import json
import re


def decouper_phrases(texte):
    texte = re.sub(r"\s+", " ", texte).strip()
    return [p.strip() for p in re.split(r"(?<=[.!?])\s+", texte) if p.strip()]


def analyser(phrase):
    mots = phrase.split()
    n = len(mots)
    triade_probable = phrase.count(",") >= 2 or bool(
        re.search(r",\s*[\w'-]+\s*,\s*(and|et)\s+[\w'-]+", phrase, re.IGNORECASE)
    )
    return {
        "phrase": phrase,
        "mots": n,
        "trop_longue": n > 22,
        "trop_courte": n < 4,
        "virgules": phrase.count(","),
        "triade_probable": triade_probable,
        "contient_parenthese_ou_url": bool(re.search(r"[()]|https?://", phrase)),
    }


def main():
    ap = argparse.ArgumentParser(description="Metriques de calibrage des phrases (§7.3).")
    ap.add_argument("--fichier", required=True)
    a = ap.parse_args()

    with open(a.fichier, encoding="utf-8") as f:
        texte = f.read()

    phrases = [analyser(p) for p in decouper_phrases(texte)]
    resume = {
        "nb_phrases": len(phrases),
        "trop_longues": sum(1 for p in phrases if p["trop_longue"]),
        "trop_courtes": sum(1 for p in phrases if p["trop_courte"]),
        "triades_probables": sum(1 for p in phrases if p["triade_probable"]),
        "parentheses_ou_url": sum(1 for p in phrases if p["contient_parenthese_ou_url"]),
    }
    print(json.dumps({"resume": resume, "phrases": phrases}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
