/*
  EvidenceProfilePanel.jsx

  A 19-checkbox questionnaire that feeds the backend realism scorer
  (/app/backend/services/appeal_strength.py). Grouped into 4 logical
  sections: Record Anchors, Crown Case Strength, Defence Indicators, and
  a Save button that triggers a grounds re-sync so the RealismBadges on
  every ground update immediately.
*/

import { useEffect, useState } from "react";
import axios from "axios";
import { toast } from "sonner";
import { API } from "../App";
import { Button } from "./ui/button";
import { Checkbox } from "./ui/checkbox";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "./ui/card";
import { Loader2, Save, Scale } from "lucide-react";

const GROUPS = [
  {
    heading: "Record anchors",
    desc: "What corroborating documentation is actually on the case file?",
    items: [
      { key: "has_trial_transcript",           label: "Trial transcript" },
      { key: "has_sentencing_remarks",         label: "Sentencing remarks / judge's reasons on sentence" },
      { key: "has_psychiatric_reports",        label: "Psychiatric / psychological reports" },
      { key: "has_counsel_affidavit",          label: "Affidavit from trial counsel" },
      { key: "has_juror_affidavit",            label: "Juror affidavit / admissible jury evidence" },
      { key: "has_expert_reports",             label: "Other expert reports (forensic, medical, etc.)" },
      { key: "has_judge_alone_material",       label: "Judge-alone application material" },
      { key: "has_pretrial_publicity_material",label: "Pre-trial publicity material" },
    ],
  },
  {
    heading: "Crown case strength",
    desc: "Indicators suggesting the prosecution case was strong at trial.",
    items: [
      { key: "has_direct_evidence",                 label: "Direct eyewitness evidence of the offence" },
      { key: "multiple_consistent_witnesses",       label: "Multiple consistent witnesses" },
      { key: "has_forensic_evidence",               label: "Forensic evidence (DNA, ballistics, prints, etc.)" },
      { key: "has_strong_circumstantial_evidence",  label: "Strong circumstantial case" },
      { key: "confession_or_admission",             label: "Confession / admission by the appellant" },
      { key: "cctv_or_audio",                       label: "CCTV or audio recording" },
      { key: "post_offence_conduct_supports_guilt", label: "Post-offence conduct supports guilt (flight, concealment, lies)" },
    ],
  },
  {
    heading: "Defence / weakness indicators",
    desc: "Factors that may soften Crown case or support appeal grounds.",
    items: [
      { key: "disputed_identity",             label: "Identity of offender genuinely disputed" },
      { key: "disputed_intent",               label: "Intent / mens rea genuinely disputed" },
      { key: "competing_psychiatric_opinions",label: "Competing psychiatric opinions (defence vs Crown)" },
      { key: "no_eyewitnesses",               label: "No eyewitnesses to the offence" },
    ],
  },
];

const EMPTY = {
  has_trial_transcript: false, has_sentencing_remarks: false, has_psychiatric_reports: false,
  has_counsel_affidavit: false, has_juror_affidavit: false, has_expert_reports: false,
  has_judge_alone_material: false, has_pretrial_publicity_material: false,
  has_forensic_evidence: false, has_direct_evidence: false, has_strong_circumstantial_evidence: false,
  multiple_consistent_witnesses: false, confession_or_admission: false, cctv_or_audio: false,
  post_offence_conduct_supports_guilt: false, disputed_identity: false, disputed_intent: false,
  competing_psychiatric_opinions: false, no_eyewitnesses: false,
};

export const EvidenceProfilePanel = ({ caseId, onSaved }) => {
  const [profile, setProfile] = useState(EMPTY);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [dirty, setDirty] = useState(false);

  useEffect(() => {
    if (!caseId) return;
    const token = localStorage.getItem("auth_token");
    axios
      .get(`${API}/cases/${caseId}/evidence-profile`, {
        headers: token ? { Authorization: `Bearer ${token}` } : {},
      })
      .then((res) => setProfile({ ...EMPTY, ...(res.data || {}) }))
      .catch(() => { /* fall back to empty */ })
      .finally(() => setLoading(false));
  }, [caseId]);

  const toggle = (key) => {
    setProfile((p) => ({ ...p, [key]: !p[key] }));
    setDirty(true);
  };

  const save = async () => {
    setSaving(true);
    try {
      const token = localStorage.getItem("auth_token");
      await axios.put(
        `${API}/cases/${caseId}/evidence-profile`,
        profile,
        { headers: token ? { Authorization: `Bearer ${token}` } : {} }
      );
      toast.success("Evidence profile saved — grounds will re-score shortly");
      setDirty(false);
      if (onSaved) onSaved();
    } catch (e) {
      toast.error(e?.response?.data?.detail || "Save failed");
    } finally {
      setSaving(false);
    }
  };

  const checkedCount = Object.values(profile).filter(Boolean).length;

  return (
    <Card className="border-slate-200" data-testid="evidence-profile-panel">
      <CardHeader>
        <div className="flex items-center justify-between gap-3">
          <div className="flex items-center gap-2">
            <Scale className="w-5 h-5 text-blue-600" />
            <CardTitle className="text-lg">Case Evidence Profile</CardTitle>
          </div>
          <span className="text-xs text-slate-500" data-testid="evidence-profile-count">
            {checkedCount} / 19 factors
          </span>
        </div>
        <CardDescription>
          Tick what actually exists on the case record. These factors feed the
          forensic realism scoring — without them, every ground is treated
          conservatively. Takes 30 seconds; saves immediately and re-scores
          all grounds.
        </CardDescription>
      </CardHeader>
      <CardContent>
        {loading ? (
          <div className="flex items-center gap-2 text-slate-500 text-sm py-4">
            <Loader2 className="w-4 h-4 animate-spin" /> Loading profile…
          </div>
        ) : (
          <div className="space-y-6">
            {GROUPS.map((g) => (
              <div key={g.heading} data-testid={`evidence-profile-group-${g.heading.replace(/\s+/g, '-').toLowerCase()}`}>
                <h4 className="text-sm font-semibold text-slate-800 uppercase tracking-wide mb-1">
                  {g.heading}
                </h4>
                <p className="text-xs text-slate-500 mb-3">{g.desc}</p>
                <div className="grid sm:grid-cols-2 gap-2">
                  {g.items.map((it) => (
                    <label
                      key={it.key}
                      htmlFor={`ep-${it.key}`}
                      className="flex items-start gap-2 text-sm text-slate-800 cursor-pointer hover:bg-slate-50 rounded px-2 py-1.5"
                      data-testid={`evidence-profile-row-${it.key}`}
                    >
                      <Checkbox
                        id={`ep-${it.key}`}
                        checked={!!profile[it.key]}
                        onCheckedChange={() => toggle(it.key)}
                        data-testid={`evidence-profile-check-${it.key}`}
                      />
                      <span className="leading-snug">{it.label}</span>
                    </label>
                  ))}
                </div>
              </div>
            ))}

            <div className="pt-2 flex items-center justify-end gap-3 border-t border-slate-200">
              {dirty && (
                <span className="text-xs text-amber-700" data-testid="evidence-profile-dirty-notice">
                  Unsaved changes
                </span>
              )}
              <Button
                onClick={save}
                disabled={saving || !dirty}
                className="bg-blue-600 hover:bg-blue-700 text-white"
                data-testid="evidence-profile-save-button"
              >
                {saving ? <Loader2 className="w-4 h-4 mr-2 animate-spin" /> : <Save className="w-4 h-4 mr-2" />}
                Save & Re-score Grounds
              </Button>
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  );
};

export default EvidenceProfilePanel;
