"""
Iteration 162 - Auth Bug Fix Verification Tests
Tests for the P0 bug fix: Removed orphaned setAuthError(null) call from AuthCallback component

This test file verifies:
1. /api/auth/session endpoint returns 401 for invalid session_id (not 500)
2. /api/auth/me endpoint returns 401 when no token provided
3. /api/auth/login endpoint responds correctly for valid/invalid credentials
4. /api/health endpoint is accessible
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Skip all tests if BASE_URL is not set
pytestmark = pytest.mark.skipif(
    not BASE_URL,
    reason="REACT_APP_BACKEND_URL environment variable not set"
)


class TestHealthEndpoint:
    """Health check endpoint tests"""
    
    def test_health_endpoint_returns_200(self):
        """Verify health endpoint is accessible"""
        response = requests.get(f"{BASE_URL}/api/health", timeout=10)
        assert response.status_code == 200
        data = response.json()
        assert data.get("status") == "healthy"
        assert "database" in data
        print(f"✓ Health endpoint returns 200 with status: {data.get('status')}")


class TestAuthSessionEndpoint:
    """Tests for /api/auth/session endpoint - Google OAuth session exchange"""
    
    def test_session_endpoint_returns_401_for_invalid_session_id(self):
        """
        CRITICAL: Verify /api/auth/session returns 401 (not 500) for invalid session_id
        This is the key backend behavior that the frontend AuthCallback relies on
        """
        response = requests.post(
            f"{BASE_URL}/api/auth/session",
            json={"session_id": "invalid_test_session_id_12345"},
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        # Must return 401 Unauthorized, NOT 500 Internal Server Error
        assert response.status_code == 401, f"Expected 401, got {response.status_code}: {response.text}"
        data = response.json()
        assert "detail" in data
        assert "Invalid session_id" in data["detail"]
        print(f"✓ Session endpoint returns 401 for invalid session_id: {data['detail']}")
    
    def test_session_endpoint_returns_400_for_missing_session_id(self):
        """Verify /api/auth/session returns 400 when session_id is missing"""
        response = requests.post(
            f"{BASE_URL}/api/auth/session",
            json={},
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        assert response.status_code == 400, f"Expected 400, got {response.status_code}: {response.text}"
        data = response.json()
        assert "detail" in data
        print(f"✓ Session endpoint returns 400 for missing session_id: {data['detail']}")


class TestAuthMeEndpoint:
    """Tests for /api/auth/me endpoint"""
    
    def test_me_endpoint_returns_401_without_token(self):
        """Verify /api/auth/me returns 401 when no token is provided"""
        response = requests.get(f"{BASE_URL}/api/auth/me", timeout=10)
        assert response.status_code == 401, f"Expected 401, got {response.status_code}: {response.text}"
        data = response.json()
        assert "detail" in data
        print(f"✓ /api/auth/me returns 401 without token: {data['detail']}")
    
    def test_me_endpoint_returns_401_with_invalid_token(self):
        """Verify /api/auth/me returns 401 with invalid Bearer token"""
        response = requests.get(
            f"{BASE_URL}/api/auth/me",
            headers={"Authorization": "Bearer invalid_token_12345"},
            timeout=10
        )
        assert response.status_code == 401, f"Expected 401, got {response.status_code}: {response.text}"
        print("✓ /api/auth/me returns 401 with invalid token")


class TestAuthLoginEndpoint:
    """Tests for /api/auth/login endpoint"""
    
    def test_login_returns_401_for_invalid_credentials(self):
        """Verify /api/auth/login returns 401 for wrong password"""
        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": "djkingy79@gmail.com", "password": "wrong_password"},
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        assert response.status_code == 401, f"Expected 401, got {response.status_code}: {response.text}"
        data = response.json()
        assert "detail" in data
        print(f"✓ Login returns 401 for invalid credentials: {data['detail']}")
    
    def test_login_returns_401_for_nonexistent_user(self):
        """Verify /api/auth/login returns 401 for non-existent email"""
        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": "nonexistent_user_test@example.com", "password": "anypassword"},
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        assert response.status_code == 401, f"Expected 401, got {response.status_code}: {response.text}"
        print("✓ Login returns 401 for non-existent user")


class TestAuthLoginWithValidCredentials:
    """Tests for /api/auth/login with valid credentials"""
    
    def test_login_returns_200_with_valid_credentials(self):
        """Verify /api/auth/login returns 200 and session_token for valid credentials"""
        # Using the admin credentials from test_credentials.md
        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": "djkingy79@gmail.com", "password": "Cr1m1nalApp3al$2025"},
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        
        # Verify response structure
        assert "user_id" in data, "Response missing user_id"
        assert "email" in data, "Response missing email"
        assert "session_token" in data, "Response missing session_token"
        assert data["email"] == "djkingy79@gmail.com"
        assert len(data["session_token"]) > 0
        
        print("✓ Login returns 200 with session_token for valid credentials")
        return data["session_token"]
    
    def test_me_endpoint_works_with_valid_token(self):
        """Verify /api/auth/me returns user data with valid token"""
        # First login to get a token
        login_response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": "djkingy79@gmail.com", "password": "Cr1m1nalApp3al$2025"},
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        assert login_response.status_code == 200
        token = login_response.json()["session_token"]
        
        # Now test /api/auth/me with the token
        me_response = requests.get(
            f"{BASE_URL}/api/auth/me",
            headers={"Authorization": f"Bearer {token}"},
            timeout=10
        )
        assert me_response.status_code == 200, f"Expected 200, got {me_response.status_code}: {me_response.text}"
        data = me_response.json()
        
        # Verify response structure
        assert "user_id" in data
        assert "email" in data
        assert data["email"] == "djkingy79@gmail.com"
        assert "terms_accepted" in data
        assert "is_admin" in data
        
        print(f"✓ /api/auth/me returns user data with valid token (is_admin: {data.get('is_admin')})")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
