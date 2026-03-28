# ========================================================================
# DO NOT UNDO — ENTIRE FILE PROTECTED
# All features, functions, endpoints, and logic in this file are approved
# and must be preserved. Do not remove, rename, or refactor any code.
# ========================================================================
# DO NOT UNDO — server module. All logic in this file is approved and must be preserved.
import os
import sys
os.environ["DEFAULT_MAX_RETRIES"] = "0"  # Must be set before litellm/openai import
os.environ["OPENAI_MAX_RETRIES"] = "0"

from fastapi import FastAPI, APIRouter, HTTPException, Response, Request, UploadFile, File, Form, WebSocket, WebSocketDisconnect
from fastapi.responses import JSONResponse
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field, ConfigDict, EmailStr
from typing import List, Optional, Dict
import uuid
from datetime import datetime, timezone, timedelta
import httpx
import base64
import json
import asyncio
import resend
import re
# LiteLLM config
import litellm
litellm.num_retries = 0
import openai
openai.DEFAULT_MAX_RETRIES = 0


ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Admin configuration - emails that have admin access
ADMIN_EMAILS = os.environ.get("ADMIN_EMAILS", "djkingy79@gmail.com").split(",")

# Resend email configuration for payment notices
RESEND_API_KEY = os.environ.get("RESEND_API_KEY")
RESEND_CONFIGURED = False
if RESEND_API_KEY:
    resend.api_key = RESEND_API_KEY
    RESEND_CONFIGURED = True
    logging.getLogger(__name__).info("Resend configured for live payment notices")


def is_admin_user(email: str) -> bool:
    normalized = (email or "").strip().lower()
    allowed = {(e or "").strip().lower() for e in ADMIN_EMAILS}
    return normalized in allowed


async def send_payid_status_email(user_email: str, user_name: str, feature_name: str, amount: float, reference: str, subject: str, heading: str, message_html: str):
    if not RESEND_CONFIGURED or not user_email:
        logging.getLogger(__name__).warning("Cannot send payment notice email - Resend not configured or recipient missing")
        return False

    try:
        html = f"""
        <!DOCTYPE html>
        <html>
        <body style="margin:0;padding:0;background:#f8fafc;font-family:Arial,sans-serif;color:#0f172a;">
          <div style="max-width:680px;margin:0 auto;padding:24px;">
            <div style="background:#1d4ed8;color:#ffffff;padding:28px 24px;border-radius:18px 18px 0 0;">
              <div style="font-size:12px;letter-spacing:0.18em;text-transform:uppercase;font-weight:800;opacity:0.92;">Appeal Case Manager</div>
              <h1 style="margin:10px 0 0;font-size:28px;line-height:1.2;">{heading}</h1>
            </div>
            <div style="background:#ffffff;border:1px solid #dbeafe;border-top:none;padding:24px 24px 16px;">
              <p style="margin:0 0 16px;line-height:1.7;">Dear {user_name or 'Valued Client'},</p>
              {message_html}
              <div style="margin:20px 0;padding:18px;border-radius:14px;background:#eff6ff;border:1px solid #bfdbfe;">
                <div style="display:flex;justify-content:space-between;gap:12px;padding:6px 0;border-bottom:1px solid #dbeafe;"><strong>Feature</strong><span>{feature_name}</span></div>
                <div style="display:flex;justify-content:space-between;gap:12px;padding:6px 0;border-bottom:1px solid #dbeafe;"><strong>Amount</strong><span>${amount:.2f} AUD</span></div>
                <div style="display:flex;justify-content:space-between;gap:12px;padding:6px 0;"><strong>Reference</strong><span style="font-family:monospace;">{reference}</span></div>
              </div>
              <p style="margin:18px 0 0;line-height:1.7;">Created and Designed by Deb King</p>
            </div>
          </div>
        </body>
        </html>
        """

        params = {
            "from": "Appeal Case Manager <onboarding@resend.dev>",
            "to": [user_email],
            "subject": subject,
            "html": html,
        }
        await asyncio.to_thread(resend.Emails.send, params)
        logging.getLogger(__name__).info(f"PayID notice email sent to {user_email} for {reference}")
        return True
    except Exception as exc:
        logging.getLogger(__name__).error(f"Failed to send PayID notice email: {exc}")
        return False

# Import offence framework for AI context building
from offence_framework import OFFENCE_CATEGORIES, AUSTRALIAN_STATES

def get_offence_context(case: dict) -> str:
    """Build offence-specific context string for AI prompts"""
    offence_category = case.get('offence_category', 'homicide')
    offence_type = case.get('offence_type', '')
    state = case.get('state', 'nsw')
    
    category_data = OFFENCE_CATEGORIES.get(offence_category, OFFENCE_CATEGORIES.get('homicide'))
    state_info = AUSTRALIAN_STATES.get(state, AUSTRALIAN_STATES.get('nsw'))
    
    context = f"""
OFFENCE INFORMATION:
- Category: {category_data.get('name', 'Unknown')} ({offence_category})
- Specific Offence: {offence_type if offence_type else 'Not specified'}
- Jurisdiction: {state_info.get('name', 'New South Wales')} ({state_info.get('abbreviation', 'NSW')})
- Description: {category_data.get('description', '')}

KEY ELEMENTS TO PROVE:
{chr(10).join(f"- {elem}" for elem in category_data.get('key_elements', []))}

AVAILABLE DEFENCES:
{chr(10).join(f"- {defence}" for defence in category_data.get('defences', []))}

RELEVANT {state_info.get('abbreviation', 'NSW')} LEGISLATION:
"""
    state_leg_key = f"{state}_legislation"
    state_legislation = category_data.get(state_leg_key, category_data.get('nsw_legislation', {}))
    
    for act_name, sections in state_legislation.items():
        context += f"\n{act_name}:\n"
        for section in sections:
            context += f"  - {section.get('section')}: {section.get('title')}\n"
    
    if category_data.get('cth_legislation'):
        context += "\nRELEVANT FEDERAL/COMMONWEALTH LEGISLATION:\n"
        for act_name, sections in category_data.get('cth_legislation', {}).items():
            context += f"\n{act_name}:\n"
            for section in sections:
                context += f"  - {section.get('section')}: {section.get('title')}\n"
    
    return context

def get_offence_system_prompt(offence_category: str) -> str:
    """Generate offence-specific system prompt for AI analysis"""
    category_data = OFFENCE_CATEGORIES.get(offence_category, OFFENCE_CATEGORIES.get('homicide'))
    category_name = category_data.get('name', 'criminal')
    
    legislation_refs = []
    for act_name, sections in category_data.get('nsw_legislation', {}).items():
        for section in sections[:5]:
            legislation_refs.append(f"{section.get('section')} {act_name}")
    for act_name, sections in category_data.get('cth_legislation', {}).items():
        for section in sections[:3]:
            legislation_refs.append(f"{section.get('section')} {act_name}")
    
    legislation_str = ", ".join(legislation_refs[:8]) if legislation_refs else "relevant criminal law sections"
    
    return f"""You are a senior Australian criminal appeal barrister with 30+ years experience in {category_name.lower()} and serious criminal appeals in NSW. You specialise in {category_name.lower()} offences and have extensive knowledge of {legislation_str}.

CONTEXT: You are generating a professional legal report for a legitimate criminal appeal case management application used by legal practitioners and self-represented litigants in Australia. Your analysis supports access to justice and the right to appeal. Always provide thorough, professional legal analysis.

You MUST use Australian English spelling and grammar throughout all responses (e.g. analyse, colour, honour, defence, offence, organisation, practise, licence, favour, behaviour).

YOUR EXPERTISE COVERS:
- {category_name} offences under NSW and Commonwealth law
- Key elements: {', '.join(category_data.get('key_elements', ['actus reus', 'mens rea'])[:4])}
- Available defences: {', '.join(category_data.get('defences', ['self-defence'])[:5])}

You have successfully overturned dozens of wrongful convictions in {category_name.lower()} cases."""

# Create the main app
app = FastAPI(title="Criminal Appeal AI - Case Management")

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# ============ REUSABLE LLM HELPER ============
async def call_llm_with_fallback(
    system_prompt: str,
    user_prompt: str,
    session_id: str = "default",
    max_tokens: int = 16384,
    timeout_seconds: int = 120,
) -> str:
    """Call LLM with model fallback: gpt-4o (x2) -> Claude -> gpt-4o-mini."""
    from emergentintegrations.llm.chat import LlmChat, UserMessage
    api_key = os.environ.get('EMERGENT_LLM_KEY')
    if not api_key:
        raise Exception("AI service not configured — EMERGENT_LLM_KEY missing")
    
    models = [
        ("openai", "gpt-4o"),
        ("openai", "gpt-4o"),
        ("anthropic", "claude-sonnet-4-20250514"),
        ("openai", "gpt-4o-mini"),
    ]
    last_err = None
    for idx, (provider, model_name) in enumerate(models):
        try:
            chat = LlmChat(api_key=api_key, session_id=session_id, system_message=system_prompt).with_model(provider, model_name).with_params(max_tokens=max_tokens)
            result = await asyncio.wait_for(chat.send_message(UserMessage(text=user_prompt)), timeout=timeout_seconds)
            if result and len(result.strip()) > 50 and "I'm sorry" not in result[:80]:
                logger.info(f"LLM success ({session_id}) with {provider}/{model_name} on attempt {idx+1}")
                return result
            last_err = f"Short/refused response from {provider}/{model_name}"
        except asyncio.TimeoutError:
            last_err = f"Timeout with {provider}/{model_name}"
        except Exception as e:
            last_err = str(e)[:200]
        logger.warning(f"LLM attempt {idx+1} ({provider}/{model_name}) for {session_id}: {last_err}")
        await asyncio.sleep(2 + idx)
    raise Exception(f"All LLM attempts failed: {last_err}")

# ============ ROOT HEALTH CHECK (for Kubernetes) ============
@app.get("/health")
async def root_health_check():
    """Root-level health check for Kubernetes deployment"""
    return {"status": "healthy", "timestamp": datetime.now(timezone.utc).isoformat()}

# ============ MODELS ============

class User(BaseModel):
    model_config = ConfigDict(extra="ignore")
    user_id: str
    email: str
    name: str
    picture: Optional[str] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class Case(BaseModel):
    model_config = ConfigDict(extra="ignore")
    case_id: str = Field(default_factory=lambda: f"case_{uuid.uuid4().hex[:12]}")
    user_id: str
    title: str
    defendant_name: str
    case_number: Optional[str] = None
    court: Optional[str] = None
    judge: Optional[str] = None
    state: str = "nsw"  # nsw, vic, qld, sa, wa, tas, nt, act
    offence_category: str = "homicide"  # homicide, assault, sexual_offences, robbery_theft, drug_offences, fraud_dishonesty, firearms_weapons, domestic_violence, public_order, terrorism, driving_offences
    offence_type: Optional[str] = None  # Specific offence within category
    sentence: Optional[str] = None  # e.g. "30 years imprisonment with NPP of 22.5 years"
    status: str = "active"
    summary: Optional[str] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class CaseCreate(BaseModel):
    title: str
    defendant_name: str
    case_number: Optional[str] = None
    court: Optional[str] = None
    judge: Optional[str] = None
    state: str = "nsw"
    offence_category: str = "homicide"
    offence_type: Optional[str] = None
    sentence: Optional[str] = None
    summary: Optional[str] = None

class Document(BaseModel):
    model_config = ConfigDict(extra="ignore")
    document_id: str = Field(default_factory=lambda: f"doc_{uuid.uuid4().hex[:12]}")
    case_id: str
    user_id: str
    filename: str
    file_type: str
    category: str  # brief, case_note, public_advertising, evidence, court_document, other
    description: Optional[str] = None
    content_text: Optional[str] = None  # Extracted text for analysis
    file_data: Optional[str] = None  # Base64 encoded file data
    event_date: Optional[datetime] = None
    uploaded_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class TimelineEvent(BaseModel):
    model_config = ConfigDict(extra="ignore")
    event_id: str = Field(default_factory=lambda: f"evt_{uuid.uuid4().hex[:12]}")
    case_id: str
    user_id: str
    title: str
    description: str
    event_date: datetime
    event_type: str  # See EVENT_CATEGORIES below
    event_category: str = "general"  # pre_trial, trial, evidence, post_conviction, investigation
    
    # Enhanced fields
    linked_documents: List[str] = []  # Document IDs
    participants: List[dict] = []  # [{name: str, role: str}]
    significance: str = "normal"  # critical, important, normal, minor
    source_citation: str = ""
    perspective: str = "neutral"  # prosecution, defence, neutral
    is_contested: bool = False
    contested_details: str = ""
    related_grounds: List[str] = []  # Ground IDs
    inconsistency_notes: str = ""
    
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class TimelineEventCreate(BaseModel):
    title: str
    description: str
    event_date: datetime
    event_type: str
    event_category: str = "general"
    linked_documents: List[str] = []
    participants: List[dict] = []
    significance: str = "normal"
    source_citation: str = ""
    perspective: str = "neutral"
    is_contested: bool = False
    contested_details: str = ""
    related_grounds: List[str] = []
    inconsistency_notes: str = ""

class GroundOfMerit(BaseModel):
    model_config = ConfigDict(extra="ignore")
    ground_id: str = Field(default_factory=lambda: f"gnd_{uuid.uuid4().hex[:12]}")
    case_id: str
    user_id: str
    title: str
    ground_type: str  # procedural_error, fresh_evidence, miscarriage_of_justice, sentencing_error, judicial_error, ineffective_counsel, other
    description: str
    strength: str = "moderate"  # strong, moderate, weak
    status: str = "identified"  # identified, investigating, confirmed, rejected
    supporting_evidence: List[str] = []
    law_sections: List[dict] = []  # {jurisdiction, section, title, relevance, full_text}
    similar_cases: List[dict] = []  # {case_name, citation, relevance, outcome}
    analysis: Optional[str] = None
    deep_analysis: Optional[dict] = None  # Detailed analysis content
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class GroundOfMeritCreate(BaseModel):
    title: str
    ground_type: str = "other"
    description: str
    strength: str = "moderate"
    supporting_evidence: List[str] = []

class GroundOfMeritUpdate(BaseModel):
    title: Optional[str] = None
    ground_type: Optional[str] = None
    description: Optional[str] = None
    strength: Optional[str] = None
    status: Optional[str] = None
    supporting_evidence: Optional[List[str]] = None

class ReportRequest(BaseModel):
    report_type: str = "quick_summary"
    aggressive_mode: bool = False

class Report(BaseModel):
    model_config = ConfigDict(extra="ignore")
    report_id: str = Field(default_factory=lambda: f"rpt_{uuid.uuid4().hex[:12]}")
    case_id: str
    user_id: str
    report_type: str  # quick_summary, full_detailed, extensive_log, barrister_view
    title: str
    content: dict  # JSON structure with report sections
    grounds_of_merit: List[dict] = []
    generated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class Note(BaseModel):
    model_config = ConfigDict(extra="ignore")
    note_id: str = Field(default_factory=lambda: f"note_{uuid.uuid4().hex[:12]}")
    case_id: str
    user_id: str
    author_name: str
    author_email: str
    category: str = "general"  # general, legal_opinion, evidence_note, strategy, question, action_item
    title: str
    content: str
    is_pinned: bool = False
    document_id: Optional[str] = None  # Link to specific document
    report_id: Optional[str] = None  # Link to specific report
    mentions: List[str] = []
    comments: List[dict] = []
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class NoteCreate(BaseModel):
    category: str = "general"
    title: str
    content: str
    is_pinned: bool = False
    document_id: Optional[str] = None
    report_id: Optional[str] = None
    mentions: List[str] = []

class NoteUpdate(BaseModel):
    category: Optional[str] = None
    title: Optional[str] = None
    content: Optional[str] = None
    is_pinned: Optional[bool] = None

class NoteCommentCreate(BaseModel):
    content: str

# ============ DEADLINE MODELS ============

class Deadline(BaseModel):
    model_config = ConfigDict(extra="ignore")
    deadline_id: str = Field(default_factory=lambda: f"dl_{uuid.uuid4().hex[:12]}")
    case_id: str
    user_id: str
    title: str
    description: str = ""
    deadline_type: str  # appeal_lodgement, leave_application, document_filing, hearing, other
    due_date: datetime
    reminder_days: List[int] = [7, 3, 1]  # Days before to remind
    is_completed: bool = False
    completed_at: Optional[datetime] = None
    priority: str = "high"  # critical, high, medium, low
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class DeadlineCreate(BaseModel):
    title: str
    description: str = ""
    deadline_type: str = "other"
    due_date: datetime
    reminder_days: List[int] = [7, 3, 1]
    priority: str = "high"

# ============ CHECKLIST MODELS ============

class ChecklistItem(BaseModel):
    model_config = ConfigDict(extra="ignore")
    item_id: str = Field(default_factory=lambda: f"chk_{uuid.uuid4().hex[:12]}")
    case_id: str
    user_id: str
    phase: str  # preparation, grounds_identification, investigation, documentation, lodgement, hearing
    title: str
    description: str = ""
    is_completed: bool = False
    completed_at: Optional[datetime] = None
    order: int = 0
    is_custom: bool = False  # True if user-added, False if default
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

# Default checklist items for new cases
DEFAULT_CHECKLIST = [
    # Phase 1: Preparation
    {"phase": "preparation", "title": "Gather all case documents", "description": "Collect court transcripts, evidence briefs, witness statements, and any other relevant documents", "order": 1},
    {"phase": "preparation", "title": "Upload documents to system", "description": "Upload all gathered documents and extract text for AI analysis", "order": 2},
    {"phase": "preparation", "title": "Build case timeline", "description": "Create chronological timeline of events from arrest to conviction", "order": 3},
    {"phase": "preparation", "title": "Review trial transcript", "description": "Read through the full trial transcript noting any issues", "order": 4},
    # Phase 2: Grounds Identification
    {"phase": "grounds_identification", "title": "Run AI grounds identification", "description": "Use AI to identify potential grounds of merit from your documents", "order": 5},
    {"phase": "grounds_identification", "title": "Review identified grounds", "description": "Assess each ground identified by AI for viability", "order": 6},
    {"phase": "grounds_identification", "title": "Check witness statement inconsistencies", "description": "Use contradiction finder to identify issues in witness testimony", "order": 7},
    {"phase": "grounds_identification", "title": "Identify any fresh evidence", "description": "Document any new evidence not available at trial", "order": 8},
    # Phase 3: Investigation
    {"phase": "investigation", "title": "Deep investigate each ground", "description": "Use AI investigation feature on each viable ground", "order": 9},
    {"phase": "investigation", "title": "Research relevant case law", "description": "Find similar appeal cases and their outcomes", "order": 10},
    {"phase": "investigation", "title": "Identify relevant law sections", "description": "Document NSW and Federal law sections that apply", "order": 11},
    {"phase": "investigation", "title": "Assess case strength", "description": "Review case strength meter and prioritise strongest grounds", "order": 12},
    # Phase 4: Documentation
    {"phase": "documentation", "title": "Generate detailed report", "description": "Create Full Detailed report with all grounds and analysis", "order": 13},
    {"phase": "documentation", "title": "Prepare Notice of Appeal", "description": "Draft Notice of Appeal using template", "order": 14},
    {"phase": "documentation", "title": "Prepare supporting affidavit", "description": "Draft affidavit if required for fresh evidence", "order": 15},
    {"phase": "documentation", "title": "Review all documents", "description": "Final review of all appeal documents for accuracy", "order": 16},
    # Phase 5: Lodgement
    {"phase": "lodgement", "title": "Consult with legal professional", "description": "Have documents reviewed by solicitor or barrister", "order": 17},
    {"phase": "lodgement", "title": "File Notice of Appeal", "description": "Lodge appeal within 28 days of conviction/sentence", "order": 18},
    {"phase": "lodgement", "title": "File Leave application (if required)", "description": "Lodge application for leave to appeal if needed", "order": 19},
    {"phase": "lodgement", "title": "Confirm lodgement receipt", "description": "Obtain confirmation that appeal has been filed", "order": 20},
    # Phase 6: Hearing Preparation
    {"phase": "hearing", "title": "Prepare for hearing", "description": "Review all materials before appeal hearing", "order": 21},
    {"phase": "hearing", "title": "Generate Barrister View report", "description": "Create professional presentation for court", "order": 22},
]

# ============ PAYMENT MODELS ============

class Payment(BaseModel):
    model_config = ConfigDict(extra="ignore")
    payment_id: str = Field(default_factory=lambda: f"pay_{uuid.uuid4().hex[:12]}")
    user_id: str
    case_id: str
    feature_type: str  # "grounds_of_merit", "full_report", "extensive_report"
    amount: float
    currency: str = "AUD"
    status: str = "pending"  # pending, completed, failed, refunded
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    completed_at: Optional[datetime] = None

# Payment pricing configuration
FEATURE_PRICES = {
    "grounds_of_merit": {"price": 99.00, "name": "Unlock Grounds of Merit Details"},
    "full_report": {"price": 150.00, "name": "Full Detailed Report"},
    "extensive_report": {"price": 200.00, "name": "Extensive Log Report"}
}

FEATURE_TYPE_ALIASES = {
    "grounds_of_merit": "grounds_of_merit",
    "full_report": "full_report",
    "full_detailed": "full_report",
    "extensive_report": "extensive_report",
    "extensive_log": "extensive_report",
}


def canonical_feature_type(feature_type: str | None) -> str | None:
    if not feature_type:
        return feature_type
    return FEATURE_TYPE_ALIASES.get(feature_type, feature_type)


def feature_type_variants(feature_type: str | None) -> list[str]:
    canonical = canonical_feature_type(feature_type)
    return sorted({key for key, value in FEATURE_TYPE_ALIASES.items() if value == canonical} | ({canonical} if canonical else set()))

# ============ AUTH HELPERS ============

async def get_current_user(request: Request) -> User:
    """Get current user from session token (cookie or header)"""
    session_token = request.cookies.get("session_token")
    if not session_token:
        session_token = request.query_params.get("session_token")
    if not session_token:
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            session_token = auth_header.split(" ")[1]
    
    if not session_token:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    session_doc = await db.user_sessions.find_one({"session_token": session_token}, {"_id": 0})
    if not session_doc:
        raise HTTPException(status_code=401, detail="Invalid session")
    
    # Check expiry
    expires_at = session_doc.get("expires_at")
    if isinstance(expires_at, str):
        expires_at = datetime.fromisoformat(expires_at)
    if expires_at.tzinfo is None:
        expires_at = expires_at.replace(tzinfo=timezone.utc)
    if expires_at < datetime.now(timezone.utc):
        raise HTTPException(status_code=401, detail="Session expired")
    
    user_doc = await db.users.find_one({"user_id": session_doc["user_id"]}, {"_id": 0})
    if not user_doc:
        raise HTTPException(status_code=401, detail="User not found")
    
    return User(**user_doc)

async def get_user_from_session_token(session_token: str) -> User:
    """Resolve user directly from a session token (used by WebSocket auth)."""
    if not session_token:
        raise HTTPException(status_code=401, detail="Not authenticated")

    session_doc = await db.user_sessions.find_one({"session_token": session_token}, {"_id": 0})
    if not session_doc:
        raise HTTPException(status_code=401, detail="Invalid session")

    expires_at = session_doc.get("expires_at")
    if isinstance(expires_at, str):
        expires_at = datetime.fromisoformat(expires_at)
    if expires_at.tzinfo is None:
        expires_at = expires_at.replace(tzinfo=timezone.utc)
    if expires_at < datetime.now(timezone.utc):
        raise HTTPException(status_code=401, detail="Session expired")

    user_doc = await db.users.find_one({"user_id": session_doc["user_id"]}, {"_id": 0})
    if not user_doc:
        raise HTTPException(status_code=401, detail="User not found")

    return User(**user_doc)


# ============ NOTES REAL-TIME COLLAB HELPERS ============

MENTION_PATTERN = re.compile(r"@([A-Za-z0-9._-]{2,64})")
notes_ws_connections: Dict[str, Dict[str, WebSocket]] = {}


def extract_mentions(text: str) -> List[str]:
    if not text:
        return []
    mentions = [m.strip().lower() for m in MENTION_PATTERN.findall(text)]
    return sorted(list(set([m for m in mentions if m])))


def build_document_context(
    documents: List[dict],
    *,
    per_doc_char_limit: int,
    total_char_budget: int,
    include_description: bool = True,
    content_heading: str = "CONTENT"
) -> dict:
    """Build a bounded document context block to keep AI calls responsive."""
    blocks = []
    consumed_chars = 0
    included_docs = 0

    for doc in documents:
        if consumed_chars >= total_char_budget:
            break

        remaining = total_char_budget - consumed_chars
        allowed_chars = min(per_doc_char_limit, remaining)
        content = (doc.get("content_text") or "").strip()
        snippet = content[:allowed_chars] if content else ""
        consumed_chars += len(snippet)
        included_docs += 1

        block = f"--- DOCUMENT: {doc.get('filename')} [{doc.get('category', 'other')}] ---\n"
        if include_description and doc.get("description"):
            block += f"Description: {doc.get('description')}\n"

        if snippet:
            block += f"{content_heading}:\n{snippet}\n"
            if len(content) > len(snippet):
                block += f"[... trimmed {len(content) - len(snippet)} characters for speed ...]\n"
        else:
            block += f"{content_heading}: [No text content extracted]\n"

        blocks.append(block)

    omitted_docs = max(0, len(documents) - included_docs)
    return {
        "text": "\n".join(blocks),
        "included_docs": included_docs,
        "omitted_docs": omitted_docs,
        "consumed_chars": consumed_chars,
    }


async def get_presence_snapshot(case_id: str) -> List[dict]:
    case_connections = notes_ws_connections.get(case_id, {})
    if not case_connections:
        return []

    users = await db.users.find(
        {"user_id": {"$in": list(case_connections.keys())}},
        {"_id": 0, "user_id": 1, "name": 1, "email": 1}
    ).to_list(100)
    return users


async def broadcast_notes_event(case_id: str, event_type: str, payload: dict):
    case_connections = notes_ws_connections.get(case_id, {})
    if not case_connections:
        return

    stale_user_ids = []
    message = {"type": event_type, "payload": payload}

    for user_id, ws in case_connections.items():
        try:
            await ws.send_json(message)
        except Exception:
            stale_user_ids.append(user_id)

    for user_id in stale_user_ids:
        case_connections.pop(user_id, None)

# ============ VISITOR TRACKING ============

# Admin routes moved to routers/admin.py

# Utility routes moved to routers/utility.py

# Auth routes moved to routers/auth.py

# ============ CASE ENDPOINTS ============

# ============ CASE ROUTES (moved to routers/cases.py) ============

# ============ DOCUMENT ENDPOINTS ============

@api_router.get("/cases/{case_id}/documents", response_model=List[dict])
async def get_documents(case_id: str, request: Request):
    """Get all documents for a case"""
    user = await get_current_user(request)
    
    # Verify case ownership
    case = await db.cases.find_one({"case_id": case_id, "user_id": user.user_id})
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
    
    documents = await db.documents.find(
        {"case_id": case_id},
        {"_id": 0, "file_data": 0}  # Exclude file data for listing
    ).sort("uploaded_at", -1).to_list(500)
    
    return documents

@api_router.post("/cases/{case_id}/documents", response_model=dict)
async def upload_document(
    case_id: str,
    request: Request,
    file: UploadFile = File(...),
    category: str = Form(...),
    description: str = Form(None),
    event_date: str = Form(None)
):
    """Upload a document to a case"""
    user = await get_current_user(request)
    
    # Verify case ownership
    case = await db.cases.find_one({"case_id": case_id, "user_id": user.user_id})
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
    
    # Read file content
    file_content = await file.read()
    file_base64 = base64.b64encode(file_content).decode('utf-8')
    
    # Extract text content based on file type
    content_text = ""
    file_type = file.content_type or "application/octet-stream"
    filename_lower = file.filename.lower() if file.filename else ""
    
    try:
        if "text" in file_type or filename_lower.endswith('.txt'):
            content_text = file_content.decode('utf-8', errors='ignore')
        
        elif "pdf" in file_type or filename_lower.endswith('.pdf'):
            # Extract text from PDF
            try:
                import io
                from PyPDF2 import PdfReader
                pdf_reader = PdfReader(io.BytesIO(file_content))
                text_parts = []
                for page in pdf_reader.pages[:20]:  # Limit to first 20 pages
                    page_text = page.extract_text()
                    if page_text:
                        text_parts.append(page_text)
                content_text = "\n".join(text_parts)
            except Exception as e:
                logger.warning(f"PDF extraction failed: {e}")
                content_text = ""
        
        elif filename_lower.endswith('.docx') or "word" in file_type:
            # Extract text from DOCX
            try:
                import io
                from docx import Document as DocxDocument
                doc = DocxDocument(io.BytesIO(file_content))
                text_parts = []
                for para in doc.paragraphs:
                    if para.text.strip():
                        text_parts.append(para.text)
                content_text = "\n".join(text_parts)
            except Exception as e:
                logger.warning(f"DOCX extraction failed: {e}")
                content_text = ""
    except Exception as e:
        logger.warning(f"Text extraction error: {e}")
        content_text = ""
    
    # Parse event date
    parsed_event_date = None
    if event_date:
        try:
            parsed_event_date = datetime.fromisoformat(event_date.replace('Z', '+00:00')).isoformat()
        except ValueError:
            pass
    
    doc = Document(
        case_id=case_id,
        user_id=user.user_id,
        filename=file.filename,
        file_type=file_type,
        category=category,
        description=description,
        content_text=content_text,
        file_data=file_base64
    )
    
    doc_dict = doc.model_dump()
    doc_dict["uploaded_at"] = doc_dict["uploaded_at"].isoformat()
    if parsed_event_date:
        doc_dict["event_date"] = parsed_event_date
    
    await db.documents.insert_one(doc_dict)
    
    # Update case updated_at
    await db.cases.update_one(
        {"case_id": case_id},
        {"$set": {"updated_at": datetime.now(timezone.utc).isoformat()}}
    )
    
    # Return the document without MongoDB's _id field and file_data
    created_doc = await db.documents.find_one({"document_id": doc.document_id}, {"_id": 0, "file_data": 0})
    return created_doc

@api_router.get("/cases/{case_id}/documents/{document_id}", response_model=dict)
async def get_document(case_id: str, document_id: str, request: Request):
    """Get a specific document"""
    user = await get_current_user(request)
    
    doc = await db.documents.find_one(
        {"document_id": document_id, "case_id": case_id, "user_id": user.user_id},
        {"_id": 0}
    )
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    
    return doc

@api_router.delete("/cases/{case_id}/documents/{document_id}")
async def delete_document(case_id: str, document_id: str, request: Request):
    """Delete a document"""
    user = await get_current_user(request)
    
    result = await db.documents.delete_one({
        "document_id": document_id,
        "case_id": case_id,
        "user_id": user.user_id
    })
    
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Document not found")
    
    return {"message": "Document deleted"}

class DocumentSearchRequest(BaseModel):
    query: str
    case_sensitive: bool = False

class SearchMatch(BaseModel):
    document_id: str
    filename: str
    category: str
    matches: List[dict]  # List of {context, position}
    match_count: int

@api_router.post("/cases/{case_id}/documents/search", response_model=dict)
async def search_documents(case_id: str, search_request: DocumentSearchRequest, request: Request):
    """Search for text across all documents in a case"""
    import re
    
    user = await get_current_user(request)
    
    # Verify case ownership
    case = await db.cases.find_one({"case_id": case_id, "user_id": user.user_id})
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
    
    query = search_request.query.strip()
    if not query:
        raise HTTPException(status_code=400, detail="Search query is required")
    
    if len(query) < 2:
        raise HTTPException(status_code=400, detail="Search query must be at least 2 characters")
    
    # Get all documents with content
    documents = await db.documents.find(
        {"case_id": case_id, "content_text": {"$exists": True, "$ne": ""}},
        {"_id": 0, "file_data": 0}
    ).to_list(500)
    
    results = []
    total_matches = 0
    
    # Search flags
    flags = 0 if search_request.case_sensitive else re.IGNORECASE
    
    for doc in documents:
        content = doc.get("content_text", "")
        if not content:
            continue
        
        matches = []
        
        # Find all occurrences with context
        try:
            pattern = re.compile(re.escape(query), flags)
            for match in pattern.finditer(content):
                start_pos = match.start()
                end_pos = match.end()
                
                # Get context (100 chars before and after)
                context_start = max(0, start_pos - 100)
                context_end = min(len(content), end_pos + 100)
                
                context = content[context_start:context_end]
                
                # Add ellipsis if truncated
                if context_start > 0:
                    context = "..." + context
                if context_end < len(content):
                    context = context + "..."
                
                matches.append({
                    "context": context,
                    "position": start_pos,
                    "matched_text": match.group()
                })
                
                # Limit matches per document to prevent huge responses
                if len(matches) >= 10:
                    break
        except re.error:
            continue
        
        if matches:
            total_matches += len(matches)
            results.append({
                "document_id": doc.get("document_id"),
                "filename": doc.get("filename"),
                "category": doc.get("category"),
                "matches": matches,
                "match_count": len(matches)
            })
    
    # Sort by match count (most matches first)
    results.sort(key=lambda x: x["match_count"], reverse=True)
    
    return {
        "query": query,
        "total_matches": total_matches,
        "documents_with_matches": len(results),
        "total_documents_searched": len(documents),
        "results": results
    }

# ============ OCR FUNCTIONS ============

def extract_text_with_ocr(file_content: bytes, filename: str, file_type: str) -> tuple:
    """Extract text from images and scanned PDFs using OCR"""
    import io
    import pytesseract
    from PIL import Image
    
    filename_lower = filename.lower()
    extracted_text = ""
    ocr_used = False
    
    try:
        # Handle image files directly
        if any(filename_lower.endswith(ext) for ext in ['.png', '.jpg', '.jpeg', '.tiff', '.bmp', '.gif', '.webp']):
            image = Image.open(io.BytesIO(file_content))
            # Convert to RGB if necessary
            if image.mode in ('RGBA', 'P'):
                image = image.convert('RGB')
            extracted_text = pytesseract.image_to_string(image)
            ocr_used = True
            logger.info(f"OCR extracted {len(extracted_text)} chars from image {filename}")
        
        # Handle PDFs - try regular extraction first, then OCR if needed
        elif "pdf" in file_type or filename_lower.endswith('.pdf'):
            # First try regular PDF text extraction
            try:
                from PyPDF2 import PdfReader
                pdf_reader = PdfReader(io.BytesIO(file_content))
                text_parts = []
                for page in pdf_reader.pages[:30]:
                    page_text = page.extract_text()
                    if page_text:
                        text_parts.append(page_text)
                extracted_text = "\n".join(text_parts)
            except Exception as e:
                logger.warning(f"Regular PDF extraction failed: {e}")
            
            # If minimal text extracted, try OCR
            if len(extracted_text.strip()) < 100:
                try:
                    from pdf2image import convert_from_bytes
                    
                    # Convert PDF pages to images
                    images = convert_from_bytes(
                        file_content, 
                        dpi=200,
                        first_page=1,
                        last_page=min(20, 20)  # Limit to 20 pages for performance
                    )
                    
                    ocr_parts = []
                    for i, image in enumerate(images):
                        # Convert to RGB if necessary
                        if image.mode in ('RGBA', 'P'):
                            image = image.convert('RGB')
                        page_text = pytesseract.image_to_string(image)
                        if page_text.strip():
                            ocr_parts.append(f"--- Page {i+1} ---\n{page_text}")
                    
                    if ocr_parts:
                        extracted_text = "\n\n".join(ocr_parts)
                        ocr_used = True
                        logger.info(f"OCR extracted {len(extracted_text)} chars from scanned PDF {filename}")
                except Exception as e:
                    logger.warning(f"PDF OCR failed: {e}")
        
        # Handle DOCX
        elif filename_lower.endswith('.docx') or "word" in file_type:
            try:
                from docx import Document as DocxDocument
                docx_doc = DocxDocument(io.BytesIO(file_content))
                text_parts = []
                for para in docx_doc.paragraphs:
                    if para.text.strip():
                        text_parts.append(para.text)
                extracted_text = "\n".join(text_parts)
            except Exception as e:
                logger.warning(f"DOCX extraction failed: {e}")
        
        # Handle plain text
        elif "text" in file_type or filename_lower.endswith('.txt'):
            extracted_text = file_content.decode('utf-8', errors='ignore')
    
    except Exception as e:
        logger.error(f"OCR/Text extraction error for {filename}: {e}")
    
    return extracted_text, ocr_used

