/* ========================================================================
   DO NOT UNDO — ENTIRE FILE PROTECTED
   All features, functions, styles, and content in this file are approved
   and must be preserved. Do not remove, rename, or refactor any code.
   ======================================================================== */
import { useState, useEffect } from "react";
import { useNavigate, Link } from "react-router-dom";
import axios from "axios";
import { Scale, Users, Eye, FolderOpen, TrendingUp, ArrowLeft, Shield, Menu, X, Calendar } from "lucide-react";
import { Button } from "../components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "../components/ui/card";
import { API } from "../App";
import { toast } from "sonner";
import { useTheme } from "../contexts/ThemeContext";

const AdminStats = () => {

  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const navigate = useNavigate();

  useEffect(() => {
    const fetchStats = async () => {
      try {
        const response = await axios.get(`${API}/stats/visits`);
        setStats(response.data);
      } catch (err) {
        if (err.response?.status === 403) {
          setError("Admin access required");
          toast.error("You don't have admin access");
        } else if (err.response?.status === 401) {
          setError("Please log in first");
          navigate("/");
        } else {
          setError("Failed to load stats");
        }
      } finally {
        setLoading(false);
      }
    };
    fetchStats();
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [navigate]);

  if (loading) {
    return (
      <div className="min-h-screen bg-white flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-red-600 mx-auto mb-4"></div>
          <p className="text-slate-600">Loading admin statistics...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-white flex items-center justify-center">
        <div className="text-center max-w-md mx-auto px-6">
          <div className="w-20 h-20 bg-red-100 rounded-2xl flex items-center justify-center mx-auto mb-6">
            <Shield className="w-10 h-10 text-red-600" />
          </div>
          <h2 className="text-2xl font-bold text-slate-900 mb-3" style={{ fontFamily: 'Crimson Pro, serif' }}>
            Access Denied
          </h2>
          <p className="text-slate-600 mb-6">{error}</p>
          <Button 
            onClick={() => navigate("/dashboard")} 
            className="bg-gradient-to-r from-red-600 to-blue-700 text-white hover:from-blue-700 hover:to-blue-800 rounded-xl px-8 py-5 font-semibold"
          >
            Go to Dashboard
          </Button>
        </div>
      </div>
    );
  }

  const maxDailyCount = Math.max(...(stats?.daily_stats?.map(d => d.count) || [1]));

  return (
    <div className="min-h-screen bg-white" style={{ fontFamily: 'Manrope, sans-serif' }}>
      {/* Header */}
      <header className="bg-slate-900 sticky top-0 z-50">
        <div className="max-w-6xl mx-auto px-6 py-4 flex items-center justify-between">
          <Link to="/dashboard" className="flex items-center gap-3">
            <div className="w-9 h-9 rounded-lg bg-red-600 flex items-center justify-center">
              <Scale className="w-5 h-5 text-white" />
            </div>
            <span className="text-lg font-semibold text-white tracking-tight hidden sm:block" style={{ fontFamily: 'Crimson Pro, serif' }}>
              Admin Dashboard
            </span>
          </Link>
          <div className="hidden md:flex items-center gap-4">
<Button 
              onClick={() => navigate("/dashboard")} 
              variant="outline" 
              className="border-slate-600 text-slate-300 hover:bg-slate-800 rounded-lg"
            >
              <ArrowLeft className="w-4 h-4 mr-2" />
              Back to Dashboard
            </Button>
          </div>
          <button className="md:hidden p-2 text-white" onClick={() => setMobileMenuOpen(!mobileMenuOpen)}>
            {mobileMenuOpen ? <X className="w-6 h-6" /> : <Menu className="w-6 h-6" />}
          </button>
        </div>
        {mobileMenuOpen && (
          <div className="md:hidden bg-slate-800 border-t border-slate-700 px-6 py-4 space-y-3">
<button 
              onClick={() => navigate("/dashboard")} 
              className="flex items-center gap-2 py-2 text-blue-500 hover:text-blue-400 w-full"
            >
              <ArrowLeft className="w-5 h-5" />
              Back to Dashboard
            </button>
          </div>
        )}
      </header>

      {/* Hero Section */}
      <section className="relative py-12 px-6 overflow-hidden">
        <div className="absolute inset-0 z-0">
          <img 
            src="https://images.unsplash.com/photo-1551288049-bebda4e38f71?crop=entropy&cs=srgb&fm=jpg&q=85&w=1920" 
            alt=""
            className="w-full h-full object-cover opacity-5"
          />
          <div className="absolute inset-0 bg-gradient-to-b from-background via-background/95 to-background" />
        </div>
        
        <div className="max-w-6xl mx-auto relative z-10">
          <div className="flex items-center gap-4 mb-2">
            <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-blue-500 to-blue-700 flex items-center justify-center shadow-lg shadow-blue-500/30">
              <TrendingUp className="w-6 h-6 text-white" />
            </div>
            <div>
              <p className="text-red-600 font-semibold text-xs uppercase tracking-widest">Admin Only</p>
              <h1 className="text-3xl font-bold text-slate-900" style={{ fontFamily: 'Crimson Pro, serif' }}>
                Site Analytics
              </h1>
            </div>
          </div>
        </div>
      </section>

      <main className="max-w-6xl mx-auto px-6 pb-16">
        {/* Stats Cards */}
        <div className="grid md:grid-cols-3 gap-6 mb-10">
          <Card className="bg-white border-slate-200 shadow-sm hover:shadow-md transition-shadow">
            <CardContent className="p-6">
              <div className="flex items-center gap-4">
                <div className="w-14 h-14 bg-blue-100 rounded-2xl flex items-center justify-center">
                  <Eye className="w-7 h-7 text-blue-600" />
                </div>
                <div>
                  <p className="text-sm text-slate-600 font-medium">Total Page Views</p>
                  <p className="text-3xl font-bold text-slate-900">{stats?.total_visits?.toLocaleString() || 0}</p>
                </div>
              </div>
            </CardContent>
          </Card>

          <Card className="bg-white border-slate-200 shadow-sm hover:shadow-md transition-shadow">
            <CardContent className="p-6">
              <div className="flex items-center gap-4">
                <div className="w-14 h-14 bg-emerald-100 rounded-2xl flex items-center justify-center">
                  <Users className="w-7 h-7 text-emerald-600" />
                </div>
                <div>
                  <p className="text-sm text-slate-600 font-medium">Registered Users</p>
                  <p className="text-3xl font-bold text-slate-900">{stats?.total_users?.toLocaleString() || 0}</p>
                </div>
              </div>
            </CardContent>
          </Card>

          <Card className="bg-white border-slate-200 shadow-sm hover:shadow-md transition-shadow">
            <CardContent className="p-6">
              <div className="flex items-center gap-4">
                <div className="w-14 h-14 bg-blue-100 rounded-2xl flex items-center justify-center">
                  <FolderOpen className="w-7 h-7 text-red-600" />
                </div>
                <div>
                  <p className="text-sm text-slate-600 font-medium">Total Cases Created</p>
                  <p className="text-3xl font-bold text-slate-900">{stats?.total_cases?.toLocaleString() || 0}</p>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Daily Stats Chart */}
        <Card className="bg-white border-slate-200 shadow-sm">
          <CardHeader>
            <CardTitle className="text-xl font-semibold text-slate-900 flex items-center gap-3" style={{ fontFamily: 'Crimson Pro, serif' }}>
              <div className="w-10 h-10 rounded-xl bg-indigo-100 flex items-center justify-center">
                <Calendar className="w-5 h-5 text-indigo-600" />
              </div>
              Last 7 Days Activity
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {stats?.daily_stats?.map((day, index) => (
                <div key={day.date} className="flex items-center gap-4">
                  <span className="text-sm text-slate-600 w-28 font-medium">{day.date}</span>
                  <div className="flex-1 bg-slate-100 rounded-full h-8 overflow-hidden">
                    <div 
                      className="bg-gradient-to-r from-blue-500 to-red-600 h-full rounded-full flex items-center justify-end pr-3 transition-all duration-500"
                      style={{ 
                        width: `${Math.max((day.count / maxDailyCount) * 100, day.count > 0 ? 10 : 0)}%`,
                        minWidth: day.count > 0 ? '40px' : '0'
                      }}
                    >
                      {day.count > 0 && (
                        <span className="text-xs font-semibold text-white">{day.count}</span>
                      )}
                    </div>
                  </div>
                  <span className="text-sm font-medium text-slate-600 w-20 text-right">
                    {day.count} visits
                  </span>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>

        <p className="text-center text-sm text-slate-600 mt-8">
          Stats update in real-time as visitors access the site
        </p>
      </main>
    </div>
  );
};

export default AdminStats;
