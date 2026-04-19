"""
Test Suite for Staged Pipeline Architecture (Iteration 131)
Tests the new 5-stage pipeline: Extract → Classify → Verify → Project → Draft
New endpoints at /api/pipeline prefix + regression tests for old /api/cases prefix
"""
import pytest
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', 'http://localhost:8001').rstrip('/')

# Test credentials
TEST_EMAIL = "test@example.com"
TEST_PASSWORD = "TestPassword123!"
TEST_CASE_ID = "case_87ef925be713"
TEST_DOC_ID = "doc_8452bbcc833c"
TEST_ISSUE_ID = "iss_330074ee5c02"


class TestAuthentication:
    """Authentication tests - must pass before other tests"""
    
    def test_login_returns_session_token(self):
        """Verify login returns session_token field"""
        

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
