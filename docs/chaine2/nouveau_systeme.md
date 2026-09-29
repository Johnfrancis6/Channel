# Zehon — cahier des charges du nouveau système (29/09/2026)

**Pour la prochaine session.** Le setup de la chaîne est terminé (vision,
niche, angle, charte, nom). Cette session-là construit **le nouveau
système**. L'ancien pipeline (agents A2 à A7, Remotion, `new-short`,
`formats_video.py`, `voix_off.ipynb` tel quel) **ne sert pas** à Zehon.

Principe de Franco : **simplicité, contenu plus net.** L'ancien système
n'était « tout juste pas performant ».

---

## 1. Les fondations (toutes décidées par Franco le 29/09/2026)

| Sujet | Décision |
|---|---|
| **Nom** | **Zehon** (remplace Zoook, déjà utilisé par une marque d'électronique). **@zehon est pris** (petite chaîne, 135 abonnés) ; **@zehonfr** et @zehon.fr sont libres selon l'API YouTube le 29/09. Vérifier le nom sur la base des marques de l'INPI avant de créer la chaîne |
| Langue | Français |
| **Ligne** | « De la matière brute à l'objet, et comment on le sait. » Chaque vidéo raconte comment une matière est devenue un objet du quotidien, de la préhistoire à aujourd'hui, et **montre les preuves** |
| Format | Vidéo longue en paysage d'environ 8 min (environ 1 480 mots), plus 1 à 2 Shorts ; 1 vidéo par semaine ; 20 h par semaine |
| Propriété | Chaîne et AdSense au nom d'une connaissance en France ; Franco est gestionnaire, avec un contrat écrit (à signer avant la première vidéo ; il doit couvrir **les droits sur la voix de Franco**) |
| **Style** | La grammaire du genre (Zelan, Zenn), **en calme** : des histoires racontées posément, de légers mouvements de caméra de temps en temps, du texte animé sobre |
| Images | Générées par **Gemini** (Franco a plusieurs comptes) |
| Voix | **Clone de la voix de Franco** (Qwen3-TTS) |
| Première vidéo | **Le sel** (dossier prêt : [`pilote_sel/01_recherche.md`](pilote_sel/01_recherche.md), plan : [`pilote_sel/02_plan_script.md`](pilote_sel/02_plan_script.md)) |
| Assemblage | Skill **`video-maker`** (HyperFrames), dans **Claude Code web** |
| Anciennes skills | Franco les supprimera (voir §7, un point à trancher avant) |

## 2. La charte (validée par Franco le 29/09)

- **Personnage** : le bonhomme à tête ronde du genre, toujours généré à
  partir de **la même planche de référence** (face, profil, 4 expressions).
- **Décors** : illustrés, lumière chaude. La palette vient de la matière
  du sujet (pour le sel : blancs, gris de saumure, ocre de terre cuite).
- **Caméra** : un zoom lent de 3 à 5 % sur chaque image, un panoramique
  lent de temps en temps, des fondus de 0,5 à 1 s. Pas de coupe sèche, pas
  de tremblement.
- **Rythme** : une image toutes les 6 à 8 s, soit 60 à 80 images pour 8 min
  (**hypothèse** : le rythme de Zelan n'est pas mesuré).
- **Texte animé** : seulement les mots-clés, les dates et les chiffres, qui
  apparaissent en fondu. Blanc cassé avec une ombre douce ; dates et lieux
  en chasse fixe. **Le jaune cerné de noir est réservé à la miniature.**
- **Pièces à conviction** : de **vraies photos** sous licence libre, avec
  un cartel (objet, lieu, date, méthode de datation, statut établi,
  probable ou hypothèse, crédit et licence). **On ne génère jamais une
  image qui imite un objet de fouille ou un document réel** : ce serait une
  fausse preuve.
- **Musique** : une nappe douce à bas volume (bibliothèque audio de YouTube).
- **Miniature** : le style du genre. Le bonhomme, l'objet, 2 à 3 mots en
  jaune cerné de noir.

## 3. Le déroulé d'une vidéo

| # | Étape | Qui / où | Entrée | Sortie (dans Drive) |
|---|---|---|---|---|
| 1 | Choix du sujet | Franco, aidé par n'importe quel Claude | `Sujets/` | le dossier de la vidéo |
| 2 | Recherche | N'importe quel compte Claude, **gratuit compris** | les instructions | `01_recherche.md` : sources, statuts, pièces à conviction |
| 3 | Script | idem : Claude pose ses questions, puis rédige | `01_recherche.md` + les règles | `02_script.md` |
| 4 | Scènes et prompts | idem | `02_script.md` + la charte | `03_scenes.md` : une ligne par scène, avec le texte dit, le type, le prompt d'image, le mouvement et le texte animé |
| 5 | Images | Franco, dans Gemini | les prompts + la planche du bonhomme | `images/scene_001.png`… |
| 6 | Voix | Colab + Qwen3-TTS (GPU gratuit) | `02_script.md` + `ref.wav` | `voix.wav` + `mots.json` (horodatage mot à mot par Whisper) |
| 7 | Assemblage | **Claude Code web**, skill `video-maker` | tout le dossier | `rendu/video.mp4` (+ les Shorts) |
| 8 | Miniature, titre, description | Claude + Gemini ; Franco publie | le script | `publication.md` (les crédits CC BY-SA y sont **obligatoires**) |

## 4. L'arborescence Drive proposée

```
Zehon/
├── LISEZMOI.md                   ← mode d'emploi pour Franco (1 page)
├── Instructions/
│   ├── 00_DEMARRAGE.md           ← le texte à coller dans n'importe quel Claude
│   ├── 01_chaine.md              ← ligne, public, ton, ce qu'on ne fait pas
│   ├── 02_recherche.md           ← sources, statuts, pièces à conviction, Commons
│   ├── 03_script.md              ← la structure mesurée (§5), avec un exemple
│   ├── 04_scenes_et_prompts.md   ← le format de 03_scenes.md, les règles de prompt
│   ├── 05_charte.md              ← §2, avec le prompt de style fixe
│   └── 06_publication.md         ← titre, description, crédits, miniature
├── Charte/
│   ├── planche_bonhomme.png
│   └── exemples/
├── Sujets/
│   └── sujets.md                 ← propositions ; Franco tranche
├── Videos/
│   └── 01_sel/
│       ├── 01_recherche.md  02_script.md  03_scenes.md
│       ├── images/  preuves/  voix/  rendu/
│       └── publication.md
└── Suivi/
    └── lecons.md                 ← ce que chaque vidéo a appris (vues, rétention)
```

**Règle de conception** : chaque fichier d'instructions **tient seul** et
reste court. Un compte gratuit a peu de contexte et peu de messages
(**hypothèse** sur les limites exactes, à vérifier). `00_DEMARRAGE.md` dit à
Claude quels fichiers lire à chaque étape, et lui demande de **poser ses
questions une par une** avant d'écrire.

## 5. Les règles du script (à reprendre dans `03_script.md`)

**Mesuré sur *le fer* de Zelan** (435 k vues, une seule vidéo) :
- **3,09 mots/s**, 1 547 mots en 500 s ; phrase médiane de 12 mots ;
- un **hook de 30 s** en 8 phrases : un objet de ton quotidien, puis un
  paradoxe. La question tombe à la 9e phrase ;
- **10 temps de 55 à 255 mots** (123 en moyenne), en fil chronologique.
  Chaque temps finit sur un obstacle, que le suivant lève. Le mot charnière
  est **« Sauf que »** ;
- le **tutoiement** et **5 à 6 retours au présent** ;
- **pas d'appel à s'abonner** ; la fin est une question ouverte.

**Notre structure** (recommandation) : environ 1 480 mots, **3 à 4 questions
d'enquête** en 8 à 10 temps, et chaque question se referme sur une **pièce à
conviction montrée**. Les statuts du dossier passent à l'oral : « on sait
que… » (établi), « on pense que… » (probable), « personne ne sait
vraiment… » (hypothèse).

**Mesuré le 29/09 (API, descriptions)** : depuis le 11/09, Zelan cite ses
sources en description sur 11 vidéos sur 12. **Notre différence ne peut
pas être « on cite des sources »** : elle se joue **à l'écran** (les pièces,
leurs statuts) **et à l'oral** (des moments « comment on le sait »). Zelan
publie tous les 2 jours et vient d'attaquer les métaux (*le cuivre*, 29/09).
**Avant chaque script, on vérifie que Zelan n'a pas déjà pris le même
paradoxe** : c'est arrivé pour le sel.

**Encore à mesurer** (bloqué depuis le conteneur : YouTube renvoie
`RequestBlocked` pour les adresses cloud) : la comparaison d'un succès et
d'un raté (*la journée* 277 k, *l'eau sale* 127 k, *le sucre* 3,6 k), *le
sel* de Zelan, *le sel rose* de Je T'explique Comment et Zenn.
**Recommandation** : demander à **Gemini** la transcription à partir du lien
YouTube, la déposer dans `Suivi/`, et faire la comparaison dans une session
Claude.

