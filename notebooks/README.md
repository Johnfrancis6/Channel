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
**Colab CLI officiel** de Google, et enchaîne ce que Franco faisait à la
main :

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

### Le consentement Drive, et pourquoi il n'y a pas de run sans humain

`colab drivemount` monte le Drive avec un **jeton éphémère** : l'URL
d'autorisation porte `authorize-for-drive-credentials-ephem` et
`prompt=consent`. Le consentement est redemandé **à chaque session**, et
autoriser une fois dans un notebook classique ne se reporte pas. Constaté le
16/09/2026, après trois runs échoués sur `ValueError: mount failed`.

Ce n'est donc pas un réglage à corriger : tant que le montage de Drive est sur
le chemin, un humain clique une fois par run. La marche à suivre :

```bash
colab new -s voixoff --gpu T4
colab drivemount -s voixoff          # ouvre l'URL affichée, autorise, Entrée

python3 outils/lancer_voix_off.py --root "$CHAINE_YT_ROOT" \
  --reprendre --session voixoff
```

`--reprendre` saute `new` et `drivemount`, vérifie que la session répond, et
enchaîne le reste. Elle **n'arrête pas** la session à la fin : le
consentement est la seule chose du run qui ait coûté un geste humain, et
l'arrêter obligerait à en redonner un pour une seconde tentative. Ajoute
`--arreter` quand tu en as fini.

Pense à libérer la machine ensuite, elle consomme du quota :

```bash
colab stop -s voixoff
```

**Le seul chemin vers un run réellement sans humain** serait de ne pas monter
Drive du tout : pousser le script et la référence avec `colab upload`,
récupérer les quatre sorties avec `colab download`, écrire `state.json`
localement. Il demande de sortir la synthèse du notebook, donc de maintenir
deux implémentations — pas fait, et à ne faire que si le clic par run devient
gênant.

### Installation du CLI

```bash
uv tool install google-colab-cli
colab new -s test-auth && colab stop -s test-auth   # authentification, une fois
```

**Pas `pip install`.** Le paquet exige Python >= 3.12 ; sous un interpréteur
plus ancien, pip répond `No matching distribution found`, ce qui ressemble à
tort à un paquet qui n'existe pas. `uv` récupère lui-même un interpréteur
compatible, sans toucher au Python du système. Linux et macOS uniquement —
sous Windows, WSL.

Le lanceur, lui, tourne sous le Python du dépôt : il n'appelle `colab` qu'en
sous-processus, il n'a donc pas besoin de 3.12.

Codes de sortie : `0` audio produit et vérifié, `1` run sans résultat
exploitable, `2` racine inutilisable (Drive non monté, rien n'a été lancé),
`3` aucune vidéo en attente ou choix ambigu, `4` `colab` absent ou en échec.

**Ce qui décide du succès n'est pas le code de retour de `colab exec`.** Le
notebook signale ses échecs par `SystemExit` depuis une cellule, et rien ne
garantit qu'un noyau Jupyter distant traduise cela en code de sortie non nul
— la documentation du CLI ne dit rien des codes de retour. Le premier run réel
l'a confirmé : `colab exec` a rendu `0` sur un run dont il ne savait rien.

Le lanceur conclut donc en relisant le résultat — **sur la VM, et avant
d'arrêter la session**. C'est là que l'écriture a eu lieu. Juger depuis la
machine de Franco revenait à interroger un miroir Drive asynchrone : le
16/09/2026, un run parfaitement réussi — WER 1,47 %, `E4_audio = termine`,
quatre fichiers écrits — a été déclaré en échec parce que les fichiers
n'étaient pas encore redescendus dans `/mnt/g`. Le contrôle était au bon
endroit logique et du mauvais côté du réseau.

Le snippet de vérification imprime une ligne préfixée `RESULTAT_E4`. Son
**absence vaut échec** : si le contrôle n'a pas pu s'exécuter, on ne conclut
pas au succès.

Une fois le run validé, le lanceur attend que le miroir local redescende les
fichiers (`--attente-miroir`, 180 s par défaut), parce que c'est lui que lira
le montage. Ce retard **n'est pas un échec** et ne change pas le code de
sortie : le dire autrement ferait chercher un bug qui n'existe pas.

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
