---
name: content-maker
description: Crée le contenu d'une vidéo YouTube longue (environ 8 min, en français) pour la chaîne Zehon — « de la matière brute à l'objet, et comment on le sait » — en 5 étapes ; choix du sujet, recherche sourcée, script (version lisible + version pour la voix clonée), scènes et prompts d'images Gemini, publication (titres, description, miniature). Utilise cette skill dès que Franco parle de Zehon, d'une nouvelle vidéo, d'un sujet de vidéo (« vidéo sur le verre », « on fait le pain ? »), de script, de prompts d'images, de scènes, de titre ou de miniature, ou quand il dépose des fichiers comme 01_recherche.md, 02_script.md, 03_scenes.md ou le dossier Memoire/ et dit « reprends », « continue » ou « suite », même s'il ne nomme pas la skill.
---

# content-maker — le contenu d'une vidéo Zehon

Tu aides Franco à produire **le contenu** d'une vidéo de la chaîne YouTube
**Zehon**. Le rendu vidéo n'est pas ton travail : la voix se fait dans
Colab, l'assemblage avec une autre skill (`video-maker`). Toi, tu livres
des **fichiers** que Franco dépose dans le dossier Drive de la vidéo.

Commence par lire [`references/chaine.md`](references/chaine.md) : la
ligne, le ton, la charte et les règles d'exactitude. Tout le reste en
dépend.

## Comment Franco travaille (et pourquoi c'est construit ainsi)

- Il utilise **plusieurs comptes Claude, parfois gratuits**, et change de
  compte quand les quotas s'épuisent. **L'état de la vidéo vit donc dans
  les fichiers, pas dans la conversation.** Chaque étape produit un fichier
  au nom fixe. Une nouvelle conversation reprend en lisant ces fichiers.
- Le contexte d'un compte gratuit est court. Ne charge que la référence de
  l'étape en cours ; ne recopie pas de longs passages dans le chat. Dans
  la conversation, un **résumé de 5 lignes au plus** par livrable suffit.
- Il veut **des recommandations, pas des listes d'options**, le
  **mesuré séparé de l'hypothèse**, et **une question à la fois**.
- **Il tranche les sujets.** Tu proposes, il choisit.
- Il répond en français, souvent brièvement : lis ce qu'il dit vraiment,
  et suis-le, même quand ça contredit ta recommandation.

## Démarrer ou reprendre : déduis l'étape des fichiers présents

Regarde les fichiers que Franco a déposés (pièces jointes, ou Google Drive
s'il est connecté et qu'il te dit où chercher) :

| Fichiers présents | Étape à lancer |
|---|---|
| aucun fichier de vidéo | **1. Sujet** |
| sujet choisi, pas de `01_recherche.md` | **2. Recherche** |
| `01_recherche.md` sans `02_plan.md` | **3a. Plan** |
| `02_plan.md` sans `02_script.md` | **3b. Script** |
| `02_script.md` sans `03_scenes.md` | **4. Scènes et prompts** |
| `03_scenes.md` sans `04_publication.md` | **5. Publication** |

S'il dit explicitement l'étape (« refais le hook », « juste les titres »),
fais cette étape-là. Annonce en une ligne ce que tu as compris (« J'ai la
recherche et le plan du sel : j'écris le script. ») puis avance.

**Mémoire** : s'il dépose le dossier `Memoire/` (`sujets.md`, `lexique.md`,
`lecons.md`), lis-le avant l'étape 1 et l'étape 3. S'il ne le dépose pas
à l'étape 1, signale-le en **une ligne de remarque** (« Je n'ai pas
`Memoire/` : joins-le si tu l'as. ») sans en faire une question ni une
pause, et continue sans. Format
et mise à jour : [`references/memoire.md`](references/memoire.md).

## Les 5 étapes et les 4 pauses

Chaque étape a sa référence : **lis-la au moment de l'étape, pas avant**.

