"""
Criminal Appeal AI - Documents Router (CRUD + OCR + Text Extraction)
Extracted from server.py monolith.
"""
from fastapi import APIRouter, HTTPException, Request, UploadFile, File, Form
from starlette.background import BackgroundTasks
from typing import List
from datetime import datetime, timezone
import base64
import uuid
import re
import os
import asyncio
import json
import logging

from config import db
from auth_utils import get_current_user
from models import Document, DocumentSearchRequest
from services.document_helpers import extract_text_with_ocr

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api", tags=["documents"])


# ==========================================================================
# DO NOT UNDO — AUTO-DETECT METADATA FUNCTION
# ==========================================================================
# This function auto-detects state, offence_category, offence_type,
# sentence, court, case_number from uploaded documents via LLM.
# It relies on CaseCreate having Optional[None] defaults (models/__init__.py).
# DO NOT remove this function. DO NOT skip calling it on upload.
# DO NOT hardcode "nsw" or "homicide" anywhere in models or routes.
# This has been broken and re-fixed 15+ times. LEAVE IT ALONE.
# ==========================================================================
async def _background_auto_detect_metadata(case_id: str, user_id: str, content_text: str, filename: str):
    """Background task: auto-detect case metadata from uploaded document via LLM"""
    try:
        from emergentintegrations.llm.chat import LlmChat, UserMessage
        case = await db.cases.find_one({"case_id": case_id, "user_id": user_id}, {"_id": 0})
        if not case:
            return
        if case.get('offence_type') and case.get('sentence') and case.get('offence_category') and case.get('offence_category') != 'homicide':
            return
        detect_prompt = f"""Analyse this criminal case document and extract metadata.
Return ONLY valid JSON (no markdown):
{{
  "offence_category": "<one of: homicide, assault, sexual_offences, robbery_theft, drug_offences, fraud_dishonesty, firearms_weapons, domestic_violence, public_order, terrorism, driving_offences>",
  "offence_type": "<specific offence e.g. Murder, Assault Occasioning ABH>",
  "sentence": "<exact sentence if stated, else null>",
  "state": "<one of: nsw, vic, qld, sa, wa, tas, nt, act>",
  "court": "<court name if found>",
  "case_number": "<case number if found>",
  "defendant_name": "<defendant full name if found>"
}}
Rules: Read the ACTUAL document. Do NOT default to homicide. If a field is unknown, set null. state must be lowercase.

DOCUMENT ({filename}):
{content_text[:20000]}"""
        detect_chat = LlmChat(
            api_key=os.environ.get("EMERGENT_LLM_KEY"),
            session_id=f"upload_detect_{case_id}",
            system_message="Extract factual metadata from Australian criminal case documents. Return only valid JSON."
        ).with_model("openai", "gpt-4o").with_params(max_tokens=2000)
        raw = await asyncio.wait_for(detect_chat.send_message(UserMessage(text=detect_prompt)), timeout=60)
        raw = (raw or "").strip()
        if raw.startswith("```"):
            raw = raw.split("\n", 1)[-1].rsplit("```", 1)[0].strip()
        meta = json.loads(raw)
        valid_cats = ["homicide","assault","sexual_offences","robbery_theft","drug_offences","fraud_dishonesty","firearms_weapons","domestic_violence","public_order","terrorism","driving_offences"]
        valid_sts = ["nsw","vic","qld","sa","wa","tas","nt","act"]
        update_fields = {}
        if meta.get("offence_category") in valid_cats:
            update_fields["offence_category"] = meta["offence_category"]
        if meta.get("offence_type"):
            update_fields["offence_type"] = meta["offence_type"]
        if meta.get("sentence"):
            update_fields["sentence"] = meta["sentence"]
        if meta.get("state") and meta["state"].lower() in valid_sts:
            update_fields["state"] = meta["state"].lower()
        if meta.get("court"):
            update_fields["court"] = meta["court"]
        if meta.get("case_number") and not case.get("case_number"):
            update_fields["case_number"] = meta["case_number"]
        if meta.get("defendant_name") and not case.get("defendant_name"):
            update_fields["defendant_name"] = meta["defendant_name"]
        if update_fields:
            update_fields["updated_at"] = datetime.now(timezone.utc).isoformat()
            await db.cases.update_one({"case_id": case_id}, {"$set": update_fields})
            logger.info(f"Background auto-detected metadata for {case_id}: {list(update_fields.keys())}")
    except Exception as e:
        logger.warning(f"Background auto-detect failed for {case_id}: {e}")


