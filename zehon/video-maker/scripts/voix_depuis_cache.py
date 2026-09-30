#!/usr/bin/env python3
"""Reconstitue voix/voix.wav à partir des phrases de voix/cache/ (NNNN_<clé>.wav).

  python3 voix_depuis_cache.py <dossier_video>

Pourquoi : le connecteur Drive ne télécharge pas plus de 10 Mo par fichier (mesuré le
30/09/2026), et voix.wav en fait plus de 20. Les phrases du cache, elles, font chacune moins
de 400 ko. On les recolle comme le notebook voix_zehon.ipynb : dans l'ordre, séparées par
`pause_ms` de silence (lu dans voix/mots.json). Le volume n'est pas retouché ici : monter.py
normalise le son au montage.

Seules les phrases 1 à N consécutives sont recollées (un extrait du début suffit pour un
rendu court) ; le script dit où il s'arrête.
"""
import json
import re
import sys
import wave
from pathlib import Path


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    if len(argv) != 1:
        print(__doc__)
        return 2
    dossier = Path(argv[0])
    cache = dossier / "voix" / "cache"
    pause_ms = json.loads((dossier / "voix" / "mots.json").read_text(encoding="utf-8")).get("pause_ms", 300)
    par_numero = {}
    for f in cache.glob("*.wav"):
        m = re.match(r"(\d{4})_", f.name)
        if m:
            par_numero[int(m.group(1))] = f
    if 1 not in par_numero:
        print("❌ voix/cache/0001_*.wav introuvable")
        return 1
    n = 1
    with wave.open(str(par_numero[1])) as w:
        parametres = w.getparams()
    silence = b"\x00" * (int(parametres.framerate * pause_ms / 1000) * parametres.sampwidth * parametres.nchannels)
    with wave.open(str(dossier / "voix" / "voix.wav"), "wb") as sortie:
        sortie.setparams(parametres)
        while n in par_numero:
            with wave.open(str(par_numero[n])) as w:
                if (w.getframerate(), w.getsampwidth(), w.getnchannels()) != (
                        parametres.framerate, parametres.sampwidth, parametres.nchannels):
                    print(f"❌ phrase {n} : format différent des autres")
                    return 1
                if n > 1:
                    sortie.writeframes(silence)
                sortie.writeframes(w.readframes(w.getnframes()))
            n += 1
        duree = sortie.tell() / parametres.framerate
    print(f"✓ voix/voix.wav : phrases 1 à {n - 1}, {duree:.2f} s")
    return 0


if __name__ == "__main__":
    sys.exit(main())
