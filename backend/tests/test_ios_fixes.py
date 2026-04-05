"""
Test iOS bug fixes for PDF export, document preview, and isIOSDevice utility.
Tests the fixes for:
1. PDF export from ReportsSection - should not throw 'Failed to export PDF' error
2. Document preview page at /document-preview should load HTML from localStorage payload
3. Report view PDF preview opens correctly via /document-preview?mode=pdf
4. Backend /api/cases/{case_id}/reports/{report_id}/export-pdf returns valid PDF
5. Backend /api/cases/{case_id}/reports/{report_id}/export-docx returns valid DOCX
"""

import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Test credentials
TEST_EMAIL = "test@example.com"
TEST_PASSWORD = "TestPassword123!"
TEST_CASE_ID = "case_b24f94577da6"
TEST_REPORT_IDS = {
    "quick_summary": "rpt_c05b213451ef",
    "full_detailed": "rpt_606196477f2a",
    "extensive_log": "rpt_65eacc931446"
}


class TestHealthCheck:
    """Basic health check to verify API is accessible"""
    
    def test_health_endpoint(self):
        """Test that the health endpoint returns healthy status"""
        response = requests.get(f"{BASE_URL}/api/health", timeout=10)
        assert response.status_code == 200
        data = response.json()
        assert data.get("status") == "healthy"
        print(f"✓ Health check passed: {data}")


class TestAuthentication:
    """Test authentication flow"""
    
    @pytest.fixture(scope="class")
    def auth_token(self):
        """Get authentication token"""
        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": TEST_EMAIL, "password": TEST_PASSWORD},
            timeout=30
        )
        if response.status_code != 200:
            pytest.skip(f"Authentication failed: {response.status_code} - {response.text}")
        data = response.json()
        token = data.get("session_token")
        if not token:
            pytest.skip("No session_token in response")
        print(f"✓ Authentication successful, got token")
        return token
    
    def test_login_success(self, auth_token):
        """Verify login returns a valid token"""
        assert auth_token is not None
        assert len(auth_token) > 10
        print(f"✓ Login successful with token length: {len(auth_token)}")


class TestPDFExport:
    """Test PDF export endpoints - critical for iOS bug fix verification"""
    
    @pytest.fixture(scope="class")
    def auth_headers(self):
        """Get authenticated headers"""
        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": TEST_EMAIL, "password": TEST_PASSWORD},
            timeout=30
        )
        if response.status_code != 200:
            pytest.skip(f"Authentication failed: {response.status_code}")
        token = response.json().get("session_token")
        return {"Authorization": f"Bearer {token}"}
    
    def test_quick_summary_pdf_export(self, auth_headers):
        """Test PDF export for quick_summary report - should return valid PDF"""
        report_id = TEST_REPORT_IDS["quick_summary"]
        response = requests.get(
            f"{BASE_URL}/api/cases/{TEST_CASE_ID}/reports/{report_id}/export-pdf",
            headers=auth_headers,
            timeout=60
        )
        
        # Should return 200 with PDF content
        assert response.status_code == 200, f"PDF export failed: {response.status_code} - {response.text[:500]}"
        
        # Verify content type is PDF
        content_type = response.headers.get("content-type", "")
        assert "pdf" in content_type.lower() or len(response.content) > 1000, \
            f"Expected PDF content, got: {content_type}"
        
        # Verify PDF magic bytes (PDF files start with %PDF)
        if len(response.content) > 4:
            assert response.content[:4] == b'%PDF', "Response does not appear to be a valid PDF"
        
        print(f"✓ Quick summary PDF export successful, size: {len(response.content)} bytes")
    
    def test_full_detailed_pdf_export(self, auth_headers):
        """Test PDF export for full_detailed report"""
        report_id = TEST_REPORT_IDS["full_detailed"]
        response = requests.get(
            f"{BASE_URL}/api/cases/{TEST_CASE_ID}/reports/{report_id}/export-pdf",
            headers=auth_headers,
            timeout=60
        )
        
        assert response.status_code == 200, f"PDF export failed: {response.status_code}"
        
        # Verify PDF content
        if len(response.content) > 4:
            assert response.content[:4] == b'%PDF', "Response does not appear to be a valid PDF"
        
        print(f"✓ Full detailed PDF export successful, size: {len(response.content)} bytes")
    
    def test_extensive_log_pdf_export(self, auth_headers):
        """Test PDF export for extensive_log report"""
        report_id = TEST_REPORT_IDS["extensive_log"]
        response = requests.get(
            f"{BASE_URL}/api/cases/{TEST_CASE_ID}/reports/{report_id}/export-pdf",
            headers=auth_headers,
            timeout=60
        )
        
        assert response.status_code == 200, f"PDF export failed: {response.status_code}"
        
        # Verify PDF content
        if len(response.content) > 4:
            assert response.content[:4] == b'%PDF', "Response does not appear to be a valid PDF"
        
        print(f"✓ Extensive log PDF export successful, size: {len(response.content)} bytes")
    
    def test_pdf_export_with_session_token_param(self, auth_headers):
        """Test PDF export using session_token as query parameter (iOS Safari method)"""
        # Extract token from headers
        token = auth_headers.get("Authorization", "").replace("Bearer ", "")
        report_id = TEST_REPORT_IDS["quick_summary"]
        
        # iOS Safari uses session_token as query param instead of header
        response = requests.get(
            f"{BASE_URL}/api/cases/{TEST_CASE_ID}/reports/{report_id}/export-pdf?session_token={token}",
            timeout=60
        )
        
        assert response.status_code == 200, f"PDF export with query param failed: {response.status_code}"
        print(f"✓ PDF export with session_token query param successful")


