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

## A completer / valider par Franco

- Ton de voix (formel/familier, humour, rythme, expressions a eviter)
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

Pas de miniature pour l'instant (§4.3).
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
