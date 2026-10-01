# Zehon — cahier des charges du nouveau système (29/09/2026)

**Pour la prochaine session.** Le setup de la chaîne est terminé (vision,
niche, angle, charte, nom). Cette session-là construit **le nouveau
système**. L'ancien pipeline (agents A2 à A7, Remotion, `new-short`,
`formats_video.py`, `voix_off.ipynb` tel quel) **ne sert pas** à Zehon.

Principe de Franco : **simplicité, contenu plus net.** L'ancien système
n'était « tout juste pas performant ».


> **Décision de Franco du 30/09/2026 : version « histoire simple ».** Les
> autres chaînes racontent des histoires qui éveillent la curiosité, sans
> s'attarder sur les preuves. Zehon fait de même : **plus de pièces à
> conviction, de cartels ni de statuts à l'écran**, tout en images Gemini ;
> une vraie photo seulement si elle se trouve en quelques minutes. **Un seul
> garde-fou, invisible** : les faits racontés sont justes (recherche
> légère, rien d'inventé). La ligne devient **« de la matière brute à
> l'objet »**. `content-maker` est passée en v3 en conséquence. Les
> mentions de preuves plus bas dans ce document sont **dépassées**.

---

## 1. Les fondations (toutes décidées par Franco le 29/09/2026)

| Sujet | Décision |
|---|---|
| **Nom** | **Zehon** (remplace Zoook, déjà utilisé par une marque d'électronique). **@zehon est pris** (petite chaîne, 135 abonnés) ; **@zehonfr** (retenu par Franco) et @zehon.fr sont libres selon l'API YouTube le 29/09. Vérifier le nom sur la base des marques de l'INPI avant de créer la chaîne |
| Langue | Français |
| **Ligne** | « De la matière brute à l'objet. » Chaque vidéo raconte comment une matière est devenue un objet du quotidien, de la préhistoire à aujourd'hui, et **montre les preuves** |
| Format | Vidéo longue en paysage d'environ 8 min (environ 1 480 mots), plus 1 à 2 Shorts ; 1 vidéo par semaine ; 20 h par semaine |
| Propriété | Chaîne et AdSense au nom d'une connaissance en France ; Franco est gestionnaire, avec un contrat écrit (à signer avant la première vidéo ; la voix n'est plus celle de Franco : voir la ligne « Voix ») |
| **Style** | La grammaire du genre (Zelan, Zenn), **en calme** : des histoires racontées posément, de légers mouvements de caméra de temps en temps, du texte animé sobre |
| Images | Générées par **Gemini** (Franco a plusieurs comptes) |
| Voix | ~~Clone de la voix de Franco~~ → **décision du 30/09 : une voix d'homme au ton narratif créée sur ElevenLabs**, clonée par Qwen3-TTS dans Colab (référence dans `Charte/voix/`). **À vérifier** : les conditions commerciales de l'offre ElevenLabs utilisée |
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
  apparaissent en fondu. Blanc cassé avec une ombre douce, sur un bandeau
  sombre transparent (sans lui, les dates disparaissaient sur les images à
  fond blanc : constaté sur le verre, 01/10) ; dates et lieux en chasse fixe. **Le jaune cerné de noir est réservé à la miniature.**
- **Pièces à conviction** : de **vraies photos** sous licence libre, avec
  un cartel (objet, lieu, date, méthode de datation, statut établi,
  probable ou hypothèse, crédit et licence). **On ne génère jamais une
  image qui imite un objet de fouille ou un document réel** : ce serait une
  fausse preuve.
- **Musique** : une nappe douce à bas volume (bibliothèque audio de YouTube).
- **Miniature** : le style du genre. Le bonhomme, l'objet, 2 à 3 mots en
  jaune cerné de noir.

## 3. Le déroulé d'une vidéo

**Mise à jour du 29/09 (fin de session)** : les étapes 1 à 4 et 8 sont
désormais faites par la skill **`content-maker`**, construite, testée et
validée par Franco (voir §10). Elle remplace le dossier `Instructions/`
prévu au départ.

| # | Étape | Qui / où | Entrée | Sortie (dans Drive) |
|---|---|---|---|---|
| 1 | Sujet et angle | `content-maker`, sur n'importe quel compte Claude (gratuit compris) | `Memoire/` | 3 sujets proposés ; Franco tranche (pause 1) |
| 2 | Recherche | `content-maker` | le sujet | `01_recherche.md` (pause 2) |
| 3 | Plan puis script | `content-maker` | `01_recherche.md` | `02_plan.md` (pause 3), `02_script.md` + `02_script_voix.txt` (pause 4) |
| 4 | Scènes et prompts | `content-maker` | `02_script.md` | `03_scenes.md` (scènes + prompts Gemini par lots de 10) |
| 5 | Images | Franco, dans Gemini | les prompts + la planche du bonhomme | `images/scene_001.png`… |
| 6 | Voix | Colab + Qwen3-TTS (GPU gratuit) | `02_script_voix.txt` + `ref.wav` | `voix.wav` + `mots.json` (horodatage mot à mot par Whisper) |
| 7 | Assemblage | **Claude Code web**, skill `video-maker` | tout le dossier | `rendu/video.mp4` |
| 8 | Publication | `content-maker` ; Franco publie | le script et les scènes | `04_publication.md` (titres, description, crédits **obligatoires**, miniature) |

## 4. L'arborescence Drive

```
Zehon/
├── LISEZMOI.md                   ← mode d'emploi pour Franco (1 page)
├── Memoire/                      ← à déposer au lancement de content-maker
│   ├── sujets.md                 ← faits, proposés, déjà traités ailleurs
│   ├── lexique.md                ← prononciations de la voix clonée
│   └── lecons.md                 ← chiffres à 24 h / 72 h / 7 j, leçons, débit mesuré
├── Charte/
│   ├── planche_bonhomme.png
│   └── exemples/
└── Videos/
    └── 01_sel/
        ├── 01_recherche.md  02_plan.md  02_script.md  02_script_voix.txt
        ├── 03_scenes.md  04_publication.md
        ├── images/  preuves/  voix/  rendu/
```

Les règles (ligne, charte, structure du script, format des scènes) vivent
dans la skill, pas dans Drive : une seule source, mise à jour en
réinstallant le fichier `.skill`.

## 5. Les règles du script (reprises dans `content-maker`, `references/etape3_script.md`)

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

> **Construite le 30/09/2026** (`zehon/video-maker/`), **sans HyperFrames** :
> Python (OpenCV, Pillow) + FFmpeg, le même script dans Claude Code (plan,
> extraits) et dans Colab (la vidéo entière, écrite dans Drive), parce que le
> connecteur Drive ne transfère pas plus de 10 Mo par fichier (mesuré). Les
> preuves et cartels ci-dessous sont dépassés (version « histoire simple ») ;
> les plans animés (`clips/anim_NNN.mp4`) et les titres sont en place. Détail
> et mesures : `CONTEXTE.md`, bloc du haut.

**Rôle** : lire un dossier de vidéo, valider, assembler, rendre. Elle
n'écrit ni le script ni les prompts.

| | |
|---|---|
| Entrées | `03_scenes.md`, `images/`, `preuves/`, `voix/voix.wav`, `voix/mots.json`, une musique (optionnelle) |
| Sorties | `rendu/video.mp4` en 1920×1080 à 30 i/s ; `rendu/short_1.mp4` en 1080×1920 (plus tard) ; un rapport (scènes, durées, avertissements) |
| Blocs | `scene-image` (zoom lent ou panoramique, fondu) ; `preuve` (photo, zoom vers un point, cartel avec statut et crédit) ; `titre-question` ; `texte-anime` (mots-clés, dates, chiffres) ; mixage voix et musique, avec la musique qui baisse sous la voix |
| Garde-fous | refuser une scène sans image ; refuser une preuve sans crédit ni licence, ou marquée « À TROUVER » ; avertir quand une image reste plus de 10 s à l'écran |
| Contrôle avant publication | Après le rendu, un contrôle automatique : piste audio présente, pas de silence (volume moyen sous −60 dB), pas de saturation (crête au-dessus de −0,5 dB), 1920×1080, durée cohérente avec la voix. **Un rendu n'est fini que si ce contrôle passe.** Idée et seuils repris de `scripts/preflight.py` du plugin *AI YouTube OS* (channelroom-studio, licence MIT, lu le 29/09/2026) : le reprendre en gardant sa mention de licence |
| Environnement | **Mesuré dans ce conteneur le 29/09** : Node 22.22 et Chromium présents ; **FFmpeg absent**, à ajouter au script de setup de l'environnement |
| Fichiers | Lus depuis Drive par le connecteur Google Drive (branché dans cette session). **Hypothèse** : renvoyer un MP4 de 100 à 300 Mo vers Drive par le connecteur. À vérifier, avec une solution de secours (fichier envoyé dans la conversation) |

**HyperFrames** ([heygen-com/hyperframes](https://github.com/heygen-com/hyperframes),
Apache 2.0) : la vidéo s'écrit en HTML avec des attributs `data-start` et
`data-duration` ; le rendu passe par Chromium headless puis FFmpeg, et il
est déterministe. Il fournit des skills Claude Code
(`npx skills add heygen-com/hyperframes`) : **à évaluer avant d'écrire nos
propres blocs**.

## 8. Ce qu'il faut vérifier ou trancher dans la prochaine session

**Vérifié le 29/09** (documentation officielle) : les skills fonctionnent
sur un compte Claude **gratuit** (*Customize > Skills*, avec *Settings >
Capabilities > Code execution and file creation* activé) ; le connecteur
Google Drive est ouvert à tous les plans sur claude.ai, en lecture
(recherche et lecture de fichiers).

**Hypothèses à vérifier** (dans cet ordre) :
1. `content-maker` sur un **vrai compte gratuit** : les tests ont tourné
   dans Claude Code, et un compte gratuit peut utiliser un modèle plus
   petit. Essai sur le sel, de la recherche aux scènes.
2. Le premier rendu HyperFrames dans Claude Code web (FFmpeg compris), avec
   3 images, une voix de test et un texte animé.
3. Gemini tient-il le bonhomme d'une image à l'autre avec une planche de
   référence ? On le mesure sur 5 images test, en comptant les rejets.
4. Les quotas de Gemini, et **les conditions d'utilisation de Google**
   pour un usage réparti sur plusieurs comptes.
5. La voix : un notebook Colab **simplifié** (le clone Qwen3-TTS et Whisper
   en français), repris de `notebooks/voix_off.ipynb`.

**À trancher par Franco** :
- **La suppression des anciennes skills** : la chaîne IA (anglais, Shorts)
  en dépend (`short-*`, `new-short`, `short-state`, `short-publier`).
  **Recommandation** : ne rien supprimer avant que Zehon ait publié sa
  première vidéo avec le nouveau système.
- Le budget mensuel (estimation : environ 35 $ si les images sont payées ;
  près de 0 si les quotas gratuits de Gemini suffisent. **Hypothèse.**)
- Les deux pièces à conviction du sel encore **À TROUVER** : la coupe de
  Poiana Slatinei (autorisation d'O. Weller ou schéma redessiné) et une page
  de Pline, *HN* 31.89.
- La vérification du nom Zehon sur la base des marques de l'INPI.

## 9. Ordre recommandé pour la prochaine session

1. Installer `content-maker` sur un compte gratuit et faire l'essai réel
   sur le sel (vérification 1) : environ 1 h. Corriger la skill si besoin.
2. **L'arborescence Drive** (§4), avec `Memoire/` amorcé (le sel dans
   `sujets.md`, les noms du sel dans `lexique.md`) : environ 1 h.
3. La skill `video-maker` : socle HyperFrames et premier rendu (environ
   6 h), puis les blocs (environ 10 à 14 h), avec le contrôle avant
   publication.
4. Le notebook de voix simplifié : environ 2 h.

**Total estimé** : environ 20 à 25 h (**hypothèse**). Le risque se
concentre sur le rendu HyperFrames et la cohérence du bonhomme sous Gemini.

## 10. La skill `content-maker` (construite et validée le 29/09)

- **Où** : `zehon/content-maker/` (sources), `zehon/content-maker.skill`
  (le fichier à installer). Hors de `skills/`, que l'ancien système recopie
  dans `.claude/skills/`.
- **Ce qu'elle fait** : 5 étapes (sujet, recherche, plan puis script,
  scènes et prompts, publication), 4 pauses, reprise d'un compte à l'autre
  en déduisant l'étape des fichiers déposés, mémoire dans `Memoire/`,
  vérificateur `scripts/verifier.py` (longueurs, question du hook, appel à
  s'abonner, version voix, format et continuité des scènes, preuves « À
  TROUVER »).
- **Mesuré** (3 cas de test, avec et sans la skill, dans Claude Code) :
  96 % des vérifications passent avec la v2 (92 % en v1), 26 % sans la
  skill. Coût : environ 450 s et 47 000 tokens de plus par tâche.
- **Repris du plugin *AI YouTube OS*** (channelroom-studio, MIT, lu le
  29/09) : la définition du « fini », la discipline des chiffres (24 h /
  72 h / 7 j, rien avant 3 vidéos, une expérience à la fois). Le contrôle
  avant publication (`preflight.py`) est pour `video-maker` (§7).
- **Résultats des tests** : `zehon/content-maker-workspace/` (non versionné).
