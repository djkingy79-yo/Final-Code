/*  — SectionTranslatableReport component (14 Feb 2026).
   Renders a markdown report split by H2 headings so each section can be
   translated individually via POST /api/cases/{case_id}/translate-section.
   Keeps the existing legal-report styling untouched. */
import { useMemo, useState } from "react";
import axios from "axios";
import { toast } from "sonner";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import { Languages, Loader2, ChevronDown, X } from "lucide-react";
import { Button } from "./ui/button";
import { API } from "../App";

// Trimmed language list — matches SUPPORTED_LANGUAGES on the backend.
const SECTION_LANGUAGES = [
  { code: "zh", name: "Chinese (Simplified)" },
  { code: "ar", name: "Arabic" },
  { code: "es", name: "Spanish" },
  { code: "fr", name: "French" },
  { code: "vi", name: "Vietnamese" },
  { code: "hi", name: "Hindi" },
  { code: "it", name: "Italian" },
  { code: "pt", name: "Portuguese" },
  { code: "de", name: "German" },
  { code: "ja", name: "Japanese" },
  { code: "ko", name: "Korean" },
  { code: "tl", name: "Filipino/Tagalog" },
  { code: "el", name: "Greek" },
  { code: "tr", name: "Turkish" },
  { code: "ru", name: "Russian" },
  { code: "th", name: "Thai" },
  { code: "ms", name: "Malay" },
  { code: "id", name: "Indonesian" },
  { code: "pl", name: "Polish" },
  { code: "nl", name: "Dutch" },
];

