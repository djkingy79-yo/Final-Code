"""
Shared test fixtures for Appeal Case Manager backend tests.
All tests use localhost:8001 to avoid firewall/DNS blocks.
"""
import pytest

BASE_URL = "http://localhost:8001"
API_URL = f"{BASE_URL}/api"

TEST_EMAIL = "test@example.com"
TEST_PASSWORD = "TestPassword123!"


@pytest.fixture
def base_url():
    return BASE_URL


@pytest.fixture
def api_url():
    return API_URL


@pytest.fixture
def auth_headers():
    """Get auth headers with a valid session token."""
    import requests
    resp = requests.post(
        f"{API_URL}/auth/login",
        json={"email": TEST_EMAIL, "password": TEST_PASSWORD}
    )
    token = resp.json().get("session_token", "")
    return {"Authorization": f"Bearer {token}"}
