"""
Regression tests for the OpenAI cost tracking endpoint and AI usage tracker.
"""
import os
import sys
import pytest
import uuid
from datetime import datetime, timezone, timedelta

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from services.ai_usage_tracker import (  # noqa: E402
    _cost_for,
    _estimate_tokens,
    _extract_case_id,
    _extract_report_type,
    MODEL_PRICING,
)


# --- Pure helpers ---

def test_pricing_table_has_gpt4o_and_mini():
    assert "gpt-4o" in MODEL_PRICING
    assert "gpt-4o-mini" in MODEL_PRICING
    assert MODEL_PRICING["gpt-4o"]["output"] == 0.01
    assert MODEL_PRICING["gpt-4o-mini"]["input"] == 0.00015


def test_cost_calculation_gpt4o():
    # 1M input @ $2.50 + 500k output @ $10 = $2.50 + $5.00 = $7.50
    assert _cost_for("gpt-4o", 1_000_000, 500_000) == 7.5


def test_cost_calculation_gpt4o_mini():
    # 1M input @ $0.15 + 1M output @ $0.60 = $0.75
    assert _cost_for("gpt-4o-mini", 1_000_000, 1_000_000) == 0.75


def test_cost_calculation_unknown_model_uses_default():
    # Unknown model falls back to gpt-4o rates (conservative)
    assert _cost_for("some-future-model", 1_000_000, 0) == 2.5


def test_token_estimation_is_nonzero():
    assert _estimate_tokens("hello world") > 0
    # Sanity: long text is more tokens than short
    assert _estimate_tokens("a" * 1000) > _estimate_tokens("hello")


def test_token_estimation_empty_returns_zero():
    assert _estimate_tokens("") == 0
    assert _estimate_tokens(None) == 0


# --- Session-id extractors ---

@pytest.mark.parametrize("sid,expected", [
    ("rpt_gen_abc12345678", "abc12345678"),
    ("rpt_gen_9f87a1b2-c3d4-4abc-8ef0-123456789abc", "9f87a1b2-c3d4-4abc-8ef0-123456789abc"),
    ("barrister-9f87a1b2-c3d4-4abc-8ef0-123456789abc-strategy", "9f87a1b2-c3d4-4abc-8ef0-123456789abc"),
    ("barrister-9f87a1b2c3d4-strategy", "9f87a1b2c3d4"),
    ("classify_deadbeef1234", "deadbeef1234"),
    ("draft_cafebabe1234_full_detailed", "cafebabe1234"),
    # Current case_<hex> format (production case_ids)
    ("rpt_gen_case_ec9b7141be1b_quick_summary", "case_ec9b7141be1b"),
    ("rpt_gen_case_ec9b7141be1b", "case_ec9b7141be1b"),
    ("barrister-case_ec9b7141be1b-strategy", "case_ec9b7141be1b"),
    ("classify_case_ec9b7141be1b", "case_ec9b7141be1b"),
    ("draft_case_ec9b7141be1b_full_detailed", "case_ec9b7141be1b"),
    ("", None),
    ("random-session", None),
])
def test_case_id_extraction(sid, expected):
    assert _extract_case_id(sid) == expected


@pytest.mark.parametrize("sid,expected", [
    ("barrister-abc-strategy", "appellate_research_brief"),
    ("draft_cafebabe1234_full_detailed", "full_detailed"),
    ("rpt_gen_9f87a1b2-c3d4-4abc-8ef0-123456789abc_quick_summary", "quick_summary"),
    # case_<hex> format
    ("rpt_gen_case_ec9b7141be1b_quick_summary", "quick_summary"),
    ("draft_case_ec9b7141be1b_extensive_log", "extensive_log"),
    ("rpt_detect_abc", "detection"),
    ("classify_xyz", "grounds_classification"),
    ("extract_abc", "document_extract"),
    ("", None),
    ("something_unknown", None),
])
def test_report_type_extraction(sid, expected):
    assert _extract_report_type(sid) == expected


# --- Admin endpoint (integration via FastAPI TestClient or httpx) ---

@pytest.mark.asyncio
async def test_record_usage_writes_to_db():
    from services.ai_usage_tracker import record_usage
    from config import db

    test_sid = f"rpt_gen_{uuid.uuid4().hex[:16]}_quick_summary"
    before = await db.ai_usage.count_documents({"session_id": test_sid})
    await record_usage(
        session_id=test_sid,
        provider="openai", model="gpt-4o",
        system_prompt="System " * 50,
        user_prompt="User " * 100,
        response_text="Response " * 200,
        task_type="report_generation", ok=True, attempt=1,
    )
    after = await db.ai_usage.count_documents({"session_id": test_sid})
    assert after == before + 1

    row = await db.ai_usage.find_one({"session_id": test_sid}, {"_id": 0})
    assert row["model"] == "gpt-4o"
    assert row["cost_usd_est"] > 0
    assert row["input_tokens_est"] > 0
    assert row["output_tokens_est"] > 0
    assert row["report_type"] == "quick_summary"

    # Clean up
    await db.ai_usage.delete_many({"session_id": test_sid})


@pytest.mark.asyncio
async def test_record_usage_swallows_errors(monkeypatch):
    """record_usage must never raise — LLM flow must not break on analytics bugs."""
    from services import ai_usage_tracker
    from services.ai_usage_tracker import record_usage

    class Boom:
        async def insert_one(self, *_, **__):
            raise RuntimeError("db down")

    class FakeDB:
        ai_usage = Boom()

    monkeypatch.setattr(ai_usage_tracker, "db", FakeDB())
    # Should not raise
    await record_usage(
        session_id="test", provider="openai", model="gpt-4o",
        system_prompt="x", user_prompt="y", response_text="z",
        task_type="general", ok=True, attempt=1,
    )
