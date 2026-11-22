# Mémoire — Application mobile de gestion de patrimoine

Brainstorming de faisabilité, idée par idée. Une idée n'entre dans
« Idées validées » qu'après validation explicite de Franco.

## Découpage du projet (11 idées)

1. Source des données bancaires : agrégation des comptes + base factice aux normes bancaires
2. Données de marché en temps réel : indices, taux de change, crypto, matières premières
3. Suivi du patrimoine et des portefeuilles multi-actifs (bourse, crypto, matières, immobilier)
4. Visualisation : graphes et schémas d'analyse
5. Analyse des dépenses : catégorisation flexible + questionnaire de performance financière
6. Analyse de risque des investissements : volatilité, bêta, VaR, expositions
7. Attribution de performance
8. Détection d'anomalies avec phase d'apprentissage des habitudes
9. Détection de fraude fondée sur des schémas officiels récents
10. Scoring de risque et moteur d'alerte combiné vers la banque
11. Choix des solutions gratuites par bloc (mobile, backend, données)

## Contexte (réponses de Franco)

- But : prototype pour un client
- Zone : Afrique francophone
- Mobile : React Native
- Source de données préférée : base factice (A), puis bac à sable réel (B)

## Idées validées

### Idée 1 — Source des données bancaires (validée le 2026-11-22)

- Base factice = « banque simulée » : comptes bancaires + portefeuilles
  mobile money (Orange Money, Wave, MTN MoMo), en francs CFA (XOF/XAF).
- Formats réels : IBAN de la zone UEMOA, mouvements au format ISO 20022,
  opérations mobile money (dépôt, retrait, transfert, paiement marchand).
- L'application lit la base via une API qui imite un vrai fournisseur.
- Plus tard : remplacer par un bac à sable réel (ex. API MTN MoMo) sans
  réécrire l'application. Bacs à sable Orange et Wave : à vérifier.

### Idée 2 — Données de marché (validée le 2026-11-22)

- Uniquement des API gratuites, cours différés (~15 min), mention
  « cours différés » à l'écran.
- Périmètre : indices mondiaux, crypto, matières premières (or, pétrole,
  cacao, café), devises ; franc CFA calculé par la parité fixe
  1 EUR = 655,957 XOF/XAF.
- BRVM : **exclue du prototype** (idée 11 : aucune API officielle
  gratuite ; FluxBourse API payante, Apify payante et suspendue,
  brvmr = miroir non officiel).

### Idée 3 — Suivi du patrimoine multi-actifs (validée le 2026-11-22)

- Patrimoine net = actifs (comptes, mobile money, actions, crypto,
  matières premières, immobilier) − dettes (crédits, prêts).
- Valorisation au dernier cours connu ; PRU, plus-values latentes et
  réalisées ; allocation par classe d'actifs, devise et pays.
- Devise de référence au choix de l'utilisateur (XOF par défaut ;
  EUR, USD, XAF possibles).
- Positions : portefeuilles factices pour la démo + saisie manuelle des
  achats/ventes (immobilier et actifs absents de la base).
- Immobilier : valeur saisie et mise à jour par l'utilisateur, date de
  mise à jour affichée.
- Toutes les transactions sont enregistrées (historique nécessaire aux
  idées 4, 6 et 7).

### Idée 4 — Graphes et schémas (validée le 2026-11-22, détails à venir)

- Graphes retenus : évolution du patrimoine + allocation ; dépenses en
  barres ; flux (Sankey) ; risque (VaR, drawdown) + chandeliers de cours.
- Priorité : fluidité native (Victory Native) ; le Sankey en composant
  dédié ou plus tard.
- Interactifs : info-bulle au toucher + sélecteur de période.
- Calculs côté serveur, le téléphone ne fait que dessiner.
- **Détails dans une session dédiée au système de design** (Franco).

### Idée 5 — Analyse des dépenses (validée le 2026-11-22)

- Catégorisation : règles et mots-clés d'abord ; opérations non reconnues
  envoyées à un modèle open source via Groq (ou hébergé ailleurs) ;
  plan de secours : règles seules.
- Chaque correction de l'utilisateur devient une règle ; catégories
  modifiables avec sous-catégories.
- Questionnaire unique à l'inscription (modifiable) : revenus et charges
  fixes, objectifs, tolérance au risque, habitudes de dépenses.
- Budgets mensuels par catégorie, alertes à 80 % et 100 %.
- Indicateurs : taux d'épargne, reste à vivre, part des dépenses
  contraintes, évolution d'un mois sur l'autre.
- Réserve : avec Groq, les libellés partent chez un tiers ; sans
  problème sur base factice, à revoir pour de vrais clients.

### Idée 6 — Analyse de risque des investissements (validée le 2026-11-22)

