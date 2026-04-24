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
  return apiRequest(`/pipeline/cases/${caseId}/issues/verify-batch`, {
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

async function refreshAllPipeline(caseId, verifyLimit = 0) {
  return apiRequest(`/pipeline/cases/${caseId}/refresh-all`, {
    method: "POST",
    body: JSON.stringify({ verify_limit: verifyLimit }),
  });
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
  const hasAnyPipelineData = summary && (extractedDocs > 0 || classifiedIssues > 0 || verifiedIssues > 0 || syncedGrounds > 0);

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
    <div className="rounded-lg border border-slate-200 bg-white p-4 mb-4 legal-content" data-testid="pipeline-progress-widget">
      <div className="font-bold text-xl text-blue-600 mb-2" style={{ fontFamily: "'Times New Roman', Times, serif" }}>Pipeline Progress</div>
      <div className="text-xs text-slate-500 mb-3">Staged workflow: extract &rarr; classify &rarr; verify &rarr; draft</div>

      {hasAnyPipelineData && (
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
      )}

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
        <Button variant="outline" size="sm" onClick={() => runAction(() => refreshAllPipeline(caseId, 0))} disabled={loading} className="bg-blue-700 text-white hover:bg-blue-600" data-testid="pipeline-refresh-all-btn">
          {loading ? <><Loader2 className="w-3 h-3 mr-1.5 animate-spin" />Working...</> : "Refresh Pipeline Now"}
        </Button>
        <Button variant="outline" size="sm" onClick={() => runAction(() => refreshAllPipeline(caseId, 3))} disabled={loading} className="bg-blue-700 text-white hover:bg-blue-600" data-testid="pipeline-refresh-verify-3-btn">
          {loading ? <><Loader2 className="w-3 h-3 mr-1.5 animate-spin" />Working...</> : "Refresh + Verify Top 3"}
        </Button>
        <Button variant="outline" size="sm" onClick={() => runAction(() => refreshAllPipeline(caseId, 6))} disabled={loading} className="bg-blue-700 text-white hover:bg-blue-600" data-testid="pipeline-refresh-verify-6-btn">
          {loading ? <><Loader2 className="w-3 h-3 mr-1.5 animate-spin" />Working...</> : "Refresh + Verify Top 6"}
        </Button>
      </div>

      {error && <div className="mt-3 text-sm text-red-700" data-testid="pipeline-error">{error}</div>}

      {result && (
        <div className="mt-3 rounded-lg border border-slate-200 p-3 text-xs text-slate-700 bg-slate-50" data-testid="pipeline-result">
          <div className="font-medium text-slate-900 mb-1">Last Pipeline Result</div>
          {"message" in result && <div>{result.message}</div>}
          {"identified_count" in result && <div>Identified: {result.identified_count}</div>}
          {"document_extracts_used" in result && <div>Document extracts used: {result.document_extracts_used}</div>}
          {"verified" in result && !("verification" in result) && <div>Verified: {result.verified}</div>}
          {"failed" in result && !("verification" in result) && <div>Failed: {result.failed}</div>}
          {"synced_count" in result && <div>Synced grounds: {result.synced_count}</div>}

          {"documents" in result ? (
            <>
              <div className="font-medium mt-2">Documents</div>
              <div>Total: {result.documents.total_documents ?? 0}</div>
              <div>New extracts: {result.documents.created ?? 0}</div>
              <div>Existing extracts skipped: {result.documents.skipped_existing ?? 0}</div>
            </>
          ) : null}

          {"case_extract" in result ? (
            <>
              <div className="font-medium mt-2">Case Extract</div>
              <div>Facts: {result.case_extract.facts ?? 0}</div>
              <div>Events: {result.case_extract.events ?? 0}</div>
              <div>Findings: {result.case_extract.findings ?? 0}</div>
            </>
          ) : null}

          {"classification" in result ? (
            <>
              <div className="font-medium mt-2">Classification</div>
              <div>Classified: {result.classification.classified ?? 0}</div>
            </>
          ) : null}

          {"verification" in result ? (
            <>
              <div className="font-medium mt-2">Verification</div>
              <div>Requested limit: {result.verification.requested_limit ?? 0}</div>
              <div>Applied limit: {result.verification.applied_limit ?? 0}</div>
              <div>Attempted: {result.verification.attempted ?? 0}</div>
              <div>Verified: {result.verification.verified ?? 0}</div>
              <div>Failed: {result.verification.failed ?? 0}</div>
            </>
          ) : null}

          {"projection" in result ? (
            <>
              <div className="font-medium mt-2">Projection</div>
              <div>Synced grounds: {result.projection.synced_count ?? 0}</div>
            </>
          ) : null}
        </div>
      )}
    </div>
  );
}
