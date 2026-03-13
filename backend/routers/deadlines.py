# DO NOT UNDO — deadlines router. All endpoints in this file are approved and must be preserved.
"""
Criminal Appeal AI - Deadlines & Checklist Router
Handles appeal deadlines and progress checklist
"""
from fastapi import APIRouter, HTTPException, Request
from typing import List
from datetime import datetime, timezone

from config import db
from models import Deadline, DeadlineCreate, ChecklistItem, DEFAULT_CHECKLIST
from auth_utils import get_current_user, verify_case_ownership

router = APIRouter(tags=["deadlines-checklist"])


# ============ DEADLINE ENDPOINTS ============

@router.get("/api/cases/{case_id}/deadlines", response_model=List[dict])
async def get_deadlines(case_id: str, request: Request):
    """Get all deadlines for a case"""
    user = await get_current_user(request)
    await verify_case_ownership(case_id, user.user_id)
    
    deadlines = await db.deadlines.find(
        {"case_id": case_id},
        {"_id": 0}
    ).sort("due_date", 1).to_list(100)
    
    return deadlines


@router.post("/api/cases/{case_id}/deadlines", response_model=dict)
async def create_deadline(case_id: str, deadline_data: DeadlineCreate, request: Request):
    """Create a new deadline"""
    user = await get_current_user(request)
    await verify_case_ownership(case_id, user.user_id)
    
    deadline = Deadline(
        case_id=case_id,
        user_id=user.user_id,
        **deadline_data.model_dump()
    )
    
    deadline_dict = deadline.model_dump()
    deadline_dict["due_date"] = deadline_dict["due_date"].isoformat()
    deadline_dict["created_at"] = deadline_dict["created_at"].isoformat()
    
    await db.deadlines.insert_one(deadline_dict)
    
    return await db.deadlines.find_one({"deadline_id": deadline.deadline_id}, {"_id": 0})


@router.patch("/api/cases/{case_id}/deadlines/{deadline_id}", response_model=dict)
async def update_deadline(case_id: str, deadline_id: str, request: Request):
    """Update a deadline"""
    await get_current_user(request)  # Verify authentication
    body = await request.json()
    
    deadline = await db.deadlines.find_one({
        "deadline_id": deadline_id,
        "case_id": case_id
    })
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
        await db.deadlines.update_one(
            {"deadline_id": deadline_id},
            {"$set": update_data}
        )
    
    return await db.deadlines.find_one({"deadline_id": deadline_id}, {"_id": 0})


@router.delete("/api/cases/{case_id}/deadlines/{deadline_id}")
async def delete_deadline(case_id: str, deadline_id: str, request: Request):
    """Delete a deadline"""
    await get_current_user(request)  # Verify authentication
    
    result = await db.deadlines.delete_one({
        "deadline_id": deadline_id,
        "case_id": case_id
    })
    
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Deadline not found")
    
    return {"message": "Deadline deleted"}


# ============ CHECKLIST ENDPOINTS ============

@router.get("/api/cases/{case_id}/checklist", response_model=List[dict])
async def get_checklist(case_id: str, request: Request):
    """Get checklist items for a case"""
    user = await get_current_user(request)
    await verify_case_ownership(case_id, user.user_id)
    
    items = await db.checklist_items.find(
        {"case_id": case_id},
        {"_id": 0}
    ).sort("order", 1).to_list(100)
    
    # If no items exist, create default checklist
    if not items:
        for item in DEFAULT_CHECKLIST:
            checklist_item = ChecklistItem(
                case_id=case_id,
                user_id=user.user_id,
                **item
            )
            item_dict = checklist_item.model_dump()
            item_dict["created_at"] = item_dict["created_at"].isoformat()
            await db.checklist_items.insert_one(item_dict)
        
        items = await db.checklist_items.find(
            {"case_id": case_id},
            {"_id": 0}
        ).sort("order", 1).to_list(100)
    
    return items


@router.patch("/api/cases/{case_id}/checklist/{item_id}", response_model=dict)
async def update_checklist_item(case_id: str, item_id: str, request: Request):
    """Update a checklist item"""
    await get_current_user(request)  # Verify authentication
    body = await request.json()
    
    item = await db.checklist_items.find_one({
        "item_id": item_id,
        "case_id": case_id
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
            {"item_id": item_id},
            {"$set": update_data}
        )
    
    return await db.checklist_items.find_one({"item_id": item_id}, {"_id": 0})
