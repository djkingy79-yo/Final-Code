# DO NOT UNDO — cases router. All endpoints in this file are approved and must be preserved.
"""
Criminal Appeal AI - Cases Router
"""
from fastapi import APIRouter, HTTPException, Request
from typing import List
from datetime import datetime, timezone

from config import db
from models import Case, CaseCreate, ChecklistItem, DEFAULT_CHECKLIST
from auth_utils import get_current_user

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
