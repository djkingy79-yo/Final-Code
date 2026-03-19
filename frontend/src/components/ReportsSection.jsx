/* ========================================================================
   DO NOT UNDO — ENTIRE FILE PROTECTED
   All features, functions, styles, and content in this file are approved
   and must be preserved. Do not remove, rename, or refactor any code.
   ======================================================================== */
import { useState, useEffect, useRef } from "react";
import axios from "axios";
import { toast } from "sonner";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import {
  FileText, Loader2, Clock, ChevronDown, ChevronRight, Trash2, Download, Presentation, Eye, Printer, AlertCircle
} from "lucide-react";
import { Button } from "./ui/button";
import { Card, CardContent } from "./ui/card";
import { Badge } from "./ui/badge";
import { Switch } from "./ui/switch";
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

const REPORT_TYPES = [
  { 
    value: "quick_summary", 
    label: "Quick Summary", 
    description: "Rapid triage brief with key grounds preview and immediate next steps",
    price: 0,
    priceId: null,
    isFree: true
  },
  { 
    value: "full_detailed", 
    label: "Full Detailed Report", 
    description: "Barrister-grade deep dossier with comparative sentencing, appeal forms, external case links and full options matrix",
    price: 150.00,
    priceId: "full_report",
    isFree: false
  },
  { 
    value: "extensive_log", 
    label: "Extensive Log Report", 
    description: "Master litigation brief with expanded precedent modelling, appeal filing steps, external law links and hearing script",
    price: 200.00,
    priceId: "extensive_report",
    isFree: false
  }
];

