"""
Iteration 74 - Report Quality and Word Count Verification Tests
Tests the multi-pass LLM generation architecture for report word counts:
- Quick Summary: 1500-2200 words (single pass)
- Full Detailed: 4500-6500 words (5-pass)
- Extensive Log: 7000-10000 words (7-pass)
"""
import pytest
import requests
import os
import re

BASE_URL = 'http://localhost:8001'
SESSION_TOKEN = "test_token_placeholder"
CASE_ID = "case_1114ec0e2fd0"

# Report IDs from the request
QUICK_SUMMARY_ID = "rpt_7c8992788870"
FULL_DETAILED_ID = "rpt_e37239e2853c"
EXTENSIVE_LOG_ID = "rpt_36287019c04b"

# AI placeholder patterns to check for
AI_PLACEHOLDER_PATTERNS = [
    r'\[Note: Continue',
    r'\[Insert details',
    r'\[Continue analysis',
    r'\[Add more',
    r'\[Expand on',
    r'\[Further details',
    r'\.\.\. \(continue',
    r'continue analysis\)',
    r'\[To be completed',
    r'\[Placeholder',
]


@pytest.fixture
def api_client():
    """Shared requests session with auth cookie"""
    session = requests.Session()
    session.cookies.set('session_token', SESSION_TOKEN)
    session.headers.update({"Content-Type": "application/json"})
    return session


def count_words(text):
    """Count words in text, excluding markdown formatting"""
    if not text:
        return 0
    # Remove markdown headers, links, etc.
    clean_text = re.sub(r'[#*_\[\](){}|`]', ' ', text)
    # Split by whitespace and count
    words = clean_text.split()
    return len(words)


def check_ai_placeholders(text):
    """Check for AI placeholder text patterns"""
    found = []
    for pattern in AI_PLACEHOLDER_PATTERNS:
        matches = re.findall(pattern, text, re.IGNORECASE)
        if matches:
            found.extend(matches)
    return found


def count_sections(text):
    """Count markdown sections (## headers)"""
    if not text:
        return 0
    # Count ## headers
    sections = re.findall(r'^##\s+', text, re.MULTILINE)
    return len(sections)


class TestReportsListAPI:
    """Test GET /api/cases/{case_id}/reports endpoint"""
    
    def test_list_reports_returns_200(self, api_client):
        """Verify reports list endpoint returns 200"""
        response = api_client.get(f"{BASE_URL}/api/cases/{CASE_ID}/reports")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        assert isinstance(data, list), "Expected list of reports"
        print(f"PASSED: GET /api/cases/{CASE_ID}/reports returns 200 with {len(data)} reports")
    
    def test_list_reports_contains_expected_reports(self, api_client):
        """Verify the expected report IDs exist"""
        response = api_client.get(f"{BASE_URL}/api/cases/{CASE_ID}/reports")
        assert response.status_code == 200
        data = response.json()
        
        report_ids = [r.get('report_id') for r in data]
        
        # Check for expected reports
        assert QUICK_SUMMARY_ID in report_ids, f"Quick summary {QUICK_SUMMARY_ID} not found in reports"
        assert FULL_DETAILED_ID in report_ids, f"Full detailed {FULL_DETAILED_ID} not found in reports"
        assert EXTENSIVE_LOG_ID in report_ids, f"Extensive log {EXTENSIVE_LOG_ID} not found in reports"
        
        print("PASSED: All 3 expected reports found in list")


def get_analysis_text(data):
    """Extract analysis text from report data structure"""
    content = data.get('content', {})
    if isinstance(content, dict):
        return content.get('analysis', '')
    return content if isinstance(content, str) else ''


class TestQuickSummaryReport:
    """Test Quick Summary report (rpt_7c8992788870) - Target: 1500-2200 words"""
    
    def test_quick_summary_exists(self, api_client):
        """Verify quick summary report exists"""
        response = api_client.get(f"{BASE_URL}/api/cases/{CASE_ID}/reports/{QUICK_SUMMARY_ID}")
        assert response.status_code == 200, f"Quick summary not found: {response.status_code}"
        print(f"PASSED: Quick summary report {QUICK_SUMMARY_ID} exists")
    
    def test_quick_summary_word_count(self, api_client):
        """Verify quick summary has 1500+ words"""
        response = api_client.get(f"{BASE_URL}/api/cases/{CASE_ID}/reports/{QUICK_SUMMARY_ID}")
        assert response.status_code == 200
        data = response.json()
        
        content = get_analysis_text(data)
        word_count = count_words(content)
        
        print(f"Quick Summary word count: {word_count}")
        assert word_count >= 1500, f"Quick summary has only {word_count} words, expected 1500+"
        print(f"PASSED: Quick summary has {word_count} words (target: 1500-2200)")
    
    def test_quick_summary_no_placeholders(self, api_client):
        """Verify no AI placeholder text in quick summary"""
        response = api_client.get(f"{BASE_URL}/api/cases/{CASE_ID}/reports/{QUICK_SUMMARY_ID}")
        assert response.status_code == 200
        data = response.json()
        
        content = get_analysis_text(data)
        placeholders = check_ai_placeholders(content)
        
        assert len(placeholders) == 0, f"Found AI placeholders: {placeholders}"
        print("PASSED: No AI placeholder text found in quick summary")
    
    def test_quick_summary_report_type(self, api_client):
        """Verify report type is quick_summary"""
        response = api_client.get(f"{BASE_URL}/api/cases/{CASE_ID}/reports/{QUICK_SUMMARY_ID}")
        assert response.status_code == 200
        data = response.json()
        
        report_type = data.get('report_type')
        assert report_type == 'quick_summary', f"Expected quick_summary, got {report_type}"
        print("PASSED: Report type is quick_summary")


