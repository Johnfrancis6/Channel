// Détection automatique des bords du document (OpenCV.js).
//
// Travail sur une copie réduite (640 px) : plusieurs cartes binaires candidates,
// contours → enveloppe convexe → approximation à 4 sommets, puis on garde le
// quadrilatère au meilleur score (grand, bien rempli, pas collé au cadre photo).
import type { Point, Quad } from '../shared/types';
import { fitWithin, fullImageQuad, isUsableQuad, orderCorners, polygonArea, scaleQuad } from './geometry';
import { free, type CV } from './opencv';

export interface Detection {
  quad: Quad;
  /** Faux si aucun document n'a été trouvé (le cadre couvre alors toute l'image). */
  found: boolean;
  score: number;
  method: string;
  /** Meilleurs candidats (diagnostic du banc d'essai). */
  candidates?: { quad: Quad; score: number; method: string; contrast: number }[];
}

export interface DetectOptions {
  workSize?: number;
  /** Aire minimale du document, en fraction de l'image. */
  minArea?: number;
}

const WORK_SIZE = 640;

function median(gray: CV): number {
  const hist = new Uint32Array(256);
  const data: Uint8Array = gray.data;
  for (let i = 0; i < data.length; i++) hist[data[i]!]!++;
  let acc = 0;
  for (let v = 0; v < 256; v++) {
    acc += hist[v]!;
    if (acc >= data.length / 2) return v;
  }
  return 127;
}

interface Candidate {
  quad: Quad;
  score: number;
  method: string;
  contrast?: number;
}

function quadFromMat(m: CV): Point[] {
  const d: Int32Array = m.data32S;
  const pts: Point[] = [];
  for (let i = 0; i < m.rows; i++) pts.push({ x: d[i * 2]!, y: d[i * 2 + 1]! });
  return pts;
}

function collect(cv: CV, bin: CV, w: number, h: number, minArea: number, method: string, out: Candidate[]) {
  const contours = new cv.MatVector();
  const hier = new cv.Mat();
  cv.findContours(bin, contours, hier, cv.RETR_LIST, cv.CHAIN_APPROX_SIMPLE);
  const imgArea = w * h;
  for (let i = 0; i < contours.size(); i++) {
    const c = contours.get(i);
    const area = Math.abs(cv.contourArea(c));
    if (area < minArea * imgArea) {
      c.delete();
      continue;
    }
    const hull = new cv.Mat();
    cv.convexHull(c, hull, false, true);
    const hullArea = Math.abs(cv.contourArea(hull));
    const peri = cv.arcLength(hull, true);
    let pts: Point[] | null = null;
    let how = method;
    for (const eps of [0.015, 0.025, 0.04, 0.06, 0.09]) {
      const approx = new cv.Mat();
      cv.approxPolyDP(hull, approx, eps * peri, true);
      if (approx.rows === 4) pts = quadFromMat(approx);
      approx.delete();
      if (pts) break;
    }
    let penalty = 1;
    if (!pts) {
      // Pas de quadrilatère net (coin plié, doigt…) : rectangle d'aire minimale, moins fiable.
      const rect = cv.minAreaRect(hull);
      pts = cv.RotatedRect.points(rect).map((p: Point) => ({ x: p.x, y: p.y }));
      how += '+rect';
      penalty = 0.7;
    }
    hull.delete();
    c.delete();
    const quad = orderCorners(pts!);
    if (!isUsableQuad(quad, w, h, minArea)) continue;
    const qa = polygonArea(quad);
    // Rapport de remplissage : 1 si le contour épouse bien le quadrilatère.
    const fill = Math.min(hullArea, qa) / Math.max(hullArea, qa);
    // Un quadrilatère collé aux 4 bords est presque toujours le cadre de la photo.
    const m = 3;
    const onBorder = quad.every((p) => p.x <= m || p.y <= m || p.x >= w - m || p.y >= h - m);
    if (onBorder) penalty *= 0.4;
    out.push({ quad, score: (qa / imgArea) * fill * fill * penalty, method: how });
  }
  contours.delete();
  hier.delete();
}

/** Écart (0–1) de clarté et de désaturation entre l'intérieur du quadrilatère et une bande extérieure. */
function contrast(cv: CV, lum: CV, sat: CV, q: Quad, w: number, h: number): number {
  const inner = cv.Mat.zeros(h, w, cv.CV_8UC1);
  const outer = new cv.Mat();
  const ring = new cv.Mat();
  const pts = cv.matFromArray(4, 1, cv.CV_32SC2, q.flatMap((p) => [Math.round(p.x), Math.round(p.y)]));
  const vec = new cv.MatVector();
  vec.push_back(pts);
  cv.fillPoly(inner, vec, new cv.Scalar(255));
  const band = Math.max(6, Math.round(Math.max(w, h) * 0.025));
  const k = cv.getStructuringElement(cv.MORPH_RECT, new cv.Size(band * 2 + 1, band * 2 + 1));
  cv.dilate(inner, outer, k);
  cv.subtract(outer, inner, ring);
  // Intérieur rogné de la même bande : on compare les deux côtés du bord, pas tout le document.
  const core = new cv.Mat();
  cv.erode(inner, core, k);
  const edgeIn = new cv.Mat();
  cv.subtract(inner, core, edgeIn);
  let result = 0;
  if (cv.countNonZero(ring) > 50 && cv.countNonZero(edgeIn) > 50) {
    const dl = cv.mean(lum, edgeIn)[0] - cv.mean(lum, ring)[0];
    const ds = cv.mean(sat, ring)[0] - cv.mean(sat, edgeIn)[0];
    result = Math.max(dl, ds, 0) / 255;
  } else {
    // Quadrilatère collé au bord de la photo : pas de bande extérieure mesurable.
    result = 0.06;
  }
  free(inner, outer, ring, pts, vec, k, core, edgeIn);
  return result;
}

