---
name: short-analyse-chaines
description: Agent A3 du pipeline chaine YouTube — analyse hebdomadaire des chaines concurrentes (§4.3, §6.1). Utilise ce skill quand Franco dit "lance l'analyse concurrentielle", "analyse les chaines cette semaine", ou quand le cycle hebdomadaire de l'Orchestrateur (dimanche, §6.1) l'indique.
---

# analyseur-chaines (A3) — analyse concurrentielle hebdomadaire

## Ce que fait cet agent, et ce qu'il ne fait pas

Il produit `02_Veille_hebdo/{AAAA-Sxx}_analyse_concurrentielle.md`, lu
ensuite par le Chercheur (A2) et le Redacteur (A4). Ce n'est **pas** un
agent par-video : il ne touche a aucun `state.json` et n'utilise donc pas
le script `etape.py` des autres agents.

Deux parties, de fiabilite tres differente (§4.3) :
1. **Statistiques** (API YouTube Data) : la voie stable.
2. **Transcriptions** (hooks, CTA, structure) : la partie fragile — un
   echec de transcription sur une chaine **ne doit jamais bloquer** les
   statistiques des autres, ni le rapport final.

## Etape 1 — Lire la liste de chaines

`00_Profil/chaines_concurrentes.json` : `[{"channel_id": "UCxxxx", "nom": "..."}]`.
Si le fichier est vide, dis-le a Franco et arrete-toi : ce n'est pas a cet
agent de choisir des concurrents.

## Etape 2 — Statistiques (voie stable)

Necessite `YOUTUBE_API_KEY` dans l'environnement (projet Google Cloud
audite, §11 et §12).

```bash
python3 <chemin-du-skill>/scripts/stats_youtube.py --chaines UCxxxx UCyyyy > /tmp/stats.json
```

Si une chaine echoue (id invalide, quota API), elle apparait avec un champ
`erreur` dans la sortie : continue avec les autres, ne t'arrete pas.

## Etape 3 — Transcriptions (partie fragile, best-effort)

Pour chaque video recente listee dans `/tmp/stats.json`, essaie de
recuperer et lire la transcription (outils de recherche/lecture web ou
sous-titres YouTube s'ils sont accessibles). Note pour chaque chaine :
hook d'ouverture, structure du script, type de CTA. Si ca echoue pour une
chaine, ecris simplement "transcriptions indisponibles" pour elle et
continue — **n'interromps jamais** l'etape 2 a cause de l'etape 3.

Rassemble ces notes dans un objet `{channel_id: "note texte"}` et
sauvegarde-le en JSON (ex. `/tmp/notes.json`).

## Etape 4 — Generer le rapport

```bash
python3 <chemin-du-skill>/scripts/generer_rapport.py --stats /tmp/stats.json \
  --semaine 2026-S37 --notes /tmp/notes.json \
  --sortie <racine>/02_Veille_hebdo/2026-S37_analyse_concurrentielle.md
```

`--notes` est optionnel : sans lui, le rapport indique "transcriptions
indisponibles" pour toutes les chaines, ce qui reste un rapport valide
(§4.3 : l'echec de transcription ne bloque pas l'analyse des stats).

## Etape 5 — Relancer l'Orchestrateur

Si `orchestrateur_cmd` est renseigne, execute-le pour que le Chercheur
(A2) puisse s'appuyer sur ce rapport pour ses propositions de sujets.

## Fichiers

- Lus : `00_Profil/chaines_concurrentes.json`
- Ecrits : `02_Veille_hebdo/{AAAA-Sxx}_analyse_concurrentielle.md`
  uniquement (aucun `state.json`)
