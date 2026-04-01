/* ========================================================================
   DO NOT UNDO - ENTIRE FILE PROTECTED
   All features, functions, styles, and content in this file are approved
   and must be preserved. Do not remove, rename, or refactor any code.
   ======================================================================== */
import { useState, useEffect, useRef } from "react";
import axios from "axios";
import { toast } from "sonner";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import { isIOSDevice } from "../utils/isIOS";
import {
  FileText, Loader2, Clock, ChevronDown, ChevronRight, Trash2, Download, Presentation, Eye, Printer, AlertCircle, Lock, Scale, BookOpen, CheckCircle2, Crown
} from "lucide-react";
import { Button } from "./ui/button";
import { Card } from "./ui/card";
import { Badge } from "./ui/badge";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogDescription,
  DialogFooter,
} from "./ui/dialog";
import {
  Collapsible,
  CollapsibleContent,
  CollapsibleTrigger,
} from "./ui/collapsible";
import { API } from "../App";
import PaymentModal from "./PaymentModal";
import ReportMetadataPanel from "./ReportMetadataPanel";
import VerificationBadge from "./VerificationBadge";
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
} from "./ui/alert-dialog";

async function verifyTopIssues(apiBase, caseId, limit) {
  const response = await axios.post(
    `${apiBase}/cases/${caseId}/issues/verify-batch`,
    { limit },
    { timeout: 300000 }
  );
  return response.data;
}

const DraftSourceBadge = ({ draftSource }) => {
  // Simplified — no need to expose pipeline internals to the user
  return null;
};

const PipelineDraftPanel = ({ report }) => {
  if (!report) return null;

  const metadata = report.metadata || {};
  const refresh = metadata.pipeline_refresh_before_draft || {};

  const hasRefreshData = Object.keys(refresh).length > 0 && refresh.refreshed;
  if (!hasRefreshData) return null;

  return (
    <div className="mt-3 rounded border p-3 text-xs" data-testid="pipeline-draft-panel">
      <div className="font-semibold mb-1">Report Generation Details</div>

      {"refreshed" in refresh ? (
        <>
          <div className="mt-2 font-medium">Pre-draft refresh</div>
          <div>Refreshed before draft: {refresh.refreshed ? "Yes" : "No"}</div>
          <div>Extracted: {refresh.extracted_count ?? 0}</div>
          <div>Classified: {refresh.classified_count ?? 0}</div>
          <div>Synced: {refresh.synced_count ?? 0}</div>

          {refresh.auto_verify_result ? (
            <>
              <div>Auto-verify attempted: {refresh.auto_verify_result.attempted ?? 0}</div>
              <div>Auto-verify verified: {refresh.auto_verify_result.verified ?? 0}</div>
              <div>Auto-verify failed: {refresh.auto_verify_result.failed ?? 0}</div>
            </>
          ) : null}
        </>
      ) : null}
    </div>
  );
};

const REPORT_TYPES = [
  { 
    value: "quick_summary", 
    label: "Quick Summary", 
    description: "Rapid triage brief with key grounds preview and immediate next steps",
    price: 0,
    priceId: null,
    isFree: true,
    color: "emerald",
    icon: "FileText",
    features: ["Case snapshot", "Primary issues", "Grounds preview", "Appeal outlook"]
  },
  { 
    value: "full_detailed", 
    label: "Full Detailed Report", 
    description: "Barrister-grade deep dossier with comparative sentencing, appeal forms, external case links and full options matrix",
    price: 150.00,
    priceId: "full_report",
    isFree: false,
    color: "blue",
    icon: "Scale",
    features: ["Everything in Quick Summary", "Deep ground analysis (500+ words each)", "8+ sentencing comparisons", "Submissions blueprint", "Action plan"]
  },
  { 
    value: "extensive_log", 
    label: "Extensive Log Report", 
    description: "Master litigation brief with expanded precedent modelling, appeal filing steps, external law links and hearing script",
    price: 200.00,
    priceId: "extensive_report",
    isFree: false,
    color: "purple",
    icon: "BookOpen",
    features: ["Everything in Full Detailed", "900+ words per ground", "15+ precedent cases", "Hearing preparation pack", "Court pathway playbook"]
  }
];

