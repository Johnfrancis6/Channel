// Écrit le rapport du banc d'essai : rapport-qualite/index.html + resultats.json.
import { mkdirSync, writeFileSync } from 'node:fs';
import { join } from 'node:path';

export const REPORT_DIR = join(import.meta.dirname, '..', '..', 'rapport-qualite');

export interface Ligne {
  nom: string;
  source: 'synthétique' | 'exemple';
  [k: string]: unknown;
  images?: { titre: string; dataUrl: string }[];
}

function saveImage(nom: string, i: number, dataUrl: string): string {
  const m = dataUrl.match(/^data:image\/(\w+);base64,(.*)$/);
  if (!m) return '';
  const file = `${nom.replace(/[^\w.-]+/g, '_')}-${i}.${m[1] === 'jpeg' ? 'jpg' : m[1]}`;
  mkdirSync(join(REPORT_DIR, 'img'), { recursive: true });
  writeFileSync(join(REPORT_DIR, 'img', file), Buffer.from(m[2]!, 'base64'));
  return `img/${file}`;
}

export function ecrireRapport(titre: string, fichier: string, lignes: Ligne[], resume: Record<string, unknown>) {
  mkdirSync(REPORT_DIR, { recursive: true });
  const esc = (s: unknown) => String(s).replace(/[&<>]/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;' })[c]!);
  const json = lignes.map(({ images, ...rest }) => rest);
  writeFileSync(join(REPORT_DIR, `${fichier}.json`), JSON.stringify({ resume, lignes: json }, null, 2));
  const rows = lignes
    .map((l) => {
      const { images = [], nom, source, ...rest } = l;
      const imgs = images.map((im, i) => `<figure><img src="${saveImage(`${fichier}-${nom}`, i, im.dataUrl)}" loading="lazy"><figcaption>${esc(im.titre)}</figcaption></figure>`).join('');
      const kv = Object.entries(rest)
        .map(([k, v]) => `<b>${esc(k)}</b> ${esc(typeof v === 'number' ? Math.round(v * 10000) / 10000 : typeof v === 'object' ? JSON.stringify(v) : v)}`)
        .join(' · ');
      return `<section><h2>${esc(nom)} <small>${esc(source)}</small></h2><p>${kv}</p><div class="imgs">${imgs}</div></section>`;
    })
    .join('\n');
  const html = `<!doctype html><meta charset="utf-8"><title>${esc(titre)}</title>
<style>body{font:15px system-ui;margin:24px;background:#f8fafc}section{background:#fff;padding:12px 16px;margin:12px 0;border-radius:10px}
.imgs{display:flex;gap:12px;flex-wrap:wrap}figure{margin:0}img{max-height:420px;max-width:100%;border:1px solid #ccc}small{color:#64748b;font-weight:normal}pre{white-space:pre-wrap}</style>
<h1>${esc(titre)}</h1><pre>${esc(JSON.stringify(resume, null, 2))}</pre>${rows}`;
  writeFileSync(join(REPORT_DIR, `${fichier}.html`), html);
}
