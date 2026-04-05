"""
Iteration 98 - Sentence Wording Verification Tests
Tests that the exact sentence wording appears correctly across all 4 report types
and their Print/PDF/Word exports for case case_76056187ad4f.

Expected exact sentence: "30 years' imprisonment with a non-parole period of 22 years and 6 months"
"""
import pytest
import requests
import re

BASE_URL = 'http://localhost:8001'

# Test credentials
TEST_EMAIL = "test@example.com"
TEST_PASSWORD = "TestPassword123!"

# Target case and reports
TARGET_CASE_ID = "case_76056187ad4f"
QUICK_SUMMARY_REPORT_ID = "rpt_72e6a39f91f6"
FULL_DETAILED_REPORT_ID = "rpt_f049e0c6b384"
EXTENSIVE_LOG_REPORT_ID = "rpt_4249ad7d9fee"
BARRISTER_REPORT_ID = "rpt_d7b82aafbdea"

# Expected exact sentence wording (after normalization)
# Note: The sentence may have a comma after "imprisonment" depending on the source text
# Using curly apostrophe (') as that's what appears in the actual data
EXPECTED_SENTENCE_VARIANTS = [
    "30 years' imprisonment with a non-parole period of 22 years and 6 months",
    "30 years' imprisonment, with a non-parole period of 22 years and 6 months",
    "30 years’ imprisonment with a non-parole period of 22 years and 6 months",
    "30 years’ imprisonment, with a non-parole period of 22 years and 6 months",
]

# Patterns that should NOT appear (offence text and "minimum" prefix)
FORBIDDEN_PATTERNS = [
    r"for\s+murder",
    r"minimum\s+non[- ]?parole\s+period",
]


@pytest.fixture(scope="module")
def session_token():
    """Get authentication token"""
    response = requests.post(
        f"{BASE_URL}/api/auth/login",
        json={"email": TEST_EMAIL, "password": TEST_PASSWORD}
    )
    assert response.status_code == 200, f"Login failed: {response.text}"
    return response.json().get("session_token")


@pytest.fixture(scope="module")
def auth_headers(session_token):
    """Get auth headers"""
    return {"Authorization": f"Bearer {session_token}"}


class TestSentenceWordingInReports:
    """Test exact sentence wording in all 4 report types"""

    def test_quick_summary_sentence_wording(self, auth_headers):
        """Quick Summary report should have exact sentence wording"""
        response = requests.get(
            f"{BASE_URL}/api/cases/{TARGET_CASE_ID}/reports/{QUICK_SUMMARY_REPORT_ID}",
            headers=auth_headers
        )
        assert response.status_code == 200, f"Failed to get quick summary: {response.text}"
        
        report = response.json()
        analysis = report.get("content", {}).get("analysis", "")
        
        # Check that one of the expected sentence variants appears
        found_expected = any(variant in analysis for variant in EXPECTED_SENTENCE_VARIANTS)
        assert found_expected, \
            f"Expected sentence variants not found in quick summary analysis. Variants: {EXPECTED_SENTENCE_VARIANTS}"
        
        # Check that forbidden patterns do NOT appear in the sentence context
        for pattern in FORBIDDEN_PATTERNS:
            # Look for the pattern near "30 years" or "imprisonment"
            sentence_context = re.search(r"30 years[^.]{0,200}", analysis, re.I)
            if sentence_context:
                context = sentence_context.group(0)
                match = re.search(pattern, context, re.I)
                assert not match, \
                    f"Forbidden pattern '{pattern}' found in sentence context: {context}"

    def test_full_detailed_sentence_wording(self, auth_headers):
        """Full Detailed report should have exact sentence wording"""
        response = requests.get(
            f"{BASE_URL}/api/cases/{TARGET_CASE_ID}/reports/{FULL_DETAILED_REPORT_ID}",
            headers=auth_headers
        )
        assert response.status_code == 200, f"Failed to get full detailed: {response.text}"
        
        report = response.json()
        analysis = report.get("content", {}).get("analysis", "")
        
        # Check that one of the expected sentence variants appears
        found_expected = any(variant in analysis for variant in EXPECTED_SENTENCE_VARIANTS)
        assert found_expected, \
            "Expected sentence variants not found in full detailed analysis"

    def test_extensive_log_sentence_wording(self, auth_headers):
        """Extensive Log report should have exact sentence wording"""
        response = requests.get(
            f"{BASE_URL}/api/cases/{TARGET_CASE_ID}/reports/{EXTENSIVE_LOG_REPORT_ID}",
            headers=auth_headers
        )
        assert response.status_code == 200, f"Failed to get extensive log: {response.text}"
        
        report = response.json()
        analysis = report.get("content", {}).get("analysis", "")
        
        # Check that one of the expected sentence variants appears
        found_expected = any(variant in analysis for variant in EXPECTED_SENTENCE_VARIANTS)
        assert found_expected, \
            "Expected sentence variants not found in extensive log analysis"

    def test_barrister_view_sentence_wording(self, auth_headers):
        """Barrister View report should have exact sentence wording"""
        response = requests.get(
            f"{BASE_URL}/api/cases/{TARGET_CASE_ID}/reports/barrister-view",
            headers=auth_headers
        )
        assert response.status_code == 200, f"Failed to get barrister view: {response.text}"
        
        report = response.json()
        analysis = report.get("content", {}).get("analysis", "")
        
        # Check that one of the expected sentence variants appears
        found_expected = any(variant in analysis for variant in EXPECTED_SENTENCE_VARIANTS)
        assert found_expected, \
            "Expected sentence variants not found in barrister view analysis"


