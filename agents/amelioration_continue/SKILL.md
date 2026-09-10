---
name: amelioration-continue
description: Agent H1 du pipeline chaine YouTube — rapport hebdomadaire d'amelioration continue (§4.3, §6.1). Utilise ce skill quand Franco dit "lance l'amelioration continue", "fais le bilan de la semaine", ou quand le cycle hebdomadaire de l'Orchestrateur (dimanche) l'indique.
---

# amelioration-continue (H1) — bilan hebdomadaire

## Ce que fait cet agent, et ce qu'il ne fait pas

Il produit `03_Amelioration/rapport_hebdo_{AAAA-Sxx}.md`. Ce n'est pas un
agent par-video (pas de `state.json` touche, pas de script `etape.py`).
**Aucune recommandation n'est appliquee automatiquement** : chaque
recommandation attend la validation de Franco avant d'etre mise en oeuvre
(§4.3).

## Etape 1 — Rassembler les inputs de la semaine

```bash
python3 <chemin-du-skill>/scripts/rassembler_inputs.py --root <racine> --jours 7
```

Ce script ne fait aucune analyse : il liste seulement les fichiers
modifies dans les 7 derniers jours (rapports de checkpoint, metriques du
Filtre TTS, rapports audio, exports `analytics/*.csv`). Lis-les tous.

Ajoute a la main :
- les notes que Franco t'a donnees directement dans la conversation ;
- les **performances YouTube** (retention, taux de swipe, vues) : au
  demarrage via l'export CSV manuel deja liste ci-dessus, plus tard via
  l'API YouTube Analytics (§4.3 — a implementer quand l'API sera prete).

## Etape 2 — Analyse ouverte

Contrairement aux autres agents, il n'y a pas de format de sortie
mecanique a suivre point par point : identifie toi-meme les points
faibles du workflow a partir de ce que tu lis. Cherche des patterns, pas
des incidents isoles :
- Le Filtre TTS echoue-t-il souvent sur le meme type de phrase ?
- Les checkpoints sont-ils souvent refuses pour la meme raison ?
- Le controle qualite audio signale-t-il des mots mal prononces qui
  devraient entrer au lexique ?
- Les videos avec le plus de retention/swipe ont-elles un point commun
  (hook, pilier, duree) ?

## Etape 3 — Ecrire le rapport

`03_Amelioration/rapport_hebdo_{AAAA-Sxx}.md` :

```markdown
# Rapport hebdomadaire — {AAAA-Sxx}

## Ce qui a bien fonctionne
...

## Points faibles identifies
...

## Recommandations (a valider par Franco)
1. Ajustement du prompt de A4/A5 : ...
2. Ajustement des seuils de calibrage (§7.3) : ...
3. Composant a refondre : ...
```

Chaque recommandation doit etre concrete et actionnable (quel fichier
modifier, quelle valeur changer), pas une observation vague.

## Etape 4 — Ne rien appliquer seul

Presente les recommandations a Franco et attends sa decision avant de
modifier quoi que ce soit (prompts d'agents dans `agents/*/SKILL.md`,
seuils dans `01_Orchestrateur/config.json` ou `00_Profil/conventions.md`,
composants dans `composants/`). Une fois validees, les modifications se
font comme n'importe quelle autre modification de code : elles doivent
rester tracables (§9.2 : prompts versionnes).

## Fichiers

- Lus : tout ce que liste `rassembler_inputs.py`, plus les notes de
  Franco
- Ecrits : `03_Amelioration/rapport_hebdo_{AAAA-Sxx}.md` uniquement (les
  changements eventuels sur d'autres fichiers ne se font qu'apres
  validation explicite de Franco, etape 4)
