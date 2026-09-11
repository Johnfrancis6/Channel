export type CharteTokens = {
  couleurs: {
    fond: string;
    texte_principal: string;
    accent: string;
    accent_secondaire: string;
  };
  typographie: {
    sous_titres: {famille: string; taille_px: number; graisse: string};
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

export type AnimationTokens = {
  easing_entree?: string;
  easing_transition?: string;
  duree_entree_s?: number;
  technique_defaut?: TechniqueDA;
  wobble?: {actif: boolean; amplitude_px: number; periode_s: number; cible?: string};
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

export type TechniqueDA = 'spring' | 'interpolate' | 'lottie' | 'statique';

export type DirectionArtistique = {
  mouvement: MouvementDA;
  rythme: RythmeDA;
  technique: TechniqueDA;
  // Ce que la scene doit mettre en avant, en clair (ex. "le chiffre 10x").
  accent?: string;
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
  // Duree estimee par A6 avant recalage sur l'audio, gardee pour comparer.
  duree_s_storyboard?: number;
  // A6 n'a pas encore tranche le composant / les params / la DA.
  a_completer?: boolean;
  // Direction artistique de la scene, decidee par A6 (§8). Optionnelle :
  // un storyboard produit avant la revue du 11/09/2026 n'en a pas.
  da?: DirectionArtistique;
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
  audioSrc?: string;
  // Duree reelle de 04_voixoff.wav. La composition ne doit jamais durer
  // moins que l'audio, sinon la voix off est coupee en fin de video.
  duree_audio_s?: number;
};
