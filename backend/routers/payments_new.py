# DO NOT UNDO — payments_new router. All endpoints in this file are approved and must be preserved.
"""
Payment Router for Appeal Case Manager
Supports PayPal and PayID (Australian bank transfer) payment methods
"""
from fastapi import APIRouter, Request, HTTPException
from pydantic import BaseModel
from typing import Optional
from datetime import datetime, timezone
from config import db, logger
from auth_utils import get_current_user
import os
import asyncio
import paypalrestsdk
import resend

router = APIRouter(prefix="/api/payments", tags=["payments"])

# Fixed pricing - NEVER accept amounts from frontend
FEATURE_PRICES = {
    "full_report": {"price": 29.00, "currency": "AUD", "name": "Full Detailed Report"},
    "extensive_report": {"price": 39.00, "currency": "AUD", "name": "Extensive Log Report"},
    "grounds_of_merit": {"price": 50.00, "currency": "AUD", "name": "Grounds of Merit Analysis"},
}

# PayID Configuration for bank transfers
PAYID_CONFIG = {
    "payid": "djkingy79@gmail.com",
    "payid_type": "email",
    "account_name": "Deb King - Appeal Case Manager",
    "bank_name": "Commonwealth Bank",
    "reference_prefix": "ACM"
}

# Resend email configuration
RESEND_API_KEY = os.environ.get('RESEND_API_KEY')
RESEND_CONFIGURED = False
if RESEND_API_KEY:
    resend.api_key = RESEND_API_KEY
    RESEND_CONFIGURED = True
    logger.info("Resend configured for payment notifications")

# PayPal Configuration
PAYPAL_CLIENT_ID = os.environ.get('PAYPAL_CLIENT_ID', '')
PAYPAL_CLIENT_SECRET = os.environ.get('PAYPAL_CLIENT_SECRET', '')
PAYPAL_MODE = os.environ.get('PAYPAL_MODE', 'sandbox')
PAYPAL_CONFIGURED = False

if PAYPAL_CLIENT_ID and PAYPAL_CLIENT_SECRET:
    try:
        paypalrestsdk.configure({
            "mode": PAYPAL_MODE,
            "client_id": PAYPAL_CLIENT_ID,
            "client_secret": PAYPAL_CLIENT_SECRET
        })
        PAYPAL_CONFIGURED = True
        logger.info(f"PayPal configured in {PAYPAL_MODE} mode")
    except Exception as e:
        logger.warning(f"PayPal configuration failed: {e}")


