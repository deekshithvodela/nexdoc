// NexDoc Service Worker (PWA)
const CACHE_NAME = 'nexdoc-v1.0.3';
const STATIC_ASSETS = [
  './',
  './index.html',
  './license.html',
  './privacy.html',
  './disclosure.html',
  './app.css',
  './app.js',
  './favicon.svg',
  './favicon.png',
  './manifest.json',
  './icons/icon-192.png',
  './icons/icon-512.png',
  './icons/apple-touch-icon.png',
  './components/SearchFilters.js',
  './components/AnalyticsPanel.js',
  './components/SankeyChart.js',
  './components/ComparisonMatrix.js',
  './components/CutoffExplorer.js',
  './data/manifest.json',
  './data/colleges_details.json',
  './data/ug_colleges_aiq_mapping.json',
  './data/aiq_cutoffs_master.json',
  './data/aiq_cutoffs_summary.json',
  './data/ug/summary.json',
  './data/ug/all.json',
  './data/pg/summary.json',
  './data/pg/all.json',
  './data/ss/summary.json',
  './data/ss/all.json',
  'https://cdn.jsdelivr.net/npm/chart.js',
  'https://cdn.jsdelivr.net/npm/d3@7',
  'https://unpkg.com/lucide@latest'
];

// Install Event
self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME).then((cache) => {
      console.log('[SW] Pre-caching core application shell');
      return cache.addAll(STATIC_ASSETS);
    }).then(() => self.skipWaiting())
  );
});

// Activate Event
self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches.keys().then((cacheNames) => {
      return Promise.all(
        cacheNames.map((cache) => {
          if (cache !== CACHE_NAME) {
            console.log('[SW] Clearing old cache:', cache);
            return caches.delete(cache);
          }
        })
      );
    }).then(() => self.clients.claim())
  );
});

// Fetch Event (Stale-While-Revalidate for app assets, Network-First for data)
self.addEventListener('fetch', (event) => {
  const url = new URL(event.request.url);

  // Ignore cross-origin non-GET requests or browser extension requests
  if (event.request.method !== 'GET') return;

  // Exclude analytics tracking
  if (url.hostname.includes('goatcounter.com') || url.pathname.includes('count.js')) {
    return;
  }

  // Handle data requests (e.g., JSON files under data/) with Stale-While-Revalidate
  if (url.pathname.includes('/data/')) {
    event.respondWith(
      caches.open(CACHE_NAME).then(async (cache) => {
        const cachedResponse = await cache.match(event.request);
        const fetchPromise = fetch(event.request)
          .then((networkResponse) => {
            if (networkResponse.status === 200) {
              cache.put(event.request, networkResponse.clone());
            }
            return networkResponse;
          })
          .catch(() => cachedResponse);

        return cachedResponse || fetchPromise;
      })
    );
    return;
  }

  // Handle core static assets with Cache First, falling back to Network
  event.respondWith(
    caches.match(event.request).then((cachedResponse) => {
      if (cachedResponse) {
        // Fetch background update
        fetch(event.request).then((networkResponse) => {
          if (networkResponse.status === 200) {
            caches.open(CACHE_NAME).then((cache) => {
              cache.put(event.request, networkResponse);
            });
          }
        }).catch(() => {});
        return cachedResponse;
      }

      // Root/Directory redirect paths normalization
      if (url.origin === self.location.origin) {
        const scopeUrl = new URL(self.registration.scope);
        const scopePath = scopeUrl.pathname;
        const scopePathNoSlash = scopePath.endsWith('/') ? scopePath.slice(0, -1) : scopePath;
        const cleanPath = url.pathname.endsWith('/index.html') ? url.pathname.slice(0, -10) : url.pathname;

        if (cleanPath === scopePath || cleanPath === scopePathNoSlash) {
          return caches.match('./').then((rootResponse) => {
            if (rootResponse) return rootResponse;
            return fetch(event.request);
          });
        }
      }

      // Caching dynamic external assets (CDNs, Google Fonts, etc.) on the fly
      if (url.origin !== self.location.origin && (url.pathname.endsWith('.js') || url.pathname.includes('/css') || url.hostname.includes('gstatic.com') || url.hostname.includes('googleapis.com'))) {
        return fetch(event.request).then((networkResponse) => {
          if (networkResponse.status === 200) {
            caches.open(CACHE_NAME).then((cache) => {
              cache.put(event.request, networkResponse.clone());
            });
          }
          return networkResponse;
        }).catch(() => {
          return caches.match(event.request);
        });
      }

      return fetch(event.request);
    })
  );
});
