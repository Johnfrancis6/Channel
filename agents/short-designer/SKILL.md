---
name: short-designer
description: Agent A6 du pipeline chaine YouTube — execute l'etape E5_storyboard d'une video (§4.3, §8), en parallele de l'audio, apres le CP2. Utilise ce skill quand le tableau de bord de l'Orchestrateur indique une ligne "[AGENT] ... designer", ou quand Franco dit "fais le storyboard de <video_id>". Ne pas confondre avec la charte visuelle (session ponctuelle, deja ebauchee dans 00_Profil/charte_visuelle/).
---

# designer (A6) — storyboard d'une video

## Ce que fait cet agent, et ce qu'il ne fait pas

Il decoupe le script final en scenes et choisit, pour chacune, un
composant de la bibliotheque `composants/` (Remotion) et ses parametres.
Il ne rend jamais la video (c'est le Monteur, A7) et ne cree pas de
nouveau composant lui-meme : s'il n'y a pas de composant adapte, il le
signale, le Monteur decidera d'en creer un (§8, regle du Monteur).

## Etape 1 — Verifier que c'est bien son tour

`etapes.E5_storyboard.statut` doit etre `a_venir` ou `echec`, et
`etapes.CP2.statut == "valide"`.

## Etape 2 — Marquer le debut

```bash
python3 <chemin-du-skill>/scripts/etape.py commencer --video <video_id> --etape E5_storyboard [--root R]
```

## Etape 3 — Lire les inputs

- `videos/{video_id}/03_script_final.md` et `03_script_tts.txt` (une
  phrase par ligne : bon decoupage naturel des scenes)
- `00_Profil/charte_visuelle/charte.json` (tokens : couleurs, typographie,
  rythme) et `charte.md` (intention visuelle)
- `composants/REGISTRE.md` (composants existants, humain) et
  `composants/src/components/registry.ts` (source de verite : les noms
  exacts a utiliser dans `composant`)

## Etape 4 — Decouper en scenes

Pour chaque scene, decide : le composant (par son nom exact du registre),
ses parametres, une duree indicative en secondes (base-toi sur le nombre
de mots de la phrase / ~2.5 mots par seconde ; le Monteur recalera les
durees exactes sur `04_timestamps.json` une fois l'audio disponible).

Ecris **deux fichiers**, toujours coherents entre eux :

`videos/{video_id}/05_storyboard.md` (lecture humaine, revu au CP3) :

```markdown
# Storyboard — {titre de travail}

## Scene s1 — {phrase ou beat concerne}
- Composant : TitleCard
- Parametres : texte="...", sousTitre="..."
- Duree indicative : 3s

## Nouveaux composants necessaires
- ... (ou "aucun")
```

`videos/{video_id}/05_storyboard.json` (lu par le Monteur) :

```json
{
  "scenes": [
    {"id": "s1", "composant": "TitleCard", "duree_s": 3, "params": {"texte": "...", "sousTitre": "..."}}
  ],
  "nouveaux_composants_necessaires": []
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

- Lus : `videos/{video_id}/state.json`, `03_script_final.md`,
  `03_script_tts.txt`, `00_Profil/charte_visuelle/charte.json` (et
  `charte.md`), `composants/REGISTRE.md`,
  `composants/src/components/registry.ts`
- Ecrits : `videos/{video_id}/05_storyboard.md`, `05_storyboard.json`,
  `videos/{video_id}/state.json` (uniquement `etapes.E5_storyboard`)
