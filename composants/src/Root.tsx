import React from 'react';
import {Composition} from 'remotion';
import {Video, dureeTotaleFrames} from './Video';
import type {VideoProps} from './types';

const FPS = 30;

// Props par defaut pour l'apercu dans Remotion Studio et pour le rendu de
// verification (aucune donnee de vraie video). Le Monteur (A7) passe ses
// propres props via --props=<json> a l'appel de `remotion render` (charte
// reelle, scenes du storyboard, mots de 04_timestamps.json).
const PROPS_PAR_DEFAUT: VideoProps = {
  charte: {
    couleurs: {
      fond: '#0B0F14',
      texte_principal: '#F5F7FA',
      accent: '#5B8CFF',
      accent_secondaire: '#FFD166',
    },
    typographie: {sous_titres: {famille: 'Arial, sans-serif', taille_px: 64, graisse: 'bold'}},
    rythme: {duree_transition_s: 0.3, easing: 'ease-in-out'},
    animation: {
      easing_entree: 'ease-out',
      easing_transition: 'ease-in-out',
      duree_entree_s: 0.3,
      technique_defaut: 'spring',
      wobble: {actif: true, amplitude_px: 6, periode_s: 1.2, cible: 'trace_main'},
      naturel: {
        decalage_entree_ms: 80,
        variation_vitesse: 0.15,
        mouvement_secondaire_retard_ms: 120,
        anticipation_px: 10,
        parallaxe_fond: 0.4,
      },
    },
    format: {largeur_px: 1080, hauteur_px: 1920, fps: FPS},
  },
  scenes: [
    {
      id: 's1',
      composant: 'TitleCard',
      duree_s: 3,
      params: {texte: 'What changed this week', sousTitre: 'AI news, decoded'},
      da: {mouvement: 'entree_par_le_bas', rythme: 'punch', technique: 'spring', accent: 'le titre'},
    },
  ],
  mots: [
    {mot: 'What', debut_s: 0.2, fin_s: 0.4},
    {mot: 'changed', debut_s: 0.4, fin_s: 0.7},
    {mot: 'this', debut_s: 0.7, fin_s: 0.9},
    {mot: 'week', debut_s: 0.9, fin_s: 1.3},
  ],
};

// Les dimensions viennent de `charte.json > format`, comme les couleurs et
// les durees : le format fait partie de la charte, et il n'y a aucune raison
// qu'il soit le seul token que le code ignore. Les valeurs en dur de
// <Composition> ne servent plus que d'amorce avant le premier appel a
// `calculateMetadata`, qui les remplace des que les props sont connues.
const {largeur_px: LARGEUR, hauteur_px: HAUTEUR} = PROPS_PAR_DEFAUT.charte.format;

export const RemotionRoot: React.FC = () => {
  return (
    <Composition
      id="Video"
      component={Video}
      fps={FPS}
      width={LARGEUR}
      height={HAUTEUR}
      durationInFrames={dureeTotaleFrames(PROPS_PAR_DEFAUT.scenes, FPS)}
      defaultProps={PROPS_PAR_DEFAUT}
      calculateMetadata={async ({props}) => {
        const format = props.charte?.format;
        const fps = format?.fps || FPS;
        return {
          width: format?.largeur_px || LARGEUR,
          height: format?.hauteur_px || HAUTEUR,
          fps,
          durationInFrames: dureeTotaleFrames(props.scenes, fps, props.duree_audio_s),
        };
      }}
    />
  );
};
