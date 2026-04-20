"""
Legislation Currency Service.

Two operations:
  1. `build_dashboard()` — aggregate per-Act status with age bucketing,
     merging the static REGISTRY with any manual "verified today" ticks
     recorded in the `framework_audit_log` Mongo collection.
  2. `ai_currency_check()` — HEAVILY guardrailed GPT-4o cross-check that
     produces a *prompt for manual review*, never a verification.

FORENSIC ANTI-HALLUCINATION RULES (apply to every AI call in this module):
  - The AI is FORBIDDEN from fabricating section numbers, amendment dates,
    or statutes that it is not certain exist in its training corpus.
  - The AI MUST respond ONLY in the strict JSON schema below.
  - The AI MUST declare its knowledge cutoff explicitly in every response.
  - Any uncertainty MUST collapse to `status: "cannot_verify"` — not to a
    best-guess fact.
  - Output is STRICTLY a *prompt for human verification*. The dashboard
    will refuse to mark anything verified based on AI output alone.
  - Forensic third-person language only; no "you", "we", "I"; no generic
    filler. Every sentence must carry forensic content.
  - If the AI has no specific knowledge of the Act, it MUST return
    `status: "outside_knowledge_cutoff"` — never invent content.
"""
from __future__ import annotations

import json
import logging
import re
from datetime import datetime, timezone
from typing import Optional

from config import db
from frameworks.legislation_registry import LEGISLATION_REGISTRY, search_url_for
from services.llm_service import call_llm_structured

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Dashboard aggregation
# ---------------------------------------------------------------------------

_GREEN_DAYS = 90      # < 3 months — current
_YELLOW_DAYS = 180    # 3–6 months — review soon
# > 6 months — review overdue (RED)


def _bucket(days_since: int) -> str:
    if days_since < _GREEN_DAYS:
        return "current"
    if days_since < _YELLOW_DAYS:
        return "review_soon"
    return "overdue"


async def build_dashboard(jurisdiction: Optional[str] = None) -> dict:
    """Return the full currency dashboard, optionally filtered by jurisdiction.

    Merges the static REGISTRY with the newest `framework_audit_log` entry
    per Act (where a user manually ticked "verified today").
    """
    # Pull latest verification per Act from Mongo
    audit_rows = await db.framework_audit_log.aggregate([
        {"$match": {"event": "verified"}},
        {"$sort": {"verified_at": -1}},
        {"$group": {
            "_id": "$act_name",
            "verified_at": {"$first": "$verified_at"},
            "verified_by": {"$first": "$verified_by"},
            "notes": {"$first": "$notes"},
        }},
    ]).to_list(500)
    latest_by_act = {row["_id"]: row for row in audit_rows}

    now = datetime.now(timezone.utc).date()
    rows = []
    for entry in LEGISLATION_REGISTRY:
        if jurisdiction and entry["jurisdiction"] != jurisdiction:
            continue

        # Pick whichever is more recent: static registry or Mongo audit log
        registry_date = datetime.fromisoformat(entry["last_verified"]).date()
        override = latest_by_act.get(entry["act_name"])
        if override and override.get("verified_at"):
            override_date = _parse_date(override["verified_at"])
            effective = max(registry_date, override_date)
            source = "audit_log" if override_date >= registry_date else "registry"
            verified_by = override.get("verified_by") if source == "audit_log" else None
            notes = override.get("notes") or entry.get("notes", "")
        else:
            effective = registry_date
            source = "registry"
            verified_by = None
            notes = entry.get("notes", "")

        days_since = (now - effective).days
        rows.append({
            "act_name": entry["act_name"],
            "short_name": entry["short_name"],
            "year": entry["year"],
            "jurisdiction": entry["jurisdiction"],
            "austlii_url": entry["austlii_url"],
            "austlii_search_url": search_url_for(entry),
            "last_verified": effective.isoformat(),
            "days_since_verified": days_since,
            "status": _bucket(days_since),
            "verification_source": source,
            "verified_by": verified_by,
            "notes": notes,
        })

    rows.sort(key=lambda r: (r["jurisdiction"], r["year"], r["short_name"]))

    totals = {"current": 0, "review_soon": 0, "overdue": 0}
    for r in rows:
        totals[r["status"]] += 1

    return {
        "total": len(rows),
        "totals": totals,
        "rows": rows,
        "buckets": {"green_max_days": _GREEN_DAYS, "yellow_max_days": _YELLOW_DAYS},
        "forensic_notice": (
            "This dashboard aggregates the `last_verified` date for every Act "
            "referenced in the legal framework. A tick recorded here certifies "
            "only that the responsible practitioner has manually confirmed the "
            "Act and its cited sections against the authoritative source "
            "(AustLII / legislation.gov.au). AI-assisted cross-checks provided "
            "by this application are prompts for human review and do NOT "
            "constitute verification."
        ),
    }


