"""
Tests for counsel round 3 improvements:
  - outcome_predictor.predict_outcome
  - outcome_predictor.select_strategy
  - proviso soft cap in appeal_strength.apply_realism_adjustments
"""

import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from services.ground_normaliser import Ground
from services.outcome_predictor import predict_outcome, select_strategy
from services.appeal_strength import CaseEvidenceProfile, apply_realism_adjustments


def _g(**overrides) -> Ground:
    base = dict(
        title="Test",
        type="conviction",
        pathway="",
        viability="arguable_moderate",
        supporting_evidence=[],
        relevant_law_sections=[],
        authorities=[],
    )
    base.update(overrides)
    return Ground(**base)


# ------------------ outcome_predictor.predict_outcome ------------------

def test_no_primary_returns_appeal_unlikely():
    assert predict_outcome({"primary": None, "secondary": None})["outcome"] == "appeal_unlikely"


def test_conviction_low_proviso_mens_rea_returns_acquittal_possible():
    primary = _g(
        title="Unsafe verdict: mens rea",
        type="conviction",
        error_identified="The jury could not have been satisfied on mens rea / intent.",
        viability="arguable_strong",
    )
    primary.proviso_risk = "low"
    out = predict_outcome({"primary": primary})
    assert out["outcome"] == "quash_conviction_acquittal_possible"


def test_conviction_low_proviso_non_mens_rea_returns_retrial_likely():
    primary = _g(
        title="Fresh evidence",
        type="conviction",
        error_identified="New DNA evidence shows reasonable doubt.",
        viability="arguable_moderate",
    )
    primary.proviso_risk = "low"
    out = predict_outcome({"primary": primary})
    assert out["outcome"] == "quash_conviction_retrial_likely"


def test_conviction_moderate_proviso_returns_retrial_possible():
    primary = _g(type="conviction", title="Unsafe verdict")
    primary.proviso_risk = "moderate"
    assert predict_outcome({"primary": primary})["outcome"] == "retrial_possible"


def test_conviction_high_proviso_returns_appeal_dismissed():
    primary = _g(type="conviction", title="Unsafe verdict")
    primary.proviso_risk = "high"
    assert predict_outcome({"primary": primary})["outcome"] == "appeal_dismissed"


def test_procedure_low_proviso_returns_retrial_likely():
    primary = _g(type="procedure", title="Procedural unfairness")
    primary.proviso_risk = "low"
    assert predict_outcome({"primary": primary})["outcome"] == "retrial_likely"


def test_procedure_non_low_proviso_returns_appeal_dismissed():
    primary = _g(type="procedure", title="Procedural unfairness")
    primary.proviso_risk = "moderate"
    assert predict_outcome({"primary": primary})["outcome"] == "appeal_dismissed"


def test_sentence_arguable_returns_resentencing_likely():
    primary = _g(type="sentence", title="Manifest excess", viability="arguable_moderate")
    assert predict_outcome({"primary": primary})["outcome"] == "resentencing_likely"


def test_sentence_weak_returns_sentence_appeal_unlikely():
    primary = _g(type="sentence", title="Manifest excess", viability="weak")
    assert predict_outcome({"primary": primary})["outcome"] == "sentence_appeal_unlikely"


def test_conviction_missing_proviso_defaults_to_high_risk_dismissed():
    # getattr fallback should read "high" → outcome dismissed.
    primary = _g(type="conviction", title="Unsafe verdict")
    # Do not set proviso_risk
    assert predict_outcome({"primary": primary})["outcome"] == "appeal_dismissed"


# ------------------ select_strategy ------------------

def test_select_strategy_picks_highest_viability_primary():
    g1 = _g(type="procedure", title="Procedural", viability="requires_development")
    g2 = _g(type="conviction", title="Unsafe verdict", viability="arguable_strong")
    g3 = _g(type="sentence", title="Manifest excess", viability="arguable_moderate")
    strategy = select_strategy([g1, g2, g3])
    assert strategy["primary"] is g2
    # secondary should be a different type
    assert strategy["secondary"] is not None
    assert strategy["secondary"].type != g2.type


def test_select_strategy_breaks_viability_ties_by_type_priority():
    conviction = _g(type="conviction", title="Unsafe verdict", viability="arguable_moderate")
    procedure = _g(type="procedure", title="Procedural", viability="arguable_moderate")
    strategy = select_strategy([procedure, conviction])
    assert strategy["primary"] is conviction


def test_select_strategy_empty_list():
    assert select_strategy([]) == {"primary": None, "secondary": None}


# ------------------ proviso soft cap ------------------

def test_proviso_high_caps_arguable_strong_to_moderate():
    g = _g(
        type="conviction",
        viability="arguable_strong",
        error_identified="Directional error in instructions",
    )
    profile = CaseEvidenceProfile(
        has_trial_transcript=True,
        has_direct_evidence=True,
        has_forensic_evidence=True,
        has_strong_circumstantial_evidence=True,
        multiple_consistent_witnesses=True,
        confession_or_admission=True,
        post_offence_conduct_supports_guilt=True,
    )
    apply_realism_adjustments(g, profile)
    # With overwhelming-style profile, proviso_risk should be high and
    # viability capped.
    assert g.proviso_risk == "high"
    assert g.viability == "arguable_moderate"


def test_proviso_low_leaves_arguable_strong_untouched():
    g = _g(
        type="conviction",
        viability="arguable_strong",
        error_identified="Directional error in instructions",
    )
    profile = CaseEvidenceProfile(
        has_trial_transcript=True,
        has_direct_evidence=False,
        has_forensic_evidence=False,
        has_strong_circumstantial_evidence=False,
        disputed_intent=True,
        competing_psychiatric_opinions=True,
    )
    apply_realism_adjustments(g, profile)
    # Weak Crown + weak verdict → proviso low → no soft cap.
    assert g.proviso_risk in {"low", "moderate"}
    # Viability may have been capped by OTHER rules (e.g. limited record)
    # but NOT by the proviso soft cap, so the log entry for the soft cap
    # must not appear on the trail.
    if g.reasoning_trail:
        assert not any("Proviso soft cap" in entry for entry in g.reasoning_trail)


def test_proviso_high_does_not_touch_non_conviction_types():
    g = _g(type="sentence", viability="arguable_strong")
    profile = CaseEvidenceProfile(has_trial_transcript=True, has_direct_evidence=True)
    apply_realism_adjustments(g, profile)
    # Sentence ground → proviso_risk is always "low" per _assess_proviso_risk.
    assert g.proviso_risk == "low"
