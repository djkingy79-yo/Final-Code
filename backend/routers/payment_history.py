"""
Criminal Appeal AI - Payment History Router
Provides payment history, summary, and PDF receipt generation.
"""
from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import StreamingResponse
from datetime import datetime, timezone
import logging
import io

from config import db, get_contact_email
from auth_utils import get_current_user
from models import FEATURE_PRICES, canonical_feature_type

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/payments", tags=["payment-history"])


@router.get("/history")
async def get_payment_history(request: Request):
    """Get all payments for the current user."""
    user = await get_current_user(request)

    payid_payments = await db.payments.find(
        {"user_id": user.user_id},
        {"_id": 0},
    ).sort("created_at", -1).to_list(200)

    combined = []
    for p in payid_payments:
        combined.append({
            "payment_id": p.get("payment_id", ""),
            "case_id": p.get("case_id", ""),
            "feature_type": p.get("feature_type", ""),
            "feature_name": FEATURE_PRICES.get(
                canonical_feature_type(p.get("feature_type")), {}
            ).get("name", p.get("feature_type", "Unknown")),
            "amount": p.get("amount", 0),
            "currency": "AUD",
            "method": p.get("method", "payid"),
            "reference": p.get("reference", ""),
            "status": p.get("status", "unknown"),
            "is_trial": p.get("is_trial", False),
            "created_at": p.get("created_at", ""),
            "completed_at": p.get("completed_at", ""),
        })

    # Sort by created_at descending
    combined.sort(key=lambda x: x.get("created_at", ""), reverse=True)

    return {"payments": combined, "total": len(combined)}


@router.get("/history/summary")
async def get_payment_summary(request: Request):
    """Get payment summary stats for the current user."""
    user = await get_current_user(request)

    payments = await db.payments.find(
        {"user_id": user.user_id, "status": "completed"},
        {"_id": 0, "amount": 1, "feature_type": 1, "case_id": 1},
    ).to_list(500)

    total_spent = sum(p.get("amount", 0) for p in payments)
    features_unlocked = set()
    cases_with_payments = set()
    for p in payments:
        ft = canonical_feature_type(p.get("feature_type"))
        if ft:
            features_unlocked.add(ft)
        cid = p.get("case_id")
        if cid:
            cases_with_payments.add(cid)

    total_payments = await db.payments.count_documents({"user_id": user.user_id})
    completed_payments = len(payments)

    return {
        "total_spent": total_spent,
        "currency": "AUD",
        "total_payments": total_payments,
        "completed_payments": completed_payments,
        "features_unlocked": list(features_unlocked),
        "features_unlocked_count": len(features_unlocked),
        "cases_with_payments": len(cases_with_payments),
    }


