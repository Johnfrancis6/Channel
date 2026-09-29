# Contexte de reprise — HyperMaker — 29/09/2026

*À coller au début d'une nouvelle session. Remplace tout l'historique.*

---

## 1. Lis ceci avant tout

Projet **HyperMaker** : agent WhatsApp qui produit des pubs verticales
9:16 pour marques et startups. 3 clients, ~60 projets/mois, développement
solo, un client existe déjà. Dépôt `Johnfrancis6/Hypermaker`.

| À lire | Contenu |
|---|---|
| `setup/*.schema.json` et `setup/*.rules.md` | Les 5 contrats de données et leurs règles S, M, R, T, B. **Ne jamais inventer, renommer ni « améliorer » un champ.** |
| `docs/architecture/` (14 fichiers, `00-` à `13-`) | L'architecture d'exécution. `docs/architecture_runtime_v1.md` n'est qu'un **sommaire**. |
| `docs/rapport_T0.md` | Le verdict de T0 et les quatre défauts de déterminisme. |
| `docs/prompts/relance.md` | Périmètre, contraintes dures, méthode. |

---

## 2. Où en est le projet

**T0-technique est terminé** (rapport `8266808`, recette `6dc5e5d`).
**L'étape suivante n'est pas T1 : c'est T0.5, l'application des
corrections de contrats** (§5). Entrer dans T1 en codant contre R4, dont
on sait que le test prescrit ne teste rien, serait construire sur un
défaut connu.

### Les trois questions

- **Q1 — oui.** Le DOM est inspectable avant capture. Le lint vérifie les
  450 frames dans le même Chrome que la capture, en 75 à 162 ms. Pas
  d'échantillonnage nécessaire, même en production.
- **Q2 — oui, mais seulement entre le manifeste et le HTML.** Entre la
  composition et le HTML, **ça ne tient pas** : la composition ne dit pas
  quel slot remplit chaque couche (É-17). Elle ne sait pas non plus
  exprimer une animation d'entrée pour une image, ni l'amplitude d'un
  glissement ou d'un zoom (É-20, É-21).
- **Q3 — oui, après quatre correctifs.** Chaque jeu donne le même hash sur
  ses trois rendus, fichiers encodés identiques octet pour octet.

### Critères d'acceptation

Tous tenus **sauf un** : le débit audio du master, 2,3 kbps mesurés
contre 128 exigés, parce qu'une piste silencieuse ne peut pas atteindre ce
débit. Tranché au §4.1.

Format conforme. Aperçu conforme, 1 à 1,9 Mo. Rendu de 15 s en 15 à
16,6 s — mais **sur 12 cœurs, pas sur les 4 vCPU de production** : à
remesurer. Aucune ligne de code modifiée entre les trois jeux, vérifié par
arbre propre avant et après.

### Les quatre défauts de déterminisme, et leur leçon

1. Frame 0 vide dans tous les rendus, et parfois les frames 150 à 224.
2. Hash dépendant du nombre de workers que le moteur choisit seul.
3. Deux façons de dessiner l'opacité, choisies par Chrome au lancement.
4. Fichiers encodés différents à partir des mêmes images, par le
   *threading* de x264.

**La leçon vaut plus que les correctifs** : le harnais ne pouvait pas voir
le premier défaut, parce qu'il comparait deux rendus qui se trompaient de
la même façon. Un commit (`8844b19`) avait conclu trop vite sur deux
rendus ; c'est un troisième, celui de la recette, qui a révélé le défaut
d'opacité. **Deux mesures d'accord ne prouvent rien si elles partagent la
même cause d'erreur.**

La preuve reste statistique : 16 rendus sur 16 identiques, ~27 % de
chances qu'un défaut rare n'ait pas encore été vu. En intégration
continue, ne te contente pas d'augmenter le nombre de rendus : **fais-les
varier sur le nombre de cœurs**, puisque deux des quatre défauts en
dépendaient.

---

## 3. Décisions actées — ne pas rediscuter sans raison nouvelle

**Moteur et rendu**

