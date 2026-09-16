# Notebooks

`voix_off.ipynb` : notebook Colab de synthèse vocale (§7.2, §13 étape 4),
**Qwen3-TTS** (`qwen-tts`, `Qwen/Qwen3-TTS-12Hz-1.7B-Base`) + faster-whisper
+ jiwer. Les 9 cellules (Cell 0 à Cell 8) sont implémentées (plus de
`TODO`/`NotImplementedError`) mais n'ont pas été exécutées dans ce sandbox
de développement, qui n'a ni GPU ni ces librairies — à valider avec un vrai
run Colab pendant la semaine de test, notamment les seuils par défaut (§12).

Qwen3-TTS a remplacé F5-TTS après que ce dernier a montré un défaut
structurel : le contenu de l'échantillon de référence fuyait dans la sortie,
reproduit sur deux références différentes.

Le débruitage `noisereduce` est **désactivé par défaut** (`DENOISE = False`) :
la référence de Franco (voix ElevenLabs) est déjà propre, et `noisereduce`
la dénaturait sans bruit réel à retirer.

Usage (Franco) : ouvre le notebook dans Colab avec un runtime GPU, modifie
uniquement les variables de la **Cell 1** (`VIDEO_ID`, `MODE`), puis exécute
les cellules dans l'ordre. Laisse `VIDEO_ID` vide pour une détection
automatique. `MODE` :
- `"full"` : run complet (upload voix si besoin, synthèse, qualité, state) ;
- `"resume_after_fail"` : reprend après un échec, sans re-uploader la voix ;
- `"quality_check"` : relance seulement le contrôle WER sur un audio existant ;
- `"voice_only"` : n'uploade/traite que l'échantillon de voix.

## Lancer sans ouvrir Colab (16/09/2026)

`python3 outils/lancer_voix_off.py --root /chemin/ChaineYouTube` exécute ce
même notebook sur un runtime Colab, depuis un terminal. Il s'appuie sur le
**Colab CLI officiel** de Google (`pip install google-colab-cli`, Linux et
macOS uniquement), et enchaîne ce que Franco faisait à la main :

```
colab new -s voixoff-<video_id> --gpu T4
colab drivemount -s voixoff-<video_id>
colab exec -s ...            ← pose les paramètres dans le noyau distant
colab exec -s ... -f notebooks/voix_off.ipynb
colab log  -s ... -o videos/<id>/audio/journal_colab_<horodatage>.md
colab stop -s ...
```

| Option | Défaut | |
|---|---|---|
| `--root` | — | racine vue **localement** (Drive pour ordinateur, rclone) |
| `--video` | auto | la seule vidéo dont `E4_audio` attend un run |
| `--mode` | `full` | `voice_only` est refusé : il demande un upload interactif |
| `--gpu` | `T4` | |
| `--timeout` | 5400 s | durée maximale du run du notebook |
| `--garder` | non | laisse la session Colab ouverte, pour diagnostiquer |
| `--verifier` | — | dit ce qui serait lancé, sans rien lancer |

Codes de sortie : `0` audio produit et vérifié, `1` run sans résultat
exploitable, `2` racine inutilisable (Drive non monté, rien n'a été lancé),
`3` aucune vidéo en attente ou choix ambigu, `4` `colab` absent ou en échec.

**Ce qui décide du succès n'est pas le code de retour de `colab exec`.** Le
notebook signale ses échecs par `SystemExit` depuis une cellule, et rien ne
garantit qu'un noyau Jupyter distant traduise cela en code de sortie non nul
— la documentation du CLI ne dit rien des codes de retour. Le lanceur conclut
donc en **relisant le Drive** : statut de `E4_audio` dans `state.json`, et les
quatre sorties présentes et non vides. C'est la leçon de `capturer_web.py`,
qui a validé trois fois une capture fausse parce que le contrôle regardait
la mauvaise chose.

### Trois changements dans le notebook, qui ne changent rien à l'usage manuel

1. **Les paramètres se lisent dans l'environnement** quand il les porte
   (`VOIX_VIDEO_ID`, `VOIX_MODE`, `VOIX_RACINE`, `VOIX_FORCER_RELANCE`).
   Sans ces variables — c'est-à-dire quand tu ouvres le notebook toi-même —
   le comportement est celui d'avant, au caractère près.
2. **Le Drive n'est pas remonté s'il l'est déjà.** `drive.mount()` ouvrirait
   un consentement OAuth que personne ne regarde dans un run automatisé : la
   cellule resterait suspendue jusqu'au timeout de la session, sans un mot.
3. **`full` ne redemande plus la voix de référence** si un profil existe
   déjà. C'était un défaut en soi : le sélecteur de fichiers s'ouvrait à
   chaque vidéo alors que la voix ne change jamais. Et en run automatisé,
   `VOIX_NON_INTERACTIF=1` fait échouer proprement, avec la marche à suivre,
   plutôt qu'attendre un clic qui ne viendra pas.

### Ce que ça ne fait pas

**E4 reste `attente_franco` dans la machine à états.** L'Orchestrateur fait
avancer les statuts, il n'exécute aucun agent (§6.4) — brancher E4 dessus
serait un autre chantier. Ce qui change, c'est que l'action attendue de
Franco est désormais **une commande**, donc quelque chose qu'une entrée de
crontab peut faire à sa place.

**Enregistrer une voix reste manuel**, une fois : `MODE='voice_only'` depuis
Colab. Il n'y a pas de chemin non interactif pour choisir un fichier, et il
n'y a pas de raison d'en fabriquer un pour une opération qui arrive une fois.

## Sorties

| Fichier | Pour qui |
|---|---|
| `04_voixoff.wav` | le montage (E6) |
| `04_timestamps.json` | les sous-titres, mot par mot |
| `04_phrases.json` | les **durées de scènes**, bornes début/fin par phrase (§8) |
| `04_rapport_audio.md` | Franco, et H1 pour le bilan hebdo — la **dernière** tentative |
| `audio/rapport_tentative_NN.md` | une copie par tentative, que la suivante n'écrase pas |

`04_phrases.json` est ce qui relie la voix au montage : c'est la seule étape
qui connaisse exactement les bornes de chaque phrase. Après coup, on ne peut
que les deviner en réalignant les mots transcrits sur le script, ce que le
WER non nul rend fragile.

Respecte le contrat `state.json` du §4.2 : démarre `E4_audio` en `en_cours`
(Cell 4), le termine ou l'échoue à la Cell 7, sans jamais toucher à une
autre étape.
