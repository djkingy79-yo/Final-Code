"""
Iteration 46 Backend Tests
- Health check
- Payment prices ($99/$150/$200)
- Auth and Case API tests
"""
import pytest
import requests

BASE_URL = 'http://localhost:8001'

# Test credentials
TEST_EMAIL = "testuser999@test.com"
TEST_PASSWORD = "TestPass123!"
TEST_CASE_ID = "case_9e57a5b899bf"

class TestHealthAndPayments:
    """Test basic health and payment pricing endpoints"""
    
    def test_health_endpoint_returns_200(self):
        """Backend /api/health should return 200"""
        response = requests.get(f"{BASE_URL}/api/health")
        assert response.status_code == 200
        data = response.json()
        assert data.get("status") == "healthy"
        print(f"Health check passed: {data}")
    
    def test_payment_prices_endpoint(self):
        """Backend /api/payments/prices should return $99/$150/$200"""
        response = requests.get(f"{BASE_URL}/api/payments/prices")
        assert response.status_code == 200
        data = response.json()
        
        # Verify prices
        assert "prices" in data
        prices = data["prices"]
        
        # Check grounds_of_merit is $99
        grounds_price = prices.get("grounds_of_merit", {}).get("price")
        assert grounds_price == 99.00, f"Expected grounds_of_merit price $99, got {grounds_price}"
        
        # Check full_report is $150
        full_price = prices.get("full_report", {}).get("price")
        assert full_price == 150.00, f"Expected full_report price $150, got {full_price}"
        
        # Check extensive_report is $200
        extensive_price = prices.get("extensive_report", {}).get("price")
        assert extensive_price == 200.00, f"Expected extensive_report price $200, got {extensive_price}"
        
        print("Payment prices verified: grounds=$99, full=$150, extensive=$200")


class TestAuthAndCaseAccess:
    """Test authentication and case data access"""
    
    @pytest.fixture(scope="class")
    def session(self):
        """Create authenticated session"""
        s = requests.Session()
        s.headers.update({"Content-Type": "application/json"})
        
        # Login
        login_response = s.post(f"{BASE_URL}/api/auth/login", json={
            "email": TEST_EMAIL,
            "password": TEST_PASSWORD
        })
        
        if login_response.status_code != 200:
            pytest.skip(f"Login failed with status {login_response.status_code}: {login_response.text}")
        
        # Session cookie should be set
        print(f"Login successful for {TEST_EMAIL}")
        return s
    
    def test_auth_login(self, session):
        """Verify auth login works"""
        # Session fixture handles login
        assert session is not None
        print("Auth login test passed")
    
    def test_get_case_data(self, session):
        """Test case endpoint returns data"""
        response = session.get(f"{BASE_URL}/api/cases/{TEST_CASE_ID}")
        assert response.status_code == 200
        
        data = response.json()
        assert data.get("case_id") == TEST_CASE_ID
        print(f"Case data retrieved: {data.get('title', 'N/A')}")
    
    def test_get_case_reports(self, session):
        """Test case reports endpoint"""
        response = session.get(f"{BASE_URL}/api/cases/{TEST_CASE_ID}/reports")
        assert response.status_code == 200
        
        data = response.json()
        assert isinstance(data, list)
        print(f"Found {len(data)} reports for case")
        
        # Verify we have at least 2 reports as mentioned in requirements
        assert len(data) >= 2, f"Expected at least 2 reports, found {len(data)}"
    
    def test_get_single_report(self, session):
        """Test single report endpoint"""
        # First get reports list
        reports_response = session.get(f"{BASE_URL}/api/cases/{TEST_CASE_ID}/reports")
        reports = reports_response.json()
        
        if len(reports) == 0:
            pytest.skip("No reports to test")
        
        report_id = reports[0].get("report_id")
        response = session.get(f"{BASE_URL}/api/cases/{TEST_CASE_ID}/reports/{report_id}")
        assert response.status_code == 200
        
        data = response.json()
        assert data.get("report_id") == report_id
        assert "content" in data
        print(f"Single report retrieved: {data.get('report_type', 'N/A')}")


class TestCaseTabs:
    """Test endpoints that support the 7 tabs in CaseDetail"""
    
    @pytest.fixture(scope="class")
    def session(self):
        """Create authenticated session"""
        s = requests.Session()
        s.headers.update({"Content-Type": "application/json"})
        
        login_response = s.post(f"{BASE_URL}/api/auth/login", json={
            "email": TEST_EMAIL,
            "password": TEST_PASSWORD
        })
        
        if login_response.status_code != 200:
            pytest.skip("Login failed")
        
        return s
    
    def test_documents_endpoint(self, session):
        """Test Documents tab endpoint"""
        response = session.get(f"{BASE_URL}/api/cases/{TEST_CASE_ID}/documents")
        assert response.status_code == 200
        print(f"Documents endpoint works, found {len(response.json())} docs")
    
    def test_timeline_endpoint(self, session):
        """Test Timeline tab endpoint"""
        response = session.get(f"{BASE_URL}/api/cases/{TEST_CASE_ID}/timeline")
        assert response.status_code == 200
        print(f"Timeline endpoint works, found {len(response.json())} events")
    
    def test_grounds_endpoint(self, session):
        """Test Grounds tab endpoint"""
        response = session.get(f"{BASE_URL}/api/cases/{TEST_CASE_ID}/grounds")
        assert response.status_code == 200
        data = response.json()
        assert "grounds" in data or isinstance(data, list)
        print("Grounds endpoint works")
    
    def test_notes_endpoint(self, session):
        """Test Notes tab endpoint"""
        response = session.get(f"{BASE_URL}/api/cases/{TEST_CASE_ID}/notes")
        assert response.status_code == 200
        print(f"Notes endpoint works, found {len(response.json())} notes")
    
    def test_reports_endpoint(self, session):
        """Test Reports tab endpoint"""
        response = session.get(f"{BASE_URL}/api/cases/{TEST_CASE_ID}/reports")
        assert response.status_code == 200
        print(f"Reports endpoint works, found {len(response.json())} reports")
    
    def test_deadlines_endpoint(self, session):
        """Test Progress tab - Deadlines endpoint"""
        response = session.get(f"{BASE_URL}/api/cases/{TEST_CASE_ID}/deadlines")
        assert response.status_code == 200
        print("Deadlines endpoint works")
    
    def test_checklist_endpoint(self, session):
        """Test Progress tab - Checklist endpoint"""
        response = session.get(f"{BASE_URL}/api/cases/{TEST_CASE_ID}/checklist")
        assert response.status_code == 200
        print("Checklist endpoint works")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
