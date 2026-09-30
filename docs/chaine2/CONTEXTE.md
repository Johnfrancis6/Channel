# Zehon — contexte de reprise (30/09/2026, nuit)

Court par règle (60 lignes au plus). L'historique complet, avec les
mesures et les raisons des décisions : [`historique.md`](historique.md).
Branche de travail : `claude/zelan-studio-analysis-rws9f6`.

## État

- **Le sel** (`Videos/01_sel`) : vidéo **validée par Franco** (sans
  musique, sous-titres incrustés, 7 min 55 s, contrôle passé). Reste la
  publication.
- **Système allégé (30/09, nuit)** :
  - Dans Drive, `Zehon/montage_zehon.ipynb` (`1lG8qLhjCM4C6Kum_zEoTRW45rsuQ5Tpg`)
    et `Zehon/voix_zehon.ipynb` (`1RPyG8c5_Drc1QSql9yHDIs7yj5wDRn05`) sont
    des **lanceurs fixes** (formulaire + clone du dépôt, puis
    `zehon/notebooks/lanceur.py`) : **plus jamais de recopie dans Drive**.
    Anciennes copies à la corbeille. Testé ici de bout en bout sur un faux
    Drive, clone GitHub compris ; **pas encore lancé dans Colab**.
  - `monter.py` écrit `rendu/verdict.json` (moins de 1 Ko) et
    `rendu/apercu/` (6 JPEG de 640 px, environ 5 Ko chacun) ; la skill
    `video-maker` lit ceux-là, plus le rapport en entier ni les pièces ;
    les extraits se rendent dans Colab (`EXTRAIT`).

## Décisions en vigueur

| Sujet | Décision |
|---|---|
| Chaîne | **Zehon** (@zehonfr), en français : « de la matière brute à l'objet », avec les preuves |
| Format | ~8 min (~1 480 mots), 1 vidéo par semaine, 20 h par semaine |
| Propriété | une connaissance en France est propriétaire ; contrat écrit avec Franco avant publication |
| Style | bonhomme à tête ronde, images Gemini, mouvements lents, texte sobre (`nouveau_systeme.md` §2) |
| Preuves | vraies photos sous licence libre ; jamais d'image générée qui imite une pièce réelle |
| Voix | voix d'homme narrative (ElevenLabs), clonée par Qwen3-TTS dans Colab |
| Sous-titres | incrustés (style validé) + `sous_titres.srt` pour YouTube Studio |
| Musique | prête (`MUSIQUE`, −26 dB) ; le sel est sans musique |
| Outils | `content-maker` (contenu), `video-maker` (montage) ; notebooks du dépôt via les lanceurs Drive |

Règles de travail : recommandations, pas d'options ; le mesuré séparé de
l'hypothèse ; une question à la fois ; `.claude/skills/` et `zehon/*.skill`
sont générés ; `git fetch` avant chaque push.

## Suite, dans l'ordre

1. **Essai du lanceur de montage dans Colab** : `EXTRAIT` = `1-10` sur le
   sel, puis « lis le verdict » (vérifie le lanceur réel et l'aperçu).
2. Vérifier les 8,1 g de sel par jour et l'usage commercial de la voix
   ElevenLabs.
3. Publier le sel (`04_publication.md`, `rendu/sous_titres.srt`).
4. Recommandé ensuite : fusionner dans `main` (puis `BRANCHE` = `main`
   dans les deux lanceurs, une fois), script de démarrage du conteneur
   (ffmpeg, OpenCV), un modèle plus léger pour les tâches simples.

Questions ouvertes : contrat signé ; nom à l'INPI ; budget ; objectif à
6 mois.
Sujets suivants candidats : le pain, le verre, le sucre (vérifier Zelan).
