import React from 'react';
import {AbsoluteFill, Img, interpolate, useCurrentFrame, useVideoConfig} from 'remotion';
import {niveaux, style} from '../typographie';
import type {CharteTokens, DirectionArtistique, Ressources} from '../types';
import {progressionEntree, pulsation, styleContinu, styleEntree} from '../animation';
import {Cadre} from './Cadre';

export type PlanNavigateurCurseurParams = {
  // Trois temps du meme plan, pas trois plans : la liste reste a l'ecran.
  etat: 'ouverture_liste' | 'parcours_liste' | 'ligne_surlignee';
  // Les entrees du selecteur. Valeur par defaut volontairement plausible :
  // ce qu'on montre est une interface RECREEE, pas une capture. Le selecteur
  // de modeles est derriere une authentification, `capturer_web.py` ne peut
  // pas l'atteindre (voir 05_cadrage.md).
  modeles?: string[];
  // L'entree qui s'allume quand `etat === 'ligne_surlignee'`.
  surligne?: string;
  // Le marqueur pose a droite de la liste. `question` dit « ce que vous
  // cherchez n'est pas la » ; `coche` dit « le voila, sous un autre nom ».
  marqueur?: 'question' | 'coche' | 'aucun';
  // Rapprochement lent sur la liste pendant toute la scene.
  zoom?: 'liste' | 'aucun';
  // Titre court au-dessus. Jamais la phrase prononcee.
  label?: string;
  // Cle de ressource. Optionnel : sans logo, une pastille neutre tient le
  // meme role et la scene reste lisible.
  logo?: string;
  domaine?: string;
};

type Props = PlanNavigateurCurseurParams & {
  charte: CharteTokens;
  da?: DirectionArtistique;
  ressources?: Ressources;
  indexScene?: number;
};

// Les sous-titres occupent le bas du cadre. Rien d'important en dessous.
const MARGE_SOUS_TITRES = 300;

const MODELES_DEFAUT = [
  'GPT-6 Pro',
  'GPT-5.6 Sol',
  'GPT-5.5',
  'GPT-5 mini',
  'o4-reasoning',
];

/** Fleche de curseur. Dessinee, pas importee : elle doit prendre la couleur de la charte. */
const Curseur: React.FC<{couleur: string; taille?: number}> = ({couleur, taille = 64}) => (
  <svg width={taille} height={taille} viewBox="0 0 24 24" style={{display: 'block'}}>
    <path
      d="M5 2.5 L5 19.5 L9.4 15.4 L12.3 21.5 L15.2 20.1 L12.4 14.2 L18.5 14.0 Z"
      fill={couleur}
      stroke="rgba(0,0,0,0.55)"
      strokeWidth={0.9}
      strokeLinejoin="round"
    />
  </svg>
);

/**
 * Un navigateur ouvert sur ChatGPT, pilote au curseur.
 *
 * C'est le hook de 2026-09-16_v01 : on cherche un modele dans le selecteur,
 * il n'y est pas. Le composant existe parce qu'aucun autre ne pouvait porter
 * un geste — `PlanCapture` montre une image fixe, et l'absence d'un element
 * dans une liste ne se raconte pas avec une image fixe : il faut voir
 * quelqu'un chercher.
 */
