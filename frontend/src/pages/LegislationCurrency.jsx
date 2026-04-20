/* DO NOT UNDO — Legislation Currency admin page (14 Feb 2026).
   Forensic-first dashboard for keeping the legal framework anchored to
   current law. Every AI output is explicitly framed as a prompt for
   manual review — never as verification. */
import { useEffect, useMemo, useState } from "react";
import axios from "axios";
import { toast } from "sonner";
import { useNavigate } from "react-router-dom";
import {
  ArrowLeft, ExternalLink, CheckCircle2, Clock, AlertTriangle,
  Sparkles, Loader2, BookOpen, Shield,
} from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "../components/ui/card";
import { Button } from "../components/ui/button";
import { Badge } from "../components/ui/badge";
import {
  Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription, DialogFooter,
} from "../components/ui/dialog";
import { API } from "../App";

const JURISDICTION_LABELS = {
  nsw: "NSW", vic: "VIC", qld: "QLD", sa: "SA", wa: "WA",
  tas: "TAS", nt: "NT", act: "ACT", cth: "Cth",
};

const STATUS_META = {
  current: { label: "Current", colour: "emerald", Icon: CheckCircle2 },
  review_soon: { label: "Review soon", colour: "amber", Icon: Clock },
  overdue: { label: "Overdue", colour: "red", Icon: AlertTriangle },
};

const StatusBadge = ({ status }) => {
  const meta = STATUS_META[status] || STATUS_META.current;
  const Icon = meta.Icon;
  const colours = {
    emerald: "bg-emerald-50 text-emerald-700 border-emerald-200",
    amber: "bg-amber-50 text-amber-700 border-amber-200",
    red: "bg-red-50 text-red-700 border-red-200",
  };
  return (
    <span className={`inline-flex items-center gap-1 px-2 py-0.5 text-xs font-semibold rounded-full border ${colours[meta.colour]}`} data-testid={`legcur-status-${status}`}>
      <Icon className="w-3.5 h-3.5" />
      {meta.label}
    </span>
  );
};

