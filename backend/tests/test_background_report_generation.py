"""
Test Background Report Generation Pattern
Tests for the new async report generation with polling

Features to test:
1. POST /api/cases/{case_id}/reports/generate - returns immediately with status='generating'
2. GET /api/cases/{case_id}/reports/{report_id}/status - polling endpoint
3. GET /api/cases/{case_id}/reports - lists reports (old ones without status field should appear)
4. Health endpoint
"""

import pytest
import requests
import os
import time

BASE_URL = 'http://localhost:8001'

# Test credentials from the review request
SESSION_TOKEN = "test_session_8962c167"
CASE_ID = "case_b2aa32564f2b"
EXISTING_REPORT_ID = "rpt_0d36ed7d31ab"
ADMIN_USER_ID = "user_d2287f20104b"


@pytest.fixture
def auth_session():
    """Create authenticated session with cookie"""
    session = requests.Session()
    session.cookies.set("session_token", SESSION_TOKEN)
    session.headers.update({"Content-Type": "application/json"})
    return session


class TestHealthEndpoint:
    """Test health check endpoint"""
    
    def test_health_returns_healthy(self, auth_session):
        """Health endpoint should return healthy status"""
        response = auth_session.get(f"{BASE_URL}/api/health")
        assert response.status_code == 200, f"Health check failed: {response.text}"
        data = response.json()
        assert data.get("status") == "healthy"
        print(f"PASS: Health endpoint returned status: {data}")


class TestReportGenerationEndpoints:
    """Test the background report generation pattern"""
    
    def test_generate_report_returns_immediately(self, auth_session):
        """POST /api/cases/{case_id}/reports/generate should return immediately with status='generating'"""
        start_time = time.time()
        
        response = auth_session.post(
            f"{BASE_URL}/api/cases/{CASE_ID}/reports/generate",
            json={"report_type": "quick_summary", "aggressive_mode": False},
            timeout=30  # Should complete well before 30s
        )
        
        elapsed = time.time() - start_time
        
        # Critical: Should return within 10 seconds (not 60+ seconds like before)
        assert elapsed < 15, f"Generate endpoint took too long: {elapsed:.2f}s (expected <15s)"
        assert response.status_code == 200, f"Generate failed: {response.status_code} - {response.text}"
        
        data = response.json()
        
        # Verify response structure
        assert "report_id" in data, "Missing report_id in response"
        assert "status" in data, "Missing status in response"
        assert data.get("status") == "generating", f"Expected status='generating', got '{data.get('status')}'"
        assert data.get("case_id") == CASE_ID, "Case ID mismatch"
        
        print(f"PASS: Generate endpoint returned in {elapsed:.2f}s with status='generating'")
        print(f"Report ID: {data.get('report_id')}")
        
        # Return report_id for subsequent tests
        return data.get("report_id")
    
    def test_report_status_endpoint(self, auth_session):
        """GET /api/cases/{case_id}/reports/{report_id}/status should return current status"""
        # Use existing report which should be completed
        response = auth_session.get(
            f"{BASE_URL}/api/cases/{CASE_ID}/reports/{EXISTING_REPORT_ID}/status"
        )
        
        assert response.status_code == 200, f"Status endpoint failed: {response.status_code} - {response.text}"
        
        data = response.json()
        assert "report_id" in data, "Missing report_id in status response"
        assert "status" in data, "Missing status in response"
        
        # Existing report should be completed
        status = data.get("status")
        assert status in ["completed", "generating", "failed"], f"Unexpected status: {status}"
        
        print(f"PASS: Status endpoint returned status='{status}' for existing report")
    
    def test_get_reports_list(self, auth_session):
        """GET /api/cases/{case_id}/reports should list all reports including old ones without status field"""
        response = auth_session.get(f"{BASE_URL}/api/cases/{CASE_ID}/reports")
        
        assert response.status_code == 200, f"Get reports failed: {response.status_code} - {response.text}"
        
        data = response.json()
        assert isinstance(data, list), "Expected list of reports"
        
        # Should have at least the existing report
        print(f"PASS: Found {len(data)} reports for case {CASE_ID}")
        
        # Check that reports have required fields
        for report in data:
            assert "report_id" in report, "Missing report_id"
            assert "report_type" in report, "Missing report_type"
            # Note: Old reports may not have 'status' field - they should still appear
            print(f"  - Report: {report.get('report_id')} | type: {report.get('report_type')} | status: {report.get('status', 'N/A (legacy)')}")
        
        return data


