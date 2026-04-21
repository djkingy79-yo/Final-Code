import { useState } from "react";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription, DialogFooter } from "./ui/dialog";
import { Button } from "./ui/button";
import { Checkbox } from "./ui/checkbox";
import { Printer, Download, FileText } from "lucide-react";

/**
 * Pre-export options picker for the "Print All / PDF All / Word All" case bundle.
 * Lets the user choose which sections end up in the output. Defaults mirror the
 * previous behaviour (everything on) so existing users see no change unless they
 * untick something.
 *
 * Usage:
 *   const [opts, setOpts] = useState(defaultSectionOptions);
 *   <ExportOptionsModal
 *     open={showExportOpts}
 *     mode={exportMode}            // "print" | "pdf" | "word"
 *     availability={{ summary: !!caseData?.summary, documents: docs.length>0, ... }}
 *     onCancel={() => setShowExportOpts(false)}
 *     onConfirm={(chosen) => { setShowExportOpts(false); doExport(chosen); }}
 *   />
 */

export const defaultSectionOptions = {
  cover: true,
  toc: true,
  summary: true,
  documents: true,
  timeline: true,
  grounds: true,
  legislation: true,
  notes: true,
  progress: true,
  quick_summary: true,
  full_detailed: true,
  extensive_log: true,
  barrister_view: true,
};

// Pre-built profiles — one-click combinations. Keys match defaultSectionOptions.
const PRESETS = [
  {
    id: "full",
    label: "Full Archive",
    desc: "Everything — all sections and all four AI reports (Quick / Full / Extensive / Barrister)",
    sections: { cover: true, toc: true, summary: true, documents: true, timeline: true, grounds: true, legislation: true, notes: true, progress: true, quick_summary: true, full_detailed: true, extensive_log: true, barrister_view: true },
  },
  {
    id: "barrister",
    label: "Brief for Barrister",
    desc: "Cover + grounds + timeline + summary + Appellate Research Brief — counsel-ready essentials",
    sections: { cover: true, toc: true, summary: true, documents: false, timeline: true, grounds: true, legislation: true, notes: false, progress: false, quick_summary: false, full_detailed: false, extensive_log: false, barrister_view: true },
  },
  {
    id: "client",
    label: "Client-friendly Summary",
    desc: "Cover + summary + Quick Summary report + progress — readable overview without legal detail",
    sections: { cover: true, toc: false, summary: true, documents: false, timeline: false, grounds: false, legislation: false, notes: false, progress: true, quick_summary: true, full_detailed: false, extensive_log: false, barrister_view: false },
  },
  {
    id: "evidence",
    label: "Evidence Pack",
    desc: "Cover + documents list + timeline — just the facts",
    sections: { cover: true, toc: true, summary: false, documents: true, timeline: true, grounds: false, legislation: false, notes: false, progress: false, quick_summary: false, full_detailed: false, extensive_log: false, barrister_view: false },
  },
];

const SECTION_LABELS = [
  { key: "cover",         label: "Cover page & case metadata", desc: "Header, defendant, offence, sentence, document counts" },
  { key: "toc",           label: "Table of contents",          desc: "Auto-generated contents list for the included sections" },
  { key: "summary",       label: "Case summary",               desc: "Your written summary of the case" },
  { key: "documents",     label: "Uploaded documents list",    desc: "Table of all documents uploaded (filename, type, date)" },
  { key: "timeline",      label: "Timeline of events",         desc: "Chronological case timeline table" },
  { key: "grounds",       label: "Grounds of merit",           desc: "All identified grounds with analysis, evidence, legislation" },
  { key: "legislation",   label: "Legislation & case law",     desc: "Consolidated list of statutes and cases cited across grounds" },
  { key: "notes",         label: "Case notes",                 desc: "Notes you or collaborators have written" },
  { key: "progress",      label: "Progress analysis",          desc: "AI-generated overall case-readiness assessment" },
  { key: "quick_summary", label: "Quick Summary report",       desc: "7-section plain-English case snapshot" },
  { key: "full_detailed", label: "Full Detailed Legal Analysis", desc: "Comprehensive legal analysis with comparative sentencing" },
  { key: "extensive_log", label: "Extensive Case Log & Analysis", desc: "Deepest 20+ section forensic log" },
  { key: "barrister_view",label: "Appellate Research Brief",   desc: "The fourth report — the counsel-ready synthesis" },
];

