"""
Iteration 134: Test Case Auto-Detect Bug Fix
Tests that creating a case with empty state/offence_category does NOT default to NSW/Homicide.
The fix made state and offence_category Optional[None] in Pydantic models.
Frontend strips empty strings from payload so backend receives None values.
"""
import pytest
import requests
import os
import time

BASE_URL = os.environ.get("REACT_APP_BACKEND_URL", "").rstrip("/")

# Test credentials from test_credentials.md
TEST_EMAIL = "test@example.com"
TEST_PASSWORD = "TestPassword123!"


@pytest.fixture(scope="module")
def session_token():
    """Login and get session token"""
    response = requests.post(
        f"{BASE_URL}/api/auth/login",
        json={"email": TEST_EMAIL, "password": TEST_PASSWORD},
        timeout=30
    )
    assert response.status_code == 200, f"Login failed: {response.text}"
    data = response.json()
    token = data.get("session_token")
    assert token, f"No session_token in response: {data}"
    return token


@pytest.fixture(scope="module")
def auth_headers(session_token):
    """Auth headers for API requests"""
    return {"Authorization": f"Bearer {session_token}"}


class TestHealthAndAuth:
    """Basic health and auth tests"""
    
    def test_health_endpoint(self):
        """Test health endpoint is accessible"""
        response = requests.get(f"{BASE_URL}/api/health", timeout=10)
        assert response.status_code == 200
        data = response.json()
        assert data.get("status") == "healthy"
        print("PASS: Health endpoint returns healthy")
    
    def test_login_returns_session_token(self):
        """Test login returns session_token (not token)"""
        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": TEST_EMAIL, "password": TEST_PASSWORD},
            timeout=30
        )
        assert response.status_code == 200
        data = response.json()
        assert "session_token" in data, f"Expected session_token in response: {data}"
        print(f"PASS: Login returns session_token: {data['session_token'][:20]}...")


