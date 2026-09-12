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
| `ConceptCutaway` | `scene` (`"llm_single_turn"` \| `"workflow_tools"` \| `"workflow_fixed_path"` \| `"agent_loop"` \| `"github_demo"` \| `"context7_demo"` \| `"playwright_demo"` \| `"firecrawl_demo"` \| `"higgsfield_demo"` \| `"github_mcp_demo"`), `label` (string, optionnel), `compteur` (string, optionnel, ex. `"1/5"`) | 2 | nouveau | 2026-09-11_v01, 2026-09-12_v01 |
| `PlanCapture` | `capture` (cle de ressource), `logo` (cle, optionnel), `label` (string, optionnel), `cadrage` (`"haut"` \| `"centre"` \| `"bas"`), `hauteur` (px, defaut 980), `compteur` (string, optionnel) | 1 | nouveau | — |
| `PlanBroll` | `broll` (cle de ressource : clip **ou** photo), `accroche` (string, optionnel), `compteur` (string, optionnel) | 1 | nouveau | — |
| `PlanLogos` | `logos` (`{cle, libelle?}[]`), `label` (string, optionnel), `relier` (bool, defaut vrai), `compteur` (string, optionnel) | 1 | nouveau | — |
| `Subtitles`* | `mots` (MotHorodate[]) | 1 | valide | — |

Colonne `DA` : `oui` si le composant applique `da`, `partiel` s'il n'en
suit qu'une partie, `non` s'il l'ignore encore.

| Composant | DA |
|---|---|
| `TitleCard` | oui |
| `StickmanTalk` | oui |
| `ConceptCutaway` | oui |
| `PlanCapture` | oui |
| `PlanBroll` | oui |
| `PlanLogos` | oui |

### Les composants « contenants » (E5b, 12/09/2026)

`PlanCapture`, `PlanBroll` et `PlanLogos` ne dessinent rien. Ils mettent en
scene un **asset** resolu en amont par l'etape E5b et passe dans
`props.ressources` — une table `cle -> {type, src, ...}` transmise a tous les
composants comme `charte`. Un composant recoit une **cle** dans ses params
et lit le fichier dans cette table.

**Pourquoi ils existent.** Jusqu'au 12/09/2026, le seul asset du systeme
etait `04_voixoff.wav`. Aucun composant n'utilisait `<Img>` ni
`<OffthreadVideo>` : tout ce qui s'affichait devait d'abord etre dessine a la
main en SVG. Creer un visuel neuf coutait donc un fichier `.tsx`, un
typecheck, une entree au catalogue et une relecture au CP3 — alors que le
reutiliser ne coutait rien. **Le barème disait « repete ».** C'est ainsi que
cinq serveurs MCP ont rendu cinq fois le meme schema a trois boites avec
d'autres mots.

Avec ces trois composants, la variete vient de la **donnee** : cinq captures
de cinq pages ne peuvent pas se ressembler, et ca ne coute pas une ligne de
code de plus que la premiere.

| Regle | Consequence |
|---|---|
| Une ressource absente affiche « Ressource manquante : <cle> » en clair | un trou se voit au catalogue et au CP3, au lieu d'un cadre noir |
| `PlanCapture` met la capture a la **largeur** du cadre | un `objectFit: cover` rognait 30 % de la largeur — navigation et panneau lateral disparaissaient |
| `PlanBroll` accepte un clip **ou une photo** | les banques libres servent les deux, et une photo qui se rapproche est un plan de liaison valable |
| `PlanBroll` coupe toujours le son du clip | la seule piste audio de la video est la voix off |
| `PlanLogos` calcule la taille des pastilles selon leur nombre | une taille fixe laissait plus de la moitie du 1080x1920 vide |

Les assets d'exemple du catalogue vivent dans `composants/apercus_assets/`
(versionne), recopies dans `public/apercus/` au moment du rendu — `public/`
est ignore par git et peut etre vide sur un depot fraichement clone.

### `ConceptCutaway` v2 — famille « serveur MCP » (2026-09-12_v01)

Cinq valeurs de `scene` de plus, sur la grammaire deja validee de
`github_demo` : trois boites verticales reliees par des fleches, la
troisieme accentuee parce qu'elle porte le benefice.

| `scene` | Boite 1 | Boite 2 | Boite 3 (accentuee) |
|---|---|---|---|
| `context7_demo` | CLAUDE | CONTEXT7 MCP | REAL DOCS |
| `playwright_demo` | CLAUDE | PLAYWRIGHT MCP | REAL BROWSER |
| `firecrawl_demo` | CLAUDE | FIRECRAWL MCP | CLEAN TEXT |
| `higgsfield_demo` | CLAUDE | HIGGSFIELD MCP | IMAGE OR VIDEO |
| `github_mcp_demo` | CLAUDE | GITHUB MCP | PULL REQUEST |

`github_mcp_demo` ne remplace pas `github_demo` : la boite centrale de ce
dernier dit « VS CODE (MCP) », ce qui ne convient qu'a un script qui parle
de VS Code.

Deux ajouts transverses vont avec :

- **`compteur`** (string, optionnel) : badge en coin haut droit pour les
  formats listicle (`"1/5"`). Place hors de la zone des sous-titres
  (220 px du bas, cf. `Subtitles`) et hors des boites centrales.
- **Accent ponctuel sur la boite 3** : une pulsation d'echelle — pas un
  wobble, que la charte reserve a `trace_main` — declenchee au timestamp
  **reel** de la phrase que `da.accent` designe. A6 ecrit « boite 3 pulse
  au debut de la phrase 7 » ; `construire_props.py` resout cet index via
  `04_phrases.json` en `scene.pulsation_s`, et `Video.tsx` le convertit en
  frame en rattrapant le chevauchement inter-scenes. Le milieu
  chronometrique d'une scene qui couvre quatre phrases ne tombe sur aucun
  mot ; l'accent doit tomber sur celui qui porte le benefice.

Pendant la pulsation, le mouvement continu du schema s'efface
(`styleContinu(..., 1 - pulse)`) : un seul mouvement dominant par scene,
premiere regle de `charte.json > animation.regles`.

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
