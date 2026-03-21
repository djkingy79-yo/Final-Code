"""
Iteration 75 - Test all 6 reports (3 types × 2 modes) for case_1114ec0e2fd0
Tests:
- All 6 reports exist with status=completed
- Word counts and section counts meet targets
- No AI placeholder text
- Content hierarchy (no repetition between tiers)
- Aggressive mode badge presence
"""
import pytest
import requests
import os
import re
from collections import Counter

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')
SESSION_TOKEN = "sess_65c07d6c3ed5440bb3e34fffe7bb41fa"
CASE_ID = "case_1114ec0e2fd0"

# Expected report IDs from main agent
REPORT_IDS = {
    "quick_summary_standard": "rpt_79bd4358a44b",
    "quick_summary_aggressive": "rpt_d949986ef6f6",
    "full_detailed_standard": "rpt_9d6663272f91",
    "full_detailed_aggressive": "rpt_8449151e3a76",
    "extensive_log_standard": "rpt_5cf6c80e4dc0",
    "extensive_log_aggressive": "rpt_5726428820cc"
}

# Word count targets
WORD_TARGETS = {
    "quick_summary_standard": (1300, 2500),
    "quick_summary_aggressive": (1500, 3000),
    "full_detailed_standard": (4500, 7000),
    "full_detailed_aggressive": (5500, 8500),
    "extensive_log_standard": (7000, 12000),
    "extensive_log_aggressive": (7000, 12000)
}

# Section count targets
SECTION_TARGETS = {
    "quick_summary_standard": 7,
    "quick_summary_aggressive": 7,
    "full_detailed_standard": 15,
    "full_detailed_aggressive": 15,
    "extensive_log_standard": 20,
    "extensive_log_aggressive": 20
}

# AI placeholder patterns to check for
AI_PLACEHOLDER_PATTERNS = [
    r'\[Note:\s*Continue',
    r'\[Insert\s+details',
    r'\[Add\s+',
    r'\[Continue\s+',
    r'\[Repeat\s+',
    r'\[Follow\s+',
    r'\[Include\s+',
    r'\[Provide\s+',
    r'\[Similar\s+',
    r'\(Note:\s*Continue',
    r'\(Entries will',
    r'\(Link formatting',
    r'\.\.\.continue',
    r'etc\.\s*\]',
]


@pytest.fixture(scope="module")
def api_client():
    """Shared requests session with auth cookie"""
    session = requests.Session()
    session.headers.update({"Content-Type": "application/json"})
    session.cookies.set("session_token", SESSION_TOKEN)
    return session


@pytest.fixture(scope="module")
def all_reports(api_client):
    """Fetch all reports for the case"""
    response = api_client.get(f"{BASE_URL}/api/cases/{CASE_ID}/reports")
    assert response.status_code == 200, f"Failed to fetch reports: {response.status_code}"
    return response.json()


@pytest.fixture(scope="module")
def report_details(api_client):
    """Fetch detailed content for each expected report"""
    details = {}
    for key, report_id in REPORT_IDS.items():
        response = api_client.get(f"{BASE_URL}/api/cases/{CASE_ID}/reports/{report_id}")
        if response.status_code == 200:
            details[key] = response.json()
        else:
            details[key] = None
    return details


def count_words(text):
    """Count words in text"""
    if not text:
        return 0
    return len(text.split())


def count_sections(text):
    """Count markdown sections (## headers)"""
    if not text:
        return 0
    # Count ## headers (level 2 markdown headers)
    pattern = r'^##\s+\d*\.?\s*[A-Z]'
    matches = re.findall(pattern, text, re.MULTILINE)
    return len(matches)


def extract_8word_phrases(text):
    """Extract all 8-word phrases from text for overlap detection"""
    if not text:
        return set()
    words = re.findall(r'\b\w+\b', text.lower())
    phrases = set()
    for i in range(len(words) - 7):
        phrase = ' '.join(words[i:i+8])
        phrases.add(phrase)
    return phrases


