# DO NOT UNDO — Weekly scheduled AI scan for legislation amendments.
"""
Weekly AI amendment scanner — runs every Monday at 09:00 AEST (23:00 UTC Sun).

Architecture: a single long-lived asyncio task that sleeps until the next
Monday 09:00 AEST, calls the same `ai_currency_check` logic the on-demand
`/admin/legislation/ai-scan` endpoint uses, and writes candidate amendments
to `legislation_amendments` with verification_status='ai_flagged'. Admin
manually confirms before users see them.

Safe-by-design:
- Only writes `ai_flagged` documents (never auto-confirms)
- Logs every run with counts
- Catches and logs any exception so a single failure doesn't kill the task
- Uses datetime arithmetic (no external cron dependency)
"""
from __future__ import annotations

import asyncio
import logging
import uuid
from datetime import datetime, timezone, timedelta

logger = logging.getLogger(__name__)

# AEST = UTC+10 (Australia has DST variations but 09:00 AEST ≈ 23:00 UTC is
# close enough for a weekly admin-review workflow).
_TARGET_DOW_UTC = 0   # Monday 00:00 UTC → around Mon 10:00/11:00 AEST
_TARGET_HOUR_UTC = 23 # Sunday 23:00 UTC → Monday 09:00/10:00 AEST
_MAX_ACTS_PER_SCAN = 12


def _seconds_until_next_run() -> float:
    """Return seconds from now until the next Sunday 23:00 UTC."""
    now = datetime.now(timezone.utc)
    # Find next Sunday at 23:00 UTC.
    days_ahead = (6 - now.weekday()) % 7  # 6 = Sunday
    candidate = (now + timedelta(days=days_ahead)).replace(
        hour=_TARGET_HOUR_UTC, minute=0, second=0, microsecond=0
    )
    if candidate <= now:
        candidate = candidate + timedelta(days=7)
    return (candidate - now).total_seconds()


async def _run_weekly_scan_once():
    """One full pass through the top Acts. Writes ai_flagged candidates and
    emails a digest to the configured admin emails so the admin can confirm
    each candidate in one sweep."""
    from config import db, get_admin_emails
    from frameworks.legislation_registry import LEGISLATION_REGISTRY
    from services.legislation_currency import ai_currency_check
    from services.email_service import send_admin_legislation_digest

    flagged_docs = []
    errors = 0
    acts = LEGISLATION_REGISTRY[:_MAX_ACTS_PER_SCAN]
    for entry in acts:
        act_name = entry["act_name"]
        jurisdiction = entry["jurisdiction"]
        try:
            result = await ai_currency_check(
                act_name=act_name,
                jurisdiction=jurisdiction,
                last_verified_iso="2025-01-01",
            )
            if not result.get("ok"):
                continue
            if result.get("status") == "possible_change" and result.get("flagged_amendments"):
                for fa in result["flagged_amendments"]:
                    flag_doc = {
                        "amendment_id": f"amnd_{uuid.uuid4().hex[:12]}",
                        "jurisdiction": jurisdiction.upper(),
                        "act_name": act_name,
                        "section": None,
                        "effective_date": f"{fa.get('approximate_year', datetime.now().year)}-01-01",
                        "amending_act": None,
                        "change_type": "amended",
                        "summary": (fa.get("description", "") or "")[:500],
                        "source_url": None,
                        "severity": "medium",
                        "verification_status": "ai_flagged",
                        "ai_source_hint": fa.get("source_hint"),
                        "ai_confidence": result.get("confidence"),
                        "ai_cutoff": result.get("knowledge_cutoff"),
                        "published_by": "system_weekly_scan",
                        "published_at": datetime.now(timezone.utc).isoformat(),
                    }
                    await db.legislation_amendments.insert_one(flag_doc.copy())
                    flag_doc.pop("_id", None)
                    flagged_docs.append(flag_doc)
        except Exception as exc:
            logger.warning("weekly_scan: %s failed — %s", act_name, exc)
            errors += 1
    logger.info("weekly_scan complete: %s Acts scanned, %s flagged, %s errors",
                len(acts), len(flagged_docs), errors)

    # Email the admin digest so they can confirm candidates in one sweep.
    try:
        admin_emails = get_admin_emails()
        if admin_emails:
            await send_admin_legislation_digest(
                admin_emails=admin_emails,
                flagged=flagged_docs,
                run_at_iso=datetime.now(timezone.utc).isoformat(),
            )
    except Exception as exc:
        logger.error("weekly_scan: digest email failed — %s", exc)

    return len(flagged_docs)


async def weekly_legislation_scan_loop():
    """Long-lived asyncio task. Call once at startup."""
    while True:
        try:
            wait_seconds = _seconds_until_next_run()
            logger.info("weekly_scan: next run in %.1f hours", wait_seconds / 3600)
            await asyncio.sleep(wait_seconds)
            await _run_weekly_scan_once()
        except asyncio.CancelledError:
            logger.info("weekly_scan loop cancelled")
            raise
        except Exception as exc:
            logger.error("weekly_scan loop exception: %s — retrying in 1 hour", exc)
            await asyncio.sleep(3600)
