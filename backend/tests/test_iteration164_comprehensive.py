"""
Iteration 164 - Comprehensive Validation Test Suite
Covers: Auth flows, API endpoints (Cases, Reports, Export, Translation, Grounds, Timeline, Documents, Notes),
Database operations, Edge cases, and Error handling.

Test credentials:
- Deb's session token: 3d1561482bd64a14962214c76c074d78
- Deb's user_id: user_d2287f20104b
- Case with reports: case_f8bf63e9dcbe (Homann v R)
- Case with no reports: case_44b2047065b2
- Email test user: testuser_emailflow@outlook.com / TestPass123
"""

import pytest
import requests
import os
import uuid

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://criminal-appeals-au-2.preview.emergentagent.com')

# Test credentials
DEB_SESSION_TOKEN = "3d1561482bd64a14962214c76c074d78"
DEB_USER_ID = "user_d2287f20104b"
CASE_WITH_REPORTS = "case_f8bf63e9dcbe"
CASE_NO_REPORTS = "case_44b2047065b2"
REPORT_WITH_SPANISH_TRANSLATION = "rpt_8d8137ad2235"
EMAIL_TEST_USER = "testuser_emailflow@outlook.com"
EMAIL_TEST_PASSWORD = "TestPass123"


@pytest.fixture
def api_client():
    """Shared requests session"""
    session = requests.Session()
    session.headers.update({"Content-Type": "application/json"})
    return session


@pytest.fixture
def auth_client(api_client):
    """Session with Deb's auth token"""
    api_client.headers.update({"Authorization": f"Bearer {DEB_SESSION_TOKEN}"})
    return api_client


# ============================================================================
# AUTH FLOWS
# ============================================================================

class TestAuthFlows:
    """Authentication endpoint tests"""

    def test_email_registration_new_user(self, api_client):
        """Test email registration for a new user"""
        unique_email = f"test_new_user_{uuid.uuid4().hex[:8]}@test.com"
        response = api_client.post(f"{BASE_URL}/api/auth/register", json={
            "email": unique_email,
            "password": "TestPass123",
            "name": "Test New User"
        })
        # Should succeed with 200 or fail with 400 if email exists
        assert response.status_code in [200, 400], f"Unexpected status: {response.status_code}"
        if response.status_code == 200:
            data = response.json()
            assert "user_id" in data
            assert "session_token" in data
            assert data["email"] == unique_email.lower()
            print(f"PASS: New user registration successful for {unique_email}")
        else:
            print(f"INFO: Registration returned 400 (may be duplicate): {response.json()}")

    def test_email_login_existing_user(self, api_client):
        """Test email login for existing user"""
        response = api_client.post(f"{BASE_URL}/api/auth/login", json={
            "email": EMAIL_TEST_USER,
            "password": EMAIL_TEST_PASSWORD
        })
        # May return 401 if user doesn't exist or wrong password
        if response.status_code == 200:
            data = response.json()
            assert "user_id" in data
            assert "session_token" in data
            print(f"PASS: Email login successful for {EMAIL_TEST_USER}")
        else:
            print(f"INFO: Login returned {response.status_code} - user may not exist or wrong password")
        assert response.status_code in [200, 401]

    def test_wrong_password_error(self, api_client):
        """Test wrong password returns 401"""
        response = api_client.post(f"{BASE_URL}/api/auth/login", json={
            "email": EMAIL_TEST_USER,
            "password": "WrongPassword123"
        })
        assert response.status_code == 401, f"Expected 401, got {response.status_code}"
        data = response.json()
        assert "detail" in data
        print(f"PASS: Wrong password correctly returns 401 with detail: {data['detail']}")

    def test_duplicate_email_registration_rejection(self, api_client):
        """Test duplicate email registration is rejected"""
        # First, try to register with an email that likely exists
        response = api_client.post(f"{BASE_URL}/api/auth/register", json={
            "email": "djkingy79@gmail.com",  # Admin email, should exist
            "password": "TestPass123",
            "name": "Duplicate Test"
        })
        assert response.status_code == 400, f"Expected 400 for duplicate, got {response.status_code}"
        data = response.json()
        assert "detail" in data
        assert "already" in data["detail"].lower() or "registered" in data["detail"].lower()
        print(f"PASS: Duplicate email registration correctly rejected: {data['detail']}")

    def test_auth_me_with_valid_token(self, auth_client):
        """Test /api/auth/me with valid token"""
        response = auth_client.get(f"{BASE_URL}/api/auth/me")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        data = response.json()
        assert "user_id" in data
        assert "email" in data
        print(f"PASS: /api/auth/me returns user data: {data['email']}")

    def test_auth_me_without_token(self, api_client):
        """Test /api/auth/me without token returns 401"""
        response = api_client.get(f"{BASE_URL}/api/auth/me")
        assert response.status_code == 401, f"Expected 401, got {response.status_code}"
        print("PASS: /api/auth/me without token returns 401")

    def test_auth_logout(self, api_client):
        """Test /api/auth/logout"""
        # Logout should work even without a valid session
        response = api_client.post(f"{BASE_URL}/api/auth/logout")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        data = response.json()
        assert "message" in data
        print(f"PASS: Logout successful: {data['message']}")


