"""
Iteration 163 - Case Export Pack PDF and Multi-Language Translation Tests
Tests for:
1. GET /api/languages - returns list of 41 supported translation languages
2. GET /api/cases/{case_id}/export/case-pack - generates formatted PDF with all completed reports
3. POST /api/cases/{case_id}/translate - translates a report to a specified language
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Test credentials from review request
SESSION_TOKEN = "3d1561482bd64a14962214c76c074d78"  # Deb's session token
CASE_WITH_REPORTS = "case_f8bf63e9dcbe"  # Homann v R - has quick_summary, full_detailed, extensive_log, barrister_view
REPORT_ID_QUICK_SUMMARY = "rpt_8d8137ad2235"  # Report ID for quick_summary
CASE_WITHOUT_REPORTS = "case_44b2047065b2"  # Case with no reports


@pytest.fixture
def auth_headers():
    """Return headers with session token for authenticated requests"""
    return {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {SESSION_TOKEN}"
    }


class TestLanguagesEndpoint:
    """Tests for GET /api/languages endpoint"""
    
    def test_get_languages_returns_list(self, auth_headers):
        """Test that /api/languages returns a list of supported languages"""
        response = requests.get(f"{BASE_URL}/api/languages", headers=auth_headers)
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert "languages" in data, "Response should contain 'languages' key"
        
        languages = data["languages"]
        assert isinstance(languages, list), "Languages should be a list"
        assert len(languages) >= 40, f"Expected at least 40 languages, got {len(languages)}"
        
        # Check structure of language objects
        for lang in languages[:5]:  # Check first 5
            assert "code" in lang, "Each language should have a 'code'"
            assert "name" in lang, "Each language should have a 'name'"
    
    def test_languages_includes_common_languages(self, auth_headers):
        """Test that common languages are included in the list"""
        response = requests.get(f"{BASE_URL}/api/languages", headers=auth_headers)
        
        assert response.status_code == 200
        
        data = response.json()
        languages = data["languages"]
        
        # Extract language codes
        codes = [lang["code"] for lang in languages]
        
        # Check for common languages
        expected_codes = ["es", "fr", "de", "zh", "ja", "ko", "ar", "hi", "vi", "th"]
        for code in expected_codes:
            assert code in codes, f"Expected language code '{code}' to be in the list"
    
    def test_languages_includes_english(self, auth_headers):
        """Test that English is included (even though translation to English is rejected)"""
        response = requests.get(f"{BASE_URL}/api/languages", headers=auth_headers)
        
        assert response.status_code == 200
        
        data = response.json()
        languages = data["languages"]
        codes = [lang["code"] for lang in languages]
        
        assert "en" in codes, "English should be in the language list"


class TestCaseExportPackEndpoint:
    """Tests for GET /api/cases/{case_id}/export/case-pack endpoint"""
    
    def test_case_pack_returns_pdf_for_case_with_reports(self, auth_headers):
        """Test that case-pack returns a PDF for a case with completed reports"""
        response = requests.get(
            f"{BASE_URL}/api/cases/{CASE_WITH_REPORTS}/export/case-pack",
            headers=auth_headers,
            timeout=120
        )
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        # Check content type is PDF
        content_type = response.headers.get("Content-Type", "")
        assert "application/pdf" in content_type, f"Expected PDF content type, got {content_type}"
        
        # Check content disposition header
        content_disposition = response.headers.get("Content-Disposition", "")
        assert "attachment" in content_disposition, "Should have attachment disposition"
        assert ".pdf" in content_disposition.lower(), "Filename should have .pdf extension"
        
        # Check that we got actual content
        assert len(response.content) > 10000, f"PDF should be substantial, got {len(response.content)} bytes"
    
    def test_case_pack_returns_404_for_case_without_reports(self, auth_headers):
        """Test that case-pack returns 404 for a case with no completed reports"""
        response = requests.get(
            f"{BASE_URL}/api/cases/{CASE_WITHOUT_REPORTS}/export/case-pack",
            headers=auth_headers,
            timeout=60
        )
        
        assert response.status_code == 404, f"Expected 404, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert "detail" in data, "Error response should have 'detail'"
        assert "report" in data["detail"].lower(), "Error should mention reports"
    
    def test_case_pack_requires_authentication(self):
        """Test that case-pack requires authentication"""
        response = requests.get(
            f"{BASE_URL}/api/cases/{CASE_WITH_REPORTS}/export/case-pack",
            timeout=30
        )
        
        assert response.status_code == 401, f"Expected 401, got {response.status_code}"
    
    def test_case_pack_returns_404_for_invalid_case(self, auth_headers):
        """Test that case-pack returns 404 for non-existent case"""
        response = requests.get(
            f"{BASE_URL}/api/cases/invalid_case_id_12345/export/case-pack",
            headers=auth_headers,
            timeout=30
        )
        
        assert response.status_code == 404, f"Expected 404, got {response.status_code}"


class TestTranslateEndpoint:
    """Tests for POST /api/cases/{case_id}/translate endpoint"""
    
    def test_translate_rejects_english_language(self, auth_headers):
        """Test that translation to English is rejected"""
        response = requests.post(
            f"{BASE_URL}/api/cases/{CASE_WITH_REPORTS}/translate",
            headers=auth_headers,
            json={
                "language": "en",
                "report_id": REPORT_ID_QUICK_SUMMARY
            },
            timeout=30
        )
        
        assert response.status_code == 400, f"Expected 400, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert "detail" in data, "Error response should have 'detail'"
        assert "english" in data["detail"].lower(), "Error should mention English"
    
    def test_translate_rejects_invalid_language_code(self, auth_headers):
        """Test that invalid language codes are rejected"""
        response = requests.post(
            f"{BASE_URL}/api/cases/{CASE_WITH_REPORTS}/translate",
            headers=auth_headers,
            json={
                "language": "xyz_invalid",
                "report_id": REPORT_ID_QUICK_SUMMARY
            },
            timeout=30
        )
        
        assert response.status_code == 400, f"Expected 400, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert "detail" in data, "Error response should have 'detail'"
        assert "unsupported" in data["detail"].lower() or "language" in data["detail"].lower(), \
            f"Error should mention unsupported language: {data['detail']}"
    
    def test_translate_requires_authentication(self):
        """Test that translate requires authentication"""
        response = requests.post(
            f"{BASE_URL}/api/cases/{CASE_WITH_REPORTS}/translate",
            json={
                "language": "es",
                "report_id": REPORT_ID_QUICK_SUMMARY
            },
            timeout=30
        )
        
        assert response.status_code == 401, f"Expected 401, got {response.status_code}"
    
    def test_translate_requires_report_id(self, auth_headers):
        """Test that translate requires report_id in body"""
        response = requests.post(
            f"{BASE_URL}/api/cases/{CASE_WITH_REPORTS}/translate",
            headers=auth_headers,
            json={
                "language": "es"
                # Missing report_id
            },
            timeout=30
        )
        
        assert response.status_code == 422, f"Expected 422 for validation error, got {response.status_code}"
    
    def test_translate_requires_language(self, auth_headers):
        """Test that translate requires language in body"""
        response = requests.post(
            f"{BASE_URL}/api/cases/{CASE_WITH_REPORTS}/translate",
            headers=auth_headers,
            json={
                "report_id": REPORT_ID_QUICK_SUMMARY
                # Missing language
            },
            timeout=30
        )
        
        assert response.status_code == 422, f"Expected 422 for validation error, got {response.status_code}"
    
    def test_translate_returns_404_for_invalid_report(self, auth_headers):
        """Test that translate returns 404 for non-existent report"""
        response = requests.post(
            f"{BASE_URL}/api/cases/{CASE_WITH_REPORTS}/translate",
            headers=auth_headers,
            json={
                "language": "es",
                "report_id": "invalid_report_id_12345"
            },
            timeout=30
        )
        
        assert response.status_code == 404, f"Expected 404, got {response.status_code}: {response.text}"
    
    def test_translate_accepts_valid_request(self, auth_headers):
        """Test that translate accepts a valid request (may take time for actual translation)"""
        # Note: This test verifies the endpoint accepts the request
        # Actual translation takes 30-60s, so we just verify it doesn't immediately fail
        response = requests.post(
            f"{BASE_URL}/api/cases/{CASE_WITH_REPORTS}/translate",
            headers=auth_headers,
            json={
                "language": "es",  # Spanish
                "report_id": REPORT_ID_QUICK_SUMMARY
            },
            timeout=180  # Allow time for translation
        )
        
        # Should either succeed (200) or be processing
        assert response.status_code in [200, 202], f"Expected 200 or 202, got {response.status_code}: {response.text}"
        
        if response.status_code == 200:
            data = response.json()
            assert "translated_content" in data, "Response should contain translated_content"
            assert "language" in data, "Response should contain language code"
            assert "language_name" in data, "Response should contain language_name"
            assert data["language"] == "es", "Language code should be 'es'"
            assert len(data["translated_content"]) > 100, "Translated content should be substantial"


class TestExportPreviewEndpoint:
    """Tests for GET /api/cases/{case_id}/export/preview endpoint (existing feature)"""
    
    def test_export_preview_returns_counts(self, auth_headers):
        """Test that export preview returns item counts"""
        response = requests.get(
            f"{BASE_URL}/api/cases/{CASE_WITH_REPORTS}/export/preview",
            headers=auth_headers,
            timeout=30
        )
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        
        # Check expected fields
        expected_fields = ["documents", "timeline_events", "grounds_of_merit", "notes", "reports", "templates"]
        for field in expected_fields:
            assert field in data, f"Response should contain '{field}'"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
