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
    format: {largeur_px: 1080, hauteur_px: 1920, fps: FPS},
  },
  scenes: [
    {id: 's1', composant: 'TitleCard', duree_s: 3, params: {texte: 'What changed this week', sousTitre: 'AI news, decoded'}},
  ],
  mots: [
    {mot: 'What', debut_s: 0.2, fin_s: 0.4},
    {mot: 'changed', debut_s: 0.4, fin_s: 0.7},
    {mot: 'this', debut_s: 0.7, fin_s: 0.9},
    {mot: 'week', debut_s: 0.9, fin_s: 1.3},
  ],
};

export const RemotionRoot: React.FC = () => {
  return (
    <Composition
      id="Video"
      component={Video}
      fps={FPS}
      width={1080}
      height={1920}
      durationInFrames={dureeTotaleFrames(PROPS_PAR_DEFAUT.scenes, FPS)}
      defaultProps={PROPS_PAR_DEFAUT}
      calculateMetadata={async ({props}) => ({
        durationInFrames: dureeTotaleFrames(props.scenes, FPS),
      })}
    />
  );
};
