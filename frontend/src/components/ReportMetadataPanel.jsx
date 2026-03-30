const ReportMetadataPanel = ({ metadata, verificationStatus }) => {
  if (!metadata && !verificationStatus) return null;

  return (
    <div data-testid="report-metadata-panel" className="rounded border border-slate-200 p-3 text-xs mt-3 bg-slate-50">
      <div className="font-semibold mb-1 text-slate-800">Report Metadata</div>
      {metadata?.generated_by_model && <div className="text-slate-600">Model: {metadata.generated_by_model}</div>}
      {typeof metadata?.fallback_used === "boolean" && (
        <div className="text-slate-600">Fallback used: {metadata.fallback_used ? "Yes" : "No"}</div>
      )}
      {typeof metadata?.documents_analyzed === "number" && (
        <div className="text-slate-600">Documents analysed: {metadata.documents_analyzed}</div>
      )}
      {typeof metadata?.timeline_events_analyzed === "number" && (
        <div className="text-slate-600">Timeline events analysed: {metadata.timeline_events_analyzed}</div>
      )}
      {typeof metadata?.grounds_considered === "number" && (
        <div className="text-slate-600">Grounds considered: {metadata.grounds_considered}</div>
      )}
      {typeof metadata?.pipeline_issue_count === "number" && (
        <div className="text-slate-600">Pipeline issues considered: {metadata.pipeline_issue_count}</div>
      )}
      {typeof metadata?.pipeline_verification_count === "number" && (
        <div className="text-slate-600">Verified issues considered: {metadata.pipeline_verification_count}</div>
      )}
      <div className="text-slate-600">Status: {verificationStatus || metadata?.verification_status || "draft"}</div>
      {metadata?.confidence_note && <div className="mt-2 text-slate-500 italic">{metadata.confidence_note}</div>}
    </div>
  );
};

export default ReportMetadataPanel;
