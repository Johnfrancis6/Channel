import React from 'react';
import {AbsoluteFill, interpolate, useCurrentFrame, useVideoConfig} from 'remotion';
import type {CharteTokens} from '../types';
import {Stickman} from './Stickman';
import type {StickmanPose} from './Stickman';

export type StickmanTalkParams = {
  pose: 'intro' | 'lean_in' | 'outro';
  label?: string;
};

type Props = StickmanTalkParams & {charte: CharteTokens};

const POSE_VERS_STICKMAN: Record<StickmanTalkParams['pose'], StickmanPose> = {
  intro: 'wave',
  lean_in: 'lean',
  outro: 'wave',
};

// Stickman plein cadre qui s'adresse a la camera (intro, transition,
// cloture) — §8, cree par le Monteur pour 2026-09-11_v01.
export const StickmanTalk: React.FC<Props> = ({pose, label, charte}) => {
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
      }}
    >
      <div style={{opacity: opacite, transform: `translateY(${decalageY}px)`, textAlign: 'center'}}>
        <Stickman
          color={charte.couleurs.accent}
          scale={1.6}
          pose={POSE_VERS_STICKMAN[pose]}
          phase={(frame % fps) / fps}
        />
        {label ? (
          <div
            style={{
              marginTop: 32,
              color: charte.couleurs.texte_principal,
              fontFamily: charte.typographie.sous_titres.famille,
              fontSize: 48,
              fontWeight: 700,
              letterSpacing: 2,
              textTransform: 'uppercase',
            }}
          >
            {label}
          </div>
        ) : null}
      </div>
    </AbsoluteFill>
  );
};
