#!/usr/bin/env python3
"""Enveloppe de tools/sync_skills.py, gardée pour la documentation Zehon.

Le vrai outil couvre les deux chaînes (zehon/ et whosedime/) et écrit un
fichier VERSION dans chaque copie générée :

  python3 zehon/synchroniser_skills.py             # = python3 tools/sync_skills.py
  python3 zehon/synchroniser_skills.py --verifier   # = python3 tools/sync_skills.py --check
"""
import importlib.util
import sys
from pathlib import Path

_CHEMIN = Path(__file__).resolve().parent.parent / "tools" / "sync_skills.py"
_spec = importlib.util.spec_from_file_location("sync_skills", _CHEMIN)
_outil = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_outil)

skills = _outil.skills
archive = _outil.archive
version = _outil.version
ecarts = _outil.drift
synchroniser = _outil.sync


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    return _outil.main(["--check" if a == "--verifier" else a for a in argv])


if __name__ == "__main__":
    sys.exit(main())