- Volatilité annualisée, bêta, VaR historique + CVaR, expositions
  (classe d'actifs, devise, pays, secteur).
- VaR à 95 % sur 1 jour et sur 1 mois.
- Bêta calculé contre l'indice du marché de chaque actif (S&P 500,
  BRVM Composite si une source existe, Bitcoin pour la crypto).
- Alertes de concentration, seuil réglable, lié au profil de risque.
- Immobilier (sans historique de cours) exclu de la VaR, montré à part.

### Idée 7 — Attribution de performance (validée le 2026-11-22)

- Option A seule : contribution par actif et par classe
  (poids × rendement) + effet devise. Pas de Brinson ni de portefeuille
  modèle.
- Rendements affichés : TWR (qualité des placements) et TRI (gain réel),
  avec une explication.
- Périodes : mois, année, depuis le début (+ période libre).

### Idée 8 — Détection d'anomalies (validée le 2026-11-22)

- Méthode : seuils statistiques par catégorie et bénéficiaire (qui
  expliquent l'alerte) + Isolation Forest (cas que les seuils ratent).
- Phase d'apprentissage sans alerte ; activation après 30 jours ET
  30 opérations ; profil recalculé sur fenêtre glissante.
- Chaque alerte donne sa raison en clair.
- Réponse « c'est moi » : le profil s'adapte.
- Démo client : la base factice contient déjà des mois d'historique
  appris ; on injecte ensuite des anomalies.

### Idée 9 — Détection de fraude sur schémas officiels (validée le 2026-11-22)

- **Mise à jour idée 11 : Tazama abandonné, remplacé par des règles
  codées** (trop lourd pour un hébergement gratuit).
- (Choix initial) Moteur : Tazama (open source, Apache-2.0, Linux Foundation, lien
  rapporté avec la BCEAO). Il lit des messages ISO 20022, cohérent avec
  l'idée 1. Réserve : architecture lourde (plusieurs services) — coût
  d'hébergement gratuit à vérifier à l'idée 11 ; repli : règles codées.
- Schémas couverts : SIM swap + prise de contrôle du compte ; vol d'OTP
  + faux dépôt ; comptes mules ; faux placements.
- Chaque règle cite sa source officielle ; catalogue mis à jour.
- La base factice simule aussi les événements de sécurité (connexions,
  nouvel appareil, changement de SIM).

### Idée 10 — Scoring de risque et alerte combinée (validée le 2026-11-22)

- Score combiné 0-100 = score d'anomalie (idée 8) + règles de fraude
  déclenchées (idée 9) + contexte (appareil, montant, profil).
- Seuils : < 40 rien ; 40-70 confirmation demandée à l'utilisateur ;
  > 70 alerte à la banque. Chaque alerte affiche ses raisons.
- « Banque » simulée : tableau de bord web d'analyste dans le prototype ;
  l'analyste répond « fraude » / « légitime », ce qui ajuste les seuils.
- L'application ne bloque jamais un paiement elle-même : la banque décide.
- Plus tard, avec un vrai partenaire : remplacer le tableau de bord par
  l'API de la banque.

### Idée 11 — Solutions gratuites par bloc (validée le 2026-11-22, provisoire)

Choix provisoires, à confirmer par la session « outils » :
- Mobile : React Native + Expo ; graphes : Victory Native.
- Base de données + authentification : Supabase (gratuit, pause après
  inactivité).
- Calculs (VaR, bêta, Isolation Forest, score) : Python FastAPI +
  scikit-learn, hébergement gratuit (ex. Render, s'endort).
- Marchés : Finnhub (~60 appels/min) + Twelve Data (~800/jour), cours
  différés ; serveur cache obligatoire. Crypto : CoinGecko (clé demo).
  Devises : Frankfurter (taux BCE, quotidien) ; F CFA par parité fixe.
- IA de catégorisation : Groq (~30 req/min, ~1 000/jour ; 429 au-delà).
- Fraude : règles codées (Tazama abandonné).
- Tableau de bord « banque » : Next.js sur Vercel.
- Mobile money réel plus tard : bac à sable MTN MoMo ; pas de bac à
  sable officiel trouvé pour Orange Money ni Wave (agrégateur Payfonte).
- Toutes les limites viennent de sources secondaires (novembre 2026),
  à reconfirmer sur les pages officielles.

## Suite : trois sessions de raffinement

1. Analyse technique + choix des outils : [BRIEF_01_TECH_ANALYSIS.md](BRIEF_01_TECH_ANALYSIS.md)
2. Architecture (brief écrit par la session 1)
3. Système de design

Chaque agent peut remettre en cause une décision ; Franco tranche.

## Points ambigus et réponses

_(à remplir)_
