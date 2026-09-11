import React from 'react';
import {AbsoluteFill, interpolate, useCurrentFrame, useVideoConfig} from 'remotion';
import type {CharteTokens} from '../types';
import {Stickman} from './Stickman';

export type ConceptScene = 'llm_single_turn' | 'workflow_tools' | 'workflow_fixed_path' | 'agent_loop' | 'github_demo';

export type ConceptCutawayParams = {
  scene: ConceptScene;
  label?: string;
};

type Props = ConceptCutawayParams & {charte: CharteTokens};

type ElementChaine = {texte: string; tag?: string};

// Une chaine lineaire = une famille de scenes (LLM single-pass, workflow a
// outils, workflow a chemin fixe, demo GitHub) ; seul agent_loop est
// circulaire (§8, la boucle est la distinction visuelle cle agent vs
// workflow).
const CHAINES: Partial<Record<ConceptScene, ElementChaine[]>> = {
  llm_single_turn: [{texte: 'PROMPT'}, {texte: 'LLM'}, {texte: 'RESPONSE'}],
  workflow_tools: [
    {texte: 'STEP 1', tag: '+ TOOL'},
    {texte: 'STEP 2', tag: '+ TOOL'},
    {texte: 'STEP 3', tag: '+ TOOL'},
  ],
  workflow_fixed_path: [{texte: 'STEP 1'}, {texte: 'STEP 2'}, {texte: 'STEP 3'}, {texte: 'DONE'}],
  github_demo: [{texte: 'CLAUDE'}, {texte: 'VS CODE (MCP)'}, {texte: 'GITHUB REPO'}],
};

const NOEUDS_BOUCLE = ['PLAN', 'ACT', 'OBSERVE', 'DECIDE'];

const Maillon: React.FC<{
  item: ElementChaine;
  opacite: number;
  couleurBord: string;
  couleurTexte: string;
  couleurTag: string;
  famille: string;
}> = ({item, opacite, couleurBord, couleurTexte, couleurTag, famille}) => (
  <div style={{opacity: opacite, textAlign: 'center'}}>
    {item.tag ? (
      <div style={{color: couleurTag, fontFamily: famille, fontSize: 20, fontWeight: 700, marginBottom: 6}}>
        {item.tag}
      </div>
    ) : null}
    <div
      style={{
        border: `3px solid ${couleurBord}`,
        borderRadius: 12,
        padding: '18px 28px',
        color: couleurTexte,
        fontFamily: famille,
        fontSize: 30,
        fontWeight: 700,
        minWidth: 260,
      }}
    >
      {item.texte}
    </div>
  </div>
);

// Stickman reduit en fond + illustration animee au premier plan pour une
// etape du concept (§8). Reutilisable pour de futures videos du pilier
// concept : le scene "kind" choisit la mise en scene (chaine lineaire ou
// boucle), le reste (label, stickman) est generique.
export const ConceptCutaway: React.FC<Props> = ({scene, label, charte}) => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const famille = charte.typographie.sous_titres.famille;
  const dureeEntree = Math.max(1, Math.round(charte.rythme.duree_transition_s * fps));
  const decalageMaillon = Math.round(fps * 0.5);

  const chaine = CHAINES[scene];

  return (
    <AbsoluteFill style={{backgroundColor: charte.couleurs.fond, alignItems: 'center'}}>
      {label ? (
        <div
          style={{
            marginTop: 120,
            color: charte.couleurs.accent_secondaire,
            fontFamily: famille,
            fontSize: 34,
            fontWeight: 700,
            letterSpacing: 2,
            textAlign: 'center',
            opacity: interpolate(frame, [0, dureeEntree], [0, 1], {extrapolateRight: 'clamp'}),
          }}
        >
          {label}
        </div>
      ) : null}

      <AbsoluteFill style={{alignItems: 'center', justifyContent: 'center'}}>
        {chaine ? (
          <div style={{display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 20}}>
            {chaine.map((item, i) => {
              const debut = i * decalageMaillon;
              const opacite = interpolate(frame, [debut, debut + dureeEntree], [0, 1], {
                extrapolateLeft: 'clamp',
                extrapolateRight: 'clamp',
              });
              return (
                <React.Fragment key={item.texte}>
                  {i > 0 ? (
                    <div style={{color: charte.couleurs.accent, fontSize: 32, opacity: opacite}}>{'↓'}</div>
                  ) : null}
                  <Maillon
                    item={item}
                    opacite={opacite}
                    couleurBord={charte.couleurs.accent}
                    couleurTexte={charte.couleurs.texte_principal}
                    couleurTag={charte.couleurs.accent_secondaire}
                    famille={famille}
                  />
                </React.Fragment>
              );
            })}
          </div>
        ) : (
          <BoucleAgent charte={charte} frame={frame} fps={fps} />
        )}
      </AbsoluteFill>

      <div style={{position: 'absolute', bottom: 90, left: 60}}>
        <Stickman color={charte.couleurs.accent} scale={0.75} pose="neutral" phase={(frame % fps) / fps} />
      </div>
    </AbsoluteFill>
  );
};

// Diagramme circulaire pour agent_loop : 4 etapes autour d'un cercle, un
// point met en evidence l'etape active pour suggerer la boucle continue
// (par opposition au chemin fixe/lineaire des autres scenes).
const BoucleAgent: React.FC<{charte: CharteTokens; frame: number; fps: number}> = ({charte, frame, fps}) => {
  const rayon = 220;
  const dureeTour = fps * 3.2;
  const angle = ((frame % dureeTour) / dureeTour) * Math.PI * 2 - Math.PI / 2;
  const famille = charte.typographie.sous_titres.famille;

  return (
    <div style={{position: 'relative', width: rayon * 2 + 200, height: rayon * 2 + 200}}>
      {NOEUDS_BOUCLE.map((nom, i) => {
        const a = (i / NOEUDS_BOUCLE.length) * Math.PI * 2 - Math.PI / 2;
        const x = rayon * Math.cos(a) + rayon + 100;
        const y = rayon * Math.sin(a) + rayon + 100;
        return (
          <div
            key={nom}
            style={{
              position: 'absolute',
              left: x - 70,
              top: y - 30,
              width: 140,
              border: `3px solid ${charte.couleurs.accent}`,
              borderRadius: 10,
              padding: '10px 0',
              textAlign: 'center',
              color: charte.couleurs.texte_principal,
              fontFamily: famille,
              fontSize: 24,
              fontWeight: 700,
            }}
          >
            {nom}
          </div>
        );
      })}
      <div
        style={{
          position: 'absolute',
          left: rayon * Math.cos(angle) + rayon + 100 - 12,
          top: rayon * Math.sin(angle) + rayon + 100 - 12,
          width: 24,
          height: 24,
          borderRadius: '50%',
          backgroundColor: charte.couleurs.accent_secondaire,
        }}
      />
    </div>
  );
};
