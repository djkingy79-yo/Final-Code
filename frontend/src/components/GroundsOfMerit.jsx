/* ========================================================================
   DO NOT UNDO — ENTIRE FILE PROTECTED
   All features, functions, styles, and content in this file are approved
   and must be preserved. Do not remove, rename, or refactor any code.
   ======================================================================== */
import { useState } from "react";
import { 
  Scale, Trash2, Search, Loader2, 
  AlertTriangle, CheckCircle, XCircle, Sparkles,
  BookOpen, Gavel, FileText, Lock, CreditCard, ExternalLink, Printer, Download
} from "lucide-react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import { renderToStaticMarkup } from "react-dom/server";
import { Button } from "./ui/button";
import { Input } from "./ui/input";
import { Card, CardContent } from "./ui/card";
import { Badge } from "./ui/badge";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
} from "./ui/dialog";
import { ScrollArea } from "./ui/scroll-area";
import { toast } from "sonner";
import PaymentModal from "./PaymentModal";
import StrengthBadge from "./StrengthBadge";
import VerificationBadge from "./VerificationBadge";
import LegitimacyPanel from "./LegitimacyPanel";
import EvidenceSummary from "./EvidenceSummary";

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

const GROUND_TYPE_COLORS = {
  procedural_error: "bg-blue-50 text-blue-700 border-blue-200",
  fresh_evidence: "bg-emerald-50 text-emerald-700 border-emerald-200",
  miscarriage_of_justice: "bg-red-50 text-red-700 border-red-200",
  sentencing_error: "bg-blue-50 text-blue-700 border-blue-200",
  judicial_error: "bg-purple-50 text-purple-700 border-purple-200",
  ineffective_counsel: "bg-orange-50 text-orange-700 border-orange-200",
  prosecution_misconduct: "bg-rose-50 text-rose-700 border-rose-200",
  jury_irregularity: "bg-indigo-50 text-indigo-700 border-indigo-200",
  constitutional_violation: "bg-slate-50 text-slate-700 border-slate-200",
  other: "bg-gray-50 text-gray-700 border-gray-200"
};

const STRENGTH_CONFIG = {
  strong: { icon: CheckCircle, color: "text-emerald-600", bg: "bg-emerald-100", label: "Strong" },
  moderate: { icon: AlertTriangle, color: "text-red-600", bg: "bg-blue-100", label: "Moderate" },
  weak: { icon: XCircle, color: "text-red-600", bg: "bg-red-100", label: "Weak" }
};

const STATUS_CONFIG = {
  identified: { color: "bg-blue-100 text-blue-700", label: "Identified" },
  investigating: { color: "bg-blue-100 text-blue-700", label: "Investigating" },
  confirmed: { color: "bg-emerald-100 text-emerald-700", label: "Confirmed" },
  rejected: { color: "bg-red-100 text-red-700", label: "Rejected" },
  needs_review: { color: "bg-amber-100 text-amber-700", label: "Needs Review" }
};

const LegitimacyBreakdown = ({ scores }) => {
  if (!scores) return null;
  return (
    <div data-testid="legitimacy-breakdown" className="mt-2 text-xs bg-slate-100 p-3 rounded-lg border border-slate-200">
      <div className="grid grid-cols-3 gap-2 mb-1">
        <div><span className="text-slate-500">Legal:</span> <span className="font-semibold">{scores.legal_score}/3</span></div>
        <div><span className="text-slate-500">Evidence:</span> <span className="font-semibold">{scores.evidence_score}/3</span></div>
        <div><span className="text-slate-500">Viability:</span> <span className="font-semibold">{scores.viability_score}/3</span></div>
      </div>
      <div className="font-bold text-slate-700">Total: {scores.total_score}/9</div>
      {scores.confidence_note && (
        <p className="italic text-slate-500 mt-1 leading-tight">{scores.confidence_note}</p>
      )}
    </div>
  );
};

const UnverifiedBadge = () => (
  <span className="ml-1 text-[10px] px-1.5 py-0.5 rounded bg-amber-100 text-amber-700 font-medium">
    UNVERIFIED
  </span>
);

const SourceModeBadge = ({ sourceMode }) => {
  const value = String(sourceMode || "legacy").toLowerCase();

  const classes = {
    derived: "border-green-700 text-green-700",
    ai_generated: "border-blue-700 text-blue-700",
    manual: "border-purple-700 text-purple-700",
    imported: "border-slate-700 text-slate-700",
    legacy: "border-yellow-700 text-yellow-700",
  };

  const labels = {
    derived: "Pipeline-derived",
    ai_generated: "AI-generated",
    manual: "Manual",
    imported: "Imported",
    legacy: "Legacy",
  };

  return (
    <span className={`px-2 py-1 rounded text-xs font-medium border ${classes[value] || classes.legacy}`} data-testid="source-mode-badge">
      {labels[value] || "Unknown source"}
    </span>
  );
};

