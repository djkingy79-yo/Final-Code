# DO NOT UNDO — pipeline router. All endpoints in this file are approved and must be preserved.
"""
Criminal Appeal AI - Staged Pipeline Router
Extract → Classify → Verify → Project → Draft

ADDITIVE: Does not remove any existing route, feature, or collection.
"""
from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel
from datetime import datetime, timezone
import uuid
import logging

from config import db
from auth_utils import get_current_user
from services.llm_service import call_llm_for_json
from services.pipeline.verify import verify_issue as pipeline_verify_issue
from services.pipeline.argue import build_issue_argument
from services.pipeline.submit import build_submissions_draft

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/cases", tags=["pipeline"])


class VerifyBatchRequest(BaseModel):
    limit: int = 3


# ============================================================================
# HELPERS
# ============================================================================

def _issue_priority_rank(issue: dict) -> tuple:
    """Lower tuple sorts earlier."""
    preferred_ground_order = {
        "judicial_error": 0,
        "procedural_error": 1,
        "miscarriage_of_justice": 2,
        "fresh_evidence": 3,
        "sentencing_error": 4,
        "jury_irregularity": 5,
        "ineffective_counsel": 6,
        "prosecution_misconduct": 7,
        "constitutional_violation": 8,
        "other": 9,
    }
    confidence_order = {
        "strong": 0,
        "moderate": 1,
        "weak": 2,
    }
    return (
        preferred_ground_order.get(issue.get("ground_type", "other"), 9),
        confidence_order.get(issue.get("classification_confidence", "moderate"), 1),
        str(issue.get("title", "")).lower(),
    )


async def _sync_pipeline_projection_to_grounds(case_id: str, user_id: str) -> int:
    """Project staged issues/verifications into grounds_of_merit.

    DO_NOT_UNDO — MUST use fuzzy dedup via is_ground_duplicate(). NEVER revert to exact-title
    upsert. Exact-title upsert was the ROOT CAUSE of grounds multiplying from 4 to 27+.
    """
    from services.ground_dedup import is_ground_duplicate, normalise_au_spelling

    issues = await db.issue_classifications.find(
        {"case_id": case_id, "user_id": user_id}, {"_id": 0}
    ).to_list(500)

    # Pre-load existing grounds for fuzzy matching
    all_existing_grounds = await db.grounds_of_merit.find(
        {"case_id": case_id, "user_id": user_id},
        {"_id": 0, "ground_id": 1, "title": 1},
    ).to_list(200)

    synced = 0
    for issue in issues:
        verification = await db.issue_verifications.find_one(
            {"case_id": case_id, "issue_id": issue["issue_id"], "user_id": user_id}, {"_id": 0}
        )
        issue_title = normalise_au_spelling((issue.get("title") or "").strip())

        # Fuzzy match against all existing grounds
        existing_ground = None
        for eg in all_existing_grounds:
            eg_title = (eg.get("title") or "").strip()
            if is_ground_duplicate(issue_title, eg_title):
                existing_ground = eg
                break

        ground_doc = {
            "case_id": case_id,
            "user_id": user_id,
            "title": existing_ground["title"] if existing_ground else issue_title,
            "ground_type": issue.get("ground_type", "other"),
            "description": issue.get("description", ""),
            "strength": (verification or {}).get("legitimacy_scores", {}).get(
                "rating", issue.get("classification_confidence", "moderate")
            ),
            "status": "investigated" if verification else "identified",
            "supporting_evidence": (verification or {}).get("supporting_items", []),
            "law_sections": (verification or {}).get("law_sections", []),
            "similar_cases": (verification or {}).get("similar_cases", []),
            "legitimacy_scores": (verification or {}).get("legitimacy_scores", {}),
            "source_mode": "derived",
            "requires_human_review": (verification or {}).get("requires_human_review", True),
            "verification_status": (verification or {}).get("verification_status", "unverified"),
            "updated_at": datetime.now(timezone.utc).isoformat(),
        }

        if existing_ground:
            await db.grounds_of_merit.update_one(
                {"ground_id": existing_ground["ground_id"]},
                {"$set": ground_doc},
            )
        else:
            ground_doc["ground_id"] = f"gnd_{uuid.uuid4().hex[:12]}"
            ground_doc["created_at"] = datetime.now(timezone.utc).isoformat()
            await db.grounds_of_merit.insert_one(ground_doc)
            all_existing_grounds.append({"ground_id": ground_doc["ground_id"], "title": issue_title})

        synced += 1
    return synced

def _gen_id(prefix: str) -> str:
    return f"{prefix}_{uuid.uuid4().hex[:12]}"


async def _require_case_ownership(case_id: str, user_id: str):
    case = await db.cases.find_one({"case_id": case_id, "user_id": user_id}, {"_id": 0, "case_id": 1})
    if not case:
        raise HTTPException(status_code=404, detail="Case not found or access denied")
    return case


# ============================================================================
# STAGE 1 — EXTRACT
# ============================================================================

