#!/usr/bin/env python3
"""
lancer_orchestrateur.py — lance l'Orchestrateur (A1) depuis cron.

Pourquoi un lanceur, plutot que `python -m orchestrateur.main` directement
dans la crontab. Cron n'est pas un shell de connexion, et chacune de ses
particularites casse quelque chose ici :

- **pas de repertoire courant utile** : `python -m orchestrateur.main` exige
  d'etre a la racine du depot. Ce script se trouve lui-meme et repare
  `sys.path`, donc il se lance depuis n'importe ou par son chemin absolu ;
- **la racine est sur le Drive**. Si le Drive n'est pas monte, le point de
  montage existe souvent quand meme, vide. `run_once` appellerait alors
  `acquerir_verrou`, qui fait un `makedirs` : on fabriquerait un faux
  `/ChaineYouTube` sur le disque local, qui masquerait le vrai au
  remontage. Le garde-fou passe donc **avant toute ecriture** ;
- **un verrou actif n'est pas une erreur** : c'est une execution qui en
  chevauche une autre, le cas nominal d'un cron serre. `main.py` sort 1,
  ce qui ferait envoyer un mail d'erreur a chaque passage jusqu'a ce que
  Franco coupe le cron. Ici, c'est une sortie 0 et une ligne de journal ;
- **la sortie part en mail que personne ne lit** : chaque execution ecrit
  une ligne dans `01_Orchestrateur/journal_cron.log`, a cote du reste de
  l'etat. Seules les vraies erreurs vont sur stderr, donc seules elles
  declenchent un mail — c'est exactement quand on le veut.

Codes de sortie : 0 execution faite ou ignoree, 1 echec de l'execution,
2 racine inutilisable (rien n'a ete ecrit).

Usage :
  python3 outils/lancer_orchestrateur.py --root /chemin/ChaineYouTube
  python3 outils/lancer_orchestrateur.py --root /chemin/ChaineYouTube --verifier
"""
import argparse
import shlex
import sys
import time
import traceback
from datetime import datetime, timezone
from pathlib import Path

RACINE_DEPOT = Path(__file__).resolve().parent.parent
if str(RACINE_DEPOT) not in sys.path:
    sys.path.insert(0, str(RACINE_DEPOT))

JOURNAL = Path("01_Orchestrateur") / "journal_cron.log"
# ~3 semaines a un passage tous les quarts d'heure. Le journal vit sur le
# Drive : il se relit a la main, il ne se garde pas indefiniment.
MAX_LIGNES_JOURNAL = 2000
CADENCE_SUGGEREE = "*/15 * * * *"


def _horodatage():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def verifier_racine(root):
    """(ok, message). Aucune ecriture : c'est tout l'interet de la fonction."""
    racine = Path(root)
    if not racine.is_dir():
        return False, f"racine introuvable : {racine} (Drive non monte ?)"
    config = racine / "01_Orchestrateur" / "config.json"
    if not config.is_file():
        return False, (f"racine non initialisee : {config} absent. "
                       f"Drive non monte, ou `python3 -m orchestrateur.init_structure "
                       f"--root {racine}` jamais lance.")
    return True, "racine utilisable"


def journaliser(root, ligne):
    """Ajoute une ligne au journal, en gardant le fichier borne."""
    chemin = Path(root) / JOURNAL
    try:
        chemin.parent.mkdir(parents=True, exist_ok=True)
        lignes = chemin.read_text(encoding="utf-8").splitlines() if chemin.is_file() else []
        lignes.append(ligne)
        if len(lignes) > MAX_LIGNES_JOURNAL:
            lignes = lignes[-MAX_LIGNES_JOURNAL:]
        chemin.write_text("\n".join(lignes) + "\n", encoding="utf-8")
    except OSError as e:
        # Un journal qu'on ne peut pas ecrire ne doit pas faire echouer une
        # execution par ailleurs valide.
        print(f"journal illisible ({e})", file=sys.stderr)


def executer(root):
    """(code de sortie, ligne de journal). Les garde-fous sont deja passes."""
    from orchestrateur.lock import VerrouActifError
    from orchestrateur.main import run_once
    from orchestrateur.state_store import list_video_dirs

    depart = time.monotonic()
    try:
        run_once(root)
    except VerrouActifError as e:
        return 0, f"{_horodatage()}  ignore   {time.monotonic() - depart:5.1f}s  {e}"
    except Exception:
        detail = traceback.format_exc()
        print(detail, file=sys.stderr)
        derniere = detail.strip().splitlines()[-1]
        return 1, f"{_horodatage()}  ERREUR   {time.monotonic() - depart:5.1f}s  {derniere}"

    nb = len(list_video_dirs(root))
    return 0, f"{_horodatage()}  ok       {time.monotonic() - depart:5.1f}s  {nb} video(s)"


def rapport_verification(root):
    """Diagnostic + la ligne de crontab exacte, chemins absolus resolus."""
    ok, message = verifier_racine(root)
    script = Path(__file__).resolve()
    python = Path(sys.executable).resolve()
    # Les chemins Drive contiennent presque toujours une espace
    # (« Mon Drive ») : sans guillemets, la ligne de crontab est cassee et
    # l'erreur n'apparait que dans un mail que personne ne lit.
    commande = " ".join(shlex.quote(str(x)) for x in (python, script)) \
        + " --root " + shlex.quote(str(Path(root).resolve()))

    lignes = [
        f"Python      : {python}",
        f"Lanceur     : {script}",
        f"Racine      : {Path(root).resolve()}",
        f"Verdict     : {'OK' if ok else 'BLOQUANT'} — {message}",
        "",
        "Ligne de crontab (`crontab -e`) :",
        f"  {CADENCE_SUGGEREE} {commande}",
        "",
        "Valeur a mettre dans 01_Orchestrateur/config.json > orchestrateur_cmd",
        "(c'est ce que `new-short` affiche a Franco apres avoir cree une video) :",
        f"  {commande}",
    ]
    return ok, "\n".join(lignes)


def main(argv=None):
    ap = argparse.ArgumentParser(description="Lance l'Orchestrateur depuis cron (§12).")
    ap.add_argument("--root", required=True, help="Racine du dossier ChaineYouTube.")
    ap.add_argument("--verifier", action="store_true",
                    help="Diagnostique et affiche la ligne de crontab, sans rien executer.")
    a = ap.parse_args(argv)

    if a.verifier:
        ok, rapport = rapport_verification(a.root)
        print(rapport)
        return 0 if ok else 2

    ok, message = verifier_racine(a.root)
    if not ok:
        # Seul cas ou on veut le mail de cron : personne ne regardera un
        # journal qui se trouve sur une racine qu'on ne sait pas atteindre.
        print(f"Execution annulee : {message}", file=sys.stderr)
        return 2

    code, ligne = executer(a.root)
    journaliser(a.root, ligne)
    return code


if __name__ == "__main__":
    sys.exit(main())
