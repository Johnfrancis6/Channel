# Étape 4 — Scènes, prompts d'images et plans animés

**But** : `03_scenes.md`, le fichier que lira `video-maker` pour assembler
la vidéo, avec les prompts que Franco colle dans Gemini. **Les prompts
s'affichent aussi dans la conversation** (voir la fin de ce fichier) :
Franco les copie depuis le chat. Pas de pause : enchaîne directement sur
l'étape 5 une fois le fichier vérifié.

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
- **Écris le découpage avec un petit script** (une liste Python de scènes
  qui génère le fichier) plutôt qu'à la main : les renvois de continuité
  (« Same kitchen as scene_001 ») et la numérotation se recalculent quand
  tu fusionnes ou déplaces une scène. Après chaque changement, vérifie que
  chaque renvoi pointe toujours vers la bonne image.

## Les types de scène

| type | Quand | Image |
|---|---|---|
| `image` | la plupart des scènes | générée par Gemini : `scene_001.png`… |
| `video` | **6 à 10 par vidéo** : un plan légèrement animé pour casser la monotonie (voir « Plans animés ») | `clips/scene_NNN.mp4`, généré dans Gemini à partir de `scene_NNN.png` ; mouvement `—` |
| `photo` | **facultatif** : seulement si la recherche a trouvé une vraie photo libre qui colle au texte | `photos/<nom>.jpg` ; colonne « crédit » remplie (auteur, licence) |
| `titre` | l'ouverture de chaque question d'enquête (Q1 à Q4), 2 à 3 s sans voix | aucune : `video-maker` affiche la question (colonne « texte animé ») sur un fond sobre ; « texte dit » vaut `—` |

Les scènes `titre` n'ont **ni image ni prompt** : dis-le à Franco quand
tu lui donnes les lots, sinon il croit à un trou dans la numérotation
(constaté le 30/09 : « il manque la scène 7 »).

## Mouvements de caméra (calmes)

`zoom_avant`, `zoom_arriere`, `pan_gauche`, `pan_droite`, et pour une
photo `zoom_vers:x,y` (le détail à montrer, en fractions de l'image : 0,0
en haut à gauche). **Alterne** : pas plus de 3 fois de suite le même
mouvement. Par défaut, `zoom_avant`. Une scène `video` porte son propre
mouvement : colonne `—`.

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
| 2 | video | Chaque hiver, des camions entiers en jettent sur les routes. | clips/scene_002.mp4 | — | — | — |
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

## Le bonhomme : la planche de référence

Toutes les images partent de `Charte/planche_bonhomme.png`. **Si elle
n'existe pas encore dans Drive**, donne d'abord ce prompt à Franco
(nouvelle conversation Gemini, sans pièce jointe), et demande-lui de te
montrer le résultat avant de lancer les lots :

> Character reference sheet for a calm animated history documentary. One simple, friendly figure: a perfectly round, smooth white head with no hair, two small black oval eyes, a small simple mouth and no nose; a slim white body with soft rounded limbs and simple four-finger hands; thin dark grey outline. Default outfit: a plain sand-coloured short-sleeved tunic tied at the waist with a brown cord, brown trousers and simple brown shoes; his white arms are visible. Anatomy: every full-body figure has exactly two arms, two hands and two legs, clearly separated from the body; no extra limbs. Show the same character on a plain off-white background: front view, three-quarter view, side view and back view in a row, standing about four heads tall, arms relaxed along the body; below them, four head close-ups with different expressions (neutral, curious, surprised, thoughtful) and one full-body pose holding an object in both hands. Every figure is complete and fully inside the frame. Flat 2D digital illustration, clean lines, soft shading, warm calm palette. Identical proportions in every view. No text, no letters, no labels, no numbers, no watermark.

**Examine chaque planche qu'il te montre, personnage par personnage, en
comptant les bras et les mains.** Le défaut fréquent de Gemini est un
bras en trop, surtout en vue de trois-quarts et dans les poses (constaté
le 30/09 sur deux planches sur deux). Si un seul personnage est
fautif, fais-le corriger dans la même conversation plutôt que de tout
regénérer :