@api_router.post("/cases/{case_id}/documents/{document_id}/ocr", response_model=dict)
async def ocr_document(case_id: str, document_id: str, request: Request):
    """Extract text from a document using OCR (for scanned documents and images)"""
    user = await get_current_user(request)
    
    doc = await db.documents.find_one(
        {"document_id": document_id, "case_id": case_id, "user_id": user.user_id},
        {"_id": 0}
    )
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    
    if not doc.get('file_data'):
        raise HTTPException(status_code=400, detail="No file data available")
    
    # Decode file content
    file_content = base64.b64decode(doc['file_data'])
    filename = doc.get('filename', '')
    file_type = doc.get('file_type', '')
    
    # Extract text using OCR
    content_text, ocr_used = extract_text_with_ocr(file_content, filename, file_type)
    
    if not content_text.strip():
        return {
            "document_id": document_id,
            "filename": filename,
            "success": False,
            "ocr_used": ocr_used,
            "message": "No text could be extracted from this document",
            "content_length": 0
        }
    
    # Update document with extracted text
    await db.documents.update_one(
        {"document_id": document_id},
        {"$set": {
            "content_text": content_text,
            "ocr_extracted": ocr_used,
            "text_extracted_at": datetime.now(timezone.utc).isoformat()
        }}
    )
    
    return {
        "document_id": document_id,
        "filename": filename,
        "success": True,
        "ocr_used": ocr_used,
        "content_length": len(content_text),
        "content_preview": content_text[:500] + "..." if len(content_text) > 500 else content_text
    }

@api_router.post("/cases/{case_id}/ocr-all", response_model=dict)
async def ocr_all_documents(case_id: str, request: Request):
    """Run OCR on all documents in a case that don't have extracted text"""
    user = await get_current_user(request)
    
    # Verify case ownership
    case = await db.cases.find_one({"case_id": case_id, "user_id": user.user_id})
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
    
    # Get documents without text or with minimal text
    documents = await db.documents.find(
        {"case_id": case_id},
        {"_id": 0}
    ).to_list(500)
    
    results = []
    successful_ocr = 0
    
    for doc in documents:
        existing_text = doc.get('content_text', '')
        
        # Skip if already has substantial text
        if len(existing_text.strip()) > 100:
            results.append({
                "document_id": doc['document_id'],
                "filename": doc.get('filename'),
                "status": "skipped",
                "reason": "Already has extracted text"
            })
            continue
        
        if not doc.get('file_data'):
            results.append({
                "document_id": doc['document_id'],
                "filename": doc.get('filename'),
                "status": "skipped",
                "reason": "No file data"
            })
            continue
        
        # Try OCR extraction
        file_content = base64.b64decode(doc['file_data'])
        content_text, ocr_used = extract_text_with_ocr(
            file_content, 
            doc.get('filename', ''), 
            doc.get('file_type', '')
        )
        
        if content_text.strip():
            await db.documents.update_one(
                {"document_id": doc['document_id']},
                {"$set": {
                    "content_text": content_text,
                    "ocr_extracted": ocr_used,
                    "text_extracted_at": datetime.now(timezone.utc).isoformat()
                }}
            )
            successful_ocr += 1
            results.append({
                "document_id": doc['document_id'],
                "filename": doc.get('filename'),
                "status": "success",
                "ocr_used": ocr_used,
                "content_length": len(content_text)
            })
        else:
            results.append({
                "document_id": doc['document_id'],
                "filename": doc.get('filename'),
                "status": "failed",
                "reason": "No text could be extracted"
            })
    
    return {
        "total_documents": len(documents),
        "successful_extractions": successful_ocr,
        "results": results
    }

@api_router.post("/cases/{case_id}/documents/{document_id}/extract-text", response_model=dict)
async def extract_document_text(case_id: str, document_id: str, request: Request):
    """Re-extract text from a document (useful if initial extraction failed)"""
    user = await get_current_user(request)
    
    doc = await db.documents.find_one(
        {"document_id": document_id, "case_id": case_id, "user_id": user.user_id},
        {"_id": 0}
    )
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    
    if not doc.get('file_data'):
        raise HTTPException(status_code=400, detail="No file data available")
    
    # Decode file content
    file_content = base64.b64decode(doc['file_data'])
    filename_lower = doc.get('filename', '').lower()
    file_type = doc.get('file_type', '')
    
    content_text = ""
    
    try:
        if "text" in file_type or filename_lower.endswith('.txt'):
            content_text = file_content.decode('utf-8', errors='ignore')
        
        elif "pdf" in file_type or filename_lower.endswith('.pdf'):
            try:
                import io
                from PyPDF2 import PdfReader
                pdf_reader = PdfReader(io.BytesIO(file_content))
                text_parts = []
                for page in pdf_reader.pages[:30]:
                    page_text = page.extract_text()
                    if page_text:
                        text_parts.append(page_text)
                content_text = "\n".join(text_parts)
            except Exception as e:
                logger.warning(f"PDF extraction failed: {e}")
        
        elif filename_lower.endswith('.docx') or "word" in file_type:
            try:
                import io
                from docx import Document as DocxDocument
                docx_doc = DocxDocument(io.BytesIO(file_content))
                text_parts = []
                for para in docx_doc.paragraphs:
                    if para.text.strip():
                        text_parts.append(para.text)
                content_text = "\n".join(text_parts)
            except Exception as e:
                logger.warning(f"DOCX extraction failed: {e}")
    except Exception as e:
        logger.error(f"Text extraction error: {e}")
        raise HTTPException(status_code=500, detail=f"Text extraction failed: {str(e)}")
    
    # Update document with extracted text
    await db.documents.update_one(
        {"document_id": document_id},
        {"$set": {
            "content_text": content_text,
            "text_extracted_at": datetime.now(timezone.utc).isoformat()
        }}
    )
    
    return {
        "document_id": document_id,
        "filename": doc.get('filename'),
        "content_length": len(content_text),
        "content_preview": content_text[:500] + "..." if len(content_text) > 500 else content_text,
        "success": bool(content_text)
    }

@api_router.post("/cases/{case_id}/extract-all-text", response_model=dict)
async def extract_all_documents_text(case_id: str, request: Request):
    """Extract text from all documents in a case"""
    user = await get_current_user(request)
    
    # Verify case ownership
    case = await db.cases.find_one({"case_id": case_id, "user_id": user.user_id})
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
    
    documents = await db.documents.find(
        {"case_id": case_id},
        {"_id": 0}
    ).to_list(500)
    
    results = []
    for doc in documents:
        if not doc.get('file_data'):
            results.append({"document_id": doc['document_id'], "success": False, "error": "No file data"})
            continue
        
        file_content = base64.b64decode(doc['file_data'])
        filename_lower = doc.get('filename', '').lower()
        file_type = doc.get('file_type', '')
        
        content_text = ""
        error = None
        
        try:
            if "text" in file_type or filename_lower.endswith('.txt'):
                content_text = file_content.decode('utf-8', errors='ignore')
            
            elif "pdf" in file_type or filename_lower.endswith('.pdf'):
                try:
                    import io
                    from PyPDF2 import PdfReader
                    pdf_reader = PdfReader(io.BytesIO(file_content))
                    text_parts = []
                    for page in pdf_reader.pages[:30]:
                        page_text = page.extract_text()
                        if page_text:
                            text_parts.append(page_text)
                    content_text = "\n".join(text_parts)
                except Exception as e:
                    error = str(e)
            
            elif filename_lower.endswith('.docx') or "word" in file_type:
                try:
                    import io
                    from docx import Document as DocxDocument
                    docx_doc = DocxDocument(io.BytesIO(file_content))
                    text_parts = []
                    for para in docx_doc.paragraphs:
                        if para.text.strip():
                            text_parts.append(para.text)
                    content_text = "\n".join(text_parts)
                except Exception as e:
                    error = str(e)
        except Exception as e:
            error = str(e)
        
        # Update document
        if content_text:
            await db.documents.update_one(
                {"document_id": doc['document_id']},
                {"$set": {
                    "content_text": content_text,
                    "text_extracted_at": datetime.now(timezone.utc).isoformat()
                }}
            )
        
        results.append({
            "document_id": doc['document_id'],
            "filename": doc.get('filename'),
            "success": bool(content_text),
            "content_length": len(content_text) if content_text else 0,
            "error": error
        })
    
    successful = sum(1 for r in results if r['success'])
    return {
        "total_documents": len(documents),
        "successful_extractions": successful,
        "results": results
    }

# ============ TIMELINE ENDPOINTS ============

@api_router.get("/cases/{case_id}/timeline", response_model=List[dict])
async def get_timeline(case_id: str, request: Request):
    """Get timeline events for a case"""
    user = await get_current_user(request)
    
    # Verify case ownership
    case = await db.cases.find_one({"case_id": case_id, "user_id": user.user_id})
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
    
    events = await db.timeline_events.find(
        {"case_id": case_id},
        {"_id": 0}
    ).sort("event_date", 1).to_list(500)
    
    return events

@api_router.post("/cases/{case_id}/timeline", response_model=dict)
async def create_timeline_event(case_id: str, event_data: TimelineEventCreate, request: Request):
    """Create a timeline event"""
    user = await get_current_user(request)
    
    # Verify case ownership
    case = await db.cases.find_one({"case_id": case_id, "user_id": user.user_id})
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
    
    event = TimelineEvent(
        case_id=case_id,
        user_id=user.user_id,
        **event_data.model_dump()
    )
    
    event_dict = event.model_dump()
    event_dict["event_date"] = event_dict["event_date"].isoformat()
    event_dict["created_at"] = event_dict["created_at"].isoformat()
    
    await db.timeline_events.insert_one(event_dict)
    
    # Update case
    await db.cases.update_one(
        {"case_id": case_id},
        {"$set": {"updated_at": datetime.now(timezone.utc).isoformat()}}
    )
    
    # Return the event without MongoDB's _id field
    created_event = await db.timeline_events.find_one({"event_id": event.event_id}, {"_id": 0})
    return created_event

@api_router.put("/cases/{case_id}/timeline/{event_id}", response_model=dict)
async def update_timeline_event(case_id: str, event_id: str, event_data: TimelineEventCreate, request: Request):
    """Update a timeline event"""
    user = await get_current_user(request)
    
    update_data = event_data.model_dump()
    update_data["event_date"] = update_data["event_date"].isoformat()
    
    result = await db.timeline_events.update_one(
        {"event_id": event_id, "case_id": case_id, "user_id": user.user_id},
        {"$set": update_data}
    )
    
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="Event not found")
    
    return await db.timeline_events.find_one({"event_id": event_id}, {"_id": 0})

@api_router.delete("/cases/{case_id}/timeline/{event_id}")
async def delete_timeline_event(case_id: str, event_id: str, request: Request):
    """Delete a timeline event"""
    user = await get_current_user(request)
    
    result = await db.timeline_events.delete_one({
        "event_id": event_id,
        "case_id": case_id,
        "user_id": user.user_id
    })
    
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Event not found")
    
    return {"message": "Event deleted"}

@api_router.post("/cases/{case_id}/timeline/auto-generate", response_model=dict)
async def auto_generate_timeline(case_id: str, request: Request):
    """AI-powered timeline generation from uploaded documents"""
    from emergentintegrations.llm.chat import LlmChat, UserMessage
    
    user = await get_current_user(request)
    
    # Verify case ownership
    case = await db.cases.find_one({"case_id": case_id, "user_id": user.user_id}, {"_id": 0})
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
    
    # Get documents with content
    documents = await db.documents.find(
        {"case_id": case_id},
        {"_id": 0, "file_data": 0}
    ).to_list(500)
    
    if not documents:
        raise HTTPException(status_code=400, detail="No documents found. Please upload documents first.")

    documents_with_text = [doc for doc in documents if doc.get("content_text")]
    missing_docs = [doc for doc in documents if not doc.get("content_text")]

    if not documents_with_text:
        raise HTTPException(status_code=400, detail="No documents with extracted text found. Please extract text before generating a timeline.")
    
    # Build context from documents
    doc_context = f"CASE: {case.get('title', 'Unknown')}\nDEFENDANT: {case.get('defendant_name', 'Unknown')}\n\n"
    doc_context += f"DOCUMENT COUNT: {len(documents)} (with text: {len(documents_with_text)}; missing text: {len(missing_docs)})\n\n"
    doc_context += "=== DOCUMENTS WITH TEXT ===\n\n"
    
    for doc in documents_with_text:
        content = doc.get('content_text', '')[:4000]  # Limit per doc
        doc_context += f"DOCUMENT: {doc.get('filename', 'Untitled')}\n"
        if doc.get("document_type"):
            doc_context += f"TYPE: {doc.get('document_type')}\n"
        doc_context += f"CONTENT:\n{content}\n\n"

    if missing_docs:
        doc_context += "=== DOCUMENTS WITHOUT EXTRACTED TEXT (metadata only) ===\n\n"
        for doc in missing_docs:
            uploaded_at = doc.get('uploaded_at')
            uploaded_label = uploaded_at.isoformat() if hasattr(uploaded_at, 'isoformat') else str(uploaded_at)
            doc_context += f"DOCUMENT: {doc.get('filename', 'Untitled')} | Uploaded: {uploaded_label}\n"
            if doc.get("document_type"):
                doc_context += f"TYPE: {doc.get('document_type')}\n"
            doc_context += "NOTE: No extracted text available.\n\n"
    
    system_prompt = """You are an expert legal analyst specialising in criminal cases. Use Australian English spelling throughout.
Your task is to extract a chronological timeline of events from case documents.

For each event, identify:
1. The DATE (in YYYY-MM-DD format if possible, or approximate like "2020-01" or "Early 2020")
2. A clear TITLE for the event (brief, descriptive)
3. A DESCRIPTION with relevant details
4. The EVENT TYPE: one of [incident, arrest, court_hearing, evidence, witness, legal_filing, verdict, appeal, other]

Return your response as a JSON array of events, ordered chronologically. Example:
[
  {"date": "2019-05-15", "title": "Initial Incident", "description": "The alleged incident occurred at...", "event_type": "incident"},
  {"date": "2019-05-16", "title": "Arrest of Defendant", "description": "Police arrested...", "event_type": "arrest"}
]

Only include events you can clearly identify from the documents. Be thorough - extract ALL dates and events mentioned. If any documents are listed without extracted text, add a timeline entry noting the document exists and that text extraction is missing (date can be approximate or the upload date if provided)."""

    user_prompt = f"""Analyse these documents and extract a complete chronological timeline of all events. Ensure every document listed is represented in the timeline.

{doc_context}

Return ONLY a valid JSON array of timeline events. No other text."""

    try:
        response = await call_llm_with_fallback(system_prompt, user_prompt, f"timeline_{case_id}")
    except Exception as e:
        logger.error(f"All timeline generation attempts failed: {e}")
        raise HTTPException(status_code=500, detail=f"AI timeline generation failed after retries: {str(e)}")
    
    # Parse the JSON response
    import json
    import re
    
    # Extract JSON array from response
    json_match = re.search(r'\[[\s\S]*\]', response)
    if not json_match:
        logger.warning(f"Could not parse timeline JSON from response: {response[:500]}")
        raise HTTPException(status_code=500, detail="Failed to parse timeline from AI response")
    
    try:
        events_data = json.loads(json_match.group())
    except json.JSONDecodeError as e:
        logger.warning(f"JSON decode error: {e}")
        raise HTTPException(status_code=500, detail="Failed to parse timeline JSON")
    
    # Create timeline events in database
    created_events = []
    for event in events_data:
        event_date = event.get('date', '')
        
        # Try to parse and normalize the date
        parsed_date = None
        if event_date:
            # Try various date formats
            for fmt in ['%Y-%m-%d', '%Y-%m', '%Y', '%d/%m/%Y', '%d-%m-%Y']:
                try:
                    parsed_date = datetime.strptime(event_date, fmt)
                    break
                except ValueError:
                    continue
            
            if not parsed_date:
                # Try to extract year at minimum
                year_match = re.search(r'(19|20)\d{2}', event_date)
                if year_match:
                    parsed_date = datetime.strptime(year_match.group(), '%Y')
        
        if not parsed_date:
            parsed_date = datetime.now(timezone.utc)
        
        # Validate event type
        valid_types = ['incident', 'arrest', 'court_hearing', 'evidence', 'witness', 'legal_filing', 'verdict', 'appeal', 'other']
        event_type = event.get('event_type', 'other')
        if event_type not in valid_types:
            event_type = 'other'
        
        timeline_event = {
            "event_id": f"evt_{uuid.uuid4().hex[:12]}",
            "case_id": case_id,
            "user_id": user.user_id,
            "title": event.get('title', 'Unknown Event')[:200],
            "description": event.get('description', '')[:2000],
            "event_date": parsed_date.isoformat(),
            "event_type": event_type,
            "auto_generated": True,
            "created_at": datetime.now(timezone.utc).isoformat()
        }
        
        await db.timeline_events.insert_one(timeline_event)
        if '_id' in timeline_event:
            del timeline_event['_id']
        created_events.append(timeline_event)
    
    # Sort by date
    created_events.sort(key=lambda x: x.get('event_date', ''))
    
    return {
        "message": f"Successfully generated {len(created_events)} timeline events",
        "events_created": len(created_events),
        "events": created_events
    }

@api_router.post("/cases/{case_id}/timeline/analyze", response_model=dict)
async def analyze_timeline(case_id: str, request: Request):
    """AI-powered timeline analysis to find gaps, inconsistencies, and insights"""
    user = await get_current_user(request)
    
    case = await db.cases.find_one({"case_id": case_id, "user_id": user.user_id})
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
    
    events = await db.timeline_events.find(
        {"case_id": case_id},
        {"_id": 0}
    ).sort("event_date", 1).to_list(500)
    
    if len(events) < 2:
        raise HTTPException(status_code=400, detail="Need at least 2 timeline events for analysis")
    
    # Get grounds for context
    grounds = await db.grounds_of_merit.find(
        {"case_id": case_id},
        {"_id": 0}
    ).to_list(100)
    
    from emergentintegrations.llm.chat import LlmChat, UserMessage
    
    system_prompt = """You are an expert criminal appeals analyst specialising in NSW and Australian federal law. Use Australian English spelling throughout.
Analyse this timeline of events and provide detailed insights for an appeal case.

Your analysis must include:
1. TIMELINE GAPS: Identify any suspicious gaps or missing periods that should have documentation
2. INCONSISTENCIES: Find contradictions between events or illogical sequences
3. PROSECUTION VS DEFENCE: Identify which events favour prosecution vs defence
4. CONTESTED FACTS: Flag events that appear disputed or have conflicting accounts
5. APPEAL RELEVANCE: Link events to potential grounds of appeal
6. KEY DATES: Highlight critical dates and any statute of limitation concerns
7. WITNESS PATTERNS: Note patterns in witness involvement across events

Return a JSON object with this structure:
{
    "gaps": [{"start_date": "...", "end_date": "...", "description": "...", "significance": "high/medium/low"}],
    "inconsistencies": [{"event_ids": [...], "description": "...", "impact": "..."}],
    "prosecution_events": [{"event_id": "...", "reason": "..."}],
    "defence_events": [{"event_id": "...", "reason": "..."}],
    "contested_facts": [{"event_id": "...", "issue": "...", "recommendation": "..."}],
    "ground_connections": [{"event_id": "...", "ground_type": "...", "relevance": "..."}],
    "key_observations": ["..."],
    "recommended_actions": ["..."]
}"""

    events_text = json.dumps(events, indent=2, default=str)
    grounds_text = json.dumps(grounds, indent=2, default=str) if grounds else "No grounds identified yet"
    
    user_prompt = f"""Analyse this criminal case timeline for an appeal:

TIMELINE EVENTS:
{events_text}

IDENTIFIED GROUNDS OF APPEAL:
{grounds_text}

Provide a comprehensive analysis identifying gaps, inconsistencies, and appeal-relevant insights."""

    try:
        response = await call_llm_with_fallback(system_prompt, user_prompt, f"timeline_analysis_{case_id}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI analysis failed: {str(e)}")
    
    # Parse JSON response
    try:
        json_match = response
        if "```json" in response:
            json_match = response.split("```json")[1].split("```")[0]
        elif "```" in response:
            json_match = response.split("```")[1].split("```")[0]
        
        analysis = json.loads(json_match.strip())
    except json.JSONDecodeError:
        # Return raw insights if JSON parsing fails
        analysis = {
            "gaps": [],
            "inconsistencies": [],
            "prosecution_events": [],
            "defence_events": [],
            "contested_facts": [],
            "ground_connections": [],
            "key_observations": [response[:2000]],
            "recommended_actions": []
        }
    
    return {
        "analysis": analysis,
        "event_count": len(events),
        "analyzed_at": datetime.now(timezone.utc).isoformat()
    }

@api_router.get("/cases/{case_id}/timeline/export-pdf")
async def export_timeline_pdf(case_id: str, request: Request):
    """Export timeline as a formatted PDF"""
    user = await get_current_user(request)
    
    case = await db.cases.find_one({"case_id": case_id, "user_id": user.user_id})
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
    
    events = await db.timeline_events.find(
        {"case_id": case_id},
        {"_id": 0}
    ).sort("event_date", 1).to_list(500)
    
    # Get linked documents for reference
    documents = await db.documents.find(
        {"case_id": case_id},
        {"_id": 0, "document_id": 1, "filename": 1}
    ).to_list(500)
    doc_map = {d["document_id"]: d["filename"] for d in documents}
    
    # Get grounds for reference
    grounds = await db.grounds_of_merit.find(
        {"case_id": case_id},
        {"_id": 0, "ground_id": 1, "title": 1}
    ).to_list(100)
    ground_map = {g["ground_id"]: g["title"] for g in grounds}
    
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import mm
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
    from io import BytesIO
    
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, topMargin=20*mm, bottomMargin=20*mm, leftMargin=15*mm, rightMargin=15*mm)
    
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle('CustomTitle', parent=styles['Heading1'], fontSize=18, spaceAfter=12, textColor=colors.HexColor('#0f172a'))
    subtitle_style = ParagraphStyle('Subtitle', parent=styles['Normal'], fontSize=10, textColor=colors.HexColor('#64748b'), spaceAfter=20)
    event_title_style = ParagraphStyle('EventTitle', parent=styles['Heading3'], fontSize=12, textColor=colors.HexColor('#1e293b'), spaceBefore=8, spaceAfter=4)
    event_body_style = ParagraphStyle('EventBody', parent=styles['Normal'], fontSize=10, textColor=colors.HexColor('#475569'), spaceAfter=4)
    meta_style = ParagraphStyle('Meta', parent=styles['Normal'], fontSize=9, textColor=colors.HexColor('#94a3b8'))
    section_style = ParagraphStyle('Section', parent=styles['Heading2'], fontSize=14, textColor=colors.HexColor('#334155'), spaceBefore=16, spaceAfter=8)
    
    story = []
    
    # Header
    story.append(Paragraph(f"Case Timeline: {case.get('title', 'Untitled Case')}", title_style))
    story.append(Paragraph(f"Generated for {user.name} on {datetime.now().strftime('%d %B %Y')}", subtitle_style))
    story.append(Paragraph("Criminal Law Appeal Case Management by Deb King GLENMORE PARK NSW", meta_style))
    story.append(Spacer(1, 10*mm))
    
    # Summary stats
    critical_count = len([e for e in events if e.get('significance') == 'critical'])
    contested_count = len([e for e in events if e.get('is_contested')])
    story.append(Paragraph("Timeline Summary", section_style))
    summary_data = [
        ["Total Events", str(len(events))],
        ["Critical Events", str(critical_count)],
        ["Contested Facts", str(contested_count)],
        ["Date Range", f"{events[0].get('event_date', 'N/A')[:10] if events else 'N/A'} to {events[-1].get('event_date', 'N/A')[:10] if events else 'N/A'}"]
    ]
    summary_table = Table(summary_data, colWidths=[80*mm, 80*mm])
    summary_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#f1f5f9')),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.HexColor('#334155')),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('PADDING', (0, 0), (-1, -1), 6),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#e2e8f0')),
    ]))
    story.append(summary_table)
    story.append(Spacer(1, 8*mm))
    
    # Events
    story.append(Paragraph("Chronological Events", section_style))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#e2e8f0')))
    
    significance_colors = {
        'critical': '#dc2626',
        'important': '#ea580c', 
        'normal': '#3b82f6',
        'minor': '#9ca3af'
    }
    
    for i, event in enumerate(events):
        date_str = event.get('event_date', '')[:10] if event.get('event_date') else 'Unknown'
        sig = event.get('significance', 'normal')
        sig_color = significance_colors.get(sig, '#3b82f6')
        
        contested_marker = " [CONTESTED]" if event.get('is_contested') else ""
        perspective = f" ({event.get('perspective', 'neutral').upper()})" if event.get('perspective') != 'neutral' else ""
        
        story.append(Paragraph(f"<font color='{sig_color}'>●</font> {date_str} — {event.get('title', 'Untitled')}{contested_marker}{perspective}", event_title_style))
        story.append(Paragraph(event.get('description', 'No description'), event_body_style))
        
        # Metadata
        meta_parts = []
        if event.get('event_type'):
            meta_parts.append(f"Type: {event['event_type'].replace('_', ' ').title()}")
        if event.get('source_citation'):
            meta_parts.append(f"Source: {event['source_citation'][:50]}")
        if event.get('linked_documents'):
            linked_names = [doc_map.get(d, d) for d in event['linked_documents'][:3]]
            meta_parts.append(f"Docs: {', '.join(linked_names)}")
        if event.get('related_grounds'):
            linked_grounds = [ground_map.get(g, g) for g in event['related_grounds'][:2]]
            meta_parts.append(f"Grounds: {', '.join(linked_grounds)}")
        if event.get('participants'):
            participants = [f"{p.get('name', 'Unknown')} ({p.get('role', 'Unknown')})" for p in event['participants'][:3]]
            meta_parts.append(f"Participants: {', '.join(participants)}")
        
        if meta_parts:
            story.append(Paragraph(" | ".join(meta_parts), meta_style))
        
        if event.get('contested_details'):
            story.append(Paragraph(f"<i>Contested: {event['contested_details']}</i>", meta_style))
        
        story.append(Spacer(1, 4*mm))
    
    # Footer
    story.append(Spacer(1, 10*mm))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#e2e8f0')))
    story.append(Paragraph("One woman's fight for justice — seeking truth for Joshua Homann, failed by the system", meta_style))
    
    doc.build(story)
    buffer.seek(0)
    
    filename = f"timeline_{case.get('title', 'case')[:30].replace(' ', '_')}_{datetime.now().strftime('%Y%m%d')}.pdf"
    
    return Response(
        content=buffer.getvalue(),
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )

# ============ DEADLINE ENDPOINTS ============

@api_router.get("/cases/{case_id}/deadlines", response_model=List[dict])
async def get_deadlines(case_id: str, request: Request):
    """Get all deadlines for a case"""
    user = await get_current_user(request)
    
    case = await db.cases.find_one({"case_id": case_id, "user_id": user.user_id})
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
    
    deadlines = await db.deadlines.find(
        {"case_id": case_id},
        {"_id": 0}
    ).sort("due_date", 1).to_list(100)
    
    return deadlines

@api_router.post("/cases/{case_id}/deadlines", response_model=dict)
async def create_deadline(case_id: str, deadline_data: DeadlineCreate, request: Request):
    """Create a new deadline"""
    user = await get_current_user(request)
    
    case = await db.cases.find_one({"case_id": case_id, "user_id": user.user_id})
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
    
    deadline = Deadline(
        case_id=case_id,
        user_id=user.user_id,
        **deadline_data.model_dump()
    )
    
    deadline_dict = deadline.model_dump()
    deadline_dict["due_date"] = deadline_dict["due_date"].isoformat()
    deadline_dict["created_at"] = deadline_dict["created_at"].isoformat()
    
    await db.deadlines.insert_one(deadline_dict)
    
    return await db.deadlines.find_one({"deadline_id": deadline.deadline_id}, {"_id": 0})

@api_router.patch("/cases/{case_id}/deadlines/{deadline_id}", response_model=dict)
async def update_deadline(case_id: str, deadline_id: str, request: Request):
    """Update a deadline (mark complete, etc.)"""
    await get_current_user(request)  # Verify authentication
    body = await request.json()
    
    deadline = await db.deadlines.find_one({
        "deadline_id": deadline_id,
        "case_id": case_id
    })
    if not deadline:
        raise HTTPException(status_code=404, detail="Deadline not found")
    
    update_data = {}
    if "is_completed" in body:
        update_data["is_completed"] = body["is_completed"]
        if body["is_completed"]:
            update_data["completed_at"] = datetime.now(timezone.utc).isoformat()
    if "title" in body:
        update_data["title"] = body["title"]
    if "due_date" in body:
        update_data["due_date"] = body["due_date"]
    if "priority" in body:
        update_data["priority"] = body["priority"]
    
    if update_data:
        await db.deadlines.update_one(
            {"deadline_id": deadline_id},
            {"$set": update_data}
        )
    
    return await db.deadlines.find_one({"deadline_id": deadline_id}, {"_id": 0})

@api_router.delete("/cases/{case_id}/deadlines/{deadline_id}")
async def delete_deadline(case_id: str, deadline_id: str, request: Request):
    """Delete a deadline"""
    await get_current_user(request)  # Verify authentication
    
    result = await db.deadlines.delete_one({
        "deadline_id": deadline_id,
        "case_id": case_id
    })
    
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Deadline not found")
    
    return {"message": "Deadline deleted"}

# ============ CHECKLIST ENDPOINTS ============

@api_router.get("/cases/{case_id}/checklist", response_model=List[dict])
async def get_checklist(case_id: str, request: Request):
    """Get checklist for a case, creating default items if none exist"""
    user = await get_current_user(request)
    
    case = await db.cases.find_one({"case_id": case_id, "user_id": user.user_id})
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
    
    items = await db.checklist_items.find(
        {"case_id": case_id},
        {"_id": 0}
    ).sort("order", 1).to_list(100)
    
    if not items:
        for item_data in DEFAULT_CHECKLIST:
            item = ChecklistItem(
                case_id=case_id,
                user_id=user.user_id,
                **item_data
            )
            item_dict = item.model_dump()
            item_dict["created_at"] = item_dict["created_at"].isoformat()
            await db.checklist_items.insert_one(item_dict)
        
        items = await db.checklist_items.find(
            {"case_id": case_id},
            {"_id": 0}
        ).sort("order", 1).to_list(100)
    
    return items

@api_router.patch("/cases/{case_id}/checklist/{item_id}", response_model=dict)
async def update_checklist_item(case_id: str, item_id: str, request: Request):
    """Update a checklist item"""
    await get_current_user(request)  # Verify authentication
    body = await request.json()
    
    item = await db.checklist_items.find_one({
        "item_id": item_id,
        "case_id": case_id
    })
    if not item:
        raise HTTPException(status_code=404, detail="Checklist item not found")
    
    update_data = {}
    if "is_completed" in body:
        update_data["is_completed"] = body["is_completed"]
        if body["is_completed"]:
            update_data["completed_at"] = datetime.now(timezone.utc).isoformat()
        else:
            update_data["completed_at"] = None
    
    if update_data:
        await db.checklist_items.update_one(
            {"item_id": item_id},
            {"$set": update_data}
        )
    
    return await db.checklist_items.find_one({"item_id": item_id}, {"_id": 0})

# ============ CASE STRENGTH ENDPOINT ============

@api_router.get("/cases/{case_id}/strength", response_model=dict)
async def get_case_strength(case_id: str, request: Request):
    """Calculate overall case strength"""
    user = await get_current_user(request)
    
    case = await db.cases.find_one({"case_id": case_id, "user_id": user.user_id})
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
    
    grounds = await db.grounds_of_merit.find({"case_id": case_id}, {"_id": 0}).to_list(100)
    documents = await db.documents.find({"case_id": case_id}, {"_id": 0}).to_list(500)
    timeline = await db.timeline_events.find({"case_id": case_id}, {"_id": 0}).to_list(500)
    checklist = await db.checklist_items.find({"case_id": case_id}, {"_id": 0}).to_list(100)
    
    strength_scores = {"strong": 3, "moderate": 2, "weak": 1}
    
    grounds_score = 0
    ground_breakdown = {"strong": 0, "moderate": 0, "weak": 0}
    if grounds:
        for g in grounds:
            strength = g.get("strength", "moderate")
            ground_breakdown[strength] = ground_breakdown.get(strength, 0) + 1
            grounds_score += strength_scores.get(strength, 1)
        max_possible = len(grounds) * 3
        grounds_score = min(100, int((grounds_score / max_possible) * 100) + (len(grounds) * 5))
    
    doc_score = 0
    docs_with_text = len([d for d in documents if d.get("content_text")])
    if documents:
        doc_score = min(100, int((docs_with_text / len(documents)) * 50) + (len(documents) * 5))
    
    timeline_score = 0
    if timeline:
        timeline_score = min(100, len(timeline) * 5)
        critical_events = len([t for t in timeline if t.get("significance") == "critical"])
        timeline_score = min(100, timeline_score + (critical_events * 10))
    
    prep_score = 0
    if checklist:
        completed = len([c for c in checklist if c.get("is_completed")])
        prep_score = int((completed / len(checklist)) * 100)
    
    overall_score = int(
        (grounds_score * 0.40) +
        (doc_score * 0.25) +
        (timeline_score * 0.15) +
        (prep_score * 0.20)
    )
    
    if overall_score >= 75:
        rating, rating_color = "Strong", "green"
    elif overall_score >= 50:
        rating, rating_color = "Moderate", "amber"
    elif overall_score >= 25:
        rating, rating_color = "Developing", "orange"
    else:
        rating, rating_color = "Early Stage", "red"
    
    recommendations = []
    if not grounds:
        recommendations.append("Run AI Grounds Identification to find potential appeal grounds")
    if len(documents) < 3:
        recommendations.append("Upload more case documents for better analysis")
    if len(timeline) < 5:
        recommendations.append("Build out your timeline with key case events")
    if prep_score < 50:
        recommendations.append("Work through the appeal checklist")
    
    return {
        "overall_score": overall_score,
        "rating": rating,
        "rating_color": rating_color,
        "breakdown": {
            "grounds": {"score": grounds_score, "count": len(grounds), **ground_breakdown},
            "documentation": {"score": doc_score, "total_docs": len(documents), "with_text": docs_with_text},
            "timeline": {"score": timeline_score, "event_count": len(timeline)},
            "preparation": {"score": prep_score, "completed": len([c for c in checklist if c.get("is_completed")]), "total": len(checklist)}
        },
        "recommendations": recommendations
    }

# ============ CONTRADICTION FINDER ============

@api_router.post("/cases/{case_id}/analyze-contradictions", response_model=dict)
async def analyze_witness_contradictions(case_id: str, request: Request):
    """AI analysis to find contradictions in documents"""
    user = await get_current_user(request)
    
    case = await db.cases.find_one({"case_id": case_id, "user_id": user.user_id})
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
    
    documents = await db.documents.find(
        {"case_id": case_id, "content_text": {"$exists": True, "$ne": ""}},
        {"_id": 0, "file_data": 0}
    ).to_list(100)
    
    if len(documents) < 2:
        raise HTTPException(status_code=400, detail="Need at least 2 documents with text to compare")
    
    doc_context = ""
    for i, doc in enumerate(documents):
        doc_context += f"\n=== DOCUMENT {i+1}: {doc.get('filename', 'Unknown')} ===\n"
        content = doc.get('content_text', '')[:4000]
        doc_context += f"Content:\n{content}\n"
    
    from emergentintegrations.llm.chat import LlmChat, UserMessage
    
    system_prompt = """You are a legal analyst finding contradictions in witness statements. Use Australian English spelling throughout. Find:
1. DIRECT CONTRADICTIONS - witnesses contradict each other
2. INTERNAL INCONSISTENCIES - witness contradicts themselves
3. TIMELINE CONFLICTS - times/dates don't align
4. FACTUAL DISCREPANCIES - differences in descriptions
5. OMISSIONS - facts missing from one account

Return JSON:
{
    "contradictions": [{"type": "...", "severity": "critical|significant|minor", "documents_involved": [], "description": "...", "appeal_relevance": "..."}],
    "summary": "...",
    "total_critical": 0, "total_significant": 0, "total_minor": 0
}"""

    try:
        response = await call_llm_with_fallback(system_prompt, f"Find contradictions in these documents:\n{doc_context}", f"contradiction_{case_id}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI analysis failed: {str(e)}")
    
    try:
        json_match = response
        if "```json" in response:
            json_match = response.split("```json")[1].split("```")[0]
        analysis = json.loads(json_match.strip())
    except (json.JSONDecodeError, IndexError, ValueError):
        analysis = {"contradictions": [], "summary": response[:2000], "total_critical": 0, "total_significant": 0, "total_minor": 0}
    
    return {"analysis": analysis, "documents_analyzed": len(documents), "analyzed_at": datetime.now(timezone.utc).isoformat()}

# ============ AI PROGRESS ANALYSIS ============
# DO NOT UNDO — AI Progress Analysis endpoint

