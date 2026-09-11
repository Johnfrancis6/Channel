# Diagnostic du pipeline, étape par étape

Document vivant. Chaque étape du §6.2 est passée au crible sur les
**artefacts réellement produits**, pas sur son intention. Les décisions
prises en séance sont consignées ici au fil de l'eau.

Vidéo de référence du diagnostic : `2026-09-11_v01` (pilier `concept`, voie
tampon, mode `sujet_impose`), première vidéo du système à être allée jusqu'au
CP3.

---

## Grille

Cinq questions par étape. Les deux dernières sont celles qui ont lâché en
conditions réelles.

1. **Entrée** — l'agent a-t-il ce qu'il lui faut pour décider ?
2. **Décision** — qui tranche, avec quelle marge, et est-ce le bon acteur ?
3. **Sortie** — le contrat est-il tenu, et l'aval peut-il la consommer ?
4. **Échec** — que se passe-t-il quand ça rate, et est-ce que ça remonte ?
5. **Boucle** — le résultat revient-il quelque part pour améliorer le tour suivant ?

---

## Décisions transverses

Prises en séance le 11/09/2026, elles dépassent une seule étape.

### La durée se calibre en idées, pas en secondes

```
idées_max = 3                          ← règle de chaîne (exceptions possibles)
mots_par_idée = propriété du FORMAT    ← c'est là que vit le dépassement
durée = idées × mots_par_idée ÷ 3,2 mots/s   ← déduite, jamais imposée
```

Une interview fictive n'a pas plus d'idées qu'une explication : chaque idée
y coûte plus de mots, parce que le dialogue doit incarner et relancer. Elle
dépasse donc 60 s **sans déroger à la règle**. Le dépassement devient de
l'arithmétique prévisible en amont, au lieu d'être découvert au montage.

