"""
Unit + list-level tests for the counsel feedback patch (23 Feb 2026 round 2):
  1. enforce_type_title_consistency
  2. downgrade_speculative_procedure
  3. merge_procedural_grounds
  4. collapse_duplicate_psychiatric_grounds
  5. apply_authority_preferences (procedure + sentence)
"""

import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from services.ground_normaliser import Ground, SubParticular
from services.ground_cleanup import (
    apply_cleanup,
    apply_authority_preferences,
    collapse_duplicate_psychiatric_grounds,
    downgrade_speculative_procedure,
    enforce_type_title_consistency,
    merge_procedural_grounds,
)


def _g(**overrides) -> Ground:
    base = dict(
        title="Test Ground",
        type="conviction",
        pathway="",
        viability="arguable_moderate",
        supporting_evidence=[],
        relevant_law_sections=[],
        authorities=[],
        sub_particulars=[],
    )
    base.update(overrides)
    return Ground(**base)


# ------------------ 1. enforce_type_title_consistency ------------------

def test_title_sentencing_sets_type_sentence():
    g = _g(title="Manifestly excessive head sentence", type="conviction")
    enforce_type_title_consistency(g)
    assert g.type == "sentence"


def test_title_mens_rea_overrides_sentence_type():
    # Ground 4 scenario — title says Sentencing Error but content is liability
    g = _g(title="Sentencing Error: Failure to Consider Substantial Impairment", type="sentence")
    enforce_type_title_consistency(g)
    assert g.type == "conviction"


def test_title_mental_impairment_forces_conviction():
    g = _g(title="Mental impairment defence mishandled", type="sentence")
    enforce_type_title_consistency(g)
    assert g.type == "conviction"


def test_title_no_triggers_leaves_type_alone():
    g = _g(title="Fresh Evidence of Alibi Witness", type="conviction")
    enforce_type_title_consistency(g)
    assert g.type == "conviction"


# ------------------ 2. downgrade_speculative_procedure ------------------

def test_procedure_with_implication_capped_at_requires_development():
    g = _g(
        type="procedure",
        viability="arguable_strong",
        materiality="There is an implication that the jury was permitted to separate.",
    )
    downgrade_speculative_procedure(g)
    assert g.viability == "requires_development"


def test_procedure_with_no_direct_evidence_capped():
    g = _g(
        type="procedure",
        viability="arguable_moderate",
        error_identified="The jury may have been biased but there is no direct evidence on the record.",
    )
    downgrade_speculative_procedure(g)
    assert g.viability == "requires_development"


def test_procedure_with_affidavit_evidence_not_capped():
    g = _g(
        type="procedure",
        viability="arguable_strong",
        materiality="Affidavit of juror X sworn 12 March demonstrates conduct affecting deliberation.",
    )
    downgrade_speculative_procedure(g)
    assert g.viability == "arguable_strong"


def test_non_procedure_ground_unaffected_by_speculation_check():
    g = _g(
        type="conviction",
        viability="arguable_strong",
        materiality="There is an implication that...",
    )
    downgrade_speculative_procedure(g)
    assert g.viability == "arguable_strong"


# ------------------ 3. merge_procedural_grounds ------------------

def test_two_procedural_grounds_collapse_to_one():
    grounds = [
        _g(title="Judge-alone refusal", type="procedure",
           sub_particulars=[SubParticular(label="a", text="Application refused without reasons")],
           supporting_evidence=["Transcript p 23"]),
        _g(title="Prejudicial material", type="procedure",
           sub_particulars=[SubParticular(label="a", text="Tendency evidence wrongly admitted")],
           supporting_evidence=["Ruling p 45"]),
        _g(title="Unrelated conviction ground", type="conviction"),
    ]
    out = merge_procedural_grounds(grounds)
    procs = [g for g in out if g.type == "procedure"]
    assert len(procs) == 1
    # Base kept its own sub + absorbed the other's
    assert len(procs[0].sub_particulars) == 2
    assert any("refused" in sp.text for sp in procs[0].sub_particulars)
    assert any("Tendency" in sp.text for sp in procs[0].sub_particulars)
    # Conviction ground untouched
    assert any(g.type == "conviction" for g in out)


def test_single_procedural_ground_untouched():
    grounds = [
        _g(title="Judge-alone refusal", type="procedure"),
        _g(title="Ground 2", type="conviction"),
    ]
    out = merge_procedural_grounds(grounds)
    assert len(out) == 2


# ------------------ 4. collapse_duplicate_psychiatric_grounds ------------------

def test_duplicate_psychiatric_grounds_collapsed():
    grounds = [
        _g(
            title="Miscarriage of Justice — Mens rea / psychiatric evidence",
            type="conviction",
            sub_particulars=[SubParticular(label="a", text="Psychosis mishandled")],
            error_identified="Substantial impairment was mishandled at trial.",
        ),
        _g(
            title="Sentencing Error — Failure to Consider Substantial Impairment",
            type="conviction",  # post-type-enforcement would flip this
            sub_particulars=[SubParticular(label="a", text="Unique mental-state sub")],
            error_identified="Partial defence under s 23A inadequately considered.",
        ),
        _g(title="Jury integrity concern", type="procedure"),
    ]
    out = collapse_duplicate_psychiatric_grounds(grounds)
    psychiatric = [
        g for g in out
        if any(tok in (g.title + " " + (g.error_identified or "")).lower()
               for tok in ("mens rea", "substantial impairment", "psychiatric"))
    ]
    assert len(psychiatric) == 1
    # Survivor absorbed the duplicate's unique sub
    survivor = psychiatric[0]
    assert any("Unique mental-state sub" in sp.text for sp in survivor.sub_particulars)
    # Reasoning trail records the merge
    assert survivor.reasoning_trail
    assert any("merged duplicate psychiatric" in entry.lower() for entry in survivor.reasoning_trail)
    # Procedural ground still there
    assert any(g.type == "procedure" for g in out)