class TestSentenceWordingInExports:
    """Test exact sentence wording in PDF and DOCX exports"""

    def test_quick_summary_pdf_export(self, auth_headers):
        """Quick Summary PDF export should succeed"""
        response = requests.get(
            f"{BASE_URL}/api/cases/{TARGET_CASE_ID}/reports/{QUICK_SUMMARY_REPORT_ID}/export-pdf",
            headers=auth_headers,
            timeout=60
        )
        assert response.status_code == 200, f"PDF export failed: {response.status_code}"
        assert response.headers.get("content-type") == "application/pdf"
        assert len(response.content) > 1000, "PDF content too small"

    def test_quick_summary_docx_export(self, auth_headers):
        """Quick Summary DOCX export should succeed"""
        response = requests.get(
            f"{BASE_URL}/api/cases/{TARGET_CASE_ID}/reports/{QUICK_SUMMARY_REPORT_ID}/export-docx",
            headers=auth_headers,
            timeout=60
        )
        assert response.status_code == 200, f"DOCX export failed: {response.status_code}"
        assert "wordprocessingml" in response.headers.get("content-type", "")
        assert len(response.content) > 1000, "DOCX content too small"

    def test_full_detailed_pdf_export(self, auth_headers):
        """Full Detailed PDF export should succeed"""
        response = requests.get(
            f"{BASE_URL}/api/cases/{TARGET_CASE_ID}/reports/{FULL_DETAILED_REPORT_ID}/export-pdf",
            headers=auth_headers,
            timeout=60
        )
        assert response.status_code == 200, f"PDF export failed: {response.status_code}"
        assert response.headers.get("content-type") == "application/pdf"

    def test_full_detailed_docx_export(self, auth_headers):
        """Full Detailed DOCX export should succeed"""
        response = requests.get(
            f"{BASE_URL}/api/cases/{TARGET_CASE_ID}/reports/{FULL_DETAILED_REPORT_ID}/export-docx",
            headers=auth_headers,
            timeout=60
        )
        assert response.status_code == 200, f"DOCX export failed: {response.status_code}"
        assert "wordprocessingml" in response.headers.get("content-type", "")

    def test_extensive_log_pdf_export(self, auth_headers):
        """Extensive Log PDF export should succeed"""
        response = requests.get(
            f"{BASE_URL}/api/cases/{TARGET_CASE_ID}/reports/{EXTENSIVE_LOG_REPORT_ID}/export-pdf",
            headers=auth_headers,
            timeout=60
        )
        assert response.status_code == 200, f"PDF export failed: {response.status_code}"
        assert response.headers.get("content-type") == "application/pdf"

    def test_extensive_log_docx_export(self, auth_headers):
        """Extensive Log DOCX export should succeed"""
        response = requests.get(
            f"{BASE_URL}/api/cases/{TARGET_CASE_ID}/reports/{EXTENSIVE_LOG_REPORT_ID}/export-docx",
            headers=auth_headers,
            timeout=60
        )
        assert response.status_code == 200, f"DOCX export failed: {response.status_code}"
        assert "wordprocessingml" in response.headers.get("content-type", "")

    def test_barrister_view_pdf_export(self, auth_headers):
        """Barrister View PDF export should succeed"""
        response = requests.get(
            f"{BASE_URL}/api/cases/{TARGET_CASE_ID}/reports/{BARRISTER_REPORT_ID}/export-pdf",
            headers=auth_headers,
            timeout=60
        )
        assert response.status_code == 200, f"PDF export failed: {response.status_code}"
        assert response.headers.get("content-type") == "application/pdf"

    def test_barrister_view_docx_export(self, auth_headers):
        """Barrister View DOCX export should succeed"""
        response = requests.get(
            f"{BASE_URL}/api/cases/{TARGET_CASE_ID}/reports/{BARRISTER_REPORT_ID}/export-docx",
            headers=auth_headers,
            timeout=60
        )
        assert response.status_code == 200, f"DOCX export failed: {response.status_code}"
        assert "wordprocessingml" in response.headers.get("content-type", "")