@router.post("/{case_id}/documents/{document_id}/extract")
async def extract_document(case_id: str, document_id: str, request: Request):
    """Per-document structured extraction: facts, events, findings."""
    user = await get_current_user(request)
    await _require_case_ownership(case_id, user.user_id)

    doc = await db.documents.find_one(
        {"document_id": document_id, "case_id": case_id, "user_id": user.user_id},
        {"_id": 0}
    )
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")

    content_text = doc.get("content_text") or ""
    if len(content_text.strip()) < 50:
        raise HTTPException(status_code=400, detail="Document has insufficient text for extraction. Upload a document with readable text content.")

    filename = doc.get("filename", "unknown")
    category = doc.get("category", "other")

    # Check for existing extract to refresh
    existing = await db.document_extracts.find_one(
        {"document_id": document_id, "case_id": case_id},
        {"_id": 0, "extract_id": 1}
    )
    extract_id = existing["extract_id"] if existing else _gen_id("ext")

    # Build extraction prompt
    extract_prompt = f"""Analyse the following legal document and extract structured information.
Return ONLY valid JSON with no markdown or explanation.

Document filename: {filename}
Document category: {category}

Return this exact JSON structure:
{{
  "facts": [
    {{
      "type": "<sentence_detail|offence_detail|procedural_fact|witness_evidence|judicial_finding|mitigation|aggravation|general>",
      "text": "<clear factual statement>",
      "quote": "<exact quote from document if available>",
      "page_reference": "<page reference if determinable, else null>",
      "confidence": "<strong|moderate|weak>"
    }}
  ],
  "events": [
    {{
      "title": "<event title>",
      "event_date": "<ISO date if determinable, else null>",
      "event_type": "<arrest|charge|hearing|trial|verdict|sentence|appeal|other>",
      "event_category": "<procedural|evidentiary|substantive>",
      "quote": "<supporting quote if available>",
      "page_reference": "<page reference if determinable>"
    }}
  ],
  "findings": [
    {{
      "type": "<judicial_finding|sentencing_remark|legal_ruling|evidentiary_ruling|general>",
      "text": "<clear statement of the finding>",
      "quote": "<exact quote from document>",
      "page_reference": "<page reference if determinable>"
    }}
  ]
}}

Rules:
- Extract ONLY what is explicitly supported by the document text.
- Do NOT classify appeal grounds at this stage.
- Do NOT invent or infer facts not present in the text.
- If a field cannot be determined, set to null.
- Include all significant facts, events, and findings.

DOCUMENT TEXT:
{content_text[:40000]}"""

    system_prompt = "You are a legal document extraction specialist. Extract only what is explicitly supported by the document. Return valid JSON only. Do not classify appeal grounds."

    def _validate_extract(parsed):
        return isinstance(parsed.get("facts"), list) and isinstance(parsed.get("events"), list)

    result = await call_llm_for_json(
        system_prompt=system_prompt,
        user_prompt=extract_prompt,
        session_id=f"extract_{case_id}_{document_id}",
        task_type="document_extraction",
        validation_fn=_validate_extract,
    )

    # Assign IDs to extracted items
    facts = []
    for f in result.get("facts", []):
        facts.append({
            "fact_id": _gen_id("fact"),
            "type": f.get("type", "general"),
            "text": f.get("text", ""),
            "quote": f.get("quote"),
            "page_reference": f.get("page_reference"),
            "confidence": f.get("confidence", "moderate"),
        })

    events = []
    for e in result.get("events", []):
        events.append({
            "event_id": _gen_id("evt"),
            "title": e.get("title", ""),
            "event_date": e.get("event_date"),
            "event_type": e.get("event_type"),
            "event_category": e.get("event_category", "procedural"),
            "quote": e.get("quote"),
            "page_reference": e.get("page_reference"),
        })

    findings = []
    for f in result.get("findings", []):
        findings.append({
            "finding_id": _gen_id("find"),
            "type": f.get("type", "general"),
            "text": f.get("text", ""),
            "quote": f.get("quote"),
            "page_reference": f.get("page_reference"),
        })

    extract_doc = {
        "extract_id": extract_id,
        "case_id": case_id,
        "user_id": user.user_id,
        "document_id": document_id,
        "filename": filename,
        "document_category": category,
        "stage": "extract",
        "status": "completed",
        "source_mode": "ai_generated",
        "verification_status": "unverified",
        "model_metadata": {
            "generated_by_model": "gpt-4o",
            "fallback_used": False,
        },
        "facts": facts,
        "events": events,
        "findings": findings,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }

    await db.document_extracts.replace_one(
        {"extract_id": extract_id},
        extract_doc,
        upsert=True,
    )

    logger.info(f"Document extraction completed: {extract_id} — {len(facts)} facts, {len(events)} events, {len(findings)} findings")

    return {
        "extract_id": extract_id,
        "status": "completed",
        "facts_count": len(facts),
        "events_count": len(events),
        "findings_count": len(findings),
    }


@router.post("/{case_id}/extract/refresh")
async def refresh_case_extract(case_id: str, request: Request):
    """Rebuild case-level merged extract from all document extracts."""
    user = await get_current_user(request)
    await _require_case_ownership(case_id, user.user_id)

    # Gather all completed document extracts
    doc_extracts = await db.document_extracts.find(
        {"case_id": case_id, "user_id": user.user_id, "status": "completed"},
        {"_id": 0},
    ).to_list(length=500)

    if not doc_extracts:
        raise HTTPException(status_code=400, detail="No completed document extractions found. Extract documents first.")

    # Merge facts, events, findings
    merged_facts = []
    merged_events = []
    merged_findings = []
    extract_ids = []

    seen_event_titles = set()

    for ext in doc_extracts:
        extract_ids.append(ext["extract_id"])
        for f in ext.get("facts", []):
            f["source_extract_id"] = ext["extract_id"]
            f["source_filename"] = ext.get("filename", "")
            merged_facts.append(f)
        for e in ext.get("events", []):
            # Dedupe events by title
            title_key = (e.get("title", "").lower().strip(), e.get("event_date", ""))
            if title_key not in seen_event_titles:
                seen_event_titles.add(title_key)
                e["source_extract_id"] = ext["extract_id"]
                e["source_filename"] = ext.get("filename", "")
                merged_events.append(e)
        for f in ext.get("findings", []):
            f["source_extract_id"] = ext["extract_id"]
            f["source_filename"] = ext.get("filename", "")
            merged_findings.append(f)

    # Infer case metadata conservatively from extracts
    case = await db.cases.find_one({"case_id": case_id}, {"_id": 0})
    inferred_metadata = {
        "state": case.get("state", "nsw"),
        "offence_category": case.get("offence_category", "homicide"),
        "offence_type": case.get("offence_type"),
        "sentence": case.get("sentence"),
        "court": case.get("court"),
        "classification_source": case.get("classification_source", "default"),
    }

    # Check for existing case extract
    existing = await db.case_extracts.find_one(
        {"case_id": case_id, "user_id": user.user_id},
        {"_id": 0, "case_extract_id": 1},
    )
    case_extract_id = existing["case_extract_id"] if existing else _gen_id("cex")

    case_extract_doc = {
        "case_extract_id": case_extract_id,
        "case_id": case_id,
        "user_id": user.user_id,
        "stage": "extract",
        "status": "completed",
        "metadata": inferred_metadata,
        "merged_facts": merged_facts,
        "merged_events": merged_events,
        "merged_findings": merged_findings,
        "document_extract_ids": extract_ids,
        "verification_status": "unverified",
        "created_at": datetime.now(timezone.utc).isoformat(),
    }

    await db.case_extracts.replace_one(
        {"case_extract_id": case_extract_id},
        case_extract_doc,
        upsert=True,
    )

    logger.info(f"Case extract refreshed: {case_extract_id} — {len(merged_facts)} facts, {len(merged_events)} events, {len(merged_findings)} findings from {len(extract_ids)} documents")

    return {
        "case_extract_id": case_extract_id,
        "status": "completed",
        "document_extracts_used": len(extract_ids),
        "merged_facts_count": len(merged_facts),
        "merged_events_count": len(merged_events),
        "merged_findings_count": len(merged_findings),
    }


@router.get("/{case_id}/extract")
async def get_case_extract(case_id: str, request: Request):
    """View merged case-level extraction."""
    user = await get_current_user(request)
    await _require_case_ownership(case_id, user.user_id)

    case_extract = await db.case_extracts.find_one(
        {"case_id": case_id, "user_id": user.user_id},
        {"_id": 0},
    )
    if not case_extract:
        return {"status": "not_extracted", "message": "No case extraction found. Run document extraction first."}

    return case_extract


# ============================================================================
# STAGE 2 — CLASSIFY
# ============================================================================

