import { useState, useEffect } from "react";
import axios from "axios";
import { toast } from "sonner";
import { Languages, Loader2, FileDown } from "lucide-react";
import { Button } from "./ui/button";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
} from "./ui/dialog";
import { API } from "../App";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";

const ReportTranslator = ({ caseId, reportId }) => {
  const [showDialog, setShowDialog] = useState(false);
  const [languages, setLanguages] = useState([]);
  const [selectedLang, setSelectedLang] = useState("");
  const [translating, setTranslating] = useState(false);
  const [translatedContent, setTranslatedContent] = useState(null);
  const [translatedLangName, setTranslatedLangName] = useState("");
  const [translatedLangCode, setTranslatedLangCode] = useState("");
  const [showTranslation, setShowTranslation] = useState(false);
  const [searchQuery, setSearchQuery] = useState("");
  const [downloadingPDF, setDownloadingPDF] = useState(false);

  useEffect(() => {
    if (showDialog && languages.length === 0) {
      axios.get(`${API}/languages`)
        .then(res => setLanguages(res.data.languages || []))
        .catch(() => toast.error("Failed to load languages"));
    }
  }, [showDialog, languages.length]);

  const filteredLanguages = languages.filter(l =>
    l.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
    l.code.toLowerCase().includes(searchQuery.toLowerCase())
  );

  const handleTranslate = async () => {
    if (!selectedLang) {
      toast.error("Please select a language");
      return;
    }
    setTranslating(true);
    try {
      const response = await axios.post(
        `${API}/cases/${caseId}/translate`,
        { language: selectedLang, report_id: reportId },
        { timeout: 30000 }
      );

      // If cached result returned immediately
      if (response.data.translated_content) {
        setTranslatedContent(response.data.translated_content);
        setTranslatedLangName(response.data.language_name);
        setTranslatedLangCode(selectedLang);
        setShowDialog(false);
        setShowTranslation(true);
        toast.success(`Report translated to ${response.data.language_name}${response.data.cached ? " (cached)" : ""}`);
        setTranslating(false);
        return;
      }

      // Background task started — poll for completion
      if (response.data.status === "started" || response.data.status === "running") {
        setShowDialog(false);
        toast.info(`Translating to ${response.data.language_name}... This runs in the background.`);
        const langName = response.data.language_name;
        let attempts = 0;
        const maxAttempts = 120;
        const pollInterval = 4000;

        const poll = async () => {
          attempts++;
          try {
            const statusRes = await axios.get(
              `${API}/cases/${caseId}/translate/status?report_id=${reportId}&language=${selectedLang}`,
              { timeout: 15000 }
            );
            const { status, translated_content, error, progress, total_chunks } = statusRes.data;

            if (status === "completed" && translated_content) {
              setTranslatedContent(translated_content);
              setTranslatedLangName(langName);
              setTranslatedLangCode(selectedLang);
              setShowTranslation(true);
              setTranslating(false);
              toast.success(`Translation to ${langName} complete!`);
              return;
            }

            if (status === "failed") {
              setTranslating(false);
              toast.error(error || "Translation failed. Please try again.");
              return;
            }

            if (status === "not_found") {
              setTranslating(false);
              toast.error("Translation task not found. Please try again.");
              return;
            }

            if (attempts >= maxAttempts) {
              setTranslating(false);
              toast.error("Translation is taking longer than expected. Please check back shortly.");
              return;
            }

            if (progress > 0 && total_chunks > 0 && attempts % 5 === 0) {
              toast.info(`Translating... ${progress}/${total_chunks} sections complete.`, { id: "translate-progress" });
            }

            setTimeout(poll, pollInterval);
          } catch (pollErr) {
            if (attempts >= maxAttempts) {
              setTranslating(false);
              toast.error("Lost connection to translation. Please refresh and check if it completed.");
            } else {
              setTimeout(poll, pollInterval);
            }
          }
        };

        setTimeout(poll, 3000);
        return;
      }

      // Unexpected response
      setTranslating(false);
      toast.error("Unexpected response from translation service.");
    } catch (error) {
      let msg;
      if (error.code === 'ECONNABORTED' || error.message?.includes('timeout')) {
        msg = "Translation request timed out. Please try again.";
      } else if (error.response?.status === 500) {
        msg = error.response?.data?.detail || "Translation service error. Please try again in a moment.";
      } else {
        msg = error.response?.data?.detail || "Translation failed. Check your connection and try again.";
      }
      toast.error(msg);
      setTranslating(false);
    }
  };

  const handleDownloadTranslatedPDF = async () => {
    setDownloadingPDF(true);
    try {
      const response = await axios.get(
        `${API}/cases/${caseId}/translate/${reportId}/pdf?lang=${translatedLangCode}`,
        { responseType: 'blob', timeout: 120000 }
      );
      const url = window.URL.createObjectURL(new Blob([response.data], { type: 'application/pdf' }));
      const isIOS = /iPad|iPhone|iPod/.test(navigator.userAgent);
      if (isIOS) {
        window.open(url, '_blank');
        toast.success("PDF opened — use Share to save.");
      } else {
        const link = document.createElement('a');
        link.href = url;
        const contentDisposition = response.headers['content-disposition'];
        let filename = `Report_${translatedLangName}_Translation.pdf`;
        if (contentDisposition) {
          const match = contentDisposition.match(/filename="(.+)"/);
          if (match) filename = match[1];
        }
        link.setAttribute('download', filename);
        document.body.appendChild(link);
        link.click();
        link.remove();
        window.URL.revokeObjectURL(url);
        toast.success(`${translatedLangName} PDF downloaded!`);
      }
    } catch (error) {
      toast.error("Failed to generate translated PDF. Please try again.");
    } finally {
      setDownloadingPDF(false);
    }
  };

  return (
    <>
      <Button
        size="sm"
        onClick={() => setShowDialog(true)}
        className="bg-blue-700 text-white hover:bg-blue-600"
        data-testid="translate-report-btn"
      >
        <Languages className="w-4 h-4 mr-2" />
        Translate
      </Button>

      {/* Language Selection Dialog */}
      <Dialog open={showDialog} onOpenChange={setShowDialog}>
        <DialogContent className="max-w-md">
          <DialogHeader>
            <DialogTitle className="flex items-center gap-3" style={{ fontFamily: "'Times New Roman', Times, serif" }}>
              <div className="w-10 h-10 rounded-xl bg-blue-100 flex items-center justify-center">
                <Languages className="w-5 h-5 text-blue-600" />
              </div>
              Translate Report
            </DialogTitle>
          </DialogHeader>

          <div className="py-4">
            <p className="text-sm text-slate-600 mb-4">
              Select a language to translate this report. Legal terminology and formatting will be preserved.
            </p>

            {/* Search */}
            <input
              type="text"
              placeholder="Search languages..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full px-3 py-2 border border-slate-200 rounded-lg text-sm mb-3 focus:outline-none focus:border-blue-400"
              data-testid="language-search-input"
            />

            {/* Language grid */}
            <div className="max-h-64 overflow-y-auto space-y-1 border border-slate-200 rounded-xl p-2">
              {filteredLanguages.map((lang) => (
                <button
                  key={lang.code}
                  onClick={() => setSelectedLang(lang.code)}
                  className={`w-full text-left px-3 py-2 rounded-lg text-sm transition-colors ${
                    selectedLang === lang.code
                      ? "bg-blue-600 text-white font-semibold"
                      : "hover:bg-slate-100 text-slate-700"
                  }`}
                  data-testid={`lang-option-${lang.code}`}
                >
                  {lang.name}
                </button>
              ))}
              {filteredLanguages.length === 0 && (
                <p className="text-sm text-slate-400 text-center py-4">No languages found</p>
              )}
            </div>

            {selectedLang && (
              <p className="text-xs text-blue-600 mt-2 font-medium">
                Selected: {languages.find(l => l.code === selectedLang)?.name}
              </p>
            )}
          </div>

          <div className="flex gap-3 justify-end">
            <Button onClick={() => setShowDialog(false)} className="bg-slate-200 text-slate-700 hover:bg-slate-300">
              Cancel
            </Button>
            <Button
              onClick={handleTranslate}
              disabled={translating || !selectedLang}
              className="bg-blue-600 text-white hover:bg-blue-700 font-semibold"
              data-testid="confirm-translate-btn"
            >
              {translating ? (
                <>
                  <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                  Translating...
                </>
              ) : (
                <>
                  <Languages className="w-4 h-4 mr-2" />
                  Translate
                </>
              )}
            </Button>
          </div>
        </DialogContent>
      </Dialog>

      {/* Translation Result Panel */}
      {showTranslation && translatedContent && (
        <Dialog open={showTranslation} onOpenChange={setShowTranslation}>
          <DialogContent className="max-w-4xl max-h-[85vh] overflow-hidden flex flex-col">
            <DialogHeader>
              <DialogTitle className="flex items-center justify-between">
                <span className="flex items-center gap-2" style={{ fontFamily: "'Times New Roman', Times, serif" }}>
                  <Languages className="w-5 h-5 text-blue-600" />
                  Translation — {translatedLangName}
                </span>
              </DialogTitle>
            </DialogHeader>
            <div className="flex-1 overflow-y-auto prose prose-sm max-w-none p-4 bg-slate-50 rounded-xl border border-slate-200">
              <ReactMarkdown
                remarkPlugins={[remarkGfm]}
                components={{
                  table: ({children}) => (
                    <table style={{width: '100%', borderCollapse: 'collapse', marginBottom: '1rem', fontSize: '13px'}}>
                      {children}
                    </table>
                  ),
                  thead: ({children}) => (
                    <thead style={{backgroundColor: '#1e3a5f', color: 'white'}}>
                      {children}
                    </thead>
                  ),
                  th: ({children}) => (
                    <th style={{border: '1px solid #cbd5e1', padding: '8px 12px', textAlign: 'left', fontWeight: 600}}>
                      {children}
                    </th>
                  ),
                  td: ({children}) => (
                    <td style={{border: '1px solid #cbd5e1', padding: '8px 12px', verticalAlign: 'top'}}>
                      {children}
                    </td>
                  ),
                  tr: ({children, ...props}) => (
                    <tr style={{backgroundColor: props.isHeader ? undefined : 'white'}} {...props}>
                      {children}
                    </tr>
                  ),
                  h1: ({children}) => <h1 style={{fontFamily: "'Times New Roman', serif", color: '#1e3a5f', borderBottom: '2px solid #1e3a5f', paddingBottom: '6px'}}>{children}</h1>,
                  h2: ({children}) => <h2 style={{fontFamily: "'Times New Roman', serif", color: '#1e3a5f', borderBottom: '1px solid #cbd5e1', paddingBottom: '4px'}}>{children}</h2>,
                  h3: ({children}) => <h3 style={{fontFamily: "'Times New Roman', serif", color: '#334155'}}>{children}</h3>,
                  p: ({children}) => <p style={{marginBottom: '0.75rem', lineHeight: '1.7'}}>{children}</p>,
                  strong: ({children}) => <strong style={{color: '#1e3a5f'}}>{children}</strong>,
                }}
              >
                {translatedContent}
              </ReactMarkdown>
            </div>
            <div className="flex gap-3 justify-end pt-4">
              <Button
                onClick={handleDownloadTranslatedPDF}
                disabled={downloadingPDF}
                className="bg-blue-600 text-white hover:bg-blue-700"
                data-testid="download-translated-pdf-btn"
              >
                {downloadingPDF ? (
                  <>
                    <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                    Generating PDF...
                  </>
                ) : (
                  <>
                    <FileDown className="w-4 h-4 mr-2" />
                    Download PDF
                  </>
                )}
              </Button>
              <Button
                onClick={() => {
                  navigator.clipboard.writeText(translatedContent);
                  toast.success("Translation copied to clipboard");
                }}
                className="bg-slate-700 text-white hover:bg-slate-600"
                data-testid="copy-translation-btn"
              >
                Copy to Clipboard
              </Button>
              <Button onClick={() => setShowTranslation(false)} className="bg-slate-200 text-slate-700 hover:bg-slate-300">
                Close
              </Button>
            </div>
          </DialogContent>
        </Dialog>
      )}
    </>
  );
};

export default ReportTranslator;
