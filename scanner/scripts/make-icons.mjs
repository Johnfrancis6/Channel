// Génère les icônes PNG à partir de public/icons/icon.svg (à relancer si le SVG change).
// Usage : node scripts/make-icons.mjs
import { chromium } from '@playwright/test';
import { readFileSync } from 'node:fs';
import { dirname, join } from 'node:path';

const dir = join(dirname(new URL(import.meta.url).pathname), '..', 'public', 'icons');
const svg = readFileSync(join(dir, 'icon.svg'), 'utf8');
const browser = await chromium.launch({ executablePath: process.env.CHROMIUM_PATH || undefined });
const page = await browser.newPage();
for (const [name, size, pad] of [
  ['apple-touch-icon.png', 180, 0],
  ['icon-192.png', 192, 0],
  ['icon-512.png', 512, 0],
  // Icône « maskable » : le dessin reste dans la zone sûre (80 %).
  ['icon-maskable-512.png', 512, 0.1],
]) {
  await page.setViewportSize({ width: size, height: size });
  const inner = size * (1 - 2 * pad);
  await page.setContent(
    `<body style="margin:0;background:#0f172a;display:grid;place-items:center;height:${size}px">` +
      `<div style="width:${inner}px;height:${inner}px">${svg.replace('<svg ', '<svg width="100%" height="100%" ')}</div></body>`,
  );
  await page.screenshot({ path: join(dir, name) });
  console.log(name);
}
await browser.close();
