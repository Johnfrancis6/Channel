import {interpolate, spring, Easing} from 'remotion';
import type {CharteTokens, DirectionArtistique, MouvementDA, RythmeDA} from './types';

/**
 * Les huit regles du §8, implementees une fois pour tous les composants.
 *
 * Avant ce module, chaque composant refaisait le meme geste a la main :
 * deux `interpolate()` lineaires, opacite 0->1 et translateY 24->0, sur
 * 0,3 s — puis plus rien pendant le reste de la scene. Trois composants,
 * un seul geste, recopie. Sur une scene de 16 s, ca donnait 0,3 s
 * d'animation et 15,7 s d'image fixe.
 *
 * `spring()` n'etait appele nulle part, alors que c'est la primitive qui
 * donne l'acceleration puis la pose — ce que l'oeil lit comme naturel.
 */

const VALEURS_PAR_DEFAUT = {
  decalage_entree_ms: 80,
  variation_vitesse: 0.15,
  mouvement_secondaire_retard_ms: 120,
  anticipation_px: 10,
  parallaxe_fond: 0.4,
};

function naturel(charte: CharteTokens) {
  return {...VALEURS_PAR_DEFAUT, ...(charte.animation?.naturel ?? {})};
}

// `pose` laisse respirer, `punch` coupe sec. Le rythme module la duree
// d'entree, pas la duree de la scene.
const FACTEUR_RYTHME: Record<RythmeDA, number> = {
  pose: 1.5,
  standard: 1,
  punch: 0.5,
};

export function dureeEntreeFrames(charte: CharteTokens, fps: number, da?: DirectionArtistique): number {
  const base = charte.animation?.duree_entree_s ?? charte.rythme.duree_transition_s;
  const facteur = FACTEUR_RYTHME[da?.rythme ?? 'standard'] ?? 1;
  return Math.max(1, Math.round(base * facteur * fps));
}

/**
 * Decalage d'entree entre elements d'un meme groupe (regle 3), avec une
 * variation de vitesse (regle 4) : deux elements exactement synchrones
 * lisent comme un bloc rigide, pas comme un groupe d'objets.
 */
export function decalageFrames(charte: CharteTokens, fps: number, index: number): number {
  return Math.round((naturel(charte).decalage_entree_ms / 1000) * fps * index);
}

export function facteurVitesse(charte: CharteTokens, index: number): number {
  const amplitude = naturel(charte).variation_vitesse;
  // Deterministe : meme index, meme facteur — un rendu doit etre reproductible.
  const oscillation = Math.sin(index * 1.7) * amplitude;
  return 1 + oscillation;
}

/**
 * Progression 0 -> 1 de l'entree. `spring` par defaut (regle 1) ; jamais de
 * rampe lineaire, que l'oeil repere immediatement comme mecanique.
 */
export function progressionEntree(
  frame: number,
  fps: number,
  charte: CharteTokens,
  da?: DirectionArtistique,
  index = 0,
): number {
  const depart = decalageFrames(charte, fps, index);
  const duree = Math.max(1, Math.round(dureeEntreeFrames(charte, fps, da) * facteurVitesse(charte, index)));
  const local = frame - depart;

  if (da?.technique === 'statique') {
    return local >= 0 ? 1 : 0;
  }
  if (da?.technique === 'interpolate') {
    // Regle 2 : meme ici, on sort par une courbe qui se pose, jamais net.
    return interpolate(local, [0, duree], [0, 1], {
      extrapolateLeft: 'clamp',
      extrapolateRight: 'clamp',
      easing: Easing.out(Easing.cubic),
    });
  }
  return spring({
    frame: local,
    fps,
    // Amorti : il se pose sans rebondir de facon caricaturale.
    config: {damping: 14, mass: 0.6, stiffness: 110},
    durationInFrames: duree,
  });
}

/** Style d'entree d'un element, selon `da.mouvement` (regle 1, 2, 6). */
export function styleEntree(
  frame: number,
  fps: number,
  charte: CharteTokens,
  da?: DirectionArtistique,
  index = 0,
): React.CSSProperties {
  const p = progressionEntree(frame, fps, charte, da, index);
  const mouvement: MouvementDA = da?.mouvement ?? 'entree_par_le_bas';
  const {anticipation_px} = naturel(charte);

  if (mouvement === 'aucun') {
    return {opacity: 1};
  }
  if (mouvement === 'fondu') {
    return {opacity: p};
  }
  if (mouvement === 'glissement_lateral') {
    // Sens alterne d'un element a l'autre : un groupe qui glisse tout du
    // meme cote redevient un bloc.
    const sens = index % 2 === 0 ? 1 : -1;
    return {opacity: p, transform: `translateX(${(1 - p) * 120 * sens}px)`};
  }
  if (mouvement === 'zoom_lent' || mouvement === 'apparition_sequencee') {
    return {opacity: p, transform: `scale(${interpolate(p, [0, 1], [0.92, 1])})`};
  }
  // entree_par_le_bas, avec anticipation (regle 6) : un leger depassement
  // vers le bas avant de remonter se pose.
  const y = interpolate(p, [0, 1], [56 + anticipation_px, 0]);
  return {opacity: p, transform: `translateY(${y}px)`};
}

/**
 * Mouvement continu sur toute la scene (regle 8 : rien n'est jamais
 * totalement immobile). C'est ce qui manquait le plus : les composants
 * s'animaient 0,3 s puis figeaient.
 */
