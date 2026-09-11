# Notebooks

`voix_off.ipynb` : notebook Colab de synthese vocale (§7.2, §13 etape 4),
F5-TTS + faster-whisper + noisereduce. Les 9 cellules (Cell 0 a Cell 8)
sont implementees (plus de `TODO`/`NotImplementedError`) mais n'ont pas
ete executees dans ce sandbox de developpement, qui n'a ni GPU ni ces
librairies (F5-TTS, faster-whisper...) — a valider avec un vrai run Colab
pendant la semaine de test, notamment les seuils par defaut (§12).

Usage (Franco) : ouvre le notebook dans Colab avec un runtime GPU, modifie
uniquement les variables de la Cell 1 (`VIDEO_ID`, `MODE`), puis execute
les cellules dans l'ordre. `MODE` :
- `"full"` : run complet (upload voix si besoin, synthese, qualite, state) ;
- `"resume_after_fail"` : reprend apres un echec, sans re-uploader la voix ;
- `"quality_check"` : relance seulement le controle WER sur un audio existant ;
- `"voice_only"` : n'uploade/traite que l'echantillon de voix.

Respecte le contrat `state.json` du §4.2 (Cell 0) : demarre `E4_audio`
en `en_cours`, le termine ou l'echoue a la Cell 7, sans jamais toucher
a une autre etape.
