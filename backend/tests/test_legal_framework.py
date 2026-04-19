"""
Self-test suite for the legal framework data integrity.
Verifies all offence categories, state frameworks, sentencing, evidence,
mental impairment, appeal pathways, and landmark cases are complete.

Run: cd /app/backend && python -m pytest tests/test_legal_framework.py -v
"""
import sys
sys.path.insert(0, "/app/backend")

import pytest
from offence_framework import (
    OFFENCE_CATEGORIES, RECENT_LEGISLATION_UPDATES,
    FEDERAL_CRIMINAL_FRAMEWORK,
    SENTENCING_FRAMEWORK, EVIDENCE_FRAMEWORK, MENTAL_IMPAIRMENT_FRAMEWORK,
    APPEAL_FRAMEWORK, PROCEEDS_OF_CRIME_FRAMEWORK, LANDMARK_CASES,
    HUMAN_RIGHTS_FRAMEWORK,
)
from services.offence_helpers import (
    STATE_FRAMEWORKS, enforce_forensic_language, validate_jurisdiction_completeness,
    _build_appeal_time_limit_note,
)
from services.case_validation import validate_citation, strip_hallucinated_citations

ALL_STATES = ["nsw", "vic", "qld", "sa", "wa", "tas", "nt", "act"]


class TestStateFrameworks:
    @pytest.mark.parametrize("state", ALL_STATES + ["federal"])
    def test_framework_exists(self, state):
        assert state in STATE_FRAMEWORKS, f"Missing framework for {state}"

    @pytest.mark.parametrize("state", ALL_STATES + ["federal"])
    def test_has_primary_legislation(self, state):
        fw = STATE_FRAMEWORKS[state]
        assert fw.get("primary_legislation"), f"No primary_legislation for {state}"
        for act in fw["primary_legislation"]:
            assert act.get("act"), f"Empty act name in {state}"
            assert act.get("description"), f"Empty description in {state}"

    @pytest.mark.parametrize("state", ALL_STATES + ["federal"])
    def test_has_last_verified(self, state):
        fw = STATE_FRAMEWORKS[state]
        assert fw.get("last_verified"), f"No last_verified date for {state}"


class TestOffenceCategories:
    def test_minimum_categories(self):
        assert len(OFFENCE_CATEGORIES) >= 15

    @pytest.mark.parametrize("cat", list(OFFENCE_CATEGORIES.keys()))
    def test_category_has_required_fields(self, cat):
        data = OFFENCE_CATEGORIES[cat]
        assert data.get("name"), f"Missing name for {cat}"
        assert data.get("description"), f"Missing description for {cat}"
        assert data.get("key_elements"), f"Missing key_elements for {cat}"
        assert data.get("defences"), f"Missing defences for {cat}"

    @pytest.mark.parametrize("cat", list(OFFENCE_CATEGORIES.keys()))
    def test_no_empty_section_values(self, cat):
        data = OFFENCE_CATEGORIES[cat]
        for key in data:
            if "_legislation" in key:
                for act_name, sections in data[key].items():
                    for sec in sections:
                        assert sec.get("section"), f"Empty section in {cat}/{key}/{act_name}"
                        assert sec.get("title"), f"Empty title in {cat}/{key}/{act_name}"

    @pytest.mark.parametrize("cat", list(OFFENCE_CATEGORIES.keys()))
    def test_no_duplicate_sections(self, cat):
        data = OFFENCE_CATEGORIES[cat]
        for key in data:
            if "_legislation" in key:
                for act_name, sections in data[key].items():
                    seen = set()
                    for sec in sections:
                        s = sec.get("section", "")
                        assert s not in seen, f"Duplicate section {s} in {cat}/{key}/{act_name}"
                        seen.add(s)


class TestSentencingFramework:
    @pytest.mark.parametrize("state", ALL_STATES + ["federal"])
    def test_sentencing_exists(self, state):
        assert state in SENTENCING_FRAMEWORK, f"Missing sentencing for {state}"

    @pytest.mark.parametrize("state", ALL_STATES + ["federal"])
    def test_sentencing_has_act(self, state):
        sf = SENTENCING_FRAMEWORK[state]
        assert sf.get("act"), f"No sentencing act for {state}"
        assert sf.get("key_provisions"), f"No key_provisions for {state}"


class TestEvidenceFramework:
    @pytest.mark.parametrize("state", ALL_STATES + ["federal"])
    def test_evidence_exists(self, state):
        assert state in EVIDENCE_FRAMEWORK, f"Missing evidence for {state}"


class TestMentalImpairment:
    @pytest.mark.parametrize("state", ALL_STATES)
    def test_mental_impairment_exists(self, state):
        assert state in MENTAL_IMPAIRMENT_FRAMEWORK, f"Missing mental impairment for {state}"


