"""
Iteration 106 Tests: Auto-Detection Feature Testing
Tests the AI auto-detection of case metadata (offence_category, offence_type, sentence, state)
when calling extract-all-text endpoint.
"""
import pytest
import requests
import os
import time

BASE_URL = 'http://localhost:8001'

class TestAutoDetection:
    """Test auto-detection of case metadata from document content"""
    
    @pytest.fixture(scope="class")
    def session(self):
        """Create authenticated session"""
        s = requests.Session()
        s.headers.update({"Content-Type": "application/json"})
        
        # Login
        login_response = s.post(f"{BASE_URL}/api/auth/login", json={
            "email": "djkingy79@gmail.com",
            "password": "Grubbygrub88"
        })
        assert login_response.status_code == 200, f"Login failed: {login_response.text}"
        data = login_response.json()
        token = data.get("session_token")
        assert token, "No session_token in login response"
        s.cookies.set("session_token", token)
        return s
    
    def test_01_health_check(self, session):
        """Verify API is healthy"""
        response = session.get(f"{BASE_URL}/api/health")
        assert response.status_code == 200
        data = response.json()
        assert data.get("status") == "healthy"
        print("PASS: Health check passed")
    
    def test_02_reset_case_metadata(self, session):
        """Reset case_e7a5b5faf51e to default homicide to test auto-detection"""
        case_id = "case_e7a5b5faf51e"
        
        # First get the current case data to preserve required fields
        get_response = session.get(f"{BASE_URL}/api/cases/{case_id}")
        assert get_response.status_code == 200
        current_case = get_response.json()
        
        # Reset the case metadata to defaults using PUT with full CaseCreate model
        reset_payload = {
            "title": current_case.get("title", "R v Karlsson"),
            "defendant_name": current_case.get("defendant_name", "R Karlsson"),
            "case_number": current_case.get("case_number", ""),
            "court": current_case.get("court", ""),
            "judge": current_case.get("judge", ""),
            "state": "nsw",  # Reset to default
            "offence_category": "homicide",  # Reset to default
            "offence_type": "",  # Clear
            "sentence": "",  # Clear
            "summary": current_case.get("summary", "")
        }
        
        response = session.put(f"{BASE_URL}/api/cases/{case_id}", json=reset_payload)
        assert response.status_code == 200, f"Failed to reset case: {response.text}"
        print(f"PASS: Reset case {case_id} to homicide defaults")
        
        # Verify reset
        get_response = session.get(f"{BASE_URL}/api/cases/{case_id}")
        assert get_response.status_code == 200
        case_data = get_response.json()
        assert case_data.get("offence_category") == "homicide", f"Case not reset to homicide, got: {case_data.get('offence_category')}"
        print(f"PASS: Verified case reset - offence_category: {case_data.get('offence_category')}")
    
    def test_03_extract_all_text_with_auto_detection(self, session):
        """Call extract-all-text and verify auto-detection runs"""
        case_id = "case_e7a5b5faf51e"
        
        # Call extract-all-text with longer timeout (LLM call takes time)
        response = session.post(
            f"{BASE_URL}/api/cases/{case_id}/extract-all-text",
            timeout=120  # 2 minute timeout for LLM processing
        )
        assert response.status_code == 200, f"Extract-all-text failed: {response.text}"
        
        data = response.json()
        print(f"Extract-all-text response: {data}")
        
        # Verify detected_metadata is in response
        assert "detected_metadata" in data, "No detected_metadata in response"
        detected = data.get("detected_metadata", {})
        print(f"Detected metadata: {detected}")
        
        # The case R v Karlsson should be detected as sexual_offences, not homicide
        if detected:
            offence_cat = detected.get("offence_category")
            print(f"Detected offence_category: {offence_cat}")
            # It should NOT be homicide (the default)
            assert offence_cat != "homicide", "Auto-detection failed - still showing homicide instead of actual offence"
            print(f"PASS: Auto-detection returned non-homicide category: {offence_cat}")
        else:
            print("WARNING: detected_metadata is empty - may need document content")
    
    def test_04_verify_case_updated_after_detection(self, session):
        """Verify the case was updated with detected metadata"""
        case_id = "case_e7a5b5faf51e"
        
        response = session.get(f"{BASE_URL}/api/cases/{case_id}")
        assert response.status_code == 200
        
        case_data = response.json()
        print(f"Case data after detection: offence_category={case_data.get('offence_category')}, "
              f"offence_type={case_data.get('offence_type')}, "
              f"sentence={case_data.get('sentence')}, "
              f"state={case_data.get('state')}")
        
        # Verify offence_category is NOT homicide (should be sexual_offences for R v Karlsson)
        offence_cat = case_data.get("offence_category")
        assert offence_cat != "homicide", "Case still shows homicide after auto-detection"
        print(f"PASS: Case offence_category updated to: {offence_cat}")
        
        # Verify other fields are populated
        offence_type = case_data.get("offence_type")
        if offence_type:
            print(f"PASS: offence_type populated: {offence_type}")
        
        sentence = case_data.get("sentence")
        if sentence:
            print(f"PASS: sentence populated: {sentence}")
        
        state = case_data.get("state")
        if state:
            print(f"PASS: state populated: {state}")


