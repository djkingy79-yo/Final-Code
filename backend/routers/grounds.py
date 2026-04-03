# DO NOT UNDO — grounds router. All endpoints in this file are approved and must be preserved.
"""
Criminal Appeal AI - Grounds of Merit Router
ADDITIVE HARDENING PATCH
"""
from fastapi import APIRouter, HTTPException, Request
from datetime import datetime, timezone
import uuid
import json
import re
import os
import logging

from config import db
from auth_utils import get_current_user
from models import (
    GroundOfMerit,
    GroundOfMeritCreate,
    GroundOfMeritUpdate,
    FEATURE_PRICES,
    feature_type_variants,
    EvidenceItem,
    LawSection,
    SimilarCase,
)
from services.llm_service import call_llm_with_fallback
from services.offence_helpers import get_offence_context, get_offence_system_prompt
from services.document_helpers import build_document_context
from services.legitimacy_engine import calculate_ground_rating
from offence_framework import OFFENCE_CATEGORIES
from services.pipeline import (
    extract_document_artifacts,
    classify_case_issues,
    verify_issue,
)
from services.pipeline_models import CaseExtract

logger = logging.getLogger(__name__)

ADMIN_EMAILS = [email.strip() for email in os.environ.get("ADMIN_EMAILS", "").split(",") if email.strip()]


def is_admin_user(email: str) -> bool:
    normalized = (email or "").strip().lower()
    allowed = {(e or "").strip().lower() for e in ADMIN_EMAILS}
    return normalized in allowed


GROUND_TYPES = [
    "procedural_error", "fresh_evidence", "miscarriage_of_justice",
    "sentencing_error", "judicial_error", "ineffective_counsel",
    "prosecution_misconduct", "jury_irregularity", "constitutional_violation", "other"
]

router = APIRouter(prefix="/api", tags=["grounds"])


# ============================================================================
# ADDITIVE COMPATIBILITY HELPERS
# ============================================================================

def _normalise_ground_type(value: str) -> str:
    v = (value or "other").strip().lower()
    return v if v in GROUND_TYPES else "other"


def _wrap_evidence_items(raw_items):
    wrapped = []
    for item in raw_items or []:
        try:
            if isinstance(item, EvidenceItem):
                wrapped.append(item)
            elif isinstance(item, dict):
                wrapped.append(EvidenceItem(**item))
            else:
                wrapped.append(EvidenceItem(quote=str(item)))
        except Exception:
            wrapped.append(EvidenceItem(quote=str(item)))
    return wrapped


def _wrap_law_sections(raw_items):
    wrapped = []
    for item in raw_items or []:
        try:
            if isinstance(item, LawSection):
                wrapped.append(item)
            elif isinstance(item, dict):
                wrapped.append(LawSection(
                    act=item.get("act", ""),
                    section=item.get("section", ""),
                    jurisdiction=item.get("jurisdiction"),
                    title=item.get("title"),
                    verification_status=item.get("verification_status", "unverified"),
                ))
        except Exception:
            continue
    return wrapped


def _wrap_similar_cases(raw_items):
    wrapped = []
    for item in raw_items or []:
        try:
            if isinstance(item, SimilarCase):
                wrapped.append(item)
            elif isinstance(item, dict):
                wrapped.append(SimilarCase(
                    case_name=item.get("case_name", ""),
                    citation=item.get("citation"),
                    jurisdiction=item.get("jurisdiction"),
                    relevance_note=item.get("relevance_note"),
                    verification_status=item.get("verification_status", "unverified"),
                ))
        except Exception:
            continue
    return wrapped


def _legacy_evidence_dump(evidence_items):
    dumped = []
    for item in evidence_items or []:
        if isinstance(item, EvidenceItem):
            dumped.append(item.model_dump())
        elif isinstance(item, dict):
            dumped.append(item)
        else:
            dumped.append(EvidenceItem(quote=str(item)).model_dump())
    return dumped


def _law_sections_dump(items):
    return [item.model_dump() if isinstance(item, LawSection) else item for item in (items or [])]


def _similar_cases_dump(items):
    return [item.model_dump() if isinstance(item, SimilarCase) else item for item in (items or [])]


# ============================================================================
# PIPELINE DELEGATION HELPERS
# ============================================================================

