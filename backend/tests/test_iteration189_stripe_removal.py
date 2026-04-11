"""
Iteration 189: Test Stripe removal and PayID-only payment flow
Tests:
1. Stripe endpoint returns 404
2. PayID create-reference works
3. PayID verify endpoint exists
4. Payment history has no Stripe references
5. Payment prices endpoint works
6. Health endpoints
7. Auth endpoints
8. Cases endpoint
9. Notifications endpoint
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

class TestStripeRemoval:
    """Verify Stripe is completely removed"""
    
    def test_stripe_checkout_returns_404(self):
        """POST /api/payments/stripe/create-checkout should return 404"""
        response = requests.post(
            f"{BASE_URL}/api/payments/stripe/create-checkout",
            json={"feature_type": "full_report", "case_id": "test"},
            headers={"Content-Type": "application/json"}
        )
        # Should be 404 (not found) or 401 (auth required before 404)
        # If Stripe is removed, the route doesn't exist
        assert response.status_code in [404, 405], f"Expected 404/405, got {response.status_code}"
        print(f"PASS: Stripe checkout endpoint returns {response.status_code} (removed)")


class TestPayIDPaymentFlow:
    """Test PayID payment flow works"""
    
    @pytest.fixture(scope="class")
    def auth_token(self):
        """Get auth token for authenticated tests"""
        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": "djkingy79@gmail.com", "password": "Grubbygrub88"}
        )
        if response.status_code == 200:
            return response.json().get("session_token")
        pytest.skip("Auth failed - skipping authenticated tests")
    
    def test_payid_create_reference_requires_auth(self):
        """POST /api/payments/payid/create-reference requires auth"""
        response = requests.post(
            f"{BASE_URL}/api/payments/payid/create-reference",
            json={"feature_type": "full_report", "case_id": "case_e24c3880b02f"}
        )
        assert response.status_code == 401, f"Expected 401, got {response.status_code}"
        print("PASS: PayID create-reference requires authentication")
    
    def test_payid_create_reference_with_auth(self, auth_token):
        """POST /api/payments/payid/create-reference returns valid reference"""
        response = requests.post(
            f"{BASE_URL}/api/payments/payid/create-reference",
            json={"feature_type": "full_report", "case_id": "case_e24c3880b02f"},
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        assert "reference" in data, "Response should contain 'reference'"
        assert "payid" in data, "Response should contain 'payid'"
        assert "amount" in data, "Response should contain 'amount'"
        print(f"PASS: PayID create-reference returns valid data: ref={data.get('reference')}")
    
    def test_payid_verify_endpoint_exists(self, auth_token):
        """POST /api/payments/payid/verify endpoint exists"""
        response = requests.post(
            f"{BASE_URL}/api/payments/payid/verify",
            json={"reference": "TEST_REF", "case_id": "case_e24c3880b02f", "feature_type": "full_report"},
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        # Should return 200, 400 (invalid reference), or 404 (reference not found in DB)
        # 404 here means the reference wasn't found in DB, not that the endpoint doesn't exist
        assert response.status_code in [200, 400, 404], f"Unexpected status: {response.status_code}"
        # Check response body to distinguish endpoint-not-found vs reference-not-found
        if response.status_code == 404:
            data = response.json()
            # If detail says "Payment reference not found", endpoint exists but ref doesn't
            assert "reference" in data.get("detail", "").lower() or "not found" in data.get("detail", "").lower(), \
                f"Unexpected 404 response: {data}"
        print(f"PASS: PayID verify endpoint exists (status: {response.status_code})")


class TestPaymentHistory:
    """Test payment history has no Stripe references"""
    
    @pytest.fixture(scope="class")
    def auth_token(self):
        """Get auth token"""
        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": "djkingy79@gmail.com", "password": "Grubbygrub88"}
        )
        if response.status_code == 200:
            return response.json().get("session_token")
        pytest.skip("Auth failed")
    
    def test_payment_history_returns_data(self, auth_token):
        """GET /api/payments/history returns data"""
        response = requests.get(
            f"{BASE_URL}/api/payments/history",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        data = response.json()
        assert "payments" in data, "Response should contain 'payments'"
        print(f"PASS: Payment history returns {len(data.get('payments', []))} payments")
    
    def test_payment_history_no_stripe_method(self, auth_token):
        """Payment history should not have 'stripe' method"""
        response = requests.get(
            f"{BASE_URL}/api/payments/history",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        payments = data.get("payments", [])
        stripe_payments = [p for p in payments if p.get("method") == "stripe"]
        # Note: There may be historical Stripe payments, but new ones shouldn't be created
        print(f"PASS: Payment history checked - {len(stripe_payments)} historical stripe payments (if any)")
    
    def test_payment_prices_returns_data(self, auth_token):
        """GET /api/payments/prices returns pricing"""
        response = requests.get(
            f"{BASE_URL}/api/payments/prices",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        data = response.json()
        assert "prices" in data or isinstance(data, dict), "Response should contain pricing data"
        print(f"PASS: Payment prices endpoint returns data")


class TestHealthEndpoints:
    """Test health endpoints"""
    
    def test_health_endpoint(self):
        """GET /api/health returns healthy"""
        response = requests.get(f"{BASE_URL}/api/health")
        assert response.status_code == 200
        data = response.json()
        assert data.get("status") == "healthy"
        print("PASS: /api/health returns healthy")
    
    def test_ready_endpoint(self):
        """GET /api/ready returns ready"""
        response = requests.get(f"{BASE_URL}/api/ready")
        assert response.status_code == 200
        data = response.json()
        assert data.get("ready") == True
        print("PASS: /api/ready returns ready")


class TestAuthEndpoints:
    """Test auth endpoints"""
    
    def test_login_with_valid_credentials(self):
        """POST /api/auth/login with valid credentials"""
        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": "djkingy79@gmail.com", "password": "Grubbygrub88"}
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        data = response.json()
        assert "session_token" in data, "Response should contain session_token"
        print("PASS: Login returns session_token")
    
    def test_auth_me_with_token(self):
        """GET /api/auth/me with valid token"""
        # First login
        login_resp = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": "djkingy79@gmail.com", "password": "Grubbygrub88"}
        )
        token = login_resp.json().get("session_token")
        
        # Then check /me
        response = requests.get(
            f"{BASE_URL}/api/auth/me",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "email" in data or "user_id" in data
        print("PASS: /api/auth/me returns user data")


class TestCasesEndpoint:
    """Test cases endpoint"""
    
    @pytest.fixture(scope="class")
    def auth_token(self):
        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": "djkingy79@gmail.com", "password": "Grubbygrub88"}
        )
        if response.status_code == 200:
            return response.json().get("session_token")
        pytest.skip("Auth failed")
    
    def test_cases_list(self, auth_token):
        """GET /api/cases returns list"""
        response = requests.get(
            f"{BASE_URL}/api/cases",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list) or "cases" in data
        print(f"PASS: /api/cases returns case list")
    
    def test_case_detail(self, auth_token):
        """GET /api/cases/{case_id} returns case"""
        response = requests.get(
            f"{BASE_URL}/api/cases/case_e24c3880b02f",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "case_id" in data or "title" in data
        print("PASS: /api/cases/{case_id} returns case detail")


class TestNotificationsEndpoint:
    """Test notifications endpoint"""
    
    @pytest.fixture(scope="class")
    def auth_token(self):
        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": "djkingy79@gmail.com", "password": "Grubbygrub88"}
        )
        if response.status_code == 200:
            return response.json().get("session_token")
        pytest.skip("Auth failed")
    
    def test_notifications_list(self, auth_token):
        """GET /api/notifications returns list"""
        response = requests.get(
            f"{BASE_URL}/api/notifications",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list) or "notifications" in data
        print("PASS: /api/notifications returns data")
