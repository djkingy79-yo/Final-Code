"""
Iteration 180: Stripe Payment Integration Tests
Tests for Stripe Checkout and PayID payment endpoints.
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Test credentials
TEST_EMAIL = "djkingy79@gmail.com"
TEST_PASSWORD = "Grubbygrub88"
TEST_CASE_ID = "case_d294f503192a"


@pytest.fixture(scope="module")
def auth_token():
    """Get authentication token for tests"""
    response = requests.post(
        f"{BASE_URL}/api/auth/login",
        json={"email": TEST_EMAIL, "password": TEST_PASSWORD}
    )
    if response.status_code == 200:
        return response.json().get("session_token")
    pytest.skip("Authentication failed - skipping authenticated tests")


@pytest.fixture
def auth_headers(auth_token):
    """Headers with auth token"""
    return {
        "Authorization": f"Bearer {auth_token}",
        "Content-Type": "application/json"
    }


class TestAuthLogin:
    """Test authentication endpoints"""
    
    def test_login_success(self):
        """POST /api/auth/login - valid credentials"""
        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": TEST_EMAIL, "password": TEST_PASSWORD}
        )
        assert response.status_code == 200
        data = response.json()
        assert "session_token" in data
        assert "user_id" in data
        assert data["email"] == TEST_EMAIL
    
    def test_login_invalid_credentials(self):
        """POST /api/auth/login - invalid credentials"""
        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": "wrong@example.com", "password": "wrongpass"}
        )
        assert response.status_code == 401


class TestStripePayments:
    """Test Stripe payment endpoints"""
    
    def test_stripe_create_checkout_success(self, auth_headers):
        """POST /api/payments/stripe/create-checkout - creates checkout session"""
        response = requests.post(
            f"{BASE_URL}/api/payments/stripe/create-checkout",
            headers=auth_headers,
            json={
                "feature_type": "full_report",  # Use full_report to avoid "already unlocked" for admin
                "case_id": TEST_CASE_ID,
                "origin_url": BASE_URL
            }
        )
        # Admin user has all features unlocked, so expect 400
        # For non-admin users, this would return 200 with url and session_id
        if response.status_code == 200:
            data = response.json()
            assert "url" in data
            assert "session_id" in data
            assert data["url"].startswith("https://checkout.stripe.com/")
            print(f"Stripe checkout URL: {data['url'][:50]}...")
        elif response.status_code == 400:
            data = response.json()
            assert "already unlocked" in data.get("detail", "").lower() or "Feature already unlocked" in data.get("detail", "")
            print("Feature already unlocked for admin user (expected)")
        else:
            pytest.fail(f"Unexpected status code: {response.status_code}")
    
    def test_stripe_create_checkout_missing_case_id(self, auth_headers):
        """POST /api/payments/stripe/create-checkout - missing case_id"""
        response = requests.post(
            f"{BASE_URL}/api/payments/stripe/create-checkout",
            headers=auth_headers,
            json={
                "feature_type": "grounds_of_merit",
                "origin_url": BASE_URL
            }
        )
        assert response.status_code == 400
        assert "case_id" in response.json().get("detail", "").lower()
    
    def test_stripe_create_checkout_invalid_feature(self, auth_headers):
        """POST /api/payments/stripe/create-checkout - invalid feature type"""
        response = requests.post(
            f"{BASE_URL}/api/payments/stripe/create-checkout",
            headers=auth_headers,
            json={
                "feature_type": "invalid_feature",
                "case_id": TEST_CASE_ID,
                "origin_url": BASE_URL
            }
        )
        assert response.status_code == 400
        assert "invalid" in response.json().get("detail", "").lower()
    
    def test_stripe_create_checkout_no_auth(self):
        """POST /api/payments/stripe/create-checkout - no authentication"""
        response = requests.post(
            f"{BASE_URL}/api/payments/stripe/create-checkout",
            json={
                "feature_type": "grounds_of_merit",
                "case_id": TEST_CASE_ID,
                "origin_url": BASE_URL
            }
        )
        assert response.status_code == 401
    
    def test_stripe_status_not_found(self, auth_headers):
        """GET /api/payments/stripe/status/{session_id} - session not found"""
        response = requests.get(
            f"{BASE_URL}/api/payments/stripe/status/nonexistent_session_id",
            headers=auth_headers
        )
        # Should return 404 for non-existent session
        assert response.status_code == 404
    
    def test_stripe_status_no_auth(self):
        """GET /api/payments/stripe/status/{session_id} - no authentication"""
        response = requests.get(
            f"{BASE_URL}/api/payments/stripe/status/test_session_id"
        )
        assert response.status_code == 401


class TestPayIDPayments:
    """Test PayID payment endpoints"""
    
    def test_payid_create_reference_success(self, auth_headers):
        """POST /api/payments/payid/create-reference - creates payment reference"""
        response = requests.post(
            f"{BASE_URL}/api/payments/payid/create-reference",
            headers=auth_headers,
            json={
                "feature_type": "grounds_of_merit",
                "case_id": TEST_CASE_ID,
                "use_trial": False
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert "reference" in data
        assert "amount" in data
        assert "payid" in data
        assert "payid_name" in data
        assert "instructions" in data
        assert data["reference"].startswith("ACM-")
        assert data["amount"] == 99.0  # grounds_of_merit price
        print(f"PayID reference: {data['reference']}")
    
    def test_payid_create_reference_with_trial(self, auth_headers):
        """POST /api/payments/payid/create-reference - with trial pricing"""
        response = requests.post(
            f"{BASE_URL}/api/payments/payid/create-reference",
            headers=auth_headers,
            json={
                "feature_type": "grounds_of_merit",
                "case_id": TEST_CASE_ID,
                "use_trial": True
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert "reference" in data
        # Trial price is $5 for first-time users, but admin may have completed payments
        assert data["amount"] in [5.0, 99.0]
        print(f"PayID amount with trial: ${data['amount']}")
    
    def test_payid_create_reference_missing_fields(self, auth_headers):
        """POST /api/payments/payid/create-reference - missing required fields"""
        response = requests.post(
            f"{BASE_URL}/api/payments/payid/create-reference",
            headers=auth_headers,
            json={
                "feature_type": "grounds_of_merit"
                # Missing case_id
            }
        )
        assert response.status_code == 400
    
    def test_payid_create_reference_no_auth(self):
        """POST /api/payments/payid/create-reference - no authentication"""
        response = requests.post(
            f"{BASE_URL}/api/payments/payid/create-reference",
            json={
                "feature_type": "grounds_of_merit",
                "case_id": TEST_CASE_ID
            }
        )
        assert response.status_code == 401
    
    def test_payid_verify_success(self, auth_headers):
        """POST /api/payments/payid/verify - verify payment reference"""
        # First create a reference
        create_response = requests.post(
            f"{BASE_URL}/api/payments/payid/create-reference",
            headers=auth_headers,
            json={
                "feature_type": "full_report",
                "case_id": TEST_CASE_ID,
                "use_trial": False
            }
        )
        assert create_response.status_code == 200
        reference = create_response.json()["reference"]
        
        # Now verify it
        verify_response = requests.post(
            f"{BASE_URL}/api/payments/payid/verify",
            headers=auth_headers,
            json={
                "reference": reference,
                "case_id": TEST_CASE_ID,
                "feature_type": "full_report"
            }
        )
        assert verify_response.status_code == 200
        data = verify_response.json()
        assert data["status"] in ["submitted_for_review", "already_verified", "pending_verification"]
        print(f"PayID verify status: {data['status']}")
    
    def test_payid_verify_invalid_reference(self, auth_headers):
        """POST /api/payments/payid/verify - invalid reference"""
        response = requests.post(
            f"{BASE_URL}/api/payments/payid/verify",
            headers=auth_headers,
            json={
                "reference": "INVALID-REF-12345",
                "case_id": TEST_CASE_ID,
                "feature_type": "grounds_of_merit"
            }
        )
        assert response.status_code == 404
    
    def test_payid_verify_no_auth(self):
        """POST /api/payments/payid/verify - no authentication"""
        response = requests.post(
            f"{BASE_URL}/api/payments/payid/verify",
            json={
                "reference": "ACM-12345678",
                "case_id": TEST_CASE_ID,
                "feature_type": "grounds_of_merit"
            }
        )
        assert response.status_code == 401


class TestPaymentPrices:
    """Test payment prices endpoint"""
    
    def test_get_prices(self):
        """GET /api/payments/prices - returns feature prices"""
        response = requests.get(f"{BASE_URL}/api/payments/prices")
        assert response.status_code == 200
        data = response.json()
        assert "prices" in data
        assert "currency" in data
        assert data["currency"] == "AUD"
        
        prices = data["prices"]
        assert "grounds_of_merit" in prices
        assert "full_report" in prices
        assert "extensive_report" in prices
        
        assert prices["grounds_of_merit"]["price"] == 99.0
        assert prices["full_report"]["price"] == 150.0
        assert prices["extensive_report"]["price"] == 200.0
        print(f"Prices: {prices}")


class TestTrialStatus:
    """Test trial status endpoint"""
    
    def test_get_trial_status(self, auth_headers):
        """GET /api/payments/trial-status - returns trial eligibility"""
        response = requests.get(
            f"{BASE_URL}/api/payments/trial-status",
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert "is_eligible" in data
        assert "trial_feature" in data
        assert data["trial_feature"] == "grounds_of_merit"
        print(f"Trial eligible: {data['is_eligible']}")
    
    def test_get_trial_status_no_auth(self):
        """GET /api/payments/trial-status - no authentication"""
        response = requests.get(f"{BASE_URL}/api/payments/trial-status")
        assert response.status_code == 401


class TestCasePayments:
    """Test case payments endpoint"""
    
    def test_get_case_payments(self, auth_headers):
        """GET /api/cases/{case_id}/payments - returns case payment info"""
        response = requests.get(
            f"{BASE_URL}/api/cases/{TEST_CASE_ID}/payments",
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert "payments" in data
        assert "unlocked_features" in data
        assert "latest_status_by_feature" in data
        
        # Admin user has all features unlocked
        unlocked = data["unlocked_features"]
        assert "grounds_of_merit" in unlocked
        assert "full_report" in unlocked
        assert "extensive_report" in unlocked
        print(f"Unlocked features: {unlocked}")
    
    def test_get_case_payments_no_auth(self):
        """GET /api/cases/{case_id}/payments - no authentication"""
        response = requests.get(f"{BASE_URL}/api/cases/{TEST_CASE_ID}/payments")
        assert response.status_code == 401


class TestHealthEndpoints:
    """Test health check endpoints"""
    
    def test_health(self):
        """GET /api/health - returns healthy status"""
        response = requests.get(f"{BASE_URL}/api/health")
        assert response.status_code == 200
        data = response.json()
        assert data.get("status") == "healthy"
    
    def test_ready(self):
        """GET /api/ready - returns ready status"""
        response = requests.get(f"{BASE_URL}/api/ready")
        assert response.status_code == 200
        data = response.json()
        assert data.get("ready") == True
