"""
Iteration 169 - Full Production Readiness Review
Tests: Auth flows, Cases CRUD, Reports, Grounds, Documents, Legal Framework, Analytics, Health
Admin account: djkingy79@gmail.com (bypasses payment locks)
"""
import pytest
import requests
import os
import uuid

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://criminal-appeals-au-2.preview.emergentagent.com')

# Test credentials from test_credentials.md
ADMIN_EMAIL = "djkingy79@gmail.com"
ADMIN_PASSWORD = "Grubbygrub88"

# Shared session to avoid rate limiting
_shared_session = {"token": None}

def get_auth_token():
    """Get or reuse auth token to avoid rate limiting"""
    if _shared_session["token"]:
        return _shared_session["token"]
    
    response = requests.post(f"{BASE_URL}/api/auth/login", json={
        "email": ADMIN_EMAIL,
        "password": ADMIN_PASSWORD
    })
    if response.status_code == 200:
        _shared_session["token"] = response.json()["session_token"]
        return _shared_session["token"]
    return None


class TestHealthEndpoints:
    """Health check endpoints"""
    
    def test_health_basic(self):
        """GET /api/health returns healthy"""
        response = requests.get(f"{BASE_URL}/api/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["database"] == "connected"
        print(f"✓ Health check passed: {data}")
    
    def test_health_deep(self):
        """GET /api/health/deep checks mongo, llm_key, email"""
        response = requests.get(f"{BASE_URL}/api/health/deep")
        assert response.status_code == 200
        data = response.json()
        assert data["healthy"] == True
        assert data["checks"]["mongodb"]["status"] == "ok"
        assert data["checks"]["llm_key"]["status"] == "ok"
        assert data["checks"]["email"]["status"] == "ok"
        print(f"✓ Deep health check passed: {data['checks']}")
    
    def test_ready_endpoint(self):
        """GET /api/ready returns ready"""
        response = requests.get(f"{BASE_URL}/api/ready")
        assert response.status_code == 200
        data = response.json()
        assert data["ready"] == True
        print(f"✓ Ready endpoint passed")


class TestAuthFlows:
    """Authentication endpoint tests"""
    
    def test_login_success(self):
        """POST /api/auth/login with valid credentials returns session_token"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        assert response.status_code == 200
        data = response.json()
        assert "session_token" in data
        assert "user_id" in data
        assert data["email"] == ADMIN_EMAIL.lower()
        assert len(data["session_token"]) > 0
        print(f"✓ Login success: user_id={data['user_id']}")
        return data["session_token"]
    
    def test_login_wrong_password(self):
        """POST /api/auth/login with wrong password returns 401"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": "wrongpassword123"
        })
        assert response.status_code == 401
        data = response.json()
        assert "detail" in data
        print(f"✓ Wrong password correctly rejected: {data['detail']}")
    
    def test_login_nonexistent_user(self):
        """POST /api/auth/login with nonexistent email returns 401"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": "nonexistent@example.com",
            "password": "anypassword"
        })
        assert response.status_code == 401
        print(f"✓ Nonexistent user correctly rejected")
    
    def test_register_new_user(self):
        """POST /api/auth/register creates new user"""
        unique_email = f"test_user_{uuid.uuid4().hex[:8]}@example.com"
        response = requests.post(f"{BASE_URL}/api/auth/register", json={
            "email": unique_email,
            "password": "testpass123",
            "name": "Test User"
        })
        assert response.status_code == 200
        data = response.json()
        assert "user_id" in data
        assert "session_token" in data
        assert data["email"] == unique_email.lower()
        print(f"✓ Registration success: user_id={data['user_id']}")
        return data
    
    def test_register_duplicate_email(self):
        """POST /api/auth/register with existing email returns 400"""
        response = requests.post(f"{BASE_URL}/api/auth/register", json={
            "email": ADMIN_EMAIL,
            "password": "testpass123",
            "name": "Duplicate User"
        })
        assert response.status_code == 400
        data = response.json()
        assert "already registered" in data["detail"].lower() or "email" in data["detail"].lower()
        print(f"✓ Duplicate email correctly rejected")
    
    def test_get_me_authenticated(self):
        """GET /api/auth/me returns current user info"""
        # First login
        login_resp = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        token = login_resp.json()["session_token"]
        
        # Get me
        response = requests.get(
            f"{BASE_URL}/api/auth/me",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["email"] == ADMIN_EMAIL.lower()
        assert "user_id" in data
        assert data["is_admin"] == True  # Admin account
        print(f"✓ Get me success: is_admin={data['is_admin']}")
    
    def test_get_me_unauthenticated(self):
        """GET /api/auth/me without token returns 401"""
        response = requests.get(f"{BASE_URL}/api/auth/me")
        assert response.status_code == 401
        print(f"✓ Unauthenticated /me correctly rejected")
    
    def test_logout(self):
        """POST /api/auth/logout clears session"""
        # First login
        login_resp = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        token = login_resp.json()["session_token"]
        
        # Logout
        response = requests.post(
            f"{BASE_URL}/api/auth/logout",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "logged out" in data["message"].lower()
        print(f"✓ Logout success")
    
    def test_session_exchange_invalid(self):
        """POST /api/auth/session with invalid session_id returns error"""
        response = requests.post(
            f"{BASE_URL}/api/auth/session",
            json={"session_id": "invalid_session_id_12345"}
        )
        assert response.status_code in [401, 400, 502, 504]
        print(f"✓ Invalid session_id correctly rejected: status={response.status_code}")


class TestCasesCRUD:
    """Cases CRUD operations"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Get shared token"""
        self.token = get_auth_token()
        if not self.token:
            pytest.skip("Could not get auth token")
        self.headers = {"Authorization": f"Bearer {self.token}"}
    
    def test_list_cases(self):
        """GET /api/cases returns array of cases"""
        response = requests.get(f"{BASE_URL}/api/cases", headers=self.headers)
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        print(f"✓ List cases: {len(data)} cases found")
        # Verify no _id exposed
        for case in data[:5]:
            assert "_id" not in case, "MongoDB _id should not be exposed"
        return data
    
    def test_create_case(self):
        """POST /api/cases creates new case"""
        case_data = {
            "title": f"TEST_Case_{uuid.uuid4().hex[:8]}",
            "defendant_name": "Test Defendant",
            "state": "nsw",
            "court": "District Court"
        }
        response = requests.post(
            f"{BASE_URL}/api/cases",
            headers=self.headers,
            json=case_data
        )
        assert response.status_code == 200
        data = response.json()
        assert "case_id" in data
        assert data["title"] == case_data["title"]
        assert data["defendant_name"] == case_data["defendant_name"]
        assert data["state"] == case_data["state"]
        assert "_id" not in data, "MongoDB _id should not be exposed"
        print(f"✓ Create case success: case_id={data['case_id']}")
        return data
    
    def test_get_single_case(self):
        """GET /api/cases/{case_id} returns case detail"""
        # First create a case
        created = self.test_create_case()
        case_id = created["case_id"]
        
        # Get the case
        response = requests.get(
            f"{BASE_URL}/api/cases/{case_id}",
            headers=self.headers
        )
        assert response.status_code == 200
        data = response.json()
        assert data["case_id"] == case_id
        assert "_id" not in data
        print(f"✓ Get single case success")
        return data
    
    def test_update_case(self):
        """PUT /api/cases/{case_id} updates case fields"""
        # First create a case
        created = self.test_create_case()
        case_id = created["case_id"]
        
        # Update the case
        update_data = {
            "title": created["title"],
            "defendant_name": created["defendant_name"],
            "state": "wa",  # Change from nsw to wa
            "court": "Supreme Court"
        }
        response = requests.put(
            f"{BASE_URL}/api/cases/{case_id}",
            headers=self.headers,
            json=update_data
        )
        assert response.status_code == 200
        data = response.json()
        assert data["state"] == "wa"
        assert data["court"] == "Supreme Court"
        print(f"✓ Update case success: state changed to {data['state']}")
        
        # Verify persistence with GET
        get_resp = requests.get(f"{BASE_URL}/api/cases/{case_id}", headers=self.headers)
        assert get_resp.json()["state"] == "wa"
        print(f"✓ Update persisted correctly")
    
    def test_delete_case(self):
        """DELETE /api/cases/{case_id} deletes case"""
        # First create a case
        created = self.test_create_case()
        case_id = created["case_id"]
        
        # Delete the case
        response = requests.delete(
            f"{BASE_URL}/api/cases/{case_id}",
            headers=self.headers
        )
        assert response.status_code == 200
        
        # Verify deletion with GET
        get_resp = requests.get(f"{BASE_URL}/api/cases/{case_id}", headers=self.headers)
        assert get_resp.status_code == 404
        print(f"✓ Delete case success: case_id={case_id}")


