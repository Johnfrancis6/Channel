// Chargement à la demande d'OpenCV.js (~10 Mo, mis en cache par le service worker).

// L'API d'OpenCV.js n'a pas de types fiables : on la manipule en `any`, confinée à src/scan/.
// eslint-disable-next-line @typescript-eslint/no-explicit-any
export type CV = any;

let loading: Promise<CV> | null = null;

export function loadOpenCV(src = `${__VENDOR__.opencv}/opencv.js`): Promise<CV> {
  if (loading) return loading;
  loading = new Promise<CV>((resolve, reject) => {
    const w = window as unknown as { cv?: CV };
    const ready = async () => {
      let cv = w.cv;
      // Selon la compilation, `cv` est une vraie promesse, ou le module Emscripten qui a
      // lui-même une méthode `then` se résolvant… sur lui-même : l'attendre avec `await`
      // bouclerait à l'infini. On ne fait donc `await` que sur une vraie Promise.
      if (cv instanceof Promise) cv = await cv;
      // Le runtime WebAssembly s'initialise de façon asynchrone ; `onRuntimeInitialized`
      // n'est pas toujours rappelé selon la compilation, donc on attend que `cv.Mat` existe.
      const started = Date.now();
      const poll = () => {
        if (cv?.Mat) {
          // Sans cela, `resolve(cv)` rappellerait cv.then(), qui se résout sur cv… sans fin.
          delete cv.then;
          return resolve(cv);
        }
        if (Date.now() - started > 60_000) return reject(new Error('OpenCV.js ne s’initialise pas'));
        setTimeout(poll, 30);
      };
      poll();
    };
    if (w.cv) {
      ready().catch(reject);
      return;
    }
    const s = document.createElement('script');
    s.src = src;
    s.async = true;
    s.onload = () => ready().catch(reject);
    s.onerror = () => {
      loading = null;
      reject(new Error('Impossible de charger OpenCV.js (réseau ?)'));
    };
    document.head.appendChild(s);
  });
  return loading;
}

/** Libère des Mat OpenCV (mémoire WebAssembly, jamais collectée automatiquement). */
export function free(...mats: { delete(): void; isDeleted?: () => boolean }[]) {
  for (const m of mats) {
    try {
      if (m && !(m.isDeleted && m.isDeleted())) m.delete();
    } catch {
      /* déjà libéré */
    }
  }
}
