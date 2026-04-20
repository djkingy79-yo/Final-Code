import { useEffect, useState } from "react";
import axios from "axios";
import { DollarSign } from "lucide-react";
import { API } from "../App";

/**
 * AiCostBadge — small inline card showing the estimated AI spend for a case.
 *
 * Intentionally silent when there's no data yet (new case, or ai_usage
 * collection empty). The value is derived from locally-counted tokens and
 * OpenAI's published rate card; actual billing is on the OpenAI dashboard.
 */
const AiCostBadge = ({ caseId, className = "" }) => {
  const [data, setData] = useState(null);

  useEffect(() => {
    let alive = true;
    axios
      .get(`${API}/cases/${caseId}/ai-cost`)
      .then((res) => alive && setData(res.data))
      .catch(() => {
        // Silent failure — badge is a nicety, not a requirement.
      });
    return () => { alive = false; };
  }, [caseId]);

  if (!data || !data.totals || data.totals.calls === 0) return null;

  const total = data.totals.cost_usd || 0;
  const byReport = data.by_report_type || [];

  return (
    <div
      className={`flex flex-wrap items-center gap-3 px-4 py-3 bg-emerald-50 border border-emerald-200 rounded-xl text-sm ${className}`}
      data-testid="ai-cost-badge"
    >
      <div className="flex items-center gap-2 font-semibold text-emerald-800">
        <DollarSign className="w-4 h-4" />
        Estimated AI cost:
        <span className="tabular-nums" data-testid="ai-cost-total">
          ${total.toFixed(2)}
        </span>
        <span className="text-xs font-normal text-emerald-700/80">
          across {data.totals.calls} AI call{data.totals.calls === 1 ? "" : "s"}
        </span>
      </div>
      {byReport.length > 0 && (
        <div className="flex flex-wrap items-center gap-2 text-xs text-emerald-800/90">
          <span className="opacity-70">·</span>
          {byReport.slice(0, 4).map((r) => (
            <span
              key={r.report_type}
              className="px-2 py-0.5 bg-white/70 rounded-full border border-emerald-200 tabular-nums"
              data-testid={`ai-cost-${r.report_type}`}
            >
              {r.report_type.replace(/_/g, " ")}: ${r.cost_usd.toFixed(2)}
            </span>
          ))}
        </div>
      )}
    </div>
  );
};

export default AiCostBadge;
