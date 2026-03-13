/* DO NOT UNDO — CaseComparison component. All features in this file are approved and must be preserved. */
import { useState, useEffect } from "react";
import { BarChart3, FileText, Shield, TrendingUp, TrendingDown, Minus, Users, MapPin, AlertTriangle, Loader2 } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "./ui/card";
import { Badge } from "./ui/badge";
import axios from "axios";
import { API } from "../App";

const CaseComparison = ({ caseId }) => {
  const [comparison, setComparison] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchComparison = async () => {
      try {
        const response = await axios.get(`${API}/cases/${caseId}/comparison`);
        setComparison(response.data);
      } catch (err) {
        console.error("Failed to fetch comparison:", err);
        setError("Unable to load comparison data");
      } finally {
        setLoading(false);
      }
    };
    
    if (caseId) {
      fetchComparison();
    }
  }, [caseId]);

  if (loading) {
    return (
      <Card className="bg-white border-slate-200">
        <CardContent className="p-8 text-center">
          <Loader2 className="w-8 h-8 animate-spin text-slate-400 mx-auto" />
          <p className="text-slate-500 mt-2">Loading comparison data...</p>
        </CardContent>
      </Card>
    );
  }

  if (error || !comparison) {
    return (
      <Card className="bg-white border-slate-200">
        <CardContent className="p-8 text-center">
          <AlertTriangle className="w-8 h-8 text-amber-400 mx-auto mb-2" />
          <p className="text-slate-500">Comparison data not available</p>
        </CardContent>
      </Card>
    );
  }

  const { your_case, similar_cases, comparison: comp, common_grounds_for_offence } = comparison;

  const getTrendIcon = (status) => {
    if (status === "above") return <TrendingUp className="w-4 h-4 text-emerald-500" />;
    if (status === "below") return <TrendingDown className="w-4 h-4 text-amber-500" />;
    return <Minus className="w-4 h-4 text-slate-400" />;
  };

  const getTrendColor = (status) => {
    if (status === "above") return "text-emerald-600 bg-emerald-50";
    if (status === "below") return "text-amber-600 bg-amber-50";
    return "text-slate-600 bg-slate-50";
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center gap-3">
        <div className="w-10 h-10 bg-blue-100 rounded-lg flex items-center justify-center">
          <BarChart3 className="w-5 h-5 text-blue-600" />
        </div>
        <div>
          <h3 className="font-semibold text-slate-900" style={{ fontFamily: 'Crimson Pro, serif' }}>
            Compare Your Case
          </h3>
          <p className="text-sm text-slate-500">
            See how your case compares to similar {your_case.offence_category} cases in {your_case.state}
          </p>
        </div>
      </div>

      {/* Similar Cases Count */}
      <div className="grid grid-cols-3 gap-4">
        <Card className="bg-gradient-to-br from-blue-50 to-white border-blue-100">
          <CardContent className="p-4 text-center">
            <p className="text-2xl font-bold text-blue-700">{similar_cases.same_offence_count}</p>
            <p className="text-xs text-blue-600">Same Offence Type</p>
          </CardContent>
        </Card>
        <Card className="bg-gradient-to-br from-purple-50 to-white border-purple-100">
          <CardContent className="p-4 text-center">
            <p className="text-2xl font-bold text-purple-700">{similar_cases.same_state_count}</p>
            <p className="text-xs text-purple-600">Same State</p>
          </CardContent>
        </Card>
        <Card className="bg-gradient-to-br from-amber-50 to-white border-amber-100">
          <CardContent className="p-4 text-center">
            <p className="text-2xl font-bold text-amber-700">{similar_cases.exact_match_count}</p>
            <p className="text-xs text-amber-600">Exact Match</p>
          </CardContent>
        </Card>
      </div>

      {/* Your Case vs Average */}
      <Card className="bg-white border-slate-200">
        <CardHeader className="pb-2">
          <CardTitle className="text-sm font-semibold text-slate-700 flex items-center gap-2">
            <Users className="w-4 h-4" />
            Your Case vs. Similar Cases Average
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          {/* Documents Comparison */}
          <div className="flex items-center justify-between p-3 bg-slate-50 rounded-lg">
            <div className="flex items-center gap-3">
              <FileText className="w-5 h-5 text-slate-500" />
              <div>
                <p className="font-medium text-slate-900">Documents Uploaded</p>
                <p className="text-xs text-slate-500">Average: {similar_cases.avg_documents} documents</p>
              </div>
            </div>
            <div className="flex items-center gap-2">
              <span className="text-lg font-bold text-slate-900">{your_case.documents}</span>
              <Badge className={`${getTrendColor(comp.documents_vs_avg)} border-0`}>
                {getTrendIcon(comp.documents_vs_avg)}
                <span className="ml-1">
                  {comp.documents_diff > 0 ? "+" : ""}{comp.documents_diff}
                </span>
              </Badge>
            </div>
          </div>

          {/* Grounds Comparison */}
          <div className="flex items-center justify-between p-3 bg-slate-50 rounded-lg">
            <div className="flex items-center gap-3">
              <Shield className="w-5 h-5 text-slate-500" />
              <div>
                <p className="font-medium text-slate-900">Grounds Identified</p>
                <p className="text-xs text-slate-500">Average: {similar_cases.avg_grounds} grounds</p>
              </div>
            </div>
            <div className="flex items-center gap-2">
              <span className="text-lg font-bold text-slate-900">{your_case.grounds_identified}</span>
              <Badge className={`${getTrendColor(comp.grounds_vs_avg)} border-0`}>
                {getTrendIcon(comp.grounds_vs_avg)}
                <span className="ml-1">
                  {comp.grounds_diff > 0 ? "+" : ""}{comp.grounds_diff}
                </span>
              </Badge>
            </div>
          </div>

          {/* Reports Count */}
          <div className="flex items-center justify-between p-3 bg-slate-50 rounded-lg">
            <div className="flex items-center gap-3">
              <BarChart3 className="w-5 h-5 text-slate-500" />
              <div>
                <p className="font-medium text-slate-900">Reports Generated</p>
                <p className="text-xs text-slate-500">Your analysis reports</p>
              </div>
            </div>
            <span className="text-lg font-bold text-slate-900">{your_case.reports_generated}</span>
          </div>
        </CardContent>
      </Card>

      {/* Common Grounds for This Offence */}
      {common_grounds_for_offence && common_grounds_for_offence.length > 0 && (
        <Card className="bg-white border-slate-200">
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-semibold text-slate-700 flex items-center gap-2">
              <Shield className="w-4 h-4" />
              Most Common Grounds for {your_case.offence_category} Cases
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-2">
              {common_grounds_for_offence.map((ground, index) => (
                <div 
                  key={index}
                  className="flex items-center justify-between p-2 hover:bg-slate-50 rounded transition-colors"
                >
                  <div className="flex items-center gap-2">
                    <span className="w-6 h-6 bg-slate-100 rounded-full flex items-center justify-center text-xs font-medium text-slate-600">
                      {index + 1}
                    </span>
                    <span className="text-sm text-slate-700">{ground.type}</span>
                  </div>
                  <Badge variant="outline" className="bg-slate-50">
                    {ground.count} cases
                  </Badge>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Insights */}
      <div className="p-4 bg-blue-50 border border-blue-100 rounded-lg">
        <p className="text-sm text-blue-800">
          <strong>Insight:</strong> Your case has {comp.documents_vs_avg === "above" ? "more" : comp.documents_vs_avg === "below" ? "fewer" : "the same number of"} documents 
          than the average {your_case.offence_category.toLowerCase()} case. 
          {comp.documents_vs_avg === "below" && " Consider uploading more relevant documents to strengthen your analysis."}
          {comp.grounds_vs_avg === "below" && " Try running the AI Identify Grounds feature to find potential appeal grounds."}
        </p>
      </div>
    </div>
  );
};

export default CaseComparison;
