---
name: short-filtre-tts
description: Agent A5 du pipeline chaine YouTube — execute l'etape E3_filtre d'une video (§4.3, §7.3), juste avant le CP2. Utilise ce skill quand le tableau de bord de l'Orchestrateur indique une ligne "[AGENT] ... filtre_tts", ou quand Franco dit "lance le filtre TTS sur <video_id>", "prepare le script pour la voix off de <video_id>".
---

# filtre-tts (A5) — calibrage et normalisation avant le CP2

## Ce que fait cet agent, et ce qu'il ne fait pas

Il transforme `02_script_brut.md` en un script pret pour le CP2 et pour la
synthese vocale. Il ne valide jamais le CP2 lui-meme, et ne touche jamais
a `E2_redaction` directement : s'il renvoie le script en revision, c'est
l'Orchestrateur qui remet `E2_redaction` a `a_venir` (§4.2, point 4) a
partir de l'`--action-suivi` que cet agent declare sur sa propre etape.

Quatre taches :
0. **Budget** : le script tient-il dans le nombre d'idees demande ? C'est
   ici qu'on le verifie, pas au montage.
1. **Style** : zombie nouns, triades, longueur des phrases.
2. **Calibrage pour la synthese** (§7.3) : 8 a 18 mots par phrase cible,
   decoupage au-dessus de 22, fusion en dessous de 4 (sauf hooks courts
   explicitement marques), pas de parentheses/symboles/URL, chiffres et
   versions en toutes lettres.
3. **Normalisation phonetique** : appliquer `00_Profil/lexique_prononciation.md`
   (sigles, noms de modeles, versions).

**Regle des sigles (§7.4), a lire avant de proposer une prononciation.** Un
sigle courant s'ecrit **normalement** — `LLM`, `MCP`, `VS Code` — jamais
epele lettre par lettre (`L L M`). L'epellation casse le controle qualite :
Whisper retranscrit `LLM`, donc le WER compte des erreurs qui n'en sont pas.
**N'entre au lexique que ce que la synthese prononce reellement mal, verifie
sur un run** — pas ce qu'on suppose difficile.

Ce n'est pas theorique : au CP2 de `2026-09-11_v01`, A5 a propose `Git Hub`,
`V S Code` et `M C P`, deja appliques au fichier TTS « pour ne pas bloquer la
suite », et Franco a valide tel quel. Mesure apres coup : **3 a 5 points de
WER fabriques** sur un audio par ailleurs propre, assez pour faire echouer
un seuil a 3 %.

## Etape 1 — Verifier que c'est bien son tour

`etapes.E3_filtre.statut` doit etre `a_venir` ou `echec`, et
`etapes.E2_redaction.statut == "termine"`.

## Etape 2 — Marquer le debut

```bash
python3 <chemin-du-skill>/scripts/etape.py commencer --video <video_id> --etape E3_filtre [--root R]
```

## Etape 3 — Mesurer objectivement

```bash
python3 <chemin-du-skill>/scripts/metriques.py --fichier videos/<video_id>/02_script_brut.md \
  --idees <consignes.idees_max>
```

**Passe toujours `--idees`**, lu dans `state.json > consignes.idees_max`
(3 par defaut). Sans lui, le script ne mesure pas le budget — et personne
d'autre ne le mesure avant le montage.

### Le budget, avant tout le reste

La duree d'un Short n'est pas fixee en secondes : c'est le **nombre
d'idees** qui est plafonne, et le cout en mots d'une idee depend du format
(§8). Le script te rend un bloc `budget` :

| `verdict` | Ce que tu fais |
|---|---|
| `ok` | rien, passe a la suite |
| `limite` (≤ +20 %) | resserre au calibrage : c'est du gras, pas une idee de trop |
| `depasse` (> +20 %) | **renvoie a A4** avec `--action-suivi revision_redaction` |

Un depassement franc ne se rattrape pas en coupant des mots : c'est une
idee de trop, et ca se regle en reecrivant. Dis a A4 **combien de mots
enlever** et **quelle idee semble en trop**, pas seulement que c'est long.

Si le format demande visiblement plus de mots par idee qu'un autre — une
interview fictive doit incarner et relancer — signale-le a Franco au CP2
plutot que de mutiler le script : c'est le cout du format qui est mal
calibre, pas le script qui est mauvais. Tu peux alors remesurer avec
`--mots-par-idee` pour montrer ce que ca donnerait.

Le contre-exemple est dans le depot : sur `2026-09-11_v01`, le script
faisait **258 mots** — 92,1 s de voix off estimees — et personne ne l'a
mesure. Le
depassement n'a ete vu qu'a E5, quand tout etait deja ecrit et enregistre.

Ce script ne fait que compter ; le jugement sur le style et les zombie nouns
reste le tien. Lis aussi `00_Profil/conventions.md` et
`00_Profil/lexique_prononciation.md`.

Il ignore les titres du gabarit (`## Hook`, `## Corps`...) : ils ne sont
jamais prononces. Pour chaque phrase il donne :

| Champ | Sens |
|---|---|
| `mots` | nombre de mots reellement prononces |
| `section` | titre d'ou vient la phrase (`Hook`, `Corps`...) |
| `hors_cible` | hors de la bande cible 8-18 mots (§7.3) — a surveiller, pas une action imposee |
| `trop_longue` | plus de 22 mots : **a decouper** |
| `trop_courte` | moins de 4 mots : **a fusionner**, sauf hook court |
| `triade_probable`, `contient_parenthese_ou_url` | a corriger |

**Exception des hooks courts (§7.3)** : une phrase `trop_courte` dont la
`section` est le Hook n'est pas a fusionner d'office — c'est un choix
d'ecriture. Marque-la explicitement dans `03_rapport_metriques.md` pour que
le controle qualite audio la surveille.

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
- `videos/{video_id}/03_rapport_metriques.md` — il commence par une section
  **`## Budget`**, avant tout le reste :

```markdown
## Budget

| Mesure | Valeur |
|---|---|
| Mots prononces | 258 |
| Budget ({idees_max} idees x {mots_par_idee}) | 135 |
| Ratio | 1.91 |
| Duree estimee / budget | 92.1 s / 48.2 s |
| Verdict | **depasse** |

{Une phrase : ce que tu as fait, ou ce que tu demandes a Franco.}
```

  Cette section est **obligatoire, meme quand le verdict est `ok`** : c'est
  la seule ligne du rapport de CP2 qui parle de longueur. Sans elle, un
  verdict `limite` que tu resserres seul, et surtout le signal « ce format
  coute plus de mots par idee » de l'etape 3, n'atteignent jamais Franco —
  c'est ce qui s'est passe sur `2026-09-11_v01`, ou le CP2 a ete valide
  sans qu'une ligne ne mentionne un depassement de 91 %.

  Puis les **nouveaux termes** du lexique rencontres, avec une proposition
  de prononciation a valider au CP2.

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

- Lus : `videos/{video_id}/state.json` (dont `consignes.idees_max` et
  `consignes.format`), `02_script_brut.md`,
  `00_Profil/conventions.md`, `00_Profil/lexique_prononciation.md`
- Ecrits : `videos/{video_id}/03_script_final.md`, `03_script_tts.txt`,
  `03_rapport_metriques.md`, `videos/{video_id}/state.json` (uniquement
  `etapes.E3_filtre`)
