# SESSION 6 — E6 Montage (A7 Monteur + Remotion)

## Contexte

Repo : https://github.com/Johnfrancis6/Channel.git
Branche : youtube-pipeline-session-2-0nnh6m
Tests actuels : 28 passent ✓

## Ce qui existe déjà — ne pas retoucher

- `agents/short-monteur/SKILL.md` — prompt A7 complet
- `agents/short-monteur/scripts/construire_props.py` — assemble props Remotion ✓
- `agents/short-monteur/scripts/etape.py` — script state.json générique ✓
- `orchestrateur/agents_factices/monteur.py` — agent factice ✓
- `tests/test_construire_props.py` — tests construire_props ✓
- `tests/test_render_remotion.py` — test rendu (skip si node_modules absent) ✓
- `composants/src/Video.tsx` — composition Remotion principale ✓
- `composants/src/Root.tsx` — point d'entrée Remotion ✓
- `composants/src/components/registry.ts` — registre composants ✓
- `composants/src/components/TitleCard.tsx` — seul composant ✓
- `composants/src/components/Subtitles.tsx` — sous-titres auto ✓
- `orchestrateur/engine.py` — DEPENDANCES correctes : E6 dépend E4 + E5 ✓

## Règle composants (§8)

A7 crée les composants à la demande, vidéo par vidéo. Cette session ne crée
pas de nouveaux composants. La logique de création sera exercée en situation
réelle sur la première vraie vidéo.

---

## STEP 1 — Script `rendre_video.py`

Créer `agents/short-monteur/scripts/rendre_video.py`.

Ce script orchestre le rendu complet E6 : props → remotion render → MP4.
Il est appelé par A7 (Claude Code) pendant E6, après `construire_props.py`.

### Usage

```bash
python3 rendre_video.py \
  --video VIDEO_ID \
  --root /chemin/ChaineYouTube \
  --props /tmp/VIDEO_ID_props.json \
  --sortie videos/VIDEO_ID/06_video_finale.mp4
```

### Arguments optionnels

- `--browser CHEMIN` : passer REMOTION_BROWSER_EXECUTABLE si Chromium non téléchargeable
- `--dry-run` : vérifier les prérequis sans lancer le rendu (exit 0 si tout OK)

### Logique interne

1. Vérifier prérequis :
   - `composants/node_modules/` existe → sinon exit 4, message clair "npm install requis"
   - `--props` existe et est un JSON valide → sinon exit 2
   - `composants/src/components/registry.ts` accessible → sinon exit 5
2. Si `--dry-run` : afficher résumé prérequis et exit 0
3. Construire la commande remotion render :
   ```
   npx remotion render src/index.ts Video <sortie> --props=<props>
   ```
   Ajouter `REMOTION_BROWSER_EXECUTABLE` à l'env si `--browser` fourni
4. Lancer subprocess depuis le dossier `composants/`
5. Streamer stdout/stderr de remotion en temps réel (ne pas bufferiser)
6. Si returncode != 0 → exit 6, JSON `{"ok": false, "message": "Remotion render failed", "code": returncode}`
7. Vérifier que le fichier MP4 de sortie existe et fait > 0 octets
8. Stdout : JSON `{"ok": true, "sortie": "...", "taille_bytes": N}`

### Gestion erreurs

- `node_modules` absent → exit 4 + message "Lance 'npm install' dans composants/"
- Props JSON invalide → exit 2
- Remotion échec → exit 6 + stderr de remotion dans le message
- MP4 absent après rendu → exit 7

---

## STEP 2 — Tests `test_monteur.py`

Créer `tests/test_monteur.py`.

### Tests à écrire

**TestRendreVideo** (teste `rendre_video.py` en mode `--dry-run`) :

1. `test_dry_run_ok_si_node_modules_present`
   - Créer un dossier `composants/node_modules/` factice
   - Props JSON valide en temp
   - `--dry-run` → exit 0

2. `test_dry_run_exit4_si_node_modules_absent`
   - Pas de `node_modules/`
   - `--dry-run` → exit 4

3. `test_exit2_si_props_json_invalide`
   - Fichier props non-JSON
   - exit 2

4. `test_exit2_si_props_absent`
   - Chemin props inexistant
   - exit 2

**TestE6DansOrchestateur** (intégration) :

5. `test_e6_declenche_apres_e4_et_e5`
   - Pipeline complet jusqu'à CP2 validé
   - Simuler E4_audio = "termine" (écrire dans state.json directement)
   - Simuler E5_storyboard = "termine"
   - `run_once` → vérifier E6_montage passe en `en_cours` puis `termine`
   - Vérifier que `06_video_finale.mp4` est dans les sorties state

6. `test_e6_bloque_si_e4_attente_franco`
   - E5 terminé, E4 = "attente_franco"
   - `run_once` → E6 reste `a_venir`

7. `test_e6_bloque_si_e5_absent`
   - E4 terminé, E5 = "a_venir"
   - `run_once` → E6 reste `a_venir`

8. `test_cp3_declenche_apres_e6`
   - E6 terminé → `run_once` → CP3 = "attente_validation"
   - Vérifier que `rapport_CP3.md` est généré et contient le storyboard

---

## STEP 3 — Mettre à jour `agents_factices/monteur.py`

L'agent factice actuel retourne `06_video_finale.mp4` dans les sorties mais
ne crée pas le fichier sur disque. Les tests E6→CP3 ont besoin que le fichier
existe physiquement (l'orchestrateur lit les sorties pour CP3).

Modifier `orchestrateur/agents_factices/monteur.py` :
- Créer `06_video_finale.mp4` (fichier vide ou 1 octet) dans `video_dir`
- Créer aussi `05_storyboard.md` factice si absent (requis pour le résumé CP3)
- Garder le même contrat de retour

---

## STEP 4 — Vérifier `RESUME_SOURCES` pour CP3

Dans `orchestrateur/engine.py`, `RESUME_SOURCES` définit ce que l'orchestrateur
met dans le rapport CP3. Vérifier que CP3 inclut `06_video_finale.mp4` dans
son résumé (ou au minimum `05_storyboard.md`).

Si `CP3` n'est pas dans `RESUME_SOURCES`, ajouter :
```python
"CP3": [("05_storyboard.md", "Storyboard"), ("04_rapport_audio.md", "Rapport audio")],
```

Ne modifier `engine.py` que si CP3 est absent de RESUME_SOURCES. Si déjà présent,
ne rien changer.

---

## STEP 5 — Commit

```
git add agents/short-monteur/scripts/rendre_video.py
git add tests/test_monteur.py
git add orchestrateur/agents_factices/monteur.py   # si modifié
git add orchestrateur/engine.py                    # si modifié
git commit -m "feat: E6 montage — rendre_video.py + tests A7 + CP3"
```

---

## Validation finale

```bash
python3 -m pytest tests/ -q
```

Tous les tests doivent passer (28 existants + nouveaux).
`test_render_remotion.py` peut rester skippé (node_modules absent en CI).

Vérifier en particulier :
- `test_e6_declenche_apres_e4_et_e5` ✓
- `test_e6_bloque_si_e4_attente_franco` ✓
- `test_cp3_declenche_apres_e6` ✓

---

## Contraintes

- Ne pas modifier `SKILL.md`, `construire_props.py`, `Video.tsx`, `Root.tsx`
- `rendre_video.py` : stdlib uniquement (subprocess, json, pathlib, os)
- Pas de nouveaux composants Remotion dans cette session
- L'agent factice monteur.py crée les fichiers sur disque (les tests en dépendent)
