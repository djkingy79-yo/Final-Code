/* ========================================================================
   DO NOT UNDO — ENTIRE FILE PROTECTED
   All features, functions, styles, and content in this file are approved
   and must be preserved. Do not remove, rename, or refactor any code.
   ======================================================================== */
import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import axios from "axios";
import { API } from "../App";
import { toast } from "sonner";
import {
  Users, Briefcase, FileText, TrendingUp, Activity, MessageCircle,
  Heart, Calendar, Eye, ArrowUp, ArrowDown, BarChart3, CreditCard,
  CheckCircle, Clock, DollarSign, Building2, Loader2
} from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "../components/ui/card";
import { Button } from "../components/ui/button";
import { Badge } from "../components/ui/badge";

const AdminDashboard = () => {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(true);
  const [stats, setStats] = useState(null);
  const [error, setError] = useState("");
  const [pendingPayments, setPendingPayments] = useState([]);
  const [confirmingRef, setConfirmingRef] = useState(null);
  const [refreshingPayments, setRefreshingPayments] = useState(false);

  useEffect(() => {
    fetchStats();
    fetchPendingPayments();
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const fetchStats = async () => {
    try {
      const response = await axios.get(`${API}/analytics/dashboard`);
      setStats(response.data);
    } catch (err) {
      if (err.response?.status === 403) {
        setError("Admin access required");
      } else if (err.response?.status === 401) {
        navigate("/");
      } else {
        setError("Failed to load analytics");
      }
    } finally {
      setLoading(false);
    }
  };

  const fetchPendingPayments = async () => {
    setRefreshingPayments(true);
    try {
      const response = await axios.get(`${API}/payments/payid/pending`);
      setPendingPayments(response.data.pending_payments || []);
      toast.success("PayID payments refreshed");
    } catch (err) {
      console.error("PayID fetch error:", err);
      if (err.response?.status === 403) {
        toast.error("Admin access required to view payments");
      } else if (err.response?.status === 401) {
        toast.error("Session expired — please log in again");
      } else {
        toast.error("Failed to fetch pending payments");
      }
    } finally {
      setRefreshingPayments(false);
    }
  };

  const confirmPayment = async (reference) => {
    setConfirmingRef(reference);
    try {
      await axios.post(`${API}/payments/payid/admin-confirm/${reference}`);
      toast.success("Payment confirmed! Feature unlocked for user.");
      fetchPendingPayments();
    } catch (err) {
      toast.error(err.response?.data?.detail || "Failed to confirm payment");
    } finally {
      setConfirmingRef(null);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-white flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-red-600 mx-auto mb-4"></div>
          <p className="text-slate-600">Loading analytics...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-white flex items-center justify-center p-6">
        <Card className="max-w-md">
          <CardContent className="pt-6 text-center">
            <p className="text-red-600 font-medium mb-4">{error}</p>
            <button
              onClick={() => navigate("/")}
              className="inline-flex items-center rounded-xl bg-blue-700 px-4 py-2 font-semibold text-white hover:bg-blue-600"
            >
              Go to Home
            </button>
          </CardContent>
        </Card>
      </div>
    );
  }

  if (!stats) return null;

  const StatCard = ({ title, value, icon: Icon, subtitle, trend, color = "blue" }) => {
    const colorClasses = {
      blue: "bg-blue-100 text-blue-600",
      emerald: "bg-emerald-100 text-emerald-600",
      blue_mapped: "bg-blue-100 text-red-600",
      purple: "bg-purple-100 text-purple-600",
      pink: "bg-pink-100 text-pink-600",
      indigo: "bg-indigo-100 text-indigo-600",
    };

    return (
      <Card>
        <CardContent className="pt-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-slate-600 mb-1">{title}</p>
              <p className="text-3xl font-bold text-slate-900">{value.toLocaleString()}</p>
              {subtitle && (
                <p className="text-xs text-slate-600 mt-1">{subtitle}</p>
              )}
              {trend && (
                <div className="flex items-center gap-1 mt-2 text-xs">
                  {trend > 0 ? (
                    <ArrowUp className="w-3 h-3 text-emerald-600" />
                  ) : (
                    <ArrowDown className="w-3 h-3 text-red-600" />
                  )}
                  <span className={trend > 0 ? "text-emerald-600" : "text-red-600"}>
                    {Math.abs(trend)} this week
                  </span>
                </div>
              )}
            </div>
            <div className={`w-12 h-12 rounded-xl flex items-center justify-center ${colorClasses[color]}`}>
              <Icon className="w-6 h-6" />
            </div>
          </div>
        </CardContent>
      </Card>
    );
  };

  return (
    <div className="min-h-screen bg-white">
      {/* Header */}
      <div className="bg-slate-900 text-white py-8 px-6">
        <div className="max-w-7xl mx-auto">
          <h1 className="text-3xl font-bold mb-2">Analytics Dashboard</h1>
          <p className="text-slate-400">Appeal Case Manager - Usage Statistics</p>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-6 py-8">
        
        {/* Live Visitor Stats - Prominent Section */}
        <Card className="mb-8 bg-gradient-to-r from-indigo-50 to-purple-50 border-indigo-200">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Eye className="w-5 h-5 text-indigo-600" />
              Live Visitor Statistics
            </CardTitle>
            <CardDescription>Real-time tracking of app visitors</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <div className="bg-white rounded-xl p-4 text-center border border-indigo-200">
                <Eye className="w-6 h-6 text-indigo-600 mx-auto mb-2" />
                <p className="text-2xl font-bold text-indigo-700">{stats.visits?.total || 0}</p>
                <p className="text-xs text-indigo-600">Total Visitors</p>
              </div>
              <div className="bg-white rounded-xl p-4 text-center border border-emerald-200">
                <Users className="w-6 h-6 text-emerald-600 mx-auto mb-2" />
                <p className="text-2xl font-bold text-emerald-700">{stats.visits?.last_7d || 0}</p>
                <p className="text-xs text-emerald-600">Last 7 Days</p>
              </div>
              <div className="bg-white rounded-xl p-4 text-center border border-blue-200">
                <TrendingUp className="w-6 h-6 text-red-600 mx-auto mb-2" />
                <p className="text-2xl font-bold text-blue-700">{stats.visits?.last_30d || 0}</p>
                <p className="text-xs text-red-600">Last 30 Days</p>
              </div>
              <div className="bg-white rounded-xl p-4 text-center border border-purple-200">
                <Activity className="w-6 h-6 text-purple-600 mx-auto mb-2" />
                <p className="text-2xl font-bold text-purple-700">{stats.users?.total || 0}</p>
                <p className="text-xs text-purple-600">Registered Users</p>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Key Metrics Grid */}
        <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          <StatCard
            title="Total Users"
            value={stats.users.total}
            icon={Users}
            subtitle={`${stats.users.new_7d} new this week`}
            trend={stats.users.new_7d}
            color="blue"
          />
          <StatCard
            title="Total Cases"
            value={stats.cases.total}
            icon={Briefcase}
            subtitle={`${stats.cases.new_7d} new this week`}
            trend={stats.cases.new_7d}
            color="emerald"
          />
          <StatCard
            title="Documents Uploaded"
            value={stats.documents.total}
            icon={FileText}
            subtitle={`${stats.documents.uploaded_7d} this week`}
            color="blue"
          />
          <StatCard
            title="Site Visits"
            value={stats.visits.total}
            icon={Eye}
            subtitle={`${stats.visits.last_7d} in last 7 days`}
            color="purple"
          />
        </div>

        {/* Secondary Metrics */}
        <div className="grid md:grid-cols-3 lg:grid-cols-6 gap-4 mb-8">
          <Card>
            <CardContent className="pt-6 text-center">
              <Calendar className="w-8 h-8 text-indigo-600 mx-auto mb-2" />
              <p className="text-2xl font-bold">{stats.engagement.deadlines_tracked}</p>
              <p className="text-xs text-slate-600">Deadlines Tracked</p>
            </CardContent>
          </Card>
          <Card>
            <CardContent className="pt-6 text-center">
              <BarChart3 className="w-8 h-8 text-emerald-600 mx-auto mb-2" />
              <p className="text-2xl font-bold">{stats.engagement.reports_generated}</p>
              <p className="text-xs text-slate-600">Reports Generated</p>
            </CardContent>
          </Card>
          <Card>
            <CardContent className="pt-6 text-center">
              <MessageCircle className="w-8 h-8 text-blue-600 mx-auto mb-2" />
              <p className="text-2xl font-bold">{stats.engagement.contact_messages}</p>
              <p className="text-xs text-slate-600">Contact Messages</p>
            </CardContent>
          </Card>
          <Card>
            <CardContent className="pt-6 text-center">
              <Heart className="w-8 h-8 text-pink-600 mx-auto mb-2" />
              <p className="text-2xl font-bold">{stats.engagement.success_stories}</p>
              <p className="text-xs text-slate-600">Success Stories</p>
            </CardContent>
          </Card>
          <Card>
            <CardContent className="pt-6 text-center">
              <Activity className="w-8 h-8 text-red-600 mx-auto mb-2" />
              <p className="text-2xl font-bold">{stats.engagement.notes_created}</p>
              <p className="text-xs text-slate-600">Notes Created</p>
            </CardContent>
          </Card>
          <Card>
            <CardContent className="pt-6 text-center">
              <TrendingUp className="w-8 h-8 text-purple-600 mx-auto mb-2" />
              <p className="text-2xl font-bold">{stats.users.new_30d}</p>
              <p className="text-xs text-slate-600">Users (30d)</p>
            </CardContent>
          </Card>
        </div>

        {/* User Breakdown */}
        <div className="grid md:grid-cols-2 gap-6 mb-8">
          <Card>
            <CardHeader>
              <CardTitle>Users by Auth Type</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                <div>
                  <div className="flex justify-between mb-1">
                    <span className="text-sm text-slate-600">Email/Password</span>
                    <span className="font-semibold">{stats.users.by_auth_type.email}</span>
                  </div>
                  <div className="h-2 bg-slate-100 rounded-full overflow-hidden">
                    <div 
                      className="h-full bg-blue-600"
                      style={{ width: `${(stats.users.by_auth_type.email / stats.users.total) * 100}%` }}
                    />
                  </div>
                </div>
                <div>
                  <div className="flex justify-between mb-1">
                    <span className="text-sm text-slate-600">Google OAuth</span>
                    <span className="font-semibold">{stats.users.by_auth_type.google}</span>
                  </div>
                  <div className="h-2 bg-slate-100 rounded-full overflow-hidden">
                    <div 
                      className="h-full bg-emerald-600"
                      style={{ width: `${(stats.users.by_auth_type.google / stats.users.total) * 100}%` }}
                    />
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Cases by State</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-2">
                {Object.entries(stats.cases.by_state).map(([state, count]) => (
                  <div key={state} className="flex justify-between items-center">
                    <span className="text-sm font-medium">{state}</span>
                    <span className="text-sm text-slate-600">{count} cases</span>
                  </div>
                ))}
                {Object.keys(stats.cases.by_state).length === 0 && (
                  <p className="text-sm text-slate-600">No cases yet</p>
                )}
              </div>
            </CardContent>
          </Card>
        </div>

        {/* 30-Day Trend Chart (Simple) */}
        <Card>
          <CardHeader>
            <CardTitle>30-Day Activity Trend</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <div>
                <p className="text-sm font-medium mb-2">New Users</p>
                <div className="flex items-end gap-1 h-24">
                  {stats.daily_stats.slice(-14).map((day, idx) => (
                    <div key={idx} className="flex-1 bg-blue-200 rounded-t"
                         style={{ height: `${Math.max((day.users / Math.max(...stats.daily_stats.map(d => d.users))) * 100, 5)}%` }}
                         title={`${day.date}: ${day.users} users`}
                    />
                  ))}
                </div>
              </div>
              <div>
                <p className="text-sm font-medium mb-2">New Cases</p>
                <div className="flex items-end gap-1 h-24">
                  {stats.daily_stats.slice(-14).map((day, idx) => (
                    <div key={idx} className="flex-1 bg-emerald-200 rounded-t"
                         style={{ height: `${Math.max((day.cases / Math.max(...stats.daily_stats.map(d => d.cases))) * 100, 5)}%` }}
                         title={`${day.date}: ${day.cases} cases`}
                    />
                  ))}
                </div>
              </div>
            </div>
            <p className="text-xs text-slate-600 mt-4 text-center">Last 14 days</p>
          </CardContent>
        </Card>

        {/* Pending PayID Payments Section */}
        <Card className="mt-8" data-testid="pending-payments-section">
          <CardHeader>
            <div className="flex items-center justify-between">
              <div>
                <CardTitle className="flex items-center gap-2">
                  <Building2 className="w-5 h-5 text-emerald-600" />
                  Pending PayID Payments
                </CardTitle>
                <CardDescription>Bank transfers awaiting verification</CardDescription>
              </div>
              <Button 
                size="sm" 
                onClick={fetchPendingPayments}
                disabled={refreshingPayments}
                className="shrink-0 bg-blue-700 text-white hover:bg-blue-600"
                data-testid="refresh-payments-btn"
              >
                {refreshingPayments ? (
                  <><Loader2 className="w-4 h-4 mr-1.5 animate-spin" />Refreshing...</>
                ) : (
                  "Refresh"
                )}
              </Button>
            </div>
          </CardHeader>
          <CardContent>
            {pendingPayments.length === 0 ? (
              <div className="text-center py-8 text-slate-600">
                <CheckCircle className="w-12 h-12 mx-auto mb-3 text-emerald-600 opacity-50" />
                <p>No pending payments to verify</p>
              </div>
            ) : (
              <div className="space-y-4">
                {pendingPayments.map((payment) => (
                  <div 
                    key={payment.reference} 
                    className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 p-4 bg-slate-50 rounded-xl border border-slate-200"
                  >
                    <div className="flex-1 min-w-0">
                      <div className="flex flex-wrap items-center gap-2 mb-2">
                        <span className="font-mono font-bold text-slate-900">{payment.reference}</span>
                        <Badge variant={payment.status === "pending_verification" ? "default" : "secondary"}>
                          {payment.status === "pending_verification" ? (
                            <><Clock className="w-3 h-3 mr-1" /> Awaiting Verification</>
                          ) : (
                            <><Clock className="w-3 h-3 mr-1" /> Pending</>
                          )}
                        </Badge>
                      </div>
                      <div className="grid grid-cols-2 sm:grid-cols-4 gap-2 text-sm text-slate-600">
                        <div>
                          <span className="text-xs opacity-75">Amount:</span>
                          <p className="font-semibold text-slate-900">${payment.amount} AUD</p>
                        </div>
                        <div>
                          <span className="text-xs opacity-75">Feature:</span>
                          <p className="text-slate-900">{payment.feature_type?.replace(/_/g, ' ')}</p>
                        </div>
                        <div>
                          <span className="text-xs opacity-75">Case:</span>
                          <p className="text-slate-900 truncate">{payment.case_id?.slice(0, 8)}...</p>
                        </div>
                        <div>
                          <span className="text-xs opacity-75">Created:</span>
                          <p className="text-slate-900">{new Date(payment.created_at).toLocaleDateString()}</p>
                        </div>
                      </div>
                    </div>
                    <Button
                      onClick={() => confirmPayment(payment.reference)}
                      disabled={confirmingRef === payment.reference}
                      className="bg-blue-700 hover:bg-blue-600 text-white shrink-0"
                      data-testid={`confirm-payment-${payment.reference}`}
                    >
                      {confirmingRef === payment.reference ? (
                        <><Loader2 className="w-4 h-4 mr-2 animate-spin" /> Confirming...</>
                      ) : (
                        <><CheckCircle className="w-4 h-4 mr-2" /> Confirm Payment</>
                      )}
                    </Button>
                  </div>
                ))}
              </div>
            )}
            <div className="mt-4 p-3 bg-blue-50 rounded-lg text-xs text-blue-800">
              <strong>How to verify:</strong> Check your bank statement for incoming transfers with the reference code shown. 
              Once you confirm receipt, click "Confirm Payment" to unlock the feature for the user.
            </div>
          </CardContent>
        </Card>

      </div>
    </div>
  );
};

export default AdminDashboard;
