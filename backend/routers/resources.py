"""
Criminal Appeal AI - Resources & Templates Router
Extracted from server.py monolith.
"""
from fastapi import APIRouter, Request
from typing import List
from datetime import datetime, timezone
import logging

from auth_utils import get_current_user

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api", tags=["resources"])


@router.get("/resources/directory", response_model=dict)
async def get_resource_directory():
    """Get directory of support resources"""
    return {
        "support_services": [
            {"name": "Community Legal Centres NSW", "website": "https://www.clcnsw.org.au", "services": ["Legal advice", "Referrals"], "region": "NSW"},
            {"name": "Aboriginal Legal Service (NSW/ACT)", "phone": "1800 765 767", "website": "https://www.alsnswact.org.au", "services": ["Criminal law", "Family law"], "region": "NSW/ACT"},
            {"name": "LawAccess NSW", "phone": "1300 888 529", "website": "https://www.lawaccess.nsw.gov.au", "services": ["Legal information", "Referrals"], "region": "NSW"}
        ],
        "advocacy_groups": [
            {"name": "Innocence Project (Australia)", "website": "https://www.innocenceproject.org.au", "focus": "Wrongful convictions"},
            {"name": "Justice Action", "phone": "(02) 9283 0123", "website": "https://www.justiceaction.org.au", "focus": "Prisoner rights"},
            {"name": "Prisoners Aid Association NSW", "phone": "(02) 9288 8700", "website": "https://www.prisonersaid.org.au", "focus": "Family support"}
        ],
        "courts": [
            {"name": "NSW Court of Criminal Appeal", "website": "https://www.supremecourt.justice.nsw.gov.au"},
            {"name": "High Court of Australia", "website": "https://www.hcourt.gov.au", "note": "Special leave required"}
        ],
        "appeal_deadlines": {"notice_of_appeal": "28 days from conviction/sentence", "leave_to_appeal": "28 days", "extension": "Can apply if missed - must show good reason"}
    }


@router.get("/templates", response_model=List[dict])
async def get_document_templates():
    """Get available document templates"""
    return [
        {"template_id": "notice_of_appeal", "title": "Notice of Appeal", "description": "Form to lodge an appeal", "category": "lodgement"},
        {"template_id": "leave_to_appeal", "title": "Application for Leave to Appeal", "description": "Application for permission to appeal sentence", "category": "lodgement"},
        {"template_id": "affidavit_fresh_evidence", "title": "Affidavit - Fresh Evidence", "description": "Sworn statement for new evidence", "category": "evidence"},
        {"template_id": "extension_of_time", "title": "Extension of Time Application", "description": "Apply to file after deadline", "category": "lodgement"},
        {"template_id": "outline_of_submissions", "title": "Written Submissions", "description": "Legal arguments for hearing", "category": "hearing"}
    ]


@router.post("/templates/{template_id}/generate", response_model=dict)
async def generate_document_from_template(template_id: str, request: Request):
    """Generate a document from template"""
    await get_current_user(request)
    body = await request.json()
    if template_id == "notice_of_appeal":
        content = f"""COURT OF CRIMINAL APPEAL - SUPREME COURT OF NSW
NOTICE OF APPEAL

Appellant: {body.get('appellant_name', '[NAME]')}
Case Number: {body.get('case_number', '[NUMBER]')}

TAKE NOTICE that the above-named appeals against: {body.get('appeal_type', '[CONVICTION/SENTENCE]')}

Court of Trial: {body.get('court_of_trial', '[COURT]')}
Date of Conviction: {body.get('date_of_conviction', '[DATE]')}
Date of Sentence: {body.get('date_of_sentence', '[DATE]')}
Offence: {body.get('offence', '[OFFENCE]')}
Sentence: {body.get('sentence', '[SENTENCE]')}

GROUNDS OF APPEAL:
{body.get('grounds', '[GROUNDS]')}

DATED: {datetime.now().strftime('%d %B %Y')}

---
Criminal Law Appeal Case Management by Deb King GLENMORE PARK NSW"""
    elif template_id == "leave_to_appeal":
        content = f"""APPLICATION FOR LEAVE TO APPEAL AGAINST SENTENCE

Appellant: {body.get('appellant_name', '[NAME]')}
Case: {body.get('case_number', '[NUMBER]')}
Sentence Date: {body.get('date_of_sentence', '[DATE]')}
Sentence: {body.get('sentence', '[SENTENCE]')}

GROUNDS: {body.get('grounds', '[GROUNDS]')}
WHY LEAVE SHOULD BE GRANTED: {body.get('why_leave_granted', '[REASONS]')}

DATED: {datetime.now().strftime('%d %B %Y')}
---
Criminal Law Appeal Case Management by Deb King GLENMORE PARK NSW"""
    else:
        content = f"Template {template_id} - Please contact support for this template."
    return {"template_id": template_id, "content": content, "generated_at": datetime.now(timezone.utc).isoformat()}
