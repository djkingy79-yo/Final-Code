"""
Archive-before-delete safety regression suite (locked 24 Feb 2026).

Proves the safety layer in services/dedup_archive.py is wired correctly
into the three delete paths AND does not alter dedup behaviour:

  1. cleanup_duplicate_grounds — every deleted ground row appears in
     `dedup_archive` before deletion.
  2. cleanup_duplicate_issues — every deleted issue row appears in
     `dedup_archive` before deletion.
  3. _dedup_document_extracts — every deleted extract row appears in
     `dedup_archive` before deletion.
  4. No archive row is written when nothing is deleted.

These tests use a real MongoDB instance (the project's standard pattern —
see tests/test_ground_dedup.py / tests/test_dedup_safety.py).

Matching rules, thresholds, and delete semantics are NOT under test here —
`test_dedup_safety.py` covers those. This suite tests only the archive
wiring.
"""
from __future__ import annotations

import os
import uuid
import pytest


def _mongo_available() -> bool:
    try:
        from motor.motor_asyncio import AsyncIOMotorClient  # noqa: F401
        return True
    except Exception:
        return False


requires_mongo = pytest.mark.skipif(
    os.environ.get("MONGO_URL", "mongodb://localhost:27017") is None or not _mongo_available(),
    reason="Requires running MongoDB instance",
)


async def _get_test_db():
    from motor.motor_asyncio import AsyncIOMotorClient
    client = AsyncIOMotorClient("mongodb://localhost:27017")
    return client["test_dedup_archive"], client


def _fresh() -> tuple[str, str]:
    tok = uuid.uuid4().hex[:12]
    return f"case_arc_{tok}", f"user_arc_{tok}"


# ---------------------------------------------------------------------------
# 1. cleanup_duplicate_grounds — archived before delete.
# ---------------------------------------------------------------------------

@requires_mongo
@pytest.mark.asyncio
async def test_cleanup_duplicate_grounds_archives_before_delete():
    """Seed 3 grounds — 2 duplicates of the first. After cleanup, the 2
    deleted ground rows must appear in `dedup_archive` with the correct
    metadata, and the surviving ground must NOT appear in the archive."""
    from services.ground_dedup import cleanup_duplicate_grounds

    db, client = await _get_test_db()
    case_id, user_id = _fresh()
    await db.grounds_of_merit.delete_many({"case_id": case_id})
    await db.dedup_archive.delete_many({"case_id": case_id})

    try:
        survivor_id = f"gnd_{uuid.uuid4().hex[:10]}"
        dup_1 = f"gnd_{uuid.uuid4().hex[:10]}"
        dup_2 = f"gnd_{uuid.uuid4().hex[:10]}"
        await db.grounds_of_merit.insert_many([
            {
                "ground_id": survivor_id,
                "case_id": case_id, "user_id": user_id,
                "title": "Trial Judge Misdirection on Intent",
                "ground_type": "judicial_error",
                "created_at": "2026-01-01T00:00:00",
                "status": "identified",
            },
            {
                "ground_id": dup_1,
                "case_id": case_id, "user_id": user_id,
                "title": "Trial Judge Misdirection on Intent",  # exact dup
                "ground_type": "judicial_error",
                "created_at": "2026-01-02T00:00:00",
                "status": "identified",
            },
            {
                "ground_id": dup_2,
                "case_id": case_id, "user_id": user_id,
                "title": "Trial Judge Misdirection on Intent",  # exact dup
                "ground_type": "judicial_error",
                "created_at": "2026-01-03T00:00:00",
                "status": "identified",
            },
        ])

        result = await cleanup_duplicate_grounds(db, case_id, user_id)
        assert result["removed"] == 2

        # Both duplicates must be GONE from grounds_of_merit.
        remaining_ids = {
            g["ground_id"]
            for g in await db.grounds_of_merit.find({"case_id": case_id}, {"_id": 0, "ground_id": 1}).to_list(10)
        }
        assert remaining_ids == {survivor_id}

        # Both duplicates MUST appear in dedup_archive.
        archive_rows = await db.dedup_archive.find(
            {"case_id": case_id, "source_collection": "grounds_of_merit"}, {"_id": 0}
        ).to_list(20)
        archived_ids = {r["original_id"] for r in archive_rows}
        assert archived_ids == {dup_1, dup_2}, (
            f"Expected archive to contain the 2 deleted ground_ids "
            f"{{dup_1, dup_2}}, got {archived_ids}"
        )
        # Survivor must NOT have been archived.
        assert survivor_id not in archived_ids

        # Every archive row has the locked schema.
        for row in archive_rows:
            for required in (
                "archive_id", "source_collection", "case_id", "user_id",
                "original_id", "original_record", "archived_at", "reason",
                "dedup_run_id",
            ):
                assert required in row, f"archive row missing '{required}': {row}"
            assert row["source_collection"] == "grounds_of_merit"
            assert row["case_id"] == case_id
            assert row["user_id"] == user_id
            assert row["reason"] == "cleanup_duplicate_grounds"
            assert row["dedup_run_id"].startswith("ddr_")
            assert row["archive_id"].startswith("arc_")
            # Original record must carry the full title — proof the archive
            # truly preserved the row's content, not just the id.
            assert row["original_record"]["title"] == "Trial Judge Misdirection on Intent"
            assert "_id" not in row["original_record"]  # Mongo _id must be stripped

        # All rows share a single dedup_run_id (they came from one pass).
        run_ids = {r["dedup_run_id"] for r in archive_rows}
        assert len(run_ids) == 1
    finally:
        await db.grounds_of_merit.delete_many({"case_id": case_id})
        await db.dedup_archive.delete_many({"case_id": case_id})
        client.close()


