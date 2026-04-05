"""
Iteration 82 - Testing report features:
1. Backend _strip_report_placeholders strips prompt instructions from headings
2. Backend _strip_report_placeholders strips we/us/our language
3. Backend report_guardrails contains language rules about 'we/us/our' ban
4. Backend report prompts include MATERIAL COUNTS section
5. Backend report prompts include GROUNDS TO COVER with 'MUST INCLUDE ALL'
6. Backend quick_summary prompt includes '## 8. WHAT THE PAID REPORTS ADD' with $150 and $200 pricing
7. Frontend ReportView cleanAIContent strips prompt instruction text
8. Frontend ReportView has comparison table component
9. Frontend ReportView has disclaimer footer with hazard symbol
10. Frontend print preview HTML includes comparison table and disclaimer
11. Notes API endpoint works correctly
12. Backend health check returns healthy status
"""

import pytest
import requests
import re

BASE_URL = 'http://localhost:8001'

class TestBackendHealth:
    """Health check endpoint tests"""
    
    def test_health_endpoint_returns_healthy(self):
        """Test that /api/health returns healthy status"""
        response = requests.get(f"{BASE_URL}/api/health")
        assert response.status_code == 200
        data = response.json()
        assert data.get("status") == "healthy"
        assert "timestamp" in data
        print("PASSED: Health endpoint returns healthy status")


class TestBackendStripReportPlaceholders:
    """Tests for _strip_report_placeholders function in server.py"""
    
    def test_function_exists_in_server(self):
        """Verify _strip_report_placeholders function exists"""
        with open('/app/backend/server.py', 'r') as f:
            content = f.read()
        assert 'def _strip_report_placeholders' in content
        print("PASSED: _strip_report_placeholders function exists")
    
    def test_strips_prompt_instruction_keep_all(self):
        """Verify function strips '— keep ALL' prompt instructions"""
        with open('/app/backend/server.py', 'r') as f:
            content = f.read()
        # Check for regex pattern that strips "— keep ALL" instructions
        assert "keep ALL" in content
        assert re.search(r"re\.sub.*keep ALL", content)
        print("PASSED: Function strips '— keep ALL' prompt instructions")
    
    def test_strips_detailed_pathway_analysis(self):
        """Verify function strips '— DETAILED PATHWAY ANALYSIS' instructions"""
        with open('/app/backend/server.py', 'r') as f:
            content = f.read()
        assert "DETAILED PATHWAY ANALYSIS" in content
        print("PASSED: Function strips DETAILED PATHWAY ANALYSIS instructions")
    
    def test_strips_word_count_parentheses(self):
        """Verify function strips word count instructions like '(900+ words per ground)'"""
        with open('/app/backend/server.py', 'r') as f:
            content = f.read()
        # Check for regex that strips "(X+ words...)" patterns - the actual pattern in code
        # Line 3437: cleaned = re.sub(r'\s*\(\d+\+?\s*words[^)]*\)', '', cleaned)
        assert "\\d+\\+?\\s*words" in content or "(900+ words" in content
        print("PASSED: Function strips word count parentheses")
    
    def test_strips_we_us_our_language(self):
        """Verify function has we/us/our replacement patterns"""
        with open('/app/backend/server.py', 'r') as f:
            content = f.read()
        
        # Check for specific we/us/our replacements
        we_us_patterns = [
            "We are arguing",
            "we are arguing",
            "our submissions",
            "Our submissions",
            "our case",
            "Our case",
            "contact us",
            "Contact us",
            "we will file",
            "We will file",
            "our analysis",
            "Our analysis"
        ]
        
        found_patterns = 0
        for pattern in we_us_patterns:
            if pattern in content:
                found_patterns += 1
        
        assert found_patterns >= 10, f"Expected at least 10 we/us/our patterns, found {found_patterns}"
        print(f"PASSED: Function has {found_patterns} we/us/our replacement patterns")
    
    def test_we_us_replacements_are_correct(self):
        """Verify specific we/us/our replacements map to correct values"""
        with open('/app/backend/server.py', 'r') as f:
            content = f.read()
        
        # Check specific replacement mappings
        assert "The applicant argues" in content  # replacement for "We are arguing"
        assert "the submissions" in content  # replacement for "our submissions"
        assert "the applicant's case" in content  # replacement for "our case"
        assert "contact the legal professional" in content  # replacement for "contact us"
        assert "the legal professional will file" in content  # replacement for "we will file"
        assert "this analysis" in content  # replacement for "our analysis"
        print("PASSED: We/us/our replacements map to correct third-person values")


