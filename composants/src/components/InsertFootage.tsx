import React from 'react';
import {AbsoluteFill, Img, Loop, OffthreadVideo, interpolate, spring, useCurrentFrame, useVideoConfig} from 'remotion';
import {niveaux} from '../typographie';
import type {CharteTokens, Insert, Ressources} from '../types';

type Props = {
  insert: Insert;
  charte: CharteTokens;
  ressources?: Ressources;
};

/**
 * Un instant de vidéo reelle par-dessus une scene animee.
 *
 * Ce n'est **pas** un composant de scene, et il n'est pas au registre. Un
 * composant de scene occupe tout le cadre pendant toute la scene : c'est ce
 * que fait `PlanBroll`, et c'est precisement le role que la contrainte du
 * format long ecarte — l'animation domine, la video reelle n'intervient qu'a
 * de courts instants, en zoom sur un point precis.
 *
 * Il appartient donc a la meme famille que `Subtitles` : une surcouche
 * surimprimee, declaree sur la scene (`scene.inserts`), bornee dans le temps
 * par le `<Sequence>` que `Video.tsx` pose autour. La scene animee continue
 * de tourner dessous, et reprend seule quand l'insert s'efface.
 *
 * Le son du clip est **toujours coupe** : la seule piste audio de la video
 * est la voix off (Video.tsx). Un fond sonore qui s'y ajoute par accident est
 * le genre de defaut qu'aucun test n'attrape.
 */
export const InsertFootage: React.FC<Props> = ({insert, charte, ressources}) => {
  const frame = useCurrentFrame();
  const {fps, durationInFrames, width, height} = useVideoConfig();
  const asset = ressources?.[insert.cle];

  // Rien a montrer : on ne laisse pas un cadre vide se poser sur la scene.
  // `construire_props.py` retire deja les inserts sans ressource ; ce garde-fou
  // couvre le rendu direct d'un storyboard non resolu (Remotion Studio).
  if (!asset) {
    return null;
  }

  // Entree et sortie courtes : un insert qui prend une seconde a arriver a
  // deja consomme le tiers de sa duree. Le ressort porte l'arrivee, un fondu
  // net ferme — `opaciteSortie` vise une fin de scene, pas une surcouche.
  const arrivee = spring({frame, fps, config: {damping: 200, mass: 0.6}, durationInFrames: Math.round(fps * 0.35)});
  const sortie = interpolate(frame, [durationInFrames - Math.round(fps * 0.25), durationInFrames], [1, 0], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  });

  // Le zoom est la raison d'etre de l'insert : il ne se pose pas, il se
  // rapproche. Amplitude par defaut modeste — c'est un detail montre, pas un
  // effet. Le sens ne s'inverse pas comme dans `punchIn` : un insert
  // s'ouvre toujours vers le point qu'il montre.
  const zoomFinal = insert.zoom ?? 1.12;
  const zoom = interpolate(frame, [0, Math.max(1, durationInFrames)], [1, zoomFinal], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  });

  // Le cadre occupe une large part de l'ecran sans le remplir : on doit voir
  // qu'il y a une scene dessous, sinon l'insert redevient un plan. La part
  // suit l'orientation — en paysage, un insert au deux tiers de la largeur
  // laisse la scene respirer sur les cotes ; en vertical, c'est la hauteur
  // qui est la ressource rare.
  const paysage = width >= height;
  const part = insert.part ?? (paysage ? 0.62 : 0.86);
  const marge = Math.round((paysage ? height : width) * 0.06);

  const framesClip = asset.duree_s ? Math.max(1, Math.floor(asset.duree_s * fps)) : undefined;
  const estVideo = asset.type === 'broll';
  const remplissage: React.CSSProperties = {width: '100%', height: '100%', objectFit: 'cover'};
  const media = estVideo ? (
    <OffthreadVideo src={asset.src} muted style={remplissage} />
  ) : (
    <Img src={asset.src} style={remplissage} />
  );

  return (
    <AbsoluteFill
      style={{
        alignItems: 'center',
        justifyContent: 'center',
        padding: marge,
        pointerEvents: 'none',
        opacity: arrivee * sortie,
      }}
    >
      <div
        style={{
          width: `${Math.round(part * 100)}%`,
          aspectRatio: '16 / 9',
          overflow: 'hidden',
          borderRadius: 24,
          // Le liseré et l'ombre portee disent « ceci est pose au-dessus ».
          // Sans eux, un clip aux bords sombres se fond dans le fond de la
          // charte et on ne sait plus ce qui est la scene et ce qui est
          // l'insert.
          border: `3px solid ${charte.couleurs.accent}55`,
          boxShadow: '0 30px 80px rgba(0,0,0,0.55)',
          transform: `scale(${0.96 + 0.04 * arrivee})`,
        }}
      >
        <AbsoluteFill style={{transform: `scale(${zoom})`}}>
          {estVideo && framesClip !== undefined && framesClip < durationInFrames ? (
            <Loop durationInFrames={framesClip}>{media}</Loop>
          ) : (
            media
          )}
        </AbsoluteFill>
      </div>

      {insert.legende ? (
        <div
          style={{
            marginTop: Math.round(marge * 0.5),
            padding: '8px 22px',
            borderRadius: 999,
            backgroundColor: `${charte.couleurs.fond}cc`,
            color: charte.couleurs.texte_principal,
            fontFamily: niveaux(charte).label.famille,
            fontSize: Math.round((paysage ? height : width) * 0.032),
            fontWeight: 700,
            opacity: arrivee,
          }}
        >
          {insert.legende}
        </div>
      ) : null}
    </AbsoluteFill>
  );
};
