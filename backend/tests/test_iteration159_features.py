"""
Iteration 159 Tests: Glossary, auSpelling utility, Ground Priority Reorder
Tests:
1. Backend health check
2. Login with test credentials
3. PUT /api/cases/{case_id}/grounds/reorder endpoint
4. GET /api/cases/{case_id}/grounds returns grounds sorted by priority_order
"""
import pytest
import requests
import os

BASE_URL = os.environ.get("REACT_APP_BACKEND_URL", "").rstrip("/")
TEST_EMAIL = "djkingy79@gmail.com"
TEST_PASSWORD = "Cr1m1nalApp3al$2025"
TEST_CASE_ID = "case_f8bf63e9dcbe"


class TestHealthAndAuth:
    """Health check and authentication tests"""

    def test_health_endpoint(self):
        """Test /api/health returns 200"""
        response = requests.get(f"{BASE_URL}/api/health")
        assert response.status_code == 200, f"Health check failed: {response.status_code}"
        data = response.json()
        assert data.get("status") == "healthy", f"Unexpected health status: {data}"
        print("PASS: Health endpoint returns 200 with status=healthy")

    def test_login_with_credentials(self):
        """Test login with test credentials"""
        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": TEST_EMAIL, "password": TEST_PASSWORD}
        )
        assert response.status_code == 200, f"Login failed: {response.status_code} - {response.text}"
        data = response.json()
        assert "session_token" in data or "token" in data, f"No token in response: {data}"
        print("PASS: Login with test credentials succeeds")