export function styleContinu(
  frame: number,
  fps: number,
  charte: CharteTokens,
  da?: DirectionArtistique,
  // Attenuation 0..1 du mouvement de fond. Sert la premiere regle de
  // `charte.json > animation.regles` : **un seul mouvement dominant par
  // scene**. Quand un element prend la main (une pulsation d'accent, par
  // exemple), le reste se calme au lieu de continuer a deriver — sinon deux
  // mouvements se disputent l'oeil et l'accent ne se lit plus.
  attenuation = 1,
): React.CSSProperties {
  const k = Math.max(0, Math.min(1, attenuation));
  const t = frame / fps;
  if (da?.mouvement === 'zoom_lent') {
    // Derive lente sur toute la scene : imperceptible image par image,
    // evidente a la lecture.
    return {transform: `scale(${1 + t * 0.012 * k})`};
  }
  const w = charte.animation?.wobble;
  if (!w?.actif) {
    return {};
  }
  // Deux sinusoides de periodes premieres entre elles : le mouvement ne se
  // repete pas a l'identique, contrairement a une oscillation d'exactement
  // une seconde, qui s'entend comme un metronome.
  const a = w.amplitude_px * 0.35 * k;
  const x = Math.sin((t / w.periode_s) * Math.PI * 2) * a;
  const y = Math.sin((t / (w.periode_s * 1.618)) * Math.PI * 2) * a * 0.6;
  return {transform: `translate(${x}px, ${y}px)`};
}

/**
 * Pulsation ponctuelle, declenchee a une frame precise : 0 -> 1 -> 0.
 *
 * C'est une **echelle**, pas un wobble : `charte.json > animation.wobble`
 * reserve l'oscillation aux traces a la main (`cible: "trace_main"`), jamais
 * au texte ni aux boites. Et c'est un ressort, pas une rampe (regle 1) qui
 * repart en douceur au lieu de s'arreter net (regle 2).
 *
 * `frameDeclenchement` est resolu au montage a partir du timestamp reel de
 * la phrase designee par `da.accent` (04_phrases.json) : l'accent tombe sur
 * le mot prononce, pas au milieu chronometrique de la scene.
 */
export function pulsation(frame: number, fps: number, frameDeclenchement?: number): number {
  if (frameDeclenchement === undefined || frameDeclenchement === null) {
    return 0;
  }
  const local = frame - frameDeclenchement;
  if (local < 0) {
    return 0;
  }
  const montee = Math.max(1, Math.round(fps * 0.22));
  const retour = Math.max(1, Math.round(fps * 0.5));
  const monte = spring({
    frame: local,
    fps,
    config: {damping: 12, mass: 0.5, stiffness: 200},
    durationInFrames: montee,
  });
  // Le retour est plus long et plus amorti que la montee : un accent frappe
  // vite et se repose lentement. Symetrique, il ressemblerait a un clignotement.
  const descend =
    local < montee
      ? 0
      : spring({
          frame: local - montee,
          fps,
          config: {damping: 18, mass: 0.9, stiffness: 90},
          durationInFrames: retour,
        });
  return Math.max(0, monte - descend);
}

/** Profondeur (regle 7) : le fond suit le premier plan, en retrait. */
export function parallaxe(charte: CharteTokens, deplacementPx: number): number {
  return deplacementPx * naturel(charte).parallaxe_fond;
}

/** Mouvement secondaire (regle 5) : ce qui suit l'element principal. */
export function retardSecondaireFrames(charte: CharteTokens, fps: number): number {
  return Math.round((naturel(charte).mouvement_secondaire_retard_ms / 1000) * fps);
}

/** Sortie qui ne coupe pas net (regle 2), sur les dernieres frames. */
export function opaciteSortie(frame: number, dureeScene: number, fps: number): number {
  const sortie = Math.round(fps * 0.25);
  return interpolate(frame, [dureeScene - sortie, dureeScene], [1, 0], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
    easing: Easing.in(Easing.cubic),
  });
}

/**
 * Punch-in : la camera se rapproche lentement sur toute la scene.
 *
 * Different de `styleContinu` : celui-ci derive pour que l'image ne soit pas
 * morte (regle 8), celui-la est un **mouvement de plan**. Sur une capture
 * d'ecran ou un b-roll, c'est ce qui distingue un plan d'une vignette collee
 * au milieu du cadre.
 *
 * `da.rythme` en decide l'ampleur : `pose` respire a peine, `punch` entre
 * franchement. Le sens s'inverse une scene sur deux (`index`) — trois plans
 * d'affilee qui se rapprochent au meme rythme redeviennent un seul geste,
 * pour la meme raison que le glissement lateral alterne son sens.
 */
export function punchIn(
  frame: number,
  fps: number,
  dureeScene: number,
  da?: DirectionArtistique,
  index = 0,
): React.CSSProperties {
  const AMPLEUR: Record<RythmeDA, number> = {pose: 0.03, standard: 0.06, punch: 0.10};
  const ampleur = AMPLEUR[da?.rythme ?? 'standard'] ?? 0.06;
  // Un plan qui s'eloigne est aussi un plan : alterner evite que chaque
  // capture de la video fasse exactement le meme geste.
  const sens = index % 2 === 0 ? 1 : -1;
  const p = interpolate(frame, [0, Math.max(1, dureeScene)], [0, 1], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
    // Lineaire a dessein : un mouvement de camera lent qui ralentit en fin
    // de plan se lit comme un ratage de rendu, pas comme une intention.
    easing: Easing.linear,
  });
  const depart = sens === 1 ? 1 : 1 + ampleur;
  return {transform: `scale(${depart + sens * ampleur * p})`};
}
