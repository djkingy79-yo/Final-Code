/* ========================================================================
   DO NOT UNDO — ENTIRE FILE PROTECTED
   All features, functions, styles, and content in this file are approved
   and must be preserved. Do not remove, rename, or refactor any code.
   ======================================================================== */
import { useState, useEffect, useRef, useCallback } from "react";
import { 
  Scale, Trash2, Search, Loader2, 
  AlertTriangle, CheckCircle, XCircle, Sparkles,
  BookOpen, Gavel, FileText, Lock, CreditCard, ExternalLink, Printer, Download,
  GripVertical, ArrowUpDown, Check
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
import auSpelling from "../utils/auSpelling";
import { normaliseMarkdown, renderMarkdownToHtml } from "../utils/mdRender";
import { API } from "../App";

/* DO NOT UNDO — Australian spelling normaliser imported from utils/auSpelling.js
   The shared utility is now used across all components. */

/* DO NOT UNDO — Universal evidence text extractor.
   Handles ALL formats the AI may return evidence in:
   - Plain string: "The judge failed to..."
   - Python dict string: "{'document_id': 'optional', 'quote': 'actual text...'}"
   - JS object: { quote: "actual text..." }
   - Key-concatenated string: "document_idfilenamequote..."
   Returns just the human-readable quote/text. */
const extractEvidenceText = (item) => {
  if (!item) return null;
  if (typeof item === "string") {
    // Check if it's a Python dict string like "{'quote': '...'}"
    const quoteMatch = item.match(/['"]quote['"]\s*:\s*['"](.+?)['"]\s*[,}]/);
    if (quoteMatch) return quoteMatch[1];
    // Check if it's a concatenation of keys
    if (item.includes("document_id") && item.includes("filename") && item.includes("quote")) {
      return null; // Skip key-concatenated garbage
    }
    // Check if it looks like raw dict/JSON
    if (item.startsWith("{") && item.includes("'optional'")) return null;
    return item;
  }
  if (typeof item === "object") {
    return item.quote || item.text || item.description || item.filename || null;
  }
  return String(item);
};

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
  strong: { icon: CheckCircle, color: "text-emerald-600", bg: "bg-emerald-100", label: "Arguable — Strong" },
  moderate: { icon: AlertTriangle, color: "text-blue-600", bg: "bg-blue-100", label: "Arguable — Moderate" },
  weak: { icon: XCircle, color: "text-red-600", bg: "bg-red-100", label: "Requires Development" }
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
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-1 sm:gap-3 mb-1">
        <div className="flex justify-between sm:block"><span className="text-slate-500">Legal:</span> <span className="font-semibold">{scores.legal_score}/3</span></div>
        <div className="flex justify-between sm:block"><span className="text-slate-500">Evidence:</span> <span className="font-semibold">{scores.evidence_score}/3</span></div>
        <div className="flex justify-between sm:block"><span className="text-slate-500">Viability:</span> <span className="font-semibold">{scores.viability_score}/3</span></div>
      </div>
      <div className="font-bold text-slate-700">Total: {scores.total_score}/9</div>
      {scores.confidence_note && (
        <p className="italic text-slate-500 mt-1 leading-tight">{scores.confidence_note}</p>
      )}
    </div>
  );
};

const UnverifiedBadge = () => (
  <span className="ml-1 text-[10px] px-1.5 py-0.5 rounded bg-blue-100 text-blue-700 font-medium">
    AI-SUGGESTED
  </span>
);

const SourceModeBadge = ({ sourceMode }) => {
  const value = String(sourceMode || "legacy").toLowerCase();

  const classes = {
    derived: "border-green-700 text-green-700",
    ai_generated: "border-blue-700 text-blue-700",
    manual: "border-purple-700 text-purple-700",
    imported: "border-slate-700 text-slate-700",
    legacy: "border-pink-600 text-pink-600",
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
    ? ground.similar_cases.filter(c => c.case_name && c.case_name !== "Case name" && c.case_name !== "R v [Surname] [Year]" && !c.case_name.includes("[Surname]") && !c.case_name.includes("[Year]") && c.case_name !== "None" && c.case_name !== "optional" && c.case_name !== "optional")
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
        <span className="text-pink-600 font-bold">
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
  caseData,
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
  const [checkingPayment, setCheckingPayment] = useState(false);
  const [trialEligible, setTrialEligible] = useState(false);
  const [trialPrice, setTrialPrice] = useState(null);
  const [reorderMode, setReorderMode] = useState(false);
  const [orderedGrounds, setOrderedGrounds] = useState([]);
  const [savingOrder, setSavingOrder] = useState(false);
  const dragItem = useRef(null);
  const dragOverItem = useRef(null);

  useEffect(() => {
    setOrderedGrounds(grounds || []);
  }, [grounds]);

  const handleDragStart = useCallback((idx) => {
    dragItem.current = idx;
  }, []);

  const handleDragEnter = useCallback((idx) => {
    dragOverItem.current = idx;
  }, []);

  const handleDragEnd = useCallback(() => {
    if (dragItem.current === null || dragOverItem.current === null) return;
    const items = [...orderedGrounds];
    const draggedItem = items[dragItem.current];
    items.splice(dragItem.current, 1);
    items.splice(dragOverItem.current, 0, draggedItem);
    dragItem.current = null;
    dragOverItem.current = null;
    setOrderedGrounds(items);
  }, [orderedGrounds]);

  const saveReorder = async () => {
    setSavingOrder(true);
    try {
      const token = localStorage.getItem("session_token") || localStorage.getItem("token");
      const res = await fetch(`${API}/api/cases/${caseId}/grounds/reorder`, {
        method: "PUT",
        headers: { "Content-Type": "application/json", Authorization: `Bearer ${token}` },
        body: JSON.stringify({ ground_ids: orderedGrounds.map(g => g.ground_id) }),
      });
      if (res.ok) {
        toast.success("Ground priority order saved");
        setReorderMode(false);
      } else {
        toast.error("Failed to save order");
      }
    } catch {
      toast.error("Failed to save order");
    }
    setSavingOrder(false);
  };

  const moveGround = useCallback((fromIdx, direction) => {
    const toIdx = fromIdx + direction;
    if (toIdx < 0 || toIdx >= orderedGrounds.length) return;
    const items = [...orderedGrounds];
    [items[fromIdx], items[toIdx]] = [items[toIdx], items[fromIdx]];
    setOrderedGrounds(items);
  }, [orderedGrounds]);

  // Always render from orderedGrounds (synced from props via useEffect).
  // This prevents UI jump after saving reorder — orderedGrounds retains the
  // locally saved order until the parent refetches and updates the grounds prop.
  const displayGrounds = orderedGrounds;

  // Fetch trial eligibility
  useEffect(() => {
    if (isUnlocked) return;
    const fetchTrial = async () => {
      try {
        const token = localStorage.getItem("session_token") || localStorage.getItem("token");
        const res = await fetch(`${API}/api/payments/trial-status`, {
          headers: { Authorization: `Bearer ${token}` },
        });
        if (res.ok) {
          const data = await res.json();
          setTrialEligible(data.is_eligible);
          setTrialPrice(data.trial_price);
        }
      } catch {}
    };
    fetchTrial();
  }, [isUnlocked]);
  /* DO NOT UNDO — Search box state for each ground. Uses object to track per-ground search visibility */
  const [searchOpen, setSearchOpen] = useState({});
  const [searchTerms, setSearchTerms] = useState({});

  /* DO_NOT_UNDO — Investigate elapsed timer. Starts counting when investigation begins,
     resets when investigation completes. Matches the report generation timer block. */
  const [investElapsed, setInvestElapsed] = useState(0);
  useEffect(() => {
    if (!investigating) { setInvestElapsed(0); return; }
    setInvestElapsed(0);
    const interval = setInterval(() => setInvestElapsed(prev => prev + 1), 1000);
    return () => clearInterval(interval);
  }, [investigating]);

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
    const auText = normaliseMarkdown(auSpelling(analysis));
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
        >{auText}</ReactMarkdown>
      </div>
    );
  };

  const buildGroundsPreviewHtml = () => {
    const contentMarkup = renderToStaticMarkup(
      <div className="grounds-export-shell">
        <div className="grounds-export-header">
          <p className="grounds-export-kicker">Grounds of Merit</p>
          <h1>Detailed Grounds Analysis</h1>
          {/* DO_NOT_UNDO — Case identity must always display in export */}
          <div style={{margin:'4px 0 6px', padding:'5px 8px', border:'1pt solid #1e3a8a', borderRadius:'4px', background:'#eff6ff'}}>
            <div style={{display:'grid', gridTemplateColumns:'1fr 1fr', columnGap:'12px', rowGap:'2px', fontSize:'10pt', fontFamily:"'Times New Roman', Times, serif", lineHeight:'1.25'}}>
              <div><span style={{fontSize:'7pt', fontWeight:800, textTransform:'uppercase', letterSpacing:'0.08em', color:'#1e3a8a'}}>Defendant</span>&nbsp;<strong style={{fontSize:'10pt'}}>{caseData?.defendant_name || "—"}</strong></div>
              <div><span style={{fontSize:'7pt', fontWeight:800, textTransform:'uppercase', letterSpacing:'0.08em', color:'#1e3a8a'}}>Offence</span>&nbsp;<strong style={{textTransform:'capitalize', fontSize:'10pt'}}>{caseData?.offence_type || caseData?.offence_category?.replace(/_/g, ' ') || "—"}</strong></div>
              <div><span style={{fontSize:'7pt', fontWeight:800, textTransform:'uppercase', letterSpacing:'0.08em', color:'#1e3a8a'}}>State</span>&nbsp;<strong style={{textTransform:'uppercase', fontSize:'10pt'}}>{caseData?.state || "—"}</strong></div>
              <div><span style={{fontSize:'7pt', fontWeight:800, textTransform:'uppercase', letterSpacing:'0.08em', color:'#1e3a8a'}}>Sentence</span>&nbsp;<strong style={{fontSize:'10pt'}}>{caseData?.sentence || "—"}</strong></div>
            </div>
          </div>
        </div>

        {grounds.map((ground, index) => (
          <section key={ground.ground_id || index} className="grounds-export-section">
            <div className="grounds-export-title-wrap">
              <h2>{`Ground ${index + 1}: ${auSpelling(ground.title)}`}</h2>
              <div className="grounds-export-meta">
                <span>{GROUND_TYPE_LABELS[ground.ground_type] || ground.ground_type}</span>
                <span>{STATUS_CONFIG[ground.status]?.label || ground.status || "Identified"}</span>
                <span>{STRENGTH_CONFIG[ground.strength]?.label || ground.strength || "Moderate"}</span>
              </div>
            </div>

            <p className="grounds-export-description">{auSpelling(ground.description)}</p>

            {/* Appellate Pathway — DO NOT UNDO */}
            {ground.appellate_pathway && (
              <div className="grounds-export-block" style={{background:'#eff6ff', border:'1px solid #93c5fd', borderRadius:'4px', padding:'4px 8px', marginBottom:'6px'}}>
                <h3 style={{color:'#1d4ed8', marginBottom:'2px', fontSize:'10pt'}}>Appellate Pathway</h3>
                <p style={{fontSize:'9pt', lineHeight:'1.4', margin:0}}>{auSpelling(ground.appellate_pathway)}</p>
              </div>
            )}

            {ground.supporting_evidence?.length > 0 && (
              <div className="grounds-export-block">
                <h3>Supporting Evidence</h3>
                <ul>
                  {ground.supporting_evidence.map((item, idx) => {
                    const text = extractEvidenceText(item);
                    if (!text) return null;
                    return <li key={idx}>{text}</li>;
                  })}
                </ul>
              </div>
            )}

            {/* DO NOT UNDO — Filter out law sections without real section numbers */}
            {ground.law_sections?.filter(s => s.section && !s.section.toLowerCase().includes('not provided') && !s.section.toLowerCase().includes('unknown') && s.section.trim() !== '')?.length > 0 && (
              <div className="grounds-export-block">
                <h3>Relevant Law Sections</h3>
                <ul>
                  {ground.law_sections.filter(s => s.section && !s.section.toLowerCase().includes('not provided') && !s.section.toLowerCase().includes('unknown') && s.section.trim() !== '').map((section, idx) => {
                    const jur = (section.jurisdiction || "NSW").toUpperCase();
                    const actText = section.act || "";
                    const jurInAct = actText.toUpperCase().includes(`(${jur})`);
                    const secRaw = section.section.trim();
                    const secLower = secRaw.toLowerCase();
                    const structural = /^(chapter|part|division|schedule|subpart)\s/.test(secLower);
                    const alreadyPrefixed = /^s\s|^s\.|^ss\s|^ss\./.test(secLower);
                    const secDisplay = structural || alreadyPrefixed ? secRaw : `s ${secRaw}`;
                    return <li key={idx}>{`${secDisplay} ${actText}${jurInAct ? "" : ` (${jur})`}`.trim()}</li>;
                  })}
                </ul>
              </div>
            )}

            {/* DO NOT UNDO — Filter out unverified/placeholder similar cases */}
            {ground.similar_cases?.filter(c => c.case_name && c.case_name !== "Case name" && !c.case_name.includes("[Surname]") && !c.case_name.includes("[Year]") && c.case_name !== "None" && c.case_name !== "optional" && !(c.citation || '').toLowerCase().includes('verification needed'))?.length > 0 && (
              <div className="grounds-export-block">
                <h3>Comparable Authority</h3>
                <ul>
                  {ground.similar_cases.filter(c => c.case_name && c.case_name !== "Case name" && !c.case_name.includes("[Surname]") && !c.case_name.includes("[Year]") && c.case_name !== "None" && c.case_name !== "optional" && !(c.citation || '').toLowerCase().includes('verification needed')).map((caseItem, idx) => (
                    <li key={idx}>{caseItem.citation ? `${caseItem.case_name} ${caseItem.citation}` : caseItem.case_name}{caseItem.relevance_note ? ` — ${caseItem.relevance_note}` : ''}</li>
                  ))}
                </ul>
              </div>
            )}

            {(ground.deep_analysis?.full_analysis || ground.analysis) && (
              <div className="grounds-export-analysis">
                <h3>Deep Investigation Analysis</h3>
                <div
                  className="legal-report"
                  dangerouslySetInnerHTML={{
                    __html: renderMarkdownToHtml(ground.deep_analysis?.full_analysis || ground.analysis || ""),
                  }}
                />
              </div>
            )}

            {/* DO NOT UNDO — Per-ground appellate disclaimer */}
            <div style={{marginTop:'6px', padding:'4px 8px', background:'#f1f5f9', border:'1px solid #cbd5e1', borderRadius:'4px', fontSize:'8pt', lineHeight:'1.4', color:'#475569', fontStyle:'italic'}}>
              This analysis identifies potential appellate issues based on available material. It does not determine that the appeal will succeed. All grounds require refinement and verification by a qualified legal practitioner.
            </div>
          </section>
        ))}

        <div className="grounds-export-disclaimer">
          <span style={{fontSize:'24px', color:'#facc15', flexShrink:0}}>&#9888;</span>
          <div>
            <strong style={{display:'block', marginBottom:'4px', textTransform:'uppercase', letterSpacing:'0.06em'}}>NOT LEGAL ADVICE</strong>
            This material is an educational tool only and does NOT constitute legal advice. All analysis and recommendations must be independently verified by a qualified Australian legal professional. Australian law only. No solicitor-client relationship is created. No document, report, or output should be filed with, submitted to, or relied upon before any court, tribunal, or regulatory body.
          </div>
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
    /* CANONICAL PRINT SPEC (locked 2026-02 by owner — DO NOT DRIFT)
       Body 11pt / H1 14pt / H2 12pt / H3 12pt italic / line-height 1.5 / para-gap 10pt
       Margins 18/20/22mm / Footer 9pt italic.
       CSS Paged Media — @bottom-* margin boxes are the ONLY reliable way to
       get a repeating footer on every page across Chrome/Safari print pipelines. */
    @page {
      size: A4;
      margin: 18mm 20mm 22mm 20mm;
      @bottom-left {
        content: "${(caseData?.defendant_name || 'Appellant').replace(/"/g,'\\"')} \\00B7  Grounds of Merit \\00B7  ${new Date().toLocaleDateString('en-AU',{day:'numeric',month:'long',year:'numeric'})}";
        font-family: 'Times New Roman', Times, serif;
        font-size: 9pt;
        font-style: italic;
        color: #334155;
      }
      @bottom-right {
        content: "Page " counter(page) " of " counter(pages);
        font-family: 'Times New Roman', Times, serif;
        font-size: 9pt;
        font-style: italic;
        color: #334155;
      }
    }
    * { -webkit-text-size-adjust: 100%; text-size-adjust: 100%; box-sizing: border-box; }
    body { margin: 0; background: #fff; color: #0f172a; font-family: 'Times New Roman', Times, serif; font-size: 11pt; line-height: 1.5; }
    .grounds-export-shell { max-width: 820px; margin: 0 auto; background: #ffffff; padding: 16px 22px; }
    .grounds-export-header { border-bottom: 1.5pt solid #1e3a8a; padding-bottom: 8pt; margin-bottom: 10pt; }
    .grounds-export-kicker { text-transform: uppercase; letter-spacing: 0.14em; color: #1e3a8a; font-weight: 800; font-size: 9pt; margin: 0 0 3px; }
    .grounds-export-header h1 { margin: 0 0 3px; font-size: 14pt; font-family: 'Times New Roman', Times, serif; font-weight: 700; line-height: 1.3; }
    /* Let content flow naturally across pages. orphans:3 widows:3 keeps
       headings from being orphaned. No forced breaks — prevents half-empty
       pages the owner reported. */
    .grounds-export-section { padding: 8pt 0 4pt; page-break-inside: auto; break-inside: auto; orphans: 3; widows: 3; }
    .grounds-export-section + .grounds-export-section { border-top: 0.5pt solid #cbd5e1; margin-top: 6pt; padding-top: 10pt; }
    /* H2 (ground title) — keep with body */
    .grounds-export-title-wrap h2 { margin: 0 0 4px; font-size: 12pt; font-weight: 700; font-family: 'Times New Roman', Times, serif; line-height: 1.4; page-break-after: avoid; break-after: avoid; }
    .grounds-export-meta { display: flex; flex-wrap: wrap; gap: 4px; margin-bottom: 6pt; }
    .grounds-export-meta span { background: #dbeafe; color: #1e3a8a; padding: 1px 8px; border-radius: 10pt; font-size: 9pt; font-weight: 700; }
    .grounds-export-description { margin: 0 0 10pt 0; line-height: 1.5; font-size: 11pt; text-align: justify; orphans: 3; widows: 3; }
    .grounds-export-block { margin-bottom: 8pt; }
    /* H3 subheadings — italic, no forced break-after */
    .grounds-export-block h3, .grounds-export-analysis h3 { margin: 8pt 0 4pt; font-size: 12pt; font-weight: 700; font-style: italic; font-family: 'Times New Roman', Times, serif; color: #1e3a8a; }
    .grounds-export-block ul { margin: 0 0 10pt; padding-left: 1.5rem; line-height: 1.5; }
    .grounds-export-block ul li { font-size: 11pt !important; line-height: 1.5; margin-bottom: 4pt; }
    .grounds-export-analysis { margin-top: 10pt; }
    .grounds-export-disclaimer { margin-top: 14pt; background: #dc2626; border: 1pt solid #b91c1c; padding: 8px 10px; font-weight: 700; line-height: 1.45; font-size: 10pt; color: #ffffff; border-radius: 4px; display: flex; gap: 8px; align-items: flex-start; -webkit-print-color-adjust: exact; print-color-adjust: exact; }
    .legal-report p { line-height: 1.5; margin: 0 0 10pt; font-size: 11pt; font-family: 'Times New Roman', Times, serif; text-align: justify; orphans: 3; widows: 3; }
    /* legal-report headings — no forced break-after */
    .legal-report h1, .legal-report h2, .legal-report h3, .legal-report h4 { color: #0f172a; font-family: 'Times New Roman', Times, serif; }
    .legal-report h2 { font-size: 12pt; font-weight: 700; margin: 10pt 0 4pt; }
    .legal-report h3 { font-size: 12pt; font-weight: 700; font-style: italic; margin: 8pt 0 4pt; }
    .legal-report h4 { font-size: 11pt; font-weight: 700; margin: 6pt 0 3pt; }
    .legal-report-table-wrap { overflow-x: auto; }
    .legal-report table { width: 100%; border-collapse: collapse; table-layout: fixed; font-size: 10pt; margin: 6pt 0 10pt; }
    .legal-report th, .legal-report td { border: 0.5pt solid #94a3b8; padding: 4px 6px; vertical-align: top; }
    .legal-report th { background: #1e3a8a; color: #fff; font-weight: 700; -webkit-print-color-adjust: exact; print-color-adjust: exact; }
    .legal-report td { overflow-wrap: anywhere; word-break: break-word; }
    .legal-report ul, .legal-report ol { padding-left: 1.4rem; margin: 4pt 0 10pt; }
    .legal-report li { font-size: 11pt; line-height: 1.5; margin-bottom: 3pt; }
    @media print {
      body { background: #fff; }
      .grounds-export-shell { max-width: none; padding: 0; }
    }
    @media (max-width: 768px) {
      /* WYSIWYG parity — same canonical sizes as print; only padding shrinks. */
      .grounds-export-shell { padding: 10px 12px; max-width: 100%; }
      .grounds-export-header h1 { font-size: 14pt; }
      .grounds-export-title-wrap h2 { font-size: 12pt; }
      .grounds-export-block h3, .grounds-export-analysis h3,
      .legal-report h3 { font-size: 12pt; }
      .grounds-export-description,
      .grounds-export-block ul li,
      .legal-report p, .legal-report li { font-size: 11pt; line-height: 1.5; }
      .legal-report table { font-size: 9.5pt; }
    }
  </style>
</head>
<body>${contentMarkup}
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
    // Use document-preview route for iOS compatibility (blob URLs fail on Safari)
    localStorage.setItem(
      "document-preview-payload",
      JSON.stringify({
        html,
        mode: "word",
        title: "Grounds of Merit — Word View",
        source: "grounds",
        returnTo: `/cases/${caseId}`,
        createdAt: Date.now(),
      })
    );
    const previewUrl = `${window.location.origin}/document-preview?mode=word`;
    window.location.assign(previewUrl);
  };

  const buildSingleGroundHtml = (ground) => {
    const analysis = ground.deep_analysis?.full_analysis || ground.analysis || "";
    const escHtml = (s) => auSpelling((s || "").replace(/&/g,"&amp;").replace(/</g,"&lt;").replace(/>/g,"&gt;"));
    return `<!DOCTYPE html>
<html lang="en"><head><meta charset="UTF-8" /><meta name="viewport" content="width=device-width, initial-scale=1.0" /><title>Ground: ${escHtml(ground.title)}</title>
<style>
/* CANONICAL PRINT SPEC (locked 2026-02 by owner — DO NOT DRIFT)
   Body 11pt / H1 14pt / H2 12pt / H3 12pt italic / line-height 1.5 / para-gap 10pt
   Margins 18/20/22mm / Footer 9pt italic */
@page{
  size:A4;margin:18mm 20mm 22mm 20mm;
  @bottom-left{
    content:"${escHtml(caseData?.defendant_name || 'Appellant').replace(/"/g,'\\"')} \\00B7  Grounds of Merit \\00B7  ${new Date().toLocaleDateString('en-AU',{day:'numeric',month:'long',year:'numeric'})}";
    font-family:'Times New Roman',Times,serif;font-size:9pt;font-style:italic;color:#334155;
  }
  @bottom-right{
    content:"Page " counter(page) " of " counter(pages);
    font-family:'Times New Roman',Times,serif;font-size:9pt;font-style:italic;color:#334155;
  }
}
*{-webkit-text-size-adjust:100%;text-size-adjust:100%;box-sizing:border-box}
body{font-family:'Times New Roman',Times,serif;font-size:11pt;color:#0f172a;padding:16px 20px;line-height:1.5;max-width:820px;margin:0 auto}
h1{font-size:14pt;margin:0 0 8pt;font-weight:700;font-family:'Times New Roman',Times,serif;line-height:1.3}
h2{font-size:12pt;margin:14pt 0 6pt;border-bottom:1.5pt solid #1d4ed8;padding-bottom:3px;font-weight:700;font-family:'Times New Roman',Times,serif;page-break-after:avoid;break-after:avoid}
h3{font-size:12pt;margin:12pt 0 4pt;font-weight:700;font-style:italic;font-family:'Times New Roman',Times,serif;color:#1e3a8a}
.meta{display:flex;gap:6px;flex-wrap:wrap;margin:6pt 0 10pt}.meta span{background:#dbeafe;color:#1d4ed8;padding:2px 8px;border-radius:999px;font-size:10pt;font-weight:700}
.desc{margin:0 0 10pt;font-size:11pt;line-height:1.5;orphans:3;widows:3}
ul,ol{padding-left:1.5rem;margin:4pt 0 10pt}
li{margin-bottom:3pt;font-size:11pt !important;line-height:1.5;-webkit-text-size-adjust:100%}
p{margin:0 0 10pt;font-size:11pt;line-height:1.5;orphans:3;widows:3}
.case-box{background:#eff6ff;border:1px solid #93c5fd;padding:8px 12px;border-radius:6px;margin-bottom:8pt;font-size:11pt}
.analysis{margin-top:10pt;font-size:11pt;line-height:1.5}
.analysis h1,.analysis h2,.analysis h3,.analysis h4{font-family:'Times New Roman',Times,serif;color:#0f172a;font-weight:700;page-break-after:avoid;break-after:avoid}
.analysis h2{font-size:12pt;margin:14pt 0 6pt;border-bottom:1.5pt solid #1d4ed8;padding-bottom:3px}
.analysis h3{font-size:12pt;margin:12pt 0 4pt;font-style:italic;color:#1e3a8a;border:0;padding:0}
.analysis h4{font-size:11pt;margin:10pt 0 4pt}
.analysis p{margin:0 0 10pt;orphans:3;widows:3}
.analysis ul,.analysis ol{padding-left:1.3rem;margin:4pt 0 10pt}
.analysis li{margin-bottom:3pt;font-size:11pt;line-height:1.5}
.analysis strong{font-weight:700}
.analysis em{font-style:italic}
table{border-collapse:collapse;width:100%;margin:6pt 0 10pt;font-family:'Times New Roman',Times,serif}
th,td{border:1px solid #cbd5e1;padding:5px 7px;text-align:left;font-size:10pt;vertical-align:top}
th{background:#dbeafe;font-weight:700}
.disclaimer{background:#dc2626;border:3px solid #b91c1c;padding:10px 14px;border-radius:8px;margin-top:16pt;page-break-inside:avoid;display:flex;gap:10px;align-items:flex-start;-webkit-print-color-adjust:exact;print-color-adjust:exact}
.disclaimer .disc-hazard{font-size:22px;color:#facc15;flex-shrink:0}
.disclaimer strong{font-size:11pt;text-transform:uppercase;color:#ffffff;display:block;margin-bottom:3px}
.disclaimer p{font-size:10pt;color:#ffffff;margin:0;line-height:1.45;font-weight:700}
@media print{body{padding:0;max-width:none}}
@media (max-width:768px){
  body{padding:12px 14px;max-width:100%}
  h1{font-size:14pt}h2{font-size:12pt}h3{font-size:12pt}
  .desc,li,p,.analysis,.case-box{font-size:11pt;line-height:1.5}
  table{font-size:9.5pt}
}
</style></head><body>
<h1>Ground of Merit: ${escHtml(ground.title)}</h1>
<div class="meta"><span>${escHtml((ground.ground_type || 'other').replace(/_/g,' '))}</span><span>${escHtml(ground.strength || 'Moderate')}</span><span>${escHtml(ground.status || 'Identified')}</span></div>
<p class="desc">${escHtml(ground.description)}</p>
${(ground.supporting_evidence||[]).length ? '<h2>Supporting Evidence</h2><ul>' + ground.supporting_evidence.map(e => {
  let t = '';
  if (typeof e === 'string') {
    const m = e.match(/['"]quote['"]\s*:\s*['"](.+?)['"]\s*[,}]/);
    t = m ? m[1] : (e.includes('document_id') && e.includes('optional') ? '' : e);
  } else { t = e?.quote || e?.text || ''; }
  return t ? '<li>'+escHtml(t)+'</li>' : '';
}).join('') + '</ul>' : ''}
${(ground.law_sections||[]).filter(s => s.section && !s.section.toLowerCase().includes('not provided') && !s.section.toLowerCase().includes('unknown') && s.section.trim() !== '').length ? '<h2>Relevant Law Sections</h2><ul>' + ground.law_sections.filter(s => s.section && !s.section.toLowerCase().includes('not provided') && !s.section.toLowerCase().includes('unknown') && s.section.trim() !== '').map(s=>{
  const jur = (s.jurisdiction||'NSW').toUpperCase();
  const actText = s.act||'';
  const jurInAct = actText.toUpperCase().includes(`(${jur})`);
  const secRaw = (s.section||'').trim();
  const secLower = secRaw.toLowerCase();
  const structural = /^(chapter|part|division|schedule|subpart)\s/.test(secLower);
  const alreadyPrefixed = /^s\s|^s\.|^ss\s|^ss\./.test(secLower);
  const secDisplay = structural || alreadyPrefixed ? secRaw : `s ${secRaw}`;
  return '<li>'+escHtml(`${secDisplay} ${actText}${jurInAct ? '' : ` (${jur})`}`.trim())+'</li>';
}).join('') + '</ul>' : ''}
${(ground.similar_cases||[]).filter(c=>c.case_name && c.case_name !== 'Case name' && !c.case_name.includes('[Surname]') && !c.case_name.includes('[Year]') && c.case_name !== 'None' && c.case_name !== 'optional' && !(c.citation || '').toLowerCase().includes('verification needed')).length ? '<h2>Comparable Authority</h2>' + ground.similar_cases.filter(c=>c.case_name && c.case_name !== 'Case name' && !c.case_name.includes('[Surname]') && !c.case_name.includes('[Year]') && c.case_name !== 'None' && c.case_name !== 'optional' && !(c.citation || '').toLowerCase().includes('verification needed')).map(c=>'<div class="case-box"><strong>'+escHtml(c.case_name)+'</strong>'+(c.citation ? ' &mdash; '+escHtml(c.citation) : '')+'</div>').join('') : ''}
${analysis ? '<h2>Deep Investigation Analysis</h2><div class="analysis">' + renderMarkdownToHtml(analysis) + '</div>' : ''}
<div class="disclaimer"><span class="disc-hazard">&#9888;</span><div><strong>NOT LEGAL ADVICE</strong><p>This application is an educational research tool only and does NOT constitute legal advice. All analysis must be independently verified by a qualified Australian legal professional. Australian law only. No solicitor-client relationship is created. No document, report, or output should be filed with, submitted to, or relied upon before any court, tribunal, or regulatory body.</p></div></div>
</body></html>`;
  };

  const handleGroundPrint = () => {
    if (!detailGround) return;
    const html = buildSingleGroundHtml(detailGround);
    const iframe = document.createElement("iframe");
    iframe.style.position = "fixed";
    iframe.style.left = "-9999px";
    iframe.style.width = "0";
    iframe.style.height = "0";
    document.body.appendChild(iframe);
    const doc = iframe.contentDocument || iframe.contentWindow.document;
    doc.open(); doc.write(html); doc.close();
    iframe.contentWindow.focus();
    iframe.contentWindow.print();
    setTimeout(() => document.body.removeChild(iframe), 5000);
  };

  const handleGroundPDF = () => {
    if (!detailGround) return;
    const html = buildSingleGroundHtml(detailGround);
    const w = window.open("", "_blank");
    if (w) {
      const doc = w.document;
      doc.open(); doc.write(html); doc.close();
      toast.success("PDF view opened — use Print / Save as PDF to download.");
    }
  };

  return (
    <div className="space-y-4" data-testid="grounds-container">
      {/* DO_NOT_UNDO — Sticky Investigation Progress Banner.
           Stays fixed at the top of the viewport whenever an investigation is running,
           so users always see the timer regardless of scroll position. */}
      {investigating && (
        <div className="fixed top-0 left-0 right-0 z-[9998] shadow-2xl" data-testid="investigate-sticky-banner">
          <div className="bg-blue-800 text-white px-4 py-3">
            <div className="max-w-4xl mx-auto flex items-center justify-between gap-4">
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 rounded-full bg-white/20 flex items-center justify-center shrink-0">
                  <Loader2 className="w-5 h-5 animate-spin text-white" />
                </div>
                <div>
                  <p className="text-sm sm:text-base font-bold text-white">
                    {investElapsed < 10
                      ? "Scanning Documents..."
                      : investElapsed < 30
                      ? "Analysing Case Law..."
                      : investElapsed < 60
                      ? "Building Deep Analysis..."
                      : "Finalising Investigation..."}
                  </p>
                  <p className="text-xs text-white/70">
                    {investElapsed < 10
                      ? "Reading case documents and extracting relevant passages"
                      : investElapsed < 30
                      ? "AI is cross-referencing legislation and precedents"
                      : investElapsed < 60
                      ? "Constructing a thorough deep investigation analysis"
                      : "Completing final sections — deep analysis can take 1-3 minutes"}
                  </p>
                </div>
              </div>
              <div className="text-right shrink-0">
                <span className="text-2xl sm:text-3xl font-mono font-bold text-white" data-testid="investigate-sticky-timer">
                  {investElapsed < 60 ? `${investElapsed}s` : `${Math.floor(investElapsed / 60)}m ${String(investElapsed % 60).padStart(2, '0')}s`}
                </span>
                <p className="text-[10px] text-white/50 uppercase tracking-wider">elapsed</p>
              </div>
            </div>
          </div>
          <div className="h-1.5 bg-blue-900">
            <div
              className="h-full bg-blue-400 transition-all duration-1000 ease-linear"
              style={{ width: `${Math.min(98, (investElapsed / 180) * 100)}%` }}
              data-testid="investigate-sticky-progress"
            />
          </div>
        </div>
      )}

      {/* Paywall Banner when not unlocked */}
      {!isUnlocked && groundsCount > 0 && (
        <Card className={trialEligible ? "bg-gradient-to-r from-blue-600 to-blue-800 border-blue-500 shadow-xl" : "bg-gradient-to-r from-blue-50 to-orange-50 border-blue-200"}>
          <CardContent className="p-6">
            {trialEligible && (
              <div className="mb-3 flex items-center gap-2">
                <Badge className="bg-pink-600 text-white text-xs font-bold px-3 py-1 rounded-full uppercase tracking-wider" data-testid="trial-badge">
                  One-Time Trial Offer
                </Badge>
                <span className="text-white/80 text-xs font-bold">First-time user exclusive</span>
              </div>
            )}
            <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
              <div className="flex items-center gap-4">
                <div className={`w-12 h-12 rounded-full flex items-center justify-center ${trialEligible ? 'bg-white/20' : 'bg-blue-100'}`}>
                  <Lock className={`w-6 h-6 ${trialEligible ? 'text-pink-300' : 'text-red-600'}`} />
                </div>
                <div>
                  <h3 className={`font-semibold text-sm sm:text-base ${trialEligible ? 'text-white' : 'text-slate-900'}`} style={{ fontFamily: "'Times New Roman', Times, serif" }}>
                    {groundsCount} Grounds of Merit Found!
                  </h3>
                  <p className={`text-xs sm:text-sm ${trialEligible ? 'text-white/80' : 'text-slate-600'}`}>
                    {trialEligible
                      ? "Try the full deep investigative analysis — see for yourself if it's worth it."
                      : "Unlock to see full details, evidence, and deep analysis for each ground."}
                  </p>
                </div>
              </div>
              <div className="flex gap-2 w-full sm:w-auto items-center">
                <Button 
                  onClick={async () => {
                    setCheckingPayment(true);
                    try {
                      onPaymentSuccess?.();
                      toast.info("Refreshing payment status...");
                    } finally {
                      setTimeout(() => setCheckingPayment(false), 1500);
                    }
                  }}
                  variant="outline"
                  disabled={checkingPayment}
                  className={trialEligible ? "text-white border-white/30 hover:bg-white/10" : "text-blue-700 border-blue-300 hover:bg-blue-50"}
                  data-testid="check-payment-status-btn"
                >
                  {checkingPayment ? <Loader2 className="w-4 h-4 animate-spin" /> : <Search className="w-4 h-4 mr-1" />}
                  {checkingPayment ? "Checking..." : "Refresh Status"}
                </Button>
                <Button 
                  onClick={() => setShowPaymentModal(true)}
                  className={trialEligible ? "bg-pink-600 hover:bg-pink-700 text-white font-bold shadow-lg" : "bg-blue-600 hover:bg-blue-700 text-white"}
                  data-testid="unlock-grounds-btn"
                >
                  <CreditCard className="w-4 h-4 mr-2" />
                  {trialEligible ? (
                    <span>
                      <span className="line-through opacity-60 mr-1">${unlockPrice?.toFixed(2)}</span>
                      ${trialPrice?.toFixed(2)} Trial
                    </span>
                  ) : (
                    `Unlock for $${unlockPrice?.toFixed(2)}`
                  )}
                </Button>
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      {groundsCount === 0 && grounds.length === 0 ? (
        <Card className="p-8 text-center">
          <Scale className="w-12 h-12 text-slate-300 mx-auto mb-4" />
          <h3 className="text-base font-semibold text-slate-900 mb-2" style={{ fontFamily: "'Times New Roman', Times, serif" }}>
            No grounds of merit identified
          </h3>
          <p className="text-xs text-slate-500 mb-4">
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
          {/* DO_NOT_UNDO — Dedup protection badge. Shows users the dedup system is active. */}
          {isUnlocked && grounds.length > 0 && (
            <div className="flex items-center gap-2 px-3 py-1.5 bg-emerald-50 border border-emerald-200 rounded-lg" data-testid="dedup-protection-badge">
              <CheckCircle className="w-3.5 h-3.5 text-emerald-600 flex-shrink-0" />
              <span className="text-xs text-emerald-700 font-medium">
                Dedup Protection Active — {grounds.length} unique {grounds.length === 1 ? 'ground' : 'grounds'} verified (12-topic classification)
              </span>
            </div>
          )}
          {/* DO NOT UNDO — Ground Priority Reorder button */}
          {isUnlocked && grounds.length > 1 && (
            <div className="flex items-center gap-2">
              {reorderMode ? (
                <>
                  <Button
                    data-testid="save-reorder-btn"
                    size="sm"
                    onClick={saveReorder}
                    disabled={savingOrder}
                    className="bg-blue-600 hover:bg-blue-700 text-white text-xs"
                  >
                    {savingOrder ? <Loader2 className="w-3 h-3 animate-spin mr-1" /> : <Check className="w-3 h-3 mr-1" />}
                    Save Order
                  </Button>
                  <Button
                    data-testid="cancel-reorder-btn"
                    size="sm"
                    variant="outline"
                    onClick={() => { setReorderMode(false); setOrderedGrounds(grounds); }}
                    className="text-xs"
                  >
                    Cancel
                  </Button>
                  <span className="text-xs text-slate-500 ml-1">Drag or use arrows to reorder grounds by priority</span>
                </>
              ) : (
                <Button
                  data-testid="reorder-grounds-btn"
                  size="sm"
                  variant="outline"
                  onClick={() => { setReorderMode(true); setOrderedGrounds([...grounds]); }}
                  className="text-xs gap-1"
                >
                  <ArrowUpDown className="w-3 h-3" />
                  Reorder Priority
                </Button>
              )}
            </div>
          )}
          {displayGrounds.map((ground, groundIdx) => {
            const strengthConfig = STRENGTH_CONFIG[ground.strength] || STRENGTH_CONFIG.moderate;
            const StrengthIcon = strengthConfig.icon;
            const statusConfig = STATUS_CONFIG[ground.status] || STATUS_CONFIG.identified;
            
            return (
              <Card 
                key={ground.ground_id} 
                className={`card-hover group ${selectedGround?.ground_id === ground.ground_id ? 'ring-2 ring-blue-500' : ''} ${reorderMode ? 'cursor-grab active:cursor-grabbing' : ''}`}
                data-testid={`ground-${ground.ground_id}`}
                draggable={reorderMode}
                onDragStart={reorderMode ? () => handleDragStart(groundIdx) : undefined}
                onDragEnter={reorderMode ? () => handleDragEnter(groundIdx) : undefined}
                onDragEnd={reorderMode ? handleDragEnd : undefined}
                onDragOver={reorderMode ? (e) => e.preventDefault() : undefined}
              >
                <CardContent className="p-4">
                  <div className="flex items-start justify-between">
                    {/* Reorder handle */}
                    {reorderMode && (
                      <div className="flex flex-col items-center gap-1 mr-3 pt-1" data-testid={`reorder-handle-${groundIdx}`}>
                        <div className="text-xs font-bold text-blue-600 w-5 h-5 flex items-center justify-center rounded-full bg-blue-100">{groundIdx + 1}</div>
                        <GripVertical className="w-4 h-4 text-slate-400" />
                        <button
                          onClick={(e) => { e.stopPropagation(); moveGround(groundIdx, -1); }}
                          disabled={groundIdx === 0}
                          className="p-0.5 hover:bg-slate-200 rounded disabled:opacity-30"
                          data-testid={`move-up-${groundIdx}`}
                        >
                          <svg className="w-3 h-3" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M18 15l-6-6-6 6"/></svg>
                        </button>
                        <button
                          onClick={(e) => { e.stopPropagation(); moveGround(groundIdx, 1); }}
                          disabled={groundIdx === displayGrounds.length - 1}
                          className="p-0.5 hover:bg-slate-200 rounded disabled:opacity-30"
                          data-testid={`move-down-${groundIdx}`}
                        >
                          <svg className="w-3 h-3" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M6 9l6 6 6-6"/></svg>
                        </button>
                      </div>
                    )}
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
                        className="font-bold text-slate-900 text-sm sm:text-base group-hover:text-blue-700 transition-colors"
                        style={{ fontFamily: "'Times New Roman', Times, serif" }}
                      >
                        {auSpelling(ground.title)}
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
                        <>
                          <p className="text-xs sm:text-sm text-slate-600 mt-1 leading-snug whitespace-pre-line">
                            {auSpelling(ground.description)}
                          </p>
                        </>
                      )}
                      
                      {/* Supporting Evidence Tags */}
                      {ground.supporting_evidence && ground.supporting_evidence.length > 0 && (
                        <EvidenceSummary items={ground.supporting_evidence} />
                      )}

                      {/* Appellate Pathway — DO NOT UNDO — blue box before Legal Framework */}
                      {ground.appellate_pathway && (
                        <div className="mt-2 p-2 bg-blue-50 border border-blue-200 rounded-lg" data-testid={`appellate-pathway-${ground.ground_id}`}>
                          <p className="text-xs font-bold text-blue-800">Appellate Pathway</p>
                          <p className="text-xs text-blue-700 mt-0.5">{auSpelling(ground.appellate_pathway)}</p>
                        </div>
                      )}
                      
                      {/* Law Sections Preview — DO NOT UNDO: displays actual legislation text */}
                      {ground.law_sections?.filter(s => s.section && !s.section.toLowerCase().includes('not provided') && !s.section.toLowerCase().includes('unknown') && s.section.trim() !== '').length > 0 && (
                        <div className="mt-2 p-2 bg-blue-50 border border-blue-200 rounded-lg" data-testid={`law-sections-${ground.ground_id}`}>
                          <div className="flex items-center gap-1.5 mb-1">
                            <BookOpen className="w-3.5 h-3.5 text-blue-600 flex-shrink-0" />
                            <span className="text-xs font-bold text-blue-800">Legal Framework</span>
                          </div>
                          <div className="space-y-1 ml-5">
                            {ground.law_sections.filter(s => s.section && !s.section.toLowerCase().includes('not provided') && !s.section.toLowerCase().includes('unknown') && s.section.trim() !== '').map((section, idx) => {
                              const jur = (section.jurisdiction || "NSW").toUpperCase();
                              const actText = section.act || "";
                              const jurAlreadyInAct = actText.toUpperCase().includes(`(${jur})`);
                              const secText = section.section.replace(/^s\s+/i, "");
                              return (
                                <div key={idx} className="text-xs text-blue-700 leading-snug">
                                  s {secText} {actText}{jurAlreadyInAct ? "" : ` (${jur})`}
                                </div>
                              );
                            })}
                          </div>
                        </div>
                      )}
                      
                      {/* Comparable Authority Preview — DO NOT UNDO: filtered for verified citations only */}
                      {ground.similar_cases?.filter(c => c.case_name && c.case_name !== "Case name" && !c.case_name.includes("[Surname]") && !c.case_name.includes("[Year]") && c.case_name !== "None" && c.case_name !== "optional" && !(c.citation || '').toLowerCase().includes('verification needed')).length > 0 && (
                        <div className="flex items-center gap-2 mt-1">
                          <Gavel className="w-4 h-4 text-slate-400" />
                          <span className="text-xs text-slate-500">
                            {ground.similar_cases.filter(c => c.case_name && c.case_name !== "Case name" && !c.case_name.includes("[Surname]") && !c.case_name.includes("[Year]") && c.case_name !== "None" && c.case_name !== "optional" && !(c.citation || '').toLowerCase().includes('verification needed')).length} comparable case{ground.similar_cases.filter(c => c.case_name && c.case_name !== "Case name" && !c.case_name.includes("[Surname]") && !c.case_name.includes("[Year]") && c.case_name !== "None" && c.case_name !== "optional" && !(c.citation || '').toLowerCase().includes('verification needed')).length > 1 ? 's' : ''} referenced
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
                        <div className="mt-2 text-xs text-pink-600 font-bold">
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

                      {/* DO NOT UNDO — Disclaimer at end of every ground */}
                      <div className="mt-3 p-2.5 bg-slate-50 border border-slate-200 rounded-lg" data-testid={`ground-disclaimer-${ground.ground_id}`}>
                        <p className="text-xs text-slate-500 leading-relaxed italic">
                          This analysis identifies potential appellate issues based on available material. It does not determine that the appeal will succeed. All grounds require refinement and verification by a qualified legal practitioner.
                        </p>
                      </div>
                    </div>
                    
                    <div className="flex flex-wrap items-center gap-1 mt-2 sm:mt-0 sm:ml-4 sm:flex-shrink-0">
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
                        className="bg-blue-600 hover:bg-blue-700 text-white border-blue-600"
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

                  {/* DO_NOT_UNDO — Full Investigation Timer Block matching report generation UI.
                       Shows elapsed timer, stage labels, and progress bar when investigating a ground. */}
                  {investigating === ground.ground_id && (
                    <div className="mt-3 rounded-xl overflow-hidden shadow-lg border-2 border-blue-300" data-testid={`ai-investigate-progress-${ground.ground_id}`}>
                      <div className="bg-blue-700 text-white px-4 py-3 sm:px-6 sm:py-4">
                        <div className="flex items-center justify-between flex-wrap gap-3">
                          <div className="flex items-center gap-3">
                            <div className="w-10 h-10 rounded-full bg-white/20 flex items-center justify-center">
                              <Loader2 className="w-5 h-5 animate-spin text-white" />
                            </div>
                            <div>
                              <p className="text-base sm:text-lg font-bold text-white">
                                {investElapsed < 10
                                  ? "Scanning Documents"
                                  : investElapsed < 30
                                  ? "Analysing Case Law"
                                  : investElapsed < 60
                                  ? "Building Deep Analysis"
                                  : "Finalising Investigation"}
                              </p>
                              <p className="text-xs sm:text-sm text-white/80">
                                {investElapsed < 10
                                  ? "Reading case documents and extracting relevant passages..."
                                  : investElapsed < 30
                                  ? "AI is cross-referencing legislation and precedents..."
                                  : investElapsed < 60
                                  ? "Constructing a thorough deep investigation analysis..."
                                  : "Completing final sections. Deep analysis can take 1-3 minutes."}
                              </p>
                            </div>
                          </div>
                          <div className="text-right">
                            <span className="text-2xl font-mono font-bold text-white">
                              {investElapsed < 60 ? `${investElapsed}s` : `${Math.floor(investElapsed / 60)}m ${String(investElapsed % 60).padStart(2, '0')}s`}
                            </span>
                            <p className="text-xs text-white/60">elapsed</p>
                          </div>
                        </div>
                      </div>
                      <div className="bg-blue-50 px-4 py-2 sm:px-6 sm:py-3">
                        <div className="flex items-center gap-3 mb-2">
                          {[
                            { label: "Scanning", active: investElapsed >= 0 },
                            { label: "Analysing", active: investElapsed >= 10 },
                            { label: "Writing", active: investElapsed >= 30 },
                            { label: "Finalising", active: investElapsed >= 60 },
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
                            style={{ width: `${Math.min(98, (investElapsed / 180) * 100)}%` }}
                          />
                        </div>
                      </div>
                    </div>
                  )}

                  {/* DO NOT UNDO — Caselaw Search Box for each ground */}
                  {searchOpen[ground.ground_id] && (
                    <div className="mt-3 p-3 bg-slate-50 border border-slate-200 rounded-lg" data-testid={`search-box-${ground.ground_id}`}>
                      <p className="text-xs font-bold text-slate-700 mb-2">Search verified case law databases for this ground</p>
                      <div className="flex gap-2 mb-2">
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
                          className="bg-blue-600 hover:bg-blue-500 text-white flex-shrink-0"
                          data-testid={`search-submit-${ground.ground_id}`}
                        >
                          <ExternalLink className="w-4 h-4 mr-1" />
                          AustLII
                        </Button>
                      </div>
                      <div className="flex flex-wrap gap-1">
                        <a href={`https://jade.io/search/?q=${encodeURIComponent(searchTerms[ground.ground_id] || ground.title)}`} target="_blank" rel="noopener noreferrer" className="inline-flex items-center gap-1 px-2 py-1 text-xs bg-blue-100 text-blue-700 rounded hover:bg-blue-200">
                          JADE <ExternalLink className="w-3 h-3" />
                        </a>
                        <a href={`https://www.caselaw.nsw.gov.au/search/advanced?query=${encodeURIComponent(searchTerms[ground.ground_id] || ground.title)}`} target="_blank" rel="noopener noreferrer" className="inline-flex items-center gap-1 px-2 py-1 text-xs bg-blue-100 text-blue-700 rounded hover:bg-blue-200">
                          NSW CaseLaw <ExternalLink className="w-3 h-3" />
                        </a>
                        <a href={`https://www.queenslandjudgments.com.au/caselaw/search?keyword=${encodeURIComponent(searchTerms[ground.ground_id] || ground.title)}`} target="_blank" rel="noopener noreferrer" className="inline-flex items-center gap-1 px-2 py-1 text-xs bg-blue-100 text-blue-700 rounded hover:bg-blue-200">
                          QLD Judgments <ExternalLink className="w-3 h-3" />
                        </a>
                        <a href={`https://scholar.google.com.au/scholar?q=${encodeURIComponent(searchTerms[ground.ground_id] || ground.title)}&hl=en&as_sdt=4`} target="_blank" rel="noopener noreferrer" className="inline-flex items-center gap-1 px-2 py-1 text-xs bg-blue-100 text-blue-700 rounded hover:bg-blue-200">
                          Google Scholar <ExternalLink className="w-3 h-3" />
                        </a>
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
            <DialogTitle style={{ fontFamily: "'Times New Roman', Times, serif" }} className="text-2xl flex items-center gap-3">
              <Scale className="w-6 h-6 text-red-600" />
              Ground of Merit Analysis
            </DialogTitle>
            {detailGround && (detailGround.deep_analysis?.full_analysis || detailGround.analysis) && (
              <div className="flex items-center gap-2 mt-2 flex-wrap">
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
                <Button variant="outline" size="sm" className="text-green-700 border-green-200 hover:bg-green-50" onClick={() => {
                  if (!detailGround) return;
                  window.open(`https://www.austlii.edu.au/cgi-bin/sinosrch.cgi?query=${encodeURIComponent(detailGround.title)}`, '_blank');
                }} data-testid="ground-search-austlii-btn">
                  <Search className="w-4 h-4 mr-1.5" /> Search AustLII
                </Button>
              </div>
            )}
            {/* Search Panel in Detail Dialog */}
            {detailGround && (
              <div className="flex flex-wrap gap-1 mt-2">
                <a href={`https://jade.io/search/?q=${encodeURIComponent(detailGround.title)}`} target="_blank" rel="noopener noreferrer" className="inline-flex items-center gap-1 px-2 py-1 text-xs bg-blue-100 text-blue-700 rounded hover:bg-blue-200" data-testid="detail-search-jade">
                  JADE <ExternalLink className="w-3 h-3" />
                </a>
                <a href={`https://www.caselaw.nsw.gov.au/search/advanced?query=${encodeURIComponent(detailGround.title)}`} target="_blank" rel="noopener noreferrer" className="inline-flex items-center gap-1 px-2 py-1 text-xs bg-blue-100 text-blue-700 rounded hover:bg-blue-200" data-testid="detail-search-nsw">
                  NSW CaseLaw <ExternalLink className="w-3 h-3" />
                </a>
                <a href={`https://www.queenslandjudgments.com.au/caselaw/search?keyword=${encodeURIComponent(detailGround.title)}`} target="_blank" rel="noopener noreferrer" className="inline-flex items-center gap-1 px-2 py-1 text-xs bg-blue-100 text-blue-700 rounded hover:bg-blue-200" data-testid="detail-search-qld">
                  QLD Judgments <ExternalLink className="w-3 h-3" />
                </a>
                <a href={`https://scholar.google.com.au/scholar?q=${encodeURIComponent(detailGround.title)}&hl=en&as_sdt=4`} target="_blank" rel="noopener noreferrer" className="inline-flex items-center gap-1 px-2 py-1 text-xs bg-blue-100 text-blue-700 rounded hover:bg-blue-200" data-testid="detail-search-scholar">
                  Google Scholar <ExternalLink className="w-3 h-3" />
                </a>
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
                    className="text-base md:text-xl font-bold text-slate-900"
                    style={{ fontFamily: "'Times New Roman', Times, serif" }}
                  >
                    {auSpelling(detailGround.title)}
                  </h3>
                  <p className="text-sm text-slate-600 mt-2 whitespace-pre-line">{auSpelling(detailGround.description)}</p>
                </div>

                {/* Supporting Evidence */}
                {detailGround.supporting_evidence && detailGround.supporting_evidence.length > 0 && (
                  <div>
                    <h4 className="text-base font-bold text-slate-900 mb-2 flex items-center gap-2">
                      <FileText className="w-4 h-4" />
                      Supporting Evidence
                    </h4>
                    <ul className="list-disc pl-5 space-y-1 text-slate-700 text-sm">
                      {detailGround.supporting_evidence.map((ev, idx) => {
                        const text = extractEvidenceText(ev);
                        if (!text) return null;
                        return <li key={idx}>{auSpelling(text)}</li>;
                      })}
                    </ul>
                  </div>
                )}

                {/* Law Sections */}
                {detailGround.law_sections && detailGround.law_sections.length > 0 && (
                  <div>
                    <h4 className="text-base font-bold text-slate-900 mb-2 flex items-center gap-2">
                      <BookOpen className="w-4 h-4" />
                      Relevant Law Sections
                    </h4>
                    <div className="space-y-2">
                      {detailGround.law_sections.map((section, idx) => {
                        const secRaw = (section.section || "").trim();
                        const secLower = secRaw.toLowerCase();
                        const structural = /^(chapter|part|division|schedule|subpart)\s/.test(secLower);
                        const alreadyPrefixed = /^s\s|^s\.|^ss\s|^ss\./.test(secLower);
                        const secDisplay = structural || alreadyPrefixed || !secRaw ? secRaw : `s ${secRaw}`;
                        return (
                          <div key={idx} className="bg-blue-50 border border-blue-200 rounded-lg p-3">
                            <div className="font-mono text-sm text-blue-800">
                              {secDisplay} {section.act}
                            </div>
                            <div className="text-xs text-blue-600 mt-1">
                              Jurisdiction: {section.jurisdiction}
                            </div>
                          </div>
                        );
                      })}
                    </div>
                  </div>
                )}

                {/* Comparable Authority — DO NOT UNDO */}
                {detailGround.similar_cases && detailGround.similar_cases.filter(c => c.case_name && c.case_name !== "Case name" && !c.case_name.includes("[Surname]") && !c.case_name.includes("[Year]") && c.case_name !== "None" && c.case_name !== "optional" && !(c.citation || '').toLowerCase().includes('verification needed')).length > 0 && (
                  <div>
                    <h4 className="text-base font-bold text-slate-900 mb-2 flex items-center gap-2">
                      <Gavel className="w-4 h-4" />
                      Comparable Authority
                      <span className="text-xs font-normal text-blue-600">(requires verification)</span>
                    </h4>
                    <div className="space-y-2">
                      {detailGround.similar_cases.filter(c => c.case_name && c.case_name !== "Case name" && !c.case_name.includes("[Surname]") && !c.case_name.includes("[Year]") && c.case_name !== "None" && c.case_name !== "optional" && !(c.citation || '').toLowerCase().includes('verification needed')).map((caseItem, idx) => (
                        <div key={idx} className="bg-blue-50 border border-blue-200 rounded-lg p-3">
                          <div className="font-medium text-blue-900">
                            {caseItem.case_name}
                            <UnverifiedBadge />
                          </div>
                          {caseItem.citation && (
                            <div className="font-mono text-xs text-blue-700 mt-1">
                              {caseItem.citation}
                            </div>
                          )}
                          {caseItem.relevance_note && (
                            <div className="text-xs text-slate-600 mt-1">{caseItem.relevance_note}</div>
                          )}
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {/* Legitimacy Score in Detail View */}
                {detailGround.legitimacy_scores && (
                  <div>
                    <h4 className="text-base font-bold text-slate-900 mb-2 flex items-center gap-2">
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
                    <h4 className="text-lg font-bold text-slate-900 mb-3 flex items-center gap-2">
                      <Sparkles className="w-5 h-5 text-red-600" />
                      Deep Investigation Analysis
                      <span className="text-xs font-normal text-slate-500">
                        Generated {formatDate(detailGround.deep_analysis.investigated_at)}
                      </span>
                    </h4>
                    <div className="bg-white border border-slate-200 rounded-lg p-4 text-sm">
                      {formatAnalysis(detailGround.deep_analysis.full_analysis)}
                    </div>
                  </div>
                )}

                {/* Basic Analysis (if no deep analysis) */}
                {!detailGround.deep_analysis?.full_analysis && detailGround.analysis && (
                  <div>
                    <h4 className="font-semibold text-slate-900 mb-2">Analysis</h4>
                    <div className="text-slate-700 whitespace-pre-wrap">
                      {auSpelling(detailGround.analysis)}
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
        price={trialEligible ? trialPrice : unlockPrice}
        useTrial={trialEligible}
        onPaymentSuccess={onPaymentSuccess}
      />
    </div>
  );
};

export default GroundsOfMerit;