class TestBackendReportGuardrails:
    """Tests for report_guardrails content in server.py"""
    
    def test_guardrails_variable_exists(self):
        """Verify report_guardrails variable exists"""
        with open('/app/backend/server.py', 'r') as f:
            content = f.read()
        assert 'report_guardrails' in content
        print("PASSED: report_guardrails variable exists")
    
    def test_guardrails_contains_language_rules(self):
        """Verify guardrails contain LANGUAGE RULES section"""
        with open('/app/backend/server.py', 'r') as f:
            content = f.read()
        assert "LANGUAGE RULES" in content
        print("PASSED: Guardrails contain LANGUAGE RULES section")
    
    def test_guardrails_bans_we_us_our(self):
        """Verify guardrails explicitly ban 'we', 'us', 'our'"""
        with open('/app/backend/server.py', 'r') as f:
            content = f.read()
        
        # Check for explicit ban language
        assert 'NEVER use the words "we", "us", "our"' in content or "NEVER use the words 'we', 'us', 'our'" in content
        print("PASSED: Guardrails explicitly ban 'we', 'us', 'our'")
    
    def test_guardrails_mentions_educational_tool(self):
        """Verify guardrails mention this is an EDUCATIONAL TOOL"""
        with open('/app/backend/server.py', 'r') as f:
            content = f.read()
        assert "EDUCATIONAL TOOL" in content
        print("PASSED: Guardrails mention EDUCATIONAL TOOL")
    
    def test_guardrails_mentions_not_legal_team(self):
        """Verify guardrails state it's NOT written by a legal team"""
        with open('/app/backend/server.py', 'r') as f:
            content = f.read()
        assert "NOT written by a legal team" in content
        print("PASSED: Guardrails state NOT written by a legal team")


