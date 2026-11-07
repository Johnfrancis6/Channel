# Audit du pipeline de production (Zehon, avant Whose Dime)

Session 1 du 07/11/2026. Portée : la chaîne de production seulement
(étapes, skills, fichiers, contrôles, reprises de session). La qualité
éditoriale et la veille sont pour la session 2.

Notes de travail : [`research_notes/Audit pipeline/`](../research_notes/Audit%20pipeline/)
([sources lues](../research_notes/Audit%20pipeline/sources_lues.md),
[mesures](../research_notes/Audit%20pipeline/mesures.md), [outils](../research_notes/Audit%20pipeline/outils/)).

**Comment lire ce rapport.** « Mesuré » veut dire refait ici par une
commande ou lu tel quel dans un fichier, avec sa source. « Hypothèse » veut
dire probable, mais pas prouvé. Les liens vers le code pointent sur la
branche `claude/optimistic-bohr-5f78k4`, celle du pipeline le plus récent.

---

## En bref

1. **Le pipeline contrôle la forme, jamais le fond.** Le vérificateur
   compte les mots, les phrases et les colonnes. Il ne compare jamais le
   script à la recherche, ni la publication au script. Mesuré : il donne
   « 0 erreur » au verre et à l'aluminium, alors que le verre contient
   5 ajouts absents de sa recherche et l'aluminium une citation sans source.
2. **Les « à vérifier » ne bloquent rien.** Sur le sel, le chiffre « 3 kilos
   par an » porte un « à vérifier » caché dans un commentaire HTML. La
   vidéo a été montée et validée avec. Cinq semaines plus tard, il n'est
   toujours pas vérifié.
3. **La publication ignore les corrections de la recherche.** La
   recherche du verre a retiré la prémisse « pas de vitre avant 1959 ». Le
   titre recommandé et une miniature la remettent.
4. **Quatre branches et trois fichiers d'état se contredisent.** Les
   lanceurs Colab de Drive tournent sur une branche figée, sans la
   dernière correction. Le contexte de reprise ignore la vidéo de
   l'aluminium. Une session qui reprend aujourd'hui part sur de fausses
   bases.
5. **Le script robotique naît de règles tirées d'une seule vidéo.** Le
   « Sauf que » obligatoire, les phrases courtes de longueur égale, le
   refus des personnages (« le procédé, pas la biographie ») et une
   recherche écrite comme une liste de faits donnent un exposé : 48
   chiffres en 8 minutes sur l'aluminium.
6. **La voix robotique naît du notebook.** Chaque phrase est synthétisée
   seule, sans la phrase d'avant, puis collée avec le même silence de
   300 ms partout. Rien ne mesure les fins coupées : le contrôle a déclaré
   0 phrase à réécouter sur le verre.

**Les 3 corrections qui comptent le plus** : un registre des faits que le
vérificateur compare au script et à la publication (C1) ; une seule branche
et un état de vidéo tenu à jour (C3, C4) ; la voix synthétisée par
paragraphe, avec des pauses variables et un détecteur de fins coupées (C6).

---

## 1. La cartographie de la chaîne réelle

« Claude » veut dire une session Claude Code avec la skill. « Franco » veut
dire un geste à la main. La dernière colonne dit ce qui ferme l'étape, ou
qu'il n'y a rien.

