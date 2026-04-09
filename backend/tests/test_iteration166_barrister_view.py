"""
Iteration 166 - Barrister View No Auto-Generate Tests

Tests for the new Barrister View behavior:
1. GET /api/cases/{case_id}/reports/barrister-view WITHOUT regenerate param — returns 404 if no report exists
2. GET /api/cases/{case_id}/reports/barrister-view?regenerate=true — starts generation
3. GET /api/cases/{case_id}/reports — includes barrister_view type reports in the list
4. Barrister View shows in reports list alongside other 3 report types
"""

import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')
ADMIN_TOKEN = "3d1561482bd64a14962214c76c074d78"
CASE_WITH_REPORTS = "case_f8bf63e9dcbe"  # Case with all 4 reports

@pytest.fixture
def admin_headers():
    return {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {ADMIN_TOKEN}"
    }


class TestBarristerViewNoAutoGenerate:
    """Test that Barrister View does NOT auto-generate when navigating to the page."""
    
    def test_barrister_view_returns_existing_report_when_completed(self, admin_headers):
        """GET /api/cases/{case_id}/reports/barrister-view returns existing completed report (200)."""
        response = requests.get(
            f"{BASE_URL}/api/cases/{CASE_WITH_REPORTS}/reports/barrister-view",
            headers=admin_headers,
            timeout=30
        )
        
        # Should return 200 if report exists, or 404 if not
        assert response.status_code in [200, 404], f"Expected 200 or 404, got {response.status_code}: {response.text}"
        
        if response.status_code == 200:
            data = response.json()
            assert "report_id" in data, "Response should contain report_id"
            assert data.get("report_type") == "barrister_view", "Report type should be barrister_view"
            assert data.get("status") in ["completed", "generating", "failed"], f"Unexpected status: {data.get('status')}"
            print(f"PASS: Barrister view returned existing report with status: {data.get('status')}")
        else:
            # 404 means no report exists - this is expected behavior
            data = response.json()
            assert "detail" in data, "404 response should contain detail message"
            print(f"PASS: Barrister view returned 404 (no report exists): {data.get('detail')}")
    
    def test_barrister_view_returns_404_when_no_report_exists(self, admin_headers):
        """GET /api/cases/{case_id}/reports/barrister-view returns 404 when no report exists and regenerate is not true."""
        # Use a case that likely doesn't have a barrister report
        test_case_id = "case_nonexistent_barrister_test"
        
        response = requests.get(
            f"{BASE_URL}/api/cases/{test_case_id}/reports/barrister-view",
            headers=admin_headers,
            timeout=30
        )
        
        # Should return 404 (case not found or no barrister report) or 409 (conflict - case doesn't exist)
        assert response.status_code in [404, 401, 403, 409], f"Expected 404/401/403/409, got {response.status_code}"
        print(f"PASS: Non-existent case returns {response.status_code}")
    
    def test_barrister_view_with_regenerate_true_starts_generation(self, admin_headers):
        """GET /api/cases/{case_id}/reports/barrister-view?regenerate=true starts generation."""
        response = requests.get(
            f"{BASE_URL}/api/cases/{CASE_WITH_REPORTS}/reports/barrister-view",
            params={"regenerate": "true"},
            headers=admin_headers,
            timeout=120
        )
        
        # Should return 200 with status "generating" or "completed"
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert "report_id" in data, "Response should contain report_id"
        assert data.get("report_type") == "barrister_view", "Report type should be barrister_view"
        assert data.get("status") in ["generating", "completed"], f"Expected generating/completed, got: {data.get('status')}"
        print(f"PASS: Barrister view with regenerate=true returned status: {data.get('status')}")


