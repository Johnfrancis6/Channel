import React from 'react';
import {AbsoluteFill, useCurrentFrame, useVideoConfig} from 'remotion';
import {niveaux, style} from '../typographie';
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
  const typo = niveaux(charte);

  return (
    <AbsoluteFill style={{overflow: 'hidden'}}>
      <AbsoluteFill
        style={{alignItems: 'center', justifyContent: 'center', padding: 90, paddingBottom: 300}}
      >
        <div style={{...styleContinu(frame, fps, charte, da), textAlign: 'center', width: '100%'}}>
          <div
            style={{
              ...styleEntree(frame, fps, charte, da, 0),
              ...style(typo.titre),
              color: charte.couleurs.texte_principal,
              lineHeight: 1.08,
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
                ...style(typo.label),
                color: charte.couleurs.accent_secondaire,
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
