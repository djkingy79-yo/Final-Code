const LABELS = {
  unverified: "Unverified",
  draft: "Draft",
  reviewed: "Reviewed",
  verified: "Verified",
};

const CLASSES = {
  verified: "border-green-600 text-green-700",
  reviewed: "border-blue-600 text-blue-700",
  draft: "border-yellow-600 text-yellow-700",
  unverified: "border-red-600 text-red-700",
};

const VerificationBadge = ({ status }) => {
  const normalised = String(status || "unverified").toLowerCase();
  return (
    <span
      data-testid="verification-badge"
      className={`px-2 py-1 rounded text-xs font-medium border ${CLASSES[normalised] || CLASSES.unverified}`}
    >
      {LABELS[normalised] || "Unverified"}
    </span>
  );
};

export default VerificationBadge;
