import React from 'react';
import {continueRender, delayRender, staticFile} from 'remotion';
import {loadFont} from '@remotion/fonts';
import type {CharteTokens, NiveauTypo} from './types';

/**
 * La typographie de la chaine, en trois niveaux.
 *
 * Avant le 16/09/2026, toute la chaine lisait `charte.typographie
 * .sous_titres.famille` — titres compris — et cette valeur etait
 * `"Arial, sans-serif"`. Une vidéo en Arial ne se lit pas comme une vidéo :
 * la police est ce que l'oeil identifie avant la composition, et c'etait le
 * plus grand ecart de rendu du depot pour le plus petit diff.
 *
 * Les fichiers sont **embarques** dans `public/fonts/` plutot que charges
 * depuis un CDN : un rendu ne doit pas dependre du reseau au moment ou il
 * tourne. Un poste hors ligne, un proxy capricieux, et c'est toute la video
 * qui repart en police systeme sans que personne le voie avant le CP3.
 */

// Outfit porte les titres : geometrique, tres lisible en gros et en gras,
// elle a une personnalite que les grotesques neutres n'ont pas. Inter porte
// le texte courant et les sous-titres : c'est elle qui tient a 44 px sur un
// telephone, ce qu'Outfit ne fait pas aussi bien.
const POLICES = [
  {family: 'Outfit', weight: '700', fichier: 'fonts/Outfit-700.woff2'},
  {family: 'Outfit', weight: '800', fichier: 'fonts/Outfit-800.woff2'},
  {family: 'Inter', weight: '600', fichier: 'fonts/Inter-600.woff2'},
  {family: 'Inter', weight: '700', fichier: 'fonts/Inter-700.woff2'},
];

const TITRE = "Outfit, 'Segoe UI', Arial, sans-serif";
const TEXTE = "Inter, 'Segoe UI', Arial, sans-serif";

/**
 * Le rendu attend les polices avant de photographier la premiere frame.
 *
 * Sans `delayRender`, Chromium dessine le texte dans la police de repli,
 * puis la vraie police arrive une frame plus tard : la video commence par un
 * saut typographique que personne ne voit sur une image fixe.
 *
 * L'echec est **volontairement non bloquant**. Si `public/fonts/` manque, on
 * rend en police de repli avec un avertissement, plutot que de faire echouer
 * un montage pour une question de fonte.
 */
const attente = delayRender('Chargement des polices de la charte');
Promise.all(
  POLICES.map((p) =>
    loadFont({family: p.family, url: staticFile(p.fichier), weight: p.weight, format: 'woff2'}),
  ),
)
  .then(() => continueRender(attente))
  .catch((e) => {
    // eslint-disable-next-line no-console
    console.warn(
      '[typographie] polices non chargees, rendu en police de repli :',
      e instanceof Error ? e.message : e,
    );
    continueRender(attente);
  });

export type NiveauResolu = {
  famille: string;
  taille_px: number;
  graisse: number;
  interlettrage: number;
};

const DEFAUTS: Record<'titre' | 'label' | 'sous_titres', NiveauResolu> = {
  // Interlettrage negatif : a 104 px, l'espacement par defaut d'une fonte
  // dessinee pour du texte courant fait flotter les mots.
  titre: {famille: TITRE, taille_px: 104, graisse: 800, interlettrage: -2},
  // Positif et en capitales : un petit label serre devient illisible.
  label: {famille: TITRE, taille_px: 52, graisse: 700, interlettrage: 1.5},
  sous_titres: {famille: TEXTE, taille_px: 64, graisse: 700, interlettrage: 0},
};

function resoudre(niveau: 'titre' | 'label' | 'sous_titres', declare?: NiveauTypo): NiveauResolu {
  const d = DEFAUTS[niveau];
  return {
    famille: declare?.famille ?? d.famille,
    taille_px: declare?.taille_px ?? d.taille_px,
    graisse: declare?.graisse ?? d.graisse,
    interlettrage: declare?.interlettrage ?? d.interlettrage,
  };
}

/**
 * Les trois niveaux, resolus depuis la charte.
 *
 * `typographie.sous_titres` ancien format (`{famille, taille_px, graisse}`)
 * n'est **plus** lu pour la famille : c'est lui qui imposait Arial partout.
 * Sa taille, elle, reste respectee — c'est un reglage que Franco a pu vouloir.
 */
export function niveaux(charte: CharteTokens) {
  const ancien = charte.typographie?.sous_titres;
  return {
    titre: resoudre('titre', charte.typographie?.titre),
    label: resoudre('label', charte.typographie?.label),
    sous_titres: resoudre('sous_titres', {taille_px: ancien?.taille_px}),
  };
}

/** Le niveau, pret a etaler dans un `style`. */
export function style(n: NiveauResolu): React.CSSProperties {
  return {
    fontFamily: n.famille,
    fontSize: n.taille_px,
    fontWeight: n.graisse,
    letterSpacing: n.interlettrage,
  };
}
