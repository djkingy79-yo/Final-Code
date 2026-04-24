"""
national_framework.py — THIN COMPATIBILITY WRAPPER.

Historic file. All implementation now lives in
`services.national_framework_engine`, which sources its data from
`backend/frameworks/` (the single source of truth).

This wrapper is preserved so that any external caller that imports from
`services.national_framework` continues to work without modification.

Do not add new logic here. All new framework code belongs in
`national_framework_engine.py`.

Counsel refactor 24 Feb 2026: wrapper shrunk from 295 lines to ~45.
Legacy NATIONAL_CRIMINAL_FRAMEWORK dict retained below for any caller
that introspects it; DEPRECATED — the authoritative data now lives in
frameworks/appeal.py, frameworks/sentencing.py, frameworks/evidence.py,
and frameworks/mental_impairment.py.
"""

from __future__ import annotations

from services.national_framework_engine import (
    build_full_system_prompt,
    build_mens_rea_analysis_block,
    build_national_appellate_context,
    build_record_integrity_block,
    get_jurisdiction_framework,
)

__all__ = [
    "build_full_system_prompt",
    "build_mens_rea_analysis_block",
    "build_national_appellate_context",
    "build_record_integrity_block",
    "get_jurisdiction_framework",
    "NATIONAL_CRIMINAL_FRAMEWORK",
]


# DEPRECATED: legacy hard-coded matrix retained for back-compat only.
# Prefer importing from frameworks/*.py. This dict is NO LONGER the
# source of truth — callers that read it should migrate to the engine's
# get_jurisdiction_framework() helper which resolves from frameworks/.
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
        "appellate_test": ["miscarriage of justice", "error of law", "unsafe verdict"],
        "mens_rea_source": "Criminal Code Act Compilation Act 1913 (WA)",
        "mental_impairment": "Criminal Code (WA) s 27",
        "sentencing": "Sentencing Act 1995 (WA)",
        "evidence": "Evidence Act 1906 (WA)",
        "proviso": True,
    },
    "sa": {
        "appellate_act": "Criminal Appeal Act 1939 (SA)",
        "appellate_test": ["miscarriage of justice", "error of law"],
        "mens_rea_source": "Criminal Law Consolidation Act 1935 (SA)",
        # Fixed 24 Feb 2026: was legacy "Mental Impairment Act 1995 (SA)".
        # Correct reference is Part 8A of the Criminal Law Consolidation
        # Act — see frameworks/mental_impairment.py for the authoritative,
        # up-to-date mapping.
        "mental_impairment": "Criminal Law Consolidation Act 1935 (SA) — Part 8A",
        "sentencing": "Sentencing Act 2017 (SA)",
        "evidence": "Evidence Act 1929 (SA)",
        "proviso": True,
    },
    "tas": {
        "appellate_act": "Criminal Code Act 1924 (TAS)",
        "appellate_test": ["miscarriage of justice", "error of law"],
        "mens_rea_source": "Criminal Code Act 1924 (TAS)",
        "mental_impairment": "Criminal Code (TAS) s 16",
        "sentencing": "Sentencing Act 1997 (TAS)",
        "evidence": "Evidence Act 2001 (TAS)",
        "proviso": True,
    },
    "nt": {
        "appellate_act": "Criminal Code Act 1983 (NT)",
        "appellate_test": ["miscarriage of justice", "error of law"],
        "mens_rea_source": "Criminal Code (NT)",
        "mental_impairment": "Criminal Code (NT)",
        "sentencing": "Sentencing Act 1995 (NT)",
        "evidence": "Evidence (National Uniform Legislation) Act 2011 (NT)",
        "proviso": True,
    },
    "act": {
        "appellate_act": "Crimes (Appeal and Review) Act 2001 (ACT)",
        "appellate_test": ["miscarriage of justice", "error of law"],
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