const LegislationCurrency = () => {
  const navigate = useNavigate();
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [jurisdictionFilter, setJurisdictionFilter] = useState("");
  const [marking, setMarking] = useState(null);
  const [aiCheck, setAiCheck] = useState({ running: null, result: null, actName: null });

  const load = async (jur) => {
    setLoading(true);
    setError("");
    try {
      const params = jur ? { jurisdiction: jur } : {};
      const res = await axios.get(`${API}/admin/legislation-currency`, { params });
      setData(res.data);
    } catch (err) {
      if (err.response?.status === 403) setError("Admin access required.");
      else if (err.response?.status === 401) setError("Please sign in.");
      else setError(err.response?.data?.detail || err.message || "Failed to load.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { load(jurisdictionFilter); }, [jurisdictionFilter]);

  const handleMark = async (actName) => {
    setMarking(actName);
    try {
      const notes = window.prompt(
        `Forensic verification note for "${actName}".\n\n` +
        "Confirm you have manually verified this Act and its cited section numbers on AustLII or legislation.gov.au. " +
        "Enter a short forensic note (optional, e.g. 'confirmed ss.18, 33 still current 14 Feb 2026'):",
      );
      if (notes === null) {
        setMarking(null);
        return;
      }
      await axios.post(`${API}/admin/legislation-currency/mark-verified`, { act_name: actName, notes });
      toast.success(`Marked "${actName}" verified today.`);
      await load(jurisdictionFilter);
    } catch (err) {
      toast.error(err.response?.data?.detail || "Failed to mark verified.");
    } finally {
      setMarking(null);
    }
  };

  const handleAICheck = async (actName) => {
    setAiCheck({ running: actName, result: null, actName });
    try {
      const res = await axios.post(
        `${API}/admin/legislation-currency/ai-check`,
        { act_name: actName },
        { timeout: 120000 },
      );
      setAiCheck({ running: null, result: res.data, actName });
    } catch (err) {
      setAiCheck({
        running: null,
        actName,
        result: {
          ok: false,
          guardrail: "request_failed",
          error: err.response?.data?.detail || err.message || "Request failed",
          forensic_caveat: "AI cross-check did not complete. Please verify manually via AustLII.",
        },
      });
    }
  };

  const grouped = useMemo(() => {
    if (!data?.rows) return [];
    const map = new Map();
    for (const row of data.rows) {
      const list = map.get(row.jurisdiction) || [];
      list.push(row);
      map.set(row.jurisdiction, list);
    }
    return Array.from(map.entries());
  }, [data]);

  if (loading && !data) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-slate-50">
        <Loader2 className="w-8 h-8 animate-spin text-blue-600" />
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-slate-50" data-testid="legislation-currency-page">
      <header className="bg-white border-b border-slate-200 sticky top-0 z-10">
        <div className="max-w-7xl mx-auto px-6 py-4 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <Button variant="outline" size="sm" onClick={() => navigate("/admin")} data-testid="back-to-admin">
              <ArrowLeft className="w-4 h-4 mr-1.5" />
              Admin
            </Button>
            <h1 className="text-xl font-bold text-slate-900 flex items-center gap-2">
              <Shield className="w-5 h-5 text-blue-700" />
              Legislation Currency
            </h1>
          </div>
          {data && (
            <div className="flex items-center gap-2 text-sm">
              <Badge className="bg-emerald-100 text-emerald-700" data-testid="legcur-total-current">{data.totals.current} current</Badge>
              <Badge className="bg-amber-100 text-amber-700" data-testid="legcur-total-review">{data.totals.review_soon} review soon</Badge>
              <Badge className="bg-red-100 text-red-700" data-testid="legcur-total-overdue">{data.totals.overdue} overdue</Badge>
            </div>
          )}
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-6 py-8 space-y-6">
        {error && (
          <Card className="border-red-200 bg-red-50">
            <CardContent className="py-6 text-red-700 font-medium" data-testid="legcur-error">{error}</CardContent>
          </Card>
        )}

        {data?.forensic_notice && (
          <Card className="border-blue-200 bg-blue-50/60">
            <CardContent className="py-4 text-sm text-slate-800 flex gap-3" data-testid="legcur-forensic-notice">
              <BookOpen className="w-5 h-5 shrink-0 text-blue-700 mt-0.5" />
              <p>{data.forensic_notice}</p>
            </CardContent>
          </Card>
        )}

        {/* Jurisdiction filter */}
        <div className="flex flex-wrap gap-2" role="group" aria-label="Filter by jurisdiction">
          <Button
            size="sm"
            variant={jurisdictionFilter === "" ? "default" : "outline"}
            onClick={() => setJurisdictionFilter("")}
            className={jurisdictionFilter === "" ? "bg-blue-700 hover:bg-blue-800 text-white" : ""}
            data-testid="legcur-filter-all"
          >
            All jurisdictions
          </Button>
          {Object.entries(JURISDICTION_LABELS).map(([code, label]) => (
            <Button
              key={code}
              size="sm"
              variant={jurisdictionFilter === code ? "default" : "outline"}
              onClick={() => setJurisdictionFilter(code)}
              className={jurisdictionFilter === code ? "bg-blue-700 hover:bg-blue-800 text-white" : ""}
              data-testid={`legcur-filter-${code}`}
            >
              {label}
            </Button>
          ))}
        </div>

        {/* Table grouped by jurisdiction */}
        {grouped.map(([jur, rows]) => (
          <Card key={jur} data-testid={`legcur-group-${jur}`}>
            <CardHeader className="pb-3">
              <CardTitle className="text-base flex items-center gap-2">
                {JURISDICTION_LABELS[jur]}
                <span className="text-xs font-normal text-slate-500">({rows.length} Acts)</span>
              </CardTitle>
            </CardHeader>
            <CardContent className="p-0">
              <table className="w-full text-sm">
                <thead className="bg-slate-50 text-xs uppercase text-slate-500 border-y border-slate-200">
                  <tr>
                    <th className="text-left py-2 px-4">Act</th>
                    <th className="text-left py-2 px-4 whitespace-nowrap">Last verified</th>
                    <th className="text-left py-2 px-4">Status</th>
                    <th className="text-right py-2 px-4">Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {rows.map((row) => (
                    <tr key={row.act_name} className="border-t border-slate-100 hover:bg-slate-50/60" data-testid={`legcur-row-${row.jurisdiction}-${row.year}`}>
                      <td className="py-3 px-4 align-top">
                        <a
                          href={row.austlii_url}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="font-medium text-blue-700 hover:underline"
                          data-testid={`legcur-austlii-${row.act_name.replace(/[^a-zA-Z0-9]/g, '_')}`}
                        >
                          {row.act_name} <ExternalLink className="inline w-3 h-3 ml-0.5" />
                        </a>
                        {row.notes && <p className="text-xs text-slate-500 mt-1 italic">{row.notes}</p>}
                        {row.verified_by && (
                          <p className="text-xs text-slate-400 mt-1">Last ticked by <span className="font-mono">{row.verified_by}</span></p>
                        )}
                        <a
                          href={row.austlii_search_url}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="text-xs text-slate-400 hover:text-slate-600 underline"
                        >
                          AustLII search fallback
                        </a>
                      </td>
                      <td className="py-3 px-4 align-top whitespace-nowrap">
                        <div className="text-slate-900 tabular-nums">{row.last_verified}</div>
                        <div className="text-xs text-slate-500">{row.days_since_verified} days ago</div>
                      </td>
                      <td className="py-3 px-4 align-top">
                        <StatusBadge status={row.status} />
                      </td>
                      <td className="py-3 px-4 align-top text-right space-x-2 whitespace-nowrap">
                        <Button
                          size="sm"
                          variant="outline"
                          onClick={() => handleAICheck(row.act_name)}
                          disabled={aiCheck.running === row.act_name}
                          className="text-xs"
                          data-testid={`legcur-ai-check-${row.jurisdiction}-${row.year}`}
                        >
                          {aiCheck.running === row.act_name ? (
                            <Loader2 className="w-3.5 h-3.5 animate-spin" />
                          ) : (
                            <><Sparkles className="w-3.5 h-3.5 mr-1" />AI check</>
                          )}
                        </Button>
                        <Button
                          size="sm"
                          onClick={() => handleMark(row.act_name)}
                          disabled={marking === row.act_name}
                          className="bg-blue-700 hover:bg-blue-800 text-white text-xs"
                          data-testid={`legcur-mark-${row.jurisdiction}-${row.year}`}
                        >
                          {marking === row.act_name ? (
                            <Loader2 className="w-3.5 h-3.5 animate-spin" />
                          ) : (
                            <>Mark verified</>
                          )}
                        </Button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </CardContent>
          </Card>
        ))}
      </main>

      {/* AI check result dialog */}
      <Dialog open={!!aiCheck.result} onOpenChange={(open) => { if (!open) setAiCheck({ running: null, result: null, actName: null }); }}>
        <DialogContent className="sm:max-w-xl bg-white text-slate-900" data-testid="legcur-ai-dialog">
          <DialogHeader>
            <DialogTitle className="flex items-center gap-2">
              <Sparkles className="w-5 h-5 text-blue-700" />
              AI currency cross-check — {aiCheck.actName}
            </DialogTitle>
            <DialogDescription className="text-amber-700 font-medium">
              This is a PROMPT FOR MANUAL REVIEW. It is not verification.
            </DialogDescription>
          </DialogHeader>

          {aiCheck.result && !aiCheck.result.ok && (
            <div className="bg-red-50 border border-red-200 rounded-lg p-4 text-sm" data-testid="legcur-ai-guardrail-tripped">
              <p className="font-semibold text-red-800 mb-1">Guardrail tripped — output suppressed.</p>
              <p className="text-red-700">{aiCheck.result.error}</p>
              <p className="text-xs text-slate-600 mt-3 italic">{aiCheck.result.forensic_caveat}</p>
            </div>
          )}

          {aiCheck.result && aiCheck.result.ok && (
            <div className="space-y-3" data-testid="legcur-ai-result">
              <div className="flex flex-wrap gap-2">
                <Badge className={`${
                  aiCheck.result.status === "appears_current" ? "bg-emerald-100 text-emerald-700" :
                  aiCheck.result.status === "possible_change" ? "bg-amber-100 text-amber-700" :
                  "bg-slate-100 text-slate-700"
                }`}>
                  status: {aiCheck.result.status}
                </Badge>
                <Badge variant="outline">confidence: {aiCheck.result.confidence}</Badge>
                <Badge variant="outline">training cutoff: {aiCheck.result.knowledge_cutoff}</Badge>
              </div>

              <div>
                <p className="text-xs font-semibold text-slate-500 uppercase mb-1">Forensic summary</p>
                <p className="text-sm text-slate-800">{aiCheck.result.forensic_summary}</p>
              </div>

              {aiCheck.result.suggested_review_focus?.length > 0 && (
                <div>
                  <p className="text-xs font-semibold text-slate-500 uppercase mb-1">Suggested review focus</p>
                  <ul className="list-disc pl-5 text-sm text-slate-800 space-y-1">
                    {aiCheck.result.suggested_review_focus.map((s, i) => <li key={i}>{s}</li>)}
                  </ul>
                </div>
              )}

              {aiCheck.result.flagged_amendments?.length > 0 && (
                <div>
                  <p className="text-xs font-semibold text-slate-500 uppercase mb-1">Flagged amendments</p>
                  <ul className="list-disc pl-5 text-sm text-slate-800 space-y-1">
                    {aiCheck.result.flagged_amendments.map((a, i) => (
                      <li key={i}>
                        <span className="font-medium">~{a.approximate_year}:</span> {a.description}
                        {a.source_hint && <span className="text-xs text-slate-500"> (source: {a.source_hint})</span>}
                      </li>
                    ))}
                  </ul>
                </div>
              )}

              <div className="bg-amber-50 border border-amber-200 rounded-lg p-3 text-xs text-amber-900">
                <p className="font-semibold mb-1">Forensic caveat</p>
                <p>{aiCheck.result.forensic_caveat}</p>
              </div>
            </div>
          )}

          <DialogFooter>
            <Button
              variant="outline"
              onClick={() => setAiCheck({ running: null, result: null, actName: null })}
              data-testid="legcur-ai-close"
            >
              Close
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
};

export default LegislationCurrency;