@router.post("/{case_id}/issues/classify")
async def classify_issues(case_id: str, request: Request):
    """Classify extracted facts into candidate appeal issues."""
    user = await get_current_user(request)
    await _require_case_ownership(case_id, user.user_id)

    case_extract = await db.case_extracts.find_one(
        {"case_id": case_id, "user_id": user.user_id, "status": "completed"},
        {"_id": 0},
    )
    if not case_extract:
        raise HTTPException(status_code=400, detail="No completed case extraction found. Run extract/refresh first.")

    case = await db.cases.find_one({"case_id": case_id}, {"_id": 0})
    state = case.get("state", "nsw")
    offence_cat = case.get("offence_category", "homicide")

    # Build classification prompt
    facts_text = "\n".join([
        f"[{f.get('fact_id', '')}] ({f.get('type', 'general')}) {f.get('text', '')}"
        for f in case_extract.get("merged_facts", [])
    ])
    events_text = "\n".join([
        f"[{e.get('event_id', '')}] {e.get('title', '')} ({e.get('event_date', 'unknown date')})"
        for e in case_extract.get("merged_events", [])
    ])
    findings_text = "\n".join([
        f"[{f.get('finding_id', '')}] ({f.get('type', 'general')}) {f.get('text', '')}"
        for f in case_extract.get("merged_findings", [])
    ])

    classify_prompt = f"""Based on the extracted record below, classify possible appellate issues.

Jurisdiction: {state.upper()}
Offence category: {offence_cat}
Offence type: {case.get('offence_type', 'Not specified')}

EXTRACTED FACTS:
{facts_text[:15000]}

EXTRACTED EVENTS:
{events_text[:5000]}

EXTRACTED FINDINGS:
{findings_text[:10000]}

Return ONLY valid JSON:
{{
  "issues": [
    {{
      "title": "<concise issue title>",
      "ground_type": "<procedural_error|fresh_evidence|miscarriage_of_justice|sentencing_error|judicial_error|ineffective_counsel|prosecution_misconduct|jury_irregularity|constitutional_violation|other>",
      "description": "<2-3 sentence description of the possible issue>",
      "linked_fact_ids": ["fact_xxx", "fact_yyy"],
      "linked_event_ids": ["evt_xxx"],
      "linked_finding_ids": ["find_xxx"],
      "classification_confidence": "<strong|moderate|weak>"
    }}
  ]
}}

Rules:
- Use conditional language (possible issue, potential ground, may warrant).
- Do NOT verify or draft final conclusions at this stage.
- Link each issue to specific extracted fact/event/finding IDs.
- ground_type MUST be from the listed values.
- Only classify issues genuinely supported by the extracted record."""

    system_prompt = "You are a legal issue classifier for criminal appeals. Classify possible appellate issues from the extracted record. Use conditional language. Do not verify or draft final conclusions. Return valid JSON only."

    def _validate_classify(parsed):
        return isinstance(parsed.get("issues"), list)

    result = await call_llm_for_json(
        system_prompt=system_prompt,
        user_prompt=classify_prompt,
        session_id=f"classify_{case_id}",
        task_type="issue_classification",
        validation_fn=_validate_classify,
    )

    issues = []
    for raw_issue in result.get("issues", []):
        issue_id = _gen_id("iss")
        issue_doc = {
            "issue_id": issue_id,
            "case_id": case_id,
            "user_id": user.user_id,
            "stage": "classify",
            "status": "identified",
            "title": raw_issue.get("title", "Untitled issue"),
            "ground_type": raw_issue.get("ground_type", "other"),
            "description": raw_issue.get("description", ""),
            "linked_fact_ids": raw_issue.get("linked_fact_ids", []),
            "linked_event_ids": raw_issue.get("linked_event_ids", []),
            "linked_finding_ids": raw_issue.get("linked_finding_ids", []),
            "classification_confidence": raw_issue.get("classification_confidence", "moderate"),
            "jurisdiction": state,
            "source_mode": "ai_generated",
            "verification_status": "unverified",
            "created_at": datetime.now(timezone.utc).isoformat(),
        }
        issues.append(issue_doc)

    # Replace all existing classifications for this case
    await db.issue_classifications.delete_many({"case_id": case_id, "user_id": user.user_id})
    if issues:
        await db.issue_classifications.insert_many(issues)

    logger.info(f"Issue classification completed for {case_id}: {len(issues)} issues identified")

    return {
        "identified_count": len(issues),
        "issues": [
            {
                "issue_id": i["issue_id"],
                "title": i["title"],
                "ground_type": i["ground_type"],
                "classification_confidence": i["classification_confidence"],
            }
            for i in issues
        ],
    }


@router.get("/{case_id}/issues")
async def list_issues(case_id: str, request: Request):
    """List classified issues for a case."""
    user = await get_current_user(request)
    await _require_case_ownership(case_id, user.user_id)

    issues = await db.issue_classifications.find(
        {"case_id": case_id, "user_id": user.user_id},
        {"_id": 0},
    ).sort("created_at", -1).to_list(length=100)

    # Attach verification status if exists
    for issue in issues:
        verification = await db.issue_verifications.find_one(
            {"issue_id": issue["issue_id"], "case_id": case_id},
            {"_id": 0, "verification_status": 1, "legitimacy_scores": 1},
        )
        if verification:
            issue["has_verification"] = True
            issue["verified_status"] = verification.get("verification_status", "unverified")
            issue["verified_rating"] = verification.get("legitimacy_scores", {}).get("rating")
        else:
            issue["has_verification"] = False

    return {"count": len(issues), "issues": issues}


# ============================================================================
# STAGE 3 — VERIFY
# ============================================================================

