"""
Iteration 69 Tests - PayID Refresh, Round Bracket Note Stripping, Barrister View Parser
Tests for:
1. Backend health check
2. AdminDashboard: refresh-payments-btn data-testid exists (code verification)
3. AdminDashboard: fetchPendingPayments has error toast (code verification)
4. AdminDashboard: refreshingPayments loading state (code verification)
5. ReportView cleanAIContent: strips (Note: ...) round bracket patterns (code verification)
6. BarristerView cleanAIContent: strips (Note: ...) round bracket patterns (code verification)
7. BarristerView parseAnalysis: detects markdown headings ## Title (code verification)
8. BarristerView parseAnalysis: detects numbered all-caps headings (code verification)
9. BarristerView parseAnalysis: cleanTitle strips leading numbers (code verification)
10. BarristerView section filtering: threshold is 80 chars (code verification)
11. Frontend compiles without errors
12. CaseDetail print button on all tabs
13. CaseDetail print has iOS detection with iframe approach
"""

import pytest
import requests
import os
import re

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://grounds-analyzer.preview.emergentagent.com')

class TestBackendHealth:
    """Backend health check tests"""
    
    def test_health_endpoint(self):
        """Test that health endpoint returns healthy status"""
        response = requests.get(f"{BASE_URL}/api/health")
        assert response.status_code == 200
        data = response.json()
        assert data.get("status") == "healthy"
        assert data.get("database") == "connected"
        print(f"Health check passed: {data}")


class TestAdminDashboardCodeVerification:
    """Code verification tests for AdminDashboard.jsx"""
    
    @pytest.fixture(scope="class")
    def admin_dashboard_content(self):
        """Read AdminDashboard.jsx content"""
        with open("/app/frontend/src/pages/AdminDashboard.jsx", "r") as f:
            return f.read()
    
    def test_refresh_payments_btn_data_testid(self, admin_dashboard_content):
        """Verify refresh-payments-btn data-testid exists"""
        assert 'data-testid="refresh-payments-btn"' in admin_dashboard_content
        print("PASS: refresh-payments-btn data-testid found")
    
    def test_refreshing_payments_state(self, admin_dashboard_content):
        """Verify refreshingPayments state exists"""
        assert "const [refreshingPayments, setRefreshingPayments] = useState(false)" in admin_dashboard_content
        print("PASS: refreshingPayments state found")
    
    def test_fetch_pending_payments_error_toasts(self, admin_dashboard_content):
        """Verify fetchPendingPayments has error toasts (not silent fail)"""
        # Check for toast.error calls in fetchPendingPayments
        assert 'toast.error("Admin access required to view payments")' in admin_dashboard_content
        assert 'toast.error("Session expired — please log in again")' in admin_dashboard_content
        assert 'toast.error("Failed to fetch pending payments")' in admin_dashboard_content
        print("PASS: fetchPendingPayments has error toasts")
    
    def test_refresh_button_loading_state(self, admin_dashboard_content):
        """Verify refresh button shows loading state when refreshingPayments is true"""
        assert "disabled={refreshingPayments}" in admin_dashboard_content
        assert "{refreshingPayments ? (" in admin_dashboard_content
        assert "Refreshing..." in admin_dashboard_content
        print("PASS: Refresh button has loading state")


class TestReportViewCodeVerification:
    """Code verification tests for ReportView.jsx"""
    
    @pytest.fixture(scope="class")
    def report_view_content(self):
        """Read ReportView.jsx content"""
        with open("/app/frontend/src/pages/ReportView.jsx", "r") as f:
            return f.read()
    
    def test_clean_ai_content_round_bracket_note(self, report_view_content):
        """Verify cleanAIContent strips (Note: ...) round bracket patterns"""
        assert r'cleaned.replace(/\(Note:\s*[^)]*\)/gi, "")' in report_view_content
        print("PASS: ReportView cleanAIContent strips (Note: ...) patterns")
    
    def test_clean_ai_content_link_formatting(self, report_view_content):
        """Verify cleanAIContent strips (Link formatting...) patterns"""
        assert r'cleaned.replace(/\(Link formatting[^)]*\)/gi, "")' in report_view_content
        print("PASS: ReportView cleanAIContent strips (Link formatting...) patterns")
    
    def test_clean_ai_content_entries_will(self, report_view_content):
        """Verify cleanAIContent strips (Entries will...) patterns"""
        assert r'cleaned.replace(/\(Entries will[^)]*\)/gi, "")' in report_view_content
        print("PASS: ReportView cleanAIContent strips (Entries will...) patterns")
    
    def test_section_filtering_threshold_80(self, report_view_content):
        """Verify section filtering threshold is 80 chars"""
        assert "content.length < 80" in report_view_content
        print("PASS: ReportView section filtering threshold is 80 chars")


