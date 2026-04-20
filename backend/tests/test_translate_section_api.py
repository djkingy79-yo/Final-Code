"""
API-level tests for POST /api/cases/{case_id}/translate-section endpoint.
Tests authentication, authorization, validation, and response handling.
"""
import os
import pytest
import requests

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Test credentials
TEST_EMAIL = "djkingy79@gmail.com"
TEST_PASSWORD = "Grubbygrub88"


@pytest.fixture(scope="module")
def auth_token():
    """Get authentication token for test user."""
    response = requests.post(
        f"{BASE_URL}/api/auth/login",
        json={"email": TEST_EMAIL, "password": TEST_PASSWORD},
        timeout=30
    )
    if response.status_code != 200:
        pytest.skip(f"Login failed: {response.status_code} - {response.text}")
    # API returns session_token, not token
    return response.json().get("session_token")


@pytest.fixture(scope="module")
def auth_headers(auth_token):
    """Return headers with auth token."""
    return {"Authorization": f"Bearer {auth_token}", "Content-Type": "application/json"}


@pytest.fixture(scope="module")
def user_case_with_report(auth_headers):
    """Find a case with a completed report for the test user."""
    # Get user's cases
    cases_resp = requests.get(f"{BASE_URL}/api/cases", headers=auth_headers, timeout=30)
    if cases_resp.status_code != 200:
        pytest.skip("Could not fetch cases")
    
    cases = cases_resp.json()
    if not cases:
        pytest.skip("No cases found for test user")
    
    # Find a case with a completed report
    for case in cases:
        case_id = case.get("case_id")
        reports_resp = requests.get(f"{BASE_URL}/api/cases/{case_id}/reports", headers=auth_headers, timeout=30)
        if reports_resp.status_code == 200:
            reports = reports_resp.json()
            completed_reports = [r for r in reports if r.get("status") == "completed"]
            if completed_reports:
                return {
                    "case_id": case_id,
                    "report_id": completed_reports[0].get("report_id"),
                    "report": completed_reports[0]
                }
    
    pytest.skip("No case with completed report found")


class TestTranslateSectionAuth:
    """Authentication and authorization tests for translate-section endpoint."""
    
    def test_unauthenticated_returns_401(self, user_case_with_report):
        """Unauthenticated requests should return 401."""
        case_id = user_case_with_report["case_id"]
        response = requests.post(
            f"{BASE_URL}/api/cases/{case_id}/translate-section",
            json={
                "report_id": "test_report",
                "language": "es",
                "section_heading": "Test Section",
                "section_text": "Test content"
            },
            timeout=30
        )
        assert response.status_code == 401, f"Expected 401, got {response.status_code}: {response.text}"
    
    def test_invalid_case_returns_403_or_404(self, auth_headers):
        """Non-existent or non-owned case should return 403 or 404."""
        response = requests.post(
            f"{BASE_URL}/api/cases/nonexistent_case_id/translate-section",
            headers=auth_headers,
            json={
                "report_id": "test_report",
                "language": "es",
                "section_heading": "Test Section",
                "section_text": "Test content"
            },
            timeout=30
        )
        assert response.status_code in [403, 404], f"Expected 403/404, got {response.status_code}: {response.text}"


class TestTranslateSectionValidation:
    """Input validation tests for translate-section endpoint."""
    
    def test_unsupported_language_returns_400(self, auth_headers, user_case_with_report):
        """Unsupported language code should return 400."""
        case_id = user_case_with_report["case_id"]
        report_id = user_case_with_report["report_id"]
        
        response = requests.post(
            f"{BASE_URL}/api/cases/{case_id}/translate-section",
            headers=auth_headers,
            json={
                "report_id": report_id,
                "language": "xx",  # Invalid language code
                "section_heading": "Test Section",
                "section_text": "Test content"
            },
            timeout=30
        )
        assert response.status_code == 400, f"Expected 400, got {response.status_code}: {response.text}"
        assert "Unsupported" in response.json().get("detail", ""), "Expected 'Unsupported' in error detail"
    
    def test_empty_section_text_returns_400(self, auth_headers, user_case_with_report):
        """Empty section_text should return 400."""
        case_id = user_case_with_report["case_id"]
        report_id = user_case_with_report["report_id"]
        
        response = requests.post(
            f"{BASE_URL}/api/cases/{case_id}/translate-section",
            headers=auth_headers,
            json={
                "report_id": report_id,
                "language": "es",
                "section_heading": "Test Section",
                "section_text": "   "  # Whitespace only
            },
            timeout=30
        )
        assert response.status_code == 400, f"Expected 400, got {response.status_code}: {response.text}"
    
    def test_too_long_section_returns_400(self, auth_headers, user_case_with_report):
        """Section text >30000 chars should return 400."""
        case_id = user_case_with_report["case_id"]
        report_id = user_case_with_report["report_id"]
        
        response = requests.post(
            f"{BASE_URL}/api/cases/{case_id}/translate-section",
            headers=auth_headers,
            json={
                "report_id": report_id,
                "language": "es",
                "section_heading": "Test Section",
                "section_text": "x" * 30001  # Exceeds 30000 char limit
            },
            timeout=30
        )
        assert response.status_code == 400, f"Expected 400, got {response.status_code}: {response.text}"
        detail = response.json().get("detail", "").lower()
        assert "too long" in detail, f"Expected 'too long' in error detail, got: {detail}"
    
    def test_report_not_in_case_returns_404(self, auth_headers, user_case_with_report):
        """Report ID not belonging to case should return 404."""
        case_id = user_case_with_report["case_id"]
        
        response = requests.post(
            f"{BASE_URL}/api/cases/{case_id}/translate-section",
            headers=auth_headers,
            json={
                "report_id": "nonexistent_report_id_12345",
                "language": "es",
                "section_heading": "Test Section",
                "section_text": "Test content"
            },
            timeout=30
        )
        assert response.status_code == 404, f"Expected 404, got {response.status_code}: {response.text}"
        detail = response.json().get("detail", "")
        assert "Report not found" in detail, f"Expected 'Report not found' in detail, got: {detail}"


