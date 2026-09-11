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
- **`composants/apercus/README.md`** — **le catalogue visuel**. Une image
  par composant et par variante, rendue par la composition reelle. C'est ce
  que la video montrera. **Regarde-les avant de choisir** : un nom comme
  `scene="workflow_fixed_path"` ne dit rien de ce qui est a l'ecran, et
  choisir sans voir, c'est laisser le Monteur inventer le visuel au moment
  de coder. Si le catalogue manque ou date, regenere-le :
  `python3 <chemin-du-skill>/outils/generer_apercus.py`
- **`videos/{video_id}/assets/`** — images d'inspiration deposees par Franco
  pour **cette** video. Regarde-les : c'est la reference visuelle la plus
  directe dont tu disposes.
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

## Etape 4 — Cadrer avec Franco, avant d'ecrire quoi que ce soit

**C'est la nouvelle etape centrale de ton travail.** Tu n'ecris pas le
storyboard puis tu attends le CP3 : tu analyses, tu proposes, tu poses tes
questions, Franco ajuste, et seulement apres tu ecris.

### 4.1 — Analyse le contenu

Lis le script en entier avant de penser images. Repere :

- la **structure reelle** (hook, promesse, les `idees_max` idees, l'exemple,
  la cloture) — elle ne suit pas forcement le decoupage en phrases ;
- les **moments qui portent** : la phrase qui fait comprendre, le chiffre, la
  chute. Ce sont eux qui meritent une image forte ;
- les **passages de liaison**, qui ne meritent qu'une image sobre.

### 4.2 — Elabore ce qui est faisable

Regarde le **catalogue visuel** (`composants/apercus/README.md`), puis
classe honnetement :

| Categorie | Ce que ca veut dire |
|---|---|
| Reutilisable tel quel | le composant existe et rend bien ce qu'il faut |
| A etendre | un parametre optionnel retro-compatible suffit |
| A creer | rien ne convient — dis **ce que ca coute** et pourquoi ca vaut le coup |
| Hors de portee | annonce-le, et propose un repli qui tient |

**Tout est code en Remotion** : la fluidite ne vient pas d'un fichier tout
fait, elle se code. Une animation vraiment naturelle sur un element dessine
a la main coute donc du temps a A7 — quand tu en demandes une, dis-le dans
« a quel cout », ce n'est pas gratuit.

### 4.3 — Ecris `05_cadrage.md` et soumets-le a Franco

```markdown
# Cadrage visuel — {video_id}

## Ce que raconte le script
(3 a 5 lignes : la structure reelle et les moments qui portent)

## Ce que je propose de montrer
| Bloc | Ce qu'on voit a l'ecran | Composant | Nouveau ? |
|---|---|---|---|
| Hook | ... | ... | non |

## Ce qui est faisable, et a quel cout
- Reutilisable tel quel : ...
- A etendre : ...
- A creer : ... (cout, et pourquoi ca vaut le coup)
- Hors de portee : ... (et le repli propose)

## Questions pour Franco
1. ...
2. ...

## Ce que je ne ferai pas sans reponse
- ...
```

**Colonne « Ce qu'on voit a l'ecran » : decris l'image, jamais la cle.**
`scene="workflow_fixed_path"` ne veut rien dire pour un humain, et sur
`2026-09-11_v01` une cle de ce genre a laisse 14,4 secondes d'ecran dont
personne n'avait decide le contenu. Ecris plutot : « trois boites reliees
par une fleche rigide, le modele au centre ne peut pas en sortir ». C'est
ca, ton metier.

Presente ensuite ta proposition a Franco et **attends ses ajustements**
avant l'etape 5. S'il n'est pas disponible, ne bloque pas : ecris le
storyboard sur ta proposition, et dis clairement dans ton message de
cloture que le cadrage n'a pas ete valide.

