"""
national_framework.py

Unified National Criminal Framework engine — counsel feedback 23 Feb 2026.

Purpose: inject a jurisdiction-accurate, state-by-state appellate context
into every LLM prompt. Refuses to generate analysis without a jurisdiction
(no silent NSW default). Operationalises mens rea, mental impairment,
sentencing, and evidence regimes per jurisdiction.

This module is designed to work alongside services/offence_helpers.py
(which already provides rich offence-specific context) and the
services/jurisdiction_rules.py classifier rules. It adds the
national-framework CONTEXT BLOCK that the LLM sees at the top of its
prompt so it cannot default across jurisdictions.
"""

from __future__ import annotations

from typing import Optional


# ---------------------------------------------------------------------------
# MASTER JURISDICTION MATRIX — counsel supplied, authoritative.
# ---------------------------------------------------------------------------
NATIONAL_CRIMINAL_FRAMEWORK: dict[str, dict] = {
    "nsw": {
        "appellate_act": "Criminal Appeal Act 1912 (NSW)",
        "appellate_test": [
            "s 6(1): unreasonable verdict",
            "s 6(1): error of law",
            "s 6(1): miscarriage of justice",
            "Proviso: no substantial miscarriage",
        ],
        "mens_rea_source": "Crimes Act 1900 (NSW) s 18",
        "mental_impairment": "Crimes Act 1900 (NSW) s 23A",
        "sentencing": "Crimes (Sentencing Procedure) Act 1999 (NSW)",
        "evidence": "Evidence Act 1995 (NSW) (Uniform Evidence Law)",
        "proviso": True,
    },
    "vic": {
        "appellate_act": "Criminal Procedure Act 2009 (VIC)",
        "appellate_test": [
            "s 276: unsafe and unsatisfactory verdict",
            "error of law",
            "miscarriage of justice",
        ],
        "mens_rea_source": "Crimes Act 1958 (VIC)",
        "mental_impairment": "Crimes (Mental Impairment and Unfitness to be Tried) Act 1997 (VIC)",
        "sentencing": "Sentencing Act 1991 (VIC)",
        "evidence": "Evidence Act 2008 (VIC) (Uniform Evidence Law)",
        "proviso": True,
    },
    "qld": {
        "appellate_act": "Criminal Code (Qld) + Criminal Practice Rules",
        "appellate_test": [
            "unsafe or unsatisfactory verdict",
            "error of law",
            "miscarriage of justice",
        ],
        "mens_rea_source": "Criminal Code Act 1899 (Qld)",
        "mental_impairment": "Criminal Code (Qld) s 27",
        "sentencing": "Penalties and Sentences Act 1992 (Qld)",
        "evidence": "Evidence Act 1977 (Qld)",
        "proviso": True,
    },
    "wa": {
        "appellate_act": "Criminal Appeals Act 2004 (WA)",
        "appellate_test": [
            "miscarriage of justice",
            "error of law",
            "unsafe verdict",
        ],
        "mens_rea_source": "Criminal Code Act Compilation Act 1913 (WA)",
        "mental_impairment": "Criminal Code (WA) s 27",
        "sentencing": "Sentencing Act 1995 (WA)",
        "evidence": "Evidence Act 1906 (WA)",
        "proviso": True,
    },
    "sa": {
        "appellate_act": "Criminal Appeal Act 1939 (SA)",
        "appellate_test": [
            "miscarriage of justice",
            "error of law",
        ],
        "mens_rea_source": "Criminal Law Consolidation Act 1935 (SA)",
        "mental_impairment": "Mental Impairment Act 1995 (SA)",
        "sentencing": "Sentencing Act 2017 (SA)",
        "evidence": "Evidence Act 1929 (SA)",
        "proviso": True,
    },
    "tas": {
        "appellate_act": "Criminal Code Act 1924 (TAS)",
        "appellate_test": [
            "miscarriage of justice",
            "error of law",
        ],
        "mens_rea_source": "Criminal Code Act 1924 (TAS)",
        "mental_impairment": "Criminal Code (TAS) s 16",
        "sentencing": "Sentencing Act 1997 (TAS)",
        "evidence": "Evidence Act 2001 (TAS)",
        "proviso": True,
    },
    "nt": {
        "appellate_act": "Criminal Code Act 1983 (NT)",
        "appellate_test": [
            "miscarriage of justice",
            "error of law",
        ],
        "mens_rea_source": "Criminal Code (NT)",
        "mental_impairment": "Criminal Code (NT)",
        "sentencing": "Sentencing Act 1995 (NT)",
        "evidence": "Evidence (National Uniform Legislation) Act 2011 (NT)",
        "proviso": True,
    },
    "act": {
        "appellate_act": "Crimes (Appeal and Review) Act 2001 (ACT)",
        "appellate_test": [
            "miscarriage of justice",
            "error of law",
        ],
        "mens_rea_source": "Criminal Code 2002 (ACT)",
        "mental_impairment": "Criminal Code (ACT)",
        "sentencing": "Crimes (Sentencing) Act 2005 (ACT)",
        "evidence": "Evidence Act 2011 (ACT) (Uniform)",
        "proviso": True,
    },
    "federal": {
        "appellate_act": "Judiciary Act 1903 (Cth)",
        "appellate_test": [
            "error of law",
            "miscarriage of justice",
            "special leave required (HCA)",
        ],
        "mens_rea_source": "Criminal Code Act 1995 (Cth) Chapter 2",
        "mental_impairment": "Criminal Code (Cth) Part 2.3",
        "sentencing": "Crimes Act 1914 (Cth) Part IB",
        "evidence": "Evidence Act 1995 (Cth)",
        "proviso": True,
    },
}


def get_jurisdiction_framework(state: Optional[str]) -> Optional[dict]:
    """
    Resolve a jurisdiction key to its framework row. Accepts lowercase or
    uppercase, with federal / commonwealth / cth all mapping to the federal
    entry. Returns None if the key is missing or unknown — callers must
    treat None as a hard failure (no silent NSW default).
    """
    if not state:
        return None
    k = str(state).strip().lower()
    # Normalise variants of "federal".
    if k in {"cth", "commonwealth"}:
        k = "federal"
    return NATIONAL_CRIMINAL_FRAMEWORK.get(k)


def build_national_appellate_context(state: Optional[str]) -> str:
    """
    Human-readable jurisdiction-accurate appellate-framework block for
    injection at the top of every LLM prompt.
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

    if fw["proviso"]:
        lines.append("")
        lines.append(
            "PROVISO APPLIES: Court may dismiss appeal if no substantial "
            "miscarriage of justice."
        )

    return "\n".join(lines)


def build_mens_rea_analysis_block(offence: Optional[str]) -> str:
    """
    Mandatory mens rea operationaliser — drilled into every brief prompt
    regardless of jurisdiction. Forces the LLM to identify fault elements,
    test them against prosecution evidence, and consider the full impact of
    intoxication / psychiatric evidence on intent / capacity / voluntariness,
    and alternative-verdict availability.
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
            f"{', '.join(sorted(NATIONAL_CRIMINAL_FRAMEWORK.keys()))}."
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
