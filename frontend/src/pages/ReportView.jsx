/* ========================================================================
   DO NOT UNDO — ENTIRE FILE PROTECTED
   All features, functions, styles, and content in this file are approved
   and must be preserved. Do not remove, rename, or refactor any code.
   ======================================================================== */
import { useState, useEffect, useMemo } from "react";
import { useParams, useNavigate } from "react-router-dom";
import axios from "axios";
import { toast } from "sonner";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import {
  Scale,
  ArrowLeft,
  Download,
  Printer,
  Eye,
  Loader2,
  FileText,
  ListOrdered,
  Gavel,
  ChevronRight,
  Sparkles,
  ShieldCheck,
  Clock,
  BookOpen,
  AlertTriangle,
} from "lucide-react";
import { Button } from "../components/ui/button";
import { Badge } from "../components/ui/badge";
import { API } from "../App";

const titleFromSnake = (value) => {
  if (!value) return "Not specified";
  return value.replace(/_/g, " ").replace(/\b\w/g, (c) => c.toUpperCase());
};

const extractSentenceSummary = (analysis = "") => {
  const byLabel = analysis.match(/sentence[^\n:]*[:\-]\s*([^\n\.]{6,140})/i);
  if (byLabel?.[1]) return byLabel[1].trim();
  const byDuration = analysis.match(/([0-9]+(?:\.[0-9]+)?\s*(?:year|years|month|months)[^\n\.]{0,90})/i);
  if (byDuration?.[1]) return byDuration[1].trim();
  return "Not clearly stated in report";
};

