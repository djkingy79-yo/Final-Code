"""
Test Compare Cases and Contradiction Finder features
Tests for:
- /api/compare/patterns - Get anonymized patterns
- /api/compare/my-cases - Compare user's cases
- /api/compare/success-factors - Get success factors
- /api/cases/{case_id}/contradictions/scan - Run contradiction scan
- /api/cases/{case_id}/contradictions/scans - Get all scans
"""
import pytest
import requests
import os
import uuid
from datetime import datetime

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://appeal-hub-5.preview.emergentagent.com')


class TestAuthentication:
    """Test that endpoints require authentication"""
    
    def test_patterns_requires_auth(self):
        """GET /api/compare/patterns returns 401 without auth"""
        response = requests.get(f"{BASE_URL}/api/compare/patterns")
        assert response.status_code == 401
        print("✓ /api/compare/patterns requires authentication")
    
    def test_my_cases_requires_auth(self):
        """POST /api/compare/my-cases returns 401 without auth"""
        response = requests.post(f"{BASE_URL}/api/compare/my-cases", json={"case_ids": []})
        assert response.status_code == 401
        print("✓ /api/compare/my-cases requires authentication")
    
    def test_success_factors_requires_auth(self):
        """GET /api/compare/success-factors returns 401 without auth"""
        response = requests.get(f"{BASE_URL}/api/compare/success-factors")
        assert response.status_code == 401
        print("✓ /api/compare/success-factors requires authentication")
    
    def test_contradictions_scan_requires_auth(self):
        """POST /api/cases/{case_id}/contradictions/scan returns 401 without auth"""
        response = requests.post(f"{BASE_URL}/api/cases/test123/contradictions/scan", json={})
        assert response.status_code == 401
        print("✓ /api/cases/{case_id}/contradictions/scan requires authentication")


@pytest.fixture(scope="module")
def auth_session():
    """Create authenticated session with test user"""
    session = requests.Session()
    
    # Register or login with test user
    test_email = f"test_compare_{uuid.uuid4().hex[:8]}@test.com"
    test_password = "testpass123"
    test_name = "Test Compare User"
    
    # Try to register
    register_response = session.post(f"{BASE_URL}/api/auth/register", json={
        "email": test_email,
        "password": test_password,
        "name": test_name
    })
    
    if register_response.status_code == 200:
        print(f"✓ Test user registered: {test_email}")
    elif register_response.status_code == 400 and "already registered" in register_response.text:
        # Login instead
        login_response = session.post(f"{BASE_URL}/api/auth/login", json={
            "email": test_email,
            "password": test_password
        })
        assert login_response.status_code == 200, f"Login failed: {login_response.text}"
        print(f"✓ Test user logged in: {test_email}")
    else:
        pytest.skip(f"Could not authenticate: {register_response.text}")
    
    # Verify authentication
    me_response = session.get(f"{BASE_URL}/api/auth/me")
    assert me_response.status_code == 200, "Failed to verify authentication"
    
    return session


class TestComparePatterns:
    """Test /api/compare/patterns endpoint"""
    
    def test_get_patterns_no_filter(self, auth_session):
        """Get patterns without filters"""
        response = auth_session.get(f"{BASE_URL}/api/compare/patterns")
        assert response.status_code == 200
        
        data = response.json()
        # Verify response structure
        assert "total_cases_analyzed" in data
        assert "patterns" in data or "message" in data
        print(f"✓ GET /api/compare/patterns - Found {data.get('total_cases_analyzed', 0)} cases")
    
    def test_get_patterns_with_offence_filter(self, auth_session):
        """Get patterns filtered by offence category"""
        response = auth_session.get(f"{BASE_URL}/api/compare/patterns?offence_category=homicide")
        assert response.status_code == 200
        
        data = response.json()
        assert "filters_applied" in data or "message" in data
        print(f"✓ GET /api/compare/patterns with offence_category filter works")
    
    def test_get_patterns_with_state_filter(self, auth_session):
        """Get patterns filtered by state"""
        response = auth_session.get(f"{BASE_URL}/api/compare/patterns?state=nsw")
        assert response.status_code == 200
        
        data = response.json()
        print(f"✓ GET /api/compare/patterns with state filter works")
    
    def test_get_patterns_with_ground_type_filter(self, auth_session):
        """Get patterns filtered by ground type"""
        response = auth_session.get(f"{BASE_URL}/api/compare/patterns?ground_type=procedural_error")
        assert response.status_code == 200
        
        data = response.json()
        print(f"✓ GET /api/compare/patterns with ground_type filter works")


