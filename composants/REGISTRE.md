# Registre des composants d'animation

Source de verite du code : `src/components/registry.ts`. Ce fichier est la
vue humaine (§8) : le Monteur (A7) l'ajoute a jour a chaque composant cree
ou modifie.

Regle du Monteur : reutiliser un composant existant, sinon en etendre un,
sinon en creer un nouveau (statut `nouveau`, revu de fait au CP3).

| Composant | Parametres | Version | Statut | Videos |
|---|---|---|---|---|
| `TitleCard` | `texte` (string), `sousTitre` (string, optionnel) | 1 | valide | — |
| `StickmanTalk` | `pose` (`"intro"` \| `"lean_in"` \| `"outro"`), `label` (string, optionnel) | 1 | nouveau | 2026-09-11_v01 |
| `ConceptCutaway` | `scene` (`"llm_single_turn"` \| `"workflow_tools"` \| `"workflow_fixed_path"` \| `"agent_loop"` \| `"github_demo"`), `label` (string, optionnel) | 1 | nouveau | 2026-09-11_v01 |
| `Subtitles`* | `mots` (MotHorodate[]) | 1 | valide | — |

\* `Subtitles` n'est pas choisi par scene : il est surimprime automatiquement
sur toute la video par `src/Video.tsx`, cale sur `04_timestamps.json`.