## 6. `03_scenes.md` : le contrat entre le script et `video-maker`

C'est le seul format que les deux côtés doivent partager. **Recommandation :
un tableau Markdown**, lisible et modifiable à la main dans Drive, que
`video-maker` valide avant le rendu (en cas d'erreur, un message clair qui
nomme la ligne).

| n° | type | texte dit (extrait exact du script) | image | mouvement | texte animé | preuve (si type = preuve) |
|---|---|---|---|---|---|---|
| 1 | image | « Regarde la salière sur ta table. » | scene_001.png | zoom_avant | — | — |
| 14 | preuve | « Cet escalier a été abattu en 1344 avant notre ère. » | preuves/hallstatt_escalier.jpg | zoom_vers:0.62,0.40 | 1344 av. J.-C. | Hallstatt · dendrochronologie · ÉTABLI · A. W. Rausch, CC BY-SA 3.0 |

- **type** : `image` (Gemini), `preuve` (vraie photo + cartel), `titre`
  (ouverture d'une question d'enquête).
- **Les durées ne sont pas écrites à la main** : `video-maker` les calcule
  en alignant le « texte dit » de chaque scène sur `mots.json`.
- Le prompt d'image de chaque scène vit dans une section à part du même
  fichier (une scène = un prompt), pour que Franco le copie dans Gemini.