async def _ensure_document_extracts(case: dict, documents: list):
    """Ensure every uploaded document has a staged extraction record. Additive only."""
    created_or_updated = 0
    for document in documents:
        existing = await db.document_extracts.find_one(
            {"case_id": case["case_id"], "document_id": document["document_id"], "user_id": case["user_id"]},
            {"_id": 0}
        )
        if existing:
            continue
        extract = await extract_document_artifacts(case, document)
        extract_dict = extract.model_dump()
        extract_dict["created_at"] = extract_dict["created_at"].isoformat()
        await db.document_extracts.update_one(
            {"case_id": case["case_id"], "document_id": document["document_id"], "user_id": case["user_id"]},
            {"$set": extract_dict},
            upsert=True,
        )
        created_or_updated += 1
    return created_or_updated


async def _refresh_case_extract_from_pipeline(case: dict) -> dict:
    """Merge all document extracts into a case-level extract."""
    extracts = await db.document_extracts.find(
        {"case_id": case["case_id"], "user_id": case["user_id"]}, {"_id": 0}
    ).to_list(500)
    merged_facts, merged_events, merged_findings, extract_ids = [], [], [], []
    for ext in extracts:
        extract_ids.append(ext.get("extract_id"))
        merged_facts.extend(ext.get("facts", []))
        merged_events.extend(ext.get("events", []))
        merged_findings.extend(ext.get("findings", []))
    case_extract = CaseExtract(
        case_id=case["case_id"],
        user_id=case["user_id"],
        metadata={
            "state": case.get("state"),
            "offence_category": case.get("offence_category"),
            "offence_type": case.get("offence_type"),
            "sentence": case.get("sentence"),
            "court": case.get("court"),
            "classification_source": case.get("classification_source", "existing"),
        },
        merged_facts=merged_facts,
        merged_events=merged_events,
        merged_findings=merged_findings,
        document_extract_ids=extract_ids,
    )
    case_extract_dict = case_extract.model_dump()
    case_extract_dict["created_at"] = case_extract_dict["created_at"].isoformat()
    await db.case_extracts.update_one(
        {"case_id": case["case_id"], "user_id": case["user_id"]},
        {"$set": case_extract_dict},
        upsert=True,
    )
    return case_extract_dict


async def _classify_pipeline_issues(case: dict, case_extract: dict) -> list[dict]:
    """Run staged issue classification and persist results.

    DO_NOT_UNDO — 3 Apr 2026: If issues already exist, DO NOT re-classify.
    Re-classification generates new LLM titles that slip past dedup and multiply grounds.
    """
    from services.ground_dedup import is_ground_duplicate, normalise_au_spelling

    existing_issues = await db.issue_classifications.find(
        {"case_id": case["case_id"], "user_id": case["user_id"]},
        {"_id": 0}
    ).to_list(500)

    if existing_issues:
        logger.info(f"Skipping re-classification for case {case['case_id']}: {len(existing_issues)} issues already exist")
        return existing_issues

    issues = await classify_case_issues(case, case_extract)

    persisted = []
    for issue in issues:
        issue_dict = issue.model_dump()
        issue_dict["created_at"] = issue_dict["created_at"].isoformat()
        issue_title = normalise_au_spelling((issue.title or "").strip())
        issue_dict["title"] = issue_title

        matched = None
        for ei in persisted:
            ei_title = (ei.get("title") or "").strip()
            if is_ground_duplicate(issue_title, ei_title):
                matched = ei
                break

        if matched:
            await db.issue_classifications.update_one(
                {"issue_id": matched["issue_id"]},
                {"$set": issue_dict},
            )
            saved = await db.issue_classifications.find_one(
                {"issue_id": matched["issue_id"]}, {"_id": 0}
            )
        else:
            await db.issue_classifications.update_one(
                {"case_id": case["case_id"], "user_id": case["user_id"], "title": issue_title, "ground_type": issue.ground_type},
                {"$set": issue_dict},
                upsert=True,
            )
            saved = await db.issue_classifications.find_one(
                {"case_id": case["case_id"], "user_id": case["user_id"], "title": issue_title, "ground_type": issue.ground_type},
                {"_id": 0}
            )

        if saved:
            persisted.append(saved)
    return persisted


