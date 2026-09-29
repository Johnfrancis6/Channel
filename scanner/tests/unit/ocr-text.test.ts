import { describe, expect, it } from 'vitest';
import { cer, lineAt, linesFromBlocks, ocrToText } from '../../src/ocr/text';
import { buildTxt, fileName } from '../../src/export/txt';

const bb = (x0: number, y0: number, x1: number, y1: number) => ({ x0, y0, x1, y1 });

describe('linesFromBlocks', () => {
  const blocks = [
    {
      paragraphs: [
        {
          lines: [
            { text: 'Bonjour  le monde\n', confidence: 91.4, bbox: bb(10, 10, 200, 40), baseline: bb(10, 34, 200, 36) },
            { text: '   \n', confidence: 10, bbox: bb(0, 0, 1, 1) },
          ],
        },
        { lines: [{ text: 'Deuxième paragraphe', confidence: 80, bbox: bb(10, 60, 220, 90) }] },
      ],
    },
  ];

  it('nettoie, ignore les lignes vides, garde cadre, ligne de base et paragraphe', () => {
    const lines = linesFromBlocks(blocks);
    expect(lines).toEqual([
      { text: 'Bonjour le monde', bbox: [10, 10, 200, 40], confidence: 91, para: 0, baseline: 35 },
      { text: 'Deuxième paragraphe', bbox: [10, 60, 220, 90], confidence: 80, para: 1 },
    ]);
  });

  it('ocrToText sépare les paragraphes par une ligne vide', () => {
    const lines = linesFromBlocks(blocks);
    expect(ocrToText({ width: 300, height: 100, lines })).toBe('Bonjour le monde\n\nDeuxième paragraphe');
    expect(ocrToText(null)).toBe('');
  });

  it('buildTxt et fileName', () => {
    const o = { width: 1, height: 1, lines: linesFromBlocks(blocks) };
    expect(buildTxt('Titre', [o, null])).toBe('Titre\n\nBonjour le monde\n\nDeuxième paragraphe\n\f\n\n');
    expect(fileName('Facture: EDF / mars?', 'pdf')).toBe('Facture- EDF - mars-.pdf');
    expect(fileName('   ', 'txt')).toBe('document.txt');
  });
});

describe('lineAt', () => {
  const lines = linesFromBlocks([
    { paragraphs: [{ lines: [
      { text: 'a', confidence: 90, bbox: bb(10, 10, 100, 30) },
      { text: 'b', confidence: 90, bbox: bb(10, 40, 100, 60) },
    ] }] },
  ]);
  it('trouve la ligne sous le doigt, ou la plus proche', () => {
    expect(lineAt(lines, 50, 20)).toBe(0);
    expect(lineAt(lines, 50, 50)).toBe(1);
    expect(lineAt(lines, 500, 58)).toBe(1);
    expect(lineAt([], 0, 0)).toBe(-1);
  });
});

describe('cer', () => {
  it('0 si identique (espaces normalisés), 1 si tout est faux', () => {
    expect(cer('un  texte\n', 'un texte')).toBe(0);
    expect(cer('abc', 'xyz')).toBe(1);
    expect(cer('chat', 'chats')).toBeCloseTo(0.2);
  });
});
