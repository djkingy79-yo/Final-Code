"""
outcome_predictor.py

Predicts likely appellate outcome based on:
- Barrister Mode strategy (primary + secondary ground selection)
- Proviso risk (Weiss v The Queen (2005) 224 CLR 300)
- Ground type (conviction / sentence / procedure)

Output is a machine-readable outcome category + one-sentence reason that
the report-rendering layer surfaces on the cover page and in the
Barrister Brief so counsel and client see an aligned projection.

Counsel feedback 23 Feb 2026 — exact logic supplied by counsel.
"""

from __future__ import annotations


def predict_outcome(strategy: dict) -> dict:
    primary = strategy.get("primary")
    secondary = strategy.get("secondary")  # noqa: F841 — reserved for future tiering

    if not primary:
        return {
            "outcome": "appeal_unlikely",
            "reason": "No viable primary ground identified."
        }

    p_type = primary.type
    p_proviso = getattr(primary, "proviso_risk", "high")

    # --- CONVICTION APPEALS ---
    if p_type == "conviction":

        if p_proviso == "low":
            # strong conviction challenge
            if "mens rea" in (primary.title or "").lower() or "intent" in (primary.error_identified or "").lower():
                return {
                    "outcome": "quash_conviction_acquittal_possible",
                    "reason": "Core element of offence (intent) in doubt; proviso unlikely to apply."
                }

            return {
                "outcome": "quash_conviction_retrial_likely",
                "reason": "Conviction unsafe but factual issues remain; retrial likely."
            }

        if p_proviso == "moderate":
            return {
                "outcome": "retrial_possible",
                "reason": "Error identified but may be cured; outcome depends on appellate evaluation."
            }

        return {
            "outcome": "appeal_dismissed",
            "reason": "Proviso likely to apply — conviction considered inevitable."
        }

    # --- PROCEDURAL APPEALS ---
    if p_type == "procedure":

        if p_proviso == "low":
            return {
                "outcome": "retrial_likely",
                "reason": "Procedural unfairness affecting trial integrity."
            }

        return {
            "outcome": "appeal_dismissed",
            "reason": "Procedural issue unlikely to have affected outcome."
        }

    # --- SENTENCE APPEALS ---
    if p_type == "sentence":

        if primary.viability in ("arguable_strong", "arguable_moderate"):
            return {
                "outcome": "resentencing_likely",
                "reason": "Sentencing error within appellate intervention range."
            }

        return {
            "outcome": "sentence_appeal_unlikely",
            "reason": "Sentence within discretionary range."
        }

    return {
        "outcome": "uncertain",
        "reason": "Unable to determine outcome from available grounds."
    }


# --- Helpers -----------------------------------------------------------

# Strategy-ranking scale matching services/ground_normaliser.py VIABILITY_SCALE.
_VIABILITY_RANK = {
    "weak": 0,
    "requires_development": 1,
    "arguable_moderate": 2,
    "arguable_strong": 3,
}

# Ground-type priority for picking a PRIMARY when viability ties.
# Conviction > Procedure > Sentence > other — conviction is the most
# consequential outcome, so a conviction challenge of equal viability
# outranks a procedural or sentencing one.
_TYPE_PRIORITY = {
    "conviction": 3,
    "procedure": 2,
    "sentence": 1,
    "ineffective_counsel": 1,
    "evidence": 0,
    None: -1,
}


def select_strategy(grounds: list) -> dict:
    """
    Pick primary + secondary grounds from the cleaned/scored list.
    Primary = highest viability × ground-type priority.
    Secondary = next-best of a different type if one exists.
    Returns a dict {"primary": Ground|None, "secondary": Ground|None}
    suitable for feeding into predict_outcome().
    """
    if not grounds:
        return {"primary": None, "secondary": None}

    def _rank(g) -> tuple[int, int]:
        return (
            _VIABILITY_RANK.get(getattr(g, "viability", "weak"), 0),
            _TYPE_PRIORITY.get(getattr(g, "type", None), -1),
        )

    sorted_grounds = sorted(grounds, key=_rank, reverse=True)
    primary = sorted_grounds[0] if sorted_grounds else None
    secondary = None
    if primary is not None and len(sorted_grounds) > 1:
        for g in sorted_grounds[1:]:
            if getattr(g, "type", None) != getattr(primary, "type", None):
                secondary = g
                break
    return {"primary": primary, "secondary": secondary}
