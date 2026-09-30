# Zehon (chaîne 2) — contexte de reprise (état au 30/09/2026, nuit)

> **Reprise au 30/09/2026, nuit : la vidéo du sel est VALIDÉE par Franco
> (`rendu/video.mp4`, sans musique, décision du 30/09). Reste la
> publication.** La musique (nappe, `--musique`) reste prête pour les
> vidéos suivantes.
>
> **Rendu complet du sel (Colab, 30/09, rapport lu par Claude)** : commit
> `ac28c5c`, sous-titres incrustés, **sans musique** ; 475,3 s (7 min 55 s)
> pour 475,3 attendues, 1920×1080, 1 piste audio, volume moyen −18,6 dB,
> crête −4,1 dB ; avertissements : scènes 32 et 80 (plus de 10 s), laissées
> telles quelles. `video.mp4` : 287 Mo. **Rendu en 2 536 s (42 min)** : mon
> estimation de 20 à 30 min était fausse ; notebook corrigé (« 45 min
> environ », essai de 10 scènes environ 5 min), copie Drive remplacée :
> `Zehon/montage_zehon.ipynb` (`1GHx1JhAHliRl3izhg2NrrREuiQ3eEYhC`).
> **Pas vu par Claude** : la vidéo complète dépasse la limite de 10 Mo du
> connecteur (les images ont été vérifiées sur l'extrait 5 à 9, même code).
> Branche de travail : `claude/zelan-studio-analysis-rws9f6`.
>
> **Fait dans la session de montage (30/09, nuit)** :
> - **Plan du sel** (mesuré) : 80 scènes, **7 min 55 s** (4 titres de 3 s),
>   toutes les scènes retrouvées à 80 % ou plus dans la voix ; 8 plans animés
>   sur 8 dans Drive ; scènes 32 (10,7 s) et 80 (10,8 s, dont 1,5 s de fin)
>   signalées, **laissées telles quelles** (recommandation).
> - **Sous-titres** (style **validé par Franco**) : `monter.py --sous-titres`
>   incruste quelques mots à la fois (34 caractères, 7 mots au plus) dans un
>   bandeau sombre transparent en bas au centre, le mot dit en jaune doré ;
>   texte du script (« 8 000 »), groupes équilibrés, rien pendant les titres,
>   texte animé remonté de 120 px. Le `.srt` YouTube (`rendu/sous_titres.srt`,
>   2 lignes de 42 caractères) s'écrit dès `--plan` : **164 sous-titres,
>   1 461 mots, 97 % calés directement sur la voix**. Extrait 5 à 9 avec et
>   sans, envoyé à Franco ; rendu 27 s en 45 s sur 4 cœurs.
> - **Notebook `zehon/notebooks/montage_zehon.ipynb`**, copie dans Drive :
>   `Zehon/montage_zehon.ipynb` (remplacée depuis, voir plus haut). Sans
>   GPU. **Une seule source** : il clone le dépôt (public) sur `BRANCHE` à
>   chaque lancement. Plan, rendu sur le disque de Colab, copie de
>   `video.mp4` et `rapport.json` dans `rendu/` (le rapport garde branche,
>   commit, `rendu_s`). Sous-titres cochés par défaut ; `EXTRAIT` pour un
>   essai. **Validé ici de bout en bout** sur un faux Drive (clone GitHub
>   compris), puis lancé par Franco dans Colab (voir plus haut).
> - **Musique** : `--musique` / `--volume-musique` (défaut −26 dB, −6 dB de
>   plus sous la voix), nappe bouclée en fondu de 3 s, entrée 2 s, sortie
>   3 s. **Mesuré** : avec une nappe à −14 LUFS, elle finit **23 dB sous la
>   voix**. Nappe à ranger dans `Zehon/Charte/musique/` ; **pas encore
>   choisie** (critères donnés à Franco : bibliothèque audio YouTube,
>   attribution non requise, ambient calme, sans batterie ni voix).
> - Conteneur : `apt-get install ffmpeg` échoue sans `apt-get update` avant.
>
> **Reste à faire, dans l'ordre** : (1) vérifier les 8,1 g de sel par jour
> et l'usage commercial de la voix ElevenLabs ; (2) publier
> (`04_publication.md`, et `rendu/sous_titres.srt` dans YouTube Studio).

---

# État précédent (30/09/2026, soir)

> **Reprise au 30/09/2026, soir : le sel est prêt à monter.**
> Pour ouvrir une nouvelle session, coller [`PROMPT_NOUVELLE_SESSION.md`](PROMPT_NOUVELLE_SESSION.md).
> Branche de travail : `claude/zelan-studio-analysis-rws9f6` (en avance sur `main`).
>
> **Contenu : terminé** dans `Zehon/Videos/01_sel/` (`01_recherche.md` à
> `04_publication.md`, 80 scènes). **À vérifier avant publication** : les
> 8,1 g de sel par jour (Esteban), qui donnent les « 3 kilos par an ».
>
> **Pièces (relevées dans Drive le 30/09 au soir)** :
> - planche : `Charte/planche_bonhomme.jpg` ;
> - images : **76 sur 76**, en `.jpg` (`scene_061` déposée par Franco à
>   19:57, vérifiée : conforme). **Revue des 76 images** (le 30/09 au soir) :
>   **4 portent du texte en anglais**, à refaire : 046 (« SALT » sur les
>   sacs), 054 (« SALINAS 17XX » gravé sur la pierre), 062 (étiquettes
>   « Topsoil… Rock Salt Layer »), 075 (« MINING ENTRANCE », « ROCK SALT »).
>   Mineur : 040 (« OED », « DICTIONARY » sur des dos de livres). Prompts
>   renforcés donnés à Franco dans la conversation ; règle ajoutée à
>   `content-maker` (`etape4_scenes.md`) ;
> - plans animés : **8 sur 8**, nommés `clips/anim_NNN.mp4` (1280×720,
>   24 i/s, 8 s, avec du son, coupé au montage) ;
> - voix : **prête** (`voix/etat.json`) : 461,8 s, 1 551 mots, **3,36 mots/s
>   pauses comprises** (3,69 en parole seule), voix de référence
>   ElevenLabs de 7,4 s, synthèse en 22 min sur T4. Reporté dans
>   `Memoire/lecons.md` : **environ 1 610 mots pour 8 min**. Les 19 phrases
>   « à réécouter » étaient des **fausses alertes** (Whisper écrit « 1344 »,
>   le script « mille trois cent… ») : corrigé dans le notebook (nombres
>   remis en lettres avant la comparaison ; 0 alerte sur 140 en rejouant le
>   sel). Copie Drive du notebook **remplacée** : `Zehon/voix_zehon.ipynb`
>   (`1nkFeUZJc82xrLKuejmMb57uUxhSBrUGk`) ;
> - miniatures : Franco s'en occupe (pas de vérification demandée).
>
> **`video-maker` construite (30/09)** : `zehon/video-maker/`
> (`scripts/monter.py`, `scripts/voix_depuis_cache.py`, polices OFL Nunito
> et IBM Plex Mono), archive `zehon/video-maker.skill`, tests
> `tests/test_video_maker.py`. **Choix, et pourquoi** : Python (OpenCV,
> Pillow) + FFmpeg plutôt que HyperFrames : pas de Chromium à faire tourner
> 14 400 fois, le même script tourne dans Claude Code et dans Colab, et il
> est testable. **Mesuré** :
> - le plan du sel : 80 scènes calées sur `mots.json` en 0,3 s, chacune
>   retrouvée à 80 % ou plus ; **7 min 55 s** avec les 4 titres (3 s
>   chacun) ; scènes 32 et 80 signalées (plus de 10 s) ;
> - **premier rendu court** : scènes 1 à 10, 48 s en 1080p, rendu en 83 s
>   sur 4 cœurs, contrôle avant publication passé, envoyé à Franco dans la
>   conversation ; son à −15,2 LUFS après normalisation (la voix brute
>   sortait à **−22 LUFS** : trop bas pour YouTube) ;
> - le connecteur Drive **télécharge au plus 10 Mo par fichier** (refus sur
>   `voix.wav`, 22 Mo) et n'envoie pas de gros fichier : la voix d'un
>   extrait se reconstitue depuis `voix/cache/`, et **la vidéo entière se
>   rendra dans Colab** (Drive monté, `rendu/video.mp4` écrit sur place).
>
> **Décisions de Franco du 30/09 au soir** :
> - **Les images restent telles quelles** (040, 046, 054, 062 et 075
>   comprises) : on monte avec. La règle « surfaces vierges » vaudra pour
>   les prochaines vidéos.
> - **La voix de la chaîne** : une **voix d'homme au ton narratif, créée sur
>   ElevenLabs**, clonée par Qwen3-TTS (c'est celle du sel). Charte mise à
>   jour (`content-maker/references/chaine.md`, `nouveau_systeme.md`).
>   **À vérifier** (hypothèse, pas lu) : que l'offre ElevenLabs utilisée
>   autorise l'usage commercial de cette voix sur une chaîne monétisée.
> - **Sous-titres animés** : à prévoir au montage, pour mieux suivre la
>   narration (les mots horodatés de `mots.json` le permettent).
>
> **Reste à faire, dans l'ordre** (effort estimé, **hypothèse**) :
> 1. **Le montage** (prochaine session, message dans
>    [`PROMPT_NOUVELLE_SESSION.md`](PROMPT_NOUVELLE_SESSION.md)) : le notebook
>    Colab `montage_zehon.ipynb` qui emballe `monter.py` (environ 2 h), les
>    sous-titres animés en option (environ 2 à 3 h), la musique (nappe, déjà
>    codée, à choisir), puis le rendu complet du sel par Franco dans Colab.
> 2. Relire la vidéo entière, puis publier (`04_publication.md`).

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
| Voix | ~~Clone de la voix de Franco~~ → **décision du 30/09 : voix d'homme au ton narratif créée sur ElevenLabs**, clonée par Qwen3-TTS (Colab) à partir d'un échantillon de 7,4 s rangé dans `Charte/voix/` |
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
