"""
Iteration 70 Tests - Report Prompt Restructuring and Barrister View Merging
Tests:
1. AUSTRALIAN_STATES has all 8 states with required URLs
2. Report prompts use state_info.get() for dynamic URLs
3. Quick Summary has 7 sections
4. Full Detailed has 15 sections with Client Brief as section 15 (LAST)
5. Extensive Log has 20 sections, 7000-10000 word target
6. Extensive Log context limits increased (total_doc_chars: 32000, per_doc_chars: 3200)
7. Aggressive mode mentions 15+ sentencing cases and 20+ precedent cases
8. BarristerView mergeAllReports function exists and works correctly
"""
import pytest
import requests
import os
import re

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://barrister-brief-1.preview.emergentagent.com')

# ============ BACKEND CODE VERIFICATION TESTS ============

class TestAustralianStatesConfig:
    """Test AUSTRALIAN_STATES dict in offence_framework.py"""
    
    def test_all_8_states_present(self):
        """Verify all 8 Australian states/territories are in AUSTRALIAN_STATES"""
        with open('/app/backend/offence_framework.py', 'r') as f:
            content = f.read()
        
        required_states = ['nsw', 'vic', 'qld', 'sa', 'wa', 'tas', 'nt', 'act']
        for state in required_states:
            assert f'"{state}"' in content or f"'{state}'" in content, f"State {state} not found in AUSTRALIAN_STATES"
        print(f"PASS: All 8 states present in AUSTRALIAN_STATES: {required_states}")
    
    def test_legal_aid_url_for_all_states(self):
        """Verify legal_aid_url exists for all states"""
        with open('/app/backend/offence_framework.py', 'r') as f:
            content = f.read()
        
        # Count legal_aid_url occurrences
        legal_aid_count = content.count('legal_aid_url')
        assert legal_aid_count >= 8, f"Expected 8+ legal_aid_url entries, found {legal_aid_count}"
        print(f"PASS: Found {legal_aid_count} legal_aid_url entries")
    
    def test_court_forms_url_for_all_states(self):
        """Verify court_forms_url exists for all states"""
        with open('/app/backend/offence_framework.py', 'r') as f:
            content = f.read()
        
        court_forms_count = content.count('court_forms_url')
        assert court_forms_count >= 8, f"Expected 8+ court_forms_url entries, found {court_forms_count}"
        print(f"PASS: Found {court_forms_count} court_forms_url entries")
    
    def test_cca_search_url_for_all_states(self):
        """Verify cca_search_url exists for all states"""
        with open('/app/backend/offence_framework.py', 'r') as f:
            content = f.read()
        
        cca_search_count = content.count('cca_search_url')
        assert cca_search_count >= 8, f"Expected 8+ cca_search_url entries, found {cca_search_count}"
        print(f"PASS: Found {cca_search_count} cca_search_url entries")
    
    def test_appeal_court_for_all_states(self):
        """Verify appeal_court exists for all states"""
        with open('/app/backend/offence_framework.py', 'r') as f:
            content = f.read()
        
        appeal_court_count = content.count('appeal_court')
        assert appeal_court_count >= 8, f"Expected 8+ appeal_court entries, found {appeal_court_count}"
        print(f"PASS: Found {appeal_court_count} appeal_court entries")
    
    def test_state_specific_urls_not_hardcoded_nsw(self):
        """Verify URLs are state-specific, not all NSW"""
        with open('/app/backend/offence_framework.py', 'r') as f:
            content = f.read()
        
        # Check for VIC-specific URL
        assert 'legalaid.vic.gov.au' in content, "VIC legal aid URL not found"
        # Check for QLD-specific URL
        assert 'legalaid.qld.gov.au' in content, "QLD legal aid URL not found"
        # Check for SA-specific URL
        assert 'lsc.sa.gov.au' in content, "SA legal aid URL not found"
        # Check for WA-specific URL
        assert 'legalaid.wa.gov.au' in content, "WA legal aid URL not found"
        print("PASS: State-specific URLs found for VIC, QLD, SA, WA")