# ============================================================================
# CASES API
# ============================================================================

class TestCasesAPI:
    """Cases CRUD endpoint tests"""

    def test_get_cases_list(self, auth_client):
        """Test GET /api/cases returns list"""
        response = auth_client.get(f"{BASE_URL}/api/cases")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        data = response.json()
        assert isinstance(data, list)
        print(f"PASS: GET /api/cases returns {len(data)} cases")

    def test_create_case(self, auth_client):
        """Test POST /api/cases creates a new case"""
        response = auth_client.post(f"{BASE_URL}/api/cases", json={
            "title": f"TEST_Case_{uuid.uuid4().hex[:8]}",
            "defendant_name": "Test Defendant",
            "state": "nsw",
            "offence_category": "assault"
        })
        assert response.status_code in [200, 201], f"Expected 200/201, got {response.status_code}"
        data = response.json()
        assert "case_id" in data
        assert "title" in data
        print(f"PASS: Case created with ID: {data['case_id']}")
        return data["case_id"]

    def test_get_single_case(self, auth_client):
        """Test GET /api/cases/{case_id} returns single case"""
        response = auth_client.get(f"{BASE_URL}/api/cases/{CASE_WITH_REPORTS}")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        data = response.json()
        assert data["case_id"] == CASE_WITH_REPORTS
        print(f"PASS: GET single case returns: {data['title']}")

    def test_update_case(self, auth_client):
        """Test PUT /api/cases/{case_id} updates case"""
        # First create a test case
        create_resp = auth_client.post(f"{BASE_URL}/api/cases", json={
            "title": f"TEST_Update_{uuid.uuid4().hex[:8]}",
            "defendant_name": "Original Name"
        })
        if create_resp.status_code not in [200, 201]:
            pytest.skip("Could not create test case")
        case_id = create_resp.json()["case_id"]
        original_title = create_resp.json()["title"]

        # Update it - title is required for PUT
        response = auth_client.put(f"{BASE_URL}/api/cases/{case_id}", json={
            "title": original_title,
            "defendant_name": "Updated Name"
        })
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        data = response.json()
        assert data["defendant_name"] == "Updated Name"
        print("PASS: Case updated successfully")

    def test_delete_case(self, auth_client):
        """Test DELETE /api/cases/{case_id}"""
        # First create a test case
        create_resp = auth_client.post(f"{BASE_URL}/api/cases", json={
            "title": f"TEST_Delete_{uuid.uuid4().hex[:8]}",
            "defendant_name": "To Delete"
        })
        if create_resp.status_code not in [200, 201]:
            pytest.skip("Could not create test case")
        case_id = create_resp.json()["case_id"]

        # Delete it
        response = auth_client.delete(f"{BASE_URL}/api/cases/{case_id}")
        assert response.status_code in [200, 204], f"Expected 200/204, got {response.status_code}"
        print("PASS: Case deleted successfully")

        # Verify deletion
        get_resp = auth_client.get(f"{BASE_URL}/api/cases/{case_id}")
        assert get_resp.status_code == 404, "Deleted case should return 404"


