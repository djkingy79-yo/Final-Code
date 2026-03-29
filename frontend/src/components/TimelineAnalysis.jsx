/* ========================================================================
   DO NOT UNDO — ENTIRE FILE PROTECTED
   All features, functions, styles, and content in this file are approved
   and must be preserved. Do not remove, rename, or refactor any code.
   ======================================================================== */
import { 
  AlertTriangle, TrendingUp, Scale, Clock, Lightbulb, 
  ChevronRight, CheckCircle, ArrowRight
} from "lucide-react";
import { Badge } from "./ui/badge";
import { Card, CardContent, CardHeader, CardTitle } from "./ui/card";
import { ScrollArea } from "./ui/scroll-area";

const TimelineAnalysis = ({ analysis, onClose }) => {
  if (!analysis) return null;

  const { 
    gaps = [], 
    inconsistencies = [], 
    prosecution_events = [], 
    defence_events = [],
    contested_facts = [],
    ground_connections = [],
    key_observations = [],
    recommended_actions = []
  } = analysis;

  const hasIssues = gaps.length > 0 || inconsistencies.length > 0 || contested_facts.length > 0;

  return (
    <div className="bg-slate-50 border border-slate-200 rounded-xl p-6 space-y-6" data-testid="timeline-analysis">
      <div className="flex items-center justify-between">
        <h3 className="text-lg font-semibold text-slate-900 flex items-center gap-2">
          <Lightbulb className="w-5 h-5 text-blue-500" />
          AI Timeline Analysis
        </h3>
        <button 
          onClick={onClose}
          className="text-slate-400 hover:text-slate-600 text-sm"
        >
          Dismiss
        </button>
      </div>

      {/* Summary Banner */}
      {hasIssues && (
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 flex items-start gap-3">
          <AlertTriangle className="w-5 h-5 text-red-600 shrink-0 mt-0.5" />
          <div>
            <p className="font-medium text-blue-800">Issues Found in Timeline</p>
            <p className="text-sm text-blue-700 mt-1">
              {gaps.length} gap{gaps.length !== 1 ? 's' : ''}, {' '}
              {inconsistencies.length} inconsistenc{inconsistencies.length !== 1 ? 'ies' : 'y'}, {' '}
              {contested_facts.length} contested fact{contested_facts.length !== 1 ? 's' : ''}
            </p>
          </div>
        </div>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        {/* Timeline Gaps */}
        {gaps.length > 0 && (
          <Card>
            <CardHeader className="pb-3">
              <CardTitle className="text-sm font-medium flex items-center gap-2">
                <Clock className="w-4 h-4 text-orange-500" />
                Timeline Gaps ({gaps.length})
              </CardTitle>
            </CardHeader>
            <CardContent>
              <ScrollArea className="max-h-48">
                <div className="space-y-3">
                  {gaps.map((gap, i) => (
                    <div key={i} className="bg-orange-50 p-3 rounded-lg border border-orange-100">
                      <div className="flex items-center gap-2 text-xs text-orange-700 mb-1">
                        <span>{gap.start_date}</span>
                        <ArrowRight className="w-3 h-3" />
                        <span>{gap.end_date}</span>
                        <Badge variant="outline" className={`ml-auto ${
                          gap.significance === 'high' ? 'bg-red-100 text-red-700 border-red-200' :
                          gap.significance === 'medium' ? 'bg-orange-100 text-orange-700 border-orange-200' :
                          'bg-slate-100 text-slate-700 border-slate-200'
                        }`}>
                          {gap.significance}
                        </Badge>
                      </div>
                      <p className="text-sm text-slate-700">{gap.description}</p>
                    </div>
                  ))}
                </div>
              </ScrollArea>
            </CardContent>
          </Card>
        )}

        {/* Inconsistencies */}
        {inconsistencies.length > 0 && (
          <Card>
            <CardHeader className="pb-3">
              <CardTitle className="text-sm font-medium flex items-center gap-2">
                <AlertTriangle className="w-4 h-4 text-red-500" />
                Inconsistencies ({inconsistencies.length})
              </CardTitle>
            </CardHeader>
            <CardContent>
              <ScrollArea className="max-h-48">
                <div className="space-y-3">
                  {inconsistencies.map((item, i) => (
                    <div key={i} className="bg-red-50 p-3 rounded-lg border border-red-100">
                      <p className="text-sm text-slate-700 font-medium">{item.description}</p>
                      {item.impact && (
                        <p className="text-xs text-red-600 mt-1">Impact: {item.impact}</p>
                      )}
                    </div>
                  ))}
                </div>
              </ScrollArea>
            </CardContent>
          </Card>
        )}

        {/* Prosecution vs Defence Balance */}
        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="text-sm font-medium flex items-center gap-2">
              <Scale className="w-4 h-4 text-blue-500" />
              Prosecution vs Defence
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {/* Visual balance bar */}
              <div className="relative h-4 bg-slate-100 rounded-full overflow-hidden">
                <div 
                  className="absolute left-0 top-0 h-full bg-red-400"
                  style={{ 
                    width: `${prosecution_events.length + defence_events.length > 0 
                      ? (prosecution_events.length / (prosecution_events.length + defence_events.length)) * 100 
                      : 50}%` 
                  }}
                />
                <div 
                  className="absolute right-0 top-0 h-full bg-green-400"
                  style={{ 
                    width: `${prosecution_events.length + defence_events.length > 0 
                      ? (defence_events.length / (prosecution_events.length + defence_events.length)) * 100 
                      : 50}%` 
                  }}
                />
              </div>
              <div className="flex justify-between text-sm">
                <span className="text-red-600 font-medium">{prosecution_events.length} Prosecution</span>
                <span className="text-green-600 font-medium">{defence_events.length} Defence</span>
              </div>
              
              {prosecution_events.length > defence_events.length && (
                <p className="text-xs text-slate-500 bg-slate-50 p-2 rounded">
                  Timeline currently favours prosecution. Consider gathering more defence-supportive evidence.
                </p>
              )}
            </div>
          </CardContent>
        </Card>

        {/* Ground Connections */}
        {ground_connections.length > 0 && (
          <Card>
            <CardHeader className="pb-3">
              <CardTitle className="text-sm font-medium flex items-center gap-2">
                <TrendingUp className="w-4 h-4 text-purple-500" />
                Appeal Ground Connections ({ground_connections.length})
              </CardTitle>
            </CardHeader>
            <CardContent>
              <ScrollArea className="max-h-48">
                <div className="space-y-2">
                  {ground_connections.map((conn, i) => (
                    <div key={i} className="flex items-start gap-2 p-2 bg-purple-50 rounded-lg border border-purple-100">
                      <ChevronRight className="w-4 h-4 text-purple-500 shrink-0 mt-0.5" />
                      <div>
                        <Badge variant="outline" className="bg-purple-100 text-purple-700 border-purple-200 mb-1">
                          {conn.ground_type?.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}
                        </Badge>
                        <p className="text-sm text-slate-700">{conn.relevance}</p>
                      </div>
                    </div>
                  ))}
                </div>
              </ScrollArea>
            </CardContent>
          </Card>
        )}
      </div>

      {/* Key Observations */}
      {key_observations.length > 0 && (
        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="text-sm font-medium flex items-center gap-2">
              <Lightbulb className="w-4 h-4 text-blue-500" />
              Key Observations
            </CardTitle>
          </CardHeader>
          <CardContent>
            <ul className="space-y-2">
              {key_observations.map((obs, i) => (
                <li key={i} className="flex items-start gap-2 text-sm text-slate-700">
                  <CheckCircle className="w-4 h-4 text-emerald-500 shrink-0 mt-0.5" />
                  <span>{obs}</span>
                </li>
              ))}
            </ul>
          </CardContent>
        </Card>
      )}

      {/* Recommended Actions */}
      {recommended_actions.length > 0 && (
        <Card className="border-emerald-200 bg-emerald-50/50">
          <CardHeader className="pb-3">
            <CardTitle className="text-sm font-medium flex items-center gap-2 text-emerald-800">
              <CheckCircle className="w-4 h-4 text-emerald-500" />
              Recommended Actions
            </CardTitle>
          </CardHeader>
          <CardContent>
            <ol className="space-y-2 list-decimal list-inside">
              {recommended_actions.map((action, i) => (
                <li key={i} className="text-sm text-slate-700">
                  {action}
                </li>
              ))}
            </ol>
          </CardContent>
        </Card>
      )}

      {/* Contested Facts */}
      {contested_facts.length > 0 && (
        <Card className="border-blue-200">
          <CardHeader className="pb-3">
            <CardTitle className="text-sm font-medium flex items-center gap-2 text-blue-800">
              <AlertTriangle className="w-4 h-4 text-blue-500" />
              Contested Facts to Investigate
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {contested_facts.map((fact, i) => (
                <div key={i} className="bg-white p-3 rounded-lg border border-blue-200">
                  <p className="text-sm font-medium text-slate-800">{fact.issue}</p>
                  {fact.recommendation && (
                    <p className="text-xs text-blue-700 mt-2 flex items-center gap-1">
                      <ChevronRight className="w-3 h-3" />
                      {fact.recommendation}
                    </p>
                  )}
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
};

export default TimelineAnalysis;
