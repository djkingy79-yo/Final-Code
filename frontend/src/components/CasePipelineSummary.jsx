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

async function getPipelineSummary(caseId) {
  return apiRequest(`/api/pipeline/cases/${caseId}/summary`, {
    method: "GET",
  });
}

export default function CasePipelineSummary({ caseId }) {
  const [summary, setSummary] = React.useState(null);
  const [loading, setLoading] = React.useState(false);
  const [error, setError] = React.useState("");

  const loadSummary = React.useCallback(async () => {
    try {
      setLoading(true);
      setError("");
      const data = await getPipelineSummary(caseId);
      setSummary(data);
    } catch (err) {
      setError(err.message || "Failed to load pipeline summary");
    } finally {
      setLoading(false);
    }
  }, [caseId]);

  React.useEffect(() => {
    if (caseId) {
      loadSummary();
    }
  }, [caseId, loadSummary]);

  if (!caseId) return null;
  if (error && !summary) return null;
  if (!summary && !loading) return null;

  return (
    <div className="rounded border p-4 mb-4" data-testid="case-pipeline-summary">
      <div className="flex items-center justify-between gap-3 mb-2">
        <div className="font-semibold text-sm">Case Pipeline Summary</div>
        <button
          type="button"
          onClick={loadSummary}
          disabled={loading}
          className="px-2 py-1 rounded border text-xs font-medium"
          data-testid="pipeline-summary-refresh-btn"
        >
          {loading ? "Refreshing..." : "Refresh"}
        </button>
      </div>

      <div className="text-xs opacity-80 mb-3">
        Overview of staged processing for this case: extract &rarr; classify &rarr; verify &rarr; draft.
      </div>

      {error ? (
        <div className="text-sm text-red-700" data-testid="pipeline-summary-error">{error}</div>
      ) : null}

      {!error && !summary && loading ? (
        <div className="text-sm opacity-75">Loading pipeline summary...</div>
      ) : null}

      {summary ? (
        <>
          <div className="grid grid-cols-2 md:grid-cols-3 gap-3 text-sm">
            <div className="rounded border p-3" data-testid="pipeline-summary-extracted">
              <div className="text-xs opacity-70">Extracted Documents</div>
              <div className="text-lg font-semibold">{summary.document_extract_count ?? 0}</div>
            </div>

            <div className="rounded border p-3" data-testid="pipeline-summary-classified">
              <div className="text-xs opacity-70">Classified Issues</div>
              <div className="text-lg font-semibold">{summary.issue_classification_count ?? 0}</div>
            </div>

            <div className="rounded border p-3" data-testid="pipeline-summary-verified">
              <div className="text-xs opacity-70">Verified Issues</div>
              <div className="text-lg font-semibold">{summary.issue_verification_count ?? 0}</div>
            </div>

            <div className="rounded border p-3" data-testid="pipeline-summary-grounds">
              <div className="text-xs opacity-70">Derived Grounds</div>
              <div className="text-lg font-semibold">{summary.synced_grounds_count ?? 0}</div>
            </div>

            <div className="rounded border p-3" data-testid="pipeline-summary-drafted">
              <div className="text-xs opacity-70">Pipeline-Drafted Reports</div>
              <div className="text-lg font-semibold">{summary.pipeline_drafted_reports_count ?? 0}</div>
            </div>

            <div className="rounded border p-3" data-testid="pipeline-summary-total-reports">
              <div className="text-xs opacity-70">Total Reports</div>
              <div className="text-lg font-semibold">{summary.total_reports_count ?? 0}</div>
            </div>
          </div>

          <div className="mt-4 rounded border p-3 text-xs" data-testid="pipeline-summary-extract-status">
            <div className="font-medium mb-1">Case Extract Status</div>
            <div>Present: {summary.case_extract_present ? "Yes" : "No"}</div>
            <div>
              Verification status: {summary.case_extract_verification_status || "unverified"}
            </div>
            {summary.case_extract_created_at ? (
              <div>Created: {new Date(summary.case_extract_created_at).toLocaleString()}</div>
            ) : null}
          </div>

          <div className="mt-3 text-xs opacity-80">
            A stronger pipeline state generally means the case materials are more fully prepared for legal review.
          </div>
        </>
      ) : null}
    </div>
  );
}