def _parse_date(value) -> "datetime.date":
    """Tolerantly parse an ISO date / datetime string or datetime object."""
    if isinstance(value, datetime):
        return value.date()
    try:
        return datetime.fromisoformat(str(value).replace("Z", "+00:00")).date()
    except ValueError:
        return datetime.strptime(str(value)[:10], "%Y-%m-%d").date()


# ---------------------------------------------------------------------------
# Manual verification
# ---------------------------------------------------------------------------

async def mark_verified(*, act_name: str, verified_by: str, notes: str = "") -> dict:
    """Record a manual 'verified today' tick in framework_audit_log.

    Returns the updated dashboard row for this Act.
    """
    entry = next((e for e in LEGISLATION_REGISTRY if e["act_name"] == act_name), None)
    if entry is None:
        raise ValueError(f"Act not in registry: {act_name}")

    doc = {
        "event": "verified",
        "act_name": act_name,
        "jurisdiction": entry["jurisdiction"],
        "verified_by": verified_by,
        "verified_at": datetime.now(timezone.utc),
        "notes": (notes or "").strip()[:500],
    }
    await db.framework_audit_log.insert_one(doc)
    logger.info(f"Legislation currency: {act_name} marked verified by {verified_by}")

    # Return the refreshed row
    dash = await build_dashboard()
    for row in dash["rows"]:
        if row["act_name"] == act_name:
            return row
    raise RuntimeError("Failed to locate refreshed row")


# ---------------------------------------------------------------------------
# AI cross-check — HEAVILY guardrailed
# ---------------------------------------------------------------------------

_AI_SYSTEM_PROMPT = """You are a forensic legislative currency checker assisting an Australian criminal appellate practitioner.

INPUT: A single Australian statute (Act / Code / Rule) with its jurisdiction and the last date it was manually verified.

TASK: Assess whether, within the bounds of your training corpus, the Act is likely to remain current or whether an amendment, repeal, or renumbering has been reported since the `last_verified` date.

ABSOLUTE RULES — VIOLATION IS A HALLUCINATION:
1. NEVER fabricate a section number, amendment date, case citation, or statute name. If uncertain, return `cannot_verify`.
2. NEVER claim knowledge of events after your training cutoff. Declare the cutoff explicitly in every response.
3. NEVER recommend that the Act is "verified". This tool produces only PROMPTS for human review.
4. NEVER invent the name of an amending Act or a section that you are not certain exists.
5. If the Act is obscure or you lack specific training coverage, return `outside_knowledge_cutoff` — do not guess.
6. Use strict third-person forensic appellate language. No "I", "we", "you", "us". No generic filler.
7. Respond ONLY in the JSON schema below. No prose, no markdown, no commentary outside the JSON.

JSON SCHEMA:
{
  "status": "appears_current" | "possible_change" | "cannot_verify" | "outside_knowledge_cutoff",
  "confidence": "low" | "medium" | "high",
  "knowledge_cutoff": "YYYY-MM",
  "forensic_summary": "One-to-three sentence third-person summary of the analysis, no filler.",
  "suggested_review_focus": ["Bullet list of specific points the human should verify on AustLII."],
  "flagged_amendments": [
    {"approximate_year": 2023, "description": "Short description of reported amendment.", "source_hint": "Where this was seen in the training corpus (e.g. 'Hansard reports', 'secondary legal commentary'). NEVER fabricate."}
  ],
  "forensic_caveat": "This AI output is a prompt for human verification. It does not constitute confirmation that the Act is current."
}

`flagged_amendments` may be an empty array. `confidence` must be `low` unless the model has direct, specific recall of the amendment in question.
"""


