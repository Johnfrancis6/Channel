# Format long — briefing de session (faisabilité d'abord)

Document de contexte pour une **nouvelle session**. Son premier travail
n'est pas de coder : c'est d'établir la **faisabilité** de chaque point
ci-dessous sur le code réel (pas sur cette description) et de lister ce
qui doit être précisé ou corrigé avant d'écrire quoi que ce soit. Une fois
ce diagnostic fait, il rejoint la file de [diagnostic_pipeline.md](diagnostic_pipeline.md)
ou devient son propre plan de construction — à trancher en fin de session.

Décidé en séance le 16/09/2026, à ne pas rouvrir sans raison :
- **Nouveau pilier de format en ajout**, la chaîne garde ses Shorts tels quels.
- **Toujours du Remotion scène par scène**, comme les Shorts — pas une bascule
  vers un montage de sources réelles.
- **L'animation domine** ; la vidéo réelle n'intervient qu'à de **courts
  instants**, en **zooms dynamiques** sur un point précis — pas en plan de
  liaison continu, pas en contenu principal.

Ouvert, à trancher en tout début de session (bloque le point 4 ci-dessous) :
- **D'où viennent les rushes ?** Franco dépose des fichiers bruts dans le
  dossier de la vidéo (comme `assets/` aujourd'hui, §9.1), ou il y a une
  étape de sélection/pré-découpage avant E5 ? Ça détermine si le point 4
  est juste une extension de composant, ou si ça ajoute une étape/agent.

---

## Ce que la lecture du code a déjà établi (16/09/2026)

À vérifier plutôt qu'à refaire : ce sont des faits de code, mesurés une
fois, pas une intention.

- `pilier` (schéma, `new_short.py > PILIERS`) désigne le **sujet**
  (`actu_ia`, `tuto`, …), pas le format. Un format long n'est **pas** un
  6ᵉ pilier au sens du code actuel — c'est une dimension orthogonale. Il
  faut un nouveau champ, pas une entrée de plus dans `PILIERS`.
- `consignes.format` existe déjà et désigne le **format narratif**
  (`explication_progressive`, etc.) — collision de nom à éviter avec le
  nouveau champ court/long. Proposition de départ : `format_video`
  (`"short" | "long"`), à discuter.
- `composants/src/Root.tsx` a `width={1080} height={1920}` **en dur**, et
  `charte.json > format` porte les mêmes valeurs. Rien n'a jamais été
  rendu en paysage.
- **`composants/src/components/PlanBroll.tsx` existe déjà** et compose du
  vrai footage (`OffthreadVideo` / `Img`) via un système de ressources
  keyé par string (`ressources?.[broll]`, `asset.src`, `asset.duree_s`).
  Mais il est câblé pour un **plan de liaison court** : voile sombre en
  dégradé systématique, zoom `punchIn`, boucle (`<Loop>`) si le clip est
  plus court que la scène. Pour des « zooms dynamiques à certains points
  » sur un contenu à dominante animée, c'est probablement le bon point de
  départ (le mécanisme de ressources et le zoom existent déjà) mais pas
  le bon comportement par défaut tel quel — le voile et la boucle
  supposent un rôle de fond, pas un insert ponctuel.
- Le dossier `assets/` d'une vidéo (§9.1) est documenté comme « images
  d'inspiration déposées par Franco » — pas pensé comme dépôt de rushes
  vidéo avec métadonnées de durée/contenu.

---

## Les 10 points touchés (établis en séance, à valider en session)

Pour chacun, la nouvelle session doit répondre à **trois questions** avant
de planifier du travail : c'est faisable tel quel ? qu'est-ce qui manque
dans le code actuel pour le faire proprement ? qu'est-ce que la séance
précédente a mal cadré ou oublié ?

1. **Schéma et état** — `schemas/state_schema.json`, `state_template.json`,
   `new_short.py` : champ format, nom à trancher (collision avec
   `consignes.format`).
2. **Budget / calibrage (A5, §7.3)** — `metriques.py`, seuils
   `ok`/`limite`/`depasse` : un format long n'est pas juste « plus
   d'idées », la structure narrative change (segments, respiration,
   peut-être plusieurs blocs de script). À creuser : est-ce que le modèle
   `idees_max × mots_par_idée ÷ 2,8 mots/s` (§7.3, diagnostic_pipeline.md)
   tient encore, ou faut-il un modèle différent pour le long format.
3. **Charte / tokens de format** — `profil_defaults.py > CHARTE_JSON`,
   `00_Profil/charte_visuelle/` : format unique aujourd'hui, à étendre
   en structure à deux formats sans casser les Shorts existants.
4. **Remotion** — cf. section dédiée ci-dessous, c'est le point le plus
   gros et le plus ouvert.
