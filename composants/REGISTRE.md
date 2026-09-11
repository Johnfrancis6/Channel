# Registre des composants d'animation

Source de verite du code : `src/components/registry.ts`. Ce fichier est la
vue humaine (§8) : le Monteur (A7) l'ajoute a jour a chaque composant cree
ou modifie.

**Les apercus sont dans [`apercus/README.md`](apercus/README.md)** — une
image par composant et par variante, rendue par la composition reelle.
Regarde-les avant de choisir : c'est le seul moyen de savoir ce qu'une cle
comme `scene="workflow_fixed_path"` met vraiment a l'ecran. Regenerer apres
avoir cree ou modifie un composant :

```bash
python3 outils/generer_apercus.py
```

Regle du Monteur : reutiliser un composant existant, sinon en etendre un,
sinon en creer un nouveau (statut `nouveau`, revu de fait au CP3).

Tout composant recoit deux props en plus des siennes : `charte`
(`CharteTokens`, dont le bloc `animation`) et `da` (`DirectionArtistique`,
optionnelle) — la direction artistique decidee par A6 pour cette scene
(§8). Un composant qui ignore `da` rend toujours, mais il rend toujours
pareil : c'est le style qui redevient improvise.

| Composant | Parametres | Version | Statut | Videos |
|---|---|---|---|---|
| `TitleCard` | `texte` (string), `sousTitre` (string, optionnel) | 1 | valide | — |
| `StickmanTalk` | `pose` (`"intro"` \| `"lean_in"` \| `"outro"`), `label` (string, optionnel) | 1 | nouveau | 2026-09-11_v01 |
| `ConceptCutaway` | `scene` (`"llm_single_turn"` \| `"workflow_tools"` \| `"workflow_fixed_path"` \| `"agent_loop"` \| `"github_demo"`), `label` (string, optionnel) | 1 | nouveau | 2026-09-11_v01 |
| `Subtitles`* | `mots` (MotHorodate[]) | 1 | valide | — |

Colonne `DA` : `oui` si le composant applique `da`, `partiel` s'il n'en
suit qu'une partie, `non` s'il l'ignore encore.

| Composant | DA |
|---|---|
| `TitleCard` | oui |
| `StickmanTalk` | oui |
| `ConceptCutaway` | oui |

Tous passent par `src/animation.ts`, qui implemente les huit regles du §8
une fois pour toutes. Un composant qui refait ses `interpolate()` a la main
retombe dans le geste unique d'origine : opacite plus translation sur
0,3 s, puis image fixe.

## Ce que le premier catalogue avait revele, et ce qui a ete corrige

| Constat (11/09/2026) | Etat |
|---|---|
| `ConceptCutaway` laissait ~3/4 du cadre vides, schemas generiques (« STEP 1 / STEP 2 ») | corrige — maillons pleine largeur, rail qui materialise le chemin fixe, boucle circulaire pour l'agent |
| `StickmanTalk` : `intro` et `outro` rendaient la **meme image** (meme md5) | corrige — trois poses distinctes (`wave`, `point`, `open`) |
| Aucun composant ne remplissait le 1080x1920 | corrige — le personnage occupe ~40 % de la hauteur, halo de profondeur |
| Un seul geste d'animation, 0,3 s puis image fixe | corrige — `spring()`, entrees en cascade, mouvement continu sur toute la scene |
| Le trait du corps traversait la tete du stickman | corrige — le cou part du bas reel du cercle |
| Le bras du salut disparaissait dans le crane | corrige — epaule abaissee, angles revus |
| Onze coupes franches entre scenes | corrige — fondu enchaine de 0,25 s dans `Video.tsx` |

Aucun de ces defauts n'etait detectable par un test : il fallait regarder.
C'est la raison d'etre du catalogue.

\* `Subtitles` n'est pas choisi par scene : il est surimprime automatiquement
sur toute la video par `src/Video.tsx`, cale sur `04_timestamps.json`.
