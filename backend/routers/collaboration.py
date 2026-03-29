"""
Criminal Appeal AI - Collaboration Router
Handles case sharing, real-time chat, activity feed, and notifications
"""
from fastapi import APIRouter, HTTPException, Request, WebSocket, WebSocketDisconnect
from pydantic import BaseModel
from typing import Dict
import os
import asyncio
import json
import resend

from config import db, logger, get_frontend_url
from auth_utils import get_current_user

router = APIRouter(tags=["collaboration"])

# Resend config
RESEND_API_KEY = os.environ.get("RESEND_API_KEY", "")
if RESEND_API_KEY:
    resend.api_key = RESEND_API_KEY

# WebSocket connections for chat
chat_ws_connections: Dict[str, Dict[str, WebSocket]] = {}


# ============ HELPER: verify case access (owner OR shared) ============

async def verify_case_access(case_id: str, user_id: str):
    """Check if user owns the case or has been shared access."""
    case = await db.cases.find_one({"case_id": case_id}, {"_id": 0})
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")

    if case.get("user_id") == user_id:
        return case, "owner"

    share = await db.case_shares.find_one({
        "case_id": case_id,
        "shared_with_user_id": user_id,
        "status": "accepted"
    }, {"_id": 0})
    if share:
        return case, "shared"

    raise HTTPException(status_code=403, detail="Access denied")


async def log_activity(case_id: str, user_id: str, user_name: str, action: str, detail: str = ""):
    """Log an activity event for a case."""
    from models import Activity
    act = Activity(case_id=case_id, user_id=user_id, user_name=user_name, action=action, detail=detail)
    act_dict = act.model_dump()
    act_dict["created_at"] = act_dict["created_at"].isoformat()
    await db.activities.insert_one(act_dict)


async def create_notification(user_id: str, ntype: str, title: str, message: str,
                              case_id: str = None, from_user_name: str = None):
    """Create an in-app notification."""
    from models import Notification
    notif = Notification(
        user_id=user_id, type=ntype, title=title, message=message,
        case_id=case_id, from_user_name=from_user_name
    )
    notif_dict = notif.model_dump()
    notif_dict["created_at"] = notif_dict["created_at"].isoformat()
    await db.notifications.insert_one(notif_dict)


async def send_email_notification(to_email: str, subject: str, html_body: str):
    """Send an email notification via Resend."""
    if not RESEND_API_KEY:
        logger.warning(f"Resend not configured — skipping email to {to_email}")
        return
    try:
        params = {
            "from": "Appeal Case Manager <onboarding@resend.dev>",
            "to": [to_email],
            "subject": subject,
            "html": html_body
        }
        await asyncio.to_thread(resend.Emails.send, params)
        logger.info(f"Email sent to {to_email}: {subject}")
    except Exception as e:
        logger.error(f"Failed to send email to {to_email}: {e}")


# ============ REQUEST MODELS ============

class ShareByEmailRequest(BaseModel):
    email: str

class MessageCreate(BaseModel):
    content: str


# ============ CASE SHARING ENDPOINTS ============

