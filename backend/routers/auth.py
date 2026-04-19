# DO NOT UNDO — auth router. All endpoints in this file are approved and must be preserved.
"""
Criminal Appeal AI - Complete Auth Router
Handles all authentication: Email/Password + Google OAuth via Emergent
"""
from fastapi import APIRouter, HTTPException, Response, Request
from pydantic import BaseModel
from datetime import datetime, timezone, timedelta
import hmac
import httpx
import uuid
import hashlib
import secrets

from config import db, get_admin_emails, limiter
from auth_utils import get_current_user
import logging

logger = logging.getLogger(__name__)

ADMIN_EMAILS = get_admin_emails()  # Cached at startup; use get_admin_emails() for live checks

router = APIRouter(prefix="/api/auth", tags=["auth"])

# ============ PASSWORD UTILITIES ============

def hash_password(password: str, salt: str = None) -> tuple:
    """Hash password with salt"""
    if salt is None:
        salt = secrets.token_hex(16)
    hashed = hashlib.pbkdf2_hmac('sha256', password.encode(), salt.encode(), 100000)
    return hashed.hex(), salt

def verify_password(password: str, hashed: str, salt: str) -> bool:
    """Verify password against hash — timing-safe comparison."""
    new_hash, _ = hash_password(password, salt)
    return hmac.compare_digest(new_hash, hashed)

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
@limiter.limit("3/minute")
async def register_user(request: Request, response: Response):
    """Register a new user with email/password"""
    body = await request.json()
    reg_data = RegisterRequest(**body)
    # Validate email format
    if not reg_data.email or '@' not in reg_data.email:
        raise HTTPException(status_code=400, detail="Invalid email format")
    
    # Check password strength
    if len(reg_data.password) < 8:
        raise HTTPException(status_code=400, detail="Password must be at least 8 characters")
    if reg_data.password.isdigit() or reg_data.password.isalpha():
        raise HTTPException(status_code=400, detail="Password must contain both letters and numbers")
    
    # Check if user exists
    existing_user = await db.users.find_one({"email": reg_data.email.lower()}, {"_id": 0})
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered. Please login instead.")
    
    # Hash password
    hashed_password, salt = hash_password(reg_data.password)
    
    # Create user
    user_id = f"user_{uuid.uuid4().hex[:12]}"
    user_doc = {
        "user_id": user_id,
        "email": reg_data.email.lower(),
        "name": reg_data.name,
        "password_hash": hashed_password,
        "password_salt": salt,
        "auth_type": "email",
        "picture": None,
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    
    await db.users.insert_one(user_doc)
    
    # Create session
    session_token = uuid.uuid4().hex
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
        "email": reg_data.email.lower(),
        "name": reg_data.name,
        "picture": None,
        "session_token": session_token
    }

@router.post("/login")
@limiter.limit("5/minute")
async def login_user(request: Request, response: Response):
    """Login with email/password"""
    body = await request.json()
    login_data = LoginRequest(**body)
    # Find user
    user_doc = await db.users.find_one({"email": login_data.email.lower()}, {"_id": 0})
    
    if not user_doc:
        raise HTTPException(status_code=401, detail="Invalid email or password")
    
    # Check if user has password (email auth) OR is a Google user who set a password
    if not user_doc.get("password_hash"):
        raise HTTPException(status_code=401, detail="This account uses Google login. Please sign in with Google, or set a password first from your profile.")
    
    # Verify password
    if not verify_password(login_data.password, user_doc["password_hash"], user_doc["password_salt"]):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    
    # Create session
    session_token = uuid.uuid4().hex
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
        "picture": user_doc.get("picture"),
        "session_token": session_token
    }

