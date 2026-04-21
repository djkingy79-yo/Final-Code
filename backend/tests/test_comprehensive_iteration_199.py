"""
Comprehensive Backend API Tests - Iteration 199
Testing Criminal Appeals AU app after major changes:
1. Barrister View renamed to 'Appellate Research Brief'
2. Quick Brief deleted
3. Document camera scanner added (WebDocumentScanner)
4. Translation converted to background tasks with polling
5. Export formatting updated (TOC, section headers, table headers)
6. Sales/Revenue added to admin dashboard
7. Disclaimer wording updated
8. Logo added to landing page and about page
9. Auth login fix (localStorage caching of auth_user)
10. Various landing page text changes
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', 'http://localhost:8001').rstrip('/')
CASE_ID = "case_ba08d8e0ad0d"
REPORT_ID = "rpt_1d3ddfc9c595"
ADMIN_EMAIL = "djkingy79@gmail.com"
ADMIN_PASSWORD = os.environ.get("TEST_PASSWORD", "Grubbygrub88")


@pytest.fixture
def api_client():
    """Shared requests session authenticated with a freshly-issued Bearer
    token. The previous hardcoded SESSION_TOKEN expired whenever admin
    logged in elsewhere, breaking every test using this fixture with a 401.
    Now we login once per session and attach the returned token as a Bearer
    header — works regardless of Secure cookie behaviour on HTTP."""
    session = requests.Session()
    session.headers.update({"Content-Type": "application/json"})
    login_resp = session.post(
        f"{BASE_URL}/api/auth/login",
        json={"email": ADMIN_EMAIL, "password": ADMIN_PASSWORD},
    )
    if login_resp.status_code == 200:
        token = login_resp.json().get("session_token")
        if token:
            session.headers["Authorization"] = f"Bearer {token}"
    return session


class TestHealthAndBasicEndpoints:
    """Basic health and public endpoint tests"""
    
    def test_health_endpoint(self, api_client):
        """Test health endpoint is accessible"""
        response = api_client.get(f"{BASE_URL}/api/health")
        assert response.status_code == 200
        print(f"Health check: {response.json()}")
    
    def test_languages_endpoint_returns_41_languages(self, api_client):
        """Test GET /api/languages returns 41 languages"""
        response = api_client.get(f"{BASE_URL}/api/languages")
        assert response.status_code == 200
        data = response.json()
        assert "languages" in data
        languages = data["languages"]
        assert len(languages) == 41, f"Expected 41 languages, got {len(languages)}"
        print(f"Languages endpoint: {len(languages)} languages returned")
        # Verify some key languages exist
        lang_codes = [lang["code"] for lang in languages]
        assert "zh" in lang_codes, "Chinese (Simplified) should be available"
        assert "es" in lang_codes, "Spanish should be available"
        assert "ar" in lang_codes, "Arabic should be available"


class TestAnalyticsDashboard:
    """Test admin analytics dashboard with sales data"""
    
    def test_analytics_dashboard_returns_sales_data(self, api_client):
        """Test GET /api/analytics/dashboard returns sales object"""
        response = api_client.get(f"{BASE_URL}/api/analytics/dashboard")
        # May return 403 if not admin, but should not 500
        if response.status_code == 200:
            data = response.json()
            assert "sales" in data, "Dashboard should include 'sales' object"
            sales = data["sales"]
            assert "total_sales" in sales, "Sales should have total_sales"
            assert "total_revenue" in sales, "Sales should have total_revenue"
            assert "by_feature" in sales, "Sales should have by_feature breakdown"
            assert "revenue_today" in sales, "Sales should have revenue_today"
            assert "revenue_7d" in sales, "Sales should have revenue_7d"
            assert "revenue_30d" in sales, "Sales should have revenue_30d"
            print(f"Analytics dashboard sales data: total_sales={sales['total_sales']}, total_revenue=${sales['total_revenue']}")
        elif response.status_code in (401, 403):
            print(f"Analytics dashboard: auth required (status {response.status_code}, expected for non-admin)")
        else:
            pytest.fail(f"Unexpected status code: {response.status_code}")


class TestTranslationBackgroundTasks:
    """Test translation endpoints with background task polling"""
    
    def test_translate_endpoint_returns_task_or_cached(self, api_client):
        """Test POST /api/cases/{case_id}/translate returns task_id or cached result"""
        response = api_client.post(
            f"{BASE_URL}/api/cases/{CASE_ID}/translate",
            json={"language": "es", "report_id": REPORT_ID}
        )
        # Could be 200 (cached), 200 (started), or 404 (report not found)
        if response.status_code == 200:
            data = response.json()
            # Should have either translated_content (cached) or status (started/running)
            if "translated_content" in data:
                assert "language_name" in data
                print(f"Translation cached: {data.get('language_name')}")
            elif "status" in data:
                assert data["status"] in ["started", "running"]
                if data["status"] == "started":
                    assert "task_id" in data, "Started translation should return task_id"
                print(f"Translation status: {data['status']}, task_id: {data.get('task_id')}")
            else:
                pytest.fail("Response should have translated_content or status")
        elif response.status_code == 404:
            print("Translation: Report not found (expected if report doesn't exist)")
        elif response.status_code == 400:
            print(f"Translation: Bad request - {response.json().get('detail')}")
        elif response.status_code in (401, 403):
            print(f"Translation: auth required (status {response.status_code})")
        else:
            pytest.fail(f"Unexpected status code: {response.status_code}")
    
    def test_translate_status_endpoint(self, api_client):
        """Test GET /api/cases/{case_id}/translate/status returns progress"""
        response = api_client.get(
            f"{BASE_URL}/api/cases/{CASE_ID}/translate/status",
            params={"report_id": REPORT_ID, "language": "es"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        valid_statuses = ["completed", "running", "failed", "not_found"]
        assert data["status"] in valid_statuses, f"Status should be one of {valid_statuses}"
        print(f"Translation status check: {data['status']}")


class TestCaseAndDocumentEndpoints:
    """Test case and document CRUD operations"""
    
    def test_get_case(self, api_client):
        """Test GET /api/cases/{case_id}"""
        response = api_client.get(f"{BASE_URL}/api/cases/{CASE_ID}")
        if response.status_code == 200:
            data = response.json()
            assert "case_id" in data
            assert "title" in data
            print(f"Case retrieved: {data.get('title')}")
        elif response.status_code == 404:
            print("Case not found (may need different case_id)")
        else:
            print(f"Get case status: {response.status_code}")
    
    def test_get_documents(self, api_client):
        """Test GET /api/cases/{case_id}/documents"""
        response = api_client.get(f"{BASE_URL}/api/cases/{CASE_ID}/documents")
        if response.status_code == 200:
            data = response.json()
            assert isinstance(data, list)
            print(f"Documents retrieved: {len(data)} documents")
        elif response.status_code == 404:
            print("Case not found for documents")
        else:
            print(f"Get documents status: {response.status_code}")
    
    def test_get_reports(self, api_client):
        """Test GET /api/cases/{case_id}/reports"""
        response = api_client.get(f"{BASE_URL}/api/cases/{CASE_ID}/reports")
        if response.status_code == 200:
            data = response.json()
            assert isinstance(data, list)
            print(f"Reports retrieved: {len(data)} reports")
            # Check report types - should NOT have 'quick_brief' anymore
            report_types = [r.get("report_type") for r in data]
            assert "quick_brief" not in report_types, "Quick Brief should be deleted"
            print(f"Report types: {report_types}")
        elif response.status_code == 404:
            print("Case not found for reports")
        else:
            print(f"Get reports status: {response.status_code}")


class TestBarristerViewEndpoint:
    """Test Appellate Research Brief (formerly Barrister View) endpoint"""
    
    def test_barrister_view_endpoint(self, api_client):
        """Test GET /api/cases/{case_id}/reports/barrister-view"""
        response = api_client.get(f"{BASE_URL}/api/cases/{CASE_ID}/reports/barrister-view")
        # Could be 200 (exists), 404 (not generated), or 403 (locked)
        if response.status_code == 200:
            data = response.json()
            assert "report_id" in data or "status" in data
            print(f"Barrister view status: {data.get('status', 'completed')}")
        elif response.status_code == 404:
            print("Barrister view not generated yet (expected)")
        else:
            print(f"Barrister view status code: {response.status_code}")


class TestOCREndpoint:
    """Test OCR endpoint for document scanning"""
    
    def test_ocr_endpoint_exists(self, api_client):
        """Test that OCR endpoint exists and handles requests"""
        # Get documents first
        docs_response = api_client.get(f"{BASE_URL}/api/cases/{CASE_ID}/documents")
        if docs_response.status_code == 200:
            docs = docs_response.json()
            if docs:
                doc_id = docs[0].get("document_id")
                response = api_client.post(f"{BASE_URL}/api/cases/{CASE_ID}/documents/{doc_id}/ocr")
                # Should return 200 or 400 (no file data), not 404 or 500
                assert response.status_code in [200, 400], f"OCR endpoint returned {response.status_code}"
                print(f"OCR endpoint test: {response.status_code}")
            else:
                print("No documents to test OCR")
        else:
            print("Could not get documents for OCR test")


class TestAuthEndpoints:
    """Test authentication endpoints"""
    
    def test_auth_me_endpoint(self, api_client):
        """Test GET /api/auth/me returns user info"""
        response = api_client.get(f"{BASE_URL}/api/auth/me")
        if response.status_code == 200:
            data = response.json()
            assert "user_id" in data or "email" in data
            print(f"Auth me: {data.get('email', 'user authenticated')}")
        elif response.status_code == 401:
            print("Auth me: Not authenticated (session may have expired)")
        else:
            print(f"Auth me status: {response.status_code}")


class TestVisitorTracking:
    """Test visitor tracking endpoints"""
    
    def test_track_visit(self, api_client):
        """Test POST /api/analytics/track-visit"""
        response = api_client.post(f"{BASE_URL}/api/analytics/track-visit")
        assert response.status_code == 200
        data = response.json()
        assert data.get("status") in ["tracked", "error"]
        print(f"Track visit: {data.get('status')}")
    
    def test_visitor_count(self, api_client):
        """Test GET /api/analytics/visitor-count"""
        response = api_client.get(f"{BASE_URL}/api/analytics/visitor-count")
        assert response.status_code == 200
        data = response.json()
        assert "total_visitors" in data
        assert "registered_users" in data
        print(f"Visitor count: {data.get('total_visitors')} total, {data.get('registered_users')} registered")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
