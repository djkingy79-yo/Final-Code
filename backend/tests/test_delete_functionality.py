"""
Test Delete Functionality - Iteration 56
Tests DELETE endpoints for cases and reports to verify the fix for user-reported delete issues

Critical paths to test:
1. DELETE /api/cases/{case_id} - Delete entire case
2. DELETE /api/cases/{case_id}/reports/{report_id} - Delete a report
"""
import pytest
import requests
import time

BASE_URL = 'http://localhost:8001'

class TestDeleteFunctionality:
    """Test delete functionality for cases and reports"""
    
    session = None
    test_case_id = None
    test_report_id = None
    
    @classmethod
    def setup_class(cls):
        """Login and create test data"""
        cls.session = requests.Session()
        cls.session.headers.update({"Content-Type": "application/json"})
        
        # Login with test credentials
        login_response = cls.session.post(
            f"{BASE_URL}/api/auth/login",
            json={
                "email": "deletetest@test.com",
                "password": "TestPass123!"
            }
        )
        print(f"Login response: {login_response.status_code}")
        if login_response.status_code != 200:
            print(f"Login failed: {login_response.text}")
    
    def test_01_login_successful(self):
        """Verify login was successful"""
        # Check if we can access the /cases endpoint (requires auth)
        response = self.session.get(f"{BASE_URL}/api/cases")
        print(f"GET /api/cases status: {response.status_code}")
        assert response.status_code == 200, f"Login verification failed: {response.status_code}"
    
    def test_02_create_test_case_for_delete(self):
        """Create a test case that we will delete"""
        response = self.session.post(
            f"{BASE_URL}/api/cases",
            json={
                "title": "TEST_DELETE_CASE_" + str(int(time.time())),
                "defendant_name": "Test Delete User",
                "case_number": "DEL-001",
                "court": "Test Court",
                "state": "nsw",
                "offence_category": "homicide",
                "offence_type": "Murder"
            }
        )
        print(f"Create case response: {response.status_code}")
        assert response.status_code == 200, f"Case creation failed: {response.text}"
        
        data = response.json()
        TestDeleteFunctionality.test_case_id = data.get("case_id")
        print(f"Created test case: {TestDeleteFunctionality.test_case_id}")
        assert TestDeleteFunctionality.test_case_id is not None
    
    def test_03_verify_case_exists(self):
        """Verify the case was created and exists"""
        response = self.session.get(f"{BASE_URL}/api/cases/{TestDeleteFunctionality.test_case_id}")
        print(f"GET case response: {response.status_code}")
        assert response.status_code == 200, f"Case not found: {response.text}"
        
        data = response.json()
        assert data.get("case_id") == TestDeleteFunctionality.test_case_id
        print(f"Case verified: {data.get('title')}")
    
    def test_04_delete_case_api(self):
        """Test DELETE /api/cases/{case_id} endpoint"""
        response = self.session.delete(f"{BASE_URL}/api/cases/{TestDeleteFunctionality.test_case_id}")
        print(f"DELETE case response: {response.status_code}")
        print(f"DELETE case body: {response.text}")
        
        assert response.status_code == 200, f"Case delete failed: {response.text}"
        data = response.json()
        assert data.get("message") == "Case deleted"
    
    def test_05_verify_case_deleted(self):
        """Verify the case no longer exists"""
        response = self.session.get(f"{BASE_URL}/api/cases/{TestDeleteFunctionality.test_case_id}")
        print(f"GET deleted case response: {response.status_code}")
        
        assert response.status_code == 404, f"Case should be deleted but still exists: {response.text}"
        print("Case deletion verified - 404 as expected")


class TestReportDelete:
    """Test report deletion functionality"""
    
    session = None
    test_case_id = None
    test_report_id = None
    
    @classmethod
    def setup_class(cls):
        """Login and create test data for report testing"""
        cls.session = requests.Session()
        cls.session.headers.update({"Content-Type": "application/json"})
        
        # Login
        login_response = cls.session.post(
            f"{BASE_URL}/api/auth/login",
            json={
                "email": "deletetest@test.com",
                "password": "TestPass123!"
            }
        )
        print(f"Login for report tests: {login_response.status_code}")
    
    def test_01_create_case_for_report_test(self):
        """Create a case for report testing"""
        response = self.session.post(
            f"{BASE_URL}/api/cases",
            json={
                "title": "TEST_REPORT_DELETE_CASE_" + str(int(time.time())),
                "defendant_name": "Test Report User",
                "case_number": "RDEL-001",
                "court": "Test Court",
                "state": "nsw",
                "offence_category": "assault"
            }
        )
        print(f"Create case for report: {response.status_code}")
        assert response.status_code == 200, f"Case creation failed: {response.text}"
        
        data = response.json()
        TestReportDelete.test_case_id = data.get("case_id")
        print(f"Created case for reports: {TestReportDelete.test_case_id}")
    
    def test_02_get_existing_reports(self):
        """Get existing reports or note that none exist"""
        response = self.session.get(f"{BASE_URL}/api/cases/{TestReportDelete.test_case_id}/reports")
        print(f"GET reports response: {response.status_code}")
        
        if response.status_code == 200:
            reports = response.json()
            print(f"Found {len(reports)} existing reports")
            
            if len(reports) > 0:
                # Use existing report for delete test
                TestReportDelete.test_report_id = reports[0].get("report_id")
                print(f"Will use existing report: {TestReportDelete.test_report_id}")
    
    def test_03_delete_report_api_unauthenticated(self):
        """Verify report delete requires authentication"""
        # Create a new session without auth
        new_session = requests.Session()
        response = new_session.delete(f"{BASE_URL}/api/cases/{TestReportDelete.test_case_id}/reports/fake_report_id")
        print(f"Unauthenticated delete response: {response.status_code}")
        
        assert response.status_code == 401, f"Should require auth: {response.status_code}"
        print("Report delete endpoint correctly requires authentication")
    
    def test_04_delete_report_nonexistent(self):
        """Test deleting a non-existent report returns 404"""
        response = self.session.delete(f"{BASE_URL}/api/cases/{TestReportDelete.test_case_id}/reports/nonexistent_report_id")
        print(f"Delete nonexistent report: {response.status_code}")
        
        assert response.status_code == 404, f"Should return 404 for nonexistent report: {response.status_code}"
        print("Report delete correctly returns 404 for nonexistent report")
    
    def test_05_cleanup_test_case(self):
        """Clean up the test case"""
        if TestReportDelete.test_case_id:
            response = self.session.delete(f"{BASE_URL}/api/cases/{TestReportDelete.test_case_id}")
            print(f"Cleanup case: {response.status_code}")
            assert response.status_code == 200


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
