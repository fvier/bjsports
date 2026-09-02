// Service Worker para App da Catraca BJ Sports
const CACHE_NAME = "bjsports-catraca-v1";
self.addEventListener("install", (e) => {
    self.skipWaiting();
});
self.addEventListener("activate", (e) => {
    e.waitUntil(clients.claim());
});
self.addEventListener("fetch", (e) => {
    // Pass-through para chamadas ao vivo
    e.respondWith(fetch(e.request).catch(() => caches.match(e.request)));
});
