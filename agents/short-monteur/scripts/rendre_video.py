#!/usr/bin/env python3
"""
rendre_video.py — orchestre le rendu complet de l'etape E6_montage (§8) :
verifie les prerequis, lance `remotion render` sur les props deja
construites par construire_props.py, et verifie le MP4 produit.

Usage :
  python3 rendre_video.py --video ID --root R --props P.json \
      --sortie videos/ID/06_video_finale.mp4 [--browser CHEMIN] [--dry-run]

Sortie : JSON sur stdout. Codes :
  0 ok | 2 props absentes/invalides | 4 node_modules absent |
  5 registry.ts inaccessible | 6 echec remotion render | 7 mp4 absent/vide
"""
import argparse
import json
import os
import subprocess
import sys
from pathlib import Path

def trouver_repo_root():
    """
    Racine du depot, trouvee en remontant jusqu'au dossier qui contient la
    bibliotheque de composants.

    Un simple `parents[3]` marche depuis agents/short-monteur/scripts/ mais
    pas depuis la copie deployee dans .claude/skills/short-monteur/scripts/,
    qui n'a pas la meme profondeur : il y designait `.claude/`, ou il n'y a
    pas de composants/. Le skill documente pourtant l'appel par le chemin du
    skill — la commande de la doc etait donc la seule a ne pas marcher. On
    cherche le repere plutot que de compter les niveaux.
    """
    depart = Path(__file__).resolve()
    for candidat in depart.parents:
        if (candidat / "composants" / "src" / "components" / "registry.ts").is_file():
            return candidat
    return depart.parents[3]


REPO_ROOT = trouver_repo_root()
COMPOSANTS = REPO_ROOT / "composants"
REGISTRY_TS = COMPOSANTS / "src" / "components" / "registry.ts"


def sortir(code, **data):
    print(json.dumps({"ok": code == 0, **data}, ensure_ascii=False, indent=2))
    sys.exit(code)


def verifier_prerequis(props_path):
    if not (COMPOSANTS / "node_modules").is_dir():
        return 4, "composants/node_modules absent — lance 'npm install' dans composants/"
    if not props_path.is_file():
        return 2, f"Fichier props introuvable : {props_path}"
    try:
        json.loads(props_path.read_text(encoding="utf-8-sig"))
    except json.JSONDecodeError as e:
        return 2, f"Props JSON invalide ({props_path}) : {e}"
    if not REGISTRY_TS.is_file():
        return 5, f"registry.ts inaccessible : {REGISTRY_TS}"
    return 0, None


def main():
    ap = argparse.ArgumentParser(description="Rend la video finale (E6, §8) via remotion render.")
    ap.add_argument("--video", required=True, help="video_id")
    ap.add_argument("--root", required=True, help="Racine de /ChaineYouTube")
    ap.add_argument("--props", required=True, help="Chemin du fichier props.json")
    ap.add_argument("--sortie", required=True, help="Chemin du .mp4 a produire")
    ap.add_argument("--browser", help="Executable Chromium (REMOTION_BROWSER_EXECUTABLE)")
    ap.add_argument("--dry-run", action="store_true", help="Verifie les prerequis sans rendre")
    a = ap.parse_args()

    racine = Path(a.root).expanduser()
    props_path = Path(a.props)
    if not props_path.is_absolute():
        props_path = racine / props_path
    sortie_path = Path(a.sortie)
    if not sortie_path.is_absolute():
        sortie_path = racine / sortie_path

    code, message = verifier_prerequis(props_path)
    if code != 0:
        sortir(code, message=message)

    if a.dry_run:
        sortir(0, dry_run=True, video=a.video, node_modules=True,
               props_valide=True, registry_accessible=True)

    sortie_path.parent.mkdir(parents=True, exist_ok=True)

    env = dict(os.environ)
    if a.browser:
        env["REMOTION_BROWSER_EXECUTABLE"] = a.browser

    cmd = ["npx", "remotion", "render", "src/index.ts", "Video",
           str(sortie_path), f"--props={props_path}"]
    # Pas de capture_output : stdout/stderr de remotion sont heredites et
    # s'affichent en temps reel, sans etre bufferises.
    resultat = subprocess.run(cmd, cwd=str(COMPOSANTS), env=env)

    if resultat.returncode != 0:
        sortir(6, message="Remotion render failed", code=resultat.returncode)

    if not sortie_path.is_file() or sortie_path.stat().st_size == 0:
        sortir(7, message=f"MP4 absent ou vide apres rendu : {sortie_path}")

    sortir(0, sortie=str(sortie_path), taille_bytes=sortie_path.stat().st_size)


if __name__ == "__main__":
    main()
