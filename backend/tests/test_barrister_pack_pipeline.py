"""
Test suite for Barrister Acceptance Pack PDF generation and Pipeline Progress endpoints.
Tests the two new features:
1. GET /api/cases/{case_id}/barrister-pack/generate - PDF generation
2. GET /api/cases/{case_id}/pipeline/status - Pipeline status for Progress widget
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', 'http://localhost:8001').rstrip('/')

# Test credentials
TEST_EMAIL = "test@example.com"
TEST_PASSWORD = "TestPassword123!"
TEST_CASE_ID = "case_87ef925be713"


@pytest.fixture(scope="module")
def session_token():
    """Get authentication token via login endpoint"""
    