async def _background_auto_generate(case_id: str, user_id: str):
    """Background task: auto-generate timeline events + case summary from documents"""
    try:
        from emergentintegrations.llm.chat import LlmChat, UserMessage
        case = await db.cases.find_one({"case_id": case_id, "user_id": user_id}, {"_id": 0})
        if not case:
            return
        documents = await db.documents.find({"case_id": case_id}, {"_id": 0, "file_data": 0}).to_list(500)
        docs_with_text = [d for d in documents if d.get("content_text")]
        if not docs_with_text:
            return
        existing_events = await db.timeline_events.count_documents({"case_id": case_id})
        doc_context = ""
        for doc in docs_with_text:
            doc_context += f"\n--- {doc.get('filename','')} ---\n{doc.get('content_text','')[:6000]}\n"
        if not case.get("summary"):
            try:
                summary_chat = LlmChat(
                    api_key=os.environ.get("EMERGENT_LLM_KEY"),
                    session_id=f"summary_{case_id}",
                    system_message="You are a legal analyst. Write a concise factual summary of this criminal case in Australian English. Use third person only. 3-5 sentences maximum."
                ).with_model("openai", "gpt-4o").with_params(max_tokens=500)
                summary = await asyncio.wait_for(summary_chat.send_message(UserMessage(text=f"Summarise this case:\n{doc_context[:15000]}")), timeout=30)
                if summary:
                    await db.cases.update_one({"case_id": case_id}, {"$set": {"summary": summary.strip(), "updated_at": datetime.now(timezone.utc).isoformat()}})
                    logger.info(f"Auto-generated summary for {case_id}")
            except Exception as e:
                logger.warning(f"Auto-summary failed for {case_id}: {e}")
        if existing_events == 0:
            try:
                tl_prompt = f"""Extract a chronological timeline of events from these case documents.
Return ONLY a JSON array (no markdown). Each event:
{{"date":"YYYY-MM-DD","title":"Brief title","description":"Details","event_type":"incident|arrest|court_hearing|evidence|witness|legal_filing|verdict|appeal|other"}}

Only include events clearly identifiable. Use Australian English.

CASE: {case.get('title','')} | DEFENDANT: {case.get('defendant_name','')}
DOCUMENTS:
{doc_context[:25000]}"""
                tl_chat = LlmChat(
                    api_key=os.environ.get("EMERGENT_LLM_KEY"),
                    session_id=f"tl_{case_id}",
                    system_message="Extract timeline events from Australian criminal case documents. Return only valid JSON array."
                ).with_model("openai", "gpt-4o").with_params(max_tokens=4000)
                raw = await asyncio.wait_for(tl_chat.send_message(UserMessage(text=tl_prompt)), timeout=90)
                raw = (raw or "").strip()
                if raw.startswith("```"):
                    raw = raw.split("\n", 1)[-1].rsplit("```", 1)[0].strip()
                events = json.loads(raw)
                if isinstance(events, list):
                    created = 0
                    for evt in events:
                        if not evt.get("title"):
                            continue
                        event_doc = {
                            "event_id": f"evt_{uuid.uuid4().hex[:12]}",
                            "case_id": case_id, "user_id": user_id,
                            "title": evt.get("title", ""), "description": evt.get("description", ""),
                            "event_date": evt.get("date", ""), "event_type": evt.get("event_type", "other"),
                            "source": "ai_generated", "created_at": datetime.now(timezone.utc).isoformat()
                        }
                        await db.timeline_events.insert_one(event_doc)
                        created += 1
                    logger.info(f"Auto-generated {created} timeline events for {case_id}")
            except Exception as e:
                logger.warning(f"Auto-timeline failed for {case_id}: {e}")
    except Exception as e:
        logger.warning(f"Background auto-generate failed for {case_id}: {e}")


