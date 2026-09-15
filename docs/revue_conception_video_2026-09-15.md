# Revue de la chaîne de conception visuelle — 15/09/2026

Point de départ, formulé par Franco : *« Remotion peut produire des
animations de qualité production, tester sur navigateur en temps réel,
animer des images, produire du motion design exclusif. Mon setup n'en est
rien. »*

La revue part des **artefacts** — le catalogue d'aperçus, `animation.ts`,
le SKILL du Monteur, le `package.json` — et pas de l'intention.

**Verdict en une phrase :** le setup n'est pas vide, il est **incomplet aux
deux bouts** — la couche d'animation est sérieuse, mais rien au-dessus
(typographie, matière, transitions) ni en dessous (boucle de regard) ne la
rend visible.

---

## 1. Ce qui est déjà là, et qu'il ne faut pas reconstruire

Le diagnostic doit commencer par là, sinon la session refait ce qui existe.

- **`animation.ts` tient les huit règles du §8** : `spring()` partout,
  décalage d'entrée, variation de vitesse, anticipation, parallaxe, sortie
  qui ne coupe pas, mouvement continu, punch-in avec sens alterné. Ce n'est
  pas un brouillon.
- **L'accent tombe sur le mot prononcé** : `pulsation_s` est résolu depuis
  `04_phrases.json`, avec rattrapage du chevauchement de scène. Peu de
  chaînes font ça.
- **Le recalage son/image existe** : les scènes déclarent les phrases
  qu'elles couvrent, `construire_props.py` recale les durées.
- **Le catalogue d'aperçus est la seule boucle de vérification visuelle du
  système**, et il a déjà attrapé quatre défauts que le typecheck ne
  pouvait pas voir.
- **Le tuyau d'assets est généralisé** (E5b, 12/09) et trois composants
  « contenants » sont écrits.

## 2. Les sept écarts réels avec la « qualité production »

### Verrou 1 — La typographie est celle du système

`charte.json` demande `Arial, sans-serif`. Toute la chaîne — titres,
sous-titres, étiquettes — sort en Helvetica/Arial. `@remotion/google-fonts`
n'est pas installé.

C'est **le plus grand écart perceptif pour le plus petit coût du dépôt**.
Une vidéo en Arial se lit comme une capture de slide ; la police est ce que
l'œil identifie avant la composition. Un poids variable et deux niveaux
hiérarchiques suffisent à changer la catégorie perçue.

### Verrou 2 — Le style visé n'est pas celui que le code dessine

Le §« Style visé » dit : **sticker animé, formes pleines**. Le catalogue
montre l'inverse — `ConceptCutaway`, `StickmanTalk`, `Cadre` : contours de
2 px, aucun remplissage, aucune ombre portée, deux couleurs, aplat sombre.
Visuellement, c'est un **schéma au tableau blanc**, pas un sticker.

