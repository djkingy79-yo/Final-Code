"""
Criminal Appeal AI - Analysis Router (Contradictions + Progress)
Extracted from server.py monolith.
"""
from fastapi import APIRouter, HTTPException, Request
from datetime import datetime, timezone
import json
import logging

from config import db
from auth_utils import get_current_user
from services.llm_service import call_llm_with_fallback
from services.offence_helpers import get_offence_context, enforce_forensic_language

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api", tags=["analysis"])


@router.post("/cases/{case_id}/analyse-contradictions", response_model=dict)
async def analyse_witness_contradictions(case_id: str, request: Request):
    """AI analysis to find contradictions in documents"""
    user = await get_current_user(request)
    case = await db.cases.find_one({"case_id": case_id, "user_id": user.user_id})
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
    documents = await db.documents.find(
        {"case_id": case_id, "content_text": {"$exists": True, "$ne": ""}},
        {"_id": 0, "file_data": 0}
    ).to_list(100)
    if len(documents) < 2:
        raise HTTPException(status_code=400, detail="Need at least 2 documents with text to compare")
    doc_context = ""
    for i, doc in enumerate(documents):
        doc_context += f"\n=== DOCUMENT {i+1}: {doc.get('filename', 'Unknown')} ===\n"
        content = doc.get('content_text', '')[:4000]
        doc_context += f"Content:\n{content}\n"
    system_prompt = """You are a legal analyst finding contradictions in witness statements. Use Australian English spelling throughout.

ANTI-HALLUCINATION — ABSOLUTE:
- Only identify contradictions that are EXPLICITLY present in the supplied documents.
- Do NOT infer or fabricate contradictions.
- Do NOT invent document names, witness names, or facts not in the supplied text.
- If no contradictions exist, return an empty contradictions array.

Find:
1. DIRECT CONTRADICTIONS - witnesses contradict each other
2. INTERNAL INCONSISTENCIES - witness contradicts themselves
3. TIMELINE CONFLICTS - times/dates don't align
4. FACTUAL DISCREPANCIES - differences in descriptions
5. OMISSIONS - facts missing from one account

Return JSON:
{
    "contradictions": [{"type": "...", "severity": "critical|significant|minor", "documents_involved": [], "description": "...", "appeal_relevance": "..."}],
    "summary": "...",
    "total_critical": 0, "total_significant": 0, "total_minor": 0
}"""
    try:
        response = await call_llm_with_fallback(system_prompt, f"Find contradictions in these documents:\n{doc_context}", f"contradiction_{case_id}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI analysis failed: {str(e)}")
    try:
        json_match = response
        if "```json" in response:
            json_match = response.split("```json")[1].split("```")[0]
        analysis = json.loads(json_match.strip())
    except (json.JSONDecodeError, IndexError, ValueError):
        analysis = {"contradictions": [], "summary": response[:2000], "total_critical": 0, "total_significant": 0, "total_minor": 0}
    return {"analysis": analysis, "documents_analysed": len(documents), "analysed_at": datetime.now(timezone.utc).isoformat()}


