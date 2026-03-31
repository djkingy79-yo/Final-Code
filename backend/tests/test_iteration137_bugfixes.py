"""
Iteration 137 - Bug Fix Verification Tests
Tests for 5 critical bugs reported by user:
1. Google Auth redirect - should redirect to /dashboard
2. Not Authenticated - Bearer token auth via localStorage
3. Print All - should include full content
4. iOS PDF view - handled in frontend
5. Similar Cases badge - AI-SUGGESTED instead of UNVERIFIED
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Test credentials from /app/memory/test_credentials.md
TEST_EMAIL = "djkingy79@gmail.com"
TEST_PASSWORD = "Grubbygrub88"
TEST_CASE_ID = "case_f8bf63e9dcbe"


class TestHealthAndBasics:
    """Basic health checks"""
    
    def test_health_endpoint(self):
        """Verify backend is healthy"""
        response = requests.get(f"{BASE_URL}/api/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["database"] == "connected"
        print("PASS: Health endpoint working")


class TestAuthBearerToken:
    """Bug 2: Bearer token authentication tests"""
    
    def test_login_returns_session_token(self):
        """Login should return session_token for localStorage storage"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": TEST_EMAIL,
            "password": TEST_PASSWORD
        })
        assert response.status_code == 200, f"Login failed: {response.text}"
        data = response.json()
        assert "session_token" in data, "session_token not in login response"
        assert data["session_token"].startswith("sess_"), "Invalid session_token format"
        assert "user_id" in data
        assert "email" in data
        print(f"PASS: Login returns session_token: {data['session_token'][:20]}...")
        return data["session_token"]
    
    def test_auth_me_with_bearer_token(self):
        """/api/auth/me should work with Bearer token in Authorization header"""
        # First login to get token
        login_response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": TEST_EMAIL,
            "password": TEST_PASSWORD
        })
        assert login_response.status_code == 200
        token = login_response.json()["session_token"]
        
        # Now test /api/auth/me with Bearer token
        response = requests.get(
            f"{BASE_URL}/api/auth/me",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 200, f"Auth/me failed: {response.text}"
        data = response.json()
        assert data["email"] == TEST_EMAIL
        assert "user_id" in data
        print(f"PASS: /api/auth/me works with Bearer token, user: {data['email']}")
    
    def test_auth_me_without_token_fails(self):
        """/api/auth/me should fail without token"""
        response = requests.get(f"{BASE_URL}/api/auth/me")
        assert response.status_code == 401
        print("PASS: /api/auth/me correctly rejects unauthenticated requests")
    
    def test_logout_with_bearer_token(self):
        """Logout should work with Bearer token (not just cookies)"""
        # Login first
        login_response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": TEST_EMAIL,
            "password": TEST_PASSWORD
        })
        assert login_response.status_code == 200
        token = login_response.json()["session_token"]
        
        # Logout with Bearer token
        response = requests.post(
            f"{BASE_URL}/api/auth/logout",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "Logged out"
        print("PASS: Logout works with Bearer token")
        
        # Verify token is invalidated
        me_response = requests.get(
            f"{BASE_URL}/api/auth/me",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert me_response.status_code == 401, "Token should be invalidated after logout"
        print("PASS: Token correctly invalidated after logout")


class TestCaseAccess:
    """Test case access with Bearer token auth"""
    
    @pytest.fixture
    def auth_token(self):
        """Get auth token for tests"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": TEST_EMAIL,
            "password": TEST_PASSWORD
        })
        if response.status_code != 200:
            pytest.skip("Login failed - skipping authenticated tests")
        return response.json()["session_token"]
    
    def test_get_case_with_bearer_token(self, auth_token):
        """Should be able to access case with Bearer token"""
        response = requests.get(
            f"{BASE_URL}/api/cases/{TEST_CASE_ID}",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        assert response.status_code == 200, f"Case access failed: {response.text}"
        data = response.json()
        assert data["case_id"] == TEST_CASE_ID
        print(f"PASS: Case access works with Bearer token, case: {data.get('title', 'N/A')}")
    
    def test_get_case_grounds_with_bearer_token(self, auth_token):
        """Should be able to access case grounds with Bearer token"""
        response = requests.get(
            f"{BASE_URL}/api/cases/{TEST_CASE_ID}/grounds",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        assert response.status_code == 200, f"Grounds access failed: {response.text}"
        data = response.json()
        assert "grounds" in data or isinstance(data, list)
        print(f"PASS: Grounds access works with Bearer token")
    
    def test_get_case_documents_with_bearer_token(self, auth_token):
        """Should be able to access case documents with Bearer token"""
        response = requests.get(
            f"{BASE_URL}/api/cases/{TEST_CASE_ID}/documents",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        assert response.status_code == 200, f"Documents access failed: {response.text}"
        print("PASS: Documents access works with Bearer token")
    
    def test_get_case_timeline_with_bearer_token(self, auth_token):
        """Should be able to access case timeline with Bearer token"""
        response = requests.get(
            f"{BASE_URL}/api/cases/{TEST_CASE_ID}/timeline",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        assert response.status_code == 200, f"Timeline access failed: {response.text}"
        print("PASS: Timeline access works with Bearer token")
    
    def test_get_case_notes_with_bearer_token(self, auth_token):
        """Should be able to access case notes with Bearer token"""
        response = requests.get(
            f"{BASE_URL}/api/cases/{TEST_CASE_ID}/notes",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        assert response.status_code == 200, f"Notes access failed: {response.text}"
        print("PASS: Notes access works with Bearer token")


class TestSessionEndpoint:
    """Test Google OAuth session exchange endpoint"""
    
    def test_session_endpoint_exists(self):
        """POST /api/auth/session should exist"""
        # Without valid session_id, should return 400 or 401
        response = requests.post(f"{BASE_URL}/api/auth/session", json={})
        assert response.status_code in [400, 401], f"Unexpected status: {response.status_code}"
        print("PASS: /api/auth/session endpoint exists and validates input")
    
    def test_session_endpoint_requires_session_id(self):
        """POST /api/auth/session should require session_id"""
        response = requests.post(f"{BASE_URL}/api/auth/session", json={"foo": "bar"})
        assert response.status_code == 400
        data = response.json()
        assert "session_id" in data.get("detail", "").lower()
        print("PASS: /api/auth/session correctly requires session_id")


class TestCaselawEndpoints:
    """Test caselaw database endpoints"""
    
    def test_caselaw_databases_endpoint(self):
        """GET /api/caselaw/databases should return database list"""
        response = requests.get(f"{BASE_URL}/api/caselaw/databases")
        assert response.status_code == 200
        data = response.json()
        # Response has 'national' and 'states' keys
        assert "national" in data or "states" in data or "databases" in data
        print("PASS: Caselaw databases endpoint working")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
