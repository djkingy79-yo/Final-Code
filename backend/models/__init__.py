#  — All models in this file are approved and must be preserved.
"""
Criminal Appeal AI - Pydantic Models
HARDENED / ADDITIVE PATCH
"""
from pydantic import BaseModel, Field, ConfigDict, field_validator
from typing import List, Optional, Literal
from datetime import datetime, timezone
import uuid
import secrets


# ============================================================================
# SHARED TYPES / ENUM-LIKE LITERALS
# ============================================================================

StateType = Literal["nsw", "vic", "qld", "sa", "wa", "tas", "nt", "act", "federal"]

OffenceCategoryType = Literal[
    "homicide",
    "assault",
    "sexual_offences",
    "robbery_theft",
    "drug_offences",
    "fraud_dishonesty",
    "firearms_weapons",
    "domestic_violence",
    "public_order",
    "terrorism",
    "driving_offences",
]

GroundType = Literal[
    "procedural_error",
    "fresh_evidence",
    "miscarriage_of_justice",
    "sentencing_error",
    "judicial_error",
    "ineffective_counsel",
    "prosecution_misconduct",
    "jury_irregularity",
    "constitutional_violation",
    "other",
]

StrengthType = Literal["strong", "moderate", "weak"]

GroundStatusType = Literal[
    "identified",
    "investigated",
    "confirmed",
    "needs_review",
    "dismissed",
]

PriorityType = Literal["low", "medium", "high", "urgent"]

ChecklistPhaseType = Literal[
    "preparation",
    "grounds_identification",
    "investigation",
    "documentation",
    "lodgement",
    "hearing",
]

VerificationStatusType = Literal[
    "unverified",
    "draft",
    "reviewed",
    "verified",
]

SourceModeType = Literal[
    "default",
    "ai_generated",
    "ai_detected",
    "manual",
    "imported",
    "user_set",
    "verified",
]

TimelineSignificanceType = Literal["low", "normal", "important", "critical"]

TimelinePerspectiveType = Literal["neutral", "defence", "prosecution", "court"]

CaseStatusType = Literal["active", "archived", "closed"]

SharePermissionType = Literal["view_comment"]

ShareStatusType = Literal["pending", "accepted", "revoked"]

NotificationType = Literal["share_invite", "new_message", "new_note", "case_update"]

ActivityActionType = Literal[
    "shared_case",
    "added_note",
    "sent_message",
    "viewed_case",
    "added_document",
]

PaymentStatusType = Literal["pending", "completed", "failed", "refunded"]

EvidenceRoleType = Literal["supports", "undermines", "contextual"]


# ============================================================================
# SHARED SUBMODELS
# ============================================================================

class EvidenceItem(BaseModel):
    model_config = ConfigDict(extra="ignore")
    document_id: Optional[str] = None
    filename: Optional[str] = None
    quote: str = ""
    page_reference: Optional[str] = None
    chunk_reference: Optional[str] = None
    confidence: StrengthType = "moderate"
    role: EvidenceRoleType = "supports"
    source_mode: SourceModeType = "ai_generated"
    verification_status: VerificationStatusType = "unverified"


class LawSection(BaseModel):
    model_config = ConfigDict(extra="ignore")
    act: str
    section: str
    jurisdiction: Optional[StateType] = None
    title: Optional[str] = None
    verification_status: VerificationStatusType = "unverified"


class SimilarCase(BaseModel):
    model_config = ConfigDict(extra="ignore")
    case_name: str
    citation: Optional[str] = None
    jurisdiction: Optional[StateType] = None
    relevance_note: Optional[str] = None
    verification_status: VerificationStatusType = "unverified"


class LegitimacyScores(BaseModel):
    model_config = ConfigDict(extra="ignore")
    legal_score: int = 0
    evidence_score: int = 0
    viability_score: int = 0
    total_score: int = 0
    rating: StrengthType = "moderate"
    confidence_note: str = ""


class ReportMetadata(BaseModel):
    model_config = ConfigDict(extra="ignore")
    generated_by_model: Optional[str] = None
    fallback_used: bool = False
    documents_analyzed: int = 0
    timeline_events_analyzed: int = 0
    grounds_considered: int = 0
    verification_status: VerificationStatusType = "draft"
    confidence_note: str = ""


# ============================================================================
# USER MODELS
# ============================================================================

class User(BaseModel):
    model_config = ConfigDict(extra="ignore")
    user_id: str
    email: str
    name: str
    picture: Optional[str] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


# ============================================================================
# CASE MODELS
# ============================================================================

