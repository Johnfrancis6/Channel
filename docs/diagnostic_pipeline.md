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
| `short-chercheur` | branche `sujet_impose` non écrite | ⬜ à faire |
| `short-chercheur` | gabarit sans hook, budget, hiérarchie des faits, incertitudes, termes à risque | ⬜ à faire |
| `short-chercheur` | échec sans critère : A2 ne peut structurellement pas échouer | ⬜ à faire |
| `short-chercheur` | `commencer` (qui incrémente `tentatives`) avant vérification des entrées | ⬜ à faire |
| Entrées | `chaines_concurrentes.json` vide, aucune analyse concurrentielle, aucun fichier projets | ⬜ à faire |

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

---

## File d'attente

| # | Chantier | État |
|---|---|---|
| 1 | Point d'entrée : format, référence, idées, titre court | ✅ fait |
| 2 | Rapport de checkpoint tronqué avant la décision | ✅ fait |
| 3 | Catalogue d'aperçus de composants + cadrage d'A6 (décrire l'image, pas la clé ; supprimer le doublon texte/sous-titres) | ⬜ |
| 4 | `outils/` + corpus + segmentation rétroactive de la vidéo 1 | ⬜ |
| 5 | E4 : 8 tentatives, `max_tentatives`=3, aucune alerte — 2 h 20 perdues | ⬜ |
| 6 | Réajustement complet d'A2 (branche `sujet_impose`, gabarit 7 sections) | ⬜ |
| 7 | Constante 2,5 → 3,2 mots/s dans `generer_storyboard.py` | ⬜ |
| — | *Plus tard* : outils du Monteur, qualité d'animation | ⬜ |

## Reste à diagnostiquer

E2 et E3 (où les 24 phrases se sont accumulées), CP2 et CP3 sur fichiers
réels, H1 et A3 (jamais tournés), E6 et E7.

## En attente de Franco

- La **vidéo de référence** pour caler le vocabulaire de segmentation.
- `00_Profil/projets_franco.md` — ce qu'il peut **montrer à l'écran**, pas
  seulement ce qu'il fait. Fichier qu'il écrit, qu'aucun agent n'écrit.
- Le lexique de prononciation sur le Drive (entrées en épellation).
- La vidéo `2026-09-11_v01` est au CP3 avec 16,4 s de décalage son/image :
  à re-monter après un run audio produisant `04_phrases.json`.
