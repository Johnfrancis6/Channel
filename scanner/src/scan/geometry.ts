// Géométrie pure des coins du document : aucune dépendance au navigateur ni à OpenCV.
import type { Point, Quad, Rotation } from '../shared/types';

export const dist = (a: Point, b: Point) => Math.hypot(a.x - b.x, a.y - b.y);

/** Aire signée (formule du lacet) ; positive si les points tournent dans le sens horaire à l'écran (y vers le bas). */
export function signedArea(pts: Point[]): number {
  let s = 0;
  for (let i = 0; i < pts.length; i++) {
    const a = pts[i]!;
    const b = pts[(i + 1) % pts.length]!;
    s += a.x * b.y - b.x * a.y;
  }
  return s / 2;
}

export const polygonArea = (pts: Point[]) => Math.abs(signedArea(pts));

/**
 * Remet 4 points dans l'ordre haut-gauche, haut-droit, bas-droit, bas-gauche.
 * Tri angulaire autour du centre (robuste même pour un document très incliné,
 * contrairement à la méthode « somme / différence des coordonnées »).
 */
export function orderCorners(pts: Point[]): Quad {
  if (pts.length !== 4) throw new Error('orderCorners attend 4 points');
  const cx = pts.reduce((s, p) => s + p.x, 0) / 4;
  const cy = pts.reduce((s, p) => s + p.y, 0) / 4;
  // Sens horaire à l'écran, en partant de la gauche.
  const sorted = [...pts].sort((a, b) => Math.atan2(a.y - cy, a.x - cx) - Math.atan2(b.y - cy, b.x - cx));
  // Le coin haut-gauche est celui dont x + y est minimal.
  let start = 0;
  for (let i = 1; i < 4; i++) {
    if (sorted[i]!.x + sorted[i]!.y < sorted[start]!.x + sorted[start]!.y) start = i;
  }
  const q = [0, 1, 2, 3].map((i) => ({ ...sorted[(start + i) % 4]! }));
  return q as Quad;
}

function cross(o: Point, a: Point, b: Point) {
  return (a.x - o.x) * (b.y - o.y) - (a.y - o.y) * (b.x - o.x);
}

/** Vrai si le quadrilatère est strictement convexe (donc aussi non croisé). */
export function isConvex(q: Quad): boolean {
  let sign = 0;
  for (let i = 0; i < 4; i++) {
    const c = cross(q[i]!, q[(i + 1) % 4]!, q[(i + 2) % 4]!);
    if (Math.abs(c) < 1e-9) return false;
    const s = Math.sign(c);
    if (sign === 0) sign = s;
    else if (s !== sign) return false;
  }
  return true;
}

/** Quadrilatère utilisable pour un redressement : convexe, aire minimale, angles raisonnables. */
export function isUsableQuad(q: Quad, imageW: number, imageH: number, minAreaFraction = 0.02): boolean {
  if (!isConvex(q)) return false;
  if (polygonArea(q) < minAreaFraction * imageW * imageH) return false;
  for (let i = 0; i < 4; i++) {
    const p = q[(i + 3) % 4]!;
    const c = q[i]!;
    const n = q[(i + 1) % 4]!;
    const v1 = { x: p.x - c.x, y: p.y - c.y };
    const v2 = { x: n.x - c.x, y: n.y - c.y };
    const cos = (v1.x * v2.x + v1.y * v2.y) / (Math.hypot(v1.x, v1.y) * Math.hypot(v2.x, v2.y));
    const deg = (Math.acos(Math.max(-1, Math.min(1, cos))) * 180) / Math.PI;
    if (deg < 35 || deg > 145) return false;
  }
  return true;
}

export function clampQuad(q: Quad, w: number, h: number): Quad {
  return q.map((p) => ({ x: Math.min(Math.max(p.x, 0), w), y: Math.min(Math.max(p.y, 0), h) })) as Quad;
}

export function scaleQuad(q: Quad, sx: number, sy: number = sx): Quad {
  return q.map((p) => ({ x: p.x * sx, y: p.y * sy })) as Quad;
}

/** Cadre couvrant toute l'image, avec une marge relative (repli si la détection échoue). */
export function fullImageQuad(w: number, h: number, inset = 0): Quad {
  const dx = w * inset;
  const dy = h * inset;
  return [
    { x: dx, y: dy },
    { x: w - dx, y: dy },
    { x: w - dx, y: h - dy },
    { x: dx, y: h - dy },
  ];
}

/**
 * Taille de la page redressée : moyenne pondérée vers le plus long des côtés opposés
 * (la perspective raccourcit le côté le plus éloigné), bornée à `maxSide`.
 */
export function outputSize(q: Quad, maxSide = 2400): { width: number; height: number } {
  const [tl, tr, br, bl] = q;
  let w = Math.max(dist(tl, tr), dist(bl, br));
  let h = Math.max(dist(tl, bl), dist(tr, br));
  const k = Math.min(1, maxSide / Math.max(w, h));
  w = Math.max(1, Math.round(w * k));
  h = Math.max(1, Math.round(h * k));
  return { width: w, height: h };
}

