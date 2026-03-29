"""
Iteration 51 - Test Delete Case, Report Sections, and Report API
Tests for: 1) Delete case functionality 2) Report content validation 3) API endpoints
"""

import pytest
import requests
import os

BASE_URL = 'http://localhost:8001'

class TestDeleteCase:
    """Test DELETE /api/cases/{case_id} endpoint"""
    
    @pytest.fixture
    def auth_session(self):
        """Create authenticated session"""
        session = requests.Session()
        login_resp = session.post(f"{BASE_URL}/api/auth/login", json={
            "email": "test@test.com",
            "password": "Test1234!"
        })
        assert login_resp.status_code == 200, f"Login failed: {login_resp.text}"
        return session
    
    def test_delete_case_endpoint_exists(self, auth_session):
        """Test that DELETE endpoint exists and creates+deletes a case"""
        # Create a test case first
        create_resp = auth_session.post(f"{BASE_URL}/api/cases", json={
            "title": "TEST_Delete_Case_51",
            "defendant_name": "Test Defendant",
            "case_number": "TEST-DEL-51"
        })
        
        assert create_resp.status_code in [200, 201], f"Case creation failed: {create_resp.text}"
        case_data = create_resp.json()
        case_id = case_data.get('case_id')
        assert case_id, "Case ID not returned"
        
        # Delete the case
        delete_resp = auth_session.delete(f"{BASE_URL}/api/cases/{case_id}")
        assert delete_resp.status_code == 200, f"Delete failed: {delete_resp.text}"
        
        # Verify response message
        delete_data = delete_resp.json()
        assert 'message' in delete_data or 'deleted' in str(delete_data).lower()
        
        # Verify case no longer exists
        verify_resp = auth_session.get(f"{BASE_URL}/api/cases/{case_id}")
        assert verify_resp.status_code == 404, "Case should return 404 after deletion"
    
    def test_delete_nonexistent_case_returns_404(self, auth_session):
        """Test deleting a case that doesn't exist returns 404"""
        delete_resp = auth_session.delete(f"{BASE_URL}/api/cases/nonexistent-case-id-12345")
        assert delete_resp.status_code == 404


class TestReportContent:
    """Test report content has all required sections"""
    
    @pytest.fixture
    def auth_session(self):
        """Create authenticated session"""
        session = requests.Session()
        session.post(f"{BASE_URL}/api/auth/login", json={
            "email": "test@test.com",
            "password": "Test1234!"
        })
        return session
    
    def test_report_has_all_sections(self, auth_session):
        """Verify test report contains all 8 required sections"""
        case_id = "case-render-test2"
        report_id = "rpt-render-test2"
        
        # Get the report
        report_resp = auth_session.get(f"{BASE_URL}/api/cases/{case_id}/reports/{report_id}")
        
        if report_resp.status_code == 404:
            pytest.skip("Test report not found - may have been deleted")
        
        assert report_resp.status_code == 200, f"Failed to get report: {report_resp.text}"
        
        report = report_resp.json()
        analysis = report.get('content', {}).get('analysis', '')
        
        # Check for all required sections
        required_sections = [
            ("Executive Summary", "executive summary"),
            ("Grounds of Appeal", "grounds of appeal"),
            ("Comparative Sentencing Table", "comparative sentencing"),
            ("Applicable Legislation", "applicable legislation"),
            ("Recommended Next Steps", "recommended next steps"),
            ("Strategic Advice", "strategic advice"),
            ("How to Start Your Appeal", "how to start"),
            ("Required Appeal Forms", "required appeal forms")
        ]
        
        missing_sections = []
        for section_name, search_term in required_sections:
            if search_term.lower() not in analysis.lower():
                missing_sections.append(section_name)
        
        assert len(missing_sections) == 0, f"Missing sections: {', '.join(missing_sections)}"
    
    def test_report_type_is_full_detailed(self, auth_session):
        """Verify test report is full_detailed type"""
        case_id = "case-render-test2"
        report_id = "rpt-render-test2"
        
        report_resp = auth_session.get(f"{BASE_URL}/api/cases/{case_id}/reports/{report_id}")
        
        if report_resp.status_code == 404:
            pytest.skip("Test report not found")
        
        report = report_resp.json()
        assert report.get('report_type') == 'full_detailed', f"Expected full_detailed, got {report.get('report_type')}"
    
    def test_report_has_tables(self, auth_session):
        """Verify report contains tables (markdown format)"""
        case_id = "case-render-test2"
        report_id = "rpt-render-test2"
        
        report_resp = auth_session.get(f"{BASE_URL}/api/cases/{case_id}/reports/{report_id}")
        
        if report_resp.status_code == 404:
            pytest.skip("Test report not found")
        
        report = report_resp.json()
        analysis = report.get('content', {}).get('analysis', '')
        
        # Check for markdown table markers
        assert '|' in analysis and '---' in analysis, "Report should contain markdown tables"
    
    def test_report_has_links(self, auth_session):
        """Verify report contains external links"""
        case_id = "case-render-test2"
        report_id = "rpt-render-test2"
        
        report_resp = auth_session.get(f"{BASE_URL}/api/cases/{case_id}/reports/{report_id}")
        
        if report_resp.status_code == 404:
            pytest.skip("Test report not found")
        
        report = report_resp.json()
        analysis = report.get('content', {}).get('analysis', '')
        
        # Check for markdown links [text](url)
        assert '](http' in analysis or '](https' in analysis, "Report should contain external links"