const ReportsSection = ({ 
  caseId, 
  reports, 
  setReports, 
  onReportsChange,
  documents,
  paymentSummary,
  navigate,
  isAdmin
}) => {
  const [showReportDialog, setShowReportDialog] = useState(false);
  const [selectedReportType, setSelectedReportType] = useState(null);
  const [generatingReport, setGeneratingReport] = useState(false);
  const [genElapsed, setGenElapsed] = useState(0);
  const [expandedReports, setExpandedReports] = useState({});
  const [showPaymentModal, setShowPaymentModal] = useState(false);
  const [pendingReportType, setPendingReportType] = useState(null);
  const [pipelineVerifyLoading, setPipelineVerifyLoading] = useState(false);
  const [pipelineVerifyResult, setPipelineVerifyResult] = useState(null);
  const [pipelineVerifyError, setPipelineVerifyError] = useState("");

  const requiredReportTypes = ["quick_summary", "full_detailed", "extensive_log"];
  const latestPaymentStatus = paymentSummary?.latest_status_by_feature || {};
  const unlockedFeatures = paymentSummary?.unlocked_features || {};

  const getReportPaymentFeature = (reportType) => {
    if (reportType === "full_detailed") return "full_report";
    if (reportType === "extensive_log") return "extensive_report";
    return null;
  };

  const getPaymentBadge = (reportType) => {
    const feature = getReportPaymentFeature(reportType);
    if (!feature) return null;
    if (unlockedFeatures[feature]) {
      return { label: "Unlocked", className: "bg-emerald-100 text-emerald-700 border-emerald-200" };
    }
    const status = latestPaymentStatus[feature]?.status;
    if (status === "submitted") {
      return { label: "Awaiting confirmation", className: "bg-amber-100 text-amber-700 border-amber-200" };
    }
    if (status === "pending") {
      return { label: "Pending", className: "bg-blue-100 text-blue-700 border-blue-200" };
    }
    return null;
  };

  const hasAllReports = requiredReportTypes.every((type) =>
    reports.some((report) =>
      report.report_type === type &&
      report.status === "completed" &&
      !report.content?.aggressive_mode
    )
  );

  const handleExportPDF = async (reportId) => {
    try {
      toast.info("Generating PDF...");
      const isIOS = isIOSDevice();
      if (isIOS) {
        const token = localStorage.getItem("session_token");
        const baseUrl = `${API}/cases/${caseId}/reports/${reportId}/export-pdf`;
        const href = token ? `${baseUrl}?session_token=${token}` : baseUrl;
        const a = document.createElement('a');
        a.href = href;
        a.target = '_blank';
        a.rel = 'noopener';
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        toast.success("PDF opening - use Share to save or print.");
        return;
      }
      const response = await axios.get(
        `${API}/cases/${caseId}/reports/${reportId}/export-pdf`,
        { responseType: 'blob' }
      );
      const blob = new Blob([response.data], { type: 'application/pdf' });
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `report_${reportId}.pdf`);
      document.body.appendChild(link);
      link.click();
      link.remove();
      setTimeout(() => window.URL.revokeObjectURL(url), 5000);
      toast.success("PDF ready!");
    } catch (error) {
      console.error("PDF export error:", error);
      toast.error("Failed to export PDF");
    }
  };

  const handleExportDOCX = async (reportId) => {
    try {
      toast.info("Generating Word document...");
      const isIOS = isIOSDevice();
      const response = await axios.get(
        `${API}/cases/${caseId}/reports/${reportId}/export-docx`,
        { responseType: 'blob', timeout: 60000 }
      );
      const blob = new Blob([response.data], { type: 'application/vnd.openxmlformats-officedocument.wordprocessingml.document' });
      const filename = `report_${reportId}.docx`;
      if (isIOS && navigator.share) {
        try {
          const file = new File([blob], filename, { type: blob.type });
          await navigator.share({ files: [file], title: filename });
          toast.success("Shared successfully!");
          return;
        } catch (e) { if (e.name === 'AbortError') return; }
      }
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', filename);
      document.body.appendChild(link);
      link.click();
      link.remove();
      setTimeout(() => window.URL.revokeObjectURL(url), 5000);
      toast.success("Word document ready!");
    } catch (error) {
      console.error("DOCX export error:", error);
      toast.error("Failed to export Word document");
    }
  };

  const handleGenerateReport = async (reportType) => {
    if (documents.length === 0) {
      toast.error("Please upload documents before generating a report");
      return;
    }
    
    // Admin bypasses all payment
    if (isAdmin) {
      generateReport(reportType);
      return;
    }
    
    // Check if this report type is free
    const reportTypeInfo = REPORT_TYPES.find(t => t.value === reportType);
    if (reportTypeInfo?.isFree) {
      // Free report - generate directly without payment
      generateReport(reportType);
      return;
    }
    
    // Check if user has already paid for this report type
    const existingReport = reports.find(r => r.report_type === reportType);
    const featureType = getReportPaymentFeature(reportType);
    const alreadyUnlocked = featureType ? unlockedFeatures[featureType] : false;
    if (existingReport || alreadyUnlocked) {
      // Already generated this type, just regenerate
      generateReport(reportType);
      return;
    }
    
    // Need to pay first for premium reports
    setPendingReportType(reportType);
    setShowPaymentModal(true);
  };

  const pollingRef = useRef(null);
  const elapsedRef = useRef(null);

  // Clean up polling on unmount
  useEffect(() => {
    return () => {
      if (pollingRef.current) clearInterval(pollingRef.current);
      if (elapsedRef.current) clearInterval(elapsedRef.current);
    };
  }, []);

  const generateReport = async (reportType) => {
    setGeneratingReport(true);
    setGenElapsed(0);
    setShowReportDialog(false);
    toast.info("Generating report...");

    // Start elapsed timer
    const startTime = Date.now();
    elapsedRef.current = setInterval(() => {
      setGenElapsed(Math.floor((Date.now() - startTime) / 1000));
    }, 1000);
    
    try {
      const response = await axios.post(
        `${API}/cases/${caseId}/reports/generate`,
        { report_type: reportType },
        { timeout: 120000 }
      );
      
      const reportId = response.data?.report_id;
      const status = response.data?.status;

      if (status === "generating" && reportId) {
        // Poll for completion
        pollForCompletion(reportId);
      } else {
        // Already completed (unlikely with new flow, but handle gracefully)
        toast.success("Report generated successfully");
        if (onReportsChange) onReportsChange();
        setGeneratingReport(false);
      }
    } catch (error) {
      const isTimeout = error?.code === "ECONNABORTED" || error?.message?.toLowerCase().includes("timeout");
      if (isTimeout) {
        toast.info("Report generation started — reconnecting...");
        try {
          const latestRes = await axios.get(`${API}/cases/${caseId}/reports`);
          const latestReport = (latestRes.data || []).find((report) =>
            report.report_type === reportType &&
            !report.content?.aggressive_mode
          );
          if (latestReport?.report_id) {
            if (latestReport.status === "completed") {
              toast.success("Report generated successfully!");
              if (onReportsChange) onReportsChange();
              stopGenerating();
            } else {
              pollForCompletion(latestReport.report_id);
            }
            return;
          }
        } catch (lookupError) {
          console.warn("Report lookup after timeout failed:", lookupError);
        }
        toast.error("Report generation is taking longer than expected. Please try again.");
        stopGenerating();
        return;
      }
      const detail = error?.response?.data?.detail;
      const statusCode = error?.response?.status;
      if (statusCode === 409 && (typeof detail === 'object' ? detail?.message : detail || '').includes("Pipeline is stale")) {
        toast.error("Pipeline is out of date. Please refresh pipeline before generating report.");
        stopGenerating();
        return;
      }
      if (typeof detail === 'string') {
        toast.error(detail);
      } else if (detail?.message) {
        toast.error(detail.message);
      } else {
        toast.error("Failed to start report generation");
      }
      stopGenerating();
    }
  };

  const stopGenerating = () => {
    if (pollingRef.current) { clearInterval(pollingRef.current); pollingRef.current = null; }
    if (elapsedRef.current) { clearInterval(elapsedRef.current); elapsedRef.current = null; }
    setGeneratingReport(false);
    setGenElapsed(0);
  };

  const pollForCompletion = (reportId) => {
    let elapsed = 0;
    const interval = 3000;
    const maxWait = 3600000;

    pollingRef.current = setInterval(async () => {
      elapsed += interval;
      try {
        const res = await axios.get(`${API}/cases/${caseId}/reports/${reportId}/status`);
        const status = res.data?.status;
        if (status === "completed") {
          toast.success("Report generated successfully!");
          if (onReportsChange) onReportsChange();
          stopGenerating();
        } else if (status === "failed") {
          toast.error("Report generation failed. Please try again.");
          if (onReportsChange) onReportsChange();
          stopGenerating();
        }
      } catch {
        // Ignore transient polling errors
      }

      if (elapsed >= maxWait) {
        toast.error("Report generation timed out. Please refresh and check your reports.");
        if (onReportsChange) onReportsChange();
        stopGenerating();
      }
    }, interval);
  };

  const handlePaymentSuccess = () => {
    setShowPaymentModal(false);
    if (pendingReportType) {
      generateReport(pendingReportType);
      setPendingReportType(null);
    }
  };

  const handleVerifyTopIssues = async (limit) => {
    try {
      setPipelineVerifyLoading(true);
      setPipelineVerifyError("");
      setPipelineVerifyResult(null);
      const result = await verifyTopIssues(API, caseId, limit);
      setPipelineVerifyResult(result);
      if (typeof onReportsChange === "function") {
        await onReportsChange();
      }
    } catch (err) {
      setPipelineVerifyError(err?.response?.data?.detail || err.message || "Verification failed");
    } finally {
      setPipelineVerifyLoading(false);
    }
  };

  const [deleteReportId, setDeleteReportId] = useState(null);

  const handleDeleteReport = (reportId) => {
    setDeleteReportId(reportId);
  };
  
  const confirmDeleteReport = async () => {
    const rId = deleteReportId;
    setDeleteReportId(null);
    try {
      await axios.delete(`${API}/cases/${caseId}/reports/${rId}`);
      setReports(reports.filter(r => r.report_id !== rId));
      toast.success("Report deleted");
    } catch (error) {
      toast.error("Failed to delete report");
    }
  };

  const toggleReportExpand = (reportId, isOpen) => {
    setExpandedReports(prev => ({
      ...prev,
      [reportId]: isOpen
    }));
  };

  const getReportTypeLabel = (type) => {
    return REPORT_TYPES.find(t => t.value === type)?.label || type;
  };

  return (
    <>
      {/* Pipeline Verification Block — DO NOT REMOVE */}
      <div className="rounded-lg border border-slate-200 p-3 mb-4 bg-white" data-testid="pipeline-verification-block">
        <div className="font-semibold text-xs text-slate-900 mb-1">Pipeline Verification</div>
        <div className="text-xs text-slate-600 mb-2">
          Verify classified issues before generating a report. This strengthens evidentiary linkage for better output.
        </div>
        <div className="flex flex-wrap gap-2">
          <Button
            variant="outline"
            size="sm"
            onClick={() => handleVerifyTopIssues(3)}
            disabled={pipelineVerifyLoading || generatingReport}
            className="bg-blue-700 text-white hover:bg-blue-600"
            data-testid="verify-top-3-btn"
          >
            {pipelineVerifyLoading ? (
              <><Loader2 className="w-3 h-3 mr-1.5 animate-spin" />Verifying...</>
            ) : "Verify Top 3 Issues"}
          </Button>
          <Button
            variant="outline"
            size="sm"
            onClick={() => handleVerifyTopIssues(6)}
            disabled={pipelineVerifyLoading || generatingReport}
            className="bg-blue-700 text-white hover:bg-blue-600"
            data-testid="verify-top-6-btn"
          >
            {pipelineVerifyLoading ? (
              <><Loader2 className="w-3 h-3 mr-1.5 animate-spin" />Verifying...</>
            ) : "Verify Top 6 Issues"}
          </Button>
        </div>
        {pipelineVerifyError && (
          <div className="mt-3 text-sm text-red-700" data-testid="pipeline-verify-error">{pipelineVerifyError}</div>
        )}
        {pipelineVerifyResult && (
          <div className="mt-3 rounded border border-slate-200 p-3 text-xs text-slate-700 bg-slate-50" data-testid="pipeline-verify-result">
            {pipelineVerifyResult.eligible_issues === 0 ? (
              <div className="font-medium text-green-700">All issues verified. Ready to generate report.</div>
            ) : (
              <>
                <div className="font-medium text-slate-900 mb-1">Verification Complete</div>
                <div>Verified: {pipelineVerifyResult.verified} of {pipelineVerifyResult.attempted} issues</div>
                <div>Grounds synced: {pipelineVerifyResult.synced_count}</div>
              </>
            )}
          </div>
        )}
      </div>

      {/* Action Button — Generate Report */}
      <div className="flex justify-end mb-4">
        <Button 
          onClick={() => setShowReportDialog(true)}
          disabled={generatingReport || pipelineVerifyLoading}
          className="landing-cta-primary"
          data-testid="generate-report-btn"
        >
          {generatingReport ? (
            <>
              <Loader2 className="w-4 h-4 mr-2 animate-spin" />
              Generating...
            </>
          ) : (
            <>
              <FileText className="w-4 h-4 mr-2" />
              Generate Report
            </>
          )}
        </Button>
      </div>

      {generatingReport && (
        <div className="mb-6 rounded-xl overflow-hidden shadow-lg border-2 border-blue-300" data-testid="report-generating-indicator">
          <div className="bg-blue-700 text-white px-6 py-4">
            <div className="flex items-center justify-between flex-wrap gap-3">
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 rounded-full bg-white/20 flex items-center justify-center">
                  <Loader2 className="w-5 h-5 animate-spin text-white" />
                </div>
                <div>
                  <p className="text-lg font-bold text-white">
                    {genElapsed < 30
                      ? "Analysing Case Materials"
                      : genElapsed < 120
                      ? "Writing Legal Analysis"
                      : genElapsed < 300
                      ? "Building Report Sections"
                      : "Finalising Report"}
                  </p>
                  <p className="text-sm text-white/80">
                    {genElapsed < 30
                      ? "Reading documents, timeline events, and grounds..."
                      : genElapsed < 120
                      ? "AI is constructing detailed legal analysis sections..."
                      : genElapsed < 300
                      ? "Multi-section generation in progress — thorough analysis takes time..."
                      : "Completing final sections. Large reports can take 5-15 minutes."}
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
                { label: "Analysing", active: genElapsed >= 15 },
                { label: "Writing", active: genElapsed >= 60 },
                { label: "Finalising", active: genElapsed >= 300 },
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
                style={{ width: `${Math.min(98, (genElapsed / 900) * 100)}%` }}
              />
            </div>
          </div>
        </div>
      )}

      {/* Reports List */}
      {reports.length === 0 ? (
        <Card className="p-12 text-center">
          <FileText className="w-12 h-12 text-slate-300 mx-auto mb-4" />
          <h3 className="text-lg font-semibold text-slate-900 mb-2" style={{ fontFamily: 'Crimson Pro, serif' }}>
            No reports yet
          </h3>
          <p className="text-slate-700 mb-4">
            Generate AI-powered reports to analyse your case documents.
          </p>
          <Button 
            onClick={() => setShowReportDialog(true)}
            disabled={generatingReport}
            className="landing-cta-primary"
          >
            <FileText className="w-4 h-4 mr-2" />
            Generate First Report
          </Button>
        </Card>
      ) : (
        <div className="space-y-4">
          {reports.map((report) => {
            const reportStatus = report.status || 'completed';

            // DO NOT UNDO — Extract report content BEFORE status checks so content stays visible during generating/failed
            const rawReportText = typeof report.content === 'string'
              ? report.content
              : report.content?.analysis || report.content?.backup_analysis || '';
            const reportText = (rawReportText || "")
              .replace(/^\s*DO NOT UNDO\.?\s*$/gim, "")
              .replace(/\n{3,}/g, "\n\n")
              .trim();

            // For generating/failed with NO existing content, show just the status card
            if (reportStatus === 'generating' && !reportText) {
              return (
                <Card key={report.report_id} className="overflow-hidden border border-blue-200 bg-blue-50 shadow-sm">
                  <div className="px-5 py-4 flex items-center justify-between">
                    <div className="flex items-center gap-3">
                      <Loader2 className="w-5 h-5 animate-spin text-blue-600" />
                      <div>
                        <p className="text-sm font-semibold text-blue-900" data-testid={`generating-label-${report.report_id}`}>Generating {getReportTypeLabel(report.report_type)}...</p>
                        <p className="text-xs text-blue-600">This usually takes 1-3 minutes. Please wait.</p>
                      </div>
                    </div>
                    <Button
                      variant="destructive"
                      size="icon"
                      onClick={() => handleDeleteReport(report.report_id)}
                      className="bg-red-600 hover:bg-red-700 text-white rounded-full"
                      data-testid={`delete-report-btn-${report.report_id}`}
                    >
                      <Trash2 className="w-4 h-4" />
                    </Button>
                  </div>
                </Card>
              );
            }

            if (reportStatus === 'failed' && !reportText) {
              const failedMessage = typeof report.error === 'string' && /BadGatewayError|OpenAIException|litellm|502|All LLM attempts failed/i.test(report.error)
                ? 'Report generation was interrupted by a temporary AI service error. Retry resumes from the last completed section.'
                : (report.error || 'Generation was interrupted. Retry resumes from the last completed section.');
              return (
                <Card key={report.report_id} className="overflow-hidden border border-red-200 bg-red-50 shadow-sm">
                  <div className="px-5 py-4 flex items-center justify-between flex-wrap gap-3">
                    <div className="flex items-center gap-3">
                      <AlertCircle className="w-5 h-5 text-red-600" />
                      <div>
                        <p className="text-sm font-semibold text-red-900" data-testid={`failed-label-${report.report_id}`}>Report generation failed</p>
                        <p className="text-xs text-red-600">{failedMessage}</p>
                      </div>
                    </div>
                    <div className="flex items-center gap-2">
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => generateReport(report.report_type)}
                        className="border-red-300 text-red-700 hover:bg-red-100"
                        data-testid={`retry-report-btn-${report.report_id}`}
                      >
                        Retry
                      </Button>
                      <Button
                        variant="destructive"
                        size="icon"
                        onClick={() => handleDeleteReport(report.report_id)}
                        className="bg-red-600 hover:bg-red-700 text-white rounded-full"
                        data-testid={`delete-report-btn-${report.report_id}`}
                      >
                        <Trash2 className="w-4 h-4" />
                      </Button>
                    </div>
                  </div>
                </Card>
              );
            }

            // DO NOT UNDO — Status banner shown ABOVE preserved content for generating/failed states
            const statusBanner = reportStatus === 'generating' ? (
              <Card className="overflow-hidden border border-blue-200 bg-blue-50 shadow-sm" data-testid={`generating-banner-${report.report_id}`}>
                <div className="px-5 py-3 flex items-center justify-between">
                  <div className="flex items-center gap-3">
                    <Loader2 className="w-5 h-5 animate-spin text-blue-600" />
                    <div>
                      <p className="text-sm font-semibold text-blue-900">Regenerating {getReportTypeLabel(report.report_type)}...</p>
                      <p className="text-xs text-blue-600">Your existing report is preserved below while the new version generates.</p>
                    </div>
                  </div>
                  <Button
                    variant="destructive"
                    size="icon"
                    onClick={() => handleDeleteReport(report.report_id)}
                    className="bg-red-600 hover:bg-red-700 text-white rounded-full"
                    data-testid={`delete-report-btn-${report.report_id}`}
                  >
                    <Trash2 className="w-4 h-4" />
                  </Button>
                </div>
              </Card>
            ) : reportStatus === 'failed' ? (
              <Card className="overflow-hidden border border-red-200 bg-red-50 shadow-sm" data-testid={`failed-banner-${report.report_id}`}>
                <div className="px-5 py-3 flex items-center justify-between flex-wrap gap-3">
                  <div className="flex items-center gap-3">
                    <AlertCircle className="w-5 h-5 text-red-600" />
                    <div>
                      <p className="text-sm font-semibold text-red-900">Generation failed — your existing report is preserved below</p>
                      <p className="text-xs text-red-600">
                        {typeof report.error === 'string' && /BadGatewayError|OpenAIException|litellm|502|All LLM attempts failed/i.test(report.error)
                          ? 'Temporary AI service error. Retry resumes from the last completed section.'
                          : (report.error || 'Generation was interrupted. Retry resumes from the last completed section.')}
                      </p>
                    </div>
                  </div>
                  <div className="flex items-center gap-2">
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => generateReport(report.report_type)}
                      className="border-red-300 text-red-700 hover:bg-red-100"
                      data-testid={`retry-report-btn-${report.report_id}`}
                    >
                      Retry
                    </Button>
                    <Button
                      variant="destructive"
                      size="icon"
                      onClick={() => handleDeleteReport(report.report_id)}
                      className="bg-red-600 hover:bg-red-700 text-white rounded-full"
                      data-testid={`delete-report-btn-${report.report_id}`}
                    >
                      <Trash2 className="w-4 h-4" />
                    </Button>
                  </div>
                </div>
              </Card>
            ) : null;
            
            /* Colour theme per report type - matches landing page */
            const rTheme = {
              quick_summary: { headerBg: "bg-emerald-600", badge: "bg-emerald-500", label: "Quick Summary", price: "FREE" },
              full_detailed: { headerBg: "bg-blue-700", badge: "bg-blue-500", label: "Full Detailed Report", price: "$150 AUD" },
              extensive_log: { headerBg: "bg-purple-700", badge: "bg-purple-500", label: "Extensive Log Report", price: "$200 AUD" },
              barrister_view: { headerBg: "bg-teal-500", badge: "bg-teal-400", label: "Barrister Brief", price: "BARRISTER" },
            }[report.report_type] || { headerBg: "bg-slate-200", badge: "bg-slate-400", label: getReportTypeLabel(report.report_type), price: "" };
            
            /* DO NOT UNDO — Content card wrapped with statusBanner above it */
            return (
              <div key={report.report_id} className="space-y-3">
                {/* DO NOT UNDO — statusBanner renders generating/failed indicator ABOVE the content */}
                {statusBanner}
              <Card className="overflow-hidden border-0 shadow-md">
                <Collapsible
                  open={Boolean(expandedReports[report.report_id])}
                  onOpenChange={(isOpen) => toggleReportExpand(report.report_id, isOpen)}
                >
                  <CollapsibleTrigger asChild>
                    <div className={`${rTheme.headerBg} text-white px-5 py-3 cursor-pointer flex items-center justify-between`}>
                      <div className="flex items-center gap-3">
                        {expandedReports[report.report_id] ? (
                          <ChevronDown className="w-5 h-5 text-white/70" />
                        ) : (
                          <ChevronRight className="w-5 h-5 text-white/70" />
                        )}
                        <div>
                          <h4 className="font-semibold text-white text-sm uppercase tracking-wide">
                            {rTheme.label}
                          </h4>
                          <div className="flex items-center gap-2 mt-0.5">
                            <Clock className="w-3 h-3 text-white/60" />
                            <span className="text-xs text-white/70">
                              {new Date(report.generated_at || report.created_at).toLocaleDateString('en-AU', {
                                day: 'numeric', month: 'short', year: 'numeric', hour: '2-digit', minute: '2-digit'
                              })}
                            </span>
                          </div>
                          <div className="flex flex-wrap items-center gap-2 mt-2">
                            <VerificationBadge status={report.verification_status || report.metadata?.verification_status} />
                          </div>
                        </div>
                      </div>
                      <div className="flex items-center gap-2">
                        {rTheme.price && <span className={`${rTheme.badge} px-3 py-1 rounded-full text-xs font-bold text-white`}>{rTheme.price}</span>}
                        <Button
                          variant="destructive"
                          size="icon"
                          onClick={(e) => {
                            e.stopPropagation();
                            handleDeleteReport(report.report_id);
                          }}
                          className="bg-red-600 hover:bg-red-700 text-white rounded-full"
                          data-testid={`delete-report-btn-${report.report_id}`}
                          aria-label="Delete report"
                        >
                          <Trash2 className="w-4 h-4" />
                        </Button>
                      </div>
                    </div>
                  </CollapsibleTrigger>
                  <CollapsibleContent>
                    <div className="px-4 pb-4 border-t border-slate-100 pt-4">
                      {/* DO NOT UNDO - Action buttons at TOP of report box */}
                      <div className="flex flex-wrap items-center gap-2 mb-4 pb-3 border-b border-slate-100">
                        <Button
                          variant="outline"
                          size="sm"
                          onClick={() => report.report_type === 'barrister_view' 
                            ? navigate(`/cases/${caseId}/reports/${report.report_id}/barrister`)
                            : navigate(`/cases/${caseId}/reports/${report.report_id}`)
                          }
                          className="bg-blue-700 text-white hover:bg-blue-600"
                          data-testid={`view-report-btn-${report.report_id}`}
                        >
                          <Eye className="w-4 h-4 mr-1.5" />
                          {report.report_type === 'barrister_view' ? 'View Barrister Brief' : 'Full Report Page'}
                        </Button>
                        {report.report_type === 'extensive_log' && (
                          hasAllReports ? (
                            <Button
                              variant="outline"
                              size="sm"
                              onClick={() => navigate(`/cases/${caseId}/reports/${report.report_id}/barrister`)}
                              className="bg-blue-700 text-white hover:bg-blue-600"
                              data-testid={`barrister-view-btn-${report.report_id}`}
                            >
                              <Presentation className="w-4 h-4 mr-1.5" />
                              Barrister View
                            </Button>
                          ) : (
                            <Button
                              variant="outline"
                              size="sm"
                              disabled
                              className="text-slate-400 border-slate-200 bg-slate-50 opacity-80 cursor-not-allowed"
                              data-testid={`barrister-view-locked-${report.report_id}`}
                            >
                              <Lock className="w-4 h-4 mr-1.5" />
                              Barrister View (locked — generate all 3 reports)
                            </Button>
                          )
                        )}
                        <Button
                          variant="outline"
                          size="sm"
                          onClick={() => handleExportPDF(report.report_id)}
                          className="bg-blue-700 text-white hover:bg-blue-600"
                          data-testid={`export-pdf-btn-${report.report_id}`}
                        >
                          <Download className="w-4 h-4 mr-1.5" />
                          PDF
                        </Button>
                        <Button
                          variant="outline"
                          size="sm"
                          onClick={() => handleExportDOCX(report.report_id)}
                          className="bg-blue-700 text-white hover:bg-blue-600"
                          data-testid={`export-docx-btn-${report.report_id}`}
                        >
                          <FileText className="w-4 h-4 mr-1.5" />
                          Word
                        </Button>
                        <Button
                          variant="outline"
                          size="sm"
                          onClick={() => {
                            navigate(`/cases/${caseId}/reports/${report.report_id}`);
                            toast.info("Navigating to full report - use your browser's print/share option.");
                          }}
                          className="bg-blue-700 text-white hover:bg-blue-600"
                          data-testid={`print-report-btn-${report.report_id}`}
                        >
                          <Printer className="w-4 h-4 mr-1.5" />
                          Print
                        </Button>
                      </div>

                      {/* Draft source & verification badges */}
                      <div className="flex flex-wrap items-center gap-2 mb-3">
                        <VerificationBadge status={report.verification_status || report.metadata?.verification_status} />
                      </div>

                      {/* DO NOT UNDO - Report content rendered as formatted Markdown */}
                      <div className="rounded-lg border border-slate-200 p-5 sm:p-6 bg-white" data-testid={`report-inline-content-${report.report_id}`}>
                        <div className="legal-report">
                          <ReactMarkdown
                            remarkPlugins={[remarkGfm]}
                            components={{
                              a: ({ href, children }) => <a href={href} target="_blank" rel="noopener noreferrer" className="text-blue-600 underline hover:text-blue-800 break-words font-medium">{children}</a>,
                              table: ({ children }) => (
                                <div className="legal-report-table-wrap">
                                  <table>{children}</table>
                                </div>
                              ),
                            }}
                          >
                            {reportText}
                          </ReactMarkdown>
                        </div>

                        {/* AI-analysis warning */}
                        <div className="text-xs text-slate-500 mt-4 pt-3 border-t border-slate-100" data-testid={`report-ai-warning-${report.report_id}`}>
                          This report is AI-assisted analysis for case preparation and legal review. It is not a determination of legal merit or appeal outcome.
                        </div>
                      </div>

                      {/* Report Metadata Panel */}
                      <ReportMetadataPanel
                        metadata={report.metadata}
                        verificationStatus={report.verification_status || report.source_mode}
                      />
                    </div>
                  </CollapsibleContent>
                </Collapsible>
              </Card>
              </div>
            );
          })}
        </div>
      )}

      {/* Report Type Selection Dialog */}
      <Dialog
        open={showReportDialog}
        onOpenChange={(open) => {
          setShowReportDialog(open);
        }}
      >
        <DialogContent className="sm:max-w-lg bg-white text-slate-900 border border-slate-200 max-h-[90vh] overflow-y-auto" data-testid="report-type-dialog">
          <DialogHeader>
            <DialogTitle className="text-2xl text-slate-900" style={{ fontFamily: 'Crimson Pro, serif' }}>
              Generate Report
            </DialogTitle>
            <DialogDescription className="text-slate-700 text-sm">Select the type of report you'd like to generate.</DialogDescription>
          </DialogHeader>
          <div className="space-y-3">
            {REPORT_TYPES.map((type) => {
              const colorMap = {
                emerald: {
                  border: selectedReportType === type.value ? 'border-emerald-500 ring-2 ring-emerald-200' : 'border-slate-200 hover:border-emerald-300',
                  badge: 'bg-emerald-100 text-emerald-700 border-emerald-200',
                  icon: 'bg-emerald-100 text-emerald-700',
                  check: 'text-emerald-600',
                },
                blue: {
                  border: selectedReportType === type.value ? 'border-blue-500 ring-2 ring-blue-200' : 'border-slate-200 hover:border-blue-300',
                  badge: 'bg-blue-100 text-blue-700 border-blue-200',
                  icon: 'bg-blue-100 text-blue-700',
                  check: 'text-blue-600',
                },
                purple: {
                  border: selectedReportType === type.value ? 'border-purple-500 ring-2 ring-purple-200' : 'border-slate-200 hover:border-purple-300',
                  badge: 'bg-purple-100 text-purple-700 border-purple-200',
                  icon: 'bg-purple-100 text-purple-700',
                  check: 'text-purple-600',
                },
              };
              const colors = colorMap[type.color] || colorMap.blue;
              const IconComponent = type.color === 'emerald' ? FileText : type.color === 'blue' ? Scale : BookOpen;
              const paymentBadge = getPaymentBadge(type.value);
              
              return (
                <div
                  key={type.value}
                  onClick={() => setSelectedReportType(type.value)}
                  className={`p-4 border-2 rounded-xl cursor-pointer transition-all bg-white shadow-sm hover:shadow-md ${colors.border}`}
                  data-testid={`report-type-${type.value}`}
                >
                  <div className="flex items-start gap-3">
                    <div className={`w-10 h-10 rounded-lg flex items-center justify-center flex-shrink-0 ${colors.icon}`}>
                      <IconComponent className="w-5 h-5" />
                    </div>
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center justify-between gap-2 mb-1">
                        <h4 className="font-bold text-slate-900 text-base">{type.label}</h4>
                        {type.isFree ? (
                          <Badge variant="outline" className={`${colors.badge} px-3 py-1 text-xs font-bold`}>
                            FREE
                          </Badge>
                        ) : (
                          <div className="flex flex-col items-end gap-1">
                            <Badge variant="outline" className={`${colors.badge} px-3 py-1 text-xs font-bold`}>
                              ${type.price.toFixed(2)} AUD
                            </Badge>
                            {paymentBadge && (
                              <Badge variant="outline" className={`${paymentBadge.className} px-3 py-1 text-[11px] font-bold`} data-testid={`payment-status-badge-${type.value}`}>
                                {paymentBadge.label}
                              </Badge>
                            )}
                          </div>
                        )}
                      </div>
                      <p className="text-sm text-slate-600 mb-2">{type.description}</p>
                      <div className="flex flex-wrap gap-x-3 gap-y-1">
                        {type.features.map((f, i) => (
                          <span key={i} className="flex items-center gap-1 text-xs text-slate-500">
                            <CheckCircle2 className={`w-3 h-3 flex-shrink-0 ${colors.check}`} />
                            {f}
                          </span>
                        ))}
                      </div>
                    </div>
                  </div>
                </div>
              );
            })}

            {/* Barrister View - locked option */}
            <div
              className={`p-4 border-2 rounded-xl transition-all ${
                hasAllReports
                  ? 'border-blue-400 bg-blue-50/50 cursor-pointer hover:shadow-md hover:border-blue-500'
                  : 'border-slate-200 bg-slate-50 opacity-70 cursor-not-allowed'
              } ${selectedReportType === 'barrister_view' ? 'ring-2 ring-blue-200 border-blue-500' : ''}`}
              onClick={() => {
                if (hasAllReports) setSelectedReportType('barrister_view');
              }}
              data-testid="report-type-barrister"
            >
              <div className="flex items-start gap-3">
                <div className={`w-10 h-10 rounded-lg flex items-center justify-center flex-shrink-0 ${hasAllReports ? 'bg-blue-100 text-blue-700' : 'bg-slate-200 text-slate-400'}`}>
                  {hasAllReports ? <Crown className="w-5 h-5" /> : <Lock className="w-5 h-5" />}
                </div>
                <div className="flex-1 min-w-0">
                  <div className="flex items-center justify-between gap-2 mb-1">
                    <h4 className={`font-bold text-base ${hasAllReports ? 'text-slate-900' : 'text-slate-400'}`}>Barrister View</h4>
                    <Badge variant="outline" className={`px-3 py-1 text-xs font-bold ${hasAllReports ? 'bg-blue-100 text-blue-700 border-blue-200' : 'bg-slate-100 text-slate-400 border-slate-200'}`}>
                      {hasAllReports ? 'UNLOCKED' : 'LOCKED'}
                    </Badge>
                  </div>
                  <p className={`text-sm mb-2 ${hasAllReports ? 'text-slate-600' : 'text-slate-400'}`}>
                    {hasAllReports
                      ? "Capstone synthesis combining all three reports into a single barrister-ready brief."
                      : "Generate and pay for all three reports to unlock this view."}
                  </p>
                  {!hasAllReports && (
                    <div className="flex flex-wrap gap-x-3 gap-y-1">
                      <span className="flex items-center gap-1 text-xs text-slate-400">
                        <Lock className="w-3 h-3" />
                        Requires: Quick Summary (Free) + Full Detailed ($150) + Extensive Log ($200)
                      </span>
                    </div>
                  )}
                  {hasAllReports && (
                    <div className="flex flex-wrap gap-x-3 gap-y-1">
                      {["All-in-one brief", "Barrister-ready format", "Complete case synthesis"].map((f, i) => (
                        <span key={i} className="flex items-center gap-1 text-xs text-blue-700">
                          <CheckCircle2 className="w-3 h-3 flex-shrink-0" />
                          {f}
                        </span>
                      ))}
                    </div>
                  )}
                </div>
              </div>
            </div>

            {/* Report tier workflow guidance */}
            <div className="text-xs text-slate-500 mb-3 rounded-lg border border-slate-200 bg-slate-50 p-3" data-testid="report-workflow-guidance">
              Recommended workflow:
              <br />
              &bull; Quick Summary: generate directly
              <br />
              &bull; Full Detailed Report: verify top 3 issues first
              <br />
              &bull; Extensive Log: verify top 6 issues first
            </div>

            {/* Report generation time info */}
            <div className="rounded-xl border border-slate-200 bg-slate-50 p-3" data-testid="report-generation-warning">
              <div className="flex items-center gap-2">
                <Clock className="w-4 h-4 text-slate-500 shrink-0" />
                <p className="text-xs text-slate-600">
                  Reports can take 10-25 minutes for large files. Keep this window open during generation.
                </p>
              </div>
            </div>
          </div>
          <DialogFooter className="flex-col-reverse gap-3 sm:flex-row sm:justify-end">
            <Button onClick={() => setShowReportDialog(false)} className="w-full sm:w-auto bg-blue-700 text-white hover:bg-blue-600" data-testid="report-dialog-cancel">
              Cancel
            </Button>
            <Button 
              onClick={() => {
                if (selectedReportType === 'barrister_view') {
                  // Navigate to barrister view of the extensive_log report
                  const extReport = reports.find(r => r.report_type === 'extensive_log' && r.status === 'completed');
                  if (extReport) {
                    navigate(`/cases/${caseId}/reports/${extReport.report_id}/barrister`);
                    setShowReportDialog(false);
                  } else {
                    toast.error("Extensive Log report not found");
                  }
                  return;
                }
                handleGenerateReport(selectedReportType);
              }}
              disabled={!selectedReportType || generatingReport || pipelineVerifyLoading || (selectedReportType === 'barrister_view' && !hasAllReports)}
              className="w-full sm:w-auto landing-cta-primary px-6 py-4 text-base font-semibold justify-center"
              data-testid="report-dialog-generate"
            >
              {generatingReport ? (
                <Loader2 className="w-4 h-4 mr-2 animate-spin" />
              ) : null}
              {selectedReportType === 'barrister_view' ? 'Open Barrister View' : 'Generate Report'}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* Payment Modal */}
      <PaymentModal
        isOpen={showPaymentModal}
        onClose={() => {
          setShowPaymentModal(false);
          setPendingReportType(null);
        }}
        onPaymentSuccess={handlePaymentSuccess}
        featureType={pendingReportType === 'extensive_log' ? 'extensive_report' : 'full_report'}
        price={pendingReportType === 'extensive_log' ? 200.00 : 150.00}
        caseId={caseId}
      />

      {/* DO NOT UNDO - Delete Report Confirmation Dialog */}
      <AlertDialog open={!!deleteReportId} onOpenChange={() => setDeleteReportId(null)}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>Delete This Report?</AlertDialogTitle>
            <AlertDialogDescription>
              This report will be permanently deleted. You can generate a new one at any time.
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel className="bg-blue-700 text-white hover:bg-blue-600 border-blue-700">Cancel</AlertDialogCancel>
            <AlertDialogAction onClick={confirmDeleteReport} className="bg-red-600 hover:bg-red-700 text-white">
              Delete Report
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>
    </>
  );
};

export default ReportsSection;
