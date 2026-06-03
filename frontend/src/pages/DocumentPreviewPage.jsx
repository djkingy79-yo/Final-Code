import { useEffect, useMemo, useRef, useState } from "react";
import { useNavigate, useSearchParams } from "react-router-dom";
import { isIOSDevice } from "../utils/isIOS";
import { ArrowLeft, Printer } from "lucide-react";
import { Button } from "../components/ui/button";
import DOMPurify from "dompurify";

export default function DocumentPreviewPage() {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const iframeRef = useRef(null);
  const [loaded, setLoaded] = useState(false);
  const [iframeHeight, setIframeHeight] = useState("90vh");
  const mode = searchParams.get("mode") || "pdf";

  const payload = useMemo(() => {
    try {
      const raw = localStorage.getItem("document-preview-payload");
      const parsed = raw ? JSON.parse(raw) : null;
      if (parsed?.html) {
        parsed.html = parsed.html.replace(/<script\b[^<]*(?:(?!<\/script>)<[^<]*)*<\/script>/gi, "");
      }
      return parsed;
    } catch (error) {
      return null;
    }
  }, []);

  const isIOS = isIOSDevice();
  const returnTo = payload?.returnTo || -1;

  const handleBack = () => {
    if (typeof returnTo === "string" && returnTo.trim()) {
      navigate(returnTo);
      return;
    }
    navigate(-1);
  };

  // Auto-trigger print for non-iOS in print mode (iframe path)
  useEffect(() => {
    if (isIOS) return;
    if (!loaded || mode !== "print" || !iframeRef.current?.contentWindow) return;
    const timer = window.setTimeout(() => iframeRef.current?.contentWindow?.print(), 900);
    return () => window.clearTimeout(timer);
  }, [loaded, mode, isIOS]);

  // iOS-only: when the user presses Print/Save as PDF, rewrite document.title
  // to just the clean filename FIRST so Safari's auto-injected print header
  // shows "Grounds of Merit — Appellant" instead of the full URL. Safari uses
  // document.title as the header text when the "Headers and Footers" option
  // is on; this makes the default output readable without the user touching
  // Share → Print → Options.
  const handleIOSPrint = () => {
    try {
      const cleanTitle = (payload?.title || "Document")
        .replace(/\s*—\s*(Print|PDF|Word)\s*View$/i, "")
        .trim();
      document.title = cleanTitle;
    } catch (_) { /* ignore */ }
    const win = iframeRef.current?.contentWindow;
    if (win) {
      try { win.focus(); win.print(); return; } catch (_) { /* fall through */ }
    }
    window.print();
  };

  if (!payload?.html) {
    return (
      <div className="min-h-screen bg-slate-100 flex items-center justify-center px-4" data-testid="document-preview-missing">
        <div className="max-w-lg bg-white border border-slate-200 rounded-2xl shadow-lg p-8 text-center">
          <h1 className="text-3xl font-bold text-slate-900">Preview unavailable</h1>
          <p className="mt-3 text-slate-700">
            The preview payload was not found. Return to the report page and open Print or PDF preview again.
          </p>
          <Button className="mt-5 bg-blue-700 text-white hover:bg-blue-600" onClick={handleBack} data-testid="document-preview-back-button">
            <ArrowLeft className="w-4 h-4 mr-2" /> Go back
          </Button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-slate-100" data-testid="document-preview-page">
      <div className="max-w-6xl mx-auto px-4 sm:px-6 py-4 no-print">
        <div className="bg-white border border-slate-200 rounded-2xl shadow-sm p-4 sm:p-5 flex items-center justify-between gap-3 flex-wrap" data-testid="document-preview-toolbar">
          <div>
            <p className="text-xs font-bold uppercase tracking-[0.2em] text-blue-700">Document preview</p>
            <h1 className="text-2xl font-bold text-slate-900">{payload.title || "Preview"}</h1>
            <p className="text-sm text-slate-600 mt-1">
              {isIOS
                ? "For a clean PDF without the URL at the top: tap Print → tap the preview → Options → turn OFF Headers and Footers."
                : mode === "print"
                ? "Print dialogue opens automatically from this clean preview page."
                : "Use browser Print / Save as PDF from this clean preview page."}
            </p>
          </div>

          <div className="flex items-center gap-2 flex-wrap">
            <Button className="bg-blue-700 text-white hover:bg-blue-600" onClick={handleBack} data-testid="document-preview-close-button">
              <ArrowLeft className="w-4 h-4 mr-2" /> Back
            </Button>
            {!isIOS && (
              <Button
                className="bg-blue-700 text-white hover:bg-blue-600"
                onClick={() => iframeRef.current?.contentWindow?.print()}
                data-testid="document-preview-print-button"
              >
                <Printer className="w-4 h-4 mr-2" /> Print / Save as PDF
              </Button>
            )}
            {isIOS && (
              <Button
                className="bg-blue-700 text-white hover:bg-blue-600"
                onClick={handleIOSPrint}
                data-testid="document-preview-print-button"
              >
                <Printer className="w-4 h-4 mr-2" /> Print / Save as PDF
              </Button>
            )}
          </div>
        </div>
      </div>

      <div className="max-w-6xl mx-auto px-4 sm:px-6 pb-8" data-testid="document-preview-frame-wrap">
        <div className="bg-white border border-slate-200 rounded-2xl shadow-xl overflow-hidden">
          {/* Use iframe with srcDoc on ALL devices (including iOS) so the full
              HTML document — including @media print rules, @page, CSS grids and
              background colours — renders EXACTLY as it will print. The older
              iOS path rendered via dangerouslySetInnerHTML into a <div>, which
              Safari parses as HTML but fails to apply head-level @page rules
              and collapses grid layouts.  */}
          <iframe
            ref={iframeRef}
            title={payload.title || "Document preview"}
            srcDoc={DOMPurify.sanitize(payload.html, { WHOLE_DOCUMENT: true, ADD_TAGS: ['style'] })}
            className="w-full bg-white border-0"
            style={{ minHeight: "90vh", height: iframeHeight }}
            onLoad={() => {
              setLoaded(true);
              try {
                const doc = iframeRef.current?.contentDocument || iframeRef.current?.contentWindow?.document;
                if (doc) {
                  const h = doc.documentElement.scrollHeight || doc.body.scrollHeight;
                  setIframeHeight(h + 40 + "px");
                }
              } catch (e) { /* cross-origin fallback */ }
            }}
            data-testid="document-preview-iframe"
          />
        </div>
      </div>
    </div>
  );
}
