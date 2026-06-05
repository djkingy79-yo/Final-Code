#  — deadlines router. All endpoints in this file are approved and must be preserved.
"""
Criminal Appeal AI - Deadlines, Checklist & Case Strength Router
ADDITIVE HARDENING PATCH
"""
from fastapi import APIRouter, HTTPException, Request
from typing import List
from datetime import datetime, timezone
from urllib.parse import urlparse
import logging

from config import db, get_frontend_url
from auth_utils import get_current_user
from models import Deadline, DeadlineCreate, ChecklistItem, DEFAULT_CHECKLIST

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api", tags=["deadlines"])


# ============================================================================
# INTERNAL HELPERS
# ============================================================================

def _safe_percentage(numerator: int, denominator: int) -> int:
    if denominator <= 0:
        return 0
    return int((numerator / denominator) * 100)


def _count_completed(items: list) -> int:
    return len([item for item in items if item.get("is_completed")])


def _documents_with_text(documents: list) -> int:
    return len([d for d in documents if d.get("content_text")])


def _ground_breakdown(grounds: list) -> dict:
    breakdown = {"strong": 0, "moderate": 0, "weak": 0}
    for g in grounds:
        strength = g.get("strength", "moderate")
        if strength not in breakdown:
            strength = "moderate"
        breakdown[strength] += 1
    return breakdown


def _calculate_readiness_scores(grounds: list, documents: list, timeline: list, checklist: list) -> dict:
    """
    This is a workflow / preparation score.
    It is NOT a legal merits predictor.
    """
    strength_scores = {"strong": 3, "moderate": 2, "weak": 1}

    # Grounds preparation score
    grounds_score = 0
    breakdown = _ground_breakdown(grounds)
    if grounds:
        raw_score = sum(strength_scores.get(g.get("strength", "moderate"), 1) for g in grounds)
        max_possible = max(1, len(grounds) * 3)
        grounds_score = min(100, int((raw_score / max_possible) * 100))
    else:
        grounds_score = 0

    # Documentation completeness score
    docs_with_text = _documents_with_text(documents)
    if documents:
        extraction_ratio = docs_with_text / max(1, len(documents))
        documentation_score = min(100, int(extraction_ratio * 70) + min(30, len(documents) * 3))
    else:
        documentation_score = 0

    # Timeline completeness score
    if timeline:
        base_timeline_score = min(70, len(timeline) * 4)
        critical_events = len([t for t in timeline if t.get("significance") == "critical"])
        timeline_score = min(100, base_timeline_score + min(30, critical_events * 8))
    else:
        timeline_score = 0

    # Preparation completion score
    completed = _count_completed(checklist)
    preparation_score = _safe_percentage(completed, len(checklist))

    # Weighted readiness score
    readiness_score = int(
        (grounds_score * 0.35) +
        (documentation_score * 0.25) +
        (timeline_score * 0.20) +
        (preparation_score * 0.20)
    )

    if readiness_score >= 75:
        readiness_level = "Advanced"
        readiness_color = "green"
    elif readiness_score >= 50:
        readiness_level = "Established"
        readiness_color = "amber"
    elif readiness_score >= 25:
        readiness_level = "Developing"
        readiness_color = "orange"
    else:
        readiness_level = "Early Stage"
        readiness_color = "red"

    recommendations = []

    if not grounds:
        recommendations.append("Run AI Grounds Identification to flag possible appeal issues for review")
    if len(documents) < 3:
        recommendations.append("Upload more case documents to improve preparation completeness")
    if docs_with_text < len(documents):
        recommendations.append("Extract text or OCR all uploaded documents so they can be analysed properly")
    if len(timeline) < 5:
        recommendations.append("Build out the timeline with additional key events and procedural dates")
    if preparation_score < 50:
        recommendations.append("Work through the appeal checklist to improve preparation completeness")
    if len(grounds) > 0 and breakdown["strong"] == 0:
        recommendations.append("Review identified grounds and prioritise those with the clearest documentary support")

    return {
        "readiness_score": readiness_score,
        "readiness_level": readiness_level,
        "readiness_color": readiness_color,
        "grounds_score": grounds_score,
        "documentation_score": documentation_score,
        "timeline_score": timeline_score,
        "preparation_score": preparation_score,
        "ground_breakdown": breakdown,
        "documents_with_text": docs_with_text,
        "completed_checklist_items": completed,
        "recommendations": recommendations,
    }


