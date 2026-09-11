# Jeu de base Lottie

Animations **récurrentes** de la chaîne, réutilisées d'une vidéo à l'autre
(§8). Un bon fichier ici est amorti sur toute la série — c'est pourquoi on
en veut peu, et bons.

Pour les animations propres à **une seule** vidéo, le fichier va dans
`videos/{video_id}/assets/`, pas ici.

## Ce que Lottie fait, et ne fait pas

Un fichier Lottie est **pré-rendu** : on le joue, on le boucle, on en lit un
segment, on recolore des couches. On ne change pas ce qu'il raconte.

- **Ici** : personnage, transitions, icônes, effets — ce qui est fixe et expressif.
- **Pas ici** : schémas, texte, chiffres, sous-titres — tout ce dont le
  contenu change d'une vidéo à l'autre reste en Remotion, avec les tokens de
  charte. Sinon chaque nouvelle vidéo exigerait un fichier fait à la main
  avant de pouvoir tourner.

## Les quatre fichiers attendus

Dérivés de l'usage réel du storyboard de `2026-09-11_v01` — le stickman y
apparaît en intro, en transition et en clôture.

| Fichier | Ce qu'il montre | Boucle ? | Utilisé pour |
|---|---|---|---|
| `stickman_parle.json` | le personnage s'adresse à la caméra | oui | intro, outro, tout plan où il raconte |
| `stickman_pointe.json` | il désigne un élément hors de lui | oui | transition vers un cutaway (`pose: lean_in`) |
| `stickman_reagit.json` | surprise, approbation, haussement d'épaules | non | ponctuer un accent, une chute |
| `transition.json` | balayage plein cadre entre deux scènes | non | passage de scène |

Les trois premiers doivent se ressembler : **même personnage, même trait,
même palette**. C'est leur cohérence qui fait l'identité de la chaîne, pas
leur nombre.

## Contraintes techniques

- **Vectoriel uniquement.** Pas d'image bitmap embarquée : ça alourdit le
  fichier et casse la mise à l'échelle en 1080×1920.
- **Peu de couches de couleur**, et des couleurs à plat. C'est ce qui permet
  de recolorer aux tokens de `charte.json` plutôt que de subir la palette du
  fichier d'origine.
- **Boucle propre** pour les fichiers marqués « oui » : la dernière image
  doit raccorder à la première, sans à-coup.
- **Fond transparent.** Le fond vient de la charte, jamais du Lottie.
- **Cadrage vertical ou carré**, centré : le personnage doit tenir dans un
  9:16 sans être rogné.

## Licence — à vérifier avant d'intégrer

Une chaîne monétisable est un **usage commercial**. Les catalogues publics
mélangent des fichiers libres et des fichiers dont la licence exclut le
commercial ou impose une attribution.

Note la licence de chaque fichier dans le tableau ci-dessus au moment de
l'ajouter. Un fichier sans licence identifiée ne rentre pas.

## Intégration

`@remotion/lottie` n'est pas encore installé — il le sera au premier fichier
réel (`npm i @remotion/lottie lottie-web` dans `composants/`). Le `.json` est
ensuite copié dans `composants/public/lottie/` : le serveur de rendu sert les
assets locaux depuis `public/`, sous le préfixe `/public/`, comme pour
l'audio.

Tant qu'un fichier manque, le Monteur ne bloque pas : il rend la scène en
Remotion et le signale à la clôture.
