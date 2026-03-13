/* DO NOT UNDO — ContradictionFinder component. All features in this file are approved and must be preserved. */
import { useState, useEffect } from "react";
import axios from "axios";
import { toast } from "sonner";
import { 
  Search, AlertTriangle, FileText, Clock, CheckCircle,
  Loader2, Sparkles, Eye, ChevronDown, ChevronUp, Trash2,
  AlertCircle, Info, RefreshCw
} from "lucide-react";
import { Button } from "./ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "./ui/card";
import { Badge } from "./ui/badge";
import { Checkbox } from "./ui/checkbox";
import {
  Collapsible,
  CollapsibleContent,
  CollapsibleTrigger,
} from "./ui/collapsible";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
} from "./ui/dialog";
import { API } from "../App";

const ContradictionFinder = ({ caseId, documents }) => {
  const [scanning, setScanning] = useState(false);
  const [scans, setScans] = useState([]);
  const [currentScan, setCurrentScan] = useState(null);
  const [selectedDocs, setSelectedDocs] = useState([]);
  const [focusAreas, setFocusAreas] = useState(["all"]);
  const [expandedContradiction, setExpandedContradiction] = useState(null);
  const [showScanDialog, setShowScanDialog] = useState(false);
  const [loadingScans, setLoadingScans] = useState(true);

  const focusAreaOptions = [
    { value: "all", label: "All Areas" },
    { value: "witness_statements", label: "Witness Statements" },
    { value: "timeline", label: "Timeline Inconsistencies" },
    { value: "evidence", label: "Evidence Conflicts" },
    { value: "testimony", label: "Testimony" },
    { value: "procedural", label: "Procedural Issues" }
  ];

  useEffect(() => {
    fetchScans();
  }, [caseId]);

  const fetchScans = async () => {
    setLoadingScans(true);
    try {
      const response = await axios.get(`${API}/cases/${caseId}/contradictions/scans`);
      setScans(response.data);
      if (response.data.length > 0) {
        setCurrentScan(response.data[0]);
      }
    } catch (error) {
      console.error("Failed to fetch scans:", error);
    } finally {
      setLoadingScans(false);
    }
  };

  const runScan = async () => {
    if (documents.length < 2) {
      toast.error("At least 2 documents are required for contradiction analysis");
      return;
    }

    setScanning(true);
    setShowScanDialog(false);
    
    try {
      const response = await axios.post(`${API}/cases/${caseId}/contradictions/scan`, {
        focus_areas: focusAreas.includes("all") ? null : focusAreas,
        document_ids: selectedDocs.length > 0 ? selectedDocs : null
      });
      
      setCurrentScan(response.data);
      setScans(prev => [response.data, ...prev]);
      
      const found = response.data.results?.contradictions?.length || 0;
      if (found > 0) {
        toast.success(`Found ${found} potential contradiction${found === 1 ? '' : 's'}`);
      } else {
        toast.info("No contradictions found in the analysed documents");
      }
    } catch (error) {
      toast.error(error.response?.data?.detail || "Failed to scan for contradictions");
    } finally {
      setScanning(false);
    }
  };

  const deleteScan = async (scanId) => {
    try {
      await axios.delete(`${API}/cases/${caseId}/contradictions/scans/${scanId}`);
      setScans(prev => prev.filter(s => s.scan_id !== scanId));
      if (currentScan?.scan_id === scanId) {
        setCurrentScan(scans.find(s => s.scan_id !== scanId) || null);
      }
      toast.success("Scan deleted");
    } catch (error) {
      toast.error("Failed to delete scan");
    }
  };

  const getSeverityColor = (severity) => {
    switch (severity) {
      case "critical":
        return "bg-red-500 text-white";
      case "significant":
        return "bg-amber-500 text-white";
      case "minor":
        return "bg-blue-500 text-white";
      default:
        return "bg-slate-500 text-white";
    }
  };

  const getSeverityBg = (severity) => {
    switch (severity) {
      case "critical":
        return "bg-red-50 dark:bg-red-900/20 border-red-200 dark:border-red-800";
      case "significant":
        return "bg-amber-50 dark:bg-amber-900/20 border-amber-200 dark:border-amber-800";
      case "minor":
        return "bg-blue-50 dark:bg-blue-900/20 border-blue-200 dark:border-blue-800";
      default:
        return "bg-slate-50 dark:bg-slate-900/20 border-slate-200 dark:border-slate-800";
    }
  };

  const getTypeIcon = (type) => {
    switch (type) {
      case "witness_statement":
        return <FileText className="w-4 h-4" />;
      case "timeline":
        return <Clock className="w-4 h-4" />;
      case "evidence":
        return <Search className="w-4 h-4" />;
      case "testimony":
        return <AlertCircle className="w-4 h-4" />;
      case "procedural":
        return <AlertTriangle className="w-4 h-4" />;
      default:
        return <Info className="w-4 h-4" />;
    }
  };

  const toggleDocSelection = (docId) => {
    setSelectedDocs(prev => 
      prev.includes(docId) 
        ? prev.filter(id => id !== docId)
        : [...prev, docId]
    );
  };

  const toggleFocusArea = (area) => {
    if (area === "all") {
      setFocusAreas(["all"]);
    } else {
      setFocusAreas(prev => {
        const newAreas = prev.filter(a => a !== "all");
        if (newAreas.includes(area)) {
          return newAreas.filter(a => a !== area);
        }
        return [...newAreas, area];
      });
    }
  };

  return (
    <div className="space-y-6">
      {/* Header Card */}
      <Card className="bg-gradient-to-r from-slate-900 to-indigo-950 border-0">
        <CardContent className="p-6">
          <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
            <div className="flex items-center gap-4">
              <div className="w-14 h-14 rounded-2xl bg-amber-500 flex items-center justify-center">
                <Search className="w-7 h-7 text-white" />
              </div>
              <div>
                <h2 className="text-xl font-bold text-white" style={{ fontFamily: 'Crimson Pro, serif' }}>
                  Contradiction Finder
                </h2>
                <p className="text-slate-400 text-sm">
                  AI-powered analysis to find inconsistencies across your case documents
                </p>
              </div>
            </div>
            <Button
              onClick={() => setShowScanDialog(true)}
              disabled={scanning || documents.length < 2}
              className="bg-amber-600 text-white hover:bg-amber-700 rounded-xl px-6 py-5 font-semibold"
              data-testid="scan-contradictions-btn"
            >
              {scanning ? (
                <>
                  <Loader2 className="w-5 h-5 mr-2 animate-spin" />
                  Scanning...
                </>
              ) : (
                <>
                  <Sparkles className="w-5 h-5 mr-2" />
                  New Scan
                </>
              )}
            </Button>
          </div>
        </CardContent>
      </Card>

      {/* Results */}
      {loadingScans ? (
        <div className="flex items-center justify-center py-12">
          <Loader2 className="w-8 h-8 animate-spin text-amber-600" />
        </div>
      ) : currentScan ? (
        <div className="space-y-6">
          {/* Scan Summary */}
          <div className="grid md:grid-cols-4 gap-4">
            <Card className="bg-card border-border">
              <CardContent className="p-4 text-center">
                <p className="text-3xl font-bold text-foreground">
                  {currentScan.results?.summary?.total_found || 0}
                </p>
                <p className="text-sm text-muted-foreground">Total Found</p>
              </CardContent>
            </Card>
            <Card className="bg-red-50 dark:bg-red-900/20 border-red-200 dark:border-red-800">
              <CardContent className="p-4 text-center">
                <p className="text-3xl font-bold text-red-700 dark:text-red-400">
                  {currentScan.results?.summary?.critical_count || 0}
                </p>
                <p className="text-sm text-red-600 dark:text-red-400">Critical</p>
              </CardContent>
            </Card>
            <Card className="bg-amber-50 dark:bg-amber-900/20 border-amber-200 dark:border-amber-800">
              <CardContent className="p-4 text-center">
                <p className="text-3xl font-bold text-amber-700 dark:text-amber-400">
                  {currentScan.results?.summary?.significant_count || 0}
                </p>
                <p className="text-sm text-amber-600 dark:text-amber-400">Significant</p>
              </CardContent>
            </Card>
            <Card className="bg-blue-50 dark:bg-blue-900/20 border-blue-200 dark:border-blue-800">
              <CardContent className="p-4 text-center">
                <p className="text-3xl font-bold text-blue-700 dark:text-blue-400">
                  {currentScan.results?.summary?.minor_count || 0}
                </p>
                <p className="text-sm text-blue-600 dark:text-blue-400">Minor</p>
              </CardContent>
            </Card>
          </div>

          {/* Key Finding */}
          {currentScan.results?.summary?.key_finding && (
            <Card className="bg-card border-border">
              <CardContent className="p-5">
                <div className="flex items-start gap-3">
                  <AlertTriangle className="w-5 h-5 text-amber-600 mt-0.5 flex-shrink-0" />
                  <div>
                    <h3 className="font-semibold text-foreground mb-1">Key Finding</h3>
                    <p className="text-muted-foreground">
                      {currentScan.results.summary.key_finding}
                    </p>
                  </div>
                </div>
              </CardContent>
            </Card>
          )}

          {/* Contradictions List */}
          {currentScan.results?.contradictions?.length > 0 ? (
            <div className="space-y-4">
              <h3 className="text-lg font-semibold text-foreground" style={{ fontFamily: 'Crimson Pro, serif' }}>
                Identified Contradictions
              </h3>
              {currentScan.results.contradictions.map((contradiction, index) => (
                <Collapsible
                  key={contradiction.id || index}
                  open={expandedContradiction === index}
                  onOpenChange={() => setExpandedContradiction(expandedContradiction === index ? null : index)}
                >
                  <Card className={`border ${getSeverityBg(contradiction.severity)}`}>
                    <CollapsibleTrigger className="w-full">
                      <CardContent className="p-5">
                        <div className="flex items-start justify-between gap-4">
                          <div className="flex items-start gap-3">
                            <div className={`p-2 rounded-lg ${getSeverityColor(contradiction.severity)}`}>
                              {getTypeIcon(contradiction.type)}
                            </div>
                            <div className="text-left">
                              <div className="flex items-center gap-2 mb-1">
                                <Badge className={getSeverityColor(contradiction.severity)}>
                                  {contradiction.severity}
                                </Badge>
                                <Badge variant="outline" className="capitalize">
                                  {contradiction.type?.replace(/_/g, ' ')}
                                </Badge>
                              </div>
                              <p className="font-medium text-foreground">
                                {contradiction.description}
                              </p>
                            </div>
                          </div>
                          {expandedContradiction === index ? (
                            <ChevronUp className="w-5 h-5 text-muted-foreground flex-shrink-0" />
                          ) : (
                            <ChevronDown className="w-5 h-5 text-muted-foreground flex-shrink-0" />
                          )}
                        </div>
                      </CardContent>
                    </CollapsibleTrigger>
                    <CollapsibleContent>
                      <div className="px-5 pb-5 space-y-4 border-t border-border/50 pt-4">
                        {/* Analysis */}
                        <div>
                          <h4 className="text-sm font-semibold text-foreground mb-2 flex items-center gap-2">
                            <Info className="w-4 h-4" />
                            Analysis
                          </h4>
                          <p className="text-sm text-muted-foreground bg-muted/50 p-3 rounded-lg">
                            {contradiction.analysis}
                          </p>
                        </div>

                        {/* Specific Quotes */}
                        {contradiction.specific_quotes?.length > 0 && (
                          <div>
                            <h4 className="text-sm font-semibold text-foreground mb-2 flex items-center gap-2">
                              <FileText className="w-4 h-4" />
                              Source Quotes
                            </h4>
                            <div className="space-y-2">
                              {contradiction.specific_quotes.map((quote, qi) => (
                                <div key={qi} className="bg-muted/50 p-3 rounded-lg border-l-4 border-amber-500">
                                  <p className="text-sm text-foreground italic">"{quote.quote}"</p>
                                  <p className="text-xs text-muted-foreground mt-1">
                                    {quote.context || quote.doc_id}
                                  </p>
                                </div>
                              ))}
                            </div>
                          </div>
                        )}

                        {/* Recommendations */}
                        {contradiction.recommendations?.length > 0 && (
                          <div>
                            <h4 className="text-sm font-semibold text-foreground mb-2 flex items-center gap-2">
                              <CheckCircle className="w-4 h-4" />
                              Recommendations
                            </h4>
                            <ul className="space-y-1">
                              {contradiction.recommendations.map((rec, ri) => (
                                <li key={ri} className="text-sm text-muted-foreground flex items-start gap-2">
                                  <span className="text-amber-600">•</span>
                                  {rec}
                                </li>
                              ))}
                            </ul>
                          </div>
                        )}
                      </div>
                    </CollapsibleContent>
                  </Card>
                </Collapsible>
              ))}
            </div>
          ) : (
            <Card className="bg-emerald-50 dark:bg-emerald-900/20 border-emerald-200 dark:border-emerald-800">
              <CardContent className="p-6 text-center">
                <CheckCircle className="w-12 h-12 text-emerald-600 dark:text-emerald-400 mx-auto mb-3" />
                <h3 className="font-semibold text-emerald-800 dark:text-emerald-200 mb-2">
                  No Contradictions Found
                </h3>
                <p className="text-sm text-emerald-700 dark:text-emerald-300">
                  The analysed documents appear to be internally consistent.
                </p>
              </CardContent>
            </Card>
          )}

          {/* Recommended Actions */}
          {currentScan.results?.recommended_actions?.length > 0 && (
            <Card className="bg-card border-border">
              <CardHeader>
                <CardTitle className="text-lg" style={{ fontFamily: 'Crimson Pro, serif' }}>
                  Recommended Next Steps
                </CardTitle>
              </CardHeader>
              <CardContent>
                <ul className="space-y-2">
                  {currentScan.results.recommended_actions.map((action, i) => (
                    <li key={i} className="flex items-start gap-3 text-muted-foreground">
                      <span className="w-6 h-6 rounded-full bg-amber-100 dark:bg-amber-900/30 flex items-center justify-center text-amber-600 text-sm font-semibold flex-shrink-0">
                        {i + 1}
                      </span>
                      {action}
                    </li>
                  ))}
                </ul>
              </CardContent>
            </Card>
          )}

          {/* Scan History */}
          {scans.length > 1 && (
            <Card className="bg-card border-border">
              <CardHeader>
                <CardTitle className="text-lg flex items-center justify-between" style={{ fontFamily: 'Crimson Pro, serif' }}>
                  Previous Scans
                  <Badge variant="outline">{scans.length} scans</Badge>
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-2">
                  {scans.map((scan) => (
                    <div 
                      key={scan.scan_id}
                      className={`flex items-center justify-between p-3 rounded-xl border cursor-pointer transition-colors ${
                        currentScan?.scan_id === scan.scan_id 
                          ? "bg-amber-50 dark:bg-amber-900/20 border-amber-300 dark:border-amber-700" 
                          : "bg-muted/50 border-border hover:bg-muted"
                      }`}
                      onClick={() => setCurrentScan(scan)}
                    >
                      <div className="flex items-center gap-3">
                        <Search className="w-4 h-4 text-muted-foreground" />
                        <div>
                          <p className="text-sm font-medium text-foreground">
                            {new Date(scan.scanned_at).toLocaleString()}
                          </p>
                          <p className="text-xs text-muted-foreground">
                            {scan.documents_analyzed} docs • {scan.results?.summary?.total_found || 0} findings
                          </p>
                        </div>
                      </div>
                      <div className="flex items-center gap-2">
                        {currentScan?.scan_id === scan.scan_id && (
                          <Badge className="bg-amber-600 text-white">Active</Badge>
                        )}
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={(e) => {
                            e.stopPropagation();
                            deleteScan(scan.scan_id);
                          }}
                          className="text-muted-foreground hover:text-red-600"
                        >
                          <Trash2 className="w-4 h-4" />
                        </Button>
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          )}
        </div>
      ) : (
        <Card className="bg-card border-border">
          <CardContent className="p-12 text-center">
            <Search className="w-16 h-16 text-muted-foreground/30 mx-auto mb-4" />
            <h3 className="text-lg font-semibold text-foreground mb-2" style={{ fontFamily: 'Crimson Pro, serif' }}>
              No Scans Yet
            </h3>
            <p className="text-muted-foreground mb-6 max-w-md mx-auto">
              Upload at least 2 documents and run a scan to find potential contradictions 
              and inconsistencies in your case materials.
            </p>
            {documents.length < 2 ? (
              <p className="text-sm text-amber-600 dark:text-amber-400">
                You need at least 2 documents to run a contradiction scan.
              </p>
            ) : (
              <Button
                onClick={() => setShowScanDialog(true)}
                className="bg-gradient-to-r from-amber-600 to-amber-700 text-white hover:from-amber-700 hover:to-amber-800 rounded-xl px-8 py-5 font-semibold"
              >
                <Sparkles className="w-5 h-5 mr-2" />
                Run First Scan
              </Button>
            )}
          </CardContent>
        </Card>
      )}

      {/* Scan Configuration Dialog */}
      <Dialog open={showScanDialog} onOpenChange={setShowScanDialog}>
        <DialogContent className="max-w-lg">
          <DialogHeader>
            <DialogTitle style={{ fontFamily: 'Crimson Pro, serif' }}>
              Configure Contradiction Scan
            </DialogTitle>
          </DialogHeader>
          
          <div className="space-y-6 py-4">
            {/* Focus Areas */}
            <div>
              <h4 className="text-sm font-semibold text-foreground mb-3">Focus Areas</h4>
              <div className="flex flex-wrap gap-2">
                {focusAreaOptions.map((area) => (
                  <Badge
                    key={area.value}
                    variant={focusAreas.includes(area.value) ? "default" : "outline"}
                    className={`cursor-pointer transition-colors ${
                      focusAreas.includes(area.value) 
                        ? "bg-amber-600 text-white hover:bg-amber-700" 
                        : "hover:bg-muted"
                    }`}
                    onClick={() => toggleFocusArea(area.value)}
                  >
                    {area.label}
                  </Badge>
                ))}
              </div>
            </div>

            {/* Document Selection */}
            <div>
              <h4 className="text-sm font-semibold text-foreground mb-3">
                Select Documents 
                <span className="text-muted-foreground font-normal ml-2">
                  (leave empty to scan all)
                </span>
              </h4>
              <div className="max-h-48 overflow-y-auto space-y-2 border border-border rounded-xl p-3">
                {documents.map((doc) => (
                  <label
                    key={doc.document_id}
                    className="flex items-center gap-3 p-2 rounded-lg hover:bg-muted cursor-pointer"
                  >
                    <Checkbox
                      checked={selectedDocs.includes(doc.document_id)}
                      onCheckedChange={() => toggleDocSelection(doc.document_id)}
                    />
                    <div className="flex-1 min-w-0">
                      <p className="text-sm font-medium text-foreground truncate">
                        {doc.filename}
                      </p>
                      <p className="text-xs text-muted-foreground capitalize">
                        {doc.category?.replace(/_/g, ' ')}
                      </p>
                    </div>
                  </label>
                ))}
              </div>
            </div>
          </div>

          <div className="flex gap-3">
            <Button variant="outline" onClick={() => setShowScanDialog(false)} className="flex-1">
              Cancel
            </Button>
            <Button
              onClick={runScan}
              disabled={scanning}
              className="flex-1 bg-gradient-to-r from-amber-600 to-amber-700 text-white hover:from-amber-700 hover:to-amber-800"
            >
              {scanning ? (
                <>
                  <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                  Scanning...
                </>
              ) : (
                <>
                  <Sparkles className="w-4 h-4 mr-2" />
                  Start Scan
                </>
              )}
            </Button>
          </div>
        </DialogContent>
      </Dialog>
    </div>
  );
};

export default ContradictionFinder;
