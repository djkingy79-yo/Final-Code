/* DO NOT UNDO — GroundsOfMerit component. All features in this file are approved and must be preserved. */
import { useState } from "react";
import { 
  Scale, Trash2, ChevronRight, Search, Loader2, 
  AlertTriangle, CheckCircle, XCircle, Sparkles,
  BookOpen, Gavel, FileText, Lock, CreditCard, ExternalLink
} from "lucide-react";
import { Button } from "./ui/button";
import { Input } from "./ui/input";
import { Card, CardContent } from "./ui/card";
import { Badge } from "./ui/badge";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
} from "./ui/dialog";
import { ScrollArea } from "./ui/scroll-area";
import PaymentModal from "./PaymentModal";

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

const GROUND_TYPE_COLORS = {
  procedural_error: "bg-blue-50 text-blue-700 border-blue-200",
  fresh_evidence: "bg-emerald-50 text-emerald-700 border-emerald-200",
  miscarriage_of_justice: "bg-red-50 text-red-700 border-red-200",
  sentencing_error: "bg-blue-50 text-blue-700 border-blue-200",
  judicial_error: "bg-purple-50 text-purple-700 border-purple-200",
  ineffective_counsel: "bg-orange-50 text-orange-700 border-orange-200",
  prosecution_misconduct: "bg-rose-50 text-rose-700 border-rose-200",
  jury_irregularity: "bg-indigo-50 text-indigo-700 border-indigo-200",
  constitutional_violation: "bg-slate-50 text-slate-700 border-slate-200",
  other: "bg-gray-50 text-gray-700 border-gray-200"
};

const STRENGTH_CONFIG = {
  strong: { icon: CheckCircle, color: "text-emerald-600", bg: "bg-emerald-100", label: "Strong" },
  moderate: { icon: AlertTriangle, color: "text-red-600", bg: "bg-blue-100", label: "Moderate" },
  weak: { icon: XCircle, color: "text-red-600", bg: "bg-red-100", label: "Weak" }
};

const STATUS_CONFIG = {
  identified: { color: "bg-blue-100 text-blue-700", label: "Identified" },
  investigating: { color: "bg-blue-100 text-blue-700", label: "Investigating" },
  confirmed: { color: "bg-emerald-100 text-emerald-700", label: "Confirmed" },
  rejected: { color: "bg-red-100 text-red-700", label: "Rejected" }
};

