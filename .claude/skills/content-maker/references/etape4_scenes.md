# Étape 4 — Scènes et prompts d'images

**But** : `03_scenes.md`, le fichier que lira `video-maker` pour assembler
la vidéo, et les prompts que Franco collera dans Gemini. Pas de pause :
enchaîne directement sur l'étape 5 une fois le fichier vérifié.

## Découper le script en scènes

- **Une scène = une image à l'écran pendant 6 à 8 s**, soit environ **18 à
  25 mots de texte dit**. Pour environ 1 480 mots : **60 à 80 scènes**.
- **Le « texte dit » est un extrait exact et continu de `02_script.md`**,
  sans les titres de blocs. Mises bout à bout, les scènes redonnent tout le
  script, dans l'ordre, sans trou ni répétition. C'est ce qui permet à
  `video-maker` de caler chaque image sur la voix (il aligne ce texte sur
  l'horodatage mot à mot) : un mot changé ou oublié casse l'alignement.
- **Coupe aux articulations** : fin de phrase de préférence, sinon une
  virgule forte. Une scène ne coupe jamais un nom ou une date en deux.
- **Une idée visuelle par scène.** Si une phrase porte deux images
  (« le feu, puis le pot »), fais deux scènes.

## Les types de scène

| type | Quand | Image |
|---|---|---|
| `image` | la plupart des scènes | générée par Gemini : `scene_001.png`… |
| `photo` | **facultatif** : seulement si la recherche a trouvé une vraie photo libre qui colle au texte | `photos/<nom>.jpg` ; colonne « crédit » remplie (auteur, licence) |
| `titre` | l'ouverture de chaque question d'enquête (Q1 à Q4), 2 à 3 s sans voix | aucune : `video-maker` affiche la question (colonne « texte animé ») sur un fond sobre ; « texte dit » vaut `—` |

## Mouvements de caméra (calmes)

`zoom_avant`, `zoom_arriere`, `pan_gauche`, `pan_droite`, et pour une
photo `zoom_vers:x,y` (le détail à montrer, en fractions de l'image : 0,0
en haut à gauche). **Alterne** : pas plus de 3 fois de suite le même
mouvement. Par défaut, `zoom_avant`.

## Texte animé

Seulement **un mot-clé, une date ou un chiffre**, et **au plus une scène
sur trois** : « 1344 av. J.-C. », « 21 km », « Hallstatt ». Sinon `—`.

## Le fichier `03_scenes.md`

```markdown
# Scènes — <sujet>

Palette : <3 à 4 couleurs de la matière>
Planche du bonhomme : Charte/planche_bonhomme.png

| n° | type | texte dit | image | mouvement | texte animé | crédit |
|---|---|---|---|---|---|---|
| 1 | image | Regarde la salière sur ta table. C'est sans doute ce qu'il y a de moins cher dans ta cuisine. | scene_001.png | zoom_avant | — | — |
| 12 | titre | — | — | — | Pourquoi, un jour, fabriquer du sel ? | — |
| 31 | photo | Regarde cet escalier. Le bois a été coupé en 1344 avant notre ère. | photos/hallstatt_escalier.jpg | zoom_vers:0.62,0.40 | 1344 av. J.-C. | Andreas W. Rausch, CC BY-SA 3.0 |
```

Notes :
- Le « texte dit » reprend `02_script.md` (**chiffres en chiffres**),
  pas la version voix. `video-maker` fait la correspondance avec la voix.
- La colonne **crédit** ne sert qu'aux scènes `photo` : `auteur, licence`.
  N'invente jamais un auteur ou une licence. Si la photo n'est pas
  trouvée, fais une scène `image` (Gemini) à la place : la mise en scène
  suffit.

## Les prompts Gemini (dans le même fichier, après le tableau)

**En anglais**, avec **le résumé français à côté** pour que Franco sache ce
que montre chaque image. **Par lots de 10** : chaque lot se joue dans une
seule conversation Gemini, où Franco a déposé la planche du bonhomme une
fois (la cohérence du personnage tient mieux dans une même conversation).

Mode d'emploi à écrire en tête de section :

```markdown
## Prompts Gemini

Pour chaque lot : ouvre une nouvelle conversation Gemini, dépose
Charte/planche_bonhomme.png, colle le **préambule**, puis les prompts un par
un. Enregistre chaque image sous le nom indiqué (scene_001.png…) dans
images/.

**Préambule (à coller une fois par lot)** :
> <le préambule de style ci-dessous, avec la palette du sujet>
```

**Le préambule de style** (adapte seulement la palette) :

> Flat 2D digital illustration in a warm, calm documentary style, soft
> painterly textures, simple readable shapes, gentle natural light.
> Palette: <palette of the material>. The main character is the
> round-headed white figure from the attached reference sheet: keep exactly
> the same head shape, proportions, line style and outfit in every image.
> 16:9 landscape composition, the character takes about a third of the
> frame, with calm empty space for text overlays. No text, no letters, no
> numbers, no logos, no watermark in the image.

**Chaque prompt** :

```markdown
### Lot 1 — scènes 1 à 10
**scene_001** — *Une salière sur une table de cuisine, lumière du matin.*
> Close-up of a simple glass salt shaker on a wooden kitchen table, morning
> light through a window, small spilled salt crystals. The character is
> not in this shot.
```

Règles des prompts :
- **Décris une action et un décor concrets** : qui fait quoi, où, quelle
  lumière, quel cadrage (gros plan, plan large…).
- **Continuité** : quand deux scènes se suivent au même endroit, ajoute
  « Same setting and lighting as scene_0NN. »
- **Aucun texte dans l'image**, même sur un panneau ou un parchemin.
- **Mise en scène plutôt que reconstitution d'objet réel** : préfère
  « un atelier de potiers au bord d'une source salée » à la copie d'un
  objet de musée précis.
- **Pas de prompt pour les scènes `photo` et `titre`.**

## Vérifier avant de livrer

Lance `python3 scripts/verifier.py 03_scenes.md --script 02_script.md`,
qui contrôle le tableau, la continuité du texte dit, les noms d'images,
les crédits des photos, et qu'il y a un prompt par scène `image`. Corrige puis
enchaîne sur l'étape 5. Sans exécution de code, vérifie au moins la
numérotation, le nombre de scènes et un prompt par scène `image`.
