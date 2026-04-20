# DO NOT UNDO — admin router. All endpoints in this file are approved and must be preserved.
"""
Criminal Appeal AI - Admin Router
Handles admin-only routes: contact messages, success stories, analytics
"""
from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel
from typing import Optional
from datetime import datetime, timezone, timedelta
import os
import uuid
import asyncio
import resend

from config import db, logger, get_admin_emails, get_contact_email, get_resend_from_email, limiter
from auth_utils import get_current_user

router = APIRouter(prefix="/api", tags=["admin"])

# Admin configuration
ADMIN_EMAILS = get_admin_emails()  # Cached at startup; use get_admin_emails() for live checks

# Resend email configuration
RESEND_API_KEY = os.environ.get("RESEND_API_KEY", "")
CONTACT_EMAIL = get_contact_email()

if RESEND_API_KEY:
    resend.api_key = RESEND_API_KEY
    logger.info("Resend email configured")
else:
    logger.warning("Resend API key not configured - contact form will store messages only")

# ============ MODELS ============

class ContactMessage(BaseModel):
    name: str
    email: str
    subject: str
    message: str

class SuccessStorySubmission(BaseModel):
    name: str
    email: str
    relationship: Optional[str] = ""
    story: str
    outcome: Optional[str] = ""
    consent: bool

# ============ VISITOR TRACKING ============

@router.post("/track/visit")
async def track_visit(request: Request):
    """Track a site visit"""
    try:
        # Get visitor info
        forwarded_for = request.headers.get("X-Forwarded-For", "")
        ip = forwarded_for.split(",")[0].strip() if forwarded_for else request.client.host if request.client else "unknown"
        user_agent = request.headers.get("User-Agent", "unknown")
        referer = request.headers.get("Referer", "direct")
        
        # Store visit
        visit = {
            "ip_hash": hash(ip) % 10000000,  # Hash IP for privacy
            "user_agent": user_agent[:200],  # Truncate
            "referer": referer[:500],
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "page": "landing"
        }
        await db.visits.insert_one(visit)
        
        # Update daily counter
        today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        await db.visit_stats.update_one(
            {"date": today},
            {"$inc": {"count": 1}},
            upsert=True
        )
        
        # Get total count
        total = await db.visits.count_documents({})
        
        return {"tracked": True, "total_visits": total}
    except Exception as e:
        logger.error(f"Visit tracking error: {e}")
        return {"tracked": False}

