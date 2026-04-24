"""
test_reports_list_payload.py

End-to-end tests for the Case Detail Reports tab payload optimisation
(24-Apr-2026 Fix #1).

LOCKS:
  1. GET /api/cases/{case_id}/reports (list) MUST NOT return heavy body
     fields: content.analysis, content.backup_analysis, content.barrister_view,
     content.full_detailed, content.extensive_log, content.quick_summary,
     content.report, content.body, content.text, content.markdown,
     content.html, content.draft, content.sections.
  2. GET /api/cases/{case_id}/reports/{report_id} (single) MUST still return
     the full body — the list strip must not leak into the per-report path.
  3. List response must still carry the metadata the frontend card uses:
     report_id, report_type, status, title, generated_at, metadata, error,
     verification_status (when present), source_mode (when present),
     content.metadata (when present), content.aggressive_mode flag.
  4. List response payload must drop dramatically (regression guard against
     accidental projection undo).

Pattern follows tests/conftest.py — calls the live supervisor backend at
localhost:8001 with the permanent CI test session token, seeds via direct
Motor connection, and cleans up after every test.
"""

from __future__ import annotations

import asyncio
import os
import sys
import uuid
from datetime import datetime, timezone

import pytest
import requests

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from tests.conftest import API_URL, SESSION_TOKEN  # noqa: E402

# ---------------------------------------------------------------------------
# Direct Mongo seeding (synchronous via PyMongo so tests don't fight the
# server's running event loop)
# ---------------------------------------------------------------------------
from pymongo import MongoClient  # noqa: E402

# Resolve the same Mongo URL + DB the running backend uses.
_DOTENV_PATH = os.path.join(os.path.dirname(__file__), "..", ".env")
_env: dict[str, str] = {}
if os.path.exists(_DOTENV_PATH):
    with open(_DOTENV_PATH) as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            k, _, v = line.partition("=")
            _env[k.strip()] = v.strip().strip('"').strip("'")

_MONGO_URL = os.environ.get("MONGO_URL") or _env.get("MONGO_URL")
_DB_NAME = os.environ.get("DB_NAME") or _env.get("DB_NAME")
assert _MONGO_URL and _DB_NAME, "MONGO_URL / DB_NAME not resolvable for tests"

_client = MongoClient(_MONGO_URL)
_db = _client[_DB_NAME]
TEST_USER_ID = "user_d2287f20104b"  # Owned by the permanent CI session


LIST_HEAVY_FIELDS = (
    "analysis",
    "backup_analysis",
    "barrister_view",
    "full_detailed",
    "extensive_log",
    "quick_summary",
    "report",
    "body",
    "text",
    "markdown",
    "html",
    "draft",
    "sections",
)

AUTH = {"Authorization": f"Bearer {SESSION_TOKEN}"}


# ---------------------------------------------------------------------------
# Fixture
# ---------------------------------------------------------------------------

