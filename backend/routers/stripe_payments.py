"""
Criminal Appeal AI - Stripe Payment Router
Handles Stripe Checkout for card/Apple Pay/Google Pay payments.
"""
from fastapi import APIRouter, HTTPException, Request
from datetime import datetime, timezone
import uuid
import logging
import os

from emergentintegrations.payments.stripe.checkout import (
    StripeCheckout,
    CheckoutSessionRequest,
)
from config import db, get_frontend_url
from auth_utils import get_current_user
from models import FEATURE_PRICES, canonical_feature_type

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/payments/stripe", tags=["stripe"])

STRIPE_API_KEY = os.environ.get("STRIPE_API_KEY")


def _get_stripe_checkout(base_url: str) -> StripeCheckout:
    if not STRIPE_API_KEY:
        raise HTTPException(status_code=503, detail="Payment service unavailable — STRIPE_API_KEY not configured")
    webhook_url = f"{base_url}api/webhook/stripe"
    return StripeCheckout(api_key=STRIPE_API_KEY, webhook_url=webhook_url)


@router.post("/create-checkout")
async def create_stripe_checkout(request: Request):
    """Create a Stripe Checkout session for a premium feature."""
    user = await get_current_user(request)
    body = await request.json()
    feature_type = body.get("feature_type")
    case_id = body.get("case_id")
    origin_url = body.get("origin_url", "")

    canonical = canonical_feature_type(feature_type)
    if not canonical or canonical not in FEATURE_PRICES:
        raise HTTPException(status_code=400, detail="Invalid feature type")
    if not case_id:
        raise HTTPException(status_code=400, detail="Missing case_id")

    # Check if already unlocked
    case = await db.cases.find_one(
        {"case_id": case_id, "user_id": user.user_id},
        {"_id": 0, "unlocked_features": 1},
    )
    if case and canonical in (case.get("unlocked_features") or []):
        raise HTTPException(status_code=400, detail="Feature already unlocked")

    # Price from server-side only (never from frontend)
    price = float(FEATURE_PRICES[canonical]["price"])
    feature_name = FEATURE_PRICES[canonical]["name"]

    # Check trial eligibility for grounds_of_merit
    is_trial = False
    if canonical == "grounds_of_merit":
        completed_count = await db.payments.count_documents(
            {"user_id": user.user_id, "status": "completed"}
        )
        if completed_count == 0:
            price = 5.00
            is_trial = True

    # Build success/cancel URLs from origin
    if not origin_url:
        origin_url = get_frontend_url()
    origin_url = origin_url.rstrip("/")
    success_url = f"{origin_url}/payment-success?session_id={{CHECKOUT_SESSION_ID}}&case_id={case_id}&feature_type={canonical}"
    cancel_url = f"{origin_url}/cases/{case_id}"

    stripe_checkout = _get_stripe_checkout(str(request.base_url))

    checkout_req = CheckoutSessionRequest(
        amount=price,
        currency="aud",
        success_url=success_url,
        cancel_url=cancel_url,
        metadata={
            "user_id": user.user_id,
            "case_id": case_id,
            "feature_type": canonical,
            "is_trial": str(is_trial),
        },
        payment_methods=["card"],
    )

    session = await stripe_checkout.create_checkout_session(checkout_req)

    # Record transaction as pending
    payment_id = f"pay_{uuid.uuid4().hex[:12]}"
    await db.payment_transactions.insert_one({
        "payment_id": payment_id,
        "stripe_session_id": session.session_id,
        "user_id": user.user_id,
        "case_id": case_id,
        "feature_type": canonical,
        "feature_name": feature_name,
        "amount": price,
        "currency": "aud",
        "method": "stripe",
        "is_trial": is_trial,
        "status": "pending",
        "payment_status": "initiated",
        "created_at": datetime.now(timezone.utc).isoformat(),
    })

    return {"url": session.url, "session_id": session.session_id}


