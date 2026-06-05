#  — cases router. All endpoints in this file are approved and must be preserved.
"""
Criminal Appeal AI - Cases Router
"""
from fastapi import APIRouter, HTTPException, Request
from typing import List
from datetime import datetime, timezone

from config import db
from models import Case, CaseCreate, ChecklistItem, DEFAULT_CHECKLIST
from auth_utils import get_current_user
from services.offence_helpers import validate_jurisdiction_completeness

router = APIRouter(prefix="/api/cases", tags=["cases"])


@router.get("", response_model=List[dict])
async def get_cases(request: Request):
    """Get all cases for current user"""
    user = await get_current_user(request)
    cases = await db.cases.find({"user_id": user.user_id}, {"_id": 0}).sort("updated_at", -1).to_list(100)

    if not cases:
        return cases

    # Optimised: Batch count queries using aggregation instead of N+1 pattern
    case_ids = [case["case_id"] for case in cases]

    doc_counts = await db.documents.aggregate([
        {"$match": {"case_id": {"$in": case_ids}}},
        {"$group": {"_id": "$case_id", "count": {"$sum": 1}}}
    ]).to_list(100)

    event_counts = await db.timeline_events.aggregate([
        {"$match": {"case_id": {"$in": case_ids}}},
        {"$group": {"_id": "$case_id", "count": {"$sum": 1}}}
    ]).to_list(100)

    doc_map = {d["_id"]: d["count"] for d in doc_counts}
    event_map = {e["_id"]: e["count"] for e in event_counts}

    for case in cases:
        case["document_count"] = doc_map.get(case["case_id"], 0)
        case["event_count"] = event_map.get(case["case_id"], 0)

    return cases


@router.post("", response_model=dict)
async def create_case(case_data: CaseCreate, request: Request):
    """Create a new case"""
    user = await get_current_user(request)

    case = Case(
        user_id=user.user_id,
        **case_data.model_dump()
    )

    case_dict = case.model_dump()
    case_dict["created_at"] = case_dict["created_at"].isoformat()
    case_dict["updated_at"] = case_dict["updated_at"].isoformat()

    await db.cases.insert_one(case_dict)

    # Initialize checklist for new case
    for item in DEFAULT_CHECKLIST:
        checklist_item = ChecklistItem(
            case_id=case.case_id,
            user_id=user.user_id,
            **item
        )
        item_dict = checklist_item.model_dump()
        item_dict["created_at"] = item_dict["created_at"].isoformat()
        await db.checklist_items.insert_one(item_dict)

    created_case = await db.cases.find_one({"case_id": case.case_id}, {"_id": 0})
    return created_case


@router.get("/{case_id}", response_model=dict)
async def get_case(case_id: str, request: Request):
    """Get a specific case"""
    user = await get_current_user(request)

    case = await db.cases.find_one({"case_id": case_id, "user_id": user.user_id}, {"_id": 0})
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")

    case["document_count"] = await db.documents.count_documents({"case_id": case_id})
    case["event_count"] = await db.timeline_events.count_documents({"case_id": case_id})

    # Inject jurisdiction completeness warnings for UI display
    state = case.get("state", "")
    offence_cat = case.get("offence_category", "")
    metadata_warnings = []
    if not state:
        metadata_warnings.append("State/jurisdiction is not set. Reports may default to generic analysis without state-specific legislation.")
    if not offence_cat:
        metadata_warnings.append("Offence category is not set. Reports will lack offence-specific legislation references and elements to prove.")
    if not case.get("offence_type"):
        metadata_warnings.append("Specific offence type is not set. The AI will need to infer the offence from case documents, which reduces accuracy.")
    jurisdiction_warnings = validate_jurisdiction_completeness(state, offence_cat) if state and offence_cat else []
    case["metadata_warnings"] = metadata_warnings
    case["jurisdiction_warnings"] = jurisdiction_warnings

    return case


@router.put("/{case_id}", response_model=dict)
async def update_case(case_id: str, case_data: CaseCreate, request: Request):
    """Update a case"""
    user = await get_current_user(request)

    result = await db.cases.update_one(
        {"case_id": case_id, "user_id": user.user_id},
        {"$set": {
            **case_data.model_dump(),
            "updated_at": datetime.now(timezone.utc).isoformat()
        }}
    )

    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="Case not found")

    return await db.cases.find_one({"case_id": case_id}, {"_id": 0})