class Case(BaseModel):
    model_config = ConfigDict(extra="ignore")
    case_id: str = Field(default_factory=lambda: f"case_{uuid.uuid4().hex[:12]}")
    user_id: str
    title: str
    defendant_name: str
    case_number: Optional[str] = None
    court: Optional[str] = None
    judge: Optional[str] = None
    state: Optional[StateType] = None                        #  — must be None for auto-detect
    offence_category: Optional[OffenceCategoryType] = None   #  — must be None for auto-detect
    offence_type: Optional[str] = None                       #  — must be None for auto-detect
    sentence: Optional[str] = None                           #  — must be None for auto-detect
    status: CaseStatusType = "active"
    summary: Optional[str] = None

    # ADDITIVE provenance / reliability fields
    classification_source: SourceModeType = "default"
    requires_metadata_review: bool = False
    verification_status: VerificationStatusType = "unverified"

    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


# ==========================================================================
#  — AUTO-DETECT PROTECTION
# ==========================================================================
# state and offence_category MUST remain Optional = None.
# DO NOT add default values like "nsw" or "homicide".
# DO NOT change these back to required fields.
# DO NOT add Field(default=...) with any non-None value.
# The background task _background_auto_detect_metadata in
# routers/documents.py detects these from uploaded documents via LLM.
# If you set defaults here, auto-detection breaks and every case
# shows "NSW / Murder" regardless of the actual documents.
# This has been broken and re-fixed 15+ times. LEAVE IT ALONE.
# ==========================================================================
class CaseCreate(BaseModel):
    model_config = ConfigDict(extra="ignore")
    title: str
    defendant_name: str
    case_number: Optional[str] = None
    court: Optional[str] = None
    judge: Optional[str] = None
    state: Optional[StateType] = None                        #  — must be None for auto-detect
    offence_category: Optional[OffenceCategoryType] = None   #  — must be None for auto-detect
    offence_type: Optional[str] = None                       #  — must be None for auto-detect
    sentence: Optional[str] = None                           #  — must be None for auto-detect
    summary: Optional[str] = None

    #  — Converts empty strings to None so enum validation doesn't reject them
    @field_validator("state", "offence_category", "offence_type", "sentence", "summary", "case_number", "court", "judge", mode="before")
    @classmethod
    def empty_str_to_none(cls, v):
        if isinstance(v, str) and v.strip() == "":
            return None
        return v


# ============================================================================
# DOCUMENT MODELS
# ============================================================================

class Document(BaseModel):
    model_config = ConfigDict(extra="ignore")
    document_id: str = Field(default_factory=lambda: f"doc_{uuid.uuid4().hex[:12]}")
    case_id: str
    user_id: str
    filename: str
    file_type: str
    category: str
    description: Optional[str] = None
    content_text: Optional[str] = None
    file_data: Optional[str] = None
    event_date: Optional[datetime] = None

    # ADDITIVE provenance fields
    extraction_method: Optional[str] = None
    extraction_confidence: Optional[StrengthType] = None
    source_mode: SourceModeType = "manual"
    verification_status: VerificationStatusType = "unverified"

    uploaded_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


# ============================================================================
# TIMELINE MODELS
# ============================================================================

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
    linked_documents: List[str] = Field(default_factory=list)
    participants: List[dict] = Field(default_factory=list)
    significance: TimelineSignificanceType = "normal"
    source_citation: str = ""
    perspective: TimelinePerspectiveType = "neutral"
    is_contested: bool = False
    contested_details: str = ""
    related_grounds: List[str] = Field(default_factory=list)
    inconsistency_notes: str = ""

    # ADDITIVE provenance fields
    source_mode: SourceModeType = "ai_generated"
    verification_status: VerificationStatusType = "unverified"

    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class TimelineEventCreate(BaseModel):
    title: str
    description: str
    event_date: datetime
    event_type: str
    event_category: str = "general"
    linked_documents: List[str] = Field(default_factory=list)
    participants: List[dict] = Field(default_factory=list)
    significance: TimelineSignificanceType = "normal"
    source_citation: str = ""
    perspective: TimelinePerspectiveType = "neutral"
    is_contested: bool = False
    contested_details: str = ""
    related_grounds: List[str] = Field(default_factory=list)
    inconsistency_notes: str = ""


# ============================================================================
# GROUNDS OF MERIT MODELS
# ============================================================================

class GroundOfMerit(BaseModel):
    model_config = ConfigDict(extra="ignore")
    ground_id: str = Field(default_factory=lambda: f"gnd_{uuid.uuid4().hex[:12]}")
    case_id: str
    user_id: str
    title: str
    ground_type: GroundType
    description: str
    strength: StrengthType = "moderate"
    status: GroundStatusType = "identified"

    # HARDENED structured fields
    supporting_evidence: List[EvidenceItem] = Field(default_factory=list)
    law_sections: List[LawSection] = Field(default_factory=list)
    similar_cases: List[SimilarCase] = Field(default_factory=list)

    analysis: Optional[str] = None
    deep_analysis: Optional[dict] = None

    # ADDITIVE reliability / legitimacy fields
    legitimacy_scores: Optional[LegitimacyScores] = None
    source_mode: SourceModeType = "ai_generated"
    requires_human_review: bool = True
    verified_by: Optional[str] = None
    verified_at: Optional[datetime] = None
    verification_status: VerificationStatusType = "unverified"

    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class GroundOfMeritCreate(BaseModel):
    title: str
    ground_type: GroundType = "other"
    description: str
    strength: StrengthType = "moderate"
    supporting_evidence: List[EvidenceItem] = Field(default_factory=list)