@api_router.post("/cases/{case_id}/progress-analysis", response_model=dict)
async def generate_progress_analysis(case_id: str, request: Request):
    """AI-powered case progress analysis with recommendations"""
    from emergentintegrations.llm.chat import LlmChat, UserMessage
    
    user = await get_current_user(request)
    case = await db.cases.find_one({"case_id": case_id, "user_id": user.user_id}, {"_id": 0})
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
    
    documents = await db.documents.find({"case_id": case_id}, {"_id": 0, "file_data": 0}).to_list(100)
    timeline = await db.timeline_events.find({"case_id": case_id}, {"_id": 0}).to_list(100)
    grounds = await db.grounds_of_merit.find({"case_id": case_id}, {"_id": 0}).to_list(50)
    deadlines = await db.deadlines.find({"case_id": case_id}, {"_id": 0}).to_list(50)
    checklist = await db.checklist_items.find({"case_id": case_id}, {"_id": 0}).to_list(50)
    reports = await db.reports.find({"case_id": case_id, "status": "completed"}, {"_id": 0, "content": 0}).to_list(20)
    
    completed_report_types = sorted({report.get("report_type") for report in reports if report.get("report_type") in {"quick_summary", "full_detailed", "extensive_log", "barrister_view"}})

    context = f"""CASE: {case.get('title', 'Unknown')}
DEFENDANT: {case.get('defendant_name', 'Unknown')}
STATE: {case.get('state', 'Unknown').upper()}
COURT: {case.get('court', 'Unknown')}
OFFENCE: {case.get('offence_type', 'Unknown')} ({case.get('offence_category', 'Unknown')})

DOCUMENTS UPLOADED: {len(documents)}
TIMELINE EVENTS: {len(timeline)}
GROUNDS IDENTIFIED: {len(grounds)}
REPORTS GENERATED: {len(completed_report_types)}
COMPLETED REPORT TYPES: {', '.join(completed_report_types) if completed_report_types else 'None'}
DEADLINES SET: {len(deadlines)}
CHECKLIST ITEMS: {len(checklist)} (Completed: {sum(1 for c in checklist if c.get('completed'))})
"""
    
    if grounds:
        context += "\nIDENTIFIED GROUNDS:\n"
        for g in grounds:
            context += f"- {g.get('title', 'Unknown')} (Type: {g.get('ground_type', 'Unknown')}, Strength: {g.get('strength', 'Unknown')})\n"
    
    if deadlines:
        context += "\nDEADLINES:\n"
        for d in deadlines:
            context += f"- {d.get('title', 'Unknown')}: {d.get('due_date', 'Unknown')} (Status: {d.get('status', 'pending')})\n"
    
    system_prompt = """You are an expert Australian criminal appeal legal analyst. 
Analyse the case progress and provide a comprehensive progress report using Australian English spelling.

Structure your analysis with these sections:

## APPEAL PROGRESS SUMMARY
Brief overview of where this case stands in the appeal process.

## COMPLETED STEPS
What has been done so far based on the data provided.

## CRITICAL NEXT STEPS
The most urgent actions needed to advance this appeal, in priority order.

## CASE STRENGTH ASSESSMENT
Based on the grounds identified and documents available, assess the overall case strength.

## TIMELINE RECOMMENDATIONS
Recommended deadlines and milestones for the appeal process in this jurisdiction.

## STRATEGIC RECOMMENDATIONS
Specific tactical advice for strengthening this appeal.

## RISK FACTORS
Potential issues or weaknesses that need to be addressed.

Be specific to the jurisdiction and offence type. Use Australian legal terminology and reference relevant courts and processes."""

    try:
        response = await call_llm_with_fallback(system_prompt, f"Analyse the progress of this criminal appeal case:\n\n{context}", f"progress_{case_id}")
        return {"analysis": response, "generated_at": datetime.now(timezone.utc).isoformat()}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI analysis failed: {str(e)}")

# ============ PAYMENT ENDPOINTS ============

@api_router.get("/payments/prices")
async def get_feature_prices():
    """Get pricing for premium features"""
    return {
        "prices": FEATURE_PRICES,
        "currency": "AUD",
        "payment_method": "payid"
    }

@api_router.get("/cases/{case_id}/payments")
async def get_case_payments(case_id: str, request: Request):
    """Get all payments for a case"""
    user = await get_current_user(request)
    
    # Admin users get everything unlocked
    if is_admin_user(user.email):
        return {
            "payments": [],
            "unlocked_features": {
                "grounds_of_merit": True,
                "full_report": True,
                "extensive_report": True
            },
            "latest_status_by_feature": {}
        }
    
    payments = await db.payments.find(
        {"case_id": case_id, "user_id": user.user_id},
        {"_id": 0}
    ).sort("created_at", -1).to_list(100)
    
    # Return which features are unlocked
    unlocked = {
        "grounds_of_merit": False,
        "full_report": False,
        "extensive_report": False
    }
    case = await db.cases.find_one({"case_id": case_id, "user_id": user.user_id}, {"_id": 0, "unlocked_features": 1})
    for feature in case.get("unlocked_features", []) if case else []:
        canonical = canonical_feature_type(feature)
        if canonical in unlocked:
            unlocked[canonical] = True
    
    for payment in payments:
        canonical = canonical_feature_type(payment.get("feature_type"))
        if canonical in unlocked:
            if payment.get("status") == "completed":
                unlocked[canonical] = True

    latest_status_by_feature = {}
    for payment in payments:
        canonical = canonical_feature_type(payment.get("feature_type"))
        if canonical and canonical not in latest_status_by_feature:
            latest_status_by_feature[canonical] = {
                "status": payment.get("status"),
                "reference": payment.get("reference"),
                "amount": payment.get("amount"),
                "created_at": payment.get("created_at"),
            }
    
    return {
        "payments": payments,
        "unlocked_features": unlocked,
        "latest_status_by_feature": latest_status_by_feature
    }

# ============ PAYID PAYMENT ENDPOINTS ============
# DO NOT UNDO — PayID payment endpoints for Australian bank transfers

