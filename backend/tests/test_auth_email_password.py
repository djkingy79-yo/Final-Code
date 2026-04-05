"""
Test email/password authentication endpoints
Tests: POST /api/auth/register, POST /api/auth/login, GET /api/auth/me
"""
import pytest
import requests
import uuid

BASE_URL = 'http://localhost:8001'


class TestAuthRegister:
    """Test user registration endpoint POST /api/auth/register"""
    
    def test_register_new_user_success(self):
        """Test successful registration of a new user"""
        unique_email = f"TEST_newuser_{uuid.uuid4().hex[:8]}@example.com"
        payload = {
            "email": unique_email,
            "password": "testpass123",
            "name": "Test New User"
        }
        
        response = requests.post(
            f"{BASE_URL}/api/auth/register",
            json=payload
        )
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert "user_id" in data
        assert data["email"] == unique_email.lower()
        assert data["name"] == "Test New User"
        assert "picture" in data
        
        # Verify session cookie was set
        cookies = response.cookies
        assert "session_token" in cookies or any("session_token" in str(c) for c in response.headers.get('set-cookie', ''))
    
    def test_register_duplicate_email_fails(self):
        """Test registration fails for existing email"""
        # First register a user
        unique_email = f"TEST_dup_{uuid.uuid4().hex[:8]}@example.com"
        payload = {
            "email": unique_email,
            "password": "testpass123",
            "name": "First User"
        }
        
        # First registration should succeed
        response1 = requests.post(f"{BASE_URL}/api/auth/register", json=payload)
        assert response1.status_code == 200
        
        # Second registration with same email should fail
        response2 = requests.post(f"{BASE_URL}/api/auth/register", json=payload)
        assert response2.status_code == 400
        assert "already registered" in response2.json().get("detail", "").lower()
    
    def test_register_invalid_email_fails(self):
        """Test registration fails with invalid email format"""
        payload = {
            "email": "not-an-email",
            "password": "testpass123",
            "name": "Test User"
        }
        
        response = requests.post(f"{BASE_URL}/api/auth/register", json=payload)
        assert response.status_code == 400
        assert "invalid email" in response.json().get("detail", "").lower()
    
    def test_register_short_password_fails(self):
        """Test registration fails with password less than 6 characters"""
        payload = {
            "email": f"TEST_shortpw_{uuid.uuid4().hex[:8]}@example.com",
            "password": "12345",  # Only 5 characters
            "name": "Test User"
        }
        
        response = requests.post(f"{BASE_URL}/api/auth/register", json=payload)
        assert response.status_code == 400
        assert "6 characters" in response.json().get("detail", "").lower()
    
    def test_register_missing_email_fails(self):
        """Test registration fails without email"""
        payload = {
            "password": "testpass123",
            "name": "Test User"
        }
        
        response = requests.post(f"{BASE_URL}/api/auth/register", json=payload)
        assert response.status_code == 422  # Validation error


class TestAuthLogin:
    """Test user login endpoint POST /api/auth/login"""
    
    @pytest.fixture
    def registered_user(self):
        """Create a registered user for login tests"""
        unique_email = f"TEST_login_{uuid.uuid4().hex[:8]}@example.com"
        payload = {
            "email": unique_email,
            "password": "testpass123",
            "name": "Login Test User"
        }
        
        response = requests.post(f"{BASE_URL}/api/auth/register", json=payload)
        assert response.status_code == 200
        
        return {
            "email": unique_email.lower(),
            "password": "testpass123",
            "user_id": response.json()["user_id"]
        }
    
    def test_login_success(self, registered_user):
        """Test successful login with valid credentials"""
        payload = {
            "email": registered_user["email"],
            "password": registered_user["password"]
        }
        
        response = requests.post(f"{BASE_URL}/api/auth/login", json=payload)
        
        assert response.status_code == 200
        data = response.json()
        assert data["user_id"] == registered_user["user_id"]
        assert data["email"] == registered_user["email"]
        assert "name" in data
    
    def test_login_wrong_password_fails(self, registered_user):
        """Test login fails with wrong password"""
        payload = {
            "email": registered_user["email"],
            "password": "wrongpassword"
        }
        
        response = requests.post(f"{BASE_URL}/api/auth/login", json=payload)
        
        assert response.status_code == 401
        assert "invalid" in response.json().get("detail", "").lower()
    
    def test_login_nonexistent_user_fails(self):
        """Test login fails for non-existent user"""
        payload = {
            "email": "nonexistent@example.com",
            "password": "testpass123"
        }
        
        response = requests.post(f"{BASE_URL}/api/auth/login", json=payload)
        
        assert response.status_code == 401
        assert "invalid" in response.json().get("detail", "").lower()
    
    def test_login_sets_session_cookie(self, registered_user):
        """Test login sets session_token cookie"""
        payload = {
            "email": registered_user["email"],
            "password": registered_user["password"]
        }
        
        session = requests.Session()
        response = session.post(f"{BASE_URL}/api/auth/login", json=payload)
        
        assert response.status_code == 200
        # Check for session_token in cookies
        assert "session_token" in session.cookies or any("session_token" in str(c) for c in response.headers.get('set-cookie', ''))


