# Chaîne 2 — contexte de reprise (état au 29/09/2026, fin de session)

**À lire en premier.** La phase de cadrage est close. La prochaine session
porte sur la **production** : recherche active, rédaction du script, images
et mise en place des vidéos, jusqu'à une **vidéo pilote**.

Ce fichier résume et renvoie. Chaque fait porte son statut : **mesuré**
(relevé, daté) ou **hypothèse** (à tester).

---

## 1. Décisions de Franco (toutes du 29/09/2026)

| Sujet | Décision |
|---|---|
| Chaîne | Seconde chaîne, à côté de la chaîne IA (anglais, Shorts), qui continue |
| Langue | **Français** |
| **Ligne éditoriale** | **« De la matière brute à l'objet, et comment on le sait. »** Chaque vidéo raconte comment une matière (minerai, sable, grain, graisse, fibre…) est devenue un objet du quotidien, en partant de la préhistoire jusqu'à aujourd'hui, et montre **les preuves** (fouilles, traces, datations, expériences). La préhistoire est le premier chapitre de chaque histoire, pas la niche entière |
| Format | Vidéo longue en paysage d'environ 8 min, plus 1 à 2 Shorts tirés du même script ; 1 vidéo par semaine au départ |
| Temps | **20 h par semaine** |
| Propriété | Franco réside au **Burkina Faso**, qui n'est pas éligible au Programme Partenaire. **Une connaissance en France est réellement propriétaire** : chaîne et AdSense à son nom, revenus déclarés en France. Franco est **gestionnaire** (compte de marque), rémunéré par un **contrat écrit** (rémunération ou part des revenus, droits sur les vidéos, conditions de sortie), à signer avant la première vidéo |
| Pipeline | Partage du pipeline et de `composants/` (Remotion). **Pas de code multi-chaînes** (`profil_chaine.json`, `--chaine`) avant la vidéo pilote. Pour la pilote : `--root` explicite, et seulement les réglages en dur que la pilote exige (langue, débit) |

Règles de travail : Claude propose, Franco tranche (sujets, nom, charte) ;
des recommandations, pas des listes d'options ; mesuré séparé de
l'hypothèse ; une question à la fois ; ne jamais éditer `.claude/skills/` ;
`git fetch` avant chaque push ; branche de travail
`claude/zelan-studio-analysis-rws9f6`.

---

## 2. Ce que la vidéo doit être (le modèle mesuré)

**La référence de structure : *Comment nos ancêtres ont-ils découvert le
fer ?* (Zelan, 435 k vues).** Transcription segmentée le 29/09 (mesuré) :
- 500 s, 1 547 mots, **3,09 mots/s** en français ;
- un **hook de 30 s** (8 phrases) : un objet que tu as sous la main, puis un
  paradoxe (« le métal le plus banal du monde… personne n'a su en
  fabriquer un gramme ») ; la question tombe à la 9e phrase ;
- **10 temps de 55 à 255 mots** (123 en moyenne), en fil chronologique.
  Chaque temps finit sur un obstacle, que le suivant lève. Le mot charnière
  est « **Sauf que** » ;
- le **tutoiement**, et 5 à 6 **retours au présent** (« un couteau à 3 € au
  supermarché », « 10 objets en fer dans ton tiroir ») ;
- **pas d'appel à s'abonner**. La vidéo finit sur une question ouverte ;
- **seulement 2 mentions de preuve** en 116 phrases. C'est là qu'on se
  distingue.

**Notre structure (recommandation, à valider sur le script pilote)** :
- environ **1 480 mots pour 8 min** ;
- hook de 25 à 30 s sur l'objet du quotidien et un paradoxe ;
- **3 à 4 questions d'enquête**, chacune en 2 à 3 temps (au total 8 à 10
  temps de 120 à 150 mots). Chaque question se referme sur **une pièce à
  conviction montrée à l'écran** : l'objet de fouille, la trace, la
  datation, l'expérience ;
