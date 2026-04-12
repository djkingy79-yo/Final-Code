"""
Shared test fixtures for Appeal Case Manager backend tests.
"""
import sys
import os
import pytest

# Add backend dir to sys.path so tests can import services/routers/config
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

BASE_URL = "http://localhost:8001"
API_URL = f"{BASE_URL}/api"
SESSION_TOKEN = "61bbcd763e9a47ed8d7ad1a7bcf1854a"


@pytest.fixture
def base_url():
    return BASE_URL


@pytest.fixture
def api_url():
    return API_URL


@pytest.fixture
def auth_headers():
    """Return auth headers with valid session token (Google OAuth)."""
    return {"Authorization": f"Bearer {SESSION_TOKEN}"}
