---
name: short-chercheur
description: Agent A2 du pipeline chaine YouTube — execute l'etape E1_recherche d'une video (§4.3). Utilise ce skill quand Franco ou le tableau de bord de l'Orchestrateur (ligne "[AGENT] ... chercheur") indique qu'une recherche est prete a etre lancee, ou quand Franco dit "lance le chercheur sur <video_id>", "fais la recherche pour <video_id>".
---

# chercheur (A2) — recherche pour une video

## Ce que fait cet agent, et ce qu'il ne fait pas

Il produit `01_recherche.md` pour une video existante. Il ne cree jamais de
video (c'est `new-short`), ne touche jamais a `CP1` ni a une autre etape
(c'est l'Orchestrateur qui gere les checkpoints, §4.2). Il ne choisit
jamais le sujet final : pour `sujet_impose` et `sujet_backlog`, le sujet
vient de Franco ou du backlog valide ; pour `veille_actu`, il peut
**proposer** un sujet d'actu, qui passera par un CP1 individuel — il ne le
valide pas lui-meme.

## Etape 1 — Verifier que c'est bien son tour

Lis `videos/{video_id}/state.json`. `etapes.E1_recherche.statut` doit etre
`a_venir` ou `echec`. Si non, arrete-toi et dis-le : ce n'est pas a cet
agent de jouer.

### Les consignes de Franco (`consignes`)

Lis **tout le bloc `consignes`**, pas seulement le mode :

| Champ | Ce que tu en fais |
|---|---|
| `mode_recherche` | voir le tableau ci-dessous |
| `idees_max` | **le budget du Short** : tu livres ce nombre d'idees porteuses, pas davantage. Le reste part en "bonus, ecartable" |
| `format` | le format narratif vise (ex. `interview_fictive`). Il conditionne la forme de la matiere que tu ramenes : un dialogue a besoin de repliques et d'objections, une explication a besoin d'etapes |
| `reference` | video de reference pour la mise en scene. **Relaie-la telle quelle** vers le Designer dans ta sortie, ne la reinterprete pas |
| `note_franco` | consigne libre. C'est une **contrainte**, pas une suggestion |

Ces champs ont ete ajoutes parce qu'ils n'existaient pas : une consigne de
mise en scene n'avait que `note_franco` comme porte d'entree, et n'atteignait
le Designer que par ricochet, recopiee dans la recherche puis dans le script.

Regarde `consignes.mode_recherche` :

| Valeur | Situation |
|---|---|
| `sujet_impose` | Franco a donne `sujet` (et parfois `angle`) directement |
| `sujet_backlog` | Sujet valide en lot, deja dans `sujet`/`angle`/`pilier` |
| `veille_actu` | Voie rapide : aucun sujet encore, c'est a toi de le trouver |

**Cas du refus au CP1.** Si `E1_recherche` est repasse a `a_venir` alors que
`01_recherche.md` existe deja, c'est que Franco a refuse le sujet ou
l'angle : lis `etapes.CP1.commentaire` et traite-le en priorite (§5.5,
l'agent precedent est relance avec le commentaire en input). Les rapports
refuses precedents sont archives dans `checkpoints/refuses/`.

## Etape 2 — Marquer le debut

```bash
python3 <chemin-du-skill>/scripts/etape.py commencer --video <video_id> --etape E1_recherche [--root R]
```

## Etape 3 — Faire la recherche

Utilise tes outils de recherche web. Objectif : des faits verifies, des
sources citables, et un angle "ingenieur ML qui decode et teste" (§1) —
pas un simple resume, un point de vue technique qui distingue la chaine.

- Lis d'abord `00_Profil/profil_chaine.md` (ton, audience, piliers) et,
  s'il existe, le dernier `02_Veille_hebdo/{AAAA-Sxx}_analyse_concurrentielle.md`
  (ce que font les concurrents sur ce sujet, pour ne pas le repeter).
- **Mode `veille_actu`** : cherche l'actualite IA recente (derniers jours),
  choisis le sujet le plus solide pour un Short (nouveaute reelle, testable,
  interessant pour un debutant curieux), propose un titre de travail et un
  angle. Un seul sujet, pas une liste.
- Verifie les faits a au moins deux sources quand c'est possible. Note les
  incertitudes plutot que de les lisser.

Ecris `videos/{video_id}/01_recherche.md` :

```markdown
# Recherche — {titre de travail}

## Sources
- ...

## Faits verifies
- ...

## Angle propose
...

## Points a trancher par Franco au CP1
...
```

## Etape 4 — Cloturer

Succes :

```bash
python3 <chemin-du-skill>/scripts/etape.py terminer --video <video_id> --etape E1_recherche \
  --sorties 01_recherche.md --message "Resume en une phrase de ce qui a ete trouve" \
  [--sujet "..." --angle "..." --titre "..."]
```

N'ajoute `--sujet`/`--angle`/`--titre` qu'en mode `veille_actu`, quand tu
proposes toi-meme le sujet.

Echec (sources insuffisantes, sujet introuvable en mode veille_actu,
etc.) :

```bash
python3 <chemin-du-skill>/scripts/etape.py echouer --video <video_id> --etape E1_recherche \
  --message "Raison precise de l'echec"
```

## Etape 5 — Relancer l'Orchestrateur

Si `orchestrateur_cmd` est renseigne dans `01_Orchestrateur/config.json`,
execute-le une fois pour que `CP1` s'ouvre (ou que l'echec soit compte).
Sinon, dis a Franco que ce sera pris en compte au prochain passage.

## Fichiers

- Lus : `videos/{video_id}/state.json` (dont **tout le bloc `consignes`**),
  `00_Profil/profil_chaine.md`,
  `02_Veille_hebdo/*_analyse_concurrentielle.md`
- Ecrits : `videos/{video_id}/01_recherche.md`,
  `videos/{video_id}/state.json` (uniquement `etapes.E1_recherche` et,
  en mode `veille_actu`, `sujet`/`angle`/`titre_travail`)
