"""
Iteration 59 Backend Tests:
1. Backend health check: GET /api/health returns healthy with database connected
2. POST /api/cases/{case_id}/progress-analysis returns AI analysis (endpoint exists)
3. POST /api/cases/{case_id}/reports/generate with report_type=extensive_log (endpoint accepts it)
4. Verify extensive_log prompt contains required content (code verification)
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

class TestHealthCheck:
    """Backend health check endpoint tests"""
    
    def test_health_endpoint_returns_healthy(self):
        """GET /api/health returns healthy with database connected"""
        response = requests.get(f"{BASE_URL}/api/health", timeout=10)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        assert data.get("status") == "healthy", f"Expected status 'healthy', got {data.get('status')}"
        assert data.get("database") == "connected", f"Expected database 'connected', got {data.get('database')}"
        assert "timestamp" in data, "Response should contain timestamp"
        print(f"PASS: Health check returns healthy with database connected")


class TestProgressAnalysisEndpoint:
    """POST /api/cases/{case_id}/progress-analysis endpoint tests"""
    
    def test_progress_analysis_requires_auth(self):
        """Endpoint requires authentication"""
        response = requests.post(f"{BASE_URL}/api/cases/test_case_id/progress-analysis", timeout=10)
        assert response.status_code == 401, f"Expected 401 without auth, got {response.status_code}"
        print(f"PASS: progress-analysis requires authentication")
    
    def test_progress_analysis_nonexistent_case_returns_404(self):
        """Nonexistent case returns 404 when authenticated"""
        # First login to get session
        login_response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": "deletetest@test.com", "password": "TestPass123!"},
            timeout=10
        )
        
        if login_response.status_code != 200:
            pytest.skip("Login failed - skipping authenticated test")
        
        cookies = login_response.cookies
        
        response = requests.post(
            f"{BASE_URL}/api/cases/nonexistent_case_xyz/progress-analysis",
            cookies=cookies,
            timeout=10
        )
        assert response.status_code == 404, f"Expected 404 for nonexistent case, got {response.status_code}"
        print(f"PASS: progress-analysis returns 404 for nonexistent case")


class TestReportsGenerateEndpoint:
    """POST /api/cases/{case_id}/reports/generate endpoint tests"""
    
    def test_reports_generate_requires_auth(self):
        """Endpoint requires authentication"""
        response = requests.post(
            f"{BASE_URL}/api/cases/test_case_id/reports/generate",
            json={"report_type": "extensive_log"},
            timeout=10
        )
        assert response.status_code == 401, f"Expected 401 without auth, got {response.status_code}"
        print(f"PASS: reports/generate requires authentication")
    
    def test_reports_generate_accepts_extensive_log_type(self):
        """Endpoint accepts report_type=extensive_log"""
        # Login first
        login_response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": "deletetest@test.com", "password": "TestPass123!"},
            timeout=10
        )
        
        if login_response.status_code != 200:
            pytest.skip("Login failed - skipping authenticated test")
        
        cookies = login_response.cookies
        
        # Try with nonexistent case - should return 404 (not 400 for invalid report type)
        response = requests.post(
            f"{BASE_URL}/api/cases/nonexistent_case_xyz/reports/generate",
            json={"report_type": "extensive_log"},
            cookies=cookies,
            timeout=10
        )
        # If extensive_log is valid, we'd get 404 (case not found) or 402 (payment required)
        # NOT 400 or 422 (validation error)
        assert response.status_code in [404, 402, 403], f"Expected 404/402/403 for nonexistent case with valid report_type, got {response.status_code}"
        print(f"PASS: reports/generate accepts extensive_log report type (got {response.status_code})")


class TestExtensiveLogPromptContent:
    """Verify the extensive_log prompt contains the required 25 sections and content"""
    
    def test_extensive_log_prompt_has_25_sections(self):
        """Verify extensive_log prompt has '25. APPENDIX' section"""
        # Read server.py content
        server_path = "/app/backend/server.py"
        with open(server_path, 'r') as f:
            content = f.read()
        
        # Check for 25. APPENDIX section
        assert "## 25. APPENDIX" in content, "Extensive log prompt should contain '## 25. APPENDIX' section"
        print(f"PASS: Extensive log prompt contains '## 25. APPENDIX' section (25 sections)")
    
    def test_extensive_log_prompt_has_word_target(self):
        """Verify extensive_log prompt has 12000-18000 words target"""
        server_path = "/app/backend/server.py"
        with open(server_path, 'r') as f:
            content = f.read()
        
        assert "12000-18000" in content, "Extensive log prompt should specify 12000-18000 words target"
        print(f"PASS: Extensive log prompt contains 12000-18000 words target")
    
    def test_extensive_log_prompt_has_draft_written_submissions(self):
        """Verify extensive_log prompt includes Draft Written Submissions"""
        server_path = "/app/backend/server.py"
        with open(server_path, 'r') as f:
            content = f.read()
        
        assert "DRAFT WRITTEN SUBMISSIONS" in content, "Extensive log prompt should include 'DRAFT WRITTEN SUBMISSIONS'"
        print(f"PASS: Extensive log prompt contains 'DRAFT WRITTEN SUBMISSIONS'")
    
    def test_extensive_log_prompt_has_draft_notice_of_appeal(self):
        """Verify extensive_log prompt includes Draft Notice of Appeal"""
        server_path = "/app/backend/server.py"
        with open(server_path, 'r') as f:
            content = f.read()
        
        assert "DRAFT NOTICE OF APPEAL" in content, "Extensive log prompt should include 'DRAFT NOTICE OF APPEAL'"
        print(f"PASS: Extensive log prompt contains 'DRAFT NOTICE OF APPEAL'")
    
    def test_extensive_log_prompt_has_barrister_case_snapshot(self):
        """Verify extensive_log prompt includes Barrister Case Snapshot section"""
        server_path = "/app/backend/server.py"
        with open(server_path, 'r') as f:
            content = f.read()
        
        # Check for section 2 - BARRISTER CASE SNAPSHOT
        assert "## 2. BARRISTER CASE SNAPSHOT" in content, "Extensive log prompt should include '## 2. BARRISTER CASE SNAPSHOT'"
        print(f"PASS: Extensive log prompt contains '## 2. BARRISTER CASE SNAPSHOT'")
    
    def test_extensive_log_prompt_has_barrister_conference_dossier(self):
        """Verify extensive_log prompt includes Barrister Conference Dossier section"""
        server_path = "/app/backend/server.py"
        with open(server_path, 'r') as f:
            content = f.read()
        
        # Check for section 24 - BARRISTER CONFERENCE DOSSIER
        assert "## 24. BARRISTER CONFERENCE DOSSIER" in content, "Extensive log prompt should include '## 24. BARRISTER CONFERENCE DOSSIER'"
        print(f"PASS: Extensive log prompt contains '## 24. BARRISTER CONFERENCE DOSSIER'")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
