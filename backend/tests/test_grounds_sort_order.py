"""
test_grounds_sort_order.py

Unit tests for the canonical grounds_of_merit display sort key exposed by
routers/grounds.py (_grounds_display_sort_key + _ground_strategic_priority).

Locks the behaviour counsel expects on the Grounds tab and in report exports:

  1. User manual reorder (priority_order) always wins.
  2. On fresh grounds (no reorder applied), conviction-safety / mens rea /
     miscarriage-of-justice grounds sort BEFORE procedural / evidentiary /
     sentencing grounds — regardless of title alphabetical order.
  3. A mens rea / miscarriage of justice ground must surface ABOVE a
     generic "Exclusion of Evidential Material" ground when both carry
     identical strength and no manual priority_order. This is the exact
     regression counsel reported on 23 Feb 2026.
  4. Strategic tier-mates are broken by strength, then by title.
"""

from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from routers.grounds import (  # noqa: E402 — path injection required above
    _ground_strategic_priority,
    _grounds_display_sort_key,
)


# ---------------------------------------------------------------------------
# Fixture builder
# ---------------------------------------------------------------------------

def _g(**overrides) -> dict:
    """Build a minimal grounds_of_merit row matching the DB projection shape
    used by get_grounds_of_merit().
    """
    base = {
        "ground_id": "gnd_test",
        "title": "Test Ground",
        "ground_type": "other",
        "strength": "moderate",
        # priority_order intentionally absent so default (999) applies —
        # tests that want a manual reorder opt in explicitly.
    }
    base.update(overrides)
    return base


# ---------------------------------------------------------------------------
# 1. Strategic tier assignment
# ---------------------------------------------------------------------------

def test_conviction_ground_is_tier_0():
    assert _ground_strategic_priority(_g(ground_type="conviction")) == 0


def test_miscarriage_of_justice_is_tier_0():
    assert _ground_strategic_priority(_g(ground_type="miscarriage_of_justice")) == 0


def test_fresh_evidence_is_tier_0():
    assert _ground_strategic_priority(_g(ground_type="fresh_evidence")) == 0


def test_mens_rea_title_forces_tier_0_even_with_other_type():
    # Counsel scenario: LLM returned a conviction-safety ground but stored
    # ground_type is generic "other". Title must still put it tier 0.
    g = _g(title="Unsafe Verdict — Mens Rea Failure", ground_type="other")
    assert _ground_strategic_priority(g) == 0


def test_miscarriage_of_justice_title_forces_tier_0():
    g = _g(
        title="Miscarriage of Justice: Failure to Properly Determine Mental State",
        ground_type="procedural_error",
    )
    assert _ground_strategic_priority(g) == 0


def test_substantial_impairment_title_forces_tier_0():
    g = _g(title="Failure to Engage Substantial Impairment Defence",
           ground_type="sentencing_error")
    assert _ground_strategic_priority(g) == 0


def test_procedure_slug_is_tier_1():
    assert _ground_strategic_priority(_g(ground_type="procedure")) == 1


def test_procedural_error_slug_is_tier_1():
    assert _ground_strategic_priority(_g(ground_type="procedural_error")) == 1


def test_jury_irregularity_is_tier_1():
    assert _ground_strategic_priority(_g(ground_type="jury_irregularity")) == 1


def test_evidence_slug_is_tier_2():
    assert _ground_strategic_priority(_g(ground_type="evidence")) == 2


def test_ineffective_counsel_is_tier_3():
    assert _ground_strategic_priority(_g(ground_type="ineffective_counsel")) == 3


def test_sentence_slug_is_tier_4():
    assert _ground_strategic_priority(_g(ground_type="sentence")) == 4


def test_sentencing_error_slug_is_tier_4():
    assert _ground_strategic_priority(_g(ground_type="sentencing_error")) == 4


def test_other_is_tier_5():
    assert _ground_strategic_priority(_g(ground_type="other")) == 5


def test_unknown_slug_falls_back_to_tier_5():
    assert _ground_strategic_priority(_g(ground_type="not_a_real_slug")) == 5