L'écart n'est pas dans la description (elle est bonne, E5b l'a prouvé), il
est dans les primitives de dessin : tant que les composants tracent des
`stroke` sans `fill`, aucune consigne de DA ne produira un sticker.

### Verrou 3 — Il n'y a pas de transitions, il y a un fondu

`Video.tsx` fait chevaucher les scènes de 0,25 s. C'est un bon correctif
contre les coupes franches, mais c'est **le même geste onze fois**.
`@remotion/transitions` (`TransitionSeries`, wipe, slide, clock-wipe,
flip) n'est pas installé. Le montage n'a donc aucun vocabulaire de
liaison — or c'est précisément là que se lit le rythme d'un Short.

### Verrou 4 — Les sous-titres ne bougent pas

`Subtitles.tsx` affiche une fenêtre de 5 mots et **change la couleur** du
mot actif. Pas d'échelle, pas de ressort, pas de hiérarchie. Sur un format
où les sous-titres occupent le tiers bas de l'écran pendant 100 % de la
durée, c'est le plus gros élément statique de la vidéo.

### Verrou 5 — La matière est possible mais personne ne la fabrique

`PlanCapture`, `PlanBroll` et `PlanLogos` sont écrits, typés, au catalogue.
Mais ils consomment `props.ressources`, qui est rempli par
`05b_ressources.json`, **qui est écrit par l'agent A8 — lequel n'existe
pas**. Les outils existent (`capturer_web.py`, `recuperer_logo.py`), rien
ne les appelle.

Conséquence directe : **trois composants sur sept sont inutilisables par une
vraie vidéo**. C'est le goulot du pipeline visuel, et il tient à un agent
manquant, pas à du code d'animation.

### Verrou 6 — Le navigateur temps réel n'est ouvert par personne

`npm run preview` (Remotion Studio) est déclaré dans `package.json` et
**n'apparaît dans aucun SKILL**. Le Monteur travaille ainsi : typecheck →
deux images fixes → rendu complet.

Or Remotion Studio, c'est exactement la capacité que Franco cite : timeline
scrubbable, rechargement à chaud à l'image près, props éditables en direct.
Le système possède l'outil et ne s'en sert pas — il fait du rendu aveugle
avec deux sondes.

### Verrou 7 — On regarde 18 % de la vidéo avant de la livrer

Deux images fixes pour onze scènes. La file d'attente porte déjà le
chantier #21 (« une image fixe par scène, regardée avant le CP3 ») ; tant
qu'il n'est pas fait, la leçon centrale d'E5b — *un contrôle automatique
n'attrape que ce qu'on a prévu, le défaut s'est vu en REGARDANT* — reste
écrite et non outillée.

### Mineur — Les paramètres de rendu sont ceux par défaut

`remotion.config.ts` ne fixe que le format d'image (`jpeg`) et l'exécutable
du navigateur. Ni `--crf`, ni `--concurrency`, ni qualité JPEG. Sur des
aplats sombres dégradés, les frames JPEG introduisent du banding visible.
À traiter **après** les six verrous ci-dessus, pas avant.

## 3. Ce que ça dit du diagnostic précédent

E5b avait conclu, à raison, que « la matière manquait, pas la description ».
Cette revue ajoute un cran : **la matière manque toujours** (verrou 5, A8
absent), et il manque en plus une **couche de finition** — police, formes
pleines, transitions, sous-titres animés — que le système n'a jamais eue et
qui n'apparaissait pas comme un manque parce qu'aucune étape ne la
réclamait.

Les verrous 1, 2 et 4 ne sont pas des optimisations reportables après
l'étude des six formats : ils fixent la **constance** du rendu, exactement
ce que la doctrine « stabiliser le visuel avant les 6 formats » demande de
faire maintenant. Ce qui reste à reporter, c'est ce qui vise l'organique
(d3-ease, `@remotion/noise`, rough.js) — la distinction tient.

## 4. Ordre recommandé

**Lot A — identité (rendu visible immédiatement, aucun agent nouveau)**

1. `@remotion/google-fonts` + deux niveaux typographiques dans `charte.json`
2. Passe « formes pleines » sur `ConceptCutaway`, `StickmanTalk`, `Cadre` :
   remplissages, ombres portées, épaisseurs variables, occupation du cadre
3. Sous-titres animés — ressort par mot, hiérarchie par ligne (file #22)
4. Régénérer le catalogue et **le regarder** : c'est le contrôle du lot

**Lot B — matière (débloque du code déjà écrit)**

5. Agent A8 Documentaliste (file #18) — rend utilisables trois composants
6. `outils/chercher_broll.py` (file #19)

**Lot C — montage et regard**

7. `TransitionSeries` avec transition par scène, jamais deux fois la même
   d'affilée (file #20)
8. Passe de critique visuelle, une image par scène avant le CP3 (file #21)
9. Remotion Studio inscrit à l'étape 5 du SKILL du Monteur (verrou 6)

Le lot A se juge au catalogue ; le lot B à la première vidéo qui affiche
une capture réelle ; le lot C au CP3.
