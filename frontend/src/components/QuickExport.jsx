/* ========================================================================
   DO NOT UNDO — ENTIRE FILE PROTECTED
   All features, functions, styles, and content in this file are approved
   and must be preserved. Do not remove, rename, or refactor any code.
   ======================================================================== */
import { useState, useEffect } from "react";
import axios from "axios";
import { toast } from "sonner";
import { 
  Download, Package, FileText, Clock, Gavel, 
  MessageSquare, Scale, Search, FileCode, Loader2,
  FolderArchive, FileDown
} from "lucide-react";
import { Button } from "./ui/button";
import { Badge } from "./ui/badge";
import { Checkbox } from "./ui/checkbox";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogFooter,
} from "./ui/dialog";
import { API } from "../App";

const QuickExport = ({ caseId, caseTitle }) => {
  const [showDialog, setShowDialog] = useState(false);
  const [preview, setPreview] = useState(null);
  const [loading, setLoading] = useState(false);
  const [exporting, setExporting] = useState(false);
  const [exportingPDF, setExportingPDF] = useState(false);
  const [options, setOptions] = useState({
    include_documents: true,
    include_timeline: true,
    include_grounds: true,
    include_notes: true,
    include_reports: true,
    include_analysis: true,
    include_templates: true
  });

  const fetchPreview = async () => {
    setLoading(true);
    try {
      const response = await axios.get(`${API}/cases/${caseId}/export/preview`);
      setPreview(response.data);
    } catch (error) {
      toast.error("Failed to load export preview");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (showDialog) {
      fetchPreview();
    }
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [showDialog, caseId]);

  const handleExport = async () => {
    setExporting(true);
    try {
      const response = await axios.post(
        `${API}/cases/${caseId}/export/package`,
        options,
        { responseType: 'blob' }
      );
      
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      
      const contentDisposition = response.headers['content-disposition'];
      let filename = `Appeal_Package_${caseTitle?.replace(/[^a-zA-Z0-9]/g, '_') || 'case'}.zip`;
      if (contentDisposition) {
        const match = contentDisposition.match(/filename="(.+)"/);
        if (match) filename = match[1];
      }
      
      link.setAttribute('download', filename);
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(url);
      
      toast.success("Appeal package downloaded successfully!");
      setShowDialog(false);
    } catch (error) {
      toast.error("Failed to generate export package");
    } finally {
      setExporting(false);
    }
  };

  const handleExportPDF = async () => {
    setExportingPDF(true);
    try {
      const response = await axios.get(
        `${API}/cases/${caseId}/export/case-pack`,
        { responseType: 'blob', timeout: 120000 }
      );

      const url = window.URL.createObjectURL(new Blob([response.data], { type: 'application/pdf' }));

      // On iOS Safari, blob downloads can break — open in new tab instead
      const isIOS = /iPad|iPhone|iPod/.test(navigator.userAgent);
      if (isIOS) {
        window.open(url, '_blank');
        toast.success("PDF opened — use Share to save.");
      } else {
        const link = document.createElement('a');
        link.href = url;
        const contentDisposition = response.headers['content-disposition'];
        let filename = `Case_Export_Pack_${caseTitle?.replace(/[^a-zA-Z0-9]/g, '_') || 'case'}.pdf`;
        if (contentDisposition) {
          const match = contentDisposition.match(/filename="(.+)"/);
          if (match) filename = match[1];
        }
        link.setAttribute('download', filename);
        document.body.appendChild(link);
        link.click();
        link.remove();
        window.URL.revokeObjectURL(url);
        toast.success("Case Export Pack PDF downloaded!");
      }
      setShowDialog(false);
    } catch (error) {
      if (error.response?.status === 404) {
        toast.error("No completed reports found. Generate at least one report first.");
      } else {
        toast.error("Failed to generate PDF export pack");
      }
    } finally {
      setExportingPDF(false);
    }
  };

  const toggleOption = (key) => {
    setOptions(prev => ({ ...prev, [key]: !prev[key] }));
  };

  const exportItems = [
    { key: "include_documents", label: "Documents", icon: FileText, count: preview?.documents },
    { key: "include_timeline", label: "Timeline Events", icon: Clock, count: preview?.timeline_events },
    { key: "include_grounds", label: "Grounds of Merit", icon: Gavel, count: preview?.grounds_of_merit },
    { key: "include_notes", label: "Case Notes", icon: MessageSquare, count: preview?.notes },
    { key: "include_reports", label: "Generated Reports", icon: Scale, count: preview?.reports },
    { key: "include_analysis", label: "AI Analysis", icon: Search, count: preview?.ai_analysis_scans },
    { key: "include_templates", label: "Editable Templates", icon: FileCode, count: 5 }
  ];

  return (
    <>
      <Button
        onClick={() => setShowDialog(true)}
        className="bg-blue-700 text-white hover:bg-blue-600 rounded-xl shadow-lg shadow-blue-700/20"
        data-testid="quick-export-btn"
      >
        <Package className="w-4 h-4 mr-2" />
        Quick Export
      </Button>

      <Dialog open={showDialog} onOpenChange={setShowDialog}>
        <DialogContent className="max-w-lg">
          <DialogHeader>
            <DialogTitle className="flex items-center gap-3" style={{ fontFamily: "'Times New Roman', Times, serif" }}>
              <div className="w-10 h-10 rounded-xl bg-blue-100 flex items-center justify-center">
                <FolderArchive className="w-5 h-5 text-blue-600" />
              </div>
              Export Case Materials
            </DialogTitle>
          </DialogHeader>

          <div className="py-4">
            {/* Case Export Pack PDF — PRIMARY ACTION */}
            <div className="p-4 bg-blue-50 border-2 border-blue-300 rounded-xl mb-4">
              <h4 className="text-sm font-bold text-blue-900 mb-2 flex items-center gap-2">
                <FileDown className="w-4 h-4" />
                Case Export Pack (Formatted PDF)
              </h4>
              <p className="text-xs text-blue-700 mb-3">
                Download a single, professionally formatted PDF containing ALL your generated reports
                with proper legal layout, headings, margins, page numbers, grounds of merit, timeline, and disclaimers.
                Only includes reports already generated and paid for.
              </p>
              <Button
                onClick={handleExportPDF}
                disabled={exportingPDF || loading}
                className="w-full bg-blue-600 text-white hover:bg-blue-700 font-semibold"
                data-testid="export-case-pack-pdf-btn"
              >
                {exportingPDF ? (
                  <>
                    <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                    Generating PDF...
                  </>
                ) : (
                  <>
                    <FileDown className="w-4 h-4 mr-2" />
                    Download Case Export Pack (PDF)
                  </>
                )}
              </Button>
            </div>

            {/* Divider */}
            <div className="flex items-center gap-3 mb-4">
              <div className="flex-1 h-px bg-slate-200"></div>
              <span className="text-xs text-slate-500 font-medium">OR DOWNLOAD RAW DATA</span>
              <div className="flex-1 h-px bg-slate-200"></div>
            </div>

            <p className="text-sm text-slate-600 mb-4">
              Select items to include in a ZIP archive with raw data files and editable templates.
            </p>

            {loading ? (
              <div className="flex items-center justify-center py-8">
                <Loader2 className="w-8 h-8 animate-spin text-blue-600" />
              </div>
            ) : (
              <div className="space-y-3">
                {exportItems.map((item) => (
                  <label
                    key={item.key}
                    className={`flex items-center gap-3 p-3 rounded-xl border cursor-pointer transition-colors ${
                      options[item.key]
                        ? "bg-blue-50 border-blue-300"
                        : "bg-white border-slate-200 hover:bg-slate-50"
                    }`}
                  >
                    <Checkbox
                      checked={options[item.key]}
                      onCheckedChange={() => toggleOption(item.key)}
                      className="data-[state=checked]:bg-blue-600"
                    />
                    <item.icon className={`w-5 h-5 ${options[item.key] ? "text-blue-600" : "text-slate-600"}`} />
                    <span className="flex-1 font-medium text-slate-900">{item.label}</span>
                    <Badge variant="outline" className="text-xs">
                      {item.count ?? 0}
                    </Badge>
                  </label>
                ))}
              </div>
            )}

            {/* Templates Info */}
            <div className="mt-4 p-4 bg-slate-50 border border-slate-200 rounded-xl">
              <h4 className="text-sm font-semibold text-slate-800 mb-2 flex items-center gap-2">
                <FileCode className="w-4 h-4" />
                Included Templates
              </h4>
              <ul className="text-xs text-slate-700 space-y-1">
                <li>- Notice of Intention to Appeal</li>
                <li>- Application for Leave to Appeal</li>
                <li>- Written Submissions Template</li>
                <li>- Fresh Evidence Affidavit</li>
                <li>- Chronology of Proceedings</li>
              </ul>
              <p className="text-xs text-slate-600 mt-2 italic">
                All templates are pre-filled with your case details
              </p>
            </div>
          </div>

          <DialogFooter className="gap-3">
            <Button onClick={() => setShowDialog(false)} className="bg-slate-200 text-slate-700 hover:bg-slate-300">
              Cancel
            </Button>
            <Button
              onClick={handleExport}
              disabled={exporting || loading}
              className="bg-blue-700 text-white hover:bg-blue-600"
              data-testid="download-zip-btn"
            >
              {exporting ? (
                <>
                  <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                  Generating...
                </>
              ) : (
                <>
                  <Download className="w-4 h-4 mr-2" />
                  Download ZIP
                </>
              )}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </>
  );
};

export default QuickExport;
