// Générateur de « photos » synthétiques de documents, avec vérité terrain connue
// (coins exacts et texte exact). Sert au banc d'essai tant que exemples/ est vide,
// et comme non-régression ensuite.
import type { Quad } from '../shared/types';
import type { CV } from '../scan/opencv';
import { free } from '../scan/opencv';

export const SAMPLE_TEXT = [
  'Facture n° 2026-0412',
  'Date : 14 septembre 2026',
  'Objet : entretien de la chaudière et remplacement du thermostat.',
  'Le technicien est intervenu le mardi à 9 h 30 ; durée : deux heures.',
  'Pièces détachées : thermostat programmable, joint, raccord laiton.',
  'Montant hors taxes : 245,80 euros. TVA à 10 % : 24,58 euros.',
  'Total à régler : 270,38 euros, par virement avant le 30 octobre.',
  'Merci de rappeler la référence du dossier lors de votre paiement.',
  'Garantie : les pièces remplacées sont garanties un an.',
  'Pour toute question, écrivez-nous ou passez à l’atelier.',
];

export interface SynthOptions {
  seed: number;
  background: 'bois' | 'gris' | 'beige' | 'nappe';
  /** Inclinaison et perspective (0 = de face, 1 = forte). */
  skew: number;
  shadow: boolean;
  width?: number;
  height?: number;
}

export interface SynthResult {
  canvas: HTMLCanvasElement;
  quad: Quad;
  text: string[];
}

function rng(seed: number) {
  let s = seed >>> 0 || 1;
  return () => {
    s ^= s << 13;
    s ^= s >>> 17;
    s ^= s << 5;
    return ((s >>> 0) % 1_000_000) / 1_000_000;
  };
}

export function renderPaper(text = SAMPLE_TEXT, w = 1240, h = 1754): HTMLCanvasElement {
  const c = document.createElement('canvas');
  c.width = w;
  c.height = h;
  const g = c.getContext('2d')!;
  g.fillStyle = '#fbfaf6';
  g.fillRect(0, 0, w, h);
  g.fillStyle = '#1b1b1b';
  g.textBaseline = 'alphabetic';
  let y = 170;
  text.forEach((line, i) => {
    g.font = i === 0 ? 'bold 44px "DejaVu Serif", Georgia, serif' : '30px "DejaVu Serif", Georgia, serif';
    g.fillText(line, 110, y);
    y += i === 0 ? 90 : 64;
  });
  // Un tampon bleu et un trait, pour que « couleur améliorée » ait de la couleur à garder.
  g.strokeStyle = '#1d4ed8';
  g.lineWidth = 6;
  g.beginPath();
  g.arc(w - 260, h - 300, 110, 0, Math.PI * 2);
  g.stroke();
  g.fillStyle = '#1d4ed8';
  g.font = 'bold 34px sans-serif';
  g.fillText('PAYÉ', w - 310, h - 288);
  return c;
}

function paintBackground(g: CanvasRenderingContext2D, w: number, h: number, kind: SynthOptions['background'], r: () => number) {
  const base = { bois: '#6b4a2f', gris: '#5d6166', beige: '#d9cdb4', nappe: '#8c2f39' }[kind];
  g.fillStyle = base;
  g.fillRect(0, 0, w, h);
  if (kind === 'bois') {
    for (let i = 0; i < 160; i++) {
      g.strokeStyle = `rgba(${40 + r() * 40},${25 + r() * 25},${10 + r() * 15},${0.15 + r() * 0.25})`;
      g.lineWidth = 1 + r() * 6;
      const y = r() * h;
      g.beginPath();
      g.moveTo(0, y);
      g.bezierCurveTo(w / 3, y + (r() - 0.5) * 60, (2 * w) / 3, y + (r() - 0.5) * 60, w, y + (r() - 0.5) * 40);
      g.stroke();
    }
  } else if (kind === 'nappe') {
    g.fillStyle = 'rgba(255,255,255,0.18)';
    const s = 60;
    for (let x = 0; x < w; x += s * 2) g.fillRect(x, 0, s, h);
    for (let y = 0; y < h; y += s * 2) g.fillRect(0, y, w, s);
  } else {
    for (let i = 0; i < 4000; i++) {
      g.fillStyle = `rgba(0,0,0,${r() * 0.06})`;
      g.fillRect(r() * w, r() * h, 2 + r() * 4, 2 + r() * 4);
    }
  }
}

