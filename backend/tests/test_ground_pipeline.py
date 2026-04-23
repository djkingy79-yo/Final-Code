"""
test_ground_pipeline.py

End-to-end tests for:
- jurisdiction-aware normalisation
- realism scoring
- cleanup layer

Covers:
- NSW psychiatric murder / substantial impairment
- NT recklessness murder
- QLD diminished responsibility
- VIC mental impairment
- Commonwealth / federal fault-elements case
"""

import os
import sys

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


def run_pipeline(raw_grounds, flags, profile, jurisdiction):
    normalised = normalise_generated_grounds(
        raw_grounds=raw_grounds,
        flags=flags,
        jurisdiction=jurisdiction,
    )
    scored = score_grounds_for_realism(normalised, profile)
    cleaned = apply_cleanup(scored, jurisdiction)
    return cleaned


def test_nsw_psychiatric_murder_pipeline():
    raw_grounds = [
        Ground(
            title="Miscarriage of Justice: Failure to Properly Determine Mental State (Mens Rea)",
            type=None,
            pathway="",
            viability="arguable_strong",
            supporting_evidence=[
                "The offender raised the partial defence of substantial impairment by abnormality of mind.",
                "Psychiatric evidence suggested psychosis at the time of the offence.",
                "The psychosis was treated as if it only went to mitigation.",
            ],
            relevant_law_sections=[
                "s 23A Crimes Act 1900 (NSW)",
                "s 18 Crimes Act 1900 (NSW)",
                "s 21A Crimes (Sentencing Procedure) Act 1999 (NSW)",
            ],
            authorities=[
                "M v The Queen (1994) 181 CLR 487",
                "SKA v The Queen (2011) 243 CLR 400",
                "House v The King (1936) 55 CLR 499",
            ],
            trial_finding=(
                "The judge concluded the psychosis was drug-induced and did not mitigate the accused's mental culpability under section 23A."
            ),
            error_identified=(
                "The trial judge failed to properly evaluate psychiatric evidence relevant to mens rea and substantial impairment."
            ),
            materiality=(
                "If substantial impairment had been accepted, the conviction may have been reduced from murder to manslaughter."
            ),
            consequence=(
                "The verdict may be unsafe and the matter may require re-sentencing."
            ),
            sub_particulars=[
                SubParticular(label="(a)", text="Failure to Properly Evaluate Psychiatric Evidence"),
                SubParticular(label="(b)", text="Inadequate Presentation of Psychiatric Evidence"),
                SubParticular(label="(c)", text="Sentencing Consideration of Drug Use"),
            ],
        )
    ]

    flags = EvidenceFlags(
        transcript_support=True,
        sentencing_remarks=True,
        psychiatric_reports=True,
    )

    profile = CaseEvidenceProfile(
        has_trial_transcript=True,
        has_sentencing_remarks=True,
        has_psychiatric_reports=True,
        has_expert_reports=True,
        disputed_intent=True,
        competing_psychiatric_opinions=True,
        has_direct_evidence=False,
        has_strong_circumstantial_evidence=True,
        has_forensic_evidence=True,
    )

    results = run_pipeline(raw_grounds, flags, profile, "NSW")
    assert len(results) >= 1

    conviction = results[0]
    assert conviction.type == "conviction"
    assert "s 23A" in " ".join(conviction.relevant_law_sections)
    assert all("sentencing" not in sp.text.lower() for sp in (conviction.sub_particulars or []))
    assert conviction.record_support in {"strong", "partial"}
    assert conviction.verdict_robustness in {"weak", "balanced", "strong"}
    assert conviction.crown_strength in {"weak", "moderate", "strong"}
    assert "mitigate" not in (conviction.trial_finding or "").lower() or "partial defence" in (conviction.trial_finding or "").lower()


def test_nt_recklessness_murder_pipeline():
    raw_grounds = [
        Ground(
            title="Misdirection on Mental Element of Murder",
            type=None,
            pathway="",
            viability="arguable_strong",
            supporting_evidence=[
                "The jury may have been directed by reference to possibility rather than probability.",
                "The issue concerns reckless indifference and criminal responsibility.",
            ],
            relevant_law_sections=[
                "s 156 Criminal Code Act 1983 (NT)",
                "Part X Criminal Code Act 1983 (NT)",
            ],
            authorities=[
                "R v Crabbe (1985) 156 CLR 464",
                "M v The Queen (1994) 181 CLR 487",
            ],
            trial_finding=(
                "The trial judge found the accused had the requisite intent or knowledge of probable consequences."
            ),
            error_identified=(
                "The jury may have been permitted to convict on a lower threshold than probability of death."
            ),
            materiality=(
                "The distinction between possibility and probability was central to the murder conviction."
            ),
            consequence=(
                "If misdirection is made out, the conviction may be unsafe."
            ),
            sub_particulars=[
                SubParticular(label="(a)", text="Misdirection on Probability versus Possibility"),
            ],
        )
    ]

    flags = EvidenceFlags(
        transcript_support=True,
        psychiatric_reports=False,
    )

    profile = CaseEvidenceProfile(
        has_trial_transcript=True,
        has_direct_evidence=False,
        has_strong_circumstantial_evidence=True,
        has_forensic_evidence=True,
        post_offence_conduct_supports_guilt=True,
        disputed_intent=True,
    )

    results = run_pipeline(raw_grounds, flags, profile, "NT")
    assert len(results) == 1
    g = results[0]
    assert g.type == "conviction"
    assert "Northern Territory" in g.pathway or "NT" in g.pathway
    assert g.record_support in {"strong", "partial"}
    assert g.failure_risk is not None


