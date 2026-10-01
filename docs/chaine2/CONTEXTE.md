# Zehon (chaîne 2) — contexte de reprise (état au 01/10/2026)

> **Reprise au 01/10/2026, fin de session : la chaîne de production des
> pièces (images, clips, miniatures).** Franco perd du temps à copier les
> prompts, renommer, télécharger et ranger chaque image. Demande : que
> Gemini enchaîne la génération, que tout arrive rangé dans Drive, avec un
> vérificateur, une reprise possible sur un autre compte quand le quota est
> épuisé, et la même chose pour les clips (Flow). **Franco génère sur
> Windows, dans un navigateur.** Rien n'est encore construit.
>
> **Vérifié le 01/10 (pages officielles Google)** :
> - API Gemini : **aucune offre gratuite** pour les modèles d'image
>   (Nano Banana 2, 2 Lite, Pro) ni pour Veo (page des prix, mise à jour
>   le 01/10/2026). Gemini 2.5 Flash Image est arrêté le 02/10/2026.
> - Essai Google Cloud à 300 $ : ne paie pas l'API Gemini dans AI Studio.
>   Sur Vertex AI : possible selon un blog seulement (non vérifié).
> - **Gratuits et acceptant des images en entrée** : Gemini 2.5 Flash,
>   2.5 Flash-Lite, 3.5 Flash-Lite (offre gratuite de l'API). C'est ce qui
>   rend un vérificateur gratuit possible.
> - **Flow** : 50 crédits par jour sans abonnement ; Veo 3.1 Lite = 10
>   crédits, Fast = 20. L'agent Flow sait générer par lots, renommer,
>   regrouper (requêtes gratuites, quota quotidien non chiffré). Pas
>   d'export Drive documenté.
> - **Skills Gemini** (lancées le 30/09/2026, remplacent les Gems) :
>   gratuites, compte personnel, 18 ans ou plus, « Keep Activity »
>   activé. Un dossier `SKILL.md` + fichiers de référence (png, md, pdf…)
>   jusqu'à 100 Mo, lancé par `/nom`. Import du dossier : web et Mac
>   seulement. Marchent avec les apps connectées Workspace. Ne marchent
>   pas avec : créer une vidéo ou de la musique, Canvas, Deep Research.
>   Ajout de fichiers depuis Drive : « bientôt ».
> - Gemini ne sait pas enregistrer une image dans un dossier Drive.
>   « Créer des images » dans Drive : AI Pro ou Ultra seulement, en
>   anglais.
> - Application Gemini gratuite : environ 20 images par jour (site non
>   officiel ; la page officielle ne chiffre pas).
>
> **Chaîne recommandée, gratuite, à construire** :
> 1. **Skill Gemini `zehon-images`** : charte, préambule sans narration,
>    règles (deux bras, pas de texte, une image par scène, dans l'ordre),
>    planche du bonhomme en fichier de référence, et les prompts de la
>    vidéo. Franco l'importe une fois par compte, puis tape
>    `/zehon-images scènes 1 à 10`. **À tester** : que la génération
>    d'images marche depuis une skill, qu'elle enchaîne 10 images dans
>    l'ordre, et comment fournir les prompts d'une nouvelle vidéo
>    (réimporter la skill ou joindre le fichier dans la conversation).
> 2. **Collecte** : Google Drive pour ordinateur sur le PC Windows, et le
>    dossier de téléchargement du navigateur réglé sur
>    `Zehon/Videos/<nn>_<sujet>/a_ranger/`. Les téléchargements arrivent
>    dans Drive, quel que soit le compte Gemini ouvert dans le navigateur.
>    L'extension Chrome « Gemini Image Auto-Downloader » est déconseillée
>    (317 utilisateurs, un seul développeur, note de 3 sur 5).
> 3. **Notebook gratuit** (Colab, sur le modèle de `voix_zehon.ipynb`) :
>    lit `a_ranger/`, reconnaît la scène de chaque fichier, vérifie les
>    défauts avec un Gemini gratuit qui voit les images, renomme
>    (`scene_NNN.png`, `clips/scene_NNN.mp4`, miniatures), range, tient
>    `images/etat.json`, produit une planche de contrôle et la liste à
>    refaire avec le prompt corrigé. Il dit aussi quel lot générer ensuite.
>    **À tester d'abord sur les images du sel** (le bras en trop).
> 4. **`content-maker`** : l'étape 4 produit aussi le dossier de skill
>    Gemini et le fichier de prompts ; « l'état des pièces » lit
>    `images/etat.json`.
> 5. Plus tard, si le gratuit ne suffit pas : clé API payante avec
>    plafond (environ 4 $ d'images et 5 $ de clips Veo par vidéo, prix de
>    sites non officiels, à vérifier).

> **Reprise au 01/10/2026 : vidéo 03, l'aluminium, script écrit, en
> attente de relecture (pause 4).** Sujet choisi par Franco le 01/10
> (contre le savon et le papier), angle, hook et plan validés. Dossier
> Drive `Zehon/Videos/03_aluminium/` (`1_d4WAgXlr2IeLwFltmSWOPHVsurIhBdp`,
> avec `images/`, `clips/`, `voix/`, `miniatures/`, `rendu/`) :
> `01_recherche.md`, `02_plan.md`, `02_script.md` (1 499 mots) et
> `02_script_voix.txt` (150 lignes, 1 612 mots dits, soit 8 min au débit
> mesuré). Vérificateur : 0 erreur, 0 avertissement sur les deux.
> **Prochaine étape : Franco relit le script** ; après sa validation,
> étape 4 (scènes et prompts) puis 5 (publication), sans pause.
> - Script : faits revérifiés le 01/10 (Wikipedia *History of aluminium*,
>   PDF AluQuébec). Écarts au plan : Davy daté « début du XIXe siècle »
>   (1807 chez AluQuébec, 1808 chez Wikipedia) ; Napoléon III « montre »
>   (et non « offre ») les premiers objets à Victoria, comme dans la
>   source ; ajout de la phrase de Bugeaud (« un kilogramme de trop »,
>   AluQuébec) ; la pointe de Washington arrondie à « près de 23 cm, près
>   de 3 kg » ; le procédé Bayer décrit en une phrase (soude, boue rouge).
> - Points soumis à Franco : le mythe de Tibère était déjà dans le verre
>   (T2 y fait un clin d'œil, « tu l'as peut-être déjà entendue à propos du
>   verre ») ; la boîte aux lettres jaune « en aluminium depuis 1950 »
>   vient d'une légende de photo d'AluQuébec.
> - `Memoire/lexique.md` : 16 graphies ajoutées (Ørsted, Wöhler, Hall,
>   Héroult, Kreuzlingen, Coors…), non vérifiées à l'écoute.
> - Angle : « partout sous nos pieds (8 % de l'écorce terrestre), et
>   introuvable » ; la chute du prix arrive comme conséquence (Q3), pour ne
>   pas refaire le « trésor devenu gratuit » du sel.
> - Plan : hook, 4 questions en 10 temps, fin ; environ **1 520 mots
>   écrits** (débit de la voix mesuré sur le sel : 3,36 mots/s, soit
>   environ 1 610 mots dits pour 8 min).
> - Garde-fous du plan : le banquet de Napoléon III reste au conditionnel
>   (« on raconte ») ; le verre incassable de Tibère est un mythe à
>   démonter ; retirés faute de source : la remise de Hall, la tannerie
>   Héroult, les barrages des Alpes.
> - Demande mesurée (API, 01/10) : EN « Why was Aluminium more expensive
>   than Gold? » 5,2 M, « luxury to affordable overnight » 1,7 M ; en
>   français, seulement le procédé moderne. Zelan ne l'a pas traité.
> - `Memoire/sujets.md` est à jour (étape 3b). Le sel et le verre : contenu terminé,
>   pièces en cours chez Franco (voir les blocs plus bas).

> **Reprise au 30/09/2026, fin de session : où en est le sel.** Pour ouvrir
> une nouvelle session, coller [`PROMPT_NOUVELLE_SESSION.md`](PROMPT_NOUVELLE_SESSION.md).
>
> **Contenu : terminé** (skill `content-maker`, étapes 1 à 5), dans
> `Zehon/Videos/01_sel/` : `01_recherche.md`, `02_plan.md`, `02_script.md`
> (1 464 mots), `02_script_voix.txt` (140 lignes, 1 551 mots),
> `03_scenes.md` (80 scènes : 68 images, 8 plans animés, 4 titres ; 76
> prompts d'image et 8 d'animation), `04_publication.md` (titre
> recommandé « Comment le sel est-il devenu presque gratuit ? », 5
> miniatures M1 à M5, trio à tester M1, M2, M3). Angle : « le trésor devenu
> presque gratuit » ; la moitié « prix » (gabelle, Arc-et-Senans, train,
> Varangéville) fait 52 % du texte, parce que Zelan a déjà montré Lunca,
> les pots cassés et l'escalier de Hallstatt. **À vérifier avant
> publication** : les 8,1 g de sel par jour (Esteban), qui donnent les
> « 3 kilos par an ».
>
> **Pièces, produites par Franco** (état déclaré dans la conversation,
> **à relire dans Drive**) : planche du bonhomme validée (la version
> retouchée, sans bras en trop), à ranger dans
> `Zehon/Charte/planche_bonhomme.png` ; images : lot 1 fait (scènes 1 à 11) ;
> miniatures : les 5 générées ; plans animés : pas encore ; **voix : premier
> run du notebook `voix_zehon.ipynb` en cours le 30/09**, avec une voix de
> référence **ElevenLabs** (et non la voix de Franco) : lire
> `Videos/01_sel/voix/etat.json`.
>
> **Outils livrés le 30/09** (branche `claude/zelan-studio-analysis-rws9f6`) :
> - `content-maker` **v5** : prompts affichés dans le chat, planche du
>   bonhomme, préambule Gemini sans narration, plans animés (type `video`,
>   `anim_NNN`), miniatures en dessin animé vif, état des pièces, voix.
>   Archive à installer sur claude.ai : `zehon/content-maker.skill`
>   (Franco doit remplacer l'ancienne version).
> - `zehon/notebooks/voix_zehon.ipynb` : Qwen3-TTS en français, voix de
>   référence dans `Zehon/Charte/voix/`, cache sur Drive, `voix.wav` +
>   `mots.json` + `etat.json`. Copie dans Drive : `Zehon/voix_zehon.ipynb`
>   (`1EMpqhqNcUvWeRoHKE_gQ8k5i2YIcM0pM`), **en retard d'un commit**
>   (affichage des phrases en entier, message `pad_token_id` masqué) : la
>   remplacer une fois le run de Franco fini.
>
> **Ménage du 30/09 (demandé par Franco)** : l'ancien pipeline de la
> chaîne IA (Shorts anglais : agents `short-*`, skills Shorts, orchestrateur,
> Remotion, outils, schémas, ancien notebook de voix, ses tests et sa
> documentation) est retiré de cette branche. Il est archivé, intact, sur
> la branche `archive/pipeline-shorts-2026-09-30` (état de `main` au 16/09).
> `CLAUDE.md` ne parle plus que de Zehon ; `zehon/synchroniser_skills.py`
> régénère le miroir `.claude/skills/` et l'archive `.skill` ;
> `tests/test_zehon.py` vérifie le miroir et le vérificateur de scènes.
> **`main` n'est pas encore touché.**
>
> **Leçons du 30/09** (intégrées à la skill v5) : Gemini ajoute un bras en
> trop (deux planches sur deux) ; en mode conversation, il raconte une
> histoire et enchaîne des images non demandées ; les miniatures sombres
> et réalistes ne plaisent pas à Franco ; les scènes « titre » sans image
> font croire à un trou dans la numérotation.
>
> **Reste à faire, dans l'ordre** :
> 1. Lire `voix/etat.json` du sel : durée, débit (`debit_mots_s`, à reporter
>    dans `Memoire/lecons.md`), phrases à réécouter. Remplacer la copie
>    Drive du notebook.
> 2. **Construire `video-maker`** (rien n'existe encore) :
>    `nouveau_systeme.md` §6 et §7, en lisant `03_scenes.md` (types
>    `image`, `video`, `titre`), `images/`, `clips/`, `voix/voix.wav` et
>    `voix/mots.json` (bornes par phrase, mots horodatés).
> 3. **À trancher par Franco** : la voix de la chaîne (ElevenLabs ou son
>    propre clone ; droits commerciaux de l'offre ElevenLabs). `chaine.md`
>    et ce document disent encore « clone de la voix de Franco ».

---

# Contexte antérieur (29/09/2026, fin de session, soir)

**À lire en premier.** Le setup est terminé : vision, niche, angle, charte
et nom sont décidés. **La prochaine session construit le nouveau système**,
décrit dans [`nouveau_systeme.md`](nouveau_systeme.md) (le cahier des
charges, à lire en entier). L'ancien pipeline (agents A2 à A7, Remotion,
`new-short`) **ne sert pas** à Zehon.

Ce fichier résume et renvoie. Chaque fait porte son statut : **mesuré**
(relevé, daté) ou **hypothèse** (à tester).


> **Décision de Franco du 30/09/2026 : version « histoire simple ».** Les
> autres chaînes racontent des histoires qui éveillent la curiosité, sans
> s'attarder sur les preuves. Zehon fait de même : **plus de pièces à
> conviction, de cartels ni de statuts à l'écran**, tout en images Gemini ;
> une vraie photo seulement si elle se trouve en quelques minutes. **Un seul
> garde-fou, invisible** : les faits racontés sont justes (recherche
> légère, rien d'inventé). La ligne devient **« de la matière brute à
> l'objet »**. `content-maker` est passée en v3 en conséquence. Les
> mentions de preuves plus bas dans ce document sont **dépassées**.

> **Session du 30/09/2026 (en cours).**
> - **Essais sur compte gratuit arrêtés** (décision de Franco) : il
>   continue dans **Claude Code**, sur des comptes Pro. Constats de l'essai :
>   [`essai_compte_gratuit/LISEZMOI.md`](essai_compte_gratuit/LISEZMOI.md).
> - **`content-maker` v4, adaptée à Claude Code** : recopiée dans
>   `.claude/skills/` par `agents/_synchroniser_vers_claude_skills.py`, remplacé le 30/09 par `zehon/synchroniser_skills.py` (qui
>   couvre désormais `zehon/*/`) ; lit et écrit elle-même dans Drive ; mesure
>   les vues par l'API (`scripts/youtube.py`, avec `YOUTUBE_API_KEY`).
>   **Présente seulement sur cette branche** : ouvrir les sessions Claude
>   Code sur `claude/zelan-studio-analysis-rws9f6`.
> - **Arborescence Drive créée** (validée par Franco) : `Zehon/` avec
>   `LISEZMOI.md`, `Memoire/` amorcé (`sujets.md` avec le relevé API de Zelan
>   du 30/09, `lexique.md` avec 9 noms du sel non vérifiés, `lecons.md`),
>   `Charte/exemples/`, `Videos/01_sel/{images,voix,rendu}`. **Pas de
>   `preuves/`** (version « histoire simple »). Dossier `Zehon` :
>   `1e3_Fu2nbhyfKtvCG2k54ME_W6K-gaKWB`, `01_sel` :
>   `1Evm6KQ6gc2p_WfSsIdTpTeL3ItNE9SZ5`.
> - **Mesuré (30/09)** : le connecteur Drive lit les `.md` (téléchargement
>   brut exact) mais **ne modifie pas le contenu d'un fichier** (seulement
>   nom et dossier) : mettre à jour = nouvelle version, puis l'ancienne à la
>   corbeille. FFmpeg s'installe par `apt-get install ffmpeg` (6.1.1), mais
>   ne survit pas au conteneur : à mettre dans le script de setup.

---

## 1. Décisions de Franco (toutes du 29/09/2026)

| Sujet | Décision |
|---|---|
| **Nom** | **Zehon** (décision du 29/09, qui remplace Zoook : au moins 6 chaînes « Zoook/ZOOOK » existaient, dont une marque d'électronique « née en France »). **Mesuré le 29/09 (API YouTube)** : **@zehon est pris** (« Zehon Vaz », 135 abonnés, 23 vidéos) ; @zehonfr, @zehon.fr, @zehon_fr sont libres ; **handle retenu par Franco : @zehonfr**. Quelques petites chaînes s'appellent aussi « Zehon » ; une marque « Zehon Tools » (outillage) est vendue en ligne. Vérifier le nom sur la base des marques de l'INPI avant de créer la chaîne |
| Chaîne | Seconde chaîne, en **français**, à côté de la chaîne IA (anglais, Shorts) |
| **Ligne éditoriale** | **« De la matière brute à l'objet. »** Chaque vidéo raconte comment une matière est devenue un objet du quotidien, de la préhistoire à aujourd'hui, et montre **les preuves** (fouilles, datations, traces). La préhistoire est le premier chapitre de chaque histoire, pas la niche entière |
| Format | Vidéo longue en paysage d'environ 8 min (environ 1 480 mots), plus 1 à 2 Shorts ; 1 vidéo par semaine ; **20 h par semaine** |
| Propriété | Franco réside au **Burkina Faso** (non éligible au Programme Partenaire). **Une connaissance en France est propriétaire** (chaîne et AdSense à son nom). Franco est gestionnaire, avec un **contrat écrit** à signer avant la première vidéo (rémunération, droits sur les vidéos **et sur sa voix**, conditions de sortie) |
| **Système** | **Nouveau, simple** : des instructions dans Drive, utilisables depuis **n'importe quel compte Claude, même gratuit** (questions, recherche, script, prompts d'images) ; les images dans **Gemini** ; la voix dans Colab ; l'assemblage par une nouvelle skill **`video-maker`** (**HyperFrames**, dans **Claude Code web**). Les anciennes skills seront supprimées (point à trancher : voir `nouveau_systeme.md` §8) |
| **Style** | La grammaire du genre (Zelan, Zenn), **en calme** : bonhomme à tête ronde, décors illustrés, images générées par **Gemini**, légers mouvements de caméra, texte animé sobre. Charte validée : `nouveau_systeme.md` §2 |
| Preuves | De **vraies photos** sous licence libre pour les pièces à conviction. **Jamais** une image générée qui imite un objet de fouille ou un document réel |
| Voix | **Clone de la voix de Franco** (Qwen3-TTS, Colab). Il faut un échantillon de référence en français de 15 à 30 s, et son texte exact |
| **Première vidéo** | **Le sel** (Franco a préféré le sel au pain, recommandé) |

Règles de travail : Claude propose, Franco tranche (sujets, nom, charte) ;
des recommandations, pas des listes d'options ; le mesuré séparé de
l'hypothèse ; une question à la fois ; ne jamais éditer `.claude/skills/` ;
`git fetch` avant chaque push ; branche de travail
`claude/zelan-studio-analysis-rws9f6`.

---

## 2. La première vidéo : le sel (état au 29/09)

| Fichier | Contenu | État |
|---|---|---|
| [`pilote_sel/01_recherche.md`](pilote_sel/01_recherche.md) | 4 questions d'enquête, 30 affirmations marquées établi, probable ou hypothèse, 21 sources (Antiquity, NHM Vienne, JFA, UNESCO, USGS, Mérimée…) | **Prêt.** Pièces à conviction Commons reportées (auteurs, licences). Corrigé le 29/09 : Hallstatt n'est **pas** la plus ancienne mine de sel (Duzdağı, Ve millénaire av. J.-C.). Quelques sources lues en extrait sont à relire |
| [`pilote_sel/02_plan_script.md`](pilote_sel/02_plan_script.md) | Plan en temps : hook, 10 temps, fin | **Prêt.** Angle validé par Franco : « le trésor devenu gratuit », le mythe du salaire romain comme moment « comment on le sait », la fin sur ce qu'on fait du sel aujourd'hui. Faits non sourcés retirés le 29/09 (galères, « 3 jours », chute du prix au XIXe) |
| [`pilote_sel/03_images.md`](pilote_sel/03_images.md) | Pièces à conviction repérées sur Commons, miniature, décisions de style | Pièces **trouvées** pour Q2 (briquetage de la Seille), Q3 (escalier de Hallstatt) et Q4 (Saline royale, poêles de Salins). **À TROUVER** : Q1 (coupe de Poiana Slatinei) et la page de Pline |
| [`pilote_sel/04_mise_en_place.md`](pilote_sel/04_mise_en_place.md) | Plan pour l'ancien pipeline | **Obsolète**, gardé pour ses mesures |

**Le script définitif n'est pas validé.** Les tests de `content-maker`
ont produit des scripts du sel (1 493 à 1 513 mots, vérificateur sans
erreur), des scènes et une publication, mais ce sont des **sorties de test**,
dans `zehon/content-maker-workspace/` (non versionné). La vraie production
du sel passe par la skill, sur un compte de Franco. La comparaison des
transcriptions (succès contre raté) reste à faire (voir §4).

## 2 bis. La skill `content-maker` (construite, testée, validée le 29/09)

La skill qui fait le contenu d'une vidéo, de la recherche aux prompts
d'images : **`zehon/content-maker/`**, à installer depuis
**`zehon/content-maker.skill`**. Détail : [`nouveau_systeme.md`](nouveau_systeme.md) §10.
- 5 étapes, 4 pauses, reprise d'un compte à l'autre par les fichiers,
  mémoire dans `Memoire/` (sujets, lexique, leçons).
- **Mesuré** : 96 % des vérifications passent avec la v2 (92 % en v1),
  26 % sans la skill, sur 3 cas de test tournés dans Claude Code.
- **Pas encore essayée sur un vrai compte gratuit** : c'est la première
  chose à faire.
- Installer : *Settings > Capabilities > Code execution and file creation*,
  puis *Customize > Skills > Upload*.
- **v5 (30/09), après la première vidéo réelle (le sel)** : prompts
  affichés en entier dans le chat ; planche du bonhomme (prompt et contrôle
  des bras en trop) ; préambule Gemini « image generator » (sans narration,
  une image par message) ; 6 à 10 plans animés par vidéo (type `video`,
  prompts `anim_NNN`, contrôlés par le vérificateur) ; miniatures en dessin
  animé vif avec gros texte, mesurées sur celles de Zelan ;
  `youtube.py description` pour lire l'angle et le corps d'un concurrent.
- **Voix off (30/09)** : notebook [`../../zehon/notebooks/voix_zehon.ipynb`](../../zehon/notebooks/voix_zehon.ipynb)
  (copie dans Drive, `Zehon/voix_zehon.ipynb`). Qwen3-TTS en français,
  voix de référence rangée dans `Zehon/Charte/voix/`, cache sur Drive pour
  reprendre après une coupure, `voix.wav` + `mots.json` + `etat.json` ;
  la skill lit `etat.json` pour dire si l'audio est prêt. **Pas encore
  lancé sur un vrai GPU** : le premier run sur le sel le validera.

**Mesuré le 29/09, à ne pas oublier** :
- La vidéo *sel* de Zelan (25/09) a pris le paradoxe « personne ne salait
  avant l'agriculture ». **Notre hook a été déplacé** sur « le trésor
  devenu gratuit » (gabelle contre saleuse).
- **Depuis le 11/09, Zelan cite ses sources en description** (11 vidéos sur
  12). Notre différence doit se voir **à l'écran** (pièces, statuts) et
  s'entendre **à l'oral** (moments « comment on le sait »).
- Zelan publie tous les 2 jours et vient d'attaquer les métaux (*le
  cuivre*, 29/09). **Avant chaque script, vérifier qu'il n'a pas déjà pris
  le même paradoxe.**
- Zenn s'effondre aussi : 8,0 M et 4,9 M vues en avril, 13 à 37 k depuis
  juillet (une exception à 311 k).

---

## 3. Le modèle de narration mesuré (*le fer* de Zelan, 435 k vues)

Transcription segmentée le 29/09 (dans [`corpus_structures.jsonl`](corpus_structures.jsonl)) :
- 500 s, 1 547 mots, **3,09 mots/s** ; phrase médiane de 12 mots (quartiles
  8 et 17) ;
- un **hook de 30 s** (8 phrases) sur un objet que tu as sous la main et un
  paradoxe ; la question tombe à la 9e phrase ;
- **10 temps de 55 à 255 mots** (123 en moyenne), en fil chronologique.
  Chaque temps finit sur un obstacle, que le suivant lève. Mot charnière :
  **« Sauf que »** ;
- le **tutoiement**, et 5 à 6 **retours au présent** ;
- **pas d'appel à s'abonner** ; la fin est une question ouverte.

**Notre structure** (recommandation) : environ 1 480 mots, 3 à 4 questions
d'enquête en 8 à 10 temps, chacune refermée sur une pièce à conviction
montrée, et des marqueurs d'incertitude à l'oral.

**Pas encore mesuré** : le même schéma sur d'autres vidéos (un succès
contre un raté), la narration de Zenn et le ton précis (humour ou gravité).

---

## 4. Transcriptions : bloquées depuis le conteneur

**Mesuré le 29/09** : YouTube renvoie `RequestBlocked` / `IpBlocked`
(adresse IP d'un fournisseur cloud) à yt-dlp comme à
`youtube-transcript-api`. Le blocage ne se lève pas en attendant.
**Recommandation** : obtenir les transcriptions par **Gemini** (à partir du
lien YouTube), les déposer dans Drive, puis les comparer dans une session
Claude.

À récupérer : *la journée* (u7gam_aBU4s, 277 k), *l'eau sale* (ZBJ0fXTN4EA,
127 k), *le sucre* (pvx89-uxxBI, 3,6 k, le raté), *le sel* de Zelan
(xu93x_VqNvM), *le sel rose* de Je T'explique Comment (nXkk_rp91k0, 145 k,
le modèle « procédé »), et Zenn (*What Did Ancient Humans Do at Night?*,
st_Ah6Ykbh4, 8,0 M ; *What Did Ancient Humans Actually Eat?*, d8lMW1uDN4s,
882 k).

L'API YouTube Data (statistiques, descriptions) fonctionne toujours
(`YOUTUBE_API_KEY`). La recherche d'images sur Commons fonctionne aussi,
mais limitée (429 en rafale : espacer les requêtes).

---

## 5. Sujets candidats (Franco tranche)

Classés par preuve de demande (mesuré le 29/09) : **le pain** (EN 333 k,
Shubayqa 1, pain d'environ 14 400 ans ; terrain FR occupé par Miettes
d'Histoire, 72 k), **le verre** (FR 154 k), le fer (déjà fait par Zelan), le
sucre, puis le ciment, le crayon et les pièces de monnaie (à vérifier : une
histoire « depuis la préhistoire » solide). **Zelan avance sur les
matières** : vérifier avant chaque choix.

À tester après 3 vidéos : le format « Chaque X expliqué » (*Chaque métal
expliqué*).

---

## 6. Questions ouvertes

1. **La suppression des anciennes skills** : la chaîne IA en dépend.
   Recommandation : ne rien supprimer avant la première vidéo de Zehon.
   Le plugin tiers *AI YouTube OS* (channelroom-studio) a été lu le 29/09 :
   sûr, mais ne remplace rien ; trois idées reprises (voir
   `nouveau_systeme.md` §10).
2. **Le budget mensuel** : environ 35 $ si les images sont payées ; près de
   0 si les quotas gratuits de Gemini suffisent (hypothèse).
3. Le texte de la miniature du sel (proposition : *UN TRÉSOR*).
4. Les pièces à conviction du sel **À TROUVER** : la coupe de Poiana
   Slatinei (autorisation d'O. Weller, CNRS, ou schéma redessiné avec la
   citation) et une page de Pline, *HN* 31.89 (édition ancienne).
5. Le nom **Zehon** sur la base des marques de l'INPI.
6. L'objectif à 6 mois.

---

## 7. Les documents

| Fichier | Contenu |
|---|---|
| [`nouveau_systeme.md`](nouveau_systeme.md) | **Le cahier des charges du nouveau système** : fondations, charte, déroulé, arborescence Drive, règles du script, format des scènes, `video-maker`, vérifications |
| [`pilote_sel/`](pilote_sel/) | La première vidéo : recherche, plan, images |
| [`../../zehon/content-maker/`](../../zehon/content-maker/) | La skill `content-maker` (sources) ; `../../zehon/content-maker.skill` à installer |
| [`../lancement_chaine_2_prehistoire.md`](../lancement_chaine_2_prehistoire.md) | Document de cadrage complet et journal de la phase de cadrage |
| [`niches_2026-09-29.md`](niches_2026-09-29.md) | 16 niches comparées ; pourquoi la transformation |
| [`concurrents_2026-09-29.md`](concurrents_2026-09-29.md) | Le genre en FR et EN, saturation, qui Zelan imite |
| [`revenus_2026-09-29.md`](revenus_2026-09-29.md) | Revenus estimés du genre, risque « contenu inauthentique » |
| [`zelan_releve_2026-09-29.csv`](zelan_releve_2026-09-29.csv) | Les 25 vidéos de Zelan (API) |
| [`corpus_structures.jsonl`](corpus_structures.jsonl) | Segmentations de vidéos (une ligne : *le fer*) |
| [`outils_releve/`](outils_releve/) | Scripts ponctuels de relevé (API YouTube, yt-dlp) |
| [`PROMPT_NOUVELLE_SESSION.md`](PROMPT_NOUVELLE_SESSION.md) | Le message à coller pour ouvrir la prochaine session |

Environnement du conteneur au 29/09 : Node 22.22 et Chromium présents,
**FFmpeg absent** ; connecteur Google Drive branché ; `YOUTUBE_API_KEY`
définie ; **`GEMINI_API_KEY` absente** (inutile tant que les images se
génèrent à la main dans Gemini).
