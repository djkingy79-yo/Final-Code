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

// Atomic one-call helper for "Sign in with Google" CTAs anywhere in the app.
// Generates state, saves it to localStorage + cookie, builds the Google OAuth
// URL, and navigates — all synchronously in the same event handler so there
// is zero opportunity for a React re-render to overwrite the stored state
// before the browser actually navigates away.
//
// The optional `source` argument captures which CTA / page triggered the login
// so we can attribute new sign-ups to the page that converted them. Default
// is the current pathname (e.g. "/success-stories"). Source is stashed in
// localStorage and consumed + cleared by the /auth/callback handler.
export const startGoogleLogin = (source) => {
  const clientId = process.env.REACT_APP_GOOGLE_CLIENT_ID;
  if (!clientId) {
    console.error("REACT_APP_GOOGLE_CLIENT_ID not configured");
    return;
  }
  try {
    const src = source || (typeof window !== "undefined" ? window.location.pathname : "/");
    localStorage.setItem("signup_source", src);
  } catch (_) { /* ignore quota / private-mode */ }
  const redirectUri = `${window.location.origin}/auth/callback`;
  const state = generateState();
  saveOAuthState(state);
  const url = `https://accounts.google.com/o/oauth2/v2/auth?${new URLSearchParams({
    client_id: clientId,
    redirect_uri: redirectUri,
    response_type: "code",
    scope: "openid email profile",
    access_type: "online",
    prompt: "select_account",
    state,
  }).toString()}`;
  window.location.href = url;
};

export const consumeSignupSource = () => {
  try {
    const v = localStorage.getItem("signup_source");
    localStorage.removeItem("signup_source");
    return v || null;
  } catch (_) { return null; }
};
