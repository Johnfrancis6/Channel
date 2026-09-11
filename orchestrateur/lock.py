import json
import os
import sys
from datetime import datetime, timedelta, timezone

from .state_store import now_iso

DUREE_VERROU_DEFAUT_SECONDES = 1800


class VerrouActifError(Exception):
    pass


def _chemin_verrou(root):
    return os.path.join(root, "01_Orchestrateur", "verrou.json")


def _lire_expiration(chemin):
    """(datetime, contenu) du verrou, ou (None, {}) s'il est illisible."""
    try:
        with open(chemin, "r", encoding="utf-8") as f:
            verrou = json.load(f)
        expire_le = datetime.strptime(verrou["expire_le"], "%Y-%m-%dT%H:%M:%SZ")
        return expire_le.replace(tzinfo=timezone.utc), verrou
    except (OSError, ValueError, TypeError, KeyError, json.JSONDecodeError):
        return None, {}


def acquerir_verrou(root, duree_secondes=DUREE_VERROU_DEFAUT_SECONDES):
    chemin = _chemin_verrou(root)
    os.makedirs(os.path.dirname(chemin), exist_ok=True)

    if os.path.exists(chemin):
        expire_le, verrou = _lire_expiration(chemin)
        if expire_le is None:
            # Verrou illisible (ecriture interrompue, synchro Drive a moitie
            # faite, edition a la main) : on le considere perime plutot que de
            # faire planter chaque execution suivante sur le meme fichier.
            # Un verrou qu'on ne sait pas dater ne protege de toute facon rien.
            print(f"Verrou illisible, ignore et remplace : {chemin}", file=sys.stderr)
        elif datetime.now(timezone.utc) < expire_le:
            raise VerrouActifError(
                f"Verrou actif jusqu'a {verrou.get('expire_le')} (pid {verrou.get('pid')})")

    expire_le = datetime.now(timezone.utc) + timedelta(seconds=duree_secondes)
    with open(chemin, "w", encoding="utf-8") as f:
        json.dump({
            "acquis_le": now_iso(),
            "expire_le": expire_le.strftime("%Y-%m-%dT%H:%M:%SZ"),
            "pid": os.getpid(),
        }, f, ensure_ascii=False, indent=2)


def liberer_verrou(root):
    chemin = _chemin_verrou(root)
    if os.path.exists(chemin):
        os.remove(chemin)
