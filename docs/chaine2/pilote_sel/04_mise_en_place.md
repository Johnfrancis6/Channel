# Mise en place de la pilote dans le pipeline (29/09/2026)

> **OBSOLÈTE (29/09/2026, décision de Franco).** La chaîne 2 ne passe pas
> par l'ancien pipeline (agents A2 à A7, Remotion, `formats_video.py`). Elle
> aura **un nouveau système, simple** : des instructions dans Drive,
> utilisables depuis n'importe quel compte Claude, des images Gemini et une
> nouvelle skill `video-maker`. Les anciennes skills seront supprimées. Voir
> [`../nouveau_systeme.md`](../nouveau_systeme.md). Le document est gardé
> pour ses mesures (débit, budget par temps, seuils de phrase), qui restent
> valables.

**Rien n'est encore modifié dans le code.** Ce document propose l'ordre et
chiffre l'effort, comme demandé. Franco valide avant qu'on touche au code.

Décisions de Franco prises en compte (29/09) : sujet *le sel* ; voix =
**clone de sa voix** (Qwen3-TTS) ; rendu de la chaîne 2 sur **HyperFrames**
(la chaîne IA reste sur Remotion) ; **style du genre entier**, avec des
scènes en images IA générées par **Gemini**. Contraintes reprises de CONTEXTE.md : pas
de code multi-chaînes avant la pilote, `--root` explicite, seulement les
réglages que la pilote exige.

**Principe** : chaque réglage « en dur » est **un paramètre avec la valeur
anglaise par défaut**, pas un remplacement. Sinon, passer la langue en
français casserait la chaîne IA, qui tourne sur le même code.

---

## 1. Le point de chaque chantier (CONTEXTE, section 4)

| # | Point | Mesuré | Proposition | Effort |
|---|---|---|---|---|
| 1 | **Voix** : `language="English"` en dur (notebook `voix_off.ipynb`, cellule 10, lignes 86 et 97) et `language="en"` pour Whisper (cellule 12, ligne 95) | Qwen3-TTS gère 10 langues, dont le français, avec un clonage possible dès 3 s d'audio ([QwenLM/Qwen3-TTS](https://github.com/QwenLM/Qwen3-TTS)). La qualité du clone français n'est **pas mesurée** | Deux paramètres dans la cellule de configuration : `LANGUE_TTS = "English"` et `LANGUE_WHISPER = "en"`. Pour la pilote : `"French"` et `"fr"`. Mettre à jour `tests/test_notebook_voix.py`. **Franco** fournit `ref.wav` (15 à 30 s, français, pièce calme) et `ref.txt` (le texte exact) | Code : 1 h. Franco : 30 min. Premier essai Colab : 1 h |
| 2 | **Débit** : `MOTS_PAR_SECONDE = 2.8`, global | 2,8 mesuré en anglais sur un Short ; 3,09 mesuré sur Zelan en français | Un débit **par format** : court 2,8 (inchangé), long **3,0** (hypothèse, prudente sous les 3,09). Aujourd'hui, seule la chaîne 2 produit du format long : c'est sans effet sur la chaîne IA. À recalibrer après le premier enregistrement | 30 min + tests |
| 3 | **Budget** : `MOTS_PAR_IDEE[long] = 300`, `IDEES_MAX_DEFAUT[long] = 8` | *Le fer* : 10 temps, 123 mots par temps en moyenne, **155 mots par temps une fois le hook et la fin répartis** (`cout_total_par_idee`) | `MOTS_PAR_IDEE[long] = 150`, `IDEES_MAX_DEFAUT[long] = 10`. Budget = 1 500 mots, soit 8 min 20 s à 3,0 mots/s. Mettre à jour le commentaire (« mesuré sur *le fer*, 1 vidéo ») et `tests/test_budget_script.py` (le test qui suppose 8 × 300) | 1 h |
| 4 | **Le Rédacteur suppose l'anglais** (`agents/short-redacteur/SKILL.md` l. 88 ; même chose dans `skills/new-short/SKILL.md` l. 79) | Vérifié par grep : ce sont les deux seules mentions | Remplacer par : « La langue est celle de `00_Profil/profil_chaine.md` de la racine. » C'est un fichier de profil **par racine Drive**, pas du code multi-chaînes. Puis `python3 agents/_synchroniser_vers_claude_skills.py` et `--verifier` | 30 min |
| 5 | **Seuils de phrase du Filtre TTS** (8 à 18 mots) | *Le fer* : médiane de 12 mots, quartiles 8 et 17. 59 % des phrases sont dans la cible ; 9 sur 116 dépassent 22 mots | **Pas de changement.** Les seuils anglais collent au français. À re-mesurer sur notre premier script (la segmentation du *fer* vient de sous-titres automatiques, donc des phrases reconstruites) | 0 |
| 6 | **Profil de la racine chaîne 2** : `profil_chaine.md`, `conventions.md`, `lexique_prononciation.md` en français | Les fichiers de la chaîne IA sont en anglais | Rédiger les trois fichiers : tutoiement, « Sauf que », marqueurs d'incertitude, pas d'appel à s'abonner, fin sur une question ; lexique amorcé avec les termes du dossier *sel* | 2 h (cette session peut les rédiger) |
| 7 | **Chercheur** : marques établi, probable, hypothèse | Pas dans `agents/short-chercheur/SKILL.md` | Ajouter la règle et la colonne de statut au format de `01_recherche.md`. Pour la chaîne IA, la colonne reste facultative. Puis synchroniser | 45 min |
| 8 | **Nouvelle racine Drive** | La racine Drive de la chaîne 2 n'existe pas | Franco crée le dossier. On lance l'initialisation de structure avec `--root`, puis `new_short.py --root … --pilier a_determiner` | 30 min (plus la création du dossier par Franco) |
| 9 | **Rendu HyperFrames** (socle + blocs) | Voir [`03_images.md`](03_images.md), sections 4 et 5 | Répertoire `hyperframes/`, séparé de `composants/` | Socle environ 6 h ; blocs 18 à 24 h |
| 10 | **Style du genre** (décision de Franco) : planche de référence du bonhomme, prompt de style, 3 à 5 images test | Rien n'existe | Voir [`03_images.md`](03_images.md) §1 | 2 h |
| 11 | **Génération d'images Gemini** (`generer_images.py`, prompts par scène dans A6) | `GEMINI_API_KEY` **absente** de l'environnement au 29/09 | Voir [`03_images.md`](03_images.md) §5. Franco ajoute la clé aux secrets de l'environnement | 6 à 8 h |

