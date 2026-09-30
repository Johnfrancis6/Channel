# Message d'ouverture de la prochaine session (Zehon) : le montage du sel

À copier tel quel dans une nouvelle discussion Claude Code web, avec le
connecteur Google Drive activé.

---

Session de travail sur ma chaîne YouTube française **Zehon** (« de la
matière brute à l'objet »). On **monte la première vidéo, le sel**.

## Mise en route
1. Récupère la branche de travail et reste dessus toute la session :
   `git fetch origin claude/zelan-studio-analysis-rws9f6`, puis
   `git checkout claude/zelan-studio-analysis-rws9f6`.
2. Lis `docs/chaine2/CONTEXTE.md` (le bloc du haut dit où on en est et ce
   que j'ai décidé), puis `zehon/video-maker/SKILL.md` et la docstring de
   `zehon/video-maker/scripts/monter.py`.
3. Installe ce qu'il faut pour les tests et les extraits :
   `apt-get install -y ffmpeg` et
   `pip install opencv-python-headless pillow numpy`. Lance
   `python3 -m unittest discover -s tests`.
4. Vérifie que le connecteur Google Drive répond : dossier `Zehon`
   (`1e3_Fu2nbhyfKtvCG2k54ME_W6K-gaKWB`), vidéo `Videos/01_sel`
   (`1Evm6KQ6gc2p_WfSsIdTpTeL3ItNE9SZ5`).

## Ce qui est décidé (ne pas y revenir)
- Les 76 images du sel restent telles quelles, même celles qui portent un
  peu de texte (040, 046, 054, 062, 075).
- La voix est prête (`voix/`) : une voix d'homme au ton narratif créée sur
  ElevenLabs, clonée par Qwen3-TTS.
- Le montage se fait avec `monter.py` (Python + FFmpeg, pas HyperFrames).
  La vidéo entière se rend dans **Colab**, parce que le connecteur Drive ne
  transfère pas plus de 10 Mo par fichier.

## Ce que j'attends, dans l'ordre
1. **Le plan du sel** : `monter.py --plan` sur `03_scenes.md` et
   `voix/mots.json`, et le point en 5 lignes (durée, pièces, avertissements).
2. **Les sous-titres animés, en option** : je veux pouvoir les ajouter pour
   qu'on suive mieux la narration. Propose un style sobre et lisible
   (quelques mots à la fois, le mot dit mis en valeur, en bas de l'image,
   sans gêner le texte animé ni les titres), calé sur les mots de
   `mots.json`, et activable par une option. Fais aussi le fichier `.srt`
   pour YouTube. Montre-moi un extrait court avec et sans, avant de
   généraliser.
3. **Le notebook Colab `montage_zehon.ipynb`** (dans `zehon/notebooks/`,
   copie dans Drive à côté de `voix_zehon.ipynb`) : il monte Drive, fait
   tourner `monter.py` sur le dossier de la vidéo et écrit
   `rendu/video.mp4` et `rendu/rapport.json` dans Drive. Une seule source
   pour le code (pas de copie de `monter.py` à entretenir à la main).
   Chiffre l'effort avant de coder.
4. **La musique** : recommande une nappe libre de droits (bibliothèque audio
   de YouTube), à bas volume sous la voix.
5. Je lance le rendu complet dans Colab ; tu lis `rendu/rapport.json` et tu
   me dis si la vidéo est prête à publier.

## Règles
- Donne tes recommandations, pas des listes d'options. Sépare ce qui est
  mesuré de ce qui est une hypothèse. Une question à la fois.
- Affiche les prompts d'images en entier dans la conversation, un bloc de
  code par prompt.
- Ne vérifie pas mes miniatures : je m'en occupe.
- Ne jamais éditer `.claude/skills/` ni `zehon/*.skill` (générés) : modifier
  `zehon/<skill>/`, puis `python3 zehon/synchroniser_skills.py`.
- Regarde toi-même quelques images de chaque rendu avant de me l'envoyer.
- Mets à jour `docs/chaine2/CONTEXTE.md` en fin de session. Commite et
  pousse sur la branche ci-dessus, avec `git fetch` avant chaque push.
- Réponds en français.
