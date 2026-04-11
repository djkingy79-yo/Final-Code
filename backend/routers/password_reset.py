# DO NOT UNDO — password_reset router. All endpoints in this file are approved and must be preserved.
"""
Criminal Appeal AI - Password Reset Router
Handles forgot password and password reset functionality
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, EmailStr
from datetime import datetime, timezone, timedelta
import secrets
import os
import asyncio
import resend

from config import db, logger, get_frontend_url, get_contact_email, get_resend_from_email
from routers.auth import hash_password

router = APIRouter(prefix="/api/auth", tags=["password-reset"])

# Resend configuration
RESEND_API_KEY = os.environ.get("RESEND_API_KEY", "")
if RESEND_API_KEY:
    resend.api_key = RESEND_API_KEY
    logger.info("Resend configured for password reset emails")
else:
    logger.warning("Resend API key not configured - password reset will store tokens but not send emails")

# ============ REQUEST MODELS ============

class ForgotPasswordRequest(BaseModel):
    email: EmailStr

class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str

# ============ PASSWORD RESET ENDPOINTS ============

@router.post("/forgot-password")
async def forgot_password(request: ForgotPasswordRequest):
    """Send password reset email"""
    try:
        # Find user by email
        user = await db.users.find_one({"email": request.email.lower()}, {"_id": 0})
        
        # Always return success (don't reveal if email exists for security)
        if not user:
            logger.info(f"Password reset requested for non-existent email: {request.email}")
            return {
                "success": True,
                "message": "If an account exists with this email, a password reset link has been sent."
            }
        
        # Check if user uses email auth (not Google OAuth)
        if not user.get("password_hash"):
            logger.info(f"Password reset requested for Google OAuth user: {request.email}")
            return {
                "success": True,
                "message": "This account uses Google login. Please sign in with Google."
            }
        
        # Generate reset token
        reset_token = secrets.token_urlsafe(32)
        expires_at = datetime.now(timezone.utc) + timedelta(hours=1)  # Token valid for 1 hour
        
        # Store reset token
        await db.password_reset_tokens.insert_one({
            "token": reset_token,
            "user_id": user["user_id"],
            "email": user["email"],
            "expires_at": expires_at.isoformat(),
            "used": False,
            "created_at": datetime.now(timezone.utc).isoformat()
        })
        
        # Send email if Resend is configured
        email_sent = False
        if RESEND_API_KEY:
            try:
                reset_url = f"{get_frontend_url()}/reset-password?token={reset_token}"
                
                html_content = f"""
                <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
                    <div style="background: linear-gradient(135deg, #1e293b 0%, #334155 100%); padding: 30px; text-align: center; border-radius: 10px 10px 0 0;">
                        <h1 style="color: #f59e0b; margin: 0; font-size: 28px;">Appeal Case Manager</h1>
                    </div>
                    
                    <div style="background: #f8fafc; padding: 40px 30px; border-radius: 0 0 10px 10px;">
                        <h2 style="color: #1e293b; margin-top: 0;">Reset Your Password</h2>
                        
                        <p style="color: #475569; line-height: 1.6;">
                            You requested to reset your password for your Appeal Case Manager account.
                            Click the button below to create a new password:
                        </p>
                        
                        <div style="text-align: center; margin: 30px 0;">
                            <a href="{reset_url}" style="background: #f59e0b; color: white; padding: 14px 32px; text-decoration: none; border-radius: 8px; font-weight: bold; display: inline-block;">
                                Reset Password
                            </a>
                        </div>
                        
                        <p style="color: #64748b; font-size: 14px; line-height: 1.6;">
                            Or copy and paste this link into your browser:<br/>
                            <a href="{reset_url}" style="color: #3b82f6; word-break: break-all;">{reset_url}</a>
                        </p>
                        
                        <div style="background: #fee2e2; border-left: 4px solid #ef4444; padding: 12px 16px; margin: 20px 0; border-radius: 4px;">
                            <p style="color: #991b1b; margin: 0; font-size: 13px;">
                                <strong>⚠️ Important:</strong> This link expires in 1 hour. If you didn't request this reset, please ignore this email.
                            </p>
                        </div>
                        
                        <p style="color: #94a3b8; font-size: 12px; margin-top: 30px; border-top: 1px solid #cbd5e1; padding-top: 20px;">
                            This email was sent from Appeal Case Manager. If you have questions, contact us at {get_contact_email()}
                        </p>
                    </div>
                </div>
                """
                
                params = {
                    "from": get_resend_from_email(),
                    "to": [user["email"]],
                    "subject": "Reset Your Password - Appeal Case Manager",
                    "html": html_content
                }
                
                await asyncio.to_thread(resend.Emails.send, params)
                email_sent = True
                logger.info(f"Password reset email sent to {user['email']}")
            except Exception as e:
                logger.error(f"Failed to send password reset email: {e}")
        
        return {
            "success": True,
            "message": "If an account exists with this email, a password reset link has been sent.",
            "email_sent": email_sent,
            "token_for_testing": reset_token if not RESEND_API_KEY else None  # Only in dev mode
        }
        
    except Exception as e:
        logger.error(f"Forgot password error: {e}")
        raise HTTPException(status_code=500, detail="Failed to process password reset request")


@router.post("/reset-password")
async def reset_password(request: ResetPasswordRequest):
    """Reset password using token"""
    try:
        # Find and validate token
        token_doc = await db.password_reset_tokens.find_one({
            "token": request.token,
            "used": False
        }, {"_id": 0})
        
        if not token_doc:
            raise HTTPException(status_code=400, detail="Invalid or expired reset token")
        
        # Check if token expired
        expires_at = datetime.fromisoformat(token_doc["expires_at"])
        if datetime.now(timezone.utc) > expires_at:
            raise HTTPException(status_code=400, detail="Reset token has expired. Please request a new one.")
        
        # Validate new password
        if len(request.new_password) < 6:
            raise HTTPException(status_code=400, detail="Password must be at least 6 characters")
        
        # Hash new password
        hashed_password, salt = hash_password(request.new_password)
        
        # Update user password
        await db.users.update_one(
            {"user_id": token_doc["user_id"]},
            {"$set": {
                "password_hash": hashed_password,
                "password_salt": salt,
                "updated_at": datetime.now(timezone.utc).isoformat()
            }}
        )
        
        # Mark token as used
        await db.password_reset_tokens.update_one(
            {"token": request.token},
            {"$set": {
                "used": True,
                "used_at": datetime.now(timezone.utc).isoformat()
            }}
        )
        
        logger.info(f"Password reset successful for user {token_doc['user_id']}")
        
        return {
            "success": True,
            "message": "Password reset successful. You can now login with your new password."
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Reset password error: {e}")
        raise HTTPException(status_code=500, detail="Failed to reset password")


@router.get("/verify-reset-token/{token}")
async def verify_reset_token(token: str):
    """Verify if a reset token is valid (for frontend validation)"""
    try:
        token_doc = await db.password_reset_tokens.find_one({
            "token": token,
            "used": False
        }, {"_id": 0})
        
        if not token_doc:
            return {"valid": False, "message": "Invalid token"}
        
        # Check if token expired
        expires_at = datetime.fromisoformat(token_doc["expires_at"])
        if datetime.now(timezone.utc) > expires_at:
            return {"valid": False, "message": "Token expired"}
        
        return {
            "valid": True,
            "email": token_doc["email"],
            "expires_in_minutes": int((expires_at - datetime.now(timezone.utc)).total_seconds() / 60)
        }
        
    except Exception as e:
        logger.error(f"Verify token error: {e}")
        return {"valid": False, "message": "Error verifying token"}
