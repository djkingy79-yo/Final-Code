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


def is_admin_user(email: str) -> bool:
    normalized = (email or "").strip().lower()
    allowed = {(e or "").strip().lower() for e in ADMIN_EMAILS}
    return normalized in allowed

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
async def call_llm_with_fallback(system_prompt: str, user_prompt: str, session_id: str = "default") -> str:
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
            chat = LlmChat(api_key=api_key, session_id=session_id, system_message=system_prompt).with_model(provider, model_name).with_params(max_tokens=16384)
            result = await asyncio.wait_for(chat.send_message(UserMessage(text=user_prompt)), timeout=120)
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
    report_type: str  # quick_summary, full_detailed, extensive_log
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

# ============ AUTH HELPERS ============

async def get_current_user(request: Request) -> User:
    """Get current user from session token (cookie or header)"""
    session_token = request.cookies.get("session_token")
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
    emergent_api_key = os.environ.get('EMERGENT_LLM_KEY')
    
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
    emergent_api_key = os.environ.get('EMERGENT_LLM_KEY')
    
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
    grounds = await db.grounds.find({"case_id": case_id}, {"_id": 0}).to_list(50)
    deadlines = await db.deadlines.find({"case_id": case_id}, {"_id": 0}).to_list(50)
    checklist = await db.checklist_items.find({"case_id": case_id}, {"_id": 0}).to_list(50)
    reports = await db.reports.find({"case_id": case_id}, {"_id": 0, "content": 0}).to_list(20)
    
    context = f"""CASE: {case.get('title', 'Unknown')}
DEFENDANT: {case.get('defendant_name', 'Unknown')}
STATE: {case.get('state', 'Unknown').upper()}
COURT: {case.get('court', 'Unknown')}
OFFENCE: {case.get('offence_type', 'Unknown')} ({case.get('offence_category', 'Unknown')})

DOCUMENTS UPLOADED: {len(documents)}
TIMELINE EVENTS: {len(timeline)}
GROUNDS IDENTIFIED: {len(grounds)}
REPORTS GENERATED: {len(reports)}
DEADLINES SET: {len(deadlines)}
CHECKLIST ITEMS: {len(checklist)} (Completed: {sum(1 for c in checklist if c.get('completed'))})
"""
    
    if grounds:
        context += "\nIDENTIFIED GROUNDS:\n"
        for g in grounds:
            context += f"- {g.get('title', 'Unknown')} (Type: {g.get('ground_type', 'Unknown')}, Strength: {g.get('strength_rating', 'Unknown')})\n"
    
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
            }
        }
    
    payments = await db.payments.find(
        {"case_id": case_id, "user_id": user.user_id, "status": "completed"},
        {"_id": 0}
    ).to_list(100)
    
    # Return which features are unlocked
    unlocked = {
        "grounds_of_merit": False,
        "full_report": False,
        "extensive_report": False
    }
    
    for payment in payments:
        if payment.get("feature_type") in unlocked:
            unlocked[payment["feature_type"]] = True
    
    return {
        "payments": payments,
        "unlocked_features": unlocked
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
    
    if not feature_type or not case_id:
        raise HTTPException(status_code=400, detail="Missing feature_type or case_id")
    
    price = FEATURE_PRICES.get(feature_type, {}).get("price", 0)
    reference = f"ACM-{uuid.uuid4().hex[:8].upper()}"
    
    payment_record = {
        "payment_id": f"pay_{uuid.uuid4().hex[:12]}",
        "user_id": user.user_id,
        "case_id": case_id,
        "feature_type": feature_type,
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
    """Mark a PayID payment as submitted (manual verification by admin)"""
    user = await get_current_user(request)
    body = await request.json()
    reference = body.get("reference")
    case_id = body.get("case_id")
    feature_type = body.get("feature_type")
    
    if not reference:
        raise HTTPException(status_code=400, detail="Missing reference")
    
    payment = await db.payments.find_one(
        {"reference": reference, "user_id": user.user_id},
        {"_id": 0}
    )
    
    if not payment:
        raise HTTPException(status_code=404, detail="Payment reference not found")
    
    await db.payments.update_one(
        {"reference": reference},
        {"$set": {"status": "submitted", "submitted_at": datetime.now(timezone.utc).isoformat()}}
    )
    
    # Auto-grant access (admin can revoke if payment not received)
    await db.payments.update_one(
        {"reference": reference},
        {"$set": {"status": "completed", "completed_at": datetime.now(timezone.utc).isoformat()}}
    )
    
    # Grant feature access
    await db.cases.update_one(
        {"case_id": case_id, "user_id": user.user_id},
        {"$addToSet": {"unlocked_features": feature_type}}
    )
    
    return {"status": "verified", "message": "Payment confirmed. Feature unlocked."}


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
            {"$addToSet": {"unlocked_features": payment["feature_type"]}}
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
        "feature_type": "grounds_of_merit",
        "status": "completed"
    })
    
    is_unlocked = payment is not None or is_admin_user(user.email)
    
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
    return cleaned