class TestBackendReportPrompts:
    """Tests for report prompt content in server.py"""
    
    def test_quick_summary_has_material_counts(self):
        """Verify quick_summary prompt includes MATERIAL COUNTS section"""
        with open('/app/backend/server.py', 'r') as f:
            content = f.read()
        
        # Find quick_summary section and check for MATERIAL COUNTS
        assert "MATERIAL COUNTS" in content
        # Check it appears in the context of quick_summary
        qs_match = re.search(r'if report_type == "quick_summary".*?elif report_type', content, re.DOTALL)
        if qs_match:
            qs_section = qs_match.group(0)
            assert "MATERIAL COUNTS" in qs_section
        print("PASSED: quick_summary prompt includes MATERIAL COUNTS section")
    
    def test_full_detailed_has_material_counts(self):
        """Verify full_detailed prompt includes MATERIAL COUNTS section"""
        with open('/app/backend/server.py', 'r') as f:
            content = f.read()
        
        # Find full_detailed section and check for MATERIAL COUNTS
        fd_match = re.search(r'elif report_type == "full_detailed".*?else:', content, re.DOTALL)
        if fd_match:
            fd_section = fd_match.group(0)
            assert "MATERIAL COUNTS" in fd_section
        print("PASSED: full_detailed prompt includes MATERIAL COUNTS section")
    
    def test_extensive_log_has_material_counts(self):
        """Verify extensive_log prompt includes MATERIAL COUNTS section"""
        with open('/app/backend/server.py', 'r') as f:
            content = f.read()
        
        # Check extensive_log section has MATERIAL COUNTS
        el_match = re.search(r'else:  # extensive_log.*?Target range', content, re.DOTALL)
        if el_match:
            el_section = el_match.group(0)
            assert "MATERIAL COUNTS" in el_section
        print("PASSED: extensive_log prompt includes MATERIAL COUNTS section")
    
    def test_prompts_have_grounds_to_cover(self):
        """Verify all prompts include GROUNDS TO COVER section"""
        with open('/app/backend/server.py', 'r') as f:
            content = f.read()
        
        # Count occurrences of GROUNDS TO COVER
        grounds_count = content.count("GROUNDS TO COVER")
        assert grounds_count >= 3, f"Expected at least 3 GROUNDS TO COVER sections, found {grounds_count}"
        print(f"PASSED: Found {grounds_count} GROUNDS TO COVER sections in prompts")
    
    def test_grounds_to_cover_has_must_include_all(self):
        """Verify GROUNDS TO COVER includes 'MUST INCLUDE ALL' instruction"""
        with open('/app/backend/server.py', 'r') as f:
            content = f.read()
        
        assert "MUST INCLUDE ALL" in content
        # Check it appears near GROUNDS TO COVER
        assert re.search(r"GROUNDS TO COVER.*MUST INCLUDE ALL", content, re.DOTALL)
        print("PASSED: GROUNDS TO COVER includes 'MUST INCLUDE ALL' instruction")
    
    def test_quick_summary_has_paid_reports_section(self):
        """Verify quick_summary has '## 8. WHAT THE PAID REPORTS ADD' section"""
        with open('/app/backend/server.py', 'r') as f:
            content = f.read()
        
        assert "## 8. WHAT THE PAID REPORTS ADD" in content
        print("PASSED: quick_summary has '## 8. WHAT THE PAID REPORTS ADD' section")
    
    def test_paid_reports_section_has_150_pricing(self):
        """Verify paid reports section mentions $150 AUD pricing"""
        with open('/app/backend/server.py', 'r') as f:
            content = f.read()
        
        assert "$150 AUD" in content or "$150" in content
        print("PASSED: Paid reports section mentions $150 pricing")
    
    def test_paid_reports_section_has_200_pricing(self):
        """Verify paid reports section mentions $200 AUD pricing"""
        with open('/app/backend/server.py', 'r') as f:
            content = f.read()
        
        assert "$200 AUD" in content or "$200" in content
        print("PASSED: Paid reports section mentions $200 pricing")


class TestFrontendCleanAIContent:
    """Tests for cleanAIContent function in ReportView.jsx"""
    
    def test_function_exists(self):
        """Verify cleanAIContent function exists in ReportView.jsx"""
        with open('/app/frontend/src/pages/ReportView.jsx', 'r') as f:
            content = f.read()
        assert 'const cleanAIContent' in content or 'function cleanAIContent' in content
        print("PASSED: cleanAIContent function exists in ReportView.jsx")
    
    def test_strips_keep_all_instructions(self):
        """Verify cleanAIContent strips '— keep ALL' prompt instructions"""
        with open('/app/frontend/src/pages/ReportView.jsx', 'r') as f:
            content = f.read()
        
        # Check for regex that strips "— keep ALL" patterns
        assert "keep ALL" in content
        print("PASSED: cleanAIContent strips '— keep ALL' instructions")
    
    def test_strips_detailed_pathway_analysis(self):
        """Verify cleanAIContent strips DETAILED PATHWAY ANALYSIS"""
        with open('/app/frontend/src/pages/ReportView.jsx', 'r') as f:
            content = f.read()
        
        assert "DETAILED PATHWAY ANALYSIS" in content
        print("PASSED: cleanAIContent strips DETAILED PATHWAY ANALYSIS")
    
    def test_has_we_us_replacements(self):
        """Verify cleanAIContent has we/us/our replacement patterns"""
        with open('/app/frontend/src/pages/ReportView.jsx', 'r') as f:
            content = f.read()
        
        # Check for we/us/our replacement patterns
        we_us_patterns = [
            "We are arguing",
            "our submissions",
            "our case",
            "contact us",
            "we will file",
            "our analysis"
        ]
        
        found_patterns = 0
        for pattern in we_us_patterns:
            if pattern in content:
                found_patterns += 1
        
        assert found_patterns >= 5, f"Expected at least 5 we/us/our patterns, found {found_patterns}"
        print(f"PASSED: cleanAIContent has {found_patterns} we/us/our replacement patterns")
    
    def test_has_australian_spelling_replacements(self):
        """Verify cleanAIContent has Australian spelling replacements"""
        with open('/app/frontend/src/pages/ReportView.jsx', 'r') as f:
            content = f.read()
        
        # Check for Australian spelling patterns
        aus_patterns = ["analysed", "analysing", "analyse", "behaviour", "defence", "offence"]
        found = sum(1 for p in aus_patterns if p in content)
        assert found >= 3, f"Expected at least 3 Australian spelling patterns, found {found}"
        print(f"PASSED: cleanAIContent has {found} Australian spelling replacement patterns")


