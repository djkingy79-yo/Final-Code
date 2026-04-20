"""
Regression tests for the POST /api/cases/{case_id}/translate-section
endpoint added 2026-02-14 (per-section translation fast-path).
"""
import os
import sys
import pytest
from unittest.mock import AsyncMock, patch

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))


@pytest.mark.asyncio
async def test_unsupported_language_returns_400():
    from routers.translate import translate_section, SectionTranslateRequest
    from fastapi import HTTPException

    payload = SectionTranslateRequest(
        report_id="rpt1", language="xx",
        section_heading="Grounds", section_text="Some text.",
    )
    fake_user = type("U", (), {"user_id": "u1"})()

    with patch("routers.translate.get_current_user", new=AsyncMock(return_value=fake_user)), \
         patch("routers.translate.verify_case_ownership", new=AsyncMock()):
        with pytest.raises(HTTPException) as exc:
            await translate_section("case_abc", payload, request=None)
        assert exc.value.status_code == 400
        assert "Unsupported" in exc.value.detail


@pytest.mark.asyncio
async def test_english_returns_original_unchanged():
    """Asking to translate to English should be a no-op that returns the
    source text — saves a pointless LLM call."""
    from routers.translate import translate_section, SectionTranslateRequest

    payload = SectionTranslateRequest(
        report_id="rpt1", language="en",
        section_heading="Grounds", section_text="Ground 1: unreasonable verdict.",
    )
    fake_user = type("U", (), {"user_id": "u1"})()

    with patch("routers.translate.get_current_user", new=AsyncMock(return_value=fake_user)), \
         patch("routers.translate.verify_case_ownership", new=AsyncMock()):
        res = await translate_section("case_abc", payload, request=None)

    assert res["status"] == "completed"
    assert res["translated_content"] == "Ground 1: unreasonable verdict."
    assert res["cached"] is False


@pytest.mark.asyncio
async def test_empty_section_text_returns_400():
    from routers.translate import translate_section, SectionTranslateRequest
    from fastapi import HTTPException

    payload = SectionTranslateRequest(
        report_id="rpt1", language="es",
        section_heading="Grounds", section_text="   ",
    )
    fake_user = type("U", (), {"user_id": "u1"})()

    with patch("routers.translate.get_current_user", new=AsyncMock(return_value=fake_user)), \
         patch("routers.translate.verify_case_ownership", new=AsyncMock()):
        with pytest.raises(HTTPException) as exc:
            await translate_section("case_abc", payload, request=None)
        assert exc.value.status_code == 400


@pytest.mark.asyncio
async def test_too_long_section_returns_400():
    from routers.translate import translate_section, SectionTranslateRequest
    from fastapi import HTTPException

    payload = SectionTranslateRequest(
        report_id="rpt1", language="es",
        section_heading="Grounds", section_text="x" * 30001,
    )
    fake_user = type("U", (), {"user_id": "u1"})()

    with patch("routers.translate.get_current_user", new=AsyncMock(return_value=fake_user)), \
         patch("routers.translate.verify_case_ownership", new=AsyncMock()):
        with pytest.raises(HTTPException) as exc:
            await translate_section("case_abc", payload, request=None)
        assert exc.value.status_code == 400
        assert "too long" in exc.value.detail.lower()


@pytest.mark.asyncio
async def test_cache_hit_short_circuits_llm():
    """When a cached translation exists, the endpoint must NOT call the LLM."""
    from routers.translate import translate_section, SectionTranslateRequest

    payload = SectionTranslateRequest(
        report_id="rpt1", language="es",
        section_heading="Grounds of Appeal",
        section_text="The learned trial judge erred...",
    )
    fake_user = type("U", (), {"user_id": "u1"})()

    cached_doc = {"translated_content": "El juez de primera instancia erró...", "language_name": "Spanish"}

    with patch("routers.translate.get_current_user", new=AsyncMock(return_value=fake_user)), \
         patch("routers.translate.verify_case_ownership", new=AsyncMock()), \
         patch("routers.translate.db") as mock_db, \
         patch("routers.translate.call_llm_structured", new=AsyncMock(return_value={"ok": True, "content": "SHOULD NOT BE CALLED"})) as mock_llm:
        mock_db.report_section_translations.find_one = AsyncMock(return_value=cached_doc)
        res = await translate_section("case_abc", payload, request=None)

    assert res["status"] == "completed"
    assert res["cached"] is True
    assert res["translated_content"] == "El juez de primera instancia erró..."
    mock_llm.assert_not_called()