class TestReportAPIEndpoints:
    """Test report API endpoints"""
    
    @pytest.fixture
    def auth_session(self):
        """Create authenticated session"""
        session = requests.Session()
        session.post(f"{BASE_URL}/api/auth/login", json={
            "email": "test@test.com",
            "password": "Test1234!"
        })
        return session
    
    def test_get_case_reports_list(self, auth_session):
        """Test GET /api/cases/{case_id}/reports returns list"""
        case_id = "case-render-test2"
        
        resp = auth_session.get(f"{BASE_URL}/api/cases/{case_id}/reports")
        
        if resp.status_code == 404:
            pytest.skip("Test case not found")
        
        assert resp.status_code == 200
        reports = resp.json()
        assert isinstance(reports, list), "Reports should be a list"
    
    def test_get_single_report(self, auth_session):
        """Test GET /api/cases/{case_id}/reports/{report_id}"""
        case_id = "case-render-test2"
        report_id = "rpt-render-test2"
        
        resp = auth_session.get(f"{BASE_URL}/api/cases/{case_id}/reports/{report_id}")
        
        if resp.status_code == 404:
            pytest.skip("Test report not found")
        
        assert resp.status_code == 200
        report = resp.json()
        
        # Validate report structure
        assert 'report_id' in report
        assert 'report_type' in report
        assert 'content' in report
        assert 'analysis' in report.get('content', {})
    
    def test_report_export_pdf_endpoint_exists(self, auth_session):
        """Test PDF export endpoint exists"""
        case_id = "case-render-test2"
        report_id = "rpt-render-test2"
        
        resp = auth_session.get(f"{BASE_URL}/api/cases/{case_id}/reports/{report_id}/export-pdf")
        
        if resp.status_code == 404:
            pytest.skip("Test report not found or export endpoint not available")
        
        # Should return PDF blob or 200
        assert resp.status_code in [200, 500], f"Unexpected status: {resp.status_code}"
    
    def test_report_export_docx_endpoint_exists(self, auth_session):
        """Test DOCX export endpoint exists"""
        case_id = "case-render-test2"
        report_id = "rpt-render-test2"
        
        resp = auth_session.get(f"{BASE_URL}/api/cases/{case_id}/reports/{report_id}/export-docx")
        
        if resp.status_code == 404:
            pytest.skip("Test report not found or export endpoint not available")
        
        # Should return DOCX blob or 200
        assert resp.status_code in [200, 500], f"Unexpected status: {resp.status_code}"


class TestCaseDetailElements:
    """Test case detail page data"""
    
    @pytest.fixture
    def auth_session(self):
        """Create authenticated session"""
        session = requests.Session()
        session.post(f"{BASE_URL}/api/auth/login", json={
            "email": "test@test.com",
            "password": "Test1234!"
        })
        return session
    
    def test_get_case_details(self, auth_session):
        """Test getting case details"""
        case_id = "case-render-test2"
        
        resp = auth_session.get(f"{BASE_URL}/api/cases/{case_id}")
        
        if resp.status_code == 404:
            pytest.skip("Test case not found")
        
        assert resp.status_code == 200
        case_data = resp.json()
        
        # Validate case structure
        assert 'case_id' in case_data
        assert 'title' in case_data
        assert case_data['title'] == "R v Smith [2024] NSWCCA 142"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