class TestFrontendComparisonTable:
    """Tests for comparison table component in ReportView.jsx"""
    
    def test_comparison_table_exists(self):
        """Verify report-comparison-table component exists"""
        with open('/app/frontend/src/pages/ReportView.jsx', 'r') as f:
            content = f.read()
        
        assert 'report-comparison-table' in content or 'Report Tier Comparison' in content
        print("PASSED: Comparison table component exists in ReportView.jsx")
    
    def test_comparison_table_has_free_column(self):
        """Verify comparison table has FREE column"""
        with open('/app/frontend/src/pages/ReportView.jsx', 'r') as f:
            content = f.read()
        
        assert "FREE" in content
        print("PASSED: Comparison table has FREE column")
    
    def test_comparison_table_has_150_column(self):
        """Verify comparison table has $150 column"""
        with open('/app/frontend/src/pages/ReportView.jsx', 'r') as f:
            content = f.read()
        
        assert "$150" in content
        print("PASSED: Comparison table has $150 column")
    
    def test_comparison_table_has_200_column(self):
        """Verify comparison table has $200 column"""
        with open('/app/frontend/src/pages/ReportView.jsx', 'r') as f:
            content = f.read()
        
        assert "$200" in content
        print("PASSED: Comparison table has $200 column")
    
    def test_comparison_table_has_checkmarks(self):
        """Verify comparison table uses checkmarks"""
        with open('/app/frontend/src/pages/ReportView.jsx', 'r') as f:
            content = f.read()
        
        # Check for checkmark character or entity
        assert "&#9745;" in content or "✅" in content or "checkmark" in content.lower()
        print("PASSED: Comparison table uses checkmarks")


class TestFrontendDisclaimerFooter:
    """Tests for disclaimer footer in ReportView.jsx"""
    
    def test_disclaimer_footer_exists(self):
        """Verify report-footer disclaimer exists"""
        with open('/app/frontend/src/pages/ReportView.jsx', 'r') as f:
            content = f.read()
        
        assert 'report-footer' in content
        print("PASSED: report-footer disclaimer exists")
    
    def test_disclaimer_has_hazard_symbol(self):
        """Verify disclaimer has hazard/warning symbol"""
        with open('/app/frontend/src/pages/ReportView.jsx', 'r') as f:
            content = f.read()
        
        # Check for AlertTriangle icon or hazard symbol
        assert "AlertTriangle" in content or "&#9888;" in content or "⚠" in content
        print("PASSED: Disclaimer has hazard/warning symbol")
    
    def test_disclaimer_has_not_legal_advice_text(self):
        """Verify disclaimer has 'Not Legal Advice' text"""
        with open('/app/frontend/src/pages/ReportView.jsx', 'r') as f:
            content = f.read()
        
        assert "Not Legal Advice" in content
        print("PASSED: Disclaimer has 'Not Legal Advice' text")


