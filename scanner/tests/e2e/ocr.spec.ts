// Banc d'essai de l'OCR : taux d'erreur de caractères (CER) de bout en bout
// (détection des bords → redressement → filtre → Tesseract), sur les documents
// synthétiques à texte connu, puis sur les photos de exemples/ qui ont un "texte".
import { expect, test } from '@playwright/test';
import { cer } from '../../src/ocr/text';
import { CAS_SYNTHETIQUES, listerExemples, ouvrirBanc } from './helpers';
import { ecrireRapport, type Ligne } from './rapport';

const FILTRES = ['enhanced', 'bw'] as const;

test('OCR : taux d’erreur de caractères', async ({ page }) => {
  await ouvrirBanc(page);
  const lignes: Ligne[] = [];
  const cers: Record<(typeof FILTRES)[number], number[]> = { enhanced: [], bw: [] };

  for (const cas of CAS_SYNTHETIQUES) {
    const verite = await page.evaluate(([id, o]) => (window as any).bench.synth(id, o), [cas.nom, cas] as const);
    const d = await page.evaluate((id) => (window as any).bench.detect(id), cas.nom);
    const ref = (verite.text as string[]).join('\n');
    const ligne: Ligne = { nom: cas.nom, source: 'synthétique' };
    for (const f of FILTRES) {
      const r = await page.evaluate(([id, q, filt]) => (window as any).bench.ocr(id, q, filt), [cas.nom, d.quad, f] as const);
      const e = cer(r.text, ref);
      cers[f].push(e);
      Object.assign(ligne, { [`cer_${f}`]: e, [`ms_${f}`]: r.ms, [`confiance_${f}`]: r.confidence });
      if (f === 'enhanced') ligne.texte = r.text.slice(0, 400);
    }
    lignes.push(ligne);
  }

  for (const ex of listerExemples().filter((e) => e.verite?.texte)) {
    await page.evaluate(([id, url]) => (window as any).bench.load(id, url), [ex.nom, ex.url] as const);
    const d = await page.evaluate((id) => (window as any).bench.detect(id), ex.nom);
    const ligne: Ligne = { nom: ex.nom, source: 'exemple' };
    for (const f of FILTRES) {
      const r = await page.evaluate(([id, q, filt]) => (window as any).bench.ocr(id, q, filt), [ex.nom, d.quad, f] as const);
      Object.assign(ligne, { [`cer_${f}`]: cer(r.text, ex.verite!.texte!), [`ms_${f}`]: r.ms, [`confiance_${f}`]: r.confidence });
    }
    lignes.push(ligne);
  }

  const moy = (a: number[]) => a.reduce((x, y) => x + y, 0) / a.length;
  const resume = {
    synthetiques: CAS_SYNTHETIQUES.length,
    cer_moyen_enhanced: moy(cers.enhanced),
    cer_max_enhanced: Math.max(...cers.enhanced),
    cer_moyen_bw: moy(cers.bw),
    cer_max_bw: Math.max(...cers.bw),
    exemples_avec_texte: lignes.filter((l) => l.source === 'exemple').length,
  };
  console.log('OCR :', JSON.stringify(resume));
  ecrireRapport('Banc d’essai — OCR', 'ocr', lignes, resume);
  // Texte imprimé net : moins de 5 % d'erreurs en moyenne avec le filtre par défaut.
  expect(resume.cer_moyen_enhanced).toBeLessThan(0.05);
});
