#!/usr/bin/env python3
"""
Copie chaque agents/short-*/ (source de verite, §9.2) vers .claude/skills/
a la racine du depot, pour que Claude Code les detecte comme skills de
projet quand ce depot est ouvert localement.

Ne jamais editer directement .claude/skills/ : modifie agents/short-*/,
puis relance ce script.

Usage :
  python3 agents/_synchroniser_vers_claude_skills.py             # synchronise
  python3 agents/_synchroniser_vers_claude_skills.py --verifier   # signale la derive, n'ecrit rien

Le mode --verifier sort en code 1 si la copie deployee ne correspond plus a
la source (fichier manquant, en trop, ou contenu different). Il existe parce
que la derive s'etait deja produite en silence : generer_storyboard.py et
rendre_video.py avaient ete ajoutes dans agents/ sans que le script soit
relance, donc les skills deployes tournaient sans eux.
"""
import argparse
import filecmp
import shutil
import sys
from pathlib import Path

RACINE_DEPOT = Path(__file__).resolve().parent.parent
AGENTS_DIR = RACINE_DEPOT / "agents"
CIBLE_DIR = RACINE_DEPOT / ".claude" / "skills"
IGNORES = shutil.ignore_patterns("__pycache__", "*.pyc")


def dossiers_sources():
    return [d for d in sorted(AGENTS_DIR.iterdir())
            if d.is_dir() and d.name.startswith("short-")]


def _fichiers_pertinents(racine):
    """Chemins relatifs des fichiers versionnes d'un skill (hors caches Python)."""
    return {
        p.relative_to(racine)
        for p in racine.rglob("*")
        if p.is_file() and "__pycache__" not in p.parts and p.suffix != ".pyc"
    }


def verifier():
    """Retourne la liste des ecarts entre agents/short-* et .claude/skills/."""
    ecarts = []
    for source in dossiers_sources():
        cible = CIBLE_DIR / source.name
        if not cible.is_dir():
            ecarts.append(f"{source.name} : absent de .claude/skills/")
            continue
        fichiers_source = _fichiers_pertinents(source)
        fichiers_cible = _fichiers_pertinents(cible)
        for manquant in sorted(fichiers_source - fichiers_cible):
            ecarts.append(f"{source.name}/{manquant} : manquant dans .claude/skills/")
        for en_trop in sorted(fichiers_cible - fichiers_source):
            ecarts.append(f"{source.name}/{en_trop} : present dans .claude/skills/ mais plus dans agents/")
        for commun in sorted(fichiers_source & fichiers_cible):
            if not filecmp.cmp(source / commun, cible / commun, shallow=False):
                ecarts.append(f"{source.name}/{commun} : contenu different")
    return ecarts


def synchroniser():
    CIBLE_DIR.mkdir(parents=True, exist_ok=True)
    copies = []
    for dossier in dossiers_sources():
        cible = CIBLE_DIR / dossier.name
        if cible.exists():
            shutil.rmtree(cible)
        shutil.copytree(dossier, cible, ignore=IGNORES)
        copies.append(dossier.name)
    return copies


def main(argv=None):
    ap = argparse.ArgumentParser(description="Synchronise agents/short-* vers .claude/skills/.")
    ap.add_argument("--verifier", action="store_true",
                    help="signale la derive sans rien ecrire (code 1 si derive)")
    args = ap.parse_args(argv)

    if args.verifier:
        ecarts = verifier()
        if ecarts:
            print("Derive detectee entre agents/short-* et .claude/skills/ :")
            for e in ecarts:
                print(f"  - {e}")
            print("\nRelance : python3 agents/_synchroniser_vers_claude_skills.py")
            return 1
        print("Aucune derive : .claude/skills/ est a jour.")
        return 0

    copies = synchroniser()
    print(f"{len(copies)} skill(s) synchronise(s) vers .claude/skills/ : {', '.join(copies)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
