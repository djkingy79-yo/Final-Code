"""
services/pipeline_actions.py

Shared pipeline stage helpers. Extracted VERBATIM from routers/pipeline_staged.py
on 24 Feb 2026 so that both the staged router and services/pipeline_orchestrator.py
can import these helpers from the service layer instead of services reaching
up into the router layer.

NO BEHAVIOUR CHANGES. Pure move/refactor. Function bodies are byte-for-byte
identical to the original router-scoped definitions. Callers continue to use
the same private, underscore-prefixed names.

Original file: backend/routers/pipeline_staged.py (lines 12–17, 36–60, 63–359).
"""

from datetime import datetime, timezone
import logging
import uuid

from config import db
from services.pipeline import (
    extract_document_artifacts,
    classify_case_issues,
    verify_issue,
)
from services.pipeline_models import CaseExtract


logger = logging.getLogger(__name__)


def _safe_isoformat(d, key):
    """Safely convert a datetime field to isoformat string."""
    if key not in d:
        d[key] = datetime.now(timezone.utc).isoformat()
    elif hasattr(d[key], "isoformat"):
        d[key] = d[key].isoformat()


def _issue_priority_rank(issue: dict) -> tuple:
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
    """ — 3 Apr 2026: If issues already exist, DO NOT re-classify.
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
    """ — Sync staged issues/verifications into grounds_of_merit.
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
