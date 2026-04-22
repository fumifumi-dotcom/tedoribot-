// sw.js (Network-First Service Worker for PWA Installability)

const CACHE_NAME = 'tedori-keisan-v2026-v5'; // Update version to force cache flush
const URLS_TO_CACHE = [
  '/',
  '/index.html',
  '/css/style.css',
  '/js/calculator.js',
  '/js/affiliate.js'
];

self.addEventListener('install', (event) => {
  self.skipWaiting(); // Force activate new worker immediately
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then((cache) => {
        return cache.addAll(URLS_TO_CACHE);
      })
  );
});

self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches.keys().then((cacheNames) => {
      return Promise.all(
        cacheNames.map((cacheName) => {
          if (cacheName !== CACHE_NAME) {
            return caches.delete(cacheName); // Old cache cleanup
          }
        })
      );
    }).then(() => self.clients.claim()) // Take page control immediately
  );
});

self.addEventListener('fetch', (event) => {
  // Ignore non-GET requests and cross-origin requests for cache
  if (event.request.method !== 'GET') {
    return;
  }
  
  event.respondWith(
    // Network-first strategy
    fetch(event.request)
      .then((response) => {
        // If network request succeeds, update the cache
        if (response && response.status === 200) {
            const responseClone = response.clone();
            caches.open(CACHE_NAME).then((cache) => {
              cache.put(event.request, responseClone);
            });
        }
        return response;
      })
      .catch((err) => {
        // Only if network fails, fallback to cache
        return caches.match(event.request);
      })
  );
});