Le débit de 3,2 mots/s est mesuré sur `2026-09-11_v01` (264 mots, 82,5 s de
voix off pauses comprises). `generer_storyboard.py` utilise encore 2,5 — à
corriger (voir file d'attente).

### Les formats se découvrent sur les 6 premières vidéos

Un format nouveau par vidéo, étude à la 6e ; si les résultats ne sont pas
clairs, on continue à en essayer.

**Deux conséquences à garder en tête :**

- **Le corpus doit exister avant la vidéo 2.** Si les six vidéos ne sont pas
  mesurées de la même façon dès la première, l'étude sera impossible : six
  vidéos, aucune donnée comparable. La vidéo 1 est mesurable rétroactivement
  (`03_script_tts.txt` + `04_timestamps.json` existent).
- **Six formats = n=1 par format.** L'étude de la 6e vidéo répondra à *quel
  format retient le mieux*, pas à *combien de mots coûte une idée dans tel
  format*. Les budgets par format demanderont de répéter les formats retenus.

### Stabiliser le visuel avant les 6 formats, pas l'optimiser

Si la qualité visuelle varie au hasard d'une vidéo à l'autre, l'étude des
formats est polluée : impossible de savoir si un format retient mieux, ou si
le rendu était plus réussi ce jour-là. L'objectif avant les 6 vidéos n'est
pas la beauté, c'est la **constance** — pour que la seule variable qui bouge
soit le format.

D'où la séparation : **catalogue d'aperçus et cadrage du Designer
maintenant** ; **outils du Monteur (Lottie, Rive, d3-ease, rough.js) après
l'étude**, quand on saura quel style on vise.

### Analyse de structure : le vocabulaire est fermé, la narration est libre

| | Fermé | Souple |
|---|---|---|
| Vocabulaire des rôles (hook, idée, exemple, CTA, sponsoring…) | ✅ sinon rien ne s'agrège | |
| Gabarit narratif (ordre, rythme, ton, mise en scène) | | ✅ c'est là que vit la vidéo de référence |

Le vocabulaire reste extensible : on peut ajouter un rôle, mais il entre
alors au registre et s'applique à tout le corpus.

L'outil d'analyse vit dans **`outils/`**, dossier commun déployé par
`agents/_synchroniser_vers_claude_skills.py` — il sert A3 (concurrents) et
H1 (nos propres vidéos).

### Style visé : sticker animé, tout codé en Remotion

Le style visé est le **sticker animé** — formes pleines, mouvement fluide et
naturel. **Lottie a été envisagé puis écarté** (11/09/2026).

Le raisonnement mérite d'être conservé, parce qu'il montre ce qu'on a pesé.
Lottie donnait la fluidité toute faite sur le personnage et les transitions,
mais un fichier pré-rendu ne peut pas illustrer un schéma dont le contenu
change d'une vidéo à l'autre : chaque nouvelle variante de `ConceptCutaway`
aurait exigé un fichier fait à la main avant que la vidéo puisse tourner.
Franco a préféré raffiner les composants existants.

**Le coût ne disparaît pas, il change de nature.** Lottie achetait la
fluidité ; en Remotion pur, elle se code, par composant, et ça retombe sur
A7. En échange : une identité propre, et des composants **paramétrables**.

Huit règles en découlent (§8, valeurs dans `charte.json >
animation.naturel`) : ressort plutôt que rampe, rien ne s'arrête net,
décalage de 80 ms à l'entrée, ±15 % de variation de vitesse entre éléments,
mouvement secondaire à 120 ms, anticipation de 10 px, parallaxe du fond à
0,4, et rien de totalement immobile.

**Conséquence sur la file d'attente : 3c se débloque.** La reprise des
composants attendait les fichiers Lottie ; elle n'attend plus rien, et c'est
désormais le seul chemin vers la qualité visuelle.

### Chaque vidéo a un dossier `assets/`

Franco y dépose ses images d'inspiration et ses fichiers Lottie. Lu par A6
(référence visuelle la plus directe) et A7 (rendu). Créé par `new_short.py`
à côté de `checkpoints/`.

C'est aussi ce qui manquait pour que le dialogue de cadrage ait un support :
une référence visuelle n'a plus à repartir dans une note en texte libre.

### Le corpus est le seul actif qui prend de la valeur

Aujourd'hui **rien ne s'accumule** dans tout le système : le rapport
hebdomadaire est un fichier neuf chaque semaine, et les notes qualitatives
d'A3 sont de la prose indexée par chaîne, pas par vidéo. Un système qui
n'accumule rien ne peut rien apprendre.

`02_Veille_hebdo/corpus_structures.jsonl`, append-only, une ligne par vidéo
analysée. Démarrage sur **nos propres vidéos** — timestamps mot à mot, donc
qualité supérieure à tout ce qu'on obtiendra des concurrents — avant de
brancher l'API YouTube.

### Paliers vers l'autonomie

| Palier | Le système | Franco | Passage au suivant |
|---|---|---|---|
| **1 — Mesure** | segmente et mesure, ne décide rien | corrige les segmentations douteuses | ~15 vidéos au corpus |
| **2 — Contrainte** | budgets issus du corpus, A4 écrit sous contrainte mesurée | valide les budgets | budgets stables à ±10 % |
| **3 — Proposition** | propose format, angle et hook d'après ce qui a marché | valide au CP1 | rétention corrélée aux prédictions |

---

## E1 — Recherche (A2) + CP1

### Ce qui va bien

`01_recherche.md` est du bon travail : quatre sources dont la primaire
Anthropic citée mot à mot, et une distinction non triviale et juste — *ce
n'est pas « a-t-il des outils ? » qui sépare workflow et agent, c'est qui
contrôle la boucle*. La section « Points à trancher » pose de vraies
questions.

### Défauts, par responsable

| Responsable | Défaut | État |
|---|---|---|
| `new_short.py` | aucun champ pour format / référence / idées ; `--note` seule porte d'entrée | ✅ corrigé |
| `new_short.py` | `titre_travail` recopie `sujet` sans limite (148 car. en réel) | ✅ corrigé |
| `engine.py` | rapport de checkpoint tronqué par le début, amputé de sa partie décisionnelle | ✅ corrigé |
| `short-designer` | ne lisait pas `consignes.note_franco`, son destinataire naturel | ✅ corrigé |
| `short-chercheur` | lisait `note_franco` sans instruction | ✅ corrigé |
| `short-chercheur` | branche `sujet_impose` non écrite | ✅ corrigé |
| `short-chercheur` | gabarit sans hook, budget, hiérarchie des faits, incertitudes, termes à risque | ✅ corrigé — sept sections |
| `short-chercheur` | échec sans critère : A2 ne pouvait structurellement pas échouer | ✅ corrigé |
| `short-chercheur` | `commencer` (qui incrémente `tentatives`) avant vérification des entrées | ✅ corrigé — les inputs passent avant |
| `projets_franco.md` | créé, mais **lu par aucun agent** | ✅ corrigé — A2 et A4 le lisent |
| Entrées | `chaines_concurrentes.json` vide, aucune analyse concurrentielle | ⬜ reste à faire |

### Le rapport CP1 ne contenait pas les questions

Le plus grave, et vérifié sur le fichier réel. `_lire_extrait()` gardait les
3000 premiers caractères. L'ordre des sections étant Sources → Faits → Angle
→ Questions, on conservait les sources (inutiles pour décider) et on jetait
les questions. La coupe tombait **au milieu du mot « caméra »**.

Les deux questions du Chercheur — *faut-il nommer MCP ?* et *quel exemple
pour l'étape 3 ?* — n'apparaissaient nulle part. Le commentaire de validation
de Franco tranche pourtant exactement ces deux points : il avait donc ouvert
`01_recherche.md` en direct. Le fichier conçu au §5.5 pour décider depuis un
téléphone faisait écran au lieu de servir.

Corrigé : l'extraction est consciente des sections Markdown et préserve
d'abord celles qui portent la décision. Vérifié sur le fichier réel de
4570 octets — les trois questions survivent intégralement.

### L'intention de mise en scène voyageait par ricochet

`note_franco` contenait la direction complète (stickman en intro, cutaway par
étape, lien de référence). Elle était destinée au Designer. Or le Designer ne
lisait jamais `consignes`. Elle l'a atteint par trois relais : A2 l'a
recopiée dans « Angle proposé », d'où elle a transité dans le script, d'où le
Designer l'a devinée. Corrigé — A2 et A6 lisent désormais `consignes`
explicitement.

### Boucle — morte

Le commentaire de CP1 corrige *cette* vidéo mais n'est réinjecté nulle part.
A2 reproposera un exemple hors-sol la prochaine fois. H1 devait fermer cette
boucle ; il n'a jamais tourné.

### Angle mort assumé

Deux modes sur trois n'ont **aucun run réel** : `veille_actu` (la voie
rapide, pilier actu IA) et `sujet_backlog`. Tout le diagnostic ci-dessus
repose sur un unique passage en `sujet_impose`.

