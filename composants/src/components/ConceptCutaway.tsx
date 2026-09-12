import React from 'react';
import {AbsoluteFill, useCurrentFrame, useVideoConfig} from 'remotion';
import type {CharteTokens, DirectionArtistique} from '../types';
import {Stickman} from './Stickman';
import {progressionEntree, retardSecondaireFrames, styleContinu, styleEntree} from '../animation';

export type ConceptScene =
  | 'llm_single_turn'
  | 'workflow_tools'
  | 'workflow_fixed_path'
  | 'agent_loop'
  | 'github_demo';

export type ConceptCutawayParams = {
  scene: ConceptScene;
  label?: string;
};

type Props = ConceptCutawayParams & {charte: CharteTokens; da?: DirectionArtistique};

type ElementChaine = {texte: string; tag?: string};

// Une chaine lineaire = une famille de scenes ; seul agent_loop est
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

// Un chemin fixe se montre par un rail rigide qui traverse les etapes :
// c'est ce qui distingue visuellement le workflow de l'agent. Sans lui, le
// schema n'etait que des rectangles empiles, vrais pour n'importe quel
// concept.
const AVEC_RAIL: ConceptScene[] = ['workflow_fixed_path'];

const Fleche: React.FC<{couleur: string; opacite: number}> = ({couleur, opacite}) => (
  <svg width={40} height={74} viewBox="0 0 40 74" style={{opacity: opacite, margin: '4px 0'}}>
    <line x1={20} y1={4} x2={20} y2={54} stroke={couleur} strokeWidth={5} strokeLinecap="round" />
    <polyline
      points="8,44 20,60 32,44"
      fill="none"
      stroke={couleur}
      strokeWidth={5}
      strokeLinecap="round"
      strokeLinejoin="round"
    />
  </svg>
);

const Maillon: React.FC<{
  item: ElementChaine;
  style: React.CSSProperties;
  charte: CharteTokens;
  accentue: boolean;
}> = ({item, style, charte, accentue}) => {
  const famille = charte.typographie.sous_titres.famille;
  const bord = accentue ? charte.couleurs.accent_secondaire : charte.couleurs.accent;
  return (
    <div style={{...style, textAlign: 'center', position: 'relative', zIndex: 1}}>
      {item.tag ? (
        <div
          style={{
            color: charte.couleurs.accent_secondaire,
            fontFamily: famille,
            fontSize: 30,
            fontWeight: 700,
            marginBottom: 10,
            letterSpacing: 2,
          }}
        >
          {item.tag}
        </div>
      ) : null}
      <div
        style={{
          border: `5px solid ${bord}`,
          borderRadius: 20,
          padding: '30px 44px',
          color: charte.couleurs.texte_principal,
          fontFamily: famille,
          fontSize: 46,
          fontWeight: 700,
          minWidth: 520,
          // Fond **opaque**, plus une teinte par-dessus. A 8 % d'alpha, le
          // rail du chemin fixe se voyait au travers et barrait le texte :
          // le z-index etait pourtant correct (rail 0 sous maillon 1), ce
          // n'etait pas un probleme d'empilement mais de transparence.
          backgroundColor: charte.couleurs.fond,
          backgroundImage: `linear-gradient(${bord}14, ${bord}14)`,
        }}
      >
        {item.texte}
      </div>
    </div>
  );
};

// La boucle : quatre noeuds en cercle, relies par un anneau. C'est la
// forme qui dit "agent" d'un coup d'oeil, par opposition a la chaine.
const Boucle: React.FC<{charte: CharteTokens; progression: number; rotation: number}> = ({
  charte,
  progression,
  rotation,
}) => {
  // Geometrie derivee, pas recopiee. Le defaut precedent vient exactement
  // de la : passer le rayon des noeuds de 72 a 88 pour que « OBSERVE »
  // tienne dans son cercle a fait sortir le cercle du cadre, parce que le
  // rayon de la boucle etait un nombre ecrit a la main. 380 + 300 + 88 +
  // 2,5 = 770,5 pour un viewBox de 760 : les quatre noeuds etaient rognes
  // de 10,5 px. Ici, changer un rayon recalcule l'autre.
  const TAILLE = 760;
  const RAYON_NOEUD = 88;
  const TRAIT_NOEUD = 5;
  const MARGE = 6;
  const C = TAILLE / 2;
  const R = C - RAYON_NOEUD - TRAIT_NOEUD / 2 - MARGE;
  const famille = charte.typographie.sous_titres.famille;
  return (
    <svg width={TAILLE} height={TAILLE} viewBox={`0 0 ${TAILLE} ${TAILLE}`}>
      <circle
        cx={C}
        cy={C}
        r={R}
        fill="none"
        stroke={charte.couleurs.accent}
        strokeWidth={6}
        strokeDasharray={2 * Math.PI * R}
        // Le cercle se trace au lieu d'apparaitre : le trace dit le sens de
        // la boucle, une apparition ne dit rien.
        strokeDashoffset={2 * Math.PI * R * (1 - progression)}
        transform={`rotate(${-90 + rotation} ${C} ${C})`}
        opacity={0.85}
      />
      {NOEUDS_BOUCLE.map((nom, i) => {
        const angle = (-90 + i * 90) * (Math.PI / 180);
        const x = C + Math.cos(angle) * R;
        const y = C + Math.sin(angle) * R;
        const apparu = Math.max(0, Math.min(1, progression * 4 - i));
        return (
          <g key={nom} opacity={apparu}>
            {/* r=88 et non 72 : "OBSERVE" debordait de son cercle. */}
            <circle
              cx={x}
              cy={y}
              r={RAYON_NOEUD}
              fill={charte.couleurs.fond}
              stroke={charte.couleurs.accent}
              strokeWidth={TRAIT_NOEUD}
            />
            <text
              x={x}
              y={y + 10}
              textAnchor="middle"
              fill={charte.couleurs.texte_principal}
              fontFamily={famille}
              fontSize={27}
              fontWeight={700}
            >
              {nom}
            </text>
          </g>
        );
      })}
    </svg>
  );
};

