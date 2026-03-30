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

async function getPipelineStaleness(caseId) {
  return apiRequest(`/api/pipeline/cases/${caseId}/staleness`, {
    method: "GET",
  });
}

export default function PipelineStalenessAlert({ caseId }) {
  const [staleness, setStaleness] = React.useState(null);
  const [loading, setLoading] = React.useState(false);
  const [error, setError] = React.useState("");

  const load = React.useCallback(async () => {
    try {
      setLoading(true);
      setError("");
      const data = await getPipelineStaleness(caseId);
      setStaleness(data);
    } catch (err) {
      setError(err.message || "Failed to load pipeline staleness");
    } finally {
      setLoading(false);
    }
  }, [caseId]);

  React.useEffect(() => {
    if (caseId) load();
  }, [caseId, load]);

  if (!caseId) return null;
  if (error) return <div className="rounded border p-3 mb-4 text-sm text-red-700" data-testid="staleness-error">{error}</div>;
  if (!staleness && loading) return <div className="rounded border p-3 mb-4 text-sm opacity-75">Checking pipeline freshness...</div>;
  if (!staleness) return null;

  if (!staleness.overall_stale) {
    return (
      <div className="rounded border p-3 mb-4 text-sm" data-testid="staleness-fresh">
        <div className="font-medium text-green-700">Pipeline up to date</div>
        <div className="text-xs opacity-80 mt-1">
          Extracts, classifications, verifications, and pipeline reports appear current.
        </div>
      </div>
    );
  }

  return (
    <div className="rounded border p-4 mb-4" data-testid="staleness-stale">
      <div className="flex items-center justify-between gap-3">
        <div className="font-medium text-yellow-700">Pipeline refresh recommended</div>
        <button
          type="button"
          onClick={load}
          disabled={loading}
          className="px-2 py-1 rounded border text-xs font-medium"
          data-testid="staleness-refresh-btn"
        >
          {loading ? "Refreshing..." : "Refresh"}
        </button>
      </div>

      <div className="mt-2 text-xs opacity-80">
        One or more staged artifacts appear older than the latest case materials.
      </div>

      <div className="mt-3 space-y-2 text-xs">
        {staleness.extract_missing_for_documents?.length > 0 ? (
          <div>Documents without extracts: {staleness.extract_missing_for_documents.length}</div>
        ) : null}

        {staleness.documents_newer_than_extracts ? (
          <div>Newer documents exist than the current document extracts.</div>
        ) : null}

        {staleness.case_extract_stale ? (
          <div>Case extract is older than the latest document extract.</div>
        ) : null}

        {staleness.classifications_stale ? (
          <div>Issue classifications should be refreshed from the current case extract.</div>
        ) : null}

        {staleness.verifications_stale ? (
          <div>Issue verifications are older than the latest issue classifications.</div>
        ) : null}

        {staleness.reports_stale ? (
          <div>Pipeline-drafted reports are older than the latest verification layer.</div>
        ) : null}
      </div>
    </div>
  );
}
