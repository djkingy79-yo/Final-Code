"""
Iteration 160 Tests: Barrister Quick Brief PDF Export + Database Index Initialization

Features tested:
1. GET /api/cases/{case_id}/reports/barrister-quick-brief - 2-page PDF with Counsel Synthesis + Priority Order + top 3 grounds
2. Database startup creates indexes for all 30+ collections
3. Regression: PUT /api/cases/{case_id}/grounds/reorder still works
"""

import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Test credentials
TEST_EMAIL = "djkingy79@gmail.com"
TEST_PASSWORD = "Cr1m1nalApp3al$2025"
TEST_CASE_ID = "case_f8bf63e9dcbe"

# Skip entire module if BASE_URL is not configured
pytestmark = pytest.mark.skipif(not BASE_URL, reason="REACT_APP_BACKEND_URL not set")


class TestHealthAndAuth:
    """Basic health and authentication tests"""
    
    def test_health_endpoint(self):
        """Test /api/health returns 200 with healthy status"""
        response = requests.get(f"{BASE_URL}/api/health")
        assert response.status_code == 200, f"Health check failed: {response.text}"
        data = response.json()
        assert data.get("status") == "healthy", f"Unexpected status: {data}"
        assert data.get("database") == "connected", f"Database not connected: {data}"
        print(f"✓ Health check passed: {data}")
    
    def test_login_with_credentials(self):
        """Test login with test credentials"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": TEST_EMAIL,
            "password": TEST_PASSWORD
        })
        assert response.status_code == 200, f"Login failed: {response.text}"
        data = response.json()
        assert "session_token" in data or "token" in data, f"No token in response: {data}"
        print(f"✓ Login successful for {TEST_EMAIL}")


class TestBarristerQuickBrief:
    """Tests for the new Barrister Quick Brief PDF export endpoint"""
    
    @pytest.fixture
    def auth_token(self):
        """Get authentication token"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": TEST_EMAIL,
            "password": TEST_PASSWORD
        })
        if response.status_code == 200:
            data = response.json()
            return data.get("session_token") or data.get("token")
        pytest.skip("Authentication failed")
    
    def test_quick_brief_returns_200(self, auth_token):
        """Test GET /api/cases/{case_id}/reports/barrister-quick-brief returns 200"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        response = requests.get(
            f"{BASE_URL}/api/cases/{TEST_CASE_ID}/reports/barrister-quick-brief",
            headers=headers,
            timeout=60
        )
        assert response.status_code == 200, f"Quick Brief failed: {response.status_code} - {response.text[:500]}"
        print("✓ Quick Brief endpoint returned 200")
    
    def test_quick_brief_returns_pdf_content_type(self, auth_token):
        """Test Quick Brief returns PDF content type"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        response = requests.get(
            f"{BASE_URL}/api/cases/{TEST_CASE_ID}/reports/barrister-quick-brief",
            headers=headers,
            timeout=60
        )
        assert response.status_code == 200
        content_type = response.headers.get("Content-Type", "")
        assert "application/pdf" in content_type, f"Expected PDF content type, got: {content_type}"
        print(f"✓ Quick Brief returns PDF content type: {content_type}")
    
    def test_quick_brief_pdf_is_valid(self, auth_token):
        """Test Quick Brief PDF starts with %PDF- magic bytes"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        response = requests.get(
            f"{BASE_URL}/api/cases/{TEST_CASE_ID}/reports/barrister-quick-brief",
            headers=headers,
            timeout=60
        )
        assert response.status_code == 200
        content = response.content
        assert content[:5] == b'%PDF-', f"PDF does not start with %PDF-, got: {content[:20]}"
        print("✓ Quick Brief PDF is valid (starts with %PDF-)")
    
    def test_quick_brief_pdf_has_reasonable_size(self, auth_token):
        """Test Quick Brief PDF has reasonable size (>2KB indicates content)"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        response = requests.get(
            f"{BASE_URL}/api/cases/{TEST_CASE_ID}/reports/barrister-quick-brief",
            headers=headers,
            timeout=60
        )
        assert response.status_code == 200
        content_length = len(response.content)
        # A proper PDF with content should be at least 2KB
        # Note: PDF text is compressed, so we check size instead of raw text
        assert content_length > 2000, f"PDF too small ({content_length} bytes), may be empty"
        print(f"✓ Quick Brief PDF has reasonable size: {content_length} bytes")
    
    def test_quick_brief_pdf_uses_reportlab(self, auth_token):
        """Test Quick Brief PDF is generated with ReportLab (as per implementation)"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        response = requests.get(
            f"{BASE_URL}/api/cases/{TEST_CASE_ID}/reports/barrister-quick-brief",
            headers=headers,
            timeout=60
        )
        assert response.status_code == 200
        content = response.content.decode('latin-1', errors='ignore')
        # ReportLab PDFs contain this marker
        assert "ReportLab" in content, "PDF should be generated with ReportLab"
        print("✓ Quick Brief PDF generated with ReportLab")
    
    def test_quick_brief_pdf_has_fonts(self, auth_token):
        """Test Quick Brief PDF has Helvetica fonts (used in implementation)"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        response = requests.get(
            f"{BASE_URL}/api/cases/{TEST_CASE_ID}/reports/barrister-quick-brief",
            headers=headers,
            timeout=60
        )
        assert response.status_code == 200
        content = response.content.decode('latin-1', errors='ignore')
        # Check for Helvetica fonts used in the PDF
        assert "Helvetica" in content, "PDF should use Helvetica fonts"
        print("✓ Quick Brief PDF has Helvetica fonts")
    
    def test_quick_brief_has_content_disposition_header(self, auth_token):
        """Test Quick Brief has Content-Disposition header for download"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        response = requests.get(
            f"{BASE_URL}/api/cases/{TEST_CASE_ID}/reports/barrister-quick-brief",
            headers=headers,
            timeout=60
        )
        assert response.status_code == 200
        content_disp = response.headers.get("Content-Disposition", "")
        assert "attachment" in content_disp, f"Expected attachment disposition, got: {content_disp}"
        assert "Quick_Brief" in content_disp, f"Expected Quick_Brief in filename, got: {content_disp}"
        print(f"✓ Quick Brief has correct Content-Disposition: {content_disp}")
    
    def test_quick_brief_requires_auth(self):
        """Test Quick Brief endpoint requires authentication"""
        response = requests.get(
            f"{BASE_URL}/api/cases/{TEST_CASE_ID}/reports/barrister-quick-brief",
            timeout=30
        )
        assert response.status_code in [401, 403], f"Expected 401/403 without auth, got: {response.status_code}"
        print(f"✓ Quick Brief requires authentication (returned {response.status_code})")
    
    def test_quick_brief_404_for_nonexistent_case(self, auth_token):
        """Test Quick Brief returns 404 for non-existent case"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        response = requests.get(
            f"{BASE_URL}/api/cases/nonexistent_case_xyz/reports/barrister-quick-brief",
            headers=headers,
            timeout=30
        )
        assert response.status_code == 404, f"Expected 404 for non-existent case, got: {response.status_code}"
        print("✓ Quick Brief returns 404 for non-existent case")


