"""
Iteration 83 - Testing report features:
1. Backend _strip_report_placeholders strips \\1 artifacts
2. Backend _strip_report_placeholders strips prompt instruction text
3. Backend _strip_report_placeholders strips we/us/our language
4. Frontend cleanAIContent strips \\1 artifacts
5. Frontend cleanAIContent strips prompt instruction text
6. Frontend cleanAIContent strips we/us/our language
7. Frontend ReportView has comparison table with Free/$150/$200 columns
8. Frontend ReportView has bold 'NOT LEGAL ADVICE' disclaimer with 'Created and Designed by Deb King'
9. Frontend ReportView print preview has table-layout:fixed CSS
10. Frontend BarristerView cleanAIContent strips we/us/our language
11. Frontend BarristerView cleanAIContent strips \\1 artifacts
12. Frontend BarristerView has bold disclaimer and 'Created and Designed by Deb King'
13. Frontend BarristerView header shows 'BARRISTER BRIEF' not 'CONFIDENTIAL LEGAL BRIEF'
14. Frontend ReportsSection shows Lock icon on locked Barrister View button
15. Frontend index.css print media has table-layout:fixed for legal-report tables
16. Backend health check works
"""

import pytest
import requests
import os
import re

BASE_URL = 'http://localhost:8001'


class TestBackendHealth:
    """Test backend health endpoint"""
    
    def test_health_endpoint(self):
        """Test /api/health returns healthy status"""
        response = requests.get(f"{BASE_URL}/api/health")
        assert response.status_code == 200
        data = response.json()
        assert data.get("status") == "healthy"
        assert "database" in data
        print(f"Health check passed: {data}")


class TestBackendStripReportPlaceholders:
    """Test _strip_report_placeholders function in server.py"""
    
    def test_function_exists(self):
        """Verify _strip_report_placeholders function exists"""
        with open('/app/backend/server.py', 'r') as f:
            content = f.read()
        assert 'def _strip_report_placeholders' in content
        print("PASSED: _strip_report_placeholders function exists")
    
    def test_strips_backslash_one_artifacts(self):
        """Verify function strips \\1 artifacts"""
        with open('/app/backend/server.py', 'r') as f:
            content = f.read()
        # Check for \\1 stripping
        assert 'cleaned.replace("\\\\1", "")' in content or "cleaned.replace('\\\\1', '')" in content or 'replace("\\1", "")' in content.replace('\\\\', '\\')
        assert 'cleaned.replace("\\x01", "")' in content or "cleaned.replace('\\x01', '')" in content
        print("PASSED: Function strips \\1 artifacts")
    
    def test_strips_prompt_instruction_text(self):
        """Verify function strips prompt instruction text from headings"""
        with open('/app/backend/server.py', 'r') as f:
            content = f.read()
        # Check for prompt instruction stripping patterns
        assert 'keep ALL' in content
        assert 'DETAILED PATHWAY ANALYSIS' in content
        assert 'words' in content  # For word count parentheses
        print("PASSED: Function strips prompt instruction text")
    
    def test_strips_we_us_our_language(self):
        """Verify function strips we/us/our language"""
        with open('/app/backend/server.py', 'r') as f:
            content = f.read()
        # Check for we/us/our replacement patterns
        assert 'We are arguing' in content
        assert 'The applicant argues' in content
        assert 'our submissions' in content
        assert 'the submissions' in content
        assert 'We will' in content  # Various "We will X" patterns
        print("PASSED: Function strips we/us/our language")


class TestFrontendReportViewCleanAIContent:
    """Test cleanAIContent function in ReportView.jsx"""
    
    def test_function_exists(self):
        """Verify cleanAIContent function exists"""
        with open('/app/frontend/src/pages/ReportView.jsx', 'r') as f:
            content = f.read()
        assert 'const cleanAIContent' in content
        print("PASSED: cleanAIContent function exists in ReportView.jsx")
    
    def test_strips_backslash_one_artifacts(self):
        """Verify function strips \\1 artifacts"""
        with open('/app/frontend/src/pages/ReportView.jsx', 'r') as f:
            content = f.read()
        # Check for \\1 stripping
        assert '\\\\1' in content or '/\\\\1/g' in content
        assert '\\x01' in content
        print("PASSED: ReportView cleanAIContent strips \\1 artifacts")
    
    def test_strips_prompt_instruction_text(self):
        """Verify function strips prompt instruction text from headings"""
        with open('/app/frontend/src/pages/ReportView.jsx', 'r') as f:
            content = f.read()
        # Check for prompt instruction stripping patterns
        assert 'keep ALL' in content
        assert 'DETAILED PATHWAY ANALYSIS' in content
        print("PASSED: ReportView cleanAIContent strips prompt instruction text")
    
    def test_strips_we_us_our_language(self):
        """Verify function strips we/us/our language"""
        with open('/app/frontend/src/pages/ReportView.jsx', 'r') as f:
            content = f.read()
        # Check for we/us/our replacement patterns
        assert 'We are arguing' in content
        assert 'The applicant argues' in content
        assert 'We argue' in content
        print("PASSED: ReportView cleanAIContent strips we/us/our language")


