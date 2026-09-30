# Étape 1 — Sujet et angle

**But** : proposer **3 sujets**, chacun avec son angle, pour que Franco en
choisisse un. Tu ne choisis pas à sa place : tu recommandes.

## Ce qu'un bon sujet Zehon doit avoir

1. **Une matière et un objet du quotidien** : le sable devient la vitre,
   le grain devient le pain, le minerai devient le couteau. Si on ne peut
   pas écrire « de ___ à ___ », ce n'est pas un sujet Zehon.
2. **Une histoire longue et riche** : au moins 3 grandes étapes du
   procédé, avec des faits étonnants à raconter. Sans rebondissements, pas
   de vidéo.
3. **Un paradoxe pour le hook** : l'objet est banal aujourd'hui, et
   pourtant… (il a coûté une fortune, il existe avant ce qu'on croit, il a
   fallu 3 000 ans pour le faire, etc.).
4. **Une demande prouvée** : le sujet (ou un proche) a déjà bien marché
   sur YouTube, en français ou en anglais. Le marché anglais sert de banc
   d'essai : un sujet à plus de 500 k vues en anglais et absent en
   français passe devant.

## Comment chercher

- Lis `Memoire/sujets.md` (dans Drive) : les sujets faits, ceux déjà
  proposés, et ce que les concurrents ont traité. **Ne repropose pas un
  sujet fait**, et signale quand un concurrent l'a déjà pris (et sous quel
  angle).
- **Mesure la demande avec l'API** (si `YOUTUBE_API_KEY` est définie),
  depuis le dossier de la skill :
  - `python3 scripts/youtube.py chaine @zelanstudio` : ce que Zelan a
    publié depuis le dernier relevé de `sujets.md` ;
  - `python3 scripts/youtube.py chercher "histoire du verre"` (et la même
    requête en anglais avec `--langue en`) : les vidéos les plus vues et
    leurs vues réelles. Chaque recherche coûte environ 100 unités sur
    10 000 par jour : 2 à 4 par sujet suffisent.
  Les résultats sont bruités (Shorts, contes, recettes) : ne garde que
  les vidéos qui racontent vraiment l'histoire de la matière. Reporte les
  relevés utiles dans `sujets.md`, datés.
- Complète par la **recherche web** : (a) si **Zelan** a déjà traité le
  sujet, et avec quel paradoxe ; (b) qu'il y a assez de faits étonnants
  pour tenir 8 minutes.
- **Sans clé API**, YouTube bloque souvent les requêtes directes (429,
  page anti-robot) : prends les vues sur une page de résultats d'un moteur
  de recherche, dis laquelle, et présente-les comme des **ordres de
  grandeur**. Ne donne jamais un nombre de vues de mémoire.
- Une date ou un fait **cité de mémoire** porte la mention « à vérifier » :
  il sera vérifié à l'étape 2.
- Sans recherche web, pars de `sujets.md` et de tes connaissances, et
  **marque clairement ce qui n'est pas vérifié** (« demande : non
  vérifiée »).

## Ce que tu livres (dans le chat, pas de fichier)

Pour chacun des 3 sujets, 5 lignes au plus :

```
1. Le verre — du sable à la vitre
   Paradoxe : [une phrase]
   Moment fort : [le fait le plus étonnant de l'histoire]
   Demande : [chiffres et source, avec la date du relevé, ou « non vérifiée »]
   Concurrence : [qui l'a traité, sous quel angle]
```

Puis **ta recommandation en 2 phrases** (lequel, et pourquoi), et **une
seule question** : « Lequel on fait ? »

Quand Franco a choisi, crée le dossier `Zehon/Videos/<nn>_<sujet>/` (avec
`images/`, `voix/`, `rendu/`), inscris le sujet dans la section *En cours*
de `sujets.md`, puis enchaîne sur l'étape 2 (recherche).
