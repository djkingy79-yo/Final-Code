"""
Iteration 73 - Cases Router Extraction Tests
Tests the cases router that was extracted from server.py into /app/backend/routers/cases.py
"""
import pytest
import requests
import os

BASE_URL = 'http://localhost:8001'
SESSION_TOKEN = "Z54IPKofu9l_AVv0fSY99-G8zJEeRuR4qnMkFqXCTeY"
CASE_ID = "case_1114ec0e2fd0"
USER_ID = "user_d2287f20104b"


@pytest.fixture
def auth_headers():
    """Headers with session cookie for authenticated requests"""
    return {
        "Cookie": f"session_token={SESSION_TOKEN}",
        "Content-Type": "application/json"
    }


class TestCasesRouterExtraction:
    """Test that cases router is properly wired and all endpoints work"""
    
    def test_get_cases_list(self, auth_headers):
        """GET /api/cases - List all user cases"""
        response = requests.get(f"{BASE_URL}/api/cases", headers=auth_headers)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert isinstance(data, list), "Response should be a list"
        
        # Verify case structure if cases exist
        if len(data) > 0:
            case = data[0]
            assert "case_id" in case, "Case should have case_id"
            assert "title" in case, "Case should have title"
            assert "user_id" in case, "Case should have user_id"
            # Verify document_count and event_count are included (batch optimization)
            assert "document_count" in case, "Case should have document_count"
            assert "event_count" in case, "Case should have event_count"
        print(f"PASSED: GET /api/cases returned {len(data)} cases")
    
    def test_get_specific_case(self, auth_headers):
        """GET /api/cases/{case_id} - Get specific case with counts"""
        response = requests.get(f"{BASE_URL}/api/cases/{CASE_ID}", headers=auth_headers)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert data["case_id"] == CASE_ID, f"Expected case_id {CASE_ID}"
        assert "document_count" in data, "Case should have document_count"
        assert "event_count" in data, "Case should have event_count"
        assert "title" in data, "Case should have title"
        print(f"PASSED: GET /api/cases/{CASE_ID} - document_count={data['document_count']}, event_count={data['event_count']}")
    
    def test_get_nonexistent_case(self, auth_headers):
        """GET /api/cases/{case_id} - Should return 404 for nonexistent case"""
        response = requests.get(f"{BASE_URL}/api/cases/nonexistent_case_123", headers=auth_headers)
        assert response.status_code == 404, f"Expected 404, got {response.status_code}"
        print("PASSED: GET nonexistent case returns 404")
    
    def test_create_case(self, auth_headers):
        """POST /api/cases - Create a new case"""
        test_case = {
            "title": "TEST_Iteration73_Case",
            "defendant_name": "Test Defendant",
            "case_number": "TEST-73-001",
            "court": "Test Court",
            "state": "nsw",
            "offence_category": "assault",
            "summary": "Test case for iteration 73 testing"
        }
        
        response = requests.post(f"{BASE_URL}/api/cases", json=test_case, headers=auth_headers)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert "case_id" in data, "Created case should have case_id"
        assert data["title"] == test_case["title"], "Title should match"
        assert data["defendant_name"] == test_case["defendant_name"], "Defendant name should match"
        
        # Store case_id for cleanup
        created_case_id = data["case_id"]
        print(f"PASSED: POST /api/cases created case {created_case_id}")
        
        # Verify case was persisted by fetching it
        get_response = requests.get(f"{BASE_URL}/api/cases/{created_case_id}", headers=auth_headers)
        assert get_response.status_code == 200, "Should be able to fetch created case"
        fetched_data = get_response.json()
        assert fetched_data["title"] == test_case["title"], "Fetched title should match"
        print("PASSED: Created case verified via GET")
        
        # Cleanup - delete the test case
        delete_response = requests.delete(f"{BASE_URL}/api/cases/{created_case_id}", headers=auth_headers)
        assert delete_response.status_code == 200, f"Cleanup failed: {delete_response.status_code}"
        print("PASSED: Test case cleaned up")
    
    def test_update_case(self, auth_headers):
        """PUT /api/cases/{case_id} - Update an existing case"""
        # First create a test case
        test_case = {
            "title": "TEST_Update_Case_73",
            "defendant_name": "Original Name",
            "state": "nsw",
            "offence_category": "fraud_dishonesty"
        }
        
        create_response = requests.post(f"{BASE_URL}/api/cases", json=test_case, headers=auth_headers)
        assert create_response.status_code == 200
        created_case_id = create_response.json()["case_id"]
        
        # Update the case
        update_data = {
            "title": "TEST_Updated_Case_73",
            "defendant_name": "Updated Name",
            "state": "vic",
            "offence_category": "assault",
            "summary": "Updated summary"
        }
        
        update_response = requests.put(f"{BASE_URL}/api/cases/{created_case_id}", json=update_data, headers=auth_headers)
        assert update_response.status_code == 200, f"Expected 200, got {update_response.status_code}: {update_response.text}"
        
        updated_data = update_response.json()
        assert updated_data["title"] == update_data["title"], "Title should be updated"
        assert updated_data["defendant_name"] == update_data["defendant_name"], "Defendant name should be updated"
        
        # Verify update persisted
        get_response = requests.get(f"{BASE_URL}/api/cases/{created_case_id}", headers=auth_headers)
        fetched_data = get_response.json()
        assert fetched_data["title"] == update_data["title"], "Fetched title should match updated value"
        print(f"PASSED: PUT /api/cases/{created_case_id} updated successfully")
        
        # Cleanup
        requests.delete(f"{BASE_URL}/api/cases/{created_case_id}", headers=auth_headers)
    
    def test_delete_case(self, auth_headers):
        """DELETE /api/cases/{case_id} - Delete a case"""
        # First create a test case
        test_case = {
            "title": "TEST_Delete_Case_73",
            "defendant_name": "To Be Deleted",
            "state": "qld",
            "offence_category": "drug_offences"
        }
        
        create_response = requests.post(f"{BASE_URL}/api/cases", json=test_case, headers=auth_headers)
        assert create_response.status_code == 200
        created_case_id = create_response.json()["case_id"]
        
        # Delete the case
        delete_response = requests.delete(f"{BASE_URL}/api/cases/{created_case_id}", headers=auth_headers)
        assert delete_response.status_code == 200, f"Expected 200, got {delete_response.status_code}"
        
        # Verify case is deleted
        get_response = requests.get(f"{BASE_URL}/api/cases/{created_case_id}", headers=auth_headers)
        assert get_response.status_code == 404, "Deleted case should return 404"
        print(f"PASSED: DELETE /api/cases/{created_case_id} - case deleted and verified")
    
    def test_delete_nonexistent_case(self, auth_headers):
        """DELETE /api/cases/{case_id} - Should return 404 for nonexistent case"""
        response = requests.delete(f"{BASE_URL}/api/cases/nonexistent_case_xyz", headers=auth_headers)
        assert response.status_code == 404, f"Expected 404, got {response.status_code}"
        print("PASSED: DELETE nonexistent case returns 404")


