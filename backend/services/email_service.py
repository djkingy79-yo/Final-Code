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


async def send_admin_legislation_digest(admin_emails: list, flagged: list, run_at_iso: str):
    """Monday-morning digest of AI-flagged legislative amendments pending
    admin confirmation. Plain, forensic tone — no editorialising, no
    opinions about judicial conduct. Simple table so the admin can skim
    and confirm in a minute."""
    if not RESEND_CONFIGURED or not admin_emails:
        logger.warning("Cannot send legislation digest — Resend not configured or no recipients")
        return False
    if not flagged:
        logger.info("legislation digest: 0 flagged amendments this week — email skipped")
        return True

    rows_html = ""
    for f in flagged[:40]:  # cap at 40 rows per email
        jur = (f.get("jurisdiction") or "").upper()
        act = (f.get("act_name") or "").replace("<", "&lt;").replace(">", "&gt;")
        summary = (f.get("summary") or "").replace("<", "&lt;").replace(">", "&gt;")[:320]
        effective = (f.get("effective_date") or "")[:10]
        confidence = f.get("ai_confidence", "")
        rows_html += (
            f'<tr>'
            f'<td style="padding:8px 10px;border-bottom:1px solid #e2e8f0;font-weight:700;color:#1e3a8a;">{jur}</td>'
            f'<td style="padding:8px 10px;border-bottom:1px solid #e2e8f0;"><strong>{act}</strong><br/>'
            f'<span style="font-size:12px;color:#475569;">{summary}</span></td>'
            f'<td style="padding:8px 10px;border-bottom:1px solid #e2e8f0;font-size:12px;color:#64748b;">{effective}</td>'
            f'<td style="padding:8px 10px;border-bottom:1px solid #e2e8f0;font-size:12px;color:#64748b;">{confidence}</td>'
            f'</tr>'
        )

    html = f"""
    <!DOCTYPE html>
    <html>
    <body style="margin:0;padding:0;background:#f8fafc;font-family:'Times New Roman',Times,serif;color:#0f172a;">
      <div style="max-width:720px;margin:0 auto;padding:24px;">
        <div style="background:#1d4ed8;color:#ffffff;padding:24px;border-radius:10px 10px 0 0;">
          <div style="font-size:12px;letter-spacing:0.16em;text-transform:uppercase;font-weight:800;opacity:0.92;">Appeal Case Manager</div>
          <h1 style="margin:8px 0 0;font-size:22px;line-height:1.3;">Weekly Legislation Scan — {len(flagged)} candidate(s) for review</h1>
        </div>
        <div style="background:#ffffff;border:1px solid #dbeafe;border-top:none;padding:20px 24px;">
          <p style="margin:0 0 12px;font-size:14px;line-height:1.6;">
            The scheduled AI scan completed at <strong>{run_at_iso}</strong> and flagged the following candidate amendments for manual verification.
            None of these are visible to end users until the admin confirms each via the Legislation Currency panel.
          </p>
          <table style="width:100%;border-collapse:collapse;font-size:13px;line-height:1.5;">
            <thead>
              <tr style="background:#eff6ff;">
                <th style="padding:8px 10px;text-align:left;font-size:11px;text-transform:uppercase;letter-spacing:0.06em;color:#1e3a8a;border-bottom:2px solid #bfdbfe;">Jurisdiction</th>
                <th style="padding:8px 10px;text-align:left;font-size:11px;text-transform:uppercase;letter-spacing:0.06em;color:#1e3a8a;border-bottom:2px solid #bfdbfe;">Act &amp; AI summary</th>
                <th style="padding:8px 10px;text-align:left;font-size:11px;text-transform:uppercase;letter-spacing:0.06em;color:#1e3a8a;border-bottom:2px solid #bfdbfe;">Approx. effective</th>
                <th style="padding:8px 10px;text-align:left;font-size:11px;text-transform:uppercase;letter-spacing:0.06em;color:#1e3a8a;border-bottom:2px solid #bfdbfe;">AI confidence</th>
              </tr>
            </thead>
            <tbody>{rows_html}</tbody>
          </table>
          <div style="margin-top:16px;padding:12px 14px;border-radius:6px;background:#fef3c7;border:1px solid #fcd34d;font-size:12px;line-height:1.55;">
            <strong>Verification reminder:</strong> each candidate must be cross-checked against the authoritative source (legislation.gov.au or the relevant state register / AustLII) before publication. Entries remain hidden until the admin sets <code>verification_status="confirmed"</code>.
          </div>
          <p style="margin:16px 0 0;font-size:13px;line-height:1.6;">
            Review and confirm at: <a href="https://criminallawappealmanagement.com.au/admin/legislation-currency" style="color:#1d4ed8;">Legislation Currency admin panel</a>.
          </p>
        </div>
        <div style="background:#f1f5f9;color:#475569;padding:14px 24px;border-radius:0 0 10px 10px;font-size:11px;font-style:italic;">
          This is an automated digest generated by the weekly AI legislation scan. It is not legal advice; no candidate flagged here has been independently verified.
        </div>
      </div>
    </body>
    </html>
    """
    try:
        params = {
            "from": get_resend_from_email(),
            "to": admin_emails,
            "subject": f"[Legislation Scan] {len(flagged)} amendment candidate(s) for review — {run_at_iso[:10]}",
            "html": html,
        }
        await asyncio.to_thread(resend.Emails.send, params)
        logger.info("Legislation digest sent to %s (%d flagged)", admin_emails, len(flagged))
        return True
    except Exception as exc:
        logger.error("Failed to send legislation digest: %s", exc)
        return False
