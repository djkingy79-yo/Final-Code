/* DO NOT UNDO — ReportView section. All features in this file are approved and must be preserved. */
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
    sections.push({
      id: `report-section-${sections.length + 1}`,
      title: currentTitle,
      content,
    });
  };

  lines.forEach((line) => {
    const trimmed = line.trim();
    const markdownHeader = trimmed.match(/^#{1,3}\s+(.+)$/);
    const numberedHeader = trimmed.match(/^(?:\d{1,2}|[IVX]{1,5})[.)]\s+(.+)$/i);
    const boldHeader = trimmed.match(/^\*\*([^*]+)\*\*$/);

    if (markdownHeader || numberedHeader || boldHeader) {
      pushSection();
      currentTitle = (markdownHeader?.[1] || numberedHeader?.[1] || boldHeader?.[1] || "Analysis")
        .replace(/[\-:]+$/, "")
        .trim();
      currentLines = [];
      return;
    }

    currentLines.push(line);
  });

  pushSection();
  return sections.length > 0 ? sections : [{ id: "report-section-1", title: "Analysis", content: text }];
};

const MarkdownBlock = ({ text, testId }) => (
  <ReactMarkdown
    remarkPlugins={[remarkGfm]}
    components={{
      h1: ({ children }) => <h1 className="text-xl font-bold mt-6 mb-3 text-slate-900" style={{ fontFamily: "Crimson Pro, serif" }}>{children}</h1>,
      h2: ({ children }) => <h2 className="text-lg font-bold mt-5 mb-3 text-slate-900" style={{ fontFamily: "Crimson Pro, serif" }}>{children}</h2>,
      h3: ({ children }) => <h3 className="text-base font-semibold mt-4 mb-2 text-slate-900">{children}</h3>,
      p: ({ children }) => <p className="text-slate-700 leading-7 mb-3">{children}</p>,
      ul: ({ children }) => <ul className="list-disc ml-5 mb-3 space-y-1 text-slate-700">{children}</ul>,
      ol: ({ children }) => <ol className="list-decimal ml-5 mb-3 space-y-1 text-slate-700">{children}</ol>,
      li: ({ children }) => <li className="leading-7">{children}</li>,
      blockquote: ({ children }) => <blockquote className="border-l-4 border-indigo-300 pl-4 italic text-slate-700 my-3">{children}</blockquote>,
      table: ({ children }) => (
        <div className="overflow-x-auto rounded-lg border border-slate-200 my-4" data-testid={`${testId}-table-wrapper`}>
          <table className="min-w-full text-sm">{children}</table>
        </div>
      ),
      thead: ({ children }) => <thead className="bg-slate-100">{children}</thead>,
      th: ({ children }) => <th className="px-3 py-2 text-left font-semibold text-slate-800 border-b border-slate-200">{children}</th>,
      td: ({ children }) => <td className="px-3 py-2 align-top text-slate-700 border-b border-slate-100">{children}</td>,
      code: ({ children }) => <code className="text-xs bg-slate-100 text-slate-700 px-1.5 py-0.5 rounded">{children}</code>,
    }}
  >
    {text}
  </ReactMarkdown>
);

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

  const handlePrint = () => window.print();

  const handleExportPDF = async () => {
    try {
      toast.info("Generating PDF...");
      const response = await axios.get(`${API}/cases/${caseId}/reports/${reportId}/export-pdf`, {
        responseType: "blob",
      });

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
      const response = await axios.get(`${API}/cases/${caseId}/reports/${reportId}/export-docx`, {
        responseType: "blob",
      });

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
    return new Date(dateStr).toLocaleDateString("en-AU", {
      day: "numeric",
      month: "long",
      year: "numeric",
      hour: "2-digit",
      minute: "2-digit",
    });
  };

  const reportTypeConfig = {
    quick_summary: { label: "Quick Summary", cls: "bg-blue-100 text-blue-800 border-blue-200" },
    full_detailed: { label: "Full Detailed Analysis", cls: "bg-amber-100 text-amber-800 border-amber-200" },
    extensive_log: { label: "Extensive Log Report", cls: "bg-purple-100 text-purple-800 border-purple-200" },
  };

  const analysisText = report?.content?.analysis || "";
  const sections = useMemo(() => parseAnalysisSections(analysisText), [analysisText]);

  const documentsCount = report?.content?.document_count || 0;
  const eventsCount = report?.content?.event_count || 0;
  const strongGrounds = grounds.filter((g) => g.strength === "strong").length;

  const sentenceSummary = extractSentenceSummary(analysisText);
  const offenceLabel = caseData?.offence_type || titleFromSnake(caseData?.offence_category);

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

  const summaryItems = [
    { label: "Accused", value: caseData?.defendant_name || "N/A", icon: ShieldCheck, testId: "report-summary-accused" },
    { label: "Sentence", value: sentenceSummary, icon: Scale, testId: "report-summary-sentence" },
    { label: "Crime / Offence", value: offenceLabel, icon: Gavel, testId: "report-summary-offence" },
    { label: "Grounds of Merit", value: String(grounds.length), icon: Sparkles, testId: "report-summary-grounds" },
    {
      label: "Court & State",
      value: `${caseData?.court || "Court N/A"} • ${(caseData?.state || "NSW").toUpperCase()}`,
      icon: Scale,
      testId: "report-summary-court-state",
    },
  ];

  return (
    <div className="min-h-screen bg-[radial-gradient(circle_at_top,#eef2ff_0%,#f8fafc_40%,#f1f5f9_100%)]">
      <header className="bg-white/95 backdrop-blur border-b border-slate-200 sticky top-0 z-40 no-print" data-testid="report-header">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 py-4">
          <div className="flex items-center justify-between gap-3 flex-wrap">
            <Button variant="ghost" size="sm" onClick={() => navigate(`/cases/${caseId}`)} data-testid="back-btn">
              <ArrowLeft className="w-4 h-4 mr-1" />
              Back to Case
            </Button>
            <div className="flex items-center gap-2 flex-wrap">
              <Button
                variant="outline"
                size="sm"
                onClick={() => navigate(`/cases/${caseId}/reports/${reportId}/barrister`)}
                data-testid="barrister-view-btn"
              >
                <Eye className="w-4 h-4 mr-2" />
                Barrister View
              </Button>
              <Button variant="outline" size="sm" onClick={handlePrint} data-testid="print-btn">
                <Printer className="w-4 h-4 mr-2" />
                Print
              </Button>
              <Button
                variant="outline"
                size="sm"
                onClick={handleExportDOCX}
                className="bg-blue-50 text-blue-700 border-blue-200 hover:bg-blue-100"
                data-testid="export-docx-btn"
              >
                <FileText className="w-4 h-4 mr-2" />
                Export Word
              </Button>
              <Button size="sm" onClick={handleExportPDF} className="bg-slate-900 text-white hover:bg-slate-800" data-testid="export-pdf-btn">
                <Download className="w-4 h-4 mr-2" />
                Export PDF
              </Button>
            </div>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 sm:px-6 py-8">
        <div className="bg-white border border-slate-200 shadow-[0_20px_60px_-30px_rgba(15,23,42,0.35)] rounded-3xl p-5 sm:p-8 md:p-10" data-testid="report-content">
          <div className="text-center mb-8 pb-8 border-b border-slate-200">
            <div className="inline-flex items-center justify-center gap-3 mb-4 px-4 py-2 rounded-full bg-slate-100 border border-slate-200" data-testid="report-brand-pill">
              <Scale className="w-5 h-5 text-slate-900" />
              <span className="text-sm font-semibold text-slate-900">Appeal Case Manager</span>
            </div>
            <h1 className="text-3xl md:text-5xl font-bold text-slate-900 tracking-tight mb-4" style={{ fontFamily: "Crimson Pro, serif" }} data-testid="report-title">
              {report?.title}
            </h1>
            <div className="flex items-center justify-center gap-3 flex-wrap">
              <Badge variant="outline" className={reportTypeConfig[report?.report_type]?.cls || reportTypeConfig.quick_summary.cls} data-testid="report-type-badge">
                {reportTypeConfig[report?.report_type]?.label || report?.report_type}
              </Badge>
              {report?.content?.aggressive_mode && (
                <Badge variant="outline" className="bg-rose-100 text-rose-800 border-rose-200" data-testid="report-aggressive-mode-badge">
                  Aggressive Mode
                </Badge>
              )}
              <span className="text-sm text-slate-500" data-testid="report-generated-date">Generated: {formatDate(report?.generated_at)}</span>
            </div>
          </div>

          <section className="mb-8 rounded-2xl border border-indigo-200 bg-gradient-to-r from-indigo-50 via-white to-amber-50 p-5 sm:p-6" data-testid="report-top-summary-box">
            <div className="flex items-center gap-2 mb-4">
              <Sparkles className="w-5 h-5 text-indigo-700" />
              <h2 className="text-lg font-bold text-slate-900" style={{ fontFamily: "Crimson Pro, serif" }}>
                Command Summary
              </h2>
            </div>
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
              {summaryItems.map((item) => (
                <SummaryPill key={item.label} label={item.label} value={item.value} icon={item.icon} testId={item.testId} />
              ))}
            </div>
          </section>

          <section className="mb-8 rounded-2xl border border-slate-200 bg-slate-900 text-white p-5 sm:p-6" data-testid="premium-value-architecture-section">
            <p className="text-[11px] uppercase tracking-widest text-blue-300 font-semibold mb-2">Premium Report Architecture</p>
            <h2 className="text-xl font-bold mb-4" style={{ fontFamily: "Crimson Pro, serif" }}>
              Built for strategic legal action — not just plain text
            </h2>
            <div className="grid md:grid-cols-2 xl:grid-cols-4 gap-3">
              <div className="rounded-xl border border-blue-800/60 bg-blue-950/40 p-3">
                <p className="text-xs font-semibold text-blue-200 mb-1">Comparative Sentencing</p>
                <p className="text-[12px] text-slate-200">Before/after reduction pathways with practical appeal outcomes.</p>
              </div>
              <div className="rounded-xl border border-yellow-700/60 bg-yellow-900/30 p-3">
                <p className="text-xs font-semibold text-yellow-100 mb-1">Similar Case Search Options</p>
                <p className="text-[12px] text-slate-200">AustLII-ready query packs and jurisdiction filters.</p>
              </div>
              <div className="rounded-xl border border-emerald-700/60 bg-emerald-900/30 p-3">
                <p className="text-xs font-semibold text-emerald-100 mb-1">How to Argue Grounds</p>
                <p className="text-[12px] text-slate-200">Lead propositions, likely prosecution responses, and rebuttal direction.</p>
              </div>
              <div className="rounded-xl border border-purple-700/60 bg-purple-900/30 p-3">
                <p className="text-xs font-semibold text-purple-100 mb-1">Next Steps Playbook</p>
                <p className="text-[12px] text-slate-200">72-hour, 7-day, and 28-day execution plan with priorities.</p>
              </div>
            </div>
          </section>

          {sections.length > 0 && (
            <section className="mb-8 rounded-2xl border border-slate-200 p-5 bg-slate-50" data-testid="report-table-of-contents">
              <div className="flex items-center gap-2 mb-3">
                <ListOrdered className="w-4 h-4 text-slate-700" />
                <h3 className="font-semibold text-slate-900" style={{ fontFamily: "Crimson Pro, serif" }}>
                  Table of Contents
                </h3>
              </div>
              <div className="grid md:grid-cols-2 gap-2">
                {sections.map((section, idx) => (
                  <button
                    key={section.id}
                    onClick={() => scrollToSection(section.id)}
                    className="text-left px-3 py-2 rounded-lg border border-slate-200 bg-white hover:bg-indigo-50 hover:border-indigo-300 text-sm text-slate-700 transition-colors"
                    data-testid={`report-toc-item-${idx + 1}`}
                  >
                    <span className="font-semibold text-slate-900 mr-1">{idx + 1}.</span>
                    {section.title}
                  </button>
                ))}
              </div>
            </section>
          )}

          <section className="space-y-5" data-testid="report-full-analysis-section">
            {sections.map((section, idx) => (
              <article key={section.id} id={section.id} className="rounded-2xl border border-slate-200 p-4 sm:p-6 bg-gradient-to-b from-white to-slate-50/40 shadow-sm">
                <div className="flex items-center gap-2 mb-3 pb-3 border-b border-slate-200">
                  <div className="w-7 h-7 rounded-full bg-indigo-100 text-indigo-700 text-sm font-bold flex items-center justify-center">
                    {idx + 1}
                  </div>
                  <h3 className="text-lg font-semibold text-slate-900" style={{ fontFamily: "Crimson Pro, serif" }} data-testid={`report-section-heading-${idx + 1}`}>
                    {section.title}
                  </h3>
                </div>

                <div className="text-slate-700" data-testid={`report-section-content-${idx + 1}`}>
                  <MarkdownBlock text={section.content} testId={`report-section-md-${idx + 1}`} />
                </div>

                <button
                  onClick={() => window.scrollTo({ top: 0, behavior: "smooth" })}
                  className="mt-2 inline-flex items-center gap-1 text-xs text-indigo-700 hover:text-indigo-900"
                  data-testid={`report-back-to-top-${idx + 1}`}
                >
                  <ChevronRight className="w-3 h-3 rotate-[-90deg]" />
                  Back to top
                </button>
              </article>
            ))}
          </section>

          <footer className="mt-12 pt-8 border-t border-slate-200 text-center text-sm text-slate-500" data-testid="report-footer">
            <p>This is a full in-browser report view — no PDF download required to read all sections.</p>
            <p className="font-medium">Prepared by Appeal Case Manager for legal review support.</p>
          </footer>
        </div>
      </main>

      <style>{`
        @media print {
          .no-print {
            display: none !important;
          }
        }
      `}</style>
    </div>
  );
};

const SummaryPill = ({ label, value, icon: Icon, testId }) => (
  <div className="rounded-xl border border-slate-200 bg-white p-3" data-testid={testId}>
    <div className="flex items-center gap-2 mb-1.5">
      <Icon className="w-4 h-4 text-indigo-600" />
      <p className="text-[11px] uppercase tracking-wide text-slate-500">{label}</p>
    </div>
    <p className="text-sm font-semibold text-slate-900 break-words">{value}</p>
  </div>
);

export default ReportView;