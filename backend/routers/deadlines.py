# DO NOT UNDO — deadlines router. All endpoints in this file are approved and must be preserved.
"""
Criminal Appeal AI - Deadlines, Checklist & Case Strength Router
ADDITIVE HARDENING PATCH
"""
from fastapi import APIRouter, HTTPException, Request
from typing import List
from datetime import datetime, timezone
import logging

from config import db
from auth_utils import get_current_user
from models import Deadline, DeadlineCreate, ChecklistItem, DEFAULT_CHECKLIST

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api", tags=["deadlines"])


# ============================================================================
# INTERNAL HELPERS
# ============================================================================

def _safe_percentage(numerator: int, denominator: int) -> int:
    if denominator <= 0:
        return 0
    return int((numerator / denominator) * 100)


def _count_completed(items: list) -> int:
    return len([item for item in items if item.get("is_completed")])


def _documents_with_text(documents: list) -> int:
    return len([d for d in documents if d.get("content_text")])


def _ground_breakdown(grounds: list) -> dict:
    breakdown = {"strong": 0, "moderate": 0, "weak": 0}
    for g in grounds:
        strength = g.get("strength", "moderate")
        if strength not in breakdown:
            strength = "moderate"
        breakdown[strength] += 1
    return breakdown


def _calculate_readiness_scores(grounds: list, documents: list, timeline: list, checklist: list) -> dict:
    """
    This is a workflow / preparation score.
    It is NOT a legal merits predictor.
    """
    strength_scores = {"strong": 3, "moderate": 2, "weak": 1}

    # Grounds preparation score
    grounds_score = 0
    breakdown = _ground_breakdown(grounds)
    if grounds:
        raw_score = sum(strength_scores.get(g.get("strength", "moderate"), 1) for g in grounds)
        max_possible = max(1, len(grounds) * 3)
        grounds_score = min(100, int((raw_score / max_possible) * 100))
    else:
        grounds_score = 0

    # Documentation completeness score
    docs_with_text = _documents_with_text(documents)
    if documents:
        extraction_ratio = docs_with_text / max(1, len(documents))
        documentation_score = min(100, int(extraction_ratio * 70) + min(30, len(documents) * 3))
    else:
        documentation_score = 0

    # Timeline completeness score
    if timeline:
        base_timeline_score = min(70, len(timeline) * 4)
        critical_events = len([t for t in timeline if t.get("significance") == "critical"])
        timeline_score = min(100, base_timeline_score + min(30, critical_events * 8))
    else:
        timeline_score = 0

    # Preparation completion score
    completed = _count_completed(checklist)
    preparation_score = _safe_percentage(completed, len(checklist))

    # Weighted readiness score
    readiness_score = int(
        (grounds_score * 0.35) +
        (documentation_score * 0.25) +
        (timeline_score * 0.20) +
        (preparation_score * 0.20)
    )

    if readiness_score >= 75:
        readiness_level = "Advanced"
        readiness_color = "green"
    elif readiness_score >= 50:
        readiness_level = "Established"
        readiness_color = "amber"
    elif readiness_score >= 25:
        readiness_level = "Developing"
        readiness_color = "orange"
    else:
        readiness_level = "Early Stage"
        readiness_color = "red"

    recommendations = []

    if not grounds:
        recommendations.append("Run AI Grounds Identification to flag possible appeal issues for review")
    if len(documents) < 3:
        recommendations.append("Upload more case documents to improve preparation completeness")
    if docs_with_text < len(documents):
        recommendations.append("Extract text or OCR all uploaded documents so they can be analysed properly")
    if len(timeline) < 5:
        recommendations.append("Build out the timeline with additional key events and procedural dates")
    if preparation_score < 50:
        recommendations.append("Work through the appeal checklist to improve preparation completeness")
    if len(grounds) > 0 and breakdown["strong"] == 0:
        recommendations.append("Review identified grounds and prioritise those with the clearest documentary support")

    return {
        "readiness_score": readiness_score,
        "readiness_level": readiness_level,
        "readiness_color": readiness_color,
        "grounds_score": grounds_score,
        "documentation_score": documentation_score,
        "timeline_score": timeline_score,
        "preparation_score": preparation_score,
        "ground_breakdown": breakdown,
        "documents_with_text": docs_with_text,
        "completed_checklist_items": completed,
        "recommendations": recommendations,
    }


