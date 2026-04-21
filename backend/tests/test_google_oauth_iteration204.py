"""
Test Google OAuth Direct Integration (iteration 204)
Tests:
1. POST /api/auth/google/callback - error handling (400 for missing code, 401 for invalid code)
2. Config loads GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET from env
3. POST /api/auth/session (Emergent fallback) still works
4. Regression: GET /api/auth/me works with session_token
5. Regression: POST /api/auth/login works
6. Regression: POST /api/auth/register works
"""
import pytest
import requests
import os
import uuid

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', "http://localhost:8001").rstrip('/')

# Test credentials from /app/memory/test_credentials.md
TEST_EMAIL = "djkingy79@gmail.com"
TEST_PASSWORD = "Grubbygrub88"


class TestGoogleOAuthCallback:
    """Tests for POST /api/auth/google/callback endpoint"""
    
    def test_google_callback_missing_code_returns_400(self):
        """POST /api/auth/google/callback with empty body → 400"""
        response = requests.post(
            f"{BASE_URL}/api/auth/google/callback",
            json={},
            headers={"Content-Type": "application/json"}
        )
        assert response.status_code == 400, f"Expected 400, got {response.status_code}: {response.text}"
        data = response.json()
        assert "code and redirect_uri required" in data.get("detail", ""), f"Unexpected error: {data}"
    
    def test_google_callback_missing_redirect_uri_returns_400(self):
        """POST /api/auth/google/callback with code but no redirect_uri → 400"""
        response = requests.post(
            f"{BASE_URL}/api/auth/google/callback",
            json={"code": "fake_code"},
            headers={"Content-Type": "application/json"}
        )
        assert response.status_code == 400, f"Expected 400, got {response.status_code}: {response.text}"
        data = response.json()
        assert "code and redirect_uri required" in data.get("detail", ""), f"Unexpected error: {data}"
    
    def test_google_callback_invalid_code_returns_401(self):
        """POST /api/auth/google/callback with fake code → 401"""
        response = requests.post(
            f"{BASE_URL}/api/auth/google/callback",
            json={"code": "fake_invalid_code", "redirect_uri": "https://example.com/callback"},
            headers={"Content-Type": "application/json"}
        )
        assert response.status_code == 401, f"Expected 401, got {response.status_code}: {response.text}"
        data = response.json()
        # Response message improved 2026-04-21 to surface the real Google
        # OAuth error reason (`invalid_grant` / `redirect_uri_mismatch` /
        # `invalid_client`) rather than a generic "Invalid or expired
        # authorization code". Either old or new wording is acceptable here.
        detail = data.get("detail", "")
        assert (
            "Invalid or expired authorization code" in detail
            or "Google rejected the sign-in" in detail
        ), f"Unexpected error: {data}"


class TestEmergentSessionFallback:
    """Tests for POST /api/auth/session (Emergent fallback) - kept for backwards compat"""
    
    def test_session_endpoint_exists_and_requires_session_id(self):
        """POST /api/auth/session is now permanently retired (HTTP 410)
        since the Emergent-hosted auth fallback was removed 2026-02-21.
        Endpoint must still return a deterministic non-500 status."""
        response = requests.post(
            f"{BASE_URL}/api/auth/session",
            json={},
            headers={"Content-Type": "application/json"}
        )
        # 400 kept for pre-migration clients; 410 returned after flow retired.
        assert response.status_code in (400, 410), f"Expected 400 or 410, got {response.status_code}: {response.text}"
        data = response.json()
        detail = data.get("detail", "")
        assert (
            "session_id required" in detail
            or "retired" in detail.lower()
        ), f"Unexpected error: {data}"
    
    def test_session_endpoint_invalid_session_id_returns_401_or_504(self):
        """POST /api/auth/session with invalid session_id → 401 / 504 / 410"""
        response = requests.post(
            f"{BASE_URL}/api/auth/session",
            json={"session_id": "invalid_session_id_12345"},
            headers={"Content-Type": "application/json"},
            timeout=30  # Emergent has retry delays
        )
        # 401 = invalid session; 504 = Emergent unreachable;
        # 410 = endpoint permanently retired after 2026-02-21.
        assert response.status_code in (401, 410, 504), f"Expected 401/410/504, got {response.status_code}: {response.text}"


