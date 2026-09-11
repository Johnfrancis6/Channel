---
name: short-redacteur
description: Agent A4 du pipeline chaine YouTube — execute l'etape E2_redaction d'une video (§4.3), en boucle avec le Filtre TTS. Utilise ce skill quand le tableau de bord de l'Orchestrateur indique une ligne "[AGENT] ... redacteur", ou quand Franco dit "lance le redacteur sur <video_id>", "ecris le script pour <video_id>".
---

# redacteur (A4) — script d'une video

## Ce que fait cet agent, et ce qu'il ne fait pas

Il produit `02_script_brut.md`. Il ne touche jamais a `CP1`, `E3_filtre`
ni `CP2` : c'est l'Orchestrateur qui gere les checkpoints et la boucle
avec le Filtre TTS (§4.2, §4.3). Son prompt est le point le plus sensible
du pipeline (§4.3) : incarner l'angle "ingenieur ML" sans sonner comme un
resume generique.

## Etape 1 — Verifier que c'est bien son tour

`etapes.E2_redaction.statut` doit etre `a_venir` ou `echec`.

Si `etapes.E3_filtre.statut == "echec"` avec un `message` present et que
l'historique montre un evenement recent de `filtre_tts`, c'est une
**revision** : le Filtre TTS a renvoye le script pour une raison precise
(triades, phrases trop longues, zombie nouns...). Lis ce message et
corrige-le specifiquement, ne reecris pas tout depuis zero.

## Etape 2 — Marquer le debut

```bash
python3 <chemin-du-skill>/scripts/etape.py commencer --video <video_id> --etape E2_redaction [--root R]
```

## Etape 3 — Lire les inputs

- `videos/{video_id}/01_recherche.md` (recherche, angle propose)
- `state.json` : `sujet`, `angle`, `pilier`, `voie`, `etapes.CP1.commentaire`
  (retour de Franco au CP1 — a respecter en priorite)
- **`state.json` > `consignes`** — ton cadre d'ecriture :
  - `idees_max` (3 par defaut) : **le budget du Short**. Tu ecris ce nombre
    d'idees porteuses, pas une de plus. Compte environ **45 mots par idee**,
    soit ~135 mots pour trois — hook et cloture compris ;
  - `format` : le format narratif vise. Un dialogue coute plus de mots par
    idee qu'une explication : c'est legitime, mais dis-le dans ton message
    de cloture pour que le Filtre TTS ne le prenne pas pour du gras ;
  - `note_franco` et `reference` : contraintes de Franco, pas suggestions
- `00_Profil/profil_chaine.md`, `00_Profil/conventions.md`
- **`00_Profil/projets_franco.md`** — ce que Franco a reellement teste et
  peut montrer a l'ecran. Quand tu ancres une idee dans un exemple, prends-le
  la : la chaine dit « j'ai teste », ca doit etre vrai
- le dernier `02_Veille_hebdo/*_analyse_concurrentielle.md`, s'il existe
- en cas de revision : `etapes.E3_filtre.message`
- **en cas de refus au CP2** : `etapes.CP2.commentaire` (§5.5, l'agent precedent
  est relance avec le commentaire en input). C'est le cas quand E2_redaction
  repasse a `a_venir` alors que le script avait deja ete ecrit : Franco a
  refuse le script, et son commentaire prime sur tout le reste. Les rapports
  refuses precedents sont archives dans `checkpoints/refuses/`.

## Etape 4 — Ecrire le script

**Le budget d'abord.** `idees_max` idees porteuses, environ 45 mots
chacune. Une idee de plus, et c'est tout l'aval qui derape : sur
`2026-09-11_v01`, le script faisait 264 mots pour un budget de 135 — 82,5 s
de voix off au lieu de ~42 s, et le probleme n'a ete vu qu'au montage,
quand l'audio etait deja enregistre.

Concretement : si la recherche te donne six faits, tu en gardes **trois**.
Les autres ne sont pas mauvais, ils sont pour une autre video. Un Short qui
essaie de tout dire ne dit rien.


La chaine est en anglais (§14, new-short). Structure attendue dans
`videos/{video_id}/02_script_brut.md` :

```markdown
# Script brut — {titre de travail}

## Hook
...

## Promesse spectateur
...

## Corps (marqueurs de voix / style oral)
...

## CTA / cloture
...
```

Respecte les regles de `conventions.md` (longueur cible des phrases,
pas de parentheses/symboles/URL) autant que possible : c'est le Filtre
TTS qui les fera respecter strictement ensuite, mais un brouillon deja
propre reduit les tours de boucle (max 3, §4.3).

## Etape 5 — Cloturer

Succes :

```bash
python3 <chemin-du-skill>/scripts/etape.py terminer --video <video_id> --etape E2_redaction \
  --sorties 02_script_brut.md --message "Resume en une phrase"
```

Echec (input manquant ou incoherent, ex. `01_recherche.md` absent) :

```bash
python3 <chemin-du-skill>/scripts/etape.py echouer --video <video_id> --etape E2_redaction \
  --message "Raison precise"
```

## Etape 6 — Relancer l'Orchestrateur

Si `orchestrateur_cmd` est renseigne, execute-le pour enchainer sur le
Filtre TTS.

## Fichiers

- Lus : `videos/{video_id}/state.json`, `01_recherche.md`,
  `00_Profil/profil_chaine.md`, `00_Profil/conventions.md`,
  `00_Profil/projets_franco.md`,
  `02_Veille_hebdo/*_analyse_concurrentielle.md`
- Ecrits : `videos/{video_id}/02_script_brut.md`,
  `videos/{video_id}/state.json` (uniquement `etapes.E2_redaction`)
