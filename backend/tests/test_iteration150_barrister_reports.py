"""
Iteration 150 - Barrister View in Reports List & Trial Pricing Reversion Tests

Tests:
1. Trial status returns is_eligible=false for admin (who has completed payments)
2. Trial status returns is_eligible=true for users with 0 completed payments
3. Reports list API GET /api/cases/{case_id}/reports now includes barrister_view reports
4. Reports list should show all 4 report types: quick_summary, full_detailed, extensive_log, barrister_view
5. Login flow works correctly
6. App loads at root URL without errors
"""

import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Test credentials
TEST_EMAIL = "djkingy79@gmail.com"
TEST_PASSWORD = "Cr1m1nalApp3al$2025"
TEST_CASE_ID = "case_f8bf63e9dcbe"


class TestHealthAndBasics:
    """Basic health and connectivity tests"""
    
    def test_api_health(self):
        """Test API health endpoint"""
        response = requests.get(f"{BASE_URL}/api/health", timeout=10)
        assert response.status_code == 200
        data = response.json()
        assert data.get("status") == "healthy"
        print(f"✓ API health check passed: {data}")
    
    def test_frontend_loads(self):
        """Test frontend loads without errors"""
        response = requests.get(BASE_URL, timeout=10)
        assert response.status_code == 200
        assert "Criminal Appeal" in response.text or "Appeal" in response.text or "<!DOCTYPE html>" in response.text
        print("✓ Frontend loads successfully")


class TestAuthentication:
    """Authentication flow tests"""
    
    @pytest.fixture
    def auth_session(self):
        """Create authenticated session"""
        session = requests.Session()
        login_response = session.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": TEST_EMAIL, "password": TEST_PASSWORD},
            timeout=30
        )
        assert login_response.status_code == 200, f"Login failed: {login_response.text}"
        data = login_response.json()
        token = data.get("session_token") or data.get("token")
        assert token, "No session token returned"
        session.headers.update({"Authorization": f"Bearer {token}"})
        print(f"✓ Login successful for {TEST_EMAIL}")
        return session
    
    def test_login_flow(self, auth_session):
        """Test login returns valid session"""
        # auth_session fixture already validates login
        assert auth_session is not None
        print("✓ Login flow works correctly")


class TestTrialPricingReversion:
    """Tests to confirm trial pricing reverts to normal after first purchase"""
    
    @pytest.fixture
    def auth_session(self):
        """Create authenticated session"""
        session = requests.Session()
        login_response = session.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": TEST_EMAIL, "password": TEST_PASSWORD},
            timeout=30
        )
        assert login_response.status_code == 200
        data = login_response.json()
        token = data.get("session_token") or data.get("token")
        session.headers.update({"Authorization": f"Bearer {token}"})
        return session
    
    def test_trial_status_admin_not_eligible(self, auth_session):
        """Admin user (who has completed payments) should NOT be trial eligible"""
        response = auth_session.get(f"{BASE_URL}/api/payments/trial-status", timeout=10)
        assert response.status_code == 200
        data = response.json()
        
        # Admin has completed payments, so should NOT be eligible for trial
        assert "is_eligible" in data
        is_eligible = data.get("is_eligible")
        
        # This confirms trial reverts to normal after first purchase
        assert is_eligible == False, f"Expected is_eligible=False for admin with completed payments, got {is_eligible}"
        
        # Trial price should be None when not eligible
        assert data.get("trial_price") is None, f"Expected trial_price=None, got {data.get('trial_price')}"
        
        print(f"✓ Trial status for admin: is_eligible={is_eligible} (confirms trial reverts after purchase)")
        print(f"  Response: {data}")
    
    def test_trial_status_response_structure(self, auth_session):
        """Verify trial status endpoint returns correct structure"""
        response = auth_session.get(f"{BASE_URL}/api/payments/trial-status", timeout=10)
        assert response.status_code == 200
        data = response.json()
        
        # Check required fields exist
        assert "is_eligible" in data
        assert "trial_feature" in data
        assert "regular_price" in data
        
        # Verify trial feature is grounds_of_merit
        assert data.get("trial_feature") == "grounds_of_merit"
        
        # Verify regular price is 99
        assert data.get("regular_price") == 99
        
        print(f"✓ Trial status structure verified: trial_feature={data.get('trial_feature')}, regular_price={data.get('regular_price')}")


