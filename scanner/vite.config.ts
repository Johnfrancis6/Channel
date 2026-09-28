import { readFileSync } from 'node:fs';
import { defineConfig, type Plugin } from 'vite';
import preact from '@preact/preset-vite';
// @ts-expect-error module JS sans déclarations de types
import { vendorDirs } from './scripts/vendor.mjs';

const vendor = vendorDirs() as Record<string, string>;

/** Émet dist/sw.js depuis src/sw.js, avec un identifiant de build et les dossiers vendor. */
function serviceWorker(): Plugin {
  return {
    name: 'scanner-sw',
    apply: 'build',
    generateBundle() {
      const source = readFileSync('src/sw.js', 'utf8')
        .replace('__BUILD_ID__', Date.now().toString(36))
        .replace('__VENDOR_DIRS__', JSON.stringify(Object.values(vendor)));
      this.emitFile({ type: 'asset', fileName: 'sw.js', source });
    },
  };
}

export default defineConfig({
  plugins: [preact(), serviceWorker()],
  define: {
    __VENDOR__: JSON.stringify(vendor),
  },
  build: {
    outDir: 'dist',
    target: 'safari15',
    sourcemap: true,
    // Seule l'app part en production ; testbench.html ne sert qu'au banc d'essai (vite dev).
    rollupOptions: { input: 'index.html' },
  },
  worker: { format: 'es' },
  server: {
    // `npx wrangler dev` sert l'API sur 8787 pendant le développement.
    proxy: { '/api': 'http://127.0.0.1:8787' },
  },
});