def check_ai_placeholders(text):
    """Check for AI placeholder patterns"""
    if not text:
        return []
    found = []
    for pattern in AI_PLACEHOLDER_PATTERNS:
        matches = re.findall(pattern, text, re.IGNORECASE)
        if matches:
            found.extend(matches)
    return found


class TestAllReportsExist:
    """Verify all 6 reports exist with status=completed"""
    
    def test_reports_list_returns_6_reports(self, all_reports):
        """GET /api/cases/{case_id}/reports returns all 6 reports"""
        assert len(all_reports) >= 6, f"Expected at least 6 reports, got {len(all_reports)}"
        print(f"✓ Found {len(all_reports)} reports for case")
    
    def test_quick_summary_standard_exists(self, report_details):
        """Quick Summary Standard report exists"""
        report = report_details.get("quick_summary_standard")
        assert report is not None, f"Report {REPORT_IDS['quick_summary_standard']} not found"
        assert report.get("status") == "completed", f"Report status: {report.get('status')}"
        assert report.get("report_type") == "quick_summary"
        print(f"✓ Quick Summary Standard exists: {REPORT_IDS['quick_summary_standard']}")
    
    def test_quick_summary_aggressive_exists(self, report_details):
        """Quick Summary Aggressive report exists"""
        report = report_details.get("quick_summary_aggressive")
        assert report is not None, f"Report {REPORT_IDS['quick_summary_aggressive']} not found"
        assert report.get("status") == "completed", f"Report status: {report.get('status')}"
        assert report.get("report_type") == "quick_summary"
        # Check aggressive_mode in content
        aggressive_mode = report.get("content", {}).get("aggressive_mode", False)
        assert aggressive_mode == True, f"Expected aggressive_mode=True, got {aggressive_mode}"
        print(f"✓ Quick Summary Aggressive exists: {REPORT_IDS['quick_summary_aggressive']}")
    
    def test_full_detailed_standard_exists(self, report_details):
        """Full Detailed Standard report exists"""
        report = report_details.get("full_detailed_standard")
        assert report is not None, f"Report {REPORT_IDS['full_detailed_standard']} not found"
        assert report.get("status") == "completed", f"Report status: {report.get('status')}"
        assert report.get("report_type") == "full_detailed"
        print(f"✓ Full Detailed Standard exists: {REPORT_IDS['full_detailed_standard']}")
    
    def test_full_detailed_aggressive_exists(self, report_details):
        """Full Detailed Aggressive report exists"""
        report = report_details.get("full_detailed_aggressive")
        assert report is not None, f"Report {REPORT_IDS['full_detailed_aggressive']} not found"
        assert report.get("status") == "completed", f"Report status: {report.get('status')}"
        assert report.get("report_type") == "full_detailed"
        aggressive_mode = report.get("content", {}).get("aggressive_mode", False)
        assert aggressive_mode == True, f"Expected aggressive_mode=True, got {aggressive_mode}"
        print(f"✓ Full Detailed Aggressive exists: {REPORT_IDS['full_detailed_aggressive']}")
    
    def test_extensive_log_standard_exists(self, report_details):
        """Extensive Log Standard report exists"""
        report = report_details.get("extensive_log_standard")
        assert report is not None, f"Report {REPORT_IDS['extensive_log_standard']} not found"
        assert report.get("status") == "completed", f"Report status: {report.get('status')}"
        assert report.get("report_type") == "extensive_log"
        print(f"✓ Extensive Log Standard exists: {REPORT_IDS['extensive_log_standard']}")
    
    def test_extensive_log_aggressive_exists(self, report_details):
        """Extensive Log Aggressive report exists"""
        report = report_details.get("extensive_log_aggressive")
        assert report is not None, f"Report {REPORT_IDS['extensive_log_aggressive']} not found"
        assert report.get("status") == "completed", f"Report status: {report.get('status')}"
        assert report.get("report_type") == "extensive_log"
        aggressive_mode = report.get("content", {}).get("aggressive_mode", False)
        assert aggressive_mode == True, f"Expected aggressive_mode=True, got {aggressive_mode}"
        print(f"✓ Extensive Log Aggressive exists: {REPORT_IDS['extensive_log_aggressive']}")


