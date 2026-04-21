# DO NOT UNDO — Legislation Alerts router. Backs a case-aware amendment
# tracker that surfaces changes to any Act referenced in the user's case.
"""
Legislation Alerts — case-aware real-time feed of legislative changes.

Added 2026-02-21 at owner's request. Laws change constantly. Appellate
practitioners need to know the MOMENT a section referenced in their case is
amended, renumbered, or repealed.

Architecture:
  1. Authoritative source of truth: `legislation_amendments` Mongo collection.
     Each document captures a single confirmed amendment.
  2. Admin workflow: bulk AI cross-check across the static REGISTRY →
     suggested amendments → admin manually confirms (which flips
     `verification_status` to "confirmed") → published to all users.
  3. Per-user acknowledgement via `legislation_alert_reads` so the bell
     badge in the case header clears once the user has seen the alert.
  4. Case linkage: on GET /cases/{id}/legislation-alerts we compute the
     intersection of (amendment.jurisdiction, amendment.act_name) with the
     Acts cited in the case's legal_framework + grounds_of_merit.

This router intentionally DOES NOT scrape state registers. Scraping 9
Australian jurisdictions reliably would require dedicated per-jurisdiction
parsers and constant maintenance. Instead, the admin uses the AI scan to
shortlist candidates, then manually verifies against AustLII before
publishing — zero hallucination risk, zero brittle scraping code.
"""
from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime, timezone
import uuid
import logging

from config import db, is_admin_user
from auth_utils import get_current_user

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api", tags=["legislation-alerts"])


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

async def _get_admin_user(request: Request):
    user = await get_current_user(request)
    if not is_admin_user(user.email):
        raise HTTPException(status_code=403, detail="Admin access required")
    return user


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


# ---------------------------------------------------------------------------
# Schemas
# ---------------------------------------------------------------------------

class AmendmentCreate(BaseModel):
    jurisdiction: str = Field(..., description="NSW|VIC|QLD|SA|WA|TAS|NT|ACT|CTH")
    act_name: str = Field(..., min_length=5, description="Full Act name, e.g. 'Crimes Act 1900'")
    section: Optional[str] = Field(None, description="Affected section(s), e.g. 's 18' or 'ss 19A-19B'")
    effective_date: str = Field(..., description="ISO date when amendment takes effect, YYYY-MM-DD")
    amending_act: Optional[str] = Field(None, description="Name of the amending statute")
    change_type: str = Field("amended", description="amended|repealed|renumbered|new_section|consolidation")
    summary: str = Field(..., min_length=20, description="Plain-English summary of the change and its practical effect on appeals")
    source_url: Optional[str] = Field(None, description="Authoritative URL, typically an AustLII or legislation.gov.au link")
    severity: str = Field("medium", description="low|medium|high|critical — critical = may require re-grounding live appeals")


# ---------------------------------------------------------------------------
# Public read endpoints
# ---------------------------------------------------------------------------

@router.get("/legislation/amendments", response_model=List[dict])
async def list_amendments(
    request: Request,
    jurisdiction: Optional[str] = None,
    since: Optional[str] = None,
    limit: int = 100,
):
    """List all CONFIRMED amendments, newest first. Optional jurisdiction
    filter (NSW|VIC|...) and ISO-date `since` filter."""
    await get_current_user(request)  # any authenticated user
    q = {"verification_status": "confirmed"}
    if jurisdiction:
        q["jurisdiction"] = jurisdiction.upper()
    if since:
        q["effective_date"] = {"$gte": since}
    items = await db.legislation_amendments.find(q, {"_id": 0}).sort(
        "effective_date", -1
    ).to_list(max(1, min(limit, 500)))
    return items


@router.get("/cases/{case_id}/legislation-alerts", response_model=dict)
async def get_case_legislation_alerts(case_id: str, request: Request):
    """Case-aware alert feed. Returns amendments affecting any Act referenced
    in this case's legal framework or grounds of merit, plus an unread count
    for the bell-badge UI."""
    user = await get_current_user(request)
    case = await db.cases.find_one(
        {"case_id": case_id, "user_id": user.user_id}, {"_id": 0}
    )
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")

    jurisdiction = (case.get("state") or "NSW").upper()

    # Strategy decision (2026-02-21): SHOW all amendments for this jurisdiction
    # + all federal (CTH) amendments. Previously this tried to intersect with
    # Acts explicitly named in the grounds text — but practitioners rarely
    # quote the full Act name in their drafts, so the intersection was too
    # aggressive and hid relevant updates. For criminal appeals, every current
    # amendment in the case's jurisdiction is relevant. Users can dismiss
    # individually via acknowledge.
    candidate = await db.legislation_amendments.find(
        {"verification_status": "confirmed", "jurisdiction": jurisdiction},
        {"_id": 0},
    ).sort("effective_date", -1).to_list(500)

    # Always include federal (CTH) amendments unless the jurisdiction IS CTH
    # (in which case they're already covered above).
    if jurisdiction != "CTH":
        cth_amends = await db.legislation_amendments.find(
            {"verification_status": "confirmed", "jurisdiction": "CTH"},
            {"_id": 0},
        ).sort("effective_date", -1).to_list(200)
    else:
        cth_amends = []

    read_ids = set()
    read_docs = await db.legislation_alert_reads.find(
        {"user_id": user.user_id, "case_id": case_id}, {"_id": 0, "amendment_id": 1}
    ).to_list(500)
    for d in read_docs:
        if d.get("amendment_id"):
            read_ids.add(d["amendment_id"])

    matched = []
    for amend in candidate + cth_amends:
        item = dict(amend)
        item["acknowledged"] = amend.get("amendment_id") in read_ids
        matched.append(item)

    # Sort combined list by effective_date desc
    matched.sort(key=lambda a: a.get("effective_date", ""), reverse=True)

    unread_count = sum(1 for m in matched if not m["acknowledged"])

    return {
        "case_id": case_id,
        "jurisdiction": jurisdiction,
        "alerts": matched,
        "total": len(matched),
        "unread_count": unread_count,
    }


