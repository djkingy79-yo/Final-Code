"""
Criminal Appeal AI - Grounds of Merit Router
Extracted from server.py monolith.
"""
from fastapi import APIRouter, HTTPException, Request
from datetime import datetime, timezone
import uuid
import json
import re
import os
import logging

from config import db
from auth_utils import get_current_user
from models import GroundOfMerit, GroundOfMeritCreate, GroundOfMeritUpdate, FEATURE_PRICES, feature_type_variants
from services.llm_service import call_llm_with_fallback
from services.offence_helpers import get_offence_context, get_offence_system_prompt
from services.document_helpers import build_document_context
from services.legitimacy_engine import calculate_ground_rating, validate_ground_type
from offence_framework import OFFENCE_CATEGORIES

logger = logging.getLogger(__name__)

ADMIN_EMAILS = [email.strip() for email in os.environ.get("ADMIN_EMAILS", "").split(",") if email.strip()]


def is_admin_user(email: str) -> bool:
    normalized = (email or "").strip().lower()
    allowed = {(e or "").strip().lower() for e in ADMIN_EMAILS}
    return normalized in allowed


GROUND_TYPES = [
    "procedural_error", "fresh_evidence", "miscarriage_of_justice",
    "sentencing_error", "judicial_error", "ineffective_counsel",
    "prosecution_misconduct", "jury_irregularity", "constitutional_violation", "other"
]

router = APIRouter(prefix="/api", tags=["grounds"])


@router.get("/cases/{case_id}/grounds", response_model=dict)
async def get_grounds_of_merit(case_id: str, request: Request):
    """Get all grounds of merit for a case - requires payment to see details"""
    user = await get_current_user(request)
    case = await db.cases.find_one({"case_id": case_id, "user_id": user.user_id})
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
    grounds = await db.grounds_of_merit.find({"case_id": case_id}, {"_id": 0}).sort([("strength", 1), ("created_at", -1)]).to_list(100)
    payment = await db.payments.find_one({
        "case_id": case_id, "user_id": user.user_id,
        "feature_type": {"$in": feature_type_variants("grounds_of_merit")},
        "status": "completed"
    })
    is_unlocked = payment is not None or "grounds_of_merit" in (case.get("unlocked_features") or []) or is_admin_user(user.email)
    if is_unlocked:
        # Retroactively score any grounds missing legitimacy_scores
        for g in grounds:
            if not g.get("legitimacy_scores"):
                scored = calculate_ground_rating({
                    "ground_type": g.get("ground_type", "other"),
                    "supporting_evidence": [{"quote": e} for e in (g.get("supporting_evidence") or [])]
                })
                g["legitimacy_scores"] = scored
                g["strength"] = scored["rating"]
                # Persist the score for future reads
                await db.grounds_of_merit.update_one(
                    {"ground_id": g["ground_id"]},
                    {"$set": {"legitimacy_scores": scored, "strength": scored["rating"]}}
                )
        return {"grounds": grounds, "count": len(grounds), "is_unlocked": True, "unlock_price": FEATURE_PRICES["grounds_of_merit"]["price"]}
    else:
        return {
            "grounds": [], "count": len(grounds), "is_unlocked": False,
            "unlock_price": FEATURE_PRICES["grounds_of_merit"]["price"],
            "message": f"Found {len(grounds)} potential grounds of merit. Pay ${FEATURE_PRICES['grounds_of_merit']['price']:.2f} to unlock full details."
        }


@router.post("/cases/{case_id}/grounds", response_model=dict)
async def create_ground_of_merit(case_id: str, ground_data: GroundOfMeritCreate, request: Request):
    """Create a new ground of merit"""
    user = await get_current_user(request)
    case = await db.cases.find_one({"case_id": case_id, "user_id": user.user_id})
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
    ground = GroundOfMerit(case_id=case_id, user_id=user.user_id, **ground_data.model_dump())
    ground_dict = ground.model_dump()
    ground_dict["created_at"] = ground_dict["created_at"].isoformat()
    ground_dict["updated_at"] = ground_dict["updated_at"].isoformat()
    await db.grounds_of_merit.insert_one(ground_dict)
    await db.cases.update_one({"case_id": case_id}, {"$set": {"updated_at": datetime.now(timezone.utc).isoformat()}})
    created_ground = await db.grounds_of_merit.find_one({"ground_id": ground.ground_id}, {"_id": 0})
    return created_ground


