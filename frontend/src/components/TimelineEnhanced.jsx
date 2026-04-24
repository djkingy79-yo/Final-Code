/* ========================================================================
   DO NOT UNDO — ENTIRE FILE PROTECTED
   All features, functions, styles, and content in this file are approved
   and must be preserved. Do not remove, rename, or refactor any code.
   ======================================================================== */
import { useState, useMemo } from "react";
import { 
  Trash2, FileText, Users, AlertTriangle, Link2, Scale,
  Filter, Search, Download, ChevronDown, ChevronUp, Printer, ArrowUp, ArrowDown
} from "lucide-react";
import auSpelling from "../utils/auSpelling";
import { renderMarkdownToHtml } from "../utils/mdRender";
import { buildExportHtml } from "../utils/exportHtml";
import { Button } from "./ui/button";
import { Badge } from "./ui/badge";
import { Input } from "./ui/input";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "./ui/select";
import {
  Collapsible,
  CollapsibleContent,
  CollapsibleTrigger,
} from "./ui/collapsible";

const EVENT_TYPE_LABELS = {
  // Pre-trial
  arrest: "Arrest",
  charge: "Charge",
  bail_hearing: "Bail Hearing",
  committal: "Committal",
  indictment: "Indictment",
  // Trial
  jury_selection: "Jury Selection",
  opening_statements: "Opening Statements",
  witness_testimony: "Witness Testimony",
  cross_examination: "Cross Examination",
  closing_arguments: "Closing Arguments",
  jury_deliberation: "Jury Deliberation",
  verdict: "Verdict",
  // Evidence
  evidence_discovery: "Evidence Discovery",
  forensic_report: "Forensic Report",
  expert_opinion: "Expert Opinion",
  disclosure: "Disclosure",
  // Post-conviction
  sentencing: "Sentencing",
  appeal_lodged: "Appeal Lodged",
  leave_application: "Leave Application",
  appeal_hearing: "Appeal Hearing",
  // Investigation
  police_interview: "Police Interview",
  erisp_recording: "ERISP Recording",
  crime_scene: "Crime Scene",
  search_warrant: "Search Warrant",
  // General
  court_hearing: "Court Hearing",
  other: "Other Event"
};

const EVENT_CATEGORIES = {
  pre_trial: { label: "Pre-Trial", color: "bg-blue-100 text-blue-800 border-blue-200" },
  trial: { label: "Trial", color: "bg-blue-100 text-blue-800 border-blue-200" },
  evidence: { label: "Evidence", color: "bg-emerald-100 text-emerald-800 border-emerald-200" },
  post_conviction: { label: "Post-Conviction", color: "bg-purple-100 text-purple-800 border-purple-200" },
  investigation: { label: "Investigation", color: "bg-slate-100 text-slate-800 border-slate-200" },
  general: { label: "General", color: "bg-gray-100 text-gray-800 border-gray-200" }
};

const SIGNIFICANCE_CONFIG = {
  critical: { label: "Critical", color: "bg-red-500", textColor: "text-red-700", borderColor: "border-l-red-500" },
  important: { label: "Important", color: "bg-orange-500", textColor: "text-orange-700", borderColor: "border-l-orange-500" },
  normal: { label: "Normal", color: "bg-blue-500", textColor: "text-blue-700", borderColor: "border-l-blue-500" },
  minor: { label: "Minor", color: "bg-gray-400", textColor: "text-gray-600", borderColor: "border-l-gray-400" }
};

const PERSPECTIVE_CONFIG = {
  prosecution: { label: "Prosecution", color: "bg-red-50 text-red-700 border-red-300" },
  defence: { label: "Defence", color: "bg-green-50 text-green-700 border-green-300" },
  neutral: { label: "Neutral", color: "bg-slate-50 text-slate-700 border-slate-300" }
};