/** Dimensions pour tenir dans un carré `max` sans agrandir. */
export function fitWithin(w: number, h: number, max: number): { width: number; height: number; scale: number } {
  const scale = Math.min(1, max / Math.max(w, h));
  return { width: Math.max(1, Math.round(w * scale)), height: Math.max(1, Math.round(h * scale)), scale };
}

export function rotateSize(w: number, h: number, r: Rotation): { width: number; height: number } {
  return r === 90 || r === 270 ? { width: h, height: w } : { width: w, height: h };
}

export const nextRotation = (r: Rotation): Rotation => (((r + 90) % 360) as Rotation);

/**
 * Transforme un point de l'image redressée (avant rotation, taille w×h) vers l'image
 * tournée de `r` degrés dans le sens horaire.
 */
export function rotatePoint(p: Point, w: number, h: number, r: Rotation): Point {
  switch (r) {
    case 0:
      return { ...p };
    case 90:
      return { x: h - p.y, y: p.x };
    case 180:
      return { x: w - p.x, y: h - p.y };
    case 270:
      return { x: p.y, y: w - p.x };
  }
}

/**
 * Erreur de détection : distance maximale entre coins homologues, rapportée à la
 * diagonale de l'image. 0 = parfait ; < 0,02 = excellent ; > 0,05 = à retoucher.
 */
export function cornerError(detected: Quad, truth: Quad, imageW: number, imageH: number): number {
  const d = orderCorners(detected);
  const t = orderCorners(truth);
  const diag = Math.hypot(imageW, imageH);
  return Math.max(...d.map((p, i) => dist(p, t[i]!))) / diag;
}

/** Intersection sur union de deux quadrilatères convexes (découpage de Sutherland–Hodgman). */
export function quadIoU(a: Quad, b: Quad): number {
  const clip = (subject: Point[], clipper: Point[]): Point[] => {
    let out = subject;
    const n = clipper.length;
    const orient = Math.sign(signedArea(clipper));
    for (let i = 0; i < n && out.length; i++) {
      const c1 = clipper[i]!;
      const c2 = clipper[(i + 1) % n]!;
      const inside = (p: Point) => orient * cross(c1, c2, p) >= 0;
      const input = out;
      out = [];
      for (let j = 0; j < input.length; j++) {
        const cur = input[j]!;
        const prev = input[(j + input.length - 1) % input.length]!;
        const inter = (): Point => {
          const x1 = prev.x, y1 = prev.y, x2 = cur.x, y2 = cur.y;
          const x3 = c1.x, y3 = c1.y, x4 = c2.x, y4 = c2.y;
          const den = (x1 - x2) * (y3 - y4) - (y1 - y2) * (x3 - x4);
          const t = ((x1 - x3) * (y3 - y4) - (y1 - y3) * (x3 - x4)) / den;
          return { x: x1 + t * (x2 - x1), y: y1 + t * (y2 - y1) };
        };
        if (inside(cur)) {
          if (!inside(prev)) out.push(inter());
          out.push(cur);
        } else if (inside(prev)) out.push(inter());
      }
    }
    return out;
  };
  const inter = polygonArea(clip(a, b));
  const union = polygonArea(a) + polygonArea(b) - inter;
  return union > 0 ? inter / union : 0;
}

/**
 * Homographie 3×3 (ligne par ligne) qui envoie `src[i]` sur `dst[i]`.
 * Sert aux tests et au générateur de documents synthétiques ; l'app utilise OpenCV.
 */
export function homography(src: Quad, dst: Quad): number[] {
  const A: number[][] = [];
  for (let i = 0; i < 4; i++) {
    const { x, y } = src[i]!;
    const { x: u, y: v } = dst[i]!;
    A.push([x, y, 1, 0, 0, 0, -u * x, -u * y, u]);
    A.push([0, 0, 0, x, y, 1, -v * x, -v * y, v]);
  }
  // Élimination de Gauss avec pivot partiel sur le système 8×8 augmenté.
  for (let c = 0; c < 8; c++) {
    let piv = c;
    for (let r = c + 1; r < 8; r++) if (Math.abs(A[r]![c]!) > Math.abs(A[piv]![c]!)) piv = r;
    [A[c], A[piv]] = [A[piv]!, A[c]!];
    const d = A[c]![c]!;
    if (Math.abs(d) < 1e-12) throw new Error('homographie dégénérée');
    for (let k = c; k < 9; k++) A[c]![k]! /= d;
    for (let r = 0; r < 8; r++) {
      if (r === c) continue;
      const f = A[r]![c]!;
      for (let k = c; k < 9; k++) A[r]![k]! -= f * A[c]![k]!;
    }
  }
  return [...A.map((row) => row[8]!), 1];
}

export function applyHomography(H: number[], p: Point): Point {
  const w = H[6]! * p.x + H[7]! * p.y + H[8]!;
  return { x: (H[0]! * p.x + H[1]! * p.y + H[2]!) / w, y: (H[3]! * p.x + H[4]! * p.y + H[5]!) / w };
}