@router.post("/{case_id}/issues/{issue_id}/verify")
async def verify_issue(case_id: str, issue_id: str, request: Request):
    """Verify a single classified issue against the extracted record."""
    user = await get_current_user(request)
    await _require_case_ownership(case_id, user.user_id)

    issue = await db.issue_classifications.find_one(
        {"issue_id": issue_id, "case_id": case_id, "user_id": user.user_id},
        {"_id": 0},
    )
    if not issue:
        raise HTTPException(status_code=404, detail="Issue not found")

    # Gather source material
    case_extract = await db.case_extracts.find_one(
        {"case_id": case_id, "user_id": user.user_id},
        {"_id": 0},
    )

    linked_facts = []
    linked_findings = []
    if case_extract:
        fact_map = {f.get("fact_id"): f for f in case_extract.get("merged_facts", [])}
        finding_map = {f.get("finding_id"): f for f in case_extract.get("merged_findings", [])}
        for fid in issue.get("linked_fact_ids", []):
            if fid in fact_map:
                linked_facts.append(fact_map[fid])
        for fid in issue.get("linked_finding_ids", []):
            if fid in finding_map:
                linked_findings.append(finding_map[fid])

    facts_context = "\n".join([
        f"- ({f.get('type', '')}) {f.get('text', '')} [Quote: {f.get('quote', 'N/A')}] [Source: {f.get('source_filename', '')}]"
        for f in linked_facts
    ]) or "No linked facts available."

    findings_context = "\n".join([
        f"- ({f.get('type', '')}) {f.get('text', '')} [Quote: {f.get('quote', 'N/A')}]"
        for f in linked_findings
    ]) or "No linked findings available."

    case = await db.cases.find_one({"case_id": case_id}, {"_id": 0})
    state = case.get("state", "nsw")

    verify_prompt = f"""Assess the following identified appellate issue against the extracted record.

ISSUE: {issue.get('title', '')}
TYPE: {issue.get('ground_type', '')}
DESCRIPTION: {issue.get('description', '')}
JURISDICTION: {state.upper()}

LINKED FACTS:
{facts_context[:8000]}

LINKED FINDINGS:
{findings_context[:5000]}

Return ONLY valid JSON:
{{
  "supporting_items": [
    {{
      "filename": "<source document>",
      "quote": "<supporting quote>",
      "page_reference": "<page ref or null>",
      "role": "supports",
      "confidence": "<strong|moderate|weak>"
    }}
  ],
  "undermining_items": [
    {{
      "filename": "<source document>",
      "quote": "<quote that undermines the issue>",
      "page_reference": "<page ref or null>",
      "role": "undermines",
      "confidence": "<strong|moderate|weak>"
    }}
  ],
  "missing_items": [
    "<description of missing document or information>"
  ],
  "law_sections": [
    {{
      "act": "<Act name and jurisdiction>",
      "section": "<section number>",
      "title": "<section title if known>",
      "verification_status": "unverified"
    }}
  ],
  "similar_cases": [
    {{
      "case_name": "<case name>",
      "citation": "<citation or null>",
      "verification_status": "unverified"
    }}
  ],
  "overall_assessment": "<strong|moderate|weak>",
  "confidence_note": "<brief note on overall assessment>",
  "requires_human_review": true
}}

Rules:
- Assess ONLY against the supplied extracted record.
- Do NOT overstate the issue.
- Include both supporting AND undermining material honestly.
- List what is missing that would strengthen or weaken the issue.
- Law sections and similar cases are UNVERIFIED unless explicitly confirmed."""

    system_prompt = "You are a legal issue verification specialist for criminal appeals. Assess the identified issue against the extracted record. Return supporting, undermining, and missing material. Do not overstate the issue. Return valid JSON only."

    def _validate_verify(parsed):
        return isinstance(parsed.get("supporting_items"), list)

    result = await call_llm_for_json(
        system_prompt=system_prompt,
        user_prompt=verify_prompt,
        session_id=f"verify_{case_id}_{issue_id}",
        task_type="issue_verification",
        validation_fn=_validate_verify,
    )

    # Calculate legitimacy scores
    supporting_count = len(result.get("supporting_items", []))
    undermining_count = len(result.get("undermining_items", []))
    law_count = len(result.get("law_sections", []))

    legal_score = min(3, law_count)
    evidence_score = min(3, max(0, supporting_count - undermining_count))
    viability_map = {"strong": 3, "moderate": 2, "weak": 1}
    viability_score = viability_map.get(result.get("overall_assessment", "moderate"), 2)
    total_score = legal_score + evidence_score + viability_score
    rating = "strong" if total_score >= 7 else ("moderate" if total_score >= 4 else "weak")

    legitimacy_scores = {
        "legal_score": legal_score,
        "evidence_score": evidence_score,
        "viability_score": viability_score,
        "total_score": total_score,
        "rating": rating,
        "confidence_note": result.get("confidence_note", ""),
    }

    verification_id = _gen_id("ver")
    verification_doc = {
        "verification_id": verification_id,
        "issue_id": issue_id,
        "case_id": case_id,
        "user_id": user.user_id,
        "stage": "verify",
        "status": "completed",
        "supporting_items": result.get("supporting_items", []),
        "undermining_items": result.get("undermining_items", []),
        "missing_items": [
            {"description": m} if isinstance(m, str) else m
            for m in result.get("missing_items", [])
        ],
        "law_sections": result.get("law_sections", []),
        "similar_cases": result.get("similar_cases", []),
        "legitimacy_scores": legitimacy_scores,
        "verification_status": "reviewed",
        "requires_human_review": result.get("requires_human_review", True),
        "created_at": datetime.now(timezone.utc).isoformat(),
    }

    # Replace existing verification for this issue
    await db.issue_verifications.replace_one(
        {"issue_id": issue_id, "case_id": case_id},
        verification_doc,
        upsert=True,
    )

    # Update the issue classification status
    await db.issue_classifications.update_one(
        {"issue_id": issue_id},
        {"$set": {"status": "verified", "verification_status": "reviewed"}},
    )

    logger.info(f"Issue verification completed: {verification_id} — rating: {rating}")

    return {
        "verification_id": verification_id,
        "verification_status": "reviewed",
        "rating": rating,
        "legitimacy_scores": legitimacy_scores,
        "supporting_count": supporting_count,
        "undermining_count": undermining_count,
        "missing_count": len(result.get("missing_items", [])),
    }


@router.post("/{case_id}/issues/verify-all")
async def verify_all_issues(case_id: str, request: Request):
    """Batch verification of all classified issues."""
    user = await get_current_user(request)
    await _require_case_ownership(case_id, user.user_id)

    issues = await db.issue_classifications.find(
        {"case_id": case_id, "user_id": user.user_id},
        {"_id": 0, "issue_id": 1, "title": 1},
    ).to_list(length=50)

    if not issues:
        raise HTTPException(status_code=400, detail="No classified issues found. Run classification first.")

    results = []
    for issue in issues:
        try:
            # Build a minimal request-like object
            result = await verify_issue(case_id, issue["issue_id"], request)
            results.append({
                "issue_id": issue["issue_id"],
                "title": issue.get("title", ""),
                "status": "completed",
                "rating": result.get("rating"),
            })
        except Exception as e:
            logger.warning(f"Verification failed for {issue['issue_id']}: {e}")
            results.append({
                "issue_id": issue["issue_id"],
                "title": issue.get("title", ""),
                "status": "failed",
                "error": str(e)[:200],
            })

    return {
        "verified_count": sum(1 for r in results if r["status"] == "completed"),
        "failed_count": sum(1 for r in results if r["status"] == "failed"),
        "results": results,
    }


@router.get("/{case_id}/issues/{issue_id}/verification")
async def get_issue_verification(case_id: str, issue_id: str, request: Request):
    """Inspect verification result for a single issue."""
    user = await get_current_user(request)
    await _require_case_ownership(case_id, user.user_id)

    verification = await db.issue_verifications.find_one(
        {"issue_id": issue_id, "case_id": case_id, "user_id": user.user_id},
        {"_id": 0},
    )
    if not verification:
        return {"status": "not_verified", "message": "No verification found for this issue."}

    return verification


