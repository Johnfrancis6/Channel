/// <reference types="vite/client" />

/** Chemins versionnés des bibliothèques lourdes (voir scripts/vendor.mjs). */
declare const __VENDOR__: {
  opencv: string;
  tesseract: string;
  tesseractCore: string;
  tessdata: string;
};
