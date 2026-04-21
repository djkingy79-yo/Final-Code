/* ========================================================================
   DO NOT UNDO — ENTIRE FILE PROTECTED
   All features, functions, styles, and content in this file are approved
   and must be preserved. Do not remove, rename, or refactor any code.
   ======================================================================== */
import { useState, useEffect, useRef } from "react";
import { useParams, useNavigate, useLocation } from "react-router-dom";
import axios from "axios";
import { toast } from "sonner";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import { isIOSDevice } from "../utils/isIOS";
import { 
  Scale, ArrowLeft, FileText, Clock, Plus,
  Loader2, AlertCircle, Sparkles, Gavel,
  BookOpen, HelpCircle, TrendingUp,
  MessageSquare, Trash2, Printer, Pencil, Share2, Users, Download, RefreshCw
} from "lucide-react";
import { Button } from "../components/ui/button";
import { Input } from "../components/ui/input";
import { Card, CardContent } from "../components/ui/card";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "../components/ui/tabs";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogFooter,
} from "../components/ui/dialog";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "../components/ui/select";
import { Label } from "../components/ui/label";
import { Textarea } from "../components/ui/textarea";
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
} from "../components/ui/alert-dialog";
import { API } from "../App";
import Timeline from "../components/TimelineEnhanced";
import TimelineAnalysis from "../components/TimelineAnalysis";
import GroundsOfMerit from "../components/GroundsOfMerit";
import DeadlineTracker from "../components/DeadlineTracker";
import AppealChecklist from "../components/AppealChecklist";
import PaymentModal from "../components/PaymentModal";
import LegalFrameworkViewer from "../components/LegalFrameworkViewer";
import DocumentsSection from "../components/DocumentsSection";
import NotesSection from "../components/NotesSection";
import ReportsSection from "../components/ReportsSection";
import AiCostBadge from "../components/AiCostBadge";
import QuickExport from "../components/QuickExport";
import DocumentBundler from "../components/DocumentBundler";
import ShareCaseModal from "../components/ShareCaseModal";
import CaseChat from "../components/CaseChat";
import ActivityFeed from "../components/ActivityFeed";
import CaseStrengthMeter from "../components/CaseStrengthMeter";
import CasePipelineSummary from "../components/CasePipelineSummary";
import PipelineStalenessAlert from "../components/PipelineStalenessAlert";
import PipelineProgress from "../components/PipelineProgress";
import CaseLawPanel from "../components/CaseLawPanel";
import { buildExportHtml } from "../utils/exportHtml";
import ExportOptionsModal from "../components/ExportOptionsModal";
import auSpelling from "../utils/auSpelling";

const EVENT_TYPES = [
  // Pre-trial
  { value: "arrest", label: "Arrest", category: "pre_trial" },
  { value: "charge", label: "Charge", category: "pre_trial" },
  { value: "bail_hearing", label: "Bail Hearing", category: "pre_trial" },
  { value: "committal", label: "Committal", category: "pre_trial" },
  { value: "indictment", label: "Indictment", category: "pre_trial" },
  // Trial
  { value: "jury_selection", label: "Jury Selection", category: "trial" },
  { value: "opening_statements", label: "Opening Statements", category: "trial" },
  { value: "witness_testimony", label: "Witness Testimony", category: "trial" },
  { value: "cross_examination", label: "Cross Examination", category: "trial" },
  { value: "closing_arguments", label: "Closing Arguments", category: "trial" },
  { value: "jury_deliberation", label: "Jury Deliberation", category: "trial" },
  { value: "verdict", label: "Verdict", category: "trial" },
  // Evidence
  { value: "evidence_discovery", label: "Evidence Discovery", category: "evidence" },
  { value: "forensic_report", label: "Forensic Report", category: "evidence" },
  { value: "expert_opinion", label: "Expert Opinion", category: "evidence" },
  { value: "disclosure", label: "Disclosure", category: "evidence" },
  // Post-conviction
  { value: "sentencing", label: "Sentencing", category: "post_conviction" },
  { value: "appeal_lodged", label: "Appeal Lodged", category: "post_conviction" },
  { value: "leave_application", label: "Leave Application", category: "post_conviction" },
  { value: "appeal_hearing", label: "Appeal Hearing", category: "post_conviction" },
  // Investigation
  { value: "police_interview", label: "Police Interview", category: "investigation" },
  { value: "erisp_recording", label: "ERISP Recording", category: "investigation" },
  { value: "crime_scene", label: "Crime Scene", category: "investigation" },
  { value: "search_warrant", label: "Search Warrant", category: "investigation" },
  // General
  { value: "court_hearing", label: "Court Hearing", category: "general" },
  { value: "other", label: "Other Event", category: "general" }
];

const EVENT_CATEGORIES = [
  { value: "pre_trial", label: "Pre-Trial" },
  { value: "trial", label: "Trial" },
  { value: "evidence", label: "Evidence" },
  { value: "post_conviction", label: "Post-Conviction" },
  { value: "investigation", label: "Investigation" },
  { value: "general", label: "General" }
];

const SIGNIFICANCE_LEVELS = [
  { value: "critical", label: "Critical - Key to appeal" },
  { value: "important", label: "Important - Significant event" },
  { value: "normal", label: "Normal - Standard event" },
  { value: "minor", label: "Minor - Background context" }
];

const PERSPECTIVES = [
  { value: "neutral", label: "Neutral" },
  { value: "prosecution", label: "Favours Prosecution" },
  { value: "defence", label: "Favours Defence" }
];

const GROUND_TYPES = [
  { value: "procedural_error", label: "Procedural Error" },
  { value: "fresh_evidence", label: "Fresh Evidence" },
  { value: "miscarriage_of_justice", label: "Miscarriage of Justice" },
  { value: "sentencing_error", label: "Sentencing Error" },
  { value: "judicial_error", label: "Judicial Error" },
  { value: "ineffective_counsel", label: "Ineffective Counsel" },
  { value: "prosecution_misconduct", label: "Prosecution Misconduct" },
  { value: "jury_irregularity", label: "Jury Irregularity" },
  { value: "constitutional_violation", label: "Constitutional Violation" },
  { value: "other", label: "Other Ground" }
];

