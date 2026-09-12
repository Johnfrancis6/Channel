import React from 'react';
import {AbsoluteFill, Img, Loop, OffthreadVideo, useCurrentFrame, useVideoConfig} from 'remotion';
import type {CharteTokens, DirectionArtistique, Ressources} from '../types';
import {punchIn, styleEntree} from '../animation';

export type PlanBrollParams = {
  // Cle de ressource. Accepte un clip (`broll`) **ou une photo** (`image`,
  // `capture`) : les banques libres servent les deux, et une photo qui se
  // rapproche lentement est un plan de liaison aussi valable qu'un clip —
  // souvent plus net, et toujours moins lourd a rendre.
  broll: string;
  // Mot-cle ou chiffre en surimpression. Jamais la phrase prononcee.
  accroche?: string;
  compteur?: string;
};

type Props = PlanBrollParams & {
  charte: CharteTokens;
  da?: DirectionArtistique;
  ressources?: Ressources;
  indexScene?: number;
};

/**
 * Un plan de matiere : une vidéo reelle plein cadre, voilee, avec un mot
 * par-dessus.
 *
 * Sert les passages de liaison, que le systeme rendait jusqu'ici avec un
 * schema de plus — donc avec un schema de trop. Un plan qui ne porte aucune
 * idee n'a pas besoin d'illustrer : il a besoin d'occuper l'oeil pendant
 * que la voix avance.
 *
 * Le son du clip est **toujours coupe** : la seule piste audio de la video
 * est la voix off (Video.tsx), et un fond sonore qui s'y ajoute par accident
 * est le genre de defaut qu'aucun test n'attrape.
 */
export const PlanBroll: React.FC<Props> = ({
  broll,
  accroche,
  compteur,
  charte,
  da,
  ressources,
  indexScene = 0,
}) => {
  const frame = useCurrentFrame();
  const {fps, durationInFrames} = useVideoConfig();
  const famille = charte.typographie.sous_titres.famille;
  const asset = ressources?.[broll];

  // `loop` n'existe pas sur <OffthreadVideo> : on reboucle par <Loop>, qui
  // remet useCurrentFrame() a zero et donc relance le clip. La coupe de
  // boucle se voit ; un ecran noir en fin de plan se voit davantage.
  const framesClip = asset?.duree_s ? Math.max(1, Math.floor(asset.duree_s * fps)) : undefined;
  const estVideo = asset?.type === 'broll';
  const remplissage: React.CSSProperties = {width: '100%', height: '100%', objectFit: 'cover'};
  const clip = asset ? (
    estVideo ? (
      <OffthreadVideo src={asset.src} muted style={remplissage} />
    ) : (
      <Img src={asset.src} style={remplissage} />
    )
  ) : null;

  return (
    <AbsoluteFill style={{backgroundColor: charte.couleurs.fond, overflow: 'hidden'}}>
      {asset ? (
        <AbsoluteFill style={punchIn(frame, fps, durationInFrames, da, indexScene)}>
          {estVideo && framesClip !== undefined && framesClip < durationInFrames ? (
            <Loop durationInFrames={framesClip}>{clip}</Loop>
          ) : (
            clip
          )}
        </AbsoluteFill>
      ) : (
        <AbsoluteFill
          style={{
            alignItems: 'center',
            justifyContent: 'center',
            color: charte.couleurs.accent_secondaire,
            fontFamily: famille,
            fontSize: 40,
          }}
        >
          Ressource manquante : « {broll} »
        </AbsoluteFill>
      )}

      {/* Voile : une video brute derriere du texte blanc est illisible des
          qu'une zone claire passe. Le degrade assombrit le haut et le bas,
          la ou vivent l'accroche et les sous-titres. */}
      <AbsoluteFill
        style={{
          background: `linear-gradient(180deg, ${charte.couleurs.fond}cc 0%, ${charte.couleurs.fond}40 32%, ${charte.couleurs.fond}40 52%, ${charte.couleurs.fond}e6 100%)`,
        }}
      />

      <AbsoluteFill style={{alignItems: 'center', justifyContent: 'center', padding: 80, paddingBottom: 320}}>
        {compteur ? (
          <div
            style={{
              ...styleEntree(frame, fps, charte, da, 0),
              position: 'absolute',
              top: 70,
              right: 70,
              padding: '10px 24px',
              borderRadius: 999,
              backgroundColor: `${charte.couleurs.accent}29`,
              color: charte.couleurs.accent,
              fontFamily: famille,
              fontSize: 40,
              fontWeight: 800,
            }}
          >
            {compteur}
          </div>
        ) : null}

        {accroche ? (
          <div
            style={{
              ...styleEntree(frame, fps, charte, da, 1),
              color: charte.couleurs.texte_principal,
              fontFamily: famille,
              fontSize: 96,
              fontWeight: 800,
              lineHeight: 1.1,
              textAlign: 'center',
              textShadow: '0 8px 30px rgba(0,0,0,0.7)',
            }}
          >
            {accroche}
          </div>
        ) : null}
      </AbsoluteFill>
    </AbsoluteFill>
  );
};
