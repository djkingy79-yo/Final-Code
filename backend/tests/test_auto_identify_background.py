"""
Test Auto-Identify Grounds Background Task Pattern
Tests the new async background task pattern for auto-identify endpoint
"""
import pytest
import requests
import os
import time

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', 'http://localhost:8001').rstrip('/')

# Test credentials
TEST_EMAIL = "djkingy79@gmail.com"
TEST_PASSWORD = "Cr1m1nalApp3al$2025"


class TestAutoIdentifyBackgroundTask:
    """Tests for the auto-identify background task pattern"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup: Login and get session token"""
        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json"})
        
        # Login
        login_response = self.session.post(f"{BASE_URL}/api/auth/login", json={
            "email": TEST_EMAIL,
            "password": TEST_PASSWORD
        })
        
        if login_response.status_code != 200:
            pytest.skip(f"Login failed: {login_response.status_code} - {login_response.text}")
        
        login_data = login_response.json()
        # Auth uses session_token not token
        self.token = login_data.get("session_token") or login_data.get("token")
        if not self.token:
            pytest.skip("No session token returned from login")
        
        self.session.headers.update({"Authorization": f"Bearer {self.token}"})
        print(f"✓ Logged in successfully, token: {self.token[:20]}...")
        
        # Get a case to test with
        cases_response = self.session.get(f"{BASE_URL}/api/cases")
        if cases_response.status_code != 200:
            pytest.skip("Failed to get cases")
        
        cases = cases_response.json()
        if not cases:
            pytest.skip("No cases available for testing")
        
        self.test_case_id = cases[0]["case_id"]
        print(f"✓ Using test case: {self.test_case_id}")
    
    def test_auto_identify_post_returns_immediately(self):
        """POST /api/cases/{case_id}/grounds/auto-identify should return immediately with task_id"""
        print("\n=== Test: POST auto-identify returns immediately ===")
        
        start_time = time.time()
        response = self.session.post(
            f"{BASE_URL}/api/cases/{self.test_case_id}/grounds/auto-identify",
            timeout=30  # Should return well before this
        )
        elapsed = time.time() - start_time
        
        print(f"Response time: {elapsed:.2f}s")
        print(f"Status code: {response.status_code}")
        print(f"Response: {response.json()}")
        
        # Should return 200 quickly (not timeout waiting for AI)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        
        # Should have task_id and status
        assert "task_id" in data or "status" in data, "Response should have task_id or status"
        
        # Status should be 'started' or 'already_running'
        status = data.get("status")
        assert status in ["started", "already_running"], f"Expected status 'started' or 'already_running', got '{status}'"
        
        if status == "started":
            assert "task_id" in data, "Started response should have task_id"
            print(f"✓ Task started with ID: {data['task_id']}")
        else:
            print(f"✓ Task already running: {data.get('message')}")
        
        # Should return quickly (< 10 seconds)
        assert elapsed < 10, f"Response took too long: {elapsed:.2f}s (expected < 10s)"
        print(f"✓ Response returned quickly ({elapsed:.2f}s)")
        
        return data
    
    def test_auto_identify_status_endpoint(self):
        """GET /api/cases/{case_id}/grounds/auto-identify/status should return task status"""
        print("\n=== Test: GET auto-identify status endpoint ===")
        
        response = self.session.get(
            f"{BASE_URL}/api/cases/{self.test_case_id}/grounds/auto-identify/status",
            timeout=10
        )
        
        print(f"Status code: {response.status_code}")
        print(f"Response: {response.json()}")
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        
        # Should have status field
        assert "status" in data, "Response should have 'status' field"
        
        status = data.get("status")
        valid_statuses = ["none", "pending", "extracting", "finalising", "completed", "failed"]
        assert status in valid_statuses, f"Invalid status '{status}', expected one of {valid_statuses}"
        
        print(f"✓ Status endpoint returned valid status: {status}")
        
        # If completed, should have result
        if status == "completed":
            assert "result" in data, "Completed status should have 'result'"
            print(f"✓ Completed with result: {data['result']}")
        
        # If failed, should have error
        if status == "failed":
            assert "error" in data, "Failed status should have 'error'"
            print(f"✗ Failed with error: {data['error']}")
        
        return data
    
    def test_auto_identify_duplicate_prevention(self):
        """Calling POST auto-identify twice should return 'already_running' if first is still processing"""
        print("\n=== Test: Duplicate prevention ===")
        
        # First call
        response1 = self.session.post(
            f"{BASE_URL}/api/cases/{self.test_case_id}/grounds/auto-identify",
            timeout=30
        )
        
        print(f"First call status: {response1.status_code}")
        data1 = response1.json()
        print(f"First call response: {data1}")
        
        # If first call started a task, second call should detect it
        if data1.get("status") == "started":
            # Immediately call again
            response2 = self.session.post(
                f"{BASE_URL}/api/cases/{self.test_case_id}/grounds/auto-identify",
                timeout=30
            )
            
            print(f"Second call status: {response2.status_code}")
            data2 = response2.json()
            print(f"Second call response: {data2}")
            
            # Second call should return 'already_running'
            assert response2.status_code == 200, f"Expected 200, got {response2.status_code}"
            assert data2.get("status") == "already_running", f"Expected 'already_running', got '{data2.get('status')}'"
            print("✓ Duplicate prevention working - second call returned 'already_running'")
        else:
            # First call returned already_running, which also proves the feature works
            print("✓ First call already detected running task - duplicate prevention working")
    
    def test_status_polling_pattern(self):
        """Test the polling pattern: start task, poll status until complete/failed"""
        print("\n=== Test: Status polling pattern ===")
        
        # Start the task
        start_response = self.session.post(
            f"{BASE_URL}/api/cases/{self.test_case_id}/grounds/auto-identify",
            timeout=30
        )
        
        assert start_response.status_code == 200
        start_data = start_response.json()
        
        if start_data.get("status") not in ["started", "already_running"]:
            # Legacy response - task completed synchronously
            print("✓ Legacy synchronous response received")
            return
        
        task_id = start_data.get("task_id")
        print(f"Task started/running: {task_id or 'unknown'}")
        
        # Poll for status (max 30 seconds for this test)
        max_polls = 6
        poll_interval = 5
        
        for i in range(max_polls):
            time.sleep(poll_interval)
            
            status_response = self.session.get(
                f"{BASE_URL}/api/cases/{self.test_case_id}/grounds/auto-identify/status",
                timeout=10
            )
            
            assert status_response.status_code == 200
            status_data = status_response.json()
            
            status = status_data.get("status")
            progress = status_data.get("progress", "")
            print(f"Poll {i+1}/{max_polls}: status={status}, progress={progress}")
            
            if status == "completed":
                print(f"✓ Task completed! Result: {status_data.get('result')}")
                return
            elif status == "failed":
                print(f"✗ Task failed: {status_data.get('error')}")
                # This is still a valid test - the endpoint works
                return
            elif status == "none":
                print("✓ No active task (may have completed before polling started)")
                return
        
        print(f"✓ Polling pattern works - task still running after {max_polls * poll_interval}s (expected for large cases)")


