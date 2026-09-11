"""
Signalement du cycle hebdomadaire (§6.1, A1 point 6). Les taches
hebdomadaires (A2 sujets_proposes, A3, H1) sont des skills Claude Code,
pas du code Python : l'Orchestrateur ne les execute pas, il se contente de
verifier si les fichiers attendus de la semaine ISO en cours existent deja.
"""

import os
from datetime import datetime, timezone


def semaine_iso(maintenant=None):
    maintenant = maintenant or datetime.now(timezone.utc)
    annee, semaine, _ = maintenant.isocalendar()
    return f"{annee}-S{semaine:02d}"


def taches_hebdo_manquantes(root, maintenant=None):
    semaine = semaine_iso(maintenant)
    attendues = [
        ("A2 (sujets_proposes, voie tampon)", os.path.join("02_Veille_hebdo", f"{semaine}_sujets_proposes.md")),
        ("A3 (analyseur_chaines)", os.path.join("02_Veille_hebdo", f"{semaine}_analyse_concurrentielle.md")),
        ("H1 (amelioration_continue)", os.path.join("03_Amelioration", f"rapport_hebdo_{semaine}.md")),
    ]
    return semaine, [
        {"tache": tache, "fichier_attendu": relatif}
        for tache, relatif in attendues
        if not os.path.isfile(os.path.join(root, relatif))
    ]