---

## E5 — Storyboard (A6), constat partiel

Le storyboard réel est de bonne qualité : 11 scènes nommées par leur
fonction, beats explicites, deux composants nouveaux correctement spécifiés
avec réutilisation anticipée. **La compétence de description n'est pas le
problème.**

Mais A6 décrit une **structure**, pas une **image** :

- `scene="workflow_fixed_path"` est une clé opaque. Ce qui est dessiné,
  combien d'éléments, dans quel sens — écrit nulle part. Pendant 14,4 s, le
  contenu de l'écran n'a été décidé par personne : A7 l'a inventé au moment
  de coder.
- Les scènes 1 à 3 affichent **le texte prononcé**, en doublon avec les
  sous-titres qui portent la même phrase.
- Plans de 14,4 s et 16 s, conséquence de l'estimation à 2,5 mots/s.
- A6 voit le dépassement de durée et ne peut rien faire : *« à trancher au
  CP3 »*, soit deux étapes plus loin.

Cause racine : **aucun référent visuel**. Le §8 prévoit pourtant « un aperçu »
par composant dans `REGISTRE.md` — jamais fait. On ne cadre pas ce qu'on n'a
jamais vu.

### Le cadrage est désormais un dialogue, pas une livraison

A6 n'écrit plus le storyboard pour le découvrir au CP3. Il analyse le
script, élabore **ce qui est faisable** au vu du catalogue et du jeu de base
Lottie, écrit `05_cadrage.md` — ce que chaque bloc montre à l'écran, le coût
de ce qui manque, ses questions — et attend les ajustements de Franco.