@router.get("/cases/{case_id}/documents", response_model=List[dict])
async def get_documents(case_id: str, request: Request):
    """Get all documents for a case"""
    user = await get_current_user(request)
    case = await db.cases.find_one({"case_id": case_id, "user_id": user.user_id})
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
    documents = await db.documents.find({"case_id": case_id}, {"_id": 0, "file_data": 0}).sort("uploaded_at", -1).to_list(500)
    return documents


@router.post("/cases/{case_id}/documents", response_model=dict)
async def upload_document(
    case_id: str, request: Request, background_tasks: BackgroundTasks,
    file: UploadFile = File(...), category: str = Form(...),
    description: str = Form(None), event_date: str = Form(None)
):
    """Upload a document to a case"""
    user = await get_current_user(request)
    case = await db.cases.find_one({"case_id": case_id, "user_id": user.user_id})
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
    file_content = await file.read()
    file_base64 = base64.b64encode(file_content).decode('utf-8')
    content_text = ""
    file_type = file.content_type or "application/octet-stream"
    filename_lower = file.filename.lower() if file.filename else ""
    try:
        if "text" in file_type or filename_lower.endswith('.txt'):
            content_text = file_content.decode('utf-8', errors='ignore')
        elif "pdf" in file_type or filename_lower.endswith('.pdf'):
            try:
                import io
                from pypdf import PdfReader
                pdf_reader = PdfReader(io.BytesIO(file_content))
                text_parts = []
                for page in pdf_reader.pages[:20]:
                    page_text = page.extract_text()
                    if page_text:
                        text_parts.append(page_text)
                content_text = "\n".join(text_parts)
            except Exception as e:
                logger.warning(f"PDF extraction failed: {e}")
        elif filename_lower.endswith('.docx') or "word" in file_type:
            try:
                import io
                from docx import Document as DocxDocument
                docx_doc = DocxDocument(io.BytesIO(file_content))
                text_parts = [para.text for para in docx_doc.paragraphs if para.text.strip()]
                content_text = "\n".join(text_parts)
            except Exception as e:
                logger.warning(f"DOCX extraction failed: {e}")
    except Exception as e:
        logger.warning(f"Text extraction error: {e}")
    parsed_event_date = None
    if event_date:
        try:
            parsed_event_date = datetime.fromisoformat(event_date.replace('Z', '+00:00')).isoformat()
        except ValueError:
            pass
    doc = Document(
        case_id=case_id, user_id=user.user_id,
        filename=file.filename, file_type=file_type, category=category,
        description=description, content_text=content_text, file_data=file_base64
    )
    doc_dict = doc.model_dump()
    doc_dict["uploaded_at"] = doc_dict["uploaded_at"].isoformat()
    if parsed_event_date:
        doc_dict["event_date"] = parsed_event_date
    await db.documents.insert_one(doc_dict)
    await db.cases.update_one({"case_id": case_id}, {"$set": {"updated_at": datetime.now(timezone.utc).isoformat()}})
    # Schedule background tasks for metadata detection and auto-generation
    if content_text and len(content_text) > 200:
        background_tasks.add_task(_background_auto_detect_metadata, case_id, user.user_id, content_text, file.filename)
        background_tasks.add_task(_background_auto_generate, case_id, user.user_id)
    created_doc = await db.documents.find_one({"document_id": doc.document_id}, {"_id": 0, "file_data": 0})
    return created_doc


@router.get("/cases/{case_id}/documents/{document_id}", response_model=dict)
async def get_document(case_id: str, document_id: str, request: Request):
    """Get a specific document"""
    user = await get_current_user(request)
    doc = await db.documents.find_one(
        {"document_id": document_id, "case_id": case_id, "user_id": user.user_id}, {"_id": 0}
    )
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    return doc


