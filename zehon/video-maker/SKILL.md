---
name: video-maker
description: Monte la vidéo d'une vidéo Zehon (chaîne YouTube « de la matière brute à l'objet ») à partir de son dossier Drive — 03_scenes.md, images/, clips/, voix/voix.wav et voix/mots.json — en rendu/video.mp4 1080p, avec zoom et panoramiques lents, fondus, plans animés, titres de question, texte animé, puis un contrôle avant publication. Utilise cette skill dès que Franco parle de montage, d'assemblage, de rendu, de « monte le sel », de video.mp4, d'un extrait ou d'un aperçu de la vidéo, ou demande si la vidéo est prête à publier, même s'il ne nomme pas la skill.
---

# video-maker — le montage d'une vidéo Zehon

Tu assembles une vidéo **dont le contenu est fini** (skill `content-maker`)
et dont Franco a produit les pièces (images Gemini, plans animés, voix
Colab). Tu n'écris ni le script ni les prompts. Tout le travail passe par
`scripts/monter.py` ; lis sa docstring si tu dois aller plus loin que
cette page.

## Ce que fait monter.py

| Étape | Ce qui se passe |
|---|---|
| Lire | le tableau de `03_scenes.md` (types `image`, `video`, `titre`) ; une erreur nomme la ligne |
| Valider | une image par scène `image` et `video` (`images/scene_NNN.png` ou `.jpg`) ; le plan animé (`clips/anim_NNN.mp4` ou `scene_NNN.mp4`) peut manquer : l'image le remplace |
| Caler | chaque scène est retrouvée mot à mot dans `mots.json` (nombres compris : « 8 000 » = « huit mille ») ; les coupes tombent dans les pauses de la voix ; un **titre** ajoute 3 s de silence, le temps de lire la question |
| Rendre | 1920×1080, 30 i/s ; zoom lent de 5 % ou panoramique, fondu enchaîné de 0,6 s, plans animés recadrés (ralentis puis figés s'ils sont trop courts), texte animé en bas à gauche quand la voix prononce le mot (au moins 2,5 s à l'écran), titres sur l'image suivante floutée ; son normalisé à −14 LUFS, crêtes à −1,5 dB |
| Contrôler | image 1920×1080, piste audio, pas de silence (volume moyen > −60 dB), pas de saturation (crête ≤ −0,5 dB), durée attendue. **Un rendu n'est fini que si ce contrôle passe** |

Sorties : `rendu/video.mp4` (ou `rendu/extrait_AAA-BBB.mp4`),
`rendu/rapport.json` (début et durée de chaque scène, avertissements,
contrôle), `rendu/verdict.json` et `rendu/apercu/` (le verdict court et
6 images, ce qu'on lit ici) et `rendu/sous_titres.srt` (vidéo entière et
`--plan`), à déposer sur YouTube avec la vidéo.

## La musique

Une nappe libre de droits (bibliothèque audio de YouTube, « attribution
non requise »), rangée dans `Zehon/Charte/musique/` : `--musique` (champ
`MUSIQUE` du notebook). Elle est bouclée avec un fondu de 3 s, entre en 2 s,
sort en 3 s, et se règle par `--volume-musique` (défaut −26 dB, puis
−6 dB de plus quand la voix parle). **Mesuré le 30/09** sur la voix du sel,
avec une nappe à −14 LUFS : à −26 dB, la nappe finit **23 dB sous la
voix**. Faire écouter un extrait (`EXTRAIT` = `1-10`) avant le rendu
complet.

## Les sous-titres

- **Le `.srt`** est toujours écrit (vidéo entière et `--plan`) : le « texte
  dit » des scènes (orthographe du script : « 8 000 », « Duzdağı »), chaque
  mot calé sur `mots.json`, deux lignes de 42 caractères au plus. Il se
  fait donc dès le plan, ici, sans rendu.
- **Incrustés, en option** (`--sous-titres`) : quelques mots à la fois
  (34 caractères, 7 mots au plus) dans un bandeau sombre transparent, en
  bas au centre ; le mot prononcé passe en jaune doré. Les groupes coupent
  aux fins de phrase, aux pauses et aux changements de scène, sont
  équilibrés (jamais un petit mot seul en fin de groupe) et s'effacent
  pendant les titres. Le texte animé remonte de 120 px pour leur laisser
  la place.

Environnement : Python 3, `numpy`, `opencv-python-headless`, `Pillow`,
`ffmpeg`. Dans un conteneur Claude Code : `apt-get install -y ffmpeg` et
`pip install opencv-python-headless pillow numpy` s'ils manquent.

## Dans Claude Code : le plan, puis la lecture du verdict