class TestAuthMe:
    """Test GET /api/auth/me endpoint for session verification"""
    
    @pytest.fixture
    def authenticated_session(self):
        """Create authenticated session for tests"""
        unique_email = f"TEST_me_{uuid.uuid4().hex[:8]}@example.com"
        
        session = requests.Session()
        
        # Register user
        register_response = session.post(
            f"{BASE_URL}/api/auth/register",
            json={
                "email": unique_email,
                "password": "testpass123",
                "name": "Auth Me Test User"
            }
        )
        
        assert register_response.status_code == 200
        
        return {
            "session": session,
            "email": unique_email.lower(),
            "user_id": register_response.json()["user_id"]
        }
    
    def test_auth_me_returns_user_data(self, authenticated_session):
        """Test /api/auth/me returns user data for authenticated user"""
        session = authenticated_session["session"]
        
        response = session.get(f"{BASE_URL}/api/auth/me")
        
        assert response.status_code == 200
        data = response.json()
        assert data["user_id"] == authenticated_session["user_id"]
        assert data["email"] == authenticated_session["email"]
        assert "terms_accepted" in data
    
    def test_auth_me_fails_without_session(self):
        """Test /api/auth/me returns 401 without session"""
        response = requests.get(f"{BASE_URL}/api/auth/me")
        
        assert response.status_code == 401
        assert "not authenticated" in response.json().get("detail", "").lower()
    
    def test_auth_me_with_bearer_token(self, authenticated_session):
        """Test /api/auth/me works with Authorization header"""
        # Get the session token from cookies
        session = authenticated_session["session"]
        cookies = session.cookies
        
        # Extract session_token if present
        session_token = cookies.get("session_token")
        
        if session_token:
            # Test with Bearer token
            response = requests.get(
                f"{BASE_URL}/api/auth/me",
                headers={"Authorization": f"Bearer {session_token}"}
            )
            
            assert response.status_code == 200
            assert response.json()["user_id"] == authenticated_session["user_id"]


class TestAuthLogout:
    """Test POST /api/auth/logout endpoint"""
    
    @pytest.fixture
    def authenticated_session(self):
        """Create authenticated session for logout tests"""
        unique_email = f"TEST_logout_{uuid.uuid4().hex[:8]}@example.com"
        
        session = requests.Session()
        
        register_response = session.post(
            f"{BASE_URL}/api/auth/register",
            json={
                "email": unique_email,
                "password": "testpass123",
                "name": "Logout Test User"
            }
        )
        
        assert register_response.status_code == 200
        
        return session
    
    def test_logout_success(self, authenticated_session):
        """Test successful logout"""
        session = authenticated_session
        
        # Verify logged in first
        me_response = session.get(f"{BASE_URL}/api/auth/me")
        assert me_response.status_code == 200
        
        # Logout
        logout_response = session.post(f"{BASE_URL}/api/auth/logout")
        assert logout_response.status_code == 200
        assert "logged out" in logout_response.json().get("message", "").lower()


class TestAuthIntegration:
    """Integration tests for complete auth flow"""
    
    def test_full_auth_flow_register_login_verify(self):
        """Test complete flow: register -> login -> verify session"""
        unique_email = f"TEST_fullflow_{uuid.uuid4().hex[:8]}@example.com"
        password = "testpass123"
        name = "Full Flow Test User"
        
        session = requests.Session()
        
        # Step 1: Register
        register_response = session.post(
            f"{BASE_URL}/api/auth/register",
            json={"email": unique_email, "password": password, "name": name}
        )
        assert register_response.status_code == 200
        user_id = register_response.json()["user_id"]
        
        # Step 2: Verify session immediately after register
        me_response = session.get(f"{BASE_URL}/api/auth/me")
        assert me_response.status_code == 200
        assert me_response.json()["user_id"] == user_id
        
        # Step 3: Logout
        logout_response = session.post(f"{BASE_URL}/api/auth/logout")
        assert logout_response.status_code == 200
        
        # Step 4: Login again with new session
        new_session = requests.Session()
        login_response = new_session.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": unique_email, "password": password}
        )
        assert login_response.status_code == 200
        assert login_response.json()["user_id"] == user_id
        
        # Step 5: Verify session after login
        me_response2 = new_session.get(f"{BASE_URL}/api/auth/me")
        assert me_response2.status_code == 200
        assert me_response2.json()["user_id"] == user_id


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
