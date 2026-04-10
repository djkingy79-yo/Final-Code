import React from "react";
import axios from "axios";
import { API } from "../App";

export default function DashboardPipelineSummary() {
  const [summary, setSummary] = React.useState(null);
  const [loading, setLoading] = React.useState(false);
  const [error, setError] = React.useState("");

  const loadSummary = React.useCallback(async () => {
    try {
      setLoading(true);
      setError("");
      const response = await axios.get(`${API}/pipeline/dashboard-summary`);
      setSummary(response.data);
    } catch (err) {
      setError(err.response?.data?.detail || err.message || "Failed to load pipeline dashboard summary");
    } finally {
      setLoading(false);
    }
  }, []);

  React.useEffect(() => {
    loadSummary();
  }, [loadSummary]);

  const totalCases = summary?.total_cases ?? 0;

  const pct = (value) => {
    if (!totalCases) return "0%";
    return `${Math.round((value / totalCases) * 100)}%`;
  };

  if (!summary && !loading) return null;

  return (
    <div className="rounded-xl border-2 border-slate-200 p-5 mb-4 bg-white shadow-sm" data-testid="dashboard-pipeline-summary">
      <div className="flex items-center justify-between gap-3 mb-3">
        <div className="font-bold text-base text-slate-900" style={{ fontFamily: "'Times New Roman', Times, serif" }}>Pipeline Portfolio Summary</div>
        <button
          type="button"
          onClick={loadSummary}
          disabled={loading}
          className="px-3 py-1.5 rounded-lg border text-xs font-semibold bg-blue-600 text-white hover:bg-blue-700 transition-colors"
          data-testid="dashboard-pipeline-refresh-btn"
        >
          {loading ? "Refreshing..." : "Refresh"}
        </button>
      </div>

      <div className="text-xs text-slate-600 mb-4">
        Portfolio-level view of staged processing across all cases.
      </div>

      {error ? (
        <div className="text-sm text-red-700" data-testid="dashboard-pipeline-error">{error}</div>
      ) : null}

      {!error && !summary && loading ? (
        <div className="text-sm opacity-75">Loading pipeline summary...</div>
      ) : null}

      {summary ? (
        <>
          <div className="grid grid-cols-2 md:grid-cols-5 gap-3">
            <div className="rounded-xl border-2 border-blue-200 bg-blue-50 p-4" data-testid="dashboard-pipeline-total">
              <div className="text-xs font-medium text-blue-600">Total Cases</div>
              <div className="text-2xl font-bold text-slate-900">{summary.total_cases ?? 0}</div>
            </div>

            <div className="rounded-xl border border-slate-200 bg-slate-50 p-4" data-testid="dashboard-pipeline-extracted">
              <div className="text-xs font-medium text-slate-600">With Case Extract</div>
              <div className="text-2xl font-bold text-slate-900">{summary.cases_with_case_extract ?? 0}</div>
              <div className="text-xs font-medium text-slate-500">{pct(summary.cases_with_case_extract ?? 0)}</div>
            </div>

            <div className="rounded-xl border border-slate-200 bg-slate-50 p-4" data-testid="dashboard-pipeline-classified">
              <div className="text-xs font-medium text-slate-600">With Classified Issues</div>
              <div className="text-2xl font-bold text-slate-900">{summary.cases_with_classified_issues ?? 0}</div>
              <div className="text-xs font-medium text-slate-500">{pct(summary.cases_with_classified_issues ?? 0)}</div>
            </div>

            <div className="rounded-xl border border-slate-200 bg-slate-50 p-4" data-testid="dashboard-pipeline-verified">
              <div className="text-xs font-medium text-slate-600">With Verified Issues</div>
              <div className="text-2xl font-bold text-slate-900">{summary.cases_with_verified_issues ?? 0}</div>
              <div className="text-xs font-medium text-slate-500">{pct(summary.cases_with_verified_issues ?? 0)}</div>
            </div>

            <div className="rounded-xl border border-slate-200 bg-slate-50 p-4" data-testid="dashboard-pipeline-reports">
              <div className="text-xs font-medium text-slate-600">With Pipeline Reports</div>
              <div className="text-2xl font-bold text-slate-900">{summary.cases_with_pipeline_reports ?? 0}</div>
              <div className="text-xs font-medium text-slate-500">{pct(summary.cases_with_pipeline_reports ?? 0)}</div>
            </div>
          </div>

          <div className="mt-4 text-xs text-slate-500">
            These figures reflect staged processing coverage across the user's portfolio and do not indicate legal merit or likely appeal outcome.
          </div>
        </>
      ) : null}
    </div>
  );
}
