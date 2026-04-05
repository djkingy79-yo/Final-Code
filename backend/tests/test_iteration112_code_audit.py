"""
Iteration 112 - Code Audit Tests
Tests for fixes from comprehensive code audit:
1. Health check endpoint
2. Login authentication
3. Case endpoints (documents, timeline, grounds, reports)
4. NEW: Chat messages endpoints (GET/POST /messages)
5. Report export endpoints (PDF, DOCX)
"""
import pytest
import requests
import os

BASE_URL = 'http://localhost:8001'

# Test credentials
TEST_EMAIL = "test@example.com"
TEST_PASSWORD = "TestPassword123!"
TEST_CASE_ID = "case_e7a5b5faf51e"
TEST_REPORT_ID = "rpt_66f34314b465"


class TestHealthCheck:
    """Health check endpoint tests"""
    
    def test_health_endpoint_returns_healthy(self):
        """Test /api/health returns status: healthy"""
        response = requests.get(f"{BASE_URL}/api/health")
        assert response.status_code == 200, f"Health check failed: {response.status_code}"
        data = response.json()
        assert data.get("status") == "healthy", f"Expected status 'healthy', got: {data}"
        print("✓ Health check passed - status: healthy")


class TestAuthentication:
    """Authentication endpoint tests"""
    
    def test_login_with_valid_credentials(self):
        """Test login with admin credentials"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": TEST_EMAIL,
            "password": TEST_PASSWORD
        })
        assert response.status_code == 200, f"Login failed: {response.status_code} - {response.text}"
        data = response.json()
        assert "session_token" in data or "token" in data or "user" in data, f"No auth token in response: {data}"
        print(f"✓ Login successful for {TEST_EMAIL}")
        return data
    
    def test_login_with_invalid_credentials(self):
        """Test login with wrong password"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": TEST_EMAIL,
            "password": "wrongpassword"
        })
        assert response.status_code in [401, 400], f"Expected 401/400, got: {response.status_code}"
        print("✓ Invalid credentials correctly rejected")


@pytest.fixture(scope="class")
def auth_session():
    """Get authenticated session"""
    session = requests.Session()
    response = session.post(f"{BASE_URL}/api/auth/login", json={
        "email": TEST_EMAIL,
        "password": TEST_PASSWORD
    })
    if response.status_code != 200:
        pytest.skip(f"Authentication failed: {response.status_code}")
    return session


class TestCaseEndpoints:
    """Case-related endpoint tests"""
    
    def test_get_cases_list(self, auth_session):
        """Test GET /api/cases returns list of cases"""
        response = auth_session.get(f"{BASE_URL}/api/cases")
        assert response.status_code == 200, f"Get cases failed: {response.status_code}"
        data = response.json()
        assert isinstance(data, list), f"Expected list, got: {type(data)}"
        print(f"✓ GET /api/cases returned {len(data)} cases")
    
    def test_get_case_documents(self, auth_session):
        """Test GET /api/cases/{caseId}/documents"""
        response = auth_session.get(f"{BASE_URL}/api/cases/{TEST_CASE_ID}/documents")
        assert response.status_code == 200, f"Get documents failed: {response.status_code}"
        data = response.json()
        assert isinstance(data, list), f"Expected list, got: {type(data)}"
        print(f"✓ GET /api/cases/{TEST_CASE_ID}/documents returned {len(data)} documents")
    
    def test_get_case_timeline(self, auth_session):
        """Test GET /api/cases/{caseId}/timeline"""
        response = auth_session.get(f"{BASE_URL}/api/cases/{TEST_CASE_ID}/timeline")
        assert response.status_code == 200, f"Get timeline failed: {response.status_code}"
        data = response.json()
        assert isinstance(data, list), f"Expected list, got: {type(data)}"
        print(f"✓ GET /api/cases/{TEST_CASE_ID}/timeline returned {len(data)} events")
    
    def test_get_case_grounds(self, auth_session):
        """Test GET /api/cases/{caseId}/grounds"""
        response = auth_session.get(f"{BASE_URL}/api/cases/{TEST_CASE_ID}/grounds")
        assert response.status_code == 200, f"Get grounds failed: {response.status_code}"
        data = response.json()
        # Grounds endpoint returns dict with 'grounds' key containing the list
        if isinstance(data, dict):
            grounds_list = data.get("grounds", [])
            assert isinstance(grounds_list, list), f"Expected grounds list, got: {type(grounds_list)}"
            print(f"✓ GET /api/cases/{TEST_CASE_ID}/grounds returned {len(grounds_list)} grounds")
        else:
            assert isinstance(data, list), f"Expected list or dict, got: {type(data)}"
            print(f"✓ GET /api/cases/{TEST_CASE_ID}/grounds returned {len(data)} grounds")
    
    def test_get_case_reports(self, auth_session):
        """Test GET /api/cases/{caseId}/reports"""
        response = auth_session.get(f"{BASE_URL}/api/cases/{TEST_CASE_ID}/reports")
        assert response.status_code == 200, f"Get reports failed: {response.status_code}"
        data = response.json()
        assert isinstance(data, list), f"Expected list, got: {type(data)}"
        print(f"✓ GET /api/cases/{TEST_CASE_ID}/reports returned {len(data)} reports")