@router.post("/api/cases/{case_id}/share")
async def share_case_by_email(case_id: str, req: ShareByEmailRequest, request: Request):
    """Share a case with another user by email."""
    user = await get_current_user(request)

    case = await db.cases.find_one({"case_id": case_id, "user_id": user.user_id}, {"_id": 0})
    if not case:
        raise HTTPException(status_code=404, detail="Case not found or not owned by you")

    if req.email.lower() == user.email.lower():
        raise HTTPException(status_code=400, detail="Cannot share a case with yourself")

    existing = await db.case_shares.find_one({
        "case_id": case_id, "shared_with_email": req.email.lower(), "status": {"$ne": "revoked"}
    }, {"_id": 0})
    if existing:
        raise HTTPException(status_code=400, detail="Case already shared with this email")

    from models import CaseShare
    target_user = await db.users.find_one({"email": req.email.lower()}, {"_id": 0})

    share = CaseShare(
        case_id=case_id,
        owner_id=user.user_id,
        shared_with_email=req.email.lower(),
        shared_with_user_id=target_user["user_id"] if target_user else None,
        status="accepted" if target_user else "pending"
    )
    share_dict = share.model_dump()
    share_dict["created_at"] = share_dict["created_at"].isoformat()
    await db.case_shares.insert_one(share_dict)

    await log_activity(case_id, user.user_id, user.name, "shared_case", f"Shared with {req.email}")

    if target_user:
        await create_notification(
            target_user["user_id"], "share_invite",
            "Case Shared With You",
            f"{user.name} shared the case \"{case.get('title', '')}\" with you.",
            case_id=case_id, from_user_name=user.name
        )

    frontend_url = get_frontend_url()
    html = f"""
    <div style="font-family:Arial,sans-serif;max-width:600px;margin:0 auto;">
        <h2 style="color:#1e3a5f;">Case Shared With You</h2>
        <p><strong>{user.name}</strong> has shared the case "<strong>{case.get('title','')}</strong>" with you on Appeal Case Manager.</p>
        <p>You can view the case, add notes, and participate in the discussion.</p>
        <a href="{frontend_url}/dashboard" style="display:inline-block;padding:12px 24px;background:#2563eb;color:#fff;text-decoration:none;border-radius:8px;margin-top:12px;">
            Open Dashboard
        </a>
        <p style="color:#94a3b8;font-size:12px;margin-top:24px;">Appeal Case Manager — Australian Law Only. Not legal advice.</p>
    </div>
    """
    await send_email_notification(req.email.lower(), f"{user.name} shared a case with you", html)

    return {"share_id": share.share_id, "status": share.status, "message": "Case shared successfully"}


@router.post("/api/cases/{case_id}/share-link")
async def generate_share_link(case_id: str, request: Request):
    """Generate a shareable link for a case."""
    user = await get_current_user(request)

    case = await db.cases.find_one({"case_id": case_id, "user_id": user.user_id}, {"_id": 0})
    if not case:
        raise HTTPException(status_code=404, detail="Case not found or not owned by you")

    existing = await db.share_links.find_one({"case_id": case_id, "owner_id": user.user_id, "is_active": True}, {"_id": 0})
    if existing:
        frontend_url = get_frontend_url()
        return {"link": f"{frontend_url}/shared/{existing['token']}", "token": existing["token"], "link_id": existing["link_id"]}

    from models import ShareLink
    link = ShareLink(case_id=case_id, owner_id=user.user_id)
    link_dict = link.model_dump()
    link_dict["created_at"] = link_dict["created_at"].isoformat()
    if link_dict.get("expires_at"):
        link_dict["expires_at"] = link_dict["expires_at"].isoformat()
    await db.share_links.insert_one(link_dict)

    frontend_url = get_frontend_url()
    return {"link": f"{frontend_url}/shared/{link.token}", "token": link.token, "link_id": link.link_id}


@router.post("/api/share-link/{token}/accept")
async def accept_share_link(token: str, request: Request):
    """Accept a shareable link — creates a share record for the current user."""
    user = await get_current_user(request)

    link = await db.share_links.find_one({"token": token, "is_active": True}, {"_id": 0})
    if not link:
        raise HTTPException(status_code=404, detail="Invalid or expired share link")

    if link["owner_id"] == user.user_id:
        return {"case_id": link["case_id"], "message": "You own this case"}

    existing = await db.case_shares.find_one({
        "case_id": link["case_id"], "shared_with_user_id": user.user_id, "status": {"$ne": "revoked"}
    }, {"_id": 0})
    if existing:
        return {"case_id": link["case_id"], "message": "Already have access"}

    from models import CaseShare
    share = CaseShare(
        case_id=link["case_id"],
        owner_id=link["owner_id"],
        shared_with_email=user.email,
        shared_with_user_id=user.user_id,
        status="accepted"
    )
    share_dict = share.model_dump()
    share_dict["created_at"] = share_dict["created_at"].isoformat()
    await db.case_shares.insert_one(share_dict)

    await log_activity(link["case_id"], user.user_id, user.name, "joined_via_link", "Joined via shareable link")

    owner = await db.users.find_one({"user_id": link["owner_id"]}, {"_id": 0})
    if owner:
        await create_notification(
            owner["user_id"], "share_accepted",
            "Someone Joined Your Case",
            f"{user.name} joined your shared case via link.",
            case_id=link["case_id"], from_user_name=user.name
        )

    return {"case_id": link["case_id"], "message": "Access granted"}


