/* ========================================================================
   DO NOT UNDO — ENTIRE FILE PROTECTED
   All features, functions, styles, and content in this file are approved
   and must be preserved. Do not remove, rename, or refactor any code.
   ======================================================================== */
import { useState, useEffect } from "react";
import { useNavigate, Link } from "react-router-dom";
import axios from "axios";
import { 
  Scale, ArrowLeft, GitCompare, BarChart3, TrendingUp, 
  Filter, CheckCircle, FileText,
  Gavel, Menu, X, Info, Sparkles
} from "lucide-react";
import { Button } from "../components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "../components/ui/card";
import { Badge } from "../components/ui/badge";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "../components/ui/select";
import { Checkbox } from "../components/ui/checkbox";
import { API } from "../App";
import { toast } from "sonner";
import { useTheme } from "../contexts/ThemeContext";
import AssessmentNote from "../components/AssessmentNote";

const CompareCasesPage = ({ user }) => {
  const navigate = useNavigate();

  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const [activeTab, setActiveTab] = useState("my-cases"); // "my-cases" or "patterns"
  
  // My Cases comparison state
  const [myCases, setMyCases] = useState([]);
  const [selectedCases, setSelectedCases] = useState([]);
  const [comparisonResult, setComparisonResult] = useState(null);
  const [loadingComparison, setLoadingComparison] = useState(false);
  
  // Patterns state
  const [patterns, setPatterns] = useState(null);
  const [loadingPatterns, setLoadingPatterns] = useState(false);
  const [patternFilters, setPatternFilters] = useState({
    offence_category: "",
    state: "",
    ground_type: ""
  });
  
  // Success factors state
  const [successFactors, setSuccessFactors] = useState(null);
  const [loadingFactors, setLoadingFactors] = useState(false);

  // Insufficient data handling
  const hasInsufficientPatterns = patterns?.message?.toLowerCase().includes("insufficient");
  const hasInsufficientFactors = successFactors?.message?.toLowerCase().includes("insufficient");

  useEffect(() => {
    if (user) {
      fetchMyCases();
    }
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [user]);

  const fetchMyCases = async () => {
    try {
      const response = await axios.get(`${API}/cases`);
      setMyCases(response.data);
    } catch (error) {
      console.error("Failed to fetch cases:", error);
    }
  };

  const toggleCaseSelection = (caseId) => {
    setSelectedCases(prev => {
      if (prev.includes(caseId)) {
        return prev.filter(id => id !== caseId);
      }
      if (prev.length >= 5) {
        toast.error("Maximum 5 cases can be compared");
        return prev;
      }
      return [...prev, caseId];
    });
  };

  const compareMyCases = async () => {
    if (selectedCases.length < 2) {
      toast.error("Select at least 2 cases to compare");
      return;
    }
    
    setLoadingComparison(true);
    try {
      const response = await axios.post(`${API}/compare/my-cases`, {
        case_ids: selectedCases
      });
      setComparisonResult(response.data);
    } catch (error) {
      toast.error(error.response?.data?.detail || "Failed to compare cases");
    } finally {
      setLoadingComparison(false);
    }
  };

  const fetchPatterns = async () => {
    setLoadingPatterns(true);
    try {
      const params = new URLSearchParams();
      if (patternFilters.offence_category) params.append("offence_category", patternFilters.offence_category);
      if (patternFilters.state) params.append("state", patternFilters.state);
      if (patternFilters.ground_type) params.append("ground_type", patternFilters.ground_type);
      
      const response = await axios.get(`${API}/compare/patterns?${params.toString()}`);
      setPatterns(response.data);
    } catch (error) {
      toast.error("Failed to fetch patterns");
    } finally {
      setLoadingPatterns(false);
    }
  };

  const fetchSuccessFactors = async () => {
    setLoadingFactors(true);
    try {
      const params = new URLSearchParams();
      if (patternFilters.offence_category) params.append("offence_category", patternFilters.offence_category);
      
      const response = await axios.get(`${API}/compare/case-composition?${params.toString()}`);
      setSuccessFactors(response.data);
    } catch (error) {
      toast.error("Failed to fetch case composition data");
    } finally {
      setLoadingFactors(false);
    }
  };

  useEffect(() => {
    if (activeTab === "patterns" && user) {
      fetchPatterns();
      fetchSuccessFactors();
    }
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [activeTab, patternFilters, user]);

  if (!user) {
    return (
      <div className="min-h-screen bg-white flex items-center justify-center">
        <Card className="max-w-md mx-auto">
          <CardContent className="p-8 text-center">
            <GitCompare className="w-12 h-12 text-red-600 mx-auto mb-4" />
            <h2 className="text-xl font-bold text-slate-900 mb-2">Sign In Required</h2>
            <p className="text-slate-600 mb-4">Please sign in to compare cases and view patterns.</p>
            <Button onClick={() => navigate("/")} className="bg-red-600 text-white hover:bg-blue-700">
              Go to Home
            </Button>
          </CardContent>
        </Card>
      </div>
    );
  }

  const groundTypeLabels = {
    procedural_error: "Procedural Error",
    fresh_evidence: "Fresh Evidence",
    miscarriage_of_justice: "Miscarriage of Justice",
    sentencing_error: "Sentencing Error",
    judicial_error: "Judicial Error",
    ineffective_counsel: "Ineffective Counsel",
    jury_irregularity: "Jury Irregularity",
    prosecution_misconduct: "Prosecution Misconduct"
  };

  const offenceLabels = {
    homicide: "Homicide",
    assault: "Assault & Violence",
    sexual_offences: "Sexual Offences",
    robbery_theft: "Robbery & Theft",
    drug_offences: "Drug Offences",
    fraud_dishonesty: "Fraud & Dishonesty",
    firearms_weapons: "Firearms & Weapons",
    domestic_violence: "Domestic Violence",
    public_order: "Public Order",
    terrorism: "Terrorism",
    driving_offences: "Driving Offences"
  };

  const stateLabels = {
    nsw: "New South Wales",
    vic: "Victoria",
    qld: "Queensland",
    sa: "South Australia",
    wa: "Western Australia",
    tas: "Tasmania",
    nt: "Northern Territory",
    act: "ACT"
  };

  return (
    <div className="min-h-screen bg-white" style={{ fontFamily: 'Manrope, sans-serif' }}>
      {/* Header */}
      <header className="bg-slate-900 sticky top-0 z-50">
        <div className="max-w-6xl mx-auto px-6 py-4 flex items-center justify-between">
          <Link to="/dashboard" className="flex items-center gap-3">
            <div className="w-9 h-9 rounded-lg bg-red-600 flex items-center justify-center">
              <Scale className="w-5 h-5 text-white" />
            </div>
            <span className="text-lg font-semibold text-white tracking-tight hidden sm:block" style={{ fontFamily: "'Times New Roman', Times, serif" }}>
              Appeal Case Manager
            </span>
          </Link>
          <div className="hidden md:flex items-center gap-4">
<Button 
              onClick={() => navigate("/dashboard")} 
              className="bg-blue-700 text-white hover:bg-blue-600 rounded-lg"
            >
              <ArrowLeft className="w-4 h-4 mr-2" />
              Dashboard
            </Button>
          </div>
          <button className="md:hidden p-2 text-white" onClick={() => setMobileMenuOpen(!mobileMenuOpen)}>
            {mobileMenuOpen ? <X className="w-6 h-6" /> : <Menu className="w-6 h-6" />}
          </button>
        </div>
      </header>

      {/* Hero Section */}
      <section className="relative py-12 px-6 overflow-hidden">
        <div className="absolute inset-0 z-0">
          <img 
            src="/images/stock/office-desk.jpg" 
            alt=""
            className="w-full h-full object-cover opacity-5"
          />
          <div className="absolute inset-0 bg-gradient-to-b from-background via-background/95 to-background" />
        </div>
        
        <div className="max-w-6xl mx-auto relative z-10">
          <div className="flex items-center gap-4 mb-2">
            <div className="w-14 h-14 rounded-2xl bg-gradient-to-br from-blue-500 to-blue-700 flex items-center justify-center shadow-lg shadow-blue-500/30">
              <GitCompare className="w-7 h-7 text-white" />
            </div>
            <div>
              <p className="text-red-600 font-semibold text-xs uppercase tracking-widest">Analysis</p>
              <h1 className="text-4xl sm:text-5xl font-bold text-slate-900" style={{ fontFamily: "'Times New Roman', Times, serif" }}>
                Compare Cases
              </h1>
            </div>
          </div>
          <p className="text-slate-600 max-w-2xl mt-2">
            Compare your own cases to find patterns, or explore anonymised insights from all cases on the platform.
          </p>
        </div>
      </section>

      {/* Tab Navigation */}
      <div className="border-b border-slate-200 bg-white/50">
        <div className="max-w-6xl mx-auto px-6">
          <div className="flex gap-1">
            <button
              onClick={() => setActiveTab("my-cases")}
              className={`px-6 py-4 font-medium text-sm border-b-2 transition-colors flex items-center gap-2 ${
                activeTab === "my-cases" 
                  ? "border-blue-500 text-red-600" 
                  : "border-transparent text-slate-600 hover:text-slate-900"
              }`}
            >
              <FileText className="w-4 h-4" />
              My Cases
            </button>
            <button
              onClick={() => setActiveTab("patterns")}
              className={`px-6 py-4 font-medium text-sm border-b-2 transition-colors flex items-center gap-2 ${
                activeTab === "patterns" 
                  ? "border-blue-500 text-red-600" 
                  : "border-transparent text-slate-600 hover:text-slate-900"
              }`}
            >
              <BarChart3 className="w-4 h-4" />
              Platform Patterns
            </button>
          </div>
        </div>
      </div>

      <main className="max-w-6xl mx-auto px-6 py-8">
        {activeTab === "my-cases" ? (
          <div className="space-y-8">
            {/* Case Selection */}
            <Card className="bg-white border-slate-200">
              <CardHeader>
                <CardTitle className="text-lg flex items-center gap-2" style={{ fontFamily: "'Times New Roman', Times, serif" }}>
                  <Gavel className="w-5 h-5 text-red-600" />
                  Select Cases to Compare
                  <Badge variant="outline" className="ml-2">
                    {selectedCases.length}/5 selected
                  </Badge>
                </CardTitle>
              </CardHeader>
              <CardContent>
                {myCases.length === 0 ? (
                  <div className="text-center py-8">
                    <FileText className="w-12 h-12 text-slate-600/50 mx-auto mb-3" />
                    <p className="text-slate-600">No cases found. Create a case first.</p>
                    <Button onClick={() => navigate("/dashboard")} className="mt-4 bg-red-600 text-white hover:bg-blue-700">
                      Go to Dashboard
                    </Button>
                  </div>
                ) : (
                  <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-4">
                    {myCases.map((case_) => (
                      <div
                        key={case_.case_id}
                        onClick={() => toggleCaseSelection(case_.case_id)}
                        className={`p-4 rounded-xl border-2 cursor-pointer transition-all ${
                          selectedCases.includes(case_.case_id)
                            ? "border-blue-500 bg-blue-50"
                            : "border-slate-200 hover:border-blue-300 bg-white"
                        }`}
                      >
                        <div className="flex items-start justify-between mb-2">
                          <h3 className="font-semibold text-slate-900 truncate">{case_.title}</h3>
                          <Checkbox 
                            checked={selectedCases.includes(case_.case_id)}
                            className="data-[state=checked]:bg-red-600"
                          />
                        </div>
                        <p className="text-sm text-slate-600 mb-2">{case_.defendant_name}</p>
                        <div className="flex flex-wrap gap-1">
                          <Badge variant="outline" className="text-xs">
                            {offenceLabels[case_.offence_category] || case_.offence_category}
                          </Badge>
                          <Badge variant="outline" className="text-xs">
                            {case_.state?.toUpperCase()}
                          </Badge>
                        </div>
                        <div className="flex gap-3 mt-3 text-xs text-slate-600">
                          <span>{case_.document_count || 0} docs</span>
                          <span>{case_.event_count || 0} events</span>
                        </div>
                      </div>
                    ))}
                  </div>
                )}
                
                {myCases.length >= 2 && (
                  <div className="mt-6 flex justify-center">
                    <Button 
                      onClick={compareMyCases} 
                      disabled={selectedCases.length < 2 || loadingComparison}
                      className="bg-gradient-to-r from-red-600 to-blue-700 text-white hover:from-blue-700 hover:to-blue-800 rounded-xl px-8 py-5 font-semibold shadow-lg shadow-red-600/20"
                    >
                      {loadingComparison ? (
                        <>
                          <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white mr-2"></div>
                          Comparing...
                        </>
                      ) : (
                        <>
                          <GitCompare className="w-5 h-5 mr-2" />
                          Compare Selected Cases
                        </>
                      )}
                    </Button>
                  </div>
                )}
              </CardContent>
            </Card>

            {/* Comparison Results */}
            {comparisonResult && (
              <div className="space-y-6">
                {/* Summary Cards */}
                <div className="grid md:grid-cols-3 gap-6">
                  {comparisonResult.cases.map((case_, index) => (
                    <Card key={case_.case_id} className="bg-white border-slate-200">
                      <CardContent className="p-5">
                        <h3 className="font-semibold text-slate-900 mb-2 truncate">{case_.title}</h3>
                        <p className="text-sm text-slate-600 mb-3">{case_.defendant_name}</p>
                        <div className="space-y-2 text-sm">
                          <div className="flex justify-between">
                            <span className="text-slate-600">Grounds:</span>
                            <span className="font-medium text-slate-900">{case_.grounds_count}</span>
                          </div>
                          <div className="flex justify-between">
                            <span className="text-slate-600">Strong:</span>
                            <span className="font-medium text-emerald-600">{case_.ground_strengths.strong}</span>
                          </div>
                          <div className="flex justify-between">
                            <span className="text-slate-600">Documents:</span>
                            <span className="font-medium text-slate-900">{case_.documents_count}</span>
                          </div>
                          <div className="flex justify-between">
                            <span className="text-slate-600">Events:</span>
                            <span className="font-medium text-slate-900">{case_.events_count}</span>
                          </div>
                        </div>
                      </CardContent>
                    </Card>
                  ))}
                </div>

                {/* Common Grounds */}
                {comparisonResult.ground_comparison.common_grounds.length > 0 && (
                  <Card className="bg-emerald-50 border-emerald-200">
                    <CardContent className="p-5">
                      <h3 className="font-semibold text-emerald-800 mb-3 flex items-center gap-2">
                        <CheckCircle className="w-5 h-5" />
                        Common Ground Types
                      </h3>
                      <div className="flex flex-wrap gap-2">
                        {comparisonResult.ground_comparison.common_grounds.map((gt, i) => (
                          <Badge key={i} className="bg-emerald-600 text-white">
                            {groundTypeLabels[gt] || gt}
                          </Badge>
                        ))}
                      </div>
                    </CardContent>
                  </Card>
                )}

                {/* Insights */}
                {comparisonResult.insights.length > 0 && (
                  <Card className="bg-white border-slate-200">
                    <CardHeader>
                      <CardTitle className="text-lg flex items-center gap-2" style={{ fontFamily: "'Times New Roman', Times, serif" }}>
                        <Sparkles className="w-5 h-5 text-red-600" />
                        Insights
                      </CardTitle>
                    </CardHeader>
                    <CardContent>
                      <ul className="space-y-2">
                        {comparisonResult.insights.map((insight, i) => (
                          <li key={i} className="flex items-start gap-2 text-slate-600">
                            <Info className="w-4 h-4 text-red-600 mt-0.5 flex-shrink-0" />
                            {insight}
                          </li>
                        ))}
                      </ul>
                    </CardContent>
                  </Card>
                )}
              </div>
            )}
          </div>
        ) : (
          /* Patterns Tab */
          <div className="space-y-8">
            {/* Assessment Note */}
            <AssessmentNote
              note={patterns?.assessment_note || successFactors?.assessment_note || "These comparisons are descriptive platform indicators and do not determine legal merit or likely appeal outcome."}
              className="mb-4"
            />

            {/* Filters */}
            <Card className="bg-white border-slate-200">
              <CardHeader>
                <CardTitle className="text-lg flex items-center gap-2" style={{ fontFamily: "'Times New Roman', Times, serif" }}>
                  <Filter className="w-5 h-5 text-red-600" />
                  Filter Patterns
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="grid md:grid-cols-3 gap-4">
                  <div>
                    <label className="text-sm font-medium text-slate-900 mb-1.5 block">Offence Category</label>
                    <Select 
                      value={patternFilters.offence_category || "all"} 
                      onValueChange={(v) => setPatternFilters({...patternFilters, offence_category: v === "all" ? "" : v})}
                    >
                      <SelectTrigger className="rounded-xl">
                        <SelectValue placeholder="All categories" />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="all">All categories</SelectItem>
                        {Object.entries(offenceLabels).map(([key, label]) => (
                          <SelectItem key={key} value={key}>{label}</SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                  </div>
                  <div>
                    <label className="text-sm font-medium text-slate-900 mb-1.5 block">State</label>
                    <Select 
                      value={patternFilters.state || "all"} 
                      onValueChange={(v) => setPatternFilters({...patternFilters, state: v === "all" ? "" : v})}
                    >
                      <SelectTrigger className="rounded-xl">
                        <SelectValue placeholder="All states" />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="all">All states</SelectItem>
                        {Object.entries(stateLabels).map(([key, label]) => (
                          <SelectItem key={key} value={key}>{label}</SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                  </div>
                  <div>
                    <label className="text-sm font-medium text-slate-900 mb-1.5 block">Ground Type</label>
                    <Select 
                      value={patternFilters.ground_type || "all"} 
                      onValueChange={(v) => setPatternFilters({...patternFilters, ground_type: v === "all" ? "" : v})}
                    >
                      <SelectTrigger className="rounded-xl">
                        <SelectValue placeholder="All ground types" />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="all">All ground types</SelectItem>
                        {Object.entries(groundTypeLabels).map(([key, label]) => (
                          <SelectItem key={key} value={key}>{label}</SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* Pattern Stats */}
            {loadingPatterns ? (
              <div className="text-center py-12">
                <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-red-600 mx-auto mb-4"></div>
                <p className="text-slate-600">Loading patterns...</p>
              </div>
            ) : hasInsufficientPatterns ? (
              <Card className="bg-white border-slate-200">
                <CardContent className="p-6">
                  <div className="flex items-center gap-3">
                    <Info className="w-5 h-5 text-blue-500 flex-shrink-0" />
                    <p className="text-sm text-slate-700">{patterns.message}</p>
                  </div>
                </CardContent>
              </Card>
            ) : patterns ? (
              <div className="space-y-6">
                {/* Overview Stats */}
                <div className="grid md:grid-cols-4 gap-4">
                  <Card className="bg-white border-slate-200">
                    <CardContent className="p-5 text-center">
                      <div className="w-12 h-12 bg-blue-100 rounded-xl flex items-center justify-center mx-auto mb-3">
                        <FileText className="w-6 h-6 text-blue-600" />
                      </div>
                      <p className="text-2xl font-bold text-slate-900">{patterns.total_cases_analyzed}</p>
                      <p className="text-sm text-slate-600">Cases Analysed</p>
                    </CardContent>
                  </Card>
                  <Card className="bg-white border-slate-200">
                    <CardContent className="p-5 text-center">
                      <div className="w-12 h-12 bg-blue-100 rounded-xl flex items-center justify-center mx-auto mb-3">
                        <Gavel className="w-6 h-6 text-red-600" />
                      </div>
                      <p className="text-2xl font-bold text-slate-900">{patterns.total_grounds_analyzed}</p>
                      <p className="text-sm text-slate-600">Grounds Identified</p>
                    </CardContent>
                  </Card>
                  <Card className="bg-white border-slate-200">
                    <CardContent className="p-5 text-center">
                      <div className="w-12 h-12 bg-emerald-100 rounded-xl flex items-center justify-center mx-auto mb-3">
                        <TrendingUp className="w-6 h-6 text-emerald-600" />
                      </div>
                      <p className="text-2xl font-bold text-slate-900">{patterns.success_indicators?.strong_grounds_count || 0}</p>
                      <p className="text-sm text-slate-600">Higher Preparation Grounds</p>
                    </CardContent>
                  </Card>
                  <Card className="bg-white border-slate-200">
                    <CardContent className="p-5 text-center">
                      <div className="w-12 h-12 bg-purple-100 rounded-xl flex items-center justify-center mx-auto mb-3">
                        <BarChart3 className="w-6 h-6 text-purple-600" />
                      </div>
                      <p className="text-2xl font-bold text-slate-900">{patterns.success_indicators?.avg_grounds_per_case || 0}</p>
                      <p className="text-sm text-slate-600">Avg Grounds/Case</p>
                    </CardContent>
                  </Card>
                </div>

                {/* Ground Type Distribution */}
                <Card className="bg-white border-slate-200">
                  <CardHeader>
                    <CardTitle className="text-lg" style={{ fontFamily: "'Times New Roman', Times, serif" }}>
                      Ground Type Distribution
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    {Object.entries(patterns.patterns?.ground_type_distribution || {}).length > 0 ? (
                      <div className="space-y-3">
                        {Object.entries(patterns.patterns.ground_type_distribution).map(([type, count], i) => {
                          const maxCount = Math.max(...Object.values(patterns.patterns.ground_type_distribution));
                          const percentage = (count / maxCount) * 100;
                          return (
                            <div key={type} className="flex items-center gap-3">
                              <div className="w-40 text-sm text-slate-600 truncate">
                                {groundTypeLabels[type] || type}
                              </div>
                              <div className="flex-1 bg-slate-100 rounded-full h-7 overflow-hidden">
                                <div 
                                  className="h-full bg-gradient-to-r from-blue-500 to-red-600 rounded-full flex items-center justify-end pr-3 transition-all duration-500"
                                  style={{ width: `${Math.max(percentage, 10)}%` }}
                                >
                                  <span className="text-xs font-semibold text-white">{count}</span>
                                </div>
                              </div>
                            </div>
                          );
                        })}
                      </div>
                    ) : (
                      <p className="text-slate-600 text-center py-8">No data available</p>
                    )}
                  </CardContent>
                </Card>

                {/* Insights */}
                {patterns.insights?.length > 0 && (
                  <Card className="bg-gradient-to-r from-slate-900 to-indigo-950 border-0">
                    <CardContent className="p-6">
                      <h3 className="text-lg font-semibold text-white mb-4 flex items-center gap-2" style={{ fontFamily: "'Times New Roman', Times, serif" }}>
                        <Sparkles className="w-5 h-5 text-blue-400" />
                        Key Insights
                      </h3>
                      <ul className="space-y-2">
                        {patterns.insights.map((insight, i) => (
                          <li key={i} className="flex items-start gap-2 text-slate-300">
                            <CheckCircle className="w-4 h-4 text-blue-400 mt-0.5 flex-shrink-0" />
                            {insight}
                          </li>
                        ))}
                      </ul>
                    </CardContent>
                  </Card>
                )}

                {/* Platform Pattern Indicators */}
                {successFactors && !hasInsufficientFactors && successFactors.insights?.length > 0 && (
                  <Card className="bg-white border-slate-200">
                    <CardHeader>
                      <CardTitle className="text-lg flex items-center gap-2" style={{ fontFamily: "'Times New Roman', Times, serif" }}>
                        <TrendingUp className="w-5 h-5 text-blue-600" />
                        Platform Pattern Indicators
                      </CardTitle>
                      <p className="text-xs text-slate-500 italic mt-1">
                        {successFactors.disclaimer || successFactors.assessment_note || "These patterns reflect internal platform indicators, not court success analytics."}
                      </p>
                    </CardHeader>
                    <CardContent>
                      <div className="space-y-4">
                        {successFactors.insights.map((insight, i) => (
                          <div key={i} className="p-4 bg-slate-50 rounded-xl">
                            <p className="text-slate-900 text-sm">{insight}</p>
                          </div>
                        ))}
                        {successFactors.recommendations?.map((rec, i) => (
                          <div key={`rec-${i}`} className="p-4 bg-blue-50 rounded-xl">
                            <p className="text-sm text-blue-800">{rec}</p>
                          </div>
                        ))}
                      </div>
                    </CardContent>
                  </Card>
                )}
              </div>
            ) : (
              <div className="text-center py-12">
                <BarChart3 className="w-12 h-12 text-slate-600/50 mx-auto mb-3" />
                <p className="text-slate-600">No pattern data available</p>
              </div>
            )}
          </div>
        )}
      </main>
    </div>
  );
};

export default CompareCasesPage;
