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
  format: {largeur_px: number; hauteur_px: number; fps: number};
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
};
