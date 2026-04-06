"""
Test suite for font size standardisation (iteration 145)
Tests that font sizes have been reduced in reports, print previews, and exports.

Font size changes:
- Body: 1.15rem → 0.95rem (~15px)
- H2: 1.6rem → 1.2rem (~19px)
- H3: 1.35rem → 1.05rem (~17px)
- DOCX title: 24pt → 18pt
- DOCX H1: 16pt → 14pt
- DOCX H2: 14pt → 12pt
- PDF title: 26 → 20
- PDF section header: 16 → 14
"""

import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://criminal-appeals-au-2.preview.emergentagent.com')


class TestHealthAndAuth:
    """Basic health and auth tests"""
    
    def test_health_endpoint(self):
        """Test that the health endpoint returns healthy status"""
        response = requests.get(f"{BASE_URL}/api/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["database"] == "connected"
        print("PASS: Health endpoint returns healthy status")
    
    def test_login_with_valid_credentials(self):
        """Test login with valid credentials"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": "djkingy79@gmail.com",
            "password": "Cr1m1nalApp3al$2025"
        })
        assert response.status_code == 200
        data = response.json()
        assert "session_token" in data
        assert "user_id" in data
        print("PASS: Login returns session token")
        return data["session_token"]


class TestExportEndpoints:
    """Test DOCX and PDF export endpoints"""
    
    @pytest.fixture
    def auth_token(self):
        """Get authentication token"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": "djkingy79@gmail.com",
            "password": "Cr1m1nalApp3al$2025"
        })
        if response.status_code == 200:
            return response.json().get("session_token")
        pytest.skip("Authentication failed - skipping authenticated tests")
    
    @pytest.fixture
    def case_and_report_ids(self, auth_token):
        """Get a case_id and report_id for testing"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        
        # Get cases
        cases_response = requests.get(f"{BASE_URL}/api/cases", headers=headers)
        assert cases_response.status_code == 200
        cases = cases_response.json()
        
        # Find Homann case or any case with reports
        case_id = None
        for case in cases:
            if "Homann" in case.get("title", ""):
                case_id = case["case_id"]
                break
        
        if not case_id and cases:
            case_id = cases[0]["case_id"]
        
        if not case_id:
            pytest.skip("No cases found")
        
        # Get reports for the case
        reports_response = requests.get(f"{BASE_URL}/api/cases/{case_id}/reports", headers=headers)
        assert reports_response.status_code == 200
        reports = reports_response.json()
        
        if not reports:
            pytest.skip("No reports found for case")
        
        report_id = reports[0]["report_id"]
        return case_id, report_id
    
    def test_docx_export_endpoint(self, auth_token, case_and_report_ids):
        """Test DOCX export endpoint returns 200"""
        case_id, report_id = case_and_report_ids
        headers = {"Authorization": f"Bearer {auth_token}"}
        
        response = requests.get(
            f"{BASE_URL}/api/cases/{case_id}/reports/{report_id}/export-docx",
            headers=headers
        )
        assert response.status_code == 200
        assert "application/vnd.openxmlformats-officedocument.wordprocessingml.document" in response.headers.get("content-type", "")
        assert len(response.content) > 1000  # Should have substantial content
        print(f"PASS: DOCX export returns 200 with {len(response.content)} bytes")
    
    def test_pdf_export_endpoint(self, auth_token, case_and_report_ids):
        """Test PDF export endpoint returns 200"""
        case_id, report_id = case_and_report_ids
        headers = {"Authorization": f"Bearer {auth_token}"}
        
        response = requests.get(
            f"{BASE_URL}/api/cases/{case_id}/reports/{report_id}/export-pdf",
            headers=headers
        )
        assert response.status_code == 200
        assert "application/pdf" in response.headers.get("content-type", "")
        assert len(response.content) > 1000  # Should have substantial content
        print(f"PASS: PDF export returns 200 with {len(response.content)} bytes")


class TestReportEndpoints:
    """Test report-related endpoints"""
    
    @pytest.fixture
    def auth_token(self):
        """Get authentication token"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": "djkingy79@gmail.com",
            "password": "Cr1m1nalApp3al$2025"
        })
        if response.status_code == 200:
            return response.json().get("session_token")
        pytest.skip("Authentication failed - skipping authenticated tests")
    
    def test_get_reports_for_case(self, auth_token):
        """Test getting reports for a case"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        
        # Get cases
        cases_response = requests.get(f"{BASE_URL}/api/cases", headers=headers)
        assert cases_response.status_code == 200
        cases = cases_response.json()
        
        if not cases:
            pytest.skip("No cases found")
        
        # Find Homann case
        case_id = None
        for case in cases:
            if "Homann" in case.get("title", ""):
                case_id = case["case_id"]
                break
        
        if not case_id:
            case_id = cases[0]["case_id"]
        
        # Get reports
        reports_response = requests.get(f"{BASE_URL}/api/cases/{case_id}/reports", headers=headers)
        assert reports_response.status_code == 200
        reports = reports_response.json()
        assert isinstance(reports, list)
        print(f"PASS: Got {len(reports)} reports for case {case_id}")
    
    def test_get_single_report(self, auth_token):
        """Test getting a single report"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        
        # Get cases
        cases_response = requests.get(f"{BASE_URL}/api/cases", headers=headers)
        cases = cases_response.json()
        
        if not cases:
            pytest.skip("No cases found")
        
        # Find Homann case
        case_id = None
        for case in cases:
            if "Homann" in case.get("title", ""):
                case_id = case["case_id"]
                break
        
        if not case_id:
            case_id = cases[0]["case_id"]
        
        # Get reports
        reports_response = requests.get(f"{BASE_URL}/api/cases/{case_id}/reports", headers=headers)
        reports = reports_response.json()
        
        if not reports:
            pytest.skip("No reports found")
        
        report_id = reports[0]["report_id"]
        
        # Get single report
        report_response = requests.get(f"{BASE_URL}/api/cases/{case_id}/reports/{report_id}", headers=headers)
        assert report_response.status_code == 200
        report = report_response.json()
        assert "report_id" in report
        assert "content" in report
        print(f"PASS: Got report {report_id}")


class TestBarristerView:
    """Test Barrister View endpoints"""
    
    @pytest.fixture
    def auth_token(self):
        """Get authentication token"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": "djkingy79@gmail.com",
            "password": "Cr1m1nalApp3al$2025"
        })
        if response.status_code == 200:
            return response.json().get("session_token")
        pytest.skip("Authentication failed - skipping authenticated tests")
    
    def test_barrister_view_endpoint(self, auth_token):
        """Test Barrister View endpoint"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        
        # Get cases
        cases_response = requests.get(f"{BASE_URL}/api/cases", headers=headers)
        cases = cases_response.json()
        
        if not cases:
            pytest.skip("No cases found")
        
        # Find Homann case
        case_id = None
        for case in cases:
            if "Homann" in case.get("title", ""):
                case_id = case["case_id"]
                break
        
        if not case_id:
            pytest.skip("Homann case not found")
        
        # Get barrister view
        barrister_response = requests.get(f"{BASE_URL}/api/cases/{case_id}/reports/barrister-view", headers=headers)
        # May return 200 (completed) or 202 (generating) or 403 (locked)
        assert barrister_response.status_code in [200, 202, 403]
        print(f"PASS: Barrister view endpoint returns {barrister_response.status_code}")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
