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
  }, [caseId]);

  if (loading) {
    return (
      <Card className="bg-card border-border">
        <CardContent className="p-6">
          <div className="animate-pulse space-y-4">
            <div className="h-4 bg-muted rounded w-1/3"></div>
            <div className="h-24 bg-muted rounded-full w-24 mx-auto"></div>
            <div className="h-4 bg-muted rounded"></div>
            <div className="h-4 bg-muted rounded"></div>
          </div>
        </CardContent>
      </Card>
    );
  }

  if (!strength) return null;

  const getScoreGradient = (score) => {
    if (score >= 75) return "from-emerald-500 to-emerald-600";
    if (score >= 50) return "from-blue-500 to-red-600";
    if (score >= 25) return "from-orange-500 to-orange-600";
    return "from-red-500 to-red-600";
  };

  const getScoreBg = (score) => {
    if (score >= 75) return "bg-emerald-100 dark:bg-emerald-900/30 text-emerald-700 dark:text-emerald-400";
    if (score >= 50) return "bg-blue-100 dark:bg-blue-900/30 text-blue-700 dark:text-blue-400";
    if (score >= 25) return "bg-orange-100 dark:bg-orange-900/30 text-orange-700 dark:text-orange-400";
    return "bg-red-100 dark:bg-red-900/30 text-red-700 dark:text-red-400";
  };

  const getProgressBg = (score) => {
    if (score >= 75) return "bg-emerald-500";
    if (score >= 50) return "bg-blue-500";
    if (score >= 25) return "bg-orange-500";
    return "bg-red-500";
  };

  const breakdownItems = [
    {
      label: "Grounds of Merit",
      icon: Gavel,
      score: strength.breakdown.grounds.score,
      detail: `${strength.breakdown.grounds.strong} strong, ${strength.breakdown.grounds.moderate} moderate, ${strength.breakdown.grounds.weak} weak`
    },
    {
      label: "Documentation",
      icon: FileText,
      score: strength.breakdown.documentation.score,
      detail: `${strength.breakdown.documentation.with_text}/${strength.breakdown.documentation.total_docs} docs with extracted text`
    },
    {
      label: "Timeline",
      icon: Clock,
      score: strength.breakdown.timeline.score,
      detail: `${strength.breakdown.timeline.event_count} events documented`
    },
    {
      label: "Preparation",
      icon: CheckCircle2,
      score: strength.breakdown.preparation.score,
      detail: `${strength.breakdown.preparation.completed}/${strength.breakdown.preparation.total} checklist items`
    }
  ];

  return (
    <Card className="bg-card border-border shadow-sm" data-testid="case-strength-meter">
      <CardHeader className="pb-2">
        <CardTitle className="text-lg flex items-center gap-2" style={{ fontFamily: 'Crimson Pro, serif' }}>
          <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-blue-500 to-red-600 flex items-center justify-center">
            <TrendingUp className="w-4 h-4 text-white" />
          </div>
          Case Strength Meter
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-6">
        {/* Overall Score - Circular Display */}
        <div className="flex flex-col items-center py-4">
          <div className="relative">
            {/* Outer ring */}
            <div className={`w-32 h-32 rounded-full bg-gradient-to-br ${getScoreGradient(strength.overall_score)} p-1 shadow-lg`}>
              <div className="w-full h-full rounded-full bg-card flex items-center justify-center">
                <div className="text-center">
                  <span className="text-4xl font-bold text-foreground">{strength.overall_score}</span>
                  <span className="text-lg text-muted-foreground">/100</span>
                </div>
              </div>
            </div>
            {/* Sparkle indicator */}
            {strength.overall_score >= 75 && (
              <div className="absolute -top-1 -right-1 w-8 h-8 bg-emerald-500 rounded-full flex items-center justify-center shadow-lg">
                <Sparkles className="w-4 h-4 text-white" />
              </div>
            )}
          </div>
          <p className={`mt-3 px-4 py-1.5 rounded-full text-sm font-semibold ${getScoreBg(strength.overall_score)}`}>
            {strength.rating}
          </p>
        </div>

        {/* Breakdown Bars */}
        <div className="space-y-4">
          {breakdownItems.map((item, index) => (
            <div key={index} className="space-y-1.5">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <item.icon className="w-4 h-4 text-muted-foreground" />
                  <span className="text-sm font-medium text-foreground">{item.label}</span>
                </div>
                <span className={`text-sm font-bold ${getScoreBg(item.score).split(' ')[0]} px-2 py-0.5 rounded-md ${getScoreBg(item.score)}`}>
                  {item.score}%
                </span>
              </div>
              <div className="h-2.5 bg-muted rounded-full overflow-hidden">
                <div 
                  className={`h-full rounded-full transition-all duration-500 ${getProgressBg(item.score)}`}
                  style={{ width: `${item.score}%` }}
                />
              </div>
              <p className="text-xs text-muted-foreground">{item.detail}</p>
            </div>
          ))}
        </div>

        {/* Recommendations */}
        {strength.recommendations.length > 0 && (
          <div className="bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-xl p-4">
            <p className="text-sm font-semibold text-blue-800 dark:text-blue-200 mb-3 flex items-center gap-2">
              <AlertCircle className="w-4 h-4" />
              Recommendations to Improve
            </p>
            <ul className="space-y-2">
              {strength.recommendations.map((rec, i) => (
                <li key={i} className="flex items-start gap-2 text-sm text-blue-700 dark:text-blue-300">
                  <ChevronRight className="w-4 h-4 shrink-0 mt-0.5" />
                  {rec}
                </li>
              ))}
            </ul>
          </div>
        )}

        {/* Success indicator */}
        {strength.overall_score >= 75 && (
          <div className="bg-emerald-50 dark:bg-emerald-900/20 border border-emerald-200 dark:border-emerald-800 rounded-xl p-4 text-center">
            <Shield className="w-8 h-8 text-emerald-600 dark:text-emerald-400 mx-auto mb-2" />
            <p className="text-sm font-semibold text-emerald-800 dark:text-emerald-200">
              Strong Appeal Potential
            </p>
            <p className="text-xs text-emerald-700 dark:text-emerald-300 mt-1">
              Your case preparation is looking solid. Consider consulting with a barrister.
            </p>
          </div>
        )}
      </CardContent>
    </Card>
  );
};

export default CaseStrengthMeter;