Ça ne crée **ni étape ni agent** dans §6.2, contrairement à l'Art Director
écarté en revue : c'est le même E5, rendu interactif. Et si Franco n'est pas
disponible, A6 poursuit sur sa proposition en le signalant — le pipeline ne
se bloque pas sur une absence.

Trois règles de contenu à l'écran en découlent, toutes tirées de ce que le
catalogue a montré : jamais la phrase prononcée à l'écran (les sous-titres
la portent), remplir le cadre 1080×1920, et laisser les 220 px du bas aux
sous-titres.

### Ce que le catalogue a révélé dès son premier passage

`outils/generer_apercus.py` existe maintenant, et les dix premières images
ont montré en quelques secondes trois défauts que personne n'avait vus :

- **`ConceptCutaway` laisse environ les trois quarts du cadre vides**, et ses
  schémas sont génériques : deux rectangles « STEP 1 / STEP 2 » qui
  n'illustrent en rien le concept annoncé. Le stickman de fond est
  minuscule, et les sous-titres (`paddingBottom: 220`) le recouvrent. **Ce
  plan a tenu 14,4 secondes** dans la vidéo qui attend au CP3.
- **`StickmanTalk` : `intro` et `outro` rendent une image strictement
  identique** — même empreinte md5. Le mapping interne envoie les deux sur
  la pose `wave`. L'API annonce trois poses, il y en a deux. A6 croit
  choisir là où il n'a pas le choix.
- **Aucun composant ne remplit le 1080×1920.** Le personnage fait environ un
  cinquième de la hauteur.

Ces trois défauts existaient depuis le début et **aucun test ne pouvait les
attraper** : il fallait regarder. C'est la meilleure justification du
catalogue — et une illustration de la remarque de méthode faite en revue,
sur ce que le dépôt teste et ce qu'il ne teste pas.

---

## E4 — Audio (notebook Colab)

**Verdict : la règle des 3 tentatives était écrite au mauvais endroit.**

Le code de l'Orchestrateur est correct — `_traiter_echec_etape_manuelle`
passe bien en `alerte` dès `tentatives >= max_tentatives`. Il n'a simplement
**jamais tourné** entre les échecs : entre deux runs audio, c'est le notebook
qu'on relance, pas lui, et en mode `reel` rien ne le déclenche
automatiquement (§12, déclenchement non tranché).

Résultat sur `2026-09-11_v01` : **8 tentatives** pour un plafond de 3, sept
échecs entre 13 h 27 et 15 h 49, **2 h 20 perdues**.

### Quatre défauts, tous corrigés

| # | Défaut | Correction |
|---|---|---|
| 1 | La règle du §2 vivait dans un composant qui ne tourne pas au moment utile | `etape_commencer` refuse au-delà de `MAX_TENTATIVES`, avec `FORCER_RELANCE` comme porte de sortie explicite |
| 2 | `MAX_TENTATIVES` était **défini et jamais lu** — garde-fou décoratif | il est désormais consulté, et un test le vérifie |
| 3 | Diagnostic WER identique à 96 % et à 9 % | deux bandes : marginal (< 30 %) et **structurel** (> 30 %), aux conseils opposés |
| 4 | L'agent de l'historique était écrit en dur | il vient de `state.json` ; le moteur va dans le message |

Le n° 3 est celui qui a coûté le temps. Les quatre premiers runs étaient à
93-98 % de WER — la fuite de référence de F5-TTS, un défaut structurel
évident — et le notebook a répondu quatre fois « re-synthèse avec une autre
graine ». Un WER de 96 % ne dit pas « réessaie », il dit « quelque chose est
fondamentalement cassé ». Les seuils sont calés sur les runs réels :
marginaux à 8-18 %, structurels à 93-98 %, frontière posée à 30 %.

Le n° 4 a un effet discret mais durable : l'historique réel contient
`colab_voix_f5tts` **et** `colab_voix_qwen_tts` pour la même étape, alors que
`state.etapes.E4_audio.agent` vaut `colab_voix`. Trois noms pour un agent,
ce qui casse tout regroupement en aval — H1, corpus.

