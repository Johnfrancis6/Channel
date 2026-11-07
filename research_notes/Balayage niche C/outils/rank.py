# (marque, secteur, qui paie (angle), titre, D, V, R, K, demande mesurée, vide mesuré, risque)
M = [
("American Express","cartes de paiement","les commerçants (frais de 2 à 3,5 %) et les clients qui paient comptant","Your Amex Points: Who Pays?",5,5,5,0,"1,65 M (Company Man, 2020) ; rel 5,5","aucune vidéo ≥300 K en 12 mois","faible"),
("Visa et Mastercard","réseaux de paiement","les commerçants via l'interchange, puis tous les clients via les prix","Your Card Swipe: Who Pays?",5,4,5,0,"1,58 M (Company Man, 2020) ; rel 5,4","182 K (Asianometry, 2025) ; 2 petites chaînes à 4 et 166 vues en oct. 2026","faible (procès DOJ à citer sans parti pris)"),
("Wells Fargo","banque","clients, employés, actionnaires (comptes fictifs)","Wells Fargo's Fake Accounts: Who Paid?",4,5,5,0,"1,51 M (Company Man, 2020)","aucune vidéo en 12 mois","faible"),
("Airbnb","location courte durée","voyageurs (frais de ménage), voisins (loyers)","Airbnb's Cleaning Fee: Who Pays?",5,5,4,0,"3,47 M (Modern MBA, 2022)","2 vidéos en 12 mois, aucune ≥300 K","faible"),
("Spotify","streaming musical","abonnés payants et artistes","Spotify's Free Tier: Who Pays?",5,5,3,0,"2,47 M (MagnatesMedia, 2022)","aucune vidéo en 12 mois","faible"),
("Uber","transport","investisseurs (pertes cumulées), puis chauffeurs et clients","Uber Was Cheap. Who Paid?",5,5,3,0,"2,97 M (MagnatesMedia, 2021)","3 vidéos en 12 mois, aucune ≥300 K","faible"),
("Rolex","luxe","acheteurs du marché gris, concessionnaires","Rolex's Waitlist: Who Pays?",5,5,3,0,"1,81 M (MagnatesMedia, 2022) ; rel 2,3","aucune vidéo en 12 mois","faible"),
("Starbucks","restauration / banque de fait","clients qui chargent la carte (dépôts sans intérêt, soldes oubliés)","Your Starbucks Card: Who Pays?",4,4,4,0,"1,24 M (PolyMatter, 2021) ; 652 K (ColdFusion, 2023)","3 vidéos en 12 mois, aucune ≥300 K ; angle « banque » déjà traité 2 fois","faible"),
("Chase (JPMorgan)","banque","clients à découvert (frais de 34 $ à vérifier)","Chase's Free Checking: Who Pays?",3,5,5,0,"Chase : 248 K max, rel 0,3 ; JPMorgan 5,6 M (ColdFusion, 2023)","aucune vidéo en 12 mois","faible"),
("Venmo (PayPal)","paiements entre particuliers","commerçants, intérêts sur les soldes, virements instantanés","Venmo Is Free. Who Pays?",3,5,5,0,"Venmo : aucune vidéo trouvée ; PayPal 1,68 M (MagnatesMedia, 2024)","aucune vidéo Venmo","faible"),
("Apple Pay","paiements mobiles","banques émettrices (commission à vérifier)","Apple Pay Is Free. Who Pays?",3,5,5,0,"aucune vidéo trouvée sur l'angle ; Apple très demandé","aucune vidéo","faible"),
("Red Bull","boissons","acheteurs de canettes (budget marketing)","Red Bull's F1 Team: Who Pays?",5,5,2,0,"1,40 M (Business Casual, 2016) ; rel 5,1","1 vidéo en 12 mois, faible","faible"),
("Domino's","restauration","franchisés et livreurs","Domino's $7.99 Pizza: Who Pays?",5,5,2,0,"2,56 M (MagnatesMedia, 2023) ; rel 2,4","aucune vidéo en 12 mois","faible"),
("Crocs","chaussures","clients (marge brute à vérifier)","Crocs' $60 Clogs: Who Pays?",5,5,2,0,"1,67 M (MagnatesMedia, 2022) ; rel 2,8","aucune vidéo en 12 mois","faible"),
("DoorDash","livraison","restaurants (commissions), livreurs, abonnés DashPass","DoorDash's $0 Delivery: Who Pays?",4,5,3,0,"1,16 M (Modern MBA, 2022)","aucune vidéo en 12 mois","faible"),
("Zillow","immobilier","agents immobiliers (Premier Agent)","Zillow Is Free. Who Pays?",3,5,4,0,"551 K (Logically Answered, 2025) ; rel 3,2","aucune vidéo en 12 mois","faible"),
("Southwest","aérien","voyageurs (fin des bagages gratuits en 2025, à vérifier)","Southwest's Free Bags: Who Paid?",3,5,4,0,"321 K (Company Man, 2021) ; rel 2,0","aucune vidéo en 12 mois","faible"),
("Berkshire Hathaway","assurance / holding","assurés de GEICO (le « float »)","Buffett's Free Money: Who Pays?",3,5,5,1,"1,64 M (Business Casual, 2018) ; rel 0,6","aucune vidéo en 12 mois","moyen : action cotée, ne rien recommander"),
("Vanguard","gestion de fonds","personne : la structure mutualiste (à expliquer)","Vanguard Charges 0.03%. Who Pays?",3,5,5,1,"308 K (Logically Answered, 2021) ; rel 4,0","aucune vidéo en 12 mois","moyen : fonds, ne rien recommander"),
("Cash App (Block)","paiements","commerçants, frais de virement instantané","Cash App Is Free. Who Pays?",2,5,5,0,"pas de vidéo trouvée","aucune vidéo","faible"),
("Chase Sapphire","cartes de crédit","commerçants et porteurs qui paient des intérêts","Chase Sapphire Points: Who Pays?",2,5,5,0,"Chase rel 0,3 (n = 2)","aucune vidéo en 12 mois","faible ; à placer après Amex"),
("Delta","aérien / fidélité","American Express et ses porteurs (achat de miles)","Delta's Free Miles: Who Pays?",2,5,5,0,"283 K (Company Man, 2022) ; rel 0,7","1 vidéo en 12 mois, faible","faible"),
("Klarna","paiement fractionné","commerçants (4 à 6 %, à vérifier) et retardataires","Klarna's 0% Loans: Who Pays?",5,3,5,1,"1,18 M (Logically Answered, 2025) ; rel 5,2","398 K (juin 2026) et 240 K (JunkBondInvestor, août 2026)","moyen : débat « prêteur prédateur »"),
("Chick-fil-A","restauration","exploitants (droit d'entrée de 10 000 $, à vérifier)","Chick-fil-A's $10K Store: Who Pays?",5,5,2,1,"2,36 M (Company Man, 2020) ; rel 3,0","aucune vidéo en 12 mois","moyen : commentaires religieux et politiques"),
("Costco","grande distribution","les membres (cotisations ≈ la moitié du bénéfice, à vérifier)","Costco Sells at Cost. Who Pays?",5,4,2,0,"4,20 M (PolyMatter, 2019) ; rel 2,4","hot-dog : 317 K (threaded., fév. 2026) ; angle cotisations libre","faible"),
("In-N-Out","restauration","personne : immobilier possédé, pas de franchise","In-N-Out's $5 Burger: Who Pays?",5,4,2,0,"4,43 M (PolyMatter, 2019) ; rel 2,8","372 K (petite chaîne, juil. 2026)","faible"),
("Amazon","commerce","membres Prime et vendeurs tiers (frais)","Amazon's Free Shipping: Who Pays?",5,3,3,0,"4,20 M (PolyMatter, 2019)","12 vidéos en 12 mois, dont 1,17 M (Crayon Capital) ; aucune sur la livraison","faible"),
("Netflix","streaming","abonnés de l'offre avec pub (annonceurs)","Netflix's $8 Ad Plan: Who Pays?",5,3,3,0,"6,56 M (MagnatesMedia, 2022)","517 K (ColdFusion, déc. 2025)","faible"),
("Boeing","aéronautique","compagnies, passagers, contribuables (737 MAX)","Boeing's 737 MAX: Who Paid?",4,4,3,0,"2,08 M ; rel 2,1","1 vidéo en 12 mois","faible"),
("Trader Joe's","grande distribution","fournisseurs (marques propres)","Trader Joe's Cheap Wine: Who Pays?",4,5,2,0,"825 K (PolyMatter, 2020)","aucune vidéo en 12 mois","faible"),
("Dollar General","grande distribution","clients ruraux (prix unitaires), employés","Dollar General Is Cheap. Who Pays?",5,5,2,1,"1,54 M (Company Man, 2021) ; rel 2,2","1 vidéo en 12 mois, faible","moyen : pauvreté, politique"),
("TurboTax (Intuit)","impôts","contribuables (fin de Direct File, à vérifier)","TurboTax Is 'Free.' Who Pays?",1,5,5,1,"46 K (n = 1)","1 vidéo en 12 mois","moyen : lobbying ; sujet saisonnier (fév.)"),
("Aldi","grande distribution","fournisseurs et marques propres","Aldi's Cheap Eggs: Who Pays?",5,3,2,0,"1,64 M (Company Man, 2019) ; rel 4,2","393 K (JunkBondInvestor, oct. 2026)","faible"),
("IKEA","ameublement","clients (montage), structure de fondation","IKEA Is Cheap. Who Pays?",5,3,2,0,"2,40 M (MagnatesMedia, 2024)","862 K (août 2026)","faible"),
("Spirit Airlines","aérien","voyageurs (frais annexes), créanciers","Spirit's $39 Fares: Who Paid?",3,3,4,0,"740 K (Company Man, 2022)","3 vidéos en 12 mois, dont JunkBondInvestor","faible"),
("Duolingo","applications","les 8 à 9 % d'abonnés (à vérifier)","Duolingo Is Free. Who Pays?",4,2,3,0,"384 K ; rel 5,5","2 vidéos ≥300 K en 12 mois","faible"),
("McDonald's","restauration","franchisés (loyers), clients","McDonald's $5 Meal: Who Pays?",5,2,2,0,"3,98 M (PolyMatter, 2020) ; rel 2,9","1,43 M (juil. 2026) et 598 K (JunkBondInvestor, août 2026)","faible"),
("Temu","commerce","fournisseurs chinois, contribuables (de minimis)","Temu's $3 Dress: Who Pays?",4,3,2,1,"789 K (Modern MBA, 2023) ; rel 5,4","513 K (Mondo Startups, oct. 2026)","moyen : Chine, droits de douane"),
("Ticketmaster","billetterie","fans (frais de service)","Ticketmaster's Fees: Who Pays?",2,5,3,1,"293 K (Company Man, 2023)","aucune vidéo en 12 mois","moyen : procès antitrust"),
("Google","recherche / pub","annonceurs, puis clients via les prix","Google Is Free. Who Pays?",5,1,3,0,"3,60 M (ColdFusion, 2016)","18 vidéos en 12 mois, dont 1,46 M (TradeoffLayer)","faible"),
("Apple App Store","applications","développeurs (commission de 30 %)","Apple's 30% Cut: Who Pays?",5,1,3,0,"7,06 M (ColdFusion)","25 vidéos en 12 mois","faible"),
("Walmart","grande distribution","employés et contribuables (aides sociales)","Walmart's Low Prices: Who Pays?",3,3,2,2,"426 K (ColdFusion, 2015)","369 K (PolyMatter, mai 2026)","élevé : politique"),
("Coinbase","crypto","traders (frais)","Coinbase's Fees: Who Pays?",2,4,5,2,"193 K (WSM, 2022) ; rel 0,8","1 vidéo en 12 mois","élevé : crypto, actifs à ne pas recommander"),
("Instagram (Meta)","réseaux sociaux","annonceurs","Instagram Is Free. Who Pays?",3,1,3,1,"Instagram chez CEOzoned : 4,8 K ; Meta 2,76 M","13 vidéos en 12 mois, dont 1,81 M","moyen"),
]
rows=[]
for m in M:
    b,s,a,t,D,V,R,K,dm,vm,rk = m
    assert len(t)<=40, (t,len(t))
    rows.append((D+V+R-K,D,b,s,a,t,len(t),D,V,R,K,dm,vm,rk))
rows.sort(key=lambda r:(-r[0],-r[1]))
print(len(rows))
for i,r in enumerate(rows,1): print(i,r[0],r[2],'|',r[5],r[6])
import json; json.dump(rows,open("rank.json","w"),ensure_ascii=False)