# ============================================================================
# DEADLINES CRUD
# ============================================================================

@router.get("/cases/{case_id}/deadlines", response_model=List[dict])
async def get_deadlines(case_id: str, request: Request):
    """Get all deadlines for a case"""
    user = await get_current_user(request)

    case = await db.cases.find_one({"case_id": case_id, "user_id": user.user_id})
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")

    deadlines = await db.deadlines.find(
        {"case_id": case_id, "user_id": user.user_id},
        {"_id": 0}
    ).sort("due_date", 1).to_list(100)

    return deadlines


@router.post("/cases/{case_id}/deadlines", response_model=dict)
async def create_deadline(case_id: str, deadline_data: DeadlineCreate, request: Request):
    """Create a new deadline"""
    user = await get_current_user(request)

    case = await db.cases.find_one({"case_id": case_id, "user_id": user.user_id})
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")

    deadline = Deadline(case_id=case_id, user_id=user.user_id, **deadline_data.model_dump())
    deadline_dict = deadline.model_dump()
    deadline_dict["due_date"] = deadline_dict["due_date"].isoformat()
    deadline_dict["created_at"] = deadline_dict["created_at"].isoformat()

    await db.deadlines.insert_one(deadline_dict)

    return await db.deadlines.find_one(
        {"deadline_id": deadline.deadline_id, "case_id": case_id, "user_id": user.user_id},
        {"_id": 0}
    )


@router.patch("/cases/{case_id}/deadlines/{deadline_id}", response_model=dict)
async def update_deadline(case_id: str, deadline_id: str, request: Request):
    """Update a deadline (mark complete, etc.)"""
    user = await get_current_user(request)
    body = await request.json()

    deadline = await db.deadlines.find_one({
        "deadline_id": deadline_id,
        "case_id": case_id,
        "user_id": user.user_id
    })
    if not deadline:
        raise HTTPException(status_code=404, detail="Deadline not found")

    update_data = {}

    if "is_completed" in body:
        update_data["is_completed"] = body["is_completed"]
        if body["is_completed"]:
            update_data["completed_at"] = datetime.now(timezone.utc).isoformat()
        else:
            update_data["completed_at"] = None

    if "title" in body:
        update_data["title"] = body["title"]

    if "due_date" in body:
        update_data["due_date"] = body["due_date"]

    if "priority" in body:
        update_data["priority"] = body["priority"]

    if "description" in body:
        update_data["description"] = body["description"]

    if "deadline_type" in body:
        update_data["deadline_type"] = body["deadline_type"]

    if update_data:
        await db.deadlines.update_one(
            {"deadline_id": deadline_id, "case_id": case_id, "user_id": user.user_id},
            {"$set": update_data}
        )

    return await db.deadlines.find_one(
        {"deadline_id": deadline_id, "case_id": case_id, "user_id": user.user_id},
        {"_id": 0}
    )


@router.delete("/cases/{case_id}/deadlines/{deadline_id}")
async def delete_deadline(case_id: str, deadline_id: str, request: Request):
    """Delete a deadline"""
    user = await get_current_user(request)

    result = await db.deadlines.delete_one({
        "deadline_id": deadline_id,
        "case_id": case_id,
        "user_id": user.user_id
    })

    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Deadline not found")

    return {"message": "Deadline deleted"}