def test_missing_ground_type_falls_back_to_tier_5():
    g = _g()
    g.pop("ground_type", None)
    g["title"] = "Some Neutral Title"
    assert _ground_strategic_priority(g) == 5


# ---------------------------------------------------------------------------
# 2. Full sort — manual priority_order wins
# ---------------------------------------------------------------------------

def test_manual_priority_order_beats_strategic_priority():
    # A sentencing ground manually reordered to position 0 must stay first,
    # even though a conviction ground is in the list untouched.
    conviction = _g(
        title="Unsafe Verdict: Mens Rea",
        ground_type="conviction",
        strength="strong",
    )
    sentencing_manual_first = _g(
        title="Sentencing Error — Manifestly Excessive",
        ground_type="sentencing_error",
        strength="moderate",
        priority_order=0,
    )
    grounds = [conviction, sentencing_manual_first]
    grounds.sort(key=_grounds_display_sort_key)
    assert grounds[0]["title"] == "Sentencing Error — Manifestly Excessive"
    assert grounds[1]["title"] == "Unsafe Verdict: Mens Rea"


def test_manual_priority_order_preserved_across_multiple_grounds():
    # User dragged the sentencing ground to top and the procedure ground to
    # second. The conviction ground (untouched) falls last. Must honour
    # the user's exact ordering regardless of strategic defaults.
    grounds = [
        _g(title="A — conviction untouched", ground_type="conviction"),
        _g(title="B — procedure reorder #1", ground_type="procedure",
           priority_order=1),
        _g(title="C — sentencing reorder #0", ground_type="sentencing_error",
           priority_order=0),
    ]
    grounds.sort(key=_grounds_display_sort_key)
    assert [g["title"] for g in grounds] == [
        "C — sentencing reorder #0",
        "B — procedure reorder #1",
        "A — conviction untouched",
    ]


# ---------------------------------------------------------------------------
# 3. Fresh grounds no longer sort alphabetically — conviction first
# ---------------------------------------------------------------------------

def test_fresh_grounds_conviction_beats_alphabetical_lead():
    # Both grounds have default priority_order and moderate strength.
    # Pre-fix sort was alphabetical → "Exclusion…" (E) would beat
    # "Miscarriage…" (M). Post-fix must put the mens rea/miscarriage
    # ground first because it is tier 0.
    exclusion = _g(
        title="Exclusion of Evidential Material",
        ground_type="procedural_error",  # LLM enum; tier 1
        strength="moderate",
    )
    mens_rea = _g(
        title="Miscarriage of Justice: Failure to Properly Determine Mental State (Mens Rea)",
        ground_type="miscarriage_of_justice",  # tier 0
        strength="moderate",
    )
    grounds = [exclusion, mens_rea]
    grounds.sort(key=_grounds_display_sort_key)
    assert grounds[0] is mens_rea, (
        "Mens rea / miscarriage of justice ground must sort above "
        "'Exclusion of Evidential Material' on default ordering."
    )


def test_fresh_grounds_conviction_type_beats_alphabetical_lead_when_types_set_by_normaliser():
    # Grounds persisted via the normaliser path carry the 5-value enum
    # ('conviction' / 'procedure' / 'evidence' / 'sentence' /
    # 'ineffective_counsel'). Same test, expressed in normaliser vocabulary.
    exclusion = _g(
        title="Exclusion of Evidential Material",
        ground_type="evidence",        # tier 2
        strength="moderate",
    )
    conviction = _g(
        title="Unsafe Verdict: Mens Rea Misdirection",
        ground_type="conviction",      # tier 0
        strength="moderate",
    )
    grounds = [exclusion, conviction]
    grounds.sort(key=_grounds_display_sort_key)
    assert grounds[0] is conviction


def test_fresh_grounds_full_strategic_ordering():
    grounds = [
        _g(title="Sentencing Error", ground_type="sentencing_error"),        # tier 4
        _g(title="Other Misc Ground", ground_type="other"),                  # tier 5
        _g(title="Ineffective Counsel Advice", ground_type="ineffective_counsel"),  # tier 3
        _g(title="Exclusion of Evidential Material", ground_type="evidence"),# tier 2
        _g(title="Procedural Unfairness",  ground_type="procedural_error"),  # tier 1
        _g(title="Unsafe Verdict — Mens Rea", ground_type="conviction"),     # tier 0
    ]
    grounds.sort(key=_grounds_display_sort_key)
    tiers = [_ground_strategic_priority(g) for g in grounds]
    assert tiers == [0, 1, 2, 3, 4, 5], f"Expected [0,1,2,3,4,5], got {tiers}"