@router.post("/{case_id}/issues/verify-batch", response_model=dict)
async def verify_batch(case_id: str, payload: VerifyBatchRequest, request: Request):
    """Verify a batch of top unverified issues and sync the projection into grounds_of_merit."""
    user = await get_current_user(request)

    case = await db.cases.find_one(
        {"case_id": case_id, "user_id": user.user_id}, {"_id": 0}
    )
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")

    case_extract = await db.case_extracts.find_one(
        {"case_id": case_id, "user_id": user.user_id}, {"_id": 0}
    )
    if not case_extract:
        raise HTTPException(status_code=400, detail="Case extract not found. Run extraction first.")

    issues = await db.issue_classifications.find(
        {"case_id": case_id, "user_id": user.user_id}, {"_id": 0}
    ).to_list(500)
    if not issues:
        raise HTTPException(status_code=400, detail="No classified issues found. Run classification first.")

    eligible = []
    for issue in issues:
        existing_verification = await db.issue_verifications.find_one(
            {"case_id": case_id, "issue_id": issue["issue_id"], "user_id": user.user_id}, {"_id": 0}
        )
        if existing_verification:
            continue
        eligible.append(issue)

    eligible.sort(key=_issue_priority_rank)
    limit = max(1, min(int(payload.limit or 1), 20))
    selected_issues = eligible[:limit]

    supporting_context = {
        "facts": case_extract.get("merged_facts", []),
        "events": case_extract.get("merged_events", []),
        "findings": case_extract.get("merged_findings", []),
    }

    verified = 0
    failed = 0
    verified_issue_ids = []

    for issue in selected_issues:
        try:
            verification = await pipeline_verify_issue(case, issue, supporting_context)
            verification_dict = verification.model_dump()
            verification_dict["created_at"] = verification_dict["created_at"].isoformat()
            await db.issue_verifications.update_one(
                {"case_id": case_id, "issue_id": issue["issue_id"], "user_id": user.user_id},
                {"$set": verification_dict},
                upsert=True,
            )
            verified += 1
            verified_issue_ids.append(issue["issue_id"])
        except Exception as e:
            logger.warning(f"Batch verification failed for issue {issue.get('issue_id')}: {e}")
            failed += 1

    synced_count = await _sync_pipeline_projection_to_grounds(case_id, user.user_id)
    # DO_NOT_UNDO — 3 Apr 2026: cleanup after EVERY sync, no exceptions
    from services.ground_dedup import cleanup_duplicate_grounds
    await cleanup_duplicate_grounds(db, case_id, user.user_id)

    return {
        "requested_limit": payload.limit,
        "applied_limit": limit,
        "eligible_issues": len(eligible),
        "attempted": len(selected_issues),
        "verified": verified,
        "failed": failed,
        "verified_issue_ids": verified_issue_ids,
        "synced_count": synced_count,
        "message": (
            f"Attempted verification for {len(selected_issues)} issue(s); "
            f"verified {verified}, failed {failed}, synced {synced_count} projected ground(s)."
        ),
    }


# ============================================================================
# STAGE 3b — ARGUE (build structured appellate reasoning)
# ============================================================================

@router.post("/{case_id}/issues/{issue_id}/argue", response_model=dict)
async def argue_issue(case_id: str, issue_id: str, request: Request):
    """Build structured appellate reasoning from a verified issue."""
    user = await get_current_user(request)

    case = await db.cases.find_one(
        {"case_id": case_id, "user_id": user.user_id}, {"_id": 0}
    )
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")

    issue = await db.issue_classifications.find_one(
        {"case_id": case_id, "issue_id": issue_id, "user_id": user.user_id}, {"_id": 0}
    )
    if not issue:
        raise HTTPException(status_code=404, detail="Issue not found")

    verification = await db.issue_verifications.find_one(
        {"case_id": case_id, "issue_id": issue_id, "user_id": user.user_id}, {"_id": 0}
    )
    if not verification:
        raise HTTPException(status_code=400, detail="Issue verification not found. Verify the issue first.")

    argument = await build_issue_argument(case, issue, verification)

    argument_doc = {
        "argument_id": f"arg_{uuid.uuid4().hex[:12]}",
        "case_id": case_id,
        "issue_id": issue_id,
        "user_id": user.user_id,
        "stage": "argue",
        "status": "completed",
        **argument,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }

    await db.issue_arguments.update_one(
        {"case_id": case_id, "issue_id": issue_id, "user_id": user.user_id},
        {"$set": argument_doc},
        upsert=True,
    )

    return argument_doc


@router.post("/{case_id}/issues/argue-batch", response_model=dict)
async def argue_batch(case_id: str, request: Request):
    """Build structured arguments for all verified issues in the case."""
    user = await get_current_user(request)

    case = await db.cases.find_one(
        {"case_id": case_id, "user_id": user.user_id}, {"_id": 0}
    )
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")

    issues = await db.issue_classifications.find(
        {"case_id": case_id, "user_id": user.user_id}, {"_id": 0}
    ).to_list(500)

    verifications = await db.issue_verifications.find(
        {"case_id": case_id, "user_id": user.user_id}, {"_id": 0}
    ).to_list(500)

    verification_map = {v.get("issue_id"): v for v in verifications}

    attempted = 0
    completed = 0
    failed = 0

    for issue in issues:
        verification = verification_map.get(issue.get("issue_id"))
        if not verification:
            continue

        attempted += 1

        try:
            argument = await build_issue_argument(case, issue, verification)

            argument_doc = {
                "argument_id": f"arg_{uuid.uuid4().hex[:12]}",
                "case_id": case_id,
                "issue_id": issue["issue_id"],
                "user_id": user.user_id,
                "stage": "argue",
                "status": "completed",
                **argument,
                "created_at": datetime.now(timezone.utc).isoformat(),
            }

            await db.issue_arguments.update_one(
                {"case_id": case_id, "issue_id": issue["issue_id"], "user_id": user.user_id},
                {"$set": argument_doc},
                upsert=True,
            )

            completed += 1
        except Exception as e:
            logger.warning(f"Argument build failed for issue {issue.get('issue_id')}: {e}")
            failed += 1

    return {
        "attempted": attempted,
        "completed": completed,
        "failed": failed,
        "message": f"Attempted {attempted} issue arguments; completed {completed}, failed {failed}.",
    }


async def _load_case_pipeline_materials(case_id: str, user_id: str) -> dict:
    case_extract = await db.case_extracts.find_one(
        {"case_id": case_id, "user_id": user_id}, {"_id": 0}
    )

    issues = await db.issue_classifications.find(
        {"case_id": case_id, "user_id": user_id}, {"_id": 0}
    ).to_list(500)

    verifications = await db.issue_verifications.find(
        {"case_id": case_id, "user_id": user_id}, {"_id": 0}
    ).to_list(500)

    arguments = await db.issue_arguments.find(
        {"case_id": case_id, "user_id": user_id}, {"_id": 0}
    ).to_list(500)

    return {
        "case_extract": case_extract,
        "issues": issues,
        "verifications": verifications,
        "arguments": arguments,
    }


# ============================================================================
# STAGE 3c — SUBMISSIONS DRAFT
# ============================================================================

@router.post("/{case_id}/submissions-draft", response_model=dict)
async def build_case_submissions_draft(case_id: str, request: Request):
    """Build structured appellate submissions draft from staged pipeline artifacts."""
    user = await get_current_user(request)

    case = await db.cases.find_one(
        {"case_id": case_id, "user_id": user.user_id}, {"_id": 0}
    )
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")

    materials = await _load_case_pipeline_materials(case_id, user.user_id)

    if not materials["case_extract"]:
        raise HTTPException(status_code=400, detail="Case extract not found. Run extraction first.")
    if not materials["issues"]:
        raise HTTPException(status_code=400, detail="No classified issues found. Run classification first.")
    if not materials["verifications"]:
        raise HTTPException(status_code=400, detail="No verified issues found. Verify issues first.")
    if not materials["arguments"]:
        raise HTTPException(status_code=400, detail="No issue arguments found. Build arguments first.")

    draft = await build_submissions_draft(
        case=case,
        case_extract=materials["case_extract"],
        issues=materials["issues"],
        verifications=materials["verifications"],
        arguments=materials["arguments"],
    )

    draft_doc = {
        "submission_draft_id": f"sub_{uuid.uuid4().hex[:12]}",
        "case_id": case_id,
        "user_id": user.user_id,
        "stage": "submit",
        "status": "completed",
        **draft,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }

    await db.submissions_drafts.update_one(
        {"case_id": case_id, "user_id": user.user_id},
        {"$set": draft_doc},
        upsert=True,
    )

    return draft_doc


