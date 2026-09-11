# Revue d'architecture — 11/09/2026

Relecture de fond du workflow et de l'architecture : la doc de référence
([architecture_chaine_v1.2.md](architecture_chaine_v1.2.md)) confrontée au
code réel (`orchestrateur/`, `agents/`, `composants/`, `notebooks/`).

**État de départ** : 114 tests au vert, `.claude/skills/` sans dérive,
vidéo `2026-09-11_v01` à `E6_montage`, `mode_agents="reel"`.

Ce document explique ce qui a été trouvé et pourquoi les décisions ont été
prises. La doc de référence, elle, dit ce que le système *est* : les deux
sont à lire ensemble, pas l'un à la place de l'autre.

---

## 1. Ce qui va bien

Il faut le dire avant le reste, parce que ça conditionne le niveau des
critiques qui suivent.

- **La machine d'états tient.** `state.json` est réellement la seule source
  de vérité, le registre est une vue reconstruite, aucun fichier n'est
  écrit par deux acteurs. L'Orchestrateur est sans mémoire et sans serveur,
  et ça se voit dans le code : `run_once()` fait exactement ce que §4.3
  décrit, dans l'ordre.
- **Les bugs corrigés l'ont été à la racine, avec le pourquoi en
  commentaire.** Le verrou illisible, le checkpoint refusé qui figeait la
  vidéo, le regex `DOTALL` de `lire_decision`, le `REGISTRE` mal parsé qui
  faisait recréer `TitleCard` : chaque correction porte la trace du
  symptôme observé. C'est ce qui rend cette revue possible.
- **Le garde-fou sur `.claude/skills/`** (`--verifier` + `test_sync_skills`)
  est exactement la bonne réponse à une dérive qui s'était déjà produite en
  silence.
- **La séparation prompt / script est juste.** Les scripts mesurent et
  appliquent le contrat `state.json` ; le jugement reste dans le `SKILL.md`.
  `metriques.py` le dit explicitement : « ce script ne fait que compter ».

## 2. Les quatre trous trouvés

Classés par gravité. Les trois premiers sont corrigés dans cette session.

### 2.1 Rien ne recalait les scènes sur l'audio *(corrigé)*

Le §4.3 promettait depuis la v1.1 : « A7 cale les scènes et les sous-titres
sur les timestamps mot par mot ». Les sous-titres, oui. Les scènes, non :
`construire_props.py` passait `storyboard["scenes"]` tel quel à Remotion,
avec les durées estimées par A6 à ~2,5 mots/s, et `calculateMetadata`
faisait durer la composition la somme de ces estimations.

Conséquences, dans l'ordre de gravité :

1. **la voix off était coupée** dès que l'estimation sous-évaluait l'audio ;
2. le visuel dérivait de la voix, cumulativement, dès la première phrase mal
   estimée — une scène en retard de 300 ms le reste jusqu'à la fin ;
3. personne ne s'en serait aperçu avant le CP3, puisque rien n'était vérifié
   visuellement (voir 2.3).

**Décision** : le notebook écrit `04_phrases.json` (bornes début/fin par
phrase), `construire_props.py --phrases` recale borne à borne, et
`duree_audio_s` garantit que la composition ne dure jamais moins que
l'audio. C'est le notebook qui produit cette donnée parce que c'est le seul
moment du pipeline où elle est *connue* : après coup, on ne peut que la
deviner en réalignant les mots transcrits sur le script, ce que le WER non
nul rend fragile.

**Ce que ça impose** : une scène par phrase. Si A6 fusionne des scènes, le
compte ne correspond plus ; le recalage est alors abandonné avec un
avertissement remonté à A7, plutôt qu'appliqué de travers.

### 2.2 Le cycle de vie d'une vidéo ne pouvait pas se fermer *(corrigé)*

`statut_global` ne dépassait jamais `prete`. Aucun code n'écrivait
`programmee`, `publiee`, ni `publication.date_effective` / `url` — alors
que le tableau de bord (`nb_publiees`) et `short-state` (`publiees_7j`,
calcul du tampon) les lisent tous les deux. Deux lecteurs, zéro écrivain.

Concrètement : le compteur « Publiées » serait resté à zéro pour toujours,
le tampon aurait compté comme disponibles des vidéos déjà en ligne, et la
seule façon d'avancer aurait été d'éditer `state.json` à la main — ce que
le §5.5 cherche précisément à éviter.

**Décision** : skill `short-publier`. Il refuse d'agir si le CP3 n'est pas
validé (§2), gère `programmee` (l'étape reste ouverte, la vidéo reste
visible au tableau de bord) et `publiee`, et refuse d'écraser une
publication déjà saisie sans `--force`.