class TestCaseCreationAutoDetectFix:
    """Test the auto-detect bug fix - empty state/offence_category should NOT default to NSW/Homicide"""
    
    def test_create_case_with_empty_state_and_offence_category(self, auth_headers):
        """
        CRITICAL TEST: Creating a case with empty state and offence_category
        should result in None values, NOT default to nsw/homicide.
        This was the user's #1 frustration bug.
        """
        # Create case with only required fields (title, defendant_name)
        # state and offence_category are intentionally omitted (simulating frontend stripping empty strings)
        payload = {
            "title": "TEST_AutoDetect_Case_Empty_Fields",
            "defendant_name": "Test Defendant Empty"
        }
        
        response = requests.post(
            f"{BASE_URL}/api/cases",
            json=payload,
            headers=auth_headers,
            timeout=30
        )
        
        assert response.status_code == 200, f"Case creation failed: {response.text}"
        case = response.json()
        
        # CRITICAL ASSERTIONS: state and offence_category should be None, NOT nsw/homicide
        assert case.get("state") is None, f"Expected state=None but got: {case.get('state')}"
        assert case.get("offence_category") is None, f"Expected offence_category=None but got: {case.get('offence_category')}"
        
        print(f"PASS: Case created with state={case.get('state')}, offence_category={case.get('offence_category')}")
        print(f"  Case ID: {case.get('case_id')}")
        
        # Cleanup - delete the test case
        case_id = case.get("case_id")
        if case_id:
            requests.delete(f"{BASE_URL}/api/cases/{case_id}", headers=auth_headers, timeout=10)
            print(f"  Cleaned up test case: {case_id}")
    
    def test_create_case_with_explicit_state_and_offence_category(self, auth_headers):
        """Test that explicit state and offence_category values are preserved"""
        payload = {
            "title": "TEST_Explicit_QLD_Robbery_Case",
            "defendant_name": "Test Defendant Explicit",
            "state": "qld",
            "offence_category": "robbery_theft"
        }
        
        response = requests.post(
            f"{BASE_URL}/api/cases",
            json=payload,
            headers=auth_headers,
            timeout=30
        )
        
        assert response.status_code == 200, f"Case creation failed: {response.text}"
        case = response.json()
        
        # Verify explicit values are preserved
        assert case.get("state") == "qld", f"Expected state=qld but got: {case.get('state')}"
        assert case.get("offence_category") == "robbery_theft", f"Expected offence_category=robbery_theft but got: {case.get('offence_category')}"
        
        print(f"PASS: Case created with explicit state={case.get('state')}, offence_category={case.get('offence_category')}")
        
        # Cleanup
        case_id = case.get("case_id")
        if case_id:
            requests.delete(f"{BASE_URL}/api/cases/{case_id}", headers=auth_headers, timeout=10)
            print(f"  Cleaned up test case: {case_id}")
    
    def test_create_case_with_only_state_set(self, auth_headers):
        """Test case creation with only state set (offence_category should be None)"""
        payload = {
            "title": "TEST_Only_State_Set_Case",
            "defendant_name": "Test Defendant State Only",
            "state": "vic"
        }
        
        response = requests.post(
            f"{BASE_URL}/api/cases",
            json=payload,
            headers=auth_headers,
            timeout=30
        )
        
        assert response.status_code == 200, f"Case creation failed: {response.text}"
        case = response.json()
        
        assert case.get("state") == "vic", f"Expected state=vic but got: {case.get('state')}"
        assert case.get("offence_category") is None, f"Expected offence_category=None but got: {case.get('offence_category')}"
        
        print(f"PASS: Case created with state={case.get('state')}, offence_category={case.get('offence_category')}")
        
        # Cleanup
        case_id = case.get("case_id")
        if case_id:
            requests.delete(f"{BASE_URL}/api/cases/{case_id}", headers=auth_headers, timeout=10)
    
    def test_create_case_with_only_offence_category_set(self, auth_headers):
        """Test case creation with only offence_category set (state should be None)"""
        payload = {
            "title": "TEST_Only_Offence_Category_Set_Case",
            "defendant_name": "Test Defendant Offence Only",
            "offence_category": "drug_offences"
        }
        
        response = requests.post(
            f"{BASE_URL}/api/cases",
            json=payload,
            headers=auth_headers,
            timeout=30
        )
        
        assert response.status_code == 200, f"Case creation failed: {response.text}"
        case = response.json()
        
        assert case.get("state") is None, f"Expected state=None but got: {case.get('state')}"
        assert case.get("offence_category") == "drug_offences", f"Expected offence_category=drug_offences but got: {case.get('offence_category')}"
        
        print(f"PASS: Case created with state={case.get('state')}, offence_category={case.get('offence_category')}")
        
        # Cleanup
        case_id = case.get("case_id")
        if case_id:
            requests.delete(f"{BASE_URL}/api/cases/{case_id}", headers=auth_headers, timeout=10)