class TestBarristerViewCodeVerification:
    """Code verification tests for BarristerView.jsx"""
    
    @pytest.fixture(scope="class")
    def barrister_view_content(self):
        """Read BarristerView.jsx content"""
        with open("/app/frontend/src/pages/BarristerView.jsx", "r") as f:
            return f.read()
    
    def test_clean_ai_content_round_bracket_note(self, barrister_view_content):
        """Verify cleanAIContent strips (Note: ...) round bracket patterns"""
        assert r'cleaned.replace(/\(Note:\s*[^)]*\)/gi, "")' in barrister_view_content
        print("PASS: BarristerView cleanAIContent strips (Note: ...) patterns")
    
    def test_clean_ai_content_link_formatting(self, barrister_view_content):
        """Verify cleanAIContent strips (Link formatting...) patterns"""
        assert r'cleaned.replace(/\(Link formatting[^)]*\)/gi, "")' in barrister_view_content
        print("PASS: BarristerView cleanAIContent strips (Link formatting...) patterns")
    
    def test_clean_ai_content_entries_will(self, barrister_view_content):
        """Verify cleanAIContent strips (Entries will...) patterns"""
        assert r'cleaned.replace(/\(Entries will[^)]*\)/gi, "")' in barrister_view_content
        print("PASS: BarristerView cleanAIContent strips (Entries will...) patterns")
    
    def test_parse_analysis_markdown_heading_detection(self, barrister_view_content):
        """Verify parseAnalysis detects markdown headings ## Title"""
        # Check for markdown heading pattern in sectionPatterns
        assert r'/^#{1,3}\s+(?:\d+\.\s*)?(.{4,70})$/i' in barrister_view_content
        print("PASS: BarristerView parseAnalysis detects markdown headings")
    
    def test_parse_analysis_numbered_allcaps_heading(self, barrister_view_content):
        """Verify parseAnalysis detects numbered all-caps headings (5. COMPARATIVE SENTENCING TABLE)"""
        # Check for numbered all-caps heading pattern
        assert r'/^\d+\.\s+([A-Z][A-Z\s\-&()]{3,70})(?:\s*\(MANDATORY\))?$/i' in barrister_view_content
        print("PASS: BarristerView parseAnalysis detects numbered all-caps headings")
    
    def test_clean_title_helper(self, barrister_view_content):
        """Verify cleanTitle helper strips leading numbers from section titles"""
        # Check for cleanTitle function that strips leading numbers
        assert 'const cleanTitle = (raw) =>' in barrister_view_content
        assert r'.replace(/^\d+\.\s*/, "")' in barrister_view_content
        print("PASS: BarristerView cleanTitle strips leading numbers")
    
    def test_section_filtering_threshold_80(self, barrister_view_content):
        """Verify section filtering threshold is 80 chars"""
        assert "cleanedContent.length >= 80" in barrister_view_content
        print("PASS: BarristerView section filtering threshold is 80 chars")


class TestCaseDetailCodeVerification:
    """Code verification tests for CaseDetail.jsx"""
    
    @pytest.fixture(scope="class")
    def case_detail_content(self):
        """Read CaseDetail.jsx content"""
        with open("/app/frontend/src/pages/CaseDetail.jsx", "r") as f:
            return f.read()
    
    def test_print_button_all_tabs(self, case_detail_content):
        """Verify print button exists for all tabs with dynamic data-testid"""
        assert 'data-testid={`print-${activeTab}-btn`}' in case_detail_content
        print("PASS: CaseDetail has print button with dynamic data-testid for all tabs")
    
    def test_ios_detection_for_print(self, case_detail_content):
        """Verify iOS detection for print functionality"""
        assert r"/iPad|iPhone|iPod/.test(navigator.userAgent)" in case_detail_content
        print("PASS: CaseDetail has iOS detection for print")
    
    def test_ios_iframe_approach(self, case_detail_content):
        """Verify iOS uses iframe approach for printing"""
        assert "const iframe = document.createElement('iframe')" in case_detail_content
        assert "iframe.contentWindow.print()" in case_detail_content
        print("PASS: CaseDetail uses iframe approach for iOS printing")
    
    def test_data_tab_content_attribute(self, case_detail_content):
        """Verify TabsContent elements have data-tab-content attribute"""
        # Count occurrences of data-tab-content
        count = case_detail_content.count("data-tab-content")
        assert count >= 7, f"Expected at least 7 data-tab-content attributes, found {count}"
        print(f"PASS: Found {count} data-tab-content attributes")


class TestFrontendBuild:
    """Frontend build verification"""
    
    def test_frontend_compiles(self):
        """Verify frontend compiles without errors"""
        import subprocess
        result = subprocess.run(
            ["yarn", "build"],
            cwd="/app/frontend",
            capture_output=True,
            text=True,
            timeout=120
        )
        assert result.returncode == 0, f"Frontend build failed: {result.stderr}"
        print("PASS: Frontend compiles without errors")


class TestLoginAPI:
    """Login API tests"""
    
    def test_login_with_valid_credentials(self):
        """Test login with valid test credentials"""
        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={
                "email": "edittest2@example.com",
                "password": "TestPass123!"
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert "user_id" in data
        assert data.get("email") == "edittest2@example.com"
        print(f"PASS: Login successful for {data.get('email')}")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