async def analyze_case_with_ai(case_id: str, user_id: str, report_type: str, aggressive_mode: bool = False) -> dict:
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
Explain the case and appeal in clear, plain English for a non-lawyer: what the sentence means, what grounds exist, what the next steps are, and what outcomes are realistic. This section must appear BEFORE the paid-report comparison so clients understand their current position.

## 8. WHAT THE PAID REPORTS ADD
The Full Detailed Report ($150) includes:
- Deep-dive analysis of every ground with Crown response and rebuttal strategies
- Comparative sentencing table with 8+ cases and reduction pathways
- Complete outcome options matrix (quash, retrial, downgrade, sentence reduction)
- Step-by-step guide on how to start the appeal with required forms and deadlines
- Submissions blueprint and argument strategy for hearing
- Evidentiary gaps checklist and prioritised action plan
- Client plain-English brief with realistic next steps

The Extensive Report ($200) adds on top of the Full Detailed:
- 300+ word analysis per ground with specific case law citations
- 12+ sentencing comparisons and 15+ precedent cases
- Hearing preparation notes with anticipated questions and responses
- Conference preparation pack for barrister briefing
- Court pathway operations playbook across all court levels
- Fallback positions and alternative argument strategies for each ground
- Tailored AustLII search strings for further research

IMPORTANT:
- No cost estimates or funding discussion.
- No witness contradiction or witness credibility section.
- Be specific to the supplied material throughout — do not write generic legal advice.

GROUNDS TO COVER (MUST INCLUDE ALL):
{grounds_enumerated}"""

    elif report_type == "full_detailed":
        system_prompt = f"""{base_system}
{report_guardrails}
You are generating a PAID Full Detailed Report ($150 AUD). The user has ALREADY received a FREE Quick Summary that covered: case snapshot, primary issues identified, top potential grounds (preview), key legislation & similar cases (preview), sentencing overview (3 comparator cases), and appeal outlook.

THIS REPORT MUST BUILD ON — NOT REPEAT — THE QUICK SUMMARY. Do NOT re-state the same overview-level analysis. Instead:
- Where the Quick Summary previewed 3-5 grounds, THIS report must provide FULL analysis with Crown response, rebuttal strategy, and appeal impact for EVERY viable ground.
- You MUST include every ground listed in GROUNDS TO COVER (no omissions) with a minimum of 500 words per ground.
- Where the Quick Summary listed 3 sentencing comparators, THIS report must provide 8+ with detailed outcome analysis paragraphs.
- Where the Quick Summary gave a 2-paragraph appeal outlook, THIS report must provide full outcome pathway analysis, submissions blueprint, and actionable steps.
- Every section must deliver NEW insights, deeper strategy, and hearing-ready material that was NOT in the Quick Summary.

Include assertive appellate strategy, professional courtroom framing, and plain-English action notes. Include working hyperlinks to AustLII legislation, case databases, and court forms wherever possible.
CRITICAL: NEVER use placeholder text in parentheses like '(Entries will develop...)'. Every section MUST have REAL, SUBSTANTIVE CONTENT with actual legal analysis."""
        user_prompt = f"""Create a FULL DETAILED LEGAL ANALYSIS REPORT for this {category_name.lower()} appeal case.

{case_context}

GROUNDS TO COVER (MUST INCLUDE ALL — if 9 grounds, write 9 full analyses):
{grounds_enumerated}

Target range 7000-9000 words. This report must feel premium, strategic, and hearing-ready.

CRITICAL — NO REPETITION FROM QUICK SUMMARY:
The user already has a Quick Summary covering the case overview, top grounds preview, and basic sentencing comparison. This Full Detailed report must ADVANCE beyond that with deep analysis, complete ground-by-ground strategy, expanded sentencing tables, full outcome matrices, and hearing preparation content NOT present in the Quick Summary. Do NOT rewrite the case overview — jump straight into deep strategic analysis.

SECTION ORDERING: Analysis first, then Strategy, then Practical steps, then Client brief at the end.

Use this exact structure:

## 1. EXECUTIVE BRIEF
High-impact summary: strongest grounds, jurisdiction posture, likely pathways to relief, urgency items, and recommended next steps. Include a clear case snapshot paragraph (defendant, offence, sentence, court, judge) and a short list of primary issues at the end of this section.

## 2. FORENSIC CASE CHRONOLOGY
Chronological reconstruction of the case with event date, source anchor (which document/evidence), and legal significance of each event. Include at least 10 dated entries from the supplied material.

## 3. DOCUMENT EVIDENCE DIGEST
For each document/source uploaded: key extracts, reliability context, probative value, and appellate relevance.

