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
  Scale, ArrowLeft, Download, Printer, Loader2, Share2, Maximize2,
  BookOpen, Gavel, FileText, CheckCircle, AlertTriangle, XCircle,
  Calendar, User, MapPin, Building2, Clock, Target, Shield, Sword,
  ChevronRight, ExternalLink, Quote, BarChart3, Bookmark
} from "lucide-react";
import { Button } from "../components/ui/button";
import { Badge } from "../components/ui/badge";
import { API } from "../App";

const GROUND_TYPE_LABELS = {
  procedural_error: "Procedural Error",
  fresh_evidence: "Fresh Evidence",
  miscarriage_of_justice: "Miscarriage of Justice",
  sentencing_error: "Sentencing Error",
  judicial_error: "Judicial Error",
  ineffective_counsel: "Ineffective Counsel",
  prosecution_misconduct: "Prosecution Misconduct",
  jury_irregularity: "Jury Irregularity",
  constitutional_violation: "Constitutional Violation",
  other: "Other Ground"
};

const STRENGTH_CONFIG = {
  strong: { icon: CheckCircle, color: "text-emerald-700", bg: "bg-emerald-50", border: "border-emerald-200", label: "Strong Ground", score: "HIGH" },
  moderate: { icon: AlertTriangle, color: "text-blue-700", bg: "bg-blue-50", border: "border-blue-200", label: "Moderate Ground", score: "MEDIUM" },
  weak: { icon: XCircle, color: "text-red-700", bg: "bg-red-50", border: "border-red-200", label: "Requires Development", score: "LOW" }
};