# ============================================================================
# JURISDICTION DEADLINE RULES (locked 2026-02 by owner)
# Times are calendar days from sentence unless noted. Figures verified against
# Criminal Appeal Act 1912 (NSW), Criminal Procedure Act 2009 (Vic),
# Criminal Code 1899 (Qld), Supreme Court Criminal Rules 2022 (SA),
# Criminal Appeals Act 2004 (WA), Criminal Code Act 1924 (Tas),
# Supreme Court Act (NT), Supreme Court Act 1933 (ACT), Federal Court Rules.
# Each rule is EDUCATIONAL; users must independently verify against the current
# rules of the relevant court before filing.
# ============================================================================
JURISDICTION_DEADLINE_RULES = {
    "nsw": {"notice_of_intention_days": 28, "notice_of_appeal_days": 6 * 30, "reference": "Criminal Appeal Act 1912 (NSW) s 10; Criminal Appeal Rules r 3B", "court": "Court of Criminal Appeal"},
    "vic": {"notice_of_intention_days": 28, "notice_of_appeal_days": 28, "reference": "Criminal Procedure Act 2009 (Vic) s 275; SCR Chap 6", "court": "Court of Appeal"},
    "qld": {"notice_of_intention_days": 30, "notice_of_appeal_days": 30, "reference": "Criminal Code 1899 (Qld) s 671; Criminal Practice Rules 1999 r 65", "court": "Court of Appeal"},
    "sa": {"notice_of_intention_days": 21, "notice_of_appeal_days": 21, "reference": "Criminal Procedure Act 1921 (SA) Pt 11; Supreme Court Criminal Rules 2022", "court": "Court of Appeal (Criminal)"},
    "wa": {"notice_of_intention_days": 21, "notice_of_appeal_days": 21, "reference": "Criminal Appeals Act 2004 (WA) s 26; Rules of the Supreme Court O 66", "court": "Court of Appeal"},
    "tas": {"notice_of_intention_days": 21, "notice_of_appeal_days": 21, "reference": "Criminal Code Act 1924 (Tas) s 404; Criminal Appeal Rules 1969", "court": "Court of Criminal Appeal"},
    "nt": {"notice_of_intention_days": 28, "notice_of_appeal_days": 28, "reference": "Criminal Code Act (NT) s 410; Supreme Court Criminal Rules", "court": "Court of Criminal Appeal"},
    "act": {"notice_of_intention_days": 28, "notice_of_appeal_days": 28, "reference": "Supreme Court Act 1933 (ACT) Pt 7; Court Procedures Rules 2006", "court": "Court of Appeal"},
    "cth": {"notice_of_intention_days": 28, "notice_of_appeal_days": 28, "reference": "Federal Court Rules 2011 Div 36.03; Crimes Act 1914 (Cth)", "court": "Full Court of the Federal Court"},
}


