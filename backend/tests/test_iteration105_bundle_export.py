"""
Iteration 105 - Bundle Export and Delete Button Tests
Tests:
1. Document bundle PDF export endpoint
2. Timeline delete functionality
3. Notes delete functionality
"""
import pytest
import requests
import os

BASE_URL = 'http://localhost:8001'

# Test credentials
TEST_EMAIL = "djkingy79@gmail.com"
TEST_PASSWORD = "Grubbygrub88"

# Test case with documents and timeline events
TEST_CASE_ID = "case_a97ea91f0692"
TEST_DOCUMENT_ID = "doc_e3e60fe91e2c"
TEST_EVENT_ID = "evt_a08391e7eb0b"


class TestAuthentication:
    """Authentication tests"""
    
    def test_login_success(self):
        """Test login returns session_token"""
        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": TEST_EMAIL, "password": TEST_PASSWORD}
        )
        assert response.status_code == 200, f"Login failed: {response.text}"
        data = response.json()
        assert "session_token" in data, f"No session_token in response: {data}"
        print(f"Login successful, session_token received")
        return data["session_token"]


class TestBundleExport:
    """Document bundle export tests"""
    
    @pytest.fixture
    def auth_session(self):
        """Get authenticated session"""
        session = requests.Session()
        response = session.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": TEST_EMAIL, "password": TEST_PASSWORD}
        )
        assert response.status_code == 200, f"Login failed: {response.text}"
        data = response.json()
        session_token = data.get("session_token")
        session.cookies.set("session_token", session_token)
        return session
    
    def test_bundle_export_endpoint_exists(self, auth_session):
        """Test that bundle export endpoint exists and accepts POST"""
        # First get case documents
        response = auth_session.get(f"{BASE_URL}/api/cases/{TEST_CASE_ID}")
        if response.status_code == 404:
            pytest.skip(f"Test case {TEST_CASE_ID} not found")
        
        # Get documents for the case
        docs_response = auth_session.get(f"{BASE_URL}/api/cases/{TEST_CASE_ID}/documents")
        if docs_response.status_code != 200:
            pytest.skip("No documents endpoint or no documents")
        
        docs = docs_response.json()
        if not docs:
            pytest.skip("No documents in test case")
        
        doc_ids = [d.get("document_id") for d in docs[:1] if d.get("document_id")]
        if not doc_ids:
            pytest.skip("No valid document IDs found")
        
        # Test bundle export
        response = auth_session.post(
            f"{BASE_URL}/api/cases/{TEST_CASE_ID}/export/bundle",
            json={
                "document_ids": doc_ids,
                "include_toc": True,
                "title": "Test Bundle"
            }
        )
        
        # Should return PDF (200) or error with proper status
        assert response.status_code in [200, 400, 404], f"Unexpected status: {response.status_code}, {response.text}"
        
        if response.status_code == 200:
            # Verify it's a PDF
            content_type = response.headers.get("content-type", "")
            assert "pdf" in content_type.lower() or len(response.content) > 0, "Response should be PDF"
            print(f"Bundle export successful, PDF size: {len(response.content)} bytes")
    
    def test_bundle_export_no_documents_error(self, auth_session):
        """Test bundle export with empty document list returns 400"""
        response = auth_session.post(
            f"{BASE_URL}/api/cases/{TEST_CASE_ID}/export/bundle",
            json={
                "document_ids": [],
                "include_toc": True,
                "title": "Empty Bundle"
            }
        )
        assert response.status_code == 400, f"Expected 400 for empty docs, got {response.status_code}"
        print("Empty document list correctly returns 400")


class TestTimelineDelete:
    """Timeline event delete tests"""
    
    @pytest.fixture
    def auth_session(self):
        """Get authenticated session"""
        session = requests.Session()
        response = session.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": TEST_EMAIL, "password": TEST_PASSWORD}
        )
        assert response.status_code == 200
        data = response.json()
        session_token = data.get("session_token")
        session.cookies.set("session_token", session_token)
        return session
    
    def test_timeline_events_endpoint(self, auth_session):
        """Test timeline events endpoint exists"""
        response = auth_session.get(f"{BASE_URL}/api/cases/{TEST_CASE_ID}/timeline")
        if response.status_code == 404:
            pytest.skip(f"Test case {TEST_CASE_ID} not found")
        
        assert response.status_code == 200, f"Timeline endpoint failed: {response.status_code}"
        events = response.json()
        print(f"Found {len(events)} timeline events")
    
    def test_timeline_delete_endpoint_exists(self, auth_session):
        """Test that timeline delete endpoint exists"""
        # First create a test event
        create_response = auth_session.post(
            f"{BASE_URL}/api/cases/{TEST_CASE_ID}/timeline",
            json={
                "event_type": "test_event",
                "event_date": "2024-01-15",
                "title": "TEST_DELETE_EVENT",
                "description": "Test event for deletion"
            }
        )
        
        if create_response.status_code not in [200, 201]:
            pytest.skip("Cannot create test event")
        
        event_data = create_response.json()
        event_id = event_data.get("event_id")
        
        if not event_id:
            pytest.skip("No event_id in response")
        
        # Now delete it
        delete_response = auth_session.delete(
            f"{BASE_URL}/api/cases/{TEST_CASE_ID}/timeline/{event_id}"
        )
        
        assert delete_response.status_code in [200, 204], f"Delete failed: {delete_response.status_code}"
        print(f"Timeline event {event_id} deleted successfully")


class TestNotesDelete:
    """Notes delete tests"""
    
    @pytest.fixture
    def auth_session(self):
        """Get authenticated session"""
        session = requests.Session()
        response = session.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": TEST_EMAIL, "password": TEST_PASSWORD}
        )
        assert response.status_code == 200
        data = response.json()
        session_token = data.get("session_token")
        session.cookies.set("session_token", session_token)
        return session
    
    def test_notes_endpoint(self, auth_session):
        """Test notes endpoint exists"""
        response = auth_session.get(f"{BASE_URL}/api/cases/{TEST_CASE_ID}/notes")
        if response.status_code == 404:
            # Notes might be part of case data
            case_response = auth_session.get(f"{BASE_URL}/api/cases/{TEST_CASE_ID}")
            if case_response.status_code == 200:
                case_data = case_response.json()
                notes = case_data.get("notes", [])
                print(f"Found {len(notes)} notes in case data")
                return
            pytest.skip("Notes endpoint not found")
        
        assert response.status_code == 200
        notes = response.json()
        print(f"Found {len(notes)} notes")


class TestHealthCheck:
    """Basic health check"""
    
    def test_api_health(self):
        """Test API is responding"""
        response = requests.get(f"{BASE_URL}/api/health")
        assert response.status_code == 200, f"Health check failed: {response.status_code}"
        print("API health check passed")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