// Illustration animee d'une etape du concept, avec le stickman en retrait
// (§8). Le composant laissait environ les trois quarts du cadre vides et
// ses schemas etaient generiques ; il occupe desormais le 1080x1920 et le
// schema porte la distinction qu'il illustre.
export const ConceptCutaway: React.FC<Props> = ({scene, label, charte, da}) => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const famille = charte.typographie.sous_titres.famille;
  const chaine = CHAINES[scene];
  const retard = retardSecondaireFrames(charte, fps);
  const progression = progressionEntree(frame, fps, charte, da, 1);

  return (
    <AbsoluteFill style={{backgroundColor: charte.couleurs.fond, overflow: 'hidden'}}>
      <AbsoluteFill
        style={{
          ...styleEntree(frame, fps, charte, da, 4),
          background: `radial-gradient(ellipse at 50% 42%, ${charte.couleurs.accent}1a 0%, transparent 62%)`,
        }}
      />

      {label ? (
        <div
          style={{
            ...styleEntree(frame, fps, charte, da, 0),
            position: 'absolute',
            top: 120,
            width: '100%',
            textAlign: 'center',
            color: charte.couleurs.accent_secondaire,
            fontFamily: famille,
            fontSize: 52,
            fontWeight: 800,
            letterSpacing: 4,
          }}
        >
          {label}
        </div>
      ) : null}

      <AbsoluteFill
        style={{
          alignItems: 'center',
          justifyContent: 'center',
          paddingTop: 120,
          paddingBottom: 420,
        }}
      >
        <div style={styleContinu(frame, fps, charte, da)}>
          {chaine ? (
            <div style={{display: 'flex', flexDirection: 'column', alignItems: 'center', position: 'relative'}}>
              {AVEC_RAIL.includes(scene) ? (
                <div
                  style={{
                    position: 'absolute',
                    left: '50%',
                    top: 0,
                    bottom: 0,
                    width: 10,
                    marginLeft: -5,
                    borderRadius: 5,
                    // Un rail rigide se lit comme une barre, pas comme une
                    // salissure : a 33 % sur un fond quasi noir, il rendait
                    // un khaki terne. Il n'est plus filtre par les maillons,
                    // il peut donc etre franc.
                    backgroundColor: `${charte.couleurs.accent_secondaire}99`,
                    opacity: progression,
                    // Derriere les maillons : au-dessus, le rail barrait le
                    // texte de chaque etape.
                    zIndex: 0,
                  }}
                />
              ) : null}
              {chaine.map((item, i) => (
                <React.Fragment key={item.texte}>
                  {i > 0 ? (
                    <div style={{position: 'relative', zIndex: 1}}>
                      <Fleche
                        couleur={charte.couleurs.accent}
                        opacite={progressionEntree(frame, fps, charte, da, i * 2)}
                      />
                    </div>
                  ) : null}
                  <Maillon
                    item={item}
                    style={styleEntree(frame, fps, charte, da, i * 2 + 1)}
                    charte={charte}
                    accentue={i === chaine.length - 1}
                  />
                </React.Fragment>
              ))}
            </div>
          ) : (
            <Boucle charte={charte} progression={progression} rotation={(frame / fps) * 6} />
          )}
        </div>
      </AbsoluteFill>

      {/* Le stickman raconte en fond, au-dessus de la zone des sous-titres. */}
      <div style={{position: 'absolute', left: 60, bottom: 300, opacity: 0.75}}>
        <div style={styleEntree(frame, fps, charte, da, 5)}>
          <Stickman
            color={charte.couleurs.accent}
            scale={1.5}
            pose="point"
            phase={(frame / (fps * 2.4)) % 1}
            phaseGeste={((frame - retard) / (fps * 1.6)) % 1}
            epaisseur={8}
          />
        </div>
      </div>
    </AbsoluteFill>
  );
};