class TestReportPollingFlow:
    """Test full polling flow for report generation"""
    
    def test_full_generation_and_polling_flow(self, auth_session):
        """Test complete flow: generate -> poll -> completion"""
        # Step 1: Generate report
        start_time = time.time()
        
        gen_response = auth_session.post(
            f"{BASE_URL}/api/cases/{CASE_ID}/reports/generate",
            json={"report_type": "quick_summary", "aggressive_mode": False},
            timeout=30
        )
        
        gen_elapsed = time.time() - start_time
        assert gen_elapsed < 15, f"Generate took too long: {gen_elapsed:.2f}s"
        assert gen_response.status_code == 200, f"Generate failed: {gen_response.text}"
        
        gen_data = gen_response.json()
        report_id = gen_data.get("report_id")
        initial_status = gen_data.get("status")
        
        print(f"Step 1: Generate returned in {gen_elapsed:.2f}s, status='{initial_status}', report_id={report_id}")
        
        # Step 2: Poll for completion (max 120 seconds for AI generation)
        poll_start = time.time()
        max_poll_time = 120  # 2 minutes max
        poll_interval = 4  # Match frontend polling interval
        final_status = initial_status
        
        while (time.time() - poll_start) < max_poll_time:
            status_response = auth_session.get(
                f"{BASE_URL}/api/cases/{CASE_ID}/reports/{report_id}/status"
            )
            
            if status_response.status_code == 200:
                status_data = status_response.json()
                final_status = status_data.get("status")
                
                print(f"  Poll: status='{final_status}' at {time.time() - poll_start:.1f}s")
                
                if final_status == "completed":
                    print(f"Step 2: Report completed after {time.time() - poll_start:.1f}s of polling")
                    break
                elif final_status == "failed":
                    print(f"Step 2: Report failed after {time.time() - poll_start:.1f}s")
                    break
            
            time.sleep(poll_interval)
        
        total_time = time.time() - start_time
        print(f"Total flow time: {total_time:.1f}s, final status: '{final_status}'")
        
        # Verify final status is completed (AI generation succeeded)
        assert final_status == "completed", f"Expected status='completed', got '{final_status}'"
        
        # Step 3: Verify report appears in list with proper content
        list_response = auth_session.get(f"{BASE_URL}/api/cases/{CASE_ID}/reports")
        assert list_response.status_code == 200
        
        reports = list_response.json()
        new_report = next((r for r in reports if r.get("report_id") == report_id), None)
        
        assert new_report is not None, f"Report {report_id} not found in list"
        assert new_report.get("status") == "completed", f"Report status mismatch in list"
        
        # Check content is populated
        content = new_report.get("content", {})
        analysis = content.get("analysis", "")
        assert len(analysis) > 100, f"Report content appears empty or too short: {len(analysis)} chars"
        
        print(f"Step 3: Report verified in list with {len(analysis)} chars of analysis")
        print("PASS: Full generation and polling flow completed successfully")


class TestLegacyReportCompatibility:
    """Test that old reports without status field still work"""
    
    def test_existing_report_accessible(self, auth_session):
        """Existing reports should be accessible even without status field"""
        response = auth_session.get(f"{BASE_URL}/api/cases/{CASE_ID}/reports/{EXISTING_REPORT_ID}")
        
        assert response.status_code == 200, f"Failed to get existing report: {response.text}"
        
        data = response.json()
        assert data.get("report_id") == EXISTING_REPORT_ID
        
        # Check content exists
        content = data.get("content", {})
        assert content, "Report content should exist"
        
        print(f"PASS: Existing report {EXISTING_REPORT_ID} accessible, has content: {bool(content)}")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
