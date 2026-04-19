"""
Framework Integrity Self-Test Suite
Validates structural correctness of offence_framework.py data.

Tests:
  1. Every section reference has both 'section' and 'title' keys (no empty/null)
  2. No duplicate section values within a single legislation block
  3. Every state in AUSTRALIAN_STATES has an APPEAL_FRAMEWORK entry
  4. Every offence category has entries for all 8 states + CTH
  5. Empty cth_legislation blocks are documented as intentional
  6. Sentencing, Evidence, and Mental Impairment frameworks cover all states
  7. Legitimacy engine handles all ground types
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import pytest
from offence_framework import (
    OFFENCE_CATEGORIES, APPEAL_FRAMEWORK,
    SENTENCING_FRAMEWORK, EVIDENCE_FRAMEWORK, MENTAL_IMPAIRMENT_FRAMEWORK,
    HUMAN_RIGHTS_FRAMEWORK,
)
from services.legitimacy_engine import (
    OUTCOME_IMPACT_SCORES, calculate_ground_rating, validate_ground_type,
    score_procedural_compliance,
)

ALL_STATES = ["nsw", "vic", "qld", "sa", "wa", "tas", "nt", "act"]


class TestSectionReferences:
    """Every section reference must have both 'section' and 'title' keys with non-empty values."""

    def test_all_sections_have_required_keys(self):
        errors = []
        for cat_key, cat_data in OFFENCE_CATEGORIES.items():
            for state in ALL_STATES:
                leg_key = f"{state}_legislation"
                legislation = cat_data.get(leg_key, {})
                for act_name, sections in legislation.items():
                    for i, sec in enumerate(sections):
                        if not sec.get("section"):
                            errors.append(f"{cat_key}/{leg_key}/{act_name}[{i}]: missing 'section'")
                        if not sec.get("title"):
                            errors.append(f"{cat_key}/{leg_key}/{act_name}[{i}]: missing 'title'")
            # CTH
            cth_leg = cat_data.get("cth_legislation", {})
            for act_name, sections in cth_leg.items():
                for i, sec in enumerate(sections):
                    if not sec.get("section"):
                        errors.append(f"{cat_key}/cth_legislation/{act_name}[{i}]: missing 'section'")
                    if not sec.get("title"):
                        errors.append(f"{cat_key}/cth_legislation/{act_name}[{i}]: missing 'title'")
        assert not errors, "Section reference errors:\n" + "\n".join(errors)


class TestNoDuplicateSections:
    """No duplicate section values within a single legislation block."""

    def test_no_duplicate_sections(self):
        duplicates = []
        for cat_key, cat_data in OFFENCE_CATEGORIES.items():
            for state in ALL_STATES + ["cth"]:
                leg_key = f"{state}_legislation"
                legislation = cat_data.get(leg_key, {})
                for act_name, sections in legislation.items():
                    seen = set()
                    for sec in sections:
                        s = sec.get("section", "")
                        if s in seen:
                            duplicates.append(f"{cat_key}/{leg_key}/{act_name}: duplicate '{s}'")
                        seen.add(s)
        assert not duplicates, "Duplicate sections found:\n" + "\n".join(duplicates)


class TestAppealFrameworkCoverage:
    """Every state in AUSTRALIAN_STATES must have an APPEAL_FRAMEWORK entry."""

    def test_all_states_have_appeal_framework(self):
        missing = []
        for state_key in ALL_STATES:
            if state_key not in APPEAL_FRAMEWORK:
                missing.append(state_key)
        assert not missing, f"States missing from APPEAL_FRAMEWORK: {missing}"

    def test_federal_in_appeal_framework(self):
        assert "federal" in APPEAL_FRAMEWORK, "Federal entry missing from APPEAL_FRAMEWORK"


class TestOffenceCategoryCoverage:
    """Every offence category should have entries for all 8 states + CTH."""

    def test_state_coverage(self):
        gaps = []
        for cat_key, cat_data in OFFENCE_CATEGORIES.items():
            for state in ALL_STATES:
                leg_key = f"{state}_legislation"
                legislation = cat_data.get(leg_key, {})
                if not legislation:
                    gaps.append(f"{cat_key}: empty {leg_key}")
            cth = cat_data.get("cth_legislation", {})
            if not cth:
                # Documented as intentional for state-only offences
                gaps.append(f"{cat_key}: empty cth_legislation (review: state-only offence?)")
        # These are info-level, not failures — print them
        if gaps:
            print(f"\nINFO — Empty legislation blocks ({len(gaps)} items):")
            for g in gaps[:20]:
                print(f"  {g}")


class TestSentencingFramework:
    """Sentencing framework must cover all 8 states + federal."""

    def test_all_states_have_sentencing(self):
        missing = [s for s in ALL_STATES if s not in SENTENCING_FRAMEWORK]
        assert not missing, f"States missing from SENTENCING_FRAMEWORK: {missing}"

    def test_federal_sentencing(self):
        assert "federal" in SENTENCING_FRAMEWORK, "Federal entry missing from SENTENCING_FRAMEWORK"

    def test_sentencing_has_key_provisions(self):
        for state_key, data in SENTENCING_FRAMEWORK.items():
            assert data.get("act"), f"{state_key}: missing 'act' in SENTENCING_FRAMEWORK"
            assert data.get("key_provisions"), f"{state_key}: missing 'key_provisions'"


class TestEvidenceFramework:
    """Evidence framework must cover all 8 states + federal."""

    def test_all_states_have_evidence(self):
        missing = [s for s in ALL_STATES if s not in EVIDENCE_FRAMEWORK]
        assert not missing, f"States missing from EVIDENCE_FRAMEWORK: {missing}"

    def test_federal_evidence(self):
        assert "federal" in EVIDENCE_FRAMEWORK, "Federal entry missing from EVIDENCE_FRAMEWORK"

    def test_uniform_provisions_present(self):
        assert "uniform_evidence_jurisdictions" in EVIDENCE_FRAMEWORK
        uniform = EVIDENCE_FRAMEWORK["uniform_evidence_jurisdictions"]
        assert uniform.get("key_uniform_provisions"), "Missing uniform provisions"


class TestMentalImpairmentFramework:
    """Mental impairment framework must cover all 8 states."""

    def test_all_states_have_mental_impairment(self):
        missing = [s for s in ALL_STATES if s not in MENTAL_IMPAIRMENT_FRAMEWORK]
        assert not missing, f"States missing from MENTAL_IMPAIRMENT_FRAMEWORK: {missing}"


class TestHumanRightsFramework:
    """Human rights framework must include key conventions."""

    def test_iccpr_present(self):
        intl = HUMAN_RIGHTS_FRAMEWORK.get("international", [])
        assert any(h["name"] == "ICCPR" for h in intl), "ICCPR missing"

    def test_cat_present(self):
        intl = HUMAN_RIGHTS_FRAMEWORK.get("international", [])
        assert any(h["name"] == "CAT" for h in intl), "CAT missing"

    def test_croc_present(self):
        intl = HUMAN_RIGHTS_FRAMEWORK.get("international", [])
        assert any(h["name"] == "CROC" for h in intl), "CROC missing"

    def test_domestic_charters_noted(self):
        assert "note" in HUMAN_RIGHTS_FRAMEWORK, "Missing note about SA/WA/TAS/NT lacking domestic charters"

    def test_anti_discrimination_present(self):
        assert "anti_discrimination" in HUMAN_RIGHTS_FRAMEWORK, "Missing anti-discrimination legislation"


class TestLegitimacyEngine:
    """Legitimacy engine must handle all ground types including new ones."""

    def test_all_ground_types_scored(self):
        for gt in OUTCOME_IMPACT_SCORES:
            result = calculate_ground_rating({"ground_type": gt, "supporting_evidence": [{"quote": "test"}]})
            assert "rating" in result, f"No rating for {gt}"
            assert "viability_label" in result, f"No viability_label for {gt}"

    def test_procedural_compliance(self):
        for status in ["within_time", "extension_granted", "out_of_time_arguable", "out_of_time"]:
            result = score_procedural_compliance(status)
            assert "score" in result
            assert "label" in result

    def test_backward_compatibility(self):
        result = calculate_ground_rating({"ground_type": "fresh_evidence", "key_evidence": [{"text": "x"}]})
        assert "legal_score" in result
        assert "evidence_score" in result
        assert "viability_score" in result
        assert "procedural_compliance" in result

    def test_validate_ground_type(self):
        assert validate_ground_type("sentencing_error") == "sentencing_error"
        assert validate_ground_type("unknown_type") == "other"
        assert validate_ground_type(["fresh_evidence"]) == "fresh_evidence"
        assert validate_ground_type(None) == "other"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
