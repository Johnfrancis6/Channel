# Lancement de la chaîne n° 2 — préhistoire et histoire du quotidien

Document de cadrage, ouvert le 29/09/2026. Rien n'est encore produit.

**Décisions de Franco (29/09/2026)** :
- **seconde chaîne** : la chaîne IA continue, la nouvelle a sa propre racine
  et partage le pipeline et `composants/` ;
- **en français** ;
- **niche** : préhistoire (« comment faisaient nos ancêtres… ? ») **et**
  histoire des objets du quotidien (« qui a inventé… ? »).

Modèle de format observé : Zelan (@ZelanStudio). Voir la section 1.

---

## 1. Le modèle observé : Zelan

Relevé le 29/09/2026 sur deux captures d'écran. C'est un échantillon de
4 vidéos, pas une mesure.

- 4,37 k abonnés, 24 vidéos, en français, sans visage, dessins au trait,
  environ 10 min par vidéo (« Le premier sel ? » dure 9:22).
- Rythme annoncé : « une nouvelle vidéo tous les deux jours » sur la
  bannière, mais « chaque semaine » dans la description.
- *Comment nos ancêtres dormaient-ils avec autant de moustiques ?* :
  **8,4 k vues en 24 h**, près de deux fois le nombre d'abonnés. L'algorithme
  la montre donc bien au-delà des abonnés.
- *Comment les humains ont-ils découvert le sel ?* : 5,8 k vues en 3 jours.

Ce qui porte le format :
1. **Une seule formule de titre** : « Comment [nos ancêtres] … ? ». On part
   d'un geste banal d'aujourd'hui et on le transpose à la préhistoire.
2. **Des miniatures à grammaire fixe** : 2 ou 3 mots énormes (blanc et jaune,
   contour noir), un « ? », un personnage aux yeux écarquillés, un ciel bleu
   saturé.
3. **Une mascotte récurrente** sur l'avatar, la bannière et les miniatures.
   Elle remplace le présentateur.
4. **Des vidéos plus simples que leurs miniatures.** L'image de la vidéo sur
   les moustiques est un bonhomme à tête ronde sur un décor plat. La richesse
   visuelle est concentrée dans la miniature, là où se joue le clic.

Zelan devient un **concurrent direct** de cette chaîne. Il va dans le
`00_Profil/chaines_concurrentes.json` de la **nouvelle** racine, pas dans
celle de la chaîne IA, pour ne pas fausser ses médianes.

---

## 2. Positionnement : ne pas être un clone

La niche n'est pas protégée, le style l'est de fait : une chaîne qui copie
la mascotte et les miniatures de Zelan passerait pour une copie, auprès du
public comme de l'algorithme.

**Angle proposé : « l'enquête ».** Chaque vidéo répond à la question, puis
montre **comment on le sait** : fossiles, traces d'usure, ADN, expérimentation
archéologique. C'est l'ADN de la chaîne IA (« on décode, on teste »)
transposé à l'histoire. Zelan ne le fait pas, et c'est aussi le meilleur
garde-fou contre les idées reçues (voir la section 5).

**Deuxième différence : la ligne du temps va jusqu'à aujourd'hui.** Le
pilier « qui a inventé… ? » part de la préhistoire et arrive à l'objet qu'on
a dans la main. Zelan s'arrête avant.

**Mascotte** : une silhouette, une couleur et un accessoire distincts de
ceux de Zelan (pas d'enfant en parka à capuche fourrée, pas d'homme
préhistorique à tête ronde blanche comme personnage principal). À dessiner
en séance de charte, pas ici.

**Nom** : à trouver. Pistes à vérifier (disponibilité du handle non
vérifiée) : *Avant Nous*, *Comment On Faisait*, *L'Enquête des Ancêtres*.

---

## 3. Piliers

À sortir dans `profil_chaine.json` (section 6). Quatre plutôt que cinq pour
commencer :

| id | Pilier | Formule de titre |
|---|---|---|
| `quotidien` | Comment faisaient nos ancêtres ? | « Comment nos ancêtres [geste banal] ? » |
| `invention` | Qui a inventé… ? | « Qui a inventé [objet] ? » / « Comment a-t-on inventé [objet] ? » |
| `autres_humains` | Espèces disparues, autres humains | « Pourquoi [espèce] a-t-elle disparu ? » |
| `enquete` | Une énigme, un site, une découverte | « Comment sait-on que [fait surprenant] ? » |

### Backlog de départ (à valider par Franco, §2 de l'architecture)

`quotidien` :
- Comment nos ancêtres se soignaient-ils une rage de dents ?
- Comment faisait-on du feu sous la pluie ?
- Comment se lavait-on il y a 20 000 ans ?
- Comment comptait-on sans les chiffres ?
- Comment se repérait-on sans carte ?
- Que faisait-on de ses morts ?

`invention` :
- Qui a inventé le pain ?
- Qui a inventé la chaussure ?
- Qui a inventé la clé ?
- Qui a inventé le lit ?
- Comment a-t-on inventé le calendrier ?
- Qui a inventé la brosse à dents ?

`autres_humains` :
- Néandertal savait-il parler ?
- Qui étaient les Dénisoviens ?
- Pourquoi les mammouths ont-ils disparu ?

