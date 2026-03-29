"""
Iteration 117 - Bug Fix Verification Tests
Tests for:
1. Backend auth endpoints still work after auth_old.py removal
2. All core API endpoints functional
3. WebSocket cleanup (frontend test - verified via Playwright)
4. ESLint warnings fixed (frontend compilation - verified via logs)
"""

import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

class TestHealthAndAuth:
    """Test health and auth endpoints after auth_old.py removal"""
    
    def test_health_endpoint(self):
        """Health endpoint should return healthy status"""
        response = requests.get(f"{BASE_URL}/api/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "database" in data
        print("PASS: Health endpoint working")
    
    def test_login_endpoint(self):
        """Login endpoint should work with valid credentials"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": "djkingy79@gmail.com",
            "password": "Grubbygrub88"
        })
        assert response.status_code == 200
        data = response.json()
        assert "session_token" in data
        assert "email" in data  # User data is at root level
        assert data["email"] == "djkingy79@gmail.com"
        print(f"PASS: Login endpoint working, got token: {data['session_token'][:20]}...")
        return data["session_token"]
    
    def test_auth_me_endpoint(self):
        """Auth/me endpoint should return user info with valid token"""
        # First login to get token
        login_response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": "djkingy79@gmail.com",
            "password": "Grubbygrub88"
        })
        token = login_response.json()["session_token"]
        
        # Test /auth/me with Bearer token
        response = requests.get(f"{BASE_URL}/api/auth/me", headers={
            "Authorization": f"Bearer {token}"
        })
        assert response.status_code == 200
        data = response.json()
        assert "email" in data
        assert data["email"] == "djkingy79@gmail.com"
        print("PASS: Auth/me endpoint working with Bearer token")
    
    def test_logout_endpoint(self):
        """Logout endpoint should work"""
        # First login to get token
        login_response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": "djkingy79@gmail.com",
            "password": "Grubbygrub88"
        })
        token = login_response.json()["session_token"]
        
        # Test logout
        response = requests.post(f"{BASE_URL}/api/auth/logout", headers={
            "Authorization": f"Bearer {token}"
        })
        assert response.status_code == 200
        print("PASS: Logout endpoint working")


class TestCoreAPIEndpoints:
    """Test core API endpoints are functional"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Get auth token for tests"""
        login_response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": "djkingy79@gmail.com",
            "password": "Grubbygrub88"
        })
        self.token = login_response.json()["session_token"]
        self.headers = {"Authorization": f"Bearer {self.token}"}
    
    def test_cases_list(self):
        """Cases list endpoint should work"""
        response = requests.get(f"{BASE_URL}/api/cases", headers=self.headers)
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        print(f"PASS: Cases list endpoint working, found {len(data)} cases")
    
    def test_offence_categories(self):
        """Offence categories endpoint should work"""
        response = requests.get(f"{BASE_URL}/api/offence-categories")
        assert response.status_code == 200
        data = response.json()
        assert "categories" in data
        print(f"PASS: Offence categories endpoint working, found {len(data['categories'])} categories")
    
    def test_states_endpoint(self):
        """States endpoint should work"""
        response = requests.get(f"{BASE_URL}/api/states")
        assert response.status_code == 200
        data = response.json()
        assert "states" in data
        print(f"PASS: States endpoint working, found {len(data['states'])} states")
    
    def test_notifications_endpoint(self):
        """Notifications endpoint should work"""
        response = requests.get(f"{BASE_URL}/api/notifications", headers=self.headers)
        assert response.status_code == 200
        data = response.json()
        assert "notifications" in data
        print("PASS: Notifications endpoint working")
    
    def test_shared_cases_endpoint(self):
        """Shared cases endpoint should work"""
        response = requests.get(f"{BASE_URL}/api/shared-cases", headers=self.headers)
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        print(f"PASS: Shared cases endpoint working, found {len(data)} shared cases")


class TestCaseDetailEndpoints:
    """Test case detail endpoints"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Get auth token and first case ID"""
        login_response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": "djkingy79@gmail.com",
            "password": "Grubbygrub88"
        })
        self.token = login_response.json()["session_token"]
        self.headers = {"Authorization": f"Bearer {self.token}"}
        
        # Get first case
        cases_response = requests.get(f"{BASE_URL}/api/cases", headers=self.headers)
        cases = cases_response.json()
        if cases:
            self.case_id = cases[0]["case_id"]
        else:
            self.case_id = None
    
    def test_case_detail(self):
        """Case detail endpoint should work"""
        if not self.case_id:
            pytest.skip("No cases available")
        
        response = requests.get(f"{BASE_URL}/api/cases/{self.case_id}", headers=self.headers)
        assert response.status_code == 200
        data = response.json()
        assert "case_id" in data
        print(f"PASS: Case detail endpoint working for case {self.case_id}")
    
    def test_case_documents(self):
        """Case documents endpoint should work"""
        if not self.case_id:
            pytest.skip("No cases available")
        
        response = requests.get(f"{BASE_URL}/api/cases/{self.case_id}/documents", headers=self.headers)
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        print(f"PASS: Case documents endpoint working, found {len(data)} documents")
    
    def test_case_timeline(self):
        """Case timeline endpoint should work"""
        if not self.case_id:
            pytest.skip("No cases available")
        
        response = requests.get(f"{BASE_URL}/api/cases/{self.case_id}/timeline", headers=self.headers)
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        print(f"PASS: Case timeline endpoint working, found {len(data)} events")
    
    def test_case_grounds(self):
        """Case grounds endpoint should work"""
        if not self.case_id:
            pytest.skip("No cases available")
        
        response = requests.get(f"{BASE_URL}/api/cases/{self.case_id}/grounds", headers=self.headers)
        assert response.status_code == 200
        data = response.json()
        assert "grounds" in data or isinstance(data, list)
        print("PASS: Case grounds endpoint working")
    
    def test_case_notes(self):
        """Case notes endpoint should work"""
        if not self.case_id:
            pytest.skip("No cases available")
        
        response = requests.get(f"{BASE_URL}/api/cases/{self.case_id}/notes", headers=self.headers)
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        print(f"PASS: Case notes endpoint working, found {len(data)} notes")
    
    def test_case_reports(self):
        """Case reports endpoint should work"""
        if not self.case_id:
            pytest.skip("No cases available")
        
        response = requests.get(f"{BASE_URL}/api/cases/{self.case_id}/reports", headers=self.headers)
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        print(f"PASS: Case reports endpoint working, found {len(data)} reports")
    
    def test_case_messages(self):
        """Case messages endpoint should work"""
        if not self.case_id:
            pytest.skip("No cases available")
        
        response = requests.get(f"{BASE_URL}/api/cases/{self.case_id}/messages", headers=self.headers)
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        print(f"PASS: Case messages endpoint working, found {len(data)} messages")
    
    def test_case_activity(self):
        """Case activity endpoint should work"""
        if not self.case_id:
            pytest.skip("No cases available")
        
        response = requests.get(f"{BASE_URL}/api/cases/{self.case_id}/activity", headers=self.headers)
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        print(f"PASS: Case activity endpoint working, found {len(data)} activities")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
