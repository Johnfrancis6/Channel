# Étape 5 — Publication

**But** : `04_publication.md`, tout ce que Franco colle dans YouTube Studio,
plus les prompts de miniature. C'est la dernière étape : termine par la
mise à jour de la mémoire (voir `memoire.md`).

## Titres : 3 propositions, une recommandée

- **Une question**, en moins de 60 caractères. C'est la forme des succès
  mesurés du genre (*Comment nos ancêtres ont-ils découvert le fer ?*,
  435 k vues).
- Le titre promet **le procédé**, pas la « découverte » (*le sucre* et *le
  sel* de Zelan, formulés en « découverte », ont fait 3,6 k et 5,9 k).
- Pas de majuscules criées, pas de fausse promesse. Si le titre pose une
  question, la vidéo y répond.
- **Ne reprends pas mot pour mot la formule de Zelan** (« Comment nos
  ancêtres ont-ils… ») : la forme question marche, mais la copier fait de
  Zehon un clone de plus. Centre le titre sur l'objet et son paradoxe
  (« Le sel valait une fortune. Pourquoi plus rien ? »).
- Recommande-en un, en une phrase.

## Description

```markdown
<2 lignes d'accroche : l'objet, le paradoxe, sans divulgâcher la réponse>

CHAPITRES
00:00 <hook>
--:-- Q1 <titre court>
--:-- Q2 …
--:-- Q3 …
--:-- Q4 …
(les horodatages se remplissent après l'enregistrement de la voix)

POUR ALLER PLUS LOIN
▸ <2 à 4 sources de la recherche>

CRÉDITS DES PHOTOS (seulement si la vidéo contient de vraies photos)
▸ <objet> — <auteur>, <licence>, via Wikimedia Commons
  (**obligatoire** en CC BY et CC BY-SA)

Illustrations générées par IA.
```

## Miniature

**4 à 5 prompts, chacun sur une idée différente**, puis Franco en teste 3
dans l'outil de test de miniatures de YouTube Studio (3 au maximum).

**Le style qui marche** (mesuré le 30/09 sur les meilleures miniatures de
Zelan : *le fer* 438 k vues, *la journée* 279 k, *l'eau sale* 128 k ; sa
miniature du *sel*, chargée et sans émotion forte, 6 k) :
- **dessin animé vif** : gros contours noirs, couleurs saturées, ciel bleu,
  lumière de plein jour, fort contraste. **Jamais sombre ni réaliste** :
  les deux premières variantes du sel (fond sombre, mains réalistes) ont
  été jugées « pas accrocheuses » par Franco ;
- **un gros texte en haut**, 2 à 4 mots en capitales blanches ou jaunes
  cernées de noir, souvent une question ou une provocation (« IL A BU
  ÇA », « PAS DE BOULOT ? ») ;
- **une émotion exagérée** du bonhomme (yeux énormes, bouche ouverte,
  larmes, panique), ou la **transformation** matière brute → objet tenue
  par deux mains dessinées (la forme du *fer*) ;
- **une seule idée**, lisible en tout petit.

**Les idées à décliner** (une par prompt) : l'émotion d'un moment fort
(« DÉPORTÉ POUR ÇA ? »), le paradoxe du titre (« ON JETTE ÇA ?! »), la
transformation (« D'OÙ VIENT LE SEL ? »), un chiffre qui frappe
(« 600 ANS D'IMPÔT ! »), l'effort absurde (« IL A CREUSÉ POUR ÇA ? »).

**Le texte est demandé directement à Gemini**, dans le prompt, entre
guillemets, avec « Write the text exactly as given, with the accents ».
C'est la seule exception à « jamais de texte dans les images » : elle
permet de tester vite. Franco vérifie les accents ; s'ils sont faux, il
regénère ou pose le texte lui-même. **Le texte doit être vrai** : pas de
« PLUS CHER QUE L'OR » si c'est faux ; un arrondi (« 600 ANS ») se
justifie dans le fichier.

**Chaque prompt est complet** (Franco le colle seul, avec la planche en
pièce jointe, sans le préambule des scènes) et suit ce modèle :

> YouTube thumbnail, 16:9. Bold cartoon illustration with thick black outlines, flat saturated colours, bright blue sky, sunny warm light, high contrast, very simple composition readable at small size. <la scène : décor, action, émotion exagérée du bonhomme>. The round-headed white character from the attached reference sheet <…>. Every person has exactly two arms and two hands. Big bold French text at the top in thick white (or yellow) capital letters with a heavy black outline: "<TEXTE>". Write the text exactly as given, with the accents. No other text, no logos, no watermark.

Recommande **un trio à tester**, chacun portant une idée différente
(l'émotion, le paradoxe, la transformation) : le test apprend alors
quelque chose. Note ce trio comme expérience en cours dans
`Memoire/lecons.md`, avant la publication. Comme pour les scènes,
**affiche les prompts dans la conversation**, un bloc de code par prompt.

## Rappel avant publication

Termine le fichier par cette liste, à cocher par Franco :

```markdown
## Avant de publier
- [ ] Horodatages des chapitres remplis
- [ ] Crédits des photos vérifiés (s'il y en a)
- [ ] Case « contenu altéré ou synthétique » de YouTube : vérifier si
      elle s'applique (voix clonée, images générées). Dans le doute, la cocher.
- [ ] Miniature : les trois variantes retenues chargées dans le test de miniatures
```

## Fin de vidéo

Donne à Franco, en 3 lignes : le lien de `04_publication.md`, ce qui lui
reste à faire (planche du bonhomme si elle manque, images et plans animés
Gemini, voix dans Colab, assemblage avec
`video-maker`), et ce que tu as mis à jour dans `Memoire/` (voir
`memoire.md`).
