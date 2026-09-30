# Message d'ouverture de la prochaine session (Zehon) : la sortie du sel

À copier tel quel dans une nouvelle discussion Claude Code web, avec le
connecteur Google Drive activé.

---

Session de travail sur ma chaîne YouTube française **Zehon** (« de la
matière brute à l'objet »). On **sort la première vidéo, le sel**.

## Mise en route
1. Récupère la branche de travail et reste dessus toute la session :
   `git fetch origin claude/zelan-studio-analysis-rws9f6`, puis
   `git checkout claude/zelan-studio-analysis-rws9f6`.
2. Lis `docs/chaine2/CONTEXTE.md` (le bloc du haut dit où on en est), puis
   `zehon/video-maker/SKILL.md`.
3. `apt-get update && apt-get install -y ffmpeg`,
   `pip install opencv-python-headless pillow numpy`, puis
   `python3 -m unittest discover -s tests`.
4. Vérifie que le connecteur Google Drive répond : dossier `Zehon`
   (`1e3_Fu2nbhyfKtvCG2k54ME_W6K-gaKWB`), vidéo `Videos/01_sel`
   (`1Evm6KQ6gc2p_WfSsIdTpTeL3ItNE9SZ5`).

## Ce qui est décidé (ne pas y revenir)
- Les 76 images restent telles quelles ; la voix est prête ; les
  sous-titres incrustés (style validé) sont activés ; la vidéo se rend dans
  Colab avec `Zehon/montage_zehon.ipynb`.

## Ce que j'attends
1. Le rendu du sel est fait et passe le contrôle (lu le 30/09). Si je l'ai
   relancé depuis (avec une musique), relis `rendu/rapport.json`.
2. Aide-moi à publier : `04_publication.md`, le `.srt`, et la vérification
   des 8,1 g de sel par jour.

## Règles
- Donne tes recommandations, pas des listes d'options. Sépare ce qui est
  mesuré de ce qui est une hypothèse. Une question à la fois.
- Ne vérifie pas mes miniatures : je m'en occupe.
- Ne jamais éditer `.claude/skills/` ni `zehon/*.skill` (générés) : modifier
  `zehon/<skill>/`, puis `python3 zehon/synchroniser_skills.py`.
- Mets à jour `docs/chaine2/CONTEXTE.md` en fin de session. Commite et
  pousse sur la branche ci-dessus, avec `git fetch` avant chaque push.
- Réponds en français.
