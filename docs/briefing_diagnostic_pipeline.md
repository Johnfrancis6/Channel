# Briefing — diagnostic complet du pipeline

*Écrit le 12/09/2026 pour être lu par une session neuve. À utiliser
**bloc par bloc** : Franco annonce « bloc N », la session lit ce qui est
listé dans ce bloc-là, et rien d'autre.*

---

## Bloc 0 — Cadrage (à lire en premier, toujours)

### Le projet

Chaîne YouTube semi-automatisée de Franco : Shorts *faceless*, tech/IA, en
anglais. Un pipeline en 10 étapes, des agents Claude Code, un orchestrateur
Python sans serveur, `state.json` comme unique source de vérité, et trois
checkpoints où Franco valide.

### À lire pour ce bloc

| Fichier | Pourquoi |
|---|---|
| `CLAUDE.md` | les règles du dépôt |
| `docs/architecture_chaine_v1.2.md architecture_chaine_v1.2.md` §0 à §6 | la référence — **le nom de fichier est bien dupliqué avec une espace, c'est voulu** |
| `docs/diagnostic_pipeline.md` — « Grille », « Décisions transverses », « File d'attente » | ce qui a déjà été tranché |

**Ne lis pas le reste maintenant.** Chaque bloc dit ce qu'il lui faut.

### Les règles qui ne se négocient pas

- **Ne jamais éditer `.claude/skills/`** : c'est un miroir généré. On modifie
  `agents/short-*/`, `skills/*/` ou `outils/`, puis on relance
  `python3 agents/_synchroniser_vers_claude_skills.py`.
- Tests : `python3 -m unittest discover -s tests` (304 au vert au 12/09).
- Composants : `cd composants && npm run typecheck`.
- **`git fetch` avant chaque push** — Franco pousse depuis plusieurs
  sessions. On résout en gardant les deux côtés, jamais en écrasant.

### La branche, avant toute chose

**`main` ne contient pas le projet.** Il porte deux fichiers : `CLAUDE.md`
et le document d'architecture. Tout le reste — orchestrateur, agents,
skills, composants, tests, journal : 155 fichiers — vit sur
`claude/practical-hamilton-37892t`, qui n'a jamais été fusionnée.

Une session qui démarre sur une branche tirée de `main` ne voit donc rien
du pipeline, et croira légitimement que le dépôt est vide. Si c'est le cas,
repars de la branche de travail **en gardant ton nom de branche assigné** :

```bash
git fetch origin
git log origin/main..HEAD          # d'abord : as-tu des commits a garder ?
git checkout -B <ta-branche> origin/claude/practical-hamilton-37892t
```

`main` est un ancêtre direct de la branche de travail : il n'y a aucune
divergence à résoudre.

**Cette anomalie est elle-même un point de diagnostic** (bloc 6) : tant que
le travail n'est pas fusionné dans `main`, chaque nouvelle session repart
de deux fichiers. La fusion appartient à Franco.

### La méthode, et pourquoi elle compte

Une leçon revient à chaque étape de la revue en cours, et c'est la seule
chose à retenir de la méthode :

> **Le dépôt teste ce qui existe, pas ce qui devrait exister.**

Les défauts trouvés cette semaine étaient tous invisibles aux tests :

- trois défauts de dessin des composants, vus seulement en **regardant les
  rendus** ;
- trois règles de structure écrites de bonne foi, invalidées par la
  **première transcription réelle** mesurée ;
- une publication défaite par l'orchestrateur — le bug ne vivait dans aucun
  des deux composants, mais dans leur **articulation** ;
- un débit de référence faux de 14 %, parce qu'on comptait des mots jamais
  prononcés.

Donc : **ouvre les artefacts réels avant de juger le code.** Le Drive de
Franco est accessible par le connecteur Google Drive. Une affirmation qui
n'a pas été vérifiée sur un fichier réel se dit comme une hypothèse.

### Ce qui a déjà été diagnostiqué (ne pas refaire)

E1, CP1, E2+E3, E4, E5, E6, CP3, E7, A3, H1, le déclenchement et le
recalage son/image ont été repris entre le 11 et le 12/09. Le journal `docs/diagnostic_pipeline.md`
dit pour chacun ce qui a été corrigé et pourquoi. **Le rôle de cette
session n'est pas de refaire ce travail, mais de le vérifier sur les
artefacts réels et de traiter ce qui reste.**

