# DO NOT UNDO — contradictions router. All endpoints in this file are approved and must be preserved.
"""
Criminal Appeal AI - Contradiction Finder Router
AI-powered feature to scan documents and notes to find contradictions and inconsistencies
"""
from fastapi import APIRouter, HTTPException, Request
from typing import List, Optional
from datetime import datetime, timezone
from pydantic import BaseModel
import os
import json

from config import db, logger
from auth_utils import get_current_user, verify_case_ownership

router = APIRouter(prefix="/api/cases/{case_id}/contradictions", tags=["contradictions"])


class ContradictionFinding(BaseModel):
    id: str
    type: str  # witness_statement, timeline, evidence, testimony
    severity: str  # critical, significant, minor
    description: str
    source_documents: List[str]
    specific_quotes: List[dict]  # [{doc_id, quote, page}]
    analysis: str
    recommendations: List[str]
    created_at: datetime


class ContradictionScanRequest(BaseModel):
    focus_areas: Optional[List[str]] = None  # witness_statements, timelines, evidence, all
    document_ids: Optional[List[str]] = None  # Specific documents to analyze, or all if empty


@router.post("/scan")
async def scan_for_contradictions(case_id: str, scan_request: ContradictionScanRequest, request: Request):
    """
    Scan case documents and notes for contradictions and inconsistencies.
    Uses AI to compare witness statements, timelines, and evidence across documents.
    """
    user = await get_current_user(request)
    await verify_case_ownership(case_id, user.user_id)
    
    # Fetch the case
    case = await db.cases.find_one({"case_id": case_id}, {"_id": 0})
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
    
    # Fetch documents
    doc_filter = {"case_id": case_id}
    if scan_request.document_ids:
        doc_filter["document_id"] = {"$in": scan_request.document_ids}
    
    documents = await db.documents.find(doc_filter, {"_id": 0, "file_data": 0}).to_list(100)
    
    if len(documents) < 2:
        raise HTTPException(
            status_code=400, 
            detail="At least 2 documents are required for contradiction analysis"
        )
    
    # Fetch notes for additional context
    notes = await db.notes.find({"case_id": case_id}, {"_id": 0}).to_list(500)
    
    # Fetch timeline events
    timeline = await db.timeline_events.find(
        {"case_id": case_id},
        {"_id": 0}
    ).sort("event_date", 1).to_list(500)
    
    # Build document content for analysis
    doc_contents = []
    for doc in documents:
        content = {
            "document_id": doc.get("document_id"),
            "filename": doc.get("filename"),
            "category": doc.get("category"),
            "extracted_text": doc.get("extracted_text", "")[:10000],  # Limit text size
            "ai_analysis": doc.get("ai_analysis", ""),
            "upload_date": doc.get("upload_date", "")
        }
        doc_contents.append(content)
    
    # Build notes content
    notes_content = []
    for note in notes:
        notes_content.append({
            "note_id": note.get("note_id"),
            "title": note.get("title", ""),
            "content": note.get("content", "")[:3000],
            "category": note.get("category", ""),
            "created_at": note.get("created_at", "")
        })
    
    # Build timeline content
    timeline_content = []
    for event in timeline:
        timeline_content.append({
            "event_date": event.get("event_date", ""),
            "title": event.get("title", ""),
            "description": event.get("description", ""),
            "source": event.get("source", "")
        })
    
    # Perform AI analysis
    from services.llm_service import call_llm_for_json
    import uuid
    
    focus_instruction = ""
    if scan_request.focus_areas:
        focus_instruction = f"Focus particularly on: {', '.join(scan_request.focus_areas)}. "
    
    prompt = f"""You are a legal contradiction analyst specialising in criminal appeals in Australia.

Analyze the following case materials for contradictions, inconsistencies, and discrepancies that could be relevant for an appeal.

CASE INFORMATION:
Title: {case.get('title', 'Unknown')}
Defendant: {case.get('defendant_name', 'Unknown')}
Offence Category: {case.get('offence_category', 'Unknown')}
State: {case.get('state', 'Unknown').upper()}

DOCUMENTS ({len(doc_contents)} documents):
{json.dumps(doc_contents, indent=2, default=str)}

CASE NOTES ({len(notes_content)} notes):
{json.dumps(notes_content, indent=2, default=str)}

TIMELINE ({len(timeline_content)} events):
{json.dumps(timeline_content, indent=2, default=str)}

{focus_instruction}

Look for:
1. WITNESS STATEMENT CONTRADICTIONS: Different witnesses giving conflicting accounts of the same event
2. TIMELINE INCONSISTENCIES: Events that couldn't have happened in the stated sequence or timeframe
3. EVIDENCE CONFLICTS: Physical evidence that contradicts testimony or other evidence
4. SELF-CONTRADICTIONS: The same witness or document contradicting itself
5. PROCEDURAL IRREGULARITIES: Actions taken outside proper procedures that contradict official records

For each contradiction found, provide:
- A severity rating (critical, significant, or minor)
- The type of contradiction
- A clear description
- The specific documents involved
- Direct quotes where possible
- Analysis of why this matters for the appeal
- Recommendations for how to use this finding

Return your analysis as JSON in this format:
{{
    "contradictions": [
        {{
            "type": "witness_statement|timeline|evidence|testimony|procedural",
            "severity": "critical|significant|minor",
            "description": "Clear description of the contradiction",
            "source_documents": ["document_id1", "document_id2"],
            "specific_quotes": [
                {{"doc_id": "...", "quote": "...", "context": "..."}}
            ],
            "analysis": "Why this matters for the appeal",
            "recommendations": ["How to use this finding"]
        }}
    ],
    "summary": {{
        "total_found": 0,
        "critical_count": 0,
        "significant_count": 0,
        "minor_count": 0,
        "key_finding": "Most important finding summary",
        "overall_assessment": "Overall assessment of contradiction severity"
    }},
    "recommended_actions": ["List of recommended next steps"]
}}

If no contradictions are found, return an empty contradictions array with an appropriate summary.
Important: Return ONLY valid JSON, no additional text."""

    try:
        analysis = await call_llm_for_json(
            "You are a legal contradiction analyst specialising in criminal appeals in Australia.",
            prompt,
            f"contradiction_{case_id}_{uuid.uuid4().hex[:8]}",
            max_tokens=8192,
            timeout_seconds=120,
        )
        if not isinstance(analysis, dict):
            analysis = {"contradictions": [], "summary": {"total_contradictions": 0, "critical_count": 0, "significant_count": 0, "minor_count": 0, "key_finding": "Analysis could not be parsed.", "overall_assessment": ""}, "recommended_actions": []}
        
        # Add IDs and timestamps to contradictions
        for i, contradiction in enumerate(analysis.get("contradictions", [])):
            contradiction["id"] = f"contra_{uuid.uuid4().hex[:12]}"
            contradiction["created_at"] = datetime.now(timezone.utc).isoformat()
        
        # Store the scan result
        scan_result = {
            "scan_id": f"scan_{uuid.uuid4().hex[:12]}",
            "case_id": case_id,
            "user_id": user.user_id,
            "scanned_at": datetime.now(timezone.utc).isoformat(),
            "documents_analysed": len(documents),
            "notes_analysed": len(notes),
            "focus_areas": scan_request.focus_areas or ["all"],
            "results": analysis
        }
        
        await db.contradiction_scans.insert_one(scan_result)
        
        # Remove MongoDB _id before returning
        scan_result.pop("_id", None)
        
        return scan_result
        
    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse AI response: {e}")
        raise HTTPException(
            status_code=500, 
            detail="Failed to analyse documents. Please try again."
        )
    except Exception as e:
        logger.error(f"Contradiction scan failed: {e}")
        raise HTTPException(
            status_code=500, 
            detail=f"Analysis failed: {str(e)}"
        )


