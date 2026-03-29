"""
Criminal Appeal AI - Timeline Router
Extracted from server.py monolith.
"""
from fastapi import APIRouter, HTTPException, Request, Response
from typing import List
from datetime import datetime, timezone
import uuid
import json
import re
import logging

from config import db
from auth_utils import get_current_user
from models import TimelineEvent, TimelineEventCreate
from services.llm_service import call_llm_with_fallback

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api", tags=["timeline"])


@router.get("/cases/{case_id}/timeline", response_model=List[dict])
async def get_timeline(case_id: str, request: Request):
    """Get timeline events for a case"""
    user = await get_current_user(request)
    case = await db.cases.find_one({"case_id": case_id, "user_id": user.user_id})
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
    events = await db.timeline_events.find({"case_id": case_id}, {"_id": 0}).sort("event_date", 1).to_list(500)
    return events


@router.post("/cases/{case_id}/timeline", response_model=dict)
async def create_timeline_event(case_id: str, event_data: TimelineEventCreate, request: Request):
    """Create a timeline event"""
    user = await get_current_user(request)
    case = await db.cases.find_one({"case_id": case_id, "user_id": user.user_id})
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
    event = TimelineEvent(case_id=case_id, user_id=user.user_id, **event_data.model_dump())
    event_dict = event.model_dump()
    event_dict["event_date"] = event_dict["event_date"].isoformat()
    event_dict["created_at"] = event_dict["created_at"].isoformat()
    await db.timeline_events.insert_one(event_dict)
    await db.cases.update_one({"case_id": case_id}, {"$set": {"updated_at": datetime.now(timezone.utc).isoformat()}})
    created_event = await db.timeline_events.find_one({"event_id": event.event_id}, {"_id": 0})
    return created_event


@router.put("/cases/{case_id}/timeline/{event_id}", response_model=dict)
async def update_timeline_event(case_id: str, event_id: str, event_data: TimelineEventCreate, request: Request):
    """Update a timeline event"""
    user = await get_current_user(request)
    update_data = event_data.model_dump()
    update_data["event_date"] = update_data["event_date"].isoformat()
    result = await db.timeline_events.update_one(
        {"event_id": event_id, "case_id": case_id, "user_id": user.user_id}, {"$set": update_data}
    )
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="Event not found")
    return await db.timeline_events.find_one({"event_id": event_id}, {"_id": 0})


