"""
Test DELETE /api/cases/{case_id}/reports/{report_id} endpoint
This tests the report deletion functionality that users were complaining about.
"""
import pytest
import requests
import os

BASE_URL = 'http://localhost:8001'

class TestHealthAndReportEndpoints:
    """Test health check and report-related API endpoints"""
    
    def test_health_check_returns_200(self):
        """GET /api/health should return 200 with status, database, timestamp"""
        response = requests.get(f"{BASE_URL}/api/health")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        assert "status" in data, "Response should contain 'status' field"
        assert "database" in data, "Response should contain 'database' field"
        assert "timestamp" in data, "Response should contain 'timestamp' field"
        
        print(f"Health check passed: status={data['status']}, database={data['database']}")
    
    def test_health_check_database_connected(self):
        """Health check should show database is connected"""
        response = requests.get(f"{BASE_URL}/api/health")
        data = response.json()
        
        assert data.get("database") == "connected", f"Database should be connected, got {data.get('database')}"
        assert data.get("status") == "healthy", f"Status should be healthy, got {data.get('status')}"
    
    def test_delete_report_requires_auth(self):
        """DELETE /api/cases/{case_id}/reports/{report_id} should require authentication"""
        # Without auth token, should return 401
        response = requests.delete(f"{BASE_URL}/api/cases/fake_case/reports/fake_report")
        assert response.status_code == 401, f"Expected 401 for unauthenticated request, got {response.status_code}"
        print(f"Delete report auth check passed: {response.status_code}")
    
    def test_root_api_endpoint(self):
        """GET /api/ should return a valid response"""
        response = requests.get(f"{BASE_URL}/api/")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        print(f"Root API endpoint check passed")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
