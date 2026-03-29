"""
Iteration 46 Backend API Tests
Tests for critical backend endpoints:
- /api/health returns 200
- /api/payments/prices returns $99/$150/$200
- Auth and case endpoints working
"""
import pytest
import requests
import os

BASE_URL = 'http://localhost:8001'

class TestHealthEndpoint:
    """Health check endpoint tests"""
    
    def test_api_health_returns_200(self):
        """Test that /api/health returns 200 with healthy status"""
        response = requests.get(f"{BASE_URL}/api/health", timeout=10)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        data = response.json()
        assert data.get("status") == "healthy", f"Expected status=healthy, got {data}"
        print(f"Health check passed: {data}")


class TestPaymentPrices:
    """Payment pricing endpoint tests"""
    
    def test_payments_prices_returns_correct_values(self):
        """Test that /api/payments/prices returns $99/$150/$200"""
        response = requests.get(f"{BASE_URL}/api/payments/prices", timeout=10)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        data = response.json()
        
        # Prices are nested under 'prices' key
        prices = data.get("prices", data)  # Handle both structures
        
        # Check grounds_of_merit price = $99
        assert "grounds_of_merit" in prices, "Missing grounds_of_merit in prices"
        assert prices["grounds_of_merit"]["price"] == 99.0, f"Expected $99, got {prices['grounds_of_merit']['price']}"
        
        # Check full_report price = $150
        assert "full_report" in prices, "Missing full_report in prices"
        assert prices["full_report"]["price"] == 150.0, f"Expected $150, got {prices['full_report']['price']}"
        
        # Check extensive_report price = $200
        assert "extensive_report" in prices, "Missing extensive_report in prices"
        assert prices["extensive_report"]["price"] == 200.0, f"Expected $200, got {prices['extensive_report']['price']}"
        
        print(f"Payment prices verified: Grounds=$99, Full=$150, Extensive=$200")


class TestAuthAndCaseAccess:
    """Test authentication and case access"""
    
    def test_login_with_test_credentials(self):
        """Test login with testuser999@test.com / TestPass123!"""
        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": "testuser999@test.com", "password": "TestPass123!"},
            timeout=10
        )
        assert response.status_code == 200, f"Login failed with status {response.status_code}: {response.text}"
        data = response.json()
        assert "user_id" in data, "Missing user_id in login response"
        assert "email" in data, "Missing email in login response"
        print(f"Login successful: {data.get('email')}")
    
    def test_case_access_requires_auth(self):
        """Test that case access returns 401 without auth"""
        response = requests.get(f"{BASE_URL}/api/cases", timeout=10)
        assert response.status_code == 401, f"Expected 401, got {response.status_code}"
        print("Unauthenticated case access correctly returns 401")
    
    def test_case_access_with_session(self):
        """Test case access with authenticated session"""
        session = requests.Session()
        
        # Login first
        login_resp = session.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": "testuser999@test.com", "password": "TestPass123!"},
            timeout=10
        )
        assert login_resp.status_code == 200, f"Login failed: {login_resp.text}"
        
        # Access cases
        cases_resp = session.get(f"{BASE_URL}/api/cases", timeout=10)
        assert cases_resp.status_code == 200, f"Cases access failed: {cases_resp.text}"
        cases = cases_resp.json()
        print(f"Successfully retrieved {len(cases)} cases")
    
    def test_specific_case_access(self):
        """Test access to case_9e57a5b899bf"""
        session = requests.Session()
        
        # Login
        login_resp = session.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": "testuser999@test.com", "password": "TestPass123!"},
            timeout=10
        )
        assert login_resp.status_code == 200, f"Login failed"
        
        # Access specific case
        case_id = "case_9e57a5b899bf"
        case_resp = session.get(f"{BASE_URL}/api/cases/{case_id}", timeout=10)
        assert case_resp.status_code == 200, f"Case access failed with {case_resp.status_code}: {case_resp.text}"
        case_data = case_resp.json()
        assert case_data.get("case_id") == case_id
        print(f"Successfully accessed case: {case_data.get('title')}")
    
    def test_report_access(self):
        """Test access to report rpt_09c95a3eba28"""
        session = requests.Session()
        
        # Login
        login_resp = session.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": "testuser999@test.com", "password": "TestPass123!"},
            timeout=10
        )
        assert login_resp.status_code == 200, f"Login failed"
        
        # Access specific report
        case_id = "case_9e57a5b899bf"
        report_id = "rpt_09c95a3eba28"
        report_resp = session.get(f"{BASE_URL}/api/cases/{case_id}/reports/{report_id}", timeout=10)
        assert report_resp.status_code == 200, f"Report access failed with {report_resp.status_code}: {report_resp.text}"
        report_data = report_resp.json()
        assert report_data.get("report_id") == report_id
        print(f"Successfully accessed report: {report_data.get('report_type')}")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
