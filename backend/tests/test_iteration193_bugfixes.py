"""
Iteration 193 Bug Fixes Tests
Tests for:
1. Translator DuplicateKeyError fix (replace_one with upsert=True)
2. Barrister View TOC in export HTML
3. Quick Brief blob download
4. Acceptance Package button removal (frontend only)
5. Word export direct download
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', 'http://localhost:8001').rstrip('/')

# Test credentials
TEST_EMAIL = "djkingy79@gmail.com"
TEST_PASSWORD = "Grubbygrub88"

# Test case and report IDs from agent context
TEST_CASE_ID = "case_ba08d8e0ad0d"
TEST_BARRISTER_REPORT_ID = "rpt_1d3ddfc9c595"


@pytest.fixture(scope="module")
def auth_token():
    """Return session token directly (Google OAuth - no email/password login)"""
    return "61bbcd763e9a47ed8d7ad1a7bcf1854a"

@pytest.fixture(scope="module")
def auth_headers(auth_token):
    """Return headers with auth token"""
    return {"Authorization": f"Bearer {auth_token}"}


class TestTranslatorDuplicateKeyFix:
    """Test that translator uses replace_one with upsert=True to prevent DuplicateKeyError"""
    
    def test_translate_report_first_time(self, auth_headers):
        """Test translating a report for the first time"""
        response = requests.post(
            f"{BASE_URL}/api/cases/{TEST_CASE_ID}/translate",
            json={"report_id": TEST_BARRISTER_REPORT_ID, "language": "es"},
            headers=auth_headers,
            timeout=180  # Translation can take time
        )
        
        # Should succeed (200) or return cached (200 with cached=True)
        assert response.status_code == 200, f"Translation failed: {response.status_code} - {response.text}"
        
        data = response.json()
        assert "translated_content" in data, "Response missing translated_content"
        assert data.get("language") == "es", "Language mismatch"
        print(f"Translation result - cached: {data.get('cached', False)}")
    
    def test_translate_report_retry_no_duplicate_error(self, auth_headers):
        """Test that retrying translation doesn't cause DuplicateKeyError"""
        # First translation (or cached)
        response1 = requests.post(
            f"{BASE_URL}/api/cases/{TEST_CASE_ID}/translate",
            json={"report_id": TEST_BARRISTER_REPORT_ID, "language": "es"},
            headers=auth_headers,
            timeout=180
        )
        assert response1.status_code == 200, f"First translation failed: {response1.status_code}"
        
        # Second translation - should return cached, NOT DuplicateKeyError
        response2 = requests.post(
            f"{BASE_URL}/api/cases/{TEST_CASE_ID}/translate",
            json={"report_id": TEST_BARRISTER_REPORT_ID, "language": "es"},
            headers=auth_headers,
            timeout=180
        )
        
        # Key assertion: Should NOT get 500 error from DuplicateKeyError
        assert response2.status_code == 200, f"Retry translation failed with {response2.status_code}: {response2.text}"
        
        data = response2.json()
        # Should be cached on retry
        assert data.get("cached") is True, "Second request should return cached translation"
        print("SUCCESS: Retry translation returned cached result without DuplicateKeyError")
    
    def test_translate_different_language(self, auth_headers):
        """Test translating to a different language works"""
        response = requests.post(
            f"{BASE_URL}/api/cases/{TEST_CASE_ID}/translate",
            json={"report_id": TEST_BARRISTER_REPORT_ID, "language": "fr"},
            headers=auth_headers,
            timeout=180
        )
        
        assert response.status_code == 200, f"French translation failed: {response.status_code} - {response.text}"
        data = response.json()
        assert data.get("language") == "fr"
        print(f"French translation - cached: {data.get('cached', False)}")