class TestCasesRouterAuthentication:
    """Test authentication requirements for cases endpoints"""
    
    def test_get_cases_without_auth(self):
        """GET /api/cases without auth should return 401"""
        response = requests.get(f"{BASE_URL}/api/cases")
        assert response.status_code == 401, f"Expected 401, got {response.status_code}"
        print("PASSED: GET /api/cases without auth returns 401")
    
    def test_get_case_without_auth(self):
        """GET /api/cases/{case_id} without auth should return 401"""
        response = requests.get(f"{BASE_URL}/api/cases/{CASE_ID}")
        assert response.status_code == 401, f"Expected 401, got {response.status_code}"
        print("PASSED: GET /api/cases/{case_id} without auth returns 401")
    
    def test_create_case_without_auth(self):
        """POST /api/cases without auth should return 401"""
        response = requests.post(f"{BASE_URL}/api/cases", json={"title": "Test", "defendant_name": "Test"})
        assert response.status_code == 401, f"Expected 401, got {response.status_code}"
        print("PASSED: POST /api/cases without auth returns 401")


class TestHealthEndpoint:
    """Test health endpoint is still working"""
    
    def test_health_check(self):
        """GET /health should return healthy status"""
        response = requests.get(f"{BASE_URL}/health")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        data = response.json()
        assert data.get("status") == "healthy", "Health status should be healthy"
        print("PASSED: Health check endpoint working")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
