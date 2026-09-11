import React from 'react';
import {AbsoluteFill, useCurrentFrame, useVideoConfig} from 'remotion';
import type {CharteTokens, DirectionArtistique} from '../types';
import {styleContinu, styleEntree} from '../animation';

export type TitleCardParams = {
  texte: string;
  sousTitre?: string;
};

type Props = TitleCardParams & {charte: CharteTokens; da?: DirectionArtistique};

// Frame d'accroche plein cadre, entierement pilotee par les tokens de
// charte. Le titre, le filet et le sous-titre entrent en cascade (regle 3)
// plutot que d'un bloc : trois elements parfaitement synchrones lisent
// comme une diapositive, pas comme une animation.
export const TitleCard: React.FC<Props> = ({texte, sousTitre, charte, da}) => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const famille = charte.typographie.sous_titres.famille;

  return (
    <AbsoluteFill style={{backgroundColor: charte.couleurs.fond, overflow: 'hidden'}}>
      <AbsoluteFill
        style={{
          ...styleEntree(frame, fps, charte, da, 3),
          background: `radial-gradient(circle at 50% 38%, ${charte.couleurs.accent}1f 0%, transparent 58%)`,
        }}
      />
      <AbsoluteFill
        style={{alignItems: 'center', justifyContent: 'center', padding: 90, paddingBottom: 300}}
      >
        <div style={{...styleContinu(frame, fps, charte, da), textAlign: 'center', width: '100%'}}>
          <div
            style={{
              ...styleEntree(frame, fps, charte, da, 0),
              color: charte.couleurs.texte_principal,
              fontFamily: famille,
              fontSize: 104,
              fontWeight: 800,
              lineHeight: 1.08,
              letterSpacing: -1,
            }}
          >
            {texte}
          </div>
          <div
            style={{
              ...styleEntree(frame, fps, charte, da, 1),
              height: 8,
              width: 160,
              margin: '48px auto 0',
              borderRadius: 4,
              backgroundColor: charte.couleurs.accent,
            }}
          />
          {sousTitre ? (
            <div
              style={{
                ...styleEntree(frame, fps, charte, da, 2),
                color: charte.couleurs.accent_secondaire,
                fontFamily: famille,
                fontSize: 52,
                fontWeight: 600,
                marginTop: 48,
              }}
            >
              {sousTitre}
            </div>
          ) : null}
        </div>
      </AbsoluteFill>
    </AbsoluteFill>
  );
};
