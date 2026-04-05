"""
Iteration 139 - Grounds Dedup Fix Verification Tests
Tests that:
1. grounds.py _classify_pipeline_issues uses fuzzy dedup (imports ground_dedup)
2. grounds.py _sync_pipeline_issues_to_grounds uses fuzzy dedup (imports ground_dedup)
3. /api/cases/{case_id}/grounds/auto-identify endpoint works
4. Calling auto-identify twice does NOT create duplicate grounds
"""
import pytest
import requests
import os
import time

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Test credentials
TEST_EMAIL = "test@example.com"
TEST_PASSWORD = "TestPassword123!"
TEST_CASE_ID = "case_f8bf63e9dcbe"  # Homann v R case with documents


class TestGroundsDedupFix:
    """Tests for the grounds deduplication fix in grounds.py"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Get auth token before each test"""
        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json"})
        
        # Login to get token
        login_response = self.session.post(f"{BASE_URL}/api/auth/login", json={
            "email": TEST_EMAIL,
            "password": TEST_PASSWORD
        })
        assert login_response.status_code == 200, f"Login failed: {login_response.text}"
        
        data = login_response.json()
        token = data.get("session_token") or data.get("token")
        assert token, "No token in login response"
        
        self.session.headers.update({"Authorization": f"Bearer {token}"})
        yield
    
    def test_health_endpoint(self):
        """Test that the API is healthy"""
        response = self.session.get(f"{BASE_URL}/api/health")
        assert response.status_code == 200
        print("✓ Health endpoint working")
    
    def test_auth_me_works(self):
        """Test that auth/me returns user info"""
        response = self.session.get(f"{BASE_URL}/api/auth/me")
        assert response.status_code == 200
        data = response.json()
        assert data.get("email") == TEST_EMAIL
        print(f"✓ Auth working for {TEST_EMAIL}")
    
    def test_get_case_exists(self):
        """Test that the test case exists"""
        response = self.session.get(f"{BASE_URL}/api/cases/{TEST_CASE_ID}")
        assert response.status_code == 200
        data = response.json()
        assert data.get("case_id") == TEST_CASE_ID
        print(f"✓ Case {TEST_CASE_ID} exists: {data.get('case_name', 'Unknown')}")
    
    def test_get_grounds_before_auto_identify(self):
        """Get current grounds count before running auto-identify"""
        response = self.session.get(f"{BASE_URL}/api/cases/{TEST_CASE_ID}/grounds")
        assert response.status_code == 200
        data = response.json()
        
        grounds = data.get("grounds", [])
        count = data.get("count", len(grounds))
        print(f"✓ Current grounds count: {count}")
        
        # Store for later comparison
        self.initial_grounds_count = count
        return count
    
    def test_auto_identify_endpoint_exists(self):
        """Test that the auto-identify endpoint exists and responds"""
        response = self.session.post(f"{BASE_URL}/api/cases/{TEST_CASE_ID}/grounds/auto-identify")
        # Should return 200 or 400 (if no documents), not 404
        assert response.status_code in [200, 400], f"Unexpected status: {response.status_code} - {response.text}"
        print(f"✓ Auto-identify endpoint exists, status: {response.status_code}")
        return response
    
    def test_auto_identify_returns_dedup_info(self):
        """Test that auto-identify returns skipped_duplicates field (proves dedup is running)"""
        response = self.session.post(f"{BASE_URL}/api/cases/{TEST_CASE_ID}/grounds/auto-identify")
        
        if response.status_code == 400:
            # No documents case - skip
            pytest.skip("No documents available for analysis")
        
        assert response.status_code == 200, f"Auto-identify failed: {response.text}"
        data = response.json()
        
        # The response should include dedup info
        assert "identified_count" in data, "Missing identified_count in response"
        assert "skipped_duplicates" in data, "Missing skipped_duplicates in response (proves dedup is running)"
        
        print(f"✓ Auto-identify response: identified={data.get('identified_count')}, skipped_duplicates={data.get('skipped_duplicates')}")
        return data
    
    def test_auto_identify_twice_no_duplicates(self):
        """CRITICAL TEST: Calling auto-identify twice should NOT create duplicate grounds"""
        # Get initial count
        response1 = self.session.get(f"{BASE_URL}/api/cases/{TEST_CASE_ID}/grounds")
        assert response1.status_code == 200
        initial_count = response1.json().get("count", 0)
        print(f"Initial grounds count: {initial_count}")
        
        # First auto-identify call
        auto1 = self.session.post(f"{BASE_URL}/api/cases/{TEST_CASE_ID}/grounds/auto-identify")
        if auto1.status_code == 400:
            pytest.skip("No documents available for analysis")
        
        assert auto1.status_code == 200, f"First auto-identify failed: {auto1.text}"
        data1 = auto1.json()
        print(f"First auto-identify: identified={data1.get('identified_count')}, skipped={data1.get('skipped_duplicates')}")
        
        # Get count after first call
        response2 = self.session.get(f"{BASE_URL}/api/cases/{TEST_CASE_ID}/grounds")
        count_after_first = response2.json().get("count", 0)
        print(f"Grounds count after first call: {count_after_first}")
        
        # Wait a moment
        time.sleep(1)
        
        # Second auto-identify call
        auto2 = self.session.post(f"{BASE_URL}/api/cases/{TEST_CASE_ID}/grounds/auto-identify")
        assert auto2.status_code == 200, f"Second auto-identify failed: {auto2.text}"
        data2 = auto2.json()
        print(f"Second auto-identify: identified={data2.get('identified_count')}, skipped={data2.get('skipped_duplicates')}")
        
        # Get count after second call
        response3 = self.session.get(f"{BASE_URL}/api/cases/{TEST_CASE_ID}/grounds")
        count_after_second = response3.json().get("count", 0)
        print(f"Grounds count after second call: {count_after_second}")
        
        # CRITICAL: Count should NOT increase on second call (dedup should prevent duplicates)
        assert count_after_second == count_after_first, \
            f"DEDUP FAILED! Grounds multiplied from {count_after_first} to {count_after_second}"
        
        # Second call should report skipped_duplicates > 0 or identified_count = 0
        # (since all grounds already exist)
        print(f"✓ DEDUP WORKING: Grounds count stable at {count_after_second}")


