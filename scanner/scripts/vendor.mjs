// Fichiers lourds servis depuis /vendor/ (OpenCV.js, Tesseract.js) : chemins versionnés,
// pour que le service worker puisse les garder en cache indéfiniment.
import { readFileSync } from 'node:fs';
import { createRequire } from 'node:module';
import { dirname, join } from 'node:path';

const require = createRequire(import.meta.url);
const root = join(dirname(new URL(import.meta.url).pathname), '..');
const pkgDir = (name) => dirname(require.resolve(`${name}/package.json`, { paths: [root] }));
const version = (name) => JSON.parse(readFileSync(join(pkgDir(name), 'package.json'), 'utf8')).version;

export function vendorDirs() {
  return {
    opencv: `/vendor/opencv-${version('@techstark/opencv-js')}`,
    tesseract: `/vendor/tesseract-${version('tesseract.js')}`,
    tesseractCore: `/vendor/tesseract-core-${version('tesseract.js-core')}`,
    tessdata: `/vendor/tessdata-fra-${version('@tesseract.js-data/fra')}`,
  };
}

/** [source, destination relative à public/] */
export function vendorFiles() {
  const d = vendorDirs();
  const core = pkgDir('tesseract.js-core');
  return [
    [join(pkgDir('@techstark/opencv-js'), 'dist/opencv.js'), `${d.opencv}/opencv.js`],
    [join(pkgDir('tesseract.js'), 'dist/worker.min.js'), `${d.tesseract}/worker.min.js`],
    // Mode LSTM seul : tesseract.js choisit la variante selon le support SIMD du navigateur.
    ...['lstm', 'simd-lstm', 'relaxedsimd-lstm'].map((v) => [
      join(core, `tesseract-core-${v}.wasm.js`),
      `${d.tesseractCore}/tesseract-core-${v}.wasm.js`,
    ]),
    [join(pkgDir('@tesseract.js-data/fra'), '4.0.0_best_int/fra.traineddata.gz'), `${d.tessdata}/fra.traineddata.gz`],
  ];
}
