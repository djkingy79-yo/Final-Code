# DO NOT UNDO — staged pipeline router. Additive module.
from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel
from datetime import datetime, timezone
import logging
import uuid

from config import db
from auth_utils import get_current_user


def _safe_isoformat(d, key):
    """Safely convert a datetime field to isoformat string."""
    if key not in d:
        d[key] = datetime.now(timezone.utc).isoformat()
    elif hasattr(d[key], "isoformat"):
        d[key] = d[key].isoformat()


from services.pipeline import (  # noqa: E402
    extract_document_artifacts,
    classify_case_issues,
    verify_issue,
    draft_report_from_verified_material,
)
from services.pipeline_models import CaseExtract  # noqa: E402

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/pipeline", tags=["pipeline-staged"])


class RefreshPipelineRequest(BaseModel):
    verify_limit: int = 0


def _issue_priority_rank(issue: dict) -> tuple:
    # DO NOT UNDO — Uses the five canonical buckets, not the old 10-type vocabulary.
    # Priority: conviction first (highest appellate impact), then procedure,
    # then evidence, then sentence, then ineffective_counsel last (contingent ground).
    preferred_ground_order = {
        "conviction": 0,
        "procedure": 1,
        "evidence": 2,
        "sentence": 3,
        "ineffective_counsel": 4,
        # Legacy labels — kept so old DB records still sort sensibly until
        # they are re-normalised through the pipeline.
        "judicial_error": 0,
        "miscarriage_of_justice": 0,
        "fresh_evidence": 0,
        "prosecution_misconduct": 0,
        "procedural_error": 1,
        "jury_irregularity": 1,
        "sentencing_error": 3,
        "constitutional_violation": 0,
        "other": 5,
    }

    confidence_order = {
        "strong": 0,
        "moderate": 1,
        "weak": 2,
    }

    return (
        preferred_ground_order.get(issue.get("ground_type", "other"), 9),
        confidence_order.get(issue.get("classification_confidence", "moderate"), 1),
        str(issue.get("title", "")).lower(),
    )


async def _ensure_document_extracts(case: dict, documents: list) -> dict:
    created = 0
    skipped = 0

    for document in documents:
        existing = await db.document_extracts.find_one(
            {
                "case_id": case["case_id"],
                "document_id": document["document_id"],
                "user_id": case["user_id"],
            },
            {"_id": 0}
        )
        if existing:
            skipped += 1
            continue

        extract = await extract_document_artifacts(case, document)
        extract_dict = extract.model_dump()
        if "created_at" in extract_dict and hasattr(extract_dict["created_at"], "isoformat"):
            extract_dict["created_at"] = extract_dict["created_at"].isoformat()
        elif "created_at" not in extract_dict:
            extract_dict["created_at"] = datetime.now(timezone.utc).isoformat()

        await db.document_extracts.update_one(
            {
                "case_id": case["case_id"],
                "document_id": document["document_id"],
                "user_id": case["user_id"],
            },
            {"$set": extract_dict},
            upsert=True,
        )
        created += 1

    return {
        "created": created,
        "skipped_existing": skipped,
    }


async def _refresh_case_extract(case: dict) -> dict:
    extracts = await db.document_extracts.find(
        {"case_id": case["case_id"], "user_id": case["user_id"]},
        {"_id": 0}
    ).to_list(500)

    merged_facts = []
    merged_events = []
    merged_findings = []
    extract_ids = []

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
    _safe_isoformat(case_extract_dict, "created_at")

    await db.case_extracts.update_one(
        {"case_id": case["case_id"], "user_id": case["user_id"]},
        {"$set": case_extract_dict},
        upsert=True,
    )

    return {
        "case_extract_id": case_extract.case_extract_id,
        "facts": len(merged_facts),
        "events": len(merged_events),
        "findings": len(merged_findings),
    }


