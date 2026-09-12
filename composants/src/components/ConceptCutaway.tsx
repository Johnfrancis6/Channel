import React from 'react';
import {AbsoluteFill, useCurrentFrame, useVideoConfig} from 'remotion';
import type {CharteTokens, DirectionArtistique} from '../types';
import {Stickman} from './Stickman';
import {progressionEntree, pulsation, retardSecondaireFrames, styleContinu, styleEntree} from '../animation';

export type ConceptScene =
  | 'llm_single_turn'
  | 'workflow_tools'
  | 'workflow_fixed_path'
  | 'agent_loop'
  | 'github_demo'
  // Famille « un serveur MCP branche a Claude » (2026-09-12_v01) : meme
  // grammaire que github_demo — trois boites verticales reliees par des
  // fleches, la derniere accentuee parce qu'elle porte le benefice. Une
  // valeur par outil plutot qu'un libelle passe en parametre : c'est ce qui
  // rend la variante visible au catalogue, donc choisissable par A6.
  | 'context7_demo'
  | 'playwright_demo'
  | 'firecrawl_demo'
  | 'higgsfield_demo'
  | 'github_mcp_demo';

export type ConceptCutawayParams = {
  scene: ConceptScene;
  label?: string;
  // Position dans une liste ("1/5"). Badge discret en coin haut : hors de la
  // zone des sous-titres (220 px du bas, cf. Subtitles) et hors des boites
  // centrales. Optionnel — les scenes hors listicle n'en ont pas.
  compteur?: string;
};

type Props = ConceptCutawayParams & {
  charte: CharteTokens;
  da?: DirectionArtistique;
  // Frame de declenchement de la pulsation de la boite accentuee, resolue au
  // montage depuis le timestamp reel de la phrase designee par `da.accent`
  // (04_phrases.json). Passee par Video.tsx, jamais ecrite dans le storyboard :
  // A6 designe une phrase, A7 en fait un instant.
  pulsationFrame?: number;
};

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
  // Claude -> le serveur MCP -> ce qu'il rapporte. La troisieme boite est le
  // benefice, et c'est elle qui est accentuee puis pulsee.
  context7_demo: [{texte: 'CLAUDE'}, {texte: 'CONTEXT7 MCP'}, {texte: 'REAL DOCS'}],
  playwright_demo: [{texte: 'CLAUDE'}, {texte: 'PLAYWRIGHT MCP'}, {texte: 'REAL BROWSER'}],
  firecrawl_demo: [{texte: 'CLAUDE'}, {texte: 'FIRECRAWL MCP'}, {texte: 'CLEAN TEXT'}],
  higgsfield_demo: [{texte: 'CLAUDE'}, {texte: 'HIGGSFIELD MCP'}, {texte: 'IMAGE OR VIDEO'}],
  // Distinct de github_demo, dont la boite centrale dit « VS CODE (MCP) » :
  // VS Code n'est jamais mentionne dans ce script, et montrer ce qu'on ne dit
  // pas est un decalage que le spectateur voit.
  github_mcp_demo: [{texte: 'CLAUDE'}, {texte: 'GITHUB MCP'}, {texte: 'PULL REQUEST'}],
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
  // Amplitude 0..1 de la pulsation d'accent. Portee par la boite elle-meme et
  // non par son conteneur : celui-ci porte deja la transformation d'entree,
  // et deux transform sur le meme noeud s'ecrasent.
  pulse?: number;
}> = ({item, style, charte, accentue, pulse = 0}) => {
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
          // 8 % suffisent a faire lire l'accent sur une boite de 520 px de
          // large ; au-dela, la boite cogne ses voisines.
          transform: `scale(${1 + pulse * 0.08})`,
          // La lueur accompagne l'echelle au lieu de la remplacer : elle
          // disparait entierement quand pulse revient a 0.
          boxShadow: pulse > 0 ? `0 0 ${Math.round(pulse * 46)}px ${bord}${pulse > 0.5 ? '66' : '33'}` : undefined,
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
export const ConceptCutaway: React.FC<Props> = ({scene, label, compteur, charte, da, pulsationFrame}) => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const famille = charte.typographie.sous_titres.famille;
  const chaine = CHAINES[scene];
  const retard = retardSecondaireFrames(charte, fps);
  const progression = progressionEntree(frame, fps, charte, da, 1);
  // Accent : la derniere boite pulse au moment ou la phrase qui porte le
  // benefice est prononcee. Pendant ce temps, le mouvement continu du schema
  // s'efface — un seul mouvement dominant par scene (charte, regle 1).
  const pulse = pulsation(frame, fps, pulsationFrame);

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

      {compteur ? (
        <div
          style={{
            ...styleEntree(frame, fps, charte, da, 6),
            position: 'absolute',
            top: 108,
            right: 56,
            zIndex: 2,
            padding: '10px 24px',
            borderRadius: 999,
            border: `4px solid ${charte.couleurs.accent_secondaire}`,
            backgroundColor: charte.couleurs.fond,
            color: charte.couleurs.accent_secondaire,
            fontFamily: famille,
            fontSize: 38,
            fontWeight: 800,
            letterSpacing: 2,
          }}
        >
          {compteur}
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
        <div style={styleContinu(frame, fps, charte, da, 1 - pulse)}>
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
                    pulse={i === chaine.length - 1 ? pulse : 0}
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