const CaseDetail = ({ user }) => {
  const { caseId } = useParams();
  const location = useLocation();
  const navigate = useNavigate();
  const caseRequestRef = useRef(0);
  const [caseData, setCaseData] = useState(null);
  const [documents, setDocuments] = useState([]);
  const [timeline, setTimeline] = useState([]);
  const [reports, setReports] = useState([]);
  const [notes, setNotes] = useState([]);
  // Export Options picker — fires before Print/PDF/Word All
  const [exportOpen, setExportOpen] = useState(false);
  const [exportMode, setExportMode] = useState("print"); // "print" | "pdf" | "word"
  const [grounds, setGrounds] = useState([]);
  const [groundsCount, setGroundsCount] = useState(0);
  const [groundsUnlocked, setGroundsUnlocked] = useState(false);
  const [groundsUnlockPrice, setGroundsUnlockPrice] = useState(99.00);
  const [paymentSummary, setPaymentSummary] = useState({ payments: [], unlocked_features: {}, latest_status_by_feature: {} });
  const [loading, setLoading] = useState(true);
  const [loadError, setLoadError] = useState(null);
  const VALID_TABS = ["documents", "timeline", "grounds", "notes", "reports", "progress", "chat"];
  const [activeTab, setActiveTab] = useState(() => {
    const tab = new URLSearchParams(window.location.search).get("tab") || "documents";
    return VALID_TABS.includes(tab) ? tab : "documents";
  });

  // Dialog states
  const [showEventDialog, setShowEventDialog] = useState(false);
  const [showGroundDialog, setShowGroundDialog] = useState(false);
  const [investigatingGround, setInvestigatingGround] = useState(null);
  const [autoIdentifying, setAutoIdentifying] = useState(false);
  const [refreshingLegalRefs, setRefreshingLegalRefs] = useState(false);
  const [selectedGround, setSelectedGround] = useState(null);
  const [generatingTimeline, setGeneratingTimeline] = useState(false);
  const [analyzingTimeline, setAnalyzingTimeline] = useState(false);
  const [showDeleteCaseDialog, setShowDeleteCaseDialog] = useState(false);
  const [deleteEventId, setDeleteEventId] = useState(null);
  const [deleteGroundId, setDeleteGroundId] = useState(null);
  const [showShareModal, setShowShareModal] = useState(false);
  const [timelineAnalysis, setTimelineAnalysis] = useState(null);
  const [generatingProgress, setGeneratingProgress] = useState(false);
  const [progressAnalysis, setProgressAnalysis] = useState(null);
  const [showEditCaseDialog, setShowEditCaseDialog] = useState(false);
  const [editCaseData, setEditCaseData] = useState(null);
  const [savingCase, setSavingCase] = useState(false);

  const [newEvent, setNewEvent] = useState({
    title: "",
    description: "",
    event_date: "",
    event_type: "other",
    event_category: "general",
    significance: "normal",
    perspective: "neutral",
    source_citation: "",
    is_contested: false,
    contested_details: "",
    linked_documents: [],
    participants: [],
    related_grounds: [],
    inconsistency_notes: ""
  });

  const [newGround, setNewGround] = useState({
    title: "",
    description: "",
    ground_type: "other",
    strength: "moderate",
    supporting_evidence: []
  });

  useEffect(() => {
    const requestedTab = new URLSearchParams(location.search).get("tab");
    if (requestedTab) {
      setActiveTab(requestedTab);
    }
  }, [location.search]);

  useEffect(() => {
    const requestId = caseRequestRef.current + 1;
    caseRequestRef.current = requestId;
    setCaseData(null);
    setDocuments([]);
    setTimeline([]);
    setReports([]);
    setNotes([]);
    setGrounds([]);
    setGroundsCount(0);
    setLoading(true);
    fetchCaseData(requestId);
    
    // Handle payment return
    const params = new URLSearchParams(window.location.search);
    const paymentStatus = params.get('payment');
    
    if (paymentStatus === 'success') {
      toast.success('Payment successful! Feature unlocked.');
      window.history.replaceState({}, '', `/cases/${caseId}`);
    } else if (paymentStatus === 'cancelled') {
      toast.info('Payment was cancelled.');
      window.history.replaceState({}, '', `/cases/${caseId}`);
    }
  }, [caseId]); // eslint-disable-line react-hooks/exhaustive-deps

  const fetchCaseData = async (requestId = caseRequestRef.current) => {
    setLoadError(null);
    setLoading(true);
    try {
      // Fetch case data first to verify access (generous timeout — case docs/grounds can grow)
      const caseRes = await axios.get(`${API}/cases/${caseId}`, { timeout: 90000 });
      if (requestId !== caseRequestRef.current) return;
      setCaseData(caseRes.data);
      
      // Then fetch related data - use Promise.allSettled for resilience (generous timeouts)
      const [docsRes, timelineRes, reportsRes, notesRes, groundsRes, paymentsRes, barristerRes] = await Promise.allSettled([
        axios.get(`${API}/cases/${caseId}/documents`, { timeout: 90000 }),
        axios.get(`${API}/cases/${caseId}/timeline`, { timeout: 60000 }),
        axios.get(`${API}/cases/${caseId}/reports`, { timeout: 60000 }),
        axios.get(`${API}/cases/${caseId}/notes`, { timeout: 60000 }),
        axios.get(`${API}/cases/${caseId}/grounds`, { timeout: 60000 }),
        axios.get(`${API}/cases/${caseId}/payments`, { timeout: 60000 }),
        axios.get(`${API}/cases/${caseId}/reports/barrister-view`, { timeout: 60000 })
      ]);
      if (requestId !== caseRequestRef.current) return;
      
      // Set data from successful responses, empty arrays for failed ones
      setDocuments(docsRes.status === 'fulfilled' ? docsRes.value.data : []);
      setTimeline(timelineRes.status === 'fulfilled' ? timelineRes.value.data : []);
      
      // Combine standard reports with barrister report if it exists and is completed
      const standardReports = reportsRes.status === 'fulfilled' ? reportsRes.value.data : [];
      const barristerReport = barristerRes.status === 'fulfilled' ? barristerRes.value.data : null;
      if (barristerReport && barristerReport.status === 'completed' && barristerReport.report_id) {
        const alreadyIncluded = standardReports.some(r => r.report_id === barristerReport.report_id);
        if (!alreadyIncluded) {
          standardReports.push(barristerReport);
        }
      }
      setReports(standardReports);
      setNotes(notesRes.status === 'fulfilled' ? notesRes.value.data : []);
      setPaymentSummary(paymentsRes.status === 'fulfilled' ? paymentsRes.value.data : { payments: [], unlocked_features: {}, latest_status_by_feature: {} });
      
      // Handle grounds response with paywall info
      if (groundsRes.status === 'fulfilled') {
        const groundsData = groundsRes.value.data;
        setGrounds(groundsData.grounds || []);
        setGroundsCount(groundsData.count || 0);
        setGroundsUnlocked(groundsData.is_unlocked || false);
        setGroundsUnlockPrice(groundsData.unlock_price || 99.00);
      } else {
        setGrounds([]);
        setGroundsCount(0);
      }
      
    } catch (error) {
      if (requestId !== caseRequestRef.current) return;
      console.error("Failed to load case:", error);
      if (error.response?.status === 401) {
        setLoadError("Session expired. Please log in again.");
        setTimeout(() => navigate("/"), 2000);
      } else if (error.response?.status === 404) {
        setLoadError("Case not found");
      } else if (error.code === 'ECONNABORTED') {
        setLoadError("Request timed out. Please try again.");
      } else {
        setLoadError("Failed to load case data. Please try again.");
      }
    } finally {
      if (requestId !== caseRequestRef.current) return;
      setLoading(false);
    }
  };

  const handleCreateEvent = async () => {
    if (!newEvent.title || !newEvent.event_date) {
      toast.error("Title and date are required");
      return;
    }

    try {
      const response = await axios.post(`${API}/cases/${caseId}/timeline`, newEvent);
      setTimeline([...timeline, response.data].sort((a, b) => 
        new Date(a.event_date) - new Date(b.event_date)
      ));
      setShowEventDialog(false);
      setNewEvent({ 
        title: "", 
        description: "", 
        event_date: "", 
        event_type: "other",
        event_category: "general",
        significance: "normal",
        perspective: "neutral",
        source_citation: "",
        is_contested: false,
        contested_details: "",
        linked_documents: [],
        participants: [],
        related_grounds: [],
        inconsistency_notes: ""
      });
      toast.success("Event added to timeline");
    } catch (error) {
      toast.error("Failed to add event");
    }
  };

  const handleDeleteEvent = async (eventId) => {
    setDeleteEventId(eventId);
  };
  
  const confirmDeleteEvent = async () => {
    const eventId = deleteEventId;
    setDeleteEventId(null);
    try {
      await axios.delete(`${API}/cases/${caseId}/timeline/${eventId}`);
      setTimeline(timeline.filter(e => e.event_id !== eventId));
      toast.success("Event deleted");
    } catch (error) {
      toast.error("Failed to delete event");
    }
  };

  const handleReorderEvent = async (eventId, direction) => {
    try {
      const response = await axios.post(`${API}/cases/${caseId}/timeline/reorder`, {
        event_id: eventId,
        direction: direction
      });
      if (response.data.events) {
        setTimeline(response.data.events);
      }
      toast.success(`Event moved ${direction}`);
    } catch (error) {
      toast.error("Failed to reorder event");
    }
  };


  const handleGenerateTimeline = async () => {
    if (documents.filter(d => d.content_text).length === 0) {
      toast.error("No documents with extracted text. Please upload documents and extract text first.");
      return;
    }

    // Soft metadata gate
    const warnings = caseData?.metadata_warnings || [];
    if (warnings.length > 0) {
      const proceed = window.confirm(
        "Missing case details may reduce accuracy:\n\n" +
        warnings.map(w => "• " + w).join("\n") +
        "\n\nProceed anyway?"
      );
      if (!proceed) return;
    }
    
    setGeneratingTimeline(true);
    toast.info("Analysing documents to generate timeline... This may take 30-60 seconds.");
    
    try {
      const response = await axios.post(`${API}/cases/${caseId}/timeline/auto-generate`, {}, {
        timeout: 180000 // 3 minute timeout
      });
      
      // Refresh timeline
      const timelineRes = await axios.get(`${API}/cases/${caseId}/timeline`);
      setTimeline(timelineRes.data);
      
      toast.success(`Generated ${response.data.events_created} timeline events from documents!`);
    } catch (error) {
      console.error("Timeline generation error:", error);
      if (error.code === 'ECONNABORTED' || error.message?.includes('timeout')) {
        toast.error("Timeline generation timed out. Please try again.");
      } else if (error.response?.data?.detail) {
        toast.error(`Failed: ${error.response.data.detail}`);
      } else {
        toast.error("Failed to generate timeline. Please try again.");
      }
    } finally {
      setGeneratingTimeline(false);
    }
  };

  const handleAnalyseTimeline = async () => {
    if (timeline.length < 2) {
      toast.error("Need at least 2 timeline events for analysis");
      return;
    }
    
    setAnalyzingTimeline(true);
    toast.info("Analysing timeline for gaps, inconsistencies, and insights...");
    
    try {
      const response = await axios.post(`${API}/cases/${caseId}/timeline/analyse`, {}, {
        timeout: 120000
      });
      setTimelineAnalysis(response.data.analysis);
      toast.success("Timeline analysis complete!");
    } catch (error) {
      console.error("Timeline analysis error:", error);
      toast.error("Failed to analyse timeline. Please try again.");
    } finally {
      setAnalyzingTimeline(false);
    }
  };

  const handleExportTimelinePDF = async () => {
    try {
      const isIOS = isIOSDevice();
      if (isIOS) {
        const { buildSecureDownloadUrl } = await import("../utils/downloadToken");
        const baseUrl = `${API}/cases/${caseId}/timeline/export-pdf`;
        const href = await buildSecureDownloadUrl(baseUrl);
        const a = document.createElement('a');
        a.href = href;
        a.target = '_blank';
        a.rel = 'noopener';
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        toast.success("PDF opening — use Share to save or print.");
        return;
      }
      const response = await axios.get(`${API}/cases/${caseId}/timeline/export-pdf`, {
        responseType: 'blob'
      });
      
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `timeline_${caseData?.title?.replace(/\s+/g, '_') || 'case'}.pdf`);
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(url);
      
      toast.success("Timeline PDF exported!");
    } catch (error) {
      console.error("PDF export error:", error);
      toast.error("Failed to export timeline PDF");
    }
  };

  const buildTabPreviewHtml = (contentHtml, tabLabel, noticeHtml) => `<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>${caseData?.title || 'Case'} — ${tabLabel}</title>
  <style>
    @page { size: A4; margin: 18mm 18mm 26mm; }
    body { font-family: 'Times New Roman', Times, serif; padding: 24px; color: #0f172a; line-height: 1.5; font-size: 11pt; }
    h1 { font-family: 'Times New Roman', Times, serif; font-size: 15pt; margin-bottom: 4px; color: #0f172a; }
    h2 { font-family: 'Times New Roman', Times, serif; font-size: 13pt; margin-top: 14px; border-bottom: 2px solid #1e3a8a; padding-bottom: 3px; color: #0f172a; }
    h3 { font-size: 11pt; margin-top: 10px; color: #1e40af; }
    p { font-size: 11pt; line-height: 1.5; margin-bottom: 5px; }
    .meta { font-size: 10pt; color: #475569; margin-bottom: 8px; }
    .notice { background: #eff6ff; border: 1px solid #93c5fd; padding: 6px 10px; border-radius: 6px; color: #1e3a8a; margin-bottom: 10px; font-size: 10pt; }
    table { border-collapse: collapse; width: 100%; margin: 8px 0; font-size: 9pt; page-break-before: always; }
    td, th { border: 1px solid #cbd5e1; padding: 4px 6px; text-align: left; font-size: 9pt; word-wrap: break-word; overflow-wrap: break-word; }
    th { background: #1d4ed8; color: #fff; font-weight: 700; -webkit-print-color-adjust: exact; print-color-adjust: exact; }
    ul, ol { padding-left: 2rem; }
    li { margin-bottom: 2px; font-size: 11pt; line-height: 1.5; }
    .disclaimer-box { background: #dc2626; border: 2px solid #b91c1c; padding: 10px 14px; border-radius: 6px; margin-top: 16px; page-break-inside: avoid; break-inside: avoid; display: flex; gap: 10px; align-items: flex-start; -webkit-print-color-adjust: exact; print-color-adjust: exact; }
    .disclaimer-box .disc-hazard { font-size: 22px; color: #facc15; flex-shrink: 0; }
    .disclaimer-box strong { font-size: 10pt; text-transform: uppercase; letter-spacing: 0.06em; color: #ffffff; display: block; margin-bottom: 3px; }
    .disclaimer-box p { font-size: 8pt; color: #ffffff; margin: 0; line-height: 1.4; font-weight: 700; }
    .no-print { display: none !important; }
    .print-footer { display: none; position: fixed; left: 0; right: 0; bottom: 0; background: #fff; border-top: 1px solid #1d4ed8; padding: 3px 18mm 4px; }
    .print-footer-row { display: flex; justify-content: space-between; align-items: center; font-size: 7pt; font-style: italic; color: #475569; font-family: 'Times New Roman', Times, serif; }
    .print-footer-page::after { content: ''; }
    @media print { * { -webkit-print-color-adjust: exact !important; print-color-adjust: exact !important; color-adjust: exact !important; } body { print-color-adjust: exact; -webkit-print-color-adjust: exact; } .disclaimer-box { page-break-inside: avoid; break-inside: avoid; } .print-footer { display: block; } .print-footer-page::after { content: "Page " counter(page) " of " counter(pages); } }
  </style>
</head>
<body>
  ${noticeHtml}
  <h1>${caseData?.title || ''} — ${tabLabel}</h1>
  <div class="meta">${caseData?.defendant_name || ''} | ${caseData?.case_number || ''} | ${caseData?.court || ''}</div>
  <hr />
  ${contentHtml}
  <div class="disclaimer-box">
    <span class="disc-hazard">&#9888;</span>
    <div>
    <strong>NOT LEGAL ADVICE</strong>
    <p>This application is an educational research tool only and does NOT constitute legal advice. It must NOT be relied upon as such. The creator of this application is not a lawyer. All analysis, findings, reports, and recommendations generated by this tool must be independently verified by a qualified Australian legal professional before any action is taken. This tool covers Australian law only. No solicitor-client relationship is created by using this service. No document, report, or output generated by this Application should be filed with, submitted to, or relied upon before any court, tribunal, or regulatory body.</p>
    </div>
  </div>
  <div class="print-footer">
    <div class="print-footer-row">
      <span>Criminal Law Appeal Management / ${tabLabel} — ${caseData?.defendant_name || 'Appellant'} — ${new Date().toLocaleDateString('en-AU')}</span>
      <span class="print-footer-page"></span>
    </div>
  </div>
</body>
</html>`;

  const openTabPrintPreview = (mode = "print") => {
    const contentEl = document.querySelector('[data-tab-content][data-state="active"]') || document.querySelector('[data-tab-content]');
    if (!contentEl) {
      toast.error("Nothing to export on this tab.");
      return;
    }
    const contentHtml = (contentEl.innerHTML || "").trim();
    if (!contentHtml) {
      toast.error("Nothing to export on this tab.");
      return;
    }
    const tabLabel = activeTab.charAt(0).toUpperCase() + activeTab.slice(1);
    const noticeHtml = mode === "pdf"
      ? '<div class="notice no-print">PDF preview — use Print / Save as PDF to download.</div>'
      : '';
    const html = buildTabPreviewHtml(contentHtml, tabLabel, noticeHtml);

    // Always use document-preview route for iOS compatibility
    const isIOS = /iPad|iPhone|iPod/.test(navigator.userAgent) || (navigator.platform === 'MacIntel' && navigator.maxTouchPoints > 1);
    if (isIOS) {
      localStorage.setItem("document-preview-payload", JSON.stringify({
        html,
        mode,
        title: `${tabLabel} — ${mode === "print" ? "Print" : mode === "word" ? "Word" : "PDF"} View`,
        source: "tab-export",
        returnTo: `/cases/${caseId}`,
        createdAt: Date.now(),
      }));
      window.location.assign(`${window.location.origin}/document-preview?mode=${mode}`);
      return;
    }

    const previewWindow = window.open("", "_blank", "width=1200,height=800");
    if (!previewWindow) {
      // Fallback: use document-preview route instead of blob
      localStorage.setItem("document-preview-payload", JSON.stringify({
        html,
        mode,
        title: `${tabLabel} — ${mode === "print" ? "Print" : mode === "word" ? "Word" : "PDF"} View`,
        source: "tab-export",
        returnTo: `/cases/${caseId}`,
        createdAt: Date.now(),
      }));
      window.location.assign(`${window.location.origin}/document-preview?mode=${mode}`);
      return;
    }
    const doc = previewWindow.document;
    doc.open();
    doc.write(html);
    doc.close();
    previewWindow.focus();
    if (mode === "print") {
      setTimeout(() => previewWindow.print(), 600);
      toast.success("Print dialogue opening...");
      return;
    }
    toast.success("PDF view opened — use Print / Save as PDF to download.");
  };

  const handleOpenEditCase = () => {
    setEditCaseData({
      title: caseData?.title || "",
      defendant_name: caseData?.defendant_name || "",
      case_number: caseData?.case_number || "",
      court: caseData?.court || "",
      judge: caseData?.judge || "",
      state: caseData?.state || "nsw",
      offence_category: caseData?.offence_category || "other",
      offence_type: caseData?.offence_type || "",
      sentence: caseData?.sentence || "",
      summary: caseData?.summary || ""
    });
    setShowEditCaseDialog(true);
  };

  const handleSaveCase = async () => {
    if (!editCaseData?.title?.trim()) {
      toast.error("Case title is required");
      return;
    }
    setSavingCase(true);
    try {
      await axios.put(`${API}/cases/${caseId}`, editCaseData);
      setCaseData({ ...caseData, ...editCaseData });
      setShowEditCaseDialog(false);
      toast.success("Case details updated");
    } catch (error) {
      console.error("Save case error:", error);
      toast.error("Failed to update case details");
    } finally {
      setSavingCase(false);
    }
  };

  // Payment modal state
  const [showPaymentModal, setShowPaymentModal] = useState(false);
  const [pendingFeatureType, setPendingFeatureType] = useState(null);
  const [pendingFeaturePrice, setPendingFeaturePrice] = useState(null);

  // Grounds of Merit handlers
  const handleCreateGround = async () => {
    if (!newGround.title || !newGround.description) {
      toast.error("Title and description are required");
      return;
    }

    try {
      const response = await axios.post(`${API}/cases/${caseId}/grounds`, newGround);
      setGrounds([response.data, ...grounds]);
      setShowGroundDialog(false);
      setNewGround({ title: "", description: "", ground_type: "other", strength: "moderate", supporting_evidence: [] });
      toast.success("Ground of merit added");
    } catch (error) {
      toast.error("Failed to add ground of merit");
    }
  };

  const handleInvestigateGround = async (groundId) => {
    setInvestigatingGround(groundId);
    toast.info("Investigating ground — this runs in the background...");
    try {
      // Start the background investigation
      const startResponse = await axios.post(`${API}/cases/${caseId}/grounds/${groundId}/investigate`, {}, {
        timeout: 30000
      });
      const taskId = startResponse.data?.task_id;
      if (!taskId) {
        // Old-style direct response (fallback)
        if (startResponse.data?.ground_id) {
          setGrounds(grounds.map(g => g.ground_id === groundId ? startResponse.data : g));
          toast.success("Deep investigation complete!");
          setInvestigatingGround(null);
          return;
        }
        throw new Error("No task_id returned");
      }

      // Poll for completion
      const pollInterval = 3000;
      const maxAttempts = 60; // 3 minutes max
      for (let attempt = 0; attempt < maxAttempts; attempt++) {
        await new Promise(r => setTimeout(r, pollInterval));
        try {
          const statusRes = await axios.get(
            `${API}/cases/${caseId}/grounds/${groundId}/investigate/status?task_id=${taskId}`,
            { timeout: 15000 }
          );
          const { status, progress, result, error } = statusRes.data;

          if (status === "completed" && result) {
            setGrounds(prev => prev.map(g => g.ground_id === groundId ? result : g));
            toast.success("Deep investigation complete!");
            setInvestigatingGround(null);
            return;
          }
          if (status === "failed") {
            toast.error(error || "Investigation failed. Please try again.");
            setInvestigatingGround(null);
            return;
          }
          // Still running — update progress toast
          if (attempt % 3 === 0) {
            toast.info(progress || "Investigating...", { id: "investigate-progress" });
          }
        } catch {
          // Poll failed — keep trying
        }
      }
      toast.error("Investigation timed out. Please check the ground — it may have completed.");
    } catch (error) {
      console.error("Investigate error:", error);
      toast.error("Failed to start investigation. Please try again.");
    } finally {
      setInvestigatingGround(null);
    }
  };

  const handleDeleteGround = async (groundId) => {
    setDeleteGroundId(groundId);
  };
  
  const confirmDeleteGround = async () => {
    const groundId = deleteGroundId;
    setDeleteGroundId(null);
    try {
      await axios.delete(`${API}/cases/${caseId}/grounds/${groundId}`);
      setGrounds(grounds.filter(g => g.ground_id !== groundId));
      toast.success("Ground of merit deleted");
    } catch (error) {
      toast.error("Failed to delete ground");
    }
  };

  const handleAutoIdentifyGrounds = async () => {
    // Soft metadata gate — warn but don't block
    const warnings = caseData?.metadata_warnings || [];
    if (warnings.length > 0) {
      const proceed = window.confirm(
        "Missing case details may reduce accuracy:\n\n" +
        warnings.map(w => "• " + w).join("\n") +
        "\n\nProceed anyway?"
      );
      if (!proceed) return;
    }
    setAutoIdentifying(true);
    toast.info("Starting AI analysis — this runs in the background for large cases.");
    try {
      // Step 1: Start the background task
      const startRes = await axios.post(`${API}/cases/${caseId}/grounds/auto-identify`, {}, {
        timeout: 30000
      });

      const { task_id, status: startStatus } = startRes.data;

      if (startStatus === "already_running") {
        toast.info("Analysis is already in progress. Waiting for results...");
      }

      if (!task_id) {
        // Legacy fallback — endpoint returned results directly
        const { identified_count, skipped_duplicates, existing_grounds, unlock_price } = startRes.data;
        const groundsRes = await axios.get(`${API}/cases/${caseId}/grounds`);
        setGrounds(groundsRes.data.grounds || []);
        setGroundsCount(groundsRes.data.count || 0);
        setGroundsUnlocked(groundsRes.data.is_unlocked || false);
        setGroundsUnlockPrice(groundsRes.data.unlock_price || 99.00);
        if (identified_count > 0) {
          toast.success(`Identified ${identified_count} potential ground(s)! Pay $${unlock_price?.toFixed(2)} to unlock full details.`);
        } else {
          toast.info(existing_grounds > 0 ? "All significant grounds have already been identified." : "No grounds identified. Try adding more documents.");
        }
        setAutoIdentifying(false);
        return;
      }

      // Step 2: Poll for completion
      let attempts = 0;
      const maxAttempts = 120; // 10 minutes max (5s intervals)
      const pollInterval = 5000;

      const poll = async () => {
        attempts++;
        try {
          const statusRes = await axios.get(`${API}/cases/${caseId}/grounds/auto-identify/status`);
          const { status, result, error, progress } = statusRes.data;

          if (status === "completed" && result) {
            const { identified_count, skipped_duplicates, existing_grounds, unlock_price } = result;
            // ALWAYS refresh grounds list after auto-identify — DO NOT skip this
            const groundsRes = await axios.get(`${API}/cases/${caseId}/grounds`);
            setGrounds(groundsRes.data.grounds || []);
            setGroundsCount(groundsRes.data.count || 0);
            setGroundsUnlocked(groundsRes.data.is_unlocked || false);
            setGroundsUnlockPrice(groundsRes.data.unlock_price || 99.00);

            if (identified_count > 0) {
              if (skipped_duplicates > 0) {
                toast.success(`Found ${identified_count} new ground(s)! ${skipped_duplicates} duplicate(s) skipped. Pay $${unlock_price?.toFixed(2)} to see full details.`);
              } else {
                toast.success(`Identified ${identified_count} potential ground(s)! Pay $${unlock_price?.toFixed(2)} to unlock full details.`);
              }
            } else {
              toast.info(existing_grounds > 0 ? "All significant grounds have already been identified for this case." : "No grounds identified. Try adding more case documents with detailed content.");
            }
            setAutoIdentifying(false);
            return;
          }

          if (status === "failed") {
            toast.error(error ? `Analysis failed: ${error}` : "AI analysis encountered an error. Please try again in a moment.");
            setAutoIdentifying(false);
            return;
          }

          // Still running
          if (attempts >= maxAttempts) {
            toast.error("Analysis is taking longer than expected. Please check back shortly — results will appear when ready.");
            setAutoIdentifying(false);
            return;
          }

          // Continue polling
          setTimeout(poll, pollInterval);
        } catch (pollErr) {
          console.error("Poll error:", pollErr);
          if (attempts >= maxAttempts) {
            toast.error("Lost connection to the analysis. Please refresh the page to check for results.");
            setAutoIdentifying(false);
          } else {
            setTimeout(poll, pollInterval);
          }
        }
      };

      // Start polling after a short initial delay
      setTimeout(poll, 3000);

    } catch (error) {
      console.error("Auto-identify error:", error);
      if (error.code === 'ECONNABORTED' || error.message?.includes('timeout')) {
        toast.error("Ground analysis timed out. Please retry — the analysis runs in the background for large cases.");
      } else {
        const detail = error?.response?.data?.detail || "";
        if (error?.response?.status === 400) {
          toast.error(detail || "No documents or case summary available for analysis. Please upload documents first.");
        } else {
          toast.error("Failed to start ground analysis. This may be a temporary server issue — please try again in a moment.");
        }
      }
      setAutoIdentifying(false);
    }
  };

  const handleRefreshLegalRefs = async () => {
    setRefreshingLegalRefs(true);
    try {
      const res = await axios.post(`${API}/cases/${caseId}/grounds/refresh-legal-refs`, {}, {
        headers: { Authorization: `Bearer ${user?.session_token}` },
        withCredentials: true,
        timeout: 180000,
      });
      toast.success(res.data?.message || "Legal references refreshed.");
      // Reload grounds
      const groundsRes = await axios.get(`${API}/cases/${caseId}/grounds`, {
        headers: { Authorization: `Bearer ${user?.session_token}` },
        withCredentials: true,
      });
      if (groundsRes.data?.grounds) {
        setGrounds(groundsRes.data.grounds);
      }
    } catch (error) {
      console.error("Refresh legal refs error:", error);
      toast.error(error?.response?.data?.detail || "Failed to refresh legal references.");
    } finally {
      setRefreshingLegalRefs(false);
    }
  };


  const formatDate = (dateStr) => {
    if (!dateStr) return "N/A";
    return new Date(dateStr).toLocaleDateString("en-AU", {
      day: "numeric",
      month: "short",
      year: "numeric"
    });
  };

  /* DO NOT UNDO — AI Progress Analysis generation */
  const handleGenerateProgressAnalysis = async () => {
    setGeneratingProgress(true);
    toast.info("Generating progress analysis — this can take several minutes.");
    try {
      const response = await axios.post(`${API}/cases/${caseId}/progress-analysis`, {}, {
        timeout: 600000
      });
      setProgressAnalysis(response.data);
      toast.success("Progress analysis generated");
    } catch (error) {
      console.error("Progress analysis error:", error);
      if (error.code === 'ECONNABORTED' || error.message?.includes('timeout')) {
        toast.error("Progress analysis timed out. Please retry — larger cases can take longer.");
      } else {
        toast.error(error?.response?.data?.detail || "Failed to generate progress analysis. Please try again.");
      }
    } finally {
      setGeneratingProgress(false);
    }
  };

  const formatDateTime = (dateStr) => {
    if (!dateStr) return "N/A";
    return new Date(dateStr).toLocaleDateString("en-AU", {
      day: "numeric",
      month: "short",
      year: "numeric",
      hour: "2-digit",
      minute: "2-digit"
    });
  };

  const handleDeleteCase = () => {
    setShowDeleteCaseDialog(true);
  };
  
  const confirmDeleteCase = async () => {
    setShowDeleteCaseDialog(false);
    try {
      await axios.delete(`${API}/cases/${caseId}`);
      toast.success("Case deleted successfully");
      navigate("/dashboard");
    } catch (error) {
      toast.error("Failed to delete case");
    }
  };

  // ── Shared HTML helpers for exports ──
  const escHtml = (text) => {
    if (!text) return '';
    return text.replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;');
  };
  const mdToHtml = (text) => {
    if (!text) return '';
    let html = escHtml(text);
    html = html.replace(/^####\s+(.+)$/gm, '<h4 style="font-family:\'Times New Roman\',Times,serif;font-size:14pt;font-weight:700;color:#1e293b;margin:14px 0 6px;">$1</h4>');
    html = html.replace(/^###\s+(.+)$/gm, '<h4 style="font-family:\'Times New Roman\',Times,serif;font-size:14pt;font-weight:700;color:#1e293b;margin:14px 0 6px;">$1</h4>');
    html = html.replace(/^##\s+(.+)$/gm, '<h3 style="font-family:\'Times New Roman\',Times,serif;font-size:14pt;font-weight:700;color:#1e293b;margin:18px 0 8px;">$1</h3>');
    html = html.replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>');
    html = html.replace(/\n\n/g, '</p><p style="margin-bottom:10px;">');
    html = html.replace(/\n/g, '<br/>');
    return auSpelling('<p style="margin-bottom:10px;">' + html + '</p>');
  };

  const buildProgressHtml = () => {
    const defendant = caseData?.defendant_name || "Unknown";
    const title = caseData?.title || "Case";

    // ── TOC ──
    const tocItems = [];
    if (caseData?.summary) tocItems.push("Case Summary");
    tocItems.push("Case Readiness Score");
    tocItems.push("Grounds Review Progress");
    tocItems.push("Documentation Completeness");
    if (progressAnalysis) tocItems.push("AI Progress Analysis");
    tocItems.push("Appeal Checklist");

    let body = `<div class="export-header" style="background:#2563eb;"><h1>Case Progress</h1><p>${escHtml(title)} - ${escHtml(defendant)}</p></div>`;

    // TOC
    body += `<div class="toc-container" style="padding:10px 24px;">
      <p class="toc-heading" style="font-size:9pt;text-transform:uppercase;letter-spacing:0.05em;color:#334155;font-weight:700;margin:0 0 4px;font-family:'Times New Roman',Times,serif;">CONTENTS (${tocItems.length} SECTIONS)</p>
      <div class="toc-grid" style="display:grid;grid-template-columns:1fr 1fr;gap:2px 16px;">
        ${tocItems.map((s, i) => `<div class="toc-item" style="font-size:8pt;color:#334155;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;padding:1px 0;font-weight:500;font-family:'Times New Roman',Times,serif;"><strong>${i + 1}.</strong> ${s}</div>`).join('')}
      </div>
    </div>`;

    let psn = 0;
    body += `<div class="sections">`;

    if (caseData?.summary) {
      psn++;
      body += `<div class="section"><div class="section-header"><span class="section-number">${psn}</span><span class="section-title">Case Summary</span></div><div class="section-body">${mdToHtml(caseData.summary)}</div></div>`;
    }

    const strengthEl = document.querySelector('[data-testid="case-strength-meter"]');
    if (strengthEl) {
      psn++;
      body += `<div class="section"><div class="section-header"><span class="section-number">${psn}</span><span class="section-title">Case Readiness Score</span></div><div class="section-body">${strengthEl.innerHTML}</div></div>`;
    }

    const pipelineSummaryEl = document.querySelector('[data-testid="case-pipeline-summary"]');
    if (pipelineSummaryEl) {
      psn++;
      body += `<div class="section"><div class="section-header"><span class="section-number">${psn}</span><span class="section-title">Pipeline Summary</span></div><div class="section-body">${pipelineSummaryEl.innerHTML}</div></div>`;
    }

    if (progressAnalysis) {
      psn++;
      const analysisText = progressAnalysis.analysis || progressAnalysis.content || "";
      body += `<div class="section"><div class="section-header"><span class="section-number">${psn}</span><span class="section-title">AI Progress Analysis</span></div><div class="section-body">${mdToHtml(analysisText)}</div></div>`;
    }

    const checklistEl = document.querySelector('[data-testid="appeal-checklist"]');
    if (checklistEl) {
      psn++;
      body += `<div class="section"><div class="section-header"><span class="section-number">${psn}</span><span class="section-title">Appeal Checklist</span></div><div class="section-body">${checklistEl.innerHTML}</div></div>`;
    }

    body += `</div>`;
    return buildExportHtml({ title: "Case Progress", sectionTitle: "Progress", defendantName: defendant, accentColor: "#2563eb", bodyHtml: body });
  };

  const buildPrintAllHtml = (opts = null) => {
    // opts is an ExportOptionsModal selection: { cover, toc, summary, documents,
    // timeline, grounds, notes, progress }. If null → include everything (legacy).
    const o = opts || { cover: true, toc: true, summary: true, documents: true, timeline: true, grounds: true, notes: true, progress: true };
    const defendant = caseData?.defendant_name || "Unknown";
    const title = caseData?.title || "Case";
    const offence = (caseData?.offence_type || caseData?.offence_category?.replace(/_/g, ' ') || "N/A");
    const offenceCapitalised = offence.charAt(0).toUpperCase() + offence.slice(1);

    // Helper: convert markdown headings + bold to HTML and apply AU spelling
    const mdToHtml = (text) => {
      if (!text) return '';
      let html = text.replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;');
      // Convert markdown headings
      html = html.replace(/^####\s+(.+)$/gm, '<h4 style="font-family:\'Times New Roman\',Times,serif;font-size:11pt;font-weight:700;color:#1e293b;margin:8px 0 4px;">$1</h4>');
      html = html.replace(/^###\s+(.+)$/gm, '<h4 style="font-family:\'Times New Roman\',Times,serif;font-size:11pt;font-weight:700;color:#1e293b;margin:8px 0 4px;">$1</h4>');
      html = html.replace(/^##\s+(.+)$/gm, '<h3 style="font-family:\'Times New Roman\',Times,serif;font-size:13pt;font-weight:700;color:#1e293b;margin:10px 0 5px;">$1</h3>');
      // Bold
      html = html.replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>');
      // Double newlines → paragraph breaks
      html = html.replace(/\n\n/g, '</p><p style="margin-bottom:5px;">');
      // Single newlines → <br>
      html = html.replace(/\n/g, '<br/>');
      return auSpelling('<p style="margin-bottom:5px;">' + html + '</p>');
    };

    // Escape HTML and apply AU spelling
    const escAu = (text) => {
      if (!text) return '';
      return auSpelling(text.replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;'));
    };

    let body = "";
    if (o.cover) {
      body += `<div class="export-header"><h1>Complete Case Bundle</h1><p>${escAu(title)} - ${escAu(defendant)}</p></div>`;
      body += `<div style="margin:10px 24px;padding:10px;border:2px solid #1d4ed8;border-radius:8px;background:#eff6ff;-webkit-print-color-adjust:exact;print-color-adjust:exact;font-family:'Times New Roman',Times,serif;">
      <div style="display:grid;grid-template-columns:1fr 1fr;gap:6px;">
        <div><span style="font-size:8pt;font-weight:800;text-transform:uppercase;letter-spacing:0.1em;color:#2563eb;">Defendant</span><br/><strong style="font-size:10pt;color:#0f172a;">${escAu(defendant)}</strong></div>
        <div><span style="font-size:8pt;font-weight:800;text-transform:uppercase;letter-spacing:0.1em;color:#2563eb;">Offence</span><br/><strong style="font-size:10pt;color:#0f172a;text-transform:capitalize;">${escAu(offenceCapitalised)}</strong></div>
        <div><span style="font-size:8pt;font-weight:800;text-transform:uppercase;letter-spacing:0.1em;color:#2563eb;">Sentence</span><br/><strong style="font-size:10pt;color:#0f172a;">${escAu(caseData?.sentence || "N/A")}</strong></div>
        <div><span style="font-size:8pt;font-weight:800;text-transform:uppercase;letter-spacing:0.1em;color:#2563eb;">Documents</span><br/><strong style="font-size:10pt;color:#0f172a;">${documents.length} files analysed</strong></div>
        <div><span style="font-size:8pt;font-weight:800;text-transform:uppercase;letter-spacing:0.1em;color:#2563eb;">Timeline Events</span><br/><strong style="font-size:10pt;color:#0f172a;">${timeline.length} events</strong></div>
      </div>
      ${caseData?.court ? `<div style="margin-top:6px;padding-top:6px;border-top:1px solid #bfdbfe;font-size:10pt;color:#1d4ed8;font-weight:600;">${escAu(caseData.court)}${caseData?.case_number ? ' — ' + escAu(caseData.case_number) : ''} — ${(caseData?.state || "NSW").toUpperCase()}</div>` : ''}
    </div>`;
    }

    // ── TABLE OF CONTENTS ──
    const tocSections = [];
    if (o.summary && caseData?.summary) tocSections.push("Case Summary");
    if (o.documents && documents.length > 0) tocSections.push("Uploaded Documents");
    if (o.timeline) tocSections.push("Timeline Events");
    if (o.grounds) tocSections.push("Grounds of Merit");
    if (o.notes) tocSections.push("Notes");
    if (o.progress && progressAnalysis) tocSections.push("Progress Analysis");

    if (o.toc && tocSections.length > 0) {
      body += `<div class="export-body" style="page-break-after:always;">
      <div class="toc-container" style="padding:10px 24px;">
        <p class="toc-heading" style="font-size:9pt;text-transform:uppercase;letter-spacing:0.05em;color:#334155;font-weight:700;margin:0 0 4px;font-family:'Times New Roman',Times,serif;">CONTENTS (${tocSections.length} SECTIONS)</p>
        <div class="toc-grid" style="display:grid;grid-template-columns:1fr 1fr;gap:2px 16px;">
          ${tocSections.map((s, i) => `<div class="toc-item" style="font-size:8pt;color:#334155;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;padding:1px 0;font-weight:500;font-family:'Times New Roman',Times,serif;"><strong>${i + 1}.</strong> ${s}</div>`).join('')}
        </div>
      </div>
    </div>`;
    }

    let sn = 0;
    body += `<div class="sections">`;
    if (o.summary && caseData?.summary) { sn++; body += `<div class="section"><div class="section-header"><span class="section-number">${sn}</span><span class="section-title">Case Summary</span></div><div class="section-body"><p>${escAu(caseData.summary)}</p></div></div>`; }
    if (o.documents && documents.length > 0) {
      sn++;
      body += `<div class="section" style="page-break-before:always;"><div class="section-header"><span class="section-number">${sn}</span><span class="section-title">Uploaded Documents</span></div><div class="section-body">`;
      body += `<table><thead><tr><th>#</th><th>Filename</th><th>Type</th><th>Uploaded</th></tr></thead><tbody>`;
      documents.forEach((d, i) => {
        const date = d.created_at ? new Date(d.created_at).toLocaleDateString("en-AU") : "";
        body += `<tr><td>${i + 1}</td><td>${escAu(d.filename || d.name || "Document")}</td><td>${escAu(d.doc_type || d.type || "—")}</td><td>${date}</td></tr>`;
      });
      body += `</tbody></table></div></div>`;
    }
    if (o.timeline) {
      sn++;
      body += `<div class="section" style="page-break-before:always;"><div class="section-header"><span class="section-number">${sn}</span><span class="section-title">Timeline Events</span></div><div class="section-body">`;
      if (timeline.length > 0) {
        body += `<table><thead><tr><th>Date</th><th>Event</th><th>Description</th></tr></thead><tbody>`;
        timeline.forEach(e => {
          body += `<tr><td>${e.event_date || ""}</td><td>${escAu(e.title || "")}</td><td>${escAu(e.description || "")}</td></tr>`;
        });
        body += `</tbody></table>`;
      } else { body += `<p>No timeline events.</p>`; }
      body += `</div></div>`;
    }
    if (o.grounds) {
    sn++;
    body += `<div class="section" style="page-break-before:always;"><div class="section-header"><span class="section-number">${sn}</span><span class="section-title">Grounds of Merit</span></div><div class="section-body">`;
    if (grounds.length > 0) {
      grounds.forEach((g, i) => {
        body += `<div class="section-block"><h3>Ground ${i + 1}: ${escAu(g.title || "")}</h3>`;
        body += `<p>${escAu(g.description || "")}</p>`;
        body += `<p><strong>Strength:</strong> ${escAu((g.strength || "N/A").charAt(0).toUpperCase() + (g.strength || "N/A").slice(1))} &nbsp; <strong>Type:</strong> ${escAu((g.ground_type || "N/A").replace(/_/g, ' ').replace(/\b\w/g, c => c.toUpperCase()))}</p>`;
        // Supporting evidence — filter garbage strings
        const evidence = Array.isArray(g.supporting_evidence) ? g.supporting_evidence : [];
        if (evidence.length > 0) {
          const cleanEvidence = evidence.map(item => {
            if (typeof item === "string") {
              if (item.includes('document_id') && item.includes('filename') && item.includes('quote')) return '';
              if (/^[a-z_]+$/.test(item) && item.length < 80) return '';
              if (item.startsWith("{") && item.includes("'optional'")) return '';
              const m = item.match(/['"]quote['"]\s*:\s*['"](.+?)['"]\s*[,}]/);
              return m ? m[1] : item;
            } else {
              return item?.quote || item?.text || '';
            }
          }).filter(Boolean);
          if (cleanEvidence.length > 0) {
            body += `<h4 style="margin:12px 0 6px;font-size:14pt;color:#1e293b;font-family:'Times New Roman',Times,serif;font-weight:700;">Supporting Evidence</h4><ul>`;
            cleanEvidence.forEach(text => {
              body += `<li>${escAu(text)}</li>`;
            });
            body += `</ul>`;
          }
        }
        // Law sections — handle both objects and raw strings/JSON
        const laws = Array.isArray(g.law_sections) ? g.law_sections : [];
        if (laws.length > 0) {
          body += `<h4 style="margin:12px 0 6px;font-size:14pt;color:#1e293b;font-family:'Times New Roman',Times,serif;font-weight:700;">Relevant Legislation</h4><ul>`;
          laws.forEach(s => {
            const esc = (v) => String(v||'').replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;');
            if (typeof s === "string") {
              try { const parsed = JSON.parse(s); body += `<li>s ${esc(parsed.section)} ${esc(parsed.act || parsed.title)} (${esc((parsed.jurisdiction || "NSW").toUpperCase())})</li>`; }
              catch { body += `<li>${escAu(s)}</li>`; }
            } else if (typeof s === "object" && s) {
              body += `<li>s ${esc(s.section)} ${esc(s.act || s.title)} (${esc((s.jurisdiction || "NSW").toUpperCase())})</li>`;
            }
          });
          body += `</ul>`;
        }
        // Similar cases
        const cases = Array.isArray(g.similar_cases) ? g.similar_cases.filter(c => c.case_name && c.case_name !== "Case name" && !c.case_name.includes("[Surname]") && !c.case_name.includes("[Year]") && c.case_name !== "None" && c.case_name !== "optional") : [];
        if (cases.length > 0) {
          body += `<h4 style="margin:12px 0 6px;font-size:14pt;color:#1e293b;font-family:'Times New Roman',Times,serif;font-weight:700;">Similar Cases (AI-Suggested)</h4><ul>`;
          cases.forEach(c => {
            body += `<li>${escAu(c.case_name || "")}${c.citation ? ` — ${escAu(c.citation)}` : ""}${c.relevance_note ? `: ${escAu(c.relevance_note)}` : ""}</li>`;
          });
          body += `</ul>`;
        }
        // Deep analysis — render markdown headings properly
        const analysis = g.deep_analysis?.full_analysis || g.analysis || "";
        if (analysis) {
          body += `<h4 style="margin:12px 0 6px;font-size:14pt;color:#1e293b;font-family:'Times New Roman',Times,serif;font-weight:700;">Deep Investigation Analysis</h4>`;
          body += `<div style="font-size:12pt;line-height:1.8;font-family:'Times New Roman',Times,serif;">${mdToHtml(analysis)}</div>`;
        }
        body += `</div>`;
      });
    } else { body += `<p>${groundsCount > 0 ? groundsCount + " grounds identified (locked)." : "No grounds identified."}</p>`; }
    body += `</div></div>`;
    }
    if (o.notes) {
    sn++;
    body += `<div class="section" style="page-break-before:always;"><div class="section-header"><span class="section-number">${sn}</span><span class="section-title">Notes</span></div><div class="section-body">`;
    if (notes.length > 0) {
      notes.forEach(n => {
        const date = new Date(n.created_at).toLocaleDateString("en-AU", { day: "numeric", month: "long", year: "numeric" });
        body += `<div class="note-card"><div class="note-title">${escAu(n.title || "Untitled")}</div><div class="note-date">${date}</div><div class="note-content">${escAu(n.content || "")}</div></div>`;
      });
    } else { body += `<p>No notes.</p>`; }
    body += `</div></div>`;
    }
    if (o.progress && progressAnalysis) {
      sn++;
      body += `<div class="section" style="page-break-before:always;"><div class="section-header"><span class="section-number">${sn}</span><span class="section-title">Progress Analysis</span></div><div class="section-body"><div style="font-size:12pt;line-height:1.8;font-family:'Times New Roman',Times,serif;">${mdToHtml(progressAnalysis.analysis || progressAnalysis.content || "")}</div></div></div>`;
    }
    body += `</div>`;
    return buildExportHtml({ title: "Complete Case Bundle", sectionTitle: "Complete Bundle", defendantName: defendant, accentColor: "#0f172a", bodyHtml: body });
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-white">
        <div className="text-center">
          <Loader2 className="w-12 h-12 animate-spin text-slate-600 mx-auto" />
          <p className="mt-4 text-slate-600">Loading case...</p>
        </div>
      </div>
    );
  }

  if (loadError) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-white">
        <div className="text-center max-w-md">
          <AlertCircle className="w-12 h-12 text-red-500 mx-auto" />
          <h2 className="mt-4 text-xl font-semibold text-slate-900">Error Loading Case</h2>
          <p className="mt-2 text-slate-600">{loadError}</p>
          <div className="mt-6 flex gap-3 justify-center">
            <Button 
              onClick={() => navigate("/dashboard")}
              className="rounded-xl bg-blue-700 text-white hover:bg-blue-600"
              data-testid="back-to-dashboard-btn"
            >
              <ArrowLeft className="w-4 h-4 mr-2" />
              Back to Dashboard
            </Button>
            <Button 
              onClick={fetchCaseData}
              className="rounded-xl bg-blue-700 text-white hover:bg-blue-600"
              data-testid="retry-load-btn"
            >
              Try Again
            </Button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="case-page min-h-screen bg-white">
      {/* Header */}
      <header className="glass-header sticky top-0 z-40">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 py-3 sm:py-4">
          <div className="flex items-center gap-2 sm:gap-4">
            <Button 
              variant="ghost" 
              size="sm" 
              onClick={() => navigate("/dashboard")}
              className="rounded-xl shrink-0 text-slate-700 hover:text-slate-900"
              data-testid="back-btn"
            >
              <ArrowLeft className="w-4 h-4 mr-1" />
              <span className="hidden sm:inline">Back</span>
            </Button>
            <div className="flex items-center gap-2 flex-1 min-w-0 overflow-hidden">
              <div className="w-8 h-8 rounded-lg bg-blue-700 flex items-center justify-center shrink-0 z-10">
                <Scale className="w-4 h-4 text-white" />
              </div>
              <span className="text-slate-500 hidden sm:inline">/</span>
              <span className="font-medium text-slate-900 truncate text-sm sm:text-base">{caseData?.title}</span>
            </div>
            <div className="flex items-center gap-1 sm:gap-2 overflow-x-auto" style={{ WebkitOverflowScrolling: 'touch' }}>
              <Button 
                size="sm" 
                onClick={() => navigate("/help")}
                className="bg-blue-700 text-white hover:bg-blue-600 rounded-xl hidden sm:flex"
                data-testid="help-btn"
              >
                <HelpCircle className="w-4 h-4 mr-1" />
                Help
              </Button>
              <span className="hidden sm:inline"><QuickExport caseId={caseId} caseTitle={caseData?.title} /></span>
              <span className="hidden sm:inline"><DocumentBundler caseId={caseId} documents={documents} /></span>
              <Button 
                variant="outline"
                size="sm"
                onClick={() => setShowShareModal(true)}
                className="text-blue-600 hover:text-blue-700 border-blue-200 hover:border-blue-300 rounded-xl"
                data-testid="share-case-btn"
              >
                <Share2 className="w-4 h-4 mr-1" />
                Share
              </Button>
              <Button variant="outline" size="sm" onClick={() => { setExportMode("print"); setExportOpen(true); }} className="bg-blue-700 text-white hover:bg-blue-600 rounded-xl" data-testid="print-all-print-btn">
                <Printer className="w-4 h-4 mr-1" />Print All
              </Button>
              <Button variant="outline" size="sm" onClick={() => { setExportMode("pdf"); setExportOpen(true); }} className="bg-blue-700 text-white hover:bg-blue-600 rounded-xl" data-testid="print-all-pdf-btn">
                <Download className="w-4 h-4 mr-1" />PDF All
              </Button>
              <Button variant="outline" size="sm" onClick={() => { setExportMode("word"); setExportOpen(true); }} className="bg-blue-700 text-white hover:bg-blue-600 rounded-xl" data-testid="print-all-word-btn">
                <FileText className="w-4 h-4 mr-1" />Word All
              </Button>
              <Button 
                variant="destructive" 
                size="sm" 
                onClick={handleDeleteCase}
                className="bg-red-600 hover:bg-red-700 text-white rounded-xl text-base font-extrabold"
                data-testid="delete-case-btn"
              >
                <Trash2 className="w-5 h-5 mr-1" />
                Delete Case
              </Button>
            </div>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 sm:px-6 py-6 sm:py-8">
        {/* Case Info */}
        <div className="mb-8">
          <div className="flex items-start justify-between gap-4">
            <h1 
              className="text-2xl sm:text-3xl md:text-4xl font-extrabold text-slate-900 tracking-tight"
              style={{ fontFamily: "'Times New Roman', Times, serif" }}
              data-testid="case-title"
            >
              {caseData?.title}
            </h1>
            <Button
              size="sm"
              onClick={handleOpenEditCase}
              className="shrink-0 rounded-xl bg-blue-700 text-white hover:bg-blue-600"
              data-testid="edit-case-btn"
            >
              <Pencil className="w-4 h-4 mr-1.5" />
              Edit
            </Button>
          </div>
          {/* DO_NOT_UNDO — Case Identity Card. Must always show defendant, offence, state, sentence prominently with colour. */}
          <div className="mt-4 rounded-xl border-2 border-blue-700 bg-blue-50 p-5 legal-content" data-testid="case-identity-card">
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div>
                <div className="text-[10pt] font-bold uppercase tracking-widest text-blue-600 mb-0.5" style={{ fontFamily: "'Times New Roman', Times, serif" }}>Defendant</div>
                <div className="font-bold text-slate-900" style={{ fontFamily: "'Times New Roman', Times, serif", fontSize: '14pt' }}>{caseData?.defendant_name || "—"}</div>
              </div>
              <div>
                <div className="text-[10pt] font-bold uppercase tracking-widest text-blue-600 mb-0.5" style={{ fontFamily: "'Times New Roman', Times, serif" }}>Offence</div>
                <div className="font-bold text-slate-900 capitalize" style={{ fontFamily: "'Times New Roman', Times, serif", fontSize: '14pt' }}>{caseData?.offence_type || caseData?.offence_category?.replace(/_/g, ' ') || "—"}</div>
              </div>
              <div>
                <div className="text-[10pt] font-bold uppercase tracking-widest text-blue-600 mb-0.5" style={{ fontFamily: "'Times New Roman', Times, serif" }}>State / Jurisdiction</div>
                <div className="font-bold text-slate-900 uppercase" style={{ fontFamily: "'Times New Roman', Times, serif", fontSize: '14pt' }}>{caseData?.state || "—"}</div>
              </div>
              <div>
                <div className="text-[10pt] font-bold uppercase tracking-widest text-blue-600 mb-0.5" style={{ fontFamily: "'Times New Roman', Times, serif" }}>Sentence</div>
                <div className="font-bold text-slate-900 break-words" style={{ fontFamily: "'Times New Roman', Times, serif", fontSize: '14pt' }}>{caseData?.sentence || "—"}</div>
              </div>
            </div>
            {caseData?.court && (
              <div className="mt-2 pt-2 border-t border-blue-200 text-blue-700 font-medium" style={{ fontFamily: "'Times New Roman', Times, serif", fontSize: '11pt' }}>
                {caseData.court}{caseData?.case_number ? ` — ${caseData.case_number}` : ""}
              </div>
            )}
          </div>

          {caseData?.summary && activeTab !== "grounds" && (
            <div className="mt-3">
              <h3 className="font-bold text-slate-500 uppercase tracking-wide mb-1" style={{ fontFamily: "'Times New Roman', Times, serif", fontSize: '10pt' }} data-testid="case-summary-heading">Case Summary</h3>
              <p className="text-slate-600 leading-relaxed max-w-3xl" style={{ fontFamily: "'Times New Roman', Times, serif", fontSize: '12pt', lineHeight: '1.8' }} data-testid="case-summary-text">{caseData.summary}</p>
            </div>
          )}

          {/* Review Status — hidden for clarity, the tabs themselves convey status */}
        </div>

        {/* Jurisdiction & Metadata Warnings */}
        {caseData && (caseData.metadata_warnings?.length > 0 || (caseData.jurisdiction_warnings || []).filter(w => !w.startsWith("APPEAL TIME LIMIT")).length > 0) && (
          <div className="bg-red-600 border-2 border-red-700 rounded-xl p-4 mb-2" data-testid="jurisdiction-warnings">
            <div className="flex items-start gap-3">
              <AlertCircle className="w-5 h-5 text-white shrink-0 mt-0.5" />
              <div className="flex-1 min-w-0">
                <p className="font-bold text-white text-sm mb-2">Case Metadata — Action Required</p>
                <ul className="space-y-1">
                  {(caseData.metadata_warnings || []).map((w, i) => (
                    <li key={`mw-${i}`} className="text-xs text-white font-semibold flex items-start gap-1.5">
                      <span className="text-red-200 mt-0.5 shrink-0">&#x25CF;</span>
                      <span>{w}</span>
                    </li>
                  ))}
                  {(caseData.jurisdiction_warnings || []).filter(w =>
                    !w.startsWith("APPEAL TIME LIMIT")
                  ).map((w, i) => (
                    <li key={`jw-${i}`} className="text-xs text-white font-semibold flex items-start gap-1.5">
                      <span className="text-red-200 mt-0.5 shrink-0">&#x25CF;</span>
                      <span>{w}</span>
                    </li>
                  ))}
                </ul>
                <p className="text-[9px] text-red-100 mt-2">
                  Set these fields under Case Details to ensure accurate, jurisdiction-specific analysis.
                </p>
              </div>
            </div>
          </div>
        )}

        {/* Tabs */}
        <Tabs value={activeTab} onValueChange={(val) => { setActiveTab(val); window.scrollTo(0, 0); }} className="space-y-6">
          <div className="flex flex-col gap-4">
            <p className="text-base font-bold text-blue-700 uppercase tracking-wide text-center" data-testid="case-tabs-heading">Select a tab below to manage your case</p>
            <div className="overflow-x-auto -mx-4 px-4 sm:mx-0 sm:px-0">
              <TabsList className="bg-white border border-slate-200 rounded-xl p-1 inline-flex min-w-max">
                <TabsTrigger value="documents" className="rounded-lg text-xs sm:text-sm px-2 sm:px-3" data-testid="tab-documents">
                  <FileText className="w-3.5 h-3.5 sm:w-4 sm:h-4 mr-1 sm:mr-2" />
                  <span className="hidden sm:inline">Documents</span><span className="sm:hidden">Docs</span> ({documents.length})
                </TabsTrigger>
                <TabsTrigger value="timeline" className="rounded-lg text-xs sm:text-sm px-2 sm:px-3" data-testid="tab-timeline">
                  <Clock className="w-3.5 h-3.5 sm:w-4 sm:h-4 mr-1 sm:mr-2" />
                  Timeline ({timeline.length})
                </TabsTrigger>
                <TabsTrigger value="grounds" className="rounded-lg text-xs sm:text-sm px-2 sm:px-3" data-testid="tab-grounds">
                  <Gavel className="w-3.5 h-3.5 sm:w-4 sm:h-4 mr-1 sm:mr-2" />
                  Grounds ({groundsCount || grounds.length})
                </TabsTrigger>
                <TabsTrigger value="notes" className="rounded-lg text-xs sm:text-sm px-2 sm:px-3" data-testid="tab-notes">
                  <MessageSquare className="w-3.5 h-3.5 sm:w-4 sm:h-4 mr-1 sm:mr-2" />
                  Notes ({notes.length})
                </TabsTrigger>
                <TabsTrigger value="reports" className="rounded-lg text-xs sm:text-sm px-2 sm:px-3" data-testid="tab-reports">
                  <Scale className="w-3.5 h-3.5 sm:w-4 sm:h-4 mr-1 sm:mr-2" />
                  Reports ({reports.length})
                </TabsTrigger>
                <TabsTrigger value="legal" className="rounded-lg text-xs sm:text-sm px-2 sm:px-3" data-testid="tab-legal">
                  <BookOpen className="w-3.5 h-3.5 sm:w-4 sm:h-4 mr-1 sm:mr-2" />
                  Legal
                </TabsTrigger>
                <TabsTrigger value="caselaw" className="rounded-lg text-xs sm:text-sm px-2 sm:px-3" data-testid="tab-caselaw">
                  <Scale className="w-3.5 h-3.5 sm:w-4 sm:h-4 mr-1 sm:mr-2" />
                  <span className="hidden sm:inline">Find Case Law</span><span className="sm:hidden">Law</span>
                </TabsTrigger>
                <TabsTrigger value="progress" className="rounded-lg text-xs sm:text-sm px-2 sm:px-3" data-testid="tab-progress">
                  <TrendingUp className="w-3.5 h-3.5 sm:w-4 sm:h-4 mr-1 sm:mr-2" />
                  Progress
                </TabsTrigger>
                <TabsTrigger value="collaboration" className="rounded-lg text-xs sm:text-sm px-2 sm:px-3" data-testid="tab-collaboration">
                  <Users className="w-3.5 h-3.5 sm:w-4 sm:h-4 mr-1 sm:mr-2" />
                  <span className="hidden sm:inline">Collaboration</span><span className="sm:hidden">Collab</span>
                </TabsTrigger>
              </TabsList>
            </div>

            <div className="flex gap-2 flex-wrap">
              {activeTab === "timeline" && (
                <>
                  <Button 
                    onClick={handleGenerateTimeline}
                    disabled={generatingTimeline}
                    className="bg-blue-700 text-white hover:bg-blue-600"
                    data-testid="generate-timeline-btn"
                  >
                    {generatingTimeline ? (
                      <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                    ) : (
                      <Sparkles className="w-4 h-4 mr-2" />
                    )}
                    AI Generate Timeline
                  </Button>
                  <Button 
                    onClick={() => setShowEventDialog(true)}
                    className="bg-blue-700 text-white hover:bg-blue-600"
                    data-testid="add-event-btn"
                  >
                    <Plus className="w-4 h-4 mr-2" />
                    Add Event
                  </Button>
                </>
              )}
              {activeTab === "grounds" && (
                <>
                  {(groundsUnlocked || !groundsCount) && (
                    <Button 
                      onClick={handleAutoIdentifyGrounds}
                      disabled={autoIdentifying}
                      className="bg-blue-700 text-white hover:bg-blue-600"
                      data-testid="auto-identify-btn"
                    >
                      {autoIdentifying ? (
                        <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                      ) : (
                        <Sparkles className="w-4 h-4 mr-2" />
                      )}
                      AI Identify Grounds
                    </Button>
                  )}
                  {groundsUnlocked && (
                    <Button 
                      onClick={() => {
                        setNewGround({ title: "", description: "", ground_type: "other", strength: "moderate", supporting_evidence: [] });
                        setShowGroundDialog(true);
                      }}
                      className="bg-blue-700 text-white hover:bg-blue-600"
                      data-testid="add-ground-btn"
                    >
                      <Plus className="w-4 h-4 mr-2" />
                      Add Ground
                    </Button>
                  )}
                  {groundsUnlocked && grounds.length > 0 && (
                    <Button 
                      onClick={handleRefreshLegalRefs}
                      disabled={refreshingLegalRefs}
                      variant="outline"
                      className="border-blue-700 text-blue-700 hover:bg-blue-50"
                      data-testid="refresh-legal-refs-btn"
                    >
                      {refreshingLegalRefs ? (
                        <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                      ) : (
                        <RefreshCw className="w-4 h-4 mr-2" />
                      )}
                      Refresh Legal Refs
                    </Button>
                  )}
                </>
              )}
            </div>
          </div>

          {/* Documents Tab */}
          <TabsContent value="documents" className="space-y-4 legal-content" data-tab-content>
            <DocumentsSection
              caseId={caseId}
              documents={documents}
              setDocuments={setDocuments}
              onDocumentsChange={fetchCaseData}
            />
          </TabsContent>

          {/* Timeline Tab */}
          <TabsContent value="timeline" className="space-y-4 legal-content" data-tab-content>
            {generatingTimeline && (
              <div className="border border-purple-200 bg-purple-50 rounded-lg overflow-hidden p-4" data-testid="ai-timeline-progress">
                <div className="flex items-center gap-3 mb-2">
                  <Loader2 className="w-5 h-5 animate-spin text-purple-600 flex-shrink-0" />
                  <p className="text-sm font-semibold text-purple-900">AI Scan in Progress — Generating Timeline</p>
                </div>
                <p className="text-xs text-purple-700 mb-3">Analysing your documents for dates and events. This may take 30-60 seconds.</p>
                <div className="w-full h-2 bg-purple-200 rounded-full overflow-hidden">
                  <div className="h-full w-3/4 bg-purple-600 rounded-full animate-pulse"></div>
                </div>
              </div>
            )}
            {timeline.length === 0 ? (
              <Card className="p-12 text-center card-elevated">
                <Clock className="w-12 h-12 text-slate-600 mx-auto mb-4" />
                <h3 className="text-lg font-semibold text-slate-900 mb-2" style={{ fontFamily: "'Times New Roman', Times, serif" }}>
                  No events yet
                </h3>
                <p className="text-slate-600 mb-4">Build a chronological timeline of case events.</p>
                <Button 
                  onClick={() => setShowEventDialog(true)}
                  className="bg-blue-700 text-white hover:bg-blue-600 rounded-xl"
                >
                  <Plus className="w-4 h-4 mr-2" />
                  Add First Event
                </Button>
              </Card>
            ) : (
              <div className="space-y-4">
                {timelineAnalysis && (
                  <TimelineAnalysis 
                    analysis={timelineAnalysis} 
                    onClose={() => setTimelineAnalysis(null)} 
                  />
                )}
                <Timeline 
                  events={timeline} 
                  documents={documents}
                  grounds={grounds}
                  caseId={caseId}
                  caseInfo={caseData}
                  onDeleteEvent={handleDeleteEvent}
                  onReorderEvent={handleReorderEvent}
                  onExportPDF={handleExportTimelinePDF}
                  onAnalyse={handleAnalyseTimeline}
                  analyzing={analyzingTimeline}
                />
              </div>
            )}
          </TabsContent>

          {/* Grounds of Merit Tab */}
          <TabsContent value="grounds" className="space-y-4 legal-content" data-tab-content>
            {autoIdentifying && (
              <div className="border border-blue-200 bg-blue-50 rounded-lg overflow-hidden p-4" data-testid="ai-grounds-progress">
                <div className="flex items-center gap-3 mb-2">
                  <Loader2 className="w-5 h-5 animate-spin text-blue-700 flex-shrink-0" />
                  <p className="text-sm font-semibold text-slate-900">AI Scan in Progress — Identifying Grounds of Appeal</p>
                </div>
                <p className="text-xs text-slate-700 mb-3">Analysing your case documents for potential appeal grounds. Please allow time for this process.</p>
                <div className="w-full h-2 bg-blue-100 rounded-full overflow-hidden">
                  <div className="h-full w-3/4 bg-blue-600 rounded-full animate-pulse"></div>
                </div>
              </div>
            )}
            {grounds.length === 0 && !groundsCount && !autoIdentifying ? (
              <Card className="p-12 text-center card-elevated">
                <Gavel className="w-12 h-12 text-slate-600 mx-auto mb-4" />
                <h3 className="text-base font-semibold text-slate-900 mb-2" style={{ fontFamily: "'Times New Roman', Times, serif" }}>
                  No grounds of merit identified
                </h3>
                <p className="text-xs text-slate-500 mb-4 max-w-md mx-auto">
                  Use AI to automatically analyse case materials and identify potential grounds for appeal, 
                  or add grounds manually.
                </p>
                <div className="flex gap-3 justify-center">
                  <Button 
                    onClick={handleAutoIdentifyGrounds}
                    disabled={autoIdentifying}
                    className="bg-blue-600 text-white hover:bg-blue-500 rounded-xl"
                  >
                    {autoIdentifying ? (
                      <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                    ) : (
                      <Sparkles className="w-4 h-4 mr-2" />
                    )}
                    AI Identify Grounds
                  </Button>
                  <Button 
                    onClick={() => {
                      setNewGround({ title: "", description: "", ground_type: "other", strength: "moderate", supporting_evidence: [] });
                      setShowGroundDialog(true);
                    }}
                    className="rounded-xl bg-blue-700 text-white hover:bg-blue-600"
                  >
                    <Plus className="w-4 h-4 mr-2" />
                    Add Manually
                  </Button>
                </div>
              </Card>
            ) : (
              <GroundsOfMerit 
                grounds={grounds}
                groundsCount={groundsCount}
                isUnlocked={groundsUnlocked}
                unlockPrice={groundsUnlockPrice}
                caseId={caseId}
                caseData={caseData}
                onInvestigate={handleInvestigateGround}
                onDelete={handleDeleteGround}
                investigating={investigatingGround}
                selectedGround={selectedGround}
                setSelectedGround={setSelectedGround}
                onPaymentSuccess={() => fetchCaseData()}
              />
            )}

            {/* Deb King Statement & Branding Footer */}
            <div className="mt-6 pt-4 border-t border-slate-200 text-center space-y-2" data-testid="grounds-footer">
              <p className="text-xs font-semibold text-slate-600 tracking-wide">
                Created and Designed by Deb King
              </p>
              <div className="flex items-center justify-center gap-2">
                <div className="w-7 h-7 bg-red-600 rounded-md flex items-center justify-center flex-shrink-0">
                  <Scale className="w-4 h-4 text-white" />
                </div>
                <div className="text-left">
                  <p className="font-bold text-slate-900 text-xs leading-tight">Appeal Case Manager</p>
                  <p className="text-[10px] text-slate-500 leading-tight">Founded by Debra King &mdash; Criminal Appeal Research Tool &mdash; Australian Law Only</p>
                </div>
              </div>
            </div>
          </TabsContent>

          {/* Notes Tab */}
          {/* Notes Tab */}
          <TabsContent value="notes" className="space-y-4 legal-content" data-tab-content>
            <NotesSection
              caseId={caseId}
              notes={notes}
              setNotes={setNotes}
              onNotesChange={fetchCaseData}
              defendantName={caseData?.defendant_name || caseData?.title || ""}
            />
          </TabsContent>

          {/* Reports Tab */}
          <TabsContent value="reports" className="space-y-4 legal-content" data-tab-content>
            {/* AiCostBadge removed per owner request — AI spend is tracked in the
                Admin dashboard; cluttering the Reports tab with a cost estimate
                undermines the professional feel when the case view is being
                printed/shared. */}
            <ReportsSection
              caseId={caseId}
              reports={reports}
              setReports={setReports}
              onReportsChange={fetchCaseData}
              documents={documents}
              paymentSummary={paymentSummary}
              navigate={navigate}
              isAdmin={user?.is_admin}
              caseData={caseData}
            />
          </TabsContent>

          {/* Legal Framework Tab — DO NOT UNDO */}
          <TabsContent value="legal" className="space-y-6 legal-content" data-tab-content>
            <LegalFrameworkViewer 
              offenceCategory={caseData?.offence_category}
              offenceType={caseData?.offence_type}
              state={caseData?.state}
              defendantName={caseData?.defendant_name || caseData?.title || ""}
            />
          </TabsContent>

          {/* Case Law Tab — Verified case law database search */}
          <TabsContent value="caselaw" className="space-y-4 legal-content" data-tab-content>
            <Card className="p-4">
              <h3 className="text-base font-bold text-slate-900 mb-1" style={{ fontFamily: "'Times New Roman', Times, serif" }}>
                Find Case Law
              </h3>
              <p className="text-xs text-slate-500 mb-4">
                Search official Australian court databases directly. All results open in the source 
                database and are not AI-generated.
              </p>
              <CaseLawPanel 
                caseId={caseId}
                state={caseData?.state}
              />
            </Card>
          </TabsContent>

          {/* Progress Tab — DO NOT UNDO, DO NOT DELETE */}
          {/* DO NOT UNDO — Progress Tab with AI Analysis */}
          <TabsContent value="progress" className="space-y-6 legal-content" data-tab-content>
            {/* Export Buttons */}
            <div className="flex items-center gap-2 flex-wrap" data-testid="progress-export-bar">
              <Button variant="outline" size="sm" onClick={() => {
                const html = buildProgressHtml();
                localStorage.setItem("document-preview-payload", JSON.stringify({ html, title: "Progress Export", mode: "print", returnTo: `/cases/${caseId}`, createdAt: Date.now() }));
                window.location.assign(`${window.location.origin}/document-preview?mode=print`);
              }} className="text-slate-700" data-testid="progress-print-btn"><Printer className="w-4 h-4 mr-1" />Print</Button>
              <Button variant="outline" size="sm" onClick={() => {
                const html = buildProgressHtml();
                localStorage.setItem("document-preview-payload", JSON.stringify({ html, title: "Progress Export", mode: "pdf", returnTo: `/cases/${caseId}`, createdAt: Date.now() }));
                window.location.assign(`${window.location.origin}/document-preview?mode=pdf`);
              }} className="text-slate-700" data-testid="progress-pdf-btn"><Download className="w-4 h-4 mr-1" />PDF</Button>
              <Button variant="outline" size="sm" onClick={() => {
                try {
                  toast.info("Opening Word preview...");
                  const html = buildProgressHtml();
                  localStorage.setItem("document-preview-payload", JSON.stringify({ html, mode: "word", title: "Progress — Word View", returnTo: `/cases/${caseId}`, createdAt: Date.now() }));
                  window.location.assign(`${window.location.origin}/document-preview?mode=word`);
                } catch { toast.error("Failed to export Word"); }
              }} className="text-slate-700" data-testid="progress-word-btn"><FileText className="w-4 h-4 mr-1" />Word</Button>
            </div>

            {/* Pipeline Staleness Check */}
            <PipelineStalenessAlert caseId={caseId} />

            {/* Analysis Pipeline */}
            <PipelineProgress
              caseId={caseId}
              sessionToken={localStorage.getItem("session_token")}
              onRunStage={(stage) => {
                if (stage === "project") fetchCaseData();
              }}
            />

            {/* Appeal Preparation Readiness + Pipeline Summary */}
            <div className="grid grid-cols-1 xl:grid-cols-2 gap-4 mb-4">
              <CaseStrengthMeter caseId={caseId} />
              <CasePipelineSummary caseId={caseId} />
            </div>

            {/* AI Progress Analysis Button */}
            <Card>
              <CardContent className="p-4">
                <div className="flex items-center justify-between flex-wrap gap-3">
                  <div>
                    <h3 className="font-semibold text-base">AI Case Progress Analysis</h3>
                    <p className="text-xs text-slate-600">Get an AI-powered assessment of your appeal progress, next steps, and strategic recommendations</p>
                  </div>
                  <Button 
                    onClick={handleGenerateProgressAnalysis} 
                    disabled={generatingProgress}
                    className="bg-blue-600 hover:bg-blue-700 text-white"
                    data-testid="ai-generate-progress-btn"
                  >
                    {generatingProgress ? (
                      <>
                        <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                        Analysing...
                      </>
                    ) : (
                      <>
                        <Sparkles className="w-4 h-4 mr-2" />
                        AI Analyse Progress
                      </>
                    )}
                  </Button>
                </div>
              </CardContent>
            </Card>

            {/* AI Scan in Progress indicator */}
            {generatingProgress && (
              <div className="border border-purple-200 bg-purple-50 rounded-lg overflow-hidden p-4" data-testid="ai-progress-generating">
                <div className="flex items-center gap-3 mb-2">
                  <Loader2 className="w-5 h-5 animate-spin text-purple-600 flex-shrink-0" />
                  <p className="text-sm font-semibold text-purple-900">AI Scan in Progress — Analysing Case Progress</p>
                </div>
                <p className="text-xs text-purple-700 mb-3">Reviewing your case data, documents, and appeal status. This may take 30-60 seconds.</p>
                <div className="w-full h-2 bg-purple-200 rounded-full overflow-hidden">
                  <div className="h-full w-3/4 bg-purple-600 rounded-full animate-pulse"></div>
                </div>
              </div>
            )}

            {/* AI Progress Analysis Results */}
            {progressAnalysis && (
              <Card className="border-purple-200">
                <CardContent className="p-4 legal-report prose prose-sm max-w-none">
                  <ReactMarkdown 
                    remarkPlugins={[remarkGfm]}
                    components={{
                      a: ({ href, children }) => (
                        <a href={href} target="_blank" rel="noopener noreferrer" className="text-blue-600 underline hover:text-blue-800">{children}</a>
                      ),
                      table: ({ children }) => (
                        <div className="overflow-x-auto my-4"><table className="w-full min-w-[560px] border-collapse border border-slate-300 table-auto">{children}</table></div>
                      ),
                      th: ({ children }) => (
                        <th className="border border-slate-300 bg-blue-700 px-3 py-2 text-left text-sm font-extrabold text-white whitespace-normal break-normal">{children}</th>
                      ),
                      td: ({ children }) => (
                        <td className="border border-slate-300 px-3 py-2 text-sm">{children}</td>
                      ),
                    }}
                  >{progressAnalysis.analysis || progressAnalysis.content || ""}</ReactMarkdown>
                </CardContent>
              </Card>
            )}

            {/* Deadline Tracker — collapsed by default */}
            <details className="border border-slate-200 rounded-lg bg-white">
              <summary className="px-4 py-3 cursor-pointer text-sm font-semibold text-slate-700 hover:bg-slate-50">
                Deadline Tracker
              </summary>
              <div className="border-t border-slate-200">
                <DeadlineTracker caseId={caseId} />
              </div>
            </details>
            
            {/* Appeal Checklist — collapsed by default */}
            <details className="border border-slate-200 rounded-lg bg-white">
              <summary className="px-4 py-3 cursor-pointer text-sm font-semibold text-slate-700 hover:bg-slate-50">
                Appeal Checklist
              </summary>
              <div className="border-t border-slate-200">
                <AppealChecklist caseId={caseId} />
              </div>
            </details>
            
            {/* Quick Links */}
            <Card>
              <CardContent className="p-4">
                <div className="flex flex-wrap gap-3">
                  <Button 
                    onClick={() => navigate('/resources')}
                    className="flex items-center gap-2 bg-blue-700 text-white hover:bg-blue-600"
                  >
                    <HelpCircle className="w-4 h-4" />
                    Resource Directory
                  </Button>
                  <Button 
                    onClick={() => navigate('/help')}
                    className="flex items-center gap-2 bg-blue-700 text-white hover:bg-blue-600"
                  >
                    <HelpCircle className="w-4 h-4" />
                    Help & Glossary
                  </Button>
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="collaboration" className="space-y-6 legal-content" data-tab-content>
            <ActivityFeed caseId={caseId} />
          </TabsContent>
        </Tabs>
      </main>

      {/* Chat Panel (floating) */}
      <CaseChat caseId={caseId} user={user} />

      {/* Share Modal */}
      <ShareCaseModal
        caseId={caseId}
        caseName={caseData?.title}
        open={showShareModal}
        onClose={() => setShowShareModal(false)}
      />

      {/* Add Event Dialog */}
      <Dialog open={showEventDialog} onOpenChange={setShowEventDialog}>
        <DialogContent className="max-w-2xl max-h-[90vh] overflow-y-auto">
          <DialogHeader>
            <DialogTitle style={{ fontFamily: "'Times New Roman', Times, serif" }} className="text-2xl">
              Add Timeline Event
            </DialogTitle>
          </DialogHeader>
          <div className="space-y-4 py-4">
            {/* Basic Info */}
            <div>
              <Label>Event Title *</Label>
              <Input
                value={newEvent.title}
                onChange={(e) => setNewEvent({ ...newEvent, title: e.target.value })}
                placeholder="e.g., Police interview with accused"
                data-testid="event-title"
              />
            </div>
            
            <div className="grid grid-cols-2 gap-4">
              <div>
                <Label>Date *</Label>
                <Input
                  type="date"
                  value={newEvent.event_date}
                  onChange={(e) => setNewEvent({ ...newEvent, event_date: e.target.value })}
                  data-testid="event-date"
                />
              </div>
              <div>
                <Label>Category</Label>
                <Select 
                  value={newEvent.event_category} 
                  onValueChange={(v) => {
                    setNewEvent({ ...newEvent, event_category: v });
                  }}
                >
                  <SelectTrigger data-testid="event-category-select">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    {EVENT_CATEGORIES.map(cat => (
                      <SelectItem key={cat.value} value={cat.value}>{cat.label}</SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div>
                <Label>Event Type</Label>
                <Select 
                  value={newEvent.event_type} 
                  onValueChange={(v) => {
                    const eventType = EVENT_TYPES.find(t => t.value === v);
                    setNewEvent({ 
                      ...newEvent, 
                      event_type: v,
                      event_category: eventType?.category || newEvent.event_category
                    });
                  }}
                >
                  <SelectTrigger data-testid="event-type-select">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    {EVENT_TYPES.map(type => (
                      <SelectItem key={type.value} value={type.value}>{type.label}</SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
              <div>
                <Label>Significance</Label>
                <Select 
                  value={newEvent.significance} 
                  onValueChange={(v) => setNewEvent({ ...newEvent, significance: v })}
                >
                  <SelectTrigger data-testid="event-significance-select">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    {SIGNIFICANCE_LEVELS.map(level => (
                      <SelectItem key={level.value} value={level.value}>{level.label}</SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
            </div>

            <div>
              <Label>Description</Label>
              <Textarea
                value={newEvent.description}
                onChange={(e) => setNewEvent({ ...newEvent, description: e.target.value })}
                placeholder="Detailed description of this event..."
                rows={3}
                data-testid="event-description"
              />
            </div>

            {/* Source & Perspective */}
            <div className="grid grid-cols-2 gap-4">
              <div>
                <Label>Source Citation</Label>
                <Input
                  value={newEvent.source_citation}
                  onChange={(e) => setNewEvent({ ...newEvent, source_citation: e.target.value })}
                  placeholder="e.g., Exhibit A, page 23"
                  data-testid="event-source"
                />
              </div>
              <div>
                <Label>Perspective</Label>
                <Select 
                  value={newEvent.perspective} 
                  onValueChange={(v) => setNewEvent({ ...newEvent, perspective: v })}
                >
                  <SelectTrigger data-testid="event-perspective-select">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    {PERSPECTIVES.map(p => (
                      <SelectItem key={p.value} value={p.value}>{p.label}</SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
            </div>

            {/* Link Documents */}
            {documents.length > 0 && (
              <div>
                <Label>Link to Documents</Label>
                <div className="flex flex-wrap gap-2 mt-2 p-3 bg-slate-50 rounded-lg max-h-32 overflow-y-auto">
                  {documents.map(doc => (
                    <label 
                      key={doc.document_id}
                      className={`flex items-center gap-2 px-3 py-1.5 rounded-full text-sm cursor-pointer transition-colors ${
                        newEvent.linked_documents.includes(doc.document_id)
                          ? 'bg-blue-100 text-blue-800 border border-blue-300'
                          : 'bg-white text-slate-600 border border-slate-200 hover:border-blue-300'
                      }`}
                    >
                      <input
                        type="checkbox"
                        className="hidden"
                        checked={newEvent.linked_documents.includes(doc.document_id)}
                        onChange={(e) => {
                          if (e.target.checked) {
                            setNewEvent({ 
                              ...newEvent, 
                              linked_documents: [...newEvent.linked_documents, doc.document_id] 
                            });
                          } else {
                            setNewEvent({ 
                              ...newEvent, 
                              linked_documents: newEvent.linked_documents.filter(id => id !== doc.document_id) 
                            });
                          }
                        }}
                      />
                      <FileText className="w-3 h-3" />
                      {doc.filename.length > 25 ? doc.filename.substring(0, 25) + '...' : doc.filename}
                    </label>
                  ))}
                </div>
              </div>
            )}

            {/* Link Grounds */}
            {grounds.length > 0 && (
              <div>
                <Label>Link to Grounds of Appeal</Label>
                <div className="flex flex-wrap gap-2 mt-2 p-3 bg-slate-50 rounded-lg max-h-32 overflow-y-auto">
                  {grounds.map(ground => (
                    <label 
                      key={ground.ground_id}
                      className={`flex items-center gap-2 px-3 py-1.5 rounded-full text-sm cursor-pointer transition-colors ${
                        newEvent.related_grounds.includes(ground.ground_id)
                          ? 'bg-purple-100 text-purple-800 border border-purple-300'
                          : 'bg-white text-slate-600 border border-slate-200 hover:border-purple-300'
                      }`}
                    >
                      <input
                        type="checkbox"
                        className="hidden"
                        checked={newEvent.related_grounds.includes(ground.ground_id)}
                        onChange={(e) => {
                          if (e.target.checked) {
                            setNewEvent({ 
                              ...newEvent, 
                              related_grounds: [...newEvent.related_grounds, ground.ground_id] 
                            });
                          } else {
                            setNewEvent({ 
                              ...newEvent, 
                              related_grounds: newEvent.related_grounds.filter(id => id !== ground.ground_id) 
                            });
                          }
                        }}
                      />
                      <Scale className="w-3 h-3" />
                      {ground.title.length > 30 ? ground.title.substring(0, 30) + '...' : ground.title}
                    </label>
                  ))}
                </div>
              </div>
            )}

            {/* Contested Fact */}
            <div className="border border-blue-200 rounded-lg p-4 bg-blue-50/50">
              <label className="flex items-center gap-2 cursor-pointer">
                <input
                  type="checkbox"
                  checked={newEvent.is_contested}
                  onChange={(e) => setNewEvent({ ...newEvent, is_contested: e.target.checked })}
                  className="w-4 h-4 rounded border-blue-300"
                />
                <span className="font-medium text-blue-800">This is a contested fact</span>
              </label>
              {newEvent.is_contested && (
                <div className="mt-3">
                  <Label className="text-blue-700">What is contested?</Label>
                  <Textarea
                    value={newEvent.contested_details}
                    onChange={(e) => setNewEvent({ ...newEvent, contested_details: e.target.value })}
                    placeholder="Explain what is disputed about this event..."
                    rows={2}
                    className="mt-1"
                  />
                </div>
              )}
            </div>

            {/* Inconsistency Notes */}
            <div>
              <Label>Inconsistency Notes (optional)</Label>
              <Textarea
                value={newEvent.inconsistency_notes}
                onChange={(e) => setNewEvent({ ...newEvent, inconsistency_notes: e.target.value })}
                placeholder="Note any inconsistencies with other evidence or testimony..."
                rows={2}
              />
            </div>
          </div>
          <DialogFooter>
            <Button onClick={() => setShowEventDialog(false)} className="bg-blue-700 text-white hover:bg-blue-600">
              Cancel
            </Button>
            <Button 
              onClick={handleCreateEvent}
              className="bg-blue-700 text-white hover:bg-blue-600"
              data-testid="event-submit"
            >
              <Plus className="w-4 h-4 mr-2" />
              Add Event
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* Add Ground of Merit Dialog */}
      <Dialog open={showGroundDialog} onOpenChange={setShowGroundDialog}>
        <DialogContent className="max-w-lg">
          <DialogHeader>
            <DialogTitle style={{ fontFamily: "'Times New Roman', Times, serif" }} className="text-2xl">
              Add Ground of Merit
            </DialogTitle>
          </DialogHeader>
          <div className="space-y-4 py-4">
            <div>
              <Label>Ground Type</Label>
              <Select 
                value={newGround.ground_type} 
                onValueChange={(v) => setNewGround({ ...newGround, ground_type: v })}
              >
                <SelectTrigger data-testid="ground-type-select">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  {GROUND_TYPES.map(type => (
                    <SelectItem key={type.value} value={type.value}>{type.label}</SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
            <div>
              <Label>Title *</Label>
              <Input
                value={newGround.title}
                onChange={(e) => setNewGround({ ...newGround, title: e.target.value })}
                placeholder="e.g., Inadequate Legal Representation at Trial"
                data-testid="ground-title"
              />
            </div>
            <div>
              <Label>Description *</Label>
              <Textarea
                value={newGround.description}
                onChange={(e) => setNewGround({ ...newGround, description: e.target.value })}
                placeholder="Describe the ground of merit in detail..."
                rows={4}
                data-testid="ground-description"
              />
            </div>
            <div>
              <Label>Strength Assessment</Label>
              <Select 
                value={newGround.strength} 
                onValueChange={(v) => setNewGround({ ...newGround, strength: v })}
              >
                <SelectTrigger data-testid="ground-strength-select">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="strong">Strong</SelectItem>
                  <SelectItem value="moderate">Moderate</SelectItem>
                  <SelectItem value="weak">Weak</SelectItem>
                </SelectContent>
              </Select>
            </div>
            <div>
              <Label>Supporting Evidence (comma-separated)</Label>
              <Input
                value={newGround.supporting_evidence.join(", ")}
                onChange={(e) => setNewGround({ 
                  ...newGround, 
                  supporting_evidence: e.target.value.split(",").map(s => s.trim()).filter(Boolean)
                })}
                placeholder="e.g., Trial transcript pg 45, Witness statement from John"
                data-testid="ground-evidence"
              />
            </div>
          </div>
          <DialogFooter>
            <Button onClick={() => setShowGroundDialog(false)} className="bg-blue-700 text-white hover:bg-blue-600">
              Cancel
            </Button>
            <Button 
              onClick={handleCreateGround}
              className="bg-blue-700 text-white hover:bg-blue-600"
              data-testid="ground-submit"
            >
              <Plus className="w-4 h-4 mr-2" />
              Add Ground
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* Payment Modal for Reports */}
      <PaymentModal
        isOpen={showPaymentModal}
        onClose={() => {
          setShowPaymentModal(false);
          setPendingFeatureType(null);
          setPendingFeaturePrice(null);
        }}
        caseId={caseId}
        featureType={pendingFeatureType}
        price={pendingFeaturePrice}
        onPaymentSuccess={() => {
          setShowPaymentModal(false);
          fetchCaseData();
          toast.success("Payment successful! You can now generate the report.");
        }}
      />

      {/* DO NOT UNDO — Delete Case Confirmation Dialog */}
      <AlertDialog open={showDeleteCaseDialog} onOpenChange={setShowDeleteCaseDialog}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>Delete This Case?</AlertDialogTitle>
            <AlertDialogDescription>
              This will permanently delete this case and ALL its documents, reports, timeline events, and notes. This cannot be undone.
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel className="bg-blue-700 text-white hover:bg-blue-600 border-blue-700">Cancel</AlertDialogCancel>
            <AlertDialogAction onClick={confirmDeleteCase} className="bg-red-600 hover:bg-red-700 text-white">
              Yes, Delete Case
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>

      {/* DO NOT UNDO — Delete Event Confirmation Dialog */}
      <AlertDialog open={!!deleteEventId} onOpenChange={() => setDeleteEventId(null)}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>Delete This Event?</AlertDialogTitle>
            <AlertDialogDescription>This timeline event will be permanently removed.</AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel className="bg-blue-700 text-white hover:bg-blue-600 border-blue-700">Cancel</AlertDialogCancel>
            <AlertDialogAction onClick={confirmDeleteEvent} className="bg-red-600 hover:bg-red-700 text-white">
              Delete Event
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>

      {/* DO NOT UNDO — Delete Ground Confirmation Dialog */}
      <AlertDialog open={!!deleteGroundId} onOpenChange={() => setDeleteGroundId(null)}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>Delete This Ground of Merit?</AlertDialogTitle>
            <AlertDialogDescription>This ground will be permanently removed from the case.</AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel className="bg-blue-700 text-white hover:bg-blue-600 border-blue-700">Cancel</AlertDialogCancel>
            <AlertDialogAction onClick={confirmDeleteGround} className="bg-red-600 hover:bg-red-700 text-white">
              Delete Ground
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>

      {/* Edit Case Details Dialog */}
      <Dialog open={showEditCaseDialog} onOpenChange={setShowEditCaseDialog}>
        <DialogContent className="max-w-lg max-h-[90vh] overflow-y-auto" aria-describedby="edit-case-description">
          <DialogHeader>
            <DialogTitle>Edit Case Details</DialogTitle>
          </DialogHeader>
          <p id="edit-case-description" className="sr-only">Edit the details of this case</p>
          {editCaseData && (
            <div className="space-y-4">
              <div>
                <Label htmlFor="edit-title">Case Title</Label>
                <Input id="edit-title" value={editCaseData.title} onChange={(e) => setEditCaseData({ ...editCaseData, title: e.target.value })} className="mt-1.5 rounded-xl" data-testid="edit-case-title" />
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <Label htmlFor="edit-defendant">Defendant</Label>
                  <Input id="edit-defendant" value={editCaseData.defendant_name} onChange={(e) => setEditCaseData({ ...editCaseData, defendant_name: e.target.value })} className="mt-1.5 rounded-xl" data-testid="edit-case-defendant" />
                </div>
                <div>
                  <Label htmlFor="edit-case-number">Case Number</Label>
                  <Input id="edit-case-number" value={editCaseData.case_number} onChange={(e) => setEditCaseData({ ...editCaseData, case_number: e.target.value })} className="mt-1.5 rounded-xl" data-testid="edit-case-number" />
                </div>
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <Label htmlFor="edit-court">Court</Label>
                  <Input id="edit-court" value={editCaseData.court} onChange={(e) => setEditCaseData({ ...editCaseData, court: e.target.value })} className="mt-1.5 rounded-xl" data-testid="edit-case-court" />
                </div>
                <div>
                  <Label htmlFor="edit-judge">Presiding Judge</Label>
                  <Input id="edit-judge" value={editCaseData.judge} onChange={(e) => setEditCaseData({ ...editCaseData, judge: e.target.value })} className="mt-1.5 rounded-xl" data-testid="edit-case-judge" />
                </div>
              </div>
              <div>
                <Label htmlFor="edit-sentence">Sentence</Label>
                <Input id="edit-sentence" value={editCaseData.sentence} onChange={(e) => setEditCaseData({ ...editCaseData, sentence: e.target.value })} placeholder="e.g., 30 years imprisonment with NPP of 22 years 6 months" className="mt-1.5 rounded-xl" data-testid="edit-case-sentence" />
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <Label htmlFor="edit-state">Jurisdiction</Label>
                  <Select value={editCaseData.state} onValueChange={(val) => setEditCaseData({ ...editCaseData, state: val })}>
                    <SelectTrigger className="mt-1.5 rounded-xl" data-testid="edit-case-state"><SelectValue /></SelectTrigger>
                    <SelectContent>
                      {[{v:"nsw",l:"NSW"},{v:"vic",l:"VIC"},{v:"qld",l:"QLD"},{v:"wa",l:"WA"},{v:"sa",l:"SA"},{v:"tas",l:"TAS"},{v:"nt",l:"NT"},{v:"act",l:"ACT"}].map(s => (
                        <SelectItem key={s.v} value={s.v}>{s.l}</SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>
                <div>
                  <Label htmlFor="edit-offence">Offence Category</Label>
                  <Select value={editCaseData.offence_category} onValueChange={(val) => setEditCaseData({ ...editCaseData, offence_category: val })}>
                    <SelectTrigger className="mt-1.5 rounded-xl" data-testid="edit-case-offence"><SelectValue /></SelectTrigger>
                    <SelectContent>
                      {[{v:"homicide",l:"Homicide"},{v:"assault",l:"Assault"},{v:"sexual_offences",l:"Sexual Offences"},{v:"drug_offences",l:"Drug Offences"},{v:"fraud",l:"Fraud"},{v:"robbery",l:"Robbery"},{v:"other",l:"Other"}].map(o => (
                        <SelectItem key={o.v} value={o.v}>{o.l}</SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>
              </div>
              <div>
                <Label htmlFor="edit-offence-type">Specific Offence</Label>
                <Input id="edit-offence-type" value={editCaseData.offence_type} onChange={(e) => setEditCaseData({ ...editCaseData, offence_type: e.target.value })} placeholder="e.g., Murder" className="mt-1.5 rounded-xl" data-testid="edit-case-offence-type" />
              </div>
              <div>
                <Label htmlFor="edit-summary">Summary</Label>
                <Textarea id="edit-summary" value={editCaseData.summary} onChange={(e) => setEditCaseData({ ...editCaseData, summary: e.target.value })} rows={3} className="mt-1.5 rounded-xl" data-testid="edit-case-summary" />
              </div>
            </div>
          )}
          <DialogFooter>
            <Button onClick={() => setShowEditCaseDialog(false)} className="rounded-xl bg-blue-700 text-white hover:bg-blue-600">Cancel</Button>
            <Button onClick={handleSaveCase} disabled={savingCase} className="rounded-xl bg-blue-700 text-white hover:bg-blue-600" data-testid="save-case-btn">
              {savingCase ? <><Loader2 className="w-4 h-4 mr-2 animate-spin" />Saving...</> : "Save Changes"}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* Export Options picker — lets user choose which sections to include */}
      <ExportOptionsModal
        open={exportOpen}
        mode={exportMode}
        availability={{
          cover: true,
          toc: true,
          summary: !!caseData?.summary,
          documents: documents.length > 0,
          timeline: timeline.length > 0,
          grounds: true,
          notes: notes.length > 0,
          progress: !!progressAnalysis,
        }}
        onCancel={() => setExportOpen(false)}
        onConfirm={(chosenOpts) => {
          setExportOpen(false);
          try {
            const html = buildPrintAllHtml(chosenOpts);
            const title = exportMode === "word" ? "Complete Case Bundle — Word View" : "Complete Case Bundle";
            localStorage.setItem("document-preview-payload", JSON.stringify({
              html, title, mode: exportMode, returnTo: `/cases/${caseId}`, createdAt: Date.now(),
            }));
            window.location.assign(`${window.location.origin}/document-preview?mode=${exportMode}`);
          } catch {
            toast.error(`Failed to open ${exportMode} preview`);
          }
        }}
      />
    </div>
  );
};

export default CaseDetail;