---

## 2. Ordre recommandé

L'ordre suit le **chemin critique** : la voix dépend de Franco (enregistrer
un échantillon), et le rendu est le plus gros poste.

1. **Tout de suite, côté Franco** : enregistrer `ref.wav` et `ref.txt`. Ça
   débloque le point 1 sans attendre le reste.
2. **Textes et réglages** (points 4, 7, 3, 2, puis 6) : environ **5 h**. Ils
   rendent possibles la recherche, le script et le filtre en français.
3. **Voix** (point 1) : **2,5 h**, dès que l'échantillon est là. On mesure
   le vrai débit et on corrige le point 2.
4. **Style et images test** (point 10) : **2 h**. On sait tôt si Gemini
   tient le bonhomme. Si ce n'est pas le cas, tout le reste du plan images
   change.
5. **Socle HyperFrames** (point 9) : **6 h**. Un premier rendu 1920×1080
   avec la voix, les sous-titres et 3 images test, avant d'écrire le moindre
   bloc.
6. **Génération d'images** (point 11) : **6 à 8 h**.
7. **Blocs** dans l'ordre de `03_images.md` §4 : `scene-image`,
   `piece-a-conviction`, `chaine-transformation`, `frise`, sous-titres.
   **Environ 16 à 21 h.** `chiffre-compare` et `titre-question` peuvent
   passer en images Gemini si le temps manque.
8. **Racine Drive et state.json** (point 8), puis on fait tourner la pilote
   de bout en bout.

**Total estimé** : environ **45 à 55 h** de travail, dont 30 à 40 h pour les
images et le rendu. **Hypothèse** : à 20 h par semaine, la pilote sort en
**environ 3 semaines** si le rendu passe sans surprise. Deux postes portent
le risque parce que rien n'y est mesuré : le socle HyperFrames et la
cohérence du bonhomme sous Gemini.

## 3. Ce qui reste hors de la pilote

`profil_chaine.json`, `--chaine`, la migration de la chaîne IA vers
HyperFrames, la génération automatique des miniatures.
