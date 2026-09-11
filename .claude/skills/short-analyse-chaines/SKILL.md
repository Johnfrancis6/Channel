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
agent de choisir des concurrents (§4.3).

**Si Franco te donne des URLs ou des `@handles`** plutot que des
identifiants, resous-les d'abord — la sortie est directement collable dans
`chaines_concurrentes.json` :

```bash
python3 <chemin-du-skill>/scripts/stats_youtube.py \
  --chaines "https://youtube.com/@unechaine" "@uneautre" --resoudre
```

Une URL YouTube moderne n'expose plus l'identifiant `UC` : le script
accepte donc les trois formes (identifiant, handle, URL).

## Etape 2 — Statistiques (voie stable)

Necessite `YOUTUBE_API_KEY` dans l'environnement (projet Google Cloud
audite, §11 et §12).

```bash
python3 <chemin-du-skill>/scripts/stats_youtube.py --chaines UCxxxx UCyyyy > /tmp/stats.json
```

Si une chaine echoue (reference invalide, quota API, erreur reseau), elle
apparait avec un champ `erreur` dans la sortie : continue avec les autres,
ne t'arrete pas. Le script attrape les erreurs HTTP et reseau par chaine
precisement pour ca.

## Etape 3 — Transcriptions et segmentation (partie fragile, best-effort)

Pour chaque video recente de `/tmp/stats.json`, essaie de recuperer la
transcription (outils web, ou sous-titres YouTube s'ils sont accessibles).
Si ca echoue pour une chaine, passe a la suivante — **n'interromps jamais**
l'etape 2 a cause de l'etape 3.

### Segmenter, une video a la fois

**Ne resume pas en prose.** Une note en texte libre indexee par chaine —
ce que faisait cet agent avant — ne se mesure pas, ne se compare pas et ne
s'accumule pas. Et ecraser cinq videos dans une phrase detruit
l'information avant meme de l'ecrire : le hook, le CTA et le rythme sont
des proprietes d'**une** video.

Pour chaque video, en trois temps :

```bash
# 1. Le squelette, phrases numerotees
python3 <chemin-du-skill>/outils/analyser_transcription.py --gabarit \
  --transcription /tmp/transcription.txt --duree 47 > /tmp/segmentation.json
```

2. **Remplis le `role` de chaque segment.** C'est ton travail de jugement :
   reconnaitre un hook ou un CTA demande de comprendre le propos, un script
   ne peut pas le faire. Vocabulaire **ferme** — `hook`, `promesse`,
   `contexte`, `idee`, `exemple`, `transition`, `cta`, `sponsoring`. N'en
   invente pas : un role hors liste rend la ligne incomparable aux autres et
   on retombe sur de la prose. Renseigne aussi `chaine` (le `channel_id`),
   `titre`, `vues` et `duree_s`.

```bash
# 3. Mesurer et ajouter au corpus
python3 <chemin-du-skill>/outils/analyser_transcription.py --mesurer \
  --segmentation /tmp/segmentation.json \
  --corpus <racine>/02_Veille_hebdo/corpus_structures.jsonl
```

Le script refuse une segmentation incomplete (code 3) et te dit quoi
corriger. Le corpus est **append-only** : c'est le seul actif du systeme
qui prend de la valeur avec le temps, on n'y reecrit jamais une ligne.

## Etape 4 — Generer le rapport

```bash
python3 <chemin-du-skill>/scripts/generer_rapport.py --stats /tmp/stats.json \
  --semaine 2026-S37 \
  --analyses <racine>/02_Veille_hebdo/corpus_structures.jsonl \
  --sortie <racine>/02_Veille_hebdo/2026-S37_analyse_concurrentielle.md
```

`--analyses` et `--notes` sont optionnels : sans eux le rapport ne porte
que les statistiques, ce qui reste un rapport valide (§4.3). `--notes`
garde sa place pour ce qui ne se mesure pas — un ton, un parti pris
editorial.

**Une semaine de mesures ne dit rien.** Les medianes du rapport ne
deviennent fiables qu'en s'accumulant, et c'est le corpus qui porte cette
accumulation, pas le rapport hebdomadaire.

## Etape 5 — Relancer l'Orchestrateur

Si `orchestrateur_cmd` est renseigne, execute-le pour que le Chercheur
(A2) puisse s'appuyer sur ce rapport pour ses propositions de sujets.

## Fichiers

- Lus : `00_Profil/chaines_concurrentes.json`
- Ecrits : `02_Veille_hebdo/{AAAA-Sxx}_analyse_concurrentielle.md` et
  `02_Veille_hebdo/corpus_structures.jsonl` (en ajout seul) — aucun
  `state.json`
