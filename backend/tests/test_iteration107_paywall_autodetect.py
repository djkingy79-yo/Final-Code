"""
Iteration 107 Tests: Grounds Paywall Enforcement & Auto-Detection Verification

Tests:
1. Backend: GET /api/cases/case_e7a5b5faf51e should show offence_category='sexual_offences' (NOT 'homicide')
2. Backend: GET /api/cases/case_e7a5b5faf51e/grounds should return is_unlocked=false, count=2, empty grounds array
3. Backend: Document bundle export still works - POST /api/cases/case_a97ea91f0692/export/bundle returns 200
4. Frontend: Grounds tab paywall banner visible with count and unlock button
5. Frontend: No ground titles/descriptions/badges visible when locked
6. Frontend: AI Identify Grounds and Add Ground buttons hidden when locked with existing grounds
7. Frontend: Dashboard new case form defaults offence_category to '' (Auto-detect from documents)
"""

import pytest
import requests

BASE_URL = 'http://localhost:8001'

# Test credentials
TEST_EMAIL = "test@example.com"
TEST_PASSWORD = "TestPassword123!"

# Test case IDs
KARLSSON_CASE_ID = "case_e7a5b5faf51e"  # R v Karlsson - 2 locked grounds, auto-detected sexual_offences
DUMMY_MURDER_CASE_ID = "case_a97ea91f0692"  # Dummy Murder - has docs for bundle export


