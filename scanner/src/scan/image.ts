// Chargement des photos et conversions canvas ↔ Blob.
import { fitWithin } from './geometry';

/** Côté long maximal de la photo source (limite de canvas iOS : 16,7 Mpx). */
export const MAX_SOURCE_SIDE = 3200;

export function loadImage(blob: Blob): Promise<HTMLImageElement> {
  return new Promise((resolve, reject) => {
    const url = URL.createObjectURL(blob);
    const img = new Image();
    img.onload = () => {
      URL.revokeObjectURL(url);
      resolve(img);
    };
    img.onerror = () => {
      URL.revokeObjectURL(url);
      reject(new Error('Image illisible'));
    };
    // Safari applique l'orientation EXIF lors du dessin dans un canvas (image-orientation: from-image).
    img.src = url;
  });
}

export function toCanvas(img: CanvasImageSource & { naturalWidth?: number; width: number; height: number; naturalHeight?: number }, max = Infinity): HTMLCanvasElement {
  const w0 = img.naturalWidth || img.width;
  const h0 = img.naturalHeight || img.height;
  const { width, height } = fitWithin(w0, h0, max);
  const c = document.createElement('canvas');
  c.width = width;
  c.height = height;
  const ctx = c.getContext('2d')!;
  ctx.imageSmoothingQuality = 'high';
  ctx.drawImage(img, 0, 0, width, height);
  return c;
}

export async function blobToCanvas(blob: Blob, max = Infinity): Promise<HTMLCanvasElement> {
  return toCanvas(await loadImage(blob), max);
}

export function canvasToBlob(c: HTMLCanvasElement, type = 'image/jpeg', quality = 0.85): Promise<Blob> {
  return new Promise((resolve, reject) =>
    c.toBlob((b) => (b ? resolve(b) : reject(new Error('Encodage de l’image impossible'))), type, quality),
  );
}

export async function thumbnail(c: HTMLCanvasElement, max = 320): Promise<Blob> {
  return canvasToBlob(toCanvas(c, max), 'image/jpeg', 0.75);
}

/** Libère la mémoire d'un canvas tout de suite (Safari tarde à le faire). */
export function releaseCanvas(c: HTMLCanvasElement | null | undefined) {
  if (!c) return;
  c.width = 0;
  c.height = 0;
}