# ---------------------------------------------------------------------------
# 2. cleanup_duplicate_issues — archived before delete.
# ---------------------------------------------------------------------------

@requires_mongo
@pytest.mark.asyncio
async def test_cleanup_duplicate_issues_archives_before_delete():
    """Seed 3 issues with 2 duplicates. After cleanup, the 2 deleted rows
    must be in `dedup_archive` with reason='cleanup_duplicate_issues'."""
    from services.ground_dedup import cleanup_duplicate_issues

    db, client = await _get_test_db()
    case_id, user_id = _fresh()
    await db.issue_classifications.delete_many({"case_id": case_id})
    await db.dedup_archive.delete_many({"case_id": case_id})

    try:
        survivor_id = f"iss_{uuid.uuid4().hex[:10]}"
        dup_1 = f"iss_{uuid.uuid4().hex[:10]}"
        dup_2 = f"iss_{uuid.uuid4().hex[:10]}"
        await db.issue_classifications.insert_many([
            {
                "issue_id": survivor_id,
                "case_id": case_id, "user_id": user_id,
                "title": "Unreasonable Verdict - Identification Evidence",
                "ground_type": "unreasonable_verdict",
                "created_at": "2026-01-01T00:00:00",
            },
            {
                "issue_id": dup_1,
                "case_id": case_id, "user_id": user_id,
                "title": "Unreasonable Verdict - Identification Evidence",
                "ground_type": "unreasonable_verdict",
                "created_at": "2026-01-02T00:00:00",
            },
            {
                "issue_id": dup_2,
                "case_id": case_id, "user_id": user_id,
                "title": "Unreasonable Verdict - Identification Evidence",
                "ground_type": "unreasonable_verdict",
                "created_at": "2026-01-03T00:00:00",
            },
        ])

        result = await cleanup_duplicate_issues(db, case_id, user_id)
        assert result["removed"] == 2

        remaining_ids = {
            i["issue_id"]
            for i in await db.issue_classifications.find({"case_id": case_id}, {"_id": 0, "issue_id": 1}).to_list(10)
        }
        assert remaining_ids == {survivor_id}

        archive_rows = await db.dedup_archive.find(
            {"case_id": case_id, "source_collection": "issue_classifications"}, {"_id": 0}
        ).to_list(20)
        archived_ids = {r["original_id"] for r in archive_rows}
        assert archived_ids == {dup_1, dup_2}
        assert survivor_id not in archived_ids
        for row in archive_rows:
            assert row["reason"] == "cleanup_duplicate_issues"
            assert row["source_collection"] == "issue_classifications"
            assert row["original_record"]["title"] == "Unreasonable Verdict - Identification Evidence"
            assert row["case_id"] == case_id
            assert row["user_id"] == user_id
    finally:
        await db.issue_classifications.delete_many({"case_id": case_id})
        await db.dedup_archive.delete_many({"case_id": case_id})
        client.close()