@pytest.fixture
def case_with_heavy_reports():
    """Insert a throwaway case + four reports each with a ~200 KB body so
    the test exercises the same payload shape the production R v Homann
    case hits. Tear down after the test."""
    case_id = f"case_test_{uuid.uuid4().hex[:8]}"
    now = datetime.now(timezone.utc).isoformat()

    _db.cases.insert_one({
        "case_id": case_id,
        "user_id": TEST_USER_ID,
        "title": "Test v Test (payload audit)",
        "state": "nsw",
        "status": "active",
        "created_at": now,
    })

    big_text = "Lorem ipsum dolor sit amet. " * 8000  # ~ 200 KB

    seeded_reports = [
        {
            "report_id": f"rpt_{uuid.uuid4().hex[:12]}",
            "case_id": case_id,
            "user_id": TEST_USER_ID,
            "report_type": "quick_summary",
            "title": "Quick Summary — Test Case",
            "status": "completed",
            "generated_at": now,
            "verification_status": "verified",
            "source_mode": "structured",
            "metadata": {"model": "gpt-4o", "documents_analysed": 5},
            "error": None,
            "content": {
                "analysis": big_text,
                "backup_analysis": big_text,
                "metadata": {"section_count": 7},
                "aggressive_mode": False,
            },
        },
        {
            "report_id": f"rpt_{uuid.uuid4().hex[:12]}",
            "case_id": case_id,
            "user_id": TEST_USER_ID,
            "report_type": "full_detailed",
            "title": "Full Detailed — Test Case",
            "status": "completed",
            "generated_at": now,
            "metadata": {"model": "gpt-4o"},
            "content": {
                "analysis": big_text,
                "full_detailed": big_text,
                "report": big_text,
                "metadata": {"sections": ["1", "2", "3"]},
            },
        },
        {
            "report_id": f"rpt_{uuid.uuid4().hex[:12]}",
            "case_id": case_id,
            "user_id": TEST_USER_ID,
            "report_type": "extensive_log",
            "title": "Extensive Log — Test Case",
            "status": "completed",
            "generated_at": now,
            "metadata": {"model": "gpt-4o"},
            "content": {
                "analysis": big_text,
                "extensive_log": big_text,
                "body": big_text,
                "sections": ["a", "b", "c"],
                "metadata": {"depth": 3},
            },
        },
        {
            "report_id": f"rpt_{uuid.uuid4().hex[:12]}",
            "case_id": case_id,
            "user_id": TEST_USER_ID,
            "report_type": "barrister_view",
            "title": "Appellate Research Brief — Test Case",
            "status": "completed",
            "generated_at": now,
            "metadata": {"model": "gpt-4o"},
            "content": {
                "analysis": big_text,
                "barrister_view": big_text,
                "draft": big_text,
                "metadata": {"counsel_grade": "senior"},
            },
        },
    ]
    _db.reports.insert_many(seeded_reports)

    yield {"case_id": case_id, "reports": seeded_reports}

    _db.reports.delete_many({"case_id": case_id})
    _db.cases.delete_one({"case_id": case_id})


def _has_heavy_fields(content: dict) -> list:
    if not isinstance(content, dict):
        return []
    return [k for k in LIST_HEAVY_FIELDS if k in content]


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

def test_list_endpoint_strips_all_heavy_body_fields(case_with_heavy_reports):
    case_id = case_with_heavy_reports["case_id"]
    r = requests.get(f"{API_URL}/cases/{case_id}/reports", headers=AUTH, timeout=10)
    assert r.status_code == 200, r.text
    reports = r.json()
    assert len(reports) == 4, f"expected 4 seeded reports, got {len(reports)}"
    for report in reports:
        content = report.get("content", {}) or {}
        leaked = _has_heavy_fields(content)
        assert not leaked, (
            f"Report {report.get('report_type')} leaked heavy fields {leaked}; "
            f"projection in routers/reports.py::get_reports is broken."
        )


def test_list_endpoint_payload_size_dropped_dramatically(case_with_heavy_reports):
    case_id = case_with_heavy_reports["case_id"]
    r = requests.get(f"{API_URL}/cases/{case_id}/reports", headers=AUTH, timeout=10)
    assert r.status_code == 200
    size_bytes = len(r.content)
    # 4 reports × 200 KB body × ~3 heavy keys each → ~2.4 MB pre-fix.
    # Post-fix every body field is stripped → < 50 KB.
    assert size_bytes < 50_000, (
        f"List payload regressed — expected < 50 KB, got {size_bytes:,} bytes. "
        f"A heavy body field has been re-added to the projection."
    )


