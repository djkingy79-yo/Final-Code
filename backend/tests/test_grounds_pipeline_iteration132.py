"""
Test Suite for Grounds Pipeline Delegation (Iteration 132)
Tests the patched grounds.py router that delegates auto-identify and investigate
operations through the new 5-stage pipeline (Extract → Classify → Verify → Project → Draft).

Key endpoints tested:
- POST /api/cases/{case_id}/grounds/auto-identify - pipeline delegation
- POST /api/cases/{case_id}/grounds/{ground_id}/investigate - pipeline verify delegation
- GET /api/cases/{case_id}/grounds - with ground_id, source_mode, verification_status
- GET /api/cases/{case_id}/grounds/{ground_id} - with enrichment
- Regression: CRUD operations on grounds
- Regression: Staged pipeline extract
- Regression: Health endpoint
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', 'http://localhost:8001').rstrip('/')

# Test credentials
TEST_EMAIL = "test@example.com"
TEST_PASSWORD = "TestPassword123!"

# Test cases from the request
TEST_CASE_1 = "case_87ef925be713"  # Scott Joshua v R - has many documents and grounds
TEST_CASE_2 = "case_a97ea91f0692"  # Dummy Murder Appeal - has pipeline-derived grounds
TEST_GROUND_ID = "gnd_0fa085cfc1ce"  # Ground ID for investigate test (case_a97ea91f0692)


class TestAuthentication:
    """Authentication tests - must pass before other tests"""
    
    def test_login_returns_session_token(self):
        """Verify login returns session_token field"""
        

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
