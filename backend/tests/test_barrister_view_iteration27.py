"""
Test Iteration 27: Barrister View and PDF Export Features
Tests:
- Backend: /api/cases/{case_id}/reports/{report_id}/export-pdf returns PDF
- Backend: /api/cases/{case_id}/reports/{report_id}/export-docx returns DOCX  
- Backend: /api/cases/{case_id}/reports returns reports with generated_at date
- Backend: /api/cases/{case_id}/grounds returns grounds data
"""
import pytest
import requests

BASE_URL = 'http://localhost:8001'

# Test credentials from previous iteration (iteration_26)
ADMIN_SESSION_TOKEN = "sFc-8brIFR8jJ1vVbc5ioTxkGjMV5gd92JhLnJfb9nQ"
TEST_CASE_ID = "case_cec9b5706fae"
TEST_REPORT_ID = "rpt_01e4334f84b9"


@pytest.fixture(scope="module")
def auth_session():
    """Get authenticated session with admin token"""
    session = requests.Session()
    session.headers.update({
        "Content-Type": "application/json",
        "Cookie": f"session_token={ADMIN_SESSION_TOKEN}"
    })
    return session


class TestReportExportPDF:
    """Test PDF export endpoint for reports"""
    
    def test_export_pdf_returns_pdf_content(self, auth_session):
        """Test that export-pdf returns valid PDF content starting with %PDF-"""
        response = auth_session.get(
            f"{BASE_URL}/api/cases/{TEST_CASE_ID}/reports/{TEST_REPORT_ID}/export-pdf",
            timeout=60
        )
        
        # Status code check
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text[:500] if response.status_code != 200 else ''}"
        
        # Content type should be PDF
        content_type = response.headers.get('Content-Type', '')
        assert 'pdf' in content_type.lower(), f"Expected PDF content type, got: {content_type}"
        
        # PDF content should start with %PDF-
        content = response.content
        assert content[:5] == b'%PDF-', f"PDF should start with %PDF-, got: {content[:20]}"
        
        # Should have reasonable size
        assert len(content) > 1000, f"PDF seems too small: {len(content)} bytes"
        
        print(f"SUCCESS: PDF export returned {len(content)} bytes of valid PDF content")
    
    def test_export_pdf_has_content_disposition(self, auth_session):
        """Test that PDF has proper Content-Disposition header for download"""
        response = auth_session.get(
            f"{BASE_URL}/api/cases/{TEST_CASE_ID}/reports/{TEST_REPORT_ID}/export-pdf",
            timeout=60
        )
        
        assert response.status_code == 200
        
        content_disp = response.headers.get('Content-Disposition', '')
        assert 'attachment' in content_disp.lower(), f"Expected attachment, got: {content_disp}"
        assert '.pdf' in content_disp.lower(), f"Expected .pdf in filename, got: {content_disp}"
        
        print(f"SUCCESS: Content-Disposition header correct: {content_disp}")


class TestReportExportDOCX:
    """Test DOCX export endpoint for reports"""
    
    def test_export_docx_returns_docx_content(self, auth_session):
        """Test that export-docx returns valid DOCX content"""
        response = auth_session.get(
            f"{BASE_URL}/api/cases/{TEST_CASE_ID}/reports/{TEST_REPORT_ID}/export-docx",
            timeout=60
        )
        
        # Status code check
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text[:500] if response.status_code != 200 else ''}"
        
        # Content type should be DOCX
        content_type = response.headers.get('Content-Type', '')
        expected_ct = 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
        assert expected_ct in content_type or 'docx' in content_type.lower(), f"Expected DOCX content type, got: {content_type}"
        
        # DOCX is a ZIP file, starts with PK
        content = response.content
        assert content[:2] == b'PK', f"DOCX (ZIP) should start with PK, got: {content[:20]}"
        
        # Should have reasonable size
        assert len(content) > 1000, f"DOCX seems too small: {len(content)} bytes"
        
        print(f"SUCCESS: DOCX export returned {len(content)} bytes of valid DOCX content")
    
    def test_export_docx_has_content_disposition(self, auth_session):
        """Test that DOCX has proper Content-Disposition header for download"""
        response = auth_session.get(
            f"{BASE_URL}/api/cases/{TEST_CASE_ID}/reports/{TEST_REPORT_ID}/export-docx",
            timeout=60
        )
        
        assert response.status_code == 200
        
        content_disp = response.headers.get('Content-Disposition', '')
        assert 'attachment' in content_disp.lower(), f"Expected attachment, got: {content_disp}"
        assert '.docx' in content_disp.lower(), f"Expected .docx in filename, got: {content_disp}"
        
        print(f"SUCCESS: Content-Disposition header correct: {content_disp}")


