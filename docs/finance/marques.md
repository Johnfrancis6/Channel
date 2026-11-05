# Les 40 marques de « Whose Dime » (série « Who Pays? »)

Liste classée pour la variante C, relevé API du 2026-11-05. Méthode, données
et limites : [research_notes/Balayage niche C/balayage.md](../../research_notes/Balayage%20niche%20C/balayage.md)
(chiffres bruts dans `marques_mesures.csv`). Le plan qui s'en sert :
[PLAN_ACTION.md](PLAN_ACTION.md).

## Comment lire le score

Score = **D + V + R − K** (de 0 à 15).

| Lettre | Ce qu'elle mesure | Barème |
|---|---|---|
| **D** demande (mesuré) | Vues des vidéos existantes sur la marque, et vues rapportées à la médiane de la chaîne qui les a faites (rel) | 5 : une vidéo ≥1,4 M et rel ≥2 ; 4 : ≥800 K ; 3 : ≥300 K ou rel ≥3 ; 2 : ≥150 K ; 1 : moins |
| **V** vide (mesuré) | Vidéos fortes sur la marque dans les 12 derniers mois (corpus de 11 chaînes établies, 37 nouvelles et 8 recherches) | 5 : aucune vidéo ≥300 K ; 4 : une, ou un angle voisin déjà pris ; 3 : une récente (<6 mois) d'un gagnant du créneau ; 2 : deux ; 1 : saturé (≥10 vidéos) |
| **R** RPM probable (inférence) | Annonceurs du sujet, d'après les estimations tierces du rapport | 5 : cartes, banque, paiement, courtage, impôts ; 4 : immobilier, voyage et fidélité ; 3 : tech, abonnements, luxe ; 2 : grande consommation, restauration |
| **K** risque (inférence) | Politique, religion, ou proximité d'une recommandation de titre (avis ACVM/OCRI 31-369) | 0 faible, 1 moyen, 2 élevé |

**Le score ne fixe pas l'ordre de publication.** Avant le YPP, la publicité
ne paie pas : ce qui compte, c'est la distribution (D). Les 5 premières
vidéos prennent donc des marques à D = 5, et le RPM pèse davantage à
l'approche du seuil (voir le plan, « Les 10 premiers sujets »).

**Le titre** suit le gabarit de la série : `[Marque] [la chose gratuite ou
bon marché] : Who Pays?` (ou `Who Paid?` pour une histoire close), moins de
40 caractères, entre parenthèses. Tout chiffre du titre passe par
`02b_factcheck.md` avant publication ; ceux marqués « à vérifier » ne sont
pas encore sourcés.

## Les 40