> Edit this image: the <position> figure has three arms. Remove the extra arm so he has exactly two arms, one on each side, like the other figures. Keep everything else exactly the same: same character, same outfit, same layout, same colours, same background.

Si une image de scène recopie la planche (des rangées de bonshommes ou de
têtes à côté de la scène), fais-la corriger dans la même conversation :

> Edit this image: remove the figures and round heads copied from the reference sheet on the <side> side; they must not appear in the scene. Extend the background to fill that space. Keep the main character exactly as he is: same pose, same face, same outfit, same two arms. Same colours, same light, same style. No text.

La planche validée le 30/09 (le sel) : tête ronde blanche lisse, yeux en
petits ovales, pas de nez, tunique sable à manches courtes avec un cordon
marron, pantalon et chaussures marron, bras blancs visibles.

## Les prompts Gemini (dans le même fichier, après le tableau)

**En anglais**, avec **le résumé français à côté** pour que Franco sache ce
que montre chaque image. **Par lots de 10** : un lot par conversation
Gemini (la cohérence du personnage tient mieux dans une même
conversation).

Mode d'emploi à écrire en tête de section (il répond à ce qui a coincé
au premier essai, le 30/09) :

```markdown
## Prompts Gemini

**Mode d'emploi.** Pour chaque lot : ouvre une **nouvelle conversation**
Gemini, joins Charte/planche_bonhomme.png (à chaque conversation : Gemini
ne garde rien d'une conversation à l'autre) et colle le **préambule** dans
le même message ; attends son « OK ». Puis envoie **un seul prompt par
message**, sous la forme `scene_001: <prompt>`. Enregistre chaque image
sous son nom (scene_001.png…) dans images/. Les scènes de type titre
(<numéros>) n'ont pas d'image. Les scènes de type video partent de leur
image (voir « Plans animés »).
```

**Le préambule** (adapte seulement la palette). Il dit à Gemini de
**ne rien raconter** et de **faire une seule image par message** : sans
ça, Gemini répond en mode conversation, écrit une petite histoire autour
de chaque image et enchaîne des images non demandées (constaté le 30/09).
Il lui interdit aussi de **recopier la planche** : sans cette phrase, Gemini
a collé les trois bonshommes debout et les quatre têtes de la planche à
gauche d'une scène (constaté le 01/10 sur le verre, scene_012).

> You are an image generator. Do not write any story, narration, caption or explanation, ever. Do not generate any image now: reply only "OK" and wait. Then, for each message I send that starts with "scene_", generate exactly ONE image and reply with the image only, no text at all. Style rules for every image: flat 2D digital illustration, warm and calm, soft painterly textures, simple readable shapes, gentle natural light. Palette: <palette of the material>. The main character is the round-headed white figure from the attached reference sheet: keep exactly the same head shape, face, proportions and line style in every image; change only his clothing when the prompt says so, otherwise keep his default outfit from the sheet. The reference sheet is only a model for the character: never copy its layout, its rows of figures or its head close-ups into a scene; each image shows only the scene described in the prompt. Every person in the image has exactly two arms and two hands, no extra limbs. 16:9 landscape composition, the character takes about a third of the frame, with calm empty space for text overlays. No text, no letters, no numbers, no logos, no watermark in the image.

**Chaque prompt** :

```markdown
### Lot 1 — scènes 1 à 11
**scene_001** — *Une salière sur une table de cuisine, lumière du matin.*
> Close-up of a simple glass salt shaker on a wooden kitchen table, morning
> light through a window, small spilled salt crystals. The character is
> not in this shot.
```

Règles des prompts :
- **Décris une action et un décor concrets** : qui fait quoi, où, quelle
  lumière, quel cadrage (gros plan, plan large…).
- **Habille le bonhomme selon l'époque** quand il est dans une scène
  historique (« dressed as a Neolithic farmer », « as an archaeologist ») :
  le préambule l'autorise ; sinon il garde sa tunique de la planche.
- **Continuité** : quand deux scènes se suivent au même endroit, ajoute
  « Same setting and lighting as scene_0NN. »
