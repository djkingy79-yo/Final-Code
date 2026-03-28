import { useEffect, useMemo, useRef, useState } from "react";
import { useNavigate, useSearchParams } from "react-router-dom";
import { ArrowLeft, Printer } from "lucide-react";
import { Button } from "../components/ui/button";

export default function DocumentPreviewPage() {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const iframeRef = useRef(null);
  const [loaded, setLoaded] = useState(false);
  const mode = searchParams.get("mode") || "pdf";

  const payload = useMemo(() => {
    try {
      const raw = localStorage.getItem("document-preview-payload");
      if (!raw) return null;
      return JSON.parse(raw);
    } catch (error) {
      return null;
    }
  }, []);

  const isIOS = /iPad|iPhone|iPod/.test(navigator.userAgent);
  const returnTo = payload?.returnTo || -1;

  const handleBack = () => {
    if (typeof returnTo === "string" && returnTo.trim()) {
      navigate(returnTo);
      return;
    }
    navigate(-1);
  };

  useEffect(() => {
    if (!loaded || mode !== "print" || isIOS || !iframeRef.current?.contentWindow) return;
    const timer = window.setTimeout(() => iframeRef.current?.contentWindow?.print(), 900);
    return () => window.clearTimeout(timer);
  }, [loaded, mode, isIOS]);

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
              {mode === "print"
                ? isIOS
                  ? "Use Safari Share / Print from this clean preview page."
                  : "Print dialogue opens automatically from this clean preview page."
                : "Use browser Print / Save as PDF from this clean preview page."}
            </p>
          </div>

          <div className="flex items-center gap-2 flex-wrap">
            <Button className="bg-blue-700 text-white hover:bg-blue-600" onClick={handleBack} data-testid="document-preview-close-button">
              <ArrowLeft className="w-4 h-4 mr-2" /> Back
            </Button>
            <Button
              className="bg-blue-700 text-white hover:bg-blue-600"
              onClick={() => iframeRef.current?.contentWindow?.print()}
              data-testid="document-preview-print-button"
            >
              <Printer className="w-4 h-4 mr-2" /> Print / Save as PDF
            </Button>
          </div>
        </div>
      </div>

      <div className="max-w-6xl mx-auto px-4 sm:px-6 pb-8" data-testid="document-preview-frame-wrap">
        <div className="bg-white border border-slate-200 rounded-2xl shadow-xl overflow-hidden min-h-[70vh]">
          <iframe
            ref={iframeRef}
            title={payload.title || "Document preview"}
            srcDoc={payload.html}
            className="w-full h-[78vh] bg-white"
            onLoad={() => setLoaded(true)}
            data-testid="document-preview-iframe"
          />
        </div>
      </div>
    </div>
  );
}