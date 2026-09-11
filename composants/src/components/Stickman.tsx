import React from 'react';

export type StickmanPose = 'neutral' | 'wave' | 'lean' | 'point' | 'open';

type Props = {
  color: string;
  scale?: number;
  pose?: StickmanPose;
  // Phase 0..1 du cycle de respiration, pilotee par l'appelant (frame courante).
  phase?: number;
  // Phase du geste, decalee par rapport a la respiration (mouvement
  // secondaire, regle 5) : un bras qui suit exactement le torse lit comme
  // une piece rigide.
  phaseGeste?: number;
  epaisseur?: number;
};

// Position du bras droit selon la pose, en degres autour de l'epaule.
// `intro` et `outro` rendaient exactement la meme image (meme empreinte
// md5) parce que les deux etaient mappees sur 'wave' : l'API annoncait
// trois poses, il y en avait deux. Elles sont distinctes desormais.
// Angles mesures depuis l'horizontale, positifs vers le bas. Ils sont
// choisis pour que le bras sorte du cadre de la tete : a -75 degres, le
// bras du salut montait presque a la verticale et disparaissait DANS le
// crane — invisible a l'image.
const ANGLE_BRAS: Record<StickmanPose, {droit: number; gauche: number}> = {
  neutral: {droit: 75, gauche: 75},  // le long du corps
  wave: {droit: -38, gauche: 75},    // salut : un bras leve, l'autre au repos
  lean: {droit: 25, gauche: 68},     // penche, bras vers l'avant
  point: {droit: -8, gauche: 75},    // designe, bras tendu a l'horizontale
  open: {droit: -30, gauche: -30},   // bras ouverts en V, conclusion
};

// Epaule assez basse pour que le bras leve degage la tete : plus haut, le
// trait partait du bord du crane et semblait en sortir.
const EPAULE = {x: 80, y: 118};
const LONGUEUR_BRAS = 62;
const RAYON_TETE = 28;

function extremite(angleDeg: number, sens: 1 | -1) {
  const rad = (angleDeg * Math.PI) / 180;
  return {
    x: EPAULE.x + sens * Math.cos(rad) * LONGUEUR_BRAS,
    y: EPAULE.y + Math.sin(rad) * LONGUEUR_BRAS,
  };
}

// Bonhomme allumettes, personnage recurrent de la chaine (§8). Reutilise
// par StickmanTalk et ConceptCutaway pour rester coherent scene a scene.
export const Stickman: React.FC<Props> = ({
  color,
  scale = 1,
  pose = 'neutral',
  phase = 0,
  phaseGeste,
  epaisseur = 7,
}) => {
  const angles = ANGLE_BRAS[pose] ?? ANGLE_BRAS.neutral;
  const gestePhase = phaseGeste ?? phase;

  // Respiration : le torse monte et descend, la tete suit avec un leger
  // retard. C'est le seul mouvement present quand la scene est "au repos",
  // et c'est ce qui evite l'image morte (regle 8).
  const souffle = Math.sin(phase * Math.PI * 2) * 3;
  const teteY = Math.sin((phase - 0.08) * Math.PI * 2) * 3.5;
  // Le cou part du BAS du cercle, pas d'une coordonnee fixe : la tete et le
  // torse respirant en dephase, un depart fixe faisait entrer le trait dans
  // le crane a chaque cycle.
  const basDeLaTete = 44 + teteY + RAYON_TETE;

  // Le bras anime bouge autour de sa position de pose, jamais depuis zero :
  // un geste qui repart de la position neutre a chaque cycle saccade.
  const amplitudeGeste = pose === 'wave' ? 16 : pose === 'open' ? 6 : 4;
  const oscillation = Math.sin(gestePhase * Math.PI * 2) * amplitudeGeste;

  const droit = extremite(angles.droit + oscillation, 1);
  const gauche = extremite(angles.gauche - oscillation * 0.35, -1);
  const inclinaison = pose === 'lean' ? 7 : 0;

  return (
    <svg width={160 * scale} height={280 * scale} viewBox="0 0 160 280" style={{overflow: 'visible'}}>
      <g
        stroke={color}
        strokeWidth={epaisseur}
        strokeLinecap="round"
        strokeLinejoin="round"
        fill="none"
        transform={`rotate(${inclinaison} 80 250)`}
      >
        <circle cx={80} cy={44 + teteY} r={RAYON_TETE} />
        <line x1={80} y1={basDeLaTete} x2={80} y2={170} />
        <line x1={80} y1={170} x2={52} y2={244} />
        <line x1={80} y1={170} x2={108} y2={244} />
        <line x1={EPAULE.x} y1={EPAULE.y + souffle} x2={droit.x} y2={droit.y + souffle} />
        <line x1={EPAULE.x} y1={EPAULE.y + souffle} x2={gauche.x} y2={gauche.y + souffle} />
      </g>
    </svg>
  );
};
