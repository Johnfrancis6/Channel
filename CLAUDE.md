# Zehon — chaîne YouTube « de la matière brute à l'objet »

Vidéos de 8 min en français : comment une matière devient un objet du
quotidien. Franco tranche les sujets et valide aux pauses ; Claude écrit le
contenu, Franco produit les pièces (images Gemini, voix Colab).

**Pour reprendre : lire [docs/chaine2/CONTEXTE.md](docs/chaine2/CONTEXTE.md)**
(le bloc du haut dit où on en est).

## Où sont les choses

- `zehon/content-maker/` : la skill qui fait le contenu d'une vidéo
  (recherche, script, scènes, prompts, publication). Tout le fonctionnement
  est dans son `SKILL.md`.
- `zehon/notebooks/voix_zehon.ipynb` : la voix off (Colab, copie dans Drive).
- Google Drive, dossier `Zehon/` : la mémoire (`Memoire/`), la charte
  (`Charte/`) et les vidéos (`Videos/<nn>_<sujet>/`). L'état d'une vidéo
  vit dans ses fichiers Drive, pas dans le dépôt.
- `docs/chaine2/` : le cadrage et l'historique des décisions.

## Règles

- Ne jamais éditer `.claude/skills/` ni `zehon/*.skill` : ils sont générés.
  Modifier `zehon/<skill>/`, puis `python3 zehon/synchroniser_skills.py`.
- Tests : `python3 -m unittest discover -s tests`.
- `git fetch` avant chaque push.
- L'ancienne chaîne (Shorts anglais, agents `short-*`, Remotion) est
  archivée sur la branche `archive/pipeline-shorts-2026-09-30`.
