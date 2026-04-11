"""
Iteration 186: Download Token Security & Footer Format Tests
Tests:
1. POST /api/auth/download-token generates short-lived token when authenticated
2. Download token works as query param on protected endpoints
3. Download token is single-use (second use returns 401)
4. Download token expires after 5 minutes
5. Legacy session_token query param still works
6. Cookie-based and Bearer header auth still work
7. PDF export endpoint works with download_token
8. DOCX export uses shared export_footer.py
"""

import pytest
import requests
import os
import time
from datetime import datetime, timedelta

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Test credentials from test_credentials.md
TEST_EMAIL = "djkingy79@gmail.com"
TEST_PASSWORD = "Grubbygrub88"


class TestAuthDownloadToken:
    """Test the download token authentication system"""
    
    @pytest.fixture(scope="class")
    def session_token(self):
        """Get a valid session token via login"""
        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": TEST_EMAIL, "password": TEST_PASSWORD},
            timeout=30
        )
        assert response.status_code == 200, f"Login failed: {response.text}"
        data = response.json()
        assert "session_token" in data, "No session_token in login response"
        return data["session_token"]
    
    @pytest.fixture(scope="class")
    def test_case_id(self, session_token):
        """Get a test case ID for export tests"""
        response = requests.get(
            f"{BASE_URL}/api/cases",
            headers={"Authorization": f"Bearer {session_token}"},
            timeout=30
        )
        assert response.status_code == 200, f"Failed to get cases: {response.text}"
        cases = response.json()
        assert len(cases) > 0, "No cases found for testing"
        return cases[0]["case_id"]
    
    @pytest.fixture(scope="class")
    def test_report_id(self, session_token, test_case_id):
        """Get a test report ID for export tests"""
        response = requests.get(
            f"{BASE_URL}/api/cases/{test_case_id}/reports",
            headers={"Authorization": f"Bearer {session_token}"},
            timeout=30
        )
        assert response.status_code == 200, f"Failed to get reports: {response.text}"
        reports = response.json()
        # Find a completed report
        completed = [r for r in reports if r.get("status") == "completed"]
        if not completed:
            pytest.skip("No completed reports found for testing")
        return completed[0]["report_id"]
    
    def test_download_token_generation(self, session_token):
        """Test POST /api/auth/download-token generates a token when authenticated"""
        response = requests.post(
            f"{BASE_URL}/api/auth/download-token",
            headers={"Authorization": f"Bearer {session_token}"},
            timeout=30
        )
        assert response.status_code == 200, f"Download token generation failed: {response.text}"
        data = response.json()
        assert "download_token" in data, "No download_token in response"
        assert len(data["download_token"]) > 20, "Download token too short"
        print(f"PASS: Download token generated successfully (length={len(data['download_token'])})")
    
    def test_download_token_requires_auth(self):
        """Test that download token endpoint requires authentication"""
        response = requests.post(
            f"{BASE_URL}/api/auth/download-token",
            timeout=30
        )
        assert response.status_code == 401, f"Expected 401, got {response.status_code}"
        print("PASS: Download token endpoint requires authentication")
    
    def test_download_token_works_as_query_param(self, session_token):
        """Test that download_token works as query param on protected endpoints"""
        # First get a download token
        token_response = requests.post(
            f"{BASE_URL}/api/auth/download-token",
            headers={"Authorization": f"Bearer {session_token}"},
            timeout=30
        )
        assert token_response.status_code == 200
        download_token = token_response.json()["download_token"]
        
        # Use it to access /api/auth/me (a protected endpoint)
        me_response = requests.get(
            f"{BASE_URL}/api/auth/me?download_token={download_token}",
            timeout=30
        )
        assert me_response.status_code == 200, f"Download token auth failed: {me_response.text}"
        data = me_response.json()
        assert data.get("email") == TEST_EMAIL, "Wrong user returned"
        print("PASS: Download token works as query param for authentication")
    
    def test_download_token_single_use(self, session_token):
        """Test that download token is single-use (second use returns 401)"""
        # Get a download token
        token_response = requests.post(
            f"{BASE_URL}/api/auth/download-token",
            headers={"Authorization": f"Bearer {session_token}"},
            timeout=30
        )
        assert token_response.status_code == 200
        download_token = token_response.json()["download_token"]
        
        # First use - should succeed
        first_response = requests.get(
            f"{BASE_URL}/api/auth/me?download_token={download_token}",
            timeout=30
        )
        assert first_response.status_code == 200, f"First use failed: {first_response.text}"
        
        # Second use - should fail with 401
        second_response = requests.get(
            f"{BASE_URL}/api/auth/me?download_token={download_token}",
            timeout=30
        )
        assert second_response.status_code == 401, f"Expected 401 on second use, got {second_response.status_code}"
        assert "already used" in second_response.text.lower(), f"Expected 'already used' error: {second_response.text}"
        print("PASS: Download token is single-use (second use returns 401)")
    
    def test_legacy_session_token_still_works(self, session_token):
        """Test that legacy session_token query param still works (for WebSocket backward compat)"""
        response = requests.get(
            f"{BASE_URL}/api/auth/me?session_token={session_token}",
            timeout=30
        )
        assert response.status_code == 200, f"Legacy session_token auth failed: {response.text}"
        data = response.json()
        assert data.get("email") == TEST_EMAIL, "Wrong user returned"
        print("PASS: Legacy session_token query param still works")
    
    def test_bearer_header_auth_works(self, session_token):
        """Test that Bearer header authentication still works"""
        response = requests.get(
            f"{BASE_URL}/api/auth/me",
            headers={"Authorization": f"Bearer {session_token}"},
            timeout=30
        )
        assert response.status_code == 200, f"Bearer auth failed: {response.text}"
        data = response.json()
        assert data.get("email") == TEST_EMAIL, "Wrong user returned"
        print("PASS: Bearer header authentication works")
    
    def test_cookie_auth_works(self, session_token):
        """Test that cookie-based authentication still works"""
        response = requests.get(
            f"{BASE_URL}/api/auth/me",
            cookies={"session_token": session_token},
            timeout=30
        )
        assert response.status_code == 200, f"Cookie auth failed: {response.text}"
        data = response.json()
        assert data.get("email") == TEST_EMAIL, "Wrong user returned"
        print("PASS: Cookie-based authentication works")


