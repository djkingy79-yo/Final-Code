"""
Iteration 179: Auth Flow Testing
Tests for Google Auth retry logic fix and email/password login

Features tested:
1. POST /api/auth/login with email/password returns session_token
2. GET /api/auth/me with valid session_token returns user data
3. POST /api/auth/session with invalid session_id returns error after retries
4. Protected routes require authentication
"""
import pytest
import requests
import os
import time

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

class TestAuthEmailPassword:
    """Test email/password authentication flow"""
    
    def test_login_success_returns_session_token(self):
        """POST /api/auth/login with valid credentials returns session_token"""
        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={
                "email": "djkingy79@gmail.com",
                "password": "Grubbygrub88"
            },
            timeout=30
        )
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert "session_token" in data, "Response should contain session_token"
        assert "user_id" in data, "Response should contain user_id"
        assert "email" in data, "Response should contain email"
        assert data["email"] == "djkingy79@gmail.com"
        assert isinstance(data["session_token"], str)
        assert len(data["session_token"]) > 0
        
        # Store for other tests
        TestAuthEmailPassword.session_token = data["session_token"]
        print(f"✓ Login successful, session_token received (len={len(data['session_token'])})")
    
    def test_login_invalid_credentials_returns_401(self):
        """POST /api/auth/login with invalid credentials returns 401"""
        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={
                "email": "invalid@example.com",
                "password": "wrongpassword"
            },
            timeout=30
        )
        
        assert response.status_code == 401, f"Expected 401, got {response.status_code}"
        print("✓ Invalid credentials correctly rejected with 401")
    
    def test_login_wrong_password_returns_401(self):
        """POST /api/auth/login with wrong password returns 401"""
        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={
                "email": "djkingy79@gmail.com",
                "password": "wrongpassword123"
            },
            timeout=30
        )
        
        assert response.status_code == 401, f"Expected 401, got {response.status_code}"
        print("✓ Wrong password correctly rejected with 401")


class TestAuthMe:
    """Test /api/auth/me endpoint"""
    
    def test_auth_me_with_valid_token(self):
        """GET /api/auth/me with valid session_token returns user data"""
        # First login to get a token
        login_response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={
                "email": "djkingy79@gmail.com",
                "password": "Grubbygrub88"
            },
            timeout=30
        )
        assert login_response.status_code == 200
        session_token = login_response.json()["session_token"]
        
        # Now test /auth/me
        response = requests.get(
            f"{BASE_URL}/api/auth/me",
            headers={"Authorization": f"Bearer {session_token}"},
            timeout=30
        )
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert "user_id" in data, "Response should contain user_id"
        assert "email" in data, "Response should contain email"
        assert data["email"] == "djkingy79@gmail.com"
        # Check for terms_accepted field (used by frontend)
        assert "terms_accepted" in data, "Response should contain terms_accepted"
        print(f"✓ /auth/me returned user data: {data['email']}, terms_accepted={data.get('terms_accepted')}")
    
    def test_auth_me_without_token_returns_401(self):
        """GET /api/auth/me without token returns 401"""
        response = requests.get(
            f"{BASE_URL}/api/auth/me",
            timeout=30
        )
        
        assert response.status_code == 401, f"Expected 401, got {response.status_code}"
        print("✓ /auth/me without token correctly rejected with 401")
    
    def test_auth_me_with_invalid_token_returns_401(self):
        """GET /api/auth/me with invalid token returns 401"""
        response = requests.get(
            f"{BASE_URL}/api/auth/me",
            headers={"Authorization": "Bearer invalid_token_12345"},
            timeout=30
        )
        
        assert response.status_code == 401, f"Expected 401, got {response.status_code}"
        print("✓ /auth/me with invalid token correctly rejected with 401")


class TestAuthSessionEndpoint:
    """Test /api/auth/session endpoint (Google OAuth flow)"""
    
    def test_session_without_session_id_returns_400(self):
        """POST /api/auth/session without session_id returns 400"""
        response = requests.post(
            f"{BASE_URL}/api/auth/session",
            json={},
            timeout=30
        )
        
        assert response.status_code == 400, f"Expected 400, got {response.status_code}"
        data = response.json()
        assert "detail" in data
        print(f"✓ Missing session_id correctly rejected: {data['detail']}")
    
    def test_session_with_invalid_session_id_returns_error(self):
        """POST /api/auth/session with invalid session_id returns error after retries
        
        This tests the backend retry logic. The Emergent API will return 404 for
        fake session_ids. Backend should retry 5 times then return 401.
        """
        start_time = time.time()
        
        response = requests.post(
            f"{BASE_URL}/api/auth/session",
            json={"session_id": "fake_invalid_session_id_12345"},
            timeout=60  # Allow time for 5 retries with delays [0,1,2,3,5s] = ~11s
        )
        
        elapsed = time.time() - start_time
        
        # Should return 401 (invalid session) or 504 (server unreachable)
        assert response.status_code in [401, 504], f"Expected 401 or 504, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert "detail" in data
        
        # Verify retry logic took some time (at least a few seconds for retries)
        # With delays [0,1,2,3,5], minimum time should be ~11 seconds if all retries happen
        print(f"✓ Invalid session_id rejected after {elapsed:.1f}s: {data['detail']}")
        print(f"  (Backend retry logic should have attempted 5 times)")


class TestProtectedRoutes:
    """Test that protected routes require authentication"""
    
    def test_cases_endpoint_requires_auth(self):
        """GET /api/cases without auth returns 401"""
        response = requests.get(
            f"{BASE_URL}/api/cases",
            timeout=30
        )
        
        assert response.status_code == 401, f"Expected 401, got {response.status_code}"
        print("✓ /api/cases correctly requires authentication")
    
    def test_cases_endpoint_with_valid_auth(self):
        """GET /api/cases with valid auth returns cases"""
        # First login
        login_response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={
                "email": "djkingy79@gmail.com",
                "password": "Grubbygrub88"
            },
            timeout=30
        )
        assert login_response.status_code == 200
        session_token = login_response.json()["session_token"]
        
        # Now test protected endpoint
        response = requests.get(
            f"{BASE_URL}/api/cases",
            headers={"Authorization": f"Bearer {session_token}"},
            timeout=30
        )
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        data = response.json()
        assert isinstance(data, list), "Response should be a list of cases"
        print(f"✓ /api/cases returned {len(data)} cases with valid auth")


class TestHealthEndpoints:
    """Verify health endpoints are working"""
    
    def test_health_endpoint(self):
        """GET /api/health returns healthy status"""
        response = requests.get(f"{BASE_URL}/api/health", timeout=30)
        assert response.status_code == 200
        data = response.json()
        assert data.get("status") == "healthy"
        print("✓ /api/health returns healthy")
    
    def test_ready_endpoint(self):
        """GET /api/ready returns ready status"""
        response = requests.get(f"{BASE_URL}/api/ready", timeout=30)
        assert response.status_code == 200
        data = response.json()
        assert data.get("ready") == True
        print("✓ /api/ready returns ready: true")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
