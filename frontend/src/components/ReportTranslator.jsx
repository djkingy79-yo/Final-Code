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
        { timeout: 180000 }
      );
      setTranslatedContent(response.data.translated_content);
      setTranslatedLangName(response.data.language_name);
      setTranslatedLangCode(selectedLang);
      setShowDialog(false);
      setShowTranslation(true);
      toast.success(`Report translated to ${response.data.language_name}${response.data.cached ? " (cached)" : ""}`);
    } catch (error) {
      const msg = error.response?.data?.detail || "Translation failed. Please try again.";
      toast.error(msg);
    } finally {
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
            <DialogTitle className="flex items-center gap-3" style={{ fontFamily: 'Crimson Pro, serif' }}>
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
                <span className="flex items-center gap-2" style={{ fontFamily: 'Crimson Pro, serif' }}>
                  <Languages className="w-5 h-5 text-blue-600" />
                  Translation — {translatedLangName}
                </span>
              </DialogTitle>
            </DialogHeader>
            <div className="flex-1 overflow-y-auto prose prose-sm max-w-none p-4 bg-slate-50 rounded-xl border border-slate-200">
              <div style={{ whiteSpace: "pre-wrap", fontFamily: "Helvetica, Arial, sans-serif", fontSize: "14px", lineHeight: "1.6" }}>
                {translatedContent}
              </div>
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