| # | Étape | Qui | Entrées | Sorties (Drive, `Videos/<nn>_<sujet>/`) | Ce qui la ferme |
|---|---|---|---|---|---|
| 0 | Reprise de session | Claude | `CONTEXTE.md` (dépôt), `Memoire/` (Drive), la liste des dossiers | — | **Rien** : aucune vérification que l'état lu est le vrai (§ 2.2, P2) |
| 1 | Sujet et angle | Claude, puis Franco | `Memoire/sujets.md`, API YouTube, web | 3 sujets dans le chat, dossier créé, `sujets.md` | **Pause 1** : Franco choisit |
| 2 | Recherche | Claude | web, description de Zelan | `01_recherche.md` | **Pause 2** : Franco valide l'angle et le hook. **Aucun contrôle des sources** |
| 3a | Plan | Claude | `01_recherche.md` | `02_plan.md` | **Pause 3**. Consigne « chaque fait du plan vient de la recherche », **sans outil** |
| 3b | Script et version voix | Claude | plan, recherche, `lexique.md` | `02_script.md`, `02_script_voix.txt` | `verifier.py` (forme) + **Pause 4** (Franco relit à l'œil). **Pas de comparaison au plan, à la recherche, ni script contre voix** |
| 4 | Scènes et prompts | Claude | script | `03_scenes.md`, prompts dans le chat | `verifier.py --script` : le texte dit redonne le script mot pour mot. **Le seul contrôle croisé qui bloque** |
| 5 | Publication | Claude | script, scènes | `04_publication.md` (titres, description, miniatures) | **Rien** : ni vérificateur, ni pause (« fin ») |
| 6 | Images, plans animés, miniatures | Franco (Gemini) | prompts | `images/`, `clips/`, `miniatures/` | Claude regarde les images que Franco lui montre (session 4) |
| 7 | Voix | Franco (Colab, lanceur Drive) | `02_script_voix.txt`, `Charte/voix/ref.wav` | `voix.wav`, `mots.json`, `etat.json` | Whisper retranscrit et signale les phrases à moins de 80 % de ressemblance. **Ne voit ni les fins coupées, ni le ton** |
| 8 | Montage | Franco (Colab), puis Claude lit le verdict | scènes, images, clips, voix | `video.mp4`, `rapport.json`, `verdict.json`, `apercu/`, `sous_titres.srt` | Contrôle technique (taille, son, durée) ; avertissement si une scène est mal retrouvée dans la voix (< 60 %), **non bloquant** |
| 9 | Visionnage et validation | Franco | `video.mp4` | décision « validée » | Franco seul ; rien n'est écrit sur ce qu'il a vérifié |
| 10 | Publication sur YouTube | Franco | `04_publication.md`, `.srt` | vidéo en ligne | Liste à cocher. **Jamais fait** : 0 vidéo publiée au 07/11 (`sujets.md`, section *Faits* vide) |
| 11 | Leçons | Claude | YouTube Studio | `Memoire/lecons.md` | — (pas de données : rien n'est publié) |

Le schéma en une ligne : **recherche → plan → script → (voix ‖ scènes) →
pièces → montage → publication**, avec quatre pauses humaines en tête et
**un seul contrôle croisé automatique** (scènes contre script).

---

## 2. Le diagnostic

Gravité : **haute** = une erreur peut sortir en ligne ou une session part
dans la mauvaise direction ; **moyenne** = elle coûte du temps ou se voit
mal ; **faible** = elle gêne sans risque.

### 2.1 Les deux symptômes : où ils naissent

#### Symptôme 1 : des scripts robotiques, formels, peu compréhensibles

Mesures sur le verre et l'aluminium ([mesures § 2](../research_notes/Audit%20pipeline/mesures.md)) :
phrases de 10 à 11 mots en médiane, très régulières (écart-type 4 à 5
mots) ; 7 et 9 « Sauf que » ; 20 et 48 nombres en chiffres ; 6 personnes
nommées et 1 seule citation sur tout le verre ; les débuts de phrase les
plus fréquents sont « Le », « Il », « Et », « En » et « Sauf ».

| # | Où ça naît | La consigne | Effet observé |
|---|---|---|---|
| S1 | Un modèle mesuré sur **une seule vidéo** devient une règle ([`etape3_script.md` l. 8-22][e3-8]) | « chaque temps finit sur un obstacle […] mot charnière : « Sauf que » ». Le vérificateur avertit s'il n'y en a pas ([`verifier.py` l. 98-99][v-98]) | Un tic : 7 blocs sur 12 du verre finissent par « Sauf que ». Certains obstacles ne sont jamais repris (verre, T2 : « ces premières perles […] sont opaques » ; T5 : « plus il est fin, plus il est fragile ») |
| S2 | Des longueurs de phrase bornées des deux côtés ([`etape3` l. 73-74][e3-73], [l. 105-106][e3-105]) | « médiane autour de 12 mots, aucune au-delà de 25 » ; version voix « 8 à 18 mots, jamais plus de 22 » | Un débit haché, sans phrase longue pour respirer ni phrase très courte pour frapper |
| S3 | Le refus des personnages ([`chaine.md` l. 14-18][ch-14]) | « Ce qui intéresse le public, c'est le procédé, pas la biographie » ; personnages anonymes en exemple (« un potier », « les mineurs », [`etape3` l. 77-79][e3-77]) | Personne à suivre ; pas de point de vue ; une seule citation |
| S4 | La recherche écrite comme une liste ([`etape2_recherche.md` l. 21-25, 55-77][e2-21]) | « Une ligne suffit : le fait, puis le lien » ; « Moments forts : – fait étonnant — source » | Le script devient une suite de faits : sur l'aluminium, un nombre toutes les 9 secondes |
| S5 | Un ton fixé à « calme » ([`chaine.md` l. 32-35][ch-32]) | « Le suspense vient de la structure, pas du ton » | Pas d'humour, pas d'étonnement, pas de « je » ni de « nous » du narrateur |
| S6 | Un script **validé à l'œil** ([`SKILL.md` l. 94][sk-94], pause 4) | Franco « relit » ; personne n'écoute avant la synthèse | Les phrases écrites pour être lues passent (« Nous sommes au premier siècle avant notre ère », « Divulguer un secret peut valoir la mort ») |

**Hypothèse sur la cause de fond** : chaque règle est raisonnable seule,
mais elles poussent toutes dans le même sens (moins de personnes, plus de
faits, phrases égales, ton plat), et le vérificateur récompense ce sens-là.
Aucune règle ne mesure « est-ce qu'on a envie d'écouter ».

#### Symptôme 2 : une voix robotique, monotone, des fins sèches

| # | Où ça naît | Le réglage | Effet |
|---|---|---|---|
| V1 | [`voix_zehon.ipynb`, cellule 4][nb] | Une synthèse `generate_voice_clone` **par ligne**, sans la ligne d'avant | Le modèle ne sait pas que la phrase suit une question ou continue une liste : chaque phrase repart avec la même intonation d'annonce. **C'est la cause la plus probable de la monotonie** (hypothèse forte, à tester en C6) |
| V2 | Cellules 1 et 5 | `PAUSE_MS = 300` entre **toutes** les lignes | Un métronome : même pause après une virgule devenue fin de ligne, après une question, à la fin d'un bloc |
| V3 | [`etape3` l. 105-106][e3-105] | « une phrase par ligne […] coupe les phrases longues » | Plus de coupures, donc plus de remises à zéro (V1). Ex. verre : « Et puis quinze pour cent de soude, et neuf pour cent de chaux. » dite seule |
| V4 | Cellule 5 | Aucun silence de fin demandé au modèle, aucun fondu, aucune mesure de la fin de chaque clip | Les fins coupées passent. Mesuré : le verre a `a_reecouter` = [] alors que ~1 phrase sur 6 finit sèche ([`CONTEXTE.md` l. 14-15][ctx-14]). Le contrôle Whisper ne voit pas un dernier son coupé : le mot reste reconnu |
| V5 | [`chaine.md` l. 25-28][ch-25] | La référence est un extrait de **7,4 s** d'une voix **ElevenLabs**, clonée par le modèle *Base* (sans consigne de style) | Hypothèse : un clone de voix de synthèse, sur un extrait court, n'a qu'une seule « couleur » à imiter |
| V6 | `lecons.md` l. 9 et 14 | 3,69 mots/s en parole, 9 % plus vite que Zelan | Pressé ; aggrave V2. L'observation « allonger les pauses » n'a jamais été appliquée |
| V7 | Pas d'étape d'écoute | Franco écoute la voix pour la première fois au montage | Le défaut se voit après 22 min de synthèse et 45 min de rendu |

**Note sur la mesure « 1 phrase sur 6 »** : elle est dans `CONTEXTE.md`,
pas dans `historique.md`, sans méthode ni données. Elle n'est donc pas
reproductible. À remesurer avec l'outil de C6.

### 2.2 Les points de défaillance, par priorité

#### Priorité 1 : erreurs de faits

| # | Défaut | Preuve | Gravité |
|---|---|---|---|
| F1 | **Le script ajoute des faits absents de la recherche**, sans que rien ne le voie | Verre : « il y a environ 3 400 ans », « il y a 3 000 ans », lingots « bleu foncé », « pendant des siècles », glaces « dans les châteaux ». Aluminium : une citation d'« un maréchal » (« Plus d'un homme, plus d'un cheval… ») absente de la recherche et du plan (recherche plein texte Drive). [Mesures § 4](../research_notes/Audit%20pipeline/mesures.md). La règle « Rien d'inventé » ([`etape3` l. 84-85][e3-84]) n'a pas d'outil | **Haute** |
| F2 | **« À vérifier » est invisible et ne bloque rien** | Sel, `02_script.md` : « Toi, tu en manges environ 3 kilos par an. `<!-- 8,1 g/jour, Esteban : à vérifier -->` ». Le vérificateur efface les commentaires ([`verifier.py` l. 55][v-55]). Vidéo validée le 30/09 ; toujours ouvert dans [`CONTEXTE.md` l. 51][ctx-51] | **Haute** |
| F3 | **La publication contredit la recherche** | Verre : la recherche v2 déclare fausse la prémisse « aucune vitre transparente avant 1959 ». Le titre recommandé (« Pourquoi a-t-il fallu 4 000 ans pour faire une vitre ? ») et la miniature M2 (« NÉE EN 1959 ?! ») la gardent ; la description présente le Bélus, une légende, comme l'origine. L'étape 5 n'a ni vérificateur ni pause | **Haute** |
| F4 | **La première recherche contient des erreurs, et la relecture n'est pas une étape** | Verre, v1 : 9 affirmations retirées en v2 (section « Retiré de la v1 » : la prémisse du hook, Pline déformé, deux dates fausses, quatre faits sans source). Rattrapé par une relecture le 01/10, qui n'est écrite nulle part dans la skill. Plusieurs faits lus seulement « (extrait) » d'un moteur de recherche | Moyenne |
| F5 | **La pause humaine ne voit pas les sources** | Aluminium : « script validé tel quel par Franco » (`sujets.md`), avec la citation sans source. La pause 4 demande « les 2 passages dont tu es le moins sûr » ([`etape3` l. 133-135][e3-133]), pas la liste des faits sans source | Moyenne |
| F6 | **Le titre promet plus que la vidéo ne montre** | Aluminium : titre recommandé « Pourquoi l'aluminium valait-il plus cher que l'or ? ». Le corps ne le montre jamais ; il dit « à peu près le prix de l'argent » (1859). Le fait est sourcé dans la recherche (1852 : 34 $ l'once contre 19 $ pour l'or), mais il n'est dit qu'en une demi-phrase du hook | Moyenne |

#### Priorité 2 : erreurs de processus

| # | Défaut | Preuve | Gravité |
|---|---|---|---|
| P1 | **Quatre branches, aucune n'est « la bonne » partout** | Lanceur voix Drive : `BRANCHE = "claude/zelan-studio-analysis-rws9f6"` (figée à `15b0fe0`). `CONTEXTE.md` dit que la branche des lanceurs est `optimistic-bohr`. `main` (`f5ceed8`, 30/09) n'a pas `video-maker`. La branche de travail de cet audit part de `main` et porte une `content-maker` ancienne (28 fichiers d'écart). **Conséquence mesurée** : le verdict du verre porte `zelan…@15b0fe0`, donc **sans** le bandeau `53fac3b` ; le « rendu à refaire » de `CONTEXTE.md` reproduirait le même défaut | **Haute** |
| P2 | **Les fichiers d'état mentent** | `CONTEXTE.md` ignore `03_aluminium` (contenu fini le 01/10 à 17:27) et propose « le pain, le sucre ». `sujets.md` dit sel et verre « reste : images, voix, assemblage » alors qu'ils sont rendus. Le `etat.json` du sel liste encore 19 phrases « à réécouter », déclarées fausses alertes ([`historique.md` l. 94-97][hi-94]) | **Haute** |
| P3 | **Un extrait écrase le verdict de la vidéo entière** | Sel : `verdict.json` décrit `extrait_001-010.mp4` (23:35), pas le rendu complet (21:21). Noms fixes dans [`monter.py` l. 1180-1181][mo-1180] et dans le notebook de montage | Moyenne |
| P4 | **Les cibles chiffrées se contredisent** | `lecons.md` : « environ 1 610 mots pour 8 min » (3,36 mots/s pauses comprises). [`verifier.py` l. 22, 106, 128][v-22] : 1 400-1 560 mots, 3 mots/s. [`SKILL.md` l. 211][sk-211] dit de reporter `debit_mots_s`, qui vaut 3,69 (parole seule) : on écrirait 1 771 mots. La règle « `lecons.md` gagne » ([`etape3` l. 24-27][e3-24]) n'est appliquée par aucun outil | Moyenne |
| P5 | **Les noms de fichiers ne suivent pas la règle** | Règle : `clips/scene_NNN.mp4` ([`etape4` l. 33][e4-33], [`verifier.py` l. 177][v-177]) ; réalité Drive : `anim_NNN.mp4`. Règle : `planche_bonhomme.png` ; réalité : `.jpg`. [`etape1` l. 67-68][e1-67] crée 3 sous-dossiers, [`SKILL.md` l. 152-155][sk-152] en veut 5. `monter.py` tolère tout, ce qui masque l'écart | Faible |
| P6 | **Deux copies de la skill, sans numéro de version** | Cette session charge `content-maker` (dépôt) et `anthropic-skills:content-maker` (claude.ai). Hypothèse : elles divergent ; rien ne permet de le savoir | Moyenne |
| P7 | **La boucle de retour n'existe pas** | 3 vidéos produites, 0 publiée au 07/11. `lecons.md` n'a aucune ligne de résultats. Les chapitres de la description restent « --:-- » : aucune étape ne les remplit depuis `rapport.json` | Moyenne |
| P8 | **Les tests ne tournent pas dans un conteneur neuf** | 1 erreur de chargement (`No module named 'cv2'`), puis 26 tests verts après installation. Aucun test sur les contrôles entre fichiers | Faible |

Point positif mesuré : **aucun doublon** dans les dossiers Drive lus. La
règle « nouvelle version, puis l'ancienne à la corbeille » fonctionne.

#### Priorité 3 : incohérences entre étapes

| Paire | Contrôlée ? | Constat |
|---|---|---|
| Recherche → plan | Non (consigne seule) | Pas mesuré ici (plans non lus) |
| Recherche → script | **Non** | F1, F2 |
| Plan → script | **Non** | Pas mesuré ici |
| Script → version voix | **Non** | Verre : fidèle (similarité 0,990, 15 écarts voulus), mais seulement parce que le modèle a bien travaillé. Les sous-titres affichent le script : si la voix s'en écarte un jour, rien ne le dira |
| Script → scènes | **Oui** (`verifier.py --script`) | — |
| Scènes → voix | Avertissement non bloquant (< 60 %) | Sel : toutes les scènes retrouvées à 80 % ou plus ([`historique.md` l. 34-37][hi-34]) |
| Script → titre, description, miniatures | **Non** | F3, F6 |
| Recherche « retiré » → publication | **Non** | F3 |
| Code utilisé → code attendu | **Non** | P1 |

---

## 3. Les corrections proposées

Classées par effet attendu sur tes trois priorités. Pour chacune : ce qui
change, où, comment on vérifie qu'elle marche. **Aucune n'est appliquée** :
j'attends ton accord, puis je les fais une par une, avec les tests et la
synchronisation des skills.

Étiquettes : **[Z]** vaut pour Zehon ; **[WD]** à faire avant de copier le
pipeline pour Whose Dime ; **[à adapter]** suppose un procédé, à réécrire
pour un conteur de dirigeants nommés.

### C1. Un registre des faits, contrôlé par le vérificateur [Z] [WD]

*Effet attendu : le plus fort sur les erreurs de faits (F1, F2, F5, F6).*

- **Ce qui change** : `01_recherche.md` gagne un tableau `| id | fait |
  valeur | source | lu en entier ? |`. Le script reste libre dans sa forme,
  mais chaque nombre, date, nom propre et citation doit correspondre à une
  ligne du registre. « À vérifier » s'écrit `[À VÉRIFIER : …]` en clair,
  jamais en commentaire.
- **Où** : `etape2_recherche.md` (format), `etape3_script.md` (règle),
  `verifier.py` (nouveau contrôle `--recherche 01_recherche.md` : nombres,
  dates, noms propres, guillemets absents du registre → avertissement ;
  `[À VÉRIFIER` → **erreur** pour la version voix, les scènes et la
  publication), tests.
- **Vérification** : rejouer sur les fichiers réels. Le contrôle doit
  signaler sur le verre « 3 400 », « 3 000 » et « bleu foncé » ; sur
  l'aluminium, la citation du maréchal ; sur le sel, le « 3 kilos ».
  Seuil : au plus 5 fausses alertes par script.
- **Whose Dime** : c'est déjà le `02b_factcheck.md` du plan d'action. On
  écrit l'outil une fois, pour les deux chaînes.

### C2. La publication relue contre la recherche [Z] [WD]

*Effet : F3, F6.*

- **Ce qui change** : chaque titre et chaque texte de miniature cite l'id
  du fait qui le justifie. La section « Retiré » de la recherche devient
  une liste de phrases interdites. La publication passe le vérificateur.
- **Où** : `etape5_publication.md`, `verifier.py` (`04_publication.md
  --recherche`), tests.
- **Vérification** : sur le verre, le titre 1 et M2 sont signalés ; sur
  l'aluminium, le titre est accepté seulement si le corps du script dit
  le fait « plus cher que l'or ».

### C3. Une seule branche pour la production [Z] [WD]

*Effet : P1, et une partie de P6.*

- **Ce qui change** : on fusionne `optimistic-bohr` dans `main`. Les deux
  lanceurs Drive passent `BRANCHE = "main"`, une fois pour toutes (toi,
  dans Colab : un champ à changer). Les branches de session ne servent
  qu'au développement et se fusionnent en fin de session. `CONTEXTE.md`
  dit « production : `main` ».
- **Où** : dépôt (fusion), lanceurs Drive, `CONTEXTE.md`, `SKILL.md`
  (« Les sessions »).
- **Vérification** : le prochain `verdict.json` porte `main@<dernier
  commit>`. Le lanceur affiche ce commit au démarrage.

### C4. Un état de vidéo qui dit la vérité [Z] [WD]

*Effet : P2, P3, P7.*

- **Ce qui change** :
  - `sujets.md` suit **toutes** les étapes, pas seulement le contenu :
    pièces, voix, rendu, validation, publication ;
  - `CONTEXTE.md` liste les dossiers de `Videos/` et leur étape, recopiés
    depuis `sujets.md` en fin de session ;
  - `verdict.json` et `apercu/` prennent le nom de la sortie
    (`verdict_extrait_001-010.json`) : un extrait n'écrase plus rien ;
  - le notebook de voix réécrit `etat.json` en entier à chaque lancement ;
  - `monter.py` écrit les chapitres (`chapitres.txt`) à partir des scènes
    `titre`.
- **Où** : `memoire.md`, `SKILL.md`, `monter.py`, `voix_zehon.ipynb`,
  `montage_zehon.ipynb`, tests.
- **Vérification** : une session neuve en Haiku 4.5, à qui on demande
  seulement « où en sont les vidéos ? », répond juste pour les trois sans
  autre aide.

### C5. Une seule source pour chaque chiffre-cible [Z]

*Effet : P4.*

- **Ce qui change** : le notebook écrit `debit_parole` et `debit_total` ;
  `lecons.md` garde `debit_total` ; le vérificateur lit la cible de mots
  dans une constante mise à jour avec `lecons.md` (1 610 aujourd'hui).
- **Vérification** : un test qui échoue si les deux valeurs divergent.

### C6. La voix : par paragraphe, pauses variables, fins mesurées [Z] [WD]

*Effet : symptôme 2 (V1 à V4, V7).*

- **Ce qui change** :
  1. La synthèse prend **un bloc de 2 à 4 phrases** à la fois, au lieu
     d'une ligne. La version voix garde une phrase par ligne, avec une
     ligne vide entre les blocs.
  2. Les pauses suivent la ponctuation : environ 250 ms après un point,
     450 ms après une question, 700 ms à la fin d'un bloc (valeurs à régler
     à l'oreille).
  3. Un **détecteur de fin sèche** : si le dernier mot retranscrit finit
     à moins de 60 ms de la fin du clip, ou si le son est encore fort dans
     les 30 dernières ms, la phrase est refaite avec une autre graine,
     deux fois au plus, puis signalée.
  4. Un **essai d'écoute** avant la synthèse complète : le hook et un
     bloc, environ 60 s, que tu écoutes et valides.
- **Où** : `voix_zehon.ipynb` (cellules 4 et 5), `etape3_script.md`
  (version voix), `SKILL.md` (session 4).
- **Vérification** : sur le verre, refaire 20 phrases des deux façons et
  les écouter **à l'aveugle** (je fournis le tableau de correspondance
  après ton vote). But : moins d'une fin sèche sur 30, et l'ancienne façon
  préférée moins d'une fois sur quatre. La ressemblance Whisper ne doit pas
  baisser.
- **Hypothèse à tester ensuite**, pas avant : une référence plus longue
  (20 à 30 s, plusieurs intonations) ou une voix humaine.

### C7. Retirer les règles qui fabriquent le style robotique [Z] [à adapter]

*Effet : symptôme 1. C'est la partie « chaîne de production » ; le fond de
l'écriture est pour la session 2.*

- **Ce qui change** :
  - le vérificateur ne réclame plus « Sauf que » ; il avertit au contraire
    au-delà de 3 ;
  - il avertit si les phrases sont trop régulières (écart-type de longueur
    sous 5 mots) et s'il y a plus d'un nombre pour 40 mots ;
  - la recherche gagne une rubrique « scènes » : 3 moments racontables,
    avec une personne, un lieu, un geste, et ce qu'elle voit ou dit
    (sourcé) ;
  - la pause 4 se fait **à l'oral** : Franco écoute l'essai de C6.4, il ne
    se contente plus de lire.
- **Où** : `verifier.py`, `etape2_recherche.md`, `etape3_script.md`,
  `chaine.md` (la phrase « le procédé, pas la biographie » devient
  « le procédé, raconté par ceux qui l'ont fait »).
- **Vérification** : la grille Exact / Clair / Vivant du journal, avant et
  après, sur les deux prochains scripts ; but : « Vivant » gagne au moins
  1 point sans que « Exact » baisse.

### C8. Les noms, les versions et les tests [Z] [WD]

*Effet : P5, P6, P8.*

- Les règles suivent la réalité : `clips/anim_NNN.mp4`,
  `planche_bonhomme.jpg`, 5 sous-dossiers partout.
- `SKILL.md` porte une ligne `version : <date>-<commit>` écrite par
  `synchroniser_skills.py` ; la skill la dit en une ligne au démarrage. La
  copie claude.ai est soit supprimée, soit rechargée à chaque
  synchronisation.
- Un script de démarrage du conteneur installe OpenCV et FFmpeg.
- **Vérification** : `python3 -m unittest discover -s tests` vert dans un
  conteneur neuf ; les deux copies de la skill affichent la même version.

### Ce qu'il faut adapter avant de copier pour Whose Dime

Zehon raconte un **procédé**, en français, sans personnage central.
« Who Pays? » raconte des **dirigeants nommés et leurs décisions**, en
anglais. Ces parties-là ne se copient pas :

| Élément de Zehon | Pourquoi il ne marche pas pour « Who Pays? » | À faire |
|---|---|---|
| Structure : hook + 4 questions en 10 temps, « Sauf que » ([`etape3`][e3-8]) | Elle découpe un procédé dans le temps. Le plan d'action prévoit 6 temps centrés sur **la décision** et **le trajet du dollar** | Réécrire l'étape 3 sur les 6 temps du plan d'action ; contrôles : question du titre avant 0:40, une décision datée avec ses personnes, un payeur, un montant et une source à chaque étape de l'engrenage |
| « Le procédé, pas la biographie » ([`chaine.md`][ch-14]) | C'est l'inverse : la personne et sa décision font le récit | Un **registre des personnes** : nom, rôle, date, décision, citation exacte avec sa source. Toute citation entre guillemets doit y figurer mot pour mot (risque juridique sur des personnes réelles) |
| Recherche « légère » | Chiffres d'entreprises : 10-K, rapports annuels, presse datée | Le registre de C1 devient `02b_factcheck.md`, **signé par Franco**, et il bloque la voix |
| Version voix française (nombres, sigles, lexique) | En anglais : « $34 », « 3.5% », « Q3 », « 10-K », « EBITDA », noms propres anglais | Nouvelles règles de version voix et nouveau lexique ; même diff script contre voix |
| Vérificateur : appel à s'abonner interdit | Le plan veut un pont vers l'épisode suivant et une question en commentaire | Inverser la règle : la fin **doit** annoncer la vidéo suivante ; interdire en revanche les phrases de conseil financier |
| Scènes : 60 à 80 images Gemini, texte animé d'un mot ([`etape4`][e4-33]) | 85 à 95 scènes dont 25 à 30 graphiques tirés du fact-check | Un type de scène `graphique`, généré par code depuis `02b_factcheck.md` ; le contrôle vérifie que chaque graphique cite un id du registre |
| Miniatures : bonhomme, émotion exagérée | Caricature du dirigeant, pastille « WHO PAYS? », pas de logo exact | Règles de miniature réécrites ; vérification « marques et personnes réelles » |
| Voix : clone d'une voix ElevenLabs | VoiceDesign en anglais, test à l'aveugle | Garder C6 tel quel (il ne dépend pas de la langue) |

**Ce qui se copie tel quel** : le registre et les contrôles de C1 et C2,
une seule branche (C3), l'état tenu à jour (C4), la synthèse par
paragraphe et le détecteur de fins sèches (C6), les noms et versions (C8),
le protocole de critique.

---

## 4. Les questions

Groupées. Pour chacune, ma recommandation.

**A. Les branches et l'état**
1. Je fusionne `optimistic-bohr` dans `main` et tu passes `BRANCHE` à
   `main` dans les deux lanceurs Drive ? **Je recommande oui** (C3) : c'est
   la cause du bandeau manquant.
2. La vidéo de l'aluminium (`03_aluminium`, contenu fini le 01/10) est-elle
   toujours prévue ? **Je recommande de l'inscrire dans `CONTEXTE.md`**,
   même gelée, pour qu'aucune session ne reparte sur « le pain ».
3. Zehon : on publie le sel, ou on gèle la chaîne pour Whose Dime ?
   **Je recommande de publier le sel** après C1 sur son script : c'est la
   seule façon d'avoir des chiffres dans `lecons.md`. Ta réponse dit aussi
   combien de corrections valent la peine sur Zehon.

**B. Les faits**
4. On adopte le registre des faits (C1) pour Zehon, au prix d'environ
   10 minutes de plus par recherche ? **Je recommande oui** : c'est le même
   outil que le fact-check de Whose Dime.
5. Un `[À VÉRIFIER]` bloque la voix et la publication ? **Je recommande
   oui.**
6. Le « 3 kilos par an » du sel : je le vérifie, ou on coupe la phrase ?
   **Je recommande de le vérifier** dans une source de santé publique
   française ; sinon on coupe.
7. Verre : je propose un autre titre et une autre miniature que « NÉE EN
   1959 ?! » ? **Je recommande oui**, par exemple « Le verre a 4 000 ans.
   Pourquoi ta vitre est-elle si plate ? ». Aluminium : je retire la
   citation du maréchal si je ne lui trouve pas de source ? **Oui.**

**C. La voix**
8. On fait le banc d'essai de C6 sur 20 phrases du verre, écoutées à
   l'aveugle ? **Je recommande oui**, avant de toucher au reste.
9. Tu acceptes une écoute de 60 s avant chaque synthèse complète ?
   **Je recommande oui** : elle évite 22 minutes de synthèse pour rien.

**D. L'écriture (partie pipeline)**
10. Je retire l'obligation de « Sauf que » et j'ajoute les avertissements
    de régularité (C7) ? **Je recommande oui.**
11. La pause 4 se fait à l'oral plutôt qu'à la lecture ? **Je recommande
    oui.**

**E. Whose Dime**
12. Une skill séparée (`whosedime-maker`) qui partage le vérificateur et le
    notebook de voix, plutôt qu'une `content-maker` à deux modes ?
    **Je recommande la skill séparée**, avec un module commun dans le dépôt.
13. Le fact-check signé par toi bloque la voix et le montage ? **Oui.**

**F. Le journal de critiques**
14. Tu notes les livrables déjà produits (scripts du sel, du verre et de
    l'aluminium, voix du sel et du verre) ? **Je recommande oui** : 5
    lignes de plus vers les 30 critiques nécessaires à la skill de
    détection.

---

## 5. Première ébauche : la skill de détection d'incohérences

**Ce que c'est** : un contrôleur qui passe après chaque étape, et en entier
avant la voix et avant la publication. Il compare les fichiers entre eux et
renvoie une liste de défauts typés comme le journal (`fait`,
`incoherence`, `processus`, `robotique`, `formel`, `nuance`,
`comprehension`, `voix`), chacun avec le fichier, la ligne et la phrase.

**Ce n'est pas encore à construire.** Le protocole le dit : environ 30
critiques notées d'abord. Ce plan dit ce qu'on construira, et comment le
journal servira à le régler.

### Quand il passe, sur quels fichiers

| Moment | Fichiers | Contrôles principaux |
|---|---|---|
| Après la recherche | `01_recherche.md` | registre complet (chaque fait a une source et « lu en entier ? ») ; pas de `[À VÉRIFIER]` sur le paradoxe du hook |
| Après le plan | plan, recherche | chaque fait du plan est dans le registre ; budget de mots par bloc |
| Après le script | script, voix, plan, recherche, lexique | faits hors registre ; écart au plan (blocs, obstacles, moments forts) ; diff script contre voix (seuls écarts permis : lexique, nombres, liaisons) ; mesures de style (régularité, chiffres par minute, connecteurs répétés) |
| Après les scènes | scènes, script, prompts | déjà fait (texte dit) ; + chaque prompt parle de ce que dit la scène (mots-clés communs, ou jugement du modèle) |
| Après la publication | publication, script, recherche | chaque promesse du titre et de la miniature est dite dans le script ; aucun fait retiré ; chapitres égaux aux titres |
| Après la voix | `etat.json`, `mots.json`, voix | fins sèches, pauses, débit, phrases mal retrouvées |
| Avant la reprise d'une session | `CONTEXTE.md`, `sujets.md`, liste Drive, `verdict.json` | l'état écrit correspond aux fichiers présents ; le code du verdict est celui de `main` |

### Deux moteurs

1. **Un script déterministe** (comme `verifier.py`) pour tout ce qui se
   compte : registre, diff, noms, état, chiffres, fins sèches.
2. **Un passage de jugement par le modèle**, avec une grille fixe, pour ce
   qui ne se compte pas : une promesse de titre tenue, un obstacle repris,
   une phrase trop longue pour l'oreille. Chaque jugement cite la phrase.

### Comment le journal le règle

- Chaque ligne du journal devient un **cas de test** : le livrable, le
  défaut, l'endroit.
- On mesure deux taux : **la part des défauts vus par Franco
  (`"vu_par": "franco"`) que le contrôleur aurait trouvés avant lui**, et
  le nombre de fausses alertes par livrable.
- Un contrôle n'entre que s'il attrape au moins un cas réel du journal, et
  avec au plus 3 fausses alertes par livrable.
- Ordre de construction : d'abord ce qui est déjà possible sans journal
  (C1, C2, diff script contre voix, état). Ensuite, avec les 30 critiques,
  les mesures de style et les jugements.

### Pour Whose Dime, en plus

Le contrôleur vérifie le registre des personnes (chaque citation mot pour
mot, chaque décision datée), le trajet du dollar (un payeur, un montant,
une source à chaque étape), les graphiques (un id du registre chacun) et
les phrases interdites (conseil financier).

---

## 6. Critique de ce rapport (protocole)

1. `fait` — § 2.1 S1-S6 : je ne mesure le style que sur le verre et
   l'aluminium ; le sel n'a été lu qu'en passages.
2. `incoherence` — F1 : la citation du maréchal est jugée absente par une
   recherche plein texte Drive, fiable mais pas exacte (pas de lecture
   ligne à ligne de la recherche de l'aluminium).
3. `processus` — je n'ai lu ni les `03_scenes.md`, ni les `02_plan.md`, ni
   les `mots.json` : les paires plan → script et scènes → prompts ne sont
   pas mesurées.
4. `voix` — tout le diagnostic de la voix vient du code et des fichiers,
   aucun de l'écoute ; la cause V1 reste une hypothèse jusqu'au banc d'essai.
5. `comprehension` — le rapport est long ; « En bref » et le § 3 suffisent
   pour décider.

**Ta grille** : Exact / Clair / Vivant, de 1 à 5, et une phrase ?

[e3-8]: https://github.com/Johnfrancis6/Channel/blob/claude/optimistic-bohr-5f78k4/zehon/content-maker/references/etape3_script.md#L8-L22
[e3-24]: https://github.com/Johnfrancis6/Channel/blob/claude/optimistic-bohr-5f78k4/zehon/content-maker/references/etape3_script.md#L24-L27
[e3-73]: https://github.com/Johnfrancis6/Channel/blob/claude/optimistic-bohr-5f78k4/zehon/content-maker/references/etape3_script.md#L73-L74
[e3-77]: https://github.com/Johnfrancis6/Channel/blob/claude/optimistic-bohr-5f78k4/zehon/content-maker/references/etape3_script.md#L77-L79
[e3-84]: https://github.com/Johnfrancis6/Channel/blob/claude/optimistic-bohr-5f78k4/zehon/content-maker/references/etape3_script.md#L84-L85
[e3-105]: https://github.com/Johnfrancis6/Channel/blob/claude/optimistic-bohr-5f78k4/zehon/content-maker/references/etape3_script.md#L105-L106
[e3-133]: https://github.com/Johnfrancis6/Channel/blob/claude/optimistic-bohr-5f78k4/zehon/content-maker/references/etape3_script.md#L133-L135
[e2-21]: https://github.com/Johnfrancis6/Channel/blob/claude/optimistic-bohr-5f78k4/zehon/content-maker/references/etape2_recherche.md#L21-L28
[e1-67]: https://github.com/Johnfrancis6/Channel/blob/claude/optimistic-bohr-5f78k4/zehon/content-maker/references/etape1_sujet.md#L67-L69
[e4-33]: https://github.com/Johnfrancis6/Channel/blob/claude/optimistic-bohr-5f78k4/zehon/content-maker/references/etape4_scenes.md#L33
[ch-14]: https://github.com/Johnfrancis6/Channel/blob/claude/optimistic-bohr-5f78k4/zehon/content-maker/references/chaine.md#L14-L18
[ch-25]: https://github.com/Johnfrancis6/Channel/blob/claude/optimistic-bohr-5f78k4/zehon/content-maker/references/chaine.md#L25-L28
[ch-32]: https://github.com/Johnfrancis6/Channel/blob/claude/optimistic-bohr-5f78k4/zehon/content-maker/references/chaine.md#L32-L35
[sk-94]: https://github.com/Johnfrancis6/Channel/blob/claude/optimistic-bohr-5f78k4/zehon/content-maker/SKILL.md#L94
[sk-152]: https://github.com/Johnfrancis6/Channel/blob/claude/optimistic-bohr-5f78k4/zehon/content-maker/SKILL.md#L152-L155
[sk-211]: https://github.com/Johnfrancis6/Channel/blob/claude/optimistic-bohr-5f78k4/zehon/content-maker/SKILL.md#L211-L213
[v-22]: https://github.com/Johnfrancis6/Channel/blob/claude/optimistic-bohr-5f78k4/zehon/content-maker/scripts/verifier.py#L22
[v-55]: https://github.com/Johnfrancis6/Channel/blob/claude/optimistic-bohr-5f78k4/zehon/content-maker/scripts/verifier.py#L53-L57
[v-98]: https://github.com/Johnfrancis6/Channel/blob/claude/optimistic-bohr-5f78k4/zehon/content-maker/scripts/verifier.py#L98-L99
[v-177]: https://github.com/Johnfrancis6/Channel/blob/claude/optimistic-bohr-5f78k4/zehon/content-maker/scripts/verifier.py#L177-L178
[nb]: https://github.com/Johnfrancis6/Channel/blob/claude/optimistic-bohr-5f78k4/zehon/notebooks/voix_zehon.ipynb
[mo-1180]: https://github.com/Johnfrancis6/Channel/blob/claude/optimistic-bohr-5f78k4/zehon/video-maker/scripts/monter.py#L1180-L1181
[ctx-14]: https://github.com/Johnfrancis6/Channel/blob/claude/optimistic-bohr-5f78k4/docs/chaine2/CONTEXTE.md#L14-L15
[ctx-51]: https://github.com/Johnfrancis6/Channel/blob/claude/optimistic-bohr-5f78k4/docs/chaine2/CONTEXTE.md#L51-L52
[hi-34]: https://github.com/Johnfrancis6/Channel/blob/claude/optimistic-bohr-5f78k4/docs/chaine2/historique.md#L34-L37
[hi-94]: https://github.com/Johnfrancis6/Channel/blob/claude/optimistic-bohr-5f78k4/docs/chaine2/historique.md#L94-L97
