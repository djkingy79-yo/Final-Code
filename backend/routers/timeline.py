# DO NOT UNDO — timeline router. All endpoints in this file are approved and must be preserved.
"""
Criminal Appeal AI - Timeline Router
ADDITIVE HARDENING PATCH
"""
from fastapi import APIRouter, HTTPException, Request, Response
from datetime import datetime, timezone
import uuid
import json
import logging
import re

from config import db
from auth_utils import get_current_user
from models import TimelineEvent, TimelineEventCreate
from services.document_helpers import build_document_context
from services.llm_service import call_llm_with_fallback, call_llm_for_json
from services.offence_helpers import get_offence_context

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api", tags=["timeline"])


# ============================================================================
# INTERNAL HELPERS
# ============================================================================

ALLOWED_SIGNIFICANCE = {"low", "normal", "important", "critical"}
ALLOWED_PERSPECTIVE = {"neutral", "defence", "prosecution", "court"}


def _safe_str(value, default=""):
    if value is None:
        return default
    return str(value).strip()


def _normalise_significance(value: str) -> str:
    v = _safe_str(value, "normal").lower()
    return v if v in ALLOWED_SIGNIFICANCE else "normal"


def _normalise_perspective(value: str) -> str:
    v = _safe_str(value, "neutral").lower()
    return v if v in ALLOWED_PERSPECTIVE else "neutral"


def _normalise_date_string(value):
    if not value:
        return None

    text = str(value).strip()

    # YYYY-MM-DD
    if re.fullmatch(r"\d{4}-\d{2}-\d{2}", text):
        return f"{text}T00:00:00+00:00"

    try:
        dt = datetime.fromisoformat(text.replace("Z", "+00:00"))
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt.isoformat()
    except Exception:
        pass

    # Try common date formats
    for fmt in ['%Y-%m-%d', '%Y-%m', '%Y', '%d/%m/%Y', '%d-%m-%Y']:
        try:
            dt = datetime.strptime(text, fmt)
            return dt.replace(tzinfo=timezone.utc).isoformat()
        except ValueError:
            continue

    # Try to extract a year
    year_match = re.search(r'(19|20)\d{2}', text)
    if year_match:
        try:
            dt = datetime.strptime(year_match.group(), '%Y')
            return dt.replace(tzinfo=timezone.utc).isoformat()
        except ValueError:
            pass

    return None


def _validate_timeline_payload(payload: dict) -> bool:
    if not isinstance(payload, dict):
        return False

    events = payload.get("events")
    if not isinstance(events, list):
        return False

    for event in events:
        if not isinstance(event, dict):
            return False
        if not event.get("title"):
            return False
        if not event.get("event_date"):
            return False

    return True


def _timeline_event_dump(event: TimelineEvent) -> dict:
    dumped = event.model_dump()
    dumped["event_date"] = dumped["event_date"].isoformat()
    dumped["created_at"] = dumped["created_at"].isoformat()
    return dumped


# ============================================================================
# CRUD
# ============================================================================

@router.get("/cases/{case_id}/timeline", response_model=list[dict])
async def get_timeline(case_id: str, request: Request):
    """Get all timeline events for a case"""
    user = await get_current_user(request)

    case = await db.cases.find_one({"case_id": case_id, "user_id": user.user_id})
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")

    events = await db.timeline_events.find(
        {"case_id": case_id, "user_id": user.user_id},
        {"_id": 0}
    ).sort("event_date", 1).to_list(500)

    return events


@router.post("/cases/{case_id}/timeline", response_model=dict)
async def create_timeline_event(case_id: str, event_data: TimelineEventCreate, request: Request):
    """Create a manual timeline event"""
    user = await get_current_user(request)

    case = await db.cases.find_one({"case_id": case_id, "user_id": user.user_id})
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")

    event = TimelineEvent(
        case_id=case_id,
        user_id=user.user_id,
        title=event_data.title,
        description=event_data.description,
        event_date=event_data.event_date,
        event_type=event_data.event_type,
        event_category=event_data.event_category,
        linked_documents=event_data.linked_documents,
        participants=event_data.participants,
        significance=_normalise_significance(event_data.significance),
        source_citation=event_data.source_citation,
        perspective=_normalise_perspective(event_data.perspective),
        is_contested=event_data.is_contested,
        contested_details=event_data.contested_details,
        related_grounds=event_data.related_grounds,
        inconsistency_notes=event_data.inconsistency_notes,
        source_mode="manual",
        verification_status="unverified",
    )

    event_dict = _timeline_event_dump(event)
    await db.timeline_events.insert_one(event_dict)

    await db.cases.update_one(
        {"case_id": case_id, "user_id": user.user_id},
        {"$set": {"updated_at": datetime.now(timezone.utc).isoformat()}}
    )

    return await db.timeline_events.find_one(
        {"event_id": event.event_id, "case_id": case_id, "user_id": user.user_id},
        {"_id": 0}
    )


