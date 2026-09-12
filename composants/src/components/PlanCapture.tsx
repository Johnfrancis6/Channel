import React from 'react';
import {AbsoluteFill, Img, useCurrentFrame, useVideoConfig} from 'remotion';
import type {CharteTokens, DirectionArtistique, Ressources} from '../types';
import {punchIn, styleEntree} from '../animation';
import {Cadre} from './Cadre';

export type PlanCaptureParams = {
  // Cle dans la table des ressources (05b_ressources.json), pas un chemin :
  // A6 designe ce qu'il veut voir, A8 decide d'ou ca vient.
  capture: string;
  // Logo affiche en pastille au-dessus du cadre. Cle de ressource aussi.
  logo?: string;
  // Titre court au-dessus. JAMAIS la phrase prononcee : les sous-titres la
  // portent deja, et sur 2026-09-11_v01 ce doublon a coute quinze secondes.
  label?: string;
  // Quelle partie garder quand la capture est plus haute que le cadre.
  // `haut` par defaut : une page web se lit par le haut.
  cadrage?: 'haut' | 'centre' | 'bas';
  // Hauteur du cadre en px. Une page dense supporte plus haut qu'une
  // capture de terminal.
  hauteur?: number;
  compteur?: string;
};

type Props = PlanCaptureParams & {
  charte: CharteTokens;
  da?: DirectionArtistique;
  ressources?: Ressources;
  indexScene?: number;
};

// Le bas du cadre appartient aux sous-titres (cf. Subtitles, 220 px). On
// s'en tient a distance : un mockup qui passe dessous est illisible des
// que la voix off parle.
const MARGE_SOUS_TITRES = 300;

/**
 * Un plan qui montre **la chose reelle** : une capture de page, de terminal,
 * de depot.
 *
 * C'est le composant qui repond au vrai defaut du systeme. Tant que le seul
 * moyen de mettre quelque chose a l'ecran etait de le dessiner en SVG,
 * cinq serveurs MCP rendaient cinq fois le meme schema a trois boites avec
 * d'autres mots. Cinq captures de cinq pages ne peuvent pas se ressembler :
 * la variete vient de la donnee, plus du code.
 */
export const PlanCapture: React.FC<Props> = ({
  capture,
  logo,
  label,
  cadrage = 'haut',
  hauteur = 980,
  compteur,
  charte,
  da,
  ressources,
  indexScene = 0,
}) => {
  const frame = useCurrentFrame();
  const {fps, durationInFrames} = useVideoConfig();
  const famille = charte.typographie.sous_titres.famille;

  const asset = ressources?.[capture];
  const assetLogo = logo ? ressources?.[logo] : undefined;

  // La capture est mise a la LARGEUR du cadre, jamais recadree lateralement.
  // Premiere version : `objectFit: cover`, qui rognait environ 30 % de la
  // largeur d'une capture 1400x900 — la navigation a gauche et le panneau de
  // droite disparaissaient, et il ne restait qu'une colonne centrale
  // illisible. Une page web se cadre par sa largeur ; c'est en hauteur qu'on
  // coupe, comme un navigateur.
  const alignement =
    cadrage === 'haut' ? 'flex-start' : cadrage === 'bas' ? 'flex-end' : 'center';

  return (
    <AbsoluteFill style={{backgroundColor: charte.couleurs.fond, overflow: 'hidden'}}>
      {/* Halo derriere le cadre : donne une profondeur que l'aplat seul n'a
          pas, et evite que le mockup flotte dans le vide. */}
      <AbsoluteFill
        style={{
          ...styleEntree(frame, fps, charte, da, 3),
          background: `radial-gradient(circle at 50% 42%, ${charte.couleurs.accent}24 0%, transparent 62%)`,
        }}
      />

      <AbsoluteFill
        style={{
          alignItems: 'center',
          justifyContent: 'center',
          padding: 60,
          paddingBottom: MARGE_SOUS_TITRES,
        }}
      >
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

        {assetLogo ? (
          <div
            style={{
              ...styleEntree(frame, fps, charte, da, 0),
              width: 132,
              height: 132,
              borderRadius: 66,
              marginBottom: 34,
              // Pastille claire : un logo monochrome pose a nu sur fond
              // sombre disparait ou vire au trait. La pastille lui rend son
              // contraste sans toucher a la marque.
              backgroundColor: '#F5F7FA',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              boxShadow: '0 18px 40px rgba(0,0,0,0.5)',
            }}
          >
            <Img src={assetLogo.src} style={{width: 76, height: 76, objectFit: 'contain'}} />
          </div>
        ) : null}

        {label ? (
          <div
            style={{
              ...styleEntree(frame, fps, charte, da, 1),
              color: charte.couleurs.accent_secondaire,
              fontFamily: famille,
              fontSize: 52,
              fontWeight: 800,
              letterSpacing: 2,
              textAlign: 'center',
              marginBottom: 40,
            }}
          >
            {label}
          </div>
        ) : null}

        <div style={{...styleEntree(frame, fps, charte, da, 2), width: '100%'}}>
          <div style={punchIn(frame, fps, durationInFrames, da, indexScene)}>
            <Cadre charte={charte} barre={asset?.type === 'capture'}>
              {asset ? (
                <div
                  style={{
                    height: hauteur,
                    overflow: 'hidden',
                    display: 'flex',
                    alignItems: alignement,
                    backgroundColor: '#FFFFFF',
                  }}
                >
                  <Img src={asset.src} style={{display: 'block', width: '100%', height: 'auto'}} />
                </div>
              ) : (
                // Repli visible plutot que cadre vide : une ressource
                // manquante doit se voir au catalogue et au CP3, pas
                // produire un trou noir que personne ne remarque.
                <div
                  style={{
                    height: hauteur,
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    color: charte.couleurs.accent_secondaire,
                    fontFamily: famille,
                    fontSize: 40,
                    textAlign: 'center',
                    padding: 40,
                  }}
                >
                  Ressource manquante : « {capture} »
                </div>
              )}
            </Cadre>
          </div>
        </div>
      </AbsoluteFill>
    </AbsoluteFill>
  );
};
