# DO NOT UNDO — notes router. All endpoints in this file are approved and must be preserved.
"""
Criminal Appeal AI - Notes Router
Handles case notes and comments
"""
from fastapi import APIRouter, HTTPException, Request
from typing import List
from datetime import datetime, timezone

from config import db
from models import Note, NoteCreate, NoteUpdate
from auth_utils import get_current_user, verify_case_ownership

router = APIRouter(prefix="/api/cases/{case_id}/notes", tags=["notes"])


@router.get("", response_model=List[dict])
async def get_notes(case_id: str, request: Request):
    """Get all notes for a case"""
    user = await get_current_user(request)
    await verify_case_ownership(case_id, user.user_id)
    
    notes = await db.notes.find(
        {"case_id": case_id},
        {"_id": 0}
    ).sort([("is_pinned", -1), ("created_at", -1)]).to_list(500)
    
    return notes


@router.post("", response_model=dict)
async def create_note(case_id: str, note_data: NoteCreate, request: Request):
    """Create a new note"""
    user = await get_current_user(request)
    await verify_case_ownership(case_id, user.user_id)
    
    note = Note(
        case_id=case_id,
        user_id=user.user_id,
        author_name=user.name,
        author_email=user.email,
        **note_data.model_dump()
    )
    
    note_dict = note.model_dump()
    note_dict["created_at"] = note_dict["created_at"].isoformat()
    note_dict["updated_at"] = note_dict["updated_at"].isoformat()
    
    await db.notes.insert_one(note_dict)
    
    await db.cases.update_one(
        {"case_id": case_id},
        {"$set": {"updated_at": datetime.now(timezone.utc).isoformat()}}
    )
    
    return await db.notes.find_one({"note_id": note.note_id}, {"_id": 0})


@router.get("/{note_id}", response_model=dict)
async def get_note(case_id: str, note_id: str, request: Request):
    """Get a specific note"""
    user = await get_current_user(request)
    
    note = await db.notes.find_one(
        {"note_id": note_id, "case_id": case_id, "user_id": user.user_id},
        {"_id": 0}
    )
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")
    
    return note


@router.put("/{note_id}", response_model=dict)
async def update_note(case_id: str, note_id: str, note_data: NoteUpdate, request: Request):
    """Update a note"""
    user = await get_current_user(request)
    
    update_data = {k: v for k, v in note_data.model_dump().items() if v is not None}
    update_data["updated_at"] = datetime.now(timezone.utc).isoformat()
    
    result = await db.notes.update_one(
        {"note_id": note_id, "case_id": case_id, "user_id": user.user_id},
        {"$set": update_data}
    )
    
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="Note not found")
    
    return await db.notes.find_one({"note_id": note_id}, {"_id": 0})


@router.delete("/{note_id}")
async def delete_note(case_id: str, note_id: str, request: Request):
    """Delete a note"""
    user = await get_current_user(request)
    
    result = await db.notes.delete_one({
        "note_id": note_id,
        "case_id": case_id,
        "user_id": user.user_id
    })
    
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Note not found")
    
    return {"message": "Note deleted"}


@router.patch("/{note_id}/pin")
async def toggle_pin_note(case_id: str, note_id: str, request: Request):
    """Toggle pin status of a note"""
    user = await get_current_user(request)
    
    note = await db.notes.find_one(
        {"note_id": note_id, "case_id": case_id, "user_id": user.user_id},
        {"_id": 0}
    )
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")
    
    await db.notes.update_one(
        {"note_id": note_id},
        {"$set": {
            "is_pinned": not note.get("is_pinned", False),
            "updated_at": datetime.now(timezone.utc).isoformat()
        }}
    )
    
    return await db.notes.find_one({"note_id": note_id}, {"_id": 0})