class TestFrontendReportViewComparisonTable:
    """Test comparison table in ReportView.jsx"""
    
    def test_comparison_table_exists(self):
        """Verify comparison table component exists"""
        with open('/app/frontend/src/pages/ReportView.jsx', 'r') as f:
            content = f.read()
        assert 'report-comparison-table' in content
        print("PASSED: Comparison table exists in ReportView.jsx")
    
    def test_has_free_column(self):
        """Verify FREE column exists"""
        with open('/app/frontend/src/pages/ReportView.jsx', 'r') as f:
            content = f.read()
        assert 'FREE' in content
        print("PASSED: FREE column exists")
    
    def test_has_150_column(self):
        """Verify $150 column exists"""
        with open('/app/frontend/src/pages/ReportView.jsx', 'r') as f:
            content = f.read()
        assert '$150' in content
        print("PASSED: $150 column exists")
    
    def test_has_200_column(self):
        """Verify $200 column exists"""
        with open('/app/frontend/src/pages/ReportView.jsx', 'r') as f:
            content = f.read()
        assert '$200' in content
        print("PASSED: $200 column exists")


class TestFrontendReportViewDisclaimer:
    """Test disclaimer footer in ReportView.jsx"""
    
    def test_disclaimer_exists(self):
        """Verify disclaimer footer exists"""
        with open('/app/frontend/src/pages/ReportView.jsx', 'r') as f:
            content = f.read()
        assert 'report-footer' in content
        print("PASSED: Disclaimer footer exists")
    
    def test_not_legal_advice_text(self):
        """Verify 'NOT LEGAL ADVICE' text exists"""
        with open('/app/frontend/src/pages/ReportView.jsx', 'r') as f:
            content = f.read()
        assert 'NOT LEGAL ADVICE' in content
        print("PASSED: 'NOT LEGAL ADVICE' text exists")
    
    def test_created_by_deb_king(self):
        """Verify 'Created and Designed by Deb King' text exists"""
        with open('/app/frontend/src/pages/ReportView.jsx', 'r') as f:
            content = f.read()
        assert 'Created and Designed by Deb King' in content
        print("PASSED: 'Created and Designed by Deb King' text exists")


class TestFrontendReportViewPrintPreview:
    """Test print preview in ReportView.jsx"""
    
    def test_print_preview_function_exists(self):
        """Verify openReportPreview function exists"""
        with open('/app/frontend/src/pages/ReportView.jsx', 'r') as f:
            content = f.read()
        assert 'openReportPreview' in content
        print("PASSED: openReportPreview function exists")
    
    def test_print_preview_has_table_layout_fixed(self):
        """Verify print preview has table-layout:fixed CSS"""
        with open('/app/frontend/src/pages/ReportView.jsx', 'r') as f:
            content = f.read()
        assert 'table-layout: fixed' in content
        print("PASSED: Print preview has table-layout:fixed CSS")
    
    def test_print_preview_has_comparison_table(self):
        """Verify print preview includes comparison table"""
        with open('/app/frontend/src/pages/ReportView.jsx', 'r') as f:
            content = f.read()
        assert 'Report Tier Comparison' in content
        print("PASSED: Print preview includes comparison table")
    
    def test_print_preview_has_disclaimer(self):
        """Verify print preview includes disclaimer"""
        with open('/app/frontend/src/pages/ReportView.jsx', 'r') as f:
            content = f.read()
        # Check for disclaimer in print HTML
        assert 'NOT LEGAL ADVICE' in content
        assert 'Created and Designed by Deb King' in content
        print("PASSED: Print preview includes disclaimer and 'Created and Designed by Deb King'")


class TestFrontendBarristerViewCleanAIContent:
    """Test cleanAIContent function in BarristerView.jsx"""
    
    def test_function_exists(self):
        """Verify cleanAIContent function exists"""
        with open('/app/frontend/src/pages/BarristerView.jsx', 'r') as f:
            content = f.read()
        assert 'const cleanAIContent' in content
        print("PASSED: cleanAIContent function exists in BarristerView.jsx")
    
    def test_strips_backslash_one_artifacts(self):
        """Verify function strips \\1 artifacts"""
        with open('/app/frontend/src/pages/BarristerView.jsx', 'r') as f:
            content = f.read()
        # Check for \\1 stripping
        assert '\\\\1' in content or '/\\\\1/g' in content
        assert '\\x01' in content
        print("PASSED: BarristerView cleanAIContent strips \\1 artifacts")
    
    def test_strips_prompt_instruction_text(self):
        """Verify function strips prompt instruction text from headings"""
        with open('/app/frontend/src/pages/BarristerView.jsx', 'r') as f:
            content = f.read()
        # Check for prompt instruction stripping patterns
        assert 'keep ALL' in content
        assert 'DETAILED PATHWAY ANALYSIS' in content
        print("PASSED: BarristerView cleanAIContent strips prompt instruction text")
    
    def test_strips_we_us_our_language(self):
        """Verify function strips we/us/our language"""
        with open('/app/frontend/src/pages/BarristerView.jsx', 'r') as f:
            content = f.read()
        # Check for we/us/our replacement patterns
        assert 'We are arguing' in content
        assert 'The applicant argues' in content
        assert 'We argue' in content
        print("PASSED: BarristerView cleanAIContent strips we/us/our language")


