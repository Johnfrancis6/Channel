// OCR en français avec Tesseract.js, dans un Web Worker. Fichiers auto-hébergés sous /vendor/.
import { createWorker, OEM, PSM, type Worker } from 'tesseract.js';
import type { OcrResult } from '../shared/types';
import { linesFromBlocks, type TBlock } from './text';

type Progress = (p: number, status: string) => void;

let workerPromise: Promise<Worker> | null = null;
let listener: Progress | null = null;

const STATUS: Record<string, string> = {
  'loading tesseract core': 'Chargement du moteur OCR…',
  'initializing tesseract': 'Démarrage de l’OCR…',
  'loading language traineddata': 'Chargement du modèle français…',
  'initializing api': 'Démarrage de l’OCR…',
  'recognizing text': 'Lecture du texte…',
};

function getWorker(): Promise<Worker> {
  workerPromise ??= createWorker('fra', OEM.LSTM_ONLY, {
    workerPath: `${__VENDOR__.tesseract}/worker.min.js`,
    corePath: __VENDOR__.tesseractCore,
    langPath: __VENDOR__.tessdata,
    // Worker du même domaine (pas de blob:) : le cookie Access accompagne ses requêtes.
    workerBlobURL: false,
    // Le service worker met déjà ces fichiers en cache.
    cacheMethod: 'none',
    logger: (m) => listener?.(m.progress ?? 0, STATUS[m.status] ?? m.status),
  })
    .then(async (w) => {
      await w.setParameters({
        tessedit_pageseg_mode: PSM.AUTO,
        preserve_interword_spaces: '1',
        user_defined_dpi: '200',
      });
      return w;
    })
    .catch((err) => {
      workerPromise = null;
      throw err;
    });
  return workerPromise;
}

/** Reconnaît le texte d'une image de page ; les cadres sont en pixels de cette image. */
export async function recognize(image: Blob, width: number, height: number, onProgress?: Progress): Promise<OcrResult> {
  listener = onProgress ?? null;
  try {
    const w = await getWorker();
    const { data } = await w.recognize(image, {}, { blocks: true, text: false });
    return { width, height, lines: linesFromBlocks(data.blocks as unknown as TBlock[]) };
  } finally {
    listener = null;
  }
}

export async function terminateOcr() {
  const w = await workerPromise?.catch(() => null);
  workerPromise = null;
  await w?.terminate();
}