class TestTranslateSectionEnglishNoOp:
    """Test that English language short-circuits without LLM call."""
    
    def test_english_returns_original_unchanged(self, auth_headers, user_case_with_report):
        """Translating to English should return original text unchanged."""
        case_id = user_case_with_report["case_id"]
        report_id = user_case_with_report["report_id"]
        original_text = "The learned trial judge erred in law by failing to properly direct the jury."
        
        response = requests.post(
            f"{BASE_URL}/api/cases/{case_id}/translate-section",
            headers=auth_headers,
            json={
                "report_id": report_id,
                "language": "en",
                "section_heading": "Grounds of Appeal",
                "section_text": original_text
            },
            timeout=30
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert data.get("status") == "completed", f"Expected status 'completed', got: {data.get('status')}"
        assert data.get("translated_content") == original_text, "English translation should return original text"
        assert data.get("cached") is False, "English no-op should not be marked as cached"


class TestTranslateSectionResponseShape:
    """Test response structure for successful translations."""
    
    def test_response_has_required_fields(self, auth_headers, user_case_with_report):
        """Successful response should have all required fields."""
        case_id = user_case_with_report["case_id"]
        report_id = user_case_with_report["report_id"]
        
        # Use English to avoid actual LLM call
        response = requests.post(
            f"{BASE_URL}/api/cases/{case_id}/translate-section",
            headers=auth_headers,
            json={
                "report_id": report_id,
                "language": "en",
                "section_heading": "Test Section",
                "section_text": "Test content for response shape validation."
            },
            timeout=30
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        # Check required fields
        assert "status" in data, "Response missing 'status' field"
        assert "translated_content" in data, "Response missing 'translated_content' field"
        assert "cached" in data, "Response missing 'cached' field"
        
        # Verify types
        assert data["status"] == "completed", f"Expected status 'completed', got: {data['status']}"
        assert isinstance(data["translated_content"], str), "translated_content should be string"
        assert isinstance(data["cached"], bool), "cached should be boolean"


class TestTranslateSectionEndpoint:
    """Integration tests for the translate-section endpoint."""
    
    def test_endpoint_exists_and_accepts_post(self, auth_headers, user_case_with_report):
        """Verify endpoint exists and accepts POST requests."""
        case_id = user_case_with_report["case_id"]
        report_id = user_case_with_report["report_id"]
        
        # Use English to avoid LLM call
        response = requests.post(
            f"{BASE_URL}/api/cases/{case_id}/translate-section",
            headers=auth_headers,
            json={
                "report_id": report_id,
                "language": "en",
                "section_heading": "Test",
                "section_text": "Test"
            },
            timeout=30
        )
        # Should not be 404 (endpoint not found) or 405 (method not allowed)
        assert response.status_code not in [404, 405], f"Endpoint issue: {response.status_code}"
    
    def test_supported_languages_list(self):
        """Verify /api/languages endpoint returns supported languages."""
        response = requests.get(f"{BASE_URL}/api/languages", timeout=30)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        assert "languages" in data, "Response missing 'languages' field"
        
        languages = data["languages"]
        assert len(languages) >= 20, f"Expected at least 20 languages, got {len(languages)}"
        
        # Check for some expected languages
        lang_codes = [l["code"] for l in languages]
        expected_codes = ["en", "es", "fr", "de", "zh", "ar", "hi", "ja", "ko"]
        for code in expected_codes:
            assert code in lang_codes, f"Expected language code '{code}' not found"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
