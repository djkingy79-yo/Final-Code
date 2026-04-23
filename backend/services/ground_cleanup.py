"""
ground_cleanup.py

Jurisdiction-aware cleanup layer applied after:
  1. ground normalisation
  2. realism scoring

Purpose:
  - remove mixed-category remnants from sub-particulars
  - apply final viability uplift where the scoring profile supports it
  - fix liability / mitigation terminology in narrative text
    so liability concepts (s 23A NSW, s 304A QLD, mental impairment, etc.)
    are never misdescribed as sentencing mitigation.

Per counsel feedback 23 Feb 2026 — jurisdiction-aware across all states,
territories and Commonwealth matters.
"""

from __future__ import annotations

from typing import Iterable

from services.ground_normaliser import Ground, SubParticular, normalise


LIABILITY_TERMS = (
    "mens rea",
    "intent",
    "intention",
    "unsafe verdict",
    "unreasonable verdict",
    "substantial impairment",
    "diminished responsibility",
    "mental impairment defence",
    "defence of mental impairment",
    "mental impairment",
    "unsoundness of mind",
    "abnormality of mind",
    "partial defence",
)

SENTENCE_TERMS = (
    "sentencing",
    "sentence",
    "rehabilitation",
    "non-parole",
    "parole",
    "manifestly excessive",
    "manifest excess",
    "mitigation",
    "moral culpability",
    "totality",
)

PROCEDURE_TERMS = (
    "jury",
    "juror",
    "judge-alone",
    "judge alone",
    "mode of trial",
    "pretrial publicity",
    "pre-trial publicity",
    "bias",
    "procedural unfairness",
)

INEFFECTIVE_COUNSEL_TERMS = (
    "ineffective counsel",
    "ineffective assistance",
    "failed to preserve",
    "failed to argue",
    "failure to preserve appellate rights",
    "appellate rights",
    "post-sentencing advice",
    "counsel failed",
)

# Jurisdiction-specific liability concepts that must never be described
# as mere sentencing mitigation.
PARTIAL_DEFENCE_MAP: dict[str, tuple[str, ...]] = {
    "NSW": (
        "s 23a",
        "section 23a",
        "substantial impairment",
        "abnormality of mind",
    ),
    "QLD": (
        "diminished responsibility",
        "section 304a",
        "s 304a",
        "unsoundness of mind",
    ),
    "VIC": (
        "defence of mental impairment",
        "mental impairment",
    ),
    "WA": (
        "unsoundness of mind",
    ),
    "SA": (
        "mental incompetence",
        "mental impairment",
    ),
    "TAS": (
        "insanity",
    ),
    "NT": (
        "mental impairment",
        "criminal responsibility",
    ),
    "ACT": (
        "mental impairment",
    ),
    "CTH": (
        "fault elements",
        "mental impairment",
        "unsoundness of mind",
    ),
}


def _contains_any(text: str, needles: Iterable[str]) -> bool:
    t = normalise(text)
    return any(n in t for n in needles)


def _log(ground: Ground, msg: str) -> None:
    if ground.reasoning_trail is None:
        ground.reasoning_trail = []
    ground.reasoning_trail.append(msg)


def remove_misclassified_subs(ground: Ground) -> Ground:
    """
    Strip sub-particulars that plainly belong to a different pathway.
    Runs regardless of jurisdiction — purely content-based triage.
    """
    if not ground.sub_particulars:
        return ground

    cleaned: list[SubParticular] = []
    dropped: list[str] = []

    for sp in ground.sub_particulars:
        t = normalise(sp.text)
        drop = False

        if ground.type == "conviction":
            if _contains_any(t, SENTENCE_TERMS) or _contains_any(t, INEFFECTIVE_COUNSEL_TERMS):
                drop = True

        elif ground.type == "sentence":
            if _contains_any(t, LIABILITY_TERMS) or _contains_any(t, INEFFECTIVE_COUNSEL_TERMS):
                drop = True

        elif ground.type == "procedure":
            # allow jury / judge-alone; reject sentencing / liability contamination
            if _contains_any(t, SENTENCE_TERMS) or (
                _contains_any(t, LIABILITY_TERMS)
                and not _contains_any(t, PROCEDURE_TERMS)
            ):
                drop = True

        elif ground.type == "ineffective_counsel":
            if (
                _contains_any(t, SENTENCE_TERMS)
                and not _contains_any(t, INEFFECTIVE_COUNSEL_TERMS)
            ):
                drop = True
            if (
                _contains_any(t, LIABILITY_TERMS)
                and not _contains_any(t, INEFFECTIVE_COUNSEL_TERMS)
            ):
                drop = True

        elif ground.type == "evidence":
            if _contains_any(t, SENTENCE_TERMS) or _contains_any(t, INEFFECTIVE_COUNSEL_TERMS):
                drop = True

        if drop:
            dropped.append(f"({sp.label}) {sp.text[:80]}" if sp.label else sp.text[:80])
        else:
            cleaned.append(sp)

    ground.sub_particulars = cleaned
    if dropped:
        _log(
            ground,
            f"Cleanup: removed {len(dropped)} misclassified sub-particular(s) "
            f"not matching ground type '{ground.type}'.",
        )
    return ground


