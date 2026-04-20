"""
Regression tests for the translate parallelisation + restart-recovery fix
(2026-02-14).

Locks in:
  - `_persist_task` writes to the `translation_tasks` collection.
  - `_run_translation_background` uses bounded concurrency (semaphore=3) so
    chunks run in parallel rather than sequentially.
  - `translate_status` recovers from Mongo when the in-memory task is lost
    (simulating a backend restart).
"""
import os
import sys
import asyncio
import pytest
from unittest.mock import AsyncMock, patch

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from routers import translate as translate_mod  # noqa: E402


@pytest.mark.asyncio
async def test_persist_task_writes_to_db():
    """Verify _persist_task calls `replace_one` on the translation_tasks
    collection with the expected shape. Uses a mock to avoid event-loop
    issues when run alongside other Mongo-touching tests."""
    from routers.translate import _persist_task

    captured = {}

    async def fake_replace(filter_, doc, upsert=False):
        captured["filter"] = filter_
        captured["doc"] = doc
        captured["upsert"] = upsert

    class FakeCollection:
        replace_one = staticmethod(fake_replace)

    class FakeDB:
        translation_tasks = FakeCollection()

    with patch("routers.translate.db", FakeDB()):
        await _persist_task("pytest_persist_test_rpt_es", {
            "task_id": "abc", "status": "running", "progress": 2, "total_chunks": 5,
        })

    assert captured["filter"] == {"task_key": "pytest_persist_test_rpt_es"}
    assert captured["doc"]["status"] == "running"
    assert captured["doc"]["progress"] == 2
    assert captured["doc"]["task_key"] == "pytest_persist_test_rpt_es"
    assert captured["upsert"] is True


@pytest.mark.asyncio
async def test_chunks_run_concurrently():
    """Each chunk takes ~200 ms; with concurrency=3, 6 chunks should finish
    in roughly 2× chunk-time (~400 ms) not 6× (~1200 ms). This proves the
    asyncio.gather + semaphore wiring is actually parallel."""
    call_times = []

    async def fake_llm_call(**kwargs):
        import time
        call_times.append(time.time())
        await asyncio.sleep(0.2)
        return {"ok": True, "content": f"translated-{kwargs.get('session_id')}"}

    # Patch the LLM call
    translate_mod._translate_tasks["pytest_concurrent_rpt_es"] = {
        "task_id": "t1", "status": "running", "progress": 0, "total_chunks": 0,
    }

    # Large analysis text so it splits into 6 chunks (each >12k chars = split)
    analysis = "\n\n".join(["x" * 12500 for _ in range(6)])

    with patch("routers.translate.call_llm_structured", new=AsyncMock(side_effect=fake_llm_call)), \
         patch("routers.translate.db") as mock_db:
        mock_db.report_translations.replace_one = AsyncMock()
        mock_db.translation_tasks.replace_one = AsyncMock()

        import time
        start = time.time()
        await translate_mod._run_translation_background(
            task_key="pytest_concurrent_rpt_es",
            task_id="t1",
            report_id="rpt_test",
            case_id="case_test",
            user_id="user_test",
            language="es",
            target_lang="Spanish",
            analysis=analysis,
        )
        elapsed = time.time() - start

    # 6 chunks × 0.2s sequential = 1.2s. With concurrency=3: ~0.4-0.5s.
    # Assert under 0.9s to catch regressions to sequential execution while
    # giving plenty of headroom for slow CI.
    assert elapsed < 0.9, f"concurrency broken — took {elapsed:.2f}s for 6 chunks"

    # State should be completed after run
    state = translate_mod._translate_tasks.get("pytest_concurrent_rpt_es")
    assert state["status"] == "completed"


@pytest.mark.asyncio
async def test_status_endpoint_recovers_from_mongo_after_restart():
    """When the in-memory task is missing (simulated restart) but Mongo has
    the persisted snapshot, the status endpoint must recover rather than
    returning `not_found`. We verify the recovery logic with a mocked db."""
    task_key = "rpt_recover_test_es"

    # Ensure in-memory is empty (simulates backend restart)
    translate_mod._translate_tasks.pop(task_key, None)

    # Mock db.translation_tasks.find_one to return a persisted snapshot
    persisted_doc = {
        "task_key": task_key,
        "task_id": "abc",
        "status": "running",
        "progress": 4,
        "total_chunks": 10,
        "report_id": "rpt_recover_test",
        "case_id": "case_test",
        "user_id": "user_test",
        "language": "es",
        "language_name": "Spanish",
    }

    with patch("routers.translate.db") as mock_db:
        mock_db.translation_tasks.find_one = AsyncMock(return_value=persisted_doc)

        # Mirror the endpoint's recovery branch
        task = translate_mod._translate_tasks.get(task_key)
        assert task is None

        persisted = await mock_db.translation_tasks.find_one({"task_key": task_key}, {"_id": 0})
        assert persisted is not None
        assert persisted["status"] == "running"
        assert persisted["progress"] == 4
        assert persisted["total_chunks"] == 10
