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

## Etape 2 — Reunir les inputs

**Avant** de marquer le debut : une tentative comptee sur une entree
manquante est une tentative perdue, et le compteur sert a declencher une
alerte (§2).

- `00_Profil/profil_chaine.md` — ton, audience, piliers
- **`00_Profil/projets_franco.md`** — ce que Franco construit, teste, et
  surtout ce qu'il peut **montrer a l'ecran**. C'est la que tu prends tes
  exemples. Un exemple qui n'est pas montrable ne sert a rien, et un
  exemple hors de ce fichier sera probablement rejete au CP1 : c'est ce qui
  s'est passe sur `2026-09-11_v01`, ou « upgrade Laravel » a du etre
  remplace a la main. Si tout y est vieux de plus d'un mois, dis-le au CP1
  plutot que de piocher un projet perime.
- le dernier `02_Veille_hebdo/{AAAA-Sxx}_analyse_concurrentielle.md`, s'il
  existe — ce que les concurrents ont deja dit, pour ne pas le repeter. S'il
  manque, signale-le dans « Points a trancher » : tu travailles alors sans
  ton calibrage concurrentiel.

## Etape 3 — Marquer le debut

```bash
python3 <chemin-du-skill>/scripts/etape.py commencer --video <video_id> --etape E1_recherche [--root R]
```

## Etape 4 — Faire la recherche

Objectif : des faits verifies, des sources citables, et un angle "ingenieur
ML qui decode et teste" (§1) — pas un resume, un point de vue technique qui
distingue la chaine.

### Ton metier change selon le mode

| Mode | Ce qu'on attend de toi |
|---|---|
| `sujet_impose` | Franco a deja tranche le sujet **et** l'angle. Tu ne les rediscutes pas : tu les **verifies, tu les etayes, et tu trouves l'exemple qui les incarne**. La section « Angle propose » devient « Angle confirme », ou tu dis ce qui tient et ce qui ne tient pas a l'epreuve des sources |
| `sujet_backlog` | Le sujet a ete valide en lot, l'angle est souvent une esquisse. Tu peux le preciser, pas le remplacer |
| `veille_actu` | Aucun sujet : cherche l'actualite IA des derniers jours, choisis **un seul** sujet (nouveaute reelle, testable, interessante pour un debutant curieux) et propose titre et angle |

### Le budget vaut aussi pour toi

`consignes.idees_max` (3 par defaut) est le budget du Short. Livre donc
**ce nombre de faits porteurs**, et marque explicitement le reste
« bonus, ecartable ». Sans cette hierarchie, A4 prend tout : sur
`2026-09-11_v01`, six faits livres a plat ont donne 258 mots pour un budget
de 135.

### Verification

Deux sources independantes sur le fait central, sans exception. Pour les
faits secondaires, une seule suffit — mais elle part alors en
« Incertitudes assumees », pas en « Faits verifies ». Un blog d'editeur et
un blog personnel qui se citent l'un l'autre ne font pas deux sources.

### Ecris `videos/{video_id}/01_recherche.md`

```markdown
# Recherche — {titre de travail}

## Sources
- ...

## Faits verifies
### Porteurs (les {idees_max} du Short)
- ...
### Bonus — ecartables
- ...

## Matiere a hook
Trois candidats, un par ligne : un fait contre-intuitif, un chiffre, une
erreur repandue. Les trois premieres secondes decident de la retention, et
A4 ne peut pas les inventer a partir de rien.

## Angle confirme (ou propose)
...

## Incertitudes assumees
Ce qui n'est pas recoupe, et ce qui sonne comme un chiffre marketing. Ne
lisse pas : un chiffre invérifiable prononce dans une video devient une
affirmation de la chaine.

## Termes a risque de prononciation
Sigles, noms de modeles, versions que tu introduis (ex. MCP, GPT-5). A5 les
traitera, mais c'est toi qui les fais entrer : les signaler ici leur evite
d'etre decouverts deux etapes plus tard.

## Points a trancher par Franco au CP1
...
```

## Etape 5 — Cloturer

Succes :

```bash
python3 <chemin-du-skill>/scripts/etape.py terminer --video <video_id> --etape E1_recherche \
  --sorties 01_recherche.md --message "Resume en une phrase de ce qui a ete trouve" \
  [--sujet "..." --angle "..." --titre "..."]
```

N'ajoute `--sujet`/`--angle`/`--titre` qu'en mode `veille_actu`, quand tu
proposes toi-meme le sujet.

**Quand echouer, precisement.** Sans critere, cet agent ne peut pas
echouer : il produira toujours un fichier, et le compteur de tentatives
n'a plus de sens. Echoue si :

- le **fait central** ne tient sur aucune source primaire ou n'a qu'une
  seule source ;
- en `veille_actu`, rien de solide n'est sorti ces derniers jours — mieux
  vaut le dire que fabriquer un sujet ;
- `sujet` est vide alors qu'on n'est pas en `veille_actu` : la video a ete
  creee sans sujet, ce n'est pas a toi d'en inventer un (§2).

Une incertitude sur un fait secondaire n'est **pas** un echec : elle va en
« Incertitudes assumees ».

Echec :

```bash
python3 <chemin-du-skill>/scripts/etape.py echouer --video <video_id> --etape E1_recherche \
  --message "Raison precise de l'echec"
```

## Etape 6 — Relancer l'Orchestrateur

Si `orchestrateur_cmd` est renseigne dans `01_Orchestrateur/config.json`,
execute-le une fois pour que `CP1` s'ouvre (ou que l'echec soit compte).
Sinon, dis a Franco que ce sera pris en compte au prochain passage.

## Fichiers

- Lus : `videos/{video_id}/state.json` (dont **tout le bloc `consignes`**),
  `00_Profil/profil_chaine.md`, `00_Profil/projets_franco.md`,
  `02_Veille_hebdo/*_analyse_concurrentielle.md`
- Ecrits : `videos/{video_id}/01_recherche.md`,
  `videos/{video_id}/state.json` (uniquement `etapes.E1_recherche` et,
  en mode `veille_actu`, `sujet`/`angle`/`titre_travail`)