## 4. GROUNDS OF MERIT PORTFOLIO
For EACH ground listed in GROUNDS TO COVER above (no omissions), provide:
- Legal threshold and supporting material from the case
- Viability rating (Strong / Moderate / Weak) with reasoning
- Likely Crown response and aggressive defence reply strategy
- **How this ground could assist in a successful appeal** — explain the practical impact if established (e.g., conviction quashed, sentence reduced, retrial ordered)
- Write each ground as a numbered entry starting with "Ground X: [Exact Title]" and then flowing paragraphs (no bullet-only answers). Minimum 500 words per ground.

## 5. COMPARATIVE SENTENCING TABLE (8+ CASES)
Provide a markdown table with at least 8 comparable sentencing outcomes.
Required columns:
| Case | Offence | Original Sentence / NPP | Appeal Outcome | Revised Sentence / NPP | Reduction (Years + %) | Key Reason |
Include AustLII search URL: [Search {state_info.get('appeal_court', 'NSWCCA')}]({state_info.get('cca_search_url', 'https://www.austlii.edu.au/cgi-bin/viewtoc/au/cases/nsw/NSWCCA/')})
After the table, provide a **Detailed Outcome Analysis** paragraph for each row explaining how the reduction was achieved and what grounds succeeded.

## 6. COMMON APPEAL GROUNDS FOR THIS OFFENCE TYPE
Provide a markdown table:
| Common Ground | Frequency in Comparable Appeals | Typical Success Pattern | Best Supporting Evidence |

## 7. OUTCOME OPTIONS AVAILABLE
First, provide a markdown table:
| Option | Legal Threshold | Likelihood in This Matter | Core Evidence Trigger | Practical Result |
Then provide detailed analysis for each pathway (keep ALL outcomes within THIS section — do NOT create separate headings for each outcome):
- **Conviction quashed** — detailed outcome analysis referencing ALL relevant grounds of merit identified above
- **Retrial ordered** — what happens next, timeframes, what changes
- **Conviction substituted/downgraded** (e.g., murder to manslaughter) — sentence impact, legal basis
- **Sentence reduced as manifestly excessive** — show before/after: Original sentence/NPP → Revised sentence/NPP
- **Appeal dismissed** — consequences and further options (special leave to High Court)

## 8. EVIDENTIARY GAPS + REMEDIATION CHECKLIST
Specific missing material from the case file and exact remediation steps with urgency priority (Critical / Important / Helpful).

## 9. PRECEDENT OUTCOME MATRIX (10-12 CASES)
For each case: citation, factual similarity to this matter, hearing outcome, extracted legal principle.
Include AustLII link: [Search {state_info.get('appeal_court', 'NSWCCA')}]({state_info.get('cca_search_url', 'https://www.austlii.edu.au/cgi-bin/viewtoc/au/cases/nsw/NSWCCA/')})

