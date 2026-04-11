/* eslint-disable no-restricted-globals */
/* DO_NOT_UNDO — Enhanced service worker for offline access */

const CACHE_NAME = "appeal-case-manager-v3";
const STATIC_ASSETS = [
  "/",
  "/index.html",
  "/manifest.json",
];

// API response cache for offline access
const API_CACHE = "appeal-api-cache-v1";
const CACHEABLE_API_PATHS = [
  "/api/cases",
  "/api/auth/me",
  "/api/pipeline/dashboard-summary",
];

// Install — cache static assets
self.addEventListener("install", (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME).then((cache) => cache.addAll(STATIC_ASSETS))
  );
  self.skipWaiting();
});

// Activate — clean old caches
self.addEventListener("activate", (event) => {
  const validCaches = [CACHE_NAME, API_CACHE];
  event.waitUntil(
    caches.keys().then((keys) =>
      Promise.all(
        keys.filter((key) => !validCaches.includes(key)).map((key) => caches.delete(key))
      )
    )
  );
  self.clients.claim();
});

// Check if a URL is a cacheable API path
const isCacheableAPI = (url) => {
  return CACHEABLE_API_PATHS.some((path) => url.pathname.includes(path));
};

// Fetch handler
self.addEventListener("fetch", (event) => {
  const { request } = event;
  const url = new URL(request.url);

  // Skip non-GET, WebSocket, and extension requests
  if (request.method !== "GET" || url.protocol === "ws:" || url.protocol === "wss:" || url.protocol === "chrome-extension:") {
    return;
  }

  // API requests — network-first with cache fallback
  if (url.pathname.startsWith("/api")) {
    if (isCacheableAPI(url)) {
      event.respondWith(
        fetch(request)
          .then((response) => {
            // Cache successful API responses
            if (response.ok) {
              const cloned = response.clone();
              caches.open(API_CACHE).then((cache) => cache.put(request, cloned));
            }
            return response;
          })
          .catch(() => {
            // Offline fallback — serve from cache
            return caches.match(request).then((cached) => {
              if (cached) return cached;
              return new Response(JSON.stringify({ error: "Offline", offline: true }), {
                status: 503,
                headers: { "Content-Type": "application/json" },
              });
            });
          })
      );
    }
    return;
  }

  // Navigation requests — network-first with index.html fallback
  if (request.mode === "navigate") {
    event.respondWith(
      fetch(request).catch(() => caches.match("/index.html"))
    );
    return;
  }

  // Static assets — network-first for JS/CSS (ensures code updates reach users immediately)
  // Cache-first only for images and fonts
  if (url.pathname.match(/\.(js|css)$/) || url.pathname.startsWith("/static/js/") || url.pathname.startsWith("/static/css/")) {
    event.respondWith(
      fetch(request).then((response) => {
        if (response.ok) {
          const cloned = response.clone();
          caches.open(CACHE_NAME).then((cache) => cache.put(request, cloned));
        }
        return response;
      }).catch(() => {
        return caches.match(request).then((cached) => cached || new Response("", { status: 503 }));
      })
    );
    return;
  }

  // Images, fonts, other static assets — cache-first
  event.respondWith(
    caches.match(request).then((cached) => {
      if (cached) return cached;
      return fetch(request).then((response) => {
        if (response.ok && url.pathname.match(/\.(png|jpg|jpeg|svg|woff2?|ttf|webp|ico)$/)) {
          const cloned = response.clone();
          caches.open(CACHE_NAME).then((cache) => cache.put(request, cloned));
        }
        return response;
      });
    })
  );
});

// Background sync for pending data
self.addEventListener("sync", (event) => {
  if (event.tag === "sync-pending-notes") {
    event.waitUntil(syncPendingNotes());
  }
});

async function syncPendingNotes() {
  // This is handled by the frontend when coming back online
  const clients = await self.clients.matchAll();
  clients.forEach((client) => {
    client.postMessage({ type: "SYNC_PENDING_NOTES" });
  });
}

// Push notification handler
self.addEventListener("push", (event) => {
  const data = event.data?.json() || {};
  const title = data.title || "Appeal Case Manager";
  const options = {
    body: data.body || "You have a new notification",
    icon: "/icons/icon-192x192.png",
    badge: "/icons/icon-72x72.png",
    data: data.url || "/dashboard",
    vibrate: [200, 100, 200],
  };
  event.waitUntil(self.registration.showNotification(title, options));
});

// Notification click handler
self.addEventListener("notificationclick", (event) => {
  event.notification.close();
  const url = event.notification.data || "/dashboard";
  event.waitUntil(
    self.clients.matchAll({ type: "window" }).then((clients) => {
      const existing = clients.find((c) => c.url.includes(url));
      if (existing) return existing.focus();
      return self.clients.openWindow(url);
    })
  );
});
