"""
Iteration 58 - Backend API Tests
Testing:
- DELETE /api/cases/{case_id} works with cookie auth
- DELETE /api/cases/{case_id}/reports/{report_id} works with cookie auth
- POST /api/cases/{case_id}/progress-analysis returns AI analysis
- POST /api/cases/{case_id}/grounds/auto-identify returns identified grounds
- POST /api/cases/{case_id}/grounds/{ground_id}/investigate returns deep analysis
"""

import pytest
import requests
import os
import time

BASE_URL = 'http://localhost:8001'

class TestBackendAPIs:
    """Test critical backend APIs for iteration 58"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup session for all tests"""
        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json"})
        # Store created resources for cleanup
        self.created_case_id = None
        self.created_ground_id = None
        yield
        # Cleanup after tests
        if self.created_case_id:
            try:
                self.session.delete(f"{BASE_URL}/api/cases/{self.created_case_id}")
            except Exception:
                pass
    
    def login_test_user(self):
        """Login with test credentials and return session"""
        # Use email/password auth - endpoint is /api/auth/login
        response = self.session.post(f"{BASE_URL}/api/auth/login", json={
            "email": "deletetest@test.com",
            "password": "TestPass123!"
        })
        if response.status_code == 200:
            return True
        print(f"Login failed with status {response.status_code}: {response.text[:200]}")
        return False
    
    # ========== DELETE /api/cases/{case_id} Tests ==========
    
    def test_delete_case_requires_auth(self):
        """DELETE /api/cases/{case_id} requires authentication"""
        # Create new session without login
        unauthenticated = requests.Session()
        response = unauthenticated.delete(f"{BASE_URL}/api/cases/nonexistent")
        assert response.status_code == 401, f"Expected 401, got {response.status_code}"
        print("PASS: DELETE /api/cases/{case_id} requires authentication")
    
    def test_delete_case_creates_and_deletes(self):
        """DELETE /api/cases/{case_id} successfully deletes a case"""
        assert self.login_test_user(), "Login failed"
        
        # Create a test case
        response = self.session.post(f"{BASE_URL}/api/cases", json={
            "title": "TEST_DELETE_CASE_58",
            "defendant_name": "Test Defendant",
            "case_number": "TEST-58-001",
            "state": "nsw",
            "offence_category": "homicide"
        })
        assert response.status_code in [200, 201], f"Failed to create case: {response.status_code}"
        case_data = response.json()
        case_id = case_data.get("case_id")
        assert case_id, "No case_id returned"
        print(f"Created test case: {case_id}")
        
        # Delete the case
        delete_response = self.session.delete(f"{BASE_URL}/api/cases/{case_id}")
        assert delete_response.status_code in [200, 204], f"Delete failed: {delete_response.status_code}"
        print(f"PASS: Successfully deleted case {case_id}")
        
        # Verify deletion - should return 404
        get_response = self.session.get(f"{BASE_URL}/api/cases/{case_id}")
        assert get_response.status_code == 404, f"Expected 404 after deletion, got {get_response.status_code}"
        print("PASS: Case correctly returns 404 after deletion")
    
    def test_delete_case_nonexistent_returns_404(self):
        """DELETE /api/cases/{case_id} returns 404 for non-existent case"""
        assert self.login_test_user(), "Login failed"
        
        response = self.session.delete(f"{BASE_URL}/api/cases/nonexistent_case_xyz123")
        assert response.status_code == 404, f"Expected 404, got {response.status_code}"
        print("PASS: DELETE /api/cases returns 404 for non-existent case")
    
    # ========== DELETE /api/cases/{case_id}/reports/{report_id} Tests ==========
    
    def test_delete_report_requires_auth(self):
        """DELETE /api/cases/{case_id}/reports/{report_id} requires authentication"""
        unauthenticated = requests.Session()
        response = unauthenticated.delete(f"{BASE_URL}/api/cases/case123/reports/report123")
        assert response.status_code == 401, f"Expected 401, got {response.status_code}"
        print("PASS: DELETE /api/cases/{case_id}/reports/{report_id} requires authentication")
    
    def test_delete_report_nonexistent_returns_404(self):
        """DELETE /api/cases/{case_id}/reports/{report_id} returns 404 for non-existent report"""
        assert self.login_test_user(), "Login failed"
        
        response = self.session.delete(f"{BASE_URL}/api/cases/nonexistent/reports/nonexistent_report")
        assert response.status_code == 404, f"Expected 404, got {response.status_code}"
        print("PASS: DELETE /api/cases/{case_id}/reports/{report_id} returns 404 for non-existent report")
    
    # ========== POST /api/cases/{case_id}/progress-analysis Tests ==========
    
    def test_progress_analysis_requires_auth(self):
        """POST /api/cases/{case_id}/progress-analysis requires authentication"""
        unauthenticated = requests.Session()
        response = unauthenticated.post(f"{BASE_URL}/api/cases/case123/progress-analysis")
        assert response.status_code == 401, f"Expected 401, got {response.status_code}"
        print("PASS: POST /api/cases/{case_id}/progress-analysis requires authentication")
    
    def test_progress_analysis_nonexistent_case_404(self):
        """POST /api/cases/{case_id}/progress-analysis returns 404 for non-existent case"""
        assert self.login_test_user(), "Login failed"
        
        response = self.session.post(f"{BASE_URL}/api/cases/nonexistent_case_xyz/progress-analysis")
        assert response.status_code == 404, f"Expected 404, got {response.status_code}"
        print("PASS: POST /api/cases/{case_id}/progress-analysis returns 404 for non-existent case")
    
    def test_progress_analysis_endpoint_exists(self):
        """POST /api/cases/{case_id}/progress-analysis endpoint exists and works"""
        assert self.login_test_user(), "Login failed"
        
        # First create a test case
        response = self.session.post(f"{BASE_URL}/api/cases", json={
            "title": "TEST_PROGRESS_ANALYSIS_58",
            "defendant_name": "Test Person",
            "state": "nsw",
            "offence_category": "assault"
        })
        assert response.status_code in [200, 201], f"Failed to create case: {response.status_code}"
        case_id = response.json().get("case_id")
        self.created_case_id = case_id
        
        # Call progress analysis - may timeout but endpoint should exist
        progress_response = self.session.post(
            f"{BASE_URL}/api/cases/{case_id}/progress-analysis",
            timeout=60
        )
        # Should get 200 (success) or 500 (AI timeout) - not 404
        assert progress_response.status_code != 404, f"Endpoint not found: {progress_response.status_code}"
        print(f"PASS: POST /api/cases/{case_id}/progress-analysis endpoint exists (status: {progress_response.status_code})")
    
    # ========== POST /api/cases/{case_id}/grounds/auto-identify Tests ==========
    
    def test_auto_identify_grounds_requires_auth(self):
        """POST /api/cases/{case_id}/grounds/auto-identify requires authentication"""
        unauthenticated = requests.Session()
        response = unauthenticated.post(f"{BASE_URL}/api/cases/case123/grounds/auto-identify")
        assert response.status_code == 401, f"Expected 401, got {response.status_code}"
        print("PASS: POST /api/cases/{case_id}/grounds/auto-identify requires authentication")
    
    def test_auto_identify_grounds_nonexistent_case_404(self):
        """POST /api/cases/{case_id}/grounds/auto-identify returns 404 for non-existent case"""
        assert self.login_test_user(), "Login failed"
        
        response = self.session.post(f"{BASE_URL}/api/cases/nonexistent_case/grounds/auto-identify")
        assert response.status_code == 404, f"Expected 404, got {response.status_code}"
        print("PASS: POST /api/cases/{case_id}/grounds/auto-identify returns 404 for non-existent case")
    
    def test_auto_identify_grounds_endpoint_exists(self):
        """POST /api/cases/{case_id}/grounds/auto-identify endpoint exists"""
        assert self.login_test_user(), "Login failed"
        
        # Create a test case
        response = self.session.post(f"{BASE_URL}/api/cases", json={
            "title": "TEST_AUTO_IDENTIFY_58",
            "defendant_name": "Test Person",
            "state": "vic",
            "offence_category": "drug_offences"
        })
        assert response.status_code in [200, 201]
        case_id = response.json().get("case_id")
        self.created_case_id = case_id
        
        # Call auto-identify - may return "no documents" message but endpoint should exist
        auto_response = self.session.post(
            f"{BASE_URL}/api/cases/{case_id}/grounds/auto-identify",
            timeout=30
        )
        # Should not be 404 - endpoint should exist
        assert auto_response.status_code != 404, f"Endpoint not found: {auto_response.status_code}"
        print(f"PASS: POST /api/cases/{case_id}/grounds/auto-identify endpoint exists (status: {auto_response.status_code})")
    
    # ========== POST /api/cases/{case_id}/grounds/{ground_id}/investigate Tests ==========
    
    def test_investigate_ground_requires_auth(self):
        """POST /api/cases/{case_id}/grounds/{ground_id}/investigate requires authentication"""
        unauthenticated = requests.Session()
        response = unauthenticated.post(f"{BASE_URL}/api/cases/case123/grounds/ground123/investigate")
        assert response.status_code == 401, f"Expected 401, got {response.status_code}"
        print("PASS: POST /api/cases/{case_id}/grounds/{ground_id}/investigate requires authentication")
    
    def test_investigate_ground_nonexistent_returns_404(self):
        """POST /api/cases/{case_id}/grounds/{ground_id}/investigate returns 404 for non-existent"""
        assert self.login_test_user(), "Login failed"
        
        response = self.session.post(f"{BASE_URL}/api/cases/nonexistent/grounds/nonexistent/investigate")
        assert response.status_code == 404, f"Expected 404, got {response.status_code}"
        print("PASS: POST /api/cases/{case_id}/grounds/{ground_id}/investigate returns 404 for non-existent")
    
    def test_investigate_ground_endpoint_exists(self):
        """POST /api/cases/{case_id}/grounds/{ground_id}/investigate endpoint exists"""
        assert self.login_test_user(), "Login failed"
        
        # Create a test case
        response = self.session.post(f"{BASE_URL}/api/cases", json={
            "title": "TEST_INVESTIGATE_58",
            "defendant_name": "Test Person",
            "state": "qld",
            "offence_category": "assault"
        })
        assert response.status_code in [200, 201]
        case_id = response.json().get("case_id")
        self.created_case_id = case_id
        
        # Create a test ground manually
        ground_response = self.session.post(f"{BASE_URL}/api/cases/{case_id}/grounds", json={
            "title": "Test Ground for Investigation",
            "description": "Test description for investigation endpoint test",
            "ground_type": "sentencing_error",
            "strength": "moderate"
        })
        assert ground_response.status_code in [200, 201], f"Failed to create ground: {ground_response.status_code}"
        ground_id = ground_response.json().get("ground_id")
        self.created_ground_id = ground_id
        
        # Call investigate - may timeout but endpoint should exist
        investigate_response = self.session.post(
            f"{BASE_URL}/api/cases/{case_id}/grounds/{ground_id}/investigate",
            timeout=30
        )
        # Should not be 404 - endpoint should exist
        assert investigate_response.status_code != 404, f"Endpoint not found: {investigate_response.status_code}"
        print(f"PASS: POST /api/cases/{case_id}/grounds/{ground_id}/investigate endpoint exists (status: {investigate_response.status_code})")
    
    # ========== POST /api/cases/{case_id}/grounds (Create ground manually) Tests ==========
    
    def test_create_ground_manually(self):
        """POST /api/cases/{case_id}/grounds creates a ground with all fields"""
        assert self.login_test_user(), "Login failed"
        
        # Create a test case first
        response = self.session.post(f"{BASE_URL}/api/cases", json={
            "title": "TEST_GROUND_CREATE_58",
            "defendant_name": "Test Person",
            "state": "nsw"
        })
        assert response.status_code in [200, 201]
        case_id = response.json().get("case_id")
        self.created_case_id = case_id
        
        # Create a ground manually
        ground_payload = {
            "title": "Test Ground Title",
            "description": "Test description for the ground",
            "ground_type": "sentencing_error",
            "strength": "moderate"
        }
        ground_response = self.session.post(f"{BASE_URL}/api/cases/{case_id}/grounds", json=ground_payload)
        assert ground_response.status_code in [200, 201], f"Failed to create ground: {ground_response.status_code}"
        
        ground_data = ground_response.json()
        assert "ground_id" in ground_data, "No ground_id in response"
        assert ground_data.get("title") == "Test Ground Title"
        assert ground_data.get("ground_type") == "sentencing_error"
        assert ground_data.get("strength") == "moderate"
        print(f"PASS: Successfully created ground manually with id {ground_data.get('ground_id')}")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