### Ce qui reste ouvert, et qui dépasse E4

**Rien ne déclenche l'Orchestrateur.** C'est la cause racine, et sa portée
va bien au-delà de l'audio : *toute* règle qui vit dans l'Orchestrateur est
inopérante tant qu'il ne tourne pas. Le §12 laisse le déclenchement non
tranché — cron local, Claude Code headless, ou lancement manuel. À trancher,
sinon d'autres règles connaîtront le même sort.

## E2 + E3 — Rédaction et Filtre TTS

**Le budget en idées n'était appliqué nulle part.** Il est écrit à la
création (`--idees`), lu par le Chercheur et par le Designer — mais A4, qui
écrit les mots, ne le connaissait pas, et A5, qui les mesure, ne le
vérifiait pas. Zéro occurrence de `idees_max` dans les deux prompts.

C'est le maillon qui compte : relancer une vidéo dans cet état aurait
reproduit les 82 secondes à l'identique.

Corrigé à trois endroits :

- **`metriques.py`** mesure désormais le total, la durée estimée et le
  budget (`--idees`). C'est la bonne place — « ce script ne fait que
  compter », le jugement reste à A5.
- **A5** passe le budget et tranche : `ok`, `limite` (≤ +20 %, se resserre
  au calibrage) ou `depasse` (> +20 %, renvoi à A4). Un dépassement franc
  ne se coupe pas en mots, c'est une idée de trop.
- **A4** écrit sous budget : `idees_max` idées porteuses, ~45 mots chacune.
  Si la recherche donne six faits, il en garde trois.

**Vérifié sur le script réel de `2026-09-11_v01`** : 24 phrases, médiane
11 mots — les chiffres exacts du `state.json` — 258 mots, ratio **1,91**,
123 mots de trop. Le contrôle aurait crié à E3.

Et la durée estimée tombe à **80,6 s** contre 82,5 s réellement enregistrées :
**2,3 % d'écart**. Le débit de 3,2 mots/s est validé sur le terrain, et la
constante de `generer_storyboard.py` passe de 2,5 à 3,2 — c'était
l'arithmétique derrière les 16,4 s de décalage son/image.

## E6 — Les composants, repris

**Le système n'était pas monotone à cause de Remotion : il n'en utilisait
presque rien.** Les trois composants faisaient le même geste — deux
`interpolate()` linéaires, opacité et translateY, sur 0,3 s. `spring()`
n'apparaissait nulle part, aucun composant ne lisait `da`, et `Sequence`
juxtaposait les scènes sans transition.

Sur la scène 8 de `2026-09-11_v01`, qui dure 16 secondes : **0,3 s
d'animation, 15,7 s d'image fixe.**

Cause : A7 a écrit ces composants sans jamais voir le résultat, et tous les
critères vérifiables étaient au vert — le code compile, les props sont
typées, aucune couleur en dur. Le skill disait « suis le style de
`TitleCard.tsx` », ce qu'il a fait fidèlement : le patron du premier
composant s'est propagé aux deux suivants. Un agent optimise ce qu'on peut
lui reprocher.

### Ce qui a été fait

- **`composants/src/animation.ts`** implémente les huit règles une fois
  pour toutes : spring amorti, décalage d'entrée, variation de vitesse,
  anticipation, mouvement secondaire, parallaxe, wobble non répétitif,
  sortie qui ne coupe pas net. Les composants s'y branchent au lieu de
  réinventer le geste.
- **Les trois composants lisent `da`** : le vocabulaire de direction
  artistique posé plus tôt était inerte.
- **Le cadre est rempli** : le personnage passe d'un cinquième à ~40 % de
  la hauteur, les schémas occupent la largeur, un halo donne de la
  profondeur.
- **Les schémas portent enfin leur distinction** : un rail rigide traverse
  les étapes du chemin fixe, une boucle circulaire figure l'agent. Avant,
  « STEP 1 / STEP 2 » aurait illustré n'importe quel concept.
