"""
barrister_mode.py

Counsel-style strategy ranker. Takes the cleaned/scored grounds list and
slots each into one of four buckets:
  primary    — the strongest single ground (highest viability × type priority)
  secondary  — the next-best ground of a DIFFERENT type
  tertiary   — the third-best ground (any type other than primary/secondary)
  abandon    — grounds with viability == "weak" or "requires_development"
                (counsel should not file these unless evidence is built)

Counsel feedback 23 Feb 2026 — wire into report_generator.py so the LLM
prompts are built from the strategised, ranked grounds rather than the
raw database list.
"""

from __future__ import annotations

from services.ground_normaliser import Ground


# Mirrors VIABILITY_SCALE in services/ground_normaliser.py.
_VIABILITY_RANK = {
    "weak": 0,
    "requires_development": 1,
    "arguable_moderate": 2,
    "arguable_strong": 3,
}

# Conviction > Procedure > Sentence > other. A conviction challenge of
# equal viability outranks a procedural or sentencing one.
_TYPE_PRIORITY = {
    "conviction": 3,
    "procedure": 2,
    "sentence": 1,
    "ineffective_counsel": 1,
    "evidence": 0,
    None: -1,
}


def _rank(g: Ground) -> tuple[int, int]:
    return (
        _VIABILITY_RANK.get(getattr(g, "viability", "weak"), 0),
        _TYPE_PRIORITY.get(getattr(g, "type", None), -1),
    )


def build_strategy_summary(grounds: list[Ground]) -> dict:
    """
    Pick primary / secondary / tertiary, and route the rest to abandon if
    their viability is weak or requires_development.
    """
    if not grounds:
        return {"primary": None, "secondary": None, "tertiary": None, "abandon": []}

    sorted_grounds = sorted(grounds, key=_rank, reverse=True)
    primary = sorted_grounds[0]

    secondary = None
    secondary_idx = None
    for i, g in enumerate(sorted_grounds[1:], start=1):
        if g.type != primary.type:
            secondary = g
            secondary_idx = i
            break

    tertiary = None
    for i, g in enumerate(sorted_grounds[1:], start=1):
        if i == secondary_idx:
            continue
        if g is primary or g is secondary:
            continue
        if secondary is not None and g.type in {primary.type, secondary.type}:
            # If we already have two distinct types, prefer to keep tertiary
            # different too — but allow same-type if it's the only option.
            continue
        tertiary = g
        break
    if tertiary is None:
        # Fall back: pick the next-best whatever type, excluding primary/secondary
        for g in sorted_grounds[1:]:
            if g is primary or g is secondary:
                continue
            tertiary = g
            break

    selected_ids = {id(g) for g in (primary, secondary, tertiary) if g is not None}
    abandon = [
        g for g in sorted_grounds
        if id(g) not in selected_ids
        and getattr(g, "viability", None) in {"weak", "requires_development"}
    ]

    return {
        "primary": primary,
        "secondary": secondary,
        "tertiary": tertiary,
        "abandon": abandon,
    }
