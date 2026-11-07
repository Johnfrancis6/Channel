# Sujets anglais repris par les chaînes françaises (01/10/2026)

Suite de [`concurrents_2026-09-29.md`](concurrents_2026-09-29.md) : on y avait
vu que Zelan prend ses sujets chez Ink Explainer. Ici, la question est
élargie à tout le genre : **quels sujets anglais les chaînes françaises
reprennent, avec quel délai, et avec quels résultats.**

**Méthode.** API YouTube Data v3, relevé du 01/10/2026
(`outils_releve/yt.py`) : 13 chaînes anglaises et 14 françaises, toutes
leurs vidéos de plus de 3 min. Le cœur de l'analyse porte sur :
- **8 sources anglaises** du genre « Ancient Humans » : Ink Explainer, Axen,
  Zenn, The Primal Glitch, Paint It Simple, Mack, Explain In Paint, Stickly
  (**399 vidéos**) ;
- **10 chaînes françaises** du même genre : Zelan, Le Gribouilleur,
  Gribouillis, L'inattendu, Nos Ancêtres, Humain Moderne, Lucas Explique,
  Avant Nous, Le Stick Qui Explique, Les Premiers Humains (**321 vidéos**).

Chaque vidéo reçoit un thème (77 thèmes) à partir de son titre, avec une
grille de mots en anglais et en français (`outils_releve/sujets.py`). Pour
une vidéo française, le titre anglais déclaré sur YouTube compte aussi :
202 vidéos sur 321 en ont un. Résultat : 84 % des vidéos françaises et 67 %
des anglaises ont un thème. Les données : [`sujets_en_fr_2026-10-01.csv`](sujets_en_fr_2026-10-01.csv)
(un thème par ligne) et [`copies_titres_2026-10-01.csv`](copies_titres_2026-10-01.csv)
(les 48 copies de titre).

Les vues sont celles du 01/10, sans correction de l'âge des vidéos : une
vidéo de septembre a eu moins de temps qu'une vidéo de juin.

---

## 1. Presque tout vient de l'anglais

*Mesuré* :
- **243 vidéos françaises sur 270 avec un thème (90 %)** traitent un thème
  déjà publié avant par une des 8 chaînes anglaises. Il en reste 27 sans
  antécédent dans ces 8 chaînes ; elles peuvent venir d'autres chaînes
  anglaises.
- Délai : une vidéo française sort en médiane **78 jours** après la
  première vidéo anglaise sur son thème, et **15 jours** après la plus
  récente. Les Français suivent le flux anglais en continu, pas seulement
  ses anciens succès.
- **48 copies de titre** : le titre anglais déclaré par la chaîne
  française est presque mot pour mot celui d'une vidéo anglaise publiée
  avant (ressemblance ≥ 0,8 et même thème). Cela fait **24 % des 202
  vidéos qui déclarent un titre anglais**. Le délai médian est de 49 jours
  (un quart sous 21 jours, un quart au-delà de 82).

| Sources des 48 copies | Copies | | Chaînes qui copient | Copies |
|---|---|---|---|---|
| Mack | 11 | | L'inattendu | 18 |
| Explain In Paint | 8 | | Humain Moderne | 10 |
| Ink Explainer | 7 | | Le Gribouilleur | 6 |
| Stickly | 7 | | Zelan | 5 |
| Axen | 6 | | Gribouillis | 5 |
| The Primal Glitch | 5 | | Nos Ancêtres | 4 |
| Zenn | 4 | | | |

Exemples : Zelan, *Que faisait réellement nos ancêtres toute la journée ?*
(283 k vues) ← Ink Explainer, *What Did Ancient Humans Actually Do All
Day?* (9,96 M) ; L'inattendu, *Que faisaient les Hommes préhistoriques la
nuit ?* (50 k) ← Zenn, *What Did Ancient Humans Do at Night?* (8,0 M).

### Par chaîne française

| Chaîne | Vidéos | Avec thème | Thème déjà en anglais | Délai médian* | Vues médianes | Depuis |
|---|---|---|---|---|---|---|
| Zelan | 25 | 25 | 23 | 20 j | **14 523** | 13/08 |
| Gribouillis | 33 | 30 | 29 | 17 j | 4 808 | 17/07 |
| L'inattendu | 67 | 64 | 50 | 13 j | 2 448 | 07/06 |
| Le Gribouilleur | 29 | 25 | 22 | 10 j | 977 | 22/05 |
| Les Premiers Humains | 19 | 16 | 14 | 9 j | 941 | 10/09 |
| Humain Moderne | 48 | 41 | 39 | 15 j | 361 | 04/06 |
| Nos Ancêtres | 18 | 15 | 14 | 12 j | 299 | 16/08 |
| Lucas Explique | 22 | 20 | 20 | 33 j | 159 | 11/07 |
| Avant Nous | 51 | 27 | 26 | 20 j | 45 | 19/07 |
| Le Stick Qui Explique | 9 | 7 | 6 | 3 j | 27 | 18/09 |

