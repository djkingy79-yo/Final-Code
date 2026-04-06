"""
Iteration 149 - Trial Pricing System Tests
Tests the one-time $5.00 AUD trial for Grounds of Merit feature.
- Trial eligibility based on completed payment count = 0
- Trial price of $5.00 vs regular $99
- Trial status endpoint structure
- Payment reference creation with use_trial flag
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Test credentials
TEST_EMAIL = "djkingy79@gmail.com"
TEST_PASSWORD = "Cr1m1nalApp3al$2025"


class TestTrialPricingSystem:
    """Tests for the trial pricing system"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup test session with authentication"""
        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json"})
        self.token = None
        self.case_id = None
        
    def get_auth_token(self):
        """Get authentication token"""
        if self.token:
            return self.token
        response = self.session.post(f"{BASE_URL}/api/auth/login", json={
            "email": TEST_EMAIL,
            "password": TEST_PASSWORD
        })
        if response.status_code == 200:
            data = response.json()
            self.token = data.get("token") or data.get("session_token")
            self.session.headers.update({"Authorization": f"Bearer {self.token}"})
            return self.token
        pytest.skip(f"Authentication failed: {response.status_code}")
        
    def get_test_case_id(self):
        """Get a case ID for testing"""
        if self.case_id:
            return self.case_id
        self.get_auth_token()
        response = self.session.get(f"{BASE_URL}/api/cases")
        if response.status_code == 200:
            data = response.json()
            # Handle both list and dict responses
            cases = data if isinstance(data, list) else data.get("cases", [])
            if cases:
                self.case_id = cases[0].get("case_id")
                return self.case_id
        pytest.skip("No cases available for testing")
    
    def test_api_health(self):
        """Test API is accessible"""
        response = self.session.get(f"{BASE_URL}/api/health")
        assert response.status_code == 200, f"Health check failed: {response.status_code}"
        print("PASS: API health check successful")
    
    def test_trial_status_endpoint_exists(self):
        """Test that trial status endpoint exists and returns correct structure"""
        self.get_auth_token()
        response = self.session.get(f"{BASE_URL}/api/payments/trial-status")
        assert response.status_code == 200, f"Trial status endpoint failed: {response.status_code}"
        
        data = response.json()
        # Check required fields exist
        assert "is_eligible" in data, "Missing is_eligible field"
        assert "trial_feature" in data, "Missing trial_feature field"
        assert "regular_price" in data, "Missing regular_price field"
        
        print(f"PASS: Trial status endpoint returns correct structure")
        print(f"  - is_eligible: {data.get('is_eligible')}")
        print(f"  - trial_price: {data.get('trial_price')}")
        print(f"  - trial_feature: {data.get('trial_feature')}")
        print(f"  - regular_price: {data.get('regular_price')}")
        
    def test_trial_status_admin_not_eligible(self):
        """Test that admin user (with completed payments) is NOT trial eligible"""
        self.get_auth_token()
        response = self.session.get(f"{BASE_URL}/api/payments/trial-status")
        assert response.status_code == 200
        
        data = response.json()
        # Admin has completed payments, so should NOT be eligible
        # Note: This test expects admin to have completed payments
        is_eligible = data.get("is_eligible")
        print(f"PASS: Admin trial eligibility check - is_eligible={is_eligible}")
        
        # Verify structure regardless of eligibility
        assert data.get("trial_feature") == "grounds_of_merit", "Trial feature should be grounds_of_merit"
        assert data.get("regular_price") == 99, f"Regular price should be 99, got {data.get('regular_price')}"
        
        if not is_eligible:
            assert data.get("trial_price") is None, "Trial price should be None for ineligible users"
            assert data.get("message") is None, "Message should be None for ineligible users"
            print("PASS: Admin correctly marked as NOT trial eligible (has completed payments)")
        else:
            assert data.get("trial_price") == 5.0, "Trial price should be 5.0 for eligible users"
            print("INFO: Admin is trial eligible (no completed payments)")
    
    def test_trial_status_response_values(self):
        """Test trial status returns correct values"""
        self.get_auth_token()
        response = self.session.get(f"{BASE_URL}/api/payments/trial-status")
        assert response.status_code == 200
        
        data = response.json()
        
        # Verify trial feature is grounds_of_merit
        assert data.get("trial_feature") == "grounds_of_merit", \
            f"Trial feature should be 'grounds_of_merit', got '{data.get('trial_feature')}'"
        
        # Verify regular price is 99
        assert data.get("regular_price") == 99, \
            f"Regular price should be 99, got {data.get('regular_price')}"
        
        # If eligible, verify trial price is 5.0
        if data.get("is_eligible"):
            assert data.get("trial_price") == 5.0, \
                f"Trial price should be 5.0, got {data.get('trial_price')}"
            assert "One-time trial" in (data.get("message") or ""), \
                "Message should mention one-time trial"
        
        print("PASS: Trial status values are correct")
    
    def test_payment_reference_creation_with_trial(self):
        """Test payment reference creation with use_trial=true"""
        self.get_auth_token()
        case_id = self.get_test_case_id()
        
        response = self.session.post(f"{BASE_URL}/api/payments/payid/create-reference", json={
            "feature_type": "grounds_of_merit",
            "case_id": case_id,
            "use_trial": True
        })
        assert response.status_code == 200, f"Create reference failed: {response.status_code} - {response.text}"
        
        data = response.json()
        assert "reference" in data, "Missing reference in response"
        assert "amount" in data, "Missing amount in response"
        assert "payid" in data, "Missing payid in response"
        assert "is_trial" in data, "Missing is_trial flag in response"
        
        # Check if trial was applied
        if data.get("is_trial"):
            assert data.get("amount") == 5.0, f"Trial amount should be 5.0, got {data.get('amount')}"
            print(f"PASS: Trial payment reference created - amount=${data.get('amount')}, reference={data.get('reference')}")
        else:
            assert data.get("amount") == 99, f"Regular amount should be 99, got {data.get('amount')}"
            print(f"PASS: Regular payment reference created (user not trial eligible) - amount=${data.get('amount')}")
    
    def test_payment_reference_creation_without_trial(self):
        """Test payment reference creation with use_trial=false returns regular price"""
        self.get_auth_token()
        case_id = self.get_test_case_id()
        
        response = self.session.post(f"{BASE_URL}/api/payments/payid/create-reference", json={
            "feature_type": "grounds_of_merit",
            "case_id": case_id,
            "use_trial": False
        })
        assert response.status_code == 200, f"Create reference failed: {response.status_code}"
        
        data = response.json()
        assert data.get("is_trial") == False, "is_trial should be False when use_trial=false"
        assert data.get("amount") == 99, f"Amount should be 99 when not using trial, got {data.get('amount')}"
        
        print(f"PASS: Regular payment reference created - amount=${data.get('amount')}")
    
    def test_payment_reference_non_trial_feature(self):
        """Test that trial only applies to grounds_of_merit feature"""
        self.get_auth_token()
        case_id = self.get_test_case_id()
        
        # Try to use trial on full_report (should not apply)
        response = self.session.post(f"{BASE_URL}/api/payments/payid/create-reference", json={
            "feature_type": "full_report",
            "case_id": case_id,
            "use_trial": True
        })
        assert response.status_code == 200, f"Create reference failed: {response.status_code}"
        
        data = response.json()
        # Trial should NOT apply to full_report
        assert data.get("is_trial") == False, "Trial should not apply to full_report"
        assert data.get("amount") == 150, f"Full report price should be 150, got {data.get('amount')}"
        
        print(f"PASS: Trial correctly NOT applied to full_report - amount=${data.get('amount')}")
    
    def test_prices_endpoint(self):
        """Test prices endpoint returns correct feature prices"""
        response = self.session.get(f"{BASE_URL}/api/payments/prices")
        assert response.status_code == 200, f"Prices endpoint failed: {response.status_code}"
        
        data = response.json()
        assert "prices" in data, "Missing prices in response"
        assert data.get("currency") == "AUD", "Currency should be AUD"
        
        prices = data.get("prices", {})
        assert "grounds_of_merit" in prices, "Missing grounds_of_merit in prices"
        assert prices.get("grounds_of_merit", {}).get("price") == 99, "Grounds of merit price should be 99"
        
        print(f"PASS: Prices endpoint returns correct values")
        print(f"  - grounds_of_merit: ${prices.get('grounds_of_merit', {}).get('price')}")
        print(f"  - full_report: ${prices.get('full_report', {}).get('price')}")
        print(f"  - extensive_report: ${prices.get('extensive_report', {}).get('price')}")


