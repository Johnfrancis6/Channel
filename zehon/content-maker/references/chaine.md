# Zehon — la chaîne

Chaîne YouTube **Zehon** (handle **@zehonfr**), en français.

## La ligne

**« De la matière brute à l'objet. »**

Chaque vidéo raconte comment **une matière** (minerai, sable, grain,
graisse, fibre, sel…) est devenue **un objet du quotidien**, de la
préhistoire à aujourd'hui. C'est **une histoire qui éveille la curiosité**,
pas un exposé : le spectateur doit vouloir savoir la suite.

**Ce qui intéresse le public, c'est le procédé, pas la biographie** : les
chaînes qui racontent les inventeurs plafonnent (médiane 1,4 k vues,
mesuré le 29/09/2026), celles qui montrent « comment c'est fait » dépassent
régulièrement 100 k. Zelan a fait 435 k avec *le fer* (un procédé) et 3,6 k
avec *le sucre* (une « découverte »).

## Le format

- Vidéo longue, **paysage 16:9, environ 8 min, environ 1 480 mots**.
- 1 vidéo par semaine. Pas de Shorts pour l'instant.
- Langue : **français**, **tutoiement**.
- Voix (décision de Franco du 30/09/2026) : **une voix d'homme au ton
  narratif, créée sur ElevenLabs**, dont un échantillon (`Zehon/Charte/voix/`)
  sert de référence au clonage par Qwen3-TTS dans Colab. Ce n'est pas la voix
  de Franco. D'où la version voix du script (étape 3).

## Le ton

Des histoires **racontées calmement**. Pas d'agitation, pas de
superlatifs criés, pas de « vous n'allez pas y croire ». Le suspense vient
de la structure (chaque temps finit sur un obstacle), pas du ton. On parle
à quelqu'un de curieux, pas à un spécialiste.

**Jamais d'appel à s'abonner ni à liker.** La vidéo finit sur une question
ouverte, rattachée au présent.

## La charte visuelle (validée le 29/09/2026)

- **Personnage** : un bonhomme blanc à tête ronde (le style du genre),
  toujours généré à partir de **la même planche de référence** dans Gemini
  (`Charte/planche_bonhomme.png`, validée le 30/09 : tête ronde lisse,
  yeux en petits ovales, pas de nez, tunique sable à manches courtes et
  cordon, pantalon marron, bras blancs visibles). Il change d'habit selon
  l'époque de la scène, jamais de tête. **Deux bras, pas un de plus** :
  c'est le défaut le plus fréquent de Gemini.
- **Décors** : illustrés, lumière chaude ; la palette vient de la matière du
  sujet (sel : blancs, gris de saumure, ocre de terre cuite ; fer : rouille
  et charbon ; verre : vert d'eau et sable).
- **Toutes les images viennent de Gemini.** Une vraie photo (musée, site)
  est un bonus, **seulement si elle se trouve en quelques minutes** sous
  licence libre ; sinon, une bonne mise en scène suffit.
- **Caméra** : zoom lent de 3 à 5 % sur chaque image, parfois un
  panoramique lent ; fondus de 0,5 à 1 s ; pas de coupe sèche.
- **Plans animés** : 6 à 10 par vidéo, de courts clips générés dans
  Gemini à partir de l'image de la scène, avec un mouvement léger (feu,
  vapeur, eau, véhicule), caméra fixe. Ils cassent la monotonie sans
  changer le style (demandé par Franco le 30/09).
- **Rythme** : une image toutes les 6 à 8 s (60 à 80 images pour 8 min).
- **Texte animé** : seulement les mots-clés, les dates, les chiffres ;
  blanc cassé, ombre douce. **Jamais de texte dans les images des
  scènes** : c'est `video-maker` qui l'anime.
- **Miniature** : **plus vive que la vidéo**. Dessin animé à gros contours
  noirs, couleurs saturées, ciel bleu, émotion exagérée du bonhomme, et un
  gros texte de 2 à 4 mots en capitales blanches ou jaunes cernées de
  noir, demandé directement à Gemini (seule exception au « pas de
  texte »). Jamais sombre ni réaliste : mesuré sur les miniatures de
  Zelan le 30/09, voir `etape5_publication.md`.

## Des faits justes (le seul garde-fou)

On ne montre pas de preuves, mais **ce qu'on raconte est vrai** : pas de
date, de chiffre ou d'anecdote inventés. La recherche est légère (quelques
sources fiables), et elle reste invisible à l'écran. Quand personne ne sait
vraiment, on le dit simplement (« personne ne sait exactement comment… »)
: ça entretient le mystère au lieu de l'abîmer. Un mythe célèbre (« les
soldats romains payés en sel ») peut être raconté **pour être démonté** :
c'est un bon rebondissement.

Pourquoi : une erreur flagrante attire les corrections en commentaire, et
la chaîne est au nom de sa propriétaire.

## Les concurrents (relevé du 29/09/2026)

- **Zelan** (FR) : même genre, publie tous les 2 jours, a traité le fer,
  le sel, le sucre, le cuivre. **Avant chaque sujet et chaque hook,
  vérifie qu'il n'a pas déjà pris le même paradoxe** : c'est arrivé pour le
  sel. Un sujet traité par Zelan **reste possible** avec un autre
  paradoxe : le sel est justement la première vidéo de Zehon (paradoxe
  « le trésor devenu gratuit », pas celui de Zelan).
- **Je T'explique Comment** (FR, « Comment c'est fait ») : procédés
  industriels modernes, sans la préhistoire.
- **Zenn** (EN) : a culminé à 8 M vues en avril 2026, retombé à 13-37 k
  depuis juillet. Copier le genre à l'identique ne suffit pas : ce qui
  compte, c'est le sujet et la qualité du récit.
