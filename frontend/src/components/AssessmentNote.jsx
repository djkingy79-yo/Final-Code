const AssessmentNote = ({ note, className = "" }) => {
  const text = note || "These comparisons are descriptive and do not determine legal merit or likely appeal outcome.";
  return (
    <div
      data-testid="assessment-note"
      className={`rounded border border-slate-200 p-3 text-xs text-slate-500 leading-relaxed ${className}`}
    >
      {text}
    </div>
  );
};

export default AssessmentNote;
