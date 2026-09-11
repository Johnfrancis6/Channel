#!/usr/bin/env python3
"""
Copie chaque agents/short-*/ (source de verite, §9.2) vers .claude/skills/
a la racine du depot, pour que Claude Code les detecte comme skills de
projet quand ce depot est ouvert localement.

Ne jamais editer directement .claude/skills/ : modifie agents/short-*/,
puis relance ce script.

Usage : python3 agents/_synchroniser_vers_claude_skills.py
"""
import shutil
from pathlib import Path

RACINE_DEPOT = Path(__file__).resolve().parent.parent
AGENTS_DIR = RACINE_DEPOT / "agents"
CIBLE_DIR = RACINE_DEPOT / ".claude" / "skills"


def main():
    CIBLE_DIR.mkdir(parents=True, exist_ok=True)
    copies = []
    for dossier in sorted(AGENTS_DIR.iterdir()):
        if not dossier.is_dir() or not dossier.name.startswith("short-"):
            continue
        cible = CIBLE_DIR / dossier.name
        if cible.exists():
            shutil.rmtree(cible)
        shutil.copytree(dossier, cible, ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
        copies.append(dossier.name)

    print(f"{len(copies)} skill(s) synchronise(s) vers .claude/skills/ : {', '.join(copies)}")


if __name__ == "__main__":
    main()
