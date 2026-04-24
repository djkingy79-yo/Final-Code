"""
national_framework_engine.py

Jurisdiction-complete bridge layer.

Purpose:
- never default to NSW
- bind offence category to the correct state/territory/Commonwealth law
- inject appellate, mens rea, sentencing, evidence and record-integrity rules

Counsel feedback 23 Feb 2026 — bridge between the offence taxonomy and
the report generator so every prompt operates through the correct
jurisdiction before the AI writes anything.
"""

from __future__ import annotations

from functools import lru_cache

from offence_framework import (
    OFFENCE_CATEGORIES,
    AUSTRALIAN_STATES,  # noqa: F401 — re-exported for callers
    APPEAL_FRAMEWORK,
    SENTENCING_FRAMEWORK,
    EVIDENCE_FRAMEWORK,
    MENTAL_IMPAIRMENT_FRAMEWORK,
    MENS_REA_FRAMEWORK,
)


STATE_ALIASES = {
    "nsw": "nsw",
    "new south wales": "nsw",
    "vic": "vic",
    "victoria": "vic",
    "qld": "qld",
    "queensland": "qld",
    "sa": "sa",
    "south australia": "sa",
    "wa": "wa",
    "western australia": "wa",
    "tas": "tas",
    "tasmania": "tas",
    "nt": "nt",
    "northern territory": "nt",
    "act": "act",
    "australian capital territory": "act",
    "cth": "cth",
    "commonwealth": "cth",
    "federal": "cth",
}


def normalise_jurisdiction(state: str | None) -> str:
    if not state:
        raise ValueError("JURISDICTION NOT SET — analysis must not proceed.")

    key = str(state).strip().lower()
    mapped = STATE_ALIASES.get(key)

    if not mapped:
        raise ValueError(f"Unsupported jurisdiction: {state}")

    return mapped


def offence_legislation_key(jurisdiction: str) -> str:
    if jurisdiction == "cth":
        return "cth_legislation"
    return f"{jurisdiction}_legislation"


def get_offence_category(category_key: str) -> dict:
    category = OFFENCE_CATEGORIES.get(category_key)
    if not category:
        raise ValueError(f"Invalid offence category: {category_key}")
    return category


def get_jurisdiction_legislation(category_key: str, jurisdiction: str) -> dict:
    category = get_offence_category(category_key)
    key = offence_legislation_key(jurisdiction)

    legislation = category.get(key)
    if not legislation:
        raise ValueError(
            f"No {jurisdiction.upper()} legislation mapped for offence category '{category_key}'."
        )

    return legislation


def render_legislation_block(category_key: str, jurisdiction: str) -> str:
    return _render_legislation_block_cached(category_key, jurisdiction)


@lru_cache(maxsize=128)
def _render_legislation_block_cached(category_key: str, jurisdiction: str) -> str:
    legislation = get_jurisdiction_legislation(category_key, jurisdiction)

    out = [f"RELEVANT {jurisdiction.upper()} OFFENCE LEGISLATION:"]
    for act, sections in legislation.items():
        out.append(f"\n{act}:")
        for item in sections:
            out.append(f"  - {item.get('section')}: {item.get('title')}")

    return "\n".join(out)


def render_commonwealth_overlay(category_key: str, jurisdiction: str) -> str:
    return _render_commonwealth_overlay_cached(category_key, jurisdiction)


@lru_cache(maxsize=128)
def _render_commonwealth_overlay_cached(category_key: str, jurisdiction: str) -> str:
    if jurisdiction == "cth":
        return ""

    category = get_offence_category(category_key)
    cth_legislation = category.get("cth_legislation") or {}

    if not cth_legislation:
        return ""

    out = [
        "\nCOMMONWEALTH OVERLAY:",
        "Commonwealth provisions are only to be applied where the case involves a federal offence, Commonwealth official, carriage service, import/export, federal property, or other federal jurisdictional hook.",
    ]

    for act, sections in cth_legislation.items():
        out.append(f"\n{act}:")
        for item in sections:
            out.append(f"  - {item.get('section')}: {item.get('title')}")

    return "\n".join(out)


