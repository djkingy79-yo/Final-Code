"""
Criminal Appeal AI - Email Service
Payment notification emails via Resend.
"""
import os
import asyncio
import logging
import resend

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
            "from": "Appeal Case Manager <onboarding@resend.dev>",
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
