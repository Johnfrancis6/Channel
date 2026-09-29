import type { OcrResult } from '../shared/types';
import { ocrToText } from '../ocr/text';

/** Texte de tout le document ; les pages sont séparées par un saut de page (\f). */
export function buildTxt(title: string, pages: (OcrResult | null)[]): string {
  const body = pages.map((o) => ocrToText(o)).join('\n\f\n');
  return `${title}\n\n${body}\n`;
}

/** Nom de fichier sûr à partir du titre. */
export function fileName(title: string, ext: string): string {
  const base = title.replace(/[\\/:*?"<>|\u0000-\u001f]+/g, '-').replace(/\s+/g, ' ').trim().slice(0, 80) || 'document';
  return `${base}.${ext}`;
}
