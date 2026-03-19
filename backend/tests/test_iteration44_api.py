"""
Iteration 44 API Tests for Appeal Case Manager
Tests: Health check, pricing, user auth, case creation, report generation
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://barrister-toolkit.preview.emergentagent.com').rstrip('/')

# Test user credentials
TEST_EMAIL = "testuser999@test.com"
TEST_PASSWORD = "TestPass123!"


class TestPublicEndpoints:
    """Public endpoints that don't require authentication"""
    
    def test_health_check(self):
        """Test /api/health returns 200 with healthy status"""
        response = requests.get(f"{BASE_URL}/api/health")
        assert response.status_code == 200, f"Health check failed: {response.text}"
        data = response.json()
        assert data.get("status") == "healthy", f"Unexpected status: {data}"
        assert "timestamp" in data, "Missing timestamp in health response"
        print(f"✓ Health check passed: {data['status']}")
    
    def test_payment_prices(self):
        """Test /api/payments/prices returns correct prices ($99, $150, $200)"""
        response = requests.get(f"{BASE_URL}/api/payments/prices")
        assert response.status_code == 200, f"Prices endpoint failed: {response.text}"
        data = response.json()
        
        # Verify price structure
        prices = data.get("prices", {})
        assert "grounds_of_merit" in prices, "Missing grounds_of_merit price"
        assert "full_report" in prices, "Missing full_report price"
        assert "extensive_report" in prices, "Missing extensive_report price"
        
        # Verify exact prices
        assert prices["grounds_of_merit"]["price"] == 99.0, f"Wrong grounds_of_merit price: {prices['grounds_of_merit']}"
        assert prices["full_report"]["price"] == 150.0, f"Wrong full_report price: {prices['full_report']}"
        assert prices["extensive_report"]["price"] == 200.0, f"Wrong extensive_report price: {prices['extensive_report']}"
        
        # Verify currency
        assert data.get("currency") == "AUD", f"Wrong currency: {data.get('currency')}"
        print(f"✓ Prices correct: $99 (grounds), $150 (full), $200 (extensive)")
    
    def test_states_endpoint(self):
        """Test /api/states returns Australian states"""
        response = requests.get(f"{BASE_URL}/api/states")
        assert response.status_code == 200, f"States endpoint failed: {response.text}"
        data = response.json()
        assert "states" in data, "Missing states in response"
        assert len(data["states"]) == 8, f"Expected 8 states, got {len(data['states'])}"
        print(f"✓ States endpoint returned {len(data['states'])} states")
    
    def test_offence_categories(self):
        """Test /api/offence-categories returns offence types"""
        response = requests.get(f"{BASE_URL}/api/offence-categories")
        assert response.status_code == 200, f"Offence categories failed: {response.text}"
        data = response.json()
        assert "categories" in data, "Missing categories in response"
        assert len(data["categories"]) >= 10, f"Expected at least 10 categories, got {len(data['categories'])}"
        print(f"✓ Offence categories endpoint returned {len(data['categories'])} categories")


class TestAuthentication:
    """Test authentication flow with test user"""
    
    @pytest.fixture
    def session(self):
        """Create requests session for cookie handling"""
        return requests.Session()
    
    def test_login_with_email(self, session):
        """Test login with existing test user"""
        response = session.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": TEST_EMAIL, "password": TEST_PASSWORD}
        )
        
        assert response.status_code == 200, f"Login failed: {response.status_code} - {response.text}"
        data = response.json()
        assert "user_id" in data, f"Missing user_id in login response: {data}"
        print(f"✓ Login successful for {TEST_EMAIL}")
        return session
    
    def test_get_user_profile_after_login(self, session):
        """Test getting user profile after login"""
        # First login
        login_response = session.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": TEST_EMAIL, "password": TEST_PASSWORD}
        )
        assert login_response.status_code == 200, f"Login failed: {login_response.text}"
        
        # Then get profile
        profile_response = session.get(f"{BASE_URL}/api/auth/me")
        assert profile_response.status_code == 200, f"Profile fetch failed: {profile_response.text}"
        
        data = profile_response.json()
        assert data.get("email") == TEST_EMAIL, f"Wrong email in profile: {data}"
        print(f"✓ User profile retrieved: {data.get('email')}")


