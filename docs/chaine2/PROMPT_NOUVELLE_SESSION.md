# Message d'ouverture de la prochaine session (Zehon) : alléger le système

À copier tel quel dans une nouvelle discussion Claude Code web, avec le
connecteur Google Drive activé.

---

Session courte sur ma chaîne YouTube **Zehon**. On allège le système pour
consommer moins de tokens. Économise les tokens toi-même : lis seulement ce
qui sert, pas de relecture de gros fichiers.

## Mise en route
1. `git fetch origin claude/zelan-studio-analysis-rws9f6`, puis
   `git checkout claude/zelan-studio-analysis-rws9f6` ; reste dessus.
2. Lis le bloc du haut de `docs/chaine2/CONTEXTE.md` (seulement lui), puis
   `zehon/video-maker/SKILL.md`.
3. `apt-get update && apt-get install -y ffmpeg`,
   `pip install opencv-python-headless pillow numpy`, puis
   `python3 -m unittest discover -s tests`.

## Ce que j'attends, dans l'ordre (décidé le 30/09)
1. **Un lanceur Drive qui ne change plus** : la copie Drive de
   `montage_zehon.ipynb` (et de `voix_zehon.ipynb`) devient quelques lignes
   qui prennent le vrai notebook dans le dépôt et l'exécutent. Une fois
   déposé, plus jamais de recopie dans Drive. Garde le formulaire de
   réglages côté lanceur.
2. **Un verdict court et un aperçu, écrits par Colab** : le notebook écrit
   `rendu/verdict.json` (moins de 1 Ko : pret, contrôle, avertissements,
   durée, rendu_s) et `rendu/apercu/` (6 JPEG réduits : un titre, un plan
   animé, des sous-titres, le début et la fin). La skill `video-maker` lit
   ces fichiers-là, plus `rapport.json` en entier ; les extraits se rendent
   dans Colab (`EXTRAIT`), plus de téléchargement de pièces.
3. **Un `CONTEXTE.md` court** (60 lignes au plus : état, décisions en
   vigueur, suite) ; l'historique part dans `docs/chaine2/historique.md`.

## Règles
- Recommandations, pas de listes d'options ; mesuré séparé de
  l'hypothèse ; une question à la fois. Réponds en français.
- Ne jamais éditer `.claude/skills/` ni `zehon/*.skill` (générés) : modifier
  `zehon/<skill>/`, puis `python3 zehon/synchroniser_skills.py`.
- Commite et pousse sur la branche ci-dessus, avec `git fetch` avant chaque
  push. Mets à jour `CONTEXTE.md` en fin de session.