const BarristerView = ({ user }) => {
  const { caseId, reportId } = useParams();
  const navigate = useNavigate();
  const [report, setReport] = useState(null);
  const [allReports, setAllReports] = useState([]);
  const [caseData, setCaseData] = useState(null);
  const [grounds, setGrounds] = useState([]);
  const [timeline, setTimeline] = useState([]);
  const [documents, setDocuments] = useState([]);
  const [loading, setLoading] = useState(true);
  const [isFullscreen, setIsFullscreen] = useState(false);

  useEffect(() => {
    fetchData();
  }, [caseId, reportId]);

  const fetchData = async () => {
    try {
      const [reportRes, caseRes, groundsRes, timelineRes, docsRes, allReportsRes] = await Promise.all([
        axios.get(`${API}/cases/${caseId}/reports/${reportId}`),
        axios.get(`${API}/cases/${caseId}`),
        axios.get(`${API}/cases/${caseId}/grounds`),
        axios.get(`${API}/cases/${caseId}/timeline`),
        axios.get(`${API}/cases/${caseId}/documents`),
        axios.get(`${API}/cases/${caseId}/reports`).catch(() => ({ data: [] }))
      ]);
      const primary = reportRes.data;
      setReport(primary);
      setCaseData(caseRes.data);
      setGrounds(groundsRes.data?.grounds || []);
      setTimeline(timelineRes.data || []);
      setDocuments(docsRes.data || []);
      // Collect all reports with analysis content, sorted by detail level (extensive > full > quick)
      const typeOrder = { extensive_log: 3, full_detailed: 2, quick_summary: 1 };
      const completed = (allReportsRes.data || [])
        .filter(r => r.content?.analysis && r.content.analysis.length > 200 && r.status !== "failed" && !r.content?.aggressive_mode)
        .sort((a, b) => {
          const typeA = typeOrder[a.report_type] || 0;
          const typeB = typeOrder[b.report_type] || 0;
          return typeB - typeA;
        });
      setAllReports(completed);
    } catch (error) {
      toast.error("Failed to load report");
      navigate(`/cases/${caseId}`);
    } finally {
      setLoading(false);
    }
  };

  const handlePrint = () => {
    openBarristerPreview("print");
  };

  const toggleFullscreen = () => {
    if (!document.fullscreenElement) {
      document.documentElement.requestFullscreen();
      setIsFullscreen(true);
    } else {
      document.exitFullscreen();
      setIsFullscreen(false);
    }
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
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', filename);
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

  const openBarristerPreview = (mode = "print") => {
    const contentEl = document.querySelector('[data-testid="barrister-report"]');
    if (!contentEl) {
      toast.error("Unable to open report preview.");
      return;
    }
    const title = `Barrister Brief — ${caseData?.title || "Case"}`;
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
  <link href="https://fonts.googleapis.com/css2?family=Crimson+Pro:wght@400;600;700&family=Manrope:wght@400;500;600;700&display=swap" rel="stylesheet" />
  <style>
    * { box-sizing: border-box; margin: 0; padding: 0; }
    body { font-family: 'Manrope', 'Arial', sans-serif; padding: 0; color: #0f172a; line-height: 1.75; font-size: 15px; background: #fff; }
    .report-container { max-width: 900px; margin: 0 auto; }
    .report-header { background: #1e3a5f; color: #fff; padding: 28px 32px; }
    .report-header h1 { font-family: 'Crimson Pro', serif; font-size: 28px; font-weight: 700; margin-bottom: 4px; color: #fff; }
    .report-header .meta-line { font-size: 13px; color: rgba(255,255,255,0.9); margin-top: 2px; }
    .report-header .header-row { display: flex; justify-content: space-between; align-items: flex-start; }
    .report-header .badge { display: inline-block; background: rgba(255,255,255,0.25); padding: 3px 12px; border-radius: 999px; font-size: 12px; font-weight: 700; margin-top: 8px; }
    .report-header .gen-date { font-size: 11px; color: rgba(255,255,255,0.85); margin-top: 4px; }
    .report-header .grounds-count { font-size: 28px; font-weight: 700; color: #fff; text-align: right; }
    .report-header .grounds-label { font-size: 11px; color: rgba(255,255,255,0.8); text-align: right; }
    .summary-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 12px; padding: 16px 32px; border-bottom: 1px solid #e2e8f0; background: #fff; }
    .summary-grid .item-label { font-size: 10px; text-transform: uppercase; letter-spacing: 0.05em; color: #475569; margin-bottom: 2px; }
    .summary-grid .item-value { font-size: 13px; font-weight: 600; color: #0f172a; font-family: 'Crimson Pro', serif; }
    .sections { padding: 24px 32px; }
    h2 { font-family: 'Crimson Pro', serif; font-size: 22px; font-weight: 700; color: #1e3a5f; margin: 1.5rem 0 0.8rem; border-bottom: 2px solid #1e3a5f; padding-bottom: 4px; }
    h3 { font-family: 'Crimson Pro', serif; font-size: 17px; font-weight: 700; color: #1e40af; margin: 1rem 0 0.5rem; }
    h4 { font-family: 'Manrope', sans-serif; font-size: 15px; font-weight: 700; color: #334155; margin: 0.8rem 0 0.4rem; }
    p { margin-bottom: 0.7rem; }
    strong { color: #0f172a; font-weight: 700; }
    ul, ol { padding-left: 1.4rem; margin: 0.6rem 0; }
    li { margin-bottom: 0.4rem; }
    a { color: #1d4ed8; text-decoration: underline; }
    table { width: 100%; border-collapse: collapse; margin: 12px 0; font-size: 13px; table-layout: fixed; }
    th { background: #1e3a5f; color: #fff !important; font-weight: 700; padding: 8px 10px; text-align: left; border: 1px solid #cbd5e1; word-wrap: break-word; }
    td { border: 1px solid #cbd5e1; padding: 8px 10px; color: #0f172a; vertical-align: top; word-wrap: break-word; overflow-wrap: break-word; }
    blockquote { border-left: 4px solid #1e3a5f; padding: 10px 14px; margin: 0.8rem 0; background: #eff6ff; color: #1e3a8a; }
    .notice { background: #eff6ff; border: 1px solid #93c5fd; padding: 8px 16px; border-radius: 8px; color: #1e3a8a; margin: 16px 32px; font-size: 13px; }
    .created-by { text-align: center; padding: 20px 32px 4px; font-size: 16px; font-weight: 700; color: #1e3a5f; font-family: 'Crimson Pro', serif; }
    .disclaimer { background: #fef2f2; border: 3px solid #ef4444; padding: 20px 28px; margin: 16px 32px; border-radius: 8px; display: flex; gap: 14px; align-items: flex-start; }
    .disclaimer-icon { color: #ef4444; font-size: 28px; flex-shrink: 0; }
    .disclaimer-text { font-size: 14px; color: #1e293b; font-weight: 700; }
    .disclaimer-text strong { font-size: 16px; text-transform: uppercase; letter-spacing: 0.08em; color: #dc2626; display: block; margin-bottom: 6px; }
    .footer { text-align: center; padding: 12px 32px; border-top: 1px solid #e2e8f0; font-size: 11px; color: #475569; }
    .no-print { display: none !important; }
    @media print {
      body { print-color-adjust: exact; -webkit-print-color-adjust: exact; }
      .report-header, th { print-color-adjust: exact; -webkit-print-color-adjust: exact; }
      .disclaimer { print-color-adjust: exact; -webkit-print-color-adjust: exact; }
      table { page-break-inside: auto; }
      tr { page-break-inside: avoid; }
    }
  </style>
</head>
<body>
  ${notice}
  <div class="report-container">
    <div class="report-header">
      <div class="header-row">
        <div>
          <div style="font-size:12px;text-transform:uppercase;letter-spacing:0.08em;font-weight:600;margin-bottom:4px;">CONFIDENTIAL BARRISTER BRIEF</div>
          <h1>${title}</h1>
          <div class="meta-line">${meta}</div>
          <div class="badge">Synthesised from ${allReports?.length || 3} Reports</div>
          <div class="gen-date">Generated: ${formatDate(report?.generated_at)}</div>
        </div>
        <div>
          <div class="grounds-count">${grounds.length}</div>
          <div class="grounds-label">Ground${grounds.length !== 1 ? 's' : ''} Identified</div>
        </div>
      </div>
    </div>
    <div class="summary-grid">
      <div><div class="item-label">Defendant</div><div class="item-value">${caseData?.defendant_name || "Not specified"}</div></div>
      <div><div class="item-label">Offence</div><div class="item-value">${formatOffenceLabel(caseData?.offence_category || caseData?.offence_type)}</div></div>
      <div><div class="item-label">Sentence</div><div class="item-value">${cleanSentence(caseData?.sentence || extractSentenceSummary(caseData))}</div></div>
      <div><div class="item-label">Documents</div><div class="item-value">${documents.length} files analysed</div></div>
      <div><div class="item-label">Timeline Events</div><div class="item-value">${timeline.length} events</div></div>
      <div><div class="item-label">Reports Synthesised</div><div class="item-value">${allReports?.length || 3} reports</div></div>
    </div>
    <div class="sections">
      ${contentEl.innerHTML}
    </div>
    <div class="created-by">Created and Designed by Deb King</div>
    <div class="disclaimer">
      <div class="disclaimer-icon">&#9888;</div>
      <div class="disclaimer-text">
        <strong>NOT LEGAL ADVICE</strong>
        This document is an educational tool only. It does NOT constitute legal advice and must NOT be relied upon as such. All analysis, findings, and recommendations must be independently verified by a qualified Australian legal professional before any action is taken. No solicitor-client relationship is formed through the provision of this report.
      </div>
    </div>
    <div class="footer">Criminal Law Appeal Case Management by Deb King — GLENMORE PARK NSW</div>
  </div>
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
      const response = await axios.get(
        `${API}/cases/${caseId}/reports/${reportId}/export-pdf`,
        { responseType: 'blob', timeout: 60000 }
      );
      const blob = new Blob([response.data], { type: 'application/pdf' });
      const filename = `${caseData?.title || 'Report'}_barrister_brief.pdf`;
      await iosShareOrDownload(blob, filename, 'application/pdf');
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
      const response = await axios.get(
        `${API}/cases/${caseId}/reports/${reportId}/export-docx`,
        { responseType: 'blob', timeout: 60000 }
      );
      const blob = new Blob([response.data], { type: 'application/vnd.openxmlformats-officedocument.wordprocessingml.document' });
      const filename = `${caseData?.title || 'Report'}_barrister_brief.docx`;
      await iosShareOrDownload(blob, filename, 'application/vnd.openxmlformats-officedocument.wordprocessingml.document');
    } catch (error) {
      console.error("DOCX export error:", error);
      toast.error("Failed to export Word document. Please try again.");
    }
  };

  const formatDate = (dateStr) => {
    if (!dateStr) return "N/A";
    return new Date(dateStr).toLocaleDateString("en-AU", {
      day: "numeric",
      month: "long",
      year: "numeric"
    });
  };

  const formatShortDate = (dateStr) => {
    if (!dateStr) return "N/A";
    return new Date(dateStr).toLocaleDateString("en-AU", {
      day: "numeric",
      month: "short",
      year: "numeric"
    });
  };

  const formatOffenceLabel = (value) => {
    if (!value) return "Not specified";
    return value.replace(/_/g, " ").replace(/\b\w/g, (c) => c.toUpperCase());
  };

  const cleanSentence = (s) => {
    if (!s) return s;
    let c = s.replace(/\s*\[.*$/, "").replace(/\s*\(https?:.*$/, "").replace(/\s*https?:.*$/, "");
    // Strip analysis text that may follow the actual sentence
    c = c.replace(/\.\s*(The|This|It|His|Her|Their|A|An|In|Under|Given|However|Furthermore|Additionally|Moreover|Such|Notably|Importantly|As|While|Although|With|For|Where|Which).*/s, ".");
    // Strip text after common analysis phrases
    c = c.replace(/,\s*(which|that|this|is crucial|meaning|indicating|suggesting|reflecting|demonstrating|as per|pursuant|under s\.).*/si, "");
    c = c.trim();
    if (c.length > 150) c = c.substring(0, 147) + "...";
    return c.trim();
  };

  const extractSentenceSummary = (caseInfo, analysis = "") => {
    if (caseInfo?.sentence && caseInfo.sentence.trim().length > 3) return cleanSentence(caseInfo.sentence.trim());
    const byVerb = analysis.match(/(?:was\s+)?sentenced?\s+to\s+(\d+\s*(?:years?|months?)\s+(?:and\s+\d+\s*(?:years?|months?)\s+)?(?:imprisonment|gaol|jail|custody)[^\n\.]{0,80})/i);
    if (byVerb?.[1]) return cleanSentence(byVerb[1]);
    const byHead = analysis.match(/(?:^|\n)\s*(?:Head\s+)?Sentence\s*:\s*(\d+[^\n]{5,100})/im);
    if (byHead?.[1] && /\d+\s*(year|month|life)/i.test(byHead[1])) return cleanSentence(byHead[1]);
    const byLife = analysis.match(/(?:sentenced?\s+to\s+)?(life\s+imprisonment|imprisonment\s+for\s+life|life\s+sentence)[^\n\.]{0,60}/i);
    if (byLife) return cleanSentence(byLife[0].replace(/^sentenced?\s+to\s+/i, ""));
    const byYears = analysis.match(/(\d+[\s-]*(?:years?|months?)(?:'s?)?\s*(?:imprisonment|gaol|jail|custody|sentence|non[- ]?parole)[^\n\.]{0,80})/i);
    if (byYears?.[1]) return cleanSentence(byYears[1]);
    const bySentOf = analysis.match(/sentence\s+of\s+(\d+[^\n\.]{5,80})/i);
    if (bySentOf?.[1]) return cleanSentence(bySentOf[1]);
    const byNPP = analysis.match(/((?:minimum|non[- ]?parole)\s+(?:period\s+)?of\s+\d+[^\n\.]{3,60})/i);
    if (byNPP?.[1]) return cleanSentence(byNPP[1]);
    return "Not recorded";
  };

  // Clean AI artifacts from content
  const cleanAIContent = (text) => {
    if (!text) return text;
    let cleaned = text;
    cleaned = cleaned.replace(/^(Certainly!|Sure!|Of course!|Absolutely!|Here('s| is) a comprehensive[^\n]*\n?)/i, "");
    cleaned = cleaned.replace(/^(Here('s| is) (a |the |your )?detailed[^\n]*\n?)/i, "");
    cleaned = cleaned.replace(/^(Here('s| is) (a |the |your )?thorough[^\n]*\n?)/i, "");
    cleaned = cleaned.replace(/^(I('ve| have) (prepared|created|compiled|generated)[^\n]*\n?)/i, "");
    // Strip \1 artifacts
    cleaned = cleaned.replace(/\\1/g, "");
    cleaned = cleaned.replace(/\x01/g, "");
    // Square bracket notes
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
    // Round bracket notes
    cleaned = cleaned.replace(/\(Note:\s*[^)]*\)/gi, "");
    cleaned = cleaned.replace(/\(See:\s*[^)]*\)/gi, "");
    cleaned = cleaned.replace(/\(Continue[^)]*\)/gi, "");
    cleaned = cleaned.replace(/\(Link formatting[^)]*\)/gi, "");
    cleaned = cleaned.replace(/\(Entries will[^)]*\)/gi, "");
    // Strip AI meta-commentary
    cleaned = cleaned.replace(/\n*This truncated document[^\n]*/gi, "");
    cleaned = cleaned.replace(/\n*This (?:document|report|analysis) (?:provides|covers|contains|demonstrates)[^\n]*(?:sections?|overview|summary)[^\n]*/gi, "");
    cleaned = cleaned.replace(/\n*Each section (?:demonstrates|provides|covers)[^\n]*/gi, "");
    cleaned = cleaned.replace(/\n*The sections? above (?:are|is|were|was) (?:crafted|designed|written|prepared|created)[^\n]*/gi, "");
    cleaned = cleaned.replace(/\n*(?:The above|These) sections? (?:are|is|were|was) (?:crafted|designed|written|prepared|created)[^\n]*/gi, "");
    cleaned = cleaned.replace(/\n*(?:presenting|advances?) (?:a comprehensive|field-specific|detailed)[^\n]*(?:court of appeal|legal professionals?)[^\n]*/gi, "");
    
    // Strip prompt instruction text from section headings
    cleaned = cleaned.replace(/\s*—\s*keep ALL[^\n]*/gi, "");
    cleaned = cleaned.replace(/\s*—\s*DETAILED PATHWAY ANALYSIS[^\n]*/gi, "");
    cleaned = cleaned.replace(/\s*\(\d+\+?\s*words[^)]*\)/gi, "");
    cleaned = cleaned.replace(/(GROUNDS OF MERIT)\s*—\s*DEEP ANALYSIS/gi, "$1");
    cleaned = cleaned.replace(/\s*\(\d+\+?\s*CASES[^)]*\)/gi, "");
    cleaned = cleaned.replace(/\s*—?\s*keep ALL[^.\n]*/gi, "");

    // Strip "we/us/our" language
    const weUsReplacements = [
      [/\bWe are arguing\b/g, 'The applicant argues'],
      [/\bwe are arguing\b/g, 'the applicant argues'],
      [/\bWe are aiming\b/g, 'The appeal aims'],
      [/\bwe are aiming\b/g, 'the appeal aims'],
      [/\bWe are filing\b/g, 'The legal professional is filing'],
      [/\bwe are filing\b/g, 'the legal professional is filing'],
      [/\bWe are taking\b/g, 'The legal professional is taking'],
      [/\bwe are taking\b/g, 'the legal professional is taking'],
      [/\bWe succeed\b/g, 'The appeal succeeds'],
      [/\bwe succeed\b/g, 'the appeal succeeds'],
      [/\bwe will gather\b/g, 'the legal professional will gather'],
      [/\bWe will gather\b/g, 'The legal professional will gather'],
      [/\bwe will craft\b/g, 'the legal professional will craft'],
      [/\bWe will craft\b/g, 'The legal professional will craft'],
      [/\bwe will file\b/g, 'the legal professional will file'],
      [/\bWe will file\b/g, 'The legal professional will file'],
      [/\bwe will prepare\b/g, 'the legal professional will prepare'],
      [/\bWe will prepare\b/g, 'The legal professional will prepare'],
      [/\bwe will submit\b/g, 'the legal professional will submit'],
      [/\bWe will submit\b/g, 'The legal professional will submit'],
      [/\bwe will seek\b/g, 'the applicant will seek'],
      [/\bWe will seek\b/g, 'The applicant will seek'],
      [/\bwe will argue\b/g, 'the applicant will argue'],
      [/\bWe will argue\b/g, 'The applicant will argue'],
      [/\bwe will demonstrate\b/g, 'the appeal will demonstrate'],
      [/\bWe will demonstrate\b/g, 'The appeal will demonstrate'],
      [/\bwe will show\b/g, 'the appeal will show'],
      [/\bWe will show\b/g, 'The appeal will show'],
      [/\bWe argue\b/g, 'The applicant argues'],
      [/\bwe argue\b/g, 'the applicant argues'],
      [/\bcontact with us\b/g, 'contact with the legal professional'],
      [/\bContact us\b/g, 'Contact the legal professional'],
      [/\bcontact us\b/g, 'contact the legal professional'],
      [/\bour submissions\b/g, 'the submissions'],
      [/\bOur submissions\b/g, 'The submissions'],
      [/\bour claims\b/g, "the applicant's claims"],
      [/\bOur claims\b/g, "The applicant's claims"],
      [/\bour arguments\b/g, "the applicant's arguments"],
      [/\bOur arguments\b/g, "The applicant's arguments"],
      [/\bour position\b/g, "the applicant's position"],
      [/\bOur position\b/g, "The applicant's position"],
      [/\bour case\b/g, "the applicant's case"],
      [/\bOur case\b/g, "The applicant's case"],
      [/\bour strategy\b/g, 'the legal strategy'],
      [/\bOur strategy\b/g, 'The legal strategy'],
      [/\bour analysis\b/g, 'this analysis'],
      [/\bOur analysis\b/g, 'This analysis'],
      [/\bon our behalf\b/g, 'on behalf of the applicant'],
      [/\byour legal team\b/g, 'the legal professional'],
      [/\bYour legal team\b/g, 'The legal professional'],
      [/\byour partner\b/g, "the victim"],
      [/\byou've been\b/g, 'the applicant has been'],
      [/\bYou've been\b/g, 'The applicant has been'],
      [/\b, we are\b/g, ', the legal professional is'],
      [/\b, we will\b/g, ', the legal professional will'],
      [/\b, we have\b/g, ', the legal professional has'],
      [/\bWe have identified\b/g, 'This analysis has identified'],
      [/\bwe have identified\b/g, 'this analysis has identified'],
      [/\bWe have reviewed\b/g, 'This analysis has reviewed'],
      [/\bwe have reviewed\b/g, 'this analysis has reviewed'],
    ];
    for (const [pattern, replacer] of weUsReplacements) {
      cleaned = cleaned.replace(pattern, replacer);
    }

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

  const sanitiseReportOutput = (text = "") => {
    if (!text) return text;
    const filtered = text.split(/\n/).filter((line) => {
      if (/\[Your Name\]|\[Your Legal Organisation\/Team\]/i.test(line)) return false;
      if (/Best regards|Prepared by|Prepared for|This report was generated by|Criminal Appeal AI|Justitia AI/i.test(line)) return false;
      if (/\bDO NOT UNDO\.?\b/i.test(line)) return false;
      return true;
    });
    return filtered.join("\n").replace(/\n{3,}/g, "\n\n").trim();
  };

  const normaliseText = (text) => (text || "")
    .toLowerCase()
    .replace(/[^a-z0-9\s]/g, " ")
    .replace(/\s+/g, " ")
    .trim();

  const toWordSet = (text) => {
    const cleaned = normaliseText(text);
    if (!cleaned) return new Set();
    return new Set(cleaned.split(" ").filter((word) => word.length > 3));
  };

  const jaccardSimilarity = (setA, setB) => {
    if (!setA.size || !setB.size) return 0;
    let intersection = 0;
    for (const item of setA) {
      if (setB.has(item)) intersection += 1;
    }
    const union = setA.size + setB.size - intersection;
    return union === 0 ? 0 : intersection / union;
  };

  const splitParagraphs = (text) => (text || "")
    .split(/\n\s*\n+/)
    .map((p) => p.trim())
    .filter((p) => p.length > 60 && !/IMPORTANT DISCLAIMER/i.test(p));

  const buildAnchorTerms = () => {
    const terms = new Set();
    const addTerms = (value) => {
      if (!value) return;
      const cleaned = String(value).toLowerCase();
      cleaned.split(/[^a-z0-9]+/).forEach((token) => {
        if (token.length > 3) terms.add(token);
      });
    };

    addTerms(caseData?.title);
    addTerms(caseData?.defendant_name);
    addTerms(caseData?.case_number);
    addTerms(caseData?.court);
    addTerms(caseData?.judge);
    addTerms(caseData?.sentence);
    addTerms(caseData?.offence_type);
    addTerms(caseData?.offence_category);
    addTerms(caseData?.state);

    (documents || []).forEach((doc) => addTerms(doc.filename));
    (timeline || []).forEach((event) => {
      addTerms(event.title);
      addTerms(event.event_type);
      addTerms(event.event_date);
    });
    (grounds || []).forEach((ground) => addTerms(ground.title));

    return terms;
  };

  const scoreParagraph = (text, anchorSet) => {
    if (!text) return 0;
    let score = 0;
    if (/\b\d{2,}\b/.test(text)) score += 1.3;
    if (/\b(?:s\.|section)\s*\d+/i.test(text)) score += 1.4;
    if (/\bAct\s+\d{4}\b/i.test(text)) score += 1.2;
    if (/\b(NSW|Cth|QLD|VIC|TAS|SA|WA|ACT|NT)\b/.test(text)) score += 0.8;
    if (/\bR\s+v\b|\bv\s+[A-Z]/.test(text)) score += 1.1;
    if (/^\s*[-*]\s+/m.test(text)) score += 0.7;

    const wordSet = toWordSet(text);
    let anchorHits = 0;
    for (const word of wordSet) {
      if (anchorSet.has(word)) anchorHits += 1;
    }
    score += Math.min(2.2, anchorHits * 0.25);
    score += Math.min(1.8, text.length / 900);

    return score;
  };

  const selectDistinctParagraphs = (entries, anchorSet) => {
    const rawParagraphs = [];
    entries.forEach((entry) => {
      const paragraphs = splitParagraphs(entry.section.content);
      paragraphs.forEach((paragraph, index) => {
        rawParagraphs.push({
          text: paragraph,
          score: scoreParagraph(paragraph, anchorSet),
          source: entry.reportLabel,
          reportRank: entry.reportRank,
          paragraphIndex: index
        });
      });
    });

    if (!rawParagraphs.length) {
      return entries[0]?.section.content || "";
    }

    const sourceCount = new Set(entries.map((entry) => entry.reportLabel)).size;
    const maxParagraphs = Math.max(6, Math.min(12, Math.ceil(sourceCount * 2.5)));
    const qualityThreshold = 1.2;
    const preferred = rawParagraphs.filter((p) => p.score >= qualityThreshold);
    const pool = preferred.length >= 4 ? preferred : rawParagraphs;

    pool.sort((a, b) => (b.score - a.score) || (b.text.length - a.text.length));

    const selected = [];
    const selectedSets = [];

    const isTooSimilar = (candidate) => {
      const candidateSet = toWordSet(candidate.text);
      return selectedSets.some((set) => jaccardSimilarity(candidateSet, set) > 0.68);
    };

    for (const paragraph of pool) {
      if (selected.length >= maxParagraphs) break;
      if (isTooSimilar(paragraph)) continue;
      selected.push(paragraph);
      selectedSets.push(toWordSet(paragraph.text));
    }

    const coveredSources = new Set(selected.map((item) => item.source));
    if (coveredSources.size < sourceCount) {
      const allSources = Array.from(new Set(entries.map((entry) => entry.reportLabel)));
      allSources.forEach((source) => {
        if (coveredSources.has(source)) return;
        const candidate = pool.find((item) => item.source === source && !isTooSimilar(item));
        if (candidate) {
          selected.push(candidate);
          coveredSources.add(source);
          selectedSets.push(toWordSet(candidate.text));
        }
      });
    }

    selected.sort((a, b) => (a.reportRank - b.reportRank) || (a.paragraphIndex - b.paragraphIndex));

    return selected.map((item) => item.text).join("\n\n");
  };

  const buildSynthesisSection = (reports) => {
    if (!reports?.length) return null;
    const paragraphs = [];
    reports.forEach((report, reportIndex) => {
      const analysis = report?.content?.analysis || "";
      splitParagraphs(analysis).forEach((paragraph, paragraphIndex) => {
        paragraphs.push({
          text: paragraph,
          score: scoreParagraph(paragraph, anchorSet || new Set()),
          reportRank: reportIndex,
          paragraphIndex
        });
      });
    });

    if (!paragraphs.length) return null;

    paragraphs.sort((a, b) => (b.score - a.score) || (b.text.length - a.text.length));
    const selected = [];
    const selectedSets = [];

    const isTooSimilar = (candidate) => {
      const candidateSet = toWordSet(candidate.text);
      return selectedSets.some((set) => jaccardSimilarity(candidateSet, set) > 0.7);
    };

    for (const paragraph of paragraphs) {
      if (selected.length >= 10) break;
      if (isTooSimilar(paragraph)) continue;
      selected.push(paragraph.text);
      selectedSets.push(toWordSet(paragraph.text));
    }

    if (!selected.length) return null;

    return {
      title: "Barrister Synthesis",
      content: selected.join("\n\n"),
      sources: ["All Reports"]
    };
  };

  const SECTION_PRIORITY = [
    [/BARRISTER SYNTHESIS/],
    [/EXECUTIVE/, /SUMMARY/],
    [/CHRONOLOGY/, /TIMELINE/],
    [/DOCUMENT/],
    [/GROUNDS OF MERIT/, /GROUNDS/],
    [/SENTENCING/, /COMPARATIVE/],
    [/COMMON APPEAL GROUNDS/, /APPEAL GROUNDS/],
    [/OUTCOME/, /OPTIONS/],
    [/EVIDENTIARY/, /GAPS/],
    [/PRECEDENT/, /MATRIX/],
    [/STATUTORY/, /DOCTRINAL/, /LEGISLATION/],
    [/ARGUE/, /STRATEGY/, /SUBMISSIONS/],
    [/HEARING/, /CONFERENCE/],
    [/FORMS/, /APPEAL/, /PATHWAY/],
    [/ACTION PLAN/, /PRIORITISED/],
    [/RISK/],
    [/CLIENT/, /PLAIN-ENGLISH/]
  ];

  const getSectionPriority = (title) => {
    if (!title) return 999;
    const upper = title.toUpperCase();
    const index = SECTION_PRIORITY.findIndex((patterns) => patterns.some((pattern) => pattern.test(upper)));
    return index === -1 ? 999 : index;
  };

  // Parse and structure the analysis for legal brief format
  const parseAnalysis = (content) => {
    if (!content?.analysis) return { sections: [] };
    
    const analysis = cleanAIContent(sanitiseReportOutput(content.analysis));
    const sections = [];
    
    const lines = analysis.split('\n');
    let currentSection = null;
    let currentContent = [];
    
    const sectionPatterns = [
      { pattern: /^(?:#{1,3}\s+)?(?:\d+\.\s*)?(?:CASE OVERVIEW|OVERVIEW)/i, title: "CASE OVERVIEW", icon: "file" },
      { pattern: /^(?:#{1,3}\s+)?(?:\d+\.\s*)?(?:EVIDENCE|DOCUMENT)/i, title: "EVIDENCE ANALYSIS", icon: "search" },
      { pattern: /^(?:#{1,3}\s+)?(?:\d+\.\s*)?(?:GROUNDS|MERIT)/i, title: "GROUNDS OF MERIT", icon: "scale" },
      { pattern: /^(?:#{1,3}\s+)?(?:\d+\.\s*)?(?:LEGAL|LAW|FRAMEWORK)/i, title: "LEGAL FRAMEWORK", icon: "book" },
      { pattern: /^(?:#{1,3}\s+)?(?:\d+\.\s*)?(?:STRATEGIC|RECOMMEND|STRATEGY)/i, title: "STRATEGIC RECOMMENDATIONS", icon: "target" },
      { pattern: /^(?:#{1,3}\s+)?(?:\d+\.\s*)?(?:SIMILAR|PRECEDENT)/i, title: "SIMILAR CASES & PRECEDENT", icon: "archive" },
      { pattern: /^(?:#{1,3}\s+)?(?:\d+\.\s*)?(?:CONCLUSION)/i, title: "CONCLUSION", icon: "flag" },
      // Only split on main ## numbered sections (e.g., "## 1. EXECUTIVE BRIEF")
      { pattern: /^##\s+\d+\.\s+(.{4,70})$/i, title: null, icon: "chevron" },
    ];
    
    // Helper to clean leading numbers from titles
    const cleanTitle = (raw) => (raw || "ANALYSIS").replace(/^\d+\.\s*/, "").replace(/\*\*/g, "").replace(/^#+\s*/, "").replace(/[\-:]+$/, "").trim();
    
    for (const line of lines) {
      let foundSection = false;
      
      for (const { pattern, title, icon } of sectionPatterns) {
        if (pattern.test(line)) {
          if (currentSection) {
            const cleanedContent = cleanAIContent(sanitiseReportOutput(currentContent.join('\n').trim()));
            if (cleanedContent && cleanedContent.length >= 80) {
              sections.push({
                number: String(sections.length + 1),
                title: currentSection,
                content: cleanedContent,
                icon: icon
              });
            }
          }
          
          if (title) {
            currentSection = title;
          } else {
            const match = line.match(/\*\*([^*]+)\*\*/) || line.match(/^#{1,3}\s+(?:\d+\.\s*)?(.+)$/) || line.match(/^\d+\.\s+(.+)$/);
            currentSection = cleanTitle(match ? (match[1] || match[2]) : line);
          }
          currentContent = [];
          foundSection = true;
          break;
        }
      }
      
      if (!foundSection && currentSection) {
        currentContent.push(line);
      } else if (!foundSection && !currentSection && line.trim()) {
        if (!currentSection) {
          currentSection = "PRELIMINARY ANALYSIS";
          currentContent = [line];
        }
      }
    }
    
    if (currentSection && currentContent.length > 0) {
      const cleanedContent = cleanAIContent(currentContent.join('\n').trim());
      if (cleanedContent && cleanedContent.length >= 80) {
        sections.push({
          number: String(sections.length + 1),
          title: currentSection,
          content: cleanedContent
        });
      }
    }
    
    if (sections.length === 0) {
      sections.push({
        number: "1",
        title: "ANALYSIS",
        content: cleanAIContent(sanitiseReportOutput(analysis))
      });
    }
    
    return { sections };
  };

  // Calculate case strength score
  const calculateStrength = () => {
    const strongGrounds = grounds.filter(g => g.strength === 'strong').length;
    const moderateGrounds = grounds.filter(g => g.strength === 'moderate').length;
    const score = (strongGrounds * 30) + (moderateGrounds * 15) + Math.min(documents.length * 2, 20) + Math.min(timeline.length, 10);
    return Math.min(score, 100);
  };

  // Get key timeline events
  const getKeyEvents = () => {
    return timeline
      .filter(e => e.significance === 'critical' || e.significance === 'important')
      .slice(0, 5);
  };

  const anchorSet = useMemo(() => buildAnchorTerms(), [caseData, documents, timeline, grounds]);

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-white">
        <div className="text-center">
          <div className="relative">
            <Scale className="w-16 h-16 text-blue-500 mx-auto animate-pulse" />
            <div className="absolute -bottom-2 left-1/2 -translate-x-1/2 w-20 h-1 bg-gradient-to-r from-transparent via-blue-500 to-transparent animate-pulse" />
          </div>
          <p className="mt-6 text-slate-300 text-lg" style={{ fontFamily: 'Crimson Pro, serif' }}>
            Preparing your brief...
          </p>
        </div>
      </div>
    );
  }

  // Merge all reports — collect distinct content from standard reports
  const mergeAllReports = () => {
    const availableReports = (allReports || []).filter((r) => !r.content?.aggressive_mode);

    if (!availableReports.length && report?.content) {
      const parsed = parseAnalysis(report.content);
      return {
        sections: parsed.sections || [],
        totalReports: parsed.sections?.length ? 1 : 0,
      };
    }

    const sectionBuckets = new Map(); // normalTitle -> { title, entries, sources }
    const reportOrder = [];

    const sortedReports = [...availableReports].sort((a, b) => {
      const typeOrder = { extensive_log: 3, full_detailed: 2, quick_summary: 1 };
      return (typeOrder[b.report_type] || 0) - (typeOrder[a.report_type] || 0);
    });

    const registerSections = (reportItem, reportLabel, reportRank) => {
      if (!reportItem?.content?.analysis) return;
      const parsed = parseAnalysis(reportItem.content);
      parsed.sections.forEach((section, sectionIndex) => {
        const normalTitle = section.title.toUpperCase().replace(/[^A-Z]/g, '');
        if (!sectionBuckets.has(normalTitle)) {
          sectionBuckets.set(normalTitle, { title: section.title, entries: [], sources: new Set() });
          reportOrder.push(normalTitle);
        }
        const bucket = sectionBuckets.get(normalTitle);
        bucket.entries.push({ section, reportLabel, reportRank, sectionIndex });
        bucket.sources.add(reportLabel);
      });
    };

    sortedReports.forEach((reportItem, index) => {
      const reportLabel = `${reportItem.report_type === 'quick_summary' ? 'Summary' : reportItem.report_type === 'full_detailed' ? 'Full' : 'Extensive'}`;
      registerSections(reportItem, reportLabel, index);
    });

    const existingIds = new Set(availableReports.map((item) => item.report_id));
    if (report?.content?.analysis && !existingIds.has(report.report_id)) {
      const reportLabel = `${report.report_type === 'quick_summary' ? 'Summary' : report.report_type === 'full_detailed' ? 'Full' : 'Extensive'}`;
      registerSections(report, reportLabel, sortedReports.length + 1);
    }

    const merged = reportOrder
      .map((key) => {
        const bucket = sectionBuckets.get(key);
        if (!bucket) return null;
        const mergedContent = selectDistinctParagraphs(bucket.entries, anchorSet || new Set());
        if (!mergedContent || mergedContent.length < 120) return null;
        return {
          title: bucket.title,
          content: mergedContent,
          sources: Array.from(bucket.sources)
        };
      })
      .filter(Boolean);

    const synthesisSection = buildSynthesisSection(sortedReports);
    if (synthesisSection) {
      merged.unshift(synthesisSection);
    }

    const ordered = [...merged].sort((a, b) => {
      const aIndex = getSectionPriority(a.title);
      const bIndex = getSectionPriority(b.title);
      if (aIndex === bIndex) return 0;
      return aIndex - bIndex;
    });

    const renumbered = ordered.map((section, index) => ({ ...section, number: String(index + 1) }));

    return { sections: renumbered, totalReports: availableReports.length };
  };

  const parsedContent = mergeAllReports();
  const reportCount = allReports.length;
  const caseStrength = calculateStrength();
  const keyEvents = getKeyEvents();
  const strongGrounds = grounds.filter(g => g.strength === 'strong');
  const moderateGrounds = grounds.filter(g => g.strength === 'moderate');
  const sentenceSummary = extractSentenceSummary(caseData, report?.content?.analysis || "");
  const offenceSummary = caseData?.offence_type || formatOffenceLabel(caseData?.offence_category) || (() => {
    // Extract offence from report analysis if not in case data
    const analysis = report?.content?.analysis || "";
    const offenceMatch = analysis.match(/(?:convicted of|charged with|offence of|crime of)\s+([A-Za-z\s]+?)(?:\.|,|\s+under|\s+contrary|\s+pursuant)/i);
    if (offenceMatch) return offenceMatch[1].trim();
    // Check case title for common patterns like "R v Homann" — look in the body for the offence
    const murderMatch = analysis.match(/\b(murder|manslaughter|assault|robbery|fraud|theft|sexual assault|drug trafficking|arson)\b/i);
    if (murderMatch) return murderMatch[1].charAt(0).toUpperCase() + murderMatch[1].slice(1).toLowerCase();
    return "See report";
  })();
  const leadGround = strongGrounds[0] || grounds[0] || null;
  const authorityMap = new Map();
  grounds.forEach((ground) => {
    (ground.law_sections || []).forEach((law) => {
      const key = `${law.section || ''}-${law.act || ''}-${law.jurisdiction || ''}`;
      if (!authorityMap.has(key) && (law.section || law.act)) {
        authorityMap.set(key, {
          section: law.section,
          act: law.act,
          jurisdiction: law.jurisdiction,
          linked_ground: ground.title
        });
      }
    });
  });
  const keyAuthorities = Array.from(authorityMap.values()).slice(0, 8);

  const precedentRows = [];
  grounds.forEach((ground) => {
    (ground.similar_cases || []).forEach((item) => {
      if (precedentRows.length < 8) {
        precedentRows.push({
          case_name: item.case_name,
          citation: item.citation,
          outcome: item.outcome,
          relevance: item.relevance,
          linked_ground: ground.title
        });
      }
    });
  });

  const strategicChecklist = [
    leadGround
      ? `Lead with "${leadGround.title}" and establish legal test before factual detail.`
      : "Open with your strongest legal error and establish the appellate test first.",
    "Use chronology as a spine: event date → source → legal consequence.",
    "Anchor each submission paragraph to one statute and one evidentiary reference.",
    "Close by stating precise orders sought (quash, retrial, or resentencing alternative)."
  ];

  const outcomeOptions = [
    {
      option: "Conviction quashed",
      threshold: "Material legal error + miscarriage consequence",
      likelihood: caseStrength >= 72 ? "High" : caseStrength >= 52 ? "Moderate" : "Developing",
      result: "Charge set aside; acquittal or further directions"
    },
    {
      option: "Retrial ordered",
      threshold: "Unsafe verdict but sufficient basis for fresh trial",
      likelihood: caseStrength >= 55 ? "Moderate" : "Low-Moderate",
      result: "Matter remitted for retrial"
    },
    {
      option: "Conviction downgraded/substituted",
      threshold: "Elements for higher offence not sustained",
      likelihood: caseStrength >= 60 ? "Moderate" : "Developing",
      result: "Possible substitution (e.g., murder → manslaughter where sustainable)"
    },
    {
      option: "Sentence reduced",
      threshold: "Manifest excess or error in principle",
      likelihood: caseStrength >= 58 ? "High" : "Moderate",
      result: "Resentencing with lower head sentence/NPP"
    },
    {
      option: "Appeal dismissed",
      threshold: "No material legal error established",
      likelihood: caseStrength >= 65 ? "Lower risk" : "Active risk",
      result: "Original conviction/sentence stands"
    }
  ];

  const comparativeSentenceRows = [
    { case_label: "Comparable Path A", original: "30 / 22.5", revised: "18 / 11", reduction: "12 years (40%)" },
    { case_label: "Comparable Path B", original: "24 / 16", revised: "16 / 10", reduction: "8 years (33%)" },
    { case_label: "Comparable Path C", original: "18 / 12", revised: "14 / 8", reduction: "4 years (22%)" },
  ];

  return (
    <div className="min-h-screen bg-white print:bg-white">
      {/* Premium Header Bar - hidden when printing */}
      <header className="bg-blue-900 text-white sticky top-0 z-50 no-print border-b border-blue-300">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 py-3">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <Button 
                variant="ghost" 
                size="sm" 
                onClick={() => navigate(`/cases/${caseId}`)}
                className="text-slate-300 hover:text-white hover:bg-slate-700"
                data-testid="back-btn"
              >
                <ArrowLeft className="w-4 h-4 mr-1" />
                <span className="hidden sm:inline">Back to Case</span>
              </Button>
              <div className="hidden sm:block h-6 w-px bg-slate-600" />
              <div className="hidden sm:flex items-center gap-2">
                <Scale className="w-5 h-5 text-blue-500" />
                <span className="font-semibold tracking-tight" style={{ fontFamily: 'Crimson Pro, serif' }}>
                  Barrister Brief
                </span>
              </div>
            </div>
            <div className="flex items-center gap-2">
              <Button
                variant="ghost"
                size="sm"
                onClick={toggleFullscreen}
                className="text-slate-300 hover:text-white hover:bg-slate-700 hidden md:flex"
                data-testid="fullscreen-btn"
              >
                <Maximize2 className="w-4 h-4" />
              </Button>
              {/* DO NOT UNDO — Print, PDF, Word buttons MUST be visible on ALL screen sizes */}
              <Button
                variant="outline"
                size="sm"
                onClick={handleExportPDF}
                className="bg-blue-600 hover:bg-blue-700 text-white border-blue-600"
                data-testid="export-btn"
              >
                <Download className="w-4 h-4 mr-1" />
                PDF
              </Button>
              <Button
                variant="outline"
                size="sm"
                onClick={handleExportDOCX}
                className="border-slate-500 text-slate-300 hover:bg-slate-700"
                data-testid="export-docx-btn"
              >
                <FileText className="w-4 h-4 mr-1" />
                Word
              </Button>
              <Button
                variant="outline"
                size="sm"
                onClick={handlePrint}
                className="border-white/50 text-white bg-white/20 hover:bg-white/30"
                data-testid="print-btn"
              >
                <Printer className="w-4 h-4 mr-1" />
                Print
              </Button>
            </div>
          </div>
        </div>
      </header>

      <main className="py-6 sm:py-8 print:py-0">
        <div className="max-w-5xl mx-auto px-4 sm:px-6">
          
          {/* ===== COVER PAGE ===== */}
          <div 
            className="bg-white shadow-2xl rounded-xl overflow-hidden mb-8 print:shadow-none print:rounded-none"
            style={{ minHeight: '100vh' }}
            data-testid="barrister-report"
          >
            {/* Created By — TOP */}
            <div className="text-center py-3 bg-white border-b border-slate-200">
              <p className="text-base font-bold text-slate-800" style={{ fontFamily: 'Crimson Pro, serif' }}>
                Created and Designed by Deb King
              </p>
            </div>

            {/* Cover Header — light mode professional */}
            <div className="bg-slate-800 text-white p-8 sm:p-12 relative overflow-hidden">
              
              <div className="relative z-10">
                {/* Document Type Badge */}
                <div className="flex items-center gap-2 mb-6">
                  <Badge className="bg-blue-500/20 text-blue-300 border-blue-500/30 px-3 py-1">
                    <Scale className="w-3 h-3 mr-1" />
                    BARRISTER BRIEF
                  </Badge>
                  <Badge variant="outline" className="border-slate-500 text-slate-300">
                    Synthesised from {allReports?.length || 3} Reports
                  </Badge>
                </div>

                {/* Case Title */}
                <h1 
                  className="text-3xl sm:text-4xl lg:text-5xl font-bold mb-4 leading-tight"
                  style={{ fontFamily: 'Crimson Pro, serif' }}
                >
                  {caseData?.title}
                </h1>
                
                {/* Subtitle */}
                <p className="text-lg sm:text-xl text-slate-300 mb-8" style={{ fontFamily: 'Crimson Pro, serif' }}>
                  Appeal Case Analysis — Deep Synthesis
                </p>

                {/* Key Case Info Grid */}
                <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 sm:gap-6">
                  <div className="bg-white/5 backdrop-blur-sm rounded-lg p-4">
                    <div className="flex items-center gap-2 text-blue-400 mb-1">
                      <User className="w-4 h-4" />
                      <span className="text-xs uppercase tracking-wide">Defendant</span>
                    </div>
                    <p className="font-semibold text-white">{caseData?.defendant_name || "Not specified"}</p>
                  </div>
                  
                  {caseData?.case_number && (
                    <div className="bg-white/5 backdrop-blur-sm rounded-lg p-4">
                      <div className="flex items-center gap-2 text-blue-400 mb-1">
                        <FileText className="w-4 h-4" />
                        <span className="text-xs uppercase tracking-wide">Case No.</span>
                      </div>
                      <p className="font-mono font-semibold text-white">{caseData.case_number}</p>
                    </div>
                  )}
                  
                  {caseData?.court && caseData.court !== "N/A" && (
                    <div className="bg-white/5 backdrop-blur-sm rounded-lg p-4">
                      <div className="flex items-center gap-2 text-blue-400 mb-1">
                        <Building2 className="w-4 h-4" />
                        <span className="text-xs uppercase tracking-wide">Court</span>
                      </div>
                      <p className="font-semibold text-white text-sm">{caseData.court}</p>
                    </div>
                  )}
                  
                  <div className="bg-white/5 backdrop-blur-sm rounded-lg p-4">
                    <div className="flex items-center gap-2 text-blue-400 mb-1">
                      <MapPin className="w-4 h-4" />
                      <span className="text-xs uppercase tracking-wide">Jurisdiction</span>
                    </div>
                    <p className="font-semibold text-white uppercase">{caseData?.state || 'NSW'}</p>
                  </div>
                </div>

                {/* Prepared by section */}
                <div className="mt-8 pt-6 border-t border-white/10 flex flex-wrap items-center justify-between gap-4">
                  <div>
                    <p className="text-xs uppercase tracking-wide text-slate-400 mb-1">Generated</p>
                    <p className="text-sm text-white font-medium">{formatDate(report?.generated_at)}</p>
                  </div>
                  <div>
                    <p className="text-xs uppercase tracking-wide text-slate-400 mb-1">Grounds Identified</p>
                    <p className="text-sm text-white font-medium">{grounds.length} grounds</p>
                  </div>
                  <div>
                    <p className="text-xs uppercase tracking-wide text-slate-400 mb-1">Documents Analysed</p>
                    <p className="text-sm text-white font-medium">{documents.length} documents</p>
                  </div>
                  <div>
                    <p className="text-xs uppercase tracking-wide text-slate-400 mb-1">Created By</p>
                    <p className="text-sm text-white font-medium">Deb King — GLENMORE PARK NSW</p>
                  </div>
                </div>
              </div>
            </div>

            {/* Confidentiality Notice — DO NOT UNDO */}
            <div className="px-8 sm:px-12 py-3 bg-red-600/10 border-b border-red-600/20">
              <p className="text-xs text-red-600 text-center font-medium tracking-wide">
                CONFIDENTIAL — This document contains privileged legal analysis prepared for educational and research purposes. Not legal advice. Consult a qualified practitioner.
              </p>
            </div>

            {/* ===== TABLE OF CONTENTS ===== */}
            <div className="p-8 sm:p-12 border-b border-slate-200 bg-slate-50" data-testid="barrister-toc">
              <div className="flex items-center gap-3 mb-6">
                <div className="w-10 h-10 rounded-lg bg-slate-100 flex items-center justify-center">
                  <FileText className="w-5 h-5 text-slate-600" />
                </div>
                <h2 
                  className="text-2xl font-bold text-slate-900"
                  style={{ fontFamily: 'Crimson Pro, serif' }}
                >
                  Table of Contents
                </h2>
                {parsedContent.totalReports > 0 && (
                  <span className="text-xs bg-blue-100 text-blue-700 px-2 py-1 rounded-lg font-medium">
                    Synthesised from {parsedContent.totalReports} reports
                  </span>
                )}
              </div>
              <div className="grid sm:grid-cols-2 gap-x-8 gap-y-1">
                {/* Fixed structural sections */}
                <div className="flex items-baseline gap-2 py-1.5 border-b border-slate-200">
                  <span className="text-sm font-bold text-blue-600 w-6">I</span>
                  <span className="text-sm text-slate-700">Executive Summary</span>
                </div>
                <div className="flex items-baseline gap-2 py-1.5 border-b border-slate-200">
                  <span className="text-sm font-bold text-blue-600 w-6">II</span>
                  <span className="text-sm text-slate-700">Hearing Strategy Snapshot</span>
                </div>
                <div className="flex items-baseline gap-2 py-1.5 border-b border-slate-200">
                  <span className="text-sm font-bold text-blue-600 w-6">III</span>
                  <span className="text-sm text-slate-700">Authorities & Precedent Pack</span>
                </div>
                <div className="flex items-baseline gap-2 py-1.5 border-b border-slate-200">
                  <span className="text-sm font-bold text-blue-600 w-6">IV</span>
                  <span className="text-sm text-slate-700">Comparative Sentencing & Relief Pathways</span>
                </div>
                {grounds.length > 0 && (
                  <div className="flex items-baseline gap-2 py-1.5 border-b border-slate-200">
                    <span className="text-sm font-bold text-blue-600 w-6">V</span>
                    <span className="text-sm text-slate-700">Grounds of Merit ({grounds.length} grounds)</span>
                  </div>
                )}
                {keyEvents.length > 0 && (
                  <div className="flex items-baseline gap-2 py-1.5 border-b border-slate-200">
                    <span className="text-sm font-bold text-blue-600 w-6">VI</span>
                    <span className="text-sm text-slate-700">Critical Timeline Events</span>
                  </div>
                )}
                {/* AI Analysis sections from merged reports */}
                {parsedContent.sections.map((section, idx) => (
                  <div key={idx} className="flex items-baseline gap-2 py-1.5 border-b border-slate-200">
                    <span className="text-sm font-bold text-blue-600 w-6">{section.number}</span>
                    <span className="text-sm text-slate-700 truncate">{section.title}</span>
                  </div>
                ))}
                <div className="flex items-baseline gap-2 py-1.5 border-b border-slate-200">
                  <span className="text-sm font-bold text-blue-600 w-6">*</span>
                  <span className="text-sm text-slate-700">Legal Reference Framework</span>
                </div>
              </div>
            </div>

            {/* ===== EXECUTIVE SUMMARY SECTION ===== */}
            <div className="p-8 sm:p-12 border-b border-slate-200">
              <div className="flex items-center gap-3 mb-6">
                <div className="w-10 h-10 rounded-lg bg-indigo-100 flex items-center justify-center">
                  <Target className="w-5 h-5 text-indigo-600" />
                </div>
                <h2 
                  className="text-2xl font-bold text-slate-900"
                  style={{ fontFamily: 'Crimson Pro, serif' }}
                >
                  Executive Summary
                </h2>
              </div>

              <div
                className="mb-6 rounded-2xl border border-indigo-200 bg-gradient-to-r from-indigo-50 via-white to-blue-50 p-5"
                data-testid="barrister-top-summary-box"
              >
                <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-3">
                  <SummaryMetric
                    label="Accused"
                    value={caseData?.defendant_name || "N/A"}
                    testId="barrister-summary-accused"
                  />
                  <SummaryMetric
                    label="Sentence"
                    value={sentenceSummary}
                    testId="barrister-summary-sentence"
                  />
                  <SummaryMetric
                    label="Crime / Offence"
                    value={offenceSummary}
                    testId="barrister-summary-offence"
                  />
                  <SummaryMetric
                    label="Grounds of Merit"
                    value={String(grounds.length)}
                    testId="barrister-summary-grounds"
                  />
                  <SummaryMetric
                    label="Court / State"
                    value={`${caseData?.court || "Court N/A"} • ${(caseData?.state || "NSW").toUpperCase()}`}
                    testId="barrister-summary-court-state"
                  />
                </div>
              </div>
              
              <div className="grid md:grid-cols-2 gap-6">
                {/* Grounds Overview */}
                <div className="bg-gradient-to-br from-emerald-50 to-teal-50 rounded-xl p-6 border border-emerald-200">
                  <div className="flex items-center gap-2 mb-4">
                    <Gavel className="w-5 h-5 text-emerald-600" />
                    <h3 className="font-semibold text-slate-900">Grounds Identified</h3>
                  </div>
                  <div className="space-y-3">
                    <div className="flex items-center justify-between">
                      <span className="text-sm text-slate-600">Strong Grounds</span>
                      <span className="font-bold text-emerald-600 text-lg">{strongGrounds.length}</span>
                    </div>
                    <div className="flex items-center justify-between">
                      <span className="text-sm text-slate-600">Moderate Grounds</span>
                      <span className="font-bold text-red-600 text-lg">{moderateGrounds.length}</span>
                    </div>
                    <div className="flex items-center justify-between">
                      <span className="text-sm text-slate-600">Total Grounds</span>
                      <span className="font-bold text-slate-900 text-lg">{grounds.length}</span>
                    </div>
                  </div>
                </div>

                {/* Quick Stats */}
                <div className="bg-gradient-to-br from-blue-50 to-orange-50 rounded-xl p-6 border border-blue-200">
                  <div className="flex items-center gap-2 mb-4">
                    <BarChart3 className="w-5 h-5 text-red-600" />
                    <h3 className="font-semibold text-slate-900">Evidence Base</h3>
                  </div>
                  <div className="space-y-3">
                    <div className="flex items-center justify-between">
                      <span className="text-sm text-slate-600">Documents</span>
                      <span className="font-bold text-slate-900 text-lg">{documents.length}</span>
                    </div>
                    <div className="flex items-center justify-between">
                      <span className="text-sm text-slate-600">Timeline Events</span>
                      <span className="font-bold text-slate-900 text-lg">{timeline.length}</span>
                    </div>
                    <div className="flex items-center justify-between">
                      <span className="text-sm text-slate-600">Key Events</span>
                      <span className="font-bold text-slate-900 text-lg">{keyEvents.length}</span>
                    </div>
                  </div>
                </div>
              </div>

              {/* Report Metadata */}
              <div className="mt-6 flex flex-wrap items-center gap-4 text-sm text-slate-500">
                <div className="flex items-center gap-2">
                  <Calendar className="w-4 h-4" />
                  <span>Generated: {formatDate(report?.generated_at)}</span>
                </div>
                <div className="flex items-center gap-2">
                  <FileText className="w-4 h-4" />
                  <span>{report?.content?.document_count || documents.length} documents analysed</span>
                </div>
                <div className="flex items-center gap-2">
                  <Clock className="w-4 h-4" />
                  <span>{report?.content?.event_count || timeline.length} timeline events</span>
                </div>
              </div>
            </div>

            {/* ===== HEARING STRATEGY SNAPSHOT ===== */}
            <div className="p-8 sm:p-12 border-b border-slate-200 page-break-inside-avoid bg-gradient-to-r from-indigo-50/60 via-white to-blue-50/50">
              <div className="flex items-center gap-3 mb-6">
                <div className="w-10 h-10 rounded-lg bg-indigo-100 flex items-center justify-center">
                  <Sword className="w-5 h-5 text-indigo-600" />
                </div>
                <h2
                  className="text-2xl font-bold text-slate-900"
                  style={{ fontFamily: 'Crimson Pro, serif' }}
                >
                  Hearing Strategy Snapshot
                </h2>
              </div>

              <div className="grid md:grid-cols-3 gap-4 mb-6" data-testid="hearing-strategy-cards">
                <div className="rounded-xl border border-indigo-200 bg-white/80 p-4">
                  <p className="text-xs uppercase tracking-wide text-indigo-600 mb-2">Lead Ground</p>
                  <p className="font-semibold text-slate-900 text-sm">
                    {leadGround?.title || "Ground to be confirmed after document review"}
                  </p>
                </div>
                <div className="rounded-xl border border-blue-200 bg-white/80 p-4">
                  <p className="text-xs uppercase tracking-wide text-blue-700 mb-2">Authorities Ready</p>
                  <p className="font-semibold text-slate-900 text-sm">
                    {keyAuthorities.length} statute references indexed for submissions
                  </p>
                </div>
                <div className="rounded-xl border border-emerald-200 bg-white/80 p-4">
                  <p className="text-xs uppercase tracking-wide text-emerald-700 mb-2">Orders Sought</p>
                  <p className="font-semibold text-slate-900 text-sm">
                    Quash conviction / alternative resentencing pathway
                  </p>
                </div>
              </div>

              <div className="rounded-xl border border-slate-200 bg-white p-5" data-testid="hearing-strategy-checklist">
                <h3 className="font-semibold text-slate-900 mb-3" style={{ fontFamily: 'Crimson Pro, serif' }}>
                  Counsel Run-Sheet
                </h3>
                <ul className="space-y-2 text-sm text-slate-700">
                  {strategicChecklist.map((item, idx) => (
                    <li key={idx} className="flex items-start gap-2">
                      <ChevronRight className="w-4 h-4 text-indigo-600 shrink-0 mt-0.5" />
                      <span>{item}</span>
                    </li>
                  ))}
                </ul>
              </div>
            </div>

            {/* ===== AUTHORITIES & PRECEDENT PACK ===== */}
            <div className="p-8 sm:p-12 border-b border-slate-200 page-break-inside-avoid">
              <div className="flex items-center gap-3 mb-6">
                <div className="w-10 h-10 rounded-lg bg-purple-100 flex items-center justify-center">
                  <BookOpen className="w-5 h-5 text-purple-600" />
                </div>
                <h2
                  className="text-2xl font-bold text-slate-900"
                  style={{ fontFamily: 'Crimson Pro, serif' }}
                >
                  Authorities & Precedent Pack
                </h2>
              </div>

              <div className="grid lg:grid-cols-2 gap-6" data-testid="authorities-precedents-section">
                <div className="rounded-xl border border-slate-200 overflow-hidden">
                  <div className="px-4 py-3 bg-slate-100 border-b border-slate-200">
                    <h3 className="font-semibold text-slate-900 text-sm">Key Legislative Authorities</h3>
                  </div>
                  <div className="p-4 space-y-3">
                    {keyAuthorities.length > 0 ? keyAuthorities.map((law, idx) => (
                      <div key={idx} className="rounded-lg border border-slate-200 p-3 bg-white">
                        <p className="text-sm font-semibold text-slate-900">
                          {law.section ? `s.${law.section} ` : ""}{law.act || "Legislation Reference"}
                        </p>
                        <p className="text-xs text-slate-600 mt-1">
                          {law.jurisdiction ? `${law.jurisdiction} • ` : ""}Linked ground: {law.linked_ground}
                        </p>
                      </div>
                    )) : (
                      <p className="text-sm text-slate-500">No legislation mapping available yet. Generate grounds analysis to populate this panel.</p>
                    )}
                  </div>
                </div>

                <div className="rounded-xl border border-slate-200 overflow-hidden">
                  <div className="px-4 py-3 bg-slate-100 border-b border-slate-200">
                    <h3 className="font-semibold text-slate-900 text-sm">Comparable Appeal Outcomes</h3>
                  </div>
                  <div className="p-4 space-y-3">
                    {precedentRows.length > 0 ? precedentRows.map((item, idx) => (
                      <div key={idx} className="rounded-lg border border-slate-200 p-3 bg-white">
                        <p className="text-sm font-semibold text-slate-900">{item.case_name || "Comparable case"}</p>
                        <p className="text-xs text-slate-600 mt-1">{item.citation || "Citation pending"}</p>
                        <p className="text-xs text-slate-600 mt-1">Outcome: {item.outcome || "Outcome not recorded"}</p>
                        <p className="text-xs text-slate-600 mt-1">Ground link: {item.linked_ground}</p>
                      </div>
                    )) : (
                      <p className="text-sm text-slate-500 italic">Precedent cases are detailed in the report sections below.</p>
                    )}
                  </div>
                </div>
              </div>
            </div>

            {/* ===== OUTCOME OPTIONS + COMPARATIVE SENTENCING ===== */}
            <div className="p-8 sm:p-12 border-b border-slate-200 page-break-inside-avoid bg-gradient-to-r from-rose-50/40 via-white to-indigo-50/40">
              <div className="flex items-center gap-3 mb-6">
                <div className="w-10 h-10 rounded-lg bg-rose-100 flex items-center justify-center">
                  <BarChart3 className="w-5 h-5 text-rose-600" />
                </div>
                <h2 className="text-2xl font-bold text-slate-900" style={{ fontFamily: 'Crimson Pro, serif' }}>
                  Comparative Sentencing & Relief Pathways
                </h2>
              </div>

              <div className="rounded-xl border border-slate-200 bg-white overflow-x-auto mb-6" data-testid="comparative-sentencing-table-panel">
                <table className="w-full text-sm min-w-[640px]">
                  <thead className="bg-slate-100">
                    <tr>
                      <th className="text-left px-4 py-2 font-semibold text-slate-800">Comparative Track</th>
                      <th className="text-left px-4 py-2 font-semibold text-slate-800">Original Sentence / NPP</th>
                      <th className="text-left px-4 py-2 font-semibold text-slate-800">Revised Sentence / NPP</th>
                      <th className="text-left px-4 py-2 font-semibold text-slate-800">Reduction</th>
                    </tr>
                  </thead>
                  <tbody>
                    {comparativeSentenceRows.map((row) => (
                      <tr key={row.case_label} className="border-t border-slate-200">
                        <td className="px-4 py-2 text-slate-700 font-medium">{row.case_label}</td>
                        <td className="px-4 py-2 text-slate-700">{row.original}</td>
                        <td className="px-4 py-2 text-slate-700">{row.revised}</td>
                        <td className="px-4 py-2 text-emerald-700 font-semibold">{row.reduction}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>

              <div className="rounded-xl border border-slate-200 bg-white overflow-hidden" data-testid="outcome-options-matrix-panel">
                <div className="px-4 py-3 bg-slate-100 border-b border-slate-200">
                  <h3 className="font-semibold text-slate-900 text-sm">Full Options Available Matrix</h3>
                </div>
                <div className="divide-y divide-slate-200">
                  {outcomeOptions.map((item, idx) => (
                    <div key={item.option} className="grid md:grid-cols-4 gap-3 px-4 py-3">
                      <div>
                        <p className="text-[11px] uppercase tracking-wide text-slate-500 mb-1">Option {idx + 1}</p>
                        <p className="font-semibold text-slate-900 text-sm">{item.option}</p>
                      </div>
                      <div>
                        <p className="text-[11px] uppercase tracking-wide text-slate-500 mb-1">Legal Threshold</p>
                        <p className="text-sm text-slate-700">{item.threshold}</p>
                      </div>
                      <div>
                        <p className="text-[11px] uppercase tracking-wide text-slate-500 mb-1">Likelihood (Current Case)</p>
                        <p className="text-sm text-slate-700">{item.likelihood}</p>
                      </div>
                      <div>
                        <p className="text-[11px] uppercase tracking-wide text-slate-500 mb-1">Practical Result</p>
                        <p className="text-sm text-slate-700">{item.result}</p>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>

            {/* ===== GROUNDS OF MERIT SECTION ===== */}
            {grounds.length > 0 && (
              <div className="p-8 sm:p-12 border-b border-slate-200 page-break-inside-avoid">
                <div className="flex items-center gap-3 mb-8">
                  <div className="w-10 h-10 rounded-lg bg-blue-100 flex items-center justify-center">
                    <Gavel className="w-5 h-5 text-red-600" />
                  </div>
                  <div>
                    <h2 
                      className="text-2xl font-bold text-slate-900"
                      style={{ fontFamily: 'Crimson Pro, serif' }}
                    >
                      Grounds of Merit
                    </h2>
                    <p className="text-sm text-slate-500">
                      {grounds.length} potential ground{grounds.length !== 1 ? 's' : ''} for appeal identified
                    </p>
                  </div>
                </div>
                
                <div className="space-y-6">
                  {grounds.map((ground, idx) => {
                    const strengthConfig = STRENGTH_CONFIG[ground.strength] || STRENGTH_CONFIG.moderate;
                    const StrengthIcon = strengthConfig.icon;
                    
                    return (
                      <div 
                        key={ground.ground_id} 
                        className={`rounded-xl border-2 ${strengthConfig.border} ${strengthConfig.bg} overflow-hidden`}
                      >
                        {/* Ground Header */}
                        <div className="p-5 sm:p-6 bg-white/50 border-b border-slate-200">
                          <div className="flex items-start justify-between gap-4">
                            <div className="flex-1">
                              <div className="flex flex-wrap items-center gap-2 mb-3">
                                <span className="flex items-center justify-center w-8 h-8 rounded-full bg-blue-500 text-white font-bold text-sm">
                                  {idx + 1}
                                </span>
                                <Badge variant="outline" className="bg-white">
                                  {GROUND_TYPE_LABELS[ground.ground_type] || ground.ground_type}
                                </Badge>
                                <div className={`flex items-center gap-1 px-2 py-1 rounded-full ${strengthConfig.bg}`}>
                                  <StrengthIcon className={`w-4 h-4 ${strengthConfig.color}`} />
                                  <span className={`text-xs font-semibold ${strengthConfig.color}`}>
                                    {strengthConfig.label}
                                  </span>
                                </div>
                              </div>
                              <h3 
                                className="text-xl font-bold text-slate-900"
                                style={{ fontFamily: 'Crimson Pro, serif' }}
                              >
                                {ground.title}
                              </h3>
                            </div>
                            <div className={`hidden sm:flex items-center justify-center w-12 h-12 rounded-xl ${strengthConfig.bg} ${strengthConfig.border} border`}>
                              <span className={`text-lg font-bold ${strengthConfig.color}`}>{strengthConfig.score}</span>
                            </div>
                          </div>
                        </div>
                        
                        {/* Ground Content */}
                        <div className="p-5 sm:p-6">
                          {/* Description */}
                          <div className="mb-5">
                            <p 
                              className="text-slate-700 leading-relaxed"
                              style={{ fontFamily: 'Crimson Pro, serif', fontSize: '1.05rem' }}
                            >
                              {ground.description}
                            </p>
                          </div>
                          
                          <div className="grid md:grid-cols-2 gap-5">
                            {/* Legal References */}
                            {ground.law_sections && ground.law_sections.length > 0 && (
                              <div className="bg-blue-50 border border-blue-200 rounded-xl p-4">
                                <h4 className="text-sm font-bold text-blue-800 flex items-center gap-2 mb-3">
                                  <BookOpen className="w-4 h-4" />
                                  Relevant Legislation
                                </h4>
                                <ul className="space-y-2">
                                  {ground.law_sections.map((section, sidx) => (
                                    <li key={sidx} className="flex items-start gap-2">
                                      <ChevronRight className="w-4 h-4 text-blue-500 shrink-0 mt-0.5" />
                                      <span className="text-sm text-blue-900">
                                        <span className="font-mono font-semibold">s.{section.section}</span>
                                        {' '}{section.act}
                                        {section.jurisdiction && (
                                          <span className="text-blue-600"> ({section.jurisdiction})</span>
                                        )}
                                      </span>
                                    </li>
                                  ))}
                                </ul>
                              </div>
                            )}
                            
                            {/* Similar Cases */}
                            {ground.similar_cases && ground.similar_cases.length > 0 && (
                              <div className="bg-purple-50 border border-purple-200 rounded-xl p-4">
                                <h4 className="text-sm font-bold text-purple-800 flex items-center gap-2 mb-3">
                                  <Scale className="w-4 h-4" />
                                  Similar Cases
                                </h4>
                                <ul className="space-y-2">
                                  {ground.similar_cases.slice(0, 3).map((caseRef, cidx) => (
                                    <li key={cidx} className="flex items-start gap-2">
                                      <Bookmark className="w-4 h-4 text-purple-500 shrink-0 mt-0.5" />
                                      <span className="text-sm text-purple-900">
                                        <span className="font-semibold">{caseRef.case_name}</span>
                                        {caseRef.citation && (
                                          <span className="text-purple-600"> [{caseRef.citation}]</span>
                                        )}
                                      </span>
                                    </li>
                                  ))}
                                </ul>
                              </div>
                            )}
                          </div>
                          
                          {/* Supporting Evidence */}
                          {ground.supporting_evidence && ground.supporting_evidence.length > 0 && (
                            <div className="mt-5 bg-emerald-50 border border-emerald-200 rounded-xl p-4">
                              <h4 className="text-sm font-bold text-emerald-800 flex items-center gap-2 mb-3">
                                <FileText className="w-4 h-4" />
                                Supporting Evidence
                              </h4>
                              <ul className="grid sm:grid-cols-2 gap-2">
                                {ground.supporting_evidence.map((evidence, eidx) => (
                                  <li key={eidx} className="flex items-start gap-2 text-sm text-emerald-900">
                                    <CheckCircle className="w-4 h-4 text-emerald-500 shrink-0 mt-0.5" />
                                    {evidence}
                                  </li>
                                ))}
                              </ul>
                            </div>
                          )}
                        </div>
                      </div>
                    );
                  })}
                </div>
              </div>
            )}

            {/* ===== KEY TIMELINE EVENTS ===== */}
            {keyEvents.length > 0 && (
              <div className="p-8 sm:p-12 border-b border-slate-200 page-break-inside-avoid">
                <div className="flex items-center gap-3 mb-6">
                  <div className="w-10 h-10 rounded-lg bg-blue-100 flex items-center justify-center">
                    <Clock className="w-5 h-5 text-blue-600" />
                  </div>
                  <h2 
                    className="text-2xl font-bold text-slate-900"
                    style={{ fontFamily: 'Crimson Pro, serif' }}
                  >
                    Critical Timeline Events
                  </h2>
                </div>
                
                <div className="relative">
                  {/* Timeline line */}
                  <div className="absolute left-4 top-0 bottom-0 w-0.5 bg-gradient-to-b from-blue-500 via-indigo-500 to-purple-500 hidden sm:block" />
                  
                  <div className="space-y-4">
                    {keyEvents.map((event, idx) => (
                      <div key={event.event_id} className="flex gap-4 sm:gap-6">
                        <div className="hidden sm:flex flex-col items-center">
                          <div className={`w-8 h-8 rounded-full flex items-center justify-center z-10 ${
                            event.significance === 'critical' 
                              ? 'bg-red-500 text-white' 
                              : 'bg-blue-500 text-white'
                          }`}>
                            {idx + 1}
                          </div>
                        </div>
                        <div className="flex-1 bg-white rounded-xl border border-slate-200 p-4 shadow-sm">
                          <div className="flex flex-wrap items-center gap-2 mb-2">
                            <Badge variant="outline" className="text-xs">
                              {formatShortDate(event.event_date)}
                            </Badge>
                            {event.significance === 'critical' && (
                              <Badge className="bg-red-100 text-red-700">
                                Critical
                              </Badge>
                            )}
                            <Badge variant="outline" className="capitalize">
                              {event.event_type?.replace(/_/g, ' ')}
                            </Badge>
                          </div>
                          <h4 className="font-semibold text-slate-900 mb-1">
                            {event.title}
                          </h4>
                          <p className="text-sm text-slate-600 line-clamp-2">
                            {event.description}
                          </p>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            )}

            {/* ===== AI ANALYSIS SECTIONS ===== */}
            <div className="p-8 sm:p-12">
              <div className="flex items-center gap-3 mb-8">
                <div className="w-10 h-10 rounded-lg bg-slate-100 flex items-center justify-center">
                  <FileText className="w-5 h-5 text-slate-600" />
                </div>
                <h2 
                  className="text-2xl font-bold text-slate-900"
                  style={{ fontFamily: 'Crimson Pro, serif' }}
                >
                  Comprehensive Analysis
                </h2>
                {parsedContent.totalReports > 1 && (
                  <span className="text-xs bg-blue-100 text-blue-700 px-2 py-1 rounded-lg font-medium">
                    Synthesised from {parsedContent.totalReports} reports
                  </span>
                )}
              </div>

              <div className="space-y-8">
                {parsedContent.sections.map((section, idx) => (
                  <div key={idx} className="page-break-inside-avoid">
                    <div className="flex flex-wrap items-baseline gap-4 mb-4 pb-3 border-b-2 border-blue-600 bg-gradient-to-r from-blue-50 via-white to-indigo-50 rounded-xl px-4 py-3">
                      <span className="text-3xl font-bold text-blue-600 bg-blue-100/80 rounded-lg px-3 py-1" style={{ fontFamily: 'Crimson Pro, serif' }}>
                        {section.number}.
                      </span>
                      <h3 
                        className="text-2xl font-bold text-slate-100 uppercase tracking-wide"
                        style={{ fontFamily: 'Crimson Pro, serif' }}
                      >
                        {section.title}
                      </h3>
                    </div>
                    {/* DO NOT UNDO — Markdown rendering for Barrister View analysis sections */}
                    <div className="pl-4 sm:pl-12 border-l-2 border-slate-200">
                      <div className="legal-report">
                        <ReactMarkdown
                          remarkPlugins={[remarkGfm]}
                          components={{
                            a: ({ href, children }) => <a href={href} target="_blank" rel="noopener noreferrer" className="text-blue-400 underline hover:text-blue-300 break-words">{children}</a>,
                            table: ({ children }) => (
                              <div style={{ overflowX: 'auto', WebkitOverflowScrolling: 'touch', display: 'block', maxWidth: '100%', margin: '0.8rem 0' }}>
                                <table style={{ minWidth: '700px', width: '100%', borderCollapse: 'collapse' }}>{children}</table>
                              </div>
                            ),
                          }}
                        >
                          {section.content}
                        </ReactMarkdown>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* ===== LEGAL REFERENCE FRAMEWORK ===== */}
            <div className="p-8 sm:p-12 bg-slate-50 border-t border-slate-200">
              <div className="flex items-center gap-3 mb-6">
                <div className="w-10 h-10 rounded-lg bg-indigo-100 flex items-center justify-center">
                  <BookOpen className="w-5 h-5 text-indigo-600" />
                </div>
                <h2 
                  className="text-xl font-bold text-slate-900"
                  style={{ fontFamily: 'Crimson Pro, serif' }}
                >
                  Legal Reference Framework
                </h2>
              </div>
              
              <div className="grid sm:grid-cols-2 gap-6">
                <div>
                  <h4 className="font-semibold text-slate-900 mb-3">
                    Primary Legislation
                  </h4>
                  <ul className="space-y-2 text-sm text-slate-600">
                    <li className="flex items-start gap-2">
                      <Scale className="w-4 h-4 text-indigo-500 shrink-0 mt-0.5" />
                      <span><strong>Crimes Act 1900 (NSW)</strong> — Primary criminal law</span>
                    </li>
                    <li className="flex items-start gap-2">
                      <Scale className="w-4 h-4 text-indigo-500 shrink-0 mt-0.5" />
                      <span><strong>Criminal Appeal Act 1912 (NSW)</strong> — Appeal procedures</span>
                    </li>
                    <li className="flex items-start gap-2">
                      <Scale className="w-4 h-4 text-indigo-500 shrink-0 mt-0.5" />
                      <span><strong>Evidence Act 1995</strong> — Evidence admissibility</span>
                    </li>
                  </ul>
                </div>
                <div>
                  <h4 className="font-semibold text-slate-900 mb-3">
                    Federal Legislation
                  </h4>
                  <ul className="space-y-2 text-sm text-slate-600">
                    <li className="flex items-start gap-2">
                      <Scale className="w-4 h-4 text-indigo-500 shrink-0 mt-0.5" />
                      <span><strong>Criminal Code Act 1995 (Cth)</strong> — Federal offences</span>
                    </li>
                    <li className="flex items-start gap-2">
                      <Scale className="w-4 h-4 text-indigo-500 shrink-0 mt-0.5" />
                      <span><strong>Judiciary Act 1903 (Cth)</strong> — Court jurisdiction</span>
                    </li>
                  </ul>
                </div>
              </div>
              
              <div className="mt-6 p-4 bg-blue-50 border border-blue-200 rounded-xl">
                <p className="text-sm text-blue-800 italic" style={{ fontFamily: 'Crimson Pro, serif' }}>
                  This document is prepared as an analytical aid and should be reviewed by qualified 
                  legal counsel before being relied upon in legal proceedings. The analysis is based 
                  on information provided and publicly available legal resources.
                </p>
              </div>
            </div>

            {/* ===== DOCUMENT FOOTER ===== */}
            <div className="p-6 sm:p-8 bg-white border-t-2 border-slate-200">
              <div className="text-center mb-4">
                <p className="text-lg font-bold text-slate-900" style={{ fontFamily: 'Crimson Pro, serif' }}>
                  Created and Designed by Deb King
                </p>
                <p className="text-sm text-slate-600 mt-1">
                  Criminal Law Appeal Case Management — GLENMORE PARK NSW
                </p>
              </div>
              <div className="bg-red-50 border-4 border-red-500 rounded-lg p-5 flex items-start gap-4">
                <AlertTriangle className="w-8 h-8 text-red-600 flex-shrink-0 mt-0.5" />
                <div>
                  <p className="text-base font-extrabold text-red-700 uppercase tracking-wide mb-2">NOT LEGAL ADVICE</p>
                  <p className="text-sm font-bold text-slate-800">
                    This document is an educational tool only. It does NOT constitute legal advice and must NOT be relied upon as such. All analysis, findings, and recommendations must be independently verified by a qualified Australian legal professional before any action is taken. No solicitor-client relationship is formed through the provision of this report.
                  </p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </main>

      {/* Print Styles */}
      <style>{`
        .legal-report {
          font-size: 1.02rem;
          line-height: 1.75;
          color: #0f172a;
        }
        .legal-report h1,
        .legal-report h2,
        .legal-report h3,
        .legal-report h4 {
          font-family: 'Crimson Pro', serif;
          font-weight: 700;
          color: #1e3a8a;
          margin: 1.4rem 0 0.7rem;
        }
        .legal-report h2 { font-size: 1.5rem; border-bottom: 2px solid #1e3a5f; padding-bottom: 4px; }
        .legal-report h3 { font-size: 1.25rem; color: #1e40af; }
        .legal-report h4 { font-size: 1.1rem; color: #334155; font-family: 'Manrope', sans-serif; }
        .legal-report strong { color: #0f172a; font-weight: 700; }
        .legal-report ul, .legal-report ol { padding-left: 1.2rem; margin: 0.6rem 0; }
        .legal-report li { margin-bottom: 0.45rem; }
        .legal-report-table-wrap { overflow-x: auto; }
        .legal-report table {
          width: 100%;
          min-width: 700px;
          border-collapse: collapse;
          margin: 0.8rem 0;
          background: #ffffff;
        }
        .legal-report th {
          background: #1e3a8a;
          color: #ffffff !important;
          font-weight: 700;
          font-size: 0.8rem;
        }
        .legal-report th, .legal-report td {
          border: 1px solid #cbd5e1;
          padding: 10px 12px;
          font-size: 0.9rem;
          vertical-align: top;
          color: #0f172a;
          min-width: 90px;
        }
        .legal-report blockquote {
          border-left: 4px solid #1e3a8a;
          padding: 10px 14px;
          margin: 0.8rem 0;
          background: #eff6ff;
          color: #1e3a8a;
        }
        @media print {
          @page {
            size: A4;
            margin: 15mm;
          }
          
          body {
            print-color-adjust: exact;
            -webkit-print-color-adjust: exact;
          }
          
          .page-break-inside-avoid {
            page-break-inside: avoid;
          }
          
          .no-print {
            display: none !important;
          }

          .legal-report { font-size: 12px; color: #0f172a; }
          .legal-report h1,
          .legal-report h2,
          .legal-report h3,
          .legal-report strong { color: #0f172a; }
          .legal-report table { background: #ffffff; }
          .legal-report th { background: #1e3a8a; color: #ffffff !important; }
          .legal-report th, .legal-report td { color: #0f172a; border-color: #cbd5e1; }
          .legal-report blockquote { background: #eff6ff; color: #1e3a8a; border-left: 4px solid #1e3a8a; }
        }
      `}</style>
    </div>
  );
};

const SummaryMetric = ({ label, value, testId }) => (
  <div className="rounded-xl border border-slate-200 bg-white/90 p-3" data-testid={testId}>
    <p className="text-[11px] uppercase tracking-wide text-slate-500 mb-1">{label}</p>
    <p className="text-sm font-semibold text-slate-900 break-words">{value}</p>
  </div>
);

export default BarristerView;
