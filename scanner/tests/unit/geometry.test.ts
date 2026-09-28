import { describe, expect, it } from 'vitest';
import type { Quad } from '../../src/shared/types';
import {
  applyHomography,
  clampQuad,
  cornerError,
  fitWithin,
  fullImageQuad,
  homography,
  isConvex,
  isUsableQuad,
  nextRotation,
  orderCorners,
  outputSize,
  polygonArea,
  quadIoU,
  rotatePoint,
  rotateSize,
  scaleQuad,
} from '../../src/scan/geometry';

const P = (x: number, y: number) => ({ x, y });
const square: Quad = [P(0, 0), P(100, 0), P(100, 100), P(0, 100)];

describe('orderCorners', () => {
  it('ordonne des points mélangés', () => {
    const q = orderCorners([P(100, 100), P(0, 0), P(0, 100), P(100, 0)]);
    expect(q).toEqual(square);
  });

  it('gère un document fortement incliné (≈ 45°)', () => {
    // Losange : haut, droite, bas, gauche.
    const q = orderCorners([P(50, 0), P(100, 50), P(50, 100), P(0, 50)]);
    // Le premier coin est celui dont x+y est minimal, puis sens horaire.
    expect(q[0]).toEqual(P(50, 0));
    expect(q[1]).toEqual(P(100, 50));
    expect(q[2]).toEqual(P(50, 100));
    expect(q[3]).toEqual(P(0, 50));
  });

  it('gère une perspective trapézoïdale', () => {
    const q = orderCorners([P(380, 900), P(20, 880), P(120, 60), P(300, 40)]);
    expect(q).toEqual([P(120, 60), P(300, 40), P(380, 900), P(20, 880)]);
  });

  it('refuse un nombre de points ≠ 4', () => {
    expect(() => orderCorners([P(0, 0)])).toThrow();
  });
});

describe('convexité et validité', () => {
  it('un carré est convexe, un quadrilatère croisé non', () => {
    expect(isConvex(square)).toBe(true);
    expect(isConvex([P(0, 0), P(100, 100), P(100, 0), P(0, 100)])).toBe(false);
  });

  it('un quadrilatère concave est refusé', () => {
    expect(isConvex([P(0, 0), P(100, 0), P(30, 30), P(0, 100)])).toBe(false);
  });

  it('isUsableQuad refuse les quadrilatères trop petits ou trop écrasés', () => {
    expect(isUsableQuad(square, 200, 200)).toBe(true);
    expect(isUsableQuad(scaleQuad(square, 0.1), 1000, 1000)).toBe(false);
    expect(isUsableQuad([P(0, 0), P(100, 0), P(200, 10), P(0, 10)], 200, 200)).toBe(false);
  });
});

describe('aires et IoU', () => {
  it('aire du carré', () => {
    expect(polygonArea(square)).toBe(10000);
  });

  it('IoU de deux carrés décalés de moitié = 1/3', () => {
    const b: Quad = [P(50, 0), P(150, 0), P(150, 100), P(50, 100)];
    expect(quadIoU(square, b)).toBeCloseTo(1 / 3, 6);
    expect(quadIoU(square, square)).toBeCloseTo(1, 6);
  });
});

describe('tailles', () => {
  it('outputSize prend le plus long des côtés opposés et respecte le plafond', () => {
    const q: Quad = [P(10, 0), P(90, 0), P(100, 200), P(0, 200)];
    expect(outputSize(q, 10000)).toEqual({ width: 100, height: 200 });
    expect(outputSize(q, 100)).toEqual({ width: 50, height: 100 });
  });

  it('fitWithin ne grossit jamais', () => {
    expect(fitWithin(400, 300, 3200)).toEqual({ width: 400, height: 300, scale: 1 });
    expect(fitWithin(4032, 3024, 3200)).toEqual({ width: 3200, height: 2400, scale: 3200 / 4032 });
  });

  it('rotations', () => {
    expect(rotateSize(100, 50, 90)).toEqual({ width: 50, height: 100 });
    expect(rotateSize(100, 50, 180)).toEqual({ width: 100, height: 50 });
    expect(nextRotation(270)).toBe(0);
    // Le coin haut-gauche d'une image 100×50 tournée de 90° part en haut à droite.
    expect(rotatePoint(P(0, 0), 100, 50, 90)).toEqual(P(50, 0));
    expect(rotatePoint(P(100, 50), 100, 50, 90)).toEqual(P(0, 100));
    expect(rotatePoint(P(10, 5), 100, 50, 180)).toEqual(P(90, 45));
    expect(rotatePoint(P(0, 0), 100, 50, 270)).toEqual(P(0, 100));
  });

  it('clampQuad et fullImageQuad', () => {
    expect(clampQuad([P(-5, -5), P(120, 0), P(100, 130), P(0, 100)], 100, 100)).toEqual(square);
    expect(fullImageQuad(100, 100, 0.1)).toEqual([P(10, 10), P(90, 10), P(90, 90), P(10, 90)]);
  });
});

describe('cornerError', () => {
  it('0 pour des coins identiques, insensible à l’ordre', () => {
    expect(cornerError(square, [square[2], square[0], square[3], square[1]] as Quad, 100, 100)).toBe(0);
  });

  it('rapporte le pire coin à la diagonale', () => {
    const d: Quad = [P(0, 0), P(100, 0), P(100, 100), P(10, 100)];
    expect(cornerError(d, square, 300, 400)).toBeCloseTo(10 / 500, 9);
  });
});

describe('homography', () => {
  it('envoie les 4 coins sources sur les 4 coins cibles, et reste cohérente à l’intérieur', () => {
    const dst: Quad = [P(120, 60), P(300, 40), P(380, 900), P(20, 880)];
    const H = homography(square, dst);
    square.forEach((p, i) => {
      const r = applyHomography(H, p);
      expect(r.x).toBeCloseTo(dst[i]!.x, 6);
      expect(r.y).toBeCloseTo(dst[i]!.y, 6);
    });
    // L'inverse ramène un point intérieur à sa place.
    const Hi = homography(dst, square);
    const m = applyHomography(Hi, applyHomography(H, P(37, 61)));
    expect(m.x).toBeCloseTo(37, 6);
    expect(m.y).toBeCloseTo(61, 6);
  });
});