def uplift_if_core_metrics_favour_ground(ground: Ground) -> Ground:
    """
    Prevent over-downgrading where realism metrics strongly favour the ground.

    If a conviction ground has strong record support, a verdict that is weak
    or balanced on the record, and the Crown response is weak (or moderate
    when robustness is weak), the viability should not sit at the bottom of
    the scale just because one sub-factor trigged an earlier cap.
    """
    record_support = getattr(ground, "record_support", None)
    verdict_robustness = getattr(ground, "verdict_robustness", None)
    crown_strength = getattr(ground, "crown_strength", None)

    if ground.type != "conviction":
        return ground

    uplifted = False

    if (
        record_support == "strong"
        and verdict_robustness in {"weak", "balanced"}
        and crown_strength == "weak"
        and ground.viability == "requires_development"
    ):
        ground.viability = "arguable_moderate"
        uplifted = True

    elif (
        record_support == "strong"
        and verdict_robustness == "weak"
        and crown_strength == "moderate"
        and ground.viability == "requires_development"
    ):
        ground.viability = "arguable_moderate"
        uplifted = True

    if uplifted:
        _log(
            ground,
            "Cleanup uplift: strong record support + weak/balanced verdict "
            f"robustness + {crown_strength} Crown response → viability "
            "'requires_development' → 'arguable_moderate'.",
        )

    return ground


def soften_timing_sensitive_jury_language(text: str) -> str:
    """
    Avoid overstatement where alleged juror conduct occurred after verdict.
    Post-verdict juror behaviour may raise an appearance concern but does
    not by itself establish deliberative bias.
    """
    if not text:
        return text

    t = normalise(text)
    if "after the verdict" not in t:
        return text

    out = text
    out = out.replace(
        "clear misconduct undermining impartiality",
        "conduct raising concern but requiring proof of material effect on trial fairness",
    )
    out = out.replace(
        "showing partiality",
        "raising an appearance issue requiring closer examination",
    )
    out = out.replace(
        "undermining impartiality",
        "requiring proof of material impact on deliberative impartiality",
    )
    return out


def fix_liability_vs_mitigation_language(text: str, jurisdiction: str) -> str:
    """
    Replace misleading mitigation language where the concept is actually
    liability / partial defence / mental impairment / fault elements.
    Jurisdiction-aware — triggers only when the text references a concept
    from PARTIAL_DEFENCE_MAP for the case's jurisdiction.
    """
    if not text:
        return text

    code = (jurisdiction or "").upper().strip()
    if code == "FEDERAL":
        code = "CTH"

    triggers = PARTIAL_DEFENCE_MAP.get(code, ())
    if not triggers or not _contains_any(text, triggers):
        return text

    replacements = {
        "mitigated culpability": "affected criminal responsibility",
        "mitigate culpability": "affect criminal responsibility",
        "did not mitigate culpability": "did not engage the asserted liability issue",
        "did not mitigate the accused's mental culpability": "did not engage the asserted liability issue",
        "did not mitigate the offender's mental culpability": "did not engage the asserted liability issue",
        "treated as mitigation": "treated as a liability issue",
        "mitigating factor": "liability issue",
        "mitigation factor": "liability issue",
        "mitigation under": "liability question under",
        "not mitigating": "not sufficient to engage the asserted defence or liability issue",
    }

    out = text
    for old, new in replacements.items():
        out = out.replace(old, new)

    # NSW-specific phrasing
    if code == "NSW":
        out = out.replace(
            "under section 23A of the Crimes Act 1900 (NSW), which addresses substantial impairment by abnormality of mind",
            "under section 23A of the Crimes Act 1900 (NSW), which provides a partial defence of substantial impairment by abnormality of mind",
        )
        out = out.replace(
            "did not mitigate the accused's mental culpability under section 23A",
            "did not engage the asserted partial defence under section 23A",
        )
        out = out.replace(
            "did not mitigate the offender's mental culpability under section 23A",
            "did not engage the asserted partial defence under section 23A",
        )

    # QLD-specific phrasing
    if code == "QLD":
        out = out.replace(
            "treated as mere mitigation",
            "treated as a question of diminished responsibility or criminal responsibility",
        )

    return out


def clean_ground_narrative_language(ground: Ground, jurisdiction: str) -> Ground:
    """
    Apply softening + terminology fixes to every narrative section.
    """
    original_trail_len = len(ground.reasoning_trail or [])

    def _clean(s):
        if not s:
            return s
        return fix_liability_vs_mitigation_language(
            soften_timing_sensitive_jury_language(s),
            jurisdiction,
        )

    before_tf = ground.trial_finding
    before_ei = ground.error_identified
    before_mat = ground.materiality
    before_con = ground.consequence

    ground.trial_finding = _clean(ground.trial_finding)
    ground.error_identified = _clean(ground.error_identified)
    ground.materiality = _clean(ground.materiality)
    ground.consequence = _clean(ground.consequence)

    ground.supporting_evidence = [_clean(item) for item in (ground.supporting_evidence or [])]

    if (
        before_tf != ground.trial_finding
        or before_ei != ground.error_identified
        or before_mat != ground.materiality
        or before_con != ground.consequence
    ):
        _log(
            ground,
            f"Cleanup narrative: liability / post-verdict language corrected "
            f"for jurisdiction {jurisdiction or 'unspecified'}.",
        )

    # Suppress empty growth of the trail if nothing changed.
    if ground.reasoning_trail and len(ground.reasoning_trail) == original_trail_len:
        pass

    return ground


def apply_cleanup(grounds: list[Ground], jurisdiction: str) -> list[Ground]:
    """
    Final cleanup pass — run AFTER realism scoring (appeal_strength).
    Order matters: scrub contaminated sub-particulars first, then uplift if
    the realism profile supports it, then clean the narrative language.
    """
    cleaned: list[Ground] = []
    for ground in grounds:
        ground = remove_misclassified_subs(ground)
        ground = uplift_if_core_metrics_favour_ground(ground)
        ground = clean_ground_narrative_language(ground, jurisdiction)
        cleaned.append(ground)
    return cleaned
