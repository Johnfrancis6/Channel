// Banc d'essai de qualité : détection des bords (et OCR, voir ocr.spec.ts) sur des
// documents synthétiques à vérité connue, puis sur les photos de exemples/.
//
// Vérité terrain facultative pour une photo exemples/nom.jpg : exemples/nom.json =
//   { "coins": [[x,y],[x,y],[x,y],[x,y]], "texte": "…" }   (pixels de la photo d'origine)
import { expect, test, type Page } from '@playwright/test';
import { existsSync, readdirSync, readFileSync } from 'node:fs';
import { join } from 'node:path';
import type { Quad } from '../../src/shared/types';
import { cornerError, quadIoU } from '../../src/scan/geometry';
import { ecrireRapport, type Ligne } from './rapport';

const EXEMPLES = join(import.meta.dirname, '..', '..', 'exemples');
const IMG = /\.(jpe?g|png|webp)$/i;

export function listerExemples(): { nom: string; url: string; verite?: { coins?: number[][]; texte?: string } }[] {
  const out = [];
  for (const sous of ['', 'prive']) {
    const dir = join(EXEMPLES, sous);
    if (!existsSync(dir)) continue;
    for (const f of readdirSync(dir).sort()) {
      if (!IMG.test(f)) continue;
      const json = join(dir, f.replace(IMG, '.json'));
      out.push({
        nom: join(sous, f),
        url: `/exemples/${sous ? `${sous}/` : ''}${encodeURIComponent(f)}`,
        verite: existsSync(json) ? JSON.parse(readFileSync(json, 'utf8')) : undefined,
      });
    }
  }
  return out;
}

export async function ouvrirBanc(page: Page) {
  // Au premier lancement, vite peut recharger la page après avoir pré-optimisé les dépendances.
  for (let essai = 0; ; essai++) {
    try {
      await page.goto('/testbench.html');
      await page.waitForFunction(() => (window as any).bench);
      await page.evaluate(() => (window as any).bench.ready());
      return;
    } catch (e) {
      if (essai >= 2) throw e;
    }
  }
}

export const CAS_SYNTHETIQUES = (['bois', 'gris', 'beige', 'nappe'] as const).flatMap((background, b) =>
  [
    { skew: 0.3, shadow: false },
    { skew: 1, shadow: false },
    { skew: 1, shadow: true },
  ].map((o, i) => ({ nom: `${background}-${i}`, seed: 1000 + b * 10 + i, background, ...o })),
);

test('détection des bords', async ({ page }) => {
  await ouvrirBanc(page);
  const lignes: Ligne[] = [];
  const erreurs: number[] = [];

  for (const cas of CAS_SYNTHETIQUES) {
    const verite = await page.evaluate(([id, o]) => (window as any).bench.synth(id, o), [cas.nom, cas] as const);
    const d = await page.evaluate((id) => (window as any).bench.detect(id), cas.nom);
    const err = cornerError(d.quad, verite.quad, verite.width, verite.height);
    erreurs.push(err);
    const apercu = await page.evaluate(([id, q, t]) => (window as any).bench.overlay(id, q, t), [cas.nom, d.quad, verite.quad] as const);
    const rendu = await page.evaluate(([id, q]) => (window as any).bench.render(id, q, 'enhanced'), [cas.nom, d.quad] as const);
    lignes.push({
      nom: cas.nom,
      source: 'synthétique',
      trouve: d.found,
      methode: d.method,
      erreur: err,
      iou: quadIoU(d.quad, verite.quad),
      ms: d.ms,
      images: [
        { titre: 'détection (vert) / vérité (magenta)', dataUrl: apercu },
        { titre: `rendu « couleur améliorée » (${rendu.ms} ms)`, dataUrl: rendu.dataUrl },
      ],
    });
  }

  for (const ex of listerExemples()) {
    const info = await page.evaluate(([id, url]) => (window as any).bench.load(id, url), [ex.nom, ex.url] as const);
    const d = await page.evaluate((id) => (window as any).bench.detect(id), ex.nom);
    const coins = ex.verite?.coins;
    const verite = coins ? (coins.map(([x, y]) => ({ x: x! * info.scale, y: y! * info.scale })) as Quad) : undefined;
    const apercu = await page.evaluate(([id, q, t]) => (window as any).bench.overlay(id, q, t), [ex.nom, d.quad, verite] as const);
    const images = [{ titre: 'détection (vert) / vérité (magenta)', dataUrl: apercu }];
    for (const f of ['enhanced', 'bw'] as const) {
      const r = await page.evaluate(([id, q, filt]) => (window as any).bench.render(id, q, filt), [ex.nom, d.quad, f] as const);
      images.push({ titre: `${f} (${r.ms} ms)`, dataUrl: r.dataUrl });
    }
    const ligne: Ligne = { nom: ex.nom, source: 'exemple', trouve: d.found, methode: d.method, score: d.score, ms: d.ms, images };
    if (verite) {
      ligne.erreur = cornerError(d.quad, verite, info.width, info.height);
      ligne.iou = quadIoU(d.quad, verite);
    }
    lignes.push(ligne);
  }

  const reussis = erreurs.filter((e) => e < 0.02).length;
  const resume = {
    synthetiques: CAS_SYNTHETIQUES.length,
    reussis_erreur_inf_2pc: reussis,
    erreur_moyenne: erreurs.reduce((a, b) => a + b, 0) / erreurs.length,
    erreur_max: Math.max(...erreurs),
    exemples: lignes.filter((l) => l.source === 'exemple').length,
  };
  console.log('Détection :', JSON.stringify(resume));
  ecrireRapport('Banc d’essai — détection des bords', 'bords', lignes, resume);
  expect(reussis / CAS_SYNTHETIQUES.length).toBeGreaterThanOrEqual(0.9);
});