@router.put("/cases/{case_id}/timeline/{event_id}", response_model=dict)
async def update_timeline_event_put(case_id: str, event_id: str, event_data: TimelineEventCreate, request: Request):
    """Update a timeline event (PUT - full replace)"""
    user = await get_current_user(request)
    update_data = event_data.model_dump()
    update_data["event_date"] = update_data["event_date"].isoformat()
    result = await db.timeline_events.update_one(
        {"event_id": event_id, "case_id": case_id, "user_id": user.user_id}, {"$set": update_data}
    )
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="Event not found")
    return await db.timeline_events.find_one({"event_id": event_id}, {"_id": 0})


@router.patch("/cases/{case_id}/timeline/{event_id}", response_model=dict)
async def update_timeline_event(case_id: str, event_id: str, request: Request):
    """Update a timeline event (PATCH - partial update)"""
    user = await get_current_user(request)
    body = await request.json()

    event = await db.timeline_events.find_one({
        "event_id": event_id,
        "case_id": case_id,
        "user_id": user.user_id
    })
    if not event:
        raise HTTPException(status_code=404, detail="Timeline event not found")

    update_data = {}

    allowed_fields = {
        "title", "description", "event_type", "event_category", "linked_documents",
        "participants", "source_citation", "is_contested", "contested_details",
        "related_grounds", "inconsistency_notes"
    }
    for field in allowed_fields:
        if field in body:
            update_data[field] = body[field]

    if "event_date" in body:
        normalised = _normalise_date_string(body["event_date"])
        if not normalised:
            raise HTTPException(status_code=400, detail="Invalid event_date")
        update_data["event_date"] = normalised

    if "significance" in body:
        update_data["significance"] = _normalise_significance(body["significance"])

    if "perspective" in body:
        update_data["perspective"] = _normalise_perspective(body["perspective"])

    if update_data:
        await db.timeline_events.update_one(
            {"event_id": event_id, "case_id": case_id, "user_id": user.user_id},
            {"$set": update_data}
        )

    return await db.timeline_events.find_one(
        {"event_id": event_id, "case_id": case_id, "user_id": user.user_id},
        {"_id": 0}
    )


@router.delete("/cases/{case_id}/timeline/{event_id}")
async def delete_timeline_event(case_id: str, event_id: str, request: Request):
    """Delete a timeline event"""
    user = await get_current_user(request)

    result = await db.timeline_events.delete_one({
        "event_id": event_id,
        "case_id": case_id,
        "user_id": user.user_id
    })

    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Timeline event not found")

    return {"message": "Timeline event deleted"}


# ============================================================================
# AI TIMELINE GENERATION (HARDENED - JSON-SAFE)
# ============================================================================

