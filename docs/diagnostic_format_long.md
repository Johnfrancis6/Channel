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
