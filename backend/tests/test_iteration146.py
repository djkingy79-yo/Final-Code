"""
Iteration 146 Tests - Bug Fixes Verification
Tests for:
1. PayID email typo fix (gmail.com not gmsil.com)
2. Export package endpoint fix (supporting_evidence dict handling)
3. Export preview endpoint
4. Terms of Service font sizes
5. Dashboard overview cards
6. Case page heading
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

class TestHealthAndAuth:
    """Basic health and authentication tests"""
    
    def test_health_endpoint(self):
        """Test health endpoint is accessible"""
        response = requests.get(f"{BASE_URL}/api/health")
        assert response.status_code == 200
        data = response.json()
        assert data.get("status") == "healthy"
        print("✓ Health endpoint working")
    
    def test_login_with_valid_credentials(self):
        """Test login with valid credentials"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": "djkingy79@gmail.com",
            "password": "Cr1m1nalApp3al$2025"
        })
        assert response.status_code == 200
        data = response.json()
        assert "token" in data or "session_token" in data
        print("✓ Login successful")
        return data.get("token") or data.get("session_token")


class TestPayIDEmailFix:
    """Test PayID email is correct (gmail.com not gmsil.com)"""
    
    @pytest.fixture
    def auth_token(self):
        """Get authentication token"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": "djkingy79@gmail.com",
            "password": "Cr1m1nalApp3al$2025"
        })
        if response.status_code == 200:
            data = response.json()
            return data.get("token") or data.get("session_token")
        pytest.skip("Authentication failed")
    
    @pytest.fixture
    def test_case_id(self, auth_token):
        """Get or create a test case"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        # Get existing cases
        response = requests.get(f"{BASE_URL}/api/cases", headers=headers)
        if response.status_code == 200:
            cases = response.json()
            if cases and len(cases) > 0:
                return cases[0].get("case_id")
        # Create a test case if none exist
        response = requests.post(f"{BASE_URL}/api/cases", headers=headers, json={
            "title": "TEST_PayID_Verification_Case",
            "defendant_name": "Test Defendant"
        })
        if response.status_code in [200, 201]:
            return response.json().get("case_id")
        pytest.skip("Could not get or create test case")
    
    def test_payid_create_reference_returns_correct_email(self, auth_token, test_case_id):
        """Test that PayID create-reference returns gmail.com not gmsil.com"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        response = requests.post(f"{BASE_URL}/api/payments/payid/create-reference", 
            headers=headers,
            json={
                "feature_type": "grounds_of_merit",
                "case_id": test_case_id
            }
        )
        assert response.status_code == 200
        data = response.json()
        
        # Verify PayID email is correct
        payid = data.get("payid", "")
        assert "gmail.com" in payid, f"PayID should contain gmail.com, got: {payid}"
        assert "gmsil.com" not in payid, f"PayID should NOT contain gmsil.com typo, got: {payid}"
        assert payid == "djkingy79@gmail.com", f"PayID should be djkingy79@gmail.com, got: {payid}"
        
        print(f"✓ PayID email is correct: {payid}")
        
        # Verify other fields
        assert "reference" in data
        assert "amount" in data
        print(f"✓ Reference generated: {data.get('reference')}")
        print(f"✓ Amount: ${data.get('amount')}")


class TestExportPackageFix:
    """Test Export Package endpoint fix (supporting_evidence dict handling)"""
    
    @pytest.fixture
    def auth_token(self):
        """Get authentication token"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": "djkingy79@gmail.com",
            "password": "Cr1m1nalApp3al$2025"
        })
        if response.status_code == 200:
            data = response.json()
            return data.get("token") or data.get("session_token")
        pytest.skip("Authentication failed")
    
    @pytest.fixture
    def test_case_id(self, auth_token):
        """Get or create a test case"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        response = requests.get(f"{BASE_URL}/api/cases", headers=headers)
        if response.status_code == 200:
            cases = response.json()
            if cases and len(cases) > 0:
                return cases[0].get("case_id")
        pytest.skip("No cases available for export test")
    
    def test_export_preview_endpoint(self, auth_token, test_case_id):
        """Test export preview endpoint returns counts"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        response = requests.get(f"{BASE_URL}/api/cases/{test_case_id}/export/preview", headers=headers)
        
        assert response.status_code == 200, f"Export preview failed with status {response.status_code}"
        data = response.json()
        
        # Verify expected fields
        assert "documents" in data
        assert "timeline_events" in data
        assert "grounds_of_merit" in data
        assert "notes" in data
        assert "reports" in data
        assert "templates" in data
        
        print(f"✓ Export preview working - Documents: {data.get('documents')}, Timeline: {data.get('timeline_events')}, Grounds: {data.get('grounds_of_merit')}")
    
    def test_export_package_endpoint(self, auth_token, test_case_id):
        """Test export package endpoint returns valid ZIP (was crashing on supporting_evidence dicts)"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        response = requests.post(
            f"{BASE_URL}/api/cases/{test_case_id}/export/package",
            headers=headers,
            json={
                "include_documents": True,
                "include_timeline": True,
                "include_grounds": True,
                "include_notes": True,
                "include_reports": True,
                "include_analysis": True,
                "include_templates": True,
                "format": "zip"
            },
            timeout=60
        )
        
        # Should return 200 with ZIP content, not 500 TypeError
        assert response.status_code == 200, f"Export package failed with status {response.status_code}: {response.text[:500] if response.text else 'No response'}"
        
        # Verify it's a ZIP file
        content_type = response.headers.get("content-type", "")
        assert "application/zip" in content_type or "application/octet-stream" in content_type, f"Expected ZIP content type, got: {content_type}"
        
        # Verify content disposition header
        content_disposition = response.headers.get("content-disposition", "")
        assert "attachment" in content_disposition, f"Expected attachment disposition, got: {content_disposition}"
        assert ".zip" in content_disposition, f"Expected .zip in filename, got: {content_disposition}"
        
        # Verify content length is reasonable (at least 1KB for a minimal ZIP)
        content_length = len(response.content)
        assert content_length > 1000, f"ZIP file too small ({content_length} bytes), may be empty or corrupted"
        
        print(f"✓ Export package working - ZIP size: {content_length} bytes")
        print(f"✓ Content-Disposition: {content_disposition}")


class TestFeaturePrices:
    """Test feature prices endpoint"""
    
    def test_get_feature_prices(self):
        """Test feature prices endpoint"""
        response = requests.get(f"{BASE_URL}/api/payments/prices")
        assert response.status_code == 200
        data = response.json()
        assert "prices" in data
        assert "currency" in data
        assert data.get("currency") == "AUD"
        print("✓ Feature prices endpoint working")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
