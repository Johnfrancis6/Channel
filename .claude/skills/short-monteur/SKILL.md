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

**Il n'invente pas le style.** La direction artistique de chaque scene est
decidee par A6 et vit dans le champ `da` du storyboard ; les principes
recurrents (easing, regle du wobble) vivent dans `charte.json > animation`.
Le role de A7 est de les implementer fidelement, pas de les rejuger. Si une
DA est impossible a rendre telle quelle, il la signale dans son message de
cloture plutot que de la remplacer en silence.

## Etape 1 — Verifier que c'est bien son tour

`etapes.E6_montage.statut` doit etre `a_venir` ou `echec`, et
`etapes.E4_audio.statut == "termine"` **et**
`etapes.E5_storyboard.statut == "termine"` (les deux, §6.2).

**Cas du refus au CP3.** Si le montage avait deja ete fait et que
`E6_montage` est repasse a `a_venir`, c'est que Franco a refuse le rendu :
lis `etapes.CP3.commentaire` et traite-le en priorite (§5.5, l'agent
precedent est relance avec le commentaire en input). Les rapports refuses
precedents sont archives dans `checkpoints/refuses/`.

## Etape 2 — Marquer le debut

```bash
python3 <chemin-du-skill>/scripts/etape.py commencer --video <video_id> --etape E6_montage [--root R]
```

## Etape 3 — Composants : reutiliser, etendre, ou creer

Lis `videos/{video_id}/05_storyboard.json`.

**Avant tout** : si des scenes portent encore `"a_completer": true`, c'est
que A6 a livre le squelette sans le trancher. Ne monte pas a l'aveugle —
echoue l'etape avec la liste des scenes concernees, pour que le storyboard
soit repris. Une video montee sur un squelette arrive au CP3 sans avoir
jamais ete concue.

Pour chaque scene :

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

**Appliquer la DA.** Chaque composant recoit `da` en prop, en plus de
`charte`. Traduis-la ainsi, en te servant de `charte.json > animation` pour
les valeurs par defaut :

| `da.mouvement` | Implementation attendue |
|---|---|
| `entree_par_le_bas` | translation Y depuis ~24px + opacite 0→1 sur `duree_entree_s` |
| `fondu` | opacite seule |
| `zoom_lent` | `scale` qui derive lentement sur toute la scene |
| `glissement_lateral` | translation X, sens alterne d'une scene a l'autre |
| `apparition_sequencee` | les elements entrent l'un apres l'autre, ~80ms d'ecart |
| `aucun` | pas d'animation d'entree |

| `da.technique` | Implementation attendue |
|---|---|
| `spring` | `spring()` de Remotion |
| `interpolate` | `interpolate()` + easing de `charte.animation.easing_entree` |
| `lottie` | `@remotion/lottie` sur un fichier de `videos/{video_id}/assets/` ou de `composants/lottie/` — voir ci-dessous |
| `statique` | aucune interpolation |

`da.rythme` module la duree d'entree : `pose` l'allonge (~1.5x),
`standard` la laisse, `punch` la raccourcit (~0.5x) et coupe sec.

La **regle du wobble** (`charte.animation.wobble`) s'applique aux elements
dessines a la main (stickman, traits), jamais au texte.

**Lottie.** Le style vise est le sticker anime, et Lottie est autorise pour
tout type d'animation. Sa limite est technique, pas reglementaire : un
fichier Lottie est **pre-rendu**. On le joue, on le boucle, on en lit un
segment, on recolore des couches — on ne change pas ce qu'il raconte.
Reserve-le donc au **fixe et expressif** (personnage, transition, icone) et
garde en Remotion tout ce qui **varie d'une video a l'autre** (schemas,
texte, chiffres, sous-titres). Sinon chaque nouvelle variante de schema
exigerait un fichier fait a la main avant que la video puisse tourner.

Ou trouver les fichiers : `videos/{video_id}/assets/` pour cette video,
`composants/lottie/` pour les recurrents. Si `@remotion/lottie` n'est pas
encore installe, installe-le (`npm i @remotion/lottie lottie-web` dans
`composants/`) et copie le `.json` dans `composants/public/lottie/` — le
serveur de rendu sert les assets locaux depuis la, comme pour l'audio
(prefixe `/public/`). Si une scene demande `technique: "lottie"` mais
qu'aucun fichier n'est disponible, ne bloque pas : rends-la en Remotion et
signale-le dans ton message de cloture.