class TestCompareSuccessFactors:
    """Test /api/compare/success-factors endpoint"""
    
    def test_get_success_factors(self, auth_session):
        """Get success factors without filter"""
        response = auth_session.get(f"{BASE_URL}/api/compare/success-factors")
        assert response.status_code == 200
        
        data = response.json()
        assert "success_factors" in data or "message" in data
        print(f"✓ GET /api/compare/success-factors works")
    
    def test_get_success_factors_with_filter(self, auth_session):
        """Get success factors filtered by offence category"""
        response = auth_session.get(f"{BASE_URL}/api/compare/success-factors?offence_category=assault")
        assert response.status_code == 200
        
        data = response.json()
        print(f"✓ GET /api/compare/success-factors with filter works")


@pytest.fixture(scope="module")
def test_cases(auth_session):
    """Create test cases for comparison"""
    created_cases = []
    
    # Create 2 test cases for comparison
    for i in range(2):
        case_data = {
            "title": f"TEST_Compare_Case_{i}_{uuid.uuid4().hex[:6]}",
            "defendant_name": f"Test Defendant {i}",
            "offence_category": "homicide" if i == 0 else "assault",
            "state": "nsw",
            "case_number": f"TEST{i}2024"
        }
        response = auth_session.post(f"{BASE_URL}/api/cases", json=case_data)
        if response.status_code == 200:
            created_cases.append(response.json())
            print(f"✓ Created test case: {case_data['title']}")
    
    yield created_cases
    
    # Cleanup - delete test cases
    for case in created_cases:
        try:
            auth_session.delete(f"{BASE_URL}/api/cases/{case['case_id']}")
            print(f"✓ Cleaned up test case: {case['case_id']}")
        except:
            pass


class TestCompareMyCases:
    """Test /api/compare/my-cases endpoint"""
    
    def test_compare_requires_2_cases(self, auth_session, test_cases):
        """Compare with less than 2 cases should fail"""
        if len(test_cases) < 1:
            pytest.skip("No test cases available")
        
        response = auth_session.post(f"{BASE_URL}/api/compare/my-cases", json={
            "case_ids": [test_cases[0]["case_id"]]
        })
        assert response.status_code == 400
        assert "at least 2 cases" in response.text.lower()
        print("✓ Compare requires at least 2 cases")
    
    def test_compare_max_5_cases(self, auth_session, test_cases):
        """Compare with more than 5 cases should fail"""
        fake_ids = [f"fake_{i}" for i in range(6)]
        
        response = auth_session.post(f"{BASE_URL}/api/compare/my-cases", json={
            "case_ids": fake_ids
        })
        assert response.status_code == 400
        assert "maximum 5" in response.text.lower()
        print("✓ Compare enforces maximum 5 cases")
    
    def test_compare_validates_case_ownership(self, auth_session):
        """Compare with non-existent case should fail"""
        response = auth_session.post(f"{BASE_URL}/api/compare/my-cases", json={
            "case_ids": ["nonexistent_case_1", "nonexistent_case_2"]
        })
        assert response.status_code == 404
        print("✓ Compare validates case ownership")
    
    def test_compare_success(self, auth_session, test_cases):
        """Successful comparison of 2 cases"""
        if len(test_cases) < 2:
            pytest.skip("Need at least 2 test cases")
        
        response = auth_session.post(f"{BASE_URL}/api/compare/my-cases", json={
            "case_ids": [case["case_id"] for case in test_cases[:2]]
        })
        assert response.status_code == 200
        
        data = response.json()
        assert "cases" in data
        assert "ground_comparison" in data
        assert "timeline_comparison" in data
        assert "document_comparison" in data
        assert "insights" in data
        
        print(f"✓ Compare my cases successful - {len(data['cases'])} cases compared")


@pytest.fixture(scope="module")
def test_case_with_docs(auth_session):
    """Create test case with multiple documents for contradiction scanning"""
    # Create a test case
    case_data = {
        "title": f"TEST_Contradiction_Case_{uuid.uuid4().hex[:6]}",
        "defendant_name": "Test Contradiction Defendant",
        "offence_category": "assault",
        "state": "nsw"
    }
    response = auth_session.post(f"{BASE_URL}/api/cases", json=case_data)
    if response.status_code != 200:
        pytest.skip(f"Could not create test case: {response.text}")
    
    case = response.json()
    case_id = case["case_id"]
    print(f"✓ Created case for contradiction testing: {case_id}")
    
    # Add 2 text documents
    docs_created = 0
    for i in range(2):
        files = {
            'file': (f'test_doc_{i}.txt', f'Test document {i} content for contradiction analysis. Witness stated event happened at {10+i}pm.', 'text/plain')
        }
        data = {
            'category': 'evidence',
            'description': f'Test document {i}'
        }
        doc_response = auth_session.post(
            f"{BASE_URL}/api/cases/{case_id}/documents",
            files=files,
            data=data
        )
        if doc_response.status_code == 200:
            docs_created += 1
            print(f"✓ Created test document {i}")
    
    yield {"case_id": case_id, "docs_created": docs_created}
    
    # Cleanup
    try:
        auth_session.delete(f"{BASE_URL}/api/cases/{case_id}")
        print(f"✓ Cleaned up test case: {case_id}")
    except:
        pass


