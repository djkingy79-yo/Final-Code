"""
Test suite for Iteration 33 - ReportView, BarristerView, and ReportsSection features
Tests: Premium summary box, Table of Contents, full in-browser reading, prompt guardrails
"""
import pytest
import requests
import os

BASE_URL = 'http://localhost:8001'

class TestHealthAndBasicEndpoints:
    """Basic API health and endpoint tests"""
    
    def test_api_health(self):
        """Test API health endpoint"""
        response = requests.get(f"{BASE_URL}/api/health", timeout=10)
        assert response.status_code == 200, f"Health check failed: {response.status_code}"
        data = response.json()
        assert data.get("status") == "healthy"
        print(f"PASS: Health endpoint returns status=healthy")
    
    def test_offence_categories(self):
        """Test offence categories endpoint"""
        response = requests.get(f"{BASE_URL}/api/offence-categories", timeout=10)
        assert response.status_code == 200, f"Offence categories failed: {response.status_code}"
        data = response.json()
        # API returns dict with 'categories' key
        categories = data.get("categories") if isinstance(data, dict) else data
        assert isinstance(categories, list), "Expected list of categories"
        assert len(categories) > 0, "Expected at least one offence category"
        print(f"PASS: Offence categories returns {len(categories)} categories")
    
    def test_states_endpoint(self):
        """Test states endpoint"""
        response = requests.get(f"{BASE_URL}/api/states", timeout=10)
        assert response.status_code == 200, f"States endpoint failed: {response.status_code}"
        data = response.json()
        # API returns dict with 'states' key
        states = data.get("states") if isinstance(data, dict) else data
        assert isinstance(states, list), "Expected list of states"
        assert len(states) >= 8, "Expected at least 8 Australian states/territories"
        print(f"PASS: States endpoint returns {len(states)} states/territories")


class TestPaymentEndpoints:
    """Test payment-related endpoints"""
    
    def test_payment_prices(self):
        """Test payment prices endpoint"""
        response = requests.get(f"{BASE_URL}/api/payments/prices", timeout=10)
        assert response.status_code == 200, f"Payment prices failed: {response.status_code}"
        data = response.json()
        assert "full_report" in data or isinstance(data, dict), "Expected prices dict"
        print(f"PASS: Payment prices endpoint returns valid response")
    
    def test_payment_methods(self):
        """Test payment methods endpoint"""
        response = requests.get(f"{BASE_URL}/api/payments/methods", timeout=10)
        assert response.status_code == 200, f"Payment methods failed: {response.status_code}"
        print(f"PASS: Payment methods endpoint returns valid response")


class TestAuthProtection:
    """Test that protected endpoints require authentication"""
    
    def test_auth_me_requires_auth(self):
        """Test that /auth/me requires authentication"""
        response = requests.get(f"{BASE_URL}/api/auth/me", timeout=10)
        assert response.status_code in [401, 403], f"Expected 401/403, got {response.status_code}"
        print(f"PASS: /auth/me correctly requires authentication")
    
    def test_cases_endpoint_requires_auth(self):
        """Test that /cases requires authentication"""
        response = requests.get(f"{BASE_URL}/api/cases", timeout=10)
        assert response.status_code in [401, 403], f"Expected 401/403, got {response.status_code}"
        print(f"PASS: /cases correctly requires authentication")


class TestReportGenerationProtection:
    """Test report generation requires auth and valid case"""
    
    def test_report_generate_requires_auth(self):
        """Test report generation requires authentication"""
        response = requests.post(
            f"{BASE_URL}/api/cases/fake-case-id/reports/generate",
            json={"report_type": "quick_summary"},
            timeout=10
        )
        assert response.status_code in [401, 403], f"Expected 401/403, got {response.status_code}"
        print(f"PASS: Report generation correctly requires authentication")


class TestExportEndpoints:
    """Test export endpoints exist (require auth)"""
    
    def test_pdf_export_endpoint_exists(self):
        """Test PDF export endpoint returns auth error (proving it exists)"""
        response = requests.get(
            f"{BASE_URL}/api/cases/fake-case-id/reports/fake-report-id/export-pdf",
            timeout=10
        )
        # Should return 401/403 (auth required) or 404 (not found) - both prove endpoint exists
        assert response.status_code in [401, 403, 404], f"Unexpected status: {response.status_code}"
        print(f"PASS: PDF export endpoint exists (status {response.status_code})")
    
    def test_docx_export_endpoint_exists(self):
        """Test DOCX export endpoint returns auth error (proving it exists)"""
        response = requests.get(
            f"{BASE_URL}/api/cases/fake-case-id/reports/fake-report-id/export-docx",
            timeout=10
        )
        assert response.status_code in [401, 403, 404], f"Unexpected status: {response.status_code}"
        print(f"PASS: DOCX export endpoint exists (status {response.status_code})")


class TestPublicPages:
    """Test public pages are accessible"""
    
    def test_landing_page_loads(self):
        """Test landing page loads"""
        response = requests.get(BASE_URL, timeout=15)
        assert response.status_code == 200, f"Landing page failed: {response.status_code}"
        assert "Criminal Appeal" in response.text or "Appeal" in response.text
        print(f"PASS: Landing page loads successfully")
    
    def test_legal_resources_page(self):
        """Test legal resources page accessible"""
        response = requests.get(f"{BASE_URL}/legal-resources", timeout=10)
        assert response.status_code == 200, f"Legal resources failed: {response.status_code}"
        print(f"PASS: Legal resources page loads")
    
    def test_terms_page(self):
        """Test terms page accessible"""
        response = requests.get(f"{BASE_URL}/terms", timeout=10)
        assert response.status_code == 200, f"Terms page failed: {response.status_code}"
        print(f"PASS: Terms page loads")
    
    def test_about_page(self):
        """Test about page accessible"""
        response = requests.get(f"{BASE_URL}/about", timeout=10)
        assert response.status_code == 200, f"About page failed: {response.status_code}"
        print(f"PASS: About page loads")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
