#!/usr/bin/env python3
"""
phrases_depuis_timestamps.py — reconstruit `04_phrases.json` a partir de
`04_timestamps.json` et `03_script_tts.txt` (§7.2).

Le notebook n'ecrit les bornes de phrases que lors d'une **synthese
complete** : il les connait exactement, puisqu'il assemble lui-meme les
clips. Les videos dont l'audio est anterieur a cette revision n'ont donc
pas de `04_phrases.json`, et les relancer coute une re-synthese entiere —
sur 2026-09-11_v01, elle est de surcroit bloquee par le plafond de
tentatives (8 essais).

Ce script reconstruit les bornes en realignant les mots transcrits sur le
script. **C'est une approximation, et le notebook la deconseille** : le
WER n'est pas nul, donc l'alignement peut deriver. Deux garde-fous :

- il mesure son propre alignement (`taux_alignement`) et **refuse** d'ecrire
  sous le seuil, plutot que de produire des bornes fausses qui decaleraient
  tout le montage ;
- le fichier produit porte `source: "reconstruit"`, pour qu'on ne le
  confonde jamais avec des bornes exactes.

A utiliser pour rattraper une video ancienne. Pour une video neuve, c'est
le notebook qui a raison.

Usage :
  python3 phrases_depuis_timestamps.py --timestamps 04_timestamps.json \\
    --script 03_script_tts.txt --sortie 04_phrases.json [--audio 04_voixoff.wav]
"""
import argparse
import difflib
import json
import re
import sys
import unicodedata
import wave
from pathlib import Path

SEUIL_ALIGNEMENT_DEFAUT = 0.80


def normaliser(mot):
    """Minuscules, sans accent ni ponctuation : LLM, 'LLM,' et 'llm' sont un."""
    sans_accent = unicodedata.normalize("NFKD", mot).encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z0-9]", "", sans_accent.lower())


def decouper(texte):
    return [t for t in (normaliser(m) for m in texte.split()) if t]


def lire_phrases(chemin):
    """Une ligne non vide = une phrase, comme le notebook et A6 les lisent."""
    return [l.strip() for l in Path(chemin).read_text(encoding="utf-8-sig").splitlines()
            if l.strip()]


def lire_mots(chemin):
    mots = []
    for entree in json.loads(Path(chemin).read_text(encoding="utf-8-sig")):
        if not isinstance(entree, dict):
            continue
        mot, debut, fin = entree.get("mot"), entree.get("debut_s"), entree.get("fin_s")
        if mot is None or debut is None or fin is None:
            continue
        mots.append({"mot": str(mot), "debut_s": float(debut), "fin_s": float(fin)})
    return mots


def duree_wav(chemin):
    """Duree exacte du wav. Sans elle, la derniere scene s'arrete au dernier
    mot et laisse tomber la queue de silence."""
    try:
        with wave.open(str(chemin), "rb") as w:
            return round(w.getnframes() / w.getframerate(), 3)
    except (OSError, wave.Error):
        return None


def apparier(phrases, mots):
    """
    [(index du mot transcrit)] par phrase, via un alignement de sequences.

    Un simple decoupage par nombre de mots derive des le premier mot insere
    ou omis par la transcription. difflib retrouve les blocs communs, donc
    un ecart local reste local.
    """
    tokens_script, phrase_du_token = [], []
    for i, phrase in enumerate(phrases):
        for token in decouper(phrase):
            tokens_script.append(token)
            phrase_du_token.append(i)

    tokens_transcrits, mot_du_token = [], []
    for j, m in enumerate(mots):
        for token in decouper(m["mot"]):
            tokens_transcrits.append(token)
            mot_du_token.append(j)

    correspondances = [[] for _ in phrases]
    apparies = 0
    matcher = difflib.SequenceMatcher(None, tokens_script, tokens_transcrits, autojunk=False)
    for i, j, taille in matcher.get_matching_blocks():
        for k in range(taille):
            correspondances[phrase_du_token[i + k]].append(mot_du_token[j + k])
            apparies += 1

    taux = apparies / len(tokens_script) if tokens_script else 0.0
    return correspondances, round(taux, 4)