- marqueurs d'incertitude à l'oral (« on sait que… », « on pense que… »,
  « personne ne sait vraiment… »), hérités du dossier de recherche ;
- fin sur une question ouverte, rattachée au présent.

**Pourquoi la transformation** (mesuré le 29/09, détail dans
[`niches_2026-09-29.md`](niches_2026-09-29.md)) :
- c'est le meilleur score de Zelan (*le fer*, 435 k), alors que *le sucre*
  (3,6 k) et *le sel* (5,9 k), traités comme des « découvertes », ont
  échoué ;
- c'est la veine française la plus régulière : **Je T'explique Comment**
  (« Comment c'est fait », 95 k abonnés, médiane 21 k), dont *le sucre* et
  *le sel* dépassent 140 k ;
- l'histoire racontée par l'inventeur ne marche pas (Quand Tout a Commencé,
  médiane 1,4 k) : **c'est le procédé qui intéresse, pas la biographie** ;
- la vague de clones « comment faisaient nos ancêtres » s'effondre (en
  anglais, médiane de 1,1 M à 6,5 k vues entre avril et août ; en français,
  10 chaînes et une médiane sous 1 k) ;
- depuis le 16/07/2026, YouTube démonétise le contenu répétitif produit en
  masse : l'enquête sourcée protège aussi la monétisation.

---

## 3. Sujets candidats pour la pilote (à valider par Franco)

Classés par preuve de demande (mesuré le 29/09) :

