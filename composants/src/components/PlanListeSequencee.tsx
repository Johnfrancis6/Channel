import React from 'react';
import {AbsoluteFill, interpolate, useCurrentFrame, useVideoConfig} from 'remotion';
import {niveaux, style} from '../typographie';
import type {CharteTokens, DirectionArtistique} from '../types';
import {progressionEntree, pulsation, styleContinu, styleEntree} from '../animation';

export type ColonneListe = {
  titre: string;
  entrees: string[];
  // Colonne qui s'efface : c'est la facon de montrer « pas ca » sans
  // l'ecrire. Sert au contraste etapes / ligne d'arrivee.
  effacee?: boolean;
};

export type PlanListeSequenceeParams = {
  titre?: string;
  // `echelle` : barreaux empiles, du bas vers le haut, pour une gradation.
  // `liste` : entrees en gros texte, pour une enumeration.
  // `deux_colonnes` : deux listes opposees, pour un contraste.
  disposition?: 'echelle' | 'liste' | 'deux_colonnes';
  entrees?: string[];
  // Entree barree, avec sa mention a cote (ex. « none » / « HTTP 400 »).
  barree?: string;
  mention_barree?: string;
  // Entree mise en avant, qui pulse une fois.
  accentuee?: string;
  // Encadre le bloc et y pose un mot en diagonale.
  cadre?: boolean;
  tampon?: string;
  colonne_gauche?: ColonneListe;
  colonne_droite?: ColonneListe;
};

type Props = PlanListeSequenceeParams & {
  charte: CharteTokens;
  da?: DirectionArtistique;
  indexScene?: number;
};

const MARGE_SOUS_TITRES = 300;

/**
 * Une liste dont les entrees s'allument en sequence.
 *
 * Le composant le plus rentable des quatre : il porte cinq des douze scenes
 * de 2026-09-16_v01 sous trois dispositions differentes. La contrainte dure
 * du §8 — deux scenes d'une meme video ne peuvent pas produire la meme
 * image — est tenue par la DONNEE : une echelle a sept barreaux dont un
 * barre ne ressemble pas a deux colonnes opposees, ni a quatre lignes
 * encadrees sous un tampon.
 */
