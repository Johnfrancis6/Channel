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
durée = idées × mots_par_idée ÷ 2,8 mots/s   ← déduite, jamais imposée
```

Une interview fictive n'a pas plus d'idées qu'une explication : chaque idée
y coûte plus de mots, parce que le dialogue doit incarner et relancer. Elle
dépasse donc 60 s **sans déroger à la règle**. Le dépassement devient de
l'arithmétique prévisible en amont, au lieu d'être découvert au montage.

Le débit de référence est **2,8 mots/s**, mesuré sur `2026-09-11_v01` :
231 mots réellement prononcés pour 82,5 s de voix off, pauses comprises.
La constante a été fausse deux fois avant de se fixer — 2,5 à l'origine,
puis 3,2 quand je l'avais mesurée sur le script *brut*, marqueurs de mise
en scène compris.

Et `mots_par_idée` s'entend **tout compris** : l'idée plus sa part de hook,
de promesse, d'exemple et de CTA. Sur la vidéo réelle, les trois idées ne
pèsent que 115 mots sur 231 — un budget qui ne compterait que les idées
serait faux de moitié.

### Les formats se découvrent sur les 6 premières vidéos

Un format nouveau par vidéo, étude à la 6e ; si les résultats ne sont pas
clairs, on continue à en essayer.

**Deux conséquences à garder en tête :**

- **Le corpus doit exister avant la vidéo 2.** Si les six vidéos ne sont pas
  mesurées de la même façon dès la première, l'étude sera impossible : six
  vidéos, aucune donnée comparable. **Fait** : la vidéo 1 est la première
  ligne du corpus, segmentée rétroactivement depuis `03_script_tts.txt`.
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
maintenant** ; les outils qui rendraient Remotion plus organique (d3-ease,
`@remotion/noise`, rough.js) **après l'étude**, quand on saura quel style
on vise. Lottie, lui, a été écarté — voir plus bas.

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

Franco y dépose ses images d'inspiration. Lu par A6 (référence visuelle la
plus directe) et A7. Créé par `new_short.py` à côté de `checkpoints/`.

C'est aussi ce qui manquait pour que le dialogue de cadrage ait un support :
une référence visuelle n'a plus à repartir dans une note en texte libre.

### Le corpus est le seul actif qui prend de la valeur

Avant, **rien ne s'accumulait** dans tout le système : le rapport
hebdomadaire était un fichier neuf chaque semaine, et les notes d'A3 de la
prose indexée par chaîne, pas par vidéo. Un système qui n'accumule rien ne
peut rien apprendre.

`02_Veille_hebdo/corpus_structures.jsonl`, append-only, une ligne par vidéo
analysée. Démarré sur **nos propres vidéos** — on y a le texte exact et les
timings, donc une qualité supérieure à tout ce qu'on obtiendra des
concurrents.

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
| 8 | H1 : indicateurs tirés des `state.json`, rapports refusés lus, suivi des recommandations | ✅ fait |
| 9 | Déclenchement : lanceur cron `outils/lancer_orchestrateur.py` | ✅ fait — reste à installer la crontab chez Franco |
| 10 | E7 : les statuts de fin appartiennent à E7, abandon d'une vidéo, `programmee` → `publiee` sans `--force` | ✅ fait |
| — | *Plus tard* : outils qui rendent Remotion plus organique (d3-ease, `@remotion/noise`, rough.js) | ⬜ |

## Reste à diagnostiquer

**CP2 sur fichier réel** — le dernier du diagnostic étape par étape. Les
deux autres checkpoints montraient chacun un défaut qu'aucun test ne
pouvait attraper ; celui-ci se lira mieux sur le script de la prochaine
vidéo que sur celui de la vidéo 1, déjà au CP3.

H1 et E7 ont été réajustés (voir plus bas) mais n'ont **jamais tourné**.
Pour H1 il faut deux ou trois vidéos passées de bout en bout ; pour E7, une
première publication réelle.

La question transverse qui remontait d'E4 — **le déclenchement de
l'Orchestrateur** — est tranchée : cron toutes les 15 minutes (§6.4, plus
bas). Le lanceur est écrit et testé ; la crontab, elle, ne peut s'installer
que depuis la machine de Franco.

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

## H1 — Le bilan hebdomadaire cherchait des motifs sans avoir les faits

`rassembler_inputs.py` listait des chemins de fichiers. Tout le reste —
lire, compter, comparer — était laissé à l'agent. Quatre conséquences :

**1. Les données d'exécution n'étaient pas lues.** Le signal le plus fort
de la semaine du 11/09 — huit tentatives sur `E4_audio`, 2 h 20 perdues —
vit dans les `state.json`, qu'aucune ligne n'ouvrait. H1 était chargé de
trouver des motifs sans avoir les événements. C'est le même défaut qu'à
E4 : la règle existait, rien ne la faisait tourner.

**2. Rien n'était agrégé.** À trois vidéos, relire tous les rapports est
faisable ; à vingt, non. Le script calcule donc `tentatives_par_etape`,
`alertes`, `refus_checkpoints`, `boucles_redaction_filtre`,
`durees_production_h` — et s'arrête là. Il compte, il ne juge pas : même
partage que `metriques.py` pour A5, et que le LLM/script d'A3.

**3. Les traces résolues étaient invisibles.** Un refus repris remet le
checkpoint à `a_venir` (`engine._reagir_au_refus`) et une alerte traitée
disparaît de l'étape. En ne lisant que l'état courant, la semaine où un
problème est **corrigé** est aussi celle où il devient invisible — donc
celle où il n'entre jamais au bilan. Les deux sources sont désormais lues,
étape et historique, dédoublonnées sur le commentaire. Même raison pour
les tours A4↔A5 : un refus CP2 remet le compteur à zéro, seul l'historique
garde les tours perdus.

**4. Rien ne retenait ce qui avait déjà été proposé.** Sans mémoire des
semaines passées, H1 repropose chaque dimanche ce que Franco a refusé le
dimanche précédent, et le bilan perd sa crédibilité en trois semaines.
`03_Amelioration/recommandations.jsonl` (append-only, statut `proposee` →
`acceptee` / `refusee` / `appliquee`) est relu avant l'écriture du rapport.

Deux corrections plus petites : les **rapports refusés archivés** dans
`checkpoints/refuses/` — la trace la plus directe de ce que Franco rejette
— n'étaient pas ramassés ; et le corpus de structures n'était cité nulle
part dans le skill, alors que c'est lui qui permet de comparer nos vidéos
aux chaînes qui marchent.

**Une vidéo figée ne compte pas comme une vidéo produite.** Elle apparaît
dans `videos_actives` avec ses `jours_sans_activite` — être immobile est
un signal — mais ses compteurs n'entrent pas dans les indicateurs de la
semaine, sinon une vidéo abandonnée en mars fausserait tous les bilans
suivants.

**Input fantôme retiré.** Le §4.3 demandait à H1 « les phrases signalées
par le contrôle qualité » : le WER est global depuis la v1.1, cette liste
n'existe pas. Le skill dit maintenant ce qui existe vraiment — le diff
référence/transcrit, écrit **uniquement quand le WER échoue** et tronqué à
200 caractères — et c'est de là qu'un candidat au lexique se déduit.

Au passage, `boucle_A4_A5` est entré au schéma : le champ était écrit par
l'orchestrateur et lu par H1, mais absent du contrat documenté.

## Déclenchement — le cron, et le faux Drive qu'il aurait fabriqué

Franco a tranché le 12/09 : **cron**. C'était le dernier point qui rendait
tout le reste décoratif — une machine à états que personne ne fait avancer
ne fait rien avancer.

La tentation était de mettre `python -m orchestrateur.main --root ...`
directement dans la crontab. En le testant, le défaut est apparu tout de
suite, et il est sérieux :

> Lancé sur un dossier **vide** — le point de montage d'un Drive non monté
> existe presque toujours, vide — `main.py` écrit `registre_videos.json`,
> `TABLEAU_DE_BORD.md` et `01_Orchestrateur/derniere_execution.json`,
> **et sort 0**.

Trois conséquences en chaîne : cron ne signale rien (code 0) ; une fausse
racine locale apparaît, qui **masque le vrai Drive au remontage** ; et
`short-state` lit ensuite un tableau de bord parfaitement sain, vide de
toute vidéo. Le pipeline ne dirait pas « je ne trouve rien », il dirait
« il n'y a rien ». C'est exactement le genre de panne silencieuse que la
revue cherche depuis le début.

`outils/lancer_orchestrateur.py` place donc le garde-fou **avant toute
écriture** : la racine doit exister *et* contenir
`01_Orchestrateur/config.json`. Sinon, sortie 2, message sur stderr, rien
d'écrit.

Trois autres particularités de cron sont traitées au passage :

- **un verrou actif n'est pas une erreur.** `main.py` sort 1 ; à un passage
  tous les quarts d'heure, deux exécutions se chevauchent régulièrement, et
  un mail d'erreur à chaque fois finit par faire couper le cron. C'est une
  sortie 0 et une ligne « ignoré » ;
- **la sortie part en mail que personne ne lit.** Chaque passage écrit une
  ligne dans `01_Orchestrateur/journal_cron.log`, plafonné à 2000 lignes —
  le fichier est sur le Drive, il se synchronise. Seules les vraies erreurs
  vont sur stderr : le mail redevient un signal ;
- **pas de répertoire courant, PATH minimal.** `--verifier` imprime la ligne
  de crontab avec l'interpréteur et les chemins absolus déjà résolus, et
  **les espaces échappées** : un chemin Google Drive contient presque
  toujours « Mon Drive ». Sans guillemets, la ligne est cassée et l'erreur
  n'apparaît que dans ce mail que personne ne lit.

La cadence de 15 minutes vient du seuil existant : `short-state` alerte sur
un Orchestrateur muet depuis 6 h. Un quart d'heure laisse aussi le pipeline
repartir sans attendre après chaque validation de checkpoint.

**Ce qui n'est pas fait, et ne peut pas l'être d'ici** : la crontab elle-même.
Elle vit sur la machine de Franco. Trois commandes, §6.4.

## E7 — l'étape tenait, l'Orchestrateur la défaisait

E7 n'avait jamais été exercée. En la testant, le défaut trouvé est le plus
coûteux du lot, et il ne vient pas de E7 :

> `publier.py` écrit `statut_global = "publiee"`. Le passage suivant de
> l'Orchestrateur le réécrit en `prete`, parce que `CP3` est valide.

Le skill dit, à son étape 4, de relancer l'Orchestrateur juste après. **La
commande censée confirmer la publication la défaisait.** Et depuis
aujourd'hui, le cron la défait tout seul dans le quart d'heure. Les trois
symptômes sont exactement ceux que `short-publier` avait été écrit pour
corriger : compteur « Publiées » à zéro, tampon qui recompte comme
disponible une vidéo déjà en ligne, `short-state` qui propose de publier ce
qui est publié.

La règle manquante tient en une phrase : **au-delà de `prete`, le statut
appartient à E7.** L'Orchestrateur calcule jusqu'à `prete` ; `programmee`,
`publiee` et `abandonnee` ne se recalculent pas.

### L'abandon : lu par quatre endroits, écrit par personne

`abandonnee` existait dans l'enum du schéma. Le tableau de bord le compte
(« Abandonnées : N »), `short-state` sort ces vidéos du tampon,
`short-state` et `new-short` libèrent leur `sujet_id`. **Aucune ligne ne
l'écrivait.** Il n'y avait donc pas de sortie de secours : une idée laissée
tomber restait à vie dans le tampon, gardait son sujet réservé, et — parce
que le tableau de bord ne filtrait pas non plus — réclamait son agent à
chaque passage. `--statut abandonnee --motif "..."` ferme le cycle, sans
exiger de CP3 : on abandonne justement une vidéo qui n'y arrivera pas. Le
motif est obligatoire, c'est la seule trace de la raison et H1 la lit.

### Deux défauts plus petits

- **`programmee` → `publiee` exigeait `--force`.** Le code 8 protège contre
  l'écrasement accidentel, mais il s'appliquait aussi à `programmee`, qui
  n'est pas un état final. Le trajet nominal décrit par le skill — je
  programme, puis je publie — se heurtait donc au drapeau réservé aux
  corrections. Seuls les cycles clos sont désormais protégés.
- **L'URL n'était pas vérifiée.** C'est le champ par lequel H1 rapproche les
  performances YouTube des vidéos produites : une valeur qui n'est pas une
  adresse ne se voit que des semaines plus tard, au premier rapport.

### Ce que ça confirme, encore

Le bug de la résurrection ne vivait dans aucun des deux composants : ni
`publier.py` ni `_mettre_a_jour_statut_global` n'ont tort isolément. Il
vivait dans leur **articulation**, et aucun test unitaire des deux côtés ne
pouvait le voir. C'est la même leçon qu'aux composants Remotion, où trois
défauts n'ont été trouvés qu'en regardant les rendus : le dépôt teste ce
qui existe, pas ce qui devrait exister.

## En attente de Franco

- **Installer la crontab** : `python3 outils/lancer_orchestrateur.py --root "<racine>" --verifier`,
  puis coller la ligne affichée dans `crontab -e` (§6.4).
- La **vidéo de référence** pour caler le vocabulaire de segmentation.
- **La liste de chaînes concurrentes** (`chaines_concurrentes.json`) et une
  clé API YouTube : c'est le chemin critique du contenu tendance.
- `00_Profil/projets_franco.md` — facultatif désormais, à compléter au fil
  des vidéos. Fichier qu'il écrit, qu'aucun agent n'écrit.
- Le lexique de prononciation sur le Drive (entrées en épellation).
- La vidéo `2026-09-11_v01` est au CP3 avec 16,4 s de décalage son/image :
  à re-monter après un run audio produisant `04_phrases.json`.
