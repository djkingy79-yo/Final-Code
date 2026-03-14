/* DO NOT UNDO — FastScrollTop component. All features in this file are approved and must be preserved. */
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
      setVisible(window.scrollY > 420);
    };

    window.addEventListener("scroll", onScroll, { passive: true });
    onScroll();

    return () => window.removeEventListener("scroll", onScroll);
  }, []);

  if (!visible) return null;

  return (
    <div className="fixed bottom-5 right-5 z-[70] flex flex-col gap-2">
      <button
        onClick={() => navigate("/")}
        className="h-12 w-12 rounded-full bg-slate-800 hover:bg-slate-900 text-white shadow-xl border-2 border-white/60 flex items-center justify-center transition-colors"
        data-testid="global-quick-home-btn"
        aria-label="Go to home"
      >
        <Home className="w-5 h-5" />
      </button>
      <button
        onClick={() => window.scrollTo({ top: 0, behavior: "smooth" })}
        className="h-12 w-12 rounded-full bg-blue-600 hover:bg-blue-700 text-white shadow-xl border-2 border-white/60 flex items-center justify-center transition-colors"
        data-testid="global-fast-scroll-top-btn"
        aria-label="Back to top"
      >
        <ArrowUp className="w-5 h-5" />
      </button>
    </div>
  );
};
