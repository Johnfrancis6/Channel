// Service worker de Scanner. Trois règles :
//  · /api/*       : jamais en cache (toujours le réseau) ;
//  · /vendor/*    : cache d'abord (chemins versionnés : OpenCV.js, Tesseract.js) ;
//  · le reste     : réseau d'abord, repli sur le cache (l'app s'ouvre hors ligne).
// Les deux jetons en majuscules ci-dessous sont remplacés au build (plugin « scanner-sw » de vite.config.ts).

const BUILD_ID = '__BUILD_ID__';
const VENDOR_DIRS = __VENDOR_DIRS__;
const SHELL_CACHE = `scanner-shell-${BUILD_ID}`;
const VENDOR_CACHE = 'scanner-vendor';

self.addEventListener('install', (event) => {
  event.waitUntil(
    caches
      .open(SHELL_CACHE)
      .then((cache) => Promise.all(['/', '/manifest.webmanifest'].map((u) => cache.add(u).catch(() => {}))))
      .then(() => self.skipWaiting()),
  );
});

self.addEventListener('activate', (event) => {
  event.waitUntil(
    (async () => {
      for (const name of await caches.keys()) {
        if (name.startsWith('scanner-shell-') && name !== SHELL_CACHE) await caches.delete(name);
      }
      // Oublie les anciennes versions d'OpenCV / Tesseract.
      const vendor = await caches.open(VENDOR_CACHE);
      for (const req of await vendor.keys()) {
        const path = new URL(req.url).pathname;
        if (!VENDOR_DIRS.some((dir) => path.startsWith(`${dir}/`))) await vendor.delete(req);
      }
      await self.clients.claim();
    })(),
  );
});

async function cacheFirst(request, cacheName) {
  const cache = await caches.open(cacheName);
  const hit = await cache.match(request);
  if (hit) return hit;
  const res = await fetch(request);
  if (res.ok && res.type === 'basic') await cache.put(request, res.clone());
  return res;
}

async function networkFirst(request, cacheKey) {
  const cache = await caches.open(SHELL_CACHE);
  try {
    const res = await fetch(request);
    // Une redirection (session Access expirée) n'est jamais mise en cache.
    if (res.ok && res.type === 'basic') await cache.put(cacheKey ?? request, res.clone());
    return res;
  } catch (err) {
    const hit = await cache.match(cacheKey ?? request);
    if (hit) return hit;
    throw err;
  }
}

self.addEventListener('fetch', (event) => {
  const { request } = event;
  if (request.method !== 'GET') return;
  const url = new URL(request.url);
  if (url.origin !== self.location.origin) return;
  if (url.pathname.startsWith('/api/')) return;

  if (url.pathname.startsWith('/vendor/')) {
    event.respondWith(cacheFirst(request, VENDOR_CACHE));
  } else if (request.mode === 'navigate') {
    event.respondWith(networkFirst(request, '/'));
  } else if (url.pathname.startsWith('/assets/')) {
    // Fichiers du build Vite : noms hachés, donc immuables.
    event.respondWith(cacheFirst(request, SHELL_CACHE));
  } else {
    event.respondWith(networkFirst(request));
  }
});