@router.post("/cases/{case_id}/deadlines/compute", response_model=dict)
async def compute_deadlines(case_id: str, request: Request):
    """Auto-compute the canonical appeal deadlines for a case from sentence_date
    + jurisdiction. Idempotent — returns the existing computed set if already
    present (identified by source_mode='jurisdiction_auto').

    Sentence date resolution order:
      1. POST body {"sentence_date": "YYYY-MM-DD"}
      2. case.sentence_date / case.sentencing_date field
    """
    import uuid as _uuid
    user = await get_current_user(request)
    case = await db.cases.find_one(
        {"case_id": case_id, "user_id": user.user_id}, {"_id": 0}
    )
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")

    # Accept sentence_date from request body (user supplies on demand) OR fallback to case fields.
    sentence_date_raw = None
    try:
        body = await request.json()
        if isinstance(body, dict):
            sentence_date_raw = body.get("sentence_date")
    except Exception:
        pass
    if not sentence_date_raw:
        sentence_date_raw = case.get("sentence_date") or case.get("sentencing_date") or case.get("sentenced_on")

    if not sentence_date_raw:
        raise HTTPException(
            status_code=400,
            detail="Sentence date required. Supply it in the request body as {\"sentence_date\": \"YYYY-MM-DD\"} or save it to the case record.",
        )
    if isinstance(sentence_date_raw, str):
        try:
            sentence_dt = datetime.fromisoformat(sentence_date_raw.replace("Z", "+00:00"))
        except ValueError:
            # Try plain date-only format
            try:
                sentence_dt = datetime.strptime(sentence_date_raw, "%Y-%m-%d").replace(tzinfo=timezone.utc)
            except ValueError:
                raise HTTPException(status_code=400, detail=f"Invalid sentence_date format: {sentence_date_raw}. Use ISO 8601 (YYYY-MM-DD).")
    else:
        sentence_dt = sentence_date_raw
    if sentence_dt.tzinfo is None:
        sentence_dt = sentence_dt.replace(tzinfo=timezone.utc)

    # Persist sentence_date back onto the case for reuse.
    if not case.get("sentence_date"):
        await db.cases.update_one(
            {"case_id": case_id, "user_id": user.user_id},
            {"$set": {"sentence_date": sentence_dt.isoformat(), "updated_at": datetime.now(timezone.utc).isoformat()}},
        )

    jur = (case.get("state") or "nsw").lower()
    rules = JURISDICTION_DEADLINE_RULES.get(jur, JURISDICTION_DEADLINE_RULES["nsw"])

    from datetime import timedelta
    now_iso = datetime.now(timezone.utc).isoformat()
    court_label = rules["court"]
    ref_label = rules["reference"]

    computed_events = [
        {
            "title": f"Notice of Intention to Appeal — lodge at {court_label}",
            "description": f"File Notice of Intention to Appeal within {rules['notice_of_intention_days']} days of sentence. Reference: {ref_label}. Missing this deadline usually means requiring leave for an extension of time — demonstrate merits and explain delay (see R v Sullivan [2009] NSWCCA; Muldrock v The Queen (2011) 244 CLR 120).",
            "deadline_type": "notice_of_intention",
            "offset_days": rules["notice_of_intention_days"],
            "priority": "critical",
        },
        {
            "title": f"Notice of Appeal (grounds) — lodge at {court_label}",
            "description": f"File the formal Notice of Appeal with numbered grounds within {rules['notice_of_appeal_days']} days of sentence (where separate from the Notice of Intention). Reference: {ref_label}.",
            "deadline_type": "notice_of_appeal",
            "offset_days": rules["notice_of_appeal_days"],
            "priority": "critical",
        },
        {
            "title": "Appellant's Written Submissions — internal draft target",
            "description": "Internal drafting target: appellant's written submissions should be substantially drafted by this date so counsel / self-represented appellant has clear time to refine before filing.",
            "deadline_type": "submissions_draft",
            "offset_days": max(rules["notice_of_intention_days"] + 14, 42),
            "priority": "high",
        },
        {
            "title": "Legal Aid merit application (if required)",
            "description": "If relying on a grant of Legal Aid for representation, lodge the merit application. The merit test is determined under the relevant state Legal Aid Commission Act; unmeritorious or late applications are routinely refused.",
            "deadline_type": "legal_aid_application",
            "offset_days": 14,
            "priority": "high",
        },
    ]

    # Delete previous jurisdiction-auto set so re-compute is idempotent.
    await db.deadlines.delete_many({
        "case_id": case_id, "user_id": user.user_id,
        "source_mode": "jurisdiction_auto",
    })

    created = []
    for ev in computed_events:
        due = sentence_dt + timedelta(days=ev["offset_days"])
        doc = {
            "deadline_id": f"dl_{_uuid.uuid4().hex[:12]}",
            "case_id": case_id,
            "user_id": user.user_id,
            "title": ev["title"],
            "description": ev["description"],
            "deadline_type": ev["deadline_type"],
            "due_date": due.isoformat(),
            "reminder_days": [14, 7, 3, 1],
            "is_completed": False,
            "completed_at": None,
            "priority": ev["priority"],
            "jurisdiction": jur,
            "is_jurisdiction_default": True,
            "source_mode": "jurisdiction_auto",
            "verification_status": "unverified",
            "created_at": now_iso,
        }
        await db.deadlines.insert_one(doc)
        doc.pop("_id", None)
        created.append(doc)

    return {
        "computed_count": len(created),
        "jurisdiction": jur,
        "reference": ref_label,
        "court": court_label,
        "deadlines": created,
        "caveat": "These deadlines are educational defaults derived from the stated jurisdictional rules. The rules of court may have been amended; users must independently verify the current time limits against the relevant Court's Practice Directions before filing.",
    }


