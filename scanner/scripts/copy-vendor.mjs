// Copie OpenCV.js et Tesseract.js dans public/vendor/ (ignoré par git).
import { copyFileSync, existsSync, mkdirSync, rmSync, statSync } from 'node:fs';
import { dirname, join } from 'node:path';
import { vendorFiles } from './vendor.mjs';

const pub = join(dirname(new URL(import.meta.url).pathname), '..', 'public');
rmSync(join(pub, 'vendor'), { recursive: true, force: true });
for (const [src, rel] of vendorFiles()) {
  const dest = join(pub, rel);
  mkdirSync(dirname(dest), { recursive: true });
  copyFileSync(src, dest);
  const mo = (statSync(dest).size / 1024 / 1024).toFixed(1);
  console.log(`vendor ${rel} (${mo} Mo)`);
  if (!existsSync(dest)) throw new Error(`copie ratée : ${rel}`);
}
