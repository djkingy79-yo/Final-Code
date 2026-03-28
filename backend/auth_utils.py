# DO NOT UNDO — auth_utils module. All logic in this file is approved and must be preserved.
"""
Criminal Appeal AI - Authentication Utilities
Shared authentication helpers used across all routers
"""
from fastapi import HTTPException, Request
from datetime import datetime, timezone

from config import db
from models import User


async def get_current_user(request: Request) -> User:
    """Get current user from session token (cookie or header)"""
    session_token = request.cookies.get("session_token")
    if not session_token:
        session_token = request.query_params.get("session_token")
    if not session_token:
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            session_token = auth_header.split(" ")[1]
    
    if not session_token:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    session_doc = await db.user_sessions.find_one({"session_token": session_token}, {"_id": 0})
    if not session_doc:
        raise HTTPException(status_code=401, detail="Invalid session")
    
    expires_at = session_doc.get("expires_at")
    if isinstance(expires_at, str):
        expires_at = datetime.fromisoformat(expires_at)
    if expires_at.tzinfo is None:
        expires_at = expires_at.replace(tzinfo=timezone.utc)
    if expires_at < datetime.now(timezone.utc):
        raise HTTPException(status_code=401, detail="Session expired")
    
    user_doc = await db.users.find_one({"user_id": session_doc["user_id"]}, {"_id": 0})
    if not user_doc:
        raise HTTPException(status_code=401, detail="User not found")
    
    return User(**user_doc)


async def verify_case_ownership(case_id: str, user_id: str):
    """Verify user owns the case, raises 404 if not found"""
    case = await db.cases.find_one({"case_id": case_id, "user_id": user_id})
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
    return case


async def verify_case_access(case_id: str, user_id: str):
    """Verify user owns OR has shared access to the case."""
    case = await db.cases.find_one({"case_id": case_id}, {"_id": 0})
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
    if case.get("user_id") == user_id:
        return case
    share = await db.case_shares.find_one({
        "case_id": case_id, "shared_with_user_id": user_id, "status": "accepted"
    }, {"_id": 0})
    if share:
        return case
    raise HTTPException(status_code=403, detail="Access denied")
