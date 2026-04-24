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


# ---------------------------------------------------------------------------
# COUNSEL REFACTOR 24 Feb 2026 — 9-jurisdiction parametric suite.
#
# Proves every state/territory + Commonwealth runs build_full_system_prompt
# correctly:
#   (a) contains the jurisdiction's own governing appellate Act, and
#   (b) does NOT leak NSW's Crimes Act 1900 (NSW) into any non-NSW prompt, and
#   (c) emits the hard NO-SILENT-NSW-DEFAULT rule.
# ---------------------------------------------------------------------------

import pytest


_JURISDICTION_EXPECTED_ACTS = {
    "nsw": "Criminal Appeal Act 1912 (NSW)",
    "vic": "Criminal Procedure Act 2009 (VIC)",
    "qld": "Criminal Code (Qld)",
    "sa": "Criminal Appeal Act 1939 (SA)",
    "wa": "Criminal Appeals Act 2004 (WA)",
    "tas": "Criminal Code Act 1924 (TAS)",
    "nt": "Criminal Code Act 1983 (NT)",
    "act": "Crimes (Appeal and Review) Act 2001 (ACT)",
    "cth": "Judiciary Act 1903 (Cth)",
}


@pytest.mark.parametrize("jurisdiction,expected_act", list(_JURISDICTION_EXPECTED_ACTS.items()))
def test_every_jurisdiction_renders_its_own_governing_act(jurisdiction, expected_act):
    """Every jurisdiction must render its own appellate Act — no NSW fallback."""
    out = build_full_system_prompt({"state": jurisdiction, "offence_type": "murder"})
    assert not out.startswith("ERROR"), f"{jurisdiction} unexpectedly errored: {out!r}"
    assert expected_act in out, (
        f"{jurisdiction.upper()} prompt missing its own governing Act "
        f"'{expected_act}'. Output was:\n{out}"
    )


@pytest.mark.parametrize(
    "jurisdiction",
    ["vic", "qld", "sa", "wa", "tas", "nt", "act", "cth"],
)
def test_non_nsw_prompts_do_not_leak_nsw_crimes_act(jurisdiction):
    """Critical counsel rule: no NSW legislation may leak into a non-NSW prompt."""
    out = build_full_system_prompt({"state": jurisdiction, "offence_type": "murder"})
    assert "Crimes Act 1900 (NSW)" not in out, (
        f"{jurisdiction.upper()} prompt unexpectedly contains "
        f"'Crimes Act 1900 (NSW)'. This is a silent NSW fallback and must not occur."
    )
    assert "Crimes (Sentencing Procedure) Act 1999 (NSW)" not in out, (
        f"{jurisdiction.upper()} prompt leaked NSW sentencing Act."
    )
    assert "Evidence Act 1995 (NSW)" not in out, (
        f"{jurisdiction.upper()} prompt leaked NSW evidence Act."
    )


def test_sa_mental_impairment_renders_part_8a_of_clca():
    """Counsel-corrected SA mental impairment must render the CLCA Part 8A, not the stale 1995 Act."""
    out = build_full_system_prompt({"state": "sa", "offence_type": "murder"})
    assert "Criminal Law Consolidation Act 1935 (SA) — Part 8A" in out, (
        f"SA mental impairment did not render the counsel-corrected Part 8A reference. "
        f"Output was:\n{out}"
    )
    assert "Mental Impairment Act 1995 (SA)" not in out, (
        "SA prompt still contains the stale, incorrect 'Mental Impairment Act 1995 (SA)' string."
    )


@pytest.mark.parametrize(
    "alias",
    ["cth", "CTH", "federal", "FEDERAL", "commonwealth", "Commonwealth"],
)
def test_all_federal_aliases_resolve_to_the_same_matrix_row(alias):
    """cth / commonwealth / federal (and case variants) must all resolve identically."""
    fw = get_jurisdiction_framework(alias)
    assert fw is not None, f"Federal alias '{alias}' did not resolve to any matrix row."
    # Identity check — all aliases must return THE SAME dict object.
    assert fw is get_jurisdiction_framework("federal"), (
        f"Federal alias '{alias}' returned a different dict object from 'federal'."
    )


def test_no_silent_nsw_default_for_missing_jurisdiction():
    """If jurisdiction is missing entirely, prompt must error out rather than default to NSW."""
    out = build_full_system_prompt({"offence_type": "murder"})
    assert out.startswith("ERROR"), (
        "Missing jurisdiction must return an ERROR string — silent NSW default is forbidden."
    )
    assert "NSW" not in out or "silent" in out.lower()


@pytest.mark.parametrize(
    "jurisdiction",
    ["nsw", "vic", "qld", "sa", "wa", "tas", "nt", "act", "cth"],
)
def test_every_jurisdiction_emits_do_not_default_to_nsw_rule(jurisdiction):
    """Every valid prompt must include the hard 'Default to NSW' DO-NOT rule."""
    out = build_full_system_prompt({"state": jurisdiction, "offence_type": "murder"})
    assert "Default to NSW" in out, (
        f"{jurisdiction.upper()} prompt missing the hard DO-NOT rule 'Default to NSW'."
    )
    assert "Invent authority" in out, (
        f"{jurisdiction.upper()} prompt missing the hard DO-NOT rule 'Invent authority'."
    )
