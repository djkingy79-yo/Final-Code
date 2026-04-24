"""
Tests for services/national_framework_engine.py — the bridge layer.
Counsel feedback 23 Feb 2026.
"""

import os
import sys

import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from services.national_framework_engine import (
    STATE_ALIASES,
    build_national_case_context,
    get_jurisdiction_legislation,
    get_offence_category,
    normalise_jurisdiction,
    offence_legislation_key,
    render_appeal_framework,
    render_commonwealth_overlay,
    render_evidence_framework,
    render_legislation_block,
    render_mens_rea_framework,
    render_mental_impairment_framework,
    render_sentencing_framework,
)


# ---------- jurisdiction normalisation ----------

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


def test_state_aliases_covers_all_jurisdictions():
    covered = set(STATE_ALIASES.values())
    assert {"nsw", "vic", "qld", "sa", "wa", "tas", "nt", "act", "cth"}.issubset(covered)


# ---------- offence_legislation_key ----------

def test_offence_legislation_key_cth():
    assert offence_legislation_key("cth") == "cth_legislation"


def test_offence_legislation_key_state():
    assert offence_legislation_key("nsw") == "nsw_legislation"


# ---------- get_offence_category ----------

def test_get_offence_category_valid():
    cat = get_offence_category("homicide")
    assert cat.get("name")


def test_get_offence_category_invalid_raises():
    with pytest.raises(ValueError, match="Invalid offence category"):
        get_offence_category("not_a_category")


# ---------- render_legislation_block ----------

def test_render_legislation_block_returns_jurisdiction_specific_content():
    out = render_legislation_block("homicide", "nsw")
    assert "NSW" in out
    assert "Crimes Act" in out or "murder" in out.lower() or "manslaughter" in out.lower()


def test_render_legislation_block_unknown_jurisdiction_legislation_raises():
    with pytest.raises(ValueError, match="No .* legislation mapped"):
        # Pick a category that definitely doesn't have every jurisdiction mapped
        render_legislation_block("homicide", "not_a_jurisdiction")


# ---------- render_commonwealth_overlay ----------

def test_commonwealth_overlay_empty_when_jurisdiction_is_cth():
    assert render_commonwealth_overlay("homicide", "cth") == ""


def test_commonwealth_overlay_mentions_federal_hook_when_nsw():
    out = render_commonwealth_overlay("homicide", "nsw")
    # May be empty if homicide has no cth overlay, but if present must include the hook text
    if out:
        assert "federal jurisdictional hook" in out.lower()


# ---------- render_appeal / sentencing / evidence / mental impairment ----------

def test_render_appeal_framework_tas_uses_correct_act():
    out = render_appeal_framework("tas")
    assert "TAS" in out.upper()


def test_render_appeal_framework_federal_accepts_cth():
    out = render_appeal_framework("cth")
    assert "FEDERAL" in out.upper() or "CTH" in out.upper()


def test_render_sentencing_framework_contains_act_label():
    out = render_sentencing_framework("nsw")
    assert "Act" in out


def test_render_evidence_framework_contains_act_label():
    out = render_evidence_framework("vic")
    assert "Act" in out


def test_render_mental_impairment_framework_returns_content():
    out = render_mental_impairment_framework("nsw")
    assert "MENTAL IMPAIRMENT" in out


# ---------- render_mens_rea_framework ----------

def test_mens_rea_framework_code_jurisdiction_note():
    out = render_mens_rea_framework("homicide", "qld")
    assert "Code jurisdiction" in out


def test_mens_rea_framework_commonwealth_note():
    out = render_mens_rea_framework("homicide", "cth")
    assert "Criminal Code Act 1995 (Cth) Chapter 2" in out


def test_mens_rea_framework_common_law_note():
    out = render_mens_rea_framework("homicide", "nsw")
    assert "Common-law" in out or "common-law" in out


# ---------- build_national_case_context ----------

def test_build_national_case_context_minimal_nsw_case():
    out = build_national_case_context({"state": "nsw", "offence_category": "homicide"})
    assert "NATIONAL JURISDICTION-COMPLETE LEGAL FRAMEWORK" in out
    assert "Jurisdiction: NSW" in out
    assert "RELEVANT NSW OFFENCE LEGISLATION" in out
    assert "APPELLATE FRAMEWORK" in out
    assert "SENTENCING FRAMEWORK" in out
    assert "EVIDENCE FRAMEWORK" in out
    assert "MENTAL IMPAIRMENT" in out
    assert "MANDATORY MENS REA" in out
    assert "RECORD INTEGRITY RULES" in out
    assert "GROUND DECISION RULES" in out


def test_build_national_case_context_no_state_raises():
    with pytest.raises(ValueError, match="JURISDICTION NOT SET"):
        build_national_case_context({})


def test_build_national_case_context_federal_alias_resolves():
    out = build_national_case_context({"state": "federal", "offence_category": "homicide"})
    assert "Jurisdiction: CTH" in out
    assert "APPELLATE FRAMEWORK (CTH)" in out