def _combler(bornes, fin_audio):
    """
    Une phrase sans aucun mot apparie n'a pas de bornes : on l'intercale
    entre ses voisines plutot que de la perdre, et on garde l'ordre
    croissant — une borne qui recule ferait une scene de duree negative.
    """
    avertissements = []
    connus = [i for i, b in enumerate(bornes) if b is not None]
    if not connus:
        return None, ["Aucune phrase appariee."]

    for i, borne in enumerate(bornes):
        if borne is not None:
            continue
        avant = [j for j in connus if j < i]
        apres = [j for j in connus if j > i]
        debut = bornes[avant[-1]]["fin_s"] if avant else 0.0
        fin = bornes[apres[0]]["debut_s"] if apres else fin_audio
        milieu = round((debut + fin) / 2, 3)
        bornes[i] = {"debut_s": debut, "fin_s": milieu}
        avertissements.append(f"Phrase {i + 1} non appariee : bornes interpolees.")

    precedent = 0.0
    for borne in bornes:
        borne["debut_s"] = round(max(borne["debut_s"], precedent), 3)
        borne["fin_s"] = round(max(borne["fin_s"], borne["debut_s"]), 3)
        precedent = borne["fin_s"]
    return bornes, avertissements


def reconstruire(phrases, mots, duree_totale=None):
    """(resultat, avertissements) au format ecrit par le notebook (§7.2)."""
    if not phrases:
        raise ValueError("Script vide : aucune phrase.")
    if not mots:
        raise ValueError("Aucun mot horodate exploitable.")

    correspondances, taux = apparier(phrases, mots)
    fin_audio = duree_totale if duree_totale is not None else mots[-1]["fin_s"]

    bornes = []
    for indices in correspondances:
        if not indices:
            bornes.append(None)
            continue
        bornes.append({"debut_s": mots[min(indices)]["debut_s"],
                       "fin_s": mots[max(indices)]["fin_s"]})

    bornes, avertissements = _combler(bornes, fin_audio)
    if bornes is None:
        raise ValueError("Aucune phrase n'a pu etre appariee aux mots transcrits.")

    resultat = {
        "phrases": [{"index": i + 1, "texte": phrases[i],
                     "debut_s": b["debut_s"], "fin_s": b["fin_s"]}
                    for i, b in enumerate(bornes)],
        "duree_totale_s": round(fin_audio, 3),
        "pause_ms": None,
        "taux_hz": None,
        # Ce que le notebook n'a pas a dire, et que ce fichier doit dire.
        "source": "reconstruit",
        "taux_alignement": taux,
    }
    if duree_totale is None:
        avertissements.append(
            "Duree totale deduite du dernier mot transcrit : la queue de silence "
            "est perdue. Passe --audio 04_voixoff.wav pour la duree exacte.")
    return resultat, avertissements


def main():
    ap = argparse.ArgumentParser(
        description="Reconstruit 04_phrases.json depuis 04_timestamps.json (§7.2).")
    ap.add_argument("--timestamps", required=True)
    ap.add_argument("--script", required=True, help="03_script_tts.txt")
    ap.add_argument("--sortie", required=True, help="04_phrases.json a ecrire")
    ap.add_argument("--audio", help="04_voixoff.wav — donne la duree totale exacte")
    ap.add_argument("--seuil", type=float, default=SEUIL_ALIGNEMENT_DEFAUT,
                    help=f"Taux d'alignement minimal (defaut {SEUIL_ALIGNEMENT_DEFAUT}).")
    ap.add_argument("--forcer", action="store_true",
                    help="Ecrit meme sous le seuil, en connaissance de cause.")
    a = ap.parse_args()

    duree = duree_wav(a.audio) if a.audio else None
    try:
        resultat, avertissements = reconstruire(lire_phrases(a.script),
                                                lire_mots(a.timestamps), duree)
    except (OSError, ValueError, json.JSONDecodeError) as e:
        print(json.dumps({"ok": False, "message": str(e)}, ensure_ascii=False, indent=2))
        return 2

    taux = resultat["taux_alignement"]
    if taux < a.seuil and not a.forcer:
        print(json.dumps({
            "ok": False,
            "message": (f"Alignement trop faible ({taux:.1%} < {a.seuil:.0%}) : les bornes "
                        f"seraient fausses et decaleraient tout le montage. Verifie que le "
                        f"script correspond bien a l'audio, ou relance une synthese complete. "
                        f"Pour passer outre : --forcer."),
            "taux_alignement": taux,
        }, ensure_ascii=False, indent=2))
        return 4

    Path(a.sortie).write_text(json.dumps(resultat, ensure_ascii=False, indent=2),
                              encoding="utf-8")
    print(json.dumps({"ok": True, "sortie": a.sortie, "phrases": len(resultat["phrases"]),
                      "taux_alignement": taux, "duree_totale_s": resultat["duree_totale_s"],
                      "avertissements": avertissements},
                     ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
