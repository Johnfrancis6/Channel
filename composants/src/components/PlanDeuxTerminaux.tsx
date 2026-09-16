import React from 'react';
import {AbsoluteFill, interpolate, useCurrentFrame, useVideoConfig} from 'remotion';
import {niveaux, style} from '../typographie';
import type {CharteTokens, DirectionArtistique} from '../types';
import {progressionEntree, styleContinu, styleEntree} from '../animation';
import {Cadre} from './Cadre';

export type ColonneTerminal = {
  titre: string;
  // Nombre de lignes de code. C'est la DONNEE qui porte le message : peu a
  // gauche, beaucoup a droite. Le contraste de densite doit se lire en une
  // seconde, sans que personne ne lise une seule ligne.
  lignes: number;
};

export type PlanDeuxTerminauxParams = {
  gauche: ColonneTerminal;
  droite: ColonneTerminal;
  // Texte court decrivant ce qui entre flou derriere, en amorce. Le flou est
  // une promesse : « ces trois reglages, on y vient ».
  fond_flou?: string;
  label?: string;
};

type Props = PlanDeuxTerminauxParams & {
  charte: CharteTokens;
  da?: DirectionArtistique;
  indexScene?: number;
};

const MARGE_SOUS_TITRES = 300;

// Largeurs de lignes, en pourcentage. Pseudo-aleatoire deterministe : un
// rendu doit etre reproductible d'une passe a l'autre, donc pas de Math.random.
function largeurLigne(i: number): number {
  const v = Math.sin(i * 12.9898) * 43758.5453;
  return 42 + (v - Math.floor(v)) * 52;
}

const Terminal: React.FC<{
  colonne: ColonneTerminal;
  charte: CharteTokens;
  da?: DirectionArtistique;
  index: number;
  // Vitesse de defilement : la colonne dense defile plus vite, c'est ce qui
  // fait sentir la duree sans qu'on ait a l'ecrire.
  vitesse: number;
  accentue: boolean;
}> = ({colonne, charte, da, index, vitesse, accentue}) => {
  const frame = useCurrentFrame();
  const {fps, durationInFrames} = useVideoConfig();
  const typo = niveaux(charte);
  const texte = charte.couleurs.texte_principal;
  const accent = accentue ? charte.couleurs.accent : charte.couleurs.accent_secondaire;

  const HAUTEUR_LIGNE = 30;
  const hauteurVisible = 760;
  const hauteurTotale = colonne.lignes * HAUTEUR_LIGNE;
  const course = Math.max(0, hauteurTotale - hauteurVisible);
  const defilement =
    course === 0
      ? 0
      : interpolate(frame, [0, Math.max(1, durationInFrames)], [0, course * vitesse], {
          extrapolateLeft: 'clamp',
          extrapolateRight: 'clamp',
        });

  return (
    <div style={{...styleEntree(frame, fps, charte, da, index), flex: 1, minWidth: 0}}>
      <Cadre charte={charte} rayon={24}>
        <div
          style={{
            display: 'flex',
            alignItems: 'baseline',
            justifyContent: 'space-between',
            gap: 12,
            padding: '24px 26px',
            borderBottom: `1px solid ${texte}1a`,
          }}
        >
          <span
            style={{
              fontFamily: typo.label.famille,
              fontSize: 48,
              fontWeight: 800,
              color: accent,
              letterSpacing: 1,
            }}
          >
            {colonne.titre}
          </span>
          <span
            style={{
              fontFamily: typo.label.famille,
              fontSize: 26,
              fontWeight: 600,
              color: `${texte}7a`,
            }}
          >
            {colonne.lignes} lines
          </span>
        </div>

        <div style={{height: hauteurVisible, overflow: 'hidden', padding: '18px 26px'}}>
          <div style={{transform: `translateY(${-defilement}px)`}}>
            {Array.from({length: colonne.lignes}).map((_, i) => (
              <div
                key={i}
                style={{
                  height: HAUTEUR_LIGNE,
                  display: 'flex',
                  alignItems: 'center',
                  gap: 12,
                }}
              >
                <div
                  style={{
                    width: 26,
                    fontFamily: 'monospace',
                    fontSize: 18,
                    color: `${texte}4d`,
                    textAlign: 'right',
                  }}
                >
                  {i + 1}
                </div>
                <div
                  style={{
                    height: 10,
                    borderRadius: 5,
                    width: `${largeurLigne(i + index * 100)}%`,
                    backgroundColor: i % 7 === 0 ? `${accent}9e` : `${texte}30`,
                  }}
                />
              </div>
            ))}
          </div>
        </div>
      </Cadre>
    </div>
  );
};

/**
 * Deux terminaux cote a cote, pour un avant/apres de duree.
 *
 * Le message n'est pas dans le texte des lignes — personne ne le lira — mais
 * dans la difference de densite entre les deux fenetres. C'est pour ca que
 * `lignes` est un nombre et pas une liste de chaines : la scene doit se
 * comprendre au premier coup d'oeil, et rester vraie quelle que soit la
 * langue de la video.
 */
export const PlanDeuxTerminaux: React.FC<Props> = ({
  gauche,
  droite,
  fond_flou,
  label,
  charte,
  da,
  indexScene = 0,
}) => {
  const frame = useCurrentFrame();
  const {fps, durationInFrames} = useVideoConfig();
  const typo = niveaux(charte);
  const texte = charte.couleurs.texte_principal;

  // L'amorce floue passe devant, puis s'efface derriere les terminaux. Elle
  // ne doit jamais rester nette : ce qu'elle annonce arrive plus tard.
  const pFlou = interpolate(frame, [0, Math.round(fps * 1.1)], [1, 0.16], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  });

  return (
    <AbsoluteFill style={{overflow: 'hidden'}}>
      {fond_flou ? (
        <AbsoluteFill
          style={{
            alignItems: 'center',
            justifyContent: 'center',
            paddingBottom: MARGE_SOUS_TITRES,
            opacity: pFlou,
            filter: `blur(${interpolate(pFlou, [0.16, 1], [18, 7])}px)`,
          }}
        >
          <div
            style={{
              ...style(typo.titre),
              color: texte,
              textAlign: 'center',
              padding: '0 90px',
              lineHeight: 1.15,
            }}
          >
            {fond_flou}
          </div>
        </AbsoluteFill>
      ) : null}

      <AbsoluteFill
        style={{
          alignItems: 'center',
          justifyContent: 'center',
          padding: 40,
          paddingBottom: MARGE_SOUS_TITRES,
        }}
      >
        <div
          style={{
            ...styleContinu(frame, fps, charte, da, 0.5),
            width: '100%',
            display: 'flex',
            flexDirection: 'column',
            gap: 30,
          }}
        >
          {label ? (
            <div
              style={{
                ...styleEntree(frame, fps, charte, da, 0),
                ...style(typo.label),
                color: charte.couleurs.accent_secondaire,
                textAlign: 'center',
                textTransform: 'uppercase',
              }}
            >
              {label}
            </div>
          ) : null}
          <div style={{display: 'flex', gap: 26, alignItems: 'flex-start'}}>
            <Terminal colonne={gauche} charte={charte} da={da} index={1} vitesse={0.35} accentue={false} />
            <Terminal colonne={droite} charte={charte} da={da} index={2} vitesse={1} accentue />
          </div>
        </div>
      </AbsoluteFill>
    </AbsoluteFill>
  );
};