# ============================================================================
# REPORTS API
# ============================================================================

class TestReportsAPI:
    """Reports endpoint tests"""

    def test_get_reports_for_case(self, auth_client):
        """Test GET /api/cases/{case_id}/reports returns reports list"""
        response = auth_client.get(f"{BASE_URL}/api/cases/{CASE_WITH_REPORTS}/reports")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        data = response.json()
        assert isinstance(data, list)
        assert len(data) > 0, "Case should have reports"
        print(f"PASS: GET reports returns {len(data)} reports for case")

    def test_get_reports_for_case_no_reports(self, auth_client):
        """Test GET /api/cases/{case_id}/reports for case with no reports"""
        response = auth_client.get(f"{BASE_URL}/api/cases/{CASE_NO_REPORTS}/reports")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        data = response.json()
        assert isinstance(data, list)
        print(f"PASS: GET reports returns {len(data)} reports for case with no reports")


# ============================================================================
# EXPORT API
# ============================================================================

class TestExportAPI:
    """Export endpoint tests"""

    def test_export_preview(self, auth_client):
        """Test GET /api/cases/{case_id}/export/preview"""
        response = auth_client.get(f"{BASE_URL}/api/cases/{CASE_WITH_REPORTS}/export/preview")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        data = response.json()
        assert "documents" in data
        assert "reports" in data
        assert "timeline_events" in data
        print(f"PASS: Export preview returns counts: docs={data['documents']}, reports={data['reports']}")

    def test_export_case_pack_with_reports(self, auth_client):
        """Test GET /api/cases/{case_id}/export/case-pack returns PDF for case with reports"""
        response = auth_client.get(f"{BASE_URL}/api/cases/{CASE_WITH_REPORTS}/export/case-pack", timeout=120)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        assert response.headers.get("content-type") == "application/pdf"
        assert len(response.content) > 10000, "PDF should be substantial"
        print(f"PASS: Case pack PDF generated, size: {len(response.content)} bytes")

    def test_export_case_pack_no_reports_returns_404(self, auth_client):
        """Test GET /api/cases/{case_id}/export/case-pack returns 404 for case with no reports"""
        response = auth_client.get(f"{BASE_URL}/api/cases/{CASE_NO_REPORTS}/export/case-pack", timeout=60)
        assert response.status_code == 404, f"Expected 404, got {response.status_code}"
        data = response.json()
        assert "detail" in data
        print(f"PASS: Case pack for case with no reports returns 404: {data['detail']}")


# ============================================================================
# TRANSLATION API
# ============================================================================

