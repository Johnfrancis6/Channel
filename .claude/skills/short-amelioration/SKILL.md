---
name: short-amelioration
description: Agent H1 du pipeline chaine YouTube — rapport hebdomadaire d'amelioration continue (§4.3, §6.1). Utilise ce skill quand Franco dit "lance l'amelioration continue", "fais le bilan de la semaine", ou quand le cycle hebdomadaire de l'Orchestrateur (dimanche) l'indique.
---

# amelioration-continue (H1) — bilan hebdomadaire

## Ce que fait cet agent, et ce qu'il ne fait pas

Il produit `03_Amelioration/rapport_hebdo_{AAAA-Sxx}.md`. Ce n'est pas un
agent par-video (pas de `state.json` touche, pas de script `etape.py`).
**Aucune recommandation n'est appliquee automatiquement** : chaque
recommandation attend la validation de Franco avant d'etre mise en oeuvre
(§4.3).

## Etape 1 — Rassembler et mesurer

```bash
python3 <chemin-du-skill>/scripts/rassembler_inputs.py --root <racine> --jours 7
```

Le script rend deux choses de nature differente :

**`indicateurs`** — ce qui se compte dans les `state.json`, agrege sur les
videos actives de la periode. C'est le socle factuel du rapport :

| Cle | Ce qu'elle repond |
|-----|-------------------|
| `tentatives_par_etape` | quelle etape coute cher (total, moyenne, max) |
| `alertes` | ou le pipeline a cale au point d'appeler Franco |
| `refus_checkpoints` | ce que Franco a rejete, avec son commentaire |
| `boucles_redaction_filtre` | combien de tours A4<->A5 par video |
| `durees_production_h` | de la creation de la video au CP3 |

Le script **compte, il ne juge pas** — comme `metriques.py` pour A5. Un
`max` a 8 sur `E4_audio` est un fait ; dire que le probleme vient de la
voix de reference est ton travail, pas le sien.

Deux points de lecture a connaitre :
- les evenements sont lus **dans l'etape et dans l'historique**. Un refus
  repris remet le checkpoint a `a_venir` et une alerte traitee disparait
  de l'etape : sans l'historique, la semaine ou le probleme a ete corrige
  serait aussi celle ou il devient invisible ;
- une video figee depuis des semaines apparait dans `videos_actives` avec
  son `jours_sans_activite`, mais ses compteurs **n'entrent pas** dans les
  indicateurs de la semaine. Une video immobile est un signal, pas une
  statistique de production.

**Les listes de fichiers** — a lire, elles, integralement :
`checkpoints` (y compris les rapports archives dans `refuses/`, la trace
la plus directe de ce que Franco a rejete), `metriques_filtre`,
`rapports_audio`, `analytics_csv`, `corpus_structures`,
`recommandations_passees` / `recommandations_en_attente`.

Ajoute a la main les notes que Franco t'a donnees dans la conversation, et
les performances YouTube (retention, taux de swipe, vues) : au demarrage
via l'export CSV manuel deja liste, plus tard via l'API YouTube Analytics
(§4.3 — a implementer quand l'API sera prete).

## Etape 2 — Analyse ouverte

Contrairement aux autres agents, il n'y a pas de format de sortie
mecanique a suivre point par point : identifie toi-meme les points
faibles du workflow a partir de ce que tu lis. Cherche des motifs, pas
des incidents isoles — un chiffre qui se repete sur trois videos vaut
mieux qu'un pic sur une seule.

Pistes de depart :
- une etape concentre-t-elle les tentatives (`tentatives_par_etape`) ?
- les checkpoints sont-ils refuses pour la meme raison
  (`refus_checkpoints`, et les rapports archives) ?
- le Filtre TTS echoue-t-il sur le meme type de phrase (rapports
  `03_rapport_metriques.md`) ?
- que dit le diff reference/transcrit des runs audio en echec — phrases
  trop longues, sigles ? Le rapport audio ne contient un diff **que si le
  WER a echoue** : ne cherche pas de liste de mots mal prononces, elle
  n'existe pas ; c'est du diff qu'un candidat au lexique se deduit ;
- les videos avec le plus de retention/swipe ont-elles un point commun
  (hook, pilier, format, duree) ?

### Croiser avec le corpus (§4.3, A3)

`02_Veille_hebdo/corpus_structures.jsonl` accumule la **structure mesuree**
des videos concurrentes : duree de hook, nombre d'idees, mots par idee,
presence de CTA. Mesure les scripts de nos propres videos de la semaine
avec le meme outil, pour comparer ce qui est comparable :

```bash
python3 <chemin-du-skill>/scripts/analyser_transcription.py --mesurer \
  --segmentation <segmentation.json>
```

Les ecarts stables (nos hooks durent le double, nos idees coutent
30 mots de plus) sont exactement le genre de motif qui justifie une
recommandation. Un ecart vu sur une semaine ne justifie rien : le corpus
est fait pour s'accumuler.

## Etape 3 — Ecrire le rapport

`03_Amelioration/rapport_hebdo_{AAAA-Sxx}.md` :

```markdown
# Rapport hebdomadaire — {AAAA-Sxx}

## Chiffres de la semaine
(les indicateurs, tels quels — c'est la base que le lecteur peut verifier)

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
modifier, quelle valeur changer), pas une observation vague. Adosse-la a
un chiffre ou a une citation de rapport : une recommandation sans preuve
ne se tranche pas.

## Etape 4 — Tracer les recommandations

Ajoute une ligne par recommandation a `03_Amelioration/recommandations.jsonl`
(**append-only**, une ligne JSON par recommandation) :

```json
{"semaine": "2026-S37", "texte": "Baisser MOTS_PAR_IDEE_DEFAUT a 40", "cible": "agents/short-filtre-tts/scripts/metriques.py", "preuve": "3 scripts sur 4 au-dessus du budget", "statut": "proposee"}
```

`statut` vaut `proposee`, puis `acceptee`, `refusee` ou `appliquee` une
fois que Franco a tranche — mets la ligne a jour en **ajoutant** une
nouvelle ligne portant le meme `texte` et le nouveau statut, sans reecrire
l'historique.

Le script te rend `recommandations_passees` et
`recommandations_en_attente` : **lis-les avant d'ecrire le rapport.** Sans
ca, tu reproposes chaque semaine ce que Franco a deja refuse la semaine
precedente, et le bilan perd sa credibilite. Si une recommandation refusee
te parait toujours juste, ne la repose pas a l'identique : apporte la
preuve nouvelle qui manquait, ou n'en parle pas.

## Etape 5 — Ne rien appliquer seul

Presente les recommandations a Franco et attends sa decision avant de
modifier quoi que ce soit (prompts d'agents dans `agents/*/SKILL.md`,
seuils dans `01_Orchestrateur/config.json` ou `00_Profil/conventions.md`,
composants dans `composants/`). Une fois validees, les modifications se
font comme n'importe quelle autre modification de code : elles doivent
rester tracables (§9.2 : prompts versionnes).

## Fichiers

- Lus : tout ce que liste `rassembler_inputs.py`, plus les notes de
  Franco
- Ecrits : `03_Amelioration/rapport_hebdo_{AAAA-Sxx}.md` et
  `03_Amelioration/recommandations.jsonl` (en ajout seul). Les changements
  eventuels sur d'autres fichiers ne se font qu'apres validation explicite
  de Franco (etape 5).
