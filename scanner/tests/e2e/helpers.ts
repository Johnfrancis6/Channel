import type { Page } from '@playwright/test';

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
