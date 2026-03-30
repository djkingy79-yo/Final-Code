import React from "react";

async function apiRequest(url, options = {}) {
  const token = localStorage.getItem("session_token");
  const response = await fetch(url, {
    credentials: "include",
    headers: {
      "Content-Type": "application/json",
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
      ...(options.headers || {}),
    },
    ...options,
  });

  const data = await response.json().catch(() => ({}));

  if (!response.ok) {
    throw new Error(data?.detail || data?.message || "Request failed");
  }

  return data;
}

async function getDashboardPipelineSummary() {
  return apiRequest("/api/pipeline/dashboard-summary", {
    method: "GET",
  });
}

export default function DashboardPipelineSummary() {
  const [summary, setSummary] = React.useState(null);
  const [loading, setLoading] = React.useState(false);
  const [error, setError] = React.useState("");

  const loadSummary = React.useCallback(async () => {
    try {
      setLoading(true);
      setError("");
      const data = await getDashboardPipelineSummary();
      setSummary(data);
    } catch (err) {
      setError(err.message || "Failed to load pipeline dashboard summary");
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

  // If there's an error or no data, hide the panel entirely
  if (error && !summary) return null;
  if (!summary && !loading) return null;

  return (
    <div className="rounded border p-4 mb-4" data-testid="dashboard-pipeline-summary">
      <div className="flex items-center justify-between gap-3 mb-2">
        <div className="font-semibold text-sm">Pipeline Portfolio Summary</div>
        <button
          type="button"
          onClick={loadSummary}
          disabled={loading}
          className="px-2 py-1 rounded border text-xs font-medium"
          data-testid="dashboard-pipeline-refresh-btn"
        >
          {loading ? "Refreshing..." : "Refresh"}
        </button>
      </div>

      <div className="text-xs opacity-80 mb-3">
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
          <div className="grid grid-cols-2 md:grid-cols-5 gap-3 text-sm">
            <div className="rounded border p-3" data-testid="dashboard-pipeline-total">
              <div className="text-xs opacity-70">Total Cases</div>
              <div className="text-lg font-semibold">{summary.total_cases ?? 0}</div>
            </div>

            <div className="rounded border p-3" data-testid="dashboard-pipeline-extracted">
              <div className="text-xs opacity-70">With Case Extract</div>
              <div className="text-lg font-semibold">{summary.cases_with_case_extract ?? 0}</div>
              <div className="text-xs opacity-70">{pct(summary.cases_with_case_extract ?? 0)}</div>
            </div>

            <div className="rounded border p-3" data-testid="dashboard-pipeline-classified">
              <div className="text-xs opacity-70">With Classified Issues</div>
              <div className="text-lg font-semibold">{summary.cases_with_classified_issues ?? 0}</div>
              <div className="text-xs opacity-70">{pct(summary.cases_with_classified_issues ?? 0)}</div>
            </div>

            <div className="rounded border p-3" data-testid="dashboard-pipeline-verified">
              <div className="text-xs opacity-70">With Verified Issues</div>
              <div className="text-lg font-semibold">{summary.cases_with_verified_issues ?? 0}</div>
              <div className="text-xs opacity-70">{pct(summary.cases_with_verified_issues ?? 0)}</div>
            </div>

            <div className="rounded border p-3" data-testid="dashboard-pipeline-reports">
              <div className="text-xs opacity-70">With Pipeline Reports</div>
              <div className="text-lg font-semibold">{summary.cases_with_pipeline_reports ?? 0}</div>
              <div className="text-xs opacity-70">{pct(summary.cases_with_pipeline_reports ?? 0)}</div>
            </div>
          </div>

          <div className="mt-4 text-xs opacity-80">
            These figures reflect staged processing coverage across the user's portfolio and do not indicate legal merit or likely appeal outcome.
          </div>
        </>
      ) : null}
    </div>
  );
}
