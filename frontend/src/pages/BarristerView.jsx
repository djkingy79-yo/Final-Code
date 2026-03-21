/* ========================================================================
   DO NOT UNDO — ENTIRE FILE PROTECTED
   All features, functions, styles, and content in this file are approved
   and must be preserved. Do not remove, rename, or refactor any code.
   ======================================================================== */
import { useState, useEffect } from "react";
import { useParams, useNavigate } from "react-router-dom";
import axios from "axios";
import { toast } from "sonner";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import { 
  Scale, ArrowLeft, Download, Printer, Loader2, Share2, Maximize2,
  BookOpen, Gavel, FileText, CheckCircle, AlertTriangle, XCircle,
  Calendar, User, MapPin, Building2, Clock, Target, Shield, Sword,
  ChevronRight, ExternalLink, Quote, BarChart3, Bookmark
} from "lucide-react";
import { Button } from "../components/ui/button";
import { Badge } from "../components/ui/badge";
import { API } from "../App";

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

const STRENGTH_CONFIG = {
  strong: { icon: CheckCircle, color: "text-emerald-700", bg: "bg-emerald-50", border: "border-emerald-200", label: "Strong Ground", score: "HIGH" },
  moderate: { icon: AlertTriangle, color: "text-blue-700", bg: "bg-blue-50", border: "border-blue-200", label: "Moderate Ground", score: "MEDIUM" },
  weak: { icon: XCircle, color: "text-red-700", bg: "bg-red-50", border: "border-red-200", label: "Requires Development", score: "LOW" }
};