Un seul trou connu : **CP2 n'a jamais été examiné sur un fichier réel.**

---

## Bloc 1 — L'état réel, avant tout jugement

**Objectif** : partir de faits, pas du code.

### À lire

- Sur le Drive : `videos/2026-09-11_v01/state.json`,
  `01_Orchestrateur/config.json`, `TABLEAU_DE_BORD.md`
- Dans le dépôt : `schemas/state_schema.json`

### Ce qui était vrai le 12/09 (à revérifier, pas à recopier)

| Fait | Valeur |
|---|---|
| Vidéos existantes | une seule, `2026-09-11_v01` |
| Son étape | `CP3`, `attente_validation` |
| Audio / rendu | **82,5 s** contre **98,9 s** → 16,4 s d'écart |
| `04_phrases.json` | **absent** (run antérieur à la révision) |
| Tentatives E4 | **8** déclarées, **9 échecs** enregistrés — deux échecs ne se rattachent à aucun run (anomalie de traçabilité). F5-TTS en deux régimes : 5 échecs à **93-98 %** (fuite de référence) puis 4 à **8-18 %** (marginaux). Qwen3-TTS ensuite : 0,87 % |
| `orchestrateur_cmd` | `null` — le cron n'est pas branché |
| `mode_agents` | `reel` ✅ |
| `chaines_concurrentes.json` | `[]`, 2 octets — **vide** |
| `lexique_prononciation.md` | 7 entrées, dont **5 épelées** (`L L M`, `G P T five`, `v L L M`, `V S Code`, `M C P`) ; `Git Hub` scindée, `rag` légitime. Contraire au §7.4 |
| `projets_franco.md` | **absent du Drive** (facultatif depuis le 11/09) |
| `consignes` de la vidéo 1 | tout en `note_franco` libre ; les champs `format` / `reference` / `idees_max` sont postérieurs |

**Livrable** : un état des lieux en 10 lignes. Ce qui a bougé depuis le
12/09, et ce qui n'a pas bougé alors qu'il aurait dû.

---

## Bloc 2 — E1 + CP1 : la recherche

**Objectif** : vérifier que le réajustement d'A2 tient sur un cas réel.

### À lire

- `agents/short-chercheur/SKILL.md`
- Sur le Drive : `videos/2026-09-11_v01/01_recherche.md` et le rapport
  `checkpoints/rapport_CP1.md`
- `orchestrateur/engine.py` — `RESUME_SOURCES`, `_extraire_sections`

### Ce qui est déjà su

Le rapport CP1 perdait sa section « Points à trancher » à la troncature :
l'extrait préserve désormais d'abord les sections qui portent la décision.
A2 a une branche `sujet_impose` et un gabarit en 7 sections.

### Questions ouvertes

- Sans analyse concurrentielle (bloc 7), sur quoi A2 fonde-t-il son angle ?
- Le rapport CP1 permet-il vraiment de décider **sans ouvrir les sorties** ?

---

## Bloc 3 — E2 + E3 + CP2 : rédaction, filtre TTS, budget ⚠️ priorité

**Objectif** : c'est **le seul trou** du diagnostic. CP2 n'a jamais été
ouvert sur un fichier réel, alors que CP1 et CP3 cachaient chacun un défaut
qu'aucun test ne pouvait attraper.

### À lire

- `agents/short-redacteur/SKILL.md`, `agents/short-filtre-tts/SKILL.md`
- `agents/short-filtre-tts/scripts/metriques.py`
- Sur le Drive : `videos/2026-09-11_v01/03_script_final.md`,
  `03_script_tts.txt`, `03_rapport_metriques.md`, et
  `checkpoints/rapport_CP2.md`
- `docs/architecture_chaine_v1.2.md architecture_chaine_v1.2.md` §7.3 et §7.4

### Ce qui est déjà su

- La durée se calibre en **idées** (3 max, exceptions admises), pas en
  secondes. `durée = idées × mots_par_idée ÷ 2,8 mots/s`.
- `MOTS_PAR_IDEE_DEFAUT = 45`, **tout compris** — hook, promesse, exemple et
  CTA pèsent la moitié d'un script, les idées seules l'autre moitié.
