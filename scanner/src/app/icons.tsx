// Icônes inline (traits, 24×24), pour ne dépendre d'aucune police d'icônes.
import type { JSX } from 'preact';

const I = (d: string) => (props: JSX.SVGAttributes<SVGSVGElement>) => (
  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true" {...props}>
    <path d={d} />
  </svg>
);

export const IconCamera = I('M4 8h3l2-3h6l2 3h3a1 1 0 0 1 1 1v10a1 1 0 0 1-1 1H4a1 1 0 0 1-1-1V9a1 1 0 0 1 1-1zM12 17a4 4 0 1 0 0-8 4 4 0 0 0 0 8z');
export const IconImport = I('M12 3v12M7 10l5 5 5-5M4 17v3h16v-3');
export const IconBack = I('M15 5l-7 7 7 7');
export const IconMore = I('M5 12h.01M12 12h.01M19 12h.01');
export const IconCrop = I('M6 2v14a2 2 0 0 0 2 2h14M2 6h14a2 2 0 0 1 2 2v14');
export const IconRotate = I('M20 11a8 8 0 1 0-2.3 5.7M20 4v7h-7');
export const IconFilter = I('M12 3a9 9 0 1 0 0 18V3zM12 3a9 9 0 0 1 0 18');
export const IconText = I('M4 6V4h16v2M12 4v16M9 20h6');
export const IconImage = I('M4 4h16v16H4zM4 16l5-5 4 4 3-3 4 4M15 9h.01');
export const IconShare = I('M12 3v12M8 7l4-4 4 4M5 12v8h14v-8');
export const IconTrash = I('M4 7h16M10 11v6M14 11v6M6 7l1 13h10l1-13M9 7V4h6v3');
export const IconPlus = I('M12 5v14M5 12h14');
export const IconCheck = I('M5 12l5 5L20 7');
export const IconExpand = I('M4 9V4h5M20 9V4h-5M4 15v5h5M20 15v5h-5');
export const IconWand = I('M15 4V2M15 10V8M11 6h-2M21 6h-2M18 3l-1 1M13 3l1 1M18 9l-1-1M3 21l11-11');
export const IconCopy = I('M8 8h12v12H8zM4 16V4h12');
export const IconSave = I('M5 3h11l3 3v15H5zM8 3v5h8V3M8 21v-7h8v7');
export const IconLeft = I('M14 6l-6 6 6 6');
export const IconRight = I('M10 6l6 6-6 6');
export const IconSearch = I('M11 18a7 7 0 1 0 0-14 7 7 0 0 0 0 14zM21 21l-5-5');