const GroundProvenancePanel = ({ ground }) => {
  if (!ground) return null;

  const supportingEvidence = Array.isArray(ground.supporting_evidence)
    ? ground.supporting_evidence
    : [];

  const lawSections = Array.isArray(ground.law_sections)
    ? ground.law_sections
    : [];

  const similarCases = Array.isArray(ground.similar_cases)
    ? ground.similar_cases
    : [];

  const sourceMode = ground.source_mode || "legacy";
  const verificationStatus = ground.verification_status || "unverified";

  return (
    <div className="mt-3 rounded border p-3 text-xs" data-testid="ground-provenance-panel">
      <div className="font-semibold mb-1">Ground Provenance</div>
      <div>Source mode: {sourceMode}</div>
      <div>Verification status: {verificationStatus}</div>
      <div>Supporting evidence items: {supportingEvidence.length}</div>
      <div>Law sections linked: {lawSections.length}</div>
      <div>Comparable cases linked: {similarCases.length}</div>
      <div>Human review required: {ground.requires_human_review ? "Yes" : "No"}</div>
    </div>
  );
};

const GroundConfidenceNote = ({ ground }) => {
  const note =
    ground?.legitimacy_scores?.confidence_note ||
    ground?.deep_analysis?.confidence_note ||
    "";

  if (!note) return null;

  return (
    <div className="mt-2 text-xs opacity-80" data-testid="ground-confidence-note">
      {note}
    </div>
  );
};

const GroundPipelineStatus = ({ ground }) => {
  const isPipelineBacked =
    ground?.source_mode === "derived" ||
    ground?.source_mode === "ai_generated";

  return (
    <div className="mt-2 text-xs" data-testid="ground-pipeline-status">
      {isPipelineBacked ? (
        <span className="text-green-700 font-medium">
          Pipeline-backed ground
        </span>
      ) : (
        <span className="text-yellow-700 font-medium">
          Legacy or manually created ground
        </span>
      )}
    </div>
  );
};