| # | Marque | Secteur | Titre (caractères) | Qui paie : l'angle | D | V | R | K | Score | Demande (meilleure vidéo) | Vide (12 derniers mois) | Risque |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | **American Express** | cartes de paiement | Your Amex Points: Who Pays? (27) | les commerçants (frais de 2 à 3,5 %) et les clients qui paient comptant | 5 | 5 | 5 | 0 | **15** | 1,65 M (Company Man, 2020) ; rel 5,5 | aucune vidéo ≥300 K en 12 mois | faible |
| 2 | **Visa et Mastercard** | réseaux de paiement | Your Card Swipe: Who Pays? (26) | les commerçants via l'interchange, puis tous les clients via les prix | 5 | 4 | 5 | 0 | **14** | 1,58 M (Company Man, 2020) ; rel 5,4 | 182 K (Asianometry, 2025) ; 2 petites chaînes à 4 et 166 vues en oct. 2026 | faible (procès DOJ à citer sans parti pris) |
| 3 | **Airbnb** | location courte durée | Airbnb's Cleaning Fee: Who Pays? (32) | voyageurs (frais de ménage), voisins (loyers) | 5 | 5 | 4 | 0 | **14** | 3,47 M (Modern MBA, 2022) | 2 vidéos en 12 mois, aucune ≥300 K | faible |
| 4 | **Wells Fargo** | banque | Wells Fargo's Fake Accounts: Who Paid? (38) | clients, employés, actionnaires (comptes fictifs) | 4 | 5 | 5 | 0 | **14** | 1,51 M (Company Man, 2020) | aucune vidéo en 12 mois | faible |
| 5 | **Spotify** | streaming musical | Spotify's Free Tier: Who Pays? (30) | abonnés payants et artistes | 5 | 5 | 3 | 0 | **13** | 2,47 M (MagnatesMedia, 2022) | aucune vidéo en 12 mois | faible |
| 6 | **Uber** | transport | Uber Was Cheap. Who Paid? (25) | investisseurs (pertes cumulées), puis chauffeurs et clients | 5 | 5 | 3 | 0 | **13** | 2,97 M (MagnatesMedia, 2021) | 3 vidéos en 12 mois, aucune ≥300 K | faible |
| 7 | **Rolex** | luxe | Rolex's Waitlist: Who Pays? (27) | acheteurs du marché gris, concessionnaires | 5 | 5 | 3 | 0 | **13** | 1,81 M (MagnatesMedia, 2022) ; rel 2,3 | aucune vidéo en 12 mois | faible |
| 8 | **Chase (JPMorgan)** | banque | Chase's Free Checking: Who Pays? (32) | clients à découvert (frais de 34 $ à vérifier) | 3 | 5 | 5 | 0 | **13** | Chase : 248 K max, rel 0,3 ; JPMorgan 5,6 M (ColdFusion, 2023) | aucune vidéo en 12 mois | faible |
| 9 | **Venmo (PayPal)** | paiements entre particuliers | Venmo Is Free. Who Pays? (24) | commerçants, intérêts sur les soldes, virements instantanés | 3 | 5 | 5 | 0 | **13** | Venmo : aucune vidéo trouvée ; PayPal 1,68 M (MagnatesMedia, 2024) | aucune vidéo Venmo | faible |
| 10 | **Apple Pay** | paiements mobiles | Apple Pay Is Free. Who Pays? (28) | banques émettrices (commission à vérifier) | 3 | 5 | 5 | 0 | **13** | aucune vidéo trouvée sur l'angle ; Apple très demandé | aucune vidéo | faible |
| 11 | **Red Bull** | boissons | Red Bull's F1 Team: Who Pays? (29) | acheteurs de canettes (budget marketing) | 5 | 5 | 2 | 0 | **12** | 1,40 M (Business Casual, 2016) ; rel 5,1 | 1 vidéo en 12 mois, faible | faible |
| 12 | **Domino's** | restauration | Domino's $7.99 Pizza: Who Pays? (31) | franchisés et livreurs | 5 | 5 | 2 | 0 | **12** | 2,56 M (MagnatesMedia, 2023) ; rel 2,4 | aucune vidéo en 12 mois | faible |
| 13 | **Crocs** | chaussures | Crocs' $60 Clogs: Who Pays? (27) | clients (marge brute à vérifier) | 5 | 5 | 2 | 0 | **12** | 1,67 M (MagnatesMedia, 2022) ; rel 2,8 | aucune vidéo en 12 mois | faible |
| 14 | **Klarna** | paiement fractionné | Klarna's 0% Loans: Who Pays? (28) | commerçants (4 à 6 %, à vérifier) et retardataires | 5 | 3 | 5 | 1 | **12** | 1,18 M (Logically Answered, 2025) ; rel 5,2 | 398 K (juin 2026) et 240 K (JunkBondInvestor, août 2026) | moyen : débat « prêteur prédateur » |
| 15 | **Starbucks** | restauration / banque de fait | Your Starbucks Card: Who Pays? (30) | clients qui chargent la carte (dépôts sans intérêt, soldes oubliés) | 4 | 4 | 4 | 0 | **12** | 1,24 M (PolyMatter, 2021) ; 652 K (ColdFusion, 2023) | 3 vidéos en 12 mois, aucune ≥300 K ; angle « banque » déjà traité 2 fois | faible |
| 16 | **DoorDash** | livraison | DoorDash's $0 Delivery: Who Pays? (33) | restaurants (commissions), livreurs, abonnés DashPass | 4 | 5 | 3 | 0 | **12** | 1,16 M (Modern MBA, 2022) | aucune vidéo en 12 mois | faible |
| 17 | **Zillow** | immobilier | Zillow Is Free. Who Pays? (25) | agents immobiliers (Premier Agent) | 3 | 5 | 4 | 0 | **12** | 551 K (Logically Answered, 2025) ; rel 3,2 | aucune vidéo en 12 mois | faible |
| 18 | **Southwest** | aérien | Southwest's Free Bags: Who Paid? (32) | voyageurs (fin des bagages gratuits en 2025, à vérifier) | 3 | 5 | 4 | 0 | **12** | 321 K (Company Man, 2021) ; rel 2,0 | aucune vidéo en 12 mois | faible |
| 19 | **Berkshire Hathaway** | assurance / holding | Buffett's Free Money: Who Pays? (31) | assurés de GEICO (le « float ») | 3 | 5 | 5 | 1 | **12** | 1,64 M (Business Casual, 2018) ; rel 0,6 | aucune vidéo en 12 mois | moyen : action cotée, ne rien recommander |
| 20 | **Vanguard** | gestion de fonds | Vanguard Charges 0.03%. Who Pays? (33) | personne : la structure mutualiste (à expliquer) | 3 | 5 | 5 | 1 | **12** | 308 K (Logically Answered, 2021) ; rel 4,0 | aucune vidéo en 12 mois | moyen : fonds, ne rien recommander |
| 21 | **Cash App (Block)** | paiements | Cash App Is Free. Who Pays? (27) | commerçants, frais de virement instantané | 2 | 5 | 5 | 0 | **12** | pas de vidéo trouvée | aucune vidéo | faible |
| 22 | **Chase Sapphire** | cartes de crédit | Chase Sapphire Points: Who Pays? (32) | commerçants et porteurs qui paient des intérêts | 2 | 5 | 5 | 0 | **12** | Chase rel 0,3 (n = 2) | aucune vidéo en 12 mois | faible ; à placer après Amex |
| 23 | **Delta** | aérien / fidélité | Delta's Free Miles: Who Pays? (29) | American Express et ses porteurs (achat de miles) | 2 | 5 | 5 | 0 | **12** | 283 K (Company Man, 2022) ; rel 0,7 | 1 vidéo en 12 mois, faible | faible |
| 24 | **Chick-fil-A** | restauration | Chick-fil-A's $10K Store: Who Pays? (35) | exploitants (droit d'entrée de 10 000 $, à vérifier) | 5 | 5 | 2 | 1 | **11** | 2,36 M (Company Man, 2020) ; rel 3,0 | aucune vidéo en 12 mois | moyen : commentaires religieux et politiques |
| 25 | **Costco** | grande distribution | Costco Sells at Cost. Who Pays? (31) | les membres (cotisations ≈ la moitié du bénéfice, à vérifier) | 5 | 4 | 2 | 0 | **11** | 4,20 M (PolyMatter, 2019) ; rel 2,4 | hot-dog : 317 K (threaded., fév. 2026) ; angle cotisations libre | faible |
| 26 | **In-N-Out** | restauration | In-N-Out's $5 Burger: Who Pays? (31) | personne : immobilier possédé, pas de franchise | 5 | 4 | 2 | 0 | **11** | 4,43 M (PolyMatter, 2019) ; rel 2,8 | 372 K (petite chaîne, juil. 2026) | faible |
| 27 | **Amazon** | commerce | Amazon's Free Shipping: Who Pays? (33) | membres Prime et vendeurs tiers (frais) | 5 | 3 | 3 | 0 | **11** | 4,20 M (PolyMatter, 2019) | 12 vidéos en 12 mois, dont 1,17 M (Crayon Capital) ; aucune sur la livraison | faible |
| 28 | **Netflix** | streaming | Netflix's $8 Ad Plan: Who Pays? (31) | abonnés de l'offre avec pub (annonceurs) | 5 | 3 | 3 | 0 | **11** | 6,56 M (MagnatesMedia, 2022) | 517 K (ColdFusion, déc. 2025) | faible |
| 29 | **Dollar General** | grande distribution | Dollar General Is Cheap. Who Pays? (34) | clients ruraux (prix unitaires), employés | 5 | 5 | 2 | 1 | **11** | 1,54 M (Company Man, 2021) ; rel 2,2 | 1 vidéo en 12 mois, faible | moyen : pauvreté, politique |
| 30 | **Boeing** | aéronautique | Boeing's 737 MAX: Who Paid? (27) | compagnies, passagers, contribuables (737 MAX) | 4 | 4 | 3 | 0 | **11** | 2,08 M ; rel 2,1 | 1 vidéo en 12 mois | faible |
| 31 | **Trader Joe's** | grande distribution | Trader Joe's Cheap Wine: Who Pays? (34) | fournisseurs (marques propres) | 4 | 5 | 2 | 0 | **11** | 825 K (PolyMatter, 2020) | aucune vidéo en 12 mois | faible |
| 32 | **Aldi** | grande distribution | Aldi's Cheap Eggs: Who Pays? (28) | fournisseurs et marques propres | 5 | 3 | 2 | 0 | **10** | 1,64 M (Company Man, 2019) ; rel 4,2 | 393 K (JunkBondInvestor, oct. 2026) | faible |
| 33 | **IKEA** | ameublement | IKEA Is Cheap. Who Pays? (24) | clients (montage), structure de fondation | 5 | 3 | 2 | 0 | **10** | 2,40 M (MagnatesMedia, 2024) | 862 K (août 2026) | faible |
| 34 | **Spirit Airlines** | aérien | Spirit's $39 Fares: Who Paid? (29) | voyageurs (frais annexes), créanciers | 3 | 3 | 4 | 0 | **10** | 740 K (Company Man, 2022) | 3 vidéos en 12 mois, dont JunkBondInvestor | faible |
| 35 | **TurboTax (Intuit)** | impôts | TurboTax Is 'Free.' Who Pays? (29) | contribuables (fin de Direct File, à vérifier) | 1 | 5 | 5 | 1 | **10** | 46 K (n = 1) | 1 vidéo en 12 mois | moyen : lobbying ; sujet saisonnier (fév.) |
| 36 | **McDonald's** | restauration | McDonald's $5 Meal: Who Pays? (29) | franchisés (loyers), clients | 5 | 2 | 2 | 0 | **9** | 3,98 M (PolyMatter, 2020) ; rel 2,9 | 1,43 M (juil. 2026) et 598 K (JunkBondInvestor, août 2026) | faible |
| 37 | **Google** | recherche / pub | Google Is Free. Who Pays? (25) | annonceurs, puis clients via les prix | 5 | 1 | 3 | 0 | **9** | 3,60 M (ColdFusion, 2016) | 18 vidéos en 12 mois, dont 1,46 M (TradeoffLayer) | faible |
| 38 | **Apple App Store** | applications | Apple's 30% Cut: Who Pays? (26) | développeurs (commission de 30 %) | 5 | 1 | 3 | 0 | **9** | 7,06 M (ColdFusion) | 25 vidéos en 12 mois | faible |
| 39 | **Duolingo** | applications | Duolingo Is Free. Who Pays? (27) | les 8 à 9 % d'abonnés (à vérifier) | 4 | 2 | 3 | 0 | **9** | 384 K ; rel 5,5 | 2 vidéos ≥300 K en 12 mois | faible |
| 40 | **Ticketmaster** | billetterie | Ticketmaster's Fees: Who Pays? (30) | fans (frais de service) | 2 | 5 | 3 | 1 | **9** | 293 K (Company Man, 2023) | aucune vidéo en 12 mois | moyen : procès antitrust |