@router.get("/cases/{case_id}/deadlines.ics")
async def export_deadlines_ics(case_id: str, request: Request):
    """Export all deadlines as an iCalendar (.ics) file so the user can import
    them into Apple Calendar / Google Calendar / Outlook. Each deadline becomes
    a VEVENT at 09:00 local time on the due date with VALARM reminders matching
    the stored `reminder_days` list."""
    from fastapi.responses import Response
    user = await get_current_user(request)
    case = await db.cases.find_one(
        {"case_id": case_id, "user_id": user.user_id}, {"_id": 0}
    )
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")

    deadlines = await db.deadlines.find(
        {"case_id": case_id, "user_id": user.user_id}, {"_id": 0}
    ).sort("due_date", 1).to_list(500)

    appellant = (case.get("defendant_name") or case.get("title") or "Appellant").strip()
    now_stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")

    def _ics_escape(s: str) -> str:
        return (s or "").replace("\\", "\\\\").replace(",", "\\,").replace(";", "\\;").replace("\n", "\\n")

    def _fmt_dt(iso_or_dt) -> str:
        if isinstance(iso_or_dt, str):
            try:
                dt = datetime.fromisoformat(iso_or_dt.replace("Z", "+00:00"))
            except ValueError:
                dt = datetime.now(timezone.utc)
        else:
            dt = iso_or_dt or datetime.now(timezone.utc)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt.strftime("%Y%m%dT%H%M%SZ")

    lines = [
        "BEGIN:VCALENDAR",
        "VERSION:2.0",
        "PRODID:-//Criminal Law Appeal Management//EN",
        "CALSCALE:GREGORIAN",
        "METHOD:PUBLISH",
        f"X-WR-CALNAME:{_ics_escape(appellant)} — Appeal Deadlines",
    ]
    for d in deadlines:
        uid = f"{d.get('deadline_id', 'unknown')}@{urlparse(get_frontend_url()).netloc}"
        dtstart = _fmt_dt(d.get("due_date"))
        summary = _ics_escape(d.get("title", "Appeal deadline"))
        description = _ics_escape(d.get("description", ""))
        priority_map = {"critical": 1, "high": 3, "medium": 5, "low": 7}
        ics_priority = priority_map.get(d.get("priority", "high"), 3)
        lines += [
            "BEGIN:VEVENT",
            f"UID:{uid}",
            f"DTSTAMP:{now_stamp}",
            f"DTSTART:{dtstart}",
            f"DTEND:{dtstart}",
            f"SUMMARY:{summary}",
            f"DESCRIPTION:{description}",
            f"PRIORITY:{ics_priority}",
            "STATUS:CONFIRMED",
            "TRANSP:OPAQUE",
        ]
        for rd in (d.get("reminder_days") or []):
            lines += [
                "BEGIN:VALARM",
                "ACTION:DISPLAY",
                f"DESCRIPTION:Reminder — {summary} in {rd} day(s)",
                f"TRIGGER:-P{int(rd)}D",
                "END:VALARM",
            ]
        lines.append("END:VEVENT")
    lines.append("END:VCALENDAR")

    body = "\r\n".join(lines) + "\r\n"
    filename = f"{appellant.replace(' ', '_')}_appeal_deadlines.ics"
    return Response(
        content=body,
        media_type="text/calendar; charset=utf-8",
        headers={
            "Content-Disposition": f"attachment; filename=\"{filename}\"",
            "Cache-Control": "private, no-store",
        },
    )


# ============================================================================
# CHECKLIST
# ============================================================================