@router.get("/api/cases/{case_id}/shares")
async def list_case_shares(case_id: str, request: Request):
    """List all shares for a case (owner only)."""
    user = await get_current_user(request)
    case = await db.cases.find_one({"case_id": case_id, "user_id": user.user_id}, {"_id": 0})
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")

    shares = await db.case_shares.find(
        {"case_id": case_id, "status": {"$ne": "revoked"}}, {"_id": 0}
    ).to_list(100)

    link = await db.share_links.find_one({"case_id": case_id, "is_active": True}, {"_id": 0})
    share_link = None
    if link:
        frontend_url = get_frontend_url()
        share_link = {"link": f"{frontend_url}/shared/{link['token']}", "link_id": link["link_id"]}

    return {"shares": shares, "share_link": share_link}


@router.delete("/api/cases/{case_id}/shares/{share_id}")
async def revoke_share(case_id: str, share_id: str, request: Request):
    """Revoke a specific share."""
    user = await get_current_user(request)
    result = await db.case_shares.update_one(
        {"share_id": share_id, "case_id": case_id, "owner_id": user.user_id},
        {"$set": {"status": "revoked"}}
    )
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="Share not found")
    return {"message": "Share revoked"}


@router.delete("/api/cases/{case_id}/share-link")
async def revoke_share_link(case_id: str, request: Request):
    """Deactivate the share link for a case."""
    user = await get_current_user(request)
    await db.share_links.update_many(
        {"case_id": case_id, "owner_id": user.user_id},
        {"$set": {"is_active": False}}
    )
    return {"message": "Share link deactivated"}


@router.get("/api/shared-cases")
async def get_shared_cases(request: Request):
    """Get all cases shared with the current user."""
    user = await get_current_user(request)

    shares = await db.case_shares.find(
        {"shared_with_user_id": user.user_id, "status": "accepted"}, {"_id": 0}
    ).to_list(100)

    case_ids = [s["case_id"] for s in shares]
    if not case_ids:
        return []

    cases = await db.cases.find({"case_id": {"$in": case_ids}}, {"_id": 0}).to_list(100)

    for c in cases:
        owner = await db.users.find_one({"user_id": c["user_id"]}, {"_id": 0})
        c["owner_name"] = owner.get("name", "Unknown") if owner else "Unknown"
        c["owner_email"] = owner.get("email", "") if owner else ""
        c["is_shared"] = True

    return cases


# ============ CHAT / MESSAGING ENDPOINTS ============

@router.get("/api/cases/{case_id}/messages")
async def get_messages(case_id: str, request: Request):
    """Get chat messages for a case."""
    user = await get_current_user(request)
    await verify_case_access(case_id, user.user_id)

    messages = await db.case_messages.find(
        {"case_id": case_id}, {"_id": 0}
    ).sort("created_at", 1).to_list(500)

    return messages


@router.post("/api/cases/{case_id}/messages")
async def send_message(case_id: str, msg: MessageCreate, request: Request):
    """Send a chat message in a case."""
    user = await get_current_user(request)
    case, role = await verify_case_access(case_id, user.user_id)

    if not msg.content.strip():
        raise HTTPException(status_code=400, detail="Message cannot be empty")

    from models import CaseMessage
    message = CaseMessage(
        case_id=case_id,
        user_id=user.user_id,
        author_name=user.name,
        author_email=user.email,
        content=msg.content.strip()
    )
    msg_dict = message.model_dump()
    msg_dict["created_at"] = msg_dict["created_at"].isoformat()
    await db.case_messages.insert_one(msg_dict)

    await log_activity(case_id, user.user_id, user.name, "sent_message", msg.content[:80])

    # Notify all participants except sender
    participants = set()
    participants.add(case.get("user_id"))
    shares = await db.case_shares.find({"case_id": case_id, "status": "accepted"}, {"_id": 0}).to_list(50)
    for s in shares:
        if s.get("shared_with_user_id"):
            participants.add(s["shared_with_user_id"])
    participants.discard(user.user_id)

    for pid in participants:
        await create_notification(
            pid, "new_message",
            "New Message",
            f"{user.name}: {msg.content[:100]}",
            case_id=case_id, from_user_name=user.name
        )

    # Broadcast to WebSocket clients
    await broadcast_chat_event(case_id, "new_message", {
        "message_id": message.message_id,
        "user_id": user.user_id,
        "author_name": user.name,
        "content": msg.content.strip(),
        "created_at": msg_dict["created_at"]
    })

    result = await db.case_messages.find_one({"message_id": message.message_id}, {"_id": 0})
    return result