async def _sync_pipeline_issues_to_grounds(case_id: str, user_id: str) -> int:
    """Project pipeline issues + verifications into existing grounds_of_merit collection.

    DO_NOT_UNDO — MUST use fuzzy dedup via is_ground_duplicate(). NEVER revert to exact-title
    upsert. Exact-title upsert was the ROOT CAUSE of grounds multiplying from 4 to 27+.
    """
    from services.ground_dedup import is_ground_duplicate, normalise_au_spelling

    issues = await db.issue_classifications.find(
        {"case_id": case_id, "user_id": user_id}, {"_id": 0}
    ).to_list(500)

    # Pre-load existing grounds for fuzzy matching
    all_existing_grounds = await db.grounds_of_merit.find(
        {"case_id": case_id, "user_id": user_id},
        {"_id": 0, "ground_id": 1, "title": 1},
    ).to_list(200)

    count = 0
    for issue in issues:
        verification = await db.issue_verifications.find_one(
            {"case_id": case_id, "issue_id": issue["issue_id"], "user_id": user_id}, {"_id": 0}
        )

        issue_title = normalise_au_spelling((issue.get("title") or "").strip())

        # Fuzzy match against all existing grounds
        existing_ground = None
        for eg in all_existing_grounds:
            eg_title = (eg.get("title") or "").strip()
            if is_ground_duplicate(issue_title, eg_title):
                existing_ground = eg
                break

        ground_doc = {
            "case_id": case_id,
            "user_id": user_id,
            "title": existing_ground["title"] if existing_ground else issue_title,
            "ground_type": issue.get("ground_type", "other"),
            "description": issue.get("description", ""),
            "strength": (verification or {}).get("legitimacy_scores", {}).get("rating", "moderate"),
            "status": "investigated" if verification else "identified",
            "supporting_evidence": (verification or {}).get("supporting_items", []),
            "law_sections": (verification or {}).get("law_sections", []),
            "similar_cases": (verification or {}).get("similar_cases", []),
            "legitimacy_scores": (verification or {}).get("legitimacy_scores", {}),
            "source_mode": "derived",
            "requires_human_review": (verification or {}).get("requires_human_review", True),
            "verification_status": (verification or {}).get("verification_status", "unverified"),
            "updated_at": datetime.now(timezone.utc).isoformat(),
        }

        if existing_ground:
            await db.grounds_of_merit.update_one(
                {"ground_id": existing_ground["ground_id"]},
                {"$set": ground_doc},
            )
        else:
            ground_doc["ground_id"] = f"gnd_{uuid.uuid4().hex[:12]}"
            ground_doc["created_at"] = datetime.now(timezone.utc).isoformat()
            await db.grounds_of_merit.insert_one(ground_doc)
            all_existing_grounds.append({"ground_id": ground_doc["ground_id"], "title": issue_title})

        count += 1
    return count


async def _ensure_pipeline_identification(case: dict, documents: list) -> dict:
    """Full staged path: extract → refresh → classify → sync to grounds.
    DO_NOT_UNDO — Final safety net: runs cleanup_duplicate_grounds AFTER sync.
    """
    from services.ground_dedup import cleanup_duplicate_grounds, cleanup_duplicate_issues
    extracted_count = await _ensure_document_extracts(case, documents)
    case_extract = await _refresh_case_extract_from_pipeline(case)
    issues = await _classify_pipeline_issues(case, case_extract)
    synced_count = await _sync_pipeline_issues_to_grounds(case["case_id"], case["user_id"])
    # Safety net: clean up any duplicates that may have slipped through
    await cleanup_duplicate_grounds(db, case["case_id"], case["user_id"])
    await cleanup_duplicate_issues(db, case["case_id"], case["user_id"])
    return {"extracted_count": extracted_count, "classified_count": len(issues), "synced_count": synced_count}


async def _verify_issue_and_sync(case: dict, issue: dict, ground_id: str | None = None) -> dict:
    """Verify one classified issue, then sync the projection back into grounds_of_merit."""
    case_extract = await db.case_extracts.find_one(
        {"case_id": case["case_id"], "user_id": case["user_id"]}, {"_id": 0}
    )
    if not case_extract:
        case_extract = await _refresh_case_extract_from_pipeline(case)
    supporting_context = {
        "facts": case_extract.get("merged_facts", []),
        "events": case_extract.get("merged_events", []),
        "findings": case_extract.get("merged_findings", []),
    }
    verification = await verify_issue(case, issue, supporting_context)
    verification_dict = verification.model_dump()
    verification_dict["created_at"] = verification_dict["created_at"].isoformat()
    await db.issue_verifications.update_one(
        {"case_id": case["case_id"], "issue_id": issue["issue_id"], "user_id": case["user_id"]},
        {"$set": verification_dict},
        upsert=True,
    )
    await _sync_pipeline_issues_to_grounds(case["case_id"], case["user_id"])
    # DO_NOT_UNDO — 3 Apr 2026: cleanup after EVERY sync, no exceptions
    from services.ground_dedup import cleanup_duplicate_grounds
    await cleanup_duplicate_grounds(db, case["case_id"], case["user_id"])
    if ground_id:
        projected = await db.grounds_of_merit.find_one(
            {"ground_id": ground_id, "case_id": case["case_id"], "user_id": case["user_id"]}, {"_id": 0}
        )
        if projected:
            return projected
    projected = await db.grounds_of_merit.find_one(
        {"case_id": case["case_id"], "user_id": case["user_id"], "title": issue.get("title"), "ground_type": issue.get("ground_type")}, {"_id": 0}
    )
    return projected or verification_dict