def test_list_endpoint_preserves_card_metadata(case_with_heavy_reports):
    case_id = case_with_heavy_reports["case_id"]
    r = requests.get(f"{API_URL}/cases/{case_id}/reports", headers=AUTH, timeout=10)
    reports = r.json()
    for report in reports:
        assert report.get("report_id"), "missing report_id"
        assert report.get("report_type"), "missing report_type"
        assert report.get("status"), "missing status"
        assert report.get("title"), "missing title"
        assert report.get("generated_at"), "missing generated_at"
        assert isinstance(report.get("metadata"), dict), "top-level metadata stripped"
        # content.metadata must survive (frontend reads from it)
        assert isinstance(
            (report.get("content") or {}).get("metadata"),
            dict,
        ), "content.metadata was wrongly stripped"


def test_list_endpoint_preserves_verification_and_source_mode(case_with_heavy_reports):
    case_id = case_with_heavy_reports["case_id"]
    r = requests.get(f"{API_URL}/cases/{case_id}/reports", headers=AUTH, timeout=10)
    reports = r.json()
    quick = next(rep for rep in reports if rep["report_type"] == "quick_summary")
    assert quick.get("verification_status") == "verified"
    assert quick.get("source_mode") == "structured"


def test_list_endpoint_filters_aggressive_mode_records(case_with_heavy_reports):
    """Sanity: the existing aggressive_mode filter still works alongside the
    new projection. The seeded report is aggressive_mode=False so it's
    returned. Add an aggressive_mode=True row and confirm it's filtered."""
    case_id = case_with_heavy_reports["case_id"]
    extra_id = f"rpt_{uuid.uuid4().hex[:12]}"
    _db.reports.insert_one({
        "report_id": extra_id,
        "case_id": case_id,
        "user_id": TEST_USER_ID,
        "report_type": "quick_summary",
        "title": "Aggressive variant",
        "status": "completed",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "content": {"analysis": "x" * 10, "aggressive_mode": True},
    })
    try:
        r = requests.get(f"{API_URL}/cases/{case_id}/reports", headers=AUTH, timeout=10)
        ids = [rep.get("report_id") for rep in r.json()]
        assert extra_id not in ids, "aggressive_mode=True record leaked into list"
    finally:
        _db.reports.delete_one({"report_id": extra_id})


def test_individual_report_endpoint_returns_full_analysis(case_with_heavy_reports):
    """Per-report endpoint must NOT inherit the list strip. The lazy-fetch
    on expand depends on this returning the full analysis."""
    case_id = case_with_heavy_reports["case_id"]
    for seed in case_with_heavy_reports["reports"]:
        r = requests.get(
            f"{API_URL}/cases/{case_id}/reports/{seed['report_id']}",
            headers=AUTH,
            timeout=10,
        )
        assert r.status_code == 200, r.text
        content = r.json().get("content", {}) or {}
        analysis = content.get("analysis")
        assert isinstance(analysis, str), (
            f"Per-report endpoint must return content.analysis for "
            f"{seed['report_type']}; got {type(analysis).__name__}."
        )
        assert len(analysis) > 100_000, (
            f"Per-report endpoint truncated analysis ({len(analysis)} chars) "
            f"for {seed['report_type']} — list-strip leaked into single fetch."
        )


def test_individual_report_endpoint_returns_tier_specific_blobs(case_with_heavy_reports):
    """Tier-specific body keys (full_detailed, extensive_log, barrister_view)
    must also survive on the per-report endpoint."""
    case_id = case_with_heavy_reports["case_id"]
    tier_keys = {
        "full_detailed": "full_detailed",
        "extensive_log": "extensive_log",
        "barrister_view": "barrister_view",
    }
    for seed in case_with_heavy_reports["reports"]:
        key = tier_keys.get(seed["report_type"])
        if not key:
            continue
        r = requests.get(
            f"{API_URL}/cases/{case_id}/reports/{seed['report_id']}",
            headers=AUTH,
            timeout=10,
        )
        content = r.json().get("content", {}) or {}
        assert isinstance(content.get(key), str), (
            f"Per-report endpoint stripped content.{key} for "
            f"{seed['report_type']} — list-strip leaked into single fetch."
        )
        assert len(content[key]) > 100_000
