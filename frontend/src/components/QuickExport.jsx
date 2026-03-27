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
  CheckCircle, FolderArchive
} from "lucide-react";
import { Button } from "./ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "./ui/card";
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
  }, [showDialog, caseId]);

  const handleExport = async () => {
    setExporting(true);
    try {
      const response = await axios.post(
        `${API}/cases/${caseId}/export/package`,
        options,
        { responseType: 'blob' }
      );
      
      // Create download link
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      
      // Get filename from header or generate one
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
            <DialogTitle className="flex items-center gap-3" style={{ fontFamily: 'Crimson Pro, serif' }}>
              <div className="w-10 h-10 rounded-xl bg-emerald-100 flex items-center justify-center">
                <FolderArchive className="w-5 h-5 text-emerald-600" />
              </div>
              Export Appeal Package
            </DialogTitle>
          </DialogHeader>

          <div className="py-4">
            <p className="text-sm text-slate-600 mb-4">
              Generate a comprehensive ZIP package with all case materials and editable legal templates.
            </p>

            {loading ? (
              <div className="flex items-center justify-center py-8">
                <Loader2 className="w-8 h-8 animate-spin text-emerald-600" />
              </div>
            ) : (
              <div className="space-y-3">
                {exportItems.map((item) => (
                  <label
                    key={item.key}
                    className={`flex items-center gap-3 p-3 rounded-xl border cursor-pointer transition-colors ${
                      options[item.key]
                        ? "bg-emerald-50 border-emerald-300"
                        : "bg-white border-slate-200 hover:bg-slate-50"
                    }`}
                  >
                    <Checkbox
                      checked={options[item.key]}
                      onCheckedChange={() => toggleOption(item.key)}
                      className="data-[state=checked]:bg-emerald-600"
                    />
                    <item.icon className={`w-5 h-5 ${options[item.key] ? "text-emerald-600" : "text-slate-600"}`} />
                    <span className="flex-1 font-medium text-slate-900">{item.label}</span>
                    <Badge variant="outline" className="text-xs">
                      {item.count ?? 0}
                    </Badge>
                  </label>
                ))}
              </div>
            )}

            {/* Templates Info */}
            <div className="mt-4 p-4 bg-blue-50 border border-blue-200 rounded-xl">
              <h4 className="text-sm font-semibold text-blue-800 mb-2 flex items-center gap-2">
                <FileCode className="w-4 h-4" />
                Included Templates
              </h4>
              <ul className="text-xs text-blue-700 space-y-1">
                <li>• Notice of Intention to Appeal</li>
                <li>• Application for Leave to Appeal</li>
                <li>• Written Submissions Template</li>
                <li>• Fresh Evidence Affidavit</li>
                <li>• Chronology of Proceedings</li>
              </ul>
              <p className="text-xs text-blue-600 mt-2 italic">
                All templates are pre-filled with your case details
              </p>
            </div>
          </div>

          <DialogFooter className="gap-3">
            <Button variant="outline" onClick={() => setShowDialog(false)}>
              Cancel
            </Button>
            <Button
              onClick={handleExport}
              disabled={exporting || loading}
              className="bg-gradient-to-r from-emerald-600 to-emerald-700 text-white hover:from-emerald-700 hover:to-emerald-800"
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
