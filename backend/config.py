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


def get_contact_email() -> str:
    return os.environ['CONTACT_EMAIL']