# ============================================================================
# CRUD ENDPOINTS
# ============================================================================

@router.get("/cases/{case_id}/grounds", response_model=dict)
async def get_grounds_of_merit(case_id: str, request: Request):
    """Get all grounds of merit for a case - requires payment to see details"""
    user = await get_current_user(request)
    case = await db.cases.find_one({"case_id": case_id, "user_id": user.user_id})
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")

    STRENGTH_ORDER = {"strong": 0, "moderate": 1, "weak": 2, "unknown": 3}

    grounds = await db.grounds_of_merit.find(
        {"case_id": case_id},
        {"_id": 0}
    ).sort([("created_at", -1)]).to_list(200)

    # Sort: strong first, then moderate, then weak
    grounds.sort(key=lambda g: (STRENGTH_ORDER.get(g.get("strength", "unknown"), 3), g.get("title", "")))

    payment = await db.payments.find_one({
        "case_id": case_id,
        "user_id": user.user_id,
        "feature_type": {"$in": feature_type_variants("grounds_of_merit")},
        "status": "completed"
    })

    is_unlocked = payment is not None or "grounds_of_merit" in (case.get("unlocked_features") or []) or is_admin_user(user.email)

    if is_unlocked:
        # Retroactively score any grounds missing legitimacy_scores
        for g in grounds:
            if not g.get("ground_id"):
                g["ground_id"] = f"gnd_{uuid.uuid4().hex[:12]}"
                await db.grounds_of_merit.update_one(
                    {"case_id": case_id, "title": g.get("title"), "ground_type": g.get("ground_type")},
                    {"$set": {"ground_id": g["ground_id"]}}
                )
            if "source_mode" not in g:
                g["source_mode"] = "legacy"
            if "verification_status" not in g:
                g["verification_status"] = "unverified"
            # Only calculate legitimacy scores for grounds that have been investigated
            # and have actual evidence. Newly identified grounds stay at their assigned strength.
            if not g.get("legitimacy_scores") and g.get("status") == "investigated" and g.get("supporting_evidence"):
                scored = calculate_ground_rating({
                    "ground_type": g.get("ground_type", "other"),
                    "supporting_evidence": [{"quote": e.get("quote", "") if isinstance(e, dict) else str(e)} for e in (g.get("supporting_evidence") or [])],
                    "undermining_items": g.get("undermining_items") or [],
                })
                g["legitimacy_scores"] = scored
                g["strength"] = scored["rating"]
                await db.grounds_of_merit.update_one(
                    {"ground_id": g["ground_id"]},
                    {"$set": {"legitimacy_scores": scored, "strength": scored["rating"]}}
                )
        return {
            "grounds": grounds,
            "count": len(grounds),
            "is_unlocked": True,
            "unlock_price": FEATURE_PRICES["grounds_of_merit"]["price"]
        }
    else:
        return {
            "grounds": [],
            "count": len(grounds),
            "is_unlocked": False,
            "unlock_price": FEATURE_PRICES["grounds_of_merit"]["price"],
            "message": f"Found {len(grounds)} potential grounds of merit. Pay ${FEATURE_PRICES['grounds_of_merit']['price']:.2f} to unlock full details."
        }