async def send_payment_confirmation_email(user_email: str, user_name: str, feature_name: str, amount: float, reference: str, case_id: str):
    """Send email notification when PayID payment is confirmed"""
    if not RESEND_CONFIGURED:
        logger.warning("Cannot send payment confirmation - Resend not configured")
        return False
    
    try:
        # Get the frontend URL for the case link
        frontend_url = os.environ.get('FRONTEND_URL', 'https://grounds-analyzer.preview.emergentagent.com')
        case_link = f"{frontend_url}/cases/{case_id}"
        
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: 'Georgia', serif; line-height: 1.6; color: #1e293b; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background: linear-gradient(135deg, #0f172a 0%, #1e3a5f 100%); color: white; padding: 30px; text-align: center; border-radius: 12px 12px 0 0; }}
                .header h1 {{ margin: 0; font-size: 24px; }}
                .content {{ background: #ffffff; padding: 30px; border: 1px solid #e2e8f0; }}
                .success-badge {{ background: #10b981; color: white; padding: 8px 16px; border-radius: 20px; display: inline-block; font-weight: bold; margin: 15px 0; }}
                .details {{ background: #f8fafc; padding: 20px; border-radius: 8px; margin: 20px 0; }}
                .details-row {{ display: flex; justify-content: space-between; padding: 8px 0; border-bottom: 1px solid #e2e8f0; }}
                .details-row:last-child {{ border-bottom: none; }}
                .button {{ background: #f59e0b; color: #1e293b; padding: 14px 28px; text-decoration: none; border-radius: 8px; display: inline-block; font-weight: bold; margin: 20px 0; }}
                .footer {{ background: #f1f5f9; padding: 20px; text-align: center; font-size: 12px; color: #64748b; border-radius: 0 0 12px 12px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>⚖️ Criminal Appeal AI</h1>
                    <p style="margin: 10px 0 0 0; opacity: 0.9;">Payment Confirmation</p>
                </div>
                <div class="content">
                    <p>Dear {user_name or 'Valued User'},</p>
                    
                    <div style="text-align: center;">
                        <span class="success-badge">✓ Payment Confirmed</span>
                    </div>
                    
                    <p>Great news! Your bank transfer has been verified and your premium feature is now <strong>unlocked</strong>.</p>
                    
                    <div class="details">
                        <div class="details-row">
                            <span><strong>Feature:</strong></span>
                            <span>{feature_name}</span>
                        </div>
                        <div class="details-row">
                            <span><strong>Amount:</strong></span>
                            <span>${amount:.2f} AUD</span>
                        </div>
                        <div class="details-row">
                            <span><strong>Reference:</strong></span>
                            <span style="font-family: monospace;">{reference}</span>
                        </div>
                        <div class="details-row">
                            <span><strong>Status:</strong></span>
                            <span style="color: #10b981; font-weight: bold;">Completed</span>
                        </div>
                    </div>
                    
                    <p style="text-align: center;">
                        <a href="{case_link}" class="button">View Your Case →</a>
                    </p>
                    
                    <p>Your {feature_name} is now ready to use. You can access it from your case dashboard.</p>
                    
                    <p>Thank you for using Criminal Appeal AI to support your case.</p>
                    
                    <p style="margin-top: 30px;">
                        Best regards,<br>
                        <strong>Deb King</strong><br>
                        <em style="color: #64748b;">Criminal Appeal AI</em>
                    </p>
                </div>
                <div class="footer">
                    <p>This email confirms your payment for premium features on Criminal Appeal AI.</p>
                    <p>Questions? Reply to this email or contact djkingy79@gmail.com</p>
                    <p style="margin-top: 15px; font-style: italic;">"One woman's fight for justice"</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        params = {
            "from": "Appeal Case Manager <onboarding@resend.dev>",
            "to": [user_email],
            "subject": f"✓ Payment Confirmed - {feature_name} Unlocked",
            "html": html_content
        }
        
        await asyncio.to_thread(resend.Emails.send, params)
        logger.info(f"Payment confirmation email sent to {user_email}")
        return True
        
    except Exception as e:
        logger.error(f"Failed to send payment confirmation email: {e}")
        return False


class PayPalOrderRequest(BaseModel):
    feature_type: str
    case_id: str
    return_url: str
    cancel_url: str


class PayIDPaymentRequest(BaseModel):
    feature_type: str
    case_id: str


class VerifyPayIDRequest(BaseModel):
    reference: str
    case_id: str
    feature_type: str


@router.get("/prices")
async def get_prices():
    """Get feature prices"""
    return FEATURE_PRICES


@router.get("/methods")
async def get_payment_methods():
    """Get available payment methods"""
    return {
        "paypal": {
            "enabled": PAYPAL_CONFIGURED,
            "name": "PayPal",
            "description": "Pay securely with PayPal, credit/debit card",
            "supports": ["Credit Card", "Debit Card", "PayPal Balance"]
        },
        "payid": {
            "enabled": True,
            "name": "PayID / Bank Transfer",
            "description": "Instant Australian bank transfer using PayID",
            "supports": ["Australian Bank Accounts", "Instant Transfer"],
            "payid": PAYID_CONFIG["payid"],
            "payid_type": PAYID_CONFIG["payid_type"],
            "account_name": PAYID_CONFIG["account_name"]
        }
    }


# ============ PAYPAL ENDPOINTS ============

@router.post("/paypal/create-order")
async def create_paypal_order(req: PayPalOrderRequest, request: Request):
    """Create a PayPal payment order"""
    user = await get_current_user(request)
    
    if not PAYPAL_CONFIGURED:
        raise HTTPException(status_code=503, detail="PayPal is not configured")
    
    if req.feature_type not in FEATURE_PRICES:
        raise HTTPException(status_code=400, detail="Invalid feature type")
    
    feature = FEATURE_PRICES[req.feature_type]
    
    try:
        payment = paypalrestsdk.Payment({
            "intent": "sale",
            "payer": {
                "payment_method": "paypal"
            },
            "redirect_urls": {
                "return_url": req.return_url,
                "cancel_url": req.cancel_url
            },
            "transactions": [{
                "item_list": {
                    "items": [{
                        "name": feature["name"],
                        "sku": req.feature_type,
                        "price": str(feature["price"]),
                        "currency": feature["currency"],
                        "quantity": 1
                    }]
                },
                "amount": {
                    "total": str(feature["price"]),
                    "currency": feature["currency"]
                },
                "description": f"Criminal Appeal AI - {feature['name']} for Case {req.case_id}"
            }]
        })
        
        if payment.create():
            # Store payment record
            await db.payment_transactions.insert_one({
                "payment_id": payment.id,
                "user_id": user.user_id,
                "case_id": req.case_id,
                "feature_type": req.feature_type,
                "amount": feature["price"],
                "currency": feature["currency"],
                "method": "paypal",
                "status": "created",
                "created_at": datetime.now(timezone.utc).isoformat()
            })
            
            # Find approval URL
            approval_url = None
            for link in payment.links:
                if link.rel == "approval_url":
                    approval_url = link.href
                    break
            
            return {
                "payment_id": payment.id,
                "approval_url": approval_url,
                "status": "created"
            }
        else:
            logger.error(f"PayPal payment creation failed: {payment.error}")
            raise HTTPException(status_code=500, detail=f"Payment creation failed: {payment.error}")
            
    except Exception as e:
        logger.error(f"PayPal error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/paypal/execute")
async def execute_paypal_payment(payment_id: str, payer_id: str, request: Request):
    """Execute an approved PayPal payment"""
    await get_current_user(request)  # Verify user is authenticated
    
    if not PAYPAL_CONFIGURED:
        raise HTTPException(status_code=503, detail="PayPal is not configured")
    
    try:
        payment = paypalrestsdk.Payment.find(payment_id)
        
        if payment.execute({"payer_id": payer_id}):
            # Update transaction record
            transaction = await db.payment_transactions.find_one(
                {"payment_id": payment_id},
                {"_id": 0}
            )
            
            if transaction:
                # Mark as completed
                await db.payment_transactions.update_one(
                    {"payment_id": payment_id},
                    {"$set": {
                        "status": "completed",
                        "payer_id": payer_id,
                        "completed_at": datetime.now(timezone.utc).isoformat()
                    }}
                )
                
                # Create payment record for feature unlocking
                await db.payments.insert_one({
                    "user_id": transaction["user_id"],
                    "case_id": transaction["case_id"],
                    "feature_type": transaction["feature_type"],
                    "amount": transaction["amount"],
                    "currency": transaction["currency"],
                    "method": "paypal",
                    "paypal_payment_id": payment_id,
                    "status": "completed",
                    "created_at": datetime.now(timezone.utc).isoformat()
                })
                
                # Send email notification to user
                payer_user = await db.users.find_one({"user_id": transaction["user_id"]}, {"_id": 0})
                if payer_user and payer_user.get("email"):
                    feature_info = FEATURE_PRICES.get(transaction["feature_type"], {})
                    await send_payment_confirmation_email(
                        user_email=payer_user["email"],
                        user_name=payer_user.get("name", ""),
                        feature_name=feature_info.get("name", transaction["feature_type"]),
                        amount=transaction["amount"],
                        reference=payment_id,
                        case_id=transaction["case_id"]
                    )
            
            return {
                "status": "success",
                "payment_id": payment_id,
                "message": "Payment completed successfully"
            }
        else:
            logger.error(f"PayPal execution failed: {payment.error}")
            raise HTTPException(status_code=400, detail=f"Payment execution failed: {payment.error}")
            
    except Exception as e:
        logger.error(f"PayPal execution error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/paypal/status/{payment_id}")
async def get_paypal_status(payment_id: str, request: Request):
    """Get PayPal payment status"""
    user = await get_current_user(request)
    
    transaction = await db.payment_transactions.find_one(
        {"payment_id": payment_id, "user_id": user.user_id},
        {"_id": 0}
    )
    
    if not transaction:
        raise HTTPException(status_code=404, detail="Payment not found")
    
    return {
        "payment_id": payment_id,
        "status": transaction.get("status", "unknown"),
        "feature_type": transaction.get("feature_type"),
        "amount": transaction.get("amount"),
        "created_at": transaction.get("created_at")
    }


# ============ PAYID ENDPOINTS ============

@router.post("/payid/create-reference")
async def create_payid_reference(req: PayIDPaymentRequest, request: Request):
    """Create a unique reference for PayID bank transfer"""
    user = await get_current_user(request)
    
    if req.feature_type not in FEATURE_PRICES:
        raise HTTPException(status_code=400, detail="Invalid feature type")
    
    feature = FEATURE_PRICES[req.feature_type]
    
    # Generate unique reference (ACM-XXXX-XXXX format)
    import uuid
    reference_code = uuid.uuid4().hex[:8].upper()
    reference = f"{PAYID_CONFIG['reference_prefix']}-{reference_code}"
    
    # Store pending payment
    await db.payment_transactions.insert_one({
        "reference": reference,
        "user_id": user.user_id,
        "case_id": req.case_id,
        "feature_type": req.feature_type,
        "amount": feature["price"],
        "currency": feature["currency"],
        "method": "payid",
        "status": "pending",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "expires_at": datetime.now(timezone.utc).isoformat()  # 7 days
    })
    
    return {
        "reference": reference,
        "payid": PAYID_CONFIG["payid"],
        "payid_type": PAYID_CONFIG["payid_type"],
        "account_name": PAYID_CONFIG["account_name"],
        "amount": feature["price"],
        "currency": feature["currency"],
        "feature_name": feature["name"],
        "instructions": [
            "1. Open your banking app and select 'Pay Anyone' or 'Transfer'",
            "2. Choose 'PayID' as the payment method",
            f"3. Enter the PayID: {PAYID_CONFIG['payid']}",
            f"4. Verify the account name shows: {PAYID_CONFIG['account_name']}",
            f"5. Enter the amount: ${feature['price']:.2f} AUD",
            f"6. In the description/reference field, enter: {reference}",
            "7. Complete the transfer",
            "8. Return here and click 'I've made the payment' to verify"
        ]
    }


@router.post("/payid/verify")
async def verify_payid_payment(req: VerifyPayIDRequest, request: Request):
    """Verify a PayID payment (manual verification by admin)"""
    await get_current_user(request)  # Verify user is authenticated
    
    # Find the pending payment
    transaction = await db.payment_transactions.find_one(
        {"reference": req.reference, "case_id": req.case_id, "method": "payid"},
        {"_id": 0}
    )
    
    if not transaction:
        raise HTTPException(status_code=404, detail="Payment reference not found")
    
    if transaction["status"] == "completed":
        return {
            "status": "already_verified",
            "message": "This payment has already been verified and the feature is unlocked"
        }
    
    # Mark as pending verification
    await db.payment_transactions.update_one(
        {"reference": req.reference},
        {"$set": {
            "status": "pending_verification",
            "verification_requested_at": datetime.now(timezone.utc).isoformat()
        }}
    )
    
    return {
        "status": "pending_verification",
        "reference": req.reference,
        "message": "Your payment is being verified. This usually takes a few minutes during business hours. You'll receive access as soon as it's confirmed."
    }


@router.post("/payid/admin-confirm/{reference}")
async def admin_confirm_payid(reference: str, request: Request):
    """Admin endpoint to confirm PayID payment receipt"""
    user = await get_current_user(request)
    
    # Check if admin
    admin_emails = os.environ.get("ADMIN_EMAILS", "djkingy79@gmail.com").split(",")
    if user.email not in admin_emails:
        raise HTTPException(status_code=403, detail="Admin access required")
    
    transaction = await db.payment_transactions.find_one(
        {"reference": reference, "method": "payid"},
        {"_id": 0}
    )
    
    if not transaction:
        raise HTTPException(status_code=404, detail="Payment reference not found")
    
    # Mark as completed
    await db.payment_transactions.update_one(
        {"reference": reference},
        {"$set": {
            "status": "completed",
            "verified_by": user.email,
            "completed_at": datetime.now(timezone.utc).isoformat()
        }}
    )
    
    # Create payment record for feature unlocking
    await db.payments.insert_one({
        "user_id": transaction["user_id"],
        "case_id": transaction["case_id"],
        "feature_type": transaction["feature_type"],
        "amount": transaction["amount"],
        "currency": transaction["currency"],
        "method": "payid",
        "reference": reference,
        "status": "completed",
        "created_at": datetime.now(timezone.utc).isoformat()
    })
    
    # Send email notification to user
    email_sent = False
    payer_user = await db.users.find_one({"user_id": transaction["user_id"]}, {"_id": 0})
    if payer_user and payer_user.get("email"):
        feature_info = FEATURE_PRICES.get(transaction["feature_type"], {})
        email_sent = await send_payment_confirmation_email(
            user_email=payer_user["email"],
            user_name=payer_user.get("name", ""),
            feature_name=feature_info.get("name", transaction["feature_type"]),
            amount=transaction["amount"],
            reference=reference,
            case_id=transaction["case_id"]
        )
    
    return {
        "status": "confirmed",
        "reference": reference,
        "message": "Payment confirmed and feature unlocked for user",
        "email_sent": email_sent
    }


@router.get("/payid/pending")
async def get_pending_payid_payments(request: Request):
    """Admin endpoint to get all pending PayID payments"""
    user = await get_current_user(request)
    
    # Check if admin
    admin_emails = os.environ.get("ADMIN_EMAILS", "djkingy79@gmail.com").split(",")
    if user.email not in admin_emails:
        raise HTTPException(status_code=403, detail="Admin access required")
    
    pending = await db.payment_transactions.find(
        {"method": "payid", "status": {"$in": ["pending", "pending_verification"]}},
        {"_id": 0}
    ).sort("created_at", -1).to_list(100)
    
    return {"pending_payments": pending}