@router.delete("/cases/{case_id}/timeline/{event_id}")
async def delete_timeline_event(case_id: str, event_id: str, request: Request):
    """Delete a timeline event"""
    user = await get_current_user(request)
    result = await db.timeline_events.delete_one({"event_id": event_id, "case_id": case_id, "user_id": user.user_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Event not found")
    return {"message": "Event deleted"}


@router.post("/cases/{case_id}/timeline/auto-generate", response_model=dict)
async def auto_generate_timeline(case_id: str, request: Request):
    """AI-powered timeline generation from uploaded documents"""
    user = await get_current_user(request)
    case = await db.cases.find_one({"case_id": case_id, "user_id": user.user_id}, {"_id": 0})
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
    documents = await db.documents.find({"case_id": case_id}, {"_id": 0, "file_data": 0}).to_list(500)
    if not documents:
        raise HTTPException(status_code=400, detail="No documents found. Please upload documents first.")
    documents_with_text = [doc for doc in documents if doc.get("content_text")]
    missing_docs = [doc for doc in documents if not doc.get("content_text")]
    if not documents_with_text:
        raise HTTPException(status_code=400, detail="No documents with extracted text found. Please extract text before generating a timeline.")
    doc_context = f"CASE: {case.get('title', 'Unknown')}\nDEFENDANT: {case.get('defendant_name', 'Unknown')}\n\n"
    doc_context += f"DOCUMENT COUNT: {len(documents)} (with text: {len(documents_with_text)}; missing text: {len(missing_docs)})\n\n"
    doc_context += "=== DOCUMENTS WITH TEXT ===\n\n"
    for doc in documents_with_text:
        content = doc.get('content_text', '')[:4000]
        doc_context += f"DOCUMENT: {doc.get('filename', 'Untitled')}\n"
        if doc.get("document_type"):
            doc_context += f"TYPE: {doc.get('document_type')}\n"
        doc_context += f"CONTENT:\n{content}\n\n"
    if missing_docs:
        doc_context += "=== DOCUMENTS WITHOUT EXTRACTED TEXT (metadata only) ===\n\n"
        for doc in missing_docs:
            uploaded_at = doc.get('uploaded_at')
            uploaded_label = uploaded_at.isoformat() if hasattr(uploaded_at, 'isoformat') else str(uploaded_at)
            doc_context += f"DOCUMENT: {doc.get('filename', 'Untitled')} | Uploaded: {uploaded_label}\n"
            if doc.get("document_type"):
                doc_context += f"TYPE: {doc.get('document_type')}\n"
            doc_context += "NOTE: No extracted text available.\n\n"
    system_prompt = """You are an expert legal analyst specialising in criminal cases. Use Australian English spelling throughout.
Your task is to extract a chronological timeline of events from case documents.

For each event, identify:
1. The DATE (in YYYY-MM-DD format if possible, or approximate like "2020-01" or "Early 2020")
2. A clear TITLE for the event (brief, descriptive)
3. A DESCRIPTION with relevant details
4. The EVENT TYPE: one of [incident, arrest, court_hearing, evidence, witness, legal_filing, verdict, appeal, other]

Return your response as a JSON array of events, ordered chronologically. Example:
[
  {"date": "2019-05-15", "title": "Initial Incident", "description": "The alleged incident occurred at...", "event_type": "incident"},
  {"date": "2019-05-16", "title": "Arrest of Defendant", "description": "Police arrested...", "event_type": "arrest"}
]

Only include events you can clearly identify from the documents. Be thorough - extract ALL dates and events mentioned. If any documents are listed without extracted text, add a timeline entry noting the document exists and that text extraction is missing (date can be approximate or the upload date if provided)."""
    user_prompt = f"""Analyse these documents and extract a complete chronological timeline of all events. Ensure every document listed is represented in the timeline.

{doc_context}

Return ONLY a valid JSON array of timeline events. No other text."""
    try:
        response = await call_llm_with_fallback(system_prompt, user_prompt, f"timeline_{case_id}")
    except Exception as e:
        logger.error(f"All timeline generation attempts failed: {e}")
        raise HTTPException(status_code=500, detail=f"AI timeline generation failed after retries: {str(e)}")
    json_match = re.search(r'\[[\s\S]*\]', response)
    if not json_match:
        raise HTTPException(status_code=500, detail="Failed to parse timeline from AI response")
    try:
        events_data = json.loads(json_match.group())
    except json.JSONDecodeError:
        raise HTTPException(status_code=500, detail="Failed to parse timeline JSON")
    created_events = []
    for event in events_data:
        event_date = event.get('date', '')
        parsed_date = None
        if event_date:
            for fmt in ['%Y-%m-%d', '%Y-%m', '%Y', '%d/%m/%Y', '%d-%m-%Y']:
                try:
                    parsed_date = datetime.strptime(event_date, fmt)
                    break
                except ValueError:
                    continue
            if not parsed_date:
                year_match = re.search(r'(19|20)\d{2}', event_date)
                if year_match:
                    parsed_date = datetime.strptime(year_match.group(), '%Y')
        if not parsed_date:
            parsed_date = datetime.now(timezone.utc)
        valid_types = ['incident', 'arrest', 'court_hearing', 'evidence', 'witness', 'legal_filing', 'verdict', 'appeal', 'other']
        event_type = event.get('event_type', 'other')
        if event_type not in valid_types:
            event_type = 'other'
        timeline_event = {
            "event_id": f"evt_{uuid.uuid4().hex[:12]}",
            "case_id": case_id, "user_id": user.user_id,
            "title": event.get('title', 'Unknown Event')[:200],
            "description": event.get('description', '')[:2000],
            "event_date": parsed_date.isoformat(),
            "event_type": event_type,
            "auto_generated": True,
            "created_at": datetime.now(timezone.utc).isoformat()
        }
        await db.timeline_events.insert_one(timeline_event)
        if '_id' in timeline_event:
            del timeline_event['_id']
        created_events.append(timeline_event)
    created_events.sort(key=lambda x: x.get('event_date', ''))
    return {"message": f"Successfully generated {len(created_events)} timeline events", "events_created": len(created_events), "events": created_events}


@router.post("/cases/{case_id}/timeline/analyze", response_model=dict)
async def analyze_timeline(case_id: str, request: Request):
    """AI-powered timeline analysis to find gaps, inconsistencies, and insights"""
    user = await get_current_user(request)
    case = await db.cases.find_one({"case_id": case_id, "user_id": user.user_id})
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
    events = await db.timeline_events.find({"case_id": case_id}, {"_id": 0}).sort("event_date", 1).to_list(500)
    if len(events) < 2:
        raise HTTPException(status_code=400, detail="Need at least 2 timeline events for analysis")
    grounds = await db.grounds_of_merit.find({"case_id": case_id}, {"_id": 0}).to_list(100)
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


@router.get("/cases/{case_id}/timeline/export-pdf")
async def export_timeline_pdf(case_id: str, request: Request):
    """Export timeline as a formatted PDF"""
    user = await get_current_user(request)
    case = await db.cases.find_one({"case_id": case_id, "user_id": user.user_id})
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
    events = await db.timeline_events.find({"case_id": case_id}, {"_id": 0}).sort("event_date", 1).to_list(500)
    documents = await db.documents.find({"case_id": case_id}, {"_id": 0, "document_id": 1, "filename": 1}).to_list(500)
    doc_map = {d["document_id"]: d["filename"] for d in documents}
    grounds = await db.grounds_of_merit.find({"case_id": case_id}, {"_id": 0, "ground_id": 1, "title": 1}).to_list(100)
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