def test_fresh_grounds_not_sorted_alphabetically_within_full_mixed_list():
    # Pre-fix alphabetical order would be:
    #   Aggravating, Evidence, Jury, Mens, Sentencing
    # Post-fix strategic order must place "Mens Rea" first (tier 0), then the
    # procedural/jury grounds (tier 1), then evidence (tier 2), then
    # sentencing (tier 4). The first title must be "Mens Rea…" — NOT
    # "Aggravating…" which would win on alphabetical.
    grounds = [
        _g(title="Aggravating Factor Miscounted", ground_type="sentencing_error"),
        _g(title="Evidence Wrongly Admitted", ground_type="evidence"),
        _g(title="Jury Misconduct Concern", ground_type="jury_irregularity"),
        _g(title="Mens Rea Misdirection on Intent", ground_type="conviction"),
        _g(title="Sentencing Error — Double Counting", ground_type="sentencing_error"),
    ]
    grounds.sort(key=_grounds_display_sort_key)
    assert grounds[0]["title"] == "Mens Rea Misdirection on Intent"
    assert grounds[-1]["ground_type"] in ("sentencing_error",)


# ---------------------------------------------------------------------------
# 4. Same tier → strength, then title
# ---------------------------------------------------------------------------

def test_same_tier_sorted_by_strength_descending():
    # Both tier 1 (procedural). Strong must beat moderate must beat weak.
    grounds = [
        _g(title="A — moderate", ground_type="procedural_error", strength="moderate"),
        _g(title="B — strong", ground_type="procedural_error", strength="strong"),
        _g(title="C — weak", ground_type="procedural_error", strength="weak"),
    ]
    grounds.sort(key=_grounds_display_sort_key)
    assert [g["strength"] for g in grounds] == ["strong", "moderate", "weak"]


def test_same_tier_same_strength_sorted_alphabetically_by_title():
    grounds = [
        _g(title="Zulu first", ground_type="conviction", strength="moderate"),
        _g(title="Alpha first", ground_type="conviction", strength="moderate"),
        _g(title="Mike middle", ground_type="conviction", strength="moderate"),
    ]
    grounds.sort(key=_grounds_display_sort_key)
    assert [g["title"] for g in grounds] == ["Alpha first", "Mike middle", "Zulu first"]


# ---------------------------------------------------------------------------
# 5. Edge cases
# ---------------------------------------------------------------------------

def test_empty_list_sorts_without_error():
    grounds = []
    grounds.sort(key=_grounds_display_sort_key)
    assert grounds == []


def test_single_ground_returns_itself():
    grounds = [_g(title="Solo", ground_type="conviction")]
    grounds.sort(key=_grounds_display_sort_key)
    assert len(grounds) == 1
    assert grounds[0]["title"] == "Solo"


def test_missing_strength_treated_as_unknown():
    # A ground with no strength key must still sort; unknown is the worst
    # strength tier so it falls behind moderate of the same type tier.
    with_strength = _g(title="A — moderate",
                       ground_type="procedural_error", strength="moderate")
    missing_strength = _g(title="B — missing",
                          ground_type="procedural_error")
    missing_strength.pop("strength", None)
    grounds = [missing_strength, with_strength]
    grounds.sort(key=_grounds_display_sort_key)
    assert grounds[0]["title"] == "A — moderate"
    assert grounds[1]["title"] == "B — missing"


def test_empty_title_does_not_crash():
    grounds = [_g(title="", ground_type="conviction"),
               _g(title="Mens Rea", ground_type="conviction")]
    grounds.sort(key=_grounds_display_sort_key)
    # Tier 0 for both (Mens Rea title promotes), strength equal → alphabetical
    # "" sorts first under ascending lexicographic order.
    assert grounds[0]["title"] == ""
