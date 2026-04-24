"""
Tests for counsel feedback round 3 (23 Feb 2026):
  Issue 1: default classification → procedure (not conviction)
  Issue 2: evidence is never standalone → routed to conviction
  Issue 3: federal s 7.3 mental impairment detection
  Issue 4: conviction grounds may reference sentencing as consequence
  Issue 5: merge key includes error_identified to preserve distinct arguments
  Issue 6: auto_repair adds manual-verification warning to reasoning_trail
  Issue 7: proviso_risk computed per Weiss v The Queen
"""

import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from services.ground_normaliser import (
    Ground,
    SubParticular,
    auto_repair_integrity,
    canonical_title,
    classify_text_with_reason,
    classify_text,
    ground_to_dict,
    merge_duplicate_grounds,
    validate_ground_integrity,
)
from services.appeal_strength import (
    CaseEvidenceProfile,
    _assess_proviso_risk,
    apply_realism_adjustments,
    score_grounds_for_realism,
)


# ------------------ Issue 1: default classification ------------------

def test_default_classification_is_procedure_not_conviction():
    gtype, reason = classify_text_with_reason(
        "A general concern about the trial that does not match any specific terms whatsoever.",
        "NSW",
    )
    assert gtype == "procedure", f"expected procedure fallback, got {gtype}"
    assert "defaulted to procedure" in reason.lower()


# ------------------ Issue 2: evidence not standalone ------------------

def test_evidence_terms_route_to_conviction_not_standalone():
    # Use an evidence-flavoured phrase that previously routed to "evidence"
    gtype, reason = classify_text_with_reason(
        "The tendency evidence was wrongly admitted; probative value did not outweigh prejudice.",
        "NSW",
    )
    assert gtype == "conviction", f"expected conviction (Issue 2), got {gtype}"
    assert "conviction" in reason.lower()


def test_evidence_terms_never_return_standalone_evidence_type_from_classifier():
    # A direct probe — feed content that heavily matches evidence_terms.
    gtype = classify_text(
        "Admissibility ruling challenge: evidence was prejudicial beyond probative value.",
        "NSW",
    )
    assert gtype != "evidence"


# ------------------ Issue 3: federal s 7.3 detection ------------------

def test_federal_s_7_3_detected_as_conviction():
    gtype, reason = classify_text_with_reason(
        "The trial judge misapplied section 7.3 of the Criminal Code (Cth) regarding mental impairment.",
        "CTH",
    )
    assert gtype == "conviction"
    assert "partial defence rule" in reason.lower() or "7.3" in reason


def test_criminal_code_s_7_3_phrase_detected():
    gtype, _ = classify_text_with_reason(
        "The trial erred in its treatment of mental impairment under the criminal code.",
        "CTH",
    )
    assert gtype == "conviction"


# ------------------ Issue 4: relaxed sentencing contamination ------------------

def test_conviction_ground_allows_incidental_rehabilitation_reference():
    # Previously this raised. Now it should pass because "rehabilitation" is
    # an incidental consequence reference, not the primary focus.
    g = Ground(
        title="Unsafe verdict on mens rea",
        type="conviction",
        pathway="",
        viability="arguable_strong",
        supporting_evidence=[],
        relevant_law_sections=[],
        authorities=[],
        trial_finding="The jury convicted notwithstanding psychiatric evidence.",
        error_identified="Mens rea was not established beyond reasonable doubt.",
        materiality="The conviction is unsafe.",
        consequence="If allowed, a retrial or acquittal follows, which will affect rehabilitation planning.",
    )
    # Should NOT raise.
    validate_ground_integrity(g)


def test_conviction_ground_still_raises_on_manifestly_excessive_primary_focus():
    g = Ground(
        title="Unsafe verdict",
        type="conviction",
        pathway="",
        viability="arguable_strong",
        supporting_evidence=[],
        relevant_law_sections=[],
        authorities=[],
        trial_finding="The trial judge handed down a sentence that was manifestly excessive.",
    )
    try:
        validate_ground_integrity(g)
        raised = False
    except ValueError:
        raised = True
    assert raised, "Expected validate_ground_integrity to raise on manifestly-excessive primary-focus content"


# ------------------ Issue 5: merge key preserves distinct arguments ------------------

