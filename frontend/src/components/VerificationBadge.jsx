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

const VerificationBadge = ({ status }) => {
  const normalised = String(status || "draft").toLowerCase();
  return (
    <span
      data-testid="verification-badge"
      className={`px-2 py-1 rounded text-xs font-medium border ${CLASSES[normalised] || CLASSES.draft}`}
    >
      {LABELS[normalised] || "Generated"}
    </span>
  );
};

export default VerificationBadge;