@lru_cache(maxsize=32)
def render_appeal_framework(jurisdiction: str) -> str:
    key = "federal" if jurisdiction == "cth" else jurisdiction
    data = APPEAL_FRAMEWORK.get(key)

    if not data:
        return (
            f"\nAPPELLATE FRAMEWORK ({jurisdiction.upper()}):\n"
            "- No appellate framework is mapped. The report must flag this as requiring legal verification."
        )

    out = [f"\nAPPELLATE FRAMEWORK ({jurisdiction.upper()}):"]

    # Counsel feedback 23 Feb 2026: taxonomy uses "legislation" as the
    # governing-Act key; bridge spec uses "act". Accept either so the VIC
    # Criminal Procedure Act 2009 (and equivalents) render correctly.
    act_value = data.get("act") or data.get("legislation")
    if act_value:
        out.append(f"- Act: {act_value}")

    for field in ("court", "time_limit", "test", "powers", "note"):
        value = data.get(field)
        if value:
            out.append(f"- {field.replace('_', ' ').title()}: {value}")

    time_limits = data.get("time_limits") or {}
    if time_limits:
        out.append("- Time limits:")
        for name, value in time_limits.items():
            out.append(f"  - {name}: {value}")

    return "\n".join(out)


@lru_cache(maxsize=32)
def render_sentencing_framework(jurisdiction: str) -> str:
    key = "federal" if jurisdiction == "cth" else jurisdiction
    data = SENTENCING_FRAMEWORK.get(key)

    if not data:
        return (
            f"\nSENTENCING FRAMEWORK ({jurisdiction.upper()}):\n"
            "- No sentencing framework is mapped. Sentencing analysis must be flagged for verification."
        )

    out = [f"\nSENTENCING FRAMEWORK ({jurisdiction.upper()}):"]
    out.append(f"- Act: {data.get('act', 'Not mapped')}")

    for item in data.get("key_provisions", []):
        out.append(f"  - {item}")

    for item in data.get("sentencing_appeal_grounds", []):
        out.append(f"  - Appeal ground: {item}")

    if data.get("note"):
        out.append(f"- Note: {data['note']}")

    return "\n".join(out)


@lru_cache(maxsize=32)
def render_evidence_framework(jurisdiction: str) -> str:
    key = "federal" if jurisdiction == "cth" else jurisdiction
    data = EVIDENCE_FRAMEWORK.get(key)

    if not data:
        return (
            f"\nEVIDENCE FRAMEWORK ({jurisdiction.upper()}):\n"
            "- No evidence framework is mapped. Evidentiary grounds must be flagged for verification."
        )

    out = [f"\nEVIDENCE FRAMEWORK ({jurisdiction.upper()}):"]
    out.append(f"- Act: {data.get('act', 'Not mapped')}")

    if data.get("type"):
        out.append(f"- Type: {data['type']}")

    for item in data.get("key_provisions", []):
        out.append(f"  - {item}")

    for item in data.get("key_local_provisions", []):
        out.append(f"  - Local provision: {item}")

    if data.get("note"):
        out.append(f"- Note: {data['note']}")

    return "\n".join(out)


@lru_cache(maxsize=32)
def render_mental_impairment_framework(jurisdiction: str) -> str:
    key = "federal" if jurisdiction == "cth" else jurisdiction
    data = MENTAL_IMPAIRMENT_FRAMEWORK.get(key)

    if not data:
        return (
            f"\nMENTAL IMPAIRMENT / CRIMINAL RESPONSIBILITY ({jurisdiction.upper()}):\n"
            "- No mental impairment framework is mapped. Mental state issues must be flagged for verification."
        )

    out = [f"\nMENTAL IMPAIRMENT / CRIMINAL RESPONSIBILITY ({jurisdiction.upper()}):"]

    if isinstance(data, dict):
        for k, v in data.items():
            if isinstance(v, list):
                out.append(f"- {k.replace('_', ' ').title()}:")
                for item in v:
                    out.append(f"  - {item}")
            else:
                out.append(f"- {k.replace('_', ' ').title()}: {v}")
    else:
        out.append(f"- {data}")

    return "\n".join(out)