class GroundOfMeritUpdate(BaseModel):
    title: Optional[str] = None
    ground_type: Optional[GroundType] = None
    description: Optional[str] = None
    strength: Optional[StrengthType] = None
    status: Optional[GroundStatusType] = None
    supporting_evidence: Optional[List[EvidenceItem]] = None


# ============================================================================
# REPORT MODELS
# ============================================================================

class ReportRequest(BaseModel):
    report_type: str = "quick_summary"
    aggressive_mode: bool = False


class Report(BaseModel):
    model_config = ConfigDict(extra="ignore")
    report_id: str = Field(default_factory=lambda: f"rpt_{uuid.uuid4().hex[:12]}")
    case_id: str
    user_id: str
    report_type: str
    title: str
    content: dict
    grounds_of_merit: List[dict] = Field(default_factory=list)

    # ADDITIVE report envelope
    metadata: Optional[ReportMetadata] = None
    source_mode: SourceModeType = "ai_generated"
    verification_status: VerificationStatusType = "draft"

    generated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


# ============================================================================
# NOTE MODELS
# ============================================================================

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
    mentions: List[str] = Field(default_factory=list)
    comments: List[dict] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class NoteCreate(BaseModel):
    category: str = "general"
    title: str
    content: str
    is_pinned: bool = False
    document_id: Optional[str] = None
    report_id: Optional[str] = None
    mentions: List[str] = Field(default_factory=list)


class NoteUpdate(BaseModel):
    category: Optional[str] = None
    title: Optional[str] = None
    content: Optional[str] = None
    is_pinned: Optional[bool] = None


class NoteCommentCreate(BaseModel):
    content: str


# ============================================================================
# SHARING MODELS
# ============================================================================

class CaseShare(BaseModel):
    model_config = ConfigDict(extra="ignore")
    share_id: str = Field(default_factory=lambda: f"share_{uuid.uuid4().hex[:12]}")
    case_id: str
    owner_id: str
    shared_with_user_id: Optional[str] = None
    shared_with_email: str
    permission: SharePermissionType = "view_comment"
    status: ShareStatusType = "pending"
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class ShareLink(BaseModel):
    model_config = ConfigDict(extra="ignore")
    link_id: str = Field(default_factory=lambda: f"slink_{uuid.uuid4().hex[:12]}")
    case_id: str
    owner_id: str
    token: str = Field(default_factory=lambda: secrets.token_urlsafe(32))
    permission: SharePermissionType = "view_comment"
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
    type: NotificationType
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
    action: ActivityActionType
    detail: str = ""
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


# ============================================================================
# DEADLINE MODELS
# ============================================================================

class Deadline(BaseModel):
    model_config = ConfigDict(extra="ignore")
    deadline_id: str = Field(default_factory=lambda: f"dl_{uuid.uuid4().hex[:12]}")
    case_id: str
    user_id: str
    title: str
    description: str = ""
    deadline_type: str
    due_date: datetime
    reminder_days: List[int] = Field(default_factory=lambda: [7, 3, 1])
    is_completed: bool = False
    completed_at: Optional[datetime] = None
    priority: PriorityType = "high"

    # ADDITIVE localisation / provenance
    jurisdiction: Optional[StateType] = None
    is_jurisdiction_default: bool = True
    source_mode: SourceModeType = "manual"
    verification_status: VerificationStatusType = "unverified"

    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class DeadlineCreate(BaseModel):
    title: str
    description: str = ""
    deadline_type: str = "other"
    due_date: datetime
    reminder_days: List[int] = Field(default_factory=lambda: [7, 3, 1])
    priority: PriorityType = "high"


# ============================================================================
# CHECKLIST MODELS
# ============================================================================

class ChecklistItem(BaseModel):
    model_config = ConfigDict(extra="ignore")
    item_id: str = Field(default_factory=lambda: f"chk_{uuid.uuid4().hex[:12]}")
    case_id: str
    user_id: str
    phase: ChecklistPhaseType
    title: str
    description: str = ""
    is_completed: bool = False
    completed_at: Optional[datetime] = None
    order: int = 0
    is_custom: bool = False

    # ADDITIVE localisation / provenance
    jurisdiction: Optional[StateType] = None
    is_jurisdiction_default: bool = True
    source_mode: SourceModeType = "default"

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
    {"phase": "hearing", "title": "Generate Appellate Research Brief report", "description": "Create professional presentation for court", "order": 22},
]


