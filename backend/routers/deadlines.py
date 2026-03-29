"""
Criminal Appeal AI - Deadlines, Checklist & Case Strength Router
Extracted from server.py monolith.
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


@router.get("/cases/{case_id}/deadlines", response_model=List[dict])
async def get_deadlines(case_id: str, request: Request):
    """Get all deadlines for a case"""
    user = await get_current_user(request)
    case = await db.cases.find_one({"case_id": case_id, "user_id": user.user_id})
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
    deadlines = await db.deadlines.find({"case_id": case_id}, {"_id": 0}).sort("due_date", 1).to_list(100)
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
    return await db.deadlines.find_one({"deadline_id": deadline.deadline_id}, {"_id": 0})


@router.patch("/cases/{case_id}/deadlines/{deadline_id}", response_model=dict)
async def update_deadline(case_id: str, deadline_id: str, request: Request):
    """Update a deadline (mark complete, etc.)"""
    await get_current_user(request)
    body = await request.json()
    deadline = await db.deadlines.find_one({"deadline_id": deadline_id, "case_id": case_id})
    if not deadline:
        raise HTTPException(status_code=404, detail="Deadline not found")
    update_data = {}
    if "is_completed" in body:
        update_data["is_completed"] = body["is_completed"]
        if body["is_completed"]:
            update_data["completed_at"] = datetime.now(timezone.utc).isoformat()
    if "title" in body:
        update_data["title"] = body["title"]
    if "due_date" in body:
        update_data["due_date"] = body["due_date"]
    if "priority" in body:
        update_data["priority"] = body["priority"]
    if update_data:
        await db.deadlines.update_one({"deadline_id": deadline_id}, {"$set": update_data})
    return await db.deadlines.find_one({"deadline_id": deadline_id}, {"_id": 0})


@router.delete("/cases/{case_id}/deadlines/{deadline_id}")
async def delete_deadline(case_id: str, deadline_id: str, request: Request):
    """Delete a deadline"""
    await get_current_user(request)
    result = await db.deadlines.delete_one({"deadline_id": deadline_id, "case_id": case_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Deadline not found")
    return {"message": "Deadline deleted"}


@router.get("/cases/{case_id}/checklist", response_model=List[dict])
async def get_checklist(case_id: str, request: Request):
    """Get checklist for a case, creating default items if none exist"""
    user = await get_current_user(request)
    case = await db.cases.find_one({"case_id": case_id, "user_id": user.user_id})
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
    items = await db.checklist_items.find({"case_id": case_id}, {"_id": 0}).sort("order", 1).to_list(100)
    if not items:
        for item_data in DEFAULT_CHECKLIST:
            item = ChecklistItem(case_id=case_id, user_id=user.user_id, **item_data)
            item_dict = item.model_dump()
            item_dict["created_at"] = item_dict["created_at"].isoformat()
            await db.checklist_items.insert_one(item_dict)
        items = await db.checklist_items.find({"case_id": case_id}, {"_id": 0}).sort("order", 1).to_list(100)
    return items


@router.patch("/cases/{case_id}/checklist/{item_id}", response_model=dict)
async def update_checklist_item(case_id: str, item_id: str, request: Request):
    """Update a checklist item"""
    await get_current_user(request)
    body = await request.json()
    item = await db.checklist_items.find_one({"item_id": item_id, "case_id": case_id})
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
        await db.checklist_items.update_one({"item_id": item_id}, {"$set": update_data})
    return await db.checklist_items.find_one({"item_id": item_id}, {"_id": 0})


@router.get("/cases/{case_id}/strength", response_model=dict)
async def get_case_strength(case_id: str, request: Request):
    """Calculate overall case strength"""
    user = await get_current_user(request)
    case = await db.cases.find_one({"case_id": case_id, "user_id": user.user_id})
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
    grounds = await db.grounds_of_merit.find({"case_id": case_id}, {"_id": 0}).to_list(100)
    documents = await db.documents.find({"case_id": case_id}, {"_id": 0}).to_list(500)
    timeline = await db.timeline_events.find({"case_id": case_id}, {"_id": 0}).to_list(500)
    checklist = await db.checklist_items.find({"case_id": case_id}, {"_id": 0}).to_list(100)
    strength_scores = {"strong": 3, "moderate": 2, "weak": 1}
    grounds_score = 0
    ground_breakdown = {"strong": 0, "moderate": 0, "weak": 0}
    if grounds:
        for g in grounds:
            strength = g.get("strength", "moderate")
            ground_breakdown[strength] = ground_breakdown.get(strength, 0) + 1
            grounds_score += strength_scores.get(strength, 1)
        max_possible = len(grounds) * 3
        grounds_score = min(100, int((grounds_score / max_possible) * 100) + (len(grounds) * 5))
    doc_score = 0
    docs_with_text = len([d for d in documents if d.get("content_text")])
    if documents:
        doc_score = min(100, int((docs_with_text / len(documents)) * 50) + (len(documents) * 5))
    timeline_score = 0
    if timeline:
        timeline_score = min(100, len(timeline) * 5)
        critical_events = len([t for t in timeline if t.get("significance") == "critical"])
        timeline_score = min(100, timeline_score + (critical_events * 10))
    prep_score = 0
    if checklist:
        completed = len([c for c in checklist if c.get("is_completed")])
        prep_score = int((completed / len(checklist)) * 100)
    overall_score = int((grounds_score * 0.40) + (doc_score * 0.25) + (timeline_score * 0.15) + (prep_score * 0.20))
    if overall_score >= 75:
        rating, rating_color = "Strong", "green"
    elif overall_score >= 50:
        rating, rating_color = "Moderate", "amber"
    elif overall_score >= 25:
        rating, rating_color = "Developing", "orange"
    else:
        rating, rating_color = "Early Stage", "red"
    recommendations = []
    if not grounds:
        recommendations.append("Run AI Grounds Identification to find potential appeal grounds")
    if len(documents) < 3:
        recommendations.append("Upload more case documents for better analysis")
    if len(timeline) < 5:
        recommendations.append("Build out your timeline with key case events")
    if prep_score < 50:
        recommendations.append("Work through the appeal checklist")
    return {
        "overall_score": overall_score, "rating": rating, "rating_color": rating_color,
        "breakdown": {
            "grounds": {"score": grounds_score, "count": len(grounds), **ground_breakdown},
            "documentation": {"score": doc_score, "total_docs": len(documents), "with_text": docs_with_text},
            "timeline": {"score": timeline_score, "event_count": len(timeline)},
            "preparation": {"score": prep_score, "completed": len([c for c in checklist if c.get("is_completed")]), "total": len(checklist)}
        },
        "recommendations": recommendations
    }
