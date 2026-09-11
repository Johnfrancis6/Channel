import React from 'react';
import {AbsoluteFill, Audio, Sequence, useVideoConfig} from 'remotion';
import {REGISTRE} from './components/registry';
import {Subtitles} from './components/Subtitles';
import type {Scene, VideoProps} from './types';

const ComposantInconnu: React.FC<{nom: string}> = ({nom}) => (
  <AbsoluteFill style={{backgroundColor: '#B00020', alignItems: 'center', justifyContent: 'center'}}>
    <div style={{color: 'white', fontSize: 48, textAlign: 'center', padding: 40}}>
      Composant inconnu : "{nom}"
      {'\n'}(a ajouter a composants/src/components/registry.ts)
    </div>
  </AbsoluteFill>
);

function framesDeScene(scene: Scene, fps: number): number {
  return Math.max(1, Math.round(scene.duree_s * fps));
}

// Duree de la composition : la plus longue des deux horloges. Les durees de
// scenes sont recalees sur l'audio par construire_props.py (04_phrases.json),
// mais si ce recalage n'a pas eu lieu — storyboard d'avant la revue du
// 11/09/2026, phrases et scenes en nombres differents — la somme des scenes
// peut etre plus courte que la voix off, qui serait alors coupee net.
export function dureeTotaleFrames(
  scenes: VideoProps['scenes'],
  fps: number,
  dureeAudioS?: number,
): number {
  const framesScenes = scenes.reduce((total, s) => total + framesDeScene(s, fps), 0);
  const framesAudio = dureeAudioS ? Math.ceil(dureeAudioS * fps) : 0;
  return Math.max(1, framesScenes, framesAudio);
}

// `duree_audio_s` n'est pas lu ici : il sert a calculateMetadata (Root.tsx),
// qui fixe durationInFrames, relu ci-dessous via useVideoConfig().
export const Video: React.FC<VideoProps> = ({charte, scenes, mots, audioSrc}) => {
  const {fps, durationInFrames} = useVideoConfig();

  // La derniere scene absorbe le reliquat : sans ca, un audio plus long que
  // les scenes se termine sur un ecran vide (seuls les sous-titres restent).
  const framesScenes = scenes.map((s) => framesDeScene(s, fps));
  const totalScenes = framesScenes.reduce((a, b) => a + b, 0);
  const reliquat = Math.max(0, durationInFrames - totalScenes);
  if (framesScenes.length > 0) {
    framesScenes[framesScenes.length - 1] += reliquat;
  }

  let frameCourant = 0;

  return (
    <AbsoluteFill style={{backgroundColor: charte.couleurs.fond}}>
      {audioSrc ? <Audio src={audioSrc} /> : null}
      {scenes.map((scene, i) => {
        const dureeFrames = framesScenes[i];
        const debut = frameCourant;
        frameCourant += dureeFrames;
        const Composant = REGISTRE[scene.composant];

        return (
          <Sequence key={scene.id} from={debut} durationInFrames={dureeFrames} name={scene.id}>
            {Composant ? (
              <Composant charte={charte} da={scene.da} {...scene.params} />
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