export const PlanNavigateurCurseur: React.FC<Props> = ({
  etat,
  modeles = MODELES_DEFAUT,
  surligne,
  marqueur = 'aucun',
  zoom = 'aucun',
  label,
  logo,
  domaine = 'chatgpt.com',
  charte,
  da,
  ressources,
  indexScene = 0,
}) => {
  const frame = useCurrentFrame();
  const {fps, durationInFrames} = useVideoConfig();
  const typo = niveaux(charte);
  const assetLogo = logo ? ressources?.[logo] : undefined;

  const texte = charte.couleurs.texte_principal;
  const accent = charte.couleurs.accent;
  const accent2 = charte.couleurs.accent_secondaire;

  // Progression du geste principal. Sur `ouverture_liste` elle ouvre la
  // liste ; ailleurs la liste est deja la, le curseur seul travaille.
  const ouverture = progressionEntree(frame, fps, charte, da, 0);
  const listeVisible = etat === 'ouverture_liste' ? ouverture : 1;

  const indexSurligne = surligne ? modeles.indexOf(surligne) : -1;

  // Trajet du curseur, en pourcentage du cadre. Il n'est jamais lineaire :
  // `progressionEntree` passe par un ressort, donc il accelere puis se pose
  // (regle 1). Une rampe lineaire se voit immediatement.
  const t = progressionEntree(frame, fps, charte, da, 1);
  const cible = (() => {
    if (etat === 'ouverture_liste') return {x: 74, y: 30};
    if (etat === 'parcours_liste') {
      // Descente continue de la liste, sans arret : c'est la fouille.
      const d = interpolate(frame, [0, Math.max(1, durationInFrames)], [0, 1], {
        extrapolateLeft: 'clamp',
        extrapolateRight: 'clamp',
      });
      return {x: 30, y: 40 + d * 34};
    }
    const rang = indexSurligne >= 0 ? indexSurligne : 0;
    return {x: 30, y: 41 + rang * 9};
  })();
  const depart = {x: 96, y: 88};
  const curseurX = interpolate(t, [0, 1], [depart.x, cible.x]);
  const curseurY = interpolate(t, [0, 1], [depart.y, cible.y]);

  // Le rapprochement se joue sur toute la scene, pas sur l'entree.
  const echelleZoom =
    zoom === 'liste'
      ? interpolate(frame, [0, Math.max(1, durationInFrames)], [1, 1.1], {
          extrapolateLeft: 'clamp',
          extrapolateRight: 'clamp',
        })
      : 1;

  // Le marqueur arrive en dernier : c'est lui la chute de la scene.
  const pMarqueur = progressionEntree(frame, fps, charte, da, 3);
  // Amplitude 0..1 (voir animation.ts), donc un supplement d'echelle et non
  // un facteur : `scale(battement)` ferait disparaitre le marqueur.
  const battement = 1 + pulsation(frame, fps, Math.round(fps * 0.9)) * 0.1;

  return (
    <AbsoluteFill style={{overflow: 'hidden'}}>
      <AbsoluteFill
        style={{
          alignItems: 'center',
          justifyContent: 'center',
          padding: 48,
          paddingBottom: MARGE_SOUS_TITRES,
        }}
      >
        <div
          style={{
            ...styleContinu(frame, fps, charte, da, 0.5),
            width: '100%',
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center',
            gap: 34,
          }}
        >
          {label ? (
            <div
              style={{
                ...styleEntree(frame, fps, charte, da, 0),
                ...style(typo.label),
                color: accent2,
                textTransform: 'uppercase',
                textAlign: 'center',
              }}
            >
              {label}
            </div>
          ) : null}

          <div style={{position: 'relative', width: '100%', transform: `scale(${echelleZoom})`}}>
            <Cadre charte={charte} barre>
              {/* Barre d'adresse. Sobre a dessein : on ne contrefait pas le
                  chrome d'un navigateur de marque, on dit « c'est le web ». */}
              <div
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: 18,
                  padding: '22px 30px',
                  borderBottom: `1px solid ${texte}14`,
                }}
              >
                <div
                  style={{
                    flex: 1,
                    height: 62,
                    borderRadius: 31,
                    backgroundColor: `${texte}12`,
                    display: 'flex',
                    alignItems: 'center',
                    paddingLeft: 28,
                    fontFamily: typo.label.famille,
                    fontSize: 34,
                    fontWeight: 600,
                    color: `${texte}b0`,
                  }}
                >
                  {domaine}
                </div>
              </div>

              <div style={{padding: '46px 46px 60px'}}>
                {/* Le bouton du selecteur, celui sur lequel on clique. */}
                <div
                  style={{
                    display: 'inline-flex',
                    alignItems: 'center',
                    gap: 20,
                    padding: '22px 34px',
                    borderRadius: 22,
                    backgroundColor: `${texte}14`,
                    border: `2px solid ${etat === 'ouverture_liste' ? accent : `${texte}1f`}`,
                  }}
                >
                  {assetLogo ? (
                    <Img src={assetLogo.src} style={{width: 48, height: 48, objectFit: 'contain'}} />
                  ) : (
                    <div
                      style={{
                        width: 44,
                        height: 44,
                        borderRadius: 22,
                        border: `4px solid ${texte}66`,
                      }}
                    />
                  )}
                  <span
                    style={{
                      fontFamily: typo.label.famille,
                      fontSize: 40,
                      fontWeight: 700,
                      color: texte,
                    }}
                  >
                    Model
                  </span>
                  <span style={{fontSize: 34, color: `${texte}88`}}>▾</span>
                </div>

                {/* La liste. Chaque ligne entre decalee (regle 3) : une liste
                    qui apparait d'un bloc lit comme une capture, pas comme
                    un menu qu'on deroule. */}
                <div
                  style={{
                    marginTop: 26,
                    borderRadius: 26,
                    backgroundColor: `${texte}0d`,
                    border: `1px solid ${texte}1a`,
                    overflow: 'hidden',
                    opacity: listeVisible,
                    transformOrigin: 'top center',
                    transform: `scaleY(${interpolate(listeVisible, [0, 1], [0.7, 1])})`,
                  }}
                >
                  {modeles.map((m, i) => {
                    const p =
                      etat === 'ouverture_liste'
                        ? progressionEntree(frame, fps, charte, da, i + 1)
                        : 1;
                    const actif = etat === 'ligne_surlignee' && i === indexSurligne;
                    return (
                      <div
                        key={m}
                        style={{
                          display: 'flex',
                          alignItems: 'center',
                          justifyContent: 'space-between',
                          padding: '30px 34px',
                          opacity: p,
                          transform: `translateX(${(1 - p) * -26}px)`,
                          backgroundColor: actif ? `${accent}2e` : 'transparent',
                          borderLeft: `6px solid ${actif ? accent : 'transparent'}`,
                          borderBottom: i < modeles.length - 1 ? `1px solid ${texte}12` : 'none',
                        }}
                      >
                        <span
                          style={{
                            fontFamily: typo.label.famille,
                            fontSize: 42,
                            fontWeight: actif ? 800 : 600,
                            color: actif ? texte : `${texte}c4`,
                          }}
                        >
                          {m}
                        </span>
                        {actif ? (
                          <span style={{fontSize: 40, color: accent}}>●</span>
                        ) : null}
                      </div>
                    );
                  })}
                </div>
              </div>
            </Cadre>

            {/* Marqueur : hors du cadre, a droite, a hauteur de la liste. */}
            {marqueur !== 'aucun' ? (
              <div
                style={{
                  position: 'absolute',
                  right: -18,
                  top: '54%',
                  width: 150,
                  height: 150,
                  borderRadius: 75,
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  backgroundColor: marqueur === 'question' ? `${accent2}26` : `${accent}26`,
                  border: `5px solid ${marqueur === 'question' ? accent2 : accent}`,
                  opacity: pMarqueur,
                  transform: `scale(${interpolate(pMarqueur, [0, 1], [0.4, 1]) * battement})`,
                  fontFamily: typo.titre.famille,
                  fontSize: 92,
                  fontWeight: 800,
                  color: marqueur === 'question' ? accent2 : accent,
                }}
              >
                {marqueur === 'question' ? '?' : '✓'}
              </div>
            ) : null}

            {/* Le curseur, par-dessus tout le reste. */}
            <div
              style={{
                position: 'absolute',
                left: `${curseurX}%`,
                top: `${curseurY}%`,
                // Retard du mouvement secondaire (regle 5) : l'ombre du
                // curseur suit d'un cheveu, ce qui lui donne du poids.
                filter: 'drop-shadow(0 6px 10px rgba(0,0,0,0.5))',
                pointerEvents: 'none',
              }}
            >
              <Curseur couleur={texte} />
            </div>
          </div>
        </div>
      </AbsoluteFill>
    </AbsoluteFill>
  );
};
