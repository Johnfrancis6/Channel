import React from 'react';
import {AbsoluteFill, Img, useCurrentFrame, useVideoConfig} from 'remotion';
import type {CharteTokens, DirectionArtistique, Ressources} from '../types';
import {progressionEntree, pulsation, styleContinu, styleEntree} from '../animation';

export type PlanLogosParams = {
  // Cles de ressources (type `logo`), avec le libelle affiche sous chacune.
  logos: {cle: string; libelle?: string}[];
  label?: string;
  // Relie les pastilles par un trait. Une rangee de logos sans lien dit
  // « voici une liste » ; avec le lien, elle dit « ils se branchent ».
  relier?: boolean;
  compteur?: string;
};

type Props = PlanLogosParams & {
  charte: CharteTokens;
  da?: DirectionArtistique;
  ressources?: Ressources;
  pulsationFrame?: number;
};

// La pastille occupe la largeur disponible plutot qu'une taille fixe. A
// 190 px, trois logos tenaient dans une bande centrale et laissaient plus de
// la moitie du 1080x1920 vide — le defaut exact reproche a ConceptCutaway au
// premier passage du catalogue, reintroduit ici par une constante.
const LARGEUR_UTILE = 1080 - 140;
const ECART = 44;

function taillePastille(nombre: number): number {
  const brute = (LARGEUR_UTILE - ECART * (nombre - 1)) / nombre;
  // Plafonnee : un logo unique ne doit pas devenir un disque de 940 px.
  return Math.max(120, Math.min(300, Math.round(brute)));
}

/**
 * Une rangee de vrais logos de marque, en pastilles reliees.
 *
 * Les marques dont parlent les scripts (Claude, GitHub, Playwright…) etaient
 * jusqu'ici rendues par leur **nom en majuscules dans une boite**. Une boite
 * qui dit « GITHUB » ressemble exactement a une boite qui dit « CONTEXT7 » ;
 * les deux logos, eux, ne se ressemblent pas. C'est de la variete gratuite,
 * pour peu qu'on aille chercher le fichier.
 */
export const PlanLogos: React.FC<Props> = ({
  logos,
  label,
  relier = true,
  compteur,
  charte,
  da,
  ressources,
  pulsationFrame,
}) => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const famille = charte.typographie.sous_titres.famille;

  // Le trait se trace au lieu d'apparaitre : un lien qui existe deja quand
  // les pastilles arrivent ne raconte pas qu'elles se connectent.
  const traceLien = progressionEntree(frame, fps, charte, da, logos.length);
  const taille = taillePastille(Math.max(1, logos.length));
  const tailleLogo = Math.round(taille * 0.56);
  const pulse = pulsation(frame, fps, pulsationFrame);

  return (
    <AbsoluteFill style={{backgroundColor: charte.couleurs.fond, overflow: 'hidden'}}>
      <AbsoluteFill
        style={{
          ...styleEntree(frame, fps, charte, da, 4),
          background: `radial-gradient(circle at 50% 44%, ${charte.couleurs.accent}24 0%, transparent 60%)`,
        }}
      />

      <AbsoluteFill style={{alignItems: 'center', justifyContent: 'center', padding: 70, paddingBottom: 300}}>
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

        {label ? (
          <div
            style={{
              ...styleEntree(frame, fps, charte, da, 0),
              color: charte.couleurs.accent_secondaire,
              fontFamily: famille,
              fontSize: 54,
              fontWeight: 800,
              letterSpacing: 2,
              textAlign: 'center',
              marginBottom: 70,
            }}
          >
            {label}
          </div>
        ) : null}

        <div
          style={{
            // Le mouvement de fond s'efface quand l'accent frappe : un seul
            // mouvement dominant par scene (charte > animation.regles).
            ...styleContinu(frame, fps, charte, da, 1 - pulse),
            position: 'relative',
            display: 'flex',
            alignItems: 'flex-start',
            justifyContent: 'center',
            gap: ECART,
          }}
        >
          {relier && logos.length > 1 ? (
            <div
              style={{
                position: 'absolute',
                top: taille / 2 - 2,
                left: taille / 2,
                right: taille / 2,
                height: 4,
                borderRadius: 2,
                backgroundColor: charte.couleurs.accent,
                // Se trace de gauche a droite.
                transform: `scaleX(${traceLien})`,
                transformOrigin: 'left center',
              }}
            />
          ) : null}

          {logos.map((l, i) => {
            const asset = ressources?.[l.cle];
            return (
              <div
                key={l.cle}
                style={{
                  ...styleEntree(frame, fps, charte, da, i + 1),
                  position: 'relative',
                  display: 'flex',
                  flexDirection: 'column',
                  alignItems: 'center',
                  width: taille,
                }}
              >
                <div
                  style={{
                    width: taille,
                    height: taille,
                    borderRadius: taille / 2,
                    backgroundColor: '#F5F7FA',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    boxShadow: '0 22px 50px rgba(0,0,0,0.55)',
                    // Le dernier logo porte le benefice : c'est lui qui pulse.
                    transform: `scale(${1 + (i === logos.length - 1 ? pulse * 0.12 : 0)})`,
                  }}
                >
                  {asset ? (
                    <Img src={asset.src} style={{width: tailleLogo, height: tailleLogo, objectFit: 'contain'}} />
                  ) : (
                    <div style={{color: '#0B0F14', fontFamily: famille, fontSize: 24, textAlign: 'center', padding: 12}}>
                      {l.cle}
                    </div>
                  )}
                </div>
                {l.libelle ? (
                  <div
                    style={{
                      marginTop: 26,
                      color: charte.couleurs.texte_principal,
                      fontFamily: famille,
                      fontSize: 44,
                      fontWeight: 700,
                      textAlign: 'center',
                    }}
                  >
                    {l.libelle}
                  </div>
                ) : null}
              </div>
            );
          })}
        </div>
      </AbsoluteFill>
    </AbsoluteFill>
  );
};
