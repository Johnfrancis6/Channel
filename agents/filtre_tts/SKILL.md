---
name: filtre-tts
description: Agent A5 du pipeline chaine YouTube — execute l'etape E3_filtre d'une video (§4.3, §7.3), juste avant le CP2. Utilise ce skill quand le tableau de bord de l'Orchestrateur indique une ligne "[AGENT] ... filtre_tts", ou quand Franco dit "lance le filtre TTS sur <video_id>", "prepare le script pour la voix off de <video_id>".
---

# filtre-tts (A5) — calibrage et normalisation avant le CP2

## Ce que fait cet agent, et ce qu'il ne fait pas

Il transforme `02_script_brut.md` en un script pret pour le CP2 et pour la
synthese vocale. Il ne valide jamais le CP2 lui-meme, et ne touche jamais
a `E2_redaction` directement : s'il renvoie le script en revision, c'est
l'Orchestrateur qui remet `E2_redaction` a `a_venir` (§4.2, point 4) a
partir de l'`--action-suivi` que cet agent declare sur sa propre etape.

Trois taches (§4.3, A5) :
1. **Style** : zombie nouns, triades, longueur des phrases.
2. **Calibrage pour la synthese** (§7.3) : 8 a 18 mots par phrase cible,
   decoupage au-dessus de 22, fusion en dessous de 4 (sauf hooks courts
   explicitement marques), pas de parentheses/symboles/URL, chiffres et
   versions en toutes lettres.
3. **Normalisation phonetique** : appliquer `00_Profil/lexique_prononciation.md`
   (sigles, noms de modeles, versions).

## Etape 1 — Verifier que c'est bien son tour

`etapes.E3_filtre.statut` doit etre `a_venir` ou `echec`, et
`etapes.E2_redaction.statut == "termine"`.

## Etape 2 — Marquer le debut

```bash
python3 <chemin-du-skill>/scripts/etape.py commencer --video <video_id> --etape E3_filtre [--root R]
```

## Etape 3 — Mesurer objectivement

```bash
python3 <chemin-du-skill>/scripts/metriques.py --fichier videos/<video_id>/02_script_brut.md
```

Ce script ne fait que compter (longueur, virgules, triades probables,
parentheses/URL) ; le jugement sur le style et les zombie nouns reste le
tien. Lis aussi `00_Profil/conventions.md` et `00_Profil/lexique_prononciation.md`.

## Etape 4 — Decider : corriger ou renvoyer en revision

- **Corrections mineures** (calibrage, lexique, quelques triades) : tu les
  fais toi-meme, pas besoin de renvoyer a la redaction.
- **Probleme de fond** (ton hors charte, structure a revoir, trop de
  phrases hors seuils pour un simple ajustement) : c'est une revision.
  La boucle redaction/filtre est plafonnee a 3 tours (§4.3) ; l'Orchestrateur
  compte les tours et alerte Franco au 3e, tu n'as pas a le faire toi-meme.

## Etape 5 — Produire les sorties (si pas de revision)

- `videos/{video_id}/03_script_final.md` — version lisible, validee au CP2
- `videos/{video_id}/03_script_tts.txt` — une phrase par ligne, lexique
  applique, sans changement de sens par rapport au script final
- `videos/{video_id}/03_rapport_metriques.md` — metriques + **nouveaux
  termes** du lexique rencontres, avec une proposition de prononciation a
  valider au CP2

## Etape 6 — Cloturer

Succes :

```bash
python3 <chemin-du-skill>/scripts/etape.py terminer --video <video_id> --etape E3_filtre \
  --sorties 03_script_final.md 03_script_tts.txt 03_rapport_metriques.md \
  --message "Resume en une phrase"
```

Revision (retour a la redaction) :

```bash
python3 <chemin-du-skill>/scripts/etape.py echouer --video <video_id> --etape E3_filtre \
  --message "Ce qui doit etre corrige, precisement, pour le redacteur" \
  --action-suivi revision_redaction
```

Echec procedural (ex. `02_script_brut.md` illisible) : meme commande sans
`--action-suivi`.

## Etape 7 — Relancer l'Orchestrateur

Si `orchestrateur_cmd` est renseigne, execute-le pour ouvrir le CP2 (ou
relancer la boucle vers la redaction).

## Fichiers

- Lus : `videos/{video_id}/state.json`, `02_script_brut.md`,
  `00_Profil/conventions.md`, `00_Profil/lexique_prononciation.md`
- Ecrits : `videos/{video_id}/03_script_final.md`, `03_script_tts.txt`,
  `03_rapport_metriques.md`, `videos/{video_id}/state.json` (uniquement
  `etapes.E3_filtre`)