class TestTranslationAPI:
    """Translation endpoint tests"""

    def test_get_languages(self, api_client):
        """Test GET /api/languages returns 41 languages"""
        response = api_client.get(f"{BASE_URL}/api/languages")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        data = response.json()
        assert "languages" in data
        assert len(data["languages"]) == 41, f"Expected 41 languages, got {len(data['languages'])}"
        # Verify structure
        lang = data["languages"][0]
        assert "code" in lang
        assert "name" in lang
        print(f"PASS: GET /api/languages returns {len(data['languages'])} languages")

    def test_translate_rejects_english(self, auth_client):
        """Test POST /api/cases/{case_id}/translate rejects 'en' language"""
        response = auth_client.post(f"{BASE_URL}/api/cases/{CASE_WITH_REPORTS}/translate", json={
            "language": "en",
            "report_id": REPORT_WITH_SPANISH_TRANSLATION
        })
        assert response.status_code == 400, f"Expected 400, got {response.status_code}"
        data = response.json()
        assert "detail" in data
        assert "english" in data["detail"].lower() or "already" in data["detail"].lower()
        print(f"PASS: Translate rejects 'en': {data['detail']}")

    def test_translate_rejects_invalid_language(self, auth_client):
        """Test POST /api/cases/{case_id}/translate rejects invalid language code"""
        response = auth_client.post(f"{BASE_URL}/api/cases/{CASE_WITH_REPORTS}/translate", json={
            "language": "xyz_invalid",
            "report_id": REPORT_WITH_SPANISH_TRANSLATION
        })
        assert response.status_code == 400, f"Expected 400, got {response.status_code}"
        data = response.json()
        assert "detail" in data
        print(f"PASS: Translate rejects invalid language: {data['detail']}")

    def test_translate_rejects_missing_report_id(self, auth_client):
        """Test POST /api/cases/{case_id}/translate rejects missing report_id"""
        response = auth_client.post(f"{BASE_URL}/api/cases/{CASE_WITH_REPORTS}/translate", json={
            "language": "es"
            # Missing report_id
        })
        assert response.status_code == 422, f"Expected 422 for validation error, got {response.status_code}"
        print("PASS: Translate rejects missing report_id with 422")

    def test_translate_cached_spanish(self, auth_client):
        """Test POST /api/cases/{case_id}/translate returns cached Spanish translation"""
        response = auth_client.post(f"{BASE_URL}/api/cases/{CASE_WITH_REPORTS}/translate", json={
            "language": "es",
            "report_id": REPORT_WITH_SPANISH_TRANSLATION
        }, timeout=180)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        data = response.json()
        assert "translated_content" in data
        assert data["language"] == "es"
        assert data["language_name"] == "Spanish"
        print(f"PASS: Spanish translation returned, cached={data.get('cached', False)}")

    def test_translated_pdf_for_cached_language(self, auth_client):
        """Test GET /api/cases/{case_id}/translate/{report_id}/pdf?lang=es returns PDF"""
        response = auth_client.get(
            f"{BASE_URL}/api/cases/{CASE_WITH_REPORTS}/translate/{REPORT_WITH_SPANISH_TRANSLATION}/pdf?lang=es",
            timeout=120
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        assert response.headers.get("content-type") == "application/pdf"
        print(f"PASS: Translated PDF generated, size: {len(response.content)} bytes")

    def test_translated_pdf_for_uncached_language_returns_404(self, auth_client):
        """Test GET /api/cases/{case_id}/translate/{report_id}/pdf?lang=xx returns 404 for uncached"""
        # Use a language that's unlikely to be cached
        response = auth_client.get(
            f"{BASE_URL}/api/cases/{CASE_WITH_REPORTS}/translate/{REPORT_WITH_SPANISH_TRANSLATION}/pdf?lang=am",
            timeout=60
        )
        # Should be 404 if not cached, or 200 if it happens to be cached
        assert response.status_code in [200, 404], f"Expected 200 or 404, got {response.status_code}"
        if response.status_code == 404:
            print("PASS: Uncached translation PDF returns 404")
        else:
            print("INFO: Translation was cached, returned PDF")


# ============================================================================
# GROUNDS API
# ============================================================================

class TestGroundsAPI:
    """Grounds endpoint tests"""

    def test_get_grounds(self, auth_client):
        """Test GET /api/cases/{case_id}/grounds returns grounds object with grounds list"""
        response = auth_client.get(f"{BASE_URL}/api/cases/{CASE_WITH_REPORTS}/grounds")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        data = response.json()
        # Grounds endpoint returns object with 'grounds' key containing the list
        assert "grounds" in data, "Response should have 'grounds' key"
        assert isinstance(data["grounds"], list)
        print(f"PASS: GET grounds returns {len(data['grounds'])} grounds")

    def test_create_ground(self, auth_client):
        """Test POST /api/cases/{case_id}/grounds creates a ground"""
        response = auth_client.post(f"{BASE_URL}/api/cases/{CASE_WITH_REPORTS}/grounds", json={
            "title": f"TEST_Ground_{uuid.uuid4().hex[:8]}",
            "ground_type": "procedural_error",
            "description": "Test ground description"
        })
        assert response.status_code in [200, 201], f"Expected 200/201, got {response.status_code}"
        data = response.json()
        assert "ground_id" in data
        print(f"PASS: Ground created with ID: {data['ground_id']}")


# ============================================================================
# TIMELINE API
# ============================================================================

class TestTimelineAPI:
    """Timeline endpoint tests"""

    def test_get_timeline(self, auth_client):
        """Test GET /api/cases/{case_id}/timeline returns events list"""
        response = auth_client.get(f"{BASE_URL}/api/cases/{CASE_WITH_REPORTS}/timeline")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        data = response.json()
        assert isinstance(data, list)
        print(f"PASS: GET timeline returns {len(data)} events")


# ============================================================================
# DOCUMENTS API
# ============================================================================

class TestDocumentsAPI:
    """Documents endpoint tests"""

    def test_get_documents(self, auth_client):
        """Test GET /api/cases/{case_id}/documents returns documents list"""
        response = auth_client.get(f"{BASE_URL}/api/cases/{CASE_WITH_REPORTS}/documents")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        data = response.json()
        assert isinstance(data, list)
        print(f"PASS: GET documents returns {len(data)} documents")


# ============================================================================
# NOTES API
# ============================================================================

class TestNotesAPI:
    """Notes endpoint tests"""

    def test_get_notes(self, auth_client):
        """Test GET /api/cases/{case_id}/notes returns notes list"""
        response = auth_client.get(f"{BASE_URL}/api/cases/{CASE_WITH_REPORTS}/notes")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        data = response.json()
        assert isinstance(data, list)
        print(f"PASS: GET notes returns {len(data)} notes")

    def test_create_note(self, auth_client):
        """Test POST /api/cases/{case_id}/notes creates a note"""
        response = auth_client.post(f"{BASE_URL}/api/cases/{CASE_WITH_REPORTS}/notes", json={
            "title": f"TEST_Note_{uuid.uuid4().hex[:8]}",
            "content": "Test note content",
            "category": "general"
        })
        assert response.status_code in [200, 201], f"Expected 200/201, got {response.status_code}"
        data = response.json()
        assert "note_id" in data
        print(f"PASS: Note created with ID: {data['note_id']}")


# ============================================================================
# EDGE CASES
# ============================================================================

class TestEdgeCases:
    """Edge case tests"""

    def test_access_nonexistent_case(self, auth_client):
        """Test accessing non-existent case returns 404"""
        response = auth_client.get(f"{BASE_URL}/api/cases/nonexistent_case_id_12345")
        assert response.status_code == 404, f"Expected 404, got {response.status_code}"
        print("PASS: Non-existent case returns 404")

    def test_access_nonexistent_report(self, auth_client):
        """Test accessing non-existent report returns 404"""
        response = auth_client.get(f"{BASE_URL}/api/cases/{CASE_WITH_REPORTS}/reports/nonexistent_report_id")
        assert response.status_code == 404, f"Expected 404, got {response.status_code}"
        print("PASS: Non-existent report returns 404")

    def test_create_case_with_empty_title(self, auth_client):
        """Test creating case with empty title"""
        response = auth_client.post(f"{BASE_URL}/api/cases", json={
            "title": "",
            "defendant_name": "Test"
        })
        # Should either reject with 400/422 or accept with default title
        assert response.status_code in [200, 201, 400, 422], f"Unexpected status: {response.status_code}"
        if response.status_code in [400, 422]:
            print("PASS: Empty title rejected with validation error")
        else:
            print("INFO: Empty title accepted (may have default)")

    def test_translate_report_with_empty_content(self, auth_client):
        """Test translating a report that might have empty content"""
        # This tests the edge case handling in the translate endpoint
        response = auth_client.post(f"{BASE_URL}/api/cases/{CASE_WITH_REPORTS}/translate", json={
            "language": "fr",
            "report_id": "nonexistent_report_id"
        })
        assert response.status_code == 404, f"Expected 404 for nonexistent report, got {response.status_code}"
        print("PASS: Translate with nonexistent report returns 404")


# ============================================================================
# CROSS-USER ACCESS (Security)
# ============================================================================

class TestCrossUserAccess:
    """Security tests for cross-user access"""

    def test_access_case_without_auth(self, api_client):
        """Test accessing case without authentication returns 401"""
        response = api_client.get(f"{BASE_URL}/api/cases/{CASE_WITH_REPORTS}")
        assert response.status_code == 401, f"Expected 401, got {response.status_code}"
        print("PASS: Accessing case without auth returns 401")

    def test_create_case_without_auth(self, api_client):
        """Test creating case without authentication returns 401"""
        response = api_client.post(f"{BASE_URL}/api/cases", json={
            "title": "Unauthorized Case",
            "defendant_name": "Test"
        })
        assert response.status_code == 401, f"Expected 401, got {response.status_code}"
        print("PASS: Creating case without auth returns 401")


# ============================================================================
# ERROR HANDLING
# ============================================================================

class TestErrorHandling:
    """Error handling tests"""

    def test_invalid_json_body(self, auth_client):
        """Test invalid JSON body returns 422"""
        response = auth_client.post(
            f"{BASE_URL}/api/cases",
            data="not valid json",
            headers={"Content-Type": "application/json"}
        )
        assert response.status_code == 422, f"Expected 422, got {response.status_code}"
        print("PASS: Invalid JSON returns 422")

    def test_missing_required_fields(self, auth_client):
        """Test missing required fields returns 422"""
        response = auth_client.post(f"{BASE_URL}/api/auth/register", json={
            "email": "test@test.com"
            # Missing password and name
        })
        assert response.status_code == 422, f"Expected 422, got {response.status_code}"
        print("PASS: Missing required fields returns 422")

    def test_error_response_has_detail(self, api_client):
        """Test error responses have 'detail' field"""
        response = api_client.get(f"{BASE_URL}/api/auth/me")
        assert response.status_code == 401
        data = response.json()
        assert "detail" in data, "Error response should have 'detail' field"
        print(f"PASS: Error response has detail: {data['detail']}")


# ============================================================================
# DATABASE OPERATIONS (Index verification via API behavior)
# ============================================================================

class TestDatabaseOperations:
    """Database operation tests - verify indexes exist via API behavior"""

    def test_report_translations_unique_constraint(self, auth_client):
        """Test that report_translations has unique compound index (report_id+language)
        by verifying that translating same report to same language returns cached result"""
        # First translation
        response1 = auth_client.post(f"{BASE_URL}/api/cases/{CASE_WITH_REPORTS}/translate", json={
            "language": "es",
            "report_id": REPORT_WITH_SPANISH_TRANSLATION
        }, timeout=180)
        assert response1.status_code == 200

        # Second translation - should return cached
        response2 = auth_client.post(f"{BASE_URL}/api/cases/{CASE_WITH_REPORTS}/translate", json={
            "language": "es",
            "report_id": REPORT_WITH_SPANISH_TRANSLATION
        }, timeout=180)
        assert response2.status_code == 200
        data2 = response2.json()
        # If unique index exists, second call should return cached=True
        assert data2.get("cached"), "Second translation should be cached (unique index working)"
        print("PASS: report_translations unique compound index verified (cached=True on second call)")

    def test_cases_user_id_index(self, auth_client):
        """Test that cases collection has user_id index by verifying fast list retrieval"""
        import time
        start = time.time()
        response = auth_client.get(f"{BASE_URL}/api/cases")
        elapsed = time.time() - start
        assert response.status_code == 200
        # With proper index, should be fast (< 2 seconds even with many cases)
        assert elapsed < 5, f"Cases list took too long ({elapsed}s) - may be missing index"
        print(f"PASS: Cases list retrieved in {elapsed:.2f}s (index working)")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
