"""
Criminal Appeal AI - Payments Router
Extracted from server.py monolith.
"""
from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import HTMLResponse
from datetime import datetime, timezone
import uuid
import os
import logging
import secrets

from config import db, get_frontend_url, get_payid_email, is_admin_user, get_admin_emails
from auth_utils import get_current_user
from models import FEATURE_PRICES, canonical_feature_type
from services.email_service import send_payid_status_email, send_admin_payid_alert

logger = logging.getLogger(__name__)


router = APIRouter(prefix="/api", tags=["payments"])

TRIAL_PRICE = 5.00
TRIAL_FEATURE = "grounds_of_merit"


@router.get("/payments/trial-status")
async def get_trial_status(request: Request):
    """Check if user is eligible for the one-time $5 trial on Grounds of Merit."""
    user = await get_current_user(request)
    completed_count = await db.payments.count_documents({
        "user_id": user.user_id,
        "status": "completed"
    })
    is_eligible = completed_count == 0
    return {
        "is_eligible": is_eligible,
        "trial_price": TRIAL_PRICE if is_eligible else None,
        "trial_feature": TRIAL_FEATURE,
        "regular_price": FEATURE_PRICES.get(TRIAL_FEATURE, {}).get("price", 99),
        "message": "One-time trial: Unlock Grounds of Merit for just $5.00 AUD!" if is_eligible else None,
    }


@router.get("/payments/prices")
async def get_feature_prices():
    """Get pricing for premium features"""
    return {"prices": FEATURE_PRICES, "currency": "AUD", "payment_method": "payid"}


@router.get("/cases/{case_id}/payments")
async def get_case_payments(case_id: str, request: Request):
    """Get all payments for a case"""
    user = await get_current_user(request)
    if is_admin_user(user.email):
        return {
            "payments": [],
            "unlocked_features": {"grounds_of_merit": True, "full_report": True, "extensive_report": True},
            "latest_status_by_feature": {}
        }
    payments = await db.payments.find(
        {"case_id": case_id, "user_id": user.user_id}, {"_id": 0}
    ).sort("created_at", -1).to_list(100)
    unlocked = {"grounds_of_merit": False, "full_report": False, "extensive_report": False}
    case = await db.cases.find_one({"case_id": case_id, "user_id": user.user_id}, {"_id": 0, "unlocked_features": 1})
    for feature in case.get("unlocked_features", []) if case else []:
        canonical = canonical_feature_type(feature)
        if canonical in unlocked:
            unlocked[canonical] = True
    for payment in payments:
        canonical = canonical_feature_type(payment.get("feature_type"))
        if canonical in unlocked:
            if payment.get("status") == "completed":
                unlocked[canonical] = True
    latest_status_by_feature = {}
    for payment in payments:
        canonical = canonical_feature_type(payment.get("feature_type"))
        if canonical and canonical not in latest_status_by_feature:
            latest_status_by_feature[canonical] = {
                "status": payment.get("status"), "reference": payment.get("reference"),
                "amount": payment.get("amount"), "created_at": payment.get("created_at"),
            }
    return {"payments": payments, "unlocked_features": unlocked, "latest_status_by_feature": latest_status_by_feature}


