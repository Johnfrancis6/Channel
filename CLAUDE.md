# Architecture de la chaîne YouTube

Référence unique : [docs/architecture_chaine_v1.2.md](<docs/architecture_chaine_v1.2.md architecture_chaine_v1.2.md>)

*Le nom de fichier est bien dupliqué avec une espace au milieu — c'est
voulu, ne pas le « corriger ».*

Lire ce document en priorité avant chaque session.

Revue de fond la plus récente, qui explique le **pourquoi** des décisions
en place : [docs/revue_architecture_2026-09-11.md](docs/revue_architecture_2026-09-11.md).

Diagnostic du pipeline **étape par étape**, en cours — décisions transverses,
file d'attente, ce qui reste à examiner :
[docs/diagnostic_pipeline.md](docs/diagnostic_pipeline.md).

## Règles du dépôt

- **Ne jamais éditer `.claude/skills/`** : c'est un miroir généré. Modifier
  `agents/short-*/` ou `skills/*/`, puis relancer
  `python3 agents/_synchroniser_vers_claude_skills.py`
  (`--verifier` signale la dérive sans rien écrire).
- Tests : `python3 -m unittest discover -s tests`.
- Composants Remotion : `cd composants && npm run typecheck`.
- `git fetch` avant chaque push — les pushs concurrents depuis d'autres
  sessions sont fréquents. Résoudre en gardant les deux côtés.
