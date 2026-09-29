// PDF cherchable : l'image de chaque page en fond, et par-dessus le texte OCR en mode
// de rendu 3 (invisible), placé et étiré ligne par ligne sur les cadres reconnus.
import {
  beginText,
  endText,
  PDFDocument,
  type PDFFont,
  setCharacterSqueeze,
  setFontAndSize,
  setTextMatrix,
  setTextRenderingMode,
  showText,
  StandardFonts,
  TextRenderingMode,
} from 'pdf-lib';
import type { ImageType, OcrResult } from '../shared/types';

export interface PdfPageInput {
  image: Uint8Array;
  type: ImageType;
  width: number;
  height: number;
  ocr: OcrResult | null;
}

const A4_SHORT = 595.28;
const A4_LONG = 841.89;

/** Rend un texte encodable en WinAnsi (police standard Helvetica). */
export function makeEncodable(font: PDFFont) {
  const cache = new Map<string, string>();
  const ok = (ch: string) => {
    try {
      font.encodeText(ch);
      return true;
    } catch {
      return false;
    }
  };
  return (text: string): string => {
    let out = '';
    // NFKC : ligatures (ﬁ → fi), espaces insécables fines, etc.
    for (const ch of text.normalize('NFKC')) {
      let r = cache.get(ch);
      if (r === undefined) {
        if (ok(ch)) r = ch;
        else {
          const base = ch.normalize('NFD').replace(/\p{M}/gu, '');
          r = base && ok(base) ? base : '?';
        }
        cache.set(ch, r);
      }
      out += r;
    }
    return out;
  };
}

export async function buildPdf(pages: PdfPageInput[], title: string): Promise<Uint8Array> {
  const pdf = await PDFDocument.create();
  pdf.setTitle(title);
  pdf.setCreator('Scanner');
  pdf.setProducer('Scanner (pdf-lib)');
  pdf.setLanguage('fr-FR');
  const font = await pdf.embedFont(StandardFonts.Helvetica);
  const encodable = makeEncodable(font);

  for (const p of pages) {
    const img = p.type === 'image/png' ? await pdf.embedPng(p.image) : await pdf.embedJpg(p.image);
    // Largeur A4 (ou hauteur A4 si la page est en paysage), proportions de l'image conservées.
    const pw = p.width > p.height ? A4_LONG : A4_SHORT;
    const ph = (pw * p.height) / p.width;
    const page = pdf.addPage([pw, ph]);
    page.drawImage(img, { x: 0, y: 0, width: pw, height: ph });

    const lines = p.ocr?.lines ?? [];
    if (!lines.length) continue;
    const s = pw / (p.ocr!.width || p.width);
    const fontKey = page.node.newFontDictionary(font.name, font.ref);
    const ops = [beginText(), setTextRenderingMode(TextRenderingMode.Invisible)];
    for (const l of lines) {
      const text = encodable(l.text.trim());
      if (!text) continue;
      const [x0, y0, x1, y1] = l.bbox;
      const boxW = (x1 - x0) * s;
      const boxH = (y1 - y0) * s;
      if (boxW <= 0 || boxH <= 0) continue;
      // Corps ≈ hauteur du cadre (jambages compris) ; ligne de base fournie par Tesseract sinon estimée.
      const size = Math.max(1, boxH * 0.9);
      const base = l.baseline ?? y1 - (y1 - y0) * 0.22;
      const tw = font.widthOfTextAtSize(text, size);
      const squeeze = tw > 0 ? Math.min(1000, Math.max(5, (boxW / tw) * 100)) : 100;
      ops.push(setFontAndSize(fontKey, size), setCharacterSqueeze(squeeze), setTextMatrix(1, 0, 0, 1, x0 * s, ph - base * s), showText(font.encodeText(text)));
    }
    ops.push(endText());
    page.pushOperators(...ops);
  }
  return pdf.save();
}