@router.post("/cases/{case_id}/timeline/auto-generate", response_model=dict)
async def auto_generate_timeline(case_id: str, request: Request):
    """
    AI generates timeline events from uploaded documents.
    Existing timeline events are preserved; duplicates are skipped heuristically.
    """
    user = await get_current_user(request)

    case = await db.cases.find_one({"case_id": case_id, "user_id": user.user_id}, {"_id": 0})
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")

    documents = await db.documents.find(
        {"case_id": case_id, "user_id": user.user_id},
        {"_id": 0, "file_data": 0}
    ).to_list(500)

    existing_events = await db.timeline_events.find(
        {"case_id": case_id, "user_id": user.user_id},
        {"_id": 0}
    ).sort("event_date", 1).to_list(500)

    if not documents:
        raise HTTPException(status_code=400, detail="No documents uploaded for this case")

    documents_with_text = [doc for doc in documents if doc.get("content_text")]
    if not documents_with_text:
        raise HTTPException(status_code=400, detail="No documents with extracted text found. Please extract text before generating a timeline.")

    offence_context = get_offence_context(case)

    doc_context = build_document_context(
        documents,
        per_doc_char_limit=2500,
        total_char_budget=22000,
        include_description=True,
        content_heading="CONTENT"
    )

    existing_summary = ""
    for event in existing_events[:120]:
        existing_summary += (
            f"- {event.get('event_date', 'Unknown date')} | "
            f"{event.get('title', 'Untitled')} | "
            f"{event.get('event_type', 'event')}\n"
        )

    system_prompt = f"""You are extracting a chronology for a criminal appeal matter.

Use cautious evidentiary discipline:
- extract only events actually supported by the provided documents
- do not invent dates
- if a date is approximate or partial, prefer the best supported date form
- distinguish clearly between factual events and procedural events
- return machine-parseable JSON only

{offence_context}
"""

    user_prompt = f"""Analyse the case documents below and extract a chronology.

CASE:
- Title: {case.get('title', 'Unknown')}
- Defendant: {case.get('defendant_name', 'Unknown')}
- Court: {case.get('court', 'N/A')}
- State: {case.get('state', 'nsw')}
- Offence Category: {case.get('offence_category', 'unknown')}
- Offence Type: {case.get('offence_type', 'N/A')}

DOCUMENTS:
{doc_context["text"]}

EXISTING TIMELINE EVENTS (DO NOT DUPLICATE THESE):
{existing_summary if existing_summary else "[No existing events]"}

Return ONLY valid JSON in this format:
{{
  "events": [
    {{
      "title": "Short event title",
      "description": "Source-grounded description of what happened",
      "event_date": "ISO date or datetime",
      "event_type": "incident|investigation|arrest|charge|hearing|application|ruling|trial|verdict|sentence|appeal|court_hearing|evidence|witness|legal_filing|other",
      "event_category": "factual|procedural|evidentiary|medical|general|other",
      "linked_documents": [],
      "significance": "low|normal|important|critical",
      "source_citation": "Filename or source note",
      "perspective": "neutral",
      "is_contested": false,
      "contested_details": "",
      "related_grounds": [],
      "inconsistency_notes": ""
    }}
  ]
}}

Rules:
- Prefer specific, document-supported dates
- Include major procedural events (application, ruling, sentence, etc.)
- Include major factual events only if document-supported
- Do not duplicate the existing timeline
"""

    try:
        parsed = await call_llm_for_json(
            system_prompt,
            user_prompt,
            session_id=f"timeline_{case_id}_{uuid.uuid4().hex[:8]}",
            task_type="timeline_extraction",
            validation_fn=_validate_timeline_payload,
        )
    except Exception as e:
        logger.error(f"Timeline auto-generation failed: {e}")
        raise HTTPException(status_code=500, detail=f"AI timeline generation failed: {str(e)}")

    generated_events = parsed.get("events", [])
    created_events = []
    skipped_duplicates = 0

    existing_fingerprints = set()
    existing_titles = []
    for event in existing_events:
        fingerprint = (
            _safe_str(event.get("title")).lower(),
            _safe_str(event.get("event_date"))[:10],
            _safe_str(event.get("event_type")).lower(),
        )
        existing_fingerprints.add(fingerprint)
        existing_titles.append(_safe_str(event.get("title")).lower())

    from fuzzywuzzy import fuzz as _fuzz

    for raw_event in generated_events:
        try:
            event_date_iso = _normalise_date_string(raw_event.get("event_date"))
            if not event_date_iso:
                continue

            fingerprint = (
                _safe_str(raw_event.get("title")).lower(),
                event_date_iso[:10],
                _safe_str(raw_event.get("event_type")).lower(),
            )

            if fingerprint in existing_fingerprints:
                skipped_duplicates += 1
                continue

            # DO_NOT_UNDO — Fuzzy title dedup for timeline events
            new_title = _safe_str(raw_event.get("title")).lower()
            if any(_fuzz.token_set_ratio(new_title, et) >= 65 for et in existing_titles):
                skipped_duplicates += 1
                continue

            dt = datetime.fromisoformat(event_date_iso.replace("Z", "+00:00"))
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=timezone.utc)

            event = TimelineEvent(
                case_id=case_id,
                user_id=user.user_id,
                title=_safe_str(raw_event.get("title"), "Untitled event"),
                description=_safe_str(raw_event.get("description")),
                event_date=dt,
                event_type=_safe_str(raw_event.get("event_type"), "event"),
                event_category=_safe_str(raw_event.get("event_category"), "general"),
                linked_documents=raw_event.get("linked_documents", []) or [],
                participants=raw_event.get("participants", []) or [],
                significance=_normalise_significance(raw_event.get("significance", "normal")),
                source_citation=_safe_str(raw_event.get("source_citation")),
                perspective=_normalise_perspective(raw_event.get("perspective", "neutral")),
                is_contested=bool(raw_event.get("is_contested", False)),
                contested_details=_safe_str(raw_event.get("contested_details")),
                related_grounds=raw_event.get("related_grounds", []) or [],
                inconsistency_notes=_safe_str(raw_event.get("inconsistency_notes")),
                source_mode="ai_generated",
                verification_status="unverified",
            )

            event_dict = _timeline_event_dump(event)
            await db.timeline_events.insert_one(event_dict)

            created = await db.timeline_events.find_one(
                {"event_id": event.event_id, "case_id": case_id, "user_id": user.user_id},
                {"_id": 0}
            )
            created_events.append(created)
            existing_fingerprints.add(fingerprint)
            existing_titles.append(new_title)

        except Exception as e:
            logger.warning(f"Skipping malformed generated timeline event: {e}")
            continue

    await db.cases.update_one(
        {"case_id": case_id, "user_id": user.user_id},
        {"$set": {"updated_at": datetime.now(timezone.utc).isoformat()}}
    )

    return {
        "message": (
            f"Successfully generated {len(created_events)} timeline events"
            + (f". Skipped {skipped_duplicates} duplicates." if skipped_duplicates else "")
        ),
        "created_count": len(created_events),
        "events_created": len(created_events),
        "skipped_duplicates": skipped_duplicates,
        "events": created_events,
        "assessment_note": (
            "These timeline events were AI-generated from uploaded case documents and should be reviewed "
            "against the source material before being relied on."
        )
    }


