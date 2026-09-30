# La mémoire : `Zehon/Memoire/`

Une skill ne se souvient de rien d'une conversation à l'autre. La mémoire
de la chaîne vit donc dans **3 fichiers courts** que Franco dépose au
lancement, et que tu lui **rends mis à jour** quand quelque chose a
changé. Garde chacun **sous une page** : ils doivent tenir dans le contexte
d'un compte gratuit. Quand un fichier grossit, résume les entrées
anciennes au lieu de les empiler.

## `sujets.md`

```markdown
# Sujets

## Faits
| n° | Sujet | Date de publication | Vues à J+7 |

## Proposés, non retenus
| Sujet | Date | Pourquoi pas (si Franco l'a dit) |

## Déjà traités ailleurs (relevé daté)
| Sujet | Chaîne | Angle / paradoxe | Vues | Date du relevé |
```

**Quand le mettre à jour** : à l'étape 1 (les sujets proposés et la
concurrence relevée), et à l'étape 5 (le sujet fait).

## `lexique.md`

```markdown
# Lexique de prononciation (voix clonée)

| Écrit | À écrire dans la version voix | Vérifié à l'écoute ? |
|---|---|---|
| Hallstatt | Halchtatt | non |
```

**Quand le mettre à jour** : à l'étape 3b, avec chaque nom difficile
rencontré. Franco passe « Vérifié » à oui après écoute : seuls les termes
vraiment mal prononcés doivent rester longtemps.

## `lecons.md`

```markdown
# Leçons

| Vidéo | Vues J+7 | Rétention moyenne | Taux de clic miniature | Leçon (une phrase) |

## Réglages mesurés
- Débit de la voix : <mots par seconde, mesuré sur l'enregistrement>
- Mots pour 8 min : <recalculé à partir du débit>
```

**Ce que Franco remplit** : les chiffres (YouTube Studio) et le débit
mesuré de sa voix.

**La discipline des chiffres** (reprise du plugin *AI YouTube OS*,
licence MIT, parce qu'elle évite les fausses conclusions) :
- relever les vues à **24 h, 72 h et 7 jours**, séparément ; un relevé
  fait en retard porte le délai réel (« 9 jours ») ; une valeur encore en
  traitement n'est pas remplacée par 0 ;
- **ne rien conclure avant 3 vidéos** : avant, une leçon est une
  observation, pas une règle ;
- **une seule expérience à la fois** (par exemple, changer seulement la
  miniature), notée dans `lecons.md` avant la publication. **Ce que tu en fais** : à l'étape 1, préfère les
formes de sujets qui ont marché ; à l'étape 3, applique les réglages
mesurés (par exemple le nombre de mots si le débit de la voix n'est pas
3 mots/s) et les leçons sur les hooks. Dis-le quand une leçon change ta
recommandation.