class TestEmailPasswordLogin:
    """Regression tests for POST /api/auth/login"""
    
    def test_login_success(self):
        """POST /api/auth/login with valid credentials → 200"""
        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": TEST_EMAIL, "password": TEST_PASSWORD},
            headers={"Content-Type": "application/json"}
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        assert "session_token" in data, f"Missing session_token in response: {data}"
        assert "user_id" in data, f"Missing user_id in response: {data}"
        assert data.get("email") == TEST_EMAIL.lower(), f"Email mismatch: {data}"
    
    def test_login_invalid_password_returns_401(self):
        """POST /api/auth/login with wrong password → 401"""
        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": TEST_EMAIL, "password": "wrong_password_123"},
            headers={"Content-Type": "application/json"}
        )
        assert response.status_code == 401, f"Expected 401, got {response.status_code}: {response.text}"
        data = response.json()
        assert "Invalid email or password" in data.get("detail", ""), f"Unexpected error: {data}"
    
    def test_login_nonexistent_user_returns_401(self):
        """POST /api/auth/login with non-existent email → 401"""
        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": "nonexistent_user_12345@example.com", "password": "any_password"},
            headers={"Content-Type": "application/json"}
        )
        assert response.status_code == 401, f"Expected 401, got {response.status_code}: {response.text}"


class TestEmailPasswordRegister:
    """Regression tests for POST /api/auth/register"""
    
    def test_register_new_user_success(self):
        """POST /api/auth/register with new email → 200"""
        unique_email = f"TEST_user_{uuid.uuid4().hex[:8]}@example.com"
        response = requests.post(
            f"{BASE_URL}/api/auth/register",
            json={
                "email": unique_email,
                "password": "TestPass123",
                "name": "Test User"
            },
            headers={"Content-Type": "application/json"}
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        assert "session_token" in data, f"Missing session_token in response: {data}"
        assert "user_id" in data, f"Missing user_id in response: {data}"
        assert data.get("email") == unique_email.lower(), f"Email mismatch: {data}"
    
    def test_register_duplicate_email_returns_400(self):
        """POST /api/auth/register with existing email → 400"""
        response = requests.post(
            f"{BASE_URL}/api/auth/register",
            json={
                "email": TEST_EMAIL,
                "password": "TestPass123",
                "name": "Duplicate User"
            },
            headers={"Content-Type": "application/json"}
        )
        assert response.status_code == 400, f"Expected 400, got {response.status_code}: {response.text}"
        data = response.json()
        assert "already registered" in data.get("detail", "").lower(), f"Unexpected error: {data}"
    
    def test_register_weak_password_returns_400(self):
        """POST /api/auth/register with weak password → 400"""
        unique_email = f"TEST_weak_{uuid.uuid4().hex[:8]}@example.com"
        response = requests.post(
            f"{BASE_URL}/api/auth/register",
            json={
                "email": unique_email,
                "password": "short",  # Too short
                "name": "Weak Password User"
            },
            headers={"Content-Type": "application/json"}
        )
        assert response.status_code == 400, f"Expected 400, got {response.status_code}: {response.text}"
        data = response.json()
        assert "at least 8 characters" in data.get("detail", "").lower(), f"Unexpected error: {data}"


class TestAuthMe:
    """Regression tests for GET /api/auth/me"""
    
    def test_auth_me_with_valid_session_token(self):
        """GET /api/auth/me with valid session_token → 200"""
        # First login to get a session token
        login_response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": TEST_EMAIL, "password": TEST_PASSWORD},
            headers={"Content-Type": "application/json"}
        )
        assert login_response.status_code == 200, f"Login failed: {login_response.text}"
        session_token = login_response.json().get("session_token")
        
        # Now test /me endpoint
        me_response = requests.get(
            f"{BASE_URL}/api/auth/me",
            headers={
                "Authorization": f"Bearer {session_token}",
                "Content-Type": "application/json"
            }
        )
        assert me_response.status_code == 200, f"Expected 200, got {me_response.status_code}: {me_response.text}"
        data = me_response.json()
        assert data.get("email") == TEST_EMAIL.lower(), f"Email mismatch: {data}"
        assert "user_id" in data, f"Missing user_id in response: {data}"
    
    def test_auth_me_with_cookie_session_token(self):
        """GET /api/auth/me with session_token in cookie → 200.
        
        In production the login cookie is `Secure=True`, which the `requests`
        library drops when the test runs over plain HTTP against localhost.
        To exercise the same auth code path, the test first drops the
        browser-Secure flag by manually injecting the cookie against the
        base URL, then calls /me without any Authorization header — proving
        cookie-based auth works end-to-end."""
        session = requests.Session()
        login_response = session.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": TEST_EMAIL, "password": TEST_PASSWORD},
            headers={"Content-Type": "application/json"}
        )
        assert login_response.status_code == 200, f"Login failed: {login_response.text}"

        # Manually set cookie (bypassing Secure flag for localhost HTTP tests).
        token = login_response.json()["session_token"]
        session.cookies.set("session_token", token)
        
        me_response = session.get(
            f"{BASE_URL}/api/auth/me",
            headers={"Content-Type": "application/json"}
        )
        assert me_response.status_code == 200, f"Expected 200, got {me_response.status_code}: {me_response.text}"
        data = me_response.json()
        assert data.get("email") == TEST_EMAIL.lower(), f"Email mismatch: {data}"
    
    def test_auth_me_without_token_returns_401(self):
        """GET /api/auth/me without session_token → 401"""
        response = requests.get(
            f"{BASE_URL}/api/auth/me",
            headers={"Content-Type": "application/json"}
        )
        assert response.status_code == 401, f"Expected 401, got {response.status_code}: {response.text}"