async def _classify_issues(case: dict, case_extract: dict) -> dict:
    """DO_NOT_UNDO — 3 Apr 2026: If issues already exist, DO NOT re-classify.
    Re-classification generates new LLM titles that slip past dedup and multiply grounds.
    """
    from services.ground_dedup import is_ground_duplicate, normalise_au_spelling

    existing_issues = await db.issue_classifications.find(
        {"case_id": case["case_id"], "user_id": case["user_id"]},
        {"_id": 0}
    ).to_list(500)

    if len(existing_issues) >= 8:
        logger.info(f"Skipping re-classification for case {case['case_id']}: {len(existing_issues)} issues already exist (>= 8)")
        return {"classified": len(existing_issues)}

    logger.info(f"Re-classifying case {case['case_id']}: only {len(existing_issues)} issues exist (< 8), looking for more")
    issues = await classify_case_issues(case, case_extract)

    upserted = 0
    persisted_titles = []
    for issue in issues:
        issue_dict = issue.model_dump()
        _safe_isoformat(issue_dict, "created_at")
        issue_title = normalise_au_spelling((issue.title or "").strip())
        issue_dict["title"] = issue_title

        matched = None
        for ei_title in persisted_titles:
            if is_ground_duplicate(issue_title, ei_title):
                matched = ei_title
                break

        if not matched:
            await db.issue_classifications.update_one(
                {"case_id": case["case_id"], "user_id": case["user_id"], "title": issue_title, "ground_type": issue.ground_type},
                {"$set": issue_dict},
                upsert=True,
            )
            persisted_titles.append(issue_title)
        upserted += 1

    return {
        "classified": upserted,
    }


async def _verify_top_issues(case: dict, verify_limit: int) -> dict:
    if verify_limit <= 0:
        return {
            "requested_limit": verify_limit,
            "applied_limit": 0,
            "attempted": 0,
            "verified": 0,
            "failed": 0,
        }

    case_extract = await db.case_extracts.find_one(
        {"case_id": case["case_id"], "user_id": case["user_id"]},
        {"_id": 0}
    )
    if not case_extract:
        return {
            "requested_limit": verify_limit,
            "applied_limit": 0,
            "attempted": 0,
            "verified": 0,
            "failed": 0,
        }

    issues = await db.issue_classifications.find(
        {"case_id": case["case_id"], "user_id": case["user_id"]},
        {"_id": 0}
    ).to_list(500)

    eligible = []
    for issue in issues:
        existing_verification = await db.issue_verifications.find_one(
            {
                "case_id": case["case_id"],
                "issue_id": issue["issue_id"],
                "user_id": case["user_id"],
            },
            {"_id": 0}
        )
        if existing_verification:
            continue
        eligible.append(issue)

    eligible.sort(key=_issue_priority_rank)

    applied_limit = max(0, min(int(verify_limit or 0), 20))
    selected = eligible[:applied_limit]

    supporting_context = {
        "facts": case_extract.get("merged_facts", []),
        "events": case_extract.get("merged_events", []),
        "findings": case_extract.get("merged_findings", []),
    }

    verified = 0
    failed = 0

    for issue in selected:
        try:
            verification = await verify_issue(case, issue, supporting_context)
            verification_dict = verification.model_dump()
            _safe_isoformat(verification_dict, "created_at")

            await db.issue_verifications.update_one(
                {
                    "case_id": case["case_id"],
                    "issue_id": issue["issue_id"],
                    "user_id": case["user_id"],
                },
                {"$set": verification_dict},
                upsert=True,
            )
            verified += 1
        except Exception as e:
            logger.warning(f"Refresh-all verification failed for issue {issue.get('issue_id')}: {e}")
            failed += 1

    return {
        "requested_limit": verify_limit,
        "applied_limit": applied_limit,
        "attempted": len(selected),
        "verified": verified,
        "failed": failed,
    }


