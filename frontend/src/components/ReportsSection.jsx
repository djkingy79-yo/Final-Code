/* DO NOT UNDO — ReportsSection component. All features in this file are approved and must be preserved. */
import { useState } from "react";
import axios from "axios";
import { toast } from "sonner";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import {
  FileText, Loader2, Clock, ChevronDown, ChevronRight, Trash2, Download, Presentation, Eye, Printer
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
  DialogFooter,
} from "./ui/dialog";
import {
  Collapsible,
  CollapsibleContent,
  CollapsibleTrigger,
} from "./ui/collapsible";
import { API } from "../App";
import PaymentModal from "./PaymentModal";

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

  const generateReport = async (reportType) => {
    setGeneratingReport(true);
    setShowReportDialog(false);
    toast.info("Generating report with optimised evidence context. Large cases may still take a few minutes.");
    
    try {
      const response = await axios.post(
        `${API}/cases/${caseId}/reports/generate`,
        { report_type: reportType, aggressive_mode: aggressiveMode },
        { timeout: 240000 }
      );
      
      toast.success("Report generated successfully");
      if (onReportsChange) onReportsChange();
    } catch (error) {
      const detail = error?.response?.data?.detail;
      if (error.code === 'ECONNABORTED') {
        toast.info("Report generation timed out. Please retry — processing is now prioritised for speed.");
      } else if (typeof detail === 'string') {
        toast.error(detail);
      } else if (detail?.message) {
        toast.error(detail.message);
      } else {
        toast.error("Failed to generate report");
      }
    } finally {
      setGeneratingReport(false);
      setAggressiveMode(false);
    }
  };

  const handlePaymentSuccess = () => {
    setShowPaymentModal(false);
    if (pendingReportType) {
      generateReport(pendingReportType);
      setPendingReportType(null);
    }
  };

  const handleDeleteReport = async (reportId) => {
    if (!confirm("Delete this report?")) return;
    
    try {
      await axios.delete(`${API}/cases/${caseId}/reports/${reportId}`);
      setReports(reports.filter(r => r.report_id !== reportId));
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
            const reportText = typeof report.content === 'string'
              ? report.content
              : report.content?.analysis || 'No analysis available';
            return (
              <Card key={report.report_id} className="overflow-hidden">
                <Collapsible
                  open={Boolean(expandedReports[report.report_id])}
                  onOpenChange={(isOpen) => toggleReportExpand(report.report_id, isOpen)}
                >
                  <CollapsibleTrigger asChild>
                    <CardContent className="p-4 cursor-pointer hover:bg-slate-50 transition-colors">
                      <div className="flex items-center justify-between">
                        <div className="flex items-center gap-3">
                          {expandedReports[report.report_id] ? (
                            <ChevronDown className="w-5 h-5 text-slate-400" />
                          ) : (
                            <ChevronRight className="w-5 h-5 text-slate-400" />
                          )}
                          <div>
                            <h4 className="font-semibold text-slate-900">
                              {getReportTypeLabel(report.report_type)}
                            </h4>
                            <div className="flex items-center gap-2 mt-1">
                              <Clock className="w-3 h-3 text-slate-400" />
                              <span className="text-xs text-slate-500">
                                {new Date(report.generated_at || report.created_at).toLocaleDateString('en-AU', {
                                  day: 'numeric',
                                  month: 'short',
                                  year: 'numeric',
                                  hour: '2-digit',
                                  minute: '2-digit'
                                })}
                              </span>
                            </div>
                          </div>
                        </div>
                        <div className="flex items-center gap-2">
                          <Badge variant="outline" className="bg-emerald-50 text-emerald-700 border-emerald-200">
                            AI Generated
                          </Badge>
                          {report?.content?.aggressive_mode && (
                            <Badge variant="outline" className="bg-rose-50 text-rose-700 border-rose-200" data-testid={`aggressive-report-badge-${report.report_id}`}>
                              Aggressive
                            </Badge>
                          )}
                          <Button
                            variant="ghost"
                            size="icon"
                            onClick={(e) => {
                              e.stopPropagation();
                              handleDeleteReport(report.report_id);
                            }}
                            className="text-slate-400 hover:text-red-600"
                          >
                            <Trash2 className="w-4 h-4" />
                          </Button>
                        </div>
                      </div>
                    </CardContent>
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
                          onClick={() => window.print()}
                          className="text-slate-700"
                          data-testid={`print-report-btn-${report.report_id}`}
                        >
                          <Printer className="w-4 h-4 mr-1.5" />
                          Print
                        </Button>
                      </div>

                      {/* DO NOT UNDO — Report content rendered as formatted Markdown */}
                      <div className="rounded-lg border border-slate-200 p-4 bg-white" data-testid={`report-inline-content-${report.report_id}`}>
                        <div className="prose prose-slate prose-sm max-w-none">
                          <ReactMarkdown
                            remarkPlugins={[remarkGfm]}
                            components={{
                              h1: ({ children }) => <h1 className="text-xl font-bold mt-5 mb-3 text-slate-900" style={{ fontFamily: "Crimson Pro, serif" }}>{children}</h1>,
                              h2: ({ children }) => <h2 className="text-lg font-bold mt-4 mb-2 text-slate-900" style={{ fontFamily: "Crimson Pro, serif" }}>{children}</h2>,
                              h3: ({ children }) => <h3 className="text-base font-semibold mt-3 mb-2 text-slate-800">{children}</h3>,
                              p: ({ children }) => <p className="text-slate-700 leading-7 mb-3">{children}</p>,
                              ul: ({ children }) => <ul className="list-disc ml-5 mb-3 space-y-1 text-slate-700">{children}</ul>,
                              ol: ({ children }) => <ol className="list-decimal ml-5 mb-3 space-y-1 text-slate-700">{children}</ol>,
                              li: ({ children }) => <li className="leading-7">{children}</li>,
                              blockquote: ({ children }) => <blockquote className="border-l-4 border-indigo-300 pl-4 italic text-slate-700 my-3">{children}</blockquote>,
                              a: ({ href, children }) => <a href={href} target="_blank" rel="noopener noreferrer" className="text-indigo-600 hover:text-indigo-800 underline">{children}</a>,
                              table: ({ children }) => (
                                <div className="overflow-x-auto rounded-lg border border-slate-200 my-4">
                                  <table className="min-w-full text-sm">{children}</table>
                                </div>
                              ),
                              thead: ({ children }) => <thead className="bg-slate-100">{children}</thead>,
                              th: ({ children }) => <th className="px-3 py-2 text-left font-semibold text-slate-800 border-b border-slate-200">{children}</th>,
                              td: ({ children }) => <td className="px-3 py-2 align-top text-slate-700 border-b border-slate-100">{children}</td>,
                              code: ({ children }) => <code className="text-xs bg-slate-100 text-slate-700 px-1.5 py-0.5 rounded">{children}</code>,
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
          </DialogHeader>
          <div className="space-y-3">
            <p className="text-sm text-slate-600">
              Select the type of report you'd like to generate:
            </p>
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
    </>
  );
};

export default ReportsSection;