class TestChatMessagesEndpoints:
    """NEW: Chat messages endpoint tests"""
    
    def test_get_case_messages(self, auth_session):
        """Test GET /api/cases/{caseId}/messages returns messages array"""
        response = auth_session.get(f"{BASE_URL}/api/cases/{TEST_CASE_ID}/messages")
        assert response.status_code == 200, f"Get messages failed: {response.status_code} - {response.text}"
        data = response.json()
        assert isinstance(data, list), f"Expected list, got: {type(data)}"
        print(f"✓ GET /api/cases/{TEST_CASE_ID}/messages returned {len(data)} messages")
    
    def test_post_case_message(self, auth_session):
        """Test POST /api/cases/{caseId}/messages creates a message"""
        test_content = "Test message from iteration 112 testing"
        response = auth_session.post(
            f"{BASE_URL}/api/cases/{TEST_CASE_ID}/messages",
            json={"content": test_content}
        )
        assert response.status_code == 200, f"Post message failed: {response.status_code} - {response.text}"
        data = response.json()
        assert "message_id" in data, f"No message_id in response: {data}"
        assert data.get("content") == test_content, f"Content mismatch: {data}"
        assert data.get("case_id") == TEST_CASE_ID, f"Case ID mismatch: {data}"
        print(f"✓ POST /api/cases/{TEST_CASE_ID}/messages created message: {data.get('message_id')}")
    
    def test_post_message_empty_content_rejected(self, auth_session):
        """Test POST with empty content is rejected"""
        response = auth_session.post(
            f"{BASE_URL}/api/cases/{TEST_CASE_ID}/messages",
            json={"content": ""}
        )
        assert response.status_code == 400, f"Expected 400, got: {response.status_code}"
        print("✓ Empty message content correctly rejected with 400")
    
    def test_get_messages_after_post(self, auth_session):
        """Test that posted message appears in GET"""
        # Post a unique message
        unique_content = f"Unique test message {os.urandom(4).hex()}"
        post_response = auth_session.post(
            f"{BASE_URL}/api/cases/{TEST_CASE_ID}/messages",
            json={"content": unique_content}
        )
        assert post_response.status_code == 200
        
        # Verify it appears in GET
        get_response = auth_session.get(f"{BASE_URL}/api/cases/{TEST_CASE_ID}/messages")
        assert get_response.status_code == 200
        messages = get_response.json()
        found = any(m.get("content") == unique_content for m in messages)
        assert found, "Posted message not found in GET response"
        print("✓ Posted message verified in GET /messages response")


class TestReportExports:
    """Report export endpoint tests"""
    
    def test_export_pdf(self, auth_session):
        """Test GET /api/cases/{caseId}/reports/{reportId}/export-pdf"""
        response = auth_session.get(
            f"{BASE_URL}/api/cases/{TEST_CASE_ID}/reports/{TEST_REPORT_ID}/export-pdf"
        )
        assert response.status_code == 200, f"PDF export failed: {response.status_code}"
        content_type = response.headers.get("content-type", "")
        assert "pdf" in content_type.lower() or len(response.content) > 0, "Invalid PDF response"
        print(f"✓ PDF export returned {len(response.content)} bytes")
    
    def test_export_docx(self, auth_session):
        """Test GET /api/cases/{caseId}/reports/{reportId}/export-docx"""
        response = auth_session.get(
            f"{BASE_URL}/api/cases/{TEST_CASE_ID}/reports/{TEST_REPORT_ID}/export-docx"
        )
        assert response.status_code == 200, f"DOCX export failed: {response.status_code}"
        content_type = response.headers.get("content-type", "")
        assert "word" in content_type.lower() or "docx" in content_type.lower() or len(response.content) > 0
        print(f"✓ DOCX export returned {len(response.content)} bytes")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
