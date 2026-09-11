import React from 'react';

export type StickmanPose = 'neutral' | 'wave' | 'lean';

type Props = {
  color: string;
  scale?: number;
  pose?: StickmanPose;
  // Phase 0..1 pour l'idle/talk bobbing, pilotee par l'appelant (frame courante).
  phase?: number;
};

// Bonhomme allumettes minimaliste (SVG), personnage recurrent de la chaine
// (§8). Reutilise par StickmanTalk et ConceptCutaway pour rester coherent
// scene a scene.
export const Stickman: React.FC<Props> = ({color, scale = 1, pose = 'neutral', phase = 0}) => {
  const armLift = pose === 'wave' ? 40 : 0;
  const bob = Math.sin(phase * Math.PI * 2) * 4;
  const inclinaison = pose === 'lean' ? 8 : 0;

  return (
    <svg width={160 * scale} height={260 * scale} viewBox="0 0 160 260" style={{overflow: 'visible'}}>
      <g
        stroke={color}
        strokeWidth={6}
        strokeLinecap="round"
        fill="none"
        transform={`translate(0 ${bob}) skewX(${-inclinaison})`}
      >
        <circle cx={80} cy={40} r={28} />
        <line x1={80} y1={68} x2={80} y2={160} />
        <line x1={80} y1={160} x2={50} y2={230} />
        <line x1={80} y1={160} x2={110} y2={230} />
        <line x1={80} y1={100} x2={35} y2={140} />
        <line x1={80} y1={100} x2={125} y2={pose === 'wave' ? 100 - armLift : 140} />
      </g>
    </svg>
  );
};
