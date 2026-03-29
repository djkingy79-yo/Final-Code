"""
Criminal Appeal AI - Notes & Comments Router
Extracted from server.py monolith.
"""
from fastapi import APIRouter, HTTPException, Request, WebSocket, WebSocketDisconnect
from typing import List
from datetime import datetime, timezone
import uuid
import json
import logging

from config import db
from auth_utils import get_current_user, get_user_from_session_token
from models import Note, NoteCreate, NoteUpdate, NoteCommentCreate
from services.document_helpers import extract_mentions
from services.notes_helpers import notes_ws_connections, broadcast_notes_event, get_presence_snapshot

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api", tags=["notes"])


@router.get("/cases/{case_id}/notes", response_model=List[dict])
async def get_notes(case_id: str, request: Request):
    """Get all notes for a case"""
    user = await get_current_user(request)
    case = await db.cases.find_one({"case_id": case_id, "user_id": user.user_id})
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
    notes = await db.notes.find(
        {"case_id": case_id}, {"_id": 0}
    ).sort([("is_pinned", -1), ("created_at", -1)]).to_list(500)
    for note in notes:
        note["pinned"] = note.get("is_pinned", False)
        note["mentions"] = note.get("mentions", [])
        note["comments"] = note.get("comments", [])
    return notes


@router.post("/cases/{case_id}/notes", response_model=dict)
async def create_note(case_id: str, note_data: NoteCreate, request: Request):
    """Create a new note"""
    user = await get_current_user(request)
    case = await db.cases.find_one({"case_id": case_id, "user_id": user.user_id})
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
    merged_mentions = sorted(list(set(note_data.mentions + extract_mentions(note_data.content))))
    note = Note(
        case_id=case_id, user_id=user.user_id,
        author_name=user.name, author_email=user.email,
        mentions=merged_mentions, comments=[],
        **note_data.model_dump(exclude={"mentions"})
    )
    note_dict = note.model_dump()
    note_dict["created_at"] = note_dict["created_at"].isoformat()
    note_dict["updated_at"] = note_dict["updated_at"].isoformat()
    await db.notes.insert_one(note_dict)
    await db.cases.update_one(
        {"case_id": case_id},
        {"$set": {"updated_at": datetime.now(timezone.utc).isoformat()}}
    )
    created_note = await db.notes.find_one({"note_id": note.note_id}, {"_id": 0})
    if created_note:
        created_note["pinned"] = created_note.get("is_pinned", False)
        created_note["mentions"] = created_note.get("mentions", [])
        created_note["comments"] = created_note.get("comments", [])
    await broadcast_notes_event(case_id, "note_created", {
        "note": created_note,
        "actor": {"user_id": user.user_id, "name": user.name}
    })
    return created_note


@router.get("/cases/{case_id}/notes/{note_id}", response_model=dict)
async def get_note(case_id: str, note_id: str, request: Request):
    """Get a specific note"""
    user = await get_current_user(request)
    note = await db.notes.find_one(
        {"note_id": note_id, "case_id": case_id, "user_id": user.user_id}, {"_id": 0}
    )
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")
    note["pinned"] = note.get("is_pinned", False)
    note["mentions"] = note.get("mentions", [])
    note["comments"] = note.get("comments", [])
    return note


@router.put("/cases/{case_id}/notes/{note_id}", response_model=dict)
async def update_note(case_id: str, note_id: str, note_data: NoteUpdate, request: Request):
    """Update a note"""
    user = await get_current_user(request)
    existing_note = await db.notes.find_one(
        {"note_id": note_id, "case_id": case_id, "user_id": user.user_id}, {"_id": 0}
    )
    if not existing_note:
        raise HTTPException(status_code=404, detail="Note not found")
    update_fields = {k: v for k, v in note_data.model_dump().items() if v is not None}
    updated_content = update_fields.get("content", existing_note.get("content", ""))
    update_fields["mentions"] = extract_mentions(updated_content)
    update_fields["updated_at"] = datetime.now(timezone.utc).isoformat()
    await db.notes.update_one(
        {"note_id": note_id, "case_id": case_id, "user_id": user.user_id},
        {"$set": update_fields}
    )
    updated_note = await db.notes.find_one({"note_id": note_id}, {"_id": 0})
    if updated_note:
        updated_note["pinned"] = updated_note.get("is_pinned", False)
        updated_note["mentions"] = updated_note.get("mentions", [])
        updated_note["comments"] = updated_note.get("comments", [])
    await broadcast_notes_event(case_id, "note_updated", {
        "note": updated_note,
        "actor": {"user_id": user.user_id, "name": user.name}
    })
    return updated_note


@router.delete("/cases/{case_id}/notes/{note_id}")
async def delete_note(case_id: str, note_id: str, request: Request):
    """Delete a note"""
    user = await get_current_user(request)
    result = await db.notes.delete_one({
        "note_id": note_id, "case_id": case_id, "user_id": user.user_id
    })
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Note not found")
    await broadcast_notes_event(case_id, "note_deleted", {
        "note_id": note_id,
        "actor": {"user_id": user.user_id, "name": user.name}
    })
    return {"message": "Note deleted"}


