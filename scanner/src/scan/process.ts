// Redressement, rotation et filtres d'une page (OpenCV.js).
import type { FilterName, ImageType, Quad, Rotation } from '../shared/types';
import { outputSize } from './geometry';
import { free, type CV } from './opencv';

/** Côté long maximal de la page rendue (~200 dpi pour un A4). */
export const MAX_PAGE_SIDE = 2400;

export interface RenderSettings {
  corners: Quad;
  rotation: Rotation;
  filter: FilterName;
}

export function warp(cv: CV, src: CV, q: Quad, maxSide = MAX_PAGE_SIDE): CV {
  const { width, height } = outputSize(q, maxSide);
  const from = cv.matFromArray(4, 1, cv.CV_32FC2, q.flatMap((p) => [p.x, p.y]));
  const to = cv.matFromArray(4, 1, cv.CV_32FC2, [0, 0, width, 0, width, height, 0, height]);
  const M = cv.getPerspectiveTransform(from, to);
  const dst = new cv.Mat();
  cv.warpPerspective(src, dst, M, new cv.Size(width, height), cv.INTER_CUBIC, cv.BORDER_REPLICATE);
  free(from, to, M);
  return dst;
}

export function rotate(cv: CV, src: CV, r: Rotation): CV {
  if (r === 0) return src;
  const dst = new cv.Mat();
  const code = r === 90 ? cv.ROTATE_90_CLOCKWISE : r === 180 ? cv.ROTATE_180 : cv.ROTATE_90_COUNTERCLOCKWISE;
  cv.rotate(src, dst, code);
  free(src);
  return dst;
}

/**
 * Estime le fond (le papier) d'une image à 1 canal : on réduit, on dilate pour
 * effacer l'encre, on lisse, puis on remet à la taille d'origine.
 */
function background(cv: CV, ch: CV): CV {
  const f = 4;
  const small = new cv.Mat();
  cv.resize(ch, small, new cv.Size(Math.max(1, Math.round(ch.cols / f)), Math.max(1, Math.round(ch.rows / f))), 0, 0, cv.INTER_AREA);
  const k = cv.getStructuringElement(cv.MORPH_ELLIPSE, new cv.Size(7, 7));
  cv.dilate(small, small, k);
  cv.medianBlur(small, small, 7);
  const bg = new cv.Mat();
  cv.resize(small, bg, new cv.Size(ch.cols, ch.rows), 0, 0, cv.INTER_LINEAR);
  free(small, k);
  return bg;
}

/** Divise par le fond : papier uniformément blanc, ombres et dégradés effacés. */
function flatten(cv: CV, ch: CV): CV {
  const bg = background(cv, ch);
  const out = new cv.Mat();
  cv.divide(ch, bg, out, 255);
  free(bg);
  return out;
}

function lut(cv: CV, src: CV, fn: (v: number) => number): CV {
  const table = cv.matFromArray(1, 256, cv.CV_8UC1, Array.from({ length: 256 }, (_, v) => Math.max(0, Math.min(255, Math.round(fn(v))))));
  const dst = new cv.Mat();
  cv.LUT(src, table, dst);
  free(table);
  return dst;
}

export interface FilterParams {
  /** Taille du voisinage du seuillage adaptatif, en fraction de la largeur. */
  bwBlock: number;
  /** Constante soustraite à la moyenne locale (plus grand = moins de noir). */
  bwC: number;
  /** Gamma appliqué aux tons moyens pour « couleur améliorée » (> 1 = encre plus foncée). */
  enhancedGamma: number;
  enhancedSaturation: number;
}

export const DEFAULT_FILTER_PARAMS: FilterParams = {
  bwBlock: 1 / 40,
  bwC: 14,
  enhancedGamma: 1.6,
  enhancedSaturation: 1.3,
};

/** Applique un filtre ; renvoie un nouveau Mat (1 ou 4 canaux) et libère `src`. */
export function applyFilter(cv: CV, src: CV, filter: FilterName, p: FilterParams = DEFAULT_FILTER_PARAMS): CV {
  if (filter === 'original') return src;
  if (filter === 'gray' || filter === 'bw') {
    const gray = new cv.Mat();
    cv.cvtColor(src, gray, cv.COLOR_RGBA2GRAY);
    free(src);
    if (filter === 'gray') return gray;
    const flat = flatten(cv, gray);
    free(gray);
    // Léger lissage : supprime le grain du capteur dans les zones d'ombre sans empâter le texte.
    cv.GaussianBlur(flat, flat, new cv.Size(3, 3), 0);
    let block = Math.round(flat.cols * p.bwBlock) | 1;
    block = Math.max(15, block);
    const out = new cv.Mat();
    cv.adaptiveThreshold(flat, out, 255, cv.ADAPTIVE_THRESH_GAUSSIAN_C, cv.THRESH_BINARY, block, p.bwC);
    free(flat);
    // Les quelques pixels du bord viennent souvent du fond : liseré blanc pour un rendu net.
    const t = Math.max(2, Math.round(out.cols * 0.004));
    cv.rectangle(out, new cv.Point(0, 0), new cv.Point(out.cols - 1, out.rows - 1), new cv.Scalar(255), t);
    return out;
  }
  // Couleur améliorée : fond blanchi canal par canal, encre renforcée, couleurs ravivées.
  const rgb = new cv.Mat();
  cv.cvtColor(src, rgb, cv.COLOR_RGBA2RGB);
  free(src);
  const planes = new cv.MatVector();
  cv.split(rgb, planes);
  const flatPlanes = new cv.MatVector();
  for (let i = 0; i < 3; i++) {
    const ch = planes.get(i);
    const f = flatten(cv, ch);
    const g = lut(cv, f, (v) => 255 * Math.pow(v / 255, p.enhancedGamma));
    flatPlanes.push_back(g);
    free(ch, f, g);
  }
  const merged = new cv.Mat();
  cv.merge(flatPlanes, merged);
  free(rgb, planes, flatPlanes);
  const hsv = new cv.Mat();
  cv.cvtColor(merged, hsv, cv.COLOR_RGB2HSV);
  free(merged);
  const hsvPlanes = new cv.MatVector();
  cv.split(hsv, hsvPlanes);
  const s = hsvPlanes.get(1);
  const s2 = new cv.Mat();
  s.convertTo(s2, -1, p.enhancedSaturation, 0);
  hsvPlanes.set(1, s2);
  cv.merge(hsvPlanes, hsv);
  const out = new cv.Mat();
  cv.cvtColor(hsv, out, cv.COLOR_HSV2RGB);
  free(hsv, hsvPlanes, s, s2);
  return out;
}

/** Rend une page complète : redressement → rotation → filtre, dans un canvas. */
export function renderPage(cv: CV, original: HTMLCanvasElement, s: RenderSettings, maxSide = MAX_PAGE_SIDE, params?: FilterParams): HTMLCanvasElement {
  const src = cv.imread(original);
  let m: CV;
  try {
    m = warp(cv, src, s.corners, maxSide);
  } finally {
    free(src);
  }
  m = rotate(cv, m, s.rotation);
  m = applyFilter(cv, m, s.filter, params);
  const canvas = document.createElement('canvas');
  cv.imshow(canvas, m);
  free(m);
  return canvas;
}

export const processedTypeFor = (f: FilterName): ImageType => (f === 'bw' ? 'image/png' : 'image/jpeg');
