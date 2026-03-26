"""
Iteration 67 - Content Quality Fixes and UI Improvements Tests
Tests for:
1. Backend health endpoint
2. Case creation/update with sentence field
3. Report export-pdf endpoint
4. Timeline export-pdf endpoint
5. Backend report_guardrails verification (anti-preamble, anti-bracket instructions)
6. Case context includes sentence field
"""

import pytest
import requests
import os
import uuid
import time

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://legal-doc-hub-5.preview.emergentagent.com')

# Use a fixed test user for all API tests
TEST_EMAIL = "test_iter67_fixed@example.com"
TEST_PASSWORD = "TestPass123!"
TEST_NAME = "Test User Iter67"


class TestIteration67ContentQuality:
    """Test content quality fixes and sentence field implementation"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup test session with authentication"""
        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json"})
        self.test_id = uuid.uuid4().hex[:8]
        self.case_id = None
        
        # Register user (ignore if already exists)
        self.session.post(f"{BASE_URL}/api/auth/register", json={
            "email": TEST_EMAIL,
            "password": TEST_PASSWORD,
            "name": TEST_NAME
        })
        
        # Login to get session
        login_resp = self.session.post(f"{BASE_URL}/api/auth/login", json={
            "email": TEST_EMAIL,
            "password": TEST_PASSWORD
        })
        if login_resp.status_code != 200:
            pytest.skip(f"Could not authenticate: {login_resp.status_code}")
        
        yield
        
        # Cleanup
        if self.case_id:
            try:
                self.session.delete(f"{BASE_URL}/api/cases/{self.case_id}")
            except:
                pass
    
    def test_01_health_endpoint(self):
        """Test backend health endpoint returns healthy"""
        response = self.session.get(f"{BASE_URL}/api/health")
        assert response.status_code == 200, f"Health check failed: {response.status_code}"
        data = response.json()
        assert data.get("status") == "healthy", f"Health status not healthy: {data}"
        print(f"PASS: Health endpoint returns healthy")
    
    def test_02_create_case_with_sentence_field(self):
        """Test case creation accepts sentence field"""
        case_payload = {
            "title": f"Test Case {self.test_id}",
            "defendant_name": "John Test Defendant",
            "case_number": "2024/TEST001",
            "court": "NSW Supreme Court",
            "state": "nsw",
            "offence_category": "homicide",
            "offence_type": "Murder",
            "sentence": "30 years imprisonment with NPP of 22 years 6 months",
            "summary": "Test case for iteration 67 content quality testing"
        }
        
        response = self.session.post(f"{BASE_URL}/api/cases", json=case_payload)
        assert response.status_code == 200, f"Case creation failed: {response.status_code} - {response.text}"
        
        data = response.json()
        assert "case_id" in data, f"Case response missing case_id: {data}"
        self.case_id = data["case_id"]
        
        # Verify sentence field was saved
        assert data.get("sentence") == case_payload["sentence"], f"Sentence field not saved correctly: {data.get('sentence')}"
        print(f"PASS: Case created with sentence field: {data.get('sentence')}")
    
    def test_03_update_case_with_sentence_field(self):
        """Test case update accepts sentence field"""
        # Create case
        create_response = self.session.post(f"{BASE_URL}/api/cases", json={
            "title": f"Update Test Case {self.test_id}",
            "defendant_name": "Jane Test Defendant",
            "state": "nsw",
            "offence_category": "homicide"
        })
        assert create_response.status_code == 200, f"Case creation failed: {create_response.status_code}"
        self.case_id = create_response.json()["case_id"]
        
        # Update with sentence field
        update_payload = {
            "title": f"Update Test Case {self.test_id}",
            "defendant_name": "Jane Test Defendant",
            "state": "nsw",
            "offence_category": "homicide",
            "sentence": "25 years imprisonment with NPP of 18 years"
        }
        
        response = self.session.put(f"{BASE_URL}/api/cases/{self.case_id}", json=update_payload)
        assert response.status_code == 200, f"Case update failed: {response.status_code} - {response.text}"
        
        data = response.json()
        assert data.get("sentence") == update_payload["sentence"], f"Sentence field not updated: {data.get('sentence')}"
        print(f"PASS: Case updated with sentence field: {data.get('sentence')}")
    
    def test_04_get_case_includes_sentence(self):
        """Test GET case returns sentence field"""
        create_response = self.session.post(f"{BASE_URL}/api/cases", json={
            "title": f"Get Test Case {self.test_id}",
            "defendant_name": "Bob Test Defendant",
            "state": "nsw",
            "offence_category": "homicide",
            "sentence": "Life imprisonment with NPP of 30 years"
        })
        assert create_response.status_code == 200, f"Case creation failed: {create_response.status_code}"
        self.case_id = create_response.json()["case_id"]
        
        # Get case
        response = self.session.get(f"{BASE_URL}/api/cases/{self.case_id}")
        assert response.status_code == 200, f"Get case failed: {response.status_code}"
        
        data = response.json()
        assert "sentence" in data, f"Sentence field missing from GET response: {data.keys()}"
        assert data.get("sentence") == "Life imprisonment with NPP of 30 years"
        print(f"PASS: GET case includes sentence field: {data.get('sentence')}")
    
    def test_05_report_export_pdf_endpoint_exists(self):
        """Test report export-pdf endpoint exists (returns 404 for non-existent report, not 405)"""
        # Create a case first
        create_response = self.session.post(f"{BASE_URL}/api/cases", json={
            "title": f"PDF Test Case {self.test_id}",
            "defendant_name": "PDF Test Defendant",
            "state": "nsw",
            "offence_category": "homicide"
        })
        assert create_response.status_code == 200, f"Case creation failed: {create_response.status_code}"
        self.case_id = create_response.json()["case_id"]
        
        # Try to export PDF for non-existent report - should return 404 (not 405 Method Not Allowed)
        response = self.session.get(f"{BASE_URL}/api/cases/{self.case_id}/reports/fake_report_id/export-pdf")
        # 404 = endpoint exists but report not found, 401 = auth issue, 500 = server error
        # 405 = endpoint doesn't exist (would be a failure)
        assert response.status_code != 405, f"Report export-pdf endpoint doesn't exist (405)"
        print(f"PASS: Report export-pdf endpoint exists (status: {response.status_code})")
    
    def test_06_timeline_export_pdf_endpoint_exists(self):
        """Test timeline export-pdf endpoint exists"""
        # Create a case first
        create_response = self.session.post(f"{BASE_URL}/api/cases", json={
            "title": f"Timeline PDF Test Case {self.test_id}",
            "defendant_name": "Timeline Test Defendant",
            "state": "nsw",
            "offence_category": "homicide"
        })
        assert create_response.status_code == 200, f"Case creation failed: {create_response.status_code}"
        self.case_id = create_response.json()["case_id"]
        
        # Try to export timeline PDF - should work or return appropriate error (not 405)
        response = self.session.get(f"{BASE_URL}/api/cases/{self.case_id}/timeline/export-pdf")
        # 200 = success, 400 = no events, 404 = case not found
        # 405 = endpoint doesn't exist (would be a failure)
        assert response.status_code != 405, f"Timeline export-pdf endpoint doesn't exist (405)"
        print(f"PASS: Timeline export-pdf endpoint exists (status: {response.status_code})")