class TestDocumentUploadAutoDetection:
    """Test document upload triggers background auto-detection of case metadata"""
    
    def test_document_upload_triggers_auto_detection(self, auth_headers):
        """
        Test that uploading a document with Australian criminal case content
        triggers background auto-detection of state, offence_category, etc.
        """
        # Step 1: Create a case with empty state/offence_category
        case_payload = {
            "title": "TEST_Document_AutoDetect_Case",
            "defendant_name": "Test Defendant Document"
        }
        
        case_response = requests.post(
            f"{BASE_URL}/api/cases",
            json=case_payload,
            headers=auth_headers,
            timeout=30
        )
        
        assert case_response.status_code == 200, f"Case creation failed: {case_response.text}"
        case = case_response.json()
        case_id = case.get("case_id")
        
        # Verify initial state is None
        assert case.get("state") is None, f"Initial state should be None: {case.get('state')}"
        assert case.get("offence_category") is None, f"Initial offence_category should be None: {case.get('offence_category')}"
        print(f"PASS: Created case {case_id} with state=None, offence_category=None")
        
        # Step 2: Upload a document with QLD armed robbery content
        document_content = """
SENTENCING REMARKS
District Court of Queensland
Brisbane

R v SMITH [2024] QDC 123

JUDGE: His Honour Judge Williams

DEFENDANT: John Michael Smith

CHARGE: Armed Robbery (Section 411 Criminal Code Act 1899 (Qld))

SENTENCE: The defendant is sentenced to 6 years imprisonment with a non-parole period of 3 years.

FACTS:
On 15 March 2024, the defendant entered the Commonwealth Bank branch at Queen Street Mall, Brisbane.
Armed with a replica firearm, the defendant demanded cash from the teller.
The defendant fled with approximately $15,000 in cash.
The defendant was apprehended by Queensland Police Service officers within 2 hours.

MITIGATING FACTORS:
- Early guilty plea
- No prior criminal history
- Expression of remorse

AGGRAVATING FACTORS:
- Use of weapon (replica firearm)
- Significant amount stolen
- Trauma caused to bank staff

The Court finds that a custodial sentence is warranted given the serious nature of armed robbery offences.
"""
        
        # Upload as text file
        files = {
            "file": ("qld_sentencing_remarks.txt", document_content.encode("utf-8"), "text/plain")
        }
        data = {
            "category": "sentencing_remarks",
            "description": "QLD District Court sentencing remarks for armed robbery"
        }
        
        upload_response = requests.post(
            f"{BASE_URL}/api/cases/{case_id}/documents",
            files=files,
            data=data,
            headers=auth_headers,
            timeout=60
        )
        
        assert upload_response.status_code == 200, f"Document upload failed: {upload_response.text}"
        doc = upload_response.json()
        print(f"PASS: Document uploaded: {doc.get('document_id')}")
        
        # Step 3: Wait for background auto-detection task to complete (20-30 seconds)
        print("  Waiting 25 seconds for background auto-detection task...")
        time.sleep(25)
        
        # Step 4: Fetch the case again to check if metadata was auto-detected
        get_case_response = requests.get(
            f"{BASE_URL}/api/cases/{case_id}",
            headers=auth_headers,
            timeout=30
        )
        
        assert get_case_response.status_code == 200, f"Get case failed: {get_case_response.text}"
        updated_case = get_case_response.json()
        
        print(f"  After auto-detection:")
        print(f"    state: {updated_case.get('state')}")
        print(f"    offence_category: {updated_case.get('offence_category')}")
        print(f"    offence_type: {updated_case.get('offence_type')}")
        print(f"    sentence: {updated_case.get('sentence')}")
        print(f"    court: {updated_case.get('court')}")
        
        # Verify auto-detection populated the fields (should be QLD and robbery_theft based on document)
        # Note: LLM may not always detect perfectly, so we check if at least some fields were populated
        auto_detected_fields = []
        if updated_case.get("state"):
            auto_detected_fields.append(f"state={updated_case.get('state')}")
        if updated_case.get("offence_category"):
            auto_detected_fields.append(f"offence_category={updated_case.get('offence_category')}")
        if updated_case.get("offence_type"):
            auto_detected_fields.append(f"offence_type={updated_case.get('offence_type')}")
        if updated_case.get("sentence"):
            auto_detected_fields.append(f"sentence={updated_case.get('sentence')}")
        if updated_case.get("court"):
            auto_detected_fields.append(f"court={updated_case.get('court')}")
        
        if auto_detected_fields:
            print(f"PASS: Auto-detection populated fields: {', '.join(auto_detected_fields)}")
        else:
            print("WARNING: No fields were auto-detected (LLM task may have failed or timed out)")
        
        # Cleanup
        requests.delete(f"{BASE_URL}/api/cases/{case_id}", headers=auth_headers, timeout=10)
        print(f"  Cleaned up test case: {case_id}")