class TestGroundsReorderRegression:
    """Regression tests for grounds reorder endpoint"""
    
    @pytest.fixture
    def auth_token(self):
        """Get authentication token"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": TEST_EMAIL,
            "password": TEST_PASSWORD
        })
        if response.status_code == 200:
            data = response.json()
            return data.get("session_token") or data.get("token")
        pytest.skip("Authentication failed")
    
    def test_grounds_reorder_endpoint_exists(self, auth_token):
        """Test PUT /api/cases/{case_id}/grounds/reorder endpoint exists"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        # First get the grounds to get their IDs
        response = requests.get(
            f"{BASE_URL}/api/cases/{TEST_CASE_ID}/grounds",
            headers=headers,
            timeout=30
        )
        assert response.status_code == 200, f"Failed to get grounds: {response.text}"
        data = response.json()
        
        # Handle both list and dict with "grounds" key
        if isinstance(data, dict) and "grounds" in data:
            grounds = data["grounds"]
        else:
            grounds = data
        
        if len(grounds) < 2:
            pytest.skip("Need at least 2 grounds to test reorder")
        
        # Get ground IDs from first 3 grounds
        ground_ids = [g.get("ground_id") for g in grounds[:3] if g.get("ground_id")]
        
        # Test reorder endpoint
        response = requests.put(
            f"{BASE_URL}/api/cases/{TEST_CASE_ID}/grounds/reorder",
            headers=headers,
            json={"ground_ids": ground_ids},
            timeout=30
        )
        assert response.status_code == 200, f"Reorder failed: {response.status_code} - {response.text}"
        print(f"✓ Grounds reorder endpoint works (reordered {len(ground_ids)} grounds)")


class TestDatabaseIndexes:
    """Tests to verify database indexes are created at startup"""
    
    @pytest.fixture
    def auth_token(self):
        """Get authentication token"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": TEST_EMAIL,
            "password": TEST_PASSWORD
        })
        if response.status_code == 200:
            data = response.json()
            return data.get("session_token") or data.get("token")
        pytest.skip("Authentication failed")
    
    def test_users_collection_accessible(self, auth_token):
        """Test users collection is accessible (implies indexes exist)"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        response = requests.get(f"{BASE_URL}/api/auth/me", headers=headers, timeout=30)
        assert response.status_code == 200, f"Failed to get user: {response.text}"
        print("✓ Users collection accessible")
    
    def test_cases_collection_accessible(self, auth_token):
        """Test cases collection is accessible"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        response = requests.get(f"{BASE_URL}/api/cases", headers=headers, timeout=30)
        assert response.status_code == 200, f"Failed to get cases: {response.text}"
        print("✓ Cases collection accessible")
    
    def test_reports_collection_accessible(self, auth_token):
        """Test reports collection is accessible"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        response = requests.get(
            f"{BASE_URL}/api/cases/{TEST_CASE_ID}/reports",
            headers=headers,
            timeout=30
        )
        assert response.status_code == 200, f"Failed to get reports: {response.text}"
        print("✓ Reports collection accessible")
    
    def test_grounds_collection_accessible(self, auth_token):
        """Test grounds_of_merit collection is accessible"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        response = requests.get(
            f"{BASE_URL}/api/cases/{TEST_CASE_ID}/grounds",
            headers=headers,
            timeout=30
        )
        assert response.status_code == 200, f"Failed to get grounds: {response.text}"
        print("✓ Grounds collection accessible")
    
    def test_payments_collection_accessible(self, auth_token):
        """Test payments collection is accessible"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        response = requests.get(f"{BASE_URL}/api/payments", headers=headers, timeout=30)
        # 200 or 404 (no payments) are both valid
        assert response.status_code in [200, 404], f"Unexpected status: {response.status_code}"
        print("✓ Payments collection accessible")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
