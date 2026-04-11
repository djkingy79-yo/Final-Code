"""
Iteration 182: Jurisdiction Flow Fixes Testing
Tests for federal/CTH jurisdiction support and metadata warnings in case detail API.

Key test cases:
1. APPELLATE_PATHWAYS contains 'federal' key with Judiciary Act reference
2. AUSTRALIAN_STATES contains 'federal' key with CTH abbreviation
3. validate_jurisdiction_completeness('federal', 'drug_offences') returns federal jurisdiction warning
4. get_offence_context for federal case shows 'Commonwealth/Federal (CTH)' jurisdiction
5. GET /api/cases/{case_id} returns metadata_warnings and jurisdiction_warnings arrays
6. Case with missing state returns metadata_warnings containing 'State/jurisdiction is not set'
7. Case with missing offence_category returns warning about missing offence category
8. Case with missing offence_type returns warning about specific offence type not set
9. Case with all metadata filled returns empty metadata_warnings
"""

import pytest
import requests
import os
import sys

# Add backend to path for imports
sys.path.insert(0, '/app/backend')

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://criminal-appeals-au-2.preview.emergentagent.com').rstrip('/')

# Test credentials
TEST_EMAIL = "djkingy79@gmail.com"
TEST_PASSWORD = "Grubbygrub88"


@pytest.fixture(scope="module")
def auth_token():
    """Get authentication token for API tests"""
    response = requests.post(f"{BASE_URL}/api/auth/login", json={
        "email": TEST_EMAIL,
        "password": TEST_PASSWORD
    })
    if response.status_code == 200:
        data = response.json()
        return data.get("session_token")
    pytest.skip(f"Authentication failed: {response.status_code} - {response.text}")


@pytest.fixture(scope="module")
def authenticated_client(auth_token):
    """Session with auth header"""
    session = requests.Session()
    session.headers.update({
        "Content-Type": "application/json",
        "Authorization": f"Bearer {auth_token}"
    })
    return session


class TestAppellatePathways:
    """Test APPELLATE_PATHWAYS contains federal entry"""
    
    def test_federal_in_appellate_pathways(self):
        """APPELLATE_PATHWAYS should contain 'federal' key with Judiciary Act reference"""
        from services.pipeline.classify import APPELLATE_PATHWAYS
        
        assert "federal" in APPELLATE_PATHWAYS, "APPELLATE_PATHWAYS missing 'federal' key"
        federal_pathway = APPELLATE_PATHWAYS["federal"]
        assert "Judiciary Act" in federal_pathway, f"Federal pathway should reference Judiciary Act, got: {federal_pathway}"
        assert "35A" in federal_pathway, f"Federal pathway should reference s 35A, got: {federal_pathway}"
        print(f"PASS: APPELLATE_PATHWAYS['federal'] = {federal_pathway}")


class TestAustralianStates:
    """Test AUSTRALIAN_STATES contains federal entry"""
    
    def test_federal_in_australian_states(self):
        """AUSTRALIAN_STATES should contain 'federal' key with CTH abbreviation"""
        from offence_framework import AUSTRALIAN_STATES
        
        assert "federal" in AUSTRALIAN_STATES, "AUSTRALIAN_STATES missing 'federal' key"
        federal_state = AUSTRALIAN_STATES["federal"]
        assert federal_state.get("abbreviation") == "CTH", f"Federal abbreviation should be CTH, got: {federal_state.get('abbreviation')}"
        assert "Commonwealth" in federal_state.get("name", ""), f"Federal name should contain 'Commonwealth', got: {federal_state.get('name')}"
        print(f"PASS: AUSTRALIAN_STATES['federal'] = {federal_state}")


class TestStateFrameworks:
    """Test STATE_FRAMEWORKS contains federal entry"""
    
    def test_federal_in_state_frameworks(self):
        """STATE_FRAMEWORKS should contain 'federal' key"""
        from services.offence_helpers import STATE_FRAMEWORKS
        
        assert "federal" in STATE_FRAMEWORKS, "STATE_FRAMEWORKS missing 'federal' key"
        print(f"PASS: STATE_FRAMEWORKS contains 'federal' key")