@router.get("/status/{session_id}")
async def get_stripe_payment_status(session_id: str, request: Request):
    """Check the status of a Stripe Checkout session and update DB."""
    user = await get_current_user(request)

    # Find the payment transaction
    txn = await db.payment_transactions.find_one(
        {"stripe_session_id": session_id, "user_id": user.user_id},
        {"_id": 0},
    )
    if not txn:
        raise HTTPException(status_code=404, detail="Payment session not found")

    # If already completed, return immediately
    if txn.get("payment_status") == "paid":
        return {
            "status": "complete",
            "payment_status": "paid",
            "feature_type": txn.get("feature_type"),
            "amount": txn.get("amount"),
        }

    # Poll Stripe for status
    stripe_checkout = _get_stripe_checkout(str(request.base_url))
    checkout_status = await stripe_checkout.get_checkout_status(session_id)

    new_status = checkout_status.payment_status
    session_status = checkout_status.status

    update_fields = {
        "payment_status": new_status,
        "status": session_status,
        "checked_at": datetime.now(timezone.utc).isoformat(),
    }

    if new_status == "paid" and txn.get("payment_status") != "paid":
        update_fields["completed_at"] = datetime.now(timezone.utc).isoformat()
        update_fields["status"] = "completed"

        # Unlock the feature on the case
        canonical = txn.get("feature_type")
        case_id = txn.get("case_id")
        if case_id and canonical:
            await db.cases.update_one(
                {"case_id": case_id, "user_id": user.user_id},
                {"$addToSet": {"unlocked_features": canonical}},
            )

        # Also record in the main payments collection for consistency
        await db.payments.insert_one({
            "payment_id": txn.get("payment_id"),
            "user_id": user.user_id,
            "case_id": case_id,
            "feature_type": canonical,
            "amount": txn.get("amount"),
            "method": "stripe",
            "reference": f"STRIPE-{session_id[:12]}",
            "status": "completed",
            "is_trial": txn.get("is_trial", False),
            "created_at": txn.get("created_at"),
            "completed_at": datetime.now(timezone.utc).isoformat(),
        })

    await db.payment_transactions.update_one(
        {"stripe_session_id": session_id},
        {"$set": update_fields},
    )

    return {
        "status": session_status,
        "payment_status": new_status,
        "feature_type": txn.get("feature_type"),
        "amount": txn.get("amount"),
    }


@router.post("/webhook")
async def stripe_webhook_handler(request: Request):
    """Handle Stripe webhook events."""
    body = await request.body()
    sig = request.headers.get("Stripe-Signature", "")

    try:
        stripe_checkout = _get_stripe_checkout(str(request.base_url))
        webhook_response = await stripe_checkout.handle_webhook(body, sig)

        if webhook_response.payment_status == "paid":
            session_id = webhook_response.session_id
            txn = await db.payment_transactions.find_one(
                {"stripe_session_id": session_id},
                {"_id": 0},
            )
            if txn and txn.get("payment_status") != "paid":
                await db.payment_transactions.update_one(
                    {"stripe_session_id": session_id},
                    {"$set": {
                        "payment_status": "paid",
                        "status": "completed",
                        "completed_at": datetime.now(timezone.utc).isoformat(),
                    }},
                )
                canonical = txn.get("feature_type")
                case_id = txn.get("case_id")
                user_id = txn.get("user_id")
                if case_id and canonical and user_id:
                    await db.cases.update_one(
                        {"case_id": case_id, "user_id": user_id},
                        {"$addToSet": {"unlocked_features": canonical}},
                    )
                    # Record in main payments collection
                    existing = await db.payments.find_one(
                        {"payment_id": txn.get("payment_id")}, {"_id": 0}
                    )
                    if not existing:
                        await db.payments.insert_one({
                            "payment_id": txn.get("payment_id"),
                            "user_id": user_id,
                            "case_id": case_id,
                            "feature_type": canonical,
                            "amount": txn.get("amount"),
                            "method": "stripe",
                            "reference": f"STRIPE-{session_id[:12]}",
                            "status": "completed",
                            "is_trial": txn.get("is_trial", False),
                            "created_at": txn.get("created_at"),
                            "completed_at": datetime.now(timezone.utc).isoformat(),
                        })

        return {"status": "processed"}
    except Exception as e:
        logger.error(f"Stripe webhook error: {e}")
        return {"status": "error", "detail": str(e)}