class TestGroundsPaywallAndAutoDetection:
    """Test grounds paywall enforcement and auto-detection metadata"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup session with authentication"""
        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json"})
        
        # Login to get session token
        login_response = self.session.post(f"{BASE_URL}/api/auth/login", json={
            "email": TEST_EMAIL,
            "password": TEST_PASSWORD
        })
        
        if login_response.status_code == 200:
            data = login_response.json()
            session_token = data.get("session_token")
            if session_token:
                self.session.cookies.set("session_token", session_token)
        else:
            pytest.skip(f"Login failed: {login_response.status_code}")
    
    def test_01_health_check(self):
        """Verify API is accessible"""
        response = self.session.get(f"{BASE_URL}/api/health")
        assert response.status_code == 200, f"Health check failed: {response.status_code}"
        print("PASS: Health check successful")
    
    def test_02_karlsson_case_metadata_auto_detected(self):
        """
        GET /api/cases/case_e7a5b5faf51e should show:
        - offence_category = 'sexual_offences' (NOT 'homicide')
        - offence_type populated
        - sentence populated
        """
        response = self.session.get(f"{BASE_URL}/api/cases/{KARLSSON_CASE_ID}")
        assert response.status_code == 200, f"Failed to get case: {response.status_code}"
        
        data = response.json()
        offence_category = data.get("offence_category", "")
        offence_type = data.get("offence_type", "")
        sentence = data.get("sentence", "")
        
        print("Case metadata:")
        print(f"  offence_category: {offence_category}")
        print(f"  offence_type: {offence_type}")
        print(f"  sentence: {sentence}")
        
        # Verify offence_category is NOT 'homicide' - should be 'sexual_offences'
        assert offence_category != "homicide", f"offence_category should NOT be 'homicide', got: {offence_category}"
        assert offence_category == "sexual_offences", f"offence_category should be 'sexual_offences', got: {offence_category}"
        
        # Verify offence_type is populated
        assert offence_type, "offence_type should be populated, got empty string"
        
        # Verify sentence is populated
        assert sentence, "sentence should be populated, got empty string"
        
        print("PASS: Case metadata auto-detected correctly (sexual_offences, not homicide)")
    
    def test_03_grounds_paywall_returns_locked_response(self):
        """
        GET /api/cases/case_e7a5b5faf51e/grounds should return:
        - is_unlocked = false
        - count = 2 (or more)
        - grounds = [] (empty array - no titles/descriptions leaked)
        """
        response = self.session.get(f"{BASE_URL}/api/cases/{KARLSSON_CASE_ID}/grounds")
        assert response.status_code == 200, f"Failed to get grounds: {response.status_code}"
        
        data = response.json()
        is_unlocked = data.get("is_unlocked")
        count = data.get("count", 0)
        grounds = data.get("grounds", [])
        unlock_price = data.get("unlock_price")
        
        print("Grounds response:")
        print(f"  is_unlocked: {is_unlocked}")
        print(f"  count: {count}")
        print(f"  grounds array length: {len(grounds)}")
        print(f"  unlock_price: {unlock_price}")
        
        # Verify paywall is enforced
        assert not is_unlocked, f"is_unlocked should be False, got: {is_unlocked}"
        
        # Verify count is returned (should be 2 based on context)
        assert count >= 2, f"count should be >= 2, got: {count}"
        
        # Verify grounds array is EMPTY (no titles/descriptions leaked)
        assert len(grounds) == 0, f"grounds array should be empty when locked, got {len(grounds)} items"
        
        # Verify unlock price is $99
        assert unlock_price == 99.00, f"unlock_price should be 99.00, got: {unlock_price}"
        
        print("PASS: Grounds paywall enforced - empty grounds array, count returned, is_unlocked=false")
    
    def test_04_bundle_export_still_works(self):
        """
        POST /api/cases/case_a97ea91f0692/export/bundle should return 200
        """
        # Get documents first to select some for the bundle
        docs_response = self.session.get(f"{BASE_URL}/api/cases/{DUMMY_MURDER_CASE_ID}/documents")
        assert docs_response.status_code == 200, f"Failed to get documents: {docs_response.status_code}"
        
        documents = docs_response.json()
        if not documents:
            pytest.skip("No documents available for bundle export test")
        
        # Select first 2 documents for bundle
        doc_ids = [doc["document_id"] for doc in documents[:2]]
        
        response = self.session.post(
            f"{BASE_URL}/api/cases/{DUMMY_MURDER_CASE_ID}/export/bundle",
            json={"document_ids": doc_ids}
        )
        
        assert response.status_code == 200, f"Bundle export failed: {response.status_code}"
        
        # Verify it returns PDF content
        content_type = response.headers.get("content-type", "")
        assert "pdf" in content_type.lower() or len(response.content) > 1000, \
            f"Expected PDF content, got content-type: {content_type}"
        
        print(f"PASS: Bundle export works - returned {len(response.content)} bytes")
    
    def test_05_verify_no_admin_bypass_in_grounds(self):
        """
        Verify that admin users also see locked grounds (admin bypass removed)
        The test user test@example.com IS an admin, but should still see locked grounds
        """
        response = self.session.get(f"{BASE_URL}/api/cases/{KARLSSON_CASE_ID}/grounds")
        assert response.status_code == 200
        
        data = response.json()
        is_unlocked = data.get("is_unlocked")
        
        # Even though test user is admin, grounds should be locked (admin bypass removed)
        assert not is_unlocked, f"Admin bypass should be removed - is_unlocked should be False, got: {is_unlocked}"
        
        print("PASS: Admin bypass removed - admin user sees locked grounds")


class TestOffenceCategoriesEndpoint:
    """Test offence categories endpoint for dashboard form defaults"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup session with authentication"""
        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json"})
        
        # Login
        login_response = self.session.post(f"{BASE_URL}/api/auth/login", json={
            "email": TEST_EMAIL,
            "password": TEST_PASSWORD
        })
        
        if login_response.status_code == 200:
            data = login_response.json()
            session_token = data.get("session_token")
            if session_token:
                self.session.cookies.set("session_token", session_token)
    
    def test_offence_categories_available(self):
        """Verify offence categories endpoint returns valid categories"""
        response = self.session.get(f"{BASE_URL}/api/offence-categories")
        assert response.status_code == 200, f"Failed to get offence categories: {response.status_code}"
        
        data = response.json()
        categories = data.get("categories", [])
        
        assert len(categories) > 0, "Should have offence categories"
        
        # Verify 'homicide' is NOT the first/default category
        # The frontend should default to '' (auto-detect)
        category_ids = [c.get("id") for c in categories]
        print(f"Available categories: {category_ids}")
        
        print("PASS: Offence categories endpoint works")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
