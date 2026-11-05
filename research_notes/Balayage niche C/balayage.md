# Balayage ciblé de la niche C « Brand Economics » (05/11/2026)

Complément au rapport [Échecs public et systèmes chaîne finance](../../reports/Échecs%20public%20et%20systèmes%20chaîne%20finance.md),
dont l'échantillon portait surtout sur les formats « simulation ». Relevé du
2026-11-05 par l'API YouTube Data v3 : **2 428 unités de quota** (budget :
~3 000). Transcriptions : API Supadata (12 vidéos).

**Mesuré** = calculé sur les fichiers de ce dossier. **Inférence** = mon
raisonnement. Les vues sont les totaux du jour du relevé.

## Ce qui a été relevé

| Étape | Coût | Fichier |
|---|---|---|
| Catalogues complets de 11 chaînes établies (ColdFusion, MagnatesMedia, Company Man, How Money Works, Business Casual, Logically Answered, Modern MBA, PolyMatter, Economics Explained, Wall Street Millennial, Asianometry) | ≈ 220 | `videos_C.csv`, `chaines_C.csv` |
| Catalogues de 2 gagnantes et de 14 entrants en échec déjà connus du rapport | ≈ 50 | idem |
| 8 recherches de vidéos (« company history documentary », « why no one can copy », « rise and fall of the company »…), publiées depuis le 2026-03-01, triées par vues | 800 | `videos_C.csv` (lignes `recherche:`) |
| Catalogues de 21 nouveaux entrants anglophones 2025-2026 repérés par ces recherches | ≈ 80 | `chaines_C.csv` |
| Contrôle des noms et du gabarit de titre (pseudos, recherches de chaînes et de titres) | ≈ 530 | ci-dessous |
| Vide récent sur 5 sujets (12 derniers mois) | 500 | ci-dessous |
| Classement des marques (139 expressions sur les titres) | 0 | `marques_mesures.csv` |

Les scripts sont dans `outils/` (cache local dans `outils/cache/`, non
versionné). **Biais** : les recherches triées par vues sur-représentent les
gagnants ; les échecs ne sont visibles que par le rapport précédent
(`data_echecs.csv`). Les vues actuelles avantagent les vidéos anciennes.

## Résultats mesurés

**1. Le créneau a plus de gagnants anglophones que le rapport n'en
comptait.** 20 chaînes anglophones lancées en 2025-2026 ont au moins une
vidéo à ≥100 000 vues : Crayon Capital (297 K abonnés), JunkBondInvestor
(78,9 K), The Invisible Game (57,1 K), Papiens, Money Chuck, The Fatal Board,
Ground Break, Built On You, CEOzoned, Business Decoded, Breaking Even, The
Business Vault, Capital Case, Mondo Startups, TradeoffLayer, Fortune & Fall,
The EconTales, Grey Finances, The Money Professor, FOLLOWTHEMONEY. Elles
font leur premier 100 K à la vidéo n° 1 à 7 dans 17 cas sur 20 (les 3 autres : n° 20, 27 et 38).

**2. La conversion en abonnés est meilleure qu'on ne le craignait.** Sur les 22
nouveaux entrants du créneau dont la meilleure vidéo dépasse 10 000 vues, la médiane est de **7,7 abonnés
pour 1 000 vues** (de 2,0 à 15,1). TradeoffLayer (2,8) est dans le bas de la
distribution, pas au milieu. Les plus hauts : Breaking Even 15,1, Built On
You 14,8, The Business Vault 12,2, Crayon Capital 12,0, CEOzoned 10,4. Je
n'ai trouvé aucun lien simple entre la conversion et la concentration des
vues sur un seul hit (Spearman +0,06, n = 22).

**3. Les gagnants du créneau font des vidéos plus longues que les échecs.**
Durée médiane des vidéos longues : **14,8 min** chez les 20 chaînes qui ont
percé, **9,1 min** chez les 13 entrants en échec. Hits : CEOzoned 9 à 14 min,
JunkBondInvestor 12 à 21 min, Crayon Capital 11 à 21 min, Built On You 19 à
21 min.

**4. Copier le gabarit d'un gagnant échoue, ici aussi.** « The ENTIRE
History of [X] » : CEOzoned et Built On You lancent le gabarit les 4 et
5 octobre (médianes de 140 K et 105 K). **9 chaînes** l'ont repris entre le
20 octobre et le 4 novembre : meilleure vidéo entre 2 et 110 vues. « Why No
One Can Copy [X]? » après TradeoffLayer : 391, 20 et 5 vues.

