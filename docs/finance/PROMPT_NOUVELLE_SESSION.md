# Message d'ouverture de la session « plan d'action chaîne finance »

À copier tel quel dans une nouvelle discussion Claude Code web, dans ce
dépôt, avec le connecteur Google Drive activé.

---

Session de travail : **plan d'action pour lancer ma nouvelle chaîne YouTube
en anglais, variante C « Brand Economics »** (histoires et mécaniques
économiques de marques célèbres, public américain, format long). La
recherche sur la niche est terminée. Cette session ne la refait pas : elle
la transforme en plan d'action que je peux exécuter semaine par semaine.

## Ma décision (05/11/2026)
J'ai choisi la **variante C, « Brand Economics »**, en connaissance de
cause : la matrice du rapport la classait 3e (score 2,2), derrière A (4,1)
et B (3,55). Ne rouvre pas ce choix. Ton travail est de **rendre C aussi
rentable et aussi rapide à monétiser que possible**, en corrigeant ses
faiblesses mesurées (voir plus bas). Si une donnée nouvelle montre que C ne
peut pas tenir, dis-le une fois, chiffres à l'appui, et laisse-moi trancher.

## Mise en route
1. Récupère la branche de la recherche et reste dessus :
   `git fetch origin claude/confident-gates-ntpt6a`, puis
   `git checkout claude/confident-gates-ntpt6a`.
2. Lis, dans cet ordre :
   - `reports/Échecs public et systèmes chaîne finance.md` : le rapport de
     référence. Sections clés pour moi : « Variante C : Brand Economics »,
     « Le socle commun », « Les signaux qui disent de pivoter ou
     d'arrêter ». Il **prime** sur le premier rapport quand ils divergent.
   - `reports/Croissance chaînes YouTube finance.md` : les profils de
     CEOzoned et TradeoffLayer, les deux modèles de C.
   - Au besoin, les notes de `research_notes/Échecs public et systèmes
     chaîne finance/` (`echecs.md` : entrants C qui ont échoué ;
     `production.md` ; `monetisation_canada.md` ; `public.md`) et les CSV.
3. Pour le pipeline existant que je réutilise : `CLAUDE.md`,
   `zehon/content-maker/SKILL.md`, `zehon/notebooks/voix_zehon.ipynb`.
   L'état le plus récent de Zehon (`docs/chaine2/CONTEXTE.md`,
   `historique.md`, `monter.py`) est sur la branche
   `origin/claude/optimistic-bohr-5f78k4` : lis-le avec `git show`, sans
   changer de branche.

## Mes contraintes (déjà tranchées)
- Je réside au **Canada**. Chaîne en **anglais**, public majoritairement
  américain.
- **20 h par semaine**. Mon niveau d'anglais n'est pas une contrainte.
- Budget : **20 $/mois** pour Claude (Pro). Le reste gratuit ou presque :
  images Gemini, voix Qwen3-TTS sur Colab, montage sur Colab (`monter.py`).
  L'option images via l'API Gemini (≈8-16 $/mois, sans filigrane, 2 à 3 h
  gagnées par vidéo) est une décision à me soumettre.
- Mes critères, dans l'ordre : **1. vitesse de monétisation, 2. revenu à
  12 mois, 3. automatiser ensuite.**
- Monétisation : publicité YouTube + affiliation (programmes ouverts à un
  résident canadien) + éventuellement un produit numérique.

