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
import { isIOSDevice } from "../utils/isIOS";
import ReportTranslator from "../components/ReportTranslator";
import {
  AlertTriangle,
  ArrowLeft,
  Clock,
  Download,
  FileText,
  Loader2,
  Printer,
  RefreshCcw,
  Scale,
  Zap,
} from "lucide-react";
import { Button } from "../components/ui/button";
import { API } from "../App";
import StrengthBadge from "../components/StrengthBadge";
import VerificationBadge from "../components/VerificationBadge";
import LegitimacyPanel from "../components/LegitimacyPanel";
import EvidenceSummary from "../components/EvidenceSummary";
import ReportMetadataPanel from "../components/ReportMetadataPanel";
import auSpelling from "../utils/auSpelling";

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
      {auSpelling(text)}
    </ReactMarkdown>
  </div>
);

const BarristerGroundBlock = ({ ground }) => (
  <div className="border border-slate-200 rounded-lg p-4 mb-4" data-testid={`barrister-ground-block-${ground.ground_id}`}>
    <div className="flex items-center gap-2 mb-2 flex-wrap">
      <div className="font-semibold text-slate-900" style={{ fontFamily: "'Times New Roman', Times, serif" }}>{ground.title}</div>
      <StrengthBadge rating={ground.strength} />
      <VerificationBadge status={ground.verification_status} />
    </div>

    {ground.ground_type && (
      <div className="text-xs uppercase tracking-wide text-slate-400 mb-2">
        {String(ground.ground_type).replace(/_/g, " ")}
      </div>
    )}

    {ground.description && (
      <div className="text-sm text-slate-600 mb-2 whitespace-pre-wrap">{ground.description}</div>
    )}

    <LegitimacyPanel scores={ground.legitimacy_scores} />

    <EvidenceSummary items={ground.supporting_evidence} expanded />

    {/* Comparable Cases — with jurisdiction and relevance note */}
    {Array.isArray(ground.similar_cases) && ground.similar_cases.length > 0 && (
      <div className="mt-3">
        <div className="font-medium text-sm mb-2 text-slate-700">Comparable Cases</div>
        <div className="space-y-2">
          {ground.similar_cases.map((c, i) => (
            <div key={i} className="text-xs border border-slate-100 rounded p-2">
              <div className="font-medium text-slate-700">{c.case_name || "Unnamed case"}</div>
              {c.citation && <div className="text-slate-600">{c.citation}</div>}
              <div className="text-slate-400 mt-1">
                {c.jurisdiction ? `${String(c.jurisdiction).toUpperCase()} \u2022 ` : ""}
                {c.verification_status || "unverified"}
              </div>
              {c.relevance_note && <div className="mt-1 text-slate-500">{c.relevance_note}</div>}
            </div>
          ))}
        </div>
      </div>
    )}

    {/* Law Sections */}
    {Array.isArray(ground.law_sections) && ground.law_sections.length > 0 && (
      <div className="mt-3">
        <div className="font-medium text-sm mb-2 text-slate-700">Law Sections</div>
        <div className="space-y-1">
          {ground.law_sections.map((section, idx) => (
            <div key={idx} className="text-xs text-slate-600">
              {section.section ? `${section.section} ` : ""}
              {section.act || ""}
              {section.title ? ` \u2014 ${section.title}` : ""}
              {section.verification_status ? ` (${section.verification_status})` : ""}
            </div>
          ))}
        </div>
      </div>
    )}

    {ground.requires_human_review && (
      <div className="mt-3 text-xs text-red-700 font-medium">
        Requires human review before filing or reliance in advice.
      </div>
    )}
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
  const [genStartTime, setGenStartTime] = useState(null);
  const [genElapsed, setGenElapsed] = useState(0);

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
        const detail = barristerRes.reason?.response?.data?.detail;
        setReport(null);
        setStatus("not_generated");
        setErrorMessage(typeof detail === "string" ? detail : "Barrister Brief has not been generated yet. Generate it from the Reports section.");
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

  // Elapsed timer for generating state
  useEffect(() => {
    if (status === "generating" || loading) {
      if (!genStartTime) setGenStartTime(Date.now());
      const interval = setInterval(() => {
        setGenElapsed(Math.floor((Date.now() - (genStartTime || Date.now())) / 1000));
      }, 1000);
      return () => clearInterval(interval);
    } else {
      setGenStartTime(null);
      setGenElapsed(0);
    }
  }, [status, loading, genStartTime]);

  const sections = useMemo(() => parseBarristerSections(report?.content?.analysis || ""), [report]);
  const sentenceSummary = useMemo(
    () => extractSentenceFromSourceReports(sourceReports, caseData, report?.content?.analysis || ""),
    [caseData, report, sourceReports]
  );
  const offenceLabel = useMemo(() => {
    const extracted = extractOffenceFromAnalysis(report?.content?.analysis || "");
    if (/murder/i.test(extracted || caseData?.offence_type || "")) return "Murder";
    const raw = caseData?.offence_type || extracted || formatTitle(caseData?.offence_category);
    return raw ? raw.charAt(0).toUpperCase() + raw.slice(1) : "Not specified";
  }, [caseData, report]);

  const buildAuthUrl = async (baseUrl) => {
    const { buildSecureDownloadUrl } = await import("../utils/downloadToken");
    return buildSecureDownloadUrl(baseUrl);
  };

  const iosShareOrDownload = async (blob, filename, mimeType) => {
    const isIOS = isIOSDevice();
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
    const contentEl = document.querySelector('[data-testid="barrister-sections-wrapper"]');
    if (!contentEl) {
      toast.error("Unable to open the barrister brief preview.");
      return;
    }

    const title = `Barrister Brief — ${caseData?.title || "Case"}`;
    const notice = mode === "pdf"
      ? '<div class="preview-notice">PDF preview — use Print / Save as PDF to download.</div>'
      : "";
    const previewDate = new Date(report?.generated_at || Date.now()).toLocaleDateString("en-AU", { day: "2-digit", month: "2-digit", year: "numeric" });
    const previewFooterLabel = `Documented from the Criminal Law /Appeal Management Application - Barrister View Report - For ${caseData?.defendant_name || caseData?.title || "Appellant"} ${previewDate}`;
    const defendantName = caseData?.defendant_name || "Appellant";
    const meta = `${caseData?.court || "Court"} — ${(caseData?.state || "NSW").toUpperCase()}`;
    const documentsCount = documents.length;
    const eventsCount = timeline.length;
    const reportsCount = sourceReportMeta.length || 3;

    // Build TOC from sections
    const tocHtml = sections.length > 1
      ? `<div class="toc-container" style="padding:14px 32px;">
          <p class="toc-heading" style="font-size:13pt;text-transform:uppercase;letter-spacing:0.05em;color:#334155;font-weight:800;margin:0 0 10px;font-family:'Times New Roman',Times,serif;">CONTENTS (${sections.length} SECTIONS)</p>
          <div class="toc-grid" style="display:grid;grid-template-columns:1fr 1fr;gap:4px 20px;">
            ${sections.map((s, i) => `<div class="toc-item" style="font-size:12pt;color:#1e293b;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;padding:3px 0;font-weight:700;text-transform:uppercase;font-family:'Times New Roman',Times,serif;"><strong>${i + 1}.</strong> ${s.title}</div>`).join('')}
          </div>
        </div>`
      : "";

    const html = `<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>${title}</title>
  <link href="https://fonts.googleapis.com/css2?family=Crimson+Pro:wght@400;600;700&family=Manrope:wght@400;500;600;700&display=swap" rel="stylesheet" />
  <style>
    @page { size: A4; margin: 14mm 14mm 20mm; }
    * { box-sizing: border-box; margin: 0; padding: 0; }
    body { font-family: 'Times New Roman', Times, serif; padding: 0 0 88px; color: #0f172a; line-height: 1.8; font-size: 12pt; background: #fff; }
    .report-container { max-width: 900px; margin: 0 auto; }
    .cover-page { padding: 32px 0 16px; }
    .cover-page-inner { border: 2px solid #cbd5e1; border-radius: 18px; padding: 28px 26px; text-align: center; background: #fff; }
    .cover-page-kicker { margin: 0 0 8px; text-transform: uppercase; letter-spacing: 0.18em; font-size: 11px; font-weight: 800; color: #1d4ed8; }
    .cover-page h1 { margin: 0 0 10px; font-family: 'Times New Roman', Times, serif; font-size: 22pt; color: #0f172a; font-weight: 700; }
    .cover-page p { margin: 0 0 8px; color: #334155; }
    .cover-page-grid { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 12px; margin: 22px 0 18px; text-align: left; }
    .cover-page-card { border: 1px solid #cbd5e1; border-radius: 14px; padding: 12px 14px; background: #f8fafc; }
    .cover-page-card-label { font-size: 13px; text-transform: uppercase; letter-spacing: 0.08em; color: #64748b; margin-bottom: 4px; }
    .cover-page-card-value { font-size: 14px; font-weight: 700; color: #0f172a; }
    .cover-page-note { margin-top: 12px; border: 2px solid #b91c1c; border-radius: 14px; padding: 14px 16px; font-size: 12px; font-weight: 700; color: #ffffff; background: #dc2626; -webkit-print-color-adjust: exact !important; print-color-adjust: exact !important; }
    .page-break { page-break-after: always; break-after: page; }
    .preview-notice { background: #dbeafe; border: 1px solid #93c5fd; color: #1d4ed8; border-radius: 12px; padding: 10px 14px; margin-bottom: 16px; font-size: 13px; }
    .report-header { background: #14b8a6; color: #fff; padding: 28px 32px; -webkit-print-color-adjust: exact !important; print-color-adjust: exact !important; color-adjust: exact !important; page-break-inside: avoid; break-inside: avoid; page-break-before: always; break-before: page; }
    .report-header h1 { font-family: 'Times New Roman', Times, serif; font-size: 18pt; font-weight: 700; margin-bottom: 4px; color: #fff; }
    .report-header .meta-line { font-size: 13px; color: rgba(255,255,255,0.9); margin-top: 2px; }
    .report-header .grounds-count { font-size: 22px; font-weight: 700; color: #fff; text-align: right; }
    .report-header .grounds-label { font-size: 11px; color: rgba(255,255,255,0.8); text-align: right; }
    .report-header .header-row { display: flex; justify-content: space-between; align-items: flex-start; }
    .report-header .badge { display: inline-block; background: rgba(255,255,255,0.25); padding: 3px 12px; border-radius: 999px; font-size: 12px; font-weight: 700; margin-top: 8px; }
    .report-header .gen-date { font-size: 11px; color: rgba(255,255,255,0.85); margin-top: 4px; }
    .report-header .case-info-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 10px; margin-top: 16px; padding-top: 12px; border-top: 1px solid rgba(255,255,255,0.2); background: inherit; -webkit-print-color-adjust: exact !important; print-color-adjust: exact !important; }
    .report-header .case-info-grid .ci-label { font-size: 12px; text-transform: uppercase; letter-spacing: 0.05em; color: rgba(255,255,255,0.7); margin-bottom: 2px; }
    .report-header .case-info-grid .ci-value { font-size: 12pt; font-weight: 700; color: #fff; font-family: 'Times New Roman', Times, serif; }
    .sections { padding: 24px 32px; }

    /* ── Tailwind utilities for captured DOM content ── */
    .flex { display: flex; }
    .items-center { align-items: center; }
    .gap-2 { gap: 8px; }
    .gap-3 { gap: 12px; }
    .gap-4 { gap: 16px; }
    .mb-1 { margin-bottom: 4px; }
    .mb-2 { margin-bottom: 8px; }
    .mb-3 { margin-bottom: 12px; }
    .mb-4 { margin-bottom: 16px; }
    .mt-1 { margin-top: 4px; }
    .mt-2 { margin-top: 8px; }
    .mt-3 { margin-top: 12px; }
    .p-2 { padding: 8px; }
    .p-4 { padding: 16px; }
    .p-6 { padding: 24px; }
    .border { border: 1px solid #e2e8f0; }
    .border-slate-100 { border-color: #f1f5f9; }
    .border-slate-200 { border-color: #e2e8f0; }
    .rounded { border-radius: 4px; }
    .rounded-lg { border-radius: 8px; }
    .rounded-full { border-radius: 9999px; }
    .font-medium { font-weight: 500; }
    .font-semibold { font-weight: 600; }
    .font-bold { font-weight: 700; }
    .text-xs { font-size: 11px; }
    .text-sm { font-size: 13px; }
    .text-base { font-size: 15px; }
    .text-lg { font-size: 17px; }
    .text-xl { font-size: 20px; }
    .text-slate-400 { color: #94a3b8; }
    .text-slate-500 { color: #64748b; }
    .text-slate-600 { color: #475569; }
    .text-slate-700 { color: #334155; }
    .text-slate-900 { color: #0f172a; }
    .text-red-700 { color: #b91c1c; }
    .text-blue-700 { color: #1d4ed8; }
    .text-white { color: #ffffff; }
    .uppercase { text-transform: uppercase; }
    .tracking-wide { letter-spacing: 0.025em; }
    .whitespace-pre-wrap { white-space: pre-wrap; }
    .flex-wrap { flex-wrap: wrap; }
    .space-y-1 > * + * { margin-top: 4px; }
    .space-y-2 > * + * { margin-top: 8px; }
    .space-y-3 > * + * { margin-top: 12px; }
    .underline { text-decoration: underline; }
    .break-words { overflow-wrap: break-word; }
    .bg-slate-50 { background-color: #f8fafc; }
    .bg-emerald-600, .bg-teal-600 { background-color: #059669; }
    .bg-green-100 { background-color: #dcfce7; }
    .bg-red-100 { background-color: #fee2e2; }
    .bg-yellow-100 { background-color: #fef9c3; }
    .text-green-800 { color: #166534; }
    .text-red-800 { color: #991b1b; }
    .text-yellow-800 { color: #854d0e; }
    .w-10 { width: 40px; }
    .h-10 { height: 40px; }
    .justify-center { justify-content: center; }
    .inline-flex { display: inline-flex; }
    .section { margin-bottom: 24px; page-break-inside: avoid; }
    .section-header { display: flex; align-items: center; gap: 10px; border-left: 4px solid #14b8a6; padding-left: 12px; margin-bottom: 12px; }
    .section-number { display: inline-flex; align-items: center; justify-content: center; width: 26px; height: 26px; border-radius: 50%; background: #e2e8f0; color: #0f172a; font-size: 12px; font-weight: 700; flex-shrink: 0; }
    .section-title { font-family: 'Times New Roman', Times, serif; font-size: 14pt; font-weight: 700; color: #0f172a; }
    .section-body { background: #fff; border: 1px solid #e2e8f0; border-radius: 8px; padding: 20px 24px; }
    .section-body h1, .section-body h2, .section-body h3, .section-body h4 { font-family: 'Times New Roman', Times, serif; font-weight: 700; color: #0f172a; }
    .section-body h2 { font-size: 18pt; border-bottom: 2px solid #1e3a8a; padding-bottom: 4px; margin: 1.2rem 0 0.6rem; page-break-before: always; }
    .section-body h3 { font-size: 14pt; color: #1e293b; margin: 1rem 0 0.5rem; }
    .section-body h4 { font-size: 12pt; color: #334155; margin: 0.8rem 0 0.4rem; }
    .section-body p { margin-bottom: 0.7rem; font-size: 12pt; line-height: 1.8; }
    .section-body strong { color: #0f172a; font-weight: 700; }
    .section-body ul, .section-body ol { padding-left: 2.5rem; margin: 0.6rem 0; }
    .section-body li { margin-bottom: 0.4rem; font-size: 12pt; line-height: 1.75; }
    .section-body a { color: #1d4ed8; text-decoration: underline; }
    .section-body .legal-report-table-wrap { overflow-x: auto; }
    .section-body table { width: 100%; min-width: 0; border-collapse: collapse; margin: 12px 0; font-size: 11pt !important; table-layout: fixed; font-family: 'Times New Roman', Times, serif !important; }
    .section-body th { background: #1d4ed8; color: #fff !important; font-weight: 800; padding: 8px 10px; text-align: left; border: 1px solid #cbd5e1; font-size: 11pt !important; font-family: 'Times New Roman', Times, serif !important; white-space: normal; word-break: break-word; overflow-wrap: anywhere; vertical-align: top; }
    .section-body td { border: 1px solid #cbd5e1; padding: 8px 10px; color: #0f172a !important; vertical-align: top; word-break: break-word; overflow-wrap: anywhere; font-size: 11pt !important; font-family: 'Times New Roman', Times, serif !important; }
    .section-body blockquote { border-left: 4px solid #14b8a6; padding: 10px 14px; margin: 0.8rem 0; background: #f0fdfa; color: #0f766e; }
    .disclaimer-bold { background: #dc2626; border: 3px solid #b91c1c; padding: 20px 28px; margin: 16px 32px; border-radius: 8px; display: flex; gap: 14px; align-items: flex-start; page-break-inside: avoid; break-inside: avoid; -webkit-print-color-adjust: exact !important; print-color-adjust: exact !important; }
    .disclaimer-bold .disc-icon { color: #facc15; font-size: 28px; flex-shrink: 0; }
    .disclaimer-bold .disc-text { font-size: 14px; color: #ffffff; font-weight: 700; }
    .disclaimer-bold .disc-text strong { font-size: 16px; text-transform: uppercase; letter-spacing: 0.08em; color: #ffffff; display: block; margin-bottom: 6px; }
    .print-footer { display: none; position: fixed; left: 14mm; right: 14mm; bottom: 6mm; background: #ffffff; border-top: 1px solid #cbd5e1; padding: 4px 0 0; }
    .print-footer-row { display: flex; justify-content: space-between; gap: 18px; align-items: center; font-family: 'Times New Roman', Times, serif; font-size: 10pt; font-style: italic; color: #475569; }
    .print-footer-label { white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
    .print-footer-page::after { content: ''; }
    @media print {
      * { -webkit-print-color-adjust: exact !important; print-color-adjust: exact !important; color-adjust: exact !important; }
      body { print-color-adjust: exact; -webkit-print-color-adjust: exact; }
      .report-container { max-width: none; }
      .cover-page { page-break-after: always; break-after: page; }
      .report-header { print-color-adjust: exact; -webkit-print-color-adjust: exact; page-break-inside: avoid; break-inside: avoid; }
      .report-header .case-info-grid { -webkit-print-color-adjust: exact !important; print-color-adjust: exact !important; background: inherit; }
      .section-number { print-color-adjust: exact; -webkit-print-color-adjust: exact; }
      .section-body th { print-color-adjust: exact; -webkit-print-color-adjust: exact; }
      .section { page-break-inside: avoid; }
      .disclaimer-bold { page-break-inside: avoid; break-inside: avoid; -webkit-print-color-adjust: exact; print-color-adjust: exact; }
      .report-branding { page-break-inside: avoid; break-inside: avoid; }
      .disclaimer-bold + .report-branding { page-break-before: avoid; break-before: avoid; }
      .section-body .legal-report-table-wrap { overflow: visible; }
      .section-body table { min-width: 0 !important; width: 100% !important; table-layout: fixed !important; }
      .preview-notice { display: none; }
      .print-footer { display: none; }
      .print-footer-page::after { content: "Page " counter(page); }
    }
    @media (max-width: 768px) {
      .cover-page-grid { grid-template-columns: 1fr; }
      body { font-size: 13px; padding: 0 0 60px; }
      .report-container { max-width: 100%; }
      .cover-page-inner { padding: 18px 16px; }
      .cover-page h1 { font-size: 22px; }
      .cover-page-card-value { font-size: 12px; }
      .cover-page-note { font-size: 10px; padding: 10px 12px; }
      .report-header { padding: 18px 16px; }
      .report-header h1 { font-size: 20px; }
      .report-header .case-info-grid { grid-template-columns: 1fr 1fr; gap: 6px; }
      .report-header .case-info-grid .ci-value { font-size: 11px; }
      .sections { padding: 16px; }
      .section-title { font-size: 13px; }
      .section-body { padding: 14px 16px; }
      .section-body h2 { font-size: 1.1rem; }
      .section-body h3 { font-size: 11pt; }
      .section-body table { font-size: 9pt !important; }
      .section-body th, .section-body td { padding: 5px 6px; font-size: 9pt !important; }
      .disclaimer-bold { margin: 12px 16px; padding: 14px 16px; }
      .disclaimer-bold .disc-text { font-size: 11px; }
      .disclaimer-bold .disc-text strong { font-size: 12px; }
      .print-footer { padding: 6px 12px; }
      .print-footer-row { font-size: 8px; }
    }
  </style>
</head>
<body>
    ${notice}
    <section class="cover-page page-break">
      <div class="cover-page-inner">
        <p class="cover-page-kicker">Appeal Case Manager</p>
        <h1>${title}</h1>
        <p>${caseData?.title || "Case"}</p>
        <div class="cover-page-grid">
          <div class="cover-page-card"><div class="cover-page-card-label">Defendant</div><div class="cover-page-card-value">${defendantName}</div></div>
          <div class="cover-page-card"><div class="cover-page-card-label">Court / State</div><div class="cover-page-card-value">${meta}</div></div>
          <div class="cover-page-card"><div class="cover-page-card-label">Offence</div><div class="cover-page-card-value">${offenceLabel}</div></div>
          <div class="cover-page-card"><div class="cover-page-card-label">Sentence</div><div class="cover-page-card-value">${sentenceSummary}</div></div>
        </div>
        <div class="cover-page-note">NOT LEGAL ADVICE — This application is an educational research tool only and does NOT constitute legal advice. The creator is not a lawyer. All analysis and recommendations must be independently verified by a qualified Australian legal professional. Australian law only. No solicitor-client relationship is created.</div>
      </div>
    </section>
  <div class="report-container">
    <div class="report-header">
      <div class="header-row">
        <div>
          <div style="font-size:12px;text-transform:uppercase;letter-spacing:0.08em;font-weight:600;margin-bottom:4px;">Barrister Brief</div>
          <h1>${title}</h1>
          <div class="meta-line">${meta}</div>
          <div class="badge">BARRISTER BRIEF</div>
          <div class="gen-date">Generated: ${previewDate}</div>
        </div>
        <div>
          <div class="grounds-count">${grounds.length}</div>
          <div class="grounds-label">Ground${grounds.length !== 1 ? 's' : ''} Identified</div>
        </div>
      </div>
      <div class="case-info-grid">
        <div><div class="ci-label">Defendant</div><div class="ci-value">${defendantName}</div></div>
        <div><div class="ci-label">Offence</div><div class="ci-value">${offenceLabel}</div></div>
        <div><div class="ci-label">Sentence</div><div class="ci-value">${sentenceSummary}</div></div>
        <div><div class="ci-label">Documents</div><div class="ci-value">${documentsCount} files analysed</div></div>
        <div><div class="ci-label">Timeline Events</div><div class="ci-value">${eventsCount} events</div></div>
        <div><div class="ci-label">Source Reports</div><div class="ci-value">${reportsCount} reports referenced</div></div>
      </div>
    </div>
    ${tocHtml}
    <div class="sections">
      ${sections.map((section, idx) => {
        // Get individual section content from DOM
        const sectionMarkdownEl = document.querySelector(`[data-testid="barrister-section-markdown-${idx + 1}"]`);
        const sectionContent = sectionMarkdownEl ? sectionMarkdownEl.innerHTML : '';
        return `<div class="section">
          <div class="section-header">
            <span class="section-number">${idx + 1}</span>
            <span class="section-title">${section.title}</span>
          </div>
          <div class="section-body">${sectionContent.replace(/<th(?=[\s>])([^>]*?)style="[^"]*"/gi, '<th$1').replace(/<th(?=[\s>])/gi, '<th style="background:#1d4ed8;color:#ffffff;font-weight:800;"')}</div>
        </div>`;
      }).join('')}
      ${(() => {
        // Grounds of Merit detailed section
        const groundsSection = document.querySelector('[data-testid="barrister-grounds-detail-section"]');
        if (!groundsSection) return '';
        return `<div class="section" style="page-break-before:always;">
          <div class="section-header">
            <span class="section-number">&#9733;</span>
            <span class="section-title">Grounds of Merit — Detailed Assessment</span>
          </div>
          <div class="section-body">${groundsSection.innerHTML.replace(/<th(?=[\s>])([^>]*?)style="[^"]*"/gi, '<th$1').replace(/<th(?=[\s>])/gi, '<th style="background:#1d4ed8;color:#ffffff;font-weight:800;"')}</div>
        </div>`;
      })()}
      ${(() => {
        // Verification section
        const verifySection = document.querySelector('[data-testid="barrister-verification-section"]');
        if (!verifySection) return '';
        return `<div class="section">
          <div class="section-header">
            <span class="section-number">&#10003;</span>
            <span class="section-title">Verification and Review Status</span>
          </div>
          <div class="section-body">${verifySection.innerHTML}</div>
        </div>`;
      })()}
    </div>
  </div>
    <div class="disclaimer-bold">
      <div class="disc-icon">&#9888;</div>
      <div class="disc-text">
        <strong>NOT LEGAL ADVICE</strong>
        This application is an educational research tool only and does NOT constitute legal advice. It must NOT be relied upon as such. The creator of this application is not a lawyer. All analysis, findings, reports, and recommendations generated by this tool must be independently verified by a qualified Australian legal professional before any action is taken. This tool covers Australian law only. No solicitor-client relationship is created by using this service.
      </div>
    </div>
    <div style="text-align:center;margin:24px 32px;padding:16px 0;page-break-inside:avoid;" class="report-branding">
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
  <div class="print-footer">
    <div class="print-footer-row">
      <span class="print-footer-label">${previewFooterLabel}</span>
      <span class="print-footer-page"></span>
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
    openBarristerPreview("word");
  };

  const handleQuickBrief = async () => {
    try {
      toast.info("Opening Quick Brief...");
      const directUrl = await buildAuthUrl(`${API}/cases/${caseId}/reports/barrister-quick-brief`);
      window.open(directUrl, '_blank');
      toast.success("Quick Brief opened — use Share to save or print.");
    } catch (error) {
      toast.error("Failed to generate the Quick Brief PDF.");
    }
  };

  const handleBackToCase = () => {
    window.location.assign(`/cases/${caseId}`);
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-slate-50 flex items-center justify-center p-4" data-testid="barrister-view-loading">
        <div className="w-full max-w-2xl rounded-xl overflow-hidden shadow-lg border-2 border-teal-300">
          <div className="bg-teal-600 text-white px-6 py-4">
            <div className="flex items-center justify-between flex-wrap gap-3">
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 rounded-full bg-white/20 flex items-center justify-center">
                  <Loader2 className="w-5 h-5 animate-spin text-white" />
                </div>
                <div>
                  <p className="text-lg font-bold text-white">
                    {genElapsed < 10
                      ? "Connecting to Barrister Engine"
                      : genElapsed < 30
                      ? "Loading Case Materials"
                      : genElapsed < 60
                      ? "Retrieving Source Reports"
                      : "Preparing Barrister Brief"}
                  </p>
                  <p className="text-sm text-white/80">
                    {genElapsed < 10
                      ? "Fetching case data, grounds, documents and reports..."
                      : genElapsed < 30
                      ? "Reading all three foundational reports for synthesis..."
                      : genElapsed < 60
                      ? "Assembling the full case picture for the barrister..."
                      : "This may take a moment for complex cases..."}
                  </p>
                </div>
              </div>
              <div className="text-right">
                <span className="text-2xl font-mono font-bold text-white">
                  {genElapsed < 60 ? `${genElapsed}s` : `${Math.floor(genElapsed / 60)}m ${String(genElapsed % 60).padStart(2, '0')}s`}
                </span>
                <p className="text-xs text-white/60">elapsed</p>
              </div>
            </div>
          </div>
          <div className="bg-blue-50 px-6 py-3">
            <div className="flex items-center gap-3 mb-2">
              {[
                { label: "Connecting", active: genElapsed >= 0 },
                { label: "Loading", active: genElapsed >= 5 },
                { label: "Preparing", active: genElapsed >= 15 },
                { label: "Ready", active: false },
              ].map((step, i) => (
                <div key={i} className="flex items-center gap-1.5">
                  <div className={`w-2 h-2 rounded-full ${step.active ? 'bg-blue-600' : 'bg-slate-300'}`} />
                  <span className={`text-xs font-medium ${step.active ? 'text-blue-700' : 'text-slate-400'}`}>{step.label}</span>
                </div>
              ))}
            </div>
            <div className="w-full h-2 bg-blue-200 rounded-full overflow-hidden">
              <div
                className="h-full bg-blue-600 rounded-full transition-all duration-1000"
                style={{ width: `${Math.min(90, genElapsed * 2)}%` }}
              />
            </div>
          </div>
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
          <Button
            size="sm"
            onClick={handleBackToCase}
            className="bg-blue-700 text-white hover:bg-blue-600"
            data-testid="barrister-back-button"
          >
            <ArrowLeft className="w-4 h-4 mr-1" /> Back to Case
          </Button>

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
            <Button
              size="sm"
              onClick={handleQuickBrief}
              disabled={!isCompleted}
              className="bg-emerald-700 text-white hover:bg-emerald-600"
              data-testid="barrister-quick-brief-button"
            >
              <Zap className="w-4 h-4 mr-2" /> Quick Brief
            </Button>
            {isCompleted && report?.report_id && (
              <ReportTranslator caseId={caseId} reportId={report.report_id} />
            )}
          </div>
        </div>
      </header>

      <main className="max-w-5xl mx-auto px-4 sm:px-6 py-8">
        {(status === "locked" || status === "error" || status === "not_generated") && (
          <div className="bg-white border border-slate-200 rounded-2xl shadow-sm p-8" data-testid="barrister-locked-state">
            <div className="flex items-start gap-4">
              <AlertTriangle className="w-8 h-8 text-blue-600 flex-shrink-0 mt-1" />
              <div>
                <h1 className="text-2xl sm:text-3xl font-bold text-slate-900">
                  {status === "not_generated" ? "Barrister Brief Not Yet Generated" : "Barrister View Unavailable"}
                </h1>
                <p className="mt-3 text-slate-700 max-w-3xl">
                  {errorMessage || "This case does not yet have the three completed standard reports required to unlock the Barrister View."}
                </p>
                {status === "not_generated" && (
                  <p className="mt-2 text-sm text-slate-500">
                    Go to the Reports tab and select "Barrister View" then click "Generate Report" to create the brief.
                  </p>
                )}
              </div>
            </div>
          </div>
        )}

        {isGenerating && (
          <div className="rounded-xl overflow-hidden shadow-lg border-2 border-teal-300" data-testid="barrister-generating-state">
            <div className="bg-teal-600 text-white px-6 py-4">
              <div className="flex items-center justify-between flex-wrap gap-3">
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 rounded-full bg-white/20 flex items-center justify-center">
                    <Loader2 className="w-5 h-5 animate-spin text-white" />
                  </div>
                  <div>
                    <p className="text-lg font-bold text-white">
                      {genElapsed < 30
                        ? "Synthesising All Reports"
                        : genElapsed < 120
                        ? "Writing Barrister Analysis"
                        : genElapsed < 300
                        ? "Building Grounds of Merit Assessment"
                        : genElapsed < 600
                        ? "Constructing Issue Matrix"
                        : "Finalising Barrister Brief"}
                    </p>
                    <p className="text-sm text-white/80">
                      {genElapsed < 30
                        ? "Merging Quick Summary, Full Detailed, and Extensive Log into one brief..."
                        : genElapsed < 120
                        ? "AI is writing a comprehensive counsel-grade legal analysis..."
                        : genElapsed < 300
                        ? "Deep analysis of each ground with case law references..."
                        : genElapsed < 600
                        ? "Generating Attachment A — Issue Matrix & Attachment B — Conference Prep..."
                        : "Completing final sections. Complex briefs can take 10-20 minutes."}
                    </p>
                  </div>
                </div>
                <div className="text-right">
                  <span className="text-2xl font-mono font-bold text-white">
                    {genElapsed < 60 ? `${genElapsed}s` : `${Math.floor(genElapsed / 60)}m ${String(genElapsed % 60).padStart(2, '0')}s`}
                  </span>
                  <p className="text-xs text-white/60">elapsed</p>
                </div>
              </div>
            </div>
            <div className="bg-blue-50 px-6 py-3">
              <div className="flex items-center gap-3 mb-2">
                {[
                  { label: "Reading", active: genElapsed >= 0 },
                  { label: "Synthesising", active: genElapsed >= 30 },
                  { label: "Writing", active: genElapsed >= 120 },
                  { label: "Issue Matrix", active: genElapsed >= 300 },
                  { label: "Finalising", active: genElapsed >= 600 },
                ].map((step, i) => (
                  <div key={i} className="flex items-center gap-1.5">
                    <div className={`w-2 h-2 rounded-full ${step.active ? 'bg-blue-600' : 'bg-slate-300'}`} />
                    <span className={`text-xs font-medium ${step.active ? 'text-blue-700' : 'text-slate-400'}`}>{step.label}</span>
                  </div>
                ))}
              </div>
              <div className="w-full h-2 bg-blue-200 rounded-full overflow-hidden">
                <div
                  className="h-full bg-blue-600 rounded-full transition-all duration-1000"
                  style={{ width: `${Math.min(98, (genElapsed / 1200) * 100)}%` }}
                />
              </div>
            </div>
          </div>
        )}

        {isFailed && (
          <div className="bg-white border border-slate-200 rounded-2xl shadow-sm p-8" data-testid="barrister-failed-state">
            <div className="flex items-start gap-4">
              <AlertTriangle className="w-8 h-8 text-red-600 flex-shrink-0 mt-1" />
              <div className="flex-1">
                <h1 className="text-2xl sm:text-3xl font-bold text-slate-900">Barrister Brief generation failed</h1>
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
          <article className="bg-white rounded-xl border border-slate-300 overflow-hidden shadow-xl" data-testid="barrister-print-frame">
            {/* ===== COLOUR-CODED BARRISTER HEADER (matches other reports) ===== */}
            <div className="bg-teal-500 text-white p-6 sm:p-8" data-testid="barrister-hero">
              <div className="flex items-center justify-between mb-4 flex-wrap gap-3">
                <div>
                  <p className="text-sm uppercase tracking-wider font-semibold text-white mb-1">Barrister Brief</p>
                  <h1 className="text-2xl sm:text-3xl font-bold text-white" style={{ fontFamily: "'Times New Roman', Times, serif" }} data-testid="barrister-title">
                    {caseData?.title || "Barrister Brief"}
                  </h1>
                  <p className="text-sm text-white/90 mt-1 font-medium">{caseData?.court || "Court"} — {(caseData?.state || "NSW").toUpperCase()}</p>
                </div>
                <div className="text-right">
                  <p className="text-2xl font-bold text-white" data-testid="barrister-grounds-count">{grounds.length} Ground{grounds.length !== 1 ? "s" : ""}</p>
                  <p className="text-xs text-white/80 font-semibold">Identified</p>
                </div>
              </div>
              <div className="flex items-center gap-3 flex-wrap text-sm text-white/90 mb-5">
                <span className="flex items-center gap-1"><Clock className="w-3.5 h-3.5" /> Generated: {formatDate(report?.generated_at)}</span>
                <span className="text-sm text-white/80" data-testid="barrister-source-badge">Built from all {sourceReportMeta.length || 3} reports</span>
              </div>
              <div className="grid grid-cols-2 sm:grid-cols-3 gap-4 text-sm border-t border-white/20 pt-4" data-testid="barrister-summary-grid">
                <div>
                  <p className="text-xs text-white/70 uppercase tracking-wide mb-1">Defendant</p>
                  <p className="font-bold text-white" data-testid="barrister-summary-defendant">{caseData?.defendant_name || "Not recorded"}</p>
                </div>
                <div>
                  <p className="text-xs text-white/70 uppercase tracking-wide mb-1">Offence</p>
                  <p className="font-bold text-white" data-testid="barrister-summary-offence">{offenceLabel}</p>
                </div>
                <div className="col-span-2 sm:col-span-1">
                  <p className="text-xs text-white/70 uppercase tracking-wide mb-1">Sentence</p>
                  <p className="font-bold text-white" data-testid="barrister-summary-sentence">{sentenceSummary}</p>
                </div>
                <div>
                  <p className="text-xs text-white/70 uppercase tracking-wide mb-1">Documents</p>
                  <p className="font-bold text-white" data-testid="barrister-meta-documents">{documents.length} files analysed</p>
                </div>
                <div>
                  <p className="text-xs text-white/70 uppercase tracking-wide mb-1">Timeline Events</p>
                  <p className="font-bold text-white" data-testid="barrister-meta-timeline">{timeline.length} events</p>
                </div>
                <div>
                  <p className="text-xs text-white/70 uppercase tracking-wide mb-1">Source Reports</p>
                  <p className="font-bold text-white" data-testid="barrister-meta-source-reports">{sourceReportMeta.length || 3} reports referenced</p>
                </div>
              </div>
            </div>

            <div className="bg-red-700 px-4 py-3" data-testid="barrister-disclaimer-banner">
              <div className="flex items-start gap-2">
                <AlertTriangle className="w-4 h-4 text-yellow-300 shrink-0 mt-0.5" />
                <div>
                  <p className="text-xs font-bold text-white uppercase tracking-wide mb-0.5">NOT LEGAL ADVICE</p>
                  <p className="text-[10px] text-white/90 leading-snug">
                    This application is an educational research tool only and does NOT constitute legal advice. All analysis must be independently verified by a qualified Australian legal professional. Australian law only. No solicitor-client relationship is created.
                  </p>
                </div>
              </div>
            </div>

            {sections.length > 1 && (
              <div className="bg-slate-50/80 border-b border-slate-200 p-4 sm:p-5" data-testid="barrister-table-of-contents">
                <div className="flex items-center gap-2 mb-2">
                  <FileText className="w-4 h-4 text-slate-700" />
                  <p className="text-xs font-semibold text-slate-700 uppercase tracking-wide">
                    Contents ({sections.length} Sections)
                  </p>
                </div>
                <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-1.5">
                  {sections.map((section, index) => (
                    <button
                      key={section.id}
                      onClick={() => document.getElementById(section.id)?.scrollIntoView({ behavior: "smooth", block: "start" })}
                      className="text-left text-xs text-slate-700 hover:text-blue-700 transition-colors truncate"
                      data-testid={`barrister-toc-item-${index + 1}`}
                    >
                      <span className="font-semibold text-slate-900">{index + 1}.</span> {section.title}
                    </button>
                  ))}
                </div>
              </div>
            )}

            <div className="p-5 sm:p-6 md:p-8 space-y-6" data-testid="barrister-sections-wrapper">
              {sections.map((section, index) => (
                <article key={section.id} id={section.id} className="scroll-mt-24" data-testid={`barrister-section-${index + 1}`}>
                  <div className="border-l-4 border-teal-500 pl-4 mb-4">
                    <div className="flex items-center gap-3">
                      <span className="inline-flex items-center justify-center w-7 h-7 rounded-full bg-teal-50 text-teal-700 text-xs font-bold" data-testid={`barrister-section-number-${index + 1}`}>
                        {index + 1}
                      </span>
                      <h3
                        className="text-lg sm:text-xl font-bold text-teal-700 tracking-tight"
                        style={{ fontFamily: "'Times New Roman', Times, serif" }}
                        data-testid={`barrister-section-heading-${index + 1}`}
                      >
                        {section.title}
                      </h3>
                    </div>
                  </div>
                  <div className="bg-white rounded-lg border border-slate-200 p-6 sm:p-7 shadow-sm" data-testid={`barrister-section-body-${index + 1}`}>
                    <MarkdownBlock text={section.content} testId={`barrister-section-markdown-${index + 1}`} />
                  </div>
                </article>
              ))}

              {/* Per-Ground Barrister Blocks */}
              {grounds.length > 0 && (
                <div data-testid="barrister-grounds-detail-section">
                  <div className="border-l-4 border-teal-500 pl-4 mb-4">
                    <h3
                      className="text-lg sm:text-xl font-bold text-teal-700 tracking-tight"
                      style={{ fontFamily: "'Times New Roman', Times, serif" }}
                    >
                      Grounds of Merit — Detailed Assessment
                    </h3>
                  </div>
                  {grounds.map((ground) => (
                    <BarristerGroundBlock key={ground.ground_id} ground={ground} />
                  ))}
                </div>
              )}

              {/* Verification and Review Status Section */}
              {grounds.length > 0 && (
                <div data-testid="barrister-verification-section">
                  <div className="border-l-4 border-teal-500 pl-4 mb-4">
                    <h3
                      className="text-lg sm:text-xl font-bold text-teal-700 tracking-tight"
                      style={{ fontFamily: "'Times New Roman', Times, serif" }}
                    >
                      Verification and Review Status
                    </h3>
                  </div>
                  <div className="border border-slate-200 rounded-lg p-4 text-sm space-y-2 bg-slate-50">
                    <div className="text-slate-700">
                      Grounds requiring human review:{" "}
                      <span className="font-semibold text-slate-900">
                        {grounds.filter((g) => g?.requires_human_review).length}
                      </span>
                    </div>
                    <div className="text-slate-700">
                      Grounds pending investigation:{" "}
                      <span className="font-semibold text-slate-900">
                        {grounds.filter((g) => !g?.verification_status || g?.verification_status === "unverified" || g?.verification_status === "draft").length}
                      </span>
                    </div>
                    <div className="text-slate-700">
                      Investigated grounds:{" "}
                      <span className="font-semibold text-slate-900">
                        {grounds.filter((g) => g?.verification_status === "verified" || g?.verification_status === "reviewed").length}
                      </span>
                    </div>
                    <div className="text-xs text-slate-500 pt-2 border-t border-slate-200">
                      All authorities, statutory references, procedural pathways, and evidentiary propositions should be independently verified before reliance in advice, filing, or hearing preparation.
                    </div>
                  </div>
                </div>
              )}

              {/* Report Metadata Panel */}
              <ReportMetadataPanel
                metadata={report?.metadata || report?.content?.metadata}
                verificationStatus={report?.verification_status || report?.source_mode}
              />
            </div>

            {/* AI-analysis footer */}
            <div className="px-6 sm:px-10 py-4 bg-slate-50 border-t border-slate-200" data-testid="barrister-ai-footer">
              <p className="text-xs text-slate-400 leading-relaxed">
                AI-assisted analysis prepared for legal review. All grounds, authorities, and procedural issues should be independently verified before use in court or formal advice.
              </p>
            </div>

            <div className="bg-red-700 px-6 sm:px-10 py-6" data-testid="barrister-footer">
              <div className="flex items-start gap-4" data-testid="barrister-footer-disclaimer">
                <AlertTriangle className="w-8 h-8 text-yellow-300 flex-shrink-0 mt-0.5" />
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
          font-size: 0.95rem;
          line-height: 1.75;
          color: #0f172a;
        }
        .legal-report h1,
        .legal-report h2,
        .legal-report h3,
        .legal-report h4 {
          font-family: 'Times New Roman', Times, serif;
          font-weight: 700;
          color: #1e3a8a;
          margin: 1.2rem 0 0.5rem;
        }
        .legal-report h2 {
          font-size: 1.2rem;
          border-bottom: 2px solid #1e3a8a;
          padding-bottom: 0.35rem;
        }
        .legal-report h3 { font-size: 1.05rem; }
        .legal-report h4 { font-size: 0.95rem; color: #334155; }
        .legal-report p { margin-bottom: 0.7rem; }
        .legal-report strong { color: #0f172a; }
        .legal-report ul, .legal-report ol { margin: 0.6rem 0 0.8rem; padding-left: 1.3rem; }
        .legal-report li { margin-bottom: 0.35rem; }
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
          padding: 0.5rem 0.6rem;
          vertical-align: top;
          overflow-wrap: anywhere;
          font-size: 0.85rem;
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
          .legal-report { font-size: 10pt; }
          .legal-report-table-wrap { overflow: visible; }
        }
      `}</style>
    </div>
  );
}