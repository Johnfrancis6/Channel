# Chaîne 2 — contexte de reprise (état au 29/09/2026, fin de journée)

À lire en premier pour reprendre le travail sur la seconde chaîne. Ce
fichier **résume et renvoie** ; le détail est dans les documents cités.
Chaque fait porte son statut : **mesuré** (données relevées, avec la
date) ou **hypothèse** (interprétation, à tester).

## 1. Les documents

| Fichier | Contenu |
|---|---|
| [`../lancement_chaine_2_prehistoire.md`](../lancement_chaine_2_prehistoire.md) | Document de cadrage : décisions, Zelan (section 1), positionnement, piliers et backlog, format, exactitude, chantiers pipeline, ordre, journal de session (section 8) |
| [`concurrents_2026-09-29.md`](concurrents_2026-09-29.md) | Cartographie FR et EN du genre « Ancient Humans », saturation, qui Zelan imite, liste proposée pour `chaines_concurrentes.json` |
| [`niches_2026-09-29.md`](niches_2026-09-29.md) | Comparaison de 16 niches, jeunes gagnants français, recommandation de recentrage |
| [`revenus_2026-09-29.md`](revenus_2026-09-29.md) | Revenus estimés des chaînes du genre (vues mesurées × RPM supposé), risque « contenu inauthentique » |
| [`zelan_releve_2026-09-29.csv`](zelan_releve_2026-09-29.csv) | Les 25 vidéos de Zelan (API) : date, durée, vues, likes, commentaires, titres FR et EN |
| [`corpus_structures.jsonl`](corpus_structures.jsonl) | Corpus de segmentations (`outils/analyser_transcription.py`), **append-only**. Une ligne : *le fer*. À déplacer dans `02_Veille_hebdo/` de la racine Drive de la chaîne 2 quand elle existera |
| [`outils_releve/`](outils_releve/) | Scripts ponctuels de relevé (API, yt-dlp, sous-titres), hors pipeline |

## 2. Décisions de Franco

| Date | Décision |
|---|---|
| 29/09 | Seconde chaîne, à côté de la chaîne IA (anglais, Shorts), qui continue |
| 29/09 | En **français** |
| 29/09 | Niche de départ : préhistoire + histoire des objets du quotidien — **remise en question par l'analyse des niches, en attente de sa réponse** |
| 29/09 | Partage du pipeline et de `composants/` (Remotion). **Pas de code multi-chaînes avant une vidéo pilote** |
| 29/09 | Format proposé : vidéo longue en paysage d'environ 8 min, plus 1 à 2 Shorts ; 1 vidéo par semaine au départ |
| 29/09 | **Temps disponible : 20 h par semaine** |

Règles de travail : Claude propose, Franco tranche (sujets, concurrents,
nom) ; recommandations plutôt que listes d'options ; mesuré séparé de
l'hypothèse ; ne jamais éditer `.claude/skills/` ; `git fetch` avant chaque
push ; branche `claude/zelan-studio-analysis-rws9f6`.

## 3. Ce qu'on sait (mesuré le 29/09)

**Zelan** (@zelanstudio, le modèle observé) :
- 7 semaines, 25 vidéos, une tous les 2 jours à 17 h 30 ; 4,37 k abonnés ;
  médiane 14,1 k vues ; 3 vidéos font 72 % des vues ; 0,38 % des vues
  deviennent des abonnés.
- **Il traduit les sujets de chaînes anglaises** (Ink Explainer surtout,
  puis Axen et The Primal Glitch), avec un décalage passé de ~120 à
  ~20 jours. Il copie aussi les **compositions de miniatures**.
- *Le fer* (435 k) : 3,09 mots/s, 10 temps de ~120 mots enchaînés par des
  « Sauf que », tutoiement et retours au présent, pas d'appel à s'abonner,
  **seulement 2 mentions de preuve**. La preuve n'est pas la structure :
  l'angle « enquête » reste libre.

**Le genre** :
- En anglais, la médiane des vues du genre « Ancient Humans » passe de
  1,1 M (vidéos d'avril) à 6,5 k (vidéos d'août).
- En français, une chaîne active en mai, dix en septembre ; médiane sous
  1 k, sauf Zelan.
- Toutes ces chaînes partagent la même grammaire visuelle (bonhomme à tête
  ronde, pagne léopard, texte jaune cerné de noir).
- Les archéologues vulgarisatrices (Passé sauvage, Boneless Archéologie)
  convertissent 1 à 3 % des vues en abonnés, contre 0,4 % pour Zelan.

**Les autres niches (français)** :
- Les deux meilleures jeunes chaînes sans visage font du **« Chaque X
  expliqué »** : Le Labo de la Curiosité (122 k abonnés, médiane 89 k) et
  Dinguerie Psychologie (64,8 k, médiane 30,8 k).