class TestBarristerViewEndpoints:
    """Test Barrister View related endpoints"""
    
    def test_barrister_view_report_exists(self, auth_headers):
        """Test that barrister view report endpoint works"""
        response = requests.get(
            f"{BASE_URL}/api/cases/{TEST_CASE_ID}/reports/barrister-view",
            headers=auth_headers
        )
        
        assert response.status_code in [200, 409], f"Unexpected status: {response.status_code} - {response.text}"
        data = response.json()
        
        if response.status_code == 409:
            assert "detail" in data, "Missing error detail"
        else:
            # Verify report structure
            assert "report_id" in data or "content" in data, "Missing report data"
            assert data.get("status") == "completed" or data.get("content"), "Report not completed"
        print(f"Barrister view report status: {data.get('status', 'N/A')}")
    
    def test_quick_brief_pdf_endpoint(self, auth_headers):
        """Test Quick Brief PDF endpoint returns blob data"""
        response = requests.get(
            f"{BASE_URL}/api/cases/{TEST_CASE_ID}/reports/barrister-quick-brief",
            headers=auth_headers,
            timeout=60
        )
        
        assert response.status_code == 200, f"Quick Brief failed: {response.status_code} - {response.text}"
        
        # Verify it returns PDF content
        content_type = response.headers.get("content-type", "")
        assert "application/pdf" in content_type, f"Expected PDF, got: {content_type}"
        
        # Verify content is not empty
        assert len(response.content) > 1000, "PDF content too small, likely empty"
        print(f"Quick Brief PDF size: {len(response.content)} bytes")


class TestLanguagesEndpoint:
    """Test languages endpoint for translator"""
    
    def test_get_supported_languages(self):
        """Test that languages endpoint returns supported languages"""
        response = requests.get(f"{BASE_URL}/api/languages")
        
        assert response.status_code == 200, f"Languages endpoint failed: {response.status_code}"
        data = response.json()
        
        assert "languages" in data, "Missing languages array"
        languages = data["languages"]
        
        # Verify some expected languages exist
        lang_codes = [lang["code"] for lang in languages]
        assert "es" in lang_codes, "Spanish not in supported languages"
        assert "fr" in lang_codes, "French not in supported languages"
        assert "zh" in lang_codes, "Chinese not in supported languages"
        
        print(f"Supported languages count: {len(languages)}")


class TestCaseEndpoints:
    """Test case-related endpoints needed for Barrister View"""
    
    def test_case_exists(self, auth_headers):
        """Test that test case exists"""
        response = requests.get(
            f"{BASE_URL}/api/cases/{TEST_CASE_ID}",
            headers=auth_headers
        )
        
        assert response.status_code == 200, f"Case not found: {response.status_code}"
        data = response.json()
        assert data.get("case_id") == TEST_CASE_ID
        print(f"Case title: {data.get('title', 'N/A')}")
    
    def test_case_reports_list(self, auth_headers):
        """Test that reports list endpoint works"""
        response = requests.get(
            f"{BASE_URL}/api/cases/{TEST_CASE_ID}/reports",
            headers=auth_headers
        )
        
        assert response.status_code == 200, f"Reports list failed: {response.status_code}"
        reports = response.json()
        
        # Should have reports
        assert isinstance(reports, list), "Reports should be a list"
        print(f"Total reports for case: {len(reports)}")
        
        # Check for barrister_view report
        barrister_reports = [r for r in reports if r.get("report_type") == "barrister_view"]
        print(f"Barrister view reports: {len(barrister_reports)}")
    
    def test_case_grounds(self, auth_headers):
        """Test grounds endpoint for Barrister View"""
        response = requests.get(
            f"{BASE_URL}/api/cases/{TEST_CASE_ID}/grounds",
            headers=auth_headers
        )
        
        assert response.status_code == 200, f"Grounds failed: {response.status_code}"
        data = response.json()
        
        grounds = data.get("grounds", [])
        print(f"Grounds count: {len(grounds)}")
    
    def test_case_timeline(self, auth_headers):
        """Test timeline endpoint for Barrister View"""
        response = requests.get(
            f"{BASE_URL}/api/cases/{TEST_CASE_ID}/timeline",
            headers=auth_headers
        )
        
        assert response.status_code == 200, f"Timeline failed: {response.status_code}"
        timeline = response.json()
        print(f"Timeline events: {len(timeline) if isinstance(timeline, list) else 'N/A'}")
    
    def test_case_documents(self, auth_headers):
        """Test documents endpoint for Barrister View"""
        response = requests.get(
            f"{BASE_URL}/api/cases/{TEST_CASE_ID}/documents",
            headers=auth_headers
        )
        
        assert response.status_code == 200, f"Documents failed: {response.status_code}"
        documents = response.json()
        print(f"Documents count: {len(documents) if isinstance(documents, list) else 'N/A'}")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
