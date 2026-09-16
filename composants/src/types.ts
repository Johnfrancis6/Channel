export type CharteTokens = {
  couleurs: {
    fond: string;
    texte_principal: string;
    accent: string;
    accent_secondaire: string;
  };
  typographie: {
    // Niveau historique, garde pour les chartes anterieures au 16/09/2026.
    // Il servait a TOUT — titres, labels, sous-titres — ce qui revenait a
    // n'avoir aucune hierarchie typographique : une seule valeur decidait de
    // l'identite de la chaine entiere, et cette valeur etait "Arial".
    sous_titres: {famille: string; taille_px: number; graisse: string};
    // Trois niveaux distincts (16/09/2026). Absents d'une charte ancienne :
    // les valeurs par defaut de `typographie.ts` prennent alors la main.
    titre?: NiveauTypo;
    label?: NiveauTypo;
  };
  rythme: {
    duree_transition_s: number;
    easing: string;
  };
  // Principes de style recurrents (§8), valides une fois avec la charte.
  // Optionnel : une charte.json anterieure a la revue du 11/09/2026 n'a pas
  // ce bloc, et les composants doivent continuer a rendre sans lui.
  animation?: AnimationTokens;
  format: {largeur_px: number; hauteur_px: number; fps: number};
};

/**
 * Un niveau de la hierarchie typographique.
 *
 * `interlettrage` est en pixels, comme `letter-spacing` : negatif pour un
 * grand titre, qui respire trop a taille reelle, positif pour un petit label
 * en capitales, qui se serre.
 */
export type NiveauTypo = {
  famille?: string;
  taille_px?: number;
  graisse?: number;
  interlettrage?: number;
};

export type AnimationTokens = {
  easing_entree?: string;
  easing_transition?: string;
  duree_entree_s?: number;
  technique_defaut?: TechniqueDA;
  wobble?: {actif: boolean; amplitude_px: number; periode_s: number; cible?: string};
  // Ce qui separe une animation vivante d'une animation mecanique. La
  // fluidite se code : elle ne vient pas d'un fichier pre-rendu.
  naturel?: {
    decalage_entree_ms?: number;
    variation_vitesse?: number;
    mouvement_secondaire_retard_ms?: number;
    anticipation_px?: number;
    parallaxe_fond?: number;
  };
  regles?: string[];
};

// Vocabulaire ferme de la direction artistique (§8). A6 le remplit par
// scene dans 05_storyboard.json, A7 l'applique. Ferme volontairement : un
// champ libre redeviendrait de l'improvisation au montage.
export type MouvementDA =
  | 'entree_par_le_bas'
  | 'fondu'
  | 'zoom_lent'
  | 'glissement_lateral'
  | 'apparition_sequencee'
  | 'aucun';

export type RythmeDA = 'pose' | 'standard' | 'punch';

// Lottie ecarte (11/09/2026) : tout est code en Remotion.
export type TechniqueDA = 'spring' | 'interpolate' | 'statique';

// Transition vers la scene suivante, choisie par A6 scene par scene.
// Avant, Video.tsx appliquait un fondu enchaine de 0,25 s code en dur,
// identique sur les dix coupes : une signature unique et repetee se lit
// comme un diaporama, exactement comme l'absence de transition se lisait
// comme onze coupes seches.
export type TransitionSortie =
  | 'fondu'
  | 'glissement'
  | 'balayage'
  | 'iris'
  | 'coupe';

export type DirectionArtistique = {
  mouvement: MouvementDA;
  rythme: RythmeDA;
  technique: TechniqueDA;
  // Ce que la scene doit mettre en avant, en clair (ex. "le chiffre 10x").
  accent?: string;
};

/**
 * Un instant de video reelle pose **par-dessus** une scene animee, sur le
 * point precis dont parle le script.
 *
 * Ce n'est pas un composant de scene : `Video.tsx` associe un composant du
 * registre a une scene entiere, donc un insert qui en deviendrait un
 * occuperait tout le cadre pendant toute la scene — c'est-a-dire qu'il
 * redeviendrait `PlanBroll`, le plan de liaison que la contrainte du format
 * long ecarte. C'est une surcouche bornee dans le temps, de la meme famille
 * que `Subtitles`, rendue par `InsertFootage`.
 *
 * Le modele de scene supportait deja un sous-element temporel : `pulsation_s`
 * designe un **instant** dans une scene. Un insert demande un **intervalle** —
 * la meme mecanique, une borne de plus.
 */
export type Insert = {
  // Cle de la table `Ressources`, resolue par A8 comme celles des `besoins`.
  cle: string;
  // Debut de l'insert, designe en clair par A6 : "phrase 7". Comme
  // `da.accent`, c'est du texte libre parce que c'est la seule chose qu'A6
  // connaisse — les secondes n'existent qu'apres la voix off.
  debut?: string;
  // Debut resolu en secondes depuis le debut de la scene, ecrit par
  // construire_props.py. C'est ce que lit le rendu ; `debut` ne l'interesse pas.
  debut_s?: number;
  // Duree de l'insert. A defaut, la duree du clip, puis 3 s. Toujours bornee
  // par la fin de la scene au montage.
  duree_s?: number;
  // Facteur de zoom atteint en fin d'insert (defaut 1.12). L'insert se
  // rapproche : c'est sa raison d'etre, pas une decoration.
  zoom?: number;
  // Part de la largeur d'ecran occupee par le cadre (0 a 1). A defaut, 0,62
  // en paysage et 0,86 en vertical — assez grand pour se lire, assez petit
  // pour qu'on voie la scene continuer dessous.
  part?: number;
  // Mot ou chiffre sous le cadre. Jamais la phrase prononcee : les
  // sous-titres la portent deja.
  legende?: string;
};