# ============================================================================
# TIMELINE ANALYSIS (PRESERVED FROM EXISTING CODEBASE)
# ============================================================================

@router.post("/cases/{case_id}/timeline/analyze", response_model=dict)
async def analyze_timeline(case_id: str, request: Request):
    """AI-powered timeline analysis to find gaps, inconsistencies, and insights"""
    user = await get_current_user(request)
    case = await db.cases.find_one({"case_id": case_id, "user_id": user.user_id})
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
    events = await db.timeline_events.find({"case_id": case_id, "user_id": user.user_id}, {"_id": 0}).sort("event_date", 1).to_list(500)
    if len(events) < 2:
        raise HTTPException(status_code=400, detail="Need at least 2 timeline events for analysis")
    grounds = await db.grounds_of_merit.find({"case_id": case_id, "user_id": user.user_id}, {"_id": 0}).to_list(100)
    system_prompt = """You are an expert criminal appeals analyst specialising in NSW and Australian federal law. Use Australian English spelling throughout.
Analyse this timeline of events and provide detailed insights for an appeal case.

Your analysis must include:
1. TIMELINE GAPS: Identify any suspicious gaps or missing periods that should have documentation
2. INCONSISTENCIES: Find contradictions between events or illogical sequences
3. PROSECUTION VS DEFENCE: Identify which events favour prosecution vs defence
4. CONTESTED FACTS: Flag events that appear disputed or have conflicting accounts
5. APPEAL RELEVANCE: Link events to potential grounds of appeal
6. KEY DATES: Highlight critical dates and any statute of limitation concerns
7. WITNESS PATTERNS: Note patterns in witness involvement across events

Return a JSON object with this structure:
{
    "gaps": [{"start_date": "...", "end_date": "...", "description": "...", "significance": "high/medium/low"}],
    "inconsistencies": [{"event_ids": [...], "description": "...", "impact": "..."}],
    "prosecution_events": [{"event_id": "...", "reason": "..."}],
    "defence_events": [{"event_id": "...", "reason": "..."}],
    "contested_facts": [{"event_id": "...", "issue": "...", "recommendation": "..."}],
    "ground_connections": [{"event_id": "...", "ground_type": "...", "relevance": "..."}],
    "key_observations": ["..."],
    "recommended_actions": ["..."]
}"""
    events_text = json.dumps(events, indent=2, default=str)
    grounds_text = json.dumps(grounds, indent=2, default=str) if grounds else "No grounds identified yet"
    user_prompt = f"""Analyse this criminal case timeline for an appeal:

TIMELINE EVENTS:
{events_text}

IDENTIFIED GROUNDS OF APPEAL:
{grounds_text}

Provide a comprehensive analysis identifying gaps, inconsistencies, and appeal-relevant insights."""
    try:
        response = await call_llm_with_fallback(system_prompt, user_prompt, f"timeline_analysis_{case_id}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI analysis failed: {str(e)}")
    try:
        json_match = response
        if "```json" in response:
            json_match = response.split("```json")[1].split("```")[0]
        elif "```" in response:
            json_match = response.split("```")[1].split("```")[0]
        analysis = json.loads(json_match.strip())
    except json.JSONDecodeError:
        analysis = {
            "gaps": [], "inconsistencies": [], "prosecution_events": [], "defence_events": [],
            "contested_facts": [], "ground_connections": [],
            "key_observations": [response[:2000]], "recommended_actions": []
        }
    return {"analysis": analysis, "event_count": len(events), "analyzed_at": datetime.now(timezone.utc).isoformat()}


