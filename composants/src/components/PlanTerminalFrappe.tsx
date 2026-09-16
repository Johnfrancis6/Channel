import React from 'react';
import {AbsoluteFill, interpolate, useCurrentFrame, useVideoConfig} from 'remotion';
import {niveaux, style} from '../typographie';
import type {CharteTokens, DirectionArtistique} from '../types';
import {styleContinu, styleEntree} from '../animation';
import {Cadre} from './Cadre';

export type PlanTerminalFrappeParams = {
  // Invite courte, ex. « codex ». Pas de chemin absolu : ca ne se lit pas a
  // hauteur de pouce et ca date la video.
  invite?: string;
  // Ce qui s'ecrit caractere par caractere. Absent : le terminal se contente
  // de defiler.
  frappe?: string;
  // Des lignes de sortie defilent seules apres la frappe.
  defilement_auto?: boolean;
  // Horloge discrete en coin, ex. « 00:00 -> 06:00 ». Elle porte la duree,
  // qui est le sujet de la scene et que rien d'autre ne peut montrer.
  horloge?: string;
  label?: string;
};

type Props = PlanTerminalFrappeParams & {
  charte: CharteTokens;
  da?: DirectionArtistique;
  indexScene?: number;
};

const MARGE_SOUS_TITRES = 300;

// Frappe humaine : la cadence varie, et elle marque un temps sur l'espace.
// Une cadence fixe est le detail qui trahit le plus vite une fausse demo.
function caracteresFrappes(texte: string, frame: number, fps: number, debutFrame: number): number {
  const ecoule = (frame - debutFrame) / fps;
  if (ecoule <= 0) return 0;
  let t = 0;
  for (let i = 0; i < texte.length; i += 1) {
    const c = texte[i];
    const jitter = (Math.sin(i * 7.13) + 1) / 2; // deterministe
    const base = c === ' ' ? 0.11 : 0.045;
    t += base + jitter * 0.035;
    if (t > ecoule) return i;
  }
  return texte.length;
}

function ligneSortie(i: number): string {
  const verbes = ['reading', 'editing', 'running', 'checking', 'writing', 'testing'];
  const cibles = ['src/api.ts', 'migrations/', 'tests/unit', 'schema.sql', 'src/router.ts', 'README.md'];
  const v = verbes[i % verbes.length];
  const c = cibles[(i * 3 + 1) % cibles.length];
  return `  ${v} ${c}`;
}

/**
 * Un terminal plein cadre ou l'on voit taper une commande, puis le travail
 * se poursuivre seul.
 *
 * Pourquoi un composant plutot qu'une capture : la frappe est le sujet. Une
 * capture de terminal montre un resultat ; ici il faut voir la commande
 * s'ecrire, puis la machine continuer sans personne. C'est aussi le plus
 * reutilisable des quatre — toute video qui montre une ligne de commande le
 * reprendra tel quel.
 */
export const PlanTerminalFrappe: React.FC<Props> = ({
  invite = 'codex',
  frappe,
  defilement_auto = false,
  horloge,
  label,
  charte,
  da,
  indexScene = 0,
}) => {
  const frame = useCurrentFrame();
  const {fps, durationInFrames} = useVideoConfig();
  const typo = niveaux(charte);
  const texte = charte.couleurs.texte_principal;
  const accent = charte.couleurs.accent;
  const accent2 = charte.couleurs.accent_secondaire;

  const debutFrappe = Math.round(fps * 0.45);
  const n = frappe ? caracteresFrappes(frappe, frame, fps, debutFrappe) : 0;
  const frappeFinie = frappe ? n >= frappe.length : true;

  // Le curseur clignote a 1,6 Hz, sauf pendant la frappe ou il reste plein :
  // un curseur qui clignote au milieu d'un mot se lit comme un bug.
  const clignote = frappe && !frappeFinie ? 1 : Math.sin(frame / fps * Math.PI * 1.6) > 0 ? 1 : 0.1;

  const nbSorties = defilement_auto ? 26 : 0;
  const sortiesVisibles = defilement_auto
    ? Math.floor(
        interpolate(frame, [0, Math.max(1, durationInFrames)], [0, nbSorties], {
          extrapolateLeft: 'clamp',
          extrapolateRight: 'clamp',
        }),
      )
    : 0;

  return (
    <AbsoluteFill style={{overflow: 'hidden'}}>
      <AbsoluteFill
        style={{
          alignItems: 'center',
          justifyContent: 'center',
          padding: 44,
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
                color: accent2,
                textAlign: 'center',
                textTransform: 'uppercase',
              }}
            >
              {label}
            </div>
          ) : null}

          <div style={{...styleEntree(frame, fps, charte, da, 1)}}>
            <Cadre charte={charte} barre>
              <div
                style={{
                  position: 'relative',
                  // Un terminal qui ne fait que recevoir une commande n'a pas
                  // besoin de neuf cents pixels de vide sous elle : le cadre
                  // se regle sur ce qu'il contient.
                  height: defilement_auto ? 980 : 420,
                  padding: '40px 40px 0',
                }}
              >
                {horloge ? (
                  <div
                    style={{
                      position: 'absolute',
                      top: 28,
                      right: 36,
                      padding: '12px 24px',
                      borderRadius: 18,
                      backgroundColor: `${accent}1f`,
                      border: `2px solid ${accent}66`,
                      fontFamily: 'monospace',
                      fontSize: 34,
                      fontWeight: 700,
                      color: accent,
                    }}
                  >
                    {horloge}
                  </div>
                ) : null}

                <div style={{fontFamily: 'monospace', fontSize: 38, lineHeight: 1.55}}>
                  <div style={{display: 'flex', alignItems: 'baseline', gap: 16, flexWrap: 'wrap'}}>
                    <span style={{color: accent, fontWeight: 700}}>{invite}</span>
                    <span style={{color: `${texte}66`}}>&gt;</span>
                    <span style={{color: texte, wordBreak: 'break-word'}}>
                      {frappe ? frappe.slice(0, n) : ''}
                    </span>
                    <span
                      style={{
                        display: 'inline-block',
                        width: 20,
                        height: 42,
                        transform: 'translateY(6px)',
                        backgroundColor: texte,
                        opacity: clignote,
                      }}
                    />
                  </div>

                  {sortiesVisibles > 0 ? (
                    <div style={{marginTop: 36}}>
                      {Array.from({length: sortiesVisibles}).map((_, i) => (
                        <div
                          key={i}
                          style={{
                            color: `${texte}b0`,
                            fontSize: 32,
                            opacity: i === sortiesVisibles - 1 ? 0.55 : 1,
                          }}
                        >
                          {ligneSortie(i)}
                        </div>
                      ))}
                    </div>
                  ) : null}
                </div>
              </div>
            </Cadre>
          </div>
        </div>
      </AbsoluteFill>
    </AbsoluteFill>
  );
};
