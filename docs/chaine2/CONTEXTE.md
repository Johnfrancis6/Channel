# Zehon — contexte de reprise (01/10/2026)

Court par règle (60 lignes au plus). L'historique complet, avec les
mesures et les raisons des décisions : [`historique.md`](historique.md).
Branche de travail : `claude/optimistic-bohr-5f78k4` (`BRANCHE` des lanceurs).

## État : chaîne gelée

**Chaîne gelée le 07/11/2026 (décision D1) : tout l'effort va à Whose
Dime. Reprendre ici seulement si Franco relance Zehon.**

- **Le sel** (`Videos/01_sel`) : rendu et validé par Franco le 30/09,
  **pas publié**.
- **Le verre** (`Videos/02_verre`) : rendu le 01/10 depuis
  `claude/zelan-studio-analysis-rws9f6@15b0fe0` ; **rendu à refaire** avec
  le bandeau sombre sous le texte animé.
- **L'aluminium** (`Videos/03_aluminium`) : contenu fini le 01/10 (de la
  recherche à la publication), aucune pièce produite.
- Décisions en attente si Zehon reprend (`docs/whosedime/DECISIONS.md`) :
  Z1 couper « Toi, tu en manges environ 3 kilos par an » (8,1 g/jour
  jamais vérifié) ; Z2 garder le titre et la miniature « NÉE EN 1959 ?! »
  du verre ; Z3 refaire le rendu du verre avec le bandeau.
- **Revue du pipeline (08/11)** : [`revue_pipeline_2026-11-08.md`](revue_pipeline_2026-11-08.md),
  3 points P1 à corriger avant toute relance (dont la branche des lanceurs, sans le bandeau).
- Lanceurs Drive fixes : `Zehon/montage_zehon.ipynb` et
  `Zehon/voix_zehon.ipynb` (clone du dépôt, puis `zehon/notebooks/lanceur.py`).

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
| Sessions | une par phase (5 par vidéo) ; à chaque fin, la skill s'arrête et donne le modèle et le prompt de relance (`content-maker`, « Les sessions ») |

Règles de travail : recommandations, pas d'options ; le mesuré séparé de
l'hypothèse ; une question à la fois ; `.claude/skills/` et `zehon/*.skill`
sont générés ; `git fetch` avant chaque push.

Questions ouvertes : contrat signé ; nom à l'INPI ; budget ; objectif à
6 mois.
Sujets suivants candidats : le pain, le sucre (vérifier Zelan).
