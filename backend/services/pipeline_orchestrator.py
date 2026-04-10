# ===========================================================================
# Pipeline Orchestration Helpers for Report Generation
# Extracted from server.py — pipeline freshness, document extraction, issue classification
# ===========================================================================

import uuid
import asyncio
from datetime import datetime, timezone

from config import db, logger
from services.pipeline import (
    extract_document_artifacts,
    classify_case_issues,
    verify_issue,
)
from services.pipeline_models import CaseExtract
from services.llm_service import call_llm_with_fallback
from routers.pipeline_staged import (
    _ensure_document_extracts as _staged_ensure_extracts,
    _refresh_case_extract as _staged_refresh_case,
    _classify_issues as _staged_classify,
    _verify_top_issues as _staged_verify,
    _sync_pipeline_projection_to_grounds as _staged_sync_grounds,
)


async def _ensure_document_extracts_for_case(case: dict, documents: list) -> int:
    """Ensure every uploaded document has a staged extraction record."""
    created = 0
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
        created += 1
    return created


async def _refresh_case_extract_for_case(case: dict) -> dict:
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


async def _ensure_issue_classifications(case: dict, case_extract: dict) -> list[dict]:
    """Run staged issue classification and persist results.
    
    DO_NOT_UNDO — 3 Apr 2026: If issues already exist for this case, DO NOT re-classify.
    Re-classification was the ROOT CAUSE of grounds multiplying — every LLM call generates
    slightly different titles which slip past dedup and create new grounds.
    Only classify if zero issues exist (first-time analysis).
    """
    from services.ground_dedup import is_ground_duplicate, normalise_au_spelling
    
    # Check if issues already exist — if so, return them without re-classifying
    existing_issues = await db.issue_classifications.find(
        {"case_id": case["case_id"], "user_id": case["user_id"]},
        {"_id": 0}
    ).to_list(500)
    
    # Check if enough issues already exist — only skip if 8+ exist (healthy count)
    # If fewer than 8, re-classify to find missing grounds (previous dedup may have been too aggressive)
    if len(existing_issues) >= 8:
        logger.info(f"Skipping re-classification for case {case['case_id']}: {len(existing_issues)} issues already exist (>= 8)")
        return existing_issues
    
    logger.info(f"Re-classifying case {case['case_id']}: only {len(existing_issues)} issues exist (< 8), looking for more")
    issues = await classify_case_issues(case, case_extract)
    
    persisted = list(existing_issues)  # Start with existing issues for dedup comparison
    for issue in issues:
        issue_dict = issue.model_dump()
        issue_dict["created_at"] = issue_dict["created_at"].isoformat()
        issue_title = normalise_au_spelling((issue.title or "").strip())
        issue_dict["title"] = issue_title
        
        # Fuzzy match against ALL existing + newly-persisted issues
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


async def _pipeline_artifacts_missing_or_stale(case: dict, documents: list) -> bool:
    """
    Conservative staleness check.
    Returns True if:
    - no case_extract exists, or
    - no issue classifications exist, or
    - any uploaded document lacks a document_extract
    """
    case_extract = await db.case_extracts.find_one(
        {"case_id": case["case_id"], "user_id": case["user_id"]},
        {"_id": 0}
    )
    if not case_extract:
        return True

    issue_count = await db.issue_classifications.count_documents(
        {"case_id": case["case_id"], "user_id": case["user_id"]}
    )
    if issue_count == 0:
        return True

    for document in documents:
        existing = await db.document_extracts.find_one(
            {
                "case_id": case["case_id"],
                "document_id": document["document_id"],
                "user_id": case["user_id"],
            },
            {"_id": 0}
        )
        if not existing:
            return True

    return False


