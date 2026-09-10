import json
import os

from .constants import MAX_TENTATIVES_DEFAUT

DEFAUTS = {
    "orchestrateur_cmd": None,
    "cible_tampon": 4,
    "seuils": {"max_tentatives": MAX_TENTATIVES_DEFAUT},
}


def charger_config(root):
    path = os.path.join(root, "01_Orchestrateur", "config.json")
    if not os.path.isfile(path):
        return dict(DEFAUTS)
    with open(path, "r", encoding="utf-8") as f:
        config = json.load(f)
    fusion = dict(DEFAUTS)
    fusion.update(config)
    fusion["seuils"] = {**DEFAUTS["seuils"], **config.get("seuils", {})}
    return fusion
