"""
Criminal Appeal AI - Email Service
Payment notification emails via Resend.
"""
import os
import asyncio
import logging
import resend

from config import get_resend_from_email

logger = logging.getLogger(__name__)

RESEND_API_KEY = os.environ.get("RESEND_API_KEY")
RESEND_CONFIGURED = False
if RESEND_API_KEY:
    resend.api_key = RESEND_API_KEY
    RESEND_CONFIGURED = True
    logger.info("Resend configured for live payment notices")


async def send_payid_status_email(user_email: str, user_name: str, feature_name: str, amount: float, reference: str, subject: str, heading: str, message_html: str):
    if not RESEND_CONFIGURED or not user_email:
        logger.warning("Cannot send payment notice email - Resend not configured or recipient missing")
        return False

    try:
        html = f"""
        <!DOCTYPE html>
        <html>
        <body style="margin:0;padding:0;background:#f8fafc;font-family:Arial,sans-serif;color:#0f172a;">
          <div style="max-width:680px;margin:0 auto;padding:24px;">
            <div style="background:#1d4ed8;color:#ffffff;padding:28px 24px;border-radius:18px 18px 0 0;">
              <div style="font-size:12px;letter-spacing:0.18em;text-transform:uppercase;font-weight:800;opacity:0.92;">Appeal Case Manager</div>
              <h1 style="margin:10px 0 0;font-size:28px;line-height:1.2;">{heading}</h1>
            </div>
            <div style="background:#ffffff;border:1px solid #dbeafe;border-top:none;padding:24px 24px 16px;">
              <p style="margin:0 0 16px;line-height:1.7;">Dear {user_name or 'Valued Client'},</p>
              {message_html}
              <div style="margin:20px 0;padding:18px;border-radius:14px;background:#eff6ff;border:1px solid #bfdbfe;">
                <div style="display:flex;justify-content:space-between;gap:12px;padding:6px 0;border-bottom:1px solid #dbeafe;"><strong>Feature</strong><span>{feature_name}</span></div>
                <div style="display:flex;justify-content:space-between;gap:12px;padding:6px 0;border-bottom:1px solid #dbeafe;"><strong>Amount</strong><span>${amount:.2f} AUD</span></div>
                <div style="display:flex;justify-content:space-between;gap:12px;padding:6px 0;"><strong>Reference</strong><span style="font-family:monospace;">{reference}</span></div>
              </div>
              <p style="margin:18px 0 0;line-height:1.7;">Created and Designed by Deb King</p>
            </div>
          </div>
        </body>
        </html>
        """

        params = {
            "from": get_resend_from_email(),
            "to": [user_email],
            "subject": subject,
            "html": html,
        }
        await asyncio.to_thread(resend.Emails.send, params)
        logger.info(f"PayID notice email sent to {user_email} for {reference}")
        return True
    except Exception as exc:
        logger.error(f"Failed to send PayID notice email: {exc}")
        return False


async def send_admin_payid_alert(admin_emails: list, user_email: str, user_name: str, feature_name: str, amount: float, reference: str, case_id: str, frontend_url: str, confirm_url: str = ""):
    """Send email to admin when a user submits a PayID payment for verification"""
    if not RESEND_CONFIGURED or not admin_emails:
        logger.warning("Cannot send admin PayID alert - Resend not configured or no admin emails")
        return False

    try:
        admin_link = f"{frontend_url}/admin"

        # Build the confirm button — big and obvious if confirm_url is provided
        confirm_button_html = ""
        if confirm_url:
            confirm_button_html = f"""
              <p style="text-align:center;margin:24px 0 8px;">
                <a href="{confirm_url}" style="background:#16a34a;color:white;padding:18px 40px;text-decoration:none;border-radius:10px;display:inline-block;font-weight:bold;font-size:18px;letter-spacing:0.5px;">CONFIRM PAYMENT</a>
              </p>
              <p style="text-align:center;color:#6b7280;font-size:12px;margin:4px 0 16px;">Click above to instantly confirm and unlock the feature for this user</p>
            """

        html = f"""
        <!DOCTYPE html>
        <html>
        <body style="margin:0;padding:0;background:#f8fafc;font-family:Arial,sans-serif;color:#0f172a;">
          <div style="max-width:680px;margin:0 auto;padding:24px;">
            <div style="background:#dc2626;color:#ffffff;padding:28px 24px;border-radius:18px 18px 0 0;">
              <div style="font-size:12px;letter-spacing:0.18em;text-transform:uppercase;font-weight:800;opacity:0.92;">Appeal Case Manager</div>
              <h1 style="margin:10px 0 0;font-size:28px;line-height:1.2;">NEW PAYID PAYMENT SUBMITTED</h1>
              <p style="margin:8px 0 0;opacity:0.9;">Action Required &mdash; Verify &amp; Confirm</p>
            </div>
            <div style="background:#ffffff;border:1px solid #fecaca;border-top:none;padding:24px 24px 16px;">
              <p style="margin:0 0 16px;line-height:1.7;">A user has submitted a PayID bank transfer and is waiting for confirmation.</p>
              <div style="margin:20px 0;padding:18px;border-radius:14px;background:#fef3c7;border:2px solid #f59e0b;">
                <div style="padding:6px 0;border-bottom:1px solid #fde68a;"><strong>User:</strong> {user_name or 'Unknown'} ({user_email})</div>
                <div style="padding:6px 0;border-bottom:1px solid #fde68a;"><strong>Feature:</strong> {feature_name}</div>
                <div style="padding:6px 0;border-bottom:1px solid #fde68a;"><strong>Amount:</strong> ${amount:.2f} AUD</div>
                <div style="padding:6px 0;border-bottom:1px solid #fde68a;"><strong>Reference:</strong> <span style="font-family:monospace;font-size:16px;color:#dc2626;">{reference}</span></div>
                <div style="padding:6px 0;"><strong>Case ID:</strong> {case_id}</div>
              </div>
              {confirm_button_html}
              <p style="margin:16px 0 8px;"><strong>Or confirm via Admin Dashboard:</strong></p>
              <p style="text-align:center;margin:8px 0;">
                <a href="{admin_link}" style="background:#2563eb;color:white;padding:12px 24px;text-decoration:none;border-radius:8px;display:inline-block;font-weight:bold;">Open Admin Dashboard</a>
              </p>
            </div>
          </div>
        </body>
        </html>
        """

        params = {
            "from": get_resend_from_email(),
            "to": admin_emails,
            "subject": f"NEW PAYMENT - {user_name or user_email} paid ${amount:.2f} for {feature_name} (Ref: {reference})",
            "html": html,
        }
        await asyncio.to_thread(resend.Emails.send, params)
        logger.info(f"Admin PayID alert sent for reference {reference} to {admin_emails}")
        return True
    except Exception as exc:
        logger.error(f"Failed to send admin PayID alert: {exc}")
        return False