@router.post("/cases/{case_id}/grounds", response_model=dict)
async def create_ground_of_merit(case_id: str, ground_data: GroundOfMeritCreate, request: Request):
    """Create a new ground of merit"""
    user = await get_current_user(request)
    case = await db.cases.find_one({"case_id": case_id, "user_id": user.user_id})
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")

    evidence_items = _wrap_evidence_items(ground_data.supporting_evidence)

    scored = calculate_ground_rating({
        "ground_type": _normalise_ground_type(ground_data.ground_type),
        "supporting_evidence": [{"quote": e.quote} for e in evidence_items]
    })

    ground = GroundOfMerit(
        case_id=case_id,
        user_id=user.user_id,
        title=ground_data.title,
        ground_type=_normalise_ground_type(ground_data.ground_type),
        description=ground_data.description,
        strength=scored["rating"],
        supporting_evidence=evidence_items,
        legitimacy_scores=scored,
        source_mode="manual",
        requires_human_review=True,
        verification_status="unverified",
    )

    ground_dict = ground.model_dump()
    ground_dict["created_at"] = ground_dict["created_at"].isoformat()
    ground_dict["updated_at"] = ground_dict["updated_at"].isoformat()

    await db.grounds_of_merit.insert_one(ground_dict)
    await db.cases.update_one(
        {"case_id": case_id, "user_id": user.user_id},
        {"$set": {"updated_at": datetime.now(timezone.utc).isoformat()}}
    )

    created_ground = await db.grounds_of_merit.find_one({"ground_id": ground.ground_id}, {"_id": 0})
    return created_ground


@router.get("/cases/{case_id}/grounds/{ground_id}", response_model=dict)
async def get_ground_of_merit(case_id: str, ground_id: str, request: Request):
    """Get a specific ground of merit"""
    user = await get_current_user(request)
    ground = await db.grounds_of_merit.find_one(
        {"ground_id": ground_id, "case_id": case_id, "user_id": user.user_id},
        {"_id": 0}
    )
    if not ground:
        raise HTTPException(status_code=404, detail="Ground of merit not found")
    if "source_mode" not in ground:
        ground["source_mode"] = "legacy"
    if "verification_status" not in ground:
        ground["verification_status"] = "unverified"
    return ground


@router.put("/cases/{case_id}/grounds/{ground_id}", response_model=dict)
async def update_ground_of_merit(case_id: str, ground_id: str, ground_data: GroundOfMeritUpdate, request: Request):
    """Update a ground of merit"""
    user = await get_current_user(request)

    update_fields = {k: v for k, v in ground_data.model_dump().items() if v is not None}

    if "ground_type" in update_fields:
        update_fields["ground_type"] = _normalise_ground_type(update_fields["ground_type"])

    if "supporting_evidence" in update_fields:
        evidence_items = _wrap_evidence_items(update_fields["supporting_evidence"])
        update_fields["supporting_evidence"] = _legacy_evidence_dump(evidence_items)

        scored = calculate_ground_rating({
            "ground_type": update_fields.get("ground_type", "other"),
            "supporting_evidence": [{"quote": e.get("quote", "")} for e in update_fields["supporting_evidence"]]
        })
        update_fields["legitimacy_scores"] = scored
        update_fields["strength"] = scored["rating"]

    update_fields["updated_at"] = datetime.now(timezone.utc).isoformat()

    result = await db.grounds_of_merit.update_one(
        {"ground_id": ground_id, "case_id": case_id, "user_id": user.user_id},
        {"$set": update_fields}
    )

    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Ground of merit not found")

    return await db.grounds_of_merit.find_one(
        {"ground_id": ground_id, "case_id": case_id, "user_id": user.user_id},
        {"_id": 0}
    )


@router.delete("/cases/{case_id}/grounds/{ground_id}")
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


# ============================================================================
# INVESTIGATE SINGLE GROUND
# ============================================================================

