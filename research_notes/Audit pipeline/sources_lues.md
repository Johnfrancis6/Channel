# Audit du pipeline — sources lues (07/11/2026)

Notes de travail du rapport [`reports/Audit pipeline de production.md`](../../reports/Audit%20pipeline%20de%20production.md).

## Dépôt

Branche lue : `origin/claude/optimistic-bohr-5f78k4` (commit `df57743`, 01/10),
ouverte dans un `git worktree`, sans changer de branche.

| Fichier | Lu |
|---|---|
| `CLAUDE.md`, `docs/chaine2/CONTEXTE.md`, `docs/chaine2/historique.md` | en entier |
| `zehon/content-maker/SKILL.md` et les 7 `references/*.md` | en entier |
| `zehon/content-maker/scripts/verifier.py`, `evals/evals.json` | en entier |
| `zehon/video-maker/SKILL.md` | en entier |
| `zehon/video-maker/scripts/monter.py` | en-tête, constantes, liste des fonctions, écriture du verdict (l. 1–80, 1180–1185) |
| `zehon/notebooks/voix_zehon.ipynb` | toutes les cellules |
| `zehon/notebooks/lanceur.py`, `montage_zehon.ipynb` (passages verdict et aperçu), `synchroniser_skills.py` (en-tête) | partiel |
| `tests/` | liste des tests, exécution |

Branche de travail `claude/admiring-ramanujan-k2uiqe` : `CLAUDE.md`,
`docs/finance/PLAN_ACTION.md` (structure, voix, automatisation, points à
vérifier), `docs/audit/PROTOCOLE_CRITIQUES.md`, `docs/audit/journal_critiques.jsonl`,
`docs/audit/PROMPT_SESSION_2_QUALITE_CONTENU.md` (début).

État des branches (`git ls-remote`, 07/11) :

| Branche | Commit | Ce qu'elle porte |
|---|---|---|
| `main` | `f5ceed8` (30/09) | content-maker ancienne, pas de video-maker |
| `claude/zelan-studio-analysis-rws9f6` | `15b0fe0` (01/10) | la branche des lanceurs Drive (`BRANCHE`), sans le bandeau `53fac3b` |
| `claude/optimistic-bohr-5f78k4` | `df57743` (01/10) | le pipeline le plus récent |
| `claude/admiring-ramanujan-k2uiqe` | `2c7ea33` (07/11) | branche de travail, partie de `main` : content-maker ancienne (28 fichiers d'écart avec bohr, +3 359/−354 lignes) |

## Drive (téléchargement brut, base64 décodé)

| Fichier | Vidéo | Lu |
|---|---|---|
| `Memoire/lecons.md`, `Memoire/sujets.md` (section *En cours*) | — | brut |
| `Zehon/voix_zehon.ipynb` (lanceur) | — | brut : `BRANCHE = "claude/zelan-studio-analysis-rws9f6"` |
| `voix/etat.json` | sel, verre | brut |
| `rendu/verdict.json` | sel, verre | brut |
| `01_recherche.md`, `02_script.md`, `02_script_voix.txt` | verre | brut, en entier |
| `04_publication.md` | verre | brut, titres et description (miniatures lues dans le base64) |
| `02_script.md`, `01_recherche.md` | aluminium | brut ; la recherche contrôlée par recherche plein texte Drive (« maréchal ») |
| `02_script.md` | sel | brut (passages cités) |
| `clips/` | verre | liste des noms (`anim_NNN.mp4`) |
| Listes des dossiers `Zehon/`, `Memoire/`, `Videos/*` | toutes | métadonnées (dates de création) |

**Pas lu** (volume) : `03_scenes.md` des trois vidéos (40 à 49 Ko),
`mots.json` (165 à 170 Ko), `rapport.json`, `02_plan.md`, les publications
du sel et de l'aluminium, `Memoire/lexique.md`, `Zehon/LISEZMOI.md`. Les
images et l'audio ne sont pas lisibles par le connecteur (limite de 10 Mo,
et pas d'écoute possible ici) : **rien de ce rapport ne vient d'une écoute**.

Découverte : un troisième dossier, `Videos/03_aluminium/`, contenu terminé
le 01/10 à 17:27, absent de `CONTEXTE.md`.