Le connecteur Drive télécharge **au plus 10 Mo par fichier** et n'envoie
pas de gros fichier vers Drive (mesuré le 30/09/2026). Donc ici, on ne
télécharge jamais les pièces (images, clips, voix) : tout rendu, extrait
compris, se fait dans Colab ; ici, on fait le plan et on lit ce que Colab a
écrit.

1. **Le plan (toujours d'abord)** : télécharge en brut `03_scenes.md` et
   `voix/mots.json` dans un dossier de travail (`<travail>/voix/mots.json`),
   puis `python3 scripts/monter.py <travail> --plan --sans-fichiers`.
   Compare la liste des scènes à la liste Drive de `images/` et `clips/`.
   Donne à Franco, en 5 lignes : durée totale, pièces manquantes (numéros),
   scènes de plus de 10 s, scènes mal retrouvées dans la voix (moins de
   60 %). Le plan écrit aussi `<travail>/rendu/sous_titres.srt`.
2. **Un essai** : Franco met `1-10` dans `EXTRAIT` du lanceur et lance
   (5 min environ). Puis lecture comme ci-dessous.
3. **Après un rendu** (extrait ou vidéo entière), lis dans `rendu/` :
   - `verdict.json` (moins de 1 Ko : `pret`, `controle`, `avertissements`,
     `duree_s`, `rendu_s`, `code`, le nom du rapport) ;
   - les 6 images de `apercu/` (JPEG de 640 px : `1_debut`, `2_titre`,
     `3_plan_anime`, `4_sous_titres`, `5_texte_anime`, `6_fin` ; `N_milieu`
     quand le passage rendu n'a pas l'élément). **Regarde-les toi-même** :
     titre lisible, plan animé bien cadré, sous-titres, texte animé ;
   - **plus le rapport en entier** (`rapport.json`, des dizaines de Ko) :
     s'il faut un détail (une scène), télécharge-le sur disque et n'en
     affiche que la partie utile (`python3 -c` ou `jq`).

   Donne le contrôle et les avertissements. Si `"pret": false`, la vidéo
   ne se publie pas.

## Colab : un lanceur fixe, le vrai notebook dans le dépôt

Dans Drive, `Zehon/montage_zehon.ipynb` et `Zehon/voix_zehon.ipynb` sont des
**lanceurs** (`zehon/notebooks/lanceur_montage.ipynb`, `lanceur_voix.ipynb`) :
le formulaire de réglages, puis quelques lignes qui clonent le dépôt
(branche `BRANCHE`) et exécutent le vrai notebook (`montage_zehon.ipynb`,
`voix_zehon.ipynb`) avec `zehon/notebooks/lanceur.py`. **On ne recopie plus
rien dans Drive** : une correction poussée sert au lancement suivant. Un
réglage ajouté au notebook garde sa valeur par défaut (cellule marquée
`reglages`) tant que le lanceur ne l'affiche pas.

Le montage tourne sans GPU (le sel, 7 min 55 s : **42 min de rendu**, mesuré
le 30/09) : plan (arrêt net si une pièce manque), rendu sur le disque de
Colab, puis copie dans `rendu/` de la vidéo, du rapport, de `verdict.json` et
de `apercu/` (le `.srt` y est écrit directement). Le rapport et le verdict
gardent la branche, le commit et la durée du rendu (`rendu_s`).

## Les sessions du montage : où t'arrêter

Le montage est la **session 5** (modèle **Haiku 4.5** ; la table des
sessions et le format de l'arrêt sont dans la skill `content-maker`,
section « Les sessions »). Elle s'arrête deux fois :

1. **Après le plan** (et un essai `EXTRAIT` s'il est à faire) : Franco
   lance le rendu dans Colab (45 min environ). Arrête-toi, avec le bloc
   « ⏹️ Fin de la session », « Avant la suivante : lance le lanceur de
   montage dans Colab », et ce prompt de relance :
   `Zehon, vidéo <nn>_<sujet> : session 5, lis le verdict du rendu.`
   (plus la ligne `git fetch … && git checkout …` de la branche de travail).
2. **Après la lecture du verdict** : si `"pret": true`, la vidéo est
   finie ; la session suivante est la publication sur YouTube, ou le sujet
   de la vidéo d'après (session 1, **Sonnet 5.5**). Si `"pret": false`,
   reste dans la session pour corriger ; si c'est un bug de `monter.py`,
   arrête-toi et relance en **Opus 5.5** avec l'erreur dans la ligne de
   contexte.

## Ce qu'il faut dire à Franco

- Des recommandations, pas des options ; le mesuré séparé de l'hypothèse ;
  une question à la fois.
- Une image fixe plus de 10 s à l'écran est signalée : propose de couper
  la scène en deux dans `03_scenes.md` (avec un prompt d'image de plus,
  affiché en entier dans le chat).
- Une scène retrouvée à moins de 60 % dans la voix veut dire que le
  script lu et les scènes ne correspondent plus : à corriger avant de
  rendre.
