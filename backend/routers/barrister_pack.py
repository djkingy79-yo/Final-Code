# DO NOT UNDO — barrister_pack router. Extracted from pipeline.py.
"""
Criminal Appeal AI - Barrister Acceptance Pack Generator
Generates a comprehensive PDF pack for barrister review containing:
case summary, ranked grounds, timeline, evidence annexures, notes, and verification summary.
"""
from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import StreamingResponse
from datetime import datetime, timezone
import logging

from config import db
from auth_utils import get_current_user, verify_case_ownership

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/cases", tags=["barrister-pack"])


@router.get("/{case_id}/barrister-pack/generate")
async def generate_barrister_pack(case_id: str, request: Request):
    """Generate a Barrister Acceptance Pack as PDF.
    Contains: case summary, ranked grounds, timeline, evidence annexures, notes, verification summary.
    """
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import mm
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, HRFlowable
    from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY
    from io import BytesIO

    user = await get_current_user(request)
    await verify_case_ownership(case_id, user.user_id)

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

    notes = await db.notes.find(
        {"case_id": case_id, "user_id": user.user_id},
        {"_id": 0}
    ).sort("created_at", -1).to_list(100)

    # Build PDF — margins locked to canonical print spec (24 Feb 2026).
    from services.print_styles import (
        canonical_page_margins_mm,
        CANONICAL_H1_PT, CANONICAL_H2_PT, CANONICAL_H3_PT,
        CANONICAL_BODY_PT, CANONICAL_TABLE_SHRINK_PT,
    )
    _m = canonical_page_margins_mm()
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer, pagesize=A4,
        rightMargin=_m["right"]*mm, leftMargin=_m["left"]*mm,
        topMargin=_m["top"]*mm, bottomMargin=_m["bottom"]*mm,
    )

    # Canonical typography (locked 24 Feb 2026): Times New Roman everywhere,
    # H1 14.5pt bold, H2 12.5pt bold, H3 11.5pt bold italic, body 10pt.
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name="PackTitle", fontName="Times-Bold", fontSize=CANONICAL_H1_PT, spaceAfter=6, textColor=colors.HexColor("#0f172a"), alignment=TA_CENTER))
    styles.add(ParagraphStyle(name="PackSubtitle", fontName="Times-Roman", fontSize=CANONICAL_BODY_PT, spaceAfter=8, textColor=colors.HexColor("#64748b"), alignment=TA_CENTER))
    styles.add(ParagraphStyle(name="SectionHead", fontName="Times-Bold", fontSize=CANONICAL_H1_PT, spaceAfter=6, spaceBefore=12, textColor=colors.HexColor("#0f4c81"), keepWithNext=True))
    styles.add(ParagraphStyle(name="SubHead", fontName="Times-Bold", fontSize=CANONICAL_H2_PT, spaceAfter=3, spaceBefore=8, textColor=colors.HexColor("#1e293b"), keepWithNext=True))
    styles.add(ParagraphStyle(name="BodyText2", fontName="Times-Roman", fontSize=CANONICAL_BODY_PT, spaceAfter=6, leading=CANONICAL_BODY_PT*1.35, alignment=TA_JUSTIFY))
    styles.add(ParagraphStyle(name="Small", fontName="Times-Roman", fontSize=CANONICAL_TABLE_SHRINK_PT, spaceAfter=3, textColor=colors.HexColor("#475569"), leading=CANONICAL_TABLE_SHRINK_PT*1.3))
    styles.add(ParagraphStyle(name="Disclaimer", fontName="Times-Italic", fontSize=8, spaceAfter=4, textColor=colors.HexColor("#94a3b8"), alignment=TA_CENTER))

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
            ("FONTNAME", (0, 0), (0, -1), "Times-Bold"),
            ("FONTSIZE", (0, 0), (-1, -1), 9),
            ("TEXTCOLOR", (0, 0), (0, -1), colors.HexColor("#475569")),
            ("TEXTCOLOR", (1, 0), (1, -1), colors.HexColor("#0f172a")),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
            ("TOPPADDING", (0, 0), (-1, -1), 5),
            ("LINEBELOW", (0, 0), (-1, -2), 0.5, colors.HexColor("#e2e8f0")),
        ]))
        elements.append(t)

    elements.append(Spacer(1, 15*mm))
    elements.append(Paragraph("NOT LEGAL ADVICE — This document is AI-assisted preparation material for legal review. It does not constitute legal advice and should not be relied upon as a substitute for independent legal judgement.", styles["Disclaimer"]))
    elements.append(PageBreak())

    # ── CASE SUMMARY ──
    case_summary = case.get("summary", "")
    if case_summary:
        elements.append(Paragraph("Case Summary", styles["SectionHead"]))
        elements.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#0f4c81")))
        elements.append(Spacer(1, 3*mm))
        for para in case_summary.split("\n\n"):
            para = para.strip()
            if para:
                elements.append(Paragraph(para.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;"), styles["BodyText2"]))
        elements.append(PageBreak())

    # ── SECTION 1: GROUNDS OF MERIT (RANKED) ──
    elements.append(Paragraph("1. Grounds of Merit", styles["SectionHead"]))
    elements.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#0f4c81")))
    elements.append(Spacer(1, 3*mm))

    if not grounds:
        elements.append(Paragraph("No grounds of merit have been identified for this case.", styles["BodyText2"]))
    else:
        strength_order = {"strong": 0, "moderate": 1, "weak": 2}
        sorted_grounds = sorted(grounds, key=lambda g: strength_order.get(g.get("strength", "moderate"), 1))

        def safe_para(text):
            return (text or "").replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

        for idx, g in enumerate(sorted_grounds, 1):
            strength = str(g.get("strength", "moderate")).upper()
            elements.append(Paragraph(f"Ground {idx}: {safe_para(g.get('title', 'Untitled'))}", styles["SubHead"]))

            meta_parts = [f"<b>Strength:</b> {strength}"]
            vs = g.get("verification_status", "unverified")
            meta_parts.append(f"<b>Verification:</b> {vs}")
            gt = g.get("ground_type", "")
            if gt:
                meta_parts.append(f"<b>Type:</b> {gt.replace('_', ' ').title()}")
            elements.append(Paragraph(" &nbsp;|&nbsp; ".join(meta_parts), styles["Small"]))

            desc = g.get("description", "")
            if desc:
                elements.append(Paragraph(safe_para(desc), styles["BodyText2"]))

            pathway = g.get("appellate_pathway", "")
            if pathway:
                elements.append(Paragraph(f"<b>Appellate Pathway:</b> {safe_para(pathway)}", styles["BodyText2"]))

            ls = g.get("legitimacy_scores")
            if ls:
                score_text = f"Legal basis: {ls.get('legal_score', 0)}/3 &nbsp;|&nbsp; Evidence support: {ls.get('evidence_score', 0)}/3 &nbsp;|&nbsp; Appellate viability: {ls.get('viability_score', 0)}/3 &nbsp;|&nbsp; <b>Total: {ls.get('total_score', 0)}/9</b>"
                elements.append(Paragraph(score_text, styles["Small"]))

            evidence = g.get("supporting_evidence", [])
            if evidence:
                elements.append(Paragraph(f"<b>Supporting Evidence ({len(evidence)}):</b>", styles["SubHead"]))
                for e in evidence[:8]:
                    quote = e.get("quote", e) if isinstance(e, dict) else str(e)
                    fname = e.get("filename", "") if isinstance(e, dict) else ""
                    prefix = f"<b>{safe_para(fname)}:</b> " if fname else ""
                    elements.append(Paragraph(f"&nbsp;&nbsp;&bull; {prefix}{safe_para(str(quote)[:300])}", styles["BodyText2"]))

            law = g.get("law_sections", [])
            if law:
                elements.append(Paragraph(f"<b>Relevant Legislation ({len(law)}):</b>", styles["SubHead"]))
                for law_item in law[:10]:
                    if isinstance(law_item, dict):
                        elements.append(Paragraph(f"&nbsp;&nbsp;&bull; s {safe_para(law_item.get('section', ''))} {safe_para(law_item.get('act', ''))} {('— ' + safe_para(law_item.get('title', ''))) if law_item.get('title') else ''} ({safe_para((law_item.get('jurisdiction', 'NSW')).upper())})", styles["BodyText2"]))
                    elif isinstance(law_item, str):
                        elements.append(Paragraph(f"&nbsp;&nbsp;&bull; {safe_para(law_item)}", styles["BodyText2"]))

            similar = g.get("similar_cases", [])
            valid_cases = [c for c in similar if isinstance(c, dict) and c.get("case_name") and c["case_name"] not in ("Case name", "None", "optional") and "[Surname]" not in c["case_name"]]
            if valid_cases:
                elements.append(Paragraph(f"<b>Similar Cases ({len(valid_cases)}):</b>", styles["SubHead"]))
                for c in valid_cases[:6]:
                    case_text = safe_para(c.get("case_name", ""))
                    if c.get("citation"):
                        case_text += f" — {safe_para(c['citation'])}"
                    if c.get("relevance_note"):
                        case_text += f": {safe_para(c['relevance_note'])}"
                    elements.append(Paragraph(f"&nbsp;&nbsp;&bull; {case_text}", styles["BodyText2"]))

            deep = g.get("deep_analysis", {})
            full_analysis = deep.get("full_analysis", "") if isinstance(deep, dict) else ""
            if not full_analysis:
                full_analysis = g.get("analysis", "")
            if full_analysis:
                elements.append(Paragraph("<b>Deep Investigation Analysis:</b>", styles["SubHead"]))
                for para in full_analysis.split("\n\n"):
                    para = para.strip()
                    if not para:
                        continue
                    if para.startswith("##"):
                        heading = para.lstrip("#").strip()
                        elements.append(Paragraph(safe_para(heading), styles["SubHead"]))
                    else:
                        elements.append(Paragraph(safe_para(para), styles["BodyText2"]))

            if g.get("requires_human_review"):
                elements.append(Paragraph("<b><font color='#dc2626'>Requires independent human review before filing or reliance in advice.</font></b>", styles["BodyText2"]))

            elements.append(Spacer(1, 6*mm))

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
            ("FONTNAME", (0, 0), (-1, 0), "Times-Bold"),
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

            for item in ver.get("supporting_items", [])[:5]:
                elements.append(Paragraph(f"&nbsp;&nbsp;<font color='#16a34a'>[SUPPORTS]</font> {item.get('filename', '')}: \"{item.get('quote', '')[:150]}\" (Confidence: {item.get('confidence', 'moderate')})", styles["Small"]))

            for item in ver.get("undermining_items", [])[:5]:
                elements.append(Paragraph(f"&nbsp;&nbsp;<font color='#dc2626'>[UNDERMINES]</font> {item.get('filename', '')}: \"{item.get('quote', '')[:150]}\" (Confidence: {item.get('confidence', 'moderate')})", styles["Small"]))

            missing = ver.get("missing_items", [])
            if missing:
                elements.append(Paragraph(f"&nbsp;&nbsp;<font color='#d97706'>[MISSING]</font> {', '.join(str(m.get('description', m) if isinstance(m, dict) else m)[:80] for m in missing[:3])}", styles["Small"]))

            elements.append(Spacer(1, 3*mm))

    elements.append(PageBreak())

    # ── SECTION 4: CASE NOTES ──
    elements.append(Paragraph("4. Case Notes", styles["SectionHead"]))
    elements.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#0f4c81")))
    elements.append(Spacer(1, 3*mm))

    if not notes:
        elements.append(Paragraph("No case notes have been recorded.", styles["BodyText2"]))
    else:
        for note in notes:
            note_title = (note.get("title") or "Untitled").replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
            note_content = (note.get("content") or "").replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
            note_date = note.get("created_at", "")
            if note_date:
                try:
                    from dateutil.parser import parse as parse_date
                    note_date = parse_date(note_date).strftime("%d %B %Y")
                except Exception:
                    note_date = str(note_date)[:10]
            elements.append(Paragraph(f"{note_title} — <i>{note_date}</i>", styles["SubHead"]))
            if note_content:
                elements.append(Paragraph(note_content, styles["BodyText2"]))
            elements.append(Spacer(1, 3*mm))

    elements.append(PageBreak())

    # ── SECTION 5: VERIFICATION SUMMARY ──
    elements.append(Paragraph("5. Verification Summary", styles["SectionHead"]))
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
        ("FONTNAME", (0, 0), (0, -1), "Times-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("LINEBELOW", (0, 0), (-1, -2), 0.5, colors.HexColor("#e2e8f0")),
    ]))
    elements.append(sum_table)

    elements.append(Spacer(1, 8*mm))

    elements.append(Paragraph("Documents on File", styles["SubHead"]))
    for d in documents:
        elements.append(Paragraph(f"&nbsp;&nbsp;&bull; {d.get('filename', 'Unknown')}", styles["Small"]))

    elements.append(Spacer(1, 10*mm))
    elements.append(Paragraph("NOT LEGAL ADVICE — AI-assisted preparation material for legal review. All grounds, authorities, and procedural issues should be independently verified before use in court or formal advice.", styles["Disclaimer"]))
    elements.append(Paragraph(f"Generated {datetime.now(timezone.utc).strftime('%d %B %Y %H:%M UTC')} by Appeal Case Manager", styles["Disclaimer"]))

    # Build PDF with standardised footer
    from services.export_footer import NumberedCanvas, build_footer_label
    footer_label = build_footer_label(case, "Barrister Acceptance Pack")
    numbered_canvas = NumberedCanvas(footer_label)
    doc.build(elements, canvasmaker=numbered_canvas)
    buffer.seek(0)

    safe_defendant = "".join(c for c in case.get("defendant_name", "case")[:30] if c.isalnum() or c in ' -_').strip().replace(' ', '_')
    filename = f"Barrister_Acceptance_Pack_{safe_defendant}_{datetime.now(timezone.utc).strftime('%Y%m%d')}.pdf"

    return StreamingResponse(
        buffer,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )
