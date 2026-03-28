# DO NOT UNDO — All models in this file are approved and must be preserved.
"""
Criminal Appeal AI - Pydantic Models
"""
from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional
from datetime import datetime, timezone
import uuid
import secrets


# ============ USER MODELS ============

class User(BaseModel):
    model_config = ConfigDict(extra="ignore")
    user_id: str
    email: str
    name: str
    picture: Optional[str] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


# ============ CASE MODELS ============

class Case(BaseModel):
    model_config = ConfigDict(extra="ignore")
    case_id: str = Field(default_factory=lambda: f"case_{uuid.uuid4().hex[:12]}")
    user_id: str
    title: str
    defendant_name: str
    case_number: Optional[str] = None
    court: Optional[str] = None
    judge: Optional[str] = None
    state: str = "nsw"
    offence_category: str = "homicide"
    offence_type: Optional[str] = None
    sentence: Optional[str] = None
    status: str = "active"
    summary: Optional[str] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class CaseCreate(BaseModel):
    model_config = ConfigDict(extra="ignore")
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


# ============ DOCUMENT MODELS ============

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


class DocumentSearchRequest(BaseModel):
    query: str
    category: Optional[str] = None
    match_all: bool = False


class SearchMatch(BaseModel):
    document_id: str
    filename: str
    category: str
    matches: List[dict]
    relevance_score: float


# ============ TIMELINE MODELS ============

class TimelineEvent(BaseModel):
    model_config = ConfigDict(extra="ignore")
    event_id: str = Field(default_factory=lambda: f"evt_{uuid.uuid4().hex[:12]}")
    case_id: str
    user_id: str
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


# ============ GROUNDS OF MERIT MODELS ============

class GroundOfMerit(BaseModel):
    model_config = ConfigDict(extra="ignore")
    ground_id: str = Field(default_factory=lambda: f"gnd_{uuid.uuid4().hex[:12]}")
    case_id: str
    user_id: str
    title: str
    ground_type: str
    description: str
    strength: str = "moderate"
    status: str = "identified"
    supporting_evidence: List[str] = []
    law_sections: List[dict] = []
    similar_cases: List[dict] = []
    analysis: Optional[str] = None
    deep_analysis: Optional[dict] = None
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


# ============ REPORT MODELS ============

class ReportRequest(BaseModel):
    report_type: str = "quick_summary"


class Report(BaseModel):
    model_config = ConfigDict(extra="ignore")
    report_id: str = Field(default_factory=lambda: f"rpt_{uuid.uuid4().hex[:12]}")
    case_id: str
    user_id: str
    report_type: str
    title: str
    content: dict
    grounds_of_merit: List[dict] = []
    generated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


# ============ NOTE MODELS ============

class Note(BaseModel):
    model_config = ConfigDict(extra="ignore")
    note_id: str = Field(default_factory=lambda: f"note_{uuid.uuid4().hex[:12]}")
    case_id: str
    user_id: str
    author_name: str
    author_email: str
    category: str = "general"
    title: str
    content: str
    is_pinned: bool = False
    document_id: Optional[str] = None
    report_id: Optional[str] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class NoteCreate(BaseModel):
    category: str = "general"
    title: str
    content: str
    is_pinned: bool = False
    document_id: Optional[str] = None
    report_id: Optional[str] = None


class NoteUpdate(BaseModel):
    category: Optional[str] = None
    title: Optional[str] = None
    content: Optional[str] = None
    is_pinned: Optional[bool] = None



# ============ SHARING MODELS ============

class CaseShare(BaseModel):
    model_config = ConfigDict(extra="ignore")
    share_id: str = Field(default_factory=lambda: f"share_{uuid.uuid4().hex[:12]}")
    case_id: str
    owner_id: str
    shared_with_user_id: Optional[str] = None
    shared_with_email: str
    permission: str = "view_comment"  # view_comment = view + add notes/comments
    status: str = "pending"  # pending, accepted, revoked
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class ShareLink(BaseModel):
    model_config = ConfigDict(extra="ignore")
    link_id: str = Field(default_factory=lambda: f"slink_{uuid.uuid4().hex[:12]}")
    case_id: str
    owner_id: str
    token: str = Field(default_factory=lambda: secrets.token_urlsafe(32))
    permission: str = "view_comment"
    is_active: bool = True
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    expires_at: Optional[datetime] = None