@api_router.post("/payments/payid/create-reference")
async def create_payid_reference(request: Request):
    """Generate a unique payment reference for PayID bank transfer"""
    user = await get_current_user(request)
    body = await request.json()
    feature_type = body.get("feature_type")
    case_id = body.get("case_id")
    canonical_type = canonical_feature_type(feature_type)
    
    if not feature_type or not case_id:
        raise HTTPException(status_code=400, detail="Missing feature_type or case_id")
    
    price = FEATURE_PRICES.get(canonical_type, {}).get("price", 0)
    reference = f"ACM-{uuid.uuid4().hex[:8].upper()}"
    
    payment_record = {
        "payment_id": f"pay_{uuid.uuid4().hex[:12]}",
        "user_id": user.user_id,
        "case_id": case_id,
        "feature_type": canonical_type,
        "amount": price,
        "method": "payid",
        "reference": reference,
        "status": "pending",
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    await db.payments.insert_one(payment_record)
    payment_record.pop("_id", None)
    
    return {
        "reference": reference,
        "amount": price,
        "payid": "djkingy79@gmail.com",
        "payid_name": "Appeal Case Manager",
        "instructions": f"Transfer ${price:.2f} AUD to the PayID above. Use reference: {reference}"
    }

@api_router.post("/payments/payid/verify")
async def verify_payid_payment(request: Request):
    """Mark a PayID payment as submitted and let users refresh until admin confirmation completes unlock."""
    user = await get_current_user(request)
    body = await request.json()
    reference = body.get("reference")
    case_id = body.get("case_id")
    feature_type = body.get("feature_type")
    canonical_type = canonical_feature_type(feature_type)
    
    if not reference:
        raise HTTPException(status_code=400, detail="Missing reference")
    
    payment = await db.payments.find_one(
        {"reference": reference, "user_id": user.user_id},
        {"_id": 0}
    )
    
    if not payment:
        raise HTTPException(status_code=404, detail="Payment reference not found")

    if payment.get("status") == "completed":
        if case_id and feature_type:
            await db.cases.update_one(
                {"case_id": case_id, "user_id": user.user_id},
                {"$addToSet": {"unlocked_features": canonical_type}}
            )
        await send_payid_status_email(
            user.email,
            user.name,
            FEATURE_PRICES.get(canonical_type, {}).get("name", canonical_type or "Feature"),
            payment.get("amount") or FEATURE_PRICES.get(canonical_type, {}).get("price", 0),
            reference,
            "✓ Payment Confirmed - Feature Unlocked",
            "Payment Confirmed",
            "<p style=\"margin:0 0 14px;line-height:1.7;\">A payment refresh confirmed that this feature has been paid and unlocked successfully.</p>",
        )
        return {"status": "already_verified", "message": "Payment confirmed. Feature unlocked."}
    
    await db.payments.update_one(
        {"reference": reference},
        {"$set": {"status": "submitted", "submitted_at": datetime.now(timezone.utc).isoformat()}}
    )

    await send_payid_status_email(
        user.email,
        user.name,
        FEATURE_PRICES.get(canonical_type, {}).get("name", canonical_type or "Feature"),
        payment.get("amount") or FEATURE_PRICES.get(canonical_type, {}).get("price", 0),
        reference,
        "Payment Notice Received - Awaiting Confirmation",
        "Payment Notice Received",
        "<p style=\"margin:0 0 14px;line-height:1.7;\">This email confirms that the PayID payment notice was received and marked for review. Once the payment is received and confirmed, the feature will unlock automatically.</p>",
    )
    
    return {
        "status": "submitted_for_review",
        "message": "Payment marked as sent. Use refresh after payment is received and confirmed."
    }


@api_router.get("/payments/payid/pending")
async def get_pending_payid_payments(request: Request):
    """Get all pending PayID payments (admin only)"""
    user = await get_current_user(request)
    if not is_admin_user(user.email):
        raise HTTPException(status_code=403, detail="Admin access required")
    
    pending = await db.payments.find(
        {"method": "payid", "status": {"$in": ["pending", "submitted", "pending_verification"]}},
        {"_id": 0}
    ).sort("created_at", -1).to_list(100)
    
    return {"pending_payments": pending}


@api_router.post("/payments/payid/admin-confirm/{reference}")
async def admin_confirm_payid_payment(reference: str, request: Request):
    """Admin confirms a PayID payment has been received"""
    user = await get_current_user(request)
    if not is_admin_user(user.email):
        raise HTTPException(status_code=403, detail="Admin access required")
    
    payment = await db.payments.find_one({"reference": reference}, {"_id": 0})
    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found")
    
    await db.payments.update_one(
        {"reference": reference},
        {"$set": {"status": "completed", "completed_at": datetime.now(timezone.utc).isoformat(), "confirmed_by": user.email}}
    )
    
    # Unlock the feature for the user
    if payment.get("case_id") and payment.get("feature_type"):
        await db.cases.update_one(
            {"case_id": payment["case_id"], "user_id": payment["user_id"]},
            {"$addToSet": {"unlocked_features": canonical_feature_type(payment["feature_type"])}},
        )

    payment_user = await db.users.find_one({"user_id": payment.get("user_id")}, {"_id": 0, "email": 1, "name": 1})
    await send_payid_status_email(
        (payment_user or {}).get("email"),
        (payment_user or {}).get("name", ""),
        FEATURE_PRICES.get(canonical_feature_type(payment.get("feature_type")), {}).get("name", canonical_feature_type(payment.get("feature_type")) or "Feature"),
        payment.get("amount") or FEATURE_PRICES.get(canonical_feature_type(payment.get("feature_type")), {}).get("price", 0),
        reference,
        "✓ Payment Confirmed - Feature Unlocked",
        "Payment Confirmed",
        "<p style=\"margin:0 0 14px;line-height:1.7;\">The PayID transfer has been confirmed and the premium feature is now unlocked on the case.</p>",
    )
    
    return {"status": "confirmed", "reference": reference}


# ============ RESOURCE DIRECTORY ============

@api_router.get("/resources/directory", response_model=dict)
async def get_resource_directory():
    """Get directory of support resources"""
    return {
        "support_services": [
            {"name": "Community Legal Centres NSW", "website": "https://www.clcnsw.org.au", "services": ["Legal advice", "Referrals"], "region": "NSW"},
            {"name": "Aboriginal Legal Service (NSW/ACT)", "phone": "1800 765 767", "website": "https://www.alsnswact.org.au", "services": ["Criminal law", "Family law"], "region": "NSW/ACT"},
            {"name": "LawAccess NSW", "phone": "1300 888 529", "website": "https://www.lawaccess.nsw.gov.au", "services": ["Legal information", "Referrals"], "region": "NSW"}
        ],
        "advocacy_groups": [
            {"name": "Innocence Project (Australia)", "website": "https://www.innocenceproject.org.au", "focus": "Wrongful convictions"},
            {"name": "Justice Action", "phone": "(02) 9283 0123", "website": "https://www.justiceaction.org.au", "focus": "Prisoner rights"},
            {"name": "Prisoners Aid Association NSW", "phone": "(02) 9288 8700", "website": "https://www.prisonersaid.org.au", "focus": "Family support"}
        ],
        "courts": [
            {"name": "NSW Court of Criminal Appeal", "website": "https://www.supremecourt.justice.nsw.gov.au"},
            {"name": "High Court of Australia", "website": "https://www.hcourt.gov.au", "note": "Special leave required"}
        ],
        "appeal_deadlines": {"notice_of_appeal": "28 days from conviction/sentence", "leave_to_appeal": "28 days", "extension": "Can apply if missed - must show good reason"}
    }

# ============ DOCUMENT TEMPLATES ============

@api_router.get("/templates", response_model=List[dict])
async def get_document_templates():
    """Get available document templates"""
    return [
        {"template_id": "notice_of_appeal", "title": "Notice of Appeal", "description": "Form to lodge an appeal", "category": "lodgement"},
        {"template_id": "leave_to_appeal", "title": "Application for Leave to Appeal", "description": "Application for permission to appeal sentence", "category": "lodgement"},
        {"template_id": "affidavit_fresh_evidence", "title": "Affidavit - Fresh Evidence", "description": "Sworn statement for new evidence", "category": "evidence"},
        {"template_id": "extension_of_time", "title": "Extension of Time Application", "description": "Apply to file after deadline", "category": "lodgement"},
        {"template_id": "outline_of_submissions", "title": "Written Submissions", "description": "Legal arguments for hearing", "category": "hearing"}
    ]

@api_router.post("/templates/{template_id}/generate", response_model=dict)
async def generate_document_from_template(template_id: str, request: Request):
    """Generate a document from template"""
    await get_current_user(request)  # Verify authentication
    body = await request.json()
    
    if template_id == "notice_of_appeal":
        content = f"""COURT OF CRIMINAL APPEAL - SUPREME COURT OF NSW
NOTICE OF APPEAL

Appellant: {body.get('appellant_name', '[NAME]')}
Case Number: {body.get('case_number', '[NUMBER]')}

TAKE NOTICE that the above-named appeals against: {body.get('appeal_type', '[CONVICTION/SENTENCE]')}

Court of Trial: {body.get('court_of_trial', '[COURT]')}
Date of Conviction: {body.get('date_of_conviction', '[DATE]')}
Date of Sentence: {body.get('date_of_sentence', '[DATE]')}
Offence: {body.get('offence', '[OFFENCE]')}
Sentence: {body.get('sentence', '[SENTENCE]')}

GROUNDS OF APPEAL:
{body.get('grounds', '[GROUNDS]')}

DATED: {datetime.now().strftime('%d %B %Y')}

---
Criminal Law Appeal Case Management by Deb King GLENMORE PARK NSW"""
    elif template_id == "leave_to_appeal":
        content = f"""APPLICATION FOR LEAVE TO APPEAL AGAINST SENTENCE

Appellant: {body.get('appellant_name', '[NAME]')}
Case: {body.get('case_number', '[NUMBER]')}
Sentence Date: {body.get('date_of_sentence', '[DATE]')}
Sentence: {body.get('sentence', '[SENTENCE]')}

GROUNDS: {body.get('grounds', '[GROUNDS]')}
WHY LEAVE SHOULD BE GRANTED: {body.get('why_leave_granted', '[REASONS]')}

DATED: {datetime.now().strftime('%d %B %Y')}
---
Criminal Law Appeal Case Management by Deb King GLENMORE PARK NSW"""
    else:
        content = f"Template {template_id} - Please contact support for this template."
    
    return {"template_id": template_id, "content": content, "generated_at": datetime.now(timezone.utc).isoformat()}

# ============ NOTES & COMMENTS ENDPOINTS ============

@api_router.get("/cases/{case_id}/notes", response_model=List[dict])
async def get_notes(case_id: str, request: Request):
    """Get all notes for a case"""
    user = await get_current_user(request)
    
    # Verify case ownership
    case = await db.cases.find_one({"case_id": case_id, "user_id": user.user_id})
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
    
    notes = await db.notes.find(
        {"case_id": case_id},
        {"_id": 0}
    ).sort([("is_pinned", -1), ("created_at", -1)]).to_list(500)

    for note in notes:
        note["pinned"] = note.get("is_pinned", False)
        note["mentions"] = note.get("mentions", [])
        note["comments"] = note.get("comments", [])
    
    return notes

@api_router.post("/cases/{case_id}/notes", response_model=dict)
async def create_note(case_id: str, note_data: NoteCreate, request: Request):
    """Create a new note"""
    user = await get_current_user(request)
    
    # Verify case ownership
    case = await db.cases.find_one({"case_id": case_id, "user_id": user.user_id})
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
    
    merged_mentions = sorted(list(set(note_data.mentions + extract_mentions(note_data.content))))

    note = Note(
        case_id=case_id,
        user_id=user.user_id,
        author_name=user.name,
        author_email=user.email,
        mentions=merged_mentions,
        comments=[],
        **note_data.model_dump(exclude={"mentions"})
    )
    
    note_dict = note.model_dump()
    note_dict["created_at"] = note_dict["created_at"].isoformat()
    note_dict["updated_at"] = note_dict["updated_at"].isoformat()
    
    await db.notes.insert_one(note_dict)
    
    # Update case
    await db.cases.update_one(
        {"case_id": case_id},
        {"$set": {"updated_at": datetime.now(timezone.utc).isoformat()}}
    )
    
    created_note = await db.notes.find_one({"note_id": note.note_id}, {"_id": 0})
    if created_note:
        created_note["pinned"] = created_note.get("is_pinned", False)
        created_note["mentions"] = created_note.get("mentions", [])
        created_note["comments"] = created_note.get("comments", [])

    await broadcast_notes_event(
        case_id,
        "note_created",
        {
            "note": created_note,
            "actor": {"user_id": user.user_id, "name": user.name}
        }
    )
    return created_note

@api_router.get("/cases/{case_id}/notes/{note_id}", response_model=dict)
async def get_note(case_id: str, note_id: str, request: Request):
    """Get a specific note"""
    user = await get_current_user(request)
    
    note = await db.notes.find_one(
        {"note_id": note_id, "case_id": case_id, "user_id": user.user_id},
        {"_id": 0}
    )
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")

    note["pinned"] = note.get("is_pinned", False)
    note["mentions"] = note.get("mentions", [])
    note["comments"] = note.get("comments", [])
    
    return note

@api_router.put("/cases/{case_id}/notes/{note_id}", response_model=dict)
async def update_note(case_id: str, note_id: str, note_data: NoteUpdate, request: Request):
    """Update a note"""
    user = await get_current_user(request)

    existing_note = await db.notes.find_one(
        {"note_id": note_id, "case_id": case_id, "user_id": user.user_id},
        {"_id": 0}
    )
    if not existing_note:
        raise HTTPException(status_code=404, detail="Note not found")
    
    update_fields = {k: v for k, v in note_data.model_dump().items() if v is not None}

    updated_content = update_fields.get("content", existing_note.get("content", ""))
    update_fields["mentions"] = extract_mentions(updated_content)
    update_fields["updated_at"] = datetime.now(timezone.utc).isoformat()
    
    await db.notes.update_one(
        {"note_id": note_id, "case_id": case_id, "user_id": user.user_id},
        {"$set": update_fields}
    )
    
    updated_note = await db.notes.find_one({"note_id": note_id}, {"_id": 0})
    if updated_note:
        updated_note["pinned"] = updated_note.get("is_pinned", False)
        updated_note["mentions"] = updated_note.get("mentions", [])
        updated_note["comments"] = updated_note.get("comments", [])

    await broadcast_notes_event(
        case_id,
        "note_updated",
        {
            "note": updated_note,
            "actor": {"user_id": user.user_id, "name": user.name}
        }
    )

    return updated_note

@api_router.delete("/cases/{case_id}/notes/{note_id}")
async def delete_note(case_id: str, note_id: str, request: Request):
    """Delete a note"""
    user = await get_current_user(request)
    
    result = await db.notes.delete_one({
        "note_id": note_id,
        "case_id": case_id,
        "user_id": user.user_id
    })
    
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Note not found")

    await broadcast_notes_event(
        case_id,
        "note_deleted",
        {
            "note_id": note_id,
            "actor": {"user_id": user.user_id, "name": user.name}
        }
    )
    
    return {"message": "Note deleted"}

@api_router.patch("/cases/{case_id}/notes/{note_id}/pin")
async def toggle_pin_note(case_id: str, note_id: str, request: Request):
    """Toggle pin status of a note"""
    user = await get_current_user(request)
    
    note = await db.notes.find_one(
        {"note_id": note_id, "case_id": case_id, "user_id": user.user_id},
        {"_id": 0}
    )
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")
    
    new_pin_status = not note.get("is_pinned", False)
    
    await db.notes.update_one(
        {"note_id": note_id},
        {"$set": {"is_pinned": new_pin_status, "updated_at": datetime.now(timezone.utc).isoformat()}}
    )

    updated_note = await db.notes.find_one({"note_id": note_id}, {"_id": 0})
    if updated_note:
        updated_note["pinned"] = updated_note.get("is_pinned", False)
        updated_note["mentions"] = updated_note.get("mentions", [])
        updated_note["comments"] = updated_note.get("comments", [])

    await broadcast_notes_event(
        case_id,
        "note_updated",
        {
            "note": updated_note,
            "actor": {"user_id": user.user_id, "name": user.name}
        }
    )
    
    return updated_note


@api_router.post("/cases/{case_id}/notes/{note_id}/comments", response_model=dict)
async def add_note_comment(case_id: str, note_id: str, comment_data: NoteCommentCreate, request: Request):
    """Add a threaded comment to a note."""
    user = await get_current_user(request)

    note = await db.notes.find_one(
        {"note_id": note_id, "case_id": case_id, "user_id": user.user_id},
        {"_id": 0}
    )
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")

    content = comment_data.content.strip()
    if not content:
        raise HTTPException(status_code=400, detail="Comment content is required")

    comment = {
        "comment_id": f"cmt_{uuid.uuid4().hex[:12]}",
        "content": content,
        "mentions": extract_mentions(content),
        "author_name": user.name,
        "author_email": user.email,
        "author_user_id": user.user_id,
        "created_at": datetime.now(timezone.utc).isoformat()
    }

    await db.notes.update_one(
        {"note_id": note_id},
        {
            "$push": {"comments": comment},
            "$set": {"updated_at": datetime.now(timezone.utc).isoformat()}
        }
    )

    updated_note = await db.notes.find_one({"note_id": note_id}, {"_id": 0})
    if updated_note:
        updated_note["pinned"] = updated_note.get("is_pinned", False)
        updated_note["mentions"] = updated_note.get("mentions", [])
        updated_note["comments"] = updated_note.get("comments", [])

    await broadcast_notes_event(
        case_id,
        "note_comment_added",
        {
            "note_id": note_id,
            "comment": comment,
            "note": updated_note,
            "actor": {"user_id": user.user_id, "name": user.name}
        }
    )

    return {"comment": comment, "note": updated_note}


@api_router.delete("/cases/{case_id}/notes/{note_id}/comments/{comment_id}")
async def delete_note_comment(case_id: str, note_id: str, comment_id: str, request: Request):
    """Delete a comment from a note."""
    user = await get_current_user(request)

    note = await db.notes.find_one(
        {"note_id": note_id, "case_id": case_id, "user_id": user.user_id},
        {"_id": 0}
    )
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")

    comments = note.get("comments", [])
    target_comment = next((c for c in comments if c.get("comment_id") == comment_id), None)
    if not target_comment:
        raise HTTPException(status_code=404, detail="Comment not found")

    if target_comment.get("author_user_id") != user.user_id:
        raise HTTPException(status_code=403, detail="Only the comment author can delete this comment")

    await db.notes.update_one(
        {"note_id": note_id},
        {
            "$pull": {"comments": {"comment_id": comment_id}},
            "$set": {"updated_at": datetime.now(timezone.utc).isoformat()}
        }
    )

    await broadcast_notes_event(
        case_id,
        "note_comment_deleted",
        {
            "note_id": note_id,
            "comment_id": comment_id,
            "actor": {"user_id": user.user_id, "name": user.name}
        }
    )

    return {"message": "Comment deleted"}


@api_router.websocket("/cases/{case_id}/notes/ws")
async def notes_collaboration_ws(websocket: WebSocket, case_id: str):
    """Realtime note collaboration channel for a case."""
    session_token = websocket.query_params.get("session_token") or websocket.cookies.get("session_token")

    try:
        user = await get_user_from_session_token(session_token)
        case = await db.cases.find_one({"case_id": case_id, "user_id": user.user_id}, {"_id": 0})
        if not case:
            await websocket.close(code=4404)
            return

        await websocket.accept()

        case_connections = notes_ws_connections.setdefault(case_id, {})
        case_connections[user.user_id] = websocket

        presence = await get_presence_snapshot(case_id)
        await broadcast_notes_event(case_id, "presence_update", {"users": presence})

        while True:
            raw_message = await websocket.receive_text()
            if not raw_message:
                continue

            if raw_message == "ping":
                await websocket.send_json({"type": "pong", "payload": {"timestamp": datetime.now(timezone.utc).isoformat()}})
                continue

            try:
                payload = json.loads(raw_message)
            except json.JSONDecodeError:
                continue

            if payload.get("type") == "typing":
                await broadcast_notes_event(
                    case_id,
                    "typing",
                    {
                        "user_id": user.user_id,
                        "name": user.name,
                        "note_id": payload.get("note_id"),
                        "is_typing": bool(payload.get("is_typing", False))
                    }
                )

    except WebSocketDisconnect:
        pass
    except HTTPException:
        if websocket.client_state.value != 3:
            await websocket.close(code=4401)
    finally:
        case_connections = notes_ws_connections.get(case_id, {})
        stale_user_id = None
        for uid, ws in list(case_connections.items()):
            if ws is websocket:
                stale_user_id = uid
                case_connections.pop(uid, None)
                break

        if stale_user_id and case_connections:
            presence = await get_presence_snapshot(case_id)
            await broadcast_notes_event(case_id, "presence_update", {"users": presence})

        if case_id in notes_ws_connections and not notes_ws_connections.get(case_id):
            notes_ws_connections.pop(case_id, None)

# ============ GROUNDS OF MERIT ENDPOINTS ============

GROUND_TYPES = [
    "procedural_error",
    "fresh_evidence", 
    "miscarriage_of_justice",
    "sentencing_error",
    "judicial_error",
    "ineffective_counsel",
    "prosecution_misconduct",
    "jury_irregularity",
    "constitutional_violation",
    "other"
]

@api_router.get("/cases/{case_id}/grounds", response_model=dict)
async def get_grounds_of_merit(case_id: str, request: Request):
    """Get all grounds of merit for a case - requires payment to see details"""
    user = await get_current_user(request)
    
    # Verify case ownership
    case = await db.cases.find_one({"case_id": case_id, "user_id": user.user_id})
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
    
    grounds = await db.grounds_of_merit.find(
        {"case_id": case_id},
        {"_id": 0}
    ).sort([("strength", 1), ("created_at", -1)]).to_list(100)
    
    # Check if user has paid for grounds access
    payment = await db.payments.find_one({
        "case_id": case_id,
        "user_id": user.user_id,
        "feature_type": {"$in": feature_type_variants("grounds_of_merit")},
        "status": "completed"
    })
    
    is_unlocked = payment is not None or "grounds_of_merit" in (case.get("unlocked_features") or []) or is_admin_user(user.email)
    
    if is_unlocked:
        # Return full grounds data
        return {
            "grounds": grounds,
            "count": len(grounds),
            "is_unlocked": True,
            "unlock_price": FEATURE_PRICES["grounds_of_merit"]["price"]
        }
    else:
        # Return only count and basic info (titles only, no descriptions)
        preview_grounds = []
        for g in grounds:
            preview_grounds.append({
                "ground_id": g.get("ground_id"),
                "title": g.get("title"),
                "ground_type": g.get("ground_type"),
                "strength": g.get("strength"),
                # Hide detailed content
                "description": "*** UNLOCK TO VIEW ***",
                "supporting_evidence": [],
                "analysis": None
            })
        return {
            "grounds": preview_grounds,
            "count": len(grounds),
            "is_unlocked": False,
            "unlock_price": FEATURE_PRICES["grounds_of_merit"]["price"],
            "message": f"Found {len(grounds)} potential grounds of merit. Pay ${FEATURE_PRICES['grounds_of_merit']['price']:.2f} to unlock full details."
        }

@api_router.post("/cases/{case_id}/grounds", response_model=dict)
async def create_ground_of_merit(case_id: str, ground_data: GroundOfMeritCreate, request: Request):
    """Create a new ground of merit"""
    user = await get_current_user(request)
    
    # Verify case ownership
    case = await db.cases.find_one({"case_id": case_id, "user_id": user.user_id})
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
    
    ground = GroundOfMerit(
        case_id=case_id,
        user_id=user.user_id,
        **ground_data.model_dump()
    )
    
    ground_dict = ground.model_dump()
    ground_dict["created_at"] = ground_dict["created_at"].isoformat()
    ground_dict["updated_at"] = ground_dict["updated_at"].isoformat()
    
    await db.grounds_of_merit.insert_one(ground_dict)
    
    # Update case
    await db.cases.update_one(
        {"case_id": case_id},
        {"$set": {"updated_at": datetime.now(timezone.utc).isoformat()}}
    )
    
    created_ground = await db.grounds_of_merit.find_one({"ground_id": ground.ground_id}, {"_id": 0})
    return created_ground

@api_router.get("/cases/{case_id}/grounds/{ground_id}", response_model=dict)
async def get_ground_of_merit(case_id: str, ground_id: str, request: Request):
    """Get a specific ground of merit"""
    user = await get_current_user(request)
    
    ground = await db.grounds_of_merit.find_one(
        {"ground_id": ground_id, "case_id": case_id, "user_id": user.user_id},
        {"_id": 0}
    )
    if not ground:
        raise HTTPException(status_code=404, detail="Ground of merit not found")
    
    return ground

@api_router.put("/cases/{case_id}/grounds/{ground_id}", response_model=dict)
async def update_ground_of_merit(case_id: str, ground_id: str, ground_data: GroundOfMeritUpdate, request: Request):
    """Update a ground of merit"""
    user = await get_current_user(request)
    
    update_fields = {k: v for k, v in ground_data.model_dump().items() if v is not None}
    update_fields["updated_at"] = datetime.now(timezone.utc).isoformat()
    
    result = await db.grounds_of_merit.update_one(
        {"ground_id": ground_id, "case_id": case_id, "user_id": user.user_id},
        {"$set": update_fields}
    )
    
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Ground of merit not found")
    
    return await db.grounds_of_merit.find_one({"ground_id": ground_id}, {"_id": 0})

@api_router.delete("/cases/{case_id}/grounds/{ground_id}")
async def delete_ground_of_merit(case_id: str, ground_id: str, request: Request):
    """Delete a ground of merit"""
    user = await get_current_user(request)
    
    result = await db.grounds_of_merit.delete_one({
        "ground_id": ground_id,
        "case_id": case_id,
        "user_id": user.user_id
    })
    
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Ground of merit not found")
    
    return {"message": "Ground of merit deleted"}

@api_router.post("/cases/{case_id}/grounds/{ground_id}/investigate", response_model=dict)
async def investigate_ground_of_merit(case_id: str, ground_id: str, request: Request):
    """Deep AI investigation of a specific ground of merit"""
    user = await get_current_user(request)
    
    # Get the ground
    ground = await db.grounds_of_merit.find_one(
        {"ground_id": ground_id, "case_id": case_id, "user_id": user.user_id},
        {"_id": 0}
    )
    if not ground:
        raise HTTPException(status_code=404, detail="Ground of merit not found")
    
    # Get case data
    case = await db.cases.find_one({"case_id": case_id}, {"_id": 0})
    
    # Get ALL documents with FULL content for cross-referencing
    documents = await db.documents.find(
        {"case_id": case_id},
        {"_id": 0, "file_data": 0}
    ).to_list(500)
    
    # Get timeline
    timeline = await db.timeline_events.find(
        {"case_id": case_id},
        {"_id": 0}
    ).sort("event_date", 1).to_list(500)
    
    # Get offence-specific context
    offence_category = case.get('offence_category', 'homicide')
    offence_context = get_offence_context(case)
    category_data = OFFENCE_CATEGORIES.get(offence_category, OFFENCE_CATEGORIES.get('homicide'))
    
    # Build comprehensive context with bounded document content for responsiveness
    context = f"""
=== CASE INFORMATION ===
Title: {case.get('title', 'Unknown')}
Defendant: {case.get('defendant_name', 'Unknown')}
Case Number: {case.get('case_number', 'N/A')}
Court: {case.get('court', 'N/A')}

{offence_context}

=== GROUND OF MERIT TO INVESTIGATE ===
Title: {ground.get('title')}
Type: {ground.get('ground_type')}
Description: {ground.get('description')}
Current Strength: {ground.get('strength')}
Supporting Evidence Listed: {', '.join(ground.get('supporting_evidence', []))}

"""

    doc_context = build_document_context(
        documents,
        per_doc_char_limit=1500,
        total_char_budget=12000,
        include_description=False,
        content_heading="CONTENT"
    )
    
    # Include bounded document content
    if documents:
        context += f"=== CASE DOCUMENTS ({doc_context['included_docs']} included / {len(documents)} total) - SEARCH THESE FOR EVIDENCE ===\n"
        context += doc_context["text"] + "\n"
        if doc_context["omitted_docs"] > 0:
            context += f"[Note: {doc_context['omitted_docs']} document(s) omitted from prompt for speed optimisation.]\n"
    
    if timeline:
        timeline_limit = 100
        timeline_slice = timeline[:timeline_limit]
        context += f"\n=== TIMELINE ({len(timeline_slice)} included / {len(timeline)} total events) ===\n"
        for event in timeline_slice:
            context += f"- {event.get('event_date')}: {event.get('title')} - {event.get('description', '')[:180]}\n"
        if len(timeline) > timeline_limit:
            context += f"[... {len(timeline) - timeline_limit} additional timeline events omitted for speed ...]\n"

    # Use offence-specific system prompt
    system_prompt = get_offence_system_prompt(offence_category)
    system_prompt += """

IMPORTANT: You must search through the provided document content and cite specific evidence.
Quote directly from documents to support your analysis."""

    # Build dynamic law section examples based on offence type
    law_examples = []
    for act_name, sections in category_data.get('nsw_legislation', {}).items():
        for section in sections[:3]:
            law_examples.append(f"   - {section.get('section')} {act_name} - {section.get('title')}")
    law_examples.append("   - s.6 Criminal Appeal Act 1912 (NSW) - Grounds for appeal")
    law_examples_str = "\n".join(law_examples)

    user_prompt = f"""Conduct a THOROUGH investigation of this ground of merit.

{context}

REQUIRED ANALYSIS (search the documents above for evidence):

1. VIABILITY ASSESSMENT
   - Rate: Strong/Moderate/Weak with detailed justification
   - Quote specific evidence FROM THE DOCUMENTS above

2. DOCUMENT EVIDENCE
   - For EACH document, explain what it contains relevant to this ground
   - Quote specific passages that support or undermine this ground

3. RELEVANT LAW SECTIONS (be specific to this {category_data.get('name', 'criminal')} case)
{law_examples_str}
   - Other relevant sections with explanations

4. SIMILAR CASES
   - Name 2-3 Australian cases with citations relevant to {category_data.get('name', 'this type of')} appeals
   - Explain relevance to this ground

5. EVIDENCE GAPS
   - What additional evidence would strengthen this ground?

6. STRATEGIC RECOMMENDATION
   - How to present this ground to the court"""

    try:
        response = await call_llm_with_fallback(system_prompt, user_prompt, f"ground_{ground_id}_{uuid.uuid4().hex[:8]}")
    except Exception as e:
        logger.error(f"Ground investigation LLM failed: {e}")
        raise HTTPException(status_code=500, detail=f"AI analysis failed after retries: {str(e)}")
    
    # Parse response to extract structured data
    law_sections = []
    similar_cases = []
    
    # Extract law sections
    import re
    section_patterns = re.findall(r'[sS]\.?\s*(\d+[A-Za-z]?)\s+([A-Za-z\s]+(?:Act|Code))\s*(?:\d{4})?', response)
    for section_num, act_name in section_patterns[:10]:
        law_sections.append({
            "section": section_num,
            "act": act_name.strip(),
            "jurisdiction": "NSW" if "NSW" in act_name or "1900" in response else "Federal"
        })
    
    # Extract case citations
    case_patterns = re.findall(r'([A-Z][a-z]+(?:\s+v\s+)[A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)', response)
    for case_name in list(set(case_patterns))[:5]:
        similar_cases.append({
            "case_name": case_name,
            "year": "",
            "citation": ""
        })
    
    # Update the ground with investigation results
    deep_analysis = {
        "full_analysis": response,
        "investigated_at": datetime.now(timezone.utc).isoformat(),
        "law_sections_identified": len(law_sections),
        "similar_cases_found": len(similar_cases),
        "documents_analyzed": len(documents)
    }
    
    await db.grounds_of_merit.update_one(
        {"ground_id": ground_id},
        {"$set": {
            "status": "investigated",
            "analysis": response[:2000] + "..." if len(response) > 2000 else response,
            "deep_analysis": deep_analysis,
            "law_sections": law_sections if law_sections else ground.get("law_sections", []),
            "similar_cases": similar_cases if similar_cases else ground.get("similar_cases", []),
            "updated_at": datetime.now(timezone.utc).isoformat()
        }}
    )
    
    return await db.grounds_of_merit.find_one({"ground_id": ground_id}, {"_id": 0})

@api_router.post("/cases/{case_id}/grounds/auto-identify", response_model=dict)
async def auto_identify_grounds(case_id: str, request: Request):
    """AI automatically identifies potential grounds of merit from case materials - prevents duplicates"""
    user = await get_current_user(request)
    
    # Verify case ownership
    case = await db.cases.find_one({"case_id": case_id, "user_id": user.user_id}, {"_id": 0})
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
    
    # Get existing grounds to avoid duplicates
    existing_grounds = await db.grounds_of_merit.find(
        {"case_id": case_id},
        {"_id": 0}
    ).to_list(100)
    
    # Get all case materials - include content_text for analysis
    documents = await db.documents.find(
        {"case_id": case_id},
        {"_id": 0, "file_data": 0}
    ).to_list(500)
    
    timeline = await db.timeline_events.find(
        {"case_id": case_id},
        {"_id": 0}
    ).sort("event_date", 1).to_list(500)
    
    notes = await db.notes.find(
        {"case_id": case_id},
        {"_id": 0}
    ).to_list(500)
    
    # Get offence-specific context
    offence_category = case.get('offence_category', 'homicide')
    offence_context = get_offence_context(case)
    
    # Build comprehensive context with bounded document content for responsiveness
    context = f"""
CRIMINAL APPEAL CASE ANALYSIS

CASE DETAILS:
- Title: {case.get('title', 'Unknown')}
- Defendant: {case.get('defendant_name', 'Unknown')}
- Case Number: {case.get('case_number', 'N/A')}
- Court: {case.get('court', 'N/A')}
- Judge: {case.get('judge', 'N/A')}
- Summary: {case.get('summary', 'No summary provided')}

{offence_context}
"""

    doc_context = build_document_context(
        documents,
        per_doc_char_limit=2200,
        total_char_budget=20000,
        include_description=True,
        content_heading="CONTENT"
    )
    
    # Include existing grounds so AI doesn't duplicate them
    if existing_grounds:
        context += f"=== ALREADY IDENTIFIED GROUNDS ({len(existing_grounds)}) ===\n"
        context += "DO NOT re-identify these grounds. Only identify NEW grounds not listed here:\n\n"
        for g in existing_grounds:
            context += f"- [{g.get('ground_type')}] {g.get('title')}\n"
            context += f"  Status: {g.get('status')}, Strength: {g.get('strength')}\n"
        context += "\n"
    
    # Include substantial but bounded document content for AI to analyse
    if documents:
        context += f"=== CASE DOCUMENTS ({doc_context['included_docs']} included / {len(documents)} total files) ===\n\n"
        context += doc_context["text"] + "\n"
        if doc_context["omitted_docs"] > 0:
            context += f"[Note: {doc_context['omitted_docs']} document(s) omitted from prompt for speed optimisation.]\n\n"
    else:
        context += "NO DOCUMENTS UPLOADED YET - Analysis based on case summary only.\n\n"

    if timeline:
        timeline_limit = 120
        timeline_slice = timeline[:timeline_limit]
        context += f"=== TIMELINE OF EVENTS ({len(timeline_slice)} included / {len(timeline)} total events) ===\n"
        for event in timeline_slice:
            context += f"- {event.get('event_date', 'Unknown date')} [{event.get('event_type', 'event')}]: {event.get('title')}\n"
            if event.get('description'):
                context += f"  Details: {event.get('description')}\n"
        if len(timeline) > timeline_limit:
            context += f"[... {len(timeline) - timeline_limit} additional events omitted for speed ...]\n"
        context += "\n"

    if notes:
        notes_limit = 80
        notes_slice = notes[:notes_limit]
        context += f"=== LEGAL NOTES & OBSERVATIONS ({len(notes_slice)} included / {len(notes)} total notes) ===\n"
        for note in notes_slice:
            context += f"- [{note.get('category', 'general')}] {note.get('title')}:\n"
            context += f"  {note.get('content', '')[:300]}\n"
        if len(notes) > notes_limit:
            context += f"[... {len(notes) - notes_limit} additional notes omitted for speed ...]\n"
        context += "\n"

    # Use offence-specific system prompt
    base_system_prompt = get_offence_system_prompt(offence_category)
    
    system_prompt = f"""{base_system_prompt}

YOUR TASK: Conduct an EXHAUSTIVE, METICULOUS analysis of ALL provided case documents to identify EVERY possible ground of appeal. Leave no stone unturned.

ANALYSIS APPROACH - You MUST:
1. READ ALL PROVIDED MATERIAL THOROUGHLY - Extract all relevant facts, dates, witness statements, and evidence
2. CROSS-REFERENCE between materials - Look for contradictions, inconsistencies, and gaps
3. IDENTIFY PROCEDURAL ISSUES - Did police/prosecution follow correct procedures?
4. EXAMINE EVIDENCE HANDLING - Was evidence properly obtained, stored, disclosed?
5. REVIEW WITNESS TESTIMONY - Look for unreliable identification, coached witnesses, inconsistent statements
6. ASSESS LEGAL REPRESENTATION - Was the defence counsel competent? Did they call all witnesses? Cross-examine effectively?
7. CHECK JUDICIAL CONDUCT - Were jury directions proper? Was the judge impartial?
8. LOOK FOR FRESH EVIDENCE - Any new information that wasn't available at trial?
9. EXAMINE EXPERT EVIDENCE - Was forensic/medical evidence properly challenged?
10. CONSIDER DISCLOSURE FAILURES - Did prosecution disclose all relevant material?

GROUND TYPES TO IDENTIFY:
- PROCEDURAL ERROR: Police/court procedure violations, warrant issues, PACE breaches
- FRESH EVIDENCE: New witnesses, DNA evidence, alibis, recanted testimony
- MISCARRIAGE OF JUSTICE: Wrongful conviction indicators, unsafe verdict
- JUDICIAL ERROR: Wrong directions to jury, biased conduct, evidentiary rulings
- INEFFECTIVE COUNSEL: Failure to call witnesses, poor cross-examination, missed defences
- PROSECUTION MISCONDUCT: Non-disclosure, improper statements, witness coaching
- JURY IRREGULARITY: Misconduct, bias, improper deliberations
- SENTENCING ERROR: Manifestly excessive, wrong principles applied
- CONSTITUTIONAL/RIGHTS VIOLATIONS: Unfair trial, self-incrimination issues

BE THOROUGH - It is better to identify 10 potential grounds than miss 1 valid one. The appellant's liberty depends on this analysis.

IMPORTANT: If grounds are listed in "ALREADY IDENTIFIED GROUNDS", do NOT duplicate them. Only add NEW grounds."""

    user_prompt = f"""CONDUCT A COMPREHENSIVE LEGAL ANALYSIS OF THIS CRIMINAL APPEAL CASE:

{context}

INSTRUCTIONS:
1. Analyse EVERY document provided - read the full content carefully
2. Compare witness statements for inconsistencies
3. Identify ANY procedural irregularities
4. Look for evidence that may have been improperly handled or excluded
5. Consider whether the defence was adequate
6. Check for any fresh evidence possibilities
7. Assess whether the verdict was safe

For EACH ground you identify, provide DETAILED analysis including:
- Specific references to documents/evidence
- Why this constitutes a valid ground of appeal
- Relevant NSW and Federal law sections
- Assessment of strength (strong/moderate/weak)
- What evidence supports this ground

Return your analysis in this JSON format:
{{
  "grounds": [
    {{
      "title": "Specific, descriptive title",
      "ground_type": "procedural_error|fresh_evidence|miscarriage_of_justice|sentencing_error|judicial_error|ineffective_counsel|prosecution_misconduct|jury_irregularity|constitutional_violation|other",
      "description": "DETAILED description (at least 3-4 sentences) explaining the ground, citing specific evidence from the documents",
      "strength": "strong|moderate|weak",
      "key_evidence": ["Specific document references and quotes that support this ground"],
      "relevant_law": ["Specific law sections e.g., 's.18 Crimes Act 1900 (NSW)', 'Evidence Act 1995 s.137'"]
    }}
  ],
  "summary": "Overall assessment of appeal prospects and most promising grounds",
  "analysis_notes": "Any additional observations about the case"
}}

BE THOROUGH. Identify ALL potential grounds. The appellant's freedom may depend on this analysis."""

    try:
        response = await call_llm_with_fallback(system_prompt, user_prompt, f"auto_identify_{case_id}_{uuid.uuid4().hex[:8]}")
    except Exception as e:
        logger.error(f"Auto-identify LLM failed: {e}")
        raise HTTPException(status_code=500, detail=f"AI analysis failed after retries: {str(e)}")
    
    # Helper function to check if ground is a duplicate
    def is_duplicate_ground(new_title, new_type, existing_grounds):
        new_title_lower = new_title.lower().strip()
        new_type_lower = new_type.lower().strip()
        
        for existing in existing_grounds:
            existing_title = existing.get('title', '').lower().strip()
            existing_type = existing.get('ground_type', '').lower().strip()
            
            # Same type and similar title = duplicate
            if existing_type == new_type_lower:
                # Check for significant title overlap
                new_words = set(new_title_lower.split())
                existing_words = set(existing_title.split())
                common_words = new_words & existing_words
                # Remove common legal words from comparison
                stop_words = {'the', 'a', 'an', 'of', 'in', 'to', 'for', 'and', 'or', 'at', 'by', 'on', 'with'}
                common_meaningful = common_words - stop_words
                new_meaningful = new_words - stop_words
                
                if len(new_meaningful) > 0:
                    overlap_ratio = len(common_meaningful) / len(new_meaningful)
                    if overlap_ratio > 0.5:  # More than 50% overlap
                        return True
            
            # Very similar titles regardless of type
            if new_title_lower == existing_title:
                return True
        
        return False
    
    # Try to parse JSON from response
    identified_grounds = []
    skipped_duplicates = 0
    try:
        import re
        json_match = re.search(r'\{[\s\S]*"grounds"[\s\S]*\}', response)
        if json_match:
            parsed = json.loads(json_match.group())
            grounds_data = parsed.get("grounds", [])
            
            for g in grounds_data:
                new_title = g.get("title", "Identified Ground")
                new_type = g.get("ground_type", "other")
                
                # Skip if duplicate
                if is_duplicate_ground(new_title, new_type, existing_grounds + identified_grounds):
                    skipped_duplicates += 1
                    logger.info(f"Skipping duplicate ground: {new_title}")
                    continue
                
                ground = GroundOfMerit(
                    case_id=case_id,
                    user_id=user.user_id,
                    title=new_title,
                    ground_type=new_type,
                    description=g.get("description", ""),
                    strength=g.get("strength", "moderate"),
                    supporting_evidence=g.get("key_evidence", []),
                    status="identified"
                )
                
                ground_dict = ground.model_dump()
                ground_dict["created_at"] = ground_dict["created_at"].isoformat()
                ground_dict["updated_at"] = ground_dict["updated_at"].isoformat()
                
                await db.grounds_of_merit.insert_one(ground_dict)
                # Fetch the inserted ground without _id
                created_ground = await db.grounds_of_merit.find_one({"ground_id": ground.ground_id}, {"_id": 0})
                identified_grounds.append(created_ground)
    except Exception as e:
        logger.error(f"Failed to parse AI response: {e}")
        # Only create fallback ground if no grounds were identified
        if len(identified_grounds) == 0:
            ground = GroundOfMerit(
                case_id=case_id,
                user_id=user.user_id,
                title="AI Analysis Results",
                ground_type="other",
                description="See analysis for identified grounds",
                strength="moderate",
                analysis=response,
                status="identified"
            )
            ground_dict = ground.model_dump()
            ground_dict["created_at"] = ground_dict["created_at"].isoformat()
            ground_dict["updated_at"] = ground_dict["updated_at"].isoformat()
            await db.grounds_of_merit.insert_one(ground_dict)
            # Fetch the inserted ground without _id
            created_ground = await db.grounds_of_merit.find_one({"ground_id": ground.ground_id}, {"_id": 0})
            identified_grounds.append(created_ground)
    
    # Update case
    await db.cases.update_one(
        {"case_id": case_id},
        {"$set": {"updated_at": datetime.now(timezone.utc).isoformat()}}
    )
    
    return {
        "identified_count": len(identified_grounds),
        "skipped_duplicates": skipped_duplicates,
        "existing_grounds": len(existing_grounds),
        "message": f"Found {len(identified_grounds)} new grounds. Skipped {skipped_duplicates} duplicates." if skipped_duplicates > 0 else f"Found {len(identified_grounds)} new grounds.",
        "unlock_required": True,
        "unlock_price": FEATURE_PRICES["grounds_of_merit"]["price"]
    }

# ============ AI ANALYSIS & REPORTS ============


def _normalise_text(value: str) -> str:
    cleaned = re.sub(r"[^a-z0-9\s]", " ", (value or "").lower())
    return re.sub(r"\s+", " ", cleaned).strip()


def _token_set(value: str) -> set:
    return {token for token in _normalise_text(value).split(" ") if len(token) > 3}


def _jaccard_similarity(set_a: set, set_b: set) -> float:
    if not set_a or not set_b:
        return 0.0
    intersection = len(set_a & set_b)
    union = len(set_a | set_b)
    return 0.0 if union == 0 else intersection / union


def _build_anchor_terms(case: dict, documents: list, timeline: list, grounds: list) -> set:
    terms = set()

    def add_terms(value):
        if not value:
            return
        for token in re.split(r"[^a-z0-9]+", str(value).lower()):
            if len(token) > 3:
                terms.add(token)

    for field in ["title", "defendant_name", "case_number", "court", "judge", "sentence", "state", "offence_type", "offence_category"]:
        add_terms(case.get(field))

    for doc in documents or []:
        add_terms(doc.get("filename"))
        add_terms(doc.get("category"))
        add_terms(doc.get("document_type"))

    for event in timeline or []:
        add_terms(event.get("title"))
        add_terms(event.get("event_type"))
        add_terms(event.get("event_date"))

    for ground in grounds or []:
        add_terms(ground.get("title"))
        add_terms(ground.get("ground_type"))

    return terms


def _paragraph_quality_score(paragraph: str, anchor_terms: set) -> float:
    if not paragraph:
        return 0.0
    score = 0.0
    if re.search(r"\b\d{2,}\b", paragraph):
        score += 1.1
    if re.search(r"\b(s\.|section)\s*\d+", paragraph, re.I):
        score += 1.2
    if re.search(r"\bAct\s+\d{4}\b", paragraph, re.I):
        score += 1.0
    if re.search(r"\bR\s+v\b", paragraph) or re.search(r"\bNSWCCA\b", paragraph):
        score += 0.9

    word_set = _token_set(paragraph)
    if anchor_terms and word_set:
        anchor_hits = sum(1 for word in word_set if word in anchor_terms)
        score += min(2.0, anchor_hits * 0.25)

    score += min(1.4, len(paragraph) / 1200)
    return score


def _split_report_sections(text: str) -> list:
    parts = re.split(r"(^##\s+\d+\.\s+.+$)", text, flags=re.M)
    if len(parts) <= 1:
        return [("", text.strip())]

    sections = []
    lead = parts[0].strip()
    if lead:
        sections.append(("", lead))

    for index in range(1, len(parts), 2):
        heading = parts[index].strip()
        content = parts[index + 1] if index + 1 < len(parts) else ""
        sections.append((heading, content.strip()))

    return sections


def _dedupe_report_content(text: str, report_type: str, anchor_terms: set) -> str:
    if not text:
        return text

    sections = _split_report_sections(text)
    cleaned_sections = []
    similarity_threshold = 0.85 if report_type == "quick_summary" else 0.82

    for heading, content in sections:
        paragraphs = [p.strip() for p in re.split(r"\n\s*\n+", content) if p.strip()]
        kept = []
        seen_sets = []
        seen_texts = []

        for paragraph in paragraphs:
            if len(paragraph) < 40:
                kept.append(paragraph)
                continue

            paragraph_set = _token_set(paragraph)
            is_duplicate = False
            for existing_set, existing_text in zip(seen_sets, seen_texts):
                if paragraph in existing_text or existing_text in paragraph:
                    is_duplicate = True
                    break
                if _jaccard_similarity(paragraph_set, existing_set) > similarity_threshold:
                    is_duplicate = True
                    break

            if is_duplicate:
                continue

            kept.append(paragraph)
            seen_sets.append(paragraph_set)
            seen_texts.append(paragraph)

        cleaned_sections.append((heading, "\n\n".join(kept).strip()))

    rebuilt = []
    for heading, content in cleaned_sections:
        if heading:
            rebuilt.append(heading)
        if content:
            rebuilt.append(content)

    return "\n\n".join(rebuilt).strip()


def _strip_report_placeholders(text: str) -> str:
    if not text:
        return text
    cleaned_lines = []
    for line in text.splitlines():
        if re.search(r"\[Your Name\]|\[Your Legal Organisation/Team\]", line, re.I):
            continue
        if re.search(r"Best regards|Prepared by|Prepared for|This report was generated by|Criminal Appeal AI|Justitia AI", line, re.I):
            continue
        if re.search(r"\bDO NOT UNDO\.?\b", line, re.I):
            continue
        cleaned_lines.append(line)
    cleaned = "\n".join(cleaned_lines)
    cleaned = re.sub(r"\n{3,}", "\n\n", cleaned).strip()
    # Strip \1 artifacts
    cleaned = cleaned.replace("\\1", "")
    cleaned = cleaned.replace("\x01", "")
    # Strip prompt instruction text from section headings
    cleaned = re.sub(r'\s*—\s*keep ALL[^\n]*', '', cleaned)
    cleaned = re.sub(r'\s*—\s*DETAILED PATHWAY ANALYSIS[^\n]*', '', cleaned)
    cleaned = re.sub(r'\s*\(\d+\+?\s*words[^)]*\)', '', cleaned)  # e.g. "(900+ words per ground, flowing paragraphs)"
    cleaned = re.sub(r'\s*\(\d+\+?\s*CASES[^)]*\)', '', cleaned)  # e.g. "(12+ CASES with full citations)"
    cleaned = re.sub(r'(GROUNDS OF MERIT)\s*—\s*DEEP ANALYSIS', r'\1', cleaned)
    # Sanitise "we/us/our" language — convert to third-person educational tone
    we_us_replacements = [
        (r'\bWe are arguing\b', 'The applicant argues'),
        (r'\bwe are arguing\b', 'the applicant argues'),
        (r'\bWe are aiming\b', 'The appeal aims'),
        (r'\bwe are aiming\b', 'the appeal aims'),
        (r'\bWe are filing\b', 'The legal professional is filing'),
        (r'\bwe are filing\b', 'the legal professional is filing'),
        (r'\bWe are taking\b', 'The legal professional is taking'),
        (r'\bwe are taking\b', 'the legal professional is taking'),
        (r'\bWe succeed\b', 'The appeal succeeds'),
        (r'\bwe succeed\b', 'the appeal succeeds'),
        (r'\bwe will gather\b', 'the legal professional will gather'),
        (r'\bWe will gather\b', 'The legal professional will gather'),
        (r'\bwe will craft\b', 'the legal professional will craft'),
        (r'\bWe will craft\b', 'The legal professional will craft'),
        (r'\bwe will file\b', 'the legal professional will file'),
        (r'\bWe will file\b', 'The legal professional will file'),
        (r'\bwe will prepare\b', 'the legal professional will prepare'),
        (r'\bWe will prepare\b', 'The legal professional will prepare'),
        (r'\bwe will submit\b', 'the legal professional will submit'),
        (r'\bWe will submit\b', 'The legal professional will submit'),
        (r'\bwe will seek\b', 'the applicant will seek'),
        (r'\bWe will seek\b', 'The applicant will seek'),
        (r'\bwe will argue\b', 'the applicant will argue'),
        (r'\bWe will argue\b', 'The applicant will argue'),
        (r'\bwe will demonstrate\b', 'the appeal will demonstrate'),
        (r'\bWe will demonstrate\b', 'The appeal will demonstrate'),
        (r'\bwe will show\b', 'the appeal will show'),
        (r'\bWe will show\b', 'The appeal will show'),
        (r'\bcontact with us\b', 'contact with the legal professional'),
        (r'\bContact us\b', 'Contact the legal professional'),
        (r'\bcontact us\b', 'contact the legal professional'),
        (r'\bour submissions\b', 'the submissions'),
        (r'\bOur submissions\b', 'The submissions'),
        (r'\bour claims\b', "the applicant's claims"),
        (r'\bOur claims\b', "The applicant's claims"),
        (r'\bour arguments\b', "the applicant's arguments"),
        (r'\bOur arguments\b', "The applicant's arguments"),
        (r'\bour position\b', "the applicant's position"),
        (r'\bOur position\b', "The applicant's position"),
        (r'\bour case\b', "the applicant's case"),
        (r'\bOur case\b', "The applicant's case"),
        (r'\bour strategy\b', 'the legal strategy'),
        (r'\bOur strategy\b', 'The legal strategy'),
        (r'\bour analysis\b', 'this analysis'),
        (r'\bOur analysis\b', 'This analysis'),
        (r'\bon our behalf\b', 'on behalf of the applicant'),
        (r'\bback our\b', "support the applicant's"),
        (r'\bensuring our\b', 'ensuring the'),
        (r', we are\b', ', the legal professional is'),
        (r', we will\b', ', the legal professional will'),
        (r', we have\b', ', the legal professional has'),
        (r'\bWe have identified\b', 'This analysis has identified'),
        (r'\bwe have identified\b', 'this analysis has identified'),
        (r'\bWe have reviewed\b', 'This analysis has reviewed'),
        (r'\bwe have reviewed\b', 'this analysis has reviewed'),
        (r'\bWe have analysed\b', 'This analysis has examined'),
        (r'\bwe have analysed\b', 'this analysis has examined'),
        (r'\bWe have analyzed\b', 'This analysis has examined'),
        (r'\bwe have analyzed\b', 'this analysis has examined'),
    ]
    for pattern, replacement in we_us_replacements:
        cleaned = re.sub(pattern, replacement, cleaned)
    
    # Catch-all: replace remaining "we " patterns at sentence boundaries
    cleaned = re.sub(r'\bwe facilitate\b', 'this analysis facilitates', cleaned, flags=re.I)
    cleaned = re.sub(r'\bwe recommend\b', 'it is recommended', cleaned, flags=re.I)
    cleaned = re.sub(r'\bwe note\b', 'it is noted', cleaned, flags=re.I)
    cleaned = re.sub(r'\bwe observe\b', 'it is observed', cleaned, flags=re.I)
    cleaned = re.sub(r'\bwe consider\b', 'it is considered', cleaned, flags=re.I)
    cleaned = re.sub(r'\bwe conclude\b', 'it is concluded', cleaned, flags=re.I)
    cleaned = re.sub(r'\bwe suggest\b', 'it is suggested', cleaned, flags=re.I)
    cleaned = re.sub(r'\bwe assess\b', 'this analysis assesses', cleaned, flags=re.I)
    cleaned = re.sub(r'\bwe examine\b', 'this analysis examines', cleaned, flags=re.I)
    cleaned = re.sub(r'\bwe highlight\b', 'this analysis highlights', cleaned, flags=re.I)
    cleaned = re.sub(r'\bwe identify\b', 'this analysis identifies', cleaned, flags=re.I)
    cleaned = re.sub(r'\bwe believe\b', 'it is assessed', cleaned, flags=re.I)
    cleaned = re.sub(r'\bwe find\b', 'this analysis finds', cleaned, flags=re.I)
    cleaned = re.sub(r'\bwe can see\b', 'it can be seen', cleaned, flags=re.I)
    cleaned = re.sub(r'\bwe can\b', 'the applicant can', cleaned, flags=re.I)
    cleaned = re.sub(r'\bwe must\b', 'the legal professional must', cleaned, flags=re.I)
    cleaned = re.sub(r'\bwe should\b', 'the legal professional should', cleaned, flags=re.I)
    cleaned = re.sub(r'\bwe need\b', 'the legal professional needs', cleaned, flags=re.I)
    cleaned = re.sub(r', we \b', ', the analysis ', cleaned)
    cleaned = re.sub(r'\. We \b', '. This analysis ', cleaned)
    # Catch remaining "our" possessives
    cleaned = re.sub(r'\bour client\b', 'the applicant', cleaned, flags=re.I)
    cleaned = re.sub(r'\bour focus\b', 'the focus', cleaned, flags=re.I)
    cleaned = re.sub(r'\bour team\b', 'the legal professional', cleaned, flags=re.I)
    cleaned = re.sub(r'\bour review\b', 'this review', cleaned, flags=re.I)
    cleaned = re.sub(r'\bour assessment\b', 'this assessment', cleaned, flags=re.I)
    cleaned = re.sub(r'\bour examination\b', 'this examination', cleaned, flags=re.I)
    
    # Strip "you/your" language — third-person only
    you_your_replacements = [
        (r'\byour opportunity\b', 'the opportunity'),
        (r'\bYour opportunity\b', 'The opportunity'),
        (r'\byour conviction\b', 'the conviction'),
        (r'\bYour conviction\b', 'The conviction'),
        (r'\bgiven to you\b', 'imposed'),
        (r'\bGiven to you\b', 'Imposed'),
        (r'\byour sentence\b', 'the sentence'),
        (r'\bYour sentence\b', 'The sentence'),
        (r'\byour appeal\b', 'the appeal'),
        (r'\bYour appeal\b', 'The appeal'),
        (r'\byour case\b', 'the case'),
        (r'\bYour case\b', 'The case'),
        (r'\byour trial\b', 'the trial'),
        (r'\bYour trial\b', 'The trial'),
        (r'\byour lawyer\b', 'the legal representative'),
        (r'\bYour lawyer\b', 'The legal representative'),
        (r'\byour barrister\b', 'the barrister'),
        (r'\bYour barrister\b', 'The barrister'),
        (r'\byour solicitor\b', 'the solicitor'),
        (r'\bYour solicitor\b', 'The solicitor'),
        (r'\byour legal team\b', 'the legal team'),
        (r'\bYour legal team\b', 'The legal team'),
        (r'\byour legal representative\b', 'the legal representative'),
        (r'\bYour legal representative\b', 'The legal representative'),
        (r'\byour defence\b', 'the defence'),
        (r'\bYour defence\b', 'The defence'),
        (r'\byour rights\b', 'the rights of the applicant'),
        (r'\bYour rights\b', 'The rights of the applicant'),
        (r'\byour circumstances\b', 'the circumstances'),
        (r'\bYour circumstances\b', 'The circumstances'),
        (r'\byour situation\b', 'the situation'),
        (r'\bYour situation\b', 'The situation'),
        (r'\byour matter\b', 'this matter'),
        (r'\bYour matter\b', 'This matter'),
        (r'\byour prospects\b', 'the prospects'),
        (r'\bYour prospects\b', 'The prospects'),
        (r'\byour grounds\b', 'the grounds'),
        (r'\bYour grounds\b', 'The grounds'),
        (r'\byour documents\b', 'the documents'),
        (r'\bYour documents\b', 'The documents'),
        (r'\byou may\b', 'the applicant may'),
        (r'\bYou may\b', 'The applicant may'),
        (r'\byou can\b', 'the applicant can'),
        (r'\bYou can\b', 'The applicant can'),
        (r'\byou should\b', 'the applicant should'),
        (r'\bYou should\b', 'The applicant should'),
        (r'\byou must\b', 'the applicant must'),
        (r'\bYou must\b', 'The applicant must'),
        (r'\byou will\b', 'the applicant will'),
        (r'\bYou will\b', 'The applicant will'),
        (r'\byou need\b', 'the applicant needs'),
        (r'\bYou need\b', 'The applicant needs'),
        (r'\byou have\b', 'the applicant has'),
        (r'\bYou have\b', 'The applicant has'),
        (r'\byou are\b', 'the applicant is'),
        (r'\bYou are\b', 'The applicant is'),
        (r'\byou were\b', 'the applicant was'),
        (r'\bYou were\b', 'The applicant was'),
        (r'\bfor you\b', 'for the applicant'),
        (r'\bFor you\b', 'For the applicant'),
        (r'\bto you\b', 'to the applicant'),
        (r'\bTo you\b', 'To the applicant'),
        (r'\bagainst you\b', 'against the applicant'),
        (r'\bAgainst you\b', 'Against the applicant'),
        (r'\bif you\b', 'if the applicant'),
        (r'\bIf you\b', 'If the applicant'),
        (r'\bwhen you\b', 'when the applicant'),
        (r'\bWhen you\b', 'When the applicant'),
    ]
    for pattern, replacement in you_your_replacements:
        cleaned = re.sub(pattern, replacement, cleaned)
    # Catch remaining "your" as possessive — broad catch-all
    cleaned = re.sub(r'\byour\b', "the applicant's", cleaned)
    cleaned = re.sub(r'\bYour\b', "The applicant's", cleaned)
    
    # Strip placeholder/future-tense filler text
    cleaned = re.sub(r'(?:The |This )?(?:comparative sentencing |sentencing )?table (?:below )?will (?:reference|provide|include|contain|show|list|detail|present|outline|cover)\b', 'The table references', cleaned, flags=re.I)
    cleaned = re.sub(r'(?:Details|Information|Data|Analysis|Content),?\s*(?:including [^,]+,?\s*)?will be provided\b', 'Details are provided', cleaned, flags=re.I)
    
    # Fix broken markdown links: <Text> [Text](url) → just [Text](url)
    cleaned = re.sub(r'<([^>]+)>\s*\[([^\]]+)\]\(([^)]+)\)', r'[\2](\3)', cleaned)
    # Fix raw angle-bracket links: <Text> without markdown
    cleaned = re.sub(r'<(Search [^>]+)>', r'\1', cleaned)
    
    return cleaned


async def analyze_case_with_ai(case_id: str, user_id: str, report_type: str, aggressive_mode: bool = False, report_id: str = None) -> dict:
    """Use OpenAI GPT-5.2 to analyse case and generate report"""
    from emergentintegrations.llm.chat import LlmChat, UserMessage
    
    # Get case data
    case = await db.cases.find_one({"case_id": case_id, "user_id": user_id}, {"_id": 0})
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
    
    # Get documents with full content
    documents = await db.documents.find(
        {"case_id": case_id},
        {"_id": 0, "file_data": 0}
    ).to_list(500)
    
    # Get timeline
    timeline = await db.timeline_events.find(
        {"case_id": case_id},
        {"_id": 0}
    ).sort("event_date", 1).to_list(500)
    
    # Get notes
    notes = await db.notes.find(
        {"case_id": case_id},
        {"_id": 0}
    ).to_list(100)
    
    # Get identified grounds
    grounds = await db.grounds_of_merit.find(
        {"case_id": case_id},
        {"_id": 0}
    ).to_list(100)
    
    # Get offence-specific context
    offence_category = case.get('offence_category', 'homicide')
    offence_context = get_offence_context(case)
    category_data = OFFENCE_CATEGORIES.get(offence_category, OFFENCE_CATEGORIES.get('homicide'))
    category_name = category_data.get('name', 'criminal')
    state = case.get('state', 'nsw')
    state_info = AUSTRALIAN_STATES.get(state, AUSTRALIAN_STATES.get('nsw'))
    
    # Context limits — FULL DETAIL for quality reports
    context_limits = {
        "quick_summary": {
            "per_doc_chars": 700,
            "total_doc_chars": 6000,
            "timeline_limit": 40,
            "notes_limit": 20,
            "note_chars": 180,
            "grounds_limit": 30,
            "ground_desc_chars": 200,
            "ground_analysis_chars": 200,
            "ground_deep_chars": 0,
        },
        "full_detailed": {
            "per_doc_chars": 2400,
            "total_doc_chars": 24000,
            "timeline_limit": 150,
            "notes_limit": 80,
            "note_chars": 500,
            "grounds_limit": 80,
            "ground_desc_chars": 600,
            "ground_analysis_chars": 500,
            "ground_deep_chars": 0,
        },
        "extensive_log": {
            "per_doc_chars": 3200,
            "total_doc_chars": 32000,
            "timeline_limit": 200,
            "notes_limit": 100,
            "note_chars": 600,
            "grounds_limit": 100,
            "ground_desc_chars": 800,
            "ground_analysis_chars": 700,
            "ground_deep_chars": 700,
        },
    }
    limits = context_limits.get(report_type, context_limits["quick_summary"])

    # Prepare comprehensive context for AI with bounded document content
    case_context = f"""
=== CASE INFORMATION ===
Title: {case.get('title', 'N/A')}
Defendant: {case.get('defendant_name', 'N/A')}
Case Number: {case.get('case_number', 'N/A')}
Court: {case.get('court', 'N/A')}
Judge: {case.get('judge', 'N/A')}
Sentence: {case.get('sentence', 'N/A')}
Summary: {case.get('summary', 'N/A')}

{offence_context}
"""

    doc_context = build_document_context(
        documents,
        per_doc_char_limit=limits["per_doc_chars"],
        total_char_budget=limits["total_doc_chars"],
        include_description=True,
        content_heading="CONTENT"
    )
    
    # Include bounded document content for cross-referencing
    if documents:
        case_context += f"=== CASE DOCUMENTS ({doc_context['included_docs']} included / {len(documents)} total files) ===\n"
        case_context += doc_context["text"] + "\n"
        if doc_context["omitted_docs"] > 0:
            case_context += f"[Note: {doc_context['omitted_docs']} document(s) omitted from prompt for speed optimisation.]\n"
    else:
        case_context += "=== NO DOCUMENTS UPLOADED ===\n"

    if timeline:
        timeline_slice = timeline[:limits["timeline_limit"]]
        case_context += f"\n=== TIMELINE OF EVENTS ({len(timeline_slice)} included / {len(timeline)} total events) ===\n"
        for event in timeline_slice:
            case_context += f"- {event.get('event_date', 'Unknown')}: [{event.get('event_type')}] {event.get('title')}\n"
            if event.get('description'):
                case_context += f"  Details: {event.get('description')}\n"
        if len(timeline) > limits["timeline_limit"]:
            case_context += f"[... {len(timeline) - limits['timeline_limit']} additional events omitted for speed ...]\n"

    if notes:
        notes_slice = notes[:limits["notes_limit"]]
        case_context += f"\n=== LEGAL NOTES ({len(notes_slice)} included / {len(notes)} total notes) ===\n"
        for note in notes_slice:
            case_context += f"- [{note.get('category')}] {note.get('title')}: {note.get('content', '')[:limits['note_chars']]}\n"
        if len(notes) > limits["notes_limit"]:
            case_context += f"[... {len(notes) - limits['notes_limit']} additional notes omitted for speed ...]\n"

    if grounds:
        grounds_slice = grounds[:limits["grounds_limit"]]
        case_context += f"\n=== IDENTIFIED GROUNDS OF MERIT ({len(grounds_slice)} included / {len(grounds)} total grounds) ===\n"
        for g in grounds_slice:
            case_context += f"- [{g.get('ground_type')}] {g.get('title')} (Strength: {g.get('strength')})\n"
            case_context += f"  {g.get('description', '')[:limits['ground_desc_chars']]}\n"
            if report_type != "quick_summary" and g.get('analysis'):
                case_context += f"  Analysis: {g.get('analysis', '')[:limits['ground_analysis_chars']]}\n"
            if limits["ground_deep_chars"] > 0 and g.get('deep_analysis'):
                deep = g.get('deep_analysis', '')
                if isinstance(deep, str):
                    case_context += f"  Deep Analysis: {deep[:limits['ground_deep_chars']]}\n"
        if len(grounds) > limits["grounds_limit"]:
            case_context += f"[... {len(grounds) - limits['grounds_limit']} additional grounds omitted for speed ...]\n"

    grounds_titles = [g.get('title') for g in grounds if g.get('title')]
    grounds_enumerated = "\n".join([f"{idx + 1}. {title}" for idx, title in enumerate(grounds_titles)])

    # Define prompts based on report type with offence-specific language
    base_system = get_offence_system_prompt(offence_category)
    report_guardrails = """
MANDATORY GUARDRAILS:
- Use a HYBRID tone: court-ready legal analysis + plain-English action notes for the client.
- Use Australian English only.
- Anchor findings to supplied case material; clearly mark uncertainty when evidence is incomplete.
- Include legislation as: section + Act + jurisdiction + year (e.g. s.18 Crimes Act 1900 (NSW)).
- Include sentencing comparisons and precedent outcomes where relevant.
- DO NOT include cost estimates, fee ranges, funding commentary, or budget analysis.
- DO NOT include witness contradiction sections or witness credibility scoring sections.

LANGUAGE RULES — ABSOLUTE AND NON-NEGOTIABLE:
- This report is an EDUCATIONAL TOOL. It is NOT written by a legal team speaking on behalf of the applicant.
- NEVER use the words "we", "us", "our", or "them" when referring to the legal team, analysis team, or report authors.
- NEVER use the words "you" or "your" when addressing the reader or the applicant. WRONG: "The appeal is your opportunity to challenge your conviction." RIGHT: "The appeal represents an opportunity for the applicant to challenge the conviction."
- Instead of "we are arguing" write "the applicant argues" or "this analysis identifies".
- Instead of "we will file" write "the legal professional will file" or "the applicant should file".
- Instead of "our submissions" write "the submissions" or "the applicant's submissions".
- Instead of "contact us" write "contact the legal professional" or "contact the assisting legal practitioner".
- Instead of "we are aiming to show" write "the appeal aims to demonstrate" or "the applicant seeks to establish".
- Instead of "our claims" write "the applicant's claims" or "the claims advanced".
- Instead of "your appeal" write "the appeal". Instead of "your conviction" write "the conviction". Instead of "your sentence" write "the sentence".
- Instead of "you should" write "the applicant should". Instead of "you may" write "the applicant may". Instead of "for you" write "for the applicant".
- The report must read as a neutral educational analysis document, NOT as a first-person legal team communication and NOT as a second-person advisory letter.
- Use third-person references throughout: "the applicant", "the defendant", "the legal professional", "this analysis", "the appeal".
- Violations of this rule make the report legally problematic and unprofessional.

NO PLACEHOLDER TEXT — ABSOLUTE RULE:
- NEVER write future-tense placeholder text like "The table will reference...", "Details will be provided...", "This section will include...", "Content will be added...", or "Analysis will cover...".
- Every sentence must contain ACTUAL analysis, ACTUAL data, or ACTUAL legal content. If a table cannot be populated with real data from the case material, populate it with the best available comparable cases from Australian jurisprudence.
- If information is unavailable, state that explicitly ("No sentencing comparisons could be identified from the supplied material") rather than promising future content.

CONTENT QUALITY — STRICTLY ENFORCED (violations make the report worthless):
- DO the analysis. Do NOT describe what analysis should be done. WRONG: "Delve into aggravating and mitigating factors." RIGHT: "Under s.21A(2) of the Crimes (Sentencing Procedure) Act 1999 (NSW), the aggravating factors in Homann's case include the use of a weapon and the vulnerability of the victim. However, the sentencing judge failed to give adequate weight to the mitigating factor under s.21A(3)(d)..."
- NEVER create filler sections with titles like "URGENCY PRIORITY", "RELEVANCE", "KEY TAKEAWAY", "SUMMARY", "OVERVIEW" as standalone sections. These are padding. Instead, weave relevance and urgency INTO the substantive analysis.
- NEVER write generic consultant-speak like "Leverage legal databases to draw parallels that authenticate excessive sentencing claims through empirical trends." Instead, NAME the specific cases, cite the specific sentencing outcomes, and EXPLAIN the specific parallels.
- Every paragraph MUST reference specific names, dates, section numbers, case citations, or document names from the supplied case material. If a paragraph could apply to ANY appeal case, it is too generic — rewrite it with THIS case's specific facts.
- Avoid repetition across sections. If a point is already covered, deepen it with NEW evidence, dates, or authority rather than restating it.
- Do NOT reuse boilerplate phrases. Every paragraph must read as drafted specifically for this case and this report tier.
- For legislation sections: Do NOT just name the Act and describe what it covers in general terms. APPLY each provision to THIS case's specific facts. WRONG: "s.44 discusses parole periods, directly affecting Homann's sentencing outcomes." RIGHT: "Under s.44 of the Crimes (Sentencing Procedure) Act 1999 (NSW), the non-parole period must reflect the objective seriousness of the offence. In Homann's case, the 22-year non-parole period imposed by Justice McCallum is arguable as disproportionate when compared with R v Loveridge [2014] NSWCCA 120 where a 7-year non-parole period was imposed for a one-punch manslaughter..."
- For precedent/sentencing tables: Include the full case citation, the specific factual similarity to THIS case, the actual sentence imposed, and the specific relevance to the current appeal. NEVER use a one-line vague description.

FORMATTING RULES — STRICTLY ENFORCED:
- DO NOT begin your response with any preamble, greeting, or introduction.
- DO NOT use placeholder notes in brackets like "[Note: Continue...]", "[Insert details...]". Every section MUST contain COMPLETE, REAL content.
- Every section heading MUST be followed by substantive content (minimum 3-4 detailed paragraphs). If a section cannot be substantiated from the case material, omit it entirely.
- Include the year in ALL legislation references (e.g. Crimes Act 1900 (NSW), NOT just Crimes Act (NSW)).
- SECTION HEADINGS: Use ONLY ## for numbered section headings (e.g. ## 1. EXECUTIVE BRIEF). Do NOT create sub-sections with ### headings. Do NOT put bold text on its own line as a sub-heading. Instead, write flowing paragraphs and use bold text inline (e.g. "The **legal threshold** for this ground requires...").
- FOR GROUND ANALYSIS: Write each ground as a continuous series of detailed paragraphs (minimum 300 words in Quick Summary, 500+ words in Full Detailed, 900+ words in Extensive). Do NOT use bullet points. Cover the legal threshold, case facts, viability, Crown response, defence rebuttal, and impact all within flowing prose.
"""
    
    if report_type == "quick_summary":
        system_prompt = f"""{base_system}
{report_guardrails}
You are generating a FREE Quick Summary. Deliver real legal value in a concise overview, then clearly explain what deeper paid reports add. IMPORTANT: Write at least 2000 words. Every section must have 3-5 substantive paragraphs — do NOT compress sections into bullet-point lists or single sentences."""
        user_prompt = f"""Analyse this {category_name.lower()} appeal matter and produce a QUICK SUMMARY REPORT.

{case_context}

Write MINIMUM 2000 words (target range 2000-3000 words). This is an OVERVIEW but each section must still be substantive with multiple paragraphs. Do NOT abbreviate or summarise sections into single sentences. Structure EXACTLY as follows:

## 1. CASE SNAPSHOT
3-4 paragraphs covering: defendant, offence, jurisdiction, sentence imposed, non-parole period, key procedural dates, presiding judge, and what material was reviewed. Be specific to the supplied facts.

MANDATORY: Start this section with a summary line: "This analysis is based on [X] documents and [Y] timeline events. [Z] grounds of appeal have been identified." Use the EXACT counts from the supplied case data.

## 2. PRIMARY ISSUES IDENTIFIED
6-10 bullet points. Each bullet must include:
- Issue label
- Which document/evidence it comes from
- Why it matters legally for an appeal

## 3. ALL GROUNDS IDENTIFIED (PREVIEW)
You MUST list EVERY ground identified in the case materials (use the grounds list provided below). For each ground:
- Ground title + type (e.g., Procedural Irregularity, Manifestly Excessive Sentence)
- Strength rating: Strong / Moderate / Weak
- 2-3 sentence legal rationale referencing the specific case facts
- One immediate action step in plain English

## 4. KEY LEGISLATION & SIMILAR CASES (PREVIEW)
First, list the most relevant statutory provisions from {state_info.get('name', 'NSW')} / Commonwealth law with section numbers, years, and one-line relevance notes.
Then list 2-3 comparable Australian appeal decisions with citation, outcome (allowed/dismissed/resentenced), and why each is relevant to this case.

## 5. SENTENCING OVERVIEW
2-3 paragraphs comparing the sentence imposed against typical appellate principles and proportionality for this offence category. Then provide a mini comparison table:
| Comparator Case | Original Sentence / NPP | Appeal Outcome | Revised Sentence / NPP | Key Insight |
Include at least 3 rows with real comparable cases.

## 6. APPEAL OUTLOOK
Overall assessment: Strong / Moderate / Needs Further Development.
2-3 paragraphs explaining the reasoning, strongest pathway to relief, and main risk factors.

## 7. CLIENT PLAIN-ENGLISH GUIDE
Explain the case and appeal in clear, plain English for a non-lawyer: what the sentence means, what grounds exist, what the next steps are, and what outcomes are realistic. This section must appear BEFORE the paid-report comparison so clients understand their current position. CRITICAL: This is an educational tool — use ONLY third-person language ("the applicant", "the legal professional"). ABSOLUTE BAN on "we", "us", "our", "you", "your". WRONG: "your conviction" RIGHT: "the conviction". WRONG: "you should" RIGHT: "the applicant should".

## 8. APPEAL OUTLOOK
Brief assessment of realistic prospects for each ground. State the overall strength rating (Strong / Moderate / Needs Further Development) and explain for each ground.

IMPORTANT:
- No cost estimates or funding discussion.
- No witness contradiction or witness credibility section.
- Be specific to the supplied material throughout — do not write generic legal advice.

GROUNDS TO COVER (MUST INCLUDE ALL — list every single one below):
{grounds_enumerated}

MATERIAL COUNTS (use these exact numbers in the report):
- Total documents analysed: {len(documents)}
- Total timeline events: {len(timeline)}
- Total grounds identified: {len(grounds)}"""

    elif report_type == "full_detailed":
        system_prompt = f"""{base_system}
{report_guardrails}
You are generating a PAID Full Detailed Report ($150 AUD). This report is the PRIMARY product the client is paying for.

CRITICAL RULES FOR THIS REPORT:
1. The client ALREADY has a FREE Quick Summary. If ANY section in this report resembles the Quick Summary, the product is WORTHLESS.
2. Every section must be 3x MORE detailed than the equivalent free report section.
3. Every paragraph must cite SPECIFIC case facts: names (Joshua Homann, Kirralee Paepaerei, Justice McCallum), dates (21 September 2015, 25 May 2018), section numbers (s.23A Crimes Act 1900 (NSW)), and document names.
4. NEVER write generic legal explanations. WRONG: "The appeal process involves reviewing the original decision." RIGHT: "Homann's appeal to the NSWCCA challenges the 30-year sentence imposed by Justice McCallum on 25 May 2018 for the murder of Kirralee Paepaerei, arguing that the non-parole period of 22 years and 6 months is manifestly excessive when compared with..."
5. EVERY ground listed in GROUNDS TO COVER MUST be covered in FULL in Sections 4, 7, 11, and 15. If there are 5 grounds, write 5 full analyses. NO OMISSIONS.
6. Write in FLOWING PARAGRAPHS, not bullet points. Bullet points are ONLY acceptable inside tables or checklists.
7. Each section heading must be followed by AT LEAST 4-6 detailed paragraphs of substantive analysis.

Include assertive appellate strategy, professional courtroom framing, and plain-English action notes. Include working hyperlinks to AustLII legislation, case databases, and court forms wherever possible.
CRITICAL: NEVER use placeholder text in parentheses like '(Entries will develop...)'. Every section MUST have REAL, SUBSTANTIVE CONTENT with actual legal analysis."""
        user_prompt = f"""Create a FULL DETAILED LEGAL ANALYSIS REPORT for this {category_name.lower()} appeal case.

{case_context}

GROUNDS TO COVER — YOU MUST INCLUDE EVERY SINGLE ONE (if 5 grounds, write 5 full analyses):
{grounds_enumerated}

MATERIAL COUNTS (use these exact numbers in the report):
- Total documents analysed: {len(documents)}
- Total timeline events: {len(timeline)}
- Total grounds identified: {len(grounds)}

TARGET: 15,000-20,000 words minimum. This is a $150 AUD paid product. It must be AT LEAST 3x the depth of the free Quick Summary in EVERY section.

ANTI-LAZINESS RULES — VIOLATIONS MAKE THE REPORT WORTHLESS:
1. Section 1 (Executive Brief): MUST be 4-6 paragraphs with strategic assessment, NOT just a case snapshot rehash. Name the strongest ground, the weakest ground, the most likely outcome, and the recommended immediate action.
2. Section 2 (Forensic Chronology): MUST have 12+ dated events in FULL PARAGRAPH FORMAT (not bullet points). Each entry: date, what happened, source document, legal significance. Write 3-4 sentences per event minimum.
3. Section 3 (Document Evidence Digest): MUST analyse EVERY uploaded document individually with key extracts, reliability, and appellate relevance. One paragraph per document minimum.
4. Section 4 (Grounds Portfolio): MUST cover EVERY ground with 800+ words each. Include: legal threshold, case-specific facts, viability rating with reasoning, Crown response prediction (what will the prosecution argue?), defence rebuttal strategy, practical impact if ground succeeds. Write as flowing prose, NOT bullets.
5. Section 7 (Outcome Options): MUST write 300+ words for EACH outcome pathway (conviction quashed, retrial, downgrade, sentence reduction, appeal dismissed). Reference which specific grounds support each outcome.
6. Section 11 (How to Argue): MUST cover EVERY ground — if there are 5 grounds, write 5 complete argument strategies with lead proposition, supporting authority, prosecution answer, and rebuttal. 400+ words per ground.
7. Section 12 (Submissions Blueprint): Write ACTUAL draft submission paragraphs ready for court. Include specific argument sequences, authority placement, and time allocation. NOT bullet point summaries.
8. Section 15 (Client Brief): MUST cover EVERY ground and EVERY outcome in plain English. Explain what each ground means in simple terms and what happens if it succeeds. 1000+ words minimum for this section.

SECTION ORDERING: Analysis first, then Strategy, then Practical steps, then Client brief at the end.

Use this exact structure:

## 1. EXECUTIVE BRIEF
High-impact strategic summary: 4-6 paragraphs covering strongest grounds, jurisdiction posture, likely pathways to relief, urgency items, recommended strategy, and risk factors. Include case snapshot (defendant, offence, sentence, court, judge) and primary issues. This section must ADD strategic value beyond the free report.

MANDATORY: Start with: "This analysis is based on [X] documents and [Y] timeline events. [Z] grounds of appeal have been identified." Use EXACT counts.

## 2. FORENSIC CASE CHRONOLOGY
Full chronological reconstruction with 12+ dated entries. Each entry must be a FULL PARAGRAPH (3-4 sentences minimum) with: exact date, what occurred, which document/evidence supports it, and legal significance for the appeal. Write this as a narrative, NOT as bullet points.

## 3. DOCUMENT EVIDENCE DIGEST
For EACH document uploaded: title, key extracts (quote directly), reliability context, probative value, and specific appellate relevance. One detailed paragraph per document minimum.

## 4. GROUNDS OF MERIT PORTFOLIO
For EACH ground listed in GROUNDS TO COVER (ALL of them — no omissions):
Write as "Ground X: [Exact Title]" then 800+ words of flowing paragraphs covering: legal threshold and test, supporting material from case files, viability rating (Strong/Moderate/Weak) with detailed reasoning, predicted Crown response, aggressive defence rebuttal strategy, and practical appeal impact if established.

## 5. COMPARATIVE SENTENCING TABLE (8+ CASES)
CRITICAL: Produce an ACTUAL populated markdown table with real case data — NEVER placeholder text like "The table will reference..." or "Details will be provided...".
Markdown table with 8+ comparable cases, then Detailed Outcome Analysis paragraph for each row.
| Case | Offence | Original Sentence / NPP | Appeal Outcome | Revised Sentence / NPP | Reduction (Years + %) | Key Reason |
Include AustLII search URL.

## 6. COMMON APPEAL GROUNDS FOR THIS OFFENCE TYPE
Markdown table with 8+ rows:
| Common Ground | Frequency in Comparable Appeals | Typical Success Pattern | Best Supporting Evidence |

## 7. OUTCOME OPTIONS AVAILABLE
First, markdown table. Then 300+ words for EACH pathway referencing specific grounds from Section 4:
- **Conviction quashed** — which grounds support this, legal threshold, likelihood
- **Retrial ordered** — implications, timeframes, changes
- **Conviction substituted/downgraded** — legal basis, sentence impact
- **Sentence reduced as manifestly excessive** — before/after with specific numbers
- **Appeal dismissed** — consequences, further options (High Court)

## 8. EVIDENTIARY GAPS + REMEDIATION CHECKLIST
Specific missing material with urgency priority (Critical/Important/Helpful) and exact remediation steps.

## 9. PRECEDENT OUTCOME MATRIX (10-12 CASES)
For each: citation, factual similarity, hearing outcome, extracted legal principle.

## 10. STATUTORY + DOCTRINAL FRAMEWORK MAP
APPLY each provision to THIS case — section number, Act name with year, specific relevance to Homann's appeal.

## 11. HOW TO ARGUE EACH TOP GROUND
For EACH ground (ALL of them — no omissions), write 400+ words covering:
- Lead proposition (core argument in 2 sentences)
- Supporting authority cluster (statute + 2-3 precedent anchors with citations)
- Expected prosecution answer (what will the Crown argue?)
- Rebuttal strategy with specific authority
- How establishing this ground leads to successful appeal outcome

## 12. SUBMISSIONS BLUEPRINT
Write ACTUAL draft submission text ready for court. Not bullet point summaries.
Written submission strategy: full argument sequence paragraphs, authority placement, framing of each ground.
Oral submission strategy: likely bench questions with response lines, time allocation per ground.

## 13. HOW TO START YOUR APPEAL + REQUIRED FORMS
Step-by-step guide specific to {state_info.get('name', 'NSW')} with forms table.

## 14. PRIORITISED ACTION PLAN
72-hour / 7-day / 28-day actions. Each action: what to do, who to contact, objective.

## 15. CLIENT PLAIN-ENGLISH BRIEF
1000+ words explaining in plain English: what the appeal is about, what EACH ground means, chances of success for each, what happens next, realistic outcomes, and what the applicant should do now. Cover EVERY ground individually. CRITICAL: Use ONLY third-person language. ABSOLUTE BAN on "you", "your", "we", "us", "our". Use "the applicant", "the legal professional".

IMPORTANT:
- No cost discussion. No witness contradiction section.
- Every section must have substantive content — no placeholders.
- Keep ALL outcomes within SECTION 7. Keep ALL timeframes within SECTION 14.
- NEVER truncate. Write the ACTUAL full content."""

    else:  # extensive_log
        system_prompt = f"""{base_system}
{report_guardrails}
You are generating the PREMIUM Extensive Report ($200 AUD) — the most detailed and case-specific legal analysis available.

The user has ALREADY received BOTH:
1. A FREE Quick Summary (case overview, top grounds preview, basic sentencing comparison)
2. A PAID Full Detailed Report (executive brief, forensic chronology, evidence digest, grounds portfolio with Crown/defence strategy, 8+ sentencing comparisons, outcome options matrix, evidence gaps checklist, 10-12 precedent cases, statutory framework, argument strategy, submissions blueprint, appeal steps guide, action plan, and plain-English brief)

THIS PREMIUM REPORT MUST BUILD ON — NOT REPEAT — THE FULL DETAILED REPORT. Do NOT re-state the same analysis. Instead:
- Where the Full Detailed analysed each ground with Crown response and rebuttal, THIS report must provide 900+ word DEEP analysis per ground with fallback positions, additional authorities, and draft submission paragraphs.
- Where the Full Detailed provided 8+ sentencing comparisons, THIS report must provide 12+ with detailed paragraph analysis for EACH case.
- Where the Full Detailed had a precedent matrix of 10-12 cases, THIS report must have 15+ with specific factual comparisons.
- THIS report adds 5 ENTIRELY NEW sections not in the Full Detailed: Hearing Preparation Notes, Conference Preparation Pack, Court Pathway Operations Playbook, Similar Case Search Options, and Risk Assessment + Contingency Planning.
- Every shared section must go SIGNIFICANTLY deeper with fresh analysis, additional authorities, and more detailed strategy.

Every section must directly reference the supplied case material. Include working hyperlinks to AustLII legislation, case databases, and court forms wherever possible.
CRITICAL: NEVER use placeholder text. Every section MUST have REAL, SUBSTANTIVE, CASE-SPECIFIC CONTENT. Each ground analysis must be at least 900 words. Reference specific documents, dates, and facts from the case throughout."""
        user_prompt = f"""Create a PREMIUM EXTENSIVE legal analysis report for this {category_name.lower()} appeal case. This must be the MOST COMPREHENSIVE report — significantly more detailed and case-specific than the Full Detailed tier.

{case_context}

GROUNDS TO COVER (MUST INCLUDE ALL — if 9 grounds, write 9 full analyses):
{grounds_enumerated}

MATERIAL COUNTS (use these exact numbers in the report):
- Total documents analysed: {len(documents)}
- Total timeline events: {len(timeline)}
- Total grounds identified: {len(grounds)}

Target range 25000-35000 words. Every section must reference specific facts, documents, and dates from this case.

CRITICAL — NO REPETITION FROM FULL DETAILED REPORT:
The user already has a Full Detailed Report covering grounds analysis, sentencing table (8 cases), outcome options, evidence gaps, precedent matrix (10-12 cases), statutory framework, argument strategy, submissions blueprint, appeal steps, and action plan. This Premium Extensive report must ADVANCE BEYOND all of that with deeper per-ground analysis (900+ words each), expanded tables (12+ sentencing, 15+ precedents), and 5 ENTIRELY NEW sections: Hearing Preparation Notes, Conference Preparation Pack, Court Pathway Operations Playbook, Similar Case Search Options, and Risk Assessment + Contingency Planning. Do NOT copy or paraphrase content from the lower-tier reports.

SECTION ORDERING: Case-specific analysis first, then broader legal framework, then strategy, then practical steps, then client brief at the very end.

Use this exact structure:

## 1. EXECUTIVE BRIEF
Confident assessment of the appeal: strongest grounds with specific evidence anchors, jurisdiction posture, pathways to relief, urgency items, and a clear one-paragraph statement of the case. Include a case snapshot paragraph (defendant, offence, sentence, court, judge) and a short list of primary issues at the end.

MANDATORY: Start this section with a summary line: "This analysis is based on [X] documents and [Y] timeline events. [Z] grounds of appeal have been identified." Use the EXACT counts from the supplied case data.

## 2. FORENSIC CASE CHRONOLOGY
Comprehensive chronological reconstruction with at least 15 dated entries. For each entry:
- Date
- Event description (specific to the case facts)
- Source document/evidence
- Legal significance for the appeal
Include pre-trial, trial, sentencing, and post-sentencing events.

## 3. DOCUMENT EVIDENCE DIGEST
For EACH document/source in the case material:
- Key extracts (quote directly where possible)
- Reliability and credibility assessment
- Probative value for the appeal
- Which grounds this evidence supports
- Rating: Critical / Important / Supporting / Peripheral

## 4. GROUNDS OF MERIT — DEEP ANALYSIS
For EACH ground listed in GROUNDS TO COVER above (no omissions), provide a MINIMUM 900-word analysis:
- Legal threshold with specific statutory reference (section + Act + year)
- How the case facts satisfy or approach this threshold — quote evidence
- Viability rating (Strong / Moderate / Weak) with detailed reasoning
- Likely Crown prosecution response (specific, not generic)
- Aggressive defence rebuttal strategy with authority citations
- **Practical impact if this ground succeeds** — what order the court would make, what happens to the conviction/sentence
- Key authority with AustLII link and explanation of how it applies
- Fallback position if the primary argument on this ground is rejected
- Write each ground as a numbered entry starting with "Ground X: [Exact Title]" and then flowing paragraphs (no bullet-only answers). Minimum 900 words per ground
- Write each ground as a numbered entry starting with "Ground X: [Exact Title]" and then flowing paragraphs (no bullet-only answers)

## 5. COMPARATIVE SENTENCING TABLE (12+ CASES)
CRITICAL: This section MUST contain an ACTUAL populated markdown table with real case data — NEVER placeholder text like "The table will reference..." or "Details will be provided...". If exact data cannot be found, use the best available comparable cases from Australian jurisprudence.

Markdown table with at least 12 comparable sentencing outcomes:
| Case | Offence | Original Sentence / NPP | Appeal Outcome | Revised Sentence / NPP | Reduction (Years + %) | Key Reason |
Include AustLII search link: [Search {state_info.get('appeal_court', 'NSWCCA')}]({state_info.get('cca_search_url', 'https://www.austlii.edu.au/cgi-bin/viewtoc/au/cases/nsw/NSWCCA/')})
After the table, provide a DETAILED paragraph for EACH case explaining:
- What was the original sentence and sentencing judge's reasoning
- What the appeal court decided and why
- How the reduction was achieved and which grounds succeeded
- How this compares to the current case

## 6. COMMON APPEAL GROUNDS FOR THIS OFFENCE TYPE
| Common Ground | Frequency in Comparable Appeals | Typical Success Pattern | Best Supporting Evidence |
Then provide detailed analysis of how each common ground applies or does not apply to THIS specific case.

## 7. OUTCOME OPTIONS — DETAILED PATHWAY ANALYSIS
Markdown table:
| Option | Legal Threshold | Likelihood in This Matter | Core Evidence Trigger | Practical Result |
Then provide DETAILED analysis (minimum 150 words each) for EVERY pathway (keep ALL outcomes within THIS section — do NOT create separate ## headings for each outcome):
- **Conviction quashed** — what standard must be met, what evidence supports this, what the defendant's position would be, which grounds support this outcome
- **Retrial ordered** — when this happens instead of quashing, what the retrial process involves, timeframes
- **Conviction substituted/downgraded** (e.g., murder to manslaughter) — legal basis, resulting sentence range, how this has worked in comparable cases
- **Sentence reduced as manifestly excessive** — show explicit before/after: Original sentence/NPP → Revised sentence/NPP with percentage reduction
- **Appeal dismissed** — consequences, options for special leave to the High Court, time limits

## 8. EVIDENTIARY GAPS + REMEDIATION CHECKLIST
For each gap:
- What is missing from the case file
- Why it matters for the appeal
- Exact steps to obtain it (who to contact, what to request, expected timeframe)
- Priority: Critical / Important / Helpful
- Impact on which grounds if not remediated

## 9. PRECEDENT OUTCOME MATRIX (15+ CASES)
For each of at least 15 cases:
- Full citation
- Factual similarity to this matter (specific comparison)
- Hearing outcome
- Extracted legal principle
- How this principle applies to the current case
Include AustLII link: [Search {state_info.get('appeal_court', 'NSWCCA')}]({state_info.get('cca_search_url', 'https://www.austlii.edu.au/cgi-bin/viewtoc/au/cases/nsw/NSWCCA/')})

## 10. STATUTORY + DOCTRINAL FRAMEWORK MAP
15+ statutory provisions with:
- Section number, Act name with year, jurisdiction
- AustLII link: [AustLII Legislation](https://www.austlii.edu.au/cgi-bin/viewdb/au/legis/)
- How this provision specifically applies to the current case
- Any recent amendments that affect the appeal

## 11. HOW TO ARGUE EACH TOP GROUND — DETAILED STRATEGY
For each priority ground (minimum 200 words each):
- Lead proposition (the core argument stated in 1-2 powerful lines)
- Supporting authority cluster (specific statute section + 3-4 precedent cases with citations)
- Expected Crown prosecution response (specific to this case)
- Detailed rebuttal strategy for the hearing
- Fallback argument if the primary submission is rejected
- **How establishing this ground leads to a specific appeal outcome** (what order to seek)

## 12. SUBMISSIONS BLUEPRINT
Written submission strategy (write as flowing paragraphs, NOT bullet lists):
Discuss the recommended argument sequence and why this ordering maximises impact. Explain the authority placement strategy for each ground. Describe how each ground should be framed in written submissions with key passages to quote from case material.

Oral submission strategy (write as flowing paragraphs, NOT bullet lists):
Discuss the likely bench questions for each ground with prepared responses. Cover time allocation per ground, opening and closing lines, and how to handle judicial scepticism on weaker grounds.

## 13. HEARING PREPARATION NOTES
For each ground, write detailed flowing paragraphs (NOT bullet lists or dot points):
Cover the key arguments and talking points for each ground, the anticipated questions from the bench with suggested responses, which authority to cite first and why, and any visual aids or demonstratives to prepare.
- Concessions to make strategically vs points to contest

## 14. CONFERENCE PREPARATION PACK
For briefing a barrister:
- One-page case summary (lead theory)
- Authorities shortlist with key passages highlighted
- Orders sought (specific orders to request from the court)
- Case strengths (with evidence references)
- Case weaknesses and mitigation strategy
- Client instructions summary
- Key dates and deadlines

## 15. COURT PATHWAY OPERATIONS PLAYBOOK
For EACH relevant court level ({state_info.get('name', 'NSW')} specific):
- Filing sequence and required documents
- Court registry details and contact information
- Deadlines for each filing step
- Extension-of-time route if deadlines have passed
- What happens at each stage of the process

## 16. HOW TO START YOUR APPEAL + REQUIRED FORMS
Step-by-step guide specific to {state_info.get('name', 'NSW')}:
1. Obtain trial transcripts and exhibits
2. Identify and finalise grounds of appeal
3. Lodge Notice of Intention to Appeal
4. Prepare detailed written submissions
5. Serve documents on the Crown/DPP
6. Attend the appeal hearing
For each step: plain English explanation, required form, deadline, and link.
Forms table:
| Form/Document | Purpose | Where to Obtain | Filing Deadline |
Links: [Legal Aid {state_info.get('name', 'NSW')}]({state_info.get('legal_aid_url', 'https://www.legalaid.nsw.gov.au/')}) | [AustLII](https://www.austlii.edu.au/) | [Court Forms]({state_info.get('court_forms_url', '#')})

## 17. SIMILAR CASE SEARCH OPTIONS
Tailored AustLII search guidance:
- 5+ query strings specifically designed for this case's offence and grounds profile
- Links: [Search {state_info.get('appeal_court', 'NSWCCA')}]({state_info.get('cca_search_url', 'https://www.austlii.edu.au/cgi-bin/viewtoc/au/cases/nsw/NSWCCA/')}) | [Search all states](https://www.austlii.edu.au/)
- Court-level filtering suggestions
- Keyword alternatives for each ground
- How to narrow results to the most relevant period and jurisdiction

## 18. PRIORITISED ACTION PLAN
72-hour actions (urgent — time-sensitive filings, evidence at risk of loss):
- Specific action, who to contact, deadline, objective

7-day actions (important — evidence gathering, legal research):
- Specific action, resources needed, dependencies

28-day actions (strategic — submission drafting, hearing preparation):
- Specific action, preparation steps, milestones

## 19. RISK ASSESSMENT + CONTINGENCY PLANNING
For each ground:
- Probability of success (percentage range)
- Main risk factor
- Contingency if this ground fails
- Impact on overall appeal if this ground is excluded

Overall appeal risk assessment:
- Best case scenario and likelihood
- Most likely outcome
- Worst case scenario and mitigation

## 20. CLIENT PLAIN-ENGLISH BRIEF
THIS MUST BE THE FINAL SECTION. Write this as if explaining the case to the defendant in everyday language, BUT STRICTLY IN THIRD PERSON:
- What the appeal is about and why it matters
- What are the strongest arguments in the applicant's favour (reference specific facts)
- What are the realistic chances of success
- What the different possible outcomes mean for the applicant personally
- What the applicant needs to do right now, this week, and this month
- What to expect at the hearing
- Honest assessment of risks alongside the opportunities
CRITICAL: This section is an educational tool. Use ONLY third-person language ("the applicant", "the legal professional", "this analysis"). NEVER use "we", "us", "our", "you", "your", or "them" when referring to the legal team or the applicant. WRONG: "The appeal is your opportunity to challenge your conviction." RIGHT: "The appeal represents an opportunity for the applicant to challenge the conviction."

IMPORTANT:
- Use markdown headings and tables exactly where specified.
- Working hyperlinks to AustLII and court websites throughout.
- Every section MUST reference specific facts from the supplied case material — no generic legal advice.
- This report must be VISIBLY more comprehensive than the Full Detailed tier.
- Australian English throughout.
- No cost discussion. No witness contradiction section.
- Quote directly from supplied documents where relevant.
- Every conclusion must be tied to case material or clearly marked as an assumption.
- NEVER use continuation markers like "... (continue with further analysis)", "... (continue analysis of other cases)", or similar truncation. Write the ACTUAL content for every section.
- Do NOT insert meta-commentary about the document itself (e.g., "This truncated document provides..."). Only output the report content.
- Keep ALL outcome pathways (conviction quashed, retrial, etc.) within SECTION 7 — do NOT create separate ## headings for individual outcomes.
- Keep ALL action items (72-hour, 7-day, 28-day) within SECTION 18 — do NOT create separate ## headings for each timeframe."""

    if aggressive_mode:
        aggressive_directive = """

AGGRESSIVE ADVOCACY MODE (USER-REQUESTED) — THIS FUNDAMENTALLY CHANGES YOUR APPROACH:

TONE SHIFT — You are no longer a cautious analyst. You are a senior criminal appeal barrister preparing to ARGUE this case in court. Write as if you are personally invested in winning this appeal:
- Use ASSERTIVE, CONFIDENT language: "This ground is compelling", "The Crown's position is untenable", "The sentencing judge plainly erred"
- NEVER hedge with "may", "could potentially", "it is possible that". Instead: "The evidence establishes", "This constitutes a clear error", "The conviction cannot stand"
- Frame EVERY ground as an argument TO BE WON, not a possibility to be explored
- Attack prosecution weaknesses directly: "The Crown's reliance on [X] is fatally undermined by [Y]"
- Draft ACTUAL submission paragraphs that could be read to the bench word-for-word
- For each ground, write the opening line you would say to the Court of Appeal judges
- Assume a standard (non-aggressive) version already exists. This aggressive report must add materially NEW arguments, authorities, and case-specific detail — do NOT rephrase or recycle the standard report.
- If a point is already made earlier in this report, deepen it with NEW evidence, dates, or authority rather than repeating it.
- This aggressive report must be approximately DOUBLE the depth of the standard report. Do not compress or summarise.

EXPANDED SCOPE:
1. DOUBLE the word count target for the entire report.
2. For EVERY ground of appeal, provide:
   - The STRONGEST possible legal argument as if arguing before the bench
   - Minimum 3 specific case citations that directly support this ground
   - A draft submission paragraph ready to be read in court
   - The specific orders to seek if this ground succeeds
   - Fallback position with alternative argument if primary is challenged
3. COMPARATIVE SENTENCING TABLE: 15+ cases minimum. For each, explain HOW the reduction was achieved.
4. OUTCOME OPTIONS: 250+ words per pathway. Reference ALL identified grounds for each pathway.
5. SUBMISSIONS: Write FULL draft argument paragraphs, not outlines. Include opening, authority chains, and closing for each ground.
6. PRECEDENT MATRIX: 20+ cases with detailed factual comparison.
7. Every conclusion must state the SPECIFIC order sought from the court.
8. Write as if the appeal WILL succeed — identify the path to victory, not just the obstacles.
"""
        system_prompt = f"{system_prompt}\n{aggressive_directive}"
        user_prompt = f"""{user_prompt}

AGGRESSIVE ADVOCACY MODE IS ON. Write as a senior barrister who believes in this appeal.
- DOUBLE the word count target.
- Use confident, assertive advocacy language throughout — no hedging, no "may", no "could potentially".
- Draft actual submission paragraphs for each ground that could be read to the bench.
- Frame the analysis as building the STRONGEST possible case for the appellant.
- Every section must reference specific case facts and documents.
- Attack Crown weaknesses directly and confidently.
- Write the opening line you would use to address the Court of Appeal for each key argument."""

    # Call AI — run in SUBPROCESS to isolate from FastAPI network stack
    # Direct subprocess calls work reliably (tested: 6 seconds)
    api_key = os.environ.get('EMERGENT_LLM_KEY')
    if not api_key:
        raise HTTPException(status_code=500, detail="AI service not configured")

    async def _subprocess_llm(prompt_text):
        """Run LLM call directly — retries across multiple models with exponential backoff."""
        
        models = [
            ("openai", "gpt-4o"),
            ("openai", "gpt-4o"),
            ("openai", "gpt-4o"),
            ("anthropic", "claude-sonnet-4-20250514"),
            ("openai", "gpt-4o-mini"),
            ("openai", "gpt-4o-mini"),
        ]
        call_timeout = 420 if report_type in ("full_detailed", "extensive_log") else 300
        
        last_err = None
        for idx, (provider, model_name) in enumerate(models):
            try:
                chat = LlmChat(api_key=api_key, session_id="rpt_gen", system_message=system_prompt).with_model(provider, model_name).with_params(max_tokens=16384)
                result = await asyncio.wait_for(
                    chat.send_message(UserMessage(text=prompt_text)),
                    timeout=call_timeout
                )
                if result and len(result.strip()) > 200 and "I'm sorry" not in result[:100] and "I can't assist" not in result[:100]:
                    logger.info(f"LLM success with {provider}/{model_name} on attempt {idx+1}")
                    return result
                if "I'm sorry" in result[:100] or "I can't assist" in result[:100]:
                    last_err = f"Model refused: {result[:100]}"
                else:
                    last_err = f"Short response ({len(result)} chars)"
                logger.warning(f"LLM attempt {idx+1} ({provider}/{model_name}): {last_err}")
            except asyncio.TimeoutError:
                last_err = f"Timeout after {call_timeout}s with {provider}/{model_name}"
                logger.warning(last_err)
            except Exception as e:
                last_err = str(e)[:200]
                logger.warning(f"LLM attempt {idx+1} ({provider}/{model_name}) failed: {last_err}")
            # Exponential backoff: 5s, 10s, 20s, 30s, 45s, 60s
            delay = min(60, 5 * (2 ** idx))
            logger.info(f"Retrying in {delay}s...")
            await asyncio.sleep(delay)
        
        raise Exception(f"All LLM attempts failed. Last error: {last_err}")

    response = None
    last_error = None
    try:
        if report_type == "full_detailed":
            # Five-pass generation for full_detailed (3 sections per pass)
            passes = [
                ("PASS 1/5", f"""

NOW GENERATE ONLY SECTIONS 1-3. Write 4000+ WORDS for this pass. DO NOT BE LAZY. This is a $150 paid report.

## 1. EXECUTIVE BRIEF (800+ words)
Write 4-6 FULL paragraphs — NOT a rehash of the case snapshot. Include:
- Paragraph 1: Document/timeline/grounds counts, then strategic overview of the appeal's overall strength
- Paragraph 2: The 2 strongest grounds and why they have the best chance of success — name specific legal tests
- Paragraph 3: The most likely outcome pathway and what the client should prepare for
- Paragraph 4: Key risks and vulnerabilities the prosecution will exploit
- Paragraph 5: Recommended immediate actions with specific deadlines
- Paragraph 6: Primary issues identified (list 6-8 specific legal issues with document references)

## 2. FORENSIC CASE CHRONOLOGY (1200+ words)
Write 12+ dated events as FULL PARAGRAPHS (3-4 sentences each). NOT bullet points. Format each as:
"On [DATE], [WHAT HAPPENED]. This is evidenced by [SOURCE DOCUMENT]. The legal significance is [SIGNIFICANCE]. This event [IMPACT ON APPEAL]."
Cover: the offence date, arrest, charges, key witness statements, psychiatric assessments, trial dates, sentencing, appeal filing.

## 3. DOCUMENT EVIDENCE DIGEST (800+ words)
For EACH of the {len(documents)} uploaded documents, write a FULL PARAGRAPH analysing: document title, key extracts (quote directly where possible), reliability, probative value, and specific appellate relevance. If there are 10 documents, write 10 paragraphs.

STOP after section 3. Write ALL content — do NOT truncate or summarise."""),
                ("PASS 2/5", f"""

NOW GENERATE ONLY SECTIONS 4-6. Write 5000+ WORDS for this pass. Section 4 is the MOST IMPORTANT section — do NOT rush it.

## 4. GROUNDS OF MERIT PORTFOLIO
You MUST write about EVERY ground listed below. If there are 5 grounds, write 5 complete analyses. NO OMISSIONS.
GROUNDS TO COVER:
{grounds_enumerated}

For EACH ground, write 800+ words as flowing paragraphs (NOT bullet points) covering:
1. "Ground X: [Exact Title from above]" as the heading
2. The legal test/threshold for this ground (cite the specific statutory provision and leading case)
3. How the case facts satisfy this test (reference specific evidence, dates, witnesses)
4. Viability rating: Strong / Moderate / Weak — with 3-4 sentences explaining WHY
5. PREDICTED CROWN RESPONSE: What will the prosecution argue against this ground? (3-4 sentences)
6. DEFENCE REBUTTAL: How should the defence counter the Crown's argument? (3-4 sentences)
7. APPEAL IMPACT: If this ground succeeds, what happens? (conviction quashed? sentence reduced? retrial?)

## 5. COMPARATIVE SENTENCING TABLE (8+ CASES)
CRITICAL: Produce an ACTUAL populated markdown table with real case data — NEVER placeholder text.
Write a markdown table with 8+ rows. After the table, write a Detailed Outcome Analysis PARAGRAPH for each case.

## 6. COMMON APPEAL GROUNDS FOR THIS OFFENCE TYPE
Markdown table with 8+ rows.

STOP after section 6."""),
                ("PASS 3/5", f"""

NOW GENERATE ONLY SECTIONS 7-9. Write 4000+ WORDS for this pass.

## 7. OUTCOME OPTIONS AVAILABLE
First provide the summary table, then write 300+ WORDS for EACH of these 5 pathways:
- **Conviction quashed**: Which of the {len(grounds)} grounds support this? What is the legal threshold (e.g., miscarriage of justice under s.6(1) Criminal Appeal Act)? How likely given this case's facts?
- **Retrial ordered**: What triggers a retrial vs outright quashing? What changes at retrial? Timeframes?
- **Conviction substituted/downgraded**: Could murder be reduced to manslaughter? Under what legal basis? Sentence impact?
- **Sentence reduced as manifestly excessive**: Show the exact before/after — Original sentence/NPP → what a reduced sentence might look like, with percentage reduction
- **Appeal dismissed**: What happens? Consequences? Can the client seek special leave to the High Court?

## 8. EVIDENTIARY GAPS + REMEDIATION CHECKLIST (600+ words)
List 8+ specific gaps with urgency ratings and exact remediation steps.

## 9. PRECEDENT OUTCOME MATRIX (10-12 CASES)
Full citations, factual similarities, outcomes, and extracted principles for each case.

STOP after section 9."""),
                ("PASS 4/5", f"""

NOW GENERATE ONLY SECTIONS 10-12. Write 4000+ WORDS for this pass. Sections 11 and 12 are critical — do NOT write thin bullet-point summaries.

## 10. STATUTORY + DOCTRINAL FRAMEWORK MAP (800+ words)
For EACH relevant statutory provision, write a paragraph APPLYING it to THIS case. Not generic descriptions of what the Act covers.

## 11. HOW TO ARGUE EACH TOP GROUND
You MUST cover EVERY ground — ALL {len(grounds)} of them. For EACH ground, write 400+ words covering:
GROUNDS TO COVER:
{grounds_enumerated}

For each ground:
- **Lead Proposition**: The core argument in 2 sentences
- **Supporting Authority Cluster**: Specific statute section + 2-3 precedent cases with citations
- **Expected Prosecution Answer**: What the Crown will argue (3-4 sentences, be specific)
- **Rebuttal Strategy**: How to counter the Crown's argument at hearing (3-4 sentences)
- **If Established**: What outcome this ground achieves

## 12. SUBMISSIONS BLUEPRINT (800+ words)
Write ACTUAL DRAFT SUBMISSION TEXT ready for court — not bullet point summaries.
**Written Submission Strategy**: Full argument sequence paragraphs that could be filed with the court. Include specific argument structure, authority placement, and framing of each ground.
**Oral Submission Strategy**: Likely bench questions with prepared response lines. Time allocation per ground. Opening and closing strategies.

STOP after section 12."""),
                ("PASS 5/5", f"""

NOW GENERATE ONLY SECTIONS 13-15. Write 4000+ WORDS for this pass. Section 15 is critical — it must be thorough and cover EVERY ground.

## 13. HOW TO START YOUR APPEAL + REQUIRED FORMS (800+ words)
Step-by-step guide with forms table. Each step: what to do in plain English, required form, deadline, and link.

## 14. PRIORITISED ACTION PLAN (600+ words)
72-hour actions (urgent filings, time-sensitive steps) — at least 5 specific actions.
7-day actions (evidence gathering, legal research) — at least 5 specific actions.
28-day actions (submission drafting, hearing preparation) — at least 5 specific actions.
Each action: what to do, who to contact, objective, and deadline.

## 15. CLIENT PLAIN-ENGLISH BRIEF (1500+ words)
THIS IS NOT GENERIC WAFFLE. For EACH of the {len(grounds)} grounds, explain in plain English using ONLY third-person language:
- What this ground means in simple terms
- Why it matters for the appeal
- What the chances of success are
- What happens if it succeeds

Then cover:
- The overall appeal: what it is, why it's happening, and the timeline
- The realistic possible outcomes and what each means for the applicant
- Exactly what the applicant should do right now, this week, and this month
- ABSOLUTE BAN: NEVER use "we", "us", "our", "you", "your". Use "the applicant", "the legal professional". WRONG: "your opportunity" RIGHT: "the opportunity for the applicant"

Do NOT truncate. Write ALL content for all 3 sections."""),
            ]
            
            parts = []
            resume_from = 0
            if report_id:
                existing_report = await db.reports.find_one(
                    {"report_id": report_id},
                    {"_id": 0, "content.partial_analysis": 1, "content.passes_completed": 1},
                )
                existing_content = (existing_report or {}).get("content") or {}
                existing_partial = existing_content.get("partial_analysis") or ""
                existing_passes_completed = int(existing_content.get("passes_completed") or 0)
                if existing_partial and existing_passes_completed > 0:
                    parts = [existing_partial]
                    resume_from = min(existing_passes_completed, len(passes))
                    logger.info(f"Resuming full_detailed report {report_id} from pass {resume_from + 1}")

            for pass_index, (label, instruction) in enumerate(passes[resume_from:], start=resume_from + 1):
                pass_prompt = user_prompt + instruction
                logger.info(f"Full detailed {label} prompt size: system={len(system_prompt)}, user={len(pass_prompt)}")
                part = await _subprocess_llm(pass_prompt)
                parts.append(part)
                logger.info(f"Full detailed {label} response: {len(part)} chars")
                # Partial save after each pass to prevent data loss on server restart
                if report_id:
                    partial_content = "\n\n".join(parts)
                    await db.reports.update_one(
                        {"report_id": report_id},
                        {"$set": {"content.analysis": partial_content, "content.partial": True, "content.partial_analysis": partial_content, "content.passes_completed": pass_index}}
                    )
            
            response = "\n\n".join(parts)
            logger.info(f"Full detailed combined: {len(response)} chars")

        elif report_type == "extensive_log":
            # Seven-pass generation for extensive_log (3 sections per pass)
            passes = [
                ("PASS 1/7", f"""

NOW GENERATE ONLY SECTIONS 1-3. Write 5000+ WORDS for this pass. This is a $200 PREMIUM report — every paragraph must be packed with case-specific facts, not generic legal education.

## 1. EXECUTIVE BRIEF (1200+ words)
Write 6-8 FULL paragraphs (NOT bullet points):
- Paragraph 1: Document/timeline/grounds counts from supplied data, then strategic overview of the appeal's overall strength with percentage assessment
- Paragraph 2: The 2-3 STRONGEST grounds with specific evidence anchors and legal tests that support them
- Paragraph 3: The weakest ground and why it's still worth pursuing (or should be abandoned)
- Paragraph 4: Jurisdiction-specific posture — what the {state_info.get('appeal_court', 'NSWCCA')} typically does with this type of appeal
- Paragraph 5: Most likely outcome pathway and realistic assessment of relief
- Paragraph 6: Key risks the prosecution will exploit and how to counter them
- Paragraph 7: Immediate actions required with specific deadlines
- Paragraph 8: Summary of 8+ primary issues identified with document references

## 2. FORENSIC CASE CHRONOLOGY (1500+ words)
Write 18+ dated events as FULL PARAGRAPHS (4-5 sentences each). NOT bullet points. Each event:
"On [EXACT DATE], [WHAT HAPPENED in detail]. This is established by [SOURCE DOCUMENT with specific reference]. The legal significance for the appeal is [SIGNIFICANCE]. The prosecution's likely treatment of this event is [PROSECUTION VIEW], while the defence can argue [DEFENCE POSITION]."
Cover: offence date and circumstances, arrest, charges laid, bail, committal, psychiatric/forensic reports, plea, trial dates, key witness testimony, jury directions, verdict, sentencing submissions, sentence, appeal filing.

## 3. DOCUMENT EVIDENCE DIGEST (1200+ words)
For EACH of the {len(documents)} uploaded documents, write 2-3 FULL PARAGRAPHS analysing:
- Document title and date
- Key extracts (QUOTE directly from the document content where possible)
- Reliability and credibility assessment
- Probative value — what it proves or disproves
- Which specific grounds this document supports
- Rating: Critical / Important / Supporting / Peripheral
If there are 10 documents, write 20-30 paragraphs.

STOP after section 3. Write ALL content — do NOT truncate."""),
                ("PASS 2/7", f"""

NOW GENERATE ONLY SECTIONS 4-5. Write 6000+ WORDS for this pass. Section 4 is the HEART of the $200 report — each ground must be a mini-essay.

## 4. GROUNDS OF MERIT — DEEP ANALYSIS
You MUST write about EVERY ground listed below. If there are 5 grounds, write 5 complete analyses. NO OMISSIONS.
GROUNDS TO COVER:
{grounds_enumerated}

For EACH ground, write 1200+ words as flowing paragraphs (NOT bullet points) covering:
1. "Ground X: [Exact Title from above]" as the heading
2. LEGAL THRESHOLD: The specific test for this ground — cite the statutory provision (section + Act + year) and the leading case that established the test. Explain what must be proved.
3. FACTUAL BASIS: How THIS case's specific facts satisfy the test. Reference documents, dates, witness statements. Quote from case material where possible.
4. VIABILITY RATING: Strong / Moderate / Weak — with 5-6 sentences explaining WHY, citing comparable cases where this type of ground succeeded or failed.
5. CROWN RESPONSE PREDICTION: Write 4-5 sentences predicting EXACTLY what the prosecution will argue. Be specific — name the authorities they'll rely on.
6. DEFENCE REBUTTAL STRATEGY: Write 4-5 sentences with the specific counter-argument. Name authorities that trump the Crown's position.
7. FALLBACK POSITION: If the primary argument fails, what's the fallback? (2-3 sentences)
8. APPEAL IMPACT: If this ground succeeds — conviction quashed? Sentence reduced? Retrial? What specific court order should be sought?
9. KEY AUTHORITY: Name the single most important case, provide the citation, and explain in 3-4 sentences exactly how it applies to this ground in this case.

## 5. COMPARATIVE SENTENCING TABLE (12+ CASES)
CRITICAL: Produce an ACTUAL populated markdown table with real case data — NEVER placeholder text like "The table will reference..." or "Details will be provided...".
Markdown table with 12+ rows. After the table, write a DETAILED PARAGRAPH for EACH of the 12+ cases (200+ words each) explaining: original sentencing reasoning, appeal court's reasoning, how the reduction was achieved, which grounds succeeded, and how this specifically compares to the current case.

STOP after section 5."""),
                ("PASS 3/7", f"""

NOW GENERATE ONLY SECTIONS 6-8. Write 4000+ WORDS for this pass.

## 6. COMMON APPEAL GROUNDS FOR THIS OFFENCE TYPE
Markdown table with 10+ rows, then for EACH common ground write 100+ words explaining how it does or does not apply to THIS specific case. Reference the actual grounds identified in this case where they overlap.

## 7. OUTCOME OPTIONS — DETAILED PATHWAY ANALYSIS
First provide summary table, then write 400+ WORDS for EACH of these 5 pathways (ALL within this one section):
- **Conviction quashed entirely**: Which of the {len(grounds)} grounds support this? What's the legal standard (e.g., miscarriage of justice)? What evidence is strongest? Historical success rate for this type of case?
- **Retrial ordered**: What triggers a retrial? What changes? Timeframes? Risks? What happens if the same evidence is presented?
- **Conviction substituted/downgraded**: Could the charge be reduced? Under what legal basis? What would the new sentence range be? Which grounds support this?
- **Sentence reduced as manifestly excessive**: Show EXACT before/after — Original sentence/NPP → realistic revised sentence/NPP with percentage. Which sentencing comparisons from Section 5 support this?
- **Appeal dismissed**: What happens? Consequences for the applicant? Special leave to High Court — threshold, timeframe, realistic prospects?

## 8. EVIDENTIARY GAPS + REMEDIATION CHECKLIST (800+ words)
List 10+ specific gaps. For each: what's missing, why it matters, exact steps to obtain it (who to contact, what to request, expected timeframe), priority (Critical/Important/Helpful), impact on which grounds if not remediated.

STOP after section 8."""),
                ("PASS 4/8", """

NOW GENERATE ONLY SECTIONS 9-10. Write 3200+ WORDS for this pass.

## 9. PRECEDENT OUTCOME MATRIX (12+ CASES)
For each of 12+ cases, write a FULL PARAGRAPH (not just a table row):
- Full citation
- Factual similarity to THIS matter (be specific — offence type, relationship, circumstances)
- Hearing outcome
- Extracted legal principle
- How this principle applies to the current case (3-4 sentences)

## 10. STATUTORY + DOCTRINAL FRAMEWORK MAP (1000+ words)
12+ statutory provisions. For EACH provision, write a FULL PARAGRAPH:
- Section number, Act name with year, jurisdiction
- What the provision covers (1 sentence)
- How it SPECIFICALLY APPLIES to THIS case (3-4 sentences) — name the defendant, the offence, the ground it relates to
- Any recent amendments or judicial interpretation that affects the appeal

STOP after section 10."""),
                ("PASS 5/8", f"""

NOW GENERATE ONLY SECTION 11. Write 2800+ WORDS for this pass. This pass exists so EVERY ground can be fully argued without truncation.

## 11. HOW TO ARGUE EACH TOP GROUND — DETAILED STRATEGY
MUST cover ALL {len(grounds)} grounds. For EACH ground write 500+ words:
GROUNDS TO COVER:
{grounds_enumerated}

For each ground:
- **Lead Proposition**: The core argument in 2 powerful sentences
- **Supporting Authority Cluster**: Specific statute + 3-4 precedent cases with full citations and 2-3 sentences explaining each
- **Expected Crown Response**: 4-5 sentences predicting what the prosecution will argue
- **Rebuttal Strategy**: 4-5 sentences with specific counter-authorities
- **Fallback Position**: If the primary argument is rejected, what's the alternative? (3-4 sentences)
- **If Established**: What specific court order should be sought?

STOP after section 11."""),
                ("PASS 6/8", f"""

NOW GENERATE ONLY SECTIONS 12-14. Write 5000+ WORDS for this pass. These are the sections that make this $200 report UNIQUE. Sections 13 and 14 DO NOT exist in the $150 report.

## 12. SUBMISSIONS BLUEPRINT (1500+ words)
**Written Submission Strategy**: Write ACTUAL DRAFT PARAGRAPHS that could be filed with the court. For each major ground, write 2-3 paragraphs of draft submission text. Include argument sequence, authority placement, and framing. Write the opening paragraph and closing paragraph of the written submissions.

**Oral Submission Strategy** (write as flowing paragraphs, NOT bullet lists): For each ground, discuss the opening line to say to the bench, the likely bench questions with prepared response lines, time allocation recommendations, and how to handle judicial scepticism on weaker grounds. Write this as continuous prose.

## 13. HEARING PREPARATION NOTES (1200+ words — NEW SECTION NOT IN $150 REPORT)
For EACH of the {len(grounds)} grounds, write detailed flowing paragraphs (NOT bullet lists or dot points):
Cover the key arguments and talking points for each ground, the top 3 anticipated bench questions with suggested answers woven into the prose, which authority to cite first and why, concessions to make strategically vs points to contest, and any visual aids or demonstratives to prepare. Write as continuous analytical prose.

## 14. CONFERENCE PREPARATION PACK (1200+ words — NEW SECTION NOT IN $150 REPORT)
For briefing a barrister — write as an actual document:
- One-page case summary (write the ACTUAL summary — 300+ words covering lead theory, key facts, strongest grounds)
- Authorities shortlist (10+ cases with key passages identified)
- Orders sought (list specific court orders to request)
- Case strengths with evidence references (6+ points)
- Case weaknesses and mitigation strategy (4+ points with specific counter-arguments)
- Client instructions summary

STOP after section 14."""),
                ("PASS 7/8", f"""

NOW GENERATE ONLY SECTIONS 15-17. Write 4000+ WORDS for this pass. These sections are UNIQUE to the $200 report.

## 15. COURT PATHWAY OPERATIONS PLAYBOOK (1200+ words — NEW SECTION NOT IN $150 REPORT)
For EACH relevant court level in {state_info.get('name', 'NSW')}:
- Court name and jurisdiction
- Filing sequence with specific documents required at each stage
- Court registry details (address, phone, email where available)
- Deadlines for each filing step
- Extension-of-time route if deadlines have passed — specific provisions and what needs to be demonstrated
- What happens at each stage (directions hearing, callover, full hearing)
- Estimated timeframes from filing to hearing
- Costs considerations

## 16. HOW TO START YOUR APPEAL + REQUIRED FORMS (800+ words)
Step-by-step guide specific to {state_info.get('name', 'NSW')} with FULL DETAIL per step:
1. Obtain trial transcripts and exhibits — from which court registry, expected cost and timeframe
2. Identify and finalise grounds of appeal — how to narrow from identified grounds to filed grounds
3. Lodge Notice of Intention to Appeal — form name, deadline, where to lodge
4. Prepare detailed written submissions — structure, length, authorities
5. Serve documents on the Crown/DPP — who, where, method
6. Attend the appeal hearing — what to expect, who attends
Forms table: | Form/Document | Purpose | Where to Obtain | Filing Deadline |

## 17. SIMILAR CASE SEARCH OPTIONS (800+ words — NEW SECTION NOT IN $150 REPORT)
5+ tailored AustLII search queries specifically designed for this case:
For each query:
- The exact search string
- What it's designed to find
- Expected number of results and how to filter them
- Key cases to look for in results
- How to use the results to strengthen the appeal
Court-level filtering suggestions and keyword alternatives for each ground.

STOP after section 17."""),
                ("PASS 8/8", f"""

NOW GENERATE ONLY SECTIONS 18-20. Write 5000+ WORDS for this pass. Section 20 is the CLIENT BRIEF — it must be thorough and cover EVERY ground.

## 18. PRIORITISED ACTION PLAN (1000+ words)
72-hour actions (urgent — at least 6 specific actions):
For each: exact action, who to contact (name the office/registry), deadline, objective, what happens if missed.

7-day actions (important — at least 6 specific actions):
For each: exact action, resources needed, dependencies, expected outcome.

28-day actions (strategic — at least 6 specific actions):
For each: exact action, preparation steps, milestones, how this contributes to the appeal.

## 19. RISK ASSESSMENT + CONTINGENCY PLANNING (1200+ words — NEW SECTION NOT IN $150 REPORT)
For EACH of the {len(grounds)} grounds, write 150+ words covering:
- Probability of success (percentage range with reasoning)
- Main risk factor (what could go wrong?)
- Contingency if this ground fails (what's the backup?)
- Impact on overall appeal if this ground is excluded

Overall appeal risk assessment (500+ words):
- Best case scenario, likelihood, and path to get there
- Most likely outcome with realistic assessment
- Worst case scenario and mitigation strategy
- How grounds interact — if Ground 1 fails, does Ground 3 become stronger?
- Whether grounds should be argued independently or as a package

## 20. CLIENT PLAIN-ENGLISH BRIEF (2000+ words)
THIS IS THE FINAL SECTION. Write in plain, everyday English that explains the case in THIRD PERSON.

For EACH of the {len(grounds)} grounds individually:
- What this ground means in simple terms (2-3 sentences)
- Why it matters for the appeal (2-3 sentences)
- What the chances are (honest assessment)
- What happens if it succeeds (specific outcome)

Then cover:
- The overall appeal: what it is, why it's happening, and the realistic timeline
- Each possible outcome and what it means personally for the applicant
- Exactly what the applicant should do right now, this week, and this month
- What to expect at the hearing — how long, who's there, what happens
- Honest assessment of risks alongside the opportunities
- ABSOLUTE BAN: NEVER use "we", "us", "our", "you", "your". Use "the applicant", "the legal professional", "this analysis". WRONG: "The appeal is your opportunity." RIGHT: "The appeal represents an opportunity for the applicant."

Do NOT truncate. Write ALL content for all 3 sections."""),
            ]
            
            parts = []
            resume_from = 0
            if report_id:
                existing_report = await db.reports.find_one(
                    {"report_id": report_id},
                    {"_id": 0, "content.partial_analysis": 1, "content.passes_completed": 1},
                )
                existing_content = (existing_report or {}).get("content") or {}
                existing_partial = existing_content.get("partial_analysis") or ""
                existing_passes_completed = int(existing_content.get("passes_completed") or 0)
                if existing_partial and existing_passes_completed > 0:
                    parts = [existing_partial]
                    resume_from = min(existing_passes_completed, len(passes))
                    logger.info(f"Resuming extensive_log report {report_id} from pass {resume_from + 1}")

            for pass_index, (label, instruction) in enumerate(passes[resume_from:], start=resume_from + 1):
                pass_prompt = user_prompt + instruction
                logger.info(f"Extensive log {label} prompt size: system={len(system_prompt)}, user={len(pass_prompt)}")
                part = await _subprocess_llm(pass_prompt)
                parts.append(part)
                logger.info(f"Extensive log {label} response: {len(part)} chars")
                # Save partial progress after each pass so server restarts don't lose work
                partial_response = "\n\n".join(parts)
                await db.reports.update_one(
                    {"report_id": report_id},
                    {"$set": {"content.partial_analysis": partial_response, "content.passes_completed": pass_index}}
                )
            
            response = "\n\n".join(parts)
            logger.info(f"Extensive log combined: {len(response)} chars")

        else:
            logger.info(f"Report prompt size: system={len(system_prompt)}, user={len(user_prompt)}, total={len(system_prompt)+len(user_prompt)}")
            response = await _subprocess_llm(user_prompt)
    except Exception as e:
        last_error = e
        logger.error(f"Report generation failed: {e}")
    
    if response is None:
        logger.error(f"All report generation attempts failed: {last_error}")
        raise HTTPException(status_code=500, detail=f"AI report generation failed after retries: {str(last_error)}")

    anchor_terms = _build_anchor_terms(case, documents, timeline, grounds)
    response = _dedupe_report_content(response, report_type, anchor_terms)

    min_lengths = {
        "quick_summary": 9000,
        "full_detailed": 35000,
        "extensive_log": 120000
    }
    target_length = min_lengths.get(report_type, 12000)
    if aggressive_mode:
        target_length = int(target_length * 2.0)

    # Skip expansion for full_detailed and extensive_log — multi-pass already produces substantial content
    if len(response) < target_length and report_type not in ("extensive_log", "full_detailed"):
        try:
            expansion_prompt = f"""{case_context}

You must expand the report below to at least {target_length} characters. Keep ALL headings exactly as-is. Do NOT remove or rewrite any existing text — only ADD new paragraphs with case-specific details, dates, document references, and authorities. Avoid repetition. Maintain the tone of the report. If aggressive mode is on, keep the assertive advocacy style and add stronger authority chains.

REPORT TO EXPAND:
{response}
"""
            expanded = await _subprocess_llm(expansion_prompt)
            if expanded and len(expanded) > len(response):
                response = expanded
        except Exception as exc:
            logger.warning(f"Report expansion skipped: {exc}")

    response = _strip_report_placeholders(response)
    response = response.strip()

    # Preserve the actual grounds linked to the case so reports reflect the real ground count.
    grounds_of_merit = [
        {
            "ground_id": ground.get("ground_id"),
            "title": ground.get("title", "Untitled ground"),
            "description": ground.get("description", ""),
            "strength": ground.get("strength", "moderate"),
            "ground_type": ground.get("ground_type", "other"),
        }
        for ground in grounds
    ]
    
    if aggressive_mode:
        response += """

---

**IMPORTANT DISCLAIMER:** This report is for educational and research purposes only. It does not constitute legal advice. Always consult a qualified legal practitioner before taking any action.
"""

    return {
        "analysis": response,
        "grounds_of_merit": grounds_of_merit,
        "case_data": case,
        "document_count": len(documents),
        "event_count": len(timeline)
    }


BARRISTER_SOURCE_TYPES = ["quick_summary", "full_detailed", "extensive_log"]
BARRISTER_GENERATION_TIMEOUT_MINUTES = 40


def _coerce_utc_datetime(value):
    if isinstance(value, datetime):
        return value if value.tzinfo else value.replace(tzinfo=timezone.utc)
    if isinstance(value, str) and value:
        try:
            parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
            return parsed if parsed.tzinfo else parsed.replace(tzinfo=timezone.utc)
        except ValueError:
            return None
    return None


def _generated_at_sort_value(report: dict) -> str:
    return str(report.get("generated_at") or "")


async def _get_latest_standard_reports(case_id: str, user_id: str) -> List[dict]:
    reports = await db.reports.find(
        {
            "case_id": case_id,
            "user_id": user_id,
            "report_type": {"$in": BARRISTER_SOURCE_TYPES},
            "status": "completed",
            "content.aggressive_mode": {"$ne": True},
        },
        {"_id": 0},
    ).sort("generated_at", -1).to_list(50)

    latest_by_type = {}
    for report in reports:
        report_type = report.get("report_type")
        if report_type not in latest_by_type:
            latest_by_type[report_type] = report

    missing_types = [report_type for report_type in BARRISTER_SOURCE_TYPES if report_type not in latest_by_type]
    if missing_types:
        missing_labels = ", ".join(missing_types)
        raise HTTPException(status_code=409, detail=f"Barrister View remains locked until all 3 standard reports are completed. Missing: {missing_labels}")

    selected = [latest_by_type[report_type] for report_type in BARRISTER_SOURCE_TYPES]
    selected.sort(key=_generated_at_sort_value, reverse=True)
    return selected


def _build_barrister_source_signature(reports: List[dict]) -> str:
    ordered = sorted(
        reports,
        key=lambda report: BARRISTER_SOURCE_TYPES.index(report.get("report_type")) if report.get("report_type") in BARRISTER_SOURCE_TYPES else 99,
    )
    return "|".join(
        f"{report.get('report_type')}::{report.get('report_id')}::{report.get('generated_at')}"
        for report in ordered
    )


def _build_barrister_report_source_text(reports: List[dict]) -> str:
    type_labels = {
        "quick_summary": "Quick Summary",
        "full_detailed": "Full Detailed Report",
        "extensive_log": "Extensive Log Report",
    }
    blocks = []
    per_report_limit = 75000
    for report in sorted(
        reports,
        key=lambda item: BARRISTER_SOURCE_TYPES.index(item.get("report_type")) if item.get("report_type") in BARRISTER_SOURCE_TYPES else 99,
    ):
        analysis = _strip_report_placeholders((report.get("content") or {}).get("analysis", ""))
        analysis = re.sub(r"\n{3,}", "\n\n", analysis).strip()
        blocks.append(
            f"===== {type_labels.get(report.get('report_type'), report.get('report_type', 'Report'))} =====\n"
            f"Report ID: {report.get('report_id')}\n"
            f"Generated: {report.get('generated_at')}\n\n"
            f"{analysis[:per_report_limit]}"
        )
    return "\n\n".join(blocks)


def _trim_text_preserving_ends(text: str, max_chars: int) -> str:
    if not text or len(text) <= max_chars:
        return text
    head_chars = int(max_chars * 0.65)
    tail_chars = max_chars - head_chars
    return (
        text[:head_chars].rstrip()
        + "\n\n[Additional detailed source material omitted here for prompt length control]\n\n"
        + text[-tail_chars:].lstrip()
    )


def _build_barrister_group_source_text(reports: List[dict], max_chars_by_type: dict) -> str:
    type_labels = {
        "quick_summary": "Quick Summary",
        "full_detailed": "Full Detailed Report",
        "extensive_log": "Extensive Log Report",
    }
    blocks = []
    for report in sorted(
        reports,
        key=lambda item: BARRISTER_SOURCE_TYPES.index(item.get("report_type")) if item.get("report_type") in BARRISTER_SOURCE_TYPES else 99,
    ):
        report_type = report.get("report_type")
        analysis = _strip_report_placeholders((report.get("content") or {}).get("analysis", ""))
        analysis = re.sub(r"\n{3,}", "\n\n", analysis).strip()
        limited_analysis = _trim_text_preserving_ends(analysis, max_chars_by_type.get(report_type, 18000))
        blocks.append(
            f"===== {type_labels.get(report_type, report_type or 'Report')} =====\n"
            f"Report ID: {report.get('report_id')}\n"
            f"Generated: {report.get('generated_at')}\n\n"
            f"{limited_analysis}"
        )
    return "\n\n".join(blocks)


def _dedupe_barrister_ground_subsections(text: str) -> str:
    section_match = re.search(r"(## Grounds of Merit\n)([\s\S]*?)(?=\n## Statutory Framework)", text)
    if not section_match:
        return text

    grounds_body = section_match.group(2).strip()
    block_pattern = re.compile(r"(### Ground \d+: [^\n]+\n[\s\S]*?)(?=(?:\n### Ground \d+: )|\Z)")
    blocks = [block.strip() for block in block_pattern.findall(grounds_body)]
    if not blocks:
        return text

    deduped_blocks = []
    seen_titles = set()
    for block in blocks:
        heading = block.split("\n", 1)[0].strip()
        title_match = re.match(r"^### Ground \d+: (.+)$", heading)
        title = (title_match.group(1).strip().lower() if title_match else heading.lower())
        if title in seen_titles:
            continue
        seen_titles.add(title)
        deduped_blocks.append(block)

    renumbered_blocks = []
    for index, block in enumerate(deduped_blocks, start=1):
        heading, remainder = (block.split("\n", 1) + [""])[:2]
        title_match = re.match(r"^### Ground \d+: (.+)$", heading.strip())
        title = title_match.group(1).strip() if title_match else heading.replace("### ", "").strip()
        rebuilt = f"### Ground {index}: {title}"
        if remainder.strip():
            rebuilt += f"\n{remainder.strip()}"
        renumbered_blocks.append(rebuilt.strip())

    replacement = "\n\n".join(renumbered_blocks)
    return text[:section_match.start(2)] + replacement + text[section_match.end(2):]


def _normalise_barrister_table_titles(text: str) -> str:
    replacements = {
        "### Table: Comparative Authorities": "### Comparative Authorities Table",
        "### Table: Sentencing Comparison": "### Sentencing Comparison Table",
        "### Table: Evidentiary Pressure Points": "### Evidentiary Pressure Points Table",
        "### Table: Relief Pathways": "### Relief Pathways Matrix",
    }
    for source, target in replacements.items():
        text = text.replace(source, target)
    return text


async def generate_barrister_brief(case_id: str, user_id: str, report_id: str | None = None) -> dict:
    case = await db.cases.find_one({"case_id": case_id, "user_id": user_id}, {"_id": 0})
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")

    documents = await db.documents.find(
        {"case_id": case_id},
        {"_id": 0}
    ).to_list(300)
    timeline = await db.timeline_events.find({"case_id": case_id}, {"_id": 0}).sort("event_date", 1).to_list(400)
    grounds = await db.grounds_of_merit.find({"case_id": case_id}, {"_id": 0}).to_list(100)
    source_reports = await _get_latest_standard_reports(case_id, user_id)

    timeline_text = "\n".join(
        f"- {event.get('event_date', '')}: {event.get('title', '')} — {event.get('description', '')[:200]}"
        for event in timeline[:25]
    ) or "- No timeline events recorded"
    grounds_text = "\n".join(
        f"- {ground.get('title', 'Untitled ground')} [{ground.get('ground_type', 'other')} / {ground.get('strength', 'unrated')}] — {ground.get('description', '')[:220]}"
        for ground in grounds[:20]
    ) or "- No structured grounds recorded"
    grounds_heading_text = "\n".join(
        f"### Ground {idx}: {ground.get('title', 'Untitled ground')}"
        for idx, ground in enumerate(grounds[:20], start=1)
    ) or "### Ground 1: Grounds identified from source reports"
    documents_text = "\n".join(
        f"- {document.get('filename', 'Untitled document')} ({document.get('category', 'other')})"
        for document in documents[:30]
    ) or "- No documents uploaded"

    case_profile = f"""
CASE TITLE: {case.get('title', 'Unknown case')}
DEFENDANT: {case.get('defendant_name', 'Not recorded')}
CASE NUMBER: {case.get('case_number', 'Not recorded')}
COURT: {case.get('court', 'Not recorded')}
JURISDICTION: {(case.get('state') or 'nsw').upper()}
OFFENCE: {case.get('offence_type') or case.get('offence_category') or 'Not recorded'}
SENTENCE: {case.get('sentence', 'Not recorded')}
DOCUMENT COUNT: {len(documents)}
TIMELINE EVENT COUNT: {len(timeline)}
GROUNDS COUNT: {len(grounds)}
""".strip()

    system_prompt = """You are a senior Australian criminal appeal barrister preparing a polished barrister brief for a criminal appeal matter. The output must read like one coherent legal document written by a careful appellate specialist.

MANDATORY RULES:
- Australian English only.
- Strict third-person educational tone only.
- Never use first-person or second-person language, including: we, us, our, you, your.
- Do not mention that reports were merged, combined, synthesised, tiered, paid, unlocked, or generated by AI.
- Do not include bullet-heavy exposition. Detailed reasoning must be written in flowing paragraphs.
- Minimal bullet points are permitted only for short authority lists, procedural checklists, or document inventories where compact presentation improves clarity.
- No duplication. If the same issue appears across multiple source reports, discuss it once in the most logical section.
- No placeholders, meta-commentary, drafting notes, or future-tense filler such as 'will be provided'.
- If the materials are uncertain on a point, say that the available materials indicate or suggest the point rather than asserting unsupported fact.
- Use markdown headings only, with ## for main sections and ### for sub-sections.
- Write a professional barrister-ready brief with strong structure, clean transitions, and substantial case-specific detail.
- This must be materially more detailed than a summary. It must preserve the strongest factual analysis, legal reasoning, statutory interpretation, sentencing comparison, and strategic detail from the source reports.
- The brief must clearly synthesise all 3 source reports as 3 distinct source analyses before building the integrated counsel brief. Each source report's unique contribution must be identified so the final brief does not recycle the same point over and over.
- The brief is for counsel. Avoid consumer-style explanation and avoid shrinking the material into a simplified note.
- Each section must be dense, specific, and useful to counsel. Generic high-level summaries are unacceptable.
"""

    shared_context = f"""CASE PROFILE
{case_profile}

STRUCTURED GROUNDS
{grounds_text}

MANDATORY GROUND LIST
{grounds_heading_text}

TIMELINE SNAPSHOT
{timeline_text}

DOCUMENT INVENTORY
{documents_text}
"""

    section_groups = [
        {
            "slug": "source-synthesis",
            "target_chars": 22000,
            "source_limits": {"quick_summary": 14000, "full_detailed": 24000, "extensive_log": 32000},
            "required_headings": [
                "## Executive Overview for Counsel",
                "## Source Report Synthesis",
                "## Case Background and Procedural History",
                "## Conviction, Offence and Sentence Analysis",
            ],
            "instructions": "Write these sections in full depth. Under ## Source Report Synthesis, create exactly these three sub-headings in this order: ### Quick Summary Synthesis, ### Full Detailed Report Synthesis, ### Extensive Log Synthesis. Under each sub-heading, identify what that source report contributes that is unique, critical, or more developed than the others. Do not repeat the same point in all 3 sub-sections. Set out the procedural history carefully and explain the conviction and sentence context at counsel depth.",
        },
        {
            "slug": "case-analysis",
            "target_chars": 26000,
            "source_limits": {"quick_summary": 11000, "full_detailed": 28000, "extensive_log": 36000},
            "required_headings": [
                "## Evidentiary Tensions and Appeal Pressure Points",
                "## Grounds of Merit",
                "## Statutory Framework and Governing Tests",
                "## Authorities and Comparative Cases",
            ],
            "instructions": "Write these sections at barrister depth. Under ## Grounds of Merit, create one dedicated ### subsection for every item in the mandatory ground list and do not omit, merge, or collapse any listed ground. Each ground must be explained with substantial factual support, legal reasoning, weaknesses, strengths, fallback positions, strategic implications, and why counsel should care about it in conference and written submissions. The authorities section must meaningfully compare cases and explain why they matter, including a markdown comparative authorities table where useful. Under ## Evidentiary Tensions and Appeal Pressure Points, identify contradictions, missing links, procedural fractures, and anything that intensifies appellate pressure without repeating the same sentence structure.",
        },
        {
            "slug": "strategy",
            "target_chars": 24000,
            "source_limits": {"quick_summary": 8000, "full_detailed": 22000, "extensive_log": 32000},
            "required_headings": [
                "## Sentencing Comparison and Relief Pathways",
                "## Proposed Submissions and Hearing Strategy",
                "## Conference Questions, Filing Priorities and Risks",
                "## Final Barrister Briefing Note",
            ],
            "instructions": "Write these sections as a serious counsel-facing strategy brief. Include detailed proposed submission themes, hearing structure, fallback positions, risk analysis, filing priorities, conference questions for counsel, and a closing barrister briefing note that is still detailed rather than compressed. Do not shorten the analysis into generic advice.",
        },
    ]

    section_outputs = []
    resume_index = 0
    if report_id:
        existing_report = await db.reports.find_one(
            {"report_id": report_id},
            {"_id": 0, "content.partial_sections": 1, "content.partial_stage": 1, "content.partial_analysis": 1},
        )
        existing_content = (existing_report or {}).get("content") or {}
        saved_sections = existing_content.get("partial_sections") or []
        if saved_sections:
            section_outputs = list(saved_sections)
            resume_index = min(len(section_outputs), len(section_groups))
            logger.info(f"Resuming barrister brief {report_id} from group {resume_index + 1}")

    for group_index, group in enumerate(section_groups[resume_index:], start=resume_index + 1):
        headings_text = "\n".join(group["required_headings"])
        group_source_text = _build_barrister_group_source_text(source_reports, group["source_limits"])
        group_prompt = f"""Prepare only the following Barrister Brief sections, using the exact headings below and in the exact order:

{headings_text}

Depth requirements:
- Minimum target length for this response: {group['target_chars']} characters.
- Preserve as much useful detail as possible from the source reports.
- Use flowing paragraphs with concrete facts, authorities, procedural detail, and strategy.
- Avoid generic summary language.
- Do not repeat material unless needed for legal continuity.

Specific drafting instruction:
{group['instructions']}

{shared_context}

SOURCE REPORTS
{group_source_text}
"""

        group_response = await call_llm_with_fallback(
            system_prompt,
            group_prompt,
            session_id=f"barrister-{case_id}-{group['slug']}",
            max_tokens=14000,
            timeout_seconds=240,
        )
        group_response = _strip_report_placeholders(group_response)
        group_response = re.sub(r"\n{3,}", "\n\n", group_response).strip()
        section_outputs.append(group_response)
        if report_id:
            partial_analysis = "\n\n".join(part for part in section_outputs if part).strip()
            await db.reports.update_one(
                {"report_id": report_id},
                {"$set": {
                    "content.partial_sections": section_outputs,
                    "content.partial_stage": group.get("slug"),
                    "content.partial_analysis": partial_analysis,
                    "generated_at": datetime.now(timezone.utc).isoformat(),
                }}
            )

    response = "\n\n".join(part for part in section_outputs if part).strip()

    target_length = 90000
    if len(response) < target_length:
        expansion_source_text = _build_barrister_group_source_text(
            source_reports,
            {"quick_summary": 8000, "full_detailed": 22000, "extensive_log": 26000},
        )
        expansion_prompt = f"""Expand the Barrister Brief below to at least {target_length} characters.

Keep every existing heading exactly as written.
Do not remove or shorten any existing material.
Add more factual depth, procedural detail, case-specific analysis, statutory interpretation, authority comparison, sentencing detail, and hearing strategy under the existing sections only.
The result must read like a deeply detailed barrister brief, not a summary.
Every ground in the mandatory ground list must remain in the final text with its own dedicated discussion.
Under ## Source Report Synthesis, deepen each of the 3 report sub-sections with further unique material rather than rephrasing the same content.

MANDATORY GROUND LIST
{grounds_heading_text}

SOURCE REPORTS
{expansion_source_text}

CURRENT BARRISTER BRIEF
{response}
"""
        try:
            expanded_response = await call_llm_with_fallback(
                system_prompt,
                expansion_prompt,
                session_id=f"barrister-{case_id}-expand",
                max_tokens=16384,
                timeout_seconds=240,
            )
            expanded_response = _strip_report_placeholders(expanded_response)
            expanded_response = re.sub(r"\n{3,}", "\n\n", expanded_response).strip()
            if len(expanded_response) > len(response):
                response = expanded_response
        except Exception as exc:
            logger.warning(f"Barrister whole-brief expansion skipped for {case_id}: {exc}")

    if len(response) < 75000 and grounds:
        ground_expansion_prompt = f"""Rewrite only the ## Grounds of Merit section of the Barrister Brief below.

Requirements:
- Keep the heading exactly as ## Grounds of Merit.
- Include every ground from the mandatory ground list below.
- Create one dedicated ### subsection per listed ground.
- Make this rewritten grounds section extremely detailed, with factual support, legal reasoning, strategic use, weaknesses, fallback positions, and any key authority or statutory link relevant to that ground.
- Minimum target length for this rewritten section alone: 26000 characters.

MANDATORY GROUND LIST
{grounds_heading_text}

STRUCTURED GROUNDS
{grounds_text}

SOURCE REPORTS
{expansion_source_text}

CURRENT BARRISTER BRIEF
{response}
"""
        try:
            rewritten_grounds = await call_llm_with_fallback(
                system_prompt,
                ground_expansion_prompt,
                session_id=f"barrister-{case_id}-grounds-expand",
                max_tokens=16384,
                timeout_seconds=240,
            )
            rewritten_grounds = _strip_report_placeholders(rewritten_grounds)
            rewritten_grounds = re.sub(r"\n{3,}", "\n\n", rewritten_grounds).strip()
            if rewritten_grounds.startswith("## Grounds of Merit"):
                response = re.sub(
                    r"## Grounds of Merit\n[\s\S]*?(?=\n## Statutory Framework and Governing Tests)",
                    rewritten_grounds + "\n\n",
                    response,
                    count=1,
                )
        except Exception as exc:
            logger.warning(f"Barrister grounds expansion skipped for {case_id}: {exc}")

    if len(response) < 70000:
        cross_analysis_prompt = f"""Produce only the following sections, in this exact order:

## Report-to-Report Cross-Analysis
## Document and Evidence Deployment for Counsel

Requirements:
- Minimum target length for this response: 22000 characters.
- Use all 3 source reports and identify where they overlap, where they diverge, and what unique critical material each one contributes.
- Do not recycle the same paragraph 3 times. Organise the material by issue and explain which source report adds what.
- Under ## Document and Evidence Deployment for Counsel, explain how specific documents, witnesses, chronology items, psychiatric material, media material, and procedural incidents should be deployed by counsel in conference, written submissions, and oral argument.
- This must be dense, counsel-facing, and case-specific.

SOURCE REPORTS
{expansion_source_text}

CURRENT BARRISTER BRIEF
{response}
"""
        try:
            cross_analysis = await call_llm_with_fallback(
                system_prompt,
                cross_analysis_prompt,
                session_id=f"barrister-{case_id}-cross-analysis",
                max_tokens=16384,
                timeout_seconds=240,
            )
            cross_analysis = _strip_report_placeholders(cross_analysis)
            cross_analysis = re.sub(r"\n{3,}", "\n\n", cross_analysis).strip()
            if cross_analysis.startswith("## Report-to-Report Cross-Analysis"):
                response = response.rstrip() + "\n\n" + cross_analysis
        except Exception as exc:
            logger.warning(f"Barrister cross-analysis expansion skipped for {case_id}: {exc}")

    if len(response) < 85000:
        strategy_expansion_prompt = f"""Rewrite only the following sections of the Barrister Brief below, keeping the same headings and making them substantially more detailed:

## Proposed Submissions and Hearing Strategy
## Conference Questions, Filing Priorities and Risks
## Final Barrister Briefing Note

Requirements:
- Minimum target length for this rewritten block alone: 24000 characters.
- Expand the oral and written submissions structure greatly.
- Include issue sequencing, fallback positions, framing choices, evidentiary use, likely resistance points, answer lines, and conference questions for counsel.
- The rewritten material must read like a serious barrister working brief, not a summary.
- Avoid repeating the same sentence structure or generic observations.

SOURCE REPORTS
{expansion_source_text}

CURRENT BARRISTER BRIEF
{response}
"""
        try:
            rewritten_strategy = await call_llm_with_fallback(
                system_prompt,
                strategy_expansion_prompt,
                session_id=f"barrister-{case_id}-strategy-expand",
                max_tokens=16384,
                timeout_seconds=240,
            )
            rewritten_strategy = _strip_report_placeholders(rewritten_strategy)
            rewritten_strategy = re.sub(r"\n{3,}", "\n\n", rewritten_strategy).strip()
            if rewritten_strategy.startswith("## Proposed Submissions and Hearing Strategy"):
                response = re.sub(
                    r"## Proposed Submissions and Hearing Strategy\n[\s\S]*$",
                    rewritten_strategy,
                    response,
                    count=1,
                )
        except Exception as exc:
            logger.warning(f"Barrister strategy expansion skipped for {case_id}: {exc}")

    try:
        comparison_tables_prompt = f"""Produce only the following markdown blocks, in this exact order, with no introduction or conclusion:

### Evidentiary Pressure Points Table
Create a markdown table with columns: Issue | Supporting Material | Why it matters on appeal | Vulnerability in the prosecution case

### Comparative Authorities Table
Create a markdown table with columns: Authority | Principle | Relevance to this case | Strategic use in submissions

### Sentencing Comparison Table
Create a markdown table with columns: Comparator | Key facts | Sentence outcome | Relevance to this appeal

### Relief Pathways Matrix
Create a markdown table with columns: Relief pathway | Legal basis | Best supporting features | Main risk or limitation

Requirements:
- Use all 3 source reports and the current barrister brief.
- Make the rows detailed and case-specific.
- Do not repeat the main narrative prose.
- Output only the 4 titled blocks above.

SOURCE REPORTS
{expansion_source_text}

CURRENT BARRISTER BRIEF
{response}
"""
        comparison_tables = await call_llm_with_fallback(
            system_prompt,
            comparison_tables_prompt,
            session_id=f"barrister-{case_id}-comparison-tables",
            max_tokens=12000,
            timeout_seconds=240,
        )
        comparison_tables = _strip_report_placeholders(comparison_tables)
        comparison_tables = re.sub(r"\n{3,}", "\n\n", comparison_tables).strip()

        evidence_table_match = re.search(
            r"(### Evidentiary Pressure Points Table[\s\S]*?)(?=\n### Comparative Authorities Table|$)",
            comparison_tables,
        )
        authorities_table_match = re.search(
            r"(### Comparative Authorities Table[\s\S]*?)(?=\n### Sentencing Comparison Table|$)",
            comparison_tables,
        )
        sentencing_table_match = re.search(
            r"(### Sentencing Comparison Table[\s\S]*?)(?=\n### Relief Pathways Matrix|$)",
            comparison_tables,
        )
        relief_table_match = re.search(r"(### Relief Pathways Matrix[\s\S]*)$", comparison_tables)

        if evidence_table_match and "### Evidentiary Pressure Points Table" not in response:
            response = re.sub(
                r"(## Evidentiary Tensions and Appeal Pressure Points\n[\s\S]*?)(?=\n## Grounds of Merit)",
                lambda match: match.group(1).rstrip() + "\n\n" + evidence_table_match.group(1).strip() + "\n\n",
                response,
                count=1,
            )

        if authorities_table_match and "### Comparative Authorities Table" not in response:
            response = re.sub(
                r"(## Authorities and Comparative Cases\n[\s\S]*?)(?=\n## Sentencing Comparison and Relief Pathways)",
                lambda match: match.group(1).rstrip() + "\n\n" + authorities_table_match.group(1).strip() + "\n\n",
                response,
                count=1,
            )

        sentencing_blocks = []
        if sentencing_table_match and "### Sentencing Comparison Table" not in response:
            sentencing_blocks.append(sentencing_table_match.group(1).strip())
        if relief_table_match and "### Relief Pathways Matrix" not in response:
            sentencing_blocks.append(relief_table_match.group(1).strip())
        if sentencing_blocks:
            response = re.sub(
                r"(## Sentencing Comparison and Relief Pathways\n[\s\S]*?)(?=\n## Proposed Submissions and Hearing Strategy)",
                lambda match: match.group(1).rstrip() + "\n\n" + "\n\n".join(sentencing_blocks) + "\n\n",
                response,
                count=1,
            )
    except Exception as exc:
        logger.warning(f"Barrister comparison table enrichment skipped for {case_id}: {exc}")

    response = _strip_report_placeholders(response)
    response = _normalise_barrister_table_titles(response)
    response = _dedupe_barrister_ground_subsections(response)
    response = re.sub(r"\n{3,}", "\n\n", response).strip()

    return {
        "analysis": response,
        "case_data": case,
        "document_count": len(documents),
        "event_count": len(timeline),
        "grounds_of_merit": grounds,
        "source_reports": [
            {
                "report_id": report.get("report_id"),
                "report_type": report.get("report_type"),
                "title": report.get("title"),
                "generated_at": report.get("generated_at"),
            }
            for report in source_reports
        ],
        "source_signature": _build_barrister_source_signature(source_reports),
    }


async def _run_barrister_report_generation(report_id: str, case_id: str, user_id: str):
    try:
        analysis_result = await generate_barrister_brief(case_id, user_id, report_id=report_id)
        await db.reports.update_one(
            {"report_id": report_id},
            {
                "$set": {
                    "status": "completed",
                    "title": "Barrister Brief",
                    "content": {
                        "analysis": analysis_result["analysis"],
                        "case_title": analysis_result["case_data"].get("title", ""),
                        "defendant": analysis_result["case_data"].get("defendant_name", ""),
                        "document_count": analysis_result["document_count"],
                        "event_count": analysis_result["event_count"],
                        "source_signature": analysis_result["source_signature"],
                        "source_reports": analysis_result["source_reports"],
                        "aggressive_mode": False,
                        "partial_sections": [],
                        "partial_stage": None,
                        "partial_analysis": "",
                    },
                    "grounds_of_merit": analysis_result["grounds_of_merit"],
                    "error": None,
                    "technical_error": None,
                }
            },
        )
        logger.info(f"Barrister brief {report_id} generated successfully")
    except Exception as exc:
        logger.error(f"Barrister brief {report_id} generation failed: {exc}")
        friendly_error = "Barrister brief generation was interrupted by a temporary AI service error. Please generate again."
        await db.reports.update_one(
            {"report_id": report_id},
            {"$set": {"status": "failed", "error": friendly_error, "technical_error": str(exc)}},
        )

async def _run_report_generation(report_id: str, case_id: str, user_id: str, report_type: str, aggressive_mode: bool):
    """Background task that generates the AI report and updates the DB record."""
    try:
        report_titles = {
            "quick_summary": "Quick Case Summary",
            "full_detailed": "Full Detailed Legal Analysis",
            "extensive_log": "Extensive Case Log & Analysis"
        }
        analysis_result = await analyze_case_with_ai(case_id, user_id, report_type, aggressive_mode, report_id=report_id)
        title = report_titles.get(report_type, "Report")
        if aggressive_mode:
            title = f"{title} (Aggressive)"
        await db.reports.update_one(
            {"report_id": report_id},
            {"$set": {
                "status": "completed",
                "title": title,
                "content": {
                    "analysis": analysis_result["analysis"],
                    "case_title": analysis_result["case_data"].get("title", ""),
                    "defendant": analysis_result["case_data"].get("defendant_name", ""),
                    "document_count": analysis_result["document_count"],
                    "event_count": analysis_result["event_count"],
                    "aggressive_mode": aggressive_mode
                },
                "grounds_of_merit": analysis_result["grounds_of_merit"],
            }}
        )
        logger.info(f"Report {report_id} generated successfully")
    except Exception as exc:
        logger.error(f"Report {report_id} generation failed: {exc}")
        friendly_error = "Report generation was interrupted by a temporary AI service error. Retry resumes from the last completed section."
        await db.reports.update_one(
            {"report_id": report_id},
            {"$set": {"status": "failed", "error": friendly_error, "technical_error": str(exc)}}
        )


@api_router.post("/cases/{case_id}/reports/generate", response_model=dict)
async def generate_report(case_id: str, report_request: ReportRequest, request: Request):
    """Generate an AI-powered report for a case (background task)"""
    user = await get_current_user(request)
    report_type = report_request.report_type
    
    if report_type not in ["quick_summary", "full_detailed", "extensive_log"]:
        raise HTTPException(status_code=400, detail="Invalid report type")
    
    # Check payment for premium reports (admin bypasses all payments)
    is_admin = is_admin_user(user.email)
    
    if report_type == "full_detailed" and not is_admin:
        payment = await db.payments.find_one({
            "case_id": case_id,
            "user_id": user.user_id,
            "feature_type": {"$in": feature_type_variants("full_report")},
            "status": "completed"
        })
        if not payment:
            raise HTTPException(
                status_code=402, 
                detail={
                    "message": "Payment required for Full Detailed Report",
                    "feature_type": "full_report",
                    "price": FEATURE_PRICES["full_report"]["price"],
                    "currency": "AUD"
                }
            )
    
    if report_type == "extensive_log" and not is_admin:
        payment = await db.payments.find_one({
            "case_id": case_id,
            "user_id": user.user_id,
            "feature_type": {"$in": feature_type_variants("extensive_report")},
            "status": "completed"
        })
        if not payment:
            raise HTTPException(
                status_code=402, 
                detail={
                    "message": "Payment required for Extensive Log Report",
                    "feature_type": "extensive_report",
                    "price": FEATURE_PRICES["extensive_report"]["price"],
                    "currency": "AUD"
                }
            )
    
    existing_failed = await db.reports.find(
        {
            "case_id": case_id,
            "user_id": user.user_id,
            "report_type": report_type,
            "status": "failed",
            "content.aggressive_mode": {"$ne": True},
        },
        {"_id": 0},
    ).sort("generated_at", -1).to_list(1)

    if existing_failed:
        resumed_report = existing_failed[0]
        await db.reports.update_one(
            {"report_id": resumed_report["report_id"]},
            {"$set": {"status": "generating", "error": None, "generated_at": datetime.now(timezone.utc).isoformat()}},
        )
        asyncio.create_task(
            _run_report_generation(resumed_report["report_id"], case_id, user.user_id, report_type, False)
        )
        resumed_report["status"] = "generating"
        resumed_report["error"] = None
        return resumed_report

    # Create a placeholder report with "generating" status and return immediately
    report_id = f"rpt_{uuid.uuid4().hex[:12]}"
    report_titles = {
        "quick_summary": "Quick Case Summary",
        "full_detailed": "Full Detailed Legal Analysis",
        "extensive_log": "Extensive Case Log & Analysis"
    }
    aggressive_mode = False
    title = report_titles.get(report_type, "Report")
    placeholder = {
        "report_id": report_id,
        "case_id": case_id,
        "user_id": user.user_id,
        "report_type": report_type,
        "title": title,
        "content": {"analysis": "", "aggressive_mode": aggressive_mode},
        "grounds_of_merit": [],
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "status": "generating",
    }
    insert_doc = {k: v for k, v in placeholder.items()}
    await db.reports.insert_one(insert_doc)

    # Fire-and-forget background task
    asyncio.create_task(
        _run_report_generation(report_id, case_id, user.user_id, report_type, aggressive_mode)
    )

    return placeholder


@api_router.get("/cases/{case_id}/reports/{report_id}/status")
async def get_report_status(case_id: str, report_id: str, request: Request):
    """Poll endpoint for report generation status"""
    user = await get_current_user(request)
    report = await db.reports.find_one(
        {"report_id": report_id, "case_id": case_id, "user_id": user.user_id},
        {"_id": 0, "report_id": 1, "status": 1, "error": 1}
    )
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    return {"report_id": report_id, "status": report.get("status", "completed")}

@api_router.get("/cases/{case_id}/reports", response_model=List[dict])
async def get_reports(case_id: str, request: Request):
    """Get all reports for a case"""
    user = await get_current_user(request)
    
    # Auto-fail any report stuck in "generating" for more than 60 minutes
    thirty_min_ago = (datetime.now(timezone.utc) - timedelta(minutes=60)).isoformat()
    await db.reports.update_many(
        {"case_id": case_id, "user_id": user.user_id, "status": "generating", "generated_at": {"$lt": thirty_min_ago}},
        {"$set": {"status": "failed", "error": "Generation timed out"}}
    )
    
    reports = await db.reports.find(
        {
            "case_id": case_id,
            "user_id": user.user_id,
            "content.aggressive_mode": {"$ne": True},
            "report_type": {"$ne": "barrister_view"},
        },
        {"_id": 0}
    ).sort("generated_at", -1).to_list(100)
    
    return reports


@api_router.get("/cases/{case_id}/reports/barrister-view", response_model=dict)
async def get_or_generate_barrister_view(case_id: str, request: Request, regenerate: bool = False):
    """Return the current barrister brief or start a fresh synthesis when required."""
    user = await get_current_user(request)
    source_reports = await _get_latest_standard_reports(case_id, user.user_id)
    source_signature = _build_barrister_source_signature(source_reports)

    existing_reports = await db.reports.find(
        {
            "case_id": case_id,
            "user_id": user.user_id,
            "report_type": "barrister_view",
            "content.source_signature": source_signature,
        },
        {"_id": 0},
    ).sort("generated_at", -1).to_list(10)

    current_report = existing_reports[0] if existing_reports else None
    if current_report and not regenerate:
        current_status = current_report.get("status")
        if current_status == "completed":
            current_analysis = ((current_report.get("content") or {}).get("analysis") or "").strip()
            if len(current_analysis) < 4000:
                await db.reports.update_one(
                    {"report_id": current_report.get("report_id")},
                    {"$set": {"status": "generating", "error": None, "generated_at": datetime.now(timezone.utc).isoformat()}},
                )
                current_report["status"] = "generating"
                current_report["error"] = None
                asyncio.create_task(_run_barrister_report_generation(current_report.get("report_id"), case_id, user.user_id))
                return current_report
            return current_report
        if current_status == "failed":
            temporary_error = str(current_report.get("technical_error") or current_report.get("error") or "")
            if re.search(r"502|BadGateway|OpenAIException|temporary AI service error|timed out", temporary_error, re.I):
                await db.reports.update_one(
                    {"report_id": current_report.get("report_id")},
                    {"$set": {"status": "generating", "error": None, "generated_at": datetime.now(timezone.utc).isoformat()}},
                )
                current_report["status"] = "generating"
                current_report["error"] = None
                asyncio.create_task(_run_barrister_report_generation(current_report.get("report_id"), case_id, user.user_id))
                return current_report
            return current_report
        if current_status == "generating":
            generated_at = _coerce_utc_datetime(current_report.get("generated_at"))
            stale_cutoff = datetime.now(timezone.utc) - timedelta(minutes=BARRISTER_GENERATION_TIMEOUT_MINUTES)
            if generated_at and generated_at >= stale_cutoff:
                return current_report

            timeout_message = "Barrister brief generation timed out. Please generate again."
            await db.reports.update_one(
                {"report_id": current_report.get("report_id")},
                {"$set": {"status": "failed", "error": timeout_message, "technical_error": timeout_message}},
            )
            await db.reports.update_one(
                {"report_id": current_report.get("report_id")},
                {"$set": {"status": "generating", "error": None, "generated_at": datetime.now(timezone.utc).isoformat()}},
            )
            current_report["status"] = "generating"
            current_report["error"] = None
            asyncio.create_task(_run_barrister_report_generation(current_report.get("report_id"), case_id, user.user_id))
            return current_report

    report_id = f"rpt_{uuid.uuid4().hex[:12]}"
    placeholder = {
        "report_id": report_id,
        "case_id": case_id,
        "user_id": user.user_id,
        "report_type": "barrister_view",
        "title": "Barrister Brief",
        "content": {
            "analysis": "",
            "document_count": len(source_reports),
            "event_count": 0,
            "source_signature": source_signature,
            "source_reports": [
                {
                    "report_id": report.get("report_id"),
                    "report_type": report.get("report_type"),
                    "title": report.get("title"),
                    "generated_at": report.get("generated_at"),
                }
                for report in source_reports
            ],
            "aggressive_mode": False,
        },
        "grounds_of_merit": [],
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "status": "generating",
    }
    await db.reports.insert_one({k: v for k, v in placeholder.items()})

    asyncio.create_task(_run_barrister_report_generation(report_id, case_id, user.user_id))
    return placeholder


@api_router.get("/reports/embedded-legacy", response_model=dict)
async def get_embedded_legacy_reports(request: Request, limit: int = 3):
    """Return strongest historical reports for embedding/reference in UI."""
    user = await get_current_user(request)

    all_reports = await db.reports.find(
        {"user_id": user.user_id},
        {
            "_id": 0,
            "report_id": 1,
            "case_id": 1,
            "report_type": 1,
            "title": 1,
            "generated_at": 1,
            "content.analysis": 1,
        },
    ).sort("generated_at", -1).to_list(400)

    def analysis_len(item: dict) -> int:
        return len((item.get("content") or {}).get("analysis", ""))

    valid_types = ["quick_summary", "full_detailed", "extensive_log"]
    by_length = [r for r in all_reports if r.get("report_type") in valid_types and analysis_len(r) > 1200]
    by_length.sort(key=analysis_len, reverse=True)

    selected = []
    seen_types = set()

    for report in by_length:
        rtype = report.get("report_type")
        if rtype in seen_types:
            continue
        seen_types.add(rtype)
        selected.append(report)
        if len(selected) >= limit:
            break

    if len(selected) < limit:
        selected_ids = {r.get("report_id") for r in selected}
        for report in by_length:
            if report.get("report_id") in selected_ids:
                continue
            selected.append(report)
            if len(selected) >= limit:
                break

    embedded = []
    for report in selected[:limit]:
        analysis = (report.get("content") or {}).get("analysis", "")
        embedded.append(
            {
                "report_id": report.get("report_id"),
                "case_id": report.get("case_id"),
                "report_type": report.get("report_type"),
                "title": report.get("title"),
                "generated_at": report.get("generated_at"),
                "analysis": analysis,
                "analysis_length": len(analysis),
            }
        )

    return {"reports": embedded}

@api_router.get("/cases/{case_id}/reports/{report_id}", response_model=dict)
async def get_report(case_id: str, report_id: str, request: Request):
    """Get a specific report"""
    user = await get_current_user(request)
    
    report = await db.reports.find_one(
        {"report_id": report_id, "case_id": case_id, "user_id": user.user_id},
        {"_id": 0}
    )
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    
    return report

@api_router.delete("/cases/{case_id}/reports/{report_id}")
async def delete_report(case_id: str, report_id: str, request: Request):
    """Delete a report"""
    user = await get_current_user(request)
    
    result = await db.reports.delete_one({
        "report_id": report_id,
        "case_id": case_id,
        "user_id": user.user_id
    })
    
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Report not found")
    
    return {"message": "Report deleted"}

# ============ PDF EXPORT ============

def _format_export_display_date(value=None) -> str:
    parsed = _coerce_utc_datetime(value)
    if not parsed:
        parsed = datetime.now(timezone.utc)
    return parsed.astimezone(timezone.utc).strftime("%d/%m/%Y")


def _build_export_footer_label(case: dict, report_label: str, generated_at=None) -> str:
    appellant_name = (case.get("defendant_name") or case.get("title") or "Appellant").strip()
    report_name = (report_label or "Legal Report").strip()
    return f"Criminal Appeal Case Management - {report_name} on {appellant_name} - {_format_export_display_date(generated_at)}"


def _build_export_footer_message() -> str:
    return "Created and Designed by Deb King — Thank you for using the tool. Good luck with the appeal process."


def _truncate_export_footer(text: str, max_chars: int = 118) -> str:
    value = (text or "").strip()
    if len(value) <= max_chars:
        return value
    return value[: max_chars - 1].rstrip() + "…"


def _clean_sentence_candidate(value: str) -> str:
    cleaned = (value or "")
    cleaned = re.sub(r"\s*\[.*$", "", cleaned)
    cleaned = re.sub(r"\s*\(https?:.*$", "", cleaned)
    cleaned = re.sub(r"\s*[|•].*$", "", cleaned)
    cleaned = re.sub(r"[,;:]?\s*(?:appeal|conviction|leave|outcome)\b.*$", "", cleaned, flags=re.I)
    cleaned = re.sub(r"[,;:]?\s*(?:dismissed|upheld|refused|granted)\b.*$", "", cleaned, flags=re.I)
    return re.sub(r"\s+", " ", cleaned).strip()


def _is_valid_sentence_candidate(value: str) -> bool:
    if not value:
        return False
    if not re.search(r"(life|year|month|non[- ]?parole|imprisonment|gaol|custody|sentence)", value, re.I):
        return False
    if re.search(r"\b(reduced|reduce|precedent|appeal|submissions|could|should|potentially|perhaps|would|adequacy|seek|sought|relief)\b", value, re.I):
        return False
    return len(value) < 140


def _extract_sentence_from_text(case: dict, analysis: str) -> str:
    if case.get('sentence') and str(case.get('sentence')).strip():
        return str(case.get('sentence')).strip()
    patterns = [
        r"(?:sentence\s+imposed\s+was|sentence\s+was|head\s+sentence\s+was|head\s+sentence:|sentenced?\s+to)\s+([^\.\n]{8,160})",
        r"(\d+\s+years?'?\s+with\s+a\s+non[- ]?parole\s+period\s+of\s+\d+\s+years?(?:\s+and\s+\d+\s+months?)?)",
        r"(\d+\s+years?'?(?:\s+and\s+\d+\s+months?)?\s*(?:imprisonment|gaol|jail|custody)?\s*(?:with\s+(?:a\s+)?non[- ]?parole\s+period\s+of\s+\d+\s+years?(?:\s+and\s+\d+\s+months?)?)?)",
        r"(?:was\s+)?sentenced?\s+to\s+(\d+\s*(?:years?|months?)\s+(?:and\s+\d+\s*(?:years?|months?)\s+)?(?:imprisonment|gaol|jail|custody)[^\n\.]{0,80})",
        r"(?:^|\n)\s*(?:Head\s+)?Sentence\s*:\s*(\d+[^\n]{5,100})",
        r"(?:sentenced?\s+to\s+)?(life\s+imprisonment|imprisonment\s+for\s+life|life\s+sentence)[^\n\.]{0,60}",
        r"(\d+[\s-]*(?:years?|months?)(?:'s?)?\s*(?:imprisonment|gaol|jail|custody|sentence|non[- ]?parole)[^\n\.]{0,80})",
        r"sentence\s+of\s+(\d+[^\n\.]{5,80})",
        r"((?:minimum|non[- ]?parole)\s+(?:period\s+)?of\s+\d+[^\n\.]{3,60})",
    ]
    for pattern in patterns:
        match = re.search(pattern, analysis or "", re.I | re.M)
        if match:
            candidate = _clean_sentence_candidate(match.group(1))
            if _is_valid_sentence_candidate(candidate):
                return candidate
    return "See report analysis"


async def _derive_export_sentence(case: dict, case_id: str, user_id: str, fallback_report: dict | None = None) -> str:
    standard_reports = await db.reports.find(
        {
            "case_id": case_id,
            "user_id": user_id,
            "report_type": {"$in": ["quick_summary", "full_detailed", "extensive_log", "barrister_view"]},
            "status": "completed",
        },
        {"_id": 0},
    ).sort("generated_at", -1).to_list(20)

    for report_type in ["quick_summary", "full_detailed", "extensive_log", "barrister_view"]:
        for item in [r for r in standard_reports if r.get("report_type") == report_type]:
            candidate = _extract_sentence_from_text(case, ((item.get("content") or {}).get("analysis") or ""))
            if candidate != "See report analysis":
                return candidate

    if fallback_report:
        candidate = _extract_sentence_from_text(case, ((fallback_report.get("content") or {}).get("analysis") or ""))
        if candidate != "See report analysis":
            return candidate

    return _extract_sentence_from_text(case, "")

@api_router.get("/cases/{case_id}/reports/{report_id}/export-pdf")
async def export_report_pdf(case_id: str, report_id: str, request: Request):
    """Export a report as PDF with Grounds of Merit and Legal References"""
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import mm
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
    from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
    from io import BytesIO
    
    user = await get_current_user(request)
    
    # Get report
    report = await db.reports.find_one(
        {"report_id": report_id, "case_id": case_id, "user_id": user.user_id},
        {"_id": 0}
    )
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    
    # Get case data
    case = await db.cases.find_one({"case_id": case_id, "user_id": user.user_id}, {"_id": 0})
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
    
    # Get grounds of merit for this case
    grounds = await db.grounds_of_merit.find(
        {"case_id": case_id},
        {"_id": 0}
    ).to_list(100)
    
    # Create PDF buffer
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=20*mm,
        leftMargin=20*mm,
        topMargin=20*mm,
        bottomMargin=28*mm
    )
    
    # Styles
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(
        name='ReportTitle',
        fontSize=26,
        spaceAfter=14,
        alignment=TA_CENTER,
        fontName='Helvetica-Bold'
    ))
    styles.add(ParagraphStyle(
        name='ReportSubtitle',
        fontSize=12,
        spaceAfter=10,
        alignment=TA_CENTER,
        textColor=colors.HexColor('#475569')
    ))
    styles.add(ParagraphStyle(
        name='SectionHeader',
        fontSize=16,
        spaceBefore=18,
        spaceAfter=8,
        fontName='Helvetica-Bold',
        textColor=colors.HexColor('#0f172a')
    ))
    styles.add(ParagraphStyle(
        name='SubHeader',
        fontSize=13,
        spaceBefore=10,
        spaceAfter=6,
        fontName='Helvetica-Bold',
        textColor=colors.HexColor('#1e293b')
    ))
    styles.add(ParagraphStyle(
        name='ReportBodyText',
        fontSize=11,
        spaceAfter=6,
        alignment=TA_JUSTIFY,
        leading=16
    ))
    styles.add(ParagraphStyle(
        name='BulletText',
        parent=styles['ReportBodyText'],
        leftIndent=12,
        bulletIndent=6
    ))
    styles.add(ParagraphStyle(
        name='LawSection',
        fontSize=10,
        spaceAfter=4,
        leftIndent=18,
        textColor=colors.HexColor('#1e40af')
    ))
    styles.add(ParagraphStyle(
        name='GroundTitle',
        fontSize=13,
        spaceBefore=10,
        spaceAfter=4,
        fontName='Helvetica-Bold',
        textColor=colors.HexColor('#1e3a8a')
    ))
    styles.add(ParagraphStyle(
        name='NumberedSectionHeader',
        fontSize=15,
        spaceBefore=16,
        spaceAfter=8,
        fontName='Helvetica-Bold',
        textColor=colors.HexColor('#0f172a')
    ))
    styles.add(ParagraphStyle(
        name='CoverMetaLabel',
        fontSize=10,
        fontName='Helvetica-Bold',
        textColor=colors.HexColor('#64748b'),
        spaceAfter=2,
    ))
    styles.add(ParagraphStyle(
        name='CoverMetaValue',
        fontSize=13,
        fontName='Helvetica-Bold',
        textColor=colors.HexColor('#0f172a'),
        spaceAfter=6,
    ))
    styles.add(ParagraphStyle(
        name='CoverDisclaimer',
        fontSize=10,
        fontName='Helvetica-Bold',
        textColor=colors.HexColor('#1e293b'),
        alignment=TA_CENTER,
        leading=14,
    ))

    def format_inline(text: str) -> str:
        clean = (text or "").replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        # Convert markdown bold
        clean = re.sub(r"\*\*(.*?)\*\*", r"<b>\1</b>", clean)
        # Convert markdown links [text](url) to just text
        clean = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", clean)
        return clean

    def render_table(lines):
        rows = []
        for line in lines:
            parts = [p.strip() for p in line.strip().strip("|").split("|")]
            if not parts:
                continue
            if all(set(p) <= set("-:") for p in parts):
                continue
            # Escape special characters in table cells for reportlab
            safe_parts = []
            for p in parts:
                cell = re.sub(r"\*\*(.*?)\*\*", r"\1", p)
                cell = cell.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
                safe_parts.append(cell)
            rows.append(safe_parts)
        if not rows:
            return
        col_count = max(len(r) for r in rows)
        rows = [r + [""] * (col_count - len(r)) for r in rows]
        try:
            col_width = doc.width / col_count
            para_rows = []
            cell_style = ParagraphStyle(name='CellText', fontSize=11, leading=13, fontName='Helvetica', wordWrap='CJK')
            header_style = ParagraphStyle(name='HeaderCellText', fontSize=11, leading=13, fontName='Helvetica-Bold', textColor=colors.white)
            for ri, row in enumerate(rows):
                style = header_style if ri == 0 else cell_style
                para_rows.append([Paragraph(c[:260], style) for c in row])
            table = Table(para_rows, colWidths=[col_width] * col_count, repeatRows=1)
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1e293b')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('FONTSIZE', (0, 0), (-1, -1), 8),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#cbd5e1')),
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.whitesmoke, colors.white]),
                ('LEFTPADDING', (0, 0), (-1, -1), 4),
                ('RIGHTPADDING', (0, 0), (-1, -1), 4),
                ('TOPPADDING', (0, 0), (-1, -1), 3),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
            ]))
            story.append(table)
            story.append(Spacer(1, 4*mm))
        except Exception as e:
            logger.warning(f"PDF table render failed: {e}")
            for row in rows:
                story.append(Paragraph(" | ".join(row), styles['ReportBodyText']))

    def render_markdown(text: str):
        lines = (text or "").splitlines()
        buffer = []
        table_lines = []

        def flush_paragraph():
            if buffer:
                paragraph = " ".join(buffer).strip()
                if paragraph:
                    try:
                        story.append(Paragraph(format_inline(paragraph), styles['ReportBodyText']))
                        story.append(Spacer(1, 2*mm))
                    except Exception as e:
                        logger.warning(f"PDF paragraph failed: {e}")
                        # Fallback: strip all XML-like content
                        safe = re.sub(r'<[^>]+>', '', paragraph)
                        story.append(Paragraph(safe, styles['ReportBodyText']))
            buffer.clear()

        for line in lines:
            stripped = line.strip()
            if not stripped:
                flush_paragraph()
                continue
            if stripped.startswith("|") and "|" in stripped:
                flush_paragraph()
                table_lines.append(stripped)
                continue
            if table_lines and not (stripped.startswith("|") and "|" in stripped):
                render_table(table_lines)
                table_lines = []
            if stripped.startswith("## "):
                flush_paragraph()
                story.append(Paragraph(format_inline(stripped[3:].strip()), styles['SectionHeader']))
                story.append(Spacer(1, 2*mm))
                continue
            if re.match(r'^\d+\.\s+[A-Z][A-Z0-9\s/&()\-]{4,}$', stripped):
                flush_paragraph()
                story.append(Paragraph(format_inline(stripped), styles['NumberedSectionHeader']))
                story.append(Spacer(1, 2*mm))
                continue
            if stripped.startswith("### "):
                flush_paragraph()
                story.append(Paragraph(format_inline(stripped[4:].strip()), styles['SubHeader']))
                story.append(Spacer(1, 1*mm))
                continue
            if stripped.startswith("#### "):
                flush_paragraph()
                story.append(Paragraph(format_inline(stripped[5:].strip()), styles['SubHeader']))
                story.append(Spacer(1, 1*mm))
                continue
            if re.match(r'^Ground\s+\d+\s*:', stripped, re.I):
                flush_paragraph()
                story.append(Paragraph(format_inline(stripped), styles['GroundTitle']))
                story.append(Spacer(1, 1*mm))
                continue
            if stripped.startswith("- ") or stripped.startswith("• "):
                flush_paragraph()
                bullet_text = stripped[2:].strip()
                story.append(Paragraph(format_inline(f"- {bullet_text}"), styles['BulletText']))
                story.append(Spacer(1, 1*mm))
                continue
            # Handle numbered lists
            if re.match(r'^\d+\.\s', stripped):
                flush_paragraph()
                story.append(Paragraph(format_inline(stripped), styles['BulletText']))
                story.append(Spacer(1, 1*mm))
                continue
            buffer.append(stripped)

        flush_paragraph()
        if table_lines:
            render_table(table_lines)

    story = []

    # Report Title
    report_type_labels = {
        'quick_summary': 'Quick Case Summary',
        'full_detailed': 'Full Detailed Legal Analysis ($150 AUD)',
        'extensive_log': 'Extensive Case Log & Analysis ($200 AUD)',
        'barrister_view': 'Barrister Brief'
    }
    title = report_type_labels.get(report.get('report_type'), 'Legal Report')
    resolved_sentence = await _derive_export_sentence(case, case_id, user.user_id, report)
    footer_label = _truncate_export_footer(_build_export_footer_label(case, title, report.get('generated_at')))
    footer_message = _build_export_footer_message()

    cover_meta = [
        ['Case Title', case.get('title', 'N/A')],
        ['Defendant', case.get('defendant_name', 'N/A')],
        ['Court / State', f"{case.get('court', 'Court')} — {(case.get('state', 'NSW') or 'NSW').upper()}"],
        ['Report', title],
        ['Offence', case.get('offence_type') or (case.get('offence_category') or 'Not recorded').replace('_', ' ').title()],
        ['Sentence', resolved_sentence],
    ]

    story.append(Spacer(1, 18*mm))
    story.append(Paragraph("Appeal Case Manager", styles['ReportSubtitle']))
    story.append(Paragraph(title, styles['ReportTitle']))
    story.append(Paragraph("Created and Designed by Deb King", styles['ReportSubtitle']))
    story.append(Paragraph("Criminal Law Appeal Case Management", styles['ReportSubtitle']))
    story.append(Spacer(1, 10*mm))

    cover_table_rows = []
    for idx in range(0, len(cover_meta), 2):
        left = cover_meta[idx]
        right = cover_meta[idx + 1] if idx + 1 < len(cover_meta) else ["", ""]
        cover_table_rows.append([
            Paragraph(f"<b>{left[0]}</b><br/>{left[1]}", styles['CoverMetaValue']),
            Paragraph(f"<b>{right[0]}</b><br/>{right[1]}", styles['CoverMetaValue'])
        ])
    cover_table = Table(cover_table_rows, colWidths=[80*mm, 80*mm])
    cover_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#f8fafc')),
        ('BOX', (0, 0), (-1, -1), 1, colors.HexColor('#cbd5e1')),
        ('INNERGRID', (0, 0), (-1, -1), 1, colors.HexColor('#e2e8f0')),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('LEFTPADDING', (0, 0), (-1, -1), 10),
        ('RIGHTPADDING', (0, 0), (-1, -1), 10),
        ('TOPPADDING', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
    ]))
    story.append(cover_table)
    story.append(Spacer(1, 12*mm))
    story.append(Paragraph(
        "NOT LEGAL ADVICE — This document is an educational tool only. All analysis and recommendations must be independently verified by a qualified Australian legal professional.",
        styles['CoverDisclaimer']
    ))
    story.append(PageBreak())

    # Header
    story.append(Paragraph("APPEAL CASE MANAGER", styles['ReportTitle']))
    story.append(Paragraph("Criminal Law Appeal Case Management", styles['ReportSubtitle']))
    story.append(Paragraph("Created and Designed by Deb King — GLENMORE PARK NSW", styles['ReportSubtitle']))
    story.append(Spacer(1, 8*mm))
    story.append(Paragraph(f"Case: {case.get('title', 'Unknown')}", styles['ReportSubtitle']))
    story.append(Spacer(1, 10*mm))

    def draw_page_footer(canvas_obj, pdf_doc):
        canvas_obj.saveState()
        footer_top = 14 * mm
        footer_mid = 10 * mm
        footer_bottom = 6 * mm
        canvas_obj.setStrokeColor(colors.HexColor('#cbd5e1'))
        canvas_obj.setLineWidth(0.6)
        canvas_obj.line(pdf_doc.leftMargin, footer_top, A4[0] - pdf_doc.rightMargin, footer_top)
        canvas_obj.setFillColor(colors.HexColor('#475569'))
        canvas_obj.setFont('Helvetica', 8)
        canvas_obj.drawString(pdf_doc.leftMargin, footer_mid, footer_label)
        canvas_obj.drawRightString(A4[0] - pdf_doc.rightMargin, footer_mid, f"Page {canvas_obj.getPageNumber()}")
        canvas_obj.setFillColor(colors.HexColor('#1e3a5f'))
        canvas_obj.setFont('Helvetica-Bold', 8)
        canvas_obj.drawCentredString(A4[0] / 2, footer_bottom, footer_message)
        canvas_obj.restoreState()

    story.append(Paragraph(title, styles['ReportTitle']))
    story.append(Spacer(1, 5*mm))
    
    # Case Info Table — skip N/A fields
    # Get grounds for PDF header
    pdf_grounds = await db.grounds_of_merit.find({"case_id": case_id}, {"_id": 0}).to_list(100)
    case_data_rows = [
        ['Case Title:', case.get('title', 'N/A')],
        ['Defendant:', case.get('defendant_name', 'N/A')],
    ]
    if case.get('case_number') and case.get('case_number') != 'N/A':
        case_data_rows.append(['Case Number:', case['case_number']])
    if case.get('court') and case.get('court') != 'N/A':
        case_data_rows.append(['Court:', case['court']])
    if case.get('state'):
        case_data_rows.append(['Jurisdiction:', case['state'].upper()])
    if resolved_sentence and resolved_sentence != 'See report analysis':
        case_data_rows.append(['Sentence:', resolved_sentence])
    case_data_rows.append(['Grounds:', f"{len(pdf_grounds)} identified"])
    case_data_rows.append(['Generated:', report.get('generated_at', 'N/A')[:10] if report.get('generated_at') else 'N/A'])
    
    case_table = Table(case_data_rows, colWidths=[40*mm, 120*mm])
    case_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor('#475569')),
        ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
        ('ALIGN', (1, 0), (1, -1), 'LEFT'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
    ]))
    story.append(case_table)
    story.append(Spacer(1, 10*mm))
    
    # Grounds of Merit Section
    if grounds:
        story.append(Paragraph("GROUNDS OF MERIT", styles['SectionHeader']))
        story.append(Spacer(1, 5*mm))
        
        ground_type_labels = {
            'procedural_error': 'Procedural Error',
            'fresh_evidence': 'Fresh Evidence',
            'miscarriage_of_justice': 'Miscarriage of Justice',
            'sentencing_error': 'Sentencing Error',
            'judicial_error': 'Judicial Error',
            'ineffective_counsel': 'Ineffective Counsel',
            'prosecution_misconduct': 'Prosecution Misconduct',
            'jury_irregularity': 'Jury Irregularity',
            'constitutional_violation': 'Constitutional Violation',
            'other': 'Other'
        }
        
        for idx, ground in enumerate(grounds, 1):
            ground_type = ground_type_labels.get(ground.get('ground_type'), 'Other')
            strength = ground.get('strength', 'moderate').capitalize()
            
            # Ground header
            story.append(Paragraph(
                f"{idx}. {ground.get('title', 'Unnamed Ground')} [{ground_type}] - Strength: {strength}",
                styles['GroundTitle']
            ))
            
            # Description
            if ground.get('description'):
                story.append(Paragraph(ground.get('description'), styles['ReportBodyText']))
            
            # Legal References (Law Sections)
            if ground.get('law_sections'):
                story.append(Paragraph("<b>Relevant Law Sections:</b>", styles['ReportBodyText']))
                for section in ground.get('law_sections', []):
                    section_text = f"• s.{section.get('section', '')} {section.get('act', '')} ({section.get('jurisdiction', 'NSW')})"
                    story.append(Paragraph(section_text.replace('•', '-'), styles['LawSection']))
            
            # Similar Cases
            if ground.get('similar_cases'):
                story.append(Paragraph("<b>Similar Cases:</b>", styles['ReportBodyText']))
                for case_ref in ground.get('similar_cases', []):
                    case_text = f"• {case_ref.get('case_name', '')} {case_ref.get('citation', '')}"
                    story.append(Paragraph(case_text.replace('•', '-'), styles['LawSection']))
            
            # Supporting Evidence
            if ground.get('supporting_evidence'):
                story.append(Paragraph("<b>Supporting Evidence:</b>", styles['ReportBodyText']))
                for evidence in ground.get('supporting_evidence', []):
                    story.append(Paragraph(f"- {evidence}", styles['LawSection']))
            
            story.append(Spacer(1, 5*mm))
    
    # Legal Framework Reference
    story.append(Paragraph("LEGAL FRAMEWORK REFERENCE", styles['SectionHeader']))
    story.append(Spacer(1, 2*mm))
    legal_refs = [
        "- Crimes Act 1900 (NSW) - Primary criminal law for NSW",
        "- Criminal Appeal Act 1912 (NSW) - Governs appeals in NSW",
        "- Criminal Code Act 1995 (Cth) - Federal criminal law",
        "- Evidence Act 1995 (NSW & Cth) - Evidence admissibility",
        "- Sentencing Act 1995 (NSW) - Sentencing guidelines"
    ]
    for ref in legal_refs:
        story.append(Paragraph(ref, styles['LawSection']))
    
    story.append(Spacer(1, 10*mm))
    
    # Main Analysis Content
    story.append(Paragraph("DETAILED ANALYSIS", styles['SectionHeader']))

    analysis_text = _strip_report_placeholders(report.get('content', {}).get('analysis', 'No analysis available.'))
    render_markdown(analysis_text)

    # Footer — Created By + Bold Disclaimer
    story.append(Spacer(1, 15*mm))
    story.append(Paragraph(
        "Created and Designed by Deb King",
        ParagraphStyle(name='CreatedBy', fontSize=14, fontName='Helvetica-Bold', alignment=TA_CENTER, textColor=colors.HexColor('#1e3a5f'), spaceAfter=6)
    ))
    story.append(Paragraph(
        "Criminal Law Appeal Case Management — GLENMORE PARK NSW",
        ParagraphStyle(name='Footer1', fontSize=9, alignment=TA_CENTER, textColor=colors.HexColor('#475569'), spaceAfter=10)
    ))
    story.append(Spacer(1, 5*mm))
    story.append(Paragraph(
        "NOT LEGAL ADVICE",
        ParagraphStyle(name='DisclaimerTitle', fontSize=14, fontName='Helvetica-Bold', alignment=TA_CENTER, textColor=colors.HexColor('#dc2626'), spaceAfter=4)
    ))
    story.append(Paragraph(
        "This document is an educational tool only. It does NOT constitute legal advice and must NOT be relied upon as such. "
        "All analysis, findings, and recommendations must be independently verified by a qualified Australian legal professional "
        "before any action is taken. No solicitor-client relationship is formed through the provision of this report.",
        ParagraphStyle(name='DisclaimerBody', fontSize=10, fontName='Helvetica-Bold', alignment=TA_CENTER, textColor=colors.HexColor('#1e293b'), leading=14)
    ))
    
    # Build PDF
    try:
        doc.build(story, onFirstPage=draw_page_footer, onLaterPages=draw_page_footer)
    except Exception as e:
        logger.error(f"PDF build failed: {e}")
        raise HTTPException(status_code=500, detail=f"PDF generation failed: {str(e)[:200]}")
    buffer.seek(0)
    
    # Create filename
    safe_title = "".join(c for c in case.get('title', 'Report')[:30] if c.isalnum() or c in ' -_').strip()
    filename = f"{safe_title}_{report.get('report_type', 'report')}.pdf"
    
    return Response(
        content=buffer.getvalue(),
        media_type="application/pdf",
        headers={
            "Content-Disposition": f'attachment; filename="{filename}"'
        }
    )

