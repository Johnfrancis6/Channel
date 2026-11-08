# Revue du pipeline Zehon — 08/11/2026

Revue de lecture et d'essais, **sans rien corriger** (la chaîne est gelée,
D1). Périmètre : `zehon/content-maker/`, `zehon/video-maker/`,
`zehon/notebooks/`, les lanceurs rangés dans Drive, et la cohérence avec
`docs/chaine2/CONTEXTE.md` et les décisions Z1 à Z3.

**Mesuré** : 167 tests passent (33 pour Zehon), `tools/sync_skills.py --check`
ne voit aucun écart, branches lues avec `git ls-remote`, lanceur de montage
Drive téléchargé, deux bugs reproduits (script dans le scratchpad de la
session). **Pas mesuré** : rien n'a tourné dans Colab ; les 03_scenes.md de
Drive n'ont été fouillés que par la recherche plein texte de Drive.

## P1 — à corriger avant de relancer Zehon

### 1. Les lanceurs clonent une vieille branche, sans le bandeau sombre

- Le lanceur Drive `Zehon/montage_zehon.ipynb` (le plus récent, modifié le
  01/10 à 14:30) a `BRANCHE = "claude/zelan-studio-analysis-rws9f6"` ; sa
  dernière sortie affiche `Code du montage : … @ 15b0fe0`. Les lanceurs du
  dépôt (`zehon/notebooks/lanceur_montage.ipynb`, `lanceur_voix.ipynb`) et
  la cellule `reglages` des deux notebooks ont la même valeur par défaut.
- `15b0fe0` n'a pas `FOND_TEXTE` (le bandeau sombre sous le texte animé) :
  c'est justement le défaut du verre. **Relancer le verre (Z3) avec ce
  lanceur redonnerait le même rendu.**
- Trois sources disent trois choses : les lanceurs disent `zelan-…`,
  `CONTEXTE.md` dit `claude/optimistic-bohr-5f78k4`, `CLAUDE.md` dit « Colab
  tourne sur `main` ». Mesuré : le code Zehon de `main` (a08aa8c) et celui
  de `optimistic-bohr` sont identiques.
- **Recommandation** : `BRANCHE = "main"` partout (dépôt, par une PR), et
  Franco change le champ dans les deux lanceurs Drive.

### 2. Le type `photo` et le mouvement `zoom_vers` sont prévus, mais le montage les refuse

- `etape4_scenes.md` (tableau des types, exemple de la scène 31) et
  `verifier.py` acceptent `photo` (`photos/<nom>.jpg`, colonne crédit) et
  `zoom_vers:x,y`.
- `monter.py` ne connaît que `image`, `video`, `titre` : une scène `photo`
  donne « type inconnu » et **le montage s'arrête** ; `zoom_vers` devient
  `zoom_avant` (avertissement), sans viser le détail.
- Latent : la recherche Drive ne trouve ni `photos/` ni `zoom_vers` dans les
  scènes du verre et de l'aluminium (indicatif, pas une lecture complète).
- **Recommandation** : enlever `photo` et `zoom_vers` de la skill et du
  vérificateur (la charte dit « toutes les images viennent de Gemini »),
  plutôt que de les coder dans `monter.py`.

### 3. Un extrait est impossible tant qu'une image manque

- La skill dit : « Un extrait se monte même avant, avec les pièces de ses
  scènes. » `monter.py --scenes 1-10` le permet bien.
- Mais la cellule 3 de `montage_zehon.ipynb` lance `--plan` **sans**
  `--scenes` : il exige toutes les images, et le notebook s'arrête.
- Reproduit : images 1 et 2 seulement → `--plan` code 1 (« Montage
  impossible ») ; `--plan --scenes 1-2` code 0.
- **Recommandation** : passer `--scenes EXTRAIT` au plan quand `EXTRAIT` est
  rempli, avec un test.

## P2 — gênant, à corriger à la reprise

4. **`REFAIRE_LIGNES` ne tient pas d'un lancement à l'autre** (voix). Une
   ligne refaite prend la graine `GRAINE + n + 1000` ; au lancement suivant
   sans ce numéro, son fichier de cache est effacé et la ligne revient à la
   graine d'origine, donc à la prise ratée. Et refaire deux fois la même
   ligne redonne la même prise (une seule graine de rechange). À garder en
   mémoire dans `etat.json` (lignes refaites et leur graine).