## 7. La skill `video-maker` (Claude Code web, HyperFrames)

**Rôle** : lire un dossier de vidéo, valider, assembler, rendre. Elle
n'écrit ni le script ni les prompts.

| | |
|---|---|
| Entrées | `03_scenes.md`, `images/`, `preuves/`, `voix/voix.wav`, `voix/mots.json`, une musique (optionnelle) |
| Sorties | `rendu/video.mp4` en 1920×1080 à 30 i/s ; `rendu/short_1.mp4` en 1080×1920 (plus tard) ; un rapport (scènes, durées, avertissements) |
| Blocs | `scene-image` (zoom lent ou panoramique, fondu) ; `preuve` (photo, zoom vers un point, cartel avec statut et crédit) ; `titre-question` ; `texte-anime` (mots-clés, dates, chiffres) ; mixage voix et musique, avec la musique qui baisse sous la voix |
| Garde-fous | refuser une scène sans image ; refuser une preuve sans crédit ni licence ; avertir quand une image reste plus de 10 s à l'écran |
| Environnement | **Mesuré dans ce conteneur le 29/09** : Node 22.22 et Chromium présents ; **FFmpeg absent**, à ajouter au script de setup de l'environnement |
| Fichiers | Lus depuis Drive par le connecteur Google Drive (branché dans cette session). **Hypothèse** : renvoyer un MP4 de 100 à 300 Mo vers Drive par le connecteur. À vérifier, avec une solution de secours (fichier envoyé dans la conversation) |

**HyperFrames** ([heygen-com/hyperframes](https://github.com/heygen-com/hyperframes),
Apache 2.0) : la vidéo s'écrit en HTML avec des attributs `data-start` et
`data-duration` ; le rendu passe par Chromium headless puis FFmpeg, et il
est déterministe. Il fournit des skills Claude Code
(`npx skills add heygen-com/hyperframes`) : **à évaluer avant d'écrire nos
propres blocs**.

## 8. Ce qu'il faut vérifier ou trancher dans la prochaine session

**Hypothèses à vérifier** (dans cet ordre) :
1. Un compte Claude **gratuit** peut-il lire Drive par le connecteur ? Si
   ce n'est pas le cas, les instructions se collent ou se déposent en
   fichier. C'est ce qui fixe la forme de `00_DEMARRAGE.md`.
2. Le premier rendu HyperFrames dans Claude Code web (FFmpeg compris), avec
   3 images, une voix de test et un texte animé.
3. Gemini tient-il le bonhomme d'une image à l'autre avec une planche de
   référence ? On le mesure sur 5 images test, en comptant les rejets.
4. Les quotas de Gemini, et **les conditions d'utilisation de Google**
   pour un usage réparti sur plusieurs comptes.
5. La voix : un notebook Colab **simplifié** (le clone Qwen3-TTS et Whisper
   en français), repris de `notebooks/voix_off.ipynb`, qui n'en garde que
   l'essentiel.

**À trancher par Franco** :
- **La suppression des anciennes skills** : la chaîne IA (anglais, Shorts)
  en dépend (`short-*`, `new-short`, `short-state`, `short-publier`). Soit
  on la migre sur le nouveau système, soit elle s'arrête, soit on garde ses
  skills. **Recommandation** : ne rien supprimer avant que Zehon ait publié
  sa première vidéo avec le nouveau système.
- Le budget mensuel (estimation : environ 35 $ si les images sont payées ;
  près de 0 si les quotas gratuits de Gemini suffisent. **Hypothèse.**)
- Le texte de la miniature du sel (proposition : *UN TRÉSOR*).

## 9. Ordre recommandé pour la prochaine session

1. Le connecteur Drive en compte gratuit (vérification 1) : 15 min. Il
   décide de la forme des instructions.
2. **L'arborescence Drive et les fichiers d'instructions** (§4 et §5), avec
   le sel comme exemple rempli : environ 4 à 5 h.
3. Un essai à blanc avec un compte gratuit sur le sel (recherche déjà
   faite, script, puis scènes) : environ 1 h. On corrige les instructions.
4. La skill `video-maker` : socle HyperFrames et premier rendu (environ
   6 h), puis les blocs (environ 10 à 14 h).
5. Le notebook de voix simplifié : environ 2 h.

**Total estimé** : environ 25 à 30 h, soit 1 semaine et demie à 20 h par
semaine (**hypothèse**). Le risque se concentre sur deux postes non
mesurés : le rendu HyperFrames et la cohérence du bonhomme sous Gemini.
