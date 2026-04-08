const LegitimacyPanel = ({ scores }) => {
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
        <div className="mt-2 text-xs text-slate-500 italic leading-tight">{scores.confidence_note}</div>
      ) : null}
    </div>
  );
};

export default LegitimacyPanel;