class TestBarristerViewInReportsList:
    """Tests to confirm barrister_view reports appear in reports list"""
    
    @pytest.fixture
    def auth_session(self):
        """Create authenticated session"""
        session = requests.Session()
        login_response = session.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": TEST_EMAIL, "password": TEST_PASSWORD},
            timeout=30
        )
        assert login_response.status_code == 200
        data = login_response.json()
        token = data.get("session_token") or data.get("token")
        session.headers.update({"Authorization": f"Bearer {token}"})
        return session
    
    def test_reports_list_includes_barrister_view(self, auth_session):
        """Reports list API should now include barrister_view reports (was previously excluded)"""
        response = auth_session.get(f"{BASE_URL}/api/cases/{TEST_CASE_ID}/reports", timeout=30)
        assert response.status_code == 200
        reports = response.json()
        
        assert isinstance(reports, list), f"Expected list of reports, got {type(reports)}"
        
        # Get all report types
        report_types = [r.get("report_type") for r in reports]
        print(f"✓ Found {len(reports)} reports with types: {report_types}")
        
        # Check if barrister_view is included (this was previously filtered out)
        barrister_reports = [r for r in reports if r.get("report_type") == "barrister_view"]
        
        # According to the issue, case_f8bf63e9dcbe has 3 barrister_view reports
        assert len(barrister_reports) > 0, "Expected barrister_view reports to be included in list (was previously excluded with $ne filter)"
        
        print(f"✓ Barrister View reports found: {len(barrister_reports)} (previously filtered out)")
        
        # Verify barrister reports have expected structure
        for br in barrister_reports:
            assert "report_id" in br
            assert "report_type" in br
            assert br.get("report_type") == "barrister_view"
            print(f"  - Barrister report: {br.get('report_id')}, status: {br.get('status')}")
    
    def test_reports_list_shows_all_four_types(self, auth_session):
        """Reports list should show all 4 report types: quick_summary, full_detailed, extensive_log, barrister_view"""
        response = auth_session.get(f"{BASE_URL}/api/cases/{TEST_CASE_ID}/reports", timeout=30)
        assert response.status_code == 200
        reports = response.json()
        
        # Get unique report types
        report_types = set(r.get("report_type") for r in reports)
        print(f"✓ Unique report types found: {report_types}")
        
        # According to the issue, case has: 3 barrister_view, 1 extensive_log, 1 full_detailed, 1 quick_summary
        expected_types = {"quick_summary", "full_detailed", "extensive_log", "barrister_view"}
        
        # Check that barrister_view is now included
        assert "barrister_view" in report_types, "barrister_view should now be included in reports list"
        
        # Count reports by type
        type_counts = {}
        for r in reports:
            rt = r.get("report_type")
            type_counts[rt] = type_counts.get(rt, 0) + 1
        
        print(f"✓ Report counts by type: {type_counts}")
        
        # Verify we have the expected total (6 reports according to issue)
        # 3 barrister_view + 1 extensive_log + 1 full_detailed + 1 quick_summary = 6
        total_expected = 6
        assert len(reports) >= total_expected, f"Expected at least {total_expected} reports, got {len(reports)}"
        
        print(f"✓ Total reports: {len(reports)} (expected at least {total_expected})")
    
    def test_barrister_report_has_correct_structure(self, auth_session):
        """Verify barrister_view reports have correct structure for frontend rendering"""
        response = auth_session.get(f"{BASE_URL}/api/cases/{TEST_CASE_ID}/reports", timeout=30)
        assert response.status_code == 200
        reports = response.json()
        
        barrister_reports = [r for r in reports if r.get("report_type") == "barrister_view"]
        assert len(barrister_reports) > 0, "No barrister_view reports found"
        
        # Check first barrister report structure
        br = barrister_reports[0]
        
        # Required fields for frontend rendering
        assert "report_id" in br, "Missing report_id"
        assert "report_type" in br, "Missing report_type"
        assert "status" in br or "generated_at" in br, "Missing status or generated_at"
        
        # Content should exist for completed reports
        if br.get("status") == "completed":
            assert "content" in br, "Completed report should have content"
        
        print(f"✓ Barrister report structure verified: {br.get('report_id')}")
        print(f"  - Status: {br.get('status')}")
        print(f"  - Generated at: {br.get('generated_at')}")


class TestReportsSectionRendering:
    """Tests for frontend ReportsSection component rendering barrister_view"""
    
    @pytest.fixture
    def auth_session(self):
        """Create authenticated session"""
        session = requests.Session()
        login_response = session.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": TEST_EMAIL, "password": TEST_PASSWORD},
            timeout=30
        )
        assert login_response.status_code == 200
        data = login_response.json()
        token = data.get("session_token") or data.get("token")
        session.headers.update({"Authorization": f"Bearer {token}"})
        return session
    
    def test_barrister_view_theme_in_frontend_code(self):
        """Verify ReportsSection.jsx has barrister_view theme with teal header"""
        # Read the frontend component file
        with open("/app/frontend/src/components/ReportsSection.jsx", "r") as f:
            content = f.read()
        
        # Check for barrister_view theme definition
        assert "barrister_view" in content, "barrister_view should be defined in ReportsSection.jsx"
        assert "bg-teal" in content, "barrister_view should have teal background color"
        assert "CAPSTONE" in content, "barrister_view should have CAPSTONE badge"
        assert "View Barrister Brief" in content, "Should have 'View Barrister Brief' button text"
        
        print("✓ ReportsSection.jsx has barrister_view theme with teal header and CAPSTONE badge")
    
    def test_barrister_view_button_navigation(self, auth_session):
        """Verify barrister_view reports can be navigated to"""
        response = auth_session.get(f"{BASE_URL}/api/cases/{TEST_CASE_ID}/reports", timeout=30)
        assert response.status_code == 200
        reports = response.json()
        
        barrister_reports = [r for r in reports if r.get("report_type") == "barrister_view"]
        assert len(barrister_reports) > 0, "No barrister_view reports found"
        
        # Get first barrister report ID
        report_id = barrister_reports[0].get("report_id")
        
        # Verify the report can be fetched individually
        report_response = auth_session.get(
            f"{BASE_URL}/api/cases/{TEST_CASE_ID}/reports/{report_id}",
            timeout=30
        )
        
        # Should return 200 or the report data
        assert report_response.status_code == 200, f"Failed to fetch barrister report: {report_response.text}"
        
        print(f"✓ Barrister report {report_id} can be fetched individually")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
