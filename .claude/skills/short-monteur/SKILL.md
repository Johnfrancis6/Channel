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

Lis d'abord **`videos/{video_id}/05_cadrage.md`** : c'est la note de
cadrage du Designer, discutee avec Franco. Elle dit en clair ce que chaque
bloc doit montrer a l'ecran, ce qui a ete juge faisable et a quel cout.
Quand le storyboard ne donne qu'une cle (`scene="workflow_fixed_path"`), le
cadrage donne l'image — c'est lui qui fait autorite sur l'intention.

Puis `videos/{video_id}/05_storyboard.json`.

**Avant tout** : si des scenes portent encore `"a_completer": true`, c'est
que A6 a livre le squelette sans le trancher. Ne monte pas a l'aveugle —
echoue l'etape avec la liste des scenes concernees, pour que le storyboard
soit repris. Une video montee sur un squelette arrive au CP3 sans avoir
jamais ete concue.

### La regle ne porte pas sur ce que tu montres

**« Reutiliser, sinon etendre, sinon creer » gouverne le STYLE, jamais le
SUJET.** Le but est d'empecher la derive stylistique : que deux videos ne
se ressemblent plus parce que chacune a invente sa facon de dessiner une
boite. Ce n'est pas un but d'economie.

Reutiliser `ConceptCutaway` pour cinq serveurs MCP differents, ce n'est pas
reutiliser un composant : c'est **rendre cinq fois la meme image**. C'est
exactement ce qui est arrive sur `2026-09-11_v01`, et c'est la faute que
cette regle est censee empecher, pas celle qu'elle doit produire.

**Contrainte dure, verifiable au catalogue :**

> Deux scenes d'une meme video ne peuvent pas produire la meme image.

Si deux scenes appellent le meme composant, elles doivent differer par la
**donnee** — une ressource differente, un nombre d'elements different, une
mise en scene differente. Deux scenes qui ne different que par leur texte
ne sont pas deux scenes : c'est une scene, et il faut soit les fusionner,
soit en trouver une seconde image. Un `label` qui change ne compte pas.

Pour chaque scene :

1. Si `composant` existe deja dans `composants/src/components/registry.ts`
   avec les bons parametres **et que la contrainte ci-dessus est tenue** :
   rien a faire.
2. Sinon, regarde si un composant existant peut etre etendu (nouveaux
   parametres optionnels, retro-compatibles). C'est le cas le plus frequent
   et le moins cher : un parametre de plus suffit souvent a faire une image
   qui ne ressemble pas a la precedente.
3. Sinon, cree un nouveau composant Remotion dans
   `composants/src/components/<Nom>.tsx` (suis le style de `TitleCard.tsx` :
   props typees, tokens de charte en entree, pas de couleur en dur, **pas de
   fond** — `Fond.tsx` est rendu une fois pour toute la video), ajoute-le a
   `REGISTRE` dans `registry.ts`, et documente-le dans
   `composants/REGISTRE.md` avec le statut `nouveau` (revu de fait au
   CP3, §8).

**Ce que creer coute reellement.** Un `.tsx`, un typecheck et une ligne dans
`REGISTRE.md` : c'est du travail, assume-le. Mais deux des quatre couts
qu'on croyait payer n'en sont pas. Les **images du catalogue** sont
generees par `python3 outils/generer_apercus.py`, tu n'as aucune image a
produire a la main. Et la **relecture au CP3** a lieu de toute facon, que le
composant soit neuf ou non : elle ne coute rien de plus.

Reste donc un fichier et une ligne de tableau. Ne renonce pas a une image
pour ca.

**Appliquer la DA.** Chaque composant recoit `da` en prop, en plus de
`charte`. **Tu n'implementes pas la DA : tu appelles `src/animation.ts`, qui
l'implemente deja.** Ce module tient les huit regles du §8 pour tous les
composants a la fois. Reecrire un `interpolate()` a la main dans un composant,
c'est refabriquer une version approximative de ce qui existe — et c'est ainsi
qu'on se retrouve avec trois composants qui bougent chacun un peu autrement.

| Ce que tu veux | Ce que tu appelles |
|---|---|
| L'entree d'un element, selon `da.mouvement` et `da.rythme` | `styleEntree(frame, fps, charte, da, index)` |
| La progression 0→1 de cette entree, pour animer autre chose (un trace SVG) | `progressionEntree(frame, fps, charte, da, index)` |
| Le mouvement continu de la scene (regle 8) | `styleContinu(frame, fps, charte, da, attenuation)` |
| L'accent sur le mot prononce | `pulsation(frame, fps, pulsationFrame)` |
| Un mouvement de plan sur une capture ou un b-roll | `punchIn(frame, fps, dureeScene, da, index)` |
| Le retard du mouvement secondaire (regle 5) | `retardSecondaireFrames(charte, fps)` |

L'`index` que prennent plusieurs de ces fonctions est le **rang de l'element
dans son groupe** : c'est lui qui produit le decalage de 80 ms, la variation
de vitesse et l'alternance des sens. Passer 0 partout annule trois des huit
regles d'un coup.

