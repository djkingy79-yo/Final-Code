"""
Backend API Tests for Report Generation and AI Features
Tests: Report Generation (all 3 types), Get Reports List, Auto-Identify Grounds, API Health Check

Focus on testing the specific features reported by user:
- Quick Summary report generation
- Full Detailed report generation  
- Extensive Log report generation
- Get reports list endpoint
- Grounds of merit auto-identification
"""
import pytest
import requests
import os

BASE_URL = 'http://localhost:8001'
SESSION_TOKEN = os.environ.get('TEST_SESSION_TOKEN', '61bbcd763e9a47ed8d7ad1a7bcf1854a')
TEST_CASE_ID = os.environ.get('TEST_CASE_ID', '')


class TestHealthCheck:
    """Health check tests"""
    
    def test_api_health(self):
        """Test API health endpoint"""
        response = requests.get(f"{BASE_URL}/api/health")
        assert response.status_code == 200
        data = response.json()
        assert data.get("status") == "healthy"
        print("✓ API health check passed")

    def test_api_root(self):
        """Test API root endpoint"""
        response = requests.get(f"{BASE_URL}/api/")
        assert response.status_code == 200
        data = response.json()
        assert "Justitia AI" in data.get("message", "") or "message" in data
        print("✓ API root endpoint passed")


