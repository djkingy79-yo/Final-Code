/* ========================================================================
   DO NOT UNDO — ENTIRE FILE PROTECTED
   All features, functions, styles, and content in this file are approved
   and must be preserved. Do not remove, rename, or refactor any code.
   ======================================================================== */
import { useState, useEffect } from "react";
import { Scale, ArrowLeft, BarChart3, FileText, Users, TrendingUp, MapPin, Gavel, Shield, AlertTriangle, Moon, Sun, Menu, X } from "lucide-react";
import { Button } from "../components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "../components/ui/card";
import { Link } from "react-router-dom";
import axios from "axios";
import { API } from "../App";
import { useTheme } from "../contexts/ThemeContext";

const Statistics = () => {
  const { theme, toggleTheme } = useTheme();
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchStats = async () => {
      try {
        const response = await axios.get(`${API}/statistics/public`);
        setStats(response.data);
      } catch (error) {
        console.error("Failed to fetch statistics:", error);
      } finally {
        setLoading(false);
      }
    };
    fetchStats();
  }, []);

  const getOffenceColor = (key) => {
    const colors = {
      homicide: "bg-red-500",
      assault: "bg-orange-500",
      sexual_offences: "bg-pink-500",
      robbery_theft: "bg-blue-500",
      drug_offences: "bg-green-500",
      fraud_dishonesty: "bg-blue-500",
      firearms_weapons: "bg-slate-500",
      domestic_violence: "bg-purple-500",
      public_order: "bg-cyan-500",
      terrorism: "bg-rose-500",
      driving_offences: "bg-teal-500"
    };
    return colors[key] || "bg-slate-400";
  };

  const getStateColor = (key) => {
    const colors = {
      nsw: "bg-blue-600",
      vic: "bg-purple-600",
      qld: "bg-red-600",
      sa: "bg-red-600",
      wa: "bg-emerald-600",
      tas: "bg-teal-600",
      nt: "bg-orange-600",
      act: "bg-indigo-600"
    };
    return colors[key] || "bg-slate-400";
  };

  const getStrengthColor = (strength) => {
    const colors = {
      Strong: "bg-emerald-500",
      Moderate: "bg-blue-500",
      Weak: "bg-red-500"
    };
    return colors[strength] || "bg-slate-400";
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-white flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-red-600 mx-auto mb-4"></div>
          <p className="text-slate-600">Loading statistics...</p>
        </div>
      </div>
    );
  }

  const maxOffenceCount = stats?.cases_by_offence?.[0]?.count || 1;
  const maxStateCount = stats?.cases_by_state?.[0]?.count || 1;

  return (
    <div className="min-h-screen bg-white" style={{ fontFamily: 'Manrope, sans-serif' }}>
      {/* Header */}
      <header className="bg-slate-900 sticky top-0 z-50">
        <div className="max-w-6xl mx-auto px-6 py-4 flex items-center justify-between">
          <Link to="/" className="flex items-center gap-3">
            <div className="w-9 h-9 rounded-lg bg-red-600 flex items-center justify-center">
              <Scale className="w-5 h-5 text-white" />
            </div>
            <span className="text-lg font-semibold text-white tracking-tight hidden sm:block" style={{ fontFamily: 'Crimson Pro, serif' }}>
              Appeal Case Manager
            </span>
          </Link>
          <div className="hidden md:flex items-center gap-4">
            <Link to="/glossary" className="text-slate-400 hover:text-white text-sm transition-colors">Legal Terms</Link>
            <Link to="/faq" className="text-slate-400 hover:text-white text-sm transition-colors">FAQ</Link>
            <Link to="/forms" className="text-slate-400 hover:text-white text-sm transition-colors">Forms</Link>
<Link to="/">
              <Button variant="outline" className="border-slate-600 text-slate-300 hover:bg-slate-800 rounded-lg">
                <ArrowLeft className="w-4 h-4 mr-2" />
                Back
              </Button>
            </Link>
          </div>
          <button className="md:hidden p-2 text-white" onClick={() => setMobileMenuOpen(!mobileMenuOpen)}>
            {mobileMenuOpen ? <X className="w-6 h-6" /> : <Menu className="w-6 h-6" />}
          </button>
        </div>
        {mobileMenuOpen && (
          <div className="md:hidden bg-slate-800 border-t border-slate-700 px-6 py-4 space-y-3">
            <Link to="/glossary" className="block py-2 text-slate-300 hover:text-white">Legal Terms</Link>
            <Link to="/faq" className="block py-2 text-slate-300 hover:text-white">FAQ</Link>
            <Link to="/forms" className="block py-2 text-slate-300 hover:text-white">Forms</Link>
            <Link to="/" className="block py-2 text-blue-500 hover:text-blue-400">Back to Home</Link>
          </div>
        )}
      </header>

      {/* Hero Section */}
      <section className="relative py-16 px-6 overflow-hidden">
        <div className="absolute inset-0 z-0">
          <img 
            src="https://images.unsplash.com/photo-1551288049-bebda4e38f71?crop=entropy&cs=srgb&fm=jpg&q=85&w=1920" 
            alt=""
            className="w-full h-full object-cover opacity-5"
          />
          <div className="absolute inset-0 bg-gradient-to-b from-background via-background/95 to-background" />
        </div>
        
        <div className="max-w-6xl mx-auto relative z-10 text-center">
          <div className="flex justify-center mb-6">
            <div className="w-16 h-16 rounded-2xl bg-gradient-to-br from-blue-500 to-blue-700 flex items-center justify-center shadow-lg shadow-blue-500/30">
              <BarChart3 className="w-8 h-8 text-white" />
            </div>
          </div>
          <p className="text-red-600 font-semibold text-xs uppercase tracking-widest mb-3">Analytics</p>
          <h1 className="text-4xl md:text-5xl font-bold text-slate-900 mb-4" style={{ fontFamily: 'Crimson Pro, serif' }}>
            Case Statistics Dashboard
          </h1>
          <p className="text-slate-600 text-lg max-w-2xl mx-auto">
            Anonymised insights from cases managed through our platform. Understanding patterns can help inform your appeal strategy.
          </p>
        </div>
      </section>

      {/* Stats Content */}
      <main className="max-w-6xl mx-auto px-6 pb-16">
        {/* Overview Cards */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 md:gap-6 mb-10">
          <Card className="bg-white border-slate-200 shadow-sm hover:shadow-md transition-shadow">
            <CardContent className="p-6 text-center">
              <div className="w-14 h-14 bg-blue-100 rounded-2xl flex items-center justify-center mx-auto mb-4">
                <Gavel className="w-7 h-7 text-blue-600" />
              </div>
              <p className="text-3xl font-bold text-slate-900">{stats?.overview?.total_cases || 0}</p>
              <p className="text-sm text-slate-600 mt-1">Total Cases</p>
            </CardContent>
          </Card>
          
          <Card className="bg-white border-slate-200 shadow-sm hover:shadow-md transition-shadow">
            <CardContent className="p-6 text-center">
              <div className="w-14 h-14 bg-emerald-100 rounded-2xl flex items-center justify-center mx-auto mb-4">
                <FileText className="w-7 h-7 text-emerald-600" />
              </div>
              <p className="text-3xl font-bold text-slate-900">{stats?.overview?.total_documents || 0}</p>
              <p className="text-sm text-slate-600 mt-1">Documents Uploaded</p>
            </CardContent>
          </Card>
          
          <Card className="bg-white border-slate-200 shadow-sm hover:shadow-md transition-shadow">
            <CardContent className="p-6 text-center">
              <div className="w-14 h-14 bg-blue-100 rounded-2xl flex items-center justify-center mx-auto mb-4">
                <TrendingUp className="w-7 h-7 text-red-600" />
              </div>
              <p className="text-3xl font-bold text-slate-900">{stats?.overview?.total_reports || 0}</p>
              <p className="text-sm text-slate-600 mt-1">Reports Generated</p>
            </CardContent>
          </Card>
          
          <Card className="bg-white border-slate-200 shadow-sm hover:shadow-md transition-shadow">
            <CardContent className="p-6 text-center">
              <div className="w-14 h-14 bg-purple-100 rounded-2xl flex items-center justify-center mx-auto mb-4">
                <Shield className="w-7 h-7 text-purple-600" />
              </div>
              <p className="text-3xl font-bold text-slate-900">{stats?.overview?.total_grounds_identified || 0}</p>
              <p className="text-sm text-slate-600 mt-1">Grounds Identified</p>
            </CardContent>
          </Card>
        </div>

        {/* Charts Section */}
        <div className="grid md:grid-cols-2 gap-6 md:gap-8 mb-10">
          {/* Cases by Offence Type */}
          <Card className="bg-white border-slate-200 shadow-sm">
            <CardHeader className="pb-2">
              <CardTitle className="text-lg font-semibold text-slate-900 flex items-center gap-2" style={{ fontFamily: 'Crimson Pro, serif' }}>
                <div className="w-8 h-8 rounded-lg bg-blue-100 flex items-center justify-center">
                  <AlertTriangle className="w-4 h-4 text-red-600" />
                </div>
                Cases by Offence Type
              </CardTitle>
            </CardHeader>
            <CardContent>
              {stats?.cases_by_offence?.length > 0 ? (
                <div className="space-y-3">
                  {stats.cases_by_offence.slice(0, 8).map((item, index) => (
                    <div key={index} className="flex items-center gap-3">
                      <div className="w-28 text-sm text-slate-600 truncate">{item.category}</div>
                      <div className="flex-1 bg-slate-100 rounded-full h-7 overflow-hidden">
                        <div 
                          className={`h-full ${getOffenceColor(item.key)} rounded-full flex items-center justify-end pr-3 transition-all duration-500`}
                          style={{ width: `${Math.max((item.count / maxOffenceCount) * 100, 15)}%` }}
                        >
                          <span className="text-xs font-semibold text-white">{item.count}</span>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="text-center py-12">
                  <div className="w-12 h-12 bg-slate-100 rounded-xl flex items-center justify-center mx-auto mb-3">
                    <BarChart3 className="w-6 h-6 text-slate-600" />
                  </div>
                  <p className="text-slate-600">No data available yet</p>
                </div>
              )}
            </CardContent>
          </Card>

          {/* Cases by State */}
          <Card className="bg-white border-slate-200 shadow-sm">
            <CardHeader className="pb-2">
              <CardTitle className="text-lg font-semibold text-slate-900 flex items-center gap-2" style={{ fontFamily: 'Crimson Pro, serif' }}>
                <div className="w-8 h-8 rounded-lg bg-blue-100 flex items-center justify-center">
                  <MapPin className="w-4 h-4 text-blue-600" />
                </div>
                Cases by State
              </CardTitle>
            </CardHeader>
            <CardContent>
              {stats?.cases_by_state?.length > 0 ? (
                <div className="space-y-3">
                  {stats.cases_by_state.map((item, index) => (
                    <div key={index} className="flex items-center gap-3">
                      <div className="w-36 text-sm text-slate-600 truncate">{item.state}</div>
                      <div className="flex-1 bg-slate-100 rounded-full h-7 overflow-hidden">
                        <div 
                          className={`h-full ${getStateColor(item.key)} rounded-full flex items-center justify-end pr-3 transition-all duration-500`}
                          style={{ width: `${Math.max((item.count / maxStateCount) * 100, 15)}%` }}
                        >
                          <span className="text-xs font-semibold text-white">{item.count}</span>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="text-center py-12">
                  <div className="w-12 h-12 bg-slate-100 rounded-xl flex items-center justify-center mx-auto mb-3">
                    <MapPin className="w-6 h-6 text-slate-600" />
                  </div>
                  <p className="text-slate-600">No data available yet</p>
                </div>
              )}
            </CardContent>
          </Card>
        </div>

        {/* Grounds Analysis */}
        <div className="grid md:grid-cols-2 gap-6 md:gap-8 mb-10">
          {/* Grounds by Type */}
          <Card className="bg-white border-slate-200 shadow-sm">
            <CardHeader className="pb-2">
              <CardTitle className="text-lg font-semibold text-slate-900 flex items-center gap-2" style={{ fontFamily: 'Crimson Pro, serif' }}>
                <div className="w-8 h-8 rounded-lg bg-purple-100 flex items-center justify-center">
                  <Shield className="w-4 h-4 text-purple-600" />
                </div>
                Most Common Appeal Grounds
              </CardTitle>
            </CardHeader>
            <CardContent>
              {stats?.grounds_by_type?.length > 0 ? (
                <div className="space-y-2">
                  {stats.grounds_by_type.slice(0, 6).map((item, index) => (
                    <div key={index} className="flex items-center justify-between p-3 bg-slate-50 rounded-xl hover:bg-slate-100 transition-colors">
                      <span className="text-sm font-medium text-slate-900">{item.type}</span>
                      <span className="text-sm font-bold text-slate-900 bg-white px-3 py-1 rounded-lg border border-slate-200">
                        {item.count}
                      </span>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="text-center py-12">
                  <div className="w-12 h-12 bg-slate-100 rounded-xl flex items-center justify-center mx-auto mb-3">
                    <Shield className="w-6 h-6 text-slate-600" />
                  </div>
                  <p className="text-slate-600">No data available yet</p>
                </div>
              )}
            </CardContent>
          </Card>

          {/* Grounds by Strength */}
          <Card className="bg-white border-slate-200 shadow-sm">
            <CardHeader className="pb-2">
              <CardTitle className="text-lg font-semibold text-slate-900 flex items-center gap-2" style={{ fontFamily: 'Crimson Pro, serif' }}>
                <div className="w-8 h-8 rounded-lg bg-emerald-100 flex items-center justify-center">
                  <TrendingUp className="w-4 h-4 text-emerald-600" />
                </div>
                Ground Strength Distribution
              </CardTitle>
            </CardHeader>
            <CardContent>
              {stats?.grounds_by_strength?.length > 0 ? (
                <div className="flex flex-col items-center justify-center py-6">
                  <div className="flex gap-6 mb-6">
                    {stats.grounds_by_strength.map((item, index) => (
                      <div key={index} className="text-center">
                        <div className={`w-20 h-20 ${getStrengthColor(item.strength)} rounded-2xl flex items-center justify-center mb-3 shadow-lg`}>
                          <span className="text-2xl font-bold text-white">{item.count}</span>
                        </div>
                        <p className="text-sm font-medium text-slate-900">{item.strength}</p>
                      </div>
                    ))}
                  </div>
                  <p className="text-xs text-slate-600 text-center">
                    Strong grounds have the highest likelihood of success on appeal
                  </p>
                </div>
              ) : (
                <div className="text-center py-12">
                  <div className="w-12 h-12 bg-slate-100 rounded-xl flex items-center justify-center mx-auto mb-3">
                    <TrendingUp className="w-6 h-6 text-slate-600" />
                  </div>
                  <p className="text-slate-600">No data available yet</p>
                </div>
              )}
            </CardContent>
          </Card>
        </div>

        {/* Key Insights */}
        {stats?.insights && (stats.overview?.total_cases > 0) && (
          <Card className="bg-gradient-to-r from-slate-900 to-indigo-950 border-0 overflow-hidden">
            <CardContent className="p-8 relative">
              <div className="absolute inset-0 opacity-10">
                <img 
                  src="https://images.unsplash.com/photo-1589578527966-fdac0f44566c?crop=entropy&cs=srgb&fm=jpg&q=85&w=800" 
                  alt=""
                  className="w-full h-full object-cover"
                />
              </div>
              <div className="relative z-10">
                <h3 className="text-2xl font-bold text-white mb-8 text-center" style={{ fontFamily: 'Crimson Pro, serif' }}>
                  Key Insights
                </h3>
                <div className="grid md:grid-cols-3 gap-8 text-center">
                  <div className="bg-white/10 backdrop-blur-sm rounded-2xl p-6">
                    <p className="text-blue-400 text-sm font-semibold mb-2">Most Common Offence</p>
                    <p className="text-white text-xl font-bold">{stats.insights.most_common_offence}</p>
                  </div>
                  <div className="bg-white/10 backdrop-blur-sm rounded-2xl p-6">
                    <p className="text-blue-400 text-sm font-semibold mb-2">Top Appeal Ground</p>
                    <p className="text-white text-xl font-bold">{stats.insights.most_common_ground}</p>
                  </div>
                  <div className="bg-white/10 backdrop-blur-sm rounded-2xl p-6">
                    <p className="text-blue-400 text-sm font-semibold mb-2">Busiest State</p>
                    <p className="text-white text-xl font-bold">{stats.insights.busiest_state}</p>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        )}

        {/* Disclaimer */}
        <div className="mt-10 p-5 bg-blue-50 border border-blue-200 rounded-2xl">
          <p className="text-sm text-blue-800">
            <strong>Note:</strong> These statistics are based on cases managed through this platform and are provided 
            for informational purposes only. They do not represent official court statistics or predict appeal outcomes. 
            Every case is unique and should be assessed on its own merits by qualified legal professionals.
          </p>
        </div>
      </main>

      {/* Footer CTA */}
      <section className="bg-slate-900 px-6 py-12 border-t border-slate-800">
        <div className="max-w-2xl mx-auto text-center">
          <h2 className="text-2xl font-bold text-white mb-4" style={{ fontFamily: 'Crimson Pro, serif' }}>
            Ready to Analyse Your Case?
          </h2>
          <p className="text-slate-400 mb-8">
            Let our AI help identify potential grounds for appeal in your case.
          </p>
          <Link to="/">
            <Button className="bg-gradient-to-r from-red-600 to-blue-700 text-white hover:from-blue-700 hover:to-blue-800 rounded-xl px-8 py-5 font-semibold shadow-lg shadow-red-600/20">
              Get Started Free
            </Button>
          </Link>
        </div>
      </section>
    </div>
  );
};

export default Statistics;
