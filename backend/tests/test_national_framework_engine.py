"""
Tests for services/national_framework_engine.py — counsel's comprehensive
national framework engine (23 Feb 2026 round).

Covers:
- jurisdiction + offence category normalisation (incl federal aliases)
- content-based Commonwealth overlay trigger
- homicide-specific mens rea + mental state controls
- framework completeness warnings
- NationalFrameworkResult dataclass
- hard-refusal on missing / unknown jurisdiction
- no NSW leak on VIC matters
"""

import os
import sys

import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from services.national_framework_engine import (
    VALID_JURISDICTIONS,
    FEDERAL_TRIGGER_TERMS,
    NationalFrameworkResult,
    build_framework_dict,
    build_national_case_context,
    build_national_framework_result,
    get_category,
    get_jurisdiction_abbreviation,
    get_jurisdiction_name,
    normalise_jurisdiction,
    normalise_offence_category,
    offence_legislation_key,
    should_apply_commonwealth_overlay,
    validate_framework_completeness,
)


# ---------- normalisation ----------

def test_normalise_jurisdiction_full_names():
    assert normalise_jurisdiction("New South Wales") == "nsw"
    assert normalise_jurisdiction("VICTORIA") == "vic"
    assert normalise_jurisdiction("Queensland") == "qld"


def test_normalise_jurisdiction_federal_aliases():
    assert normalise_jurisdiction("cth") == "cth"
    assert normalise_jurisdiction("commonwealth") == "cth"
    assert normalise_jurisdiction("federal") == "cth"


def test_normalise_jurisdiction_empty_raises():
    with pytest.raises(ValueError, match="JURISDICTION NOT SET"):
        normalise_jurisdiction(None)
    with pytest.raises(ValueError, match="JURISDICTION NOT SET"):
        normalise_jurisdiction("")


def test_normalise_jurisdiction_unknown_raises():
    with pytest.raises(ValueError, match="Unsupported jurisdiction"):
        normalise_jurisdiction("xyz")


def test_valid_jurisdictions_covers_all():
    assert {"nsw", "vic", "qld", "sa", "wa", "tas", "nt", "act", "cth"}.issubset(set(VALID_JURISDICTIONS.values()))


# ---------- offence category ----------

def test_normalise_offence_category_aliases():
    assert normalise_offence_category("murder") == "homicide"
    assert normalise_offence_category("rape") == "sexual_offences"
    assert normalise_offence_category("drugs") == "drug_offences"
    assert normalise_offence_category("firearms") == "firearms_weapons"


def test_normalise_offence_category_empty_raises():
    with pytest.raises(ValueError, match="OFFENCE CATEGORY NOT SET"):
        normalise_offence_category(None)


def test_normalise_offence_category_unknown_raises():
    with pytest.raises(ValueError, match="Unsupported offence category"):
        normalise_offence_category("zzz_fake_category")


# ---------- offence_legislation_key ----------

def test_offence_legislation_key_cth():
    assert offence_legislation_key("cth") == "cth_legislation"


def test_offence_legislation_key_state():
    assert offence_legislation_key("nsw") == "nsw_legislation"
    assert offence_legislation_key("vic") == "vic_legislation"


# ---------- get_category / jurisdiction helpers ----------

def test_get_category_homicide():
    cat = get_category("homicide")
    assert cat["name"] == "Homicide"


def test_get_jurisdiction_name_federal():
    assert get_jurisdiction_name("cth") == "Commonwealth / Federal"


def test_get_jurisdiction_abbreviation_federal():
    assert get_jurisdiction_abbreviation("cth") == "Cth"


# ---------- Commonwealth overlay ----------

def test_commonwealth_overlay_always_applies_for_cth_jurisdiction():
    assert should_apply_commonwealth_overlay({}, "homicide", "cth") is True


def test_commonwealth_overlay_triggers_on_terrorism_category():
    assert should_apply_commonwealth_overlay({}, "terrorism", "nsw") is True


def test_commonwealth_overlay_triggers_on_content_keyword():
    case = {"summary": "Importation of narcotics through the airport customs hall"}
    assert should_apply_commonwealth_overlay(case, "drug_offences", "nsw") is True


def test_commonwealth_overlay_not_triggered_for_plain_state_case():
    case = {"summary": "Local pub assault after a football game"}
    # assault is a state offence with no federal overlay mapped in most cases
    assert should_apply_commonwealth_overlay(case, "assault", "nsw") is False


def test_federal_trigger_terms_include_common_hooks():
    assert "terrorism" in FEDERAL_TRIGGER_TERMS
    assert "carriage service" in FEDERAL_TRIGGER_TERMS
    assert "import" in FEDERAL_TRIGGER_TERMS


