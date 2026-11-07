> Done on 07/11: see reports/Audit pipeline de production.md

# Message d'ouverture de la session 1 : audit du pipeline de production

À copier tel quel dans une nouvelle discussion Claude Code web, dans ce
dépôt, avec le connecteur Google Drive activé. La session 2 (qualité du
contenu et veille) se lance **après** celle-ci : [PROMPT_SESSION_2_QUALITE_CONTENU.md](PROMPT_SESSION_2_QUALITE_CONTENU.md).

---

Session de travail : **audit complet de mon pipeline de production de
vidéos**, pour réduire les erreurs avant de le réutiliser pour ma nouvelle
chaîne anglaise « Whose Dime ». Cette session porte **uniquement sur la
chaîne de production et de gestion du contenu** (étapes, skills, fichiers,
contrôles, reprises de session). La qualité éditoriale, l'agrément de
visionnage et la veille concurrentielle sont pour la session 2.

## Mise en route
1. `git fetch origin claude/admiring-ramanujan-k2uiqe claude/optimistic-bohr-5f78k4`,
   puis `git checkout claude/admiring-ramanujan-k2uiqe` (branche de
   travail ; pousse dessus, `git fetch` avant chaque push).
2. Le pipeline Zehon le plus récent est sur `origin/claude/optimistic-bohr-5f78k4` :
   lis-le avec `git show` ou `git worktree`, sans changer de branche.
   Il contient `zehon/content-maker/` (skill de contenu, 5 étapes),
   `zehon/video-maker/` (montage, `monter.py`), `zehon/notebooks/` (voix
   Qwen3-TTS et montage sur Colab, lanceurs), `tests/`,
   `docs/chaine2/CONTEXTE.md` et `docs/chaine2/historique.md` (365 lignes :
   les décisions, les mesures et les incidents réels).
3. Lis aussi, sur la branche de travail : `CLAUDE.md`,
   `docs/finance/PLAN_ACTION.md` (le pipeline anglais prévu),
   `docs/audit/PROTOCOLE_CRITIQUES.md` (à appliquer dès cette session).
4. Dans Drive, dossier `Zehon/` : `Memoire/`, `Charte/` et les deux vidéos
   produites, `Videos/01_sel/` et `Videos/02_verre/`. Ce sont les seules
   preuves réelles de ce que le pipeline produit : lis leurs fichiers
   (téléchargement brut, pas la version « lisible »).

## Ce que je constate (à expliquer par la chaîne de production)
- **Les scripts** sont robotiques, sans narration humaine, peu nuancés,
  peu compréhensibles et très formels.
- **La voix off** est robotique : débit monotone, environ une phrase sur
  six qui finit sèche (mesuré dans `historique.md`).

## Les erreurs à réduire, par priorité
1. **Erreurs de faits** : chiffres, dates ou noms faux ou non sourcés,
   entre la recherche, le script et la publication.
2. **Erreurs de processus** : étape sautée, fichier manquant ou mal nommé
   dans Drive, doublons, session qui reprend au mauvais endroit.
3. **Incohérences entre étapes** : script contre plan, scènes contre
   script, voix contre texte, miniature et titre contre contenu.

## Ce que j'attends, dans l'ordre
1. **Une cartographie** de la chaîne réelle : chaque étape, qui la fait
   (moi ou Claude), ses entrées, ses sorties, le contrôle qui la ferme
   (vérificateur, tests, pause de validation) ou son absence.
2. **Un diagnostic** des points de défaillance, chacun avec sa preuve
   (fichier et ligne du dépôt ou de Drive, passage de `historique.md`) et
   sa gravité. Pour les deux symptômes ci-dessus : à quelle étape et par
   quelle consigne de skill ils naissent (instructions d'écriture, version
   voix, absence de relecture à l'oral, réglages Qwen3-TTS…).
3. **Les corrections proposées**, classées par effet attendu, chacune
   avec ce qui change, où, et comment on vérifie qu'elle marche. Sépare
   ce qui vaut pour Zehon de ce qu'il faut corriger avant de copier le
   pipeline pour Whose Dime. **Attention au changement de narration** :
   Zehon raconte un procédé de fabrication, en français, sans personnage
   central. Whose Dime aura un conteur d'histoires de startups et
   d'industries qui ont réussi, en anglais, centré sur des dirigeants
   nommés et leurs décisions (série « Who Pays? »). Les étapes et
   consignes de skill qui supposent un procédé (structure, scènes, version
   voix, contrôles) doivent être signalées comme à adapter, pas copiées.
4. **Les questions** qui me permettront d'itérer : pose-les toutes,
   groupées, avec ta recommandation pour chacune.
5. **Une première ébauche de la skill de détection d'incohérences** :
   ce qu'elle contrôlerait, à quel moment, sur quels fichiers, avec quels
   types de défauts. Elle ne sera construite qu'avec les données du
   journal de critiques (`docs/audit/journal_critiques.jsonl`) : propose
   le plan, pas le code.
6. Écris le rapport dans `reports/Audit pipeline de production.md`, les
   notes de travail dans `research_notes/Audit pipeline/`, commite, pousse,
   et **donne-moi le lien GitHub de chaque rapport écrit**
   (`https://github.com/Johnfrancis6/Channel/blob/claude/admiring-ramanujan-k2uiqe/<chemin>`).

## Les corrections
Propose-les dans le rapport. **N'en applique aucune sans mon accord**,
puis une par une, sur la branche de travail, avec les tests
(`python3 -m unittest discover -s tests`) et la synchronisation des skills
(`python3 zehon/synchroniser_skills.py`). Ne jamais éditer `.claude/skills/`
ni `zehon/*.skill` : ils sont générés.

## Critiques et retours
Applique `docs/audit/PROTOCOLE_CRITIQUES.md` à chaque livrable que tu
génères, ce rapport compris : ta critique en 5 lignes au plus, puis ma
grille (Exact / Clair / Vivant de 1 à 5, et une phrase), puis une ligne
dans `docs/audit/journal_critiques.jsonl`.

## Règles
- Des recommandations, pas des listes d'options. Sépare ce qui est mesuré
  (avec sa source) de ce qui est une hypothèse.
- Écris le rapport pour qu'il se lise facilement : phrases courtes, termes
  expliqués, pas de jargon non défini.
- Les clés `YOUTUBE_API_KEY` et `SUPADATA_API_KEY` sont dans
  l'environnement : ne les affiche jamais. Reddit et Social Blade sont
  bloqués depuis le cloud : pas de contournement.
- Donne toujours le lien vers chaque rapport rédigé.