const GroundsOfMerit = ({ 
  grounds, 
  groundsCount,
  isUnlocked,
  unlockPrice,
  caseId,
  onInvestigate, 
  onDelete, 
  investigating,
  selectedGround,
  setSelectedGround,
  onPaymentSuccess
}) => {
  const [showDetailDialog, setShowDetailDialog] = useState(false);
  const [detailGround, setDetailGround] = useState(null);
  const [showPaymentModal, setShowPaymentModal] = useState(false);
  /* DO NOT UNDO — Search box state for each ground. Uses object to track per-ground search visibility */
  const [searchOpen, setSearchOpen] = useState({});
  const [searchTerms, setSearchTerms] = useState({});

  const toggleSearch = (groundId) => {
    setSearchOpen(prev => ({ ...prev, [groundId]: !prev[groundId] }));
  };

  const handleCaselawSearch = (groundId, groundTitle) => {
    const query = searchTerms[groundId] || groundTitle;
    const encoded = encodeURIComponent(query);
    window.open(`https://www.austlii.edu.au/cgi-bin/sinosrch.cgi?method=auto&query=${encoded}`, '_blank');
  };

  const openGroundDetail = (ground) => {
    setDetailGround(ground);
    setShowDetailDialog(true);
  };

  const formatDate = (dateStr) => {
    if (!dateStr) return "N/A";
    return new Date(dateStr).toLocaleDateString("en-AU", {
      day: "numeric",
      month: "short",
      year: "numeric"
    });
  };

  // Format the analysis content with sections
  /* DO NOT UNDO — formatAnalysis renders investigation results with clickable links */
  const formatAnalysis = (analysis) => {
    if (!analysis) return null;
    return (
      <div className="legal-report prose prose-sm max-w-none">
        <ReactMarkdown 
          remarkPlugins={[remarkGfm]}
          components={{
            a: ({ href, children }) => (
              <a href={href} target="_blank" rel="noopener noreferrer" className="text-blue-600 underline hover:text-blue-800 break-words font-medium">{children}</a>
            ),
            table: ({ children }) => (
              <div className="overflow-x-auto my-4 border border-slate-300 rounded-xl"><table className="w-full min-w-[640px] border-collapse border border-slate-300 table-fixed">{children}</table></div>
            ),
            th: ({ children }) => (
              <th className="border border-slate-300 bg-blue-700 px-3 py-2 text-left text-sm font-extrabold text-white whitespace-normal break-normal align-top">{children}</th>
            ),
            td: ({ children }) => (
              <td className="border border-slate-300 px-3 py-2 text-sm break-words align-top">{children}</td>
            ),
          }}
        >{analysis}</ReactMarkdown>
      </div>
    );
  };

  const buildGroundsPreviewHtml = () => {
    const contentMarkup = renderToStaticMarkup(
      <div className="grounds-export-shell">
        <div className="grounds-export-header">
          <p className="grounds-export-kicker">Grounds of Merit</p>
          <h1>Detailed Grounds Analysis</h1>
          <p>Full grounds file including descriptions, supporting evidence, legal references, similar cases, and deep investigation analysis.</p>
        </div>

        {grounds.map((ground, index) => (
          <section key={ground.ground_id || index} className="grounds-export-section">
            <div className="grounds-export-title-wrap">
              <h2>{`Ground ${index + 1}: ${ground.title}`}</h2>
              <div className="grounds-export-meta">
                <span>{GROUND_TYPE_LABELS[ground.ground_type] || ground.ground_type}</span>
                <span>{STATUS_CONFIG[ground.status]?.label || ground.status || "Identified"}</span>
                <span>{STRENGTH_CONFIG[ground.strength]?.label || ground.strength || "Moderate"}</span>
              </div>
            </div>

            <p className="grounds-export-description">{ground.description}</p>

            {ground.supporting_evidence?.length > 0 && (
              <div className="grounds-export-block">
                <h3>Supporting Evidence</h3>
                <ul>
                  {ground.supporting_evidence.map((item, idx) => <li key={idx}>{item}</li>)}
                </ul>
              </div>
            )}

            {ground.law_sections?.length > 0 && (
              <div className="grounds-export-block">
                <h3>Relevant Law Sections</h3>
                <ul>
                  {ground.law_sections.map((section, idx) => (
                    <li key={idx}>{`s.${section.section} ${section.act} (${section.jurisdiction || "NSW"})`}</li>
                  ))}
                </ul>
              </div>
            )}

            {ground.similar_cases?.length > 0 && (
              <div className="grounds-export-block">
                <h3>Similar Cases</h3>
                <ul>
                  {ground.similar_cases.map((caseItem, idx) => (
                    <li key={idx}>{caseItem.citation ? `${caseItem.case_name} — ${caseItem.citation}` : caseItem.case_name}</li>
                  ))}
                </ul>
              </div>
            )}

            {(ground.deep_analysis?.full_analysis || ground.analysis) && (
              <div className="grounds-export-analysis">
                <h3>Deep Investigation Analysis</h3>
                <div className="legal-report">
                  <ReactMarkdown
                    remarkPlugins={[remarkGfm]}
                    components={{
                      table: ({ children }) => (
                        <div className="legal-report-table-wrap"><table>{children}</table></div>
                      )
                    }}
                  >
                    {ground.deep_analysis?.full_analysis || ground.analysis}
                  </ReactMarkdown>
                </div>
              </div>
            )}
          </section>
        ))}

        <div className="grounds-export-disclaimer">
          NOT LEGAL ADVICE — This material is an educational tool only. All analysis and recommendations must be independently verified by a qualified Australian legal professional.
        </div>
        <div style={{textAlign:'center', margin:'24px 0', padding:'16px 0'}}>
          <p style={{fontSize:'12px', fontWeight:700, color:'#334155', margin:'0 0 10px'}}>Created and Designed by Deb King</p>
          <div style={{display:'inline-flex', alignItems:'center', gap:'10px'}}>
            <div style={{width:'36px', height:'36px', background:'#dc2626', borderRadius:'6px', display:'flex', alignItems:'center', justifyContent:'center'}}>
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="white" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="m16 16 3-8 3 8c-.87.65-1.92 1-3 1s-2.13-.35-3-1Z"/><path d="m2 16 3-8 3 8c-.87.65-1.92 1-3 1s-2.13-.35-3-1Z"/><path d="M7 21h10"/><path d="M12 3v18"/><path d="M3 7h2c2 0 5-1 7-2 2 1 5 2 7 2h2"/></svg>
            </div>
            <div style={{textAlign:'left'}}>
              <p style={{margin:0, fontWeight:700, fontSize:'13px', color:'#0f172a'}}>Appeal Case Manager</p>
              <p style={{margin:0, fontSize:'11px', color:'#64748b'}}>Founded by Debra King</p>
              <p style={{margin:0, fontSize:'11px', color:'#64748b'}}>Criminal Appeal Research Tool — Australian Law Only</p>
            </div>
          </div>
        </div>
      </div>
    );

    return `<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>Grounds of Merit Export</title>
  <style>
    @page { size: A4; margin: 12mm; }
    body { margin: 0; background: #f8fafc; color: #0f172a; font-family: Arial, sans-serif; font-size: 12px; }
    .grounds-export-shell { max-width: 1000px; margin: 0 auto; background: #ffffff; padding: 28px; }
    .grounds-export-brand { text-align: center; font-size: 16px; font-weight: 700; margin-bottom: 14px; }
    .grounds-export-header { border-bottom: 2px solid #cbd5e1; padding-bottom: 16px; margin-bottom: 24px; }
    .grounds-export-kicker { text-transform: uppercase; letter-spacing: 0.18em; color: #1d4ed8; font-weight: 800; font-size: 11px; margin: 0 0 8px; }
    .grounds-export-header h1 { margin: 0 0 8px; font-size: 26px; }
    .grounds-export-header p { margin: 0; line-height: 1.5; font-size: 12px; }
    .grounds-export-section { padding: 18px 0; border-bottom: 1px solid #e2e8f0; }
    .grounds-export-title-wrap h2 { margin: 0 0 8px; font-size: 20px; }
    .grounds-export-meta { display: flex; flex-wrap: wrap; gap: 8px; margin-bottom: 12px; }
    .grounds-export-meta span { background: #dbeafe; color: #1d4ed8; padding: 5px 9px; border-radius: 999px; font-size: 11px; font-weight: 700; }
    .grounds-export-description { margin: 0 0 12px; line-height: 1.55; font-size: 12px; }
    .grounds-export-block h3, .grounds-export-analysis h3 { margin: 0 0 8px; font-size: 15px; }
    .grounds-export-block ul { margin: 0 0 12px; padding-left: 18px; line-height: 1.45; font-size: 11px; }
    .grounds-export-analysis { margin-top: 14px; }
    .grounds-export-disclaimer { margin-top: 18px; border: 2px solid #dc2626; padding: 14px; font-weight: 700; line-height: 1.45; font-size: 11px; }
    .legal-report p { line-height: 1.5; margin: 0 0 8px; font-size: 11px; }
    .legal-report h1, .legal-report h2, .legal-report h3, .legal-report h4 { color: #1d4ed8; }
    .legal-report-table-wrap { overflow-x: auto; -webkit-overflow-scrolling: touch; }
    .legal-report table { width: 100%; min-width: 0; border-collapse: collapse; table-layout: fixed; font-size: 10px; }
    .legal-report th, .legal-report td { border: 1px solid #cbd5e1; padding: 6px 7px; vertical-align: top; }
    .legal-report th { background: #1d4ed8; color: #ffffff; font-weight: 800; white-space: normal; word-break: break-word; overflow-wrap: anywhere; }
    .legal-report td { overflow-wrap: anywhere; word-break: break-word; }
    .print-footer { position: fixed; left: 0; right: 0; bottom: 0; background: #ffffff; border-top: 1px solid #cbd5e1; padding: 8px 24px 10px; }
    .print-footer-row { display: flex; justify-content: space-between; gap: 16px; align-items: center; font-size: 10px; color: #475569; }
    .print-footer-label { white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
    .print-footer-page-print::after { content: ''; }
    @media print {
      body { background: #ffffff; }
      .grounds-export-shell { max-width: none; padding: 0; }
      .legal-report-table-wrap { overflow: visible; }
      .print-footer-page-print::after { content: "Page " counter(page); }
    }
  </style>
</head>
<body>${contentMarkup}
  <div class="print-footer">
    <div class="print-footer-row">
      <span class="print-footer-label">Criminal Appeal Case Management - Grounds of Merit - ${new Date().toLocaleDateString('en-AU', {day:'numeric',month:'long',year:'numeric'})}</span>
      <span class="print-footer-page"><span class="print-footer-page-print"></span></span>
    </div>
  </div>
</body>
</html>`;
  };

  const openGroundsPreview = (mode = "print") => {
    const html = buildGroundsPreviewHtml();
    localStorage.setItem(
      "document-preview-payload",
      JSON.stringify({
        html,
        mode,
        title: "Grounds of Merit Export",
        source: "grounds",
        returnTo: `/cases/${caseId}`,
        createdAt: Date.now(),
      })
    );

    const previewUrl = `${window.location.origin}/document-preview?mode=${mode}`;
    window.location.assign(previewUrl);
  };

  const exportGroundsWord = () => {
    const html = buildGroundsPreviewHtml();
    const blob = new Blob([html], { type: "application/msword" });
    const url = window.URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = `grounds_of_merit_${caseId}.doc`;
    document.body.appendChild(link);
    link.click();
    link.remove();
    setTimeout(() => window.URL.revokeObjectURL(url), 10000);
  };

  const buildSingleGroundHtml = (ground) => {
    const analysis = ground.deep_analysis?.full_analysis || ground.analysis || "";
    const escHtml = (s) => (s || "").replace(/&/g,"&amp;").replace(/</g,"&lt;").replace(/>/g,"&gt;");
    return `<!DOCTYPE html>
<html lang="en"><head><meta charset="UTF-8" /><title>Ground: ${escHtml(ground.title)}</title>
<style>
@page{size:A4;margin:12mm}body{font-family:Arial,sans-serif;font-size:12px;color:#0f172a;padding:28px;line-height:1.6}
h1{font-size:22px;margin:0 0 6px}h2{font-size:16px;margin:16px 0 8px;border-bottom:2px solid #1d4ed8;padding-bottom:4px}
.meta{display:flex;gap:8px;margin:8px 0 16px}.meta span{background:#dbeafe;color:#1d4ed8;padding:4px 10px;border-radius:999px;font-size:11px;font-weight:700}
.desc{margin:0 0 14px;font-size:13px}ul{padding-left:18px;margin:0 0 12px}li{margin-bottom:4px;font-size:12px}
.case-box{background:#eff6ff;border:1px solid #93c5fd;padding:8px 12px;border-radius:6px;margin-bottom:6px;font-size:12px}
.analysis{margin-top:16px;white-space:pre-wrap;font-size:12px}
table{border-collapse:collapse;width:100%;margin:12px 0}th,td{border:1px solid #cbd5e1;padding:6px 10px;text-align:left;font-size:11px}th{background:#dbeafe;font-weight:700}
.disclaimer{background:#fef2f2;border:3px solid #ef4444;padding:14px 18px;border-radius:8px;margin-top:28px;page-break-inside:avoid}
.disclaimer strong{font-size:13px;text-transform:uppercase;color:#dc2626;display:block;margin-bottom:4px}
.disclaimer p{font-size:11px;color:#1e293b;margin:0;line-height:1.5}
@media print{body{padding:0}}
</style></head><body>
<h1>Ground of Merit: ${escHtml(ground.title)}</h1>
<div class="meta"><span>${escHtml((ground.ground_type || 'other').replace(/_/g,' '))}</span><span>${escHtml(ground.strength || 'Moderate')}</span><span>${escHtml(ground.status || 'Identified')}</span></div>
<p class="desc">${escHtml(ground.description)}</p>
${(ground.supporting_evidence||[]).length ? '<h2>Supporting Evidence</h2><ul>' + ground.supporting_evidence.map(e=>'<li>'+escHtml(e)+'</li>').join('') + '</ul>' : ''}
${(ground.law_sections||[]).length ? '<h2>Relevant Law Sections</h2><ul>' + ground.law_sections.map(s=>'<li>s.'+escHtml(s.section)+' '+escHtml(s.act)+' ('+(s.jurisdiction||'NSW')+')</li>').join('') + '</ul>' : ''}
${(ground.similar_cases||[]).length ? '<h2>Similar Cases</h2>' + ground.similar_cases.map(c=>'<div class="case-box"><strong>'+escHtml(c.case_name)+'</strong>'+(c.citation ? ' &mdash; '+escHtml(c.citation) : '')+'</div>').join('') : ''}
${analysis ? '<h2>Deep Investigation Analysis</h2><div class="analysis">' + analysis + '</div>' : ''}
<div class="disclaimer"><strong>NOT LEGAL ADVICE</strong><p>This application is an educational research tool only and does NOT constitute legal advice. All analysis must be independently verified by a qualified Australian legal professional. Australian law only. No solicitor-client relationship is created.</p></div>
<div style="text-align:center;margin:24px 0;padding:16px 0;">
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
</body></html>`;
  };

  const handleGroundPrint = () => {
    if (!detailGround) return;
    const html = buildSingleGroundHtml(detailGround);
    const w = window.open("", "_blank");
    if (w) { w.document.write(html); w.document.close(); w.print(); }
  };

  const handleGroundPDF = () => {
    if (!detailGround) return;
    const html = buildSingleGroundHtml(detailGround);
    const w = window.open("", "_blank");
    if (w) {
      w.document.write(html);
      w.document.close();
      toast.success("PDF view opened — use Print / Save as PDF to download.");
    }
  };

  return (
    <div className="space-y-4" data-testid="grounds-container">
      {/* Paywall Banner when not unlocked */}
      {!isUnlocked && groundsCount > 0 && (
        <Card className="bg-gradient-to-r from-blue-50 to-orange-50 border-blue-200">
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-4">
                <div className="w-12 h-12 bg-blue-100 rounded-full flex items-center justify-center">
                  <Lock className="w-6 h-6 text-red-600" />
                </div>
                <div>
                  <h3 className="font-semibold text-slate-900 text-lg" style={{ fontFamily: 'Crimson Pro, serif' }}>
                    {groundsCount} Grounds of Merit Found!
                  </h3>
                  <p className="text-slate-600">
                    Unlock to see full details, evidence, and deep analysis for each ground.
                  </p>
                </div>
              </div>
              <Button 
                onClick={() => setShowPaymentModal(true)}
                className="bg-red-600 hover:bg-blue-700 text-white"
                data-testid="unlock-grounds-btn"
              >
                <CreditCard className="w-4 h-4 mr-2" />
                Unlock for ${unlockPrice?.toFixed(2)}
              </Button>
            </div>
          </CardContent>
        </Card>
      )}

      {groundsCount === 0 && grounds.length === 0 ? (
        <Card className="p-12 text-center">
          <Scale className="w-12 h-12 text-slate-300 mx-auto mb-4" />
          <h3 className="text-lg font-semibold text-slate-900 mb-2" style={{ fontFamily: 'Crimson Pro, serif' }}>
            No grounds of merit identified
          </h3>
          <p className="text-slate-600 mb-4">
            Use AI to automatically identify potential grounds or add them manually.
          </p>
        </Card>
      ) : !isUnlocked ? (
        /* LOCKED — paywall banner above is shown, nothing else */
        null
      ) : (
        <div className="grid gap-4">
          {isUnlocked && (
            <div className="flex flex-wrap gap-2 justify-end" data-testid="grounds-export-actions">
              <Button onClick={() => openGroundsPreview("print")} className="bg-blue-700 text-white hover:bg-blue-600" data-testid="grounds-print-view-btn">
                <Printer className="w-4 h-4 mr-2" /> Print View
              </Button>
              <Button onClick={() => openGroundsPreview("pdf")} className="bg-blue-700 text-white hover:bg-blue-600" data-testid="grounds-pdf-view-btn">
                <Download className="w-4 h-4 mr-2" /> PDF View
              </Button>
              <Button onClick={exportGroundsWord} className="bg-blue-700 text-white hover:bg-blue-600" data-testid="grounds-word-view-btn">
                <FileText className="w-4 h-4 mr-2" /> Word View
              </Button>
            </div>
          )}
          {grounds.map((ground) => {
            const strengthConfig = STRENGTH_CONFIG[ground.strength] || STRENGTH_CONFIG.moderate;
            const StrengthIcon = strengthConfig.icon;
            const statusConfig = STATUS_CONFIG[ground.status] || STATUS_CONFIG.identified;
            
            return (
              <Card 
                key={ground.ground_id} 
                className={`card-hover group ${selectedGround?.ground_id === ground.ground_id ? 'ring-2 ring-blue-500' : ''}`}
                data-testid={`ground-${ground.ground_id}`}
              >
                <CardContent className="p-4">
                  <div className="flex items-start justify-between">
                    <div className="flex-1 cursor-pointer" onClick={() => openGroundDetail(ground)}>
                      <div className="flex items-center gap-2 flex-wrap mb-2">
                        <Badge variant="outline" className={GROUND_TYPE_COLORS[ground.ground_type] || GROUND_TYPE_COLORS.other}>
                          {GROUND_TYPE_LABELS[ground.ground_type] || ground.ground_type}
                        </Badge>
                        <Badge variant="outline" className={statusConfig.color}>
                          {statusConfig.label}
                        </Badge>
                        <div className={`flex items-center gap-1 px-2 py-0.5 rounded-full ${strengthConfig.bg}`}>
                          <StrengthIcon className={`w-3 h-3 ${strengthConfig.color}`} />
                          <span className={`text-xs font-medium ${strengthConfig.color}`}>
                            {strengthConfig.label}
                          </span>
                        </div>
                      </div>
                      
                      <h4 
                        className="font-semibold text-slate-900 text-lg group-hover:text-blue-700 transition-colors"
                        style={{ fontFamily: 'Crimson Pro, serif' }}
                      >
                        {ground.title}
                      </h4>
                      
                      {/* Show locked message or actual description */}
                      {!isUnlocked && ground.description === "*** UNLOCK TO VIEW ***" ? (
                        <div className="mt-2 p-3 bg-slate-100 rounded-lg border border-slate-200">
                          <div className="flex items-center gap-2 text-slate-500">
                            <Lock className="w-4 h-4" />
                            <span className="text-sm">Unlock to view full details</span>
                          </div>
                        </div>
                      ) : (
                        <p className="text-slate-600 mt-2 line-clamp-2">
                          {ground.description}
                        </p>
                      )}
                      
                      {/* Supporting Evidence Tags */}
                      {ground.supporting_evidence && ground.supporting_evidence.length > 0 && (
                        <EvidenceSummary items={ground.supporting_evidence} />
                      )}
                      
                      {/* Law Sections Preview */}
                      {ground.law_sections && ground.law_sections.length > 0 && (
                        <div className="flex items-center gap-2 mt-2">
                          <BookOpen className="w-4 h-4 text-slate-400" />
                          <span className="text-xs text-slate-500">
                            {ground.law_sections.length} law section{ground.law_sections.length > 1 ? 's' : ''} identified
                          </span>
                        </div>
                      )}
                      
                      {/* Similar Cases Preview */}
                      {ground.similar_cases && ground.similar_cases.length > 0 && (
                        <div className="flex items-center gap-2 mt-1">
                          <Gavel className="w-4 h-4 text-slate-400" />
                          <span className="text-xs text-slate-500">
                            {ground.similar_cases.length} similar case{ground.similar_cases.length > 1 ? 's' : ''} referenced
                          </span>
                        </div>
                      )}
                      
                      {/* Legitimacy Score Breakdown */}
                      {ground.legitimacy_scores && <LegitimacyPanel scores={ground.legitimacy_scores} />}
                      
                      {/* Verification + Source + Human Review */}
                      <div className="flex flex-wrap items-center gap-2 mt-3">
                        <StrengthBadge rating={ground.strength} />
                        <VerificationBadge status={ground.verification_status} />
                        <SourceModeBadge sourceMode={ground.source_mode} />
                        {ground.ground_type ? (
                          <span className="text-xs opacity-75">
                            {String(ground.ground_type).replaceAll("_", " ")}
                          </span>
                        ) : null}
                      </div>

                      <GroundProvenancePanel ground={ground} />
                      <GroundConfidenceNote ground={ground} />

                      {ground.source_mode === "derived" && ground.verification_status !== "verified" ? (
                        <div className="mt-2 text-xs text-yellow-700 font-medium">
                          This ground has been projected from staged pipeline analysis and should be reviewed before legal reliance.
                        </div>
                      ) : null}

                      <GroundPipelineStatus ground={ground} />

                      {ground.requires_human_review && (
                        <div className="mt-2 text-xs text-red-700 font-medium">
                          Requires human review before legal reliance
                        </div>
                      )}

                      <div className="text-xs opacity-75 mt-1">
                        Evidence: {Array.isArray(ground.supporting_evidence) ? ground.supporting_evidence.length : 0}
                        {" \u2022 "}
                        Source: {ground.source_mode || "legacy"}
                        {" \u2022 "}
                        Status: {ground.verification_status || "unverified"}
                      </div>

                      <p className="text-xs text-slate-400 mt-3">
                        Added {formatDate(ground.created_at)}
                        {ground.deep_analysis && " • Has deep analysis"}
                      </p>
                    </div>
                    
                    <div className="flex items-center gap-1 ml-4 flex-shrink-0">
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => toggleSearch(ground.ground_id)}
                        className="text-green-700 border-green-200 hover:bg-green-50"
                        data-testid={`search-caselaw-toggle-${ground.ground_id}`}
                      >
                        <Search className="w-4 h-4 mr-1" />
                        Search
                      </Button>
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => onInvestigate(ground.ground_id)}
                        disabled={investigating === ground.ground_id}
                        className="text-blue-700 border-blue-200 hover:bg-blue-50"
                        data-testid={`investigate-${ground.ground_id}`}
                      >
                        {investigating === ground.ground_id ? (
                          <Loader2 className="w-4 h-4 animate-spin" />
                        ) : (
                          <>
                            <Sparkles className="w-4 h-4 mr-1" />
                            Investigate
                          </>
                        )}
                      </Button>
                      <Button
                        variant="destructive"
                        size="sm"
                        onClick={() => onDelete(ground.ground_id)}
                        className="bg-red-600 hover:bg-red-700 text-white"
                        data-testid={`delete-ground-${ground.ground_id}`}
                      >
                        <Trash2 className="w-4 h-4" />
                      </Button>
                    </div>
                  </div>

                  {/* DO NOT UNDO — AI Investigation Progress Bar shown on THIS ground */}
                  {investigating === ground.ground_id && (
                    <div className="mt-3 p-3 bg-blue-50 border border-blue-200 rounded-lg" data-testid={`ai-investigate-progress-${ground.ground_id}`}>
                      <div className="flex items-center gap-3 mb-2">
                        <Loader2 className="w-5 h-5 animate-spin text-blue-600 flex-shrink-0" />
                        <p className="text-sm font-semibold text-blue-900">AI Scan in Progress — Investigating This Ground</p>
                      </div>
                      <p className="text-xs text-blue-700 mb-3">Deep analysis can take 1-3 minutes. Searching documents, case law, and legislation.</p>
                      <div className="w-full h-2 bg-blue-200 rounded-full overflow-hidden">
                        <div className="h-full w-3/4 bg-blue-600 rounded-full animate-pulse"></div>
                      </div>
                    </div>
                  )}

                  {/* DO NOT UNDO — Caselaw Search Box for each ground */}
                  {searchOpen[ground.ground_id] && (
                    <div className="mt-3 p-3 bg-green-50 border border-green-200 rounded-lg" data-testid={`search-box-${ground.ground_id}`}>
                      <p className="text-xs font-semibold text-green-800 mb-2">Search AustLII for cases related to this ground</p>
                      <div className="flex gap-2">
                        <Input
                          placeholder={ground.title || "Search caselaw..."}
                          value={searchTerms[ground.ground_id] || ""}
                          onChange={(e) => setSearchTerms(prev => ({ ...prev, [ground.ground_id]: e.target.value }))}
                          className="flex-1 text-sm"
                          data-testid={`search-input-${ground.ground_id}`}
                        />
                        <Button
                          size="sm"
                          onClick={() => handleCaselawSearch(ground.ground_id, ground.title)}
                          className="bg-green-600 hover:bg-green-700 text-white flex-shrink-0"
                          data-testid={`search-submit-${ground.ground_id}`}
                        >
                          <ExternalLink className="w-4 h-4 mr-1" />
                          Search
                        </Button>
                      </div>
                    </div>
                  )}
                </CardContent>
              </Card>
            );
          })}
        </div>
      )}

      {/* Ground Detail Dialog */}
      <Dialog open={showDetailDialog} onOpenChange={setShowDetailDialog}>
        <DialogContent className="max-w-4xl max-h-[90vh]">
          <DialogHeader>
            <DialogTitle style={{ fontFamily: 'Crimson Pro, serif' }} className="text-2xl flex items-center gap-3">
              <Scale className="w-6 h-6 text-red-600" />
              Ground of Merit Analysis
            </DialogTitle>
            {detailGround && (detailGround.deep_analysis?.full_analysis || detailGround.analysis) && (
              <div className="flex items-center gap-2 mt-2">
                <Button variant="outline" size="sm" onClick={handleGroundPrint} data-testid="ground-print-btn">
                  <Printer className="w-4 h-4 mr-1.5" /> Print
                </Button>
                <Button variant="outline" size="sm" onClick={handleGroundPDF} data-testid="ground-pdf-btn">
                  <Download className="w-4 h-4 mr-1.5" /> PDF View
                </Button>
                <Button variant="outline" size="sm" onClick={() => {
                  if (!detailGround) return;
                  const html = buildSingleGroundHtml(detailGround);
                  const blob = new Blob([`<html xmlns:o="urn:schemas-microsoft-com:office:office" xmlns:w="urn:schemas-microsoft-com:office:word" xmlns="http://www.w3.org/TR/REC-html40"><head><meta charset="utf-8"></head><body>${html}</body></html>`], {type:'application/msword'});
                  const url = window.URL.createObjectURL(blob);
                  const a = document.createElement('a');
                  a.href = url;
                  a.download = `Ground_${detailGround.title?.replace(/[^a-zA-Z0-9]/g,'_')}.doc`;
                  a.click();
                  window.URL.revokeObjectURL(url);
                  toast.success("Word document downloaded");
                }} data-testid="ground-word-btn">
                  <FileText className="w-4 h-4 mr-1.5" /> Word
                </Button>
              </div>
            )}
          </DialogHeader>
          
          {detailGround && (
            <ScrollArea className="max-h-[70vh] pr-4">
              <div className="space-y-6">
                {/* Header Info */}
                <div className="bg-slate-50 rounded-lg p-4 border border-slate-200">
                  <div className="flex items-center gap-2 flex-wrap mb-3">
                    <Badge variant="outline" className={GROUND_TYPE_COLORS[detailGround.ground_type] || GROUND_TYPE_COLORS.other}>
                      {GROUND_TYPE_LABELS[detailGround.ground_type] || detailGround.ground_type}
                    </Badge>
                    <Badge variant="outline" className={STATUS_CONFIG[detailGround.status]?.color}>
                      {STATUS_CONFIG[detailGround.status]?.label}
                    </Badge>
                    {(() => {
                      const cfg = STRENGTH_CONFIG[detailGround.strength] || STRENGTH_CONFIG.moderate;
                      const Icon = cfg.icon;
                      return (
                        <div className={`flex items-center gap-1 px-2 py-0.5 rounded-full ${cfg.bg}`}>
                          <Icon className={`w-3 h-3 ${cfg.color}`} />
                          <span className={`text-xs font-medium ${cfg.color}`}>{cfg.label}</span>
                        </div>
                      );
                    })()}
                  </div>
                  <h3 
                    className="text-xl font-bold text-slate-900"
                    style={{ fontFamily: 'Crimson Pro, serif' }}
                  >
                    {detailGround.title}
                  </h3>
                  <p className="text-slate-600 mt-2">{detailGround.description}</p>
                </div>

                {/* Supporting Evidence */}
                {detailGround.supporting_evidence && detailGround.supporting_evidence.length > 0 && (
                  <div>
                    <h4 className="font-semibold text-slate-900 mb-2 flex items-center gap-2">
                      <FileText className="w-4 h-4" />
                      Supporting Evidence
                    </h4>
                    <ul className="list-disc pl-5 space-y-1 text-slate-700">
                      {detailGround.supporting_evidence.map((ev, idx) => (
                        <li key={idx}>{ev}</li>
                      ))}
                    </ul>
                  </div>
                )}

                {/* Law Sections */}
                {detailGround.law_sections && detailGround.law_sections.length > 0 && (
                  <div>
                    <h4 className="font-semibold text-slate-900 mb-2 flex items-center gap-2">
                      <BookOpen className="w-4 h-4" />
                      Relevant Law Sections
                    </h4>
                    <div className="space-y-2">
                      {detailGround.law_sections.map((section, idx) => (
                        <div key={idx} className="bg-blue-50 border border-blue-200 rounded-lg p-3">
                          <div className="font-mono text-sm text-blue-800">
                            s.{section.section} {section.act}
                          </div>
                          <div className="text-xs text-blue-600 mt-1">
                            Jurisdiction: {section.jurisdiction}
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {/* Similar Cases */}
                {detailGround.similar_cases && detailGround.similar_cases.length > 0 && (
                  <div>
                    <h4 className="font-semibold text-slate-900 mb-2 flex items-center gap-2">
                      <Gavel className="w-4 h-4" />
                      Similar Cases
                      <span className="text-xs font-normal text-amber-600">(AI-referenced — requires verification)</span>
                    </h4>
                    <div className="space-y-2">
                      {detailGround.similar_cases.map((caseItem, idx) => (
                        <div key={idx} className="bg-blue-50 border border-blue-200 rounded-lg p-3">
                          <div className="font-medium text-blue-900">
                            {caseItem.case_name}
                            {!caseItem.verified && <UnverifiedBadge />}
                          </div>
                          {caseItem.citation && (
                            <div className="font-mono text-xs text-blue-700 mt-1">
                              {caseItem.citation}
                            </div>
                          )}
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {/* Legitimacy Score in Detail View */}
                {detailGround.legitimacy_scores && (
                  <div>
                    <h4 className="font-semibold text-slate-900 mb-2 flex items-center gap-2">
                      Ground Scoring
                    </h4>
                    <LegitimacyPanel scores={detailGround.legitimacy_scores} />
                  </div>
                )}

                {/* Verification + Source + Human Review in Detail View */}
                <div className="flex flex-wrap items-center gap-2">
                  <StrengthBadge rating={detailGround.strength} />
                  <VerificationBadge status={detailGround.verification_status} />
                  <SourceModeBadge sourceMode={detailGround.source_mode} />
                  {detailGround.ground_type ? (
                    <span className="text-xs opacity-75">
                      {String(detailGround.ground_type).replaceAll("_", " ")}
                    </span>
                  ) : null}
                </div>

                <GroundProvenancePanel ground={detailGround} />
                <GroundConfidenceNote ground={detailGround} />

                {detailGround.source_mode === "derived" && detailGround.verification_status !== "verified" ? (
                  <div className="mt-2 text-xs text-yellow-700 font-medium">
                    This ground has been projected from staged pipeline analysis and should be reviewed before legal reliance.
                  </div>
                ) : null}

                <GroundPipelineStatus ground={detailGround} />

                {detailGround.requires_human_review && (
                  <div className="text-xs text-red-700 font-medium">
                    Requires human review before legal reliance
                  </div>
                )}

                {/* Deep Analysis */}
                {detailGround.deep_analysis?.full_analysis && (
                  <div>
                    <h4 className="font-semibold text-slate-900 mb-3 flex items-center gap-2">
                      <Sparkles className="w-4 h-4 text-red-600" />
                      Deep Analysis
                      <span className="text-xs font-normal text-slate-500">
                        Generated {formatDate(detailGround.deep_analysis.investigated_at)}
                      </span>
                    </h4>
                    <div className="bg-white border border-slate-200 rounded-lg p-4">
                      {formatAnalysis(detailGround.deep_analysis.full_analysis)}
                    </div>
                  </div>
                )}

                {/* Basic Analysis (if no deep analysis) */}
                {!detailGround.deep_analysis?.full_analysis && detailGround.analysis && (
                  <div>
                    <h4 className="font-semibold text-slate-900 mb-2">Analysis</h4>
                    <div className="text-slate-700 whitespace-pre-wrap">
                      {detailGround.analysis}
                    </div>
                  </div>
                )}

                {/* No Analysis Yet */}
                {!detailGround.deep_analysis?.full_analysis && !detailGround.analysis && (
                  <div className="text-center py-8 bg-slate-50 rounded-lg border border-slate-200">
                    <Search className="w-10 h-10 text-slate-300 mx-auto mb-3" />
                    <p className="text-slate-600">
                      Click "Investigate" to run a deep AI analysis of this ground of merit.
                    </p>
                  </div>
                )}
              </div>
            </ScrollArea>
          )}
        </DialogContent>
      </Dialog>

      {/* Payment Modal */}
      <PaymentModal
        isOpen={showPaymentModal}
        onClose={() => setShowPaymentModal(false)}
        caseId={caseId}
        featureType="grounds_of_merit"
        price={unlockPrice}
        onPaymentSuccess={onPaymentSuccess}
      />
    </div>
  );
};

export default GroundsOfMerit;