@router.get("/stats/visits")
async def get_visit_stats(request: Request):
    """Get visit statistics (admin only - requires auth)"""
    try:
        user = await get_current_user(request)
        
        # Only allow admin emails
        if user.email not in ADMIN_EMAILS:
            raise HTTPException(status_code=403, detail="Admin access required")
        
        total_visits = await db.visits.count_documents({})
        total_users = await db.users.count_documents({})
        total_cases = await db.cases.count_documents({})
        
        # Get last 7 days stats
        daily_stats = []
        for i in range(7):
            date = (datetime.now(timezone.utc) - timedelta(days=i)).strftime("%Y-%m-%d")
            stat = await db.visit_stats.find_one({"date": date}, {"_id": 0})
            daily_stats.append({
                "date": date,
                "count": stat["count"] if stat else 0
            })
        
        return {
            "total_visits": total_visits,
            "total_users": total_users,
            "total_cases": total_cases,
            "daily_stats": daily_stats
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Stats error: {e}")
        raise HTTPException(status_code=500, detail="Failed to get stats")

# ============ CONTACT FORM ============

@router.post("/contact")
@limiter.limit("3/minute")
async def submit_contact_form(request: Request, contact: ContactMessage):
    """Submit a contact form message"""
    try:
        # Store message in database
        message_doc = {
            "message_id": f"msg_{uuid.uuid4().hex[:12]}",
            "name": contact.name,
            "email": contact.email,
            "subject": contact.subject,
            "message": contact.message,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "read": False
        }
        await db.contact_messages.insert_one(message_doc)
        
        # Try to send email notification
        email_sent = False
        if RESEND_API_KEY:
            try:
                import html as html_mod
                safe_name = html_mod.escape(contact.name or "")
                safe_email = html_mod.escape(contact.email or "")
                safe_subject = html_mod.escape(contact.subject or "")
                safe_message = html_mod.escape(contact.message or "")
                html_content = f"""
                <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
                    <h2 style="color: #1e293b; border-bottom: 2px solid #f59e0b; padding-bottom: 10px;">
                        New Contact Form Message
                    </h2>
                    <div style="background: #f8fafc; padding: 20px; border-radius: 8px; margin: 20px 0;">
                        <p><strong>From:</strong> {safe_name}</p>
                        <p><strong>Email:</strong> {safe_email}</p>
                        <p><strong>Subject:</strong> {safe_subject}</p>
                    </div>
                    <div style="background: #fff; padding: 20px; border: 1px solid #e2e8f0; border-radius: 8px;">
                        <p><strong>Message:</strong></p>
                        <p style="white-space: pre-wrap;">{safe_message}</p>
                    </div>
                    <p style="color: #64748b; font-size: 12px; margin-top: 20px;">
                        Sent from Appeal Case Manager contact form
                    </p>
                </div>
                """
                
                params = {
                    "from": get_resend_from_email(),
                    "to": [CONTACT_EMAIL],
                    "subject": f"Contact Form: {contact.subject}",
                    "html": html_content,
                    "reply_to": contact.email
                }
                
                await asyncio.to_thread(resend.Emails.send, params)
                email_sent = True
                logger.info(f"Contact form email sent to {CONTACT_EMAIL}")
            except Exception as e:
                logger.error(f"Failed to send contact email: {e}")
        
        return {
            "success": True,
            "message": "Your message has been sent. We'll get back to you soon!",
            "email_sent": email_sent
        }
    except Exception as e:
        logger.error(f"Contact form error: {e}")
        raise HTTPException(status_code=500, detail="Failed to send message")

@router.get("/admin/messages")
async def get_contact_messages(request: Request):
    """Get all contact messages (admin only)"""
    user = await get_current_user(request)
    if user.email not in ADMIN_EMAILS:
        raise HTTPException(status_code=403, detail="Admin access required")
    
    messages = await db.contact_messages.find({}, {"_id": 0}).sort("timestamp", -1).to_list(100)
    unread_count = await db.contact_messages.count_documents({"read": False})
    
    return {
        "messages": messages,
        "unread_count": unread_count
    }

@router.post("/admin/messages/{message_id}/read")
async def mark_message_read(message_id: str, request: Request):
    """Mark a message as read"""
    user = await get_current_user(request)
    if user.email not in ADMIN_EMAILS:
        raise HTTPException(status_code=403, detail="Admin access required")
    
    await db.contact_messages.update_one(
        {"message_id": message_id},
        {"$set": {"read": True}}
    )
    return {"success": True}

# ============ SUCCESS STORIES ============

@router.post("/success-stories")
async def submit_success_story(submission: SuccessStorySubmission):
    """Submit a success story"""
    if not submission.consent:
        raise HTTPException(status_code=400, detail="Consent is required")
    
    story_doc = {
        "story_id": f"story_{uuid.uuid4().hex[:12]}",
        "name": submission.name,
        "email": submission.email,
        "relationship": submission.relationship,
        "story": submission.story,
        "outcome": submission.outcome,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "approved": False,
        "featured": False
    }
    await db.success_stories.insert_one(story_doc)
    
    return {"success": True, "message": "Story submitted for review"}

@router.get("/admin/success-stories")
async def get_submitted_stories(request: Request):
    """Get all submitted stories (admin only)"""
    user = await get_current_user(request)
    if user.email not in ADMIN_EMAILS:
        raise HTTPException(status_code=403, detail="Admin access required")
    
    stories = await db.success_stories.find({}, {"_id": 0}).sort("timestamp", -1).to_list(100)
    return {"stories": stories}


# ============ DATABASE NORMALISATION ============

@router.post("/admin/normalise-db")
async def normalise_database(request: Request):
    """DO_NOT_UNDO — Run database normalisation script (admin only).
    Fixes missing fields, removes stale sessions, and cleans up duplicate grounds.
    Safe to run multiple times (idempotent).
    """
    user = await get_current_user(request)
    if user.email not in ADMIN_EMAILS:
        raise HTTPException(status_code=403, detail="Admin access required")

    from scripts.normalise_db import (
        normalise_cases, normalise_grounds, normalise_reports,
        normalise_documents, normalise_timeline_events,
        normalise_issue_classifications, cleanup_stale_sessions,
        run_ground_dedup,
    )

    results = {}
    results["cases"] = await normalise_cases(db)
    results["grounds"] = await normalise_grounds(db)
    results["reports"] = await normalise_reports(db)
    results["documents"] = await normalise_documents(db)
    results["timeline_events"] = await normalise_timeline_events(db)
    results["issue_classifications"] = await normalise_issue_classifications(db)
    results["sessions"] = await cleanup_stale_sessions(db)
    results["dedup"] = await run_ground_dedup(db)

    total_updated = sum(r.get("updated", 0) for r in results.values())
    total_removed = results["sessions"].get("removed", 0) + results["dedup"].get("grounds_removed", 0) + results["dedup"].get("issues_removed", 0)

    return {
        "results": results,
        "summary": f"{total_updated} documents updated, {total_removed} stale entries removed",
    }



# DO_NOT_UNDO — Admin manual unlock endpoint
@router.post("/admin/unlock-feature")
async def admin_unlock_feature(request: Request):
    """Admin-only: manually unlock a feature for any user's case.
    Body: { email: str, case_id: str, feature_type: str }
    """
    user = await get_current_user(request)
    if user.email not in ADMIN_EMAILS:
        raise HTTPException(status_code=403, detail="Admin access required")

    body = await request.json()
    target_email = body.get("email")
    case_id = body.get("case_id")
    feature_type = body.get("feature_type", "grounds_of_merit")

    if not target_email or not case_id:
        raise HTTPException(status_code=400, detail="email and case_id are required")

    # Find the target user
    target_user = await db.users.find_one({"email": target_email}, {"_id": 0, "user_id": 1})
    if not target_user:
        raise HTTPException(status_code=404, detail=f"User {target_email} not found")

    target_uid = target_user["user_id"]

    # Find the case
    case = await db.cases.find_one({"case_id": case_id, "user_id": target_uid}, {"_id": 0})
    if not case:
        raise HTTPException(status_code=404, detail=f"Case {case_id} not found for {target_email}")

    # Add to unlocked_features
    await db.cases.update_one(
        {"case_id": case_id, "user_id": target_uid},
        {"$addToSet": {"unlocked_features": feature_type}},
    )

    # Create a payment record
    payment = {
        "payment_id": f"pay_{uuid.uuid4().hex[:12]}",
        "user_id": target_uid,
        "case_id": case_id,
        "feature_type": feature_type,
        "amount": 0,
        "method": "admin_manual",
        "reference": f"ACM-ADMIN-{uuid.uuid4().hex[:6].upper()}",
        "status": "completed",
        "confirmed_by": user.email,
        "confirmed_at": datetime.now(timezone.utc).isoformat(),
        "created_at": datetime.now(timezone.utc).isoformat(),
        "notes": f"Manually unlocked by admin {user.email}",
    }
    await db.payments.insert_one(payment)
    payment.pop("_id", None)

    return {
        "success": True,
        "message": f"Unlocked {feature_type} for {target_email} on case {case_id}",
        "reference": payment["reference"],
    }


# ============ SIGNUP SOURCE ANALYTICS ============

@router.get("/admin/signup-sources")
async def get_signup_sources(request: Request):
    """Admin-only: aggregated count of new user sign-ups grouped by source CTA/page.

    `signup_source` is captured on the user doc at Google OAuth sign-up time
    (see routers/auth.py google_oauth_callback), value comes from the page
    path that triggered startGoogleLogin(). This endpoint returns:
      {
        "total_users": 42,
        "users_with_source": 37,
        "sources": [
          {"source": "/success-stories", "count": 18, "first": "2026-02-14T...", "last": "2026-04-20T..."},
          {"source": "/",               "count": 12, ...},
          ...
        ]
      }
    """
    user = await get_current_user(request)
    if user.email not in ADMIN_EMAILS:
        raise HTTPException(status_code=403, detail="Admin access required")

    total_users = await db.users.count_documents({})
    users_with_source = await db.users.count_documents({"signup_source": {"$exists": True, "$ne": None}})

    pipeline = [
        {"$match": {"signup_source": {"$exists": True, "$ne": None}}},
        {"$group": {
            "_id": "$signup_source",
            "count": {"$sum": 1},
            "first": {"$min": "$created_at"},
            "last": {"$max": "$created_at"},
        }},
        {"$sort": {"count": -1}},
        {"$project": {"_id": 0, "source": "$_id", "count": 1, "first": 1, "last": 1}},
    ]
    sources = await db.users.aggregate(pipeline).to_list(100)

    return {
        "total_users": total_users,
        "users_with_source": users_with_source,
        "sources": sources,
    }
