# Message d'ouverture de la prochaine session (Zehon)

À copier tel quel dans une nouvelle discussion Claude Code web, avec le
connecteur Google Drive activé. Compléter la ligne « Script de
l'aluminium » avant d'envoyer.

---

Session de travail sur ma chaîne YouTube française **Zehon** (« de la
matière brute à l'objet »).

**Script de l'aluminium** : [validé / mes corrections : …]

## Mise en route
1. Récupère la branche de travail et reste dessus toute la session :
   `git fetch origin claude/modest-darwin-gnew9l`, puis
   `git checkout claude/modest-darwin-gnew9l`.
2. Lis `docs/chaine2/CONTEXTE.md` : les deux blocs du haut (« Reprise au
   01/10/2026 ») disent où on en est. Puis `zehon/content-maker/SKILL.md`.
3. Vérifie que le connecteur Google Drive répond : dossier `Zehon`
   (`1e3_Fu2nbhyfKtvCG2k54ME_W6K-gaKWB`), vidéo `Videos/03_aluminium`
   (`1_d4WAgXlr2IeLwFltmSWOPHVsurIhBdp`).

## Ce que j'attends, dans l'ordre
1. **L'aluminium** : si j'ai validé le script, enchaîne les étapes 4
   (scènes et prompts) et 5 (publication) de la skill `content-maker`.
   Si j'ai donné des corrections, applique-les d'abord (script et version
   voix, vérificateur), puis enchaîne.
2. **La chaîne de production des pièces** (bloc « chaîne de production »
   de `CONTEXTE.md`) : je génère sur **Windows, dans un navigateur**.
   Construis, dans cet ordre :
   - la **skill Gemini `zehon-images`** (dossier prêt à importer) et le
     mode d'emploi pour la tester avec moi sur quelques scènes de
     l'aluminium ;
   - le réglage **Google Drive pour ordinateur + dossier de
     téléchargement** vers `a_ranger/`, en étapes courtes ;
   - le **notebook gratuit** qui vérifie, renomme et range ce qui arrive
     dans `a_ranger/`, tient `images/etat.json` et me donne la liste à
     refaire et le prochain lot. Teste d'abord le vérificateur sur les
     images du sel (le bras en trop) ;
   - la mise à jour de `content-maker` (étape 4 et état des pièces).
   Chiffre l'effort et propose l'ordre avant de coder.

## Règles
- Donne tes recommandations, pas des listes d'options. Sépare ce qui est
  mesuré de ce qui est une hypothèse. Une question à la fois.
- Affiche les prompts d'images en entier dans la conversation, un bloc de
  code par prompt.
- Ne jamais éditer `.claude/skills/` (miroir généré) : modifier
  `zehon/content-maker/`, puis `python3 zehon/synchroniser_skills.py`.
- Tests : `python3 -m unittest discover -s tests`.
- Mets à jour `docs/chaine2/CONTEXTE.md` en fin de session. Commite et
  pousse sur la branche ci-dessus, avec `git fetch` avant chaque push.
- Réponds en français.
