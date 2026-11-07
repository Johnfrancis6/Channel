# Message d'ouverture de la session 2 : qualité du contenu et veille

À lancer **après** la session 1 (audit du pipeline,
[PROMPT_SESSION_1_AUDIT_PIPELINE.md](PROMPT_SESSION_1_AUDIT_PIPELINE.md)).
À copier tel quel dans une nouvelle discussion Claude Code web, dans ce
dépôt, avec le connecteur Google Drive activé.

---

Session de travail : **rendre le contenu de mes vidéos plus agréable à
suivre**, et mettre en place une **veille permanente** sur les concurrents
de ma chaîne anglaise « Whose Dime » (série « Who Pays? »), avec les
externalités à exploiter. L'audit du pipeline de production est fait :
cette session ne le refait pas, elle s'appuie dessus.

## Mise en route
1. `git fetch origin claude/admiring-ramanujan-k2uiqe`, puis
   `git checkout claude/admiring-ramanujan-k2uiqe` (`git fetch` avant
   chaque push).
2. Lis, dans cet ordre :
   - `reports/Audit pipeline de production.md` (session 1) et les
     corrections que j'y ai acceptées ;
   - `docs/audit/journal_critiques.jsonl` : mes notes Exact / Clair /
     Vivant et mes remarques, livrable par livrable ;
   - `reports/Crayon Capital et concurrents.md` : ce qui fait gagner et
     perdre les chaînes du créneau (personnage nommé et paradoxe dans
     l'ouverture, mini-scènes dialoguées, tension dans le titre) ;
   - `docs/finance/PLAN_ACTION.md` et `docs/finance/marques.md`.
3. Les transcriptions YouTube passent par l'API Supadata
   (`SUPADATA_API_KEY`), les mesures par l'API YouTube Data v3
   (`YOUTUBE_API_KEY`). Ne les affiche jamais. Reddit et Social Blade
   sont bloqués : pas de contournement.

## Ce que j'attends, dans l'ordre
1. **Qualité du contenu.** Mes scripts et ma voix off sont robotiques,
   sans narration humaine, peu nuancés, peu compréhensibles et très
   formels. Compare, à partir de transcriptions, mes scripts avec les hits
   du créneau (Crayon Capital, Built On You, CEOzoned, JunkBondInvestor) :
   personnages, scènes, dialogues, rythme des phrases, registre, nuances,
   explications. Donne des règles d'écriture mesurables (longueur des
   phrases, part de scènes, nombre de personnages nommés…) et réécris un
   passage témoin avant/après. Fais de même pour la voix : ce qui la rend
   robotique et les réglages ou méthodes qui la corrigent, à tester à
   l'aveugle.
2. **Veille hebdomadaire sur les concurrents de Whose Dime** (pas Zehon) :
   un outil qui relève chaque semaine, pour environ 300 unités de quota,
   les nouvelles vidéos et les hits (≥5 fois la médiane) des chaînes du
   créneau, les nouveaux entrants, les changements de titres, et les
   marques traitées (mise à jour de la colonne « vide » de `marques.md`).
   Sortie : une page de synthèse datée dans `docs/veille/`.
3. **Externalités à exploiter**, dans la même page hebdomadaire :
   - **actualité et calendrier** : résultats trimestriels, procès,
     anniversaires, sorties de films, saisons (impôts, fêtes) qui font
     monter la demande sur une marque de `marques.md` ;
   - **faiblesses des concurrents** : sujets non traités, erreurs relevées
     dans leurs commentaires, chaînes qui ralentissent ou s'arrêtent.
4. **Les questions** utiles pour itérer : pose-les toutes, groupées, avec
   ta recommandation pour chacune.
5. Écris le rapport dans `reports/Qualité du contenu et veille.md`, l'outil
   de veille dans `docs/veille/outils/`, commite, pousse, et **donne-moi
   le lien GitHub de chaque rapport écrit**
   (`https://github.com/Johnfrancis6/Channel/blob/claude/admiring-ramanujan-k2uiqe/<chemin>`).

## Critiques et retours
Applique `docs/audit/PROTOCOLE_CRITIQUES.md` à chaque livrable que tu
génères : ta critique en 5 lignes au plus, puis ma grille (Exact / Clair /
Vivant de 1 à 5, et une phrase), puis une ligne dans
`docs/audit/journal_critiques.jsonl`.

## Règles
- Des recommandations, pas des listes d'options. Sépare ce qui est mesuré
  de ce qui est une hypothèse.
- Ne modifie aucune skill sans mon accord ; jamais `.claude/skills/` ni
  `zehon/*.skill` (générés : modifier `zehon/<skill>/`, puis
  `python3 zehon/synchroniser_skills.py`).
- Donne toujours le lien vers chaque rapport rédigé.
