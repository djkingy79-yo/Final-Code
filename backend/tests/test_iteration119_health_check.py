"""
Iteration 119 - Full Production Health Check
Tests all CRUD operations, exports, and critical endpoints
"""
import pytest
import requests
import os
import time

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', 'http://localhost:8001').rstrip('/')
CASE_ID = "case_a97ea91f0692"
TEST_EMAIL = "test@example.com"
TEST_PASSWORD = "TestPassword123!"


class TestHealthCheck:
    """Basic health and connectivity tests"""
    
    def test_health_endpoint(self):
        """Test /api/health returns healthy status"""
        response = requests.get(f"{BASE_URL}/api/health")
        assert response.status_code == 200
        data = response.json()
        assert data.get("status") == "healthy"
        assert data.get("database") == "connected"
        print(f"✓ Health check passed: {data}")


class TestAuthentication:
    """Authentication flow tests"""
    
    def test_login_success(self):
        """Test login with valid credentials"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": TEST_EMAIL,
            "password": TEST_PASSWORD
        })
        assert response.status_code == 200
        data = response.json()
        assert "session_token" in data
        # Response may have user nested or flat
        email = data.get("user", {}).get("email") or data.get("email")
        assert email == TEST_EMAIL
        print("✓ Login successful, session_token received")
        return data["session_token"]
    
    def test_login_invalid_credentials(self):
        """Test login with invalid credentials"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": "wrong@example.com",
            "password": "wrongpassword"
        })
        assert response.status_code == 401
        print("✓ Invalid login correctly rejected")


@pytest.fixture(scope="class")
def auth_token():
    """Get authentication token for tests"""
    response = requests.post(f"{BASE_URL}/api/auth/login", json={
        "email": TEST_EMAIL,
        "password": TEST_PASSWORD
    })
    if response.status_code == 200:
        return response.json().get("session_token")
    pytest.skip("Authentication failed")


@pytest.fixture(scope="class")
def auth_headers(auth_token):
    """Get headers with auth token"""
    return {"Authorization": f"Bearer {auth_token}"}


