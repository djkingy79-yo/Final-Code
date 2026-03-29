"""
Iteration 34 Backend Tests - Report Prompt Verification
Tests:
- Backend prompt upgrade verification for full_detailed and extensive_log
- Mandatory markdown tables (comparative sentencing, common grounds, options matrix)
- Sentence reduction format instructions
- Guardrails enforcement (no cost discussion, no witness sections)
- Frontend ReportView dependencies (react-markdown, remark-gfm)
"""

import pytest
import requests
import os

BASE_URL = 'http://localhost:8001'

class TestHealthAndPublicEndpoints:
    """Basic health and public endpoint tests"""
    
    def test_health_endpoint(self):
        """Test health check is accessible"""
        response = requests.get(f"{BASE_URL}/api/health", timeout=10)
        assert response.status_code == 200
        data = response.json()
        assert data.get("status") == "healthy"
        print("PASS: Health endpoint returns healthy status")
    
    def test_offence_categories(self):
        """Test offence categories endpoint"""
        response = requests.get(f"{BASE_URL}/api/offence-categories", timeout=10)
        assert response.status_code == 200
        data = response.json()
        assert "categories" in data
        print(f"PASS: Offence categories returns {len(data.get('categories', {}))} categories")
    
    def test_states_endpoint(self):
        """Test states endpoint"""
        response = requests.get(f"{BASE_URL}/api/states", timeout=10)
        assert response.status_code == 200
        data = response.json()
        assert "states" in data
        print(f"PASS: States endpoint returns {len(data.get('states', {}))} states")
    
    def test_payment_prices(self):
        """Test payment prices endpoint"""
        response = requests.get(f"{BASE_URL}/api/payments/prices", timeout=10)
        assert response.status_code == 200
        data = response.json()
        assert "prices" in data
        prices = data["prices"]
        # Verify report prices exist
        assert "full_report" in prices
        assert "extensive_report" in prices
        assert prices["full_report"]["price"] == 29.00
        assert prices["extensive_report"]["price"] == 39.00
        print("PASS: Payment prices endpoint returns correct report prices")


class TestAuthenticationProtection:
    """Test that protected routes require authentication"""
    
    def test_cases_requires_auth(self):
        """Test cases endpoint requires authentication"""
        response = requests.get(f"{BASE_URL}/api/cases", timeout=10)
        assert response.status_code == 401
        print("PASS: Cases endpoint correctly requires authentication (401)")
    
    def test_auth_me_requires_auth(self):
        """Test auth/me endpoint requires authentication"""
        response = requests.get(f"{BASE_URL}/api/auth/me", timeout=10)
        assert response.status_code == 401
        print("PASS: Auth/me endpoint correctly requires authentication (401)")


class TestReportEndpointsExist:
    """Test that report-related endpoints exist"""
    
    def test_report_generate_requires_auth(self):
        """Test report generation endpoint exists but requires auth"""
        # Try to generate a report without auth - should return 401
        response = requests.post(
            f"{BASE_URL}/api/cases/test_case/reports/generate",
            json={"report_type": "quick_summary"},
            timeout=10
        )
        assert response.status_code == 401
        print("PASS: Report generate endpoint exists and requires auth (401)")
    
    def test_pdf_export_endpoint_exists(self):
        """Test PDF export endpoint structure exists"""
        response = requests.get(
            f"{BASE_URL}/api/cases/test_case/reports/test_report/export-pdf",
            timeout=10
        )
        # Should return 401 (auth required) not 404 (endpoint not found)
        assert response.status_code == 401
        print("PASS: PDF export endpoint exists (requires auth)")
    
    def test_docx_export_endpoint_exists(self):
        """Test DOCX export endpoint structure exists"""
        response = requests.get(
            f"{BASE_URL}/api/cases/test_case/reports/test_report/export-docx",
            timeout=10
        )
        # Should return 401 (auth required) not 404 (endpoint not found)
        assert response.status_code == 401
        print("PASS: DOCX export endpoint exists (requires auth)")


