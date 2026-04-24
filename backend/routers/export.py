# DO NOT UNDO — export router. All endpoints in this file are approved and must be preserved.
"""
Criminal Appeal AI - Export Router
Handles Quick Export (Appeal Package) generation - ZIP with all docs, reports, and editable templates
Also handles Case Export Pack (formatted PDF with all paid reports) and report translation.
"""
from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import StreamingResponse
from typing import List
from datetime import datetime, timezone
from pydantic import BaseModel
import io
import re
import zipfile
import json
import logging

from config import db, get_contact_email
from auth_utils import get_current_user, verify_case_ownership

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/cases/{case_id}/export", tags=["export"])


class ExportOptions(BaseModel):
    include_documents: bool = True
    include_timeline: bool = True
    include_grounds: bool = True
    include_notes: bool = True
    include_reports: bool = True
    include_analysis: bool = True
    include_templates: bool = True
    format: str = "zip"  # zip or individual


@router.post("/package")
async def generate_appeal_package(case_id: str, options: ExportOptions, request: Request):
    """
    Generate a comprehensive appeal package as a ZIP file.
    Includes: all documents, timeline PDF, grounds summary, AI analysis, and editable DOCX templates.
    """
    user = await get_current_user(request)
    await verify_case_ownership(case_id, user.user_id)
    
    # Fetch case data
    case = await db.cases.find_one({"case_id": case_id}, {"_id": 0})
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
    
    # Create ZIP file in memory
    zip_buffer = io.BytesIO()
    
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        # 1. Case Summary (JSON + TXT)
        case_summary = {
            "case_id": case.get("case_id"),
            "title": case.get("title"),
            "defendant_name": case.get("defendant_name"),
            "case_number": case.get("case_number"),
            "court": case.get("court"),
            "judge": case.get("judge"),
            "state": case.get("state"),
            "offence_category": case.get("offence_category"),
            "offence_type": case.get("offence_type"),
            "summary": case.get("summary"),
            "created_at": case.get("created_at"),
            "exported_at": datetime.now(timezone.utc).isoformat()
        }
        zip_file.writestr("00_Case_Summary.json", json.dumps(case_summary, indent=2))
        
        # Text version of case summary
        summary_txt = f"""CASE SUMMARY
{'='*50}

Title: {case.get('title', 'N/A')}
Defendant: {case.get('defendant_name', 'N/A')}
Case Number: {case.get('case_number', 'N/A')}
Court: {case.get('court', 'N/A')}
Judge: {case.get('judge', 'N/A')}
State: {case.get('state', 'N/A').upper()}
Offence Category: {case.get('offence_category', 'N/A').replace('_', ' ').title()}
Offence Type: {case.get('offence_type', 'N/A')}

Summary:
{case.get('summary', 'No summary provided')}

Exported: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')}
"""
        zip_file.writestr("00_Case_Summary.txt", summary_txt)
        
        # 2. Documents
        if options.include_documents:
            documents = await db.documents.find(
                {"case_id": case_id},
                {"_id": 0}
            ).to_list(500)
            
            # Create documents folder
            doc_index = []
            for i, doc in enumerate(documents, 1):
                doc_info = {
                    "filename": doc.get("filename"),
                    "category": doc.get("category"),
                    "upload_date": doc.get("upload_date"),
                    "has_text": bool(doc.get("extracted_text"))
                }
                doc_index.append(doc_info)
                
                # Save document metadata
                doc_meta = f"""Document: {doc.get('filename')}
Category: {doc.get('category', 'N/A').replace('_', ' ').title()}
Uploaded: {doc.get('upload_date', 'N/A')}

Extracted Text:
{'-'*40}
{doc.get('extracted_text', 'No text extracted')[:50000]}

AI Analysis:
{'-'*40}
{doc.get('ai_analysis', 'No AI analysis available')}
"""
                zip_file.writestr(f"01_Documents/{i:02d}_{doc.get('filename', 'document')}.txt", doc_meta)
            
            # Document index
            zip_file.writestr("01_Documents/_Document_Index.json", json.dumps(doc_index, indent=2))
        
        # 3. Timeline
        if options.include_timeline:
            timeline = await db.timeline_events.find(
                {"case_id": case_id},
                {"_id": 0}
            ).sort("event_date", 1).to_list(500)
            
            timeline_txt = "CASE TIMELINE\n" + "="*50 + "\n\n"
            for event in timeline:
                event_date = event.get("event_date", "Unknown date")
                timeline_txt += f"""[{event_date}] {event.get('title', 'Untitled')}
Category: {event.get('event_category', 'N/A').replace('_', ' ').title()}
Type: {event.get('event_type', 'N/A').replace('_', ' ').title()}
Significance: {event.get('significance', 'N/A').title()}

{event.get('description', 'No description')}

Source: {event.get('source_citation', 'N/A')}
{'-'*40}

"""
            zip_file.writestr("02_Timeline/Timeline_Chronological.txt", timeline_txt)
            zip_file.writestr("02_Timeline/Timeline_Data.json", json.dumps(timeline, indent=2, default=str))
        
        # 4. Grounds of Merit
        if options.include_grounds:
            grounds = await db.grounds_of_merit.find(
                {"case_id": case_id},
                {"_id": 0}
            ).to_list(100)
            
            grounds_txt = "GROUNDS OF MERIT\n" + "="*50 + "\n\n"
            for i, ground in enumerate(grounds, 1):
                strength_indicator = {"strong": "★★★", "moderate": "★★☆", "weak": "★☆☆"}.get(ground.get("strength"), "★★☆")
                grounds_txt += f"""GROUND {i}: {ground.get('title', 'Untitled')}
Type: {ground.get('ground_type', 'N/A').replace('_', ' ').title()}
Strength: {ground.get('strength', 'N/A').title()} {strength_indicator}
Status: {ground.get('status', 'identified').title()}

Description:
{ground.get('description', 'No description')}

Analysis:
{ground.get('analysis', 'No analysis available')}

Supporting Evidence:
{chr(10).join(['- ' + (e if isinstance(e, str) else e.get('text', str(e))) for e in ground.get('supporting_evidence', [])] or ['None listed'])}

{'='*50}

"""
            zip_file.writestr("03_Grounds/Grounds_of_Merit.txt", grounds_txt)
            zip_file.writestr("03_Grounds/Grounds_Data.json", json.dumps(grounds, indent=2, default=str))
        
        # 5. Notes
        if options.include_notes:
            notes = await db.notes.find(
                {"case_id": case_id},
                {"_id": 0}
            ).sort("created_at", -1).to_list(500)
            
            notes_txt = "CASE NOTES\n" + "="*50 + "\n\n"
            for note in notes:
                pinned = "📌 PINNED" if note.get("is_pinned") else ""
                notes_txt += f"""{pinned}
[{note.get('created_at', 'Unknown date')}] {note.get('title', 'Untitled')}
Category: {note.get('category', 'general').title()}

{note.get('content', 'No content')}

{'-'*40}

"""
            zip_file.writestr("04_Notes/Case_Notes.txt", notes_txt)
            zip_file.writestr("04_Notes/Notes_Data.json", json.dumps(notes, indent=2, default=str))
        
        # 6. Reports
        if options.include_reports:
            reports = await db.reports.find(
                {"case_id": case_id},
                {"_id": 0}
            ).sort("generated_at", -1).to_list(50)
            
            for i, report in enumerate(reports, 1):
                report_type = report.get("report_type", "unknown").replace("_", " ").title()
                report_txt = f"""REPORT: {report_type}
Generated: {report.get('generated_at', 'Unknown')}
{'='*50}

{report.get('content', 'No content')}
"""
                zip_file.writestr(f"05_Reports/{i:02d}_{report_type.replace(' ', '_')}.txt", report_txt)
        
        # 7. AI Analysis Summary
        if options.include_analysis:
            # Get contradiction scans
            scans = await db.contradiction_scans.find(
                {"case_id": case_id},
                {"_id": 0}
            ).sort("scanned_at", -1).to_list(10)
            
            if scans:
                latest_scan = scans[0]
                contradictions = latest_scan.get("results", {}).get("contradictions", [])
                
                analysis_txt = "AI ANALYSIS - CONTRADICTION FINDINGS\n" + "="*50 + "\n\n"
                analysis_txt += f"Scan Date: {latest_scan.get('scanned_at', 'Unknown')}\n"
                analysis_txt += f"Documents Analysed: {latest_scan.get('documents_analysed', latest_scan.get('documents_analyzed', 0))}\n\n"
                
                summary = latest_scan.get("results", {}).get("summary", {})
                analysis_txt += f"Total Findings: {summary.get('total_found', 0)}\n"
                analysis_txt += f"Critical: {summary.get('critical_count', 0)}\n"
                analysis_txt += f"Significant: {summary.get('significant_count', 0)}\n"
                analysis_txt += f"Minor: {summary.get('minor_count', 0)}\n\n"
                
                if summary.get("key_finding"):
                    analysis_txt += f"Key Finding: {summary.get('key_finding')}\n\n"
                
                analysis_txt += "DETAILED FINDINGS:\n" + "-"*40 + "\n\n"
                
                for i, c in enumerate(contradictions, 1):
                    analysis_txt += f"""FINDING {i}: [{c.get('severity', 'unknown').upper()}]
Type: {c.get('type', 'N/A').replace('_', ' ').title()}

Description:
{c.get('description', 'No description')}

Analysis:
{c.get('analysis', 'No analysis')}

Recommendations:
{chr(10).join(['- ' + r for r in c.get('recommendations', [])] or ['None'])}

{'-'*40}

"""
                zip_file.writestr("06_AI_Analysis/Contradiction_Analysis.txt", analysis_txt)
                zip_file.writestr("06_AI_Analysis/Contradiction_Data.json", json.dumps(scans, indent=2, default=str))
        
        # 8. Editable Templates (DOCX-ready TXT files)
        if options.include_templates:
            # Notice of Appeal Template
            notice_template = f"""NOTICE OF INTENTION TO APPEAL
{'='*50}

IN THE COURT OF CRIMINAL APPEAL
SUPREME COURT OF {case.get('state', 'NSW').upper()}

BETWEEN:
    {case.get('defendant_name', '[APPELLANT NAME]')}
    Appellant

AND:
    REGINA
    Respondent

CASE NUMBER: {case.get('case_number', '[CASE NUMBER]')}

NOTICE

TAKE NOTICE that the Appellant intends to appeal against:

[ ] Conviction
[ ] Sentence
[ ] Both Conviction and Sentence

in the proceedings at {case.get('court', '[COURT NAME]')} on [DATE OF CONVICTION/SENTENCE].

GROUNDS OF APPEAL:

1. [GROUND 1]

2. [GROUND 2]

3. [GROUND 3]

[ADD ADDITIONAL GROUNDS AS REQUIRED]

DATED this _____ day of _______________ 20___

_________________________________
[Appellant/Appellant's Solicitor]
[Address]
[Phone]
[Email]

Filed by: _________________________________
"""
            zip_file.writestr("07_Templates/Notice_of_Appeal_Template.txt", notice_template)
            
            # Leave to Appeal Template
            leave_template = f"""APPLICATION FOR LEAVE TO APPEAL
{'='*50}

IN THE COURT OF CRIMINAL APPEAL
SUPREME COURT OF {case.get('state', 'NSW').upper()}

BETWEEN:
    {case.get('defendant_name', '[APPLICANT NAME]')}
    Applicant

AND:
    REGINA
    Respondent

CASE NUMBER: {case.get('case_number', '[CASE NUMBER]')}

APPLICATION FOR LEAVE TO APPEAL AGAINST [CONVICTION/SENTENCE]

The Applicant applies for leave to appeal on the following grounds:

GROUND 1: [TITLE]
[Detailed submission for Ground 1]

GROUND 2: [TITLE]
[Detailed submission for Ground 2]

GROUND 3: [TITLE]
[Detailed submission for Ground 3]

SUBMISSIONS IN SUPPORT OF LEAVE:
[Why leave should be granted - prospects of success, importance of issues, etc.]

DATED this _____ day of _______________ 20___

_________________________________
[Applicant/Applicant's Solicitor]
"""
            zip_file.writestr("07_Templates/Leave_to_Appeal_Template.txt", leave_template)
            
            # Written Submissions Template
            submissions_template = f"""WRITTEN SUBMISSIONS ON BEHALF OF THE APPELLANT
{'='*50}

IN THE COURT OF CRIMINAL APPEAL
SUPREME COURT OF {case.get('state', 'NSW').upper()}

BETWEEN:
    {case.get('defendant_name', '[APPELLANT NAME]')}
    Appellant

AND:
    REGINA
    Respondent

CASE NUMBER: {case.get('case_number', '[CASE NUMBER]')}

APPELLANT'S WRITTEN SUBMISSIONS

A. INTRODUCTION

1. These submissions are filed on behalf of the Appellant, {case.get('defendant_name', '[NAME]')}.

2. The Appellant was convicted on [DATE] at {case.get('court', '[COURT]')} before [JUDGE NAME] of:
   (a) [OFFENCE 1]
   (b) [OFFENCE 2]

3. The Appellant was sentenced to [SENTENCE DETAILS].

B. FACTUAL BACKGROUND

4. [Summary of relevant facts]

C. GROUND 1: [TITLE]

5. [Submissions on Ground 1]

6. [Legal authorities and precedents]

D. GROUND 2: [TITLE]

7. [Submissions on Ground 2]

8. [Legal authorities and precedents]

E. CONCLUSION

9. For the reasons set out above, the appeal should be allowed and:
   (a) [Relief sought - e.g., conviction quashed, new trial ordered, sentence reduced]

DATED this _____ day of _______________ 20___

_________________________________
[Counsel for the Appellant]
"""
            zip_file.writestr("07_Templates/Written_Submissions_Template.txt", submissions_template)
            
            # Fresh Evidence Affidavit Template
            affidavit_template = f"""AFFIDAVIT IN SUPPORT OF FRESH EVIDENCE
{'='*50}

IN THE COURT OF CRIMINAL APPEAL
SUPREME COURT OF {case.get('state', 'NSW').upper()}

BETWEEN:
    {case.get('defendant_name', '[APPELLANT NAME]')}
    Appellant

AND:
    REGINA
    Respondent

CASE NUMBER: {case.get('case_number', '[CASE NUMBER]')}

AFFIDAVIT OF [DEPONENT NAME]

I, [FULL NAME], of [ADDRESS], [OCCUPATION], MAKE OATH AND SAY:

1. I am [relationship to case/appellant].

2. I make this affidavit in support of the Appellant's application to adduce fresh evidence on appeal.

THE FRESH EVIDENCE

3. [Describe the fresh evidence in detail]

4. [Explain what the evidence shows/proves]

EXPLANATION FOR NOT ADDUCING AT TRIAL

5. This evidence was not adduced at the trial because:
   [Explain why - e.g., not known, not available, overlooked by counsel]

6. [If applicable: Steps taken to obtain the evidence earlier]

CREDIBILITY

7. [Any matters relevant to credibility of the evidence]

ANNEXED DOCUMENTS

8. Annexed hereto and marked "[Exhibit A]" is [description of annexure].

SWORN at [PLACE] in the State of [STATE]
this _____ day of _______________ 20___

Before me:

_________________________________          _________________________________
[Signature of Deponent]                    [Justice of the Peace/Solicitor]
"""
            zip_file.writestr("07_Templates/Fresh_Evidence_Affidavit_Template.txt", affidavit_template)
            
            # Chronology Template
            chronology_template = f"""CHRONOLOGY OF PROCEEDINGS
{'='*50}

IN THE COURT OF CRIMINAL APPEAL
SUPREME COURT OF {case.get('state', 'NSW').upper()}

APPELLANT: {case.get('defendant_name', '[APPELLANT NAME]')}
CASE NUMBER: {case.get('case_number', '[CASE NUMBER]')}

DATE                | EVENT                              | REFERENCE
--------------------|------------------------------------|-----------
[DD/MM/YYYY]        | [Event description]                | [TB page]
[DD/MM/YYYY]        | [Event description]                | [TB page]
[DD/MM/YYYY]        | [Event description]                | [TB page]
[DD/MM/YYYY]        | [Event description]                | [TB page]
[DD/MM/YYYY]        | [Event description]                | [TB page]
[DD/MM/YYYY]        | Conviction                         | [TB page]
[DD/MM/YYYY]        | Sentence                           | [TB page]
[DD/MM/YYYY]        | Notice of Appeal filed             | 
[DD/MM/YYYY]        | Appeal Hearing                     | 

TB = Trial Bundle
AB = Appeal Book

Notes:
- [Any relevant notes about the chronology]
"""
            zip_file.writestr("07_Templates/Chronology_Template.txt", chronology_template)
        
        # 8. README
        readme = f"""APPEAL CASE PACKAGE
{'='*50}

Case: {case.get('title', 'Unknown')}
Defendant: {case.get('defendant_name', 'Unknown')}
Exported: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')}

CONTENTS:
---------

00_Case_Summary.txt/json  - Basic case information
01_Documents/             - All uploaded documents with extracted text
02_Timeline/              - Chronological timeline of events
03_Grounds/               - Identified grounds of merit
04_Notes/                 - Case notes and observations
05_Reports/               - Generated reports (Quick Summary, Full, Extensive)
06_AI_Analysis/           - AI contradiction analysis findings
07_Templates/             - Editable legal document templates:
                           - Notice of Appeal
                           - Leave to Appeal Application
                           - Written Submissions
                           - Fresh Evidence Affidavit
                           - Chronology of Proceedings

IMPORTANT DISCLAIMER:
--------------------
This package was generated by Appeal Case Manager.
This is NOT legal advice. All documents should be reviewed
by a qualified legal professional before submission to any court.

The creator of this tool, Debra King, is not a lawyer.
Always seek independent legal advice.

For questions: {get_contact_email()}
"""
        zip_file.writestr("README.txt", readme)
    
    # Prepare response
    zip_buffer.seek(0)
    
    # Generate filename
    safe_title = "".join(c for c in case.get("title", "case")[:30] if c.isalnum() or c in " -_").strip()
    filename = f"Appeal_Package_{safe_title}_{datetime.now().strftime('%Y%m%d')}.zip"
    
    return StreamingResponse(
        zip_buffer,
        media_type="application/zip",
        headers={
            "Content-Disposition": f'attachment; filename="{filename}"'
        }
    )


