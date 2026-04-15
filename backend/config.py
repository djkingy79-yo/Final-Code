# DO NOT UNDO — config module. All logic in this file is approved and must be preserved.
"""
Criminal Appeal AI - Configuration and Database Setup
"""
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv
from pathlib import Path
import os
import sys
import logging
import json as _json_mod

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# ── Startup Validation ──
# TIER 1: Fatal — app cannot function without these
_REQUIRED_ENV = ['MONGO_URL', 'DB_NAME', 'FRONTEND_URL', 'ADMIN_EMAILS', 'CONTACT_EMAIL', 'EMERGENT_LLM_KEY']
_missing = [k for k in _REQUIRED_ENV if not os.environ.get(k)]
if _missing:
    print(f"FATAL: Missing required environment variables: {', '.join(_missing)}", file=sys.stderr)
    sys.exit(1)

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Configure logging — JSON format for production, text for development

class JSONFormatter(logging.Formatter):
    def format(self, record):
        log_obj = {
            "timestamp": self.formatTime(record, self.datefmt),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        if record.exc_info and record.exc_info[0]:
            log_obj["exception"] = self.formatException(record.exc_info)
        return _json_mod.dumps(log_obj)

_handler = logging.StreamHandler()
_handler.setFormatter(JSONFormatter())
logging.basicConfig(level=logging.INFO, handlers=[_handler])
logger = logging.getLogger(__name__)

# Environment variables
EMERGENT_LLM_KEY = os.environ['EMERGENT_LLM_KEY']


def get_frontend_url() -> str:
    return os.environ['FRONTEND_URL'].replace('/api', '')


def get_admin_emails() -> list[str]:
    return [email.strip() for email in os.environ['ADMIN_EMAILS'].split(',') if email.strip()]


def is_admin_user(email: str) -> bool:
    admin_emails = get_admin_emails()
    normalized = (email or "").strip().lower()
    allowed = {(e or "").strip().lower() for e in admin_emails}
    return normalized in allowed


def get_contact_email() -> str:
    return os.environ['CONTACT_EMAIL']


def get_resend_from_email() -> str:
    return os.environ.get('RESEND_FROM_EMAIL', f"Appeal Case Manager <{os.environ['CONTACT_EMAIL']}>")


def get_payid_email() -> str:
    return os.environ.get('PAYID_EMAIL', os.environ['CONTACT_EMAIL'])


# ── Startup Warnings ──
# TIER 3: Email — notifications/password-reset will fail without these
_EMAIL_ENV = ['RESEND_API_KEY']
_email_missing = [k for k in _EMAIL_ENV if not os.environ.get(k)]
if _email_missing:
    logger.warning(f"Optional env vars missing (email features will not work): {', '.join(_email_missing)}")

# TIER 4: Security — warn if CORS is wildcard in production
_cors_raw = os.environ.get('CORS_ORIGINS', '')
_frontend = os.environ.get('FRONTEND_URL', '')
if _cors_raw.strip() == '*' and 'preview.emergentagent.com' not in _frontend:
    logger.warning("SECURITY: CORS_ORIGINS is set to '*' — restrict to specific origins for production")

# TIER 5: Optional with sensible defaults — log if missing so operator knows
_OPTIONAL_ENV = ['PAYID_EMAIL', 'RESEND_FROM_EMAIL']
_opt_missing = [k for k in _OPTIONAL_ENV if not os.environ.get(k)]
if _opt_missing:
    logger.info(f"Optional env vars using defaults: {', '.join(_opt_missing)}")


def validate_env_status() -> dict:
    """Return a diagnostic summary of all env vars without exposing values.
    Used by /api/health/env endpoint.
    """
    def _status(key):
        val = os.environ.get(key, '')
        if not val:
            return 'missing'
        if val.startswith('sk_test_') or val == 'sk_test_emergent':
            return 'test_key'
        if len(val) < 5:
            return 'suspicious'
        return 'set'

    return {
        'required': {k: _status(k) for k in _REQUIRED_ENV},
        'email': {k: _status(k) for k in _EMAIL_ENV},
        'optional': {k: _status(k) for k in _OPTIONAL_ENV},
        'security': {
            'CORS_ORIGINS': 'wildcard' if _cors_raw.strip() == '*' else 'restricted',
        },
    }

# ── Shared Rate Limiter (process-safe via slowapi) ──
from slowapi import Limiter

def _get_real_client_ip(request) -> str:
    """Extract real client IP behind Cloudflare/proxy. Falls back to direct IP."""
    return (
        request.headers.get("CF-Connecting-IP")
        or request.headers.get("X-Forwarded-For", "").split(",")[0].strip()
        or (request.client.host if request.client else "unknown")
    )

limiter = Limiter(key_func=_get_real_client_ip)