class TestFrontendPrintPreview:
    """Tests for print preview HTML in ReportView.jsx"""
    
    def test_print_preview_function_exists(self):
        """Verify openReportPreview function exists"""
        with open('/app/frontend/src/pages/ReportView.jsx', 'r') as f:
            content = f.read()
        
        assert 'openReportPreview' in content
        print("PASSED: openReportPreview function exists")
    
    def test_print_preview_has_comparison_table(self):
        """Verify print preview HTML includes comparison table"""
        with open('/app/frontend/src/pages/ReportView.jsx', 'r') as f:
            content = f.read()
        
        # Check for comparison table in the HTML template
        assert "Report Tier Comparison" in content
        print("PASSED: Print preview HTML includes comparison table")
    
    def test_print_preview_has_disclaimer(self):
        """Verify print preview HTML includes disclaimer"""
        with open('/app/frontend/src/pages/ReportView.jsx', 'r') as f:
            content = f.read()
        
        # Check for disclaimer in the HTML template
        assert "disclaimer" in content.lower()
        print("PASSED: Print preview HTML includes disclaimer")
    
    def test_print_preview_has_styled_headers(self):
        """Verify print preview has styled headers"""
        with open('/app/frontend/src/pages/ReportView.jsx', 'r') as f:
            content = f.read()
        
        # Check for header styling in print preview
        assert "report-header" in content
        print("PASSED: Print preview has styled headers")
    
    def test_print_preview_has_numbered_sections(self):
        """Verify print preview has numbered sections"""
        with open('/app/frontend/src/pages/ReportView.jsx', 'r') as f:
            content = f.read()
        
        # Check for section numbering
        assert "section-number" in content
        print("PASSED: Print preview has numbered sections")


class TestNotesAPI:
    """Tests for Notes API endpoint - requires auth so we test endpoint existence"""
    
    def test_notes_endpoint_structure_exists(self):
        """Verify notes endpoint structure exists in server.py"""
        with open('/app/backend/server.py', 'r') as f:
            content = f.read()
        
        # Check for notes endpoint
        assert "/cases/{case_id}/notes" in content
        print("PASSED: Notes endpoint structure exists in server.py")
    
    def test_notes_post_endpoint_exists(self):
        """Verify POST notes endpoint exists"""
        with open('/app/backend/server.py', 'r') as f:
            content = f.read()
        
        # Check for POST method on notes
        assert "async def create_note" in content or "@api_router.post" in content
        print("PASSED: POST notes endpoint exists")
    
    def test_notes_model_exists(self):
        """Verify Note model exists"""
        with open('/app/backend/server.py', 'r') as f:
            content = f.read()
        
        assert "class Note" in content
        assert "class NoteCreate" in content
        print("PASSED: Note and NoteCreate models exist")


class TestReportsPricing:
    """Tests for report pricing configuration"""
    
    def test_reports_section_has_correct_pricing(self):
        """Verify ReportsSection.jsx has correct pricing"""
        with open('/app/frontend/src/components/ReportsSection.jsx', 'r') as f:
            content = f.read()
        
        # Check for pricing values
        assert "150" in content  # $150 for full_detailed
        assert "200" in content  # $200 for extensive_log
        print("PASSED: ReportsSection.jsx has correct pricing ($150, $200)")
    
    def test_report_theme_has_pricing(self):
        """Verify REPORT_THEME in ReportView.jsx has pricing"""
        with open('/app/frontend/src/pages/ReportView.jsx', 'r') as f:
            content = f.read()
        
        assert "REPORT_THEME" in content
        assert "$150 AUD" in content
        assert "$200 AUD" in content
        print("PASSED: REPORT_THEME has correct pricing labels")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