# ============================================================================
# TIMELINE PDF EXPORT (PRESERVED FROM EXISTING CODEBASE)
# ============================================================================

@router.get("/cases/{case_id}/timeline/export-pdf")
async def export_timeline_pdf(case_id: str, request: Request):
    """Export timeline as a formatted PDF"""
    user = await get_current_user(request)
    case = await db.cases.find_one({"case_id": case_id, "user_id": user.user_id})
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
    events = await db.timeline_events.find({"case_id": case_id, "user_id": user.user_id}, {"_id": 0}).sort("event_date", 1).to_list(500)
    documents = await db.documents.find({"case_id": case_id, "user_id": user.user_id}, {"_id": 0, "document_id": 1, "filename": 1}).to_list(500)
    doc_map = {d["document_id"]: d["filename"] for d in documents}
    grounds = await db.grounds_of_merit.find({"case_id": case_id, "user_id": user.user_id}, {"_id": 0, "ground_id": 1, "title": 1}).to_list(100)
    ground_map = {g["ground_id"]: g["title"] for g in grounds}

    from reportlab.lib import colors
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import mm
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
    from io import BytesIO

    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, topMargin=20*mm, bottomMargin=20*mm, leftMargin=15*mm, rightMargin=15*mm)
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle('CustomTitle', parent=styles['Heading1'], fontSize=18, spaceAfter=12, textColor=colors.HexColor('#0f172a'))
    subtitle_style = ParagraphStyle('Subtitle', parent=styles['Normal'], fontSize=10, textColor=colors.HexColor('#64748b'), spaceAfter=20)
    event_title_style = ParagraphStyle('EventTitle', parent=styles['Heading3'], fontSize=12, textColor=colors.HexColor('#1e293b'), spaceBefore=8, spaceAfter=4)
    event_body_style = ParagraphStyle('EventBody', parent=styles['Normal'], fontSize=10, textColor=colors.HexColor('#475569'), spaceAfter=4)
    meta_style = ParagraphStyle('Meta', parent=styles['Normal'], fontSize=9, textColor=colors.HexColor('#94a3b8'))
    section_style = ParagraphStyle('Section', parent=styles['Heading2'], fontSize=14, textColor=colors.HexColor('#334155'), spaceBefore=16, spaceAfter=8)
    story = []
    story.append(Paragraph(f"Case Timeline: {case.get('title', 'Untitled Case')}", title_style))
    story.append(Paragraph(f"Generated for {user.name} on {datetime.now().strftime('%d %B %Y')}", subtitle_style))
    story.append(Paragraph("Criminal Law Appeal Case Management by Deb King GLENMORE PARK NSW", meta_style))
    story.append(Spacer(1, 10*mm))
    critical_count = len([e for e in events if e.get('significance') == 'critical'])
    contested_count = len([e for e in events if e.get('is_contested')])
    story.append(Paragraph("Timeline Summary", section_style))
    summary_data = [
        ["Total Events", str(len(events))],
        ["Critical Events", str(critical_count)],
        ["Contested Facts", str(contested_count)],
        ["Date Range", f"{events[0].get('event_date', 'N/A')[:10] if events else 'N/A'} to {events[-1].get('event_date', 'N/A')[:10] if events else 'N/A'}"]
    ]
    summary_table = Table(summary_data, colWidths=[80*mm, 80*mm])
    summary_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#f1f5f9')),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.HexColor('#334155')),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('PADDING', (0, 0), (-1, -1), 6),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#e2e8f0')),
    ]))
    story.append(summary_table)
    story.append(Spacer(1, 8*mm))
    story.append(Paragraph("Chronological Events", section_style))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#e2e8f0')))
    significance_colors = {'critical': '#dc2626', 'important': '#ea580c', 'normal': '#3b82f6', 'minor': '#9ca3af'}
    for event in events:
        date_str = event.get('event_date', '')[:10] if event.get('event_date') else 'Unknown'
        sig = event.get('significance', 'normal')
        sig_color = significance_colors.get(sig, '#3b82f6')
        contested_marker = " [CONTESTED]" if event.get('is_contested') else ""
        perspective = f" ({event.get('perspective', 'neutral').upper()})" if event.get('perspective') != 'neutral' else ""
        story.append(Paragraph(f"<font color='{sig_color}'>\u25cf</font> {date_str} \u2014 {event.get('title', 'Untitled')}{contested_marker}{perspective}", event_title_style))
        story.append(Paragraph(event.get('description', 'No description'), event_body_style))
        meta_parts = []
        if event.get('event_type'):
            meta_parts.append(f"Type: {event['event_type'].replace('_', ' ').title()}")
        if event.get('source_citation'):
            meta_parts.append(f"Source: {event['source_citation'][:50]}")
        if event.get('linked_documents'):
            linked_names = [doc_map.get(d, d) for d in event['linked_documents'][:3]]
            meta_parts.append(f"Docs: {', '.join(linked_names)}")
        if event.get('related_grounds'):
            linked_grounds = [ground_map.get(g, g) for g in event['related_grounds'][:2]]
            meta_parts.append(f"Grounds: {', '.join(linked_grounds)}")
        if event.get('participants'):
            participants = [f"{p.get('name', 'Unknown')} ({p.get('role', 'Unknown')})" for p in event['participants'][:3]]
            meta_parts.append(f"Participants: {', '.join(participants)}")
        if meta_parts:
            story.append(Paragraph(" | ".join(meta_parts), meta_style))
        if event.get('contested_details'):
            story.append(Paragraph(f"<i>Contested: {event['contested_details']}</i>", meta_style))
        story.append(Spacer(1, 4*mm))
    story.append(Spacer(1, 10*mm))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#e2e8f0')))
    story.append(Paragraph("One woman's fight for justice \u2014 seeking truth for Joshua Homann, failed by the system", meta_style))
    story.append(Spacer(1, 8*mm))
    disclaimer_style = ParagraphStyle('Disclaimer', parent=styles['Normal'], fontSize=9, leading=12, textColor=colors.HexColor('#1e293b'))
    disclaimer_text = (
        "<b><font color='#dc2626'>NOT LEGAL ADVICE</font></b> \u2014 This application is an educational research tool only and does NOT constitute legal advice. "
        "It must NOT be relied upon as such. The creator of this application is not a lawyer. All analysis, findings, reports, and "
        "recommendations generated by this tool must be independently verified by a qualified Australian legal professional before "
        "any action is taken. This tool covers Australian law only. No solicitor-client relationship is created by using this service."
    )
    story.append(Paragraph(disclaimer_text, disclaimer_style))
    doc.build(story)
    buffer.seek(0)
    filename = f"timeline_{case.get('title', 'case')[:30].replace(' ', '_')}_{datetime.now().strftime('%Y%m%d')}.pdf"
    return Response(content=buffer.getvalue(), media_type="application/pdf", headers={"Content-Disposition": f"attachment; filename={filename}"})