class CaseMessage(BaseModel):
    model_config = ConfigDict(extra="ignore")
    message_id: str = Field(default_factory=lambda: f"msg_{uuid.uuid4().hex[:12]}")
    case_id: str
    user_id: str
    author_name: str
    author_email: str
    content: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class Notification(BaseModel):
    model_config = ConfigDict(extra="ignore")
    notification_id: str = Field(default_factory=lambda: f"notif_{uuid.uuid4().hex[:12]}")
    user_id: str
    type: str  # share_invite, new_message, new_note, case_update
    title: str
    message: str
    case_id: Optional[str] = None
    from_user_name: Optional[str] = None
    is_read: bool = False
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class Activity(BaseModel):
    model_config = ConfigDict(extra="ignore")
    activity_id: str = Field(default_factory=lambda: f"act_{uuid.uuid4().hex[:12]}")
    case_id: str
    user_id: str
    user_name: str
    action: str  # shared_case, added_note, sent_message, viewed_case, added_document
    detail: str = ""
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))



# ============ DEADLINE MODELS ============

class Deadline(BaseModel):
    model_config = ConfigDict(extra="ignore")
    deadline_id: str = Field(default_factory=lambda: f"dl_{uuid.uuid4().hex[:12]}")
    case_id: str
    user_id: str
    title: str
    description: str = ""
    deadline_type: str
    due_date: datetime
    reminder_days: List[int] = [7, 3, 1]
    is_completed: bool = False
    completed_at: Optional[datetime] = None
    priority: str = "high"
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
    phase: str
    title: str
    description: str = ""
    is_completed: bool = False
    completed_at: Optional[datetime] = None
    order: int = 0
    is_custom: bool = False
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


# Default checklist items for new cases
DEFAULT_CHECKLIST = [
    {"phase": "preparation", "title": "Gather all case documents", "description": "Collect court transcripts, evidence briefs, witness statements, and any other relevant documents", "order": 1},
    {"phase": "preparation", "title": "Upload documents to system", "description": "Upload all gathered documents and extract text for AI analysis", "order": 2},
    {"phase": "preparation", "title": "Build case timeline", "description": "Create chronological timeline of events from arrest to conviction", "order": 3},
    {"phase": "preparation", "title": "Review trial transcript", "description": "Read through the full trial transcript noting any issues", "order": 4},
    {"phase": "grounds_identification", "title": "Run AI grounds identification", "description": "Use AI to identify potential grounds of merit from your documents", "order": 5},
    {"phase": "grounds_identification", "title": "Review identified grounds", "description": "Assess each ground identified by AI for viability", "order": 6},
    {"phase": "grounds_identification", "title": "Check witness statement inconsistencies", "description": "Use contradiction finder to identify issues in witness testimony", "order": 7},
    {"phase": "grounds_identification", "title": "Identify any fresh evidence", "description": "Document any new evidence not available at trial", "order": 8},
    {"phase": "investigation", "title": "Deep investigate each ground", "description": "Use AI investigation feature on each viable ground", "order": 9},
    {"phase": "investigation", "title": "Research relevant case law", "description": "Find similar appeal cases and their outcomes", "order": 10},
    {"phase": "investigation", "title": "Identify relevant law sections", "description": "Document NSW and Federal law sections that apply", "order": 11},
    {"phase": "investigation", "title": "Assess case strength", "description": "Review case strength meter and prioritise strongest grounds", "order": 12},
    {"phase": "documentation", "title": "Generate detailed report", "description": "Create Full Detailed report with all grounds and analysis", "order": 13},
    {"phase": "documentation", "title": "Prepare Notice of Appeal", "description": "Draft Notice of Appeal using template", "order": 14},
    {"phase": "documentation", "title": "Prepare supporting affidavit", "description": "Draft affidavit if required for fresh evidence", "order": 15},
    {"phase": "documentation", "title": "Review all documents", "description": "Final review of all appeal documents for accuracy", "order": 16},
    {"phase": "lodgement", "title": "Consult with legal professional", "description": "Have documents reviewed by solicitor or barrister", "order": 17},
    {"phase": "lodgement", "title": "File Notice of Appeal", "description": "Lodge appeal within 28 days of conviction/sentence", "order": 18},
    {"phase": "lodgement", "title": "File Leave application (if required)", "description": "Lodge application for leave to appeal if needed", "order": 19},
    {"phase": "lodgement", "title": "Confirm lodgement receipt", "description": "Obtain confirmation that appeal has been filed", "order": 20},
    {"phase": "hearing", "title": "Prepare for hearing", "description": "Review all materials before appeal hearing", "order": 21},
    {"phase": "hearing", "title": "Generate Barrister View report", "description": "Create professional presentation for court", "order": 22},
]
