import React from "react";
import axios from "axios";
import { API } from "../App";
import { Loader2 } from "lucide-react";
import { Button } from "../components/ui/button";

async function apiRequest(url, options = {}) {
  const response = await axios({
    url: `${API}${url}`,
    method: options.method || "GET",
    data: options.body ? JSON.parse(options.body) : undefined,
    timeout: 300000,
  });
  return response.data;
}

async function getPipelineSummary(caseId) {
  return apiRequest(`/pipeline/cases/${caseId}/summary`);
}

async function refreshCaseExtract(caseId) {
  return apiRequest(`/pipeline/cases/${caseId}/extract/refresh`, { method: "POST" });
}

async function classifyIssues(caseId) {
  return apiRequest(`/pipeline/cases/${caseId}/issues/classify`, { method: "POST" });
}

async function verifyBatch(caseId, limit) {
  return apiRequest(`/cases/${caseId}/issues/verify-batch`, {
    method: "POST",
    body: JSON.stringify({ limit }),
  });
}

async function extractDocument(caseId, documentId) {
  return apiRequest(`/pipeline/cases/${caseId}/documents/${documentId}/extract`, { method: "POST" });
}

async function syncGrounds(caseId) {
  return apiRequest(`/pipeline/cases/${caseId}/grounds/sync-from-issues`, { method: "POST" });
}

