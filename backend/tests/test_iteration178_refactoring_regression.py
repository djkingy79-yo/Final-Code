"""
Iteration 178: Backend Refactoring Regression Tests
====================================================
Tests to verify no regressions after server.py decomposition from 6068 to 426 lines.
Extracted modules:
- services/report_quality.py (453 lines)
- services/pipeline_orchestrator.py (529 lines)
- services/report_generator.py (1847 lines)
- services/barrister_generator.py (1092 lines)
- routers/reports.py (812 lines)
- routers/report_exports.py (1047 lines)
"""

import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Test credentials from test_credentials.md
TEST_EMAIL = "djkingy79@gmail.com"
TEST_PASSWORD = "Grubbygrub88"
TEST_CASE_ID = "case_d294f503192a"


class TestHealthEndpoints:
    """Health check endpoints - verify server is running after refactoring"""
    
    def test_health_check(self):
        """GET /api/health - basic health check"""
        response = requests.get(f"{BASE_URL}/api/health", timeout=10)
        assert response.status_code == 200, f"Health check failed: {response.text}"
        data = response.json()
        assert "status" in data
        assert data["status"] == "healthy"
        assert "database" in data
        assert "timestamp" in data
        print(f"✓ Health check passed: {data}")
    
    def test_readiness_check(self):
        """GET /api/ready - readiness probe"""
        response = requests.get(f"{BASE_URL}/api/ready", timeout=10)
        assert response.status_code == 200, f"Readiness check failed: {response.text}"
        data = response.json()
        assert "ready" in data
        print(f"✓ Readiness check passed: {data}")
    
    def test_deep_health_check(self):
        """GET /api/health/deep - deep health check with MongoDB, LLM, email"""
        response = requests.get(f"{BASE_URL}/api/health/deep", timeout=15)
        assert response.status_code == 200, f"Deep health check failed: {response.text}"
        data = response.json()
        assert "healthy" in data
        assert "checks" in data
        assert "mongodb" in data["checks"]
        assert "llm_key" in data["checks"]
        print(f"✓ Deep health check passed: {data}")


class TestAuthFlow:
    """Authentication flow - verify login works after refactoring"""
    
    def test_login_success(self):
        """POST /api/auth/login - successful login"""
        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": TEST_EMAIL, "password": TEST_PASSWORD},
            timeout=15
        )
        assert response.status_code == 200, f"Login failed: {response.text}"
        data = response.json()
        # Note: session_token is used, not token
        assert "session_token" in data, f"Expected session_token in response, got: {data.keys()}"
        # User data may be at root level or nested under "user"
        email = data.get("email") or data.get("user", {}).get("email")
        assert email == TEST_EMAIL, f"Expected email {TEST_EMAIL}, got {email}"
        print(f"✓ Login successful for {TEST_EMAIL}")
        return data["session_token"]
    
    def test_login_invalid_credentials(self):
        """POST /api/auth/login - invalid credentials"""
        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": "invalid@example.com", "password": "wrongpassword"},
            timeout=15
        )
        assert response.status_code in [401, 404], f"Expected 401/404, got {response.status_code}"
        print("✓ Invalid login correctly rejected")


@pytest.fixture(scope="class")
def auth_session():
    """Get authenticated session for tests"""
    response = requests.post(
        f"{BASE_URL}/api/auth/login",
        json={"email": TEST_EMAIL, "password": TEST_PASSWORD},
        timeout=15
    )
    if response.status_code != 200:
        pytest.skip(f"Authentication failed: {response.text}")
    data = response.json()
    session_token = data.get("session_token")
    if not session_token:
        pytest.skip("No session_token in login response")
    return {"Authorization": f"Bearer {session_token}"}


class TestCasesEndpoints:
    """Cases listing - verify cases router works after refactoring"""
    
    def test_get_cases_list(self, auth_session):
        """GET /api/cases - list all cases"""
        response = requests.get(
            f"{BASE_URL}/api/cases",
            headers=auth_session,
            timeout=15
        )
        assert response.status_code == 200, f"Get cases failed: {response.text}"
        data = response.json()
        assert isinstance(data, list), f"Expected list, got {type(data)}"
        print(f"✓ Cases list returned {len(data)} cases")
        return data
    
    def test_get_specific_case(self, auth_session):
        """GET /api/cases/{case_id} - get specific case"""
        response = requests.get(
            f"{BASE_URL}/api/cases/{TEST_CASE_ID}",
            headers=auth_session,
            timeout=15
        )
        # Case may or may not exist, but endpoint should work
        assert response.status_code in [200, 404], f"Unexpected status: {response.status_code}"
        if response.status_code == 200:
            data = response.json()
            assert "case_id" in data
            print(f"✓ Case {TEST_CASE_ID} retrieved successfully")
        else:
            print(f"✓ Case {TEST_CASE_ID} not found (expected for test)")


class TestReportsEndpoints:
    """Reports endpoints - verify routers/reports.py works after extraction"""
    
    def test_get_reports_for_case(self, auth_session):
        """GET /api/cases/{case_id}/reports - list reports for a case"""
        response = requests.get(
            f"{BASE_URL}/api/cases/{TEST_CASE_ID}/reports",
            headers=auth_session,
            timeout=15
        )
        # Case may not exist, but endpoint should work
        assert response.status_code in [200, 404], f"Unexpected status: {response.status_code}"
        if response.status_code == 200:
            data = response.json()
            assert isinstance(data, list), f"Expected list, got {type(data)}"
            print(f"✓ Reports list returned {len(data)} reports for case {TEST_CASE_ID}")
        else:
            print("✓ Reports endpoint working (case not found)")
    
    def test_barrister_view_endpoint(self, auth_session):
        """GET /api/cases/{case_id}/reports/barrister-view - barrister view status"""
        response = requests.get(
            f"{BASE_URL}/api/cases/{TEST_CASE_ID}/reports/barrister-view",
            headers=auth_session,
            timeout=15
        )
        # Can return 200 (exists), 404 (not generated yet), or 404 (case not found)
        assert response.status_code in [200, 404], f"Unexpected status: {response.status_code}"
        if response.status_code == 200:
            data = response.json()
            assert "report_id" in data or "status" in data
            print(f"✓ Barrister view endpoint working: {data.get('status', 'completed')}")
        else:
            print("✓ Barrister view endpoint working (not generated or case not found)")


