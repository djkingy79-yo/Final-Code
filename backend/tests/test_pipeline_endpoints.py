"""
Pipeline Endpoints Test Suite - Iteration 129
Tests the 5-stage pipeline: Extract → Classify → Verify → Project → Draft

Endpoints tested:
- POST /api/cases/{case_id}/documents/{document_id}/extract
- POST /api/cases/{case_id}/extract/refresh
- GET /api/cases/{case_id}/extract
- POST /api/cases/{case_id}/issues/classify
- GET /api/cases/{case_id}/issues
- POST /api/cases/{case_id}/issues/{issue_id}/verify
- POST /api/cases/{case_id}/issues/verify-all
- GET /api/cases/{case_id}/issues/{issue_id}/verification
- POST /api/cases/{case_id}/grounds/sync-from-issues
- GET /api/cases/{case_id}/pipeline/status
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', 'http://localhost:8001').rstrip('/')

# Test credentials from test_credentials.md
TEST_EMAIL = "test@example.com"
TEST_PASSWORD = "TestPassword123!"
TEST_CASE_ID = "case_ba08d8e0ad0d"

# Documents with content_text > 100 chars (from review request)
DOCUMENT_IDS_WITH_CONTENT = [
    "doc_64ff35a2e3e2",  # 27571 chars
    "doc_5be64e096915",  # 15106 chars
    "doc_db2eb259f271",  # 14409 chars
]

# Already extracted (from review request)
EXISTING_EXTRACT_IDS = ["ext_c955ed0114be", "ext_ba6a34e87288"]

# Already classified issue (from review request)
VERIFIED_ISSUE_ID = "iss_5487e633cdd7"


@pytest.fixture(scope="module")
def session():
    """Create a requests session with auth token."""
    s = requests.Session()
    s.headers.update({"Content-Type": "application/json"})
    
    # Use direct session token (Google OAuth - no email/password login)
    s.headers.update({"Authorization": "Bearer ci_test_token_permanent_20260412"})
    
    return s


class TestHealthCheck:
    """Verify backend is healthy before running pipeline tests."""
    
    def test_health_endpoint(self, session):
        """Test /api/health returns healthy status."""
        response = session.get(f"{BASE_URL}/api/health")
        assert response.status_code == 200
        data = response.json()
        assert data.get("status") == "healthy"
        assert data.get("database") == "connected"
        print(f"✓ Health check passed: {data}")


class TestPipelineStatus:
    """Test GET /api/cases/{case_id}/pipeline/status - fast endpoint."""
    
    def test_pipeline_status_returns_stage_counts(self, session):
        """Test pipeline status returns all stage counts."""
        response = session.get(f"{BASE_URL}/api/cases/{TEST_CASE_ID}/pipeline/status")
        assert response.status_code == 200
        
        data = response.json()
        assert "case_id" in data
        assert data["case_id"] == TEST_CASE_ID
        assert "stages" in data
        
        stages = data["stages"]
        assert "extract" in stages
        assert "classify" in stages
        assert "verify" in stages
        assert "project" in stages
        
        # Verify extract stage structure
        extract = stages["extract"]
        assert "documents_total" in extract
        assert "documents_extracted" in extract
        assert "case_extract_ready" in extract
        
        # Verify classify stage structure
        classify = stages["classify"]
        assert "issues_identified" in classify
        
        # Verify verify stage structure
        verify = stages["verify"]
        assert "issues_verified" in verify
        assert "issues_pending" in verify
        
        # Verify project stage structure
        project = stages["project"]
        assert "grounds_synced" in project
        
        print(f"✓ Pipeline status: {data}")
    
    def test_pipeline_status_unauthorized(self):
        """Test pipeline status requires authentication."""
        response = requests.get(f"{BASE_URL}/api/cases/{TEST_CASE_ID}/pipeline/status")
        assert response.status_code in [401, 403]
        print("✓ Pipeline status correctly requires auth")


class TestGetCaseExtract:
    """Test GET /api/cases/{case_id}/extract - fast endpoint."""
    
    def test_get_case_extract(self, session):
        """Test getting merged case extract."""
        response = session.get(f"{BASE_URL}/api/cases/{TEST_CASE_ID}/extract")
        assert response.status_code == 200
        
        data = response.json()
        # Either returns case extract or status: not_extracted
        if data.get("status") == "not_extracted":
            assert "message" in data
            print(f"✓ Case extract not yet created: {data['message']}")
        else:
            # Verify case extract structure
            assert "case_extract_id" in data or "case_id" in data
            if "merged_facts" in data:
                assert isinstance(data["merged_facts"], list)
            if "merged_events" in data:
                assert isinstance(data["merged_events"], list)
            if "merged_findings" in data:
                assert isinstance(data["merged_findings"], list)
            print(f"✓ Case extract retrieved: {data.get('case_extract_id', 'N/A')}")


class TestListIssues:
    """Test GET /api/cases/{case_id}/issues - fast endpoint."""
    
    def test_list_issues(self, session):
        """Test listing classified issues."""
        response = session.get(f"{BASE_URL}/api/cases/{TEST_CASE_ID}/issues")
        assert response.status_code == 200
        
        data = response.json()
        assert "count" in data
        assert "issues" in data
        assert isinstance(data["issues"], list)
        
        # If issues exist, verify structure
        if data["count"] > 0:
            issue = data["issues"][0]
            assert "issue_id" in issue
            assert "title" in issue
            assert "ground_type" in issue
            assert "has_verification" in issue
            print(f"✓ Found {data['count']} issues, first: {issue['title'][:50]}...")
        else:
            print("✓ No issues found (classification may not have run)")
    
    def test_list_issues_unauthorized(self):
        """Test list issues requires authentication."""
        response = requests.get(f"{BASE_URL}/api/cases/{TEST_CASE_ID}/issues")
        assert response.status_code in [401, 403]
        print("✓ List issues correctly requires auth")


class TestGetIssueVerification:
    """Test GET /api/cases/{case_id}/issues/{issue_id}/verification - fast endpoint."""
    
    def test_get_verification_for_verified_issue(self, session):
        """Test getting verification for a verified issue."""
        response = session.get(
            f"{BASE_URL}/api/cases/{TEST_CASE_ID}/issues/{VERIFIED_ISSUE_ID}/verification"
        )
        assert response.status_code == 200
        
        data = response.json()
        # Either returns verification or status: not_verified
        if data.get("status") == "not_verified":
            print(f"✓ Issue not yet verified: {data.get('message', 'N/A')}")
        else:
            # Verify verification structure
            assert "verification_id" in data
            assert "issue_id" in data
            assert "supporting_items" in data
            assert "undermining_items" in data
            assert "legitimacy_scores" in data
            
            scores = data["legitimacy_scores"]
            assert "legal_score" in scores
            assert "evidence_score" in scores
            assert "viability_score" in scores
            assert "rating" in scores
            
            print(f"✓ Verification found: {data['verification_id']}, rating: {scores['rating']}")
    
    def test_get_verification_nonexistent_issue(self, session):
        """Test getting verification for non-existent issue."""
        response = session.get(
            f"{BASE_URL}/api/cases/{TEST_CASE_ID}/issues/iss_nonexistent/verification"
        )
        # Should return 200 with status: not_verified or 404
        assert response.status_code in [200, 404]
        print("✓ Non-existent issue verification handled correctly")


class TestExtractRefresh:
    """Test POST /api/cases/{case_id}/extract/refresh - merges document extracts."""
    
    def test_refresh_case_extract(self, session):
        """Test refreshing/merging case extract from document extracts."""
        response = session.post(f"{BASE_URL}/api/cases/{TEST_CASE_ID}/extract/refresh")
        
        # May return 400 if no document extracts exist
        if response.status_code == 400:
            data = response.json()
            assert "detail" in data
            print(f"✓ Refresh blocked (expected): {data['detail']}")
        else:
            assert response.status_code == 200
            data = response.json()
            assert "case_extract_id" in data
            assert "status" in data
            assert data["status"] == "completed"
            assert "document_extracts_used" in data
            assert "merged_facts_count" in data
            assert "merged_events_count" in data
            assert "merged_findings_count" in data
            print(f"✓ Case extract refreshed: {data['case_extract_id']}, "
                  f"facts: {data['merged_facts_count']}, "
                  f"events: {data['merged_events_count']}, "
                  f"findings: {data['merged_findings_count']}")


class TestSyncGroundsFromIssues:
    """Test POST /api/cases/{case_id}/grounds/sync-from-issues - projects issues to grounds."""
    
    def test_sync_grounds_from_issues(self, session):
        """Test syncing grounds from classified issues."""
        response = session.post(f"{BASE_URL}/api/cases/{TEST_CASE_ID}/grounds/sync-from-issues")
        
        # May return 400 if no classified issues exist
        if response.status_code == 400:
            data = response.json()
            assert "detail" in data
            print(f"✓ Sync blocked (expected): {data['detail']}")
        else:
            assert response.status_code == 200
            data = response.json()
            assert "synced_count" in data
            assert "grounds" in data
            assert isinstance(data["grounds"], list)
            
            if data["synced_count"] > 0:
                ground = data["grounds"][0]
                assert "ground_id" in ground
                assert "issue_id" in ground
                assert "title" in ground
                assert "strength" in ground
                assert "has_verification" in ground
                print(f"✓ Synced {data['synced_count']} grounds, first: {ground['title'][:50]}...")
            else:
                print("✓ No grounds synced (no issues to sync)")


class TestDocumentExtraction:
    """Test POST /api/cases/{case_id}/documents/{document_id}/extract - LLM endpoint (slow)."""
    
    def test_extract_document_with_content(self, session):
        """Test extracting facts/events/findings from a document with content.
        
        NOTE: This endpoint calls LLM and takes 10-30 seconds.
        """
        # Use first document with content
        doc_id = DOCUMENT_IDS_WITH_CONTENT[0]
        
        response = session.post(
            f"{BASE_URL}/api/cases/{TEST_CASE_ID}/documents/{doc_id}/extract",
            timeout=60  # LLM calls can be slow
        )
        
        # May return 400 if document has insufficient text
        if response.status_code == 400:
            data = response.json()
            print(f"✓ Extraction blocked: {data.get('detail', 'Unknown')}")
        elif response.status_code == 404:
            print(f"✓ Document not found: {doc_id}")
        else:
            assert response.status_code == 200
            data = response.json()
            assert "extract_id" in data
            assert "status" in data
            assert data["status"] == "completed"
            assert "facts_count" in data
            assert "events_count" in data
            assert "findings_count" in data
            
            print(f"✓ Document extracted: {data['extract_id']}, "
                  f"facts: {data['facts_count']}, "
                  f"events: {data['events_count']}, "
                  f"findings: {data['findings_count']}")
    
    def test_extract_nonexistent_document(self, session):
        """Test extraction fails for non-existent document."""
        response = session.post(
            f"{BASE_URL}/api/cases/{TEST_CASE_ID}/documents/doc_nonexistent/extract"
        )
        assert response.status_code == 404
        print("✓ Non-existent document extraction correctly returns 404")


class TestIssueClassification:
    """Test POST /api/cases/{case_id}/issues/classify - LLM endpoint (slow)."""
    
    def test_classify_issues(self, session):
        """Test classifying extracted facts into appeal issues.
        
        NOTE: This endpoint calls LLM and takes 10-30 seconds.
        Requires case extract to exist first.
        """
        response = session.post(
            f"{BASE_URL}/api/cases/{TEST_CASE_ID}/issues/classify",
            timeout=60
        )
        
        # May return 400 if no case extraction exists
        if response.status_code == 400:
            data = response.json()
            print(f"✓ Classification blocked (expected): {data.get('detail', 'Unknown')}")
        else:
            assert response.status_code == 200
            data = response.json()
            assert "identified_count" in data
            assert "issues" in data
            assert isinstance(data["issues"], list)
            
            if data["identified_count"] > 0:
                issue = data["issues"][0]
                assert "issue_id" in issue
                assert "title" in issue
                assert "ground_type" in issue
                assert "classification_confidence" in issue
                print(f"✓ Classified {data['identified_count']} issues, "
                      f"first: {issue['title'][:50]}...")
            else:
                print("✓ No issues classified")


class TestIssueVerification:
    """Test POST /api/cases/{case_id}/issues/{issue_id}/verify - LLM endpoint (slow)."""
    
    def test_verify_single_issue(self, session):
        """Test verifying a single classified issue.
        
        NOTE: This endpoint calls LLM and takes 10-30 seconds.
        """
        # First get list of issues
        list_response = session.get(f"{BASE_URL}/api/cases/{TEST_CASE_ID}/issues")
        if list_response.status_code != 200:
            pytest.skip("Could not get issues list")
        
        issues = list_response.json().get("issues", [])
        if not issues:
            pytest.skip("No issues to verify")
        
        # Verify first issue
        issue_id = issues[0]["issue_id"]
        
        response = session.post(
            f"{BASE_URL}/api/cases/{TEST_CASE_ID}/issues/{issue_id}/verify",
            timeout=60
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "verification_id" in data
        assert "verification_status" in data
        assert "rating" in data
        assert "legitimacy_scores" in data
        assert "supporting_count" in data
        assert "undermining_count" in data
        assert "missing_count" in data
        
        print(f"✓ Issue verified: {data['verification_id']}, "
              f"rating: {data['rating']}, "
              f"supporting: {data['supporting_count']}, "
              f"undermining: {data['undermining_count']}")
    
    def test_verify_nonexistent_issue(self, session):
        """Test verification fails for non-existent issue."""
        response = session.post(
            f"{BASE_URL}/api/cases/{TEST_CASE_ID}/issues/iss_nonexistent/verify",
            timeout=30
        )
        assert response.status_code == 404
        print("✓ Non-existent issue verification correctly returns 404")


class TestVerifyAllIssues:
    """Test POST /api/cases/{case_id}/issues/verify-all - LLM endpoint (very slow)."""
    
    def test_verify_all_issues(self, session):
        """Test batch verification of all classified issues.
        
        NOTE: This endpoint calls LLM for EACH issue and can take several minutes.
        """
        response = session.post(
            f"{BASE_URL}/api/cases/{TEST_CASE_ID}/issues/verify-all",
            timeout=300  # 5 minutes for batch verification
        )
        
        # May return 400 if no classified issues exist
        if response.status_code == 400:
            data = response.json()
            print(f"✓ Verify-all blocked (expected): {data.get('detail', 'Unknown')}")
        else:
            assert response.status_code == 200
            data = response.json()
            assert "verified_count" in data
            assert "failed_count" in data
            assert "results" in data
            assert isinstance(data["results"], list)
            
            print(f"✓ Batch verification: {data['verified_count']} verified, "
                  f"{data['failed_count']} failed")
            
            # Check result structure
            if data["results"]:
                result = data["results"][0]
                assert "issue_id" in result
                assert "status" in result


class TestCaseOwnership:
    """Test that pipeline endpoints enforce case ownership."""
    
    def test_pipeline_status_wrong_case(self, session):
        """Test pipeline status for non-existent case."""
        response = session.get(f"{BASE_URL}/api/cases/case_nonexistent/pipeline/status")
        assert response.status_code == 404
        print("✓ Pipeline status correctly returns 404 for non-existent case")
    
    def test_extract_wrong_case(self, session):
        """Test extract for non-existent case."""
        response = session.get(f"{BASE_URL}/api/cases/case_nonexistent/extract")
        assert response.status_code == 404
        print("✓ Get extract correctly returns 404 for non-existent case")
    
    def test_issues_wrong_case(self, session):
        """Test issues list for non-existent case."""
        response = session.get(f"{BASE_URL}/api/cases/case_nonexistent/issues")
        assert response.status_code == 404
        print("✓ List issues correctly returns 404 for non-existent case")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