# ============ ACTIVITY FEED ============

@router.get("/api/cases/{case_id}/activity")
async def get_activity(case_id: str, request: Request):
    """Get activity feed for a case."""
    user = await get_current_user(request)
    await verify_case_access(case_id, user.user_id)

    activities = await db.activities.find(
        {"case_id": case_id}, {"_id": 0}
    ).sort("created_at", -1).to_list(100)

    return activities


# ============ NOTIFICATIONS ============

@router.get("/api/notifications")
async def get_notifications(request: Request):
    """Get notifications for the current user."""
    user = await get_current_user(request)

    notifications = await db.notifications.find(
        {"user_id": user.user_id}, {"_id": 0}
    ).sort("created_at", -1).to_list(50)

    unread_count = await db.notifications.count_documents({"user_id": user.user_id, "is_read": False})

    return {"notifications": notifications, "unread_count": unread_count}


@router.patch("/api/notifications/{notification_id}/read")
async def mark_notification_read(notification_id: str, request: Request):
    """Mark a notification as read."""
    user = await get_current_user(request)
    await db.notifications.update_one(
        {"notification_id": notification_id, "user_id": user.user_id},
        {"$set": {"is_read": True}}
    )
    return {"message": "Marked as read"}


@router.patch("/api/notifications/read-all")
async def mark_all_notifications_read(request: Request):
    """Mark all notifications as read."""
    user = await get_current_user(request)
    await db.notifications.update_many(
        {"user_id": user.user_id, "is_read": False},
        {"$set": {"is_read": True}}
    )
    return {"message": "All marked as read"}


# ============ CHAT WEBSOCKET ============

async def broadcast_chat_event(case_id: str, event_type: str, payload: dict):
    """Broadcast a chat event to all WebSocket connections for a case."""
    connections = chat_ws_connections.get(case_id, {})
    dead = []
    for uid, ws in connections.items():
        try:
            await ws.send_json({"type": event_type, "payload": payload})
        except Exception:
            dead.append(uid)
    for uid in dead:
        connections.pop(uid, None)


@router.websocket("/api/cases/{case_id}/chat/ws")
async def chat_websocket(websocket: WebSocket, case_id: str):
    """Real-time chat WebSocket for a case."""
    session_token = websocket.query_params.get("session_token") or websocket.cookies.get("session_token")

    try:
        from models import User
        if not session_token:
            await websocket.close(code=4401)
            return

        session_doc = await db.user_sessions.find_one({"session_token": session_token}, {"_id": 0})
        if not session_doc:
            await websocket.close(code=4401)
            return

        user_doc = await db.users.find_one({"user_id": session_doc["user_id"]}, {"_id": 0})
        if not user_doc:
            await websocket.close(code=4401)
            return

        user = User(**user_doc)

        # Verify access
        try:
            await verify_case_access(case_id, user.user_id)
        except HTTPException:
            await websocket.close(code=4403)
            return

        await websocket.accept()

        case_connections = chat_ws_connections.setdefault(case_id, {})
        case_connections[user.user_id] = websocket

        # Broadcast user joined
        await broadcast_chat_event(case_id, "user_joined", {
            "user_id": user.user_id,
            "name": user.name,
            "online_users": list(case_connections.keys())
        })

        while True:
            raw = await websocket.receive_text()
            if raw == "ping":
                await websocket.send_json({"type": "pong"})
                continue

            try:
                data = json.loads(raw)
            except json.JSONDecodeError:
                continue

            if data.get("type") == "typing":
                await broadcast_chat_event(case_id, "typing", {
                    "user_id": user.user_id,
                    "name": user.name,
                    "is_typing": data.get("is_typing", False)
                })

    except WebSocketDisconnect:
        pass
    except Exception:
        pass
    finally:
        conns = chat_ws_connections.get(case_id, {})
        for uid, ws in list(conns.items()):
            if ws is websocket:
                conns.pop(uid, None)
                break
        if case_id in chat_ws_connections:
            remaining = chat_ws_connections.get(case_id, {})
            if remaining:
                await broadcast_chat_event(case_id, "user_left", {
                    "user_id": user_doc.get("user_id", "") if user_doc else "",
                    "online_users": list(remaining.keys())
                })
            else:
                chat_ws_connections.pop(case_id, None)
