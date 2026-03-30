import { useState, useEffect, useCallback } from "react";
import axios from "axios";
import { toast } from "sonner";
import { API } from "../App";
import { CheckCircle2, Circle, Loader2, ArrowRight, FileSearch, Brain, Shield, GitMerge } from "lucide-react";
import { Button } from "./ui/button";

const STAGES = [
  { key: "extract", label: "Extract", icon: FileSearch, description: "Structured extraction from documents" },
  { key: "classify", label: "Classify", icon: Brain, description: "Identify candidate appeal issues" },
  { key: "verify", label: "Verify", icon: Shield, description: "Assess supporting and undermining material" },
  { key: "project", label: "Project", icon: GitMerge, description: "Sync verified issues to grounds" },
];

const StageIcon = ({ stage, status }) => {
  if (status === "complete") return <CheckCircle2 className="w-5 h-5 text-green-600" />;
  if (status === "partial") return <div className="w-5 h-5 rounded-full border-2 border-blue-500 bg-blue-100 flex items-center justify-center"><div className="w-2 h-2 rounded-full bg-blue-500" /></div>;
  if (status === "running") return <Loader2 className="w-5 h-5 text-blue-500 animate-spin" />;
  return <Circle className="w-5 h-5 text-slate-300" />;
};

const PipelineProgress = ({ caseId, sessionToken, onRunStage }) => {
  const [status, setStatus] = useState(null);
  const [loading, setLoading] = useState(true);
  const [runningStage, setRunningStage] = useState(null);

  const fetchStatus = useCallback(async () => {
    if (!caseId || !sessionToken) return;
    try {
      const { data } = await axios.get(`${API}/api/cases/${caseId}/pipeline/status`, {
        headers: { Authorization: `Bearer ${sessionToken}` },
      });
      setStatus(data.stages);
    } catch {
      // silently fail — pipeline may not have data yet
    } finally {
      setLoading(false);
    }
  }, [caseId, sessionToken]);

  useEffect(() => { fetchStatus(); }, [fetchStatus]);

  const getStageStatus = (key) => {
    if (!status) return "pending";
    if (key === "extract") {
      if (status.extract.case_extract_ready) return "complete";
      if (status.extract.documents_extracted > 0) return "partial";
      return "pending";
    }
    if (key === "classify") {
      if (status.classify.issues_identified > 0) return "complete";
      return "pending";
    }
    if (key === "verify") {
      if (status.verify.issues_pending === 0 && status.verify.issues_verified > 0) return "complete";
      if (status.verify.issues_verified > 0) return "partial";
      return "pending";
    }
    if (key === "project") {
      if (status.project.grounds_synced > 0) return "complete";
      return "pending";
    }
    return "pending";
  };

  const getStageDetail = (key) => {
    if (!status) return "";
    if (key === "extract") {
      return `${status.extract.documents_extracted}/${status.extract.documents_total} documents extracted`;
    }
    if (key === "classify") {
      return status.classify.issues_identified > 0
        ? `${status.classify.issues_identified} issues identified`
        : "Not yet classified";
    }
    if (key === "verify") {
      if (status.verify.issues_verified === 0) return "Not yet verified";
      return `${status.verify.issues_verified} verified, ${status.verify.issues_pending} pending`;
    }
    if (key === "project") {
      return status.project.grounds_synced > 0
        ? `${status.project.grounds_synced} grounds synced`
        : "Not yet projected";
    }
    return "";
  };

  const canRun = (key) => {
    if (!status || runningStage) return false;
    if (key === "extract") return status.extract.documents_total > 0;
    if (key === "classify") return status.extract.case_extract_ready;
    if (key === "verify") return status.classify.issues_identified > 0;
    if (key === "project") return status.classify.issues_identified > 0;
    return false;
  };

  const handleRunStage = async (key) => {
    if (!canRun(key)) return;
    setRunningStage(key);
    try {
      if (key === "extract") {
        // Extract all unextracted documents, then refresh
        const { data: docs } = await axios.get(`${API}/api/cases/${caseId}/documents`, {
          headers: { Authorization: `Bearer ${sessionToken}` },
        });
        const textDocs = docs.filter(d => (d.content_text || "").length > 50);
        let extracted = 0;
        for (const doc of textDocs) {
          try {
            await axios.post(`${API}/api/cases/${caseId}/documents/${doc.document_id}/extract`, {}, {
              headers: { Authorization: `Bearer ${sessionToken}` },
            });
            extracted++;
          } catch { /* skip failed docs */ }
        }
        if (extracted > 0) {
          await axios.post(`${API}/api/cases/${caseId}/extract/refresh`, {}, {
            headers: { Authorization: `Bearer ${sessionToken}` },
          });
        }
        toast.success(`Extracted ${extracted} documents and merged case extract`);
      } else if (key === "classify") {
        await axios.post(`${API}/api/cases/${caseId}/issues/classify`, {}, {
          headers: { Authorization: `Bearer ${sessionToken}` },
        });
        toast.success("Issues classified successfully");
      } else if (key === "verify") {
        await axios.post(`${API}/api/cases/${caseId}/issues/verify-all`, {}, {
          headers: { Authorization: `Bearer ${sessionToken}` },
        });
        toast.success("All issues verified");
      } else if (key === "project") {
        await axios.post(`${API}/api/cases/${caseId}/grounds/sync-from-issues`, {}, {
          headers: { Authorization: `Bearer ${sessionToken}` },
        });
        toast.success("Grounds synced from verified issues");
        if (onRunStage) onRunStage("project");
      }
      await fetchStatus();
    } catch (err) {
      toast.error(`Pipeline stage failed: ${err?.response?.data?.detail || err.message}`);
    } finally {
      setRunningStage(null);
    }
  };

  if (loading) {
    return (
      <div className="rounded-lg border border-slate-200 p-4 bg-white" data-testid="pipeline-progress-loading">
        <div className="flex items-center gap-2 text-sm text-slate-500">
          <Loader2 className="w-4 h-4 animate-spin" /> Loading pipeline status...
        </div>
      </div>
    );
  }

  return (
    <div className="rounded-lg border border-slate-200 bg-white overflow-hidden" data-testid="pipeline-progress-widget">
      <div className="px-4 py-3 bg-slate-50 border-b border-slate-200">
        <h3 className="text-sm font-semibold text-slate-800">Analysis Pipeline</h3>
        <p className="text-xs text-slate-500 mt-0.5">Document upload to counsel-ready output</p>
      </div>

      <div className="p-4">
        <div className="space-y-3">
          {STAGES.map((stage, idx) => {
            const stageStatus = runningStage === stage.key ? "running" : getStageStatus(stage.key);
            const detail = getStageDetail(stage.key);
            const isRunnable = canRun(stage.key);

            return (
              <div key={stage.key}>
                <div className="flex items-center gap-3" data-testid={`pipeline-stage-${stage.key}`}>
                  <StageIcon stage={stage.key} status={stageStatus} />
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2">
                      <span className="text-sm font-medium text-slate-800">{stage.label}</span>
                      {stageStatus === "complete" && <span className="text-xs text-green-600 font-medium">Done</span>}
                      {stageStatus === "partial" && <span className="text-xs text-blue-600 font-medium">Partial</span>}
                    </div>
                    <p className="text-xs text-slate-400">{detail || stage.description}</p>
                  </div>
                  <Button
                    size="sm"
                    variant={stageStatus === "complete" ? "outline" : "default"}
                    className={stageStatus === "complete" ? "text-slate-500 border-slate-200" : "bg-blue-600 hover:bg-blue-700 text-white"}
                    disabled={!isRunnable || runningStage !== null}
                    onClick={() => handleRunStage(stage.key)}
                    data-testid={`pipeline-run-${stage.key}`}
                  >
                    {runningStage === stage.key ? (
                      <Loader2 className="w-3.5 h-3.5 animate-spin" />
                    ) : stageStatus === "complete" ? (
                      "Re-run"
                    ) : (
                      "Run"
                    )}
                  </Button>
                </div>
                {idx < STAGES.length - 1 && (
                  <div className="ml-2.5 mt-1 mb-1 h-3 border-l-2 border-dashed border-slate-200" />
                )}
              </div>
            );
          })}
        </div>

        {/* Run All button */}
        <div className="mt-4 pt-3 border-t border-slate-100">
          <Button
            className="w-full bg-blue-600 hover:bg-blue-700 text-white"
            disabled={runningStage !== null || !status || status.extract.documents_total === 0}
            onClick={async () => {
              for (const stage of STAGES) {
                if (canRun(stage.key)) {
                  await handleRunStage(stage.key);
                }
              }
            }}
            data-testid="pipeline-run-all"
          >
            {runningStage ? (
              <><Loader2 className="w-4 h-4 mr-2 animate-spin" /> Running {STAGES.find(s => s.key === runningStage)?.label}...</>
            ) : (
              <><ArrowRight className="w-4 h-4 mr-2" /> Run Full Pipeline</>
            )}
          </Button>
        </div>
      </div>
    </div>
  );
};

export default PipelineProgress;