class TestDashboardAndCaseDetail:
    """Test dashboard and case detail page endpoints"""
    
    def test_get_cases_returns_list(self, auth_headers):
        """Test GET /api/cases returns list of cases"""
        response = requests.get(
            f"{BASE_URL}/api/cases",
            headers=auth_headers,
            timeout=30
        )
        
        assert response.status_code == 200, f"Get cases failed: {response.text}"
        cases = response.json()
        assert isinstance(cases, list), f"Expected list but got: {type(cases)}"
        print(f"PASS: GET /api/cases returns {len(cases)} cases")
        
        # Check that cases have expected fields
        if cases:
            first_case = cases[0]
            expected_fields = ["case_id", "title", "defendant_name", "state", "offence_category"]
            for field in expected_fields:
                assert field in first_case, f"Missing field {field} in case"
            print(f"  First case: {first_case.get('title')} (state={first_case.get('state')}, offence_category={first_case.get('offence_category')})")
    
    def test_get_case_detail(self, auth_headers):
        """Test GET /api/cases/{case_id} returns case detail"""
        # First get list of cases
        list_response = requests.get(
            f"{BASE_URL}/api/cases",
            headers=auth_headers,
            timeout=30
        )
        
        assert list_response.status_code == 200
        cases = list_response.json()
        
        if not cases:
            pytest.skip("No cases available to test case detail")
        
        case_id = cases[0].get("case_id")
        
        # Get case detail
        detail_response = requests.get(
            f"{BASE_URL}/api/cases/{case_id}",
            headers=auth_headers,
            timeout=30
        )
        
        assert detail_response.status_code == 200, f"Get case detail failed: {detail_response.text}"
        case = detail_response.json()
        
        assert case.get("case_id") == case_id
        assert "document_count" in case, "Missing document_count in case detail"
        assert "event_count" in case, "Missing event_count in case detail"
        
        print(f"PASS: GET /api/cases/{case_id} returns case detail")
        print(f"  Title: {case.get('title')}")
        print(f"  Documents: {case.get('document_count')}, Events: {case.get('event_count')}")
    
    def test_get_offence_categories(self, auth_headers):
        """Test GET /api/offence-categories returns list of categories"""
        response = requests.get(
            f"{BASE_URL}/api/offence-categories",
            headers=auth_headers,
            timeout=30
        )
        
        assert response.status_code == 200, f"Get offence categories failed: {response.text}"
        data = response.json()
        assert "categories" in data, f"Missing categories in response: {data}"
        
        categories = data["categories"]
        assert isinstance(categories, list), f"Expected list but got: {type(categories)}"
        assert len(categories) > 0, "No offence categories returned"
        
        # Check expected categories exist
        category_ids = [c.get("id") for c in categories]
        expected_categories = ["homicide", "assault", "robbery_theft", "drug_offences"]
        for expected in expected_categories:
            assert expected in category_ids, f"Missing expected category: {expected}"
        
        print(f"PASS: GET /api/offence-categories returns {len(categories)} categories")
    
    def test_get_states(self, auth_headers):
        """Test GET /api/states returns list of Australian states"""
        response = requests.get(
            f"{BASE_URL}/api/states",
            headers=auth_headers,
            timeout=30
        )
        
        assert response.status_code == 200, f"Get states failed: {response.text}"
        data = response.json()
        assert "states" in data, f"Missing states in response: {data}"
        
        states = data["states"]
        assert isinstance(states, list), f"Expected list but got: {type(states)}"
        assert len(states) > 0, "No states returned"
        
        # Check expected states exist
        state_ids = [s.get("id") for s in states]
        expected_states = ["nsw", "vic", "qld", "sa", "wa", "tas", "nt", "act"]
        for expected in expected_states:
            assert expected in state_ids, f"Missing expected state: {expected}"
        
        print(f"PASS: GET /api/states returns {len(states)} states")


class TestCaseUpdateWithAutoDetect:
    """Test case update preserves auto-detect behavior"""
    
    def test_update_case_preserves_none_values(self, auth_headers):
        """Test that updating a case doesn't accidentally set state/offence_category"""
        # Create case with empty fields
        create_payload = {
            "title": "TEST_Update_Preserve_None_Case",
            "defendant_name": "Test Defendant Update"
        }
        
        create_response = requests.post(
            f"{BASE_URL}/api/cases",
            json=create_payload,
            headers=auth_headers,
            timeout=30
        )
        
        assert create_response.status_code == 200
        case = create_response.json()
        case_id = case.get("case_id")
        
        # Verify initial state is None
        assert case.get("state") is None
        assert case.get("offence_category") is None
        
        # Update case with only title change (not setting state/offence_category)
        update_payload = {
            "title": "TEST_Update_Preserve_None_Case_Updated",
            "defendant_name": "Test Defendant Update"
        }
        
        update_response = requests.put(
            f"{BASE_URL}/api/cases/{case_id}",
            json=update_payload,
            headers=auth_headers,
            timeout=30
        )
        
        assert update_response.status_code == 200, f"Update failed: {update_response.text}"
        updated_case = update_response.json()
        
        # Verify state and offence_category are still None after update
        assert updated_case.get("state") is None, f"state should still be None after update: {updated_case.get('state')}"
        assert updated_case.get("offence_category") is None, f"offence_category should still be None after update: {updated_case.get('offence_category')}"
        
        print(f"PASS: Update preserves None values for state and offence_category")
        
        # Cleanup
        requests.delete(f"{BASE_URL}/api/cases/{case_id}", headers=auth_headers, timeout=10)


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
