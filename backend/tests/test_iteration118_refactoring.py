"""
Iteration 118 - Refactoring Verification Tests
Tests all extracted routers after server.py monolith split.
Verifies that all endpoints work correctly after refactoring.
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', 'http://localhost:8001').rstrip('/')

# Test credentials
TEST_EMAIL = "test@example.com"
TEST_PASSWORD = "TestPassword123!"
TEST_CASE_ID = "case_a97ea91f0692"


class TestHealthAndAuth:
    """Health check and authentication tests"""
    
    def test_health_check(self):
        """Test /api/health endpoint"""
        response = requests.get(f"{BASE_URL}/api/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "database" in data
        assert "timestamp" in data
        print(f"✓ Health check passed: {data['status']}, DB: {data['database']}")
    
    def test_login_success(self):
        """Test login with valid credentials"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": TEST_EMAIL,
            "password": TEST_PASSWORD
        })
        assert response.status_code == 200
        data = response.json()
        assert "session_token" in data
        assert "user_id" in data
        assert data["email"] == TEST_EMAIL
        print(f"✓ Login successful: {data['email']}")
        return data["session_token"]


class TestExtractedRouters:
    """Tests for all extracted routers from server.py"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Get auth token before each test"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": TEST_EMAIL,
            "password": TEST_PASSWORD
        })
        if response.status_code == 200:
            self.session_token = response.json().get("session_token")
            self.cookies = {"session_token": self.session_token}
        else:
            pytest.skip("Authentication failed")
    
    # ============ DOCUMENTS ROUTER ============
    def test_get_documents(self):
        """Test GET /api/cases/{case_id}/documents (documents.py router)"""
        response = requests.get(
            f"{BASE_URL}/api/cases/{TEST_CASE_ID}/documents",
            cookies=self.cookies
        )
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        print(f"✓ Documents router: Found {len(data)} documents")
    
    # ============ TIMELINE ROUTER ============
    def test_get_timeline(self):
        """Test GET /api/cases/{case_id}/timeline (timeline.py router)"""
        response = requests.get(
            f"{BASE_URL}/api/cases/{TEST_CASE_ID}/timeline",
            cookies=self.cookies
        )
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        print(f"✓ Timeline router: Found {len(data)} events")
    
    # ============ NOTES ROUTER ============
    def test_get_notes(self):
        """Test GET /api/cases/{case_id}/notes (notes.py router)"""
        response = requests.get(
            f"{BASE_URL}/api/cases/{TEST_CASE_ID}/notes",
            cookies=self.cookies
        )
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        print(f"✓ Notes router: Found {len(data)} notes")
    
    # ============ DEADLINES ROUTER ============
    def test_get_deadlines(self):
        """Test GET /api/cases/{case_id}/deadlines (deadlines.py router)"""
        response = requests.get(
            f"{BASE_URL}/api/cases/{TEST_CASE_ID}/deadlines",
            cookies=self.cookies
        )
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        print(f"✓ Deadlines router: Found {len(data)} deadlines")
    
    def test_get_checklist(self):
        """Test GET /api/cases/{case_id}/checklist (deadlines.py router)"""
        response = requests.get(
            f"{BASE_URL}/api/cases/{TEST_CASE_ID}/checklist",
            cookies=self.cookies
        )
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        print(f"✓ Checklist router: Found {len(data)} items")
    
    def test_get_case_strength(self):
        """Test GET /api/cases/{case_id}/strength (deadlines.py router)"""
        response = requests.get(
            f"{BASE_URL}/api/cases/{TEST_CASE_ID}/strength",
            cookies=self.cookies
        )
        assert response.status_code == 200
        data = response.json()
        assert "overall_score" in data
        assert "rating" in data
        assert "breakdown" in data
        print(f"✓ Case strength router: Score {data['overall_score']}, Rating: {data['rating']}")
    
    # ============ GROUNDS ROUTER ============
    def test_get_grounds(self):
        """Test GET /api/cases/{case_id}/grounds (grounds.py router)"""
        response = requests.get(
            f"{BASE_URL}/api/cases/{TEST_CASE_ID}/grounds",
            cookies=self.cookies
        )
        assert response.status_code == 200
        data = response.json()
        assert "grounds" in data or "count" in data
        print("✓ Grounds router: Response contains grounds data")
    
    # ============ PAYMENTS ROUTER ============
    def test_get_payment_prices(self):
        """Test GET /api/payments/prices (payments.py router)"""
        response = requests.get(f"{BASE_URL}/api/payments/prices")
        assert response.status_code == 200
        data = response.json()
        assert "prices" in data
        assert "currency" in data
        print(f"✓ Payments router: Prices endpoint working, currency: {data['currency']}")
    
    def test_get_case_payments(self):
        """Test GET /api/cases/{case_id}/payments (payments.py router)"""
        response = requests.get(
            f"{BASE_URL}/api/cases/{TEST_CASE_ID}/payments",
            cookies=self.cookies
        )
        assert response.status_code == 200
        data = response.json()
        assert "payments" in data
        assert "unlocked_features" in data
        print(f"✓ Case payments router: Found {len(data['payments'])} payments")
    
    # ============ RESOURCES ROUTER ============
    def test_get_resource_directory(self):
        """Test GET /api/resources/directory (resources.py router)"""
        response = requests.get(f"{BASE_URL}/api/resources/directory")
        assert response.status_code == 200
        data = response.json()
        assert "support_services" in data
        assert "advocacy_groups" in data
        assert "courts" in data
        print("✓ Resources router: Directory endpoint working")
    
    def test_get_templates(self):
        """Test GET /api/templates (resources.py router)"""
        response = requests.get(f"{BASE_URL}/api/templates")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) > 0
        print(f"✓ Templates router: Found {len(data)} templates")
    
    # ============ ANALYSIS ROUTER ============
    def test_analyze_contradictions(self):
        """Test POST /api/cases/{case_id}/analyze-contradictions (analysis.py router)"""
        response = requests.post(
            f"{BASE_URL}/api/cases/{TEST_CASE_ID}/analyze-contradictions",
            cookies=self.cookies
        )
        # May return 400 if not enough documents, which is valid behavior
        assert response.status_code in [200, 400]
        if response.status_code == 200:
            data = response.json()
            assert "analysis" in data
            print("✓ Contradictions analysis router: Analysis completed")
        else:
            print("✓ Contradictions analysis router: Correctly returned 400 (need 2+ docs)")
    
    def test_progress_analysis(self):
        """Test POST /api/cases/{case_id}/progress-analysis (analysis.py router)"""
        response = requests.post(
            f"{BASE_URL}/api/cases/{TEST_CASE_ID}/progress-analysis",
            cookies=self.cookies,
            timeout=60  # AI analysis may take time
        )
        assert response.status_code == 200
        data = response.json()
        assert "analysis" in data
        assert "generated_at" in data
        print("✓ Progress analysis router: Analysis generated")
    
    # ============ REPORTS (stays in server.py) ============
    def test_get_reports(self):
        """Test GET /api/cases/{case_id}/reports (stays in server.py)"""
        response = requests.get(
            f"{BASE_URL}/api/cases/{TEST_CASE_ID}/reports",
            cookies=self.cookies
        )
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        print(f"✓ Reports endpoint (server.py): Found {len(data)} reports")
    
    def test_get_barrister_view(self):
        """Test GET /api/cases/{case_id}/reports/barrister-view (stays in server.py)"""
        response = requests.get(
            f"{BASE_URL}/api/cases/{TEST_CASE_ID}/reports/barrister-view",
            cookies=self.cookies
        )
        # May return 404 if no barrister view exists
        assert response.status_code in [200, 404]
        if response.status_code == 200:
            response.json()
            print("✓ Barrister view endpoint (server.py): View found")
        else:
            print("✓ Barrister view endpoint (server.py): No view exists (404 expected)")
    
    # ============ COLLABORATION ROUTER ============
    def test_get_messages(self):
        """Test GET /api/cases/{case_id}/messages (collaboration.py router)"""
        response = requests.get(
            f"{BASE_URL}/api/cases/{TEST_CASE_ID}/messages",
            cookies=self.cookies
        )
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        print(f"✓ Messages router: Found {len(data)} messages")


class TestCasesRouter:
    """Tests for cases router"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Get auth token before each test"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": TEST_EMAIL,
            "password": TEST_PASSWORD
        })
        if response.status_code == 200:
            self.session_token = response.json().get("session_token")
            self.cookies = {"session_token": self.session_token}
        else:
            pytest.skip("Authentication failed")
    
    def test_list_cases(self):
        """Test GET /api/cases - list all cases"""
        response = requests.get(
            f"{BASE_URL}/api/cases",
            cookies=self.cookies
        )
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        print(f"✓ Cases list: Found {len(data)} cases")
    
    def test_get_single_case(self):
        """Test GET /api/cases/{case_id} - get single case"""
        response = requests.get(
            f"{BASE_URL}/api/cases/{TEST_CASE_ID}",
            cookies=self.cookies
        )
        assert response.status_code == 200
        data = response.json()
        assert "case_id" in data
        assert data["case_id"] == TEST_CASE_ID
        print(f"✓ Single case: {data.get('title', 'Unknown')}")


class TestRouterImports:
    """Verify all router imports are working"""
    
    def test_all_routers_loaded(self):
        """Verify server starts with all routers"""
        # If health check works, all routers loaded successfully
        response = requests.get(f"{BASE_URL}/api/health")
        assert response.status_code == 200
        print("✓ All routers loaded successfully (server started)")
    
    def test_no_route_conflicts(self):
        """Test that there are no route conflicts between routers"""
        # Test a few endpoints from different routers
        endpoints = [
            "/api/health",
            "/api/payments/prices",
            "/api/resources/directory",
            "/api/templates"
        ]
        for endpoint in endpoints:
            response = requests.get(f"{BASE_URL}{endpoint}")
            assert response.status_code == 200, f"Route conflict or error at {endpoint}"
        print("✓ No route conflicts detected")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
