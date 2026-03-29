/* ========================================================================
   DO NOT UNDO — ENTIRE FILE PROTECTED
   All features, functions, styles, and content in this file are approved
   and must be preserved. Do not remove, rename, or refactor any code.
   ======================================================================== */
import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import axios from "axios";
import { toast } from "sonner";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import {
  AlertTriangle,
  ArrowLeft,
  
  Clock,
  Download,
  FileText,
  FolderOpen,
  Gavel,
  Loader2,
  Printer,
  RefreshCcw,
  Scale,
} from "lucide-react";
import { Button } from "../components/ui/button";
import { Badge } from "../components/ui/badge";
import { API } from "../App";

const formatDate = (dateStr) => {
  if (!dateStr) return "N/A";
  return new Date(dateStr).toLocaleDateString("en-AU", {
    day: "numeric",
    month: "long",
    year: "numeric",
  });
};

const formatTitle = (value) => {
  if (!value) return "Not recorded";
  return value.replace(/_/g, " ").replace(/\b\w/g, (char) => char.toUpperCase());
};

const extractSentenceSummary = (caseInfo, analysis = "") => {
  if (caseInfo?.sentence && caseInfo.sentence.trim().length > 3) return caseInfo.sentence.trim();
  const bySentenceImposed = analysis.match(/(?:sentence\s+imposed\s+was|sentence\s+was|head\s+sentence\s+was|head\s+sentence:|sentenced?\s+to)\s+([^\.\n]{8,160})/i);
  if (bySentenceImposed?.[1]) {
    const cleaned = bySentenceImposed[1]
      .replace(/\s*[|•].*$/, "")
      .replace(/[,;:]?\s*(?:appeal|conviction|leave|outcome)\b.*$/i, "")
      .replace(/[,;:]?\s*(?:dismissed|upheld|refused|granted)\b.*$/i, "")
      .replace(/\s+for\s+[a-z\s'-]+(?=,|\s+with\b|$)/i, "")
      .replace(/\bminimum\s+non[- ]?parole\s+period\b/gi, "non-parole period")
      .replace(/\bwith\s+a\s+minimum\s+non[- ]?parole\s+period\b/gi, "with a non-parole period")
      .replace(/imprisonment,\s+with/gi, "imprisonment with")
      .trim();
    if (/(life|year|month|non[- ]?parole|imprisonment|gaol|custody|sentence)/i.test(cleaned) && !/\b(reduced|reduce|precedent|appeal|submissions|could|should|potentially|perhaps|would|adequacy|seek|sought|relief)\b/i.test(cleaned)) return cleaned;
  }
  const byVerb = analysis.match(/(?:was\s+)?sentenced?\s+to\s+([^\n\.]{10,160})/i);
  if (byVerb?.[1]) {
    return byVerb[1]
      .replace(/\s*[|•].*$/, "")
      .replace(/[,;:]?\s*(?:appeal|conviction|leave|outcome)\b.*$/i, "")
      .replace(/[,;:]?\s*(?:dismissed|upheld|refused|granted)\b.*$/i, "")
      .replace(/\s+for\s+[a-z\s'-]+(?=,|\s+with\b|$)/i, "")
      .replace(/\bminimum\s+non[- ]?parole\s+period\b/gi, "non-parole period")
      .replace(/\bwith\s+a\s+minimum\s+non[- ]?parole\s+period\b/gi, "with a non-parole period")
      .replace(/imprisonment,\s+with/gi, "imprisonment with")
      .trim();
  }
  return "Not recorded";
};

const extractSentenceFromSourceReports = (reports = [], caseInfo = null, fallbackAnalysis = "") => {
  const typeOrder = ["quick_summary", "full_detailed", "extensive_log"];

  for (const reportType of typeOrder) {
    const orderedReports = [...reports]
      .filter((item) => item?.report_type === reportType)
      .sort((a, b) => new Date(b?.generated_at || 0) - new Date(a?.generated_at || 0));

    for (const item of orderedReports) {
      const candidate = extractSentenceSummary(caseInfo, item?.content?.analysis || "")
        .replace(/^sentence\s*[:\-]?\s*/i, "")
        .trim();

      if (
        candidate &&
        candidate !== "Not recorded" &&
        candidate.length < 140 &&
        !/\b(reduced|reduce|precedent|appeal|submissions|could|should|potentially|perhaps|would|adequacy|seek|sought|relief)\b/i.test(candidate)
      ) {
        return candidate;
      }
    }
  }

  return extractSentenceSummary(caseInfo, fallbackAnalysis);
};

const extractOffenceFromAnalysis = (analysis = "") => {
  const patterns = [
    /(?:offence(?:s)?\s+of|for\s+the\s+offence\s+of|convicted\s+of|charged\s+with)\s+([A-Z][A-Za-z0-9\s,'-]{4,120})/i,
    /(?:primary|principal)\s+offence(?:\s+was|:)?\s+([A-Z][A-Za-z0-9\s,'-]{4,120})/i,
    /(?:count\s+\d+\s*[:\-])\s*([A-Z][A-Za-z0-9\s,'-]{4,120})/i,
  ];

  for (const pattern of patterns) {
    const match = analysis.match(pattern);
    if (match?.[1]) {
      return match[1]
        .replace(/under\s+s\.[^\n\.]+/i, "")
        .replace(/,?\s*(?:under|pursuant\s+to).*/i, "")
        .replace(/\s+(?:on|by|amid(?:st)?|with|during)\b.*$/i, "")
        .replace(/\s+of\b.*$/i, "")
        .trim();
    }
  }
  return "";
};

const parseBarristerSections = (analysis = "") => {
  const text = analysis.replace(/\r\n/g, "\n").trim();
  if (!text) return [];

  const chunks = text.split(/\n(?=##\s+)/g);
  const sections = [];
  const introduction = [];

  chunks.forEach((chunk) => {
    const trimmed = chunk.trim();
    if (!trimmed) return;
    const match = trimmed.match(/^##\s+(.+?)\n([\s\S]*)$/);
    if (!match) {
      introduction.push(trimmed);
      return;
    }
    sections.push({
      id: `barrister-section-${sections.length + 1}`,
      title: match[1].trim(),
      content: match[2].trim(),
    });
  });

  if (introduction.length) {
    sections.unshift({
      id: "barrister-section-0",
      title: "Overview",
      content: introduction.join("\n\n"),
    });
  }

  return sections.filter((section) => section.content && section.content.length > 40);
};

const MarkdownBlock = ({ text, testId }) => (
  <div className="legal-report text-slate-900" data-testid={testId}>
    <ReactMarkdown
      remarkPlugins={[remarkGfm]}
      components={{
        a: ({ href, children }) => (
          <a
            href={href}
            target="_blank"
            rel="noopener noreferrer"
            className="text-blue-700 underline underline-offset-2 hover:text-blue-500 break-words"
          >
            {children}
          </a>
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

export default function BarristerView() {
  const { caseId } = useParams();
  const navigate = useNavigate();
  const requestRef = useRef(0);
  const [report, setReport] = useState(null);
  const [caseData, setCaseData] = useState(null);
  const [grounds, setGrounds] = useState([]);
  const [sourceReports, setSourceReports] = useState([]);
  const [timeline, setTimeline] = useState([]);
  const [documents, setDocuments] = useState([]);
  const [loading, setLoading] = useState(true);
  const [status, setStatus] = useState("loading");
  const [errorMessage, setErrorMessage] = useState("");

  const loadBarristerView = useCallback(async (regenerate = false) => {
    const requestId = requestRef.current + 1;
    requestRef.current = requestId;
    setLoading(true);
    try {
      const [caseRes, groundsRes, timelineRes, documentsRes, reportsRes, barristerRes] = await Promise.allSettled([
        axios.get(`${API}/cases/${caseId}`),
        axios.get(`${API}/cases/${caseId}/grounds`),
        axios.get(`${API}/cases/${caseId}/timeline`),
        axios.get(`${API}/cases/${caseId}/documents`),
        axios.get(`${API}/cases/${caseId}/reports`),
        axios.get(`${API}/cases/${caseId}/reports/barrister-view`, {
          params: regenerate ? { regenerate: true } : {},
        }),
      ]);

      if (requestId !== requestRef.current) return;

      if (caseRes.status === "fulfilled") setCaseData(caseRes.value.data);
      if (groundsRes.status === "fulfilled") setGrounds(groundsRes.value.data?.grounds || []);
      if (reportsRes.status === "fulfilled") setSourceReports(reportsRes.value.data || []);
      if (timelineRes.status === "fulfilled") setTimeline(timelineRes.value.data || []);
      if (documentsRes.status === "fulfilled") setDocuments(documentsRes.value.data || []);
      const completedStandardReports = reportsRes.status === "fulfilled"
        ? ["quick_summary", "full_detailed", "extensive_log"].every((type) =>
            (reportsRes.value.data || []).some((item) => item.report_type === type && item.status === "completed")
          )
        : false;

      if (barristerRes.status === "rejected") {
        if (completedStandardReports && !regenerate) {
          const retryRes = await axios.get(`${API}/cases/${caseId}/reports/barrister-view`, {
            params: { regenerate: true },
          });
          if (requestId !== requestRef.current) return;
          const retryReport = retryRes.data;
          setReport(retryReport);
          setStatus(retryReport?.status || "generating");
          setErrorMessage(retryReport?.error || "");
          return;
        }
        const detail = barristerRes.reason?.response?.data?.detail;
        setReport(null);
        setStatus("locked");
        setErrorMessage(typeof detail === "string" ? detail : "Barrister View is not available for this case yet.");
        return;
      }

      const barristerReport = barristerRes.value.data;
      setReport(barristerReport);
      setStatus(barristerReport?.status || "completed");
      setErrorMessage(barristerReport?.error || "");
    } catch (error) {
      if (requestId !== requestRef.current) return;
      setReport(null);
      setStatus("error");
      setErrorMessage("Failed to load the barrister brief.");
    } finally {
      if (requestId !== requestRef.current) return;
      setLoading(false);
    }
  }, [caseId]);

  useEffect(() => {
    setReport(null);
    setCaseData(null);
    setGrounds([]);
    setSourceReports([]);
    setTimeline([]);
    setDocuments([]);
    setStatus("loading");
    setErrorMessage("");
    setLoading(true);
  }, [caseId]);

  useEffect(() => {
    loadBarristerView();
  }, [loadBarristerView]);

  useEffect(() => {
    if (status !== "generating") return undefined;
    const timer = window.setTimeout(() => loadBarristerView(), 4000);
    return () => window.clearTimeout(timer);
  }, [loadBarristerView, status]);

  const sections = useMemo(() => parseBarristerSections(report?.content?.analysis || ""), [report]);
  const sentenceSummary = useMemo(
    () => extractSentenceFromSourceReports(sourceReports, caseData, report?.content?.analysis || ""),
    [caseData, report, sourceReports]
  );
  const offenceLabel = useMemo(() => {
    const extracted = extractOffenceFromAnalysis(report?.content?.analysis || "");
    if (/murder/i.test(extracted || caseData?.offence_type || "")) return "murder";
    return caseData?.offence_type || extracted || formatTitle(caseData?.offence_category);
  }, [caseData, report]);

  const buildAuthUrl = (baseUrl) => {
    const token = localStorage.getItem("session_token");
    if (!token) return baseUrl;
    const separator = baseUrl.includes("?") ? "&" : "?";
    return `${baseUrl}${separator}session_token=${token}`;
  };

  const iosShareOrDownload = async (blob, filename, mimeType) => {
    const isIOS = /iPad|iPhone|iPod/.test(navigator.userAgent);
    if (isIOS && navigator.share) {
      try {
        const file = new File([blob], filename, { type: mimeType });
        if (navigator.canShare && navigator.canShare({ files: [file] })) {
          await navigator.share({ title: filename, files: [file] });
          toast.success("Shared successfully.");
          return;
        }
      } catch (error) {
        if (error.name === "AbortError") return;
      }
    }

    const url = window.URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.setAttribute("download", filename);
    document.body.appendChild(link);
    link.click();
    link.remove();
    setTimeout(() => window.URL.revokeObjectURL(url), 10000);
  };

  const openBarristerPreview = (mode = "print") => {
    const contentEl = document.querySelector('[data-testid="barrister-print-frame"]');
    if (!contentEl) {
      toast.error("Unable to open the barrister brief preview.");
      return;
    }

    const title = `Barrister Brief — ${caseData?.title || "Case"}`;
    const notice = mode === "pdf"
      ? '<div class="preview-notice">PDF preview — use Print / Save as PDF to download.</div>'
      : "";
    const previewDate = new Date(report?.generated_at || Date.now()).toLocaleDateString("en-AU");
    const previewFooterLabel = `Criminal Appeal Case Management - Barrister Brief on ${caseData?.defendant_name || "Appellant"} - ${previewDate}`;

    const html = `<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>${title}</title>
  <link href="https://fonts.googleapis.com/css2?family=Crimson+Pro:wght@400;600;700&family=Manrope:wght@400;500;600;700&display=swap" rel="stylesheet" />
  <style>
    @page { size: A4; margin: 16mm; }
    * { box-sizing: border-box; }
    body { margin: 0; padding-bottom: 88px; background: #eef2f7; color: #0f172a; font-family: 'Manrope', Arial, sans-serif; }
    .preview-shell { max-width: 920px; margin: 24px auto; padding: 0 18px; }
    .cover-page { padding: 0 0 16px; }
    .cover-page-inner { border: 2px solid #cbd5e1; border-radius: 18px; padding: 28px 26px; text-align: center; background: #fff; }
    .cover-page-kicker { margin: 0 0 8px; text-transform: uppercase; letter-spacing: 0.18em; font-size: 11px; font-weight: 800; color: #1d4ed8; }
    .cover-page h1 { margin: 0 0 10px; font-family: 'Crimson Pro', serif; font-size: 32px; color: #0f172a; }
    .cover-page p { margin: 0 0 8px; color: #334155; }
    .cover-page-grid { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 12px; margin: 22px 0 18px; text-align: left; }
    .cover-page-card { border: 1px solid #cbd5e1; border-radius: 14px; padding: 12px 14px; background: #f8fafc; }
    .cover-page-card-label { font-size: 10px; text-transform: uppercase; letter-spacing: 0.08em; color: #64748b; margin-bottom: 4px; }
    .cover-page-card-value { font-size: 14px; font-weight: 700; color: #0f172a; }
    .cover-page-note { margin-top: 12px; border: 2px solid #dc2626; border-radius: 14px; padding: 14px 16px; font-size: 12px; font-weight: 700; color: #1e293b; background: #fef2f2; }
    .page-break { page-break-after: always; break-after: page; }
    .preview-notice { background: #dbeafe; border: 1px solid #93c5fd; color: #1d4ed8; border-radius: 12px; padding: 10px 14px; margin-bottom: 16px; font-size: 13px; }
    .preview-paper { background: #ffffff; border: 1px solid #cbd5e1; box-shadow: 0 20px 40px rgba(15, 23, 42, 0.08); }
    .preview-paper h1, .preview-paper h2, .preview-paper h3, .preview-paper h4 { font-family: 'Crimson Pro', serif; }
    .preview-paper h2 { font-size: 28px; margin: 0; }
    .preview-paper h3 { font-size: 22px; margin: 0 0 10px; }
    .preview-paper p { margin: 0 0 12px; line-height: 1.75; }
    .preview-paper ul, .preview-paper ol { margin: 0 0 14px; padding-left: 22px; }
    .preview-paper li { margin-bottom: 6px; }
    .preview-paper .legal-report-table-wrap { overflow-x: auto; -webkit-overflow-scrolling: touch; }
    .preview-paper table { width: 100%; min-width: 0; border-collapse: collapse; table-layout: fixed; margin: 16px 0; font-size: 12px; }
    .preview-paper th { background: #1d4ed8; color: #ffffff; padding: 10px; text-align: left; border: 1px solid #cbd5e1; font-weight: 800; white-space: normal; word-break: break-word; overflow-wrap: anywhere; vertical-align: top; }
    .preview-paper td { padding: 10px; border: 1px solid #cbd5e1; vertical-align: top; overflow-wrap: anywhere; word-break: break-word; }
    .preview-paper blockquote { margin: 16px 0; padding: 12px 16px; border-left: 4px solid #1d4ed8; background: #eff6ff; }
    .preview-paper a { color: #1d4ed8; text-decoration: underline; }
    .print-footer { position: fixed; left: 0; right: 0; bottom: 0; background: #ffffff; border-top: 1px solid #cbd5e1; padding: 8px 24px 10px; }
    .print-footer-row { display: flex; justify-content: space-between; gap: 16px; align-items: center; font-size: 10px; color: #475569; }
    .print-footer-label { white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
    .print-footer-page-print::after { content: ''; }
    @media print {
      body { background: #ffffff; }
      .preview-shell { max-width: none; margin: 0; padding: 0; }
      .preview-notice { display: none; }
      .preview-paper { border: none; box-shadow: none; }
      .preview-paper .legal-report-table-wrap { overflow: visible; }
      .preview-paper table { min-width: 0 !important; width: 100% !important; table-layout: fixed !important; }
      .print-footer { print-color-adjust: exact; -webkit-print-color-adjust: exact; }
      .print-footer-page-print::after { content: "Page " counter(page); }
    }
    @media (max-width: 768px) {
      .cover-page-grid { grid-template-columns: 1fr; }
      body { font-size: 13px; padding-bottom: 60px; }
      .preview-shell { max-width: 100%; padding: 0 8px; margin: 8px auto; }
      .cover-page-inner { padding: 18px 16px; }
      .cover-page h1 { font-size: 22px; }
      .cover-page-card-value { font-size: 12px; }
      .cover-page-note { font-size: 10px; padding: 10px 12px; }
      .preview-paper h2 { font-size: 20px; }
      .preview-paper h3 { font-size: 17px; }
      .preview-paper p { font-size: 13px; line-height: 1.6; }
      .preview-paper table { font-size: 10px; }
      .preview-paper th, .preview-paper td { padding: 6px; font-size: 10px; }
      .preview-notice { font-size: 11px; padding: 8px 12px; }
      .print-footer { padding: 6px 12px; }
      .print-footer-row { font-size: 8px; }
    }
  </style>
</head>
<body>
  <div class="preview-shell">
    ${notice}
    <section class="cover-page page-break">
      <div class="cover-page-inner">
        <p class="cover-page-kicker">Appeal Case Manager</p>
        <h1>${title}</h1>
        <p>${caseData?.title || "Case"}</p>
        <div class="cover-page-grid">
          <div class="cover-page-card"><div class="cover-page-card-label">Defendant</div><div class="cover-page-card-value">${caseData?.defendant_name || "Appellant"}</div></div>
          <div class="cover-page-card"><div class="cover-page-card-label">Court / State</div><div class="cover-page-card-value">${caseData?.court || "Court"} — ${(caseData?.state || "NSW").toUpperCase()}</div></div>
          <div class="cover-page-card"><div class="cover-page-card-label">Offence</div><div class="cover-page-card-value">${offenceLabel}</div></div>
          <div class="cover-page-card"><div class="cover-page-card-label">Sentence</div><div class="cover-page-card-value">${sentenceSummary}</div></div>
        </div>
        <div class="cover-page-note">NOT LEGAL ADVICE — This application is an educational research tool only and does NOT constitute legal advice. The creator is not a lawyer. All analysis and recommendations must be independently verified by a qualified Australian legal professional. Australian law only. No solicitor-client relationship is created.</div>
      </div>
    </section>
    <div class="preview-paper">${contentEl.innerHTML}</div>
    <div class="disclaimer-bold" style="background:#fef2f2;border:3px solid #ef4444;padding:20px 28px;margin:16px 32px;border-radius:8px;display:flex;gap:14px;align-items:flex-start;">
      <div class="disc-icon" style="color:#ef4444;font-size:28px;flex-shrink:0;">&#9888;</div>
      <div class="disc-text" style="font-size:14px;color:#1e293b;font-weight:700;">
        <strong style="font-size:16px;text-transform:uppercase;letter-spacing:0.08em;color:#dc2626;display:block;margin-bottom:6px;">NOT LEGAL ADVICE</strong>
        This application is an educational research tool only and does NOT constitute legal advice. It must NOT be relied upon as such. The creator of this application is not a lawyer. All analysis, findings, reports, and recommendations generated by this tool must be independently verified by a qualified Australian legal professional before any action is taken. This tool covers Australian law only. No solicitor-client relationship is created by using this service.
      </div>
    </div>
    <div style="text-align:center;margin:24px 32px;padding:16px 0;">
      <p style="font-size:12px;font-weight:700;color:#334155;margin:0 0 10px;">Created and Designed by Deb King</p>
      <div style="display:inline-flex;align-items:center;gap:10px;">
        <div style="width:36px;height:36px;background:#dc2626;border-radius:6px;display:flex;align-items:center;justify-content:center;">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="m16 16 3-8 3 8c-.87.65-1.92 1-3 1s-2.13-.35-3-1Z"/><path d="m2 16 3-8 3 8c-.87.65-1.92 1-3 1s-2.13-.35-3-1Z"/><path d="M7 21h10"/><path d="M12 3v18"/><path d="M3 7h2c2 0 5-1 7-2 2 1 5 2 7 2h2"/></svg>
        </div>
        <div style="text-align:left;">
          <p style="margin:0;font-weight:700;font-size:13px;color:#0f172a;">Appeal Case Manager</p>
          <p style="margin:0;font-size:11px;color:#64748b;">Founded by Debra King</p>
          <p style="margin:0;font-size:11px;color:#64748b;">Criminal Appeal Research Tool &mdash; Australian Law Only</p>
        </div>
      </div>
    </div>
  </div>
  <div class="print-footer">
    <div class="print-footer-row">
      <span class="print-footer-label">${previewFooterLabel}</span>
      <span class="print-footer-page"><span class="print-footer-page-print"></span></span>
    </div>
  </div>
</body>
</html>`;

    localStorage.setItem(
      "document-preview-payload",
      JSON.stringify({
        html,
        mode,
        title,
        source: "barrister",
        returnTo: `/cases/${caseId}/reports/${report?.report_id}/barrister`,
        createdAt: Date.now(),
      })
    );

    const previewUrl = `${window.location.origin}/document-preview?mode=${mode}`;
    window.location.assign(previewUrl);

    toast.success(mode === "print" ? "Print preview opened." : "PDF preview opened.");
  };

  const handleExportPDF = async () => {
    if (!report?.report_id || report?.status !== "completed") return;
    openBarristerPreview("pdf");
  };

  const handleExportDOCX = async () => {
    if (!report?.report_id || report?.status !== "completed") return;
    try {
      const response = await axios.get(`${API}/cases/${caseId}/reports/${report.report_id}/export-docx`, {
        responseType: "blob",
        timeout: 60000,
      });
      const blob = new Blob([response.data], {
        type: "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
      });
      await iosShareOrDownload(
        blob,
        `${caseData?.title || "Case"}_barrister_brief.docx`,
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
      );
      toast.success("Barrister brief Word document downloaded.");
    } catch (error) {
      toast.error("Failed to export the barrister brief Word document.");
    }
  };

  const handleBackToCase = () => {
    window.location.assign(`/cases/${caseId}`);
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-slate-50 flex items-center justify-center" data-testid="barrister-view-loading">
        <div className="text-center">
          <Loader2 className="w-12 h-12 animate-spin text-blue-700 mx-auto" />
          <p className="mt-4 text-slate-700">Loading Barrister View…</p>
        </div>
      </div>
    );
  }

  const reportStatus = report?.status || status;
  const isGenerating = reportStatus === "generating";
  const isCompleted = reportStatus === "completed" && report?.content?.analysis;
  const isFailed = reportStatus === "failed";
  const sourceReportMeta = report?.content?.source_reports || [];

  return (
    <div className="min-h-screen bg-slate-50 report-page">
      <header className="sticky top-0 z-40 border-b border-slate-200 bg-white/95 backdrop-blur no-print" data-testid="barrister-header">
        <div className="max-w-5xl mx-auto px-4 sm:px-6 py-3 flex items-center justify-between gap-3 flex-wrap">
          <div className="flex items-center gap-3 flex-wrap">
            <Button
              size="sm"
              onClick={handleBackToCase}
              className="bg-blue-700 text-white hover:bg-blue-600"
              data-testid="barrister-back-button"
            >
              <ArrowLeft className="w-4 h-4 mr-1" /> Back to Case
            </Button>
            <Badge className="bg-slate-900 text-white" data-testid="barrister-status-badge">
              {isGenerating ? "Generating Barrister Brief" : isCompleted ? "Barrister Brief Ready" : "Barrister Brief"}
            </Badge>
          </div>

          <div className="flex items-center gap-2 flex-wrap">
            <Button
              size="sm"
              onClick={() => openBarristerPreview("print")}
              disabled={!isCompleted}
              className="bg-blue-700 text-white hover:bg-blue-600"
              data-testid="barrister-print-button"
            >
              <Printer className="w-4 h-4 mr-2" /> Print
            </Button>
            <Button
              size="sm"
              onClick={handleExportDOCX}
              disabled={!isCompleted}
              className="bg-blue-700 text-white hover:bg-blue-600"
              data-testid="barrister-export-docx-button"
            >
              <FileText className="w-4 h-4 mr-2" /> Export Word
            </Button>
            <Button
              size="sm"
              onClick={handleExportPDF}
              disabled={!isCompleted}
              className="bg-blue-700 text-white hover:bg-blue-600"
              data-testid="barrister-export-pdf-button"
            >
              <Download className="w-4 h-4 mr-2" /> Export PDF
            </Button>
          </div>
        </div>
      </header>

      <main className="max-w-5xl mx-auto px-4 sm:px-6 py-8">
        {(status === "locked" || status === "error") && (
          <div className="bg-white border border-slate-200 rounded-2xl shadow-sm p-8" data-testid="barrister-locked-state">
            <div className="flex items-start gap-4">
              <AlertTriangle className="w-8 h-8 text-red-600 flex-shrink-0 mt-1" />
              <div>
                <h1 className="text-3xl sm:text-4xl font-bold text-slate-900">Barrister View unavailable</h1>
                <p className="mt-3 text-slate-700 max-w-3xl">{errorMessage || "This case does not yet have the three completed standard reports required to unlock the Barrister View."}</p>
              </div>
            </div>
          </div>
        )}

        {isGenerating && (
          <div className="bg-white border border-slate-200 rounded-2xl shadow-sm p-8" data-testid="barrister-generating-state">
            <div className="flex items-start gap-4">
              <Loader2 className="w-8 h-8 animate-spin text-blue-700 flex-shrink-0 mt-1" />
              <div>
                <h1 className="text-3xl sm:text-4xl font-bold text-slate-900">Preparing the Barrister Brief</h1>
                <p className="mt-3 text-slate-700 max-w-3xl">
                  The backend is now writing one consolidated barrister-ready brief from the Quick Summary, Full Detailed Report, and Extensive Log Report. This page refreshes automatically while the synthesis is running.
                </p>
                <div className="mt-5 flex flex-wrap gap-3">
                  <Badge variant="outline" className="border-blue-200 text-blue-700">Single cohesive brief</Badge>
                  <Badge variant="outline" className="border-blue-200 text-blue-700">No frontend merge logic</Badge>
                  <Badge variant="outline" className="border-blue-200 text-blue-700">Professional export formatting</Badge>
                </div>
              </div>
            </div>
          </div>
        )}

        {isFailed && (
          <div className="bg-white border border-slate-200 rounded-2xl shadow-sm p-8" data-testid="barrister-failed-state">
            <div className="flex items-start gap-4">
              <AlertTriangle className="w-8 h-8 text-red-600 flex-shrink-0 mt-1" />
              <div className="flex-1">
                <h1 className="text-3xl sm:text-4xl font-bold text-slate-900">Barrister Brief generation failed</h1>
                <p className="mt-3 text-slate-700 max-w-3xl">{errorMessage || "The brief could not be generated on the last attempt."}</p>
                <Button
                  className="mt-5 bg-blue-700 text-white hover:bg-blue-600"
                  onClick={() => loadBarristerView(true)}
                  data-testid="barrister-retry-button"
                >
                  <RefreshCcw className="w-4 h-4 mr-2" /> Generate again
                </Button>
              </div>
            </div>
          </div>
        )}

        {isCompleted && (
          <article className="bg-white border border-slate-200 rounded-2xl shadow-xl overflow-hidden" data-testid="barrister-print-frame">
            <div className="px-6 sm:px-10 py-6 sm:py-7 border-b border-slate-200 bg-white" data-testid="barrister-hero">
              <div className="flex flex-col xl:flex-row xl:items-start xl:justify-between gap-8">
                <div className="min-w-0 flex-1 xl:flex-[1.2] xl:pr-8">
                  <div className="flex flex-wrap items-center gap-3 mb-3">
                    <Badge className="bg-blue-700 text-white" data-testid="barrister-hero-badge">
                      <Scale className="w-3.5 h-3.5 mr-1.5" /> BARRISTER BRIEF
                    </Badge>
                    <span className="text-sm font-medium text-slate-600" data-testid="barrister-source-badge">
                      Built from all {sourceReportMeta.length || 3} completed reports
                    </span>
                  </div>

                  <h1 className="text-4xl sm:text-5xl font-bold text-slate-900 leading-[1.05] break-words max-w-3xl" data-testid="barrister-title">
                    {caseData?.title || "Barrister Brief"}
                  </h1>
                </div>

                <div className="grid grid-cols-1 sm:grid-cols-2 gap-x-6 gap-y-4 w-full xl:w-[440px] xl:flex-shrink-0" data-testid="barrister-summary-grid">
                  <CompactMetric label="Defendant" value={caseData?.defendant_name || "Not recorded"} testId="barrister-summary-defendant" />
                  <CompactMetric label="Court / State" value={`${caseData?.court || "Court not recorded"} • ${(caseData?.state || "nsw").toUpperCase()}`} testId="barrister-summary-court-state" />
                  <CompactMetric label="Sentence" value={sentenceSummary} testId="barrister-summary-sentence" />
                  <CompactMetric label="Offence" value={offenceLabel} testId="barrister-summary-offence" />
                  <CompactMetric label="Grounds" value={`${grounds.length}`} testId="barrister-summary-grounds" />
                  <CompactMetric label="Generated" value={formatDate(report?.generated_at)} testId="barrister-summary-generated" />
                </div>
              </div>
            </div>

            <div className="px-6 sm:px-10 py-5 bg-red-700" data-testid="barrister-disclaimer-banner">
              <div className="flex items-start gap-3">
                <AlertTriangle className="w-6 h-6 text-white shrink-0 mt-0.5" />
                <div>
                  <p className="text-base font-extrabold text-white uppercase tracking-wide mb-1">NOT LEGAL ADVICE</p>
                  <p className="text-sm text-white leading-relaxed">
                    This application is an educational research tool only and does NOT constitute legal advice. It must NOT be relied upon as such. The creator of this application is not a lawyer. All analysis, findings, reports, and recommendations generated by this tool must be independently verified by a qualified Australian legal professional before any action is taken. This tool covers Australian law only. No solicitor-client relationship is created by using this service.
                  </p>
                </div>
              </div>
            </div>

            <div className="px-6 sm:px-10 py-4 bg-slate-50 border-b border-slate-200" data-testid="barrister-meta-strip">
              <div className="grid md:grid-cols-3 gap-3 text-sm text-slate-700">
                <div className="flex items-center gap-2" data-testid="barrister-meta-documents">
                  <FolderOpen className="w-4 h-4 text-blue-700" /> {documents.length} documents analysed
                </div>
                <div className="flex items-center gap-2" data-testid="barrister-meta-timeline">
                  <Clock className="w-4 h-4 text-blue-700" /> {timeline.length} timeline events
                </div>
                <div className="flex items-center gap-2" data-testid="barrister-meta-source-reports">
                  <Gavel className="w-4 h-4 text-blue-700" /> {sourceReportMeta.length || 3} source reports referenced
                </div>
              </div>
            </div>

            {sections.length > 1 && (
              <div className="px-6 sm:px-10 py-8 border-b border-slate-200 bg-white" data-testid="barrister-table-of-contents">
                <div className="flex items-center gap-3 mb-5">
                  <FileText className="w-5 h-5 text-blue-700" />
                  <h2 className="text-2xl font-bold text-slate-900">Table of contents</h2>
                </div>
                <div className="grid md:grid-cols-2 gap-2">
                  {sections.map((section, index) => (
                    <button
                      key={section.id}
                      onClick={() => document.getElementById(section.id)?.scrollIntoView({ behavior: "smooth", block: "start" })}
                      className="text-left rounded-xl border border-slate-200 bg-slate-50 px-4 py-3 hover:border-blue-300 hover:bg-blue-50 transition-colors"
                      data-testid={`barrister-toc-item-${index + 1}`}
                    >
                      <span className="text-xs font-bold uppercase tracking-wide text-blue-700">Section {index + 1}</span>
                      <p className="mt-1 text-sm font-semibold text-slate-900">{section.title}</p>
                    </button>
                  ))}
                </div>
              </div>
            )}

            <div className="px-6 sm:px-10 py-8 sm:py-10 space-y-10" data-testid="barrister-sections-wrapper">
              {sections.map((section, index) => (
                <section key={section.id} id={section.id} className="scroll-mt-24" data-testid={`barrister-section-${index + 1}`}>
                  <div className="flex items-start gap-4 mb-5">
                    <div className="w-11 h-11 rounded-full bg-blue-100 text-blue-800 flex items-center justify-center text-sm font-bold flex-shrink-0" data-testid={`barrister-section-number-${index + 1}`}>
                      {index + 1}
                    </div>
                    <div>
                      <p className="text-xs uppercase tracking-[0.2em] text-slate-500">Section {index + 1}</p>
                      <h2 className="text-3xl font-bold text-slate-900" data-testid={`barrister-section-heading-${index + 1}`}>
                        {section.title}
                      </h2>
                    </div>
                  </div>
                  <div className="rounded-2xl border border-slate-200 bg-white p-6 sm:p-8 shadow-sm" data-testid={`barrister-section-body-${index + 1}`}>
                    <MarkdownBlock text={section.content} testId={`barrister-section-markdown-${index + 1}`} />
                  </div>
                </section>
              ))}
            </div>

            <div className="bg-red-700 px-6 sm:px-10 py-6" data-testid="barrister-footer">
              <div className="flex items-start gap-4" data-testid="barrister-footer-disclaimer">
                <AlertTriangle className="w-8 h-8 text-white flex-shrink-0 mt-0.5" />
                <div>
                  <p className="text-base font-extrabold text-white uppercase tracking-wide mb-2">NOT LEGAL ADVICE</p>
                  <p className="text-sm text-white leading-relaxed">
                    This application is an educational research tool only and does NOT constitute legal advice. It must NOT be relied upon as such. The creator of this application is not a lawyer. All analysis, findings, reports, and recommendations generated by this tool must be independently verified by a qualified Australian legal professional before any action is taken. This tool covers Australian law only. No solicitor-client relationship is created by using this service.
                  </p>
                </div>
              </div>
            </div>
            {/* ===== BRANDING FOOTER ===== */}
            <div className="bg-white py-6 text-center" data-testid="barrister-branding-footer">
              <p className="text-xs font-bold text-slate-600 mb-3">Created and Designed by Deb King</p>
              <div className="flex items-center justify-center gap-2.5">
                <div className="w-9 h-9 bg-red-600 rounded-md flex items-center justify-center flex-shrink-0">
                  <Scale className="w-5 h-5 text-white" />
                </div>
                <div className="text-left">
                  <p className="font-bold text-slate-900 text-sm leading-tight">Appeal Case Manager</p>
                  <p className="text-xs text-slate-500 leading-tight">Founded by Debra King</p>
                  <p className="text-xs text-slate-500 leading-tight">Criminal Appeal Research Tool — Australian Law Only</p>
                </div>
              </div>
            </div>
          </article>
        )}
      </main>

      <style>{`
        .legal-report {
          font-size: 1.05rem;
          line-height: 1.85;
          color: #0f172a;
        }
        .legal-report h1,
        .legal-report h2,
        .legal-report h3,
        .legal-report h4 {
          font-family: 'Crimson Pro', serif;
          font-weight: 700;
          color: #1e3a8a;
          margin: 1.4rem 0 0.75rem;
        }
        .legal-report h2 {
          font-size: 1.6rem;
          border-bottom: 2px solid #1e3a8a;
          padding-bottom: 0.35rem;
        }
        .legal-report h3 { font-size: 1.3rem; }
        .legal-report h4 { font-size: 1.1rem; color: #334155; }
        .legal-report p { margin-bottom: 0.9rem; }
        .legal-report strong { color: #0f172a; }
        .legal-report ul, .legal-report ol { margin: 0.8rem 0 1rem; padding-left: 1.5rem; }
        .legal-report li { margin-bottom: 0.45rem; }
        .legal-report table {
          width: 100%;
          min-width: 640px;
          table-layout: fixed;
          border-collapse: collapse;
          margin: 0;
        }
        .legal-report th,
        .legal-report td {
          border: 1px solid #cbd5e1;
          padding: 0.75rem 0.85rem;
          vertical-align: top;
          overflow-wrap: anywhere;
          font-size: 0.92rem;
        }
        .legal-report th {
          background: #1d4ed8;
          color: #ffffff;
          font-weight: 800;
          white-space: normal;
          word-break: normal;
          overflow-wrap: normal;
          vertical-align: top;
        }
        .legal-report blockquote {
          margin: 1rem 0;
          padding: 0.9rem 1rem;
          border-left: 4px solid #1d4ed8;
          background: #eff6ff;
          color: #1e3a8a;
        }
        @media print {
          body { print-color-adjust: exact; -webkit-print-color-adjust: exact; }
          .no-print { display: none !important; }
          .legal-report { font-size: 11.5pt; }
          .legal-report-table-wrap { overflow: visible; }
        }
      `}</style>
    </div>
  );
}

const CompactMetric = ({ label, value, testId }) => (
  <div className="min-w-0" data-testid={testId}>
    <p className="text-[11px] uppercase tracking-[0.2em] text-slate-500 mb-1">{label}</p>
    <p className="text-sm font-semibold text-slate-900 break-words leading-snug">{value}</p>
  </div>
);