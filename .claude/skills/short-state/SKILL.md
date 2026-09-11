---
name: short-state
description: Donne à Franco l'état actuel de la production de sa chaîne YouTube IA. Indique ce qu'il doit faire maintenant (checkpoints à valider, run Colab à lancer, alertes), où en est chaque Short, le tampon et la santé du système. Tout est calculé en direct depuis les state.json, en lecture seule. Utilise ce skill dès que Franco demande "short state", "où en est la prod", "état des vidéos", "qu'est-ce que je dois valider", "des alertes ?", "où en est la vidéo 2026-…", "liste des vidéos", "qu'est-ce qui est publié", ou tape /short-state, même sans nommer le skill.
---

# short-state — l'état de la production, en direct

## Principe

Ce skill est **strictement en lecture seule**. Il ne modifie jamais un `state.json`, ne transcrit aucune décision et ne relance aucun agent : ce sont les rôles de l'Orchestrateur. Franco doit pouvoir le lancer dix fois par jour sans aucun effet de bord.

L'état est recalculé à partir des `state.json`, pas lu dans `TABLEAU_DE_BORD.md`. Le tableau de bord n'est à jour qu'après un passage de l'Orchestrateur, alors que ce skill voit aussi ce qui a changé depuis : une décision que Franco vient de saisir, une étape bloquée.

## Étape 1 — Choisir le mode

| Franco demande… | Commande |
|---|---|
| l'état général, quoi faire, des alertes | `short_state.py` |
| une vidéo précise (« où en est la v02 d'hier ») | `short_state.py --video 2026-09-10_v02` |
| la liste des vidéos conçues ou publiées | `short_state.py --registre` |

```bash
python3 <chemin-du-skill>/scripts/short_state.py [--video ID | --registre] [--root CHEMIN]
```

La racine est trouvée comme pour new-short : `--root`, sinon `CHAINE_YT_ROOT`, sinon les emplacements habituels de Google Drive. Code 2 : demande le chemin à Franco. Code 6 : la vidéo est inconnue ; propose les identifiants de `videos_connues` qui ressemblent à sa demande.

## Étape 2 — Rédiger la réponse (vue d'ensemble)

Franco lit souvent sur son téléphone : réponse en français, compacte, les actions d'abord. Les actions arrivent déjà triées par priorité dans le JSON ; garde cet ordre.

```
**À faire maintenant** (3)
1. ⚠ `2026-09-10_v03` — Recherche en alerte : quota API atteint → voir log_erreurs.md
2. CP2 `2026-09-10_v01` — How RAG actually works → valider checkpoints/rapport_CP2.md
3. Audio `2026-09-10_v02` — lancer le run Colab

**En production**
• `2026-09-10_v02` What the new open-weight model changes — Voix off (attente Franco) · storyboard en cours
• `2026-09-11_v01` Whisper vs faster-whisper — CP1 en attente depuis 26 h

**Tampon** 1/4 prêtes · 0 sujet en réserve · prochaine publication 12/09 15:00
**Système** Orchestrateur passé il y a 2 h · 6 vidéos au total
```

Libellés des types d'action :

| Type | Formulation |
|---|---|
| `CORROMPU` | fichier d'état illisible, à réparer |
| `ALERTE` | 3 échecs, afficher `detail` |
| `BLOQUE` | étape en cours depuis trop longtemps, l'agent a probablement planté |
| `CHECKPOINT` | valider le fichier indiqué |
| `AUDIO` | lancer le run Colab |
| `SUJETS` | tampon bas et plus de sujets validés : proposer de lancer ou valider le lot de sujets, ou un `new-short` en voie rapide |
| `ORCHESTRATEUR` | l'Orchestrateur n'est pas passé récemment, les décisions et étapes terminées attendent |
| `DECISION_EN_ATTENTE_ORCHESTRATEUR` | à placer hors liste, en info : « ta décision au CP2 est bien saisie, elle sera prise en compte au prochain passage » |

Règles :
- **Aucune action ?** Commence par « Rien à faire de ton côté pour l'instant », puis le résumé.
- **Liste longue ?** Au-delà de 6 vidéos en production, montre les 6 plus avancées et indique le nombre restant.
- **Dates** : convertis-les en heure locale si tu connais le fuseau de Franco, sinon laisse-les en UTC en le précisant.
- **Pas de commentaire inventé** : ne formule pas de recommandation qui ne découle pas des données. Tu peux proposer de lancer `new-short` quand le type `SUJETS` apparaît, parce que c'est directement lié.

## Étape 2 bis — Mode vidéo (`--video`)

Donne :
1. l'en-tête : id, titre, voie, pilier, statut global ;
2. la frise des étapes, une ligne par étape : ✓ terminée · ▶ en cours · ⏸ attente de Franco · ✗ échec ou alerte · ○ à venir, avec les tentatives et la durée quand elles sont connues ;
3. les décisions lues dans les rapports de checkpoint ;
4. les fichiers de sortie annoncés mais absents (`present: false`), car c'est un signe d'incohérence ;
5. les 3 derniers événements de l'historique.

## Étape 2 ter — Mode registre (`--registre`)

Commence par un décompte par statut (idée, en production, prêtes, programmées, publiées, abandonnées). Liste ensuite les vidéos, les plus récentes d'abord, avec leur date de publication et leur URL quand elles sont publiées. Si Franco demande seulement ce qui est publié, filtre.

## Mode sans système de fichiers local (claude.ai, mobile)

Si le dossier n'est pas accessible localement mais que le connecteur Google Drive est disponible :
1. Recrée en local, dans un dossier temporaire, la structure utile en téléchargeant :
   - le `state.json` de chaque dossier de `videos/` ;
   - les `checkpoints/rapport_CP*.md` des vidéos en attente de validation ;
   - `01_Orchestrateur/config.json` et `derniere_execution.json` s'ils existent ;
   - `02_Veille_hebdo/backlog_sujets.json`.
2. Lance le script avec `--root` sur ce dossier.

La logique reste ainsi identique dans les deux modes. Ne remonte rien sur Drive : ce skill n'écrit jamais.

## Fichiers lus (jamais écrits)

- `videos/*/state.json`, `videos/*/checkpoints/rapport_CP*.md`
- `01_Orchestrateur/config.json`, qui fournit :
  - `cible_tampon` (défaut 4) ;
  - `seuil_blocage_heures` (défaut 2) ;
  - `seuil_orchestrateur_heures` (défaut 6).
- `01_Orchestrateur/derniere_execution.json` ; à défaut, la date de modification de `TABLEAU_DE_BORD.md`
- `02_Veille_hebdo/backlog_sujets.json`