5. **Storyboard / cadrage (A6, §4.3, §8)** — « une scène par phrase »
   (règle actuelle) ne tient pas sur 150-300+ phrases d'un long format.
   Découpage par segment/bloc à définir ; impact sur le recalage
   audio/image (§8, `04_phrases.json`) à vérifier.
6. **Voix off (§7.2)** — le WER **global** du notebook fait échouer tout
   le run sur une seule phrase ratée ; déjà noté comme décision ouverte
   au §12 de `architecture_chaine_v1.2.md`, mais optionnel pour un Short
   de 50 s. Sur un run de 10-20 min, l'évaluer devient probablement
   nécessaire plutôt que « à reprendre si les runs réels le montrent
   fréquent ».
7. **Monteur (A7, §8)** — `rendre_video.py`, temps de rendu, protocole
   « images fixes avant CP3 » à étendre pour couvrir plus de points sur
   une vidéo plus longue.
8. **Checkpoints (§5.5)** — le rapport CP3 (storyboard borné à 1200
   caractères) ne passe pas à l'échelle sur un long script ; résumé par
   segment à concevoir.
9. **Tests** — `tests/test_render_remotion.py`, `test_recalage_scenes.py`,
   `test_apercus.py` : cas de format long à ajouter.
10. **Doc** — `docs/architecture_chaine_v1.2.md` §1, §7.3, §8, §9.1 à
    mettre à jour une fois les décisions prises, pas avant.

---

## Point 4 en détail — Remotion, scène par scène, footage en zooms ponctuels

Contrainte actée : l'animation domine toujours, la vidéo réelle n'apparaît
qu'à de courts instants en zoom dynamique sur un point précis — jamais en
plan de fond continu.

Ce que ça implique, à vérifier en session :

- **`PlanBroll` n'est probablement pas le bon composant à réutiliser tel
  quel** : son rôle (plan de liaison, voile systématique, zoom
  d'ambiance) ne correspond pas à un insert ponctuel sur un point précis
  pendant qu'une scène animée est en cours. Un nouveau composant (nom de
  travail : `ZoomFootage` ou similaire) est probablement plus propre
  qu'une variante de `PlanBroll` — à évaluer sur le code réel, pas
  supposé.
- **Le mécanisme de ressources (`ressources?.[clé]`, `asset.src`,
  `asset.duree_s`) est réutilisable tel quel** pour référencer un clip
  court. Pas besoin de le refaire.
- **`04_phrases.json` / recalage (§8)** : un insert vidéo ponctuel dans
  une scène animée ne doit pas décaler les bornes de phrase — c'est un
  détail *dans* une scène, pas une scène de plus. À vérifier que le
  modèle de scène actuel (durée, `da`, `phrases: [...]`) supporte un
  sous-élément temporel (ex. « zoom entre 2,1 s et 3,4 s de la scène »)
  sans tout redessiner.
- **Rushes** : dépend de la question ouverte en tête de document.

---

## Ce que la session doit produire

1. Un diagnostic de faisabilité par point (1 à 10), avec pour chacun :
   faisable tel quel / bloqué par quoi / ce qui a été mal cadré ici.
2. Une réponse tranchée à la question des rushes (tête de document).
3. Un nom de champ définitif pour `format_video` (ou équivalent),
   propagé au schéma.
4. Une décision sur le point 4 : nouveau composant vs extension de
   `PlanBroll`.
5. Seulement après ça : un plan de construction ordonné, sur le modèle du
   §13 de `architecture_chaine_v1.2.md` (« chaque étape testée avant de
   passer à la suivante »).

Ne pas coder avant l'étape 5. Le risque identifié dans cette séance est le
même que celui déjà écrit au §12 pour le multi-chaînes : préparer le
terrain avant d'avoir produit une seule vidéo dans le nouveau format,
c'est généraliser sur zéro exemple.

---

# Diagnostic de faisabilité (session du 16/09/2026)

Établi en lisant le code, pas la description ci-dessus. Quatre constats
transverses d'abord : ils déplacent trois des dix points, et le dernier
remet en cause l'ordre dans lequel ce chantier doit être pris.

## A. Le point 4 n'a pas de producteur — et ça, ce n'est pas un détail de cadrage

Le briefing traite la question des rushes comme une précision à obtenir.
C'est en fait un chantier entier, **déjà dans la file, déjà ouvert** :

| Maillon | État réel |
|---|---|
| `PlanBroll` lit `ressources?.[broll]` | ✅ existe |
| `construire_props.preparer_ressources()` résout `05b_ressources.json` | ✅ existe |
| Contrat `Besoin` / `Ressource` dans `types.ts` | ✅ existe |
| **Quelque chose qui écrit `05b_ressources.json`** | ❌ **A8, file #18, ⬜** |
| **Quelque chose qui trouve un clip** | ❌ `chercher_broll.py`, file #19, ⬜ |

