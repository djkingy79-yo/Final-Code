# DO NOT UNDO — auth router. All endpoints in this file are approved and must be preserved.
"""
Criminal Appeal AI - Complete Auth Router
Handles all authentication: Email/Password + Google OAuth via Emergent
"""
from fastapi import APIRouter, HTTPException, Response, Request
from pydantic import BaseModel
from datetime import datetime, timezone, timedelta
import httpx
import uuid
import hashlib
import secrets

from config import db, logger
from auth_utils import get_current_user
import os

ADMIN_EMAILS = os.environ.get("ADMIN_EMAILS", "djkingy79@gmail.com").split(",")

router = APIRouter(prefix="/api/auth", tags=["auth"])

# ============ PASSWORD UTILITIES ============

def hash_password(password: str, salt: str = None) -> tuple:
    """Hash password with salt"""
    if salt is None:
        salt = secrets.token_hex(16)
    hashed = hashlib.pbkdf2_hmac('sha256', password.encode(), salt.encode(), 100000)
    return hashed.hex(), salt

def verify_password(password: str, hashed: str, salt: str) -> bool:
    """Verify password against hash"""
    new_hash, _ = hash_password(password, salt)
    return new_hash == hashed

# ============ REQUEST MODELS ============

class RegisterRequest(BaseModel):
    email: str
    password: str
    name: str

class LoginRequest(BaseModel):
    email: str
    password: str

# ============ AUTH ENDPOINTS ============

