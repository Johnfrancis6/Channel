# Agents (§9.2)

Prompts versionnes des agents du pipeline (A2 a A7, H1), un dossier par
agent. Chaque dossier suit le meme format que `skills/` : `SKILL.md` (le
prompt) + `scripts/` (les scripts qu'il utilise), pour rester installable
de la meme facon.

Prefixe `short-` : tous les skills personnels de cette chaine (agents du
pipeline + `new-short`/`short-state`) partagent ce prefixe pour rester
distincts des skills generiques du marketplace (`design`, `docx`, etc.).

| Dossier | Skill (`name:`) | Agent |
|---|---|---|
| `short-chercheur/` | `short-chercheur` | A2 |
| `short-redacteur/` | `short-redacteur` | A4 |
| `short-filtre-tts/` | `short-filtre-tts` | A5 |
| `short-designer/` | `short-designer` | A6 (storyboard) |
| `short-monteur/` | `short-monteur` | A7 |
| `short-analyse-chaines/` | `short-analyse-chaines` | A3 (hebdo) |
| `short-amelioration/` | `short-amelioration` | H1 (hebdo) |

## Installation locale (`.claude/skills/`)

Il y a deux sources de verite versionnees (§9.2), et une seule cible :

| Source | Contenu | Cible |
|---|---|---|
| `agents/short-*/` | les 7 agents du pipeline | `.claude/skills/<nom>/` |
| `skills/*/` | `new-short`, `short-state` | `.claude/skills/<nom>/` |

`.claude/skills/` est **entierement genere**. Ne jamais l'editer
directement : modifie la source, puis relance

```bash
python3 agents/_synchroniser_vers_claude_skills.py
```

Les fichiers texte sont normalises en LF a la copie (les sources sont en
CRLF), sinon chaque synchronisation reecrirait les fichiers deployes en
entier et polluerait les diffs git.

Pour verifier sans rien ecrire — fichier manquant, en trop, contenu
different, dossier orphelin :

```bash
python3 agents/_synchroniser_vers_claude_skills.py --verifier
```

`tests/test_sync_skills.py` lance cette verification : la suite echoue si
`.claude/skills/` a derive. C'est deja arrive en silence — deux scripts
ajoutes dans `agents/` n'avaient jamais ete deployes, et les skills
reellement charges par Claude Code tournaient sans eux.

`_etape_template.py` est la source commune de `scripts/etape.py`, duplique
dans chaque agent (les skills sont installes independamment, voir §14) :
il applique le contrat `state.json` du §4.2 (demarrage/succes/echec) sans
jamais toucher aux checkpoints ni a l'etape d'un autre agent. Si ce
contrat evolue, modifie ce fichier puis recopie-le dans chaque
`scripts/etape.py`.

Les agents factices utilises pour tester le squelette de l'Orchestrateur
(§13, etape 1) sont dans `orchestrateur/agents_factices/`, pas ici : ce
sont des simulations Python pour les tests, pas des prompts pour Claude.
