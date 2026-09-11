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
| `TitleCard` | non — a reprendre |
| `StickmanTalk` | partiel — entree en dur (`entree_par_le_bas` + `interpolate`) |
| `ConceptCutaway` | non — a reprendre |

## A reprendre, vu sur les apercus

Constats du premier passage du catalogue (11/09/2026) :

- **`ConceptCutaway`** : environ les trois quarts du cadre sont vides, et les
  schemas sont generiques — deux rectangles « STEP 1 / STEP 2 » qui
  n'illustrent pas le concept annonce. Le stickman de fond est minuscule, et
  les sous-titres (`paddingBottom: 220`) le recouvrent. Ce composant a tenu
  14,4 s a l'ecran dans `2026-09-11_v01`.
- **`StickmanTalk`** : les poses `intro` et `outro` rendent une image
  **strictement identique** (meme empreinte). L'API en annonce trois, il n'y
  en a que deux. A6 croit choisir la ou il n'a pas le choix.
- **Occupation du cadre** : aucun composant ne remplit le 1080x1920. Le
  personnage fait environ un cinquieme de la hauteur.

Ces trois defauts existaient depuis le debut. Aucun test ne pouvait les
attraper : il fallait regarder.

\* `Subtitles` n'est pas choisi par scene : il est surimprime automatiquement
sur toute la video par `src/Video.tsx`, cale sur `04_timestamps.json`.
