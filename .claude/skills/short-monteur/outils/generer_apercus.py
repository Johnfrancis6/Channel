#!/usr/bin/env python3
"""
generer_apercus.py — rend une image par composant et par variante de
parametres, pour que le Designer (A6) choisisse en regardant plutot qu'en
devinant (§8).

Le §8 prevoit « un apercu » par composant dans composants/REGISTRE.md
depuis le depart ; il n'a jamais existe. Consequence observee sur
2026-09-11_v01 : A6 a demande `scene="workflow_fixed_path"` — une cle
opaque — sans avoir jamais vu ce que ca rend. Pendant 14,4 s de video, ce
qui etait a l'ecran n'avait ete decide par personne : A7 l'a invente au
moment de coder. On ne cadre pas ce qu'on n'a jamais vu.

Les apercus passent par la **composition de rendu reelle** (`Video`, une
seule scene) : ce qu'on voit dans le catalogue est exactement ce que la
video montrera, tokens de charte compris.

Les variantes a rendre sont declarees dans composants/apercus.json. A7 le
met a jour quand il cree un composant, comme il met a jour REGISTRE.md.

Usage :
  python3 generer_apercus.py [--charte CHARTE.json] [--composant NOM]
                             [--frame N] [--browser CHEMIN] [--liste]

Sortie : JSON sur stdout. Codes :
  0 ok | 2 apercus.json absent/invalide | 4 node_modules absent |
  6 echec d'un rendu
"""
import argparse
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
COMPOSANTS = REPO_ROOT / "composants"
DECLARATION = COMPOSANTS / "apercus.json"
SORTIE_DIR = COMPOSANTS / "apercus"
REGISTRY_TS = COMPOSANTS / "src" / "components" / "registry.ts"

# 1 s : apres l'animation d'entree (~0,3 s par defaut), donc en regime
# etabli. Une frame 0 montrerait surtout des elements a opacite zero.
FRAME_DEFAUT = 30
DUREE_SCENE_S = 3


def sortir(code, **data):
    print(json.dumps({"ok": code == 0, **data}, ensure_ascii=False, indent=2))
    sys.exit(code)


def charger_declaration():
    try:
        data = json.loads(DECLARATION.read_text(encoding="utf-8-sig"))
    except FileNotFoundError:
        sortir(2, message=f"Declaration introuvable : {DECLARATION}")
    except json.JSONDecodeError as e:
        sortir(2, message=f"apercus.json invalide : {e}")
    if not isinstance(data, dict) or not data:
        sortir(2, message="apercus.json doit etre un objet {Composant: [variantes]} non vide.")
    return data


def charte_par_defaut():
    """Charte de repli quand aucune n'est fournie : celle de Root.tsx."""
    return {
        "couleurs": {"fond": "#0B0F14", "texte_principal": "#F5F7FA",
                     "accent": "#5B8CFF", "accent_secondaire": "#FFD166"},
        "typographie": {"sous_titres": {"famille": "Arial, sans-serif",
                                        "taille_px": 64, "graisse": "bold"}},
        "rythme": {"duree_transition_s": 0.3, "easing": "ease-in-out"},
        "animation": {"easing_entree": "ease-out", "easing_transition": "ease-in-out",
                      "duree_entree_s": 0.3, "technique_defaut": "spring",
                      "wobble": {"actif": True, "amplitude_px": 6,
                                 "periode_s": 1.2, "cible": "trace_main"}},
        "format": {"largeur_px": 1080, "hauteur_px": 1920, "fps": 30},
    }


def variantes(declaration, filtre=None):
    """[(composant, nom_variante, params, da)] a rendre."""
    resultat = []
    for composant, liste in sorted(declaration.items()):
        if filtre and composant != filtre:
            continue
        for i, variante in enumerate(liste or []):
            nom = variante.get("nom") or f"v{i + 1}"
            resultat.append((composant, nom, variante.get("params") or {}, variante.get("da")))
    return resultat


def props_pour(composant, params, da, charte):
    scene = {"id": "apercu", "composant": composant, "duree_s": DUREE_SCENE_S, "params": params}
    if da:
        scene["da"] = da
    # Deux mots horodates factices, et non `mots: []`. Avec une liste vide
    # Subtitles ne rend rien, et le catalogue ne montrait jamais la bande
    # basse qu'il occupe (`paddingBottom: 220`) — alors que « un element du
    # composant passe sous les sous-titres » est precisement le genre de
    # defaut qu'un apercu doit attraper. Le docstring promettait « exactement
    # ce que la video montrera » : ce n'etait pas vrai sur ce point.
    mots = [{"mot": "apercu", "debut_s": 0.0, "fin_s": 0.6},
            {"mot": "sous-titre", "debut_s": 0.6, "fin_s": 1.4}]
    return {"charte": charte, "scenes": [scene], "mots": mots}