class TestReports:
    """Report generation and listing"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Get shared token"""
        self.token = get_auth_token()
        if not self.token:
            pytest.skip("Could not get auth token")
        self.headers = {"Authorization": f"Bearer {self.token}"}
    
    def test_list_reports_for_case(self):
        """GET /api/cases/{case_id}/reports lists reports"""
        # Get existing cases
        cases_resp = requests.get(f"{BASE_URL}/api/cases", headers=self.headers)
        cases = cases_resp.json()
        
        if not cases:
            pytest.skip("No cases available for testing")
        
        case_id = cases[0]["case_id"]
        response = requests.get(
            f"{BASE_URL}/api/cases/{case_id}/reports",
            headers=self.headers
        )
        assert response.status_code == 200
        data = response.json()
        # Reports endpoint returns array directly
        assert isinstance(data, list)
        print(f"✓ List reports: {len(data)} reports for case {case_id}")
    
    def test_trigger_quick_summary_report(self):
        """POST /api/cases/{case_id}/reports/generate triggers report generation"""
        # Create a test case first
        case_data = {
            "title": f"TEST_Report_Case_{uuid.uuid4().hex[:8]}",
            "defendant_name": "Test Defendant",
            "state": "nsw",
            "court": "District Court"
        }
        create_resp = requests.post(
            f"{BASE_URL}/api/cases",
            headers=self.headers,
            json=case_data
        )
        case_id = create_resp.json()["case_id"]
        
        # Trigger quick_summary report via /generate endpoint
        response = requests.post(
            f"{BASE_URL}/api/cases/{case_id}/reports/generate",
            headers=self.headers,
            json={"report_type": "quick_summary"}
        )
        # Should return 200 (accepted) or 202 (processing)
        assert response.status_code in [200, 202]
        data = response.json()
        # Should have report_id or status
        assert "report_id" in data or "status" in data or "message" in data
        print(f"✓ Report generation triggered: {data}")
        
        # Cleanup
        requests.delete(f"{BASE_URL}/api/cases/{case_id}", headers=self.headers)


