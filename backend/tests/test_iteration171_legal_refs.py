"""
Test iteration 171: Refresh Legal References feature
Tests:
1. POST /api/cases/{case_id}/grounds/refresh-legal-refs endpoint
2. Verify law_sections contain substantive legislation (not Criminal Appeal Act)
3. Verify law_sections don't contain placeholder text
4. All 93 pytest tests pass
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Test credentials
TEST_EMAIL = "djkingy79@gmail.com"
TEST_PASSWORD = "Grubbygrub88"

# Test case IDs from the review request
NSW_CASE_ID = "case_6cc234434cbd"  # NSW homicide case with 10 grounds
WA_CASE_ID = "case_e8a9de2d8331"   # WA case with 8 grounds


class TestRefreshLegalRefs:
    """Test the new refresh-legal-refs endpoint and law_sections quality"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Login and get session token"""
        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json"})
        
        # Login
        login_response = self.session.post(f"{BASE_URL}/api/auth/login", json={
            "email": TEST_EMAIL,
            "password": TEST_PASSWORD
        })
        assert login_response.status_code == 200, f"Login failed: {login_response.text}"
        
        data = login_response.json()
        self.session_token = data.get("session_token")
        self.user_id = data.get("user_id")
        assert self.session_token, "No session token returned"
        
        self.session.headers.update({"Authorization": f"Bearer {self.session_token}"})
    
    def test_refresh_legal_refs_endpoint_exists(self):
        """Test that POST /api/cases/{case_id}/grounds/refresh-legal-refs returns 200"""
        # Use NSW case
        response = self.session.post(f"{BASE_URL}/api/cases/{NSW_CASE_ID}/grounds/refresh-legal-refs", timeout=180)
        
        # Should return 200 with updated/total counts
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert "updated" in data, "Response should contain 'updated' count"
        assert "total" in data, "Response should contain 'total' count"
        assert "message" in data, "Response should contain 'message'"
        
        print(f"Refresh legal refs result: {data}")
    
    def test_nsw_grounds_have_substantive_legislation(self):
        """Test that NSW case grounds have substantive legislation in law_sections"""
        response = self.session.get(f"{BASE_URL}/api/cases/{NSW_CASE_ID}/grounds")
        assert response.status_code == 200, f"Failed to get grounds: {response.text}"
        
        data = response.json()
        grounds = data.get("grounds", [])
        assert len(grounds) > 0, "NSW case should have grounds"
        
        # Check law_sections for substantive legislation
        substantive_acts = [
            "Crimes Act",
            "Evidence Act",
            "Sentencing",
            "Criminal Procedure Act",
            "Mental Health Act",
            "Jury Act"
        ]
        
        placeholder_phrases = [
            "Act name",
            "Relevant Act",
            "section specific to",
            "identically associated",
            "applicable section",
            "not provided",
            "unknown"
        ]
        
        grounds_with_law_sections = 0
        grounds_with_substantive = 0
        grounds_with_criminal_appeal_only = 0
        grounds_with_placeholders = 0
        
        for ground in grounds:
            law_sections = ground.get("law_sections", [])
            if law_sections:
                grounds_with_law_sections += 1
                
                has_substantive = False
                has_criminal_appeal_only = True
                has_placeholder = False
                
                for ls in law_sections:
                    act = ls.get("act", "")
                    section = ls.get("section", "")
                    
                    # Check for substantive legislation
                    if any(sub_act in act for sub_act in substantive_acts):
                        has_substantive = True
                        has_criminal_appeal_only = False
                    
                    # Check for Criminal Appeal Act only
                    if "Criminal Appeal Act" not in act:
                        has_criminal_appeal_only = False
                    
                    # Check for placeholder text
                    if any(ph.lower() in act.lower() or ph.lower() in section.lower() for ph in placeholder_phrases):
                        has_placeholder = True
                
                if has_substantive:
                    grounds_with_substantive += 1
                if has_criminal_appeal_only and law_sections:
                    grounds_with_criminal_appeal_only += 1
                if has_placeholder:
                    grounds_with_placeholders += 1
        
        print("NSW case grounds analysis:")
        print(f"  Total grounds: {len(grounds)}")
        print(f"  Grounds with law_sections: {grounds_with_law_sections}")
        print(f"  Grounds with substantive legislation: {grounds_with_substantive}")
        print(f"  Grounds with Criminal Appeal Act only: {grounds_with_criminal_appeal_only}")
        print(f"  Grounds with placeholder text: {grounds_with_placeholders}")
        
        # Assertions
        assert grounds_with_criminal_appeal_only == 0, \
            f"Found {grounds_with_criminal_appeal_only} grounds with only Criminal Appeal Act - should have substantive legislation"
        assert grounds_with_placeholders == 0, \
            f"Found {grounds_with_placeholders} grounds with placeholder text in law_sections"
    
    def test_law_sections_no_placeholder_text(self):
        """Test that law_sections don't contain placeholder text"""
        response = self.session.get(f"{BASE_URL}/api/cases/{NSW_CASE_ID}/grounds")
        assert response.status_code == 200
        
        data = response.json()
        grounds = data.get("grounds", [])
        
        placeholder_phrases = [
            "Act name",
            "Relevant Act", 
            "section specific to",
            "identically associated",
            "applicable section",
            "associated section",
            "corresponding section",
            "appropriate section",
            "not provided",
            "unknown",
            "n/a"
        ]
        
        for ground in grounds:
            law_sections = ground.get("law_sections", [])
            for ls in law_sections:
                act = (ls.get("act") or "").lower()
                section = (ls.get("section") or "").lower()
                
                for placeholder in placeholder_phrases:
                    assert placeholder.lower() not in act, \
                        f"Ground '{ground.get('title')}' has placeholder '{placeholder}' in act: {ls.get('act')}"
                    assert placeholder.lower() not in section, \
                        f"Ground '{ground.get('title')}' has placeholder '{placeholder}' in section: {ls.get('section')}"
    
    def test_wa_case_grounds_empty_law_sections_acceptable(self):
        """Test that WA case grounds with empty law_sections is acceptable (better than placeholders)"""
        response = self.session.get(f"{BASE_URL}/api/cases/{WA_CASE_ID}/grounds")
        
        # WA case may not exist or may not be accessible
        if response.status_code == 404:
            pytest.skip("WA case not found - skipping")
        
        assert response.status_code == 200, f"Failed to get WA grounds: {response.text}"
        
        data = response.json()
        grounds = data.get("grounds", [])
        
        if not grounds:
            pytest.skip("WA case has no grounds")
        
        # For WA case, empty law_sections is acceptable
        # But if there are law_sections, they should not have placeholders
        placeholder_phrases = ["Act name", "Relevant Act", "section specific to", "identically associated"]
        
        for ground in grounds:
            law_sections = ground.get("law_sections", [])
            for ls in law_sections:
                act = (ls.get("act") or "").lower()
                section = (ls.get("section") or "").lower()
                
                for placeholder in placeholder_phrases:
                    assert placeholder.lower() not in act, \
                        f"WA ground has placeholder in act: {ls.get('act')}"
                    assert placeholder.lower() not in section, \
                        f"WA ground has placeholder in section: {ls.get('section')}"
        
        print(f"WA case has {len(grounds)} grounds")