@router.post("/payments/payid/create-reference")
async def create_payid_reference(request: Request):
    """Generate a unique payment reference for PayID bank transfer"""
    user = await get_current_user(request)
    body = await request.json()
    feature_type = body.get("feature_type")
    case_id = body.get("case_id")
    use_trial = body.get("use_trial", False)
    canonical_type = canonical_feature_type(feature_type)
    if not feature_type or not case_id:
        raise HTTPException(status_code=400, detail="Missing feature_type or case_id")
    
    # Check trial eligibility
    price = FEATURE_PRICES.get(canonical_type, {}).get("price", 0)
    is_trial = False
    if use_trial and canonical_type == TRIAL_FEATURE:
        completed_count = await db.payments.count_documents({
            "user_id": user.user_id,
            "status": "completed"
        })
        if completed_count == 0:
            price = TRIAL_PRICE
            is_trial = True
    
    reference = f"ACM-{uuid.uuid4().hex[:8].upper()}"
    payment_record = {
        "payment_id": f"pay_{uuid.uuid4().hex[:12]}",
        "user_id": user.user_id, "case_id": case_id,
        "feature_type": canonical_type, "amount": price,
        "method": "payid", "reference": reference, "status": "pending",
        "is_trial": is_trial,
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    await db.payments.insert_one(payment_record)
    payment_record.pop("_id", None)
    return {
        "reference": reference, "amount": price,
        "payid": get_payid_email(), "payid_name": "Appeal Case Manager",
        "instructions": f"Transfer ${price:.2f} AUD to the PayID above. Use reference: {reference}",
        "is_trial": is_trial,
    }


@router.post("/payments/payid/verify")
async def verify_payid_payment(request: Request):
    """Mark a PayID payment as submitted."""
    user = await get_current_user(request)
    body = await request.json()
    reference = body.get("reference")
    case_id = body.get("case_id")
    feature_type = body.get("feature_type")
    canonical_type = canonical_feature_type(feature_type)
    if not reference:
        raise HTTPException(status_code=400, detail="Missing reference")
    payment = await db.payments.find_one({"reference": reference, "user_id": user.user_id}, {"_id": 0})
    if not payment:
        raise HTTPException(status_code=404, detail="Payment reference not found")
    if payment.get("status") == "completed":
        if case_id and feature_type:
            await db.cases.update_one(
                {"case_id": case_id, "user_id": user.user_id},
                {"$addToSet": {"unlocked_features": canonical_type}}
            )
        await send_payid_status_email(
            user.email, user.name,
            FEATURE_PRICES.get(canonical_type, {}).get("name", canonical_type or "Feature"),
            payment.get("amount") or FEATURE_PRICES.get(canonical_type, {}).get("price", 0),
            reference,
            "Payment Confirmed - Feature Unlocked", "Payment Confirmed",
            "<p style=\"margin:0 0 14px;line-height:1.7;\">A payment refresh confirmed that this feature has been paid and unlocked successfully.</p>",
        )
        return {"status": "already_verified", "message": "Payment confirmed. Feature unlocked."}
    await db.payments.update_one(
        {"reference": reference},
        {"$set": {"status": "submitted", "submitted_at": datetime.now(timezone.utc).isoformat()}}
    )
    await send_payid_status_email(
        user.email, user.name,
        FEATURE_PRICES.get(canonical_type, {}).get("name", canonical_type or "Feature"),
        payment.get("amount") or FEATURE_PRICES.get(canonical_type, {}).get("price", 0),
        reference,
        "Payment Notice Received - Awaiting Confirmation", "Payment Notice Received",
        "<p style=\"margin:0 0 14px;line-height:1.7;\">This email confirms that the PayID payment notice was received and marked for review. Once the payment is received and confirmed, the feature will unlock automatically.</p>",
    )
    # Generate a secure one-click confirmation token for the admin email
    confirm_token = secrets.token_urlsafe(32)
    await db.payments.update_one(
        {"reference": reference},
        {"$set": {"confirm_token": confirm_token}}
    )
    # Notify admin with a one-click confirm link
    frontend_url = get_frontend_url()
    confirm_url = f"{frontend_url}/api/payments/payid/email-confirm/{confirm_token}"
    await send_admin_payid_alert(
        admin_emails=get_admin_emails(),
        user_email=user.email,
        user_name=user.name if hasattr(user, 'name') else "",
        feature_name=FEATURE_PRICES.get(canonical_type, {}).get("name", canonical_type or "Feature"),
        amount=payment.get("amount") or FEATURE_PRICES.get(canonical_type, {}).get("price", 0),
        reference=reference,
        case_id=case_id or "",
        frontend_url=frontend_url,
        confirm_url=confirm_url
    )
    return {"status": "submitted_for_review", "message": "Payment submitted! The admin has been notified and will confirm your payment shortly."}


@router.get("/payments/payid/pending")
async def get_pending_payid_payments(request: Request):
    """Get all pending PayID payments (admin only)"""
    user = await get_current_user(request)
    if not is_admin_user(user.email):
        raise HTTPException(status_code=403, detail="Admin access required")
    pending = await db.payments.find(
        {"method": "payid", "status": {"$in": ["pending", "submitted", "pending_verification"]}}, {"_id": 0}
    ).sort("created_at", -1).to_list(100)
    return {"pending_payments": pending}


@router.post("/payments/payid/admin-confirm/{reference}")
async def admin_confirm_payid_payment(reference: str, request: Request):
    """Admin confirms a PayID payment has been received"""
    user = await get_current_user(request)
    if not is_admin_user(user.email):
        raise HTTPException(status_code=403, detail="Admin access required")
    payment = await db.payments.find_one({"reference": reference}, {"_id": 0})
    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found")
    await db.payments.update_one(
        {"reference": reference},
        {"$set": {"status": "completed", "completed_at": datetime.now(timezone.utc).isoformat(), "confirmed_by": user.email}}
    )
    if payment.get("case_id") and payment.get("feature_type"):
        await db.cases.update_one(
            {"case_id": payment["case_id"], "user_id": payment["user_id"]},
            {"$addToSet": {"unlocked_features": canonical_feature_type(payment["feature_type"])}},
        )
    payment_user = await db.users.find_one({"user_id": payment.get("user_id")}, {"_id": 0, "email": 1, "name": 1})
    await send_payid_status_email(
        (payment_user or {}).get("email"), (payment_user or {}).get("name", ""),
        FEATURE_PRICES.get(canonical_feature_type(payment.get("feature_type")), {}).get("name", canonical_feature_type(payment.get("feature_type")) or "Feature"),
        payment.get("amount") or FEATURE_PRICES.get(canonical_feature_type(payment.get("feature_type")), {}).get("price", 0),
        reference,
        "Payment Confirmed - Feature Unlocked", "Payment Confirmed",
        "<p style=\"margin:0 0 14px;line-height:1.7;\">The PayID transfer has been confirmed and the premium feature is now unlocked on the case.</p>",
    )
    return {"status": "confirmed", "reference": reference}


@router.get("/payments/payid/email-confirm/{confirm_token}")
async def email_confirm_payid_payment(confirm_token: str):
    """One-click payment confirmation from admin email — no login required.
    Uses a secure token generated when the payment was submitted."""
    payment = await db.payments.find_one({"confirm_token": confirm_token}, {"_id": 0})
    if not payment:
        return HTMLResponse(content="""
        <html><body style="font-family:Arial,sans-serif;text-align:center;padding:60px;background:#fef2f2;">
        <h1 style="color:#dc2626;">Invalid or Expired Link</h1>
        <p>This confirmation link is not valid. It may have already been used or the payment was not found.</p>
        </body></html>""", status_code=404)

    reference = payment.get("reference", "")

    if payment.get("status") == "completed":
        return HTMLResponse(content=f"""
        <html><body style="font-family:Arial,sans-serif;text-align:center;padding:60px;background:#f0fdf4;">
        <h1 style="color:#16a34a;">Already Confirmed</h1>
        <p>Payment <strong>{reference}</strong> has already been confirmed and the feature is unlocked.</p>
        </body></html>""")

    # Confirm the payment
    await db.payments.update_one(
        {"confirm_token": confirm_token},
        {"$set": {"status": "completed", "completed_at": datetime.now(timezone.utc).isoformat(), "confirmed_by": "email-link"}}
    )

    # Unlock the feature on the case
    canonical = canonical_feature_type(payment.get("feature_type"))
    if payment.get("case_id") and canonical:
        await db.cases.update_one(
            {"case_id": payment["case_id"], "user_id": payment["user_id"]},
            {"$addToSet": {"unlocked_features": canonical}},
        )

    # Send confirmation email to the user
    payment_user = await db.users.find_one({"user_id": payment.get("user_id")}, {"_id": 0, "email": 1, "name": 1})
    feature_name = FEATURE_PRICES.get(canonical, {}).get("name", canonical or "Feature")
    amount = payment.get("amount") or FEATURE_PRICES.get(canonical, {}).get("price", 0)
    if payment_user and payment_user.get("email"):
        await send_payid_status_email(
            payment_user["email"], payment_user.get("name", ""),
            feature_name, amount, reference,
            "Payment Confirmed - Feature Unlocked", "Payment Confirmed",
            "<p style=\"margin:0 0 14px;line-height:1.7;\">The PayID transfer has been confirmed and the premium feature is now unlocked on the case.</p>",
        )

    return HTMLResponse(content=f"""
    <html><body style="font-family:Arial,sans-serif;text-align:center;padding:60px;background:#f0fdf4;">
    <div style="max-width:500px;margin:0 auto;background:white;border-radius:16px;padding:40px;box-shadow:0 4px 24px rgba(0,0,0,0.1);">
        <div style="width:64px;height:64px;background:#16a34a;border-radius:50%;display:flex;align-items:center;justify-content:center;margin:0 auto 20px;">
            <span style="color:white;font-size:32px;">&#10003;</span>
        </div>
        <h1 style="color:#16a34a;margin:0 0 12px;">Payment Confirmed</h1>
        <p style="color:#374151;margin:0 0 8px;">Reference: <strong>{reference}</strong></p>
        <p style="color:#374151;margin:0 0 8px;">Feature: <strong>{feature_name}</strong></p>
        <p style="color:#374151;margin:0 0 20px;">Amount: <strong>${amount:.2f} AUD</strong></p>
        <p style="color:#6b7280;font-size:14px;">The user has been notified and their feature is now unlocked.</p>
    </div>
    </body></html>""")
