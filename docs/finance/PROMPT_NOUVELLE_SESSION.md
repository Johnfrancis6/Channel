# Message d'ouverture de la session « plan d'action chaîne finance »

À copier tel quel dans une nouvelle discussion Claude Code web, dans ce
dépôt, avec le connecteur Google Drive activé.

---

Session de travail : **plan d'action pour lancer ma nouvelle chaîne YouTube
finance en anglais** (public américain, format long). La recherche sur la
niche est terminée. Cette session ne refait pas la recherche : elle la
transforme en plan d'action que je peux exécuter semaine par semaine.

## Mise en route
1. Récupère la branche de la recherche et reste dessus :
   `git fetch origin claude/confident-gates-ntpt6a`, puis
   `git checkout claude/confident-gates-ntpt6a`.
2. Lis, dans cet ordre :
   - `reports/Échecs public et systèmes chaîne finance.md` : le rapport de
     référence (échecs, public, 3 variantes, matrice, règles d'arrêt). Il
     **prime** sur le premier rapport quand ils divergent.
   - `reports/Croissance chaînes YouTube finance.md` : ce qui fait réussir
     les 8 chaînes de référence.
   - Au besoin, les notes de `research_notes/Échecs public et systèmes
     chaîne finance/` (`production.md`, `monetisation_canada.md`,
     `public.md`, `echecs.md`) et les CSV de données brutes.
3. Pour le pipeline existant que je réutilise : `CLAUDE.md`,
   `zehon/content-maker/SKILL.md`, `zehon/notebooks/voix_zehon.ipynb`.
   L'état le plus récent de Zehon (`docs/chaine2/CONTEXTE.md`,
   `historique.md`, `monter.py`) est sur la branche
   `origin/claude/optimistic-bohr-5f78k4` : lis-le avec `git show`, sans
   changer de branche.

## Mes contraintes (déjà tranchées)
- Je réside au **Canada**. Chaîne en **anglais**, public majoritairement
  américain, vidéos de **8 à 20 min**.
- **20 h par semaine**. Mon niveau d'anglais n'est pas une contrainte.
- Budget : **20 $/mois** pour Claude (Pro). Le reste gratuit ou presque :
  images Gemini, voix Qwen3-TTS sur Colab, montage sur Colab (`monter.py`).
  Le rapport chiffre l'option images via l'API Gemini à environ 8-16 $/mois :
  présente-la comme une décision à prendre, avec son gain de temps.
- Mes critères, dans l'ordre : **1. vitesse de monétisation, 2. revenu à
  12 mois, 3. automatiser ensuite.**
- Monétisation : publicité YouTube + affiliation (programmes ouverts à un
  résident canadien) + produit numérique simple.

## Ce que la recherche a établi (à ne pas remettre en cause sans données)
- Variante recommandée : **A, « Money Mechanics simulées »** (cible 23-40
  ans, 16-18 min, un protagoniste récurrent qui vit une vraie mécanique
  d'argent américaine, chiffres sourcés). Pivot préparé : **B, « Quiet
  Empire »** (rachat de business ennuyeux, retraite, 18-22 min). 3 des 10
  premières vidéos testent le cadre B. La variante C est écartée avant la
  monétisation.
- L'échec dominant : l'algorithme ne montre jamais la chaîne. Copier un
  titre déjà pris par 3 chaînes ou plus échoue. Les vidéos de moins de
  12 min échouent dans ces formats. La cadence et la mascotte ne
  distinguent plus les gagnantes des échecs.
- Seuil de monétisation : **1 000 abonnés + 8 000 h** à partir du
  1er février 2027 (confirmé par YouTube).
- Voix : **pas de clone d'une voix commerciale**. Voix créée avec Qwen3-TTS
  VoiceDesign à partir d'une description texte, puis clonée.
- Publication à horaire fixe, **12 h-14 h heure de l'Est**.
- Règles d'arrêt aux vidéos 5, 10 et 20 (tableau du rapport).

## Ce que j'attends, dans l'ordre
1. **Un plan d'action semaine par semaine**, de maintenant jusqu'à J+90
   après le lancement (lancement visé vers le 1er décembre 2026), qui tient
   dans 20 h par semaine. Pour chaque semaine : les tâches, qui les fait
   (moi ou Claude), le temps estimé, le livrable et le critère de « fini ».
   Il couvre au minimum :
   - la mise en place : nom et identité de la chaîne (vérifier que le nom
     est libre), compte AdSense et formulaire W-8BEN, comptes d'affiliation
     (Monarch, Rocket Money, Seeking Alpha, Wealthsimple), fiche mascotte,
     voix VoiceDesign et test à l'aveugle, lexique de prononciation ;
   - l'adaptation du pipeline Zehon : nouvelle skill de contenu en anglais
     (fact-check `02b_factcheck.md`, graphiques générés par code, 100-110
     scènes), réglages de `monter.py` pour 16-18 min ;
   - les 10 premiers sujets (7 de la variante A, 3 du cadre B), chacun
     vérifié contre l'API YouTube pour éviter les titres déjà pris ;
   - le produit PDF et sa page de vente ;
   - les points de contrôle J+30, J+60, J+90 avec leurs décisions.
2. **La liste de mes décisions** à prendre avant de démarrer, une question
   à la fois, avec ta recommandation pour chacune (exemples : images via
   l'API ou non, nom de la chaîne, prix du PDF).
3. **Le chemin d'automatisation** après le lancement, dans l'ordre du
   rapport, en gardant humains : choix du sujet, validation des chiffres,
   validation du script, visionnage final, choix de la miniature.
4. Écris le plan dans `docs/finance/PLAN_ACTION.md`, commite et pousse.

## Points encore à vérifier (à intégrer au plan comme tâches)
- Retenue d'impôt américaine pour un Canadien (0 % ou 10 %) et TPS/TVH :
  à faire valider par un comptable.
- Acceptation réelle d'un éditeur canadien par chaque programme
  d'affiliation américain.
- Qualité de Qwen3-TTS en anglais sur 15 min : test à l'aveugle.
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