5. **`etat.json` reste `en_cours` après certains échecs.** Seule la boucle de
   synthèse écrit `echec`. Un `pip install` raté (la cellule 2 affiche ✗ et
   continue), un chargement de modèle ou Whisper qui plante laissent
   `en_cours` : la skill conclut « Colab coupé, relance » au lieu de donner
   l'erreur.
6. **Insérer une ligne dans `02_script_voix.txt` refait toute la suite.** Le
   cache est nommé et ensemencé par le numéro de ligne : une ligne ajoutée au
   début relance la synthèse de toutes les suivantes (du temps de T4).
7. **Quatre `montage_zehon.ipynb` dans le même dossier Drive** (créés le
   30/09 à 20:37 et 23:27, le 01/10 à 04:21 et 14:20). La skill elle-même dit
   que deux fichiers du même nom sont une erreur. Le bon lanceur est le plus
   récent (`1gyVRY4H…`) ; les trois autres sont à mettre à la corbeille
   (par Franco, ou par moi s'il le demande).
8. **Un extrait écrase le verdict de la vidéo entière** : `verdict.json` et
   `apercu/` ont le même nom pour les deux. Whose Dime nomme déjà le verdict
   d'après sa sortie (`verdict_<sortie>.json`).
9. **Paquets de la voix non épinglés** (`qwen-tts`, `faster-whisper`,
   `librosa`…). Une version de PyAV a déjà cassé la lecture le 30/09.

## P3 — mineur

10. Les deux skills donnent **Haiku 4.5** pour la session 5 : génération
    dépassée (Haiku 5.5).
11. `CONTEXTE.md` : en-tête daté du 01/10 alors que le gel date du 07/11 ;
    Z1 et Z2 dites « en attente » alors que `DECISIONS.md` les écrit
    tranchées (« couper », « garder »).
12. Noms des clips : le vérificateur exige `clips/scene_NNN.mp4`, la skill et
    l'avertissement de `monter.py` parlent de `clips/anim_NNN.mp4`. Les deux
    marchent (le montage cherche les deux), mais c'est confus.
13. Nombres en lettres : `80 000` → « quatre-vingts mille », `200 000` →
    « deux cents mille », `10⁹` → « mille millions », `8,1` → « huit un ».
    Effet faible (le script et Whisper passent par la même fonction dans
    `monter.py` ; un peu de ressemblance perdue dans le contrôle de la voix).
14. La musique baisse sous la voix avec `np.convolve` direct : environ 1 min
    de calcul pour 8 min de son (mesuré ici : 3,6 s pour 30 s). Une moyenne
    glissante par somme cumulée prend quelques millisecondes.
15. Le contrôle avant publication ne mesure pas le volume (LUFS) : « −14
    LUFS » est la consigne de `loudnorm`, pas une mesure. Le seuil de
    silence (volume moyen > −60 dB) laisse passer de longs trous.
16. Le vérificateur ne connaît pas le mouvement `fixe`, que `monter.py` sait
    rendre.
17. Une scène `video` sans clip n'est pas signalée au-delà de 10 s (seules
    les scènes `image` le sont).
18. Dans Colab, le plan s'affiche deux fois (cellule 3, puis au début du
    rendu). Cosmétique.

## Ce que les tests ne couvrent pas

Le type `photo` côté montage, la branche des lanceurs, le plan du notebook
avec `EXTRAIT`, l'état `echec` hors de la synthèse, la persistance de
`REFAIRE_LIGNES`. Chaque correction P1 et P2 devrait venir avec son test.

## Hors périmètre (noté, pas traité)

`docs/whosedime/STATE.md` a deux blocs « Last update / Where we are » à la
suite (un reste de fusion).

## Autocritique

- `process` (point 2) : l'absence de scènes `photo` dans le verre et
  l'aluminium vient de la recherche plein texte de Drive, pas d'une lecture
  des fichiers.
- `nuance` (point 14) : 1 min pour 8 min de son est extrapolé d'un essai de
  30 s sur 4 cœurs ; Colab peut être plus lent.
- `process` : le lanceur voix de Drive (367 Ko, sorties comprises) n'a pas
  été téléchargé ; sa branche est supposée identique à celle du lanceur de
  montage.
