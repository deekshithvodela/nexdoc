// NexDoc Optimized High-Performance Service Worker (PWA)
const CACHE_NAME = 'nexdoc-v1.2.0';
const DATA_CACHE_NAME = 'nexdoc-data-v1.2.0';

const STATIC_SHELL_ASSETS = [
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
  './components/CutoffExplorer.js'
];

const EXTERNAL_CDN_ASSETS = [
  'https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700;800&family=Inter:wght@300;400;500;600;700&display=swap',
  'https://cdn.jsdelivr.net/npm/chart.js',
  'https://cdn.jsdelivr.net/npm/d3@7',
  'https://unpkg.com/lucide@latest'
];

// Install Event - Pre-cache core shell
self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME).then(async (cache) => {
      console.log('[SW] Pre-caching core application shell & static assets');
      await cache.addAll(STATIC_SHELL_ASSETS);
      // Attempt caching external assets asynchronously
      EXTERNAL_CDN_ASSETS.forEach(url => {
        fetch(url).then(response => {
          if (response.ok) cache.put(url, response);
        }).catch(() => {});
      });
    }).then(() => self.skipWaiting())
  );
});

// Activate Event - Clean up legacy caches
self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches.keys().then((cacheNames) => {
      return Promise.all(
        cacheNames.map((cache) => {
          if (cache !== CACHE_NAME && cache !== DATA_CACHE_NAME) {
            console.log('[SW] Deleting legacy cache store:', cache);
            return caches.delete(cache);
          }
        })
      );
    }).then(() => self.clients.claim())
  );
});

// Fetch Strategy:
// 1. Data JSON (/data/): Stale-While-Revalidate with fast local cache fallback
// 2. Static Application Shell & CDNs: Cache-First with background revalidation
self.addEventListener('fetch', (event) => {
  const url = new URL(event.request.url);

  if (event.request.method !== 'GET') return;

  // Ignore analytics trackers from caching
  if (url.hostname.includes('goatcounter.com') || url.pathname.includes('count.js')) {
    return;
  }

  // 1. Data Files Optimization (JSON data)
  if (url.pathname.includes('/data/')) {
    event.respondWith(
      caches.open(DATA_CACHE_NAME).then(async (cache) => {
        const cachedResponse = await cache.match(event.request);
        const networkFetch = fetch(event.request).then((networkResponse) => {
          if (networkResponse.status === 200) {
            cache.put(event.request, networkResponse.clone());
          }
          return networkResponse;
        }).catch(() => cachedResponse);

        return cachedResponse || networkFetch;
      })
    );
    return;
  }

  // 2. Static Shell & External CDN Assets (Cache-First, Network Fallback)
  event.respondWith(
    caches.match(event.request).then((cachedResponse) => {
      if (cachedResponse) {
        // Asynchronous background update
        fetch(event.request).then((networkResponse) => {
          if (networkResponse.status === 200) {
            caches.open(CACHE_NAME).then((cache) => {
              cache.put(event.request, networkResponse);
            });
          }
        }).catch(() => {});
        return cachedResponse;
      }

      // Root path navigation normalization
      if (url.origin === self.location.origin) {
        const scopeUrl = new URL(self.registration.scope);
        const cleanPath = url.pathname.endsWith('/index.html') ? url.pathname.slice(0, -10) : url.pathname;
        if (cleanPath === scopeUrl.pathname || cleanPath === scopeUrl.pathname.replace(/\/$/, '')) {
          return caches.match('./').then(res => res || fetch(event.request));
        }
      }

      // Network fetch with dynamic caching for CDN & font requests
      return fetch(event.request).then((networkResponse) => {
        if (networkResponse.status === 200 && (
          url.origin !== self.location.origin ||
          url.pathname.endsWith('.css') ||
          url.pathname.endsWith('.js') ||
          url.pathname.endsWith('.svg') ||
          url.pathname.endsWith('.png')
        )) {
          caches.open(CACHE_NAME).then((cache) => {
            cache.put(event.request, networkResponse.clone());
          });
        }
        return networkResponse;
      }).catch(() => {
        if (event.request.mode === 'navigate') {
          return caches.match('./index.html');
        }
      });
    })
  );
});