const ReportsSection = ({ 
  caseId, 
  reports, 
  setReports, 
  onReportsChange,
  documents,
  navigate,
  isAdmin
}) => {
  const [showReportDialog, setShowReportDialog] = useState(false);
  const [selectedReportType, setSelectedReportType] = useState(null);
  const [generatingReport, setGeneratingReport] = useState(false);
  const [expandedReports, setExpandedReports] = useState({});
  const [showPaymentModal, setShowPaymentModal] = useState(false);
  const [pendingReportType, setPendingReportType] = useState(null);
  const [aggressiveMode, setAggressiveMode] = useState(false);

  const handleExportPDF = async (reportId) => {
    try {
      toast.info("Generating PDF...");
      const response = await axios.get(
        `${API}/cases/${caseId}/reports/${reportId}/export-pdf`,
        { responseType: 'blob' }
      );
      const blob = new Blob([response.data], { type: 'application/pdf' });
      const url = window.URL.createObjectURL(blob);
      
      // iOS Safari doesn't support programmatic downloads well
      // Open in new tab instead
      const isIOS = /iPad|iPhone|iPod/.test(navigator.userAgent);
      if (isIOS) {
        window.open(url, '_blank');
      } else {
        const link = document.createElement('a');
        link.href = url;
        link.setAttribute('download', `report_${reportId}.pdf`);
        document.body.appendChild(link);
        link.click();
        link.remove();
      }
      
      setTimeout(() => window.URL.revokeObjectURL(url), 5000);
      toast.success("PDF ready!");
    } catch (error) {
      console.error("PDF export error:", error);
      toast.error("Failed to export PDF");
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
    if (existingReport) {
      // Already generated this type, just regenerate
      generateReport(reportType);
      return;
    }
    
    // Need to pay first for premium reports
    setPendingReportType(reportType);
    setShowPaymentModal(true);
  };

  const pollingRef = useRef(null);

  // Clean up polling on unmount
  useEffect(() => {
    return () => {
      if (pollingRef.current) clearInterval(pollingRef.current);
    };
  }, []);

  const generateReport = async (reportType) => {
    setGeneratingReport(true);
    setShowReportDialog(false);
    toast.info("Generating report — usually takes 20-60 seconds.");
    
    try {
      const response = await axios.post(
        `${API}/cases/${caseId}/reports/generate`,
        { report_type: reportType, aggressive_mode: aggressiveMode },
        { timeout: 30000 }
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
        setAggressiveMode(false);
      }
    } catch (error) {
      const detail = error?.response?.data?.detail;
      if (typeof detail === 'string') {
        toast.error(detail);
      } else if (detail?.message) {
        toast.error(detail.message);
      } else {
        toast.error("Failed to start report generation");
      }
      setGeneratingReport(false);
      setAggressiveMode(false);
    }
  };

  const pollForCompletion = (reportId) => {
    let elapsed = 0;
    const interval = 3000; // poll every 3 seconds
    const maxWait = 180000; // 3 minutes max

    pollingRef.current = setInterval(async () => {
      elapsed += interval;
      try {
        const res = await axios.get(`${API}/cases/${caseId}/reports/${reportId}/status`);
        const status = res.data?.status;
        if (status === "completed") {
          clearInterval(pollingRef.current);
          pollingRef.current = null;
          toast.success("Report generated successfully!");
          if (onReportsChange) onReportsChange();
          setGeneratingReport(false);
          setAggressiveMode(false);
        } else if (status === "failed") {
          clearInterval(pollingRef.current);
          pollingRef.current = null;
          toast.error("Report generation failed. Please try again.");
          setGeneratingReport(false);
          setAggressiveMode(false);
        }
      } catch {
        // Ignore transient polling errors
      }

      if (elapsed >= maxWait) {
        clearInterval(pollingRef.current);
        pollingRef.current = null;
        toast.error("Report generation timed out. Please check back shortly.");
        if (onReportsChange) onReportsChange();
        setGeneratingReport(false);
        setAggressiveMode(false);
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
      {/* Action Button */}
      <div className="flex justify-end mb-4">
        <Button 
          onClick={() => setShowReportDialog(true)}
          disabled={generatingReport}
          className="bg-slate-900 text-white hover:bg-slate-800"
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
        <div className="mb-4 border border-blue-200 bg-blue-50 rounded-lg overflow-hidden p-4" data-testid="report-generating-indicator">
          <div className="flex items-center gap-3 mb-2">
            <Loader2 className="w-5 h-5 animate-spin text-blue-600 flex-shrink-0" />
            <p className="text-sm font-semibold text-blue-900">AI is analysing your case. Please allow time for generation.</p>
          </div>
          <p className="text-xs text-blue-700 mb-3">Usually takes 20-60 seconds. Do not close this page.</p>
          <div className="w-full h-2 bg-blue-200 rounded-full overflow-hidden">
            <div className="h-full w-3/4 bg-blue-600 rounded-full animate-pulse"></div>
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
          <p className="text-slate-600 mb-4">
            Generate AI-powered reports to analyse your case documents.
          </p>
          <Button 
            onClick={() => setShowReportDialog(true)}
            disabled={generatingReport}
            className="bg-slate-900 text-white hover:bg-slate-800"
          >
            <FileText className="w-4 h-4 mr-2" />
            Generate First Report
          </Button>
        </Card>
      ) : (
        <div className="space-y-4">
          {reports.map((report) => {
            const reportStatus = report.status || 'completed';

            // Show inline card for generating/failed reports
            if (reportStatus === 'generating') {
              return (
                <Card key={report.report_id} className="overflow-hidden border border-blue-200 bg-blue-50 shadow-sm">
                  <div className="px-5 py-4 flex items-center justify-between">
                    <div className="flex items-center gap-3">
                      <Loader2 className="w-5 h-5 animate-spin text-blue-600" />
                      <div>
                        <p className="text-sm font-semibold text-blue-900">Generating {getReportTypeLabel(report.report_type)}...</p>
                        <p className="text-xs text-blue-600">This usually takes 20-60 seconds.</p>
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

            if (reportStatus === 'failed') {
              return (
                <Card key={report.report_id} className="overflow-hidden border border-red-200 bg-red-50 shadow-sm">
                  <div className="px-5 py-4 flex items-center justify-between">
                    <div className="flex items-center gap-3">
                      <AlertCircle className="w-5 h-5 text-red-600" />
                      <div>
                        <p className="text-sm font-semibold text-red-900">Report generation failed</p>
                        <p className="text-xs text-red-600">Please delete and try again.</p>
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

            const reportText = typeof report.content === 'string'
              ? report.content
              : report.content?.analysis || 'No analysis available';
            
            /* Colour theme per report type — matches landing page */
            const rTheme = {
              quick_summary: { headerBg: "bg-gradient-to-r from-emerald-700 to-green-600", badge: "bg-green-500", label: "Quick Summary", price: "FREE" },
              full_detailed: { headerBg: "bg-gradient-to-r from-slate-900 to-blue-900", badge: "bg-blue-500", label: "Full Detailed Report", price: "$150 AUD" },
              extensive_log: { headerBg: "bg-gradient-to-r from-purple-900 via-slate-900 to-indigo-900", badge: "bg-purple-500", label: "Extensive Log Report", price: "$200 AUD" },
            }[report.report_type] || { headerBg: "bg-slate-800", badge: "bg-slate-500", label: getReportTypeLabel(report.report_type), price: "" };
            
            return (
              <Card key={report.report_id} className="overflow-hidden border-0 shadow-md">
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
                        </div>
                      </div>
                      <div className="flex items-center gap-2">
                        {rTheme.price && <span className={`${rTheme.badge} px-3 py-1 rounded-full text-xs font-bold text-white`}>{rTheme.price}</span>}
                        {report?.content?.aggressive_mode && (
                          <span className="bg-red-500 px-2 py-0.5 rounded-full text-xs font-bold" data-testid={`aggressive-report-badge-${report.report_id}`}>Aggressive</span>
                        )}
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
                      {/* DO NOT UNDO — Action buttons at TOP of report box */}
                      <div className="flex flex-wrap items-center gap-2 mb-4 pb-3 border-b border-slate-100">
                        <Button
                          variant="outline"
                          size="sm"
                          onClick={() => navigate(`/cases/${caseId}/reports/${report.report_id}`)}
                          className="text-slate-700"
                          data-testid={`view-report-btn-${report.report_id}`}
                        >
                          <Eye className="w-4 h-4 mr-1.5" />
                          Full Report Page
                        </Button>
                        <Button
                          variant="outline"
                          size="sm"
                          onClick={() => navigate(`/cases/${caseId}/reports/${report.report_id}/barrister`)}
                          className="text-slate-700"
                          data-testid={`barrister-view-btn-${report.report_id}`}
                        >
                          <Presentation className="w-4 h-4 mr-1.5" />
                          Barrister View
                        </Button>
                        <Button
                          variant="outline"
                          size="sm"
                          onClick={() => handleExportPDF(report.report_id)}
                          className="text-slate-700"
                          data-testid={`export-pdf-btn-${report.report_id}`}
                        >
                          <Download className="w-4 h-4 mr-1.5" />
                          Export PDF
                        </Button>
                        <Button
                          variant="outline"
                          size="sm"
                          onClick={() => {
                            navigate(`/cases/${caseId}/reports/${report.report_id}`);
                            toast.info("Navigating to full report — use your browser's print/share option.");
                          }}
                          className="text-slate-700"
                          data-testid={`print-report-btn-${report.report_id}`}
                        >
                          <Printer className="w-4 h-4 mr-1.5" />
                          Print
                        </Button>
                      </div>

                      {/* DO NOT UNDO — Report content rendered as formatted Markdown */}
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
                      </div>
                    </div>
                  </CollapsibleContent>
                </Collapsible>
              </Card>
            );
          })}
        </div>
      )}

      {/* Report Type Selection Dialog */}
      <Dialog
        open={showReportDialog}
        onOpenChange={(open) => {
          setShowReportDialog(open);
          if (!open) setAggressiveMode(false);
        }}
      >
        <DialogContent className="sm:max-w-lg">
          <DialogHeader>
            <DialogTitle style={{ fontFamily: 'Crimson Pro, serif' }}>
              Generate Report
            </DialogTitle>
            <DialogDescription>Select the type of report you'd like to generate.</DialogDescription>
          </DialogHeader>
          <div className="space-y-3">
            {REPORT_TYPES.map((type) => (
              <div
                key={type.value}
                onClick={() => setSelectedReportType(type.value)}
                className={`p-4 border rounded-lg cursor-pointer transition-colors ${
                  selectedReportType === type.value 
                    ? 'border-slate-900 bg-slate-50' 
                    : 'border-slate-200 hover:border-slate-300'
                }`}
              >
                <div className="flex items-center justify-between">
                  <div>
                    <h4 className="font-medium text-slate-900">{type.label}</h4>
                    <p className="text-sm text-slate-600 mt-1">{type.description}</p>
                  </div>
                  {type.isFree ? (
                    <Badge variant="outline" className="bg-emerald-50 text-emerald-700 border-emerald-200">
                      FREE
                    </Badge>
                  ) : (
                    <Badge variant="outline" className="bg-blue-50 text-blue-700 border-blue-200">
                      ${type.price.toFixed(2)} AUD
                    </Badge>
                  )}
                </div>
              </div>
            ))}

            <div className="rounded-lg border border-rose-200 bg-rose-50 p-3" data-testid="aggressive-mode-container">
              <div className="flex items-center justify-between gap-3">
                <div>
                  <p className="text-sm font-semibold text-rose-900">Aggressive Mode</p>
                  <p className="text-xs text-rose-700">
                    Uses stronger advocacy language with primary and fallback orders sought.
                  </p>
                </div>
                <Switch
                  checked={aggressiveMode}
                  onCheckedChange={setAggressiveMode}
                  data-testid="aggressive-mode-switch"
                />
              </div>
            </div>

            {/* DO NOT UNDO — Report generation time warning */}
            <div className="rounded-lg border border-blue-200 bg-blue-50 p-3" data-testid="report-generation-warning">
              <div className="flex items-start gap-2">
                <AlertCircle className="w-4 h-4 text-blue-600 mt-0.5 shrink-0" />
                <div>
                  <p className="text-sm font-semibold text-blue-900">Please Allow Time for Generation</p>
                  <p className="text-xs text-blue-700">
                    Reports typically take 20-60 seconds to generate. Please do not close this page while generating.
                  </p>
                </div>
              </div>
            </div>
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setShowReportDialog(false)}>
              Cancel
            </Button>
            <Button 
              onClick={() => handleGenerateReport(selectedReportType)}
              disabled={!selectedReportType || generatingReport}
              className="bg-slate-900 text-white hover:bg-slate-800"
            >
              {generatingReport ? (
                <Loader2 className="w-4 h-4 mr-2 animate-spin" />
              ) : null}
              Generate Report
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

      {/* DO NOT UNDO — Delete Report Confirmation Dialog */}
      <AlertDialog open={!!deleteReportId} onOpenChange={() => setDeleteReportId(null)}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>Delete This Report?</AlertDialogTitle>
            <AlertDialogDescription>
              This report will be permanently deleted. You can generate a new one at any time.
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel>Cancel</AlertDialogCancel>
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
