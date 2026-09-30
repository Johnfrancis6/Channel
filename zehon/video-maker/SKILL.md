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
contrôle) et `rendu/sous_titres.srt` (vidéo entière et `--plan`), à déposer
sur YouTube avec la vidéo.

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

## Dans Claude Code : le plan, puis un extrait

Le connecteur Drive télécharge **au plus 10 Mo par fichier** et n'envoie
pas de gros fichier vers Drive (mesuré le 30/09/2026). Donc ici, on
vérifie et on rend des extraits ; la vidéo entière se rend dans Colab
(voir plus bas).

1. **Le plan (toujours d'abord)** : télécharge en brut `03_scenes.md` et
   `voix/mots.json` dans un dossier de travail (`<travail>/voix/mots.json`),
   puis `python3 scripts/monter.py <travail> --plan --sans-fichiers`.
   Compare la liste des scènes à la liste Drive de `images/` et `clips/`.
   Donne à Franco, en 5 lignes : durée totale, pièces manquantes (numéros),
   scènes de plus de 10 s, scènes mal retrouvées dans la voix (moins de
   60 %). Le plan écrit aussi `<travail>/rendu/sous_titres.srt` (pour le
   relire ici ; le rendu dans Colab l'écrit dans Drive).
2. **Un extrait** (`--scenes 1-10`) : télécharge les images et clips de ces
   scènes dans `<travail>/images/` et `<travail>/clips/` (chaque résultat
   du connecteur est enregistré sur disque : décode son champ `content`,
   en base64), et les phrases de voix correspondantes depuis
   `voix/cache/` (`0001_….wav`, `0002_…` : les N premières, sans trou).
   Puis `python3 scripts/voix_depuis_cache.py <travail>` et
   `python3 scripts/monter.py <travail> --scenes 1-10`.
   Envoie la vidéo à Franco dans la conversation, et **regarde toi-même
   quelques images** (`ffmpeg -ss <t> -i … -frames:v 1`) : fondus, texte
   animé, titre, plans animés.

## La vidéo entière : dans Colab

`monter.py` tourne tel quel dans Colab, où Drive est monté : il lit le
dossier de la vidéo et écrit `rendu/video.mp4` directement dans Drive,
sans limite de taille. *(Le notebook `montage_zehon.ipynb` qui l'emballe
est la prochaine étape : tant qu'il n'existe pas, dis-le simplement.)*

Quand Franco a rendu la vidéo : lis `rendu/rapport.json` en brut, et
donne le résultat du contrôle et les avertissements. Si `"pret": false`,
la vidéo ne se publie pas.

## Prévu, pas encore fait

- Le notebook Colab `montage_zehon.ipynb`, pour rendre la vidéo entière.

## Ce qu'il faut dire à Franco

- Des recommandations, pas des options ; le mesuré séparé de l'hypothèse ;
  une question à la fois.
- Une image fixe plus de 10 s à l'écran est signalée : propose de couper
  la scène en deux dans `03_scenes.md` (avec un prompt d'image de plus,
  affiché en entier dans le chat).
- Une scène retrouvée à moins de 60 % dans la voix veut dire que le
  script lu et les scènes ne correspondent plus : à corriger avant de
  rendre.
