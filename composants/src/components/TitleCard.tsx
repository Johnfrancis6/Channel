import React from 'react';
import {AbsoluteFill, interpolate, useCurrentFrame, useVideoConfig} from 'remotion';
import type {CharteTokens} from '../types';

export type TitleCardParams = {
  texte: string;
  sousTitre?: string;
};

type Props = TitleCardParams & {charte: CharteTokens};

// Premier composant reutilisable de la bibliotheque (§8) : une frame
// d'accroche plein cadre, texte anime en fondu/translation, entierement
// pilotee par les tokens de charte (couleurs, typographie).
export const TitleCard: React.FC<Props> = ({texte, sousTitre, charte}) => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const dureeEntree = Math.max(1, Math.round(charte.rythme.duree_transition_s * fps));

  const opacite = interpolate(frame, [0, dureeEntree], [0, 1], {extrapolateRight: 'clamp'});
  const decalageY = interpolate(frame, [0, dureeEntree], [24, 0], {extrapolateRight: 'clamp'});

  return (
    <AbsoluteFill
      style={{
        backgroundColor: charte.couleurs.fond,
        alignItems: 'center',
        justifyContent: 'center',
        padding: 80,
      }}
    >
      <div
        style={{
          opacity: opacite,
          transform: `translateY(${decalageY}px)`,
          textAlign: 'center',
          fontFamily: charte.typographie.sous_titres.famille,
        }}
      >
        <div
          style={{
            color: charte.couleurs.texte_principal,
            fontSize: 88,
            fontWeight: 700,
            lineHeight: 1.1,
          }}
        >
          {texte}
        </div>
        {sousTitre ? (
          <div style={{color: charte.couleurs.accent, fontSize: 44, marginTop: 24}}>{sousTitre}</div>
        ) : null}
      </div>
    </AbsoluteFill>
  );
};