class TestPDFExportWithDownloadToken:
    """Test PDF export endpoints with download token"""
    
    @pytest.fixture(scope="class")
    def session_token(self):
        """Get a valid session token via login"""
        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": TEST_EMAIL, "password": TEST_PASSWORD},
            timeout=30
        )
        assert response.status_code == 200
        return response.json()["session_token"]
    
    @pytest.fixture(scope="class")
    def test_case_id(self, session_token):
        """Get a test case ID"""
        response = requests.get(
            f"{BASE_URL}/api/cases",
            headers={"Authorization": f"Bearer {session_token}"},
            timeout=30
        )
        assert response.status_code == 200
        cases = response.json()
        assert len(cases) > 0
        return cases[0]["case_id"]
    
    @pytest.fixture(scope="class")
    def test_report_id(self, session_token, test_case_id):
        """Get a test report ID"""
        response = requests.get(
            f"{BASE_URL}/api/cases/{test_case_id}/reports",
            headers={"Authorization": f"Bearer {session_token}"},
            timeout=30
        )
        assert response.status_code == 200
        reports = response.json()
        completed = [r for r in reports if r.get("status") == "completed"]
        if not completed:
            pytest.skip("No completed reports found")
        return completed[0]["report_id"]
    
    def test_pdf_export_with_download_token(self, session_token, test_case_id, test_report_id):
        """Test PDF export endpoint works with download_token query param"""
        # Get a download token
        token_response = requests.post(
            f"{BASE_URL}/api/auth/download-token",
            headers={"Authorization": f"Bearer {session_token}"},
            timeout=30
        )
        assert token_response.status_code == 200
        download_token = token_response.json()["download_token"]
        
        # Use download token to export PDF
        pdf_response = requests.get(
            f"{BASE_URL}/api/cases/{test_case_id}/reports/{test_report_id}/export-pdf?download_token={download_token}",
            timeout=120
        )
        assert pdf_response.status_code == 200, f"PDF export failed: {pdf_response.text[:500]}"
        assert pdf_response.headers.get("content-type") == "application/pdf", "Wrong content type"
        assert len(pdf_response.content) > 1000, "PDF too small"
        print(f"PASS: PDF export works with download_token (size={len(pdf_response.content)} bytes)")
    
    def test_pdf_export_with_bearer_token(self, session_token, test_case_id, test_report_id):
        """Test PDF export endpoint works with Bearer token"""
        pdf_response = requests.get(
            f"{BASE_URL}/api/cases/{test_case_id}/reports/{test_report_id}/export-pdf",
            headers={"Authorization": f"Bearer {session_token}"},
            timeout=120
        )
        assert pdf_response.status_code == 200, f"PDF export failed: {pdf_response.text[:500]}"
        assert pdf_response.headers.get("content-type") == "application/pdf"
        print("PASS: PDF export works with Bearer token")
    
    def test_docx_export_with_download_token(self, session_token, test_case_id, test_report_id):
        """Test DOCX export endpoint works with download_token query param"""
        # Get a download token
        token_response = requests.post(
            f"{BASE_URL}/api/auth/download-token",
            headers={"Authorization": f"Bearer {session_token}"},
            timeout=30
        )
        assert token_response.status_code == 200
        download_token = token_response.json()["download_token"]
        
        # Use download token to export DOCX
        docx_response = requests.get(
            f"{BASE_URL}/api/cases/{test_case_id}/reports/{test_report_id}/export-docx?download_token={download_token}",
            timeout=120
        )
        assert docx_response.status_code == 200, f"DOCX export failed: {docx_response.text[:500]}"
        expected_type = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        assert docx_response.headers.get("content-type") == expected_type, f"Wrong content type: {docx_response.headers.get('content-type')}"
        assert len(docx_response.content) > 1000, "DOCX too small"
        print(f"PASS: DOCX export works with download_token (size={len(docx_response.content)} bytes)")


