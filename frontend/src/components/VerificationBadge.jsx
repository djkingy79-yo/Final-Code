const LABELS = {
  unverified: "Generated",
  draft: "Generated",
  reviewed: "Reviewed",
  verified: "Verified",
  completed: "Complete",
};

const CLASSES = {
  verified: "border-green-600 text-green-700",
  reviewed: "border-blue-600 text-blue-700",
  completed: "border-green-600 text-green-700",
  draft: "border-blue-600 text-blue-700",
  unverified: "border-blue-600 text-blue-700",
};

const DARK_CLASSES = {
  verified: "bg-green-500 text-white border-green-500",
  reviewed: "bg-blue-500 text-white border-blue-500",
  completed: "bg-green-500 text-white border-green-500",
  draft: "text-white border-white/60",
  unverified: "text-white border-white/60",
};

const VerificationBadge = ({ status, onDark = false }) => {
  const normalised = String(status || "draft").toLowerCase();
  const classes = onDark ? DARK_CLASSES : CLASSES;
  return (
    <span
      data-testid="verification-badge"
      className={`px-2 py-1 rounded text-xs font-bold border ${classes[normalised] || classes.draft}`}
      style={onDark ? { backgroundColor: '#00B09E', color: '#ffffff', borderColor: '#00B09E' } : undefined}
    >
      {LABELS[normalised] || "Generated"}
    </span>
  );
};

export default VerificationBadge;
