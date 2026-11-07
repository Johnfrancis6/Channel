#!/usr/bin/env python3
"""Compare le script lisible et la version voix, mot à mot (audit du 07/11/2026).

Les nombres du script sont redits en lettres avec la fonction de monter.py, pour
ne garder que les vrais écarts (mots ajoutés, retirés ou réécrits).

Usage :
  python3 diff_script_voix.py 02_script.md 02_script_voix.txt <dossier de monter.py>

Exemple : <dossier de monter.py> = zehon/video-maker/scripts (branche optimistic-bohr).
"""
import difflib
import sys


def main(chemin_script, chemin_voix, dossier_monter):
    sys.path.insert(0, dossier_monter)
    import monter  # noqa: E402  (jetons() redit les nombres en lettres)

    script = open(chemin_script, encoding="utf-8").read()
    voix = open(chemin_voix, encoding="utf-8").read()
    script = "\n".join(l for l in script.splitlines() if l.strip() and not l.startswith("#"))
    a = [x if isinstance(x, str) else x[0] for x in monter.jetons(script)]
    b = [x if isinstance(x, str) else x[0] for x in monter.jetons(voix)]
    comparaison = difflib.SequenceMatcher(None, a, b, autojunk=False)
    ecarts = 0
    for op, i1, i2, j1, j2 in comparaison.get_opcodes():
        if op != "equal":
            ecarts += 1
            print(f"{op:8} script : {' '.join(a[i1:i2])[:60]!r:65} voix : {' '.join(b[j1:j2])[:60]!r}")
    print(f"écarts : {ecarts} ; similarité {comparaison.ratio():.3f} ; mots script {len(a)}, voix {len(b)}")


if __name__ == "__main__":
    main(*sys.argv[1:4])