class TestCasesAPI:
    """Cases CRUD tests"""
    
    def test_get_cases_list(self, auth_headers):
        """Test getting list of cases"""
        response = requests.get(f"{BASE_URL}/api/cases", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 1
        print(f"✓ Cases list returned {len(data)} cases")
    
    def test_get_case_detail(self, auth_headers):
        """Test getting specific case details"""
        response = requests.get(f"{BASE_URL}/api/cases/{CASE_ID}", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data.get("case_id") == CASE_ID
        print(f"✓ Case detail retrieved: {data.get('title', 'N/A')}")


class TestDocumentsAPI:
    """Documents router tests"""
    
    def test_get_documents(self, auth_headers):
        """Test getting documents for a case"""
        response = requests.get(f"{BASE_URL}/api/cases/{CASE_ID}/documents", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        print(f"✓ Documents endpoint returned {len(data)} documents")


class TestTimelineAPI:
    """Timeline router tests - CRUD operations"""
    
    def test_get_timeline(self, auth_headers):
        """Test getting timeline events"""
        response = requests.get(f"{BASE_URL}/api/cases/{CASE_ID}/timeline", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        print(f"✓ Timeline endpoint returned {len(data)} events")
    
    def test_create_and_delete_timeline_event(self, auth_headers):
        """Test creating and deleting a timeline event"""
        # Create
        create_payload = {
            "title": "TEST_Event_119",
            "event_date": "2024-01-15",
            "event_type": "hearing",
            "description": "Test event for iteration 119"
        }
        create_response = requests.post(
            f"{BASE_URL}/api/cases/{CASE_ID}/timeline",
            headers=auth_headers,
            json=create_payload
        )
        assert create_response.status_code in [200, 201]
        created = create_response.json()
        event_id = created.get("event_id")
        assert event_id is not None
        print(f"✓ Timeline event created: {event_id}")
        
        # Verify it exists
        get_response = requests.get(f"{BASE_URL}/api/cases/{CASE_ID}/timeline", headers=auth_headers)
        events = get_response.json()
        event_ids = [e.get("event_id") for e in events]
        assert event_id in event_ids
        print("✓ Timeline event verified in list")
        
        # Delete
        delete_response = requests.delete(
            f"{BASE_URL}/api/cases/{CASE_ID}/timeline/{event_id}",
            headers=auth_headers
        )
        assert delete_response.status_code in [200, 204]
        print(f"✓ Timeline event deleted: {event_id}")
        
        # Verify deletion
        get_response2 = requests.get(f"{BASE_URL}/api/cases/{CASE_ID}/timeline", headers=auth_headers)
        events2 = get_response2.json()
        event_ids2 = [e.get("event_id") for e in events2]
        assert event_id not in event_ids2
        print("✓ Timeline event deletion verified")


class TestNotesAPI:
    """Notes router tests - CRUD operations"""
    
    def test_get_notes(self, auth_headers):
        """Test getting notes for a case"""
        response = requests.get(f"{BASE_URL}/api/cases/{CASE_ID}/notes", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        print(f"✓ Notes endpoint returned {len(data)} notes")
    
    def test_create_and_delete_note(self, auth_headers):
        """Test creating and deleting a note"""
        # Create
        create_payload = {
            "title": "TEST_Note_119",
            "content": "Test note content for iteration 119",
            "category": "general"
        }
        create_response = requests.post(
            f"{BASE_URL}/api/cases/{CASE_ID}/notes",
            headers=auth_headers,
            json=create_payload
        )
        assert create_response.status_code in [200, 201]
        created = create_response.json()
        note_id = created.get("note_id")
        assert note_id is not None
        print(f"✓ Note created: {note_id}")
        
        # Verify it exists
        get_response = requests.get(f"{BASE_URL}/api/cases/{CASE_ID}/notes", headers=auth_headers)
        notes = get_response.json()
        note_ids = [n.get("note_id") for n in notes]
        assert note_id in note_ids
        print("✓ Note verified in list")
        
        # Delete
        delete_response = requests.delete(
            f"{BASE_URL}/api/cases/{CASE_ID}/notes/{note_id}",
            headers=auth_headers
        )
        assert delete_response.status_code in [200, 204]
        print(f"✓ Note deleted: {note_id}")
        
        # Verify deletion
        get_response2 = requests.get(f"{BASE_URL}/api/cases/{CASE_ID}/notes", headers=auth_headers)
        notes2 = get_response2.json()
        note_ids2 = [n.get("note_id") for n in notes2]
        assert note_id not in note_ids2
        print("✓ Note deletion verified")


class TestDeadlinesAPI:
    """Deadlines router tests - CRUD operations"""
    
    def test_get_deadlines(self, auth_headers):
        """Test getting deadlines for a case"""
        response = requests.get(f"{BASE_URL}/api/cases/{CASE_ID}/deadlines", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        print(f"✓ Deadlines endpoint returned {len(data)} deadlines")
    
    def test_get_checklist(self, auth_headers):
        """Test getting checklist for a case"""
        response = requests.get(f"{BASE_URL}/api/cases/{CASE_ID}/checklist", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        print(f"✓ Checklist endpoint returned {len(data)} items")
    
    def test_get_strength(self, auth_headers):
        """Test getting case strength assessment"""
        response = requests.get(f"{BASE_URL}/api/cases/{CASE_ID}/strength", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert "overall_strength" in data or "strength" in data or isinstance(data, dict)
        print("✓ Strength endpoint returned assessment")
    
    def test_create_and_delete_deadline(self, auth_headers):
        """Test creating and deleting a deadline"""
        # Create
        create_payload = {
            "title": "TEST_Deadline_119",
            "due_date": "2024-06-15",
            "description": "Test deadline for iteration 119",
            "priority": "high"
        }
        create_response = requests.post(
            f"{BASE_URL}/api/cases/{CASE_ID}/deadlines",
            headers=auth_headers,
            json=create_payload
        )
        assert create_response.status_code in [200, 201]
        created = create_response.json()
        deadline_id = created.get("deadline_id")
        assert deadline_id is not None
        print(f"✓ Deadline created: {deadline_id}")
        
        # Verify it exists
        get_response = requests.get(f"{BASE_URL}/api/cases/{CASE_ID}/deadlines", headers=auth_headers)
        deadlines = get_response.json()
        deadline_ids = [d.get("deadline_id") for d in deadlines]
        assert deadline_id in deadline_ids
        print("✓ Deadline verified in list")
        
        # Delete
        delete_response = requests.delete(
            f"{BASE_URL}/api/cases/{CASE_ID}/deadlines/{deadline_id}",
            headers=auth_headers
        )
        assert delete_response.status_code in [200, 204]
        print(f"✓ Deadline deleted: {deadline_id}")
        
        # Verify deletion
        get_response2 = requests.get(f"{BASE_URL}/api/cases/{CASE_ID}/deadlines", headers=auth_headers)
        deadlines2 = get_response2.json()
        deadline_ids2 = [d.get("deadline_id") for d in deadlines2]
        assert deadline_id not in deadline_ids2
        print("✓ Deadline deletion verified")


class TestGroundsAPI:
    """Grounds router tests"""
    
    def test_get_grounds(self, auth_headers):
        """Test getting grounds for a case"""
        response = requests.get(f"{BASE_URL}/api/cases/{CASE_ID}/grounds", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        # Response may be list or dict with grounds key
        if isinstance(data, dict):
            grounds = data.get("grounds", [])
            assert isinstance(grounds, list)
            print(f"✓ Grounds endpoint returned {len(grounds)} grounds")
        else:
            assert isinstance(data, list)
            print(f"✓ Grounds endpoint returned {len(data)} grounds")


class TestReportsAPI:
    """Reports router tests"""
    
    def test_get_reports(self, auth_headers):
        """Test getting reports for a case"""
        response = requests.get(f"{BASE_URL}/api/cases/{CASE_ID}/reports", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        print(f"✓ Reports endpoint returned {len(data)} reports")
    
    def test_get_barrister_view(self, auth_headers):
        """Test getting barrister view"""
        response = requests.get(f"{BASE_URL}/api/cases/{CASE_ID}/reports/barrister-view", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert "content" in data or "sections" in data or isinstance(data, dict)
        print("✓ Barrister view endpoint returned data")


class TestExportsAPI:
    """Export endpoints tests - PDF and DOCX"""
    
    def test_report_export_pdf(self, auth_headers):
        """Test PDF export for a report"""
        # First get a report ID
        reports_response = requests.get(f"{BASE_URL}/api/cases/{CASE_ID}/reports", headers=auth_headers)
        reports = reports_response.json()
        if not reports:
            pytest.skip("No reports available for export test")
        
        report_id = reports[0].get("report_id")
        response = requests.get(
            f"{BASE_URL}/api/cases/{CASE_ID}/reports/{report_id}/export-pdf",
            headers=auth_headers
        )
        assert response.status_code == 200
        assert "application/pdf" in response.headers.get("Content-Type", "")
        assert int(response.headers.get("Content-Length", 0)) > 0
        print(f"✓ Report PDF export successful, size: {len(response.content)} bytes")
    
    def test_report_export_docx(self, auth_headers):
        """Test DOCX export for a report"""
        # First get a report ID
        reports_response = requests.get(f"{BASE_URL}/api/cases/{CASE_ID}/reports", headers=auth_headers)
        reports = reports_response.json()
        if not reports:
            pytest.skip("No reports available for export test")
        
        report_id = reports[0].get("report_id")
        response = requests.get(
            f"{BASE_URL}/api/cases/{CASE_ID}/reports/{report_id}/export-docx",
            headers=auth_headers
        )
        assert response.status_code == 200
        content_type = response.headers.get("Content-Type", "")
        assert "application/vnd.openxmlformats" in content_type or "application/octet-stream" in content_type
        assert int(response.headers.get("Content-Length", 0)) > 0
        print(f"✓ Report DOCX export successful, size: {len(response.content)} bytes")
    
    def test_barrister_view_export_pdf(self, auth_headers):
        """Test PDF export for barrister view"""
        response = requests.get(
            f"{BASE_URL}/api/cases/{CASE_ID}/reports/barrister-view/export-pdf",
            headers=auth_headers
        )
        assert response.status_code == 200
        assert "application/pdf" in response.headers.get("Content-Type", "")
        assert int(response.headers.get("Content-Length", 0)) > 0
        print(f"✓ Barrister view PDF export successful, size: {len(response.content)} bytes")
    
    def test_barrister_view_export_docx(self, auth_headers):
        """Test DOCX export for barrister view"""
        response = requests.get(
            f"{BASE_URL}/api/cases/{CASE_ID}/reports/barrister-view/export-docx",
            headers=auth_headers
        )
        assert response.status_code == 200
        content_type = response.headers.get("Content-Type", "")
        assert "application/vnd.openxmlformats" in content_type or "application/octet-stream" in content_type
        assert int(response.headers.get("Content-Length", 0)) > 0
        print(f"✓ Barrister view DOCX export successful, size: {len(response.content)} bytes")


class TestPaymentsAPI:
    """Payments router tests"""
    
    def test_get_prices(self, auth_headers):
        """Test getting payment prices"""
        response = requests.get(f"{BASE_URL}/api/payments/prices", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, dict) or isinstance(data, list)
        print("✓ Prices endpoint returned data")
    
    def test_get_case_payments(self, auth_headers):
        """Test getting payments for a case"""
        response = requests.get(f"{BASE_URL}/api/cases/{CASE_ID}/payments", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        # Response may be list or dict with payments key
        if isinstance(data, dict):
            payments = data.get("payments", [])
            assert isinstance(payments, list)
            print(f"✓ Case payments endpoint returned {len(payments)} payments")
        else:
            assert isinstance(data, list)
            print(f"✓ Case payments endpoint returned {len(data)} payments")


class TestResourcesAPI:
    """Resources router tests"""
    
    def test_get_resources_directory(self, auth_headers):
        """Test getting resources directory"""
        response = requests.get(f"{BASE_URL}/api/resources/directory", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list) or isinstance(data, dict)
        print("✓ Resources directory endpoint returned data")
    
    def test_get_templates(self, auth_headers):
        """Test getting templates"""
        response = requests.get(f"{BASE_URL}/api/templates", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        print(f"✓ Templates endpoint returned {len(data)} templates")


class TestCollaborationAPI:
    """Collaboration router tests"""
    
    def test_get_messages(self, auth_headers):
        """Test getting messages for a case"""
        response = requests.get(f"{BASE_URL}/api/cases/{CASE_ID}/messages", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        print(f"✓ Messages endpoint returned {len(data)} messages")


class TestStatisticsAPI:
    """Statistics router tests"""
    
    def test_get_public_statistics(self, auth_headers):
        """Test getting public statistics"""
        response = requests.get(f"{BASE_URL}/api/statistics/public", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, dict)
        print("✓ Public statistics endpoint returned data")


class TestAnalyticsAPI:
    """Analytics router tests"""
    
    def test_get_visitor_count(self, auth_headers):
        """Test getting visitor count"""
        response = requests.get(f"{BASE_URL}/api/analytics/visitor-count", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert "count" in data or isinstance(data, dict)
        print("✓ Visitor count endpoint returned data")


class TestStatesAPI:
    """States and offence framework tests"""
    
    def test_get_states(self, auth_headers):
        """Test getting Australian states"""
        response = requests.get(f"{BASE_URL}/api/states", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list) or isinstance(data, dict)
        print("✓ States endpoint returned data")
    
    def test_get_offence_framework(self, auth_headers):
        """Test getting offence framework"""
        response = requests.get(f"{BASE_URL}/api/offence-framework", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, dict) or isinstance(data, list)
        print("✓ Offence framework endpoint returned data")
    
    def test_get_offence_categories(self, auth_headers):
        """Test getting offence categories"""
        response = requests.get(f"{BASE_URL}/api/offence-categories", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, dict) or isinstance(data, list)
        print("✓ Offence categories endpoint returned data")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
