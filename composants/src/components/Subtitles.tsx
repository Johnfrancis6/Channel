import React from 'react';
import {AbsoluteFill, useCurrentFrame, useVideoConfig} from 'remotion';
import {niveaux, style} from '../typographie';
import type {CharteTokens, MotHorodate} from '../types';

type Props = {
  mots: MotHorodate[];
  charte: CharteTokens;
  // Nombre de mots affiches simultanement (fenetre glissante autour du mot actif).
  fenetre?: number;
};

/**
 * Recolle les morceaux d'un meme mot avant l'affichage.
 *
 * La transcription decoupe « GPT-6-Astra » en trois jetons horodates :
 * `GPT`, `-6`, `-Astra.`. Chacun a son propre debut et sa propre fin, ce qui
 * est exactement ce qu'il faut pour surligner la syllabe prononcee — mais
 * poses cote a cote avec l'espacement du conteneur, ils s'affichent
 * « GPT -6 -Astra ». Le defaut se voit sur n'importe quel nom de modele, et
 * il tombait ici sur les trois premieres secondes de la video.
 *
 * On ne fusionne donc pas les jetons : on les groupe. Le surlignage reste
 * mot a mot, seul l'espace saute.
 */
function souder(
  groupe: MotHorodate[],
  decalage: number,
): {mot: string; index: number}[][] {
  const blocs: {mot: string; index: number}[][] = [];
  groupe.forEach((m, i) => {
    const suite = /^[-'’]/.test(m.mot);
    if (suite && blocs.length > 0) {
      blocs[blocs.length - 1].push({mot: m.mot, index: decalage + i});
    } else {
      blocs.push([{mot: m.mot, index: decalage + i}]);
    }
  });
  return blocs;
}

// Sous-titres dynamiques cales sur 04_timestamps.json (§7.2, §8). Affiche
// une petite fenetre de mots autour de l'instant courant, avec le mot en
// cours de prononciation mis en avant.
export const Subtitles: React.FC<Props> = ({mots, charte, fenetre = 5}) => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const tSecondes = frame / fps;

  // Dernier mot commence a cet instant, pas seulement le mot en cours de
  // prononciation : entre deux mots il y a toujours un silence, et une
  // correspondance exacte (debut <= t < fin) faisait disparaitre les
  // sous-titres dans chacun de ces trous. En pratique ils clignotaient entre
  // chaque mot. On garde le groupe affiche pendant le silence, seule la mise
  // en avant du mot s'eteint.
  let indexActif = -1;
  for (let i = 0; i < mots.length; i++) {
    if (tSecondes >= mots[i].debut_s) {
      indexActif = i;
    } else {
      break;
    }
  }
  if (indexActif === -1) {
    return null;
  }
  const enCoursDePrononciation = tSecondes < mots[indexActif].fin_s;

  const debut = Math.max(0, indexActif - Math.floor(fenetre / 2));
  const fin = Math.min(mots.length, debut + fenetre);
  const groupe = mots.slice(debut, fin);

  return (
    <AbsoluteFill
      style={{
        alignItems: 'center',
        justifyContent: 'flex-end',
        paddingBottom: 220,
        pointerEvents: 'none',
      }}
    >
      <div
        style={{
          display: 'flex',
          flexWrap: 'wrap',
          justifyContent: 'center',
          maxWidth: '85%',
          gap: '0 0.4em',
          ...style(niveaux(charte).sous_titres),
          textShadow: '0 4px 16px rgba(0,0,0,0.6)',
        }}
      >
        {souder(groupe, debut).map((bloc) => (
          <span key={bloc[0].index} style={{whiteSpace: 'nowrap'}}>
            {bloc.map((j) => (
              <span
                key={j.index}
                style={{
                  color:
                    j.index === indexActif && enCoursDePrononciation
                      ? charte.couleurs.accent
                      : charte.couleurs.texte_principal,
                }}
              >
                {j.mot}
              </span>
            ))}
          </span>
        ))}
      </div>
    </AbsoluteFill>
  );
};