# ============================================================================
# DEADLINES CRUD
# ============================================================================

@router.get("/cases/{case_id}/deadlines", response_model=List[dict])
async def get_deadlines(case_id: str, request: Request):
    """Get all deadlines for a case"""
    user = await get_current_user(request)

    case = await db.cases.find_one({"case_id": case_id, "user_id": user.user_id})
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")

    deadlines = await db.deadlines.find(
        {"case_id": case_id, "user_id": user.user_id},
        {"_id": 0}
    ).sort("due_date", 1).to_list(100)

    return deadlines


@router.post("/cases/{case_id}/deadlines", response_model=dict)
async def create_deadline(case_id: str, deadline_data: DeadlineCreate, request: Request):
    """Create a new deadline"""
    user = await get_current_user(request)

    case = await db.cases.find_one({"case_id": case_id, "user_id": user.user_id})
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")

    deadline = Deadline(case_id=case_id, user_id=user.user_id, **deadline_data.model_dump())
    deadline_dict = deadline.model_dump()
    deadline_dict["due_date"] = deadline_dict["due_date"].isoformat()
    deadline_dict["created_at"] = deadline_dict["created_at"].isoformat()

    await db.deadlines.insert_one(deadline_dict)

    return await db.deadlines.find_one(
        {"deadline_id": deadline.deadline_id, "case_id": case_id, "user_id": user.user_id},
        {"_id": 0}
    )


@router.patch("/cases/{case_id}/deadlines/{deadline_id}", response_model=dict)
async def update_deadline(case_id: str, deadline_id: str, request: Request):
    """Update a deadline (mark complete, etc.)"""
    user = await get_current_user(request)
    body = await request.json()

    deadline = await db.deadlines.find_one({
        "deadline_id": deadline_id,
        "case_id": case_id,
        "user_id": user.user_id
    })
    if not deadline:
        raise HTTPException(status_code=404, detail="Deadline not found")

    update_data = {}

    if "is_completed" in body:
        update_data["is_completed"] = body["is_completed"]
        if body["is_completed"]:
            update_data["completed_at"] = datetime.now(timezone.utc).isoformat()
        else:
            update_data["completed_at"] = None

    if "title" in body:
        update_data["title"] = body["title"]

    if "due_date" in body:
        update_data["due_date"] = body["due_date"]

    if "priority" in body:
        update_data["priority"] = body["priority"]

    if "description" in body:
        update_data["description"] = body["description"]

    if "deadline_type" in body:
        update_data["deadline_type"] = body["deadline_type"]

    if update_data:
        await db.deadlines.update_one(
            {"deadline_id": deadline_id, "case_id": case_id, "user_id": user.user_id},
            {"$set": update_data}
        )

    return await db.deadlines.find_one(
        {"deadline_id": deadline_id, "case_id": case_id, "user_id": user.user_id},
        {"_id": 0}
    )


@router.delete("/cases/{case_id}/deadlines/{deadline_id}")
async def delete_deadline(case_id: str, deadline_id: str, request: Request):
    """Delete a deadline"""
    user = await get_current_user(request)

    result = await db.deadlines.delete_one({
        "deadline_id": deadline_id,
        "case_id": case_id,
        "user_id": user.user_id
    })

    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Deadline not found")

    return {"message": "Deadline deleted"}


# ============================================================================
# CHECKLIST
# ============================================================================

