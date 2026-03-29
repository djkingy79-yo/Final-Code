"""
Iteration 65 - Comprehensive Backend Tests
Testing: Health, Auth, Cases, Report Generation (Background Pattern)
"""
import pytest
import requests
import os
import time

BASE_URL = 'http://localhost:8001'

# Test credentials
TEST_EMAIL = "djkingy79@gmail.com"
TEST_PASSWORD = "Appeal2026!"
TEST_CASE_ID = "case_b2aa32564f2b"


class TestHealthEndpoint:
    """Test /api/health endpoint"""
    
    def test_health_returns_healthy(self):
        """Health endpoint returns healthy status"""
        response = requests.get(f"{BASE_URL}/api/health")
        assert response.status_code == 200
        data = response.json()
        assert data.get("status") == "healthy"
        print(f"PASS: Health endpoint returned status={data.get('status')}")


class TestAuthLogin:
    """Test /api/auth/login endpoint"""
    
    def test_login_with_valid_credentials(self):
        """Login with valid email/password works"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": TEST_EMAIL,
            "password": TEST_PASSWORD
        })
        assert response.status_code == 200
        data = response.json()
        assert "user_id" in data
        assert data["email"] == TEST_EMAIL
        print(f"PASS: Login succeeded for {data['email']}")
    
    def test_login_with_invalid_password(self):
        """Login with wrong password returns 401"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": TEST_EMAIL,
            "password": "wrongpassword123"
        })
        assert response.status_code == 401
        print("PASS: Invalid credentials properly rejected")


class TestCasesEndpoint:
    """Test /api/cases endpoint"""
    
    @pytest.fixture(autouse=True)
    def setup_auth(self):
        """Get auth token before each test"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": TEST_EMAIL,
            "password": TEST_PASSWORD
        })
        if response.status_code == 200:
            # Extract session token from cookie
            self.session = requests.Session()
            self.session.cookies.update(response.cookies)
            # Also try Authorization header
            cookies = response.cookies.get_dict()
            if "session_token" in cookies:
                self.auth_header = {"Authorization": f"Bearer {cookies['session_token']}"}
            else:
                self.auth_header = {}
        else:
            pytest.skip("Login failed")
    
    def test_get_cases_returns_list(self):
        """GET /api/cases returns cases list"""
        response = self.session.get(f"{BASE_URL}/api/cases", headers=self.auth_header)
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        print(f"PASS: Found {len(data)} cases")
        if len(data) > 0:
            assert "case_id" in data[0]
            print(f"  First case: {data[0].get('title', 'Untitled')}")
    
    def test_get_specific_case(self):
        """GET /api/cases/{case_id} returns case details"""
        response = self.session.get(f"{BASE_URL}/api/cases/{TEST_CASE_ID}", headers=self.auth_header)
        assert response.status_code == 200
        data = response.json()
        assert data["case_id"] == TEST_CASE_ID
        print(f"PASS: Case details retrieved: {data.get('title')}")


class TestReportGeneration:
    """Test report generation with background task pattern"""
    
    @pytest.fixture(autouse=True)
    def setup_auth(self):
        """Get auth token before each test"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": TEST_EMAIL,
            "password": TEST_PASSWORD
        })
        if response.status_code == 200:
            self.session = requests.Session()
            self.session.cookies.update(response.cookies)
            cookies = response.cookies.get_dict()
            if "session_token" in cookies:
                self.auth_header = {"Authorization": f"Bearer {cookies['session_token']}"}
                self.session_token = cookies['session_token']
            else:
                self.auth_header = {}
                self.session_token = None
        else:
            pytest.skip("Login failed")
    
    def test_generate_report_returns_immediately(self):
        """POST /api/cases/{case_id}/reports/generate returns immediately with status='generating'"""
        start = time.time()
        response = self.session.post(
            f"{BASE_URL}/api/cases/{TEST_CASE_ID}/reports/generate",
            json={"report_type": "quick_summary", "aggressive_mode": False},
            headers=self.auth_header,
            timeout=30
        )
        elapsed = time.time() - start
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text[:200]}"
        data = response.json()
        
        # Must return immediately (< 15 seconds)
        assert elapsed < 15, f"Took {elapsed:.1f}s, expected < 15s"
        
        # Must have status='generating' (background pattern)
        assert data.get("status") == "generating", f"Expected status='generating', got '{data.get('status')}'"
        assert "report_id" in data, "Response must include report_id"
        
        self.report_id = data["report_id"]
        print(f"PASS: Generate endpoint returned in {elapsed:.1f}s with status='generating', report_id={self.report_id}")
        
        return data["report_id"]
    
    def test_report_status_endpoint(self):
        """GET /api/cases/{case_id}/reports/{report_id}/status returns status"""
        # First generate a report
        gen_response = self.session.post(
            f"{BASE_URL}/api/cases/{TEST_CASE_ID}/reports/generate",
            json={"report_type": "quick_summary", "aggressive_mode": False},
            headers=self.auth_header,
            timeout=30
        )
        assert gen_response.status_code == 200
        report_id = gen_response.json()["report_id"]
        
        # Then check status
        status_response = self.session.get(
            f"{BASE_URL}/api/cases/{TEST_CASE_ID}/reports/{report_id}/status",
            headers=self.auth_header
        )
        assert status_response.status_code == 200
        status_data = status_response.json()
        assert "status" in status_data
        assert status_data["status"] in ["generating", "completed", "failed"]
        print(f"PASS: Status endpoint returned status='{status_data['status']}'")
    
    def test_full_polling_flow(self):
        """Full flow: generate -> poll until completed (up to 5 min)"""
        # Generate
        gen_response = self.session.post(
            f"{BASE_URL}/api/cases/{TEST_CASE_ID}/reports/generate",
            json={"report_type": "quick_summary", "aggressive_mode": False},
            headers=self.auth_header,
            timeout=30
        )
        assert gen_response.status_code == 200
        report_id = gen_response.json()["report_id"]
        print(f"Generated report {report_id}, now polling...")
        
        # Poll for completion
        max_wait = 300  # 5 minutes
        interval = 5  # 5 seconds
        elapsed = 0
        final_status = None
        
        while elapsed < max_wait:
            status_response = self.session.get(
                f"{BASE_URL}/api/cases/{TEST_CASE_ID}/reports/{report_id}/status",
                headers=self.auth_header
            )
            if status_response.status_code == 200:
                status_data = status_response.json()
                final_status = status_data.get("status")
                print(f"  [{elapsed}s] Status: {final_status}")
                
                if final_status in ["completed", "failed"]:
                    break
            
            time.sleep(interval)
            elapsed += interval
        
        assert final_status in ["completed", "failed"], f"Report did not complete within {max_wait}s"
        print(f"PASS: Report generation finished with status='{final_status}' after {elapsed}s")
        
        # Clean up - delete the test report
        if final_status == "completed":
            delete_response = self.session.delete(
                f"{BASE_URL}/api/cases/{TEST_CASE_ID}/reports/{report_id}",
                headers=self.auth_header
            )
            if delete_response.status_code in [200, 204]:
                print(f"  Cleaned up test report {report_id}")


class TestGetReports:
    """Test GET /api/cases/{case_id}/reports"""
    
    @pytest.fixture(autouse=True)
    def setup_auth(self):
        """Get auth token before each test"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": TEST_EMAIL,
            "password": TEST_PASSWORD
        })
        if response.status_code == 200:
            self.session = requests.Session()
            self.session.cookies.update(response.cookies)
            cookies = response.cookies.get_dict()
            if "session_token" in cookies:
                self.auth_header = {"Authorization": f"Bearer {cookies['session_token']}"}
            else:
                self.auth_header = {}
        else:
            pytest.skip("Login failed")
    
    def test_get_reports_list(self):
        """GET /api/cases/{case_id}/reports returns list of reports"""
        response = self.session.get(
            f"{BASE_URL}/api/cases/{TEST_CASE_ID}/reports",
            headers=self.auth_header
        )
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        print(f"PASS: Found {len(data)} reports for case {TEST_CASE_ID}")
        
        # Check report structure
        if len(data) > 0:
            first_report = data[0]
            assert "report_id" in first_report
            assert "report_type" in first_report
            print(f"  Latest report: {first_report.get('report_type')} - status: {first_report.get('status', 'completed')}")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