class TestWordCounts:
    """Verify word counts meet targets for each report"""
    
    def test_quick_summary_standard_word_count(self, report_details):
        """Quick Summary Standard: 1300+ words"""
        report = report_details.get("quick_summary_standard")
        if not report:
            pytest.skip("Report not found")
        analysis = report.get("content", {}).get("analysis", "")
        word_count = count_words(analysis)
        min_words, max_words = WORD_TARGETS["quick_summary_standard"]
        assert word_count >= min_words, f"Word count {word_count} < {min_words}"
        print(f"✓ Quick Summary Standard: {word_count} words (target: {min_words}+)")
    
    def test_quick_summary_aggressive_word_count(self, report_details):
        """Quick Summary Aggressive: 1500+ words"""
        report = report_details.get("quick_summary_aggressive")
        if not report:
            pytest.skip("Report not found")
        analysis = report.get("content", {}).get("analysis", "")
        word_count = count_words(analysis)
        min_words, max_words = WORD_TARGETS["quick_summary_aggressive"]
        assert word_count >= min_words, f"Word count {word_count} < {min_words}"
        print(f"✓ Quick Summary Aggressive: {word_count} words (target: {min_words}+)")
    
    def test_full_detailed_standard_word_count(self, report_details):
        """Full Detailed Standard: 4500+ words"""
        report = report_details.get("full_detailed_standard")
        if not report:
            pytest.skip("Report not found")
        analysis = report.get("content", {}).get("analysis", "")
        word_count = count_words(analysis)
        min_words, max_words = WORD_TARGETS["full_detailed_standard"]
        assert word_count >= min_words, f"Word count {word_count} < {min_words}"
        print(f"✓ Full Detailed Standard: {word_count} words (target: {min_words}+)")
    
    def test_full_detailed_aggressive_word_count(self, report_details):
        """Full Detailed Aggressive: 5500+ words"""
        report = report_details.get("full_detailed_aggressive")
        if not report:
            pytest.skip("Report not found")
        analysis = report.get("content", {}).get("analysis", "")
        word_count = count_words(analysis)
        min_words, max_words = WORD_TARGETS["full_detailed_aggressive"]
        assert word_count >= min_words, f"Word count {word_count} < {min_words}"
        print(f"✓ Full Detailed Aggressive: {word_count} words (target: {min_words}+)")
    
    def test_extensive_log_standard_word_count(self, report_details):
        """Extensive Log Standard: 7000+ words"""
        report = report_details.get("extensive_log_standard")
        if not report:
            pytest.skip("Report not found")
        analysis = report.get("content", {}).get("analysis", "")
        word_count = count_words(analysis)
        min_words, max_words = WORD_TARGETS["extensive_log_standard"]
        assert word_count >= min_words, f"Word count {word_count} < {min_words}"
        print(f"✓ Extensive Log Standard: {word_count} words (target: {min_words}+)")
    
    def test_extensive_log_aggressive_word_count(self, report_details):
        """Extensive Log Aggressive: 7000+ words"""
        report = report_details.get("extensive_log_aggressive")
        if not report:
            pytest.skip("Report not found")
        analysis = report.get("content", {}).get("analysis", "")
        word_count = count_words(analysis)
        min_words, max_words = WORD_TARGETS["extensive_log_aggressive"]
        assert word_count >= min_words, f"Word count {word_count} < {min_words}"
        print(f"✓ Extensive Log Aggressive: {word_count} words (target: {min_words}+)")


