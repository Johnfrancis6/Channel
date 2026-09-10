"""
Cree la structure du dossier /ChaineYouTube sur le Drive (§9.1), dont
01_Orchestrateur/config.json et 02_Veille_hebdo/backlog_sujets.json (§13,
etape 1 - Fondations). Idempotent : n'ecrase jamais un fichier existant.

Usage : python -m orchestrateur.init_structure --root /chemin/vers/ChaineYouTube
"""

import argparse
import json
import os
import sys

from .config import DEFAUTS as CONFIG_DEFAUTS
from .profil_defaults import (
    CHARTE_JSON,
    CHARTE_MD,
    CONVENTIONS_MD,
    LEXIQUE_PRONONCIATION_MD,
    PROFIL_CHAINE_MD,
)

DOSSIERS = [
    "00_Profil",
    "00_Profil/charte_visuelle",
    "00_Profil/voix",
    "01_Orchestrateur",
    "02_Veille_hebdo",
    "03_Amelioration",
    "03_Amelioration/analytics",
    "04_Architecture_technique",
    "videos",
]


def _ecrire_si_absent(path, contenu):
    if os.path.exists(path):
        return False
    with open(path, "w", encoding="utf-8") as f:
        f.write(contenu)
    return True


def initialiser(root):
    resultat = {"dossiers_crees": [], "fichiers_crees": [], "deja_present": []}

    for relatif in DOSSIERS:
        chemin = os.path.join(root, relatif)
        if os.path.isdir(chemin):
            resultat["deja_present"].append(relatif)
        else:
            os.makedirs(chemin, exist_ok=True)
            resultat["dossiers_crees"].append(relatif)

    config_path = os.path.join(root, "01_Orchestrateur", "config.json")
    if _ecrire_si_absent(config_path, json.dumps(CONFIG_DEFAUTS, ensure_ascii=False, indent=2)):
        resultat["fichiers_crees"].append("01_Orchestrateur/config.json")
    else:
        resultat["deja_present"].append("01_Orchestrateur/config.json")

    backlog_path = os.path.join(root, "02_Veille_hebdo", "backlog_sujets.json")
    if _ecrire_si_absent(backlog_path, json.dumps({"sujets": []}, ensure_ascii=False, indent=2)):
        resultat["fichiers_crees"].append("02_Veille_hebdo/backlog_sujets.json")
    else:
        resultat["deja_present"].append("02_Veille_hebdo/backlog_sujets.json")

    log_path = os.path.join(root, "01_Orchestrateur", "log_erreurs.md")
    if _ecrire_si_absent(log_path, "# Log d'erreurs\n"):
        resultat["fichiers_crees"].append("01_Orchestrateur/log_erreurs.md")
    else:
        resultat["deja_present"].append("01_Orchestrateur/log_erreurs.md")

    profil = {
        "00_Profil/profil_chaine.md": PROFIL_CHAINE_MD,
        "00_Profil/conventions.md": CONVENTIONS_MD,
        "00_Profil/lexique_prononciation.md": LEXIQUE_PRONONCIATION_MD,
        "00_Profil/charte_visuelle/charte.md": CHARTE_MD,
        "00_Profil/charte_visuelle/charte.json": json.dumps(CHARTE_JSON, ensure_ascii=False, indent=2),
    }
    for relatif, contenu in profil.items():
        chemin = os.path.join(root, *relatif.split("/"))
        if _ecrire_si_absent(chemin, contenu):
            resultat["fichiers_crees"].append(relatif)
        else:
            resultat["deja_present"].append(relatif)

    return resultat


def main(argv=None):
    parser = argparse.ArgumentParser(description="Initialise la structure du dossier ChaineYouTube.")
    parser.add_argument("--root", required=True, help="Racine du dossier ChaineYouTube (cree si absente).")
    args = parser.parse_args(argv)

    os.makedirs(args.root, exist_ok=True)
    resultat = initialiser(args.root)
    print(json.dumps(resultat, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