@router.post("/cases/{case_id}/legislation-alerts/{amendment_id}/acknowledge", response_model=dict)
async def acknowledge_alert(case_id: str, amendment_id: str, request: Request):
    """Mark a specific amendment as read for this case. Clears the bell badge."""
    user = await get_current_user(request)
    await db.legislation_alert_reads.update_one(
        {"user_id": user.user_id, "case_id": case_id, "amendment_id": amendment_id},
        {"$set": {
            "user_id": user.user_id,
            "case_id": case_id,
            "amendment_id": amendment_id,
            "acknowledged_at": _now_iso(),
        }},
        upsert=True,
    )
    return {"ok": True, "amendment_id": amendment_id}


# ---------------------------------------------------------------------------
# Admin workflow — create / confirm amendments
# ---------------------------------------------------------------------------

@router.post("/admin/legislation/amendments", response_model=dict)
async def create_amendment(payload: AmendmentCreate, request: Request):
    """Admin-only: record a confirmed amendment."""
    admin = await _get_admin_user(request)
    amendment_id = f"amnd_{uuid.uuid4().hex[:12]}"
    doc = {
        "amendment_id": amendment_id,
        "jurisdiction": payload.jurisdiction.upper(),
        "act_name": payload.act_name.strip(),
        "section": (payload.section or "").strip() or None,
        "effective_date": payload.effective_date[:10],
        "amending_act": (payload.amending_act or "").strip() or None,
        "change_type": payload.change_type,
        "summary": payload.summary.strip(),
        "source_url": (payload.source_url or "").strip() or None,
        "severity": payload.severity,
        "verification_status": "confirmed",
        "published_by": admin.user_id,
        "published_at": _now_iso(),
    }
    await db.legislation_amendments.insert_one(doc.copy())
    doc.pop("_id", None)
    return doc


@router.patch("/admin/legislation/amendments/{amendment_id}", response_model=dict)
async def update_amendment(amendment_id: str, payload: dict, request: Request):
    """Admin-only: edit an existing amendment (e.g. correct a typo)."""
    await _get_admin_user(request)
    # Whitelist the editable fields to prevent accidental mutation of IDs.
    editable = {"act_name", "section", "effective_date", "amending_act",
                "change_type", "summary", "source_url", "severity",
                "verification_status"}
    patch = {k: v for k, v in payload.items() if k in editable and v is not None}
    if not patch:
        raise HTTPException(status_code=400, detail="No editable fields supplied")
    patch["updated_at"] = _now_iso()
    result = await db.legislation_amendments.update_one(
        {"amendment_id": amendment_id}, {"$set": patch}
    )
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Amendment not found")
    doc = await db.legislation_amendments.find_one({"amendment_id": amendment_id}, {"_id": 0})
    return doc or {"ok": True}


@router.delete("/admin/legislation/amendments/{amendment_id}", response_model=dict)
async def delete_amendment(amendment_id: str, request: Request):
    """Admin-only: delete an erroneously-published amendment."""
    await _get_admin_user(request)
    result = await db.legislation_amendments.delete_one({"amendment_id": amendment_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Amendment not found")
    return {"ok": True, "deleted": amendment_id}


@router.post("/admin/legislation/ai-scan", response_model=dict)
async def run_ai_amendment_scan(request: Request):
    """Admin-only: run the guardrailed AI currency check across the static
    REGISTRY and shortlist Acts that the AI flags as 'possible_change'. These
    are written to `legislation_amendments` with verification_status='ai_flagged'
    so the admin can manually confirm before publishing. NEVER auto-published."""
    admin = await _get_admin_user(request)
    from frameworks.legislation_registry import LEGISLATION_REGISTRY
    from services.legislation_currency import ai_currency_check

    flagged = []
    errors = []
    # Cap at 12 Acts per scan to respect rate limits + credits. Caller can
    # re-run with a filter in a follow-up.
    acts_to_scan = LEGISLATION_REGISTRY[:12]
    for entry in acts_to_scan:
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
                        "published_by": admin.user_id,
                        "published_at": _now_iso(),
                    }
                    await db.legislation_amendments.insert_one(flag_doc.copy())
                    flag_doc.pop("_id", None)
                    flagged.append(flag_doc)
        except Exception as exc:
            logger.warning("AI scan failed for %s: %s", act_name, exc)
            errors.append({"act": act_name, "error": str(exc)[:200]})

    return {
        "ok": True,
        "scanned": len(acts_to_scan),
        "flagged_count": len(flagged),
        "flagged": flagged,
        "errors": errors,
        "note": "Items flagged by AI must be manually confirmed via PATCH /admin/legislation/amendments/{id} with {\"verification_status\":\"confirmed\"} before they surface to end users.",
    }
