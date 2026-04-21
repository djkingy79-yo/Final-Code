/* ========================================================================
   Barrister Tools Panel — three appellate-practice features in one card:
     1. Deadline Tracker (auto-compute + .ics export)
     2. Crown Response Simulator (stress-test a ground via AI rebuttal)
     3. Fresh Evidence Wizard (Gallagher-factor evaluation)
   All outputs respect the canonical print spec (Times 11pt / 14-12-12 /
   line 1.5 / 10pt gap) and use 3rd-person forensic Australian English.
   ====================================================================== */
import { useState, useEffect } from "react";
import axios from "axios";
import { toast } from "sonner";
import {
  CalendarClock, Download, Loader2, Gavel, ShieldAlert, ScrollText,
  AlertTriangle, CheckCircle2, XCircle, HelpCircle, Copy,
  Bell, ExternalLink
} from "lucide-react";
import { Button } from "./ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "./ui/card";
import { Badge } from "./ui/badge";
import { Input } from "./ui/input";
import { Label } from "./ui/label";
import { Textarea } from "./ui/textarea";
import {
  Select, SelectContent, SelectItem, SelectTrigger, SelectValue,
} from "./ui/select";
import {
  Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter,
} from "./ui/dialog";
import { API } from "../App";

// Utility — copy to clipboard with iOS Safari private-mode fallback
async function copyText(text) {
  try {
    if (navigator.clipboard && window.isSecureContext) {
      await navigator.clipboard.writeText(text);
    } else {
      const ta = document.createElement("textarea");
      ta.value = text;
      ta.style.position = "fixed";
      ta.style.opacity = "0";
      document.body.appendChild(ta);
      ta.select();
      document.execCommand("copy");
      ta.remove();
    }
    toast.success("Copied to clipboard");
  } catch {
    toast.error("Copy failed — long-press to select text");
  }
}

function daysBetween(dueIso) {
  const due = new Date(dueIso);
  const now = new Date();
  return Math.ceil((due.getTime() - now.getTime()) / 86400000);
}

function statusStyle(days, completed) {
  if (completed) return { label: "Completed", cls: "bg-slate-100 text-slate-500 border-slate-200" };
  if (days < 0) return { label: `${Math.abs(days)}d overdue`, cls: "bg-red-100 text-red-800 border-red-300" };
  if (days < 7) return { label: `${days}d left`, cls: "bg-red-50 text-red-700 border-red-200" };
  if (days < 14) return { label: `${days}d left`, cls: "bg-amber-50 text-amber-700 border-amber-200" };
  return { label: `${days}d left`, cls: "bg-emerald-50 text-emerald-700 border-emerald-200" };
}

