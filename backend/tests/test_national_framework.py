"""
Tests for services/national_framework.py — counsel feedback 23 Feb 2026.

Covers:
  - jurisdiction matrix has all 8 states/territories + federal
  - build_national_appellate_context returns proper content per jurisdiction
  - build_full_system_prompt refuses to proceed without a jurisdiction
  - federal / commonwealth / cth all normalise to the federal entry
  - mens rea + record integrity blocks are always present when state is set
"""

import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from services.national_framework import (
    NATIONAL_CRIMINAL_FRAMEWORK,
    build_full_system_prompt,
    build_mens_rea_analysis_block,
    build_national_appellate_context,
    build_record_integrity_block,
    get_jurisdiction_framework,
)


# ---------- matrix completeness ----------

def test_matrix_has_all_nine_jurisdictions():
    required = {"nsw", "vic", "qld", "wa", "sa", "tas", "nt", "act", "federal"}
    assert required.issubset(NATIONAL_CRIMINAL_FRAMEWORK.keys())


def test_every_jurisdiction_has_required_fields():
    required_fields = {
        "appellate_act", "appellate_test", "mens_rea_source",
        "mental_impairment", "sentencing", "evidence", "proviso",
    }
    for key, fw in NATIONAL_CRIMINAL_FRAMEWORK.items():
        missing = required_fields - set(fw.keys())
        assert not missing, f"{key} missing {missing}"


# ---------- get_jurisdiction_framework ----------

def test_federal_variants_all_normalise():
    assert get_jurisdiction_framework("cth") is not None
    assert get_jurisdiction_framework("Commonwealth") is not None
    assert get_jurisdiction_framework("FEDERAL") is not None
    assert get_jurisdiction_framework("cth") is get_jurisdiction_framework("federal")


def test_unknown_jurisdiction_returns_none():
    assert get_jurisdiction_framework("xyz") is None
    assert get_jurisdiction_framework("") is None
    assert get_jurisdiction_framework(None) is None


# ---------- build_national_appellate_context ----------

def test_national_context_includes_nsw_specifics():
    out = build_national_appellate_context("nsw")
    assert "Criminal Appeal Act 1912 (NSW)" in out
    assert "s 23A" in out
    assert "Uniform Evidence Law" in out
    assert "PROVISO APPLIES" in out


def test_national_context_tas_uses_criminal_code():
    out = build_national_appellate_context("tas")
    assert "Criminal Code Act 1924 (TAS)" in out
    assert "s 16" in out  # mental impairment in TAS


def test_national_context_federal_shows_federal_label():
    out = build_national_appellate_context("cth")
    assert "FEDERAL" in out
    assert "Judiciary Act 1903 (Cth)" in out
    assert "Criminal Code Act 1995 (Cth)" in out
    assert "special leave required (HCA)" in out


def test_national_context_no_state_returns_error():
    out = build_national_appellate_context("")
    assert out.startswith("ERROR:")
    assert "no silent NSW default" in out.lower() or "silent nsw default" in out.lower()


# ---------- mens rea + record blocks ----------

def test_mens_rea_block_uses_offence_name():
    out = build_mens_rea_analysis_block("murder")
    assert "murder" in out.lower()
    assert "fault elements" in out.lower()
    assert "intoxication" in out.lower()
    assert "voluntariness" in out.lower()


def test_record_integrity_block_distinguishes_three_categories():
    out = build_record_integrity_block()
    assert "transcript-supported" in out.lower()
    assert "inference from conduct" in out.lower()
    assert "extra-curial allegation" in out.lower()


# ---------- build_full_system_prompt ----------

def test_full_system_prompt_without_state_errors_out():
    out = build_full_system_prompt({})
    assert out == "ERROR: Jurisdiction must be specified before analysis."


def test_full_system_prompt_with_unknown_state_errors_out():
    out = build_full_system_prompt({"state": "xyz"})
    assert out.startswith("ERROR: Unknown jurisdiction")


def test_full_system_prompt_injects_all_four_sections_when_valid():
    out = build_full_system_prompt({"state": "nsw", "offence_type": "murder"})
    assert "APPELLATE FRAMEWORK — NSW" in out
    assert "MANDATORY MENS REA ANALYSIS" in out
    assert "RECORD INTEGRITY RULE" in out
    assert "MANDATORY ANALYSIS STRUCTURE" in out
    # Hard DO-NOT rules are present
    assert "Default to NSW" in out
    assert "Invent authority" in out


def test_full_system_prompt_federal_accepts_cth_alias():
    out = build_full_system_prompt({"state": "cth", "offence_type": "federal fraud"})
    assert not out.startswith("ERROR")
    assert "FEDERAL" in out