| Sujet | Demande prouvée | Pièces à conviction possibles |
|---|---|---|
| **Le pain** (du grain sauvage à la baguette) | EN 333 k (*How Did Humans Invent Bread?*) | Pain carbonisé de Shubayqa 1 (Jordanie), il y a environ 14 400 ans, avant l'agriculture ; meules ; grains carbonisés |
| Le verre (du sable à la vitre) | FR 154 k (Je T'explique Comment) | Obsidienne, perles de verre mésopotamiennes et égyptiennes, fours |
| Le fer (de la pierre rouge à l'acier) | FR 435 k (Zelan) | Scories, bas fourneaux, lame météoritique de Toutânkhamon. **Déjà fait par Zelan** : à garder pour plus tard, sous l'angle de la preuve |
| Le sel, le sucre | FR 145 k et 142 k (Je T'explique Comment) ; ratés chez Zelan | Mines de Hallstatt, salines ; à traiter comme des procédés, pas comme des « découvertes » |
| Le ciment, le crayon, les pièces de monnaie | FR 279 k, 369 k, 718 k (Je T'explique Comment, procédé moderne) | Mortiers romains, graphite de Borrowdale, ateliers monétaires. À vérifier : existe-t-il une histoire « depuis la préhistoire » solide ? |

**Recommandation pour la pilote : le pain.** La demande est prouvée, la
transformation est visible (grain → farine → pâte → pain) et il y a une
vraie pièce à conviction récente et datée (Shubayqa 1). En plus, le pain
tombe avant l'agriculture, ce qui fait un paradoxe de hook. **Hypothèse** :
à vérifier pendant la recherche. Franco tranche.

À tester après les 3 premières vidéos : le format « **Chaque X expliqué** »
sur notre terrain (*Chaque métal expliqué*, *Chaque âge des matériaux
expliqué*). C'est le format des deux meilleures jeunes chaînes françaises
sans visage (Le Labo de la Curiosité, médiane 89 k ; Dinguerie Psychologie,
30,8 k).

---

## 4. Ce que le pipeline sait déjà faire, et ce qui bloque la pilote

Pipeline de la chaîne IA : agents A2 (Chercheur) → A4 (Rédacteur) ⇄ A5
(Filtre TTS) → CP2 → voix off (Colab, `notebooks/voix_off.ipynb`) et A6
(Designer, storyboard) → A7 (Monteur, Remotion) → publication. Les
composants disponibles sont dans `composants/REGISTRE.md`, avec leurs
aperçus.

**Déjà prêt pour le format long** (commits du 16/09) : le champ
`format_video: "long"` dans `state.json`, le budget, le rendu en
1920×1080, des scènes cibles de 12 s (120 au plus), l'insert de footage
(`InsertFootage`). Tout est centralisé dans `outils/formats_video.py`.

**À régler pour la pilote** (vérifié dans le code le 29/09) :

| # | Point | Où | Mesure disponible |
|---|---|---|---|
| 1 | Voix en anglais en dur : `language="English"` (2 endroits), `language="en"` pour les horodatages Whisper (dont dépendent les sous-titres) | `notebooks/voix_off.ipynb` | Il faut un **échantillon de voix de référence en français**. Choix de la voix non tranché (celle de Franco, un clone, Qwen3-TTS) |
| 2 | Débit : `MOTS_PAR_SECONDE = 2.8` (mesuré en anglais, sur un Short) | `outils/formats_video.py` | Zelan : 3,09 mots/s en français. À mesurer sur notre propre voix |
| 3 | Budget : `MOTS_PAR_IDEE[long] = 300`, `IDEES_MAX_DEFAUT[long] = 8`. Le plafond de 8 idées colle ; les 300 mots par idée, non (le modèle mesuré en fait environ 120 à 150) | `outils/formats_video.py`, `agents/short-redacteur/SKILL.md` | Mesuré sur *le fer* |
| 4 | Le Rédacteur suppose une chaîne en anglais (« La chaîne est en anglais », l. 88) | `agents/short-redacteur/SKILL.md` | Puis relancer `python3 agents/_synchroniser_vers_claude_skills.py` |
| 5 | Seuils de phrase du Filtre TTS (8 à 18 mots, §7.3) calibrés en anglais | `agents/short-filtre-tts/scripts/metriques.py` | Phrase médiane de Zelan : 12 mots |
| 6 | Charte visuelle de la chaîne 2 (mascotte ou pas, palette, décors) | `00_Profil/charte_visuelle/` de la nouvelle racine Drive (à créer) | Voir section 5 |
| 7 | Composants Remotion pour montrer une transformation (matière → étapes → objet) et une pièce à conviction (objet de fouille, légende, date, lieu) | `composants/` | Aucun composant existant ne le fait : `Stickman`, `ConceptCutaway`, `PlanListeSequencee` sont pensés pour l'IA |
| 8 | Règle d'exactitude du Chercheur : chaque affirmation marquée **établi**, **probable** ou **hypothèse**, avec sa source | `agents/short-chercheur/SKILL.md` | Voir la section 5 du doc de cadrage |

---

## 5. Images et miniatures : ce qui est décidé et ce qui ne l'est pas

**Mesuré le 29/09** : tout le genre partage une seule grammaire. Bonhomme
blanc à tête ronde, pagne léopard, savane ou grotte peinte, 2 à 3 mots en
capitales jaunes cernées de noir, rendu d'image générée par IA. Zelan
copie jusqu'aux compositions (*PAS DE BOULOT ?* reprend *NO JOBS* d'Ink
Explainer). La seule miniature de Zelan sans personnage, *le fer*, est son
meilleur score : deux mains, un minerai, une lame.

**Recommandations** :
- **Charte hors du genre entier** : ni bonhomme à tête ronde, ni texte jaune
  cerné de noir.
- **Miniature « transformation »** : la matière brute et l'objet fini côte à
  côte, sans personnage, avec 2 à 4 mots. On la teste contre une variante
  avec personnage dès que deux vidéos existent.
- **Vidéo en Remotion, décors simples** (décision du 11/09 : tout codé) ;
  la richesse visuelle va dans la miniature. La pièce à conviction est
  l'endroit où une **vraie photo** (musée, fouille, sous licence libre) a
  sa place, via `PlanBroll` ou `InsertFootage`.
- **Non tranché** : générer des images par IA pour les scènes (plus riche,
  mais dépendance et cohérence d'un plan à l'autre), la mascotte, le nom.

**Nom** : *Avant Nous* est écarté (pris). Handles vérifiés libres le 29/09 :
@commentonlesait, @enquetedorigine, @preuvesalappui (et
@lenquetedesancetres, moins adapté à la nouvelle ligne). À trancher avec la
charte.

---

## 6. Recherche active : méthode et outils

- **Veille des sujets** : le marché anglais sert de banc d'essai. Un sujet
  qui a fait plus de 500 k en anglais et n'existe pas en français passe
  devant. Pour la transformation, la référence française est Je T'explique
  Comment. On reprend des sujets, **jamais des scripts**.
- **Recherche d'un sujet** (A2) : sources primaires ou institutionnelles
  (publications, musées, rapports de fouille) ; chaque affirmation marquée
  établi, probable ou hypothèse ; au moins une pièce à conviction montrable
  (photo sous licence libre) par question d'enquête.
- **Outils de relevé** : [`outils_releve/`](outils_releve/) (API YouTube,
  yt-dlp, sous-titres avec le client `mweb`). YouTube renvoie un 429 après
  quelques dizaines de requêtes : espacer.
- **Transcriptions encore à récupérer**, utiles pour l'écriture : *la
  journée* (u7gam_aBU4s), *l'eau sale* (ZBJ0fXTN4EA), *le sucre*
  (pvx89-uxxBI, le raté) et la n° 1 (efqIZk5HDVs). La question : *le sucre*
  diffère-t-il du *fer* par la structure ou seulement par le sujet ?
  Récupérer aussi une transcription de Je T'explique Comment (le modèle
  « procédé »). Segmenter avec `outils/analyser_transcription.py`, puis
  ajouter à [`corpus_structures.jsonl`](corpus_structures.jsonl).
- Le vocabulaire fermé des rôles n'a pas de rôle « conclusion ». La question
  finale du *fer* a été classée `cta`. À trancher avant d'étendre le corpus.

---

## 7. Questions ouvertes pour la prochaine session, dans l'ordre

1. **Sujet de la pilote** (recommandation : le pain).
2. **Voix** : la sienne, un clone ou Qwen3-TTS ? Il faut un échantillon
   français de référence.
3. **Budget mensuel** (images, voix, musique, banques d'images).
4. **Charte** : images générées ou non, mascotte ou non, nom.
5. Objectif à 6 mois.

---

## 8. Les documents de la phase de cadrage

| Fichier | Contenu |
|---|---|
| [`../lancement_chaine_2_prehistoire.md`](../lancement_chaine_2_prehistoire.md) | Document de cadrage complet et journal de session (section 8) |
| [`niches_2026-09-29.md`](niches_2026-09-29.md) | 16 niches comparées ; pourquoi la transformation |
| [`concurrents_2026-09-29.md`](concurrents_2026-09-29.md) | Le genre en FR et EN, saturation, qui Zelan imite |
| [`revenus_2026-09-29.md`](revenus_2026-09-29.md) | Revenus estimés du genre, risque « contenu inauthentique » |
| [`zelan_releve_2026-09-29.csv`](zelan_releve_2026-09-29.csv) | Les 25 vidéos de Zelan (API) |
| [`corpus_structures.jsonl`](corpus_structures.jsonl) | Segmentations de vidéos, append-only (une ligne : *le fer*) |
| [`outils_releve/`](outils_releve/) | Scripts ponctuels de relevé, hors pipeline |
| [`PROMPT_NOUVELLE_SESSION.md`](PROMPT_NOUVELLE_SESSION.md) | Le message à coller pour ouvrir la prochaine session |

Environnement du conteneur au 29/09 : `googleapis.com`, `youtube.com`,
`i.ytimg.com` et `google.com` accessibles, `socialblade.com` refusé.
`YOUTUBE_API_KEY` définie (10 000 unités par jour ; `search.list` coûte
100 unités, donc les recherches passent par yt-dlp).
