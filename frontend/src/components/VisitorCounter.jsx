/* ========================================================================
   DO NOT UNDO — ENTIRE FILE PROTECTED
   All features, functions, styles, and content in this file are approved
   and must be preserved. Do not remove, rename, or refactor any code.
   ======================================================================== */
import { useState, useEffect } from "react";
import axios from "axios";
import { Users, Eye, Briefcase, UserCheck } from "lucide-react";
import { API } from "../App";

const VisitorCounter = ({ variant = "full" }) => {
  const [stats, setStats] = useState({
    total_visitors: 0,
    today_visitors: 0,
    registered_users: 0,
    cases_created: 0
  });
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Track this visit
    trackVisit();
    // Fetch stats
    fetchStats();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const trackVisit = async () => {
    try {
      await axios.post(`${API}/analytics/track-visit`);
    } catch (error) {
      // Silent fail for tracking
    }
  };

  const fetchStats = async () => {
    try {
      const response = await axios.get(`${API}/analytics/visitor-count`);
      setStats(response.data);
    } catch (error) {
      console.error("Failed to fetch visitor stats");
    } finally {
      setLoading(false);
    }
  };

  const formatNumber = (num) => {
    if (num >= 1000000) return (num / 1000000).toFixed(1) + "M";
    if (num >= 1000) return (num / 1000).toFixed(1) + "K";
    return num.toLocaleString();
  };

  if (loading) {
    return (
      <div className="animate-pulse flex gap-4">
        <div className="h-8 w-24 bg-slate-200 rounded"></div>
        <div className="h-8 w-24 bg-slate-200 rounded"></div>
      </div>
    );
  }

  // Compact variant - just shows total visitors
  if (variant === "compact") {
    return (
      <div className="inline-flex items-center gap-2 px-3 py-1.5 bg-emerald-500/10 border border-emerald-500/20 rounded-full">
        <Eye className="w-4 h-4 text-emerald-500" />
        <span className="text-sm font-semibold text-emerald-600">
          {formatNumber(stats.total_visitors)} visitors
        </span>
      </div>
    );
  }

  // Badge variant - small inline badge
  if (variant === "badge") {
    return (
      <span className="inline-flex items-center gap-1 text-xs text-slate-600">
        <Eye className="w-3 h-3" />
        {formatNumber(stats.total_visitors)}
      </span>
    );
  }

  // Full variant - shows all stats
  return (
    <div className="grid grid-cols-2 sm:grid-cols-4 gap-4" data-testid="visitor-counter">
      {/* Total Visitors */}
      <div className="bg-gradient-to-br from-blue-50 to-blue-100 rounded-xl p-4 border border-blue-200 text-center">
        <Eye className="w-6 h-6 text-blue-600 mx-auto mb-2" />
        <p className="text-2xl font-bold text-blue-700" style={{ fontFamily: 'Crimson Pro, serif' }}>
          {formatNumber(stats.total_visitors)}
        </p>
        <p className="text-xs text-blue-600">Total Visitors</p>
      </div>

      {/* Today's Visitors */}
      <div className="bg-gradient-to-br from-emerald-50 to-emerald-100 rounded-xl p-4 border border-emerald-200 text-center">
        <Users className="w-6 h-6 text-emerald-600 mx-auto mb-2" />
        <p className="text-2xl font-bold text-emerald-700" style={{ fontFamily: 'Crimson Pro, serif' }}>
          {formatNumber(stats.today_visitors)}
        </p>
        <p className="text-xs text-emerald-600">Today</p>
      </div>

      {/* Registered Users */}
      <div className="bg-gradient-to-br from-purple-50 to-purple-100 rounded-xl p-4 border border-purple-200 text-center">
        <UserCheck className="w-6 h-6 text-purple-600 mx-auto mb-2" />
        <p className="text-2xl font-bold text-purple-700" style={{ fontFamily: 'Crimson Pro, serif' }}>
          {formatNumber(stats.registered_users)}
        </p>
        <p className="text-xs text-purple-600">Users</p>
      </div>

      {/* Cases Created */}
      <div className="bg-gradient-to-br from-blue-50 to-blue-100 rounded-xl p-4 border border-blue-200 text-center">
        <Briefcase className="w-6 h-6 text-red-600 mx-auto mb-2" />
        <p className="text-2xl font-bold text-blue-700" style={{ fontFamily: 'Crimson Pro, serif' }}>
          {formatNumber(stats.cases_created)}
        </p>
        <p className="text-xs text-red-600">Cases</p>
      </div>
    </div>
  );
};

export default VisitorCounter;