export const PlanListeSequencee: React.FC<Props> = ({
  titre,
  disposition = 'liste',
  entrees = [],
  barree,
  mention_barree,
  accentuee,
  cadre = false,
  tampon,
  colonne_gauche,
  colonne_droite,
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
  const rouge = '#FF6B6B';

  // `pulsation` rend une AMPLITUDE 0..1, pas un facteur d'echelle : elle vaut
  // 0 hors de l'accent. L'utiliser telle quelle dans un `scale()` fait
  // disparaitre l'element — c'est ce qui avait efface `medium` de l'echelle
  // au premier catalogue. On s'en sert donc comme d'un supplement.
  const accentEchelle = 1 + pulsation(frame, fps, Math.round(fps * 1.1)) * 0.07;

  const enTete = titre ? (
    <div
      style={{
        ...styleEntree(frame, fps, charte, da, 0),
        ...style(typo.label),
        color: accent2,
        textAlign: 'center',
        textTransform: 'uppercase',
        marginBottom: 46,
      }}
    >
      {titre}
    </div>
  ) : null;

  // --- Echelle : gradation du bas vers le haut ---------------------------
  if (disposition === 'echelle') {
    // Rendu du bas vers le haut : `column-reverse` fait que `entrees[0]` est
    // en bas, ce qui est le sens de lecture d'une gradation.
    return (
      <AbsoluteFill style={{overflow: 'hidden'}}>
        <AbsoluteFill
          style={{
            alignItems: 'center',
            justifyContent: 'center',
            padding: 70,
            paddingBottom: MARGE_SOUS_TITRES,
          }}
        >
          <div style={{...styleContinu(frame, fps, charte, da, 0.5), width: '100%'}}>
            {enTete}
            <div style={{display: 'flex', flexDirection: 'column-reverse', gap: 18}}>
              {entrees.map((e, i) => {
                const p = progressionEntree(frame, fps, charte, da, i + 1);
                const estBarree = e === barree;
                const estAccent = e === accentuee;
                const couleur = estBarree ? rouge : estAccent ? accent : texte;
                return (
                  <div
                    key={e}
                    style={{
                      display: 'flex',
                      alignItems: 'center',
                      gap: 26,
                      opacity: p,
                      transform: `translateX(${(1 - p) * -40}px) scale(${estAccent ? accentEchelle : 1})`,
                    }}
                  >
                    <div
                      style={{
                        flex: 1,
                        height: 92,
                        borderRadius: 18,
                        display: 'flex',
                        alignItems: 'center',
                        paddingLeft: 34,
                        backgroundColor: estBarree
                          ? `${rouge}1f`
                          : estAccent
                            ? `${accent}33`
                            : `${texte}12`,
                        border: `3px solid ${estAccent ? accent : estBarree ? `${rouge}88` : `${texte}1f`}`,
                        // Largeur croissante : la gradation se voit avant
                        // qu'on ait lu le moindre mot.
                        marginRight: `${Math.max(0, (entrees.length - 1 - i) * 5)}%`,
                      }}
                    >
                      <span
                        style={{
                          fontFamily: typo.label.famille,
                          fontSize: 52,
                          fontWeight: estAccent ? 800 : 600,
                          color: couleur,
                          textDecoration: estBarree ? 'line-through' : 'none',
                          textDecorationThickness: estBarree ? 6 : undefined,
                        }}
                      >
                        {e}
                      </span>
                    </div>
                    {estBarree && mention_barree ? (
                      <span
                        style={{
                          fontFamily: 'monospace',
                          fontSize: 38,
                          fontWeight: 700,
                          color: rouge,
                          whiteSpace: 'nowrap',
                        }}
                      >
                        {mention_barree}
                      </span>
                    ) : null}
                  </div>
                );
              })}
            </div>
          </div>
        </AbsoluteFill>
      </AbsoluteFill>
    );
  }

  // --- Deux colonnes : un contraste --------------------------------------
  if (disposition === 'deux_colonnes') {
    const colonnes = [colonne_gauche, colonne_droite].filter(Boolean) as ColonneListe[];
    return (
      <AbsoluteFill style={{overflow: 'hidden'}}>
        <AbsoluteFill
          style={{
            alignItems: 'center',
            justifyContent: 'center',
            padding: 60,
            paddingBottom: MARGE_SOUS_TITRES,
          }}
        >
          <div style={{...styleContinu(frame, fps, charte, da, 0.5), width: '100%'}}>
            {enTete}
            <div style={{display: 'flex', gap: 34, alignItems: 'stretch'}}>
              {colonnes.map((c, ci) => {
                // La colonne « effacee » part nette puis s'eteint : on doit
                // la voir avant de la perdre, sinon le contraste n'existe pas.
                const extinction = c.effacee
                  ? interpolate(frame, [Math.round(fps * 0.9), Math.round(fps * 2.1)], [1, 0.14], {
                      extrapolateLeft: 'clamp',
                      extrapolateRight: 'clamp',
                    })
                  : 1;
                return (
                  <div
                    key={c.titre}
                    style={{
                      ...styleEntree(frame, fps, charte, da, ci + 1),
                      flex: 1,
                      minWidth: 0,
                      opacity: extinction,
                      filter: c.effacee ? `blur(${(1 - extinction) * 7}px)` : 'none',
                      borderRadius: 26,
                      padding: '34px 30px',
                      backgroundColor: c.effacee ? `${texte}0d` : `${accent}1f`,
                      border: `3px solid ${c.effacee ? `${texte}1f` : accent}`,
                    }}
                  >
                    <div
                      style={{
                        fontFamily: typo.label.famille,
                        fontSize: 40,
                        fontWeight: 800,
                        letterSpacing: 1.5,
                        textTransform: 'uppercase',
                        color: c.effacee ? `${texte}88` : accent,
                        marginBottom: 28,
                      }}
                    >
                      {c.titre}
                    </div>
                    {c.entrees.map((e) => (
                      <div
                        key={e}
                        style={{
                          fontFamily: typo.label.famille,
                          fontSize: 62,
                          fontWeight: 700,
                          color: c.effacee ? `${texte}99` : texte,
                          padding: '14px 0',
                          textDecoration: c.effacee ? 'line-through' : 'none',
                        }}
                      >
                        {e}
                      </div>
                    ))}
                  </div>
                );
              })}
            </div>
          </div>
        </AbsoluteFill>
      </AbsoluteFill>
    );
  }

  // --- Liste simple ------------------------------------------------------
  return (
    <AbsoluteFill style={{overflow: 'hidden'}}>
      <AbsoluteFill
        style={{
          alignItems: 'center',
          justifyContent: 'center',
          padding: 70,
          paddingBottom: MARGE_SOUS_TITRES,
        }}
      >
        <div style={{...styleContinu(frame, fps, charte, da, 0.5), width: '100%'}}>
          {enTete}
          <div
            style={{
              position: 'relative',
              display: 'flex',
              flexDirection: 'column',
              gap: 22,
              padding: cadre ? 46 : 0,
              borderRadius: cadre ? 30 : 0,
              border: cadre ? `5px solid ${accent}` : 'none',
              backgroundColor: cadre ? `${accent}14` : 'transparent',
            }}
          >
            {entrees.map((e, i) => {
              const p = progressionEntree(frame, fps, charte, da, i + 1);
              const estAccent = e === accentuee;
              return (
                <div
                  key={e}
                  style={{
                    display: 'flex',
                    alignItems: 'center',
                    gap: 28,
                    opacity: p,
                    transform: `translateY(${(1 - p) * 34}px) scale(${estAccent ? accentEchelle : 1})`,
                  }}
                >
                  <div
                    style={{
                      width: 18,
                      height: 18,
                      borderRadius: 9,
                      flexShrink: 0,
                      backgroundColor: estAccent ? accent : accent2,
                    }}
                  />
                  <span
                    style={{
                      fontFamily: typo.label.famille,
                      fontSize: 76,
                      fontWeight: 800,
                      letterSpacing: 0.5,
                      color: texte,
                    }}
                  >
                    {e}
                  </span>
                </div>
              );
            })}

            {tampon ? (
              <div
                style={{
                  position: 'absolute',
                  right: -10,
                  bottom: -34,
                  transform: `rotate(-11deg) scale(${interpolate(
                    progressionEntree(frame, fps, charte, da, entrees.length + 1),
                    [0, 1],
                    [1.6, 1],
                  )})`,
                  opacity: progressionEntree(frame, fps, charte, da, entrees.length + 1),
                  padding: '16px 38px',
                  border: `7px solid ${accent2}`,
                  borderRadius: 16,
                  fontFamily: typo.titre.famille,
                  fontSize: 78,
                  fontWeight: 800,
                  letterSpacing: 4,
                  color: accent2,
                  backgroundColor: `${charte.couleurs.fond}cc`,
                }}
              >
                {tampon}
              </div>
            ) : null}
          </div>
        </div>
      </AbsoluteFill>
    </AbsoluteFill>
  );
};
