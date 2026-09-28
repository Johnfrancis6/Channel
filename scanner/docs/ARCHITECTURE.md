# Scanner — architecture

App personnelle de scan et d'édition de documents (type CamScanner), pour un
seul utilisateur, sur iPhone via Safari (PWA ajoutée à l'écran d'accueil),
hébergée sur Cloudflare dans les offres gratuites.

Principe directeur : **tout le calcul lourd tourne dans le navigateur**
(détection des bords, redressement, filtres, OCR, génération du PDF). Le
serveur ne fait que stocker et chercher. Aucun appel à une API d'IA.

---

## 1. Schéma des composants

```
 iPhone — Safari / PWA (écran d'accueil)
 ┌──────────────────────────────────────────────────────────────────────┐
 │  UI Preact (Vite + TypeScript)                                       │
 │   Liste ─── Éditeur [onglet Image | onglet Texte] ─── Coins          │
 │     │            │                    │                              │
 │     │   ┌────────┴────────┐   ┌───────┴────────┐   ┌──────────────┐  │
 │     │   │ scan/ (OpenCV.js│   │ ocr/ (Tesseract│   │ export/      │  │
 │     │   │ à la demande)   │   │ .js, fra)      │   │ pdf-lib,     │  │
 │     │   │ bords, warp,    │   │ Web Worker     │   │ txt (docx V2)│  │
 │     │   │ filtres         │   │                │   │              │  │
 │     │   └─────────────────┘   └────────────────┘   └──────────────┘  │
 │     │   géométrie pure (geometry.ts) — testée unitairement           │
 │     └── api.ts (fetch /api/*, cookie Access)                         │
 │                                                                      │
 │  Service worker (sw.js)                                              │
 │   · coquille de l'app : réseau d'abord, repli sur le cache           │
 │   · /vendor/* (OpenCV.js ~10 Mo, Tesseract ~10 Mo) : cache d'abord   │
 │   · /api/* : jamais mis en cache                                     │
 └───────────────────────────────┬──────────────────────────────────────┘
                                 │ HTTPS (même origine)
 ┌───────────────────────────────▼──────────────────────────────────────┐
 │ Cloudflare Access (configuré à la main dans le tableau de bord)      │
 │   → pose le cookie CF_Authorization et l'en-tête                     │
 │     Cf-Access-Jwt-Assertion sur chaque requête                       │
 └───────────────────────────────┬──────────────────────────────────────┘
 ┌───────────────────────────────▼──────────────────────────────────────┐
 │ Worker « scanner » (Workers Static Assets)                           │
 │   /api/*  → Worker Hono : vérifie le JWT Access (JWKS, aud, iss, exp)│
 │   le reste → fichiers statiques du build Vite (repli SPA)            │
 │        │                         │                                   │
 │   ┌────▼─────┐              ┌────▼──────────────┐                    │
 │   │ D1       │              │ R2                │                    │
 │   │ métadon. │              │ images des pages  │                    │
 │   │ + texte  │              │ (original,        │                    │
 │   │ OCR, FTS5│              │  traitée, vignette)│                   │
 │   └──────────┘              └───────────────────┘                    │
 └──────────────────────────────────────────────────────────────────────┘

 GitHub Actions (push sur main, dossier scanner/) :
   tests → build → provisionnement D1/R2 idempotent → migrations D1 → wrangler deploy
```

## 2. Parcours utilisateur, écran par écran

Tout est pensé pour le pouce : actions principales en bas de l'écran, cibles
d'au moins 48 px, marges `env(safe-area-inset-*)` pour l'encoche et la barre
d'accueil.