export function detectDocument(cv: CV, source: HTMLCanvasElement, opts: DetectOptions = {}): Detection {
  const W = source.width;
  const H = source.height;
  const minArea = opts.minArea ?? 0.1;
  const { width: w, height: h, scale } = fitWithin(W, H, opts.workSize ?? WORK_SIZE);

  const small = document.createElement('canvas');
  small.width = w;
  small.height = h;
  const ctx = small.getContext('2d')!;
  ctx.imageSmoothingQuality = 'high';
  ctx.drawImage(source, 0, 0, w, h);

  const src = cv.imread(small);
  const gray = new cv.Mat();
  const closed = new cv.Mat();
  const blurred = new cv.Mat();
  const sat = new cv.Mat();
  const edges = new cv.Mat();
  const bin = new cv.Mat();
  const kClose = cv.getStructuringElement(cv.MORPH_RECT, new cv.Size(9, 9));
  const kDilate = cv.getStructuringElement(cv.MORPH_RECT, new cv.Size(3, 3));
  let candidates: Candidate[] = [];
  try {
    cv.cvtColor(src, gray, cv.COLOR_RGBA2GRAY);
    // Fermeture : efface le texte (sombre, fin) pour que la page devienne une zone uniforme.
    cv.morphologyEx(gray, closed, cv.MORPH_CLOSE, kClose);
    cv.GaussianBlur(closed, blurred, new cv.Size(5, 5), 0);

    // Saturation : le papier est gris-blanc, la plupart des fonds (bois, nappe, table
    // beige) sont colorés. Ce canal résiste mieux aux ombres que la luminosité.
    const rgb = new cv.Mat();
    const hsv = new cv.Mat();
    const planes = new cv.MatVector();
    cv.cvtColor(src, rgb, cv.COLOR_RGBA2RGB);
    cv.cvtColor(rgb, hsv, cv.COLOR_RGB2HSV);
    cv.split(hsv, planes);
    const s = planes.get(1);
    cv.morphologyEx(s, s, cv.MORPH_OPEN, kClose);
    cv.GaussianBlur(s, sat, new cv.Size(5, 5), 0);
    free(rgb, hsv, planes, s);

    for (const [chan, name] of [
      [blurred, 'lum'],
      [sat, 'sat'],
    ] as const) {
      // 1. Contours de Canny, seuils calés sur la médiane du canal.
      const med = Math.max(20, median(chan));
      for (const [lo, hi] of [
        [0.66 * med, 1.33 * med],
        [0.33 * med, 0.66 * med],
      ] as const) {
        cv.Canny(chan, edges, Math.max(5, lo), Math.max(15, hi));
        cv.dilate(edges, edges, kDilate);
        collect(cv, edges, w, h, minArea, `canny-${name}`, candidates);
      }
      // 2. Seuillage d'Otsu : page claire (luminosité) ou peu saturée (saturation).
      cv.threshold(chan, bin, 0, 255, (name === 'lum' ? cv.THRESH_BINARY : cv.THRESH_BINARY_INV) + cv.THRESH_OTSU);
      collect(cv, bin, w, h, minArea, `otsu-${name}`, candidates);
    }

    // 3. Contraste : l'intérieur d'un vrai document est plus clair et moins saturé que
    //    la bande juste à l'extérieur. Écarte les grands quadrilatères pris dans un motif.
    candidates.sort((a, b) => b.score - a.score);
    candidates = candidates.slice(0, 12);
    for (const c of candidates) {
      const k = contrast(cv, blurred, sat, c.quad, w, h);
      c.contrast = k;
      c.score *= Math.max(0.05, Math.min(1, k / 0.4));
    }
  } finally {
    free(src, gray, closed, blurred, sat, edges, bin, kClose, kDilate);
  }

  candidates.sort((a, b) => b.score - a.score);
  const best = candidates[0];
  if (!best) {
    return { quad: fullImageQuad(W, H, 0.03), found: false, score: 0, method: 'aucun' };
  }
  return {
    quad: scaleQuad(best.quad, 1 / scale),
    found: true,
    score: best.score,
    method: best.method,
    candidates: candidates.slice(0, 5).map((c) => ({ ...c, quad: scaleQuad(c.quad, 1 / scale), contrast: c.contrast ?? 0 })),
  };
}
