/* ========================================================================
   DO NOT UNDO — ENTIRE FILE PROTECTED
   All features, functions, styles, and content in this file are approved
   and must be preserved. Do not remove, rename, or refactor any code.
   ======================================================================== */
import { useEffect, useState } from "react";
import { useLocation, useNavigate } from "react-router-dom";
import { ArrowUp, Home, ArrowLeft, MessageCircle } from "lucide-react";

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
    <div className="fixed bottom-20 right-2 sm:right-4 z-[70] flex flex-col gap-1.5 sm:gap-2">
      <button
        onClick={() => navigate(-1)}
        className="h-8 w-8 sm:h-10 sm:w-10 rounded-full bg-blue-600/80 sm:bg-blue-600 hover:bg-blue-700 text-white shadow-lg border-2 border-white/60 flex items-center justify-center transition-colors backdrop-blur-sm"
        data-testid="global-back-btn"
        aria-label="Go back"
      >
        <ArrowLeft className="w-3.5 h-3.5 sm:w-4 sm:h-4" />
      </button>
      <button
        onClick={() => navigate("/")}
        className="h-8 w-8 sm:h-10 sm:w-10 rounded-full bg-blue-600/80 sm:bg-blue-600 hover:bg-blue-700 text-white shadow-lg border-2 border-white/60 flex items-center justify-center transition-colors backdrop-blur-sm"
        data-testid="global-home-btn"
        aria-label="Home"
      >
        <Home className="w-3.5 h-3.5 sm:w-4 sm:h-4" />
      </button>
      <button
        onClick={() => window.scrollTo({ top: 0, behavior: "smooth" })}
        className="h-8 w-8 sm:h-10 sm:w-10 rounded-full bg-blue-600/80 sm:bg-blue-600 hover:bg-blue-700 text-white shadow-lg border-2 border-white/60 flex items-center justify-center transition-colors backdrop-blur-sm"
        data-testid="global-fast-scroll-top-btn"
        aria-label="Back to top"
      >
        <ArrowUp className="w-3.5 h-3.5 sm:w-4 sm:h-4" />
      </button>
      <button
        onClick={() => navigate("/about")}
        className="h-8 w-8 sm:h-10 sm:w-10 rounded-full bg-blue-600/80 sm:bg-blue-600 hover:bg-blue-700 text-white shadow-lg border-2 border-white/60 flex items-center justify-center transition-colors backdrop-blur-sm"
        data-testid="global-chat-btn"
        aria-label="Contact"
      >
        <MessageCircle className="w-3.5 h-3.5 sm:w-4 sm:h-4" />
      </button>
    </div>
  );
};