Le tuyau footage → écran est complet et ses **deux bouts sont ouverts**.
Aucune vidéo réelle n'est jamais passée par `PlanBroll` : il a été écrit,
mis au registre, et jamais alimenté. Le format long n'ajoute pas ce
problème, il en hérite — et il ne peut pas le contourner, puisque son
pilier visuel *est* l'insert de footage.

**Conséquence sur l'ordre** : #18 et #19 ne sont pas des prérequis du
format long qu'on découvre ici, ce sont des chantiers qui bloquent déjà
`PlanBroll` sur les Shorts. Les faire sert les deux formats.

## B. Point 6 (WER) — le blocage n'est pas le seuil, c'est l'absence de cache

Le briefing dit : « le WER global fait échouer tout le run sur une seule
phrase ratée ». Exact, mais ce n'est pas le coût dominant. Le vrai défaut
est dans la Cell 4 :

```python
clips_bruts = []      # liste de (audio_np, taux) — une entrée par phrase
for i, phrase in enumerate(phrases):
    audio_np, taux = synthetiser_phrase(phrase, GRAINE + i)
    clips_bruts.append((audio_np, taux))
```

Les clips vivent **en RAM uniquement**. Rien n'est écrit sur disque avant
l'assemblage de la Cell 5. `MODE="resume_after_fail"` re-synthétise donc
l'intégralité du script depuis zéro.

Sur 24 phrases (vidéo 1), c'est quelques minutes. Sur les 150-300 phrases
d'un format long, c'est une session Colab complète perdue à chaque échec
— et une session Colab a un timeout, donc l'échec peut devenir
structurel : un run trop long n'atteint jamais la Cell 5, et il n'en
reste rien.

La synthèse est déjà **phrase par phrase** avec une graine par phrase
(`GRAINE + i`), donc déterministe et reprenable : le cache manquant est
une trentaine de lignes, pas une refonte. C'est un correctif qui a de la
valeur **dès maintenant**, format long ou pas.

Le WER par phrase, lui, devient effectivement nécessaire — mais il n'a
d'intérêt qu'une fois le cache en place : re-synthétiser trois phrases sur
trois cents ne sert à rien si le run repart de la phrase 1.

## C. Point 7 — le rendu a exactement le même défaut, et le briefing ne le voit pas

`rendre_video.py` lance un `remotion render` monolithique :

```python
cmd = ["npx", "remotion", "render", "src/index.ts", "Video",
       str(sortie_path), f"--props={props_path}"]
```

