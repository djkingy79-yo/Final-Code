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
    <div className="rounded-xl bg-blue-600 p-4 mb-4 text-white" data-testid="dashboard-pipeline-summary">
      <div className="flex items-center justify-between gap-3 mb-2">
        <div className="font-bold text-sm text-white">Pipeline Portfolio Summary</div>
        <button
          type="button"
          onClick={loadSummary}
          disabled={loading}
          className="px-2 py-1 rounded border border-white/40 text-xs font-bold text-white hover:bg-blue-500"
          data-testid="dashboard-pipeline-refresh-btn"
        >
          {loading ? "Refreshing..." : "Refresh"}
        </button>
      </div>

      <div className="text-xs text-white/80 mb-3">
        Portfolio-level view of staged processing across all cases.
      </div>

      {error ? (
        <div className="text-sm text-red-200 font-bold" data-testid="dashboard-pipeline-error">{error}</div>
      ) : null}

      {!error && !summary && loading ? (
        <div className="text-sm text-white/80">Loading pipeline summary...</div>
      ) : null}

      {summary ? (
        <>
          <div className="grid grid-cols-2 md:grid-cols-5 gap-3 text-sm">
            <div className="rounded-lg bg-white/15 p-3" data-testid="dashboard-pipeline-total">
              <div className="text-xs text-white/80 font-medium">Total Cases</div>
              <div className="text-lg font-bold text-white">{summary.total_cases ?? 0}</div>
            </div>

            <div className="rounded-lg bg-white/15 p-3" data-testid="dashboard-pipeline-extracted">
              <div className="text-xs text-white/80 font-medium">With Case Extract</div>
              <div className="text-lg font-bold text-white">{summary.cases_with_case_extract ?? 0}</div>
              <div className="text-xs text-white/70">{pct(summary.cases_with_case_extract ?? 0)}</div>
            </div>

            <div className="rounded-lg bg-white/15 p-3" data-testid="dashboard-pipeline-classified">
              <div className="text-xs text-white/80 font-medium">With Classified Issues</div>
              <div className="text-lg font-bold text-white">{summary.cases_with_classified_issues ?? 0}</div>
              <div className="text-xs text-white/70">{pct(summary.cases_with_classified_issues ?? 0)}</div>
            </div>

            <div className="rounded-lg bg-white/15 p-3" data-testid="dashboard-pipeline-verified">
              <div className="text-xs text-white/80 font-medium">With Verified Issues</div>
              <div className="text-lg font-bold text-white">{summary.cases_with_verified_issues ?? 0}</div>
              <div className="text-xs text-white/70">{pct(summary.cases_with_verified_issues ?? 0)}</div>
            </div>

            <div className="rounded-lg bg-white/15 p-3" data-testid="dashboard-pipeline-reports">
              <div className="text-xs text-white/80 font-medium">With Pipeline Reports</div>
              <div className="text-lg font-bold text-white">{summary.cases_with_pipeline_reports ?? 0}</div>
              <div className="text-xs text-white/70">{pct(summary.cases_with_pipeline_reports ?? 0)}</div>
            </div>
          </div>

          <div className="mt-4 text-xs text-white/70">
            These figures reflect staged processing coverage across the user's portfolio and do not indicate legal merit or likely appeal outcome.
          </div>
        </>
      ) : null}
    </div>
  );
}
