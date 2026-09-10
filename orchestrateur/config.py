import json
import os

from .constants import MAX_TENTATIVES_DEFAUT

# Cles a plat, alignees sur ce que lisent skills/new-short et skills/short-state
# (voir new_short.py: config.get("orchestrateur_cmd") ; short_state.py:
# config.get("cible_tampon", 4), config.get("seuil_blocage_heures", 2),
# config.get("seuil_orchestrateur_heures", 6)). "max_tentatives" est propre a
# l'Orchestrateur, ajoute au meme niveau.
DEFAUTS = {
    "orchestrateur_cmd": None,
    "cible_tampon": 4,
    "seuil_blocage_heures": 2,
    "seuil_orchestrateur_heures": 6,
    "max_tentatives": MAX_TENTATIVES_DEFAUT,
    # "factice" (defaut lib, utilise par les tests) : l'Orchestrateur execute
    # lui-meme les agents factices de agents/factices/.
    # "reel" : les agents sont des skills Claude Code lances a la main ou en
    # headless ; l'Orchestrateur se contente de signaler au tableau de bord
    # quelle etape est prete, et gere l'escalade en alerte / la boucle A4<->A5.
    "mode_agents": "factice",
}


def charger_config(root):
    path = os.path.join(root, "01_Orchestrateur", "config.json")
    if not os.path.isfile(path):
        return dict(DEFAUTS)
    with open(path, "r", encoding="utf-8") as f:
        config = json.load(f)
    return {**DEFAUTS, **config}
