# Message d'ouverture de la prochaine session (Zehon)

À copier tel quel dans une nouvelle discussion Claude Code web, avec le
connecteur Google Drive activé.

---

Session de travail sur ma chaîne YouTube française **Zehon** (« de la
matière brute à l'objet »). On continue **la première vidéo, le sel**.

## Mise en route
1. Récupère la branche de travail et reste dessus toute la session :
   `git fetch origin claude/zelan-studio-analysis-rws9f6`, puis
   `git checkout claude/zelan-studio-analysis-rws9f6`.
2. Lis `docs/chaine2/CONTEXTE.md` : le bloc du haut (« Reprise au 30/09 »)
   dit exactement où on en est. Puis `zehon/content-maker/SKILL.md`.
3. Vérifie que le connecteur Google Drive répond : dossier `Zehon`
   (`1e3_Fu2nbhyfKtvCG2k54ME_W6K-gaKWB`), vidéo `Videos/01_sel`
   (`1Evm6KQ6gc2p_WfSsIdTpTeL3ItNE9SZ5`).

## Ce que j'attends, dans l'ordre
1. **Fais le point sur les pièces du sel** comme la skill le prévoit
   (« l'état des pièces ») : images, plans animés, voix (`voix/etat.json`),
   miniatures. Si la voix est prête : donne la durée, le débit, les phrases
   à réécouter, et reporte le débit dans `Memoire/lecons.md`. Remplace la
   copie Drive du notebook `voix_zehon.ipynb` par la version du dépôt.
2. **Construis la skill `video-maker`** (`docs/chaine2/nouveau_systeme.md`
   §6 et §7) : elle assemble `rendu/video.mp4` à partir de `03_scenes.md`,
   `images/`, `clips/`, `voix/voix.wav` et `voix/mots.json`. Propose
   l'ordre et chiffre l'effort avant de coder ; commence par un premier
   rendu court (quelques scènes du sel).
3. Pose-moi la question de la voix de la chaîne (ElevenLabs ou mon propre
   clone), puis mets la charte à jour selon ma réponse.

## Règles
- Donne tes recommandations, pas des listes d'options. Sépare ce qui est
  mesuré de ce qui est une hypothèse. Une question à la fois.
- Affiche les prompts d'images en entier dans la conversation, un bloc de
  code par prompt.
- Ne vérifie pas mes miniatures : je m'en occupe.
- Ne jamais éditer `.claude/skills/` (miroir généré) : modifier
  `zehon/content-maker/`, puis `python3 zehon/synchroniser_skills.py` (miroir
  et archive `.skill` en une fois).
- Mets à jour `docs/chaine2/CONTEXTE.md` en fin de session. Commite et
  pousse sur la branche ci-dessus, avec `git fetch` avant chaque push.
- Réponds en français.
