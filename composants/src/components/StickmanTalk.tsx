import React from 'react';
import {AbsoluteFill, useCurrentFrame, useVideoConfig} from 'remotion';
import type {CharteTokens, DirectionArtistique} from '../types';
import {Stickman} from './Stickman';
import type {StickmanPose} from './Stickman';
import {retardSecondaireFrames, styleContinu, styleEntree} from '../animation';

export type StickmanTalkParams = {
  pose: 'intro' | 'lean_in' | 'outro';
  label?: string;
};

type Props = StickmanTalkParams & {charte: CharteTokens; da?: DirectionArtistique};

// Trois poses distinctes. `intro` et `outro` rendaient la meme image avant
// (toutes deux mappees sur 'wave') : A6 croyait choisir la ou il n'avait
// pas le choix.
const POSE_VERS_STICKMAN: Record<StickmanTalkParams['pose'], StickmanPose> = {
  intro: 'wave',
  // `lean_in` pointait sur 'point' (bras tendu a l'horizontale), et la pose
  // 'lean' — la seule qui porte un vrai basculement du buste, 7 degres —
  // n'etait atteignable par personne. Meme defaut que `intro`/`outro`
  // corrige juste au-dessus : A6 croyait choisir une pose la ou il n'avait
  // pas le choix. Le storyboard de 2026-09-11_v01 demande `lean_in` sur s9.
  lean_in: 'lean',
  outro: 'open',
};

// Stickman plein cadre qui s'adresse a la camera (§8). Le personnage
// occupait un cinquieme de la hauteur sur un fond noir vide : il prend
// desormais la moitie du cadre, sur un halo qui donne de la profondeur.
export const StickmanTalk: React.FC<Props> = ({pose, label, charte, da}) => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();

  const entree = styleEntree(frame, fps, charte, da);
  const continu = styleContinu(frame, fps, charte, da);
  // Le halo suit le personnage en retrait (parallaxe, regle 7).
  const haloEntree = styleEntree(frame, fps, charte, da, 1);
  const retard = retardSecondaireFrames(charte, fps);

  return (
    <AbsoluteFill style={{backgroundColor: charte.couleurs.fond, overflow: 'hidden'}}>
      <AbsoluteFill
        style={{
          ...haloEntree,
          background: `radial-gradient(circle at 50% 46%, ${charte.couleurs.accent}22 0%, transparent 62%)`,
        }}
      />
      <AbsoluteFill style={{alignItems: 'center', justifyContent: 'center', paddingBottom: 260}}>
        <div style={{...entree, textAlign: 'center'}}>
          <div style={continu}>
            <Stickman
              color={charte.couleurs.accent}
              scale={3.1}
              pose={POSE_VERS_STICKMAN[pose]}
              phase={(frame / (fps * 2.4)) % 1}
              phaseGeste={((frame - retard) / (fps * 1.3)) % 1}
            />
          </div>
          {label ? (
            <div
              style={{
                ...styleEntree(frame, fps, charte, da, 2),
                marginTop: 56,
                color: charte.couleurs.texte_principal,
                fontFamily: charte.typographie.sous_titres.famille,
                fontSize: 54,
                fontWeight: 700,
                letterSpacing: 3,
                textTransform: 'uppercase',
              }}
            >
              {label}
            </div>
          ) : null}
        </div>
      </AbsoluteFill>
    </AbsoluteFill>
  );
};
