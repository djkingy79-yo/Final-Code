# DO NOT UNDO — export router. All endpoints in this file are approved and must be preserved.
"""
Criminal Appeal AI - Export Router
Handles Quick Export (Appeal Package) generation - ZIP with all docs, reports, and editable templates
"""
from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import StreamingResponse
from typing import List
from datetime import datetime, timezone
from pydantic import BaseModel
import io
import zipfile
import json

from config import db, get_contact_email
from auth_utils import get_current_user, verify_case_ownership

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
                analysis_txt += f"Documents Analysed: {latest_scan.get('documents_analyzed', 0)}\n\n"
                
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
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
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
