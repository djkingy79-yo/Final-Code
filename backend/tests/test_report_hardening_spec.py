"""
Report hardening pass — spec regression tests (locked 24 Feb 2026).

Three tests, per REPORT_PRODUCT_SPEC.md §2.T1 and tier prerequisites:

  a. Case Summary (T1) prompt must NOT emit grounds / legislation /
     appeal-outcome language.
  b. Full Detailed Report (T3) must be blocked with 402 when the caller
     has not purchased Grounds Unlock (T2).
  c. Extensive Log Report (T4) must be blocked with 402 when the caller
     has not purchased Full Detailed Report (T3).

Admin bypass is explicitly exercised so this refactor can't accidentally
tighten the rules for admin users.
"""
from __future__ import annotations

import os
import re
import uuid
import pytest
import requests


BASE_URL = os.environ.get("REACT_APP_BACKEND_URL", "http://localhost:8001").rstrip("/")
CI_AUTH_TOKEN = "ci_test_token_permanent_20260412"


@pytest.fixture(scope="module")
def auth_session():
    s = requests.Session()
    s.headers.update({"Authorization": f"Bearer {CI_AUTH_TOKEN}"})
    return s


# ---------------------------------------------------------------------------
# (a) Case Summary prompt must not contain grounds / legislation / outcome.
# ---------------------------------------------------------------------------

def test_case_summary_prompt_excludes_grounds_legislation_and_outcome():
    """Reads the locked quick_summary prompt directly out of
    services/report_generator.py and asserts that the paid-tier content
    boundary is intact."""
    # Pull the generator source so the assertion is static — no LLM call,
    # no DB hit. This is the only way to guarantee no regression at the
    # prompt level without making every CI run cost money.
    gen_path = "/app/backend/services/report_generator.py"
    src = open(gen_path, encoding="utf-8").read()

    # Isolate the quick_summary branch (between the `if report_type ==
    # "quick_summary":` line and the next `elif report_type ==` line).
    m = re.search(
        r'if report_type == "quick_summary":(.*?)elif report_type ==',
        src, flags=re.DOTALL,
    )
    assert m, "quick_summary branch not found in report_generator.py"
    qs_block = m.group(1)

    # === Forbidden appellate-analysis section headings ===
    for forbidden in (
        "ALL GROUNDS IDENTIFIED",
        "PRIMARY ISSUES IDENTIFIED",
        "KEY LEGISLATION",
        "APPEAL OUTLOOK",
        "SENTENCING OVERVIEW",
        "PLAIN ENGLISH GUIDE",
    ):
        assert forbidden not in qs_block, (
            f"Case Summary prompt must not contain section '{forbidden}' "
            "— that belongs to a paid tier. Spec REPORT_PRODUCT_SPEC.md §2.T1."
        )

    # === "grounds" keyword ban — spec rule (a) ===
    # Strict interpretation: the 6 sent-to-LLM section HEADINGS of the
    # quick_summary prompt must not mention grounds, legislation, or
    # appellate strength — that is the content boundary that matters.
    # The instruction prose may legitimately say "do NOT identify grounds"
    # (that's the ABSOLUTE PROHIBITIONS block and the system-prompt
    # preamble), and the final "WHAT HAPPENS NEXT" bullet may reference
    # "Grounds of Merit" as the upsell target — that is the product
    # upsell, not report content.
    section_headings = re.findall(r"^## \d+\.\s+(.+)$", qs_block, flags=re.MULTILINE)
    assert section_headings, "quick_summary prompt has no ## section headings"
    heading_blob = " | ".join(h.upper() for h in section_headings)
    for banned in (
        "GROUND", "GROUNDS",
        "LEGISLATION", "STATUTORY", "STATUTE", "ACT (", "SECTION ",
        "APPEAL OUTLOOK", "OUTLOOK", "VIABILITY", "LIKELIHOOD",
        "STRONG", "MODERATE", "WEAK", "PROSPECT", "STRATEGY",
        "BLUEPRINT", "SUBMISSIONS",
    ):
        assert banned not in heading_blob, (
            f"Case Summary section heading contains forbidden term "
            f"'{banned}'. Full heading list: {section_headings}"
        )

    # === Mandatory affirmative rules must be present ===
    for required in (
        "CASE SNAPSHOT",
        "CASE NARRATIVE",
        "DOCUMENTS UPLOADED",
        "KEY DATES",
        "APPEAL DEADLINE STATUS",
        "WHAT HAPPENS NEXT",
        "ABSOLUTE PROHIBITIONS",
        "Ground titles, ground types",
        "Statutory citations, Act names, section numbers",
    ):
        assert required in qs_block, (
            f"Case Summary prompt is missing required element '{required}'."
        )


