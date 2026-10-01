# Message d'ouverture de la prochaine session (Zehon)

À copier tel quel dans une nouvelle discussion Claude Code web, avec le
connecteur Google Drive activé. Compléter la ligne « Ce que je veux
faire » avant d'envoyer.

---

Session de travail sur ma chaîne YouTube française **Zehon** (« de la
matière brute à l'objet »).

**Ce que je veux faire** : […]

## Mise en route
1. Récupère la branche de travail et reste dessus toute la session :
   `git fetch origin claude/modest-darwin-gnew9l`, puis
   `git checkout claude/modest-darwin-gnew9l`.
2. Lis `docs/chaine2/CONTEXTE.md` : le bloc du haut dit où on en est. Puis `zehon/content-maker/SKILL.md`.
3. Vérifie que le connecteur Google Drive répond : dossier `Zehon`
   (`1e3_Fu2nbhyfKtvCG2k54ME_W6K-gaKWB`), vidéo `Videos/03_aluminium`
   (`1_d4WAgXlr2IeLwFltmSWOPHVsurIhBdp`).

## Ce que j'attends
Fais ce que j'ai écrit plus haut, avec la skill `content-maker`. La
chaîne de production automatisée (skill Gemini, dossier `a_ranger/`,
notebook de rangement) est **abandonnée** : je copie les prompts à la
main dans Gemini.

## Règles
- Donne tes recommandations, pas des listes d'options. Sépare ce qui est
  mesuré de ce qui est une hypothèse. Une question à la fois.
- Affiche les prompts d'images en entier dans la conversation, un bloc de
  code par prompt.
- Ne jamais éditer `.claude/skills/` (miroir généré) : modifier
  `zehon/content-maker/`, puis `python3 zehon/synchroniser_skills.py`.
- Tests : `python3 -m unittest discover -s tests`.
- Mets à jour `docs/chaine2/CONTEXTE.md` en fin de session. Commite et
  pousse sur la branche ci-dessus, avec `git fetch` avant chaque push.
- Réponds en français.