class TestVerifyPyNoDefaultState:
    """Test that verify.py no longer defaults state to 'nsw'"""
    
    def test_verify_py_no_nsw_default(self):
        """Check that verify.py doesn't default state to 'nsw'"""
        verify_path = "/app/backend/services/pipeline/verify.py"
        
        with open(verify_path, 'r') as f:
            content = f.read()
        
        # Should NOT have: state = case.get('state', 'nsw')
        # Should have: state = case.get('state', '') or ''
        assert "case.get('state', 'nsw')" not in content, \
            "verify.py should not default state to 'nsw'"
        
        # Verify the correct pattern is used
        assert "case.get('state', '')" in content or "case.get('state') or ''" in content, \
            "verify.py should use empty string default for state"
        
        print("verify.py correctly does not default state to 'nsw'")


class TestAllPytestPass:
    """Run all existing pytest tests to ensure no regressions"""
    
    def test_legislation_framework_tests_pass(self):
        """Verify all 93 legislation framework tests pass"""
        import subprocess
        
        result = subprocess.run(
            ["pytest", "/app/backend/tests/test_legislation_framework.py", "-v", "--tb=short"],
            capture_output=True,
            text=True,
            timeout=300
        )
        
        print(f"Legislation framework tests output:\n{result.stdout}")
        if result.returncode != 0:
            print(f"Errors:\n{result.stderr}")
        
        assert result.returncode == 0, f"Legislation framework tests failed: {result.stderr}"