### 2.3 On livrait un rendu jamais regardé *(corrigé)*

C'était déjà au backlog du §12. Le skill A7 lançait `npx remotion render` à
l'aveugle puis clôturait l'étape. Le premier humain à voir la vidéo était
Franco, au CP3 — donc chaque défaut visuel coûtait un refus, une reprise et
un tour complet.

**Décision** : étape « vérification visuelle » dans `short-monteur` —
`remotion still` sur le hook, un milieu et une fin, regardés avant de
rendre. Corriger sur une image coûte une fraction d'un rendu complet.

Au passage : le skill A7 ne mentionnait nulle part `rendre_video.py`, écrit
et testé à la session précédente, qui vérifie les prérequis avant et le MP4
après. Le prompt demandait la commande brute. Corrigé.

### 2.4 Le contrôle qualité audio a perdu son grain *(ouvert)*

Le §7.2 décrivait un contrôle par phrase, avec régénération automatique (3
tentatives) et signalement des phrases fautives. Le notebook réel fait un
**WER global** après assemblage, et c'est Franco qui relance.

C'est plus simple, et probablement le bon choix pour démarrer. Mais deux
choses en découlent, qu'il vaut mieux avoir dites :

- une seule phrase ratée fait échouer **tout** le run ;
- le rapport ne dit pas *laquelle*. Or le §4.3 donne « les rapports audio
  (phrases signalées par le contrôle qualité) » comme input de H1 : cet
  input n'existe plus.

**Décision** : on ne touche pas au notebook là-dessus maintenant. La doc dit
désormais ce que fait le code, et l'écart est consigné au §12 pour être
tranché sur des runs réels — le seul argument qui compte ici est la
fréquence du cas, et on ne l'a pas encore.

## 3. La direction artistique (question 1)

**Retenu : option (a)** — enrichir A6, pas d'agent Art Director.

Le raisonnement : la décision de style tient dans quatre champs par scène.
Un agent dédié aurait ajouté une étape à §6.2 (un statut de plus, un skill
de plus, un point de blocage de plus au tableau de bord) pour transporter
ces quatre champs d'un agent à l'autre. La séparation nette qu'il aurait
apportée, on l'obtient déjà en écrivant la DA dans le storyboard : A6
décide, A7 exécute, et l'un ne peut plus déborder sur l'autre sans que ça
se voie dans un fichier.

Deux niveaux, donc :

1. **Les principes récurrents** dans `charte.json > animation` — easing par
   défaut, durée d'entrée, règle du wobble, un mouvement dominant par scène,
   hook sobre. **Validés une fois avec la charte.** C'est le point important
   de la recommandation : ce qui est récurrent ne doit pas être redécidé à
   chaque vidéo, sinon la cohérence visuelle dépend de la constance d'un
   agent, pas d'une décision.
2. **La DA par scène** dans `05_storyboard.json`, champ `da` :
   `mouvement`, `rythme`, `technique`, `accent`.

**Le vocabulaire est fermé volontairement.** Un champ de style en texte
libre aurait juste déplacé l'improvisation d'un agent à l'autre : A7 aurait
interprété « dynamique, un peu joueur » comme il l'entend. Six mouvements,
trois rythmes, quatre techniques — A7 a une table de correspondance, pas une
marge d'interprétation.

**Effet de bord trouvé en chemin** : `generer_storyboard.py` mettait
`TitleCard` sur *toutes* les scènes, avec la phrase prononcée en paramètre
`texte`. Le rendu aurait donc affiché chaque phrase en gros à l'écran…
au-dessus des sous-titres qui affichent la même phrase. Le script ne produit
plus qu'un squelette, marqué `a_completer`, et A7 refuse désormais de monter
un storyboard dont des scènes portent encore cette marque.

## 4. Multi-chaînes (question 4)

**Retenu : analyse d'impact, décision « après la semaine de test ».**

La bonne nouvelle est que le point qui aurait coûté cher est déjà réglé : la
racine est paramétrable partout (`--root`, `CHAINE_YT_ROOT`, puis les
emplacements Drive habituels). Ce qui reste :

| Verrou | Où | Coût |
|---|---|---|
| Piliers figés | `new_short.py` (`PILIERS`), `schemas/state_schema.json` (enum), profil par défaut | le vrai chantier — à sortir dans un `profil_chaine.json` |
| Nom `ChaineYouTube` en dur | détection automatique de la racine | faible — une 2ᵉ chaîne passe `--root` |
| `REPO_ROOT = parents[3]` | `generer_storyboard.py`, `rendre_video.py` | `composants/` devient commun aux chaînes. Probablement souhaitable, mais alors la charte reste par chaîne et `REGISTRE.md` gagne une colonne |
| Pas de `--chaine` | tous les skills | mécanique, une fois les piliers sortis |

