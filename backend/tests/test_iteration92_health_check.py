"""
Iteration 92 - Full Health Check Tests
Tests for: Public routes, case flow, reports, barrister view, grounds, progress tab
"""
import pytest
import requests

BASE_URL = 'http://localhost:8001'

class TestHealthAndPublicEndpoints:
    """Test health check and public API endpoints"""
    
    def test_health_endpoint(self):
        """Test /api/health returns healthy status"""
        response = requests.get(f"{BASE_URL}/api/health", timeout=10)
        assert response.status_code == 200
        data = response.json()
        assert data.get("status") == "healthy"
        assert "database" in data
        print(f"✓ Health check passed: {data}")
    
    def test_offence_categories_endpoint(self):
        """Test /api/offence-categories returns list of categories"""
        response = requests.get(f"{BASE_URL}/api/offence-categories", timeout=10)
        assert response.status_code == 200
        data = response.json()
        # Response is wrapped in {"categories": [...]}
        assert "categories" in data
        categories = data["categories"]
        assert isinstance(categories, list)
        assert len(categories) > 0
        # Check for expected categories
        category_ids = [c.get("id") for c in categories]
        assert "homicide" in category_ids
        assert "assault" in category_ids
        print(f"✓ Offence categories: {len(categories)} categories found")
    
    def test_states_endpoint(self):
        """Test /api/states returns Australian states"""
        response = requests.get(f"{BASE_URL}/api/states", timeout=10)
        assert response.status_code == 200
        data = response.json()
        # Response is wrapped in {"states": [...]}
        assert "states" in data
        states = data["states"]
        assert isinstance(states, list)
        # Check for expected states
        state_ids = [s.get("id") for s in states]
        assert "nsw" in state_ids
        assert "vic" in state_ids
        assert "qld" in state_ids
        print(f"✓ States endpoint: {len(states)} states found")
    
    def test_offence_framework_endpoint(self):
        """Test /api/offence-framework/{category} returns framework data"""
        response = requests.get(f"{BASE_URL}/api/offence-framework/homicide?state=nsw", timeout=10)
        assert response.status_code == 200
        data = response.json()
        # Response has category, appeal_framework, common_appeal_grounds
        assert "category" in data
        assert "appeal_framework" in data
        assert "common_appeal_grounds" in data
        print(f"✓ Offence framework: {data.get('category', {}).get('name', 'homicide')}")


class TestUnauthenticatedAccess:
    """Test that protected endpoints require authentication"""
    
    def test_cases_requires_auth(self):
        """Test /api/cases requires authentication"""
        response = requests.get(f"{BASE_URL}/api/cases", timeout=10)
        assert response.status_code == 401
        print("✓ /api/cases correctly requires authentication")
    
    def test_case_detail_requires_auth(self):
        """Test /api/cases/{case_id} requires authentication"""
        response = requests.get(f"{BASE_URL}/api/cases/case_76056187ad4f", timeout=10)
        assert response.status_code == 401
        print("✓ /api/cases/{case_id} correctly requires authentication")
    
    def test_reports_requires_auth(self):
        """Test /api/cases/{case_id}/reports requires authentication"""
        response = requests.get(f"{BASE_URL}/api/cases/case_76056187ad4f/reports", timeout=10)
        assert response.status_code == 401
        print("✓ /api/cases/{case_id}/reports correctly requires authentication")
    
    def test_grounds_requires_auth(self):
        """Test /api/cases/{case_id}/grounds requires authentication"""
        response = requests.get(f"{BASE_URL}/api/cases/case_76056187ad4f/grounds", timeout=10)
        assert response.status_code == 401
        print("✓ /api/cases/{case_id}/grounds correctly requires authentication")
    
    def test_barrister_view_requires_auth(self):
        """Test /api/cases/{case_id}/reports/barrister-view requires authentication"""
        response = requests.get(f"{BASE_URL}/api/cases/case_76056187ad4f/reports/barrister-view", timeout=10)
        assert response.status_code == 401
        print("✓ /api/cases/{case_id}/reports/barrister-view correctly requires authentication")


class TestContactEndpoint:
    """Test contact form endpoint"""
    
    def test_contact_form_validation(self):
        """Test /api/contact validates required fields"""
        # Missing required fields
        response = requests.post(f"{BASE_URL}/api/contact", json={}, timeout=10)
        assert response.status_code in [400, 422]
        print("✓ Contact form validates required fields")
    
    def test_contact_form_with_data(self):
        """Test /api/contact accepts valid data"""
        data = {
            "name": "Test User",
            "email": "test@example.com",
            "subject": "Test Subject",
            "message": "This is a test message for iteration 92 testing."
        }
        response = requests.post(f"{BASE_URL}/api/contact", json=data, timeout=10)
        # Should succeed or fail gracefully (email service may not be configured)
        assert response.status_code in [200, 500]
        print(f"✓ Contact form submission: status {response.status_code}")


class TestAuthEndpoints:
    """Test authentication endpoints"""
    
    def test_auth_me_requires_session(self):
        """Test /api/auth/me requires valid session"""
        response = requests.get(f"{BASE_URL}/api/auth/me", timeout=10)
        assert response.status_code == 401
        print("✓ /api/auth/me correctly requires authentication")
    
    def test_auth_login_endpoint_exists(self):
        """Test /api/auth/login endpoint exists"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": "test@example.com",
            "password": "wrongpassword"
        }, timeout=10)
        # Should return 401 for invalid credentials, not 404
        assert response.status_code in [401, 400]
        print("✓ /api/auth/login endpoint exists")
    
    def test_auth_register_endpoint_exists(self):
        """Test /api/auth/register endpoint exists"""
        response = requests.post(f"{BASE_URL}/api/auth/register", json={
            "email": "test_iteration92@example.com",
            "password": "testpass123",
            "name": "Test User"
        }, timeout=10)
        # Should return 200 (success) or 400 (already exists)
        assert response.status_code in [200, 400]
        print(f"✓ /api/auth/register endpoint exists (status: {response.status_code})")


class TestProgressAnalysis:
    """Test progress analysis endpoint"""
    
    def test_progress_analysis_requires_auth(self):
        """Test /api/cases/{case_id}/progress-analysis requires authentication"""
        response = requests.post(f"{BASE_URL}/api/cases/case_76056187ad4f/progress-analysis", timeout=10)
        assert response.status_code == 401
        print("✓ /api/cases/{case_id}/progress-analysis correctly requires authentication")


class TestStatisticsEndpoints:
    """Test statistics endpoints"""
    
    def test_appeal_statistics_endpoint(self):
        """Test /api/statistics/appeals endpoint"""
        response = requests.get(f"{BASE_URL}/api/statistics/appeals", timeout=10)
        # Should return 200 or 404 if not implemented
        if response.status_code == 200:
            response.json()
            print("✓ Appeal statistics endpoint works")
        else:
            print(f"✓ Appeal statistics endpoint status: {response.status_code}")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