@router.post("/google/callback")
async def google_oauth_callback(request: Request, response: Response):
    """Direct Google OAuth callback — exchanges `code` from Google for user profile, issues session_token.
    
    Flow:
      1. Frontend redirects user to https://accounts.google.com/o/oauth2/v2/auth with client_id, redirect_uri, scope=openid email profile.
      2. Google redirects back to /auth/callback?code=... on the frontend.
      3. Frontend POSTs {code, redirect_uri} to this endpoint.
      4. This endpoint exchanges code for id_token + access_token at Google's token endpoint.
      5. Verifies id_token signature + audience against GOOGLE_CLIENT_ID.
      6. Upserts user record (matched by verified email) and issues session_token.
    """
    from config import GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET
    from google.oauth2 import id_token as google_id_token
    from google.auth.transport import requests as google_requests

    if not GOOGLE_CLIENT_ID or not GOOGLE_CLIENT_SECRET:
        raise HTTPException(status_code=503, detail="Google OAuth not configured on this server")

    body = await request.json()
    code = body.get("code")
    redirect_uri = body.get("redirect_uri")
    if not code or not redirect_uri:
        raise HTTPException(status_code=400, detail="code and redirect_uri required")

    # 1) Exchange code for tokens at Google's token endpoint
    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            token_response = await client.post(
                "https://oauth2.googleapis.com/token",
                data={
                    "code": code,
                    "client_id": GOOGLE_CLIENT_ID,
                    "client_secret": GOOGLE_CLIENT_SECRET,
                    "redirect_uri": redirect_uri,
                    "grant_type": "authorization_code",
                },
            )
    except httpx.RequestError as e:
        logger.error(f"Google token exchange failed: {e}")
        raise HTTPException(status_code=504, detail="Google authentication server unreachable. Please try again.")

    if token_response.status_code != 200:
        logger.warning(f"Google token exchange rejected: {token_response.status_code} {token_response.text[:200]}")
        raise HTTPException(status_code=401, detail="Invalid or expired authorization code. Please sign in again.")

    tokens = token_response.json()
    google_id_token_str = tokens.get("id_token")
    if not google_id_token_str:
        raise HTTPException(status_code=502, detail="Google did not return an id_token")

    # 2) Verify id_token signature + audience
    try:
        user_data = google_id_token.verify_oauth2_token(
            google_id_token_str,
            google_requests.Request(),
            GOOGLE_CLIENT_ID,
        )
    except ValueError as e:
        logger.warning(f"Google id_token verification failed: {e}")
        raise HTTPException(status_code=401, detail="Invalid id_token from Google")

    email = user_data.get("email")
    if not email or not user_data.get("email_verified", False):
        raise HTTPException(status_code=403, detail="Google account email is not verified")

    name = user_data.get("name") or user_data.get("given_name") or email.split("@")[0]
    picture = user_data.get("picture")

    logger.info(f"Google OAuth direct: verified email={email}")

    # 3) Upsert user
    existing_user = await db.users.find_one({"email": email}, {"_id": 0})
    if existing_user:
        user_id = existing_user["user_id"]
        await db.users.update_one(
            {"user_id": user_id},
            {"$set": {
                "name": name,
                "picture": picture,
                "updated_at": datetime.now(timezone.utc).isoformat(),
            }}
        )
        logger.info(f"Google OAuth direct: updated existing user {user_id}")
    else:
        user_id = f"user_{uuid.uuid4().hex[:12]}"
        await db.users.insert_one({
            "user_id": user_id,
            "email": email,
            "name": name,
            "picture": picture,
            "auth_type": "google",
            "created_at": datetime.now(timezone.utc).isoformat(),
        })
        logger.info(f"Google OAuth direct: created new user {user_id}")

    # 4) Issue session_token
    session_token = uuid.uuid4().hex
    expires_at = datetime.now(timezone.utc) + timedelta(days=7)
    await db.user_sessions.insert_one({
        "user_id": user_id,
        "session_token": session_token,
        "expires_at": expires_at.isoformat(),
        "created_at": datetime.now(timezone.utc).isoformat(),
    })

    response.set_cookie(
        key="session_token",
        value=session_token,
        httponly=True,
        secure=True,
        samesite="none",
        path="/",
        max_age=7 * 24 * 60 * 60,
    )

    user_doc = await db.users.find_one({"user_id": user_id}, {"_id": 0})
    safe_response = {
        "user_id": user_doc.get("user_id"),
        "email": user_doc.get("email"),
        "name": user_doc.get("name"),
        "picture": user_doc.get("picture"),
        "session_token": session_token,
        "terms_accepted": user_doc.get("terms_accepted", False),
        "created_at": user_doc.get("created_at"),
    }
    logger.info(f"Google OAuth direct: SUCCESS — issuing session for {email}, token={session_token[:8]}...")
    return safe_response


