/* ========================================================================
   DO NOT UNDO — ENTIRE FILE PROTECTED
   All features, functions, styles, and content in this file are approved
   and must be preserved. Do not remove, rename, or refactor any code.
   ======================================================================== */
import { useState, useEffect } from "react";
import axios from "axios";
import { API } from "../App";
import { 
  TrendingUp, AlertCircle, FileText, Clock, CheckCircle2,
  ChevronRight, Gavel, Shield, Sparkles
} from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "./ui/card";
import { Progress } from "./ui/progress";

const CaseStrengthMeter = ({ caseId }) => {
  const [strength, setStrength] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchStrength = async () => {
      try {
        const response = await axios.get(`${API}/cases/${caseId}/strength`);
        setStrength(response.data);
      } catch (error) {
        console.error("Failed to fetch case strength:", error);
      } finally {
        setLoading(false);
      }
    };

    if (caseId) fetchStrength();
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [caseId]);

  if (loading) {
    return (
      <Card className="bg-white border-slate-200">
        <CardContent className="p-6">
          <div className="animate-pulse space-y-4">
            <div className="h-4 bg-slate-100 rounded w-1/3"></div>
            <div className="h-24 bg-slate-100 rounded-full w-24 mx-auto"></div>
            <div className="h-4 bg-slate-100 rounded"></div>
            <div className="h-4 bg-slate-100 rounded"></div>
          </div>
        </CardContent>
      </Card>
    );
  }

  if (!strength) return null;

  const readinessLevel = strength.readiness_level || strength.rating || "Developing";
  const readinessScore = strength.readiness_score ?? strength.overall_score ?? 0;
  const assessmentNote = strength.assessment_note || strength.disclaimer || "This score reflects case preparation and documentation completeness. It is not a determination of legal merit or likelihood of appeal success.";

  const getScoreGradient = (score) => {
    if (score >= 75) return "from-emerald-500 to-emerald-600";
    if (score >= 50) return "from-blue-500 to-red-600";
    if (score >= 25) return "from-orange-500 to-orange-600";
    return "from-red-500 to-red-600";
  };

  const getScoreBg = (score) => {
    if (score >= 75) return "bg-emerald-100 text-emerald-700";
    if (score >= 50) return "bg-blue-100 text-blue-700";
    if (score >= 25) return "bg-orange-100 text-orange-700";
    return "bg-red-100 text-red-700";
  };

  const getProgressBg = (score) => {
    if (score >= 75) return "bg-emerald-500";
    if (score >= 50) return "bg-blue-500";
    if (score >= 25) return "bg-orange-500";
    return "bg-red-500";
  };

  const breakdownItems = [
    {
      label: "Grounds Review Progress",
      icon: Gavel,
      score: strength.breakdown.grounds.score,
      detail: `${strength.breakdown.grounds.strong} strong, ${strength.breakdown.grounds.moderate} moderate, ${strength.breakdown.grounds.weak} weak`
    },
    {
      label: "Documentation Completeness",
      icon: FileText,
      score: strength.breakdown.documentation.score,
      detail: `${strength.breakdown.documentation.with_text}/${strength.breakdown.documentation.total_docs} docs with extracted text`
    },
    {
      label: "Timeline Development",
      icon: Clock,
      score: strength.breakdown.timeline.score,
      detail: `${strength.breakdown.timeline.event_count} events documented`
    },
    {
      label: "Preparation Checklist Completion",
      icon: CheckCircle2,
      score: strength.breakdown.preparation.score,
      detail: `${strength.breakdown.preparation.completed}/${strength.breakdown.preparation.total} checklist items`
    }
  ];

  return (
    <Card className="bg-white border-slate-200 shadow-sm" data-testid="case-strength-meter">
      <CardHeader className="pb-2">
        <CardTitle className="text-xl sm:text-2xl flex items-center gap-3" style={{ fontFamily: 'Crimson Pro, serif' }}>
          <div className="w-10 h-10 rounded-lg bg-gradient-to-br from-blue-500 to-red-600 flex items-center justify-center">
            <TrendingUp className="w-5 h-5 text-white" />
          </div>
          Case Readiness Score
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-6">
        {/* Readiness disclaimer */}
        <p className="text-xs text-slate-500 italic leading-tight">
          {assessmentNote}
        </p>
        {/* Appeal Preparation Readiness summary */}
        <div className="rounded border border-slate-200 p-4 bg-slate-50">
          <div className="text-sm font-semibold text-slate-700">Appeal Preparation Readiness</div>
          <div className="text-3xl font-bold mt-1 text-slate-900">{readinessScore}/100</div>
          <div className="mt-1 text-sm text-slate-600">{readinessLevel}</div>
        </div>
        {/* Overall Score - Circular Display */}
        <div className="flex flex-col items-center py-4">
          <div className="relative">
            {/* Outer ring */}
            <div className={`w-32 h-32 rounded-full bg-gradient-to-br ${getScoreGradient(readinessScore)} p-1 shadow-lg`}>
              <div className="w-full h-full rounded-full bg-white flex items-center justify-center">
                <div className="text-center">
                  <span className="text-4xl font-bold text-slate-900">{readinessScore}</span>
                  <span className="text-lg text-slate-600">/100</span>
                </div>
              </div>
            </div>
            {/* Sparkle indicator */}
            {readinessScore >= 75 && (
              <div className="absolute -top-1 -right-1 w-8 h-8 bg-emerald-500 rounded-full flex items-center justify-center shadow-lg">
                <Sparkles className="w-4 h-4 text-white" />
              </div>
            )}
          </div>
          <p className={`mt-3 px-4 py-1.5 rounded-full text-sm font-semibold ${getScoreBg(readinessScore)}`}>
            {readinessLevel}
          </p>
        </div>

        {/* Breakdown Bars */}
        <div className="space-y-4">
          {breakdownItems.map((item, index) => (
            <div key={index} className="space-y-1.5">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <item.icon className="w-4 h-4 text-slate-600" />
                  <span className="text-sm font-medium text-slate-900">{item.label}</span>
                </div>
                <span className={`text-sm font-bold ${getScoreBg(item.score).split(' ')[0]} px-2 py-0.5 rounded-md ${getScoreBg(item.score)}`}>
                  {item.score}%
                </span>
              </div>
              <div className="h-2.5 bg-slate-100 rounded-full overflow-hidden">
                <div 
                  className={`h-full rounded-full transition-all duration-500 ${getProgressBg(item.score)}`}
                  style={{ width: `${item.score}%` }}
                />
              </div>
              <p className="text-xs text-slate-600">{item.detail}</p>
            </div>
          ))}
        </div>

        {/* Recommendations */}
        {strength.recommendations.length > 0 && (
          <div className="bg-blue-50 border border-blue-200 rounded-xl p-4">
            <p className="text-sm font-semibold text-blue-800 mb-3 flex items-center gap-2">
              <AlertCircle className="w-4 h-4" />
              Recommendations to Improve Readiness
            </p>
            <ul className="space-y-2">
              {strength.recommendations.map((rec, i) => (
                <li key={i} className="flex items-start gap-2 text-sm text-blue-700">
                  <ChevronRight className="w-4 h-4 shrink-0 mt-0.5" />
                  {rec}
                </li>
              ))}
            </ul>
          </div>
        )}

        {/* Readiness indicator */}
        {readinessScore >= 75 && (
          <div className="bg-emerald-50 border border-emerald-200 rounded-xl p-4 text-center">
            <Shield className="w-8 h-8 text-emerald-600 mx-auto mb-2" />
            <p className="text-sm font-semibold text-emerald-800">
              Thorough Case Preparation
            </p>
            <p className="text-xs text-emerald-700 mt-1">
              Case documentation and preparation appear comprehensive. All identified grounds require independent assessment by qualified counsel.
            </p>
          </div>
        )}
      </CardContent>
    </Card>
  );
};

export default CaseStrengthMeter;