class TestValidateJurisdictionCompleteness:
    """Test validate_jurisdiction_completeness function for federal cases"""
    
    def test_federal_jurisdiction_warning(self):
        """validate_jurisdiction_completeness('federal', 'drug_offences') should return federal jurisdiction warning"""
        from services.offence_helpers import validate_jurisdiction_completeness
        
        warnings = validate_jurisdiction_completeness('federal', 'drug_offences')
        
        assert isinstance(warnings, list), f"Expected list, got {type(warnings)}"
        assert len(warnings) > 0, "Expected at least one warning for federal jurisdiction"
        
        # Check for federal jurisdiction note
        federal_warning_found = any("FEDERAL JURISDICTION" in w or "federal" in w.lower() for w in warnings)
        assert federal_warning_found, f"Expected federal jurisdiction warning, got: {warnings}"
        print(f"PASS: validate_jurisdiction_completeness('federal', 'drug_offences') returned {len(warnings)} warnings")
        for w in warnings:
            print(f"  - {w[:100]}...")
    
    def test_missing_jurisdiction_warning(self):
        """validate_jurisdiction_completeness with empty state should return jurisdiction not confirmed warning"""
        from services.offence_helpers import validate_jurisdiction_completeness
        
        warnings = validate_jurisdiction_completeness('', 'drug_offences')
        
        assert isinstance(warnings, list), f"Expected list, got {type(warnings)}"
        assert len(warnings) > 0, "Expected at least one warning for missing jurisdiction"
        
        # Check for jurisdiction not confirmed warning
        not_confirmed_found = any("NOT CONFIRMED" in w for w in warnings)
        assert not_confirmed_found, f"Expected 'NOT CONFIRMED' warning, got: {warnings}"
        print(f"PASS: validate_jurisdiction_completeness('', 'drug_offences') returned jurisdiction not confirmed warning")


class TestGetOffenceContext:
    """Test get_offence_context function for federal cases"""
    
    def test_federal_offence_context(self):
        """get_offence_context for federal case should show 'Commonwealth/Federal (CTH)' jurisdiction"""
        from services.offence_helpers import get_offence_context
        
        case = {
            "state": "federal",
            "offence_category": "drug_offences",
            "offence_type": "Drug Importation"
        }
        
        context = get_offence_context(case)
        
        assert isinstance(context, str), f"Expected string, got {type(context)}"
        assert "Commonwealth" in context or "Federal" in context or "CTH" in context, \
            f"Expected federal jurisdiction reference in context, got: {context[:500]}..."
        print(f"PASS: get_offence_context for federal case contains federal jurisdiction reference")


