---
name: new-short
description: Déclenche la création d'un nouveau Short pour la chaîne YouTube IA de Franco. Crée le dossier de la vidéo et son state.json dans /ChaineYouTube/videos/, puis relance l'Orchestrateur pour que la recherche démarre. Utilise ce skill dès que Franco dit "new short", "nouveau short", "lance une vidéo", "crée une vidéo sur…", "démarre la prod", "on fait un short sur…", "lance la veille actu", ou tape /new-short, même s'il ne nomme pas le skill. Ne l'utilise pas pour consulter l'avancement (c'est le rôle de short-state).
---

# new-short — démarrer la production d'un Short

## Ce que fait ce skill, et ce qu'il ne fait pas

Ce skill ouvre une nouvelle vidéo dans le pipeline. Concrètement, il crée `videos/{video_id}/state.json` et le dossier `checkpoints/`, puis relance l'Orchestrateur. Il **n'exécute aucun agent lui-même** : la recherche, le script et le reste sont faits par les agents, pilotés par l'Orchestrateur.

Deux règles de la chaîne s'appliquent ici. Garde-les en tête, car elles protègent le contrôle éditorial de Franco :
- **Ne jamais choisir un sujet que Franco n'a pas validé.** Les seules sources de sujet légitimes sont :
  - un sujet que Franco donne lui-même ;
  - un sujet du backlog validé en lot (`02_Veille_hebdo/backlog_sujets.json`) ;
  - la veille actu, dont les propositions passeront par un CP1 individuel.
- **N'écrire aucun fichier partagé.** Le script ne crée que des fichiers neufs dans le dossier de la vidéo. Le registre des vidéos est reconstruit à partir des `state.json`, donc il n'y a jamais de conflit d'écriture avec l'Orchestrateur.

## Étape 1 — Traduire la demande en arguments

| Franco dit… | Arguments |
|---|---|
| « new short » (sans précision) | aucun : prend le plus ancien sujet disponible du backlog validé |
| « new short sur X » | `--sujet "X"` (+ `--pilier` si c'est évident) |
| « new short actu » / « lance la veille actu » | `--voie rapide` : le Chercheur proposera des sujets d'actu au CP1 |
| « new short sur X, angle Y » | `--sujet "X" --angle "Y"` |
| « new short avec le sujet 2026-S37-02 » | `--sujet-id 2026-S37-02` |
| une consigne pour le Chercheur (« focus benchmark local ») | `--note "…"` |

Piliers possibles : `actu_ia`, `avis_outil`, `concept`, `projet_perso`, `tuto`. Ne devine pas si ce n'est pas clair : laisse le script mettre `a_determiner`, le Chercheur tranchera et Franco validera au CP1.

La chaîne est en anglais. Si Franco donne le sujet en français, passe-le tel quel : le Rédacteur produira le script en anglais.

## Étape 2 — Lancer le script

```bash
python3 <chemin-du-skill>/scripts/new_short.py [arguments]
```

Le script trouve la racine `/ChaineYouTube` tout seul : `--root`, sinon la variable `CHAINE_YT_ROOT`, sinon les emplacements habituels de Google Drive pour ordinateur. En cas de doute, fais d'abord un essai avec `--dry-run`.

La sortie est toujours un JSON avec `code` :

| Code | Signification | Que faire |
|---|---|---|
| 0 | Vidéo créée | Passer à l'étape 3 |
| 2 | Racine introuvable ou erreur d'écriture | Demander le chemin du dossier à Franco et suggérer de définir `CHAINE_YT_ROOT` |
| 3 | Backlog vide | Proposer deux options : un short en voie rapide (`--voie rapide`), ou un sujet donné par Franco |
| 4 | Doublon probable (`doublon_de`) | Montrer la vidéo existante et demander s'il veut quand même créer (`--force`) |
| 5 | `sujet_id` inconnu | Montrer la liste `disponibles` renvoyée |

Ne relance jamais avec `--force` sans l'accord explicite de Franco.

## Étape 3 — Relancer l'Orchestrateur

Si `orchestrateur_cmd` n'est pas vide dans la sortie (il vient de `01_Orchestrateur/config.json`), exécute cette commande une fois, pour que la recherche démarre tout de suite. Sauf si Franco a dit de ne pas lancer.

Si la commande est vide ou échoue, ne tente pas de faire le travail des agents à sa place. Dis simplement que la vidéo sera prise en charge au prochain passage de l'Orchestrateur, et donne l'erreur si la commande a échoué.

## Étape 4 — Répondre à Franco

Réponse courte, lisible sur téléphone, en français :

```
Short créé : `2026-09-10_v02` — What the new open-weight model changes
Voie rapide · pilier actu_ia · CP1 à venir
Prochaine étape : recherche, puis tu valideras le sujet et l'angle (CP1).
[Orchestrateur relancé | Pris en charge au prochain passage de l'Orchestrateur]
```

Ajoute une ligne seulement si c'est utile : backlog presque vide (`backlog_restant` ≤ 1), ou note transmise au Chercheur. Pas de JSON brut dans la réponse.

## Mode sans système de fichiers local (claude.ai, mobile)

Si le dossier n'est pas accessible localement mais que le connecteur Google Drive est disponible :
1. Recrée en local, dans un dossier temporaire, la structure minimale en téléchargeant :
   - `02_Veille_hebdo/backlog_sujets.json` ;
   - `01_Orchestrateur/config.json` ;
   - le `state.json` de chaque dossier de `videos/` (pour la numérotation et la détection de doublons).
2. Lance le script avec `--root` sur ce dossier temporaire.
3. Crée sur Drive le dossier `videos/{video_id}/` et uploade le `state.json` généré.
4. Dans ce mode, l'Orchestrateur ne peut pas être relancé : dis-le à Franco.

## Fichiers

- Lus : `02_Veille_hebdo/backlog_sujets.json`, `01_Orchestrateur/config.json`, `videos/*/state.json`
- Écrits : `videos/{video_id}/state.json`, `videos/{video_id}/checkpoints/` (création uniquement)
- Modèle : `assets/state_template.json`. Si le schéma de `state.json` évolue, modifie ce fichier plutôt que le script.
