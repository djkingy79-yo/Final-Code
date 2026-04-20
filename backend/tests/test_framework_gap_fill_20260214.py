"""
Regression tests for the 14 February 2026 offence framework gap fill.

Locks in:
  - Coverage matrix completeness (terrorism across all 8 states/territories;
    organised_crime for TAS/NT/ACT; Cth references for extortion,
    arson/property damage, DV, public order, robbery_theft).
  - Every OFFENCE_CATEGORIES entry has procedural_flow + relevant_mens_rea.
  - MENS_REA_FRAMEWORK core keys are present.
  - INDICTABLE, HYBRID, SUMMARY procedural flows exist and are coherent.
  - Context builder surfaces mens rea + procedural pipeline into LLM prompts.
"""
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from offence_framework import (  # noqa: E402
    OFFENCE_CATEGORIES,
    INDICTABLE_PROCEDURE_FLOW,
    HYBRID_PROCEDURE_FLOW,
    SUMMARY_PROCEDURE_FLOW,
    MENS_REA_FRAMEWORK,
    LEGISLATION_CURRENCY,
)
from services.offence_helpers import get_offence_context  # noqa: E402


JURISDICTIONS_FULL = ("nsw", "vic", "qld", "sa", "wa", "tas", "nt", "act", "cth")

# Cth is genuinely N/A for driving (state matter). Everything else must have Cth.
MUST_HAVE_CTH = {
    c
    for c in OFFENCE_CATEGORIES.keys()
    if c not in {"driving_offences"}
}


def test_terrorism_state_coverage():
    t = OFFENCE_CATEGORIES["terrorism"]
    for j in JURISDICTIONS_FULL:
        assert t.get(f"{j}_legislation"), f"terrorism missing {j}_legislation"


def test_organised_crime_full_coverage():
    oc = OFFENCE_CATEGORIES["organised_crime"]
    for j in JURISDICTIONS_FULL:
        assert oc.get(f"{j}_legislation"), f"organised_crime missing {j}_legislation"


def test_cth_gap_fills():
    for cat in MUST_HAVE_CTH:
        data = OFFENCE_CATEGORIES[cat]
        assert data.get("cth_legislation"), f"{cat} missing cth_legislation"


def test_every_category_has_procedural_flow_and_mens_rea():
    for cat, data in OFFENCE_CATEGORIES.items():
        assert isinstance(data.get("procedural_flow"), list) and data["procedural_flow"], \
            f"{cat} missing procedural_flow"
        assert isinstance(data.get("relevant_mens_rea"), list) and data["relevant_mens_rea"], \
            f"{cat} missing relevant_mens_rea"
        for key in data["relevant_mens_rea"]:
            assert key in MENS_REA_FRAMEWORK, f"{cat}: unknown mens rea key {key}"


def test_indictable_flow_has_all_13_stages():
    assert len(INDICTABLE_PROCEDURE_FLOW) == 13
    names = [s["name"] for s in INDICTABLE_PROCEDURE_FLOW]
    # Key forensic stages per user-provided 12-stage flow
    assert "Incident" in names
    assert any("Bail" in n for n in names)
    assert any("Committal" in n for n in names)
    assert any("Indictment" in n for n in names)
    assert any("Trial" in n for n in names)
    assert any("Sentencing" in n for n in names)
    assert any("Intermediate Appellate" in n for n in names)
    assert any("High Court" in n for n in names)


def test_hybrid_flow_drops_committal_and_indictment():
    names = [s["name"] for s in HYBRID_PROCEDURE_FLOW]
    assert not any("Committal" in n for n in names)
    assert not any("Indictment" in n for n in names)


def test_summary_flow_basic_shape():
    assert len(SUMMARY_PROCEDURE_FLOW) >= 8
    names = [s["name"] for s in SUMMARY_PROCEDURE_FLOW]
    assert any("Summary" in n for n in names)
    assert any("High Court" in n for n in names)


def test_mens_rea_framework_has_core_elements():
    for key in ("intention", "knowledge", "recklessness", "negligence", "strict_liability", "absolute_liability"):
        assert key in MENS_REA_FRAMEWORK
        assert MENS_REA_FRAMEWORK[key].get("definition")
        assert MENS_REA_FRAMEWORK[key].get("authorities")


def test_currency_tracker_updated_2026_02():
    assert LEGISLATION_CURRENCY.get("last_verified", "").startswith("2026-02")


def test_context_builder_surfaces_new_blocks():
    case = {"offence_category": "homicide", "offence_type": "Murder", "state": "nsw"}
    ctx = get_offence_context(case)
    assert "RELEVANT MENS REA" in ctx
    assert "FORENSIC PROCEDURAL PIPELINE" in ctx
    assert "Stage 1:" in ctx
    assert "Stage 13:" in ctx
    assert "Intention" in ctx


def test_context_builder_summary_flow_for_public_order():
    case = {"offence_category": "public_order", "offence_type": "Offensive conduct", "state": "nsw"}
    ctx = get_offence_context(case)
    assert "Summary Hearing" in ctx or "Summary" in ctx


def test_context_builder_hybrid_flow_for_driving():
    case = {"offence_category": "driving_offences", "offence_type": "Drink Driving", "state": "nsw"}
    ctx = get_offence_context(case)
    # Hybrid flow must NOT include committal/indictment
    assert "Committal Proceedings" not in ctx.split("FORENSIC PROCEDURAL PIPELINE")[-1].split("RELEVANT")[0]
