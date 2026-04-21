"""
AI Usage Tracker — records every LLM call with token counts and USD cost into
the `ai_usage` MongoDB collection for the admin cost dashboard.

PREFERRED token source (since 2026-04-21): the real `response.usage` object
returned by `AsyncOpenAI.chat.completions.create(...)`. Those counts are the
exact values OpenAI billed on, so USD costs are accurate to the cent.

FALLBACK: tiktoken's `o200k_base` encoder — used when a caller doesn't (or
can't) pass real usage (e.g. the path hits `ai_service.call_llm_with_retry`
before this tracker was wired up, or a fallback retry path). Tiktoken is
within ~2% of the true tokeniser, still fine for analytics.

Pricing verified against OpenAI's published rate card (Feb 2026):
  gpt-4o        : $2.50 / 1M input tokens,  $10.00 / 1M output tokens
  gpt-4o-mini   : $0.15 / 1M input tokens,  $0.60  / 1M output tokens

This file is intentionally lightweight and side-effect-free on import —
the tracker is fire-and-forget; any failure to record usage is swallowed
so LLM traffic is never blocked by analytics.
"""
from __future__ import annotations

import re
import logging
from datetime import datetime, timezone
from typing import Optional

from config import db

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Pricing (USD per 1,000 tokens)
# ---------------------------------------------------------------------------
MODEL_PRICING = {
    "gpt-4o":            {"input": 0.0025,  "output": 0.01},
    "gpt-4o-2024-08-06": {"input": 0.0025,  "output": 0.01},
    "gpt-4o-mini":       {"input": 0.00015, "output": 0.0006},
    "gpt-4o-mini-2024-07-18": {"input": 0.00015, "output": 0.0006},
    # Conservative fallback — billed at gpt-4o rate if model is unrecognised.
    "_default":          {"input": 0.0025,  "output": 0.01},
}


# ---------------------------------------------------------------------------
# Token estimation
# ---------------------------------------------------------------------------
_encoder = None


def _get_encoder():
    """Lazy-load tiktoken's o200k_base encoder (used by gpt-4o family)."""
    global _encoder
    if _encoder is not None:
        return _encoder
    try:
        import tiktoken
        _encoder = tiktoken.get_encoding("o200k_base")
    except Exception as exc:  # pragma: no cover — tiktoken should be installed
        logger.warning(f"tiktoken unavailable ({exc}); falling back to char/4 estimate")
        _encoder = False  # sentinel for fallback
    return _encoder


