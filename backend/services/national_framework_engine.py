"""
national_framework_engine.py

National jurisdiction-aware legal framework engine for Appeal Case Manager.

Purpose:
- Never default to NSW.
- Bind offence category + jurisdiction to the correct legislation.
- Add Commonwealth overlay only where relevant.
- Force mens rea / fault element analysis.
- Force appellate pathway, sentencing, evidence, and mental impairment context.
- Produce structured legal prompt context for AI report generation.

DO NOT place this inside /frameworks/.
This belongs in /app/backend/services/.
"""

from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
from typing import Any

from frameworks.offences import OFFENCE_CATEGORIES
from frameworks.jurisdictions import AUSTRALIAN_STATES
from frameworks.appeal import APPEAL_FRAMEWORK
from frameworks.sentencing import SENTENCING_FRAMEWORK
from frameworks.evidence import EVIDENCE_FRAMEWORK
from frameworks.mental_impairment import MENTAL_IMPAIRMENT_FRAMEWORK
from frameworks.procedure import MENS_REA_FRAMEWORK


VALID_JURISDICTIONS = {
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


CODE_JURISDICTIONS = {"qld", "wa", "tas", "nt", "act", "cth"}
COMMON_LAW_HYBRID_JURISDICTIONS = {"nsw", "vic", "sa"}


FEDERAL_TRIGGER_TERMS = {
    "terrorism",
    "carriage service",
    "online",
    "internet",
    "telecommunications",
    "commonwealth",
    "federal",
    "import",
    "export",
    "border",
    "airport",
    "customs",
    "child abuse material",
    "child exploitation material",
    "foreign",
    "money laundering",
    "public official",
    "commonwealth official",
    "tax",
    "centrelink",
    "medicare",
}


@dataclass(frozen=True)
class NationalFrameworkResult:
    jurisdiction: str
    offence_category: str
    offence_type: str | None
    context: str
    warnings: list[str]
    framework: dict[str, Any]


def normalise_jurisdiction(raw: str | None) -> str:
    """
    Converts user/app jurisdiction values into canonical internal keys.

    Raises:
        ValueError if missing or unsupported.
    """
    if not raw or not str(raw).strip():
        raise ValueError(
            "JURISDICTION NOT SET — legal analysis must not proceed and must not default to NSW."
        )

    key = str(raw).strip().lower()
    mapped = VALID_JURISDICTIONS.get(key)

    if not mapped:
        raise ValueError(
            f"Unsupported jurisdiction '{raw}'. Valid values are NSW, VIC, QLD, SA, WA, TAS, NT, ACT, CTH/Federal/Commonwealth."
        )

    return mapped


def normalise_offence_category(raw: str | None) -> str:
    if not raw or not str(raw).strip():
        raise ValueError("OFFENCE CATEGORY NOT SET — legal analysis must not proceed.")

    key = str(raw).strip().lower()

    aliases = {
        "murder": "homicide",
        "manslaughter": "homicide",
        "homicide": "homicide",
        "rape": "sexual_offences",
        "sexual assault": "sexual_offences",
        "sex": "sexual_offences",
        "armed robbery": "robbery_theft",
        "robbery": "robbery_theft",
        "theft": "robbery_theft",
        "larceny": "robbery_theft",
        "drugs": "drug_offences",
        "drug": "drug_offences",
        "fraud": "fraud_dishonesty",
        "dishonesty": "fraud_dishonesty",
        "firearms": "firearms_weapons",
        "weapons": "firearms_weapons",
        "dv": "domestic_violence",
        "domestic violence": "domestic_violence",
        "terrorism": "terrorism",
        "driving": "driving_offences",
        "arson": "arson_property_damage",
        "cyber": "cybercrime",
        "perjury": "perjury_justice_offences",
        "blackmail": "extortion_blackmail",
        "extortion": "extortion_blackmail",
        "organised crime": "organised_crime",
        "child exploitation": "child_exploitation_material",
        "corruption": "corruption_public_officials",
    }

    key = aliases.get(key, key)

    if key not in OFFENCE_CATEGORIES:
        raise ValueError(f"Unsupported offence category '{raw}'.")

    return key


def offence_legislation_key(jurisdiction: str) -> str:
    if jurisdiction == "cth":
        return "cth_legislation"
    return f"{jurisdiction}_legislation"


def get_category(category_key: str) -> dict[str, Any]:
    category = OFFENCE_CATEGORIES.get(category_key)
    if not category:
        raise ValueError(f"No offence framework found for category '{category_key}'.")
    return category


def get_jurisdiction_name(jurisdiction: str) -> str:
    if jurisdiction == "cth":
        return "Commonwealth / Federal"
    return AUSTRALIAN_STATES.get(jurisdiction, {}).get("name", jurisdiction.upper())


def get_jurisdiction_abbreviation(jurisdiction: str) -> str:
    if jurisdiction == "cth":
        return "Cth"
    return AUSTRALIAN_STATES.get(jurisdiction, {}).get("abbreviation", jurisdiction.upper())


def get_offence_legislation(category_key: str, jurisdiction: str) -> dict[str, list[dict[str, str]]]:
    category = get_category(category_key)
    key = offence_legislation_key(jurisdiction)
    legislation = category.get(key)

    if not legislation:
        raise ValueError(
            f"No {jurisdiction.upper()} legislation mapped for offence category '{category_key}'."
        )

    return legislation


def should_apply_commonwealth_overlay(case: dict[str, Any], category_key: str, jurisdiction: str) -> bool:
    if jurisdiction == "cth":
        return True

    category = get_category(category_key)

    if category_key in {
        "terrorism",
        "cybercrime",
        "child_exploitation_material",
        "corruption_public_officials",
    }:
        return True

    searchable = " ".join(
        str(case.get(k, ""))
        for k in (
            "title",
            "summary",
            "offence_type",
            "facts",
            "description",
            "case_number",
            "court",
        )
    ).lower()

    return any(term in searchable for term in FEDERAL_TRIGGER_TERMS) and bool(
        category.get("cth_legislation")
    )


def render_legislation_block(title: str, legislation: dict[str, list[dict[str, str]]]) -> str:
    lines = [title]

    for act, sections in legislation.items():
        lines.append(f"\n{act}:")
        for item in sections:
            section = item.get("section", "Unknown section")
            heading = item.get("title", "")
            lines.append(f"  - {section}: {heading}")

    return "\n".join(lines)


def render_commonwealth_overlay(case: dict[str, Any], category_key: str, jurisdiction: str) -> str:
    if not should_apply_commonwealth_overlay(case, category_key, jurisdiction):
        return (
            "\nCOMMONWEALTH OVERLAY:\n"
            "- No Commonwealth overlay has been triggered on the supplied case metadata.\n"
            "- Commonwealth law must only be applied if the record shows a federal jurisdictional hook."
        )

    category = get_category(category_key)
    cth_legislation = category.get("cth_legislation") or {}

    if not cth_legislation:
        return (
            "\nCOMMONWEALTH OVERLAY:\n"
            "- Commonwealth overlay was considered, but no offence-specific Commonwealth legislation is mapped for this category."
        )

    return render_legislation_block(
        "\nCOMMONWEALTH / FEDERAL OVERLAY:\n"
        "Apply these provisions only where the facts disclose a Commonwealth jurisdictional hook.",
        cth_legislation,
    )


@lru_cache(maxsize=128)
def render_offence_elements(category_key: str) -> str:
    category = get_category(category_key)

    lines = [
        "\nOFFENCE ELEMENTS:",
        f"- Category: {category.get('name', category_key)}",
        f"- Description: {category.get('description', '')}",
        "- Offences included:",
    ]

    for offence in category.get("offences", []):
        lines.append(f"  - {offence}")

    lines.append("- Key elements:")
    for element in category.get("key_elements", []):
        lines.append(f"  - {element}")

    lines.append("- Available defences:")
    for defence in category.get("defences", []):
        lines.append(f"  - {defence}")

    return "\n".join(lines)


@lru_cache(maxsize=128)
def render_mens_rea_framework(category_key: str, jurisdiction: str) -> str:
    category = get_category(category_key)
    mens_rea_keys = category.get("relevant_mens_rea", [])

    lines = [
        "\nMANDATORY MENS REA / FAULT ELEMENT ANALYSIS:",
        "- Identify each physical element of the charged offence.",
        "- Identify the fault element attached to each physical element.",
        "- Analyse whether the prosecution evidence could prove the required mental element beyond reasonable doubt.",
        "- Where psychiatric evidence, intoxication, automatism, mistake, cognitive impairment, or abnormal mental state appears, analyse its effect on intent, knowledge, recklessness, negligence, voluntariness, or criminal responsibility.",
    ]

    if jurisdiction == "cth":
        lines.extend(
            [
                "- Commonwealth offences require Criminal Code Act 1995 (Cth) Chapter 2 fault-element analysis.",
                "- Do not import State common law mens rea unless the statute or authority requires it.",
            ]
        )
    elif jurisdiction in CODE_JURISDICTIONS:
        lines.extend(
            [
                f"- {jurisdiction.upper()} is treated as a Code jurisdiction for offence-structure purposes.",
                "- Do not assume NSW common-law offence elements.",
                "- Apply the relevant Code text and any preserved common-law interpretive authority.",
            ]
        )
    elif jurisdiction in COMMON_LAW_HYBRID_JURISDICTIONS:
        lines.extend(
            [
                f"- {jurisdiction.upper()} is treated as a statutory/common-law hybrid jurisdiction.",
                "- Analyse both the statutory language and common-law principles where applicable.",
            ]
        )

    if category_key == "homicide":
        lines.extend(
            [
                "\nHOMICIDE-SPECIFIC MENS REA CONTROL:",
                "- For murder, identify the available mental element pathway: intent to kill, intent to cause grievous bodily harm, or reckless indifference / equivalent jurisdictional formulation.",
                "- Do not treat psychiatric evidence merely as mitigation if it goes to liability, intent, substantial impairment, diminished responsibility, mental impairment, automatism, or criminal responsibility.",
                "- If a partial defence is raised, classify it as a conviction/liability issue, not a sentence issue.",
            ]
        )

    for key in mens_rea_keys:
        entry = MENS_REA_FRAMEWORK.get(key)

        if not entry:
            lines.append(f"\n{key.upper()}:")
            lines.append("- Mapped in offence category but not found in MENS_REA_FRAMEWORK. Verify manually.")
            continue

        lines.append(f"\n{key.upper()}:")
        lines.append(f"- Definition: {entry.get('definition', '')}")

        authorities = entry.get("authorities", [])
        if authorities:
            lines.append("- Authorities:")
            for authority in authorities[:5]:
                lines.append(f"  - {authority}")

        applications = entry.get("application", [])
        if applications:
            lines.append("- Application:")
            for item in applications[:5]:
                lines.append(f"  - {item}")

    return "\n".join(lines)


@lru_cache(maxsize=32)
def render_appeal_framework(jurisdiction: str) -> str:
    key = "federal" if jurisdiction == "cth" else jurisdiction
    data = APPEAL_FRAMEWORK.get(key)

    lines = [f"\nAPPELLATE FRAMEWORK — {get_jurisdiction_name(jurisdiction)}:"]

    if not data:
        lines.append("- No appellate framework is mapped. The report must flag this for legal verification.")
        return "\n".join(lines)

    # Counsel feedback 23 Feb 2026: taxonomy uses "legislation" as the
    # governing-Act key; bridge spec uses "act". Accept either so every
    # jurisdiction's governing Act renders correctly.
    act_value = data.get("act") or data.get("legislation")
    if act_value:
        lines.append(f"- Act: {act_value}")

    for field in ("court", "time_limit", "test", "powers", "note"):
        value = data.get(field)
        if value:
            lines.append(f"- {field.replace('_', ' ').title()}: {value}")

    time_limits = data.get("time_limits") or {}
    if time_limits:
        lines.append("- Time limits:")
        for name, value in time_limits.items():
            lines.append(f"  - {name}: {value}")

    grounds = data.get("grounds") or data.get("appeal_grounds") or []
    if grounds:
        lines.append("- Appeal grounds:")
        for ground in grounds:
            lines.append(f"  - {ground}")

    return "\n".join(lines)


@lru_cache(maxsize=32)
def render_sentencing_framework(jurisdiction: str) -> str:
    key = "federal" if jurisdiction == "cth" else jurisdiction
    data = SENTENCING_FRAMEWORK.get(key)

    lines = [f"\nSENTENCING FRAMEWORK — {get_jurisdiction_name(jurisdiction)}:"]

    if not data:
        lines.append("- No sentencing framework is mapped. Sentencing issues must be flagged for legal verification.")
        return "\n".join(lines)

    if data.get("act"):
        lines.append(f"- Act: {data['act']}")

    for item in data.get("key_provisions", []):
        lines.append(f"  - {item}")

    for item in data.get("sentencing_appeal_grounds", []):
        lines.append(f"  - Sentencing appeal ground: {item}")

    if data.get("note"):
        lines.append(f"- Note: {data['note']}")

    if jurisdiction != "cth":
        federal_data = SENTENCING_FRAMEWORK.get("federal")
        if federal_data:
            lines.append("\nFEDERAL SENTENCING OVERLAY:")
            lines.append("- Applies only if the offence is federal or Commonwealth sentencing is otherwise engaged.")
            if federal_data.get("act"):
                lines.append(f"- Act: {federal_data['act']}")
            for item in federal_data.get("key_provisions", [])[:5]:
                lines.append(f"  - {item}")

    return "\n".join(lines)


@lru_cache(maxsize=32)
def render_evidence_framework(jurisdiction: str) -> str:
    key = "federal" if jurisdiction == "cth" else jurisdiction
    data = EVIDENCE_FRAMEWORK.get(key)

    lines = [f"\nEVIDENCE FRAMEWORK — {get_jurisdiction_name(jurisdiction)}:"]

    if not data:
        lines.append("- No evidence framework is mapped. Evidentiary issues must be flagged for legal verification.")
        return "\n".join(lines)

    if data.get("act"):
        lines.append(f"- Act: {data['act']}")

    if data.get("type"):
        lines.append(f"- Type: {data['type']}")

    for item in data.get("key_provisions", []):
        lines.append(f"  - {item}")

    for item in data.get("key_local_provisions", []):
        lines.append(f"  - Local provision: {item}")

    if data.get("note"):
        lines.append(f"- Note: {data['note']}")

    common = EVIDENCE_FRAMEWORK.get("common_evidence_appeal_grounds", [])
    if common:
        lines.append("- Common evidentiary appeal grounds:")
        for item in common:
            lines.append(f"  - {item}")

    return "\n".join(lines)


@lru_cache(maxsize=128)
def render_mental_impairment_framework(jurisdiction: str, category_key: str) -> str:
    key = "federal" if jurisdiction == "cth" else jurisdiction
    data = MENTAL_IMPAIRMENT_FRAMEWORK.get(key)

    lines = [
        f"\nMENTAL IMPAIRMENT / CRIMINAL RESPONSIBILITY — {get_jurisdiction_name(jurisdiction)}:"
    ]

    if not data:
        lines.append("- No mental impairment framework is mapped. Any mental state issue must be flagged for verification.")
        return "\n".join(lines)

    if isinstance(data, dict):
        for k, value in data.items():
            label = k.replace("_", " ").title()
            if isinstance(value, list):
                lines.append(f"- {label}:")
                for item in value:
                    lines.append(f"  - {item}")
            else:
                lines.append(f"- {label}: {value}")
    else:
        lines.append(f"- {data}")

    if category_key == "homicide":
        lines.extend(
            [
                "\nHOMICIDE MENTAL STATE CONTROL:",
                "- If substantial impairment, diminished responsibility, mental impairment, unsoundness of mind, automatism, or intoxication is raised, identify whether it goes to liability, intent, partial defence, complete defence, or sentence.",
                "- Do not describe a liability-stage partial defence as mere mitigation.",
                "- Where expert psychiatric evidence conflicts, identify the exact forensic question: intent, capacity, control, appreciation of wrongfulness, voluntariness, or causal intoxication.",
            ]
        )

    return "\n".join(lines)


@lru_cache(maxsize=128)
def render_procedural_flow(category_key: str) -> str:
    category = get_category(category_key)
    flow = category.get("procedural_flow") or []

    lines = ["\nPROCEDURAL PIPELINE:"]

    if not flow:
        lines.append("- No procedural flow is mapped.")
        return "\n".join(lines)

    for stage in flow:
        if isinstance(stage, dict):
            number = stage.get("stage", "")
            name = stage.get("name", "")
            description = stage.get("description", "")
            lines.append(f"- Stage {number}: {name} — {description}")
            considerations = stage.get("forensic_considerations") or []
            for item in considerations[:3]:
                lines.append(f"  - Forensic focus: {item}")
        else:
            lines.append(f"- {stage}")

    return "\n".join(lines)


def render_record_integrity_rules() -> str:
    return """
RECORD INTEGRITY RULES:
- Each proposed ground must be tied to the trial record, sentencing remarks, transcript, exhibit, affidavit, expert report, or identified missing material.
- Distinguish transcript-supported error from inference and from extra-curial allegation.
- If a point depends on material outside the record, classify it as requiring affidavit, fresh evidence, or further investigation.
- Do not state that a ground is strong unless the record support is strong.
- Jury misconduct, ineffective counsel, fresh evidence, and post-trial information require special evidentiary caution.
"""


def render_ground_classification_rules() -> str:
    return """
GROUND CLASSIFICATION RULES:
- Classify each ground as conviction, sentence, procedure, evidence, fresh evidence, or ineffective counsel.
- Do not merge conviction and sentence grounds.
- Do not merge partial-defence liability issues with sentencing mitigation.
- For homicide, prioritise mens rea and criminal responsibility before sentence.
- For evidentiary issues, identify whether the complaint affects admissibility, probative value, prejudicial effect, directions, fairness, or verdict safety.
- For sentence appeals, identify specific error, House error, manifest excess/inadequacy, parity, totality, moral culpability, or statutory misapplication.
- For procedural issues, identify whether the defect creates unfairness, apparent bias, jury irregularity, denial of fair trial, or miscarriage of justice.
- For ineffective counsel, mark the ground as contingent unless supported by transcript, affidavit, or objective record material.
"""


def render_no_hallucination_rules(jurisdiction: str) -> str:
    return f"""
NO-HALLUCINATION / JURISDICTION FIDELITY RULES:
- The selected jurisdiction is {jurisdiction.upper()}.
- Do not cite NSW legislation unless the selected jurisdiction is NSW or a genuine cross-jurisdiction comparison is being made.
- Cite full Act name, year, and jurisdiction.
- Do not invent section numbers, case names, judges, dates, sentences, or appeal outcomes.
- If authority is uncertain, write: "citation requires verification".
- If jurisdiction is uncertain, stop legal conclusion generation and request correction in the app UI.
- Commonwealth legislation may only be applied where the case is federal/CTH or a Commonwealth overlay is triggered by the record.
"""


def build_framework_dict(case: dict[str, Any]) -> dict[str, Any]:
    jurisdiction = normalise_jurisdiction(case.get("state") or case.get("jurisdiction"))
    category_key = normalise_offence_category(case.get("offence_category"))

    category = get_category(category_key)
    offence_legislation = get_offence_legislation(category_key, jurisdiction)

    framework = {
        "jurisdiction": jurisdiction,
        "jurisdiction_name": get_jurisdiction_name(jurisdiction),
        "jurisdiction_abbreviation": get_jurisdiction_abbreviation(jurisdiction),
        "offence_category": category_key,
        "offence_category_name": category.get("name"),
        "offence_type": case.get("offence_type"),
        "offence_legislation": offence_legislation,
        "commonwealth_overlay_applies": should_apply_commonwealth_overlay(
            case, category_key, jurisdiction
        ),
        "appeal_framework": APPEAL_FRAMEWORK.get("federal" if jurisdiction == "cth" else jurisdiction),
        "sentencing_framework": SENTENCING_FRAMEWORK.get("federal" if jurisdiction == "cth" else jurisdiction),
        "evidence_framework": EVIDENCE_FRAMEWORK.get("federal" if jurisdiction == "cth" else jurisdiction),
        "mental_impairment_framework": MENTAL_IMPAIRMENT_FRAMEWORK.get("federal" if jurisdiction == "cth" else jurisdiction),
        "mens_rea_keys": category.get("relevant_mens_rea", []),
        "defences": category.get("defences", []),
        "key_elements": category.get("key_elements", []),
    }

    return framework


def validate_framework_completeness(framework: dict[str, Any]) -> list[str]:
    warnings: list[str] = []

    jurisdiction = framework["jurisdiction"]
    category = framework["offence_category"]

    if not framework.get("offence_legislation"):
        warnings.append(f"No offence legislation mapped for {jurisdiction.upper()} / {category}.")

    if not framework.get("appeal_framework"):
        warnings.append(f"No appeal framework mapped for {jurisdiction.upper()}.")

    if not framework.get("sentencing_framework"):
        warnings.append(f"No sentencing framework mapped for {jurisdiction.upper()}.")

    if not framework.get("evidence_framework"):
        warnings.append(f"No evidence framework mapped for {jurisdiction.upper()}.")

    if category == "homicide" and not framework.get("mental_impairment_framework"):
        warnings.append(f"No mental impairment framework mapped for homicide in {jurisdiction.upper()}.")

    if not framework.get("mens_rea_keys"):
        warnings.append(f"No mens rea keys mapped for offence category {category}.")

    return warnings


def build_national_case_context(case: dict[str, Any]) -> str:
    """
    Main prompt-context builder.

    Use inside offence_helpers.get_offence_context(case).
    """
    framework = build_framework_dict(case)
    warnings = validate_framework_completeness(framework)

    jurisdiction = framework["jurisdiction"]
    category_key = framework["offence_category"]

    lines = [
        "\n\n============================================================",
        "NATIONAL JURISDICTION-COMPLETE FRAMEWORK ENGINE",
        "============================================================",
        f"Jurisdiction: {framework['jurisdiction_name']} ({framework['jurisdiction_abbreviation']})",
        f"Offence category: {framework['offence_category_name']} ({category_key})",
        f"Specific offence: {framework.get('offence_type') or 'Not specified'}",
        "",
        render_legislation_block(
            f"PRIMARY OFFENCE LEGISLATION — {framework['jurisdiction_abbreviation']}:",
            framework["offence_legislation"],
        ),
        render_commonwealth_overlay(case, category_key, jurisdiction),
        render_offence_elements(category_key),
        render_mens_rea_framework(category_key, jurisdiction),
        render_mental_impairment_framework(jurisdiction, category_key),
        render_appeal_framework(jurisdiction),
        render_sentencing_framework(jurisdiction),
        render_evidence_framework(jurisdiction),
        render_procedural_flow(category_key),
        render_record_integrity_rules(),
        render_ground_classification_rules(),
        render_no_hallucination_rules(jurisdiction),
    ]

    if warnings:
        lines.append("\nFRAMEWORK COMPLETENESS WARNINGS:")
        for warning in warnings:
            lines.append(f"- {warning}")

    return "\n".join(lines)


def build_national_framework_result(case: dict[str, Any]) -> NationalFrameworkResult:
    framework = build_framework_dict(case)
    warnings = validate_framework_completeness(framework)
    context = build_national_case_context(case)

    return NationalFrameworkResult(
        jurisdiction=framework["jurisdiction"],
        offence_category=framework["offence_category"],
        offence_type=framework.get("offence_type"),
        context=context,
        warnings=warnings,
        framework=framework,
    )


# ---------------------------------------------------------------------------
# COUNSEL REFACTOR 24 Feb 2026 — PROMPT-INJECTION COMPAT LAYER.
#
# The following five functions were previously defined in
# services/national_framework.py. They are the summary-level prompt-injection
# API that report_generator.py and the counsel test suite have always called.
#
# Per counsel's 7-task refactor brief, all prompt-building responsibility now
# lives in this engine file. The wrapper services/national_framework.py is
# kept as a thin re-export shim so any external caller continues to work.
#
# DATA SOURCE: These functions read from the legacy NATIONAL_CRIMINAL_FRAMEWORK
# matrix preserved in services/national_framework.py. That matrix is the
# counsel-approved one-line-per-topic summary for every jurisdiction
# (appellate_act / appellate_test / mens_rea_source / mental_impairment /
# sentencing / evidence / proviso). The detailed multi-section framework
# rendering lives in build_national_case_context() above and is backed by
# frameworks/*.py. Two complementary surfaces, one source of truth each.
#
# NO SILENT NSW DEFAULT. Any unknown/missing jurisdiction returns an explicit
# ERROR string or None — callers surface that upstream so the LLM never
# silently falls back to NSW law on a SA/WA/NT/CTH matter.
# ---------------------------------------------------------------------------

_FEDERAL_MATRIX_ALIASES = {"cth", "commonwealth", "federal"}


def _load_national_matrix() -> dict[str, dict]:
    """
    Lazy accessor for the counsel-approved summary matrix. Lazy import is
    required because services.national_framework imports FROM this engine
    module at load time; resolving NATIONAL_CRIMINAL_FRAMEWORK at call time
    (rather than module-load time) avoids a circular import while keeping
    the matrix physically preserved in the compatibility wrapper.
    """
    from services.national_framework import NATIONAL_CRIMINAL_FRAMEWORK

    return NATIONAL_CRIMINAL_FRAMEWORK


def get_jurisdiction_framework(state: str | None) -> dict | None:
    """
    Returns the counsel-approved summary matrix row for the supplied
    jurisdiction, or None if the jurisdiction is missing / unrecognised.

    Accepts every counsel-approved input: NSW, VIC, QLD, SA, WA, TAS, NT,
    ACT plus cth / commonwealth / federal (case-insensitive; all three
    federal aliases resolve to the SAME 'federal' row — identity preserved,
    so `get_jurisdiction_framework('cth') is get_jurisdiction_framework('federal')`).

    Does NOT raise. Callers rely on None to surface explicit ERROR strings
    upstream (no silent NSW fallback).
    """
    if state is None:
        return None

    key = str(state).strip().lower()
    if not key:
        return None

    if key in _FEDERAL_MATRIX_ALIASES:
        key = "federal"

    return _load_national_matrix().get(key)


def build_national_appellate_context(state: str | None) -> str:
    """
    Human-readable jurisdiction-accurate appellate-framework block for
    injection at the TOP of every LLM prompt. No silent NSW default.
    """
    fw = get_jurisdiction_framework(state)
    if fw is None:
        return (
            "ERROR: Jurisdiction must be specified before analysis. "
            "No silent NSW default is permitted under the National Criminal Framework."
        )

    display_state = (state or "").upper().strip()
    if display_state in {"CTH", "COMMONWEALTH"}:
        display_state = "FEDERAL"

    lines = [
        f"APPELLATE FRAMEWORK — {display_state}:",
        "",
        "GOVERNING ACT:",
        fw["appellate_act"],
        "",
        "CORE APPELLATE TESTS:",
    ]
    for test in fw["appellate_test"]:
        lines.append(f"- {test}")

    lines += [
        "",
        "MENS REA SOURCE:",
        f"- {fw['mens_rea_source']}",
        "",
        "MENTAL IMPAIRMENT REGIME:",
        f"- {fw['mental_impairment']}",
        "",
        "SENTENCING FRAMEWORK:",
        f"- {fw['sentencing']}",
        "",
        "EVIDENCE FRAMEWORK:",
        f"- {fw['evidence']}",
    ]

    if fw.get("proviso"):
        lines.append("")
        lines.append(
            "PROVISO APPLIES: Court may dismiss appeal if no substantial "
            "miscarriage of justice."
        )

    return "\n".join(lines)


def build_mens_rea_analysis_block(offence: str | None) -> str:
    """
    Mandatory mens rea operationaliser — drilled into every brief prompt
    regardless of jurisdiction. Forces the LLM to identify fault elements,
    test them against prosecution evidence, and consider the impact of
    intoxication / psychiatric evidence on intent / capacity / voluntariness,
    plus alternative-verdict availability.
    """
    offence = (offence or "the offence").strip() or "the offence"
    return (
        "MANDATORY MENS REA ANALYSIS:\n"
        "\n"
        f"- Identify the fault elements required for {offence}\n"
        "- Assess whether prosecution evidence established those elements beyond reasonable doubt\n"
        "- Where intoxication or psychiatric evidence exists:\n"
        "    - assess impact on intent\n"
        "    - assess capacity to reason\n"
        "    - assess voluntariness\n"
        "- Determine whether an alternative verdict (e.g. manslaughter) was reasonably open\n"
    )


def build_record_integrity_block() -> str:
    """
    Record vs speculation enforcer — forces the LLM to distinguish
    transcript-supported error from inference or extra-curial allegation,
    and to treat off-record issues as fresh evidence questions.
    """
    return (
        "RECORD INTEGRITY RULE:\n"
        "\n"
        "- Identify whether each alleged error appears on the trial record\n"
        "- If not on record → classify as fresh evidence issue\n"
        "- Distinguish:\n"
        "    (a) transcript-supported error\n"
        "    (b) inference from conduct\n"
        "    (c) extra-curial allegation\n"
    )


def build_full_system_prompt(case: dict) -> str:
    """
    Full system-prompt injection counsel requires.

    - Refuses to analyse without a jurisdiction (returns an explicit ERROR
      string so the LLM cannot silently proceed on an NSW default).
    - Injects the national framework + mens rea operationaliser + record
      integrity rule.
    - Mandatory analysis structure + hard DO-NOT rules.
    """
    state = case.get("state") or case.get("jurisdiction")
    offence = case.get("offence_type") or case.get("offence_category") or "offence"

    if not state:
        return "ERROR: Jurisdiction must be specified before analysis."

    fw = get_jurisdiction_framework(state)
    if fw is None:
        return (
            f"ERROR: Unknown jurisdiction '{state}'. Must be one of: "
            f"{', '.join(sorted(_load_national_matrix().keys()))}."
        )

    return (
        f"{build_national_appellate_context(state)}\n"
        f"\n"
        f"{build_mens_rea_analysis_block(offence)}\n"
        f"\n"
        f"{build_record_integrity_block()}\n"
        f"\n"
        "MANDATORY ANALYSIS STRUCTURE:\n"
        "\n"
        "1. Identify alleged legal error\n"
        "2. Link error to appellate test\n"
        "3. Assess evidentiary support\n"
        "4. Consider Crown counterargument\n"
        "5. Apply proviso where relevant\n"
        "\n"
        "DO NOT:\n"
        "- Default to NSW\n"
        "- Assume uniform law\n"
        "- Predict success\n"
        "- Invent authority\n"
    )
