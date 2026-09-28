// Modèle d'un document en cours d'édition, et opérations de scan sur ses pages.
import type { DocumentDetail, FileKind, FilterName, ImageType, OcrResult, PageMeta, Quad, Rotation } from '../shared/types';
import { detectDocument, type Detection } from '../scan/detect';
import { blobToCanvas, canvasToBlob, MAX_SOURCE_SIDE, releaseCanvas, thumbnail } from '../scan/image';
import { loadOpenCV } from '../scan/opencv';
import { processedTypeFor, renderPage } from '../scan/process';
import { api } from './api';

export interface PageState {
  id: string;
  corners: Quad;
  rotation: Rotation;
  filter: FilterName;
  width: number;
  height: number;
  processedType: ImageType;
  ocr: OcrResult | null;
  /** Fichiers présents en mémoire (absents tant qu'une page chargée du cloud n'est pas modifiée). */
  original?: Blob;
  processed?: Blob;
  thumb?: Blob;
  /** URL d'affichage : blob: local, ou /api/… pour une page chargée du cloud. */
  processedUrl: string;
  thumbUrl: string;
  /** Fichiers modifiés depuis le dernier enregistrement. */
  dirty: FileKind[];
}

export interface DocState {
  id: string | null;
  title: string;
  pages: PageState[];
  /** Vrai si quelque chose (titre, pages, texte) n'est pas encore enregistré. */
  dirty: boolean;
}

export const newId = () => crypto.randomUUID();

export function defaultTitle(d = new Date()): string {
  const date = d.toLocaleDateString('fr-FR');
  const time = d.toLocaleTimeString('fr-FR', { hour: '2-digit', minute: '2-digit' });
  return `Scan du ${date} à ${time}`;
}

export const emptyDoc = (): DocState => ({ id: null, title: defaultTitle(), pages: [], dirty: true });

export function docFromDetail(d: DocumentDetail): DocState {
  return {
    id: d.id,
    title: d.title,
    dirty: false,
    pages: d.pages.map((p) => ({
      ...p,
      corners: p.corners ?? [
        { x: 0, y: 0 },
        { x: p.width, y: 0 },
        { x: p.width, y: p.height },
        { x: 0, y: p.height },
      ],
      processedUrl: api.fileUrl(d.id, p.id, 'processed'),
      thumbUrl: api.fileUrl(d.id, p.id, 'thumb'),
      dirty: [],
    })),
  };
}

export function pageMeta(p: PageState): PageMeta {
  return {
    id: p.id,
    width: p.width,
    height: p.height,
    corners: p.corners,
    rotation: p.rotation,
    filter: p.filter,
    processedType: p.processedType,
    ocr: p.ocr,
  };
}

// --- Photo source -----------------------------------------------------------

export interface Source {
  blob: Blob;
  canvas: HTMLCanvasElement;
}

/** Réduit la photo à 3200 px et la réencode (l'orientation EXIF est alors appliquée pour de bon). */
export async function prepareSource(file: Blob): Promise<Source> {
  const canvas = await blobToCanvas(file, MAX_SOURCE_SIDE);
  const blob = await canvasToBlob(canvas, 'image/jpeg', 0.9);
  return { blob, canvas };
}

export async function detect(canvas: HTMLCanvasElement): Promise<Detection> {
  const cv = await loadOpenCV();
  return detectDocument(cv, canvas);
}

/** Petit cache des photos sources décodées (une page modifiée plusieurs fois d'affilée). */
const sourceCache = new Map<string, HTMLCanvasElement>();

export function rememberSource(pageId: string, canvas: HTMLCanvasElement) {
  sourceCache.set(pageId, canvas);
  while (sourceCache.size > 2) {
    const [k, c] = sourceCache.entries().next().value!;
    sourceCache.delete(k);
    if (c !== canvas) releaseCanvas(c);
  }
}

export async function sourceCanvas(docId: string | null, page: PageState): Promise<{ canvas: HTMLCanvasElement; blob: Blob }> {
  let blob = page.original;
  if (!blob) {
    if (!docId) throw new Error('Photo source introuvable');
    blob = await api.getFile(docId, page.id, 'original');
  }
  let canvas = sourceCache.get(page.id);
  if (!canvas) {
    canvas = await blobToCanvas(blob);
    rememberSource(page.id, canvas);
  }
  return { canvas, blob };
}

// --- Rendu ------------------------------------------------------------------

/**
 * (Re)calcule l'image traitée et la vignette d'une page. Renvoie une nouvelle page ;
 * l'OCR est invalidé si le rendu a changé.
 */
export async function renderInto(
  base: Omit<PageState, 'processedUrl' | 'thumbUrl' | 'width' | 'height' | 'processedType' | 'dirty'> & Partial<PageState>,
  source: HTMLCanvasElement,
): Promise<PageState> {
  const cv = await loadOpenCV();
  const out = renderPage(cv, source, { corners: base.corners, rotation: base.rotation, filter: base.filter });
  try {
    const type = processedTypeFor(base.filter);
    const processed = await canvasToBlob(out, type, 0.85);
    const thumb = await thumbnail(out);
    if (base.processedUrl?.startsWith('blob:')) URL.revokeObjectURL(base.processedUrl);
    if (base.thumbUrl?.startsWith('blob:')) URL.revokeObjectURL(base.thumbUrl);
    const dirty = new Set<FileKind>([...(base.dirty ?? []), 'processed', 'thumb']);
    return {
      ...base,
      width: out.width,
      height: out.height,
      processedType: type,
      processed,
      thumb,
      processedUrl: URL.createObjectURL(processed),
      thumbUrl: URL.createObjectURL(thumb),
      ocr: null,
      dirty: [...dirty],
    } as PageState;
  } finally {
    releaseCanvas(out);
  }
}

/** Nouvelle page à partir d'une photo et de ses coins. */
export async function createPage(src: Source, corners: Quad, filter: FilterName = 'enhanced'): Promise<PageState> {
  const id = newId();
  rememberSource(id, src.canvas);
  return renderInto({ id, corners, rotation: 0, filter, ocr: null, original: src.blob, dirty: ['original'] }, src.canvas);
}

export function revokePage(p: PageState) {
  if (p.processedUrl.startsWith('blob:')) URL.revokeObjectURL(p.processedUrl);
  if (p.thumbUrl.startsWith('blob:')) URL.revokeObjectURL(p.thumbUrl);
}
