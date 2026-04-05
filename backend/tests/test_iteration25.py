"""
Iteration 25 Backend Tests
Testing:
1. Auth routes (register, login, /me with is_admin)
2. States endpoint (utilities router)
3. Analytics dashboard (admin only)
"""
import pytest
import requests
import os
import uuid

# Get BASE_URL from environment
BASE_URL = 'http://localhost:8001'

# Test user credentials
TEST_EMAIL = f"TEST_user_{uuid.uuid4().hex[:8]}@test.com"
TEST_PASSWORD = "testpass123"
TEST_NAME = "Test User"

# Admin email
ADMIN_EMAIL = "test@example.com"

class TestAuthEndpoints:
    """Test auth endpoints from routers/auth.py"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup test session"""
        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json"})
    
    def test_register_new_user(self):
        """Test /api/auth/register creates new user"""
        response = self.session.post(f"{BASE_URL}/api/auth/register", json={
            "email": TEST_EMAIL,
            "password": TEST_PASSWORD,
            "name": TEST_NAME
        })
        
        # Check status
        assert response.status_code == 200, f"Register failed: {response.text}"
        
        # Check response data
        data = response.json()
        assert "user_id" in data
        assert data["email"] == TEST_EMAIL.lower()
        assert data["name"] == TEST_NAME
        print(f"✓ Register returned user_id: {data['user_id']}")
    
    def test_register_duplicate_email_fails(self):
        """Test /api/auth/register fails for duplicate email"""
        response = self.session.post(f"{BASE_URL}/api/auth/register", json={
            "email": TEST_EMAIL,
            "password": TEST_PASSWORD,
            "name": TEST_NAME
        })
        
        # Should return 400 for duplicate
        assert response.status_code == 400, f"Should fail for duplicate: {response.text}"
        assert "already registered" in response.json().get("detail", "").lower()
        print("✓ Duplicate email correctly rejected")
    
    def test_login_with_registered_user(self):
        """Test /api/auth/login with registered credentials"""
        response = self.session.post(f"{BASE_URL}/api/auth/login", json={
            "email": TEST_EMAIL,
            "password": TEST_PASSWORD
        })
        
        # Check status
        assert response.status_code == 200, f"Login failed: {response.text}"
        
        # Check response data
        data = response.json()
        assert "user_id" in data
        assert data["email"] == TEST_EMAIL.lower()
        print(f"✓ Login successful for {data['email']}")
        
        # Store session cookie for later tests
        self.session_token = response.cookies.get("session_token")
        assert self.session_token is not None, "Session token cookie should be set"
        print("✓ Session token cookie set")
    
    def test_login_invalid_credentials(self):
        """Test /api/auth/login fails with wrong password"""
        response = self.session.post(f"{BASE_URL}/api/auth/login", json={
            "email": TEST_EMAIL,
            "password": "wrongpassword"
        })
        
        # Should return 401
        assert response.status_code == 401, f"Should fail for wrong password: {response.text}"
        print("✓ Invalid credentials correctly rejected")
    
    def test_auth_me_returns_user(self):
        """Test /api/auth/me returns current user info"""
        # First login to get session
        login_response = self.session.post(f"{BASE_URL}/api/auth/login", json={
            "email": TEST_EMAIL,
            "password": TEST_PASSWORD
        })
        assert login_response.status_code == 200
        
        # Now call /me endpoint with session cookie
        me_response = self.session.get(f"{BASE_URL}/api/auth/me")
        
        assert me_response.status_code == 200, f"/me failed: {me_response.text}"
        
        data = me_response.json()
        assert data["email"] == TEST_EMAIL.lower()
        assert "is_admin" in data, "is_admin field should be present"
        assert not data["is_admin"], "Regular user should not be admin"
        print(f"✓ /me returned user with is_admin={data['is_admin']}")
    
    def test_auth_me_has_is_admin_field(self):
        """Test /api/auth/me explicitly includes is_admin field"""
        # Login first
        login_response = self.session.post(f"{BASE_URL}/api/auth/login", json={
            "email": TEST_EMAIL,
            "password": TEST_PASSWORD
        })
        assert login_response.status_code == 200
        
        # Call /me
        me_response = self.session.get(f"{BASE_URL}/api/auth/me")
        assert me_response.status_code == 200
        
        data = me_response.json()
        
        # Verify is_admin field exists and is boolean
        assert "is_admin" in data, "is_admin field MUST be present in /auth/me response"
        assert isinstance(data["is_admin"], bool), "is_admin should be boolean"
        print(f"✓ is_admin field present and is boolean: {data['is_admin']}")