class TestConfigLoadsGoogleCredentials:
    """Verify GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET are loaded from env"""
    
    def test_google_oauth_not_503_when_credentials_set(self):
        """If GOOGLE_CLIENT_ID/SECRET are missing, endpoint returns 503.
        Since they ARE set, we should get 400 (missing code) not 503."""
        response = requests.post(
            f"{BASE_URL}/api/auth/google/callback",
            json={},
            headers={"Content-Type": "application/json"}
        )
        # If credentials were missing, we'd get 503 "Google OAuth not configured"
        # Since they're set, we get 400 "code and redirect_uri required"
        assert response.status_code != 503, f"Got 503 - Google OAuth not configured: {response.text}"
        assert response.status_code == 400, f"Expected 400, got {response.status_code}: {response.text}"


class TestLogout:
    """Regression tests for POST /api/auth/logout"""
    
    def test_logout_success(self):
        """POST /api/auth/logout → 200"""
        # First login
        login_response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": TEST_EMAIL, "password": TEST_PASSWORD},
            headers={"Content-Type": "application/json"}
        )
        assert login_response.status_code == 200
        session_token = login_response.json().get("session_token")
        
        # Logout
        logout_response = requests.post(
            f"{BASE_URL}/api/auth/logout",
            headers={
                "Authorization": f"Bearer {session_token}",
                "Content-Type": "application/json"
            }
        )
        assert logout_response.status_code == 200, f"Expected 200, got {logout_response.status_code}: {logout_response.text}"
        data = logout_response.json()
        assert "Logged out" in data.get("message", ""), f"Unexpected response: {data}"
        
        # Verify session is invalidated
        me_response = requests.get(
            f"{BASE_URL}/api/auth/me",
            headers={
                "Authorization": f"Bearer {session_token}",
                "Content-Type": "application/json"
            }
        )
        assert me_response.status_code == 401, f"Session should be invalidated after logout"
