"""
Auth CORS Fix Tests - Iteration 115
Tests for email/password login, registration, Bearer token auth, and session management.
Focus: Verify CORS fix (withCredentials removed, Bearer token auth works)
"""
import pytest
import requests
import os
import uuid

BASE_URL = 'http://localhost:8001'

# Test credentials from /app/memory/test_credentials.md
TEST_EMAIL = "test@example.com"
TEST_PASSWORD = "TestPassword123!"

# Unique test user for registration tests
TEST_UNIQUE_EMAIL = f"test_user_{uuid.uuid4().hex[:8]}@example.com"
TEST_UNIQUE_PASSWORD = "TestPass123"
TEST_UNIQUE_NAME = "Test User"


class TestHealthCheck:
    """Verify backend is running"""
    
    def test_health_endpoint(self):
        response = requests.get(f"{BASE_URL}/api/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["database"] == "connected"
        print(f"✓ Health check passed: {data}")


class TestEmailPasswordLogin:
    """Test email/password login flow - the main fix being tested"""
    
    def test_login_returns_session_token(self):
        """POST /api/auth/login should return session_token in response body"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": TEST_EMAIL,
            "password": TEST_PASSWORD
        })
        
        assert response.status_code == 200, f"Login failed: {response.text}"
        data = response.json()
        
        # Verify session_token is in response body (critical for Bearer auth)
        assert "session_token" in data, "session_token missing from login response"
        assert data["session_token"].startswith("sess_"), f"Invalid token format: {data['session_token']}"
        
        # Verify user data is returned
        assert "user_id" in data
        assert "email" in data
        assert data["email"] == TEST_EMAIL.lower()
        
        print(f"✓ Login successful, session_token: {data['session_token'][:20]}...")
        return data["session_token"]
    
    def test_login_invalid_credentials(self):
        """Login with wrong password should return 401"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": TEST_EMAIL,
            "password": "wrongpassword"
        })
        
        assert response.status_code == 401
        data = response.json()
        assert "detail" in data
        print(f"✓ Invalid credentials correctly rejected: {data['detail']}")
    
    def test_login_nonexistent_user(self):
        """Login with non-existent email should return 401"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": "nonexistent@example.com",
            "password": "anypassword"
        })
        
        assert response.status_code == 401
        print("✓ Non-existent user correctly rejected")


class TestBearerTokenAuth:
    """Test Bearer token authentication - the core of the CORS fix"""
    
    @pytest.fixture
    def auth_token(self):
        """Get a valid session token"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": TEST_EMAIL,
            "password": TEST_PASSWORD
        })
        assert response.status_code == 200
        return response.json()["session_token"]
    
    def test_auth_me_with_bearer_token(self, auth_token):
        """GET /api/auth/me with Authorization: Bearer token should return user data"""
        response = requests.get(
            f"{BASE_URL}/api/auth/me",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        
        assert response.status_code == 200, f"Auth/me failed: {response.text}"
        data = response.json()
        
        # Verify user data
        assert "user_id" in data
        assert "email" in data
        assert data["email"] == TEST_EMAIL.lower()
        
        print(f"✓ Bearer token auth works, user: {data['email']}")
    
    def test_auth_me_without_token(self):
        """GET /api/auth/me without token should return 401"""
        response = requests.get(f"{BASE_URL}/api/auth/me")
        
        assert response.status_code == 401
        print("✓ Unauthenticated request correctly rejected")
    
    def test_auth_me_with_invalid_token(self):
        """GET /api/auth/me with invalid token should return 401"""
        response = requests.get(
            f"{BASE_URL}/api/auth/me",
            headers={"Authorization": "Bearer invalid_token_12345"}
        )
        
        assert response.status_code == 401
        print("✓ Invalid token correctly rejected")


class TestRegistration:
    """Test user registration flow"""
    
    def test_register_returns_session_token(self):
        """POST /api/auth/register should return session_token in response body"""
        unique_email = f"test_reg_{uuid.uuid4().hex[:8]}@example.com"
        
        response = requests.post(f"{BASE_URL}/api/auth/register", json={
            "email": unique_email,
            "password": TEST_UNIQUE_PASSWORD,
            "name": TEST_UNIQUE_NAME
        })
        
        assert response.status_code == 200, f"Registration failed: {response.text}"
        data = response.json()
        
        # Verify session_token is in response body
        assert "session_token" in data, "session_token missing from register response"
        assert data["session_token"].startswith("sess_"), f"Invalid token format: {data['session_token']}"
        
        # Verify user data
        assert "user_id" in data
        assert "email" in data
        assert data["email"] == unique_email.lower()
        assert "name" in data
        assert data["name"] == TEST_UNIQUE_NAME
        
        print(f"✓ Registration successful, session_token: {data['session_token'][:20]}...")
        
        # Verify the token works for auth/me
        me_response = requests.get(
            f"{BASE_URL}/api/auth/me",
            headers={"Authorization": f"Bearer {data['session_token']}"}
        )
        assert me_response.status_code == 200
        print("✓ New user's token works for auth/me")
    
    def test_register_duplicate_email(self):
        """Registration with existing email should fail"""
        response = requests.post(f"{BASE_URL}/api/auth/register", json={
            "email": TEST_EMAIL,  # Already exists
            "password": "anypassword",
            "name": "Test User"
        })
        
        assert response.status_code == 400
        data = response.json()
        assert "already registered" in data["detail"].lower() or "already" in data["detail"].lower()
        print(f"✓ Duplicate email correctly rejected: {data['detail']}")
    
    def test_register_weak_password(self):
        """Registration with weak password should fail"""
        response = requests.post(f"{BASE_URL}/api/auth/register", json={
            "email": f"test_{uuid.uuid4().hex[:8]}@example.com",
            "password": "123",  # Too short
            "name": "Test User"
        })
        
        assert response.status_code == 400
        data = response.json()
        assert "6 characters" in data["detail"]
        print(f"✓ Weak password correctly rejected: {data['detail']}")


class TestLogout:
    """Test logout flow"""
    
    def test_logout_endpoint(self):
        """POST /api/auth/logout should work"""
        # First login to get a session
        login_response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": TEST_EMAIL,
            "password": TEST_PASSWORD
        })
        assert login_response.status_code == 200
        token = login_response.json()["session_token"]
        
        # Logout
        logout_response = requests.post(
            f"{BASE_URL}/api/auth/logout",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert logout_response.status_code == 200
        data = logout_response.json()
        assert "message" in data
        print(f"✓ Logout successful: {data['message']}")


class TestGoogleOAuthSession:
    """Test Google OAuth session endpoint (can't fully test without real Google auth)"""
    
    def test_session_endpoint_requires_session_id(self):
        """POST /api/auth/session without session_id should fail"""
        response = requests.post(f"{BASE_URL}/api/auth/session", json={})
        
        assert response.status_code == 400
        data = response.json()
        assert "session_id" in data["detail"].lower()
        print(f"✓ Session endpoint correctly requires session_id: {data['detail']}")
    
    def test_session_endpoint_invalid_session_id(self):
        """POST /api/auth/session with invalid session_id should fail"""
        response = requests.post(f"{BASE_URL}/api/auth/session", json={
            "session_id": "invalid_session_id_12345"
        })
        
        assert response.status_code == 401
        print("✓ Invalid session_id correctly rejected")


class TestProtectedEndpoints:
    """Test that protected endpoints work with Bearer token"""
    
    @pytest.fixture
    def auth_token(self):
        """Get a valid session token"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": TEST_EMAIL,
            "password": TEST_PASSWORD
        })
        assert response.status_code == 200
        return response.json()["session_token"]
    
    def test_cases_endpoint_with_bearer(self, auth_token):
        """GET /api/cases should work with Bearer token"""
        response = requests.get(
            f"{BASE_URL}/api/cases",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        print(f"✓ Cases endpoint works with Bearer token, found {len(data)} cases")
    
    def test_cases_endpoint_without_auth(self):
        """GET /api/cases without auth should fail"""
        response = requests.get(f"{BASE_URL}/api/cases")
        
        assert response.status_code == 401
        print("✓ Cases endpoint correctly requires auth")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