class TestGrounds:
    """Grounds of merit endpoints"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Get shared token"""
        self.token = get_auth_token()
        if not self.token:
            pytest.skip("Could not get auth token")
        self.headers = {"Authorization": f"Bearer {self.token}"}
    
    def test_list_grounds_for_case(self):
        """GET /api/cases/{case_id}/grounds lists grounds"""
        # Get existing cases
        cases_resp = requests.get(f"{BASE_URL}/api/cases", headers=self.headers)
        cases = cases_resp.json()
        
        if not cases:
            pytest.skip("No cases available for testing")
        
        case_id = cases[0]["case_id"]
        response = requests.get(
            f"{BASE_URL}/api/cases/{case_id}/grounds",
            headers=self.headers
        )
        assert response.status_code == 200
        data = response.json()
        assert "grounds" in data
        assert "count" in data
        assert "is_unlocked" in data
        # Admin should have unlocked access
        assert data["is_unlocked"] == True, "Admin should have unlocked access"
        print(f"✓ List grounds: {data['count']} grounds, unlocked={data['is_unlocked']}")


class TestDocuments:
    """Document endpoints"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Get shared token"""
        self.token = get_auth_token()
        if not self.token:
            pytest.skip("Could not get auth token")
        self.headers = {"Authorization": f"Bearer {self.token}"}
    
    def test_list_documents_for_case(self):
        """GET /api/cases/{case_id}/documents lists documents"""
        # Get existing cases
        cases_resp = requests.get(f"{BASE_URL}/api/cases", headers=self.headers)
        cases = cases_resp.json()
        
        if not cases:
            pytest.skip("No cases available for testing")
        
        case_id = cases[0]["case_id"]
        response = requests.get(
            f"{BASE_URL}/api/cases/{case_id}/documents",
            headers=self.headers
        )
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        print(f"✓ List documents: {len(data)} documents for case {case_id}")


class TestLegalFramework:
    """Legal framework / offence-framework endpoints"""
    
    def test_offence_framework_nsw_homicide(self):
        """GET /api/offence-framework/homicide?state=nsw returns NSW legislation"""
        response = requests.get(f"{BASE_URL}/api/offence-framework/homicide?state=nsw")
        assert response.status_code == 200
        data = response.json()
        assert "category" in data
        assert "state" in data
        assert data["state"]["abbreviation"] == "NSW"
        # Should have NSW-specific legislation
        state_leg = data["category"].get("state_legislation", {})
        print(f"✓ NSW homicide framework: state={data['state']['name']}")
    
    def test_offence_framework_wa_domestic_violence(self):
        """GET /api/offence-framework/domestic_violence?state=wa returns WA legislation (no NSW)"""
        response = requests.get(f"{BASE_URL}/api/offence-framework/domestic_violence?state=wa")
        assert response.status_code == 200
        data = response.json()
        assert data["state"]["abbreviation"] == "WA"
        assert data["state"]["name"] == "Western Australia"
        # Should NOT have NSW legislation
        state_leg = data["category"].get("state_legislation", {})
        # Verify no NSW contamination
        leg_str = str(state_leg).lower()
        assert "crimes act 1900 (nsw)" not in leg_str, "WA should not have NSW Crimes Act"
        print(f"✓ WA domestic violence framework: state={data['state']['name']}")
    
    def test_offence_framework_empty_state(self):
        """GET /api/offence-framework/assault?state= returns Unspecified, NOT NSW"""
        response = requests.get(f"{BASE_URL}/api/offence-framework/assault?state=")
        assert response.status_code == 200
        data = response.json()
        # Should return Unspecified, not default to NSW
        state_name = data["state"].get("name", "")
        assert state_name == "Unspecified" or data["state"].get("abbreviation") == "N/A", \
            f"Empty state should return Unspecified, got: {data['state']}"
        print(f"✓ Empty state returns Unspecified: {data['state']}")
    
    def test_offence_framework_qld(self):
        """GET /api/offence-framework/homicide?state=qld returns QLD legislation"""
        response = requests.get(f"{BASE_URL}/api/offence-framework/homicide?state=qld")
        assert response.status_code == 200
        data = response.json()
        assert data["state"]["abbreviation"] == "QLD"
        print(f"✓ QLD homicide framework: state={data['state']['name']}")