def rendre(composant, nom, params, da, charte, frame, browser):
    SORTIE_DIR.mkdir(parents=True, exist_ok=True)
    sortie = SORTIE_DIR / f"{composant}-{nom}.png"

    fd, chemin_props = tempfile.mkstemp(suffix=".json", prefix="apercu_")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            json.dump(props_pour(composant, params, da, charte), f, ensure_ascii=False)

        env = dict(os.environ)
        if browser:
            env["REMOTION_BROWSER_EXECUTABLE"] = browser
        cmd = ["npx", "remotion", "still", "src/index.ts", "Video", str(sortie),
               f"--props={chemin_props}", f"--frame={frame}"]
        resultat = subprocess.run(cmd, cwd=str(COMPOSANTS), env=env,
                                  capture_output=True, text=True)
    finally:
        os.path.exists(chemin_props) and os.remove(chemin_props)

    if resultat.returncode != 0:
        return None, (resultat.stderr or resultat.stdout or "").strip()[-500:]
    if not sortie.is_file() or sortie.stat().st_size == 0:
        return None, f"PNG absent ou vide : {sortie}"
    return sortie, None


def ecrire_catalogue(rendus, frame):
    """Catalogue lisible par A6 : chaque variante avec son image et ses params."""
    lignes = [
        "# Catalogue visuel des composants",
        "",
        "*Genere par `outils/generer_apercus.py` — ne pas editer a la main.*",
        "",
        "A quoi ressemble chaque composant, variante par variante. Le Designer",
        "(A6) choisit ici **en regardant**, pas en devinant a partir d'un nom.",
        "Les images passent par la composition de rendu reelle : c'est ce que la",
        "video montrera, tokens de charte compris.",
        "",
        f"Images prises a la frame {frame} (~{frame / 30:.1f} s), donc apres",
        "l'animation d'entree.",
        "",
        "Pour regenerer apres avoir cree ou modifie un composant :",
        "",
        "```bash",
        "python3 outils/generer_apercus.py",
        "```",
        "",
    ]
    composant_courant = None
    for composant, nom, params, _, chemin in rendus:
        if composant != composant_courant:
            lignes += [f"## {composant}", ""]
            composant_courant = composant
        rendu_params = ", ".join(f"`{c}` = `{v}`" for c, v in params.items()) or "*(aucun)*"
        lignes += [
            f"### {nom}",
            "",
            f"![{composant} — {nom}]({Path(chemin).name})",
            "",
            f"- Parametres : {rendu_params}",
            "",
        ]
    (SORTIE_DIR / "README.md").write_text("\n".join(lignes), encoding="utf-8")


def main():
    ap = argparse.ArgumentParser(description="Rend un apercu par composant et par variante (§8).")
    ap.add_argument("--charte", help="charte.json (defaut : celle de Root.tsx)")
    ap.add_argument("--composant", help="ne rendre que ce composant")
    ap.add_argument("--frame", type=int, default=FRAME_DEFAUT)
    ap.add_argument("--browser", help="Executable Chromium (REMOTION_BROWSER_EXECUTABLE)")
    ap.add_argument("--liste", action="store_true", help="liste les variantes sans rien rendre")
    a = ap.parse_args()

    declaration = charger_declaration()
    a_rendre = variantes(declaration, a.composant)
    if not a_rendre:
        sortir(2, message=f"Aucune variante a rendre{' pour ' + a.composant if a.composant else ''}.")

    if a.liste:
        sortir(0, variantes=[{"composant": c, "nom": n, "params": p} for c, n, p, _ in a_rendre])

    if not (COMPOSANTS / "node_modules").is_dir():
        sortir(4, message="composants/node_modules absent — lance 'npm install' dans composants/")

    charte = charte_par_defaut()
    if a.charte:
        chemin = Path(a.charte)
        if chemin.is_file():
            charte = {**charte, **json.loads(chemin.read_text(encoding="utf-8-sig"))}

    rendus, echecs = [], []
    for composant, nom, params, da in a_rendre:
        chemin, erreur = rendre(composant, nom, params, da, charte, a.frame, a.browser)
        if erreur:
            echecs.append({"composant": composant, "variante": nom, "erreur": erreur})
        else:
            rendus.append((composant, nom, params, da, str(chemin)))

    if rendus:
        ecrire_catalogue(rendus, a.frame)

    if echecs and not rendus:
        sortir(6, message="Aucun apercu n'a pu etre rendu.", echecs=echecs)

    sortir(0, rendus=[{"composant": c, "variante": n, "fichier": Path(f).name}
                      for c, n, _, _, f in rendus],
           catalogue=str(SORTIE_DIR / "README.md"),
           echecs=echecs)


if __name__ == "__main__":
    main()