def test_single_psychiatric_ground_left_alone():
    grounds = [
        _g(title="Substantial impairment issue", type="conviction"),
        _g(title="Sentence too long", type="sentence"),
    ]
    out = collapse_duplicate_psychiatric_grounds(grounds)
    assert len(out) == 2


# ------------------ 5. apply_authority_preferences ------------------

def test_procedure_ground_prefers_ebner_gittany_belghar_over_weiss():
    g = _g(
        type="procedure",
        authorities=[
            "Weiss v The Queen (2005) 224 CLR 300",
            "Ebner v Official Trustee (2000) 205 CLR 337",
            "R v Gittany [2013] NSWSC 1670",
        ],
    )
    apply_authority_preferences(g)
    joined = " ".join(g.authorities).lower()
    assert "ebner" in joined
    assert "gittany" in joined
    assert "weiss" not in joined


def test_sentence_ground_prefers_house_hili_dinsdale_over_m_v_queen():
    g = _g(
        type="sentence",
        authorities=[
            "M v The Queen (1994) 181 CLR 487",
            "House v The King (1936) 55 CLR 499",
            "Hili v The Queen (2010) 242 CLR 520",
        ],
    )
    apply_authority_preferences(g)
    joined = " ".join(g.authorities).lower()
    assert "house v the king" in joined
    assert "hili" in joined
    assert "m v the queen" not in joined


def test_procedure_ground_with_no_preferred_keeps_fallback():
    g = _g(
        type="procedure",
        authorities=[
            "Weiss v The Queen (2005) 224 CLR 300",
            "SKA v The Queen (2011) 243 CLR 400",
        ],
    )
    apply_authority_preferences(g)
    # No Ebner/Gittany/Belghar in input → fallback retains first 3
    assert len(g.authorities) <= 3
    assert len(g.authorities) >= 1


def test_conviction_ground_authorities_untouched_by_procedure_filter():
    g = _g(
        type="conviction",
        authorities=[
            "M v The Queen (1994) 181 CLR 487",
            "SKA v The Queen (2011) 243 CLR 400",
        ],
    )
    apply_authority_preferences(g)
    assert len(g.authorities) == 2


# ------------------ 6. End-to-end apply_cleanup — counsel's Homann scenario ------------------

def test_full_pipeline_handles_counsel_homann_scenario():
    """Mirrors the exact failure counsel described:
       - Ground 2 = psychiatric (correctly conviction)
       - Ground 4 = 'Sentencing Error' BUT about substantial impairment
       - Ground 1 + 3 = fragmented procedural
       Expected after apply_cleanup:
         - Ground 4 collapsed into Ground 2
         - Ground 1 + 3 merged into a single procedural ground
         - Ground 4's type corrected to conviction before the collapse
    """
    grounds = [
        _g(
            title="Jury separation — implied only",
            type="procedure",
            viability="arguable_strong",
            materiality="There is an implication that the jury was permitted to separate.",
            authorities=[
                "Weiss v The Queen (2005) 224 CLR 300",
                "Ebner v Official Trustee (2000) 205 CLR 337",
            ],
            sub_particulars=[SubParticular(label="a", text="Jury separation")],
        ),
        _g(
            title="Miscarriage of Justice: Mens rea / psychiatric evidence",
            type="conviction",
            viability="requires_development",
            record_support="strong",
            verdict_robustness="weak",
            crown_strength="weak",
            error_identified="Substantial impairment under s 23A was mishandled at trial.",
            sub_particulars=[SubParticular(label="a", text="Psychosis mishandled")],
        ),
        _g(
            title="Judge-alone refusal + prejudicial material",
            type="procedure",
            viability="arguable_moderate",
            sub_particulars=[SubParticular(label="a", text="Tendency evidence wrongly admitted")],
        ),
        _g(
            title="Sentencing Error — Failure to Consider Substantial Impairment as a Mitigating Factor",
            type="sentence",
            viability="arguable_moderate",
            error_identified="Partial defence under s 23A was not considered as mitigation.",
            sub_particulars=[SubParticular(label="a", text="Unique mental-state sub")],
        ),
    ]

    out = apply_cleanup(grounds, "NSW")

    # Exactly 2 grounds expected: merged procedural + merged psychiatric
    assert len(out) == 2, f"Expected 2 grounds, got {len(out)}: {[g.title for g in out]}"

    procs = [g for g in out if g.type == "procedure"]
    psych = [g for g in out if g.type == "conviction"]

    # Merged procedural is present, has absorbed sub-particulars
    assert len(procs) == 1
    assert any("separation" in sp.text.lower() for sp in procs[0].sub_particulars)
    assert any("tendency" in sp.text.lower() for sp in procs[0].sub_particulars)

    # Speculative procedure capped at requires_development
    assert procs[0].viability == "requires_development"

    # Weiss dropped (no procedure-authority matches in fallback list either — short input)
    assert not any("weiss" in a.lower() for a in (procs[0].authorities or []))

    # Psychiatric ground absorbed the 'Sentencing Error' twin — one survivor, unique sub preserved
    assert len(psych) == 1
    assert any("unique mental-state sub" in sp.text.lower() for sp in psych[0].sub_particulars)

    # NSW s 23A mitigation language corrected on the survivor
    assert psych[0].error_identified
    assert "mitigate" not in psych[0].error_identified.lower() or "liability" in psych[0].error_identified.lower()