@router.get("/preview")
async def preview_export(case_id: str, request: Request):
    """
    Preview what will be included in the export package.
    """
    user = await get_current_user(request)
    await verify_case_ownership(case_id, user.user_id)
    
    # Count items
    doc_count = await db.documents.count_documents({"case_id": case_id})
    timeline_count = await db.timeline_events.count_documents({"case_id": case_id})
    grounds_count = await db.grounds_of_merit.count_documents({"case_id": case_id})
    notes_count = await db.notes.count_documents({"case_id": case_id})
    reports_count = await db.reports.count_documents({"case_id": case_id})
    scans_count = await db.contradiction_scans.count_documents({"case_id": case_id})
    
    return {
        "documents": doc_count,
        "timeline_events": timeline_count,
        "grounds_of_merit": grounds_count,
        "notes": notes_count,
        "reports": reports_count,
        "ai_analysis_scans": scans_count,
        "templates": 5,  # Fixed number of templates
        "estimated_files": doc_count + 2 + 2 + 2 + notes_count + reports_count + 2 + 5 + 1  # Rough estimate
    }


class BundleRequest(BaseModel):
    document_ids: List[str]
    include_toc: bool = True
    title: str = "Document Bundle"


@router.post("/bundle")
async def create_document_bundle(case_id: str, bundle_request: BundleRequest, request: Request):
    """
    Bundle selected documents into a single PDF with table of contents.
    """
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import cm
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, Table, TableStyle
    from reportlab.lib import colors
    
    user = await get_current_user(request)
    await verify_case_ownership(case_id, user.user_id)
    
    if not bundle_request.document_ids:
        raise HTTPException(status_code=400, detail="No documents selected")
    
    # Fetch case
    case = await db.cases.find_one({"case_id": case_id}, {"_id": 0})
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
    
    # Fetch selected documents
    documents = await db.documents.find(
        {"case_id": case_id, "document_id": {"$in": bundle_request.document_ids}},
        {"_id": 0, "file_data": 0}
    ).to_list(100)
    
    if not documents:
        raise HTTPException(status_code=404, detail="No documents found")
    
    # Create PDF
    pdf_buffer = io.BytesIO()
    pdf_doc = SimpleDocTemplate(
        pdf_buffer,
        pagesize=A4,
        rightMargin=2*cm,
        leftMargin=2*cm,
        topMargin=2*cm,
        bottomMargin=2*cm
    )
    
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        spaceAfter=30,
        alignment=1  # Center
    )
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=16,
        spaceBefore=20,
        spaceAfter=10
    )
    body_style = ParagraphStyle(
        'CustomBody',
        parent=styles['Normal'],
        fontSize=11,
        leading=14
    )
    
    story = []
    
    # Title Page
    story.append(Spacer(1, 3*cm))
    story.append(Paragraph(bundle_request.title, title_style))
    story.append(Spacer(1, 1*cm))
    story.append(Paragraph(f"Case: {case.get('title', 'Unknown')}", styles['Normal']))
    story.append(Paragraph(f"Defendant: {case.get('defendant_name', 'Unknown')}", styles['Normal']))
    story.append(Paragraph(f"Generated: {datetime.now().strftime('%d %B %Y')}", styles['Normal']))
    story.append(Spacer(1, 2*cm))
    story.append(Paragraph(f"Contains {len(documents)} document(s)", styles['Normal']))
    story.append(PageBreak())
    
    # Table of Contents
    if bundle_request.include_toc:
        story.append(Paragraph("Table of Contents", title_style))
        story.append(Spacer(1, 0.5*cm))
        
        toc_data = [["#", "Document", "Category", "Page"]]
        current_page = 3  # Start after title and TOC
        
        for i, doc in enumerate(documents, 1):
            category = doc.get("category", "general").replace("_", " ").title()
            toc_data.append([str(i), doc.get("filename", "Unknown")[:40], category, str(current_page)])
            # Estimate pages based on text length
            text_len = len(doc.get("extracted_text", ""))
            current_page += max(1, text_len // 3000)
        
        toc_table = Table(toc_data, colWidths=[1*cm, 9*cm, 4*cm, 2*cm])
        toc_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Times-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('FONTSIZE', (0, 1), (-1, -1), 9),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ]))
        story.append(toc_table)
        story.append(PageBreak())
    
    # Document Contents
    for i, doc in enumerate(documents, 1):
        # Document header
        story.append(Paragraph(f"Document {i}: {doc.get('filename', 'Unknown')}", heading_style))
        story.append(Paragraph(f"Category: {doc.get('category', 'N/A').replace('_', ' ').title()}", styles['Normal']))
        story.append(Paragraph(f"Uploaded: {doc.get('upload_date', 'N/A')}", styles['Normal']))
        story.append(Spacer(1, 0.5*cm))
        
        # Document text
        text = doc.get("extracted_text", "No text extracted from this document.")
        # Clean and split text into paragraphs
        paragraphs = text.split('\n\n')
        for para in paragraphs[:100]:  # Limit paragraphs
            if para.strip():
                # Escape special characters for ReportLab
                clean_para = para.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
                try:
                    story.append(Paragraph(clean_para[:2000], body_style))
                    story.append(Spacer(1, 0.3*cm))
                except Exception:
                    pass
        
        # AI Analysis if available
        if doc.get("ai_analysis"):
            story.append(Spacer(1, 0.5*cm))
            story.append(Paragraph("AI Analysis:", heading_style))
            analysis = doc.get("ai_analysis", "").replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
            try:
                story.append(Paragraph(analysis[:3000], body_style))
            except Exception:
                pass
        
        if i < len(documents):
            story.append(PageBreak())
    
    # Legal Disclaimer
    story.append(Spacer(1, 1*cm))
    disclaimer_style = ParagraphStyle(
        'Disclaimer',
        parent=styles['Normal'],
        fontSize=9,
        leading=12,
        textColor=colors.HexColor('#1e293b'),
        borderWidth=2,
        borderColor=colors.HexColor('#ef4444'),
        borderPadding=10,
    )
    disclaimer_text = (
        "<b>NOT LEGAL ADVICE</b> — This application is an educational research tool only and does NOT constitute legal advice. "
        "The creator is not a lawyer. All analysis and recommendations must be independently verified by a qualified "
        "Australian legal professional. Australian law only. No solicitor-client relationship is created."
    )
    story.append(Paragraph(disclaimer_text, disclaimer_style))

    # Build PDF
    pdf_doc.build(story)
    pdf_buffer.seek(0)
    
    # Generate filename
    safe_title = "".join(c for c in bundle_request.title[:30] if c.isalnum() or c in " -_").strip()
    filename = f"{safe_title.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d')}.pdf"
    
    return StreamingResponse(
        pdf_buffer,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f'attachment; filename="{filename}"'
        }
    )