@router.get("/scans")
async def get_contradiction_scans(case_id: str, request: Request):
    """
    Get all previous contradiction scans for a case.
    """
    user = await get_current_user(request)
    await verify_case_ownership(case_id, user.user_id)
    
    scans = await db.contradiction_scans.find(
        {"case_id": case_id},
        {"_id": 0}
    ).sort("scanned_at", -1).to_list(50)
    
    return scans


@router.get("/scans/{scan_id}")
async def get_contradiction_scan(case_id: str, scan_id: str, request: Request):
    """
    Get a specific contradiction scan result.
    """
    user = await get_current_user(request)
    await verify_case_ownership(case_id, user.user_id)
    
    scan = await db.contradiction_scans.find_one(
        {"case_id": case_id, "scan_id": scan_id},
        {"_id": 0}
    )
    
    if not scan:
        raise HTTPException(status_code=404, detail="Scan not found")
    
    return scan


@router.delete("/scans/{scan_id}")
async def delete_contradiction_scan(case_id: str, scan_id: str, request: Request):
    """
    Delete a contradiction scan result.
    """
    user = await get_current_user(request)
    await verify_case_ownership(case_id, user.user_id)
    
    result = await db.contradiction_scans.delete_one({
        "case_id": case_id,
        "scan_id": scan_id
    })
    
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Scan not found")
    
    return {"message": "Scan deleted successfully"}