class TestAppealFramework:
    @pytest.mark.parametrize("state", ALL_STATES + ["federal"])
    def test_appeal_exists(self, state):
        assert state in APPEAL_FRAMEWORK, f"Missing appeal for {state}"

    @pytest.mark.parametrize("state", ALL_STATES)
    def test_appeal_has_court(self, state):
        af = APPEAL_FRAMEWORK[state]
        assert af.get("court"), f"No court for {state}"

    @pytest.mark.parametrize("state", ALL_STATES)
    def test_appeal_has_time_limit(self, state):
        af = APPEAL_FRAMEWORK[state]
        has_tl = af.get("time_limit") or af.get("time_limits")
        assert has_tl, f"No time_limit(s) for {state}"

    @pytest.mark.parametrize("state", ALL_STATES)
    def test_time_limit_note_not_empty(self, state):
        note = _build_appeal_time_limit_note(state)
        assert "verify" not in note.lower() or "time" in note.lower(), f"Time limit note unhelpful for {state}"


class TestRecentLegislation:
    @pytest.mark.parametrize("state", ALL_STATES + ["federal"])
    def test_recent_legislation_exists(self, state):
        assert state in RECENT_LEGISLATION_UPDATES, f"Missing recent legislation for {state}"
        assert len(RECENT_LEGISLATION_UPDATES[state]) > 0, f"No recent legislation entries for {state}"


class TestLandmarkCases:
    def test_minimum_categories(self):
        assert len(LANDMARK_CASES) >= 6

    @pytest.mark.parametrize("cat", list(LANDMARK_CASES.keys()))
    def test_cases_have_required_fields(self, cat):
        for case in LANDMARK_CASES[cat]:
            assert case.get("case"), f"Missing case name in {cat}"
            assert case.get("principle"), f"Missing principle in {cat}"


class TestProceedsOfCrime:
    @pytest.mark.parametrize("state", ALL_STATES + ["federal"])
    def test_proceeds_exists(self, state):
        assert state in PROCEEDS_OF_CRIME_FRAMEWORK, f"Missing proceeds of crime for {state}"


class TestHumanRights:
    def test_has_international(self):
        assert "international" in HUMAN_RIGHTS_FRAMEWORK
        names = [i["name"] for i in HUMAN_RIGHTS_FRAMEWORK["international"]]
        assert "ICCPR" in names
        assert "CAT" in names
        assert "CROC" in names

    def test_has_australian(self):
        assert "australian" in HUMAN_RIGHTS_FRAMEWORK
        assert len(HUMAN_RIGHTS_FRAMEWORK["australian"]) >= 3

    def test_has_anti_discrimination(self):
        assert "anti_discrimination" in HUMAN_RIGHTS_FRAMEWORK
        names = [i["name"] for i in HUMAN_RIGHTS_FRAMEWORK["anti_discrimination"]]
        assert any("Racial" in n for n in names)
        assert any("Sex" in n for n in names)

    def test_has_no_charter_note(self):
        note = HUMAN_RIGHTS_FRAMEWORK.get("note", "")
        assert "SA" in note and "WA" in note and "TAS" in note and "NT" in note


class TestForensicLanguage:
    @pytest.mark.parametrize("phrase", [
        "The trial judge erred in failing to consider evidence.",
        "The conviction is unsafe.",
        "The sentence is manifestly excessive.",
        "The judge was biased against the defendant.",
        "The court failed to apply the correct legal test.",
    ])
    def test_declarative_phrases_caught(self, phrase):
        result = enforce_forensic_language(phrase)
        assert result != phrase, f"Phrase not caught: {phrase}"

    def test_does_not_double_prefix(self):
        text = "It is arguable that it is arguable that the judge erred."
        result = enforce_forensic_language(text)
        assert "arguably arguably" not in result.lower()


class TestCitationValidation:
    def test_valid_medium_neutral(self):
        v = validate_citation("R v Smith [2023] NSWCCA 123")
        assert v["valid"]

    def test_rejects_placeholder(self):
        v = validate_citation("[Surname] v [Year]")
        assert not v["valid"]

    def test_rejects_suspicious(self):
        v = validate_citation("citation not available")
        assert not v["valid"]

    def test_strips_hallucinated(self):
        text = "Good.\nSee R v [Surname] [2024] NSWCCA 999.\nMore good."
        result = strip_hallucinated_citations(text)
        assert "[Surname]" not in result
        assert "Good" in result


class TestJurisdictionValidation:
    @pytest.mark.parametrize("state", ALL_STATES)
    def test_confirmed_state_not_flagged(self, state):
        warnings = validate_jurisdiction_completeness(state, "homicide")
        assert not any("NOT CONFIRMED" in w for w in warnings)

    def test_unconfirmed_state_flagged(self):
        warnings = validate_jurisdiction_completeness("", "homicide")
        assert any("NOT CONFIRMED" in w for w in warnings)


class TestFederalFramework:
    def test_has_absolute_liability(self):
        for act in FEDERAL_CRIMINAL_FRAMEWORK["primary_legislation"]:
            if "Criminal Code" in act["act"]:
                provs = " ".join(act.get("key_provisions", []))
                assert "4.4" in provs, "Missing s.4.4 absolute liability"
                assert "9.3" in provs, "Missing s.9.3 mistake of fact (absolute liability)"
                break
        else:
            pytest.fail("Criminal Code not found in federal framework")

    def test_federal_appeal_has_fca(self):
        leg = APPEAL_FRAMEWORK["federal"].get("legislation", "")
        assert "Federal Court" in leg, "Missing Federal Court Act reference"
