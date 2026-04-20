"""
Regression tests for the Legislation Currency module.

Verifies:
  - Registry contains >= 79 Acts across all 9 jurisdictions.
  - _validate_ai_response enforces the anti-hallucination schema strictly.
  - build_dashboard returns the expected shape with totals bucketing.
  - mark_verified writes an audit-log entry and updates verification_source.
  - ai_currency_check forensic rules: output cannot contain first-person
    pronouns, filler phrases, or missing required fields.
"""
import os
import sys
import asyncio
import uuid
from datetime import datetime, timezone
from unittest.mock import AsyncMock, patch
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from frameworks.legislation_registry import (  # noqa: E402
    LEGISLATION_REGISTRY, total_count, by_jurisdiction, search_url_for,
)
from services.legislation_currency import (  # noqa: E402
    _validate_ai_response, build_dashboard, mark_verified, ai_currency_check, _bucket,
)


# --- Registry coverage ---

def test_registry_has_minimum_coverage():
    assert total_count() >= 79, "Registry must cover at least 79 Acts"
    jurs = by_jurisdiction()
    # Every jurisdiction must have at least one Act
    for j in ["nsw", "vic", "qld", "sa", "wa", "tas", "nt", "act", "cth"]:
        assert j in jurs and len(jurs[j]) >= 1, f"Jurisdiction {j} has no registered Acts"


def test_every_entry_has_austlii_and_last_verified():
    for e in LEGISLATION_REGISTRY:
        assert e.get("austlii_url", "").startswith("http"), f"No AustLII URL for {e['act_name']}"
        assert e.get("last_verified"), f"No last_verified for {e['act_name']}"
        # Search fallback must also be reachable shape
        assert search_url_for(e).startswith("http")


def test_act_names_match_strict_pattern():
    import re
    pat = re.compile(r"^.+ (Act|Code|Rules|Constitution|Law)( Compilation Act)? \d{4} \([A-Z][a-zA-Z]*\)$")
    failures = [e["act_name"] for e in LEGISLATION_REGISTRY if not pat.match(e["act_name"])]
    assert not failures, f"Registry entries with non-conforming names: {failures}"


# --- Bucketing ---

def test_bucket_thresholds():
    assert _bucket(0) == "current"
    assert _bucket(89) == "current"
    assert _bucket(90) == "review_soon"
    assert _bucket(179) == "review_soon"
    assert _bucket(180) == "overdue"
    assert _bucket(500) == "overdue"


# --- Anti-hallucination schema validator ---

def _good_response(**overrides):
    base = {
        "status": "cannot_verify",
        "confidence": "low",
        "knowledge_cutoff": "2024-05",
        "forensic_summary": "The Act cannot be independently confirmed against recent amendments on the basis of training corpus alone.",
        "suggested_review_focus": ["Confirm section numbering on AustLII."],
        "flagged_amendments": [],
        "forensic_caveat": "Prompt for human verification.",
    }
    base.update(overrides)
    return base


def test_validator_accepts_well_formed_response():
    assert _validate_ai_response(_good_response()) is True


def test_validator_rejects_missing_keys():
    r = _good_response()
    del r["knowledge_cutoff"]
    assert _validate_ai_response(r) is False


def test_validator_rejects_invalid_status():
    assert _validate_ai_response(_good_response(status="verified")) is False
    assert _validate_ai_response(_good_response(status="definitely_current")) is False


def test_validator_rejects_invalid_confidence():
    assert _validate_ai_response(_good_response(confidence="very_high")) is False


def test_validator_rejects_non_list_amendments():
    assert _validate_ai_response(_good_response(flagged_amendments="none")) is False


def test_validator_rejects_generic_filler():
    assert _validate_ai_response(_good_response(forensic_summary="As an AI language model, I cannot say.")) is False
    assert _validate_ai_response(_good_response(forensic_summary="I'm sorry but this is too hard.")) is False
    assert _validate_ai_response(_good_response(forensic_summary="Lorem ipsum dolor sit amet adequate length")) is False


def test_validator_rejects_first_person_forensic_breach():
    # Must reject "you / we / i / us / our" — forensic appellate language only
    assert _validate_ai_response(_good_response(forensic_summary="You should verify this on AustLII yourself now.")) is False
    assert _validate_ai_response(_good_response(forensic_summary="We cannot confirm this amendment with certainty here.")) is False


def test_validator_rejects_empty_or_short_summary():
    assert _validate_ai_response(_good_response(forensic_summary="")) is False
    assert _validate_ai_response(_good_response(forensic_summary="Too short")) is False


# --- Dashboard (uses real db but deterministic on empty audit log) ---

@pytest.mark.asyncio
async def test_build_dashboard_shape_and_totals():
    # Mock an empty audit log so this test is hermetic
    class Agg:
        def __init__(self, *a, **kw): pass
        async def to_list(self, _n): return []
    fake_db = type("D", (), {"framework_audit_log": type("C", (), {"aggregate": lambda self, *a, **kw: Agg()})()})()
    with patch("services.legislation_currency.db", fake_db):
        dash = await build_dashboard()
    assert dash["total"] == total_count()
    assert set(dash["totals"].keys()) == {"current", "review_soon", "overdue"}
    sum_totals = sum(dash["totals"].values())
    assert sum_totals == dash["total"], "Totals must sum to row count"
    assert dash["rows"], "Dashboard must return rows"
    req = {
        "act_name", "short_name", "year", "jurisdiction", "austlii_url",
        "austlii_search_url", "last_verified", "days_since_verified",
        "status", "verification_source", "notes",
    }
    assert req.issubset(set(dash["rows"][0].keys()))
    assert "forensic_notice" in dash and "AI-assisted" in dash["forensic_notice"]