**Recommandation** : ne rien préparer maintenant. Généraliser sur un seul
exemple, c'est se tromper deux fois — une fois sur l'abstraction, une fois
sur ce qu'on découvrira en publiant vraiment. Le coût ne baissera pas en
attendant une semaine.

## 5. Doc contre code : ce qui avait dérivé

Toutes ces sections sont remises à jour.

| Section | Ce que la doc disait | Ce que le code faisait |
|---|---|---|
| §4.3 (A6) | une seule sortie, `05_storyboard.md` | `.md` **et** `.json`, plus un script de squelette |
| §4.3 (A7) | « cale les scènes sur les timestamps » | ne le faisait pas (§2.1) |
| §5.4 | exemple de `state.json` de la v1.1 | champs `version_schema`, `cree_le`, `consignes`, `sujet_id`, `seo`, `boucle_A4_A5`, `agent` sur E4/E7 |
| §7.2 | 9 cellules F5-TTS, QC par phrase | Qwen3-TTS, 4 modes, WER global, ordre des cellules différent |
| §7.4 | lexique en épellation (`L L M`) | convention abandonnée cette semaine — mais toujours semée par `profil_defaults.py` |
| §8 | « outil à trancher » | Remotion, tranché |
| §9.1 | ni `05_storyboard.json`, ni `04_phrases.json`, ni `checkpoints/refuses/`, ni `chaines_concurrentes.json` | tous présents |
| §9.2 | pas de `tests/`, pas de `.claude/skills/` | 114 tests, miroir généré |

**Le cas du lexique mérite un mot.** La convention « écriture normale
plutôt qu'épellation » avait été tranchée cette semaine, et l'action notée
comme « à faire côté Franco, sur le Drive ». Mais `L L M` était aussi dans
`orchestrateur/profil_defaults.py` : toute nouvelle installation aurait
re-semé la convention abandonnée. Corrigé dans le dépôt *et* dans la doc —
il reste bien une action sur le fichier Drive existant, mais elle ne se
reproduira plus.

## 6. Deux défauts plus petits, corrigés au passage

- **Sous-titres clignotants.** `Subtitles` cherchait le mot dont
  `debut_s <= t < fin_s`. Entre deux mots il y a toujours un silence : dans
  chacun de ces trous, la condition n'était vraie pour aucun mot et le
  composant renvoyait `null`. Les sous-titres disparaissaient **entre chaque
  mot**. Ils restent maintenant affichés pendant les silences ; seule la mise
  en avant du mot s'éteint.
- **Rapport audio trompeur.** Le rapport annonçait en dur « 22050 Hz,
  débruité, normalisé LUFS » alors que `DENOISE = False` depuis cette
  semaine. Les valeurs viennent maintenant des variables réelles.

## 7. Ce qui reste ouvert

Consigné au §12, pas traité ici :

- **contrôle qualité audio par phrase** (§2.4) — à trancher sur des runs réels ;
- **Lottie** (`@remotion/lottie`) pour le stickman — en attente d'un fichier de Franco ;
- **`statut_global: attente_franco`** — prévu au §5.3, jamais écrit. Soit on l'écrit, soit on le retire ;
- **seuil `[BLOQUE]` à 2 h** — un run Colab long déclencherait une fausse alerte ;
- **lexique de prononciation sur le Drive** — l'action côté Franco reste à faire (§5) ;
- **audit API YouTube** — à lancer pendant la phase test, c'est le long pôle du passage en publication automatisée (§11).

## 8. Une remarque de méthode

Trois des quatre trous de §2 ont la même forme : **une promesse de la doc
que personne n'exécutait**, et aucun test ne pouvait la contredire parce
qu'il n'y avait rien à tester. Le recalage des scènes, la clôture du cycle
de vie, la vérification visuelle : à chaque fois, du texte dans le §4.3 ou
le §12, et rien en face.

Le dépôt teste très bien ce qui existe. Ce qu'il ne teste pas, c'est ce qui
*devrait* exister. Une piste concrète, si on veut que ça ne se reproduise
pas : à chaque fois qu'une section de la doc décrit un comportement, se
demander quel test échouerait s'il disparaissait — et si la réponse est
« aucun », c'est peut-être qu'il n'a jamais existé.
