---
name: short-monteur
description: Agent A7 du pipeline chaine YouTube — execute l'etape E6_montage d'une video (§4.3, §8), une fois l'audio et le storyboard termines. Utilise ce skill quand le tableau de bord de l'Orchestrateur indique une ligne "[AGENT] ... monteur", ou quand Franco dit "monte la video <video_id>", "rends la video pour <video_id>".
---

# monteur (A7) — rendu final d'une video

## Ce que fait cet agent, et ce qu'il ne fait pas

Il rend `06_video_finale.mp4` avec Remotion, a partir du storyboard, de
l'audio et de la charte. Il peut creer de nouveaux composants dans
`composants/` s'il en manque (§8, regle du Monteur), mais ne touche jamais
au storyboard lui-meme (c'est le Designer, A6) ni au CP3.

## Etape 1 — Verifier que c'est bien son tour

`etapes.E6_montage.statut` doit etre `a_venir` ou `echec`, et
`etapes.E4_audio.statut == "termine"` **et**
`etapes.E5_storyboard.statut == "termine"` (les deux, §6.2).

## Etape 2 — Marquer le debut

```bash
python3 <chemin-du-skill>/scripts/etape.py commencer --video <video_id> --etape E6_montage [--root R]
```

## Etape 3 — Composants : reutiliser, etendre, ou creer

Lis `videos/{video_id}/05_storyboard.json`. Pour chaque scene :

1. Si `composant` existe deja dans `composants/src/components/registry.ts`
   avec les bons parametres : rien a faire.
2. Sinon, regarde si un composant existant peut etre etendu (nouveaux
   parametres optionnels, retro-compatibles).
3. Sinon, cree un nouveau composant Remotion dans
   `composants/src/components/<Nom>.tsx` (suis le style de `TitleCard.tsx` :
   props typees, tokens de charte en entree, pas de couleur en dur),
   ajoute-le a `REGISTRE` dans `registry.ts`, et documente-le dans
   `composants/REGISTRE.md` avec le statut `nouveau` (revu de fait au
   CP3, §8).

Verifie que ca compile : `cd composants && npm run typecheck`.

## Etape 4 — Construire les props de rendu

```bash
cd composants
python3 <chemin-du-skill>/scripts/construire_props.py \
  --charte <racine>/00_Profil/charte_visuelle/charte.json \
  --storyboard <racine>/videos/<video_id>/05_storyboard.json \
  --timestamps <racine>/videos/<video_id>/04_timestamps.json \
  --audio <racine>/videos/<video_id>/04_voixoff.wav \
  --sortie /tmp/<video_id>_props.json
```

Ce script normalise `04_timestamps.json` quel que soit son format exact
(cles `word`/`start`/`end` ou `mot`/`debut_s`/`fin_s`).

## Etape 5 — Rendre

```bash
cd composants
npx remotion render src/index.ts Video <racine>/videos/<video_id>/06_video_finale.mp4 \
  --props=/tmp/<video_id>_props.json
```

Si l'environnement n'a pas de navigateur telechargeable (sandbox de dev),
utilise un Chromium deja installe : `REMOTION_BROWSER_EXECUTABLE=<chemin>`
avant la commande (voir `composants/remotion.config.ts`). Sur le poste de
Franco, ce n'est normalement pas necessaire.

## Etape 6 — Cloturer

Succes :

```bash
python3 <chemin-du-skill>/scripts/etape.py terminer --video <video_id> --etape E6_montage \
  --sorties 06_video_finale.mp4 --message "Resume : N scenes, nouveaux composants : ..."
```

Echec (composant impossible a rendre, props invalides, rendu qui plante) :

```bash
python3 <chemin-du-skill>/scripts/etape.py echouer --video <video_id> --etape E6_montage \
  --message "Raison precise"
```

## Etape 7 — Relancer l'Orchestrateur

Si `orchestrateur_cmd` est renseigne, execute-le pour ouvrir le CP3.

## Fichiers

- Lus : `videos/{video_id}/state.json`, `05_storyboard.json`,
  `04_voixoff.wav`, `04_timestamps.json`,
  `00_Profil/charte_visuelle/charte.json`,
  `composants/src/components/registry.ts`
- Ecrits : `videos/{video_id}/06_video_finale.mp4`,
  `videos/{video_id}/state.json` (uniquement `etapes.E6_montage`),
  et, si necessaire, de nouveaux fichiers dans `composants/src/components/`
  + mise a jour de `composants/REGISTRE.md`