# ============================================================================
# CASE EXPORT PACK — Properly formatted PDF with ALL paid reports
# ============================================================================

REPORT_TYPE_ORDER = ["quick_summary", "full_detailed", "extensive_log", "barrister_view"]
REPORT_TYPE_LABELS = {
    "quick_summary": "Quick Case Summary (Free)",
    "full_detailed": "Full Detailed Legal Analysis ($150 AUD)",
    "extensive_log": "Extensive Case Log & Analysis ($200 AUD)",
    "barrister_view": "Appellate Research Brief (Counsel Synthesis)",
}
GROUND_TYPE_LABELS = {
    "procedural_error": "Procedural Error",
    "fresh_evidence": "Fresh Evidence",
    "miscarriage_of_justice": "Miscarriage of Justice",
    "sentencing_error": "Sentencing Error",
    "judicial_error": "Judicial Error",
    "ineffective_counsel": "Ineffective Counsel",
    "prosecution_misconduct": "Prosecution Misconduct",
    "jury_irregularity": "Jury Irregularity",
    "constitutional_violation": "Constitutional Violation",
    "other": "Other",
}


def _format_inline(text: str) -> str:
    clean = (text or "").replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    clean = re.sub(r"\*\*(.*?)\*\*", r"<b>\1</b>", clean)
    clean = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", clean)
    return clean


