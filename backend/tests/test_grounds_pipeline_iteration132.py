"""
Test Suite for Grounds Pipeline Delegation (Iteration 132)
Tests the patched grounds.py router that delegates auto-identify and investigate
operations through the new 5-stage pipeline (Extract → Classify → Verify → Project → Draft).

Key endpoints tested:
- POST /api/cases/{case_id}/grounds/auto-identify - pipeline delegation
- POST /api/cases/{case_id}/grounds/{ground_id}/investigate - pipeline verify delegation
- GET /api/cases/{case_id}/grounds - with ground_id, source_mode, verification_status
- GET /api/cases/{case_id}/grounds/{ground_id} - with enrichment
- Regression: CRUD operations on grounds
- Regression: Staged pipeline extract
- Regression: Health endpoint
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Test credentials
TEST_EMAIL = "test@example.com"
TEST_PASSWORD = "TestPassword123!"

# Test cases from the request
TEST_CASE_1 = "case_87ef925be713"  # Scott Joshua v R - has many documents and grounds
TEST_CASE_2 = "case_a97ea91f0692"  # Dummy Murder Appeal - has pipeline-derived grounds
TEST_GROUND_ID = "gnd_0fa085cfc1ce"  # Ground ID for investigate test (case_a97ea91f0692)


class TestAuthentication:
    """Authentication tests - must pass before other tests"""
    
    def test_login_returns_session_token(self):
        """Verify login returns session_token field"""
        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": TEST_EMAIL, "password": TEST_PASSWORD},
            timeout=30
        )
        assert response.status_code == 200, f"Login failed: {response.text}"
        data = response.json()
        assert "session_token" in data, "session_token not in response"
        assert len(data["session_token"]) > 10, "session_token too short"


@pytest.fixture(scope="module")
def auth_token():
    """Get authentication token for all tests"""
    response = requests.post(
        f"{BASE_URL}/api/auth/login",
        json={"email": TEST_EMAIL, "password": TEST_PASSWORD},
        timeout=30
    )
    if response.status_code != 200:
        pytest.skip(f"Authentication failed: {response.text}")
    return response.json().get("session_token")


@pytest.fixture(scope="module")
def auth_headers(auth_token):
    """Headers with auth token"""
    return {
        "Authorization": f"Bearer {auth_token}",
        "Content-Type": "application/json"
    }


# ============================================================================
# REGRESSION TESTS - Health and Basic Endpoints
# ============================================================================

class TestRegressionHealth:
    """Regression: Health endpoint"""
    
    def test_health_endpoint_returns_healthy(self):
        """GET /api/health should return healthy status"""
        response = requests.get(f"{BASE_URL}/api/health", timeout=10)
        assert response.status_code == 200
        data = response.json()
        assert data.get("status") == "healthy"
        assert "database" in data


# ============================================================================
# GET GROUNDS TESTS - ground_id, source_mode, verification_status enrichment
# ============================================================================

class TestGetGrounds:
    """Test GET /api/cases/{case_id}/grounds with enrichment fields"""
    
    def test_get_grounds_returns_list(self, auth_headers):
        """GET /api/cases/{case_id}/grounds returns grounds list"""
        response = requests.get(
            f"{BASE_URL}/api/cases/{TEST_CASE_1}/grounds",
            headers=auth_headers,
            timeout=30
        )
        assert response.status_code == 200, f"Get grounds failed: {response.text}"
        data = response.json()
        assert "grounds" in data
        assert "count" in data
        assert "is_unlocked" in data
        assert "unlock_price" in data
    
    def test_get_grounds_has_ground_id_field(self, auth_headers):
        """GET /api/cases/{case_id}/grounds - each ground has ground_id"""
        response = requests.get(
            f"{BASE_URL}/api/cases/{TEST_CASE_1}/grounds",
            headers=auth_headers,
            timeout=30
        )
        assert response.status_code == 200
        data = response.json()
        
        if data.get("is_unlocked") and data.get("grounds"):
            for ground in data["grounds"]:
                assert "ground_id" in ground, f"ground_id missing from ground: {ground.get('title')}"
                # Accept both gnd_ and ground_ prefixes (legacy grounds may have ground_ prefix)
                assert ground["ground_id"].startswith(("gnd_", "ground_")), f"Invalid ground_id format: {ground['ground_id']}"
    
    def test_get_grounds_has_source_mode_field(self, auth_headers):
        """GET /api/cases/{case_id}/grounds - each ground has source_mode"""
        response = requests.get(
            f"{BASE_URL}/api/cases/{TEST_CASE_1}/grounds",
            headers=auth_headers,
            timeout=30
        )
        assert response.status_code == 200
        data = response.json()
        
        if data.get("is_unlocked") and data.get("grounds"):
            for ground in data["grounds"]:
                assert "source_mode" in ground, f"source_mode missing from ground: {ground.get('title')}"
                # Accept all valid source_mode values including ai_generated (legacy)
                assert ground["source_mode"] in ["manual", "derived", "legacy", "ai_generated"], f"Invalid source_mode: {ground['source_mode']}"
    
    def test_get_grounds_has_verification_status_field(self, auth_headers):
        """GET /api/cases/{case_id}/grounds - each ground has verification_status"""
        response = requests.get(
            f"{BASE_URL}/api/cases/{TEST_CASE_1}/grounds",
            headers=auth_headers,
            timeout=30
        )
        assert response.status_code == 200
        data = response.json()
        
        if data.get("is_unlocked") and data.get("grounds"):
            for ground in data["grounds"]:
                assert "verification_status" in ground, f"verification_status missing from ground: {ground.get('title')}"
    
    def test_get_grounds_case_not_found(self, auth_headers):
        """GET /api/cases/{case_id}/grounds with non-existent case returns 404"""
        response = requests.get(
            f"{BASE_URL}/api/cases/case_nonexistent/grounds",
            headers=auth_headers,
            timeout=30
        )
        assert response.status_code == 404


class TestGetSingleGround:
    """Test GET /api/cases/{case_id}/grounds/{ground_id} with enrichment"""
    
    def test_get_single_ground_returns_ground(self, auth_headers):
        """GET /api/cases/{case_id}/grounds/{ground_id} returns ground details"""
        # First get a ground_id from the list
        list_response = requests.get(
            f"{BASE_URL}/api/cases/{TEST_CASE_1}/grounds",
            headers=auth_headers,
            timeout=30
        )
        if list_response.status_code != 200:
            pytest.skip("Could not get grounds list")
        
        data = list_response.json()
        if not data.get("is_unlocked") or not data.get("grounds"):
            pytest.skip("No unlocked grounds available")
        
        ground_id = data["grounds"][0]["ground_id"]
        
        response = requests.get(
            f"{BASE_URL}/api/cases/{TEST_CASE_1}/grounds/{ground_id}",
            headers=auth_headers,
            timeout=30
        )
        assert response.status_code == 200, f"Get single ground failed: {response.text}"
        ground = response.json()
        assert "ground_id" in ground
        assert "title" in ground
        assert "ground_type" in ground
    
    def test_get_single_ground_has_source_mode(self, auth_headers):
        """GET /api/cases/{case_id}/grounds/{ground_id} has source_mode enrichment"""
        # First get a ground_id from the list
        list_response = requests.get(
            f"{BASE_URL}/api/cases/{TEST_CASE_1}/grounds",
            headers=auth_headers,
            timeout=30
        )
        if list_response.status_code != 200:
            pytest.skip("Could not get grounds list")
        
        data = list_response.json()
        if not data.get("is_unlocked") or not data.get("grounds"):
            pytest.skip("No unlocked grounds available")
        
        ground_id = data["grounds"][0]["ground_id"]
        
        response = requests.get(
            f"{BASE_URL}/api/cases/{TEST_CASE_1}/grounds/{ground_id}",
            headers=auth_headers,
            timeout=30
        )
        assert response.status_code == 200
        ground = response.json()
        assert "source_mode" in ground, "source_mode missing from single ground response"
        assert ground["source_mode"] in ["manual", "derived", "legacy", "ai_generated"]
    
    def test_get_single_ground_has_verification_status(self, auth_headers):
        """GET /api/cases/{case_id}/grounds/{ground_id} has verification_status enrichment"""
        # First get a ground_id from the list
        list_response = requests.get(
            f"{BASE_URL}/api/cases/{TEST_CASE_1}/grounds",
            headers=auth_headers,
            timeout=30
        )
        if list_response.status_code != 200:
            pytest.skip("Could not get grounds list")
        
        data = list_response.json()
        if not data.get("is_unlocked") or not data.get("grounds"):
            pytest.skip("No unlocked grounds available")
        
        ground_id = data["grounds"][0]["ground_id"]
        
        response = requests.get(
            f"{BASE_URL}/api/cases/{TEST_CASE_1}/grounds/{ground_id}",
            headers=auth_headers,
            timeout=30
        )
        assert response.status_code == 200
        ground = response.json()
        assert "verification_status" in ground, "verification_status missing from single ground response"
    
    def test_get_single_ground_not_found(self, auth_headers):
        """GET /api/cases/{case_id}/grounds/{ground_id} with non-existent ground returns 404"""
        response = requests.get(
            f"{BASE_URL}/api/cases/{TEST_CASE_1}/grounds/gnd_nonexistent",
            headers=auth_headers,
            timeout=30
        )
        assert response.status_code == 404


# ============================================================================
# AUTO-IDENTIFY TESTS - Pipeline Delegation
# ============================================================================

class TestAutoIdentify:
    """Test POST /api/cases/{case_id}/grounds/auto-identify - pipeline delegation"""
    
    def test_auto_identify_returns_expected_fields(self, auth_headers):
        """POST /api/cases/{case_id}/grounds/auto-identify returns expected response fields"""
        response = requests.post(
            f"{BASE_URL}/api/cases/{TEST_CASE_2}/grounds/auto-identify",
            headers=auth_headers,
            timeout=180  # LLM calls can take time
        )
        assert response.status_code == 200, f"Auto-identify failed: {response.text}"
        data = response.json()
        
        # Check all expected fields from the request
        assert "identified_count" in data, "identified_count missing"
        assert "skipped_duplicates" in data, "skipped_duplicates missing"
        assert "existing_grounds" in data, "existing_grounds missing"
        assert "message" in data, "message missing"
        assert "unlock_required" in data, "unlock_required missing"
        assert "unlock_price" in data, "unlock_price missing"
        
        # Validate types
        assert isinstance(data["identified_count"], int)
        assert isinstance(data["skipped_duplicates"], int)
        assert isinstance(data["existing_grounds"], int)
        assert isinstance(data["message"], str)
        assert isinstance(data["unlock_required"], bool)
        assert isinstance(data["unlock_price"], (int, float))
    
    def test_auto_identify_message_mentions_pipeline(self, auth_headers):
        """POST /api/cases/{case_id}/grounds/auto-identify message mentions pipeline operations"""
        response = requests.post(
            f"{BASE_URL}/api/cases/{TEST_CASE_2}/grounds/auto-identify",
            headers=auth_headers,
            timeout=180
        )
        assert response.status_code == 200
        data = response.json()
        
        # Message should mention pipeline operations
        message = data.get("message", "").lower()
        assert any(word in message for word in ["pipeline", "extracted", "classified", "synced"]), \
            f"Message doesn't mention pipeline operations: {data['message']}"
    
    def test_auto_identify_case_not_found(self, auth_headers):
        """POST /api/cases/{case_id}/grounds/auto-identify with non-existent case returns 404"""
        response = requests.post(
            f"{BASE_URL}/api/cases/case_nonexistent/grounds/auto-identify",
            headers=auth_headers,
            timeout=30
        )
        assert response.status_code == 404
    
    def test_auto_identify_unauthorized(self):
        """POST /api/cases/{case_id}/grounds/auto-identify without auth returns 401/403"""
        response = requests.post(
            f"{BASE_URL}/api/cases/{TEST_CASE_2}/grounds/auto-identify",
            timeout=30
        )
        assert response.status_code in [401, 403, 422]


# ============================================================================
# INVESTIGATE TESTS - Pipeline Verify Delegation
# ============================================================================

class TestInvestigateGround:
    """Test POST /api/cases/{case_id}/grounds/{ground_id}/investigate - pipeline verify delegation"""
    
    def test_investigate_returns_projected_ground(self, auth_headers):
        """POST /api/cases/{case_id}/grounds/{ground_id}/investigate returns projected ground"""
        # First get a ground_id from case 2 (has pipeline-derived grounds)
        list_response = requests.get(
            f"{BASE_URL}/api/cases/{TEST_CASE_2}/grounds",
            headers=auth_headers,
            timeout=30
        )
        if list_response.status_code != 200:
            pytest.skip("Could not get grounds list")
        
        data = list_response.json()
        if not data.get("is_unlocked") or not data.get("grounds"):
            pytest.skip("No unlocked grounds available")
        
        ground_id = data["grounds"][0]["ground_id"]
        
        response = requests.post(
            f"{BASE_URL}/api/cases/{TEST_CASE_2}/grounds/{ground_id}/investigate",
            headers=auth_headers,
            timeout=180  # LLM calls can take time
        )
        assert response.status_code == 200, f"Investigate failed: {response.text}"
        ground = response.json()
        
        # Check expected fields from the request
        assert "ground_id" in ground or "title" in ground, "Ground data missing"
    
    def test_investigate_returns_legitimacy_scores(self, auth_headers):
        """POST investigate returns legitimacy_scores"""
        list_response = requests.get(
            f"{BASE_URL}/api/cases/{TEST_CASE_2}/grounds",
            headers=auth_headers,
            timeout=30
        )
        if list_response.status_code != 200:
            pytest.skip("Could not get grounds list")
        
        data = list_response.json()
        if not data.get("is_unlocked") or not data.get("grounds"):
            pytest.skip("No unlocked grounds available")
        
        ground_id = data["grounds"][0]["ground_id"]
        
        response = requests.post(
            f"{BASE_URL}/api/cases/{TEST_CASE_2}/grounds/{ground_id}/investigate",
            headers=auth_headers,
            timeout=180
        )
        assert response.status_code == 200
        ground = response.json()
        
        assert "legitimacy_scores" in ground, "legitimacy_scores missing from investigate response"
        assert isinstance(ground["legitimacy_scores"], dict)
    
    def test_investigate_returns_supporting_evidence(self, auth_headers):
        """POST investigate returns supporting_evidence"""
        list_response = requests.get(
            f"{BASE_URL}/api/cases/{TEST_CASE_2}/grounds",
            headers=auth_headers,
            timeout=30
        )
        if list_response.status_code != 200:
            pytest.skip("Could not get grounds list")
        
        data = list_response.json()
        if not data.get("is_unlocked") or not data.get("grounds"):
            pytest.skip("No unlocked grounds available")
        
        ground_id = data["grounds"][0]["ground_id"]
        
        response = requests.post(
            f"{BASE_URL}/api/cases/{TEST_CASE_2}/grounds/{ground_id}/investigate",
            headers=auth_headers,
            timeout=180
        )
        assert response.status_code == 200
        ground = response.json()
        
        assert "supporting_evidence" in ground, "supporting_evidence missing from investigate response"
        assert isinstance(ground["supporting_evidence"], list)
    
    def test_investigate_returns_law_sections(self, auth_headers):
        """POST investigate returns law_sections"""
        list_response = requests.get(
            f"{BASE_URL}/api/cases/{TEST_CASE_2}/grounds",
            headers=auth_headers,
            timeout=30
        )
        if list_response.status_code != 200:
            pytest.skip("Could not get grounds list")
        
        data = list_response.json()
        if not data.get("is_unlocked") or not data.get("grounds"):
            pytest.skip("No unlocked grounds available")
        
        ground_id = data["grounds"][0]["ground_id"]
        
        response = requests.post(
            f"{BASE_URL}/api/cases/{TEST_CASE_2}/grounds/{ground_id}/investigate",
            headers=auth_headers,
            timeout=180
        )
        assert response.status_code == 200
        ground = response.json()
        
        assert "law_sections" in ground, "law_sections missing from investigate response"
        assert isinstance(ground["law_sections"], list)
    
    def test_investigate_returns_similar_cases(self, auth_headers):
        """POST investigate returns similar_cases"""
        list_response = requests.get(
            f"{BASE_URL}/api/cases/{TEST_CASE_2}/grounds",
            headers=auth_headers,
            timeout=30
        )
        if list_response.status_code != 200:
            pytest.skip("Could not get grounds list")
        
        data = list_response.json()
        if not data.get("is_unlocked") or not data.get("grounds"):
            pytest.skip("No unlocked grounds available")
        
        ground_id = data["grounds"][0]["ground_id"]
        
        response = requests.post(
            f"{BASE_URL}/api/cases/{TEST_CASE_2}/grounds/{ground_id}/investigate",
            headers=auth_headers,
            timeout=180
        )
        assert response.status_code == 200
        ground = response.json()
        
        assert "similar_cases" in ground, "similar_cases missing from investigate response"
        assert isinstance(ground["similar_cases"], list)
    
    def test_investigate_returns_verification_status(self, auth_headers):
        """POST investigate returns verification_status"""
        list_response = requests.get(
            f"{BASE_URL}/api/cases/{TEST_CASE_2}/grounds",
            headers=auth_headers,
            timeout=30
        )
        if list_response.status_code != 200:
            pytest.skip("Could not get grounds list")
        
        data = list_response.json()
        if not data.get("is_unlocked") or not data.get("grounds"):
            pytest.skip("No unlocked grounds available")
        
        ground_id = data["grounds"][0]["ground_id"]
        
        response = requests.post(
            f"{BASE_URL}/api/cases/{TEST_CASE_2}/grounds/{ground_id}/investigate",
            headers=auth_headers,
            timeout=180
        )
        assert response.status_code == 200
        ground = response.json()
        
        assert "verification_status" in ground, "verification_status missing from investigate response"
    
    def test_investigate_returns_source_mode(self, auth_headers):
        """POST investigate returns source_mode"""
        list_response = requests.get(
            f"{BASE_URL}/api/cases/{TEST_CASE_2}/grounds",
            headers=auth_headers,
            timeout=30
        )
        if list_response.status_code != 200:
            pytest.skip("Could not get grounds list")
        
        data = list_response.json()
        if not data.get("is_unlocked") or not data.get("grounds"):
            pytest.skip("No unlocked grounds available")
        
        ground_id = data["grounds"][0]["ground_id"]
        
        response = requests.post(
            f"{BASE_URL}/api/cases/{TEST_CASE_2}/grounds/{ground_id}/investigate",
            headers=auth_headers,
            timeout=180
        )
        assert response.status_code == 200
        ground = response.json()
        
        assert "source_mode" in ground, "source_mode missing from investigate response"
    
    def test_investigate_ground_not_found(self, auth_headers):
        """POST investigate with non-existent ground returns 404"""
        response = requests.post(
            f"{BASE_URL}/api/cases/{TEST_CASE_2}/grounds/gnd_nonexistent/investigate",
            headers=auth_headers,
            timeout=30
        )
        assert response.status_code == 404
    
    def test_investigate_case_not_found(self, auth_headers):
        """POST investigate with non-existent case returns 404"""
        response = requests.post(
            f"{BASE_URL}/api/cases/case_nonexistent/grounds/{TEST_GROUND_ID}/investigate",
            headers=auth_headers,
            timeout=30
        )
        assert response.status_code == 404
    
    def test_investigate_unauthorized(self):
        """POST investigate without auth returns 401/403"""
        response = requests.post(
            f"{BASE_URL}/api/cases/{TEST_CASE_2}/grounds/{TEST_GROUND_ID}/investigate",
            timeout=30
        )
        assert response.status_code in [401, 403, 422]


# ============================================================================
# REGRESSION TESTS - CRUD Operations on Grounds
# ============================================================================

class TestGroundsCRUD:
    """Regression: CRUD operations on grounds should still work"""
    
    def test_create_ground_works(self, auth_headers):
        """POST /api/cases/{case_id}/grounds creates a new ground"""
        response = requests.post(
            f"{BASE_URL}/api/cases/{TEST_CASE_1}/grounds",
            headers=auth_headers,
            json={
                "title": "TEST_Regression Ground",
                "ground_type": "procedural_error",
                "description": "Test ground for regression testing"
            },
            timeout=30
        )
        assert response.status_code == 200, f"Create ground failed: {response.text}"
        ground = response.json()
        assert "ground_id" in ground
        assert ground["title"] == "TEST_Regression Ground"
        assert ground["ground_type"] == "procedural_error"
        
        # Store ground_id for cleanup
        TestGroundsCRUD.created_ground_id = ground["ground_id"]
    
    def test_update_ground_works(self, auth_headers):
        """PUT /api/cases/{case_id}/grounds/{ground_id} updates a ground"""
        if not hasattr(TestGroundsCRUD, 'created_ground_id'):
            pytest.skip("No ground created to update")
        
        response = requests.put(
            f"{BASE_URL}/api/cases/{TEST_CASE_1}/grounds/{TestGroundsCRUD.created_ground_id}",
            headers=auth_headers,
            json={
                "description": "Updated description for regression testing"
            },
            timeout=30
        )
        assert response.status_code == 200, f"Update ground failed: {response.text}"
        ground = response.json()
        assert ground["description"] == "Updated description for regression testing"
    
    def test_delete_ground_works(self, auth_headers):
        """DELETE /api/cases/{case_id}/grounds/{ground_id} deletes a ground"""
        if not hasattr(TestGroundsCRUD, 'created_ground_id'):
            pytest.skip("No ground created to delete")
        
        response = requests.delete(
            f"{BASE_URL}/api/cases/{TEST_CASE_1}/grounds/{TestGroundsCRUD.created_ground_id}",
            headers=auth_headers,
            timeout=30
        )
        assert response.status_code == 200, f"Delete ground failed: {response.text}"
        
        # Verify deletion
        get_response = requests.get(
            f"{BASE_URL}/api/cases/{TEST_CASE_1}/grounds/{TestGroundsCRUD.created_ground_id}",
            headers=auth_headers,
            timeout=30
        )
        assert get_response.status_code == 404


# ============================================================================
# REGRESSION TESTS - Staged Pipeline Extract
# ============================================================================

class TestStagedPipelineRegression:
    """Regression: Staged pipeline extract should still work"""
    
    def test_staged_pipeline_extract_works(self, auth_headers):
        """POST /api/pipeline/cases/{case_id}/documents/{doc_id}/extract still works"""
        # Get a document ID first
        docs_response = requests.get(
            f"{BASE_URL}/api/cases/{TEST_CASE_1}/documents",
            headers=auth_headers,
            timeout=30
        )
        if docs_response.status_code != 200 or not docs_response.json():
            pytest.skip("No documents available for extraction test")
        
        doc_id = docs_response.json()[0]["document_id"]
        
        response = requests.post(
            f"{BASE_URL}/api/pipeline/cases/{TEST_CASE_1}/documents/{doc_id}/extract",
            headers=auth_headers,
            timeout=120
        )
        assert response.status_code == 200, f"Pipeline extract failed: {response.text}"
        data = response.json()
        assert "extract_id" in data
        assert "status" in data


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