## 10. STATUTORY + DOCTRINAL FRAMEWORK MAP
Section-level mapping of all key Acts and appellate principles applicable. For each provision include the section number, Act name with year, and relevance to this case.
Link: [AustLII Legislation](https://www.austlii.edu.au/cgi-bin/viewdb/au/legis/)

## 11. HOW TO ARGUE EACH TOP GROUND
For each priority ground:
- Lead proposition (1-2 lines stating the core argument)
- Supporting authority cluster (statute + 2-3 precedent anchors)
- Expected prosecution answer
- Rebuttal strategy for hearing
- **How establishing this ground could lead to a successful appeal outcome**

## 12. SUBMISSIONS BLUEPRINT
Written submission strategy: argument sequence, authority placement, framing of each ground.
Oral submission strategy: likely bench questions, response lines, time allocation per ground.

## 13. HOW TO START YOUR APPEAL + REQUIRED FORMS
Step-by-step guide specific to {state_info.get('name', 'NSW')}:
1. Obtain trial transcripts and exhibits from court registry
2. Identify and finalise grounds of appeal
3. Lodge Notice of Intention to Appeal (within time limit)
4. Prepare detailed written submissions
5. Serve documents on the Crown/DPP
6. Attend the appeal hearing
For each step: what to do in plain English, required form name, time limit/deadline, and link to relevant court registry.
Then list all required forms in a table:
| Form/Document | Purpose | Where to Obtain | Filing Deadline |
Links: [Legal Aid {state_info.get('name', 'NSW')}]({state_info.get('legal_aid_url', 'https://www.legalaid.nsw.gov.au/')}) | [AustLII](https://www.austlii.edu.au/) | [Court Forms]({state_info.get('court_forms_url', '#')})

## 14. PRIORITISED ACTION PLAN
72-hour actions (urgent filings, time-sensitive steps).
7-day actions (evidence gathering, legal research).
28-day actions (submission drafting, hearing preparation).
Each action must specify what to do, who to contact, and the objective.

## 15. CLIENT PLAIN-ENGLISH BRIEF
THIS MUST BE THE FINAL SECTION. Translate the entire technical analysis into plain English that the defendant can understand:
- What is the appeal about in simple terms
- What are the chances of success and why
- What needs to happen next and in what order
- What are the realistic possible outcomes
- What the client should do right now

IMPORTANT:
- Use markdown headings and tables exactly where specified.
- Include working hyperlinks to AustLII and court websites.
- No cost discussion. No witness contradiction section.
- Quote supplied case material where possible.
- Keep analysis jurisdiction-specific to {state_info.get('name', 'NSW')} and relevant Commonwealth law.
- Every section must contain substantive content — no placeholders, no vague one-liners.
- NEVER use continuation markers like "... (continue)" or similar truncation. Write the ACTUAL content.
- Do NOT insert meta-commentary about the document itself. Only output the report content.
- Keep ALL outcome pathways within SECTION 7 — do NOT create separate ## headings for each outcome.
- Keep ALL action items (72-hour, 7-day, 28-day) within SECTION 14 — do NOT create separate ## headings for each timeframe."""

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

Target range 15000-20000 words. Every section must reference specific facts, documents, and dates from this case.

CRITICAL — NO REPETITION FROM FULL DETAILED REPORT:
The user already has a Full Detailed Report covering grounds analysis, sentencing table (8 cases), outcome options, evidence gaps, precedent matrix (10-12 cases), statutory framework, argument strategy, submissions blueprint, appeal steps, and action plan. This Premium Extensive report must ADVANCE BEYOND all of that with deeper per-ground analysis (900+ words each), expanded tables (12+ sentencing, 15+ precedents), and 5 ENTIRELY NEW sections: Hearing Preparation Notes, Conference Preparation Pack, Court Pathway Operations Playbook, Similar Case Search Options, and Risk Assessment + Contingency Planning. Do NOT copy or paraphrase content from the lower-tier reports.

SECTION ORDERING: Case-specific analysis first, then broader legal framework, then strategy, then practical steps, then client brief at the very end.

Use this exact structure:

## 1. EXECUTIVE BRIEF
Confident assessment of the appeal: strongest grounds with specific evidence anchors, jurisdiction posture, pathways to relief, urgency items, and a clear one-paragraph statement of the case. Include a case snapshot paragraph (defendant, offence, sentence, court, judge) and a short list of primary issues at the end.

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
Written submission strategy:
- Recommended argument sequence and why
- Authority placement for maximum impact
- Framing of each ground in written submissions
- Key passages to quote from case material

Oral submission strategy:
- Likely bench questions for each ground and prepared responses
- Time allocation per ground
- Opening and closing lines
- How to handle judicial scepticism on weaker grounds

## 13. HEARING PREPARATION NOTES
For each ground:
- Key talking points (dot points for quick reference)
- Anticipated questions from the bench and suggested answers
- Authority to cite first and why
- Visual aids or demonstratives to prepare
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
THIS MUST BE THE FINAL SECTION. Write this as if explaining directly to the defendant in everyday language:
- What the appeal is about and why it matters
- What are the strongest arguments in their favour (reference specific facts they know)
- What are the realistic chances of success
- What the different possible outcomes mean for them personally
- What they need to do right now, this week, and this month
- What to expect at the hearing
- Honest assessment of risks alongside the opportunities

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
        """Run LLM call directly — retries across multiple models."""
        from emergentintegrations.llm.chat import LlmChat, UserMessage
        
        # gpt-4o has intermittent refusals — retry multiple times
        # Same model order for all report types
        if report_type == "extensive_log":
            models = [
                ("openai", "gpt-4o"),
                ("openai", "gpt-4o"),
                ("openai", "gpt-4o"),
                ("openai", "gpt-4o"),
                ("openai", "gpt-4o-mini"),
                ("openai", "gpt-4o-mini"),
            ]
        else:
            models = [
                ("openai", "gpt-4o"),
                ("openai", "gpt-4o"),
                ("anthropic", "claude-sonnet-4-20250514"),
                ("openai", "gpt-4o-mini"),
            ]
        
        last_err = None
        for idx, (provider, model_name) in enumerate(models):
            try:
                chat = LlmChat(api_key=api_key, session_id="rpt_gen", system_message=system_prompt).with_model(provider, model_name).with_params(max_tokens=16384)
                result = await asyncio.wait_for(
                    chat.send_message(UserMessage(text=prompt_text)),
                    timeout=420
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
                last_err = f"Timeout after 180s with {provider}/{model_name}"
                logger.warning(last_err)
            except Exception as e:
                last_err = str(e)[:200]
                logger.warning(f"LLM attempt {idx+1} ({provider}/{model_name}) failed: {last_err}")
            await asyncio.sleep(3 + idx * 2)
        
        raise Exception(f"All LLM attempts failed. Last error: {last_err}")

    response = None
    last_error = None
    try:
        if report_type == "full_detailed":
            # Five-pass generation for full_detailed (3 sections per pass)
            passes = [
                ("PASS 1/5", """

NOW GENERATE ONLY SECTIONS 1-3. Write thorough, CASE-SPECIFIC legal analysis. MINIMUM 2000 WORDS for this pass. Every paragraph must name specific people, dates, documents, or legislation from this case. Do NOT write generic descriptions — DO the analysis.

## 1. EXECUTIVE BRIEF
## 2. FORENSIC CASE CHRONOLOGY
## 3. DOCUMENT EVIDENCE DIGEST

Write ALL 3 sections with specific case facts in every paragraph. STOP after section 3."""),
                ("PASS 2/5", """

NOW GENERATE ONLY SECTIONS 4-6. Write thorough, CASE-SPECIFIC legal analysis. MINIMUM 2000 WORDS for this pass. Section 4 MUST include EVERY ground listed in GROUNDS TO COVER, written as "Ground X: [Exact Title]" with 500+ words per ground. For the sentencing table, include full case citations and SPECIFIC factual comparisons to THIS case — not generic descriptions.

## 4. GROUNDS OF MERIT PORTFOLIO
## 5. COMPARATIVE SENTENCING TABLE (8+ CASES with full citations and specific factual parallels)
## 6. COMMON APPEAL GROUNDS FOR THIS OFFENCE TYPE

Write ALL 3 sections. STOP after section 6."""),
                ("PASS 3/5", """

NOW GENERATE ONLY SECTIONS 7-9. Write thorough, CASE-SPECIFIC legal analysis. MINIMUM 2000 WORDS for this pass. Apply every legal concept to THIS case's specific facts. Do NOT describe what analysis should be done — DO it.

## 7. OUTCOME OPTIONS AVAILABLE — keep ALL outcome pathways in this ONE section
## 8. EVIDENTIARY GAPS + REMEDIATION CHECKLIST
## 9. PRECEDENT OUTCOME MATRIX (10-12 CASES with full citations and factual parallels)

Write ALL 3 sections. STOP after section 9."""),
                ("PASS 4/5", """

NOW GENERATE ONLY SECTIONS 10-12. Write thorough, CASE-SPECIFIC legal analysis. MINIMUM 2000 WORDS for this pass. For the statutory framework, APPLY each provision to THIS case — do NOT just list what the Act covers generally. For submissions, write draft paragraphs ready for court.

## 10. STATUTORY + DOCTRINAL FRAMEWORK MAP (apply each provision to THIS case)
## 11. HOW TO ARGUE EACH TOP GROUND
## 12. SUBMISSIONS BLUEPRINT

Write ALL 3 sections. STOP after section 12."""),
                ("PASS 5/5", """

NOW GENERATE ONLY SECTIONS 13-15. Write thorough, CASE-SPECIFIC legal analysis. MINIMUM 2000 WORDS for this pass. Include specific court forms, filing deadlines, and explain everything in plain English for the client.

## 13. HOW TO START YOUR APPEAL + REQUIRED FORMS
## 14. PRIORITISED ACTION PLAN — keep ALL timeframes (72-hour, 7-day, 28-day) in this ONE section
## 15. CLIENT PLAIN-ENGLISH BRIEF

Write ALL 3 sections. Do NOT truncate any section."""),
            ]
            
            parts = []
            for label, instruction in passes:
                pass_prompt = user_prompt + instruction
                logger.info(f"Full detailed {label} prompt size: system={len(system_prompt)}, user={len(pass_prompt)}")
                part = await _subprocess_llm(pass_prompt)
                parts.append(part)
                logger.info(f"Full detailed {label} response: {len(part)} chars")
            
            response = "\n\n".join(parts)
            logger.info(f"Full detailed combined: {len(response)} chars")

        elif report_type == "extensive_log":
            # Seven-pass generation for extensive_log (3 sections per pass)
            passes = [
                ("PASS 1/7", """

NOW GENERATE ONLY SECTIONS 1-3. Write thorough, exhaustive, CASE-SPECIFIC legal analysis. MINIMUM 2000 WORDS for this pass. Every paragraph must name specific people, dates, documents, or legislation from this case. Do NOT write generic descriptions of what analysis should be done — DO the analysis.

## 1. EXECUTIVE BRIEF
## 2. FORENSIC CASE CHRONOLOGY
## 3. DOCUMENT EVIDENCE DIGEST

Write ALL 3 sections with specific case facts in every paragraph. STOP after section 3."""),
                ("PASS 2/7", """

NOW GENERATE ONLY SECTIONS 4-5. Write thorough, exhaustive, CASE-SPECIFIC legal analysis. MINIMUM 2000 WORDS for this pass. Section 4 requires 900+ words PER ground and MUST include EVERY ground listed in GROUNDS TO COVER, written as "Ground X: [Exact Title]" in flowing paragraphs (no bullet points or sub-headings within grounds).

## 4. GROUNDS OF MERIT — DEEP ANALYSIS (900+ words per ground, flowing paragraphs)
## 5. COMPARATIVE SENTENCING TABLE (12+ CASES with full citations and specific factual comparisons)

Write BOTH sections with deep case-specific analysis. STOP after section 5."""),
                ("PASS 3/7", """

NOW GENERATE ONLY SECTIONS 6-8. Write thorough, exhaustive, CASE-SPECIFIC legal analysis. MINIMUM 2000 WORDS for this pass. Apply every provision to THIS case's facts. Do NOT just describe what the law says — explain how it applies to Homann specifically.

## 6. COMMON APPEAL GROUNDS FOR THIS OFFENCE TYPE
## 7. OUTCOME OPTIONS — DETAILED PATHWAY ANALYSIS — keep ALL pathways in this ONE section
## 8. EVIDENTIARY GAPS + REMEDIATION CHECKLIST

Write ALL 3 sections. STOP after section 8."""),
                ("PASS 4/7", """

NOW GENERATE ONLY SECTIONS 9-11. Write thorough, exhaustive, CASE-SPECIFIC legal analysis. MINIMUM 2000 WORDS for this pass. For the precedent matrix, include full citations and explain the SPECIFIC factual parallel to Homann's case for each. For the statutory framework, APPLY each provision to THIS case — do NOT just list what the Act covers generally.

## 9. PRECEDENT OUTCOME MATRIX (15+ CASES with full citations and factual parallels)
## 10. STATUTORY + DOCTRINAL FRAMEWORK MAP (apply each provision to THIS case specifically)
## 11. HOW TO ARGUE EACH TOP GROUND — DETAILED STRATEGY

Write ALL 3 sections. STOP after section 11."""),
                ("PASS 5/7", """

NOW GENERATE ONLY SECTIONS 12-14. Write thorough, exhaustive, CASE-SPECIFIC legal analysis. MINIMUM 2000 WORDS for this pass. These are practical hearing-ready sections — include draft submission paragraphs, specific questions to prepare for, and conference agenda items tied to THIS case.

## 12. SUBMISSIONS BLUEPRINT
## 13. HEARING PREPARATION NOTES
## 14. CONFERENCE PREPARATION PACK

Write ALL 3 sections. STOP after section 14."""),
                ("PASS 6/7", """

NOW GENERATE ONLY SECTIONS 15-17. Write thorough, exhaustive, CASE-SPECIFIC legal analysis. MINIMUM 2000 WORDS for this pass. Include specific court forms, filing deadlines for NSW, and similar case search strategies tied to THIS case's facts.

## 15. COURT PATHWAY OPERATIONS PLAYBOOK
## 16. HOW TO START YOUR APPEAL + REQUIRED FORMS
## 17. SIMILAR CASE SEARCH OPTIONS

Write ALL 3 sections. STOP after section 17."""),
                ("PASS 7/7", """

NOW GENERATE ONLY SECTIONS 18-20. Write thorough, exhaustive, CASE-SPECIFIC legal analysis. MINIMUM 2000 WORDS for this pass. The action plan must have specific deadlines. The risk assessment must address specific weaknesses in THIS case. The plain-English brief must explain the specific grounds and their implications to the client.

## 18. PRIORITISED ACTION PLAN — keep ALL timeframes in this ONE section
## 19. RISK ASSESSMENT + CONTINGENCY PLANNING
## 20. CLIENT PLAIN-ENGLISH BRIEF

Write ALL 3 sections. Do NOT truncate any section."""),
            ]
            
            parts = []
            for label, instruction in passes:
                pass_prompt = user_prompt + instruction
                logger.info(f"Extensive log {label} prompt size: system={len(system_prompt)}, user={len(pass_prompt)}")
                part = await _subprocess_llm(pass_prompt)
                parts.append(part)
                logger.info(f"Extensive log {label} response: {len(part)} chars")
            
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
        "full_detailed": 50000,
        "extensive_log": 95000
    }
    target_length = min_lengths.get(report_type, 12000)
    if aggressive_mode:
        target_length = int(target_length * 2.0)

    if len(response) < target_length:
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

    # Parse response to extract grounds of merit
    grounds_of_merit = []
    if "GROUNDS OF MERIT" in response or "Ground" in response:
        grounds_of_merit = [{
            "title": "AI-Identified Ground",
            "description": "See full report for details",
            "strength": "To be assessed by legal professional"
        }]
    
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

async def _run_report_generation(report_id: str, case_id: str, user_id: str, report_type: str, aggressive_mode: bool):
    """Background task that generates the AI report and updates the DB record."""
    try:
        report_titles = {
            "quick_summary": "Quick Case Summary",
            "full_detailed": "Full Detailed Legal Analysis",
            "extensive_log": "Extensive Case Log & Analysis"
        }
        analysis_result = await analyze_case_with_ai(case_id, user_id, report_type, aggressive_mode)
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
        await db.reports.update_one(
            {"report_id": report_id},
            {"$set": {"status": "failed", "error": str(exc)}}
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
            "feature_type": "full_report",
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
            "feature_type": "extensive_report",
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
    
    # Create a placeholder report with "generating" status and return immediately
    report_id = f"rpt_{uuid.uuid4().hex[:12]}"
    report_titles = {
        "quick_summary": "Quick Case Summary",
        "full_detailed": "Full Detailed Legal Analysis",
        "extensive_log": "Extensive Case Log & Analysis"
    }
    title = report_titles.get(report_type, "Report")
    if report_request.aggressive_mode:
        title = f"{title} (Aggressive)"
    placeholder = {
        "report_id": report_id,
        "case_id": case_id,
        "user_id": user.user_id,
        "report_type": report_type,
        "title": title,
        "content": {"analysis": "", "aggressive_mode": report_request.aggressive_mode},
        "grounds_of_merit": [],
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "status": "generating",
    }
    insert_doc = {k: v for k, v in placeholder.items()}
    await db.reports.insert_one(insert_doc)

    # Fire-and-forget background task
    asyncio.create_task(
        _run_report_generation(report_id, case_id, user.user_id, report_type, report_request.aggressive_mode)
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
    
    # Auto-fail any report stuck in "generating" for more than 30 minutes
    thirty_min_ago = (datetime.now(timezone.utc) - timedelta(minutes=30)).isoformat()
    await db.reports.update_many(
        {"case_id": case_id, "user_id": user.user_id, "status": "generating", "generated_at": {"$lt": thirty_min_ago}},
        {"$set": {"status": "failed", "error": "Generation timed out"}}
    )
    
    reports = await db.reports.find(
        {"case_id": case_id, "user_id": user.user_id},
        {"_id": 0}
    ).sort("generated_at", -1).to_list(100)
    
    return reports


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
        bottomMargin=20*mm
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
        textColor=colors.HexColor('#92400e')
    ))

    def format_inline(text: str) -> str:
        clean = (text or "").replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        clean = re.sub(r"\*\*(.*?)\*\*", r"<b>\\1</b>", clean)
        return clean

    def render_table(lines):
        rows = []
        for line in lines:
            parts = [p.strip() for p in line.strip().strip("|").split("|")]
            if not parts:
                continue
            if all(set(p) <= set("-:") for p in parts):
                continue
            rows.append([re.sub(r"\*\*(.*?)\*\*", r"\\1", p) for p in parts])
        if not rows:
            return
        col_count = max(len(r) for r in rows)
        rows = [r + [""] * (col_count - len(r)) for r in rows]
        col_width = doc.width / col_count
        table = Table(rows, colWidths=[col_width] * col_count, repeatRows=1)
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1e293b')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#cbd5e1')),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.whitesmoke, colors.white])
        ]))
        story.append(table)
        story.append(Spacer(1, 4*mm))

    def render_markdown(text: str):
        lines = (text or "").splitlines()
        buffer = []
        table_lines = []

        def flush_paragraph():
            if buffer:
                paragraph = " ".join(buffer).strip()
                if paragraph:
                    story.append(Paragraph(format_inline(paragraph), styles['ReportBodyText']))
                    story.append(Spacer(1, 2*mm))
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
            if stripped.startswith("### "):
                flush_paragraph()
                story.append(Paragraph(format_inline(stripped[4:].strip()), styles['SubHeader']))
                story.append(Spacer(1, 1*mm))
                continue
            if stripped.startswith("- ") or stripped.startswith("• "):
                flush_paragraph()
                bullet_text = stripped[2:].strip()
                story.append(Paragraph(f"• {format_inline(bullet_text)}", styles['BulletText']))
                story.append(Spacer(1, 1*mm))
                continue
            buffer.append(stripped)

        flush_paragraph()
        if table_lines:
            render_table(table_lines)

    story = []
    
    # Header
    story.append(Paragraph("Criminal Law Appeal Case Management by Deb King GLENMORE PARK NSW", styles['ReportSubtitle']))
    story.append(Paragraph(f"Case: {case.get('title', 'Unknown')}", styles['ReportSubtitle']))
    story.append(Paragraph(f"Defendant: {case.get('defendant_name', 'Unknown')}", styles['ReportSubtitle']))
    story.append(Spacer(1, 10*mm))
    
    # Report Title
    report_type_labels = {
        'quick_summary': 'Quick Case Summary',
        'full_detailed': 'Full Detailed Legal Analysis',
        'extensive_log': 'Extensive Case Log & Analysis'
    }
    title = report_type_labels.get(report.get('report_type'), 'Legal Report')
    if report.get('content', {}).get('aggressive_mode'):
        title = f"{title} (Aggressive)"
    story.append(Paragraph(title, styles['ReportTitle']))
    story.append(Spacer(1, 5*mm))
    
    # Case Info Table
    case_data_table = [
        ['Case Title:', case.get('title', 'N/A')],
        ['Defendant:', case.get('defendant_name', 'N/A')],
        ['Case Number:', case.get('case_number', 'N/A') or 'N/A'],
        ['Court:', case.get('court', 'N/A') or 'N/A'],
        ['Generated:', report.get('generated_at', 'N/A')[:10] if report.get('generated_at') else 'N/A']
    ]
    
    case_table = Table(case_data_table, colWidths=[40*mm, 120*mm])
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
                    story.append(Paragraph(section_text, styles['LawSection']))
            
            # Similar Cases
            if ground.get('similar_cases'):
                story.append(Paragraph("<b>Similar Cases:</b>", styles['ReportBodyText']))
                for case_ref in ground.get('similar_cases', []):
                    case_text = f"• {case_ref.get('case_name', '')} {case_ref.get('citation', '')}"
                    story.append(Paragraph(case_text, styles['LawSection']))
            
            # Supporting Evidence
            if ground.get('supporting_evidence'):
                story.append(Paragraph("<b>Supporting Evidence:</b>", styles['ReportBodyText']))
                for evidence in ground.get('supporting_evidence', []):
                    story.append(Paragraph(f"• {evidence}", styles['LawSection']))
            
            story.append(Spacer(1, 5*mm))
    
    # Legal Framework Reference
    story.append(Paragraph("LEGAL FRAMEWORK REFERENCE", styles['SectionHeader']))
    legal_refs = [
        "• Crimes Act 1900 (NSW) - Primary criminal law for NSW",
        "• Criminal Appeal Act 1912 (NSW) - Governs appeals in NSW",
        "• Criminal Code Act 1995 (Cth) - Federal criminal law",
        "• Evidence Act 1995 (NSW & Cth) - Evidence admissibility",
        "• Sentencing Act 1995 (NSW) - Sentencing guidelines"
    ]
    for ref in legal_refs:
        story.append(Paragraph(ref, styles['LawSection']))
    
    story.append(Spacer(1, 10*mm))
    
    # Main Analysis Content
    story.append(Paragraph("DETAILED ANALYSIS", styles['SectionHeader']))

    analysis_text = _strip_report_placeholders(report.get('content', {}).get('analysis', 'No analysis available.'))
    render_markdown(analysis_text)

    # Footer disclaimer
    story.append(Spacer(1, 15*mm))
    story.append(Paragraph(
        "Criminal Law Appeal Case Management by Deb King GLENMORE PARK NSW",
        ParagraphStyle(
            name='Disclaimer',
            fontSize=8,
            textColor=colors.grey,
            alignment=TA_CENTER
        )
    ))
    
    # Build PDF
    doc.build(story)
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
    h2_style.font.color.rgb = RGBColor(146, 64, 14)
    
    # Header
    header_para = doc.add_paragraph()
    header_para.alignment = WD_ALIGN_PARAGRAPH.CENTER
    header_run = header_para.add_run("APPEAL CASE MANAGER")
    header_run.font.size = Pt(14)
    header_run.font.bold = True
    header_run.font.color.rgb = RGBColor(15, 23, 42)

    sub_header = doc.add_paragraph()
    sub_header.alignment = WD_ALIGN_PARAGRAPH.CENTER
    sub_run = sub_header.add_run("Criminal Law Appeal Case Management by Deb King GLENMORE PARK NSW")
    sub_run.font.size = Pt(11)
    sub_run.font.color.rgb = RGBColor(71, 85, 105)

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
        'extensive_log': 'Extensive Case Log & Analysis'
    }
    report_title = report_type_labels.get(report.get('report_type'), 'Legal Report')
    if report.get('content', {}).get('aggressive_mode'):
        report_title = f"{report_title} (Aggressive)"
    title = doc.add_heading(report_title, 0)
    title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    
    doc.add_paragraph()
    
    # Case Information Table
    case_table = doc.add_table(rows=5, cols=2)
    case_table.style = 'Table Grid'
    
    case_info = [
        ('Case Title:', case.get('title', 'N/A')),
        ('Defendant:', case.get('defendant_name', 'N/A')),
        ('Case Number:', case.get('case_number', 'N/A') or 'N/A'),
        ('Court:', case.get('court', 'N/A') or 'N/A'),
        ('Generated:', report.get('generated_at', 'N/A')[:10] if report.get('generated_at') else 'N/A')
    ]
    
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
                cases_run.font.color.rgb = RGBColor(146, 64, 14)
                
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
        for r_idx, row in enumerate(rows):
            for c_idx, value in enumerate(row):
                cell = table.cell(r_idx, c_idx)
                cell.text = value.replace('**', '')
                if r_idx == 0:
                    for run in cell.paragraphs[0].runs:
                        run.bold = True
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
    disclaimer = doc.add_paragraph()
    disclaimer.alignment = WD_ALIGN_PARAGRAPH.CENTER
    disclaimer_run = disclaimer.add_run(
        "Criminal Law Appeal Case Management by Deb King GLENMORE PARK NSW"
    )
    disclaimer_run.font.size = Pt(9)
    disclaimer_run.font.italic = True
    disclaimer_run.font.color.rgb = RGBColor(100, 116, 139)
    
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

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()
