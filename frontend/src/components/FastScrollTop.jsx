/* ========================================================================
   DO NOT UNDO — ENTIRE FILE PROTECTED
   All features, functions, styles, and content in this file are approved
   and must be preserved. Do not remove, rename, or refactor any code.
   ======================================================================== */
import { useEffect, useState } from "react";
import { useLocation, useNavigate } from "react-router-dom";
import { ArrowUp, Home } from "lucide-react";

/* Scroll to top on every route change */
export const ScrollToTopOnNav = () => {
  const { pathname } = useLocation();

  useEffect(() => {
    window.scrollTo(0, 0);
  }, [pathname]);

  return null;
};

export const FastScrollTop = () => {
  const [visible, setVisible] = useState(false);
  const navigate = useNavigate();

  useEffect(() => {
    const onScroll = () => {
      setVisible(window.scrollY > 240);
    };

    window.addEventListener("scroll", onScroll, { passive: true });
    onScroll();

    return () => window.removeEventListener("scroll", onScroll);
  }, []);

  if (!visible) return null;

  return (
    <div className="fixed bottom-20 right-4 z-[70] flex flex-col gap-2">
      <button
        onClick={() => navigate("/")}
        className="h-10 w-10 rounded-full bg-blue-600 hover:bg-blue-700 text-white shadow-lg border-2 border-white/60 flex items-center justify-center transition-colors"
        data-testid="global-home-btn"
        aria-label="Home"
      >
        <Home className="w-4 h-4" />
      </button>
      <button
        onClick={() => window.scrollTo({ top: 0, behavior: "smooth" })}
        className="h-10 w-10 rounded-full bg-blue-600 hover:bg-blue-700 text-white shadow-lg border-2 border-white/60 flex items-center justify-center transition-colors"
        data-testid="global-fast-scroll-top-btn"
        aria-label="Back to top"
      >
        <ArrowUp className="w-4 h-4" />
      </button>
    </div>
  );
};
