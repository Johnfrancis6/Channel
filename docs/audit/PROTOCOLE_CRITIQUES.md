# Protocole de critique à chaque génération

Décidé par Franco le 07/11/2026. S'applique à **toutes les sessions** qui
produisent du contenu (Zehon, puis Whose Dime) : recherche, plan, script,
version voix, scènes et prompts, publication. Les lignes accumulées serviront
à concevoir la future skill de détection d'incohérences : on ne la conçoit
pas avant d'avoir environ 30 critiques notées.

## Après chaque livrable généré

1. **Claude critique son propre livrable**, en 5 lignes au plus, avant de le
   présenter comme fini. Chaque défaut porte un type pris dans la liste
   ci-dessous et cite l'endroit exact (ligne, scène, phrase).
2. **Claude demande la grille à Franco**, en une seule question :
   « Exact / Clair / Vivant, de 1 à 5, et une phrase ? »
3. **Claude ajoute une ligne** à `docs/audit/journal_critiques.jsonl` (et la
   commite en fin de session), même si Franco ne répond pas : ses champs
   restent alors vides.

## Types de défauts

| Type | Exemple |
|---|---|
| `fait` | chiffre, date ou nom faux, non sourcé ou cité de mémoire |
| `incoherence` | le script contredit le plan ; une scène ne correspond pas à la phrase dite ; le titre promet ce que la vidéo ne montre pas |
| `processus` | étape sautée, fichier manquant ou mal nommé, doublon dans Drive, reprise au mauvais endroit |
| `robotique` | phrase de rapport, énumération, absence de personnage ou de scène |
| `formel` | registre trop soutenu, jargon, tournures administratives |
| `nuance` | affirmation absolue là où les sources hésitent ; pas de « mais » |
| `comprehension` | notion non expliquée, phrase trop longue pour l'oreille, saut logique |
| `voix` | mot ou nombre mal prononcé, fin de phrase coupée, débit monotone (critique après écoute de Franco) |

## Format d'une ligne du journal

```json
{"date": "2026-11-08", "chaine": "zehon", "video": "03_pain", "etape": "3b_script",
 "livrable": "02_script.md", "session": "<lien de la session>",
 "critique_claude": [{"type": "robotique", "ou": "§4, l. 2", "defaut": "trois chiffres d'affilée sans scène"}],
 "franco": {"exact": 4, "clair": 3, "vivant": 2, "phrase": "on dirait un exposé"},
 "corrige": true}
```

Un défaut que Franco signale sans que Claude l'ait vu s'écrit dans
`critique_claude` avec `"vu_par": "franco"` : ce sont les cas les plus utiles
pour la future skill.