const ExportOptionsModal = ({ open, mode = "print", availability = {}, onCancel, onConfirm }) => {
  const [sections, setSections] = useState(defaultSectionOptions);

  const modeLabel = mode === "pdf" ? "PDF" : mode === "word" ? "Word" : "Print";
  const ModeIcon = mode === "pdf" ? Download : mode === "word" ? FileText : Printer;

  const toggle = (key) => setSections((s) => ({ ...s, [key]: !s[key] }));
  const selectAll = () => setSections(Object.fromEntries(SECTION_LABELS.map(({ key }) => [key, true])));
  const selectNone = () => setSections(Object.fromEntries(SECTION_LABELS.map(({ key }) => [key, false])));

  const anySelected = Object.values(sections).some(Boolean);

  return (
    <Dialog open={open} onOpenChange={(o) => { if (!o) onCancel(); }}>
      <DialogContent className="sm:max-w-md" data-testid="export-options-modal">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2">
            <ModeIcon className="w-5 h-5 text-blue-700" />
            {modeLabel} Options
          </DialogTitle>
          <DialogDescription>
            Choose which sections to include in the {modeLabel.toLowerCase()}.
            Untick anything you don't need.
          </DialogDescription>
        </DialogHeader>

        <div className="space-y-2 pb-1">
          <p className="text-xs font-semibold uppercase tracking-wider text-slate-500">Quick presets</p>
          <div className="flex flex-wrap gap-1.5">
            {PRESETS.map((p) => (
              <button
                key={p.id}
                type="button"
                onClick={() => setSections(p.sections)}
                title={p.desc}
                className="text-xs px-3 py-1.5 rounded-full border border-blue-200 bg-blue-50 text-blue-800 font-medium hover:bg-blue-100 hover:border-blue-400"
                data-testid={`export-preset-${p.id}`}
              >
                {p.label}
              </button>
            ))}
          </div>
        </div>

        <div className="space-y-3 py-2">
          {SECTION_LABELS.map(({ key, label, desc }) => {
            const isAvailable = availability[key] !== false;
            return (
              <label
                key={key}
                className={`flex items-start gap-3 p-2 rounded-lg border ${isAvailable ? "border-slate-200 hover:bg-slate-50 cursor-pointer" : "border-slate-100 bg-slate-50 opacity-50 cursor-not-allowed"}`}
                data-testid={`export-opt-${key}`}
              >
                <Checkbox
                  checked={!!sections[key] && isAvailable}
                  onCheckedChange={() => isAvailable && toggle(key)}
                  disabled={!isAvailable}
                  className="mt-0.5"
                />
                <div className="flex-1 min-w-0">
                  <div className="text-sm font-semibold text-slate-900">
                    {label}
                    {!isAvailable && <span className="text-xs font-normal text-slate-400 ml-2">(no content)</span>}
                  </div>
                  <div className="text-xs text-slate-500">{desc}</div>
                </div>
              </label>
            );
          })}
        </div>

        <div className="flex items-center gap-2 text-xs">
          <button onClick={selectAll}  type="button" className="text-blue-700 hover:underline" data-testid="export-select-all">Select all</button>
          <span className="text-slate-300">·</span>
          <button onClick={selectNone} type="button" className="text-slate-500 hover:underline" data-testid="export-select-none">Select none</button>
        </div>

        <DialogFooter className="gap-2">
          <Button variant="outline" onClick={onCancel} data-testid="export-options-cancel">Cancel</Button>
          <Button
            className="bg-blue-700 text-white hover:bg-blue-600"
            disabled={!anySelected}
            onClick={() => onConfirm(sections)}
            data-testid="export-options-confirm"
          >
            <ModeIcon className="w-4 h-4 mr-1.5" />
            {modeLabel}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
};

export default ExportOptionsModal;
