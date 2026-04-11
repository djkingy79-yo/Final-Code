"""
Iteration 187 - Testing new features:
1. Case Law Search with AI-suggested authorities
2. Barrister Pack PDF generation
3. Barrister Quick Brief PDF
4. Download token auth
5. Footer standardisation
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')
TEST_EMAIL = "djkingy79@gmail.com"
TEST_PASSWORD = "Grubbygrub88"
TEST_CASE_ID = "case_e24c3880b02f"


class TestAuth:
    """Authentication tests"""
    
    @pytest.fixture(scope="class")
    def session_token(self):
        """Get session token for authenticated requests"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": TEST_EMAIL,
            "password": TEST_PASSWORD
        })
        assert response.status_code == 200, f"Login failed: {response.text}"
        data = response.json()
        return data.get("session_token")
    
    def test_login_success(self):
        """Test login returns session token"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": TEST_EMAIL,
            "password": TEST_PASSWORD
        })
        assert response.status_code == 200
        data = response.json()
        assert "session_token" in data
        assert data.get("email") == TEST_EMAIL
    
    def test_download_token_generation(self, session_token):
        """Test download token generation endpoint"""
        response = requests.post(
            f"{BASE_URL}/api/auth/download-token",
            headers={"Authorization": f"Bearer {session_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "download_token" in data
        assert len(data["download_token"]) > 10


class TestCaseLawSearch:
    """Case Law Search API tests"""
    
    @pytest.fixture(scope="class")
    def session_token(self):
        """Get session token for authenticated requests"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": TEST_EMAIL,
            "password": TEST_PASSWORD
        })
        assert response.status_code == 200
        return response.json().get("session_token")
    
    def test_caselaw_search_returns_suggested_authorities(self, session_token):
        """Test GET /api/cases/{case_id}/caselaw/search returns suggested_authorities array"""
        response = requests.get(
            f"{BASE_URL}/api/cases/{TEST_CASE_ID}/caselaw/search",
            headers={"Authorization": f"Bearer {session_token}"}
        )
        assert response.status_code == 200, f"Failed: {response.text}"
        data = response.json()
        
        # Verify response structure
        assert "query" in data
        assert "state" in data
        assert "search_links" in data
        assert "suggested_authorities" in data
        assert isinstance(data["suggested_authorities"], list)
        
        # If there are authorities, verify structure
        if len(data["suggested_authorities"]) > 0:
            auth = data["suggested_authorities"][0]
            assert "type" in auth  # 'case' or 'legislation'
            assert "name" in auth
    
    def test_caselaw_search_with_custom_query(self, session_token):
        """Test case law search with custom query parameter"""
        response = requests.get(
            f"{BASE_URL}/api/cases/{TEST_CASE_ID}/caselaw/search?q=murder+appeal+NSW",
            headers={"Authorization": f"Bearer {session_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "murder" in data["query"].lower() or "appeal" in data["query"].lower()
    
    def test_caselaw_databases_list(self, session_token):
        """Test listing all case law databases"""
        response = requests.get(
            f"{BASE_URL}/api/caselaw/databases",
            headers={"Authorization": f"Bearer {session_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "states" in data or "national" in data


class TestBarristerPack:
    """Barrister Acceptance Pack PDF tests"""
    
    @pytest.fixture(scope="class")
    def session_token(self):
        """Get session token for authenticated requests"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": TEST_EMAIL,
            "password": TEST_PASSWORD
        })
        assert response.status_code == 200
        return response.json().get("session_token")
    
    def test_barrister_pack_generate_returns_pdf(self, session_token):
        """Test GET /api/cases/{case_id}/barrister-pack/generate returns PDF"""
        response = requests.get(
            f"{BASE_URL}/api/cases/{TEST_CASE_ID}/barrister-pack/generate",
            headers={"Authorization": f"Bearer {session_token}"},
            timeout=120
        )
        assert response.status_code == 200, f"Failed: {response.status_code} - {response.text[:500]}"
        assert response.headers.get("content-type") == "application/pdf"
        
        # Verify it's a valid PDF (starts with %PDF)
        content = response.content
        assert content[:4] == b'%PDF', "Response is not a valid PDF"
        assert len(content) > 1000, "PDF content too small"


class TestBarristerQuickBrief:
    """Barrister Quick Brief PDF tests"""
    
    @pytest.fixture(scope="class")
    def session_token(self):
        """Get session token for authenticated requests"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": TEST_EMAIL,
            "password": TEST_PASSWORD
        })
        assert response.status_code == 200
        return response.json().get("session_token")
    
    def test_quick_brief_returns_valid_pdf(self, session_token):
        """Test GET /api/cases/{case_id}/reports/barrister-quick-brief returns valid PDF"""
        response = requests.get(
            f"{BASE_URL}/api/cases/{TEST_CASE_ID}/reports/barrister-quick-brief",
            headers={"Authorization": f"Bearer {session_token}"},
            timeout=60
        )
        assert response.status_code == 200, f"Failed: {response.status_code} - {response.text[:500]}"
        assert response.headers.get("content-type") == "application/pdf"
        
        # Verify it's a valid PDF
        content = response.content
        assert content[:4] == b'%PDF', "Response is not a valid PDF"
        assert len(content) > 500, "PDF content too small"
    
    def test_quick_brief_with_download_token(self, session_token):
        """Test Quick Brief works with download token auth"""
        # First get a download token
        token_response = requests.post(
            f"{BASE_URL}/api/auth/download-token",
            headers={"Authorization": f"Bearer {session_token}"}
        )
        assert token_response.status_code == 200
        download_token = token_response.json().get("download_token")
        
        # Use download token to get Quick Brief
        response = requests.get(
            f"{BASE_URL}/api/cases/{TEST_CASE_ID}/reports/barrister-quick-brief?download_token={download_token}",
            timeout=60
        )
        assert response.status_code == 200, f"Failed with download token: {response.status_code}"
        assert response.headers.get("content-type") == "application/pdf"


class TestBarristerView:
    """Barrister View report tests"""
    
    @pytest.fixture(scope="class")
    def session_token(self):
        """Get session token for authenticated requests"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": TEST_EMAIL,
            "password": TEST_PASSWORD
        })
        assert response.status_code == 200
        return response.json().get("session_token")
    
    def test_barrister_view_exists(self, session_token):
        """Test barrister view endpoint returns report or 404"""
        response = requests.get(
            f"{BASE_URL}/api/cases/{TEST_CASE_ID}/reports/barrister-view",
            headers={"Authorization": f"Bearer {session_token}"}
        )
        # Either returns completed report or 404 if not generated
        assert response.status_code in [200, 404]
        
        if response.status_code == 200:
            data = response.json()
            assert "report_type" in data
            assert data["report_type"] == "barrister_view"


class TestFooterFormat:
    """Footer format standardisation tests"""
    
    @pytest.fixture(scope="class")
    def session_token(self):
        """Get session token for authenticated requests"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": TEST_EMAIL,
            "password": TEST_PASSWORD
        })
        assert response.status_code == 200
        return response.json().get("session_token")
    
    def test_export_footer_module_exists(self):
        """Verify export_footer.py module exists and has correct functions"""
        import sys
        sys.path.insert(0, '/app/backend')
        from services.export_footer import build_footer_label, format_export_date, NumberedCanvas
        
        # Test build_footer_label
        test_case = {"title": "Test Case", "defendant_name": "John Doe"}
        label = build_footer_label(test_case, "Quick Brief")
        
        assert "Documented from the Criminal Law /Appeal Management Application" in label
        assert "Quick Brief" in label
        assert "Test Case" in label or "John Doe" in label
    
    def test_footer_date_format(self):
        """Test footer date format is DD/MM/YYYY"""
        import sys
        sys.path.insert(0, '/app/backend')
        from services.export_footer import format_export_date
        from datetime import datetime, timezone
        
        date_str = format_export_date()
        # Should be DD/MM/YYYY format
        parts = date_str.split('/')
        assert len(parts) == 3
        assert len(parts[0]) == 2  # DD
        assert len(parts[1]) == 2  # MM
        assert len(parts[2]) == 4  # YYYY