@pytest.mark.asyncio
async def test_build_dashboard_jurisdiction_filter():
    class Agg:
        def __init__(self, *a, **kw): pass
        async def to_list(self, _n): return []
    fake_db = type("D", (), {"framework_audit_log": type("C", (), {"aggregate": lambda self, *a, **kw: Agg()})()})()
    with patch("services.legislation_currency.db", fake_db):
        dash = await build_dashboard(jurisdiction="nsw")
    assert dash["total"] >= 13
    assert all(r["jurisdiction"] == "nsw" for r in dash["rows"])


# --- mark_verified ---

@pytest.mark.asyncio
async def test_mark_verified_writes_audit_log_and_updates_source():
    act = "Crimes Act 1900 (NSW)"
    marker = f"pytest-{uuid.uuid4().hex[:8]}"

    inserted = {}
    async def fake_insert(doc): inserted.update(doc)
    class Agg:
        def __init__(self, *a, **kw): pass
        async def to_list(self, _n): return [{
            "_id": act, "verified_at": datetime.now(timezone.utc),
            "verified_by": marker, "notes": f"marker={marker}",
        }]
    fake_db = type("D", (), {"framework_audit_log": type("C", (), {
        "insert_one": staticmethod(fake_insert),
        "aggregate": lambda self, *a, **kw: Agg(),
    })()})()

    with patch("services.legislation_currency.db", fake_db):
        row = await mark_verified(act_name=act, verified_by=marker, notes=f"marker={marker}")

    assert row["act_name"] == act
    assert row["verification_source"] == "audit_log"
    assert row["verified_by"] == marker
    assert inserted["event"] == "verified"


@pytest.mark.asyncio
async def test_mark_verified_rejects_unknown_act():
    with pytest.raises(ValueError):
        await mark_verified(act_name="Made-up Act 9999 (XYZ)", verified_by="pytest")


# --- ai_currency_check error handling ---

@pytest.mark.asyncio
async def test_ai_check_guardrail_on_llm_failure():
    with patch("services.legislation_currency.call_llm_structured",
               new=AsyncMock(return_value={"ok": False, "error": "timeout"})):
        out = await ai_currency_check(
            act_name="Crimes Act 1900 (NSW)", jurisdiction="nsw",
            last_verified="2026-02-14", session_id="pytest_fail",
        )
    assert out["ok"] is False
    assert out["guardrail"] == "llm_failure"
    assert "verify manually" in out["forensic_caveat"].lower()


@pytest.mark.asyncio
async def test_ai_check_guardrail_on_schema_violation():
    # Model hands back a plausible-looking but invalid JSON (missing required key)
    bad = '{"status": "appears_current", "confidence": "high"}'
    with patch("services.legislation_currency.call_llm_structured",
               new=AsyncMock(return_value={"ok": True, "content": bad})):
        out = await ai_currency_check(
            act_name="Crimes Act 1900 (NSW)", jurisdiction="nsw",
            last_verified="2026-02-14", session_id="pytest_schema",
        )
    assert out["ok"] is False
    assert out["guardrail"] == "schema_violation"
    assert "AI response failed" in out["error"]


@pytest.mark.asyncio
async def test_ai_check_guardrail_on_fabrication_tripwire():
    # Model hands back first-person pronouns — must be rejected
    hallucinated = (
        '{"status": "appears_current", "confidence": "high", "knowledge_cutoff": "2024-05", '
        '"forensic_summary": "I checked this and we are confident it is current as of today.", '
        '"suggested_review_focus": ["none"], "flagged_amendments": [], '
        '"forensic_caveat": "n/a"}'
    )
    with patch("services.legislation_currency.call_llm_structured",
               new=AsyncMock(return_value={"ok": True, "content": hallucinated})):
        out = await ai_currency_check(
            act_name="Crimes Act 1900 (NSW)", jurisdiction="nsw",
            last_verified="2026-02-14", session_id="pytest_hallucinate",
        )
    assert out["ok"] is False
    assert out["guardrail"] == "schema_violation"


@pytest.mark.asyncio
async def test_ai_check_valid_response_is_augmented_with_caveat():
    ok_response = (
        '{"status": "cannot_verify", "confidence": "low", "knowledge_cutoff": "2024-05", '
        '"forensic_summary": "Independent confirmation of currency is not possible on the available training data.", '
        '"suggested_review_focus": ["Confirm on AustLII."], "flagged_amendments": [], '
        '"forensic_caveat": "AI-only; not verification."}'
    )
    with patch("services.legislation_currency.call_llm_structured",
               new=AsyncMock(return_value={"ok": True, "content": ok_response})):
        out = await ai_currency_check(
            act_name="Crimes Act 1900 (NSW)", jurisdiction="nsw",
            last_verified="2026-02-14", session_id="pytest_valid",
        )
    assert out["ok"] is True
    assert out["guardrail"] == "passed"
    # The service must OVERWRITE the caveat to its authoritative wording
    assert "prompt for human review only" in out["forensic_caveat"]
    assert "AustLII or legislation.gov.au" in out["forensic_caveat"]
