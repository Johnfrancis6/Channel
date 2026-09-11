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

## Sorties

| Fichier | Pour qui |
|---|---|
| `04_voixoff.wav` | le montage (E6) |
| `04_timestamps.json` | les sous-titres, mot par mot |
| `04_phrases.json` | les **durées de scènes**, bornes début/fin par phrase (§8) |
| `04_rapport_audio.md` | Franco, et H1 pour le bilan hebdo |

`04_phrases.json` est ce qui relie la voix au montage : c'est la seule étape
qui connaisse exactement les bornes de chaque phrase. Après coup, on ne peut
que les deviner en réalignant les mots transcrits sur le script, ce que le
WER non nul rend fragile.

Respecte le contrat `state.json` du §4.2 : démarre `E4_audio` en `en_cours`
(Cell 4), le termine ou l'échoue à la Cell 7, sans jamais toucher à une
autre étape.