# ---------------------------------------------------------------------------
# In-process test harness for the tier-gate tests (b) and (c).
#
# The preview CI token resolves to an admin email, so live HTTP would bypass
# every gate under test. We therefore drive the handler directly with a
# non-admin user and a minimal in-memory case + no payments — isolating the
# gate code path from auth / DB / admin-email concerns.
# ---------------------------------------------------------------------------

import asyncio
import pathlib
import sys as _sys

# Ensure backend/ is on sys.path for the router import (pytest rootdir is
# /app/backend so this is already true in CI, but guard for local dev).
_sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))


class _FakeCollection:
    """Minimal async Mongo double — every method we use is coroutine-friendly
    and returns either the fixture or an empty list."""
    def __init__(self, docs=None):
        self._docs = list(docs or [])

    async def find_one(self, query, projection=None):
        for d in self._docs:
            if all(d.get(k) == v for k, v in query.items() if not isinstance(v, dict)):
                # Match $in on feature_type for the payments collection.
                ok = True
                for k, v in query.items():
                    if isinstance(v, dict) and "$in" in v:
                        ok = d.get(k) in v["$in"]
                    elif d.get(k) != v:
                        ok = False
                if ok:
                    return d
        return None

    def find(self, *a, **kw):
        class _Cur:
            def __init__(inner, docs): inner.docs = docs
            async def to_list(inner, n): return list(inner.docs)
            def sort(inner, *a, **kw): return inner
        return _Cur(self._docs)


class _FakeDB:
    def __init__(self, case=None, payments=None):
        self.cases = _FakeCollection([case] if case else [])
        self.payments = _FakeCollection(payments or [])
        self.documents = _FakeCollection([])
        self.grounds_of_merit = _FakeCollection([])
        self.notes = _FakeCollection([])
        self.timeline_events = _FakeCollection([])
        self.reports = _FakeCollection([])


class _FakeUser:
    def __init__(self, email="non_admin@example.com", user_id="u_non_admin"):
        self.email = email
        self.user_id = user_id
        self.id = user_id


def _invoke_generate_report(report_type: str, user, case, payments=None):
    """Call routers.reports.generate_report with a non-admin user and no
    payments. Monkeypatches `db` and `get_current_user` at the module level
    for the duration of the call. Returns (status_code, detail_dict) or
    raises if the handler returned a non-402 response."""
    from fastapi import HTTPException
    from routers import reports as reports_router
    import auth_utils

    original_db = reports_router.db
    original_get_current_user = reports_router.get_current_user

    fake_db = _FakeDB(case=case, payments=payments or [])

    async def _fake_get_current_user(_req):
        return user

    reports_router.db = fake_db
    reports_router.get_current_user = _fake_get_current_user
    try:
        coro = reports_router.generate_report(
            case_id=case["case_id"],
            report_request=reports_router.ReportRequest(report_type=report_type),
            request=None,
        )
        try:
            asyncio.get_event_loop().run_until_complete(coro)
        except HTTPException as e:
            return e.status_code, e.detail
        raise AssertionError(f"Expected HTTPException, handler returned without raising")
    finally:
        reports_router.db = original_db
        reports_router.get_current_user = original_get_current_user


# ---------------------------------------------------------------------------
# (b) T3 must 402 without T2 purchase. Admin bypass must NOT 402.
# ---------------------------------------------------------------------------

def test_t3_full_detailed_requires_grounds_unlock_payment():
    """Non-admin user with NO grounds_of_merit payment requesting T3 must
    receive 402 with prerequisite_required=grounds_of_merit."""
    user = _FakeUser(email="non_admin@example.com", user_id="u_non_admin")
    case = {
        "case_id": "case_hardening_t3",
        "user_id": "u_non_admin",
        "title": "T3 Gate Test",
        "defendant_name": "Gate Appellant",
        "state": "nsw",
        "offence_category": "indictable",
        "offence_type": "assault",
    }
    status_code, detail = _invoke_generate_report("full_detailed", user, case, payments=[])

    assert status_code == 402, f"Expected 402, got {status_code}"
    assert detail.get("feature_type") == "full_report"
    assert detail.get("prerequisite_required") == "grounds_of_merit", (
        f"402 body missing prerequisite_required=grounds_of_merit: {detail}"
    )
    assert detail.get("prerequisite_price") == 99.00
    assert detail.get("price") == 150.00
    assert detail.get("currency") == "AUD"


# ---------------------------------------------------------------------------
# (c) T4 must 402 without T3 purchase.
# ---------------------------------------------------------------------------

def test_t4_extensive_log_requires_full_detailed_payment():
    """Non-admin user with NO full_report payment requesting T4 must
    receive 402 with prerequisite_required=full_report."""
    user = _FakeUser(email="non_admin@example.com", user_id="u_non_admin")
    case = {
        "case_id": "case_hardening_t4",
        "user_id": "u_non_admin",
        "title": "T4 Gate Test",
        "defendant_name": "T4 Appellant",
        "state": "nsw",
        "offence_category": "indictable",
        "offence_type": "assault",
    }
    status_code, detail = _invoke_generate_report("extensive_log", user, case, payments=[])

    assert status_code == 402, f"Expected 402, got {status_code}"
    assert detail.get("feature_type") == "extensive_report"
    assert detail.get("prerequisite_required") == "full_report", (
        f"402 body missing prerequisite_required=full_report: {detail}"
    )
    assert detail.get("prerequisite_price") == 150.00
    assert detail.get("price") == 200.00
    assert detail.get("currency") == "AUD"


def test_admin_bypass_preserves_tier_access():
    """Admin users must NOT be rejected by the new prerequisite gate.
    The handler proceeds past the 402 branch and eventually fails/succeeds
    on a later check — we only assert it does NOT raise 402."""
    # Pull the first configured admin email (guaranteed by config.py to
    # exist or startup would have failed).
    from config import get_admin_emails
    admin_emails = get_admin_emails()
    if not admin_emails:
        pytest.skip("No ADMIN_EMAILS configured in this environment")
    admin_user = _FakeUser(email=admin_emails[0], user_id="u_admin")
    case = {
        "case_id": "case_hardening_admin_bypass",
        "user_id": "u_admin",
        "title": "Admin bypass test",
        "defendant_name": "Admin Appellant",
        "state": "nsw",
        "offence_category": "indictable",
        "offence_type": "assault",
    }
    # Admin must not hit the prerequisite 402; the handler may still raise a
    # *different* HTTPException later (e.g. 400 for missing data), but
    # it must NOT be 402.
    try:
        status, detail = _invoke_generate_report("full_detailed", admin_user, case, payments=[])
    except Exception as e:  # noqa: BLE001 — handler may raise anything later
        # Any non-402 exception means admin passed the gate. That's the
        # assertion we care about.
        assert "402" not in str(e), f"Admin hit 402: {e}"
        return
    assert status != 402, (
        f"Admin must bypass the 402 gate, got status {status} with detail {detail}"
    )