Pas de `--concurrency`, pas de découpage, pas de reprise. 10-20 min à
30 fps = 18 000 à 36 000 frames, rendues en PNG (file #27). Un échec à
80 % perd tout.

C'est le même défaut de forme que la voix off : **le pipeline n'a aucun
mécanisme de reprise partielle, ni sur l'audio ni sur l'image**. Tant que
les vidéos durent 50 s, ça ne se voit pas. Le format long ne crée pas ce
défaut, il le rend bloquant aux deux endroits à la fois. Le point 7 parle
de « temps de rendu » et du protocole d'images fixes ; il passe à côté du
point de rupture.

## D. Point 8 — le rapport CP3 casse avant d'atteindre le budget de 1200

Le briefing accuse la troncature à 1200 caractères. Mais cette borne ne
s'applique qu'à `_lire_extrait(05_storyboard.md)`. Ce qui déborde d'abord
est dans `_resume_video_finale`, **hors budget** :

```python
a_completer = [sc.get("id") for sc in scenes if sc.get("a_completer")]
lignes.append(f"- ⚠️ **Scenes non tranchees par le Designer** : {', '.join(...)}")
```

Sur 200 scènes, c'est une ligne de 200 identifiants, en tête du rapport,
que rien ne tronque. Idem pour `nouveaux_composants_necessaires`. Le
résumé par segment reste à concevoir — mais le premier correctif est de
plafonner ces énumérations, ce qui est petit et utile tout de suite.

---

## Point par point

**1. Schéma et état — faisable tel quel.**
Le schéma n'a pas `additionalProperties: false` au niveau racine (il ne
l'a que sur `etapes`) : ajouter un champ ne casse aucune validation
existante. Trois fichiers à toucher ensemble — `state_template.json`
(source de vérité, §13), `schemas/state_schema.json`, `new_short.py`.

**Nom recommandé : `format_video`, au niveau racine, à côté de `pilier`
et `voie` — pas dans `consignes`.** La raison n'est pas seulement la
collision de nom. `consignes` porte ce que Franco demande *à un agent*
(`mode_recherche`, `note_franco`, `reference`) ; court/long change le
pipeline lui-même — le budget, la charte, la stratégie de rendu — au même
titre que `voie`, qui est bien à la racine. Enum fermé
`"short" | "long"`, défaut `"short"` pour que toutes les vidéos
existantes restent valides sans migration.

**2. Budget / calibrage — faisable, mais le modèle n'est pas mesuré.**
`evaluer_budget()` est de l'arithmétique pure et accepte déjà
`--budget-mots`, qui court-circuite `--idees × --mots-par-idee`. Aucun
code à changer pour qu'un format long ait son budget.

Ce qui manque est en amont : `MOTS_PAR_SECONDE = 2.8` est calibré sur
**une seule vidéo de 82,5 s**. L'extrapoler à 20 min est une hypothèse.
Un débit moyen sur 20 min intègre des respirations, des changements de
rythme et des pauses de section qu'un Short de 50 s n'a pas — il sera
plus bas, d'un montant que personne ne connaît. Et la décision transverse
« les formats se découvrent sur les 6 premières vidéos » donne déjà n=1
par format : un format long serait un 7ᵉ format à n=0.

**Ce que le briefing a mal cadré** : il demande si le modèle
`idées × mots/idée ÷ 2,8` « tient encore ». La bonne question est
antérieure — le modèle n'a jamais été validé sur *quoi que ce soit*
d'autre que la vidéo 1. Il ne s'agit pas de l'étendre, il s'agit de ne
pas confondre une constante mesurée une fois avec une loi.

**3. Charte / tokens — faisable, avec un piège de déploiement.**
`init_structure.py` écrit `charte.json` via `_ecrire_si_absent` :
**changer `CHARTE_JSON` dans le code ne met pas à jour la charte déjà
posée sur le Drive de Franco.** Toute évolution de structure demande soit
une migration explicite, soit une lecture tolérante côté composants (ce
que `types.ts` fait déjà pour `animation` et les niveaux typographiques,
avec le bon commentaire à l'appui).

Passer `format: {...}` à `formats: {short: {...}, long: {...}}` casserait
`Root.tsx`, `generer_apercus.py` (1080×1920 en dur ligne 104) et toute
charte antérieure. **Chemin moins cher** : garder `charte.format` et
remarquer que `Root.tsx` a déjà la primitive nécessaire —
`calculateMetadata` reçoit les props et peut retourner `width`/`height`
autant que `durationInFrames` :

```tsx
width={1080} height={1920}          // en dur sur <Composition>
calculateMetadata={async ({props}) => ({
  durationInFrames: dureeTotaleFrames(props.scenes, FPS, props.duree_audio_s),
})}
```

Les dimensions en dur sont donc un **défaut**, pas un verrou : elles
peuvent venir de `props.charte.format` sans rien changer d'autre. C'est
le correctif à faire, et il est petit.

**4. Remotion — faisable, mais pas sous la forme proposée. Voir la
section dédiée plus bas.**

**5. Storyboard / cadrage — le recalage n'est pas le problème.**
Le briefing craint pour le recalage audio/image. Vérification faite,
**c'est déjà réglé** : `_fins_par_scene()` accepte depuis la file #11 que
chaque scène déclare `phrases: [...]` et n'exige plus 1:1. Regrouper
30 phrases dans une scène de segment marche tel quel.

Ce qui casse vraiment est ailleurs : `construire_scenes()` produit
littéralement une scène par ligne, toutes marquées `a_completer`, sans
plafond. Sur 300 phrases, le squelette livré à A6 fait 300 scènes à
trancher une par une — ce n'est pas une charge de travail, c'est un
livrable indéfendable, et A6 le rendra en sautant des scènes. Le
découpage par segment doit être fait **par le générateur de squelette**,
pas laissé à A6.

**6. Voix off — bloquant. Voir B ci-dessus.** Le point est correctement
identifié comme nécessaire, mais pour la mauvaise raison, et le correctif
qu'il suggère (WER par phrase) n'a d'effet qu'après celui qu'il ne
mentionne pas (cache par phrase).

**7. Monteur — bloquant. Voir C ci-dessus.** Le protocole « images fixes
avant CP3 » est le moindre des sujets : sur 200 scènes, une image par
scène n'est plus une passe de critique, c'est une planche-contact que
personne ne regarde. À repenser en échantillonnage, mais après le
problème de rendu.

**8. Checkpoints — faisable. Voir D ci-dessus.**

**9. Tests — faisables, avec une réserve.** `test_render_remotion.py` se
saute déjà sans `node_modules`, et un test de rendu long serait de toute
façon trop lent pour la suite. Ce qui doit être testé à l'échelle du
format long, c'est `construire_props.recaler_scenes()` et
`dureeTotaleFrames()` sur 200-300 scènes — du Python et de
l'arithmétique, rapides — pas le rendu lui-même.

**10. Doc — d'accord, après les décisions.** À ajouter à la liste du
briefing : §5 (le champ `format_video` dans le `state.json` d'exemple) et
§12, où ce chantier a sa place dans les décisions ouvertes.

---

## Point 4 en détail — la vraie question n'est pas quel composant

Le briefing pose l'alternative « nouveau composant `ZoomFootage` vs
variante de `PlanBroll` ». Le code dit que les deux branches sont
fausses, pour la même raison.

`Video.tsx` associe **un composant du registre à une scène entière** :

```tsx
const Composant = REGISTRE[scene.composant];
```

Un insert de footage ponctuel *pendant qu'une scène animée est en cours*
n'est donc pas un composant de scène du tout — quel que soit son nom.
S'il en devenait un, il redeviendrait exactement ce que la contrainte
actée interdit : un plan qui occupe le cadre, comme `PlanBroll`.

Il y a déjà un précédent pour ce qu'il faut, et un seul : **`Subtitles`**,
surimprimé au-dessus de la `TransitionSeries`, hors du registre, avec le
commentaire qui l'explique dans `registry.ts` (« ce n'est pas un choix
par scène »). L'insert de footage est de cette famille-là : une **surcouche
bornée dans le temps**, déclarée sur la scène, rendue par-dessus elle.

Trois vérifications faites sur le code, qui rendent ça peu coûteux :

- **Le modèle de scène supporte déjà un sous-élément temporel.**
  `pulsation_s` est exactement ça : un instant *dans* une scène, désigné
  par A6 en clair (`da.accent` = « …phrase 7 »), résolu en secondes au
  montage par `_pulsation_s()` depuis `04_phrases.json`, et converti en
  frame par `Video.tsx`. Un insert demande un **intervalle** au lieu d'un
  instant — même mécanique, une borne de plus. La crainte du briefing
  (« sans tout redessiner ») est levée : le précédent existe et il
  fonctionne.
- **Le mécanisme de ressources est réutilisable tel quel**, comme le
  briefing le dit. `asset.src`, `asset.duree_s`, la table `Ressources`
  passée à tous les composants — rien à refaire.
- **Le recalage n'est pas menacé.** Un insert interne ne change ni
  `duree_s` ni `phrases`, donc `recaler_scenes()` n'en sait rien et n'a
  pas à en savoir quelque chose.

Ce qu'il faut réellement écrire : un type `Insert` sur `Scene` (clé de
ressource, borne de début désignée comme `da.accent` le fait, durée), sa
résolution dans `construire_props.py` sur le modèle de `_pulsation_s()`,
et une surcouche de rendu dans `Video.tsx` sur le modèle de `Subtitles`.
Pas de nouveau composant au registre. `PlanBroll` reste ce qu'il est —
un plan de liaison plein cadre — et n'a pas à être tordu.

**Réserve, qui domine tout le reste** : cette conception ne peut pas être
validée sans un vrai clip à l'écran, et rien n'en produit aujourd'hui
(voir A).

---

## La question des rushes — tranchée le 16/09/2026

**Franco dépose ses propres rushes dans `videos/<id>/assets/`**, avec une
description (durée, ce qu'on voit). Pas de banque libre pour ce rôle, pas
d'étape de sélection en plus.

Le raisonnement : la contrainte actée est un zoom **sur un point précis**.
Un clip de banque illustre une ambiance ; il ne montre presque jamais le
point exact dont parle le script. Les rushes qui le montrent sont ceux que
Franco produit lui-même — une capture de démo, un enregistrement d'écran.

**Ce que ça change dans le code :**

- **Pas d'étape ni d'agent en plus.** C'est une extension du chantier #18
  (A8) : au lieu d'aller chercher, A8 indexe ce qui est déjà là et écrit
  `05b_ressources.json` comme prévu. Le point 4 reste donc bien un
  travail de composant, pas un travail de pipeline.
- **`assets/` change de nature.** Le §9.1 le documente comme « images
  d'inspiration déposées par Franco », lu par A6 et A7 pour cadrer. Il
  devient aussi un dépôt de matière montée, avec des métadonnées
  (`duree_s` au minimum, que `Ressource` porte déjà). Les deux usages
  cohabitent ; le §9.1 est à reformuler.
- **Il faut un format de description.** `Ressource` a déjà `duree_s`,
  `provenance` et `licence` ; ce qui manque est ce qu'A6 lit pour décider
  *où* poser le zoom — une phrase en clair par rush. Le plus petit chemin
  est un `assets/rushes.json` (ou des sidecars `<fichier>.json`), écrit
  par Franco ou par A8 à partir du nom de fichier.
- **#19 (banques libres) n'est pas annulé** : il garde son rôle pour les
  plans de liaison de `PlanBroll` sur les Shorts. Il n'est simplement plus
  sur le chemin critique du format long.

---

## Recommandation d'ordre — et la réserve du §12

Le briefing se termine en nommant le risque : « préparer le terrain avant
d'avoir produit une seule vidéo dans le nouveau format, c'est généraliser
sur zéro exemple ». La lecture du code le confirme et l'aggrave — la
chaîne n'a **aucune vidéo publiée** ; la vidéo 1 est au CP3, E7 n'a jamais
tourné, H1 non plus. Et la décision transverse « stabiliser le visuel
avant les 6 formats » dit que la seule variable qui doit bouger est le
format narratif : ajouter court/long en introduit une seconde, qui
polluera l'étude de la 6ᵉ vidéo exactement comme la variance visuelle
l'aurait fait.

Ordre proposé, du plus utile au moins urgent :

1. **#18** (A8), étendu aux rushes d'`assets/` selon la décision
   ci-dessus. Déjà dans la file, il débloque `PlanBroll` sur les Shorts
   *et* tout le point 4. Sans lui, le format long n'a pas de pilier
   visuel. #19 (banques libres) peut suivre à son rythme.
2. **Cache des clips par phrase** dans le notebook (B). Petit, sans
   rapport avec le format long, et il supprime le mode d'échec qui rend
   un long run impossible.
3. **Dimensions depuis `props.charte.format`** dans `Root.tsx` (point 3).
   Petit, et c'est le seul verrou dur du paysage.
4. **Plafonner les énumérations du rapport CP3** (D). Petit.
5. Le format long lui-même — champ `format_video`, découpage par segment,
   `Insert` — **après une deuxième vidéo publiée**, pas avant.

Les points 1 à 4 ont de la valeur sur les Shorts tels quels. Aucun n'est
un investissement à fonds perdus si le format long est repoussé.

---

# Mise en place — points 1 à 4 (16/09/2026)

Les quatre chantiers utiles dès maintenant sont faits. **Le point 5 — le
format long lui-même — n'est pas commencé**, conformément à la
recommandation ci-dessus : il attend une deuxième vidéo publiée.

## 1. Résolution des ressources — `outils/resoudre_ressources.py`

Le tuyau footage → écran avait ses deux bouts ouverts : A6 déclarait des
`besoins`, `construire_props` savait lire `05b_ressources.json`, les trois
composants `Plan*` savaient afficher le résultat, et **rien n'écrivait le
fichier du milieu**. Ils ont été écrits, mis au registre, et alimentés par
rien.

**Ce qui a été tranché en écrivant.** L'outil s'arrête là où commence le
jugement. Il fait la plomberie déterministe — télécharger un logo,
capturer une page, retrouver un fichier désigné, mesurer la durée d'un
clip — et sort en `non_resolus` tout besoin qui demande de décider *quel*
rush illustre *quelle* intention, avec la liste de ce qui est disponible.
C'est l'agent qui choisit, puis relance avec `--associer <clé>=<fichier>`.
Une correspondance par mots-clés aurait rendu un jugement qu'on ne peut
pas relire. C'est la même séparation que `generer_storyboard.py`, qui
livre un squelette et laisse le choix des composants à A6.

**Pas d'agent A8, pas d'étape de machine à états.** La décision sur les
rushes l'impliquait déjà ; l'outil est appelé par le Monteur à son étape
4a, juste avant de construire les props qu'il alimente. Rien ne bouge dans
le §6.2.

Trois façons de lier un rush à un besoin, de la plus explicite à la plus
implicite : `--associer` ; `assets/rushes.json` ; le nom du fichier
(`assets/<clé>.mp4`).

**Un détail qui aurait cassé le rendu en silence** : `PlanBroll` choisit
`<OffthreadVideo>` ou `<Img>` sur `type === 'broll'`, et `PlanCapture`
n'affiche sa barre de navigateur que sur `type === 'capture'`. Le type
écrit dans `05b_ressources.json` suit donc le **fichier**, pas la demande :
un besoin de b-roll honoré par une photo sort en `image`, avec un
avertissement. Sinon le composant tentait de lire un PNG comme une vidéo.

Le test qui compte est `TestRoundTrip` : la sortie de l'outil est
effectivement relue par `construire_props.preparer_ressources`. Un contrat
vérifié seulement sur ses propres assertions est exactement ce qui a
produit trois composants alimentés par rien.

## 2. Cache des clips TTS par phrase

La synthèse était déjà phrase par phrase avec une graine par phrase, donc
déterministe — mais les clips ne vivaient qu'en RAM. Chaque clip est
maintenant écrit dans `audio/clips/`, nommé par une empreinte de ce qui le
détermine : **texte, graine, voix de référence**. Un script corrigé ou une
graine changée invalident donc le cache d'eux-mêmes, ce qui évite un
drapeau de configuration de plus — et garde intact le conseil du notebook
sur un WER marginal (« relance avec une autre graine » produit bien une
vraie re-synthèse).

L'écriture se fait en deux temps (`.wav.tmp` puis `os.replace`) : un cache
dont le seul rôle est de survivre à une interruption ne peut pas se
permettre de relire un fichier tronqué comme s'il était bon.

## 3. Dimensions de composition depuis la charte

`Root.tsx` lit `props.charte.format` dans `calculateMetadata`, qui peut
retourner `width`/`height`/`fps` autant que `durationInFrames`. Les
valeurs en dur ne servent plus que d'amorce. **Vérifié par un rendu réel**,
pas seulement par le typecheck : une charte 1920×1080 produit un PNG
1920×1080, et le test le verrouille.

Le verrou dur du paysage est donc levé. Ce qui reste — et qui n'est pas
petit — c'est que les composants sont *composés* pour du vertical.

## 4. Énumérations du rapport CP3 plafonnées

Bornées à 12 entrées, puis « (+ N autres, sur M au total) ». Ces listes
vivaient hors du budget de caractères du §5.5 : sur 200 scènes, c'était
200 identifiants en tête du rapport, devant tout ce qui porte la décision.

## Ce qui n'a pas pu être vérifié ici

- **`ffprobe` n'est pas installé dans cet environnement.** La durée d'un
  clip retombe donc sur `rushes.json`, et l'absence est signalée en
  avertissement. Le chemin ffprobe lui-même n'a pas été exercé.
- **Ni `capturer_web.py` ni `recuperer_logo.py` n'ont été appelés en
  réseau** : les tests tournent en `--hors-ligne`, et le proxy du bac à
  sable refuse le web général (même réserve qu'à la séance du 15/09). Le
  premier appel réel reste à faire chez Franco.
- **Le cache TTS n'a pas été exécuté** : le notebook demande Colab et un
  GPU. Ce qui est testé ici, c'est la fonction de nommage, extraite du
  notebook et exécutée pour de vrai — l'invalidation est exactement la
  règle qu'un test par sous-chaîne aurait déclarée verte en se trompant.

---

# Mise en place — point 5, le format long lui-même (16/09/2026)

Fait **contre la recommandation d'ordre ci-dessus**, sur décision explicite
de Franco en séance : il veut le format long avant d'avoir publié une
deuxième vidéo. La réserve n'est pas levée pour autant — elle est reportée
au §12 de l'architecture, avec les trois chiffres qu'elle vise.

## Ce qui a été construit

**1. `format_video` à la racine du state**, enum fermé `short | long`, défaut
`short`. Les trois fichiers qui portent le schéma ont bougé ensemble
(`state_template.json` en source de vérité, `schemas/state_schema.json`,
`new_short.py`). Le champ n'est **pas** dans `required` : les trois vidéos
existantes n'en ont pas et restent valides, et `format_de()` les lit comme
des Shorts.

`--format` (format narratif) et `--format-video` (court/long) coexistent
sans se recouvrir, et un test le verrouille : la collision de nom relevée au
diagnostic était le vrai risque, puisque les deux champs auraient fini au
même endroit.

**2. `outils/formats_video.py`**, source unique de ce qui change entre les
deux formats. Ce n'était pas prévu par le briefing : en le construisant, on
a trouvé `MOTS_PAR_SECONDE = 2.8` recopié à l'identique dans `metriques.py`
(A5) et `generer_storyboard.py` (A6) — deux copies d'un débit mesuré une
fois, qu'il faudra recalibrer. Ajouter des constantes de format par script
aurait doublé la dette au lieu de l'éteindre. Le module est déployé sous
`<skill>/outils/` chez les quatre skills qui en dépendent, par le mécanisme
d'outils partagés qui existait déjà (§9.2).

**3. Budget par format** (A5). 300 mots par idée en long contre 45, 8 idées
par défaut contre 3. Aucune de ces valeurs n'a été mesurée, et c'est le
point important : `evaluer_budget()` rend désormais un champ `calibrage`
(`mesure_n1` / `non_mesure`) avec sa note en clair. Sans lui, A5 aurait
renvoyé à A4 un script long « dépassé de 1700 % » — un verdict que personne
ne peut utiliser, rendu au nom d'un seuil que personne n'a établi.

**4. Découpage par segment** (A6). `grouper_phrases()` groupe vers une durée
cible de 12 s, avec un plafond dur de 120 scènes : au-delà, on élargit les
scènes, **on ne tronque jamais** — un storyboard qui ne couvre pas tout
l'audio, c'est un écran figé pendant la fin de la voix off. Vérifié sur 280
phrases : 92 scènes, toutes les phrases couvertes une fois et une seule, dans
l'ordre. Le `.md` liste les phrases numérotées de chaque scène, parce que
c'est par un numéro de phrase qu'A6 désigne un accent ou un insert.

Le briefing craignait pour le recalage : il n'a jamais été menacé,
`_fins_par_scene()` accepte les scènes multi-phrases depuis la file #11.

**5. Cadre paysage** (A7). `appliquer_format()` écrit `charte.format` depuis
`charte.formats[<format>]`, sinon — en long — par **rotation** de la charte
existante. Le choix de la rotation plutôt que d'une valeur par défaut n'est
pas cosmétique : une charte réglée en 1440×2560 à 60 fps garde sa résolution
et son fps, là où imposer 1920×1080 les aurait jetés en silence.

**6. L'insert de footage.** Conçu comme le diagnostic le recommandait —
surcouche hors registre, de la famille de `Subtitles` — et pas comme le
briefing le proposait. Type `Insert` sur `Scene`, résolution dans
`construire_props.py` sur le modèle de `_pulsation_s()`, rendu par
`InsertFootage` sous un `<Sequence>` posé par `Video.tsx`.

**Vérifié par un rendu réel**, pas par le typecheck : un asset d'une couleur
pleine, trois images fixes rendues à 1,0 s / 3,0 s / 5,3 s, et les pixels
comptés. L'insert est absent avant et après sa fenêtre, occupe entre 5 % et
75 % du cadre pendant — la borne haute est ce qui vérifie qu'il n'est pas
redevenu un plan. Le décodeur PNG du test est écrit à la main : Pillow n'est
pas une dépendance du dépôt, et vérifier un rendu sur autre chose que les
pixels revient à vérifier le typecheck une deuxième fois.

**7. Rendu par tranches reprenables** (A7). C'est le point C du diagnostic,
que le briefing ne voyait pas. Trois décisions prises en écrivant :

- **le nombre de frames est demandé à `remotion compositions`**, jamais
  recalculé en Python. `calculateMetadata` peut dériver la durée de l'audio
  autant que des scènes ; deux formules pour une même durée auraient
  divergé ;
- **les tranches sont rendues muettes**, et la voix off remontée d'un seul
  bloc au recollage. Mesuré ici : recoller deux tranches sonores donne
  4,096 s là où le rendu monolithique donne 4,054 s — l'AAC ne se coupe pas à
  la frame, et chaque jointure ajoute une vingtaine de millisecondes. Sur
  huit tranches, la voix finirait ~150 ms derrière l'image, avec un décalage
  qui grandit jusqu'à la fin : exactement le défaut que le recalage sur
  `04_phrases.json` existe pour éliminer ;
- **écriture en deux temps** (`.tmp.mp4` puis `os.replace`), comme le cache
  TTS, pour qu'une tranche interrompue ne soit jamais relue comme terminée.

`npx remotion ffmpeg` sert au recollage : Remotion embarque son ffmpeg, donc
aucune dépendance système n'est ajoutée. (C'est aussi la réponse au « ffprobe
n'est pas installé » noté à la séance précédente.)

**8. Repères horodatés au CP3** (§5.5). Le diagnostic demandait un « résumé
par segment ». Ce qui manque réellement à Franco sur quinze minutes, ce n'est
pas un résumé : c'est **où aller regarder**. Le rapport donne huit points
d'entrée horodatés sur l'audio réel (`04_phrases.json`), avec les scènes non
tranchées signalées **à leur minutage** plutôt que par leur identifiant — un
`s47` ne dit rien dans un MP4 de quinze minutes. Rien de tel sur un Short,
où les repères feraient plus de lignes que la vidéo ne dure de secondes.

## Deux défauts préexistants trouvés en chemin

Aucun des deux n'a de rapport avec le format long ; tous deux étaient sur le
chemin du premier rendu long.

- **`rendre_video.py` plantait au lieu de rendre son erreur.**
  `sortir(6, message=..., code=resultat.returncode)` entre en collision avec
  le paramètre positionnel `code` de `sortir(code, **data)` : `TypeError`, au
  lieu du JSON promis par le skill. Le seul chemin où ça se voyait était
  celui d'un rendu qui échoue — donc jamais dans un test vert.
- **Un `--root` relatif cassait le rendu.** Les sous-processus `remotion`
  tournent avec `cwd=composants/`, où un chemin encore relatif désigne autre
  chose : `--props` échouait sur « neither valid JSON nor a file path », sans
  que rien ne dise que le problème était le chemin. Les deux chemins sont
  maintenant résolus avant tout appel.

## Ce qui n'a pas été fait, et pourquoi

- **Les composants ne sont pas recomposés pour le paysage.** Le verrou du
  cadre est levé, la mise en page ne l'est pas : une vidéo longue les
  montrera cadrés au milieu d'un écran large. Les reprendre un par un sans
  avoir vu une seule vidéo longue à l'écran, ce serait refaire l'erreur que
  ce document nomme depuis le début.
- **Le point 6 (WER par phrase) reste ouvert.** Le cache par phrase, qui le
  conditionne, a été fait à la séance précédente ; le WER par phrase lui-même
  n'a d'intérêt qu'une fois qu'un long run aura réellement échoué quelque
  part, et on saura alors où.
- **Aucun rush réel n'est passé par un insert.** `resoudre_ressources.py`
  existe depuis la séance précédente et sait indexer `assets/`, mais le
  premier vrai clip reste à voir. C'est la réserve qui domine la conception
  de l'insert, et elle n'est pas levée.