@router.patch("/cases/{case_id}/notes/{note_id}/pin")
async def toggle_pin_note(case_id: str, note_id: str, request: Request):
    """Toggle pin status of a note"""
    user = await get_current_user(request)
    note = await db.notes.find_one(
        {"note_id": note_id, "case_id": case_id, "user_id": user.user_id}, {"_id": 0}
    )
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")
    new_pin_status = not note.get("is_pinned", False)
    await db.notes.update_one(
        {"note_id": note_id},
        {"$set": {"is_pinned": new_pin_status, "updated_at": datetime.now(timezone.utc).isoformat()}}
    )
    updated_note = await db.notes.find_one({"note_id": note_id}, {"_id": 0})
    if updated_note:
        updated_note["pinned"] = updated_note.get("is_pinned", False)
        updated_note["mentions"] = updated_note.get("mentions", [])
        updated_note["comments"] = updated_note.get("comments", [])
    await broadcast_notes_event(case_id, "note_updated", {
        "note": updated_note,
        "actor": {"user_id": user.user_id, "name": user.name}
    })
    return updated_note


@router.post("/cases/{case_id}/notes/{note_id}/comments", response_model=dict)
async def add_note_comment(case_id: str, note_id: str, comment_data: NoteCommentCreate, request: Request):
    """Add a threaded comment to a note."""
    user = await get_current_user(request)
    note = await db.notes.find_one(
        {"note_id": note_id, "case_id": case_id, "user_id": user.user_id}, {"_id": 0}
    )
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")
    content = comment_data.content.strip()
    if not content:
        raise HTTPException(status_code=400, detail="Comment content is required")
    comment = {
        "comment_id": f"cmt_{uuid.uuid4().hex[:12]}",
        "content": content,
        "mentions": extract_mentions(content),
        "author_name": user.name,
        "author_email": user.email,
        "author_user_id": user.user_id,
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    await db.notes.update_one(
        {"note_id": note_id},
        {"$push": {"comments": comment}, "$set": {"updated_at": datetime.now(timezone.utc).isoformat()}}
    )
    updated_note = await db.notes.find_one({"note_id": note_id}, {"_id": 0})
    if updated_note:
        updated_note["pinned"] = updated_note.get("is_pinned", False)
        updated_note["mentions"] = updated_note.get("mentions", [])
        updated_note["comments"] = updated_note.get("comments", [])
    await broadcast_notes_event(case_id, "note_comment_added", {
        "note_id": note_id, "comment": comment, "note": updated_note,
        "actor": {"user_id": user.user_id, "name": user.name}
    })
    return {"comment": comment, "note": updated_note}


@router.delete("/cases/{case_id}/notes/{note_id}/comments/{comment_id}")
async def delete_note_comment(case_id: str, note_id: str, comment_id: str, request: Request):
    """Delete a comment from a note."""
    user = await get_current_user(request)
    note = await db.notes.find_one(
        {"note_id": note_id, "case_id": case_id, "user_id": user.user_id}, {"_id": 0}
    )
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")
    comments = note.get("comments", [])
    target_comment = next((c for c in comments if c.get("comment_id") == comment_id), None)
    if not target_comment:
        raise HTTPException(status_code=404, detail="Comment not found")
    if target_comment.get("author_user_id") != user.user_id:
        raise HTTPException(status_code=403, detail="Only the comment author can delete this comment")
    await db.notes.update_one(
        {"note_id": note_id},
        {"$pull": {"comments": {"comment_id": comment_id}}, "$set": {"updated_at": datetime.now(timezone.utc).isoformat()}}
    )
    await broadcast_notes_event(case_id, "note_comment_deleted", {
        "note_id": note_id, "comment_id": comment_id,
        "actor": {"user_id": user.user_id, "name": user.name}
    })
    return {"message": "Comment deleted"}


# ============ NOTES WEBSOCKET ============

@router.websocket("/cases/{case_id}/notes/ws")
async def notes_collaboration_ws(websocket: WebSocket, case_id: str):
    """Realtime note collaboration channel for a case."""
    session_token = websocket.query_params.get("session_token") or websocket.cookies.get("session_token")
    try:
        user = await get_user_from_session_token(session_token)
        case = await db.cases.find_one({"case_id": case_id, "user_id": user.user_id}, {"_id": 0})
        if not case:
            await websocket.close(code=4404)
            return
        await websocket.accept()
        case_connections = notes_ws_connections.setdefault(case_id, {})
        case_connections[user.user_id] = websocket
        presence = await get_presence_snapshot(case_id)
        await broadcast_notes_event(case_id, "presence_update", {"users": presence})
        while True:
            raw_message = await websocket.receive_text()
            if not raw_message:
                continue
            if raw_message == "ping":
                await websocket.send_json({"type": "pong", "payload": {"timestamp": datetime.now(timezone.utc).isoformat()}})
                continue
            try:
                payload = json.loads(raw_message)
            except json.JSONDecodeError:
                continue
            if payload.get("type") == "typing":
                await broadcast_notes_event(case_id, "typing", {
                    "user_id": user.user_id, "name": user.name,
                    "note_id": payload.get("note_id"),
                    "is_typing": bool(payload.get("is_typing", False))
                })
    except WebSocketDisconnect:
        pass
    except HTTPException:
        if websocket.client_state.value != 3:
            await websocket.close(code=4401)
    finally:
        case_connections = notes_ws_connections.get(case_id, {})
        for uid, ws in list(case_connections.items()):
            if ws is websocket:
                case_connections.pop(uid, None)
                break
        if case_connections:
            presence = await get_presence_snapshot(case_id)
            await broadcast_notes_event(case_id, "presence_update", {"users": presence})
        if case_id in notes_ws_connections and not notes_ws_connections.get(case_id):
            notes_ws_connections.pop(case_id, None)