class TestReportPromptsUseDynamicURLs:
    """Test that report prompts use state_info.get() for dynamic URLs"""
    
    def test_prompts_use_state_info_cca_search_url(self):
        """Verify prompts use state_info.get('cca_search_url') not hardcoded NSWCCA"""
        with open('/app/backend/server.py', 'r') as f:
            content = f.read()
        
        # Check for dynamic cca_search_url usage
        cca_dynamic_count = content.count("state_info.get('cca_search_url'")
        assert cca_dynamic_count >= 3, f"Expected 3+ state_info.get('cca_search_url') usages, found {cca_dynamic_count}"
        print(f"PASS: Found {cca_dynamic_count} dynamic cca_search_url usages")
    
    def test_prompts_use_state_info_legal_aid_url(self):
        """Verify prompts use state_info.get('legal_aid_url') not hardcoded legalaid.nsw"""
        with open('/app/backend/server.py', 'r') as f:
            content = f.read()
        
        legal_aid_dynamic_count = content.count("state_info.get('legal_aid_url'")
        assert legal_aid_dynamic_count >= 2, f"Expected 2+ state_info.get('legal_aid_url') usages, found {legal_aid_dynamic_count}"
        print(f"PASS: Found {legal_aid_dynamic_count} dynamic legal_aid_url usages")
    
    def test_prompts_use_state_info_court_forms_url(self):
        """Verify prompts use state_info.get('court_forms_url')"""
        with open('/app/backend/server.py', 'r') as f:
            content = f.read()
        
        court_forms_dynamic_count = content.count("state_info.get('court_forms_url'")
        assert court_forms_dynamic_count >= 2, f"Expected 2+ state_info.get('court_forms_url') usages, found {court_forms_dynamic_count}"
        print(f"PASS: Found {court_forms_dynamic_count} dynamic court_forms_url usages")
    
    def test_prompts_use_state_info_appeal_court(self):
        """Verify prompts use state_info.get('appeal_court')"""
        with open('/app/backend/server.py', 'r') as f:
            content = f.read()
        
        appeal_court_dynamic_count = content.count("state_info.get('appeal_court'")
        assert appeal_court_dynamic_count >= 3, f"Expected 3+ state_info.get('appeal_court') usages, found {appeal_court_dynamic_count}"
        print(f"PASS: Found {appeal_court_dynamic_count} dynamic appeal_court usages")


class TestQuickSummarySections:
    """Test Quick Summary has exactly 7 sections"""
    
    def test_quick_summary_has_7_sections(self):
        """Verify Quick Summary prompt has 7 sections"""
        with open('/app/backend/server.py', 'r') as f:
            content = f.read()
        
        # Find the quick_summary section
        quick_summary_start = content.find('if report_type == "quick_summary"')
        quick_summary_end = content.find('elif report_type == "full_detailed"')
        quick_summary_section = content[quick_summary_start:quick_summary_end]
        
        # Count section headings (## 1. through ## 7.)
        section_count = 0
        for i in range(1, 10):
            if f'## {i}.' in quick_summary_section:
                section_count += 1
        
        assert section_count == 7, f"Quick Summary should have 7 sections, found {section_count}"
        print(f"PASS: Quick Summary has {section_count} sections")
    
    def test_quick_summary_section_7_is_paid_reports(self):
        """Verify section 7 is 'WHAT THE PAID REPORTS ADD'"""
        with open('/app/backend/server.py', 'r') as f:
            content = f.read()
        
        assert '## 7. WHAT THE PAID REPORTS ADD' in content, "Section 7 should be 'WHAT THE PAID REPORTS ADD'"
        print("PASS: Section 7 is 'WHAT THE PAID REPORTS ADD'")


class TestFullDetailedSections:
    """Test Full Detailed has 15 sections with Client Brief as section 15 (LAST)"""
    
    def test_full_detailed_has_15_sections(self):
        """Verify Full Detailed prompt has 15 sections"""
        with open('/app/backend/server.py', 'r') as f:
            content = f.read()
        
        # Find the full_detailed section
        full_detailed_start = content.find('elif report_type == "full_detailed"')
        full_detailed_end = content.find('else:  # extensive_log')
        full_detailed_section = content[full_detailed_start:full_detailed_end]
        
        # Count section headings (## 1. through ## 15.)
        section_count = 0
        for i in range(1, 20):
            if f'## {i}.' in full_detailed_section:
                section_count += 1
        
        assert section_count == 15, f"Full Detailed should have 15 sections, found {section_count}"
        print(f"PASS: Full Detailed has {section_count} sections")
    
    def test_full_detailed_section_15_is_client_brief(self):
        """Verify section 15 is 'CLIENT PLAIN-ENGLISH BRIEF' and is LAST"""
        with open('/app/backend/server.py', 'r') as f:
            content = f.read()
        
        # Find the full_detailed section
        full_detailed_start = content.find('elif report_type == "full_detailed"')
        full_detailed_end = content.find('else:  # extensive_log')
        full_detailed_section = content[full_detailed_start:full_detailed_end]
        
        assert '## 15. CLIENT PLAIN-ENGLISH BRIEF' in full_detailed_section, "Section 15 should be 'CLIENT PLAIN-ENGLISH BRIEF'"
        
        # Verify it's the last section (no ## 16.)
        assert '## 16.' not in full_detailed_section, "Section 16 should not exist in Full Detailed"
        print("PASS: Section 15 is 'CLIENT PLAIN-ENGLISH BRIEF' and is the LAST section")