class TestFullDetailedReport:
    """Test Full Detailed report (rpt_e37239e2853c) - Target: 4500-6500 words, 15 sections"""
    
    def test_full_detailed_exists(self, api_client):
        """Verify full detailed report exists"""
        response = api_client.get(f"{BASE_URL}/api/cases/{CASE_ID}/reports/{FULL_DETAILED_ID}")
        assert response.status_code == 200, f"Full detailed not found: {response.status_code}"
        print(f"PASSED: Full detailed report {FULL_DETAILED_ID} exists")
    
    def test_full_detailed_word_count(self, api_client):
        """Verify full detailed has 4500+ words"""
        response = api_client.get(f"{BASE_URL}/api/cases/{CASE_ID}/reports/{FULL_DETAILED_ID}")
        assert response.status_code == 200
        data = response.json()
        
        content = get_analysis_text(data)
        word_count = count_words(content)
        
        print(f"Full Detailed word count: {word_count}")
        assert word_count >= 4500, f"Full detailed has only {word_count} words, expected 4500+"
        print(f"PASSED: Full detailed has {word_count} words (target: 4500-6500)")
    
    def test_full_detailed_section_count(self, api_client):
        """Verify full detailed has 15 sections"""
        response = api_client.get(f"{BASE_URL}/api/cases/{CASE_ID}/reports/{FULL_DETAILED_ID}")
        assert response.status_code == 200
        data = response.json()
        
        content = get_analysis_text(data)
        section_count = count_sections(content)
        
        print(f"Full Detailed section count: {section_count}")
        assert section_count >= 15, f"Full detailed has only {section_count} sections, expected 15+"
        print(f"PASSED: Full detailed has {section_count} sections (target: 15)")
    
    def test_full_detailed_no_placeholders(self, api_client):
        """Verify no AI placeholder text in full detailed"""
        response = api_client.get(f"{BASE_URL}/api/cases/{CASE_ID}/reports/{FULL_DETAILED_ID}")
        assert response.status_code == 200
        data = response.json()
        
        content = get_analysis_text(data)
        placeholders = check_ai_placeholders(content)
        
        assert len(placeholders) == 0, f"Found AI placeholders: {placeholders}"
        print("PASSED: No AI placeholder text found in full detailed")
    
    def test_full_detailed_report_type(self, api_client):
        """Verify report type is full_detailed"""
        response = api_client.get(f"{BASE_URL}/api/cases/{CASE_ID}/reports/{FULL_DETAILED_ID}")
        assert response.status_code == 200
        data = response.json()
        
        report_type = data.get('report_type')
        assert report_type == 'full_detailed', f"Expected full_detailed, got {report_type}"
        print("PASSED: Report type is full_detailed")