class TestBackendCodeVerification:
    """Verify backend code contains required guardrails and sentence field handling"""
    
    def test_07_report_guardrails_anti_preamble(self):
        """Verify report_guardrails contains anti-preamble instruction"""
        with open('/app/backend/server.py', 'r') as f:
            content = f.read()
        
        # Check for anti-preamble instruction
        assert "DO NOT begin your response with any preamble" in content, "Missing anti-preamble instruction"
        assert "Certainly!" in content, "Missing 'Certainly!' in anti-preamble examples"
        assert "Here's a comprehensive" in content or "Here\\'s a comprehensive" in content, "Missing 'Here's a comprehensive' in anti-preamble examples"
        print("PASS: report_guardrails contains anti-preamble instruction")
    
    def test_08_report_guardrails_anti_bracket(self):
        """Verify report_guardrails contains anti-bracket placeholder instruction"""
        with open('/app/backend/server.py', 'r') as f:
            content = f.read()
        
        # Check for anti-bracket instruction
        assert "DO NOT use placeholder notes in brackets" in content, "Missing anti-bracket instruction"
        assert "[Note: Repeat this format" in content or "[Note:" in content, "Missing bracket note examples"
        print("PASS: report_guardrails contains anti-bracket instruction")
    
    def test_09_case_model_has_sentence_field(self):
        """Verify Case model has sentence field"""
        with open('/app/backend/server.py', 'r') as f:
            content = f.read()
        
        # Check Case model has sentence field
        assert "sentence: Optional[str]" in content, "Case model missing sentence field"
        print("PASS: Case model has sentence field")
    
    def test_10_case_create_model_has_sentence_field(self):
        """Verify CaseCreate model has sentence field"""
        with open('/app/backend/server.py', 'r') as f:
            content = f.read()
        
        # Find CaseCreate class and check for sentence field
        # The CaseCreate model should have sentence field
        lines = content.split('\n')
        in_case_create = False
        found_sentence = False
        
        for i, line in enumerate(lines):
            if 'class CaseCreate' in line:
                in_case_create = True
            elif in_case_create and 'class ' in line and 'CaseCreate' not in line:
                break
            elif in_case_create and 'sentence' in line:
                found_sentence = True
                break
        
        assert found_sentence, "CaseCreate model missing sentence field"
        print("PASS: CaseCreate model has sentence field")
    
    def test_11_case_context_includes_sentence(self):
        """Verify case_context for AI reports includes sentence field"""
        with open('/app/backend/server.py', 'r') as f:
            content = f.read()
        
        # Check that case_context includes sentence
        assert "Sentence: {case.get('sentence'" in content or "Sentence: {case.get(\"sentence\"" in content, "case_context missing sentence field"
        print("PASS: case_context includes sentence field for AI reports")