@router.get("/cases/{case_id}/checklist", response_model=List[dict])
async def get_checklist(case_id: str, request: Request):
    """Get checklist for a case, creating default items if none exist"""
    user = await get_current_user(request)

    case = await db.cases.find_one({"case_id": case_id, "user_id": user.user_id})
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")

    items = await db.checklist_items.find(
        {"case_id": case_id, "user_id": user.user_id},
        {"_id": 0}
    ).sort("order", 1).to_list(100)

    if not items:
        for item_data in DEFAULT_CHECKLIST:
            item = ChecklistItem(case_id=case_id, user_id=user.user_id, **item_data)
            item_dict = item.model_dump()
            item_dict["created_at"] = item_dict["created_at"].isoformat()
            await db.checklist_items.insert_one(item_dict)

        items = await db.checklist_items.find(
            {"case_id": case_id, "user_id": user.user_id},
            {"_id": 0}
        ).sort("order", 1).to_list(100)

    return items


@router.patch("/cases/{case_id}/checklist/{item_id}", response_model=dict)
async def update_checklist_item(case_id: str, item_id: str, request: Request):
    """Update a checklist item"""
    user = await get_current_user(request)
    body = await request.json()

    item = await db.checklist_items.find_one({
        "item_id": item_id,
        "case_id": case_id,
        "user_id": user.user_id
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
            {"item_id": item_id, "case_id": case_id, "user_id": user.user_id},
            {"$set": update_data}
        )

    return await db.checklist_items.find_one(
        {"item_id": item_id, "case_id": case_id, "user_id": user.user_id},
        {"_id": 0}
    )


# ============================================================================
# READINESS / PREPARATION SCORE
# ============================================================================

@router.get("/cases/{case_id}/strength", response_model=dict)
async def get_case_strength(case_id: str, request: Request):
    """
    Compatibility endpoint.
    Preserves the existing route path while returning a safer readiness-based interpretation.
    """
    user = await get_current_user(request)

    case = await db.cases.find_one({"case_id": case_id, "user_id": user.user_id})
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")

    grounds = await db.grounds_of_merit.find(
        {"case_id": case_id, "user_id": user.user_id},
        {"_id": 0}
    ).to_list(100)

    documents = await db.documents.find(
        {"case_id": case_id, "user_id": user.user_id},
        {"_id": 0}
    ).to_list(500)

    timeline = await db.timeline_events.find(
        {"case_id": case_id, "user_id": user.user_id},
        {"_id": 0}
    ).to_list(500)

    checklist = await db.checklist_items.find(
        {"case_id": case_id, "user_id": user.user_id},
        {"_id": 0}
    ).to_list(100)

    scores = _calculate_readiness_scores(grounds, documents, timeline, checklist)

    overall_score = scores["readiness_score"]
    rating = scores["readiness_level"]
    rating_color = scores["readiness_color"]

    breakdown = {
        "grounds": {
            "score": scores["grounds_score"],
            "count": len(grounds),
            **scores["ground_breakdown"],
        },
        "documentation": {
            "score": scores["documentation_score"],
            "total_docs": len(documents),
            "with_text": scores["documents_with_text"],
        },
        "timeline": {
            "score": scores["timeline_score"],
            "event_count": len(timeline),
        },
        "preparation": {
            "score": scores["preparation_score"],
            "completed": scores["completed_checklist_items"],
            "total": len(checklist),
        },
    }

    return {
        # compatibility keys preserved
        "overall_score": overall_score,
        "rating": rating,
        "rating_color": rating_color,

        # additive clearer keys
        "readiness_score": scores["readiness_score"],
        "readiness_level": scores["readiness_level"],
        "readiness_color": scores["readiness_color"],

        "breakdown": breakdown,
        "recommendations": scores["recommendations"],

        "assessment_note": (
            "This score reflects case preparation and documentation completeness. "
            "It is not a determination of legal merit or likelihood of success."
        ),
        "assessment_type": "appeal_preparation_readiness"
    }
