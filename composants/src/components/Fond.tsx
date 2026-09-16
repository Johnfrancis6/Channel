import React from 'react';
import {AbsoluteFill, useCurrentFrame, useVideoConfig} from 'remotion';
import type {CharteTokens, DirectionArtistique} from '../types';
import {parallaxe, styleContinu} from '../animation';

/**
 * Le fond de la video, une fois pour toutes.
 *
 * Avant le 16/09/2026, cinq composants recopiaient le meme bloc « aplat +
 * halo radial », avec trois alphas differents (`1f`, `1a`, `24`) sans qu'aucune
 * regle ne dise lequel etait le bon. Et comme chaque composant peignait son
 * propre fond opaque, le fond **repartait de zero a chaque scene** : onze
 * fonds identiques mais discontinus, la ou une video a un fond, point.
 *
 * Il est rendu une seule fois, hors de la `TransitionSeries` : il ne
 * transitionne donc pas avec les scenes. C'est voulu — un fond qui se fond
 * dans lui-meme a chaque coupe est un fond qui clignote.
 *
 * Trois choses en plus de l'aplat, et la troisieme n'est pas cosmetique :
 *
 * 1. **Un halo** en degrade radial, qui derive lentement en parallaxe.
 * 2. **Une vignette**, qui ramene l'oeil au centre en 1080x1920.
 * 3. **Un grain**, qui casse le banding. Sur un `#0B0F14` avec degrade, le
 *    rendu produisait des paliers visibles dans les noirs. Le grain les
 *    dissout en les bruitant — c'est la meme correction qui rend le fond
 *    moins plat a l'oeil.
 */

// Tuile de bruit, generee une fois par le moteur SVG de Chromium puis
// repetee : une turbulence plein cadre en 1080x1920 serait recalculee a
// chaque frame pour le meme resultat.
const TUILE = 180;
const GRAIN = `data:image/svg+xml;utf8,${encodeURIComponent(
  `<svg xmlns="http://www.w3.org/2000/svg" width="${TUILE}" height="${TUILE}">` +
    `<filter id="g"><feTurbulence type="fractalNoise" baseFrequency="0.85" numOctaves="3" stitchTiles="stitch"/>` +
    `<feColorMatrix type="saturate" values="0"/></filter>` +
    `<rect width="100%" height="100%" filter="url(#g)"/></svg>`,
)}`;

type Props = {
  charte: CharteTokens;
  da?: DirectionArtistique;
  // Deplace le halo d'une scene a l'autre : un halo toujours au meme endroit
  // redevient une texture de fond qu'on cesse de voir.
  indexScene?: number;
};

// Trois ancrages, parcourus en boucle. Deterministe : deux rendus de la meme
// video doivent donner la meme image.
const ANCRAGES = [
  {x: 50, y: 38},
  {x: 38, y: 46},
  {x: 62, y: 42},
];

export const Fond: React.FC<Props> = ({charte, da, indexScene = 0}) => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const ancrage = ANCRAGES[indexScene % ANCRAGES.length];

  // Regle 7 du §8 : le fond suit le premier plan, en retrait. `parallaxe()`
  // rend le facteur de retrait (0,4 par defaut) ; passe en attenuation, il
  // fait deriver le halo a 40 % de l'amplitude du contenu. Sans lui, fond et
  // contenu bougeaient ensemble — donc ne bougeaient pas l'un par rapport a
  // l'autre, donc ne creaient aucune profondeur.
  const derive = styleContinu(frame, fps, charte, da, parallaxe(charte, 1));
  // Sur-dimensionne : un calque translate a la taille exacte du cadre
  // decouvrirait un bord.
  const transform = `${derive.transform ?? ''} scale(1.08)`.trim();

  return (
    <AbsoluteFill style={{backgroundColor: charte.couleurs.fond}}>
      <AbsoluteFill
        style={{
          transform,
          background: `radial-gradient(ellipse 70% 45% at ${ancrage.x}% ${ancrage.y}%, ${charte.couleurs.accent}30 0%, transparent 68%)`,
        }}
      />
      <AbsoluteFill
        style={{
          background: `radial-gradient(ellipse 85% 65% at 50% 45%, transparent 48%, rgba(0,0,0,0.42) 100%)`,
        }}
      />
      <AbsoluteFill
        style={{
          backgroundImage: `url("${GRAIN}")`,
          backgroundRepeat: 'repeat',
          backgroundSize: `${TUILE}px ${TUILE}px`,
          // Assez pour dissoudre un palier, pas assez pour se lire comme une
          // texture. Au-dela de ~0,08 le grain devient un effet.
          opacity: 0.055,
          mixBlendMode: 'overlay',
        }}
      />
    </AbsoluteFill>
  );
};