1. **Liste des documents** (écran d'accueil)
   - Barre de recherche en haut (plein texte sur titres et textes OCR, avec
     extrait surligné).
   - Liste : vignette de la 1re page, titre, date, nombre de pages.
   - Chaque ligne a un bouton « ⋯ » : Renommer, Supprimer.
   - Gros bouton flottant en bas : **« Scanner »**. Bouton secondaire
     « Importer » (photos de la photothèque).
2. **Capture** — le bouton ouvre l'appareil photo natif d'iOS
   (`<input type="file" accept="image/*" capture="environment">`). Une photo
   = une page. On revient automatiquement à l'étape suivante.
3. **Coins** (après chaque photo, ou via « Recadrer »)
   - La photo s'affiche avec le quadrilatère détecté automatiquement et
     4 poignées déplaçables au doigt (loupe au-dessus du doigt pendant le
     glissement, pour voir le coin sous le pouce).
   - Boutons : « Tout » (image entière), « Auto » (relancer la détection),
     « Pivoter », « Valider ».
   - Si la détection échoue, le cadre prend toute l'image avec une petite
     marge et un message l'indique.
4. **Éditeur** (même écran pour le scan et l'édition)
   - En haut : retour, titre (touchable pour renommer), menu Exporter
     (PDF / TXT ; DOCX en V2).
   - Onglets **Image | Texte**.
   - Bandeau de vignettes des pages, avec « + » pour ajouter une page
     (caméra) et suppression / réordonnancement.
   - **Onglet Image** : page traitée en grand ; barre d'outils en bas :
     Recadrer (→ écran Coins), Pivoter 90°, Filtres (Original, Gris, N&B,
     Couleur améliorée). V2 : Annoter (stylo, surligneur), Signature.
   - **Onglet Texte** : lance l'OCR de la page si ce n'est pas fait (barre de
     progression). Moitié haute : l'image avec les cadres des lignes
     reconnues. Moitié basse : le texte, une zone modifiable par ligne.
     Toucher un cadre sur l'image sélectionne et fait défiler la ligne
     correspondante ; toucher une ligne met son cadre en évidence.
     Bouton « Copier tout le texte ».
   - L'enregistrement dans le cloud est automatique en quittant l'éditeur,
     et manuel via « Enregistrer » ; un indicateur montre l'état
     (non enregistré / envoi / enregistré).
5. **Export** : génère le fichier dans le navigateur et ouvre la feuille de
   partage d'iOS (`navigator.share` avec fichier) — « Enregistrer dans
   Fichiers », AirDrop, Mail… Repli : téléchargement classique.

## 3. Modèle de données

### Côté client (en mémoire pendant l'édition)

```ts
Page {
  id: string                 // uuid, stable : sert de clé R2
  original: Blob             // photo réduite à 3200 px max (JPEG)
  corners: Quad              // 4 coins dans le repère de l'original
  rotation: 0|90|180|270     // appliquée après le redressement
  filter: 'original'|'gray'|'bw'|'enhanced'
  processed: Blob            // rendu final (JPEG ; PNG pour le N&B)
  width, height              // dimensions du rendu
  ocr?: { lines: OcrLine[], width, height }  // coordonnées dans le rendu
}
OcrLine { text: string; bbox: [x0,y0,x1,y1]; confidence: number }
```

Changer les coins, la rotation ou le filtre invalide l'OCR de la page (le
texte modifié à la main est perdu si l'on refait l'OCR ; une confirmation le
signale).

### D1 (`migrations/0001_init.sql`)

```sql
documents(id TEXT PK, title TEXT, created_at INT, updated_at INT,
          page_count INT, cover_page_id TEXT)
pages(document_id TEXT, idx INT, id TEXT, width INT, height INT,
      corners TEXT /*JSON*/, rotation INT, filter TEXT,
      processed_type TEXT, ocr_json TEXT, ocr_text TEXT,
      PRIMARY KEY(document_id, idx))
docs_fts USING fts5(document_id UNINDEXED, title, body,
          tokenize = 'unicode61 remove_diacritics 2')
```

- Dates en millisecondes depuis l'époque Unix.
- `docs_fts` est réécrit (delete + insert) à chaque enregistrement du
  document : `body` = concaténation des `ocr_text` des pages. Le tokeniseur
  ignore les accents : « releve » trouve « relevé ».
- V2 : table `folders` et colonne `documents.folder_id`.

### R2 (bucket `scanner-files`)

```
docs/{documentId}/pages/{pageId}/original.jpg    photo source (pour recadrer à nouveau)
docs/{documentId}/pages/{pageId}/processed.jpg   rendu final (ou .png pour le N&B)
docs/{documentId}/pages/{pageId}/thumb.jpg       vignette 320 px
```

Suppression d'un document : suppression des lignes D1 puis de tous les
objets sous le préfixe `docs/{documentId}/`. Les PDF ne sont pas stockés :
ils sont régénérés à la demande, ce qui évite les doublons et garde un seul
état de vérité.

## 4. Routes de l'API

Toutes les routes `/api/*` exigent un JWT Access valide dans l'en-tête
`Cf-Access-Jwt-Assertion` (sinon `401`). Si la configuration Access manque
côté Worker, l'API refuse tout (`503`) : échec fermé, jamais ouvert.

| Méthode | Route | Rôle |
|---|---|---|
| GET | `/api/me` | E-mail de l'utilisateur authentifié (test de session) |
| GET | `/api/documents?q=` | Liste (tri par date de modification) ; avec `q`, recherche plein texte + extraits |
| POST | `/api/documents` | Crée un document `{title}` → `{id}` |
| GET | `/api/documents/:id` | Document + métadonnées des pages + OCR |
| PATCH | `/api/documents/:id` | Renomme `{title}` |
| DELETE | `/api/documents/:id` | Supprime le document, ses pages et ses fichiers R2 |
| PUT | `/api/documents/:id/pages` | Remplace la liste ordonnée des pages (métadonnées + OCR) ; supprime de R2 les pages retirées ; met à jour la recherche |
| PUT | `/api/documents/:id/pages/:pageId/:kind` | Envoie un fichier (`original`, `processed`, `thumb`), corps brut `image/jpeg` ou `image/png`, 25 Mo max |
| GET | `/api/documents/:id/pages/:pageId/:kind` | Lit un fichier depuis R2 (ETag, `Cache-Control: private`) |

Ordre d'un enregistrement côté client : `POST` (si nouveau) → `PUT` des
fichiers modifiés → `PUT /pages` (qui valide que les fichiers référencés
existent). Ainsi une coupure réseau en cours de route ne laisse jamais une
page qui pointe vers une image absente.

## 5. Choix techniques et justification

| Sujet | Choix | Pourquoi |
|---|---|---|
| Emplacement | Sous-dossier `scanner/` de ce dépôt | Les secrets Cloudflare sont dans ce dépôt ; un sous-dossier n'interfère pas avec le reste (chaîne YouTube). Le workflow ne se déclenche que sur `scanner/**`. |
| Hébergement | **Workers Static Assets** (un seul Worker sert l'app et l'API) | Un seul `wrangler.toml`, un seul `wrangler deploy`, une seule origine (pas de CORS), une seule application Access. Pages + Functions ajoute une seconde convention (dossier `functions/`) pour rien, et Cloudflare oriente désormais les nouveaux projets vers Workers. `run_worker_first = ["/api/*"]` : les fichiers statiques ne coûtent aucune invocation du Worker. |
| Frontend | Vite + TypeScript + **Preact** | 4 ko ; l'éditeur a assez d'états (onglets, pages, sélection de ligne) pour qu'un rendu déclaratif simplifie le code. |
| Capture | Appareil photo natif via `<input capture>` | Qualité maximale (12 Mpx, mise au point, flash, HDR) et zéro souci de permission `getUserMedia` dans une PWA iOS. Pas d'aperçu vidéo avec détection en direct : noté comme amélioration possible. |
| Traitement d'image | **OpenCV.js** (paquet `@techstark/opencv-js`, auto-hébergé sous `/vendor/`), chargé à la demande | Canny + contours + `approxPolyDP` pour les bords, `warpPerspective`, `adaptiveThreshold`. Code de détection écrit à la main plutôt que jscanify : même principe, mais on garde la main sur les réglages, la stratégie de repli et les tests. |
| Géométrie | Module TypeScript pur (`geometry.ts`) | Ordre des coins, convexité, taille de sortie, rotation, mise à l'échelle, erreur de détection : testable sans navigateur. |
| OCR | **Tesseract.js** + `fra` (`@tesseract.js-data/fra`, modèle LSTM « best_int »), fichiers auto-hébergés sous `/vendor/tesseract/` | Pas de dépendance à un CDN tiers ; le service worker met tout en cache ; fonctionne hors ligne une fois chargé. |
| PDF | **pdf-lib** | Image de la page en fond + texte en mode de rendu 3 (invisible) positionné sur chaque ligne, étiré horizontalement à la largeur du cadre : la sélection et la recherche tombent au bon endroit. Police Helvetica standard (WinAnsi couvre le français ; les caractères hors jeu sont translittérés). |
| Word | bibliothèque **docx** (V2) | Demandé. |
| Backend | Worker TypeScript + **Hono** | Routage et middlewares concis ; aucun coût d'exécution notable. |
| Recherche | **FTS5** de D1, tokeniseur `unicode61 remove_diacritics 2` | Recherche plein texte insensible aux accents, extraits via `snippet()`. |
| Auth | Vérification du JWT Access dans le Worker (WebCrypto, JWKS de l'équipe mis en cache 1 h, contrôle `aud`, `iss`, `exp`, `nbf`) | Défense en profondeur : même si Access était mal réglé, l'API reste fermée. Paramètres `ACCESS_TEAM_DOMAIN` et `ACCESS_AUD` passés au déploiement depuis les variables GitHub. |
| Service worker | Écrit à la main (~80 lignes), sans Workbox | Trois règles de cache simples ; pas de dépendance de build supplémentaire. |
| Déploiement | GitHub Actions + wrangler, secrets `CLOUDFLARE_API_TOKEN` / `CLOUDFLARE_ACCOUNT_ID` | Un script crée D1 et R2 s'ils manquent (idempotent), injecte l'id D1, applique les migrations puis déploie. |
| Résolution de travail | Photo source réduite à 3200 px (côté long) ; page rendue à 2400 px max (~200 dpi en A4) | Garde la mémoire sous contrôle sur iPhone (un Mat RGBA de 12 Mpx pèse 48 Mo) tout en restant très lisible. |

### Décisions prises seul (option la plus simple, comme demandé)

- **Pas de stockage hors ligne des documents** en V1 : l'éditeur travaille en
  mémoire et enregistre dans le cloud. Si l'envoi échoue, le document reste
  ouvert avec « Non enregistré » et un bouton pour réessayer.
- **Les PDF ne sont pas stockés** : on les régénère à l'export.
- **`/api/me` est aussi protégé** : « toutes les routes de l'API » signifie
  toutes, y compris celle de diagnostic.
- **Mode développement** : `ACCESS_DEV_BYPASS=1` dans `.dev.vars` (fichier non
  commité) désactive la vérification, **uniquement** si la requête vise
  `localhost` ou `127.0.0.1`. En production, l'hôte n'est jamais `localhost`.
- **Chiffrement côté client (V2)** : il portera sur les fichiers R2 (images).
  Le texte OCR restera en clair dans D1, sinon la recherche plein texte côté
  serveur devient impossible. À trancher en V2 si tu préfères chiffrer aussi
  le texte (la recherche se ferait alors dans le navigateur).
- **`exemples/`** : les photos que tu y déposes sont utilisées par les tests
  Playwright. Le sous-dossier `exemples/prive/` est ignoré par git pour les
  photos à ne jamais commiter.

## 6. Limites connues

**Safari iOS**
- Taille de canvas limitée à 16,7 Mpx (4096 × 4096) : d'où la réduction à
  3200 px avant tout traitement.
- Mémoire : un onglet qui dépasse ~1–1,5 Go est tué sans prévenir. Les Mat
  OpenCV sont libérés explicitement (`.delete()`) après chaque étape ; le
  document ne garde en mémoire que des Blob compressés.
- PWA et Cloudflare Access : l'app installée sur l'écran d'accueil a ses
  propres cookies, séparés de Safari. Il faut donc se connecter à Access une
  fois **dans** la PWA. Choisis de préférence la méthode « One-time PIN »
  (code par e-mail), qui reste dans la fenêtre de l'app. Si la session Access
  expire, l'API renvoie une redirection que l'app détecte ; elle propose
  alors de recharger pour se reconnecter.
- Le manifeste est chargé avec `crossorigin="use-credentials"` pour que
  Access le laisse passer.
- iOS peut vider le stockage d'une PWA peu utilisée : au pire, OpenCV.js et
  le modèle OCR sont retéléchargés (~20 Mo).
- `navigator.share` avec fichiers : disponible depuis iOS 15 ; repli sur un
  téléchargement.

**OpenCV.js**
- ~10 Mo (WebAssembly embarqué). Premier chargement : quelques secondes en
  4G, puis instantané (cache du service worker). Il n'est chargé qu'au
  premier scan, jamais sur la liste des documents.
- La détection des bords suppose un document plus clair que le fond et
  bien visible. Sur fond blanc ou document froissé, le repli (image entière
  ou plus grand contour) oblige à ajuster les coins à la main.

**OCR**
- Tesseract en WebAssembly sur iPhone : compter 3 à 10 s par page A4 selon
  la densité du texte et le modèle. L'OCR tourne dans un Web Worker (l'UI
  reste fluide) et n'est lancé qu'à l'ouverture de l'onglet Texte ou à
  l'export PDF.
- Modèle `fra` ~ 3 Mo (compressé), chargé au premier OCR puis mis en cache.
- Manuscrit : mal reconnu (limite de Tesseract).

**Offres gratuites Cloudflare** (largement suffisantes pour un utilisateur)
- Workers : 100 000 requêtes / jour ; fichiers statiques : 25 Mo max par
  fichier (OpenCV.js passe).
- R2 : 10 Go, 1 M écritures / mois. Une page ≈ 1,5 Mo (original + rendu +
  vignette) : ~6 500 pages avant d'approcher la limite.
- D1 : 5 Go, 5 M lectures / jour.

## 7. Plan par phases

**V1**
1. **Squelette** — projet Vite + Preact + TS, PWA vide (manifeste, icônes,
   service worker), Worker Hono avec vérification Access, `wrangler.toml`,
   migration D1, workflow GitHub Actions (tests + déploiement), `SETUP.md`.
2. **Scan** — capture multi-pages, chargement d'OpenCV.js à la demande,
   détection des bords, écran Coins avec loupe, redressement, rotation,
   4 filtres, éditeur avec vignettes. Tests unitaires de géométrie, banc
   d'essai Playwright sur `exemples/` (et sur des documents synthétiques
   générés, pour mesurer dès maintenant).
3. **OCR et PDF** — Tesseract.js dans un Worker, onglet Texte modifiable
   avec lien image ↔ lignes, export PDF cherchable et TXT. Mesure du taux
   d'erreur de caractères (CER) dans le banc d'essai.
4. **Stockage** — API complète D1/R2, enregistrement, liste, renommage,
   suppression, recherche plein texte. Tests Vitest du Worker.

**V2** (après la V1)
- Annotations (stylo, surligneur) et signature (tracée une fois, réutilisable).
- Export `.docx`.
- Dossiers.
- Chiffrement des fichiers côté client avant l'envoi (AES-GCM, clé dérivée
  d'une phrase secrète via PBKDF2, jamais envoyée au serveur).

**Améliorations possibles, hors plan**
- Aperçu caméra en direct avec détection des bords en temps réel.
- File d'envoi hors ligne (IndexedDB) pour enregistrer sans réseau.