export default function PipelineProgress({
  caseId,
  documents = [],
  onRefreshCase,
  onRefreshGrounds,
  onRefreshReports,
}) {
  const [loading, setLoading] = React.useState(false);
  const [error, setError] = React.useState("");
  const [result, setResult] = React.useState(null);
  const [summary, setSummary] = React.useState(null);

  React.useEffect(() => {
    let cancelled = false;
    const load = async () => {
      try {
        const data = await getPipelineSummary(caseId);
        if (!cancelled) setSummary(data);
      } catch (_) { /* silent */ }
    };
    if (caseId) load();
    return () => { cancelled = true; };
  }, [caseId]);

  const extractedDocs = summary?.document_extract_count ?? 0;
  const classifiedIssues = summary?.issue_classification_count ?? 0;
  const verifiedIssues = summary?.issue_verification_count ?? 0;
  const syncedGrounds = summary?.synced_grounds_count ?? 0;

  const runAction = async (fn) => {
    try {
      setLoading(true);
      setError("");
      setResult(null);
      const data = await fn();
      setResult(data);
      try {
        const freshSummary = await getPipelineSummary(caseId);
        setSummary(freshSummary);
      } catch (_) { /* ignore */ }
      if (typeof onRefreshCase === "function") await onRefreshCase();
      if (typeof onRefreshGrounds === "function") await onRefreshGrounds();
      if (typeof onRefreshReports === "function") await onRefreshReports();
    } catch (err) {
      setError(err?.response?.data?.detail || err.message || "Pipeline action failed");
    } finally {
      setLoading(false);
    }
  };

  const handleExtractAllDocuments = () => runAction(async () => {
    let completed = 0, failed = 0;
    for (const doc of documents) {
      try { await extractDocument(caseId, doc.document_id); completed++; }
      catch (_) { failed++; }
    }
    return { message: `Extraction attempted for ${documents.length} document(s). Completed ${completed}, failed ${failed}.`, attempted: documents.length, completed, failed };
  });

  return (
    <div className="rounded-lg border border-slate-200 bg-white p-4 mb-4" data-testid="pipeline-progress-widget">
      <div className="font-semibold text-sm text-slate-900 mb-2">Pipeline Progress</div>
      <div className="text-xs text-slate-500 mb-3">Staged workflow: extract &rarr; classify &rarr; verify &rarr; draft</div>

      <div className="grid grid-cols-2 md:grid-cols-4 gap-3 mb-4 text-sm">
        <div className="rounded-lg border border-slate-200 p-3 bg-slate-50" data-testid="pipeline-stat-extracted">
          <div className="text-xs text-slate-500">Extracted Docs</div>
          <div className="text-lg font-semibold text-slate-900">{extractedDocs}</div>
        </div>
        <div className="rounded-lg border border-slate-200 p-3 bg-slate-50" data-testid="pipeline-stat-classified">
          <div className="text-xs text-slate-500">Classified Issues</div>
          <div className="text-lg font-semibold text-slate-900">{classifiedIssues}</div>
        </div>
        <div className="rounded-lg border border-slate-200 p-3 bg-slate-50" data-testid="pipeline-stat-verified">
          <div className="text-xs text-slate-500">Verified Issues</div>
          <div className="text-lg font-semibold text-slate-900">{verifiedIssues}</div>
        </div>
        <div className="rounded-lg border border-slate-200 p-3 bg-slate-50" data-testid="pipeline-stat-synced">
          <div className="text-xs text-slate-500">Synced Grounds</div>
          <div className="text-lg font-semibold text-slate-900">{syncedGrounds}</div>
        </div>
      </div>

      <div className="flex flex-wrap gap-2">
        <Button variant="outline" size="sm" onClick={handleExtractAllDocuments} disabled={loading || documents.length === 0} className="bg-blue-700 text-white hover:bg-blue-600" data-testid="pipeline-extract-all-btn">
          {loading ? <><Loader2 className="w-3 h-3 mr-1.5 animate-spin" />Working...</> : "Extract All Documents"}
        </Button>
        <Button variant="outline" size="sm" onClick={() => runAction(() => refreshCaseExtract(caseId))} disabled={loading} className="bg-blue-700 text-white hover:bg-blue-600" data-testid="pipeline-refresh-extract-btn">
          {loading ? <><Loader2 className="w-3 h-3 mr-1.5 animate-spin" />Working...</> : "Refresh Case Extract"}
        </Button>
        <Button variant="outline" size="sm" onClick={() => runAction(() => classifyIssues(caseId))} disabled={loading} className="bg-blue-700 text-white hover:bg-blue-600" data-testid="pipeline-classify-btn">
          {loading ? <><Loader2 className="w-3 h-3 mr-1.5 animate-spin" />Working...</> : "Classify Issues"}
        </Button>
        <Button variant="outline" size="sm" onClick={() => runAction(() => verifyBatch(caseId, 3))} disabled={loading} className="bg-blue-700 text-white hover:bg-blue-600" data-testid="pipeline-verify-3-btn">
          {loading ? <><Loader2 className="w-3 h-3 mr-1.5 animate-spin" />Working...</> : "Verify Top 3"}
        </Button>
        <Button variant="outline" size="sm" onClick={() => runAction(() => verifyBatch(caseId, 6))} disabled={loading} className="bg-blue-700 text-white hover:bg-blue-600" data-testid="pipeline-verify-6-btn">
          {loading ? <><Loader2 className="w-3 h-3 mr-1.5 animate-spin" />Working...</> : "Verify Top 6"}
        </Button>
        <Button variant="outline" size="sm" onClick={() => runAction(() => syncGrounds(caseId))} disabled={loading} className="bg-blue-700 text-white hover:bg-blue-600" data-testid="pipeline-sync-grounds-btn">
          {loading ? <><Loader2 className="w-3 h-3 mr-1.5 animate-spin" />Working...</> : "Sync Grounds"}
        </Button>
      </div>

      {error && <div className="mt-3 text-sm text-red-700" data-testid="pipeline-error">{error}</div>}

      {result && (
        <div className="mt-3 rounded-lg border border-slate-200 p-3 text-xs text-slate-700 bg-slate-50" data-testid="pipeline-result">
          <div className="font-medium text-slate-900 mb-1">Last Pipeline Result</div>
          {"message" in result && <div>{result.message}</div>}
          {"identified_count" in result && <div>Identified: {result.identified_count}</div>}
          {"document_extracts_used" in result && <div>Document extracts used: {result.document_extracts_used}</div>}
          {"verified" in result && <div>Verified: {result.verified}</div>}
          {"failed" in result && <div>Failed: {result.failed}</div>}
          {"synced_count" in result && <div>Synced grounds: {result.synced_count}</div>}
        </div>
      )}
    </div>
  );
}