class TestStaticPages:
    """Test static/landing pages"""
    
    def test_landing_page(self):
        """Test landing page loads"""
        response = requests.get(f"{BASE_URL}/", timeout=10)
        assert response.status_code == 200
        assert "appeal" in response.text.lower() or "criminal" in response.text.lower()
        print("PASS: Landing page loads successfully")
    
    def test_legal_resources_page(self):
        """Test legal resources page"""
        response = requests.get(f"{BASE_URL}/legal-resources", timeout=10)
        assert response.status_code == 200
        print("PASS: Legal resources page accessible")
    
    def test_terms_page(self):
        """Test terms page"""
        response = requests.get(f"{BASE_URL}/terms", timeout=10)
        assert response.status_code == 200
        print("PASS: Terms page accessible")
    
    def test_about_page(self):
        """Test about page"""
        response = requests.get(f"{BASE_URL}/about", timeout=10)
        assert response.status_code == 200
        print("PASS: About page accessible")


class TestPromptContentVerification:
    """
    These tests verify the backend prompts contain required elements.
    Since we can't call the AI without auth, we verify through code analysis.
    """
    
    def test_verify_backend_prompts_via_code_inspection(self):
        """Verify prompt content requirements are met in server.py"""
        server_path = "/app/backend/server.py"
        
        with open(server_path, 'r') as f:
            content = f.read()
        
        # Test 1: full_detailed prompt has extensive-level depth
        assert "FULL DETAILED LEGAL ANALYSIS REPORT" in content, "Missing full_detailed title"
        assert "6200 words" in content, "full_detailed should have 6200+ word minimum"
        print("PASS: full_detailed prompt has extensive-level depth (6200+ words)")
        
        # Test 2: extensive_log has expanded requirements
        assert "EXTENSIVE LOG REPORT" in content, "Missing extensive_log title"
        assert "7800 words" in content, "extensive_log should have 7800+ word minimum"
        print("PASS: extensive_log prompt has expanded requirements (7800+ words)")
        
        # Test 3: Comparative Sentencing Table mandatory in both paid reports
        assert "COMPARATIVE SENTENCING TABLE (MANDATORY)" in content
        assert "COMPARATIVE SENTENCING TABLE (MANDATORY, EXPANDED)" in content
        print("PASS: Comparative Sentencing Table is mandatory in both paid reports")
        
        # Test 4: Common Grounds Table mandatory in both paid reports
        assert "COMMON APPEAL GROUNDS FOR THIS OFFENCE TYPE (MANDATORY)" in content
        assert "COMMON GROUNDS BENCHMARK TABLE FOR THIS OFFENCE (MANDATORY)" in content
        print("PASS: Common Grounds Table is mandatory in both paid reports")
        
        # Test 5: Full Options Matrix mandatory in both paid reports
        assert "OUTCOME OPTIONS AVAILABLE (MANDATORY)" in content
        assert "FULL OPTIONS AVAILABLE REPORT (MANDATORY)" in content
        print("PASS: Full Options Matrix is mandatory in both paid reports")
        
        # Test 6: Sentence reduction format instructions
        assert "30/22.5 -> 18/11" in content, "Missing explicit sentence reduction format"
        print("PASS: Sentence reduction format (30/22.5 -> 18/11) is specified")
        
        # Test 7: Options include all required pathways
        pathways = ["quashed", "Retrial ordered", "downgraded", "substituted", "reduced", "dismissed"]
        for pathway in pathways:
            assert pathway.lower() in content.lower(), f"Missing pathway: {pathway}"
        print("PASS: All required outcome pathways are specified")
    
    def test_verify_guardrails_in_prompts(self):
        """Verify guardrails are enforced in all report types"""
        server_path = "/app/backend/server.py"
        
        with open(server_path, 'r') as f:
            content = f.read()
        
        # Test 1: No cost discussion guardrail
        assert "DO NOT include cost estimates" in content or "No cost discussion" in content
        print("PASS: Cost discussion guardrail is present")
        
        # Test 2: No witness contradiction/credibility sections
        assert "DO NOT include witness contradiction" in content or "No witness contradiction" in content
        print("PASS: Witness contradiction guardrail is present")
        
        # Test 3: Guardrails appear in MANDATORY GUARDRAILS block
        assert "MANDATORY GUARDRAILS" in content
        print("PASS: MANDATORY GUARDRAILS block is present")
        
        # Test 4: Guardrails instructions appear in all report type prompts
        # Check that the IMPORTANT section with guardrails appears multiple times
        important_sections = content.count("No cost discussion")
        assert important_sections >= 3, f"Expected 3+ cost guardrail mentions, found {important_sections}"
        print(f"PASS: Cost guardrail mentioned {important_sections} times (for each report type)")
    
    def test_verify_table_column_specifications(self):
        """Verify required markdown table column specifications"""
        server_path = "/app/backend/server.py"
        
        with open(server_path, 'r') as f:
            content = f.read()
        
        # Test comparative sentencing table columns
        assert "Original Sentence / NPP" in content
        assert "Appeal Outcome" in content
        assert "Revised Sentence / NPP" in content
        assert "Reduction (Years + %)" in content
        print("PASS: Comparative sentencing table has all required columns")
        
        # Test common grounds table columns
        assert "Common Ground" in content
        assert "Frequency" in content or "Prevalence" in content
        assert "Success" in content
        print("PASS: Common grounds table has required columns")
        
        # Test options matrix columns
        assert "Legal Threshold" in content
        assert "Likelihood" in content
        assert "Practical Result" in content or "Typical Remedy" in content
        print("PASS: Options matrix table has required columns")