// ===========================================================================
// DEADLINE TRACKER SUBSECTION
// ===========================================================================
function DeadlineTracker({ caseId, initialSentenceDate }) {
  const [deadlines, setDeadlines] = useState([]);
  const [loading, setLoading] = useState(false);
  const [sentenceDate, setSentenceDate] = useState(initialSentenceDate || "");
  const [lastComputed, setLastComputed] = useState(null);

  useEffect(() => {
    let cancelled = false;
    const load = async () => {
      try {
        const { data } = await axios.get(`${API}/cases/${caseId}/deadlines`);
        if (!cancelled) setDeadlines(data || []);
      } catch { /* silent */ }
    };
    if (caseId) load();
    return () => { cancelled = true; };
  }, [caseId]);

  const handleCompute = async () => {
    if (!sentenceDate) {
      toast.error("Enter the sentence date (YYYY-MM-DD) first");
      return;
    }
    try {
      setLoading(true);
      const { data } = await axios.post(
        `${API}/cases/${caseId}/deadlines/compute`,
        { sentence_date: sentenceDate }
      );
      setLastComputed(data);
      const refresh = await axios.get(`${API}/cases/${caseId}/deadlines`);
      setDeadlines(refresh.data || []);
      toast.success(`${data.computed_count} deadlines computed for ${data.court}`);
    } catch (err) {
      toast.error(err?.response?.data?.detail || "Failed to compute deadlines");
    } finally {
      setLoading(false);
    }
  };

  const handleDownloadIcs = async () => {
    try {
      const res = await axios.get(`${API}/cases/${caseId}/deadlines.ics`, { responseType: "blob" });
      const blob = new Blob([res.data], { type: "text/calendar;charset=utf-8" });
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = "appeal_deadlines.ics";
      document.body.appendChild(a);
      a.click();
      a.remove();
      setTimeout(() => URL.revokeObjectURL(url), 1000);
      toast.success("Calendar downloaded — import into Apple / Google / Outlook Calendar");
    } catch {
      toast.error("Calendar export failed");
    }
  };

  return (
    <Card data-testid="deadline-tracker">
      <CardHeader className="pb-3">
        <CardTitle className="flex items-center gap-2 text-[16px] font-bold" style={{ fontFamily: "'Times New Roman', Times, serif" }}>
          <CalendarClock className="w-5 h-5 text-blue-700" />
          Appeal Deadline Tracker
        </CardTitle>
        <p className="text-[12px] text-slate-600 mt-1">
          Auto-computes statutory time limits for the jurisdiction set on the case.
          Missing these dates is the #1 reason appeals are dismissed without reaching merit.
        </p>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="flex flex-wrap gap-2 items-end">
          <div className="flex-1 min-w-[180px]">
            <Label className="text-[12px] font-medium">Date of sentence</Label>
            <Input
              type="date"
              value={sentenceDate}
              onChange={(e) => setSentenceDate(e.target.value)}
              data-testid="deadline-sentence-date-input"
              className="mt-1"
            />
          </div>
          <Button
            onClick={handleCompute}
            disabled={loading || !sentenceDate}
            className="bg-blue-700 text-white hover:bg-blue-600"
            data-testid="deadline-compute-btn"
          >
            {loading ? <><Loader2 className="w-4 h-4 mr-2 animate-spin" /> Computing...</> : "Compute statutory deadlines"}
          </Button>
          {deadlines.length > 0 && (
            <Button
              variant="outline"
              onClick={handleDownloadIcs}
              data-testid="deadline-ics-export-btn"
            >
              <Download className="w-4 h-4 mr-2" />
              Export .ics
            </Button>
          )}
        </div>

        {lastComputed?.reference && (
          <div className="text-[11px] text-slate-500 italic">
            Reference: {lastComputed.reference} &mdash; {lastComputed.caveat}
          </div>
        )}

        {deadlines.length === 0 ? (
          <div className="text-[13px] text-slate-500 italic py-2">
            No deadlines recorded yet. Enter the sentence date and tap <strong>Compute</strong>.
          </div>
        ) : (
          <div className="space-y-2">
            {deadlines.map((d) => {
              const days = daysBetween(d.due_date);
              const stat = statusStyle(days, d.is_completed);
              return (
                <div
                  key={d.deadline_id}
                  className="flex items-start gap-3 p-3 rounded-lg border border-slate-200 bg-white"
                  data-testid={`deadline-row-${d.deadline_id}`}
                >
                  <div className="flex-1 min-w-0">
                    <div className="flex flex-wrap items-center gap-2 mb-1">
                      <p className="font-semibold text-[13px] text-slate-900">{d.title}</p>
                      <Badge variant="outline" className={`text-[10px] ${stat.cls}`}>{stat.label}</Badge>
                      {d.priority === "critical" && (
                        <Badge variant="outline" className="bg-red-50 text-red-700 border-red-200 text-[10px]">Critical</Badge>
                      )}
                    </div>
                    <p className="text-[11px] text-slate-500 mb-1">
                      Due {new Date(d.due_date).toLocaleDateString("en-AU", { day: "numeric", month: "long", year: "numeric" })}
                    </p>
                    <p className="text-[11px] text-slate-600 leading-relaxed">{d.description}</p>
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </CardContent>
    </Card>
  );
}

// ===========================================================================
// CROWN RESPONSE SIMULATOR SUBSECTION
// ===========================================================================
function CrownResponseSimulator({ caseId, grounds }) {
  const [selectedGround, setSelectedGround] = useState("");
  const [loading, setLoading] = useState(false);
  const [response, setResponse] = useState(null);

  useEffect(() => {
    setResponse(null);
  }, [selectedGround]);

  const handleGenerate = async () => {
    if (!selectedGround) {
      toast.error("Select a ground to stress-test");
      return;
    }
    try {
      setLoading(true);
      const { data } = await axios.post(
        `${API}/cases/${caseId}/grounds/${selectedGround}/crown-response`,
        {},
        { timeout: 150000 }
      );
      setResponse(data);
      toast.success(`Crown response generated — weakness score ${data.weakness_score}/10`);
    } catch (err) {
      toast.error(err?.response?.data?.detail || "Stress-test failed — retry in a moment");
    } finally {
      setLoading(false);
    }
  };

  const scoreColor = (s) => s >= 7 ? "text-red-700" : s >= 4 ? "text-amber-700" : "text-emerald-700";

  return (
    <Card data-testid="crown-response-simulator">
      <CardHeader className="pb-3">
        <CardTitle className="flex items-center gap-2 text-[16px] font-bold" style={{ fontFamily: "'Times New Roman', Times, serif" }}>
          <Gavel className="w-5 h-5 text-blue-700" />
          Crown Response Simulator
        </CardTitle>
        <p className="text-[12px] text-slate-600 mt-1">
          Generates the strongest version of the DPP's reply to a ground, with weakness
          score and authorities the Crown will rely on. Address the weaknesses BEFORE filing.
        </p>
      </CardHeader>
      <CardContent className="space-y-3">
        <div className="flex flex-wrap gap-2 items-end">
          <div className="flex-1 min-w-[220px]">
            <Label className="text-[12px] font-medium">Select ground to stress-test</Label>
            <Select value={selectedGround} onValueChange={setSelectedGround}>
              <SelectTrigger className="mt-1" data-testid="crown-ground-select">
                <SelectValue placeholder={grounds.length === 0 ? "No grounds yet — add one on the Grounds tab" : "Choose a ground"} />
              </SelectTrigger>
              <SelectContent>
                {grounds.map((g) => (
                  <SelectItem key={g.ground_id} value={g.ground_id}>
                    {g.title?.slice(0, 80) || g.ground_id}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>
          <Button
            onClick={handleGenerate}
            disabled={loading || !selectedGround}
            className="bg-blue-700 text-white hover:bg-blue-600"
            data-testid="crown-generate-btn"
          >
            {loading ? <><Loader2 className="w-4 h-4 mr-2 animate-spin" />Drafting Crown reply...</> : <>Generate Crown response</>}
          </Button>
        </div>

        {response && (
          <div className="mt-3 rounded-lg border-2 border-red-200 bg-red-50 p-4 space-y-3" data-testid="crown-response-output">
            <div className="flex items-center justify-between flex-wrap gap-2">
              <h4 className="font-bold text-[14px] text-red-900 flex items-center gap-2">
                <ShieldAlert className="w-4 h-4" /> Crown Written Submissions in Reply
              </h4>
              <div className={`text-[13px] font-bold ${scoreColor(response.weakness_score)}`}>
                Weakness score: {response.weakness_score}/10
              </div>
            </div>

            <div className="bg-white rounded border border-red-100 p-3">
              <div className="text-[11px] font-bold uppercase tracking-wide text-slate-500 mb-1">The Crown's rebuttal</div>
              <p className="text-[12px] leading-relaxed text-slate-800 whitespace-pre-wrap">{response.crown_rebuttal}</p>
              <button
                type="button"
                onClick={() => copyText(response.crown_rebuttal)}
                className="text-[11px] text-blue-700 hover:underline mt-2 flex items-center gap-1"
                data-testid="crown-copy-rebuttal"
              >
                <Copy className="w-3 h-3" /> Copy rebuttal
              </button>
            </div>

            <div>
              <div className="text-[11px] font-bold uppercase tracking-wide text-slate-500 mb-1">Weaknesses the Crown will exploit</div>
              <ul className="list-disc pl-5 text-[12px] space-y-1 text-slate-800">
                {response.weakness_reasons.map((r, i) => <li key={i}>{r}</li>)}
              </ul>
            </div>

            <div>
              <div className="text-[11px] font-bold uppercase tracking-wide text-slate-500 mb-1">Crown's key authorities (AGLC4)</div>
              <div className="flex flex-wrap gap-1">
                {response.key_counter_authorities.map((a, i) => (
                  <Badge key={i} variant="outline" className="bg-white border-red-200 text-red-800 text-[10px]">{a}</Badge>
                ))}
              </div>
            </div>

            <div className="bg-white rounded border border-emerald-200 p-3">
              <div className="text-[11px] font-bold uppercase tracking-wide text-emerald-700 mb-1">How the appellant should respond</div>
              <p className="text-[12px] leading-relaxed text-slate-800 whitespace-pre-wrap">{response.strategic_response}</p>
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  );
}

// ===========================================================================
// FRESH EVIDENCE (GALLAGHER) WIZARD SUBSECTION
// ===========================================================================
function FreshEvidenceWizard({ caseId }) {
  const [open, setOpen] = useState(false);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [form, setForm] = useState({
    evidence_description: "",
    reason_for_delay: "",
    materiality: "",
    credibility_basis: "",
    source_type: "affidavit",
  });
  const [history, setHistory] = useState([]);

  useEffect(() => {
    let cancelled = false;
    const load = async () => {
      try {
        const { data } = await axios.get(`${API}/cases/${caseId}/fresh-evidence`);
        if (!cancelled) setHistory(data || []);
      } catch { /* silent */ }
    };
    if (caseId) load();
    return () => { cancelled = true; };
  }, [caseId]);

  const setField = (k, v) => setForm((f) => ({ ...f, [k]: v }));

  const handleEvaluate = async () => {
    for (const [k, min] of [["evidence_description", 30], ["reason_for_delay", 30], ["materiality", 30]]) {
      if ((form[k] || "").trim().length < min) {
        toast.error(`"${k.replace(/_/g, " ")}" needs at least ${min} characters`);
        return;
      }
    }
    try {
      setLoading(true);
      const { data } = await axios.post(
        `${API}/cases/${caseId}/fresh-evidence/evaluate`,
        form,
        { timeout: 150000 }
      );
      setResult(data);
      setHistory((h) => [data, ...h]);
      toast.success(`Evaluation complete — admissibility likelihood: ${data.admissibility_likelihood}`);
    } catch (err) {
      toast.error(err?.response?.data?.detail || "Evaluation failed — refine inputs and retry");
    } finally {
      setLoading(false);
    }
  };

  const factorIcon = (status) => {
    if (status === "satisfied") return <CheckCircle2 className="w-4 h-4 text-emerald-600" />;
    if (status === "not_satisfied") return <XCircle className="w-4 h-4 text-red-600" />;
    return <HelpCircle className="w-4 h-4 text-amber-600" />;
  };

  const factorLabel = {
    new: "Evidence is 'new' (not before trial court)",
    reasonable_diligence: "Reasonable diligence could not have uncovered it",
    credible: "Evidence is credible / reliable",
    material: "Materiality — would have affected verdict",
  };

  return (
    <Card data-testid="fresh-evidence-wizard">
      <CardHeader className="pb-3">
        <CardTitle className="flex items-center gap-2 text-[16px] font-bold" style={{ fontFamily: "'Times New Roman', Times, serif" }}>
          <ScrollText className="w-5 h-5 text-blue-700" />
          Fresh Evidence Wizard (Gallagher)
        </CardTitle>
        <p className="text-[12px] text-slate-600 mt-1">
          Evaluates proposed fresh evidence against <em>R v Gallagher</em> (1986) 160 CLR 392,
          <em> Mickelberg</em> (1989) 167 CLR 259 and <em>R v Lawless</em> [1974] VR 398.
          Produces a submission-ready paragraph with AGLC4 citations.
        </p>
      </CardHeader>
      <CardContent className="space-y-3">
        <Button
          onClick={() => setOpen(true)}
          className="bg-blue-700 text-white hover:bg-blue-600"
          data-testid="fresh-evidence-open-btn"
        >
          New fresh-evidence evaluation
        </Button>

        {history.length > 0 && (
          <div className="mt-2">
            <div className="text-[12px] font-semibold text-slate-700 mb-2">Previous evaluations ({history.length})</div>
            <div className="space-y-2">
              {history.slice(0, 3).map((h) => (
                <button
                  key={h.application_id}
                  type="button"
                  onClick={() => setResult(h)}
                  className="w-full text-left p-2 rounded border border-slate-200 bg-white hover:bg-slate-50"
                  data-testid={`fresh-evidence-history-${h.application_id}`}
                >
                  <div className="flex items-center justify-between gap-2">
                    <span className="text-[12px] text-slate-800 truncate">{h.inputs?.evidence_description?.slice(0, 80) || "Evaluation"}</span>
                    <Badge variant="outline" className="text-[10px]">{h.admissibility_likelihood}</Badge>
                  </div>
                </button>
              ))}
            </div>
          </div>
        )}

        {result && (
          <div className="mt-3 rounded-lg border-2 border-blue-200 bg-blue-50 p-4 space-y-3" data-testid="fresh-evidence-output">
            <div className="flex items-center justify-between flex-wrap gap-2">
              <h4 className="font-bold text-[14px] text-blue-900">Gallagher factor assessment</h4>
              <Badge variant="outline" className="bg-white text-[11px]">
                Admissibility: {result.admissibility_likelihood}
              </Badge>
            </div>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-2">
              {["new", "reasonable_diligence", "credible", "material"].map((k) => {
                const f = result.gallagher_assessment?.[k] || {};
                return (
                  <div key={k} className="bg-white rounded border border-blue-100 p-3">
                    <div className="flex items-center gap-2 mb-1">
                      {factorIcon(f.status)}
                      <div className="text-[12px] font-bold text-slate-900">{factorLabel[k]}</div>
                    </div>
                    <div className="text-[11px] text-slate-600 leading-relaxed">{f.reasoning}</div>
                  </div>
                );
              })}
            </div>

            <div className="bg-white rounded border border-blue-200 p-3">
              <div className="flex items-center justify-between mb-1">
                <div className="text-[11px] font-bold uppercase tracking-wide text-blue-700">Submission paragraph (ready to paste)</div>
                <button
                  type="button"
                  onClick={() => copyText(result.submission_paragraph)}
                  className="text-[11px] text-blue-700 hover:underline flex items-center gap-1"
                  data-testid="fresh-evidence-copy-submission"
                >
                  <Copy className="w-3 h-3" /> Copy
                </button>
              </div>
              <p className="text-[12px] leading-relaxed text-slate-800 whitespace-pre-wrap" style={{ fontFamily: "'Times New Roman', Times, serif" }}>
                {result.submission_paragraph}
              </p>
            </div>

            <div>
              <div className="text-[11px] font-bold uppercase tracking-wide text-slate-500 mb-1">Recommended authorities</div>
              <div className="flex flex-wrap gap-1">
                {result.recommended_authorities.map((a, i) => (
                  <Badge key={i} variant="outline" className="bg-white text-[10px]">{a}</Badge>
                ))}
              </div>
            </div>

            <div>
              <div className="text-[11px] font-bold uppercase tracking-wide text-slate-500 mb-1">Practical next steps</div>
              <ul className="list-disc pl-5 text-[12px] space-y-1 text-slate-800">
                {result.practical_next_steps.map((s, i) => <li key={i}>{s}</li>)}
              </ul>
            </div>
          </div>
        )}
      </CardContent>

      <Dialog open={open} onOpenChange={setOpen}>
        <DialogContent className="max-w-2xl">
          <DialogHeader>
            <DialogTitle style={{ fontFamily: "'Times New Roman', Times, serif" }}>
              Fresh Evidence — Gallagher Factor Evaluation
            </DialogTitle>
            <p className="text-[11px] text-slate-500 mt-1">
              Apply <em>R v Gallagher</em> (1986) 160 CLR 392. Each field needs at least 30 characters.
            </p>
          </DialogHeader>
          <div className="space-y-3">
            <div>
              <Label className="text-[12px] font-medium">Source type</Label>
              <Select value={form.source_type} onValueChange={(v) => setField("source_type", v)}>
                <SelectTrigger data-testid="fresh-ev-source-type" className="mt-1"><SelectValue /></SelectTrigger>
                <SelectContent>
                  <SelectItem value="affidavit">Affidavit</SelectItem>
                  <SelectItem value="document">Documentary evidence</SelectItem>
                  <SelectItem value="forensic_report">Forensic report</SelectItem>
                  <SelectItem value="witness_statement">Witness statement</SelectItem>
                  <SelectItem value="expert_report">Expert report</SelectItem>
                  <SelectItem value="other">Other</SelectItem>
                </SelectContent>
              </Select>
            </div>
            <div>
              <Label className="text-[12px] font-medium">Evidence description — what is it, what does it prove?</Label>
              <Textarea rows={3} value={form.evidence_description}
                onChange={(e) => setField("evidence_description", e.target.value)}
                data-testid="fresh-ev-description" className="mt-1"
                placeholder="e.g. Signed affidavit of a witness, Jane Roberts, present at the incident, describing events inconsistent with the Crown's identification case." />
            </div>
            <div>
              <Label className="text-[12px] font-medium">Why was this evidence NOT before the trial court?</Label>
              <Textarea rows={3} value={form.reason_for_delay}
                onChange={(e) => setField("reason_for_delay", e.target.value)}
                data-testid="fresh-ev-delay" className="mt-1"
                placeholder="e.g. Witness only came forward after seeing media coverage post-verdict; she was not known to the defence at trial despite reasonable diligence." />
            </div>
            <div>
              <Label className="text-[12px] font-medium">Materiality — how would it have changed the verdict?</Label>
              <Textarea rows={3} value={form.materiality}
                onChange={(e) => setField("materiality", e.target.value)}
                data-testid="fresh-ev-materiality" className="mt-1"
                placeholder="e.g. Evidence directly contradicts the identification relied on by the Crown and would have raised reasonable doubt." />
            </div>
            <div>
              <Label className="text-[12px] font-medium">Credibility basis (optional but strongly recommended)</Label>
              <Textarea rows={2} value={form.credibility_basis}
                onChange={(e) => setField("credibility_basis", e.target.value)}
                data-testid="fresh-ev-credibility" className="mt-1"
                placeholder="e.g. Independent witness, no relationship to appellant, corroborated by CCTV from the same evening." />
            </div>
          </div>
          <DialogFooter className="mt-4">
            <Button variant="outline" onClick={() => setOpen(false)}>Cancel</Button>
            <Button
              onClick={async () => { await handleEvaluate(); if (!loading) setOpen(false); }}
              disabled={loading}
              className="bg-blue-700 text-white hover:bg-blue-600"
              data-testid="fresh-ev-evaluate-btn"
            >
              {loading ? <><Loader2 className="w-4 h-4 mr-2 animate-spin" />Applying Gallagher factors...</> : "Evaluate"}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </Card>
  );
}

// ===========================================================================
// LEGISLATION ALERTS PANEL — real-time amendment feed for this case
// ===========================================================================
function LegislationAlertsPanel({ caseId }) {
  const [data, setData] = useState({ alerts: [], total: 0, unread_count: 0, jurisdiction: "" });
  const [loading, setLoading] = useState(true);

  const load = async () => {
    try {
      setLoading(true);
      const res = await axios.get(`${API}/cases/${caseId}/legislation-alerts`);
      setData(res.data || { alerts: [], total: 0, unread_count: 0 });
    } catch {
      /* silent — endpoint may be empty on a brand-new case */
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (caseId) load();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [caseId]);

  const handleAcknowledge = async (amendmentId) => {
    try {
      await axios.post(`${API}/cases/${caseId}/legislation-alerts/${amendmentId}/acknowledge`);
      setData((prev) => ({
        ...prev,
        unread_count: Math.max(0, (prev.unread_count || 0) - 1),
        alerts: prev.alerts.map((a) => a.amendment_id === amendmentId ? { ...a, acknowledged: true } : a),
      }));
    } catch {
      toast.error("Failed to mark as read");
    }
  };

  const sevStyles = {
    critical: "bg-red-600 text-white border-red-700",
    high: "bg-amber-500 text-white border-amber-600",
    medium: "bg-blue-500 text-white border-blue-600",
    low: "bg-slate-400 text-white border-slate-500",
  };
  const jurStyles = {
    NSW: "bg-blue-100 text-blue-800 border-blue-300",
    VIC: "bg-purple-100 text-purple-800 border-purple-300",
    QLD: "bg-red-100 text-red-800 border-red-300",
    SA: "bg-red-100 text-red-800 border-red-300",
    WA: "bg-emerald-100 text-emerald-800 border-emerald-300",
    TAS: "bg-teal-100 text-teal-800 border-teal-300",
    NT: "bg-orange-100 text-orange-800 border-orange-300",
    ACT: "bg-indigo-100 text-indigo-800 border-indigo-300",
    CTH: "bg-slate-800 text-white border-slate-900",
  };

  return (
    <Card data-testid="legislation-alerts-panel">
      <CardHeader className="pb-3">
        <CardTitle className="flex items-center gap-2 text-[16px] font-bold" style={{ fontFamily: "'Times New Roman', Times, serif" }}>
          <Bell className="w-5 h-5 text-blue-700" />
          Legislative Change Alerts
          {data.unread_count > 0 && (
            <Badge className="bg-red-600 text-white ml-1" data-testid="legislation-unread-badge">
              {data.unread_count} new
            </Badge>
          )}
        </CardTitle>
        <p className="text-[12px] text-slate-600 mt-1">
          Confirmed amendments affecting this case's jurisdiction ({data.jurisdiction || "—"}) and federal law.
          Acts amended since last visit are flagged here so sentencing and procedural arguments remain current.
        </p>
      </CardHeader>
      <CardContent className="space-y-2">
        {loading ? (
          <div className="text-[12px] text-slate-500 italic py-2">Loading alerts...</div>
        ) : data.alerts.length === 0 ? (
          <div className="text-[12px] text-slate-500 italic py-2">
            No confirmed amendments affecting {data.jurisdiction || "this jurisdiction"} at this time.
          </div>
        ) : (
          data.alerts.map((a) => (
            <div
              key={a.amendment_id}
              className={`p-3 rounded-lg border ${a.acknowledged ? "border-slate-200 bg-slate-50 opacity-70" : "border-blue-200 bg-white"}`}
              data-testid={`legislation-alert-${a.amendment_id}`}
            >
              <div className="flex flex-wrap items-center gap-2 mb-1">
                <Badge variant="outline" className={`text-[10px] ${jurStyles[a.jurisdiction] || ""}`}>
                  {a.jurisdiction}
                </Badge>
                <Badge className={`text-[10px] ${sevStyles[a.severity] || sevStyles.medium}`}>
                  {a.severity}
                </Badge>
                <span className="text-[11px] text-slate-500">
                  Effective {new Date(a.effective_date).toLocaleDateString("en-AU", { day: "numeric", month: "long", year: "numeric" })}
                </span>
                {!a.acknowledged && (
                  <button
                    type="button"
                    onClick={() => handleAcknowledge(a.amendment_id)}
                    className="ml-auto text-[11px] text-blue-700 hover:underline"
                    data-testid={`legislation-alert-ack-${a.amendment_id}`}
                  >
                    Mark as read
                  </button>
                )}
              </div>
              <div className="font-semibold text-[13px] text-slate-900">
                {a.act_name}{a.section ? ` — ${a.section}` : ""}
              </div>
              {a.amending_act && (
                <div className="text-[11px] text-slate-500 italic mb-1">by {a.amending_act}</div>
              )}
              <p className="text-[12px] text-slate-700 leading-relaxed">{a.summary}</p>
              {a.source_url && (
                <a
                  href={a.source_url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-[11px] text-blue-700 hover:underline mt-1 inline-flex items-center gap-1"
                  data-testid={`legislation-alert-source-${a.amendment_id}`}
                >
                  <ExternalLink className="w-3 h-3" /> View on source register
                </a>
              )}
            </div>
          ))
        )}
      </CardContent>
    </Card>
  );
}


// ===========================================================================
// MAIN EXPORT
// ===========================================================================
export default function BarristerToolsPanel({ caseId, caseData, grounds = [] }) {
  const initialDate = caseData?.sentence_date ? String(caseData.sentence_date).slice(0, 10) : "";
  return (
    <div className="space-y-4" data-testid="barrister-tools-panel">
      <div className="flex items-center gap-2">
        <AlertTriangle className="w-5 h-5 text-blue-700" />
        <h2 className="text-[18px] font-bold text-blue-700" style={{ fontFamily: "'Times New Roman', Times, serif" }}>
          Barrister Tools
        </h2>
      </div>
      <LegislationAlertsPanel caseId={caseId} />
      <DeadlineTracker caseId={caseId} initialSentenceDate={initialDate} />
      <CrownResponseSimulator caseId={caseId} grounds={grounds} />
      <FreshEvidenceWizard caseId={caseId} />
    </div>
  );
}
