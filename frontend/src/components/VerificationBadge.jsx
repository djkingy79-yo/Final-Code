const LABELS = {
  unverified: "Unverified",
  draft: "Draft",
  reviewed: "Reviewed",
  verified: "Verified",
};

const VerificationBadge = ({ status }) => {
  const normalised = String(status || "unverified").toLowerCase();
  return (
    <span
      data-testid="verification-badge"
      className="px-2 py-1 rounded text-xs border border-slate-300 text-slate-600"
    >
      {LABELS[normalised] || "Unverified"}
    </span>
  );
};

export default VerificationBadge;