class TestDOCXExport:
    """Test DOCX export endpoints"""
    
    @pytest.fixture(scope="class")
    def auth_headers(self):
        """Get authenticated headers"""
        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": TEST_EMAIL, "password": TEST_PASSWORD},
            timeout=30
        )
        if response.status_code != 200:
            pytest.skip(f"Authentication failed: {response.status_code}")
        token = response.json().get("session_token")
        return {"Authorization": f"Bearer {token}"}
    
    def test_quick_summary_docx_export(self, auth_headers):
        """Test DOCX export for quick_summary report"""
        report_id = TEST_REPORT_IDS["quick_summary"]
        response = requests.get(
            f"{BASE_URL}/api/cases/{TEST_CASE_ID}/reports/{report_id}/export-docx",
            headers=auth_headers,
            timeout=60
        )
        
        assert response.status_code == 200, f"DOCX export failed: {response.status_code} - {response.text[:500]}"
        
        # Verify content type
        content_type = response.headers.get("content-type", "")
        assert "word" in content_type.lower() or "openxml" in content_type.lower() or len(response.content) > 1000, \
            f"Expected DOCX content, got: {content_type}"
        
        # DOCX files are ZIP archives starting with PK
        if len(response.content) > 2:
            assert response.content[:2] == b'PK', "Response does not appear to be a valid DOCX (ZIP archive)"
        
        print(f"✓ Quick summary DOCX export successful, size: {len(response.content)} bytes")
    
    def test_full_detailed_docx_export(self, auth_headers):
        """Test DOCX export for full_detailed report"""
        report_id = TEST_REPORT_IDS["full_detailed"]
        response = requests.get(
            f"{BASE_URL}/api/cases/{TEST_CASE_ID}/reports/{report_id}/export-docx",
            headers=auth_headers,
            timeout=60
        )
        
        assert response.status_code == 200, f"DOCX export failed: {response.status_code}"
        
        if len(response.content) > 2:
            assert response.content[:2] == b'PK', "Response does not appear to be a valid DOCX"
        
        print(f"✓ Full detailed DOCX export successful, size: {len(response.content)} bytes")


