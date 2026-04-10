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
    NSW_CRIMINAL_FRAMEWORK,
    VIC_CRIMINAL_FRAMEWORK,
    QLD_CRIMINAL_FRAMEWORK,
    SA_CRIMINAL_FRAMEWORK,
    WA_CRIMINAL_FRAMEWORK,
    TAS_CRIMINAL_FRAMEWORK,
    NT_CRIMINAL_FRAMEWORK,
    ACT_CRIMINAL_FRAMEWORK,
    FEDERAL_CRIMINAL_FRAMEWORK,
)
from services.offence_helpers import (
    get_offence_context,
    get_offence_system_prompt,
    _build_recent_legislation_context,
    _build_state_framework_context,
    _build_federal_framework_context,
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
        assert total >= 28, f"Expected at least 28 recent legislation entries, got {total}"

    def test_nt_has_entries(self):
        assert len(RECENT_LEGISLATION_UPDATES["nt"]) >= 3, "NT should have at least 3 recent legislation entries"

    def test_act_has_entries(self):
        assert len(RECENT_LEGISLATION_UPDATES["act"]) >= 3, "ACT should have at least 3 recent legislation entries"

    def test_nt_youth_justice_amendment_present(self):
        nt = RECENT_LEGISLATION_UPDATES["nt"]
        acts = [e["act"] for e in nt]
        assert any("Youth Justice" in a for a in acts), "NT Youth Justice Legislation Amendment Act missing"

    def test_nt_bail_amendment_present(self):
        nt = RECENT_LEGISLATION_UPDATES["nt"]
        acts = [e["act"] for e in nt]
        assert any("Bail" in a for a in acts), "NT Bail and Youth Justice Amendment missing"

    def test_act_macr_reform_present(self):
        act_updates = RECENT_LEGISLATION_UPDATES["act"]
        acts = [e["act"] for e in act_updates]
        assert any("Age of Criminal Responsibility" in a for a in acts), "ACT MACR reform missing"

    def test_act_disclosure_present(self):
        act_updates = RECENT_LEGISLATION_UPDATES["act"]
        acts = [e["act"] for e in act_updates]
        assert any("Disclosure" in a for a in acts), "ACT Disclosure Amendment missing"


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


class TestNSWCriminalFramework:
    """Verify the full NSW criminal legislative framework."""

    def test_primary_legislation_count(self):
        assert len(NSW_CRIMINAL_FRAMEWORK["primary_legislation"]) >= 5

    def test_crimes_act_present(self):
        acts = [a["act"] for a in NSW_CRIMINAL_FRAMEWORK["primary_legislation"]]
        assert any("Crimes Act 1900" in a for a in acts)

    def test_criminal_procedure_act_present(self):
        acts = [a["act"] for a in NSW_CRIMINAL_FRAMEWORK["primary_legislation"]]
        assert any("Criminal Procedure Act 1986" in a for a in acts)

    def test_sentencing_procedure_act_present(self):
        acts = [a["act"] for a in NSW_CRIMINAL_FRAMEWORK["primary_legislation"]]
        assert any("Crimes (Sentencing Procedure) Act 1999" in a for a in acts)

    def test_lepra_present(self):
        acts = [a["act"] for a in NSW_CRIMINAL_FRAMEWORK["primary_legislation"]]
        assert any("LEPRA" in a for a in acts)

    def test_evidence_act_present(self):
        acts = [a["act"] for a in NSW_CRIMINAL_FRAMEWORK["primary_legislation"]]
        assert any("Evidence Act 1995" in a for a in acts)

    def test_key_regulations_present(self):
        regs = [r["regulation"] for r in NSW_CRIMINAL_FRAMEWORK["key_regulations"]]
        assert any("Crimes Regulation 2020" in r for r in regs)
        assert any("Criminal Procedure Regulation 2017" in r for r in regs)
        assert any("Crimes (Sentencing Procedure) Regulation 2017" in r for r in regs)
        assert any("Law Enforcement" in r for r in regs)

    def test_specialised_legislation_present(self):
        specs = [s["act"] for s in NSW_CRIMINAL_FRAMEWORK["specialised_legislation"]]
        assert any("Domestic and Personal Violence" in s for s in specs)
        assert any("Bail Act 2013" in s for s in specs)
        assert any("Drug Misuse" in s for s in specs)
        assert any("Summary Offences" in s for s in specs)
        assert any("Mental Health" in s for s in specs)
        assert any("Forensic Procedures" in s for s in specs)
        assert any("Criminal Appeal Act 1912" in s for s in specs)
        assert any("Jury Act 1977" in s for s in specs)

    def test_nsw_framework_injected_for_nsw_cases(self):
        case = {"offence_category": "homicide", "state": "nsw"}
        context = get_offence_context(case)
        assert "Crimes Act 1900 No 40" in context
        assert "Criminal Procedure Act 1986 No 209" in context
        assert "Evidence Act 1995 No 25" in context
        assert "LEPRA" in context

    def test_nsw_recent_animal_abuse_present(self):
        nsw = RECENT_LEGISLATION_UPDATES["nsw"]
        acts = [e["act"] for e in nsw]
        assert any("Animal Sexual Abuse" in a for a in acts)

    def test_nsw_good_character_bill_present(self):
        nsw = RECENT_LEGISLATION_UPDATES["nsw"]
        acts = [e["act"] for e in nsw]
        assert any("Good Character" in a for a in acts)

    def test_nsw_surveillance_devices_present(self):
        nsw = RECENT_LEGISLATION_UPDATES["nsw"]
        acts = [e["act"] for e in nsw]
        assert any("Surveillance Devices" in a for a in acts)

    def test_nsw_mental_health_act_present(self):
        nsw = RECENT_LEGISLATION_UPDATES["nsw"]
        acts = [e["act"] for e in nsw]
        assert any("Mental Health" in a for a in acts)


class TestAllStateFrameworks:
    """Verify all state/territory criminal frameworks are complete and correctly injected."""

    def test_vic_framework_has_crimes_act_1958(self):
        acts = [a["act"] for a in VIC_CRIMINAL_FRAMEWORK["primary_legislation"]]
        assert any("Crimes Act 1958" in a for a in acts)

    def test_vic_framework_has_sentencing_act(self):
        acts = [a["act"] for a in VIC_CRIMINAL_FRAMEWORK["primary_legislation"]]
        assert any("Sentencing Act 1991" in a for a in acts)

    def test_vic_framework_has_evidence_act(self):
        acts = [a["act"] for a in VIC_CRIMINAL_FRAMEWORK["primary_legislation"]]
        assert any("Evidence Act 2008" in a for a in acts)

    def test_vic_framework_injected(self):
        case = {"offence_category": "assault", "state": "vic"}
        context = get_offence_context(case)
        assert "Crimes Act 1958" in context
        assert "Sentencing Act 1991" in context

    def test_qld_framework_has_criminal_code_1899(self):
        acts = [a["act"] for a in QLD_CRIMINAL_FRAMEWORK["primary_legislation"]]
        assert any("Criminal Code Act 1899" in a for a in acts)

    def test_qld_framework_has_penalties_sentences(self):
        acts = [a["act"] for a in QLD_CRIMINAL_FRAMEWORK["primary_legislation"]]
        assert any("Penalties and Sentences Act 1992" in a for a in acts)

    def test_qld_framework_injected(self):
        case = {"offence_category": "homicide", "state": "qld"}
        context = get_offence_context(case)
        assert "Criminal Code Act 1899" in context
        assert "Penalties and Sentences Act 1992" in context

    def test_sa_framework_has_clca_1935(self):
        acts = [a["act"] for a in SA_CRIMINAL_FRAMEWORK["primary_legislation"]]
        assert any("Criminal Law Consolidation Act 1935" in a for a in acts)

    def test_sa_framework_has_sentencing_act(self):
        acts = [a["act"] for a in SA_CRIMINAL_FRAMEWORK["primary_legislation"]]
        assert any("Sentencing Act 2017" in a for a in acts)

    def test_sa_framework_injected(self):
        case = {"offence_category": "assault", "state": "sa"}
        context = get_offence_context(case)
        assert "Criminal Law Consolidation Act 1935" in context
        assert "Sentencing Act 2017" in context

    def test_wa_framework_has_criminal_code_1913(self):
        acts = [a["act"] for a in WA_CRIMINAL_FRAMEWORK["primary_legislation"]]
        assert any("Criminal Code Act Compilation Act 1913" in a for a in acts)

    def test_wa_framework_has_sentencing_act(self):
        acts = [a["act"] for a in WA_CRIMINAL_FRAMEWORK["primary_legislation"]]
        assert any("Sentencing Act 1995" in a for a in acts)

    def test_wa_framework_injected(self):
        case = {"offence_category": "domestic_violence", "state": "wa"}
        context = get_offence_context(case)
        assert "Criminal Code Act Compilation Act 1913" in context
        assert "Sentencing Act 1995" in context

    def test_tas_framework_has_criminal_code_1924(self):
        acts = [a["act"] for a in TAS_CRIMINAL_FRAMEWORK["primary_legislation"]]
        assert any("Criminal Code Act 1924" in a for a in acts)

    def test_tas_framework_has_sentencing_act(self):
        acts = [a["act"] for a in TAS_CRIMINAL_FRAMEWORK["primary_legislation"]]
        assert any("Sentencing Act 1997" in a for a in acts)

    def test_tas_framework_has_evidence_act(self):
        acts = [a["act"] for a in TAS_CRIMINAL_FRAMEWORK["primary_legislation"]]
        assert any("Evidence Act 2001" in a for a in acts)

    def test_tas_framework_injected(self):
        case = {"offence_category": "homicide", "state": "tas"}
        context = get_offence_context(case)
        assert "Criminal Code Act 1924" in context
        assert "Sentencing Act 1997" in context

    def test_nt_framework_has_criminal_code_1983(self):
        acts = [a["act"] for a in NT_CRIMINAL_FRAMEWORK["primary_legislation"]]
        assert any("Criminal Code Act 1983" in a for a in acts)

    def test_nt_framework_has_sentencing_act(self):
        acts = [a["act"] for a in NT_CRIMINAL_FRAMEWORK["primary_legislation"]]
        assert any("Sentencing Act 1995" in a for a in acts)

    def test_nt_framework_injected(self):
        case = {"offence_category": "drug_offences", "state": "nt"}
        context = get_offence_context(case)
        assert "Criminal Code Act 1983" in context
        assert "Sentencing Act 1995" in context

    def test_act_framework_has_criminal_code_2002(self):
        acts = [a["act"] for a in ACT_CRIMINAL_FRAMEWORK["primary_legislation"]]
        assert any("Criminal Code 2002" in a for a in acts)

    def test_act_framework_has_crimes_act_1900(self):
        acts = [a["act"] for a in ACT_CRIMINAL_FRAMEWORK["primary_legislation"]]
        assert any("Crimes Act 1900" in a for a in acts)

    def test_act_framework_injected(self):
        case = {"offence_category": "fraud_dishonesty", "state": "act"}
        context = get_offence_context(case)
        assert "Criminal Code 2002" in context
        assert "Crimes Act 1900 (ACT)" in context


class TestFederalFramework:
    """Verify the Commonwealth/Federal criminal framework."""

    def test_criminal_code_act_1995(self):
        acts = [a["act"] for a in FEDERAL_CRIMINAL_FRAMEWORK["primary_legislation"]]
        assert any("Criminal Code Act 1995" in a for a in acts)

    def test_crimes_act_1914(self):
        acts = [a["act"] for a in FEDERAL_CRIMINAL_FRAMEWORK["primary_legislation"]]
        assert any("Crimes Act 1914" in a for a in acts)

    def test_judiciary_act_1903(self):
        acts = [a["act"] for a in FEDERAL_CRIMINAL_FRAMEWORK["primary_legislation"]]
        assert any("Judiciary Act 1903" in a for a in acts)

    def test_dpp_act_1983(self):
        acts = [a["act"] for a in FEDERAL_CRIMINAL_FRAMEWORK["primary_legislation"]]
        assert any("Director of Public Prosecutions Act 1983" in a for a in acts)

    def test_federal_framework_always_injected(self):
        # Federal framework should appear for ANY state
        for state in ["nsw", "vic", "qld", "sa", "wa", "tas", "nt", "act"]:
            case = {"offence_category": "homicide", "state": state}
            context = get_offence_context(case)
            assert "COMMONWEALTH/FEDERAL CRIMINAL LEGISLATIVE FRAMEWORK" in context, f"Federal framework missing for {state}"
            assert "Criminal Code Act 1995 (Cth)" in context, f"Criminal Code Act 1995 missing for {state}"
            assert "Crimes Act 1914 (Cth)" in context, f"Crimes Act 1914 missing for {state}"


class TestUserProvidedPrimaryActs:
    """Verify the exact list of primary Acts the user specified."""

    def test_crimes_act_1914_cth(self):
        acts = [a["act"] for a in FEDERAL_CRIMINAL_FRAMEWORK["primary_legislation"]]
        assert any("Crimes Act 1914 (Cth)" in a for a in acts)

    def test_crimes_act_1900_act(self):
        acts = [a["act"] for a in ACT_CRIMINAL_FRAMEWORK["primary_legislation"]]
        assert any("Crimes Act 1900 (ACT)" in a for a in acts)

    def test_crimes_act_1900_nsw(self):
        acts = [a["act"] for a in NSW_CRIMINAL_FRAMEWORK["primary_legislation"]]
        assert any("Crimes Act 1900" in a for a in acts)

    def test_criminal_code_1899_qld(self):
        acts = [a["act"] for a in QLD_CRIMINAL_FRAMEWORK["primary_legislation"]]
        assert any("Criminal Code Act 1899 (Qld)" in a for a in acts)

    def test_criminal_code_1924_tas(self):
        acts = [a["act"] for a in TAS_CRIMINAL_FRAMEWORK["primary_legislation"]]
        assert any("Criminal Code Act 1924 (Tas)" in a for a in acts)

    def test_criminal_code_compilation_1913_wa(self):
        acts = [a["act"] for a in WA_CRIMINAL_FRAMEWORK["primary_legislation"]]
        assert any("Criminal Code Act Compilation Act 1913 (WA)" in a for a in acts)

    def test_criminal_code_act_1995_cth(self):
        acts = [a["act"] for a in FEDERAL_CRIMINAL_FRAMEWORK["primary_legislation"]]
        assert any("Criminal Code Act 1995 (Cth)" in a for a in acts)

    def test_criminal_code_2002_act(self):
        acts = [a["act"] for a in ACT_CRIMINAL_FRAMEWORK["primary_legislation"]]
        assert any("Criminal Code 2002 (ACT)" in a for a in acts)

    def test_criminal_code_act_1983_nt(self):
        acts = [a["act"] for a in NT_CRIMINAL_FRAMEWORK["primary_legislation"]]
        assert any("Criminal Code Act 1983 (NT)" in a for a in acts)

    def test_criminal_law_consolidation_act_1935_sa(self):
        acts = [a["act"] for a in SA_CRIMINAL_FRAMEWORK["primary_legislation"]]
        assert any("Criminal Law Consolidation Act 1935 (SA)" in a for a in acts)

    def test_crimes_act_1958_vic(self):
        acts = [a["act"] for a in VIC_CRIMINAL_FRAMEWORK["primary_legislation"]]
        assert any("Crimes Act 1958 (Vic)" in a for a in acts)


class TestNoNSWFallbacks:
    """Ensure NO code-level fallbacks to NSW or homicide exist."""

    def test_wa_context_no_nsw_crimes_act(self):
        wa_case = {'state': 'wa', 'offence_category': 'domestic_violence', 'offence_type': 'Common Assault (DV)'}
        ctx = get_offence_context(wa_case)
        assert 'Crimes Act 1900 (NSW)' not in ctx, 'NSW Crimes Act found in WA context!'

    def test_qld_context_no_nsw_crimes_act(self):
        qld_case = {'state': 'qld', 'offence_category': 'assault', 'offence_type': 'GBH'}
        ctx = get_offence_context(qld_case)
        assert 'Crimes Act 1900 (NSW)' not in ctx, 'NSW Crimes Act found in QLD context!'

    def test_sa_context_no_nsw_crimes_act(self):
        sa_case = {'state': 'sa', 'offence_category': 'homicide', 'offence_type': 'Murder'}
        ctx = get_offence_context(sa_case)
        assert 'Crimes Act 1900 (NSW)' not in ctx, 'NSW Crimes Act found in SA context!'

    def test_empty_state_no_nsw_default(self):
        empty_case = {'state': '', 'offence_category': 'assault'}
        ctx = get_offence_context(empty_case)
        assert 'Crimes Act 1900 (NSW)' not in ctx, 'NSW Crimes Act crept in with empty state!'

    def test_none_state_no_nsw_default(self):
        none_case = {'offence_category': 'assault'}
        ctx = get_offence_context(none_case)
        assert 'Crimes Act 1900 (NSW)' not in ctx, 'NSW Crimes Act crept in with None state!'

    def test_system_prompt_wa_no_nsw(self):
        prompt = get_offence_system_prompt('domestic_violence', 'wa')
        assert 'Western Australia' in prompt
        assert 'New South Wales' not in prompt

    def test_system_prompt_empty_state_flags_unconfirmed(self):
        prompt = get_offence_system_prompt('assault', '')
        assert 'not been confirmed' in prompt.lower() or 'unconfirmed' in prompt.lower() or 'flag this' in prompt.lower()

    def test_export_refs_wa_no_nsw(self):
        from services.offence_helpers import get_export_legal_refs
        refs = get_export_legal_refs('wa')
        refs_str = ' '.join(refs)
        assert 'WA' in refs_str
        assert 'Crimes Act 1900 (NSW)' not in refs_str

    def test_export_refs_empty_no_nsw(self):
        from services.offence_helpers import get_export_legal_refs
        refs = get_export_legal_refs('')
        refs_str = ' '.join(refs)
        assert 'Crimes Act 1900 (NSW)' not in refs_str
        assert 'Unspecified' in refs_str

    def test_offence_context_no_homicide_fallback(self):
        """Ensure unknown offence_category doesn't fall back to homicide."""
        case = {'state': 'vic', 'offence_category': 'nonexistent_category'}
        ctx = get_offence_context(case)
        # Should NOT contain homicide-specific keys or elements
        assert 'Category: Homicide' not in ctx


class TestLegislativeAuditFixes:
    """Verify corrections from the deep legislative audit."""

    def test_qld_no_criminal_appeal_act_1912(self):
        """QLD does NOT have a Criminal Appeal Act 1912 - that's NSW only."""
        specs = [s["act"] for s in QLD_CRIMINAL_FRAMEWORK["specialised_legislation"]]
        assert not any("Criminal Appeal Act 1912" in s for s in specs), \
            "QLD incorrectly references Criminal Appeal Act 1912 (NSW-only legislation)"

    def test_qld_has_correct_appeal_provisions(self):
        """QLD appeals are via Criminal Code Act 1899 Schedule 1 Chapter LXVIII."""
        specs = [s["act"] for s in QLD_CRIMINAL_FRAMEWORK["specialised_legislation"]]
        assert any("Chapter LXVIII" in s or "Appeals" in s for s in specs), \
            "QLD missing correct Criminal Code appeals reference"

    def test_vic_no_criminal_appeal_act_1914(self):
        """VIC Criminal Appeal Act 1914 has been superseded by Criminal Procedure Act 2009."""
        specs = [s["act"] for s in VIC_CRIMINAL_FRAMEWORK["specialised_legislation"]]
        assert not any(s == "Criminal Appeal Act 1914 (Vic)" for s in specs), \
            "VIC still references standalone Criminal Appeal Act 1914 (superseded)"

    def test_vic_has_criminal_procedure_appeal_entry(self):
        """VIC appeals are now governed by Criminal Procedure Act 2009 Part 6.3."""
        specs = [s["act"] for s in VIC_CRIMINAL_FRAMEWORK["specialised_legislation"]]
        assert any("Criminal Procedure Act 2009" in s and "Appeal" in s for s in specs), \
            "VIC missing Criminal Procedure Act 2009 appeals entry in specialised legislation"

    def test_sa_appeal_court_updated(self):
        """SA Court of Appeal was established 1 January 2021."""
        sa_info = AUSTRALIAN_STATES["sa"]
        assert "Court of Appeal" in sa_info["appeal_court"], \
            "SA appeal court should reference Court of Appeal (est. 2021)"

    def test_sa_appeal_time_limit_21_days(self):
        """SA appeal time limit is 21 days."""
        sa_appeal = APPEAL_FRAMEWORK["sa"]
        assert "21 days" in sa_appeal["time_limits"]["notice_of_appeal"]

    def test_nt_recent_updates_not_empty(self):
        """NT should now have recent legislation entries."""
        assert len(RECENT_LEGISLATION_UPDATES["nt"]) >= 3

    def test_act_recent_updates_not_empty(self):
        """ACT should now have recent legislation entries."""
        assert len(RECENT_LEGISLATION_UPDATES["act"]) >= 3

    def test_nt_context_includes_recent_leg(self):
        """NT cases should inject recent legislation into AI context."""
        case = {"offence_category": "assault", "state": "nt"}
        context = get_offence_context(case)
        assert "RECENT LEGISLATION UPDATES" in context
        assert "Youth Justice" in context

    def test_act_context_includes_recent_leg(self):
        """ACT cases should inject recent legislation into AI context."""
        case = {"offence_category": "sexual_offences", "state": "act"}
        context = get_offence_context(case)
        assert "RECENT LEGISLATION UPDATES" in context
        assert "Disclosure" in context or "Age of Criminal Responsibility" in context

    def test_no_fabricated_acts_in_any_framework(self):
        """Verify none of the frameworks contain known incorrect Act names."""
        all_specs = []
        for fw in [NSW_CRIMINAL_FRAMEWORK, VIC_CRIMINAL_FRAMEWORK, QLD_CRIMINAL_FRAMEWORK,
                    SA_CRIMINAL_FRAMEWORK, WA_CRIMINAL_FRAMEWORK, TAS_CRIMINAL_FRAMEWORK,
                    NT_CRIMINAL_FRAMEWORK, ACT_CRIMINAL_FRAMEWORK]:
            for spec in fw.get("specialised_legislation", []):
                all_specs.append(spec["act"])
        # Known incorrect references that should not appear
        assert not any("Criminal Appeal Act 1912 (Qld)" in s for s in all_specs), "QLD has fabricated Criminal Appeal Act 1912"
        assert not any(s == "Criminal Appeal Act 1914 (Vic)" for s in all_specs), "VIC has superseded Criminal Appeal Act 1914"


    def test_wa_has_wa_legislation(self):
        wa_case = {'state': 'wa', 'offence_category': 'domestic_violence'}
        ctx = get_offence_context(wa_case)
        assert 'Criminal Code Act Compilation Act 1913 (WA)' in ctx

    def test_vic_has_vic_legislation(self):
        vic_case = {'state': 'vic', 'offence_category': 'assault'}
        ctx = get_offence_context(vic_case)
        assert 'Crimes Act 1958 (Vic)' in ctx

class TestForensicLanguageFilter:
    """Ensure over-assertive declarative phrases are rewritten to forensic appellate language."""

    def test_trial_judge_erred(self):
        from services.offence_helpers import enforce_forensic_language
        result = enforce_forensic_language("The trial judge erred in failing to consider.")
        assert "It is arguable that the trial judge erred" in result

    def test_conviction_unsafe(self):
        from services.offence_helpers import enforce_forensic_language
        result = enforce_forensic_language("The conviction is unsafe because the jury was misdirected.")
        assert "It is arguable that the conviction is unsafe" in result

    def test_sentence_manifestly_excessive(self):
        from services.offence_helpers import enforce_forensic_language
        result = enforce_forensic_language("The sentence is manifestly excessive.")
        assert "It is arguable that the sentence is manifestly excessive" in result

    def test_denied_fair_trial(self):
        from services.offence_helpers import enforce_forensic_language
        result = enforce_forensic_language("The applicant was denied a fair trial.")
        assert "arguably denied a fair trial" in result

    def test_miscarriage_of_justice(self):
        from services.offence_helpers import enforce_forensic_language
        result = enforce_forensic_language("This constituted a miscarriage of justice.")
        assert "arguably constituted" in result

    def test_preserves_precedent_citation(self):
        from services.offence_helpers import enforce_forensic_language
        text = "In R v Smith, the Court held that the trial judge erred."
        result = enforce_forensic_language(text)
        assert "the Court held that the trial judge erred" in result

    def test_preserves_already_forensic(self):
        from services.offence_helpers import enforce_forensic_language
        text = "It is arguable that the trial judge erred in law."
        result = enforce_forensic_language(text)
        assert result == text

    def test_no_double_forensic(self):
        from services.offence_helpers import enforce_forensic_language
        result = enforce_forensic_language("It is arguable that it is arguable that the judge erred.")
        assert "arguable that it is arguable" not in result

    def test_empty_string(self):
        from services.offence_helpers import enforce_forensic_language
        assert enforce_forensic_language("") == ""
        assert enforce_forensic_language(None) is None

    def test_prosecution_failed(self):
        from services.offence_helpers import enforce_forensic_language
        result = enforce_forensic_language("The prosecution failed to disclose evidence.")
        assert "It is arguable that the prosecution failed" in result

    def test_defence_counsel_failed(self):
        from services.offence_helpers import enforce_forensic_language
        result = enforce_forensic_language("Defence counsel failed to object.")
        assert "It is arguable that defence counsel failed" in result