async def _sync_pipeline_projection_to_grounds(case_id: str, user_id: str) -> int:
    """DO_NOT_UNDO — Sync staged issues/verifications into grounds_of_merit.
    MUST use fuzzy dedup via is_ground_duplicate(). NEVER revert to exact-title upsert.
    Exact-title upsert was the ROOT CAUSE of grounds multiplying from 4 to 27+.
    """
    from services.ground_dedup import is_ground_duplicate, normalise_au_spelling

    issues = await db.issue_classifications.find(
        {"case_id": case_id, "user_id": user_id},
        {"_id": 0}
    ).to_list(500)

    # Pre-load existing grounds for fuzzy matching
    all_existing_grounds = await db.grounds_of_merit.find(
        {"case_id": case_id, "user_id": user_id},
        {"_id": 0, "ground_id": 1, "title": 1},
    ).to_list(200)

    synced = 0
    for issue in issues:
        verification = await db.issue_verifications.find_one(
            {
                "case_id": case_id,
                "issue_id": issue["issue_id"],
                "user_id": user_id,
            },
            {"_id": 0}
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
            "strength": (verification or {}).get("legitimacy_scores", {}).get(
                "rating",
                issue.get("classification_confidence", "moderate")
            ),
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

        synced += 1

    return synced


@router.post("/cases/{case_id}/documents/{document_id}/extract", response_model=dict)
async def extract_document(case_id: str, document_id: str, request: Request):
    user = await get_current_user(request)

    case = await db.cases.find_one({"case_id": case_id, "user_id": user.user_id}, {"_id": 0})
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")

    document = await db.documents.find_one(
        {"case_id": case_id, "document_id": document_id, "user_id": user.user_id},
        {"_id": 0, "file_data": 0}
    )
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")

    extract = await extract_document_artifacts(case, document)
    extract_dict = extract.model_dump()
    if "created_at" in extract_dict and hasattr(extract_dict["created_at"], "isoformat"):
        extract_dict["created_at"] = extract_dict["created_at"].isoformat()
    elif "created_at" not in extract_dict:
        extract_dict["created_at"] = datetime.now(timezone.utc).isoformat()

    await db.document_extracts.update_one(
        {"case_id": case_id, "document_id": document_id, "user_id": user.user_id},
        {"$set": extract_dict},
        upsert=True,
    )

    return {
        "extract_id": extract.extract_id,
        "status": extract.status,
        "facts_count": len(extract.facts),
        "events_count": len(extract.events),
        "findings_count": len(extract.findings),
    }


@router.post("/cases/{case_id}/extract/refresh", response_model=dict)
async def refresh_case_extract(case_id: str, request: Request):
    user = await get_current_user(request)

    case = await db.cases.find_one({"case_id": case_id, "user_id": user.user_id}, {"_id": 0})
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")

    extracts = await db.document_extracts.find(
        {"case_id": case_id, "user_id": user.user_id},
        {"_id": 0}
    ).to_list(500)

    merged_facts = []
    merged_events = []
    merged_findings = []
    extract_ids = []

    for ext in extracts:
        extract_ids.append(ext.get("extract_id"))
        merged_facts.extend(ext.get("facts", []))
        merged_events.extend(ext.get("events", []))
        merged_findings.extend(ext.get("findings", []))

    case_extract = CaseExtract(
        case_id=case_id,
        user_id=user.user_id,
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
    _safe_isoformat(case_extract_dict, "created_at")

    await db.case_extracts.update_one(
        {"case_id": case_id, "user_id": user.user_id},
        {"$set": case_extract_dict},
        upsert=True,
    )

    return {
        "case_extract_id": case_extract.case_extract_id,
        "status": case_extract.status,
        "document_extracts_used": len(extracts),
    }


@router.post("/cases/{case_id}/issues/classify", response_model=dict)
async def classify_issues(case_id: str, request: Request):
    user = await get_current_user(request)

    case = await db.cases.find_one({"case_id": case_id, "user_id": user.user_id}, {"_id": 0})
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")

    case_extract = await db.case_extracts.find_one({"case_id": case_id, "user_id": user.user_id}, {"_id": 0})
    if not case_extract:
        raise HTTPException(status_code=400, detail="Case extract not found. Run extraction first.")

    issues = await classify_case_issues(case, case_extract)

    # DO_NOT_UNDO — Fuzzy dedup on issue_classifications to stop them multiplying.
    from services.ground_dedup import is_ground_duplicate, normalise_au_spelling

    # Get existing classifications for this case
    existing_issues = await db.issue_classifications.find(
        {"case_id": case_id, "user_id": user.user_id},
        {"_id": 0, "issue_id": 1, "title": 1}
    ).to_list(200)

    inserted = 0
    for issue in issues:
        issue_dict = issue.model_dump()
        _safe_isoformat(issue_dict, "created_at")
        issue_title = normalise_au_spelling((issue.title or "").strip())
        # Find existing issue with topic + fuzzy match
        matched_existing = None
        for ei in existing_issues:
            ei_title = (ei.get("title") or "").strip()
            if is_ground_duplicate(issue_title, ei_title):
                matched_existing = ei
                break

        if matched_existing:
            # Update existing, keep original title
            await db.issue_classifications.update_one(
                {"issue_id": matched_existing["issue_id"]},
                {"$set": {k: v for k, v in issue_dict.items() if k not in ("title", "issue_id")}},
            )
        else:
            await db.issue_classifications.update_one(
                {"case_id": case_id, "user_id": user.user_id, "issue_id": issue_dict["issue_id"]},
                {"$set": issue_dict},
                upsert=True,
            )
            existing_issues.append({"issue_id": issue_dict["issue_id"], "title": issue_title})
        inserted += 1

    return {"identified_count": inserted}


@router.post("/cases/{case_id}/issues/{issue_id}/verify", response_model=dict)
async def verify_single_issue(case_id: str, issue_id: str, request: Request):
    user = await get_current_user(request)

    case = await db.cases.find_one({"case_id": case_id, "user_id": user.user_id}, {"_id": 0})
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")

    issue = await db.issue_classifications.find_one(
        {"case_id": case_id, "issue_id": issue_id, "user_id": user.user_id},
        {"_id": 0}
    )
    if not issue:
        raise HTTPException(status_code=404, detail="Issue not found")

    case_extract = await db.case_extracts.find_one({"case_id": case_id, "user_id": user.user_id}, {"_id": 0})
    supporting_context = {
        "facts": case_extract.get("merged_facts", []) if case_extract else [],
        "events": case_extract.get("merged_events", []) if case_extract else [],
        "findings": case_extract.get("merged_findings", []) if case_extract else [],
    }

    verification = await verify_issue(case, issue, supporting_context)
    verification_dict = verification.model_dump()
    _safe_isoformat(verification_dict, "created_at")

    await db.issue_verifications.update_one(
        {"case_id": case_id, "issue_id": issue_id, "user_id": user.user_id},
        {"$set": verification_dict},
        upsert=True,
    )

    return {
        "verification_id": verification.verification_id,
        "verification_status": verification.verification_status,
        "rating": verification.legitimacy_scores.get("rating", "moderate"),
    }


@router.post("/cases/{case_id}/grounds/sync-from-issues", response_model=dict)
async def sync_grounds_from_issues(case_id: str, request: Request):
    """Compatibility projection layer into existing grounds_of_merit collection."""
    user = await get_current_user(request)

    case = await db.cases.find_one({"case_id": case_id, "user_id": user.user_id}, {"_id": 0})
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")

    issues = await db.issue_classifications.find(
        {"case_id": case_id, "user_id": user.user_id},
        {"_id": 0}
    ).to_list(500)

    # DO_NOT_UNDO — Fuzzy ground deduplication in staged pipeline sync.
    # Previous exact-title match let grounds multiply on every pipeline run.
    from services.ground_dedup import is_ground_duplicate, normalise_au_spelling

    # Pre-load all existing grounds for efficient matching
    all_existing_grounds = await db.grounds_of_merit.find(
        {"case_id": case_id, "user_id": user.user_id},
        {"_id": 0, "ground_id": 1, "title": 1},
    ).to_list(200)

    count = 0
    for issue in issues:
        verification = await db.issue_verifications.find_one(
            {"case_id": case_id, "issue_id": issue["issue_id"], "user_id": user.user_id},
            {"_id": 0}
        )

        issue_title = normalise_au_spelling((issue.get("title") or "").strip())
        # Check for existing ground with topic + fuzzy match
        existing_ground = None
        for eg in all_existing_grounds:
            eg_title = (eg.get("title") or "").strip()
            if is_ground_duplicate(issue_title, eg_title):
                existing_ground = eg
                break

        ground_doc = {
            "case_id": case_id,
            "user_id": user.user_id,
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
            # Update existing ground — keep original title
            await db.grounds_of_merit.update_one(
                {"ground_id": existing_ground["ground_id"]},
                {"$set": ground_doc},
            )
        else:
            # Create new ground
            ground_doc["ground_id"] = f"gnd_{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}_{count}"
            ground_doc["created_at"] = datetime.now(timezone.utc).isoformat()
            await db.grounds_of_merit.insert_one(ground_doc)
            # Add to in-memory list so subsequent issues in the same batch see it
            all_existing_grounds.append({"ground_id": ground_doc["ground_id"], "title": issue_title})
        count += 1

    return {"synced_count": count}


@router.get("/cases/{case_id}/summary", response_model=dict)
async def get_pipeline_summary(case_id: str, request: Request):
    """Return a high-level summary of the pipeline state for a case."""
    user = await get_current_user(request)

    case = await db.cases.find_one(
        {"case_id": case_id, "user_id": user.user_id}, {"_id": 0}
    )
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")

    case_extract = await db.case_extracts.find_one(
        {"case_id": case_id, "user_id": user.user_id}, {"_id": 0}
    )

    document_extract_count = await db.document_extracts.count_documents(
        {"case_id": case_id, "user_id": user.user_id}
    )

    issue_classification_count = await db.issue_classifications.count_documents(
        {"case_id": case_id, "user_id": user.user_id}
    )

    issue_verification_count = await db.issue_verifications.count_documents(
        {"case_id": case_id, "user_id": user.user_id}
    )

    synced_grounds_count = await db.grounds_of_merit.count_documents(
        {"case_id": case_id, "user_id": user.user_id, "source_mode": "derived"}
    )

    pipeline_drafted_reports_count = await db.reports.count_documents(
        {
            "case_id": case_id,
            "user_id": user.user_id,
            "content.draft_source": "pipeline",
        }
    )

    total_reports_count = await db.reports.count_documents(
        {
            "case_id": case_id,
            "user_id": user.user_id,
        }
    )

    return {
        "case_extract_present": case_extract is not None,
        "case_extract_id": case_extract.get("case_extract_id") if case_extract else None,
        "case_extract_created_at": case_extract.get("created_at") if case_extract else None,
        "case_extract_verification_status": case_extract.get("verification_status") if case_extract else None,
        "document_extract_count": document_extract_count,
        "issue_classification_count": issue_classification_count,
        "issue_verification_count": issue_verification_count,
        "synced_grounds_count": synced_grounds_count,
        "pipeline_drafted_reports_count": pipeline_drafted_reports_count,
        "total_reports_count": total_reports_count,
    }


@router.post("/cases/{case_id}/refresh-all", response_model=dict)
async def refresh_all_pipeline(case_id: str, payload: RefreshPipelineRequest, request: Request):
    """
    One-click orchestration route for the staged pipeline.
    """
    user = await get_current_user(request)

    case = await db.cases.find_one(
        {"case_id": case_id, "user_id": user.user_id},
        {"_id": 0}
    )
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")

    documents = await db.documents.find(
        {"case_id": case_id, "user_id": user.user_id},
        {"_id": 0, "file_data": 0}
    ).to_list(1000)

    extract_result = await _ensure_document_extracts(case, documents)
    case_extract_result = await _refresh_case_extract(case)

    case_extract = await db.case_extracts.find_one(
        {"case_id": case_id, "user_id": user.user_id},
        {"_id": 0}
    )
    classify_result = await _classify_issues(case, case_extract)

    verify_result = await _verify_top_issues(case, payload.verify_limit)
    synced_count = await _sync_pipeline_projection_to_grounds(case_id, user.user_id)
    # DO_NOT_UNDO — 3 Apr 2026: cleanup after EVERY sync, no exceptions
    from services.ground_dedup import cleanup_duplicate_grounds
    await cleanup_duplicate_grounds(db, case_id, user.user_id)

    return {
        "message": "Pipeline refresh completed",
        "documents": {
            "total_documents": len(documents),
            **extract_result,
        },
        "case_extract": case_extract_result,
        "classification": classify_result,
        "verification": verify_result,
        "projection": {
            "synced_count": synced_count,
        },
    }


@router.get("/dashboard-summary", response_model=dict)
async def get_pipeline_dashboard_summary(request: Request):
    """Portfolio-level pipeline summary across all user cases."""
    user = await get_current_user(request)

    cases = await db.cases.find(
        {"user_id": user.user_id},
        {"_id": 0, "case_id": 1}
    ).to_list(5000)

    case_ids = [c["case_id"] for c in cases]

    if not case_ids:
        return {
            "total_cases": 0,
            "cases_with_case_extract": 0,
            "cases_with_classified_issues": 0,
            "cases_with_verified_issues": 0,
            "cases_with_pipeline_reports": 0,
        }

    case_extract_ids = await db.case_extracts.distinct(
        "case_id",
        {"user_id": user.user_id, "case_id": {"$in": case_ids}}
    )

    classified_issue_case_ids = await db.issue_classifications.distinct(
        "case_id",
        {"user_id": user.user_id, "case_id": {"$in": case_ids}}
    )

    verified_issue_case_ids = await db.issue_verifications.distinct(
        "case_id",
        {"user_id": user.user_id, "case_id": {"$in": case_ids}}
    )

    pipeline_report_case_ids = await db.reports.distinct(
        "case_id",
        {
            "user_id": user.user_id,
            "case_id": {"$in": case_ids},
            "content.draft_source": "pipeline",
        }
    )

    return {
        "total_cases": len(case_ids),
        "cases_with_case_extract": len(case_extract_ids),
        "cases_with_classified_issues": len(classified_issue_case_ids),
        "cases_with_verified_issues": len(verified_issue_case_ids),
        "cases_with_pipeline_reports": len(pipeline_report_case_ids),
    }


@router.get("/cases/{case_id}/staleness", response_model=dict)
async def get_pipeline_staleness(case_id: str, request: Request):
    """Check whether pipeline artifacts are stale relative to source materials."""
    user = await get_current_user(request)

    case = await db.cases.find_one(
        {"case_id": case_id, "user_id": user.user_id},
        {"_id": 0, "case_id": 1, "updated_at": 1}
    )
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")

    documents = await db.documents.find(
        {"case_id": case_id, "user_id": user.user_id},
        {"_id": 0, "document_id": 1, "uploaded_at": 1}
    ).to_list(1000)

    doc_extracts = await db.document_extracts.find(
        {"case_id": case_id, "user_id": user.user_id},
        {"_id": 0, "document_id": 1, "created_at": 1}
    ).to_list(1000)

    case_extract = await db.case_extracts.find_one(
        {"case_id": case_id, "user_id": user.user_id},
        {"_id": 0, "created_at": 1}
    )

    issue_classifications = await db.issue_classifications.find(
        {"case_id": case_id, "user_id": user.user_id},
        {"_id": 0, "created_at": 1}
    ).to_list(1000)

    issue_verifications = await db.issue_verifications.find(
        {"case_id": case_id, "user_id": user.user_id},
        {"_id": 0, "created_at": 1}
    ).to_list(1000)

    reports = await db.reports.find(
        {"case_id": case_id, "user_id": user.user_id, "content.draft_source": "pipeline"},
        {"_id": 0, "generated_at": 1}
    ).to_list(1000)

    def _to_iso(value):
        if not value:
            return None
        if isinstance(value, str):
            return value
        try:
            return value.isoformat()
        except Exception:
            return str(value)

    def _latest_iso(items, field):
        values = [i.get(field) for i in items if i.get(field)]
        if not values:
            return None
        values = [v if isinstance(v, str) else v.isoformat() for v in values]
        return max(values)

    latest_document_upload = _latest_iso(documents, "uploaded_at")
    latest_document_extract = _latest_iso(doc_extracts, "created_at")
    latest_issue_classification = _latest_iso(issue_classifications, "created_at")
    latest_issue_verification = _latest_iso(issue_verifications, "created_at")
    latest_pipeline_report = _latest_iso(reports, "generated_at")
    case_extract_created_at = _to_iso(case_extract.get("created_at")) if case_extract else None

    extract_missing_for_documents = []
    extract_map = {d.get("document_id"): d for d in doc_extracts}
    for doc in documents:
        if doc.get("document_id") not in extract_map:
            extract_missing_for_documents.append(doc.get("document_id"))

    documents_newer_than_extracts = False
    if latest_document_upload and latest_document_extract:
        documents_newer_than_extracts = latest_document_upload > latest_document_extract
    elif latest_document_upload and not latest_document_extract:
        documents_newer_than_extracts = True

    case_extract_stale = False
    if latest_document_extract and case_extract_created_at:
        case_extract_stale = latest_document_extract > case_extract_created_at
    elif latest_document_extract and not case_extract_created_at:
        case_extract_stale = True

    classifications_stale = False
    if case_extract_created_at and latest_issue_classification:
        classifications_stale = case_extract_created_at > latest_issue_classification
    elif case_extract_created_at and not latest_issue_classification:
        classifications_stale = True

    verifications_stale = False
    if latest_issue_classification and latest_issue_verification:
        verifications_stale = latest_issue_classification > latest_issue_verification
    elif latest_issue_classification and not latest_issue_verification:
        verifications_stale = True

    reports_stale = False
    if latest_issue_verification and latest_pipeline_report:
        reports_stale = latest_issue_verification > latest_pipeline_report
    elif latest_issue_verification and not latest_pipeline_report:
        reports_stale = True

    overall_stale = any([
        len(extract_missing_for_documents) > 0,
        documents_newer_than_extracts,
        case_extract_stale,
        classifications_stale,
        verifications_stale,
        reports_stale,
    ])

    return {
        "overall_stale": overall_stale,
        "extract_missing_for_documents": extract_missing_for_documents,
        "documents_newer_than_extracts": documents_newer_than_extracts,
        "case_extract_stale": case_extract_stale,
        "classifications_stale": classifications_stale,
        "verifications_stale": verifications_stale,
        "reports_stale": reports_stale,
        "latest_document_upload": latest_document_upload,
        "latest_document_extract": latest_document_extract,
        "case_extract_created_at": case_extract_created_at,
        "latest_issue_classification": latest_issue_classification,
        "latest_issue_verification": latest_issue_verification,
        "latest_pipeline_report": latest_pipeline_report,
    }


@router.post("/cases/{case_id}/reports/draft", response_model=dict)
async def draft_report(case_id: str, request: Request):
    user = await get_current_user(request)
    body = await request.json()
    report_type = body.get("report_type", "full_report")

    case = await db.cases.find_one({"case_id": case_id, "user_id": user.user_id}, {"_id": 0})
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")

    case_extract = await db.case_extracts.find_one({"case_id": case_id, "user_id": user.user_id}, {"_id": 0})
    if not case_extract:
        raise HTTPException(status_code=400, detail="Case extract not found")

    issues = await db.issue_classifications.find({"case_id": case_id, "user_id": user.user_id}, {"_id": 0}).to_list(200)
    verifications = await db.issue_verifications.find({"case_id": case_id, "user_id": user.user_id}, {"_id": 0}).to_list(200)

    drafted = await draft_report_from_verified_material(case, case_extract, issues, verifications, report_type)

    return {
        "content": drafted["content"],
        "metadata": drafted["metadata"],
    }