\* Délai après la vidéo anglaise la plus récente sur le même thème.

---

## 2. Copier un succès ne rapporte pas plus

*Mesuré* :
- Une copie de titre fait en médiane **2,3 k vues**, contre **801 k** pour
  sa source anglaise : **0,66 %** des vues de la source.
- Copier un gros succès anglais (source ≥ 500 k vues) donne **2,7 k vues**
  en médiane (26 copies). Copier une vidéo anglaise moyenne (moins de
  500 k) en donne **2,2 k** (22 copies). L'écart est faible.
- Sur les 71 thèmes traités dans les deux langues :
  - succès anglais et succès français évoluent à peine ensemble
    (corrélation de rang de 0,27 entre les meilleures vidéos) ;
  - les vues médianes vont même en sens inverse (−0,22) ;
  - en revanche, le nombre de vidéos suit (0,66) : **les chaînes
    françaises reprennent les thèmes fréquents en anglais, pas ceux qui
    marchent le mieux.**

*Mesuré aussi* : les plus gros succès français ne copient pas un gros
succès anglais.
- Zelan, *Comment nos ancêtres ont-ils découvert le fer ?* : **446 k**.
  Sa source (Primal Glitch, *How Did Ancient Humans Turn Rock Into Iron?*)
  n'a que 188 k.
- Gribouillis, *Pourquoi personne ne mange d'œufs de canard ?* : 250 k,
  pour 15 k au mieux en anglais sur les œufs et le lait.

*Hypothèse* : en français, l'exécution (titre, récit, chaîne) et le sujet
pèsent plus que le succès anglais de départ.

---

## 3. Le volume français a rattrapé l'anglais

| Mois | Vidéos EN | Médiane EN | Vidéos FR | Médiane FR |
|---|---|---|---|---|
| Avril 2026 | 15 | 582 k | 0 | — |
| Mai | 33 | 152 k | 1 | 6,7 k |
| Juin | 90 | 37,5 k | 21 | 407 |
| Juillet | 69 | 17,9 k | 63 | 1,2 k |
| Août | 79 | 7,4 k | 119 | 652 |
| Septembre | 113 | 7,3 k | 117 | 941 |

*Mesuré* : en août et en septembre, les 10 chaînes françaises publient
**autant ou plus** que les 8 sources anglaises, pour une médiane autour
de 1 k vues. La médiane anglaise s'est stabilisée vers 7 k.

---

## 4. Les thèmes, du plus repris au moins repris

Les 20 thèmes que les chaînes françaises reprennent le plus (le tableau
complet, 77 thèmes, est dans le CSV) :

| Thème | Vidéos EN | Médiane EN | Meilleure EN | Vidéos FR (chaînes) | Médiane FR | Meilleure FR | Délai du 1er FR |
|---|---|---|---|---|---|---|---|
| Froid, hiver | 13 | 68 k | 2,4 M | 19 (9) | 923 | 44 k | 38 j |
| Prédateurs | 8 | 25 k | 1,3 M | 14 (8) | 703 | 15 k | 50 j |
| Mort, sépultures | 10 | 9,8 k | 582 k | 11 (6) | 134 | 3,7 k | 64 j |
| Ce qu'ils mangeaient | 11 | 10 k | 883 k | 9 (6) | 1,9 k | 19 k | 80 j |
| Toute la journée | 8 | 254 k | **9,96 M** | 9 (6) | 1,3 k | 283 k | 63 j |
| Grossesse, naissance | 4 | 10,5 k | 14 k | 9 (6) | 1,7 k | 59 k | 40 j |
| Chaleur, désert | 0 | — | — | 9 (7) | 2,4 k | 39 k | thème français |
| Santé, maladies | 14 | 16,6 k | 373 k | 8 (6) | 244 | 4,1 k | 69 j |
| Vêtements | 2 | 665 k | 973 k | 8 (5) | 722 | 22 k | 87 j |
| Chiens, loups | 20 | 15 k | 935 k | 7 (6) | 312 | 2,3 k | 34 j |
| Seule espèce humaine | 6 | 30 k | 1,3 M | 7 (6) | 10,4 k | 31 k | 51 j |
| La nuit | 6 | 34 k | 8,0 M | 7 (5) | 415 | 50 k | 60 j |
| Drogues, tabac | 6 | 173 k | 1,7 M | 7 (5) | 477 | 2,1 k | 22 j |
| Couleur de peau | 4 | 156 k | 1,1 M | 6 (5) | 549 | 30 k | 66 j |
| Manger les prédateurs | 4 | 6,3 k | 25 k | 6 (4) | 4,3 k | 42 k | 11 j |
| La pluie | 3 | 442 k | 1,6 M | 6 (6) | 3,0 k | 16 k | 8 j |
| Prédateurs et dormeurs | 2 | 1,1 M | 2,2 M | 6 (5) | 5,1 k | 58 k | 0 j |
| Métaux (fer, bronze, cuivre) | 6 | 7,8 k | 188 k | 5 (4) | 2,1 k | **446 k** | 36 j |
| Intimité | 4 | 227 k | 271 k | 5 (5) | 443 | 37 k | 38 j |
| Règles | 1 | 743 k | 743 k | 4 (4) | **39 k** | 76 k | 36 j |

