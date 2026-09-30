#!/usr/bin/env python3
"""Déploie les skills Zehon (zehon/<skill>/) vers .claude/skills/, et reconstruit
l'archive à installer sur claude.ai (zehon/<skill>.skill).

`.claude/skills/` et les `.skill` sont entièrement générés : ne jamais les
éditer à la main. Modifier la source dans zehon/<skill>/, puis relancer :

  python3 zehon/synchroniser_skills.py             # synchronise
  python3 zehon/synchroniser_skills.py --verifier   # signale la dérive, n'écrit rien (code 1 si dérive)

Seuls les dossiers qui portent un SKILL.md sont des skills (les espaces de
test zehon/*-workspace/ sont ignorés). L'archive .skill n'embarque pas
evals/ : les cas de test servent au dépôt, pas à la skill installée.
"""
import argparse
import io
import shutil
import sys
import zipfile
from pathlib import Path

ZEHON = Path(__file__).resolve().parent
CIBLE = ZEHON.parent / ".claude" / "skills"
IGNORES = {"__pycache__", ".pytest_cache", ".DS_Store"}
HORS_ARCHIVE = {"evals"}
DATE_FIXE = (2026, 1, 1, 0, 0, 0)  # archive reproductible : même source, mêmes octets


def skills():
    return sorted(d for d in ZEHON.iterdir() if d.is_dir() and (d / "SKILL.md").is_file())


def fichiers(racine, exclus=()):
    return sorted(p.relative_to(racine) for p in racine.rglob("*")
                  if p.is_file() and not (IGNORES | set(exclus)) & set(p.relative_to(racine).parts)
                  and p.suffix not in (".pyc", ".pyo"))


def archive(source):
    """Les octets du .skill : un zip de <skill>/..., sans evals/, à date fixe."""
    tampon = io.BytesIO()
    with zipfile.ZipFile(tampon, "w", zipfile.ZIP_DEFLATED) as z:
        for relatif in fichiers(source, HORS_ARCHIVE):
            info = zipfile.ZipInfo(f"{source.name}/{relatif.as_posix()}", DATE_FIXE)
            info.compress_type = zipfile.ZIP_DEFLATED
            z.writestr(info, (source / relatif).read_bytes())
    return tampon.getvalue()


def ecarts():
    trouves = []
    noms = {s.name for s in skills()}
    for source in skills():
        cible = CIBLE / source.name
        attendu, present = set(fichiers(source)), set(fichiers(cible)) if cible.is_dir() else set()
        trouves += [f"{source.name}/{f} : manquant dans .claude/skills/" for f in sorted(attendu - present)]
        trouves += [f"{source.name}/{f} : en trop dans .claude/skills/" for f in sorted(present - attendu)]
        trouves += [f"{source.name}/{f} : contenu différent" for f in sorted(attendu & present)
                    if (source / f).read_bytes() != (cible / f).read_bytes()]
        paquet = ZEHON / f"{source.name}.skill"
        if not paquet.is_file() or paquet.read_bytes() != archive(source):
            trouves.append(f"{paquet.name} : pas à jour")
    if CIBLE.is_dir():
        trouves += [f"{d.name} : dossier orphelin dans .claude/skills/"
                    for d in sorted(CIBLE.iterdir()) if d.is_dir() and d.name not in noms]
    return trouves


def synchroniser():
    CIBLE.mkdir(parents=True, exist_ok=True)
    noms = {s.name for s in skills()}
    for d in CIBLE.iterdir():
        if d.is_dir() and d.name not in noms:
            shutil.rmtree(d)
    for source in skills():
        cible = CIBLE / source.name
        if cible.exists():
            shutil.rmtree(cible)
        for relatif in fichiers(source):
            (cible / relatif).parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(source / relatif, cible / relatif)
        (ZEHON / f"{source.name}.skill").write_bytes(archive(source))
    return sorted(noms)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--verifier", action="store_true", help="signale la dérive sans rien écrire")
    if ap.parse_args(argv).verifier:
        trouves = ecarts()
        for e in trouves:
            print(e)
        print("Aucune dérive." if not trouves else "\nRelance : python3 zehon/synchroniser_skills.py")
        return 1 if trouves else 0
    print("Synchronisé :", ", ".join(synchroniser()))
    return 0


if __name__ == "__main__":
    sys.exit(main())