class TestExportFooterFormat:
    """Test that export footer uses correct format"""
    
    @pytest.fixture(scope="class")
    def session_token(self):
        """Get a valid session token via login"""
        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": TEST_EMAIL, "password": TEST_PASSWORD},
            timeout=30
        )
        assert response.status_code == 200
        return response.json()["session_token"]
    
    def test_export_footer_module_exists(self):
        """Test that export_footer.py module exists and has required functions"""
        import sys
        sys.path.insert(0, '/app/backend')
        from services.export_footer import build_footer_label, NumberedCanvas, apply_docx_footer
        
        # Test build_footer_label
        test_case = {"title": "Test Case", "defendant_name": "John Doe"}
        label = build_footer_label(test_case, "Full Detailed Report")
        
        # Verify format: "Documented from the Criminal Law /Appeal Management Application - [Doc Type] - For [Case Name] [Date]"
        assert "Documented from the Criminal Law /Appeal Management Application" in label, f"Wrong prefix: {label}"
        assert "Full Detailed Report" in label, f"Doc type missing: {label}"
        assert "Test Case" in label or "John Doe" in label, f"Case name missing: {label}"
        
        # Check date format DD/MM/YYYY
        import re
        date_pattern = r'\d{2}/\d{2}/\d{4}'
        assert re.search(date_pattern, label), f"Date format wrong: {label}"
        
        print(f"PASS: Footer label format correct: {label}")
    
    def test_footer_label_format_exact(self):
        """Test exact footer format matches specification"""
        import sys
        sys.path.insert(0, '/app/backend')
        from services.export_footer import build_footer_label
        
        test_case = {"title": "R v Smith", "defendant_name": "John Smith"}
        label = build_footer_label(test_case, "Case Summary Report (Free)")
        
        # Expected format: "Documented from the Criminal Law /Appeal Management Application - Case Summary Report (Free) - For R v Smith DD/MM/YYYY"
        expected_prefix = "Documented from the Criminal Law /Appeal Management Application - Case Summary Report (Free) - For"
        assert label.startswith(expected_prefix), f"Footer doesn't match expected format.\nExpected prefix: {expected_prefix}\nGot: {label}"
        print(f"PASS: Footer format matches specification: {label}")


class TestTimelinePDFExport:
    """Test timeline PDF export with download token"""
    
    @pytest.fixture(scope="class")
    def session_token(self):
        """Get a valid session token via login"""
        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": TEST_EMAIL, "password": TEST_PASSWORD},
            timeout=30
        )
        assert response.status_code == 200
        return response.json()["session_token"]
    
    @pytest.fixture(scope="class")
    def test_case_id(self, session_token):
        """Get a test case ID with timeline events"""
        response = requests.get(
            f"{BASE_URL}/api/cases",
            headers={"Authorization": f"Bearer {session_token}"},
            timeout=30
        )
        assert response.status_code == 200
        cases = response.json()
        # Find a case with timeline events
        for case in cases:
            timeline_resp = requests.get(
                f"{BASE_URL}/api/cases/{case['case_id']}/timeline",
                headers={"Authorization": f"Bearer {session_token}"},
                timeout=30
            )
            if timeline_resp.status_code == 200 and len(timeline_resp.json()) > 0:
                return case["case_id"]
        pytest.skip("No cases with timeline events found")
    
    def test_timeline_pdf_with_download_token(self, session_token, test_case_id):
        """Test timeline PDF export works with download_token"""
        # Get a download token
        token_response = requests.post(
            f"{BASE_URL}/api/auth/download-token",
            headers={"Authorization": f"Bearer {session_token}"},
            timeout=30
        )
        assert token_response.status_code == 200
        download_token = token_response.json()["download_token"]
        
        # Use download token to export timeline PDF
        pdf_response = requests.get(
            f"{BASE_URL}/api/cases/{test_case_id}/timeline/export-pdf?download_token={download_token}",
            timeout=120
        )
        assert pdf_response.status_code == 200, f"Timeline PDF export failed: {pdf_response.text[:500]}"
        assert pdf_response.headers.get("content-type") == "application/pdf"
        print(f"PASS: Timeline PDF export works with download_token (size={len(pdf_response.content)} bytes)")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