## Ce que la recherche dit de C (mesuré, sauf mention)
- **Le créneau le moins encombré par les nouvelles chaînes** (0 à 4 par
  mois jusqu'en septembre 2026), avec les plus gros hits récents :
  « Can Google Beat Nvidia? » 1,46 M (TradeoffLayer), Coca-Cola 377 K
  (CEOzoned).
- **Tout dépend de la notoriété de la marque** : même gabarit chez CEOzoned,
  Coca-Cola 349 K, Instagram 4 K. Les entrants qui ont échoué (The Corporate
  Story, Fletcher Finance, The Invisible Ledger) prenaient des sujets peu
  connus ou des miniatures infographiques.
- Format qui marche : **10-13 min**, 1 500-1 900 mots, en six temps (cold
  open qui annonce le résultat, mise en place, **la décision**, engrenage,
  conséquences, leçon). Titres : questions courtes, moins de 40 caractères,
  sur une marque que tout le monde connaît. Miniatures : caricature non
  réaliste du dirigeant avec le produit, 1 à 3 mots.
- **Faiblesse n° 1, la conversion en abonnés** : 2,8 abonnés pour
  1 000 vues chez TradeoffLayer, 10,2 chez CEOzoned (format en série
  reconnaissable). À 2,8, il faut 200-350 K vues pour 1 000 abonnés.
- **Faiblesse n° 2, le RPM** : 5 à 8 $ estimés (public mondial, annonceurs
  généralistes) ; affiliation faible (Seeking Alpha, TradingView).
- Revenus 12 mois (inférence du rapport) : médiane ≈ 1 300 $, espérance
  ≈ 2 900 $, monétisation vers octobre 2027 dans le scénario médian.
- Temps estimé : 6-7 h par vidéo une fois rodé (≈ 4,5 h avec les images
  via l'API), 9-10 h pour les premières ; **2 à 3 vidéos par semaine**
  possibles dans 20 h.
- Seuil de monétisation : **1 000 abonnés + 8 000 h** à partir du
  1er février 2027 (confirmé par YouTube).
- Risques : forte variance, commentaires politiques sur les milliardaires,
  portrait réaliste d'une vraie personne = contenu synthétique à déclarer,
  usage des logos non étudié, et **ne jamais glisser vers « achetez cette
  action »** (avis ACVM/OCRI 31-369 : un avertissement ne suffit pas).
- Ne pas copier les gabarits exacts des concurrents (« The ENTIRE History
  of X in N Minutes » est celui de CEOzoned) : les copies tardives échouent.

## Ce que j'attends, dans l'ordre
1. **Un balayage ciblé de la niche C** (court, borné à ~3 000 unités de
   quota API), parce que l'échantillon du rapport était construit sur les
   formats « simulation » et ne couvre presque pas C :
   - les chaînes établies du créneau (ColdFusion, MagnatesMedia, Company
     Man, How Money Works, Business Casual, Logically Answered…) et les
     nouvelles de 2025-2026 : quelles marques elles ont déjà traitées,
     quand, avec quelles vues ;
   - **une liste de 40 marques classées** selon la demande (vues des
     vidéos existantes sur la marque), le vide (pas de vidéo récente forte),
     le RPM probable (finance, paiements, tech > grande conso) et le risque
     (politique, action à recommander) ;
   - un nom de série et un gabarit de titre **originaux** (vérifiés libres
     via l'API) qui visent la conversion de CEOzoned (≈ 10 abonnés pour
     1 000 vues) plutôt que celle de TradeoffLayer.
2. **Un plan d'action semaine par semaine**, de maintenant jusqu'à J+90
   après le lancement (lancement visé vers le 1er décembre 2026), qui tient
   dans 20 h par semaine. Pour chaque semaine : les tâches, qui les fait
   (moi ou Claude), le temps estimé, le livrable et le critère de « fini ».
   Il couvre au minimum :
   - la mise en place : nom et identité de la chaîne (vérifier que le nom
     est libre), compte AdSense et formulaire W-8BEN, comptes d'affiliation
     (Seeking Alpha, TradingView, puis ce que la liste de marques ouvre),
     style de caricature et règles de miniature, voix VoiceDesign et test à
     l'aveugle, lexique de prononciation (noms de marques et de dirigeants) ;
   - l'adaptation du pipeline Zehon : nouvelle skill de contenu en anglais
     pour C (structure en six temps, fichier `02b_factcheck.md` sourcé sur
     rapports SEC / 10-K / presse, graphiques générés par code, 70-80
     scènes pour 10-13 min), réglages de `monter.py` ;
   - les 10 premiers sujets tirés de la liste, avec titre et miniature ;
   - les **leviers pour accélérer la monétisation** malgré C : conversion
     en abonnés (série, écran de fin vers la marque suivante, playlists),
     marques à RPM plus élevé, rythme de 2-3 vidéos par semaine pour
     multiplier les tirages dans un créneau à forte variance ;
   - les points de contrôle J+30, J+60, J+90 avec leurs décisions, en
     adaptant à C les règles d'arrêt du rapport (vidéos 5, 10, 20).
3. **La liste de mes décisions** à prendre avant de démarrer, une question
   à la fois, avec ta recommandation pour chacune (exemples : images via
   l'API ou non, nom de la chaîne, pivot de repli si C échoue à la vidéo 10).
4. **Le chemin d'automatisation** après le lancement, dans l'ordre du
   rapport, en gardant humains : choix de la marque, validation des
   chiffres, validation du script, visionnage final, choix de la miniature.
5. Écris le tout dans `docs/finance/PLAN_ACTION.md` (et la liste de marques
   dans `docs/finance/marques.md`), commite et pousse.

## Points encore à vérifier (à intégrer au plan comme tâches)
- Retenue d'impôt américaine pour un Canadien (0 % ou 10 %) et TPS/TVH :
  à faire valider par un comptable.
- Acceptation réelle d'un éditeur canadien par Seeking Alpha, TradingView
  et les autres programmes retenus.
- Règles d'usage des logos et des caricatures de dirigeants réels dans les
  miniatures (marques déposées, politique YouTube sur le contenu
  synthétique).
- Qualité de Qwen3-TTS en anglais sur 12 min : test à l'aveugle.
- Limites réelles de Claude Pro : mesurer avec `/status` sur les 2
  premières vidéos.

## Règles
- Donne tes recommandations, pas des listes d'options. Sépare ce qui est
  mesuré de ce qui est une hypothèse. Une question à la fois.
- La clé `YOUTUBE_API_KEY` est disponible dans l'environnement : ne
  l'affiche jamais. Transcriptions YouTube, Reddit et Social Blade sont
  bloqués depuis le cloud : ne tente pas de contournement.
- Ne jamais éditer `.claude/skills/` ni `zehon/*.skill` : ils sont générés
  (voir `CLAUDE.md`). Une nouvelle skill se crée dans son propre dossier,
  puis `python3 zehon/synchroniser_skills.py`.
- `git fetch` avant chaque push.