- **Aucun texte dans l'image**, même sur un panneau ou un parchemin.
  Le préambule ne suffit pas (mesuré sur le sel, le 30/09 : 4 images sur 76
  portaient du texte **en anglais**, sur un sac, une pierre gravée, un schéma
  en coupe et l'entrée d'une mine). Dès que la scène contient une surface qui
  appelle l'écriture (sac, pierre, panneau, enseigne, camion, schéma, carte,
  livre), le prompt le dit lui-même : « plain unmarked sacks », « a blank
  uncarved stone », « the layers are shown by colour only, with no labels ».
- **Mise en scène plutôt que reconstitution d'objet réel** : préfère
  « un atelier de potiers au bord d'une source salée » à la copie d'un
  objet de musée précis.
- **Pas de prompt pour les scènes `photo` et `titre`.** Une scène `video`
  a **deux** prompts : `scene_NNN` (son image de départ, dans son lot) et
  `anim_NNN` (l'animation).

## Plans animés

Demandé par Franco le 30/09 : quelques plans animés pour casser la
monotonie d'une image fixe toutes les 7 s. **6 à 10 par vidéo** (la
génération vidéo de Gemini est limitée par jour, et chaque clip se
vérifie à l'œil), **répartis sur toute la vidéo** (pas deux de suite), là
où le mouvement est naturel : feu, fumée, vapeur, eau, vagues, torche,
neige, un véhicule qui roule, des gens qui marchent. Évite les gros
plans de visage et les mains qui manipulent un objet : c'est là que
l'animation déforme le personnage.

Chaque clip se génère **à partir de l'image de la scène** : Franco
produit d'abord `scene_NNN.png` dans son lot, puis crée une vidéo depuis
cette image avec le prompt `anim_NNN` : dans l'app Gemini, l'outil
**Vidéo** (modèle Veo), l'image en pièce jointe ; à défaut, Google Flow
(`labs.google/flow`, « images vers vidéo »). La génération vidéo dépend
de l'abonnement Google et a un quota par jour : c'est pourquoi on s'en
tient à 6 à 10 clips. Il l'enregistre sous
`clips/scene_NNN.mp4` et garde l'image : si le clip est raté,
`video-maker` utilise l'image à la place. Le son du clip n'est pas
utilisé.

Section à écrire après les lots :

```markdown
## Plans animés

**anim_002** — *La saleuse avance doucement, le sel jaillit, la neige tombe.* (à partir de scene_002.png)
> Animate this illustration with a slow, subtle motion: <le mouvement, en une phrase>. The camera stays still. Keep exactly the same drawing style, colours, characters and composition as the image; the character keeps the same face and exactly two arms. No new objects or people, no cuts, no text, no talking, no music.
```

Le mouvement tient en une phrase, lent et léger : les flammes vacillent,
la vapeur monte, le bateau tangue. Jamais une action nouvelle (quelqu'un
qui entre, un objet qui apparaît) : le plan doit rester celui de l'image.

## Vérifier avant de livrer

Lance `python3 scripts/verifier.py 03_scenes.md --script 02_script.md`,
qui contrôle le tableau, la continuité du texte dit, les noms d'images et
de clips, les crédits des photos, un prompt par scène `image` ou `video`,
un prompt `anim_NNN` par scène `video`, et au plus 12 plans animés.
Corrige, dépose dans Drive, puis affiche les prompts (ci-dessous) et
enchaîne sur l'étape 5. Sans exécution de code, vérifie au moins la
numérotation, le nombre de scènes et un prompt par scène `image`.

## Afficher les prompts dans la conversation

Franco copie les prompts depuis le chat (demandé le 30/09). Après le
dépôt de `03_scenes.md`, affiche, dans cet ordre et **structuré** :

1. la planche du bonhomme, **seulement si** `Charte/planche_bonhomme.png`
   n'existe pas encore ;
2. le préambule, dans un bloc de code ;
3. les lots, un titre par lot (`## Lot 1 — Hook et Q1 (scènes 1 à 11)`),
   puis pour chaque scène : `**scene_001** — *résumé français*` et le
   prompt anglais **dans son propre bloc de code**, pour qu'il se copie
   d'un clic ;
4. les plans animés, de la même façon (`**anim_002**`…) ;
5. une ligne qui rappelle les scènes `titre` sans image.

C'est long : ne résume pas, ne coupe pas. C'est la seule partie de
l'étape 4 qui s'écrit en entier dans le chat.