class TestReportsListWithDate:
    """Test reports list includes generated_at date"""
    
    def test_reports_have_generated_at_date(self, auth_session):
        """Test that reports list includes generated_at field with valid date"""
        response = auth_session.get(
            f"{BASE_URL}/api/cases/{TEST_CASE_ID}/reports",
            timeout=30
        )
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        reports = response.json()
        assert len(reports) > 0, "Expected at least one report"
        
        # Check each report has generated_at
        for report in reports:
            assert 'generated_at' in report or 'created_at' in report, f"Report missing date field: {report.keys()}"
            date_field = report.get('generated_at') or report.get('created_at')
            assert date_field is not None, "Date field is None"
            assert len(str(date_field)) > 10, f"Date seems invalid: {date_field}"
            print(f"Report {report.get('report_id')}: date = {date_field}")
        
        print(f"SUCCESS: All {len(reports)} reports have valid date fields")


class TestGroundsEndpoint:
    """Test grounds endpoint returns proper data for Barrister View"""
    
    def test_get_grounds_returns_grounds_array(self, auth_session):
        """Test that grounds endpoint returns grounds in proper structure"""
        response = auth_session.get(
            f"{BASE_URL}/api/cases/{TEST_CASE_ID}/grounds",
            timeout=30
        )
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        # Response should have 'grounds' key or be an array
        if isinstance(data, dict):
            grounds = data.get('grounds', [])
        else:
            grounds = data
        
        # Verify structure
        assert isinstance(grounds, list), f"Expected list of grounds, got {type(grounds)}"
        
        if len(grounds) > 0:
            ground = grounds[0]
            # Check required fields for Barrister View
            assert 'ground_id' in ground, "Ground missing ground_id"
            assert 'title' in ground, "Ground missing title"
            assert 'ground_type' in ground, "Ground missing ground_type"
            assert 'description' in ground, "Ground missing description"
            assert 'strength' in ground, "Ground missing strength"
            
            print(f"SUCCESS: Grounds endpoint returned {len(grounds)} grounds with proper structure")
            print(f"First ground: {ground.get('title')} ({ground.get('strength')})")
        else:
            print("INFO: No grounds found for this case - not a failure, just empty")


class TestSingleReportEndpoint:
    """Test single report endpoint for Barrister View"""
    
    def test_get_single_report(self, auth_session):
        """Test that single report endpoint returns full report data"""
        response = auth_session.get(
            f"{BASE_URL}/api/cases/{TEST_CASE_ID}/reports/{TEST_REPORT_ID}",
            timeout=30
        )
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        report = response.json()
        
        # Check required fields
        assert 'report_id' in report, "Report missing report_id"
        assert 'report_type' in report, "Report missing report_type"
        assert 'content' in report, "Report missing content"
        assert 'generated_at' in report or 'created_at' in report, "Report missing date field"
        
        # Check content has analysis
        content = report.get('content', {})
        if isinstance(content, dict):
            assert 'analysis' in content, f"Report content missing analysis. Keys: {content.keys()}"
            print(f"SUCCESS: Report has analysis of {len(content.get('analysis', ''))} chars")
        
        print("SUCCESS: Single report endpoint returned valid data")


class TestCaseEndpoint:
    """Test case endpoint for Barrister View"""
    
    def test_get_case_returns_case_data(self, auth_session):
        """Test case endpoint returns required fields for Barrister View"""
        response = auth_session.get(
            f"{BASE_URL}/api/cases/{TEST_CASE_ID}",
            timeout=30
        )
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        case = response.json()
        
        # Check required fields for Barrister View
        assert 'case_id' in case, "Case missing case_id"
        assert 'title' in case, "Case missing title"
        assert 'defendant_name' in case, "Case missing defendant_name"
        
        print(f"SUCCESS: Case '{case.get('title')}' loaded for defendant {case.get('defendant_name')}")


# Run tests if executed directly
if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
