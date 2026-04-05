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

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Environment variables
EMERGENT_LLM_KEY = os.environ['EMERGENT_LLM_KEY']


def get_frontend_url() -> str:
    return os.environ['FRONTEND_URL'].replace('/api', '')


def get_admin_emails() -> list[str]:
    return [email.strip() for email in os.environ['ADMIN_EMAILS'].split(',') if email.strip()]


def get_contact_email() -> str:
    return os.environ['CONTACT_EMAIL']