// Split a markdown string into [{heading, body}] sections on H2 headings.
// Content before the first H2 is preserved as a "preamble" with no heading.
function splitSections(markdown) {
  if (!markdown) return [];
  const lines = markdown.split("\n");
  const sections = [];
  let current = { heading: null, body: [] };
  for (const line of lines) {
    const h2 = line.match(/^##\s+(.+?)\s*$/);
    if (h2) {
      if (current.body.length || current.heading) {
        sections.push({ ...current, body: current.body.join("\n").trim() });
      }
      current = { heading: h2[1], body: [] };
    } else {
      current.body.push(line);
    }
  }
  if (current.body.length || current.heading) {
    sections.push({ ...current, body: current.body.join("\n").trim() });
  }
  return sections;
}

const MARKDOWN_COMPONENTS = {
  a: ({ href, children }) => (
    <a href={href} target="_blank" rel="noopener noreferrer" className="text-blue-600 underline hover:text-blue-800 break-words font-medium">
      {children}
    </a>
  ),
  table: ({ children }) => (
    <div className="legal-report-table-wrap">
      <table>{children}</table>
    </div>
  ),
};

const SectionTranslateMenu = ({ onPick, onClose, activeCode }) => (
  <div
    className="absolute right-0 top-full mt-1 z-20 bg-white border border-slate-200 rounded-lg shadow-lg w-56 max-h-80 overflow-y-auto"
    data-testid="section-translate-menu"
  >
    <div className="sticky top-0 bg-slate-50 px-3 py-2 text-xs font-semibold text-slate-600 border-b border-slate-200 flex items-center justify-between">
      Translate this section to…
      <button onClick={onClose} className="text-slate-400 hover:text-slate-700" aria-label="Close" data-testid="section-translate-close">
        <X className="w-3.5 h-3.5" />
      </button>
    </div>
    <ul>
      {SECTION_LANGUAGES.map((lang) => (
        <li key={lang.code}>
          <button
            onClick={() => onPick(lang.code, lang.name)}
            className={`w-full text-left px-3 py-2 text-sm hover:bg-blue-50 ${activeCode === lang.code ? "bg-blue-50 font-semibold text-blue-700" : "text-slate-700"}`}
            data-testid={`section-translate-pick-${lang.code}`}
          >
            {lang.name}
          </button>
        </li>
      ))}
    </ul>
  </div>
);

const Section = ({ heading, body, reportId, caseId, index }) => {
  const [menuOpen, setMenuOpen] = useState(false);
  const [loading, setLoading] = useState(false);
  const [translation, setTranslation] = useState(null); // { code, name, content }

  const canTranslate = !!heading && !!body && !!reportId && !!caseId;

  const handleTranslate = async (code, name) => {
    setMenuOpen(false);
    if (!canTranslate) return;
    setLoading(true);
    try {
      const res = await axios.post(
        `${API}/cases/${caseId}/translate-section`,
        {
          report_id: reportId,
          language: code,
          section_heading: heading,
          section_text: body,
        },
        { timeout: 180000 },
      );
      if (res.data?.status === "completed") {
        setTranslation({ code, name, content: res.data.translated_content });
        toast.success(
          res.data.cached ? `${name} translation loaded from cache.` : `Translated "${heading}" to ${name}.`,
        );
      } else {
        toast.error("Section translation failed.");
      }
    } catch (err) {
      const detail = err.response?.data?.detail || err.message || "Translation failed";
      toast.error(detail);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="relative mb-4" data-testid={`report-section-${index}`}>
      {heading && (
        <div className="flex items-start justify-between gap-3 mb-2">
          <h2 className="text-xl font-bold text-slate-900 leading-snug flex-1" style={{ fontFamily: "'Times New Roman', Times, serif" }}>
            {heading}
          </h2>
          {canTranslate && (
            <div className="relative shrink-0 print:hidden">
              <Button
                size="sm"
                variant="outline"
                onClick={() => setMenuOpen((v) => !v)}
                disabled={loading}
                className="h-8 text-xs border-blue-200 text-blue-700 hover:bg-blue-50"
                data-testid={`section-translate-btn-${index}`}
              >
                {loading ? (
                  <Loader2 className="w-3.5 h-3.5 mr-1.5 animate-spin" />
                ) : (
                  <Languages className="w-3.5 h-3.5 mr-1.5" />
                )}
                Translate section
                <ChevronDown className="w-3 h-3 ml-1" />
              </Button>
              {menuOpen && (
                <SectionTranslateMenu
                  onPick={handleTranslate}
                  onClose={() => setMenuOpen(false)}
                  activeCode={translation?.code}
                />
              )}
            </div>
          )}
        </div>
      )}

      <ReactMarkdown remarkPlugins={[remarkGfm]} components={MARKDOWN_COMPONENTS}>
        {body}
      </ReactMarkdown>

      {translation && (
        <div
          className="mt-4 border-l-4 border-blue-600 bg-blue-50/40 pl-4 pr-3 py-3 rounded-r print:hidden"
          data-testid={`section-translation-${index}`}
        >
          <div className="flex items-center justify-between mb-2">
            <p className="text-xs font-semibold text-blue-700 uppercase tracking-wide">
              {translation.name} translation
            </p>
            <button
              onClick={() => setTranslation(null)}
              className="text-xs text-blue-700 hover:text-blue-900 underline"
              data-testid={`section-translation-hide-${index}`}
            >
              Hide
            </button>
          </div>
          <div className="legal-report">
            <ReactMarkdown remarkPlugins={[remarkGfm]} components={MARKDOWN_COMPONENTS}>
              {translation.content}
            </ReactMarkdown>
          </div>
        </div>
      )}
    </div>
  );
};

const SectionTranslatableReport = ({ reportText, reportId, caseId }) => {
  const sections = useMemo(() => splitSections(reportText), [reportText]);

  if (!sections.length) return null;

  return (
    <div className="legal-report" data-testid="section-translatable-report">
      {sections.map((s, i) => (
        <Section
          key={`${s.heading || "preamble"}-${i}`}
          heading={s.heading}
          body={s.body}
          reportId={reportId}
          caseId={caseId}
          index={i}
        />
      ))}
    </div>
  );
};

export default SectionTranslatableReport;
