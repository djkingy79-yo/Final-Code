"""
appeal_strength.py

Post-normalisation realism scoring for criminal appeal grounds.

Purpose:
- assess record support
- assess verdict robustness / proviso-style risk
- assess likely Crown response strength
- downgrade inflated grounds
- attach concise failure-risk explanations

Jurisdiction-agnostic at the scoring layer.
Use AFTER ground_normaliser.py and BEFORE final report rendering.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

from services.ground_normaliser import Ground, cap_viability, normalise


RecordSupport = Literal["strong", "partial", "limited", "none"]
VerdictRobustness = Literal["overwhelming", "strong", "balanced", "weak"]
CrownStrength = Literal["strong", "moderate", "weak"]


@dataclass
class CaseEvidenceProfile:
    has_trial_transcript: bool = False
    has_sentencing_remarks: bool = False
    has_psychiatric_reports: bool = False
    has_counsel_affidavit: bool = False
    has_juror_affidavit: bool = False
    has_expert_reports: bool = False
    has_judge_alone_material: bool = False
    has_pretrial_publicity_material: bool = False
    has_forensic_evidence: bool = False
    has_direct_evidence: bool = False
    has_strong_circumstantial_evidence: bool = False
    multiple_consistent_witnesses: bool = False
    confession_or_admission: bool = False
    cctv_or_audio: bool = False
    post_offence_conduct_supports_guilt: bool = False
    disputed_identity: bool = False
    disputed_intent: bool = False
    competing_psychiatric_opinions: bool = False
    no_eyewitnesses: bool = False


def _text_blob(ground: Ground) -> str:
    return normalise(
        " ".join(
            [
                ground.title,
                ground.pathway,
                ground.trial_finding or "",
                ground.error_identified or "",
                ground.materiality or "",
                ground.consequence or "",
                " ".join(ground.supporting_evidence or []),
                " ".join(ground.relevant_law_sections or []),
                " ".join(ground.authorities or []),
                " ".join(f"{sp.label} {sp.text}" for sp in (ground.sub_particulars or [])),
            ]
        )
    )


def assess_record_support(ground: Ground, profile: CaseEvidenceProfile) -> RecordSupport:
    text = _text_blob(ground)

    if ground.type == "conviction":
        if any(x in text for x in ("mens rea", "mental state", "substantial impairment", "diminished responsibility", "mental impairment", "psychiatric", "psychosis", "intent")):
            if profile.has_trial_transcript and (profile.has_psychiatric_reports or profile.has_expert_reports):
                return "strong"
            if profile.has_psychiatric_reports or profile.has_expert_reports:
                return "partial"
            if profile.has_trial_transcript:
                return "partial"
            return "limited"
        if profile.has_trial_transcript:
            return "partial"
        return "limited"

    if ground.type == "sentence":
        if profile.has_sentencing_remarks:
            return "strong"
        return "limited"

    if ground.type == "procedure":
        if any(x in text for x in ("juror", "jury", "partiality", "misconduct", "bias")):
            if profile.has_juror_affidavit and profile.has_trial_transcript:
                return "strong"
            if profile.has_juror_affidavit:
                return "partial"
            return "limited"
        if any(x in text for x in ("judge-alone", "judge alone", "mode of trial")):
            if profile.has_judge_alone_material and profile.has_trial_transcript:
                return "strong"
            if profile.has_judge_alone_material:
                return "partial"
            return "limited"
        if any(x in text for x in ("pretrial publicity", "pre-trial publicity")):
            if profile.has_pretrial_publicity_material:
                return "partial"
            return "limited"
        return "limited"

    if ground.type == "ineffective_counsel":
        if profile.has_counsel_affidavit and profile.has_trial_transcript:
            return "strong"
        if profile.has_counsel_affidavit or profile.has_trial_transcript:
            return "partial"
        return "limited"

    if ground.type == "evidence":
        if profile.has_trial_transcript:
            return "strong"
        return "limited"

    return "none"


def assess_verdict_robustness(ground: Ground, profile: CaseEvidenceProfile) -> VerdictRobustness:
    if ground.type != "conviction":
        return "balanced"

    text = _text_blob(ground)
    overwhelming_score = 0
    weak_score = 0

    if profile.has_direct_evidence:
        overwhelming_score += 3
    if profile.multiple_consistent_witnesses:
        overwhelming_score += 2
    if profile.has_forensic_evidence:
        overwhelming_score += 2
    if profile.has_strong_circumstantial_evidence:
        overwhelming_score += 2
    if profile.confession_or_admission:
        overwhelming_score += 3
    if profile.cctv_or_audio:
        overwhelming_score += 2
    if profile.post_offence_conduct_supports_guilt:
        overwhelming_score += 1

    if profile.disputed_identity:
        weak_score += 2
    if profile.disputed_intent:
        weak_score += 2
    if profile.no_eyewitnesses:
        weak_score += 1

    if any(x in text for x in ("psychiatric", "psychosis", "mental state", "mens rea", "substantial impairment", "diminished responsibility", "mental impairment")):
        if profile.competing_psychiatric_opinions:
            weak_score += 3
        elif profile.has_psychiatric_reports:
            weak_score += 2

    net = overwhelming_score - weak_score
    if net >= 6:
        return "overwhelming"
    if net >= 3:
        return "strong"
    if net >= 0:
        return "balanced"
    return "weak"


def assess_crown_strength(ground: Ground, profile: CaseEvidenceProfile) -> CrownStrength:
    text = _text_blob(ground)

    if ground.type == "conviction":
        crown_score = 0
        if profile.has_direct_evidence:
            crown_score += 3
        if profile.multiple_consistent_witnesses:
            crown_score += 2
        if profile.has_forensic_evidence:
            crown_score += 2
        if profile.has_strong_circumstantial_evidence:
            crown_score += 2
        if profile.confession_or_admission:
            crown_score += 3
        if profile.cctv_or_audio:
            crown_score += 2
        if profile.post_offence_conduct_supports_guilt:
            crown_score += 1
        if any(x in text for x in ("psychiatric", "psychosis", "mental state", "mens rea", "substantial impairment", "mental impairment")):
            if profile.competing_psychiatric_opinions:
                crown_score -= 2
            elif profile.has_psychiatric_reports:
                crown_score -= 1

        if crown_score >= 6:
            return "strong"
        if crown_score >= 3:
            return "moderate"
        return "weak"

    if ground.type == "sentence":
        return "strong" if not profile.has_sentencing_remarks else "moderate"

    if ground.type == "ineffective_counsel":
        return "strong" if not profile.has_counsel_affidavit else "moderate"

    if ground.type == "procedure":
        if any(x in text for x in ("juror", "jury", "misconduct", "partiality")):
            return "strong" if not profile.has_juror_affidavit else "moderate"
        if any(x in text for x in ("judge-alone", "judge alone")):
            return "strong" if not profile.has_judge_alone_material else "moderate"
        return "moderate"

    if ground.type == "evidence":
        return "moderate" if profile.has_trial_transcript else "strong"

    return "moderate"


def build_failure_risk(
    ground: Ground,
    record_support: RecordSupport,
    verdict_robustness: VerdictRobustness,
    crown_strength: CrownStrength,
    profile: CaseEvidenceProfile,
) -> str:
    if record_support == "none":
        return "No meaningful record anchor has been identified for this ground."
    if record_support == "limited":
        return "The ground presently rests on limited record support and requires further documentary anchoring."

    if ground.type == "conviction":
        if verdict_robustness == "overwhelming":
            return "Even if error is shown, the Crown case appears overwhelming and the proviso-style answer may defeat the appeal."
        if verdict_robustness == "strong":
            return "The verdict may still have been open on the evidence despite the identified error."
        if crown_strength == "strong":
            return "The Crown is likely to answer this ground forcefully by relying on the strength of the prosecution case."
        if profile.competing_psychiatric_opinions:
            return "The appellate court may accept that the jury was entitled to prefer the Crown psychiatric evidence."

    if ground.type == "sentence":
        if not profile.has_sentencing_remarks:
            return "Without sentencing remarks, it is difficult to demonstrate appellable House error or manifest excess."
        return "The sentencing court may be found to have acted within the permissible range of discretion."

    if ground.type == "procedure":
        text = _text_blob(ground)
        if any(x in text for x in ("juror", "jury", "misconduct", "partiality", "bias")) and not profile.has_juror_affidavit:
            return "The alleged jury issue may not be provable in admissible form."
        if any(x in text for x in ("judge-alone", "judge alone")):
            return "Appellate courts are generally slow to interfere with mode-of-trial decisions absent clear error."
        return "The court may conclude that no substantial practical unfairness has been demonstrated."

    if ground.type == "ineffective_counsel":
        if not profile.has_counsel_affidavit:
            return "Ineffective counsel allegations usually fail without affidavit material and transcript-based particulars."
        return "The court may regard counsel's conduct as forensic choice rather than incompetence."

    if ground.type == "evidence":
        return "The court may regard any evidentiary error as non-material to the outcome."

    return "The identified issue may not be sufficient to demonstrate appellable error."


def apply_realism_adjustments(ground: Ground, profile: CaseEvidenceProfile) -> Ground:
    record_support = assess_record_support(ground, profile)
    verdict_robustness = assess_verdict_robustness(ground, profile)
    crown_strength = assess_crown_strength(ground, profile)

    ground.record_support = record_support
    ground.verdict_robustness = verdict_robustness
    ground.crown_strength = crown_strength

    # Helper to log trail entries for realism decisions.
    def _log(msg: str) -> None:
        if ground.reasoning_trail is None:
            ground.reasoning_trail = []
        ground.reasoning_trail.append(msg)

    if record_support == "none":
        prior = ground.viability
        ground.viability = cap_viability(ground.viability, "weak")
        if ground.viability != prior:
            _log(f"Realism cap: no record anchor detected → viability '{prior}' → 'weak'.")
        ground.failure_risk = build_failure_risk(
            ground, record_support, verdict_robustness, crown_strength, profile
        )
        return ground

    if record_support == "limited":
        prior = ground.viability
        ground.viability = cap_viability(ground.viability, "requires_development")
        if ground.viability != prior:
            _log(f"Realism cap: limited record support → viability '{prior}' → 'requires_development'.")

    if ground.type == "conviction":
        if verdict_robustness == "overwhelming":
            prior = ground.viability
            ground.viability = cap_viability(ground.viability, "arguable_moderate")
            if ground.viability != prior:
                _log(f"Proviso risk (overwhelming Crown case): viability '{prior}' → 'arguable_moderate'.")
        elif verdict_robustness == "strong":
            # Only cap down when the record support is thin. A strong-record
            # conviction ground should not be over-downgraded just because the
            # trial verdict was robust — counsel feedback 23 Feb 2026.
            if record_support in {"limited", "none"}:
                prior = ground.viability
                ground.viability = cap_viability(ground.viability, "arguable_moderate")
                if ground.viability != prior:
                    _log(f"Strong Crown case (thin record): viability '{prior}' → 'arguable_moderate'.")

    # Post-verdict juror conduct cap.
    if ground.type == "procedure":
        text = _text_blob(ground)
        if any(x in text for x in ("juror", "jury")):
            is_post_verdict_only = any(x in text for x in (
                "post-verdict", "post verdict", "after verdict", "after the verdict",
                "after deliberations", "once the verdict was returned",
            ))
            no_contemporaneous_record = not (
                profile.has_trial_transcript and profile.has_juror_affidavit
            )
            if is_post_verdict_only and no_contemporaneous_record:
                prior = ground.viability
                ground.viability = cap_viability(ground.viability, "weak")
                if ground.viability != prior:
                    _log(f"Post-verdict juror-conduct rule: minimal probative value on deliberative bias without contemporaneous record + juror affidavit → viability '{prior}' → 'weak'.")

    if crown_strength == "strong" and ground.viability == "arguable_strong":
        ground.viability = "arguable_moderate"
        _log("Strong Crown response: viability 'arguable_strong' → 'arguable_moderate'.")

    ground.failure_risk = build_failure_risk(
        ground, record_support, verdict_robustness, crown_strength, profile
    )
    return ground


def score_grounds_for_realism(
    grounds: list[Ground],
    profile: CaseEvidenceProfile,
) -> list[Ground]:
    return [apply_realism_adjustments(g, profile) for g in grounds]
