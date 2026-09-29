# Message d'ouverture de la prochaine session (chaîne 2)

À copier tel quel dans une nouvelle discussion.

---

Session de travail : **production de la vidéo pilote** de ma seconde chaîne
YouTube (en français). Ligne éditoriale : « de la matière brute à l'objet,
et comment on le sait ».

## Mise en route
1. Récupère la branche de travail et reste dessus pour toute la session :
   `git fetch origin claude/zelan-studio-analysis-rws9f6`, puis
   `git checkout claude/zelan-studio-analysis-rws9f6`.
2. Lis `CLAUDE.md`, puis **en entier** `docs/chaine2/CONTEXTE.md`. C'est le
   contexte de reprise : décisions, modèle de structure mesuré, sujets
   candidats, ce qui bloque la pilote dans le pipeline, méthode de
   recherche. Va voir les autres documents seulement quand CONTEXTE.md y
   renvoie.
3. Vérifie que `YOUTUBE_API_KEY` est définie (sans jamais afficher sa
   valeur), que `youtube.com` est accessible, et installe yt-dlp si besoin.

## Déjà décidé (29/09/2026)
- Chaîne en français, en plus de ma chaîne IA (anglais, Shorts), qui
  continue. Même pipeline, même `composants/` (Remotion).
- Ligne : chaque vidéo raconte comment une matière est devenue un objet du
  quotidien, de la préhistoire à aujourd'hui, et montre les preuves.
- Vidéo longue en paysage d'environ 8 min (environ 1 480 mots), plus 1 à 2
  Shorts. 1 vidéo par semaine au départ. 20 h par semaine.
- La chaîne appartient réellement à une connaissance en France (AdSense à
  son nom). Je suis gestionnaire, avec un contrat écrit.
- Pas de code multi-chaînes (`profil_chaine.json`, `--chaine`) avant la
  pilote. Seulement les réglages que la pilote exige (langue, débit),
  avec `--root` explicite.

## Ce que j'attends de cette session, dans l'ordre
1. **Recherche active** : me faire trancher le sujet de la pilote (ta
   recommandation est le pain), puis construire le dossier de recherche.
   Sources primaires ou institutionnelles, chaque affirmation marquée
   établi, probable ou hypothèse, et au moins une pièce à conviction
   montrable (photo sous licence libre) par question d'enquête.
2. **Rédaction du script** : structure mesurée sur *le fer* de Zelan (hook
   de 30 s sur un objet et un paradoxe, 3 à 4 questions d'enquête en 8 à
   10 temps, « Sauf que », tutoiement, retours au présent, fin sur une
   question ouverte, pas d'appel à s'abonner). Avant d'écrire, récupère et
   segmente les transcriptions en attente (la journée, l'eau sale, le sucre
   de Zelan, et une vidéo de Je T'explique Comment) pour comparer un succès
   et un raté.
3. **Images** : charte hors de la grammaire du genre (pas de bonhomme à
   tête ronde, pas de texte jaune cerné de noir), miniature
   « transformation » (la matière et l'objet fini, sans personnage), place
   des vraies photos pour les pièces à conviction. Dis-moi quels
   composants Remotion manquent pour montrer une transformation et une
   pièce à conviction.
4. **Mise en place de la vidéo** : ce qu'il faut régler dans le pipeline
   pour produire la pilote (voix française, débit, budget par idée,
   Rédacteur supposé en anglais, seuils du Filtre TTS). La liste est dans
   CONTEXTE.md, section 4. Propose l'ordre et chiffre l'effort avant de
   toucher au code.

## Règles
- Donne tes recommandations, pas des listes d'options. Sépare ce qui est
  mesuré de ce qui est une hypothèse.
- Pose-moi les questions une par une (voix, budget, charte…).
- Ne choisis pas les sujets à ma place : propose, je tranche.
- Écris les résultats dans `docs/chaine2/` et mets à jour CONTEXTE.md en fin
  de session. Commite et pousse sur la branche ci-dessus, avec `git fetch`
  avant chaque push.
- Ne jamais éditer `.claude/skills/` (c'est un miroir généré).
- Réponds en français.