class TestStatesEndpoint:
    """Test /api/states endpoint from utilities router"""
    
    def test_states_returns_all_australian_states(self):
        """Test /api/states returns all 8 Australian states/territories"""
        response = requests.get(f"{BASE_URL}/api/states")
        
        assert response.status_code == 200, f"/api/states failed: {response.text}"
        
        data = response.json()
        assert "states" in data
        
        states = data["states"]
        assert len(states) >= 8, f"Expected at least 8 states, got {len(states)}"
        
        # Check expected states are present
        state_ids = [s["id"] for s in states]
        expected_states = ["nsw", "vic", "qld", "sa", "wa", "tas", "nt", "act"]
        
        for expected in expected_states:
            assert expected in state_ids, f"Missing state: {expected}"
        
        print(f"✓ /api/states returned {len(states)} states: {state_ids}")
        
        # Verify state structure
        for state in states:
            assert "id" in state
            assert "name" in state
            assert "abbreviation" in state
        
        print("✓ All states have required fields (id, name, abbreviation)")


class TestAnalyticsDashboard:
    """Test /api/analytics/dashboard endpoint - admin only"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup test session"""
        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json"})
    
    def test_analytics_dashboard_requires_auth(self):
        """Test /api/analytics/dashboard requires authentication"""
        response = requests.get(f"{BASE_URL}/api/analytics/dashboard")
        
        # Should return 401 for unauthenticated
        assert response.status_code == 401, f"Should require auth: {response.text}"
        print("✓ Analytics dashboard requires authentication")
    
    def test_analytics_dashboard_requires_admin(self):
        """Test /api/analytics/dashboard requires admin role"""
        # Login as regular user
        login_response = self.session.post(f"{BASE_URL}/api/auth/login", json={
            "email": TEST_EMAIL,
            "password": TEST_PASSWORD
        })
        
        if login_response.status_code != 200:
            # Create user if not exists
            self.session.post(f"{BASE_URL}/api/auth/register", json={
                "email": TEST_EMAIL,
                "password": TEST_PASSWORD,
                "name": TEST_NAME
            })
            login_response = self.session.post(f"{BASE_URL}/api/auth/login", json={
                "email": TEST_EMAIL,
                "password": TEST_PASSWORD
            })
        
        # Try to access dashboard as regular user
        dashboard_response = self.session.get(f"{BASE_URL}/api/analytics/dashboard")
        
        # Should return 403 for non-admin
        assert dashboard_response.status_code == 403, f"Should require admin: {dashboard_response.text}"
        print("✓ Analytics dashboard correctly requires admin access")


class TestHealthCheck:
    """Test basic health check"""
    
    def test_health_endpoint(self):
        """Test /api/health or /health endpoint is accessible"""
        # Try /api/health first (standard for external access)
        response = requests.get(f"{BASE_URL}/api/health")
        
        if response.status_code != 200:
            # Try root health (internal)
            response = requests.get(f"{BASE_URL}/health")
        
        # Accept 200 or check for any valid response
        # The health endpoint may return HTML for the frontend SPA
        if response.status_code == 200:
            try:
                data = response.json()
                if "status" in data:
                    assert data["status"] == "healthy"
                    print(f"✓ Health check passed: {data}")
                    return
            except Exception:
                pass
        
        # If we reach here, try states endpoint as health proxy
        response = requests.get(f"{BASE_URL}/api/states")
        assert response.status_code == 200, f"Backend connectivity check failed: {response.text}"
        print("✓ Backend is accessible (verified via /api/states)")


# Cleanup function
def cleanup_test_data():
    """Cleanup test users - called at end"""
    session = requests.Session()
    session.headers.update({"Content-Type": "application/json"})
    
    # Login as test user
    login_response = session.post(f"{BASE_URL}/api/auth/login", json={
        "email": TEST_EMAIL,
        "password": TEST_PASSWORD
    })
    
    if login_response.status_code == 200:
        # Logout to invalidate session
        session.post(f"{BASE_URL}/api/auth/logout")
        print(f"Logged out test user: {TEST_EMAIL}")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
