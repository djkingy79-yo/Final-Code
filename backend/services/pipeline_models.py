# DO NOT UNDO — Pipeline models for the staged extraction/classification/verification pipeline.
# ExtractedFact, ExtractedEvent, ExtractedFinding are re-exported from models/ (canonical source).
# Pipeline-specific models (DocumentExtract, CaseExtract, IssueClassification, IssueVerification)
# are defined here with ALL fields that the pipeline code actually uses.

from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional
from datetime import datetime, timezone
import uuid

# Re-export extraction models from the canonical source (models/__init__.py)
# These have the full field definitions (type, quote, page_reference, confidence, etc.)
from models import (
    ExtractedFact,
    ExtractedEvent,
    ExtractedFinding,
    SupportingItem,
    MissingItem,
    LawSection,
    SimilarCase,
    LegitimacyScores,
)


# ============================================================================
# DOCUMENT EXTRACT — output of extract_document_artifacts()
# ============================================================================

class DocumentExtract(BaseModel):
    model_config = ConfigDict(extra="ignore")
    case_id: str
    user_id: str
    document_id: str
    filename: str
    document_category: Optional[str] = None
    model_metadata: dict = Field(default_factory=dict)
    facts: List[ExtractedFact] = Field(default_factory=list)
    events: List[ExtractedEvent] = Field(default_factory=list)
    findings: List[ExtractedFinding] = Field(default_factory=list)


# ============================================================================
# CASE EXTRACT — merged extracts across all documents for a case
# ============================================================================

class CaseExtract(BaseModel):
    model_config = ConfigDict(extra="ignore")
    case_id: str
    user_id: str
    merged_facts: List[dict] = Field(default_factory=list)
    merged_events: List[dict] = Field(default_factory=list)
    merged_findings: List[dict] = Field(default_factory=list)
    document_count: int = 0
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


# ============================================================================
# ISSUE CLASSIFICATION — output of classify_case_issues()
# Used by classify.py and _merge_overlapping_grounds() with model_copy()
# ============================================================================

class IssueClassification(BaseModel):
    model_config = ConfigDict(extra="ignore")
    issue_id: str = Field(default_factory=lambda: f"issue_{uuid.uuid4().hex[:8]}")
    case_id: str
    user_id: str
    title: str
    ground_type: str = "other"
    description: str = ""
    classification_confidence: str = "moderate"

    # Linked extraction IDs
    linked_fact_ids: List[str] = Field(default_factory=list)
    linked_event_ids: List[str] = Field(default_factory=list)
    linked_finding_ids: List[str] = Field(default_factory=list)

    # Appellate context — populated by classify.py
    jurisdiction: str = ""
    appellate_pathway: str = ""
    error_identified: str = ""
    materiality: str = ""

    # Law sections — cleaned by classify.py post-processing
    law_sections: List[dict] = Field(default_factory=list)


# ============================================================================
# ISSUE VERIFICATION — output of verify_issue()
# ============================================================================

class IssueVerification(BaseModel):
    model_config = ConfigDict(extra="ignore")
    issue_id: str
    case_id: str
    user_id: str

    # Evidence items
    supporting_items: List[dict] = Field(default_factory=list)
    undermining_items: List[dict] = Field(default_factory=list)
    missing_items: List[str] = Field(default_factory=list)

    # Legal references — populated by verify.py post-processing
    law_sections: List[dict] = Field(default_factory=list)
    similar_cases: List[dict] = Field(default_factory=list)

    # Legitimacy scoring — calculated by legitimacy_engine
    legitimacy_scores: Optional[dict] = None

    # Review status
    verification_status: str = "draft"
    requires_human_review: bool = True
