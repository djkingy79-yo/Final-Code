# DO NOT UNDO — resources router. All endpoints in this file are approved and must be preserved.
"""
Criminal Appeal AI - Resources Router
Handles resource directory and document templates
"""
from fastapi import APIRouter, HTTPException, Request
from typing import List
from datetime import datetime, timezone

from config import db

router = APIRouter(tags=["resources"])


# Resource Directory Data
RESOURCE_DIRECTORY = {
    "support_services": [
        {"name": "Community Legal Centres NSW", "website": "https://www.clcnsw.org.au", "description": "Free legal advice and referrals"},
        {"name": "Aboriginal Legal Service NSW/ACT", "phone": "1800 765 767", "website": "https://www.alsnswact.org.au", "description": "Legal services for Aboriginal and Torres Strait Islander people"},
    ],
    "advocacy_groups": [
        {"name": "Innocence Project Australia", "email": "info@innocenceproject.org.au", "website": "https://innocenceproject.org.au", "description": "Works to exonerate wrongfully convicted people"},
        {"name": "Justice Action", "phone": "(02) 9283 0123", "website": "https://www.justiceaction.org.au", "description": "Prisoner advocacy and justice reform"},
    ],
    "courts": [
        {"name": "NSW Court of Criminal Appeal", "address": "Law Courts Building, Queens Square, Sydney NSW 2000", "website": "https://www.supremecourt.justice.nsw.gov.au", "description": "Handles criminal appeals in NSW"},
        {"name": "High Court of Australia", "address": "Parkes Place, Canberra ACT 2600", "website": "https://www.hcourt.gov.au", "description": "Australia's highest court"},
    ],
    "information_services": [
        {"name": "LawAccess NSW", "phone": "1300 888 529", "website": "https://www.lawaccess.nsw.gov.au", "description": "Free legal information and referrals"},
        {"name": "Community Legal Centres NSW", "website": "https://www.clcnsw.org.au", "description": "Directory of community legal centres"},
    ]
}

# Document Templates
DOCUMENT_TEMPLATES = [
    {
        "template_id": "notice_of_appeal",
        "name": "Notice of Appeal",
        "description": "Standard form for lodging a criminal appeal in NSW",
        "category": "appeal",
        "fields": ["appellant_name", "case_number", "conviction_date", "grounds"]
    },
    {
        "template_id": "leave_to_appeal",
        "name": "Application for Leave to Appeal",
        "description": "Application when leave is required for the appeal",
        "category": "appeal",
        "fields": ["appellant_name", "case_number", "reasons_for_leave"]
    },
    {
        "template_id": "fresh_evidence_affidavit",
        "name": "Fresh Evidence Affidavit",
        "description": "Affidavit supporting fresh evidence ground of appeal",
        "category": "evidence",
        "fields": ["deponent_name", "evidence_description", "why_not_available_at_trial"]
    },
    {
        "template_id": "extension_of_time",
        "name": "Application for Extension of Time",
        "description": "Application when appeal is lodged outside the 28-day period",
        "category": "procedural",
        "fields": ["appellant_name", "original_deadline", "reasons_for_delay"]
    }
]


@router.get("/api/resources/directory", response_model=dict)
async def get_resource_directory():
    """Get the legal resource directory"""
    return RESOURCE_DIRECTORY


@router.get("/api/templates", response_model=List[dict])
async def get_document_templates():
    """Get available document templates"""
    return DOCUMENT_TEMPLATES


@router.post("/api/templates/{template_id}/generate", response_model=dict)
async def generate_document_from_template(template_id: str, request: Request):
    """Generate a document from a template with provided data"""
    body = await request.json()
    
    template = next((t for t in DOCUMENT_TEMPLATES if t["template_id"] == template_id), None)
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")
    
    # Generate document content based on template
    content_parts = [f"# {template['name']}\n"]
    content_parts.append(f"Generated: {datetime.now(timezone.utc).strftime('%d %B %Y')}\n\n")
    
    if template_id == "notice_of_appeal":
        content_parts.append("IN THE COURT OF CRIMINAL APPEAL\n")
        content_parts.append("SUPREME COURT OF NEW SOUTH WALES\n\n")
        content_parts.append(f"Appellant: {body.get('appellant_name', '[APPELLANT NAME]')}\n")
        content_parts.append(f"Case Number: {body.get('case_number', '[CASE NUMBER]')}\n")
        content_parts.append(f"Date of Conviction: {body.get('conviction_date', '[DATE]')}\n\n")
        content_parts.append("GROUNDS OF APPEAL:\n")
        for i, ground in enumerate(body.get('grounds', ['[GROUND 1]']), 1):
            content_parts.append(f"{i}. {ground}\n")
    
    elif template_id == "leave_to_appeal":
        content_parts.append("APPLICATION FOR LEAVE TO APPEAL\n\n")
        content_parts.append(f"Appellant: {body.get('appellant_name', '[APPELLANT NAME]')}\n")
        content_parts.append(f"Case Number: {body.get('case_number', '[CASE NUMBER]')}\n\n")
        content_parts.append("REASONS WHY LEAVE SHOULD BE GRANTED:\n")
        content_parts.append(body.get('reasons_for_leave', '[REASONS]'))
    
    elif template_id == "fresh_evidence_affidavit":
        content_parts.append("AFFIDAVIT IN SUPPORT OF FRESH EVIDENCE\n\n")
        content_parts.append(f"I, {body.get('deponent_name', '[DEPONENT NAME]')}, make oath and say:\n\n")
        content_parts.append(f"1. The evidence I wish to adduce is:\n{body.get('evidence_description', '[DESCRIPTION]')}\n\n")
        content_parts.append(f"2. This evidence was not available at trial because:\n{body.get('why_not_available_at_trial', '[REASONS]')}")
    
    elif template_id == "extension_of_time":
        content_parts.append("APPLICATION FOR EXTENSION OF TIME TO APPEAL\n\n")
        content_parts.append(f"Appellant: {body.get('appellant_name', '[APPELLANT NAME]')}\n")
        content_parts.append(f"Original Deadline: {body.get('original_deadline', '[DATE]')}\n\n")
        content_parts.append("REASONS FOR DELAY:\n")
        content_parts.append(body.get('reasons_for_delay', '[REASONS]'))
    
    return {
        "template_id": template_id,
        "template_name": template["name"],
        "content": "".join(content_parts),
        "generated_at": datetime.now(timezone.utc).isoformat()
    }
