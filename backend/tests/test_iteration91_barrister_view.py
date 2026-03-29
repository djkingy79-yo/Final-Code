"""
Iteration 91 - Barrister View Backend Synthesis Tests
Tests the new backend barrister-view endpoint and related functionality.
"""
import pytest
import requests
import os

BASE_URL = 'http://localhost:8001'


class TestHealthAndBasicEndpoints:
    """Basic health and endpoint availability tests"""
    
    def test_health_check(self):
        """Test backend health endpoint"""
        response = requests.get(f"{BASE_URL}/api/health")
        assert response.status_code == 200
        data = response.json()
        assert data.get("status") == "healthy"
        assert data.get("database") == "connected"
        print(f"✓ Health check passed: {data}")
    
    def test_offence_categories_endpoint(self):
        """Test offence categories endpoint"""
        response = requests.get(f"{BASE_URL}/api/offence-categories")
        assert response.status_code == 200
        data = response.json()
        assert "categories" in data
        assert len(data["categories"]) > 0
        print(f"✓ Offence categories: {len(data['categories'])} categories available")
    
    def test_states_endpoint(self):
        """Test Australian states endpoint"""
        response = requests.get(f"{BASE_URL}/api/states")
        assert response.status_code == 200
        data = response.json()
        assert "states" in data
        assert len(data["states"]) > 0
        print(f"✓ States: {len(data['states'])} states available")


class TestBarristerViewEndpointStructure:
    """Tests for the barrister-view endpoint structure (without auth)"""
    
    def test_barrister_view_requires_auth(self):
        """Test that barrister-view endpoint requires authentication"""
        # Using a fake case_id to test auth requirement
        response = requests.get(f"{BASE_URL}/api/cases/fake_case_id/reports/barrister-view")
        assert response.status_code == 401
        data = response.json()
        assert "detail" in data
        print(f"✓ Barrister view requires auth: {data.get('detail')}")
    
    def test_reports_endpoint_requires_auth(self):
        """Test that reports endpoint requires authentication"""
        response = requests.get(f"{BASE_URL}/api/cases/fake_case_id/reports")
        assert response.status_code == 401
        print("✓ Reports endpoint requires auth")
    
    def test_export_pdf_requires_auth(self):
        """Test that PDF export requires authentication"""
        response = requests.get(f"{BASE_URL}/api/cases/fake_case_id/reports/fake_report_id/export-pdf")
        assert response.status_code == 401
        print("✓ PDF export requires auth")
    
    def test_export_docx_requires_auth(self):
        """Test that DOCX export requires authentication"""
        response = requests.get(f"{BASE_URL}/api/cases/fake_case_id/reports/fake_report_id/export-docx")
        assert response.status_code == 401
        print("✓ DOCX export requires auth")


class TestReportExportEndpoints:
    """Tests for report export endpoints structure"""
    
    def test_export_pdf_endpoint_exists(self):
        """Verify PDF export endpoint exists and returns proper auth error"""
        response = requests.get(f"{BASE_URL}/api/cases/test_case/reports/test_report/export-pdf")
        # Should return 401 (auth required) not 404 (endpoint not found)
        assert response.status_code == 401
        print("✓ PDF export endpoint exists")
    
    def test_export_docx_endpoint_exists(self):
        """Verify DOCX export endpoint exists and returns proper auth error"""
        response = requests.get(f"{BASE_URL}/api/cases/test_case/reports/test_report/export-docx")
        # Should return 401 (auth required) not 404 (endpoint not found)
        assert response.status_code == 401
        print("✓ DOCX export endpoint exists")


class TestQueryParamTokenSupport:
    """Tests for session_token query parameter support"""
    
    def test_invalid_session_token_query_param(self):
        """Test that invalid session_token in query param returns 401"""
        response = requests.get(
            f"{BASE_URL}/api/cases/test_case/reports/barrister-view",
            params={"session_token": "invalid_token_12345"}
        )
        assert response.status_code == 401
        data = response.json()
        assert "detail" in data
        print(f"✓ Invalid session_token rejected: {data.get('detail')}")
    
    def test_export_with_invalid_session_token(self):
        """Test that export with invalid session_token returns 401"""
        response = requests.get(
            f"{BASE_URL}/api/cases/test_case/reports/test_report/export-pdf",
            params={"session_token": "invalid_token_12345"}
        )
        assert response.status_code == 401
        print("✓ Export with invalid session_token rejected")


class TestCaseEndpoints:
    """Tests for case-related endpoints"""
    
    def test_cases_endpoint_requires_auth(self):
        """Test that cases endpoint requires authentication"""
        response = requests.get(f"{BASE_URL}/api/cases")
        assert response.status_code == 401
        print("✓ Cases endpoint requires auth")
    
    def test_single_case_requires_auth(self):
        """Test that single case endpoint requires authentication"""
        response = requests.get(f"{BASE_URL}/api/cases/test_case_id")
        assert response.status_code == 401
        print("✓ Single case endpoint requires auth")
    
    def test_case_grounds_requires_auth(self):
        """Test that case grounds endpoint requires authentication"""
        response = requests.get(f"{BASE_URL}/api/cases/test_case_id/grounds")
        assert response.status_code == 401
        print("✓ Case grounds endpoint requires auth")
    
    def test_case_timeline_requires_auth(self):
        """Test that case timeline endpoint requires authentication"""
        response = requests.get(f"{BASE_URL}/api/cases/test_case_id/timeline")
        assert response.status_code == 401
        print("✓ Case timeline endpoint requires auth")
    
    def test_case_documents_requires_auth(self):
        """Test that case documents endpoint requires authentication"""
        response = requests.get(f"{BASE_URL}/api/cases/test_case_id/documents")
        assert response.status_code == 401
        print("✓ Case documents endpoint requires auth")


class TestPublicPages:
    """Tests for public pages that don't require auth"""
    
    def test_landing_page_loads(self):
        """Test that landing page loads"""
        response = requests.get(f"{BASE_URL}/")
        assert response.status_code == 200
        assert "Criminal Appeal AI" in response.text
        print("✓ Landing page loads")
    
    def test_how_it_works_page_loads(self):
        """Test that How It Works page loads"""
        response = requests.get(f"{BASE_URL}/how-it-works")
        assert response.status_code == 200
        print("✓ How It Works page loads")
    
    def test_faq_page_loads(self):
        """Test that FAQ page loads"""
        response = requests.get(f"{BASE_URL}/faq")
        assert response.status_code == 200
        print("✓ FAQ page loads")
    
    def test_about_page_loads(self):
        """Test that About page loads"""
        response = requests.get(f"{BASE_URL}/about")
        assert response.status_code == 200
        print("✓ About page loads")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