# ---------------------------------------------------------------------------
# 3. _dedup_document_extracts — archived before delete.
# ---------------------------------------------------------------------------

@requires_mongo
@pytest.mark.asyncio
async def test_dedup_document_extracts_archives_before_delete():
    """Seed 3 rows for the same (document_id, case_id): 2 old and 1 new.
    The oldest 2 must be deleted AND archived; the newest survives and is
    NOT archived. Uses the startup helper directly with a module-level db
    swap so the real app DB is never touched."""
    import services.startup_tasks as st_mod
    from services.startup_tasks import _dedup_document_extracts

    db, client = await _get_test_db()
    case_id, _ = _fresh()
    doc_id = f"doc_{uuid.uuid4().hex[:10]}"

    # Clean residue.
    await db.document_extracts.delete_many({"case_id": case_id})
    await db.dedup_archive.delete_many({"case_id": case_id})

    try:
        await db.document_extracts.insert_many([
            {
                "extract_id": f"ext_{uuid.uuid4().hex[:8]}",
                "document_id": doc_id,
                "case_id": case_id,
                "user_id": "u_test",
                "facts": ["fact 1 v1"],
                "created_at": "2026-01-01T00:00:00",
            },
            {
                "extract_id": f"ext_{uuid.uuid4().hex[:8]}",
                "document_id": doc_id,
                "case_id": case_id,
                "user_id": "u_test",
                "facts": ["fact 1 v2"],
                "created_at": "2026-01-02T00:00:00",
            },
            {
                "extract_id": f"ext_{uuid.uuid4().hex[:8]}",
                "document_id": doc_id,
                "case_id": case_id,
                "user_id": "u_test",
                "facts": ["fact 1 v3 newest"],
                "created_at": "2026-01-03T00:00:00",
            },
        ])
        before = await db.document_extracts.count_documents({"document_id": doc_id})
        assert before == 3

        # Swap the module-level `db` in startup_tasks for our test DB.
        original_db = st_mod.db
        st_mod.db = db
        try:
            await _dedup_document_extracts()
        finally:
            st_mod.db = original_db

        after = await db.document_extracts.count_documents({"document_id": doc_id})
        assert after == 1, f"Expected 1 extract to survive, got {after}"

        archive_rows = await db.dedup_archive.find(
            {"case_id": case_id, "source_collection": "document_extracts"}, {"_id": 0}
        ).to_list(20)
        assert len(archive_rows) == 2, (
            f"Expected 2 archive rows for deleted document_extracts, got {len(archive_rows)}"
        )
        for row in archive_rows:
            assert row["reason"] == "_dedup_document_extracts"
            assert row["source_collection"] == "document_extracts"
            assert row["case_id"] == case_id
            # original_id is the stringified Mongo _id (document_extracts
            # has no business-id field the helper can use); it must be a
            # non-empty string.
            assert isinstance(row["original_id"], str) and row["original_id"]
            # The full original record (including facts) must be preserved.
            assert "facts" in row["original_record"]
            assert row["original_record"]["document_id"] == doc_id
            assert "_id" not in row["original_record"]
    finally:
        await db.document_extracts.delete_many({"case_id": case_id})
        await db.dedup_archive.delete_many({"case_id": case_id})
        client.close()


# ---------------------------------------------------------------------------
# 4. No archive row when nothing is deleted.
# ---------------------------------------------------------------------------