- **`intro` ≠ `outro`** : trois poses distinctes.
- **Fondu enchaîné de 0,25 s** entre scènes, sans dépendance
  supplémentaire — la scène suivante déborde sur la précédente, le calage
  sur l'audio est préservé.

### Corrigé en regardant, pas en testant

Deux défauts de dessin n'ont été vus que sur les aperçus : le trait du
corps **traversait la tête** du stickman (le cou partait d'une coordonnée
fixe alors que tête et torse respirent en déphasé), et le bras du salut
**disparaissait dans le crâne** (à −75°, il montait presque à la
verticale). Un troisième est apparu au rendu suivant : le rail barrait le
texte des étapes.

Aucun test ne pouvait les attraper. C'est exactement ce que le catalogue
existe pour rendre visible.

## CP3 — le rapport montrait le mauvais fichier

Le CP3 **autorise la publication**. Son rapport contenait le storyboard
entier — le plan de tournage — et sur la vidéo elle-même : rien. Pas le
chemin du `.mp4`, pas sa durée, pas le nombre de scènes rendues, pas les
composants créés. Il était même tronqué au milieu de « Nouveaux composants
neces… ».

Et le storyboard disait : *« ~98.8s, au-dessus d'un Short typique, à
trancher par Franco au CP3 »*. La décision avait bien été repoussée jusqu'à
lui — sans aucun des chiffres pour la prendre.

Le rapport porte désormais, dans cet ordre : le fichier et son poids, la
durée du rendu **face à celle de la voix off**, l'écart s'il dépasse une
seconde, les scènes laissées `a_completer`, les nouveaux composants, le
message du Monteur, puis un rappel de regarder la vidéo. Le storyboard
n'est plus qu'un rappel borné à 1200 caractères.

Vérifié sur le dossier reconstitué de `2026-09-11_v01` : l'écart de
**16,3 s** apparaît en troisième ligne.

## File d'attente

| # | Chantier | État |
|---|---|---|
| 1 | Point d'entrée : format, référence, idées, titre court | ✅ fait |
| 2 | Rapport de checkpoint tronqué avant la décision | ✅ fait |
| 3a | Catalogue d'aperçus de composants (`outils/generer_apercus.py`) | ✅ fait |
| 3b | Cadrage d'A6 : `05_cadrage.md`, décrire l'image et non la clé, doublon texte/sous-titres supprimé | ✅ fait |
| 3c | Composants repris : `animation.ts`, cadre rempli, `intro`≠`outro`, schémas parlants, transitions | ✅ fait |
| 4 | `outils/` + analyseur de structure + corpus + segmentation de la vidéo 1 | ✅ fait |
| 5 | E4 : plafond de tentatives dans le notebook, diagnostic WER gradué, agent cohérent | ✅ fait |
| 6 | Réajustement complet d'A2 (branche `sujet_impose`, gabarit 7 sections) | ✅ fait |
| 6b | Budget en idées appliqué par A4 et mesuré par A5 | ✅ fait |
| 7 | Constante 2,5 → 3,2 mots/s dans `generer_storyboard.py` | ✅ fait |
| — | *Plus tard* : outils qui rendent Remotion plus organique (d3-ease, `@remotion/noise`, rough.js) | ⬜ |

## Reste à diagnostiquer

