# Document d'Architecture — Chaîne YouTube Semi-Automatisée — v1.2

*Révision du 10/09/2026 : v1.1 (revue d'architecture) + v1.2 (skills `new-short` et `short-state`). Ce document est la référence unique pour la mise en place de l'écosystème.*

---

## 0. Changements

### Revue d'architecture du 11/09/2026

Relecture de fond du workflow, doc contre code. Le détail et le raisonnement sont dans [revue_architecture_2026-09-11.md](revue_architecture_2026-09-11.md) ; ce document intègre les décisions.

- **Direction artistique** : décidée par A6 par scène (`da` dans le storyboard) + principes récurrents dans `charte.json > animation`. Pas d'agent Art Director dédié (§8, §12).
- **Durées de scènes recalées sur l'audio réel** : le notebook écrit `04_phrases.json`, `construire_props.py --phrases` recale borne à borne, et la composition ne dure jamais moins que la voix off (§7.2, §8). Le §4.3 promettait ce recalage depuis la v1.1 ; il n'était fait nulle part.
- **Le cycle de vie d'une vidéo peut se fermer** : skill `short-publier` (§11, §14). Rien n'écrivait `publiee` ni `date_effective`, que le tableau de bord et `short-state` lisent pourtant tous les deux.
- **Vérification visuelle avant le CP3** : A7 rend des images fixes et les regarde (§8).
- **Règle des sigles** : écriture normale (`LLM`), pas d'épellation (`L L M`) — l'épellation casse le contrôle qualité WER (§7.4).
- **Sections remises à jour sur le code réel** : §4.3 (A6/A7), §5.4 (`state.json`), §7.2 (notebook Qwen3-TTS et ses modes), §9.1 et §9.2 (arborescences), §12.

### Diagnostic étape par étape — à partir du 11/09/2026

Relecture du pipeline étape par étape sur les artefacts réellement produits. Journal, décisions et file d'attente dans [diagnostic_pipeline.md](diagnostic_pipeline.md).

- **La durée se calibre en idées, pas en secondes** : 3 idées maximum, le coût en mots d'une idée dépend du **format**. Une interview fictive dépasse 60 s sans déroger à la règle (§9.1, §14).
- **Consignes structurées à la création** : `format`, `reference` et `idees_max` remplacent le fourre-tout de `note_franco`, et sont lues par le Chercheur **et** le Designer.
- **Le rapport de checkpoint ne perd plus sa partie décisionnelle** : l'extrait préserve d'abord les sections qui portent la décision (§5.5).
- **Titre de travail borné à 80 caractères** : un sujet d'une phrase entière ne fait pas un titre.

### v1.2 (création des skills)

- **Le registre n'est plus écrit par plusieurs acteurs.** `state.json` est la seule source de vérité. `registre_videos.json` devient une vue reconstruite par l'Orchestrateur, et `short-state` le recalcule en direct. Aucun fichier partagé n'est écrit par deux acteurs.
- **Trois nouveaux fichiers** :
  - `02_Veille_hebdo/backlog_sujets.json` : sujets validés en lot ;
  - `01_Orchestrateur/config.json` : commande de l'Orchestrateur et seuils ;
  - `01_Orchestrateur/derniere_execution.json` : horodatage du dernier passage.
- **Deux skills livrés** : `new-short` (déclenche une vidéo) et `short-state` (état en lecture seule), décrits au §14.
- **Question ouverte** : rendre le pipeline multi-chaînes (§12).

### v1.1 (par rapport à la v1.0)

| Sujet | v1.0 | v1.1 |
|---|---|---|
| Filtre TTS | Après le Checkpoint 2 | **Avant** le Checkpoint 2 : Franco valide un script déjà propre |
| Prononciation | Non traitée | **Lexique de prononciation** maintenu dans `00_Profil/` |
| Designer | Miniatures | **Charte visuelle** (validée en lot) + **storyboard** par vidéo. Pas de miniature pour l'instant |
| Agents | 10 listés, "9 obligatoires" | **7 agents pipeline + 1 agent hebdomadaire**. Profil de chaîne et Architecte deviennent des sessions de travail |
| Suivi d'état | Rapports de checkpoint | **`state.json` par vidéo**, écrit par chaque agent, lu par un Orchestrateur sans serveur |
| Drive | Par type de fichier | **Par vidéo**, + registre des vidéos + tableau de bord permanent |
| Amélioration continue | Logs + métriques TTS + notes | + **performances YouTube** (rétention, swipe, vues) |
| Rythme de production | Tout au quotidien | **Tampon** pour les piliers intemporels, **voie rapide** pour l'actu IA |
| Analyseur de chaînes | Par vidéo | **Hebdomadaire** |
| Voix off | Cron Colab multi-comptes | **Run Colab lancé par Franco**, notebook avec clonage de voix et contrôle qualité automatique |
| Animation | Choix d'outil par thème | **Bibliothèque de composants réutilisables**, créée et enrichie au fil des vidéos par Claude Code |
| Publication | Toujours manuelle | **Phase test manuelle**, puis **publication automatisée** après validation CP3 (voir §11) |

---

## 1. Vision de la chaîne (inchangée)

- **Type** : faceless total
- **Format** : Shorts (vertical 1080×1920)
- **Langue** : anglais
- **Niche** : tech / IA appliquée, actu IA décodée
- **Audience** : débutants curieux
- **Angle** : "ingénieur ML" qui décode et teste. Les projets réels de Franco servent d'illustration ponctuelle.
- **5 piliers** : actu IA décodée, avis sur des outils testés, vulgarisation de concepts, projets perso en construction, tutos pratiques

---

## 2. Périmètre et règles fixes

**Le système NE DOIT PAS :**
- choisir le sujet final d'une vidéo sans l'accord de Franco ;
- gérer le SEO (titres, descriptions, tags) : c'est Franco qui le fournit ;
- publier une vidéo dont le Checkpoint 3 n'est pas validé.

**3 checkpoints humains par vidéo :**
1. **CP1** : validation du sujet et de l'angle (en lot pour la voie tampon, individuel pour la voie rapide)
2. **CP2** : validation du script **propre**, c'est-à-dire déjà passé par le Filtre TTS, avec la version TTS affichée à côté
3. **CP3** : validation du rendu final, puis petites retouches

**Autres règles :**
- **Charte visuelle** validée en lot, une fois au démarrage puis à chaque évolution majeure
- **Retry** : 3 tentatives maximum par étape, puis alerte à Franco
- **Travail par étapes** : chaque étape écrit son état avant et après son exécution, et le tableau de bord reflète en permanence l'état du process
- **Cadence** : quotidienne, soutenue par un tampon de vidéos prêtes d'avance

---

## 3. Sessions de travail (hors pipeline)

Ces rôles ne tournent pas automatiquement. Ce sont des sessions dédiées avec Franco.

- **Session Profil de chaîne** : produit `profil_chaine.md`, le lexique initial et, avec le Designer, la charte visuelle. Toute mise à jour est validée par Franco.
- **Session Architecture** : produit et maintient ce document, la structure Drive, le dépôt de code et le squelette de l'Orchestrateur.

---

## 4. Les agents

### 4.1 Vue d'ensemble

| # | Agent | Cadence | Déclenché par | Produit | Autonomie |
|---|---|---|---|---|---|
| A1 | Orchestrateur | À chaque exécution (cron ou manuel) | Cron / Franco | Tableau de bord, registre, log | Autonome entre checkpoints |
| A2 | Chercheur web | Hebdo (tampon) + quotidien (actu) | Orchestrateur | Sujets proposés, `01_recherche.md` | Semi-autonome |
| A3 | Analyseur de chaînes | Hebdomadaire | Orchestrateur | Analyse concurrentielle | Autonome sur la liste fournie |
| A4 | Rédacteur de script | Par vidéo | Orchestrateur, après CP1 | `02_script_brut.md` | Boucle avec A5, puis CP2 |
| A5 | Filtre TTS | Par vidéo | Orchestrateur, après A4 | Script final + version TTS + rapport | Autonome, 3 tentatives |
| A6 | Designer | Charte : ponctuel. Storyboard : par vidéo | Orchestrateur, après CP2 | Charte, `05_storyboard.md` | Charte validée en lot |
| A7 | Monteur vidéo | Par vidéo | Orchestrateur, après audio + storyboard | `06_video_finale.mp4` | Autonome, puis CP3 |
| H1 | Amélioration continue | Hebdomadaire | Orchestrateur | Rapport hebdo | Diagnostic autonome, recommandations validées par Franco |

### 4.2 Contrat commun à tous les agents

Chaque agent respecte les mêmes règles vis-à-vis de `state.json` :
1. **Au démarrage**, il écrit dans sa propre étape `statut: en_cours`, l'heure de début et le numéro de tentative.
2. **À la fin**, il écrit `termine` avec la liste des fichiers produits, ou bien `echec` avec un message explicite.
3. Il ajoute une ligne dans `historique`.
4. Il **ne modifie jamais** l'étape d'un autre agent ni les blocs de validation. Seul l'Orchestrateur y écrit, en retranscrivant les décisions de Franco.

### 4.3 Détail par agent

**A1 — Orchestrateur**
- Il ne garde aucune mémoire entre deux exécutions : les `state.json` sont sa seule source de vérité.
- À chaque exécution :
  1. il pose un verrou (`01_Orchestrateur/verrou.json`, qui expire au bout d'un délai fixé) pour empêcher deux exécutions simultanées ;
  2. il lit le registre et les `state.json` des vidéos actives ;
  3. il décide pour chaque vidéo : lancer l'étape suivante, relancer une étape en échec (moins de 3 tentatives), lever une alerte (3 échecs) ou attendre Franco (checkpoint ou audio) ;
  4. il lit les décisions de Franco dans les `rapport_CPx.md` et les retranscrit dans `state.json`. Pour le CP1 groupé, il ajoute les sujets validés dans `backlog_sujets.json` ;
  5. si le tampon descend sous la cible, il crée de nouvelles vidéos à partir du backlog, avec la même logique que `new-short` ;
  6. il déclenche les tâches hebdomadaires (A3, H1, lot de sujets A2) ;
  7. il régénère `TABLEAU_DE_BORD.md` et la vue `registre_videos.json`, écrit `derniere_execution.json`, puis libère le verrou.

**A2 — Chercheur web**
- **Son métier change selon `consignes.mode_recherche`.** En `sujet_impose` — le mode courant — Franco a déjà tranché le sujet et l'angle : A2 ne les rediscute pas, il les **vérifie, les étaye et trouve l'exemple qui les incarne**. En `sujet_backlog` il précise une esquisse d'angle ; en `veille_actu` seulement, il propose un sujet.
- Il livre **`idees_max` faits porteurs** et marque le reste « bonus, écartable ». Sans cette hiérarchie, A4 prend tout : six faits livrés à plat ont donné 258 mots pour un budget de 135 sur `2026-09-11_v01`.
- `01_recherche.md` compte sept sections : Sources · Faits vérifiés (porteurs / bonus) · **Matière à hook** (trois candidats) · Angle confirmé ou proposé · **Incertitudes assumées** · **Termes à risque de prononciation** · Points à trancher au CP1.
- Il lit `00_Profil/projets_franco.md` pour ses exemples : un exemple qui n'est pas **montrable à l'écran** ne sert à rien.
- **Vérification** : deux sources indépendantes sur le fait central, sans exception. Un fait secondaire à une seule source part en « Incertitudes assumées », pas en « Faits vérifiés » — sinon un chiffre invérifiable devient une affirmation de la chaîne.
- Chaque semaine, il produit `sujets_proposes_{AAAA-Sxx}.md` pour la voie tampon (piliers intemporels), soumis au CP1 groupé.
- Chaque jour, il fait une veille actu IA. Si un sujet mérite la voie rapide, il le propose au CP1 individuel.
- Pour chaque vidéo validée, il produit `01_recherche.md` : sources, faits vérifiés, angle "ingénieur ML".
- Ses inputs sont la liste de chaînes et mots-clés fournie par Franco et `profil_chaine.md`.

**A3 — Analyseur de chaînes (hebdo)**
- Il **segmente chaque vidéo** avec `outils/analyser_transcription.py` : le LLM attribue un rôle à chaque phrase (vocabulaire fermé — `hook`, `promesse`, `contexte`, `idee`, `exemple`, `transition`, `cta`, `sponsoring`), le script mesure et valide. Les mesures s'accumulent dans `02_Veille_hebdo/corpus_structures.jsonl`, **append-only**.
- Avant, il produisait une note en prose **indexée par chaîne** : ni mesurable, ni comparable, ni cumulable — et le hook, le CTA et le rythme sont des propriétés d'**une** vidéo, pas d'une chaîne. Le rapport hebdomadaire étant un fichier neuf chaque semaine, rien ne s'accumulait dans tout le système.
- Il accepte les chaînes sous trois formes : identifiant `UCxxxx`, `@handle`, ou URL (`--resoudre` les convertit).
- Il récupère les statistiques des concurrents via l'API YouTube Data, qui est la voie stable.
- Il analyse les transcriptions quand elles sont disponibles (hooks, CTA, structure). C'est la partie fragile : un échec de transcription ne bloque pas l'analyse des statistiques.
- Il produit `02_Veille_hebdo/{AAAA-Sxx}_analyse_concurrentielle.md`, lu par A2 et A4.

**A4 — Rédacteur de script**
- Inputs : recherche, dernière analyse concurrentielle, profil de chaîne, commentaire de CP1.
- Il rédige le script (hook, promesse spectateur, marqueurs de voix, style oral) en incarnant l'angle "ingénieur ML". Son prompt est à calibrer finement.
- **Il écrit sous budget** : `consignes.idees_max` idées porteuses, ~45 mots chacune. Si la recherche donne six faits, il en garde trois — les autres sont pour une autre vidéo.
- Il reçoit le retour de A5 et révise son script. La boucle A4 ↔ A5 compte au maximum 3 tours.

**A5 — Filtre TTS**
Il intervient avant le CP2 et fait quatre choses :
0. **Budget** : le script tient-il dans `consignes.idees_max` idées ? C'est le seul point du pipeline où la longueur est mesurée avant l'enregistrement (§7.3).
1. **Style** : il mesure les zombie nouns, les triades et la longueur des phrases (seuils à calibrer). En cas d'échec, il renvoie le script à A4 avec un retour précis.
2. **Calibrage des phrases pour la synthèse** : il applique les règles du §7.3 (phrases ni trop longues, ni trop courtes).
3. **Normalisation phonétique** : il applique le lexique (sigles, noms de modèles, numéros de version, chiffres en toutes lettres).

Il produit :
- `03_script_final.md` : la version lisible, celle que Franco valide au CP2 ;
- `03_script_tts.txt` : une phrase par ligne, lexique appliqué, dérivée mécaniquement du script final sans changement de sens ;
- `03_rapport_metriques.md` : les métriques et les **nouveaux termes inconnus**, avec une proposition de prononciation à valider au CP2.

**A6 — Designer**
- **Charte visuelle** (ponctuelle, validée en lot) : palette, typographie des sous-titres, rythme des transitions, frame d'accroche, style d'illustration. Elle est livrée en deux formats : `charte.md` pour l'humain et `charte.json` pour le code (design tokens).
- **Cadrage** (par vidéo, avant le storyboard) : A6 analyse le script, élabore **ce qui est faisable** au vu du catalogue visuel et du jeu de base Lottie, et écrit `05_cadrage.md` — ce que chaque bloc doit montrer **à l'écran** (l'image, pas la clé), le coût de ce qui manque, et ses questions. Il le soumet à Franco et attend ses ajustements avant d'écrire le storyboard. C'est un dialogue, pas une étape de la machine d'états : rien ne change dans §6.2. Si Franco n'est pas disponible, A6 poursuit sur sa proposition et le signale à la clôture.
- **Storyboard** (par vidéo, après le CP2, en parallèle de l'audio) :
  - découpage du script en scènes — **une scène par phrase de `03_script_tts.txt`** (le recalage des durées sur l'audio en dépend, §8) ;
  - pour chaque scène, le composant de la bibliothèque à utiliser et ses paramètres ;
  - pour chaque scène, sa **direction artistique** : `mouvement`, `rythme`, `technique`, `accent` (vocabulaire fermé, §8) ;
  - la liste des **nouveaux composants nécessaires** s'il en manque.
- Il produit **trois fichiers** : `05_cadrage.md` (l'intention, discutée avec Franco), `05_storyboard.md` (lecture humaine, revue au CP3) et `05_storyboard.json` (lu par le Monteur).
- Le script `generer_storyboard.py` ne produit qu'un **squelette** (une scène par phrase, durées estimées, DA par défaut de la charte), marqué `a_completer`. Le choix du composant, des paramètres et de la direction artistique reste le travail de l'agent.

**A7 — Monteur vidéo**
- Inputs : storyboard, `04_voixoff.wav`, `04_timestamps.json`, `04_phrases.json`, charte.
- Il réutilise d'abord les composants existants. Sinon, il en crée de nouveaux avec Claude Code et les ajoute à la bibliothèque (§8).
- **Il n'invente pas le style** : la direction artistique vient du storyboard (A6) et de `charte.json > animation`. Il l'implémente, il ne la rejuge pas.
- Il cale les **sous-titres** sur les timestamps mot par mot et les **durées de scènes** sur les bornes de phrases de `04_phrases.json`, puis rend `06_video_finale.mp4` avec l'audio déjà synchronisé.
- Avant de clore l'étape, il rend quelques **images fixes** (`remotion still`) et les regarde : rien ne part au CP3 sans avoir été vu.
- Le rendu passe par `rendre_video.py`, qui vérifie les prérequis avant et le MP4 produit après.

**H1 — Amélioration continue (hebdo)**
- Inputs :
  - logs et rapports de checkpoint ;
  - métriques du Filtre TTS ;
  - rapports audio (phrases signalées par le contrôle qualité) ;
  - notes de Franco ;
  - **performances YouTube** : rétention, taux de swipe, vues. Au démarrage, via un export CSV manuel ; ensuite, via l'API YouTube Analytics.
- Il fait une analyse ouverte du workflow et identifie lui-même les points faibles.
- Il produit un rapport hebdomadaire avec des recommandations : ajustement des prompts de A4 et A5, des seuils de calibrage des phrases, et des composants à refondre. Chaque recommandation est validée par Franco avant d'être appliquée.

---

## 5. Machine d'états et `state.json`

### 5.1 Principe

L'Orchestrateur n'a ni serveur ni mémoire. Tout l'état du système vit dans des fichiers :
- **`videos/{id}/state.json`** : l'état détaillé d'une vidéo, écrit par chaque agent ;
- **`registre_videos.json`** : une **vue** de toutes les vidéos conçues et de leur statut global, reconstruite à partir des `state.json`. Personne n'y écrit directement ;
- **`TABLEAU_DE_BORD.md`** : la vue humaine, régénérée à chaque exécution.

On peut donc arrêter le système n'importe quand : l'exécution suivante reprend exactement là où il en était.

### 5.2 Statuts d'une étape

| Statut | Signification |
|---|---|
| `a_venir` | Pas encore commencée |
| `en_cours` | Un agent travaille dessus |
| `termine` | Terminée, sorties disponibles |
| `echec` | Échec, sera relancée si moins de 3 tentatives |
| `alerte` | 3 échecs : intervention de Franco requise |
| `attente_validation` | Checkpoint en attente de la décision de Franco |
| `attente_franco` | Action manuelle requise (ex. lancer le run Colab) |
| `valide` / `refuse` | Décision de Franco à un checkpoint |

### 5.3 Statuts globaux (registre)

`idee` → `sujet_valide` → `en_production` → `prete` → `programmee` → `publiee`
(+ `abandonnee`, et `attente_franco` quand la vidéo est bloquée sur une action humaine)

Le dossier d'une vidéo **ne bouge jamais**. Seul son statut change dans le registre. Quand une vidéo est publiée, le registre passe à `publiee`, avec la date de publication et l'URL.

### 5.4 Exemple de `state.json`

La forme qui fait foi est `skills/new-short/assets/state_template.json`, validée par `schemas/state_schema.json`. Extrait :

```json
{
  "version_schema": 1,
  "video_id": "2026-09-10_v01",
  "cree_le": "2026-09-10T06:55:00Z",
  "cree_par": "new_short",
  "titre_travail": "What the new model actually changes",
  "sujet": "...", "angle": "...", "sujet_id": null,
  "pilier": "actu_ia",
  "voie": "rapide",
  "consignes": {
    "mode_recherche": "sujet_impose",
    "note_franco": "Stickman en intro, puis cutaway par étape",
    "format": "explication_progressive",
    "reference": "https://www.youtube.com/shorts/…",
    "idees_max": 3
  },
  "statut_global": "en_production",
  "etape_actuelle": "CP2",
  "boucle_A4_A5": 1,
  "etapes": {
    "E1_recherche": { "agent": "chercheur", "statut": "termine", "tentatives": 1,
                      "debut": "2026-09-10T07:00:00Z", "fin": "2026-09-10T07:06:00Z",
                      "sorties": ["01_recherche.md"] },
    "CP1":          { "statut": "valide", "commentaire": "Angle OK, insister sur le test", "date": "2026-09-10T08:15:00Z" },
    "E2_redaction": { "agent": "redacteur", "statut": "termine", "tentatives": 2, "sorties": ["02_script_brut.md"] },
    "E3_filtre":    { "agent": "filtre_tts", "statut": "termine", "tentatives": 2,
                      "sorties": ["03_script_final.md", "03_script_tts.txt", "03_rapport_metriques.md"] },
    "CP2":          { "statut": "attente_validation", "commentaire": null, "date": null },
    "E4_audio":     { "agent": "colab_voix", "statut": "a_venir", "tentatives": 0, "debut": null, "fin": null, "sorties": [] },
    "E5_storyboard":{ "agent": "designer",   "statut": "a_venir", "tentatives": 0, "debut": null, "fin": null, "sorties": [] },
    "E6_montage":   { "agent": "monteur",    "statut": "a_venir", "tentatives": 0, "debut": null, "fin": null, "sorties": [] },
    "CP3":          { "statut": "a_venir", "commentaire": null, "date": null,
                      "seo": { "titre": null, "description": null, "tags": [] } },
    "E7_publication":{ "agent": "publication", "statut": "a_venir", "tentatives": 0, "debut": null, "fin": null, "sorties": [] }
  },
  "publication": { "date_prevue": null, "date_effective": null, "url": null },
  "historique": [
    { "horodatage": "2026-09-10T09:02:00Z", "agent": "filtre_tts", "evenement": "echec",
      "message": "Tentative 1 : 3 phrases > 22 mots, 2 triades" },
    { "horodatage": "2026-09-10T09:10:00Z", "agent": "filtre_tts", "evenement": "termine", "message": "Tentative 2 OK" }
  ]
}
```

Quelques champs méritent un mot :

- **`boucle_A4_A5`** : compteur de tours de révision rédaction ⇄ filtre, écrit par l'Orchestrateur. Au 3ᵉ tour, `E3_filtre` passe en `alerte` (§4.3, A5). Un refus au CP2 le remet à zéro : un refus n'est pas un échec technique.
- **`etapes.CP3.seo`** : les champs SEO remplis par Franco au CP3 (§11).
- **`consignes`** : ce que Franco impose à la création (§14). `format` porte le budget en mots par idée et sert de clé au corpus ; `reference` est une vidéo dont on reprend le gabarit narratif ; `idees_max` est le budget du Short — **un nombre d'idées, pas une durée**. Ces trois champs sont lus par le Chercheur (A2) **et** par le Designer (A6) : avant eux, une consigne de mise en scène n'avait que `note_franco` comme porte d'entrée et n'atteignait le Designer que par ricochet, recopiée dans la recherche puis dans le script.
- **Toutes les étapes portent `agent`**, y compris `E4_audio` (`colab_voix`, le notebook) et `E7_publication` (`publication`, le skill `short-publier`) : les scripts d'étape s'en servent pour savoir à qui attribuer l'écriture.

### 5.5 Protocole de validation

Pour que Franco n'ait pas à modifier du JSON à la main, notamment depuis son téléphone, chaque checkpoint génère `checkpoints/rapport_CPx.md`. Ce fichier contient le résumé à valider, suivi d'un bloc de décision :

```markdown
## DÉCISION
Statut : EN_ATTENTE        <!-- remplacer par VALIDE ou REFUSE -->
Commentaire :
```

**Ce qui porte la décision survit à la coupe.** Le résumé est un extrait borné ; l'extraction suit les sections Markdown et garde en priorité celles qui portent la décision — « Points à trancher », « Angle proposé », « Nouveaux termes », « Nouveaux composants ». Une troncature naïve par le début coupait le rapport de CP1 en plein milieu d'une phrase et jetait précisément les questions posées à Franco, ne laissant que les sources : le fichier fait pour décider depuis un téléphone faisait écran au lieu de servir.

À l'exécution suivante, l'Orchestrateur lit ce bloc et le retranscrit dans `state.json`. En cas de refus, l'agent précédent est relancé avec le commentaire en input. Au CP2, le bloc contient aussi les nouveaux termes du lexique, à valider ou corriger. Au CP3, il contient les champs SEO (§11).

---

## 6. Séquencement du pipeline

### 6.1 Cycle hebdomadaire (ex. dimanche)

1. **A3** : analyse concurrentielle de la semaine
2. **H1** : rapport d'amélioration continue, qui intègre les performances YouTube
3. **A2** : `sujets_proposes_{AAAA-Sxx}.md` pour la voie tampon
4. **CP1 groupé** : Franco valide les sujets en une seule fois
5. **A1** : crée un dossier vidéo par sujet validé

### 6.2 Par vidéo

```
E1 Recherche (A2)
   │
CP1 ── sujet / angle ─────────────── [Franco]
   │
E2 Rédaction (A4) ⇄ E3 Filtre TTS (A5)   ← max 3 tours
   │
CP2 ── script propre + version TTS + nouveaux termes du lexique ── [Franco]
   │
   ├──► E4 Audio : attente_franco → Franco lance le run Colab → le notebook écrit "termine"
   │
   └──► E5 Storyboard (A6)                ← en parallèle de E4
   │
E6 Montage (A7)                            ← démarre quand E4 et E5 sont "termine"
   │
CP3 ── rendu final + champs SEO ───────── [Franco] → petites retouches
   │
E7 Publication                             ← manuelle (phase test) puis automatisée (§11)
```

### 6.3 Tampon et voie rapide

- **Voie tampon** : piliers intemporels (concepts, tutos, avis, projets). Cible : **3 à 5 vidéos `prete` d'avance**, à ajuster.
- **Voie rapide** : pilier actu IA, produit dans la journée avec un CP1 individuel. Une vidéo rapide passe devant le tampon dans le calendrier de publication.

---

## 7. Voix off — notebook Colab

### 7.1 Workflow

1. Après le CP2, l'Orchestrateur passe `E4_audio` en `attente_franco` et affiche dans le tableau de bord : « Lancer l'audio pour `2026-09-10_v01` ».
2. Franco ouvre le notebook, saisit `video_id` et le modèle, puis lance le run.
3. Le notebook lit `03_script_tts.txt`, génère l'audio, écrit ses sorties dans le dossier de la vidéo et passe `E4_audio` à `termine`.
4. À l'exécution suivante, l'Orchestrateur voit l'étape terminée et le workflow continue.

### 7.2 Structure du notebook

Le notebook est **modulaire** : Franco ne modifie que la Cell 1, où `MODE` décide des cellules actives — `full` (run complet), `resume_after_fail` (re-synthèse après échec, sans re-uploader la voix), `quality_check` (WER seul sur un audio existant), `voice_only` (échantillon de voix seul).

| Cellule | Rôle |
|---|---|
| 0. Setup & Auth | Dépendances, montage de Drive, chemins |
| 1. Config + MODE | **Seule cellule modifiée par Franco.** `VIDEO_ID` (détecté tout seul s'il est vide), `MODE`, nom de la voix, graine, seuils (`SEUIL_WER`, `PAUSE_MS`, `CIBLE_LUFS`, `DENOISE`) |
| 2. Voix | Premier usage ou nouvel upload : découpe d'un extrait de référence court, transcription de la référence, sauvegarde versionnée dans `00_Profil/voix/{nom}/vN/`. Sessions suivantes : chargement de la voix stockée. Accepte `.wav`, `.mp3`, `.m4a` (converti via ffmpeg). Débruitage `noisereduce` **désactivé par défaut** (`DENOISE = False`) |
| 3. Modèles | Chargement de Qwen3-TTS et de faster-whisper (mis en cache) |
| 4. Synthèse | Lecture de `03_script_tts.txt`, génération phrase par phrase, reprise sur OOM GPU |
| 5. Assemblage + Timestamps | Concaténation avec pauses calibrées, normalisation LUFS, puis faster-whisper `word_timestamps=True` → `04_timestamps.json`. Écrit aussi **`04_phrases.json`** : les bornes début/fin de chaque phrase dans l'audio assemblé |
| 6. Contrôle qualité | **WER global** sur l'audio assemblé (transcription vs `03_script_tts.txt`), ponctuation et casse normalisées. Sous le seuil : l'étape passe `termine`. Au-dessus : `echec`, avec un **diagnostic gradué** — voir ci-dessous |
| 7. Rapport + State | `04_rapport_audio.md` et mise à jour de `state.json` (§4.2) |
| 8. Bilan | Résumé console et prochaines actions |

**`04_phrases.json` est ce qui relie la voix au montage.** C'est la seule étape du pipeline qui connaisse exactement où commence et finit chaque phrase : après coup, on ne peut que le deviner en réalignant les mots transcrits sur le script, ce que le WER non nul rend fragile. A6 faisant une scène par phrase, ces bornes permettent à A7 de caler les durées de scènes sur la voix off (§8).

**Le plafond de tentatives vit dans le notebook, pas dans l'Orchestrateur.** Le §2 fixe 3 essais par étape, puis alerte. Cette règle était appliquée par l'Orchestrateur seul — or entre deux runs audio, c'est le **notebook** qu'on relance, pas lui : en mode `reel`, rien ne déclenche l'Orchestrateur automatiquement (§12, déclenchement non tranché). Sur `2026-09-11_v01`, le compteur est monté à **8** sans qu'aucune alerte ne parte. `etape_commencer` refuse donc désormais de démarrer au-delà de `MAX_TENTATIVES`, avec `FORCER_RELANCE = True` comme porte de sortie explicite.

**Diagnostic WER gradué.** Un seuil unique donnait les mêmes conseils à 96 % qu'à 9 %. Deux bandes :

| WER | Nature | Ce que dit le notebook |
|---|---|---|
| ≤ `SEUIL_WER` (3 %) | validé | l'étape passe `termine` |
| entre 3 % et `SEUIL_WER_GRAVE` (30 %) | **marginal** | re-synthèse avec une autre graine a de bonnes chances de passer |
| > 30 % | **structurel** | **ne pas relancer à l'identique** — moteur, échantillon de référence ou `ref.txt` en cause |

Les quatre premiers runs de `2026-09-11_v01` étaient à 93-98 % (fuite de référence F5-TTS) et le notebook a répondu quatre fois « re-synthèse avec une autre graine ». Ce conseil suivi quatre fois a coûté 2 h 20.

**Écart assumé avec la v1.1** : le contrôle qualité est **global** et non par phrase, et la régénération est relancée par Franco (`MODE = 'resume_after_fail'`) plutôt qu'automatiquement, 3 fois. C'est plus simple, mais ça a un coût : une seule phrase mal prononcée fait échouer tout le run, et le rapport ne signale plus *quelle* phrase a raté. Or le §4.3 donne « les phrases signalées par le contrôle qualité » comme input de H1 : cet input n'existe plus. À reprendre quand les runs réels diront si le cas est fréquent (§12).

### 7.3 Budget et calibrage des phrases (appliqués par A5)

**Le budget du Short, d'abord.** La durée n'est pas fixée en secondes : c'est le **nombre d'idées** qui est plafonné (`consignes.idees_max`, 3 par défaut), et le coût en mots d'une idée dépend du format (§8). A5 mesure le total avec `metriques.py --idees N` et tranche :

| Verdict | Écart | Action |
|---|---|---|
| `ok` | dans le budget | rien |
| `limite` | ≤ +20 % | se resserre au calibrage — c'est du gras |
| `depasse` | > +20 % | **renvoi à A4** : c'est une idée de trop, ça se règle en réécrivant |

Vérifié sur `2026-09-11_v01` : 258 mots pour un budget de 135, ratio **1,91**, 123 mots de trop, 80,6 s estimées contre 42 s de budget. Le contrôle aurait crié à E3 ; en son absence, le dépassement n'a été vu qu'à E5, l'audio déjà enregistré, et repoussé au CP3.

Le débit de référence est **2,8 mots/seconde**, mesuré sur cette même vidéo : **231 mots réellement prononcés** pour 82,5 s de voix off, pauses comprises. Une première estimation à 3,2 partait du script brut, marqueurs de mise en scène compris (`[intro — stickman face camera]`) — 27 mots jamais dits, soit 14 % d'erreur. `metriques.py` les retire désormais.

Le budget compte **45 mots par idée, tout compris** : l'idée plus sa part de hook, de promesse, d'exemple et de CTA. Ce n'est pas un détail — sur `2026-09-11_v01`, les trois idées ne pèsent que 115 mots sur 231, l'autre moitié étant l'enveloppe narrative. Un budget qui ne compterait que les idées serait faux de moitié. Le corpus le recalibre via `cout_total_par_idee`.



Ce sont des valeurs de départ, à ajuster à partir des rapports audio de la semaine de test.

- **Une phrase = une ligne** dans `03_script_tts.txt`.
- **Longueur cible : 8 à 18 mots.**
  - Au-dessus de 22 mots, la phrase est découpée.
  - En dessous de 4 mots, elle est fusionnée avec la voisine.
  - Les hooks courts sont une exception : ils sont marqués explicitement et surveillés par le contrôle qualité.
- Pas de parenthèses, de symboles ni d'URL.
- Chiffres, unités et versions écrits en toutes lettres.
- Sigles et noms propres techniques passés par le lexique.

### 7.4 Lexique de prononciation

`00_Profil/lexique_prononciation.md`, sous forme de tableau :

| Terme | Forme écrite pour le TTS | Statut |
|---|---|---|
| GPT-5 | GPT five | validé |
| RAG | rag | validé |

**Règle des sigles (révisée le 11/09/2026).** Un sigle courant s'écrit **normalement** (`LLM`, `MCP`, `VS`), pas épelé lettre par lettre (`L L M`). L'épellation a deux défauts : la synthèse la rend souvent moins bien que le sigle brut, et surtout elle casse le contrôle qualité, puisque Whisper retranscrit `LLM` et non `L L M` — le WER compte alors des erreurs qui n'en sont pas. N'entrent au lexique que les termes que la synthèse prononce réellement mal, vérifiés sur un run.

Le lexique s'enrichit de trois façons : les propositions de A5 validées au CP2, les signalements du contrôle qualité audio, et les notes de Franco.

### 7.5 Multi-comptes Colab

Le dossier `/ChaineYouTube/` doit être partagé avec chaque compte Colab, et chaque compte doit y ajouter un **raccourci dans "Mon Drive"** pour que `drive.mount` le trouve au même chemin.

---

## 8. Animation — bibliothèque de composants évolutive

- **Tokens de charte** : tous les composants lisent `charte.json` (couleurs, typos, durées, easing). La cohérence visuelle est donc garantie par le code, pas par la discipline.
- **Registre des composants** : `composants/REGISTRE.md` indique pour chaque composant son nom, ses paramètres, sa version et les vidéos qui l'utilisent.
- **Catalogue visuel** : `composants/apercus/` — une image par composant et par variante de paramètres, générée par `outils/generer_apercus.py` et déclarée dans `composants/apercus.json`. Les aperçus passent par la **composition de rendu réelle**, donc ce qu'on y voit est ce que la vidéo montrera. A6 choisit en regardant ; A7 régénère après avoir créé ou modifié un composant. Sans lui, A6 choisissait une clé (`scene="workflow_fixed_path"`) sans avoir jamais vu ce qu'elle met à l'écran, et le contenu visuel était improvisé au montage.
- **Règle du Monteur** :
  1. réutiliser un composant existant ;
  2. sinon, en étendre un ;
  3. sinon, en créer un nouveau, qui entre au registre avec le statut `nouveau`.

  Un nouveau composant est de fait revu au CP3, puisque Franco le voit dans la vidéo.
- **Évolution** : un composant modifié prend une nouvelle version. Les anciennes vidéos ne sont jamais re-rendues, et H1 peut recommander de refondre un composant.
- **Format** : 1080×1920, 30 fps, sous-titres dynamiques calés sur `04_timestamps.json`.
- **Outil** : **Remotion** (React + TypeScript). Tranché en Session 2.
- **Le code vit dans Git, pas dans Drive** (voir §9.2).

### Direction artistique

Deux niveaux, et aucun des deux n'est décidé au moment de coder :

1. **Les principes récurrents** vivent dans `charte.json > animation`, validés une fois avec la charte : easing par défaut, durée d'entrée, technique par défaut, **règle du wobble** (oscillation légère sur les tracés à la main, jamais sur le texte), un mouvement dominant par scène, hook sobre.
2. **La direction artistique de chaque scène** est décidée par A6 et écrite dans `05_storyboard.json`, champ `da`, avec un vocabulaire fermé :

| Champ | Valeurs | Ce que ça décide |
|---|---|---|
| `mouvement` | `entree_par_le_bas`, `fondu`, `zoom_lent`, `glissement_lateral`, `apparition_sequencee`, `aucun` | comment la scène entre et vit |
| `rythme` | `pose`, `standard`, `punch` | l'énergie de la scène |
| `technique` | `spring`, `interpolate`, `lottie`, `statique` | comment A7 l'implémente |
| `accent` | texte libre court | ce que la scène met en avant |

A7 l'implémente fidèlement et ne la rejuge pas. Le vocabulaire est fermé volontairement : un champ libre redeviendrait de l'improvisation au montage. C'est l'**option (a)** de la revue du 11/09/2026 — enrichir A6 plutôt que créer un agent Art Director, qui aurait ajouté une étape à §6.2 pour une décision qui tient dans un champ.

### Style visé et animation

Le style visé est le **sticker animé** : formes pleines, contours nets, mouvement fluide et naturel — pas le trait filaire procédural des premiers composants.

**Lottie a été envisagé puis écarté** (11/09/2026) : tout est codé en Remotion. Le raisonnement vaut d'être conservé, parce qu'il éclaire le compromis. Un fichier Lottie est **pré-rendu** : on le joue, on le boucle, on le recolore, mais on ne change pas ce qu'il raconte. Il aurait donné la fluidité toute faite sur le personnage et les transitions, au prix d'un blocage dur — un schéma dont le contenu change à chaque vidéo aurait exigé un nouveau fichier fait à la main, faisant de chaque vidéo une dépendance humaine. En restant tout-Remotion, on garde des composants **paramétrables** et une identité propre ; en contrepartie, **la fluidité se code**.

Huit règles séparent une animation vivante d'une animation mécanique. Elles sont implémentées **une fois pour toutes** dans `composants/src/animation.ts` — un composant qui refait ses `interpolate()` à la main retombe dans le geste unique d'origine. Leurs valeurs sont dans `charte.json > animation.naturel`, et elles s'appliquent à **tous** les composants, pas seulement au personnage :

1. **Ressort plutôt que rampe** — `spring()` par défaut ; une rampe linéaire se voit immédiatement.
2. **Rien ne s'arrête net** — une fin brutale est le signe le plus sûr d'une animation bâclée.
3. **Décalage** (80 ms) — ce qui entre ensemble paraît mécanique.
4. **Jamais deux éléments à la même vitesse** (±15 %) — sinon c'est un bloc rigide, pas un groupe d'objets.
5. **Mouvement secondaire** (120 ms de retard) — quelque chose suit l'élément principal.
6. **Anticipation** (10 px) — un léger recul avant les gestes marqués.
7. **Parallaxe** (fond à 0,4) — c'est ce qui fait l'immersion, bien plus que le détail du dessin.
8. **Rien n'est jamais totalement immobile** — une image figée paraît morte.

### Durées de scènes

Les durées du storyboard sont des **estimations** (~2,5 mots/s). Elles sont recalées au montage sur `04_phrases.json`, borne à borne, par `construire_props.py --phrases`. Trois conséquences :

- le recalage **suppose une scène par phrase** ; si A6 fusionne ou coupe des scènes, le compte ne correspond plus, le recalage est abandonné (avec avertissement) et l'estimation est conservée ;
- les scènes se suivent sans trou : une scène va de la fin de la phrase précédente à la fin de la sienne, ce qui absorbe la pause inter-phrases ;
- la composition ne dure **jamais moins que l'audio** : `duree_audio_s` est passé aux props, la dernière scène absorbe le reliquat. Sans ça, une voix off plus longue que la somme des scènes était coupée net.

### Ce que le premier catalogue a corrigé

Avant `animation.ts`, les trois composants faisaient **exactement le même geste** : deux `interpolate()` linéaires — opacité 0→1 et translateY 24→0 — sur 0,3 seconde. Sur une scène de 16 s, cela donnait 0,3 s d'animation et 15,7 s d'image fixe. `spring()` n'était appelé nulle part, aucun composant ne lisait `da`, et `Sequence` juxtaposait les scènes sans transition : onze coupes franches d'affilée.

Ce n'était pas une limite de Remotion mais de ce qui en était utilisé. Un agent optimise ce qu'on peut lui reprocher : le code compilait, les props étaient typées, aucune couleur n'était en dur — tous les critères vérifiables étaient au vert, et personne ne regardait le reste.

### Vérification visuelle

Avant de clore E6, A7 rend quelques images fixes (`remotion still` sur le hook, un milieu, une fin) et les regarde. Rien n'arrive au CP3 sans avoir été vu : corriger sur une image coûte bien moins qu'un rendu complet.

---

## 9. Organisation des fichiers

### 9.1 Drive (données et artefacts)

```
/ChaineYouTube/
├── TABLEAU_DE_BORD.md              # état permanent du process, régénéré à chaque exécution
├── registre_videos.json            # VUE reconstruite depuis les state.json (jamais éditée)
├── 00_Profil/
│   ├── profil_chaine.md
│   ├── conventions.md
│   ├── lexique_prononciation.md
│   ├── chaines_concurrentes.json   # liste pour A2 (veille) et A3 (analyse)
│   ├── charte_visuelle/
│   │   ├── charte.md
│   │   └── charte.json             # design tokens + principes d'animation (§8)
│   └── voix/
│       └── {nom_voix}/v1/          # ref.wav (débruitée), ref.txt, meta.json
├── 01_Orchestrateur/
│   ├── config.json                 # orchestrateur_cmd, cible_tampon, seuils
│   ├── derniere_execution.json
│   ├── verrou.json
│   ├── log_erreurs.md
│   └── calendrier_publication.md
├── 02_Veille_hebdo/
│   ├── {AAAA-Sxx}_analyse_concurrentielle.md
│   ├── {AAAA-Sxx}_sujets_proposes.md
│   └── backlog_sujets.json         # sujets validés en lot (sujet_id, sujet, angle, pilier, semaine, valide_le)
├── 03_Amelioration/
│   ├── rapport_hebdo_{AAAA-Sxx}.md
│   └── analytics/                  # exports YouTube Analytics
├── 04_Architecture_technique/
└── videos/
    └── 2026-09-10_v01/
        ├── state.json
        ├── 01_recherche.md
        ├── 02_script_brut.md
        ├── 03_script_final.md
        ├── 03_script_tts.txt
        ├── 03_rapport_metriques.md
        ├── 04_voixoff.wav
        ├── 04_timestamps.json       # mot par mot, pour les sous-titres
        ├── 04_phrases.json          # bornes par phrase, pour les durées de scènes (§8)
        ├── 04_rapport_audio.md
        ├── 05_cadrage.md            # intention visuelle, discutée avec Franco avant le storyboard
        ├── 05_storyboard.md         # lecture humaine, revu au CP3
        ├── 05_storyboard.json       # lu par le Monteur
        ├── 06_video_finale.mp4
        ├── assets/                  # images d'inspiration déposées par Franco
        └── checkpoints/
            ├── rapport_CP1.md
            ├── rapport_CP2.md
            ├── rapport_CP3.md
            └── refuses/             # rapports archivés après un refus (§5.5)
```

**Convention d'identifiant** : `{date de création}_v{nn}`. La date de publication est suivie dans le registre et dans `state.json`, pas dans le nom du dossier.

### 9.2 Dépôt Git (code)

```
chaine-youtube/
├── orchestrateur/        # machine d'états, lecture/écriture des state.json, tableau de bord
├── agents/               # prompts versionnés de A2 à A7 et H1 (+ scripts d'étape)
├── composants/           # bibliothèque Remotion + REGISTRE.md
├── notebooks/            # notebook voix off (Qwen3-TTS)
├── schemas/              # schéma JSON de state.json
├── outils/               # scripts partagés par plusieurs agents, embarqués par ceux qui les déclarent
├── skills/               # new-short, short-state, short-publier
├── tests/                # suite unittest (orchestrateur, agents, skills)
└── .claude/skills/       # MIROIR GÉNÉRÉ — ne jamais éditer à la main
```

**`.claude/skills/` est entièrement généré** par `agents/_synchroniser_vers_claude_skills.py`, à partir de trois sources : `agents/short-*/`, `skills/*/` et `outils/`. Les outils partagés sont **copiés** sous `<skill>/outils/` chez ceux qui les déclarent (`OUTILS_PAR_SKILL`) plutôt que partagés par un chemin commun : un skill doit rester installable seul (§14), donc il embarque ce dont il a besoin, et la liste explicite montre d'un coup d'œil qui dépend de quoi. On modifie la source, puis on relance le script ; `--verifier` signale la dérive sans rien écrire, et `tests/test_sync_skills.py` fait échouer la suite si le miroir a divergé. Le garde-fou existe parce que la dérive s'est déjà produite en silence : des scripts ajoutés dans `agents/` n'avaient jamais été déployés, et les skills réellement chargés par Claude Code tournaient sans eux.

Les prompts sont versionnés : quand H1 recommande un ajustement validé par Franco, on garde la trace de ce qui a changé et on peut comparer avant et après.

---

## 10. Tableau de bord permanent

Ce fichier est régénéré à chaque exécution de l'Orchestrateur. C'est la première chose que Franco ouvre.

```markdown
# Tableau de bord — mis à jour le 2026-09-12 07:00

## À faire par Franco maintenant
- [CP2] 2026-09-11_v02 — valider le script (+ 2 termes de lexique)
- [AUDIO] 2026-09-11_v01 — lancer le run Colab
- [ALERTE] 2026-09-10_v03 — E3 Filtre TTS : 3 échecs (voir log)

## En production
| Vidéo | Pilier | Étape | Statut | Tentative |
|---|---|---|---|---|

## Tampon
Prêtes : 3 / cible 4 — prochaine publication : 2026-09-12 (2026-09-09_v02)

## Semaine
Publiées : 4 — Abandonnées : 1 — Prochain cycle hebdo : dimanche
```

---

## 11. Publication

**Phase test (semaine 1 minimum)** :
- Franco publie manuellement après le CP3.
- Le système mesure les retouches nécessaires et les défauts signalés.

**Critères pour passer en phase automatisée**. Tous doivent être remplis :
- au moins une semaine de test ;
- **5 vidéos consécutives validées au CP3 sans retouche majeure** (seuil à confirmer) ;
- projet API YouTube autorisé à publier en public (voir la contrainte ci-dessous).

**Phase automatisée** :
- Le **CP3 reste obligatoire**.
- Franco remplit les champs SEO (titre, description, tags) dans le bloc de décision de `rapport_CP3.md`.
- Une fois le CP3 validé, le système uploade la vidéo via l'API YouTube, la programme selon le calendrier et passe le registre à `programmee`, puis à `publiee`.

**Contrainte à vérifier tôt** : à ma connaissance, les vidéos uploadées via l'API par un projet Google Cloud non audité restent bloquées en privé. Il faut demander l'audit de conformité du projet API **dès la phase test** pour ne pas bloquer le passage en automatique. À revérifier dans la documentation actuelle au moment de l'implémentation.

---

## 12. Décisions ouvertes (Session 2)

> Le diagnostic étape par étape en cours ([diagnostic_pipeline.md](diagnostic_pipeline.md)) tient sa propre file d'attente et ses décisions transverses — budget en idées, découverte des formats sur 6 vidéos, corpus de structures, paliers vers l'autonomie. Les deux listes se complètent.


- **À trancher en ouverture de session** :
  - système d'exploitation de la machine qui fera tourner l'Orchestrateur ;
  - chemin local de `/ChaineYouTube` (Google Drive pour ordinateur ou rclone) ;
  - cron ou lancement manuel pour les premiers tests.
- **Multi-chaînes** : **après**, et pas avant la semaine de test. Analyse d'impact faite le 11/09/2026 — le coût est réel mais modéré, et il ne baissera pas en attendant :
  - **la racine est déjà paramétrable** partout (`--root`, `CHAINE_YT_ROOT`, puis les emplacements Drive habituels). C'est le point qui aurait pu coûter cher, et il est déjà réglé. Ce qui reste en dur, c'est le *nom* `ChaineYouTube` dans la détection automatique : une seconde chaîne devra passer `--root` explicitement, ou on remplace la liste de candidats par un fichier de chaînes connues ;
  - **les piliers sont figés à trois endroits** : `new_short.py` (`PILIERS`), `schemas/state_schema.json` (enum `pilier`) et le profil par défaut. C'est le vrai chantier : il faut les sortir dans un `profil_chaine.json` lisible par la machine, et assouplir l'enum du schéma ;
  - **les scripts d'agent trouvent le dépôt par `REPO_ROOT = parents[3]`** (`generer_storyboard.py`, `rendre_video.py`), donc `composants/` est commun à toutes les chaînes. C'est probablement ce qu'on veut — une bibliothèque partagée — mais alors la charte doit rester par chaîne, et `REGISTRE.md` gagner une colonne « chaîne » ;
  - **un argument `--chaine`** pour les skills, qui résout vers la bonne racine ;
  - ordre recommandé : faire tourner une chaîne une semaine, puis sortir les piliers, puis `--chaine`. Préparer le terrain avant d'avoir publié une seule vidéo, c'est généraliser sur un seul exemple.

- **Déclenchement de l'Orchestrateur** : cron local + Claude Code en mode headless, ou lancement manuel. Accès à Drive depuis la machine locale : Google Drive pour ordinateur ou rclone.
- **Outil d'animation** : ~~Manim, Motion Canvas ou Remotion~~ → **tranché : Remotion** (React + spring animations).
- **Notebook voix** : ~~réduction de bruit~~ → **tranché : désactivée par défaut** (`DENOISE = False` dans `voix_off.ipynb`) — la référence de Franco (voix ElevenLabs) est déjà propre, `noisereduce` la dénaturait sans bruit réel à retirer. ~~version exacte et API de Qwen TTS~~ → **tranché : moteur de synthèse basculé sur Qwen3-TTS** (package `qwen-tts`, modèle `Qwen/Qwen3-TTS-12Hz-1.7B-Base`, `generate_voice_clone(text, language, ref_audio, ref_text)`) après que F5-TTS ait montré un défaut structurel (fuite du contenu de la référence dans la sortie, reproduit sur deux échantillons différents). Reste ouvert : durée idéale de l'extrait de référence (3-10s annoncé par Qwen3-TTS, à confirmer sur plusieurs voix).
- **Seuils** : métriques de style de A5, écart toléré par le contrôle qualité audio, cible du tampon.
- **Quota Claude Pro** : partagé entre claude.ai et Claude Code, à mesurer pendant la semaine de test.
- **Transcriptions des concurrents** : méthode de récupération et plan B quand elle casse.
- **Audit API YouTube** : à lancer pendant la phase test.
- **Qualité des animations (A7 Monteur)** : à intégrer dans `agents/short-monteur/` — pas encore fait.
  - ~~**Lottie** pour les composants où une vraie qualité d'animation compte~~ → **écarté le 11/09/2026**. Un fichier pré-rendu ne peut pas illustrer un schéma dont le contenu change d'une vidéo à l'autre : chaque variante serait devenue une dépendance humaine. Tout est codé en Remotion, et la fluidité se code — huit règles en §8. Le style visé reste le **sticker animé**. La contrepartie est assumée : **raffiner les composants existants** devient le chantier, à la place de l'intégration de fichiers.
  - ~~**Boucle de vérification visuelle**~~ → **faite le 11/09/2026** : étape 5 du skill `short-monteur` (`remotion still` sur le hook, un milieu, une fin), documentée en §8.
  - Pistes évoquées, non actées : **Rive** (`@remotion/rive`), **d3-ease** pour des courbes de mouvement plus naturelles, **rough.js** pour un rendu « tracé à la main » si Franco veut cette esthétique, **`@remotion/noise`** pour le wobble (la règle du wobble est posée en charte, son implémentation reste au choix de A7).
- **Contrôle qualité audio par phrase** : le notebook fait un WER **global** ; une seule phrase ratée fait échouer tout le run, et le rapport ne dit pas laquelle. Le §4.3 donne pourtant « les phrases signalées par le contrôle qualité » comme input de H1 : cet input n'existe pas. À reprendre si les runs réels montrent que le cas est fréquent (§7.2).
- **Statut `attente_franco` au niveau global** : `statut_global` ne prend jamais cette valeur, alors que §5.3 la prévoit. En pratique le blocage est visible étape par étape, donc ce n'est pas urgent — mais soit on l'écrit, soit on le retire du §5.3.
- **Seuil de blocage et runs longs** : le tableau de bord signale `[BLOQUE]` une étape `en_cours` depuis plus de `seuil_blocage_heures` (2 h par défaut). Un run Colab long déclencherait une fausse alerte. À ajuster après la semaine de test.

---

## 13. Ordre de construction (par étapes)

Chaque étape est testée avant de passer à la suivante.

1. **Fondations** : structure Drive (dont `config.json` et `backlog_sujets.json`), dépôt Git, schéma `state.json` (repartir de `new-short/assets/state_template.json`), squelette de l'Orchestrateur, tableau de bord, installation de `new-short` et `short-state`. Tests avec des agents factices qui simulent succès, échecs et checkpoints ; `short-state` sert d'outil de vérification.
2. **Session Profil** : `profil_chaine.md`, lexique initial, charte visuelle (A6), validés en lot.
3. **De la recherche au CP2** : A2, A4, A5 et la boucle de révision.
4. **Notebook voix off** : clonage, débruitage, synthèse, contrôle qualité, timestamps.
5. **Montage** : A6 storyboard, A7 Monteur, premiers composants.
6. **Hebdomadaire** : A3 Analyseur et H1 Amélioration continue.
7. **Semaine de test**, puis passage en publication automatisée selon les critères du §11.

---

## 14. Skills livrés

### `new-short` — déclencher une vidéo

Il crée `videos/{id}/state.json` et `checkpoints/`, puis relance l'Orchestrateur si `orchestrateur_cmd` est configuré. Il n'exécute aucun agent et ne choisit jamais un sujet non validé.

| Demande | Source du sujet | CP1 |
|---|---|---|
| « new short » | Plus ancien sujet disponible du backlog | Déjà validé en lot |
| « new short sur X » | Sujet de Franco | Individuel, après la recherche |
| « new short actu » | Veille du Chercheur (voie rapide) | Individuel |

**Consignes structurées.** `--format` (format narratif, **champ libre** : les formats se découvrent au fil des premières vidéos), `--reference` (vidéo dont on reprend le format ou la mise en scène, relayée jusqu'au Designer) et `--idees` (budget du Short, défaut 3). `--note` reste pour le reste. `--titre` donne une étiquette courte ; sans lui elle est dérivée du sujet et bornée à 80 caractères.

Codes de retour du script :
- 0 : vidéo créée ;
- 2 : racine introuvable, ou argument invalide ;
- 3 : backlog vide ;
- 4 : doublon (création seulement avec l'accord de Franco) ;
- 5 : `sujet_id` inconnu.

### `short-state` — état de la production

Il est en lecture seule et recalcule tout à partir des `state.json`. Il a trois modes :
- **vue d'ensemble** : actions triées par priorité (fichier corrompu, alerte, étape bloquée, checkpoint, audio, sujets, Orchestrateur) ;
- **`--video ID`** : frise détaillée d'une vidéo ;
- **`--registre`** : toutes les vidéos conçues et publiées.

Il détecte aussi une décision déjà saisie par Franco mais pas encore transcrite par l'Orchestrateur.

### `short-publier` — fermer le cycle de vie d'une vidéo

Il enregistre une publication faite par Franco (phase test, §11) : date, URL, passage du registre à `publiee` ou `programmee`, clôture de `E7_publication`. Il ne parle pas à l'API YouTube et refuse d'agir si le CP3 n'est pas validé (§2).

Codes de retour : 0 enregistré · 2 racine introuvable · 4 date invalide ou URL manquante · 6 vidéo inconnue · 7 CP3 non validé · 8 déjà enregistrée (relancer avec `--force` pour corriger).

Une vidéo `programmee` garde `E7_publication` en `attente_franco` : elle reste visible au tableau de bord jusqu'à la mise en ligne réelle.

### Emplacement de la racine

Les deux skills trouvent la racine avec `--root`, sinon la variable `CHAINE_YT_ROOT`, sinon les emplacements habituels de Google Drive pour ordinateur. Sans accès local (claude.ai, mobile), ils passent par le connecteur Google Drive : ils recréent une copie locale temporaire des fichiers utiles et lancent le même script dessus.