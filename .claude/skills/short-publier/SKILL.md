---
name: short-publier
description: Enregistre la publication d'un Short de la chaine YouTube de Franco (etape E7, §11) et ferme son cycle de vie dans le registre. Utilise ce skill quand Franco dit "j'ai publie 2026-09-11_v01", "voici l'URL du short", "marque la video comme publiee", "programme la publication pour vendredi", ou tape /short-publier. Ne publie rien sur YouTube : Franco publie, ce skill enregistre.
---

# short-publier (E7) — fermer le cycle de vie d'une video

## Ce que fait ce skill, et ce qu'il ne fait pas

Il enregistre une publication deja faite (ou programmee) par Franco :
date, URL, passage du registre a `publiee` ou `programmee`. Il ne parle pas
a l'API YouTube et ne publie rien lui-meme — on est en phase test (§11),
Franco publie a la main.

Il refuse d'agir si `etapes.CP3.statut` n'est pas `valide` : aucune
publication sans CP3 valide (§2).

## Pourquoi ce skill existe

Sans lui, `statut_global` ne depassait jamais `prete`. Rien n'ecrivait
`publiee` ni `publication.date_effective`, que le tableau de bord et
`short-state` lisent pourtant tous les deux : le compteur "Publiees"
restait a zero, et le tampon comptait comme disponibles des videos deja en
ligne. La seule issue etait d'editer `state.json` a la main, ce que le
§5.5 cherche precisement a eviter.

## Etape 1 — Reunir ce qu'il faut

- le `video_id` (ex. `2026-09-11_v01`) ;
- l'**URL** du Short, si la video est en ligne ;
- la **date** : celle de la mise en ligne, ou celle prevue si on programme.

Si Franco ne donne pas l'URL et dit seulement "c'est publie", demande-la :
sans elle, le registre est inexploitable pour H1 (§4.3), qui rapproche les
performances YouTube des videos produites.

## Etape 2 — Enregistrer

Video deja en ligne :

```bash
python3 <chemin-du-skill>/scripts/publier.py --video <video_id> \
  --url https://www.youtube.com/shorts/xxxx [--date 2026-09-14] [--root R]
```

Publication programmee, pas encore en ligne :

```bash
python3 <chemin-du-skill>/scripts/publier.py --video <video_id> \
  --statut programmee --date 2026-09-14 [--url ...] [--root R]
```

Une video `programmee` reste visible au tableau de bord (`E7_publication`
en `attente_franco`) jusqu'a ce qu'on la repasse en `publiee` avec l'URL —
sans `--force` : programmer puis publier est le trajet normal, pas une
correction.

Video abandonnee (sujet laisse tomber, doublon, actualite perimee) :

```bash
python3 <chemin-du-skill>/scripts/publier.py --video <video_id> \
  --statut abandonnee --motif "sujet deja traite dans 2026-09-04_v01" [--root R]
```

L'abandon n'exige **pas** de CP3 valide : on abandonne justement une video
qui n'y arrivera pas. Le `--motif` est obligatoire — c'est la seule trace
de la raison, et H1 la lit (§4.3). Une fois abandonnee, la video sort du
tampon, libere son `sujet_id` et ne reclame plus aucun agent.

Correction d'une URL ou d'une date deja saisie : ajoute `--force`. Sans
lui, le script refuse avec le code 8 sur un cycle **deja clos** (`publiee`
ou `abandonnee`), pour ne pas ecraser en silence.

## Etape 3 — Lire le resultat

Le script repond en JSON. Codes : `0` ok, `2` racine introuvable,
`4` date invalide, URL manquante ou fantaisiste, motif d'abandon manquant,
`6` video inconnue, `7` CP3 non valide, `8` cycle deja clos (utiliser
`--force`).

Sur un code `7`, ne contourne rien : dis a Franco que le CP3 doit etre
valide d'abord, et propose `short-state --video <id>` pour voir ou en est
la validation.

## Etape 4 — Relancer l'Orchestrateur

Si `orchestrateur_cmd` est renseigne dans `01_Orchestrateur/config.json`,
execute-le : le registre et le tableau de bord sont regeneres, le tampon
recalcule, et la video sort de la file de production.

L'Orchestrateur ne touche plus au statut une fois qu'il vaut `programmee`,
`publiee` ou `abandonnee` (§5.3). Ce n'etait pas le cas : il le reecrivait
en `prete` des le passage suivant, et cette relance-ci defaisait donc la
publication qu'elle etait censee confirmer.

## Fichiers

- Lus : `videos/{video_id}/state.json`,
  `01_Orchestrateur/config.json`
- Ecrits : `videos/{video_id}/state.json` (`etapes.E7_publication`,
  `publication`, `statut_global`, `historique`) — jamais un checkpoint,
  jamais l'etape d'un autre agent (§4.2)
