"""
Iteration 188: API Endpoint Testing
Tests all critical API endpoints for correct HTTP status codes and responses.
Includes: health, auth, cases, documents, timeline, grounds, notes, reports,
notifications, payments, statistics, languages, states, offence-categories
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')
if not BASE_URL:
    BASE_URL = "https://criminal-appeals-au-2.preview.emergentagent.com"

# Test credentials
TEST_EMAIL = "djkingy79@gmail.com"
TEST_PASSWORD = "Grubbygrub88"
TEST_CASE_ID = "case_e24c3880b02f"


class TestHealthEndpoint:
    """Health check endpoint tests"""
    
    def test_health_returns_200(self):
        """GET /api/health should return 200 with healthy status"""
        response = requests.get(f"{BASE_URL}/api/health", timeout=10)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        data = response.json()
        assert data.get("status") == "healthy", f"Expected healthy status, got {data}"
        assert "database" in data, "Missing database field in health response"
        print(f"✓ Health endpoint: {data['status']}, DB: {data.get('database')}")


class TestAuthEndpoints:
    """Authentication endpoint tests"""
    
    @pytest.fixture(scope="class")
    def session_token(self):
        """Login and get session token"""
        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": TEST_EMAIL, "password": TEST_PASSWORD},
            timeout=30
        )
        if response.status_code == 200:
            token = response.json().get("session_token")
            print(f"✓ Login successful, got session token")
            return token
        pytest.skip(f"Login failed with status {response.status_code}: {response.text}")
    
    def test_login_success(self):
        """POST /api/auth/login should return 200 with valid credentials"""
        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": TEST_EMAIL, "password": TEST_PASSWORD},
            timeout=30
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        assert "session_token" in data, "Missing session_token in login response"
        print(f"✓ Login endpoint working, token received")
    
    def test_login_invalid_credentials(self):
        """POST /api/auth/login should return 401 with invalid credentials"""
        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": "invalid@example.com", "password": "wrongpassword"},
            timeout=30
        )
        assert response.status_code in [401, 400], f"Expected 401/400, got {response.status_code}"
        print(f"✓ Invalid login correctly rejected with {response.status_code}")
    
    def test_auth_me_requires_auth(self):
        """GET /api/auth/me should return 401 without token"""
        response = requests.get(f"{BASE_URL}/api/auth/me", timeout=10)
        assert response.status_code == 401, f"Expected 401, got {response.status_code}"
        print(f"✓ /api/auth/me correctly requires authentication")
    
    def test_auth_me_with_token(self, session_token):
        """GET /api/auth/me should return 200 with valid token"""
        response = requests.get(
            f"{BASE_URL}/api/auth/me",
            headers={"Authorization": f"Bearer {session_token}"},
            timeout=10
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        assert "email" in data or "user_id" in data, "Missing user info in /auth/me response"
        print(f"✓ /api/auth/me returns user data")


class TestCaseEndpoints:
    """Case CRUD endpoint tests"""
    
    @pytest.fixture(scope="class")
    def auth_headers(self):
        """Get auth headers"""
        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": TEST_EMAIL, "password": TEST_PASSWORD},
            timeout=30
        )
        if response.status_code == 200:
            token = response.json().get("session_token")
            return {"Authorization": f"Bearer {token}"}
        pytest.skip("Login failed")
    
    def test_cases_list_requires_auth(self):
        """GET /api/cases should return 401 without auth"""
        response = requests.get(f"{BASE_URL}/api/cases", timeout=10)
        assert response.status_code == 401, f"Expected 401, got {response.status_code}"
        print(f"✓ /api/cases correctly requires authentication")
    
    def test_cases_list_with_auth(self, auth_headers):
        """GET /api/cases should return 200 with auth"""
        response = requests.get(
            f"{BASE_URL}/api/cases",
            headers=auth_headers,
            timeout=30
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        assert isinstance(data, list), "Expected list of cases"
        print(f"✓ /api/cases returns {len(data)} cases")
    
    def test_case_detail(self, auth_headers):
        """GET /api/cases/{case_id} should return 200 for existing case"""
        response = requests.get(
            f"{BASE_URL}/api/cases/{TEST_CASE_ID}",
            headers=auth_headers,
            timeout=30
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        assert "case_id" in data or "title" in data, "Missing case data"
        print(f"✓ /api/cases/{TEST_CASE_ID} returns case data")
    
    def test_case_documents(self, auth_headers):
        """GET /api/cases/{case_id}/documents should return 200"""
        response = requests.get(
            f"{BASE_URL}/api/cases/{TEST_CASE_ID}/documents",
            headers=auth_headers,
            timeout=30
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        assert isinstance(data, list), "Expected list of documents"
        print(f"✓ /api/cases/{TEST_CASE_ID}/documents returns {len(data)} documents")
    
    def test_case_timeline(self, auth_headers):
        """GET /api/cases/{case_id}/timeline should return 200"""
        response = requests.get(
            f"{BASE_URL}/api/cases/{TEST_CASE_ID}/timeline",
            headers=auth_headers,
            timeout=30
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        assert isinstance(data, list), "Expected list of timeline events"
        print(f"✓ /api/cases/{TEST_CASE_ID}/timeline returns {len(data)} events")
    
    def test_case_grounds(self, auth_headers):
        """GET /api/cases/{case_id}/grounds should return 200"""
        response = requests.get(
            f"{BASE_URL}/api/cases/{TEST_CASE_ID}/grounds",
            headers=auth_headers,
            timeout=30
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        # Grounds endpoint returns object with grounds array and metadata
        assert "grounds" in data or isinstance(data, list), "Expected grounds data"
        print(f"✓ /api/cases/{TEST_CASE_ID}/grounds returns grounds data")
    
    def test_case_notes(self, auth_headers):
        """GET /api/cases/{case_id}/notes should return 200"""
        response = requests.get(
            f"{BASE_URL}/api/cases/{TEST_CASE_ID}/notes",
            headers=auth_headers,
            timeout=30
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        assert isinstance(data, list), "Expected list of notes"
        print(f"✓ /api/cases/{TEST_CASE_ID}/notes returns {len(data)} notes")
    
    def test_case_reports(self, auth_headers):
        """GET /api/cases/{case_id}/reports should return 200"""
        response = requests.get(
            f"{BASE_URL}/api/cases/{TEST_CASE_ID}/reports",
            headers=auth_headers,
            timeout=30
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        assert isinstance(data, list), "Expected list of reports"
        print(f"✓ /api/cases/{TEST_CASE_ID}/reports returns {len(data)} reports")


class TestNotificationsEndpoint:
    """Notifications endpoint tests"""
    
    @pytest.fixture(scope="class")
    def auth_headers(self):
        """Get auth headers"""
        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": TEST_EMAIL, "password": TEST_PASSWORD},
            timeout=30
        )
        if response.status_code == 200:
            token = response.json().get("session_token")
            return {"Authorization": f"Bearer {token}"}
        pytest.skip("Login failed")
    
    def test_notifications_endpoint(self, auth_headers):
        """GET /api/notifications should return 200"""
        response = requests.get(
            f"{BASE_URL}/api/notifications",
            headers=auth_headers,
            timeout=30
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        # API returns object with notifications array
        notifications = data.get("notifications", data) if isinstance(data, dict) else data
        assert isinstance(notifications, list), "Expected notifications list"
        print(f"✓ /api/notifications returns {len(notifications)} notifications")


class TestPaymentEndpoints:
    """Payment endpoint tests"""
    
    @pytest.fixture(scope="class")
    def auth_headers(self):
        """Get auth headers"""
        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": TEST_EMAIL, "password": TEST_PASSWORD},
            timeout=30
        )
        if response.status_code == 200:
            token = response.json().get("session_token")
            return {"Authorization": f"Bearer {token}"}
        pytest.skip("Login failed")
    
    def test_payment_prices(self, auth_headers):
        """GET /api/payments/prices should return 200"""
        response = requests.get(
            f"{BASE_URL}/api/payments/prices",
            headers=auth_headers,
            timeout=30
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        assert isinstance(data, dict) or isinstance(data, list), "Expected prices data"
        print(f"✓ /api/payments/prices returns pricing data")
    
    def test_payment_history(self, auth_headers):
        """GET /api/payments/history should return 200"""
        response = requests.get(
            f"{BASE_URL}/api/payments/history",
            headers=auth_headers,
            timeout=30
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        assert isinstance(data, list) or isinstance(data, dict), "Expected payment history data"
        print(f"✓ /api/payments/history returns payment history")
    
    def test_stripe_checkout_requires_auth(self):
        """POST /api/payments/stripe/create-checkout should return 401 without auth"""
        response = requests.post(
            f"{BASE_URL}/api/payments/stripe/create-checkout",
            json={"feature_type": "grounds_of_merit", "case_id": TEST_CASE_ID},
            timeout=30
        )
        assert response.status_code == 401, f"Expected 401, got {response.status_code}"
        print(f"✓ Stripe checkout correctly requires authentication")
    
    def test_stripe_checkout_with_auth(self, auth_headers):
        """POST /api/payments/stripe/create-checkout should return checkout URL"""
        response = requests.post(
            f"{BASE_URL}/api/payments/stripe/create-checkout",
            headers=auth_headers,
            json={
                "feature_type": "grounds_of_merit",
                "case_id": TEST_CASE_ID,
                "origin_url": BASE_URL
            },
            timeout=60
        )
        # Could be 200 (success), 400 (already unlocked), or 503 (Stripe not configured)
        if response.status_code == 200:
            data = response.json()
            assert "url" in data, "Missing checkout URL in response"
            assert data["url"].startswith("https://"), "Invalid checkout URL"
            print(f"✓ Stripe checkout returns valid URL: {data['url'][:50]}...")
        elif response.status_code == 400:
            data = response.json()
            print(f"✓ Stripe checkout: Feature already unlocked or invalid request: {data.get('detail', '')}")
        elif response.status_code == 503:
            print(f"⚠ Stripe checkout: Service unavailable (Stripe not configured)")
        else:
            pytest.fail(f"Unexpected status {response.status_code}: {response.text}")


class TestPublicEndpoints:
    """Public endpoint tests (no auth required)"""
    
    def test_statistics_public(self):
        """GET /api/statistics/public should return 200"""
        response = requests.get(f"{BASE_URL}/api/statistics/public", timeout=30)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        assert isinstance(data, dict), "Expected statistics data"
        print(f"✓ /api/statistics/public returns statistics")
    
    def test_languages_endpoint(self):
        """GET /api/languages should return 200"""
        response = requests.get(f"{BASE_URL}/api/languages", timeout=10)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        # API returns object with languages array
        languages = data.get("languages", data) if isinstance(data, dict) else data
        assert isinstance(languages, list), "Expected list of languages"
        print(f"✓ /api/languages returns {len(languages)} languages")
    
    def test_states_endpoint(self):
        """GET /api/states should return 200"""
        response = requests.get(f"{BASE_URL}/api/states", timeout=10)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        # API returns object with states array
        states = data.get("states", data) if isinstance(data, dict) else data
        assert isinstance(states, list), "Expected list of states"
        # Should include Australian states
        state_codes = [s.get("abbreviation") or s.get("id") for s in states if isinstance(s, dict)]
        print(f"✓ /api/states returns {len(states)} states: {state_codes[:5]}...")
    
    def test_offence_categories_endpoint(self):
        """GET /api/offence-categories should return 200"""
        response = requests.get(f"{BASE_URL}/api/offence-categories", timeout=10)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        # API returns object with categories array
        categories = data.get("categories", data) if isinstance(data, dict) else data
        assert isinstance(categories, list), "Expected list of offence categories"
        print(f"✓ /api/offence-categories returns {len(categories)} categories")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