const parseAnalysisSections = (analysis = "") => {
  const text = analysis.replace(/\r\n/g, "\n").trim();
  if (!text) return [];
  const lines = text.split("\n");
  const sections = [];
  let currentTitle = "Executive Analysis";
  let currentLines = [];

  const pushSection = () => {
    const content = currentLines.join("\n").trim();
    if (!content) return;
    sections.push({ id: `report-section-${sections.length + 1}`, title: currentTitle, content });
  };

  lines.forEach((line) => {
    const trimmed = line.trim();
    const markdownHeader = trimmed.match(/^#{1,3}\s+(.+)$/);
    const boldHeader = trimmed.length < 80 && trimmed.match(/^\*\*([^*]{4,70})\*\*$/);
    if (markdownHeader || boldHeader) {
      pushSection();
      currentTitle = (markdownHeader?.[1] || boldHeader?.[1] || "Analysis").replace(/[\-:]+$/, "").trim();
      currentLines = [];
      return;
    }
    currentLines.push(line);
  });

  pushSection();
  return sections.length > 0 ? sections : [{ id: "report-section-1", title: "Analysis", content: text }];
};

const MarkdownBlock = ({ text, testId }) => (
  <div className="legal-report" data-testid={testId}>
    <ReactMarkdown
      remarkPlugins={[remarkGfm]}
      components={{
        a: ({ href, children }) => (
          <a href={href} target="_blank" rel="noopener noreferrer" className="text-blue-600 underline underline-offset-2 hover:text-blue-800 break-words font-medium">{children}</a>
        ),
        table: ({ children }) => (
          <div className="legal-report-table-wrap" data-testid={`${testId}-table-wrapper`}>
            <table>{children}</table>
          </div>
        ),
      }}
    >
      {text}
    </ReactMarkdown>
  </div>
);

/* Colour configs per report type — matches landing page design */
const REPORT_THEME = {
  quick_summary: {
    label: "Quick Summary Report",
    headerBg: "bg-gradient-to-r from-emerald-700 to-green-600",
    accentBg: "bg-green-600",
    accentText: "text-green-600",
    priceBadge: "bg-green-500",
    price: "FREE",
    borderColor: "border-green-200 dark:border-green-800",
    lightBg: "from-green-50 to-white dark:from-green-900/20 dark:to-slate-900",
    sectionBorder: "border-green-500",
    tocBg: "bg-green-50 dark:bg-green-900/20",
    tocBorder: "border-green-200 dark:border-green-700",
    sectionNumberBg: "bg-green-100 text-green-700",
  },
  full_detailed: {
    label: "Full Detailed Report",
    headerBg: "bg-gradient-to-r from-slate-900 to-blue-900",
    accentBg: "bg-blue-600",
    accentText: "text-blue-600",
    priceBadge: "bg-blue-500",
    price: "$150 AUD",
    borderColor: "border-blue-200 dark:border-blue-800",
    lightBg: "from-blue-50 to-white dark:from-blue-900/20 dark:to-slate-900",
    sectionBorder: "border-blue-500",
    tocBg: "bg-blue-50/50 dark:bg-blue-900/20",
    tocBorder: "border-blue-200 dark:border-blue-700",
    sectionNumberBg: "bg-blue-100 text-blue-700",
  },
  extensive_log: {
    label: "Extensive Log Report",
    headerBg: "bg-gradient-to-r from-purple-900 via-slate-900 to-indigo-900",
    accentBg: "bg-purple-600",
    accentText: "text-purple-600",
    priceBadge: "bg-purple-500",
    price: "$200 AUD",
    borderColor: "border-purple-200 dark:border-purple-800",
    lightBg: "from-purple-50 to-white dark:from-purple-900/20 dark:to-slate-900",
    sectionBorder: "border-purple-500",
    tocBg: "bg-purple-50/50 dark:bg-purple-900/20",
    tocBorder: "border-purple-200 dark:border-purple-700",
    sectionNumberBg: "bg-purple-100 text-purple-700",
  },
};

const ReportView = () => {
  const { caseId, reportId } = useParams();
  const navigate = useNavigate();
  const [report, setReport] = useState(null);
  const [caseData, setCaseData] = useState(null);
  const [grounds, setGrounds] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchData();
  }, [caseId, reportId]);

  const fetchData = async () => {
    try {
      const [reportRes, caseRes, groundsRes] = await Promise.all([
        axios.get(`${API}/cases/${caseId}/reports/${reportId}`),
        axios.get(`${API}/cases/${caseId}`),
        axios.get(`${API}/cases/${caseId}/grounds`),
      ]);
      setReport(reportRes.data);
      setCaseData(caseRes.data);
      setGrounds(groundsRes.data?.grounds || []);
    } catch (error) {
      toast.error("Failed to load report");
      navigate(`/cases/${caseId}`);
    } finally {
      setLoading(false);
    }
  };

  const handlePrint = () => {
    window.print();
  };

  const handleExportPDF = async () => {
    try {
      toast.info("Generating PDF...");
      const isIOS = /iPad|iPhone|iPod/.test(navigator.userAgent);
      if (isIOS) {
        const a = document.createElement('a');
        a.href = `${API}/cases/${caseId}/reports/${reportId}/export-pdf`;
        a.target = '_blank';
        a.rel = 'noopener';
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        toast.success("PDF opening — use Share to save or print.");
        return;
      }
      const response = await axios.get(`${API}/cases/${caseId}/reports/${reportId}/export-pdf`, { responseType: "blob" });
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement("a");
      link.href = url;
      link.setAttribute("download", `${caseData?.title || "Report"}_${report?.report_type || "report"}.pdf`);
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(url);
      toast.success("PDF downloaded successfully!");
    } catch (error) {
      toast.error("Failed to export PDF.");
    }
  };

  const handleExportDOCX = async () => {
    try {
      toast.info("Generating Word document...");
      const isIOS = /iPad|iPhone|iPod/.test(navigator.userAgent);
      if (isIOS) {
        const a = document.createElement('a');
        a.href = `${API}/cases/${caseId}/reports/${reportId}/export-docx`;
        a.target = '_blank';
        a.rel = 'noopener';
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        toast.success("Word document opening — use Share to save.");
        return;
      }
      const response = await axios.get(`${API}/cases/${caseId}/reports/${reportId}/export-docx`, { responseType: "blob" });
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement("a");
      link.href = url;
      link.setAttribute("download", `${caseData?.title || "Report"}_${report?.report_type || "report"}.docx`);
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(url);
      toast.success("Word document downloaded successfully!");
    } catch (error) {
      toast.error("Failed to export Word document.");
    }
  };

  const formatDate = (dateStr) => {
    if (!dateStr) return "N/A";
    return new Date(dateStr).toLocaleDateString("en-AU", { day: "numeric", month: "long", year: "numeric", hour: "2-digit", minute: "2-digit" });
  };

  const analysisText = report?.content?.analysis || "";
  const sections = useMemo(() => parseAnalysisSections(analysisText), [analysisText]);
  const documentsCount = report?.content?.document_count || 0;
  const eventsCount = report?.content?.event_count || 0;
  const sentenceSummary = extractSentenceSummary(analysisText);
  const offenceLabel = caseData?.offence_type || titleFromSnake(caseData?.offence_category);
  const theme = REPORT_THEME[report?.report_type] || REPORT_THEME.quick_summary;

  const scrollToSection = (sectionId) => {
    document.getElementById(sectionId)?.scrollIntoView({ behavior: "smooth", block: "start" });
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-slate-50" data-testid="report-view-loading">
        <div className="text-center">
          <Loader2 className="w-12 h-12 animate-spin text-slate-400 mx-auto" />
          <p className="mt-4 text-slate-600">Loading report...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-slate-100 dark:bg-slate-950">
      {/* Sticky action bar */}
      <header className="bg-white/95 backdrop-blur border-b border-slate-200 sticky top-0 z-40 no-print" data-testid="report-header">
        <div className="max-w-5xl mx-auto px-4 sm:px-6 py-3">
          <div className="flex items-center justify-between gap-3 flex-wrap">
            <Button variant="ghost" size="sm" onClick={() => navigate(`/cases/${caseId}`)} data-testid="back-btn">
              <ArrowLeft className="w-4 h-4 mr-1" /> Back to Case
            </Button>
            <div className="flex items-center gap-2 flex-wrap">
              <Button variant="outline" size="sm" onClick={() => navigate(`/cases/${caseId}/reports/${reportId}/barrister`)} data-testid="barrister-view-btn">
                <Eye className="w-4 h-4 mr-2" /> Barrister View
              </Button>
              <Button variant="outline" size="sm" onClick={handlePrint} data-testid="print-btn">
                <Printer className="w-4 h-4 mr-2" /> Print
              </Button>
              <Button variant="outline" size="sm" onClick={handleExportDOCX} className="bg-blue-50 text-blue-700 border-blue-200 hover:bg-blue-100" data-testid="export-docx-btn">
                <FileText className="w-4 h-4 mr-2" /> Export Word
              </Button>
              <Button size="sm" onClick={handleExportPDF} className="bg-slate-900 text-white hover:bg-slate-800" data-testid="export-pdf-btn">
                <Download className="w-4 h-4 mr-2" /> Export PDF
              </Button>
            </div>
          </div>
        </div>
      </header>

      <main className="max-w-5xl mx-auto px-4 sm:px-6 py-8">
        <div className={`bg-gradient-to-r ${theme.lightBg} rounded-xl border ${theme.borderColor} overflow-hidden shadow-xl`} data-testid="report-content">

          {/* ===== COLOUR-CODED REPORT HEADER (matches landing page) ===== */}
          <div className={`${theme.headerBg} text-white p-6 sm:p-8`} data-testid="report-colour-header">
            <div className="flex items-center justify-between mb-4 flex-wrap gap-3">
              <div>
                <p className="text-xs uppercase tracking-wider opacity-70 mb-1">{theme.label}</p>
                <h1 className="text-2xl sm:text-3xl font-bold" style={{ fontFamily: "Crimson Pro, serif" }} data-testid="report-title">
                  {report?.title || `${caseData?.title || "Case"} Report`}
                </h1>
                <p className="text-sm opacity-80 mt-1">{caseData?.court || "Court"} — {(caseData?.state || "NSW").toUpperCase()}</p>
              </div>
              <div className="text-right">
                <p className="text-3xl font-bold opacity-90">{grounds.length} Ground{grounds.length !== 1 ? "s" : ""}</p>
                <p className="text-xs opacity-60">Identified</p>
              </div>
            </div>
            <div className="flex items-center gap-3 flex-wrap text-sm opacity-80">
              <span className={`${theme.priceBadge} px-3 py-1 rounded-full text-sm font-bold text-white`}>{theme.price}</span>
              {report?.content?.aggressive_mode && (
                <span className="bg-red-500 px-3 py-1 rounded-full text-sm font-bold text-white" data-testid="report-aggressive-mode-badge">Aggressive Mode</span>
              )}
              <span className="flex items-center gap-1"><Clock className="w-3.5 h-3.5" /> Generated: {formatDate(report?.generated_at)}</span>
            </div>
          </div>

          {/* ===== CASE OVERVIEW GRID ===== */}
          <div className="bg-white dark:bg-slate-800 border-b border-slate-200 dark:border-slate-700 p-5 sm:p-6" data-testid="report-top-summary-box">
            <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-5 gap-3 text-sm" style={{ fontFamily: "Crimson Pro, serif" }}>
              <div>
                <p className="text-xs text-slate-500 uppercase tracking-wide mb-0.5">Defendant</p>
                <p className="font-bold text-slate-900 dark:text-white" data-testid="report-summary-accused">{caseData?.defendant_name || "N/A"}</p>
              </div>
              <div>
                <p className="text-xs text-slate-500 uppercase tracking-wide mb-0.5">Offence</p>
                <p className="font-bold text-slate-900 dark:text-white" data-testid="report-summary-offence">{offenceLabel}</p>
              </div>
              <div>
                <p className="text-xs text-slate-500 uppercase tracking-wide mb-0.5">Sentence</p>
                <p className="font-bold text-slate-900 dark:text-white" data-testid="report-summary-sentence">{sentenceSummary}</p>
              </div>
              <div>
                <p className="text-xs text-slate-500 uppercase tracking-wide mb-0.5">Documents</p>
                <p className="font-bold text-slate-900 dark:text-white">{documentsCount} files analysed</p>
              </div>
              <div>
                <p className="text-xs text-slate-500 uppercase tracking-wide mb-0.5">Timeline Events</p>
                <p className="font-bold text-slate-900 dark:text-white">{eventsCount} events</p>
              </div>
            </div>
          </div>

          {/* ===== TABLE OF CONTENTS BAR (matches landing page grey bar) ===== */}
          {sections.length > 1 && (
            <div className={`${theme.tocBg} border-b ${theme.tocBorder} p-4 sm:p-5`} data-testid="report-table-of-contents">
              <div className="flex items-center gap-2 mb-2">
                <ListOrdered className="w-4 h-4 text-slate-600 dark:text-slate-400" />
                <p className="text-xs font-semibold text-slate-700 dark:text-slate-300 uppercase tracking-wide">
                  Contents ({sections.length} Sections)
                </p>
              </div>
              <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-1.5">
                {sections.map((section, idx) => (
                  <button
                    key={section.id}
                    onClick={() => scrollToSection(section.id)}
                    className="text-left text-xs text-slate-600 dark:text-slate-400 hover:text-blue-700 dark:hover:text-blue-300 transition-colors truncate"
                    data-testid={`report-toc-item-${idx + 1}`}
                  >
                    <span className="font-semibold text-slate-800 dark:text-slate-200">{idx + 1}.</span> {section.title}
                  </button>
                ))}
              </div>
            </div>
          )}

          {/* ===== REPORT SECTIONS ===== */}
          <div className="p-5 sm:p-6 md:p-8 space-y-6" data-testid="report-full-analysis-section">
            {sections.map((section, idx) => (
              <article key={section.id} id={section.id} className="scroll-mt-24">
                {/* Section header with coloured left border (matches landing page) */}
                <div className={`border-l-4 ${theme.sectionBorder} pl-4 mb-4`}>
                  <div className="flex items-center gap-3">
                    <span className={`inline-flex items-center justify-center w-7 h-7 rounded-full ${theme.sectionNumberBg} text-xs font-bold`}>
                      {idx + 1}
                    </span>
                    <h3
                      className="text-lg font-bold text-slate-900 dark:text-white uppercase tracking-wide"
                      style={{ fontFamily: "Crimson Pro, serif" }}
                      data-testid={`report-section-heading-${idx + 1}`}
                    >
                      {section.title}
                    </h3>
                  </div>
                </div>

                {/* Section content with professional markdown rendering */}
                <div className="bg-white dark:bg-slate-800 rounded-lg border border-slate-200 dark:border-slate-700 p-5 sm:p-6 shadow-sm" data-testid={`report-section-content-${idx + 1}`}>
                  <MarkdownBlock text={section.content} testId={`report-section-md-${idx + 1}`} />
                </div>

                <button
                  onClick={() => window.scrollTo({ top: 0, behavior: "smooth" })}
                  className="mt-2 inline-flex items-center gap-1 text-xs text-slate-500 hover:text-slate-700 dark:hover:text-slate-300"
                  data-testid={`report-back-to-top-${idx + 1}`}
                >
                  <ChevronRight className="w-3 h-3 rotate-[-90deg]" /> Back to top
                </button>
              </article>
            ))}
          </div>

          {/* ===== DISCLAIMER FOOTER ===== */}
          <div className="bg-slate-50 dark:bg-slate-800/50 border-t border-slate-200 dark:border-slate-700 p-5 sm:p-6" data-testid="report-footer">
            <div className="flex items-start gap-3 mb-3">
              <AlertTriangle className="w-5 h-5 text-red-500 flex-shrink-0 mt-0.5" />
              <div>
                <p className="text-xs font-bold text-slate-800 dark:text-slate-200 uppercase tracking-wide mb-1">Not Legal Advice</p>
                <p className="text-xs text-slate-600 dark:text-slate-400">This report does NOT constitute legal advice. All findings must be verified by a qualified Australian legal professional before any action is taken.</p>
              </div>
            </div>
            <div className="text-center pt-3 border-t border-slate-200 dark:border-slate-700">
              <p className="text-xs text-slate-500">
                Prepared by <strong>Appeal Case Manager</strong> — AI-Powered Criminal Appeal Research Tool
              </p>
            </div>
          </div>
        </div>
      </main>

      <style>{`
        @media print {
          .no-print { display: none !important; }
        }
      `}</style>
    </div>
  );
};

export default ReportView;