async def _sync_pipeline_projection_to_grounds(case: dict) -> int:
    """
    Sync staged issues/verifications into grounds_of_merit so report consumers
    and existing frontend views remain aligned.

    DO_NOT_UNDO — 3 Apr 2026: HARD CAP on ground creation.
    If grounds already exist, NEVER create more than existing_count + 2.
    This prevents the recurring multiplication bug permanently.
    """
    from services.ground_dedup import is_ground_duplicate, normalise_au_spelling

    issues = await db.issue_classifications.find(
        {"case_id": case["case_id"], "user_id": case["user_id"]},
        {"_id": 0}
    ).to_list(500)

    # Pre-load existing grounds for fuzzy matching
    all_existing_grounds = await db.grounds_of_merit.find(
        {"case_id": case["case_id"], "user_id": case["user_id"]},
        {"_id": 0, "ground_id": 1, "title": 1},
    ).to_list(200)

    # DO_NOT_UNDO — HARD CAP enforcement. If grounds already exist,
    # NEVER create more than existing_count + 2. This prevents the
    # recurring multiplication bug permanently.
    initial_ground_count = len(all_existing_grounds)
    max_new_grounds = 2 if initial_ground_count > 0 else 50
    new_grounds_created = 0

    synced = 0
    for issue in issues:
        verification = await db.issue_verifications.find_one(
            {"case_id": case["case_id"], "issue_id": issue["issue_id"], "user_id": case["user_id"]},
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

        if not existing_ground:
            logger.info(f"Sync: new ground '{issue_title[:50]}'")

        ground_doc = {
            "case_id": case["case_id"],
            "user_id": case["user_id"],
            "title": existing_ground["title"] if existing_ground else issue_title,
            "ground_type": issue.get("ground_type", "other"),
            "description": issue.get("description", ""),
            "strength": (verification or {}).get("legitimacy_scores", {}).get(
                "rating", issue.get("classification_confidence", "moderate")
            ),
            "status": "investigated" if verification else "identified",
            "supporting_evidence": (verification or {}).get("supporting_items", []),
            "law_sections": (verification or {}).get("law_sections", []) or issue.get("law_sections", []),
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
            # DO_NOT_UNDO — Hard cap check: skip if at limit
            if new_grounds_created >= max_new_grounds:
                logger.info(f"Sync: HARD CAP reached ({initial_ground_count}+{max_new_grounds}). Skipping '{issue_title[:50]}'")
                continue
            ground_doc["ground_id"] = f"gnd_{uuid.uuid4().hex[:12]}"
            ground_doc["created_at"] = datetime.now(timezone.utc).isoformat()
            await db.grounds_of_merit.insert_one(ground_doc)
            all_existing_grounds.append({"ground_id": ground_doc["ground_id"], "title": issue_title})
            new_grounds_created += 1

        synced += 1
    return synced


async def _refresh_pipeline_for_reporting(case: dict, documents: list, report_type: str = "quick_summary") -> dict:
    """
    Reporting-time pipeline refresh:
    1. ensure document extracts
    2. refresh case extract
    3. ensure issue classifications
    4. optionally auto-verify top issues by report tier
    5. sync projection into grounds
    6. DO_NOT_UNDO — safety net dedup cleanup after sync
    """
    from services.ground_dedup import cleanup_duplicate_grounds, cleanup_duplicate_issues

    extracted_count = await _ensure_document_extracts_for_case(case, documents)
    case_extract = await _refresh_case_extract_for_case(case)
    issues = await _ensure_issue_classifications(case, case_extract)

    auto_verify_limit = _auto_verification_limit_for_report_type(report_type)
    selected_issues = await _select_issues_for_auto_verification(case, auto_verify_limit)
    auto_verify_result = await _auto_verify_selected_issues(case, selected_issues)

    synced_count = await _sync_pipeline_projection_to_grounds(case)

    # Safety net: clean up any duplicates that may have slipped through
    await cleanup_duplicate_grounds(db, case["case_id"], case["user_id"])
    await cleanup_duplicate_issues(db, case["case_id"], case["user_id"])

    return {
        "extracted_count": extracted_count,
        "classified_count": len(issues),
        "synced_count": synced_count,
        "auto_verify_limit": auto_verify_limit,
        "auto_verify_result": auto_verify_result,
    }


def _issue_priority_rank(issue: dict) -> tuple:
    """Lower tuple sorts earlier."""
    preferred_ground_order = {
        "judicial_error": 0,
        "procedural_error": 1,
        "miscarriage_of_justice": 2,
        "fresh_evidence": 3,
        "sentencing_error": 4,
        "jury_irregularity": 5,
        "ineffective_counsel": 6,
        "prosecution_misconduct": 7,
        "constitutional_violation": 8,
        "other": 9,
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


async def _select_issues_for_auto_verification(case: dict, limit: int) -> list[dict]:
    """Select issues that do not yet have verifications."""
    if limit <= 0:
        return []
    issues = await db.issue_classifications.find(
        {"case_id": case["case_id"], "user_id": case["user_id"]}, {"_id": 0}
    ).to_list(500)
    if not issues:
        return []
    eligible = []
    for issue in issues:
        existing_verification = await db.issue_verifications.find_one(
            {"case_id": case["case_id"], "issue_id": issue["issue_id"], "user_id": case["user_id"]},
            {"_id": 0}
        )
        if existing_verification:
            continue
        eligible.append(issue)
    eligible.sort(key=_issue_priority_rank)
    return eligible[:limit]


async def _auto_verify_selected_issues(case: dict, selected_issues: list[dict]) -> dict:
    """Verify selected issues and persist results."""
    if not selected_issues:
        return {"attempted": 0, "verified": 0, "failed": 0}
    case_extract = await db.case_extracts.find_one(
        {"case_id": case["case_id"], "user_id": case["user_id"]}, {"_id": 0}
    )
    if not case_extract:
        return {"attempted": len(selected_issues), "verified": 0, "failed": len(selected_issues)}
    supporting_context = {
        "facts": case_extract.get("merged_facts", []),
        "events": case_extract.get("merged_events", []),
        "findings": case_extract.get("merged_findings", []),
    }
    verified = 0
    failed = 0
    for issue in selected_issues:
        try:
            verification = await verify_issue(case, issue, supporting_context)
            verification_dict = verification.model_dump()
            verification_dict["created_at"] = verification_dict["created_at"].isoformat()
            await db.issue_verifications.update_one(
                {"case_id": case["case_id"], "issue_id": issue["issue_id"], "user_id": case["user_id"]},
                {"$set": verification_dict},
                upsert=True,
            )
            verified += 1
        except Exception as e:
            logger.warning(f"Auto-verification failed for case {case['case_id']} issue {issue.get('issue_id')}: {e}")
            failed += 1
    return {"attempted": len(selected_issues), "verified": verified, "failed": failed}


def _auto_verification_limit_for_report_type(report_type: str) -> int:
    if report_type in ("full_report", "full_detailed"):
        return 3
    if report_type in ("extensive_report", "extensive_log"):
        return 6
    return 0


async def _check_case_pipeline_staleness(case_id: str, user_id: str) -> dict:
    """Check pipeline staleness without needing a Request object."""
    documents = await db.documents.find(
        {"case_id": case_id, "user_id": user_id},
        {"_id": 0, "document_id": 1, "uploaded_at": 1}
    ).to_list(1000)

    doc_extracts = await db.document_extracts.find(
        {"case_id": case_id, "user_id": user_id},
        {"_id": 0, "document_id": 1, "created_at": 1}
    ).to_list(1000)

    case_extract = await db.case_extracts.find_one(
        {"case_id": case_id, "user_id": user_id},
        {"_id": 0, "created_at": 1}
    )

    issue_classifications = await db.issue_classifications.find(
        {"case_id": case_id, "user_id": user_id},
        {"_id": 0, "created_at": 1}
    ).to_list(1000)

    issue_verifications = await db.issue_verifications.find(
        {"case_id": case_id, "user_id": user_id},
        {"_id": 0, "created_at": 1}
    ).to_list(1000)

    reports = await db.reports.find(
        {"case_id": case_id, "user_id": user_id, "content.draft_source": "pipeline"},
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

    extract_map = {d.get("document_id"): d for d in doc_extracts}
    extract_missing = [d.get("document_id") for d in documents if d.get("document_id") not in extract_map]

    documents_newer = (latest_document_upload > latest_document_extract) if (latest_document_upload and latest_document_extract) else bool(latest_document_upload and not latest_document_extract)
    case_extract_stale = (latest_document_extract > case_extract_created_at) if (latest_document_extract and case_extract_created_at) else bool(latest_document_extract and not case_extract_created_at)
    classifications_stale = (case_extract_created_at > latest_issue_classification) if (case_extract_created_at and latest_issue_classification) else bool(case_extract_created_at and not latest_issue_classification)
    verifications_stale = (latest_issue_classification > latest_issue_verification) if (latest_issue_classification and latest_issue_verification) else bool(latest_issue_classification and not latest_issue_verification)
    reports_stale = (latest_issue_verification > latest_pipeline_report) if (latest_issue_verification and latest_pipeline_report) else bool(latest_issue_verification and not latest_pipeline_report)

    overall_stale = any([len(extract_missing) > 0, documents_newer, case_extract_stale, classifications_stale, verifications_stale, reports_stale])

    return {
        "overall_stale": overall_stale,
        "extract_missing_for_documents": extract_missing,
        "documents_newer_than_extracts": documents_newer,
        "case_extract_stale": case_extract_stale,
        "classifications_stale": classifications_stale,
        "verifications_stale": verifications_stale,
        "reports_stale": reports_stale,
    }


async def _enforce_pipeline_freshness(case_id: str, user_id: str, auto_refresh: bool = False) -> dict:
    """Ensure pipeline artifacts are current before report generation."""
    staleness = await _check_case_pipeline_staleness(case_id, user_id)

    if not staleness.get("overall_stale"):
        return {"status": "fresh", "staleness": staleness}

    if not auto_refresh:
        return {"status": "stale", "staleness": staleness}

    # Auto-refresh pipeline
    case = await db.cases.find_one({"case_id": case_id, "user_id": user_id}, {"_id": 0})
    if not case:
        return {"status": "stale", "staleness": staleness}

    docs = await db.documents.find(
        {"case_id": case_id, "user_id": user_id},
        {"_id": 0, "file_data": 0}
    ).to_list(1000)

    extract_result = await _staged_ensure_extracts(case, docs)
    case_extract_result = await _staged_refresh_case(case)
    ce = await db.case_extracts.find_one({"case_id": case_id, "user_id": user_id}, {"_id": 0})
    classify_result = await _staged_classify(case, ce)
    verify_result = await _staged_verify(case, 3)
    synced = await _staged_sync_grounds(case_id, user_id)

    return {
        "status": "refreshed",
        "staleness": staleness,
        "refresh_result": {
            "documents": extract_result,
            "case_extract": case_extract_result,
            "classification": classify_result,
            "verification": verify_result,
            "projection": {"synced_count": synced},
        },
    }


async def _load_issue_arguments(case_id: str, user_id: str) -> list:
    return await db.issue_arguments.find(
        {"case_id": case_id, "user_id": user_id},
        {"_id": 0}
    ).to_list(500)


async def _load_submission_draft(case_id: str, user_id: str):
    return await db.submissions_drafts.find_one(
        {"case_id": case_id, "user_id": user_id},
        {"_id": 0}
    )