def _validate_ai_response(parsed: dict) -> bool:
    """Strict schema validator — returns False if the model tried to fabricate."""
    required_keys = {
        "status", "confidence", "knowledge_cutoff", "forensic_summary",
        "suggested_review_focus", "flagged_amendments", "forensic_caveat",
    }
    if not isinstance(parsed, dict):
        return False
    if not required_keys.issubset(parsed.keys()):
        return False
    if parsed["status"] not in {"appears_current", "possible_change", "cannot_verify", "outside_knowledge_cutoff"}:
        return False
    if parsed["confidence"] not in {"low", "medium", "high"}:
        return False
    if not isinstance(parsed["flagged_amendments"], list):
        return False
    if not isinstance(parsed["suggested_review_focus"], list):
        return False
    # Reject generic forensic_summary filler (anti-hallucination signal)
    summary = (parsed.get("forensic_summary") or "").strip()
    if len(summary) < 15:
        return False
    banned_generic = {"lorem ipsum", "as an ai", "i'm sorry", "as a language model"}
    low = summary.lower()
    if any(b in low for b in banned_generic):
        return False
    # Forensic language check — first-person pronouns leak forbidden style
    if re.search(r"\b(i|we|you|us|our)\b", low):
        return False
    return True


async def ai_currency_check(*, act_name: str, jurisdiction: str, last_verified: str, session_id: str) -> dict:
    """Run the anti-hallucination-guarded AI cross-check for a single Act.

    Returns a dict with the AI output PLUS guardrail metadata so the
    dashboard can display the appropriate level of caution.
    """
    user_prompt = (
        f"Statute under review: {act_name}\n"
        f"Jurisdiction: {jurisdiction.upper()}\n"
        f"Last manually verified: {last_verified}\n\n"
        "Produce the JSON report per the schema in the system prompt. "
        "If no specific amendment is recalled, set status to 'appears_current' "
        "only when you have direct training-corpus recall of the Act's "
        "unchanged state; otherwise default to 'cannot_verify' or "
        "'outside_knowledge_cutoff'. Do not invent."
    )

    result = await call_llm_structured(
        system_prompt=_AI_SYSTEM_PROMPT,
        user_prompt=user_prompt,
        session_id=session_id,
        task_type="json_analysis",
        timeout_seconds=60,
        require_json=True,
    )

    if not result.get("ok"):
        return {
            "ok": False,
            "guardrail": "llm_failure",
            "error": result.get("error", "AI check failed"),
            "forensic_caveat": "AI cross-check did not complete. Please verify manually via AustLII.",
        }

    # Parse & validate the JSON content
    content = result.get("content", "")
    parsed = None
    try:
        parsed = json.loads(content)
    except json.JSONDecodeError:
        # Try to locate a JSON object inside the response (model went off-script)
        m = re.search(r"\{.*\}", content, re.DOTALL)
        if m:
            try:
                parsed = json.loads(m.group(0))
            except json.JSONDecodeError:
                parsed = None

    if parsed is None or not _validate_ai_response(parsed):
        # Anti-hallucination tripwire fired — refuse to surface the output
        logger.warning(
            f"AI currency check for {act_name}: guardrail tripped — "
            f"raw content snippet={content[:200]!r}"
        )
        return {
            "ok": False,
            "guardrail": "schema_violation",
            "error": "AI response failed the anti-hallucination guardrail and was discarded. Please verify manually via AustLII.",
            "forensic_caveat": "AI cross-check produced non-compliant output. No findings are surfaced. This is by design — the tool refuses to display AI text that may contain fabricated citations.",
        }

    # Attach the authoritative caveat regardless of model output
    parsed["forensic_caveat"] = (
        "This AI cross-check is a prompt for human review only. "
        "It does not constitute verification of the Act's currency. "
        "Confirm against AustLII or legislation.gov.au before relying on "
        "any section reference in an appellate submission."
    )
    parsed["ok"] = True
    parsed["guardrail"] = "passed"
    parsed["reviewed_at"] = datetime.now(timezone.utc).isoformat()
    parsed["act_name"] = act_name
    parsed["jurisdiction"] = jurisdiction
    return parsed
