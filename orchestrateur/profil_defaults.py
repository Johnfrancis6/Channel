"""
Contenu de depart pour 00_Profil/, genere a l'initialisation (§13, etape 2).
Ce sont des brouillons a valider par Franco (§3 : "Toute mise a jour est
validee par Franco") : rien ici n'est ecrase si le fichier existe deja.
"""

PROFIL_CHAINE_MD = """# Profil de la chaine

*Brouillon genere automatiquement a partir de docs/architecture_chaine_v1.2.md §1. A valider et completer par Franco.*

- **Type** : faceless total
- **Format** : Shorts (vertical 1080x1920)
- **Langue** : anglais
- **Niche** : tech / IA appliquee, actu IA decodee
- **Audience** : debutants curieux
- **Angle** : "ingenieur ML" qui decode et teste. Les projets reels de Franco servent d'illustration ponctuelle.
- **5 piliers** : actu_ia, avis_outil, concept, projet_perso, tuto

## Ton de voix

**Pas de charabia neutre a la robotique.** Une voix incarnee, qui assume un
point de vue : "j'ai teste, voila ce qui a casse". Pas de tournures
impersonnelles, pas de precautions oratoires, pas de vocabulaire d'assistant
("il est important de noter que", "plongeons dans"). Si une phrase pourrait
sortir telle quelle d'un billet de blog genere, elle est a reecrire.

## A completer / valider par Franco

- Ton de voix : preciser l'humour et le rythme (le registre est pose ci-dessus)
- Chaines concurrentes de reference, pour l'Analyseur de chaines (A3)
- Mots-cles et sources de veille, pour le Chercheur (A2)
- Exemples de titres/hooks qui fonctionnent bien dans la niche
- Duree cible d'un Short et rythme de montage souhaite
"""

CONVENTIONS_MD = """# Conventions de production

*Brouillon genere a partir de docs/architecture_chaine_v1.2.md §7.3 et §2. A valider par Franco.*

## Calibrage des phrases (Filtre TTS, A5)

- Une phrase = une ligne dans `03_script_tts.txt`.
- Longueur cible : 8 a 18 mots.
  - Au-dessus de 22 mots, la phrase est decoupee.
  - En dessous de 4 mots, elle est fusionnee avec la voisine (sauf hooks courts, marques explicitement).
- Pas de parentheses, de symboles ni d'URL dans le texte destine au TTS.
- Chiffres, unites et versions ecrits en toutes lettres.
- Sigles et noms propres techniques passes par `lexique_prononciation.md`.

## Regles fixes de la chaine (§2)

- Le systeme ne choisit jamais le sujet final d'une video sans l'accord de Franco.
- Le systeme ne gere pas le SEO (titres, descriptions, tags) : c'est Franco qui le fournit au CP3.
- Aucune publication sans Checkpoint 3 valide.
- Retry : 3 tentatives maximum par etape automatisee, puis alerte a Franco.
"""

LEXIQUE_PRONONCIATION_MD = """# Lexique de prononciation

*Amorce reprise de docs/architecture_chaine_v1.2.md §7.4. S'enrichit via les propositions de A5 validees au CP2, les signalements du controle qualite audio, et les notes de Franco.*

## Regle des sigles

Un sigle courant s'ecrit **normalement** (`LLM`, `MCP`, `VS`), pas epele
lettre par lettre (`L L M`). L'epellation a deux defauts : la synthese la
rend souvent moins bien que le sigle brut, et surtout elle casse le
controle qualite, puisque Whisper retranscrit `LLM` et non `L L M` — le
WER compte alors des erreurs qui n'en sont pas.

N'entrent au lexique que les termes que la synthese prononce reellement
mal, verifies sur un run. Un sigle qui passe bien n'a pas d'entree.

| Terme | Forme ecrite pour le TTS | Statut |
|---|---|---|
| GPT-5 | GPT five | valide |
| RAG | rag | valide |
"""

