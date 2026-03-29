"""
Iteration 113 - Export Features and Responsive CSS Testing
Tests: PDF/Word exports, chat endpoint, health check
"""
import pytest
import requests
import os

BASE_URL = 'http://localhost:8001'

class TestHealthAndAuth:
    """Health check and authentication tests"""
    
    def test_health_check(self):
        """Backend health check returns healthy"""
        response = requests.get(f"{BASE_URL}/api/health")
        assert response.status_code == 200
        data = response.json()
        assert data.get("status") == "healthy"
        print(f"PASS: Health check - status: {data.get('status')}")
    
    def test_login_success(self):
        """Login with valid credentials"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": "djkingy79@gmail.com",
            "password": "Grubbygrub88"
        })
        assert response.status_code == 200
        data = response.json()
        assert "session_token" in data
        assert "user_id" in data
        print(f"PASS: Login successful - user_id: {data.get('user_id')}")
        return data.get("session_token")


class TestChatEndpoint:
    """Chat/Messages endpoint tests"""
    
    @pytest.fixture
    def auth_token(self):
        """Get authentication token"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": "djkingy79@gmail.com",
            "password": "Grubbygrub88"
        })
        if response.status_code == 200:
            return response.json().get("session_token")
        pytest.skip("Authentication failed")
    
    def test_get_messages_returns_200(self, auth_token):
        """GET /api/cases/{caseId}/messages returns 200"""
        case_id = "case_e7a5b5faf51e"
        response = requests.get(
            f"{BASE_URL}/api/cases/{case_id}/messages",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        print(f"PASS: GET /messages returns 200 with {len(data)} messages")


class TestExportFeatures:
    """PDF and Word export tests"""
    
    @pytest.fixture
    def auth_token(self):
        """Get authentication token"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": "djkingy79@gmail.com",
            "password": "Grubbygrub88"
        })
        if response.status_code == 200:
            return response.json().get("session_token")
        pytest.skip("Authentication failed")
    
    def test_word_export_success(self, auth_token):
        """Word export (.docx) downloads successfully"""
        case_id = "case_e7a5b5faf51e"
        report_id = "rpt_66f34314b465"
        response = requests.get(
            f"{BASE_URL}/api/cases/{case_id}/reports/{report_id}/export-docx",
            headers={"Authorization": f"Bearer {auth_token}"},
            timeout=60
        )
        assert response.status_code == 200
        assert len(response.content) > 0
        # Check content type
        content_type = response.headers.get("content-type", "")
        assert "application/vnd.openxmlformats-officedocument.wordprocessingml.document" in content_type or len(response.content) > 1000
        print(f"PASS: Word export - HTTP 200, file size: {len(response.content)} bytes")
    
    def test_pdf_export_success(self, auth_token):
        """PDF export downloads successfully"""
        case_id = "case_e7a5b5faf51e"
        report_id = "rpt_66f34314b465"
        response = requests.get(
            f"{BASE_URL}/api/cases/{case_id}/reports/{report_id}/export-pdf",
            headers={"Authorization": f"Bearer {auth_token}"},
            timeout=60
        )
        assert response.status_code == 200
        assert len(response.content) > 0
        print(f"PASS: PDF export - HTTP 200, file size: {len(response.content)} bytes")


class TestReportView:
    """Report view endpoint tests"""
    
    @pytest.fixture
    def auth_token(self):
        """Get authentication token"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": "djkingy79@gmail.com",
            "password": "Grubbygrub88"
        })
        if response.status_code == 200:
            return response.json().get("session_token")
        pytest.skip("Authentication failed")
    
    def test_get_report_success(self, auth_token):
        """GET report returns 200 with content"""
        case_id = "case_e7a5b5faf51e"
        report_id = "rpt_66f34314b465"
        response = requests.get(
            f"{BASE_URL}/api/cases/{case_id}/reports/{report_id}",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "report_id" in data or "report_type" in data
        print(f"PASS: GET report - HTTP 200, report_type: {data.get('report_type')}")
    
    def test_get_case_success(self, auth_token):
        """GET case returns 200 with case data"""
        case_id = "case_e7a5b5faf51e"
        response = requests.get(
            f"{BASE_URL}/api/cases/{case_id}",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "case_id" in data or "title" in data
        print(f"PASS: GET case - HTTP 200, title: {data.get('title')}")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