class TestFrontendDependencies:
    """Verify frontend has required dependencies"""
    
    def test_verify_react_markdown_dependency(self):
        """Verify react-markdown is in package.json"""
        package_path = "/app/frontend/package.json"
        
        with open(package_path, 'r') as f:
            content = f.read()
        
        assert '"react-markdown"' in content, "Missing react-markdown dependency"
        print("PASS: react-markdown dependency is present in package.json")
    
    def test_verify_remark_gfm_dependency(self):
        """Verify remark-gfm is in package.json"""
        package_path = "/app/frontend/package.json"
        
        with open(package_path, 'r') as f:
            content = f.read()
        
        assert '"remark-gfm"' in content, "Missing remark-gfm dependency"
        print("PASS: remark-gfm dependency is present in package.json")


class TestReportViewComponent:
    """Verify ReportView component has required features"""
    
    def test_verify_reportview_has_required_elements(self):
        """Verify ReportView has summary box, TOC, markdown rendering"""
        report_view_path = "/app/frontend/src/pages/ReportView.jsx"
        
        with open(report_view_path, 'r') as f:
            content = f.read()
        
        # Test 1: ReactMarkdown import
        assert "import ReactMarkdown" in content or "from 'react-markdown'" in content
        print("PASS: ReportView imports ReactMarkdown")
        
        # Test 2: remarkGfm import
        assert "remarkGfm" in content
        print("PASS: ReportView imports remarkGfm")
        
        # Test 3: Top summary box exists
        assert "report-top-summary-box" in content
        print("PASS: ReportView has top summary box (data-testid='report-top-summary-box')")
        
        # Test 4: Table of contents exists
        assert "report-table-of-contents" in content
        print("PASS: ReportView has table of contents (data-testid='report-table-of-contents')")
        
        # Test 5: Appeal readiness gauge
        assert "appeal-readiness-gauge" in content
        print("PASS: ReportView has appeal readiness gauge")
        
        # Test 6: Markdown table rendering
        assert "table" in content.lower() and "thead" in content.lower()
        print("PASS: ReportView has markdown table rendering components")
        
        # Test 7: MarkdownBlock component for rendering
        assert "MarkdownBlock" in content
        print("PASS: ReportView has MarkdownBlock component for markdown rendering")


class TestReportsSectionComponent:
    """Verify ReportsSection component functionality"""
    
    def test_verify_reports_section_features(self):
        """Verify ReportsSection allows expanding and navigation"""
        reports_section_path = "/app/frontend/src/components/ReportsSection.jsx"
        
        with open(reports_section_path, 'r') as f:
            content = f.read()
        
        # Test 1: Collapsible for expanding reports
        assert "Collapsible" in content
        print("PASS: ReportsSection uses Collapsible for expanding reports")
        
        # Test 2: Full Report Page button
        assert "Full Report Page" in content
        print("PASS: ReportsSection has 'Full Report Page' button")
        
        # Test 3: Barrister View button
        assert "Barrister View" in content
        print("PASS: ReportsSection has 'Barrister View' button")
        
        # Test 4: Inline content display
        assert "report-inline-content" in content or "reportText" in content.lower()
        print("PASS: ReportsSection displays inline report content")
        
        # Test 5: Navigation to report page
        assert "navigate(`/cases/${caseId}/reports/${report.report_id}`)" in content
        print("PASS: ReportsSection navigates to full report page")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