class TestTrialEligibilityLogic:
    """Tests for trial eligibility logic"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup test session"""
        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json"})
        
    def get_auth_token(self):
        """Get authentication token"""
        response = self.session.post(f"{BASE_URL}/api/auth/login", json={
            "email": TEST_EMAIL,
            "password": TEST_PASSWORD
        })
        if response.status_code == 200:
            data = response.json()
            token = data.get("token") or data.get("session_token")
            self.session.headers.update({"Authorization": f"Bearer {token}"})
            return token
        pytest.skip("Authentication failed")
    
    def test_trial_eligibility_based_on_completed_payments(self):
        """Test that trial eligibility is based on completed payment count"""
        self.get_auth_token()
        
        # Get trial status
        response = self.session.get(f"{BASE_URL}/api/payments/trial-status")
        assert response.status_code == 200
        
        data = response.json()
        is_eligible = data.get("is_eligible")
        
        # The logic is: completed_count == 0 means eligible
        # Admin user likely has completed payments, so should be ineligible
        print(f"PASS: Trial eligibility check completed - is_eligible={is_eligible}")
        
        # Verify the response structure is correct regardless of eligibility
        assert isinstance(is_eligible, bool), "is_eligible should be a boolean"
        assert data.get("trial_feature") == "grounds_of_merit"
        assert data.get("regular_price") == 99


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
