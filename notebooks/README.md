# Notebooks

`voix_off.ipynb` : squelette du notebook Colab de synthese vocale (§7.2,
§13 etape 4). Structure complete (les 9 cellules de la table du §7.2),
mais **non executable tel quel** : les points ouverts au §12 (API exacte
de Qwen-TTS, duree de l'extrait de reference, librairie de reduction de
bruit, seuils de controle qualite) sont marques `TODO`/`NotImplementedError`
a trancher pendant la semaine de test, avec un vrai GPU Colab. Ce sandbox
de developpement n'a ni GPU ni ces librairies, il n'a donc pas ete
possible de l'executer ici.

Respecte le contrat `state.json` du §4.2 (cellule 1) : demarre `E4_audio`
en `en_cours`, le termine ou l'echoue a la cellule 8, sans jamais toucher
a une autre etape.