class TestSectionCounts:
    """Verify section counts meet targets"""
    
    def test_quick_summary_standard_sections(self, report_details):
        """Quick Summary Standard: 7 sections"""
        report = report_details.get("quick_summary_standard")
        if not report:
            pytest.skip("Report not found")
        analysis = report.get("content", {}).get("analysis", "")
        section_count = count_sections(analysis)
        target = SECTION_TARGETS["quick_summary_standard"]
        assert section_count >= target, f"Section count {section_count} < {target}"
        print(f"✓ Quick Summary Standard: {section_count} sections (target: {target})")
    
    def test_quick_summary_aggressive_sections(self, report_details):
        """Quick Summary Aggressive: 7 sections"""
        report = report_details.get("quick_summary_aggressive")
        if not report:
            pytest.skip("Report not found")
        analysis = report.get("content", {}).get("analysis", "")
        section_count = count_sections(analysis)
        target = SECTION_TARGETS["quick_summary_aggressive"]
        assert section_count >= target, f"Section count {section_count} < {target}"
        print(f"✓ Quick Summary Aggressive: {section_count} sections (target: {target})")
    
    def test_full_detailed_standard_sections(self, report_details):
        """Full Detailed Standard: 15 sections"""
        report = report_details.get("full_detailed_standard")
        if not report:
            pytest.skip("Report not found")
        analysis = report.get("content", {}).get("analysis", "")
        section_count = count_sections(analysis)
        target = SECTION_TARGETS["full_detailed_standard"]
        assert section_count >= target, f"Section count {section_count} < {target}"
        print(f"✓ Full Detailed Standard: {section_count} sections (target: {target})")
    
    def test_full_detailed_aggressive_sections(self, report_details):
        """Full Detailed Aggressive: 15 sections"""
        report = report_details.get("full_detailed_aggressive")
        if not report:
            pytest.skip("Report not found")
        analysis = report.get("content", {}).get("analysis", "")
        section_count = count_sections(analysis)
        target = SECTION_TARGETS["full_detailed_aggressive"]
        assert section_count >= target, f"Section count {section_count} < {target}"
        print(f"✓ Full Detailed Aggressive: {section_count} sections (target: {target})")
    
    def test_extensive_log_standard_sections(self, report_details):
        """Extensive Log Standard: 20 sections"""
        report = report_details.get("extensive_log_standard")
        if not report:
            pytest.skip("Report not found")
        analysis = report.get("content", {}).get("analysis", "")
        section_count = count_sections(analysis)
        target = SECTION_TARGETS["extensive_log_standard"]
        assert section_count >= target, f"Section count {section_count} < {target}"
        print(f"✓ Extensive Log Standard: {section_count} sections (target: {target})")
    
    def test_extensive_log_aggressive_sections(self, report_details):
        """Extensive Log Aggressive: 20 sections"""
        report = report_details.get("extensive_log_aggressive")
        if not report:
            pytest.skip("Report not found")
        analysis = report.get("content", {}).get("analysis", "")
        section_count = count_sections(analysis)
        target = SECTION_TARGETS["extensive_log_aggressive"]
        assert section_count >= target, f"Section count {section_count} < {target}"
        print(f"✓ Extensive Log Aggressive: {section_count} sections (target: {target})")