class TestExtensiveLogSections:
    """Test Extensive Log has 20 sections, 7000-10000 word target"""
    
    def test_extensive_log_has_20_sections(self):
        """Verify Extensive Log prompt has 20 sections"""
        with open('/app/backend/server.py', 'r') as f:
            content = f.read()
        
        # Find the extensive_log section
        extensive_start = content.find('else:  # extensive_log')
        extensive_end = content.find('if aggressive_mode:')
        extensive_section = content[extensive_start:extensive_end]
        
        # Count section headings (## 1. through ## 20.)
        section_count = 0
        for i in range(1, 25):
            if f'## {i}.' in extensive_section:
                section_count += 1
        
        assert section_count == 20, f"Extensive Log should have 20 sections, found {section_count}"
        print(f"PASS: Extensive Log has {section_count} sections")
    
    def test_extensive_log_word_target_7000_10000(self):
        """Verify Extensive Log has 7000-10000 word target"""
        with open('/app/backend/server.py', 'r') as f:
            content = f.read()
        
        assert '7000-10000 words' in content, "Extensive Log should have 7000-10000 word target"
        print("PASS: Extensive Log has 7000-10000 word target")
    
    def test_extensive_log_section_20_is_client_brief(self):
        """Verify section 20 is 'CLIENT PLAIN-ENGLISH BRIEF' and is LAST"""
        with open('/app/backend/server.py', 'r') as f:
            content = f.read()
        
        # Find the extensive_log section
        extensive_start = content.find('else:  # extensive_log')
        extensive_end = content.find('if aggressive_mode:')
        extensive_section = content[extensive_start:extensive_end]
        
        assert '## 20. CLIENT PLAIN-ENGLISH BRIEF' in extensive_section, "Section 20 should be 'CLIENT PLAIN-ENGLISH BRIEF'"
        
        # Verify it's the last section (no ## 21.)
        assert '## 21.' not in extensive_section, "Section 21 should not exist in Extensive Log"
        print("PASS: Section 20 is 'CLIENT PLAIN-ENGLISH BRIEF' and is the LAST section")


class TestExtensiveLogContextLimits:
    """Test Extensive Log context limits increased"""
    
    def test_extensive_log_total_doc_chars_32000(self):
        """Verify extensive_log total_doc_chars is 32000"""
        with open('/app/backend/server.py', 'r') as f:
            content = f.read()
        
        # Find the context limits section
        assert '"total_doc_chars": 32000' in content, "extensive_log total_doc_chars should be 32000"
        print("PASS: extensive_log total_doc_chars is 32000")
    
    def test_extensive_log_per_doc_chars_3200(self):
        """Verify extensive_log per_doc_chars is 3200"""
        with open('/app/backend/server.py', 'r') as f:
            content = f.read()
        
        assert '"per_doc_chars": 3200' in content, "extensive_log per_doc_chars should be 3200"
        print("PASS: extensive_log per_doc_chars is 3200")


