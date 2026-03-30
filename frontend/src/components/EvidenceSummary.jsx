const EvidenceSummary = ({ items = [], expanded = false }) => {
  if (!Array.isArray(items) || items.length === 0) {
    return <div data-testid="evidence-summary-empty" className="text-xs text-slate-400 mt-2">No structured evidence linked yet</div>;
  }

  const displayCount = expanded ? 5 : 2;

  return (
    <div data-testid="evidence-summary" className="mt-3 text-xs">
      <div className="font-medium mb-2 text-slate-700">Supporting Evidence ({items.length})</div>
      <div className="space-y-2">
        {items.slice(0, displayCount).map((item, idx) => {
          const isString = typeof item === "string";
          const text = isString ? item : (item?.quote || item?.text || "Evidence item");
          const filename = !isString ? item?.filename : null;
          const pageRef = !isString ? item?.page_reference : null;
          const chunkRef = !isString ? item?.chunk_reference : null;
          const verStatus = !isString ? item?.verification_status : null;

          return (
            <div key={idx} className="border border-slate-100 rounded p-2 text-slate-600">
              {filename && <div className="font-medium mb-1 text-slate-700">{filename}</div>}
              <div>{text}</div>
              {(pageRef || chunkRef || verStatus) && (
                <div className="mt-1 text-slate-400">
                  {pageRef ? `Page: ${pageRef}` : ""}
                  {pageRef && chunkRef ? " \u2022 " : ""}
                  {chunkRef ? `Chunk: ${chunkRef}` : ""}
                  {(pageRef || chunkRef) && verStatus ? " \u2022 " : ""}
                  {verStatus ? `Status: ${verStatus}` : ""}
                </div>
              )}
            </div>
          );
        })}
      </div>
      {items.length > displayCount && (
        <div className="text-slate-400 mt-1">+{items.length - displayCount} more</div>
      )}
    </div>
  );
};

export default EvidenceSummary;