// Une scene du storyboard (05_storyboard.md), telle que la produit le
// Designer (A6) et que la consomme le Monteur (A7). `composant` doit
// exister dans components/registry.ts, sinon c'est un nouveau composant a
// creer (§8, regle du Monteur).
export type Scene = {
  id: string;
  composant: string;
  duree_s: number;
  params: Record<string, unknown>;
  // La phrase prononcee pendant la scene. Lisibilite du storyboard et des
  // sequences dans Remotion Studio ; jamais affichee a l'ecran, les
  // sous-titres la portent deja.
  phrase?: string;
  // Numeros de ligne de 03_script_tts.txt couvertes par la scene (§8). A6
  // fusionne ces listes quand il fusionne des scenes ; c'est ce qui permet le
  // recalage sur 04_phrases.json sans exiger une scene par phrase.
  phrases?: number[];
  // Duree estimee par A6 avant recalage sur l'audio, gardee pour comparer.
  duree_s_storyboard?: number;
  // Instant de l'accent demande par `da.accent`, en secondes depuis le debut
  // de la scene. Resolu au montage par construire_props.py : A6 designe une
  // phrase, le timestamp reel vient de 04_phrases.json. Absent quand la DA ne
  // demande pas d'accent ponctuel.
  pulsation_s?: number;
  // Assets a aller chercher pour cette scene (E5b). Ecrits par A6, resolus
  // par A8 ; inertes au rendu, ou seule compte `Ressources`.
  besoins?: Besoin[];
  // Instants de video reelle poses par-dessus la scene animee (§8). Declares
  // par A6, resolus en secondes par construire_props.py, rendus par
  // `InsertFootage`. Un insert ne change ni `duree_s` ni `phrases` : c'est un
  // detail *dans* la scene, donc le recalage n'en sait rien et n'a pas a en
  // savoir quelque chose.
  inserts?: Insert[];
  // Transition vers la scene suivante. Absente = valeur par defaut de la
  // charte. Ignoree sur la derniere scene.
  transition_sortie?: TransitionSortie;
  // A6 n'a pas encore tranche le composant / les params / la DA.
  a_completer?: boolean;
  // Direction artistique de la scene, decidee par A6 (§8). Optionnelle :
  // un storyboard produit avant la revue du 11/09/2026 n'en a pas.
  da?: DirectionArtistique;
};

// --- Ressources (E5b) -------------------------------------------------
// Ce qui manquait au systeme : un chemin pour qu'un pixel non dessine en SVG
// arrive a l'ecran. Avant, le seul asset du pipeline etait 04_voixoff.wav,
// copie en dur dans public/ par construire_props.py ; aucun composant
// n'utilisait <Img> ni <OffthreadVideo>. Resultat : tout ce qui s'affichait
// devait d'abord etre dessine a la main dans un .tsx, ce qui rendait la
// variete structurellement plus chere que la repetition.

export type TypeRessource = 'logo' | 'capture' | 'image' | 'broll';

/** Un asset resolu par A8, pret a etre affiche. */
export type Ressource = {
  type: TypeRessource;
  // URL servie par le bundle de rendu (prefixe /public/), pas un chemin
  // disque : un chemin absolu ou une URI file:// echouent tous les deux.
  src: string;
  largeur_px?: number;
  hauteur_px?: number;
  // Broll uniquement : duree du clip. Sert a le boucler quand le recalage
  // sur l'audio rend la scene plus longue que lui — sinon la fin du plan
  // est un ecran noir, et le recalage peut allonger une scene bien apres
  // qu'A8 a choisi le clip.
  duree_s?: number;
  // D'ou vient le fichier, et sous quelle licence. Trace parce qu'on publie
  // sur YouTube : une capture d'ecran, un logo CC0 et une image generee
  // n'engagent pas la meme chose.
  provenance?: string;
  licence?: string;
};

/** Table des ressources de la video, indexee par la cle choisie par A6. */
export type Ressources = Record<string, Ressource>;

/**
 * Un besoin declare par A6 dans le storyboard, resolu par A8 (E5b) en une
 * entree de `Ressources` portant la meme `cle`.
 *
 * C'est le renversement de contrat : A6 ne nomme plus une cle de composant
 * opaque (`scene="context7_demo"`), il declare **ce qu'il faut aller
 * chercher**. Deux scenes voisines qui declarent deux URL differentes ne
 * peuvent pas rendre la meme image — ce que cinq variantes de
 * ConceptCutaway, elles, faisaient.
 */
export type Besoin = {
  cle: string;
  type: TypeRessource;
  // Logo : le nom de la marque (resolu sur Simple Icons).
  // Image / broll : la requete en clair.
  requete?: string;
  // Capture : la page a photographier.
  url?: string;
  // Broll : duree minimale utile, pour ecarter les clips trop courts.
  duree_min_s?: number;
  // Une scene peut se rendre sans (repli sur le texte seul).
  obligatoire?: boolean;
};

// Un mot avec ses timestamps, tel que produit par faster-whisper sur
// 04_timestamps.json (§7.2, cellule 7).
export type MotHorodate = {
  mot: string;
  debut_s: number;
  fin_s: number;
};

export type VideoProps = {
  charte: CharteTokens;
  scenes: Scene[];
  mots: MotHorodate[];
  // Table des assets resolus par A8, passee a tous les composants comme
  // `charte` : un composant recoit une **cle** dans ses params et lit le
  // fichier ici. Absente sur une video montee avant E5b.
  ressources?: Ressources;
  audioSrc?: string;
  // Duree reelle de 04_voixoff.wav. La composition ne doit jamais durer
  // moins que l'audio, sinon la voix off est coupee en fin de video.
  duree_audio_s?: number;
};
