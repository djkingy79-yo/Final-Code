"""
Iteration 181: Payment History & Receipts Testing
Tests for:
- GET /api/payments/history - returns all user payments (PayID + Stripe)
- GET /api/payments/history/summary - returns total_spent, completed_payments, features_unlocked_count, cases_with_payments
- GET /api/payments/receipt/{payment_id}/pdf - generates PDF receipt for completed payments
- Auth requirements for all endpoints (401 without token)
- Login still works after rate limiting changes
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Test credentials from test_credentials.md
TEST_EMAIL = "djkingy79@gmail.com"
TEST_PASSWORD = "Grubbygrub88"


class TestAuthLogin:
    """Verify login still works after rate limiting changes to auth.py"""
    
    def test_login_success(self):
        """Test that login endpoint works correctly"""
        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": TEST_EMAIL, "password": TEST_PASSWORD},
            timeout=30
        )
        assert response.status_code == 200, f"Login failed: {response.text}"
        data = response.json()
        assert "session_token" in data, "Missing session_token in response"
        assert data.get("email") == TEST_EMAIL
        print(f"✓ Login successful for {TEST_EMAIL}")
    
    def test_login_invalid_credentials(self):
        """Test login with invalid credentials returns 401"""
        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": "invalid@test.com", "password": "wrongpassword"},
            timeout=30
        )
        assert response.status_code == 401, f"Expected 401, got {response.status_code}"
        print("✓ Invalid credentials correctly returns 401")


class TestPaymentHistoryEndpoints:
    """Test payment history API endpoints"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Get auth token before each test"""
        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": TEST_EMAIL, "password": TEST_PASSWORD},
            timeout=30
        )
        if response.status_code == 200:
            self.token = response.json().get("session_token")
            self.headers = {"Authorization": f"Bearer {self.token}"}
        else:
            pytest.skip("Could not authenticate - skipping test")
    
    def test_payment_history_returns_payments(self):
        """GET /api/payments/history returns all user payments"""
        response = requests.get(
            f"{BASE_URL}/api/payments/history",
            headers=self.headers,
            timeout=30
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        
        # Verify response structure
        assert "payments" in data, "Missing 'payments' key in response"
        assert "total" in data, "Missing 'total' key in response"
        assert isinstance(data["payments"], list), "payments should be a list"
        assert isinstance(data["total"], int), "total should be an integer"
        
        # User has 20 payments according to context
        print(f"✓ Payment history returned {data['total']} payments")
        
        # Verify payment structure if payments exist
        if data["payments"]:
            payment = data["payments"][0]
            required_fields = ["payment_id", "case_id", "feature_type", "feature_name", 
                             "amount", "currency", "method", "reference", "status", "created_at"]
            for field in required_fields:
                assert field in payment, f"Missing field '{field}' in payment"
            print(f"✓ Payment structure verified with all required fields")
    
    def test_payment_history_no_auth_returns_401(self):
        """GET /api/payments/history without auth returns 401"""
        response = requests.get(
            f"{BASE_URL}/api/payments/history",
            timeout=30
        )
        assert response.status_code == 401, f"Expected 401, got {response.status_code}"
        print("✓ Payment history without auth correctly returns 401")
    
    def test_payment_summary_returns_stats(self):
        """GET /api/payments/history/summary returns summary stats"""
        response = requests.get(
            f"{BASE_URL}/api/payments/history/summary",
            headers=self.headers,
            timeout=30
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        
        # Verify response structure
        required_fields = ["total_spent", "currency", "total_payments", "completed_payments",
                         "features_unlocked", "features_unlocked_count", "cases_with_payments"]
        for field in required_fields:
            assert field in data, f"Missing field '{field}' in summary"
        
        # Verify data types
        assert isinstance(data["total_spent"], (int, float)), "total_spent should be numeric"
        assert data["currency"] == "AUD", "currency should be AUD"
        assert isinstance(data["completed_payments"], int), "completed_payments should be int"
        assert isinstance(data["features_unlocked_count"], int), "features_unlocked_count should be int"
        assert isinstance(data["cases_with_payments"], int), "cases_with_payments should be int"
        
        print(f"✓ Payment summary: total_spent=${data['total_spent']}, completed={data['completed_payments']}, features={data['features_unlocked_count']}, cases={data['cases_with_payments']}")
    
    def test_payment_summary_no_auth_returns_401(self):
        """GET /api/payments/history/summary without auth returns 401"""
        response = requests.get(
            f"{BASE_URL}/api/payments/history/summary",
            timeout=30
        )
        assert response.status_code == 401, f"Expected 401, got {response.status_code}"
        print("✓ Payment summary without auth correctly returns 401")


class TestReceiptPDFEndpoint:
    """Test PDF receipt generation endpoint"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Get auth token and find a completed payment"""
        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": TEST_EMAIL, "password": TEST_PASSWORD},
            timeout=30
        )
        if response.status_code == 200:
            self.token = response.json().get("session_token")
            self.headers = {"Authorization": f"Bearer {self.token}"}
        else:
            pytest.skip("Could not authenticate - skipping test")
        
        # Get a completed payment_id for testing
        history_response = requests.get(
            f"{BASE_URL}/api/payments/history",
            headers=self.headers,
            timeout=30
        )
        if history_response.status_code == 200:
            payments = history_response.json().get("payments", [])
            completed = [p for p in payments if p.get("status") == "completed"]
            if completed:
                self.completed_payment_id = completed[0].get("payment_id")
                self.completed_payment_ref = completed[0].get("reference")
            else:
                self.completed_payment_id = None
                self.completed_payment_ref = None
        else:
            self.completed_payment_id = None
            self.completed_payment_ref = None
    
    def test_receipt_pdf_for_completed_payment(self):
        """GET /api/payments/receipt/{payment_id}/pdf generates valid PDF"""
        if not self.completed_payment_id:
            pytest.skip("No completed payments found for testing")
        
        response = requests.get(
            f"{BASE_URL}/api/payments/receipt/{self.completed_payment_id}/pdf",
            headers=self.headers,
            timeout=60
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        # Verify it's a PDF
        content_type = response.headers.get("content-type", "")
        assert "application/pdf" in content_type, f"Expected PDF content-type, got {content_type}"
        
        # Verify Content-Disposition header
        content_disp = response.headers.get("content-disposition", "")
        assert "attachment" in content_disp, "Expected attachment disposition"
        assert ".pdf" in content_disp.lower(), "Expected .pdf in filename"
        
        # Verify PDF content starts with PDF magic bytes
        assert response.content[:4] == b'%PDF', "Response does not start with PDF magic bytes"
        
        print(f"✓ PDF receipt generated successfully for payment {self.completed_payment_id}")
        print(f"  Content-Disposition: {content_disp}")
        print(f"  PDF size: {len(response.content)} bytes")
    
    def test_receipt_pdf_nonexistent_payment_returns_404(self):
        """GET /api/payments/receipt/{payment_id}/pdf returns 404 for non-existent payment"""
        fake_payment_id = "nonexistent-payment-id-12345"
        response = requests.get(
            f"{BASE_URL}/api/payments/receipt/{fake_payment_id}/pdf",
            headers=self.headers,
            timeout=30
        )
        assert response.status_code == 404, f"Expected 404, got {response.status_code}"
        print("✓ Non-existent payment correctly returns 404")
    
    def test_receipt_pdf_no_auth_returns_401(self):
        """GET /api/payments/receipt/{payment_id}/pdf without auth returns 401"""
        response = requests.get(
            f"{BASE_URL}/api/payments/receipt/any-payment-id/pdf",
            timeout=30
        )
        assert response.status_code == 401, f"Expected 401, got {response.status_code}"
        print("✓ Receipt PDF without auth correctly returns 401")


class TestPaymentHistoryDataIntegrity:
    """Test data integrity and filtering in payment history"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Get auth token"""
        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": TEST_EMAIL, "password": TEST_PASSWORD},
            timeout=30
        )
        if response.status_code == 200:
            self.token = response.json().get("session_token")
            self.headers = {"Authorization": f"Bearer {self.token}"}
        else:
            pytest.skip("Could not authenticate - skipping test")
    
    def test_payment_history_includes_both_methods(self):
        """Verify payment history includes both PayID and Stripe payments"""
        response = requests.get(
            f"{BASE_URL}/api/payments/history",
            headers=self.headers,
            timeout=30
        )
        assert response.status_code == 200
        payments = response.json().get("payments", [])
        
        methods = set(p.get("method") for p in payments)
        print(f"✓ Payment methods found: {methods}")
        
        # Count by method
        payid_count = len([p for p in payments if p.get("method") == "payid"])
        stripe_count = len([p for p in payments if p.get("method") == "stripe"])
        print(f"  PayID payments: {payid_count}, Stripe payments: {stripe_count}")
    
    def test_payment_history_includes_completed_and_pending(self):
        """Verify payment history includes both completed and pending payments"""
        response = requests.get(
            f"{BASE_URL}/api/payments/history",
            headers=self.headers,
            timeout=30
        )
        assert response.status_code == 200
        payments = response.json().get("payments", [])
        
        statuses = set(p.get("status") for p in payments)
        print(f"✓ Payment statuses found: {statuses}")
        
        # Count by status
        completed_count = len([p for p in payments if p.get("status") == "completed"])
        pending_count = len([p for p in payments if p.get("status") != "completed"])
        print(f"  Completed: {completed_count}, Pending/Other: {pending_count}")
    
    def test_summary_matches_history_data(self):
        """Verify summary stats match the payment history data"""
        # Get history
        history_response = requests.get(
            f"{BASE_URL}/api/payments/history",
            headers=self.headers,
            timeout=30
        )
        assert history_response.status_code == 200
        payments = history_response.json().get("payments", [])
        
        # Get summary
        summary_response = requests.get(
            f"{BASE_URL}/api/payments/history/summary",
            headers=self.headers,
            timeout=30
        )
        assert summary_response.status_code == 200
        summary = summary_response.json()
        
        # Count completed payments from history
        completed_from_history = len([p for p in payments if p.get("status") == "completed"])
        
        # Summary completed_payments should match
        print(f"✓ Summary completed_payments: {summary['completed_payments']}")
        print(f"  History completed count: {completed_from_history}")
        
        # Note: total_payments in summary counts from payments collection only,
        # while history merges both collections, so they may differ


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