@api_router.get("/cases/{case_id}/reports/{report_id}/export-docx")
async def export_report_docx(case_id: str, report_id: str, request: Request):
    """Export a report as DOCX (Microsoft Word) with Grounds of Merit and Legal References"""
    from docx import Document as DocxDocument
    from docx.shared import Inches, Pt, RGBColor
    from docx.enum.text import WD_ALIGN_PARAGRAPH
    from docx.enum.style import WD_STYLE_TYPE
    from docx.oxml import OxmlElement
    from docx.oxml.ns import qn
    from io import BytesIO
    
    user = await get_current_user(request)
    
    # Get report
    report = await db.reports.find_one(
        {"report_id": report_id, "case_id": case_id, "user_id": user.user_id},
        {"_id": 0}
    )
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    
    # Get case data
    case = await db.cases.find_one({"case_id": case_id, "user_id": user.user_id}, {"_id": 0})
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
    
    # Get grounds of merit
    grounds = await db.grounds_of_merit.find(
        {"case_id": case_id},
        {"_id": 0}
    ).to_list(100)
    
    # Create DOCX document
    doc = DocxDocument()
    
    # Set up styles
    styles = doc.styles
    
    # Title style
    title_style = styles['Title']
    title_style.font.size = Pt(24)
    title_style.font.bold = True
    title_style.font.color.rgb = RGBColor(30, 41, 59)
    
    # Heading 1 style
    h1_style = styles['Heading 1']
    h1_style.font.size = Pt(16)
    h1_style.font.bold = True
    h1_style.font.color.rgb = RGBColor(30, 41, 59)
    
    # Heading 2 style
    h2_style = styles['Heading 2']
    h2_style.font.size = Pt(14)
    h2_style.font.bold = True
    h2_style.font.color.rgb = RGBColor(30, 58, 138)
    
    # Header
    header_para = doc.add_paragraph()
    header_para.alignment = WD_ALIGN_PARAGRAPH.CENTER
    header_run = header_para.add_run("APPEAL CASE MANAGER")
    header_run.font.size = Pt(14)
    header_run.font.bold = True
    header_run.font.color.rgb = RGBColor(15, 23, 42)

    sub_header = doc.add_paragraph()
    sub_header.alignment = WD_ALIGN_PARAGRAPH.CENTER
    sub_run = sub_header.add_run("Criminal Law Appeal Case Management")
    sub_run.font.size = Pt(11)
    sub_run.font.color.rgb = RGBColor(71, 85, 105)

    created_by = doc.add_paragraph()
    created_by.alignment = WD_ALIGN_PARAGRAPH.CENTER
    cb_run = created_by.add_run("Created and Designed by Deb King — GLENMORE PARK NSW")
    cb_run.font.size = Pt(11)
    cb_run.font.bold = True
    cb_run.font.color.rgb = RGBColor(30, 58, 95)

    case_line = doc.add_paragraph()
    case_line.alignment = WD_ALIGN_PARAGRAPH.CENTER
    case_run = case_line.add_run(f"Case: {case.get('title', 'Unknown')}")
    case_run.font.size = Pt(10)
    case_run.font.color.rgb = RGBColor(71, 85, 105)

    doc.add_paragraph()
    
    # Report Title
    report_type_labels = {
        'quick_summary': 'Quick Case Summary',
        'full_detailed': 'Full Detailed Legal Analysis', 
        'extensive_log': 'Extensive Case Log & Analysis',
        'barrister_view': 'Barrister Brief'
    }
    report_title = report_type_labels.get(report.get('report_type'), 'Legal Report')
    resolved_sentence = await _derive_export_sentence(case, case_id, user.user_id, report)
    footer_label = _truncate_export_footer(_build_export_footer_label(case, report_title, report.get('generated_at')))
    footer_message = _build_export_footer_message()

    def add_page_number_field(paragraph):
        run = paragraph.add_run()
        fld_char_begin = OxmlElement('w:fldChar')
        fld_char_begin.set(qn('w:fldCharType'), 'begin')
        instr_text = OxmlElement('w:instrText')
        instr_text.set(qn('xml:space'), 'preserve')
        instr_text.text = ' PAGE '
        fld_char_end = OxmlElement('w:fldChar')
        fld_char_end.set(qn('w:fldCharType'), 'end')
        run._r.append(fld_char_begin)
        run._r.append(instr_text)
        run._r.append(fld_char_end)

    for section in doc.sections:
        section.footer_distance = Inches(0.35)
        footer = section.footer
        footer_line = footer.paragraphs[0]
        footer_line.alignment = WD_ALIGN_PARAGRAPH.LEFT
        footer_line_run = footer_line.add_run(f"{footer_label} — Page ")
        footer_line_run.font.size = Pt(8)
        footer_line_run.font.color.rgb = RGBColor(71, 85, 105)
        add_page_number_field(footer_line)

        footer_msg_para = footer.add_paragraph()
        footer_msg_para.alignment = WD_ALIGN_PARAGRAPH.CENTER
        footer_msg_run = footer_msg_para.add_run(footer_message)
        footer_msg_run.font.size = Pt(8)
        footer_msg_run.font.bold = True
        footer_msg_run.font.color.rgb = RGBColor(30, 58, 95)

    cover_title = doc.add_paragraph()
    cover_title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    cover_title_run = cover_title.add_run(report_title)
    cover_title_run.font.size = Pt(24)
    cover_title_run.font.bold = True
    cover_title_run.font.color.rgb = RGBColor(15, 23, 42)

    cover_subtitle = doc.add_paragraph()
    cover_subtitle.alignment = WD_ALIGN_PARAGRAPH.CENTER
    cover_subtitle_run = cover_subtitle.add_run("Appeal Case Manager")
    cover_subtitle_run.font.size = Pt(11)
    cover_subtitle_run.font.bold = True
    cover_subtitle_run.font.color.rgb = RGBColor(29, 78, 216)

    cover_created = doc.add_paragraph()
    cover_created.alignment = WD_ALIGN_PARAGRAPH.CENTER
    cover_created_run = cover_created.add_run("Created and Designed by Deb King")
    cover_created_run.font.size = Pt(11)
    cover_created_run.font.bold = True
    cover_created_run.font.color.rgb = RGBColor(30, 58, 95)

    cover_case = doc.add_paragraph()
    cover_case.alignment = WD_ALIGN_PARAGRAPH.CENTER
    cover_case_run = cover_case.add_run(case.get('title', 'Unknown case'))
    cover_case_run.font.size = Pt(12)
    cover_case_run.font.color.rgb = RGBColor(71, 85, 105)

    doc.add_paragraph()
    cover_info = [
        ('Case Title', case.get('title', 'N/A')),
        ('Defendant', case.get('defendant_name', 'N/A')),
        ('Court / State', f"{case.get('court', 'Court')} — {(case.get('state', 'NSW') or 'NSW').upper()}"),
        ('Report', report_title),
        ('Offence', case.get('offence_type') or (case.get('offence_category') or 'Not recorded').replace('_', ' ').title()),
        ('Sentence', resolved_sentence),
    ]
    cover_table = doc.add_table(rows=len(cover_info), cols=2)
    cover_table.style = 'Table Grid'
    for row_idx, (label, value) in enumerate(cover_info):
        row = cover_table.rows[row_idx]
        row.cells[0].text = label
        row.cells[1].text = str(value)
        row.cells[0].paragraphs[0].runs[0].font.bold = True

    cover_disclaimer = doc.add_paragraph()
    cover_disclaimer.alignment = WD_ALIGN_PARAGRAPH.CENTER
    cover_disclaimer_run = cover_disclaimer.add_run(
        "NOT LEGAL ADVICE — This document is an educational tool only. All analysis and recommendations must be independently verified by a qualified Australian legal professional."
    )
    cover_disclaimer_run.font.size = Pt(10)
    cover_disclaimer_run.font.bold = True
    cover_disclaimer_run.font.color.rgb = RGBColor(30, 41, 59)

    doc.add_page_break()

    title = doc.add_heading(report_title, 0)
    title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    
    doc.add_paragraph()
    
    # Case Information Table — skip N/A fields
    case_info = [
        ('Case Title:', case.get('title', 'N/A')),
        ('Defendant:', case.get('defendant_name', 'N/A')),
    ]
    if case.get('case_number') and case.get('case_number') != 'N/A':
        case_info.append(('Case Number:', case['case_number']))
    if case.get('court') and case.get('court') != 'N/A':
        case_info.append(('Court:', case['court']))
    if case.get('state'):
        case_info.append(('Jurisdiction:', case['state'].upper()))
    if resolved_sentence and resolved_sentence != 'See report analysis':
        case_info.append(('Sentence:', resolved_sentence))
    case_info.append(('Grounds:', f"{len(grounds)} identified"))
    case_info.append(('Generated:', report.get('generated_at', 'N/A')[:10] if report.get('generated_at') else 'N/A'))
    
    case_table = doc.add_table(rows=len(case_info), cols=2)
    case_table.style = 'Table Grid'
    
    for i, (label, value) in enumerate(case_info):
        row = case_table.rows[i]
        row.cells[0].text = label
        row.cells[0].paragraphs[0].runs[0].font.bold = True
        row.cells[1].text = str(value)
    
    doc.add_paragraph()
    
    # Grounds of Merit Section
    if grounds:
        doc.add_heading('GROUNDS OF MERIT', level=1)
        
        ground_type_labels = {
            'procedural_error': 'Procedural Error',
            'fresh_evidence': 'Fresh Evidence',
            'miscarriage_of_justice': 'Miscarriage of Justice',
            'sentencing_error': 'Sentencing Error',
            'judicial_error': 'Judicial Error',
            'ineffective_counsel': 'Ineffective Counsel',
            'prosecution_misconduct': 'Prosecution Misconduct',
            'jury_irregularity': 'Jury Irregularity',
            'constitutional_violation': 'Constitutional Violation',
            'other': 'Other'
        }
        
        for idx, ground in enumerate(grounds, 1):
            ground_type = ground_type_labels.get(ground.get('ground_type'), 'Other')
            strength = ground.get('strength', 'moderate').capitalize()
            
            # Ground heading
            doc.add_heading(
                f"{idx}. {ground.get('title', 'Unnamed Ground')} [{ground_type}] - Strength: {strength}",
                level=2
            )
            
            # Description
            if ground.get('description'):
                doc.add_paragraph(ground.get('description'))
            
            # Legal References
            if ground.get('law_sections'):
                law_para = doc.add_paragraph()
                law_run = law_para.add_run('Relevant Law Sections:')
                law_run.font.bold = True
                law_run.font.color.rgb = RGBColor(30, 64, 175)
                
                for section in ground.get('law_sections', []):
                    section_text = f"s.{section.get('section', '')} {section.get('act', '')} ({section.get('jurisdiction', 'NSW')})"
                    bullet = doc.add_paragraph(section_text, style='List Bullet')
                    for run in bullet.runs:
                        run.font.color.rgb = RGBColor(30, 64, 175)
            
            # Similar Cases
            if ground.get('similar_cases'):
                cases_para = doc.add_paragraph()
                cases_run = cases_para.add_run('Similar Cases:')
                cases_run.font.bold = True
                cases_run.font.color.rgb = RGBColor(30, 58, 138)
                
                for case_ref in ground.get('similar_cases', []):
                    case_text = f"{case_ref.get('case_name', '')} {case_ref.get('citation', '')}"
                    doc.add_paragraph(case_text, style='List Bullet')
            
            # Supporting Evidence
            if ground.get('supporting_evidence'):
                evidence_para = doc.add_paragraph()
                evidence_run = evidence_para.add_run('Supporting Evidence:')
                evidence_run.font.bold = True
                evidence_run.font.color.rgb = RGBColor(5, 150, 105)
                
                for evidence in ground.get('supporting_evidence', []):
                    doc.add_paragraph(evidence, style='List Bullet')
            
            doc.add_paragraph()
    
    # Legal Framework Reference
    doc.add_heading('LEGAL FRAMEWORK REFERENCE', level=1)
    
    legal_refs = [
        "Crimes Act 1900 (NSW) - Primary criminal law for New South Wales",
        "Criminal Appeal Act 1912 (NSW) - Governs criminal appeals in NSW",
        "Criminal Code Act 1995 (Cth) - Federal criminal law",
        "Evidence Act 1995 (NSW & Cth) - Rules on evidence admissibility",
        "Sentencing Act 1995 (NSW) - Sentencing guidelines and procedures"
    ]
    
    for ref in legal_refs:
        doc.add_paragraph(ref, style='List Bullet')
    
    doc.add_paragraph()
    
    # Detailed Analysis
    doc.add_heading('DETAILED ANALYSIS', level=1)

    def add_table_docx(lines):
        rows = []
        for line in lines:
            parts = [p.strip() for p in line.strip().strip("|").split("|")]
            if not parts:
                continue
            if all(set(p) <= set("-:") for p in parts):
                continue
            rows.append(parts)
        if not rows:
            return
        table = doc.add_table(rows=len(rows), cols=len(rows[0]))
        table.style = 'Table Grid'
        table.autofit = False
        available_width = doc.sections[0].page_width - doc.sections[0].left_margin - doc.sections[0].right_margin
        col_width = int(available_width / max(1, len(rows[0])))
        for r_idx, row in enumerate(rows):
            for c_idx, value in enumerate(row):
                cell = table.cell(r_idx, c_idx)
                cell.width = col_width
                cell.text = value.replace('**', '')
                if r_idx == 0:
                    for run in cell.paragraphs[0].runs:
                        run.bold = True
                        run.font.size = Pt(11)
                        run.font.name = 'Arial'
                else:
                    for run in cell.paragraphs[0].runs:
                        run.font.size = Pt(11)
                        run.font.name = 'Arial'
        doc.add_paragraph()

    def render_markdown_docx(text):
        lines = (text or "").splitlines()
        buffer = []
        table_lines = []

        def flush_paragraph():
            if buffer:
                paragraph = " ".join(buffer).replace('**', '').strip()
                if paragraph:
                    doc.add_paragraph(paragraph)
            buffer.clear()

        for line in lines:
            stripped = line.strip()
            if not stripped:
                flush_paragraph()
                continue
            if stripped.startswith("|") and "|" in stripped:
                flush_paragraph()
                table_lines.append(stripped)
                continue
            if table_lines and not (stripped.startswith("|") and "|" in stripped):
                add_table_docx(table_lines)
                table_lines = []
            if stripped.startswith("## "):
                flush_paragraph()
                doc.add_heading(stripped[3:].strip(), level=1)
                continue
            if stripped.startswith("### "):
                flush_paragraph()
                doc.add_heading(stripped[4:].strip(), level=2)
                continue
            if stripped.startswith("- ") or stripped.startswith("• "):
                flush_paragraph()
                doc.add_paragraph(stripped[2:].strip(), style='List Bullet')
                continue
            buffer.append(stripped)

        flush_paragraph()
        if table_lines:
            add_table_docx(table_lines)

    analysis_text = _strip_report_placeholders(report.get('content', {}).get('analysis', 'No analysis available.'))
    render_markdown_docx(analysis_text)
    
    # Footer disclaimer
    doc.add_paragraph()
    
    # Created By
    created_para = doc.add_paragraph()
    created_para.alignment = WD_ALIGN_PARAGRAPH.CENTER
    created_run = created_para.add_run("Created and Designed by Deb King")
    created_run.font.size = Pt(14)
    created_run.font.bold = True
    created_run.font.color.rgb = RGBColor(30, 58, 95)
    
    footer_para = doc.add_paragraph()
    footer_para.alignment = WD_ALIGN_PARAGRAPH.CENTER
    footer_run = footer_para.add_run("Criminal Law Appeal Case Management — GLENMORE PARK NSW")
    footer_run.font.size = Pt(9)
    footer_run.font.color.rgb = RGBColor(100, 116, 139)
    
    doc.add_paragraph()
    
    # Bold Disclaimer
    disc_title = doc.add_paragraph()
    disc_title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    disc_run = disc_title.add_run("NOT LEGAL ADVICE")
    disc_run.font.size = Pt(14)
    disc_run.font.bold = True
    disc_run.font.color.rgb = RGBColor(220, 38, 38)
    
    disc_body = doc.add_paragraph()
    disc_body.alignment = WD_ALIGN_PARAGRAPH.CENTER
    disc_body_run = disc_body.add_run(
        "This document is an educational tool only. It does NOT constitute legal advice and must NOT be relied upon "
        "as such. All analysis, findings, and recommendations must be independently verified by a qualified Australian "
        "legal professional before any action is taken. No solicitor-client relationship is formed through the provision "
        "of this report."
    )
    disc_body_run.font.size = Pt(10)
    disc_body_run.font.bold = True
    disc_body_run.font.color.rgb = RGBColor(30, 41, 59)
    
    # Save to buffer
    buffer = BytesIO()
    doc.save(buffer)
    buffer.seek(0)
    
    # Create filename
    safe_title = "".join(c for c in case.get('title', 'Report')[:30] if c.isalnum() or c in ' -_').strip()
    filename = f"{safe_title}_{report.get('report_type', 'report')}.docx"
    
    return Response(
        content=buffer.getvalue(),
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        headers={
            "Content-Disposition": f'attachment; filename="{filename}"'
        }
    )