CP2 sur fichier réel, H1 (jamais tourné, et son input « phrases signalées
par le contrôle qualité » n'existe plus depuis que le WER est global), E7
(neuf, jamais exercé).

Et une question transverse qui remonte d'E4 : **le déclenchement de
l'Orchestrateur**, non tranché depuis le §12. Tant qu'il ne tourne pas, tout
ce qu'on lui confie est décoratif.

## A3 — L'analyse de structure, et ce que la mesure reelle a corrige

`outils/analyser_transcription.py` remplace les notes en prose. Le LLM
segmente (reconnaître un hook demande de comprendre le propos), le script
compte et valide — même séparation que `metriques.py` pour A5. Le
vocabulaire des rôles est **fermé** : `hook`, `promesse`, `contexte`,
`idee`, `exemple`, `transition`, `cta`, `sponsoring`. Le corpus
`02_Veille_hebdo/corpus_structures.jsonl` est **append-only**.

La première ligne du corpus est `2026-09-11_v01`, segmentée à la main. Elle
a immédiatement invalidé trois choses que j'avais posées :

### 1. La règle « un seul hook » était fausse

Le hook réel tient en **deux phrases** — *« Everyone calls their product an
AI agent now. / Most of them are not agents at all. »* — figure classique,
pas une erreur. La règle est devenue : un rôle de ce type doit être
**contigu**, pas unique. Un hook dispersé dans la vidéo reste suspect.

### 2. Le débit de référence était faux de 14 %

J'avais mesuré 3,2 mots/s à partir du script **brut**, marqueurs de mise en
scène compris — `[intro — stickman face camera]`, 27 mots jamais prononcés.
Le script réellement dit fait **231 mots**, pas 258, soit **2,8 mots/s**.

`metriques.py` retire désormais ces marqueurs, et les deux constantes de
débit sont corrigées. Elles avaient été fausses dans les deux sens : 2,5
puis 3,2.

### 3. « Idée » n'avait pas la même granularité des deux côtés

Compter les segments donnait **12 idées** pour un budget de 3 : les trois
idées du script — LLM, workflow, agent — occupent douze phrases. On compte
donc les **blocs** (groupes explicites, sinon suites contiguës).

Et la mesure a révélé un écart dans le modèle de budget : les trois idées
ne pèsent que **115 mots sur 231**. Le hook, la promesse, l'exemple et le
CTA consomment l'autre moitié. Le budget de A5 se compare donc à
`cout_total_par_idee` — 45 mots **tout compris** — et non au coût des
seules idées, qui serait faux de moitié.

### Ce que ça dit de la méthode

Trois règles écrites de bonne foi, invalidées par la première donnée réelle.
Aucun test synthétique ne pouvait les attraper : ils validaient mes
hypothèses, pas le terrain. C'est l'argument le plus concret pour le corpus
— et pour segmenter les vidéos **avant** d'en produire six.

## Priorite revisee : le contenu qui marche avant le vecu

Franco a tranche (11/09/2026) : partir d'abord du **contenu tendance** de la
niche, pas de ses propres donnees. `projets_franco.md` reste donc un
brouillon facultatif, qui se remplira au fil des videos — A2 et A4 s'en
servent quand il est rempli, et prennent un exemple public verifiable
sinon, en le signalant au CP1.

**Ce qui devient le chemin critique**, et qui est aujourd'hui a zero :

| Maillon | Etat |
|---|---|
| `00_Profil/chaines_concurrentes.json` | **vide** — seul maillon manquant |
| `YOUTUBE_API_KEY` | ✅ configurée chez Franco |
| A3 analyseur de chaines | **jamais tourne** |
| `02_Veille_hebdo/*_analyse_concurrentielle.md` | **n'existe pas** |
| Corpus de structures | pas encore construit |

A2 signale deja lui-meme l'absence d'analyse concurrentielle dans ses
« Points a trancher ». Tant que cette chaine reste vide, « se baser sur le
contenu qui marche » n'a aucun support : on retombe sur l'intuition.

**Tension a garder en tete** : le §1 positionne la chaine sur « l'ingenieur
ML qui decode et **teste** ». Un sujet tendance traite sans vecu s'aligne
sur la niche mais affaiblit l'angle. Les deux se concilient — prendre un
sujet qui marche et l'ancrer dans un test reel — mais ca suppose de
remplir `projets_franco.md` a un moment.

## En attente de Franco

- La **vidéo de référence** pour caler le vocabulaire de segmentation.
- **La liste de chaînes concurrentes** (`chaines_concurrentes.json`) et une
  clé API YouTube : c'est le chemin critique du contenu tendance.
- `00_Profil/projets_franco.md` — facultatif désormais, à compléter au fil
  des vidéos. Fichier qu'il écrit, qu'aucun agent n'écrit.
- Le lexique de prononciation sur le Drive (entrées en épellation).
- La vidéo `2026-09-11_v01` est au CP3 avec 16,4 s de décalage son/image :
  à re-monter après un run audio produisant `04_phrases.json`.
