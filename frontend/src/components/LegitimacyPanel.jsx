import { useState } from "react";
import { ChevronDown, ChevronUp } from "lucide-react";
import auSpelling from "../utils/auSpelling";

const LegitimacyPanel = ({ scores }) => {
  const [showGlossary, setShowGlossary] = useState(false);

  if (!scores) return null;

  const viabilityColors = {
    "strong": "text-emerald-700 bg-emerald-50 border-emerald-200",
    "moderate": "text-blue-700 bg-blue-50 border-blue-200",
    "weak": "text-red-700 bg-red-50 border-red-200",
  };

  const viabilityColor = viabilityColors[scores.rating] || viabilityColors.moderate;

  return (
    <div data-testid="legitimacy-panel" className="mt-3 rounded-lg border border-slate-200 p-3 text-sm bg-slate-50">
      <div className="font-bold mb-2 text-slate-800">Appellate Viability Assessment</div>
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-2 text-slate-700">
        <div className="p-2 bg-white rounded border border-slate-100">
          <div className="text-xs text-slate-500 mb-0.5">Outcome Impact</div>
          <div className="font-bold text-sm">{scores.outcome_impact?.label || `${scores.viability_score || 0}/3`}</div>
        </div>
        <div className="p-2 bg-white rounded border border-slate-100">
          <div className="text-xs text-slate-500 mb-0.5">Legal Alignment</div>
          <div className="font-bold text-sm">{scores.legal_alignment?.label || `${scores.legal_score || 0}/3`}</div>
        </div>
        <div className="p-2 bg-white rounded border border-slate-100">
          <div className="text-xs text-slate-500 mb-0.5">Evidence Support</div>
          <div className="font-bold text-sm">{scores.evidence_support?.label || `${scores.evidence_score || 0}/3`}</div>
        </div>
      </div>
      <div className={`mt-2 p-2 rounded border font-bold text-sm ${viabilityColor}`}>
        {scores.viability_label || (scores.rating === "strong" ? "Arguable \u2014 Strong" : scores.rating === "moderate" ? "Arguable \u2014 Moderate" : "Requires Development")}
        <span className="text-xs font-normal ml-2 opacity-70">({scores.total_score || 0}/9)</span>
      </div>
      {scores.is_contingent ? (
        <div data-testid="contingent-warning" className="mt-2 px-2 py-1.5 rounded border border-amber-300 bg-amber-50 text-xs text-amber-800 font-medium leading-tight">
          CONTINGENT — Requires evidentiary support before advancement (affidavit, transcript confirmation)
        </div>
      ) : null}
      {scores.confidence_note ? (
        <div className="mt-2 text-xs text-slate-500 italic leading-tight">{auSpelling(scores.confidence_note)}</div>
      ) : null}

      {/* Glossary Toggle */}
      <button
        data-testid="glossary-toggle"
        onClick={() => setShowGlossary(!showGlossary)}
        className="mt-3 flex items-center gap-1 text-xs text-blue-600 hover:text-blue-800 font-medium transition-colors"
      >
        {showGlossary ? <ChevronUp className="w-3 h-3" /> : <ChevronDown className="w-3 h-3" />}
        {showGlossary ? "Hide Glossary" : "What do these terms mean?"}
      </button>

      {/* Glossary Content */}
      {showGlossary && (
        <div data-testid="viability-glossary" className="mt-2 p-3 bg-white rounded-lg border border-slate-200 text-xs text-slate-600 space-y-3">
          <div>
            <div className="font-bold text-slate-800 mb-1">Outcome Impact</div>
            <p className="leading-relaxed">How significantly this ground could affect the appeal result if successful.</p>
            <ul className="mt-1 ml-3 space-y-0.5 list-disc">
              <li><span className="font-semibold text-slate-700">Determinative:</span> If this ground succeeds, it alone would likely result in the appeal being allowed (e.g. the conviction quashed or a retrial ordered).</li>
              <li><span className="font-semibold text-slate-700">Influential:</span> This ground substantially strengthens the appeal but may not be sufficient on its own to secure the outcome.</li>
              <li><span className="font-semibold text-slate-700">Minor:</span> This ground provides additional support but is unlikely to determine the result independently.</li>
            </ul>
          </div>

          <div>
            <div className="font-bold text-slate-800 mb-1">Legal Alignment</div>
            <p className="leading-relaxed">How directly existing legal authority (legislation and case law) supports this ground.</p>
            <ul className="mt-1 ml-3 space-y-0.5 list-disc">
              <li><span className="font-semibold text-slate-700">Direct authority:</span> There is binding or highly persuasive precedent that directly supports this ground of appeal.</li>
              <li><span className="font-semibold text-slate-700">Analogous:</span> There is relevant authority that can be applied by analogy, but it is not directly on point.</li>
              <li><span className="font-semibold text-slate-700">Weak:</span> Limited legal authority exists to support this ground — it may require novel argument or distinguishing adverse authority.</li>
            </ul>
          </div>

          <div>
            <div className="font-bold text-slate-800 mb-1">Evidence Support</div>
            <p className="leading-relaxed">How strongly the available case materials and documents support this ground.</p>
            <ul className="mt-1 ml-3 space-y-0.5 list-disc">
              <li><span className="font-semibold text-slate-700">Strong:</span> Multiple, clear pieces of evidence in the record directly support this ground.</li>
              <li><span className="font-semibold text-slate-700">Partial:</span> Some supporting evidence exists but gaps remain that require further substantiation.</li>
              <li><span className="font-semibold text-slate-700">Limited:</span> Minimal evidence currently available — requires further documentary substantiation before this ground can be advanced with confidence.</li>
            </ul>
          </div>

          <div>
            <div className="font-bold text-slate-800 mb-1">Viability Rating (Overall)</div>
            <p className="leading-relaxed">The combined assessment across all three axes, scored out of 9.</p>
            <ul className="mt-1 ml-3 space-y-0.5 list-disc">
              <li><span className="font-semibold text-emerald-700">Arguable — Strong:</span> This ground has strong prospects on appeal and warrants prioritisation in the notice of appeal.</li>
              <li><span className="font-semibold text-blue-700">Arguable — Moderate:</span> This ground is viable but requires further development, evidence, or refinement before it reaches its full potential.</li>
              <li><span className="font-semibold text-red-700">Requires Development:</span> This ground needs significant additional material, research, or evidentiary support before it should be advanced.</li>
            </ul>
          </div>

          <div className="pt-1 border-t border-slate-100">
            <div className="font-bold text-slate-800 mb-1">Contingent Ground</div>
            <p className="leading-relaxed">A ground marked as <span className="font-semibold text-amber-700">CONTINGENT</span> has an extremely high evidentiary threshold. It requires specific supporting material (such as an affidavit from the accused, evidence of advice given, or transcript confirmation) before it can be properly advanced. Without this foundation, including the ground risks weakening overall appellate credibility.</p>
          </div>
        </div>
      )}
    </div>
  );
};

export default LegitimacyPanel;