# ============================================================================
# PAYMENT MODELS
# ============================================================================

class Payment(BaseModel):
    model_config = ConfigDict(extra="ignore")
    payment_id: str = Field(default_factory=lambda: f"pay_{uuid.uuid4().hex[:12]}")
    user_id: str
    case_id: str
    feature_type: str
    amount: float
    currency: str = "AUD"
    status: PaymentStatusType = "pending"
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    completed_at: Optional[datetime] = None


FEATURE_PRICES = {
    "grounds_of_merit": {"price": 99.00, "name": "Unlock Grounds of Merit Details"},
    "full_report": {"price": 150.00, "name": "Full Detailed Report"},
    "extensive_report": {"price": 200.00, "name": "Extensive Log Report"}
}

FEATURE_TYPE_ALIASES = {
    "grounds_of_merit": "grounds_of_merit",
    "grounds_unlock": "grounds_of_merit",
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
    return sorted({
        key for key, value in FEATURE_TYPE_ALIASES.items() if value == canonical
    } | ({canonical} if canonical else set()))


# ============================================================================
# DOCUMENT SEARCH MODELS
# ============================================================================

class DocumentSearchRequest(BaseModel):
    query: str
    case_sensitive: bool = False


class SearchMatch(BaseModel):
    document_id: str
    filename: str
    category: str
    matches: List[dict] = Field(default_factory=list)


# ============================================================================
# PIPELINE MODELS — Extract → Classify → Verify → Project → Draft
# ============================================================================

PipelineStageType = Literal["extract", "classify", "verify", "project", "draft"]

DocumentCategoryType = Literal[
    "court_document", "sentencing_remarks", "judgement", "transcript",
    "submissions", "affidavit", "expert_report", "correspondence",
    "legislation", "case_law", "other",
]

ClassificationConfidenceType = Literal["strong", "moderate", "weak"]

VerificationRoleType = Literal["supports", "undermines", "missing"]


class ExtractedFact(BaseModel):
    model_config = ConfigDict(extra="ignore")
    fact_id: str = Field(default_factory=lambda: f"fact_{uuid.uuid4().hex[:8]}")
    type: str = "general"
    text: str
    quote: Optional[str] = None
    page_reference: Optional[str] = None
    confidence: ClassificationConfidenceType = "moderate"


class ExtractedEvent(BaseModel):
    model_config = ConfigDict(extra="ignore")
    event_id: str = Field(default_factory=lambda: f"evt_{uuid.uuid4().hex[:8]}")
    title: str
    event_date: Optional[str] = None
    event_type: Optional[str] = None
    event_category: Optional[str] = "procedural"
    quote: Optional[str] = None
    page_reference: Optional[str] = None


class ExtractedFinding(BaseModel):
    model_config = ConfigDict(extra="ignore")
    finding_id: str = Field(default_factory=lambda: f"find_{uuid.uuid4().hex[:8]}")
    type: str = "judicial_finding"
    text: str
    quote: Optional[str] = None
    page_reference: Optional[str] = None


class SupportingItem(BaseModel):
    model_config = ConfigDict(extra="ignore")
    document_id: Optional[str] = None
    filename: Optional[str] = None
    quote: str = ""
    page_reference: Optional[str] = None
    role: VerificationRoleType = "supports"
    confidence: ClassificationConfidenceType = "moderate"


class MissingItem(BaseModel):
    model_config = ConfigDict(extra="ignore")
    description: str



# ============================================================================
# OPTIONAL NORMALISERS (ADDITIVE / SAFE)
# ============================================================================

class _NormaliserMixin(BaseModel):
    """
    Optional normaliser mixin for models that include these fields.
    Use check_fields=False because the mixin itself does not define these fields.
    """
    model_config = ConfigDict(extra="ignore")

    @field_validator("state", mode="before", check_fields=False)
    @classmethod
    def _normalise_state(cls, v):
        if v is None:
            return v
        return str(v).strip().lower()

    @field_validator("offence_category", mode="before", check_fields=False)
    @classmethod
    def _normalise_offence_category(cls, v):
        if v is None:
            return v
        return str(v).strip().lower()

    @field_validator("ground_type", mode="before", check_fields=False)
    @classmethod
    def _normalise_ground_type(cls, v):
        if v is None:
            return v
        return str(v).strip().lower()

    @field_validator("strength", mode="before", check_fields=False)
    @classmethod
    def _normalise_strength(cls, v):
        if v is None:
            return v
        return str(v).strip().lower()

    @field_validator("status", mode="before", check_fields=False)
    @classmethod
    def _normalise_status(cls, v):
        if v is None:
            return v
        return str(v).strip().lower()
