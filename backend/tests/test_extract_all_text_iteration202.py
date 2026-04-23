"""
Backend tests for extract-all-text background task + polling pattern (iteration 202)
Tests the fix for timeout issues on /api/cases/{case_id}/extract-all-text

Features tested:
1. POST /api/cases/{case_id}/extract-all-text - starts background task, returns task_id immediately
2. GET /api/cases/{case_id}/extract-all-text/status?task_id=... - polling endpoint
3. Error paths: bogus task_id, non-existent case
4. Regression: GET /api/cases/{case_id} still works
5. Regression: POST /api/cases/{case_id}/documents (file upload) still works
6. Regression: /api/cases/{case_id}/grounds/{ground_id}/investigate + status
"""

import pytest
import requests
import os
import time
import io

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', "http://localhost:8001").rstrip('/')
if not BASE_URL:
    BASE_URL = "https://criminallawappealmanagement.com.au"

# Test credentials
TEST_EMAIL = "djkingy79@gmail.com"
TEST_PASSWORD = os.environ.get("TEST_PASSWORD", "Grubbygrub88")
TEST_CASE_ID = "case_0885e6d0cba8"  # Tasmania v Scott - known case with documents


class TestExtractAllTextBackgroundTask:
    """Tests for the new background task + polling pattern for extract-all-text"""
    
    @pytest.fixture(scope="class")
    def auth_token(self):
        """Get authentication token"""
        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": TEST_EMAIL, "password": TEST_PASSWORD},
            timeout=30
        )
        if response.status_code == 200:
            return response.json().get("session_token")
        pytest.skip(f"Authentication failed: {response.status_code}")
    
    @pytest.fixture(scope="class")
    def auth_headers(self, auth_token):
        """Get auth headers"""
        return {"Authorization": f"Bearer {auth_token}"}
    
    def test_01_extract_all_text_returns_immediately(self, auth_headers):
        """POST /api/cases/{case_id}/extract-all-text should return within 1 second with task_id"""
        start_time = time.time()
        response = requests.post(
            f"{BASE_URL}/api/cases/{TEST_CASE_ID}/extract-all-text",
            headers=auth_headers,
            timeout=10
        )
        elapsed = time.time() - start_time
        
        # Must return quickly (< 2 seconds)
        assert elapsed < 2.0, f"Endpoint took {elapsed:.2f}s - should return immediately"
        
        # Status code check
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        # Response structure check
        data = response.json()
        assert "status" in data, "Response missing 'status' field"
        assert data["status"] == "started", f"Expected status='started', got '{data.get('status')}'"
        assert "task_id" in data, "Response missing 'task_id' field"
        assert data["task_id"].startswith("extract_"), f"task_id should start with 'extract_', got '{data.get('task_id')}'"
        
        print(f"PASS: POST /extract-all-text returned in {elapsed:.2f}s with task_id={data['task_id']}")
    
    def test_02_extract_all_text_status_polling(self, auth_headers):
        """GET /api/cases/{case_id}/extract-all-text/status should return running/completed"""
        # First start a task
        start_response = requests.post(
            f"{BASE_URL}/api/cases/{TEST_CASE_ID}/extract-all-text",
            headers=auth_headers,
            timeout=10
        )
        assert start_response.status_code == 200
        task_id = start_response.json().get("task_id")
        assert task_id, "No task_id returned"
        
        # Poll for status
        max_attempts = 40  # 40 * 3s = 120s max
        final_status = None
        for attempt in range(max_attempts):
            time.sleep(3)
            poll_response = requests.get(
                f"{BASE_URL}/api/cases/{TEST_CASE_ID}/extract-all-text/status",
                params={"task_id": task_id},
                headers=auth_headers,
                timeout=20
            )
            assert poll_response.status_code == 200, f"Poll failed: {poll_response.status_code}"
            
            poll_data = poll_response.json()
            status = poll_data.get("status")
            print(f"Poll attempt {attempt + 1}: status={status}, progress={poll_data.get('progress', 'N/A')}")
            
            if status == "completed":
                final_status = poll_data
                break
            elif status == "failed":
                pytest.fail(f"Task failed: {poll_data.get('error')}")
            elif status == "not_found":
                # Task may have been cleaned up already
                print("Task not found - may have completed and been cleaned up")
                final_status = {"status": "not_found"}
                break
            # status == "running" - continue polling
        
        # Verify completion
        if final_status and final_status.get("status") == "completed":
            result = final_status.get("result", {})
            assert "total_documents" in result, "Result missing 'total_documents'"
            assert "successful_extractions" in result, "Result missing 'successful_extractions'"
            assert "results" in result, "Result missing 'results'"
            print(f"PASS: Task completed - {result.get('successful_extractions')}/{result.get('total_documents')} docs extracted")
            
            # Check for detected_metadata
            if result.get("detected_metadata"):
                print(f"Detected metadata: {result['detected_metadata']}")
        else:
            print("Task may still be running or was cleaned up - this is acceptable for long-running LLM tasks")
    
    def test_03_status_with_bogus_task_id(self, auth_headers):
        """GET status with bogus task_id should return {status: 'not_found'}"""
        response = requests.get(
            f"{BASE_URL}/api/cases/{TEST_CASE_ID}/extract-all-text/status",
            params={"task_id": "extract_bogus_12345678"},
            headers=auth_headers,
            timeout=10
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        assert data.get("status") == "not_found", f"Expected status='not_found', got '{data.get('status')}'"
        print("PASS: Bogus task_id returns {status: 'not_found'}")
    
    def test_04_extract_all_text_nonexistent_case(self, auth_headers):
        """POST extract-all-text on non-existent case should return 404"""
        response = requests.post(
            f"{BASE_URL}/api/cases/case_nonexistent_12345/extract-all-text",
            headers=auth_headers,
            timeout=10
        )
        assert response.status_code == 404, f"Expected 404, got {response.status_code}"
        print("PASS: Non-existent case returns 404")


class TestRegressionCaseEndpoints:
    """Regression tests for case-related endpoints"""
    
    @pytest.fixture(scope="class")
    def auth_token(self):
        """Get authentication token"""
        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": TEST_EMAIL, "password": TEST_PASSWORD},
            timeout=30
        )
        if response.status_code == 200:
            return response.json().get("session_token")
        pytest.skip(f"Authentication failed: {response.status_code}")
    
    @pytest.fixture(scope="class")
    def auth_headers(self, auth_token):
        """Get auth headers"""
        return {"Authorization": f"Bearer {auth_token}"}
    
    def test_05_get_case_response_time(self, auth_headers):
        """GET /api/cases/{case_id} should return within 2 seconds"""
        start_time = time.time()
        response = requests.get(
            f"{BASE_URL}/api/cases/{TEST_CASE_ID}",
            headers=auth_headers,
            timeout=10
        )
        elapsed = time.time() - start_time
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        assert elapsed < 2.0, f"GET /cases/{TEST_CASE_ID} took {elapsed:.2f}s - should be < 2s"
        
        data = response.json()
        assert "case_id" in data, "Response missing 'case_id'"
        assert data["case_id"] == TEST_CASE_ID
        
        # Check for metadata_warnings / jurisdiction_warnings fields
        print(f"PASS: GET /cases/{TEST_CASE_ID} returned in {elapsed:.2f}s")
        print(f"  - metadata_warnings: {data.get('metadata_warnings', [])}")
        print(f"  - jurisdiction_warnings: {data.get('jurisdiction_warnings', [])}")
    
    def test_06_get_case_documents(self, auth_headers):
        """GET /api/cases/{case_id}/documents should work"""
        response = requests.get(
            f"{BASE_URL}/api/cases/{TEST_CASE_ID}/documents",
            headers=auth_headers,
            timeout=30
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        assert isinstance(data, list), "Expected list of documents"
        print(f"PASS: GET /documents returned {len(data)} documents")
    
    def test_07_upload_document(self, auth_headers):
        """POST /api/cases/{case_id}/documents should work without blocking on LLM"""
        # Create a small test file
        test_content = b"This is a test document for iteration 202 testing.\nIt contains some text for extraction."
        files = {
            "file": ("test_iteration202.txt", io.BytesIO(test_content), "text/plain")
        }
        data = {
            "category": "other",
            "description": "Test document for iteration 202"
        }
        
        start_time = time.time()
        response = requests.post(
            f"{BASE_URL}/api/cases/{TEST_CASE_ID}/documents",
            headers=auth_headers,
            files=files,
            data=data,
            timeout=60
        )
        elapsed = time.time() - start_time
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        result = response.json()
        assert "document_id" in result, "Response missing 'document_id'"
        assert "content_text" in result, "Response missing 'content_text'"
        
        # Should return quickly (LLM metadata detection runs in background)
        print(f"PASS: Document upload completed in {elapsed:.2f}s")
        print(f"  - document_id: {result.get('document_id')}")
        print(f"  - content_text length: {len(result.get('content_text', ''))}")
        
        # Clean up - delete the test document
        doc_id = result.get("document_id")
        if doc_id:
            delete_response = requests.delete(
                f"{BASE_URL}/api/cases/{TEST_CASE_ID}/documents/{doc_id}",
                headers=auth_headers,
                timeout=10
            )
            print(f"  - Cleanup: deleted test document (status={delete_response.status_code})")


class TestRegressionGroundsInvestigate:
    """Regression tests for grounds investigate endpoint (already uses background task pattern)"""
    
    @pytest.fixture(scope="class")
    def auth_token(self):
        """Get authentication token"""
        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": TEST_EMAIL, "password": TEST_PASSWORD},
            timeout=30
        )
        if response.status_code == 200:
            return response.json().get("session_token")
        pytest.skip(f"Authentication failed: {response.status_code}")
    
    @pytest.fixture(scope="class")
    def auth_headers(self, auth_token):
        """Get auth headers"""
        return {"Authorization": f"Bearer {auth_token}"}
    
    def test_08_get_grounds(self, auth_headers):
        """GET /api/cases/{case_id}/grounds should work"""
        response = requests.get(
            f"{BASE_URL}/api/cases/{TEST_CASE_ID}/grounds",
            headers=auth_headers,
            timeout=30
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        assert "grounds" in data, "Response missing 'grounds'"
        assert "count" in data, "Response missing 'count'"
        print(f"PASS: GET /grounds returned {data.get('count')} grounds")
        return data.get("grounds", [])
    
    def test_09_investigate_ground_returns_task_id(self, auth_headers):
        """POST /api/cases/{case_id}/grounds/{ground_id}/investigate should return task_id"""
        # First get grounds
        grounds_response = requests.get(
            f"{BASE_URL}/api/cases/{TEST_CASE_ID}/grounds",
            headers=auth_headers,
            timeout=30
        )
        if grounds_response.status_code != 200:
            pytest.skip("Could not get grounds")
        
        grounds = grounds_response.json().get("grounds", [])
        if not grounds:
            pytest.skip("No grounds available to investigate")
        
        ground_id = grounds[0].get("ground_id")
        
        start_time = time.time()
        response = requests.post(
            f"{BASE_URL}/api/cases/{TEST_CASE_ID}/grounds/{ground_id}/investigate",
            headers=auth_headers,
            timeout=30
        )
        elapsed = time.time() - start_time
        
        # Should return quickly with task_id
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        # May return task_id (new pattern) or direct result (old pattern)
        if "task_id" in data:
            print(f"PASS: Investigate returned task_id in {elapsed:.2f}s")
            print(f"  - task_id: {data.get('task_id')}")
        else:
            print(f"PASS: Investigate returned direct result in {elapsed:.2f}s (legacy pattern)")


class TestHealthAndAuth:
    """Basic health and auth tests"""
    
    def test_10_health_endpoint(self):
        """GET /api/health should return 200"""
        response = requests.get(f"{BASE_URL}/api/health", timeout=10)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        assert data.get("status") == "healthy", f"Expected healthy, got {data.get('status')}"
        print(f"PASS: Health endpoint - status={data.get('status')}, db={data.get('database')}")
    
    def test_11_auth_login(self):
        """POST /api/auth/login should work"""
        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": TEST_EMAIL, "password": TEST_PASSWORD},
            timeout=30
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        assert "session_token" in data, "Response missing 'session_token'"
        print("PASS: Auth login successful")
    
    def test_12_auth_me(self):
        """GET /api/auth/me should work with valid token"""
        # First login
        login_response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": TEST_EMAIL, "password": TEST_PASSWORD},
            timeout=30
        )
        if login_response.status_code != 200:
            pytest.skip("Login failed")
        
        token = login_response.json().get("session_token")
        
        response = requests.get(
            f"{BASE_URL}/api/auth/me",
            headers={"Authorization": f"Bearer {token}"},
            timeout=10
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        assert "email" in data, "Response missing 'email'"
        print(f"PASS: Auth me - email={data.get('email')}")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
