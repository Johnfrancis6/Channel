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

  const indexActif = mots.findIndex((m) => tSecondes >= m.debut_s && tSecondes < m.fin_s);
  if (indexActif === -1) {
    return null;
  }

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
              color: debut + i === indexActif ? charte.couleurs.accent : charte.couleurs.texte_principal,
            }}
          >
            {m.mot}
          </span>
        ))}
      </div>
    </AbsoluteFill>
  );
};