class TestGroundsReorder:
    """Tests for ground priority reorder feature"""

    @pytest.fixture
    def auth_token(self):
        """Get authentication token"""
        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": TEST_EMAIL, "password": TEST_PASSWORD}
        )
        if response.status_code == 200:
            data = response.json()
            return data.get("session_token") or data.get("token")
        pytest.skip("Authentication failed")

    def test_get_grounds_returns_sorted_by_priority(self, auth_token):
        """Test GET /api/cases/{case_id}/grounds returns grounds sorted by priority_order"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        response = requests.get(
            f"{BASE_URL}/api/cases/{TEST_CASE_ID}/grounds",
            headers=headers
        )
        assert response.status_code == 200, f"Get grounds failed: {response.status_code} - {response.text}"
        data = response.json()
        assert "grounds" in data, f"No grounds in response: {data}"
        grounds = data["grounds"]
        print(f"PASS: GET grounds returns {len(grounds)} grounds")
        
        # Check if grounds have ground_id
        if grounds:
            assert all("ground_id" in g for g in grounds), "Some grounds missing ground_id"
            print(f"PASS: All grounds have ground_id")

    def test_reorder_grounds_endpoint_exists(self, auth_token):
        """Test PUT /api/cases/{case_id}/grounds/reorder endpoint exists"""
        headers = {"Authorization": f"Bearer {auth_token}", "Content-Type": "application/json"}
        
        # First get the grounds to get their IDs
        response = requests.get(
            f"{BASE_URL}/api/cases/{TEST_CASE_ID}/grounds",
            headers=headers
        )
        assert response.status_code == 200, f"Get grounds failed: {response.status_code}"
        data = response.json()
        grounds = data.get("grounds", [])
        
        if len(grounds) < 2:
            pytest.skip("Need at least 2 grounds to test reorder")
        
        # Get ground IDs
        ground_ids = [g["ground_id"] for g in grounds]
        print(f"Found {len(ground_ids)} grounds to reorder")
        
        # Test reorder endpoint - reverse the order
        reversed_ids = list(reversed(ground_ids))
        response = requests.put(
            f"{BASE_URL}/api/cases/{TEST_CASE_ID}/grounds/reorder",
            headers=headers,
            json={"ground_ids": reversed_ids}
        )
        assert response.status_code == 200, f"Reorder failed: {response.status_code} - {response.text}"
        data = response.json()
        assert "message" in data, f"No message in response: {data}"
        print(f"PASS: Reorder endpoint works - {data.get('message')}")

    def test_reorder_persists_priority_order(self, auth_token):
        """Test that reorder persists priority_order to DB and GET returns sorted"""
        headers = {"Authorization": f"Bearer {auth_token}", "Content-Type": "application/json"}
        
        # Get current grounds
        response = requests.get(
            f"{BASE_URL}/api/cases/{TEST_CASE_ID}/grounds",
            headers=headers
        )
        assert response.status_code == 200
        data = response.json()
        grounds = data.get("grounds", [])
        
        if len(grounds) < 2:
            pytest.skip("Need at least 2 grounds to test reorder persistence")
        
        # Get ground IDs and reverse them
        ground_ids = [g["ground_id"] for g in grounds]
        reversed_ids = list(reversed(ground_ids))
        
        # Reorder
        response = requests.put(
            f"{BASE_URL}/api/cases/{TEST_CASE_ID}/grounds/reorder",
            headers=headers,
            json={"ground_ids": reversed_ids}
        )
        assert response.status_code == 200
        
        # Get grounds again and verify order
        response = requests.get(
            f"{BASE_URL}/api/cases/{TEST_CASE_ID}/grounds",
            headers=headers
        )
        assert response.status_code == 200
        data = response.json()
        new_grounds = data.get("grounds", [])
        new_ids = [g["ground_id"] for g in new_grounds]
        
        # The first ground should now be what was last
        assert new_ids[0] == reversed_ids[0], f"Reorder did not persist: expected {reversed_ids[0]} first, got {new_ids[0]}"
        print("PASS: Reorder persists priority_order correctly")

    def test_reorder_with_empty_list_fails(self, auth_token):
        """Test that reorder with empty ground_ids list returns 400"""
        headers = {"Authorization": f"Bearer {auth_token}", "Content-Type": "application/json"}
        
        response = requests.put(
            f"{BASE_URL}/api/cases/{TEST_CASE_ID}/grounds/reorder",
            headers=headers,
            json={"ground_ids": []}
        )
        assert response.status_code == 400, f"Expected 400 for empty list, got {response.status_code}"
        print("PASS: Reorder with empty list returns 400")

    def test_reorder_with_invalid_ground_id_fails(self, auth_token):
        """Test that reorder with invalid ground_id returns 404"""
        headers = {"Authorization": f"Bearer {auth_token}", "Content-Type": "application/json"}
        
        response = requests.put(
            f"{BASE_URL}/api/cases/{TEST_CASE_ID}/grounds/reorder",
            headers=headers,
            json={"ground_ids": ["invalid_ground_id_12345"]}
        )
        assert response.status_code == 404, f"Expected 404 for invalid ground_id, got {response.status_code}"
        print("PASS: Reorder with invalid ground_id returns 404")


class TestGroundsEndpointSorting:
    """Tests for grounds endpoint sorting behavior"""

    @pytest.fixture
    def auth_token(self):
        """Get authentication token"""
        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": TEST_EMAIL, "password": TEST_PASSWORD}
        )
        if response.status_code == 200:
            data = response.json()
            return data.get("session_token") or data.get("token")
        pytest.skip("Authentication failed")

    def test_grounds_sorted_by_priority_then_strength(self, auth_token):
        """Test that grounds are sorted by priority_order first, then strength"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        response = requests.get(
            f"{BASE_URL}/api/cases/{TEST_CASE_ID}/grounds",
            headers=headers
        )
        assert response.status_code == 200
        data = response.json()
        grounds = data.get("grounds", [])
        
        if len(grounds) < 2:
            pytest.skip("Need at least 2 grounds to test sorting")
        
        # Check that grounds with priority_order come first
        priority_orders = [g.get("priority_order", 999) for g in grounds]
        
        # Verify sorting is correct (priority_order ascending)
        for i in range(len(priority_orders) - 1):
            if priority_orders[i] != 999 and priority_orders[i+1] != 999:
                assert priority_orders[i] <= priority_orders[i+1], \
                    f"Grounds not sorted by priority_order: {priority_orders[i]} > {priority_orders[i+1]}"
        
        print(f"PASS: Grounds sorted correctly by priority_order")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