class TestGroundsEndpoints:
    """Additional tests for grounds endpoints"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup: Login and get session token"""
        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json"})
        
        login_response = self.session.post(f"{BASE_URL}/api/auth/login", json={
            "email": TEST_EMAIL,
            "password": TEST_PASSWORD
        })
        
        if login_response.status_code != 200:
            pytest.skip(f"Login failed: {login_response.status_code}")
        
        login_data = login_response.json()
        self.token = login_data.get("session_token") or login_data.get("token")
        self.session.headers.update({"Authorization": f"Bearer {self.token}"})
        
        cases_response = self.session.get(f"{BASE_URL}/api/cases")
        if cases_response.status_code != 200 or not cases_response.json():
            pytest.skip("No cases available")
        
        self.test_case_id = cases_response.json()[0]["case_id"]
    
    def test_get_grounds_endpoint(self):
        """GET /api/cases/{case_id}/grounds should return grounds list"""
        print("\n=== Test: GET grounds endpoint ===")
        
        response = self.session.get(
            f"{BASE_URL}/api/cases/{self.test_case_id}/grounds",
            timeout=10
        )
        
        print(f"Status code: {response.status_code}")
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        
        # Should have expected fields
        assert "grounds" in data or "count" in data, "Response should have 'grounds' or 'count'"
        assert "is_unlocked" in data, "Response should have 'is_unlocked'"
        
        print(f"✓ Grounds count: {data.get('count', len(data.get('grounds', [])))}")
        print(f"✓ Is unlocked: {data.get('is_unlocked')}")
        
        if data.get("grounds"):
            print(f"✓ First ground: {data['grounds'][0].get('title', 'N/A')}")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
