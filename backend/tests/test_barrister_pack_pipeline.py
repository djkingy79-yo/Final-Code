"""
Test suite for Barrister Acceptance Pack PDF generation and Pipeline Progress endpoints.
Tests the two new features:
1. GET /api/cases/{case_id}/barrister-pack/generate - PDF generation
2. GET /api/cases/{case_id}/pipeline/status - Pipeline status for Progress widget
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Test credentials
TEST_EMAIL = "test@example.com"
TEST_PASSWORD = "TestPassword123!"
TEST_CASE_ID = "case_87ef925be713"


@pytest.fixture(scope="module")
def session_token():
    """Get authentication token via login endpoint"""
    response = requests.post(
        f"{BASE_URL}/api/auth/login",
        json={"email": TEST_EMAIL, "password": TEST_PASSWORD},
        timeout=30
    )
    if response.status_code == 200:
        data = response.json()
        return data.get("session_token")
    pytest.skip(f"Authentication failed: {response.status_code}")


@pytest.fixture(scope="module")
def auth_headers(session_token):
    """Return headers with auth token"""
    return {"Authorization": f"Bearer {session_token}"}


class TestBarristerAcceptancePackPDF:
    """Tests for Barrister Acceptance Pack PDF generation endpoint"""
    
    def test_generate_barrister_pack_returns_pdf(self, auth_headers):
        """Test that endpoint returns a valid PDF file"""
        response = requests.get(
            f"{BASE_URL}/api/cases/{TEST_CASE_ID}/barrister-pack/generate",
            headers=auth_headers,
            timeout=120
        )
        
        # Status code assertion
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        # Content-Type assertion
        content_type = response.headers.get("Content-Type", "")
        assert "application/pdf" in content_type, f"Expected application/pdf, got {content_type}"
        
        # Content-Disposition assertion (should have filename)
        content_disposition = response.headers.get("Content-Disposition", "")
        assert "attachment" in content_disposition, "Expected attachment disposition"
        assert "filename=" in content_disposition, "Expected filename in disposition"
        assert ".pdf" in content_disposition, "Expected .pdf extension in filename"
        
        # PDF content assertion (check PDF magic bytes)
        assert len(response.content) > 1000, "PDF content too small"
        assert response.content[:4] == b'%PDF', "Content does not start with PDF magic bytes"
    
    def test_generate_barrister_pack_unauthorized(self):
        """Test that endpoint requires authentication"""
        response = requests.get(
            f"{BASE_URL}/api/cases/{TEST_CASE_ID}/barrister-pack/generate",
            timeout=30
        )
        
        assert response.status_code in [401, 403], f"Expected 401/403, got {response.status_code}"
    
    def test_generate_barrister_pack_nonexistent_case(self, auth_headers):
        """Test that endpoint returns 404 for non-existent case"""
        response = requests.get(
            f"{BASE_URL}/api/cases/nonexistent_case_id/barrister-pack/generate",
            headers=auth_headers,
            timeout=30
        )
        
        assert response.status_code == 404, f"Expected 404, got {response.status_code}"
    
    def test_generate_barrister_pack_filename_format(self, auth_headers):
        """Test that PDF filename follows expected format"""
        response = requests.get(
            f"{BASE_URL}/api/cases/{TEST_CASE_ID}/barrister-pack/generate",
            headers=auth_headers,
            timeout=120
        )
        
        assert response.status_code == 200
        
        content_disposition = response.headers.get("Content-Disposition", "")
        # Expected format: Barrister_Acceptance_Pack_{defendant_name}_{date}.pdf
        assert "Barrister_Acceptance_Pack" in content_disposition, "Filename should contain 'Barrister_Acceptance_Pack'"


class TestPipelineStatusEndpoint:
    """Tests for Pipeline Status endpoint used by PipelineProgress widget"""
    
    def test_pipeline_status_returns_stages(self, auth_headers):
        """Test that endpoint returns all pipeline stages"""
        response = requests.get(
            f"{BASE_URL}/api/cases/{TEST_CASE_ID}/pipeline/status",
            headers=auth_headers,
            timeout=30
        )
        
        # Status code assertion
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        # Data structure assertions
        data = response.json()
        assert "case_id" in data, "Response should contain case_id"
        assert data["case_id"] == TEST_CASE_ID, "case_id should match request"
        assert "stages" in data, "Response should contain stages"
        
        stages = data["stages"]
        
        # Check all 4 stages exist
        assert "extract" in stages, "Missing 'extract' stage"
        assert "classify" in stages, "Missing 'classify' stage"
        assert "verify" in stages, "Missing 'verify' stage"
        assert "project" in stages, "Missing 'project' stage"
    
    def test_pipeline_status_extract_stage_structure(self, auth_headers):
        """Test extract stage has correct structure"""
        response = requests.get(
            f"{BASE_URL}/api/cases/{TEST_CASE_ID}/pipeline/status",
            headers=auth_headers,
            timeout=30
        )
        
        assert response.status_code == 200
        data = response.json()
        extract = data["stages"]["extract"]
        
        assert "documents_total" in extract, "Extract stage should have documents_total"
        assert "documents_extracted" in extract, "Extract stage should have documents_extracted"
        assert "case_extract_ready" in extract, "Extract stage should have case_extract_ready"
        
        # Type assertions
        assert isinstance(extract["documents_total"], int)
        assert isinstance(extract["documents_extracted"], int)
        assert isinstance(extract["case_extract_ready"], bool)
    
    def test_pipeline_status_classify_stage_structure(self, auth_headers):
        """Test classify stage has correct structure"""
        response = requests.get(
            f"{BASE_URL}/api/cases/{TEST_CASE_ID}/pipeline/status",
            headers=auth_headers,
            timeout=30
        )
        
        assert response.status_code == 200
        data = response.json()
        classify = data["stages"]["classify"]
        
        assert "issues_identified" in classify, "Classify stage should have issues_identified"
        assert isinstance(classify["issues_identified"], int)
    
    def test_pipeline_status_verify_stage_structure(self, auth_headers):
        """Test verify stage has correct structure"""
        response = requests.get(
            f"{BASE_URL}/api/cases/{TEST_CASE_ID}/pipeline/status",
            headers=auth_headers,
            timeout=30
        )
        
        assert response.status_code == 200
        data = response.json()
        verify = data["stages"]["verify"]
        
        assert "issues_verified" in verify, "Verify stage should have issues_verified"
        assert "issues_pending" in verify, "Verify stage should have issues_pending"
        assert isinstance(verify["issues_verified"], int)
        assert isinstance(verify["issues_pending"], int)
    
    def test_pipeline_status_project_stage_structure(self, auth_headers):
        """Test project stage has correct structure"""
        response = requests.get(
            f"{BASE_URL}/api/cases/{TEST_CASE_ID}/pipeline/status",
            headers=auth_headers,
            timeout=30
        )
        
        assert response.status_code == 200
        data = response.json()
        project = data["stages"]["project"]
        
        assert "grounds_synced" in project, "Project stage should have grounds_synced"
        assert isinstance(project["grounds_synced"], int)
    
    def test_pipeline_status_unauthorized(self):
        """Test that endpoint requires authentication"""
        response = requests.get(
            f"{BASE_URL}/api/cases/{TEST_CASE_ID}/pipeline/status",
            timeout=30
        )
        
        assert response.status_code in [401, 403], f"Expected 401/403, got {response.status_code}"
    
    def test_pipeline_status_nonexistent_case(self, auth_headers):
        """Test that endpoint returns 404 for non-existent case"""
        response = requests.get(
            f"{BASE_URL}/api/cases/nonexistent_case_id/pipeline/status",
            headers=auth_headers,
            timeout=30
        )
        
        assert response.status_code == 404, f"Expected 404, got {response.status_code}"


class TestHealthCheck:
    """Basic health check to ensure API is running"""
    
    def test_health_endpoint(self):
        """Test health endpoint returns healthy status"""
        response = requests.get(f"{BASE_URL}/api/health", timeout=10)
        
        assert response.status_code == 200
        data = response.json()
        assert data.get("status") == "healthy"