# ---------- build_framework_dict / validate_framework_completeness ----------

def test_build_framework_dict_vic_homicide():
    fw = build_framework_dict({"state": "vic", "offence_category": "homicide"})
    assert fw["jurisdiction"] == "vic"
    assert fw["jurisdiction_name"] == "Victoria"
    assert fw["jurisdiction_abbreviation"] == "VIC"
    assert fw["offence_category"] == "homicide"
    assert fw["mens_rea_keys"]
    assert fw["commonwealth_overlay_applies"] is False


def test_validate_framework_completeness_complete_case():
    fw = build_framework_dict({"state": "vic", "offence_category": "homicide"})
    warnings = validate_framework_completeness(fw)
    # VIC homicide is fully mapped — zero warnings expected.
    assert warnings == []


# ---------- build_national_case_context + counsel's critical test ----------

def test_build_national_case_context_vic_murder_no_nsw_leak():
    """Counsel's exact mandatory test case (23 Feb 2026)."""
    out = build_national_case_context(
        {"state": "vic", "offence_category": "homicide", "offence_type": "Murder"}
    )
    assert "Jurisdiction: Victoria (VIC)" in out
    assert "Crimes Act 1958 (Vic)" in out
    # No NSW Crimes Act 1900 leakage
    assert "Crimes Act 1900 (NSW)" not in out


def test_build_national_case_context_includes_all_sections():
    out = build_national_case_context(
        {"state": "nsw", "offence_category": "homicide", "offence_type": "Murder"}
    )
    assert "NATIONAL JURISDICTION-COMPLETE FRAMEWORK ENGINE" in out
    assert "PRIMARY OFFENCE LEGISLATION" in out
    assert "OFFENCE ELEMENTS" in out
    assert "MANDATORY MENS REA / FAULT ELEMENT ANALYSIS" in out
    assert "MENTAL IMPAIRMENT / CRIMINAL RESPONSIBILITY" in out
    assert "APPELLATE FRAMEWORK" in out
    assert "SENTENCING FRAMEWORK" in out
    assert "EVIDENCE FRAMEWORK" in out
    assert "PROCEDURAL PIPELINE" in out
    assert "RECORD INTEGRITY RULES" in out
    assert "GROUND CLASSIFICATION RULES" in out
    assert "NO-HALLUCINATION" in out


def test_build_national_case_context_homicide_triggers_specific_controls():
    out = build_national_case_context(
        {"state": "nsw", "offence_category": "homicide", "offence_type": "Murder"}
    )
    assert "HOMICIDE-SPECIFIC MENS REA CONTROL" in out
    assert "HOMICIDE MENTAL STATE CONTROL" in out


def test_build_national_case_context_code_jurisdiction_qld():
    out = build_national_case_context(
        {"state": "qld", "offence_category": "homicide", "offence_type": "Murder"}
    )
    assert "Queensland" in out or "QLD" in out
    # Code-jurisdiction note present
    assert "Code jurisdiction" in out


def test_build_national_case_context_federal_accepts_cth():
    out = build_national_case_context(
        {"state": "federal", "offence_category": "terrorism", "offence_type": "Federal terrorism"}
    )
    assert "Commonwealth / Federal" in out
    assert "Criminal Code Act 1995 (Cth)" in out
    # Chapter 2 fault element note for CTH
    assert "Chapter 2" in out


def test_build_national_case_context_no_state_raises():
    with pytest.raises(ValueError, match="JURISDICTION NOT SET"):
        build_national_case_context({"offence_category": "homicide"})


def test_build_national_case_context_no_category_raises():
    with pytest.raises(ValueError, match="OFFENCE CATEGORY NOT SET"):
        build_national_case_context({"state": "nsw"})


# ---------- NationalFrameworkResult ----------

def test_build_national_framework_result_returns_dataclass():
    r = build_national_framework_result(
        {"state": "vic", "offence_category": "homicide", "offence_type": "Murder"}
    )
    assert isinstance(r, NationalFrameworkResult)
    assert r.jurisdiction == "vic"
    assert r.offence_category == "homicide"
    assert r.offence_type == "Murder"
    assert isinstance(r.warnings, list)
    assert isinstance(r.context, str)
    assert "Crimes Act 1958 (Vic)" in r.context


def test_national_framework_result_is_frozen():
    r = build_national_framework_result(
        {"state": "nsw", "offence_category": "homicide"}
    )
    with pytest.raises(Exception):
        r.jurisdiction = "vic"  # frozen dataclass should refuse mutation