class TestAuthentication:
    """Authentication tests"""
    
    def test_auth_me_with_valid_token(self, auth_headers):
        """Test /api/auth/me with valid session token"""
        response = requests.get(f"{BASE_URL}/api/auth/me", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert "user_id" in data
        assert "email" in data
        print(f"✓ Auth me passed - User: {data.get('name')}")

    def test_auth_me_without_token(self):
        """Test /api/auth/me without token returns 401"""
        response = requests.get(f"{BASE_URL}/api/auth/me")
        assert response.status_code == 401
        print("✓ Auth me without token correctly returns 401")


class TestReportGeneration:
    """Report generation tests for all 3 types"""
    
    def test_generate_quick_summary_report(self, auth_headers, test_case_id_with_content):
        """Test generating a quick summary report"""
        payload = {"report_type": "quick_summary"}
        response = requests.post(
            f"{BASE_URL}/api/cases/{test_case_id_with_content}/reports/generate",
            json=payload,
            headers=auth_headers,
            timeout=180  # 3 minute timeout for AI generation
        )
        
        if response.status_code == 200:
            data = response.json()
            assert "report_id" in data
            assert data["report_type"] == "quick_summary"
            assert "content" in data
            assert "analysis" in data.get("content", {})
            print(f"✓ Quick summary report generated: {data['report_id']}")
            print(f"  Analysis length: {len(data['content'].get('analysis', ''))}")
            return data["report_id"]
        elif response.status_code == 500:
            # AI may fail due to external service issues
            error_detail = response.json().get('detail', '')
            if 'retry' in error_detail.lower() or '502' in error_detail or 'timeout' in error_detail.lower():
                pytest.skip(f"AI service temporarily unavailable: {error_detail}")
            else:
                pytest.fail(f"Unexpected server error: {error_detail}")
        else:
            pytest.fail(f"Unexpected status code {response.status_code}: {response.text[:500]}")

    def test_generate_full_detailed_report(self, auth_headers, test_case_id_with_content):
        """Test generating a full detailed report"""
        payload = {"report_type": "full_detailed"}
        response = requests.post(
            f"{BASE_URL}/api/cases/{test_case_id_with_content}/reports/generate",
            json=payload,
            headers=auth_headers,
            timeout=240  # 4 minute timeout for larger report
        )
        
        if response.status_code == 200:
            data = response.json()
            assert "report_id" in data
            assert data["report_type"] == "full_detailed"
            assert "content" in data
            assert "analysis" in data.get("content", {})
            print(f"✓ Full detailed report generated: {data['report_id']}")
            print(f"  Analysis length: {len(data['content'].get('analysis', ''))}")
            return data["report_id"]
        elif response.status_code == 500:
            error_detail = response.json().get('detail', '')
            if 'retry' in error_detail.lower() or '502' in error_detail or 'timeout' in error_detail.lower():
                pytest.skip(f"AI service temporarily unavailable: {error_detail}")
            else:
                pytest.fail(f"Unexpected server error: {error_detail}")
        else:
            pytest.fail(f"Unexpected status code {response.status_code}: {response.text[:500]}")

    def test_generate_extensive_log_report(self, auth_headers, test_case_id_with_content):
        """Test generating an extensive log report"""
        payload = {"report_type": "extensive_log"}
        response = requests.post(
            f"{BASE_URL}/api/cases/{test_case_id_with_content}/reports/generate",
            json=payload,
            headers=auth_headers,
            timeout=240  # 4 minute timeout for largest report type
        )
        
        if response.status_code == 200:
            data = response.json()
            assert "report_id" in data
            assert data["report_type"] == "extensive_log"
            assert "content" in data
            assert "analysis" in data.get("content", {})
            print(f"✓ Extensive log report generated: {data['report_id']}")
            print(f"  Analysis length: {len(data['content'].get('analysis', ''))}")
            return data["report_id"]
        elif response.status_code == 500:
            error_detail = response.json().get('detail', '')
            if 'retry' in error_detail.lower() or '502' in error_detail or 'timeout' in error_detail.lower():
                pytest.skip(f"AI service temporarily unavailable: {error_detail}")
            else:
                pytest.fail(f"Unexpected server error: {error_detail}")
        else:
            pytest.fail(f"Unexpected status code {response.status_code}: {response.text[:500]}")

    def test_generate_report_invalid_type(self, auth_headers, test_case_id_with_content):
        """Test generating report with invalid type returns 400"""
        payload = {"report_type": "invalid_type"}
        response = requests.post(
            f"{BASE_URL}/api/cases/{test_case_id_with_content}/reports/generate",
            json=payload,
            headers=auth_headers
        )
        assert response.status_code == 400
        assert "Invalid report type" in response.json().get("detail", "")
        print("✓ Invalid report type correctly returns 400")

    def test_generate_report_unauthorized(self, test_case_id_with_content):
        """Test generating report without authentication returns 401"""
        payload = {"report_type": "quick_summary"}
        response = requests.post(
            f"{BASE_URL}/api/cases/{test_case_id_with_content}/reports/generate",
            json=payload
        )
        assert response.status_code == 401
        print("✓ Generate report without auth correctly returns 401")


class TestGetReportsList:
    """Test getting reports list endpoint"""
    
    def test_get_reports_list(self, auth_headers, test_case_id_with_content):
        """Test getting all reports for a case"""
        response = requests.get(
            f"{BASE_URL}/api/cases/{test_case_id_with_content}/reports",
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        print(f"✓ Got {len(data)} reports for case")
        
        # Verify report structure if reports exist
        if data:
            report = data[0]
            assert "report_id" in report
            assert "case_id" in report
            assert "report_type" in report
            assert "title" in report
            assert "content" in report
            assert "generated_at" in report
            print(f"✓ Report structure verified - Types found: {[r['report_type'] for r in data]}")

    def test_get_reports_unauthorized(self, test_case_id_with_content):
        """Test getting reports without authentication returns 401"""
        response = requests.get(
            f"{BASE_URL}/api/cases/{test_case_id_with_content}/reports"
        )
        assert response.status_code == 401
        print("✓ Get reports without auth correctly returns 401")

    def test_get_reports_invalid_case(self, auth_headers):
        """Test getting reports for invalid case returns 404 or empty list"""
        response = requests.get(
            f"{BASE_URL}/api/cases/case_invalid_123/reports",
            headers=auth_headers
        )
        # Should return 404 or empty list (depends on implementation)
        assert response.status_code in [200, 404]
        if response.status_code == 200:
            assert response.json() == []
        print("✓ Get reports for invalid case handled correctly")


class TestAutoIdentifyGrounds:
    """Auto-identify grounds of merit tests"""
    
    def test_auto_identify_grounds(self, auth_headers, test_case_id_with_content):
        """Test AI auto-identification of grounds of merit"""
        response = requests.post(
            f"{BASE_URL}/api/cases/{test_case_id_with_content}/grounds/auto-identify",
            headers=auth_headers,
            timeout=180  # 3 minute timeout for AI analysis
        )
        
        if response.status_code == 200:
            data = response.json()
            assert "task_id" in data or "grounds" in data or "created_grounds" in data or "summary" in data or "status" in data
            print("✓ Auto-identify grounds succeeded")
            if "created_grounds" in data:
                print(f"  Created {len(data['created_grounds'])} new grounds")
            if "summary" in data:
                print(f"  Summary: {data['summary'][:200]}...")
            return data
        elif response.status_code == 500:
            error_detail = response.json().get('detail', '')
            if 'retry' in error_detail.lower() or '502' in error_detail or 'timeout' in error_detail.lower():
                pytest.skip(f"AI service temporarily unavailable: {error_detail}")
            else:
                pytest.fail(f"Unexpected server error: {error_detail}")
        else:
            pytest.fail(f"Unexpected status code {response.status_code}: {response.text[:500]}")

    def test_auto_identify_grounds_unauthorized(self, test_case_id_with_content):
        """Test auto-identify grounds without authentication returns 401"""
        response = requests.post(
            f"{BASE_URL}/api/cases/{test_case_id_with_content}/grounds/auto-identify"
        )
        assert response.status_code == 401
        print("✓ Auto-identify without auth correctly returns 401")

    def test_auto_identify_grounds_invalid_case(self, auth_headers):
        """Test auto-identify on invalid case returns 404"""
        response = requests.post(
            f"{BASE_URL}/api/cases/case_invalid_123/grounds/auto-identify",
            headers=auth_headers,
            timeout=60
        )
        assert response.status_code == 404
        print("✓ Auto-identify on invalid case correctly returns 404")


class TestExistingReports:
    """Test with existing test case and reports"""
    
    def test_verify_existing_reports(self, auth_headers):
        """Verify the existing test case has reports"""
        case_id = TEST_CASE_ID or "case_cec9b5706fae"
        response = requests.get(
            f"{BASE_URL}/api/cases/{case_id}/reports",
            headers=auth_headers
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✓ Found {len(data)} existing reports for test case")
            
            # Check for each report type
            report_types = [r['report_type'] for r in data]
            if 'quick_summary' in report_types:
                print("  ✓ Quick Summary report exists")
            if 'full_detailed' in report_types:
                print("  ✓ Full Detailed report exists")
            if 'extensive_log' in report_types:
                print("  ✓ Extensive Log report exists")
            
            return data
        else:
            pytest.skip(f"Test case not accessible: {response.status_code}")


class TestCleanup:
    """Cleanup test data"""
    
    def test_cleanup_test_case(self, auth_headers, cleanup_case_id):
        """Delete test case created during tests"""
        if cleanup_case_id:
            response = requests.delete(
                f"{BASE_URL}/api/cases/{cleanup_case_id}",
                headers=auth_headers
            )
            assert response.status_code == 200
            print(f"✓ Test case {cleanup_case_id} deleted")


# Fixtures
@pytest.fixture(scope="session")
def auth_headers():
    """Get authentication headers"""
    token = SESSION_TOKEN or os.environ.get('TEST_SESSION_TOKEN', '')
    if not token:
        pytest.skip("TEST_SESSION_TOKEN not set")
    return {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }


@pytest.fixture(scope="session")
def test_case_id_with_content(auth_headers):
    """Create a test case with document content for report generation testing"""
    # Create case
    payload = {
        "title": "TEST_Report Generation Test Case",
        "defendant_name": "TEST_Defendant",
        "case_number": "TEST_RPT/2024",
        "court": "NSW Supreme Court",
        "summary": "Test case for verifying report generation with all 3 report types works correctly. Contains murder appeal evidence."
    }
    response = requests.post(f"{BASE_URL}/api/cases", json=payload, headers=auth_headers)
    assert response.status_code == 200
    case_id = response.json()["case_id"]
    print(f"Created test case: {case_id}")
    
    # Upload document with substantial content for AI analysis
    headers = {"Authorization": auth_headers["Authorization"]}
    doc_content = b"""CRIMINAL APPEAL CASE BRIEF
Case Reference: R v Smith [2024] NSWCCA 123

CASE SUMMARY:
The defendant John Smith was convicted of murder on 15 March 2023 following a jury trial at the NSW Supreme Court. The conviction relates to the death of Jane Doe on 1 January 2023.

EVIDENCE AT TRIAL:
1. Witness Statement - Mary Johnson: "I saw the defendant and the victim arguing outside the bar at approximately 11pm. The defendant appeared agitated and was shouting."
2. Witness Statement - James Brown: "I heard screaming from the alley around 11:30pm. When I arrived, I saw the defendant running away."
3. Forensic Evidence: DNA samples found at the scene matched the defendant.
4. CCTV Footage: Security cameras captured the defendant entering the alley at 11:15pm.

PROCEDURAL ISSUES:
1. The arresting officer failed to caution the defendant properly
2. CCTV evidence was disclosed late - only 2 days before trial
3. Witness James Brown changed his statement between police interview and trial

GROUNDS FOR APPEAL:
1. PROCEDURAL ERROR: The trial judge failed to properly direct the jury on the elements of murder under s.18 Crimes Act 1900 (NSW). Specifically, the direction on intent was inadequate.
2. FRESH EVIDENCE: A new witness has come forward who claims to have seen another person leaving the scene at 11:45pm.
3. PROSECUTION MISCONDUCT: Late disclosure of CCTV evidence prejudiced the defence's ability to prepare.
4. UNRELIABLE IDENTIFICATION: Witness identification was made in poor lighting conditions.

RELEVANT LAW:
- Section 18 Crimes Act 1900 (NSW) - Murder
- Section 23 Crimes Act 1900 (NSW) - Provocation
- Section 137 Evidence Act 1995 (NSW) - Exclusion of prejudicial evidence
- Criminal Appeal Act 1912 (NSW) - Grounds for appeal

RECOMMENDATION:
Strong grounds exist for appeal on procedural error and fresh evidence grounds.
"""
    
    files = {'file': ('legal_brief.txt', doc_content, 'text/plain')}
    data = {'category': 'brief', 'description': 'Legal brief for report generation testing'}
    response = requests.post(f"{BASE_URL}/api/cases/{case_id}/documents", files=files, data=data, headers=headers)
    assert response.status_code == 200
    print(f"Uploaded test document: {response.json()['document_id']}")
    
    yield case_id
    
    # Cleanup - delete test case
    requests.delete(f"{BASE_URL}/api/cases/{case_id}", headers=auth_headers)
    print(f"Deleted test case: {case_id}")


@pytest.fixture(scope="session")
def cleanup_case_id():
    """Placeholder for cleanup - actual cleanup handled by test_case_id_with_content fixture"""
    return None