def _strip_placeholders(text: str) -> str:
    if not text:
        return text
    lines = []
    for line in text.splitlines():
        if re.search(r"\[Your Name\]|\[Your Legal Organisation/Team\]", line, re.I):
            continue
        if re.search(r"Best regards|Prepared by|Prepared for|This report was generated by|Criminal Appeal AI|Justitia AI", line, re.I):
            continue
        lines.append(line)
    cleaned = "\n".join(lines)
    cleaned = re.sub(r"\n{3,}", "\n\n", cleaned).strip()
    cleaned = cleaned.replace("\\1", "").replace("\x01", "")
    cleaned = re.sub(r'\s*—\s*keep ALL[^\n]*', '', cleaned)
    cleaned = re.sub(r'\s*—\s*DETAILED PATHWAY ANALYSIS[^\n]*', '', cleaned)
    cleaned = re.sub(r'\s*\(\d+\+?\s*words[^)]*\)', '', cleaned)
    cleaned = re.sub(r'\s*\(\d+\+?\s*CASES[^)]*\)', '', cleaned)
    cleaned = re.sub(r'(GROUNDS OF MERIT)\s*—\s*DEEP ANALYSIS', r'\1', cleaned)
    return cleaned


def _render_table_to_story(lines, story_ref, doc_ref, body_style=None):
    """Module-level table renderer for PDF exports."""
    from reportlab.lib import colors
    from reportlab.lib.units import mm
    from reportlab.lib.styles import ParagraphStyle
    from reportlab.platypus import Paragraph, Spacer, Table, TableStyle

    rows = []
    for line in lines:
        parts = [p.strip() for p in line.strip().strip("|").split("|")]
        if not parts:
            continue
        if all(set(p) <= set("-:") for p in parts):
            continue
        safe_parts = [re.sub(r"\*\*(.*?)\*\*", r"\1", p).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;") for p in parts]
        rows.append(safe_parts)
    if not rows:
        return
    col_count = max(len(r) for r in rows)
    rows = [r + [""] * (col_count - len(r)) for r in rows]
    try:
        col_width = doc_ref.width / col_count
        cell_style = ParagraphStyle(name="TblCell", fontSize=9, leading=12, fontName="Times-Roman", wordWrap="CJK")
        header_cell = ParagraphStyle(name="TblHeader", fontSize=9, leading=12, fontName="Times-Bold", textColor=colors.white)
        para_rows = []
        for ri, row in enumerate(rows):
            st = header_cell if ri == 0 else cell_style
            para_rows.append([Paragraph(c[:260], st) for c in row])
        table = Table(para_rows, colWidths=[col_width] * col_count, repeatRows=1)
        table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1e293b")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.whitesmoke, colors.white]),
            ("LEFTPADDING", (0, 0), (-1, -1), 4),
            ("RIGHTPADDING", (0, 0), (-1, -1), 4),
            ("TOPPADDING", (0, 0), (-1, -1), 3),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
        ]))
        story_ref.append(table)
        story_ref.append(Spacer(1, 4 * mm))
    except Exception as e:
        logger.warning(f"Table render failed: {e}")
        fallback = body_style or cell_style
        for row in rows:
            story_ref.append(Paragraph(" | ".join(row), fallback))