**5. L'écriture du cold open ne distingue pas les hits des échecs.** Les
deux vidéos Visa en échec (The Invisible Ledger, 4 vues ; The Quiet
Monopoly, 166 vues) ont des ouvertures aussi concrètes que les hits, et la
première partage une formule mot pour mot (« That is the whole trick ») avec
le hit Amazon de Built On You (383 K). Position de la première question :
du 78e au 318e mot chez les hits, du 94e au 321e chez les échecs. Débit
mesuré : **153 mots par minute** en médiane (de 143 à 184). **Inférence** :
ce qui sépare les hits, c'est la distribution de la chaîne, la notoriété du
sujet et l'emballage, pas la qualité d'écriture de l'ouverture.

**6. Les marques de paiement surperforment et ne sont plus traitées.** Vues
d'une vidéo rapportées à la médiane de sa chaîne (rel) : American Express
5,5, Mastercard 5,4, Klarna 5,2, Temu 5,4, Duolingo 5,5, Red Bull 5,1. La
dernière vidéo forte sur Amex ou Visa/Mastercard date de 2020-2022 (Company
Man, 1,65 M et 1,58 M). Les deux échecs Visa d'octobre 2026 viennent de
chaînes sans distribution (médianes de 12 et 128 vues).

**7. Saturés ou couverts récemment** (vidéos ≥300 K dans les 12 derniers
mois) : OpenAI (36 vidéos en 12 mois), Apple (25), Google (18), Nvidia (15),
Tesla (15), Meta (13), McDonald's (1,43 M en juillet, 598 K en août),
Coca-Cola (CEOzoned, 386 K en octobre).

## Contrôles de nom et de gabarit (API, 2026-11-05)

| Vérification | Résultat |
|---|---|
| Pseudo `@whosedime` | **libre** ; `@onwhosedime`, `@whosedimetv`, `@whosedimeyt` libres aussi |
| Chaîne nommée « Whose Dime » (recherche de chaînes) | aucune |
| Pseudos déjà pris (chaînes vides ou minuscules) | `@someonepays`, `@somebodypays`, `@costoffree`, `@hiddentab`, `@nothingisfree`, `@whopaysfor` (« Who Pays For This », 3 abonnés), `@whopays` (WhoPay, 31,6 K, marque de paiement) |
| Titres contenant « who pays for » (50 résultats) | expression courante (politique, assurance, impôts). Une chaîne minuscule, Nadvert, en a fait une série en octobre 2026 (11 à 29 vues). « If UPI Is Free, Who Pays for It? » : 792 K (Nikhil Kamath, Inde) |
| Titres de la forme « [X]: Who Pays? » / « [X]. Who Pays? » | 2 sur 50 : « Your Free Bank Account Isn't Free. Who Pays? » (12 vues) et « Vinted Is Free to Sell. Who Pays? » (36 vues) |

**Inférence** : la forme « [Marque] [chose gratuite ou bon marché] : Who
Pays? » n'est le gabarit d'aucune chaîne qui réussit, donc aucune vidéo
classée ne la bloque. Le mécanisme des « copies tardives » ne s'applique
pas. La règle du rapport (rejeter un titre normalisé déjà utilisé par au
moins 3 chaînes) est respectée titre par titre. Le nom « Whose Dime » est
propre et libre.

## Vide récent sur 5 sujets (vidéos longues des 12 derniers mois, triées par vues)

| Sujet | Résultat |
|---|---|
| Costco, hot-dog | 317 K (threaded., février 2026, « Why Costco Built Entire Factories Just to Keep a $1.50 Hot Dog ») : angle déjà pris, celui des cotisations reste libre |
| Points de cartes de crédit | aucune explication de marque ; vidéos de conseil personnel (Daniel Braun 511 K) |
| Robinhood, courtage gratuit | aucune explication ; tutoriels de trading |
| Livraison gratuite d'Amazon | actualité (Cash Jordan 1,39 M) ; aucune explication |
| Paiement fractionné (Klarna) | George Kamel 318 K, JunkBondInvestor 240 K, Zac Rios 440 K |

## Limites

- Les classements de marques reposent sur des expressions dans les titres :
  « Apple » attrape aussi des vidéos sur l'iPhone, « Target » peut rater.
- Le « rel » mélange des chaînes de tailles très différentes ; les marques
  qui n'ont qu'une ou deux vidéos ont un rel fragile.
- Aucune donnée de CTR, de rétention ni de RPM : la demande est mesurée par
  les vues, le RPM reste une estimation tierce (rapport, OutlierKit).
- Les transcriptions (12) ne sont pas versionnées (droit d'auteur) ; seules
  les mesures ci-dessus le sont.
