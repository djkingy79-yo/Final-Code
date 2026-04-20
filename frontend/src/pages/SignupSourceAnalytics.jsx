import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import axios from "axios";
import { API } from "../App";
import { TrendingUp, ArrowLeft, Users, Target, Loader2 } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "../components/ui/card";
import { Button } from "../components/ui/button";
import { Badge } from "../components/ui/badge";

/**
 * /admin/analytics — Signup Source Conversion Dashboard
 * Admin-only. Shows which pages/CTAs are actually converting visitors into
 * signed-up users, using the `signup_source` captured at Google OAuth sign-up.
 */
const SignupSourceAnalytics = () => {
  const navigate = useNavigate();
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    const load = async () => {
      try {
        const res = await axios.get(`${API}/admin/signup-sources`);
        setData(res.data);
      } catch (err) {
        if (err.response?.status === 403) setError("Admin access required.");
        else if (err.response?.status === 401) setError("Please sign in.");
        else setError(err.response?.data?.detail || err.message || "Failed to load analytics.");
      } finally {
        setLoading(false);
      }
    };
    load();
  }, []);

  const prettyLabel = (s) => {
    // "success-stories-get-started" → "Success Stories / Get Started"
    // "pagecta-default" → "Banner CTA (default)"
    // "modal-landing" → "Modal / Landing"
    if (!s) return "Unknown";
    if (s.startsWith("pagecta-")) return `Banner CTA (${s.replace("pagecta-", "")})`;
    if (s.startsWith("modal-")) return `Modal / ${s.replace("modal-", "").replace(/-/g, " ")}`;
    return s.replace(/-/g, " ").replace(/\b\w/g, (c) => c.toUpperCase());
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-slate-50 flex items-center justify-center" data-testid="analytics-loading">
        <Loader2 className="w-8 h-8 animate-spin text-blue-600" />
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-slate-50 flex items-center justify-center p-6" data-testid="analytics-error">
        <Card className="max-w-md w-full border-red-200">
          <CardHeader>
            <CardTitle className="text-red-700">Unable to load</CardTitle>
            <CardDescription>{error}</CardDescription>
          </CardHeader>
          <CardContent>
            <Button onClick={() => navigate("/admin/dashboard")} variant="outline" data-testid="analytics-back-btn">
              <ArrowLeft className="w-4 h-4 mr-2" /> Back to Admin
            </Button>
          </CardContent>
        </Card>
      </div>
    );
  }

  const sources = data?.sources || [];
  const totalUsers = data?.total_users || 0;
  const usersWithSource = data?.users_with_source || 0;
  const totalVisits = data?.total_visits_tracked || 0;
  const maxCount = sources.length > 0 ? Math.max(...sources.map((s) => s.count)) : 1;

  return (
    <div className="min-h-screen bg-slate-50" data-testid="signup-source-analytics">
      {/* Header */}
      <div className="bg-white border-b border-slate-200">
        <div className="max-w-6xl mx-auto px-6 py-4 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <Button
              onClick={() => navigate("/admin/dashboard")}
              variant="ghost"
              size="sm"
              data-testid="analytics-back-btn"
            >
              <ArrowLeft className="w-4 h-4 mr-1" /> Admin
            </Button>
            <div>
              <h1 className="text-xl font-bold text-slate-900">Signup Source Analytics</h1>
              <p className="text-xs text-slate-600">Which CTAs actually convert visitors</p>
            </div>
          </div>
          <Badge className="bg-blue-100 text-blue-700 border-blue-200">
            <TrendingUp className="w-3 h-3 mr-1" />
            Live
          </Badge>
        </div>
      </div>

      <div className="max-w-6xl mx-auto px-6 py-8 space-y-6">
        {/* Summary stat cards */}
        <div className="grid grid-cols-1 sm:grid-cols-4 gap-4">
          <Card data-testid="analytics-stat-total">
            <CardHeader className="pb-2">
              <CardDescription className="flex items-center gap-1 text-xs">
                <Users className="w-3.5 h-3.5" /> Total Users
              </CardDescription>
              <CardTitle className="text-3xl font-bold">{totalUsers.toLocaleString()}</CardTitle>
            </CardHeader>
          </Card>
          <Card data-testid="analytics-stat-tracked">
            <CardHeader className="pb-2">
              <CardDescription className="flex items-center gap-1 text-xs">
                <Target className="w-3.5 h-3.5" /> Tracked Sign-ups
              </CardDescription>
              <CardTitle className="text-3xl font-bold">{usersWithSource.toLocaleString()}</CardTitle>
              <p className="text-xs text-slate-500 mt-1">
                {totalUsers > 0 ? Math.round((usersWithSource / totalUsers) * 100) : 0}% of total
              </p>
            </CardHeader>
          </Card>
          <Card data-testid="analytics-stat-visits">
            <CardHeader className="pb-2">
              <CardDescription className="flex items-center gap-1 text-xs">
                <TrendingUp className="w-3.5 h-3.5" /> Page Visits (tracked)
              </CardDescription>
              <CardTitle className="text-3xl font-bold">{totalVisits.toLocaleString()}</CardTitle>
              <p className="text-xs text-slate-500 mt-1">
                {totalVisits > 0
                  ? `overall ${((usersWithSource / totalVisits) * 100).toFixed(2)}% convert`
                  : "tracking starts on deploy"}
              </p>
            </CardHeader>
          </Card>
          <Card data-testid="analytics-stat-unique-sources">
            <CardHeader className="pb-2">
              <CardDescription className="flex items-center gap-1 text-xs">
                <TrendingUp className="w-3.5 h-3.5" /> Unique Sources
              </CardDescription>
              <CardTitle className="text-3xl font-bold">{sources.length}</CardTitle>
            </CardHeader>
          </Card>
        </div>

        {/* Sources bar chart */}
        <Card data-testid="analytics-sources-card">
          <CardHeader>
            <CardTitle className="text-lg">Top Converting Pages / CTAs</CardTitle>
            <CardDescription>
              Ranked by number of new sign-ups attributed. Each row shows the conversion rate
              (signups ÷ page visits) — <span className="text-emerald-600 font-semibold">green ≥ 5%</span>,
              <span className="text-amber-600 font-semibold"> amber 1–5%</span>,
              <span className="text-red-600 font-semibold"> red &lt; 1%</span>. Hover a row for raw counts + dates.
            </CardDescription>
          </CardHeader>
          <CardContent>
            {sources.length === 0 ? (
              <div className="text-center py-12 text-slate-500" data-testid="analytics-empty-state">
                <Target className="w-12 h-12 mx-auto mb-3 text-slate-300" />
                <p className="font-medium">No tracked sign-ups yet</p>
                <p className="text-sm mt-1">
                  As new users sign up via the CTAs on your pages, their conversion source will appear here.
                </p>
              </div>
            ) : (
              <div className="space-y-3">
                {sources.map((s, idx) => {
                  const pct = maxCount > 0 ? (s.count / maxCount) * 100 : 0;
                  const conv = s.conversion_rate;
                  const convColor =
                    conv == null ? "text-slate-400"
                    : conv >= 5 ? "text-emerald-600"
                    : conv >= 1 ? "text-amber-600"
                    : "text-red-600";
                  return (
                    <div
                      key={s.source}
                      className="group"
                      title={`First: ${s.first?.slice(0, 10) || "?"} · Last: ${s.last?.slice(0, 10) || "?"}${s.visits != null ? ` · ${s.visits} visits` : ""}`}
                      data-testid={`analytics-bar-${idx}`}
                    >
                      <div className="flex items-center justify-between mb-1">
                        <div className="flex items-center gap-2 min-w-0">
                          <Badge variant="outline" className="text-xs shrink-0">
                            #{idx + 1}
                          </Badge>
                          <span className="text-sm font-medium text-slate-800 truncate">
                            {prettyLabel(s.source)}
                          </span>
                          <span className="text-xs text-slate-400 font-mono truncate hidden sm:inline">
                            {s.source}
                          </span>
                        </div>
                        <div className="flex items-center gap-3 shrink-0 tabular-nums">
                          {conv != null && (
                            <span
                              className={`text-xs font-semibold ${convColor}`}
                              data-testid={`analytics-conv-${idx}`}
                              title={`${s.count} signups / ${s.visits} visits`}
                            >
                              {conv}%
                            </span>
                          )}
                          <span className="text-sm font-bold text-blue-700">
                            {s.count}
                          </span>
                        </div>
                      </div>
                      <div className="h-7 bg-slate-100 rounded overflow-hidden">
                        <div
                          className="h-full bg-gradient-to-r from-blue-600 to-blue-500 transition-all group-hover:from-blue-700 group-hover:to-blue-600"
                          style={{ width: `${pct}%` }}
                        />
                      </div>
                    </div>
                  );
                })}
              </div>
            )}
          </CardContent>
        </Card>

        {/* Explainer */}
        <Card className="border-slate-200 bg-slate-50">
          <CardContent className="pt-5 text-xs text-slate-600 space-y-2">
            <p>
              <strong>How this works:</strong> When a visitor clicks any "Get Started" / "Sign In" /
              "Contact" CTA on your site, a source label is attached to their session. When they complete
              Google sign-up, that label is permanently recorded on their user record. This page aggregates
              those labels so you can see which pages are actually converting traffic.
            </p>
            <p>
              <strong>Why "Tracked Sign-ups" may be lower than "Total Users":</strong> Users who signed up
              before this tracking was deployed won't have a source. New users from this point forward will.
            </p>
          </CardContent>
        </Card>
      </div>
    </div>
  );
};

export default SignupSourceAnalytics;
