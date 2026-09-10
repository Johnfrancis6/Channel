# Agents (§9.2)

Prompts versionnes des agents du pipeline (A2 a A7, H1), un dossier par
agent. Chaque dossier suit le meme format que `skills/` : `SKILL.md` (le
prompt) + `scripts/` (les scripts qu'il utilise), pour rester installable
de la meme facon.

`_etape_template.py` est la source commune de `scripts/etape.py`, duplique
dans chaque agent (les skills sont installes independamment, voir §14) :
il applique le contrat `state.json` du §4.2 (demarrage/succes/echec) sans
jamais toucher aux checkpoints ni a l'etape d'un autre agent. Si ce
contrat evolue, modifie ce fichier puis recopie-le dans chaque
`scripts/etape.py`.

Les agents factices utilises pour tester le squelette de l'Orchestrateur
(§13, etape 1) sont dans `orchestrateur/agents_factices/`, pas ici : ce
sont des simulations Python pour les tests, pas des prompts pour Claude.
