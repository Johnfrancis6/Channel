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

SOURCES
▸ <auteur, titre, revue ou institution, année>
▸ … (5 à 8 sources principales du dossier)

CRÉDITS DES PHOTOS
▸ <objet> — <auteur>, <licence>, via Wikimedia Commons
▸ … (une ligne par pièce à conviction : **obligatoire** en CC BY et CC BY-SA)

Illustrations générées par IA ; les pièces à conviction sont de vraies
photographies.
```

## Miniature

- **Deux prompts Gemini** (en anglais, avec le résumé français) :
  1. **avec le bonhomme** (le personnage de la planche), qui tient ou montre
     la matière brute, l'objet fini à côté ;
  2. **sans personnage** : deux mains, la matière brute et l'objet fini. C'est
     la forme de la meilleure miniature mesurée de Zelan (*le fer*).
  Les deux : composition simple, contraste fort, fond peu chargé, et **de la
  place pour le texte** (ajouté ensuite, pas généré dans l'image).
- **3 textes de 2 à 3 mots**, en capitales, à poser en jaune cerné de noir.
  Recommande-en un. **Le texte doit être vrai** : pas de « PLUS CHER QUE
  L'OR » si c'est faux.
- Rappelle que les deux variantes se testent avec l'outil de test de
  miniatures de YouTube Studio.

## Rappel avant publication

Termine le fichier par cette liste, à cocher par Franco :

```markdown
## Avant de publier
- [ ] Horodatages des chapitres remplis
- [ ] Crédits des photos vérifiés (auteur, licence)
- [ ] Case « contenu altéré ou synthétique » de YouTube : vérifier si
      elle s'applique (voix clonée, images générées). Dans le doute, la cocher.
- [ ] Miniature : les deux variantes chargées dans le test de miniatures
```

## Fin de vidéo

Donne à Franco, en 3 lignes : où déposer `04_publication.md`, ce qui lui
reste à faire (images Gemini, voix dans Colab, assemblage avec
`video-maker`), et la **mise à jour de `Memoire/`** (voir `memoire.md`).
