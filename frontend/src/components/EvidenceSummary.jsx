const EvidenceSummary = ({ items = [] }) => {
  if (!items.length) {
    return <div data-testid="evidence-summary-empty" className="text-xs text-slate-400">No structured evidence linked yet</div>;
  }

  return (
    <div data-testid="evidence-summary" className="mt-2 text-xs">
      <div className="font-medium mb-1 text-slate-700">Supporting Evidence ({items.length})</div>
      {items.slice(0, 2).map((item, idx) => {
        const text = typeof item === "string" ? item : (item?.quote || item?.text || "Evidence item");
        const filename = typeof item === "object" ? item?.filename : null;
        return (
          <div key={idx} className="mb-1 text-slate-600">
            {filename ? <span className="font-medium">{filename}: </span> : null}
            <span>{text}</span>
          </div>
        );
      })}
      {items.length > 2 && (
        <div className="text-slate-400">+{items.length - 2} more</div>
      )}
    </div>
  );
};

export default EvidenceSummary;
