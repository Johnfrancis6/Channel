import json
import os
from datetime import datetime, timedelta, timezone

from .state_store import now_iso

DUREE_VERROU_DEFAUT_SECONDES = 1800


class VerrouActifError(Exception):
    pass


def _chemin_verrou(root):
    return os.path.join(root, "01_Orchestrateur", "verrou.json")


def acquerir_verrou(root, duree_secondes=DUREE_VERROU_DEFAUT_SECONDES):
    chemin = _chemin_verrou(root)
    os.makedirs(os.path.dirname(chemin), exist_ok=True)

    if os.path.exists(chemin):
        with open(chemin, "r", encoding="utf-8-sig") as f:
            verrou = json.load(f)
        expire_le = datetime.strptime(verrou["expire_le"], "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
        if datetime.now(timezone.utc) < expire_le:
            raise VerrouActifError(f"Verrou actif jusqu'a {verrou['expire_le']} (pid {verrou.get('pid')})")

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