- **« Comment c'est fait »** (la matière qui devient un objet) : Je
  T'explique Comment, 95 k abonnés, médiane 21 k, plus de 20 vidéos
  au-dessus de 100 k.
- L'histoire des inventions racontée par l'inventeur ne marche pas (Quand
  Tout a Commencé, médiane 1,4 k).

**Revenus (estimés, pas mesurés)** : les chaînes françaises du genre qui
ont percé font de l'ordre de 500 à 3 000 € par mois. Une chaîne à la médiane
de Zelan, avec une vidéo par semaine, ferait 60 à 300 € par mois. Depuis le
16/07/2026, YouTube démonétise le contenu répétitif produit en masse : les
clones du genre sont exposés.

**Backlog** : le pain, la nuit, Néandertal (« ce qu'il nous a laissé »),
Lascaux (« le mystère ») et le feu sous la pluie sont prouvés en anglais.
La veine française « corps des femmes et des enfants » (règles, grossesse,
bébés, espérance de vie) est prouvée, et Zelan n'y a pas touché.

## 4. Les recommandations en cours (hypothèses)

1. **Recentrer la ligne sur la transformation** : « comment on est passé de
   la matière brute à l'objet que tu as dans la main, et comment on le
   sait ». La préhistoire devient le premier chapitre de chaque histoire,
   pas la niche entière. Tester aussi le format « Chaque X expliqué » sur ce
   terrain.
2. **L'enquête comme structure** : 3 à 4 questions d'enquête par vidéo,
   chacune en 2 à 3 temps, avec une pièce à conviction à l'écran. Environ
   1 480 mots pour 8 min (3,1 mots/s).
3. **Utiliser l'anglais comme banc d'essai** : un sujet qui a fait plus de
   500 k en anglais et n'existe pas en français passe devant. On reprend des
   sujets, jamais des scripts.
4. **Une charte visuelle hors du genre** : pas de bonhomme à tête ronde, pas
   de texte jaune cerné de noir. La miniature du fer (l'objet transformé,
   sans personnage) est la piste à creuser.
5. **Calendrier** : vidéo pilote en octobre. Avec 20 h par semaine : la
   pilote pendant les semaines 1 à 3, puis 1 vidéo par semaine, puis 2 si le
   coût tombe sous 8 h par vidéo.
6. Nom : *Avant Nous* est écarté (déjà pris). Handles libres relevés :
   @commentonlesait, @lenquetedesancetres, @enquetedorigine,
   @preuvesalappui. **À revoir si la ligne est recentrée.**

## 5. Questions ouvertes, dans l'ordre

1. ~~Temps par semaine~~ → 20 h.
2. **Niche : garder « comment faisaient nos ancêtres », ou recentrer sur la
   transformation** (niches, section 5) ? C'est la question en cours.
3. **Propriété de la chaîne** : Franco a demandé à une connaissance en
   France de créer la chaîne. Il reste à savoir pourquoi (pays de résidence
   de Franco, éligibilité au Programme Partenaire), qui en est propriétaire
   et à qui revient l'AdSense. Voir la réponse du 29/09 dans la section 8
   du doc principal.
4. Budget mensuel (images, voix, musique).
5. Voix : la sienne, un clone, ou Qwen3-TTS ? Il faut de toute façon un
   échantillon de référence en français (chantier 3).
6. Objectif à 6 mois (abonnés ? revenu ? apprentissage ?).
7. Rapport personnel au sujet.
8. Nom de la chaîne et mascotte (distincte du genre entier).
9. Grammaire des miniatures.
10. Relecture et priorisation du backlog selon la ligne retenue.

## 6. Travail technique en suspens

- **Transcriptions** de *la journée* (u7gam_aBU4s), *l'eau sale*
  (ZBJ0fXTN4EA), *le sucre* (pvx89-uxxBI) et de la n° 1 (efqIZk5HDVs) :
  bloquées par un 429 de YouTube le 29/09. Relancer
  `outils_releve/transcription.sh <id>` un autre jour, puis segmenter
  (`outils/analyser_transcription.py --gabarit`, puis `--mesurer --corpus
  docs/chaine2/corpus_structures.jsonl`). Question à trancher : *le sucre*
  (raté) diffère-t-il du *fer* par la structure ou seulement par le sujet ?
- Le vocabulaire fermé des rôles n'a pas de rôle « conclusion ». La
  question ouverte finale du *fer* a été classée `cta` (appel à commenter).
  À discuter avant d'étendre le corpus.
- Environnement : `googleapis.com`, `youtube.com` et `i.ytimg.com` sont
  accessibles ; `socialblade.com` ne l'est pas. Quota de l'API : 10 000
  unités par jour, et `search.list` coûte 100 unités. Les recherches
  passent donc par yt-dlp.
