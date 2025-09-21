// Simple service worker that doesn't interfere with API calls
self.addEventListener('install', (event) => {
  console.log('Service Worker: Installed');
  self.skipWaiting();
});

self.addEventListener('activate', (event) => {
  console.log('Service Worker: Activated');
  event.waitUntil(self.clients.claim());
});

// Don't intercept any fetch requests - let them go through normally
self.addEventListener('fetch', (event) => {
  // Just let all requests pass through without caching
  return;
});