def _estimate_tokens(text: str) -> int:
    if not text:
        return 0
    enc = _get_encoder()
    if enc and enc is not False:
        try:
            return len(enc.encode(text))
        except Exception:
            pass
    # Fallback: ~4 characters per token
    return max(1, len(text) // 4)


# ---------------------------------------------------------------------------
# Session-id parsing — extract case_id from the session_id convention used
# across the codebase. Patterns: `rpt_gen_{case_id}`, `barrister-{case_id}-*`,
# `classify_{case_id}`, `draft_{case_id}_{report_type}` etc.
# ---------------------------------------------------------------------------
# Case IDs in this codebase take two shapes:
#   (a) Legacy UUID-style: `9f87a1b2-c3d4-4abc-8ef0-123456789abc`
#   (b) Current app format: `case_` + 12 hex chars (e.g. `case_ec9b7141be1b`)
# Session IDs embed the case_id directly after the task prefix.
_CASE_ID_PATTERNS = [
    # UUID-style legacy case_ids
    re.compile(r"^(?:rpt_gen|rpt_detect|classify|verify|extract|submit|draft)_([a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12})", re.I),
    re.compile(r"^barrister-([a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12})", re.I),
    # Current `case_<12hex>` format
    re.compile(r"^(?:rpt_gen|rpt_detect|classify|verify|extract|submit)_(case_[a-f0-9]{6,})(?:_|$)", re.I),
    re.compile(r"^barrister-(case_[a-f0-9]{6,})-[a-z]", re.I),
    re.compile(r"^draft_(case_[a-f0-9]{6,})_", re.I),
    # Compact hex IDs (>=8 chars) followed by an underscore or end-of-section hyphen
    re.compile(r"^(?:rpt_gen|rpt_detect|classify|verify|extract|submit)_([a-f0-9]{8,})(?:_|$)", re.I),
    re.compile(r"^barrister-([a-f0-9]{8,})-[a-z]", re.I),
    re.compile(r"^draft_([a-f0-9]{8,})_", re.I),
]


def _extract_case_id(session_id: str) -> Optional[str]:
    if not session_id:
        return None
    for pat in _CASE_ID_PATTERNS:
        m = pat.match(session_id)
        if m:
            return m.group(1)
    return None


def _extract_report_type(session_id: str) -> Optional[str]:
    """Extract report_type hint from the session_id where encoded.

    Patterns:
      - `draft_{case_id}_{report_type}`
      - `rpt_gen_{case_id}_{report_type}` (where used)
      - `barrister-{case_id}-{section}` → treat as appellate_research_brief
    """
    if not session_id:
        return None
    if session_id.startswith("barrister-"):
        return "appellate_research_brief"
    # Current `case_<hex>` format
    m = re.match(r"^(?:draft|rpt_gen)_case_[a-f0-9]+_(.+)$", session_id, re.I)
    if m:
        return m.group(1)
    # Legacy UUID / compact hex format
    m = re.match(r"^(?:draft|rpt_gen)_[a-f0-9\-]{8,}_(.+)$", session_id)
    if m:
        return m.group(1)
    if session_id.startswith("rpt_detect_"):
        return "detection"
    if session_id.startswith("classify_"):
        return "grounds_classification"
    if session_id.startswith("argue_"):
        return "grounds_argue"
    if session_id.startswith("verify_"):
        return "grounds_verify"
    if session_id.startswith("extract_"):
        return "document_extract"
    return None


# ---------------------------------------------------------------------------
# Cost calculation
# ---------------------------------------------------------------------------

def _cost_for(model: str, input_tokens: int, output_tokens: int) -> float:
    pricing = MODEL_PRICING.get(model) or MODEL_PRICING["_default"]
    cost = (input_tokens / 1000.0) * pricing["input"] + (output_tokens / 1000.0) * pricing["output"]
    return round(cost, 6)


# ---------------------------------------------------------------------------
# Public API — fire-and-forget recorder
# ---------------------------------------------------------------------------

async def record_usage(
    *,
    session_id: str,
    provider: str,
    model: str,
    system_prompt: str,
    user_prompt: str,
    response_text: str,
    task_type: str,
    ok: bool,
    attempt: int,
    # Optional exact counts from `response.usage` (preferred — cent-accurate).
    # When None, fall back to tiktoken estimate on the prompt/response text.
    prompt_tokens: Optional[int] = None,
    completion_tokens: Optional[int] = None,
    total_tokens: Optional[int] = None,
) -> None:
    """Record a single LLM call. Never raises.

    Writes one document per call to `ai_usage` — aggregation is done at
    read time by the admin dashboard endpoint.

    When `prompt_tokens` / `completion_tokens` are supplied (from the OpenAI
    response's `usage` field), the recorded cost is exact — identical to what
    OpenAI actually bills. When absent, falls back to tiktoken estimates.
    """
    try:
        if prompt_tokens is not None and completion_tokens is not None:
            input_tokens = int(prompt_tokens)
            output_tokens = int(completion_tokens) if ok else 0
            source = "api_usage"
        else:
            input_tokens = _estimate_tokens(system_prompt) + _estimate_tokens(user_prompt)
            output_tokens = _estimate_tokens(response_text) if ok else 0
            source = "tiktoken_estimate"
        total_tok = int(total_tokens) if total_tokens is not None else input_tokens + output_tokens
        cost_usd = _cost_for(model, input_tokens, output_tokens)

        case_id = _extract_case_id(session_id)
        report_type = _extract_report_type(session_id)

        doc = {
            "session_id": session_id,
            "provider": provider,
            "model": model,
            "task_type": task_type,
            "report_type": report_type,
            "case_id": case_id,
            "input_tokens_est": input_tokens,
            "output_tokens_est": output_tokens,
            "total_tokens_est": total_tok,
            "cost_usd_est": cost_usd,
            "token_source": source,
            "ok": ok,
            "attempt": attempt,
            "created_at": datetime.now(timezone.utc),
        }
        await db.ai_usage.insert_one(doc)
    except Exception as exc:
        # Never let analytics kill an LLM flow.
        logger.warning(f"ai_usage record failed for session={session_id}: {exc}")
