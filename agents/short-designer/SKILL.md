---
name: short-designer
description: Agent A6 du pipeline chaine YouTube — execute l'etape E5_storyboard d'une video (§4.3, §8), en parallele de l'audio, apres le CP2. Utilise ce skill quand le tableau de bord de l'Orchestrateur indique une ligne "[AGENT] ... designer", ou quand Franco dit "fais le storyboard de <video_id>". Ne pas confondre avec la charte visuelle (session ponctuelle, deja ebauchee dans 00_Profil/charte_visuelle/).
---

# designer (A6) — storyboard d'une video

## Ce que fait cet agent, et ce qu'il ne fait pas

Il decoupe le script final en scenes et decide, pour chacune, **trois
choses** : le composant de la bibliotheque `composants/` (Remotion), ses
parametres, et sa **direction artistique** — comment la scene bouge.

Il ne rend jamais la video (c'est le Monteur, A7) et ne cree pas de
nouveau composant lui-meme : s'il n'y a pas de composant adapte, il le
signale, le Monteur decidera d'en creer un (§8, regle du Monteur).

La direction artistique est de son ressort, pas de celui du Monteur.
Avant, A6 choisissait les composants et A7 improvisait le style au moment
de coder : deux videos d'affilee pouvaient ne pas avoir le meme langage
visuel sans que personne ne l'ait decide. Desormais A6 l'ecrit dans le
storyboard, et A7 l'applique.

## Etape 1 — Verifier que c'est bien son tour

`etapes.E5_storyboard.statut` doit etre `a_venir` ou `echec`, et
`etapes.CP2.statut == "valide"`.

## Etape 2 — Marquer le debut

```bash
python3 <chemin-du-skill>/scripts/etape.py commencer --video <video_id> --etape E5_storyboard [--root R]
```

## Etape 3 — Lire les inputs

- **`state.json` > `consignes`** — a lire en premier, c'est la que Franco
  s'adresse a toi :
  - `note_franco` : consigne de mise en scene. Une **contrainte**, pas une
    suggestion. Si elle decrit un dispositif (ex. « un stickman parle en
    intro, puis s'ecarte et raconte en fond pendant un cutaway »), ton
    decoupage doit le suivre scene par scene ;
  - `reference` : video de reference. Tu t'en inspires pour le **gabarit
    narratif** (ordre, rythme, mise en scene), pas pour copier son contenu ;
  - `format` et `idees_max` : le format vise et le nombre d'idees. Une
    scene par phrase reste la regle, mais le decoupage doit laisser lire
    les `idees_max` idees comme des blocs distincts.

  Avant, rien de tout ca ne t'etait adresse : `note_franco` ne figurait pas
  dans tes inputs, et l'intention de Franco ne t'arrivait que si le
  Chercheur l'avait recopiee dans sa recherche.
- **`composants/lottie/README.md`** — le jeu de base Lottie reutilisable
  (personnage, transitions) et ce que chaque fichier montre. Regarde-le
  avant de demander une animation de personnage : elle existe peut-etre
  deja.
- **`videos/{video_id}/assets/`** — images d'inspiration et fichiers Lottie
  deposes par Franco pour **cette** video. Regarde-les : c'est la reference
  visuelle la plus directe dont tu disposes. Un `.json` Lottie qui s'y
  trouve est une animation prete a l'emploi, a placer dans une scene avec
  `technique: "lottie"`.
- `videos/{video_id}/03_script_final.md` et `03_script_tts.txt` (une
  phrase par ligne : bon decoupage naturel des scenes)
- `00_Profil/charte_visuelle/charte.json` — en particulier le bloc
  `animation` : easing par defaut, regle du wobble, regles de style. Ces
  principes sont **valides une fois avec la charte, pas redecides par
  video** (§8). Ta direction artistique les decline, elle ne les
  contredit pas.
- `charte.md` (intention visuelle)
- `composants/REGISTRE.md` (composants existants, humain) et
  `composants/src/components/registry.ts` (source de verite : les noms
  exacts a utiliser dans `composant`)

## Etape 4 — Generer le squelette, puis le trancher

```bash
python3 <chemin-du-skill>/scripts/generer_storyboard.py --video <video_id> --root <racine> \
  --sortie-md videos/<video_id>/05_storyboard.md \
  --sortie-json videos/<video_id>/05_storyboard.json
```

Ce script pose la structure : une scene par phrase, les ids, les durees
estimees, la DA par defaut de la charte. Il marque chaque scene
`"a_completer": true`.

**Le vrai travail commence ici.** Reprends le `.json` scene par scene et
tranche :

1. **le composant** — nom exact du registre ; reutilise avant de demander
   du neuf (§8) ;
2. **les parametres** du composant. N'y remets jamais la phrase prononcee
   comme texte a l'ecran : les sous-titres la portent deja, l'afficher
   ferait doublon. Le champ `phrase` sert de repere, pas de parametre ;
3. **la direction artistique** (`da`), avec ce vocabulaire ferme :

| Champ | Valeurs | Ce que ca decide |
|---|---|---|
| `mouvement` | `entree_par_le_bas`, `fondu`, `zoom_lent`, `glissement_lateral`, `apparition_sequencee`, `aucun` | comment la scene entre et vit |
| `rythme` | `pose` (on laisse respirer), `standard`, `punch` (accent, coupe seche) | l'energie de la scene |
| `technique` | `spring`, `interpolate`, `lottie`, `statique` | comment A7 l'implemente |

**Quand choisir `lottie`** (charte, bloc `animation.lottie`) : pour ce qui
est **fixe et expressif** — personnage, transition, icone, effet. Un
fichier Lottie est pre-rendu : on le joue, on le boucle, on le recolore,
on ne change pas ce qu'il raconte. Tout ce qui **varie d'une video a
l'autre** — un schema, du texte, des chiffres — reste en Remotion, sinon
chaque nouvelle video exigerait un fichier fait a la main avant de pouvoir
tourner. Les deux se superposent dans une meme scene.
| `accent` | texte libre court, optionnel | ce que la scene doit mettre en avant |

Puis retire `"a_completer"` de la scene. **Aucune scene ne doit rester
`a_completer` a la cloture** : le Monteur s'en sert pour savoir si le
storyboard a vraiment ete travaille, et le signalera au CP3 sinon.

Quelques reperes de bon sens, en plus des regles de la charte : varier le
`mouvement` entre scenes voisines, reserver `punch` aux deux ou trois
moments qui portent le propos, et garder le hook sobre (rien ne bouge
au-dela de l'entree).

**Durees** : celles du squelette sont des estimations (~2.5 mots/s).
Elles sont recalees automatiquement sur l'audio reel au montage, a partir
de `04_phrases.json` (§7.2). Ce recalage **suppose une scene par phrase** :
si tu fusionnes ou coupes des scenes, le compte ne correspond plus, le
recalage est abandonne et le visuel derive de la voix. Ne t'en ecarte que
si c'est vraiment necessaire, et dis-le dans le `.md`.

Ecris **deux fichiers**, toujours coherents entre eux :

`videos/{video_id}/05_storyboard.md` (lecture humaine, revu au CP3) :

```markdown
# Storyboard — {titre de travail}

## s1 — TitleCard (3.2s)

{phrase prononcee, pour situer la scene}

- Mouvement : entree_par_le_bas
- Rythme : punch
- Technique : spring
- Accent : le titre
- Parametres : titre="...", sousTitre="..."

## Nouveaux composants necessaires
- ... (ou "aucun")
```

`videos/{video_id}/05_storyboard.json` (lu par le Monteur) :

```json
{
  "scenes": [
    {"id": "s1", "phrase": "...", "composant": "TitleCard", "duree_s": 3.2,
     "params": {"texte": "...", "sousTitre": "..."},
     "da": {"mouvement": "entree_par_le_bas", "rythme": "punch",
            "technique": "spring", "accent": "le titre"}}
  ],
  "nouveaux_composants_necessaires": [],
  "da_defaut": {"mouvement": "fondu", "rythme": "standard", "technique": "spring"}
}
```

`composant` doit correspondre exactement a une cle de
`composants/src/components/registry.ts` ; si le composant ideal n'existe
pas encore, mets son nom quand meme (le Monteur le creera) et decris-le
dans `nouveaux_composants_necessaires`.

## Etape 5 — Cloturer

Succes :

```bash
python3 <chemin-du-skill>/scripts/etape.py terminer --video <video_id> --etape E5_storyboard \
  --sorties 05_storyboard.md 05_storyboard.json --message "Resume en une phrase"
```

Echec (script final absent, charte introuvable) :

```bash
python3 <chemin-du-skill>/scripts/etape.py echouer --video <video_id> --etape E5_storyboard \
  --message "Raison precise"
```

## Etape 6 — Relancer l'Orchestrateur

Si `orchestrateur_cmd` est renseigne, execute-le. Le montage (E6) attend
aussi que l'audio (E4) soit termine : ne t'inquiete pas si rien ne bouge
tant que Franco n'a pas lance le run Colab.

## Fichiers

- Lus : `videos/{video_id}/state.json` (dont **`consignes`** :
  `note_franco`, `reference`, `format`, `idees_max`), `03_script_final.md`,
  `03_script_tts.txt`, `00_Profil/charte_visuelle/charte.json` (bloc
  `animation` compris) et `charte.md`, `videos/{video_id}/assets/`,
  `composants/lottie/README.md`,
  `composants/REGISTRE.md`,
  `composants/src/components/registry.ts`
- Ecrits : `videos/{video_id}/05_storyboard.md`, `05_storyboard.json`,
  `videos/{video_id}/state.json` (uniquement `etapes.E5_storyboard`)