class TestNoAIPlaceholders:
    """Verify no AI placeholder text in any report"""
    
    def test_quick_summary_standard_no_placeholders(self, report_details):
        """Quick Summary Standard: No AI placeholders"""
        report = report_details.get("quick_summary_standard")
        if not report:
            pytest.skip("Report not found")
        analysis = report.get("content", {}).get("analysis", "")
        placeholders = check_ai_placeholders(analysis)
        assert len(placeholders) == 0, f"Found AI placeholders: {placeholders[:5]}"
        print("✓ Quick Summary Standard: No AI placeholders")
    
    def test_quick_summary_aggressive_no_placeholders(self, report_details):
        """Quick Summary Aggressive: No AI placeholders"""
        report = report_details.get("quick_summary_aggressive")
        if not report:
            pytest.skip("Report not found")
        analysis = report.get("content", {}).get("analysis", "")
        placeholders = check_ai_placeholders(analysis)
        assert len(placeholders) == 0, f"Found AI placeholders: {placeholders[:5]}"
        print("✓ Quick Summary Aggressive: No AI placeholders")
    
    def test_full_detailed_standard_no_placeholders(self, report_details):
        """Full Detailed Standard: No AI placeholders"""
        report = report_details.get("full_detailed_standard")
        if not report:
            pytest.skip("Report not found")
        analysis = report.get("content", {}).get("analysis", "")
        placeholders = check_ai_placeholders(analysis)
        assert len(placeholders) == 0, f"Found AI placeholders: {placeholders[:5]}"
        print("✓ Full Detailed Standard: No AI placeholders")
    
    def test_full_detailed_aggressive_no_placeholders(self, report_details):
        """Full Detailed Aggressive: No AI placeholders"""
        report = report_details.get("full_detailed_aggressive")
        if not report:
            pytest.skip("Report not found")
        analysis = report.get("content", {}).get("analysis", "")
        placeholders = check_ai_placeholders(analysis)
        assert len(placeholders) == 0, f"Found AI placeholders: {placeholders[:5]}"
        print("✓ Full Detailed Aggressive: No AI placeholders")
    
    def test_extensive_log_standard_no_placeholders(self, report_details):
        """Extensive Log Standard: No AI placeholders"""
        report = report_details.get("extensive_log_standard")
        if not report:
            pytest.skip("Report not found")
        analysis = report.get("content", {}).get("analysis", "")
        placeholders = check_ai_placeholders(analysis)
        assert len(placeholders) == 0, f"Found AI placeholders: {placeholders[:5]}"
        print("✓ Extensive Log Standard: No AI placeholders")
    
    def test_extensive_log_aggressive_no_placeholders(self, report_details):
        """Extensive Log Aggressive: No AI placeholders"""
        report = report_details.get("extensive_log_aggressive")
        if not report:
            pytest.skip("Report not found")
        analysis = report.get("content", {}).get("analysis", "")
        placeholders = check_ai_placeholders(analysis)
        assert len(placeholders) == 0, f"Found AI placeholders: {placeholders[:5]}"
        print("✓ Extensive Log Aggressive: No AI placeholders")