@router.get("/case-pack")
async def generate_case_export_pack(case_id: str, request: Request):
    """
    Generate a properly formatted PDF containing ALL paid/generated reports
    with correct legal formatting: fonts, headings, margins, page numbers.
    Only includes reports the user has actually generated.
    """
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import mm
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
    from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY

    user = await get_current_user(request)
    await verify_case_ownership(case_id, user.user_id)

    # Fetch case
    case = await db.cases.find_one({"case_id": case_id}, {"_id": 0})
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")

    # Fetch ALL completed reports for this case, ordered by type
    reports = await db.reports.find(
        {"case_id": case_id, "user_id": user.user_id, "status": "completed"},
        {"_id": 0},
    ).sort("generated_at", -1).to_list(50)

    if not reports:
        raise HTTPException(status_code=404, detail="No completed reports found. Generate at least one report first.")

    # Deduplicate: keep latest of each report_type
    seen_types = set()
    unique_reports = []
    for r in reports:
        rt = r.get("report_type")
        if rt not in seen_types:
            seen_types.add(rt)
            unique_reports.append(r)

    # Sort by tier order
    unique_reports.sort(key=lambda r: REPORT_TYPE_ORDER.index(r.get("report_type")) if r.get("report_type") in REPORT_TYPE_ORDER else 99)

    # Fetch grounds
    grounds = await db.grounds_of_merit.find({"case_id": case_id}, {"_id": 0}).to_list(100)

    # Fetch timeline
    timeline = await db.timeline_events.find({"case_id": case_id}, {"_id": 0}).sort("event_date", 1).to_list(500)

    # ── Build PDF ── canonical margins (locked 24 Feb 2026)
    from services.print_styles import (
        canonical_page_margins_mm,
        CANONICAL_H1_PT, CANONICAL_H2_PT, CANONICAL_H3_PT,
        CANONICAL_BODY_PT,
    )
    _m = canonical_page_margins_mm()
    pdf_buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        pdf_buffer,
        pagesize=A4,
        rightMargin=_m["right"] * mm,
        leftMargin=_m["left"] * mm,
        topMargin=_m["top"] * mm,
        bottomMargin=_m["bottom"] * mm,
    )

    # Canonical typography (locked 24 Feb 2026): Times New Roman only.
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name="PackTitle", fontSize=CANONICAL_H1_PT, spaceAfter=6, alignment=TA_CENTER, fontName="Times-Bold", textColor=colors.HexColor("#0f172a")))
    styles.add(ParagraphStyle(name="PackSubtitle", fontSize=CANONICAL_BODY_PT, spaceAfter=6, alignment=TA_CENTER, fontName="Times-Roman", textColor=colors.HexColor("#475569")))
    styles.add(ParagraphStyle(name="PackSection", fontSize=CANONICAL_H1_PT, spaceBefore=10, spaceAfter=6, fontName="Times-Bold", textColor=colors.HexColor("#0f172a"), keepWithNext=True))
    styles.add(ParagraphStyle(name="PackSubSection", fontSize=CANONICAL_H2_PT, spaceBefore=8, spaceAfter=3, fontName="Times-Bold", textColor=colors.HexColor("#1e293b"), keepWithNext=True))
    styles.add(ParagraphStyle(name="PackBody", fontSize=CANONICAL_BODY_PT, spaceAfter=6, alignment=TA_JUSTIFY, leading=CANONICAL_BODY_PT*1.35, fontName="Times-Roman"))
    styles.add(ParagraphStyle(name="PackBullet", parent=styles["PackBody"], leftIndent=14, bulletIndent=7))
    styles.add(ParagraphStyle(name="PackLaw", fontSize=CANONICAL_BODY_PT, spaceAfter=3, leftIndent=18, fontName="Times-Italic", textColor=colors.HexColor("#1e40af")))
    styles.add(ParagraphStyle(name="PackGround", fontSize=CANONICAL_H3_PT, spaceBefore=6, spaceAfter=3, fontName="Times-BoldItalic", textColor=colors.HexColor("#1e3a8a"), keepWithNext=True))
    styles.add(ParagraphStyle(name="PackDisclaimer", fontSize=CANONICAL_BODY_PT, fontName="Times-Bold", textColor=colors.HexColor("#dc2626"), alignment=TA_CENTER, leading=CANONICAL_BODY_PT*1.35))
    styles.add(ParagraphStyle(name="PackMetaLabel", fontSize=8, fontName="Times-Bold", textColor=colors.HexColor("#64748b"), spaceAfter=2))
    styles.add(ParagraphStyle(name="PackMetaValue", fontSize=CANONICAL_BODY_PT, fontName="Times-Bold", textColor=colors.HexColor("#0f172a"), spaceAfter=4))
    styles.add(ParagraphStyle(name="PackTocEntry", fontSize=CANONICAL_BODY_PT, spaceAfter=3, leftIndent=10, leading=CANONICAL_BODY_PT*1.35, fontName="Times-Roman"))
    styles.add(ParagraphStyle(name="PackReportTitle", fontSize=CANONICAL_H1_PT, spaceBefore=8, spaceAfter=6, fontName="Times-Bold", textColor=colors.HexColor("#1e3a8a"), alignment=TA_CENTER, keepWithNext=True))
    styles.add(ParagraphStyle(name="PackNumberedHeader", fontSize=CANONICAL_H1_PT, spaceBefore=10, spaceAfter=6, fontName="Times-Bold", textColor=colors.HexColor("#0f172a"), keepWithNext=True))

    # ── Resolve sentence ──
    sentence = case.get("sentence") or "See report analysis"

    # ── Helpers ──
    def render_table_pack(lines, story_ref, doc_ref, body_style=None):
        _render_table_to_story(lines, story_ref, doc_ref, body_style)

    def render_markdown_pack(text, story_ref, doc_ref):
        lines = (text or "").splitlines()
        buffer = []
        table_lines = []

        def flush():
            if buffer:
                para = " ".join(buffer).strip()
                if para:
                    try:
                        story_ref.append(Paragraph(_format_inline(para), styles["PackBody"]))
                        story_ref.append(Spacer(1, 2 * mm))
                    except Exception:
                        safe = re.sub(r"<[^>]+>", "", para)
                        story_ref.append(Paragraph(safe, styles["PackBody"]))
                buffer.clear()

        for line in lines:
            stripped = line.strip()
            if not stripped:
                flush()
                continue
            if stripped.startswith("|") and "|" in stripped:
                flush()
                table_lines.append(stripped)
                continue
            if table_lines and not (stripped.startswith("|") and "|" in stripped):
                render_table_pack(table_lines, story_ref, doc_ref)
                table_lines = []
            if stripped.startswith("## "):
                flush()
                story_ref.append(Paragraph(_format_inline(stripped[3:].strip()), styles["PackSection"]))
                story_ref.append(Spacer(1, 2 * mm))
                continue
            if re.match(r"^\d+\.\s+[A-Z][A-Z0-9\s/&()\-]{4,}$", stripped):
                flush()
                story_ref.append(Paragraph(_format_inline(stripped), styles["PackNumberedHeader"]))
                story_ref.append(Spacer(1, 2 * mm))
                continue
            if stripped.startswith("### "):
                flush()
                story_ref.append(Paragraph(_format_inline(stripped[4:].strip()), styles["PackSubSection"]))
                story_ref.append(Spacer(1, 1 * mm))
                continue
            if stripped.startswith("#### "):
                flush()
                story_ref.append(Paragraph(_format_inline(stripped[5:].strip()), styles["PackSubSection"]))
                story_ref.append(Spacer(1, 1 * mm))
                continue
            if re.match(r"^Ground\s+\d+\s*:", stripped, re.I):
                flush()
                story_ref.append(Paragraph(_format_inline(stripped), styles["PackGround"]))
                story_ref.append(Spacer(1, 1 * mm))
                continue
            if stripped.startswith("- ") or stripped.startswith("• "):
                flush()
                story_ref.append(Paragraph(_format_inline(f"- {stripped[2:].strip()}"), styles["PackBullet"]))
                story_ref.append(Spacer(1, 1 * mm))
                continue
            if re.match(r"^\d+\.\s", stripped):
                flush()
                story_ref.append(Paragraph(_format_inline(stripped), styles["PackBullet"]))
                story_ref.append(Spacer(1, 1 * mm))
                continue
            buffer.append(stripped)

        flush()
        if table_lines:
            render_table_pack(table_lines, story_ref, doc_ref)

    story = []

    # ══════════════════════════════════════════════════════════════
    # COVER PAGE
    # ══════════════════════════════════════════════════════════════
    story.append(Spacer(1, 20 * mm))
    story.append(Paragraph("APPEAL CASE MANAGER", styles["PackSubtitle"]))
    story.append(Paragraph("Complete Case Export Pack", styles["PackTitle"]))
    story.append(Paragraph("Criminal Law Appeal Case Management", styles["PackSubtitle"]))
    story.append(Spacer(1, 12 * mm))

    cover_meta = [
        ["Case Title", case.get("title", "N/A")],
        ["Defendant", case.get("defendant_name", "N/A")],
        ["Court / State", f"{case.get('court', 'Court')} — {(case.get('state', 'NSW') or 'NSW').upper()}"],
        ["Reports Included", f"{len(unique_reports)} report(s)"],
        ["Offence", case.get("offence_type") or (case.get("offence_category") or "Not recorded").replace("_", " ").title()],
        ["Sentence", sentence],
    ]
    cover_rows = []
    for idx in range(0, len(cover_meta), 2):
        left = cover_meta[idx]
        right = cover_meta[idx + 1] if idx + 1 < len(cover_meta) else ["", ""]
        cover_rows.append([
            Paragraph(f"<b>{left[0]}</b><br/>{left[1]}", styles["PackMetaValue"]),
            Paragraph(f"<b>{right[0]}</b><br/>{right[1]}", styles["PackMetaValue"]),
        ])
    cover_table = Table(cover_rows, colWidths=[80 * mm, 80 * mm])
    cover_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#f8fafc")),
        ("BOX", (0, 0), (-1, -1), 1, colors.HexColor("#cbd5e1")),
        ("INNERGRID", (0, 0), (-1, -1), 1, colors.HexColor("#e2e8f0")),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 10),
        ("RIGHTPADDING", (0, 0), (-1, -1), 10),
        ("TOPPADDING", (0, 0), (-1, -1), 10),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 10),
    ]))
    story.append(cover_table)
    story.append(Spacer(1, 12 * mm))
    story.append(Paragraph(
        "IMPORTANT DISCLAIMER — NOT LEGAL ADVICE — This application is an educational research tool only "
        "and does NOT constitute legal advice. The creator is not a lawyer. All analysis and recommendations "
        "must be independently verified by a qualified Australian legal professional. Australian law only. "
        "No solicitor-client relationship is created.",
        styles["PackDisclaimer"],
    ))
    story.append(Spacer(1, 8 * mm))
    story.append(Paragraph(
        f"Exported: {datetime.now(timezone.utc).strftime('%d %B %Y at %H:%M UTC')}",
        styles["PackSubtitle"],
    ))
    story.append(PageBreak())

    # ══════════════════════════════════════════════════════════════
    # TABLE OF CONTENTS
    # ══════════════════════════════════════════════════════════════
    story.append(Paragraph("TABLE OF CONTENTS", styles["PackTitle"]))
    story.append(Spacer(1, 8 * mm))

    toc_num = 1
    if grounds:
        story.append(Paragraph(f"<b>{toc_num}.</b>  Grounds of Merit ({len(grounds)} identified)", styles["PackTocEntry"]))
        toc_num += 1
    if timeline:
        story.append(Paragraph(f"<b>{toc_num}.</b>  Case Timeline ({len(timeline)} events)", styles["PackTocEntry"]))
        toc_num += 1
    for r in unique_reports:
        label = REPORT_TYPE_LABELS.get(r.get("report_type"), "Report")
        story.append(Paragraph(f"<b>{toc_num}.</b>  {_format_inline(label)}", styles["PackTocEntry"]))
        toc_num += 1
    story.append(Paragraph(f"<b>{toc_num}.</b>  Legal Framework Reference", styles["PackTocEntry"]))
    story.append(Spacer(1, 6 * mm))
    story.append(Paragraph("Each section begins on a new page for clear separation.", styles["PackSubtitle"]))
    story.append(PageBreak())

    # ══════════════════════════════════════════════════════════════
    # SECTION: GROUNDS OF MERIT
    # ══════════════════════════════════════════════════════════════
    if grounds:
        story.append(Paragraph("GROUNDS OF MERIT", styles["PackSection"]))
        story.append(Spacer(1, 5 * mm))
        for idx, ground in enumerate(grounds, 1):
            gtype = GROUND_TYPE_LABELS.get(ground.get("ground_type"), "Other")
            strength = ground.get("strength", "moderate").capitalize()
            story.append(Paragraph(
                f"{idx}. {_format_inline(ground.get('title', 'Unnamed Ground'))} [{gtype}] — Strength: {strength}",
                styles["PackGround"],
            ))
            if ground.get("description"):
                story.append(Paragraph(_format_inline(ground["description"]), styles["PackBody"]))
            if ground.get("analysis"):
                story.append(Paragraph(_format_inline(ground["analysis"]), styles["PackBody"]))
            if ground.get("law_sections"):
                story.append(Paragraph("<b>Relevant Law Sections:</b>", styles["PackBody"]))
                for sec in ground["law_sections"]:
                    story.append(Paragraph(
                        f"- s.{sec.get('section', '')} {sec.get('act', '')} ({sec.get('jurisdiction', 'NSW')})",
                        styles["PackLaw"],
                    ))
            if ground.get("similar_cases"):
                story.append(Paragraph("<b>Similar Cases:</b>", styles["PackBody"]))
                for cr in ground["similar_cases"]:
                    story.append(Paragraph(f"- {cr.get('case_name', '')} {cr.get('citation', '')}", styles["PackLaw"]))
            if ground.get("supporting_evidence"):
                story.append(Paragraph("<b>Supporting Evidence:</b>", styles["PackBody"]))
                for ev in ground["supporting_evidence"]:
                    story.append(Paragraph(f"- {_format_inline(ev if isinstance(ev, str) else str(ev))}", styles["PackLaw"]))
            story.append(Spacer(1, 6 * mm))
        story.append(PageBreak())

    # ══════════════════════════════════════════════════════════════
    # SECTION: TIMELINE
    # ══════════════════════════════════════════════════════════════
    if timeline:
        story.append(Paragraph("CASE TIMELINE", styles["PackSection"]))
        story.append(Spacer(1, 5 * mm))
        tl_data = [["Date", "Event", "Category", "Significance"]]
        for ev in timeline:
            tl_data.append([
                str(ev.get("event_date", "Unknown"))[:10],
                str(ev.get("title", ""))[:60],
                str(ev.get("event_category", "")).replace("_", " ").title()[:25],
                str(ev.get("significance", "")).title()[:15],
            ])
        try:
            cell_style = ParagraphStyle(name="TLCell", fontSize=9, leading=11, fontName="Times-Roman")
            hdr_style = ParagraphStyle(name="TLHeader", fontSize=9, leading=11, fontName="Times-Bold", textColor=colors.white)
            para_rows = []
            for ri, row in enumerate(tl_data):
                st = hdr_style if ri == 0 else cell_style
                para_rows.append([Paragraph(c, st) for c in row])
            tl_table = Table(para_rows, colWidths=[25 * mm, 70 * mm, 35 * mm, 25 * mm], repeatRows=1)
            tl_table.setStyle(TableStyle([
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1e293b")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.whitesmoke, colors.white]),
                ("LEFTPADDING", (0, 0), (-1, -1), 4),
                ("RIGHTPADDING", (0, 0), (-1, -1), 4),
                ("TOPPADDING", (0, 0), (-1, -1), 3),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
            ]))
            story.append(tl_table)
        except Exception as e:
            logger.warning(f"Timeline table failed: {e}")
            for ev in timeline:
                story.append(Paragraph(f"[{ev.get('event_date', '?')}] {ev.get('title', '')}", styles["PackBody"]))
        story.append(PageBreak())

    # ══════════════════════════════════════════════════════════════
    # SECTION: EACH REPORT — FULL CONTENT
    # ══════════════════════════════════════════════════════════════
    for report in unique_reports:
        report_label = REPORT_TYPE_LABELS.get(report.get("report_type"), "Report")
        story.append(Paragraph(report_label, styles["PackReportTitle"]))
        story.append(Spacer(1, 3 * mm))
        gen_date = report.get("generated_at", "")[:10] if report.get("generated_at") else "N/A"
        story.append(Paragraph(f"Generated: {gen_date}", styles["PackSubtitle"]))
        story.append(Spacer(1, 8 * mm))

        # Case info mini-table
        info_rows = [
            ["Case:", case.get("title", "N/A")],
            ["Defendant:", case.get("defendant_name", "N/A")],
        ]
        if case.get("court"):
            info_rows.append(["Court:", case["court"]])
        if case.get("state"):
            info_rows.append(["Jurisdiction:", case["state"].upper()])
        info_table = Table(info_rows, colWidths=[35 * mm, 120 * mm])
        info_table.setStyle(TableStyle([
            ("FONTNAME", (0, 0), (0, -1), "Times-Bold"),
            ("FONTSIZE", (0, 0), (-1, -1), 10),
            ("TEXTCOLOR", (0, 0), (0, -1), colors.HexColor("#475569")),
            ("ALIGN", (0, 0), (0, -1), "RIGHT"),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
            ("TOPPADDING", (0, 0), (-1, -1), 5),
        ]))
        story.append(info_table)
        story.append(Spacer(1, 8 * mm))

        # Report content
        analysis = _strip_placeholders((report.get("content") or {}).get("analysis", "No analysis available."))
        render_markdown_pack(analysis, story, doc)

        # Separator + disclaimer before next report
        story.append(Spacer(1, 10 * mm))
        story.append(Paragraph(
            "NOT LEGAL ADVICE — This section is an educational research tool only. "
            "All analysis must be verified by a qualified Australian legal professional.",
            styles["PackDisclaimer"],
        ))
        story.append(PageBreak())

    # ══════════════════════════════════════════════════════════════
    # SECTION: LEGAL FRAMEWORK REFERENCE
    # ══════════════════════════════════════════════════════════════
    story.append(Paragraph("LEGAL FRAMEWORK REFERENCE", styles["PackSection"]))
    story.append(Spacer(1, 3 * mm))
    legal_refs = [
        "Crimes Act 1900 (NSW) — Primary criminal law for New South Wales",
        "Criminal Appeal Act 1912 (NSW) — Governs criminal appeals in NSW",
        "Criminal Code Act 1995 (Cth) — Federal criminal law",
        "Evidence Act 1995 (NSW &amp; Cth) — Rules on evidence admissibility",
        "Sentencing Act 1995 (NSW) — Sentencing guidelines and procedures",
    ]
    for ref in legal_refs:
        story.append(Paragraph(f"- {ref}", styles["PackLaw"]))

    # Final disclaimer
    story.append(Spacer(1, 15 * mm))
    story.append(Paragraph("IMPORTANT DISCLAIMER — NOT LEGAL ADVICE", ParagraphStyle(
        name="FinalDiscTitle", fontSize=12, fontName="Times-Bold", alignment=TA_CENTER,
        textColor=colors.HexColor("#dc2626"), spaceAfter=4,
    )))
    story.append(Paragraph(
        "This application is an educational research tool only and does NOT constitute legal advice. "
        "It must NOT be relied upon as such. The creator of this application is not a lawyer. "
        "All analysis, findings, reports, and recommendations generated by this tool must be independently verified "
        "by a qualified Australian legal professional before any action is taken. This tool covers Australian law only. "
        "No solicitor-client relationship is created by using this service.",
        styles["PackDisclaimer"],
    ))

    # ── Footer ──
    from services.export_footer import build_footer_label, NumberedCanvas
    footer_label = build_footer_label(case, "Case Export Pack")
    numbered_canvas = NumberedCanvas(footer_label)

    # Build
    try:
        doc.build(story, canvasmaker=numbered_canvas)
    except Exception as e:
        logger.error(f"Case Export Pack PDF build failed: {e}")
        raise HTTPException(status_code=500, detail=f"PDF generation failed: {str(e)[:200]}")

    pdf_buffer.seek(0)
    safe_title = "".join(c for c in case.get("title", "Case")[:30] if c.isalnum() or c in " -_").strip()
    filename = f"Case_Export_Pack_{safe_title}_{datetime.now().strftime('%Y%m%d')}.pdf"

    return StreamingResponse(
        pdf_buffer,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


# Translation routes moved to routers/translate.py
# Re-export for backward compatibility with routers/__init__.py
from routers.translate import translate_router  # noqa: F401, E402