`enquete` :
- Comment sait-on ce que mangeait Ötzi ?
- Comment date-t-on un os ?
- Qui a peint Lascaux, et pourquoi dans le noir ?

---

## 4. Format

- **Vidéo longue en paysage** (`format_video: "long"`), 8 à 10 min : c'est la
  durée de Zelan.
- **1 à 2 Shorts par vidéo longue**, tirés du même script. Ce sont des
  produits d'appel vers la vidéo longue, pas une ligne éditoriale séparée.
- **Rythme de départ : 1 vidéo longue par semaine.** Zelan annonce une tous
  les deux jours, mais le pipeline n'a encore produit **aucune** vidéo
  longue (§12). On accélère une fois le coût réel mesuré.

**Un conflit à trancher sur la vidéo pilote.** Avec la règle actuelle
(`idées_max = 3`, 300 mots par idée en long, 2,8 mots/s), une vidéo longue
fait 900 mots, soit **environ 5 min 20**. Pour atteindre 9 ou 10 min, il
faut soit 5 idées, soit environ 550 mots par idée. Les deux se défendent :
la seconde garde la règle des 3 idées et donne plus de place à
« l'enquête ». À décider sur un script réel, pas dans l'abstrait.

---

## 5. Exactitude : le vrai risque de la niche

La préhistoire est pleine d'idées reçues (« les hommes préhistoriques
vivaient dans des grottes », « on mourait à 30 ans »). Une chaîne qui les
répète se fait corriger en commentaires, et à raison.

Règle pour A2 (Chercheur) : chaque affirmation du dossier de recherche est
marquée **établi**, **probable** ou **hypothèse**, avec sa source
(publication, musée, fouille). A4 (Rédacteur) traduit ces marques à l'oral
(« on sait que… », « on pense que… », « personne ne sait vraiment… »). C'est
aussi la matière de l'angle « enquête » : la preuve devient le contenu.

---

## 6. Ce que ça demande au pipeline

Rassemble le chantier multi-chaînes du §12 et ce que le français et le
style ajoutent.

| # | Chantier | Où | Nature |
|---|---|---|---|
| 1 | Sortir les piliers dans un `profil_chaine.json` (piliers, langue, format par défaut) | `skills/new-short/scripts/new_short.py` (`PILIERS`), `schemas/state_schema.json` (enum `pilier`), profil par défaut | code, déjà identifié au §12 |
| 2 | Seconde racine Drive + argument `--chaine` pour les skills | détection de la racine, skills | code, déjà identifié au §12 |
| 3 | **Voix en français** : la langue est écrite en dur (`language="English"` à deux endroits, `language="en"` pour les horodatages mot à mot de Whisper, dont dépendent les sous-titres) | `notebooks/voix_off.ipynb` | code + un **échantillon de voix de référence en français** à fournir |
| 4 | Recalibrer le débit (2,8 mots/s mesuré en anglais) et les seuils de phrase du §7.3 (8 à 18 mots) | `outils/formats_video.py`, `agents/short-filtre-tts/scripts/metriques.py` | à mesurer sur le premier enregistrement français |
| 5 | Le Rédacteur suppose une chaîne en anglais | `agents/short-redacteur/SKILL.md` (l. 88) | lire la langue dans le profil |
| 6 | Charte visuelle propre à la chaîne : mascotte, palette, décors | `00_Profil/charte_visuelle/` de la nouvelle racine | séance de design |
| 7 | Mascotte et décors préhistoriques en Remotion, en partant de `Stickman` / `StickmanTalk` | `composants/` | code. Les composants sont encore pensés pour le vertical (§12), coût déjà connu |
| 8 | Miniatures | hors pipeline | Franco, ou génération d'image. C'est là que doit aller l'effort visuel (voir la section 1, point 4) |

**Le choix visuel recommandé : tout en Remotion, décors simples.**
C'est cohérent avec la décision du 11/09 (tout codé, pas de fichiers
pré-rendus), c'est automatisable, et le modèle observé montre que la vidéo
peut rester simple si la miniature est riche. Générer les images de chaque
scène par IA serait plus riche, mais ajouterait une dépendance et le
problème de garder la mascotte identique d'une image à l'autre.

---

## 7. Ordre recommandé

Le §12 veut qu'une chaîne tourne une semaine avant qu'on généralise le
pipeline. On le respecte pour le **code**, pas pour l'éditorial :

1. **Tout de suite, sans toucher au code** : nom, mascotte et charte ;
   validation du backlog ; création de la racine Drive ; ajout de Zelan et
   de 2 ou 3 autres chaînes du genre à ses `chaines_concurrentes.json` ;
   récupération de transcriptions de Zelan pour le corpus de structures.
2. **Une vidéo pilote**, produite avec `--root` explicite et les réglages
   écrits en dur ajustés à la main : elle mesure le débit en français, la
   durée par idée et le coût réel d'une vidéo longue.
3. **Ensuite seulement**, chantiers 1 et 2 (profil de chaîne, `--chaine`),
   avec deux chaînes réelles comme exemples au lieu d'une.
4. Critères pour juger les 10 premières vidéos : vues à 24 h rapportées aux
   abonnés (le signal relevé chez Zelan), taux de clic des miniatures,
   rétention à 30 s.