def test_qld_diminished_responsibility_pipeline():
    raw_grounds = [
        Ground(
            title="Failure to Properly Assess Diminished Responsibility",
            type=None,
            pathway="",
            viability="arguable_strong",
            supporting_evidence=[
                "The defence relied on diminished responsibility.",
                "Psychiatric evidence addressed the accused's mental condition at the time of the killing.",
                "The material should not be treated as mere mitigation.",
            ],
            relevant_law_sections=[
                "s 304A Criminal Code 1899 (Qld)",
                "Penalties and Sentences Act 1992 (Qld)",
            ],
            authorities=[
                "M v The Queen (1994) 181 CLR 487",
                "House v The King (1936) 55 CLR 499",
            ],
            trial_finding=(
                "The trial judge rejected the mental condition evidence as not sufficient to reduce culpability."
            ),
            error_identified=(
                "It is arguable the trial judge failed to properly engage diminished responsibility."
            ),
            materiality=(
                "If diminished responsibility was made out, murder would not stand."
            ),
            consequence=(
                "The conviction may require substitution or retrial."
            ),
            sub_particulars=[
                SubParticular(label="(a)", text="Diminished Responsibility"),
                SubParticular(label="(b)", text="Mental health mitigation at sentence"),
            ],
        )
    ]

    flags = EvidenceFlags(
        transcript_support=True,
        sentencing_remarks=True,
        psychiatric_reports=True,
    )

    profile = CaseEvidenceProfile(
        has_trial_transcript=True,
        has_sentencing_remarks=True,
        has_psychiatric_reports=True,
        has_expert_reports=True,
        disputed_intent=True,
        competing_psychiatric_opinions=True,
    )

    results = run_pipeline(raw_grounds, flags, profile, "QLD")
    assert len(results) >= 1

    conviction = next(g for g in results if g.type == "conviction")
    assert "diminished responsibility" in " ".join(conviction.supporting_evidence).lower() or \
           "diminished responsibility" in (conviction.error_identified or "").lower()
    assert all("mitigation" not in sp.text.lower() for sp in (conviction.sub_particulars or []))


def test_vic_mental_impairment_pipeline():
    raw_grounds = [
        Ground(
            title="Failure to Properly Leave the Defence of Mental Impairment",
            type=None,
            pathway="",
            viability="arguable_strong",
            supporting_evidence=[
                "The defence of mental impairment was raised.",
                "Competing psychiatric evidence addressed cognitive capacity and mental state.",
            ],
            relevant_law_sections=[
                "Crimes (Mental Impairment and Unfitness to be Tried) Act 1997 (Vic)",
                "Criminal Procedure Act 2009 (Vic)",
            ],
            authorities=[
                "M v The Queen (1994) 181 CLR 487",
            ],
            trial_finding=(
                "The jury convicted notwithstanding the defence contention that mental impairment was engaged."
            ),
            error_identified=(
                "The jury may not have been properly directed as to the defence of mental impairment."
            ),
            materiality=(
                "The issue went directly to criminal responsibility."
            ),
            consequence=(
                "The conviction may be unsafe."
            ),
            sub_particulars=[
                SubParticular(label="(a)", text="Mental Impairment"),
                SubParticular(label="(b)", text="Sentence failed to consider rehabilitation"),
            ],
        )
    ]

    flags = EvidenceFlags(
        transcript_support=True,
        psychiatric_reports=True,
        sentencing_remarks=True,
    )

    profile = CaseEvidenceProfile(
        has_trial_transcript=True,
        has_psychiatric_reports=True,
        has_expert_reports=True,
        disputed_intent=True,
        competing_psychiatric_opinions=True,
    )

    results = run_pipeline(raw_grounds, flags, profile, "VIC")
    conviction = next(g for g in results if g.type == "conviction")
    assert "Vic" in conviction.pathway or "VIC" in conviction.pathway
    assert all("rehabilitation" not in sp.text.lower() for sp in (conviction.sub_particulars or []))


def test_cth_fault_elements_pipeline():
    raw_grounds = [
        Ground(
            title="Failure to Properly Determine Federal Fault Elements",
            type=None,
            pathway="",
            viability="arguable_strong",
            supporting_evidence=[
                "The issue concerns intention, knowledge, recklessness, and negligence under the Criminal Code Act 1995 (Cth).",
                "The trial reasoning may have conflated recklessness with knowledge.",
            ],
            relevant_law_sections=[
                "Criminal Code Act 1995 (Cth)",
                "fault elements",
            ],
            authorities=[
                "He Kaw Teh v The Queen (1985) 157 CLR 523",
            ],
            trial_finding=(
                "The trial court concluded the requisite federal fault element was satisfied."
            ),
            error_identified=(
                "The court may have failed to distinguish the relevant fault elements with sufficient precision."
            ),
            materiality=(
                "The issue went to liability rather than mere punishment."
            ),
            consequence=(
                "The conviction may be unsafe if the wrong fault element was applied."
            ),
            sub_particulars=[
                SubParticular(label="(a)", text="Fault Elements"),
                SubParticular(label="(b)", text="Mitigation at sentence"),
            ],
        )
    ]

    flags = EvidenceFlags(
        transcript_support=True,
        psychiatric_reports=False,
    )

    profile = CaseEvidenceProfile(
        has_trial_transcript=True,
        has_direct_evidence=False,
        has_strong_circumstantial_evidence=True,
        disputed_intent=True,
    )

    results = run_pipeline(raw_grounds, flags, profile, "CTH")
    conviction = next(g for g in results if g.type == "conviction")
    assert "Commonwealth" in conviction.pathway or "federal" in conviction.pathway.lower()
    assert all("mitigation" not in sp.text.lower() for sp in (conviction.sub_particulars or []))
    assert conviction.failure_risk is not None
