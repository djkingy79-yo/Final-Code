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

const cleanSentence = (s) => {
  if (!s) return s;
  let c = s.replace(/\s*\[.*$/, "").replace(/\s*\(https?:.*$/, "").replace(/\s*\(http.*$/, "").replace(/\s*https?:.*$/, "");
  c = c.trim();
  return c.trim();
};

const extractSentenceSummary = (caseInfo, analysis = "") => {
  if (caseInfo?.sentence && caseInfo.sentence.trim().length > 3) return caseInfo.sentence.trim();
  const combined = analysis.match(/sentenced?\s+to\s+([^\n\.]{10,180}?(?:non[- ]?parole\s+period|NPP)[^\n\.]{0,160})/i);
  if (combined?.[1]) return cleanSentence(combined[1]);
  // Match "sentenced to X years imprisonment" patterns
  const byVerb = analysis.match(/(?:was\s+)?sentenced?\s+to\s+(\d+\s*(?:years?|months?)\s+(?:and\s+\d+\s*(?:years?|months?)\s+)?(?:imprisonment|gaol|jail|custody)[^\n\.]{0,80})/i);
  if (byVerb?.[1]) return cleanSentence(byVerb[1]);
  // Match "Head Sentence: X years"
  const byHead = analysis.match(/(?:^|\n)\s*(?:Head\s+)?Sentence\s*:\s*(\d+[^\n]{5,100})/im);
  if (byHead?.[1] && /\d+\s*(year|month|life)/i.test(byHead[1])) return cleanSentence(byHead[1]);
  // Match "life imprisonment" / "imprisonment for life"
  const byLife = analysis.match(/(?:sentenced?\s+to\s+)?(life\s+imprisonment|imprisonment\s+for\s+life|life\s+sentence)[^\n\.]{0,60}/i);
  if (byLife) return cleanSentence(byLife[0].replace(/^sentenced?\s+to\s+/i, ""));
  // Match "X years' imprisonment" or "X-year sentence"
  const byYears = analysis.match(/(\d+[\s-]*(?:years?|months?)(?:'s?)?\s*(?:imprisonment|gaol|jail|custody|sentence|non[- ]?parole)[^\n\.]{0,80})/i);
  if (byYears?.[1]) return cleanSentence(byYears[1]);
  // Match "sentence of X years"
  const bySentOf = analysis.match(/sentence\s+of\s+(\d+[^\n\.]{5,80})/i);
  if (bySentOf?.[1]) return cleanSentence(bySentOf[1]);
  // Match "minimum/non-parole period of X years"
  const byNPP = analysis.match(/((?:minimum|non[- ]?parole)\s+(?:period\s+)?of\s+\d+[^\n\.]{3,60})/i);
  if (byNPP?.[1]) return cleanSentence(byNPP[1]);
  return "Not recorded";
};

const extractOffenceFromAnalysis = (analysis = "") => {
  const patterns = [
    /(?:offence(?:s)?\s+of|for\s+the\s+offence\s+of|convicted\s+of|charged\s+with)\s+([A-Z][A-Za-z0-9\s,'-]{4,120})/i,
    /(?:primary|principal)\s+offence(?:\s+was|:)?\s+([A-Z][A-Za-z0-9\s,'-]{4,120})/i,
    /(?:count\s+\d+\s*[:\-])\s*([A-Z][A-Za-z0-9\s,'-]{4,120})/i
  ];

  for (const pattern of patterns) {
    const match = analysis.match(pattern);
    if (match?.[1]) {
      return match[1]
        .replace(/under\s+s\.[^\n\.]+/i, "")
        .replace(/,?\s*(?:under|pursuant\s+to).*/i, "")
        .trim();
    }
  }
  return "Not specified";
};

const extractDefendantFromAnalysis = (analysis = "") => {
  const byCaseName = analysis.match(/\bR\s+v\.?\s+([A-Z][A-Za-z\s'\-]{2,60})/);
  if (byCaseName?.[1]) return byCaseName[1].trim();
  const byAppellant = analysis.match(/(?:the\s+)?appellant\s+([A-Z][A-Za-z\s'\-]{2,60})/i);
  if (byAppellant?.[1]) return byAppellant[1].trim();
  const byDefendant = analysis.match(/(?:the\s+)?defendant\s+(?:was|is|,)?\s*([A-Z][A-Za-z\s'\-]{2,60})/i);
  if (byDefendant?.[1]) return byDefendant[1].trim();
  return "N/A";
};

const cleanAIContent = (text) => {
  if (!text) return text;
  let cleaned = text;
  // Strip AI preamble lines ("Certainly!", "Here's a comprehensive...", "Sure!", etc.)
  cleaned = cleaned.replace(/^(Certainly!|Sure!|Of course!|Absolutely!|Here('s| is) a comprehensive[^\n]*\n?)/i, "");
  cleaned = cleaned.replace(/^(Here('s| is) (a |the |your )?detailed[^\n]*\n?)/i, "");
  cleaned = cleaned.replace(/^(Here('s| is) (a |the |your )?thorough[^\n]*\n?)/i, "");
  cleaned = cleaned.replace(/^(I('ve| have) (prepared|created|compiled|generated)[^\n]*\n?)/i, "");
  // Strip bracket placeholder notes — BOTH square [] and round () brackets
  cleaned = cleaned.replace(/\[Note:\s*[^\]]*\]/gi, "");
  cleaned = cleaned.replace(/\[Continue[^\]]*\]/gi, "");
  cleaned = cleaned.replace(/\[Repeat[^\]]*\]/gi, "");
  cleaned = cleaned.replace(/\[Follow[^\]]*\]/gi, "");
  cleaned = cleaned.replace(/\[Insert[^\]]*\]/gi, "");
  cleaned = cleaned.replace(/\[Add[^\]]*\]/gi, "");
  cleaned = cleaned.replace(/\[Include[^\]]*\]/gi, "");
  cleaned = cleaned.replace(/\[Provide[^\]]*\]/gi, "");
  cleaned = cleaned.replace(/\[Similar[^\]]*\]/gi, "");
  cleaned = cleaned.replace(/\[See[^\]]*\]/gi, "");
  // Round bracket notes — (Note: ...), (See: ...), etc.
  cleaned = cleaned.replace(/\(Note:\s*[^)]*\)/gi, "");
  cleaned = cleaned.replace(/\(See:\s*[^)]*\)/gi, "");
  cleaned = cleaned.replace(/\(Continue[^)]*\)/gi, "");
  cleaned = cleaned.replace(/\(Link formatting[^)]*\)/gi, "");
  cleaned = cleaned.replace(/\(Entries will[^)]*\)/gi, "");
  // Strip AI meta-commentary about truncation or its own output
  cleaned = cleaned.replace(/\n*This truncated document[^\n]*/gi, "");
  cleaned = cleaned.replace(/\n*This (?:document|report|analysis) (?:provides|covers|contains|demonstrates)[^\n]*(?:sections?|overview|summary)[^\n]*/gi, "");
  cleaned = cleaned.replace(/\n*Each section (?:demonstrates|provides|covers)[^\n]*/gi, "");
  cleaned = cleaned.replace(/\n*The sections? above (?:are|is|were|was) (?:crafted|designed|written|prepared|created)[^\n]*/gi, "");
  cleaned = cleaned.replace(/\n*(?:The above|These) sections? (?:are|is|were|was) (?:crafted|designed|written|prepared|created)[^\n]*/gi, "");
  cleaned = cleaned.replace(/\n*(?:presenting|advances?) (?:a comprehensive|field-specific|detailed)[^\n]*(?:court of appeal|legal professionals?)[^\n]*/gi, "");
  
  // Convert American spellings to Australian
  const ausReplacements = [
    [/\bfinalized\b/gi, (m) => m[0] === 'F' ? 'Finalised' : 'finalised'],
    [/\brecognized\b/gi, (m) => m[0] === 'R' ? 'Recognised' : 'recognised'],
    [/\borganized\b/gi, (m) => m[0] === 'O' ? 'Organised' : 'organised'],
    [/\bsummarized\b/gi, (m) => m[0] === 'S' ? 'Summarised' : 'summarised'],
    [/\bprioritized\b/gi, (m) => m[0] === 'P' ? 'Prioritised' : 'prioritised'],
    [/\banalyzing\b/gi, (m) => m[0] === 'A' ? 'Analysing' : 'analysing'],
    [/\banalyzed\b/gi, (m) => m[0] === 'A' ? 'Analysed' : 'analysed'],
    [/\banalyze\b/gi, (m) => m[0] === 'A' ? 'Analyse' : 'analyse'],
    [/\bbehavior\b/gi, (m) => m[0] === 'B' ? 'Behaviour' : 'behaviour'],
    [/\bfavored\b/gi, (m) => m[0] === 'F' ? 'Favoured' : 'favoured'],
    [/\bfavoring\b/gi, (m) => m[0] === 'F' ? 'Favouring' : 'favouring'],
    [/\bfavor\b/gi, (m) => m[0] === 'F' ? 'Favour' : 'favour'],
    [/\bhonor\b/gi, (m) => m[0] === 'H' ? 'Honour' : 'honour'],
    [/\bdefense\b/gi, (m) => m[0] === 'D' ? 'Defence' : 'defence'],
    [/\boffense\b/gi, (m) => m[0] === 'O' ? 'Offence' : 'offence'],
    [/\blabor\b/gi, (m) => m[0] === 'L' ? 'Labour' : 'labour'],
    [/\bcenter\b/gi, (m) => m[0] === 'C' ? 'Centre' : 'centre'],
    [/\bspecialized\b/gi, (m) => m[0] === 'S' ? 'Specialised' : 'specialised'],
    [/\bcharacterized\b/gi, (m) => m[0] === 'C' ? 'Characterised' : 'characterised'],
    [/\butilized\b/gi, (m) => m[0] === 'U' ? 'Utilised' : 'utilised'],
    [/\bemphasized\b/gi, (m) => m[0] === 'E' ? 'Emphasised' : 'emphasised'],
    [/\bemphasize\b/gi, (m) => m[0] === 'E' ? 'Emphasise' : 'emphasise'],
    [/\bminimize\b/gi, (m) => m[0] === 'M' ? 'Minimise' : 'minimise'],
    [/\bmaximize\b/gi, (m) => m[0] === 'M' ? 'Maximise' : 'maximise'],
    [/\bcriticized\b/gi, (m) => m[0] === 'C' ? 'Criticised' : 'criticised'],
    [/\bcriticize\b/gi, (m) => m[0] === 'C' ? 'Criticise' : 'criticise'],
  ];
  for (const [pattern, replacer] of ausReplacements) {
    cleaned = cleaned.replace(pattern, replacer);
  }
  
  return cleaned.trim();
};

const parseAnalysisSections = (analysis = "") => {
  const text = cleanAIContent(analysis.replace(/\r\n/g, "\n").trim());
  if (!text) return [];
  const lines = text.split("\n");
  const sections = [];
  const cleanSectionTitle = (value) => (value || "")
    .replace(/^\d+\.\s*/, "")
    .replace(/[\-:]+$/, "")
    .replace(/\*\*/g, "")
    .trim();
  let currentTitle = "Executive Analysis";
  let currentLines = [];

  const pushSection = () => {
    const content = cleanAIContent(currentLines.join("\n").trim());
    if (!content || content.length < 80) return;
    sections.push({ id: `report-section-${sections.length + 1}`, title: currentTitle, content });
  };

  lines.forEach((line) => {
    const trimmed = line.trim();
    const mainSectionHeader = trimmed.match(/^##\s+(\d+\.\s+.+)$/);
    if (mainSectionHeader) {
      pushSection();
      currentTitle = cleanSectionTitle(mainSectionHeader[1]);
      currentLines = [];
      return;
    }
    currentLines.push(line);
  });

  pushSection();
  return sections.length > 0 ? sections : [{ id: "report-section-1", title: "Analysis", content: text }];
};

const MarkdownBlock = ({ text, testId }) => (
  <div className="legal-report text-[1.02rem] sm:text-[1.08rem] text-slate-100" data-testid={testId}>
    <ReactMarkdown
      remarkPlugins={[remarkGfm]}
      components={{
        a: ({ href, children }) => (
          <a href={href} target="_blank" rel="noopener noreferrer" className="text-blue-300 underline underline-offset-2 hover:text-blue-200 break-words font-medium">{children}</a>
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
    headerBg: "bg-gradient-to-r from-emerald-600 via-emerald-500 to-lime-500",
    accentBg: "bg-emerald-600",
    accentText: "text-emerald-700",
    priceBadge: "bg-emerald-500",
    price: "FREE",
    borderColor: "border-emerald-300 dark:border-emerald-700",
    lightBg: "from-emerald-50 via-white to-lime-50 dark:from-emerald-900/20 dark:to-slate-900",
    sectionBorder: "border-emerald-500",
    tocBg: "bg-emerald-50/80 dark:bg-emerald-900/20",
    tocBorder: "border-emerald-200 dark:border-emerald-700",
    sectionNumberBg: "bg-emerald-100 text-emerald-700",
  },
  full_detailed: {
    label: "Full Detailed Report",
    headerBg: "bg-gradient-to-r from-blue-900 via-blue-700 to-cyan-600",
    accentBg: "bg-blue-600",
    accentText: "text-blue-700",
    priceBadge: "bg-blue-500",
    price: "$150 AUD",
    borderColor: "border-blue-300 dark:border-blue-700",
    lightBg: "from-blue-50 via-white to-cyan-50 dark:from-blue-900/20 dark:to-slate-900",
    sectionBorder: "border-blue-500",
    tocBg: "bg-blue-50/80 dark:bg-blue-900/20",
    tocBorder: "border-blue-200 dark:border-blue-700",
    sectionNumberBg: "bg-blue-100 text-blue-700",
  },
  extensive_log: {
    label: "Extensive Log Report",
    headerBg: "bg-gradient-to-r from-fuchsia-900 via-purple-800 to-indigo-700",
    accentBg: "bg-purple-600",
    accentText: "text-purple-700",
    priceBadge: "bg-purple-500",
    price: "$200 AUD",
    borderColor: "border-purple-300 dark:border-purple-700",
    lightBg: "from-purple-50 via-white to-indigo-50 dark:from-purple-900/20 dark:to-slate-900",
    sectionBorder: "border-purple-500",
    tocBg: "bg-purple-50/80 dark:bg-purple-900/20",
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
  const [hasAllReports, setHasAllReports] = useState(false);

  useEffect(() => {
    fetchData();
  }, [caseId, reportId]);

  const fetchData = async () => {
    try {
      const [reportRes, caseRes, groundsRes, reportsRes] = await Promise.all([
        axios.get(`${API}/cases/${caseId}/reports/${reportId}`),
        axios.get(`${API}/cases/${caseId}`),
        axios.get(`${API}/cases/${caseId}/grounds`),
        axios.get(`${API}/cases/${caseId}/reports`),
      ]);
      setReport(reportRes.data);
      setCaseData(caseRes.data);
      setGrounds(groundsRes.data?.grounds || []);
      const requiredTypes = ["quick_summary", "full_detailed", "extensive_log"];
      const hasAll = requiredTypes.every((type) =>
        (reportsRes.data || []).some((item) => item.report_type === type && item.status === "completed")
      );
      setHasAllReports(hasAll);
    } catch (error) {
      toast.error("Failed to load report");
      navigate(`/cases/${caseId}`);
    } finally {
      setLoading(false);
    }
  };

  const handlePrint = () => {
    openReportPreview("print");
  };

  const iosShareOrDownload = async (blob, filename, mimeType) => {
    const isIOS = /iPad|iPhone|iPod/.test(navigator.userAgent);
    if (isIOS && navigator.share) {
      try {
        const file = new File([blob], filename, { type: mimeType });
        if (navigator.canShare && navigator.canShare({ files: [file] })) {
          await navigator.share({ title: filename, files: [file] });
          toast.success("Shared successfully!");
          return;
        }
      } catch (shareErr) {
        if (shareErr.name === 'AbortError') return;
        console.warn("Share API failed, falling back:", shareErr);
      }
    }
    if (isIOS) {
      const url = window.URL.createObjectURL(blob);
      window.location.href = url;
      toast.success("File opened — use the Share button to save.");
      setTimeout(() => window.URL.revokeObjectURL(url), 30000);
    } else {
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement("a");
      link.href = url;
      link.setAttribute("download", filename);
      document.body.appendChild(link);
      link.click();
      link.remove();
      toast.success("Downloaded successfully!");
      setTimeout(() => window.URL.revokeObjectURL(url), 10000);
    }
  };

  const buildAuthUrl = (baseUrl) => {
    const token = localStorage.getItem("session_token");
    if (!token) return baseUrl;
    const separator = baseUrl.includes("?") ? "&" : "?";
    return `${baseUrl}${separator}session_token=${token}`;
  };

  const openReportPreview = (mode = "print") => {
    const contentEl = document.querySelector('[data-testid="report-content"]');
    if (!contentEl) {
      toast.error("Unable to open report preview.");
      return;
    }
    const title = report?.title || `${caseData?.title || "Case"} Report`;
    const meta = `${caseData?.court || "Court"} — ${(caseData?.state || "NSW").toUpperCase()}`;
    const notice = mode === "pdf"
      ? '<div class="notice">PDF preview — use Print / Save as PDF to download.</div>'
      : '';

    const html = `<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>${title}</title>
  <style>
    body { font-family: 'Manrope', 'Arial', sans-serif; padding: 28px; color: #0f172a; line-height: 1.7; }
    h1 { font-family: 'Crimson Pro', serif; font-size: 24px; margin-bottom: 6px; color: #0f172a; }
    h2 { font-family: 'Crimson Pro', serif; font-size: 18px; margin-top: 18px; border-bottom: 2px solid #1d4ed8; padding-bottom: 4px; color: #1e3a8a; }
    h3 { font-size: 15px; margin-top: 14px; color: #1e40af; }
    .meta { font-size: 12px; color: #475569; margin-bottom: 12px; }
    .notice { background: #eff6ff; border: 1px solid #93c5fd; padding: 8px 12px; border-radius: 8px; color: #1e3a8a; margin-bottom: 16px; }
    table { border-collapse: collapse; width: 100%; margin: 12px 0; }
    td, th { border: 1px solid #cbd5e1; padding: 6px 10px; text-align: left; font-size: 12px; color: #0f172a; }
    th { background: #dbeafe; font-weight: 700; }
    ul, ol { padding-left: 18px; }
    li { margin-bottom: 4px; }
    button, .no-print { display: none !important; }
    @media print { body { print-color-adjust: exact; -webkit-print-color-adjust: exact; } }
  </style>
</head>
<body>
  ${notice}
  <h1>${title}</h1>
  <div class="meta">${meta}</div>
  <hr />
  ${contentEl.innerHTML}
</body>
</html>`;

    const previewWindow = window.open("", "_blank", "width=1200,height=800");
    if (!previewWindow) {
      const blob = new Blob([html], { type: "text/html" });
      const url = window.URL.createObjectURL(blob);
      window.location.href = url;
      toast.success("Preview opened — use Print / Save as PDF to download.");
      return;
    }

    previewWindow.document.open();
    previewWindow.document.write(html);
    previewWindow.document.close();
    previewWindow.focus();

    if (mode === "print") {
      setTimeout(() => previewWindow.print(), 700);
      toast.success("Print dialogue opening...");
      return;
    }
    toast.success("PDF preview opened — use Print / Save as PDF to download.");
  };

  const handleExportPDF = async () => {
    try {
      const isIOS = /iPad|iPhone|iPod/.test(navigator.userAgent);
      if (isIOS) {
        const url = buildAuthUrl(`${API}/cases/${caseId}/reports/${reportId}/export-pdf`);
        window.open(url, "_blank", "noopener,noreferrer");
        toast.success("PDF opened — use Share to save or print.");
        return;
      }
      toast.info("Generating PDF...");
      const response = await axios.get(`${API}/cases/${caseId}/reports/${reportId}/export-pdf`, { responseType: "blob", timeout: 60000 });
      const blob = new Blob([response.data], { type: "application/pdf" });
      const filename = `${caseData?.title || "Report"}_${report?.report_type || "report"}.pdf`;
      await iosShareOrDownload(blob, filename, "application/pdf");
    } catch (error) {
      console.error("PDF export error:", error);
      toast.error("Failed to export PDF. Please try again.");
    }
  };

  const handleExportDOCX = async () => {
    try {
      const isIOS = /iPad|iPhone|iPod/.test(navigator.userAgent);
      if (isIOS) {
        const url = buildAuthUrl(`${API}/cases/${caseId}/reports/${reportId}/export-docx`);
        window.open(url, "_blank", "noopener,noreferrer");
        toast.success("Word document opened — use Share to save.");
        return;
      }
      toast.info("Generating Word document...");
      const response = await axios.get(`${API}/cases/${caseId}/reports/${reportId}/export-docx`, { responseType: "blob", timeout: 60000 });
      const blob = new Blob([response.data], { type: "application/vnd.openxmlformats-officedocument.wordprocessingml.document" });
      const filename = `${caseData?.title || "Report"}_${report?.report_type || "report"}.docx`;
      await iosShareOrDownload(blob, filename, "application/vnd.openxmlformats-officedocument.wordprocessingml.document");
    } catch (error) {
      console.error("DOCX export error:", error);
      toast.error("Failed to export Word document. Please try again.");
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
  const sentenceSummary = extractSentenceSummary(caseData, analysisText);
  const defendantName = caseData?.defendant_name || report?.content?.defendant || extractDefendantFromAnalysis(analysisText);
  const offenceLabel = caseData?.offence_type || titleFromSnake(caseData?.offence_category) || extractOffenceFromAnalysis(analysisText);
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
    <div className="min-h-screen bg-slate-950">
      {/* Sticky action bar */}
      <header className="bg-slate-950/95 backdrop-blur border-b border-slate-800 sticky top-0 z-40 no-print" data-testid="report-header">
        <div className="max-w-5xl mx-auto px-4 sm:px-6 py-3">
          <div className="flex items-center justify-between gap-3 flex-wrap text-slate-100">
            <Button variant="ghost" size="sm" onClick={() => navigate(`/cases/${caseId}`)} className="text-slate-200 hover:text-white hover:bg-slate-800" data-testid="back-btn">
              <ArrowLeft className="w-4 h-4 mr-1" /> Back to Case
            </Button>
            <div className="flex items-center gap-2 flex-wrap">
              {report?.report_type === 'extensive_log' && (
                hasAllReports ? (
                  <Button variant="outline" size="sm" onClick={() => navigate(`/cases/${caseId}/reports/${reportId}/barrister`)} data-testid="barrister-view-btn">
                    <Eye className="w-4 h-4 mr-2" /> Barrister View
                  </Button>
                ) : (
                  <Button variant="outline" size="sm" disabled className="text-slate-500 border-slate-700 cursor-not-allowed" data-testid="barrister-view-locked">
                    <Eye className="w-4 h-4 mr-2" /> Barrister View — unlock after all 3 reports
                  </Button>
                )
              )}
              <Button variant="outline" size="sm" onClick={handlePrint} className="border-slate-700 text-slate-200 hover:bg-slate-800" data-testid="print-btn">
                <Printer className="w-4 h-4 mr-2" /> Print
              </Button>
              <Button variant="outline" size="sm" onClick={handleExportDOCX} className="bg-blue-600/20 text-blue-200 border-blue-500/40 hover:bg-blue-600/30" data-testid="export-docx-btn">
                <FileText className="w-4 h-4 mr-2" /> Export Word
              </Button>
              <Button size="sm" onClick={handleExportPDF} className="bg-blue-600 text-white hover:bg-blue-500" data-testid="export-pdf-btn">
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
                <h1 className="text-3xl sm:text-4xl font-bold text-slate-100" style={{ fontFamily: "Crimson Pro, serif" }} data-testid="report-title">
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
          <div className="bg-slate-900 border-b border-slate-700 p-5 sm:p-6" data-testid="report-top-summary-box">
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-6 gap-4 text-base" style={{ fontFamily: "Crimson Pro, serif" }}>
              <div className="lg:col-span-1">
                <p className="text-xs text-slate-400 uppercase tracking-wide mb-1">Defendant</p>
                <p className="font-semibold text-slate-100" data-testid="report-summary-accused">{defendantName}</p>
              </div>
              <div className="lg:col-span-1">
                <p className="text-xs text-slate-400 uppercase tracking-wide mb-1">Offence</p>
                <p className="font-semibold text-slate-100" data-testid="report-summary-offence">{offenceLabel}</p>
              </div>
              <div className="sm:col-span-2 lg:col-span-2">
                <p className="text-xs text-slate-400 uppercase tracking-wide mb-1">Sentence</p>
                <p className="font-semibold text-slate-100" data-testid="report-summary-sentence">{sentenceSummary}</p>
              </div>
              <div className="lg:col-span-1">
                <p className="text-xs text-slate-400 uppercase tracking-wide mb-1">Documents</p>
                <p className="font-semibold text-slate-100">{documentsCount} files analysed</p>
              </div>
              <div className="lg:col-span-1">
                <p className="text-xs text-slate-400 uppercase tracking-wide mb-1">Timeline Events</p>
                <p className="font-semibold text-slate-100">{eventsCount} events</p>
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
                      className="text-2xl font-bold text-slate-100 uppercase tracking-wide"
                      style={{ fontFamily: "Crimson Pro, serif" }}
                      data-testid={`report-section-heading-${idx + 1}`}
                    >
                      {section.title}
                    </h3>
                  </div>
                </div>

                {/* Section content with professional markdown rendering */}
                <div className="bg-slate-900 rounded-lg border border-slate-700 p-6 sm:p-7 shadow-md" data-testid={`report-section-content-${idx + 1}`}>
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
        .legal-report {
          font-size: 1.05rem;
          line-height: 1.8;
          color: #0f172a;
        }
        .legal-report h1,
        .legal-report h2,
        .legal-report h3 {
          font-family: 'Crimson Pro', serif;
          font-weight: 700;
          color: #f8fafc;
          margin: 1.4rem 0 0.7rem;
        }
        .legal-report h2 { font-size: 1.25rem; }
        .legal-report h3 { font-size: 1.1rem; }
        .legal-report strong { color: #f8fafc; font-weight: 700; }
        .legal-report ul, .legal-report ol { padding-left: 1.2rem; margin: 0.6rem 0; }
        .legal-report li { margin-bottom: 0.4rem; }
        .legal-report-table-wrap { overflow-x: auto; }
        .legal-report table {
          width: 100%;
          min-width: 720px;
          border-collapse: collapse;
          margin: 0.8rem 0;
          background: #0b1220;
        }
        .legal-report th {
          background: #1e293b;
          color: #e2e8f0 !important;
          font-weight: 700;
        }
        .legal-report th, .legal-report td {
          border: 1px solid #334155;
          padding: 10px 12px;
          font-size: 0.95rem;
          vertical-align: top;
          color: #e2e8f0;
        }
        .legal-report blockquote {
          border-left: 4px solid #38bdf8;
          padding: 10px 14px;
          margin: 0.8rem 0;
          background: #1e293b;
          color: #e2e8f0;
        }
        @media print {
          body {
            print-color-adjust: exact;
            -webkit-print-color-adjust: exact;
          }
          .no-print { display: none !important; }
          .legal-report { font-size: 12px; color: #0f172a; }
          .legal-report h1,
          .legal-report h2,
          .legal-report h3,
          .legal-report strong { color: #0f172a; }
          .legal-report table { background: #ffffff; }
          .legal-report th { background: #dbeafe; color: #0f172a !important; }
          .legal-report th, .legal-report td { color: #0f172a; border-color: #cbd5e1; }
          .legal-report blockquote { background: #eff6ff; color: #1e3a8a; }
        }
      `}</style>
    </div>
  );
};

export default ReportView;