@lru_cache(maxsize=128)
def render_mens_rea_framework(category_key: str, jurisdiction: str) -> str:
    category = get_offence_category(category_key)
    keys = category.get("relevant_mens_rea") or []

    out = [
        f"\nMANDATORY MENS REA / FAULT ELEMENT ANALYSIS ({jurisdiction.upper()}):",
        "- Identify the physical elements of the offence.",
        "- Identify the fault element required for each physical element.",
        "- Assess whether the prosecution evidence could prove those elements beyond reasonable doubt.",
        "- Where psychiatric evidence, intoxication, automatism, mistake, or cognitive impairment appears, assess whether it affects intent, knowledge, recklessness, negligence, voluntariness, or criminal responsibility.",
    ]

    if jurisdiction == "cth":
        out.append("- Commonwealth offences require Criminal Code Act 1995 (Cth) Chapter 2 fault-element analysis. Do not import State common-law mens rea tests unless relevant to the trial court's reasoning.")
    elif jurisdiction in {"qld", "wa", "tas", "nt"}:
        out.append("- Code jurisdiction: apply the relevant Criminal Code structure and do not assume common-law offence elements unless preserved by authority.")
    else:
        out.append("- Common-law/statutory hybrid jurisdiction: analyse both statutory language and common-law principles where applicable.")

    for key in keys:
        entry = MENS_REA_FRAMEWORK.get(key)
        if not entry:
            out.append(f"- {key}: mapped in offence category but not found in MENS_REA_FRAMEWORK.")
            continue

        out.append(f"\n{key.upper()}:")
        out.append(f"- Definition: {entry.get('definition', '')}")
        for auth in entry.get("authorities", [])[:4]:
            out.append(f"  - Authority: {auth}")
        for app in entry.get("application", [])[:4]:
            out.append(f"  - Application: {app}")

    return "\n".join(out)


def render_record_integrity_rules() -> str:
    return """
RECORD INTEGRITY RULES:
- For each proposed ground, identify whether the error appears on the trial record.
- If the issue is not on the trial record, classify it as requiring fresh evidence or affidavit support.
- Distinguish transcript-supported error, documentary inference, and extra-curial allegation.
- Do not elevate speculation into a ground of appeal.
- Do not state that a ground is strong unless the record support is strong.
"""


def render_ground_decision_rules() -> str:
    return """
GROUND DECISION RULES:
- Link every ground to the governing appellate test for the selected jurisdiction.
- Classify each ground as conviction, sentence, procedure, evidence, or ineffective counsel.
- Do not merge conviction and sentence grounds.
- Do not describe partial defences or mental impairment liability issues as sentencing mitigation.
- For evidentiary issues, state whether the error affects verdict safety, trial fairness, or sentence.
- Apply proviso / no-substantial-miscarriage reasoning where applicable.
- Anticipate the Crown response.
- State the evidentiary gap that must be filled before the ground can be advanced.
"""


def build_national_case_context(case: dict) -> str:
    jurisdiction = normalise_jurisdiction(case.get("state") or case.get("jurisdiction"))
    category_key = case.get("offence_category") or "other"

    category = get_offence_category(category_key)

    out = [
        "NATIONAL JURISDICTION-COMPLETE LEGAL FRAMEWORK",
        f"Jurisdiction: {jurisdiction.upper()}",
        f"Offence Category: {category.get('name', category_key)}",
        f"Specific Offence: {case.get('offence_type') or 'Not specified'}",
        "",
        render_legislation_block(category_key, jurisdiction),
        render_commonwealth_overlay(category_key, jurisdiction),
        render_appeal_framework(jurisdiction),
        render_sentencing_framework(jurisdiction),
        render_evidence_framework(jurisdiction),
        render_mental_impairment_framework(jurisdiction),
        render_mens_rea_framework(category_key, jurisdiction),
        render_record_integrity_rules(),
        render_ground_decision_rules(),
    ]

    return "\n".join(out)