@router.delete("/cases/{case_id}/documents/{document_id}")
async def delete_document(case_id: str, document_id: str, request: Request):
    """Delete a document"""
    user = await get_current_user(request)
    result = await db.documents.delete_one({"document_id": document_id, "case_id": case_id, "user_id": user.user_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Document not found")
    return {"message": "Document deleted"}


@router.post("/cases/{case_id}/documents/search", response_model=dict)
async def search_documents(case_id: str, search_request: DocumentSearchRequest, request: Request):
    """Search for text across all documents in a case"""
    user = await get_current_user(request)
    case = await db.cases.find_one({"case_id": case_id, "user_id": user.user_id})
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
    query = search_request.query.strip()
    if not query:
        raise HTTPException(status_code=400, detail="Search query is required")
    if len(query) < 2:
        raise HTTPException(status_code=400, detail="Search query must be at least 2 characters")
    documents = await db.documents.find(
        {"case_id": case_id, "content_text": {"$exists": True, "$ne": ""}}, {"_id": 0, "file_data": 0}
    ).to_list(500)
    results = []
    total_matches = 0
    flags = 0 if search_request.case_sensitive else re.IGNORECASE
    for doc in documents:
        content = doc.get("content_text", "")
        if not content:
            continue
        matches = []
        try:
            pattern = re.compile(re.escape(query), flags)
            for match in pattern.finditer(content):
                start_pos = match.start()
                end_pos = match.end()
                context_start = max(0, start_pos - 100)
                context_end = min(len(content), end_pos + 100)
                context = content[context_start:context_end]
                if context_start > 0:
                    context = "..." + context
                if context_end < len(content):
                    context = context + "..."
                matches.append({"context": context, "position": start_pos, "matched_text": match.group()})
                if len(matches) >= 10:
                    break
        except re.error:
            continue
        if matches:
            total_matches += len(matches)
            results.append({
                "document_id": doc.get("document_id"), "filename": doc.get("filename"),
                "category": doc.get("category"), "matches": matches, "match_count": len(matches)
            })
    results.sort(key=lambda x: x["match_count"], reverse=True)
    return {"query": query, "total_matches": total_matches, "documents_with_matches": len(results), "total_documents_searched": len(documents), "results": results}


@router.post("/cases/{case_id}/documents/{document_id}/ocr", response_model=dict)
async def ocr_document(case_id: str, document_id: str, request: Request):
    """Extract text from a document using OCR"""
    user = await get_current_user(request)
    doc = await db.documents.find_one({"document_id": document_id, "case_id": case_id, "user_id": user.user_id}, {"_id": 0})
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    if not doc.get('file_data'):
        raise HTTPException(status_code=400, detail="No file data available")
    file_content = base64.b64decode(doc['file_data'])
    content_text, ocr_used = extract_text_with_ocr(file_content, doc.get('filename', ''), doc.get('file_type', ''))
    if not content_text.strip():
        return {"document_id": document_id, "filename": doc.get('filename', ''), "success": False, "ocr_used": ocr_used, "message": "No text could be extracted from this document", "content_length": 0}
    await db.documents.update_one(
        {"document_id": document_id},
        {"$set": {"content_text": content_text, "ocr_extracted": ocr_used, "text_extracted_at": datetime.now(timezone.utc).isoformat()}}
    )
    return {"document_id": document_id, "filename": doc.get('filename', ''), "success": True, "ocr_used": ocr_used, "content_length": len(content_text), "content_preview": content_text[:500] + "..." if len(content_text) > 500 else content_text}


@router.post("/cases/{case_id}/ocr-all", response_model=dict)
async def ocr_all_documents(case_id: str, request: Request):
    """Run OCR on all documents in a case that don't have extracted text"""
    user = await get_current_user(request)
    case = await db.cases.find_one({"case_id": case_id, "user_id": user.user_id})
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
    documents = await db.documents.find({"case_id": case_id}, {"_id": 0}).to_list(500)
    results = []
    successful_ocr = 0
    for doc in documents:
        existing_text = doc.get('content_text', '')
        if len(existing_text.strip()) > 100:
            results.append({"document_id": doc['document_id'], "filename": doc.get('filename'), "status": "skipped", "reason": "Already has extracted text"})
            continue
        if not doc.get('file_data'):
            results.append({"document_id": doc['document_id'], "filename": doc.get('filename'), "status": "skipped", "reason": "No file data"})
            continue
        file_content = base64.b64decode(doc['file_data'])
        content_text, ocr_used = extract_text_with_ocr(file_content, doc.get('filename', ''), doc.get('file_type', ''))
        if content_text.strip():
            await db.documents.update_one(
                {"document_id": doc['document_id']},
                {"$set": {"content_text": content_text, "ocr_extracted": ocr_used, "text_extracted_at": datetime.now(timezone.utc).isoformat()}}
            )
            successful_ocr += 1
            results.append({"document_id": doc['document_id'], "filename": doc.get('filename'), "status": "success", "ocr_used": ocr_used, "content_length": len(content_text)})
        else:
            results.append({"document_id": doc['document_id'], "filename": doc.get('filename'), "status": "failed", "reason": "No text could be extracted"})
    return {"total_documents": len(documents), "successful_extractions": successful_ocr, "results": results}


@router.post("/cases/{case_id}/documents/{document_id}/extract-text", response_model=dict)
async def extract_document_text(case_id: str, document_id: str, request: Request):
    """Re-extract text from a document"""
    user = await get_current_user(request)
    doc = await db.documents.find_one({"document_id": document_id, "case_id": case_id, "user_id": user.user_id}, {"_id": 0})
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    if not doc.get('file_data'):
        raise HTTPException(status_code=400, detail="No file data available")
    file_content = base64.b64decode(doc['file_data'])
    filename_lower = doc.get('filename', '').lower()
    file_type = doc.get('file_type', '')
    content_text = ""
    try:
        if "text" in file_type or filename_lower.endswith('.txt'):
            content_text = file_content.decode('utf-8', errors='ignore')
        elif "pdf" in file_type or filename_lower.endswith('.pdf'):
            try:
                import io
                from pypdf import PdfReader
                pdf_reader = PdfReader(io.BytesIO(file_content))
                text_parts = [page.extract_text() for page in pdf_reader.pages[:30] if page.extract_text()]
                content_text = "\n".join(text_parts)
            except Exception as e:
                logger.warning(f"PDF extraction failed: {e}")
        elif filename_lower.endswith('.docx') or "word" in file_type:
            try:
                import io
                from docx import Document as DocxDocument
                docx_doc = DocxDocument(io.BytesIO(file_content))
                text_parts = [para.text for para in docx_doc.paragraphs if para.text.strip()]
                content_text = "\n".join(text_parts)
            except Exception as e:
                logger.warning(f"DOCX extraction failed: {e}")
    except Exception as e:
        logger.error(f"Text extraction error: {e}")
        raise HTTPException(status_code=500, detail=f"Text extraction failed: {str(e)}")
    await db.documents.update_one(
        {"document_id": document_id},
        {"$set": {"content_text": content_text, "text_extracted_at": datetime.now(timezone.utc).isoformat()}}
    )
    return {"document_id": document_id, "filename": doc.get('filename'), "content_length": len(content_text), "content_preview": content_text[:500] + "..." if len(content_text) > 500 else content_text, "success": bool(content_text)}


@router.post("/cases/{case_id}/extract-all-text", response_model=dict)
async def extract_all_documents_text(case_id: str, request: Request):
    """Extract text from all documents in a case"""
    user = await get_current_user(request)
    case = await db.cases.find_one({"case_id": case_id, "user_id": user.user_id})
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
    documents = await db.documents.find({"case_id": case_id}, {"_id": 0}).to_list(500)
    results = []
    for doc in documents:
        if not doc.get('file_data'):
            results.append({"document_id": doc['document_id'], "success": False, "error": "No file data"})
            continue
        file_content = base64.b64decode(doc['file_data'])
        filename_lower = doc.get('filename', '').lower()
        file_type = doc.get('file_type', '')
        content_text = ""
        error = None
        try:
            if "text" in file_type or filename_lower.endswith('.txt'):
                content_text = file_content.decode('utf-8', errors='ignore')
            elif "pdf" in file_type or filename_lower.endswith('.pdf'):
                try:
                    import io
                    from pypdf import PdfReader
                    pdf_reader = PdfReader(io.BytesIO(file_content))
                    text_parts = [page.extract_text() for page in pdf_reader.pages[:30] if page.extract_text()]
                    content_text = "\n".join(text_parts)
                except Exception as e:
                    error = str(e)
            elif filename_lower.endswith('.docx') or "word" in file_type:
                try:
                    import io
                    from docx import Document as DocxDocument
                    docx_doc = DocxDocument(io.BytesIO(file_content))
                    text_parts = [para.text for para in docx_doc.paragraphs if para.text.strip()]
                    content_text = "\n".join(text_parts)
                except Exception as e:
                    error = str(e)
        except Exception as e:
            error = str(e)
        if content_text:
            await db.documents.update_one(
                {"document_id": doc['document_id']},
                {"$set": {"content_text": content_text, "text_extracted_at": datetime.now(timezone.utc).isoformat()}}
            )
        results.append({"document_id": doc['document_id'], "filename": doc.get('filename'), "success": bool(content_text), "content_length": len(content_text) if content_text else 0, "error": error})
    successful = sum(1 for r in results if r['success'])
    # AI auto-detect case metadata from extracted text
    detected_metadata = {}
    if successful > 0:
        try:
            from emergentintegrations.llm.chat import LlmChat, UserMessage
            combined_text = ""
            for doc in documents:
                ct = doc.get("content_text") or ""
                if not ct:
                    for r in results:
                        if r.get("document_id") == doc["document_id"] and r.get("success"):
                            fresh = await db.documents.find_one({"document_id": doc["document_id"]}, {"_id": 0, "content_text": 1})
                            ct = (fresh or {}).get("content_text", "")
                if ct:
                    combined_text += f"\n--- DOCUMENT: {doc.get('filename','')} ---\n{ct[:6000]}\n"
            if len(combined_text) > 200:
                detect_prompt = f"""Analyse the following case documents and extract these metadata fields.
Return ONLY valid JSON with these exact keys (no markdown, no explanation):
{{
  "offence_category": "<one of: homicide, assault, sexual_offences, robbery_theft, drug_offences, fraud_dishonesty, firearms_weapons, domestic_violence, public_order, terrorism, driving_offences>",
  "offence_type": "<specific offence>",
  "sentence": "<exact sentence imposed>",
  "state": "<one of: nsw, vic, qld, sa, wa, tas, nt, act>",
  "court": "<court name if found>",
  "case_number": "<case number if found>",
  "defendant_name": "<defendant full name if found>"
}}
Rules: offence_category MUST be from the provided list. Read ACTUAL content. If unknown, null. state lowercase.

DOCUMENTS:
{combined_text[:30000]}"""
                chat = LlmChat(
                    api_key=os.environ.get("EMERGENT_LLM_KEY"),
                    session_id=f"detect_{case_id}",
                    system_message="You are a legal document analyst. Extract factual metadata from Australian criminal case documents. Return only valid JSON."
                ).with_model("openai", "gpt-4o").with_params(max_tokens=2000)
                raw = await asyncio.wait_for(chat.send_message(UserMessage(text=detect_prompt)), timeout=60)
                raw = (raw or "").strip()
                if raw.startswith("```"):
                    raw = raw.split("\n", 1)[-1].rsplit("```", 1)[0].strip()
                meta = json.loads(raw)
                update_fields = {}
                valid_categories = ["homicide","assault","sexual_offences","robbery_theft","drug_offences","fraud_dishonesty","firearms_weapons","domestic_violence","public_order","terrorism","driving_offences"]
                valid_states = ["nsw","vic","qld","sa","wa","tas","nt","act"]
                if meta.get("offence_category") in valid_categories:
                    update_fields["offence_category"] = meta["offence_category"]
                if meta.get("offence_type"):
                    update_fields["offence_type"] = meta["offence_type"]
                if meta.get("sentence"):
                    update_fields["sentence"] = meta["sentence"]
                if meta.get("state") and meta["state"].lower() in valid_states:
                    update_fields["state"] = meta["state"].lower()
                if meta.get("court"):
                    update_fields["court"] = meta["court"]
                if meta.get("case_number"):
                    update_fields["case_number"] = meta["case_number"]
                if meta.get("defendant_name") and not case.get("defendant_name"):
                    update_fields["defendant_name"] = meta["defendant_name"]
                if update_fields:
                    update_fields["updated_at"] = datetime.now(timezone.utc).isoformat()
                    await db.cases.update_one({"case_id": case_id}, {"$set": update_fields})
                    detected_metadata = update_fields
                    logger.info(f"Auto-detected case metadata for {case_id}: {update_fields}")
        except Exception as e:
            logger.warning(f"Auto-detect metadata failed for {case_id}: {e}")
    return {"total_documents": len(documents), "successful_extractions": successful, "results": results, "detected_metadata": detected_metadata}
