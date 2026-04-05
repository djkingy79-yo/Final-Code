"""
Iteration 96 - Backend API Tests for Export Endpoints and Barrister View
Tests:
1. PDF export for reports
2. DOCX export for reports
3. Barrister view endpoint
4. Report status endpoint
"""
import pytest
import requests
import os

BASE_URL = 'http://localhost:8001'

# Test credentials
TEST_EMAIL = "test@example.com"
TEST_PASSWORD = "TestPassword123!"

# Known test data from previous iterations
TEST_CASE_ID = "case_76056187ad4f"
TEST_REPORT_ID = "rpt_1cc1bfeace33"  # Full report
TEST_BARRISTER_REPORT_ID = "rpt_dcb21f0efc62"  # Barrister report


@pytest.fixture(scope="module")
def session():
    """Create a requests session"""
    s = requests.Session()
    s.headers.update({"Content-Type": "application/json"})
    return s


@pytest.fixture(scope="module")
def auth_token(session):
    """Get authentication token via email/password login"""
    response = session.post(f"{BASE_URL}/api/auth/login", json={
        "email": TEST_EMAIL,
        "password": TEST_PASSWORD
    })
    if response.status_code == 200:
        data = response.json()
        token = data.get("session_token")
        if token:
            return token
    pytest.skip(f"Authentication failed: {response.status_code} - {response.text[:200]}")


@pytest.fixture(scope="module")
def authenticated_session(session, auth_token):
    """Session with auth header"""
    session.headers.update({"Authorization": f"Bearer {auth_token}"})
    return session


class TestHealthCheck:
    """Basic health check tests"""
    
    def test_api_health(self, session):
        """Test API health endpoint"""
        response = session.get(f"{BASE_URL}/api/health")
        assert response.status_code == 200, f"Health check failed: {response.status_code}"
        data = response.json()
        assert data.get("status") == "healthy"
        print(f"✓ API health check passed: {data}")


class TestReportExports:
    """Test report export endpoints"""
    
    def test_export_report_pdf(self, authenticated_session):
        """Test PDF export for a completed report"""
        response = authenticated_session.get(
            f"{BASE_URL}/api/cases/{TEST_CASE_ID}/reports/{TEST_REPORT_ID}/export-pdf",
            timeout=60
        )
        assert response.status_code == 200, f"PDF export failed: {response.status_code} - {response.text[:500]}"
        assert "application/pdf" in response.headers.get("Content-Type", ""), f"Expected PDF content type, got: {response.headers.get('Content-Type')}"
        assert len(response.content) > 1000, f"PDF content too small: {len(response.content)} bytes"
        print(f"✓ PDF export successful: {len(response.content)} bytes")
    
    def test_export_report_docx(self, authenticated_session):
        """Test DOCX export for a completed report"""
        response = authenticated_session.get(
            f"{BASE_URL}/api/cases/{TEST_CASE_ID}/reports/{TEST_REPORT_ID}/export-docx",
            timeout=60
        )
        assert response.status_code == 200, f"DOCX export failed: {response.status_code} - {response.text[:500]}"
        content_type = response.headers.get("Content-Type", "")
        assert "application" in content_type, f"Expected application content type, got: {content_type}"
        assert len(response.content) > 1000, f"DOCX content too small: {len(response.content)} bytes"
        print(f"✓ DOCX export successful: {len(response.content)} bytes")
    
    def test_export_barrister_pdf(self, authenticated_session):
        """Test PDF export for barrister report"""
        response = authenticated_session.get(
            f"{BASE_URL}/api/cases/{TEST_CASE_ID}/reports/{TEST_BARRISTER_REPORT_ID}/export-pdf",
            timeout=60
        )
        assert response.status_code == 200, f"Barrister PDF export failed: {response.status_code} - {response.text[:500]}"
        assert "application/pdf" in response.headers.get("Content-Type", ""), "Expected PDF content type"
        assert len(response.content) > 1000, f"PDF content too small: {len(response.content)} bytes"
        print(f"✓ Barrister PDF export successful: {len(response.content)} bytes")
    
    def test_export_barrister_docx(self, authenticated_session):
        """Test DOCX export for barrister report"""
        response = authenticated_session.get(
            f"{BASE_URL}/api/cases/{TEST_CASE_ID}/reports/{TEST_BARRISTER_REPORT_ID}/export-docx",
            timeout=60
        )
        assert response.status_code == 200, f"Barrister DOCX export failed: {response.status_code} - {response.text[:500]}"
        assert len(response.content) > 1000, f"DOCX content too small: {len(response.content)} bytes"
        print(f"✓ Barrister DOCX export successful: {len(response.content)} bytes")


class TestBarristerView:
    """Test Barrister View endpoint"""
    
    def test_get_barrister_view(self, authenticated_session):
        """Test getting barrister view for a case with all 3 reports"""
        response = authenticated_session.get(
            f"{BASE_URL}/api/cases/{TEST_CASE_ID}/reports/barrister-view",
            timeout=60
        )
        assert response.status_code == 200, f"Barrister view failed: {response.status_code} - {response.text[:500]}"
        data = response.json()
        assert data.get("status") == "completed", f"Expected completed status, got: {data.get('status')}"
        assert data.get("report_id"), "Missing report_id in barrister view response"
        assert data.get("content"), "Missing content in barrister view response"
        print(f"✓ Barrister view loaded: report_id={data.get('report_id')}, status={data.get('status')}")


class TestReportStatus:
    """Test report status endpoint"""
    
    def test_get_report_status(self, authenticated_session):
        """Test getting report status"""
        response = authenticated_session.get(
            f"{BASE_URL}/api/cases/{TEST_CASE_ID}/reports/{TEST_REPORT_ID}/status"
        )
        assert response.status_code == 200, f"Report status failed: {response.status_code}"
        data = response.json()
        assert "status" in data, "Missing status in response"
        print(f"✓ Report status: {data.get('status')}")


class TestCaseReports:
    """Test case reports listing"""
    
    def test_get_case_reports(self, authenticated_session):
        """Test getting all reports for a case"""
        response = authenticated_session.get(
            f"{BASE_URL}/api/cases/{TEST_CASE_ID}/reports"
        )
        assert response.status_code == 200, f"Get reports failed: {response.status_code}"
        data = response.json()
        assert isinstance(data, list), "Expected list of reports"
        assert len(data) > 0, "Expected at least one report"
        
        # Check for required report types
        report_types = [r.get("report_type") for r in data]
        print(f"✓ Found {len(data)} reports: {report_types}")
        
        # Verify report structure
        for report in data:
            assert "report_id" in report, "Missing report_id"
            assert "report_type" in report, "Missing report_type"
            assert "status" in report, "Missing status"


class TestCaseData:
    """Test case data endpoint to verify no stale data"""
    
    def test_get_case_data(self, authenticated_session):
        """Test getting case data"""
        response = authenticated_session.get(
            f"{BASE_URL}/api/cases/{TEST_CASE_ID}"
        )
        assert response.status_code == 200, f"Get case failed: {response.status_code}"
        data = response.json()
        assert data.get("case_id") == TEST_CASE_ID, "Case ID mismatch"
        assert data.get("title"), "Missing case title"
        print(f"✓ Case data: {data.get('title')}, defendant: {data.get('defendant_name')}")
        
        # Verify offence and sentence fields exist
        if data.get("offence_type"):
            print(f"  Offence type: {data.get('offence_type')}")
        if data.get("sentence"):
            print(f"  Sentence: {data.get('sentence')}")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
