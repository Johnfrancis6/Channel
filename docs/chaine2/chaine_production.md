# La chaîne de production des pièces (images, clips, miniatures)

État au 01/10/2026. Franco génère sur **Windows, dans un navigateur**.
Ordre de construction validé : 1. skill Gemini `zehon-images`,
2. Drive pour ordinateur et dossier de téléchargement, 3. notebook
« ranger » (vérifie, renomme, range, `images/etat.json`), 4. mise à jour
de `content-maker`.

| # | Pièce | État |
|---|---|---|
| 1 | Skill Gemini `zehon-images` | **Construite le 01/10, à tester avec Franco.** Modèle : `zehon/content-maker/assets/zehon-images/SKILL.md` ; dossier d'une vidéo fabriqué par `scripts/skill_gemini.py` ; celui de l'aluminium est dans Drive (`Videos/03_aluminium/zehon-images/`) |
| 2 | Drive pour ordinateur + `Zehon/a_ranger/` | Dossier `a_ranger/` créé le 01/10 (`1fLWTCArcXMBypMGyV5SZeMFqerb1JhHE`) ; réglage du PC à faire par Franco (ci-dessous) |
| 3 | Notebook « ranger » | À construire. Clé : d'abord `google.colab.ai` (sans clé), sinon clé AI Studio gratuite |
| 4 | `content-maker` (étape 4, état des pièces) | À faire après le test de la skill et le notebook |

## 1. La skill Gemini `zehon-images`

**Mesuré (aide Google, page « Create & manage skills », lue le 01/10)** :
import par Paramètres > Skills > Importer, d'un `SKILL.md`, d'un dossier
ou d'un `.zip` qui porte `SKILL.md` à sa racine ; nom en minuscules avec
tirets ; fichiers de référence `.md`, `.jpg`, `.png`… jusqu'à 100 Mo ;
lancement par `/` dans la conversation ; **pour changer les fichiers,
réimporter tout le dossier** (« Replace skill ») ; compte personnel,
18 ans ou plus, « Keep Activity » activé ; web, mobile, Mac.

**Le dossier** (un par vidéo) : `SKILL.md` (fixe), `prompts.md` (les lots,
la palette, les miniatures de la vidéo), `planche_bonhomme.jpg`.

**Hypothèses à tester** (aucune n'est vérifiée) :
- T1 : la génération d'images marche depuis une skill ;
- T2 : Gemini enchaîne plusieurs images dans une seule réponse, dans
  l'ordre, sans raconter d'histoire ;
- T3 : les bras en trop sont moins fréquents qu'à la main (la skill
  demande à Gemini de se relire) ;
- T4 : joindre un autre `prompts.md` dans la conversation suffit pour une
  nouvelle vidéo (sinon : réimporter le dossier, environ 1 min par compte).

