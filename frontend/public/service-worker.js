/* eslint-disable no-restricted-globals */
/* DO_NOT_UNDO — Enhanced service worker for offline access.
   CACHE_NAME bumped on 2026-04-21 after a CORS regression left stale error
   responses cached on users' phones; bumping the name forces every installed
   PWA to wipe its caches on next open. */

const CACHE_NAME = "appeal-case-manager-v4";
const STATIC_ASSETS = [
  "/",
  "/index.html",
  "/manifest.json",
];

// API response cache for offline access
const API_CACHE = "appeal-api-cache-v2";
const CACHEABLE_API_PATHS = [
  "/api/cases",
  "/api/auth/me",
  "/api/pipeline/dashboard-summary",
];

// Paths the service worker MUST NEVER intercept or cache — auth, callbacks,
// health checks. If a stale cache ever returns a wrong response for these,
// users get stuck on "Sign In Failed" with no way to recover.
const NEVER_INTERCEPT = [
  "/api/auth/",            // all auth (login, google callback, me, logout, etc.)
  "/api/health",
  "/auth/callback",        // the OAuth redirect landing page must ALWAYS be fresh
];

// Install — cache static assets
self.addEventListener("install", (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME).then((cache) => cache.addAll(STATIC_ASSETS))
  );
  self.skipWaiting();
});

// Accept a SKIP_WAITING message from the page so a newly-installed SW can take
// control immediately after `yarn build` ships, without the user having to
// close and reopen the PWA.
self.addEventListener("message", (event) => {
  if (event.data?.type === "SKIP_WAITING") {
    self.skipWaiting();
  }
});

// Activate — clean old caches + take control of all open tabs immediately so
// the fresh SW is in charge before the next fetch.
self.addEventListener("activate", (event) => {
  const validCaches = [CACHE_NAME, API_CACHE];
  event.waitUntil(
    (async () => {
      const keys = await caches.keys();
      await Promise.all(
        keys.filter((key) => !validCaches.includes(key)).map((key) => caches.delete(key))
      );
      await self.clients.claim();
      // Tell every open tab to reload so they pick up the new bundle + fresh state.
      const clients = await self.clients.matchAll({ type: "window" });
      clients.forEach((client) => client.postMessage({ type: "SW_UPDATED", cache: CACHE_NAME }));
    })()
  );
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

  // Never intercept auth / callback / health — always go straight to network.
  // Prevents any stale cached response from ever producing a "Sign In Failed".
  if (NEVER_INTERCEPT.some((p) => url.pathname.startsWith(p) || url.pathname.includes(p))) {
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