@requires_mongo
@pytest.mark.asyncio
async def test_no_archive_row_when_no_grounds_are_deleted():
    """Two genuinely distinct grounds → cleanup removes nothing → NO archive
    rows produced. Protects against a spurious-archive regression."""
    from services.ground_dedup import cleanup_duplicate_grounds

    db, client = await _get_test_db()
    case_id, user_id = _fresh()
    await db.grounds_of_merit.delete_many({"case_id": case_id})
    await db.dedup_archive.delete_many({"case_id": case_id})

    try:
        await db.grounds_of_merit.insert_many([
            {
                "ground_id": f"gnd_{uuid.uuid4().hex[:10]}",
                "case_id": case_id, "user_id": user_id,
                "title": "Trial Judge Misdirection on Intent Element",
                "ground_type": "judicial_error",
                "created_at": "2026-01-01T00:00:00",
                "status": "identified",
            },
            {
                "ground_id": f"gnd_{uuid.uuid4().hex[:10]}",
                "case_id": case_id, "user_id": user_id,
                "title": "Unreasonable Verdict — Identification Evidence",
                "ground_type": "unreasonable_verdict",
                "created_at": "2026-01-02T00:00:00",
                "status": "identified",
            },
        ])

        result = await cleanup_duplicate_grounds(db, case_id, user_id)
        assert result["removed"] == 0

        archive_count = await db.dedup_archive.count_documents({"case_id": case_id})
        assert archive_count == 0, (
            f"No archive rows should be created when nothing is deleted, "
            f"found {archive_count}"
        )
    finally:
        await db.grounds_of_merit.delete_many({"case_id": case_id})
        await db.dedup_archive.delete_many({"case_id": case_id})
        client.close()


@requires_mongo
@pytest.mark.asyncio
async def test_no_archive_row_when_no_issues_are_deleted():
    """Same guarantee for cleanup_duplicate_issues."""
    from services.ground_dedup import cleanup_duplicate_issues

    db, client = await _get_test_db()
    case_id, user_id = _fresh()
    await db.issue_classifications.delete_many({"case_id": case_id})
    await db.dedup_archive.delete_many({"case_id": case_id})

    try:
        await db.issue_classifications.insert_many([
            {
                "issue_id": f"iss_{uuid.uuid4().hex[:10]}",
                "case_id": case_id, "user_id": user_id,
                "title": "Judicial Error — Intent Direction",
                "ground_type": "judicial_error",
                "created_at": "2026-01-01T00:00:00",
            },
            {
                "issue_id": f"iss_{uuid.uuid4().hex[:10]}",
                "case_id": case_id, "user_id": user_id,
                "title": "Fresh Evidence — Post-Trial Witness Recantation",
                "ground_type": "fresh_evidence",
                "created_at": "2026-01-02T00:00:00",
            },
        ])

        result = await cleanup_duplicate_issues(db, case_id, user_id)
        assert result["removed"] == 0

        archive_count = await db.dedup_archive.count_documents({"case_id": case_id})
        assert archive_count == 0
    finally:
        await db.issue_classifications.delete_many({"case_id": case_id})
        await db.dedup_archive.delete_many({"case_id": case_id})
        client.close()


@requires_mongo
@pytest.mark.asyncio
async def test_no_archive_row_when_no_document_extracts_are_deleted():
    """_dedup_document_extracts must not write any archive row when every
    (document_id, case_id) already has exactly one extract."""
    import services.startup_tasks as st_mod
    from services.startup_tasks import _dedup_document_extracts

    db, client = await _get_test_db()
    case_id, _ = _fresh()
    doc_id = f"doc_{uuid.uuid4().hex[:10]}"
    await db.document_extracts.delete_many({"case_id": case_id})
    await db.dedup_archive.delete_many({"case_id": case_id})

    try:
        await db.document_extracts.insert_one({
            "extract_id": f"ext_{uuid.uuid4().hex[:8]}",
            "document_id": doc_id, "case_id": case_id, "user_id": "u_test",
            "facts": ["only one"],
            "created_at": "2026-01-01T00:00:00",
        })

        original_db = st_mod.db
        st_mod.db = db
        try:
            await _dedup_document_extracts()
        finally:
            st_mod.db = original_db

        assert await db.document_extracts.count_documents({"document_id": doc_id}) == 1
        assert await db.dedup_archive.count_documents({"case_id": case_id}) == 0
    finally:
        await db.document_extracts.delete_many({"case_id": case_id})
        await db.dedup_archive.delete_many({"case_id": case_id})
        client.close()