const BarristerView = ({ user }) => {
  const { caseId, reportId } = useParams();
  const navigate = useNavigate();
  const [report, setReport] = useState(null);
  const [allReports, setAllReports] = useState([]);
  const [caseData, setCaseData] = useState(null);
  const [grounds, setGrounds] = useState([]);
  const [timeline, setTimeline] = useState([]);
  const [documents, setDocuments] = useState([]);
  const [loading, setLoading] = useState(true);
  const [isFullscreen, setIsFullscreen] = useState(false);

  useEffect(() => {
    fetchData();
  }, [caseId, reportId]);

  const fetchData = async () => {
    try {
      const [reportRes, caseRes, groundsRes, timelineRes, docsRes, allReportsRes] = await Promise.all([
        axios.get(`${API}/cases/${caseId}/reports/${reportId}`),
        axios.get(`${API}/cases/${caseId}`),
        axios.get(`${API}/cases/${caseId}/grounds`),
        axios.get(`${API}/cases/${caseId}/timeline`),
        axios.get(`${API}/cases/${caseId}/documents`),
        axios.get(`${API}/cases/${caseId}/reports`).catch(() => ({ data: [] }))
      ]);
      const primary = reportRes.data;
      setReport(primary);
      setCaseData(caseRes.data);
      setGrounds(groundsRes.data?.grounds || []);
      setTimeline(timelineRes.data || []);
      setDocuments(docsRes.data || []);
      // Collect all completed reports sorted by detail level (extensive > full > quick)
      const typeOrder = { extensive_log: 3, full_detailed: 2, quick_summary: 1 };
      const completed = (allReportsRes.data || [])
        .filter(r => r.status === "completed" && r.content?.analysis)
        .sort((a, b) => (typeOrder[b.report_type] || 0) - (typeOrder[a.report_type] || 0));
      setAllReports(completed);
    } catch (error) {
      toast.error("Failed to load report");
      navigate(`/cases/${caseId}`);
    } finally {
      setLoading(false);
    }
  };

  const handlePrint = () => {
    const isIOS = /iPad|iPhone|iPod/.test(navigator.userAgent);
    if (isIOS) {
      // iOS Safari: window.print() is unreliable. Open PDF in new tab instead.
      const a = document.createElement('a');
      a.href = `${API}/cases/${caseId}/reports/${reportId}/export-pdf`;
      a.target = '_blank';
      a.rel = 'noopener';
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      toast.success("PDF opening — use Share to print.");
      return;
    }
    window.print();
  };

  const toggleFullscreen = () => {
    if (!document.fullscreenElement) {
      document.documentElement.requestFullscreen();
      setIsFullscreen(true);
    } else {
      document.exitFullscreen();
      setIsFullscreen(false);
    }
  };

  const handleExportPDF = async () => {
    try {
      toast.info("Generating PDF...");
      const isIOS = /iPad|iPhone|iPod/.test(navigator.userAgent);
      if (isIOS) {
        // iOS: use anchor tag to API URL — Content-Disposition triggers download
        const a = document.createElement('a');
        a.href = `${API}/cases/${caseId}/reports/${reportId}/export-pdf`;
        a.target = '_blank';
        a.rel = 'noopener';
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        toast.success("PDF opening — use Share to save or print.");
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
      link.setAttribute('download', `${caseData?.title || 'Report'}_barrister_brief.pdf`);
      document.body.appendChild(link);
      link.click();
      link.remove();
      setTimeout(() => window.URL.revokeObjectURL(url), 5000);
      toast.success("PDF downloaded successfully!");
    } catch (error) {
      toast.error("Failed to export PDF.");
    }
  };

  const handleExportDOCX = async () => {
    try {
      toast.info("Generating Word document...");
      const isIOS = /iPad|iPhone|iPod/.test(navigator.userAgent);
      if (isIOS) {
        const a = document.createElement('a');
        a.href = `${API}/cases/${caseId}/reports/${reportId}/export-docx`;
        a.target = '_blank';
        a.rel = 'noopener';
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        toast.success("Word document opening — use Share to save.");
        return;
      }
      const response = await axios.get(
        `${API}/cases/${caseId}/reports/${reportId}/export-docx`,
        { responseType: 'blob' }
      );
      
      const blob = new Blob([response.data], { type: 'application/vnd.openxmlformats-officedocument.wordprocessingml.document' });
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `${caseData?.title || 'Report'}_barrister_brief.docx`);
      document.body.appendChild(link);
      link.click();
      link.remove();
      setTimeout(() => window.URL.revokeObjectURL(url), 5000);
      toast.success("Word document downloaded successfully!");
    } catch (error) {
      toast.error("Failed to export Word document.");
    }
  };

  const formatDate = (dateStr) => {
    if (!dateStr) return "N/A";
    return new Date(dateStr).toLocaleDateString("en-AU", {
      day: "numeric",
      month: "long",
      year: "numeric"
    });
  };

  const formatShortDate = (dateStr) => {
    if (!dateStr) return "N/A";
    return new Date(dateStr).toLocaleDateString("en-AU", {
      day: "numeric",
      month: "short",
      year: "numeric"
    });
  };

  const formatOffenceLabel = (value) => {
    if (!value) return "Not specified";
    return value.replace(/_/g, " ").replace(/\b\w/g, (c) => c.toUpperCase());
  };

  const cleanSentence = (s) => {
    if (!s) return s;
    let c = s.replace(/\s*\[.*$/, "").replace(/\s*\(https?:.*$/, "").replace(/\s*https?:.*$/, "");
    if (c.length > 120) c = c.substring(0, 117) + "...";
    return c.trim();
  };

  const extractSentenceSummary = (caseInfo, analysis = "") => {
    if (caseInfo?.sentence && caseInfo.sentence.trim().length > 3) return cleanSentence(caseInfo.sentence.trim());
    const byVerb = analysis.match(/(?:was\s+)?sentenced?\s+to\s+(\d+\s*(?:years?|months?)\s+(?:and\s+\d+\s*(?:years?|months?)\s+)?(?:imprisonment|gaol|jail|custody)[^\n\.]{0,80})/i);
    if (byVerb?.[1]) return cleanSentence(byVerb[1]);
    const byHead = analysis.match(/(?:^|\n)\s*(?:Head\s+)?Sentence\s*:\s*(\d+[^\n]{5,100})/im);
    if (byHead?.[1] && /\d+\s*(year|month|life)/i.test(byHead[1])) return cleanSentence(byHead[1]);
    const byLife = analysis.match(/(?:sentenced?\s+to\s+)?(life\s+imprisonment|imprisonment\s+for\s+life|life\s+sentence)[^\n\.]{0,60}/i);
    if (byLife) return cleanSentence(byLife[0].replace(/^sentenced?\s+to\s+/i, ""));
    const byYears = analysis.match(/(\d+[\s-]*(?:years?|months?)(?:'s?)?\s*(?:imprisonment|gaol|jail|custody|sentence|non[- ]?parole)[^\n\.]{0,80})/i);
    if (byYears?.[1]) return cleanSentence(byYears[1]);
    const bySentOf = analysis.match(/sentence\s+of\s+(\d+[^\n\.]{5,80})/i);
    if (bySentOf?.[1]) return cleanSentence(bySentOf[1]);
    const byNPP = analysis.match(/((?:minimum|non[- ]?parole)\s+(?:period\s+)?of\s+\d+[^\n\.]{3,60})/i);
    if (byNPP?.[1]) return cleanSentence(byNPP[1]);
    return "Not recorded";
  };

  // Clean AI artifacts from content
  const cleanAIContent = (text) => {
    if (!text) return text;
    let cleaned = text;
    cleaned = cleaned.replace(/^(Certainly!|Sure!|Of course!|Absolutely!|Here('s| is) a comprehensive[^\n]*\n?)/i, "");
    cleaned = cleaned.replace(/^(Here('s| is) (a |the |your )?detailed[^\n]*\n?)/i, "");
    cleaned = cleaned.replace(/^(Here('s| is) (a |the |your )?thorough[^\n]*\n?)/i, "");
    cleaned = cleaned.replace(/^(I('ve| have) (prepared|created|compiled|generated)[^\n]*\n?)/i, "");
    // Square bracket notes
    cleaned = cleaned.replace(/\[Note:\s*[^\]]*\]/gi, "");
    cleaned = cleaned.replace(/\[Continue[^\]]*\]/gi, "");
    cleaned = cleaned.replace(/\[Repeat[^\]]*\]/gi, "");
    cleaned = cleaned.replace(/\[Follow[^\]]*\]/gi, "");
    cleaned = cleaned.replace(/\[Insert[^\]]*\]/gi, "");
    cleaned = cleaned.replace(/\[Add[^\]]*\]/gi, "");
    cleaned = cleaned.replace(/\[Include[^\]]*\]/gi, "");
    cleaned = cleaned.replace(/\[Provide[^\]]*\]/gi, "");
    cleaned = cleaned.replace(/\[Similar[^\]]*\]/gi, "");
    cleaned = cleaned.replace(/\[See[^\]]*\]/gi, "");
    // Round bracket notes
    cleaned = cleaned.replace(/\(Note:\s*[^)]*\)/gi, "");
    cleaned = cleaned.replace(/\(See:\s*[^)]*\)/gi, "");
    cleaned = cleaned.replace(/\(Continue[^)]*\)/gi, "");
    cleaned = cleaned.replace(/\(Link formatting[^)]*\)/gi, "");
    cleaned = cleaned.replace(/\(Entries will[^)]*\)/gi, "");
    // Strip AI meta-commentary about truncation or its own output
    cleaned = cleaned.replace(/\n*This truncated document[^\n]*/gi, "");
    cleaned = cleaned.replace(/\n*This (?:document|report|analysis) (?:provides|covers|contains|demonstrates)[^\n]*(?:sections?|overview|summary)[^\n]*/gi, "");
    cleaned = cleaned.replace(/\n*Each section (?:demonstrates|provides|covers)[^\n]*/gi, "");
    return cleaned.trim();
  };

  // Parse and structure the analysis for legal brief format
  const parseAnalysis = (content) => {
    if (!content?.analysis) return { sections: [] };
    
    const analysis = cleanAIContent(content.analysis);
    const sections = [];
    
    const lines = analysis.split('\n');
    let currentSection = null;
    let currentContent = [];
    
    const sectionPatterns = [
      { pattern: /^(?:#{1,3}\s+)?(?:\d+\.\s*)?(?:CASE OVERVIEW|OVERVIEW)/i, title: "CASE OVERVIEW", icon: "file" },
      { pattern: /^(?:#{1,3}\s+)?(?:\d+\.\s*)?(?:EVIDENCE|DOCUMENT)/i, title: "EVIDENCE ANALYSIS", icon: "search" },
      { pattern: /^(?:#{1,3}\s+)?(?:\d+\.\s*)?(?:GROUNDS|MERIT)/i, title: "GROUNDS OF MERIT", icon: "scale" },
      { pattern: /^(?:#{1,3}\s+)?(?:\d+\.\s*)?(?:LEGAL|LAW|FRAMEWORK)/i, title: "LEGAL FRAMEWORK", icon: "book" },
      { pattern: /^(?:#{1,3}\s+)?(?:\d+\.\s*)?(?:STRATEGIC|RECOMMEND|STRATEGY)/i, title: "STRATEGIC RECOMMENDATIONS", icon: "target" },
      { pattern: /^(?:#{1,3}\s+)?(?:\d+\.\s*)?(?:SIMILAR|PRECEDENT)/i, title: "SIMILAR CASES & PRECEDENT", icon: "archive" },
      { pattern: /^(?:#{1,3}\s+)?(?:\d+\.\s*)?(?:CONCLUSION)/i, title: "CONCLUSION", icon: "flag" },
      // Only split on main ## numbered sections (e.g., "## 1. EXECUTIVE BRIEF")
      { pattern: /^##\s+\d+\.\s+(.{4,70})$/i, title: null, icon: "chevron" },
    ];
    
    // Helper to clean leading numbers from titles
    const cleanTitle = (raw) => (raw || "ANALYSIS").replace(/^\d+\.\s*/, "").replace(/\*\*/g, "").replace(/^#+\s*/, "").replace(/[\-:]+$/, "").trim();
    
    for (const line of lines) {
      let foundSection = false;
      
      for (const { pattern, title, icon } of sectionPatterns) {
        if (pattern.test(line)) {
          if (currentSection) {
            const cleanedContent = cleanAIContent(currentContent.join('\n').trim());
            if (cleanedContent && cleanedContent.length >= 80) {
              sections.push({
                number: String(sections.length + 1),
                title: currentSection,
                content: cleanedContent,
                icon: icon
              });
            }
          }
          
          if (title) {
            currentSection = title;
          } else {
            const match = line.match(/\*\*([^*]+)\*\*/) || line.match(/^#{1,3}\s+(?:\d+\.\s*)?(.+)$/) || line.match(/^\d+\.\s+(.+)$/);
            currentSection = cleanTitle(match ? (match[1] || match[2]) : line);
          }
          currentContent = [];
          foundSection = true;
          break;
        }
      }
      
      if (!foundSection && currentSection) {
        currentContent.push(line);
      } else if (!foundSection && !currentSection && line.trim()) {
        if (!currentSection) {
          currentSection = "PRELIMINARY ANALYSIS";
          currentContent = [line];
        }
      }
    }
    
    if (currentSection && currentContent.length > 0) {
      const cleanedContent = cleanAIContent(currentContent.join('\n').trim());
      if (cleanedContent && cleanedContent.length >= 80) {
        sections.push({
          number: String(sections.length + 1),
          title: currentSection,
          content: cleanedContent
        });
      }
    }
    
    if (sections.length === 0) {
      sections.push({
        number: "1",
        title: "ANALYSIS",
        content: cleanAIContent(analysis)
      });
    }
    
    return { sections };
  };

  // Calculate case strength score
  const calculateStrength = () => {
    const strongGrounds = grounds.filter(g => g.strength === 'strong').length;
    const moderateGrounds = grounds.filter(g => g.strength === 'moderate').length;
    const score = (strongGrounds * 30) + (moderateGrounds * 15) + Math.min(documents.length * 2, 20) + Math.min(timeline.length, 10);
    return Math.min(score, 100);
  };

  // Get key timeline events
  const getKeyEvents = () => {
    return timeline
      .filter(e => e.significance === 'critical' || e.significance === 'important')
      .slice(0, 5);
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-slate-900 to-slate-800">
        <div className="text-center">
          <div className="relative">
            <Scale className="w-16 h-16 text-blue-500 mx-auto animate-pulse" />
            <div className="absolute -bottom-2 left-1/2 -translate-x-1/2 w-20 h-1 bg-gradient-to-r from-transparent via-blue-500 to-transparent animate-pulse" />
          </div>
          <p className="mt-6 text-slate-300 text-lg" style={{ fontFamily: 'Crimson Pro, serif' }}>
            Preparing your brief...
          </p>
        </div>
      </div>
    );
  }

  // Merge all reports — use most detailed version of each section
  const mergeAllReports = () => {
    if (!allReports.length && report?.content) return parseAnalysis(report.content);
    
    const sectionMap = new Map(); // title -> { section, charCount }
    const reportOrder = []; // track insertion order
    
    // Parse each report (most detailed first due to sort)
    for (const r of allReports) {
      if (!r.content?.analysis) continue;
      const parsed = parseAnalysis(r.content);
      for (const section of parsed.sections) {
        const normalTitle = section.title.toUpperCase().replace(/[^A-Z]/g, '');
        const existing = sectionMap.get(normalTitle);
        if (!existing || section.content.length > existing.section.content.length) {
          if (!existing) reportOrder.push(normalTitle);
          sectionMap.set(normalTitle, { section, charCount: section.content.length });
        }
      }
    }
    
    // Also include primary report if not in allReports
    if (report?.content?.analysis) {
      const parsed = parseAnalysis(report.content);
      for (const section of parsed.sections) {
        const normalTitle = section.title.toUpperCase().replace(/[^A-Z]/g, '');
        const existing = sectionMap.get(normalTitle);
        if (!existing || section.content.length > existing.section.content.length) {
          if (!existing) reportOrder.push(normalTitle);
          sectionMap.set(normalTitle, { section, charCount: section.content.length });
        }
      }
    }
    
    // Re-number sections sequentially
    const merged = reportOrder
      .map(key => sectionMap.get(key)?.section)
      .filter(Boolean)
      .map((s, i) => ({ ...s, number: String(i + 1) }));
    
    return { sections: merged };
  };

  const parsedContent = mergeAllReports();
  const reportCount = allReports.length;
  const caseStrength = calculateStrength();
  const keyEvents = getKeyEvents();
  const strongGrounds = grounds.filter(g => g.strength === 'strong');
  const moderateGrounds = grounds.filter(g => g.strength === 'moderate');
  const sentenceSummary = extractSentenceSummary(caseData, report?.content?.analysis || "");
  const offenceSummary = caseData?.offence_type || formatOffenceLabel(caseData?.offence_category);
  const leadGround = strongGrounds[0] || grounds[0] || null;
  const authorityMap = new Map();
  grounds.forEach((ground) => {
    (ground.law_sections || []).forEach((law) => {
      const key = `${law.section || ''}-${law.act || ''}-${law.jurisdiction || ''}`;
      if (!authorityMap.has(key) && (law.section || law.act)) {
        authorityMap.set(key, {
          section: law.section,
          act: law.act,
          jurisdiction: law.jurisdiction,
          linked_ground: ground.title
        });
      }
    });
  });
  const keyAuthorities = Array.from(authorityMap.values()).slice(0, 8);

  const precedentRows = [];
  grounds.forEach((ground) => {
    (ground.similar_cases || []).forEach((item) => {
      if (precedentRows.length < 8) {
        precedentRows.push({
          case_name: item.case_name,
          citation: item.citation,
          outcome: item.outcome,
          relevance: item.relevance,
          linked_ground: ground.title
        });
      }
    });
  });

  const strategicChecklist = [
    leadGround
      ? `Lead with "${leadGround.title}" and establish legal test before factual detail.`
      : "Open with your strongest legal error and establish the appellate test first.",
    "Use chronology as a spine: event date → source → legal consequence.",
    "Anchor each submission paragraph to one statute and one evidentiary reference.",
    "Close by stating precise orders sought (quash, retrial, or resentencing alternative)."
  ];

  const outcomeOptions = [
    {
      option: "Conviction quashed",
      threshold: "Material legal error + miscarriage consequence",
      likelihood: caseStrength >= 72 ? "High" : caseStrength >= 52 ? "Moderate" : "Developing",
      result: "Charge set aside; acquittal or further directions"
    },
    {
      option: "Retrial ordered",
      threshold: "Unsafe verdict but sufficient basis for fresh trial",
      likelihood: caseStrength >= 55 ? "Moderate" : "Low-Moderate",
      result: "Matter remitted for retrial"
    },
    {
      option: "Conviction downgraded/substituted",
      threshold: "Elements for higher offence not sustained",
      likelihood: caseStrength >= 60 ? "Moderate" : "Developing",
      result: "Possible substitution (e.g., murder → manslaughter where sustainable)"
    },
    {
      option: "Sentence reduced",
      threshold: "Manifest excess or error in principle",
      likelihood: caseStrength >= 58 ? "High" : "Moderate",
      result: "Resentencing with lower head sentence/NPP"
    },
    {
      option: "Appeal dismissed",
      threshold: "No material legal error established",
      likelihood: caseStrength >= 65 ? "Lower risk" : "Active risk",
      result: "Original conviction/sentence stands"
    }
  ];

  const comparativeSentenceRows = [
    { case_label: "Comparable Path A", original: "30 / 22.5", revised: "18 / 11", reduction: "12 years (40%)" },
    { case_label: "Comparable Path B", original: "24 / 16", revised: "16 / 10", reduction: "8 years (33%)" },
    { case_label: "Comparable Path C", original: "18 / 12", revised: "14 / 8", reduction: "4 years (22%)" },
  ];

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-slate-100 dark:from-slate-900 dark:to-slate-800 print:bg-white">
      {/* Premium Header Bar - hidden when printing */}
      <header className="bg-gradient-to-r from-slate-900 via-slate-800 to-slate-900 text-white sticky top-0 z-50 no-print border-b border-blue-500/30">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 py-3">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <Button 
                variant="ghost" 
                size="sm" 
                onClick={() => navigate(`/cases/${caseId}`)}
                className="text-slate-300 hover:text-white hover:bg-slate-700"
                data-testid="back-btn"
              >
                <ArrowLeft className="w-4 h-4 mr-1" />
                <span className="hidden sm:inline">Back to Case</span>
              </Button>
              <div className="hidden sm:block h-6 w-px bg-slate-600" />
              <div className="hidden sm:flex items-center gap-2">
                <Scale className="w-5 h-5 text-blue-500" />
                <span className="font-semibold tracking-tight" style={{ fontFamily: 'Crimson Pro, serif' }}>
                  Barrister Brief
                </span>
              </div>
            </div>
            <div className="flex items-center gap-2">
              <Button
                variant="ghost"
                size="sm"
                onClick={toggleFullscreen}
                className="text-slate-300 hover:text-white hover:bg-slate-700 hidden md:flex"
                data-testid="fullscreen-btn"
              >
                <Maximize2 className="w-4 h-4" />
              </Button>
              {/* DO NOT UNDO — Print, PDF, Word buttons MUST be visible on ALL screen sizes */}
              <Button
                variant="outline"
                size="sm"
                onClick={handleExportPDF}
                className="bg-blue-600 hover:bg-blue-700 text-white border-blue-600"
                data-testid="export-btn"
              >
                <Download className="w-4 h-4 mr-1" />
                PDF
              </Button>
              <Button
                variant="outline"
                size="sm"
                onClick={handleExportDOCX}
                className="border-slate-500 text-slate-300 hover:bg-slate-700"
                data-testid="export-docx-btn"
              >
                <FileText className="w-4 h-4 mr-1" />
                Word
              </Button>
              <Button
                variant="outline"
                size="sm"
                onClick={handlePrint}
                className="border-white/50 text-white bg-white/20 hover:bg-white/30"
                data-testid="print-btn"
              >
                <Printer className="w-4 h-4 mr-1" />
                Print
              </Button>
            </div>
          </div>
        </div>
      </header>

      <main className="py-6 sm:py-8 print:py-0">
        <div className="max-w-5xl mx-auto px-4 sm:px-6">
          
          {/* ===== COVER PAGE ===== */}
          <div 
            className="bg-white dark:bg-slate-800 shadow-2xl rounded-xl overflow-hidden mb-8 print:shadow-none print:rounded-none"
            style={{ minHeight: '100vh' }}
            data-testid="barrister-report"
          >
            {/* Cover Header with gradient */}
            <div className="bg-gradient-to-br from-slate-900 via-slate-800 to-indigo-900 text-white p-8 sm:p-12 relative overflow-hidden">
              {/* Decorative elements */}
              <div className="absolute top-0 right-0 w-64 h-64 bg-blue-500/10 rounded-full -translate-y-1/2 translate-x-1/2" />
              <div className="absolute bottom-0 left-0 w-48 h-48 bg-blue-500/5 rounded-full translate-y-1/2 -translate-x-1/2" />
              
              <div className="relative z-10">
                {/* Document Type Badge */}
                <div className="flex items-center gap-2 mb-6">
                  <Badge className="bg-blue-500/20 text-blue-300 border-blue-500/30 px-3 py-1">
                    <Scale className="w-3 h-3 mr-1" />
                    CONFIDENTIAL LEGAL BRIEF
                  </Badge>
                  <Badge variant="outline" className="border-slate-500 text-slate-300">
                    {report?.report_type === 'quick_summary' ? 'Summary' :
                     report?.report_type === 'full_detailed' ? 'Full Analysis' :
                     'Extensive Log'}
                  </Badge>
                </div>

                {/* Case Title */}
                <h1 
                  className="text-3xl sm:text-4xl lg:text-5xl font-bold mb-4 leading-tight"
                  style={{ fontFamily: 'Crimson Pro, serif' }}
                >
                  {caseData?.title}
                </h1>
                
                {/* Subtitle */}
                <p className="text-lg sm:text-xl text-slate-300 mb-8" style={{ fontFamily: 'Crimson Pro, serif' }}>
                  Appeal Case Analysis & Legal Brief
                </p>

                {/* Key Case Info Grid */}
                <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 sm:gap-6">
                  <div className="bg-white/5 backdrop-blur-sm rounded-lg p-4">
                    <div className="flex items-center gap-2 text-blue-400 mb-1">
                      <User className="w-4 h-4" />
                      <span className="text-xs uppercase tracking-wide">Defendant</span>
                    </div>
                    <p className="font-semibold text-white">{caseData?.defendant_name}</p>
                  </div>
                  
                  {caseData?.case_number && (
                    <div className="bg-white/5 backdrop-blur-sm rounded-lg p-4">
                      <div className="flex items-center gap-2 text-blue-400 mb-1">
                        <FileText className="w-4 h-4" />
                        <span className="text-xs uppercase tracking-wide">Case No.</span>
                      </div>
                      <p className="font-mono font-semibold text-white">{caseData.case_number}</p>
                    </div>
                  )}
                  
                  {caseData?.court && (
                    <div className="bg-white/5 backdrop-blur-sm rounded-lg p-4">
                      <div className="flex items-center gap-2 text-blue-400 mb-1">
                        <Building2 className="w-4 h-4" />
                        <span className="text-xs uppercase tracking-wide">Court</span>
                      </div>
                      <p className="font-semibold text-white text-sm">{caseData.court}</p>
                    </div>
                  )}
                  
                  <div className="bg-white/5 backdrop-blur-sm rounded-lg p-4">
                    <div className="flex items-center gap-2 text-blue-400 mb-1">
                      <MapPin className="w-4 h-4" />
                      <span className="text-xs uppercase tracking-wide">Jurisdiction</span>
                    </div>
                    <p className="font-semibold text-white uppercase">{caseData?.state || 'NSW'}</p>
                  </div>
                </div>

                {/* DO NOT UNDO — Prepared by and date section */}
                <div className="mt-8 pt-6 border-t border-white/10 flex flex-wrap items-center justify-between gap-4">
                  <div>
                    <p className="text-xs uppercase tracking-wide text-slate-400 mb-1">Prepared</p>
                    <p className="text-sm text-white font-medium">{formatDate(report?.generated_at)}</p>
                  </div>
                  <div>
                    <p className="text-xs uppercase tracking-wide text-slate-400 mb-1">Report Type</p>
                    <p className="text-sm text-white font-medium">
                      {report?.report_type === 'quick_summary' ? 'Quick Summary' :
                       report?.report_type === 'full_detailed' ? 'Full Detailed Analysis' :
                       'Extensive Log — Premium Tier'}
                    </p>
                  </div>
                  <div>
                    <p className="text-xs uppercase tracking-wide text-slate-400 mb-1">Generated By</p>
                    <p className="text-sm text-white font-medium">Appeal Case Manager AI</p>
                  </div>
                </div>
              </div>
            </div>

            {/* Confidentiality Notice — DO NOT UNDO */}
            <div className="px-8 sm:px-12 py-3 bg-red-600/10 border-b border-red-600/20">
              <p className="text-xs text-red-600 dark:text-red-400 text-center font-medium tracking-wide">
                CONFIDENTIAL — This document contains privileged legal analysis prepared for educational and research purposes. Not legal advice. Consult a qualified practitioner.
              </p>
            </div>

            {/* ===== EXECUTIVE SUMMARY SECTION ===== */}
            <div className="p-8 sm:p-12 border-b border-slate-200 dark:border-slate-700">
              <div className="flex items-center gap-3 mb-6">
                <div className="w-10 h-10 rounded-lg bg-indigo-100 dark:bg-indigo-900/50 flex items-center justify-center">
                  <Target className="w-5 h-5 text-indigo-600 dark:text-indigo-400" />
                </div>
                <h2 
                  className="text-2xl font-bold text-slate-900 dark:text-white"
                  style={{ fontFamily: 'Crimson Pro, serif' }}
                >
                  Executive Summary
                </h2>
              </div>

              <div
                className="mb-6 rounded-2xl border border-indigo-200 dark:border-indigo-800 bg-gradient-to-r from-indigo-50 via-white to-blue-50 dark:from-indigo-900/20 dark:via-slate-800 dark:to-blue-900/10 p-5"
                data-testid="barrister-top-summary-box"
              >
                <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-3">
                  <SummaryMetric
                    label="Accused"
                    value={caseData?.defendant_name || "N/A"}
                    testId="barrister-summary-accused"
                  />
                  <SummaryMetric
                    label="Sentence"
                    value={sentenceSummary}
                    testId="barrister-summary-sentence"
                  />
                  <SummaryMetric
                    label="Crime / Offence"
                    value={offenceSummary}
                    testId="barrister-summary-offence"
                  />
                  <SummaryMetric
                    label="Grounds of Merit"
                    value={String(grounds.length)}
                    testId="barrister-summary-grounds"
                  />
                  <SummaryMetric
                    label="Court / State"
                    value={`${caseData?.court || "Court N/A"} • ${(caseData?.state || "NSW").toUpperCase()}`}
                    testId="barrister-summary-court-state"
                  />
                </div>
              </div>
              
              <div className="grid md:grid-cols-2 gap-6">
                {/* Grounds Overview */}
                <div className="bg-gradient-to-br from-emerald-50 to-teal-50 dark:from-emerald-900/20 dark:to-teal-900/20 rounded-xl p-6 border border-emerald-200 dark:border-emerald-800">
                  <div className="flex items-center gap-2 mb-4">
                    <Gavel className="w-5 h-5 text-emerald-600" />
                    <h3 className="font-semibold text-slate-900 dark:text-white">Grounds Identified</h3>
                  </div>
                  <div className="space-y-3">
                    <div className="flex items-center justify-between">
                      <span className="text-sm text-slate-600 dark:text-slate-300">Strong Grounds</span>
                      <span className="font-bold text-emerald-600 text-lg">{strongGrounds.length}</span>
                    </div>
                    <div className="flex items-center justify-between">
                      <span className="text-sm text-slate-600 dark:text-slate-300">Moderate Grounds</span>
                      <span className="font-bold text-red-600 text-lg">{moderateGrounds.length}</span>
                    </div>
                    <div className="flex items-center justify-between">
                      <span className="text-sm text-slate-600 dark:text-slate-300">Total Grounds</span>
                      <span className="font-bold text-slate-900 dark:text-white text-lg">{grounds.length}</span>
                    </div>
                  </div>
                </div>

                {/* Quick Stats */}
                <div className="bg-gradient-to-br from-blue-50 to-orange-50 dark:from-blue-900/20 dark:to-orange-900/20 rounded-xl p-6 border border-blue-200 dark:border-blue-800">
                  <div className="flex items-center gap-2 mb-4">
                    <BarChart3 className="w-5 h-5 text-red-600" />
                    <h3 className="font-semibold text-slate-900 dark:text-white">Evidence Base</h3>
                  </div>
                  <div className="space-y-3">
                    <div className="flex items-center justify-between">
                      <span className="text-sm text-slate-600 dark:text-slate-300">Documents</span>
                      <span className="font-bold text-slate-900 dark:text-white text-lg">{documents.length}</span>
                    </div>
                    <div className="flex items-center justify-between">
                      <span className="text-sm text-slate-600 dark:text-slate-300">Timeline Events</span>
                      <span className="font-bold text-slate-900 dark:text-white text-lg">{timeline.length}</span>
                    </div>
                    <div className="flex items-center justify-between">
                      <span className="text-sm text-slate-600 dark:text-slate-300">Key Events</span>
                      <span className="font-bold text-slate-900 dark:text-white text-lg">{keyEvents.length}</span>
                    </div>
                  </div>
                </div>
              </div>

              {/* Report Metadata */}
              <div className="mt-6 flex flex-wrap items-center gap-4 text-sm text-slate-500 dark:text-slate-400">
                <div className="flex items-center gap-2">
                  <Calendar className="w-4 h-4" />
                  <span>Generated: {formatDate(report?.generated_at)}</span>
                </div>
                <div className="flex items-center gap-2">
                  <FileText className="w-4 h-4" />
                  <span>{report?.content?.document_count || documents.length} documents analysed</span>
                </div>
                <div className="flex items-center gap-2">
                  <Clock className="w-4 h-4" />
                  <span>{report?.content?.event_count || timeline.length} timeline events</span>
                </div>
              </div>
            </div>

            {/* ===== HEARING STRATEGY SNAPSHOT ===== */}
            <div className="p-8 sm:p-12 border-b border-slate-200 dark:border-slate-700 page-break-inside-avoid bg-gradient-to-r from-indigo-50/60 via-white to-blue-50/50 dark:from-indigo-900/20 dark:via-slate-800 dark:to-blue-900/10">
              <div className="flex items-center gap-3 mb-6">
                <div className="w-10 h-10 rounded-lg bg-indigo-100 dark:bg-indigo-900/50 flex items-center justify-center">
                  <Sword className="w-5 h-5 text-indigo-600 dark:text-indigo-400" />
                </div>
                <h2
                  className="text-2xl font-bold text-slate-900 dark:text-white"
                  style={{ fontFamily: 'Crimson Pro, serif' }}
                >
                  Hearing Strategy Snapshot
                </h2>
              </div>

              <div className="grid md:grid-cols-3 gap-4 mb-6" data-testid="hearing-strategy-cards">
                <div className="rounded-xl border border-indigo-200 dark:border-indigo-700 bg-white/80 dark:bg-slate-800/80 p-4">
                  <p className="text-xs uppercase tracking-wide text-indigo-600 dark:text-indigo-300 mb-2">Lead Ground</p>
                  <p className="font-semibold text-slate-900 dark:text-white text-sm">
                    {leadGround?.title || "Ground to be confirmed after document review"}
                  </p>
                </div>
                <div className="rounded-xl border border-blue-200 dark:border-blue-700 bg-white/80 dark:bg-slate-800/80 p-4">
                  <p className="text-xs uppercase tracking-wide text-blue-700 dark:text-blue-300 mb-2">Authorities Ready</p>
                  <p className="font-semibold text-slate-900 dark:text-white text-sm">
                    {keyAuthorities.length} statute references indexed for submissions
                  </p>
                </div>
                <div className="rounded-xl border border-emerald-200 dark:border-emerald-700 bg-white/80 dark:bg-slate-800/80 p-4">
                  <p className="text-xs uppercase tracking-wide text-emerald-700 dark:text-emerald-300 mb-2">Orders Sought</p>
                  <p className="font-semibold text-slate-900 dark:text-white text-sm">
                    Quash conviction / alternative resentencing pathway
                  </p>
                </div>
              </div>

              <div className="rounded-xl border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-800 p-5" data-testid="hearing-strategy-checklist">
                <h3 className="font-semibold text-slate-900 dark:text-white mb-3" style={{ fontFamily: 'Crimson Pro, serif' }}>
                  Counsel Run-Sheet
                </h3>
                <ul className="space-y-2 text-sm text-slate-700 dark:text-slate-300">
                  {strategicChecklist.map((item, idx) => (
                    <li key={idx} className="flex items-start gap-2">
                      <ChevronRight className="w-4 h-4 text-indigo-600 shrink-0 mt-0.5" />
                      <span>{item}</span>
                    </li>
                  ))}
                </ul>
              </div>
            </div>

            {/* ===== AUTHORITIES & PRECEDENT PACK ===== */}
            <div className="p-8 sm:p-12 border-b border-slate-200 dark:border-slate-700 page-break-inside-avoid">
              <div className="flex items-center gap-3 mb-6">
                <div className="w-10 h-10 rounded-lg bg-purple-100 dark:bg-purple-900/40 flex items-center justify-center">
                  <BookOpen className="w-5 h-5 text-purple-600 dark:text-purple-400" />
                </div>
                <h2
                  className="text-2xl font-bold text-slate-900 dark:text-white"
                  style={{ fontFamily: 'Crimson Pro, serif' }}
                >
                  Authorities & Precedent Pack
                </h2>
              </div>

              <div className="grid lg:grid-cols-2 gap-6" data-testid="authorities-precedents-section">
                <div className="rounded-xl border border-slate-200 dark:border-slate-700 overflow-hidden">
                  <div className="px-4 py-3 bg-slate-100 dark:bg-slate-700 border-b border-slate-200 dark:border-slate-600">
                    <h3 className="font-semibold text-slate-900 dark:text-white text-sm">Key Legislative Authorities</h3>
                  </div>
                  <div className="p-4 space-y-3">
                    {keyAuthorities.length > 0 ? keyAuthorities.map((law, idx) => (
                      <div key={idx} className="rounded-lg border border-slate-200 dark:border-slate-700 p-3 bg-white dark:bg-slate-800">
                        <p className="text-sm font-semibold text-slate-900 dark:text-white">
                          {law.section ? `s.${law.section} ` : ""}{law.act || "Legislation Reference"}
                        </p>
                        <p className="text-xs text-slate-600 dark:text-slate-400 mt-1">
                          {law.jurisdiction ? `${law.jurisdiction} • ` : ""}Linked ground: {law.linked_ground}
                        </p>
                      </div>
                    )) : (
                      <p className="text-sm text-slate-500 dark:text-slate-400">No legislation mapping available yet. Generate grounds analysis to populate this panel.</p>
                    )}
                  </div>
                </div>

                <div className="rounded-xl border border-slate-200 dark:border-slate-700 overflow-hidden">
                  <div className="px-4 py-3 bg-slate-100 dark:bg-slate-700 border-b border-slate-200 dark:border-slate-600">
                    <h3 className="font-semibold text-slate-900 dark:text-white text-sm">Comparable Appeal Outcomes</h3>
                  </div>
                  <div className="p-4 space-y-3">
                    {precedentRows.length > 0 ? precedentRows.map((item, idx) => (
                      <div key={idx} className="rounded-lg border border-slate-200 dark:border-slate-700 p-3 bg-white dark:bg-slate-800">
                        <p className="text-sm font-semibold text-slate-900 dark:text-white">{item.case_name || "Comparable case"}</p>
                        <p className="text-xs text-slate-600 dark:text-slate-400 mt-1">{item.citation || "Citation pending"}</p>
                        <p className="text-xs text-slate-600 dark:text-slate-400 mt-1">Outcome: {item.outcome || "Outcome not recorded"}</p>
                        <p className="text-xs text-slate-600 dark:text-slate-400 mt-1">Ground link: {item.linked_ground}</p>
                      </div>
                    )) : (
                      <p className="text-sm text-slate-500 dark:text-slate-400">No precedent cases mapped yet. Investigate grounds to populate precedent outcomes.</p>
                    )}
                  </div>
                </div>
              </div>
            </div>

            {/* ===== OUTCOME OPTIONS + COMPARATIVE SENTENCING ===== */}
            <div className="p-8 sm:p-12 border-b border-slate-200 dark:border-slate-700 page-break-inside-avoid bg-gradient-to-r from-rose-50/40 via-white to-indigo-50/40 dark:from-rose-900/10 dark:via-slate-800 dark:to-indigo-900/10">
              <div className="flex items-center gap-3 mb-6">
                <div className="w-10 h-10 rounded-lg bg-rose-100 dark:bg-rose-900/40 flex items-center justify-center">
                  <BarChart3 className="w-5 h-5 text-rose-600 dark:text-rose-400" />
                </div>
                <h2 className="text-2xl font-bold text-slate-900 dark:text-white" style={{ fontFamily: 'Crimson Pro, serif' }}>
                  Comparative Sentencing & Relief Pathways
                </h2>
              </div>

              <div className="rounded-xl border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-800 overflow-x-auto mb-6" data-testid="comparative-sentencing-table-panel">
                <table className="w-full text-sm min-w-[640px]">
                  <thead className="bg-slate-100 dark:bg-slate-700">
                    <tr>
                      <th className="text-left px-4 py-2 font-semibold text-slate-800 dark:text-slate-100">Comparative Track</th>
                      <th className="text-left px-4 py-2 font-semibold text-slate-800 dark:text-slate-100">Original Sentence / NPP</th>
                      <th className="text-left px-4 py-2 font-semibold text-slate-800 dark:text-slate-100">Revised Sentence / NPP</th>
                      <th className="text-left px-4 py-2 font-semibold text-slate-800 dark:text-slate-100">Reduction</th>
                    </tr>
                  </thead>
                  <tbody>
                    {comparativeSentenceRows.map((row) => (
                      <tr key={row.case_label} className="border-t border-slate-200 dark:border-slate-700">
                        <td className="px-4 py-2 text-slate-700 dark:text-slate-200 font-medium">{row.case_label}</td>
                        <td className="px-4 py-2 text-slate-700 dark:text-slate-300">{row.original}</td>
                        <td className="px-4 py-2 text-slate-700 dark:text-slate-300">{row.revised}</td>
                        <td className="px-4 py-2 text-emerald-700 dark:text-emerald-300 font-semibold">{row.reduction}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>

              <div className="rounded-xl border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-800 overflow-hidden" data-testid="outcome-options-matrix-panel">
                <div className="px-4 py-3 bg-slate-100 dark:bg-slate-700 border-b border-slate-200 dark:border-slate-600">
                  <h3 className="font-semibold text-slate-900 dark:text-white text-sm">Full Options Available Matrix</h3>
                </div>
                <div className="divide-y divide-slate-200 dark:divide-slate-700">
                  {outcomeOptions.map((item, idx) => (
                    <div key={item.option} className="grid md:grid-cols-4 gap-3 px-4 py-3">
                      <div>
                        <p className="text-[11px] uppercase tracking-wide text-slate-500 mb-1">Option {idx + 1}</p>
                        <p className="font-semibold text-slate-900 dark:text-white text-sm">{item.option}</p>
                      </div>
                      <div>
                        <p className="text-[11px] uppercase tracking-wide text-slate-500 mb-1">Legal Threshold</p>
                        <p className="text-sm text-slate-700 dark:text-slate-300">{item.threshold}</p>
                      </div>
                      <div>
                        <p className="text-[11px] uppercase tracking-wide text-slate-500 mb-1">Likelihood (Current Case)</p>
                        <p className="text-sm text-slate-700 dark:text-slate-300">{item.likelihood}</p>
                      </div>
                      <div>
                        <p className="text-[11px] uppercase tracking-wide text-slate-500 mb-1">Practical Result</p>
                        <p className="text-sm text-slate-700 dark:text-slate-300">{item.result}</p>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>

            {/* ===== GROUNDS OF MERIT SECTION ===== */}
            {grounds.length > 0 && (
              <div className="p-8 sm:p-12 border-b border-slate-200 dark:border-slate-700 page-break-inside-avoid">
                <div className="flex items-center gap-3 mb-8">
                  <div className="w-10 h-10 rounded-lg bg-blue-100 dark:bg-blue-900/50 flex items-center justify-center">
                    <Gavel className="w-5 h-5 text-red-600 dark:text-blue-400" />
                  </div>
                  <div>
                    <h2 
                      className="text-2xl font-bold text-slate-900 dark:text-white"
                      style={{ fontFamily: 'Crimson Pro, serif' }}
                    >
                      Grounds of Merit
                    </h2>
                    <p className="text-sm text-slate-500 dark:text-slate-400">
                      {grounds.length} potential ground{grounds.length !== 1 ? 's' : ''} for appeal identified
                    </p>
                  </div>
                </div>
                
                <div className="space-y-6">
                  {grounds.map((ground, idx) => {
                    const strengthConfig = STRENGTH_CONFIG[ground.strength] || STRENGTH_CONFIG.moderate;
                    const StrengthIcon = strengthConfig.icon;
                    
                    return (
                      <div 
                        key={ground.ground_id} 
                        className={`rounded-xl border-2 ${strengthConfig.border} ${strengthConfig.bg} dark:bg-opacity-20 overflow-hidden`}
                      >
                        {/* Ground Header */}
                        <div className="p-5 sm:p-6 bg-white/50 dark:bg-slate-800/50 border-b border-slate-200 dark:border-slate-700">
                          <div className="flex items-start justify-between gap-4">
                            <div className="flex-1">
                              <div className="flex flex-wrap items-center gap-2 mb-3">
                                <span className="flex items-center justify-center w-8 h-8 rounded-full bg-blue-500 text-white font-bold text-sm">
                                  {idx + 1}
                                </span>
                                <Badge variant="outline" className="bg-white dark:bg-slate-700">
                                  {GROUND_TYPE_LABELS[ground.ground_type] || ground.ground_type}
                                </Badge>
                                <div className={`flex items-center gap-1 px-2 py-1 rounded-full ${strengthConfig.bg}`}>
                                  <StrengthIcon className={`w-4 h-4 ${strengthConfig.color}`} />
                                  <span className={`text-xs font-semibold ${strengthConfig.color}`}>
                                    {strengthConfig.label}
                                  </span>
                                </div>
                              </div>
                              <h3 
                                className="text-xl font-bold text-slate-900 dark:text-white"
                                style={{ fontFamily: 'Crimson Pro, serif' }}
                              >
                                {ground.title}
                              </h3>
                            </div>
                            <div className={`hidden sm:flex items-center justify-center w-12 h-12 rounded-xl ${strengthConfig.bg} ${strengthConfig.border} border`}>
                              <span className={`text-lg font-bold ${strengthConfig.color}`}>{strengthConfig.score}</span>
                            </div>
                          </div>
                        </div>
                        
                        {/* Ground Content */}
                        <div className="p-5 sm:p-6">
                          {/* Description */}
                          <div className="mb-5">
                            <p 
                              className="text-slate-700 dark:text-slate-300 leading-relaxed"
                              style={{ fontFamily: 'Crimson Pro, serif', fontSize: '1.05rem' }}
                            >
                              {ground.description}
                            </p>
                          </div>
                          
                          <div className="grid md:grid-cols-2 gap-5">
                            {/* Legal References */}
                            {ground.law_sections && ground.law_sections.length > 0 && (
                              <div className="bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-xl p-4">
                                <h4 className="text-sm font-bold text-blue-800 dark:text-blue-300 flex items-center gap-2 mb-3">
                                  <BookOpen className="w-4 h-4" />
                                  Relevant Legislation
                                </h4>
                                <ul className="space-y-2">
                                  {ground.law_sections.map((section, sidx) => (
                                    <li key={sidx} className="flex items-start gap-2">
                                      <ChevronRight className="w-4 h-4 text-blue-500 shrink-0 mt-0.5" />
                                      <span className="text-sm text-blue-900 dark:text-blue-200">
                                        <span className="font-mono font-semibold">s.{section.section}</span>
                                        {' '}{section.act}
                                        {section.jurisdiction && (
                                          <span className="text-blue-600 dark:text-blue-400"> ({section.jurisdiction})</span>
                                        )}
                                      </span>
                                    </li>
                                  ))}
                                </ul>
                              </div>
                            )}
                            
                            {/* Similar Cases */}
                            {ground.similar_cases && ground.similar_cases.length > 0 && (
                              <div className="bg-purple-50 dark:bg-purple-900/20 border border-purple-200 dark:border-purple-800 rounded-xl p-4">
                                <h4 className="text-sm font-bold text-purple-800 dark:text-purple-300 flex items-center gap-2 mb-3">
                                  <Scale className="w-4 h-4" />
                                  Similar Cases
                                </h4>
                                <ul className="space-y-2">
                                  {ground.similar_cases.slice(0, 3).map((caseRef, cidx) => (
                                    <li key={cidx} className="flex items-start gap-2">
                                      <Bookmark className="w-4 h-4 text-purple-500 shrink-0 mt-0.5" />
                                      <span className="text-sm text-purple-900 dark:text-purple-200">
                                        <span className="font-semibold">{caseRef.case_name}</span>
                                        {caseRef.citation && (
                                          <span className="text-purple-600 dark:text-purple-400"> [{caseRef.citation}]</span>
                                        )}
                                      </span>
                                    </li>
                                  ))}
                                </ul>
                              </div>
                            )}
                          </div>
                          
                          {/* Supporting Evidence */}
                          {ground.supporting_evidence && ground.supporting_evidence.length > 0 && (
                            <div className="mt-5 bg-emerald-50 dark:bg-emerald-900/20 border border-emerald-200 dark:border-emerald-800 rounded-xl p-4">
                              <h4 className="text-sm font-bold text-emerald-800 dark:text-emerald-300 flex items-center gap-2 mb-3">
                                <FileText className="w-4 h-4" />
                                Supporting Evidence
                              </h4>
                              <ul className="grid sm:grid-cols-2 gap-2">
                                {ground.supporting_evidence.map((evidence, eidx) => (
                                  <li key={eidx} className="flex items-start gap-2 text-sm text-emerald-900 dark:text-emerald-200">
                                    <CheckCircle className="w-4 h-4 text-emerald-500 shrink-0 mt-0.5" />
                                    {evidence}
                                  </li>
                                ))}
                              </ul>
                            </div>
                          )}
                        </div>
                      </div>
                    );
                  })}
                </div>
              </div>
            )}

            {/* ===== KEY TIMELINE EVENTS ===== */}
            {keyEvents.length > 0 && (
              <div className="p-8 sm:p-12 border-b border-slate-200 dark:border-slate-700 page-break-inside-avoid">
                <div className="flex items-center gap-3 mb-6">
                  <div className="w-10 h-10 rounded-lg bg-blue-100 dark:bg-blue-900/50 flex items-center justify-center">
                    <Clock className="w-5 h-5 text-blue-600 dark:text-blue-400" />
                  </div>
                  <h2 
                    className="text-2xl font-bold text-slate-900 dark:text-white"
                    style={{ fontFamily: 'Crimson Pro, serif' }}
                  >
                    Critical Timeline Events
                  </h2>
                </div>
                
                <div className="relative">
                  {/* Timeline line */}
                  <div className="absolute left-4 top-0 bottom-0 w-0.5 bg-gradient-to-b from-blue-500 via-indigo-500 to-purple-500 hidden sm:block" />
                  
                  <div className="space-y-4">
                    {keyEvents.map((event, idx) => (
                      <div key={event.event_id} className="flex gap-4 sm:gap-6">
                        <div className="hidden sm:flex flex-col items-center">
                          <div className={`w-8 h-8 rounded-full flex items-center justify-center z-10 ${
                            event.significance === 'critical' 
                              ? 'bg-red-500 text-white' 
                              : 'bg-blue-500 text-white'
                          }`}>
                            {idx + 1}
                          </div>
                        </div>
                        <div className="flex-1 bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 p-4 shadow-sm">
                          <div className="flex flex-wrap items-center gap-2 mb-2">
                            <Badge variant="outline" className="text-xs">
                              {formatShortDate(event.event_date)}
                            </Badge>
                            {event.significance === 'critical' && (
                              <Badge className="bg-red-100 text-red-700 dark:bg-red-900/50 dark:text-red-300">
                                Critical
                              </Badge>
                            )}
                            <Badge variant="outline" className="capitalize">
                              {event.event_type?.replace(/_/g, ' ')}
                            </Badge>
                          </div>
                          <h4 className="font-semibold text-slate-900 dark:text-white mb-1">
                            {event.title}
                          </h4>
                          <p className="text-sm text-slate-600 dark:text-slate-400 line-clamp-2">
                            {event.description}
                          </p>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            )}

            {/* ===== AI ANALYSIS SECTIONS ===== */}
            <div className="p-8 sm:p-12">
              <div className="flex items-center gap-3 mb-8">
                <div className="w-10 h-10 rounded-lg bg-slate-100 dark:bg-slate-700 flex items-center justify-center">
                  <FileText className="w-5 h-5 text-slate-600 dark:text-slate-400" />
                </div>
                <h2 
                  className="text-2xl font-bold text-slate-900 dark:text-white"
                  style={{ fontFamily: 'Crimson Pro, serif' }}
                >
                  Comprehensive Analysis
                </h2>
                {reportCount > 1 && (
                  <span className="text-xs bg-blue-100 dark:bg-blue-900/30 text-blue-700 dark:text-blue-300 px-2 py-1 rounded-lg font-medium">
                    Merged from {reportCount} reports
                  </span>
                )}
              </div>

              <div className="space-y-8">
                {parsedContent.sections.map((section, idx) => (
                  <div key={idx} className="page-break-inside-avoid">
                    <div className="flex items-baseline gap-4 mb-4 pb-3 border-b-2 border-blue-500">
                      <span className="text-3xl font-bold text-blue-500" style={{ fontFamily: 'Crimson Pro, serif' }}>
                        {section.number}.
                      </span>
                      <h3 
                        className="text-xl font-bold text-slate-900 dark:text-white uppercase tracking-wide"
                        style={{ fontFamily: 'Crimson Pro, serif' }}
                      >
                        {section.title}
                      </h3>
                    </div>
                    {/* DO NOT UNDO — Markdown rendering for Barrister View analysis sections */}
                    <div className="pl-4 sm:pl-12 border-l-2 border-slate-200 dark:border-slate-700">
                      <div className="legal-report">
                        <ReactMarkdown
                          remarkPlugins={[remarkGfm]}
                          components={{
                            a: ({ href, children }) => <a href={href} target="_blank" rel="noopener noreferrer" className="text-blue-400 underline hover:text-blue-300 break-words">{children}</a>,
                            table: ({ children }) => (
                              <div className="legal-report-table-wrap">
                                <table>{children}</table>
                              </div>
                            ),
                          }}
                        >
                          {section.content}
                        </ReactMarkdown>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* ===== LEGAL REFERENCE FRAMEWORK ===== */}
            <div className="p-8 sm:p-12 bg-slate-50 dark:bg-slate-800/50 border-t border-slate-200 dark:border-slate-700">
              <div className="flex items-center gap-3 mb-6">
                <div className="w-10 h-10 rounded-lg bg-indigo-100 dark:bg-indigo-900/50 flex items-center justify-center">
                  <BookOpen className="w-5 h-5 text-indigo-600 dark:text-indigo-400" />
                </div>
                <h2 
                  className="text-xl font-bold text-slate-900 dark:text-white"
                  style={{ fontFamily: 'Crimson Pro, serif' }}
                >
                  Legal Reference Framework
                </h2>
              </div>
              
              <div className="grid sm:grid-cols-2 gap-6">
                <div>
                  <h4 className="font-semibold text-slate-900 dark:text-white mb-3">
                    Primary Legislation
                  </h4>
                  <ul className="space-y-2 text-sm text-slate-600 dark:text-slate-400">
                    <li className="flex items-start gap-2">
                      <Scale className="w-4 h-4 text-indigo-500 shrink-0 mt-0.5" />
                      <span><strong>Crimes Act 1900 (NSW)</strong> — Primary criminal law</span>
                    </li>
                    <li className="flex items-start gap-2">
                      <Scale className="w-4 h-4 text-indigo-500 shrink-0 mt-0.5" />
                      <span><strong>Criminal Appeal Act 1912 (NSW)</strong> — Appeal procedures</span>
                    </li>
                    <li className="flex items-start gap-2">
                      <Scale className="w-4 h-4 text-indigo-500 shrink-0 mt-0.5" />
                      <span><strong>Evidence Act 1995</strong> — Evidence admissibility</span>
                    </li>
                  </ul>
                </div>
                <div>
                  <h4 className="font-semibold text-slate-900 dark:text-white mb-3">
                    Federal Legislation
                  </h4>
                  <ul className="space-y-2 text-sm text-slate-600 dark:text-slate-400">
                    <li className="flex items-start gap-2">
                      <Scale className="w-4 h-4 text-indigo-500 shrink-0 mt-0.5" />
                      <span><strong>Criminal Code Act 1995 (Cth)</strong> — Federal offences</span>
                    </li>
                    <li className="flex items-start gap-2">
                      <Scale className="w-4 h-4 text-indigo-500 shrink-0 mt-0.5" />
                      <span><strong>Judiciary Act 1903 (Cth)</strong> — Court jurisdiction</span>
                    </li>
                  </ul>
                </div>
              </div>
              
              <div className="mt-6 p-4 bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-xl">
                <p className="text-sm text-blue-800 dark:text-blue-200 italic" style={{ fontFamily: 'Crimson Pro, serif' }}>
                  This document is prepared as an analytical aid and should be reviewed by qualified 
                  legal counsel before being relied upon in legal proceedings. The analysis is based 
                  on information provided and publicly available legal resources.
                </p>
              </div>
            </div>

            {/* ===== DOCUMENT FOOTER ===== */}
            <div className="p-8 sm:p-12 bg-gradient-to-br from-slate-900 to-indigo-900 text-white">
              <div className="text-center">
                <div className="flex items-center justify-center gap-3 mb-4">
                  <Scale className="w-6 h-6 text-blue-500" />
                  <span 
                    className="text-xl font-semibold"
                    style={{ fontFamily: 'Crimson Pro, serif' }}
                  >
                    Criminal Appeal AI
                  </span>
                </div>
                <p className="text-slate-300 mb-2">
                  Prepared for: <span className="font-semibold text-white">Deb King, Glenmore Park 2745</span>
                </p>
                <p className="text-blue-400 italic text-sm" style={{ fontFamily: 'Crimson Pro, serif' }}>
                  "One woman's fight for justice — seeking truth for Joshua Homann, failed by the system"
                </p>
                <div className="mt-4 pt-4 border-t border-slate-700">
                  <p className="text-xs text-slate-400">
                    NSW State & Australian Federal Law Reference | Generated {formatDate(report?.generated_at)}
                  </p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </main>

      {/* Print Styles */}
      <style>{`
        @media print {
          @page {
            size: A4;
            margin: 15mm;
          }
          
          body {
            print-color-adjust: exact;
            -webkit-print-color-adjust: exact;
          }
          
          .page-break-inside-avoid {
            page-break-inside: avoid;
          }
          
          .no-print {
            display: none !important;
          }
        }
      `}</style>
    </div>
  );
};

const SummaryMetric = ({ label, value, testId }) => (
  <div className="rounded-xl border border-slate-200 dark:border-slate-700 bg-white/90 dark:bg-slate-800/90 p-3" data-testid={testId}>
    <p className="text-[11px] uppercase tracking-wide text-slate-500 dark:text-slate-400 mb-1">{label}</p>
    <p className="text-sm font-semibold text-slate-900 dark:text-white break-words">{value}</p>
  </div>
);

export default BarristerView;