class TestExtensiveLogReport:
    """Test Extensive Log report (rpt_36287019c04b) - Target: 7000-10000 words, 20 sections"""
    
    def test_extensive_log_exists(self, api_client):
        """Verify extensive log report exists"""
        response = api_client.get(f"{BASE_URL}/api/cases/{CASE_ID}/reports/{EXTENSIVE_LOG_ID}")
        assert response.status_code == 200, f"Extensive log not found: {response.status_code}"
        print(f"PASSED: Extensive log report {EXTENSIVE_LOG_ID} exists")
    
    def test_extensive_log_word_count(self, api_client):
        """Verify extensive log has 7000+ words"""
        response = api_client.get(f"{BASE_URL}/api/cases/{CASE_ID}/reports/{EXTENSIVE_LOG_ID}")
        assert response.status_code == 200
        data = response.json()
        
        content = get_analysis_text(data)
        word_count = count_words(content)
        
        print(f"Extensive Log word count: {word_count}")
        assert word_count >= 7000, f"Extensive log has only {word_count} words, expected 7000+"
        print(f"PASSED: Extensive log has {word_count} words (target: 7000-10000)")
    
    def test_extensive_log_section_count(self, api_client):
        """Verify extensive log has 20 sections"""
        response = api_client.get(f"{BASE_URL}/api/cases/{CASE_ID}/reports/{EXTENSIVE_LOG_ID}")
        assert response.status_code == 200
        data = response.json()
        
        content = get_analysis_text(data)
        section_count = count_sections(content)
        
        print(f"Extensive Log section count: {section_count}")
        assert section_count >= 20, f"Extensive log has only {section_count} sections, expected 20+"
        print(f"PASSED: Extensive log has {section_count} sections (target: 20)")
    
    def test_extensive_log_no_placeholders(self, api_client):
        """Verify no AI placeholder text in extensive log"""
        response = api_client.get(f"{BASE_URL}/api/cases/{CASE_ID}/reports/{EXTENSIVE_LOG_ID}")
        assert response.status_code == 200
        data = response.json()
        
        content = get_analysis_text(data)
        placeholders = check_ai_placeholders(content)
        
        assert len(placeholders) == 0, f"Found AI placeholders: {placeholders}"
        print("PASSED: No AI placeholder text found in extensive log")
    
    def test_extensive_log_report_type(self, api_client):
        """Verify report type is extensive_log"""
        response = api_client.get(f"{BASE_URL}/api/cases/{CASE_ID}/reports/{EXTENSIVE_LOG_ID}")
        assert response.status_code == 200
        data = response.json()
        
        report_type = data.get('report_type')
        assert report_type == 'extensive_log', f"Expected extensive_log, got {report_type}"
        print("PASSED: Report type is extensive_log")


class TestReportContentQuality:
    """Test that report sections contain substantive content"""
    
    def test_full_detailed_sections_substantive(self, api_client):
        """Verify full detailed sections are not single-line summaries"""
        response = api_client.get(f"{BASE_URL}/api/cases/{CASE_ID}/reports/{FULL_DETAILED_ID}")
        assert response.status_code == 200
        data = response.json()
        
        content = get_analysis_text(data)
        
        # Split by ## headers and check each section
        sections = re.split(r'^##\s+', content, flags=re.MULTILINE)
        
        short_sections = []
        for i, section in enumerate(sections[1:], 1):  # Skip first empty split
            # Get section title and content
            lines = section.strip().split('\n')
            if lines:
                title = lines[0].strip()
                section_content = '\n'.join(lines[1:]).strip()
                word_count = count_words(section_content)
                
                # Each section should have at least 100 words
                if word_count < 100:
                    short_sections.append(f"Section '{title}': {word_count} words")
        
        if short_sections:
            print(f"WARNING: Short sections found: {short_sections}")
        
        # Allow up to 3 short sections (some may be tables or lists)
        assert len(short_sections) <= 3, f"Too many short sections: {short_sections}"
        print("PASSED: Full detailed sections are substantive")
    
    def test_extensive_log_sections_substantive(self, api_client):
        """Verify extensive log sections are not single-line summaries"""
        response = api_client.get(f"{BASE_URL}/api/cases/{CASE_ID}/reports/{EXTENSIVE_LOG_ID}")
        assert response.status_code == 200
        data = response.json()
        
        content = get_analysis_text(data)
        
        # Split by ## headers and check each section
        sections = re.split(r'^##\s+', content, flags=re.MULTILINE)
        
        short_sections = []
        for i, section in enumerate(sections[1:], 1):  # Skip first empty split
            lines = section.strip().split('\n')
            if lines:
                title = lines[0].strip()
                section_content = '\n'.join(lines[1:]).strip()
                word_count = count_words(section_content)
                
                if word_count < 100:
                    short_sections.append(f"Section '{title}': {word_count} words")
        
        if short_sections:
            print(f"WARNING: Short sections found: {short_sections}")
        
        # Allow up to 3 short sections
        assert len(short_sections) <= 3, f"Too many short sections: {short_sections}"
        print("PASSED: Extensive log sections are substantive")


class TestReportGenerationEndpoint:
    """Test POST /api/cases/{case_id}/reports/generate endpoint structure"""
    
    def test_generate_endpoint_exists(self, api_client):
        """Verify the generate endpoint exists (don't actually generate)"""
        # Just check OPTIONS or a minimal request to verify endpoint exists
        # We won't actually generate as it takes 2+ minutes
        response = api_client.options(f"{BASE_URL}/api/cases/{CASE_ID}/reports/generate")
        # OPTIONS might return 200 or 405 depending on CORS config
        # Just verify we don't get 404
        assert response.status_code != 404, "Generate endpoint not found"
        print(f"PASSED: Generate endpoint exists (status: {response.status_code})")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
