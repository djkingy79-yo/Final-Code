"""
Shared test fixtures for Appeal Case Manager backend tests.
"""
import sys
import os
import asyncio
import pytest
from datetime import datetime, timezone, timedelta

# Add backend dir to sys.path so tests can import services/routers/config
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

BASE_URL = "http://localhost:8001"
API_URL = f"{BASE_URL}/api"
SESSION_TOKEN = "ci_test_token_permanent_20260412"


def _ensure_session():
    """Ensure test session exists in DB, drop TTL indexes that delete sessions."""
    from motor.motor_asyncio import AsyncIOMotorClient

    async def _create():
        client = AsyncIOMotorClient('mongodb://localhost:27017')
        db = client['test_database']
        # Drop TTL indexes on user_sessions
        indexes = await db.user_sessions.index_information()
        for n, i in indexes.items():
            if 'expireAfterSeconds' in i and 'expires_at' in str(i.get('key', '')):
                try:
                    await db.user_sessions.drop_index(n)
                except Exception:
                    pass
        existing = await db.user_sessions.find_one({'session_token': SESSION_TOKEN})
        if not existing:
            await db.user_sessions.insert_one({
                'session_token': SESSION_TOKEN,
                'user_id': 'user_d2287f20104b',
                'expires_at': (datetime.now(timezone.utc) + timedelta(days=30)).isoformat(),
                'created_at': datetime.now(timezone.utc).isoformat()
            })

    try:
        loop = asyncio.get_event_loop()
        if loop.is_closed():
            loop = asyncio.new_event_loop()
        loop.run_until_complete(_create())
    except Exception:
        pass


# Ensure session exists at import time
_ensure_session()


@pytest.fixture
def base_url():
    return BASE_URL


@pytest.fixture
def api_url():
    return API_URL


@pytest.fixture
def auth_headers():
    """Return auth headers with valid session token."""
    _ensure_session()
    return {"Authorization": f"Bearer {SESSION_TOKEN}"}
