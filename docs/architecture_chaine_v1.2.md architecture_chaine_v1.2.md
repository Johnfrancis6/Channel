# Document d'Architecture — Chaîne YouTube Semi-Automatisée — v1.2

*Révision du 10/09/2026 : v1.1 (revue d'architecture) + v1.2 (skills `new-short` et `short-state`). Ce document est la référence unique pour la mise en place de l'écosystème.*

---

## 0. Changements

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
- Chaque semaine, il produit `sujets_proposes_{AAAA-Sxx}.md` pour la voie tampon (piliers intemporels), soumis au CP1 groupé.
- Chaque jour, il fait une veille actu IA. Si un sujet mérite la voie rapide, il le propose au CP1 individuel.
- Pour chaque vidéo validée, il produit `01_recherche.md` : sources, faits vérifiés, angle "ingénieur ML".
- Ses inputs sont la liste de chaînes et mots-clés fournie par Franco et `profil_chaine.md`.

**A3 — Analyseur de chaînes (hebdo)**
- Il récupère les statistiques des concurrents via l'API YouTube Data, qui est la voie stable.
- Il analyse les transcriptions quand elles sont disponibles (hooks, CTA, structure). C'est la partie fragile : un échec de transcription ne bloque pas l'analyse des statistiques.
- Il produit `02_Veille_hebdo/{AAAA-Sxx}_analyse_concurrentielle.md`, lu par A2 et A4.

**A4 — Rédacteur de script**
- Inputs : recherche, dernière analyse concurrentielle, profil de chaîne, commentaire de CP1.
- Il rédige le script (hook, promesse spectateur, marqueurs de voix, style oral) en incarnant l'angle "ingénieur ML". Son prompt est à calibrer finement.
- Il reçoit le retour de A5 et révise son script. La boucle A4 ↔ A5 compte au maximum 3 tours.

**A5 — Filtre TTS**
Il intervient avant le CP2 et fait trois choses :
1. **Style** : il mesure les zombie nouns, les triades et la longueur des phrases (seuils à calibrer). En cas d'échec, il renvoie le script à A4 avec un retour précis.
2. **Calibrage des phrases pour la synthèse** : il applique les règles du §7.3 (phrases ni trop longues, ni trop courtes).
3. **Normalisation phonétique** : il applique le lexique (sigles, noms de modèles, numéros de version, chiffres en toutes lettres).

Il produit :
- `03_script_final.md` : la version lisible, celle que Franco valide au CP2 ;
- `03_script_tts.txt` : une phrase par ligne, lexique appliqué, dérivée mécaniquement du script final sans changement de sens ;
- `03_rapport_metriques.md` : les métriques et les **nouveaux termes inconnus**, avec une proposition de prononciation à valider au CP2.

**A6 — Designer**
- **Charte visuelle** (ponctuelle, validée en lot) : palette, typographie des sous-titres, rythme des transitions, frame d'accroche, style d'illustration. Elle est livrée en deux formats : `charte.md` pour l'humain et `charte.json` pour le code (design tokens).
- **Storyboard** (par vidéo, après le CP2, en parallèle de l'audio) :
  - découpage du script en scènes ;
  - pour chaque scène, le composant de la bibliothèque à utiliser et ses paramètres ;
  - la liste des **nouveaux composants nécessaires** s'il en manque.

**A7 — Monteur vidéo**
- Inputs : storyboard, `04_voixoff.wav`, `04_timestamps.json`, charte.
- Il réutilise d'abord les composants existants. Sinon, il en crée de nouveaux avec Claude Code et les ajoute à la bibliothèque (§8).
- Il cale les scènes et les sous-titres sur les timestamps mot par mot, puis rend `06_video_finale.mp4` avec l'audio déjà synchronisé.

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

```json
{
  "video_id": "2026-09-10_v01",
  "titre_travail": "What the new model actually changes",
  "pilier": "actu_ia",
  "voie": "rapide",
  "statut_global": "en_production",
  "etape_actuelle": "CP2",
  "etapes": {
    "E1_recherche": { "agent": "chercheur", "statut": "termine", "tentatives": 1,
                      "debut": "2026-09-10T07:00Z", "fin": "2026-09-10T07:06Z",
                      "sorties": ["01_recherche.md"] },
    "CP1":          { "statut": "valide", "commentaire": "Angle OK, insister sur le test", "date": "2026-09-10T08:15Z" },
    "E2_redaction": { "agent": "redacteur", "statut": "termine", "tentatives": 2, "sorties": ["02_script_brut.md"] },
    "E3_filtre":    { "agent": "filtre_tts", "statut": "termine", "tentatives": 2,
                      "sorties": ["03_script_final.md", "03_script_tts.txt", "03_rapport_metriques.md"] },
    "CP2":          { "statut": "attente_validation", "commentaire": null, "date": null },
    "E4_audio":     { "statut": "a_venir" },
    "E5_storyboard":{ "statut": "a_venir" },
    "E6_montage":   { "statut": "a_venir" },
    "CP3":          { "statut": "a_venir" },
    "E7_publication":{ "statut": "a_venir" }
  },
  "publication": { "date_prevue": null, "date_effective": null, "url": null },
  "historique": [
    { "horodatage": "2026-09-10T09:02Z", "agent": "filtre_tts", "evenement": "echec",
      "message": "Tentative 1 : 3 phrases > 22 mots, 2 triades" },
    { "horodatage": "2026-09-10T09:10Z", "agent": "filtre_tts", "evenement": "termine", "message": "Tentative 2 OK" }
  ]
}
```

### 5.5 Protocole de validation

Pour que Franco n'ait pas à modifier du JSON à la main, notamment depuis son téléphone, chaque checkpoint génère `checkpoints/rapport_CPx.md`. Ce fichier contient le résumé à valider, suivi d'un bloc de décision :

```markdown
## DÉCISION
Statut : EN_ATTENTE        <!-- remplacer par VALIDE ou REFUSE -->
Commentaire :
```

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

| Cellule | Rôle |
|---|---|
| 0. Config | `video_id`, modèle (`f5tts` / `qwen_tts`), nom de la voix, graine fixe |
| 1. Drive | Montage de Drive, vérification que le dossier de la vidéo existe |
| 2. Voix | **Upload toujours présent.** Premier usage ou nouvel upload : réduction de bruit, découpe d'un extrait de référence court et propre, transcription de la référence (nécessaire à F5-TTS), sauvegarde versionnée dans `00_Profil/voix/{nom}/vN/`. Sessions suivantes : chargement de la voix stockée par défaut |
| 3. Script | Lecture de `03_script_tts.txt` (une phrase par ligne) |
| 4. Synthèse | Génération phrase par phrase |
| 5. Contrôle qualité | Transcription de chaque phrase générée (Whisper), comparaison avec le texte attendu. Si l'écart dépasse le seuil, régénération (3 tentatives max), puis signalement dans le rapport |
| 6. Assemblage | Concaténation avec pauses calibrées, normalisation du volume |
| 7. Timestamps | faster-whisper avec `word_timestamps=True` sur l'audio final → `04_timestamps.json` |
| 8. Sorties | `04_voixoff.wav`, `04_timestamps.json`, `04_rapport_audio.md`, mise à jour de `state.json` |

Le contrôle qualité de la cellule 5 détecte automatiquement les défauts de prononciation. Ses signalements alimentent le lexique et le calibrage des phrases.

### 7.3 Calibrage des phrases (appliqué par A5)

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
| LLM | L L M | validé |
| GPT-5 | G P T five | validé |
| vLLM | v L L M | validé |
| RAG | rag | validé |

Le lexique s'enrichit de trois façons : les propositions de A5 validées au CP2, les signalements du contrôle qualité audio, et les notes de Franco.

### 7.5 Multi-comptes Colab

Le dossier `/ChaineYouTube/` doit être partagé avec chaque compte Colab, et chaque compte doit y ajouter un **raccourci dans "Mon Drive"** pour que `drive.mount` le trouve au même chemin.

---

## 8. Animation — bibliothèque de composants évolutive

- **Tokens de charte** : tous les composants lisent `charte.json` (couleurs, typos, durées, easing). La cohérence visuelle est donc garantie par le code, pas par la discipline.
- **Registre des composants** : `composants/REGISTRE.md` indique pour chaque composant son nom, ses paramètres, un aperçu, sa version et les vidéos qui l'utilisent.
- **Règle du Monteur** :
  1. réutiliser un composant existant ;
  2. sinon, en étendre un ;
  3. sinon, en créer un nouveau, qui entre au registre avec le statut `nouveau`.

  Un nouveau composant est de fait revu au CP3, puisque Franco le voit dans la vidéo.
- **Évolution** : un composant modifié prend une nouvelle version. Les anciennes vidéos ne sont jamais re-rendues, et H1 peut recommander de refondre un composant.
- **Format** : 1080×1920, 30 fps, sous-titres dynamiques calés sur `04_timestamps.json`.
- **Outil** : à trancher en Session 2 (Manim, Motion Canvas, ou Remotion, qui correspond à ton profil React/TypeScript et à la logique de composants).
- **Le code vit dans Git, pas dans Drive** (voir §9.2).

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
│   ├── charte_visuelle/
│   │   ├── charte.md
│   │   └── charte.json             # design tokens lus par les composants
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
        ├── 04_timestamps.json
        ├── 04_rapport_audio.md
        ├── 05_storyboard.md
        ├── 06_video_finale.mp4
        └── checkpoints/
            ├── rapport_CP1.md
            ├── rapport_CP2.md
            └── rapport_CP3.md
```

**Convention d'identifiant** : `{date de création}_v{nn}`. La date de publication est suivie dans le registre et dans `state.json`, pas dans le nom du dossier.

### 9.2 Dépôt Git (code)

```
chaine-youtube/
├── orchestrateur/        # machine d'états, lecture/écriture des state.json, tableau de bord
├── agents/               # prompts versionnés de A2 à A7 et H1
├── composants/           # bibliothèque d'animation + REGISTRE.md
├── notebooks/            # notebook voix off (F5-TTS / Qwen TTS)
├── schemas/              # schéma JSON de state.json
└── skills/               # new-short, short-state (source des fichiers .skill)
```

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

- **À trancher en ouverture de session** :
  - système d'exploitation de la machine qui fera tourner l'Orchestrateur ;
  - chemin local de `/ChaineYouTube` (Google Drive pour ordinateur ou rclone) ;
  - cron ou lancement manuel pour les premiers tests.
- **Multi-chaînes** : faut-il le faire avant ou après l'Orchestrateur ? Si oui :
  - un dossier racine par chaîne ;
  - un `profil_chaine.json` lisible par la machine (piliers, langue, format, voie rapide activée ou non) ;
  - les piliers sortis de `new_short.py` ;
  - un argument `--chaine` pour les skills.

- **Déclenchement de l'Orchestrateur** : cron local + Claude Code en mode headless, ou lancement manuel. Accès à Drive depuis la machine locale : Google Drive pour ordinateur ou rclone.
- **Outil d'animation** : ~~Manim, Motion Canvas ou Remotion~~ → **tranché : Remotion** (React + spring animations).
- **Notebook voix** : ~~réduction de bruit~~ → **tranché : désactivée par défaut** (`DENOISE = False` dans `voix_off.ipynb`) — la référence de Franco (voix ElevenLabs) est déjà propre, `noisereduce` la dénaturait sans bruit réel à retirer. ~~version exacte et API de Qwen TTS~~ → **tranché : moteur de synthèse basculé sur Qwen3-TTS** (package `qwen-tts`, modèle `Qwen/Qwen3-TTS-12Hz-1.7B-Base`, `generate_voice_clone(text, language, ref_audio, ref_text)`) après que F5-TTS ait montré un défaut structurel (fuite du contenu de la référence dans la sortie, reproduit sur deux échantillons différents). Reste ouvert : durée idéale de l'extrait de référence (3-10s annoncé par Qwen3-TTS, à confirmer sur plusieurs voix).
- **Seuils** : métriques de style de A5, écart toléré par le contrôle qualité audio, cible du tampon.
- **Quota Claude Pro** : partagé entre claude.ai et Claude Code, à mesurer pendant la semaine de test.
- **Transcriptions des concurrents** : méthode de récupération et plan B quand elle casse.
- **Audit API YouTube** : à lancer pendant la phase test.
- **Qualité des animations (A7 Monteur)** : à intégrer dans `agents/short-monteur/` — pas encore fait.
  - **Lottie** (`@remotion/lottie`) pour les composants où une vraie qualité d'animation compte (ex. le stickman) : Claude Code intègre un fichier Lottie fourni par Franco (export After Effects, ou pioché sur LottieFiles) plutôt que de dessiner l'animation en SVG procédural à la main.
  - **Boucle de vérification visuelle** : avant de clore E6_montage, l'agent rend quelques frames clés (`npx remotion render` sur une image) et les regarde, pour itérer sur le visuel plutôt que de livrer un rendu jamais vu directement au CP3.

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

Codes de retour du script :
- 0 : vidéo créée ;
- 2 : racine introuvable ;
- 3 : backlog vide ;
- 4 : doublon (création seulement avec l'accord de Franco) ;
- 5 : `sujet_id` inconnu.

### `short-state` — état de la production

Il est en lecture seule et recalcule tout à partir des `state.json`. Il a trois modes :
- **vue d'ensemble** : actions triées par priorité (fichier corrompu, alerte, étape bloquée, checkpoint, audio, sujets, Orchestrateur) ;
- **`--video ID`** : frise détaillée d'une vidéo ;
- **`--registre`** : toutes les vidéos conçues et publiées.

Il détecte aussi une décision déjà saisie par Franco mais pas encore transcrite par l'Orchestrateur.

### Emplacement de la racine

Les deux skills trouvent la racine avec `--root`, sinon la variable `CHAINE_YT_ROOT`, sinon les emplacements habituels de Google Drive pour ordinateur. Sans accès local (claude.ai, mobile), ils passent par le connecteur Google Drive : ils recréent une copie locale temporaire des fichiers utiles et lancent le même script dessus.