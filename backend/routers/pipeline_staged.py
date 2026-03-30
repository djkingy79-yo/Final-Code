# DO NOT UNDO — staged pipeline router. Additive module.
from fastapi import APIRouter, HTTPException, Request
from datetime import datetime, timezone

from config import db
from auth_utils import get_current_user
from services.pipeline import (
    extract_document_artifacts,
    classify_case_issues,
    verify_issue,
    draft_report_from_verified_material,
)
from services.pipeline_models import CaseExtract

router = APIRouter(prefix="/api/pipeline", tags=["pipeline-staged"])


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
    extract_dict["created_at"] = extract_dict["created_at"].isoformat()

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
    case_extract_dict["created_at"] = case_extract_dict["created_at"].isoformat()

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

    inserted = 0
    for issue in issues:
        issue_dict = issue.model_dump()
        issue_dict["created_at"] = issue_dict["created_at"].isoformat()
        await db.issue_classifications.update_one(
            {"case_id": case_id, "user_id": user.user_id, "title": issue.title, "ground_type": issue.ground_type},
            {"$set": issue_dict},
            upsert=True,
        )
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
    verification_dict["created_at"] = verification_dict["created_at"].isoformat()

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

    count = 0
    for issue in issues:
        verification = await db.issue_verifications.find_one(
            {"case_id": case_id, "issue_id": issue["issue_id"], "user_id": user.user_id},
            {"_id": 0}
        )

        ground_doc = {
            "case_id": case_id,
            "user_id": user.user_id,
            "title": issue.get("title"),
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

        await db.grounds_of_merit.update_one(
            {
                "case_id": case_id,
                "user_id": user.user_id,
                "title": ground_doc["title"],
                "ground_type": ground_doc["ground_type"],
            },
            {"$set": ground_doc, "$setOnInsert": {"ground_id": f"gnd_{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}_{count}", "created_at": datetime.now(timezone.utc).isoformat()}},
            upsert=True,
        )
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
