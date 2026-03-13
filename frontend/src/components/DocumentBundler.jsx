/* DO NOT UNDO — DocumentBundler component. All features in this file are approved and must be preserved. */
import { useState } from "react";
import axios from "axios";
import { toast } from "sonner";
import { 
  FileStack, Download, FileText, Loader2, CheckCircle,
  List, X
} from "lucide-react";
import { Button } from "./ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "./ui/card";
import { Badge } from "./ui/badge";
import { Checkbox } from "./ui/checkbox";
import { Input } from "./ui/input";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogFooter,
} from "./ui/dialog";
import { API } from "../App";

const DocumentBundler = ({ caseId, documents }) => {
  const [showDialog, setShowDialog] = useState(false);
  const [selectedDocs, setSelectedDocs] = useState([]);
  const [bundleTitle, setBundleTitle] = useState("Document Bundle");
  const [includeToc, setIncludeToc] = useState(true);
  const [generating, setGenerating] = useState(false);

  const toggleDocument = (docId) => {
    setSelectedDocs(prev => 
      prev.includes(docId)
        ? prev.filter(id => id !== docId)
        : [...prev, docId]
    );
  };

  const selectAll = () => {
    if (selectedDocs.length === documents.length) {
      setSelectedDocs([]);
    } else {
      setSelectedDocs(documents.map(d => d.document_id));
    }
  };

  const generateBundle = async () => {
    if (selectedDocs.length === 0) {
      toast.error("Please select at least one document");
      return;
    }

    setGenerating(true);
    try {
      const response = await axios.post(
        `${API}/cases/${caseId}/export/bundle`,
        {
          document_ids: selectedDocs,
          include_toc: includeToc,
          title: bundleTitle
        },
        { responseType: 'blob' }
      );
      
      // Create download link
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `${bundleTitle.replace(/[^a-zA-Z0-9]/g, '_')}.pdf`);
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(url);
      
      toast.success("Document bundle downloaded!");
      setShowDialog(false);
    } catch (error) {
      toast.error("Failed to generate bundle");
    } finally {
      setGenerating(false);
    }
  };

  const getCategoryColor = (category) => {
    const colors = {
      court_documents: "bg-blue-100 text-blue-700 dark:bg-blue-900/30 dark:text-blue-400",
      evidence: "bg-amber-100 text-amber-700 dark:bg-amber-900/30 dark:text-amber-400",
      witness_statements: "bg-purple-100 text-purple-700 dark:bg-purple-900/30 dark:text-purple-400",
      police_documents: "bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-400",
      legal_correspondence: "bg-emerald-100 text-emerald-700 dark:bg-emerald-900/30 dark:text-emerald-400",
      medical_records: "bg-pink-100 text-pink-700 dark:bg-pink-900/30 dark:text-pink-400",
      character_references: "bg-cyan-100 text-cyan-700 dark:bg-cyan-900/30 dark:text-cyan-400",
    };
    return colors[category] || "bg-slate-100 text-slate-700 dark:bg-slate-900/30 dark:text-slate-400";
  };

  return (
    <>
      <Button
        onClick={() => setShowDialog(true)}
        variant="outline"
        className="rounded-xl"
        disabled={documents.length === 0}
        data-testid="bundle-docs-btn"
      >
        <FileStack className="w-4 h-4 mr-2" />
        Bundle Docs
      </Button>

      <Dialog open={showDialog} onOpenChange={setShowDialog}>
        <DialogContent className="max-w-2xl max-h-[90vh] overflow-hidden flex flex-col">
          <DialogHeader>
            <DialogTitle className="flex items-center gap-3" style={{ fontFamily: 'Crimson Pro, serif' }}>
              <div className="w-10 h-10 rounded-xl bg-blue-100 dark:bg-blue-900/30 flex items-center justify-center">
                <FileStack className="w-5 h-5 text-blue-600 dark:text-blue-400" />
              </div>
              Bundle Documents
            </DialogTitle>
          </DialogHeader>

          <div className="flex-1 overflow-y-auto py-4 space-y-4">
            {/* Bundle Options */}
            <div className="space-y-3">
              <div>
                <label className="text-sm font-medium text-foreground mb-1.5 block">Bundle Title</label>
                <Input
                  value={bundleTitle}
                  onChange={(e) => setBundleTitle(e.target.value)}
                  placeholder="Enter bundle title"
                  className="rounded-xl"
                />
              </div>
              
              <label className="flex items-center gap-3 p-3 bg-muted/50 rounded-xl cursor-pointer hover:bg-muted transition-colors">
                <Checkbox
                  checked={includeToc}
                  onCheckedChange={(checked) => setIncludeToc(checked)}
                  className="data-[state=checked]:bg-blue-600"
                />
                <div className="flex items-center gap-2">
                  <List className="w-4 h-4 text-muted-foreground" />
                  <span className="text-sm text-foreground">Include Table of Contents</span>
                </div>
              </label>
            </div>

            {/* Document Selection */}
            <div>
              <div className="flex items-center justify-between mb-3">
                <h4 className="text-sm font-semibold text-foreground">Select Documents</h4>
                <Button 
                  variant="ghost" 
                  size="sm" 
                  onClick={selectAll}
                  className="text-xs"
                >
                  {selectedDocs.length === documents.length ? "Deselect All" : "Select All"}
                </Button>
              </div>
              
              <div className="space-y-2 max-h-64 overflow-y-auto border border-border rounded-xl p-3">
                {documents.map((doc, index) => (
                  <label
                    key={doc.document_id}
                    className={`flex items-center gap-3 p-3 rounded-xl border cursor-pointer transition-all ${
                      selectedDocs.includes(doc.document_id)
                        ? "bg-blue-50 dark:bg-blue-900/20 border-blue-300 dark:border-blue-700"
                        : "bg-card border-border hover:bg-muted/50"
                    }`}
                  >
                    <Checkbox
                      checked={selectedDocs.includes(doc.document_id)}
                      onCheckedChange={() => toggleDocument(doc.document_id)}
                      className="data-[state=checked]:bg-blue-600"
                    />
                    <div className="flex items-center gap-2 flex-1 min-w-0">
                      <span className="w-6 h-6 rounded-lg bg-muted flex items-center justify-center text-xs font-medium text-muted-foreground">
                        {index + 1}
                      </span>
                      <div className="flex-1 min-w-0">
                        <p className="text-sm font-medium text-foreground truncate">
                          {doc.filename}
                        </p>
                        <Badge className={`text-xs mt-1 ${getCategoryColor(doc.category)}`}>
                          {doc.category?.replace(/_/g, ' ') || 'general'}
                        </Badge>
                      </div>
                    </div>
                    {selectedDocs.includes(doc.document_id) && (
                      <CheckCircle className="w-5 h-5 text-blue-600 flex-shrink-0" />
                    )}
                  </label>
                ))}
              </div>
              
              <p className="text-xs text-muted-foreground mt-2">
                {selectedDocs.length} of {documents.length} documents selected
              </p>
            </div>

            {/* Preview */}
            {selectedDocs.length > 0 && (
              <div className="p-4 bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-xl">
                <h4 className="text-sm font-semibold text-blue-800 dark:text-blue-200 mb-2">
                  Bundle Preview
                </h4>
                <ul className="text-xs text-blue-700 dark:text-blue-300 space-y-1">
                  <li>• Title page with case details</li>
                  {includeToc && <li>• Table of contents</li>}
                  <li>• {selectedDocs.length} document(s) with extracted text</li>
                  <li>• AI analysis notes (where available)</li>
                </ul>
              </div>
            )}
          </div>

          <DialogFooter className="gap-3 border-t border-border pt-4">
            <Button variant="outline" onClick={() => setShowDialog(false)}>
              Cancel
            </Button>
            <Button
              onClick={generateBundle}
              disabled={generating || selectedDocs.length === 0}
              className="bg-gradient-to-r from-blue-600 to-blue-700 text-white hover:from-blue-700 hover:to-blue-800"
            >
              {generating ? (
                <>
                  <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                  Generating...
                </>
              ) : (
                <>
                  <Download className="w-4 h-4 mr-2" />
                  Download PDF
                </>
              )}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </>
  );
};

export default DocumentBundler;
