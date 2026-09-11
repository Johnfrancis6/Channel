import React from 'react';
import {AbsoluteFill, useCurrentFrame, useVideoConfig} from 'remotion';
import type {CharteTokens, MotHorodate} from '../types';

type Props = {
  mots: MotHorodate[];
  charte: CharteTokens;
  // Nombre de mots affiches simultanement (fenetre glissante autour du mot actif).
  fenetre?: number;
};

// Sous-titres dynamiques cales sur 04_timestamps.json (§7.2, §8). Affiche
// une petite fenetre de mots autour de l'instant courant, avec le mot en
// cours de prononciation mis en avant.
export const Subtitles: React.FC<Props> = ({mots, charte, fenetre = 5}) => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const tSecondes = frame / fps;

  // Dernier mot commence a cet instant, pas seulement le mot en cours de
  // prononciation : entre deux mots il y a toujours un silence, et une
  // correspondance exacte (debut <= t < fin) faisait disparaitre les
  // sous-titres dans chacun de ces trous. En pratique ils clignotaient entre
  // chaque mot. On garde le groupe affiche pendant le silence, seule la mise
  // en avant du mot s'eteint.
  let indexActif = -1;
  for (let i = 0; i < mots.length; i++) {
    if (tSecondes >= mots[i].debut_s) {
      indexActif = i;
    } else {
      break;
    }
  }
  if (indexActif === -1) {
    return null;
  }
  const enCoursDePrononciation = tSecondes < mots[indexActif].fin_s;

  const debut = Math.max(0, indexActif - Math.floor(fenetre / 2));
  const fin = Math.min(mots.length, debut + fenetre);
  const groupe = mots.slice(debut, fin);

  return (
    <AbsoluteFill
      style={{
        alignItems: 'center',
        justifyContent: 'flex-end',
        paddingBottom: 220,
        pointerEvents: 'none',
      }}
    >
      <div
        style={{
          display: 'flex',
          flexWrap: 'wrap',
          justifyContent: 'center',
          maxWidth: '85%',
          gap: '0 0.4em',
          fontFamily: charte.typographie.sous_titres.famille,
          fontSize: charte.typographie.sous_titres.taille_px,
          fontWeight: charte.typographie.sous_titres.graisse === 'bold' ? 700 : 400,
          textShadow: '0 4px 16px rgba(0,0,0,0.6)',
        }}
      >
        {groupe.map((m, i) => (
          <span
            key={debut + i}
            style={{
              color:
                debut + i === indexActif && enCoursDePrononciation
                  ? charte.couleurs.accent
                  : charte.couleurs.texte_principal,
            }}
          >
            {m.mot}
          </span>
        ))}
      </div>
    </AbsoluteFill>
  );
};