@router.get("/{case_id}/submissions-draft-view", response_model=dict)
async def get_case_submissions_draft(case_id: str, request: Request):
    """Get saved submissions draft for a case."""
    user = await get_current_user(request)

    case = await db.cases.find_one(
        {"case_id": case_id, "user_id": user.user_id}, {"_id": 0}
    )
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")

    draft = await db.submissions_drafts.find_one(
        {"case_id": case_id, "user_id": user.user_id}, {"_id": 0}
    )
    if not draft:
        raise HTTPException(status_code=404, detail="Submissions draft not found")

    return draft


# ============================================================================
# STAGE 4 — PROJECT TO GROUNDS
# ============================================================================

@router.post("/{case_id}/grounds/sync-from-issues")
async def sync_grounds_from_issues(case_id: str, request: Request):
    """Project classified + verified issues into grounds_of_merit."""
    user = await get_current_user(request)
    await _require_case_ownership(case_id, user.user_id)

    issues = await db.issue_classifications.find(
        {"case_id": case_id, "user_id": user.user_id},
        {"_id": 0},
    ).to_list(length=100)

    if not issues:
        raise HTTPException(status_code=400, detail="No classified issues found. Run classification first.")

    synced = []
    for issue in issues:
        # Look up verification if it exists
        verification = await db.issue_verifications.find_one(
            {"issue_id": issue["issue_id"], "case_id": case_id},
            {"_id": 0},
        )

        # Build ground from issue + verification
        ground_id = _gen_id("ground")

        # Build supporting_evidence from verification supporting items
        supporting_evidence = []
        if verification:
            for item in verification.get("supporting_items", []):
                supporting_evidence.append({
                    "filename": item.get("filename"),
                    "quote": item.get("quote", ""),
                    "page_reference": item.get("page_reference"),
                    "confidence": item.get("confidence", "moderate"),
                    "role": "supports",
                    "verification_status": "unverified",
                })

        # Build law_sections from verification
        law_sections = []
        if verification:
            for ls in verification.get("law_sections", []):
                law_sections.append({
                    "act": ls.get("act", ""),
                    "section": ls.get("section", ""),
                    "title": ls.get("title"),
                    "verification_status": ls.get("verification_status", "unverified"),
                })

        # Build similar_cases from verification
        similar_cases = []
        if verification:
            for sc in verification.get("similar_cases", []):
                similar_cases.append({
                    "case_name": sc.get("case_name", ""),
                    "citation": sc.get("citation"),
                    "verification_status": sc.get("verification_status", "unverified"),
                })

        # Legitimacy scores
        legitimacy_scores = None
        strength = "moderate"
        if verification and verification.get("legitimacy_scores"):
            legitimacy_scores = verification["legitimacy_scores"]
            strength = legitimacy_scores.get("rating", "moderate")

        ground_doc = {
            "ground_id": ground_id,
            "case_id": case_id,
            "user_id": user.user_id,
            "title": issue.get("title", ""),
            "description": issue.get("description", ""),
            "ground_type": issue.get("ground_type", "other"),
            "strength": strength,
            "status": "identified" if not verification else "investigated",
            "analysis": "",
            "supporting_evidence": supporting_evidence,
            "law_sections": law_sections,
            "similar_cases": similar_cases,
            "legitimacy_scores": legitimacy_scores,
            "source_mode": "ai_generated",
            "verification_status": verification.get("verification_status", "unverified") if verification else "unverified",
            "requires_human_review": verification.get("requires_human_review", True) if verification else True,
            "pipeline_source": {
                "issue_id": issue["issue_id"],
                "verification_id": verification["verification_id"] if verification else None,
                "synced_at": datetime.now(timezone.utc).isoformat(),
            },
            "created_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat(),
        }

        # DO_NOT_UNDO — Fuzzy ground deduplication. MUST use topic-based + fuzzy + bidirectional overlap.
        # First check: exact match by pipeline source issue_id
        existing = await db.grounds_of_merit.find_one(
            {"case_id": case_id, "user_id": user.user_id, "pipeline_source.issue_id": issue["issue_id"]},
            {"_id": 0, "ground_id": 1},
        )
        # Second check: topic + fuzzy title match to prevent duplicates with different wording
        if not existing:
            from services.ground_dedup import is_ground_duplicate
            issue_title = (issue.get("title") or "").strip()
            if issue_title:
                existing_grounds_cursor = db.grounds_of_merit.find(
                    {"case_id": case_id, "user_id": user.user_id},
                    {"_id": 0, "ground_id": 1, "title": 1},
                )
                async for eg in existing_grounds_cursor:
                    eg_title = (eg.get("title") or "").strip()
                    if is_ground_duplicate(issue_title, eg_title):
                        existing = eg
                        logger.info(f"Ground dedup match: '{issue_title}' ≈ '{eg_title}'")
                        break

        if existing:
            ground_doc["ground_id"] = existing["ground_id"]
            await db.grounds_of_merit.replace_one(
                {"ground_id": existing["ground_id"]},
                ground_doc,
            )
        else:
            await db.grounds_of_merit.insert_one(ground_doc)

        synced.append({
            "ground_id": ground_doc["ground_id"],
            "issue_id": issue["issue_id"],
            "title": issue.get("title", ""),
            "strength": strength,
            "has_verification": verification is not None,
        })

    logger.info(f"Synced {len(synced)} grounds from issues for case {case_id}")

    return {
        "synced_count": len(synced),
        "grounds": synced,
    }


# ============================================================================
# PIPELINE STATUS
# ============================================================================

@router.get("/{case_id}/pipeline/status")
async def get_pipeline_status(case_id: str, request: Request):
    """Get the current pipeline status for a case."""
    user = await get_current_user(request)
    await _require_case_ownership(case_id, user.user_id)

    # Count documents
    doc_count = await db.documents.count_documents({"case_id": case_id, "user_id": user.user_id})

    # Count document extracts
    extract_count = await db.document_extracts.count_documents(
        {"case_id": case_id, "user_id": user.user_id, "status": "completed"}
    )

    # Check case extract
    case_extract = await db.case_extracts.find_one(
        {"case_id": case_id, "user_id": user.user_id},
        {"_id": 0, "case_extract_id": 1, "status": 1},
    )

    # Count issues
    issue_count = await db.issue_classifications.count_documents(
        {"case_id": case_id, "user_id": user.user_id}
    )

    # Count verifications
    verification_count = await db.issue_verifications.count_documents(
        {"case_id": case_id, "user_id": user.user_id}
    )

    # Count grounds with pipeline source
    pipeline_ground_count = await db.grounds_of_merit.count_documents(
        {"case_id": case_id, "user_id": user.user_id, "pipeline_source": {"$exists": True}}
    )

    return {
        "case_id": case_id,
        "stages": {
            "extract": {
                "documents_total": doc_count,
                "documents_extracted": extract_count,
                "case_extract_ready": case_extract is not None and case_extract.get("status") == "completed",
            },
            "classify": {
                "issues_identified": issue_count,
            },
            "verify": {
                "issues_verified": verification_count,
                "issues_pending": max(0, issue_count - verification_count),
            },
            "project": {
                "grounds_synced": pipeline_ground_count,
            },
        },
    }



