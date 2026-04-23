"""
test_ground_invariants.py

Global regression guards — counsel feedback 23 Feb 2026.

Enforces two cross-jurisdictional invariants that MUST hold after the full
normalise → realism → cleanup pipeline, no matter which state/territory
or fact pattern is put through:

  INVARIANT 1: No conviction ground contains sentencing language
               in any of its sub-particulars.
  INVARIANT 2: No sentence ground contains liability language
               in any of its sub-particulars.

These are stop-the-line assertions. If either fails, the normaliser /
splitter / cleanup chain has regressed and contaminated output is about
to reach counsel — fix before merging.
"""

import os
import sys

import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from services.ground_normaliser import (
    EvidenceFlags,
    Ground,
    SubParticular,
    normalise_generated_grounds,
)
from services.appeal_strength import (
    CaseEvidenceProfile,
    score_grounds_for_realism,
)
from services.ground_cleanup import apply_cleanup


# Must mirror services/ground_cleanup.py — if these lists ever drift, the
# invariant assertions become toothless.
SENTENCING_TOKENS = (
    "sentencing",
    "non-parole",
    "non parole",
    "manifestly excessive",
    "manifest excess",
    "mitigation",
    "moral culpability",
    "rehabilitation",
    "totality",
)

LIABILITY_TOKENS = (
    "mens rea",
    "unsafe verdict",
    "unreasonable verdict",
    "substantial impairment",
    "diminished responsibility",
    "mental impairment defence",
    "defence of mental impairment",
    "abnormality of mind",
    "partial defence",
    "unsoundness of mind",
)


def _run(raw_grounds, flags, profile, jurisdiction):
    normalised = normalise_generated_grounds(
        raw_grounds=raw_grounds,
        flags=flags,
        jurisdiction=jurisdiction,
    )
    scored = score_grounds_for_realism(normalised, profile)
    return apply_cleanup(scored, jurisdiction)


def _assert_invariants(grounds, case_label=""):
    """Stop-the-line invariant check."""
    for g in grounds:
        subs = g.sub_particulars or []
        if g.type == "conviction":
            for sp in subs:
                t = sp.text.lower()
                hit = next((tok for tok in SENTENCING_TOKENS if tok in t), None)
                assert hit is None, (
                    f"[{case_label}] INVARIANT 1 FAILED — conviction ground "
                    f"'{g.title}' retained sentencing token '{hit}' in sub-particular: {sp.text!r}"
                )
        elif g.type == "sentence":
            for sp in subs:
                t = sp.text.lower()
                hit = next((tok for tok in LIABILITY_TOKENS if tok in t), None)
                assert hit is None, (
                    f"[{case_label}] INVARIANT 2 FAILED — sentence ground "
                    f"'{g.title}' retained liability token '{hit}' in sub-particular: {sp.text!r}"
                )


# ------------------ INVARIANT 1 guards ------------------

@pytest.mark.parametrize(
    "jurisdiction,contaminated_sub_text",
    [
        ("NSW", "Sentencing Consideration of Drug Use"),
        ("NSW", "Failure to take into account rehabilitation prospects"),
        ("NSW", "Non-parole period too long"),
        ("QLD", "Manifestly excessive head sentence"),
        ("QLD", "Moral culpability at sentencing was overstated"),
        ("VIC", "Totality principle breached"),
        ("WA", "Mitigation at sentence not properly considered"),
        ("SA", "Rehabilitation opportunities ignored"),
        ("TAS", "Non parole period unjust"),
        ("NT", "Sentencing discretion miscarried"),
        ("ACT", "Manifest excess in head sentence"),
        ("CTH", "Mitigation at sentence"),
    ],
)
def test_conviction_ground_never_retains_sentencing_sub(jurisdiction, contaminated_sub_text):
    raw = [
        Ground(
            title="Alleged trial misdirection on mens rea",
            type="conviction",
            pathway="",
            viability="arguable_strong",
            supporting_evidence=["The jury may have been misdirected as to intent."],
            relevant_law_sections=[],
            authorities=[],
            trial_finding="The trial judge gave directions regarding intent.",
            error_identified="Intent was conflated with motive.",
            materiality="The misdirection went to a core element of the offence.",
            consequence="The conviction may be unsafe.",
            sub_particulars=[
                SubParticular(label="(a)", text="Misdirection on intent"),
                SubParticular(label="(b)", text=contaminated_sub_text),
            ],
        )
    ]
    flags = EvidenceFlags(transcript_support=True)
    profile = CaseEvidenceProfile(has_trial_transcript=True, disputed_intent=True)
    results = _run(raw, flags, profile, jurisdiction)
    _assert_invariants(results, case_label=f"INV1/{jurisdiction}")


# ------------------ INVARIANT 2 guards ------------------

