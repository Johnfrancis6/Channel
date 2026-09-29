import type { Page } from '@playwright/test';
import { existsSync, readdirSync, readFileSync } from 'node:fs';
import { join } from 'node:path';

/** Fabrique une photo synthétique (JPEG) dans le banc d'essai et renvoie ses octets. */
export async function photoSynthetique(page: Page, seed = 1011, background = 'bois'): Promise<Buffer> {
  for (let essai = 0; ; essai++) {
    try {
      await page.goto('/testbench.html');
      await page.waitForFunction(() => (window as any).bench);
      await page.evaluate(() => (window as any).bench.ready());
      break;
    } catch (e) {
      if (essai >= 2) throw e;
    }
  }
  const dataUrl: string = await page.evaluate(
    async ([seed, background]) => {
      const b = (window as any).bench;
      b.synth('p', { seed, background, skew: 1, shadow: false });
      return b.jpeg('p');
    },
    [seed, background] as const,
  );
  return Buffer.from(dataUrl.split(',')[1]!, 'base64');
}

// --- Banc d'essai (qualite.spec.ts, ocr.spec.ts) ---------------------------

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