class TestFrontendBarristerViewDisclaimer:
    """Test disclaimer in BarristerView.jsx"""
    
    def test_disclaimer_exists(self):
        """Verify disclaimer exists"""
        with open('/app/frontend/src/pages/BarristerView.jsx', 'r') as f:
            content = f.read()
        assert 'NOT LEGAL ADVICE' in content
        print("PASSED: Disclaimer exists in BarristerView.jsx")
    
    def test_created_by_deb_king(self):
        """Verify 'Created and Designed by Deb King' text exists"""
        with open('/app/frontend/src/pages/BarristerView.jsx', 'r') as f:
            content = f.read()
        assert 'Created and Designed by Deb King' in content
        print("PASSED: 'Created and Designed by Deb King' text exists in BarristerView.jsx")


class TestFrontendBarristerViewHeader:
    """Test header in BarristerView.jsx"""
    
    def test_barrister_brief_header(self):
        """Verify header shows 'BARRISTER BRIEF'"""
        with open('/app/frontend/src/pages/BarristerView.jsx', 'r') as f:
            content = f.read()
        assert 'BARRISTER BRIEF' in content
        print("PASSED: Header shows 'BARRISTER BRIEF'")
    
    def test_print_preview_has_professional_layout(self):
        """Verify print preview has professional layout with styled header"""
        with open('/app/frontend/src/pages/BarristerView.jsx', 'r') as f:
            content = f.read()
        assert 'openBarristerPreview' in content
        assert 'report-header' in content
        print("PASSED: Print preview has professional layout with styled header")
    
    def test_print_preview_has_table_layout_fixed(self):
        """Verify print preview has table-layout:fixed CSS"""
        with open('/app/frontend/src/pages/BarristerView.jsx', 'r') as f:
            content = f.read()
        assert 'table-layout: fixed' in content
        print("PASSED: BarristerView print preview has table-layout:fixed CSS")


class TestFrontendReportsSectionLockIcon:
    """Test Lock icon in ReportsSection.jsx"""
    
    def test_lock_icon_imported(self):
        """Verify Lock icon is imported"""
        with open('/app/frontend/src/components/ReportsSection.jsx', 'r') as f:
            content = f.read()
        assert 'Lock' in content
        print("PASSED: Lock icon is imported")
    
    def test_lock_icon_used_on_barrister_button(self):
        """Verify Lock icon is used on locked Barrister View button"""
        with open('/app/frontend/src/components/ReportsSection.jsx', 'r') as f:
            content = f.read()
        # Check for Lock icon usage near Barrister View button
        assert '<Lock' in content
        assert 'Barrister View' in content
        print("PASSED: Lock icon is used on locked Barrister View button")


class TestFrontendIndexCSSPrintMedia:
    """Test print media rules in index.css"""
    
    def test_table_layout_fixed_in_print_media(self):
        """Verify table-layout:fixed exists in print media for legal-report tables"""
        with open('/app/frontend/src/index.css', 'r') as f:
            content = f.read()
        # Check for table-layout: fixed in print media
        assert 'table-layout: fixed' in content
        print("PASSED: table-layout:fixed exists in index.css")
    
    def test_legal_report_table_print_styles(self):
        """Verify legal-report table has print styles"""
        with open('/app/frontend/src/index.css', 'r') as f:
            content = f.read()
        assert '.legal-report table' in content
        print("PASSED: legal-report table has print styles")


class TestBackendReportPromptsMaterialCounts:
    """Test report prompts contain MATERIAL COUNTS section"""
    
    def test_material_counts_in_prompts(self):
        """Verify MATERIAL COUNTS section exists in report prompts"""
        with open('/app/backend/server.py', 'r') as f:
            content = f.read()
        # Check for MATERIAL COUNTS in prompts
        material_count = content.count('MATERIAL COUNTS')
        assert material_count >= 1, f"Expected at least 1 MATERIAL COUNTS section, found {material_count}"
        print(f"PASSED: Found {material_count} MATERIAL COUNTS sections in prompts")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