## Écartées (score ≤ 9 ou risque élevé)

| Marque | Raison (mesuré ou inférence) |
|---|---|
| Coinbase | Crypto : proximité d'une recommandation d'actif (risque 2), demande faible (rel 0,8) |
| Temu | Couverte en octobre 2026 (Mondo Startups, 513 K) ; Chine et droits de douane |
| Walmart | Angle « contribuables » politique ; PolyMatter 369 K en mai 2026 |
| Instagram (Meta) | Saturé (13 vidéos en 12 mois) ; Instagram a fait 4,8 K chez CEOzoned |
| Coca-Cola | CEOzoned, 386 K, octobre 2026 (« The ENTIRE History of Coca-Cola ») |
| OpenAI, Nvidia, Apple, Google, Tesla | 15 à 36 vidéos en 12 mois, dont plusieurs au-dessus du million |
| Tesla / Musk, Bezos, BlackRock, UnitedHealth | Commentaires politiques sur les milliardaires et sujets à conspirations : à éviter avant 1 000 abonnés |
| Robinhood | Demande mesurée faible (rel 0,6, meilleure vidéo 149 K en 2021) malgré le vide ; à réessayer après le YPP |

## Mettre la liste à jour

- **Avant chaque sujet** : relancer la vérification du vide sur la marque
  (`python3 zehon/content-maker/scripts/youtube.py chercher "<marque> business"`,
  101 unités) et la collision du titre exact.
- **Une fois par mois** : refaire le classement (`research_notes/Balayage
  niche C/outils/`, environ 300 unités pour les catalogues, 0 pour le
  classement). Une marque traitée par un gagnant du créneau perd 2 points
  de V.
- **Après chaque vidéo publiée** : la passer en « faite » dans
  `Memoire/sujets.md` du Drive avec ses vues à 7 et 28 jours.