@router.post("/register")
async def register_user(request: RegisterRequest, response: Response):
    """Register a new user with email/password"""
    # Validate email format
    if not request.email or '@' not in request.email:
        raise HTTPException(status_code=400, detail="Invalid email format")
    
    # Check password strength
    if len(request.password) < 6:
        raise HTTPException(status_code=400, detail="Password must be at least 6 characters")
    
    # Check if user exists
    existing_user = await db.users.find_one({"email": request.email.lower()}, {"_id": 0})
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered. Please login instead.")
    
    # Hash password
    hashed_password, salt = hash_password(request.password)
    
    # Create user
    user_id = f"user_{uuid.uuid4().hex[:12]}"
    user_doc = {
        "user_id": user_id,
        "email": request.email.lower(),
        "name": request.name,
        "password_hash": hashed_password,
        "password_salt": salt,
        "auth_type": "email",
        "picture": None,
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    
    await db.users.insert_one(user_doc)
    
    # Create session
    session_token = f"sess_{uuid.uuid4().hex}"
    expires_at = datetime.now(timezone.utc) + timedelta(days=7)
    
    await db.user_sessions.insert_one({
        "user_id": user_id,
        "session_token": session_token,
        "expires_at": expires_at.isoformat(),
        "created_at": datetime.now(timezone.utc).isoformat()
    })
    
    # Set cookie
    response.set_cookie(
        key="session_token",
        value=session_token,
        httponly=True,
        secure=True,
        samesite="none",
        path="/",
        max_age=7 * 24 * 60 * 60
    )
    
    return {
        "user_id": user_id,
        "email": request.email.lower(),
        "name": request.name,
        "picture": None
    }

@router.post("/login")
async def login_user(request: LoginRequest, response: Response):
    """Login with email/password"""
    # Find user
    user_doc = await db.users.find_one({"email": request.email.lower()}, {"_id": 0})
    
    if not user_doc:
        raise HTTPException(status_code=401, detail="Invalid email or password")
    
    # Check if user has password (email auth)
    if not user_doc.get("password_hash"):
        raise HTTPException(status_code=401, detail="This account uses Google login. Please sign in with Google.")
    
    # Verify password
    if not verify_password(request.password, user_doc["password_hash"], user_doc["password_salt"]):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    
    # Create session
    session_token = f"sess_{uuid.uuid4().hex}"
    expires_at = datetime.now(timezone.utc) + timedelta(days=7)
    
    await db.user_sessions.insert_one({
        "user_id": user_doc["user_id"],
        "session_token": session_token,
        "expires_at": expires_at.isoformat(),
        "created_at": datetime.now(timezone.utc).isoformat()
    })
    
    # Set cookie
    response.set_cookie(
        key="session_token",
        value=session_token,
        httponly=True,
        secure=True,
        samesite="none",
        path="/",
        max_age=7 * 24 * 60 * 60
    )
    
    return {
        "user_id": user_doc["user_id"],
        "email": user_doc["email"],
        "name": user_doc["name"],
        "picture": user_doc.get("picture")
    }

@router.post("/session")
async def create_session(request: Request, response: Response):
    """Exchange session_id for session_token (Google OAuth via Emergent)"""
    body = await request.json()
    session_id = body.get("session_id")
    
    if not session_id:
        raise HTTPException(status_code=400, detail="session_id required")
    
    # Call Emergent Auth to get user data
    async with httpx.AsyncClient() as client:
        auth_response = await client.get(
            "https://demobackend.emergentagent.com/auth/v1/env/oauth/session-data",
            headers={"X-Session-ID": session_id}
        )
    
    if auth_response.status_code != 200:
        raise HTTPException(status_code=401, detail="Invalid session_id")
    
    user_data = auth_response.json()
    
    # Create or update user
    user_id = f"user_{uuid.uuid4().hex[:12]}"
    existing_user = await db.users.find_one({"email": user_data["email"]}, {"_id": 0})
    
    if existing_user:
        user_id = existing_user["user_id"]
        await db.users.update_one(
            {"user_id": user_id},
            {"$set": {
                "name": user_data["name"],
                "picture": user_data.get("picture"),
                "updated_at": datetime.now(timezone.utc).isoformat()
            }}
        )
    else:
        await db.users.insert_one({
            "user_id": user_id,
            "email": user_data["email"],
            "name": user_data["name"],
            "picture": user_data.get("picture"),
            "auth_type": "google",
            "created_at": datetime.now(timezone.utc).isoformat()
        })
    
    # Create session
    session_token = user_data.get("session_token", f"sess_{uuid.uuid4().hex}")
    expires_at = datetime.now(timezone.utc) + timedelta(days=7)
    
    await db.user_sessions.insert_one({
        "user_id": user_id,
        "session_token": session_token,
        "expires_at": expires_at.isoformat(),
        "created_at": datetime.now(timezone.utc).isoformat()
    })
    
    # Set cookie
    response.set_cookie(
        key="session_token",
        value=session_token,
        httponly=True,
        secure=True,
        samesite="none",
        path="/",
        max_age=7 * 24 * 60 * 60
    )
    
    user_doc = await db.users.find_one({"user_id": user_id}, {"_id": 0})
    return user_doc

@router.get("/me")
async def get_me(request: Request):
    """Get current user info"""
    user = await get_current_user(request)
    user_dict = user.model_dump()
    # Check if user has accepted terms
    user_doc = await db.users.find_one({"user_id": user.user_id}, {"_id": 0})
    user_dict["terms_accepted"] = user_doc.get("terms_accepted", False)
    user_dict["terms_accepted_at"] = user_doc.get("terms_accepted_at")
    user_dict["is_admin"] = user.email in ADMIN_EMAILS
    return user_dict

@router.post("/accept-terms")
async def accept_terms(request: Request):
    """Accept terms and conditions"""
    user = await get_current_user(request)
    await db.users.update_one(
        {"user_id": user.user_id},
        {"$set": {
            "terms_accepted": True,
            "terms_accepted_at": datetime.now(timezone.utc).isoformat()
        }}
    )
    return {"message": "Terms accepted", "terms_accepted": True}

@router.post("/logout")
async def logout(request: Request, response: Response):
    """Logout user"""
    session_token = request.cookies.get("session_token")
    if session_token:
        await db.user_sessions.delete_one({"session_token": session_token})
    
    response.delete_cookie(key="session_token", path="/", samesite="none", secure=True)
    return {"message": "Logged out"}
