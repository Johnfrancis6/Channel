// Banc d'essai piloté par Playwright (tests/e2e/qualite.spec.ts) : expose window.bench.
// Servi uniquement par `vite` en développement, jamais inclus dans le build.
import type { FilterName, Quad } from '../shared/types';
import { detectDocument } from '../scan/detect';
import { blobToCanvas, canvasToBlob } from '../scan/image';
import { loadOpenCV, type CV } from '../scan/opencv';
import { DEFAULT_FILTER_PARAMS, renderPage, type FilterParams } from '../scan/process';
import { MAX_SOURCE_SIDE } from '../scan/image';
import { synthPhoto, type SynthOptions } from './synth';
import { recognize } from '../ocr/ocr';
import { ocrToText } from '../ocr/text';

let cv: CV;
const images = new Map<string, HTMLCanvasElement>();

const toDataUrl = async (c: HTMLCanvasElement, type = 'image/jpeg') => {
  const b = await canvasToBlob(c, type, 0.8);
  return await new Promise<string>((res) => {
    const fr = new FileReader();
    fr.onload = () => res(fr.result as string);
    fr.readAsDataURL(b);
  });
};

const bench = {
  async ready() {
    cv = await loadOpenCV();
    return true;
  },
  /** Crée une photo synthétique, la garde sous `id`, renvoie la vérité terrain. */
  synth(id: string, o: SynthOptions) {
    const s = synthPhoto(cv, o);
    images.set(id, s.canvas);
    return { quad: s.quad, text: s.text, width: s.canvas.width, height: s.canvas.height };
  },
  /** Charge une image (URL servie par vite) sous `id`, réduite comme dans l'app. */
  async load(id: string, url: string) {
    const blob = await (await fetch(url)).blob();
    const full = await blobToCanvas(blob);
    const c = await blobToCanvas(blob, MAX_SOURCE_SIDE);
    images.set(id, c);
    return { width: c.width, height: c.height, scale: c.width / full.width };
  },
  /** Exporte une image du banc en JPEG (data URL), comme une photo d'iPhone. */
  jpeg(id: string) {
    return toDataUrl(images.get(id)!);
  },
  detect(id: string) {
    const t0 = performance.now();
    const d = detectDocument(cv, images.get(id)!);
    return { ...d, ms: Math.round(performance.now() - t0) };
  },
  async render(id: string, quad: Quad, filter: FilterName, params?: Partial<FilterParams>) {
    const t0 = performance.now();
    const c = renderPage(cv, images.get(id)!, { corners: quad, rotation: 0, filter }, undefined, { ...DEFAULT_FILTER_PARAMS, ...params });
    const ms = Math.round(performance.now() - t0);
    return { ms, width: c.width, height: c.height, dataUrl: await toDataUrl(c, filter === 'bw' ? 'image/png' : 'image/jpeg') };
  },
  /** Redresse, filtre puis lit le texte, comme l'app (mêmes réglages Tesseract). */
  async ocr(id: string, quad: Quad, filter: FilterName) {
    const c = renderPage(cv, images.get(id)!, { corners: quad, rotation: 0, filter });
    const blob = await canvasToBlob(c, filter === 'bw' ? 'image/png' : 'image/jpeg', 0.85);
    const t0 = performance.now();
    const r = await recognize(blob, c.width, c.height);
    const ms = Math.round(performance.now() - t0);
    const conf = r.lines.length ? r.lines.reduce((a, l) => a + l.confidence, 0) / r.lines.length : 0;
    return { ms, text: ocrToText(r), lines: r.lines.length, confidence: Math.round(conf) };
  },
  /** Aperçu de la photo avec le quadrilatère détecté (vert) et la vérité (magenta). */
  async overlay(id: string, detected: Quad, truth?: Quad) {
    const src = images.get(id)!;
    const k = Math.min(1, 900 / Math.max(src.width, src.height));
    const c = document.createElement('canvas');
    c.width = Math.round(src.width * k);
    c.height = Math.round(src.height * k);
    const g = c.getContext('2d')!;
    g.drawImage(src, 0, 0, c.width, c.height);
    const draw = (q: Quad, color: string, w: number) => {
      g.strokeStyle = color;
      g.lineWidth = w;
      g.beginPath();
      q.forEach((p, i) => (i ? g.lineTo(p.x * k, p.y * k) : g.moveTo(p.x * k, p.y * k)));
      g.closePath();
      g.stroke();
    };
    if (truth) draw(truth, '#ff00ff', 5);
    draw(detected, '#00e676', 3);
    return toDataUrl(c);
  },
};

(window as unknown as { bench: typeof bench }).bench = bench;
document.getElementById('etat')!.textContent = 'prêt';