La **regle du wobble** (`charte.animation.wobble`) s'applique aux elements
dessines a la main (stickman, traits), jamais au texte.

**Tout est code en Remotion.** Lottie a ete envisage puis ecarte : la
fluidite ne vient pas d'un fichier pre-rendu, elle se code. Les huit regles
ci-dessous separent une animation vivante d'une animation mecanique ; leurs
valeurs sont dans `charte.json > animation.naturel`.

**Chaque regle est nommee avec la fonction qui la porte.** C'est deliberé :
une regle « appliquee » doit se verifier par un `grep`, pas par une
declaration. Les regles 2 et 7 sont restees ecrites, documentees et fausses
pendant cinq jours parce que leur fonction n'avait aucun appelant.

| # | Regle | Qui la porte |
|---|---|---|
| 1 | **Ressort plutot que rampe.** Un mouvement reel accelere puis se pose ; une rampe lineaire se voit immediatement. | `progressionEntree` (`spring()` par defaut) |
| 2 | **Rien ne s'arrete net.** Une fin brutale est le signe le plus sur d'une animation bâclee. | `opaciteSortie` pour la derniere scene ; `TransitionSeries` pour toutes les autres |
| 3 | **Decalage** (80 ms) : ce qui entre ensemble parait mecanique. | `decalageFrames`, via l'`index` de `styleEntree` |
| 4 | **Jamais deux elements exactement a la meme vitesse** (15 %). | `facteurVitesse`, via le meme `index` |
| 5 | **Mouvement secondaire** (120 ms) : quelque chose suit l'element principal. | `retardSecondaireFrames` |
| 6 | **Anticipation** (10 px) sur les gestes marques. | `styleEntree` (`anticipation_px`) |
| 7 | **Parallaxe** (0,4) : le fond bouge moins vite que le premier plan. | `parallaxe`, applique par `Fond.tsx` |
| 8 | **Rien n'est jamais totalement immobile.** Une image figee parait morte. | `styleContinu` |

Applique-les a **tous** les composants, pas seulement au personnage. Si un
composant que tu ecris n'appelle aucune de ces fonctions, il ne respecte
aucune des huit regles — c'est vrai par construction, verifie-le avant de
rendre.

Verifie que ca compile : `cd composants && npm run typecheck`.

**Apres avoir cree ou modifie un composant**, declare ses variantes dans
`composants/apercus.json` et regenere le catalogue :

```bash
python3 <chemin-du-skill>/outils/generer_apercus.py
```

Sans ca, le Designer continuera de choisir a l'aveugle sur la prochaine
video — c'est exactement ce qui s'est passe sur `2026-09-11_v01`. Regarde
les images produites : elles disent en une seconde ce qu'aucun test ne peut
verifier (cadre trop vide, texte illisible, element hors champ).

## Etape 4 — Construire les props de rendu

### 4a — Resoudre les ressources declarees par le Designer

Si le storyboard contient des `besoins` (captures, logos, images, b-roll) :

```bash
python3 <chemin-du-skill>/outils/resoudre_ressources.py \
  --storyboard <racine>/videos/<video_id>/05_storyboard.json \
  --root <racine>
```

Il ecrit `05b_ressources.json`, le fichier que l'etape suivante consomme.
Il fait la plomberie deterministe — telecharger un logo, capturer une page,
retrouver un fichier designe, mesurer la duree d'un clip — et **s'arrete la
ou commence le jugement** : associer « l'agent modifie un fichier dans VS
Code » au rush `capture_ecran_2026_09_16.mp4` est ton travail, pas le sien.

Lis sa sortie JSON :

- **`non_resolus`** — pour chacun, regarde `rushes_disponibles` (les fichiers
  que Franco a deposes dans `assets/`, avec leur description quand
  `assets/rushes.json` en donne une), choisis, et relance avec
  `--associer <cle>=<fichier>`. Un besoin `obligatoire` non resolu sort en
  **code 3** : ne rends pas la video sans l'avoir traite ou signale.
- **`avertissements`** — une duree de clip inconnue (pas de `ffprobe`)
  signifie que `PlanBroll` ne rebouclera pas un clip plus court que sa
  scene : la fin du plan sera noire. Declare la duree dans
  `assets/rushes.json` si le cas se presente.

Un besoin sans fichier n'empeche pas le montage : la ressource est
simplement absente de la table et le composant affiche « Ressource
manquante » en clair — ce qui se voit au CP3, contrairement a un cadre noir.
Mais **ne laisse pas passer ca en silence** : dis-le au message de cloture.

### 4b — Assembler les props

```bash
cd composants
python3 <chemin-du-skill>/scripts/construire_props.py \
  --charte <racine>/00_Profil/charte_visuelle/charte.json \
  --storyboard <racine>/videos/<video_id>/05_storyboard.json \
  --timestamps <racine>/videos/<video_id>/04_timestamps.json \
  --phrases <racine>/videos/<video_id>/04_phrases.json \
  --audio <racine>/videos/<video_id>/04_voixoff.wav \
  --ressources <racine>/videos/<video_id>/05b_ressources.json \
  --sortie /tmp/<video_id>_props.json
```

Ce script fait trois choses :

