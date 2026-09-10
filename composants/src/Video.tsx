import React from 'react';
import {AbsoluteFill, Audio, Sequence, useVideoConfig} from 'remotion';
import {REGISTRE} from './components/registry';
import {Subtitles} from './components/Subtitles';
import type {VideoProps} from './types';

const ComposantInconnu: React.FC<{nom: string}> = ({nom}) => (
  <AbsoluteFill style={{backgroundColor: '#B00020', alignItems: 'center', justifyContent: 'center'}}>
    <div style={{color: 'white', fontSize: 48, textAlign: 'center', padding: 40}}>
      Composant inconnu : "{nom}"
      {'\n'}(a ajouter a composants/src/components/registry.ts)
    </div>
  </AbsoluteFill>
);

export const Video: React.FC<VideoProps> = ({charte, scenes, mots, audioSrc}) => {
  const {fps} = useVideoConfig();
  let frameCourant = 0;

  return (
    <AbsoluteFill style={{backgroundColor: charte.couleurs.fond}}>
      {audioSrc ? <Audio src={audioSrc} /> : null}
      {scenes.map((scene) => {
        const dureeFrames = Math.max(1, Math.round(scene.duree_s * fps));
        const debut = frameCourant;
        frameCourant += dureeFrames;
        const Composant = REGISTRE[scene.composant];

        return (
          <Sequence key={scene.id} from={debut} durationInFrames={dureeFrames} name={scene.id}>
            {Composant ? (
              <Composant charte={charte} {...scene.params} />
            ) : (
              <ComposantInconnu nom={scene.composant} />
            )}
          </Sequence>
        );
      })}
      <Subtitles mots={mots} charte={charte} />
    </AbsoluteFill>
  );
};

export function dureeTotaleFrames(scenes: VideoProps['scenes'], fps: number): number {
  return scenes.reduce((total, s) => total + Math.max(1, Math.round(s.duree_s * fps)), 0);
}
