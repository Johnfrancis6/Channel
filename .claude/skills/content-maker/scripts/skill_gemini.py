#!/usr/bin/env python3
"""Fabrique le dossier de la skill Gemini `zehon-images` d'une vidéo.

  python3 scripts/skill_gemini.py 03_scenes.md [04_publication.md] --sortie zehon-images/ [--planche planche_bonhomme.jpg]

Le dossier produit s'importe tel quel dans Gemini (Paramètres > Skills >
Importer) : SKILL.md (le modèle, assets/zehon-images/SKILL.md), prompts.md
(les lots de la vidéo, la palette, les miniatures) et, si on la donne, la
planche du bonhomme. Sans --planche, Franco l'ajoute au dossier lui-même.
"""
import argparse
import re
import shutil
import sys
from pathlib import Path

MODELE = Path(__file__).resolve().parent.parent / "assets" / "zehon-images" / "SKILL.md"


def prompts_scenes(scenes):
    """(sujet, palette, titres, bloc des lots) lus dans 03_scenes.md."""
    sujet = re.search(r"^# Scènes — (.+)$", scenes, re.M)
    palette = re.search(r"Palette: (.+?)\. The main character", scenes)
    titres = [m.group(1) for m in re.finditer(r"^\|\s*(\d+)\s*\|\s*titre\s*\|", scenes, re.M)]
    debut = scenes.find("### Lot ")
    if debut < 0:
        raise ValueError("aucun « ### Lot » dans le fichier de scènes")
    fin = scenes.find("\n## ", debut)
    lots = scenes[debut:fin if fin >= 0 else len(scenes)].strip()
    return (sujet.group(1).strip() if sujet else "?"), (palette.group(1) if palette else None), titres, lots


def prompts_miniatures(publication):
    """Les blocs **Mn** de la section ## Miniatures : la ligne de titre et le prompt."""
    section = re.search(r"^## Miniatures\n(.*?)(?=^## |\Z)", publication, re.M | re.S)
    if not section:
        return []
    blocs = []
    lignes = section.group(1).splitlines()
    for i, ligne in enumerate(lignes):
        if re.match(r"\*\*M\d+\*\*", ligne) and i + 1 < len(lignes) and lignes[i + 1].startswith("> "):
            blocs.append(f"{ligne}\n{lignes[i + 1]}")
    return blocs


def fabriquer(scenes, publication=None):
    sujet, palette, titres, lots = prompts_scenes(scenes)
    morceaux = [f"# Prompts — {sujet}", ""]
    if palette:
        morceaux += [f"Palette: {palette}.", ""]
    if titres:
        morceaux += [f"Sans image (scènes de titre) : {', '.join(titres)}.", ""]
    morceaux += [lots, ""]
    miniatures = prompts_miniatures(publication) if publication else []
    if miniatures:
        morceaux += ["## Miniatures", ""] + [b + "\n" for b in miniatures]
    return "\n".join(morceaux).rstrip() + "\n"


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("scenes")
    ap.add_argument("publication", nargs="?")
    ap.add_argument("--sortie", required=True)
    ap.add_argument("--planche")
    a = ap.parse_args(argv)
    scenes = Path(a.scenes).read_text(encoding="utf-8")
    publication = Path(a.publication).read_text(encoding="utf-8") if a.publication else None
    sortie = Path(a.sortie)
    sortie.mkdir(parents=True, exist_ok=True)
    texte = fabriquer(scenes, publication)
    (sortie / "prompts.md").write_text(texte, encoding="utf-8")
    shutil.copyfile(MODELE, sortie / "SKILL.md")
    if a.planche:
        shutil.copyfile(a.planche, sortie / Path(a.planche).name)
    n = len(re.findall(r"^\*\*scene_\d{3}\*\*", texte, re.M))
    m = len(re.findall(r"^\*\*M\d+\*\*", texte, re.M))
    print(f"{sortie}/ : SKILL.md, prompts.md ({n} scènes, {m} miniatures)"
          + ("" if a.planche else " ; ajouter planche_bonhomme.jpg"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
