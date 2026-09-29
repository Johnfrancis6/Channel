# Zehon (chaîne 2) — contexte de reprise (état au 29/09/2026, fin de session)

**À lire en premier.** Le setup est terminé : vision, niche, angle, charte
et nom sont décidés. **La prochaine session construit le nouveau système**,
décrit dans [`nouveau_systeme.md`](nouveau_systeme.md) (le cahier des
charges, à lire en entier). L'ancien pipeline (agents A2 à A7, Remotion,
`new-short`) **ne sert pas** à Zehon.

Ce fichier résume et renvoie. Chaque fait porte son statut : **mesuré**
(relevé, daté) ou **hypothèse** (à tester).

---

## 1. Décisions de Franco (toutes du 29/09/2026)

| Sujet | Décision |
|---|---|
| **Nom** | **Zehon** (décision du 29/09, qui remplace Zoook : au moins 6 chaînes « Zoook/ZOOOK » existaient, dont une marque d'électronique « née en France »). **Mesuré le 29/09 (API YouTube)** : **@zehon est pris** (« Zehon Vaz », 135 abonnés, 23 vidéos) ; @zehonfr, @zehon.fr, @zehon_fr sont libres ; **handle retenu par Franco : @zehonfr**. Quelques petites chaînes s'appellent aussi « Zehon » ; une marque « Zehon Tools » (outillage) est vendue en ligne. Vérifier le nom sur la base des marques de l'INPI avant de créer la chaîne |
| Chaîne | Seconde chaîne, en **français**, à côté de la chaîne IA (anglais, Shorts) |
| **Ligne éditoriale** | **« De la matière brute à l'objet, et comment on le sait. »** Chaque vidéo raconte comment une matière est devenue un objet du quotidien, de la préhistoire à aujourd'hui, et montre **les preuves** (fouilles, datations, traces). La préhistoire est le premier chapitre de chaque histoire, pas la niche entière |
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
| [`pilote_sel/01_recherche.md`](pilote_sel/01_recherche.md) | 4 questions d'enquête, 29 affirmations marquées établi, probable ou hypothèse, 20 sources (Antiquity, NHM Vienne, UNESCO, USGS, Mérimée…) | **Prêt.** Quelques sources, lues seulement via un extrait (Inrap, Cloudflare), sont à relire |
| [`pilote_sel/02_plan_script.md`](pilote_sel/02_plan_script.md) | Plan en temps : hook, 10 temps, fin | **Prêt.** Angle validé par Franco : « le trésor devenu gratuit », le mythe du salaire romain comme moment « comment on le sait », la fin sur ce qu'on fait du sel aujourd'hui |
| [`pilote_sel/03_images.md`](pilote_sel/03_images.md) | Pièces à conviction repérées sur Commons, miniature, décisions de style | Pièces **trouvées** pour Q2 (briquetage de la Seille), Q3 (escalier de Hallstatt) et Q4 (Saline royale, poêles de Salins). **Q1 (Poiana Slatinei) : aucune photo libre** |
| [`pilote_sel/04_mise_en_place.md`](pilote_sel/04_mise_en_place.md) | Plan pour l'ancien pipeline | **Obsolète**, gardé pour ses mesures |

**Le texte du script n'est pas écrit.** Franco voulait d'abord la
comparaison des transcriptions (succès contre raté), et YouTube les bloque
depuis le conteneur (voir §4).

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
2. **Le budget mensuel** : environ 35 $ si les images sont payées ; près de
   0 si les quotas gratuits de Gemini suffisent (hypothèse).
3. Le texte de la miniature du sel (proposition : *UN TRÉSOR*).
4. La pièce à conviction de Q1 (Poiana Slatinei) : demander à O. Weller
   (CNRS) l'autorisation pour une figure, ou redessiner la coupe avec la
   citation.
5. L'objectif à 6 mois.

---

## 7. Les documents

| Fichier | Contenu |
|---|---|
| [`nouveau_systeme.md`](nouveau_systeme.md) | **Le cahier des charges du nouveau système** : fondations, charte, déroulé, arborescence Drive, règles du script, format des scènes, `video-maker`, vérifications |
| [`pilote_sel/`](pilote_sel/) | La première vidéo : recherche, plan, images |
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