const GroundsOfMerit = ({ 
  grounds, 
  groundsCount,
  isUnlocked,
  unlockPrice,
  caseId,
  onInvestigate, 
  onDelete, 
  investigating,
  selectedGround,
  setSelectedGround,
  onPaymentSuccess
}) => {
  const [showDetailDialog, setShowDetailDialog] = useState(false);
  const [detailGround, setDetailGround] = useState(null);
  const [showPaymentModal, setShowPaymentModal] = useState(false);
  /* DO NOT UNDO — Search box state for each ground. Uses object to track per-ground search visibility */
  const [searchOpen, setSearchOpen] = useState({});
  const [searchTerms, setSearchTerms] = useState({});

  const toggleSearch = (groundId) => {
    setSearchOpen(prev => ({ ...prev, [groundId]: !prev[groundId] }));
  };

  const handleCaselawSearch = (groundId, groundTitle) => {
    const query = searchTerms[groundId] || groundTitle;
    const encoded = encodeURIComponent(query);
    window.open(`https://www.austlii.edu.au/cgi-bin/sinosrch.cgi?method=auto&query=${encoded}`, '_blank');
  };

  const openGroundDetail = (ground) => {
    setDetailGround(ground);
    setShowDetailDialog(true);
  };

  const formatDate = (dateStr) => {
    if (!dateStr) return "N/A";
    return new Date(dateStr).toLocaleDateString("en-AU", {
      day: "numeric",
      month: "short",
      year: "numeric"
    });
  };

  // Format the analysis content with sections
  const formatAnalysis = (analysis) => {
    if (!analysis) return null;
    
    const sections = analysis.split(/(?=\d+\.\s+\*\*|(?:\n|\r\n)##\s+|\*\*[A-Z][A-Z\s]+\*\*)/g);
    
    return sections.map((section, idx) => {
      const headerMatch = section.match(/^(\d+\.\s+\*\*[^*]+\*\*|##\s+[^\n]+|\*\*[A-Z][A-Z\s]+\*\*)/);
      
      if (headerMatch) {
        const header = headerMatch[0]
          .replace(/^##\s+/, '')
          .replace(/\*\*/g, '')
          .replace(/^\d+\.\s+/, '')
          .trim();
        const body = section.substring(headerMatch[0].length).trim();
        
        return (
          <div key={idx} className="mb-6">
            <h4 
              className="text-lg font-semibold text-slate-900 mb-2 border-b border-slate-200 pb-1"
              style={{ fontFamily: 'Crimson Pro, serif' }}
            >
              {header}
            </h4>
            <div className="text-slate-700 leading-relaxed whitespace-pre-wrap text-sm">
              {body}
            </div>
          </div>
        );
      }
      
      return section.trim() ? (
        <div key={idx} className="text-slate-700 leading-relaxed whitespace-pre-wrap text-sm mb-4">
          {section}
        </div>
      ) : null;
    });
  };

  return (
    <div className="space-y-4" data-testid="grounds-container">
      {/* Paywall Banner when not unlocked */}
      {!isUnlocked && groundsCount > 0 && (
        <Card className="bg-gradient-to-r from-blue-50 to-orange-50 border-blue-200">
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-4">
                <div className="w-12 h-12 bg-blue-100 rounded-full flex items-center justify-center">
                  <Lock className="w-6 h-6 text-red-600" />
                </div>
                <div>
                  <h3 className="font-semibold text-slate-900 text-lg" style={{ fontFamily: 'Crimson Pro, serif' }}>
                    {groundsCount} Grounds of Merit Found!
                  </h3>
                  <p className="text-slate-600">
                    Unlock to see full details, evidence, and deep analysis for each ground.
                  </p>
                </div>
              </div>
              <Button 
                onClick={() => setShowPaymentModal(true)}
                className="bg-red-600 hover:bg-blue-700 text-white"
                data-testid="unlock-grounds-btn"
              >
                <CreditCard className="w-4 h-4 mr-2" />
                Unlock for ${unlockPrice?.toFixed(2)}
              </Button>
            </div>
          </CardContent>
        </Card>
      )}

      {grounds.length === 0 ? (
        <Card className="p-12 text-center">
          <Scale className="w-12 h-12 text-slate-300 mx-auto mb-4" />
          <h3 className="text-lg font-semibold text-slate-900 mb-2" style={{ fontFamily: 'Crimson Pro, serif' }}>
            No grounds of merit identified
          </h3>
          <p className="text-slate-600 mb-4">
            Use AI to automatically identify potential grounds or add them manually.
          </p>
        </Card>
      ) : (
        <div className="grid gap-4">
          {grounds.map((ground) => {
            const strengthConfig = STRENGTH_CONFIG[ground.strength] || STRENGTH_CONFIG.moderate;
            const StrengthIcon = strengthConfig.icon;
            const statusConfig = STATUS_CONFIG[ground.status] || STATUS_CONFIG.identified;
            
            return (
              <Card 
                key={ground.ground_id} 
                className={`card-hover group ${selectedGround?.ground_id === ground.ground_id ? 'ring-2 ring-blue-500' : ''}`}
                data-testid={`ground-${ground.ground_id}`}
              >
                <CardContent className="p-4">
                  <div className="flex items-start justify-between">
                    <div className="flex-1 cursor-pointer" onClick={() => openGroundDetail(ground)}>
                      <div className="flex items-center gap-2 flex-wrap mb-2">
                        <Badge variant="outline" className={GROUND_TYPE_COLORS[ground.ground_type] || GROUND_TYPE_COLORS.other}>
                          {GROUND_TYPE_LABELS[ground.ground_type] || ground.ground_type}
                        </Badge>
                        <Badge variant="outline" className={statusConfig.color}>
                          {statusConfig.label}
                        </Badge>
                        <div className={`flex items-center gap-1 px-2 py-0.5 rounded-full ${strengthConfig.bg}`}>
                          <StrengthIcon className={`w-3 h-3 ${strengthConfig.color}`} />
                          <span className={`text-xs font-medium ${strengthConfig.color}`}>
                            {strengthConfig.label}
                          </span>
                        </div>
                      </div>
                      
                      <h4 
                        className="font-semibold text-slate-900 text-lg group-hover:text-blue-700 transition-colors"
                        style={{ fontFamily: 'Crimson Pro, serif' }}
                      >
                        {ground.title}
                      </h4>
                      
                      {/* Show locked message or actual description */}
                      {!isUnlocked && ground.description === "*** UNLOCK TO VIEW ***" ? (
                        <div className="mt-2 p-3 bg-slate-100 rounded-lg border border-slate-200">
                          <div className="flex items-center gap-2 text-slate-500">
                            <Lock className="w-4 h-4" />
                            <span className="text-sm">Unlock to view full details</span>
                          </div>
                        </div>
                      ) : (
                        <p className="text-slate-600 mt-2 line-clamp-2">
                          {ground.description}
                        </p>
                      )}
                      
                      {/* Supporting Evidence Tags */}
                      {ground.supporting_evidence && ground.supporting_evidence.length > 0 && (
                        <div className="flex items-center gap-2 mt-3 flex-wrap">
                          <FileText className="w-4 h-4 text-slate-400" />
                          {ground.supporting_evidence.slice(0, 3).map((evidence, idx) => (
                            <span key={idx} className="text-xs bg-slate-100 px-2 py-1 rounded text-slate-600">
                              {evidence}
                            </span>
                          ))}
                          {ground.supporting_evidence.length > 3 && (
                            <span className="text-xs text-slate-500">
                              +{ground.supporting_evidence.length - 3} more
                            </span>
                          )}
                        </div>
                      )}
                      
                      {/* Law Sections Preview */}
                      {ground.law_sections && ground.law_sections.length > 0 && (
                        <div className="flex items-center gap-2 mt-2">
                          <BookOpen className="w-4 h-4 text-slate-400" />
                          <span className="text-xs text-slate-500">
                            {ground.law_sections.length} law section{ground.law_sections.length > 1 ? 's' : ''} identified
                          </span>
                        </div>
                      )}
                      
                      {/* Similar Cases Preview */}
                      {ground.similar_cases && ground.similar_cases.length > 0 && (
                        <div className="flex items-center gap-2 mt-1">
                          <Gavel className="w-4 h-4 text-slate-400" />
                          <span className="text-xs text-slate-500">
                            {ground.similar_cases.length} similar case{ground.similar_cases.length > 1 ? 's' : ''} found
                          </span>
                        </div>
                      )}
                      
                      <p className="text-xs text-slate-400 mt-3">
                        Added {formatDate(ground.created_at)}
                        {ground.deep_analysis && " • Has deep analysis"}
                      </p>
                    </div>
                    
                    <div className="flex items-center gap-1 ml-4 flex-shrink-0">
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => toggleSearch(ground.ground_id)}
                        className="text-green-700 border-green-200 hover:bg-green-50"
                        data-testid={`search-caselaw-toggle-${ground.ground_id}`}
                      >
                        <Search className="w-4 h-4 mr-1" />
                        Search
                      </Button>
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => onInvestigate(ground.ground_id)}
                        disabled={investigating === ground.ground_id}
                        className="text-blue-700 border-blue-200 hover:bg-blue-50"
                        data-testid={`investigate-${ground.ground_id}`}
                      >
                        {investigating === ground.ground_id ? (
                          <Loader2 className="w-4 h-4 animate-spin" />
                        ) : (
                          <>
                            <Sparkles className="w-4 h-4 mr-1" />
                            Investigate
                          </>
                        )}
                      </Button>
                      <Button
                        variant="destructive"
                        size="sm"
                        onClick={() => onDelete(ground.ground_id)}
                        className="bg-red-600 hover:bg-red-700 text-white"
                        data-testid={`delete-ground-${ground.ground_id}`}
                      >
                        <Trash2 className="w-4 h-4" />
                      </Button>
                    </div>
                  </div>

                  {/* DO NOT UNDO — Caselaw Search Box for each ground */}
                  {searchOpen[ground.ground_id] && (
                    <div className="mt-3 p-3 bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-800 rounded-lg" data-testid={`search-box-${ground.ground_id}`}>
                      <p className="text-xs font-semibold text-green-800 dark:text-green-200 mb-2">Search AustLII for cases related to this ground</p>
                      <div className="flex gap-2">
                        <Input
                          placeholder={ground.title || "Search caselaw..."}
                          value={searchTerms[ground.ground_id] || ""}
                          onChange={(e) => setSearchTerms(prev => ({ ...prev, [ground.ground_id]: e.target.value }))}
                          className="flex-1 text-sm"
                          data-testid={`search-input-${ground.ground_id}`}
                        />
                        <Button
                          size="sm"
                          onClick={() => handleCaselawSearch(ground.ground_id, ground.title)}
                          className="bg-green-600 hover:bg-green-700 text-white flex-shrink-0"
                          data-testid={`search-submit-${ground.ground_id}`}
                        >
                          <ExternalLink className="w-4 h-4 mr-1" />
                          Search
                        </Button>
                      </div>
                    </div>
                  )}
                </CardContent>
              </Card>
            );
          })}
        </div>
      )}

      {/* Ground Detail Dialog */}
      <Dialog open={showDetailDialog} onOpenChange={setShowDetailDialog}>
        <DialogContent className="max-w-4xl max-h-[90vh]">
          <DialogHeader>
            <DialogTitle style={{ fontFamily: 'Crimson Pro, serif' }} className="text-2xl flex items-center gap-3">
              <Scale className="w-6 h-6 text-red-600" />
              Ground of Merit Analysis
            </DialogTitle>
          </DialogHeader>
          
          {detailGround && (
            <ScrollArea className="max-h-[70vh] pr-4">
              <div className="space-y-6">
                {/* Header Info */}
                <div className="bg-slate-50 rounded-lg p-4 border border-slate-200">
                  <div className="flex items-center gap-2 flex-wrap mb-3">
                    <Badge variant="outline" className={GROUND_TYPE_COLORS[detailGround.ground_type] || GROUND_TYPE_COLORS.other}>
                      {GROUND_TYPE_LABELS[detailGround.ground_type] || detailGround.ground_type}
                    </Badge>
                    <Badge variant="outline" className={STATUS_CONFIG[detailGround.status]?.color}>
                      {STATUS_CONFIG[detailGround.status]?.label}
                    </Badge>
                    {(() => {
                      const cfg = STRENGTH_CONFIG[detailGround.strength] || STRENGTH_CONFIG.moderate;
                      const Icon = cfg.icon;
                      return (
                        <div className={`flex items-center gap-1 px-2 py-0.5 rounded-full ${cfg.bg}`}>
                          <Icon className={`w-3 h-3 ${cfg.color}`} />
                          <span className={`text-xs font-medium ${cfg.color}`}>{cfg.label}</span>
                        </div>
                      );
                    })()}
                  </div>
                  <h3 
                    className="text-xl font-bold text-slate-900"
                    style={{ fontFamily: 'Crimson Pro, serif' }}
                  >
                    {detailGround.title}
                  </h3>
                  <p className="text-slate-600 mt-2">{detailGround.description}</p>
                </div>

                {/* Supporting Evidence */}
                {detailGround.supporting_evidence && detailGround.supporting_evidence.length > 0 && (
                  <div>
                    <h4 className="font-semibold text-slate-900 mb-2 flex items-center gap-2">
                      <FileText className="w-4 h-4" />
                      Supporting Evidence
                    </h4>
                    <ul className="list-disc pl-5 space-y-1 text-slate-700">
                      {detailGround.supporting_evidence.map((ev, idx) => (
                        <li key={idx}>{ev}</li>
                      ))}
                    </ul>
                  </div>
                )}

                {/* Law Sections */}
                {detailGround.law_sections && detailGround.law_sections.length > 0 && (
                  <div>
                    <h4 className="font-semibold text-slate-900 mb-2 flex items-center gap-2">
                      <BookOpen className="w-4 h-4" />
                      Relevant Law Sections
                    </h4>
                    <div className="space-y-2">
                      {detailGround.law_sections.map((section, idx) => (
                        <div key={idx} className="bg-blue-50 border border-blue-200 rounded-lg p-3">
                          <div className="font-mono text-sm text-blue-800">
                            s.{section.section} {section.act}
                          </div>
                          <div className="text-xs text-blue-600 mt-1">
                            Jurisdiction: {section.jurisdiction}
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {/* Similar Cases */}
                {detailGround.similar_cases && detailGround.similar_cases.length > 0 && (
                  <div>
                    <h4 className="font-semibold text-slate-900 mb-2 flex items-center gap-2">
                      <Gavel className="w-4 h-4" />
                      Similar Cases
                    </h4>
                    <div className="space-y-2">
                      {detailGround.similar_cases.map((caseItem, idx) => (
                        <div key={idx} className="bg-blue-50 border border-blue-200 rounded-lg p-3">
                          <div className="font-medium text-blue-900">
                            {caseItem.case_name}
                          </div>
                          {caseItem.citation && (
                            <div className="font-mono text-xs text-blue-700 mt-1">
                              {caseItem.citation}
                            </div>
                          )}
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {/* Deep Analysis */}
                {detailGround.deep_analysis?.full_analysis && (
                  <div>
                    <h4 className="font-semibold text-slate-900 mb-3 flex items-center gap-2">
                      <Sparkles className="w-4 h-4 text-red-600" />
                      Deep Analysis
                      <span className="text-xs font-normal text-slate-500">
                        Generated {formatDate(detailGround.deep_analysis.investigated_at)}
                      </span>
                    </h4>
                    <div className="bg-white border border-slate-200 rounded-lg p-4">
                      {formatAnalysis(detailGround.deep_analysis.full_analysis)}
                    </div>
                  </div>
                )}

                {/* Basic Analysis (if no deep analysis) */}
                {!detailGround.deep_analysis?.full_analysis && detailGround.analysis && (
                  <div>
                    <h4 className="font-semibold text-slate-900 mb-2">Analysis</h4>
                    <div className="text-slate-700 whitespace-pre-wrap">
                      {detailGround.analysis}
                    </div>
                  </div>
                )}

                {/* No Analysis Yet */}
                {!detailGround.deep_analysis?.full_analysis && !detailGround.analysis && (
                  <div className="text-center py-8 bg-slate-50 rounded-lg border border-slate-200">
                    <Search className="w-10 h-10 text-slate-300 mx-auto mb-3" />
                    <p className="text-slate-600">
                      Click "Investigate" to run a deep AI analysis of this ground of merit.
                    </p>
                  </div>
                )}
              </div>
            </ScrollArea>
          )}
        </DialogContent>
      </Dialog>

      {/* Payment Modal */}
      <PaymentModal
        isOpen={showPaymentModal}
        onClose={() => setShowPaymentModal(false)}
        caseId={caseId}
        featureType="grounds_of_merit"
        price={unlockPrice}
        onPaymentSuccess={onPaymentSuccess}
      />
    </div>
  );
};

export default GroundsOfMerit;