- il normalise `04_timestamps.json` quel que soit son format exact (cles
  `word`/`start`/`end` ou `mot`/`debut_s`/`fin_s`) ;
- avec `--ressources`, il **copie les assets** de `05b_ressources.json`
  (captures, logos, images, b-roll) dans `composants/public/` et remplit
  `props.ressources`, la table que les composants `Plan*` consultent. Le
  serveur de rendu de Remotion ne sert que ce dossier : un chemin absolu ou
  une URI `file://` echouent tous les deux. Une ressource dont le fichier
  manque est **omise** — le composant affiche « Ressource manquante » en
  clair, ce qui se voit, plutot qu'un cadre noir que personne ne remarque ;
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

Ne livre pas un rendu que tu n'as jamais regarde (§12). Deux images fixes
sur onze scenes, c'est 18 % de la video : c'est ce qui a laisse passer les
defauts de `2026-09-11_v01`.

### Une image par scene, pas deux par video

```bash
cd composants
python3 - <<'EOF'
import json, subprocess
props = json.load(open("/tmp/<video_id>_props.json"))
fps = props["charte"]["format"]["fps"]
debut = 0.0
for i, sc in enumerate(props["scenes"]):
    milieu = round((debut + sc["duree_s"] / 2) * fps)
    subprocess.run(["npx", "remotion", "still", "src/index.ts", "Video",
                    f"/tmp/<video_id>_s{i+1}.png",
                    "--props=/tmp/<video_id>_props.json", f"--frame={milieu}"])
    debut += sc["duree_s"]
EOF
```

**Regarde-les toutes**, puis verifie :

- le texte tient dans le cadre en 1080x1920 ;
- les sous-titres ne recouvrent pas l'element principal ;
- les couleurs viennent de la charte, aucune n'est ecrite en dur ;
- la scene correspond a la DA demandee ;
- **aucune image ne ressemble a une autre.** C'est la contrainte de
  l'etape 3, et c'est ici qu'elle se verifie. Deux images qui ne different
  que par leur texte sont un defaut, pas une variante.

Si quelque chose ne va pas, corrige le composant et refais l'image — c'est
beaucoup moins cher qu'un rendu complet.

### Ce que les images fixes ne peuvent pas montrer

Un saut d'opacite a un raccord, une entree qui arrive trop tard, un element
qui se fige apres 0,3 s : **rien de tout cela n'existe sur une image fixe**,
par construction. C'est un angle mort du controle, pas un oubli.

Tu ne peux pas le lever toi-meme — Remotion Studio est une interface
navigateur, elle se regarde. **Donne donc la commande a Franco dans ton
message de cloture**, pour qu'il puisse parcourir la timeline avant de
valider le CP3 :

```bash
cd composants && npx remotion studio src/index.ts
# puis, dans le Studio : charger /tmp/<video_id>_props.json
```

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

**Avant de cloturer : rien de mort.** Tout ce que tu as ajoute — une
fonction exportee dans `animation.ts`, un champ dans `types.ts`, un
parametre de composant — doit avoir **au moins un appelant dans le meme
commit**. Verifie-le, litteralement :

```bash
cd composants && grep -rn "<nom_de_ce_que_tu_as_ajoute>" src/ | grep -v "export"
```

Ce n'est pas une regle de proprete. `opaciteSortie`, `parallaxe` et
`transition_sortie` ont ete ecrits le 11/09, typecheck au vert, documentes
comme faits — et sont restes a zero appelant pendant cinq jours. Pendant ce
temps aucun element ne sortait jamais de l'ecran, et la revue les comptait
comme livres. **Un export qui compile passe pour du travail fait.** Si tu ne
peux pas l'appeler maintenant, ne l'ajoute pas.

Succes :

```bash
python3 <chemin-du-skill>/scripts/etape.py terminer --video <video_id> --etape E6_montage \
  --sorties 06_video_finale.mp4 --message "Resume : N scenes, nouveaux composants : ..."""

# Le message de cloture porte aussi la commande du Studio (etape 5) :
# c'est le seul moyen pour Franco de voir bouger la video avant le CP3.
```

Echec (composant impossible a rendre, props invalides, rendu qui plante) :

```bash
python3 <chemin-du-skill>/scripts/etape.py echouer --video <video_id> --etape E6_montage \
  --message "Raison precise"
```

## Etape 8 — Relancer l'Orchestrateur

Si `orchestrateur_cmd` est renseigne, execute-le pour ouvrir le CP3.

## Fichiers

- Lus : `videos/{video_id}/state.json`, `05_cadrage.md`, `05_storyboard.json`,
  `04_voixoff.wav`, `04_timestamps.json`, `04_phrases.json`,
  `videos/{video_id}/assets/` (images d'inspiration),
  `00_Profil/charte_visuelle/charte.json` (bloc `animation` compris),
  `composants/src/components/registry.ts`
- Ecrits : `videos/{video_id}/06_video_finale.mp4`,
  `videos/{video_id}/state.json` (uniquement `etapes.E6_montage`),
  et, si necessaire, de nouveaux fichiers dans `composants/src/components/`
  + mise a jour de `composants/REGISTRE.md`