## Etape 5 — Generer le squelette, puis le trancher

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
2. **les parametres** du composant, en respectant trois regles que le
   premier catalogue a rendues evidentes :

   - **Jamais la phrase prononcee a l'ecran.** Les sous-titres la portent
     deja. Sur `2026-09-11_v01`, les trois premieres scenes affichaient mot
     pour mot la phrase dite, par-dessus les sous-titres qui la repetaient :
     quinze secondes de doublon. Le texte a l'ecran est un **mot-cle**, un
     **chiffre** ou un **titre court** — jamais la phrase. Le champ `phrase`
     est un repere pour toi, pas un parametre.
   - **Remplis le cadre.** On est en 1080x1920. Aucun composant actuel ne
     remplit ce format : le personnage fait un cinquieme de la hauteur, le
     reste est noir. Si ta scene laisse les trois quarts de l'ecran vides,
     c'est qu'il manque quelque chose.
   - **Laisse la place aux sous-titres.** Ils occupent le bas du cadre
     (environ 220 px de marge). N'y place rien d'important ;
3. **la direction artistique** (`da`), avec ce vocabulaire ferme :

| Champ | Valeurs | Ce que ca decide |
|---|---|---|
| `mouvement` | `entree_par_le_bas`, `fondu`, `zoom_lent`, `glissement_lateral`, `apparition_sequencee`, `aucun` | comment la scene entre et vit |
| `rythme` | `pose` (on laisse respirer), `standard`, `punch` (accent, coupe seche) | l'energie de la scene |
| `technique` | `spring`, `interpolate`, `statique` | comment A7 l'implemente |

`spring` par defaut : un mouvement reel accelere puis se pose, une rampe
lineaire se voit immediatement. Reserve `interpolate` a ce qui doit rester
discret, et `statique` a ce qui ne doit pas bouger du tout.
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

**Un composant ou une variante qui n'existe pas encore se DECRIT, il ne se
nomme pas.** Donne au minimum :

- ce qu'on voit : les elements, leur nombre, leur disposition dans le cadre ;
- ce qui bouge, et ce qui reste fixe ;
- ce que la scene doit faire comprendre en une seconde.

Exemple de ce qu'il ne faut pas faire — c'est ce qui a ete livre sur
`2026-09-11_v01` : `scene="workflow_fixed_path"`, sans un mot de plus. Le
Monteur a invente le visuel seul, et le resultat est deux rectangles
generiques dans un ecran aux trois quarts vide.

## Etape 6 — Cloturer

Succes :

```bash
python3 <chemin-du-skill>/scripts/etape.py terminer --video <video_id> --etape E5_storyboard \
  --sorties 05_cadrage.md 05_storyboard.md 05_storyboard.json \
  --message "Resume en une phrase, et si le cadrage n'a pas ete valide par Franco, dis-le"
```

Echec (script final absent, charte introuvable) :

```bash
python3 <chemin-du-skill>/scripts/etape.py echouer --video <video_id> --etape E5_storyboard \
  --message "Raison precise"
```

## Etape 7 — Relancer l'Orchestrateur

Si `orchestrateur_cmd` est renseigne, execute-le. Le montage (E6) attend
aussi que l'audio (E4) soit termine : ne t'inquiete pas si rien ne bouge
tant que Franco n'a pas lance le run Colab.

## Fichiers

- Lus : `videos/{video_id}/state.json` (dont **`consignes`** :
  `note_franco`, `reference`, `format`, `idees_max`), `03_script_final.md`,
  `03_script_tts.txt`, `00_Profil/charte_visuelle/charte.json` (bloc
  `animation` compris) et `charte.md`, `videos/{video_id}/assets/`,
  `composants/apercus/README.md`,
  `composants/REGISTRE.md`,
  `composants/src/components/registry.ts`
- Ecrits : `videos/{video_id}/05_cadrage.md`, `05_storyboard.md`,
  `05_storyboard.json`,
  `videos/{video_id}/state.json` (uniquement `etapes.E5_storyboard`)
