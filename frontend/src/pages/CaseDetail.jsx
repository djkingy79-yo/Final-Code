/* DO NOT UNDO — CaseDetail section. All features in this file are approved and must be preserved. */
import { useState, useEffect } from "react";
import { useParams, useNavigate } from "react-router-dom";
import axios from "axios";
import { toast } from "sonner";
import { 
  Scale, ArrowLeft, FileText, Clock, Plus,
  Loader2, AlertCircle, Sparkles, Gavel,
  BookOpen, HelpCircle, TrendingUp,
  MessageSquare
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
import { Badge } from "../components/ui/badge";
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
import QuickExport from "../components/QuickExport";
import DocumentBundler from "../components/DocumentBundler";

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
  const navigate = useNavigate();
  const [caseData, setCaseData] = useState(null);
  const [documents, setDocuments] = useState([]);
  const [timeline, setTimeline] = useState([]);
  const [reports, setReports] = useState([]);
  const [notes, setNotes] = useState([]);
  const [grounds, setGrounds] = useState([]);
  const [groundsCount, setGroundsCount] = useState(0);
  const [groundsUnlocked, setGroundsUnlocked] = useState(false);
  const [groundsUnlockPrice, setGroundsUnlockPrice] = useState(99.00);
  const [loading, setLoading] = useState(true);
  const [loadError, setLoadError] = useState(null);
  const [activeTab, setActiveTab] = useState("documents");

  // Dialog states
  const [showEventDialog, setShowEventDialog] = useState(false);
  const [showGroundDialog, setShowGroundDialog] = useState(false);
  const [investigatingGround, setInvestigatingGround] = useState(null);
  const [autoIdentifying, setAutoIdentifying] = useState(false);
  const [selectedGround, setSelectedGround] = useState(null);
  const [generatingTimeline, setGeneratingTimeline] = useState(false);
  const [analyzingTimeline, setAnalyzingTimeline] = useState(false);
  const [timelineAnalysis, setTimelineAnalysis] = useState(null);

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
    fetchCaseData();
    
    // Handle payment return (for future PayPal integration)
    const params = new URLSearchParams(window.location.search);
    const paymentStatus = params.get('payment');
    
    if (paymentStatus === 'success') {
      toast.success('Payment successful! Feature unlocked.');
      window.history.replaceState({}, '', `/cases/${caseId}`);
    } else if (paymentStatus === 'cancelled') {
      toast.info('Payment was cancelled.');
      window.history.replaceState({}, '', `/cases/${caseId}`);
    }
  }, [caseId]);

  const fetchCaseData = async () => {
    setLoadError(null);
    setLoading(true);
    try {
      // Fetch case data first to verify access
      const caseRes = await axios.get(`${API}/cases/${caseId}`);
      setCaseData(caseRes.data);
      
      // Then fetch related data - use Promise.allSettled for resilience
      const [docsRes, timelineRes, reportsRes, notesRes, groundsRes] = await Promise.allSettled([
        axios.get(`${API}/cases/${caseId}/documents`),
        axios.get(`${API}/cases/${caseId}/timeline`),
        axios.get(`${API}/cases/${caseId}/reports`),
        axios.get(`${API}/cases/${caseId}/notes`),
        axios.get(`${API}/cases/${caseId}/grounds`)
      ]);
      
      // Set data from successful responses, empty arrays for failed ones
      setDocuments(docsRes.status === 'fulfilled' ? docsRes.value.data : []);
      setTimeline(timelineRes.status === 'fulfilled' ? timelineRes.value.data : []);
      setReports(reportsRes.status === 'fulfilled' ? reportsRes.value.data : []);
      setNotes(notesRes.status === 'fulfilled' ? notesRes.value.data : []);
      
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
    if (!window.confirm("Delete this event?")) return;
    
    try {
      await axios.delete(`${API}/cases/${caseId}/timeline/${eventId}`);
      setTimeline(timeline.filter(e => e.event_id !== eventId));
      toast.success("Event deleted");
    } catch (error) {
      toast.error("Failed to delete event");
    }
  };

  const handleGenerateTimeline = async () => {
    if (documents.filter(d => d.content_text).length === 0) {
      toast.error("No documents with extracted text. Please upload documents and extract text first.");
      return;
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

  const handleAnalyzeTimeline = async () => {
    if (timeline.length < 2) {
      toast.error("Need at least 2 timeline events for analysis");
      return;
    }
    
    setAnalyzingTimeline(true);
    toast.info("Analysing timeline for gaps, inconsistencies, and insights...");
    
    try {
      const response = await axios.post(`${API}/cases/${caseId}/timeline/analyze`, {}, {
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
    toast.info("Investigating this ground with speed optimisation. Large matters can still take up to 2-3 minutes.");
    try {
      const response = await axios.post(`${API}/cases/${caseId}/grounds/${groundId}/investigate`, {}, {
        timeout: 180000 // 3 minute timeout for complex AI analysis
      });
      setGrounds(grounds.map(g => g.ground_id === groundId ? response.data : g));
      toast.success("Deep investigation complete!");
    } catch (error) {
      console.error("Investigate error:", error);
      if (error.code === 'ECONNABORTED' || error.message?.includes('timeout')) {
        toast.error("Investigation timed out. Please retry — the system now prioritises key evidence for faster results.");
      } else {
        toast.error("Failed to investigate ground. Please try again.");
      }
    } finally {
      setInvestigatingGround(null);
    }
  };

  const handleDeleteGround = async (groundId) => {
    if (!window.confirm("Delete this ground of merit?")) return;
    
    try {
      await axios.delete(`${API}/cases/${caseId}/grounds/${groundId}`);
      setGrounds(grounds.filter(g => g.ground_id !== groundId));
      toast.success("Ground of merit deleted");
    } catch (error) {
      toast.error("Failed to delete ground");
    }
  };

  const handleAutoIdentifyGrounds = async () => {
    setAutoIdentifying(true);
    toast.info("Analysing grounds with an optimised evidence window for faster response.");
    try {
      const response = await axios.post(`${API}/cases/${caseId}/grounds/auto-identify`, {}, {
        timeout: 180000 // 3 minute timeout for AI analysis
      });
      
      const { identified_count, skipped_duplicates, existing_grounds, unlock_required, unlock_price } = response.data;
      
      if (identified_count > 0) {
        // Refresh grounds list to get updated data with proper paywall state
        const groundsRes = await axios.get(`${API}/cases/${caseId}/grounds`);
        setGrounds(groundsRes.data.grounds || []);
        setGroundsCount(groundsRes.data.count || 0);
        setGroundsUnlocked(groundsRes.data.is_unlocked || false);
        setGroundsUnlockPrice(groundsRes.data.unlock_price || 50.00);
        
        // Show appropriate message
        if (skipped_duplicates > 0) {
          toast.success(`Found ${identified_count} new ground(s)! ${skipped_duplicates} duplicate(s) skipped. Pay $${unlock_price?.toFixed(2)} to see full details.`);
        } else {
          toast.success(`Identified ${identified_count} potential ground(s)! Pay $${unlock_price?.toFixed(2)} to unlock full details.`);
        }
      } else {
        // No new grounds found
        if (existing_grounds > 0) {
          toast.info("All significant grounds have already been identified for this case.");
        } else {
          toast.info("No grounds identified. Try adding more case documents with detailed content.");
        }
      }
    } catch (error) {
      console.error("Auto-identify error:", error);
      if (error.code === 'ECONNABORTED' || error.message?.includes('timeout')) {
        toast.error("Ground analysis timed out. Please retry — long files are now processed in a faster, prioritised mode.");
      } else {
        toast.error("Failed to auto-identify grounds. Please try again.");
      }
    } finally {
      setAutoIdentifying(false);
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

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-background">
        <div className="text-center">
          <Loader2 className="w-12 h-12 animate-spin text-muted-foreground mx-auto" />
          <p className="mt-4 text-muted-foreground">Loading case...</p>
        </div>
      </div>
    );
  }

  if (loadError) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-background">
        <div className="text-center max-w-md">
          <AlertCircle className="w-12 h-12 text-red-500 mx-auto" />
          <h2 className="mt-4 text-xl font-semibold text-foreground">Error Loading Case</h2>
          <p className="mt-2 text-muted-foreground">{loadError}</p>
          <div className="mt-6 flex gap-3 justify-center">
            <Button 
              variant="outline" 
              onClick={() => navigate("/dashboard")}
              className="rounded-xl"
              data-testid="back-to-dashboard-btn"
            >
              <ArrowLeft className="w-4 h-4 mr-2" />
              Back to Dashboard
            </Button>
            <Button 
              onClick={fetchCaseData}
              className="rounded-xl"
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
    <div className="min-h-screen bg-background">
      {/* Header */}
      <header className="glass-header sticky top-0 z-40">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 py-3 sm:py-4">
          <div className="flex items-center gap-2 sm:gap-4">
            <Button 
              variant="ghost" 
              size="sm" 
              onClick={() => navigate("/dashboard")}
              className="rounded-xl shrink-0"
              data-testid="back-btn"
            >
              <ArrowLeft className="w-4 h-4 mr-1" />
              <span className="hidden sm:inline">Back</span>
            </Button>
            <div className="flex items-center gap-2 flex-1 min-w-0">
              <div className="w-8 h-8 rounded-lg gradient-blue flex items-center justify-center shrink-0">
                <Scale className="w-4 h-4 text-white" />
              </div>
              <span className="text-muted-foreground hidden sm:inline">/</span>
              <span className="font-medium text-foreground truncate text-sm sm:text-base">{caseData?.title}</span>
            </div>
            <div className="hidden sm:flex items-center gap-2">
              <Button 
                variant="ghost" 
                size="sm" 
                onClick={() => navigate("/help")}
                className="text-muted-foreground hover:text-foreground rounded-xl"
                data-testid="help-btn"
              >
                <HelpCircle className="w-4 h-4 mr-1" />
                Help
              </Button>
              <QuickExport caseId={caseId} caseTitle={caseData?.title} />
              <DocumentBundler caseId={caseId} documents={documents} />
            </div>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 sm:px-6 py-6 sm:py-8">
        {/* Case Info */}
        <div className="mb-8">
          <h1 
            className="text-3xl md:text-4xl font-bold text-foreground tracking-tight"
            style={{ fontFamily: 'Crimson Pro, serif' }}
            data-testid="case-title"
          >
            {caseData?.title}
          </h1>
          <div className="flex flex-wrap items-center gap-4 mt-3 text-muted-foreground">
            <span className="font-medium text-foreground">{caseData?.defendant_name}</span>
            {caseData?.case_number && (
              <span className="font-mono text-sm bg-muted px-2 py-1 rounded-lg">
                {caseData.case_number}
              </span>
            )}
            {caseData?.court && <span>{caseData.court}</span>}
          </div>
          {/* Offence Type Display */}
          {caseData?.offence_category && (
            <div className="flex flex-wrap items-center gap-2 mt-3">
              {caseData?.state && (
                <Badge variant="outline" className="bg-blue-100 dark:bg-blue-900/30 text-blue-700 dark:text-blue-400 border-blue-200 dark:border-blue-800 uppercase rounded-lg">
                  {caseData.state}
                </Badge>
              )}
              <Badge variant="outline" className="bg-blue-100 dark:bg-blue-900/30 text-blue-700 dark:text-blue-400 border-blue-200 dark:border-blue-800 capitalize rounded-lg">
                {caseData.offence_category.replace(/_/g, ' ')}
              </Badge>
              {caseData?.offence_type && (
                <Badge variant="outline" className="bg-muted text-muted-foreground border-border rounded-lg">
                  {caseData.offence_type}
                </Badge>
              )}
            </div>
          )}
          {caseData?.summary && (
            <p className="mt-4 text-muted-foreground max-w-3xl">{caseData.summary}</p>
          )}
        </div>

        {/* Tabs */}
        <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-6">
          <div className="flex flex-col gap-4">
            <div className="overflow-x-auto -mx-4 px-4 sm:mx-0 sm:px-0">
              <TabsList className="bg-muted rounded-xl p-1 inline-flex min-w-max">
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
                  Grounds ({grounds.length})
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
                <TabsTrigger value="progress" className="rounded-lg text-xs sm:text-sm px-2 sm:px-3" data-testid="tab-progress">
                  <TrendingUp className="w-3.5 h-3.5 sm:w-4 sm:h-4 mr-1 sm:mr-2" />
                  Progress
                </TabsTrigger>
              </TabsList>
            </div>

            <div className="flex gap-2">
              {activeTab === "timeline" && (
                <>
                  <Button 
                    onClick={handleGenerateTimeline}
                    disabled={generatingTimeline}
                    variant="outline"
                    className="bg-purple-50 dark:bg-purple-900/20 border-purple-200 dark:border-purple-800 text-purple-700 dark:text-purple-400 hover:bg-purple-100 dark:hover:bg-purple-900/40 rounded-xl"
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
                    className="bg-primary text-primary-foreground hover:bg-primary/90 rounded-xl"
                    data-testid="add-event-btn"
                  >
                    <Plus className="w-4 h-4 mr-2" />
                    Add Event
                  </Button>
                </>
              )}
              {activeTab === "grounds" && (
                <>
                  <Button 
                    onClick={handleAutoIdentifyGrounds}
                    disabled={autoIdentifying}
                    className="bg-red-600 text-white hover:bg-blue-700 rounded-xl"
                    data-testid="auto-identify-btn"
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
                    className="bg-primary text-primary-foreground hover:bg-primary/90 rounded-xl"
                    data-testid="add-ground-btn"
                  >
                    <Plus className="w-4 h-4 mr-2" />
                    Add Ground
                  </Button>
                </>
              )}
            </div>
          </div>

          {/* Documents Tab */}
          <TabsContent value="documents" className="space-y-4">
            <DocumentsSection
              caseId={caseId}
              documents={documents}
              setDocuments={setDocuments}
              onDocumentsChange={fetchCaseData}
            />
          </TabsContent>

          {/* Timeline Tab */}
          <TabsContent value="timeline" className="space-y-4">
            {timeline.length === 0 ? (
              <Card className="p-12 text-center card-elevated">
                <Clock className="w-12 h-12 text-muted-foreground mx-auto mb-4" />
                <h3 className="text-lg font-semibold text-foreground mb-2" style={{ fontFamily: 'Crimson Pro, serif' }}>
                  No events yet
                </h3>
                <p className="text-muted-foreground mb-4">Build a chronological timeline of case events.</p>
                <Button 
                  onClick={() => setShowEventDialog(true)}
                  className="bg-primary text-primary-foreground hover:bg-primary/90 rounded-xl"
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
                  onDeleteEvent={handleDeleteEvent}
                  onExportPDF={handleExportTimelinePDF}
                  onAnalyze={handleAnalyzeTimeline}
                  analyzing={analyzingTimeline}
                />
              </div>
            )}
          </TabsContent>

          {/* Grounds of Merit Tab */}
          <TabsContent value="grounds" className="space-y-4">
            {grounds.length === 0 ? (
              <Card className="p-12 text-center card-elevated">
                <Gavel className="w-12 h-12 text-muted-foreground mx-auto mb-4" />
                <h3 className="text-lg font-semibold text-foreground mb-2" style={{ fontFamily: 'Crimson Pro, serif' }}>
                  No grounds of merit identified
                </h3>
                <p className="text-muted-foreground mb-4 max-w-md mx-auto">
                  Use AI to automatically analyse your case materials and identify potential grounds for appeal, 
                  or add grounds manually.
                </p>
                <div className="flex gap-3 justify-center">
                  <Button 
                    onClick={handleAutoIdentifyGrounds}
                    disabled={autoIdentifying}
                    className="bg-red-600 text-white hover:bg-blue-700 rounded-xl"
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
                    variant="outline"
                    className="rounded-xl"
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
                onInvestigate={handleInvestigateGround}
                onDelete={handleDeleteGround}
                investigating={investigatingGround}
                selectedGround={selectedGround}
                setSelectedGround={setSelectedGround}
                onPaymentSuccess={() => fetchCaseData()}
              />
            )}
          </TabsContent>

          {/* Notes Tab */}
          {/* Notes Tab */}
          <TabsContent value="notes" className="space-y-4">
            <NotesSection
              caseId={caseId}
              notes={notes}
              setNotes={setNotes}
              onNotesChange={fetchCaseData}
            />
          </TabsContent>

          {/* Reports Tab */}
          <TabsContent value="reports" className="space-y-4">
            <ReportsSection
              caseId={caseId}
              reports={reports}
              setReports={setReports}
              onReportsChange={fetchCaseData}
              documents={documents}
              navigate={navigate}
              isAdmin={user?.is_admin}
            />
          </TabsContent>

          {/* Legal Framework Tab — DO NOT UNDO */}
          <TabsContent value="legal" className="space-y-6">
            <LegalFrameworkViewer 
              offenceCategory={caseData?.offence_category}
              offenceType={caseData?.offence_type}
              state={caseData?.state}
            />
          </TabsContent>

          {/* Progress Tab — DO NOT UNDO, DO NOT DELETE */}
          <TabsContent value="progress" className="space-y-6">
            {/* Deadline Tracker */}
            <DeadlineTracker caseId={caseId} />
            
            {/* Appeal Checklist */}
            <AppealChecklist caseId={caseId} />
            
            {/* Quick Links */}
            <Card>
              <CardContent className="p-4">
                <div className="flex flex-wrap gap-3">
                  <Button 
                    variant="outline" 
                    onClick={() => navigate('/resources')}
                    className="flex items-center gap-2"
                  >
                    <HelpCircle className="w-4 h-4" />
                    Resource Directory
                  </Button>
                  <Button 
                    variant="outline" 
                    onClick={() => navigate('/help')}
                    className="flex items-center gap-2"
                  >
                    <HelpCircle className="w-4 h-4" />
                    Help & Glossary
                  </Button>
                </div>
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>
      </main>

      {/* Add Event Dialog */}
      <Dialog open={showEventDialog} onOpenChange={setShowEventDialog}>
        <DialogContent className="max-w-2xl max-h-[90vh] overflow-y-auto">
          <DialogHeader>
            <DialogTitle style={{ fontFamily: 'Crimson Pro, serif' }} className="text-2xl">
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
            <Button variant="outline" onClick={() => setShowEventDialog(false)}>
              Cancel
            </Button>
            <Button 
              onClick={handleCreateEvent}
              className="bg-slate-900 text-white hover:bg-slate-800"
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
            <DialogTitle style={{ fontFamily: 'Crimson Pro, serif' }} className="text-2xl">
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
            <Button variant="outline" onClick={() => setShowGroundDialog(false)}>
              Cancel
            </Button>
            <Button 
              onClick={handleCreateGround}
              className="bg-slate-900 text-white hover:bg-slate-800"
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
    </div>
  );
};

export default CaseDetail;