@router.post("/session")
async def create_session(request: Request, response: Response):
    """DO_NOT_UNDO — Exchange session_id for session_token (Google OAuth via Emergent)"""
    # REMINDER: DO NOT HARDCODE THE URL, OR ADD ANY FALLBACKS OR REDIRECT URLS, THIS BREAKS THE AUTH
    import asyncio
    body = await request.json()
    session_id = body.get("session_id")
    
    if not session_id:
        raise HTTPException(status_code=400, detail="session_id required")
    
    # DO_NOT_UNDO — Call Emergent Auth to get user data with server-side retry.
    # Session data may take a moment to propagate on the Emergent side after redirect.
    logger.info(f"Google auth: exchanging session_id (len={len(session_id)})")
    
    retry_delays = [0, 1.0, 2.0, 3.0, 5.0]
    auth_response = None
    last_error = None
    
    for attempt, delay in enumerate(retry_delays):
        if delay > 0:
            await asyncio.sleep(delay)
        try:
            async with httpx.AsyncClient(timeout=15.0) as client:
                auth_response = await client.get(
                    "https://demobackend.emergentagent.com/auth/v1/env/oauth/session-data",
                    headers={"X-Session-ID": session_id}
                )
            logger.info(f"Google auth attempt {attempt+1}/{len(retry_delays)}: Emergent status={auth_response.status_code}")
            if auth_response.status_code == 200:
                break
        except httpx.ConnectTimeout:
            last_error = "timeout"
            logger.warning(f"Google auth attempt {attempt+1}/{len(retry_delays)}: Emergent timed out")
        except httpx.RequestError as e:
            last_error = str(e)
            logger.warning(f"Google auth attempt {attempt+1}/{len(retry_delays)}: Emergent error: {e}")
    
    if auth_response is None:
        logger.error(f"Google auth: all {len(retry_delays)} attempts failed (last_error={last_error})")
        raise HTTPException(status_code=504, detail="Authentication server unreachable. Please try again.")
    
    if auth_response.status_code != 200:
        logger.warning(f"Google auth: session_id exchange failed after {len(retry_delays)} attempts. Last status={auth_response.status_code}: {auth_response.text[:200]}")
        raise HTTPException(status_code=401, detail="Invalid or expired session. Please try logging in again.")
    
    user_data = auth_response.json()
    logger.info(f"Google auth: Emergent returned user email={user_data.get('email')}")
    
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
        logger.info(f"Google auth: updated existing user {user_id}")
    else:
        await db.users.insert_one({
            "user_id": user_id,
            "email": user_data["email"],
            "name": user_data["name"],
            "picture": user_data.get("picture"),
            "auth_type": "google",
            "created_at": datetime.now(timezone.utc).isoformat()
        })
        logger.info(f"Google auth: created new user {user_id}")
    
    # Create session
    session_token = uuid.uuid4().hex
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
    # Return ONLY safe fields — never leak password_hash, password_salt, or internal fields
    safe_response = {
        "user_id": user_doc.get("user_id"),
        "email": user_doc.get("email"),
        "name": user_doc.get("name"),
        "picture": user_doc.get("picture"),
        "session_token": session_token,
        "terms_accepted": user_doc.get("terms_accepted", False),
        "created_at": user_doc.get("created_at"),
    }
    logger.info(f"Google auth: SUCCESS — returning session for {user_data.get('email')}, token={session_token[:8]}...")
    return safe_response

@router.get("/me")
async def get_me(request: Request):
    """Get current user info"""
    user = await get_current_user(request)
    user_dict = user.model_dump()
    # Check if user has accepted terms
    user_doc = await db.users.find_one({"user_id": user.user_id}, {"_id": 0})
    user_dict["terms_accepted"] = user_doc.get("terms_accepted", False)
    user_dict["terms_accepted_at"] = user_doc.get("terms_accepted_at")
    user_dict["is_admin"] = user.email in get_admin_emails()
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

class SetPasswordRequest(BaseModel):
    password: str

@router.post("/set-password")
async def set_password(req: SetPasswordRequest, request: Request):
    """Allow any authenticated user (including Google users) to set/change their password"""
    user = await get_current_user(request)
    
    if len(req.password) < 6:
        raise HTTPException(status_code=400, detail="Password must be at least 6 characters")
    
    password_hash, password_salt = hash_password(req.password)
    await db.users.update_one(
        {"user_id": user.user_id},
        {"$set": {"password_hash": password_hash, "password_salt": password_salt}}
    )
    return {"message": "Password set successfully. You can now log in with email and password."}


@router.post("/logout")
async def logout(request: Request, response: Response):
    """Logout user"""
    session_token = request.cookies.get("session_token")
    if not session_token:
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            session_token = auth_header.split(" ")[1]
    if session_token:
        await db.user_sessions.delete_one({"session_token": session_token})
    
    response.delete_cookie(key="session_token", path="/", samesite="lax", secure=True)
    return {"message": "Logged out"}



# ============ DOWNLOAD TOKEN ============

@router.post("/download-token")
async def generate_download_token(request: Request):
    """Generate a short-lived, single-use download token for file downloads.
    Replaces session_token in URLs to prevent session hijack via logs/Referrer."""
    user = await get_current_user(request)
    token = secrets.token_urlsafe(32)
    await db.download_tokens.insert_one({
        "token": token,
        "user_id": user.user_id,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "expires_at": (datetime.now(timezone.utc) + timedelta(minutes=5)).isoformat(),
        "used": False,
    })
    return {"download_token": token}