@router.post("/cases/{case_id}/grounds/{ground_id}/investigate", response_model=dict)
async def investigate_ground_of_merit(case_id: str, ground_id: str, request: Request):
    """Deep investigation of a specific ground via staged pipeline verification"""
    user = await get_current_user(request)

    ground = await db.grounds_of_merit.find_one(
        {"ground_id": ground_id, "case_id": case_id, "user_id": user.user_id},
        {"_id": 0}
    )
    if not ground:
        raise HTTPException(status_code=404, detail="Ground of merit not found")

    case = await db.cases.find_one(
        {"case_id": case_id, "user_id": user.user_id},
        {"_id": 0}
    )
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")

    try:
        # DO NOT re-run _ensure_pipeline_identification here — it re-classifies
        # ALL issues and creates new grounds. We only want to verify THIS ground.

        issue = await db.issue_classifications.find_one(
            {
                "case_id": case_id,
                "user_id": user.user_id,
                "title": ground.get("title"),
                "ground_type": ground.get("ground_type"),
            },
            {"_id": 0}
        )

        if not issue:
            issue = {
                "issue_id": f"compat_{ground_id}",
                "case_id": case_id,
                "user_id": user.user_id,
                "title": ground.get("title", "Untitled ground"),
                "ground_type": ground.get("ground_type", "other"),
                "description": ground.get("description", ""),
            }

        # Verify ONLY this issue and update ONLY this ground — not all grounds
        case_extract = await db.case_extracts.find_one(
            {"case_id": case_id, "user_id": user.user_id}, {"_id": 0}
        )
        if not case_extract:
            case_extract = {"merged_facts": [], "merged_events": [], "merged_findings": []}

        supporting_context = {
            "facts": case_extract.get("merged_facts", []),
            "events": case_extract.get("merged_events", []),
            "findings": case_extract.get("merged_findings", []),
        }
        verification = await verify_issue(case, issue, supporting_context)
        verification_dict = verification.model_dump()
        verification_dict["created_at"] = verification_dict["created_at"].isoformat()

        # Store verification
        await db.issue_verifications.update_one(
            {"case_id": case_id, "issue_id": issue["issue_id"], "user_id": user.user_id},
            {"$set": verification_dict},
            upsert=True,
        )

        # Generate deep analysis text for this ground
        deep_analysis_text = ""
        try:
            analysis_prompt = f"""Analyse the following ground of appeal in the criminal case of {case.get('defendant_name', 'the appellant')} ({case.get('state', 'NSW')}).

Ground: {ground.get('title', '')}
Type: {ground.get('ground_type', '')}
Description: {ground.get('description', '')}

Supporting evidence found:
{json.dumps(verification_dict.get('supporting_items', []), indent=2, default=str)[:2000]}

Undermining factors:
{json.dumps(verification_dict.get('undermining_items', []), indent=2, default=str)[:1000]}

Relevant legislation:
{json.dumps(verification_dict.get('law_sections', []), indent=2, default=str)[:1000]}

Similar cases:
{json.dumps(verification_dict.get('similar_cases', []), indent=2, default=str)[:1000]}

Legitimacy assessment: {json.dumps(verification_dict.get('legitimacy_scores', {}), default=str)}

Write a detailed investigative analysis of this ground (500-800 words). Use third person only. Write in paragraphs, NOT bullet points. Cover:
1. The factual basis and evidentiary foundation
2. The applicable legal framework and statutory provisions
3. How supporting and undermining evidence interacts
4. Comparable case law and precedent
5. Overall viability assessment and what further material could strengthen or weaken this ground

Use Australian English spelling (analyse, defence, offence). Do NOT use first or second person."""

            deep_analysis_text = await call_llm_with_fallback(
                system_prompt="You are a senior Australian criminal appellate researcher conducting deep issue analysis. Write in formal third person. Use paragraphs, not bullet points. Australian English only.",
                user_prompt=analysis_prompt,
                session_id=f"deep_analysis_{ground_id}",
                task_type="ground_deep_analysis",
            )
        except Exception as e:
            logger.warning(f"Deep analysis generation failed for ground {ground_id}: {e}")

        # Update ONLY this ground with verification results — DO NOT re-sync all
        update_fields = {
            "status": "investigated",
            "verification_status": "verified",
        }
        if verification_dict.get("legitimacy_scores"):
            scores = verification_dict["legitimacy_scores"]
            update_fields["legitimacy_scores"] = scores
            update_fields["strength"] = scores.get("rating", ground.get("strength", "moderate"))
        if verification_dict.get("law_sections"):
            update_fields["law_sections"] = verification_dict["law_sections"]
        if verification_dict.get("similar_cases"):
            update_fields["similar_cases"] = verification_dict["similar_cases"]
        if verification_dict.get("supporting_items"):
            update_fields["supporting_evidence"] = verification_dict["supporting_items"]
        if deep_analysis_text:
            update_fields["deep_analysis"] = {
                "full_analysis": deep_analysis_text,
                "generated_at": datetime.now(timezone.utc).isoformat(),
            }
            update_fields["analysis"] = deep_analysis_text

        await db.grounds_of_merit.update_one(
            {"ground_id": ground_id, "case_id": case_id},
            {"$set": update_fields}
        )

        # Return updated ground
        updated = await db.grounds_of_merit.find_one(
            {"ground_id": ground_id, "case_id": case_id}, {"_id": 0}
        )
        return updated or verification_dict

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Ground investigation pipeline failed: {e}")
        raise HTTPException(status_code=500, detail=f"Ground investigation failed: {str(e)}")