class TestBundleExport:
    """Test document bundle export functionality"""
    
    @pytest.fixture(scope="class")
    def session(self):
        """Create authenticated session"""
        s = requests.Session()
        s.headers.update({"Content-Type": "application/json"})
        
        login_response = s.post(f"{BASE_URL}/api/auth/login", json={
            "email": "djkingy79@gmail.com",
            "password": "Grubbygrub88"
        })
        assert login_response.status_code == 200
        data = login_response.json()
        token = data.get("session_token")
        s.cookies.set("session_token", token)
        return s
    
    def test_bundle_export_returns_pdf(self, session):
        """Verify bundle export endpoint returns PDF"""
        case_id = "case_a97ea91f0692"
        
        # Get documents for this case first
        docs_response = session.get(f"{BASE_URL}/api/cases/{case_id}/documents")
        assert docs_response.status_code == 200
        docs = docs_response.json()
        
        if not docs:
            pytest.skip("No documents in test case")
        
        # Use first document
        doc_id = docs[0].get("document_id")
        
        response = session.post(
            f"{BASE_URL}/api/cases/{case_id}/export/bundle",
            json={
                "document_ids": [doc_id],
                "include_toc": True,
                "title": "Test Bundle"
            }
        )
        
        assert response.status_code == 200, f"Bundle export failed: {response.text}"
        assert "application/pdf" in response.headers.get("Content-Type", ""), "Response is not PDF"
        assert len(response.content) > 1000, "PDF content too small"
        print(f"PASS: Bundle export returned PDF ({len(response.content)} bytes)")


class TestCaseDetails:
    """Test case detail retrieval"""
    
    @pytest.fixture(scope="class")
    def session(self):
        """Create authenticated session"""
        s = requests.Session()
        s.headers.update({"Content-Type": "application/json"})
        
        login_response = s.post(f"{BASE_URL}/api/auth/login", json={
            "email": "djkingy79@gmail.com",
            "password": "Grubbygrub88"
        })
        assert login_response.status_code == 200
        data = login_response.json()
        token = data.get("session_token")
        s.cookies.set("session_token", token)
        return s
    
    def test_get_karlsson_case(self, session):
        """Get R v Karlsson case details"""
        case_id = "case_e7a5b5faf51e"
        
        response = session.get(f"{BASE_URL}/api/cases/{case_id}")
        assert response.status_code == 200
        
        case_data = response.json()
        print(f"Case: {case_data.get('case_name')}")
        print(f"  offence_category: {case_data.get('offence_category')}")
        print(f"  offence_type: {case_data.get('offence_type')}")
        print(f"  sentence: {case_data.get('sentence')}")
        print(f"  state: {case_data.get('state')}")
        
        assert case_data.get("case_id") == case_id
        print("PASS: Case retrieved successfully")
    
    def test_get_dummy_murder_case(self, session):
        """Get Dummy Murder case details"""
        case_id = "case_a97ea91f0692"
        
        response = session.get(f"{BASE_URL}/api/cases/{case_id}")
        assert response.status_code == 200
        
        case_data = response.json()
        print(f"Case: {case_data.get('case_name')}")
        print(f"  offence_category: {case_data.get('offence_category')}")
        
        assert case_data.get("case_id") == case_id
        print("PASS: Case retrieved successfully")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
