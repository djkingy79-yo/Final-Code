"""
Regression tests for the recent legislation framework.
Ensures all recent Acts are correctly integrated and injected into LLM prompts.
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from offence_framework import (
    OFFENCE_CATEGORIES,
    AUSTRALIAN_STATES,
    RECENT_LEGISLATION_UPDATES,
    APPEAL_FRAMEWORK,
    HUMAN_RIGHTS_FRAMEWORK,
    COMMON_APPEAL_GROUNDS,
)
from services.offence_helpers import (
    get_offence_context,
    get_offence_system_prompt,
    _build_recent_legislation_context,
)


class TestRecentLegislationData:
    """Verify the RECENT_LEGISLATION_UPDATES dictionary is well-formed."""

    def test_all_states_present(self):
        expected = {"nsw", "vic", "qld", "sa", "wa", "tas", "nt", "act", "federal"}
        assert expected == set(RECENT_LEGISLATION_UPDATES.keys())

    def test_entries_have_required_fields(self):
        required = {"act", "amending_act", "commenced", "summary", "relevant_categories", "appeal_relevance"}
        for state_key, entries in RECENT_LEGISLATION_UPDATES.items():
            for entry in entries:
                missing = required - set(entry.keys())
                assert not missing, f"State {state_key}: entry '{entry.get('act', '?')}' missing fields: {missing}"

    def test_nsw_coercive_control_present(self):
        nsw = RECENT_LEGISLATION_UPDATES["nsw"]
        acts = [e["act"] for e in nsw]
        assert any("Coercive Control" in a for a in acts), "NSW coercive control Act missing"

    def test_nsw_jury_amendment_present(self):
        nsw = RECENT_LEGISLATION_UPDATES["nsw"]
        acts = [e["act"] for e in nsw]
        assert any("Jury Amendment" in a for a in acts), "NSW Jury Amendment Act missing"

    def test_nsw_knife_crime_present(self):
        nsw = RECENT_LEGISLATION_UPDATES["nsw"]
        acts = [e["act"] for e in nsw]
        assert any("Knife Crime" in a for a in acts), "NSW Knife Crime Act missing"

    def test_nsw_racial_hatred_present(self):
        nsw = RECENT_LEGISLATION_UPDATES["nsw"]
        acts = [e["act"] for e in nsw]
        assert any("Racial and Religious Hatred" in a for a in acts), "NSW Racial Hatred Act missing"

    def test_qld_coercive_control_present(self):
        qld = RECENT_LEGISLATION_UPDATES["qld"]
        acts = [e["act"] for e in qld]
        assert any("Coercive Control" in a for a in acts), "QLD coercive control Act missing"

    def test_vic_youth_justice_present(self):
        vic = RECENT_LEGISLATION_UPDATES["vic"]
        acts = [e["act"] for e in vic]
        assert any("Youth Justice" in a for a in acts), "VIC Youth Justice Act missing"

    def test_federal_hate_crimes_present(self):
        fed = RECENT_LEGISLATION_UPDATES["federal"]
        acts = [e["act"] for e in fed]
        assert any("Hate Crimes" in a for a in acts), "Federal Hate Crimes Act missing"

    def test_total_entries_minimum(self):
        total = sum(len(v) for v in RECENT_LEGISLATION_UPDATES.values())
        assert total >= 18, f"Expected at least 18 recent legislation entries, got {total}"


class TestOffenceContextInjection:
    """Verify recent legislation is injected into LLM prompt context."""

    def test_nsw_homicide_includes_recent_leg(self):
        case = {"offence_category": "homicide", "state": "nsw"}
        context = get_offence_context(case)
        assert "RECENT LEGISLATION UPDATES" in context
        assert "Jury Amendment Act 2024" in context
        assert "Bail Act 2013" in context

    def test_nsw_dv_includes_coercive_control(self):
        case = {"offence_category": "domestic_violence", "state": "nsw"}
        context = get_offence_context(case)
        assert "s.54D" in context
        assert "Coercive Control" in context

    def test_qld_dv_includes_coercive_control(self):
        case = {"offence_category": "domestic_violence", "state": "qld"}
        context = get_offence_context(case)
        assert "s.334C" in context
        assert "14 years" in context

    def test_nsw_firearms_includes_knife_crime(self):
        case = {"offence_category": "firearms_weapons", "state": "nsw"}
        context = get_offence_context(case)
        assert "Knife Crime" in context

    def test_terrorism_includes_federal_hate_crimes(self):
        case = {"offence_category": "terrorism", "state": "nsw"}
        context = get_offence_context(case)
        assert "Hate Crimes" in context

    def test_vic_assault_includes_strangulation(self):
        case = {"offence_category": "domestic_violence", "state": "vic"}
        context = get_offence_context(case)
        assert "Non-Fatal Strangulation" in context or "strangulation" in context.lower()

    def test_sa_includes_coercive_control(self):
        case = {"offence_category": "domestic_violence", "state": "sa"}
        context = get_offence_context(case)
        assert "s.20A" in context or "Coercive" in context


class TestSystemPromptAntiHallucination:
    """Verify system prompts include anti-hallucination controls."""

    def test_nsw_system_prompt_has_recent_leg_awareness(self):
        prompt = get_offence_system_prompt("homicide", "nsw")
        assert "RECENT LEGISLATION AWARENESS" in prompt

    def test_system_prompt_has_legislation_accuracy_rule(self):
        prompt = get_offence_system_prompt("domestic_violence", "nsw")
        assert "LEGISLATION ACCURACY" in prompt
        assert "FULL Act name" in prompt or "full Act name" in prompt.lower()

    def test_system_prompt_anti_fabrication(self):
        prompt = get_offence_system_prompt("assault", "vic")
        assert "Do NOT invent or fabricate" in prompt

    def test_system_prompt_australian_english(self):
        prompt = get_offence_system_prompt("homicide", "nsw")
        assert "Australian English" in prompt


class TestBuildRecentLegislationContext:
    """Test the _build_recent_legislation_context helper directly."""

    def test_returns_empty_for_no_matches(self):
        result = _build_recent_legislation_context("nt", "terrorism")
        # NT has no state entries, but federal should match
        if result:
            assert "Hate Crimes" in result

    def test_federal_always_included_when_relevant(self):
        result = _build_recent_legislation_context("vic", "terrorism")
        assert "Hate Crimes" in result

    def test_all_category_filter_works(self):
        result = _build_recent_legislation_context("nsw", "fraud_dishonesty")
        # 'all' category entries like Jury Amendment should appear
        assert "Jury Amendment" in result or "Bail Act" in result


class TestExistingFrameworkIntegrity:
    """Ensure existing framework data wasn't broken by updates."""

    def test_all_offence_categories_exist(self):
        expected = {
            "homicide", "assault", "sexual_offences", "robbery_theft",
            "drug_offences", "fraud_dishonesty", "firearms_weapons",
            "domestic_violence", "public_order", "terrorism", "driving_offences"
        }
        assert expected.issubset(set(OFFENCE_CATEGORIES.keys()))

    def test_all_states_exist(self):
        expected = {"nsw", "vic", "qld", "sa", "wa", "tas", "nt", "act"}
        assert expected == set(AUSTRALIAN_STATES.keys())

    def test_appeal_framework_all_states(self):
        expected = {"nsw", "vic", "qld", "sa", "wa", "tas", "nt", "act", "federal"}
        assert expected == set(APPEAL_FRAMEWORK.keys())

    def test_common_appeal_grounds_minimum(self):
        assert len(COMMON_APPEAL_GROUNDS) >= 10

    def test_human_rights_framework_present(self):
        assert "international" in HUMAN_RIGHTS_FRAMEWORK
        assert "australian" in HUMAN_RIGHTS_FRAMEWORK
