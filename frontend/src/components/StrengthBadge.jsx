const STRENGTH_CLASSES = {
  strong: "bg-green-600 text-white",
  moderate: "bg-yellow-500 text-white",
  weak: "bg-red-600 text-white",
};

const StrengthBadge = ({ rating }) => {
  const normalised = String(rating || "moderate").toLowerCase();
  return (
    <span
      data-testid="strength-badge"
      className={`px-2 py-1 rounded text-xs font-semibold ${STRENGTH_CLASSES[normalised] || STRENGTH_CLASSES.moderate}`}
    >
      {normalised.toUpperCase()}
    </span>
  );
};

export default StrengthBadge;
