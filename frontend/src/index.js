/*  — Main entry point. All features in this file are approved and must be preserved. */
import React from "react";
import ReactDOM from "react-dom/client";
import "@fontsource/crimson-pro/400.css";
import "@fontsource/crimson-pro/600.css";
import "@fontsource/crimson-pro/700.css";
import "@fontsource/manrope/400.css";
import "@fontsource/manrope/500.css";
import "@fontsource/manrope/600.css";
import "@/index.css";
import App from "@/App";

const root = ReactDOM.createRoot(document.getElementById("root"));
root.render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
);

// Register service worker for PWA.
// Also: if the user lands on /auth/callback, proactively bypass any cache and
// force-reload the page after a stale SW activates with a newer CACHE_NAME.
// This guarantees that the CORS regression that left stale error responses on
// users' phones can never persist past one page load.
if ("serviceWorker" in navigator && process.env.NODE_ENV === "production") {
  window.addEventListener("load", () => {
    navigator.serviceWorker.register("/service-worker.js").catch(() => {});

    // Relay: if a new SW has taken control, reload once so the fresh bundle runs.
    let reloaded = false;
    navigator.serviceWorker.addEventListener("message", (event) => {
      if (event.data?.type === "SW_UPDATED" && !reloaded) {
        reloaded = true;
        // Only auto-reload on the callback page — reloading silently mid-session
        // would be annoying everywhere else.
        if (window.location.pathname === "/auth/callback") {
          window.location.reload();
        }
      }
    });

    // When a brand-new SW has installed and is waiting, tell it to activate now
    // instead of making the user close the tab first.
    navigator.serviceWorker.ready.then((reg) => {
      if (reg.waiting) reg.waiting.postMessage({ type: "SKIP_WAITING" });
      reg.addEventListener("updatefound", () => {
        const nw = reg.installing;
        if (nw) {
          nw.addEventListener("statechange", () => {
            if (nw.state === "installed" && reg.waiting) {
              reg.waiting.postMessage({ type: "SKIP_WAITING" });
            }
          });
        }
      });
    });
  });

  // Expose a one-liner so the user can recover from ANY stale cache by typing
  // `window.__resetAppCache()` in Safari devtools, or we can call it from code.
  window.__resetAppCache = async () => {
    try {
      if ("caches" in window) {
        const keys = await caches.keys();
        await Promise.all(keys.map((k) => caches.delete(k)));
      }
      const regs = await navigator.serviceWorker.getRegistrations();
      await Promise.all(regs.map((r) => r.unregister()));
      window.location.reload();
    } catch (_) { window.location.reload(); }
  };
}