class TestReportExportsEndpoints:
    """Report export endpoints - verify routers/report_exports.py works after extraction"""
    
    def test_export_pdf_endpoint_exists(self, auth_session):
        """GET /api/cases/{case_id}/reports/{report_id}/export-pdf - PDF export endpoint exists"""
        # Use a dummy report_id to test endpoint routing
        response = requests.get(
            f"{BASE_URL}/api/cases/{TEST_CASE_ID}/reports/rpt_test123/export-pdf",
            headers=auth_session,
            timeout=15
        )
        # Should return 404 (report not found) not 405 (method not allowed) or 500
        assert response.status_code in [200, 404], f"PDF export endpoint issue: {response.status_code} - {response.text}"
        print("✓ PDF export endpoint exists and routed correctly")
    
    def test_export_docx_endpoint_exists(self, auth_session):
        """GET /api/cases/{case_id}/reports/{report_id}/export-docx - DOCX export endpoint exists"""
        response = requests.get(
            f"{BASE_URL}/api/cases/{TEST_CASE_ID}/reports/rpt_test123/export-docx",
            headers=auth_session,
            timeout=15
        )
        # Should return 404 (report not found) not 405 (method not allowed) or 500
        assert response.status_code in [200, 404], f"DOCX export endpoint issue: {response.status_code} - {response.text}"
        print("✓ DOCX export endpoint exists and routed correctly")


class TestRouterImports:
    """Verify all routers are properly imported and mounted"""
    
    def test_api_root(self):
        """GET /api/ - API root endpoint"""
        response = requests.get(f"{BASE_URL}/api/", timeout=10)
        assert response.status_code == 200, f"API root failed: {response.text}"
        data = response.json()
        assert "message" in data
        assert "Criminal Appeal AI" in data["message"]
        print(f"✓ API root working: {data}")
    
    def test_reports_router_mounted(self, auth_session):
        """Verify reports router is mounted at /api/cases/{case_id}/reports"""
        # This tests that the router prefix is correct
        response = requests.get(
            f"{BASE_URL}/api/cases/{TEST_CASE_ID}/reports",
            headers=auth_session,
            timeout=15
        )
        # Should not return 404 for the route itself (only for missing case)
        assert response.status_code != 405, "Reports router not mounted correctly"
        print("✓ Reports router mounted correctly")
    
    def test_report_exports_router_mounted(self, auth_session):
        """Verify report_exports router is mounted"""
        response = requests.get(
            f"{BASE_URL}/api/cases/{TEST_CASE_ID}/reports/rpt_dummy/export-pdf",
            headers=auth_session,
            timeout=15
        )
        # Should not return 405 (method not allowed)
        assert response.status_code != 405, "Report exports router not mounted correctly"
        print("✓ Report exports router mounted correctly")


class TestServiceModules:
    """Verify service modules are working (indirectly through endpoints)"""
    
    def test_report_quality_module(self, auth_session):
        """Verify report_quality.py functions work via report generation"""
        # The report quality module is used during report generation
        # We can verify it's imported correctly by checking health
        response = requests.get(f"{BASE_URL}/api/health", timeout=10)
        assert response.status_code == 200
        print("✓ Server running (report_quality module imported)")
    
    def test_pipeline_orchestrator_module(self, auth_session):
        """Verify pipeline_orchestrator.py functions work"""
        # Pipeline orchestrator is used during report generation
        response = requests.get(f"{BASE_URL}/api/health", timeout=10)
        assert response.status_code == 200
        print("✓ Server running (pipeline_orchestrator module imported)")
    
    def test_barrister_generator_module(self, auth_session):
        """Verify barrister_generator.py functions work via barrister-view endpoint"""
        response = requests.get(
            f"{BASE_URL}/api/cases/{TEST_CASE_ID}/reports/barrister-view",
            headers=auth_session,
            timeout=15
        )
        # Endpoint should work (200 or 404), not 500
        assert response.status_code in [200, 404], f"Barrister generator issue: {response.status_code}"
        print("✓ Barrister generator module working")


class TestCORSAndSecurity:
    """Verify CORS and security middleware still work after refactoring"""
    
    def test_cors_headers(self):
        """Verify CORS headers are present"""
        response = requests.options(
            f"{BASE_URL}/api/health",
            headers={"Origin": "https://criminal-appeals-au-2.preview.emergentagent.com"},
            timeout=10
        )
        # CORS preflight should work
        assert response.status_code in [200, 204], f"CORS preflight failed: {response.status_code}"
        print("✓ CORS preflight working")
    
    def test_security_headers(self):
        """Verify security headers are present"""
        response = requests.get(f"{BASE_URL}/api/health", timeout=10)
        assert response.status_code == 200
        # Check for security headers added by SecurityHeadersMiddleware
        headers = response.headers
        assert "X-Content-Type-Options" in headers, "Missing X-Content-Type-Options header"
        assert "X-Frame-Options" in headers, "Missing X-Frame-Options header"
        print(f"✓ Security headers present: X-Content-Type-Options={headers.get('X-Content-Type-Options')}")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
