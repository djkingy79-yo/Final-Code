import { useEffect, useRef } from "react";
import { useLocation } from "react-router-dom";
import axios from "axios";
import { API } from "../App";

/**
 * Lightweight page-view tracker. Mounted once at the app root.
 * On every route change, POSTs {path} to /api/track/visit so we can
 * compute visits-to-signup conversion rates per page. Fire-and-forget —
 * silently swallows errors so tracking failures never disrupt the user.
 * Debounced to once per path per session to avoid double-counting on
 * React re-renders or StrictMode double-mounts.
 */
const PageViewTracker = () => {
  const location = useLocation();
  const tracked = useRef(new Set());

  useEffect(() => {
    const key = location.pathname;
    if (!key || tracked.current.has(key)) return;
    tracked.current.add(key);

    // fire-and-forget
    axios
      .post(`${API}/track/visit`, { path: key }, { timeout: 5000 })
      .catch(() => { /* swallow */ });
  }, [location.pathname]);

  return null;
};

export default PageViewTracker;