class TestCaseData:
    """Test case data retrieval"""
    
    @pytest.fixture(scope="class")
    def session_token(self):
        """Get session token for authenticated requests"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": TEST_EMAIL,
            "password": TEST_PASSWORD
        })
        assert response.status_code == 200
        return response.json().get("session_token")
    
    def test_case_exists(self, session_token):
        """Verify test case exists"""
        response = requests.get(
            f"{BASE_URL}/api/cases/{TEST_CASE_ID}",
            headers={"Authorization": f"Bearer {session_token}"}
        )
        assert response.status_code == 200, f"Test case not found: {response.text}"
        data = response.json()
        assert "case_id" in data
        assert data["case_id"] == TEST_CASE_ID
    
    def test_case_has_grounds(self, session_token):
        """Verify test case has grounds of merit"""
        response = requests.get(
            f"{BASE_URL}/api/cases/{TEST_CASE_ID}/grounds",
            headers={"Authorization": f"Bearer {session_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        # Should have grounds array
        assert "grounds" in data or isinstance(data, list)


class TestHealthCheck:
    """Basic health check tests"""
    
    def test_health_endpoint(self):
        """Test health endpoint is accessible"""
        response = requests.get(f"{BASE_URL}/api/health")
        assert response.status_code == 200
        data = response.json()
        assert data.get("status") == "healthy"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