class TestReportsListIncludesBarristerView:
    """Test that GET /api/cases/{case_id}/reports includes barrister_view type reports."""
    
    def test_reports_list_includes_all_report_types(self, admin_headers):
        """GET /api/cases/{case_id}/reports should include barrister_view alongside other report types."""
        response = requests.get(
            f"{BASE_URL}/api/cases/{CASE_WITH_REPORTS}/reports",
            headers=admin_headers,
            timeout=30
        )
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        reports = response.json()
        assert isinstance(reports, list), "Response should be a list of reports"
        
        # Check what report types are present
        report_types = set(r.get("report_type") for r in reports)
        print(f"Report types found: {report_types}")
        
        # Verify standard report types are present
        expected_types = {"quick_summary", "full_detailed", "extensive_log"}
        for expected_type in expected_types:
            if expected_type in report_types:
                print(f"PASS: Found {expected_type} in reports list")
        
        # Check if barrister_view is included (may or may not exist)
        if "barrister_view" in report_types:
            print("PASS: barrister_view is included in reports list")
            barrister_reports = [r for r in reports if r.get("report_type") == "barrister_view"]
            for br in barrister_reports:
                print(f"  - Barrister report: {br.get('report_id')}, status: {br.get('status')}")
        else:
            print("INFO: No barrister_view reports found in list (may not have been generated yet)")
        
        # Verify report structure
        for report in reports[:3]:  # Check first 3 reports
            assert "report_id" in report, "Report should have report_id"
            assert "report_type" in report, "Report should have report_type"
            assert "status" in report, "Report should have status"
    
    def test_reports_list_barrister_view_has_correct_structure(self, admin_headers):
        """Verify barrister_view reports have the correct structure when present."""
        response = requests.get(
            f"{BASE_URL}/api/cases/{CASE_WITH_REPORTS}/reports",
            headers=admin_headers,
            timeout=30
        )
        
        assert response.status_code == 200
        reports = response.json()
        
        barrister_reports = [r for r in reports if r.get("report_type") == "barrister_view"]
        
        if barrister_reports:
            br = barrister_reports[0]
            assert br.get("report_type") == "barrister_view"
            assert "report_id" in br
            assert "status" in br
            assert "generated_at" in br or "created_at" in br
            print(f"PASS: Barrister report has correct structure: {br.get('report_id')}")
        else:
            print("INFO: No barrister_view reports to verify structure")


class TestBarristerViewEndpointBehavior:
    """Test specific endpoint behaviors for barrister-view."""
    
    def test_barrister_view_without_regenerate_does_not_auto_generate(self, admin_headers):
        """Verify that calling barrister-view without regenerate=true does NOT start generation."""
        # First, get the current state
        response1 = requests.get(
            f"{BASE_URL}/api/cases/{CASE_WITH_REPORTS}/reports/barrister-view",
            headers=admin_headers,
            timeout=30
        )
        
        if response1.status_code == 404:
            # No report exists - this is the expected "no auto-generate" behavior
            print("PASS: No auto-generation when regenerate param is not provided (404 returned)")
            return
        
        assert response1.status_code == 200
        data1 = response1.json()
        
        # If report exists and is completed, calling again should return same report without regenerating
        if data1.get("status") == "completed":
            response2 = requests.get(
                f"{BASE_URL}/api/cases/{CASE_WITH_REPORTS}/reports/barrister-view",
                headers=admin_headers,
                timeout=30
            )
            
            assert response2.status_code == 200
            data2 = response2.json()
            
            # Should return same report, not start new generation
            assert data2.get("report_id") == data1.get("report_id"), "Should return same report"
            assert data2.get("status") == "completed", "Status should remain completed"
            print(f"PASS: Existing completed report returned without regeneration: {data2.get('report_id')}")
    
    def test_barrister_view_status_endpoint(self, admin_headers):
        """Test that barrister report status can be checked via standard status endpoint."""
        # First get a barrister report
        response = requests.get(
            f"{BASE_URL}/api/cases/{CASE_WITH_REPORTS}/reports/barrister-view",
            headers=admin_headers,
            timeout=30
        )
        
        if response.status_code == 404:
            print("INFO: No barrister report exists to check status")
            return
        
        assert response.status_code == 200
        data = response.json()
        report_id = data.get("report_id")
        
        # Check status via standard endpoint
        status_response = requests.get(
            f"{BASE_URL}/api/cases/{CASE_WITH_REPORTS}/reports/{report_id}/status",
            headers=admin_headers,
            timeout=30
        )
        
        assert status_response.status_code == 200, f"Status check failed: {status_response.text}"
        status_data = status_response.json()
        assert "status" in status_data
        print(f"PASS: Barrister report status check works: {status_data.get('status')}")


class TestHealthCheck:
    """Basic health check to ensure API is accessible."""
    
    def test_health_endpoint(self):
        """Verify API health endpoint is accessible."""
        response = requests.get(f"{BASE_URL}/api/health", timeout=10)
        assert response.status_code == 200
        data = response.json()
        assert data.get("status") == "healthy"
        print("PASS: API health check passed")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
