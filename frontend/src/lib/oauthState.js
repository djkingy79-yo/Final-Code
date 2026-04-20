// OAuth CSRF state storage — resilient across www. ↔ bare-domain DNS hops.
// Writes to BOTH localStorage and a domain-scoped cookie so the state survives
// GoDaddy-style redirects between subdomains. Reads from either source.

const KEY = "google_oauth_state";

// Derive the registrable parent domain so the cookie is shared between
// `www.criminallawappealmanagement.com.au` and `criminallawappealmanagement.com.au`.
// For localhost / preview URLs we fall back to the host-only cookie.
const getCookieDomain = () => {
  const host = window.location.hostname;
  if (!host || host === "localhost" || /^[\d.]+$/.test(host)) return null;
  const parts = host.split(".");
  if (parts.length <= 2) return "." + host.replace(/^www\./, "");
  // e.g. www.foo.com.au -> .foo.com.au ; app.foo.com -> .foo.com
  return "." + parts.slice(-3).join(".").replace(/^\.?www\./, "");
};

export const generateState = () =>
  Math.random().toString(36).slice(2) + Date.now().toString(36);

export const saveOAuthState = (state) => {
  try {
    localStorage.setItem(KEY, state);
  } catch (_) { /* private-mode / quota — fall through to cookie */ }

  const domain = getCookieDomain();
  const attrs = [
    `${KEY}=${encodeURIComponent(state)}`,
    "path=/",
    "max-age=600",
    "SameSite=Lax",
  ];
  if (window.location.protocol === "https:") attrs.push("Secure");
  if (domain) attrs.push(`Domain=${domain}`);
  document.cookie = attrs.join("; ");
};

export const readOAuthState = () => {
  try {
    const v = localStorage.getItem(KEY);
    if (v) return v;
  } catch (_) { /* ignore */ }
  const match = document.cookie
    .split("; ")
    .find((c) => c.startsWith(`${KEY}=`));
  return match ? decodeURIComponent(match.split("=")[1]) : null;
};

export const clearOAuthState = () => {
  try { localStorage.removeItem(KEY); } catch (_) { /* ignore */ }
  const domain = getCookieDomain();
  const base = `${KEY}=; path=/; max-age=0; SameSite=Lax`;
  document.cookie = base;
  if (domain) document.cookie = `${base}; Domain=${domain}`;
};
