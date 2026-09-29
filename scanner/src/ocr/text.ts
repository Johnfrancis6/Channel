// Conversion des résultats Tesseract en lignes, et des lignes en texte (logique pure).
import type { OcrLine, OcrResult } from '../shared/types';

interface TBbox {
  x0: number;
  y0: number;
  x1: number;
  y1: number;
}
export interface TLine {
  text: string;
  confidence: number;
  bbox: TBbox;
  baseline?: TBbox;
}
export interface TBlock {
  paragraphs: { lines: TLine[] }[];
}

export function linesFromBlocks(blocks: TBlock[] | null | undefined): OcrLine[] {
  const out: OcrLine[] = [];
  let para = 0;
  for (const b of blocks ?? []) {
    for (const p of b.paragraphs) {
      for (const l of p.lines) {
        const text = l.text.replace(/\s+$/u, '').replace(/[ \t]+/g, ' ');
        if (!text.trim()) continue;
        const { x0, y0, x1, y1 } = l.bbox;
        const line: OcrLine = { text, bbox: [x0, y0, x1, y1], confidence: Math.round(l.confidence), para };
        if (l.baseline && l.baseline.y0 >= y0 && l.baseline.y0 <= y1 + 2) {
          line.baseline = Math.round((l.baseline.y0 + l.baseline.y1) / 2);
        }
        out.push(line);
      }
      para++;
    }
  }
  return out;
}

/** Texte d'une page : une ligne par ligne reconnue, une ligne vide entre paragraphes. */
export function ocrToText(ocr: OcrResult | null | undefined): string {
  if (!ocr) return '';
  let s = '';
  let prev: number | undefined;
  for (const l of ocr.lines) {
    if (s && l.para !== undefined && prev !== undefined && l.para !== prev) s += '\n';
    s += `${l.text}\n`;
    prev = l.para;
  }
  return s.trimEnd();
}

/** Index de la ligne dont le cadre contient le point (ou la plus proche verticalement). */
export function lineAt(lines: OcrLine[], x: number, y: number): number {
  let best = -1;
  let bestD = Infinity;
  lines.forEach((l, i) => {
    const [x0, y0, x1, y1] = l.bbox;
    const dx = x < x0 ? x0 - x : x > x1 ? x - x1 : 0;
    const dy = y < y0 ? y0 - y : y > y1 ? y - y1 : 0;
    const d = dy * 3 + dx; // la proximité verticale compte davantage
    if (d < bestD) {
      bestD = d;
      best = i;
    }
  });
  return best;
}

/** Taux d'erreur de caractères (distance de Levenshtein / longueur de la référence). */
export function cer(hyp: string, ref: string): number {
  const norm = (s: string) => s.replace(/\s+/g, ' ').trim();
  const a = norm(hyp);
  const b = norm(ref);
  if (!b.length) return a.length ? 1 : 0;
  let prev = Array.from({ length: b.length + 1 }, (_, j) => j);
  for (let i = 1; i <= a.length; i++) {
    const cur = [i];
    for (let j = 1; j <= b.length; j++) {
      cur[j] = Math.min(prev[j]! + 1, cur[j - 1]! + 1, prev[j - 1]! + (a[i - 1] === b[j - 1] ? 0 : 1));
    }
    prev = cur;
  }
  return prev[b.length]! / b.length;
}