@pytest.mark.asyncio
async def test_cache_miss_calls_llm_and_persists():
    from routers.translate import translate_section, SectionTranslateRequest

    payload = SectionTranslateRequest(
        report_id="rpt1", language="es",
        section_heading="Grounds of Appeal",
        section_text="The learned trial judge erred...",
    )
    fake_user = type("U", (), {"user_id": "u1"})()
    replace_calls = []

    async def fake_replace(filter_, doc, upsert=False):
        replace_calls.append(doc)

    with patch("routers.translate.get_current_user", new=AsyncMock(return_value=fake_user)), \
         patch("routers.translate.verify_case_ownership", new=AsyncMock()), \
         patch("routers.translate.db") as mock_db, \
         patch("routers.translate.call_llm_structured", new=AsyncMock(return_value={"ok": True, "content": "Translated Spanish body."})):
        mock_db.report_section_translations.find_one = AsyncMock(return_value=None)
        mock_db.report_section_translations.replace_one = fake_replace
        mock_db.reports.find_one = AsyncMock(return_value={"report_id": "rpt1"})

        res = await translate_section("case_abc", payload, request=None)

    assert res["status"] == "completed"
    assert res["cached"] is False
    assert res["translated_content"] == "Translated Spanish body."
    assert len(replace_calls) == 1
    doc = replace_calls[0]
    assert doc["section_slug"] == "grounds-of-appeal"
    assert doc["translated_content"] == "Translated Spanish body."
    assert doc["report_id"] == "rpt1"
    assert doc["user_id"] == "u1"


@pytest.mark.asyncio
async def test_report_not_in_case_returns_404():
    from routers.translate import translate_section, SectionTranslateRequest
    from fastapi import HTTPException

    payload = SectionTranslateRequest(
        report_id="rpt_other", language="es",
        section_heading="Grounds", section_text="The judge erred.",
    )
    fake_user = type("U", (), {"user_id": "u1"})()

    with patch("routers.translate.get_current_user", new=AsyncMock(return_value=fake_user)), \
         patch("routers.translate.verify_case_ownership", new=AsyncMock()), \
         patch("routers.translate.db") as mock_db:
        mock_db.report_section_translations.find_one = AsyncMock(return_value=None)
        mock_db.reports.find_one = AsyncMock(return_value=None)

        with pytest.raises(HTTPException) as exc:
            await translate_section("case_abc", payload, request=None)
        assert exc.value.status_code == 404


@pytest.mark.asyncio
async def test_llm_failure_returns_502():
    from routers.translate import translate_section, SectionTranslateRequest
    from fastapi import HTTPException

    payload = SectionTranslateRequest(
        report_id="rpt1", language="es",
        section_heading="Grounds", section_text="Text here.",
    )
    fake_user = type("U", (), {"user_id": "u1"})()

    with patch("routers.translate.get_current_user", new=AsyncMock(return_value=fake_user)), \
         patch("routers.translate.verify_case_ownership", new=AsyncMock()), \
         patch("routers.translate.db") as mock_db, \
         patch("routers.translate.call_llm_structured", new=AsyncMock(return_value={"ok": False, "error": "rate limit"})):
        mock_db.report_section_translations.find_one = AsyncMock(return_value=None)
        mock_db.reports.find_one = AsyncMock(return_value={"report_id": "rpt1"})

        with pytest.raises(HTTPException) as exc:
            await translate_section("case_abc", payload, request=None)
        assert exc.value.status_code == 502