*Mesuré* : **aucun thème anglais du genre ayant dépassé 50 k vues n'est
encore libre en français.** Ce qui reste libre, ce sont des vidéos hors
grille, surtout la psychologie de Zenn :
- *What If WE Are The Aliens?* (828 k) ;
- *Why Do We Always Need to Pet Everything?* (463 k, Stickly) ;
- *The Slotow Effect* (319 k) ;
- *Do Animals Know When Another Animal is a Baby?* (292 k, Ink Explainer) ;
- *Did Autistic Traits Help Ancient Tribes?* (189 k, Mack) ;
- *Why Life Speeds Up As You Get Older?* (152 k) ;
- *The Spotlight Effect* (148 k) ;
- *Is Your Inner Voice Really You?* (102 k).

*Mesuré aussi* : deux veines sont **plus fortes en français qu'en
anglais**, en médiane :
- le corps des femmes : règles 39 k en français, grossesse 1,7 k ;
- la chaleur (canicule, désert), un thème que les 8 sources anglaises
  n'ont pas.

---

## 5. Les matières, le créneau de Zehon

| Matière | Vidéos EN (1re) | Meilleure EN | Vidéos FR | Meilleure FR |
|---|---|---|---|---|
| Métaux | 6 (09/08) | 188 k (Primal Glitch, fer) | 5 | **446 k** (Zelan, fer) |
| Sel | 4 (13/07) | 35 k (Stickly) | 2 | 6,3 k (Zelan) |
| Sucre, chocolat | 2 (12/08) | 3,7 k | 4 | 3,7 k (Zelan) |
| Papier | 1 (30/08) | 5,9 k (Stickly) | 1 | 4,6 k (Zelan) |
| **Verre** | 1 (20/09) | 7,0 k (Stickly, *When Did Humans First Invent Glass?*) | 1 | **443** (L'inattendu, *Comment les Humains ont inventé le VERRE ?*, 13/08) |
| Pain | 0 | — | 1 | 1,2 k (L'inattendu) |

*Mesuré* :
- Les matières sont **récentes** dans le genre anglais (depuis juillet)
  et **rares** : 14 vidéos sur 399.
- Hors le fer, elles font peu de vues dans les deux langues.
- En français, **Zelan tient presque seul la veine** (fer, sel, sucre,
  papier). Le fer est le plus gros succès de toutes les chaînes clones.
- **Le verre n'a qu'une vidéo française**, à 443 vues, et elle date
  d'avant la vidéo anglaise.

*Hypothèse* :
- la matière n'est pas un thème saturé ;
- le fer a marché par le récit de la découverte, pas parce que le sujet
  venait d'une source anglaise ;
- c'est l'angle de Zehon (« de la matière à l'objet »), à condition de
  ne pas copier les titres « How did ancient humans discover X ».

---

## 6. Les autres familles

- **Le Labo de la Curiosité** (122 k abonnés, médiane 92 k) reprend le
  **format** de The Paint Explainer, « Chaque X expliqué en N minutes »
  (23 vidéos sur 45). Il reprend peu ses sujets : 6 seulement en commun
  (idéologies politiques, niveaux de l'enfer, philosophes, intelligence,
  châtiments, sectes). The Paint Explainer a deux ans d'avance (11/2023
  contre 02/2025).
- **Premiers humains** est la version française officielle d'EarlyHumans
  (des traductions, pas des copies) : médiane **1,8 k**, contre 16,4 k pour
  l'original.
- **Quand Tout a Commencé** (« Comment a été fabriqué le premier… en
  18xx ») : **aucune source trouvée** parmi les chaînes anglaises
  relevées. History of Simple Things et Simple Things posent une autre
  question (« pourquoi tel objet a tel détail »).

---

## Limites

- **Les thèmes viennent de mots-clés.** Un titre mal classé change un
  compte de quelques unités, pas les tendances. 16 % des vidéos françaises
  et 33 % des anglaises n'ont pas de thème.
- **Seules 8 chaînes anglaises comptent comme sources.** Un thème sans
  antécédent ici peut en avoir un ailleurs. La part réelle de sujets
  venus de l'anglais est donc **au moins** de 90 %.
- **Les copies de titre sont un plancher.** 119 vidéos françaises n'ont
  pas de titre anglais déclaré, et une copie réécrite n'est pas détectée.
