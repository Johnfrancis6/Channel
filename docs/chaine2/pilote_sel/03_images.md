# Images — pilote « le sel » (29/09/2026)

## Décisions de Franco (29/09/2026)

| Sujet | Décision |
|---|---|
| Moteur de rendu | **HyperFrames** (HTML → MP4, Apache 2.0, [heygen-com/hyperframes](https://github.com/heygen-com/hyperframes)) **pour la chaîne 2**, dès la pilote. La chaîne IA reste sur Remotion ; sa migration se décidera après la pilote |
| Style | **Le même que Zelan et Zenn, entièrement** : bonhomme à tête ronde, décors illustrés, miniature du genre (texte jaune cerné de noir compris), **scènes en images générées par IA** |
| Générateur d'images | **Gemini** (famille « Nano Banana ») |
| Voix | Clone de la voix de Franco (Qwen3-TTS) |

Ces décisions **remplacent** la recommandation du 29/09 (une charte hors du
genre). Mes recommandations précédentes et les mesures qui les motivaient
restent dans l'historique git de ce fichier et dans
[`../concurrents_2026-09-29.md`](../concurrents_2026-09-29.md).

**Le risque, mesuré** : les clones qui copient tout le genre s'effondrent.
En anglais, la médiane est passée de 1,1 M à 6,5 k vues entre avril et août
2026 ; en français, 10 chaînes ont une médiane sous 1 k. **Ce qui nous
distingue désormais**, ce sont le sujet (la transformation), le script (les
questions d'enquête, les marqueurs d'incertitude) et **les pièces à
conviction**.

**Une règle maintenue, qui relève de l'exactitude et non du style** : les
pièces à conviction restent de **vraies photos** sous licence libre. On ne
génère **jamais** une image qui imite un objet de fouille, un document ou un
site réel : ce serait une fausse preuve. Pour lever cette règle, il faut une
décision explicite de Franco.

---

## 1. La grammaire à reproduire (mesurée sur les miniatures du genre)

- Un **bonhomme blanc à tête ronde**, en pagne, expressif, le même d'une
  scène à l'autre.
- Des **décors illustrés chauds** : savane, grotte, feu, village.
- Des **miniatures** avec 2 à 3 mots en capitales jaunes cernées de noir.

**À produire avant la pilote** (environ 2 h, avec Gemini) :
1. une **planche de référence du bonhomme** : face, profil, 4 expressions,
   fond neutre. Elle sert d'image de référence à **chaque** génération. Sans
   elle, le personnage change d'une scène à l'autre ;
2. un **prompt de style** fixe (trait, palette, lumière), écrit dans
   `00_Profil/charte_visuelle/` de la racine de la chaîne 2 ;
3. **3 à 5 images test** sur des scènes du sel (source salée, feu, mine).
   On vérifie la cohérence du personnage avant de lancer une vidéo entière.

**Hypothèse** : Gemini tient le personnage avec une seule image de
référence. À mesurer sur les images test : on compte les images rejetées.

**Pour nous distinguer sans quitter le genre** (recommandation, que Franco
peut refuser) : ne pas **copier** de composition existante. Zelan reprend
jusqu'aux compositions d'Ink Explainer (mesuré). La vidéo et la miniature
suivent le genre, mais les scènes et les compositions restent les nôtres.

---

## 2. Miniature

Grammaire du genre (décision) : le bonhomme, l'objet et 2 à 3 mots en jaune
cerné de noir.

**Proposition pour le sel** : le bonhomme tient à deux mains un **bloc de sel**
comme un trésor, à côté d'une **salière moderne**. Texte (Franco tranche) :
*PLUS CHER QUE L'OR ?* (à éviter : c'est faux au sens strict), *UN TRÉSOR*,
*7 000 ANS DE SEL*. **Recommandation : *UN TRÉSOR*.** C'est vrai, et ça
porte le paradoxe.

**Mesuré** : la meilleure miniature de Zelan (*le fer*, 435 k) est la seule
sans bonhomme : deux mains, un minerai, une lame. **Recommandation** : faire
les deux variantes (avec le bonhomme ; mains, sel et salière seuls) et les
tester avec l'outil de test de miniatures de YouTube dès la pilote.

---

## 3. Pièces à conviction : les vraies photos

Mesuré sur Wikimedia Commons le 29/09 :

| Q | Pièce | Fichier Commons | Licence | Statut |
|---|---|---|---|---|
| Q1 | Poiana Slatinei (6050 av. J.-C.) | **Aucune photo libre trouvée** | — | **Manque.** Dans l'ordre : (a) une photo de la source salée de Lunca (deuxième recherche en cours) ; (b) demander à O. Weller (CNRS) l'autorisation d'utiliser une figure d'*Antiquity* 2005 ; (c) une coupe stratigraphique redessinée, avec la citation « d'après Weller & Dumitroaia 2005 » |
| Q2 | Tessons de briquetage de la Seille | `Briquetage.jpg`, `Récipients.jpg`, `Fourneaux.jpg` | CC BY-SA 4.0 (compte « User:Laur… », auteur exact à relever) | **Trouvé** |
| Q3 | Escalier de Hallstatt (1344 av. J.-C.) | `Escalier de l'âge du bronze, mines de sel de Hallstatt. XIVe av. J.-C.jpg` | CC BY-SA 3.0, Andreas W. Rausch | **Trouvé**. En plus : `Casquet de pell, segle XIII aC. Mina de sal de Hallstatt.JPG` (bonnet en peau, CC BY-SA 3.0, Joanbanjo) |
| Q4 | Saline royale d'Arc-et-Senans ; poêles de la Grande Saline de Salins (où l'on faisait bouillir la saumure) | `Berniers Ouest, Saline Royale, Arc-et-Senans, 2026.jpg` ; `Salines de Salins - Poele 1.JPG` (et Poele 2, Poele 3) | CC0 (DimiTalen) ; CC BY-SA 3.0 (photographe à relever) | **Trouvé** |
| Q4 bis | Pline, *HN* 31 (le mythe du salaire) | Recherche en cours (manuscrit ou incunable, domaine public) | — | À faire |

