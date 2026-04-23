"""
Unit tests for ground_cleanup.py — the post-realism cleanup layer.
Verifies counsel feedback 23 Feb 2026:
  1. Misclassified sub-particulars are stripped
  2. Strong-record / weak-Crown conviction grounds are uplifted
  3. NSW s 23A / QLD s 304A / CTH fault-elements never described as mitigation
  4. Post-verdict juror language is softened
"""
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from services.ground_normaliser import Ground, SubParticular
from services.ground_cleanup import (
    apply_cleanup,
    remove_misclassified_subs,
    uplift_if_core_metrics_favour_ground,
    fix_liability_vs_mitigation_language,
    soften_timing_sensitive_jury_language,
)


def _make_ground(**overrides) -> Ground:
    base = dict(
        title="Test Ground",
        type="conviction",
        pathway="Criminal Appeal Act 1912 (NSW) s 6(1)",
        viability="requires_development",
        supporting_evidence=[],
        relevant_law_sections=[],
        authorities=[],
    )
    base.update(overrides)
    return Ground(**base)


# ------------------ 1. Misclassified sub-particulars ------------------

def test_conviction_ground_strips_sentencing_sub():
    g = _make_ground(
        type="conviction",
        sub_particulars=[
            SubParticular(label="a", text="Trial judge misdirected the jury on intent."),
            SubParticular(label="c", text="Sentencing Consideration of Drug Use — manifestly excessive."),
        ],
    )
    remove_misclassified_subs(g)
    texts = [sp.text for sp in g.sub_particulars]
    assert any("misdirected" in t for t in texts)
    assert not any("Sentencing Consideration" in t for t in texts)


def test_sentence_ground_strips_appellate_rights_sub():
    g = _make_ground(
        type="sentence",
        sub_particulars=[
            SubParticular(label="a", text="Failure to Preserve Appellate Rights post-sentencing."),
            SubParticular(label="b", text="Non-parole period manifestly excessive."),
        ],
    )
    remove_misclassified_subs(g)
    texts = [sp.text for sp in g.sub_particulars]
    assert not any("Appellate Rights" in t for t in texts)
    assert any("Non-parole" in t for t in texts)


# ------------------ 2. Realism uplift ------------------

def test_uplift_strong_record_weak_robust_weak_crown_conviction():
    g = _make_ground(
        type="conviction",
        viability="requires_development",
        record_support="strong",
        verdict_robustness="weak",
        crown_strength="weak",
    )
    uplift_if_core_metrics_favour_ground(g)
    assert g.viability == "arguable_moderate"


def test_uplift_strong_record_balanced_robust_weak_crown_conviction():
    g = _make_ground(
        type="conviction",
        viability="requires_development",
        record_support="strong",
        verdict_robustness="balanced",
        crown_strength="weak",
    )
    uplift_if_core_metrics_favour_ground(g)
    assert g.viability == "arguable_moderate"


def test_uplift_strong_record_weak_robust_moderate_crown_conviction():
    g = _make_ground(
        type="conviction",
        viability="requires_development",
        record_support="strong",
        verdict_robustness="weak",
        crown_strength="moderate",
    )
    uplift_if_core_metrics_favour_ground(g)
    assert g.viability == "arguable_moderate"


def test_no_uplift_for_sentence_type():
    g = _make_ground(
        type="sentence",
        viability="requires_development",
        record_support="strong",
        verdict_robustness="weak",
        crown_strength="weak",
    )
    uplift_if_core_metrics_favour_ground(g)
    assert g.viability == "requires_development"  # unchanged


def test_no_uplift_if_record_limited():
    g = _make_ground(
        type="conviction",
        viability="requires_development",
        record_support="limited",
        verdict_robustness="weak",
        crown_strength="weak",
    )
    uplift_if_core_metrics_favour_ground(g)
    assert g.viability == "requires_development"  # unchanged


# ------------------ 3. Liability vs mitigation language (NSW s 23A) ------------------

def test_nsw_s23a_mitigation_language_corrected():
    text = (
        "The judge determined that this condition was drug-induced and did not "
        "mitigate the accused's mental culpability under section 23A."
    )
    out = fix_liability_vs_mitigation_language(text, "NSW")
    assert "mitigate" not in out
    assert "partial defence" in out or "liability" in out


def test_nsw_s23a_mitigating_factor_corrected():
    text = "The trial judge treated the impairment as a mitigating factor under section 23A."
    out = fix_liability_vs_mitigation_language(text, "NSW")
    assert "mitigating factor" not in out
    assert "liability" in out or "partial defence" in out


def test_qld_diminished_responsibility_kept_as_liability():
    text = "Evidence treated as mere mitigation under s 304A of the Criminal Code (QLD)."
    out = fix_liability_vs_mitigation_language(text, "QLD")
    assert "mere mitigation" not in out


def test_non_triggering_jurisdiction_unchanged():
    text = "The trial judge considered rehabilitation prospects as a mitigating factor."
    # No liability trigger words → text should pass through untouched.
    out = fix_liability_vs_mitigation_language(text, "NSW")
    assert out == text


# ------------------ 4. Post-verdict juror softening ------------------

def test_post_verdict_juror_softened():
    text = (
        "Reports confirm a juror waved to the victim's family after the verdict — "
        "clear misconduct undermining impartiality."
    )
    out = soften_timing_sensitive_jury_language(text)
    assert "clear misconduct undermining impartiality" not in out
    assert "raising concern" in out


def test_pre_verdict_juror_language_untouched():
    text = "During the trial a juror showed partiality — clear misconduct undermining impartiality."
    out = soften_timing_sensitive_jury_language(text)
    # No "after the verdict" trigger → text must not change.
    assert out == text


# ------------------ 5. End-to-end apply_cleanup ------------------

def test_apply_cleanup_full_pipeline():
    grounds = [
        _make_ground(
            title="Ground 1 — s 23A partial defence",
            type="conviction",
            viability="requires_development",
            record_support="strong",
            verdict_robustness="weak",
            crown_strength="weak",
            trial_finding="The judge determined that this condition was drug-induced and did not mitigate the accused's mental culpability under section 23A.",
            sub_particulars=[
                SubParticular(label="a", text="Trial judge misdirected the jury."),
                SubParticular(label="c", text="Sentencing Consideration of Drug Use."),
            ],
        ),
    ]
    out = apply_cleanup(grounds, "NSW")
    g = out[0]
    # uplift applied
    assert g.viability == "arguable_moderate"
    # misclassified sub stripped
    assert all("Sentencing Consideration" not in sp.text for sp in g.sub_particulars)
    # s 23A language corrected
    assert "mitigate" not in g.trial_finding.lower()
    # trail recorded
    assert g.reasoning_trail
    assert any("uplift" in entry.lower() for entry in g.reasoning_trail)