def test_three_distinct_mens_rea_grounds_not_collapsed():
    grounds = [
        Ground(
            title="Unsafe verdict: mens rea", type="conviction", pathway="", viability="arguable_moderate",
            supporting_evidence=[], relevant_law_sections=[], authorities=[],
            error_identified="Psychiatric evidence conflicted; the jury could not have been satisfied on mens rea.",
        ),
        Ground(
            title="Unsafe verdict: mens rea", type="conviction", pathway="", viability="arguable_moderate",
            supporting_evidence=[], relevant_law_sections=[], authorities=[],
            error_identified="Intoxication rebutted specific intent; jury could not have been satisfied on mens rea.",
        ),
        Ground(
            title="Unsafe verdict: mens rea", type="conviction", pathway="", viability="arguable_moderate",
            supporting_evidence=[], relevant_law_sections=[], authorities=[],
            error_identified="The trial judge misdirected the jury on the mens rea element required for murder.",
        ),
    ]
    merged = merge_duplicate_grounds(grounds)
    assert len(merged) == 3, (
        f"expected 3 distinct grounds preserved (psychiatric / intoxication / "
        f"direction error), got {len(merged)}: "
        f"{[g.error_identified[:60] for g in merged]}"
    )


def test_true_duplicate_mens_rea_grounds_still_merge():
    grounds = [
        Ground(
            title="Unsafe verdict: mens rea", type="conviction", pathway="", viability="arguable_moderate",
            supporting_evidence=["a"], relevant_law_sections=[], authorities=[],
            error_identified="Psychiatric evidence conflicted.",
        ),
        Ground(
            title="Unsafe verdict: mens rea", type="conviction", pathway="", viability="arguable_strong",
            supporting_evidence=["b"], relevant_law_sections=[], authorities=[],
            error_identified="Psychiatric evidence conflicted.",
        ),
    ]
    merged = merge_duplicate_grounds(grounds)
    assert len(merged) == 1, "identical error_identified should still collapse"
    # supporting_evidence absorbed
    assert set(merged[0].supporting_evidence) == {"a", "b"}


# ------------------ Issue 6: auto_repair warning ------------------

def test_auto_repair_emits_manual_verification_warning():
    # A conviction ground polluted with "manifestly excessive" (triggers integrity fail)
    g = Ground(
        title="Unsafe verdict on mens rea",
        type="conviction",
        pathway="",
        viability="arguable_strong",
        supporting_evidence=["Psychiatric evidence supports impairment."],
        relevant_law_sections=["s 23A"],
        authorities=[],
        trial_finding="The sentence was manifestly excessive.",  # contaminant
    )
    repaired = auto_repair_integrity(g, "NSW")
    assert any(
        "REQUIRES MANUAL VERIFICATION" in entry
        for r in repaired
        for entry in (r.reasoning_trail or [])
    ), "expected auto-repair to flag manual-verification requirement on the trail"


# ------------------ Issue 7: proviso risk ------------------

def test_proviso_risk_high_on_strong_crown_strong_verdict():
    assert _assess_proviso_risk("conviction", "strong", "strong") == "high"
    assert _assess_proviso_risk("conviction", "strong", "overwhelming") == "high"


def test_proviso_risk_moderate_on_mixed_signals():
    assert _assess_proviso_risk("conviction", "strong", "balanced") == "moderate"
    assert _assess_proviso_risk("conviction", "moderate", "strong") == "moderate"


def test_proviso_risk_low_on_weak_signals():
    assert _assess_proviso_risk("conviction", "weak", "weak") == "low"


def test_proviso_risk_low_for_non_conviction_grounds():
    assert _assess_proviso_risk("sentence", "strong", "overwhelming") == "low"
    assert _assess_proviso_risk("procedure", "strong", "overwhelming") == "low"


def test_proviso_risk_written_to_ground_and_dict():
    g = Ground(
        title="Mens rea misdirection",
        type="conviction",
        pathway="",
        viability="arguable_strong",
        supporting_evidence=[
            "trial transcript",
            "direct eyewitness evidence identifying the accused",
            "DNA matching the accused",
            "confession to police",
        ],
        relevant_law_sections=[],
        authorities=[],
    )
    profile = CaseEvidenceProfile(
        has_trial_transcript=True,
        has_direct_evidence=True,
        has_forensic_evidence=True,
        has_strong_circumstantial_evidence=True,
        confession_or_admission=True,
        post_offence_conduct_supports_guilt=True,
        disputed_intent=False,
    )
    apply_realism_adjustments(g, profile)
    assert g.proviso_risk in {"high", "moderate"}, f"got {g.proviso_risk}"
    d = ground_to_dict(g)
    assert "proviso_risk" in d
    assert d["proviso_risk"] == g.proviso_risk
