/* DO NOT UNDO — FastScrollTop component. All features in this file are approved and must be preserved. */
import { useEffect, useState } from "react";
import { ArrowUp } from "lucide-react";

export const FastScrollTop = () => {
  const [visible, setVisible] = useState(false);

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
    <button
      onClick={() => window.scrollTo({ top: 0, behavior: "smooth" })}
      className="fixed bottom-5 right-5 z-[70] h-12 w-12 rounded-full bg-blue-600 hover:bg-blue-700 text-white shadow-xl border-2 border-white/60 flex items-center justify-center"
      data-testid="global-fast-scroll-top-btn"
      aria-label="Back to top"
    >
      <ArrowUp className="w-5 h-5" />
    </button>
  );
};
