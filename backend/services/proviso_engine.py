"""
proviso_engine.py

Narrative reasoning layer that interprets the proviso_risk computed by
services/appeal_strength.py against Weiss v The Queen (2005) 224 CLR 300.

Reads the already-set ground.proviso_risk (high/moderate/low) and:
  - appends a plain-language reasoning_trail entry explaining the exposure
  - emits a case-level proviso summary the report renderer can include on
    the cover page so counsel and client see a forensic explanation rather
    than a bare colour-coded pill.

Counsel feedback 23 Feb 2026 — bottom-line: wire the new legal engines
into the report generator so they DRIVE the prompt, not sit alongside it.
"""

from __future__ import annotations

from services.ground_normaliser import Ground


_HIGH_REASON = (
    "Conviction ground exposed to Weiss v The Queen (2005) 224 CLR 300 — "
    "a strong Crown case combined with strong/overwhelming verdict robustness "
    "means the appellate court may dismiss the appeal under the proviso even "
    "if error is established. The argument must address why no substantial "
    "miscarriage occurred is not made out on the record."
)

_MODERATE_REASON = (
    "Conviction ground carries moderate proviso exposure under Weiss v The Queen "
    "(2005) 224 CLR 300. Either the Crown case or verdict robustness is strong, "
    "but the other signal is weaker. The proviso is a real factor to address but "
    "is not decisive — counsel should still confront the question of whether the "
    "verdict was inevitable on the record."
)

_LOW_REASON = (
    "Conviction ground carries low proviso exposure under Weiss v The Queen "
    "(2005) 224 CLR 300. Crown case and verdict robustness are weak, so the "
    "proviso is unlikely to save the conviction if error is established."
)


def _append_trail(ground: Ground, entry: str) -> None:
    if ground.reasoning_trail is None:
        ground.reasoning_trail = []
    ground.reasoning_trail.append(entry)


def apply_proviso_engine(grounds: list[Ground]) -> list[Ground]:
    """
    Add narrative proviso reasoning to each conviction ground's
    reasoning_trail. Sentence / procedure / other ground types are passed
    through untouched (proviso is meaningful only at conviction stage).
    """
    for g in grounds:
        if g.type != "conviction":
            continue
        risk = getattr(g, "proviso_risk", None)
        if risk == "high":
            _append_trail(g, _HIGH_REASON)
        elif risk == "moderate":
            _append_trail(g, _MODERATE_REASON)
        elif risk == "low":
            _append_trail(g, _LOW_REASON)
    return grounds


def case_proviso_summary(grounds: list[Ground]) -> dict:
    """
    Aggregate proviso exposure across all conviction grounds for the case
    cover page. Returns the worst-case risk plus a short explanation.
    """
    convictions = [g for g in grounds if g.type == "conviction"]
    if not convictions:
        return {"risk": "n/a", "summary": "No conviction grounds; proviso analysis not applicable."}
    risks = {getattr(g, "proviso_risk", None) for g in convictions}
    if "high" in risks:
        return {"risk": "high", "summary": _HIGH_REASON}
    if "moderate" in risks:
        return {"risk": "moderate", "summary": _MODERATE_REASON}
    if "low" in risks:
        return {"risk": "low", "summary": _LOW_REASON}
    return {"risk": "unknown", "summary": "Proviso risk not computed."}
