import { useState, useEffect } from "react";
import axios from "axios";
import { API } from "../App";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "./ui/card";
import { Button } from "./ui/button";
import { Badge } from "./ui/badge";
import { DollarSign, TrendingUp, Loader2, AlertCircle } from "lucide-react";

/**
 * OpenAICostsPanel
 * Fetches /api/admin/openai-costs and renders:
 *   - Headline spend + projection
 *   - Token/calls totals (success vs failed)
 *   - Breakdown by model, task, report_type
 *   - Top users by spend
 *   - Daily series sparkline
 *
 * Costs are estimated locally via tiktoken + OpenAI's Feb 2026 rate card.
 * Actual billing appears on the user's OpenAI dashboard.
 */
const OpenAICostsPanel = () => {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [period, setPeriod] = useState("month");

  useEffect(() => {
    let alive = true;
    const load = async () => {
      setLoading(true);
      setError("");
      try {
        const res = await axios.get(`${API}/admin/openai-costs`, { params: { period } });
        if (alive) setData(res.data);
      } catch (err) {
        if (!alive) return;
        if (err.response?.status === 403) setError("Admin access required.");
        else if (err.response?.status === 401) setError("Please sign in.");
        else setError(err.response?.data?.detail || err.message || "Failed to load cost data.");
      } finally {
        if (alive) setLoading(false);
      }
    };
    load();
    return () => { alive = false; };
  }, [period]);

  const fmtUSD = (n) => n == null ? "—" : `$${Number(n).toFixed(2)}`;
  const fmtInt = (n) => n == null ? "—" : Number(n).toLocaleString();

  if (loading && !data) {
    return (
      <Card data-testid="openai-costs-loading">
        <CardContent className="py-10 flex items-center justify-center">
          <Loader2 className="w-6 h-6 animate-spin text-blue-600" />
          <span className="ml-3 text-sm text-slate-600">Loading OpenAI cost data…</span>
        </CardContent>
      </Card>
    );
  }

  if (error) {
    return (
      <Card className="border-red-200" data-testid="openai-costs-error">
        <CardHeader>
          <CardTitle className="text-red-700 flex items-center gap-2 text-base">
            <AlertCircle className="w-4 h-4" /> OpenAI Cost Tracker
          </CardTitle>
          <CardDescription>{error}</CardDescription>
        </CardHeader>
      </Card>
    );
  }

  const totals = data?.totals || {};
  const daily = data?.daily || [];
  const maxDaily = daily.length ? Math.max(...daily.map((d) => d.cost_usd || 0)) : 0;

  return (
    <div className="space-y-4" data-testid="openai-costs-panel">
      {/* Header + period selector */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <DollarSign className="w-5 h-5 text-emerald-600" />
          <h2 className="text-lg font-bold text-slate-900">OpenAI Cost Tracker</h2>
          <Badge variant="outline" className="text-xs">estimated</Badge>
        </div>
        <div className="flex items-center gap-2" role="group" aria-label="Period selector">
          {["week", "month", "all"].map((p) => (
            <Button
              key={p}
              size="sm"
              variant={period === p ? "default" : "outline"}
              onClick={() => setPeriod(p)}
              className={period === p ? "bg-blue-700 hover:bg-blue-800 text-white" : ""}
              data-testid={`openai-costs-period-${p}`}
            >
              {p === "week" ? "7 days" : p === "month" ? "This month" : "All time"}
            </Button>
          ))}
        </div>
      </div>

      {/* Headline stat cards */}
      <div className="grid grid-cols-1 sm:grid-cols-4 gap-3">
        <Card data-testid="openai-costs-spend">
          <CardHeader className="pb-2">
            <CardDescription className="text-xs">USD spent</CardDescription>
            <CardTitle className="text-3xl font-bold text-emerald-700">{fmtUSD(totals.cost_usd)}</CardTitle>
            <p className="text-xs text-slate-500 mt-1">{fmtInt(totals.calls)} LLM calls</p>
          </CardHeader>
        </Card>
        <Card data-testid="openai-costs-projection">
          <CardHeader className="pb-2">
            <CardDescription className="flex items-center gap-1 text-xs">
              <TrendingUp className="w-3.5 h-3.5" /> Projected month-end
            </CardDescription>
            <CardTitle className="text-3xl font-bold text-blue-700">
              {totals.projected_month_end_usd != null ? fmtUSD(totals.projected_month_end_usd) : "—"}
            </CardTitle>
            <p className="text-xs text-slate-500 mt-1">
              {totals.projected_month_end_usd == null ? "available once the current month accumulates data" : "linear run-rate from today"}
            </p>
          </CardHeader>
        </Card>
        <Card data-testid="openai-costs-tokens">
          <CardHeader className="pb-2">
            <CardDescription className="text-xs">Tokens processed</CardDescription>
            <CardTitle className="text-3xl font-bold">{fmtInt(totals.total_tokens)}</CardTitle>
            <p className="text-xs text-slate-500 mt-1">
              in {fmtInt(totals.input_tokens)} · out {fmtInt(totals.output_tokens)}
            </p>
          </CardHeader>
        </Card>
        <Card data-testid="openai-costs-success">
          <CardHeader className="pb-2">
            <CardDescription className="text-xs">Success rate</CardDescription>
            <CardTitle className="text-3xl font-bold">
              {totals.calls > 0 ? `${Math.round((totals.successful_calls / totals.calls) * 100)}%` : "—"}
            </CardTitle>
            <p className="text-xs text-slate-500 mt-1">
              {fmtInt(totals.successful_calls)} ok · {fmtInt(totals.failed_calls)} failed
            </p>
          </CardHeader>
        </Card>
      </div>

      {/* Daily sparkline */}
      {daily.length > 0 && (
        <Card data-testid="openai-costs-daily">
          <CardHeader>
            <CardTitle className="text-sm">Daily spend</CardTitle>
            <CardDescription className="text-xs">USD per day across the selected period</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="flex items-end gap-1 h-20">
              {daily.map((d) => {
                const h = maxDaily > 0 ? Math.max(2, (d.cost_usd / maxDaily) * 76) : 2;
                return (
                  <div
                    key={d.date}
                    className="flex-1 bg-gradient-to-t from-blue-700 to-blue-400 rounded-t transition-all hover:from-blue-800 hover:to-blue-500"
                    style={{ height: `${h}px` }}
                    title={`${d.date} · ${fmtUSD(d.cost_usd)} · ${d.calls} calls`}
                    data-testid={`openai-costs-bar-${d.date}`}
                  />
                );
              })}
            </div>
            <div className="flex justify-between mt-2 text-xs text-slate-500 tabular-nums">
              <span>{daily[0]?.date}</span>
              <span>{daily[daily.length - 1]?.date}</span>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Three-column breakdowns */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-3">
        <BreakdownCard
          title="By model"
          rows={data?.by_model || []}
          labelKey="model"
          testid="openai-costs-by-model"
        />
        <BreakdownCard
          title="By report type"
          rows={data?.by_report_type || []}
          labelKey="report_type"
          testid="openai-costs-by-report"
          formatLabel={(v) => (v ? v.replace(/_/g, " ") : "—")}
        />
        <BreakdownCard
          title="By task type"
          rows={data?.by_task_type || []}
          labelKey="task_type"
          testid="openai-costs-by-task"
          formatLabel={(v) => (v ? v.replace(/_/g, " ") : "—")}
        />
      </div>

      {/* Top users */}
      {data?.by_user?.length > 0 && (
        <Card data-testid="openai-costs-by-user">
          <CardHeader>
            <CardTitle className="text-sm">Top users by spend</CardTitle>
            <CardDescription className="text-xs">Joined via case_id → user_id. Unauthenticated or anonymous calls are excluded.</CardDescription>
          </CardHeader>
          <CardContent className="p-0">
            <table className="w-full text-sm">
              <thead className="bg-slate-50 text-xs uppercase text-slate-500">
                <tr>
                  <th className="text-left py-2 px-4">User</th>
                  <th className="text-right py-2 px-4">Cases</th>
                  <th className="text-right py-2 px-4">Calls</th>
                  <th className="text-right py-2 px-4">USD</th>
                </tr>
              </thead>
              <tbody>
                {data.by_user.map((u, i) => (
                  <tr key={u.user_id} className="border-t border-slate-100" data-testid={`openai-costs-user-row-${i}`}>
                    <td className="py-2 px-4">
                      <div className="font-medium text-slate-800">{u.name || "—"}</div>
                      <div className="text-xs text-slate-500">{u.email || u.user_id}</div>
                    </td>
                    <td className="py-2 px-4 text-right tabular-nums">{u.cases}</td>
                    <td className="py-2 px-4 text-right tabular-nums">{u.calls}</td>
                    <td className="py-2 px-4 text-right tabular-nums font-semibold text-emerald-700">{fmtUSD(u.cost_usd)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </CardContent>
        </Card>
      )}

      {/* Pricing note */}
      <p className="text-xs text-slate-500 italic px-1" data-testid="openai-costs-pricing-note">
        {data?.pricing_note}
      </p>
    </div>
  );
};

const BreakdownCard = ({ title, rows, labelKey, testid, formatLabel }) => {
  const fmtUSD = (n) => (n == null ? "—" : `$${Number(n).toFixed(2)}`);
  const total = rows.reduce((acc, r) => acc + (r.cost_usd || 0), 0);
  return (
    <Card data-testid={testid}>
      <CardHeader className="pb-2">
        <CardTitle className="text-sm">{title}</CardTitle>
      </CardHeader>
      <CardContent>
        {rows.length === 0 ? (
          <p className="text-xs text-slate-400 py-4 text-center">No data for this period.</p>
        ) : (
          <div className="space-y-2">
            {rows.map((r, i) => {
              const pct = total > 0 ? (r.cost_usd / total) * 100 : 0;
              const label = formatLabel ? formatLabel(r[labelKey]) : r[labelKey];
              return (
                <div key={`${r[labelKey]}-${i}`} data-testid={`${testid}-row-${i}`}>
                  <div className="flex items-center justify-between text-sm mb-1">
                    <span className="truncate font-medium text-slate-800">{label || "—"}</span>
                    <span className="tabular-nums text-emerald-700 font-semibold">{fmtUSD(r.cost_usd)}</span>
                  </div>
                  <div className="h-1.5 bg-slate-100 rounded overflow-hidden">
                    <div className="h-full bg-gradient-to-r from-emerald-600 to-emerald-400" style={{ width: `${pct}%` }} />
                  </div>
                  <p className="text-xs text-slate-400 mt-0.5">{r.calls} calls</p>
                </div>
              );
            })}
          </div>
        )}
      </CardContent>
    </Card>
  );
};

export default OpenAICostsPanel;