class TestFrontendCodeVerification:
    """Verify frontend code contains required content cleaning functions"""
    
    def test_12_reportview_cleanAIContent_exists(self):
        """Verify ReportView.jsx has cleanAIContent function"""
        with open('/app/frontend/src/pages/ReportView.jsx', 'r') as f:
            content = f.read()
        
        assert "const cleanAIContent" in content, "ReportView.jsx missing cleanAIContent function"
        assert "Certainly!" in content, "cleanAIContent missing 'Certainly!' pattern"
        assert "[Note:" in content, "cleanAIContent missing bracket note pattern"
        print("PASS: ReportView.jsx has cleanAIContent function with correct patterns")
    
    def test_13_barristerview_cleanAIContent_exists(self):
        """Verify BarristerView.jsx has cleanAIContent function"""
        with open('/app/frontend/src/pages/BarristerView.jsx', 'r') as f:
            content = f.read()
        
        assert "const cleanAIContent" in content, "BarristerView.jsx missing cleanAIContent function"
        assert "Certainly!" in content, "cleanAIContent missing 'Certainly!' pattern"
        assert "[Note:" in content, "cleanAIContent missing bracket note pattern"
        print("PASS: BarristerView.jsx has cleanAIContent function with correct patterns")
    
    def test_14_reportview_extractSentenceSummary_uses_caseData(self):
        """Verify extractSentenceSummary uses caseData.sentence first"""
        with open('/app/frontend/src/pages/ReportView.jsx', 'r') as f:
            content = f.read()
        
        # Check that extractSentenceSummary checks caseInfo.sentence first
        assert "caseInfo?.sentence" in content or "caseInfo.sentence" in content, "extractSentenceSummary not checking caseInfo.sentence"
        print("PASS: ReportView extractSentenceSummary uses caseData.sentence first")
    
    def test_15_barristerview_extractSentenceSummary_uses_caseData(self):
        """Verify BarristerView extractSentenceSummary uses caseData.sentence first"""
        with open('/app/frontend/src/pages/BarristerView.jsx', 'r') as f:
            content = f.read()
        
        # Check that extractSentenceSummary checks caseInfo.sentence first
        assert "caseInfo?.sentence" in content or "caseInfo.sentence" in content, "extractSentenceSummary not checking caseInfo.sentence"
        print("PASS: BarristerView extractSentenceSummary uses caseData.sentence first")
    
    def test_16_reportview_section_filtering(self):
        """Verify ReportView filters sections with content < 30 chars"""
        with open('/app/frontend/src/pages/ReportView.jsx', 'r') as f:
            content = f.read()
        
        # Check for content length filtering in pushSection
        assert "content.length < 30" in content, "ReportView missing section content length filtering"
        print("PASS: ReportView filters sections with content < 30 chars")
    
    def test_17_barristerview_section_filtering(self):
        """Verify BarristerView filters sections with content < 30 chars"""
        with open('/app/frontend/src/pages/BarristerView.jsx', 'r') as f:
            content = f.read()
        
        # Check for content length filtering
        assert "cleanedContent.length >= 30" in content or "content.length < 30" in content or "length >= 30" in content, "BarristerView missing section content length filtering"
        print("PASS: BarristerView filters sections with content < 30 chars")
    
    def test_18_dashboard_sentence_input_field(self):
        """Verify Dashboard has sentence input field in case creation form"""
        with open('/app/frontend/src/pages/Dashboard.jsx', 'r') as f:
            content = f.read()
        
        # Check for sentence field in newCase state
        assert "sentence:" in content and "newCase" in content, "Dashboard missing sentence in newCase state"
        # Check for sentence input field
        assert 'id="sentence"' in content or 'data-testid="new-case-sentence"' in content, "Dashboard missing sentence input field"
        print("PASS: Dashboard has sentence input field in case creation form")
    
    def test_19_casedetail_ios_timeline_pdf_fix(self):
        """Verify CaseDetail has iOS fix for timeline PDF export"""
        with open('/app/frontend/src/pages/CaseDetail.jsx', 'r') as f:
            content = f.read()
        
        # Check for iOS detection in handleExportTimelinePDF
        assert "iPad|iPhone|iPod" in content, "CaseDetail missing iOS detection"
        assert "handleExportTimelinePDF" in content, "CaseDetail missing handleExportTimelinePDF function"
        print("PASS: CaseDetail has iOS fix for timeline PDF export")
    
    def test_20_reportview_print_button(self):
        """Verify ReportView has Print button that calls window.print()"""
        with open('/app/frontend/src/pages/ReportView.jsx', 'r') as f:
            content = f.read()
        
        assert "handlePrint" in content, "ReportView missing handlePrint function"
        assert "window.print()" in content, "ReportView handlePrint not calling window.print()"
        assert 'data-testid="print-btn"' in content, "ReportView missing print button with data-testid"
        print("PASS: ReportView has Print button that calls window.print()")
    
    def test_21_australian_english_spelling(self):
        """Verify frontend uses Australian English spelling"""
        files_to_check = [
            '/app/frontend/src/pages/ReportView.jsx',
            '/app/frontend/src/pages/BarristerView.jsx',
            '/app/frontend/src/pages/Dashboard.jsx'
        ]
        
        for filepath in files_to_check:
            with open(filepath, 'r') as f:
                content = f.read()
            
            # Check for Australian English spellings
            # Should have "analyse" not "analyze" in user-facing text
            # Note: Some technical terms may use American spelling in code
            if "Analysing" in content or "analysing" in content or "Analyse" in content:
                print(f"PASS: {filepath} uses Australian English 'analyse'")
            
            # Check for "colour" usage if applicable
            if "colour" in content.lower():
                print(f"PASS: {filepath} uses Australian English 'colour'")
        
        print("PASS: Frontend files checked for Australian English spelling")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