class TestAggressiveMode:
    """Test Aggressive mode mentions 15+ sentencing cases and 20+ precedent cases"""
    
    def test_aggressive_mode_15_sentencing_cases(self):
        """Verify aggressive mode mentions 15 sentencing cases"""
        with open('/app/backend/server.py', 'r') as f:
            content = f.read()
        
        # Find aggressive mode section
        aggressive_start = content.find('if aggressive_mode:')
        aggressive_end = content.find('# Call AI')
        aggressive_section = content[aggressive_start:aggressive_end]
        
        # Check for 15 cases in sentencing table
        assert '15 cases' in aggressive_section.lower() or 'at least 15' in aggressive_section.lower(), \
            "Aggressive mode should mention 15 sentencing cases"
        print("PASS: Aggressive mode mentions 15 sentencing cases")
    
    def test_aggressive_mode_20_precedent_cases(self):
        """Verify aggressive mode mentions 20+ precedent cases"""
        with open('/app/backend/server.py', 'r') as f:
            content = f.read()
        
        # Find aggressive mode section
        aggressive_start = content.find('if aggressive_mode:')
        aggressive_end = content.find('# Call AI')
        aggressive_section = content[aggressive_start:aggressive_end]
        
        # Check for 20+ cases in precedent matrix
        assert '20+' in aggressive_section or '20 cases' in aggressive_section.lower(), \
            "Aggressive mode should mention 20+ precedent cases"
        print("PASS: Aggressive mode mentions 20+ precedent cases")


class TestBarristerViewMergeAllReports:
    """Test BarristerView mergeAllReports function"""
    
    def test_barrister_view_fetches_all_reports(self):
        """Verify BarristerView fetches allReports via /api/cases/{caseId}/reports"""
        with open('/app/frontend/src/pages/BarristerView.jsx', 'r') as f:
            content = f.read()
        
        assert '/reports`' in content or '/reports)' in content, \
            "BarristerView should fetch all reports"
        assert 'allReports' in content, "BarristerView should have allReports state"
        print("PASS: BarristerView fetches allReports")
    
    def test_barrister_view_merge_all_reports_function_exists(self):
        """Verify mergeAllReports function exists"""
        with open('/app/frontend/src/pages/BarristerView.jsx', 'r') as f:
            content = f.read()
        
        assert 'mergeAllReports' in content, "mergeAllReports function should exist"
        print("PASS: mergeAllReports function exists")
    
    def test_merge_all_reports_uses_map_for_deduplication(self):
        """Verify mergeAllReports uses Map for deduplication by title"""
        with open('/app/frontend/src/pages/BarristerView.jsx', 'r') as f:
            content = f.read()
        
        # Check for Map usage
        assert 'new Map()' in content or 'sectionMap' in content, \
            "mergeAllReports should use Map for deduplication"
        print("PASS: mergeAllReports uses Map for deduplication")
    
    def test_merge_all_reports_keeps_longest_version(self):
        """Verify mergeAllReports keeps longest version of each section"""
        with open('/app/frontend/src/pages/BarristerView.jsx', 'r') as f:
            content = f.read()
        
        # Check for length comparison
        assert '.length' in content and 'content.length' in content, \
            "mergeAllReports should compare content lengths"
        print("PASS: mergeAllReports compares content lengths")
    
    def test_barrister_view_shows_merged_badge(self):
        """Verify BarristerView shows 'Merged from N reports' badge"""
        with open('/app/frontend/src/pages/BarristerView.jsx', 'r') as f:
            content = f.read()
        
        assert 'Merged from' in content or 'reportCount' in content, \
            "BarristerView should show merged reports badge"
        print("PASS: BarristerView shows merged reports indicator")
    
    def test_merge_all_reports_sequential_numbering(self):
        """Verify merged sections have sequential numbering"""
        with open('/app/frontend/src/pages/BarristerView.jsx', 'r') as f:
            content = f.read()
        
        # Check for re-numbering logic
        assert 'String(i + 1)' in content or 'number: String' in content, \
            "mergeAllReports should re-number sections sequentially"
        print("PASS: mergeAllReports re-numbers sections sequentially")


class TestAPIEndpoints:
    """Test API endpoints are working"""
    
    def test_health_endpoint(self):
        """Test health endpoint returns healthy status"""
        response = requests.get(f"{BASE_URL}/api/health")
        assert response.status_code == 200
        data = response.json()
        assert data.get('status') == 'healthy'
        assert data.get('database') == 'connected'
        print("PASS: Health endpoint returns healthy status")
    
    def test_login_endpoint(self):
        """Test login endpoint works with test credentials"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": "edittest2@example.com",
            "password": "TestPass123!"
        })
        assert response.status_code == 200
        data = response.json()
        assert 'user_id' in data
        print(f"PASS: Login successful, user_id: {data.get('user_id')}")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