const Timeline = ({ 
  events, 
  documents = [], 
  grounds = [],
  caseId,
  caseInfo,
  onDeleteEvent, 
  onEditEvent,
  onExportPDF,
  onAnalyse,
  onReorderEvent,
  analyzing = false
}) => {
  const [searchQuery, setSearchQuery] = useState("");
  const [categoryFilter, setCategoryFilter] = useState("all");
  const [significanceFilter, setSignificanceFilter] = useState("all");
  const [perspectiveFilter, setPerspectiveFilter] = useState("all");
  const [showContestedOnly, setShowContestedOnly] = useState(false);
  const [expandedEvents, setExpandedEvents] = useState(new Set());

  // Create lookup maps
  const docMap = useMemo(() => {
    const map = {};
    documents.forEach(d => { map[d.document_id] = d; });
    return map;
  }, [documents]);

  const groundMap = useMemo(() => {
    const map = {};
    grounds.forEach(g => { map[g.ground_id] = g; });
    return map;
  }, [grounds]);

  // Filter events
  const filteredEvents = useMemo(() => {
    return events.filter(event => {
      // Search filter
      if (searchQuery) {
        const query = searchQuery.toLowerCase();
        const matchesSearch = 
          event.title?.toLowerCase().includes(query) ||
          event.description?.toLowerCase().includes(query) ||
          event.source_citation?.toLowerCase().includes(query) ||
          event.participants?.some(p => p.name?.toLowerCase().includes(query));
        if (!matchesSearch) return false;
      }
      
      // Category filter
      if (categoryFilter !== "all" && event.event_category !== categoryFilter) {
        return false;
      }
      
      // Significance filter
      if (significanceFilter !== "all" && event.significance !== significanceFilter) {
        return false;
      }
      
      // Perspective filter
      if (perspectiveFilter !== "all" && event.perspective !== perspectiveFilter) {
        return false;
      }
      
      // Contested filter
      if (showContestedOnly && !event.is_contested) {
        return false;
      }
      
      return true;
    });
  }, [events, searchQuery, categoryFilter, significanceFilter, perspectiveFilter, showContestedOnly]);

  /* DO_NOT_UNDO — formatDate handles year-only ("2018"), year-month ("2018-06"), and
     full ISO dates. Never convert year-only to "Mon, 1 Jan" — display just the year. */
  const formatDate = (dateStr) => {
    if (!dateStr) return "Unknown date";
    const s = String(dateStr).trim();
    // Year-only: "2018" or "2022" — display just the year
    if (/^\d{4}$/.test(s)) return s;
    // Year-month only: "2018-06" — display month + year
    if (/^\d{4}-\d{2}$/.test(s)) {
      const [y, m] = s.split("-");
      const d = new Date(Number(y), Number(m) - 1, 1);
      return d.toLocaleDateString("en-AU", { month: "short", year: "numeric" });
    }
    const date = new Date(s);
    if (isNaN(date.getTime())) return s;
    return date.toLocaleDateString("en-AU", {
      weekday: "short",
      day: "numeric",
      month: "short",
      year: "numeric"
    });
  };

  const toggleExpanded = (eventId) => {
    const newExpanded = new Set(expandedEvents);
    if (newExpanded.has(eventId)) {
      newExpanded.delete(eventId);
    } else {
      newExpanded.add(eventId);
    }
    setExpandedEvents(newExpanded);
  };

  const escapeHtml = (value = "") => String(value)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/\"/g, "&quot;")
    .replace(/'/g, "&#39;");

  const buildTimelinePrintHtml = () => {
    const previewDate = new Date().toLocaleDateString("en-AU");
    const footerLabel = `Criminal Appeal Case Management - Timeline on ${caseInfo?.defendant_name || "Appellant"} - ${previewDate}`;
    const footerMessage = "Created and Designed by Deb King — Thank you for using the tool. Good luck with the appeal process.";
    const eventsMarkup = filteredEvents.map((event) => {
      const catConfig = EVENT_CATEGORIES[event.event_category] || EVENT_CATEGORIES.general;
      const sigConfig = SIGNIFICANCE_CONFIG[event.significance] || SIGNIFICANCE_CONFIG.normal;
      const perspConfig = PERSPECTIVE_CONFIG[event.perspective] || PERSPECTIVE_CONFIG.neutral;
      const linkedDocs = (event.linked_documents || []).map((docId) => docMap[docId]?.filename || docId);
      const linkedGrounds = (event.related_grounds || []).map((groundId) => groundMap[groundId]?.title || groundId);
      const participants = event.participants || [];

      return `
        <section class="timeline-print-event">
          <div class="timeline-print-heading">
            <div>
              <div class="timeline-print-meta-row">
                <span class="timeline-pill">${escapeHtml(catConfig.label)}</span>
                <span class="timeline-pill timeline-pill-alt">${escapeHtml(sigConfig.label)}</span>
                ${event.perspective !== 'neutral' ? `<span class="timeline-pill timeline-pill-neutral">${escapeHtml(perspConfig.label)}</span>` : ""}
                ${event.is_contested ? `<span class="timeline-pill timeline-pill-contested">Contested</span>` : ""}
              </div>
              <h2>${escapeHtml(event.title || "Untitled event")}</h2>
              <p class="timeline-print-subtitle">${escapeHtml(EVENT_TYPE_LABELS[event.event_type] || event.event_type || "Event")} • ${escapeHtml(formatDate(event.event_date))}</p>
            </div>
          </div>
          ${event.description ? `<div class="timeline-print-block"><h3>Description</h3>${renderMarkdownToHtml(event.description)}</div>` : ""}
          ${event.is_contested && event.contested_details ? `<div class="timeline-print-block timeline-print-alert"><h3>Contested Details</h3>${renderMarkdownToHtml(event.contested_details)}</div>` : ""}
          ${event.source_citation ? `<div class="timeline-print-block"><h3>Source</h3><p>${escapeHtml(event.source_citation)}</p></div>` : ""}
          ${participants.length ? `<div class="timeline-print-block"><h3>Participants</h3><ul>${participants.map((participant) => `<li>${escapeHtml(participant.name || "Unnamed participant")}${participant.role ? ` (${escapeHtml(participant.role)})` : ""}</li>`).join("")}</ul></div>` : ""}
          ${linkedDocs.length ? `<div class="timeline-print-block"><h3>Linked Documents</h3><ul>${linkedDocs.map((item) => `<li>${escapeHtml(item)}</li>`).join("")}</ul></div>` : ""}
          ${linkedGrounds.length ? `<div class="timeline-print-block"><h3>Related Grounds of Appeal</h3><ul>${linkedGrounds.map((item) => `<li>${escapeHtml(item)}</li>`).join("")}</ul></div>` : ""}
          ${event.inconsistency_notes ? `<div class="timeline-print-block timeline-print-warn"><h3>Inconsistency Notes</h3>${renderMarkdownToHtml(event.inconsistency_notes)}</div>` : ""}
        </section>
      `;
    }).join("");

    // CANONICAL-ONLY: single buildExportHtml() call. No HTML shell, no @page,
    // no footer CSS. Disclaimer + branding emitted by buildExportHtml().
    const bodyHtml = `
  <div class="timeline-print-shell">
    <div class="timeline-print-header">
      <p class="timeline-print-kicker">Timeline</p>
      <h1>${escapeHtml(caseInfo?.title || "Case Timeline")}</h1>
      <p>${escapeHtml(caseInfo?.defendant_name || "")} ${caseInfo?.court ? `• ${escapeHtml(caseInfo.court)}` : ""} ${caseInfo?.case_number ? `• ${escapeHtml(caseInfo.case_number)}` : ""}</p>
      <p>${filteredEvents.length} event${filteredEvents.length === 1 ? "" : "s"} included.</p>
    </div>
    ${eventsMarkup || `<p>No timeline events available.</p>`}
  </div>`;

    const extraStyles = `
    .timeline-print-shell { max-width: 820px; margin: 0 auto; background: #ffffff; padding: 12px 16px; }
    .timeline-print-header { border-bottom: 1.2pt solid #1e3a8a; padding-bottom: 6pt; margin-bottom: 8pt; }
    .timeline-print-kicker { margin: 0 0 2px; font-weight: 800; letter-spacing: 0.14em; text-transform: uppercase; color: #1d4ed8; }
    .timeline-print-event { padding: 8pt 0; border-bottom: 0.5pt solid #cbd5e1; page-break-inside: auto; break-inside: auto; orphans: 3; widows: 3; }
    .timeline-print-subtitle { margin: 0 0 6pt; color: #475569; }
    .timeline-print-meta-row { display: flex; flex-wrap: wrap; gap: 4px; margin-bottom: 6pt; }
    .timeline-pill { display: inline-flex; align-items: center; padding: 2px 8px; border-radius: 999px; background: #dbeafe; color: #1d4ed8; font-weight: 700;
      -webkit-print-color-adjust: exact !important; print-color-adjust: exact !important; }
    .timeline-pill-alt { background: #eff6ff; color: #1d4ed8; }
    .timeline-pill-neutral { background: #f1f5f9; color: #334155; }
    .timeline-pill-contested { background: #fee2e2; color: #b91c1c; }
    .timeline-print-block { margin-top: 6pt; }
    .timeline-print-alert { background: #eff6ff; border: 1px solid #bfdbfe; border-radius: 6px; padding: 6px 10px; }
    .timeline-print-warn { background: #fef2f2; border: 1px solid #fecaca; border-radius: 6px; padding: 6px 10px; }
    @media print { .timeline-print-shell { max-width: none; margin: 0; padding: 0; } }`;

    return buildExportHtml({
      title: `${caseInfo?.title || "Case"} — Timeline`,
      docLabel: "Timeline of Events",
      defendantName: caseInfo?.defendant_name,
      caseNumber: caseInfo?.case_number,
      accentColor: "#1e3a8a",
      extraStyles,
      bodyHtml,
    });
  };

  const openTimelinePrintPreview = (mode = "print") => {
    const html = buildTimelinePrintHtml();
    localStorage.setItem(
      "document-preview-payload",
      JSON.stringify({
        html,
        mode,
        title: `${caseInfo?.title || "Case"} Timeline`,
        source: "timeline",
        returnTo: `/cases/${caseId}?tab=timeline`,
        createdAt: Date.now(),
      })
    );
    window.location.assign(`${window.location.origin}/document-preview?mode=${mode}`);
  };

  // Stats
  const stats = useMemo(() => ({
    total: events.length,
    critical: events.filter(e => e.significance === 'critical').length,
    contested: events.filter(e => e.is_contested).length,
    prosecution: events.filter(e => e.perspective === 'prosecution').length,
    defence: events.filter(e => e.perspective === 'defence').length
  }), [events]);

  return (
    <div className="space-y-4" data-testid="enhanced-timeline">
      {/* Stats Bar */}
      <div className="grid grid-cols-5 gap-2 p-3 bg-slate-50 rounded-lg text-center text-sm">
        <div>
          <div className="font-semibold text-slate-900">{stats.total}</div>
          <div className="text-slate-500 text-xs">Total</div>
        </div>
        <div>
          <div className="font-semibold text-red-600">{stats.critical}</div>
          <div className="text-slate-500 text-xs">Critical</div>
        </div>
        <div>
          <div className="font-semibold text-red-600">{stats.contested}</div>
          <div className="text-slate-500 text-xs">Contested</div>
        </div>
        <div>
          <div className="font-semibold text-red-500">{stats.prosecution}</div>
          <div className="text-slate-500 text-xs">Prosecution</div>
        </div>
        <div>
          <div className="font-semibold text-green-600">{stats.defence}</div>
          <div className="text-slate-500 text-xs">Defence</div>
        </div>
      </div>

      {/* Filters */}
      <div className="flex flex-wrap gap-2 items-center p-3 bg-white border border-slate-200 rounded-lg">
        <div className="relative flex-1 min-w-[200px]">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400" />
          <Input
            placeholder="Search events, participants, sources..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="pl-9"
            data-testid="timeline-search"
          />
        </div>
        
        <Select value={categoryFilter} onValueChange={setCategoryFilter}>
          <SelectTrigger className="w-[140px]" data-testid="category-filter">
            <Filter className="w-4 h-4 mr-2" />
            <SelectValue placeholder="Category" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="all">All Categories</SelectItem>
            {Object.entries(EVENT_CATEGORIES).map(([key, { label }]) => (
              <SelectItem key={key} value={key}>{label}</SelectItem>
            ))}
          </SelectContent>
        </Select>
        
        <Select value={significanceFilter} onValueChange={setSignificanceFilter}>
          <SelectTrigger className="w-[130px]" data-testid="significance-filter">
            <SelectValue placeholder="Significance" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="all">All Levels</SelectItem>
            <SelectItem value="critical">Critical</SelectItem>
            <SelectItem value="important">Important</SelectItem>
            <SelectItem value="normal">Normal</SelectItem>
            <SelectItem value="minor">Minor</SelectItem>
          </SelectContent>
        </Select>
        
        <Select value={perspectiveFilter} onValueChange={setPerspectiveFilter}>
          <SelectTrigger className="w-[130px]" data-testid="perspective-filter">
            <Scale className="w-4 h-4 mr-2" />
            <SelectValue placeholder="Perspective" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="all">All Sides</SelectItem>
            <SelectItem value="prosecution">Prosecution</SelectItem>
            <SelectItem value="defence">Defence</SelectItem>
            <SelectItem value="neutral">Neutral</SelectItem>
          </SelectContent>
        </Select>
        
        <Button
          variant={showContestedOnly ? "default" : "outline"}
          size="sm"
          onClick={() => setShowContestedOnly(!showContestedOnly)}
          className={showContestedOnly ? "bg-blue-500 hover:bg-red-600" : ""}
          data-testid="contested-filter"
        >
          <AlertTriangle className="w-4 h-4 mr-1" />
          Contested
        </Button>
        
        <div className="flex gap-2 ml-auto">
          <Button
            variant="outline"
            size="sm"
            onClick={onAnalyse}
            disabled={analyzing || events.length < 2}
            data-testid="analyse-timeline-btn"
          >
            {analyzing ? "Analysing..." : "AI Analysis"}
          </Button>
          <Button
            size="sm"
            onClick={() => openTimelinePrintPreview("print")}
            className="bg-blue-700 text-white hover:bg-blue-600"
            data-testid="print-timeline-btn"
          >
            <Printer className="w-4 h-4 mr-1" />
            Print
          </Button>
          <Button
            variant="outline"
            size="sm"
            onClick={onExportPDF}
            data-testid="export-timeline-pdf"
          >
            <Download className="w-4 h-4 mr-1" />
            Export PDF
          </Button>
          <Button
            variant="outline"
            size="sm"
            onClick={() => {
              const html = buildTimelinePrintHtml();
              localStorage.setItem("document-preview-payload", JSON.stringify({ html, title: "Timeline — Word View", mode: "word", returnTo: window.location.pathname, createdAt: Date.now() }));
              window.location.assign(`${window.location.origin}/document-preview?mode=word`);
            }}
            data-testid="export-timeline-word"
          >
            <Download className="w-4 h-4 mr-1" />
            Word
          </Button>
        </div>
      </div>

      {/* Results count */}
      <div className="text-sm text-slate-500">
        Showing {filteredEvents.length} of {events.length} events
      </div>

      {/* Timeline */}
      <div className="relative pl-8 py-4">
        {/* Vertical line */}
        <div className="absolute left-3 top-0 bottom-0 w-0.5 bg-slate-200"></div>

        <div className="space-y-4">
          {filteredEvents.map((event) => {
            const sigConfig = SIGNIFICANCE_CONFIG[event.significance] || SIGNIFICANCE_CONFIG.normal;
            const perspConfig = PERSPECTIVE_CONFIG[event.perspective] || PERSPECTIVE_CONFIG.neutral;
            const catConfig = EVENT_CATEGORIES[event.event_category] || EVENT_CATEGORIES.general;
            const isExpanded = expandedEvents.has(event.event_id);
            
            return (
              <div 
                key={event.event_id} 
                className="relative group"
                data-testid={`timeline-event-${event.event_id}`}
              >
                {/* Significance dot */}
                <div className={`absolute -left-5 w-4 h-4 rounded-full border-2 border-white shadow-sm ${sigConfig.color}`}></div>

                {/* Event card */}
                <div className={`bg-white rounded-lg border border-slate-200 ml-4 shadow-sm hover:shadow-md transition-shadow overflow-hidden border-l-4 ${sigConfig.borderColor}`}>
                  <Collapsible open={isExpanded} onOpenChange={() => toggleExpanded(event.event_id)}>
                    {/* Header - always visible */}
                    <div className="p-4">
                      <div className="flex items-start justify-between">
                        <div className="flex-1">
                          {/* Badges row */}
                          <div className="flex flex-wrap items-center gap-2 mb-2">
                            <Badge variant="outline" className={catConfig.color}>
                              {catConfig.label}
                            </Badge>
                            <Badge variant="outline" className={`${sigConfig.textColor} bg-opacity-10`}>
                              {sigConfig.label}
                            </Badge>
                            {event.perspective !== 'neutral' && (
                              <Badge variant="outline" className={perspConfig.color}>
                                {perspConfig.label}
                              </Badge>
                            )}
                            {event.is_contested && (
                              <Badge variant="outline" className="bg-blue-50 text-blue-700 border-blue-300">
                                <AlertTriangle className="w-3 h-3 mr-1" />
                                Contested
                              </Badge>
                            )}
                            <span className="text-sm text-slate-500 font-mono ml-auto">
                              {formatDate(event.event_date)}
                            </span>
                          </div>
                          
                          {/* Title */}
                          <h4 className="font-semibold text-slate-900 text-lg leading-tight">
                            {auSpelling(event.title)}
                          </h4>
                          
                          {/* Type */}
                          <p className="text-sm text-slate-500 mt-1">
                            {EVENT_TYPE_LABELS[event.event_type] || event.event_type}
                          </p>
                          
                          {/* Quick indicators */}
                          <div className="flex items-center gap-3 mt-2 text-xs text-slate-400">
                            {event.linked_documents?.length > 0 && (
                              <span className="flex items-center gap-1">
                                <FileText className="w-3 h-3" />
                                {event.linked_documents.length} doc{event.linked_documents.length > 1 ? 's' : ''}
                              </span>
                            )}
                            {event.participants?.length > 0 && (
                              <span className="flex items-center gap-1">
                                <Users className="w-3 h-3" />
                                {event.participants.length} participant{event.participants.length > 1 ? 's' : ''}
                              </span>
                            )}
                            {event.related_grounds?.length > 0 && (
                              <span className="flex items-center gap-1">
                                <Link2 className="w-3 h-3" />
                                {event.related_grounds.length} ground{event.related_grounds.length > 1 ? 's' : ''}
                              </span>
                            )}
                          </div>
                        </div>
                        
                        {/* Actions */}
                        <div className="flex items-center gap-1 ml-2">
                          <CollapsibleTrigger asChild>
                            <Button variant="ghost" size="sm" className="text-slate-400 hover:text-slate-600">
                              {isExpanded ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
                            </Button>
                          </CollapsibleTrigger>
                          <Button
                            variant="ghost"
                            size="sm"
                            onClick={() => onDeleteEvent(event.event_id)}
                            className="opacity-100 md:opacity-0 md:group-hover:opacity-100 text-red-600 hover:text-red-700 hover:bg-red-50"
                            data-testid={`delete-event-${event.event_id}`}
                          >
                            <Trash2 className="w-4 h-4" />
                          </Button>
                          {onReorderEvent && (
                            <>
                              <Button
                                variant="ghost"
                                size="sm"
                                onClick={() => onReorderEvent(event.event_id, "up")}
                                className="opacity-100 md:opacity-0 md:group-hover:opacity-100 text-blue-600 hover:text-blue-700 hover:bg-blue-50"
                                data-testid={`move-up-${event.event_id}`}
                                title="Move up"
                              >
                                <ArrowUp className="w-4 h-4" />
                              </Button>
                              <Button
                                variant="ghost"
                                size="sm"
                                onClick={() => onReorderEvent(event.event_id, "down")}
                                className="opacity-100 md:opacity-0 md:group-hover:opacity-100 text-blue-600 hover:text-blue-700 hover:bg-blue-50"
                                data-testid={`move-down-${event.event_id}`}
                                title="Move down"
                              >
                                <ArrowDown className="w-4 h-4" />
                              </Button>
                            </>
                          )}
                        </div>
                      </div>
                    </div>
                    
                    {/* Expanded content */}
                    <CollapsibleContent>
                      <div className="px-4 pb-4 pt-0 border-t border-slate-100 space-y-4">
                        {/* Description */}
                        {event.description && (
                          <div>
                            <h5 className="text-xs font-medium text-slate-500 uppercase tracking-wide mb-1">Description</h5>
                            <p className="text-slate-700 text-sm leading-relaxed whitespace-pre-wrap">
                              {auSpelling(event.description)}
                            </p>
                          </div>
                        )}
                        
                        {/* Contested details */}
                        {event.is_contested && event.contested_details && (
                          <div className="bg-blue-50 p-3 rounded-lg border border-blue-200">
                            <h5 className="text-xs font-medium text-blue-700 uppercase tracking-wide mb-1 flex items-center gap-1">
                              <AlertTriangle className="w-3 h-3" />
                              Contested Details
                            </h5>
                            <p className="text-blue-800 text-sm">{event.contested_details}</p>
                          </div>
                        )}
                        
                        {/* Source citation */}
                        {event.source_citation && (
                          <div>
                            <h5 className="text-xs font-medium text-slate-500 uppercase tracking-wide mb-1">Source</h5>
                            <p className="text-slate-600 text-sm italic">{event.source_citation}</p>
                          </div>
                        )}
                        
                        {/* Participants */}
                        {event.participants?.length > 0 && (
                          <div>
                            <h5 className="text-xs font-medium text-slate-500 uppercase tracking-wide mb-2">Participants</h5>
                            <div className="flex flex-wrap gap-2">
                              {event.participants.map((p, i) => (
                                <Badge key={i} variant="secondary" className="bg-slate-100">
                                  <Users className="w-3 h-3 mr-1" />
                                  {p.name} {p.role && <span className="text-slate-400 ml-1">({p.role})</span>}
                                </Badge>
                              ))}
                            </div>
                          </div>
                        )}
                        
                        {/* Linked Documents */}
                        {event.linked_documents?.length > 0 && (
                          <div>
                            <h5 className="text-xs font-medium text-slate-500 uppercase tracking-wide mb-2">Linked Documents</h5>
                            <div className="flex flex-wrap gap-2">
                              {event.linked_documents.map((docId) => {
                                const doc = docMap[docId];
                                return (
                                  <Badge key={docId} variant="outline" className="bg-blue-50 text-blue-700 border-blue-200">
                                    <FileText className="w-3 h-3 mr-1" />
                                    {doc?.filename || docId}
                                  </Badge>
                                );
                              })}
                            </div>
                          </div>
                        )}
                        
                        {/* Related Grounds */}
                        {event.related_grounds?.length > 0 && (
                          <div>
                            <h5 className="text-xs font-medium text-slate-500 uppercase tracking-wide mb-2">Related Grounds of Appeal</h5>
                            <div className="flex flex-wrap gap-2">
                              {event.related_grounds.map((groundId) => {
                                const ground = groundMap[groundId];
                                return (
                                  <Badge key={groundId} variant="outline" className="bg-purple-50 text-purple-700 border-purple-200">
                                    <Scale className="w-3 h-3 mr-1" />
                                    {ground?.title || groundId}
                                  </Badge>
                                );
                              })}
                            </div>
                          </div>
                        )}
                        
                        {/* Inconsistency notes */}
                        {event.inconsistency_notes && (
                          <div className="bg-red-50 p-3 rounded-lg border border-red-200">
                            <h5 className="text-xs font-medium text-red-700 uppercase tracking-wide mb-1">Inconsistency Notes</h5>
                            <p className="text-red-800 text-sm">{event.inconsistency_notes}</p>
                          </div>
                        )}
                      </div>
                    </CollapsibleContent>
                  </Collapsible>
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {filteredEvents.length === 0 && events.length > 0 && (
        <div className="text-center py-8 text-slate-500">
          No events match your filters. Try adjusting the filter criteria.
        </div>
      )}
    </div>
  );
};

export default Timeline;