# ============================================================================
# BARRISTER ACCEPTANCE PACK
# ============================================================================

@router.get("/{case_id}/barrister-pack/generate")
async def generate_barrister_pack(case_id: str, request: Request):
    """Generate a Barrister Acceptance Pack as PDF.
    Contains: case summary, ranked grounds, timeline, evidence annexures, verification summary.
    """
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import mm
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, HRFlowable
    from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY
    from io import BytesIO
    from fastapi.responses import StreamingResponse

    user = await get_current_user(request)
    await _require_case_ownership(case_id, user.user_id)

    # Gather all data
    case = await db.cases.find_one({"case_id": case_id, "user_id": user.user_id}, {"_id": 0})
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")

    grounds = await db.grounds_of_merit.find(
        {"case_id": case_id, "user_id": user.user_id},
        {"_id": 0}
    ).sort("created_at", 1).to_list(100)

    timeline = await db.timeline_events.find(
        {"case_id": case_id, "user_id": user.user_id},
        {"_id": 0}
    ).sort("event_date", 1).to_list(200)

    verifications = await db.issue_verifications.find(
        {"case_id": case_id, "user_id": user.user_id},
        {"_id": 0}
    ).to_list(100)

    documents = await db.documents.find(
        {"case_id": case_id, "user_id": user.user_id},
        {"_id": 0, "document_id": 1, "filename": 1}
    ).to_list(200)

    # Build PDF
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer, pagesize=A4,
        rightMargin=20*mm, leftMargin=20*mm,
        topMargin=25*mm, bottomMargin=25*mm,
    )

    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name="PackTitle", fontName="Helvetica-Bold", fontSize=18, spaceAfter=6, textColor=colors.HexColor("#0f172a"), alignment=TA_CENTER))
    styles.add(ParagraphStyle(name="PackSubtitle", fontName="Helvetica", fontSize=10, spaceAfter=12, textColor=colors.HexColor("#64748b"), alignment=TA_CENTER))
    styles.add(ParagraphStyle(name="SectionHead", fontName="Helvetica-Bold", fontSize=13, spaceAfter=8, spaceBefore=16, textColor=colors.HexColor("#0f4c81")))
    styles.add(ParagraphStyle(name="SubHead", fontName="Helvetica-Bold", fontSize=11, spaceAfter=4, spaceBefore=10, textColor=colors.HexColor("#1e293b")))
    styles.add(ParagraphStyle(name="BodyText2", fontName="Helvetica", fontSize=9, spaceAfter=4, leading=13, alignment=TA_JUSTIFY))
    styles.add(ParagraphStyle(name="Small", fontName="Helvetica", fontSize=8, spaceAfter=2, textColor=colors.HexColor("#94a3b8")))
    styles.add(ParagraphStyle(name="Disclaimer", fontName="Helvetica-Oblique", fontSize=7, spaceAfter=4, textColor=colors.HexColor("#94a3b8"), alignment=TA_CENTER))

    elements = []

    # ── COVER PAGE ──
    elements.append(Spacer(1, 40*mm))
    elements.append(Paragraph("BARRISTER ACCEPTANCE PACK", styles["PackTitle"]))
    elements.append(Spacer(1, 4*mm))
    elements.append(Paragraph("Appeal Case Manager — Confidential Preparation Material", styles["PackSubtitle"]))
    elements.append(Spacer(1, 10*mm))

    cover_data = []
    if case.get("title"):
        cover_data.append(["Case Title", case["title"]])
    if case.get("defendant_name"):
        cover_data.append(["Defendant", case["defendant_name"]])
    if case.get("case_number"):
        cover_data.append(["Case Number", case["case_number"]])
    if case.get("court"):
        cover_data.append(["Court", case["court"]])
    if case.get("state"):
        cover_data.append(["Jurisdiction", str(case["state"]).upper()])
    if case.get("offence_category"):
        cover_data.append(["Offence Category", case["offence_category"].replace("_", " ").title()])
    if case.get("offence_type"):
        cover_data.append(["Offence Type", case["offence_type"]])
    if case.get("sentence"):
        cover_data.append(["Sentence", case["sentence"]])
    cover_data.append(["Generated", datetime.now(timezone.utc).strftime("%d %B %Y")])
    cover_data.append(["Documents", str(len(documents))])
    cover_data.append(["Grounds of Merit", str(len(grounds))])

    if cover_data:
        t = Table(cover_data, colWidths=[45*mm, 110*mm])
        t.setStyle(TableStyle([
            ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, -1), 9),
            ("TEXTCOLOR", (0, 0), (0, -1), colors.HexColor("#475569")),
            ("TEXTCOLOR", (1, 0), (1, -1), colors.HexColor("#0f172a")),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
            ("TOPPADDING", (0, 0), (-1, -1), 5),
            ("LINEBELOW", (0, 0), (-1, -2), 0.5, colors.HexColor("#e2e8f0")),
        ]))
        elements.append(t)

    elements.append(Spacer(1, 15*mm))
    elements.append(Paragraph("NOT LEGAL ADVICE — This document is AI-assisted preparation material for legal review. It does not constitute legal advice and should not be relied upon as a substitute for independent legal judgment.", styles["Disclaimer"]))
    elements.append(PageBreak())

    # ── SECTION 1: GROUNDS OF MERIT (RANKED) ──
    elements.append(Paragraph("1. Grounds of Merit", styles["SectionHead"]))
    elements.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#0f4c81")))
    elements.append(Spacer(1, 3*mm))

    if not grounds:
        elements.append(Paragraph("No grounds of merit have been identified for this case.", styles["BodyText2"]))
    else:
        # Sort by strength: strong first, then moderate, then weak
        strength_order = {"strong": 0, "moderate": 1, "weak": 2}
        sorted_grounds = sorted(grounds, key=lambda g: strength_order.get(g.get("strength", "moderate"), 1))

        for idx, g in enumerate(sorted_grounds, 1):
            strength = str(g.get("strength", "moderate")).upper()
            elements.append(Paragraph(f"Ground {idx}: {g.get('title', 'Untitled')}", styles["SubHead"]))

            # Strength and verification
            meta_parts = [f"<b>Strength:</b> {strength}"]
            vs = g.get("verification_status", "unverified")
            meta_parts.append(f"<b>Verification:</b> {vs}")
            gt = g.get("ground_type", "")
            if gt:
                meta_parts.append(f"<b>Type:</b> {gt.replace('_', ' ').title()}")
            elements.append(Paragraph(" &nbsp;|&nbsp; ".join(meta_parts), styles["Small"]))

            # Description
            desc = g.get("description", "")
            if desc:
                elements.append(Paragraph(desc, styles["BodyText2"]))

            # Legitimacy scores
            ls = g.get("legitimacy_scores")
            if ls:
                score_text = f"Legal basis: {ls.get('legal_score', 0)}/3 &nbsp;|&nbsp; Evidence support: {ls.get('evidence_score', 0)}/3 &nbsp;|&nbsp; Appellate viability: {ls.get('viability_score', 0)}/3 &nbsp;|&nbsp; <b>Total: {ls.get('total_score', 0)}/9</b>"
                elements.append(Paragraph(score_text, styles["Small"]))

            # Supporting evidence
            evidence = g.get("supporting_evidence", [])
            if evidence:
                elements.append(Paragraph(f"<b>Supporting Evidence ({len(evidence)}):</b>", styles["Small"]))
                for e in evidence[:3]:
                    quote = e.get("quote", e) if isinstance(e, dict) else str(e)
                    fname = e.get("filename", "") if isinstance(e, dict) else ""
                    prefix = f"{fname}: " if fname else ""
                    elements.append(Paragraph(f"&nbsp;&nbsp;&bull; {prefix}{quote[:200]}", styles["Small"]))

            # Law sections
            law = g.get("law_sections", [])
            if law:
                elements.append(Paragraph(f"<b>Legislation ({len(law)}):</b>", styles["Small"]))
                for law_item in law[:3]:
                    if isinstance(law_item, dict):
                        elements.append(Paragraph(f"&nbsp;&nbsp;&bull; {law_item.get('section', '')} {law_item.get('act', '')} {('— ' + law_item.get('title', '')) if law_item.get('title') else ''}", styles["Small"]))

            # Human review warning
            if g.get("requires_human_review"):
                elements.append(Paragraph("<b>Requires human review before filing or reliance in advice.</b>", styles["Small"]))

            elements.append(Spacer(1, 4*mm))

    elements.append(PageBreak())

    # ── SECTION 2: PROCEDURAL TIMELINE ──
    elements.append(Paragraph("2. Procedural Timeline", styles["SectionHead"]))
    elements.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#0f4c81")))
    elements.append(Spacer(1, 3*mm))

    if not timeline:
        elements.append(Paragraph("No timeline events recorded.", styles["BodyText2"]))
    else:
        tl_data = [["Date", "Event", "Category"]]
        for evt in timeline:
            date_str = str(evt.get("event_date", "Unknown"))[:10]
            tl_data.append([date_str, str(evt.get("title", ""))[:80], str(evt.get("event_category", evt.get("category", "")))[:30]])

        tl_table = Table(tl_data, colWidths=[25*mm, 100*mm, 35*mm])
        tl_table.setStyle(TableStyle([
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, -1), 8),
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#0f4c81")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ("TOPPADDING", (0, 0), (-1, -1), 4),
            ("LINEBELOW", (0, 0), (-1, -2), 0.5, colors.HexColor("#e2e8f0")),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f8fafc")]),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ]))
        elements.append(tl_table)

    elements.append(PageBreak())

    # ── SECTION 3: EVIDENCE ANNEXURES ──
    elements.append(Paragraph("3. Evidence Annexures", styles["SectionHead"]))
    elements.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#0f4c81")))
    elements.append(Spacer(1, 3*mm))

    if not verifications:
        elements.append(Paragraph("No verified evidence annexures available. Run the pipeline verification stage to populate.", styles["BodyText2"]))
    else:
        for ver in verifications:
            issue = await db.issue_classifications.find_one(
                {"issue_id": ver.get("issue_id"), "case_id": case_id},
                {"_id": 0, "title": 1}
            )
            issue_title = issue.get("title", "Unknown Issue") if issue else "Unknown Issue"
            elements.append(Paragraph(f"Issue: {issue_title}", styles["SubHead"]))

            # Supporting items
            for item in ver.get("supporting_items", [])[:5]:
                elements.append(Paragraph(f"&nbsp;&nbsp;<font color='#16a34a'>[SUPPORTS]</font> {item.get('filename', '')}: \"{item.get('quote', '')[:150]}\" (Confidence: {item.get('confidence', 'moderate')})", styles["Small"]))

            # Undermining items
            for item in ver.get("undermining_items", [])[:5]:
                elements.append(Paragraph(f"&nbsp;&nbsp;<font color='#dc2626'>[UNDERMINES]</font> {item.get('filename', '')}: \"{item.get('quote', '')[:150]}\" (Confidence: {item.get('confidence', 'moderate')})", styles["Small"]))

            # Missing items
            missing = ver.get("missing_items", [])
            if missing:
                elements.append(Paragraph(f"&nbsp;&nbsp;<font color='#d97706'>[MISSING]</font> {', '.join(str(m.get('description', m) if isinstance(m, dict) else m)[:80] for m in missing[:3])}", styles["Small"]))

            elements.append(Spacer(1, 3*mm))

    elements.append(PageBreak())

    # ── SECTION 4: VERIFICATION SUMMARY ──
    elements.append(Paragraph("4. Verification Summary", styles["SectionHead"]))
    elements.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#0f4c81")))
    elements.append(Spacer(1, 3*mm))

    verified_count = len([g for g in grounds if g.get("verification_status") in ("reviewed", "verified")])
    unverified_count = len([g for g in grounds if g.get("verification_status") not in ("reviewed", "verified")])
    human_review_count = len([g for g in grounds if g.get("requires_human_review")])

    summary_data = [
        ["Total grounds identified", str(len(grounds))],
        ["Verified/Reviewed grounds", str(verified_count)],
        ["Unverified grounds", str(unverified_count)],
        ["Grounds requiring human review", str(human_review_count)],
        ["Timeline events", str(len(timeline))],
        ["Documents on file", str(len(documents))],
        ["Issue verifications completed", str(len(verifications))],
    ]
    sum_table = Table(summary_data, colWidths=[80*mm, 40*mm])
    sum_table.setStyle(TableStyle([
        ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("LINEBELOW", (0, 0), (-1, -2), 0.5, colors.HexColor("#e2e8f0")),
    ]))
    elements.append(sum_table)

    elements.append(Spacer(1, 8*mm))

    # Document list
    elements.append(Paragraph("Documents on File", styles["SubHead"]))
    for d in documents:
        elements.append(Paragraph(f"&nbsp;&nbsp;&bull; {d.get('filename', 'Unknown')}", styles["Small"]))

    elements.append(Spacer(1, 10*mm))
    elements.append(Paragraph("NOT LEGAL ADVICE — AI-assisted preparation material for legal review. All grounds, authorities, and procedural issues should be independently verified before use in court or formal advice.", styles["Disclaimer"]))
    elements.append(Paragraph(f"Generated {datetime.now(timezone.utc).strftime('%d %B %Y %H:%M UTC')} by Appeal Case Manager", styles["Disclaimer"]))

    # Build PDF
    doc.build(elements)
    buffer.seek(0)

    defendant = case.get("defendant_name", "case").replace(" ", "_")
    filename = f"Barrister_Acceptance_Pack_{defendant}_{datetime.now(timezone.utc).strftime('%Y%m%d')}.pdf"

    return StreamingResponse(
        buffer,
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename={filename}"},
    )