@router.get("/cases/{case_id}/grounds/{ground_id}", response_model=dict)
async def get_ground_of_merit(case_id: str, ground_id: str, request: Request):
    """Get a specific ground of merit"""
    user = await get_current_user(request)
    ground = await db.grounds_of_merit.find_one(
        {"ground_id": ground_id, "case_id": case_id, "user_id": user.user_id}, {"_id": 0}
    )
    if not ground:
        raise HTTPException(status_code=404, detail="Ground of merit not found")
    return ground


@router.put("/cases/{case_id}/grounds/{ground_id}", response_model=dict)
async def update_ground_of_merit(case_id: str, ground_id: str, ground_data: GroundOfMeritUpdate, request: Request):
    """Update a ground of merit"""
    user = await get_current_user(request)
    update_fields = {k: v for k, v in ground_data.model_dump().items() if v is not None}
    update_fields["updated_at"] = datetime.now(timezone.utc).isoformat()
    result = await db.grounds_of_merit.update_one(
        {"ground_id": ground_id, "case_id": case_id, "user_id": user.user_id}, {"$set": update_fields}
    )
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Ground of merit not found")
    return await db.grounds_of_merit.find_one({"ground_id": ground_id}, {"_id": 0})


@router.delete("/cases/{case_id}/grounds/{ground_id}")
async def delete_ground_of_merit(case_id: str, ground_id: str, request: Request):
    """Delete a ground of merit"""
    user = await get_current_user(request)
    result = await db.grounds_of_merit.delete_one({"ground_id": ground_id, "case_id": case_id, "user_id": user.user_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Ground of merit not found")
    return {"message": "Ground of merit deleted"}


@router.post("/cases/{case_id}/grounds/{ground_id}/investigate", response_model=dict)
async def investigate_ground_of_merit(case_id: str, ground_id: str, request: Request):
    """Deep AI investigation of a specific ground of merit"""
    user = await get_current_user(request)
    ground = await db.grounds_of_merit.find_one({"ground_id": ground_id, "case_id": case_id, "user_id": user.user_id}, {"_id": 0})
    if not ground:
        raise HTTPException(status_code=404, detail="Ground of merit not found")
    case = await db.cases.find_one({"case_id": case_id}, {"_id": 0})
    documents = await db.documents.find({"case_id": case_id}, {"_id": 0, "file_data": 0}).to_list(500)
    timeline = await db.timeline_events.find({"case_id": case_id}, {"_id": 0}).sort("event_date", 1).to_list(500)
    offence_category = case.get('offence_category', 'homicide')
    offence_context = get_offence_context(case)
    category_data = OFFENCE_CATEGORIES.get(offence_category, OFFENCE_CATEGORIES.get('homicide'))
    context = f"""
=== CASE INFORMATION ===
Title: {case.get('title', 'Unknown')}
Defendant: {case.get('defendant_name', 'Unknown')}
Case Number: {case.get('case_number', 'N/A')}
Court: {case.get('court', 'N/A')}

{offence_context}

=== GROUND OF MERIT TO INVESTIGATE ===
Title: {ground.get('title')}
Type: {ground.get('ground_type')}
Description: {ground.get('description')}
Current Strength: {ground.get('strength')}
Supporting Evidence Listed: {', '.join(ground.get('supporting_evidence', []))}

"""
    doc_context = build_document_context(documents, per_doc_char_limit=1500, total_char_budget=12000, include_description=False, content_heading="CONTENT")
    if documents:
        context += f"=== CASE DOCUMENTS ({doc_context['included_docs']} included / {len(documents)} total) - SEARCH THESE FOR EVIDENCE ===\n"
        context += doc_context["text"] + "\n"
        if doc_context["omitted_docs"] > 0:
            context += f"[Note: {doc_context['omitted_docs']} document(s) omitted from prompt for speed optimisation.]\n"
    if timeline:
        timeline_limit = 100
        timeline_slice = timeline[:timeline_limit]
        context += f"\n=== TIMELINE ({len(timeline_slice)} included / {len(timeline)} total events) ===\n"
        for event in timeline_slice:
            context += f"- {event.get('event_date')}: {event.get('title')} - {event.get('description', '')[:180]}\n"
        if len(timeline) > timeline_limit:
            context += f"[... {len(timeline) - timeline_limit} additional timeline events omitted for speed ...]\n"
    system_prompt = get_offence_system_prompt(offence_category, case.get('state', ''))
    system_prompt += "\n\nIMPORTANT: You must search through the provided document content and cite specific evidence.\nQuote directly from documents to support your analysis.\nDo NOT invent case citations. Only reference cases you are confident are real."
    # Build legislation examples from case jurisdiction, not NSW default
    case_state = case.get('state', 'nsw')
    state_leg_key = f"{case_state}_legislation"
    state_legislation = category_data.get(state_leg_key, category_data.get('nsw_legislation', {}))
    law_examples = []
    for act_name, sections in state_legislation.items():
        for section in sections[:3]:
            law_examples.append(f"   - {section.get('section')} {act_name} - {section.get('title')}")
    law_examples_str = "\n".join(law_examples)
    user_prompt = f"""Conduct a THOROUGH investigation of this ground of merit.

{context}

REQUIRED ANALYSIS (search the documents above for evidence):

1. VIABILITY ASSESSMENT
   - Rate: Strong/Moderate/Weak with detailed justification
   - Quote specific evidence FROM THE DOCUMENTS above

2. DOCUMENT EVIDENCE
   - For EACH document, explain what it contains relevant to this ground
   - Quote specific passages that support or undermine this ground

3. RELEVANT LAW SECTIONS (be specific to this {category_data.get('name', 'criminal')} case)
{law_examples_str}
   - Other relevant sections with explanations

4. SIMILAR CASES
   - Name 2-3 well-established Australian cases relevant to {category_data.get('name', 'this type of')} appeals
   - Only reference cases you are confident are real — do NOT fabricate citations
   - Explain relevance to this ground

5. EVIDENCE GAPS
   - What additional evidence would strengthen this ground?
   - What material appears to be missing from the analysis?

6. ASSESSMENT
   - Assess the arguability of this ground based on the available material
   - Use conditional language: 'It is arguable that...' / 'The material suggests...'
   - Do NOT state that an appeal will succeed or is likely to succeed"""
    try:
        response = await call_llm_with_fallback(system_prompt, user_prompt, f"ground_{ground_id}_{uuid.uuid4().hex[:8]}")
    except Exception as e:
        logger.error(f"Ground investigation LLM failed: {e}")
        raise HTTPException(status_code=500, detail=f"AI analysis failed after retries: {str(e)}")
    law_sections = []
    similar_cases = []
    section_patterns = re.findall(r'[sS]\.?\s*(\d+[A-Za-z]?)\s+([A-Za-z\s]+(?:Act|Code))\s*(?:\d{4})?', response)
    case_state_upper = (case.get('state', 'nsw') or 'nsw').upper()
    for section_num, act_name in section_patterns[:10]:
        act_stripped = act_name.strip()
        # Determine jurisdiction from act name, not from arbitrary string matching
        jurisdiction = "Federal" if any(kw in act_stripped for kw in ["Commonwealth", "Cth", "Criminal Code Act"]) else case_state_upper
        law_sections.append({"section": section_num, "act": act_stripped, "jurisdiction": jurisdiction})
    case_patterns = re.findall(r'([A-Z][a-z]+(?:\s+v\s+)[A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)', response)
    for case_name in list(set(case_patterns))[:5]:
        similar_cases.append({"case_name": case_name, "year": "", "citation": "", "verified": False})
    deep_analysis = {
        "full_analysis": response, "investigated_at": datetime.now(timezone.utc).isoformat(),
        "law_sections_identified": len(law_sections), "similar_cases_found": len(similar_cases),
        "documents_analyzed": len(documents)
    }
    await db.grounds_of_merit.update_one(
        {"ground_id": ground_id, "case_id": case_id, "user_id": user.user_id},
        {"$set": {
            "status": "investigated",
            "analysis": response[:2000] + "..." if len(response) > 2000 else response,
            "deep_analysis": deep_analysis,
            "law_sections": law_sections if law_sections else ground.get("law_sections", []),
            "similar_cases": similar_cases if similar_cases else ground.get("similar_cases", []),
            "updated_at": datetime.now(timezone.utc).isoformat()
        }}
    )
    return await db.grounds_of_merit.find_one({"ground_id": ground_id}, {"_id": 0})


@router.post("/cases/{case_id}/grounds/auto-identify", response_model=dict)
async def auto_identify_grounds(case_id: str, request: Request):
    """AI automatically identifies potential grounds of merit from case materials - prevents duplicates"""
    user = await get_current_user(request)
    case = await db.cases.find_one({"case_id": case_id, "user_id": user.user_id}, {"_id": 0})
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
    existing_grounds = await db.grounds_of_merit.find({"case_id": case_id}, {"_id": 0}).to_list(100)
    documents = await db.documents.find({"case_id": case_id}, {"_id": 0, "file_data": 0}).to_list(500)
    timeline = await db.timeline_events.find({"case_id": case_id}, {"_id": 0}).sort("event_date", 1).to_list(500)
    notes = await db.notes.find({"case_id": case_id}, {"_id": 0}).to_list(500)
    offence_category = case.get('offence_category', 'homicide')
    offence_context = get_offence_context(case)
    context = f"""
CRIMINAL APPEAL CASE ANALYSIS

CASE DETAILS:
- Title: {case.get('title', 'Unknown')}
- Defendant: {case.get('defendant_name', 'Unknown')}
- Case Number: {case.get('case_number', 'N/A')}
- Court: {case.get('court', 'N/A')}
- Judge: {case.get('judge', 'N/A')}
- Summary: {case.get('summary', 'No summary provided')}

{offence_context}
"""
    doc_context = build_document_context(documents, per_doc_char_limit=2200, total_char_budget=20000, include_description=True, content_heading="CONTENT")
    if existing_grounds:
        context += f"=== ALREADY IDENTIFIED GROUNDS ({len(existing_grounds)}) ===\n"
        context += "DO NOT re-identify these grounds. Only identify NEW grounds not listed here:\n\n"
        for g in existing_grounds:
            context += f"- [{g.get('ground_type')}] {g.get('title')}\n"
            context += f"  Status: {g.get('status')}, Strength: {g.get('strength')}\n"
        context += "\n"
    if documents:
        context += f"=== CASE DOCUMENTS ({doc_context['included_docs']} included / {len(documents)} total files) ===\n\n"
        context += doc_context["text"] + "\n"
        if doc_context["omitted_docs"] > 0:
            context += f"[Note: {doc_context['omitted_docs']} document(s) omitted from prompt for speed optimisation.]\n\n"
    else:
        context += "NO DOCUMENTS UPLOADED YET - Analysis based on case summary only.\n\n"
    if timeline:
        timeline_limit = 120
        timeline_slice = timeline[:timeline_limit]
        context += f"=== TIMELINE OF EVENTS ({len(timeline_slice)} included / {len(timeline)} total events) ===\n"
        for event in timeline_slice:
            context += f"- {event.get('event_date', 'Unknown date')} [{event.get('event_type', 'event')}]: {event.get('title')}\n"
            if event.get('description'):
                context += f"  Details: {event.get('description')}\n"
        if len(timeline) > timeline_limit:
            context += f"[... {len(timeline) - timeline_limit} additional events omitted for speed ...]\n"
        context += "\n"
    if notes:
        notes_limit = 80
        notes_slice = notes[:notes_limit]
        context += f"=== LEGAL NOTES & OBSERVATIONS ({len(notes_slice)} included / {len(notes)} total notes) ===\n"
        for note in notes_slice:
            context += f"- [{note.get('category', 'general')}] {note.get('title')}:\n"
            context += f"  {note.get('content', '')[:300]}\n"
        if len(notes) > notes_limit:
            context += f"[... {len(notes) - notes_limit} additional notes omitted for speed ...]\n"
        context += "\n"
    base_system_prompt = get_offence_system_prompt(offence_category, case.get('state', ''))
    system_prompt = f"""{base_system_prompt}

YOUR TASK: Conduct a thorough analysis of ALL provided case documents to identify potential grounds of appeal.

IMPORTANT: If grounds are listed in "ALREADY IDENTIFIED GROUNDS", do NOT duplicate them. Only add NEW grounds.

NOTE ON DOCUMENT COVERAGE: The analysis is based on the document excerpts provided. Not all documents may be included in full. Where documents have been truncated or omitted, this is noted. Do not overstate confidence where document coverage is incomplete.

Return your analysis in this JSON format:
{{
  "grounds": [
    {{
      "title": "Specific, descriptive title",
      "ground_type": "procedural_error|fresh_evidence|miscarriage_of_justice|sentencing_error|judicial_error|ineffective_counsel|prosecution_misconduct|jury_irregularity|constitutional_violation|other",
      "description": "DETAILED description (at least 3-4 sentences) explaining the ground, citing specific evidence from the documents. Use conditional language: 'It is arguable that...' / 'The material suggests...'",
      "strength": "strong|moderate|weak",
      "key_evidence": ["Specific document references and quotes that support this ground"],
      "relevant_law": ["Specific law sections e.g., 's.18 Crimes Act 1900 (NSW)', 'Evidence Act 1995 s.137'"]
    }}
  ],
  "summary": "Overall assessment of identified issues requiring further legal review",
  "analysis_notes": "Any additional observations about the case, including gaps in available material"
}}

ANALYTICAL DISCIPLINE:
- Identify potential grounds supported by the supplied material
- Use conditional language for all conclusions
- Do NOT state that an appeal will succeed or is likely to succeed
- Flag where evidence is incomplete or further investigation needed
- Do NOT invent case citations"""
    user_prompt = f"""CONDUCT A STRUCTURED LEGAL ANALYSIS OF THIS CRIMINAL APPEAL CASE:

{context}

INSTRUCTIONS:
1. Analyse the document excerpts provided — note that some may be truncated
2. Compare witness statements for inconsistencies where available
3. Identify any procedural irregularities suggested by the material
4. Look for evidence that may have been improperly handled or excluded
5. Consider whether the defence appears to have been adequate
6. Check for any fresh evidence possibilities
7. Assess whether the verdict appears safe on the available material
8. Use conditional language for all conclusions

For EACH ground you identify, cite the specific documentary evidence that supports it."""
    try:
        response = await call_llm_with_fallback(system_prompt, user_prompt, f"auto_identify_{case_id}_{uuid.uuid4().hex[:8]}")
    except Exception as e:
        logger.error(f"Auto-identify LLM failed: {e}")
        raise HTTPException(status_code=500, detail=f"AI analysis failed after retries: {str(e)}")

    def is_duplicate_ground(new_title, new_type, existing_grounds_list):
        new_title_lower = new_title.lower().strip()
        new_type_lower = new_type.lower().strip()
        for existing in existing_grounds_list:
            existing_title = existing.get('title', '').lower().strip()
            existing_type = existing.get('ground_type', '').lower().strip()
            if existing_type == new_type_lower:
                new_words = set(new_title_lower.split())
                existing_words = set(existing_title.split())
                common_words = new_words & existing_words
                stop_words = {'the', 'a', 'an', 'of', 'in', 'to', 'for', 'and', 'or', 'at', 'by', 'on', 'with'}
                common_meaningful = common_words - stop_words
                new_meaningful = new_words - stop_words
                if len(new_meaningful) > 0:
                    overlap_ratio = len(common_meaningful) / len(new_meaningful)
                    if overlap_ratio > 0.5:
                        return True
            if new_title_lower == existing_title:
                return True
        return False

    identified_grounds = []
    skipped_duplicates = 0
    try:
        json_match = re.search(r'\{[\s\S]*"grounds"[\s\S]*\}', response)
        if json_match:
            parsed = json.loads(json_match.group())
            grounds_data = parsed.get("grounds", [])
            for g in grounds_data:
                new_title = str(g.get("title", "Identified Ground") or "Identified Ground")
                raw_type = g.get("ground_type", "other")
                new_type = validate_ground_type(raw_type)
                if is_duplicate_ground(new_title, new_type, existing_grounds + identified_grounds):
                    skipped_duplicates += 1
                    continue
                # Normalise key_evidence to list of strings
                raw_evidence = g.get("key_evidence") or []
                if isinstance(raw_evidence, str):
                    raw_evidence = [raw_evidence]
                evidence_list = [str(e) for e in raw_evidence if e]
                # Calculate legitimacy score — overrides AI-guessed strength
                scored = calculate_ground_rating({
                    "ground_type": new_type,
                    "supporting_evidence": [{"quote": q} for q in evidence_list]
                })
                ground = GroundOfMerit(
                    case_id=case_id, user_id=user.user_id,
                    title=new_title, ground_type=new_type,
                    description=str(g.get("description", "") or ""),
                    strength=scored["rating"],  # Legitimacy engine rating, not AI guess
                    supporting_evidence=evidence_list,
                    status="identified"
                )
                ground_dict = ground.model_dump()
                ground_dict["created_at"] = ground_dict["created_at"].isoformat()
                ground_dict["updated_at"] = ground_dict["updated_at"].isoformat()
                ground_dict["legitimacy_scores"] = scored
                await db.grounds_of_merit.insert_one(ground_dict)
                created_ground = await db.grounds_of_merit.find_one({"ground_id": ground.ground_id}, {"_id": 0})
                identified_grounds.append(created_ground)
    except Exception as e:
        logger.error(f"Failed to parse AI response: {e}")
        if len(identified_grounds) == 0:
            # Fallback — mark as needs_review, not moderate
            ground = GroundOfMerit(
                case_id=case_id, user_id=user.user_id,
                title="AI Analysis — Review Required", ground_type="other",
                description="The AI analysis produced results that require manual review. See raw analysis below.",
                strength="weak", analysis=response, status="needs_review"
            )
            ground_dict = ground.model_dump()
            ground_dict["created_at"] = ground_dict["created_at"].isoformat()
            ground_dict["updated_at"] = ground_dict["updated_at"].isoformat()
            ground_dict["legitimacy_scores"] = {
                "legal_score": 1, "evidence_score": 0, "viability_score": 0,
                "total_score": 1, "rating": "weak",
                "confidence_note": "AI output could not be parsed into structured grounds — manual review required"
            }
            await db.grounds_of_merit.insert_one(ground_dict)
            created_ground = await db.grounds_of_merit.find_one({"ground_id": ground.ground_id}, {"_id": 0})
            identified_grounds.append(created_ground)
    await db.cases.update_one({"case_id": case_id}, {"$set": {"updated_at": datetime.now(timezone.utc).isoformat()}})
    return {
        "identified_count": len(identified_grounds), "skipped_duplicates": skipped_duplicates,
        "existing_grounds": len(existing_grounds),
        "message": f"Found {len(identified_grounds)} new grounds. Skipped {skipped_duplicates} duplicates." if skipped_duplicates > 0 else f"Found {len(identified_grounds)} new grounds.",
        "unlock_required": True, "unlock_price": FEATURE_PRICES["grounds_of_merit"]["price"]
    }
