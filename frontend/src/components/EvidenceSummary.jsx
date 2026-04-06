const EvidenceSummary = ({ items = [], expanded = false }) => {
  if (!Array.isArray(items) || items.length === 0) {
    return <div data-testid="evidence-summary-empty" className="text-xs text-slate-400 mt-2">No structured evidence linked yet</div>;
  }

  /* DO NOT UNDO — Extract readable evidence text, filtering out garbage key-concatenated strings */
  const extractText = (item) => {
    if (!item) return null;
    if (typeof item === "string") {
      const quoteMatch = item.match(/['"]quote['"]\s*:\s*['"](.+?)['"]\s*[,}]/);
      if (quoteMatch) return quoteMatch[1];
      if (item.includes("document_id") && item.includes("filename") && item.includes("quote")) return null;
      if (/^[a-z_]+$/.test(item) && item.length < 80) return null;
      if (item.startsWith("{") && item.includes("'optional'")) return null;
      return item;
    }
    if (typeof item === "object") {
      return item.quote || item.text || item.description || item.filename || null;
    }
    return String(item);
  };

  const displayCount = expanded ? 5 : 2;
  const cleaned = items.map((item, idx) => {
    const isString = typeof item === "string";
    const text = isString ? extractText(item) : (item?.quote || item?.text || null);
    if (!text) return null;
    const filename = !isString ? item?.filename : null;
    const pageRef = !isString ? item?.page_reference : null;
    const chunkRef = !isString ? item?.chunk_reference : null;
    const verStatus = !isString ? item?.verification_status : null;
    return { text, filename, pageRef, chunkRef, verStatus, idx };
  }).filter(Boolean);

  if (cleaned.length === 0) {
    return <div data-testid="evidence-summary-empty" className="text-xs text-slate-400 mt-2">No structured evidence linked yet</div>;
  }

  return (
    <div data-testid="evidence-summary" className="mt-3 text-xs">
      <div className="font-medium mb-2 text-slate-700">Supporting Evidence ({cleaned.length})</div>
      <div className="space-y-2">
        {cleaned.slice(0, displayCount).map((ev) => (
          <div key={ev.idx} className="border border-slate-100 rounded p-2 text-slate-600">
            {ev.filename && <div className="font-medium mb-1 text-slate-700">{ev.filename}</div>}
            <div>{ev.text}</div>
            {(ev.pageRef || ev.chunkRef || ev.verStatus) && (
              <div className="mt-1 text-slate-400">
                {ev.pageRef ? `Page: ${ev.pageRef}` : ""}
                {ev.pageRef && ev.chunkRef ? " \u2022 " : ""}
                {ev.chunkRef ? `Chunk: ${ev.chunkRef}` : ""}
                {(ev.pageRef || ev.chunkRef) && ev.verStatus ? " \u2022 " : ""}
                {ev.verStatus ? `Status: ${ev.verStatus}` : ""}
              </div>
            )}
          </div>
        ))}
      </div>
      {cleaned.length > displayCount && (
        <div className="text-slate-400 mt-1">+{cleaned.length - displayCount} more</div>
      )}
    </div>
  );
};

export default EvidenceSummary;