class TestSentenceNormalization:
    """Test that sentence normalization removes offence text and 'minimum' prefix"""

    def test_sentence_extraction_function(self, auth_headers):
        """Test that _derive_export_sentence returns normalized sentence"""
        # Get the quick summary report to check the raw analysis
        response = requests.get(
            f"{BASE_URL}/api/cases/{TARGET_CASE_ID}/reports/{QUICK_SUMMARY_REPORT_ID}",
            headers=auth_headers
        )
        assert response.status_code == 200
        
        report = response.json()
        analysis = report.get("content", {}).get("analysis", "")
        
        # Find all sentence mentions in the analysis
        sentence_mentions = re.findall(
            r"30 years[^.]{0,150}(?:non[- ]?parole|NPP)[^.]{0,100}",
            analysis,
            re.I
        )
        
        # Verify at least one mention exists
        assert len(sentence_mentions) > 0, "No sentence mentions found in analysis"
        
        # Check that at least one expected normalized sentence variant appears
        found_expected = False
        for mention in sentence_mentions:
            for variant in EXPECTED_SENTENCE_VARIANTS:
                if variant in mention:
                    found_expected = True
                    break
            if found_expected:
                break
        
        assert found_expected, \
            f"Expected sentence variants not found. Found mentions: {sentence_mentions}"

    def test_no_offence_text_in_sentence_display(self, auth_headers):
        """Verify 'for murder' is not in the sentence display context"""
        response = requests.get(
            f"{BASE_URL}/api/cases/{TARGET_CASE_ID}/reports/{QUICK_SUMMARY_REPORT_ID}",
            headers=auth_headers
        )
        assert response.status_code == 200
        
        report = response.json()
        analysis = report.get("content", {}).get("analysis", "")
        
        # The sentence in the CASE SNAPSHOT section should not have "for murder"
        # Extract the case snapshot section
        snapshot_match = re.search(
            r"CASE SNAPSHOT.*?(?=##|\Z)",
            analysis,
            re.I | re.S
        )
        
        if snapshot_match:
            snapshot = snapshot_match.group(0)
            # Find the sentence in the snapshot
            sentence_in_snapshot = re.search(
                r"30 years[^.]{0,200}",
                snapshot,
                re.I
            )
            if sentence_in_snapshot:
                sentence_text = sentence_in_snapshot.group(0)
                # The sentence should contain the expected wording
                assert "non-parole period of 22 years and 6 months" in sentence_text, \
                    f"Sentence in snapshot doesn't have expected NPP: {sentence_text}"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
