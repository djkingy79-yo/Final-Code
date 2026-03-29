"""
Criminal Appeal AI - Notes Real-time Collaboration Helpers
WebSocket connection tracking and broadcasting for notes.
"""
from typing import Dict, List
from fastapi import WebSocket
from config import db

notes_ws_connections: Dict[str, Dict[str, WebSocket]] = {}


async def get_presence_snapshot(case_id: str) -> List[dict]:
    case_connections = notes_ws_connections.get(case_id, {})
    if not case_connections:
        return []

    users = await db.users.find(
        {"user_id": {"$in": list(case_connections.keys())}},
        {"_id": 0, "user_id": 1, "name": 1, "email": 1}
    ).to_list(100)
    return users


async def broadcast_notes_event(case_id: str, event_type: str, payload: dict):
    case_connections = notes_ws_connections.get(case_id, {})
    if not case_connections:
        return

    stale_user_ids = []
    message = {"type": event_type, "payload": payload}

    for user_id, ws in case_connections.items():
        try:
            await ws.send_json(message)
        except Exception:
            stale_user_ids.append(user_id)

    for user_id in stale_user_ids:
        case_connections.pop(user_id, None)
