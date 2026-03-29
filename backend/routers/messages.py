"""
Criminal Appeal AI - Messages & Chat Router
Extracted from server.py monolith.
"""
from fastapi import APIRouter, HTTPException, Request, WebSocket, WebSocketDisconnect
from typing import Dict
from datetime import datetime, timezone
import uuid
import json
import logging

from config import db
from auth_utils import get_current_user, get_user_from_session_token

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api", tags=["messages"])

chat_ws_connections: Dict[str, Dict[str, WebSocket]] = {}


@router.get("/cases/{case_id}/messages")
async def get_case_messages(case_id: str, request: Request):
    """Get all messages for a case."""
    user = await get_current_user(request)
    case = await db.cases.find_one({"case_id": case_id, "user_id": user.user_id})
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
    messages = await db.case_messages.find(
        {"case_id": case_id}, {"_id": 0}
    ).sort("created_at", 1).to_list(500)
    return messages


@router.post("/cases/{case_id}/messages")
async def create_case_message(case_id: str, request: Request):
    """Create a new chat message for a case."""
    user = await get_current_user(request)
    body = await request.json()
    case = await db.cases.find_one({"case_id": case_id, "user_id": user.user_id})
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
    content = body.get("content", "").strip()
    if not content:
        raise HTTPException(status_code=400, detail="Message content required")
    message = {
        "message_id": f"msg_{uuid.uuid4().hex[:12]}",
        "case_id": case_id,
        "user_id": user.user_id,
        "user_name": user.name or user.email.split("@")[0],
        "content": content,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    await db.case_messages.insert_one(message)
    message.pop("_id", None)
    if case_id in chat_ws_connections:
        payload = json.dumps({"type": "new_message", "payload": message})
        for uid, ws in list(chat_ws_connections[case_id].items()):
            if uid != user.user_id:
                try:
                    await ws.send_text(payload)
                except Exception:
                    del chat_ws_connections[case_id][uid]
    return message


@router.websocket("/cases/{case_id}/chat/ws")
async def case_chat_ws(websocket: WebSocket, case_id: str):
    """Real-time chat WebSocket for a case."""
    session_token = websocket.query_params.get("session_token") or websocket.cookies.get("session_token")
    try:
        user = await get_user_from_session_token(session_token)
    except Exception:
        await websocket.close(code=4401)
        return
    case = await db.cases.find_one({"case_id": case_id, "user_id": user.user_id})
    if not case:
        await websocket.close(code=4404)
        return
    await websocket.accept()
    if case_id not in chat_ws_connections:
        chat_ws_connections[case_id] = {}
    chat_ws_connections[case_id][user.user_id] = websocket
    try:
        while True:
            raw = await websocket.receive_text()
            data = json.loads(raw)
            if data.get("type") == "typing":
                broadcast = json.dumps({
                    "type": "typing",
                    "payload": {
                        "user_id": user.user_id,
                        "name": user.name or user.email.split("@")[0],
                        "is_typing": data.get("is_typing", False)
                    }
                })
                for uid, ws in list(chat_ws_connections.get(case_id, {}).items()):
                    if uid != user.user_id:
                        try:
                            await ws.send_text(broadcast)
                        except Exception:
                            pass
    except WebSocketDisconnect:
        pass
    except Exception:
        pass
    finally:
        if case_id in chat_ws_connections:
            chat_ws_connections[case_id].pop(user.user_id, None)
            if not chat_ws_connections[case_id]:
                del chat_ws_connections[case_id]