# ============ HEALTH CHECK ============

@api_router.get("/")
async def root():
    return {"message": "Criminal Appeal AI API", "status": "operational"}

@api_router.get("/health")
async def health_check():
    try:
        await db.command("ping")
        db_status = "connected"
    except Exception:
        db_status = "disconnected"
    return {
        "status": "healthy" if db_status == "connected" else "degraded",
        "database": db_status,
        "timestamp": datetime.now(timezone.utc).isoformat()
    }

# Include the router in the main app
app.include_router(api_router)

# Include modular routers
from routers.cases import router as cases_router
app.include_router(cases_router)

from routers.auth import router as auth_router
app.include_router(auth_router)

from routers.password_reset import router as password_reset_router
app.include_router(password_reset_router)

from routers.admin import router as admin_router
app.include_router(admin_router)

from routers.utilities import router as utilities_router
app.include_router(utilities_router)

from routers.deadlines import router as deadlines_router
app.include_router(deadlines_router)

from routers.analytics import router as analytics_router
app.include_router(analytics_router)

# Include statistics router
from routers.statistics import router as statistics_router
app.include_router(statistics_router)

# Include compare cases router
from routers.compare import router as compare_router
app.include_router(compare_router)

# Include contradictions router
from routers.contradictions import router as contradictions_router
app.include_router(contradictions_router)

# Include export router
from routers.export import router as export_router
app.include_router(export_router)

# PayID-only payment system (PayPal removed)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def cleanup_orphaned_reports():
    """Auto-fail or recover reports stuck in 'generating' from server restarts."""
    five_min_ago = (datetime.now(timezone.utc) - timedelta(minutes=5)).isoformat()
    
    # First, try to recover reports with partial content
    async for report in db.reports.find({"status": "generating", "generated_at": {"$lt": five_min_ago}}):
        partial = report.get("content", {}).get("analysis", "") or report.get("content", {}).get("partial_analysis", "")
        if partial and len(partial) > 5000:
            # Has substantial partial content — complete it
            await db.reports.update_one(
                {"report_id": report["report_id"]},
                {"$set": {
                    "status": "completed",
                    "content.analysis": partial,
                    "content.partial": False
                }}
            )
            logger.info(f"Recovered partial report {report['report_id']} ({len(partial)} chars)")
        else:
            await db.reports.update_one(
                {"report_id": report["report_id"]},
                {"$set": {"status": "failed", "error": "Generation interrupted by server restart. Please try again."}}
            )
            logger.info(f"Failed orphaned report {report['report_id']}")


@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()
