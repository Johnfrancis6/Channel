import { deflateSync } from 'node:zlib';
import { describe, expect, it } from 'vitest';
import { PDFDocument, StandardFonts } from 'pdf-lib';
// Import statique : pdf.js est lourd, son chargement ne doit pas compter dans le délai d'un test.
import * as pdfjs from 'pdfjs-dist/legacy/build/pdf.mjs';
import { buildPdf, makeEncodable } from '../../src/export/pdf';

/** PNG blanc minimal (niveaux de gris 8 bits), sans dépendance. */
function whitePng(w: number, h: number): Uint8Array {
  const crcTable = Array.from({ length: 256 }, (_, n) => {
    let c = n;
    for (let k = 0; k < 8; k++) c = c & 1 ? 0xedb88320 ^ (c >>> 1) : c >>> 1;
    return c >>> 0;
  });
  const crc = (buf: Buffer) => {
    let c = 0xffffffff;
    for (const b of buf) c = crcTable[(c ^ b) & 0xff]! ^ (c >>> 8);
    return (c ^ 0xffffffff) >>> 0;
  };
  const chunk = (type: string, data: Buffer) => {
    const len = Buffer.alloc(4);
    len.writeUInt32BE(data.length);
    const td = Buffer.concat([Buffer.from(type, 'ascii'), data]);
    const c = Buffer.alloc(4);
    c.writeUInt32BE(crc(td));
    return Buffer.concat([len, td, c]);
  };
  const ihdr = Buffer.alloc(13);
  ihdr.writeUInt32BE(w, 0);
  ihdr.writeUInt32BE(h, 4);
  ihdr[8] = 8; // profondeur
  ihdr[9] = 0; // niveaux de gris
  const raw = Buffer.alloc((w + 1) * h, 255);
  for (let y = 0; y < h; y++) raw[y * (w + 1)] = 0; // filtre « none »
  return new Uint8Array(
    Buffer.concat([Buffer.from([137, 80, 78, 71, 13, 10, 26, 10]), chunk('IHDR', ihdr), chunk('IDAT', deflateSync(raw)), chunk('IEND', Buffer.alloc(0))]),
  );
}

async function extract(bytes: Uint8Array) {
  const doc = await pdfjs.getDocument({ data: bytes, useSystemFonts: false, disableFontFace: true }).promise;
  const pages = [];
  for (let i = 1; i <= doc.numPages; i++) {
    const page = await doc.getPage(i);
    const vp = page.getViewport({ scale: 1 });
    const tc = await page.getTextContent();
    pages.push({
      width: vp.width,
      height: vp.height,
      items: (tc.items as { str: string; transform: number[]; width: number }[]).filter((it) => it.str.trim()),
    });
  }
  return pages;
}

describe('buildPdf', () => {
  it('produit un PDF dont le texte est extractible et placé sur les lignes', async () => {
    const W = 1240;
    const H = 1754;
    const bytes = await buildPdf(
      [
        {
          image: whitePng(W, H),
          type: 'image/png',
          width: W,
          height: H,
          ocr: {
            width: W,
            height: H,
            lines: [
              { text: 'Relevé de compte — août 2026', bbox: [100, 200, 900, 240], confidence: 90, baseline: 232 },
              { text: 'Total : 1 234,56 €', bbox: [100, 300, 500, 330], confidence: 88 },
              { text: 'ﬁn ≥ 3 ✓', bbox: [100, 400, 400, 430], confidence: 50 },
            ],
          },
        },
        { image: whitePng(H, W), type: 'image/png', width: H, height: W, ocr: null },
      ],
      'Relevé',
    );
    const pages = await extract(bytes);
    expect(pages).toHaveLength(2);
    expect(pages[0]!.width).toBeCloseTo(595.28, 1);
    expect(pages[0]!.height).toBeCloseTo((595.28 * H) / W, 1);
    // Page 2 en paysage : largeur A4 longue.
    expect(pages[1]!.width).toBeCloseTo(841.89, 1);

    // pdf.js découpe parfois une ligne en plusieurs morceaux : on recolle avec des espaces.
    const texts = pages[0]!.items.map((i) => i.str).join(' ');
    expect(texts).toContain('Relevé de compte');
    expect(texts).toContain('1 234,56 €');
    expect(texts).toContain('fin ? 3 ?'); // ligature décomposée, symboles hors WinAnsi remplacés

    // Position : x de la 1re ligne = 100 px × échelle, largeur ≈ largeur du cadre.
    const s = 595.28 / W;
    const first = pages[0]!.items.find((i) => i.str.startsWith('Relevé'))!;
    expect(first.transform[4]).toBeCloseTo(100 * s, 0);
    expect(first.transform[5]).toBeCloseTo(pages[0]!.height - 232 * s, 0);
    expect(first.width).toBeGreaterThan(800 * s * 0.95);
    expect(first.width).toBeLessThan(800 * s * 1.05);
  });

  it('le texte est invisible (mode de rendu 3)', async () => {
    const bytes = await buildPdf(
      [{ image: whitePng(100, 100), type: 'image/png', width: 100, height: 100, ocr: { width: 100, height: 100, lines: [{ text: 'x', bbox: [0, 0, 50, 10], confidence: 1 }] } }],
      't',
    );
    const doc = await pdfjs.getDocument({ data: bytes }).promise;
    const ops = await (await doc.getPage(1)).getOperatorList();
    const modes = ops.fnArray.flatMap((fn, i) => (fn === pdfjs.OPS.setTextRenderingMode ? [ops.argsArray[i][0]] : []));
    expect(modes).toEqual([3]);
  });
});

describe('makeEncodable', () => {
  it('garde les accents français et remplace le reste', async () => {
    const doc = await PDFDocument.create();
    const f = await doc.embedFont(StandardFonts.Helvetica);
    const enc = makeEncodable(f);
    expect(enc('Œuvre à l’été : « ça coûte 5 € »')).toBe('Œuvre à l’été : « ça coûte 5 € »');
    expect(enc('ą ĉ')).toBe('a c');
    expect(enc('日本')).toBe('??');
  });
});