class TestGroundsDedupCodeStructure:
    """Tests that verify the code structure has the correct imports and function calls"""
    
    def test_grounds_py_imports_ground_dedup(self):
        """Verify grounds.py imports from ground_dedup module"""
        grounds_file = "/app/backend/routers/grounds.py"
        
        with open(grounds_file, 'r') as f:
            content = f.read()
        
        # Check for imports in _classify_pipeline_issues
        assert "from services.ground_dedup import" in content, \
            "grounds.py missing import from services.ground_dedup"
        
        assert "is_ground_duplicate" in content, \
            "grounds.py missing is_ground_duplicate function call"
        
        assert "normalise_au_spelling" in content, \
            "grounds.py missing normalise_au_spelling function call"
        
        print("✓ grounds.py has correct imports from ground_dedup")
    
    def test_classify_pipeline_issues_uses_fuzzy_dedup(self):
        """Verify _classify_pipeline_issues uses fuzzy dedup, not exact-title match"""
        grounds_file = "/app/backend/routers/grounds.py"
        
        with open(grounds_file, 'r') as f:
            content = f.read()
        
        # Find the _classify_pipeline_issues function
        assert "async def _classify_pipeline_issues" in content, \
            "_classify_pipeline_issues function not found"
        
        # The function should use is_ground_duplicate for matching
        # Extract the function body (rough check)
        func_start = content.find("async def _classify_pipeline_issues")
        func_end = content.find("async def _sync_pipeline_issues_to_grounds")
        func_body = content[func_start:func_end]
        
        assert "is_ground_duplicate" in func_body, \
            "_classify_pipeline_issues does NOT use is_ground_duplicate (fuzzy dedup)"
        
        print("✓ _classify_pipeline_issues uses fuzzy dedup via is_ground_duplicate")
    
    def test_sync_pipeline_issues_uses_fuzzy_dedup(self):
        """Verify _sync_pipeline_issues_to_grounds uses fuzzy dedup, not exact-title match"""
        grounds_file = "/app/backend/routers/grounds.py"
        
        with open(grounds_file, 'r') as f:
            content = f.read()
        
        # Find the _sync_pipeline_issues_to_grounds function
        assert "async def _sync_pipeline_issues_to_grounds" in content, \
            "_sync_pipeline_issues_to_grounds function not found"
        
        # The function should use is_ground_duplicate for matching
        func_start = content.find("async def _sync_pipeline_issues_to_grounds")
        func_end = content.find("async def _ensure_pipeline_identification")
        func_body = content[func_start:func_end]
        
        assert "is_ground_duplicate" in func_body, \
            "_sync_pipeline_issues_to_grounds does NOT use is_ground_duplicate (fuzzy dedup)"
        
        print("✓ _sync_pipeline_issues_to_grounds uses fuzzy dedup via is_ground_duplicate")
    
    def test_ground_dedup_module_exists(self):
        """Verify ground_dedup.py exists and has required functions"""
        dedup_file = "/app/backend/services/ground_dedup.py"
        
        with open(dedup_file, 'r') as f:
            content = f.read()
        
        assert "def is_ground_duplicate" in content, \
            "is_ground_duplicate function not found in ground_dedup.py"
        
        assert "def normalise_au_spelling" in content, \
            "normalise_au_spelling function not found in ground_dedup.py"
        
        # Check for fuzzy matching methods
        assert "fuzz.token_set_ratio" in content or "fuzzywuzzy" in content, \
            "ground_dedup.py missing fuzzywuzzy fuzzy matching"
        
        print("✓ ground_dedup.py has is_ground_duplicate and normalise_au_spelling")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