class TestCaseDetailAPIWarnings:
    """Test GET /api/cases/{case_id} returns metadata_warnings and jurisdiction_warnings"""
    
    def test_case_with_missing_state_returns_metadata_warning(self, authenticated_client):
        """Case with missing state should return metadata_warnings containing 'State/jurisdiction is not set'"""
        # First, get list of cases to find one with missing state, or create one
        response = authenticated_client.get(f"{BASE_URL}/api/cases")
        assert response.status_code == 200, f"Failed to get cases: {response.status_code}"
        
        cases = response.json()
        
        # Find case_d0f0469d5cab (state=None, offence_category=None) as mentioned in context
        test_case_id = "case_d0f0469d5cab"
        
        # Get case detail
        response = authenticated_client.get(f"{BASE_URL}/api/cases/{test_case_id}")
        
        if response.status_code == 404:
            pytest.skip(f"Test case {test_case_id} not found - skipping")
        
        assert response.status_code == 200, f"Failed to get case: {response.status_code}"
        
        case_data = response.json()
        
        # Check metadata_warnings exists
        assert "metadata_warnings" in case_data, "Case response missing 'metadata_warnings' field"
        metadata_warnings = case_data["metadata_warnings"]
        assert isinstance(metadata_warnings, list), f"metadata_warnings should be list, got {type(metadata_warnings)}"
        
        # Check jurisdiction_warnings exists
        assert "jurisdiction_warnings" in case_data, "Case response missing 'jurisdiction_warnings' field"
        jurisdiction_warnings = case_data["jurisdiction_warnings"]
        assert isinstance(jurisdiction_warnings, list), f"jurisdiction_warnings should be list, got {type(jurisdiction_warnings)}"
        
        # If state is missing, should have state warning
        if not case_data.get("state"):
            state_warning_found = any("State/jurisdiction is not set" in w for w in metadata_warnings)
            assert state_warning_found, f"Expected 'State/jurisdiction is not set' warning, got: {metadata_warnings}"
            print(f"PASS: Case with missing state has state warning in metadata_warnings")
        
        # If offence_category is missing, should have offence category warning
        if not case_data.get("offence_category"):
            offence_warning_found = any("Offence category is not set" in w for w in metadata_warnings)
            assert offence_warning_found, f"Expected 'Offence category is not set' warning, got: {metadata_warnings}"
            print(f"PASS: Case with missing offence_category has offence category warning")
        
        # If offence_type is missing, should have offence type warning
        if not case_data.get("offence_type"):
            offence_type_warning_found = any("offence type is not set" in w for w in metadata_warnings)
            assert offence_type_warning_found, f"Expected 'offence type is not set' warning, got: {metadata_warnings}"
            print(f"PASS: Case with missing offence_type has offence type warning")
        
        print(f"Case {test_case_id}: metadata_warnings={len(metadata_warnings)}, jurisdiction_warnings={len(jurisdiction_warnings)}")
    
    def test_case_with_complete_metadata_returns_empty_warnings(self, authenticated_client):
        """Case with all metadata filled (state=nsw, offence_category=homicide, offence_type=murder) should return empty metadata_warnings"""
        # Use case_f8bf63e9dcbe as mentioned in context
        test_case_id = "case_f8bf63e9dcbe"
        
        response = authenticated_client.get(f"{BASE_URL}/api/cases/{test_case_id}")
        
        if response.status_code == 404:
            pytest.skip(f"Test case {test_case_id} not found - skipping")
        
        assert response.status_code == 200, f"Failed to get case: {response.status_code}"
        
        case_data = response.json()
        
        # Check metadata_warnings exists
        assert "metadata_warnings" in case_data, "Case response missing 'metadata_warnings' field"
        metadata_warnings = case_data["metadata_warnings"]
        
        # If case has all metadata, warnings should be empty
        if case_data.get("state") and case_data.get("offence_category") and case_data.get("offence_type"):
            assert len(metadata_warnings) == 0, f"Case with complete metadata should have empty metadata_warnings, got: {metadata_warnings}"
            print(f"PASS: Case with complete metadata has empty metadata_warnings")
        else:
            print(f"INFO: Case {test_case_id} has incomplete metadata: state={case_data.get('state')}, offence_category={case_data.get('offence_category')}, offence_type={case_data.get('offence_type')}")
    
    def test_case_with_partial_metadata(self, authenticated_client):
        """Case with state=nsw, offence_category=homicide, offence_type=None should show 1 metadata warning"""
        # Use case_44b2047065b2 as mentioned in context
        test_case_id = "case_44b2047065b2"
        
        response = authenticated_client.get(f"{BASE_URL}/api/cases/{test_case_id}")
        
        if response.status_code == 404:
            pytest.skip(f"Test case {test_case_id} not found - skipping")
        
        assert response.status_code == 200, f"Failed to get case: {response.status_code}"
        
        case_data = response.json()
        
        # Check metadata_warnings exists
        assert "metadata_warnings" in case_data, "Case response missing 'metadata_warnings' field"
        metadata_warnings = case_data["metadata_warnings"]
        
        # If case has state and offence_category but no offence_type, should have 1 warning
        if case_data.get("state") and case_data.get("offence_category") and not case_data.get("offence_type"):
            assert len(metadata_warnings) == 1, f"Case with missing offence_type only should have 1 warning, got: {metadata_warnings}"
            offence_type_warning_found = any("offence type is not set" in w for w in metadata_warnings)
            assert offence_type_warning_found, f"Expected 'offence type is not set' warning, got: {metadata_warnings}"
            print(f"PASS: Case with missing offence_type only has 1 metadata warning about offence_type")
        else:
            print(f"INFO: Case {test_case_id} metadata: state={case_data.get('state')}, offence_category={case_data.get('offence_category')}, offence_type={case_data.get('offence_type')}")


class TestLoginStillWorks:
    """Verify login endpoint still works correctly"""
    
    def test_login_valid_credentials(self):
        """Login with valid credentials should return session_token"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": TEST_EMAIL,
            "password": TEST_PASSWORD
        })
        
        assert response.status_code == 200, f"Login failed: {response.status_code} - {response.text}"
        data = response.json()
        assert "session_token" in data, f"Response missing session_token: {data}"
        print(f"PASS: Login returns session_token")
    
    def test_login_invalid_credentials(self):
        """Login with invalid credentials should return 401"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": "invalid@example.com",
            "password": "wrongpassword"
        })
        
        assert response.status_code == 401, f"Expected 401, got: {response.status_code}"
        print(f"PASS: Login with invalid credentials returns 401")


class TestPaymentHistoryStillAccessible:
    """Verify Payment History page is still accessible"""
    
    def test_payment_history_endpoint(self, authenticated_client):
        """GET /api/payments/history should return payment history"""
        response = authenticated_client.get(f"{BASE_URL}/api/payments/history")
        
        assert response.status_code == 200, f"Payment history failed: {response.status_code} - {response.text}"
        data = response.json()
        # Payment history returns dict with 'payments' key
        assert isinstance(data, dict), f"Expected dict, got {type(data)}"
        assert "payments" in data, f"Response missing 'payments' key: {data.keys()}"
        payments = data["payments"]
        assert isinstance(payments, list), f"Expected payments to be list, got {type(payments)}"
        print(f"PASS: Payment history endpoint returns {len(payments)} payments")
    
    def test_payment_history_requires_auth(self):
        """GET /api/payments/history without auth should return 401"""
        response = requests.get(f"{BASE_URL}/api/payments/history")
        
        assert response.status_code == 401, f"Expected 401, got: {response.status_code}"
        print(f"PASS: Payment history requires authentication")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