# ============================================================================
# AUTO IDENTIFY GROUNDS
# ============================================================================

@router.post("/cases/{case_id}/grounds/auto-identify", response_model=dict)
async def auto_identify_grounds(case_id: str, request: Request):
    """AI automatically identifies potential grounds of merit from case materials using staged pipeline"""
    user = await get_current_user(request)

    case = await db.cases.find_one({"case_id": case_id, "user_id": user.user_id}, {"_id": 0})
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")

    existing_grounds = await db.grounds_of_merit.find(
        {"case_id": case_id, "user_id": user.user_id}, {"_id": 0}
    ).to_list(100)

    documents = await db.documents.find(
        {"case_id": case_id, "user_id": user.user_id}, {"_id": 0, "file_data": 0}
    ).to_list(500)

    if not documents and not case.get("summary"):
        raise HTTPException(status_code=400, detail="No documents or case summary available for analysis")

    try:
        pipeline_result = await _ensure_pipeline_identification(case, documents)
    except Exception as e:
        logger.error(f"Pipeline auto-identify failed: {e}")
        raise HTTPException(status_code=500, detail=f"Pipeline identification failed: {str(e)}")

    updated_grounds = await db.grounds_of_merit.find(
        {"case_id": case_id, "user_id": user.user_id}, {"_id": 0}
    ).to_list(200)

    existing_titles = {(g.get("title"), g.get("ground_type")) for g in existing_grounds}

    # DO_NOT_UNDO — Fuzzy ground deduplication with topic classification + fuzzywuzzy + overlap.
    from services.ground_dedup import is_ground_duplicate, normalise_au_spelling

    def is_duplicate(new_ground):
        """Check if a ground is duplicate by exact match, topic classification, fuzzywuzzy, or word overlap"""
        if (new_ground.get("title"), new_ground.get("ground_type")) in existing_titles:
            return True
        new_title = normalise_au_spelling((new_ground.get("title") or "").strip())
        if not new_title:
            return False
        for eg in existing_grounds:
            eg_title = (eg.get("title") or "").strip()
            if is_ground_duplicate(new_title, eg_title):
                return True
        return False

    new_grounds = [
        g for g in updated_grounds
        if not is_duplicate(g)
    ]
    skipped_duplicates = max(0, pipeline_result["classified_count"] - len(new_grounds))

    await db.cases.update_one(
        {"case_id": case_id, "user_id": user.user_id},
        {"$set": {"updated_at": datetime.now(timezone.utc).isoformat()}}
    )

    return {
        "identified_count": len(new_grounds),
        "skipped_duplicates": skipped_duplicates,
        "existing_grounds": len(existing_grounds),
        "message": (
            f"Found {len(new_grounds)} new grounds. "
            f"Pipeline extracted {pipeline_result['extracted_count']} new document extract(s), "
            f"classified {pipeline_result['classified_count']} issue(s), "
            f"and synced {pipeline_result['synced_count']} projected ground(s)."
        ),
        "unlock_required": True,
        "unlock_price": FEATURE_PRICES["grounds_of_merit"]["price"]
    }



# ============================================================================
# DEDUP CLEANUP ENDPOINT
# ============================================================================

@router.post("/cases/{case_id}/grounds/cleanup-duplicates", response_model=dict)
async def cleanup_ground_duplicates(case_id: str, request: Request):
    """DO_NOT_UNDO — Remove duplicate grounds using fuzzy deduplication.
    Merges data from duplicates into the kept ground (first by created_at).
    """
    user = await get_current_user(request)
    case = await db.cases.find_one({"case_id": case_id, "user_id": user.user_id})
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")

    from services.ground_dedup import cleanup_duplicate_grounds, cleanup_duplicate_issues

    grounds_result = await cleanup_duplicate_grounds(db, case_id, user.user_id)
    issues_result = await cleanup_duplicate_issues(db, case_id, user.user_id)

    return {
        "grounds": grounds_result,
        "issues": issues_result,
        "message": f"Cleaned up {grounds_result['removed']} duplicate grounds and {issues_result['removed']} duplicate issues.",
    }