@router.get("/cases/{case_id}/checklist", response_model=List[dict])
async def get_checklist(case_id: str, request: Request):
    """Get checklist for a case, creating default items if none exist"""
    user = await get_current_user(request)

    case = await db.cases.find_one({"case_id": case_id, "user_id": user.user_id})
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")

    items = await db.checklist_items.find(
        {"case_id": case_id, "user_id": user.user_id},
        {"_id": 0}
    ).sort("order", 1).to_list(100)

    if not items:
        for item_data in DEFAULT_CHECKLIST:
            item = ChecklistItem(case_id=case_id, user_id=user.user_id, **item_data)
            item_dict = item.model_dump()
            item_dict["created_at"] = item_dict["created_at"].isoformat()
            await db.checklist_items.insert_one(item_dict)

        items = await db.checklist_items.find(
            {"case_id": case_id, "user_id": user.user_id},
            {"_id": 0}
        ).sort("order", 1).to_list(100)

    return items


@router.patch("/cases/{case_id}/checklist/{item_id}", response_model=dict)
async def update_checklist_item(case_id: str, item_id: str, request: Request):
    """Update a checklist item"""
    user = await get_current_user(request)
    body = await request.json()

    item = await db.checklist_items.find_one({
        "item_id": item_id,
        "case_id": case_id,
        "user_id": user.user_id
    })
    if not item:
        raise HTTPException(status_code=404, detail="Checklist item not found")

    update_data = {}

    if "is_completed" in body:
        update_data["is_completed"] = body["is_completed"]
        if body["is_completed"]:
            update_data["completed_at"] = datetime.now(timezone.utc).isoformat()
        else:
            update_data["completed_at"] = None

    if update_data:
        await db.checklist_items.update_one(
            {"item_id": item_id, "case_id": case_id, "user_id": user.user_id},
            {"$set": update_data}
        )

    return await db.checklist_items.find_one(
        {"item_id": item_id, "case_id": case_id, "user_id": user.user_id},
        {"_id": 0}
    )


# ============================================================================
# READINESS / PREPARATION SCORE
# ============================================================================

@router.get("/cases/{case_id}/strength", response_model=dict)
async def get_case_strength(case_id: str, request: Request):
    """
    Compatibility endpoint.
    Preserves the existing route path while returning a safer readiness-based interpretation.
    """
    user = await get_current_user(request)

    case = await db.cases.find_one({"case_id": case_id, "user_id": user.user_id})
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")

    grounds = await db.grounds_of_merit.find(
        {"case_id": case_id, "user_id": user.user_id},
        {"_id": 0}
    ).to_list(100)

    documents = await db.documents.find(
        {"case_id": case_id, "user_id": user.user_id},
        {"_id": 0}
    ).to_list(500)

    timeline = await db.timeline_events.find(
        {"case_id": case_id, "user_id": user.user_id},
        {"_id": 0}
    ).to_list(500)

    checklist = await db.checklist_items.find(
        {"case_id": case_id, "user_id": user.user_id},
        {"_id": 0}
    ).to_list(100)

    scores = _calculate_readiness_scores(grounds, documents, timeline, checklist)

    overall_score = scores["readiness_score"]
    rating = scores["readiness_level"]
    rating_color = scores["readiness_color"]

    breakdown = {
        "grounds": {
            "score": scores["grounds_score"],
            "count": len(grounds),
            **scores["ground_breakdown"],
        },
        "documentation": {
            "score": scores["documentation_score"],
            "total_docs": len(documents),
            "with_text": scores["documents_with_text"],
        },
        "timeline": {
            "score": scores["timeline_score"],
            "event_count": len(timeline),
        },
        "preparation": {
            "score": scores["preparation_score"],
            "completed": scores["completed_checklist_items"],
            "total": len(checklist),
        },
    }

    return {
        # compatibility keys preserved
        "overall_score": overall_score,
        "rating": rating,
        "rating_color": rating_color,

        # additive clearer keys
        "readiness_score": scores["readiness_score"],
        "readiness_level": scores["readiness_level"],
        "readiness_color": scores["readiness_color"],

        "breakdown": breakdown,
        "recommendations": scores["recommendations"],

        "assessment_note": (
            "This score reflects case preparation and documentation completeness. "
            "It is not a determination of legal merit or likelihood of success."
        ),
        "assessment_type": "appeal_preparation_readiness"
    }