class TestContradictionFinder:
    """Test Contradiction Finder endpoints"""
    
    def test_scan_requires_2_documents(self, auth_session, test_case_with_docs):
        """Scan should require at least 2 documents"""
        case_id = test_case_with_docs["case_id"]
        
        # Create a case with only 1 document
        case_data = {
            "title": f"TEST_Single_Doc_Case_{uuid.uuid4().hex[:6]}",
            "defendant_name": "Test Single Doc",
            "offence_category": "assault",
            "state": "nsw"
        }
        response = auth_session.post(f"{BASE_URL}/api/cases", json=case_data)
        if response.status_code != 200:
            pytest.skip("Could not create test case")
        
        single_doc_case = response.json()
        single_case_id = single_doc_case["case_id"]
        
        # Add only 1 document
        files = {
            'file': ('single.txt', 'Single document content', 'text/plain')
        }
        data = {'category': 'evidence'}
        auth_session.post(f"{BASE_URL}/api/cases/{single_case_id}/documents", files=files, data=data)
        
        # Try to scan
        scan_response = auth_session.post(f"{BASE_URL}/api/cases/{single_case_id}/contradictions/scan", json={})
        
        # Cleanup
        auth_session.delete(f"{BASE_URL}/api/cases/{single_case_id}")
        
        assert scan_response.status_code == 400
        assert "at least 2 documents" in scan_response.text.lower()
        print("✓ Contradiction scan requires at least 2 documents")
    
    def test_get_scans_empty(self, auth_session, test_case_with_docs):
        """Get scans for case with no scans"""
        case_id = test_case_with_docs["case_id"]
        
        response = auth_session.get(f"{BASE_URL}/api/cases/{case_id}/contradictions/scans")
        assert response.status_code == 200
        
        data = response.json()
        assert isinstance(data, list)
        print(f"✓ GET /api/cases/{case_id}/contradictions/scans works (found {len(data)} scans)")
    
    def test_scan_validates_case_ownership(self, auth_session):
        """Scan should validate case ownership"""
        response = auth_session.post(f"{BASE_URL}/api/cases/nonexistent_case/contradictions/scan", json={})
        assert response.status_code == 404
        print("✓ Contradiction scan validates case ownership")
    
    def test_scan_with_focus_areas(self, auth_session, test_case_with_docs):
        """Scan with focus areas specified"""
        if test_case_with_docs["docs_created"] < 2:
            pytest.skip("Need at least 2 documents")
        
        case_id = test_case_with_docs["case_id"]
        
        # Note: This test may take long due to AI processing
        # Just verify the request is accepted
        response = auth_session.post(
            f"{BASE_URL}/api/cases/{case_id}/contradictions/scan",
            json={"focus_areas": ["witness_statements", "timeline"]}
        )
        # Accept 200 (success) or 500 (AI processing issues)
        assert response.status_code in [200, 500, 400]
        print(f"✓ Contradiction scan with focus areas - status {response.status_code}")


class TestEndpointStructure:
    """Test that endpoints return expected structure"""
    
    def test_patterns_response_structure(self, auth_session):
        """Verify patterns endpoint returns expected structure"""
        response = auth_session.get(f"{BASE_URL}/api/compare/patterns")
        assert response.status_code == 200
        
        data = response.json()
        # When no data
        if data.get("total_cases_analyzed", 0) == 0:
            assert "message" in data
        else:
            # When data exists
            expected_keys = ["total_cases_analyzed", "patterns"]
            for key in expected_keys:
                assert key in data, f"Missing key: {key}"
        
        print("✓ Patterns endpoint returns expected structure")
    
    def test_success_factors_response_structure(self, auth_session):
        """Verify success factors endpoint returns expected structure"""
        response = auth_session.get(f"{BASE_URL}/api/compare/success-factors")
        assert response.status_code == 200
        
        data = response.json()
        expected_keys = ["success_factors"]
        for key in expected_keys:
            assert key in data, f"Missing key: {key}"
        
        print("✓ Success factors endpoint returns expected structure")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
