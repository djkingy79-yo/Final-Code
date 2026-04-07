# DO NOT UNDO — staged pipeline models. Additive module.
from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional, Literal
from datetime import datetime, timezone
import uuid

ConfidenceType = Literal["strong", "moderate", "weak"]
StageStatusType = Literal["pending", "completed", "failed", "needs_review"]
VerificationStatusType = Literal["unverified", "draft", "reviewed", "verified"]
SourceModeType = Literal["ai_generated", "manual", "imported", "derived"]


class ExtractedFact(BaseModel):
    model_config = ConfigDict(extra="ignore")
    fact_id: str = Field(default_factory=lambda: f"fact_{uuid.uuid4().hex[:10]}")
    type: str
    text: str
    quote: Optional[str] = None
    page_reference: Optional[str] = None
    confidence: ConfidenceType = "moderate"


class ExtractedEvent(BaseModel):
    model_config = ConfigDict(extra="ignore")
    extracted_event_id: str = Field(default_factory=lambda: f"xevt_{uuid.uuid4().hex[:10]}")
    title: str
    event_date: Optional[str] = None
    event_type: str = "event"
    event_category: str = "general"
    description: str = ""
    quote: Optional[str] = None
    page_reference: Optional[str] = None
    significance: str = "normal"


class ExtractedFinding(BaseModel):
    model_config = ConfigDict(extra="ignore")
    finding_id: str = Field(default_factory=lambda: f"find_{uuid.uuid4().hex[:10]}")
    type: str = "judicial_finding"
    text: str
    quote: Optional[str] = None
    page_reference: Optional[str] = None
    confidence: ConfidenceType = "moderate"


class DocumentExtract(BaseModel):
    model_config = ConfigDict(extra="ignore")
    extract_id: str = Field(default_factory=lambda: f"ext_{uuid.uuid4().hex[:12]}")
    case_id: str
    user_id: str
    document_id: str
    filename: str
    document_category: Optional[str] = None
    stage: str = "extract"
    status: StageStatusType = "completed"
    source_mode: SourceModeType = "ai_generated"
    verification_status: VerificationStatusType = "unverified"
    model_metadata: dict = Field(default_factory=dict)
    facts: List[ExtractedFact] = Field(default_factory=list)
    events: List[ExtractedEvent] = Field(default_factory=list)
    findings: List[ExtractedFinding] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class CaseExtract(BaseModel):
    model_config = ConfigDict(extra="ignore")
    case_extract_id: str = Field(default_factory=lambda: f"cex_{uuid.uuid4().hex[:12]}")
    case_id: str
    user_id: str
    stage: str = "extract"
    status: StageStatusType = "completed"
    metadata: dict = Field(default_factory=dict)
    merged_facts: List[dict] = Field(default_factory=list)
    merged_events: List[dict] = Field(default_factory=list)
    merged_findings: List[dict] = Field(default_factory=list)
    document_extract_ids: List[str] = Field(default_factory=list)
    verification_status: VerificationStatusType = "unverified"
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class IssueClassification(BaseModel):
    model_config = ConfigDict(extra="ignore")
    issue_id: str = Field(default_factory=lambda: f"iss_{uuid.uuid4().hex[:12]}")
    case_id: str
    user_id: str
    stage: str = "classify"
    status: str = "identified"
    title: str
    ground_type: str
    description: str
    appellate_pathway: str = ""
    error_identified: str = ""
    materiality: str = ""
    linked_fact_ids: List[str] = Field(default_factory=list)
    linked_event_ids: List[str] = Field(default_factory=list)
    linked_finding_ids: List[str] = Field(default_factory=list)
    classification_confidence: ConfidenceType = "moderate"
    jurisdiction: Optional[str] = None
    source_mode: SourceModeType = "ai_generated"
    verification_status: VerificationStatusType = "unverified"
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class IssueVerification(BaseModel):
    model_config = ConfigDict(extra="ignore")
    verification_id: str = Field(default_factory=lambda: f"ver_{uuid.uuid4().hex[:12]}")
    issue_id: str
    case_id: str
    user_id: str
    stage: str = "verify"
    status: StageStatusType = "completed"
    supporting_items: List[dict] = Field(default_factory=list)
    undermining_items: List[dict] = Field(default_factory=list)
    missing_items: List[str] = Field(default_factory=list)
    law_sections: List[dict] = Field(default_factory=list)
    similar_cases: List[dict] = Field(default_factory=list)
    legitimacy_scores: dict = Field(default_factory=dict)
    verification_status: VerificationStatusType = "reviewed"
    requires_human_review: bool = True
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