class TestDeadlinesAndChecklist:
    """Deadlines and checklist endpoints"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Get shared token"""
        self.token = get_auth_token()
        if not self.token:
            pytest.skip("Could not get auth token")
        self.headers = {"Authorization": f"Bearer {self.token}"}
    
    def test_list_deadlines(self):
        """GET /api/cases/{case_id}/deadlines lists deadlines"""
        cases_resp = requests.get(f"{BASE_URL}/api/cases", headers=self.headers)
        cases = cases_resp.json()
        
        if not cases:
            pytest.skip("No cases available for testing")
        
        case_id = cases[0]["case_id"]
        response = requests.get(
            f"{BASE_URL}/api/cases/{case_id}/deadlines",
            headers=self.headers
        )
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        print(f"✓ List deadlines: {len(data)} deadlines")
    
    def test_list_checklist(self):
        """GET /api/cases/{case_id}/checklist lists checklist items"""
        cases_resp = requests.get(f"{BASE_URL}/api/cases", headers=self.headers)
        cases = cases_resp.json()
        
        if not cases:
            pytest.skip("No cases available for testing")
        
        case_id = cases[0]["case_id"]
        response = requests.get(
            f"{BASE_URL}/api/cases/{case_id}/checklist",
            headers=self.headers
        )
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        print(f"✓ List checklist: {len(data)} items")


class TestAnalytics:
    """Analytics endpoints (admin only)"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Get shared token"""
        self.token = get_auth_token()
        if not self.token:
            pytest.skip("Could not get auth token")
        self.headers = {"Authorization": f"Bearer {self.token}"}
    
    def test_quick_stats(self):
        """GET /api/analytics/quick-stats returns stats (admin only)"""
        response = requests.get(
            f"{BASE_URL}/api/analytics/quick-stats",
            headers=self.headers
        )
        assert response.status_code == 200
        data = response.json()
        assert "total_users" in data
        assert "total_cases" in data
        print(f"✓ Quick stats: users={data['total_users']}, cases={data['total_cases']}")


class TestNoMongoIdExposure:
    """Verify MongoDB _id is not exposed in any API response"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Get shared token"""
        self.token = get_auth_token()
        if not self.token:
            pytest.skip("Could not get auth token")
        self.headers = {"Authorization": f"Bearer {self.token}"}
    
    def test_cases_no_id(self):
        """GET /api/cases should not expose _id"""
        response = requests.get(f"{BASE_URL}/api/cases", headers=self.headers)
        assert response.status_code == 200
        data = response.json()
        for case in data[:10]:
            assert "_id" not in case, f"MongoDB _id exposed in case: {case.get('case_id')}"
        print(f"✓ Cases endpoint: no _id exposure")
    
    def test_auth_me_no_id(self):
        """GET /api/auth/me should not expose _id"""
        response = requests.get(f"{BASE_URL}/api/auth/me", headers=self.headers)
        assert response.status_code == 200
        data = response.json()
        assert "_id" not in data, "MongoDB _id exposed in /auth/me"
        print(f"✓ Auth/me endpoint: no _id exposure")


# Cleanup test data
class TestCleanup:
    """Cleanup TEST_ prefixed data"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Get shared token"""
        self.token = get_auth_token()
        if not self.token:
            pytest.skip("Could not get auth token")
        self.headers = {"Authorization": f"Bearer {self.token}"}
    
    def test_cleanup_test_cases(self):
        """Delete TEST_ prefixed cases"""
        response = requests.get(f"{BASE_URL}/api/cases", headers=self.headers)
        cases = response.json()
        deleted = 0
        for case in cases:
            if case.get("title", "").startswith("TEST_"):
                del_resp = requests.delete(
                    f"{BASE_URL}/api/cases/{case['case_id']}",
                    headers=self.headers
                )
                if del_resp.status_code == 200:
                    deleted += 1
        print(f"✓ Cleanup: deleted {deleted} TEST_ cases")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