- La constante de débit a été fausse deux fois (2,5 puis 3,2) avant 2,8. Le
  3,2 venait de compter les marqueurs de mise en scène `[...]`, jamais
  prononcés.
- Règle des sigles (§7.4) : écriture normale, **pas d'épellation**.

### Ce qu'il faut regarder

1. Le rapport CP2 permet-il de trancher, ou noie-t-il la décision comme le
   faisait CP1 ?
2. Le script réel tient-il le budget en idées, mesuré et non estimé ?
3. Le lexique du Drive contredit le §7.4 (7 entrées épelées). Il a été écrit
   **après** le script de la vidéo 1, donc il n'a rien abîmé — mais il
   s'appliquerait à tous les suivants. Le ramener à ce que le §7.4 autorise.

---

## Bloc 4 — E4 : l'audio

**Objectif** : vérifier le notebook et débloquer la vidéo 1.

### À lire

- `notebooks/voix_off.ipynb` (Cell 1 pour les modes, Cell 5 et 7)
- `notebooks/README.md`
- Sur le Drive : `videos/2026-09-11_v01/04_rapport_audio.md`
- `docs/architecture_chaine_v1.2.md architecture_chaine_v1.2.md` §7.2

### Ce qui est déjà su

Plafond de tentatives appliqué dans le notebook (la règle vivait dans
l'orchestrateur, qui ne tourne pas entre deux runs Colab), diagnostic WER
gradué (structurel au-delà de 30 %), nom d'agent pris du state, et écriture
de `04_phrases.json`.

### Une piste ouverte au bloc 1, à instruire ici

Le lexique fait prononcer `L L M`, `M C P`, `V S Code`. Si Whisper
retranscrit `LLM`, le WER compte des erreurs qui n'en sont pas — ce qui
expliquerait des runs F5-TTS bloqués à 8-18 % **sans défaut audio réel**.

Deux faits à croiser avant de conclure :

- le `03_script_tts.txt` **actuel** ne contient aucune forme épelée (`Step
  one is the plain LLM`, `a VS Code tool called MCP`) — vérifié ;
- mais il a été **modifié le 11/09 à 15:41**, soit après le dernier échec
  (15:31) et juste avant le run Qwen3 réussi (15:45). Les runs à 8-18 % ont
  donc tourné sur une version que personne n'a relue.

La modification de 15:41 est peut-être exactement le retrait des
épellations. **Le test est l'historique des versions du fichier sur le
Drive** (Google Drive garde les révisions) : si la version d'avant 15:41
contient `L L M`, l'hypothèse est confirmée et le §7.4 gagne sa preuve la
plus solide. Sinon, elle tombe, et les 8-18 % restent à expliquer.

Ne conclus pas sans cette version : c'est la seule donnée qui tranche.

### Le blocage concret à traiter

Relancer l'audio de la vidéo 1 est bloqué **deux fois** : `E4_audio.statut`
vaut `termine`, et `tentatives = 8` dépasse le plafond de 3. Or
`04_phrases.json` n'est écrit que par une **synthèse complète**.

**Réglé le 12/09** : `outils/phrases_depuis_timestamps.py` reconstruit les
bornes depuis les timestamps mot à mot, sans re-synthèse ni édition
manuelle. Une commande, décrite au §7.2. Il reste à **la lancer** sur la
vidéo 1, puis à relancer A7.

Attention : c'est une approximation (le script mesure son alignement et
refuse d'écrire sous 80 %), et le fichier produit porte
`source: "reconstruit"`. Pour une vidéo neuve, c'est le notebook qui a
raison.

---

## Bloc 5 — E5 + E6 + CP3 : storyboard, montage, la vidéo

**Objectif** : la qualité d'animation, et le décalage son/image.

### À lire

- `agents/short-designer/SKILL.md`, `agents/short-monteur/SKILL.md`
- `composants/src/animation.ts` — les 8 règles de naturel
- `composants/src/components/` — 5 composants
- `agents/short-monteur/scripts/construire_props.py`
- `docs/architecture_chaine_v1.2.md architecture_chaine_v1.2.md` §8

### Ce qui est déjà su

Lottie a été **écarté** (un fichier pré-rendu ne peut pas illustrer un
schéma dont le contenu change) : tout est codé en Remotion, et la fluidité
se code — d'où `animation.ts`. Le style visé est le **sticker animé**.
`outils/generer_apercus.py` rend une image par composant à travers la
composition réelle : c'est ce catalogue qui a révélé trois défauts de dessin
que les tests ne voyaient pas.

### Ce qu'il faut faire, pas seulement lire

**Rendre les aperçus et les regarder.** Rendu Remotion :
`PLAYWRIGHT_BROWSERS_PATH=/opt/pw-browsers`, binaire
`chromium_headless_shell`. Ne pas lancer `playwright install`.

---

## Bloc 6 — E7, cycle de vie, orchestrateur et cron

**Objectif** : vérifier que la fin du pipeline tient.

### À lire

- `skills/short-publier/SKILL.md` et `scripts/publier.py`
- `orchestrateur/engine.py` — `_mettre_a_jour_statut_global`, `traiter_video`
- `orchestrateur/constants.py` — `STATUTS_E7`, `STATUTS_CLOS`
- `outils/lancer_orchestrateur.py`
- `docs/architecture_chaine_v1.2.md architecture_chaine_v1.2.md` §5.3, §6.4, §11

### Ce qui est déjà su

`publier.py` écrivait `publiee`, et le passage suivant de l'orchestrateur
réécrivait `prete` (CP3 étant valide) : la commande censée confirmer la
publication la défaisait. Règle posée : **au-delà de `prete`, le statut
appartient à E7**. Une vidéo publiée ou abandonnée sort du pipeline.
`abandonnee` est maintenant écrit par quelqu'un — il était lu par quatre
endroits et écrit par personne.

Le cron est décidé (toutes les 15 min) et le lanceur est écrit et testé,
mais **la crontab n'est peut-être pas encore installée** : vérifier
`orchestrateur_cmd` dans `config.json` et l'existence de
`01_Orchestrateur/journal_cron.log`.

---

## Bloc 7 — A3 et H1 : l'hebdomadaire et le corpus

**Objectif** : les deux agents hebdo n'ont **jamais tourné**.

### À lire

- `agents/short-analyse-chaines/SKILL.md`
- `agents/short-amelioration/SKILL.md`
- `outils/analyser_transcription.py`

### Ce qui est déjà su

A3 produisait de la prose inagrégeable : le LLM segmente (reconnaître un
hook demande de comprendre le propos), le script mesure et valide —
vocabulaire de rôles **fermé**, corpus `02_Veille_hebdo/corpus_structures.jsonl`
en **ajout seul**. H1 ne lisait pas les `state.json` : il cherchait des
motifs sans avoir les événements. Il calcule maintenant des indicateurs et
relit `03_Amelioration/recommandations.jsonl` avant de proposer.

### Le blocage

`chaines_concurrentes.json` est vide. **Tant qu'il l'est, A3 n'a rien à
analyser.** Depuis le 12/09 c'est A3 qui le remplit : Franco donne ses
chaînes en conversation (URLs ou `@handles`), le script les résout et les
fusionne dans le fichier, en ajout seul. Demande-lui la liste.

---

## Bloc 8 — Synthèse

**Livrable** : mettre à jour `docs/diagnostic_pipeline.md` (file d'attente
et « en attente de Franco »), puis proposer **trois** chantiers classés, pas
une liste de vingt. Ce qui fait avancer une vidéo de plus passe avant ce qui
consolide l'existant.

---

## Ce qui appartient à Franco, et à personne d'autre

- installer la crontab et remplir `orchestrateur_cmd` ;
- **donner** sa liste de chaînes concurrentes à A3 (c'est A3 qui écrit le fichier) ;
- corriger `00_Profil/lexique_prononciation.md` (épellations) ;
- le **format** de la vidéo 2 et la **vidéo de référence** pour la
  segmentation ;
- valider ou refuser le CP3 de la vidéo 1 ;
- `projets_franco.md`, facultatif, à remplir au fil des vidéos.

## Ce qu'il ne faut pas faire

- Croire un test vert : il prouve que le code fait ce qu'on a écrit, pas
  qu'on a écrit la bonne chose.
- Élargir un chantier sans le dire. Franco travaille **étape par étape** et
  tranche lui-même.
- Toucher à `.claude/skills/` à la main.
- Pousser sans `git fetch`.