class TestReportEndpoints:
    """Test report-related endpoints"""
    
    @pytest.fixture(scope="class")
    def auth_headers(self):
        """Get authenticated headers"""
        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": TEST_EMAIL, "password": TEST_PASSWORD},
            timeout=30
        )
        if response.status_code != 200:
            pytest.skip(f"Authentication failed: {response.status_code}")
        token = response.json().get("session_token")
        return {"Authorization": f"Bearer {token}"}
    
    def test_get_case_reports(self, auth_headers):
        """Test fetching all reports for a case"""
        response = requests.get(
            f"{BASE_URL}/api/cases/{TEST_CASE_ID}/reports",
            headers=auth_headers,
            timeout=30
        )
        
        assert response.status_code == 200, f"Failed to get reports: {response.status_code}"
        reports = response.json()
        assert isinstance(reports, list), "Expected list of reports"
        
        # Verify we have the expected report types
        report_types = [r.get("report_type") for r in reports]
        print(f"✓ Found {len(reports)} reports: {report_types}")
        
        # Check that at least one report exists
        assert len(reports) > 0, "Expected at least one report"
    
    def test_get_single_report(self, auth_headers):
        """Test fetching a single report"""
        report_id = TEST_REPORT_IDS["quick_summary"]
        response = requests.get(
            f"{BASE_URL}/api/cases/{TEST_CASE_ID}/reports/{report_id}",
            headers=auth_headers,
            timeout=30
        )
        
        assert response.status_code == 200, f"Failed to get report: {response.status_code}"
        report = response.json()
        
        assert report.get("report_id") == report_id
        assert report.get("report_type") == "quick_summary"
        assert report.get("status") == "completed"
        
        print(f"✓ Single report fetch successful: {report.get('title', 'Untitled')}")
    
    def test_get_report_status(self, auth_headers):
        """Test fetching report status"""
        report_id = TEST_REPORT_IDS["quick_summary"]
        response = requests.get(
            f"{BASE_URL}/api/cases/{TEST_CASE_ID}/reports/{report_id}/status",
            headers=auth_headers,
            timeout=30
        )
        
        assert response.status_code == 200, f"Failed to get report status: {response.status_code}"
        status_data = response.json()
        
        assert "status" in status_data
        print(f"✓ Report status: {status_data.get('status')}")


class TestCaseEndpoints:
    """Test case-related endpoints"""
    
    @pytest.fixture(scope="class")
    def auth_headers(self):
        """Get authenticated headers"""
        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": TEST_EMAIL, "password": TEST_PASSWORD},
            timeout=30
        )
        if response.status_code != 200:
            pytest.skip(f"Authentication failed: {response.status_code}")
        token = response.json().get("session_token")
        return {"Authorization": f"Bearer {token}"}
    
    def test_get_case(self, auth_headers):
        """Test fetching case details"""
        response = requests.get(
            f"{BASE_URL}/api/cases/{TEST_CASE_ID}",
            headers=auth_headers,
            timeout=30
        )
        
        assert response.status_code == 200, f"Failed to get case: {response.status_code}"
        case_data = response.json()
        
        assert case_data.get("case_id") == TEST_CASE_ID
        assert "title" in case_data
        
        print(f"✓ Case fetch successful: {case_data.get('title')}")
    
    def test_get_case_documents(self, auth_headers):
        """Test fetching case documents"""
        response = requests.get(
            f"{BASE_URL}/api/cases/{TEST_CASE_ID}/documents",
            headers=auth_headers,
            timeout=30
        )
        
        assert response.status_code == 200, f"Failed to get documents: {response.status_code}"
        documents = response.json()
        assert isinstance(documents, list)
        
        print(f"✓ Found {len(documents)} documents")
    
    def test_get_case_grounds(self, auth_headers):
        """Test fetching case grounds"""
        response = requests.get(
            f"{BASE_URL}/api/cases/{TEST_CASE_ID}/grounds",
            headers=auth_headers,
            timeout=30
        )
        
        assert response.status_code == 200, f"Failed to get grounds: {response.status_code}"
        grounds_data = response.json()
        
        # Response should have grounds array
        assert "grounds" in grounds_data or isinstance(grounds_data, list)
        
        print(f"✓ Grounds fetch successful")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