class TestContentHierarchy:
    """Verify content hierarchy - no repetition between tiers"""
    
    def test_full_detailed_not_repeating_quick_summary_standard(self, report_details):
        """Full Detailed Standard should NOT repeat Quick Summary Standard content"""
        qs_report = report_details.get("quick_summary_standard")
        fd_report = report_details.get("full_detailed_standard")
        if not qs_report or not fd_report:
            pytest.skip("Reports not found")
        
        qs_analysis = qs_report.get("content", {}).get("analysis", "")
        fd_analysis = fd_report.get("content", {}).get("analysis", "")
        
        qs_phrases = extract_8word_phrases(qs_analysis)
        fd_phrases = extract_8word_phrases(fd_analysis)
        
        if len(qs_phrases) == 0 or len(fd_phrases) == 0:
            pytest.skip("Not enough content to compare")
        
        overlap = qs_phrases.intersection(fd_phrases)
        overlap_pct = (len(overlap) / len(qs_phrases)) * 100 if len(qs_phrases) > 0 else 0
        
        # Allow up to 10% overlap (some legal terms will naturally repeat)
        assert overlap_pct < 10, f"Overlap {overlap_pct:.1f}% >= 10% - too much repetition"
        print(f"✓ Full Detailed vs Quick Summary overlap: {overlap_pct:.1f}% (< 10%)")
    
    def test_extensive_log_not_repeating_full_detailed_standard(self, report_details):
        """Extensive Log Standard should NOT repeat Full Detailed Standard content"""
        fd_report = report_details.get("full_detailed_standard")
        el_report = report_details.get("extensive_log_standard")
        if not fd_report or not el_report:
            pytest.skip("Reports not found")
        
        fd_analysis = fd_report.get("content", {}).get("analysis", "")
        el_analysis = el_report.get("content", {}).get("analysis", "")
        
        fd_phrases = extract_8word_phrases(fd_analysis)
        el_phrases = extract_8word_phrases(el_analysis)
        
        if len(fd_phrases) == 0 or len(el_phrases) == 0:
            pytest.skip("Not enough content to compare")
        
        overlap = fd_phrases.intersection(el_phrases)
        overlap_pct = (len(overlap) / len(fd_phrases)) * 100 if len(fd_phrases) > 0 else 0
        
        # Allow up to 10% overlap
        assert overlap_pct < 10, f"Overlap {overlap_pct:.1f}% >= 10% - too much repetition"
        print(f"✓ Extensive Log vs Full Detailed overlap: {overlap_pct:.1f}% (< 10%)")
    
    def test_full_detailed_aggressive_not_repeating_quick_summary_aggressive(self, report_details):
        """Full Detailed Aggressive should NOT repeat Quick Summary Aggressive content"""
        qs_report = report_details.get("quick_summary_aggressive")
        fd_report = report_details.get("full_detailed_aggressive")
        if not qs_report or not fd_report:
            pytest.skip("Reports not found")
        
        qs_analysis = qs_report.get("content", {}).get("analysis", "")
        fd_analysis = fd_report.get("content", {}).get("analysis", "")
        
        qs_phrases = extract_8word_phrases(qs_analysis)
        fd_phrases = extract_8word_phrases(fd_analysis)
        
        if len(qs_phrases) == 0 or len(fd_phrases) == 0:
            pytest.skip("Not enough content to compare")
        
        overlap = qs_phrases.intersection(fd_phrases)
        overlap_pct = (len(overlap) / len(qs_phrases)) * 100 if len(qs_phrases) > 0 else 0
        
        assert overlap_pct < 10, f"Overlap {overlap_pct:.1f}% >= 10% - too much repetition"
        print(f"✓ Full Detailed Aggressive vs Quick Summary Aggressive overlap: {overlap_pct:.1f}%")
    
    def test_extensive_log_aggressive_not_repeating_full_detailed_aggressive(self, report_details):
        """Extensive Log Aggressive should NOT repeat Full Detailed Aggressive content"""
        fd_report = report_details.get("full_detailed_aggressive")
        el_report = report_details.get("extensive_log_aggressive")
        if not fd_report or not el_report:
            pytest.skip("Reports not found")
        
        fd_analysis = fd_report.get("content", {}).get("analysis", "")
        el_analysis = el_report.get("content", {}).get("analysis", "")
        
        fd_phrases = extract_8word_phrases(fd_analysis)
        el_phrases = extract_8word_phrases(el_analysis)
        
        if len(fd_phrases) == 0 or len(el_phrases) == 0:
            pytest.skip("Not enough content to compare")
        
        overlap = fd_phrases.intersection(el_phrases)
        overlap_pct = (len(overlap) / len(fd_phrases)) * 100 if len(fd_phrases) > 0 else 0
        
        assert overlap_pct < 10, f"Overlap {overlap_pct:.1f}% >= 10% - too much repetition"
        print(f"✓ Extensive Log Aggressive vs Full Detailed Aggressive overlap: {overlap_pct:.1f}%")


class TestAggressiveModeFlag:
    """Verify aggressive_mode flag is correctly set in content"""
    
    def test_standard_reports_not_aggressive(self, report_details):
        """Standard reports should NOT have aggressive_mode=True"""
        for key in ["quick_summary_standard", "full_detailed_standard", "extensive_log_standard"]:
            report = report_details.get(key)
            if not report:
                continue
            aggressive_mode = report.get("content", {}).get("aggressive_mode", False)
            assert aggressive_mode == False, f"{key} has aggressive_mode={aggressive_mode}"
        print("✓ All standard reports have aggressive_mode=False")
    
    def test_aggressive_reports_have_flag(self, report_details):
        """Aggressive reports should have aggressive_mode=True"""
        for key in ["quick_summary_aggressive", "full_detailed_aggressive", "extensive_log_aggressive"]:
            report = report_details.get(key)
            if not report:
                continue
            aggressive_mode = report.get("content", {}).get("aggressive_mode", False)
            assert aggressive_mode == True, f"{key} has aggressive_mode={aggressive_mode}"
        print("✓ All aggressive reports have aggressive_mode=True")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
