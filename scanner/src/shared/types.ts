// Types partagés entre l'app (navigateur) et le Worker.

export type Point = { x: number; y: number };
/** Quadrilatère dans l'ordre : haut-gauche, haut-droit, bas-droit, bas-gauche. */
export type Quad = [Point, Point, Point, Point];

export type Rotation = 0 | 90 | 180 | 270;
export type FilterName = 'original' | 'gray' | 'bw' | 'enhanced';
export const FILTERS: FilterName[] = ['original', 'gray', 'bw', 'enhanced'];

export type FileKind = 'original' | 'processed' | 'thumb';
export const FILE_KINDS: FileKind[] = ['original', 'processed', 'thumb'];

export type ImageType = 'image/jpeg' | 'image/png';

export interface OcrLine {
  text: string;
  /** [x0, y0, x1, y1] en pixels de l'image traitée. */
  bbox: [number, number, number, number];
  confidence: number;
}

export interface OcrResult {
  width: number;
  height: number;
  lines: OcrLine[];
}

/** Métadonnées d'une page, telles que stockées dans D1. */
export interface PageMeta {
  id: string;
  width: number;
  height: number;
  corners: Quad | null;
  rotation: Rotation;
  filter: FilterName;
  processedType: ImageType;
  ocr: OcrResult | null;
}

export interface DocumentSummary {
  id: string;
  title: string;
  createdAt: number;
  updatedAt: number;
  pageCount: number;
  coverPageId: string | null;
  /** Extrait HTML échappé, avec <mark>…</mark> autour des termes trouvés (recherche seulement). */
  snippet?: string;
}

export interface DocumentDetail extends DocumentSummary {
  pages: PageMeta[];
}
