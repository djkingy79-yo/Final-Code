"""
Test Document Export Formatting - PDF, DOCX, and Barrister View exports
Tests for iteration 174: Document formatting overhaul verification
- PDF export returns HTTP 200 for quick_summary, full_detailed, barrister-view
- DOCX export returns HTTP 200 for quick_summary, full_detailed, barrister-view
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', 'http://localhost:8001').rstrip('/')

# Test credentials
TEST_EMAIL = "djkingy79@gmail.com"
TEST_PASSWORD = "Grubbygrub88"

# Test case and report IDs
TEST_CASE_ID = "case_6cc234434cbd"
QUICK_SUMMARY_REPORT_ID = "rpt_0f71b9abfacd"
FULL_DETAILED_REPORT_ID = "rpt_2f3effb97c84"
EXTENSIVE_REPORT_ID = "rpt_42fc6f6dddb9"


@pytest.fixture(scope="module")
def session_token():
    """Get authentication token for testing"""
    response = requests.post(
        f"{BASE_URL}/api/auth/login",
        json={"email": TEST_EMAIL, "password": TEST_PASSWORD}
    )
    if response.status_code == 200:
        data = response.json()
        return data.get("session_token") or data.get("token")
    pytest.skip(f"Authentication failed: {response.status_code} - {response.text}")


@pytest.fixture(scope="module")
def auth_headers(session_token):
    """Return headers with authentication"""
    return {
        "Authorization": f"Bearer {session_token}",
        "Content-Type": "application/json"
    }


class TestHealthCheck:
    """Basic health check to ensure API is running"""
    
    def test_api_health(self):
        """Test API health endpoint"""
        response = requests.get(f"{BASE_URL}/api/health")
        assert response.status_code == 200, f"Health check failed: {response.status_code}"
        print("✓ API health check passed")


class TestPDFExport:
    """Test PDF export endpoints for all report types"""
    
    def test_pdf_export_quick_summary(self, auth_headers):
        """Test PDF export for quick_summary report (rpt_0f71b9abfacd)"""
        url = f"{BASE_URL}/api/cases/{TEST_CASE_ID}/reports/{QUICK_SUMMARY_REPORT_ID}/export-pdf"
        response = requests.get(url, headers=auth_headers, timeout=60)
        
        assert response.status_code == 200, f"PDF export failed for quick_summary: {response.status_code} - {response.text}"
        assert response.headers.get('content-type') == 'application/pdf', f"Wrong content type: {response.headers.get('content-type')}"
        assert len(response.content) > 1000, "PDF content too small, likely empty"
        print(f"✓ PDF export for quick_summary returned 200 OK ({len(response.content)} bytes)")
    
    def test_pdf_export_full_detailed(self, auth_headers):
        """Test PDF export for full_detailed report (rpt_2f3effb97c84)"""
        url = f"{BASE_URL}/api/cases/{TEST_CASE_ID}/reports/{FULL_DETAILED_REPORT_ID}/export-pdf"
        response = requests.get(url, headers=auth_headers, timeout=60)
        
        assert response.status_code == 200, f"PDF export failed for full_detailed: {response.status_code} - {response.text}"
        assert response.headers.get('content-type') == 'application/pdf', f"Wrong content type: {response.headers.get('content-type')}"
        assert len(response.content) > 1000, "PDF content too small, likely empty"
        print(f"✓ PDF export for full_detailed returned 200 OK ({len(response.content)} bytes)")
    
    def test_pdf_export_barrister_view(self, auth_headers):
        """Test PDF export for barrister-view"""
        url = f"{BASE_URL}/api/cases/{TEST_CASE_ID}/reports/barrister-view/export-pdf"
        response = requests.get(url, headers=auth_headers, timeout=60)
        
        assert response.status_code == 200, f"PDF export failed for barrister-view: {response.status_code} - {response.text}"
        assert response.headers.get('content-type') == 'application/pdf', f"Wrong content type: {response.headers.get('content-type')}"
        assert len(response.content) > 1000, "PDF content too small, likely empty"
        print(f"✓ PDF export for barrister-view returned 200 OK ({len(response.content)} bytes)")


class TestDOCXExport:
    """Test DOCX export endpoints for all report types"""
    
    def test_docx_export_quick_summary(self, auth_headers):
        """Test DOCX export for quick_summary report (rpt_0f71b9abfacd)"""
        url = f"{BASE_URL}/api/cases/{TEST_CASE_ID}/reports/{QUICK_SUMMARY_REPORT_ID}/export-docx"
        response = requests.get(url, headers=auth_headers, timeout=60)
        
        assert response.status_code == 200, f"DOCX export failed for quick_summary: {response.status_code} - {response.text}"
        content_type = response.headers.get('content-type', '')
        assert 'application/vnd.openxmlformats-officedocument.wordprocessingml.document' in content_type or 'application/octet-stream' in content_type, f"Wrong content type: {content_type}"
        assert len(response.content) > 1000, "DOCX content too small, likely empty"
        print(f"✓ DOCX export for quick_summary returned 200 OK ({len(response.content)} bytes)")
    
    def test_docx_export_full_detailed(self, auth_headers):
        """Test DOCX export for full_detailed report (rpt_2f3effb97c84)"""
        url = f"{BASE_URL}/api/cases/{TEST_CASE_ID}/reports/{FULL_DETAILED_REPORT_ID}/export-docx"
        response = requests.get(url, headers=auth_headers, timeout=60)
        
        assert response.status_code == 200, f"DOCX export failed for full_detailed: {response.status_code} - {response.text}"
        content_type = response.headers.get('content-type', '')
        assert 'application/vnd.openxmlformats-officedocument.wordprocessingml.document' in content_type or 'application/octet-stream' in content_type, f"Wrong content type: {content_type}"
        assert len(response.content) > 1000, "DOCX content too small, likely empty"
        print(f"✓ DOCX export for full_detailed returned 200 OK ({len(response.content)} bytes)")
    
    def test_docx_export_barrister_view(self, auth_headers):
        """Test DOCX export for barrister-view"""
        url = f"{BASE_URL}/api/cases/{TEST_CASE_ID}/reports/barrister-view/export-docx"
        response = requests.get(url, headers=auth_headers, timeout=60)
        
        assert response.status_code == 200, f"DOCX export failed for barrister-view: {response.status_code} - {response.text}"
        content_type = response.headers.get('content-type', '')
        assert 'application/vnd.openxmlformats-officedocument.wordprocessingml.document' in content_type or 'application/octet-stream' in content_type, f"Wrong content type: {content_type}"
        assert len(response.content) > 1000, "DOCX content too small, likely empty"
        print(f"✓ DOCX export for barrister-view returned 200 OK ({len(response.content)} bytes)")


class TestReportAccess:
    """Test report access endpoints"""
    
    def test_get_quick_summary_report(self, auth_headers):
        """Test accessing quick_summary report"""
        url = f"{BASE_URL}/api/cases/{TEST_CASE_ID}/reports/{QUICK_SUMMARY_REPORT_ID}"
        response = requests.get(url, headers=auth_headers)
        
        assert response.status_code == 200, f"Failed to get quick_summary report: {response.status_code}"
        data = response.json()
        assert data.get('report_type') == 'quick_summary', f"Wrong report type: {data.get('report_type')}"
        print(f"✓ Quick summary report accessible: {data.get('title', 'N/A')}")
    
    def test_get_full_detailed_report(self, auth_headers):
        """Test accessing full_detailed report"""
        url = f"{BASE_URL}/api/cases/{TEST_CASE_ID}/reports/{FULL_DETAILED_REPORT_ID}"
        response = requests.get(url, headers=auth_headers)
        
        assert response.status_code == 200, f"Failed to get full_detailed report: {response.status_code}"
        data = response.json()
        assert data.get('report_type') == 'full_detailed', f"Wrong report type: {data.get('report_type')}"
        print(f"✓ Full detailed report accessible: {data.get('title', 'N/A')}")
    
    def test_get_barrister_view(self, auth_headers):
        """Test accessing barrister-view"""
        url = f"{BASE_URL}/api/cases/{TEST_CASE_ID}/reports/barrister-view"
        response = requests.get(url, headers=auth_headers)
        
        assert response.status_code == 200, f"Failed to get barrister-view: {response.status_code}"
        data = response.json()
        assert data.get('report_type') == 'barrister_view', f"Wrong report type: {data.get('report_type')}"
        print(f"✓ Barrister view accessible: {data.get('title', 'N/A')}")


class TestCaseAccess:
    """Test case access"""
    
    def test_get_case(self, auth_headers):
        """Test accessing the test case"""
        url = f"{BASE_URL}/api/cases/{TEST_CASE_ID}"
        response = requests.get(url, headers=auth_headers)
        
        assert response.status_code == 200, f"Failed to get case: {response.status_code}"
        data = response.json()
        assert data.get('case_id') == TEST_CASE_ID, f"Wrong case ID: {data.get('case_id')}"
        print(f"✓ Case accessible: {data.get('title', 'N/A')} - State: {data.get('state', 'N/A')}")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
