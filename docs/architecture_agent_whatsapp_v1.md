# Architecture — Agent WhatsApp de contenu — v1

*Rédigé le 26/09/2026, à partir du document d'état du même jour. Les
décisions D1 à D36 sont tenues pour acquises : ce document les met en
œuvre, il ne les rediscute pas. Les désaccords sont rassemblés au §12
« Objections », sans effet ailleurs dans le document.*

| § | Contenu |
|---|---|
| [0](#0-portée-méthode-et-ce-que-ce-document-ne-fait-pas) | Portée et méthode |
| [1](#1-vue-densemble) | Vue d'ensemble : trois unités, flux nominal, couches |
| [2](#2-schéma-postgres) | Schéma Postgres `ops` et `history`, isolation, purge |
| [3](#3-machine-à-états) | États, transitions, durées maximales, watchdog |
| [4](#4-services-jobs-et-flux) | Services, Cloud Run Jobs (dont le Job GPU), flux |
| [5](#5-les-deux-adaptateurs) | Adaptateur de rendu, adaptateur de génération |
| [6](#6-contrats-de-données--amendements) | Amendements A1 (storyboard) et A2 (composition) |
| [7](#7-le-monteur-et-le-compilateur) | Vocabulaire fermé A3, validateur, compilateur |
| [8](#8-pipeline-audio) | TTS, alignement, effets, ducking, normalisation |
| [9](#9-canal-admin-whatsapp-d29) | Commandes typées, schéma, garde-fous, audit |
| [10](#10-erreurs-et-alertes-o4-b-d33) | Taxonomie, messages neutres, alertes |
| [11](#11-plan-dimplémentation) | T-1 à T4 |
| [12](#12-objections) | 12 objections, sans effet sur D1–D36 |
| [13](#13-points-ouverts-qui-bloquent-une-partie-de-larchitecture) | Points ouverts bloquants |

---

## 0. Portée, méthode, et ce que ce document ne fait pas

**Critère de tri, appliqué partout** : 3 clients, ~60 projets par mois,
soit **2 projets par jour**. À cette échelle, tout mécanisme qui n'existe
que pour absorber la charge est de la sur-ingénierie. Aucune file de
messages, aucun cache distribué, aucun service par étape. Postgres est la
file d'attente, le verrou et la source de vérité ; R2 porte les octets ;
Cloud Run exécute. Les contraintes qui pilotent réellement la conception
sont ailleurs : **l'idempotence** (le coût dominant est la génération),
**l'isolation entre clients** (D30), **le délai de 4 h en 24/7** (D36) et
**la conformité binaire** de la sortie.

**Règle de reprise, posée d'emblée** (consigne 4) : un état est un point
de reprise, et *aucun état n'est franchi avant que ses artefacts soient
durables sur R2 et inscrits en base* (D10). Un job relancé depuis l'état
courant ne repaie donc jamais ce qui précède. À l'intérieur d'un état,
c'est la clé d'idempotence qui protège chaque appel payant, pas l'état :
un crash au milieu de `GENERATING` retrouve les générations déjà payées
par `cle_generation` et ne paie que le reste. Les deux mécanismes sont
complémentaires et tous les deux nécessaires — l'un est grossier, l'autre
fin.

**Trois unités de déploiement, pas plus** : un service HTTP, un Job CPU,
un Job GPU. Le découpage est justifié au §4 ; il découle des machines
nécessaires, pas des responsabilités logiques.

Ce document ne contient aucun code applicatif. Il contient du DDL
Postgres et des schémas JSON, qui sont les livrables demandés.

---

## 1. Vue d'ensemble

### 1.1 Les trois unités

| Unité | Type | Machine | Rôle | Durée de vie |
|---|---|---|---|---|
| `svc-conversation` | Cloud Run Service | 1 vCPU, 512 Mo, `min-instances=1`, **CPU toujours alloué** | Webhook, classifieur, clarificateur, Storyboard, canal admin, envois WhatsApp, watchdog, purge | permanente |
| `job-produce` | Cloud Run Job | 4 vCPU, 8 Go, Node + FFmpeg + Chrome headless | Les trois pipelines de production (vidéo, visuel, retouche), rendu, mixage, contrôles, livraison | une exécution par tentative de projet |
| `job-tts` | Cloud Run Job | GPU L4 24 Go, `europe-west4` | Chatterbox Multilingual + alignement mot à mot | ~2 min par projet vidéo |

`svc-conversation` a **CPU toujours alloué** et `min-instances=1` parce
qu'il fait trois choses qui ne tiennent pas dans le cycle
requête/réponse : copier le média entrant sur R2 avant expiration de
l'URL, tenir le watchdog toutes les 60 s, et vider la file d'envoi. La
variante « tout déléguer à un Job » a été écartée : elle ajoute un
démarrage à froid de 10 à 15 s sur le chemin le plus sensible (le média
entrant) et une unité de déploiement, pour économiser une vingtaine de
dollars par mois.

Écarté aussi : un Job distinct par type de pipeline. D28 exige que la
retouche photo soit un pipeline **séparé** ; elle l'est, comme chemin de
code disjoint dans `job-produce`, avec ses propres états terminaux. Trois
images de conteneur pour trois chemins qui partagent la livraison, les
contrôles et l'idempotence coûteraient trois déploiements pour zéro
isolation supplémentaire.

Le GPU est séparé parce que la machine est différente et chère : il est
tenu ~2 min par projet au lieu de l'être pendant le rendu.

### 1.2 Flux nominal, projet vidéo

```
WhatsApp                 svc-conversation              Postgres / R2
   │                            │
   ├── POST webhook ───────────► vérif X-Hub-Signature-256
   │                            INSERT message_entrant (PK = wa_message_id)
   ◄────── 200 (< 1 s) ─────────┤   ← dédup structurelle
                                │
                                ├─ média entrant → R2 (immédiat, URL périssable)
                                ├─ numéro admin ?  → §9
                                ├─ hors liste blanche ? → message fixe, fin
                                ├─ Classifieur (LLM) → job_type | hors périmètre
                                ├─ Clarificateur → boutons / listes / brouillon
                                ├─ Storyboard (LLM) → R2 + ops.objet
                                └─ envoi au client pour validation (D24)
                                        │
                                   validation client
                                        │
                                        ├─ plafond copié dans projet.budget_restant
                                        └─ exécute job-produce ──┐
                                                                 ▼
                          job-produce                    ┌─────────────────┐
                            ├─ génération d'assets ──────►│ cle_generation  │
                            ├─ exécute job-tts (GPU) ─────┤ ops.generation  │
                            │     voix off + alignement   └─────────────────┘
                            ├─ ÉTAT: ASSETS_READY  ◄── point de reprise
                            ├─ Monteur (LLM) → montage_plan.json → validateur
                            ├─ compilateur → composition.json → validateur → lint DOM
                            ├─ adaptateur de rendu → video muette + hash de frames
                            ├─ effets sonores → musique + ducking → -14 LUFS / -1 dBTP
                            ├─ mux → master + aperçu → ffprobe bloquant
                            └─ ÉTAT: RENDERED_VERIFIED  ◄── point de reprise
                                        │
                        svc-conversation ├─ aperçu envoyé à Franco (D22)
                                         │
                                    validation Franco
                                         │
                                         └─ livraison double : video + document (D23)
```

### 1.3 Ce qui traverse les couches

La séparation des couches du document d'état est la règle ; elle se lit
ici comme une contrainte de contenu sur chaque artefact, vérifiée par un
validateur mécanique à chaque frontière.

| Frontière | Validateur | Refuse |
|---|---|---|
| Storyboard → client | `storyboard.schema.json` + R-SB-1..4 | ms, px, hex, noms d'animation, script qui ne tient pas en 30 s |
| Monteur → compilateur | `montage_plan.schema.json` + V-MP-1..9 | toute valeur résolue, toute durée, tout identifiant hors catalogue |
| Compilateur → moteur | `composition.schema.json` + lint DOM | intention, adjectif, slot inconnu, dépassement de zone de sécurité |
| Moteur → livraison | ffprobe + mesure de boucle | non-conformité technique, dérive de durée |

**Test de complétude des contrats** : si le compilateur ou l'adaptateur
de rendu doit *choisir* quelque chose, le contrat en amont est incomplet.
Chaque valeur du `composition.json` doit être traçable à une règle
numérotée du §7.3 ; c'est à cela que sert le `trace_resolution` (§7.4).

---

## 2. Schéma Postgres

Un seul Postgres (D8), deux schémas (D8) dont la frontière est un
**cycle de vie**, pas un domaine :

- **`ops`** : l'ensemble de travail. Mutable, petit, **purgé à 7 jours**
  après la fin du projet (D27). Contient des clés R2 qui pointent vers
  des octets eux-mêmes périssables.
- **`history`** : métadonnées permanentes, **append-only**, sans média et
  sans clé R2 vivante. C'est ce qui reste quand R2 a été purgé : les
  transitions, l'audit, les livraisons, les dépenses. Le seul consommateur
  est Franco (commande admin « état, dépenses ») et la calibration future
  du juge automatique (D22).

Volumétrie cible à 12 mois : ~720 projets, ~8 000 générations, ~20 000
messages. Tout tient dans la plus petite instance ; aucun partitionnement,
aucun index de recherche plein texte.

### 2.1 Isolation par `client_id` (D30)

Trois mécanismes, dans cet ordre de fiabilité :

1. **`client_id NOT NULL` sur toute table portant de la donnée client**,
   et **clé étrangère composite** vers `ops.projet (projet_id, client_id)`.
   Une ligne d'un client attachée au projet d'un autre est donc
   *impossible*, pas seulement interdite : la base la rejette. C'est le
   mécanisme central, il ne coûte qu'une colonne dénormalisée et une
   contrainte d'unicité.
2. **Préfixe R2 par client** : `clients/{client_id}/projets/{projet_id}/…`,
   `brand/{client_id}/…`. La bibliothèque audio, partagée, vit sous
   `library/audio/…` et n'a pas de `client_id`.
3. **Assemblage du contexte LLM par projet, jamais cumulatif** : la
   charte (D5), les exemples et les assets injectés dans un prompt sont
   lus par `client_id` et `projet_id` du projet courant. Aucun cache de
   prompt partagé entre clients. La `cle_generation` inclut le
   `client_id` (§5.2) : deux clients qui demandent la même image paient
   deux fois, et c'est voulu — un cache commun serait une fuite.

**RLS écarté.** Un seul backend de confiance, trois clients, aucun accès
direct à la base depuis l'extérieur : RLS ajouterait une couche de
politiques à maintenir et à déboguer pour une menace (client SQL hostile)
qui n'existe pas dans ce déploiement. Les clés étrangères composites
attrapent la seule erreur réaliste, qui est une erreur de code. À
reconsidérer le jour où un client obtient un accès direct à la base.

### 2.2 Types

```sql
CREATE SCHEMA ops;
CREATE SCHEMA history;

CREATE TYPE ops.statut_client AS ENUM ('actif', 'pause', 'retire');

CREATE TYPE ops.type_job AS ENUM ('video', 'visuel', 'retouche');

-- Valeurs reprises telles quelles du diagramme du document d'état.
CREATE TYPE ops.etat_projet AS ENUM (
  'RECEIVED', 'REJECTED', 'CLARIFYING', 'BRIEF_READY',
  'STORYBOARD_PENDING_CLIENT', 'GENERATING', 'ASSETS_READY',
  'RENDERED_VERIFIED', 'PENDING_REVIEW', 'DELIVERED',
  'CORRECTION', 'FAILED'
);

CREATE TYPE ops.role_objet AS ENUM (
  -- entrants et permanents
  'asset_client', 'brand_asset', 'police',
  -- contrats
  'storyboard', 'montage_plan', 'composition', 'alignement',
  -- audio
  'voix_brute', 'voix_mix', 'effets_mix', 'musique_mix', 'mix_final',
  -- images et vidéo
  'asset_genere', 'rendu_muet', 'master', 'apercu', 'visuel', 'retouche',
  -- diagnostic
  'trace_resolution', 'rapport_conformite'
);

CREATE TYPE ops.statut_generation AS ENUM
  ('reserve', 'en_cours', 'reussie', 'echouee', 'abandonnee');

CREATE TYPE ops.statut_template AS ENUM
  ('brouillon', 'en_validation', 'approuve', 'retire');

CREATE TYPE ops.role_audio AS ENUM ('voix', 'effets', 'musique');

CREATE TYPE ops.kind_piste AS ENUM ('effet', 'musique');

CREATE TYPE ops.statut_envoi AS ENUM ('en_file', 'envoye', 'echoue');

CREATE TYPE ops.kind_envoi AS ENUM
  ('texte', 'interactif', 'video', 'document', 'image', 'template_utility');

CREATE TYPE ops.commande_admin_nom AS ENUM (
  'client_ajouter', 'client_retirer', 'client_pause', 'client_reprendre',
  'plafond_modifier', 'livraison_valider', 'livraison_refuser',
  'style_approuver', 'job_relancer', 'etat_lire', 'depenses_lire',
  'donnees_supprimer'
);

CREATE TYPE ops.statut_commande AS ENUM
  ('proposee', 'confirmee', 'executee', 'refusee', 'expiree');

CREATE TYPE ops.au_depassement AS ENUM ('relancer', 'echouer', 'alerter');

CREATE TYPE ops.kind_job AS ENUM ('produce', 'tts');
```

### 2.3 `ops` — clients, projets, objets

```sql
CREATE TABLE ops.client (
  client_id        uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  wa_phone_e164    text NOT NULL,
  nom_affiche      text NOT NULL,
  statut           ops.statut_client NOT NULL DEFAULT 'actif',
  langue           text NOT NULL DEFAULT 'fr',
  brand_pack_id    uuid,              -- FK ajoutée après ops.brand_pack
  cree_le          timestamptz NOT NULL DEFAULT now(),
  maj_le           timestamptz NOT NULL DEFAULT now(),
  CONSTRAINT client_phone_e164 CHECK (wa_phone_e164 ~ '^\+[1-9][0-9]{7,14}$')
);

-- La liste blanche (D25) EST cette table : un numéro joignable est un
-- client non retiré. Pas de table dédiée.
CREATE UNIQUE INDEX client_phone_unique
  ON ops.client (wa_phone_e164) WHERE statut <> 'retire';

CREATE TABLE ops.projet (
  projet_id           uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  client_id           uuid NOT NULL REFERENCES ops.client (client_id),
  type_job            ops.type_job NOT NULL,
  etat                ops.etat_projet NOT NULL DEFAULT 'RECEIVED',
  etat_depuis         timestamptz NOT NULL DEFAULT now(),
  tentatives_etat     smallint NOT NULL DEFAULT 0,
  -- horloge de service : n'accumule que le temps qui nous appartient (§3.4)
  sla_cumul_ms        bigint NOT NULL DEFAULT 0,
  sla_alerte_envoyee  boolean NOT NULL DEFAULT false,
  -- plafond D35 : copié à l'entrée en GENERATING, décrémenté avant appel
  budget_centimes     integer NOT NULL DEFAULT 0,
  budget_restant      integer NOT NULL DEFAULT 0,
  brief               jsonb NOT NULL DEFAULT '{}'::jsonb,
  voix_id             text,
  template_slug       text,
  template_version    integer,
  -- bail d'exécution : empêche deux jobs sur le même projet
  bail_par            text,
  bail_jusqu_a        timestamptz,
  code_echec          text,
  detail_echec        jsonb,
  -- état quitté pour aller en FAILED, restauré par la commande admin
  -- « relancer un job ». Écart assumé avec le diagramme, voir §12 / O-2.
  etat_avant_echec    ops.etat_projet,
  cree_le             timestamptz NOT NULL DEFAULT now(),
  livre_le            timestamptz,
  clos_le             timestamptz,
  purge_apres         timestamptz,

  CONSTRAINT projet_client_unique UNIQUE (projet_id, client_id),
  CONSTRAINT projet_budget_positif CHECK (budget_restant >= 0),
  CONSTRAINT projet_budget_borne   CHECK (budget_restant <= budget_centimes),
  CONSTRAINT projet_bail_coherent
    CHECK ((bail_par IS NULL) = (bail_jusqu_a IS NULL)),
  CONSTRAINT projet_livre_coherent
    CHECK ((etat = 'DELIVERED') = (livre_le IS NOT NULL)
           OR etat IN ('CORRECTION', 'FAILED')),
  CONSTRAINT projet_echec_documente
    CHECK (etat <> 'FAILED' OR code_echec IS NOT NULL)
);
```

`budget_restant >= 0` **est** l'application de D35 : le décrément et
l'insertion de la ligne `ops.generation` sont dans la même transaction,
donc un dépassement de plafond fait échouer la transaction *avant*
l'appel au fournisseur. La limite stricte chez fal.ai (O6-B) reste la
seconde ligne, hors de notre contrôle.

`projet_echec_documente` interdit un `FAILED` muet : c'est la moitié de
O4-B écrite dans la base.

```sql
CREATE INDEX projet_a_surveiller
  ON ops.projet (etat, etat_depuis)
  WHERE etat NOT IN ('DELIVERED', 'REJECTED', 'FAILED');

CREATE INDEX projet_bail_expire
  ON ops.projet (bail_jusqu_a) WHERE bail_jusqu_a IS NOT NULL;

CREATE INDEX projet_par_client ON ops.projet (client_id, cree_le DESC);

CREATE INDEX projet_a_purger
  ON ops.projet (purge_apres) WHERE purge_apres IS NOT NULL;
```

**`ops.objet` : l'inventaire R2.** Une seule table pour tout ce qui a des
octets — assets entrants, assets générés, contrats, pistes audio de
travail, master, aperçu. C'est ici que se lit la reprise : avant de
produire un artefact, on cherche la ligne ; si elle existe et que le
`sha256` correspond, on saute l'étape.

```sql
CREATE TABLE ops.objet (
  objet_id     uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  client_id    uuid NOT NULL REFERENCES ops.client (client_id),
  projet_id    uuid,                  -- NULL pour brand/ et polices
  role         ops.role_objet NOT NULL,
  cle          text,                  -- sous-clé : scene_03, logo, …
  version      integer NOT NULL DEFAULT 1,
  r2_key       text NOT NULL,
  mime         text NOT NULL,
  octets       bigint NOT NULL CHECK (octets > 0),
  sha256       char(64) NOT NULL,
  duree_ms     integer CHECK (duree_ms IS NULL OR duree_ms > 0),
  largeur      integer,
  hauteur      integer,
  -- copie jsonb des petits contrats, pour requêter sans passer par R2
  contenu      jsonb,
  cree_le      timestamptz NOT NULL DEFAULT now(),
  expire_le    timestamptz,           -- NULL = permanent (brand/, library/)

  FOREIGN KEY (projet_id, client_id)
    REFERENCES ops.projet (projet_id, client_id) ON DELETE CASCADE,
  CONSTRAINT objet_prefixe_client
    CHECK (r2_key LIKE 'clients/' || client_id::text || '/%'
        OR r2_key LIKE 'brand/'   || client_id::text || '/%'),
  CONSTRAINT objet_contenu_petit
    CHECK (contenu IS NULL OR pg_column_size(contenu) < 262144),
  CONSTRAINT objet_permanent_sans_projet
    CHECK (expire_le IS NOT NULL OR role IN ('brand_asset', 'police'))
);

CREATE UNIQUE INDEX objet_unique
  ON ops.objet (projet_id, role, coalesce(cle, ''), version)
  WHERE projet_id IS NOT NULL;

CREATE UNIQUE INDEX objet_r2_unique ON ops.objet (r2_key);
CREATE INDEX objet_a_expirer ON ops.objet (expire_le)
  WHERE expire_le IS NOT NULL;
```

`objet_prefixe_client` est la traduction en contrainte du préfixe R2 :
une clé mal préfixée ne s'écrit pas en base, donc l'inventaire ne peut
pas désigner l'espace d'un autre client.

### 2.4 `ops` — générations payantes

```sql
CREATE TABLE ops.generation (
  generation_id    uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  cle_generation   char(64) NOT NULL,     -- sha256, §5.2
  client_id        uuid NOT NULL REFERENCES ops.client (client_id),
  projet_id        uuid NOT NULL,
  fournisseur      text NOT NULL,         -- 'fal.ai', 'chatterbox', 'llm:…'
  modele           text NOT NULL,
  kind             text NOT NULL,         -- 'image', 'video', 'tts', 'llm'
  requete          jsonb NOT NULL,
  statut           ops.statut_generation NOT NULL DEFAULT 'reserve',
  cout_estime_c    integer NOT NULL CHECK (cout_estime_c >= 0),
  cout_reel_c      integer CHECK (cout_reel_c >= 0),
  ref_fournisseur  text,                  -- id côté fal.ai, pour réconcilier
  objet_id         uuid REFERENCES ops.objet (objet_id),
  tentatives       smallint NOT NULL DEFAULT 0,
  code_erreur      text,
  cree_le          timestamptz NOT NULL DEFAULT now(),
  fini_le          timestamptz,

  FOREIGN KEY (projet_id, client_id)
    REFERENCES ops.projet (projet_id, client_id) ON DELETE CASCADE,
  CONSTRAINT generation_cle_unique UNIQUE (cle_generation),
  CONSTRAINT generation_reussie_a_un_objet
    CHECK (statut <> 'reussie' OR objet_id IS NOT NULL)
);

CREATE INDEX generation_par_projet ON ops.generation (projet_id, cree_le);
CREATE INDEX generation_en_vol ON ops.generation (statut, cree_le)
  WHERE statut IN ('reserve', 'en_cours');
```

`generation_cle_unique` est le cœur de la promesse « un job relancé ne
repaie jamais » : l'insertion est la réservation. Une seconde tentative
avec la même clé viole l'unicité, lit la ligne existante et réutilise son
`objet_id`. Une ligne restée `reserve`/`en_cours` plus de 30 min est
réconciliée contre `ref_fournisseur` avant toute relance — on ne relance
jamais un appel payant sur la foi d'un timeout.

### 2.5 `ops` — marque, templates, voix

```sql
CREATE TABLE ops.brand_pack (
  brand_pack_id  uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  client_id      uuid NOT NULL REFERENCES ops.client (client_id),
  version        integer NOT NULL,
  payload        jsonb NOT NULL,        -- tokens, courbes, signature, sons
  statut         ops.statut_template NOT NULL DEFAULT 'brouillon',
  approuve_par   text,
  approuve_le    timestamptz,
  cree_le        timestamptz NOT NULL DEFAULT now(),
  CONSTRAINT brand_pack_version_unique UNIQUE (client_id, version),
  CONSTRAINT brand_pack_approuve_signe
    CHECK (statut <> 'approuve' OR (approuve_par IS NOT NULL
                                AND approuve_le IS NOT NULL))
);

ALTER TABLE ops.client
  ADD CONSTRAINT client_brand_pack_fk
  FOREIGN KEY (brand_pack_id) REFERENCES ops.brand_pack (brand_pack_id);

CREATE TABLE ops.template (
  template_id    uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  slug           text NOT NULL,
  version        integer NOT NULL,
  moteur         text NOT NULL,         -- 'hyperframes', 'remotion', …
  moteur_version text NOT NULL,
  statut         ops.statut_template NOT NULL DEFAULT 'brouillon',
  r2_key         text NOT NULL,         -- source figée du template (D15)
  sha256         char(64) NOT NULL,
  emplacements   jsonb NOT NULL,        -- slots déclarés (D34 / O5-C)
  scenes_min     smallint NOT NULL CHECK (scenes_min >= 1),
  scenes_max     smallint NOT NULL CHECK (scenes_max >= scenes_min),
  presets        text[] NOT NULL,       -- presets de mouvement admis (D14)
  approuve_par   text,
  approuve_le    timestamptz,
  cree_le        timestamptz NOT NULL DEFAULT now(),
  CONSTRAINT template_version_unique UNIQUE (slug, version),
  CONSTRAINT template_approuve_signe
    CHECK (statut <> 'approuve' OR (approuve_par IS NOT NULL
                                AND approuve_le IS NOT NULL))
);

CREATE INDEX template_catalogue ON ops.template (statut, slug, version DESC);
```

La « file de validation » de D15 est `statut = 'en_validation'` ; la
commande admin `style_approuver` la vide. Aucune table de file : une
colonne suffit. Les templates sont **figés** — un template approuvé n'est
jamais modifié, on crée `version + 1`. `ops.projet` retient
`(template_slug, template_version)`, donc un projet relancé six jours
plus tard rend le même montage même si le catalogue a avancé.

Le catalogue de voix, les messages neutres au client (§10.2) et les
limites du canal admin vivent dans une table de réglages, parce qu'ils
changent sans migration et n'ont ni contraintes propres ni relations :

```sql
CREATE TABLE ops.parametre (
  cle       text PRIMARY KEY,       -- 'catalogue_voix', 'messages_neutres', …
  valeur    jsonb NOT NULL,
  maj_le    timestamptz NOT NULL DEFAULT now(),
  maj_par   text NOT NULL
);
```

### 2.6 `ops` — bibliothèque audio et licences (D32)

```sql
CREATE TABLE ops.piste_audio (
  piste_id     uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  kind         ops.kind_piste NOT NULL,
  titre        text NOT NULL,
  r2_key       text NOT NULL,           -- library/audio/…
  sha256       char(64) NOT NULL,
  duree_ms     integer NOT NULL CHECK (duree_ms > 0),
  -- instant de l'attaque dans le fichier, mesuré à l'import : c'est lui
  -- qu'on cale sur l'ancre, pas le premier échantillon (§8.4)
  attaque_ms   integer NOT NULL DEFAULT 0 CHECK (attaque_ms >= 0),
  lufs         numeric(5,2),
  tags         text[] NOT NULL DEFAULT '{}',
  -- licence : obligatoire, sinon la piste n'entre pas dans la bibliothèque
  source       text NOT NULL,           -- 'pixabay', …
  licence      text NOT NULL,
  licence_url  text NOT NULL,
  releve_le    date NOT NULL,           -- date du relevé de licence
  cree_le      timestamptz NOT NULL DEFAULT now(),
  CONSTRAINT piste_r2_unique UNIQUE (r2_key),
  CONSTRAINT piste_licence_non_vide
    CHECK (length(licence) > 0 AND licence_url LIKE 'http%')
);

CREATE INDEX piste_par_tags ON ops.piste_audio USING gin (tags);
CREATE INDEX piste_par_kind ON ops.piste_audio (kind, duree_ms);

-- D32 : une musique n'est jamais réutilisée entre deux clients.
-- La clé primaire sur piste_id l'impose : une piste ne peut être
-- attribuée qu'une fois, et l'attribution nomme son client.
CREATE TABLE ops.attribution_musique (
  piste_id    uuid PRIMARY KEY REFERENCES ops.piste_audio (piste_id),
  client_id   uuid NOT NULL REFERENCES ops.client (client_id),
  attribue_le timestamptz NOT NULL DEFAULT now()
);

CREATE INDEX attribution_par_client ON ops.attribution_musique (client_id);

-- Trace d'usage : survit à la purge R2, part dans history à la clôture.
CREATE TABLE ops.usage_audio (
  projet_id     uuid NOT NULL,
  client_id     uuid NOT NULL,
  piste_id      uuid NOT NULL REFERENCES ops.piste_audio (piste_id),
  role          ops.role_audio NOT NULL,
  licence_snap  jsonb NOT NULL,        -- copie de la licence au moment du mix
  PRIMARY KEY (projet_id, piste_id, role),
  FOREIGN KEY (projet_id, client_id)
    REFERENCES ops.projet (projet_id, client_id) ON DELETE CASCADE
);
```

L'exclusivité de la musique est donc **structurelle** et sans course :
deux jobs concurrents qui élisent la même piste se départagent sur la clé
primaire, le perdant relit la table et en choisit une autre.
`licence_snap` est une copie, pas une jointure : si Pixabay change ses
conditions, la vidéo livrée garde la trace de ce qui était vrai le jour
du mix.

### 2.7 `ops` — messages WhatsApp

```sql
CREATE TABLE ops.message_entrant (
  wa_message_id  text PRIMARY KEY,      -- dédup structurelle des retries Meta
  client_id      uuid REFERENCES ops.client (client_id),  -- NULL si inconnu
  wa_from        text NOT NULL,
  projet_id      uuid,
  kind           text NOT NULL,         -- text, image, audio, document, button
  corps          text,
  r2_key         text,                  -- média copié dès réception
  brut           jsonb NOT NULL,
  recu_le        timestamptz NOT NULL DEFAULT now(),
  traite_le      timestamptz,
  code_erreur    text
);

CREATE INDEX entrant_a_traiter ON ops.message_entrant (recu_le)
  WHERE traite_le IS NULL;
CREATE INDEX entrant_par_client
  ON ops.message_entrant (client_id, recu_le DESC);

CREATE TABLE ops.message_sortant (
  envoi_id      uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  destinataire  text NOT NULL,          -- client ou numéro admin
  client_id     uuid REFERENCES ops.client (client_id),
  projet_id     uuid,
  kind          ops.kind_envoi NOT NULL,
  payload       jsonb NOT NULL,
  cle_envoi     text NOT NULL,          -- idempotence applicative
  statut        ops.statut_envoi NOT NULL DEFAULT 'en_file',
  tentatives    smallint NOT NULL DEFAULT 0,
  wa_message_id text,
  code_erreur   text,
  cree_le       timestamptz NOT NULL DEFAULT now(),
  envoye_le     timestamptz,
  CONSTRAINT sortant_cle_unique UNIQUE (cle_envoi)
);

CREATE INDEX sortant_a_envoyer ON ops.message_sortant (cree_le)
  WHERE statut = 'en_file';
```

`cle_envoi` est déterministe (par exemple
`projet_id:apercu_a_franco:tentative_2`) : une relance de job ne renvoie
pas deux fois le même aperçu à Franco ni deux fois la même livraison au
client. C'est le pendant, en sortie, de la dédup en entrée.

### 2.8 `ops` — exécutions, budgets d'état, plafonds

```sql
CREATE TABLE ops.execution_job (
  execution_id  uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  projet_id     uuid NOT NULL,
  client_id     uuid NOT NULL,
  kind          ops.kind_job NOT NULL,
  etat_depart   ops.etat_projet NOT NULL,
  nom_execution text,                   -- nom Cloud Run, pour les logs
  declencheur   text NOT NULL,          -- 'client', 'watchdog', 'admin'
  demarre_le    timestamptz NOT NULL DEFAULT now(),
  fini_le       timestamptz,
  ok            boolean,
  code_erreur   text,
  FOREIGN KEY (projet_id, client_id)
    REFERENCES ops.projet (projet_id, client_id) ON DELETE CASCADE
);

CREATE INDEX execution_par_projet ON ops.execution_job (projet_id, demarre_le);

-- Le watchdog est déclaratif : cette table EST sa configuration (§3.3).
CREATE TABLE ops.budget_etat (
  etat            ops.etat_projet PRIMARY KEY,
  duree_max_s     integer NOT NULL CHECK (duree_max_s > 0),
  au_depassement  ops.au_depassement NOT NULL,
  relances_max    smallint NOT NULL DEFAULT 1 CHECK (relances_max >= 0),
  -- délai au bout duquel le projet part en FAILED quoi qu'il arrive.
  -- NULL = jamais (le seul cas est PENDING_REVIEW : on n'abandonne pas
  -- un rendu déjà payé parce que Franco dort).
  abandon_apres_s integer CHECK (abandon_apres_s IS NULL
                                 OR abandon_apres_s > duree_max_s),
  compte_sla      boolean NOT NULL      -- entre dans l'horloge des 4 h ?
);

CREATE TABLE ops.plafond_cout (
  type_job        ops.type_job PRIMARY KEY,
  plafond_c       integer NOT NULL CHECK (plafond_c > 0),
  plafond_mois_c  integer NOT NULL CHECK (plafond_mois_c > 0),
  maj_le          timestamptz NOT NULL DEFAULT now(),
  maj_par         text NOT NULL
);
```

`plafond_mois_c` n'est pas une extension de D35 mais sa condition de
sûreté : un plafond par projet borne un projet, pas une boucle de projets
(voir §12, objection O-6).

### 2.9 `ops` — canal admin

```sql
CREATE TABLE ops.commande_admin (
  commande_id     uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  wa_message_id   text NOT NULL REFERENCES ops.message_entrant (wa_message_id),
  texte_brut      text NOT NULL,        -- expurgé du code de confirmation
  nom             ops.commande_admin_nom NOT NULL,
  parametres      jsonb NOT NULL,       -- validé par le schéma de la commande
  reformulation   text NOT NULL,        -- ce qui a été montré à Franco
  exige_code      boolean NOT NULL,
  statut          ops.statut_commande NOT NULL DEFAULT 'proposee',
  essais_code     smallint NOT NULL DEFAULT 0,
  cree_le         timestamptz NOT NULL DEFAULT now(),
  expire_le       timestamptz NOT NULL,
  execute_le      timestamptz,
  resultat        jsonb,
  CONSTRAINT commande_expire_apres CHECK (expire_le > cree_le),
  CONSTRAINT commande_executee_datee
    CHECK ((statut = 'executee') = (execute_le IS NOT NULL))
);

CREATE INDEX commande_en_attente ON ops.commande_admin (expire_le)
  WHERE statut = 'proposee';
```

Une seule commande `proposee` à la fois par numéro admin (vérifié à
l'insertion) : « oui » ne doit jamais être ambigu.

### 2.10 `history` — permanent, append-only

Aucune de ces tables n'est mise à jour ni supprimée. Interdiction
appliquée par les droits : le rôle applicatif n'a que `INSERT` et
`SELECT` sur `history`.

```sql
CREATE TABLE history.transition (
  id           bigserial PRIMARY KEY,
  projet_id    uuid NOT NULL,
  client_id    uuid NOT NULL,
  etat_avant   ops.etat_projet,
  etat_apres   ops.etat_projet NOT NULL,
  declencheur  text NOT NULL,          -- 'client', 'franco', 'job', 'watchdog'
  acteur       text,
  detail       jsonb NOT NULL DEFAULT '{}'::jsonb,
  duree_etat_s integer,                -- temps passé dans etat_avant
  le           timestamptz NOT NULL DEFAULT now()
);

CREATE INDEX transition_par_projet ON history.transition (projet_id, id);
CREATE INDEX transition_par_jour ON history.transition (le);

CREATE TABLE history.audit (
  id            bigserial PRIMARY KEY,
  le            timestamptz NOT NULL DEFAULT now(),
  acteur        text NOT NULL,          -- numéro admin ou 'systeme'
  source        text NOT NULL,          -- 'admin_wa' | 'systeme' | 'migration'
  action        text NOT NULL,
  objet_type    text NOT NULL,
  objet_id      text NOT NULL,
  valeur_avant  jsonb,
  valeur_apres  jsonb,
  commande_id   uuid,
  client_id     uuid
);

CREATE INDEX audit_par_objet ON history.audit (objet_type, objet_id, id);
CREATE INDEX audit_par_jour ON history.audit (le);

CREATE TABLE history.livraison (
  id             bigserial PRIMARY KEY,
  projet_id      uuid NOT NULL,
  client_id      uuid NOT NULL,
  type_job       ops.type_job NOT NULL,
  apercu_octets  bigint,
  master_octets  bigint,
  duree_ms       integer,
  lufs           numeric(5,2),
  dbtp           numeric(5,2),
  template_slug  text,
  template_version integer,
  hash_frames    char(64),
  valide_par     text NOT NULL,         -- 'franco' (D22), plus tard 'auto'
  valide_le      timestamptz NOT NULL,
  refus_avant    smallint NOT NULL DEFAULT 0,  -- calibration du futur juge
  livre_le       timestamptz NOT NULL,
  delai_sla_s    integer NOT NULL
);

CREATE TABLE history.generation (
  id            bigserial PRIMARY KEY,
  projet_id     uuid NOT NULL,
  client_id     uuid NOT NULL,
  fournisseur   text NOT NULL,
  modele        text NOT NULL,
  kind          text NOT NULL,
  statut        ops.statut_generation NOT NULL,
  cout_reel_c   integer,
  cree_le       timestamptz NOT NULL,
  archive_le    timestamptz NOT NULL DEFAULT now()
);

CREATE INDEX generation_hist_par_mois
  ON history.generation (client_id, cree_le);

CREATE TABLE history.message (
  id            bigserial PRIMARY KEY,
  projet_id     uuid,
  client_id     uuid,
  sens          text NOT NULL CHECK (sens IN ('entrant', 'sortant')),
  kind          text NOT NULL,
  corps         text,                   -- texte seul, jamais de média
  le            timestamptz NOT NULL
);

CREATE TABLE history.projet (
  projet_id     uuid PRIMARY KEY,
  client_id     uuid NOT NULL,
  type_job      ops.type_job NOT NULL,
  etat_final    ops.etat_projet NOT NULL,
  code_echec    text,
  cout_total_c  integer NOT NULL,
  brief         jsonb NOT NULL,
  storyboard    jsonb,                  -- contrats conservés, octets purgés
  montage_plan  jsonb,
  cree_le       timestamptz NOT NULL,
  clos_le       timestamptz NOT NULL
);
```

`history.projet` garde les **contrats** (storyboard, montage_plan) après
la purge des médias : c'est peu volumineux, c'est ce qui permettra de
calibrer le juge automatique promis par D22, et c'est la seule trace
utile en cas de litige au-delà de 7 jours.

### 2.11 Purge (D27)

Un passage quotidien dans `svc-conversation`, en trois temps, dans cet
ordre :

1. **Archiver** : projets `clos_le < now() - 7 jours` → `INSERT` dans
   `history.projet`, `history.generation`, `history.message` (les
   transitions, l'audit et les livraisons y sont déjà, écrits au fil de
   l'eau).
2. **Supprimer sur R2** les objets dont `expire_le < now()`, par préfixe
   de projet, en lisant `ops.objet`.
3. **Supprimer en base** les lignes `ops.projet` archivées ; les cascades
   emportent `ops.objet`, `ops.generation`, `ops.usage_audio`,
   `ops.execution_job`.

L'ordre importe : jamais de suppression R2 avant archivage réussi, et
jamais de suppression de l'inventaire avant celle des octets — sinon un
objet devient orphelin et invisible, donc payé pour toujours.

`expire_le` est calculé **à partir de la livraison**, pas de la création
(voir §12, objection O-4 : la fenêtre de correction de D26 et la
rétention de D27 font toutes deux 7 jours, ce qui est trop juste ; la
mise en œuvre retenue est `expire_le = clos_le + 10 jours` pour les
objets nécessaires à une correction — `composition`, `alignement`,
`voix_mix`, `asset_genere`, `master` — et `clos_le + 7 jours` pour le
reste).

---

## 3. Machine à états

### 3.1 Ce qu'un état garantit

Un état est un **contrat de reprise** : quand un projet est dans l'état
E, tout ce que les états antérieurs devaient produire existe sur R2 et
est inscrit dans `ops.objet`. La transition est donc toujours écrite
*en dernier*, dans une transaction qui contient aussi l'inscription des
artefacts :

```
BEGIN;
  INSERT INTO ops.objet (…);              -- artefacts déjà sur R2
  UPDATE ops.projet SET etat = 'ASSETS_READY', etat_depuis = now(),
         tentatives_etat = 0, sla_cumul_ms = sla_cumul_ms + …,
         bail_par = NULL, bail_jusqu_a = NULL
   WHERE projet_id = $1 AND etat = 'GENERATING';   -- garde optimiste
  INSERT INTO history.transition (…);
COMMIT;
```

La garde `AND etat = 'GENERATING'` rend la transition idempotente : deux
jobs concurrents (celui qu'on croyait mort et le relancé) ne peuvent pas
avancer deux fois. Le second voit `0 rows updated`, constate que l'état
attendu est déjà atteint, et se termine sans rien renvoyer au client.

Corollaire, qui est la consigne 4 : **l'ordre des opérations dans un état
va toujours du plus cher au moins cher, et chaque dépense est inscrite
avant la suivante.** Une relance ne repaie rien parce qu'elle retrouve
soit l'état suivant déjà atteint, soit les lignes `ops.generation` et
`ops.objet` de ce qui a déjà été payé.

### 3.2 Les états

| État | Propriétaire | Travail | Artefacts écrits (= reprise) | Durée max | Au dépassement | Abandon | Horloge SLA |
|---|---|---|---|---|---|---|---|
| `RECEIVED` | svc | Classifieur (D2) : type de job, périmètre, canal | `brief.type_job` | 120 s | relancer (×2) | 1 h | oui |
| `REJECTED` | — | terminal : message fixe déjà envoyé | — | — | — | — | — |
| `CLARIFYING` | svc | Slots + brouillon (D4), collecte des assets | `asset_client` sur R2, `brief.slots` | 12 h | relancer le client (×1) | 48 h | non |
| `BRIEF_READY` | svc | Storyboard (LLM) + budget de mots (R-SB-1) | `storyboard` v_n | 300 s | relancer (×2) | 1 h | oui |
| `STORYBOARD_PENDING_CLIENT` | client | attente de validation (D24) | — | 24 h | relancer le client (×1) | 48 h | non |
| `GENERATING` | job-produce + job-tts | assets payants, voix off, alignement | `asset_genere`, `voix_brute` (par scène), `alignement` | 30 min | relancer (×1) | 2 h | oui |
| `ASSETS_READY` | job-produce | Monteur, compilateur, lint, rendu, audio, mux, ffprobe | `montage_plan`, `composition`, `rendu_muet`, `voix_mix`, `effets_mix`, `musique_mix`, `mix_final`, `master`, `apercu`, `rapport_conformite` | 20 min | relancer (×1) | 1 h 30 | oui |
| `RENDERED_VERIFIED` | svc | envoi de l'aperçu à Franco (D22) | `message_sortant` (aperçu) | 300 s | relancer (×2) | 1 h | oui |
| `PENDING_REVIEW` | Franco | décision par boutons | — | 1 h | alerter (×3) | **jamais** | oui |
| `DELIVERED` | — | terminal pour le goût (D26) | `history.livraison` | — | — | — | — |
| `CORRECTION` | job-produce | correction factuelle ≤ 7 j (D26) | contrats v_n+1, `master`/`apercu` v_n+1 | 30 min | relancer (×1) | 2 h | oui |
| `FAILED` | — | terminal : message neutre envoyé, Franco alerté (D33) | `code_echec`, `detail_echec` | — | — | — | — |

Les valeurs sont celles qui peuplent `ops.budget_etat` ; elles se
changent par migration, pas par commande admin — un plafond de temps
n'est pas un réglage d'exploitation.

Justification des trois durées qui comptent : `GENERATING` à 30 min
couvre 3 à 6 générations d'images chez fal.ai **plus** le démarrage à
froid du Job GPU (image + poids, 2 à 4 min) et la synthèse ; `ASSETS_READY`
à 20 min laisse 4× la cible T0 de 5 min pour le rendu ; `PENDING_REVIEW`
à 1 h est un seuil de rappel, pas d'échec.

### 3.3 Transitions

| # | De → Vers | Déclencheur | Garde | Effets |
|---|---|---|---|---|
| T1 | ∅ → `RECEIVED` | message entrant d'un numéro en liste blanche | `client.statut = 'actif'` | création du projet, `purge_apres` provisoire |
| T2 | `RECEIVED` → `REJECTED` | classifieur : hors périmètre (D2, D25) | — | message fixe décrivant le service, `clos_le` |
| T3 | `RECEIVED` → `CLARIFYING` | classifieur : type de job reconnu | type ∈ {video, visuel, retouche} | premier message de clarification (brouillon par défaut) |
| T4 | `CLARIFYING` → `BRIEF_READY` | tous les slots requis remplis | assets minimaux présents sur R2 | — |
| T5 | `BRIEF_READY` → `STORYBOARD_PENDING_CLIENT` | storyboard écrit et valide | R-SB-1..4 passent | envoi du storyboard au client |
| T6 | `STORYBOARD_PENDING_CLIENT` → `BRIEF_READY` | correction demandée par le client | itérations < 3 | version de storyboard suivante |
| T7 | `STORYBOARD_PENDING_CLIENT` → `GENERATING` | validation du client (D24) | `plafond_cout` copié dans `budget_centimes`, plafond mensuel non atteint | exécution de `job-produce` |
| T8 | `GENERATING` → `ASSETS_READY` | assets + voix off + alignement durables | tous les `ops.generation` du plan sont `reussie` | — |
| T9 | `ASSETS_READY` → `RENDERED_VERIFIED` | `ffprobe` du master et de l'aperçu conformes | conformité binaire du §8.6 | — |
| T10 | `RENDERED_VERIFIED` → `PENDING_REVIEW` | aperçu envoyé à Franco | `message_sortant` accepté par Meta | — |
| T11 | `PENDING_REVIEW` → `ASSETS_READY` | Franco refuse | motif choisi dans une liste fermée | `tentatives_etat = 0`, le motif entre dans le prompt du Monteur |
| T12 | `PENDING_REVIEW` → `DELIVERED` | Franco valide | — | livraison double (D23), `history.livraison`, `clos_le` |
| T13 | `DELIVERED` → `CORRECTION` | erreur factuelle signalée ≤ 7 j (D26) | `now() < livre_le + 7 j` | rouvre le projet, budget **non** rechargé |
| T14 | `CORRECTION` → `RENDERED_VERIFIED` | nouveau master conforme | conformité binaire | — |
| T15 | `GENERATING`/`ASSETS_READY`/`RENDERED_VERIFIED`/`CORRECTION` → `FAILED` | erreur non rattrapable, ou watchdog après relance | `code_echec` renseigné | message neutre au client, alerte Franco (D33) |
| T16 | `CLARIFYING`/`STORYBOARD_PENDING_CLIENT` → `FAILED` | `abandon_apres_s` dépassé | — | `code_echec = 'ABANDON_CLIENT'`, aucune alerte P1 |
| T17 | `FAILED` → `etat_avant_echec` | commande admin « relancer un job » | `etat_avant_echec` non nul, cause traitée | reprise sans repaiement. **Cette transition n'est pas dans le diagramme du document d'état** : voir §12, objection O-2 |

**T11 est le point sensible** : un refus de Franco revient en
`ASSETS_READY`, donc au Monteur — pas en `GENERATING`. Les assets et la
voix off sont conservés et ne sont **jamais** repayés. Seuls le montage,
le rendu et le mixage sont refaits, avec le motif de refus ajouté au
prompt du Monteur. Si le motif de refus porte sur un asset (« la photo
produit est floue »), la seule issue est un nouveau projet ou une
génération explicitement autorisée par la commande admin — ce qui
consomme le budget restant du projet.

**T13** ne recharge pas le budget : une correction factuelle est à notre
charge (D26), donc elle doit tenir dans ce qui reste, sinon elle alerte
Franco. C'est une décision de conception, pas une contrainte technique :
elle empêche qu'un enchaînement de « corrections » double le coût d'un
projet sans que personne ne le voie.

### 3.4 Horloge de service et délai de 4 h (D36)

Le délai de 4 h ne peut pas être mesuré de bout en bout, sinon un client
qui met deux jours à valider son storyboard nous met en faute. Chaque
projet porte donc `sla_cumul_ms`, qui **n'accumule que le temps passé
dans les états dont nous sommes propriétaires** (colonne `compte_sla`) :
`RECEIVED`, `BRIEF_READY`, `GENERATING`, `ASSETS_READY`,
`RENDERED_VERIFIED`, `PENDING_REVIEW`, `CORRECTION`. Les deux états
d'attente client (`CLARIFYING`, `STORYBOARD_PENDING_CLIENT`) sont
exclus, et le client est prévenu à l'entrée dans ces états que le délai
repart de sa réponse.

L'incrément est fait à chaque transition, dans la transaction de §3.1 :
`sla_cumul_ms += (now() - etat_depuis)` si l'état quitté compte.

`PENDING_REVIEW` compte, lui, dans l'horloge : c'est **notre** attente,
pas celle du client. Et c'est exactement ce qui rend D22 et D36
incompatibles la nuit (§12, objection O-1, et §13).

### 3.5 Watchdog

Une boucle dans `svc-conversation`, toutes les **60 s**, sans état
propre : tout ce dont elle a besoin est dans `ops.projet` et
`ops.budget_etat`. Elle exécute cinq contrôles dans cet ordre, le plus
spécifique d'abord.

**1. Bail expiré — le job est mort.** Un job renouvelle son bail toutes
les 60 s (`bail_jusqu_a = now() + 3 min`). Un bail périmé signifie une
exécution perdue, pas une exécution lente : on relance immédiatement
sans attendre `duree_max_s`. C'est ce qui ramène le temps de
récupération d'un crash de 20 min à 3 min.

```sql
-- prédicat, pas une implémentation
SELECT projet_id FROM ops.projet
 WHERE etat IN ('GENERATING','ASSETS_READY','CORRECTION')
   AND bail_jusqu_a IS NOT NULL AND bail_jusqu_a < now()
 FOR UPDATE SKIP LOCKED;
```

**2. Durée maximale dépassée.**
`now() - etat_depuis > budget_etat.duree_max_s` :
- `au_depassement = 'relancer'` et `tentatives_etat < relances_max` →
  libère le bail, `tentatives_etat += 1`, relance (`job-produce` pour les
  états de job, reprise interne pour les états de service), écrit
  `ops.execution_job` avec `declencheur = 'watchdog'` ;
- `au_depassement = 'relancer'` et `tentatives_etat >= relances_max` →
  `FAILED` (T15) : message neutre au client, alerte P1 à Franco ;
- `au_depassement = 'alerter'` → rappel (au client pour les états
  d'attente client, à Franco pour `PENDING_REVIEW`), `tentatives_etat += 1`,
  au plus `relances_max` fois. **Jamais de `FAILED`.**

**3. Abandon.** `abandon_apres_s` non nul et dépassé → `FAILED` avec
`code_echec = 'ABANDON_CLIENT'` ou `'ABANDON_TECHNIQUE'`. Le premier
n'alerte pas Franco en P1 (ce n'est pas une panne), il entre dans le
digest quotidien.

**4. Alerte de service à T+3 h.** `sla_cumul_ms + (now() - etat_depuis)`
> 3 h, état non terminal, `sla_alerte_envoyee = false` → alerte Franco
avec l'état courant et la commande admin suggérée, puis
`sla_alerte_envoyee = true`. Une seule fois par projet.

**5. Réconciliations.** Trois balayages courts, qui empêchent chacun une
perte d'argent ou de message :
- `ops.generation` en `reserve`/`en_cours` depuis > 30 min → interroger
  le fournisseur par `ref_fournisseur` avant toute relance ; si l'appel a
  abouti, on récupère le résultat et on ne repaie pas ; sinon
  `abandonnee` et le budget réservé est rendu ;
- `ops.message_sortant` en `en_file` → envoi avec reprise exponentielle
  (2 s, 8 s, 30 s, 2 min, 10 min), `echoue` à 5 tentatives, alerte P1 si
  le message était une livraison ;
- `ops.commande_admin` `proposee` et expirée → `expiree`.

**Qui surveille le watchdog ?** Rien, dans le système. Si
`svc-conversation` tombe, plus aucune alerte ne part — c'est le seul
point unique de défaillance de l'architecture. Il est couvert *hors*
système : un contrôle de disponibilité Cloud Monitoring sur
`GET /sante` toutes les 5 min, avec politique d'alerte vers l'e-mail et
le SMS de Franco. `/sante` renvoie 503 si la dernière boucle de watchdog
a plus de 5 min, ce qui couvre aussi le cas « le service répond mais la
boucle est bloquée ».

### 3.6 Ce que coûte une relance, état par état

C'est la vérification de la consigne 4, cas par cas.

| Relance depuis | Repaie | Ne repaie pas |
|---|---|---|
| `RECEIVED`, `CLARIFYING`, `BRIEF_READY` | un appel LLM (centimes) | — |
| `GENERATING` | uniquement les générations sans ligne `reussie` | les assets déjà produits, et toute scène dont la `voix_brute` existe |
| `ASSETS_READY` | un appel LLM (Monteur), le CPU de rendu et de mixage | **toutes** les générations, la voix off, l'alignement |
| `RENDERED_VERIFIED` | un envoi WhatsApp | le rendu et le mixage |
| `PENDING_REVIEW` | rien | rien |
| `CORRECTION` | le Monteur, le rendu, le mixage | les générations et la voix off, sauf texte à resynthétiser (§8.8) |

Le seul cas où une relance coûte du GPU est la correction d'un texte de
voix off : on resynthétise **la scène concernée uniquement** (§8.2 :
synthèse par scène), pas le script entier.

---

## 4. Services, Jobs et flux

### 4.1 `svc-conversation` (Cloud Run Service)

Une seule instance, toujours chaude, CPU toujours alloué,
`max-instances=2` (pour ne pas perdre le webhook pendant un
déploiement ; le watchdog et la purge sont protégés par
`pg_try_advisory_lock`, donc une seconde instance ne les double pas).

Quatre entrées HTTP et deux boucles :

| Entrée | Rôle | Contrainte |
|---|---|---|
| `POST /webhook` | réception Meta | vérifie `X-Hub-Signature-256` (HMAC-SHA256 du corps brut, comparaison à temps constant), insère `ops.message_entrant`, répond **200 en moins d'une seconde**, ne traite rien avant d'avoir répondu |
| `GET /webhook` | vérification Meta (`hub.challenge`) | — |
| `GET /sante` | contrôle de disponibilité | 503 si watchdog en retard |
| `POST /interne/job-fini` | notification de fin de `job-produce` | OIDC, service account dédié |

Boucles internes : **watchdog** (60 s, §3.5) et **maintenance**
quotidienne (purge §2.11, archivage, relevé des dépenses du mois).

Le traitement d'un message entrant est déclenché *après* la réponse
HTTP, dans la même instance. Ordre imposé, et non négociable :

1. **Copier le média sur R2** s'il y en a un. L'URL de téléchargement
   Meta expire en quelques minutes et il n'y a pas de boîte de
   réception : ce qui n'est pas copié est perdu. Cette étape passe avant
   toute logique, avant même de savoir si le numéro est en liste
   blanche — on jette ensuite si nécessaire.
2. **Aiguiller** : numéro admin (§9) → liste blanche (D25) → classifieur.
3. **Traiter** l'état courant du projet.
4. `traite_le = now()` sur `ops.message_entrant`.

Si l'instance meurt entre 1 et 4, le message reste `traite_le IS NULL` et
la boucle de maintenance le reprend. Le média, lui, est déjà sauvé.

### 4.2 `job-produce` (Cloud Run Job, CPU)

Image : Node 22, FFmpeg 7 (avec `libfdk_aac` ou `aac` selon la licence
retenue), Chrome headless, polices du Brand Pack installées dans l'image
— **aucune police téléchargée à l'exécution** (déterminisme).

Paramètres : `PROJET_ID`, `ETAT_ATTENDU`, `EXECUTION_ID`.
`--task-timeout=45m`, `--max-retries=0` (les relances sont décidées par
le watchdog, pas par Cloud Run : lui ne sait pas si l'échec est
rattrapable et relancerait un appel payant).

Le job commence par **prendre le bail** (`UPDATE … WHERE projet_id = $1
AND etat = $2 AND (bail_jusqu_a IS NULL OR bail_jusqu_a < now())`) ; zéro
ligne mise à jour ⇒ il sort immédiatement en succès. C'est ce qui rend
inoffensif un double déclenchement (client + watchdog).

Trois pipelines disjoints après le bail, selon `type_job` :

- **`video`** : §5 à §8. C'est le seul qui appelle `job-tts`.
- **`visuel`** : génération d'image, composition d'un visuel statique par
  le même moteur de rendu (une frame), lint de zone de sécurité, export
  JPEG/PNG ≤ 5 Mo sans transparence, livraison.
- **`retouche`** : pipeline séparé (D28) — pas de storyboard, pas de
  Monteur, pas de template. Entrée = photo du client + consigne ; sortie
  = image retouchée. Il partage avec les autres la prise de bail,
  l'adaptateur de génération, la table `ops.generation`, les contrôles de
  format et la livraison. Il a ses propres états utiles
  (`RECEIVED → CLARIFYING → GENERATING → PENDING_REVIEW → DELIVERED`) et
  ne passe jamais par `ASSETS_READY`.

### 4.3 `job-tts` (Cloud Run Job, GPU L4)

Image : Python, Chatterbox Multilingual, **poids du modèle inclus dans
l'image** (pas de téléchargement au démarrage : déterminisme et
démarrage à froid), aligneur forcé embarqué. Région `europe-west4` ou
`europe-west1` selon la disponibilité L4, `--task-timeout=15m`,
`--max-retries=0`.

Paramètres : `PROJET_ID`, `SCENES` (liste d'identifiants de scènes à
synthétiser — vide = toutes celles qui manquent).

Entrée/sortie par R2 et Postgres uniquement, **jamais par HTTP** : le job
lit le `storyboard` (script voix off, voix, prononciations), écrit les
`voix_brute` par scène, le `voix_mix` et l'`alignement`, inscrit ses
lignes `ops.objet` et `ops.generation`, puis sort. Il n'a le droit
d'écrire que ces rôles-là, et il ne touche jamais `ops.projet.etat` :
c'est `job-produce` qui décide de la transition. Un seul écrivain d'état
par projet, c'est ce qui permet de ne pas avoir de verrou distribué.

**Qui attend qui.** `job-produce` déclenche `job-tts` par l'API Cloud Run
Admin et **attend sa fin** en interrogeant l'exécution toutes les 10 s.
La variante « `job-tts` rappelle `job-produce` à la fin » économiserait
quelques minutes de CPU à 2 projets par jour et ajouterait un point de
reprise, un rappel HTTP et une transition. Elle est écartée. En revanche
`job-produce` **lance les générations d'images en parallèle de la
synthèse** : ce sont les deux dépenses les plus lentes et elles sont
indépendantes.

### 4.4 Flux entre unités

| Flux | Transport | Idempotence assurée par |
|---|---|---|
| Meta → `svc` | HTTPS + HMAC | PK `wa_message_id` |
| `svc` → Meta | HTTPS + token permanent (System User) | `cle_envoi` unique |
| `svc` → `job-produce` | API Cloud Run Admin (`run`), OIDC | bail + garde d'état |
| `job-produce` → `job-tts` | API Cloud Run Admin (`run`), OIDC | `cle_generation` + `ops.objet` |
| `job-*` → `svc` | **rien** : uniquement Postgres | transition gardée |
| `job-*` ↔ R2 | S3 API, préfixe par client | `sha256` + `objet_r2_unique` |
| fal.ai, LLM | HTTPS via adaptateur | `cle_generation` |

Il n'y a **aucun appel HTTP d'un job vers le service** dans le chemin
nominal (`/interne/job-fini` n'est qu'une accélération : sans lui, le
watchdog verrait l'état changer dans les 60 s). Les jobs communiquent par
la base. C'est la simplification qui supprime le besoin d'une file de
messages, d'un bus d'événements et de leur supervision.

### 4.5 Secrets et identités

Un compte de service par unité, droits minimaux :
`svc-conversation` peut exécuter les deux jobs et lire/écrire `ops` +
insérer dans `history` ; `job-produce` peut exécuter `job-tts` ;
`job-tts` n'a aucun droit d'exécution. Secret Manager porte : token
permanent Meta, `app_secret` Meta (vérification de signature), clé
fal.ai, clé LLM, identifiants R2, empreinte du code de confirmation admin
(§9.3), URL Postgres. Aucun secret en variable d'environnement en clair,
aucune clé dans une image.

---

## 5. Les deux adaptateurs

Un adaptateur existe pour une seule raison : **isoler une décision non
prise**. Le moteur de rendu est un pari (D7, à tester en T0) ; le
fournisseur de génération est un poste de coût qui changera. Aucun des
deux adaptateurs ne décide quoi que ce soit : ils exécutent un contrat
déjà entièrement résolu. S'ils choisissent, le contrat en amont est
incomplet (§1.3).

### 5.1 Adaptateur de moteur de rendu

```
interface AdaptateurRendu {
  capacites() -> Capacites
  verifier(composition, dossier_assets) -> RapportLint
  rendre(composition, options) -> ResultatRendu
}

Capacites {
  moteur            : text            // 'hyperframes' | 'revideo' | 'remotion'
  version           : text
  fps_supportes     : int[]
  taille_max        : {l: int, h: int}
  lint_dom          : bool            // D16 : le DOM est-il inspectable ?
  emplacements      : bool            // D34 : templates à slots déclarés ?
  polices_requises  : text[]
  sorties           : text[]          // 'mp4_h264', 'png_sequence'
}

Options {
  sortie        : chemin
  fps           : 30                  // fixe, imposé par Meta
  taille        : {l: 1080, h: 1920}  // D12
  graine        : int                 // consignée dans le résultat
  timeout_s     : int
  sans_reseau   : true                // toujours
}

ResultatRendu {
  chemin_video  : chemin              // MUETTE — voir ci-dessous
  duree_ms      : int
  frames        : int
  hash_frames   : sha256              // hash des hashs de frames, ordonné
  polices_ok    : bool
  journal       : text
  mesures       : {temps_s, pic_memoire_mo}
}

Erreurs : E_ASSET_MANQUANT · E_POLICE_MANQUANTE · E_EMPLACEMENT_INCONNU
        · E_HORS_ZONE_SECURITE · E_DEBORDEMENT_TEXTE · E_TIMEOUT
        · E_NON_DETERMINISTE · E_MOTEUR
```

Cinq règles, qui sont le contrat réel :

1. **La sortie est muette.** Le moteur rend l'image, jamais le son. Tout
   l'audio est assemblé par FFmpeg (§8), donc la garantie de -14 LUFS /
   -1 dBTP ne dépend pas du moteur, et changer de moteur ne remet pas en
   jeu la conformité sonore. C'est la décision qui rend D7 réversible à
   bon marché.
2. **Aucun réseau pendant la capture.** Les assets sont sur disque local,
   les polices sont dans l'image, `document.fonts.check()` est vérifié
   avant la première frame. Une police absente est une erreur, pas un
   fallback silencieux — un fallback change le rendu sans le dire.
3. **Déterminisme vérifiable** : mêmes `composition` + mêmes assets +
   même `version` du moteur ⇒ même `hash_frames`. C'est le critère C de
   T0, et c'est aussi ce qui permet de détecter une régression de moteur
   sans regarder une vidéo.
4. **`verifier()` avant `rendre()`** : le lint (D16) tourne sur le DOM
   pré-rendu et vérifie la zone de sécurité unique (14 % / 35 % / 6 % /
   10 %), le débordement de texte, les emplacements inconnus. S'il
   échoue, on ne rend pas. Si `capacites().lint_dom` est faux, D16 n'est
   pas applicable et le moteur est **refusé** en production (§12,
   objection O-5).
5. **`rendre()` ne lit ni la base ni R2.** Il reçoit un dossier et une
   composition. C'est ce qui permet de l'exécuter à la main en T1, sans
   base.

### 5.2 Adaptateur de génération

```
interface AdaptateurGeneration {
  estimer(demande) -> {cout_c: int, latence_p50_s: int}
  produire(demande, contexte) -> ResultatGeneration     // idempotent
  reconcilier(cle_generation) -> StatutGeneration
}

Demande {
  kind        : 'image' | 'image_animee' | 'video_courte' | 'retouche'
  modele      : text
  prompt      : text?
  entrees     : [{objet_id, sha256}]
  parametres  : {graine, taille, …}     // normalisés, clés triées
  variante    : int                     // 0 par défaut ; +1 = « refais-le »
}

Contexte { client_id, projet_id }

ResultatGeneration {
  cle_generation : sha256
  objet_id       : uuid
  r2_key         : text
  sha256         : sha256
  cout_reel_c    : int
  deja_paye      : bool            // true = servi par l'idempotence
  ref_fournisseur: text
}

Erreurs : E_BUDGET · E_QUOTA_FOURNISSEUR · E_FOURNISSEUR_INDISPO
        · E_REFUS_CONTENU · E_ENTREE_INVALIDE · E_TIMEOUT
```

**La clé d'idempotence.**

```
cle_generation = sha256( json_canonique({
    client_id, projet_id, fournisseur, modele, kind,
    prompt, entrees[].sha256 (triés), parametres, variante,
    version_adaptateur
}) )
```

- `client_id` y est **par isolation** (D30) : deux clients qui demandent
  la même image paient chacun la leur. Un cache commun serait une fuite
  d'un client vers l'autre.
- `projet_id` y est **par honnêteté** : la clé protège les relances d'un
  projet, elle ne prétend pas être un cache inter-projets. Un cache
  inter-projets serait de toute façon vide la plupart du temps (R2 purge
  à 7 jours, les assets d'entrée diffèrent) et coûterait un mécanisme
  d'expiration.
- `variante` est le seul moyen de repayer volontairement, et il est
  toujours déclenché par un humain (refus de Franco, commande admin).

**Séquence de `produire()`** — l'ordre est la garantie :

1. calculer `cle_generation` ;
2. `SELECT` : si `statut = 'reussie'`, renvoyer l'objet existant avec
   `deja_paye = true`. **Aucun appel réseau.** Si `reserve`/`en_cours`,
   appeler `reconcilier()` ;
3. transaction unique : `UPDATE ops.projet SET budget_restant =
   budget_restant - cout_estime_c` **puis** `INSERT ops.generation (…,
   'reserve')`. La contrainte `budget_restant >= 0` fait échouer la
   transaction avant tout appel → `E_BUDGET`. **Le plafond est
   décrémenté avant l'appel** (D35) parce qu'il l'est dans la même
   transaction que la réservation ;
4. appel fournisseur ; `ref_fournisseur` écrit dès réception de
   l'identifiant, avant d'attendre le résultat — sans quoi un timeout
   laisse un appel payé et anonyme ;
5. téléchargement, `sha256`, écriture R2 sous le préfixe du client,
   `INSERT ops.objet`, `UPDATE ops.generation → 'reussie'` avec
   `cout_reel_c` (D10 : écrit sur R2 **et** en base avant l'étape
   suivante) ;
6. si `cout_reel_c < cout_estime_c`, la différence est rendue au budget.
   L'estimation est le **prix maximal** du modèle appelé, jamais une
   moyenne : ainsi le budget n'est jamais dépassé après coup, et la
   contrainte de la base n'a jamais à être contournée.

**Reprises** : uniquement sur erreur réseau, 5xx ou timeout, deux fois,
2 s puis 8 s. Jamais sur 4xx. Jamais de nouvelle soumission sans
`reconcilier()` préalable quand `ref_fournisseur` existe — c'est la seule
façon de ne pas payer deux fois un appel qui a réussi côté fournisseur et
échoué côté réseau.

**D11 dans l'adaptateur** : `kind = 'image_animee'` ne produit pas de
vidéo chez le fournisseur. Il produit une image, et c'est le moteur de
rendu qui l'anime (parallaxe, punch-in, masques). `video_courte` existe
dans le contrat mais n'est pas appelé en v1 : le vocabulaire du Monteur
(§7.2) ne contient aucun terme qui s'y résolve. Le jour où il le
contiendra, le plafond par type de job sera à revoir — une vidéo générée
coûte un ordre de grandeur de plus qu'une image.

---

## 6. Contrats de données : amendements

Cinq contrats sont en jeu. Le document d'état les déclare « à réécrire »
tout en validant les versions existantes ; conformément à la consigne 2,
**je n'amende que les trois endroits qu'il exige**, et je marque chaque
amendement.

| Contrat | Traitement ici |
|---|---|
| `storyboard.schema.json` | **AMENDEMENT A1** : durées cibles + script voix off |
| `composition.schema.json` | **AMENDEMENT A2** : pistes audio |
| `montage_plan.schema.json` | **NOUVEAU — A3** (§7.2) |
| `brand_pack.schema.json` | inchangé ici ; les clés lues par le compilateur sont listées §7.3 |
| `template.schema.json` | inchangé ici ; les emplacements déclarés sont lus tels quels (D34) |

Les fichiers de contrats existants ne m'ont pas été transmis avec le
document d'état : les amendements ci-dessous sont donc écrits au niveau
des **champs**, et les noms des champs préexistants sont à confirmer à
l'application (§13, B9).

### AMENDEMENT A1 — `storyboard.schema.json`

*Motif : D20. L'audio devient l'horloge, donc les durées du storyboard
cessent d'être normatives ; et le script de voix off doit exister avant
la génération pour que le client valide ce qu'il va entendre (D24).*

**Champs renommés**

| Avant | Après | Effet |
|---|---|---|
| `scenes[].duree_ms` | `scenes[].duree_cible_ms` | valeur **indicative**. Le compilateur ne l'utilise que comme borne de vraisemblance (règle C-3) et comme repère pour le client. |
| `duree_totale_ms` | `duree_cible_totale_ms` | idem. Contrainte conservée : ≤ 30 000. |

Le renommage est volontairement visible : un champ qui s'appelle encore
`duree_ms` serait lu comme une consigne par le premier lecteur, humain ou
LLM.

**Champs ajoutés**

```jsonc
{
  "voix_id": "string",                  // AJOUTÉ — du catalogue ops.parametre
  "langue": "fr | en",                  // AJOUTÉ
  "budget_mots": {                      // AJOUTÉ — calculé, non rédigé
    "debit_mots_par_s": 2.6,            // français, à recalibrer après T0b
    "mots_total": 0,
    "mots_max": 0
  },
  "scenes": [
    {
      "script_voix_off": {              // AJOUTÉ — obligatoire si voix off
        "texte": "string",              // ce qui sera prononcé, mot pour mot
        "prononciations": [             // graphies à forcer (marques, sigles)
          { "graphie": "string", "phonetique": "string" }
        ],
        "pauses": [                     // respirations voulues par l'auteur
          { "apres_mot_index": 0, "duree_ms": 0 }
        ],
        "muet": false                   // scène sans voix (pur visuel)
      }
    }
  ]
}
```

**Règles de validation ajoutées** (bloquantes, avant envoi au client) :

- **R-SB-1** : `mots_total / debit_mots_par_s + Σ pauses ≤ 28 s`. La
  marge de 2 s couvre l'amorce, la chute et les pads inter-scènes. Un
  script qui ne tient pas est renvoyé au rédacteur, **avant** toute
  dépense — c'est ce qui empêche de découvrir à la synthèse qu'on dépasse
  les 30 s.
- **R-SB-2** : toute scène a soit un `script_voix_off.texte` non vide,
  soit `muet: true`. Pas de troisième cas.
- **R-SB-3** : `voix_id` appartient au catalogue de voix actif.
- **R-SB-4** : aucun `ms`, `px`, `#hex` ni nom d'animation ailleurs que
  dans `duree_cible_ms` et `pauses[].duree_ms` (contrôle lexical sur les
  champs de texte). C'est la frontière de couche, vérifiée
  mécaniquement.

### AMENDEMENT A2 — `composition.schema.json`

*Motif : D19 et D20. La composition est la seule chose que voient le
moteur et FFmpeg ; elle doit donc porter l'audio entièrement résolu, y
compris l'enveloppe de ducking.*

**Champ ajouté : `pistes_audio`** (obligatoire, `minItems: 1` dès qu'il
y a de la voix off)

```jsonc
"pistes_audio": [
  {
    "id": "voix",                      // unique dans la composition
    "role": "voix | effets | musique",
    "segments": [
      {
        "source_r2": "clients/…/voix_scene_03.wav",
        "sha256": "…",
        "debut_ms": 4820,              // position absolue sur la timeline
        "offset_source_ms": 0,         // point d'entrée dans le fichier
        "duree_ms": 2140,
        "gain_db": -3.0,
        "fade_in_ms": 0,
        "fade_out_ms": 40,
        "licence_ref": "piste_id|null" // null pour la voix synthétisée
      }
    ],
    "enveloppe_gain": [                // ducking : valeurs absolues, pas de
      { "t_ms": 4700, "gain_db": 0.0 },//  compresseur — voir §8.5
      { "t_ms": 4820, "gain_db": -9.0 },
      { "t_ms": 7260, "gain_db": -9.0 },
      { "t_ms": 7560, "gain_db": 0.0 }
    ],
    "boucle": false                    // musique : boucle jusqu'à duree_ms
  }
]
```

**Champ ajouté : `audio`** (obligatoire)

```jsonc
"audio": {
  "cible_lufs": -14.0,
  "cible_dbtp": -1.0,
  "canaux": 2,                         // stéréo exigé par Meta
  "debit_aac_kbps": 128                // minimum exigé par Meta
}
```

**Champs modifiés**

| Champ | Avant | Après |
|---|---|---|
| `duree_ms` | valeur libre | **dérivée** : `max(fin de la piste voix, fin de la dernière scène)`, arrondie à la frame (règle C-7). Reste dans le fichier — le moteur en a besoin — mais toute autre valeur que la valeur dérivée est un rejet du validateur. |
| `fps` | nombre | **constante 30**, et `CHECK` explicite : Meta exige une fréquence fixe. |

**Règles de validation ajoutées** :

- **R-CO-1** : tout `segments[].source_r2` existe dans `ops.objet` avec
  le `sha256` indiqué.
- **R-CO-2** : toute piste `musique` ou `effets` a un `licence_ref` non
  nul qui résout dans `ops.piste_audio`. Une piste sans licence ne se
  monte pas (contrainte dure : une musique sans licence commerciale fait
  couper la pub).
- **R-CO-3** : `enveloppe_gain` est monotone en `t_ms`, commence et
  finit à `0.0 dB`, et n'existe que sur la piste `musique`.
- **R-CO-4** : `duree_ms ≤ 30 000`.
- **R-CO-5** : les pistes `voix` ne se chevauchent jamais entre elles.

### A3 — `montage_plan.schema.json` (nouveau)

Le schéma complet est au §7.2, avec le vocabulaire qu'il ferme.

---

## 7. Le Monteur et le compilateur

### 7.1 Partage des rôles

D21 coupe la décision en deux : un LLM choisit **dans des listes
fermées**, un compilateur déterministe transforme ces choix en valeurs.
La ligne de partage se lit en trois interdits.

**Le Monteur ne voit pas de temps.** Son prompt contient, par scène, la
liste des mots du script avec leur **index**, jamais leur horodatage.
C'est ainsi qu'on empêche à la source qu'il raisonne en millisecondes :
il ne peut pas, il n'a pas les nombres. Les durées viennent de
l'alignement (D20) et de lui seul.

**Le Monteur ne choisit pas la signature de mouvement.** D14 la fixe
**par client**, dans le Brand Pack, parmi 3 ou 4 presets. Le Monteur ne
peut que la moduler scène par scène avec `intensite`. Cela retire un
terme au vocabulaire et garantit qu'un client se reconnaît d'une vidéo à
l'autre.

**Le Monteur ne déclenche aucune dépense.** Il choisit parmi des assets
qui **existent déjà** : ceux du client et ceux générés en `GENERATING`
d'après le storyboard que le client a validé (D24). `b_roll:
"image_generee"` désigne une image déjà produite et inscrite dans
`ops.objet`, pas une image à produire. Conséquence : `ASSETS_READY` ne
coûte jamais de génération, donc un refus de Franco (T11) est gratuit en
API.

**Si le Monteur échoue, rien ne bloque.** Deux reprises avec les erreurs
du validateur en retour ; si le plan est encore invalide, le compilateur
utilise un **plan par défaut déterministe** (coupe franche partout,
`intensite: moyenne`, un effet sonore par transition, aucune emphase, CTA
sur la dernière scène). La vidéo est plate mais conforme, et Franco la
voit en revue. Un projet ne part jamais en `FAILED` à cause du Monteur.

### 7.2 A3 — `montage_plan.schema.json` (nouveau)

```jsonc
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "montage_plan.schema.json",
  "type": "object",
  "additionalProperties": false,
  "required": ["version", "storyboard_ref", "template", "musique", "scenes"],
  "properties": {
    "version": { "const": 1 },

    "storyboard_ref": {
      "type": "object",
      "additionalProperties": false,
      "required": ["objet_id", "sha256"],
      "properties": {
        "objet_id": { "type": "string", "format": "uuid" },
        "sha256":   { "type": "string", "pattern": "^[0-9a-f]{64}$" }
      }
    },

    "template": {
      "type": "object",
      "additionalProperties": false,
      "required": ["slug", "version"],
      "properties": {
        "slug":    { "type": "string" },      // du catalogue approuvé
        "version": { "type": "integer", "minimum": 1 }
      }
    },

    "musique": {
      "type": "object",
      "additionalProperties": false,
      "required": ["ambiance", "intensite"],
      "properties": {
        "ambiance":  { "enum": ["aucune", "energique", "calme",
                                "epique", "chaleureux", "neutre"] },
        "intensite": { "enum": ["faible", "moyenne", "forte"] }
      }
    },

    "scenes": {
      "type": "array", "minItems": 1, "maxItems": 12,
      "items": {
        "type": "object",
        "additionalProperties": false,
        "required": ["scene_id", "fonction", "intensite",
                     "transition_entree", "affichage_texte", "b_roll"],
        "properties": {

          "scene_id": { "type": "string" },   // identique au storyboard

          "fonction": { "enum": ["accroche", "probleme", "solution",
                                 "preuve", "demo", "prix", "cta"] },

          "intensite": { "enum": ["faible", "moyenne", "forte"] },

          "cadence":   { "enum": ["lente", "moyenne", "rapide"],
                         "default": "moyenne" },

          "transition_entree": {
            "enum": ["coupe", "fondu", "glissement_gauche",
                     "glissement_droite", "glissement_haut",
                     "glissement_bas", "zoom_avant", "flash",
                     "masque_forme"]
          },

          "affichage_texte": {
            "enum": ["aucun", "titre", "mot_cle", "phrase_courte",
                     "chiffre", "sous_titre_integral"]
          },

          "b_roll": {
            "enum": ["aucun", "photo_produit", "photo_contexte",
                     "image_generee", "capture_ecran", "logo_plein_cadre"]
          },

          "emphases": {
            "type": "array", "maxItems": 3,
            "items": {
              "type": "object",
              "additionalProperties": false,
              "required": ["effet", "ancre"],
              "properties": {
                "effet": { "enum": ["surlignage", "agrandissement",
                                    "secousse", "apparition_lettres",
                                    "soulignement", "encadre"] },
                "ancre": { "enum": ["debut_scene", "fin_scene",
                                    "sur_transition", "sur_mot"] },
                "mot_index": { "type": "integer", "minimum": 0 }
              }
            }
          },

          "effets_sonores": {
            "type": "array", "maxItems": 2,
            "items": {
              "type": "object",
              "additionalProperties": false,
              "required": ["role", "ancre"],
              "properties": {
                "role": { "enum": ["whoosh", "clic", "impact", "ting",
                                   "pop", "riser", "souffle", "bip"] },
                "ancre": { "enum": ["debut_scene", "fin_scene",
                                    "sur_transition", "sur_mot"] },
                "mot_index": { "type": "integer", "minimum": 0 },
                "intensite": { "enum": ["faible", "moyenne", "forte"],
                               "default": "moyenne" }
              }
            }
          },

          "note_intention": { "type": "string", "maxLength": 200 }
        }
      }
    }
  }
}
```

**Le vocabulaire complet, et rien d'autre** : 7 fonctions de scène,
3 intensités, 3 cadences, 9 transitions, 6 affichages de texte,
6 b-rolls, 6 effets d'emphase, 8 rôles d'effet sonore, 4 ancres,
6 ambiances de musique. Une centaine de combinaisons par scène, zéro
valeur résolue.

`note_intention` est le seul champ libre. Il n'est **jamais lu par le
compilateur** : il sert au débogage et au prompt de la tentative
suivante. C'est délibéré : sans exutoire, un LLM contraint invente des
champs.

Ce qui est **absent, et doit rester absent** : toute durée, tout
horodatage, toute couleur, toute police, tout nom de fichier, tout nom de
courbe, toute coordonnée, toute opacité, tout preset de mouvement (§7.1).

### 7.3 Validateur du plan (avant compilation)

Les neuf règles sont mécaniques et s'exécutent en dehors du LLM.

| Règle | Contrôle | Si échec |
|---|---|---|
| V-MP-1 | `scenes[].scene_id` est une **bijection** avec les scènes du storyboard, dans le même ordre | reprise LLM |
| V-MP-2 | `storyboard_ref.sha256` = sha256 du storyboard validé par le client | **erreur dure** : le plan porte sur un autre storyboard |
| V-MP-3 | `template.slug/version` est `approuve`, et le nombre de scènes ∈ `[scenes_min, scenes_max]` | reprise LLM |
| V-MP-4 | `affichage_texte` correspond à un emplacement déclaré par le template (D34) | reprise LLM |
| V-MP-5 | `mot_index` < nombre de mots de la scène ; requis si et seulement si `ancre = "sur_mot"` | reprise LLM |
| V-MP-6 | deux emphases ne visent pas le même `mot_index` ; ≤ 3 par scène | reprise LLM |
| V-MP-7 | exactement une scène `fonction = "cta"`, et c'est la dernière | reprise LLM |
| V-MP-8 | `b_roll` demandé ⇒ un `ops.objet` du kind correspondant existe pour cette scène | dégradation en `aucun`, tracée |
| V-MP-9 | aucune chaîne ne contient `#hex`, `px`, `ms`, `cubic-bezier`, `ease` (contrôle lexical) | reprise LLM |

V-MP-8 est le seul qui **dégrade** au lieu de reprendre : redemander au
LLM de choisir un b-roll qui n'existe pas ne donnera pas un meilleur
plan.

### 7.4 Règles du compilateur

Déterministe, sans appel réseau, sans LLM, sans horloge. Ordre imposé :
chaque règle ne consomme que le résultat des précédentes.

**C-1 — Figer les entrées.** Lire storyboard (v_n), `alignement`,
Brand Pack (version), template (slug+version), plan. Calculer
l'`empreinte_entrees = sha256` de leurs sha256 triés. Elle est écrite
dans la composition : deux compositions d'empreinte identique doivent
être **octet pour octet** identiques.

**C-2 — Grille temporelle.** `fps = 30`. Tout instant est un numéro de
frame ; les millisecondes de sortie sont `round(frame × 1000 / 30)`.
Aucun calcul en flottant de millisecondes, jamais, sinon le déterminisme
part en arrondis.

**C-3 — Bornes de scène depuis l'audio** (D20, l'audio est l'horloge).
Pour chaque scène : `debut = premier_mot.debut - amorce` (amorce = 4
frames), `fin = dernier_mot.fin + chute` (chute = 6 frames). Une scène
`muet: true` prend sa `duree_cible_ms` arrondie à la frame — c'est le
seul endroit où la cible est utilisée comme durée. Vraisemblance : si
`|duree_reelle - duree_cible| > 40 %`, une ligne d'avertissement est
écrite dans la trace et dans le message de revue à Franco. Ce n'est pas
une erreur : la cible est indicative depuis A1.

**C-4 — Budget de durée (30 s).** Si le total dépasse 30 s, réduire dans
cet ordre : (1) les pads inter-scènes jusqu'à 0, (2) les chutes jusqu'à 2
frames, (3) les amorces jusqu'à 1 frame. Si le total dépasse encore,
**échouer** avec `E_SURDUREE`. On ne coupe jamais un mot : une phrase
tronquée est un défaut visible, un dépassement est un refus de
plateforme, et les deux sont pires qu'un échec propre qui alerte Franco.
R-SB-1 rend ce cas rare par construction.

**C-5 — Emplacements et texte.** Le texte vient du storyboard, choisi
par `affichage_texte` ; il remplit l'emplacement déclaré du template
(D34). Débordement : appliquer l'échelle typographique du Brand Pack, 3
crans maximum ; au 4ᵉ, `E_DEBORDEMENT_TEXTE`. Aucun ajustement libre de
taille — un compilateur qui interpole une taille de police décide, et
n'a pas le droit de décider.

**C-6 — Mouvement.** `signature` du Brand Pack (D14) × `intensite` ×
`cadence` → amplitudes, durées et courbes, lues dans une table du Brand
Pack. Le compilateur ne calcule aucune courbe : il en lit une.

**C-7 — Transitions.** `(transition_entree, intensite)` → durée en
frames, table du Brand Pack. `coupe` = 0. La durée est tronquée au pad
disponible calculé en C-4 ; une transition qui ne tient pas devient
`coupe`, et c'est tracé.

**C-8 — Emphases.** `ancre` → instant : `debut_scene` = début + 2
frames, `fin_scene` = fin − 3 frames, `sur_transition` = fin de la
transition entrante, `sur_mot` = début du mot d'index `mot_index` dans
l'`alignement`. Paramètres de l'effet : Brand Pack.

**C-9 — B-roll.** Résoudre vers un `objet_id` existant. Plusieurs
candidats : tri par `(role, cle, objet_id)` puis choix par
`sha256(client_id + projet_id + scene_id + role) mod n`. C'est arbitraire
mais **stable et tracé** — c'est ce qui compte. Aucun candidat : voir
V-MP-8.

**C-10 — Pistes audio.** Construire les trois pistes selon §8, y compris
l'enveloppe de ducking, et les écrire dans `pistes_audio` (A2).

**C-11 — Zone de sécurité.** Calculer la boîte de chaque élément et
vérifier qu'elle tient dans la zone utile (≈ 907 × 979 px après 14 % /
35 % / 6 % / 10 %). Un dépassement est `E_HORS_ZONE_SECURITE` : c'est une
erreur de template ou d'échelle typographique, pas quelque chose à
rattraper en déplaçant l'élément. Le lint DOM (D16) refait la mesure sur
le rendu réel ; les deux contrôles ne sont pas redondants, l'un mesure
l'intention, l'autre le résultat.

**C-12 — Sérialisation canonique.** Clés triées, entiers pour les temps,
2 décimales pour les dB, UTF-8 NFC, pas de flottant hors gains, saut de
ligne final. La composition doit être reproductible à l'octet.

**C-13 — Trace.** `trace_resolution` : pour chaque valeur produite, la
règle (`C-6`), la source (`brand_pack v3 > signature.dynamique.punch`) et
la valeur. Écrite sur R2 comme rôle `trace_resolution`. C'est le seul
moyen de répondre à « pourquoi cette vidéo est-elle comme ça » sans
relire quatre fichiers, et ça rend l'écart de deux rendus diffable.

**Toute valeur du `composition.json` doit être imputable à l'une des
règles C-3 à C-11.** Une valeur sans règle est un bug de conception du
contrat, pas un détail d'implémentation.

### 7.5 Traduction du flou (D4)

La table qui fait le lien entre ce que dit le client et le vocabulaire
fermé vit dans `ops.parametre` (clé `traduction_flou`) et n'est lue que
par le clarificateur, jamais par le Monteur — sinon le vocabulaire
cesserait d'être fermé.

| Le client dit | Devient |
|---|---|
| « plus dynamique » | `intensite: forte`, `cadence: rapide`, transitions `glissement_*`/`zoom_avant`, musique `energique` |
| « plus sobre » | `intensite: faible`, `cadence: lente`, transitions `coupe`/`fondu`, musique `neutre` |
| « plus luxe » | `intensite: faible`, `cadence: lente`, `masque_forme`, musique `calme`, emphases `soulignement` |
| « plus pro » | `sous_titre_integral`, `cadence: moyenne`, emphases `encadre` |
| « trop chargé » | `emphases: []`, `b_roll: aucun` hors `photo_produit` |

Ces valeurs entrent dans le `brief`, donc dans le prompt du Monteur comme
**contraintes**, pas comme suggestions : le validateur vérifie qu'elles
sont respectées (règle V-MP-10, ajoutée quand la table est peuplée).

---

## 8. Pipeline audio

D20 renverse l'ordre habituel : l'audio est produit **avant** le montage
et lui impose son horloge. Le pipeline se lit donc en deux moitiés, de
part et d'autre du point de reprise `ASSETS_READY`.

### 8.1 Chaîne complète

```
GENERATING  (job-tts, GPU L4)
  script voix off (storyboard A1)
   └─ synthèse Chatterbox, UNE PASSE PAR SCÈNE ──► voix_brute[scene]
        ├─ rognage des silences de bord
        ├─ passe-haut 80 Hz
        └─ gain statique vers -18 LUFS par scène
   └─ alignement forcé (texte, audio) ──────────► alignement.json
                                                  (mots, ms LOCAUX, confiance)

ASSETS_READY  (job-produce, CPU)
  compilateur (C-3) : bornes de scènes depuis alignement.json
  compilateur (C-10) :
     piste voix    : un segment par scène, positions absolues
     piste effets  : rôles → pistes de bibliothèque, ancres → ms
     piste musique : ambiance → piste exclusive au client, boucle, ducking
  FFmpeg :
     voix_mix ── effets_mix ── musique_mix ──► amix ──► mix_final
                                                  └─ loudnorm 2 passes
                                                     -14 LUFS / -1 dBTP
  mux avec rendu_muet ──► master (document) + apercu (video)
  ffprobe + ebur128 : contrôle bloquant, re-contrôle après ré-encodage
```

Ce qui vit sur le GPU est **exactement** ce qui a besoin du GPU : la
synthèse et l'alignement. Le mixage est du FFmpeg sur CPU, donc il est
refait gratuitement à chaque refus de Franco.

### 8.2 Voix off (D31)

**Une passe de synthèse par scène**, pas une passe pour le script entier.
Trois raisons, dans l'ordre d'importance :

1. une correction de texte sur une scène ne resynthétise que cette scène
   (§3.6) — c'est la seule dépense GPU qu'une relance peut engager ;
2. les bornes de scènes sont exactes par construction, sans avoir à
   découper un fichier long sur des silences ;
3. l'alignement forcé est bien plus fiable sur 3 s de texte connu que sur
   30 s.

Paramètres, tous dans la `cle_generation` : `voix_id` (catalogue
`ops.parametre`), `langue`, texte, `prononciations` (A1), `graine =
sha256(projet_id + scene_id) mod 2^31`. Deux synthèses de la même scène
donnent le même fichier ; c'est ce qui rend une relance gratuite en
qualité comme en coût.

**Post-traitement, identique pour toutes les scènes** (sinon les scènes
ne se ressemblent pas) : rognage des bords sous -45 dBFS en gardant 40 ms
de respiration, passe-haut 80 Hz, puis **gain statique** vers -18 LUFS
mesuré. Gain statique et non compresseur : un compresseur est
dépendant du contenu, donc du hasard de la synthèse, donc
non reproductible d'une scène à l'autre.

Le tatouage audio inaudible de Chatterbox reste en place : il n'est ni
retiré ni contourné, et sa survie au réencodage AAC est un point à
vérifier en T0b (§13).

### 8.3 Alignement mot à mot

Alignement **forcé** — on connaît le texte, donc on n'utilise pas de
reconnaissance libre : un aligneur CTC sur modèle français, dans le même
job GPU, modèle déjà chargé.

```jsonc
// alignement.json
{
  "scenes": [{
    "scene_id": "s03",
    "duree_ms": 2140,               // durée du voix_brute après rognage
    "aligne": true,                 // false = mode dégradé
    "mots": [
      { "index": 0, "mot": "Trois", "debut_ms": 0,   "fin_ms": 310, "conf": 0.98 },
      { "index": 1, "mot": "jours", "debut_ms": 310, "fin_ms": 620, "conf": 0.96 }
    ]
  }]
}
```

Les millisecondes sont **locales à la scène**. Les positions absolues
n'existent qu'après C-3 : c'est ce qui permet au compilateur de déplacer
une scène sans toucher à l'alignement.

**Mode dégradé** : si l'aligneur échoue, ou si plus de 20 % des mots ont
`conf < 0.5`, la scène est marquée `aligne: false` et les mots reçoivent
une répartition proportionnelle au nombre de caractères. Le compilateur
refuse alors toute ancre `sur_mot` sur cette scène et la remplace par
`debut_scene`, en le traçant. Une emphase mal calée est plus visible
qu'une emphase au début de scène.

### 8.4 Placement des effets sonores

**Élection de la piste.** `role` → requête par tags sur
`ops.piste_audio` (`kind = 'effet'`), candidats triés par `piste_id`,
choix par `sha256(client_id + projet_id + scene_id + role) mod n`.
Stable, tracé, et différent d'un client à l'autre.

**Calage sur l'attaque, pas sur le fichier.** Un « whoosh » dont le
fichier commence par 90 ms de souffle tombe à côté si on aligne le début
du fichier sur l'ancre. On cale donc `attaque_ms` (mesuré à l'import,
premier échantillon à -20 dBFS du pic) :

```
debut_ms = ancre_ms - attaque_ms + offset_role
```

**Offsets par rôle** (table figée, pas un réglage) :

| Rôle | Ancre naturelle | `offset_role` | Durée max |
|---|---|---|---|
| `impact` | début de mot, début de scène | 0 | 800 ms |
| `clic`, `ting`, `pop` | début de mot | 0 | 400 ms |
| `whoosh` | transition | −60 ms | 900 ms |
| `riser` | transition (il *monte vers* elle) | −(durée) | 1500 ms |
| `bip` | début de mot | 0 | 300 ms |
| `souffle` | début ou fin de scène | 0 | 1200 ms |

**Règles d'élagage**, appliquées dans cet ordre :

- ≤ 2 effets par scène (schéma A3) **et ≤ 6 par vidéo**. Une pub de 30 s
  avec douze effets n'est pas montée, elle est bruyante.
- deux attaques distantes de moins de **300 ms** : on garde la plus
  prioritaire. Priorité : `impact` > `whoosh` > `riser` > `ting` > `pop`
  > `clic` > `bip` > `souffle`.
- un effet dont l'attaque tombe pendant un mot dont `conf < 0.5` est
  décalé au début de la scène.
- tout élagage est écrit dans `trace_resolution`.

**Gains.** Piste normalisée au pic à -18 dBFS, puis
`intensite` → `faible: -6 dB`, `moyenne: -3 dB`, `forte: 0 dB`.

### 8.5 Musique et ducking

**Élection** : `ambiance` → tags, `kind = 'musique'`, **candidats
excluant toute piste déjà présente dans `ops.attribution_musique`**
(D32). La piste élue est insérée dans `attribution_musique` ; en cas de
collision sur la clé primaire, on relit et on réélit. Le client garde
ensuite sa piste : la deuxième vidéo du même client réutilise son
attribution, ce qui donne au passage une cohérence sonore gratuite d'une
vidéo à l'autre.

**Mise en longueur** : boucle avec fondu croisé de 500 ms jusqu'à
`duree_ms`, fondu d'entrée 800 ms, fondu de sortie 1200 ms. Lit de
musique à **-30 LUFS** (gain statique depuis `piste_audio.lufs`).

**Ducking déterministe, par enveloppe et non par compresseur.** Un
`sidechaincompress` dépend de l'attaque réelle du signal, donc deux
mixages du même projet peuvent différer ; une enveloppe est une donnée,
donc elle est reproductible et **inspectable** — elle est écrite dans la
composition (A2).

Construction :

1. intervalles de parole = intervalles de mots de la piste voix ;
2. fusionner deux intervalles séparés de moins de **400 ms** (sinon la
   musique remonte entre deux mots, ce qui s'entend comme un défaut) ;
3. pour chaque région de parole : `-9 dB`, attaque **120 ms avant** le
   début de la région, retour à `0 dB` **300 ms après** la fin ;
4. l'enveloppe commence et finit à `0 dB` (R-CO-3) ;
5. appliquée par un fichier de commandes `asendcmd` sur un filtre
   `volume` — des données, pas un traitement adaptatif.

Les effets sonores ne ducke rien : ils sont courts, et une musique qui
plonge à chaque « clic » respire mal.

### 8.6 Normalisation, encodage, contrôle bloquant

**Mixage** : les trois pistes sont placées par `adelay` aux positions
absolues de la composition, puis `amix` sans normalisation automatique
(elle est dépendante du nombre d'entrées, donc traître).

**Normalisation** : `loudnorm` en **deux passes**, mode linéaire — passe
1 mesure, passe 2 applique avec les valeurs mesurées : `I = -14`,
`TP = -1`, `LRA = 11`. Le mode linéaire est le seul déterministe ; le
mode dynamique par défaut change le son selon l'historique du signal.

**Deux encodages, un seul mixage.**

| | Master (`document`, D23) | Aperçu (`video`, D23) |
|---|---|---|
| Vidéo | H.264 High, CRF 18, 1080×1920 | H.264 **Main**, **`-bf 0`**, `yuv420p` |
| Fréquence | 30 fps **fixe** (`-r 30 -vsync cfr`) | idem |
| Audio | AAC 192 kb/s, stéréo, 48 kHz | AAC 128 kb/s minimum, stéréo, 48 kHz |
| Taille | ≤ 100 Mo | **≤ 16 Mo** |
| Divers | `+faststart` | `+faststart` |

**Contrôle bloquant** (`rapport_conformite`, rôle `ops.objet`) — 14
assertions, toutes binaires, sur les **deux** pièces :

1. conteneur MP4, `+faststart` effectif ; 2. `codec = h264` ;
3. profil (`High` master / `Main` aperçu) ; 4. `has_b_frames = 0` sur
l'aperçu ; 5. `pix_fmt = yuv420p` ; 6. `1080×1920` ;
7. `r_frame_rate = 30/1` et `avg_frame_rate = 30/1` (fréquence fixe) ;
8. `duree ≤ 30,0 s` ; 9. `codec audio = aac` ; 10. `canaux = 2` ;
11. débit audio ≥ 128 kb/s ; 12. `48 kHz` ;
13. `LUFS ∈ [-14,5 ; -13,5]` (mesure `ebur128`) ;
14. `dBTP ≤ -1,0`.

Plus, pour l'aperçu, la taille ≤ 16 Mo. Si elle dépasse : nouveau débit
cible `= 16 Mo × 0,92 / duree`, ré-encodage, et **relance de la totalité
des 14 assertions** — le document l'exige, et c'est justifié : un
ré-encodage peut réintroduire des B-frames ou changer le pic.
Deux ré-encodages au maximum, puis `E_CONFORMITE` et `FAILED`.

Le résultat du contrôle part dans `history.livraison` (LUFS, dBTP,
durée, octets, `hash_frames`) : c'est la preuve qu'on a livré conforme, et
la base de calibration du futur juge automatique (D22).

### 8.7 Licences (contrainte dure)

Aucune piste n'entre dans la bibliothèque sans `licence`, `licence_url`
et `releve_le` (contrainte `piste_licence_non_vide`, §2.6). À chaque
usage, `ops.usage_audio` garde une **copie** de la licence, pas une
jointure. À la clôture, la trace part dans `history` et survit à la purge
des octets. Une vidéo livrée en janvier reste donc défendable en juillet,
même si Pixabay a changé ses conditions entre-temps et même si le fichier
a été purgé.

### 8.8 Reprise dans le pipeline audio

| Ce qui change | Ce qu'on resynthétise | Ce qu'on remixe |
|---|---|---|
| refus de Franco sur le montage (T11) | rien | tout le mixage |
| refus sur une intonation | la scène concernée (nouvelle `graine`) | tout le mixage |
| correction factuelle d'un mot (T13) | la scène concernée | tout le mixage |
| changement de voix | toutes les scènes | tout le mixage |
| relance après crash | les scènes sans `voix_brute` | tout le mixage |

Le remixage complet est systématique et assumé : il coûte moins d'une
minute de CPU, alors qu'un mixage partiel exigerait de savoir quelles
parties du mix dépendent de quoi — une complexité qui ne se rentabilise
jamais à 60 projets par mois.

---

## 9. Canal admin WhatsApp (D29)

### 9.1 Chaîne de traitement

```
message du numéro admin (constante de déploiement, jamais modifiable
                         par WhatsApp — garde-fou 4)
  │
  ├─ réponse à un bouton ? ──► pas de LLM du tout : la charge utile du
  │                            bouton EST la commande (commande_id + oui/non)
  │
  └─ texte libre
       └─ LLM contraint ──► JSON unique validé par commande_admin.schema.json
            ├─ invalide ou hors vocabulaire → question de clarification
            │                                 prise dans une liste fixe
            └─ valide → ops.commande_admin (statut 'proposee')
                 └─ reformulation + boutons [oui] [annuler]
                      ├─ commande sensible → + code de confirmation
                      └─ exécution transactionnelle + history.audit
```

Le LLM **traduit**, il n'exécute pas. Sa sortie est une valeur de
`ops.commande_admin_nom` et un objet de paramètres validé par schéma ;
il n'a accès à aucun outil d'écriture. Une phrase qu'il ne sait pas
traduire produit `nom: null`, et le système répond avec la liste des
commandes — jamais avec une tentative d'interprétation.

### 9.2 Les douze commandes

| Commande | Paramètres | Effet | Code | Réversible |
|---|---|---|---|---|
| `client_ajouter` | `telephone`, `nom_affiche` | entre en liste blanche (D25) | **oui** | oui (`client_retirer`) |
| `client_retirer` | `client_id` | `statut = 'retire'`, plus aucun message accepté | **oui** | oui |
| `client_pause` | `client_id` | bloque les **nouveaux** projets ; les projets en cours vont au bout | non | oui |
| `client_reprendre` | `client_id` | `statut = 'actif'` | non | oui |
| `plafond_modifier` | `type_job`, `plafond_c`, `plafond_mois_c?` | change `ops.plafond_cout` ; s'applique aux projets **futurs** | **oui** | oui |
| `livraison_valider` | `projet_id` | T12 : livraison double | non | non |
| `livraison_refuser` | `projet_id`, `motif` (liste fermée) | T11 : retour au Monteur | non | oui (re-revue) |
| `style_approuver` | `template_id` | `statut = 'approuve'` (file D15) | non | oui (`retire`) |
| `job_relancer` | `projet_id` | reprise depuis l'état courant, ou depuis `etat_avant_echec` si `FAILED` (O-2) | non | — |
| `etat_lire` | `client_id?`, `projet_id?` | lecture seule | non | — |
| `depenses_lire` | `mois?`, `client_id?` | lecture seule, depuis `ops.generation` + `history.generation` | non | — |
| `donnees_supprimer` | `client_id`, `portee` ∈ {`projet`, `client_travail`, `client_tout`} | purge ciblée | **oui** | **non** |

Les plafonds ne s'appliquent qu'aux projets futurs : changer le plafond
d'un projet en cours reviendrait à casser l'invariant
`budget_restant <= budget_centimes` ou à rendre du budget déjà consommé.
`budget_centimes` est une **copie** faite à l'entrée en `GENERATING`,
justement pour cela.

`livraison_valider` et `livraison_refuser` arrivent normalement par
bouton, donc sans LLM et sans ambiguïté. Le motif de refus est une liste
fermée (`montage`, `rythme`, `texte`, `voix`, `musique`, `asset`,
`marque`, `autre`) parce qu'il est réinjecté dans le prompt du Monteur :
un motif libre ferait dériver le vocabulaire fermé, et ces motifs sont
aussi les **données de calibration** du juge automatique promis par D22.

### 9.3 Schéma de validation

Un seul fichier, `commande_admin.schema.json`, discriminé par `nom`,
`additionalProperties: false` partout — c'est ce qui empêche un paramètre
inventé de passer.

```jsonc
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "commande_admin.schema.json",
  "type": "object",
  "required": ["nom"],
  "additionalProperties": false,
  "properties": {
    "nom": { "enum": ["client_ajouter", "client_retirer", "client_pause",
                      "client_reprendre", "plafond_modifier",
                      "livraison_valider", "livraison_refuser",
                      "style_approuver", "job_relancer", "etat_lire",
                      "depenses_lire", "donnees_supprimer", null] },
    "parametres": { "type": "object" },
    "confiance": { "type": "number", "minimum": 0, "maximum": 1 }
  },
  "allOf": [
    {
      "if":   { "properties": { "nom": { "const": "client_ajouter" } } },
      "then": { "properties": { "parametres": {
                  "type": "object", "additionalProperties": false,
                  "required": ["telephone", "nom_affiche"],
                  "properties": {
                    "telephone":   { "type": "string",
                                     "pattern": "^\\+[1-9][0-9]{7,14}$" },
                    "nom_affiche": { "type": "string", "minLength": 2,
                                     "maxLength": 60 }
                  } } } }
    },
    {
      "if":   { "properties": { "nom": { "const": "plafond_modifier" } } },
      "then": { "properties": { "parametres": {
                  "type": "object", "additionalProperties": false,
                  "required": ["type_job", "plafond_c"],
                  "properties": {
                    "type_job":       { "enum": ["video","visuel","retouche"] },
                    "plafond_c":      { "type": "integer",
                                        "minimum": 1, "maximum": 500000 },
                    "plafond_mois_c": { "type": "integer",
                                        "minimum": 1, "maximum": 5000000 }
                  } } } }
    },
    {
      "if":   { "properties": { "nom": { "const": "livraison_refuser" } } },
      "then": { "properties": { "parametres": {
                  "type": "object", "additionalProperties": false,
                  "required": ["projet_id", "motif"],
                  "properties": {
                    "projet_id": { "type": "string", "format": "uuid" },
                    "motif": { "enum": ["montage","rythme","texte","voix",
                                        "musique","asset","marque","autre"] },
                    "precision": { "type": "string", "maxLength": 200 }
                  } } } }
    },
    {
      "if":   { "properties": { "nom": { "const": "donnees_supprimer" } } },
      "then": { "properties": { "parametres": {
                  "type": "object", "additionalProperties": false,
                  "required": ["client_id", "portee"],
                  "properties": {
                    "client_id": { "type": "string", "format": "uuid" },
                    "portee": { "enum": ["projet","client_travail",
                                         "client_tout"] },
                    "projet_id": { "type": "string", "format": "uuid" }
                  } } } }
    }
    // … un bloc par commande, même forme
  ]
}
```

`plafond_c` a un **maximum** dans le schéma : une faute de frappe (un
zéro de trop) ne doit pas pouvoir devenir un plafond de 5 000 €. C'est le
genre de garde-fou qui coûte une ligne et sauve un mois de marge.

`confiance` est renseigné par le LLM ; sous 0,8, la reformulation est
posée comme une question fermée (« Tu veux bien retirer le client X ? »)
au lieu d'une confirmation (« Je retire le client X, c'est bon ? »). La
différence n'est pas cosmétique : une affirmation obtient « oui » par
réflexe.

### 9.4 Garde-fous

1. **Confirmation systématique.** Toute commande qui écrit est reformulée
   et attend un « oui » explicite, par bouton. Une commande `proposee`
   expire en **10 minutes**. Une seule commande `proposee` à la fois :
   « oui » ne doit jamais être ambigu.
2. **Code de confirmation** pour les quatre commandes sensibles
   (`client_ajouter`, `client_retirer`, `plafond_modifier`,
   `donnees_supprimer`). C'est une
   **phrase de passe mémorisée par Franco**, pas un code envoyé par
   message ni un TOTP : la menace visée est le vol du téléphone ou le
   clonage de SIM, or un code envoyé sur le téléphone volé et une
   application d'authentification installée sur le téléphone volé ne
   protègent de rien. La phrase est stockée **hachée** (Argon2id) dans
   Secret Manager, jamais en base. Trois essais, puis verrouillage du
   canal admin pendant 15 minutes et alerte P1 — l'alerte partant vers le
   même numéro, elle est doublée par e-mail.
3. **Expurgation.** Le message contenant la phrase de passe est stocké
   avec `corps = '[code expurgé]'` dans `ops.message_entrant`, et n'entre
   jamais dans `history.message` ni dans les journaux.
4. **Numéro admin non modifiable par WhatsApp** : constante de
   déploiement. Aucune commande ne le change ; le changer demande un
   déploiement, donc un accès Google Cloud, donc un second facteur qui
   n'est pas le téléphone.
5. **Pas d'exécution libre.** Il n'existe aucune commande « exécuter »,
   « SQL », « shell » ni « prompt ». Le vocabulaire des douze commandes
   est la surface d'attaque totale du canal.
6. **Suppression : trace avant l'acte.** `donnees_supprimer` écrit dans
   `history.audit` la liste des clés R2 et des identifiants concernés
   **avant** de supprimer quoi que ce soit. Après, l'information n'existe
   plus.

### 9.5 Audit

`history.audit` est écrit **dans la même transaction que la mutation** :
pas d'écriture après coup, donc pas de mutation sans trace. Une ligne
par commande exécutée, avec `acteur` (numéro admin), `source`
(`admin_wa`), `action`, `objet_type`, `objet_id`, `valeur_avant`,
`valeur_apres`, `commande_id`. Les lectures (`etat_lire`,
`depenses_lire`) sont aussi auditées, avec des valeurs nulles : savoir
qui a consulté quoi coûte une ligne et répond à une question qu'on se
pose toujours trop tard.

Le rôle applicatif n'a que `INSERT` et `SELECT` sur `history` (§2.10) :
l'audit n'est donc pas modifiable par le code qui l'écrit.

### 9.6 Alertes hors fenêtre de 24 h

La fenêtre de service WhatsApp de 24 h se compte depuis le dernier
message de Franco. Au-delà, un message libre est refusé par Meta : les
alertes passent alors par le **template utility** approuvé, avec au plus
trois variables (projet, état, cause courte). C'est pour cela que ce
template est bloquant en T1 et pas « à faire un jour » : sans lui, une
panne à 3 h du matin est silencieuse jusqu'à ce que Franco écrive de
lui-même.

Le système suit `derniere_activite_admin` et choisit seul entre message
libre et template. Toute alerte P1 est **aussi** envoyée par e-mail : si
la panne est dans l'envoi WhatsApp, l'alerte WhatsApp ne partira pas.

---

## 10. Erreurs et alertes (O4-B, D33)

O4-B tient en trois obligations, et l'architecture les rend structurelles
plutôt que déclaratives : **message neutre au client**, **alerte à
Franco**, **watchdog**. La troisième est au §3.5 ; les deux premières
sont ici.

### 10.1 Taxonomie

| Code | Classe | Action automatique | Client | Franco |
|---|---|---|---|---|
| `E_BUDGET` | argent | arrêt immédiat, `FAILED` | neutre 3 | **P1** + plafond courant |
| `E_QUOTA_FOURNISSEUR` | argent | `FAILED` (reprise possible par T17) | neutre 3 | **P1** + « recharger » |
| `E_FOURNISSEUR_INDISPO` | externe | 2 reprises, puis relance watchdog, puis `FAILED` | neutre 2 puis 3 | P2, **P1** si `FAILED` |
| `E_REFUS_CONTENU` | contenu | retour en `CLARIFYING` | neutre 4 (reformuler) | P3 |
| `E_TIMEOUT` | externe | reprise, réconciliation obligatoire | neutre 2 | P2 |
| `E_CONFORMITE` | sortie | 2 ré-encodages, puis `FAILED` | neutre 3 | **P1** + rapport |
| `E_SURDUREE` | sortie | `FAILED` | neutre 3 | **P1** + écart mesuré |
| `E_DEBORDEMENT_TEXTE` | sortie | 3 crans typographiques, puis `FAILED` | neutre 3 | **P1** + scène fautive |
| `E_HORS_ZONE_SECURITE` | template | `FAILED` | neutre 3 | **P1** — bug de template |
| `E_POLICE_MANQUANTE` | déploiement | `FAILED` | neutre 3 | **P1** — bug d'image |
| `E_NON_DETERMINISTE` | moteur | `FAILED` | neutre 3 | **P1** — régression moteur |
| `E_ASSET_MANQUANT` (client) | entrée | retour en `CLARIFYING` | neutre 4 | — |
| `E_ASSET_MANQUANT` (généré) | interne | régénération idempotente | — | P3 |
| `E_ALIGNEMENT` | audio | mode dégradé (§8.3) | — | P3 |
| `E_MONTEUR_INVALIDE` | LLM | 2 reprises, puis plan par défaut | — | P3 |
| `E_WA_ENVOI` | externe | reprise exponentielle, 5 essais | — | **P1** si livraison |
| `E_SIGNATURE_WEBHOOK` | sécurité | 403, rien traité | — | P2 (dédupliqué) |
| `ABANDON_CLIENT` | client | `FAILED` | — | P3 (digest) |
| `E_INTERNE` | inconnu | `FAILED`, pile dans `detail_echec` | neutre 3 | **P1** |

Deux principes se lisent dans cette table. **Ce qui est réparable seul
n'alerte pas** (alignement dégradé, plan par défaut, régénération) : une
alerte sans action possible entraîne qu'on cesse de lire les alertes.
**Ce qui coûte de l'argent ou casse une livraison alerte tout de suite**,
même si le client n'a rien vu.

### 10.2 Messages neutres au client

Catalogue fermé, dans `ops.parametre`, cinq messages, aucun autre
autorisé dans le code :

1. **accusé** — « Bien reçu. Je regarde ça et je reviens vers vous. »
2. **en cours** — « C'est en production, je vous envoie l'aperçu dès
   qu'il est prêt. »
3. **incident** — « Un imprévu technique de notre côté sur cette vidéo.
   Je reprends la main et je reviens vers vous rapidement. »
4. **il me manque** — « Il me manque *{élément}* pour continuer. »
5. **hors périmètre** — description fixe du service rendu (elle sert
   aussi de réponse aux numéros hors liste blanche, D25, et de défense
   vis-à-vis de la politique Meta du 15 janvier 2026).

Aucun code d'erreur, aucun nom de fournisseur, aucun délai chiffré qu'on
ne peut pas tenir, et **jamais** de mention de l'IA ou du pipeline. Le
message 3 ne promet pas de correction gratuite : c'est D26 qui la définit,
sur l'erreur factuelle, et c'est Franco qui l'accorde.

### 10.3 Alertes à Franco

**Trois niveaux, un seul canal.**

| Niveau | Quand | Livraison |
|---|---|---|
| **P1** | argent, livraison cassée, bug de template ou de déploiement, verrouillage admin | immédiate : WhatsApp (template utility hors fenêtre) **+ e-mail** |
| **P2** | incident externe absorbé, 80 % du plafond mensuel atteint, signature invalide | lot horaire |
| **P3** | dégradations, abandons client, plans par défaut | digest quotidien à heure fixe |

**Anti-noyade**, trois mécanismes : clé de déduplication
`(projet_id, code)` avec au plus une alerte par heure ; plafond global de
10 P1 par heure, au-delà un seul message « N alertes supprimées, voir
`etat_lire` » ; et une alerte P1 contient toujours **la commande admin à
taper** (`job_relancer <projet_id>`), pour que lire l'alerte suffise à
agir depuis le téléphone.

Contenu d'une P1 : projet, client, état, code, une ligne de cause,
commande suggérée. Rien de plus — c'est lu sur un téléphone, souvent la
nuit.

### 10.4 Ce qui n'est pas dans le système

Deux surveillances sont **hors** du système, parce qu'un système ne
constate pas sa propre mort :

- **contrôle de disponibilité** Cloud Monitoring sur `GET /sante` toutes
  les 5 min → e-mail + SMS. `/sante` renvoie 503 si la boucle de watchdog
  a plus de 5 min de retard ;
- **alerte de solde** chez fal.ai et Google Cloud (budget d'alerte à 50 %,
  80 %, 100 %), parce que D35 borne ce que *nous* dépensons, pas ce que
  coûte l'infrastructure.

Rien d'autre : pas de collecte de métriques, pas de tableau de bord, pas
de traçage distribué. Les questions d'exploitation à cette échelle se
répondent par trois requêtes SQL (projets non terminaux, dépenses du
mois, échecs des 7 derniers jours), et le journal Cloud Logging du Job
suffit au diagnostic. Le jour où on lit ces requêtes plus de deux fois
par jour, il sera temps d'en faire un écran — pas avant.

---

## 11. Plan d'implémentation

### 11.1 Où chaque partie de ce document est construite

| Section | T-1 | T0 | T0b | T1 | T2 | T3 | T4 |
|---|:-:|:-:|:-:|:-:|:-:|:-:|:-:|
| §2 Postgres (`ops` + `history`) | | | | | | ● | |
| §3 Machine à états, watchdog | | | | | | ● | |
| §4 `svc-conversation` | | | | | | | ● |
| §4 `job-produce` | | | | ○ | ○ | ● | |
| §4 `job-tts` (GPU) | | | ○ | | | ● | |
| §5.1 Adaptateur de rendu | | ● | | ● | ● | | |
| §5.2 Adaptateur de génération | | | | | ○ | ● | |
| §6 A1 storyboard | | | ○ | | | ● | ● |
| §6 A2 composition | | | | ● | ● | | |
| §7 Monteur + compilateur | | | | | ○ | ● | |
| §8 Pipeline audio | | | ● | ● | | ● | |
| §8.6 Contrôle bloquant (14 assertions) | | ● | | ● | | | |
| §9 Canal admin | | | | | | | ● |
| §10 Erreurs et alertes | | | | ○ | | ● | ● |

● construit — ○ ébauché à la main, sans automatisation

Lecture : **T0 et T1 travaillent sans base de données**. L'état d'un
projet y vit dans un `projet.json` sur R2 qui porte **exactement les noms
de colonnes** de `ops.projet`. T3 est alors une migration mécanique, pas
une réécriture — et si les noms divergent, on l'aura su tôt.

### 11.2 Prérequis, avant tout code

Ils ne sont pas dans une tranche parce qu'ils ne dépendent de rien et
bloquent tout le reste.

| Prérequis | Bloque | Quand |
|---|---|---|
| System User + token permanent | T1 (tout envoi) | maintenant |
| Template utility approuvé | §9.6, donc toute alerte nocturne | maintenant (délai d'approbation Meta) |
| Carte de paiement Google Cloud acceptée | `job-tts`, donc T3 | avant T3, à tester tôt |
| Offre Supabase payante (O-3) | 24/7, donc T3 | avant T3 |
| Webhook HTTPS + `messages` + vérification de signature | T4 | avec T4 |
| Mode Live + profil business explicite | premier client hors développement | avant T4 |

### 11.3 T-1 — ce que veut vraiment le client existant

*En parallèle de T0.* 3 à 5 vidéos produites à la main.

À produire, en plus des vidéos : un relevé par vidéo — assets fournis
(nombre, qualité), corrections demandées et **leur nature** (les motifs
fermés du §9.2), délai réellement accepté, usage final (TikTok Shop,
Ads, statut). Ce relevé est la première source du Brand Pack et de la
table `traduction_flou` (§7.5), et la seule mesure honnête du délai avant
que D36 ne soit un engagement.

**Sortie** : un Brand Pack rédigé, une liste de motifs de refus réels, un
délai observé.

### 11.4 T0 — le moteur rend-il pro ?

*Le pari D7.* Un template, 3 jeux d'assets, aucun pipeline.

Au-delà des critères A/B/C du document d'état, T0 doit répondre à **trois
questions d'architecture** qui décident du reste :

1. `capacites().lint_dom` — le DOM pré-rendu est-il inspectable ? Sinon
   **D16 tombe** et il faut un lint sur image rendue, plus faible
   (objection O-5).
2. `capacites().emplacements` — les templates acceptent-ils des
   emplacements déclarés remplis par JSON (D34 / O5-C) ? Sinon c'est le
   contrat `template.schema.json` qui change, et avec lui la règle C-5.
3. Le `hash_frames` est-il stable entre deux rendus identiques ? Sinon le
   déterminisme n'est pas une propriété du moteur et le critère C de T0
   est inatteignable.

**À construire en T0** (et pas plus) : l'adaptateur de rendu §5.1 réduit
à `capacites()` et `rendre()`, le lint de zone de sécurité, et les 14
assertions du §8.6 — le critère A du document exige qu'elles soient
vérifiées par code, et elles serviront jusqu'en production.

**Sortie** : le format d'authoring figé, `template.schema.json`, un
verdict sur D7, D16 et D34.

### 11.5 T0b — la synchronisation audio tient-elle ?

*Sur Colab (D31), sur un des jeux d'assets de T0.*

À décider ici, parce que tout le §8 en dépend : le **choix de
l'aligneur** forcé, la mesure réelle du **débit de parole** en français
(la valeur 2,6 mots/s de R-SB-1 est une hypothèse), le **catalogue de
voix** effectivement utilisable, et les six constantes du §8 (amorce 4
frames, chute 6 frames, -9 dB de ducking, fusion à 400 ms, lit à
-30 LUFS, effets à -18 dBFS).

Contrôle supplémentaire : le tatouage inaudible de Chatterbox survit-il à
l'encodage AAC à 128 kb/s ?

**Sortie** : les constantes du §8 mesurées et non supposées, le catalogue
de voix, l'aligneur choisi, l'image du futur `job-tts` esquissée.

### 11.6 T1 — peut-on livrer de bout en bout ?

`composition.json` (A2) écrit à la main → rendu → mixage audio → 14
assertions → livraison double. Pas de webhook : Franco déclenche, le
système envoie.

Ordre : disposition R2 et préfixes → adaptateur de rendu complet
(`verifier` inclus) → chaîne FFmpeg du §8.6 → envoi WhatsApp avec
`cle_envoi` → aperçu et master sur un vrai téléphone.

**Sortie** : une vidéo livrée en deux pièces, l'aperçu qui se lit dans le
fil, le master qui se télécharge intact, les 14 assertions vertes sur les
deux. C'est aussi le premier test de la contrainte des 16 Mo, celle qui
se découvre toujours trop tard.

### 11.7 T2 — est-ce reproductible d'une marque à l'autre ?

Brand Pack du client réel + 3 ou 4 templates. C'est ici que se règlent
l'échelle typographique (C-5), les presets de mouvement (D14, C-6) et la
table des transitions (C-7) — tout ce que le compilateur **lira** au lieu
de calculer.

**Sortie** : deux marques rendues par le même `composition.json`
structurel, sans une ligne de code modifiée. Le critère du document
d'état (« code modifié entre les 3 jeux d'assets : aucun ») s'applique
ici aussi, et il est plus dur.

### 11.8 T3 — la compilation s'automatise-t-elle ?

La tranche la plus lourde. Ordre imposé par le risque, chaque étape
utilisable avant la suivante :

1. **Base** : les deux schémas, les contraintes, les index, et un test
   qui prouve l'isolation (une ligne d'un client attachée au projet d'un
   autre doit être **rejetée par la base**, pas par le code).
2. **Machine à états et baux** : transitions gardées (§3.1),
   `ops.execution_job`, `job-produce` qui ne fait encore que prendre le
   bail et avancer. Testable en injectant des états à la main.
3. **Adaptateur de génération et plafonds** ensemble (§5.2) : ils
   partagent une transaction. Test : une relance après coupure ne crée
   pas de seconde ligne `ops.generation`.
4. **`job-tts`** : image GPU avec poids embarqués, synthèse par scène,
   alignement, écriture R2 + base.
5. **Compilateur** (C-1 → C-13) et validateurs A2/R-CO. Testable sans
   LLM, avec des `montage_plan` écrits à la main — **c'est la pièce à
   tester le plus durement**, puisque c'est elle qui ne doit rien
   décider.
6. **Monteur** : prompt à vocabulaire fermé, validateur V-MP, plan par
   défaut. Le plan par défaut **avant** le LLM : ainsi le pipeline est
   complet sans lui, et le LLM est une amélioration, pas une dépendance.
7. **Watchdog** et alertes (§3.5, §10), puis contrôle de disponibilité
   externe.

**Sortie** : un projet lancé par une insertion en base et un storyboard
conforme à A1 arrive livré, sans intervention hors revue de Franco. Et le
test qui compte : **relancer le job depuis chaque état et vérifier que
`count(ops.generation)` ne bouge pas.** C'est la consigne 4, rendue
mesurable.

### 11.9 T4 — la conversation s'automatise-t-elle ?

Ordre imposé par ce qu'on perd en cas d'absence :

1. **Webhook** : signature, dédup, 200 immédiat, **copie du média sur R2
   avant toute logique** (ce qui n'est pas copié est définitivement
   perdu).
2. **Canal admin** (§9) : avant le reste, parce que c'est ce qui permet
   d'exploiter le système pendant qu'on construit le reste.
3. **Classifieur** + liste blanche + message hors périmètre (D2, D25).
4. **Clarificateur** : slots, boutons, listes, brouillon par défaut,
   extraits de démonstration, échantillons de voix.
5. **Storyboard LLM** + règles R-SB-1..4 + boucle de validation client.

**Sortie** : un message WhatsApp réel devient une vidéo livrée, avec une
seule intervention humaine — la validation de Franco. Et le canal admin
permet d'ajouter un client et de relancer un job depuis le téléphone.

---

## 12. Objections

Aucune de ces objections ne modifie une décision. Elles signalent des
endroits où deux décisions se contredisent, ou où une décision ne tient
pas ce qu'elle promet.

**O-1 — D22 et D36 ne sont pas simultanément satisfiables.** Service
24 h/24 avec 4 h de délai, et validation humaine de **chaque** livraison :
une commande reçue à 2 h du matin ne peut pas être livrée à 6 h si Franco
dort. Ce n'est pas un détail d'exploitation, c'est une impossibilité
arithmétique. L'architecture la contient au lieu de la masquer :
`PENDING_REVIEW` compte dans l'horloge de service (§3.4) et le watchdog
alerte, donc le manquement est **visible et mesuré** dès le premier
projet nocturne. La sortie de secours existe déjà structurellement — il
manque une seule arête, `PENDING_REVIEW → DELIVERED` automatique, sous
conditions vérifiables (template approuvé, 14 assertions vertes, aucun
avertissement de compilation, client déjà servi au moins une fois). Elle
n'est pas dessinée parce que la décision appartient à Franco (§13, B1).

**O-2 — `FAILED` est terminal dans le diagramme, mais le canal admin
promet une relance « depuis le dernier état ».** Les deux ne peuvent pas
être vrais. J'ai tranché dans le sens de l'utilité : `ops.projet` retient
`etat_avant_echec` et la commande `job_relancer` restaure cet état
(transition T17). C'est un écart **assumé et signalé** avec le
diagramme ; sans lui, `E_QUOTA_FOURNISSEUR` détruirait un projet dont
tous les assets sont payés et valides, ce qui contredit la consigne 4.

**O-3 — D8 sur l'offre gratuite est incompatible avec D36.** Un projet
Supabase gratuit est mis en pause après inactivité ; un service 24 h/24
dont la base peut s'endormir n'est pas un service 24 h/24. Ce n'est donc
pas un point « à vérifier » mais une ligne de coût à accepter avant T3.
La décision D8 (Postgres unique, Supabase) n'est pas remise en cause —
seulement l'offre.

**O-4 — D26 et D27 se recouvrent exactement, et c'est trop juste.** La
correction factuelle est due 7 jours, la rétention est de 7 jours : un
client qui signale une erreur le septième jour trouve les assets purgés,
et la correction devient une régénération payante. Mise en œuvre retenue
(§2.11) : `expire_le = clos_le + 10 jours` pour les objets nécessaires à
une correction (`composition`, `alignement`, `voix_mix`, `asset_genere`,
`master`), 7 jours pour le reste. Trois jours de R2 supplémentaires pour
une trentaine de projets coûtent quelques centimes.

**O-5 — D7, D16 et D34 sont un seul pari, pas trois décisions
indépendantes.** Le lint DOM pré-rendu (D16) et les templates HTML à
emplacements déclarés (D34) présupposent tous deux un moteur à DOM. Si
HyperFrames n'en est pas un, D16 et D34 tombent **ensemble** avec D7, et
c'est la moitié du §7 qui change. T0 doit donc tester le moteur contre
ces deux décisions explicitement (§11.4), et pas seulement contre la
qualité perçue.

**O-6 — D35 borne un projet, pas un mois.** Un plafond par type de job
n'empêche pas soixante projets d'échouer chacun à la limite de son
plafond. L'exposition réelle est `plafond × nombre de projets`, et une
boucle de relances reste invisible tant que chaque projet est dans les
clous. D'où `plafond_mois_c` (§2.8) et l'alerte P2 à 80 %. Ce n'est pas
une modification de D35 mais sa condition de sûreté.

**O-7 — D24 fait valider au client une durée qui n'existe pas encore.**
Depuis D20, la durée est une conséquence de l'alignement ; le storyboard
n'en porte qu'une cible (A1). Le client valide donc « 15 s » et peut
recevoir 19 s. Atténuations retenues : R-SB-1 (le script doit tenir en
28 s, contrôlé avant toute dépense), une durée annoncée arrondie
(« ≈ 15 s »), et l'écart signalé à Franco en revue au-delà de 40 %
(C-3). La tension subsiste et elle est structurelle.

**O-8 — « réduire le délai vers quelques minutes » est hors d'atteinte
tant que D22 tient.** Même sans validation humaine, le plancher technique
est de 6 à 10 min : démarrage à froid du Job GPU (2 à 4 min), générations
fal.ai, rendu (cible T0 : 5 min), mixage, encodages, envois. Avec D22, le
délai est celui du sommeil de Franco. L'objectif « quelques minutes »
n'est pas une contrainte d'architecture mais une ambition produit ; il ne
faut pas concevoir contre lui aujourd'hui.

**O-9 — « voix off au choix du client » (D19) n'a pas encore d'objet.**
D31 fixe le moteur (Chatterbox) mais pas le nombre de voix françaises
réellement utilisables. Si T0b en donne deux, « au choix » est un mot de
trop dans la promesse commerciale. Le catalogue est un livrable de T0b,
pas une option (§13, B8).

**O-10 — D32 protège notre coût, pas le client.** La licence Pixabay
autorise l'usage commercial, mais elle n'accorde ni exclusivité ni
transfert : le client qui reçoit la pub n'acquiert pas de droits sur la
musique, et une revendication Content ID reste possible s'il la diffuse
ailleurs. L'architecture garde la preuve (`ops.usage_audio`,
`licence_snap`, §8.7) ; elle ne peut pas créer le droit. À dire au client
en une phrase à la livraison, et à considérer comme la vraie raison de
passer à ACE-Step, bien avant l'unicité sonore.

**O-11 — « charte dans le prompt système » (D5) et isolation (D30) se
contredisent si le prompt système est une constante de déploiement.**
Trois chartes dans un prompt partagé sont une fuite par construction. Le
prompt est donc **assemblé par projet**, à partir du Brand Pack du client
courant. D5 est respectée (pas de mémoire sémantique, pas de base
vectorielle) ; c'est sa lecture naïve qui est écartée.

**O-12 — deux écarts de lettre, assumés, sur D2 et D3.** D2 confie au
classifieur l'aiguillage du canal admin : ici le numéro admin est
reconnu **avant** tout appel de LLM (§4.1, §9.1), car faire dépendre la
surface d'administration d'une décision de LLM est une mauvaise idée pour
un gain nul. D3 place les deux agents LLM « dans le Job » : le Storyboard
tourne dans `svc-conversation`, puisque D24 exige que le client le valide
**avant** que le Job ne démarre. Le Monteur, lui, est bien dans le Job.

---

## 13. Points ouverts qui bloquent une partie de l'architecture

Classés par ce qu'ils empêchent d'écrire, pas par urgence ressentie.

**B1 — Validation nocturne (O-1). BLOQUE** l'arête
`PENDING_REVIEW → DELIVERED` automatique, donc la fermeture de la machine
à états, donc la promesse D36. Décision attendue **avant T3** (étape 2 du
§11.8). Deux options, à trancher par Franco : (a) le délai de 4 h ne
court que pendant ses heures de veille — il faut alors le dire au client
et le mettre dans le message d'accusé de réception ; (b) validation
automatique de nuit, sous conditions vérifiables, sur templates déjà
validés. Recommandation : (b) pour les clients déjà servis, (a) pour un
premier projet — la conformité est binaire et vérifiée par code, c'est le
goût qui n'est pas automatisable, et le goût est déjà cadré par un
template approuvé.

**B2 — Moteur de rendu (D7, T0). BLOQUE** le gel de `capacites()`, du
contrat `template.schema.json`, de la règle C-5 (échelle typographique),
et la validité de D16 et D34 (O-5). Rien en aval du §5.1 ne doit être
figé avant le verdict de T0.

**B3 — Aligneur forcé non choisi. BLOQUE** le §8.3 et l'image de
`job-tts`. Sans lui, pas d'ancre `sur_mot`, donc les emphases et les
effets sonores se dégradent tous en `debut_scene` et le montage perd ce
qui le distingue d'un diaporama. À choisir en T0b.

**B4 — Constantes audio non mesurées. BLOQUE** la calibration de R-SB-1
(le débit de 2,6 mots/s est une hypothèse) et les six constantes du §8.
Conséquence concrète : tant qu'elles ne sont pas mesurées, `E_SURDUREE`
peut survenir sur un storyboard que R-SB-1 avait accepté. À mesurer en
T0b.

**B5 — Carte de paiement Google Cloud. BLOQUE** `job-tts`, donc toute la
voix off, donc D19 et D20, donc T3 entier. C'est le blocage le plus
grossier de la liste et le plus facile à découvrir trop tard : à tester
dès maintenant, avec le risque connu sur les cartes prépayées.

**B6 — Offre Supabase (O-3). BLOQUE** le 24/7 à partir de T3.

**B7 — Template utility Meta. BLOQUE** le §9.6, donc toute alerte hors
fenêtre de 24 h, donc le watchdog nocturne — c'est-à-dire précisément le
cas où le watchdog sert. Le délai est celui de l'approbation Meta : à
déposer maintenant.

**B8 — Catalogue de voix (O-9). BLOQUE** le slot « voix » du
clarificateur et la règle R-SB-3 (validation de `voix_id`). Livrable de
T0b.

**B9 — Contrats de base non fournis.** Les amendements A1 et A2 (§6) sont
écrits **au niveau des champs**, contre la structure décrite par le
document d'état : les fichiers `storyboard.schema.json` et
`composition.schema.json` existants ne m'ont pas été transmis avec ce
document, et ce dépôt ne les contient pas. Les noms des champs
**préexistants** cités dans les tableaux « avant/après » sont donc à
confirmer au moment d'appliquer les amendements ; les champs **ajoutés**
et les règles R-SB / R-CO sont complets et indépendants de ce point.

**Non bloquants**, pour mémoire : fournisseur LLM (n'affecte que
l'estimation de coût du §5.2 et le budget de prompt du Monteur) ;
couverture audio de l'API Pixabay (l'import manuel est déjà le plan) ;
survie du tatouage Chatterbox à l'AAC (à constater, sans effet sur
l'architecture) ; durée maximale du statut WhatsApp au Burkina (la limite
de 30 s est déjà la plus basse des trois plateformes) ; langues locales et
clonage de voix (hors v1) ; modèle commercial (les plafonds du §2.8 sont
des paramètres, pas une structure) ; statistiques de diffusion (elles
alimenteraient `history`, qui les accueille déjà).
