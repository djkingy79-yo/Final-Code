"""
Regression Tests for Criminal Appeal AI - Backend APIs
Tests all core endpoints after refactoring:
- Health check
- Cases CRUD
- Documents endpoint
- Timeline endpoint
- Notes endpoint
- Deadlines endpoint
- Checklist endpoint
- Resources directory
- Templates endpoint
- Report generation (all 3 types verified via existing reports)
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://barrister-brief.preview.emergentagent.com').rstrip('/')
SESSION_TOKEN = os.environ.get('TEST_SESSION_TOKEN', 'test_sess_7b8591ebfb684a3fa6a5b8e3dbcad052')
TEST_CASE_ID = os.environ.get('TEST_CASE_ID', 'case_cec9b5706fae')


@pytest.fixture(scope="session")
def auth_headers():
    """Get authentication headers"""
    return {
        "Authorization": f"Bearer {SESSION_TOKEN}",
        "Content-Type": "application/json"
    }


class TestHealthCheck:
    """Health check endpoints - should pass"""
    
    def test_api_health(self):
        """Test /api/health endpoint"""
        response = requests.get(f"{BASE_URL}/api/health")
        assert response.status_code == 200
        data = response.json()
        assert data.get("status") == "healthy"
        assert "timestamp" in data
        print("✓ API health check passed")

    def test_root_health_returns_html(self):
        """Test /health returns frontend HTML (expected behavior with ingress)"""
        response = requests.get(f"{BASE_URL}/health")
        # The root health check returns the frontend HTML in production
        # API health at /api/health is the correct endpoint
        assert response.status_code == 200
        print("✓ Root endpoint accessible")


class TestAuthentication:
    """Authentication tests"""
    
    def test_auth_me_with_valid_token(self, auth_headers):
        """Test /api/auth/me with valid session token"""
        response = requests.get(f"{BASE_URL}/api/auth/me", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert "user_id" in data
        assert "email" in data
        assert "name" in data
        print(f"✓ Auth me passed - User: {data.get('name')}")

    def test_auth_me_without_token(self):
        """Test /api/auth/me without token returns 401"""
        response = requests.get(f"{BASE_URL}/api/auth/me")
        assert response.status_code == 401
        print("✓ Auth me without token correctly returns 401")


class TestCasesEndpoint:
    """Cases CRUD endpoint tests"""
    
    def test_get_cases(self, auth_headers):
        """Test GET /api/cases returns list of cases"""
        response = requests.get(f"{BASE_URL}/api/cases", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        print(f"✓ Get cases passed - Found {len(data)} cases")
        
        # Verify case structure
        if data:
            case = data[0]
            assert "case_id" in case
            assert "title" in case
            assert "defendant_name" in case
            assert "document_count" in case
            assert "event_count" in case
            print("✓ Case structure verified")

    def test_get_cases_unauthorized(self):
        """Test GET /api/cases without auth returns 401"""
        response = requests.get(f"{BASE_URL}/api/cases")
        assert response.status_code == 401
        print("✓ Get cases unauthorized returns 401")


class TestDocumentsEndpoint:
    """Documents endpoint tests"""
    
    def test_get_documents(self, auth_headers):
        """Test GET /api/cases/{case_id}/documents"""
        response = requests.get(
            f"{BASE_URL}/api/cases/{TEST_CASE_ID}/documents",
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        print(f"✓ Get documents passed - Found {len(data)} documents")
        
        # Verify document structure
        if data:
            doc = data[0]
            assert "document_id" in doc
            assert "filename" in doc
            assert "category" in doc
            print("✓ Document structure verified")

    def test_get_documents_invalid_case(self, auth_headers):
        """Test GET documents for invalid case returns 404"""
        response = requests.get(
            f"{BASE_URL}/api/cases/invalid_case/documents",
            headers=auth_headers
        )
        assert response.status_code == 404
        print("✓ Get documents for invalid case returns 404")


class TestTimelineEndpoint:
    """Timeline endpoint tests"""
    
    def test_get_timeline(self, auth_headers):
        """Test GET /api/cases/{case_id}/timeline"""
        response = requests.get(
            f"{BASE_URL}/api/cases/{TEST_CASE_ID}/timeline",
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        print(f"✓ Get timeline passed - Found {len(data)} events")


class TestNotesEndpoint:
    """Notes endpoint tests"""
    
    def test_get_notes(self, auth_headers):
        """Test GET /api/cases/{case_id}/notes"""
        response = requests.get(
            f"{BASE_URL}/api/cases/{TEST_CASE_ID}/notes",
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        print(f"✓ Get notes passed - Found {len(data)} notes")


class TestDeadlinesEndpoint:
    """Deadlines endpoint tests"""
    
    def test_get_deadlines(self, auth_headers):
        """Test GET /api/cases/{case_id}/deadlines"""
        response = requests.get(
            f"{BASE_URL}/api/cases/{TEST_CASE_ID}/deadlines",
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        print(f"✓ Get deadlines passed - Found {len(data)} deadlines")


class TestChecklistEndpoint:
    """Checklist endpoint tests"""
    
    def test_get_checklist(self, auth_headers):
        """Test GET /api/cases/{case_id}/checklist"""
        response = requests.get(
            f"{BASE_URL}/api/cases/{TEST_CASE_ID}/checklist",
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) > 0  # Should have default checklist items
        print(f"✓ Get checklist passed - Found {len(data)} items")
        
        # Verify checklist structure
        item = data[0]
        assert "item_id" in item
        assert "title" in item
        assert "phase" in item


class TestResourcesEndpoint:
    """Resources directory endpoint tests"""
    
    def test_get_resources_directory(self, auth_headers):
        """Test GET /api/resources/directory"""
        response = requests.get(
            f"{BASE_URL}/api/resources/directory",
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        # Resources endpoint returns an object with categories, not a list
        assert isinstance(data, dict)
        # Should have key categories like legal_aid, courts, etc.
        assert "legal_aid" in data or "courts" in data or "advocacy_groups" in data
        print(f"✓ Get resources directory passed - Found {len(data.keys())} categories")


class TestTemplatesEndpoint:
    """Templates endpoint tests"""
    
    def test_get_templates(self, auth_headers):
        """Test GET /api/templates"""
        response = requests.get(
            f"{BASE_URL}/api/templates",
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        print(f"✓ Get templates passed - Found {len(data)} templates")


class TestReportsEndpoint:
    """Reports endpoint tests - verify all 3 report types exist"""
    
    def test_get_reports(self, auth_headers):
        """Test GET /api/cases/{case_id}/reports"""
        response = requests.get(
            f"{BASE_URL}/api/cases/{TEST_CASE_ID}/reports",
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        print(f"✓ Get reports passed - Found {len(data)} reports")
        
        # Verify report structure
        if data:
            report = data[0]
            assert "report_id" in report
            assert "report_type" in report
            assert "title" in report
            assert "content" in report
    
    def test_verify_all_report_types_exist(self, auth_headers):
        """Verify all 3 report types (quick_summary, full_detailed, extensive_log) exist"""
        response = requests.get(
            f"{BASE_URL}/api/cases/{TEST_CASE_ID}/reports",
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        
        report_types = [r['report_type'] for r in data]
        
        # Check for each type
        has_quick = 'quick_summary' in report_types
        has_full = 'full_detailed' in report_types
        has_extensive = 'extensive_log' in report_types
        
        print(f"  - quick_summary: {'✓' if has_quick else '✗'}")
        print(f"  - full_detailed: {'✓' if has_full else '✗'}")
        print(f"  - extensive_log: {'✓' if has_extensive else '✗'}")
        
        # All 3 types should exist based on previous test run
        assert has_quick, "quick_summary report type missing"
        assert has_full, "full_detailed report type missing"
        assert has_extensive, "extensive_log report type missing"
        print("✓ All 3 report types verified")

    def test_get_reports_unauthorized(self):
        """Test GET reports without auth returns 401"""
        response = requests.get(
            f"{BASE_URL}/api/cases/{TEST_CASE_ID}/reports"
        )
        assert response.status_code == 401
        print("✓ Get reports unauthorized returns 401")