CHARTE_MD = """# Charte visuelle

*Brouillon a valider en lot par Franco avec le Designer (§4.3, A6). Rien ici n'est definitif.*

- **Palette** : a definir (voir `charte.json` pour les valeurs par defaut placeholder)
- **Typographie des sous-titres** : a definir
- **Rythme des transitions** : a definir
- **Frame d'accroche** : a definir
- **Style d'illustration** : a definir

## Principes d'animation (valides une fois, pas redecides par video)

Ces principes vivent dans `charte.json` sous la cle `animation` : les
composants Remotion les lisent, le Designer (A6) s'y refere dans la
direction artistique de chaque scene, et le Monteur (A7) les applique sans
avoir a les reinventer (§8).

- **Easing par defaut** : `ease-out` pour les entrees (le mouvement arrive
  vite puis se pose), `ease-in-out` pour les transitions entre scenes.
- **Entrees en ressort** : `spring` pour tout ce qui doit avoir du
  caractere (personnage, chiffre cle) ; `interpolate` pour ce qui doit
  rester discret (texte de fond, cartouche).
- **Regle du wobble** : une oscillation permanente et legere sur les
  elements dessines a la main (stickman, traits), jamais sur le texte —
  ca rend le trait vivant sans fatiguer la lecture.
- **Un mouvement dominant par scene** : si l'element principal bouge, le
  fond est fixe, et inversement.
- **Rien ne bouge pendant le hook** au-dela de l'entree : les trois
  premieres secondes se jouent sur le texte et la voix.

## Style vise : sticker anime

Formes pleines, contours nets, mouvement **fluide et naturel** — pas le
trait filaire procedural des premiers composants. L'elasticite prime sur la
precision geometrique.

## Lottie ou Remotion : qui fait quoi

Lottie est autorise pour tout type d'animation (decision du 11/09/2026),
mais un fichier Lottie est une animation **pre-rendue** : on la joue, on la
boucle, on en lit un segment, on recolore des couches — on ne change pas ce
qu'elle raconte. La repartition suit donc cette limite :

| Ce qu'on anime | Technique |
|---|---|
| Personnage, stickman, mascotte | **Lottie** — c'est fait pour ca |
| Transitions, icones animees, effets | **Lottie** |
| Schema dont le contenu change d'une video a l'autre | **Remotion** |
| Texte, chiffres, labels | **Remotion** |
| Sous-titres cales sur `04_timestamps.json` | **Remotion** |

La raison est operationnelle : `ConceptCutaway` a cinq variantes et la
prochaine video en demandera d'autres. En Lottie, chaque nouveau schema
serait un fichier a produire a la main avant de pouvoir tourner — chaque
video deviendrait une dependance humaine. Les deux techniques se
superposent sans probleme dans une meme scene.

**Provenance des fichiers** : un **jeu de base reutilisable** de quatre
fichiers dans `composants/lottie/` (stickman qui parle, qui pointe, qui
reagit, plus une transition), rejoue d'une video a l'autre. Le stickman
revient dans chaque video : un seul bon fichier s'amortit sur toute la
serie. Les animations propres a une seule video vont dans
`videos/{video_id}/assets/`. Cahier des charges, contraintes techniques et
licences : `composants/lottie/README.md`.

Pas de miniature pour l'instant (§4.3).
"""

