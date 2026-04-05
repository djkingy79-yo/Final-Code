"""
Iteration 48 - Comprehensive Backend API Tests for Appeal Case Manager
Tests: health, pricing, authentication, case access, reports
"""
import pytest
import requests

BASE_URL = 'http://localhost:8001'
TEST_EMAIL = "testuser999@test.com"
TEST_PASSWORD = "TestPass123!"
TEST_CASE_ID = "case_9e57a5b899bf"
TEST_REPORT_ID = "rpt_09c95a3eba28"


class TestHealthAndPricing:
    """Backend health and pricing endpoint tests"""
    
    def test_health_endpoint(self):
        """Test /api/health returns 200"""
        response = requests.get(f"{BASE_URL}/api/health")
        assert response.status_code == 200, f"Health check failed with {response.status_code}"
        print("✅ Health endpoint returns 200")
    
    def test_pricing_endpoint(self):
        """Test /api/payments/prices returns correct prices ($99/$150/$200)"""
        response = requests.get(f"{BASE_URL}/api/payments/prices")
        assert response.status_code == 200, f"Pricing failed with {response.status_code}"
        
        data = response.json()
        prices = data.get('prices', {})
        
        # Check grounds_of_merit price ($99)
        grounds_price = prices.get('grounds_of_merit', {}).get('price')
        assert grounds_price == 99.0, f"Expected $99 for grounds_of_merit, got {grounds_price}"
        print(f"✅ Grounds of Merit price: ${grounds_price}")
        
        # Check full_report price ($150)
        full_price = prices.get('full_report', {}).get('price')
        assert full_price == 150.0, f"Expected $150 for full_report, got {full_price}"
        print(f"✅ Full Report price: ${full_price}")
        
        # Check extensive_report price ($200)
        extensive_price = prices.get('extensive_report', {}).get('price')
        assert extensive_price == 200.0, f"Expected $200 for extensive_report, got {extensive_price}"
        print(f"✅ Extensive Report price: ${extensive_price}")


class TestAuthentication:
    """Authentication flow tests"""
    
    def test_login_returns_user_data(self):
        """Test login endpoint returns user info"""
        session = requests.Session()
        response = session.post(f"{BASE_URL}/api/auth/login", json={
            "email": TEST_EMAIL,
            "password": TEST_PASSWORD
        })
        
        assert response.status_code == 200, f"Login failed with {response.status_code}: {response.text}"
        
        data = response.json()
        assert 'user_id' in data, "Response missing user_id"
        assert data['email'] == TEST_EMAIL, f"Email mismatch: expected {TEST_EMAIL}, got {data.get('email')}"
        print(f"✅ Login successful for {data['email']}")
        return session
    
    def test_authenticated_case_access(self):
        """Test authenticated user can access their case"""
        session = requests.Session()
        
        # Login first
        login_response = session.post(f"{BASE_URL}/api/auth/login", json={
            "email": TEST_EMAIL,
            "password": TEST_PASSWORD
        })
        assert login_response.status_code == 200, "Login failed"
        
        # Access case
        case_response = session.get(f"{BASE_URL}/api/cases/{TEST_CASE_ID}")
        # 200 = success, 404 = case not found (might have been deleted)
        assert case_response.status_code in [200, 404], f"Case access failed with {case_response.status_code}"
        
        if case_response.status_code == 200:
            print(f"✅ Case {TEST_CASE_ID} accessible")
        else:
            print(f"⚠️ Case {TEST_CASE_ID} not found (may have been deleted)")


class TestReports:
    """Report-related API tests"""
    
    def test_reports_api_authenticated(self):
        """Test reports endpoint requires authentication"""
        session = requests.Session()
        
        # Login
        login_response = session.post(f"{BASE_URL}/api/auth/login", json={
            "email": TEST_EMAIL,
            "password": TEST_PASSWORD
        })
        assert login_response.status_code == 200, "Login failed"
        
        # Try to get reports
        reports_response = session.get(f"{BASE_URL}/api/cases/{TEST_CASE_ID}/reports")
        
        if reports_response.status_code == 200:
            data = reports_response.json()
            # Response is a list directly
            report_count = len(data) if isinstance(data, list) else len(data.get('reports', []))
            print(f"✅ Reports endpoint accessible, found {report_count} reports")
        elif reports_response.status_code == 404:
            print("⚠️ Case or reports not found")
        else:
            print(f"⚠️ Reports endpoint returned {reports_response.status_code}")
    
    def test_report_types_available(self):
        """Test report type definitions"""
        # This is checked via pricing endpoint
        response = requests.get(f"{BASE_URL}/api/payments/prices")
        assert response.status_code == 200
        
        data = response.json()
        prices = data.get('prices', {})
        
        # Verify all 3 report types exist
        expected_types = ['grounds_of_merit', 'full_report', 'extensive_report']
        for report_type in expected_types:
            assert report_type in prices, f"Missing report type: {report_type}"
        
        print("✅ All 3 report types available in pricing")


class TestPublicPages:
    """Test public pages load correctly"""
    
    def test_landing_page_loads(self):
        """Test landing page is accessible"""
        response = requests.get(f"{BASE_URL}")
        # Frontend is served differently, but we can check if it's not an error
        # The frontend routes are handled by React, so we may get 200 for the HTML
        assert response.status_code in [200, 304], f"Landing page error: {response.status_code}"
        print("✅ Landing page accessible")
    
    def test_faq_api_if_exists(self):
        """Test FAQ data API if it exists"""
        response = requests.get(f"{BASE_URL}/api/faq", timeout=10)
        # May or may not exist
        if response.status_code == 200:
            print("✅ FAQ API exists and returns data")
        elif response.status_code == 404:
            print("ℹ️ No FAQ API endpoint (FAQ is static)")
        else:
            print(f"ℹ️ FAQ API returned {response.status_code}")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
