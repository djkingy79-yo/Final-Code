"""
ground_normaliser.py

Generic jurisdiction-aware post-generation normaliser for appellate grounds.
No NSW default is hardcoded. Every classification/pathway call takes the
case's jurisdiction as a parameter.
"""

from __future__ import annotations

import re
from collections import defaultdict
from dataclasses import dataclass
from typing import Iterable, Literal, Optional

from services.jurisdiction_rules import get_rules, infer_pathway


GroundType = Literal["conviction", "sentence", "procedure", "evidence", "ineffective_counsel"]
Viability = Literal["arguable_strong", "arguable_moderate", "requires_development", "weak"]


VIABILITY_ORDER: dict[Viability, int] = {
    "weak": 0,
    "requires_development": 1,
    "arguable_moderate": 2,
    "arguable_strong": 3,
}

TYPE_PRIORITY: dict[GroundType, int] = {
    "conviction": 1,
    "procedure": 2,
    "ineffective_counsel": 3,
    "evidence": 4,
    "sentence": 5,
}


@dataclass
class SubParticular:
    label: str
    text: str
    detected_type: Optional[GroundType] = None


@dataclass
class Ground:
    title: str
    type: Optional[GroundType]
    pathway: str
    viability: Viability
    supporting_evidence: list[str]
    relevant_law_sections: list[str]
    authorities: list[str]
    trial_finding: Optional[str] = None
    error_identified: Optional[str] = None
    materiality: Optional[str] = None
    consequence: Optional[str] = None
    sub_particulars: Optional[list[SubParticular]] = None
    # Realism scoring (set by services/appeal_strength.py)
    record_support: Optional[str] = None          # strong | partial | limited | none
    verdict_robustness: Optional[str] = None      # overwhelming | strong | balanced | weak
    crown_strength: Optional[str] = None          # strong | moderate | weak
    failure_risk: Optional[str] = None            # one-sentence explanation
    # Chain of Reasoning — audit trail of every classification / split / cap /
    # realism decision this engine made on the ground. Shown to users in the
    # UI so counsel can verify the forensic logic, not just the output.
    reasoning_trail: Optional[list[str]] = None


@dataclass
class EvidenceFlags:
    transcript_support: bool = False
    sentencing_remarks: bool = False
    counsel_affidavit: bool = False
    juror_affidavit: bool = False
    psychiatric_reports: bool = False
    judge_alone_application_material: bool = False
    pretrial_publicity_material: bool = False


def normalise(text: str) -> str:
    return re.sub(r"\s+", " ", (text or "").lower()).strip()


def dedupe_keep_order(items: Iterable[str]) -> list[str]:
    seen: set[str] = set()
    out: list[str] = []
    for item in items:
        cleaned = (item or "").strip()
        if not cleaned:
            continue
        key = normalise(cleaned)
        if key in seen:
            continue
        seen.add(key)
        out.append(cleaned)
    return out


def max_viability(a: Viability, b: Viability) -> Viability:
    return a if VIABILITY_ORDER[a] >= VIABILITY_ORDER[b] else b


def cap_viability(current: Viability, cap: Viability) -> Viability:
    return current if VIABILITY_ORDER[current] <= VIABILITY_ORDER[cap] else cap


