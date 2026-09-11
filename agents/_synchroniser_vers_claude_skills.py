#!/usr/bin/env python3
"""
Deploie les skills du depot vers .claude/skills/, pour que Claude Code les
detecte comme skills de projet quand ce depot est ouvert localement.

Deux sources de verite (§9.2), toutes deux couvertes :
  - agents/short-*/  : les 7 agents du pipeline (A2 a A7, H1) ;
  - skills/*/        : les skills utilitaires (new-short, short-state).

`.claude/skills/` est entierement genere : ne jamais l'editer a la main.
Modifie la source, puis relance ce script.

Les fichiers texte sont normalises en fins de ligne LF a la copie. Les
sources sont en CRLF ; sans cette normalisation, chaque synchronisation
reecrirait integralement les fichiers deployes et polluerait les diffs git.

Usage :
  python3 agents/_synchroniser_vers_claude_skills.py             # synchronise
  python3 agents/_synchroniser_vers_claude_skills.py --verifier   # signale la derive, n'ecrit rien

Le mode --verifier sort en code 1 si un deploiement ne correspond plus a sa
source (fichier manquant, en trop, contenu different, dossier orphelin). Il
existe parce que la derive s'etait deja produite en silence : des scripts
ajoutes dans agents/ n'avaient jamais ete deployes, et les skills reellement
charges par Claude Code tournaient sans eux.
"""
import argparse
import shutil
import sys
from pathlib import Path

RACINE_DEPOT = Path(__file__).resolve().parent.parent
AGENTS_DIR = RACINE_DEPOT / "agents"
SKILLS_DIR = RACINE_DEPOT / "skills"
CIBLE_DIR = RACINE_DEPOT / ".claude" / "skills"

# Extensions traitees comme du texte : contenu normalise en LF a la copie et
# a la comparaison. Tout le reste est copie octet pour octet.
EXTENSIONS_TEXTE = {".md", ".py", ".json", ".txt", ".ts", ".tsx", ".js",
                    ".jsx", ".yaml", ".yml", ".toml", ".cfg", ".ini", ".sh"}

IGNORES = {"__pycache__", ".pytest_cache", ".DS_Store"}


def dossiers_sources():
    """Dossiers a deployer, tous tris confondus, tries par nom de skill."""
    sources = []
    if AGENTS_DIR.is_dir():
        sources += [d for d in AGENTS_DIR.iterdir()
                    if d.is_dir() and d.name.startswith("short-")]
    if SKILLS_DIR.is_dir():
        sources += [d for d in SKILLS_DIR.iterdir()
                    if d.is_dir() and not d.name.startswith(("_", "."))]

    par_nom = {}
    for dossier in sources:
        if dossier.name in par_nom:
            raise SystemExit(
                f"Conflit de nom : {par_nom[dossier.name]} et {dossier} se deploieraient "
                f"tous les deux vers .claude/skills/{dossier.name}."
            )
        par_nom[dossier.name] = dossier
    return [par_nom[nom] for nom in sorted(par_nom)]


def _en_lf(donnees):
    return donnees.replace(b"\r\n", b"\n").replace(b"\r", b"\n")


def contenu_normalise(chemin):
    donnees = chemin.read_bytes()
    return _en_lf(donnees) if chemin.suffix.lower() in EXTENSIONS_TEXTE else donnees


def fichiers_pertinents(racine):
    """Chemins relatifs des fichiers versionnes d'un skill (hors caches)."""
    return {
        p.relative_to(racine)
        for p in racine.rglob("*")
        if p.is_file()
        and not IGNORES & set(p.parts)
        and p.suffix not in (".pyc", ".pyo")
    }


def verifier():
    """Liste des ecarts entre les sources et .claude/skills/."""
    ecarts = []
    attendus = set()

    for source in dossiers_sources():
        attendus.add(source.name)
        cible = CIBLE_DIR / source.name
        if not cible.is_dir():
            ecarts.append(f"{source.name} : absent de .claude/skills/")
            continue

        fichiers_source = fichiers_pertinents(source)
        fichiers_cible = fichiers_pertinents(cible)
        for manquant in sorted(fichiers_source - fichiers_cible):
            ecarts.append(f"{source.name}/{manquant} : manquant dans .claude/skills/")
        for en_trop in sorted(fichiers_cible - fichiers_source):
            ecarts.append(f"{source.name}/{en_trop} : dans .claude/skills/ mais plus dans la source")
        for commun in sorted(fichiers_source & fichiers_cible):
            if contenu_normalise(source / commun) != contenu_normalise(cible / commun):
                ecarts.append(f"{source.name}/{commun} : contenu different")

    if CIBLE_DIR.is_dir():
        for deploye in sorted(CIBLE_DIR.iterdir()):
            if deploye.is_dir() and deploye.name not in attendus:
                ecarts.append(f"{deploye.name} : dossier orphelin dans .claude/skills/ (plus de source)")

    return ecarts


def synchroniser():
    """Regenere .claude/skills/. Retourne (skills deployes, orphelins retires)."""
    CIBLE_DIR.mkdir(parents=True, exist_ok=True)
    sources = dossiers_sources()
    attendus = {s.name for s in sources}

    orphelins = []
    for deploye in sorted(CIBLE_DIR.iterdir()):
        if deploye.is_dir() and deploye.name not in attendus:
            shutil.rmtree(deploye)
            orphelins.append(deploye.name)

    deployes = []
    for source in sources:
        cible = CIBLE_DIR / source.name
        if cible.exists():
            shutil.rmtree(cible)
        for relatif in sorted(fichiers_pertinents(source)):
            destination = cible / relatif
            destination.parent.mkdir(parents=True, exist_ok=True)
            destination.write_bytes(contenu_normalise(source / relatif))
        deployes.append(source.name)

    return deployes, orphelins


def main(argv=None):
    ap = argparse.ArgumentParser(
        description="Deploie agents/short-* et skills/* vers .claude/skills/.")
    ap.add_argument("--verifier", action="store_true",
                    help="signale la derive sans rien ecrire (code 1 si derive)")
    args = ap.parse_args(argv)

    if args.verifier:
        ecarts = verifier()
        if ecarts:
            print("Derive detectee entre les sources et .claude/skills/ :")
            for e in ecarts:
                print(f"  - {e}")
            print("\nRelance : python3 agents/_synchroniser_vers_claude_skills.py")
            return 1
        print("Aucune derive : .claude/skills/ est a jour.")
        return 0

    deployes, orphelins = synchroniser()
    for nom in orphelins:
        print(f"Retire (plus de source) : {nom}")
    print(f"{len(deployes)} skill(s) deploye(s) vers .claude/skills/ : {', '.join(deployes)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