**Obligation CC BY-SA** : le crédit (auteur, licence) est visible **à
l'écran pendant la pièce**, et repris dans la description de la vidéo.

---

## 4. Ce qui manque pour montrer une transformation et une pièce à conviction

Le rendu part de zéro sous HyperFrames. Avec des scènes en images IA, les
décors codés disparaissent. Restent : **l'image qui bouge**, la **preuve**
et le **fil du procédé**. Les estimations sont des **hypothèses** : rien
n'est encore mesuré sous HyperFrames.

| # | Bloc HyperFrames | Ce qu'il montre | Paramètres | Effort estimé |
|---|---|---|---|---|
| 4.1 | **`scene-image`** | L'image générée en plein cadre, avec un mouvement lent (zoom, panoramique) et un fondu vers la suivante. C'est **80 % de la vidéo** | `image`, `mouvement` (zoom avant, zoom arrière, panoramique gauche ou droite), `duree` | 3 à 4 h |
| 4.2 | **`piece-a-conviction`** | Une vraie photo, un zoom vers un détail, puis un **cartel** : objet, lieu, date, **méthode de datation**, tampon « établi », « probable » ou « hypothèse », **crédit et licence** toujours visibles | `photo`, `point_zoom`, `objet`, `lieu`, `date`, `methode`, `statut`, `credit`, `licence` | 5 à 6 h |
| 4.3 | **`chaine-transformation`** | Un bandeau posé sur l'image : eau salée → feu → pain de sel → poudre, avec l'étape en cours allumée. Il revient à chaque question comme **fil rouge** | `etapes[]`, `active` | 3 à 4 h (plus simple qu'en plein cadre : c'est une surcouche) |
| 4.4 | **`frise`** | Un curseur sur une frise de −10 000 à aujourd'hui. Sert aux **retours au présent** | `debut`, `fin`, `reperes[]`, `curseur` | 3 à 4 h |
| 4.5 | **Sous-titres** | Les mots horodatés par Whisper, le mot en cours en relief. HyperFrames fournit une skill de sous-titres, à évaluer d'abord | `mots` | 2 à 3 h |
| 4.6 | `titre-question`, `chiffre-compare` | L'ouverture des questions Q1 à Q4 ; les comparaisons de quantités (33 kg / 3 kg) | voir le dossier | 2 à 3 h |

**Total des blocs : environ 18 à 24 h.** La carte (`carte-lieu`) sort de la
liste : Gemini peut dessiner une carte dans le style du genre. Les lieux
restent donnés par le cartel de la pièce à conviction, qui est une vraie
source.

---

## 5. Ce qui s'ajoute au pipeline

**Mesuré** (lecture du code le 29/09) : Remotion n'est branché qu'en bout de
chaîne, dans A7 (`construire_props.py`, `rendre_video.py`) et dans deux
outils (`generer_apercus.py`, `capturer_web.py`). De A2 à A6, rien ne dépend
du moteur de rendu.

1. **Génération d'images** : un script `generer_images.py` qui lit le
   storyboard d'A6 (un prompt par scène), appelle l'API Gemini avec la
   planche de référence, met en cache, relance en cas d'échec et consigne le
   coût. Il faut une clé `GEMINI_API_KEY` (**absente de l'environnement au
   29/09**, à ajouter aux secrets). Environ 4 à 6 h.
2. **A6 (Designer)** : écrire un prompt d'image par scène (le prompt de
   style + le bonhomme + l'action), à la place du choix d'un composant
   Remotion. Pour la pilote, un mode propre à la chaîne 2 dans son SKILL.md,
   ou un passage à la main. Environ 2 h.
3. **Rendu** : un répertoire `hyperframes/` séparé de `composants/`, avec
   le projet HyperFrames, les blocs du §4 et `storyboard_vers_html.py`
   (storyboard + mots horodatés → composition HTML). Rendu en `--root`
   explicite. Socle : environ 6 h (FFmpeg à installer : absent du
   conteneur ; Node 22.22 présent).

Ce n'est pas du code multi-chaînes : ni `--chaine` ni `profil_chaine.json`.

---

## 6. Budget

**Générateur : Gemini** (décision). **Le montant n'est pas fixé.**
Estimation (**hypothèse**, le nombre d'images de Zelan n'est pas mesuré) :
environ 100 images par vidéo de 8 min, fois 2 pour les reprises, à environ
0,04 $ l'image. Cela fait environ 8 $ par vidéo, soit **environ 35 $ par mois**
à 4 vidéos. Voix : Colab (gratuit, ou Colab Pro si le GPU gratuit
manque). Musique : la bibliothèque audio de YouTube (gratuite).