export function synthPhoto(cv: CV, o: SynthOptions): SynthResult {
  const r = rng(o.seed);
  const W = o.width ?? 2016;
  const H = o.height ?? 2688;
  const paper = renderPaper();
  const pw = paper.width;
  const ph = paper.height;

  // Placement : document centré, occupant 55–80 % de la hauteur, incliné et en perspective.
  const scale = ((0.55 + r() * 0.25) * H) / ph;
  const cx = W / 2 + (r() - 0.5) * W * 0.12;
  const cy = H / 2 + (r() - 0.5) * H * 0.1;
  const angle = (r() - 0.5) * 0.5 * o.skew;
  const hw = (pw * scale) / 2;
  const hh = (ph * scale) / 2;
  const base = [
    [-hw, -hh],
    [hw, -hh],
    [hw, hh],
    [-hw, hh],
  ].map(([x, y]) => ({ x: x!, y: y! }));
  // Perspective : le haut plus étroit que le bas (téléphone incliné vers l'avant).
  const k = 0.18 * o.skew * r();
  base[0]!.x *= 1 - k;
  base[1]!.x *= 1 - k;
  const jitter = () => (r() - 0.5) * 0.06 * o.skew * hw;
  const quad = base.map((p) => {
    const x = p.x + jitter();
    const y = p.y + jitter();
    return {
      x: cx + x * Math.cos(angle) - y * Math.sin(angle),
      y: cy + x * Math.sin(angle) + y * Math.cos(angle),
    };
  }) as Quad;

  const out = document.createElement('canvas');
  out.width = W;
  out.height = H;
  const g = out.getContext('2d')!;
  paintBackground(g, W, H, o.background, r);

  // Déformation du papier avec OpenCV, puis composition par masque.
  const src = cv.imread(paper);
  const bg = cv.imread(out);
  const from = cv.matFromArray(4, 1, cv.CV_32FC2, [0, 0, pw, 0, pw, ph, 0, ph]);
  const to = cv.matFromArray(4, 1, cv.CV_32FC2, quad.flatMap((p) => [p.x, p.y]));
  const M = cv.getPerspectiveTransform(from, to);
  const warped = new cv.Mat();
  cv.warpPerspective(src, warped, M, new cv.Size(W, H), cv.INTER_LINEAR, cv.BORDER_CONSTANT, new cv.Scalar(0, 0, 0, 0));
  const mask = new cv.Mat();
  const planes = new cv.MatVector();
  cv.split(warped, planes);
  const alpha = planes.get(3);
  cv.threshold(alpha, mask, 128, 255, cv.THRESH_BINARY);
  warped.copyTo(bg, mask);
  cv.imshow(out, bg);
  free(src, bg, from, to, M, warped, mask, planes, alpha);

  // Éclairage : léger vignettage, et une ombre portée de main/téléphone en option.
  const grad = g.createRadialGradient(W / 2, H / 2, Math.min(W, H) * 0.3, W / 2, H / 2, Math.max(W, H) * 0.75);
  grad.addColorStop(0, 'rgba(0,0,0,0)');
  grad.addColorStop(1, 'rgba(0,0,0,0.35)');
  g.fillStyle = grad;
  g.fillRect(0, 0, W, H);
  if (o.shadow) {
    const sg = g.createLinearGradient(0, 0, W, H * 0.3);
    sg.addColorStop(0, 'rgba(0,0,0,0.45)');
    sg.addColorStop(0.45, 'rgba(0,0,0,0.25)');
    sg.addColorStop(0.6, 'rgba(0,0,0,0)');
    g.fillStyle = sg;
    g.fillRect(0, 0, W, H);
  }
  // Bruit de capteur.
  const img = g.getImageData(0, 0, W, H);
  for (let i = 0; i < img.data.length; i += 4) {
    const n = (r() - 0.5) * 14;
    img.data[i] = img.data[i]! + n;
    img.data[i + 1] = img.data[i + 1]! + n;
    img.data[i + 2] = img.data[i + 2]! + n;
  }
  g.putImageData(img, 0, 0);
  return { canvas: out, quad, text: SAMPLE_TEXT };
}