@router.delete("/{case_id}")
async def delete_case(case_id: str, request: Request):
    """Delete a case and all related data"""
    user = await get_current_user(request)

    await db.documents.delete_many({"case_id": case_id, "user_id": user.user_id})
    await db.timeline_events.delete_many({"case_id": case_id, "user_id": user.user_id})
    await db.reports.delete_many({"case_id": case_id, "user_id": user.user_id})
    await db.notes.delete_many({"case_id": case_id, "user_id": user.user_id})
    await db.grounds_of_merit.delete_many({"case_id": case_id, "user_id": user.user_id})
    await db.deadlines.delete_many({"case_id": case_id, "user_id": user.user_id})
    await db.checklist_items.delete_many({"case_id": case_id, "user_id": user.user_id})

    result = await db.cases.delete_one({"case_id": case_id, "user_id": user.user_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Case not found")

    return {"message": "Case deleted"}


@router.get("/{case_id}/ai-cost")
async def get_case_ai_cost(case_id: str, request: Request):
    """Return the estimated AI cost for this case, broken down by report_type.

    Uses the `ai_usage` collection populated by services.ai_usage_tracker.
    Owner-only: non-owners of the case get 404 to avoid leaking data.
    """
    user = await get_current_user(request)

    # Authorise
    case = await db.cases.find_one({"case_id": case_id, "user_id": user.user_id}, {"_id": 0, "case_id": 1})
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")

    totals_rows = await db.ai_usage.aggregate([
        {"$match": {"case_id": case_id}},
        {"$group": {
            "_id": None,
            "calls": {"$sum": 1},
            "cost_usd": {"$sum": "$cost_usd_est"},
            "input_tokens": {"$sum": "$input_tokens_est"},
            "output_tokens": {"$sum": "$output_tokens_est"},
        }},
    ]).to_list(1)
    totals = totals_rows[0] if totals_rows else {"calls": 0, "cost_usd": 0.0, "input_tokens": 0, "output_tokens": 0}
    totals.pop("_id", None)
    totals["cost_usd"] = round(totals["cost_usd"], 4)

    by_report = await db.ai_usage.aggregate([
        {"$match": {"case_id": case_id, "report_type": {"$ne": None}}},
        {"$group": {"_id": "$report_type", "calls": {"$sum": 1}, "cost_usd": {"$sum": "$cost_usd_est"}}},
        {"$project": {"_id": 0, "report_type": "$_id", "calls": 1, "cost_usd": {"$round": ["$cost_usd", 4]}}},
        {"$sort": {"cost_usd": -1}},
    ]).to_list(20)

    return {
        "case_id": case_id,
        "totals": totals,
        "by_report_type": by_report,
        "note": "Estimated cost based on locally counted tokens and OpenAI's Feb 2026 rate card. Actual billing on your OpenAI dashboard.",
    }



# ── Evidence Profile — feeds services/appeal_strength.py realism scoring ──
# The 19 booleans below describe what corroborating material is actually on
# the case record. Used to (a) cap or adjust ground viability post-generation,
# (b) compute verdict-robustness / Crown-strength / record-support and (c)
# produce a forensic "why this may fail" explanation for each ground.

EVIDENCE_PROFILE_FIELDS = [
    # Record anchors
    "has_trial_transcript",
    "has_sentencing_remarks",
    "has_psychiatric_reports",
    "has_counsel_affidavit",
    "has_juror_affidavit",
    "has_expert_reports",
    "has_judge_alone_material",
    "has_pretrial_publicity_material",
    # Crown case strength indicators
    "has_forensic_evidence",
    "has_direct_evidence",
    "has_strong_circumstantial_evidence",
    "multiple_consistent_witnesses",
    "confession_or_admission",
    "cctv_or_audio",
    "post_offence_conduct_supports_guilt",
    # Defence / weakness indicators
    "disputed_identity",
    "disputed_intent",
    "competing_psychiatric_opinions",
    "no_eyewitnesses",
]


@router.get("/{case_id}/evidence-profile")
async def get_evidence_profile(case_id: str, request: Request):
    """Return the evidence profile flags for a case. All False if never saved."""
    user = await get_current_user(request)
    case = await db.cases.find_one(
        {"case_id": case_id, "user_id": user.user_id},
        {"_id": 0, **{f: 1 for f in EVIDENCE_PROFILE_FIELDS}},
    )
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
    return {f: bool(case.get(f, False)) for f in EVIDENCE_PROFILE_FIELDS}


@router.put("/{case_id}/evidence-profile")
async def set_evidence_profile(case_id: str, request: Request):
    """Save the evidence profile. Re-syncs grounds so realism scoring updates
    immediately without waiting for the next pipeline run."""
    user = await get_current_user(request)
    try:
        payload = await request.json()
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid JSON body")

    updates = {f: bool(payload.get(f, False)) for f in EVIDENCE_PROFILE_FIELDS}
    updates["evidence_profile_updated_at"] = datetime.now(timezone.utc).isoformat()

    result = await db.cases.update_one(
        {"case_id": case_id, "user_id": user.user_id},
        {"$set": updates},
    )
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Case not found")

    # Kick grounds re-sync so realism scoring reflects the new profile right
    # away. Fire-and-forget — UI will show updated badges on next /grounds fetch.
    try:
        from routers.grounds import _sync_pipeline_issues_to_grounds
        await _sync_pipeline_issues_to_grounds(case_id, user.user_id)
    except Exception:
        # Non-fatal — save still succeeds; realism will update on next sync.
        pass

    return {"ok": True, "profile": {f: updates[f] for f in EVIDENCE_PROFILE_FIELDS}}
