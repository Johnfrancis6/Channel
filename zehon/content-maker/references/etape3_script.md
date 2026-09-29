# Étape 3 — Plan, puis script

Deux temps, avec une pause entre les deux : **3a, le plan** (`02_plan.md`),
validé par Franco ; puis **3b, le script** (`02_script.md` et
`02_script_voix.txt`). Pourquoi : une structure fausse se corrige en 10
lignes au plan, pas en réécrivant 1 480 mots.

## Le modèle mesuré

Mesuré sur *Comment nos ancêtres ont-ils découvert le fer ?* (Zelan,
435 k vues, transcription segmentée le 29/09/2026) :

- **3,09 mots/s** ; 1 547 mots pour 500 s ; phrase médiane de **12 mots**
  (la moitié des phrases entre 8 et 17) ;
- **hook de 30 s** en 8 phrases : un objet que tu as sous la main, puis un
  paradoxe ; **la question de la vidéo tombe à la 9e phrase** ;
- **10 temps** de 55 à 255 mots (123 en moyenne), en fil chronologique ;
  **chaque temps finit sur un obstacle, que le suivant lève** ; mot
  charnière : **« Sauf que »** (avec « Mais », « Alors ») ;
- **tutoiement**, et **5 à 6 retours au présent** (« un couteau à 3 € au
  supermarché », « tu as 10 objets en fer dans un tiroir ») ;
- **pas d'appel à s'abonner** ; la fin est une **question ouverte**.

Ce modèle vient d'**une seule vidéo** : c'est un point de départ, que
`Memoire/lecons.md` corrigera au fil des vidéos. Si `lecons.md` dit
autre chose (par exemple un débit mesuré sur la voix de Franco), c'est
`lecons.md` qui gagne.

## La structure Zehon

| Bloc | Contenu | Mots |
|---|---|---|
| **Hook** | L'objet du quotidien, puis le paradoxe. La question de la vidéo **au plus tard à la 9e phrase** | 85-95 |
| **Q1 à Q4** | Les 3 à 4 questions d'enquête du dossier, **en 8 à 10 temps au total** (2 à 3 temps par question). Chaque question se referme sur **sa pièce à conviction**, décrite à l'oral pendant qu'elle est montrée | 120-150 par temps |
| **Fin** | Retour à l'objet du début, et une **question ouverte** tournée vers le présent. Pas d'appel à s'abonner | 50-60 |

**Total : environ 1 480 mots** (environ 8 min).

## 3a. Le plan : `02_plan.md`

Un tableau, une ligne par bloc :

```markdown
# Plan — <sujet>

| Bloc | Temps | Contenu (renvois au dossier : 1.2, 3.3…) | Obstacle de fin (« Sauf que ») | Pièce / retour au présent | Mots |
|---|---|---|---|---|---|
| Hook | — | … | — | Présent : … | 90 |
| Q1 … | T1 | … | … | … | 130 |
…
**Total visé** : … mots
```

Vérifie avant de livrer : 8 à 10 temps, chaque temps a un obstacle (sauf
le dernier), chaque question a sa pièce, 5 à 6 retours au présent en tout,
total entre 1 400 et 1 560 mots.

**Pause 3** : 3 lignes de résumé, puis « Tu valides le plan ? ».

## 3b. Le script : `02_script.md`

Écris le texte **tel qu'il sera dit**, bloc par bloc, avec les titres de
blocs en commentaire (`## Hook`, `## Q1 — T1`…). Règles :

- **Le tutoiement**, des phrases courtes (médiane autour de 12 mots),
  aucune phrase au-delà de 25 mots.
- **Calme** : pas de superlatifs criés ni de « incroyable ». Le suspense
  vient des obstacles.
- **Les statuts passent à l'oral** : établi → énoncé direct ou « on
  sait que » ; probable → « on pense que », « tout indique que » ;
  hypothèse → « personne ne sait vraiment, mais… ». **Ne présente jamais
  un probable comme un établi.**
- **Au moins un moment « comment on le sait » par question** : dire la
  méthode (« les cernes du bois donnent l'année exacte où l'arbre a été
  coupé : 1344 avant notre ère »), ou démonter un mythe.
- **Les pièces à conviction sont annoncées à l'oral** (« Regarde cet
  escalier. ») : `video-maker` les montrera à ce moment-là.
- **Les chiffres restent en chiffres** dans cette version (elle sert à la
  relecture et au texte animé).
- **Rien d'inventé** : chaque fait du script vient du dossier. Si tu as
  besoin d'un fait absent du dossier, signale-le au lieu de l'écrire.
- **On reprend des sujets, jamais des scripts** : ne paraphrase pas une
  vidéo concurrente.

**Un hook dans le bon registre** (exemple Zehon, le sel) :

> Regarde la salière sur ta table. C'est sans doute ce qu'il y a de moins
> cher dans ta cuisine. Chaque hiver, des camions entiers en jettent sur
> les routes. Sauf qu'il y a deux cent cinquante ans, en France, porter un
> sac de sel sans payer l'impôt pouvait t'envoyer aux galères…
> (…)
> Alors comment une eau salée est devenue cette poudre blanche ? Et
> comment un trésor est devenu presque gratuit ?

## La version voix : `02_script_voix.txt`

La même histoire, préparée pour la synthèse vocale (clone de la voix de
Franco). Ce fichier remplace l'ancien « filtre TTS » :

- **une phrase par ligne**, 8 à 18 mots de préférence, **jamais plus de
  22** : coupe les phrases longues à une articulation naturelle ;
- **les nombres en lettres** : « 1344 av. J.-C. » → « mille trois cent
  quarante-quatre avant notre ère » ; « 8,1 g » → « huit grammes » ;
  « XVIIIe siècle » → « dix-huitième siècle » ;
- **aucun symbole, sigle, abréviation ni parenthèse** : « % » → « pour
  cent », « km » → « kilomètres », « CNRS » → une périphrase ou les
  lettres épelées (« cé-èn-èr-èss ») ;
- **les noms difficiles réécrits comme ils se prononcent**, à partir de
  `Memoire/lexique.md` (« Hallstatt » → « Halchtatt ») ; ajoute les
  nouveaux noms au lexique (voir `memoire.md`) ;
- **pas de titres de blocs ni de commentaires** : uniquement ce qui sera
  prononcé.

## Vérifier avant de livrer

Lance `python3 scripts/verifier.py 02_script.md` puis
`python3 scripts/verifier.py 02_script_voix.txt`, et corrige ce qui est
signalé. Sans exécution de code, vérifie à la main : le total de mots, la
question du hook avant la 9e phrase, au moins un « Sauf que », aucun appel
à s'abonner, et pour la version voix aucun chiffre ni phrase de plus de 22
mots.

**Pause 4** : résume en 3 lignes (le total de mots, la durée estimée à
environ 3 mots/s, les 2 passages dont tu es le moins sûr), puis « Tu
valides le script ? ». Après sa validation, enchaîne sur l'étape 4 sans
t'arrêter.
