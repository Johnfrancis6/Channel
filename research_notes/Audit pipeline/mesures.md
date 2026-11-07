# Audit du pipeline — mesures (07/11/2026)

Toutes faites ici, sur les fichiers Drive téléchargés en brut. Outils dans
[`outils/`](outils/). « Mesuré » = refait par une commande ; le reste est
signalé comme hypothèse dans le rapport.

## 1. Le vérificateur passe, alors que les défauts sont là

```
python3 verifier.py verre/02_script.md
02_script.md — 1505 mots, 144 phrases, médiane 10.0 mots, ~8.4 min à 3 mots/s. 0 erreur(s), 0 avertissement(s).
python3 verifier.py verre/02_script_voix.txt
02_script_voix.txt — 148 lignes, 1551 mots, ~8.6 min à 3 mots/s. 0 erreur(s), 4 avertissement(s).  (4 lignes de 2-3 mots)
python3 verifier.py aluminium/02_script.md
02_script.md — 1499 mots, 140 phrases, médiane 11.0 mots, ~8.3 min à 3 mots/s. 0 erreur(s), 0 avertissement(s).
```

Le vérificateur ne regarde que la forme : il ne voit ni les faits absents de
la recherche, ni le ton.

## 2. La forme des scripts (`outils/stats_script.py`)

| Mesure | Verre | Aluminium |
|---|---|---|
| Mots / phrases | 1 505 / 144 | 1 499 / 140 |
| Longueur des phrases : médiane, écart-type | 10 mots, 4,8 | 11 mots, 4,1 |
| « Sauf que » | 7 (7 blocs sur 12 finissent par lui) | 9 |
| Nombres écrits en chiffres | 20 (un tous les 75 mots) | 48 (un tous les 31 mots, ~ toutes les 9 s à 3,4 mots/s) |
| Premiers mots les plus fréquents | Le 10, Et 8, Les 7, Mais 7, Sauf 7, Il 7 | Il 16, En 12, Et 11, Le 10, Sauf 9 |
| Personnes nommées (verre) | Pline 3, Tibère, Toutânkhamon, Barovier, Pilkington, Bickerstaff : 1 chacun | — |
| Citations ou dialogues (verre) | 1 (« plus répandue que bien attestée ») | — |
| Version voix (verre) | 148 lignes, médiane 10 mots, 142 finissent par un point, 6 par « ? » | — |

## 3. Script contre version voix (`outils/diff_script_voix.py`, verre)

Similarité 0,990, 15 écarts, tous voulus : graphies phonétiques
(Bélusse, lapisse, Toutankamon, Ouloubouroune, Mourano, Andjélo Barovière,
Alastère Pilkingtone, Bickerstaffe), petits ajouts (« et puis », « mais »,
« c'était », « c'est », « très clair »), « années 1960 » dit « années
soixante ». **La version voix est fidèle**, mais aucun outil du pipeline ne
fait ce contrôle : il a fallu l'écrire pour l'audit.

## 4. Faits du script absents de la recherche

Verre (recherche v2 relue « fait par fait » le 01/10) :

| Bloc | Phrase du script | Dans `01_recherche.md` ? |
|---|---|---|
| Q2-T3 | « Il y a environ 3 400 ans, en Égypte, le verre est un matériau de pharaon » | non (aucune date ; Amarna ≈ −1350 la rend plausible) |
| Q2-T3 | lingots « bleu foncé, turquoise ou lavande » | « du lavande au turquoise » : « bleu foncé » ajouté |
| Q2-T4 | « Il y a 3 000 ans, c'était un objet de luxe » | non |
| Q3-T7 | Venise et la Normandie « pendant des siècles » | « méthode tenue secrète », sans durée |
| Q4-T9 | « Ces glaces finissent en miroirs, dans les châteaux » | « produits de luxe » seulement |

Aluminium : la citation « Un maréchal l'avait dit avant lui : « Plus d'un
homme, plus d'un cheval, sont restés en route pour un kilogramme de trop. » »
(Q2-T4). La recherche plein texte Drive du 07/11 trouve « maréchal » dans
`02_script.md`, `02_script_voix.txt` et `03_scenes.md`, **pas** dans
`01_recherche.md` ni `02_plan.md` : citation sans source, attribuée à une
personne non nommée.

Sel : `02_script.md`, bloc Q4-T10 : « Toi, tu en manges environ 3 kilos par
an. `<!-- 8,1 g/jour, Esteban : à vérifier -->` ». Le « à vérifier » est un
commentaire HTML, effacé par le vérificateur (`texte_du_script`, l. 55) et
invisible pour la voix et les scènes. La vidéo a été validée le 30/09 avec
cette phrase ; `CONTEXTE.md` (l. 51) la liste encore « à vérifier » au 01/10.