@router.get("/receipt/{payment_id}/pdf")
async def generate_receipt_pdf(payment_id: str, request: Request):
    """Generate a PDF receipt for a specific payment."""
    user = await get_current_user(request)

    # Find payment in either collection
    payment = await db.payments.find_one(
        {"payment_id": payment_id, "user_id": user.user_id},
        {"_id": 0},
    )
    if not payment:
        payment = await db.payment_transactions.find_one(
            {"payment_id": payment_id, "user_id": user.user_id},
            {"_id": 0},
        )
    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found")

    # Find case title
    case_id = payment.get("case_id", "")
    case = await db.cases.find_one({"case_id": case_id}, {"_id": 0, "title": 1})
    case_title = (case or {}).get("title", case_id)

    # Find user info
    user_doc = await db.users.find_one(
        {"user_id": user.user_id}, {"_id": 0, "name": 1, "email": 1}
    )

    # Generate PDF
    from reportlab.lib.pagesizes import A4
    from reportlab.lib import colors
    from reportlab.lib.units import mm
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, topMargin=30*mm, bottomMargin=30*mm,
                            leftMargin=25*mm, rightMargin=25*mm)

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle("ReceiptTitle", parent=styles["Title"],
                                  fontSize=22, textColor=colors.HexColor("#1e3a5f"),
                                  spaceAfter=4*mm, fontName="Times-Bold")
    heading_style = ParagraphStyle("ReceiptHeading", parent=styles["Heading2"],
                                    fontSize=13, textColor=colors.HexColor("#1e3a5f"),
                                    spaceBefore=6*mm, spaceAfter=3*mm, fontName="Times-Bold")
    normal_style = ParagraphStyle("ReceiptNormal", parent=styles["Normal"],
                                   fontSize=10, leading=14, fontName="Times-Roman")
    small_style = ParagraphStyle("ReceiptSmall", parent=normal_style, fontSize=8,
                                  textColor=colors.HexColor("#6b7280"))

    feature_type = canonical_feature_type(payment.get("feature_type", ""))
    feature_name = FEATURE_PRICES.get(feature_type, {}).get("name", feature_type or "Premium Feature")
    amount = payment.get("amount", 0)
    method = payment.get("method", "payid").upper()
    if method == "PAYID":
        method = "PayID (Bank Transfer)"
    reference = payment.get("reference", payment_id)
    status = payment.get("status", "unknown").title()
    created = payment.get("created_at", "")
    completed = payment.get("completed_at", "")

    # Format dates
    def fmt_date(iso_str):
        if not iso_str:
            return "—"
        try:
            dt = datetime.fromisoformat(iso_str.replace("Z", "+00:00"))
            return dt.strftime("%d %B %Y, %I:%M %p")
        except Exception:
            return iso_str[:19]

    elements = []

    # Header
    elements.append(Paragraph("Appeal Case Manager", title_style))
    elements.append(Paragraph("Payment Receipt", heading_style))
    elements.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#2563eb"),
                                spaceAfter=5*mm))

    # Receipt details table
    data = [
        ["Receipt No:", reference],
        ["Date:", fmt_date(created)],
        ["Status:", status],
        ["Payment Method:", method],
    ]
    if completed:
        data.append(["Completed:", fmt_date(completed)])

    t = Table(data, colWidths=[45*mm, 105*mm])
    t.setStyle(TableStyle([
        ("FONTNAME", (0, 0), (0, -1), "Times-Bold"),
        ("FONTNAME", (1, 0), (1, -1), "Times-Roman"),
        ("FONTSIZE", (0, 0), (-1, -1), 10),
        ("TEXTCOLOR", (0, 0), (0, -1), colors.HexColor("#374151")),
        ("TEXTCOLOR", (1, 0), (1, -1), colors.HexColor("#111827")),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3*mm),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
    ]))
    elements.append(t)
    elements.append(Spacer(1, 5*mm))

    # Customer details
    elements.append(Paragraph("Customer", heading_style))
    elements.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor("#cbd5e1"),
                                spaceAfter=3*mm))
    elements.append(Paragraph(f"Name: {(user_doc or {}).get('name', '—')}", normal_style))
    elements.append(Paragraph(f"Email: {(user_doc or {}).get('email', '—')}", normal_style))
    elements.append(Spacer(1, 5*mm))

    # Item details
    elements.append(Paragraph("Item Details", heading_style))
    elements.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor("#cbd5e1"),
                                spaceAfter=3*mm))

    item_data = [
        ["Description", "Case", "Amount"],
        [feature_name, case_title[:50], f"${amount:.2f} AUD"],
    ]
    if payment.get("is_trial"):
        item_data[1][0] += " (Trial)"

    item_table = Table(item_data, colWidths=[65*mm, 55*mm, 30*mm])
    item_table.setStyle(TableStyle([
        ("FONTNAME", (0, 0), (-1, 0), "Times-Bold"),
        ("FONTNAME", (0, 1), (-1, -1), "Times-Roman"),
        ("FONTSIZE", (0, 0), (-1, -1), 10),
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#f1f5f9")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.HexColor("#1e3a5f")),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3*mm),
        ("TOPPADDING", (0, 0), (-1, -1), 3*mm),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#e2e8f0")),
        ("ALIGN", (2, 0), (2, -1), "RIGHT"),
    ]))
    elements.append(item_table)
    elements.append(Spacer(1, 4*mm))

    # Total
    total_data = [["Total Paid:", f"${amount:.2f} AUD"]]
    total_table = Table(total_data, colWidths=[120*mm, 30*mm])
    total_table.setStyle(TableStyle([
        ("FONTNAME", (0, 0), (-1, -1), "Times-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 12),
        ("TEXTCOLOR", (0, 0), (-1, -1), colors.HexColor("#1e3a5f")),
        ("ALIGN", (1, 0), (1, 0), "RIGHT"),
        ("TOPPADDING", (0, 0), (-1, -1), 2*mm),
    ]))
    elements.append(total_table)
    elements.append(Spacer(1, 10*mm))

    # Footer
    elements.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor("#cbd5e1"),
                                spaceAfter=3*mm))
    contact = get_contact_email()
    elements.append(Paragraph(
        f"Appeal Case Manager — Payment Receipt<br/>"
        f"Contact: {contact}<br/>"
        f"This is an automatically generated receipt. "
        f"Appeal Case Manager is an educational tool only and does not provide legal advice.",
        small_style,
    ))

    doc.build(elements)
    buffer.seek(0)

    filename = f"Receipt_{reference}.pdf"
    return StreamingResponse(
        buffer,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )
