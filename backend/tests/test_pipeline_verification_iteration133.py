"""
Iteration 133: Pipeline Verification UI Backend Tests
Tests for verify-batch endpoint and reports regression
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Test credentials
TEST_EMAIL = "test@example.com"
TEST_PASSWORD = "TestPassword123!"
TEST_CASE_ID = "case_a97ea91f0692"  # Dummy Murder Appeal


class TestAuth:
    """Authentication tests"""
    
    @pytest.fixture(scope="class")
    def session(self):
        return requests.Session()
    
    def test_login_returns_session_token(self, session):
        """Login should return session_token"""
        response = session.post(f"{BASE_URL}/api/auth/login", json={
            "email": TEST_EMAIL,
            "password": TEST_PASSWORD
        }, timeout=30)
        assert response.status_code == 200, f"Login failed: {response.text}"
        data = response.json()
        assert "session_token" in data, f"No session_token in response: {data}"
        assert len(data["session_token"]) > 0
        print("Login successful, got session_token")


class TestVerifyBatchEndpoint:
    """Tests for POST /api/cases/{case_id}/issues/verify-batch"""
    
    @pytest.fixture(scope="class")
    def auth_session(self):
        session = requests.Session()
        response = session.post(f"{BASE_URL}/api/auth/login", json={
            "email": TEST_EMAIL,
            "password": TEST_PASSWORD
        }, timeout=30)
        assert response.status_code == 200
        token = response.json().get("session_token")
        session.headers.update({"Authorization": f"Bearer {token}"})
        return session
    
    def test_verify_batch_with_limit_3(self, auth_session):
        """POST /api/cases/{case_id}/issues/verify-batch with limit=3 should return verification result"""
        response = auth_session.post(
            f"{BASE_URL}/api/cases/{TEST_CASE_ID}/issues/verify-batch",
            json={"limit": 3},
            timeout=300  # Long timeout for LLM calls
        )
        # Accept 200 (success) or 400 (no issues to verify - which is valid)
        assert response.status_code in [200, 400], f"Unexpected status: {response.status_code}, {response.text}"
        
        if response.status_code == 200:
            data = response.json()
            # Verify expected fields in response
            assert "eligible_issues" in data, f"Missing eligible_issues: {data}"
            assert "attempted" in data, f"Missing attempted: {data}"
            assert "verified" in data, f"Missing verified: {data}"
            assert "failed" in data, f"Missing failed: {data}"
            assert "synced_count" in data, f"Missing synced_count: {data}"
            assert "message" in data, f"Missing message: {data}"
            print(f"verify-batch response: eligible={data['eligible_issues']}, attempted={data['attempted']}, verified={data['verified']}, failed={data['failed']}, synced={data['synced_count']}")
        else:
            # 400 means no issues to verify - still valid
            data = response.json()
            print(f"verify-batch returned 400 (expected if no issues): {data}")
    
    def test_verify_batch_with_limit_6(self, auth_session):
        """POST /api/cases/{case_id}/issues/verify-batch with limit=6 should return verification result"""
        response = auth_session.post(
            f"{BASE_URL}/api/cases/{TEST_CASE_ID}/issues/verify-batch",
            json={"limit": 6},
            timeout=300
        )
        assert response.status_code in [200, 400], f"Unexpected status: {response.status_code}, {response.text}"
        
        if response.status_code == 200:
            data = response.json()
            assert "applied_limit" in data, f"Missing applied_limit: {data}"
            # applied_limit should be capped at 6 or less
            assert data["applied_limit"] <= 6, f"applied_limit should be <= 6: {data}"
            print(f"verify-batch limit=6 response: applied_limit={data['applied_limit']}")
    
    def test_verify_batch_unauthorized(self):
        """POST /api/cases/{case_id}/issues/verify-batch without auth should fail"""
        session = requests.Session()
        response = session.post(
            f"{BASE_URL}/api/cases/{TEST_CASE_ID}/issues/verify-batch",
            json={"limit": 3},
            timeout=30
        )
        assert response.status_code == 401, f"Expected 401, got {response.status_code}"
    
    def test_verify_batch_case_not_found(self, auth_session):
        """POST /api/cases/{invalid_case}/issues/verify-batch should return 404"""
        response = auth_session.post(
            f"{BASE_URL}/api/cases/invalid_case_xyz/issues/verify-batch",
            json={"limit": 3},
            timeout=30
        )
        assert response.status_code == 404, f"Expected 404, got {response.status_code}"


class TestReportsRegression:
    """Regression tests for reports endpoints"""
    
    @pytest.fixture(scope="class")
    def auth_session(self):
        session = requests.Session()
        response = session.post(f"{BASE_URL}/api/auth/login", json={
            "email": TEST_EMAIL,
            "password": TEST_PASSWORD
        }, timeout=30)
        assert response.status_code == 200
        token = response.json().get("session_token")
        session.headers.update({"Authorization": f"Bearer {token}"})
        return session
    
    def test_get_reports_list(self, auth_session):
        """GET /api/cases/{case_id}/reports should return list of reports"""
        response = auth_session.get(
            f"{BASE_URL}/api/cases/{TEST_CASE_ID}/reports",
            timeout=30
        )
        assert response.status_code == 200, f"Failed to get reports: {response.text}"
        data = response.json()
        assert isinstance(data, list), f"Expected list, got {type(data)}"
        print(f"GET reports returned {len(data)} reports")
        
        # If reports exist, verify structure
        if len(data) > 0:
            report = data[0]
            assert "report_id" in report, f"Missing report_id: {report}"
            assert "report_type" in report, f"Missing report_type: {report}"
            assert "status" in report, f"Missing status: {report}"
    
    def test_generate_quick_summary_report(self, auth_session):
        """POST /api/cases/{case_id}/reports/generate with quick_summary should work"""
        response = auth_session.post(
            f"{BASE_URL}/api/cases/{TEST_CASE_ID}/reports/generate",
            json={"report_type": "quick_summary"},
            timeout=120  # Long timeout for report generation
        )
        # Accept 200 (success), 202 (accepted/generating), or 400 (already exists)
        assert response.status_code in [200, 202, 400], f"Unexpected status: {response.status_code}, {response.text}"
        
        if response.status_code in [200, 202]:
            data = response.json()
            # Should have report_id and status
            assert "report_id" in data or "status" in data, f"Missing report_id or status: {data}"
            print(f"Generate report response: {data}")
        else:
            # 400 might mean report already exists or other validation error
            print(f"Generate report returned 400: {response.json()}")
    
    def test_get_reports_unauthorized(self):
        """GET /api/cases/{case_id}/reports without auth should fail"""
        session = requests.Session()
        response = session.get(
            f"{BASE_URL}/api/cases/{TEST_CASE_ID}/reports",
            timeout=30
        )
        assert response.status_code == 401, f"Expected 401, got {response.status_code}"


class TestHealthCheck:
    """Health check regression"""
    
    def test_health_endpoint(self):
        """GET /api/health should return healthy"""
        response = requests.get(f"{BASE_URL}/api/health", timeout=10)
        assert response.status_code == 200, f"Health check failed: {response.text}"
        data = response.json()
        assert data.get("status") == "healthy", f"Unexpected health status: {data}"
        print("Health check passed")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