## 5. Publication contre recherche (verre)

La recherche v2 écrit : « la prémisse « aucune vitre transparente avant
1959 » était fausse ». La publication garde cette prémisse :
- titre recommandé : « Pourquoi a-t-il fallu 4 000 ans pour faire une vitre ? » ;
- miniature M2 : « NÉE EN 1959 ?! », justifiée par « le procédé float est
  annoncé le 20 janvier 1959 » (le procédé, pas la vitre) ;
- description : « Du sable du fleuve Bélus au bain d'étain » : le Bélus
  est présenté comme l'origine, alors que le script dit « c'est une légende ».

## 6. État des fichiers de reprise

| Fichier | Ce qu'il dit | Ce qui est vrai (Drive, 07/11) |
|---|---|---|
| `CONTEXTE.md` (bohr, 01/10) | vidéos : sel, verre ; sujets suivants : pain, sucre | `03_aluminium` a son contenu complet depuis le 01/10 17:27 |
| `Memoire/sujets.md` | sel et verre : « reste : images, voix, assemblage » | les deux sont rendus (`verdict.json` « pret »: true) |
| sel `voix/etat.json` | `a_reecouter` : 19 phrases | `historique.md` l. 94-97 : 19 fausses alertes, corrigées dans le notebook ; le fichier n'a pas été réécrit |
| sel `rendu/verdict.json` | `sortie` : `extrait_001-010.mp4`, 48,3 s | le rendu complet (`rapport.json`, 21:21) a été écrasé par le verdict d'un extrait (23:35) |
| verre `rendu/verdict.json` | `code` : `claude/zelan-studio-analysis-rws9f6@15b0fe0` | ce commit n'a pas le bandeau `53fac3b` ; le lanceur voix Drive pointe aussi sur cette branche |
| `Memoire/lecons.md` | « environ 1 610 mots pour 8 min » (3,36 mots/s pauses comprises) | `verifier.py` vise 1 400-1 560 et calcule à 3 mots/s ; `etat.json` donne `debit_mots_s` = 3,69 (parole seule), que `SKILL.md` l. 211 demande de reporter |

## 7. Voix

- `voix_zehon.ipynb` : une synthèse `generate_voice_clone` **par ligne** de
  `02_script_voix.txt` (cellule 4), puis un silence fixe de `PAUSE_MS = 300`
  entre toutes les lignes (cellules 1 et 5). Aucun silence de fin ajouté,
  aucun fondu, aucune mesure de la fin de chaque clip.
- Contrôle existant : Whisper retranscrit, ressemblance ≥ 0,80 par phrase.
  Verre : `a_reecouter` = [] alors que `CONTEXTE.md` l. 14-15 rapporte
  « ~1 phrase sur 6 finit sèche ». Le contrôle ne voit pas ce défaut.
- La mesure « 1 sur 6 » n'a ni méthode ni données dans le dépôt (elle est
  dans `CONTEXTE.md`, pas dans `historique.md`) : non reproductible.
- Débit : 3,69 mots/s en parole (sel), 3,65 (verre) ; Zelan 3,09 pauses
  comprises (`lecons.md` l. 9 et 14).

## 8. Tests

`python3 -m unittest discover -s tests` (bohr) : 1 erreur de chargement
(`No module named 'cv2'`) dans un conteneur neuf ; après
`pip install opencv-python-headless pillow numpy` : **26 tests, OK**.
`python3 zehon/synchroniser_skills.py --verifier` : « Aucune dérive ».
Aucun test ne couvre script contre recherche, script contre voix ou
publication contre recherche.

## 9. Noms de fichiers

- `etape4_scenes.md` l. 33 et `verifier.py` l. 177 imposent
  `clips/scene_NNN.mp4` ; dans Drive (verre), les clips s'appellent
  `anim_NNN.mp4` ; `monter.py` accepte les deux.
- La charte et `etape4` parlent de `planche_bonhomme.png` ; le fichier est
  `.jpg` (publication du verre).
- `etape1_sujet.md` l. 67-68 crée 3 sous-dossiers ; `SKILL.md` l. 152-155 en
  demande 5.
- Dans cette session, deux copies de la skill sont chargées :
  `content-maker` (dépôt) et `anthropic-skills:content-maker` (claude.ai).
  Leur version n'est écrite nulle part (hypothèse : elles divergent).