class TestCaseManagement:
    """Test case CRUD operations"""
    
    @pytest.fixture
    def auth_session(self):
        """Create authenticated session"""
        session = requests.Session()
        response = session.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": TEST_EMAIL, "password": TEST_PASSWORD}
        )
        if response.status_code != 200:
            pytest.skip(f"Login failed - skipping authenticated tests: {response.text}")
        return session
    
    def test_get_cases(self, auth_session):
        """Test getting user's cases"""
        response = auth_session.get(f"{BASE_URL}/api/cases")
        assert response.status_code == 200, f"Get cases failed: {response.text}"
        data = response.json()
        assert isinstance(data, list), f"Expected list of cases, got: {type(data)}"
        print(f"✓ Retrieved {len(data)} cases")
    
    def test_create_case_drug_offences_nsw(self, auth_session):
        """Test creating a new case with drug_offences category in NSW"""
        case_data = {
            "title": "TEST_Iteration44_Case",
            "defendant_name": "Test Defendant 44",
            "state": "nsw",
            "offence_category": "drug_offences",
            "offence_type": "Supply prohibited drug",
            "case_number": "TEST/2026/44",
            "court": "District Court",
            "summary": "Test case for iteration 44 API testing"
        }
        
        response = auth_session.post(f"{BASE_URL}/api/cases", json=case_data)
        assert response.status_code == 200, f"Create case failed: {response.text}"
        
        data = response.json()
        assert "case_id" in data, f"Missing case_id in response: {data}"
        assert data.get("offence_category") == "drug_offences", f"Wrong offence_category: {data}"
        assert data.get("state") == "nsw", f"Wrong state: {data}"
        
        print(f"✓ Created case: {data.get('case_id')}")
        return data.get("case_id")


class TestExistingCase:
    """Test operations on existing case (case_9e57a5b899bf)"""
    
    EXISTING_CASE_ID = "case_9e57a5b899bf"
    
    @pytest.fixture
    def auth_session(self):
        """Create authenticated session"""
        session = requests.Session()
        response = session.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": TEST_EMAIL, "password": TEST_PASSWORD}
        )
        if response.status_code != 200:
            pytest.skip(f"Login failed: {response.text}")
        return session
    
    def test_get_existing_case(self, auth_session):
        """Test fetching existing case"""
        response = auth_session.get(f"{BASE_URL}/api/cases/{self.EXISTING_CASE_ID}")
        
        # Case may or may not exist anymore
        if response.status_code == 404:
            pytest.skip("Existing test case not found - may have been cleaned up")
        
        assert response.status_code == 200, f"Get case failed: {response.text}"
        data = response.json()
        assert data.get("case_id") == self.EXISTING_CASE_ID
        print(f"✓ Retrieved case: {data.get('title')}")
    
    def test_get_case_reports(self, auth_session):
        """Test fetching reports for existing case"""
        response = auth_session.get(f"{BASE_URL}/api/cases/{self.EXISTING_CASE_ID}/reports")
        
        if response.status_code == 404:
            pytest.skip("Existing test case not found")
        
        assert response.status_code == 200, f"Get reports failed: {response.text}"
        data = response.json()
        assert isinstance(data, list), f"Expected list of reports, got: {type(data)}"
        print(f"✓ Retrieved {len(data)} reports for case")
        
        # Check if any reports have proper content structure
        for report in data:
            if report.get("content"):
                content = report.get("content")
                # Reports should have analysis field (from fix)
                if isinstance(content, dict) and "analysis" in content:
                    print(f"  - Report {report.get('report_id')}: Has analysis field ✓")


class TestReportGeneration:
    """Test report generation via API - verifies content.analysis structure"""
    
    @pytest.fixture
    def auth_session(self):
        """Create authenticated session"""
        session = requests.Session()
        response = session.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": TEST_EMAIL, "password": TEST_PASSWORD}
        )
        if response.status_code != 200:
            pytest.skip(f"Login failed: {response.text}")
        return session
    
    def test_report_content_structure(self, auth_session):
        """Verify reports have content.analysis structure for Markdown rendering"""
        # Get all cases
        cases_response = auth_session.get(f"{BASE_URL}/api/cases")
        if cases_response.status_code != 200:
            pytest.skip("Could not get cases")
        
        cases = cases_response.json()
        if not cases:
            pytest.skip("No cases found for user")
        
        # Find a case with reports
        for case in cases:
            case_id = case.get("case_id")
            reports_response = auth_session.get(f"{BASE_URL}/api/cases/{case_id}/reports")
            
            if reports_response.status_code == 200:
                reports = reports_response.json()
                if reports:
                    report = reports[0]
                    content = report.get("content")
                    
                    # Verify the content structure matches what frontend expects
                    if isinstance(content, dict):
                        if "analysis" in content:
                            analysis = content.get("analysis", "")
                            print(f"✓ Report {report.get('report_id')} has content.analysis ({len(analysis)} chars)")
                            assert len(analysis) > 0, "Analysis should not be empty"
                            return
                    elif isinstance(content, str):
                        print(f"✓ Report {report.get('report_id')} has string content ({len(content)} chars)")
                        return
        
        print("No reports found with content to validate")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