- `hyperframes@0.8.83` épinglé exactement ; Chrome `152.0.7977.30`.
  **La version du moteur n'épingle pas Chrome** : c'est l'image du
  conteneur qui pin le couple, et les deux vont au rapport.
- `fps = 30` partout.
- Frames **PNG sans perte**, puis **une seule** commande FFmpeg de notre
  code pour l'aperçu et le master. Aucun remux après encodage.
- `hash_frames` sur les **pixels décodés** (`framemd5`) fait foi ; le hash
  de fichier est informatif.
- Adaptateur = **un seul `rendre.mjs`**, champs de `ResultatRendu` figés :
  `duree_ms`, `frames`, `hash_frames`, `polices_ok`.
- **Quatre règles de rendu issues de T0** : état à t = 0 posé dans le DOM,
  `will-change` sur toute opacité animée, **un seul worker**, **x264 sur
  un thread**. Emplacement tranché au §4.4.

**Polices**

- Inter OFL, `.woff2` commités avec `OFL.txt`, déclarée sous la **famille
  privée `HM-Demo-Sans`** — pour qu'une police publique homonyme ne puisse
  pas se faire passer pour la nôtre.
- Pas de fragment de Brand Pack : B4 ne gouverne que les Brand Packs, et
  T0 n'en a pas.
- Démo : `--brand-fond: #0E1116`, `--brand-texte: #FFFFFF`,
  `--brand-accent: #FF5A1F`, `--brand-secondaire: #9AA4B2`.

**Fixtures**

- Sous-ensemble **fidèle** de `Composition.schema.json` + un fichier
  `fixture-X.omissions.json` qui liste les chemins omis et leur raison.
  Validation `ajv` contre le vrai schéma, `required` relâchés pour les
  seuls chemins déclarés.
- `animation.start_ms` est **global**, pas relatif à la scène.

**Règle réseau en vigueur**

> Un rendu échoue si **une donnée franchit la frontière** : toute
> connexion TCP hors boucle locale ; tout envoi d'octets sur un
> descripteur associé à une adresse hors boucle locale ; toute connexion
> UDP hors boucle locale, **sauf** la sonde IPv6 de Chrome —
> `AF_INET6`, `SOCK_DGRAM`, `connect` vers `2001:4860:4860::8888:443`,
> et **zéro octet émis sur ce descripteur de `socket()` à `close()`**.
>
> Toute tolérance est nommée, pinée à une adresse, et se retourne en échec
> dès qu'un octet part.

Le principe : **c'est la donnée qui franchit, pas l'appel système.**

**Hors T0 — décidé, pas encore en jeu**

- Validation nocturne : **Franco valide lui-même 24 h/24**. Rien à
  construire. L'horloge de service et `history.revue` restent en place.
- Fenêtre de non-réutilisation musicale : **30 jours**.
- Plafonds **proposés, non confirmés** : 200 / 50 / 30 c par projet,
  15 000 / 3 000 / 2 000 c par mois, en **cents de dollar**.
- LLM : **Groq `openai/gpt-oss-120b`**. `strict` y est ignoré → budget de
  reprise du Monteur scindé en **3 tentatives de forme** et **1 reprise de
  fond**. Appels gratuits ⇒ le plafond ne protège plus d'une boucle : ces
  deux bornes sont la seule barrière. Adaptateur à **deux fournisseurs**.
- `job_relancer` sur `E_BUDGET` **recharge** le budget, avec audit.

---

## 4. Les quatre points tranchés le 29/09

### 4.1 Débit audio du silence

**Essaie d'abord de forcer le débit** : `-b:a 128k` sur la source
`anullsrc`. Raison de principe, plus forte que le critère lui-même — la
composition **déclare** `audio.bitrate_kbps: 128`, et R2 a calculé le
budget d'encodage en supposant ces 128 kbps dépensés. Un fichier à
2,3 kbps contredit sa propre composition et fausse l'arithmétique de R2,
même si c'est dans le sens inoffensif.

