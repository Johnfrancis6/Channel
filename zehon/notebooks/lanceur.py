"""Exécute un notebook Zehon du dépôt depuis le lanceur rangé dans Drive.

La copie Drive d'un notebook (Zehon/montage_zehon.ipynb, Zehon/voix_zehon.ipynb) n'est qu'un
lanceur : le formulaire de réglages, puis quelques lignes qui clonent le dépôt et appellent
executer(). Le vrai notebook vit ici, dans zehon/notebooks/ : une correction poussée sert au
lancement suivant, sans jamais recopier quoi que ce soit dans Drive.

executer() lance les cellules de code du notebook l'une après l'autre, dans l'espace de noms
du lanceur. La cellule marquée « reglages » (métadonnées, tags) pose les valeurs par défaut ;
les réglages du lanceur passent par-dessus. Un réglage ajouté plus tard au notebook garde donc
sa valeur par défaut, même dans un vieux lanceur. La première cellule qui échoue arrête tout.
"""
import json
from pathlib import Path

ICI = Path(__file__).resolve().parent


def cellules(notebook):
    """[(indice, source, est_reglages)] des cellules de code du notebook."""
    nb = json.loads((ICI / notebook).read_text(encoding="utf-8"))
    return [(i, "".join(c["source"]), "reglages" in c.get("metadata", {}).get("tags", []))
            for i, c in enumerate(nb["cells"]) if c["cell_type"] == "code"]


def executer(notebook, reglages, espace=None):
    """Exécute le notebook ; reglages = le formulaire du lanceur, espace = ses globals()."""
    espace = {} if espace is None else espace
    espace["DEPOT_PRET"] = True  # le lanceur a déjà cloné le dépôt : le notebook ne le reclone pas
    try:
        transformer = get_ipython().transform_cell  # noqa: F821 (Colab : « !commande », « %magie »)
    except NameError:
        transformer = None
    for i, source, est_reglages in cellules(notebook):
        if transformer:
            source = transformer(source)
        exec(compile(source, f"<{notebook}, cellule {i}>", "exec"), espace)
        if est_reglages:
            espace.update(reglages)
    return espace
