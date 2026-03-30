const LegitimacyPanel = ({ scores }) => {
  if (!scores) return null;

  return (
    <div data-testid="legitimacy-panel" className="mt-3 rounded border border-slate-200 p-3 text-sm bg-slate-50">
      <div className="font-semibold mb-2 text-slate-800">Legitimacy Assessment</div>
      <div className="grid grid-cols-3 gap-2 text-slate-700">
        <div>Legal basis: <span className="font-semibold">{scores.legal_score}/3</span></div>
        <div>Evidence support: <span className="font-semibold">{scores.evidence_score}/3</span></div>
        <div>Appellate viability: <span className="font-semibold">{scores.viability_score}/3</span></div>
      </div>
      <div className="font-semibold mt-2 text-slate-900">Total: {scores.total_score}/9</div>
      {scores.confidence_note ? (
        <div className="mt-2 text-xs text-slate-500 italic leading-tight">{scores.confidence_note}</div>
      ) : null}
    </div>
  );
};

export default LegitimacyPanel;
