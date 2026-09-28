# Scanner

App personnelle de scan de documents, à la CamScanner, sans abonnement.
C'est une PWA pour iPhone (Safari → « Ajouter à l'écran d'accueil »),
hébergée sur Cloudflare dans les offres gratuites. Tout le traitement
(détection des bords, redressement, filtres, OCR, PDF) tourne dans le
téléphone ; le serveur ne fait que stocker et chercher.

- **Scanner** : appareil photo arrière, plusieurs pages par document,
  détection automatique des bords, 4 coins ajustables au doigt (avec loupe),
  redressement, rotation, filtres (original, gris, noir et blanc, couleur
  améliorée).
- **Éditer** sur le même écran : onglet **Image** (recadrer, pivoter,
  filtres) et onglet **Texte** (OCR en français, texte modifiable ; toucher
  une ligne sur l'image la sélectionne dans le texte).
- **Exporter** : PDF cherchable (couche de texte invisible), texte brut.
- **Ranger** : documents stockés dans le cloud (R2 + D1), liste, renommage,
  suppression, recherche plein texte dans les textes reconnus.

Architecture et choix techniques : [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md).

## Installer sur l'iPhone

1. Mise en place à faire une fois : [docs/SETUP.md](docs/SETUP.md)
   (D1, R2, Cloudflare Access).
2. Sur l'iPhone, ouvre **Safari** (pas Chrome : seul Safari sait installer
   une PWA sur iOS) à l'adresse `https://scanner.<ton-sous-domaine>.workers.dev`.
3. Connecte-toi à Cloudflare Access (code reçu par e-mail).
4. Bouton **Partager** (carré avec une flèche) → **Sur l'écran d'accueil** →
   Ajouter.
5. Ouvre l'app depuis l'icône **Scanner**. Elle a ses propres cookies, séparés
   de Safari : reconnecte-toi à Access une fois dedans.
6. Au premier scan, autorise l'appareil photo. OpenCV.js (~10 Mo) se
   télécharge alors une fois, puis reste en cache ; même chose pour le modèle
   OCR français au premier passage dans l'onglet Texte.

## Déployer

Automatique : tout push sur `main` qui touche `scanner/` lance le workflow
GitHub Actions **Scanner** — tests, build, création de D1/R2 si besoin,
migrations, `wrangler deploy`. Les secrets `CLOUDFLARE_API_TOKEN` et
`CLOUDFLARE_ACCOUNT_ID` du dépôt suffisent ; les variables Access se règlent
dans GitHub (voir [SETUP.md](docs/SETUP.md#4-donner-ces-valeurs-au-worker)).

Relancer à la main : GitHub → Actions → Scanner → Run workflow.

## Développer

```sh
cd scanner
npm ci
npm test              # tests unitaires + tests du Worker (Vitest, runtime Workers)
npm run typecheck
npm run test:e2e      # Playwright : app + banc d'essai qualité (voir exemples/)
npm run build
```

Développement local avec l'API : voir [SETUP.md](docs/SETUP.md#développement-en-local-facultatif).

## Arborescence

```
src/app/       interface Preact (écrans, composants, client API)
src/scan/      géométrie pure, OpenCV.js (bords, redressement, filtres)
src/ocr/       Tesseract.js (Web Worker)
src/export/    PDF (pdf-lib), TXT
src/worker/    Worker Cloudflare : API Hono, vérification Access, D1, R2
src/shared/    types communs app / Worker
src/sw.js      service worker
migrations/    schéma D1
scripts/       copie d'OpenCV/Tesseract, provisionnement D1/R2, icônes
tests/         unit/ (Vitest), worker/ (Vitest Workers), e2e/ (Playwright)
exemples/      photos de test pour le banc d'essai
```
