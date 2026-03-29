"""
Test health check endpoint and basic API functionality
Iteration 54 - Backend API verification test
"""
import pytest
import requests
import os

BASE_URL = 'http://localhost:8001'

class TestHealthEndpoint:
    """Health check endpoint tests - verifies /api/health returns correct structure"""
    
    def test_health_endpoint_returns_200(self):
        """Test /api/health returns 200 status code"""
        response = requests.get(f"{BASE_URL}/api/health", timeout=10)
        assert response.status_code == 200
        print(f"✅ Health endpoint returned status: {response.status_code}")
    
    def test_health_response_has_status_field(self):
        """Test health response contains status field"""
        response = requests.get(f"{BASE_URL}/api/health", timeout=10)
        data = response.json()
        assert "status" in data, "Response missing 'status' field"
        assert data["status"] in ["healthy", "degraded"], f"Unexpected status: {data['status']}"
        print(f"✅ Health status: {data['status']}")
    
    def test_health_response_has_database_field(self):
        """Test health response contains database field"""
        response = requests.get(f"{BASE_URL}/api/health", timeout=10)
        data = response.json()
        assert "database" in data, "Response missing 'database' field"
        assert data["database"] in ["connected", "disconnected"], f"Unexpected database status: {data['database']}"
        print(f"✅ Database status: {data['database']}")
    
    def test_health_response_has_timestamp_field(self):
        """Test health response contains timestamp field"""
        response = requests.get(f"{BASE_URL}/api/health", timeout=10)
        data = response.json()
        assert "timestamp" in data, "Response missing 'timestamp' field"
        assert len(data["timestamp"]) > 0, "Timestamp should not be empty"
        print(f"✅ Timestamp: {data['timestamp']}")
    
    def test_database_is_connected(self):
        """Test that database is actually connected"""
        response = requests.get(f"{BASE_URL}/api/health", timeout=10)
        data = response.json()
        assert data["database"] == "connected", f"Database not connected: {data['database']}"
        assert data["status"] == "healthy", f"Health status not healthy: {data['status']}"
        print(f"✅ Database connected and healthy")


class TestRootEndpoint:
    """Root API endpoint tests"""
    
    def test_root_endpoint_returns_200(self):
        """Test /api/ returns 200 status code"""
        response = requests.get(f"{BASE_URL}/api/", timeout=10)
        assert response.status_code == 200
        print(f"✅ Root endpoint returned status: {response.status_code}")
    
    def test_root_endpoint_has_message(self):
        """Test root response contains message and status"""
        response = requests.get(f"{BASE_URL}/api/", timeout=10)
        data = response.json()
        assert "message" in data, "Response missing 'message' field"
        assert "status" in data, "Response missing 'status' field"
        print(f"✅ Root message: {data['message']}, Status: {data['status']}")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