PROJETS_FRANCO_MD = """# Projets et outils de Franco

*Brouillon monte a partir des reponses de Franco (11/09/2026). **A relire et
corriger par lui** : c'est son fichier, aucun agent n'ecrit ici.*

**Lu par** : le Chercheur (A2) pour choisir ses exemples, le Redacteur (A4)
pour les ancrer dans du vecu.

## A quoi sert ce fichier

A fournir des **exemples et des illustrations**, pas des sujets. Les sujets
viennent du backlog, de la veille actu ou de ce qui marche dans la niche.
Ici, on repond a une seule question : *quand il faut illustrer une idee,
qu'est-ce que Franco a sous la main qui soit vrai, teste, et montrable ?*

Un exemple qui n'est pas **montrable a l'ecran** ne sert a rien. C'est le
champ decisif de chaque entree.

## Terrain quotidien

Franco construit et teste **chaque jour des systemes d'agents**, avec deux
obsessions : l'**autonomie** et le **cadrage dans le contexte de
l'utilisateur**. C'est le socle de credibilite de la chaine — tout ce qui
touche aux agents, au contexte, a la memoire et aux garde-fous est du vecu,
pas de la lecture.

## En cours

### Serveur MCP — maj 2026-09-11
- Montrable : *a completer par Franco*
- Illustre bien : comment un agent atteint un service externe

### Automatisation YouTube (ce pipeline) — maj 2026-09-11
- Montrable : le tableau de bord, un `state.json` qui avance, un storyboard
- Illustre bien : machine d'etats, checkpoints humains, agents specialises

### Tests sur Claude Code — maj 2026-09-11
- Montrable : *a completer par Franco*
- Illustre bien : ce qu'un agent de code fait vraiment, et ou il achoppe

### Agent WhatsApp — maj 2026-09-11
- Montrable : *a completer par Franco*
- Illustre bien : un agent branche sur un canal que tout le monde connait

### Orchestration d'agents pour construire un logiciel — maj 2026-09-11
- Montrable : *a completer par Franco*
- Illustre bien : plusieurs agents qui se repartissent un travail reel

### Claude + MCP VS Code sur GitHub — maj 2026-09-11
- Montrable : Claude lit le code, le modifie et commit sur un vrai depot
- Illustre bien : la difference workflow / agent, l'action via un service
  externe. C'est l'exemple valide au CP1 de `2026-09-11_v01`

## Outils testes

| Outil | Verdict | Montrable ? |
|---|---|---|
| Qwen3-TTS | clonage propre, WER 0,87 % | oui — comparaison audio avant/apres |
| F5-TTS | defaut structurel : le contenu de la reference fuit dans la sortie, reproduit sur deux echantillons | oui — excellent contre-exemple |
| Remotion | bibliotheque de composants d'animation | oui — le rendu lui-meme |

## Echecs reproductibles

Un echec qu'on sait refaire vaut mieux qu'une reussite qu'on ne sait pas
expliquer. Pas de captures gardees, mais les erreurs se reproduisent — donc
elles se filment.

### Site e-commerce construit par copier-coller entre sessions
Du code repris morceau par morceau d'une session a l'autre, jusqu'a
l'ecroulement complet du projet.

- **Ce que ca illustre** : ce qui arrive quand un agent n'a pas le contexte
  du projet, seulement des fragments. Le sujet n'est pas "l'IA code mal",
  c'est la perte de contexte entre sessions
- **Montrable** : oui, l'echec est reproductible — donc rejouable a l'ecran
- **Pilier** : avis d'outil, ou concept (contexte et memoire d'un agent)

## A ne pas utiliser comme exemple

- **Trop niche pour des debutants curieux** : upgrade Laravel, configuration
  serveur, tout ce qui suppose un metier precis
- **Jamais teste en vrai** : tout ce qui viendrait d'une demo ou d'une page
  marketing. La chaine dit "j'ai teste", ca doit etre vrai

## A completer par Franco

- Le champ **Montrable** des quatre projets marques *a completer* : qu'est-ce
  qu'on voit a l'ecran ? Un terminal qui defile, une interface, une courbe,
  un avant/apres ?
- Ce qui est **sous NDA ou non partageable**, s'il y en a — la question n'a
  pas encore ete tranchee
- D'autres echecs reproductibles : ce sont les meilleures illustrations
"""

CHAINES_CONCURRENTES_JSON = []
# Liste a remplir par Franco : [{"channel_id": "UCxxxx", "nom": "..."}]
# Utilisee par le Chercheur (A2, veille) et l'Analyseur de chaines (A3, §4.3).

CHARTE_JSON = {
    "version": 1,
    "statut": "brouillon",
    "couleurs": {
        "fond": "#0B0F14",
        "texte_principal": "#F5F7FA",
        "accent": "#5B8CFF",
        "accent_secondaire": "#FFD166"
    },
    "typographie": {
        "sous_titres": {"famille": "a_definir", "taille_px": 64, "graisse": "bold"}
    },
    "rythme": {
        "duree_transition_s": 0.3,
        "easing": "ease-in-out"
    },
    # Principes de style recurrents (§8), valides une fois avec la charte
    # plutot que redecides a chaque video. A6 s'y refere dans le bloc
    # `da` de chaque scene, A7 les applique.
    "animation": {
        "style": "sticker_anime",
        # Lottie autorise pour tout type d'animation (11/09/2026), dans la
        # limite de ce qu'un fichier pre-rendu sait faire : `fixe` liste ce
        # qui lui revient, `variable` ce qui reste a Remotion parce que le
        # contenu change d'une video a l'autre.
        "lottie": {
            "actif": True,
            "fixe": ["personnage", "transition", "icone", "effet"],
            "variable": ["schema", "texte", "sous_titres"],
            "dossiers": ["videos/{video_id}/assets/", "composants/lottie/"],
            # Jeu de base reutilise d'une video a l'autre : peu de fichiers,
            # mais coherents entre eux. Cahier des charges et licences dans
            # composants/lottie/README.md.
            "jeu_de_base": ["stickman_parle", "stickman_pointe",
                            "stickman_reagit", "transition"]
        },
        "easing_entree": "ease-out",
        "easing_transition": "ease-in-out",
        "duree_entree_s": 0.3,
        "technique_defaut": "spring",
        "wobble": {
            "actif": True,
            "amplitude_px": 6,
            "periode_s": 1.2,
            "cible": "trace_main"
        },
        "regles": [
            "Un seul mouvement dominant par scene.",
            "Pas de wobble sur le texte.",
            "Pendant le hook, rien ne bouge au-dela de l'entree."
        ]
    },
    "format": {"largeur_px": 1080, "hauteur_px": 1920, "fps": 30}
}