Verifie que ca compile : `cd composants && npm run typecheck`.

## Etape 4 — Construire les props de rendu

```bash
cd composants
python3 <chemin-du-skill>/scripts/construire_props.py \
  --charte <racine>/00_Profil/charte_visuelle/charte.json \
  --storyboard <racine>/videos/<video_id>/05_storyboard.json \
  --timestamps <racine>/videos/<video_id>/04_timestamps.json \
  --phrases <racine>/videos/<video_id>/04_phrases.json \
  --audio <racine>/videos/<video_id>/04_voixoff.wav \
  --sortie /tmp/<video_id>_props.json
```

Ce script fait deux choses :

- il normalise `04_timestamps.json` quel que soit son format exact (cles
  `word`/`start`/`end` ou `mot`/`debut_s`/`fin_s`) ;
- avec `--phrases`, il **recale les durees de scenes sur l'audio reel**.
  Sans ce recalage, les scenes gardent l'estimation a ~2.5 mots/s du
  storyboard : le visuel derive de la voix, et la video se termine avant ou
  apres l'audio.

**Lis le champ `avertissements` de sa sortie JSON.** S'il signale un
desaccord entre le nombre de phrases et le nombre de scenes, le recalage
n'a pas eu lieu : dis-le dans ton message de cloture, c'est un defaut
visible au CP3. Si `04_phrases.json` est absent (run audio anterieur a la
revue du 11/09/2026), relancer le notebook en `MODE='full'` le produit.

## Etape 5 — Verification visuelle avant de rendre

Ne livre pas un rendu que tu n'as jamais regarde (§12). Sors quelques
images fixes et regarde-les :

```bash
cd composants
npx remotion still src/index.ts Video /tmp/<video_id>_f0.png \
  --props=/tmp/<video_id>_props.json --frame=0
npx remotion still src/index.ts Video /tmp/<video_id>_mid.png \
  --props=/tmp/<video_id>_props.json --frame=<moitie de la duree en frames>
```

Prends au moins la premiere frame du hook, une frame de milieu de video et
une frame de fin. Verifie : le texte tient dans le cadre en 1080x1920, les
sous-titres ne recouvrent pas l'element principal, les couleurs viennent
bien de la charte, et la scene correspond a la DA demandee. Si quelque
chose ne va pas, corrige le composant et refais des images fixes — c'est
beaucoup moins cher qu'un rendu complet.

## Etape 6 — Rendre

```bash
python3 <chemin-du-skill>/scripts/rendre_video.py \
  --video <video_id> --root <racine> \
  --props /tmp/<video_id>_props.json \
  --sortie videos/<video_id>/06_video_finale.mp4 [--browser <chemin-chromium>]
```

Ce script verifie les prerequis avant de lancer `remotion render`
(node_modules present, props lisibles, registre accessible) et verifie que
le MP4 produit n'est ni absent ni vide. Codes : `0` ok, `2` props
absentes/invalides, `4` `node_modules` absent (`npm install` dans
`composants/`), `5` registre inaccessible, `6` echec du rendu, `7` MP4
absent ou vide. `--dry-run` verifie les prerequis sans rendre.

Si l'environnement n'a pas de navigateur telechargeable (sandbox de dev),
passe un Chromium deja installe via `--browser` (voir
`composants/remotion.config.ts`). Sur le poste de Franco, ce n'est
normalement pas necessaire.

## Etape 7 — Cloturer

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

## Etape 8 — Relancer l'Orchestrateur

Si `orchestrateur_cmd` est renseigne, execute-le pour ouvrir le CP3.

## Fichiers

- Lus : `videos/{video_id}/state.json`, `05_storyboard.json`,
  `04_voixoff.wav`, `04_timestamps.json`, `04_phrases.json`,
  `videos/{video_id}/assets/` (images d'inspiration, fichiers Lottie),
  `00_Profil/charte_visuelle/charte.json` (bloc `animation` compris),
  `composants/src/components/registry.ts`
- Ecrits : `videos/{video_id}/06_video_finale.mp4`,
  `videos/{video_id}/state.json` (uniquement `etapes.E6_montage`),
  et, si necessaire, de nouveaux fichiers dans `composants/src/components/`
  + mise a jour de `composants/REGISTRE.md`
