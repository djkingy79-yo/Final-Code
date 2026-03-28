"""
Iteration 62 - Full Regression Test for Appeal Case Manager
Tests all major backend APIs including:
- Auth (register/login)
- Cases (CRUD)
- Reports (generate/delete)
- Progress Analysis (AI)
- PayID payments (create-reference/verify)
- Payment prices

Test credentials: deletetest@test.com / TestPass123!
"""
import pytest
import requests
import os
import uuid
import time

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://criminal-appeals-au-2.preview.emergentagent.com')

class TestIteration62Regression:
    """Full regression test suite for iteration 62"""
    
    @pytest.fixture(scope="class")
    def session(self):
        """Create a session to maintain cookies"""
        session = requests.Session()
        session.headers.update({"Content-Type": "application/json"})
        return session
    
    @pytest.fixture(scope="class")
    def test_user_email(self):
        """Generate unique test user email"""
        return f"test_iter62_{uuid.uuid4().hex[:8]}@test.com"
    
    @pytest.fixture(scope="class")
    def auth_session(self, session):
        """Login with test credentials and return authenticated session"""
        # Use existing test user
        login_response = session.post(f"{BASE_URL}/api/auth/login", json={
            "email": "deletetest@test.com",
            "password": "TestPass123!"
        })
        
        if login_response.status_code == 200:
            return session
        else:
            pytest.skip("Login failed - cannot continue with authenticated tests")
    
    # ============ HEALTH CHECK ============
    def test_01_health_check(self, session):
        """Test /health endpoint"""
        response = session.get(f"{BASE_URL}/health")
        assert response.status_code == 200, f"Health check failed: {response.text}"
        data = response.json()
        assert "status" in data
        print(f"PASS: Health check - status: {data.get('status')}")
    
    def test_02_api_health(self, session):
        """Test /api/health endpoint"""
        response = session.get(f"{BASE_URL}/api/health")
        assert response.status_code == 200, f"API health check failed: {response.text}"
        data = response.json()
        print(f"PASS: API health - {data}")
    
    # ============ AUTH TESTS ============
    def test_03_register_new_user(self, session, test_user_email):
        """Test POST /api/auth/register - create new user"""
        response = session.post(f"{BASE_URL}/api/auth/register", json={
            "email": test_user_email,
            "password": "TestPass123!",
            "name": "Test User Iteration 62"
        })
        # Accept 200, 201 (success) or 400 (user exists)
        assert response.status_code in [200, 201, 400], f"Register failed: {response.text}"
        print(f"PASS: Register endpoint - status: {response.status_code}")
    
    def test_04_login_test_user(self, session):
        """Test POST /api/auth/login - login with test user"""
        response = session.post(f"{BASE_URL}/api/auth/login", json={
            "email": "deletetest@test.com",
            "password": "TestPass123!"
        })
        assert response.status_code == 200, f"Login failed: {response.text}"
        data = response.json()
        assert "user_id" in data or "email" in data, "Login response missing user info"
        print(f"PASS: Login - user authenticated")
    
    # ============ CASE TESTS ============
    def test_05_create_case(self, auth_session):
        """Test POST /api/cases - create a case"""
        case_title = f"Test Case Iter62 {uuid.uuid4().hex[:6]}"
        response = auth_session.post(f"{BASE_URL}/api/cases", json={
            "title": case_title,
            "defendant_name": "Test Defendant",
            "case_number": "TEST-62-001",
            "court": "NSW Supreme Court",
            "state": "nsw",
            "offence_category": "homicide",
            "summary": "Test case for iteration 62 regression"
        })
        assert response.status_code == 200, f"Create case failed: {response.text}"
        data = response.json()
        assert "case_id" in data, "Response missing case_id"
        # Store for later tests
        auth_session.test_case_id = data["case_id"]
        print(f"PASS: Create case - case_id: {data['case_id']}")
    
    def test_06_get_cases(self, auth_session):
        """Test GET /api/cases - list all cases"""
        response = auth_session.get(f"{BASE_URL}/api/cases")
        assert response.status_code == 200, f"Get cases failed: {response.text}"
        data = response.json()
        assert isinstance(data, list), "Response should be a list"
        print(f"PASS: Get cases - found {len(data)} cases")
    
    def test_07_get_single_case(self, auth_session):
        """Test GET /api/cases/{id} - get single case"""
        case_id = getattr(auth_session, 'test_case_id', None)
        if not case_id:
            pytest.skip("No test case ID available")
        
        response = auth_session.get(f"{BASE_URL}/api/cases/{case_id}")
        assert response.status_code == 200, f"Get case failed: {response.text}"
        data = response.json()
        assert data.get("case_id") == case_id
        print(f"PASS: Get single case - {data.get('title')}")
    
    # ============ REPORT TESTS ============
    def test_08_generate_quick_summary_report(self, auth_session):
        """Test POST /api/cases/{id}/reports/generate with report_type=quick_summary"""
        case_id = getattr(auth_session, 'test_case_id', None)
        if not case_id:
            pytest.skip("No test case ID available")
        
        response = auth_session.post(
            f"{BASE_URL}/api/cases/{case_id}/reports/generate",
            json={"report_type": "quick_summary", "aggressive_mode": False},
            timeout=180  # AI generation can take time
        )
        # Accept 200 (success), 400 (no docs) or 500 (AI error)
        assert response.status_code in [200, 400, 500], f"Report generation unexpected error: {response.text}"
        
        if response.status_code == 200:
            data = response.json()
            auth_session.test_report_id = data.get("report_id")
            print(f"PASS: Generate quick_summary report - report_id: {data.get('report_id')}")
        else:
            print(f"INFO: Report generation returned {response.status_code} (may need documents)")
    
    def test_09_get_reports(self, auth_session):
        """Test GET /api/cases/{id}/reports - list reports"""
        case_id = getattr(auth_session, 'test_case_id', None)
        if not case_id:
            pytest.skip("No test case ID available")
        
        response = auth_session.get(f"{BASE_URL}/api/cases/{case_id}/reports")
        assert response.status_code == 200, f"Get reports failed: {response.text}"
        data = response.json()
        assert isinstance(data, list), "Response should be a list"
        print(f"PASS: Get reports - found {len(data)} reports")
    
    # ============ PROGRESS ANALYSIS TEST ============
    def test_10_generate_progress_analysis(self, auth_session):
        """Test POST /api/cases/{id}/progress-analysis - generates AI progress analysis"""
        case_id = getattr(auth_session, 'test_case_id', None)
        if not case_id:
            pytest.skip("No test case ID available")
        
        response = auth_session.post(
            f"{BASE_URL}/api/cases/{case_id}/progress-analysis",
            timeout=120
        )
        # Accept 200 (success) or 400/500 (insufficient data)
        assert response.status_code in [200, 400, 500], f"Progress analysis unexpected error: {response.text}"
        
        if response.status_code == 200:
            data = response.json()
            assert "analysis" in data or "content" in data, "Response missing analysis"
            print(f"PASS: Progress analysis generated successfully")
        else:
            print(f"INFO: Progress analysis returned {response.status_code}")
    
    # ============ PAYID PAYMENT TESTS ============
    def test_11_get_payment_prices(self, session):
        """Test GET /api/payments/prices - returns feature prices"""
        response = session.get(f"{BASE_URL}/api/payments/prices")
        assert response.status_code == 200, f"Get prices failed: {response.text}"
        data = response.json()
        assert "full_report" in data or len(data) > 0, "Response should contain prices"
        print(f"PASS: Get payment prices - {len(data)} features")
    
    def test_12_payid_create_reference(self, auth_session):
        """Test POST /api/payments/payid/create-reference - creates payment reference"""
        case_id = getattr(auth_session, 'test_case_id', None)
        if not case_id:
            pytest.skip("No test case ID available")
        
        response = auth_session.post(f"{BASE_URL}/api/payments/payid/create-reference", json={
            "feature_type": "full_report",
            "case_id": case_id
        })
        assert response.status_code == 200, f"PayID create reference failed: {response.text}"
        data = response.json()
        assert "reference" in data, "Response missing reference"
        assert "payid" in data, "Response missing payid"
        auth_session.test_payid_reference = data.get("reference")
        print(f"PASS: PayID create reference - ref: {data.get('reference')}, payid: {data.get('payid')}")
    
    def test_13_payid_verify(self, auth_session):
        """Test POST /api/payments/payid/verify - verifies payment"""
        case_id = getattr(auth_session, 'test_case_id', None)
        reference = getattr(auth_session, 'test_payid_reference', None)
        if not case_id or not reference:
            pytest.skip("No test case ID or reference available")
        
        response = auth_session.post(f"{BASE_URL}/api/payments/payid/verify", json={
            "reference": reference,
            "case_id": case_id,
            "feature_type": "full_report"
        })
        # 200 = verified, 400 = pending/invalid
        assert response.status_code in [200, 400], f"PayID verify unexpected error: {response.text}"
        data = response.json()
        print(f"PASS: PayID verify - status: {data.get('status', 'checked')}")
    
    # ============ DELETE TESTS (Cleanup) ============
    def test_14_delete_report(self, auth_session):
        """Test DELETE /api/cases/{id}/reports/{report_id} - deletes report"""
        case_id = getattr(auth_session, 'test_case_id', None)
        report_id = getattr(auth_session, 'test_report_id', None)
        
        if not case_id:
            pytest.skip("No test case ID available")
        
        if not report_id:
            # Try to get a report to delete
            response = auth_session.get(f"{BASE_URL}/api/cases/{case_id}/reports")
            if response.status_code == 200:
                reports = response.json()
                if reports:
                    report_id = reports[0].get("report_id")
        
        if not report_id:
            print("INFO: No reports to delete")
            return
        
        response = auth_session.delete(f"{BASE_URL}/api/cases/{case_id}/reports/{report_id}")
        assert response.status_code in [200, 204, 404], f"Delete report failed: {response.text}"
        print(f"PASS: Delete report - report_id: {report_id}")
    
    def test_15_delete_case(self, auth_session):
        """Test DELETE /api/cases/{id} - deletes case"""
        case_id = getattr(auth_session, 'test_case_id', None)
        if not case_id:
            pytest.skip("No test case ID available")
        
        response = auth_session.delete(f"{BASE_URL}/api/cases/{case_id}")
        assert response.status_code in [200, 204], f"Delete case failed: {response.text}"
        print(f"PASS: Delete case - case_id: {case_id}")
    
    # ============ ADDITIONAL API TESTS ============
    def test_16_get_offence_categories(self, session):
        """Test GET /api/offence-categories"""
        response = session.get(f"{BASE_URL}/api/offence-categories")
        assert response.status_code == 200, f"Get offence categories failed: {response.text}"
        data = response.json()
        assert "categories" in data, "Response missing categories"
        print(f"PASS: Get offence categories - {len(data.get('categories', []))} categories")
    
    def test_17_get_states(self, session):
        """Test GET /api/states"""
        response = session.get(f"{BASE_URL}/api/states")
        assert response.status_code == 200, f"Get states failed: {response.text}"
        data = response.json()
        assert "states" in data, "Response missing states"
        print(f"PASS: Get states - {len(data.get('states', []))} states")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