@pytest.mark.parametrize(
    "jurisdiction,contaminated_sub_text",
    [
        ("NSW", "Substantial impairment by abnormality of mind"),
        ("NSW", "Partial defence was wrongly rejected"),
        ("QLD", "Diminished responsibility evidence was overlooked"),
        ("QLD", "Unsoundness of mind was not properly left"),
        ("VIC", "Defence of mental impairment not properly put to jury"),
        ("WA", "Unsoundness of mind should have been left"),
        ("SA", "Mental impairment engaged"),
        ("TAS", "Insanity defence was not properly considered"),
        ("NT", "Mental impairment defence was engaged"),
        ("ACT", "Mental impairment should have reduced conviction"),
        ("CTH", "Mens rea was not established on the fault elements"),
        ("CTH", "Unsafe verdict on the element of recklessness"),
    ],
)
def test_sentence_ground_never_retains_liability_sub(jurisdiction, contaminated_sub_text):
    raw = [
        Ground(
            title="Alleged manifest excess in head sentence",
            type="sentence",
            pathway="",
            viability="arguable_moderate",
            supporting_evidence=["The sentencing judge did not properly weigh mitigating factors."],
            relevant_law_sections=[],
            authorities=["House v The King (1936) 55 CLR 499"],
            trial_finding="The sentencing judge imposed the head sentence of x years.",
            error_identified="The head sentence was disproportionate on comparable authorities.",
            materiality="If manifest excess is made out, the sentence must be reduced.",
            consequence="Re-sentencing is required.",
            sub_particulars=[
                SubParticular(label="(a)", text="Manifestly excessive head sentence"),
                SubParticular(label="(b)", text=contaminated_sub_text),
            ],
        )
    ]
    flags = EvidenceFlags(transcript_support=True, sentencing_remarks=True)
    profile = CaseEvidenceProfile(
        has_trial_transcript=True,
        has_sentencing_remarks=True,
    )
    results = _run(raw, flags, profile, jurisdiction)
    _assert_invariants(results, case_label=f"INV2/{jurisdiction}")


# ------------------ Invariants hold on the full counsel-supplied pipeline scenarios ------------------

def test_invariants_hold_on_nsw_psychiatric_murder():
    raw = [
        Ground(
            title="Miscarriage of Justice: Failure to Properly Determine Mental State (Mens Rea)",
            type=None,
            pathway="",
            viability="arguable_strong",
            supporting_evidence=[
                "The offender raised the partial defence of substantial impairment by abnormality of mind.",
            ],
            relevant_law_sections=["s 23A Crimes Act 1900 (NSW)"],
            authorities=[],
            trial_finding="The judge concluded the psychosis did not mitigate the accused's mental culpability under section 23A.",
            error_identified="Psychiatric evidence was mishandled.",
            materiality="If substantial impairment had been accepted, murder might have been reduced to manslaughter.",
            consequence="The verdict may be unsafe.",
            sub_particulars=[
                SubParticular(label="(a)", text="Failure to Properly Evaluate Psychiatric Evidence"),
                SubParticular(label="(b)", text="Sentencing Consideration of Drug Use"),
            ],
        )
    ]
    flags = EvidenceFlags(transcript_support=True, psychiatric_reports=True, sentencing_remarks=True)
    profile = CaseEvidenceProfile(
        has_trial_transcript=True,
        has_sentencing_remarks=True,
        has_psychiatric_reports=True,
        has_expert_reports=True,
        disputed_intent=True,
        competing_psychiatric_opinions=True,
    )
    results = _run(raw, flags, profile, "NSW")
    _assert_invariants(results, case_label="NSW/psychiatric")


def test_invariants_hold_on_qld_diminished_responsibility():
    raw = [
        Ground(
            title="Failure to Properly Assess Diminished Responsibility",
            type=None,
            pathway="",
            viability="arguable_strong",
            supporting_evidence=["The defence relied on diminished responsibility."],
            relevant_law_sections=["s 304A Criminal Code 1899 (Qld)"],
            authorities=[],
            trial_finding="The trial judge rejected the mental condition evidence.",
            error_identified="The court failed to properly engage diminished responsibility.",
            materiality="If made out, murder would not stand.",
            consequence="Conviction may require substitution.",
            sub_particulars=[
                SubParticular(label="(a)", text="Diminished Responsibility"),
                SubParticular(label="(b)", text="Mental health mitigation at sentence"),
            ],
        )
    ]
    flags = EvidenceFlags(transcript_support=True, psychiatric_reports=True, sentencing_remarks=True)
    profile = CaseEvidenceProfile(
        has_trial_transcript=True,
        has_sentencing_remarks=True,
        has_psychiatric_reports=True,
        has_expert_reports=True,
        disputed_intent=True,
        competing_psychiatric_opinions=True,
    )
    results = _run(raw, flags, profile, "QLD")
    _assert_invariants(results, case_label="QLD/diminished")


def test_invariants_hold_on_cth_fault_elements():
    raw = [
        Ground(
            title="Failure to Properly Determine Federal Fault Elements",
            type=None,
            pathway="",
            viability="arguable_strong",
            supporting_evidence=["The trial may have conflated recklessness with knowledge."],
            relevant_law_sections=["Criminal Code Act 1995 (Cth)"],
            authorities=[],
            trial_finding="The trial court concluded the requisite federal fault element was satisfied.",
            error_identified="Fault elements not distinguished with sufficient precision.",
            materiality="The issue went to liability rather than mere punishment.",
            consequence="The conviction may be unsafe.",
            sub_particulars=[
                SubParticular(label="(a)", text="Fault Elements"),
                SubParticular(label="(b)", text="Mitigation at sentence"),
            ],
        )
    ]
    flags = EvidenceFlags(transcript_support=True)
    profile = CaseEvidenceProfile(
        has_trial_transcript=True,
        disputed_intent=True,
        has_strong_circumstantial_evidence=True,
    )
    results = _run(raw, flags, profile, "CTH")
    _assert_invariants(results, case_label="CTH/fault-elements")
