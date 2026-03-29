# DO NOT UNDO — documents router. All endpoints in this file are approved and must be preserved.
"""
Criminal Appeal AI - Documents Router
Handles document upload, retrieval, search, OCR, and text extraction
"""
from fastapi import APIRouter, HTTPException, Request, UploadFile, File, Form, Response
from typing import List
from datetime import datetime, timezone
import base64
import re
import io
import logging

from config import db, logger
from models import Document
from auth_utils import get_current_user, verify_case_ownership

router = APIRouter(prefix="/api/cases/{case_id}/documents", tags=["documents"])


@router.get("", response_model=List[dict])
async def get_documents(case_id: str, request: Request):
    """Get all documents for a case"""
    user = await get_current_user(request)
    await verify_case_ownership(case_id, user.user_id)
    
    documents = await db.documents.find(
        {"case_id": case_id},
        {"_id": 0, "file_data": 0}
    ).sort("uploaded_at", -1).to_list(500)
    
    return documents


@router.post("", response_model=dict)
async def upload_document(
    case_id: str,
    request: Request,
    file: UploadFile = File(...),
    category: str = Form(...),
    description: str = Form(None),
    event_date: str = Form(None)
):
    """Upload a document to a case"""
    user = await get_current_user(request)
    await verify_case_ownership(case_id, user.user_id)
    
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
                from docx import Document as DocxDocument
                doc = DocxDocument(io.BytesIO(file_content))
                text_parts = [para.text for para in doc.paragraphs if para.text.strip()]
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
        case_id=case_id,
        user_id=user.user_id,
        filename=file.filename,
        file_type=file_type,
        category=category,
        description=description,
        content_text=content_text,
        file_data=file_base64
    )
    
    doc_dict = doc.model_dump()
    doc_dict["uploaded_at"] = doc_dict["uploaded_at"].isoformat()
    if parsed_event_date:
        doc_dict["event_date"] = parsed_event_date
    
    await db.documents.insert_one(doc_dict)
    
    await db.cases.update_one(
        {"case_id": case_id},
        {"$set": {"updated_at": datetime.now(timezone.utc).isoformat()}}
    )
    
    created_doc = await db.documents.find_one({"document_id": doc.document_id}, {"_id": 0, "file_data": 0})
    return created_doc


@router.get("/{document_id}", response_model=dict)
async def get_document(case_id: str, document_id: str, request: Request):
    """Get a specific document"""
    user = await get_current_user(request)
    
    doc = await db.documents.find_one(
        {"document_id": document_id, "case_id": case_id, "user_id": user.user_id},
        {"_id": 0}
    )
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    
    return doc


@router.delete("/{document_id}")
async def delete_document(case_id: str, document_id: str, request: Request):
    """Delete a document"""
    user = await get_current_user(request)
    
    result = await db.documents.delete_one({
        "document_id": document_id,
        "case_id": case_id,
        "user_id": user.user_id
    })
    
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Document not found")
    
    return {"message": "Document deleted"}


@router.post("/search", response_model=dict)
async def search_documents(case_id: str, request: Request):
    """Search for text across all documents in a case"""
    user = await get_current_user(request)
    await verify_case_ownership(case_id, user.user_id)
    
    body = await request.json()
    query = body.get("query", "").strip()
    case_sensitive = body.get("case_sensitive", False)
    
    if not query:
        raise HTTPException(status_code=400, detail="Search query is required")
    if len(query) < 2:
        raise HTTPException(status_code=400, detail="Search query must be at least 2 characters")
    
    documents = await db.documents.find(
        {"case_id": case_id, "content_text": {"$exists": True, "$ne": ""}},
        {"_id": 0, "file_data": 0}
    ).to_list(500)
    
    results = []
    total_matches = 0
    flags = 0 if case_sensitive else re.IGNORECASE
    
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
                
                matches.append({
                    "context": context,
                    "position": start_pos,
                    "matched_text": match.group()
                })
                
                if len(matches) >= 10:
                    break
        except re.error:
            continue
        
        if matches:
            total_matches += len(matches)
            results.append({
                "document_id": doc.get("document_id"),
                "filename": doc.get("filename"),
                "category": doc.get("category"),
                "matches": matches,
                "match_count": len(matches)
            })
    
    results.sort(key=lambda x: x["match_count"], reverse=True)
    
    return {
        "query": query,
        "total_matches": total_matches,
        "documents_with_matches": len(results),
        "total_documents_searched": len(documents),
        "results": results
    }
