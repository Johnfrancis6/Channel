import React from 'react';
import {AbsoluteFill, Audio, useCurrentFrame, useVideoConfig} from 'remotion';
import {TransitionSeries, springTiming} from '@remotion/transitions';
import type {TransitionPresentation} from '@remotion/transitions';
import {fade} from '@remotion/transitions/fade';
import {slide} from '@remotion/transitions/slide';
import {wipe} from '@remotion/transitions/wipe';
import {iris} from '@remotion/transitions/iris';
import {opaciteSortie} from './animation';
import {REGISTRE} from './components/registry';
import {Fond} from './components/Fond';
import {Subtitles} from './components/Subtitles';
import type {Scene, TransitionSortie, VideoProps} from './types';

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
//
// Les transitions ne changent rien a ce total : chaque scene se voit allonger
// de la duree de la transition qui la suit, et `TransitionSeries` reprend
// exactement ce qu'elle a ajoute en faisant se chevaucher les deux plans.
// C'est ce qui permet d'avoir de vraies transitions **sans** decaler la voix
// off, qui est le seul point du pipeline ou le montage n'a pas droit a
// l'erreur.
export function dureeTotaleFrames(
  scenes: VideoProps['scenes'],
  fps: number,
  dureeAudioS?: number,
): number {
  const framesScenes = scenes.reduce((total, s) => total + framesDeScene(s, fps), 0);
  const framesAudio = dureeAudioS ? Math.ceil(dureeAudioS * fps) : 0;
  return Math.max(1, framesScenes, framesAudio);
}

/**
 * Transitions par defaut, quand A6 ne declare pas `transition_sortie`.
 *
 * L'ordre n'est pas decoratif : il applique la regle « jamais deux fois la
 * meme d'affilee » (file d'attente #20) et garde le fondu majoritaire. Une
 * video qui balaie a chaque coupe fatigue autant qu'une video qui coupe sec ;
 * le fondu est le repos, les autres sont la ponctuation.
 */
const ROTATION: TransitionSortie[] = ['fondu', 'glissement', 'fondu', 'balayage', 'fondu', 'iris'];

// `any` sur le parametre de la presentation, comme `REGISTRE` le fait pour
// les composants : chaque presentation a ses propres props (`SlideProps`,
// `WipeProps`…) et TypeScript refuse de les unifier. Le choix se fait sur un
// vocabulaire ferme, donc la verification utile est faite par `TransitionSortie`.
// eslint-disable-next-line @typescript-eslint/no-explicit-any
function presentation(
  nom: TransitionSortie,
  index: number,
  largeur: number,
  hauteur: number,
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
): TransitionPresentation<any> {
  // Le sens alterne d'une transition a l'autre, pour la meme raison que le
  // sens du punch-in : trois glissements dans le meme sens redeviennent un
  // seul geste.
  const pair = index % 2 === 0;
  switch (nom) {
    case 'glissement':
      return slide({direction: pair ? 'from-right' : 'from-left'});
    case 'balayage':
      return wipe({direction: pair ? 'from-bottom' : 'from-top'});
    case 'iris':
      return iris({width: largeur, height: hauteur});
    case 'fondu':
    default:
      return fade();
  }
}

/**
 * La derniere scene, qui n'a pas de transition apres elle, se terminait par
 * une coupure a l'image pleine. `opaciteSortie` existait depuis la revue du
 * 11/09 — la regle 2 du §8, « rien ne s'arrete net » — et n'avait jamais eu
 * un seul appelant.
 */
const SortieFinale: React.FC<{duree: number; children: React.ReactNode}> = ({duree, children}) => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  return <AbsoluteFill style={{opacity: opaciteSortie(frame, duree, fps)}}>{children}</AbsoluteFill>;
};

export const Video: React.FC<VideoProps> = ({charte, scenes, mots, ressources, audioSrc}) => {
  const {fps, durationInFrames, width, height} = useVideoConfig();

  // La derniere scene absorbe le reliquat : sans ca, un audio plus long que
  // les scenes se termine sur un ecran vide (seuls les sous-titres restent).
  const dureesScenes = scenes.map((s) => framesDeScene(s, fps));
  const totalScenes = dureesScenes.reduce((a, b) => a + b, 0);
  const reliquat = Math.max(0, durationInFrames - totalScenes);
  if (dureesScenes.length > 0) {
    dureesScenes[dureesScenes.length - 1] += reliquat;
  }

  const dureeDefaut = Math.max(1, Math.round((charte.rythme?.duree_transition_s ?? 0.3) * fps));

  // Duree de la transition qui SUIT chaque scene. Calculee a rebours : une
  // transition ne peut pas durer plus longtemps que la scene dans laquelle
  // elle entre, sinon `TransitionSeries` refuse la composition entiere. Une
  // scene de 0,2 s recalee sur une phrase courte ne doit pas faire echouer le
  // rendu de toute la video.
  const transitions: number[] = new Array(scenes.length).fill(0);
  for (let i = scenes.length - 2; i >= 0; i--) {
    if (scenes[i].transition_sortie === 'coupe') {
      transitions[i] = 0;
      continue;
    }
    const place = dureesScenes[i + 1] + transitions[i + 1] - 1;
    transitions[i] = Math.max(0, Math.min(dureeDefaut, place));
  }

  const elements: React.ReactNode[] = [];
  scenes.forEach((scene, i) => {
    const Composant = REGISTRE[scene.composant];
    const dernier = i === scenes.length - 1;
    const contenu = Composant ? (
      <Composant
        charte={charte}
        da={scene.da}
        // L'accent tombe a `pulsation_s` depuis le debut **audio** de la
        // scene, et c'est aussi la frame 0 de sa sequence : la transition
        // deborde sur la scene precedente, pas sur celle-ci. Le rattrapage
        // de 0,25 s qu'exigeait l'ancien chevauchement manuel n'a plus lieu
        // d'etre.
        pulsationFrame={
          scene.pulsation_s === undefined || scene.pulsation_s === null
            ? undefined
            : Math.round(scene.pulsation_s * fps)
        }
        ressources={ressources}
        indexScene={i}
        {...scene.params}
      />
    ) : (
      <ComposantInconnu nom={scene.composant} />
    );

    elements.push(
      <TransitionSeries.Sequence
        key={scene.id}
        durationInFrames={dureesScenes[i] + transitions[i]}
      >
        {dernier ? <SortieFinale duree={dureesScenes[i]}>{contenu}</SortieFinale> : contenu}
      </TransitionSeries.Sequence>,
    );

    if (!dernier && transitions[i] > 0) {
      const nom = scene.transition_sortie ?? ROTATION[i % ROTATION.length];
      elements.push(
        <TransitionSeries.Transition
          key={`${scene.id}-vers-${scenes[i + 1].id}`}
          presentation={presentation(nom, i, width, height)}
          // `damping: 200` : un ressort sans rebond. Une transition qui
          // rebondit attire l'oeil sur le raccord, alors que son travail est
          // de le faire oublier.
          timing={springTiming({config: {damping: 200}, durationInFrames: transitions[i]})}
        />,
      );
    }
  });

  return (
    <AbsoluteFill style={{backgroundColor: charte.couleurs.fond}}>
      {audioSrc ? <Audio src={audioSrc} /> : null}
      <Fond charte={charte} da={scenes[0]?.da} />
      <TransitionSeries>{elements}</TransitionSeries>
      <Subtitles mots={mots} charte={charte} />
    </AbsoluteFill>
  );
};
