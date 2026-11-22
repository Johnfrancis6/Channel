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

## Points ambigus et réponses

_(à remplir)_
