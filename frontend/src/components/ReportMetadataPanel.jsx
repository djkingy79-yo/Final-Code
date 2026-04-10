const ReportMetadataPanel = ({ metadata, verificationStatus }) => {
  if (!metadata && !verificationStatus) return null;

  // Normalise status — never show "draft" or "unverified" to the user
  const rawStatus = verificationStatus || metadata?.verification_status || "generated";
  const displayStatus = (rawStatus === "draft" || rawStatus === "unverified") ? "Generated" :
                        rawStatus === "completed" ? "Complete" :
                        rawStatus === "verified" ? "Verified" :
                        rawStatus === "reviewed" ? "Reviewed" :
                        rawStatus.charAt(0).toUpperCase() + rawStatus.slice(1);

  return (
    <div data-testid="report-metadata-panel" className="rounded border border-slate-200 p-3 text-xs mt-3 bg-slate-50">
      <div className="font-semibold mb-1 text-slate-800">Report Metadata</div>
      {metadata?.generated_by_model && <div className="text-slate-600">Model: {metadata.generated_by_model}</div>}
      {typeof metadata?.documents_analysed === "number" && (
        <div className="text-slate-600">Documents analysed: {metadata.documents_analysed}</div>
      )}
      {typeof metadata?.timeline_events_analysed === "number" && (
        <div className="text-slate-600">Timeline events analysed: {metadata.timeline_events_analysed}</div>
      )}
      {typeof metadata?.grounds_considered === "number" && (
        <div className="text-slate-600">Grounds considered: {metadata.grounds_considered}</div>
      )}
      <div className="text-slate-600">Status: {displayStatus}</div>
      {metadata?.confidence_note && <div className="mt-2 text-slate-500 italic">{metadata.confidence_note}</div>}
    </div>
  );
};

export default ReportMetadataPanel;