@router.post("/cases/{case_id}/progress-analysis", response_model=dict)
async def generate_progress_analysis(case_id: str, request: Request):
    """AI-powered case progress analysis with recommendations"""
    user = await get_current_user(request)
    case = await db.cases.find_one({"case_id": case_id, "user_id": user.user_id}, {"_id": 0})
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
    documents = await db.documents.find({"case_id": case_id}, {"_id": 0, "file_data": 0}).to_list(100)
    timeline = await db.timeline_events.find({"case_id": case_id}, {"_id": 0}).to_list(100)
    grounds = await db.grounds_of_merit.find({"case_id": case_id}, {"_id": 0}).to_list(50)
    deadlines = await db.deadlines.find({"case_id": case_id}, {"_id": 0}).to_list(50)
    checklist = await db.checklist_items.find({"case_id": case_id}, {"_id": 0}).to_list(50)
    reports = await db.reports.find({"case_id": case_id, "status": "completed"}, {"_id": 0, "content": 0}).to_list(20)
    completed_report_types = sorted({report.get("report_type") for report in reports if report.get("report_type") in {"quick_summary", "full_detailed", "extensive_log", "barrister_view"}})
    context = f"""CASE: {case.get('title', 'Unknown')}
DEFENDANT: {case.get('defendant_name', 'Unknown')}
STATE: {case.get('state', 'Unknown').upper()}
COURT: {case.get('court', 'Unknown')}
OFFENCE: {case.get('offence_type', 'Unknown')} ({case.get('offence_category', 'Unknown')})

DOCUMENTS UPLOADED: {len(documents)}
TIMELINE EVENTS: {len(timeline)}
GROUNDS IDENTIFIED: {len(grounds)}
REPORTS GENERATED: {len(completed_report_types)}
COMPLETED REPORT TYPES: {', '.join(completed_report_types) if completed_report_types else 'None'}
DEADLINES SET: {len(deadlines)}
CHECKLIST ITEMS: {len(checklist)} (Completed: {sum(1 for c in checklist if c.get('completed'))})
"""
    if grounds:
        context += "\nIDENTIFIED GROUNDS:\n"
        for g in grounds:
            context += f"- {g.get('title', 'Unknown')} (Type: {g.get('ground_type', 'Unknown')}, Strength: {g.get('strength', 'Unknown')})\n"
    if deadlines:
        context += "\nDEADLINES:\n"
        for d in deadlines:
            context += f"- {d.get('title', 'Unknown')}: {d.get('due_date', 'Unknown')} (Status: {d.get('status', 'pending')})\n"

    offence_context = get_offence_context(case)
    state_name = case.get('state', 'Unknown').upper()

    system_prompt = f"""You are an expert Australian criminal appeal legal analyst.
Analyse the case progress and provide a comprehensive progress report using Australian English spelling.

JURISDICTION: {state_name}
{offence_context}

ANTI-HALLUCINATION — ABSOLUTE:
- Do NOT invent or fabricate any legislation, Act, section, case authority, dates, or names.
- Only cite Acts that are current and in force for {state_name}.
- Do NOT default to NSW legislation if this case is from a different jurisdiction.
- If the jurisdiction is UNSPECIFIED, flag this explicitly and note which jurisdiction's legislation is being applied provisionally.
- Do NOT fabricate sentencing statistics, comparator cases, or appellate outcomes.

FORENSIC LANGUAGE:
- Use strict third-person forensic appellate language throughout.
- Do NOT use "we", "us", "our", "you", "your", or "your legal team".
- Use hedging qualifiers: "It is arguable that", "There is a tenable basis", "It is submitted that".
- Do NOT make definitive assertions such as "The trial judge erred" — instead use "It is arguable that the trial judge erred".
- Do NOT state that an appeal will succeed or is likely to succeed.

Structure your analysis with these sections:

## APPEAL PROGRESS SUMMARY
Brief overview of where this case stands in the appeal process.

## COMPLETED STEPS
What has been done so far based on the data provided.

## CRITICAL NEXT STEPS
The most urgent actions needed to advance this appeal, in priority order.

## CASE STRENGTH ASSESSMENT
Based on the grounds identified and documents available, assess the overall case strength.

## TIMELINE RECOMMENDATIONS
Recommended deadlines and milestones for the appeal process in this jurisdiction.

## STRATEGIC RECOMMENDATIONS
Specific tactical advice for strengthening this appeal.

## RISK FACTORS
Potential issues or weaknesses that need to be addressed.

Be specific to the jurisdiction and offence type. Use Australian legal terminology and reference relevant courts and processes."""
    try:
        response = await call_llm_with_fallback(system_prompt, f"Analyse the progress of this criminal appeal case:\n\n{context}", f"progress_{case_id}")
        response = enforce_forensic_language(response)
        return {"analysis": response, "generated_at": datetime.now(timezone.utc).isoformat()}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI analysis failed: {str(e)}")
