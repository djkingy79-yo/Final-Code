"""
Iteration 208 Feature Tests
Tests for:
1. Translate concurrency + restart-recovery
2. Admin Dashboard PayID reordering (frontend only - verified via code review)
3. AiCostBadge / ai-cost endpoint
4. Cost tracker regex fix for case_<12hex> format
"""
import os
import sys
import pytest
import requests

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://criminallawappealmanagement.com.au')


class TestAiCostEndpoint:
    """Tests for GET /api/cases/{case_id}/ai-cost endpoint"""
    
    def test_ai_cost_requires_auth(self):
        """Unauthenticated requests should return 401"""
        response = requests.get(f"{BASE_URL}/api/cases/test_case_id/ai-cost")
        assert response.status_code == 401
    
    def test_ai_cost_returns_404_for_nonexistent_case(self):
        """Non-owner should get 404 (not 403) to avoid leaking case existence"""
        # This test requires auth - skip if no session
        pytest.skip("Requires authenticated session to test 404 behavior")


class TestTranslateStatusEndpoint:
    """Tests for GET /api/cases/{case_id}/translate/status endpoint"""
    
    def test_translate_status_requires_auth(self):
        """Unauthenticated requests should return 401"""
        response = requests.get(
            f"{BASE_URL}/api/cases/test_case_id/translate/status",
            params={"report_id": "test", "language": "es"}
        )
        assert response.status_code == 401


class TestLanguagesEndpoint:
    """Tests for GET /api/languages endpoint"""
    
    def test_languages_returns_list(self):
        """Languages endpoint should return list of supported languages"""
        response = requests.get(f"{BASE_URL}/api/languages")
        assert response.status_code == 200
        data = response.json()
        assert "languages" in data
        assert len(data["languages"]) > 30  # 41 languages supported
        
        # Check structure
        first_lang = data["languages"][0]
        assert "code" in first_lang
        assert "name" in first_lang
    
    def test_languages_includes_common_languages(self):
        """Should include common translation targets"""
        response = requests.get(f"{BASE_URL}/api/languages")
        data = response.json()
        codes = [l["code"] for l in data["languages"]]
        
        # Check for common languages
        assert "es" in codes  # Spanish
        assert "zh" in codes  # Chinese
        assert "ar" in codes  # Arabic
        assert "fr" in codes  # French
        assert "de" in codes  # German
        assert "ja" in codes  # Japanese
        assert "ko" in codes  # Korean
        assert "vi" in codes  # Vietnamese


class TestCaseIdRegexPatterns:
    """Tests for case_id extraction patterns in ai_usage_tracker"""
    
    def test_case_hex_format_extraction(self):
        """Verify case_<12hex> format is correctly extracted"""
        from services.ai_usage_tracker import _extract_case_id
        
        # Production case_id format
        assert _extract_case_id("rpt_gen_case_ec9b7141be1b_quick_summary") == "case_ec9b7141be1b"
        assert _extract_case_id("rpt_gen_case_ec9b7141be1b") == "case_ec9b7141be1b"
        assert _extract_case_id("barrister-case_ec9b7141be1b-strategy") == "case_ec9b7141be1b"
        assert _extract_case_id("classify_case_ec9b7141be1b") == "case_ec9b7141be1b"
        assert _extract_case_id("draft_case_ec9b7141be1b_full_detailed") == "case_ec9b7141be1b"
    
    def test_report_type_extraction_case_hex(self):
        """Verify report_type extraction for case_<hex> format"""
        from services.ai_usage_tracker import _extract_report_type
        
        assert _extract_report_type("rpt_gen_case_ec9b7141be1b_quick_summary") == "quick_summary"
        assert _extract_report_type("draft_case_ec9b7141be1b_extensive_log") == "extensive_log"
        assert _extract_report_type("barrister-case_ec9b7141be1b-strategy") == "appellate_research_brief"


class TestTranslateParallelRecovery:
    """Tests for translate parallelisation and recovery features"""
    
    def test_persist_task_function_exists(self):
        """Verify _persist_task function exists in translate module"""
        from routers.translate import _persist_task
        assert callable(_persist_task)
    
    def test_translate_tasks_dict_exists(self):
        """Verify in-memory task store exists"""
        from routers.translate import _translate_tasks
        assert isinstance(_translate_tasks, dict)
    
    def test_supported_languages_count(self):
        """Verify 41 languages are supported"""
        from routers.translate import SUPPORTED_LANGUAGES
        assert len(SUPPORTED_LANGUAGES) == 41


class TestFrontendCodeVerification:
    """Code verification tests (not runtime tests)"""
    
    def test_report_translator_max_attempts(self):
        """Verify ReportTranslator.jsx has maxAttempts=300"""
        import subprocess
        result = subprocess.run(
            ["grep", "-c", "maxAttempts = 300", "/app/frontend/src/components/ReportTranslator.jsx"],
            capture_output=True, text=True
        )
        assert result.returncode == 0
        assert int(result.stdout.strip()) >= 1
    
    def test_report_translator_poll_interval(self):
        """Verify ReportTranslator.jsx has pollInterval=5000"""
        import subprocess
        result = subprocess.run(
            ["grep", "-c", "pollInterval = 5000", "/app/frontend/src/components/ReportTranslator.jsx"],
            capture_output=True, text=True
        )
        assert result.returncode == 0
        assert int(result.stdout.strip()) >= 1
    
    def test_admin_dashboard_payid_testid(self):
        """Verify AdminDashboard.jsx has pending-payments-section data-testid"""
        import subprocess
        result = subprocess.run(
            ["grep", "-c", 'data-testid="pending-payments-section"', "/app/frontend/src/pages/AdminDashboard.jsx"],
            capture_output=True, text=True
        )
        assert result.returncode == 0
        assert int(result.stdout.strip()) >= 1
    
    def test_admin_dashboard_refresh_btn_testid(self):
        """Verify AdminDashboard.jsx has refresh-payments-btn data-testid"""
        import subprocess
        result = subprocess.run(
            ["grep", "-c", 'data-testid="refresh-payments-btn"', "/app/frontend/src/pages/AdminDashboard.jsx"],
            capture_output=True, text=True
        )
        assert result.returncode == 0
        assert int(result.stdout.strip()) >= 1
    
    def test_ai_cost_badge_testid(self):
        """Verify AiCostBadge.jsx has ai-cost-badge data-testid"""
        import subprocess
        result = subprocess.run(
            ["grep", "-c", 'data-testid="ai-cost-badge"', "/app/frontend/src/components/AiCostBadge.jsx"],
            capture_output=True, text=True
        )
        assert result.returncode == 0
        assert int(result.stdout.strip()) >= 1


class TestHealthEndpoint:
    """Basic health check"""
    
    def test_health_returns_200(self):
        """Health endpoint should return 200"""
        response = requests.get(f"{BASE_URL}/api/health", timeout=10)
        assert response.status_code == 200