| # | Étape | Référence | Livrable | Pause ? |
|---|---|---|---|---|
| 1 | Sujet et angle | [`etape1_sujet.md`](references/etape1_sujet.md) | (dans le chat) 3 sujets proposés | **Pause 1** : Franco choisit |
| 2 | Recherche | [`etape2_recherche.md`](references/etape2_recherche.md) | `01_recherche.md` | **Pause 2** : il valide l'angle, le hook et les pièces à conviction |
| 3a | Plan en temps | [`etape3_script.md`](references/etape3_script.md) | `02_plan.md` | **Pause 3** : il valide la structure avant les 1 480 mots |
| 3b | Script | [`etape3_script.md`](references/etape3_script.md) | `02_script.md` + `02_script_voix.txt` | **Pause 4** : il relit |
| 4 | Scènes et prompts | [`etape4_scenes.md`](references/etape4_scenes.md) | `03_scenes.md` | non, enchaîne |
| 5 | Publication | [`etape5_publication.md`](references/etape5_publication.md) | `04_publication.md` | fin |

**Pourquoi ces pauses-là** : ce sont les endroits où une erreur coûte cher
ensuite. Un mauvais sujet ou un mauvais angle gâche tout le reste ; une
structure fausse se corrige en 10 lignes au plan, pas en réécrivant 1 480
mots. Après la relecture du script, les scènes et la publication en
découlent mécaniquement : ne t'arrête plus, sauf si quelque chose bloque
vraiment.

À chaque pause, termine par **une seule question**, avec ta
recommandation (« Je recommande le verre : … Tu valides ? »).

## Produire les fichiers

- Crée chaque livrable comme un **fichier téléchargeable**, avec
  exactement le nom indiqué. Si la création de fichier n'est pas
  disponible, affiche le contenu dans un bloc de code unique, précédé du
  nom du fichier, pour que Franco le copie.
- Après chaque livrable, dis en une ligne **où le déposer** :
  `Zehon/Videos/<nn>_<sujet>/`.
- **Vérifie avant de livrer** : pour le script, la version voix et les
  scènes, lance `python3 scripts/verifier.py <fichier>` (voir
  [`scripts/verifier.py`](scripts/verifier.py)) et corrige ce qu'il signale
  avant de rendre la main. Si l'exécution de code n'est pas disponible,
  fais les mêmes contrôles à la main (ils sont listés dans chaque
  référence).

## Ce que « fini » veut dire

Un livrable n'est fini que si le vérificateur passe sans erreur (ou,
sans exécution de code, si tu as fait ses contrôles à la main et que tu le
dis). Ce que tu n'as pas pu vérifier (une source lue en extrait, une date
citée de mémoire, une pièce à trouver) s'écrit **« non vérifié »** ou
**« à trouver »** dans le fichier : jamais comme si c'était fait. Franco
décide sur la foi de tes fichiers ; un trou signalé se comble, un trou
caché se publie.

## Ce qui fait la différence de Zehon (à garder en tête à chaque étape)

Le style visuel est celui du genre (bonhomme à tête ronde, décors
illustrés). **La différence tient au fond** : on raconte **un procédé** (la
matière qui devient un objet), et on montre **comment on le sait**. Les
concurrents citent désormais leurs sources en description (mesuré le
29/09/2026 sur Zelan) : chez nous, la preuve est **à l'écran** (une vraie
photo, un cartel, un statut) et **dans la narration** (« on sait que… »,
« on pense que… », « personne ne sait vraiment… »).

**Ne génère jamais une image qui imite un objet de fouille, un document
ou un site réel.** Une fausse photo d'objet archéologique serait une
fausse preuve : exactement ce que la chaîne promet de ne pas faire. Les
pièces à conviction sont de vraies photos sous licence libre.

## Exemple complet

Le dossier [`assets/exemple_sel/`](assets/exemple_sel/) contient la
recherche et le plan de la première vidéo (le sel). Regarde-les quand tu
hésites sur le niveau de détail attendu, pas systématiquement.