def blob_for_ground(ground: Ground) -> str:
    parts = [
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
    return normalise(" ".join(parts))


def _append_trail(ground: Ground, entry: str) -> None:
    if ground.reasoning_trail is None:
        ground.reasoning_trail = []
    ground.reasoning_trail.append(entry)


def classify_text_with_reason(text: str, jurisdiction: str) -> tuple[GroundType, str]:
    """Classify a chunk of legal text and RETURN the specific rule that fired.
    Used to build the Chain of Reasoning shown to counsel."""
    t = normalise(text)
    rules = get_rules(jurisdiction)

    # HARD PRIORITY: partial defences — liability stage, never sentencing.
    _PARTIAL_DEFENCE_TERMS = {
        "s 23a", "section 23a", "substantial impairment", "abnormality of mind",
        "diminished responsibility", "mental impairment defence",
        "defence of mental impairment", "unsoundness of mind", "mental incompetence",
        "partial defence",
    }
    for term in _PARTIAL_DEFENCE_TERMS:
        if term in t:
            return "conviction", f"Partial defence rule: content matches '{term}' → conviction (liability stage, never sentencing mitigation)"

    for term in rules.hard_conviction_terms:
        if term in t:
            return "conviction", f"Hard conviction rule: content matches '{term}' → conviction"
    for term in rules.hard_sentence_terms:
        if term in t:
            return "sentence", f"Hard sentence rule: content matches '{term}' → sentence"
    for term in rules.hard_procedure_terms:
        if term in t:
            return "procedure", f"Hard procedure rule: content matches '{term}' → procedure"
    for term in rules.ineffective_counsel_terms:
        if term in t:
            return "ineffective_counsel", f"Ineffective counsel rule: content matches '{term}'"
    for term in rules.evidence_terms:
        if term in t:
            return "evidence", f"Evidence rule: content matches '{term}'"

    score: dict[GroundType, int] = {
        "conviction": 0, "sentence": 0, "procedure": 0,
        "evidence": 0, "ineffective_counsel": 0,
    }
    for term in rules.conviction_terms:
        if term in t:
            score["conviction"] += 2
    for term in rules.sentence_terms:
        if term in t:
            score["sentence"] += 2
    for term in rules.procedure_terms:
        if term in t:
            score["procedure"] += 2
    for term in rules.evidence_terms:
        if term in t:
            score["evidence"] += 2
    for term in rules.ineffective_counsel_terms:
        if term in t:
            score["ineffective_counsel"] += 2

    best = max(score, key=score.get)
    if score[best] > 0:
        return best, f"Weighted classification: highest score ({score[best]}) for '{best}'"
    return "conviction", "No specific terms matched; defaulted to conviction (safest classification)"


def classify_text(text: str, jurisdiction: str) -> GroundType:
    gtype, _reason = classify_text_with_reason(text, jurisdiction)
    return gtype


def build_title_for_type(original_title: str, gtype: GroundType) -> str:
    original = normalise(original_title)

    if gtype == "conviction":
        if "mens rea" in original or "mental state" in original or "psychiatric" in original:
            return "Unsafe Verdict: Failure to Properly Determine Mental State"
        if "substantial impairment" in original or "mental impairment" in original:
            return "Failure to Properly Assess Mental Impairment Defence"
        return "Unsafe Verdict"

    if gtype == "sentence":
        if "rehabilitation" in original:
            return "Sentencing Error: Failure to Properly Consider Rehabilitation"
        if "mental" in original or "psychiatric" in original:
            return "Sentencing Error: Failure to Properly Assess Mental Condition and Culpability"
        return "Sentencing Error"

    if gtype == "procedure":
        if "jury" in original or "juror" in original:
            return "Procedural Unfairness (Jury Integrity)"
        if "judge alone" in original or "judge-alone" in original:
            return "Procedural Unfairness: Refusal of Judge-Alone Trial"
        return "Procedural Unfairness"

    if gtype == "evidence":
        return "Evidentiary Error"

    return "Ineffective Assistance of Counsel"


def classify_sub_particulars(ground: Ground, jurisdiction: str) -> None:
    for sp in ground.sub_particulars or []:
        sp.detected_type = classify_text(f"{sp.label} {sp.text}", jurisdiction)


def filter_items_by_type(items: list[str], gtype: GroundType, jurisdiction: str) -> list[str]:
    out: list[str] = []
    for item in items or []:
        item_type = classify_text(item, jurisdiction)
        if item_type == gtype:
            out.append(item)
    # Empty fallback — do NOT fall back to the ORIGINAL list when filtering
    # for a split. Returning the mixed originals would re-contaminate the
    # split grounds with off-topic content (e.g. a "Sentencing Error" split
    # inheriting psychiatric supporting evidence, which then flips the ground
    # type back to conviction during revalidation).
    return out


def canonical_title(title: str) -> str:
    t = normalise(title)
    if any(x in t for x in ("mens rea", "mental state", "unsafe verdict", "substantial impairment", "mental impairment", "psychiatric")):
        return "mens_rea"
    if any(x in t for x in ("rehabilitation", "manifestly excessive", "manifest excess", "sentence", "sentencing")):
        return "sentence"
    if any(x in t for x in ("jury", "juror", "judge-alone", "judge alone", "mode of trial")):
        return "jury_procedure"
    if any(x in t for x in ("ineffective counsel", "ineffective assistance", "tkwj")):
        return "ineffective_counsel"
    if any(x in t for x in ("admissibility", "prejudicial", "probative", "evidence")):
        return "evidence"
    return t


def _strip_off_topic_language(text: Optional[str], keep_type: GroundType, jurisdiction: str) -> Optional[str]:
    """Strip sentences from free-text fields that belong to a different
    appellate pathway. Used during force-splits so the CONVICTION half of a
    mixed ground doesn't inherit sentencing phrases (and vice versa), which
    would retrigger the integrity validator."""
    if not text:
        return text
    sentences = re.split(r"(?<=[.!?])\s+(?=[A-Z])", text)
    kept = []
    for s in sentences:
        stype = classify_text(s, jurisdiction)
        if stype == keep_type:
            kept.append(s)
    joined = " ".join(kept).strip()
    return joined or None


def split_mixed_ground(ground: Ground, jurisdiction: str) -> list[Ground]:
    """Split a ground into separate grounds when its content spans multiple
    appellate pathways. Two triggers:

    1. SUB-PARTICULARS with different detected types.
    2. HARD RULE: if parent content contains BOTH hard_conviction AND
       hard_sentence indicators (or procedure + conviction), force-split.
       Counsel rule: "Do not merge conviction grounds with sentencing grounds
       under any circumstance."
    """
    classify_sub_particulars(ground, jurisdiction)
    rules = get_rules(jurisdiction)
    parent_text = blob_for_ground(ground)

    has_conv = any(term in parent_text for term in rules.hard_conviction_terms)
    has_sent = any(term in parent_text for term in rules.hard_sentence_terms)
    has_proc = any(term in parent_text for term in rules.hard_procedure_terms)

    active_types: list[GroundType] = []
    if has_conv:
        active_types.append("conviction")
    if has_sent:
        active_types.append("sentence")
    if has_proc and len(active_types) >= 1:
        active_types.append("procedure")

    if len(active_types) >= 2:
        matched_conv = [t for t in rules.hard_conviction_terms if t in parent_text]
        matched_sent = [t for t in rules.hard_sentence_terms if t in parent_text]
        matched_proc = [t for t in rules.hard_procedure_terms if t in parent_text]
        reason = (
            f"Force-split trigger: parent content contains indicators from multiple pathways "
            f"(conviction={matched_conv[:2] or '-'}, sentence={matched_sent[:2] or '-'}, "
            f"procedure={matched_proc[:2] or '-'}). Counsel rule: conviction and sentence "
            f"grounds may never be merged."
        )
        split: list[Ground] = []
        for gtype in active_types:
            new_g = Ground(
                title=build_title_for_type(ground.title, gtype),
                type=gtype,
                pathway=infer_pathway(jurisdiction, gtype),
                viability=ground.viability,
                supporting_evidence=filter_items_by_type(ground.supporting_evidence, gtype, jurisdiction),
                relevant_law_sections=filter_items_by_type(ground.relevant_law_sections, gtype, jurisdiction),
                authorities=filter_items_by_type(ground.authorities, gtype, jurisdiction),
                trial_finding=ground.trial_finding,
                error_identified=_strip_off_topic_language(ground.error_identified, gtype, jurisdiction),
                materiality=_strip_off_topic_language(ground.materiality, gtype, jurisdiction),
                consequence=_strip_off_topic_language(ground.consequence, gtype, jurisdiction),
                sub_particulars=[sp for sp in (ground.sub_particulars or []) if sp.detected_type == gtype],
            )
            _append_trail(new_g, reason)
            _append_trail(new_g, f"This ground is the {gtype.upper()} half of the original mixed ground titled '{ground.title}'.")
            split.append(new_g)
        return split

    parent_type, reason = classify_text_with_reason(parent_text, jurisdiction)

    if not ground.sub_particulars:
        ground.type = parent_type
        ground.pathway = infer_pathway(jurisdiction, parent_type)
        _append_trail(ground, reason)
        return [ground]

    buckets: dict[GroundType, list[SubParticular]] = defaultdict(list)
    for sp in ground.sub_particulars:
        if sp.detected_type is not None:
            buckets[sp.detected_type].append(sp)

    if len(buckets) <= 1:
        only_type = next(iter(buckets)) if buckets else parent_type
        ground.type = only_type
        ground.pathway = infer_pathway(jurisdiction, only_type)
        _append_trail(ground, reason)
        return [ground]

    split: list[Ground] = []
    reason = (
        f"Sub-particular split: the ground's sub-particulars span "
        f"{len(buckets)} appellate pathways ({', '.join(buckets.keys())}) and "
        f"have been separated into one ground per pathway."
    )
    for gtype, subs in buckets.items():
        new_g = Ground(
            title=build_title_for_type(ground.title, gtype),
            type=gtype,
            pathway=infer_pathway(jurisdiction, gtype),
            viability=ground.viability,
            supporting_evidence=filter_items_by_type(ground.supporting_evidence, gtype, jurisdiction),
            relevant_law_sections=filter_items_by_type(ground.relevant_law_sections, gtype, jurisdiction),
            authorities=filter_items_by_type(ground.authorities, gtype, jurisdiction),
            trial_finding=ground.trial_finding,
            error_identified=ground.error_identified,
            materiality=ground.materiality,
            consequence=ground.consequence,
            sub_particulars=subs,
        )
        _append_trail(new_g, reason)
        _append_trail(new_g, f"Routed to {gtype.upper()} pathway: {len(subs)} sub-particular(s) classified as {gtype}.")
        split.append(new_g)
    return split


def merge_duplicate_grounds(grounds: list[Ground]) -> list[Ground]:
    merged: dict[tuple[GroundType, str], Ground] = {}

    for g in grounds:
        if g.type is None:
            continue
        key = (g.type, canonical_title(g.title))
        existing = merged.get(key)

        if existing is None:
            merged[key] = Ground(
                title=g.title, type=g.type, pathway=g.pathway, viability=g.viability,
                supporting_evidence=list(g.supporting_evidence or []),
                relevant_law_sections=list(g.relevant_law_sections or []),
                authorities=list(g.authorities or []),
                trial_finding=g.trial_finding, error_identified=g.error_identified,
                materiality=g.materiality, consequence=g.consequence,
                sub_particulars=list(g.sub_particulars or []),
                reasoning_trail=list(g.reasoning_trail or []) or None,
            )
            continue

        existing.viability = max_viability(existing.viability, g.viability)
        existing.supporting_evidence = dedupe_keep_order([*existing.supporting_evidence, *(g.supporting_evidence or [])])
        existing.relevant_law_sections = dedupe_keep_order([*existing.relevant_law_sections, *(g.relevant_law_sections or [])])
        existing.authorities = dedupe_keep_order([*existing.authorities, *(g.authorities or [])])
        existing.sub_particulars = list(existing.sub_particulars or []) + list(g.sub_particulars or [])

        if not existing.trial_finding and g.trial_finding:
            existing.trial_finding = g.trial_finding
        if not existing.error_identified and g.error_identified:
            existing.error_identified = g.error_identified
        if not existing.materiality and g.materiality:
            existing.materiality = g.materiality
        if not existing.consequence and g.consequence:
            existing.consequence = g.consequence

        # Preserve the combined reasoning trail from both grounds — counsel
        # needs to see why each merge happened.
        if g.reasoning_trail:
            existing.reasoning_trail = (existing.reasoning_trail or []) + [
                f"Merged with duplicate ground '{g.title}'."
            ] + list(g.reasoning_trail)

    return list(merged.values())


def apply_viability_caps(ground: Ground, flags: EvidenceFlags) -> Ground:
    title_blob = normalise(ground.title + " " + (ground.error_identified or ""))

    if ground.type == "ineffective_counsel":
        if not (flags.counsel_affidavit or flags.transcript_support):
            ground.viability = cap_viability(ground.viability, "arguable_moderate")

    if ground.type == "sentence":
        if not flags.sentencing_remarks:
            ground.viability = cap_viability(ground.viability, "requires_development")

    if ground.type == "procedure":
        if any(x in title_blob for x in ("jury", "juror", "partiality", "misconduct")) and not flags.juror_affidavit:
            ground.viability = cap_viability(ground.viability, "requires_development")
        if any(x in title_blob for x in ("judge-alone", "judge alone", "mode of trial")) and not flags.judge_alone_application_material:
            ground.viability = cap_viability(ground.viability, "arguable_moderate")
        if any(x in title_blob for x in ("pretrial publicity", "pre-trial publicity")) and not flags.pretrial_publicity_material:
            ground.viability = cap_viability(ground.viability, "requires_development")

    if ground.type == "conviction":
        if any(x in title_blob for x in ("mens rea", "mental state", "substantial impairment", "mental impairment", "psychiatric")) and not flags.psychiatric_reports:
            ground.viability = cap_viability(ground.viability, "arguable_moderate")

    return ground


def validate_ground_integrity(ground: Ground) -> None:
    text = blob_for_ground(ground)

    if ground.type == "conviction":
        if any(x in text for x in ("rehabilitation", "manifestly excessive", "manifest excess", "non-parole", "parole")):
            raise ValueError(f"Conviction ground contains sentencing content: {ground.title}")

    if ground.type == "sentence":
        if any(x in text for x in ("unsafe verdict", "mens rea", "intent", "mental impairment defence", "substantial impairment")):
            raise ValueError(f"Sentence ground contains liability content: {ground.title}")


def auto_repair_integrity(ground: Ground, jurisdiction: str) -> list[Ground]:
    try:
        validate_ground_integrity(ground)
        return [ground]
    except ValueError:
        synthetic_subs: list[SubParticular] = []
        for label, text in [
            ("trial_finding", ground.trial_finding or ""),
            ("error_identified", ground.error_identified or ""),
            ("materiality", ground.materiality or ""),
            ("consequence", ground.consequence or ""),
        ]:
            if text.strip():
                synthetic_subs.append(SubParticular(label=label, text=text))
        for idx, item in enumerate(ground.supporting_evidence or [], start=1):
            synthetic_subs.append(SubParticular(label=f"support_{idx}", text=item))
        for idx, item in enumerate(ground.relevant_law_sections or [], start=1):
            synthetic_subs.append(SubParticular(label=f"law_{idx}", text=item))

        repaired = Ground(
            title=ground.title, type=ground.type, pathway=ground.pathway, viability=ground.viability,
            supporting_evidence=ground.supporting_evidence,
            relevant_law_sections=ground.relevant_law_sections,
            authorities=ground.authorities,
            trial_finding=ground.trial_finding, error_identified=ground.error_identified,
            materiality=ground.materiality, consequence=ground.consequence,
            sub_particulars=synthetic_subs,
        )
        return split_mixed_ground(repaired, jurisdiction)


def sort_grounds(grounds: list[Ground]) -> list[Ground]:
    return sorted(
        grounds,
        key=lambda g: (
            TYPE_PRIORITY.get(g.type or "sentence", 99),
            -VIABILITY_ORDER[g.viability],
            normalise(g.title),
        ),
    )


def normalise_generated_grounds(
    raw_grounds: list[Ground],
    flags: EvidenceFlags,
    jurisdiction: str,
) -> list[Ground]:
    processed: list[Ground] = []

    for raw in raw_grounds:
        initial = split_mixed_ground(raw, jurisdiction)
        repaired: list[Ground] = []
        for g in initial:
            repaired.extend(auto_repair_integrity(g, jurisdiction))
        for g in repaired:
            if g.type is None:
                g.type, reason = classify_text_with_reason(blob_for_ground(g), jurisdiction)
                _append_trail(g, f"Type was unset; reclassified — {reason}")
            g.pathway = infer_pathway(jurisdiction, g.type)
            g.supporting_evidence = dedupe_keep_order(g.supporting_evidence or [])
            g.relevant_law_sections = dedupe_keep_order(g.relevant_law_sections or [])
            g.authorities = dedupe_keep_order(g.authorities or [])
            prior_viability = g.viability
            g = apply_viability_caps(g, flags)
            if g.viability != prior_viability:
                _append_trail(g, f"Viability capped from '{prior_viability}' to '{g.viability}' due to missing corroborating evidence (see realism profile).")
            processed.append(g)

    merged = merge_duplicate_grounds(processed)

    for g in merged:
        try:
            validate_ground_integrity(g)
        except ValueError as ve:
            _append_trail(g, f"Integrity violation caught ({ve}); ground type force-reclassified from content.")
            g.type, reason = classify_text_with_reason(blob_for_ground(g), jurisdiction)
            g.pathway = infer_pathway(jurisdiction, g.type)
            _append_trail(g, reason)

    return sort_grounds(merged)


def ground_from_dict(data: dict) -> Ground:
    subs = [
        SubParticular(
            label=str(sp.get("label", "")),
            text=str(sp.get("text", "")),
            detected_type=sp.get("detected_type"),
        )
        for sp in data.get("sub_particulars", []) or []
    ]
    return Ground(
        title=str(data.get("title", "")),
        type=data.get("type"),
        pathway=str(data.get("pathway", "")),
        viability=data.get("viability", "requires_development"),
        supporting_evidence=list(data.get("supporting_evidence", []) or []),
        relevant_law_sections=list(data.get("relevant_law_sections", []) or []),
        authorities=list(data.get("authorities", []) or []),
        trial_finding=data.get("trial_finding"),
        error_identified=data.get("error_identified"),
        materiality=data.get("materiality"),
        consequence=data.get("consequence"),
        sub_particulars=subs,
        record_support=data.get("record_support"),
        verdict_robustness=data.get("verdict_robustness"),
        crown_strength=data.get("crown_strength"),
        failure_risk=data.get("failure_risk"),
        reasoning_trail=list(data.get("reasoning_trail", []) or []) or None,
    )


def ground_to_dict(ground: Ground) -> dict:
    return {
        "title": ground.title,
        "type": ground.type,
        "pathway": ground.pathway,
        "viability": ground.viability,
        "supporting_evidence": ground.supporting_evidence,
        "relevant_law_sections": ground.relevant_law_sections,
        "authorities": ground.authorities,
        "trial_finding": ground.trial_finding,
        "error_identified": ground.error_identified,
        "materiality": ground.materiality,
        "consequence": ground.consequence,
        "sub_particulars": [
            {"label": sp.label, "text": sp.text, "detected_type": sp.detected_type}
            for sp in (ground.sub_particulars or [])
        ],
        "record_support": getattr(ground, "record_support", None),
        "verdict_robustness": getattr(ground, "verdict_robustness", None),
        "crown_strength": getattr(ground, "crown_strength", None),
        "failure_risk": getattr(ground, "failure_risk", None),
        "reasoning_trail": getattr(ground, "reasoning_trail", None) or [],
    }
