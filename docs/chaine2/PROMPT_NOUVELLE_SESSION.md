# Message d'ouverture de la prochaine session (Zehon)

À copier tel quel dans une nouvelle discussion Claude Code web, avec le
connecteur Google Drive activé.

---

Session de travail : **construire le nouveau système de production** de ma
chaîne YouTube française **Zehon**. Ligne éditoriale : « de la matière brute
à l'objet, et comment on le sait ».

## Mise en route
1. Récupère la branche de travail et reste dessus pour toute la session :
   `git fetch origin claude/zelan-studio-analysis-rws9f6`, puis
   `git checkout claude/zelan-studio-analysis-rws9f6`.
2. Lis `docs/chaine2/CONTEXTE.md`, puis **en entier**
   `docs/chaine2/nouveau_systeme.md` : c'est le cahier des charges.
   L'ancien pipeline (agents `short-*`, Remotion, `new-short`) ne sert pas
   à Zehon : ne t'en sers pas comme base.
3. Vérifie que le connecteur Google Drive répond, et si FFmpeg est
   installé.

## Déjà décidé (29/09/2026)
- Le setup : nom, ligne, format (8 min en paysage, plus 1 à 2 Shorts),
  charte (le genre en calme, images Gemini, vraies photos pour les
  preuves), voix clonée de la mienne. Tout est dans `nouveau_systeme.md`
  §1 et §2.
- Première vidéo : **le sel**. La recherche et le plan sont prêts dans
  `docs/chaine2/pilote_sel/`.
- Le système : des instructions dans mon Drive, utilisables depuis
  **n'importe quel compte Claude, même gratuit**. Le compte me pose les
  questions, rédige le script et les prompts d'images. Je génère les
  images dans Gemini. L'assemblage se fait avec une nouvelle skill
  **`video-maker`** (HyperFrames, Claude Code web) : des histoires
  racontées calmement, de légers mouvements de caméra, du texte animé.
- Simplicité avant tout.

## Ce que j'attends de cette session, dans l'ordre
1. Vérifie si un compte Claude gratuit peut lire Drive (ça fixe la forme
   des instructions).
2. **Crée l'arborescence Zehon dans mon Drive et les fichiers
   d'instructions** (`nouveau_systeme.md` §4 à §6), avec le sel comme
   exemple rempli. Montre-moi l'arborescence avant de créer les fichiers.
3. Fais un essai à blanc des instructions sur le sel, comme le ferait un
   compte gratuit, et corrige-les.
4. Crée la skill **`video-maker`** : d'abord un premier rendu HyperFrames
   (3 images, une voix de test, un texte animé), puis les blocs.
   Propose l'ordre et chiffre l'effort avant de coder.
5. Le notebook de voix simplifié (clone Qwen3-TTS et Whisper en français).

## Règles
- Donne tes recommandations, pas des listes d'options. Sépare ce qui est
  mesuré de ce qui est une hypothèse.
- Pose-moi les questions une par une.
- Ne choisis pas les sujets à ma place : propose, je tranche.
- Ne supprime aucune ancienne skill sans mon accord explicite.
- Ne jamais éditer `.claude/skills/` (c'est un miroir généré).
- Mets à jour `docs/chaine2/CONTEXTE.md` en fin de session. Commite et
  pousse sur la branche ci-dessus, avec `git fetch` avant chaque push.
- Réponds en français.