**Mesure ensuite** : l'encodeur AAC peut refuser de remplir un débit sur
du silence pur. Si c'est le cas, **É-24 s'applique** — le seuil de
128 kbps rejoint É-13 et ne s'applique que si `silent_fallback` est faux ;
sinon « non applicable : silent_fallback », ni succès ni rejet. Les
assertions de présence, codec, canaux et fréquence restent inconditionnelles.

### 4.2 R4 et B4

**Réécrites, et en tête du lot.** Remplacement :

> Pour chaque `font_ref` effectivement utilisé, il doit exister dans
> `document.fonts` une `FontFace` dont la famille, la graisse et le style
> correspondent à `composition.fonts[]`, **et dont `status` vaut
> `loaded`** — après `document.fonts.ready` et après mise en page, et
> seulement pour les familles réellement utilisées par des éléments
> rendus. `document.fonts.check()` peut rester comme filtre préalable ;
> un `true` de sa part ne prouve rien.

La restriction aux familles réellement rendues évite les faux négatifs :
les polices se chargent paresseusement, et une `@font-face` que rien
n'utilise reste légitimement `unloaded`.

### 4.3 Espace colorimétrique — É-25

C'est exactement la règle du projet : **l'encodeur choisit, donc le
contrat est incomplet.** Et l'enjeu est réel pour une activité de pub de
marque — un espace mal étiqueté décale les couleurs à la lecture, et
c'est la couleur de la marque du client qui dérive.

**BT.709, plage limitée, étiquetés explicitement** :
`-colorspace bt709 -color_primaries bt709 -color_trc bt709` et
`-color_range tv`. BT.601 est un héritage de la définition standard et n'a
rien à faire sur du 1080×1920 livré à TikTok et Meta. sRGB, dans lequel
Chrome rend, partage les primaires et le point blanc de BT.709 : la
conversion ne porte que sur la fonction de transfert et la plage.

Surveille la plage de près : ton `--brand-fond` est `#0E1116`, un
quasi-noir. Une erreur pleine/limitée s'y verra immédiatement, en noirs
écrasés ou délavés.

Le contrat doit gagner un bloc couleur dans `encode` ; en attendant, les
valeurs sont pinées dans les règles de rendu.

### 4.4 Où écrire les quatre règles de rendu

Elles sont de deux natures, et les mélanger serait une erreur :

- **Règles d'authoring** — état à t = 0 posé dans le DOM, `will-change`
  sur toute opacité animée. Elles contraignent **le template** →
  `Template.rules.md`, et le contrôle statique T11 les vérifie.
- **Règles d'invocation** — un seul worker, x264 sur un thread. Elles
  contraignent **l'adaptateur**, pas le template → §5.1 de l'architecture,
  et surtout **appliquées par le code de `rendre.mjs`**, pas seulement
  documentées. Une règle d'invocation écrite dans un document se perd ;
  la même en argument de ligne de commande ne se perd pas.

Les quatre restent aussi au rapport T0, parce que ce sont des faits
découverts sur **ce couple moteur + Chrome** : changer l'un ou l'autre
oblige à les redériver.

---

## 5. La suite : T0.5, puis T1

**T0.5 — appliquer le lot de corrections de contrats.** Court, mécanique,
et il évite que la liste d'écarts pourrisse.

À appliquer maintenant, parce que T1 consomme ces contrats :

| # | Correction |
|---|---|
| É-23 | R4 et B4 réécrites (§4.2) |
| É-19 | `$comment` sur `animation.start_ms` : global, quand `camera.keyframes[].t_ms` est relatif à la scène |
| É-13 | R10 = deux contrôles : présence toujours, volume seulement si `silent_fallback` est faux |
| É-14 | R11 : le hash de **frames** fait foi, le hash de fichier est informatif |
| É-24 | Débit audio du silence, selon la mesure du §4.1 |
| É-25 | Bloc couleur dans `encode` : BT.709, plage limitée |

**À différer avant T2**, parce qu'elles demandent une passe de conception,
pas une correction :