**Premier essai de Franco (01/10, soir), mesuré** : `/zehon-images scènes
1 à 5` lance bien la skill, mais Gemini répond que `prompts.md` et la
planche « n'ont pas été fournis » : il ne voit pas les fichiers de
référence. Cause à établir : import du seul `SKILL.md`, ou skill qui ne
lit pas ses fichiers. Contournement : joindre les 2 fichiers dans la
conversation. Si la skill ne lit jamais ses fichiers : mettre les prompts
dans le corps de `SKILL.md` (les instructions, qu'elle lit) et joindre la
planche à chaque conversation.

**Mode d'emploi du test** (environ 20 min) :
1. Dans Drive (web), ouvre `Zehon/Videos/03_aluminium/`, clic droit sur
   `zehon-images` > Télécharger. Windows reçoit un `.zip` : clic droit >
   Extraire tout. Tu obtiens un dossier `zehon-images` avec 3 fichiers.
2. Sur gemini.google.com : Paramètres > Skills > Importer > choisis le
   dossier `zehon-images` (pas le `.zip` de Drive, qui ajoute un niveau de
   dossier). Vérifie le nom `zehon-images`, puis Créer.
3. Nouvelle conversation : tape `/zehon-images scènes 1 à 5`.
4. Note : combien d'images dans la réponse (T2), s'il y a du texte autour,
   si les numéros `scene_001`… sont dans l'ordre, et si le bonhomme
   ressemble à la planche. Compte les bras sur chaque image (T3).
5. S'il s'est arrêté avant la fin : tape `suite`.
6. Tape `/zehon-images refais 3 : <le défaut>` sur une image ratée.
7. Télécharge les 5 images (Télécharger, en haut à droite de chaque
   image) et envoie-les à Claude avec tes notes. Après le réglage du
   point 2, elles iront d'elles-mêmes dans `a_ranger/`.

## 2. Google Drive pour ordinateur + dossier de téléchargement

**Pourquoi** : tout ce que le navigateur télécharge arrive dans Drive,
quel que soit le compte Gemini ouvert, sans renommer ni déplacer.
**Un seul dossier pour toutes les vidéos**, `Zehon/a_ranger/` : on règle
le navigateur une fois ; le notebook range chaque fichier dans la bonne
vidéo (écart volontaire avec CONTEXTE, qui prévoyait un `a_ranger/` par
vidéo et donc un réglage à refaire à chaque vidéo).

1. Télécharge « Google Drive pour ordinateur » : google.com/drive/download,
   installe-le.
2. Connecte-toi avec **le compte qui possède le dossier `Zehon`**
   (celui de Drive, pas forcément celui de Gemini).
3. Dans l'Explorateur Windows, un lecteur **Google Drive (G:)** apparaît.
   Vérifie que tu vois `G:\Mon Drive\Zehon\a_ranger`.
4. Chrome : ⋮ > Paramètres > Téléchargements > Emplacement > Modifier >
   choisis `G:\Mon Drive\Zehon\a_ranger`. Laisse « Toujours demander où
   enregistrer » **désactivé**. (Edge : ⋯ > Paramètres > Téléchargements >
   Emplacement > Modifier.)
5. Test : télécharge une image de Gemini, puis ouvre
   drive.google.com > `Zehon/a_ranger/` : elle doit y être en moins d'une
   minute.

**Hypothèse** : le mode par défaut (« streaming ») suffit et le
navigateur écrit directement dans `G:`. Si le téléchargement échoue,
passer le dossier `Zehon` en « Disponible hors connexion » (clic droit).

## 3. La clé Gemini pour le vérificateur (notebook)

**Mesuré le 01/10 (pages officielles)** :
- l'offre gratuite de l'API Gemini **ne demande pas de carte** : « New
  accounts begin on the Free Tier » ; la carte ne sert qu'à passer aux
  offres payantes (prépaiement de 5 $ minimum) — page *Billing*, mise à
  jour le 28/09/2026 ;
- le **Burkina Faso** est dans la liste des pays où l'API et AI Studio
  sont disponibles (page *Available regions*, mise à jour le 28/04/2026) ;
- Colab donne à tous ses utilisateurs, **sans clé ni compte Cloud**, la
  bibliothèque `google.colab.ai` (Gemini 2.5 Flash et Flash-Lite, avec une
  limite mensuelle). **Non vérifié** : qu'elle accepte des images.

**Hypothèses sur ce qui a coincé avant** : la carte est demandée quand on
passe par la console Google Cloud (essai à 300 $, Vertex AI), par
« Set up billing » / « Upgrade » dans AI Studio, ou en choisissant un
modèle sans offre gratuite (tous les modèles qui *génèrent* des images).
Les « time out » ressemblent à la limite de requêtes de l'offre gratuite
(erreur 429), ou à un modèle payant appelé sans facturation : le notebook
espacera les appels et réessaiera.

**Recommandation** : le notebook essaie d'abord `google.colab.ai` (aucune
clé) ; la clé AI Studio ne sert que si Colab refuse les images.

**Si la clé est nécessaire** :
1. Ouvre **aistudio.google.com/apikey** (pas console.cloud.google.com),
   avec un compte Google personnel.
2. Accepte les conditions, puis « Create API key » (« Créer une clé
   API ») ; s'il demande un projet, prends celui qu'il propose ou « nouveau
   projet ».
3. **Si une page demande une carte : arrête-toi**, c'est le mauvais
   chemin. Ne clique jamais sur « Set up billing », « Upgrade » ni
   « Activate free trial ».
4. Copie la clé. Dans Colab : icône de clé (Secrets) à gauche > Ajouter >
   nom `GEMINI_API_KEY`, valeur la clé, et active « Accès au notebook ».
   Ne la colle jamais dans une cellule ni dans une conversation.