| # | Objet |
|---|---|
| É-16 | Le Brand Pack de démo n'a pas de propriétaire — c'est une **ressource partagée**, comme `owner.scope: "shared"` |
| É-17 | **`slot_id` absent de `layer` et `text_element`** — bloquant pour T2. Le vocabulaire existe déjà dans `montage_plan.broll[]` |
| É-20/21/22 | **La grappe du mouvement** — voir ci-dessous |

**Déjà corrigés dans les contrats** : É-1 (idempotence bornée au client,
clé `(client_id, generation_key)`) et É-7 (R14 sur `start_ms + attack_ms`).

### La grappe du mouvement — la vraie découverte de T0

Ce ne sont pas trois défauts mais un seul : **la composition sait exprimer
la mise en page et le temps, mais pas le mouvement.** Le Brand Pack porte
les maps, le template porte les beats, `text_element.animation` porte le
canal résolu pour le texte — **il n'existe pas pour les médias**. `layer`
n'a qu'une `opacity` statique et `media_start_ms` ; `slide_in`, `scale_in`
et `mask_reveal` n'ont pas d'amplitude, donc seul `fade_in` est utilisable.

Elle pèse sur le **critère B** — la façon dont un sujet entre à l'écran
est une grande part de ce qui sépare « monté par un pro » d'un diaporama.
Et la contrainte est **dans le contrat, pas dans HyperFrames** : le moteur
sait animer ce qu'on veut. Une passe de conception avant T2, sans quoi on
écrira trois templates qui ne pourront pas s'en servir.

### Les autres écarts, pour mémoire

É-2 (`FAILED` terminal vs `job_relancer`, transition T17 assumée) ·
É-3 (Supabase gratuit incompatible avec le 24/7, à payer avant T3) ·
É-4 (D26 et D27 se recouvrent, `expire_le = clos_le + 10 j` pour les
objets de correction) · É-5 (D7, D16, D34 sont un seul pari — **tranché
par T0 : le DOM est inspectable, D16 tient**) · É-6 (`plafond_mois_c`) ·
É-8 (D24 valide une durée qui n'existe pas, R13 avertit à ±25 %) ·
É-9 (Pixabay protège notre coût, pas le client) · É-10 (« quelques
minutes » hors d'atteinte ; D22 ∧ D36 résolu par engagement) ·
É-11 (catalogue de voix, T0b) · É-12 (écarts de lettre D2/D3) ·
É-15 (**le GPU du Job TTS n'est peut-être pas nécessaire** — seuil :
8 scènes de 4 s en moins de 5 min sur 8 vCPU, mesure en T0b ; s'il tombe,
`job-tts` disparaît et le blocage de la carte Google Cloud avec lui) ·
É-18 (`provenance.source` sans valeur pour une fixture).

### Portes encore fermées

- **T0-qualité** attend les assets du premier client — date non fixée. Le
  critère B et donc le verdict complet sur D7 en dépendent.
- **Le pipeline audio et le Monteur** attendent T0b : les constantes ne
  sont pas mesurées.
- **Les templates supplémentaires** attendent la passe de conception sur
  le mouvement.

---

## 6. Méthode — ce qui a marché, à continuer

- **Propose un plan court avant d'écrire du code.** Attends validation.
- **Si une information manque, demande.** N'invente pas.
- **Prouve qu'un détecteur détecte.** Six fixtures cassées volontairement
  et rejetées ; un rendu avec requête sortante délibérée, qui a révélé un
  bug de parseur IPv6 dont le premier résultat « propre » était un **faux
  négatif rassurant**. Un détecteur non éprouvé raconte ce qu'on veut
  entendre.
- **Deux mesures d'accord ne prouvent rien** si elles partagent la même
  cause d'erreur. C'est un troisième rendu qui a trouvé le défaut
  d'opacité.
- **Une seule implémentation par mesure.** Le comptage de lignes est
  partagé entre le runtime et le lint.
- **Un écart se signale, il ne se contourne pas.** Contourne par le cas le
  plus simple, consigne, continue.
- **Un commit par livrable**, message en français qui dit *pourquoi*.
- Critère de conception : **éviter la sur-ingénierie**. Pas d'abstraction
  « au cas où ».
